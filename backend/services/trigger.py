"""
services/trigger.py — Deterministic trigger evaluation engine.

Rule (frozen for PS-F03):
  IF consensus_status == REACHED
     AND consensus_value_mm >= 100.0
     AND policy is currently valid
  THEN TRIGGERED
  ELSE NOT_TRIGGERED or TRIGGER_BLOCKED_NO_CONSENSUS

AI MUST NOT call or override this function.
This is the authoritative financial decision point.
"""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from models.consensus import ConsensusResult, ConsensusStatus
from models.trigger import TriggerEvaluation, TriggerStatus
from models.policy import Policy
from models.audit import AuditEventType
from services.audit import write_audit_event
from services.ids import new_ulid


RAINFALL_THRESHOLD_MM: float = 100.0


async def evaluate_trigger(
    consensus_result: ConsensusResult,
    policy: Policy,
    correlation_id: str,
    db: AsyncSession,
) -> TriggerEvaluation:
    """
    Deterministic trigger evaluation.

    Decision logic:
    1. If consensus is NO_CONSENSUS → TRIGGER_BLOCKED_NO_CONSENSUS.
    2. If policy is not currently valid → NOT_TRIGGERED.
    3. If consensus_value_mm >= threshold → TRIGGERED.
    4. Otherwise → NOT_TRIGGERED.

    Persists TriggerEvaluation and writes audit event.
    """
    evaluated_at = datetime.now(timezone.utc)

    # Explicitly query the trigger rule to avoid MissingGreenlet on implicit lazy load
    from sqlalchemy import select
    from models.policy import TriggerRule
    trigger_rule = await db.scalar(
        select(TriggerRule).where(TriggerRule.policy_id == policy.id)
    )
    threshold = trigger_rule.threshold_value if trigger_rule else RAINFALL_THRESHOLD_MM

    # ── Decision ─────────────────────────────────────────────────────────────
    if consensus_result.status == ConsensusStatus.NO_CONSENSUS:
        trigger_status = TriggerStatus.TRIGGER_BLOCKED_NO_CONSENSUS
        reason = "No authoritative consensus established. Trigger blocked."

    elif not policy.is_currently_valid():
        trigger_status = TriggerStatus.NOT_TRIGGERED
        reason = f"Policy {policy.id!r} is not currently active or within validity window."

    elif (
        consensus_result.consensus_value_mm is not None
        and consensus_result.consensus_value_mm >= threshold
    ):
        trigger_status = TriggerStatus.TRIGGERED
        reason = (
            f"Consensus rainfall {consensus_result.consensus_value_mm:.1f} mm "
            f">= threshold {threshold:.1f} mm. Trigger fires."
        )

    else:
        trigger_status = TriggerStatus.NOT_TRIGGERED
        reason = (
            f"Consensus rainfall {consensus_result.consensus_value_mm} mm "
            f"< threshold {threshold:.1f} mm. Trigger does not fire."
        )

    # ── Persist ──────────────────────────────────────────────────────────────
    record = TriggerEvaluation(
        id=new_ulid(),
        policy_id=policy.id,
        consensus_result_id=consensus_result.id,
        trigger_status=trigger_status,
        consensus_value_mm=consensus_result.consensus_value_mm,
        threshold_mm=threshold,
        evaluated_at=evaluated_at,
        reason=reason,
    )
    db.add(record)
    await db.flush()

    # ── Audit ────────────────────────────────────────────────────────────────
    if trigger_status == TriggerStatus.TRIGGERED:
        audit_type = AuditEventType.TRIGGER_FIRED
        audit_status = "TRIGGERED"
    elif trigger_status == TriggerStatus.TRIGGER_BLOCKED_NO_CONSENSUS:
        audit_type = AuditEventType.TRIGGER_BLOCKED
        audit_status = "BLOCKED_NO_CONSENSUS"
    else:
        audit_type = AuditEventType.TRIGGER_EVALUATED
        audit_status = "NOT_TRIGGERED"

    await write_audit_event(
        db=db,
        event_type=audit_type,
        entity_type="TRIGGER",
        entity_id=record.id,
        policy_id=policy.id,
        correlation_id=correlation_id,
        status=audit_status,
        message=reason,
        metadata={
            "trigger_status": trigger_status.value,
            "consensus_value_mm": consensus_result.consensus_value_mm,
            "threshold_mm": threshold,
        },
    )

    return record

