import pytest
import os
from ai.schemas import (
    VoiceCallRequest,
    CallPurpose,
    ExplanationLanguage,
    CallState,
    BackendEventContract
)
from ai.voice import (
    execute_voice_assistance,
    _generate_script,
    MockVoiceProvider,
    TwilioVoiceProvider,
    _call_execution_keys
)
from ai.adapter import map_event_to_voice_request

@pytest.fixture(autouse=True)
def clear_idempotency_keys():
    """Clear the in-memory deduplication set before each test."""
    _call_execution_keys.clear()

def get_base_request(language=ExplanationLanguage.EN, event_id="EVT-1042"):
    return VoiceCallRequest(
        event_id=event_id,
        settlement_id="SET-1042",
        language=language,
        phone_number="+1234567890",
        purpose=CallPurpose.SETTLEMENT_ACKNOWLEDGEMENT,
        settlement_amount_paise=1000000,
        consensus_value=102.0,
        threshold_value=100.0,
        acknowledgement_status="NOT_ACKNOWLEDGED"
    )

def test_english_script():
    req = get_base_request(ExplanationLanguage.EN)
    script = _generate_script(req)
    assert "TerraFlux" in script.opening_message
    assert "102.0" in script.opening_message
    assert "100.0" in script.opening_message
    assert "10,000" in script.opening_message
    assert "Press 1" in script.acknowledgement_prompt

def test_hindi_script():
    req = get_base_request(ExplanationLanguage.HI)
    script = _generate_script(req)
    assert "टेराफ्लक्स" in script.opening_message
    assert "102.0" in script.opening_message
    assert "100.0" in script.opening_message
    assert "10,000" in script.opening_message
    assert "1 दबाएं" in script.acknowledgement_prompt

def test_telugu_script():
    req = get_base_request(ExplanationLanguage.TE)
    script = _generate_script(req)
    assert "టెర్రాఫ్లక్స్" in script.opening_message
    assert "102.0" in script.opening_message
    assert "100.0" in script.opening_message
    assert "10,000" in script.opening_message
    assert "1 నొక్కండి" in script.acknowledgement_prompt

def test_no_fabricated_data():
    # Verify that the generated script strictly relies on requested values
    req = VoiceCallRequest(
        event_id="EVT-999",
        language=ExplanationLanguage.EN,
        phone_number="+1234567890",
        purpose=CallPurpose.SETTLEMENT_ACKNOWLEDGEMENT,
        settlement_amount_paise=55000,  # 550 rupees
        consensus_value=85.5,
        threshold_value=80.0,
        acknowledgement_status="NOT_ACKNOWLEDGED"
    )
    script = _generate_script(req)
    assert "85.5" in script.opening_message
    assert "80.0" in script.opening_message
    assert "550" in script.opening_message
    assert "102" not in script.opening_message
    assert "10,000" not in script.opening_message

def test_duplicate_call_prevention():
    req = get_base_request()
    provider = MockVoiceProvider()
    
    # First call should succeed (INITIATED state)
    res1 = execute_voice_assistance(req, force_provider=provider)
    assert res1.status == CallState.INITIATED
    
    # Second call should be blocked by idempotency check
    res2 = execute_voice_assistance(req, force_provider=provider)
    assert res2.status == CallState.NOT_REQUIRED
    assert res2.error_code == "DUPLICATE_CALL"

def test_mock_provider_success():
    req = get_base_request()
    res = execute_voice_assistance(req, force_provider=MockVoiceProvider())
    assert res.provider == "mock"
    assert res.status == CallState.INITIATED

def test_twilio_provider_failure_no_creds():
    # Force Twilio provider without env vars set
    req = get_base_request()
    provider = TwilioVoiceProvider() # should disable itself safely
    # Explicitly run make_call to test failure
    res = provider.make_call(req, _generate_script(req))
    assert res.status == CallState.FAILED
    assert res.error_code == "TWILIO_NOT_CONFIGURED"

# --- Adapter Tests ---

def get_base_backend_event() -> BackendEventContract:
    return BackendEventContract(
        event_id="EVT-123",
        policy_id="POL-123",
        timestamp="2026-09-18T10:00:00Z",
        consensus_value=102.0,
        consensus_status="ACHIEVED",
        trigger_status="TRIGGERED",
        payout_amount_paise=1000000,
        settlement_status="COMPLETED",
        wallet_acknowledgement_status="NOT_ACKNOWLEDGED"
    )

def test_call_only_after_unacknowledged_settlement():
    event = get_base_backend_event()
    req = map_event_to_voice_request(event, "+123")
    assert req is not None
    assert req.settlement_amount_paise == 1000000

def test_no_call_after_acknowledgement():
    event = get_base_backend_event()
    event.wallet_acknowledgement_status = "ACKNOWLEDGED"
    req = map_event_to_voice_request(event, "+123")
    assert req is None

def test_no_call_for_blocked_or_unsettled():
    event = get_base_backend_event()
    event.settlement_status = "PENDING"
    req = map_event_to_voice_request(event, "+123")
    assert req is None
    
    event.settlement_status = "FAILED"
    req = map_event_to_voice_request(event, "+123")
    assert req is None

def test_no_call_for_no_consensus():
    event = get_base_backend_event()
    event.consensus_status = "NO_CONSENSUS"
    req = map_event_to_voice_request(event, "+123")
    assert req is None
    
def test_no_call_for_duplicate_idempotent_event():
    event = get_base_backend_event()
    event.idempotency_status = "DUPLICATE"
    req = map_event_to_voice_request(event, "+123")
    assert req is None
