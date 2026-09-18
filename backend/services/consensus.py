"""
services/consensus.py — Deterministic consensus engine.

Algorithm (frozen for PS-F03):
  Input: list of (source_id, value_mm) pairs from valid, deduplicated observations.

  Step 1: Compute median of ALL available source values.
  Step 2: For each source, accepted = abs(value - median) <= TOLERANCE (5 mm, inclusive).
  Step 3: If accepted_count < QUORUM (2): NO_CONSENSUS.
  Step 4: If accepted_count >= QUORUM: REACHED.
           consensus_value = median of accepted observations only.
  Step 5: Sources outside tolerance are recorded as outliers.

This function is PURE (no DB, no side effects) for testability.
Database persistence is handled by run_consensus().
"""
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from models.consensus import ConsensusResult, ConsensusStatus
from models.audit import AuditEventType
from services.audit import write_audit_event
from services.ids import new_ulid


TOLERANCE_MM: float = 5.0   # inclusive: abs(value - median) <= TOLERANCE
QUORUM: int = 2             # minimum accepted sources


@dataclass
class SourceObservation:
    source_id: str
    value_mm: float


@dataclass
class ConsensusOutput:
    status: ConsensusStatus
    median_all_sources_mm: float | None
    consensus_value_mm: float | None
    accepted_sources: list[str]
    outlier_sources: list[str]
    reason: str

    # For building SimulationResponse
    source_count_total: int = 0
    source_count_accepted: int = 0
    source_count_outliers: int = 0


def evaluate_consensus(observations: list[SourceObservation]) -> ConsensusOutput:
    """
    Pure, deterministic consensus evaluation.
    No DB. No side effects. Fully testable.

    Verified against the four frozen scenarios:

    Scenario 1: A=110, B=108, C=111
      median=110, all |diff|<=5 → REACHED, consensus=110.0

    Scenario 2: A=110, B=108, C=7
      median=108, A diff=2✓, B diff=0✓, C diff=101✗
      accepted=[A,B], consensus=median(110,108)=109.0 → REACHED

    Scenario 3: A=120, B=50, C=5
      median=50, A diff=70✗, B diff=0✓, C diff=45✗
      accepted=[B] only, count=1 < 2 → NO_CONSENSUS
    """
    n = len(observations)
    if n == 0:
        return ConsensusOutput(
            status=ConsensusStatus.NO_CONSENSUS,
            median_all_sources_mm=None,
            consensus_value_mm=None,
            accepted_sources=[],
            outlier_sources=[],
            reason="No observations provided.",
            source_count_total=0,
            source_count_accepted=0,
            source_count_outliers=0,
        )

    values = [o.value_mm for o in observations]

    # Step 1: Median of ALL sources
    # statistics.median returns float for even-length lists (average of two midpoints).
    median_all = statistics.median(values)

    # Step 2: Classify each source
    accepted: list[SourceObservation] = []
    outliers: list[SourceObservation] = []

    for obs in observations:
        diff = abs(obs.value_mm - median_all)
        if diff <= TOLERANCE_MM:    # INCLUSIVE tolerance (frozen decision)
            accepted.append(obs)
        else:
            outliers.append(obs)

    accepted_ids = [o.source_id for o in accepted]
    outlier_ids = [o.source_id for o in outliers]

    # Step 3: Quorum check
    if len(accepted) < QUORUM:
        return ConsensusOutput(
            status=ConsensusStatus.NO_CONSENSUS,
            median_all_sources_mm=float(median_all),
            consensus_value_mm=None,
            accepted_sources=accepted_ids,
            outlier_sources=outlier_ids,
            reason=(
                f"Only {len(accepted)} source(s) within ±{TOLERANCE_MM} mm tolerance. "
                f"Quorum requires {QUORUM}."
            ),
            source_count_total=n,
            source_count_accepted=len(accepted),
            source_count_outliers=len(outliers),
        )

    # Step 4: Consensus value = median of ACCEPTED observations
    accepted_values = [o.value_mm for o in accepted]
    consensus_value = statistics.median(accepted_values)

    return ConsensusOutput(
        status=ConsensusStatus.REACHED,
        median_all_sources_mm=float(median_all),
        consensus_value_mm=float(consensus_value),
        accepted_sources=accepted_ids,
        outlier_sources=outlier_ids,
        reason=(
            f"Consensus reached. {len(accepted)}/{n} sources within tolerance. "
            f"Consensus value: {consensus_value:.1f} mm."
        ),
        source_count_total=n,
        source_count_accepted=len(accepted),
        source_count_outliers=len(outliers),
    )


async def run_consensus(
    observations: list[SourceObservation],
    policy_id: str,
    region_id: str,
    correlation_id: str,
    db: AsyncSession,
) -> ConsensusResult:
    """
    Evaluate consensus, persist the result, write audit events, and return the DB record.
    """
    evaluated_at = datetime.now(timezone.utc)
    output = evaluate_consensus(observations)

    # Persist ConsensusResult
    record = ConsensusResult(
        id=new_ulid(),
        policy_id=policy_id,
        region_id=region_id,
        status=output.status,
        median_all_sources_mm=output.median_all_sources_mm,
        consensus_value_mm=output.consensus_value_mm,
        source_count_total=output.source_count_total,
        source_count_accepted=output.source_count_accepted,
        source_count_outliers=output.source_count_outliers,
        accepted_source_ids=output.accepted_sources,
        outlier_source_ids=output.outlier_sources,
        evaluated_at=evaluated_at,
        reason=output.reason,
    )
    db.add(record)
    await db.flush()

    # Write audit event
    if output.status == ConsensusStatus.REACHED:
        await write_audit_event(
            db=db,
            event_type=AuditEventType.CONSENSUS_REACHED,
            entity_type="CONSENSUS",
            entity_id=record.id,
            policy_id=policy_id,
            correlation_id=correlation_id,
            status="REACHED",
            message=output.reason,
            metadata={
                "consensus_value_mm": output.consensus_value_mm,
                "median_all_mm": output.median_all_sources_mm,
                "accepted": output.accepted_sources,
                "outliers": output.outlier_sources,
            },
        )
    else:
        await write_audit_event(
            db=db,
            event_type=AuditEventType.CONSENSUS_FAILED,
            entity_type="CONSENSUS",
            entity_id=record.id,
            policy_id=policy_id,
            correlation_id=correlation_id,
            status="NO_CONSENSUS",
            message=output.reason,
            metadata={
                "median_all_mm": output.median_all_sources_mm,
                "accepted": output.accepted_sources,
                "outliers": output.outlier_sources,
            },
        )

    return record

