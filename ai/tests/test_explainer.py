import pytest

from ai.explainer import explain_event
from ai.schemas import ExplanationInput, ExplanationLanguage, ConsensusInfo, TriggerInfo, PayoutInfo

def test_explain_clean_trigger_english():
    input_data = ExplanationInput(
        correlation_id="test-123",
        policy_id="SYN-POLICY-RAIN-001",
        payout=PayoutInfo(state="COMPLETED", amount_paise=1000000),
        consensus=ConsensusInfo(state="ACHIEVED", value=102.0, member_count=3),
        trigger=TriggerInfo(outcome="TRIGGERED", reason_code="THRESHOLD_MET", threshold_value=100.0)
    )
    
    result = explain_event(input_data, ExplanationLanguage.EN)
    
    assert result.is_synthetic is True
    assert "Synthetic Payout Completed" in result.title
    assert "₹10,000" in result.body
    assert "102.0" in result.body
    
def test_explain_no_consensus_hindi():
    input_data = ExplanationInput(
        correlation_id="test-124",
        policy_id="SYN-POLICY-RAIN-001",
        consensus=ConsensusInfo(state="NO_CONSENSUS", member_count=0),
        trigger=TriggerInfo(outcome="NO_CONSENSUS", reason_code="CONSENSUS_NOT_ACHIEVED", threshold_value=100.0)
    )
    
    result = explain_event(input_data, ExplanationLanguage.HI)
    
    assert result.language == ExplanationLanguage.HI
    assert "सहमति नहीं" in result.title
    assert "मौसम स्रोत असहमत" in result.title
