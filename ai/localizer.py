"""
SYNTRAX AI Layer — Local-Language Settlement Notification

Generates structured notification messages in local languages
(English, Hindi, Telugu) AFTER settlement is completed.

CRITICAL BOUNDARY:
  - This module is called AFTER the payout is COMPLETED.
  - It communicates an already-established result.
  - It does NOT authorize, modify, or reverse any payout.
  - If this module fails, the payout remains completed and valid.

Implementation:
  Template-based string generation. No LLM or external API required.
  Suitable for display as text OR as input to a TTS engine.
"""

from __future__ import annotations

import logging

from .schemas import (
    ExplanationLanguage,
    SettlementNotificationInput,
    SettlementNotificationOutput,
)

logger = logging.getLogger(__name__)


def generate_settlement_message(
    input_data: SettlementNotificationInput,
) -> SettlementNotificationOutput:
    """Generate a local-language notification for a completed settlement.

    Args:
        input_data: Settlement details from the deterministic pipeline.

    Returns:
        SettlementNotificationOutput with formatted message.
        Always succeeds with a deterministic fallback.

    This function is POST-SETTLEMENT communication only. It does NOT
    participate in the financial decision process.
    """
    if input_data.payout_state != "COMPLETED":
        logger.warning(
            "Settlement notification requested for non-completed payout "
            "(state=%s). Generating informational message.",
            input_data.payout_state,
        )

    try:
        amount_display = _format_inr(input_data.payout_amount_paise)

        if input_data.language == ExplanationLanguage.HI:
            message = _hindi_message(input_data, amount_display)
        elif input_data.language == ExplanationLanguage.TE:
            message = _telugu_message(input_data, amount_display)
        else:
            message = _english_message(input_data, amount_display)

        return SettlementNotificationOutput(
            message=message,
            language=input_data.language,
            amount_display=amount_display,
            is_synthetic=True,
            fallback_used=False,
            method="template",
        )

    except Exception as exc:
        logger.warning(
            "Settlement notification generation failed: %s", exc,
            exc_info=True,
        )
        return _fallback_notification(input_data)


# ============================================================
# Language Templates
# ============================================================

def _english_message(
    data: SettlementNotificationInput,
    amount: str,
) -> str:
    return (
        f"Dear {data.policyholder_name}, "
        f"your parametric rainfall insurance policy for {data.region_name} "
        f"has been triggered. "
        f"Weather consensus confirmed {data.consensus_value}{data.consensus_unit} "
        f"of rainfall, exceeding the {data.threshold_value}{data.consensus_unit} threshold. "
        f"A synthetic payout of {amount} has been credited to your wallet. "
        f"Please note: this is a simulated transaction — no real money is involved. "
        f"The parametric payout is based on the predefined weather index "
        f"and does not individually assess actual loss."
    )


def _hindi_message(
    data: SettlementNotificationInput,
    amount: str,
) -> str:
    return (
        f"प्रिय {data.policyholder_name}, "
        f"आपकी {data.region_name} क्षेत्र की पैरामीट्रिक वर्षा बीमा पॉलिसी "
        f"सक्रिय हो गई है। "
        f"मौसम सहमति ने {data.consensus_value}{data.consensus_unit} वर्षा की "
        f"पुष्टि की, जो {data.threshold_value}{data.consensus_unit} की सीमा से अधिक है। "
        f"{amount} का सिंथेटिक भुगतान आपके वॉलेट में जमा कर दिया गया है। "
        f"कृपया ध्यान दें: यह एक अनुकरणित लेनदेन है — कोई वास्तविक धन शामिल नहीं है। "
        f"पैरामीट्रिक भुगतान पूर्वनिर्धारित मौसम सूचकांक पर आधारित है "
        f"और वास्तविक नुकसान का व्यक्तिगत रूप से आकलन नहीं करता।"
    )


def _telugu_message(
    data: SettlementNotificationInput,
    amount: str,
) -> str:
    return (
        f"ప్రియమైన {data.policyholder_name}, "
        f"మీ {data.region_name} ప్రాంతపు పారామెట్రిక్ వర్షపాతం బీమా పాలసీ "
        f"ట్రిగ్గర్ అయింది. "
        f"వాతావరణ ఏకాభిప్రాయం {data.consensus_value}{data.consensus_unit} "
        f"వర్షపాతాన్ని నిర్ధారించింది, ఇది {data.threshold_value}{data.consensus_unit} "
        f"పరిమితిని మించింది. "
        f"{amount} సింథటిక్ చెల్లింపు మీ వాలెట్‌కు జమ చేయబడింది. "
        f"దయచేసి గమనించండి: ఇది అనుకరణ లావాదేవీ — నిజమైన డబ్బు ఏదీ ఉపయోగించబడదు. "
        f"పారామెట్రిక్ చెల్లింపు ముందుగా నిర్ణయించిన వాతావరణ సూచిక ఆధారంగా ఉంటుంది."
    )


# ============================================================
# Utility
# ============================================================

def _format_inr(paise: int) -> str:
    """Format paise as INR display string."""
    rupees = paise / 100
    if rupees == int(rupees):
        return f"₹{int(rupees):,}"
    return f"₹{rupees:,.2f}"


def _fallback_notification(
    data: SettlementNotificationInput,
) -> SettlementNotificationOutput:
    """Safe fallback notification."""
    amount = _format_inr(data.payout_amount_paise)
    return SettlementNotificationOutput(
        message=(
            f"Settlement notification for {data.policyholder_name}: "
            f"{amount} (synthetic). Details available in the audit trail."
        ),
        language=data.language,
        amount_display=amount,
        is_synthetic=True,
        fallback_used=True,
        method="fallback",
    )

