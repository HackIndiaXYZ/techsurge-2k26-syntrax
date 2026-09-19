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
from services.ids import new_uuid


TOLERANCE_MM: float = 5.0   # inclusive: abs(value - median) <= TOLERANCE
QUORUM: int = 2             # minimum accepted sources


@dataclass
class SourceObservation:
    source_id: str
    value_mm: float
    observed_at: datetime | None = None


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


def evaluate_consensus(
    observations: list[SourceObservation],
    stale_threshold_seconds: int = 7200,
    evaluated_at: datetime | None = None
) -> ConsensusOutput:
    if evaluated_at is None:
        evaluated_at = datetime.now(timezone.utc)
        
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

    # Filter out invalid, stale, or duplicate sources
    import math
    valid_obs = {}
    
    for obs in observations:
        # Defect 1: Deduplication (keep first encountered per source, or just safely overwrite since they should be identical if they happen, but to be deterministic, keep the first one seen. Wait, a safer approach is to ignore duplicates if source_id already processed)
        if obs.source_id in valid_obs:
            continue
            
        # Defect 2: Non-finite values
        if not math.isfinite(obs.value_mm):
            continue
            
        # Defect 3: Negative rainfall
        if obs.value_mm < 0:
            continue
            
        # Defect 4: Freshness check
        if obs.observed_at is None:
            continue
        age_seconds = (evaluated_at - obs.observed_at).total_seconds()
        if age_seconds < 0 or age_seconds > stale_threshold_seconds:
            continue
                
        valid_obs[obs.source_id] = obs

    deduped_observations = list(valid_obs.values())
    
    if len(deduped_observations) == 0:
        return ConsensusOutput(
            status=ConsensusStatus.NO_CONSENSUS,
            median_all_sources_mm=None,
            consensus_value_mm=None,
            accepted_sources=[],
            outlier_sources=[],
            reason="No valid, fresh observations available for consensus.",
            source_count_total=n,
            source_count_accepted=0,
            source_count_outliers=0,
        )

    values = [o.value_mm for o in deduped_observations]

    # Step 1: Median of ALL valid sources
    median_all = statistics.median(values)

    # Step 2: Classify each source
    accepted: list[SourceObservation] = []
    outliers: list[SourceObservation] = []

    for obs in deduped_observations:
        diff = abs(obs.value_mm - median_all)
        if diff <= TOLERANCE_MM:    # INCLUSIVE tolerance
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
            f"Consensus reached. {len(accepted)}/{len(deduped_observations)} sources within tolerance. "
            f"Consensus value: {consensus_value:.1f} mm."
        ),
        source_count_total=n,
        source_count_accepted=len(accepted),
        source_count_outliers=len(outliers),
    )


async def run_consensus(
    observations: list[SourceObservation],
    policy_id,
    region_id,
    correlation_id: str,
    db: AsyncSession,
) -> ConsensusResult:
    """
    Evaluate consensus, persist the result, write audit events, and return the DB record.
    """
    from config import get_settings
    settings = get_settings()
    
    evaluated_at = datetime.now(timezone.utc)
    output = evaluate_consensus(
        observations=observations, 
        stale_threshold_seconds=settings.stale_threshold_seconds,
        evaluated_at=evaluated_at
    )

    # Convert IDs to UUID if they're strings
    import uuid as uuid_mod
    if isinstance(policy_id, str):
        policy_id = uuid_mod.UUID(policy_id)
    if isinstance(region_id, str):
        region_id = uuid_mod.UUID(region_id)

    # Persist ConsensusResult
    record = ConsensusResult(
        id=new_uuid(),
        policy_id=policy_id,
        region_id=region_id,
        metric="RAINFALL_MM",
        window_start=evaluated_at,
        window_end=evaluated_at,
        quorum=2,
        status=output.status.value,
        median_all_sources_mm=output.median_all_sources_mm,
        consensus_value_mm=output.consensus_value_mm,
        source_count_total=output.source_count_total,
        source_count_accepted=output.source_count_accepted,
        source_count_outliers=output.source_count_outliers,
        accepted_source_ids=output.accepted_sources,
        outlier_source_ids=output.outlier_sources,
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
            entity_id=str(record.id),
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
            entity_id=str(record.id),
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
