"""
services/settlement.py — Idempotent payout settlement engine.

CORE INVARIANT:
  Same policy + same trigger_evaluation → AT MOST ONE wallet credit.

HOW IDEMPOTENCY IS ENFORCED (two layers):
  Layer 1 (fast path): Query payouts table for existing record before INSERT.
  Layer 2 (concurrency-safe): DB UniqueConstraint on (policy_id, trigger_evaluation_id).
    If two requests race, the second INSERT raises IntegrityError → caught here → ALREADY_SETTLED.

PROVIDER LAYER:
  Settlement calls the PayoutProvider *after* the payout record is created and
  *before* the wallet is credited. The provider executes the synthetic disbursement.

  Provider status decides whether to credit the wallet:
    PROVIDER_SUCCESS  → credit wallet → Payout.status = SUCCESS
    PROVIDER_FAILED   → do NOT credit → Payout.status = FAILED
    PROVIDER_UNKNOWN  → do NOT credit → Payout.status = FAILED
                        (treat UNKNOWN as FAILED — safe for hackathon scope)

  The defensible guarantee remains:
    "Same settlement identity produces at most one successful wallet credit."

NEVER use floating point for payout amounts.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.payout import Payout, PayoutStatus
from models.trigger import TriggerEvaluation, TriggerStatus
from models.policy import Policy
from models.audit import AuditEventType
from services.audit import write_audit_event
from services.wallet import credit_wallet
from services.ids import new_ulid
from services.providers import PayoutProvider, ProviderStatus, get_default_provider


async def settle_payout(
    trigger_evaluation: TriggerEvaluation,
    policy: Policy,
    correlation_id: str,
    db: AsyncSession,
    provider: PayoutProvider | None = None,
) -> tuple[Payout | None, str]:
    """
    Attempt to settle a payout for a triggered evaluation.

    Args:
        trigger_evaluation: The DB record from trigger service.
        policy:             Loaded policy with payout_amount_paise.
        correlation_id:     Links this call to a simulation run in the audit trail.
        db:                 Active async DB session.
        provider:           Payout provider to use. Defaults to MockPayoutProvider.

    Returns:
        (payout_record, idempotency_status)
        idempotency_status: "NEW" | "ALREADY_SETTLED" | "SKIPPED" | "FAILED"

    Does NOT raise on provider failure — returns ("FAILED",) with payout in FAILED state.
    """
    if provider is None:
        provider = get_default_provider()

    # ── Guard: only settle for TRIGGERED evaluations ─────────────────────────
    if trigger_evaluation.trigger_status != TriggerStatus.TRIGGERED:
        return None, "SKIPPED"

    idempotency_key = f"{policy.id}::{trigger_evaluation.id}"

    # ── Layer 1: Fast-path duplicate check ───────────────────────────────────
    existing = await db.scalar(
        select(Payout).where(
            Payout.policy_id == policy.id,
            Payout.trigger_evaluation_id == trigger_evaluation.id,
        )
    )
    if existing is not None:
        # Already settled — do not credit wallet again
        await write_audit_event(
            db=db,
            event_type=AuditEventType.DUPLICATE_SETTLEMENT,
            entity_type="PAYOUT",
            entity_id=existing.id,
            policy_id=policy.id,
            correlation_id=correlation_id,
            status="DUPLICATE",
            message=f"Settlement already completed. idempotency_key={idempotency_key!r}",
            metadata={"existing_payout_id": existing.id, "idempotency_key": idempotency_key},
        )
        return existing, "ALREADY_SETTLED"

    # ── Create payout record (PENDING) ───────────────────────────────────────
    payout_id = new_ulid()
    payout = Payout(
        id=payout_id,
        policy_id=policy.id,
        trigger_evaluation_id=trigger_evaluation.id,
        status=PayoutStatus.PENDING,
        amount_paise=policy.payout_amount_paise,   # integer paise — NEVER float
        idempotency_key=idempotency_key,
    )

    try:
        async with db.begin_nested():
            db.add(payout)
            await db.flush()  # triggers UniqueConstraint check
    except IntegrityError:
        # Layer 2: Concurrent duplicate caught by DB constraint (savepoint auto-rolled back)
        existing = await db.scalar(
            select(Payout).where(Payout.idempotency_key == idempotency_key)
        )
        await write_audit_event(
            db=db,
            event_type=AuditEventType.DUPLICATE_SETTLEMENT,
            entity_type="PAYOUT",
            entity_id=existing.id if existing else payout_id,
            policy_id=policy.id,
            correlation_id=correlation_id,
            status="DUPLICATE",
            message="Concurrent duplicate settlement blocked by DB constraint.",
            metadata={"idempotency_key": idempotency_key},
        )
        return existing, "ALREADY_SETTLED"

    # ── Audit: payout created ────────────────────────────────────────────────
    await write_audit_event(
        db=db,
        event_type=AuditEventType.PAYOUT_CREATED,
        entity_type="PAYOUT",
        entity_id=payout_id,
        policy_id=policy.id,
        correlation_id=correlation_id,
        status="PENDING",
        message=f"Payout created: {policy.payout_amount_paise} paise.",
        metadata={
            "payout_id": payout_id,
            "amount_paise": policy.payout_amount_paise,
            "idempotency_key": idempotency_key,
        },
    )

    # ── Invoke provider ───────────────────────────────────────────────────────
    provider_result = provider.disburse(
        payout_id=payout_id,
        amount_paise=policy.payout_amount_paise,
        policy_id=policy.id,
        idempotency_key=idempotency_key,
    )

    # ── Handle provider outcome ───────────────────────────────────────────────
    if provider_result.status == ProviderStatus.SUCCESS:
        # Provider confirmed disbursement — credit synthetic wallet
        wallet_tx = await credit_wallet(
            policy_id=policy.id,
            payout_id=payout_id,
            amount_paise=policy.payout_amount_paise,  # integer paise
            correlation_id=correlation_id,
            db=db,
        )
        payout.status = PayoutStatus.SUCCESS
        payout.provider_reference = provider_result.provider_reference
        await db.flush()

        await write_audit_event(
            db=db,
            event_type=AuditEventType.PAYOUT_COMPLETED,
            entity_type="PAYOUT",
            entity_id=payout_id,
            policy_id=policy.id,
            correlation_id=correlation_id,
            status="SUCCESS",
            message="Payout completed. Provider confirmed. Wallet credited.",
            metadata={
                "payout_id": payout_id,
                "amount_paise": policy.payout_amount_paise,
                "provider_reference": provider_result.provider_reference,
                "wallet_tx_id": wallet_tx.id,
            },
        )
        return payout, "NEW"

    else:
        # Provider FAILED or UNKNOWN — do NOT credit wallet
        # UNKNOWN is treated as FAILED for hackathon scope.
        # Defensible guarantee: no wallet credit occurs if provider did not confirm.
        payout.status = PayoutStatus.FAILED
        payout.failure_reason = (
            f"{provider_result.status.value}: "
            f"[{provider_result.error_code}] {provider_result.error_message}"
        )[:512]
        await db.flush()

        await write_audit_event(
            db=db,
            event_type=AuditEventType.PAYOUT_FAILED,
            entity_type="PAYOUT",
            entity_id=payout_id,
            policy_id=policy.id,
            correlation_id=correlation_id,
            status=provider_result.status.value,
            message=(
                f"Provider {provider_result.status.value}: "
                f"[{provider_result.error_code}] {provider_result.error_message}"
            ),
            metadata={
                "payout_id": payout_id,
                "amount_paise": policy.payout_amount_paise,
                "provider_status": provider_result.status.value,
                "provider_reference": provider_result.provider_reference,
                "error_code": provider_result.error_code,
            },
        )
        return payout, "FAILED"
