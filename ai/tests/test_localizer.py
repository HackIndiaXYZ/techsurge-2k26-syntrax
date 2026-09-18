import pytest

from ai.localizer import generate_settlement_message
from ai.schemas import SettlementNotificationInput, ExplanationLanguage

def test_generate_settlement_message_english():
    input_data = SettlementNotificationInput(
        policyholder_name="Ravi Kumar (Synthetic Farmer)",
        region_name="Kurnool Synthetic Micro-Region",
        payout_amount_paise=1000000,
        payout_state="COMPLETED",
        consensus_value=102.0,
        threshold_value=100.0,
        language=ExplanationLanguage.EN
    )
    
    result = generate_settlement_message(input_data)
    
    assert "₹10,000" in result.message
    assert "102.0mm" in result.message
    assert "simulated transaction" in result.message
    assert result.is_synthetic is True

def test_generate_settlement_message_telugu():
    input_data = SettlementNotificationInput(
        policyholder_name="Ravi Kumar (Synthetic Farmer)",
        region_name="Kurnool Synthetic Micro-Region",
        payout_amount_paise=1000000,
        payout_state="COMPLETED",
        consensus_value=102.0,
        threshold_value=100.0,
        language=ExplanationLanguage.TE
    )
    
    result = generate_settlement_message(input_data)
    
    assert result.language == ExplanationLanguage.TE
    assert "₹10,000" in result.message
    assert "సింథటిక్" in result.message
