import pytest
from datetime import datetime, timezone

from ai.schemas import BackendEventContract, FrontendAIResponse
from ai.router import process_backend_event
from ai.fixtures import ALL_SCENARIOS

def convert_fixture_to_backend_event(scenario: dict) -> BackendEventContract:
    """Helper to simulate the backend sending the canonical event contract based on the fixture."""
    
    # 1. Map telemetry
    source_obs = []
    val_obs = []
    
    for r in scenario.get("readings", []):
        obs = {
            "source_id": r["source_code"],
            "source_code": r["source_code"],
            "value": r["value"],
            "unit": r["unit"],
            "observed_at": datetime.now(timezone.utc)
        }
        source_obs.append(obs)
        
        # Add to validated if accepted
        expected_val = scenario["expected"].get("validation", {}).get(r["source_code"], "REJECTED")
        if expected_val == "ACCEPTED":
            v_obs = obs.copy()
            v_obs["validation_state"] = "ACCEPTED"
            val_obs.append(v_obs)
        elif expected_val == "DUPLICATE":
            v_obs = obs.copy()
            v_obs["validation_state"] = "DUPLICATE"
            val_obs.append(v_obs)
            
    # Add duplicate reading if it exists
    if "duplicate_reading" in scenario:
        dup = scenario["duplicate_reading"]
        obs = {
            "source_id": dup["source_code"],
            "source_code": dup["source_code"],
            "value": dup["value"],
            "unit": dup["unit"],
            "observed_at": datetime.now(timezone.utc)
        }
        source_obs.append(obs)
        v_obs = obs.copy()
        v_obs["validation_state"] = "DUPLICATE"
        val_obs.append(v_obs)

    # 2. Map consensus
    consensus = scenario["expected"].get("consensus", {})
    consensus_value = consensus.get("value")
    consensus_status = consensus.get("state", "PENDING")
    outlier = consensus.get("outlier")
    
    # 3. Map trigger
    trigger = scenario["expected"].get("trigger", {})
    trigger_status = trigger.get("outcome", "PENDING")
    trigger_reason = trigger.get("reason_code")
    
    # 4. Map payout
    payout = scenario["expected"].get("payout") or {}
    payout_amount = payout.get("amount_paise")
    settlement_status = payout.get("state", "PENDING")
    
    # 5. Idempotency (scenario 6 is payout-retry)
    idem = "SETTLED" if scenario["name"] == "payout-retry" else None
    if scenario["name"] == "duplicate-event":
        idem = "DUPLICATE"
    if scenario["name"] == "payout-retry":
        idem = "DUPLICATE"  # The execute call is idempotent
        settlement_status = "COMPLETED"
        payout_amount = 1000000

    return BackendEventContract(
        event_id=f"evt_{scenario['name']}",
        policy_id="SYN-POLICY-RAIN-001",
        timestamp=datetime.now(timezone.utc),
        source_observations=source_obs,
        validated_observations=val_obs,
        consensus_value=consensus_value,
        consensus_status=consensus_status,
        outlier_sources=[outlier] if outlier else [],
        trigger_status=trigger_status,
        trigger_reason=trigger_reason,
        payout_amount_paise=payout_amount,
        settlement_status=settlement_status,
        idempotency_status=idem
    )


@pytest.mark.parametrize("scenario", ALL_SCENARIOS)
def test_integration_scenarios(scenario):
    """Test that every scenario successfully runs through the unified AI integration pipeline."""
    
    # 1. Convert fixture to backend contract
    contract = convert_fixture_to_backend_event(scenario)
    
    # 2. Process via AI router unified endpoint
    response = process_backend_event(contract)
    
    # 3. Assertions
    assert isinstance(response, FrontendAIResponse)
    assert response.is_advisory is True
    assert response.is_synthetic is True
    assert response.basis_risk_notice != ""
    assert response.fallback_used is False
    
    # All scenarios should generate an explanation
    assert response.explanation_en is not None
    assert response.explanation_hi is not None
    assert response.explanation_te is not None
    
    # Check explanations have right correlation ids
    assert response.explanation_en.correlation_id == contract.event_id
    
    # Check anomalies if there are observations
    if contract.source_observations:
        assert response.anomaly is not None
        assert len(response.anomaly.source_scores) == len(contract.source_observations)
        
    # Check notifications
    if contract.settlement_status == "COMPLETED" and contract.idempotency_status != "DUPLICATE":
        assert response.notification_en is not None
        assert response.notification_hi is not None
        assert response.notification_te is not None
        assert "₹10,000" in response.notification_en.message
    else:
        # No new credit should mean no standard settlement notification
        assert response.notification_en is None
