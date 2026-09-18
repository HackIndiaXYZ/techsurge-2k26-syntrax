"""
SYNTRAX AI Layer — Event Adapter

Maps the canonical backend event to internal AI module schemas.
"""
from datetime import datetime, timezone
from typing import Optional

from .schemas import (
    BackendEventContract,
    AnomalyInput,
    TelemetryReading,
    ExplanationInput,
    ConsensusInfo,
    TriggerInfo,
    PayoutInfo,
    WalletInfo,
    SettlementNotificationInput,
    ExplanationLanguage
)

def map_event_to_anomaly_input(event: BackendEventContract) -> Optional[AnomalyInput]:
    if not event.source_observations:
        return None
        
    readings = []
    # Map validated observations to establish state, default to ACCEPTED if not specified
    val_map = {v.get("source_code"): v.get("validation_state", "ACCEPTED") for v in event.validated_observations}
    
    # Check if there's any source observations at all to process
    for obs in event.source_observations:
        sc = obs.get("source_code", "UNKNOWN")
        readings.append(TelemetryReading(
            source_id=obs.get("source_id", sc),
            source_code=sc,
            value=obs.get("value", 0.0),
            unit=obs.get("unit", "mm"),
            observed_at=obs.get("observed_at", datetime.now(timezone.utc)),
            validation_state=val_map.get(sc, "REJECTED" if val_map else "ACCEPTED")
        ))
        
    if not readings:
        return None
        
    return AnomalyInput(
        region_id="SYN-REGION-001",
        metric="RAINFALL_MM",
        window_start=datetime.now(timezone.utc), # simplified for mapping
        window_end=datetime.now(timezone.utc),
        readings=readings
    )


def map_event_to_explanation_input(event: BackendEventContract) -> ExplanationInput:
    readings = []
    val_map = {v.get("source_code"): v.get("validation_state", "ACCEPTED") for v in event.validated_observations}
    for obs in event.source_observations:
        sc = obs.get("source_code", "UNKNOWN")
        readings.append(TelemetryReading(
            source_id=obs.get("source_id", sc),
            source_code=sc,
            value=obs.get("value", 0.0),
            unit=obs.get("unit", "mm"),
            observed_at=obs.get("observed_at", datetime.now(timezone.utc)),
            validation_state=val_map.get(sc, "ACCEPTED")
        ))

    consensus = ConsensusInfo(
        state=event.consensus_status,
        value=event.consensus_value,
        member_count=len(event.validated_observations)
    )

    trigger = None
    if event.trigger_status and event.trigger_status != "PENDING":
        trigger = TriggerInfo(
            outcome=event.trigger_status,
            reason_code=event.trigger_reason or "UNKNOWN",
            threshold_value=100.0 # Standard demo threshold
        )
        
    payout = None
    wallet = None
    if event.settlement_status and event.settlement_status != "PENDING":
        payout = PayoutInfo(
            state=event.settlement_status,
            amount_paise=event.payout_amount_paise or 0,
            is_retry=(event.idempotency_status == "DUPLICATE")
        )
        # Mock wallet info for demo consistency
        if event.settlement_status == "COMPLETED" and not payout.is_retry:
            wallet = WalletInfo(balance_before_paise=500000, balance_after_paise=500000 + (event.payout_amount_paise or 0))
        elif event.settlement_status == "COMPLETED" and payout.is_retry:
            wallet = WalletInfo(balance_before_paise=1500000, balance_after_paise=1500000)

    ts = event.timestamp
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except:
            ts = datetime.now(timezone.utc)

    return ExplanationInput(
        correlation_id=event.event_id,
        policy_id=event.policy_id,
        readings=readings,
        consensus=consensus,
        trigger=trigger,
        payout=payout,
        wallet=wallet,
        timestamp=ts
    )


def map_event_to_notification_input(event: BackendEventContract) -> Optional[SettlementNotificationInput]:
    if event.settlement_status != "COMPLETED":
        return None
        
    # Only notify if it wasn't a duplicate retry that had no new credit
    if event.idempotency_status == "DUPLICATE":
        return None

    return SettlementNotificationInput(
        policyholder_name="Ravi Kumar (Synthetic Farmer)",
        region_name="Kurnool Synthetic Micro-Region",
        payout_amount_paise=event.payout_amount_paise or 0,
        payout_state=event.settlement_status,
        consensus_value=event.consensus_value or 0.0,
        threshold_value=100.0,
        language=ExplanationLanguage.EN
    )
