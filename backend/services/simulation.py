"""
services/simulation.py — Full pipeline orchestrator for POST /simulations.

This service runs the complete PS-F03 pipeline in one transaction:
  ingestion → consensus → trigger → settlement → wallet → audit

The simulation endpoint does NOT return hardcoded responses.
It exercises the real pipeline with whatever observations are provided.
"""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.policy import Policy
from models.wallet import Wallet
from schemas.simulation import (
    ConsensusResult as ConsensusSchema,
    LatencyResult,
    ObservationResult,
    SettlementResult,
    SimulationRequest,
    SimulationResponse,
    TelemetryResult,
    TriggerResult,
    WalletResult,
)
from services.consensus import SourceObservation, run_consensus
from services.ids import new_ulid
from services.settlement import settle_payout
from services.trigger import evaluate_trigger
from services.telemetry import ingest_telemetry
from services.providers import PayoutProvider
from schemas.telemetry import TelemetryIngestRequest


def _paise_to_inr_display(paise: int | None) -> str | None:
    if paise is None:
        return None
    rupees = paise // 100
    return f"₹{rupees:,}"


async def run_simulation(
    request: SimulationRequest,
    db: AsyncSession,
    provider: PayoutProvider | None = None,
) -> SimulationResponse:
    """
    Run the complete PS-F03 pipeline for a given simulation request.

    Args:
        request:  Simulation request (observations, policy, scenario).
        db:       Active async DB session.
        provider: Payout provider to use. Defaults to MockPayoutProvider (success).
                  Pass MockPayoutProvider(force_failure=True) to test failure paths.

    Steps:
      1. Fetch policy (with trigger_rule via eager load).
      2. Ingest each source observation as a TelemetryEvent.
      3. Run consensus evaluation.
      4. Run trigger evaluation.
      5. If triggered: run settlement via provider (idempotent).
      6. Return complete structured result.
    """
    correlation_id = new_ulid()
    pipeline_start = datetime.now(timezone.utc)

    # ── 1. Fetch policy ───────────────────────────────────────────────────────
    policy = await db.scalar(
        select(Policy)
        .options(selectinload(Policy.trigger_rule))
        .where(Policy.id == uuid.UUID(request.policy_id))
    )
    if policy is None:
        raise ValueError(f"Policy {request.policy_id!r} not found.")

    # ── 2. Ingest telemetry observations ─────────────────────────────────────
    obs_results: list[ObservationResult] = []
    accepted_observations: list[SourceObservation] = []
    ingested_at = datetime.now(timezone.utc)

    for obs in request.observations:
        # Generate a unique event_id per observation per simulation run
        event_id = f"{correlation_id}-{obs.source_id}"

        ingest_req = TelemetryIngestRequest(
            event_id=event_id,
            source_id=obs.source_id,
            region_id=request.region_id,
            observed_at=request.observed_at,
            metric="rainfall",
            value=obs.value,
            unit="mm",
        )

        try:
            result = await ingest_telemetry(
                request=ingest_req,
                correlation_id=correlation_id,
                db=db,
            )
            status = result.status  # "ACCEPTED" or "DUPLICATE"
        except ValueError as exc:
            status = "REJECTED"
            obs_results.append(ObservationResult(
                source_id=obs.source_id,
                value=obs.value,
                status="REJECTED",
                rejection_reason=str(exc),
            ))
            continue

        obs_results.append(ObservationResult(
            source_id=obs.source_id,
            value=obs.value,
            status=status,
        ))

        if status == "ACCEPTED":
            accepted_observations.append(
                SourceObservation(source_id=obs.source_id, value_mm=obs.value)
            )

    n_accepted = sum(1 for r in obs_results if r.status == "ACCEPTED")
    n_rejected = sum(1 for r in obs_results if r.status == "REJECTED")
    n_duplicates = sum(1 for r in obs_results if r.status == "DUPLICATE")

    telemetry_result = TelemetryResult(
        submitted=len(request.observations),
        accepted=n_accepted,
        rejected=n_rejected,
        duplicates=n_duplicates,
        observations=obs_results,
    )

    # ── 3. Consensus evaluation ───────────────────────────────────────────────
    consensus_record = await run_consensus(
        observations=accepted_observations,
        policy_id=request.policy_id,
        region_id=request.region_id,
        correlation_id=correlation_id,
        db=db,
    )

    consensus_schema = ConsensusSchema(
        status=str(consensus_record.status),
        median_all_sources=float(consensus_record.median_all_sources_mm) if consensus_record.median_all_sources_mm is not None else None,
        consensus_value_mm=float(consensus_record.consensus_value_mm) if consensus_record.consensus_value_mm is not None else None,
        accepted_sources=consensus_record.accepted_source_ids or [],
        outlier_sources=consensus_record.outlier_source_ids or [],
        reason=consensus_record.reason,
    )

    # ── 4. Trigger evaluation ─────────────────────────────────────────────────
    trigger_evaluated_at = datetime.now(timezone.utc)
    trigger_record = await evaluate_trigger(
        consensus_result=consensus_record,
        policy=policy,
        correlation_id=correlation_id,
        db=db,
    )

    trigger_schema = TriggerResult(
        status=str(trigger_record.trigger_status),
        threshold_mm=float(trigger_record.threshold_mm) if trigger_record.threshold_mm is not None else None,
        consensus_value_mm=float(trigger_record.consensus_value_mm) if trigger_record.consensus_value_mm is not None else None,
        reason=trigger_record.reason or "",
    )

    # ── 5. Settlement (idempotent) ─────────────────────────────────────────────
    settlement_schema = SettlementResult(
        status="SKIPPED",
        reason="Trigger did not fire.",
    )
    wallet_schema = WalletResult(credited=False)
    payout_completed_at: datetime | None = None

    from models.trigger import TriggerStatus
    if str(trigger_record.trigger_status) == "TRIGGERED":
        payout, idempotency_status = await settle_payout(
            trigger_evaluation=trigger_record,
            policy=policy,
            correlation_id=correlation_id,
            db=db,
            provider=provider,
        )
        payout_completed_at = datetime.now(timezone.utc)

        if payout is not None:
            if idempotency_status == "NEW":
                settlement_status = "SUCCESS"
            elif idempotency_status == "ALREADY_SETTLED":
                settlement_status = "DUPLICATE"
            elif idempotency_status == "FAILED":
                settlement_status = "FAILED"
            else:
                settlement_status = idempotency_status

            settlement_schema = SettlementResult(
                status=settlement_status,
                payout_id=str(payout.id),
                idempotency_status=idempotency_status,
                payout_amount_paise=payout.amount_paise,
                payout_amount_inr_display=_paise_to_inr_display(payout.amount_paise),
                reason=(
                    None if idempotency_status == "NEW"
                    else payout.failure_reason if idempotency_status == "FAILED"
                    else "Already settled."
                ),
            )
        else:
            # Payout was None because a payout for this policy already exists
            settlement_schema = SettlementResult(
                status="DUPLICATE",
                reason="Already settled for this policy.",
            )

            # Fetch updated wallet state with eager load for transactions
            wallet_rec = await db.scalar(
                select(Wallet)
                .where(Wallet.policy_id == uuid.UUID(request.policy_id))
                .options(selectinload(Wallet.transactions))
            )
            if wallet_rec:
                # Only show before/after when wallet was actually credited (NEW + provider SUCCESS)
                if idempotency_status == "NEW" and wallet_rec.transactions:
                    latest_tx = wallet_rec.transactions[0]
                    before = latest_tx.balance_before_paise
                    after = latest_tx.balance_after_paise
                    credited = True
                else:
                    before = None
                    after = wallet_rec.balance_paise
                    credited = False

                wallet_schema = WalletResult(
                    wallet_id=str(wallet_rec.id),
                    balance_before_paise=before if credited else wallet_rec.balance_paise,
                    balance_after_paise=after,
                    credited=credited,
                )
    elif str(trigger_record.trigger_status) == "TRIGGER_BLOCKED_NO_CONSENSUS":
        settlement_schema = SettlementResult(
            status="SKIPPED",
            reason="No consensus — trigger blocked. No payout.",
        )

    # ── 6. Latency tracking ────────────────────────────────────────────────────
    end_time = datetime.now(timezone.utc)

    def ms(a: datetime, b: datetime) -> int:
        return int((b - a).total_seconds() * 1000)

    latency = LatencyResult(
        observed_at=request.observed_at,
        received_at=ingested_at,
        trigger_evaluated_at=trigger_evaluated_at,
        payout_completed_at=payout_completed_at,
        detection_latency_ms=ms(request.observed_at, trigger_evaluated_at),
        settlement_latency_ms=ms(trigger_evaluated_at, payout_completed_at) if payout_completed_at else None,
        end_to_end_latency_ms=ms(request.observed_at, end_time),
    )

    # ── 7. AI event schema ─────────────────────────────────────────────────────
    ai_event = {
        "correlation_id": correlation_id,
        "policy_id": request.policy_id,
        "region_id": request.region_id,
        "scenario": request.scenario,
        "source_observations": [
            {"source_id": o.source_id, "value_mm": o.value}
            for o in request.observations
        ],
        "consensus_status": consensus_schema.status,
        "consensus_value_mm": consensus_schema.consensus_value_mm,
        "outlier_sources": consensus_schema.outlier_sources,
        "trigger_status": trigger_schema.status,
        "trigger_reason": trigger_schema.reason,
        "payout_amount_paise": settlement_schema.payout_amount_paise,
        "settlement_status": settlement_schema.status,
        "idempotency_status": settlement_schema.idempotency_status,
        # AI delivery mechanism: TBD (webhook / polling / DB read — not yet defined)
    }

    return SimulationResponse(
        correlation_id=correlation_id,
        scenario=request.scenario,
        policy_id=request.policy_id,
        telemetry=telemetry_result,
        consensus=consensus_schema,
        trigger=trigger_schema,
        settlement=settlement_schema,
        wallet=wallet_schema,
        latency=latency,
        ai_event=ai_event,
    )
