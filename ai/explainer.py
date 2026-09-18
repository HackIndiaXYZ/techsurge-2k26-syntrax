"""
SYNTRAX AI Layer — Event Explanation Engine

Generates human-readable explanations of deterministic pipeline events.
Template-based — NO LLM REQUIRED. Same inputs always produce same outputs.

CRITICAL BOUNDARY:
  - This module READS structured evidence from the deterministic pipeline.
  - It does NOT produce, modify, or reinterpret evidence.
  - It does NOT invent facts beyond what is in the input.
  - If this module fails, the audit trail and raw data remain authoritative.

Supported explanation types:
  1. Full pipeline explanation ("Why did this payout happen?")
  2. Consensus explanation ("How was the weather data verified?")
  3. Trigger explanation ("Why did the policy trigger / not trigger?")
  4. Rejection explanation ("Why was this source excluded?")
"""

from __future__ import annotations

import logging
from datetime import datetime

from .schemas import (
    ExplanationInput,
    ExplanationLanguage,
    ExplanationOutput,
)

logger = logging.getLogger(__name__)

# Basis risk disclosure — mandatory on every explanation
_BASIS_RISK_NOTICE = (
    "This parametric payout is based on the predefined weather index "
    "and does not individually assess actual loss."
)


def explain_event(
    input_data: ExplanationInput,
    language: ExplanationLanguage = ExplanationLanguage.EN,
) -> ExplanationOutput:
    """Generate a human-readable explanation of a pipeline event.

    Args:
        input_data: Structured evidence from the deterministic pipeline.
        language: Target language for the explanation.

    Returns:
        ExplanationOutput with title, body, and evidence summary.
        Always succeeds — returns a fallback explanation on any error.

    This function is ADVISORY. It communicates deterministic decisions
    in human-readable form. It does not make or modify decisions.
    """
    try:
        if language == ExplanationLanguage.EN:
            return _explain_english(input_data)
        elif language == ExplanationLanguage.HI:
            return _explain_hindi(input_data)
        elif language == ExplanationLanguage.TE:
            return _explain_telugu(input_data)
        else:
            return _explain_english(input_data)
    except Exception as exc:
        logger.warning(
            "Explanation generation failed (advisory, continuing): %s", exc,
            exc_info=True,
        )
        return _fallback_explanation(input_data, language)


def _explain_english(input_data: ExplanationInput) -> ExplanationOutput:
    """Generate English explanation from structured evidence."""

    sections: list[str] = []
    evidence: dict = {}
    title = ""

    # --- Determine the overall event type ---
    if input_data.payout and input_data.payout.state == "COMPLETED":
        title = _en_payout_title(input_data)
        sections.append(_en_payout_section(input_data))
    elif input_data.trigger and input_data.trigger.outcome == "TRIGGERED":
        title = "Policy Triggered — Awaiting Settlement"
        sections.append(_en_trigger_section(input_data))
    elif input_data.trigger and input_data.trigger.outcome == "NOT_MET":
        title = "Policy Evaluated — Threshold Not Met"
        sections.append(_en_not_met_section(input_data))
    elif input_data.trigger and input_data.trigger.outcome == "NO_CONSENSUS":
        title = "Policy Not Evaluated — No Weather Consensus"
        sections.append(_en_no_consensus_trigger_section(input_data))
    elif input_data.trigger and input_data.trigger.outcome == "ALREADY_TRIGGERED":
        title = "Policy Already Triggered — No Additional Payout"
        sections.append(_en_already_triggered_section(input_data))
    elif input_data.consensus and input_data.consensus.state == "NO_CONSENSUS":
        title = "Weather Sources Disagree — No Consensus Reached"
        sections.append(_en_no_consensus_section(input_data))
    elif input_data.consensus and input_data.consensus.state == "ACHIEVED":
        title = "Weather Consensus Established"
        sections.append(_en_consensus_section(input_data))
    else:
        title = "Telemetry Received"
        sections.append(_en_telemetry_section(input_data))

    # --- Build evidence summary (facts only, never invented) ---
    if input_data.readings:
        evidence["sources"] = [
            {"source": r.source_code, "value": r.value, "state": r.validation_state}
            for r in input_data.readings
        ]
    if input_data.consensus:
        evidence["consensus"] = {
            "state": input_data.consensus.state,
            "value": input_data.consensus.value,
            "members": input_data.consensus.member_count,
        }
    if input_data.trigger:
        evidence["trigger"] = {
            "outcome": input_data.trigger.outcome,
            "threshold": input_data.trigger.threshold_value,
            "operator": input_data.trigger.threshold_operator,
        }
    if input_data.payout:
        evidence["payout"] = {
            "state": input_data.payout.state,
            "amount_inr": input_data.payout.amount_paise / 100,
        }
    if input_data.wallet:
        evidence["wallet"] = {
            "before_inr": input_data.wallet.balance_before_paise / 100,
            "after_inr": input_data.wallet.balance_after_paise / 100,
        }

    body = "\n\n".join(sections)

    return ExplanationOutput(
        correlation_id=input_data.correlation_id,
        language=ExplanationLanguage.EN,
        title=title,
        body=body,
        evidence_summary=evidence,
        basis_risk_notice=_BASIS_RISK_NOTICE,
        is_synthetic=True,
        method="template",
        fallback_used=False,
    )


# ============================================================
# English Template Sections
# ============================================================

def _en_payout_title(data: ExplanationInput) -> str:
    if data.payout and data.payout.is_retry:
        return "Payout Retry — Idempotent Return (No Additional Credit)"
    return "Synthetic Payout Completed"


def _en_payout_section(data: ExplanationInput) -> str:
    parts = [f"Policyholder {data.policyholder_name} in {data.region_name} "
             f"received a synthetic settlement."]

    if data.readings:
        source_list = ", ".join(
            f"{r.source_code}: {r.value}{r.unit}" for r in data.readings
            if r.validation_state == "ACCEPTED"
        )
        parts.append(f"Weather sources reported: {source_list}.")

    if data.consensus and data.consensus.value is not None:
        parts.append(
            f"The {data.consensus.member_count}-source consensus value was "
            f"{data.consensus.value}{data.consensus.unit} "
            f"(state: {data.consensus.state})."
        )

    if data.trigger:
        parts.append(
            f"The policy trigger threshold of "
            f"{data.trigger.threshold_value}{data.trigger.threshold_unit} "
            f"was {'met' if data.trigger.outcome == 'TRIGGERED' else 'not met'} "
            f"(outcome: {data.trigger.outcome})."
        )

    if data.payout:
        amount_display = _format_inr(data.payout.amount_paise)
        parts.append(
            f"A synthetic payout of {amount_display} was {data.payout.state.lower()}."
        )
        if data.payout.is_retry:
            parts.append(
                "This was a retry request. The original payout was returned "
                "idempotently — no additional credit was applied."
            )

    if data.wallet:
        before = _format_inr(data.wallet.balance_before_paise)
        after = _format_inr(data.wallet.balance_after_paise)
        parts.append(
            f"Synthetic wallet balance changed from {before} to {after}."
        )

    parts.append(
        "Note: All amounts are synthetic. "
        + _BASIS_RISK_NOTICE
    )

    return " ".join(parts)


def _en_trigger_section(data: ExplanationInput) -> str:
    parts = []
    if data.consensus and data.consensus.value is not None:
        parts.append(
            f"Weather consensus value of {data.consensus.value}mm "
            f"met the policy threshold of {data.trigger.threshold_value}mm."
        )
    parts.append("The policy has been triggered. Settlement is pending.")
    return " ".join(parts)


def _en_not_met_section(data: ExplanationInput) -> str:
    parts = []
    if data.consensus and data.consensus.value is not None:
        parts.append(
            f"Weather consensus value of {data.consensus.value}mm "
            f"did not meet the policy threshold of "
            f"{data.trigger.threshold_value}mm."
        )
    parts.append("No payout will be issued for this measurement window.")
    return " ".join(parts)


def _en_no_consensus_section(data: ExplanationInput) -> str:
    parts = [
        "Weather sources provided conflicting readings that could not "
        "establish a reliable consensus."
    ]
    if data.readings:
        readings_str = ", ".join(
            f"{r.source_code}: {r.value}{r.unit}" for r in data.readings
        )
        parts.append(f"Source readings: {readings_str}.")
    parts.append(
        "No policy evaluation or payout will occur without consensus. "
        "This is a safety mechanism."
    )
    return " ".join(parts)


def _en_no_consensus_trigger_section(data: ExplanationInput) -> str:
    return (
        "The policy could not be evaluated because no weather consensus "
        "was achieved. When sources disagree beyond the tolerance threshold, "
        "the system does not trigger a payout. This protects against "
        "unreliable weather data."
    )


def _en_already_triggered_section(data: ExplanationInput) -> str:
    return (
        "This policy has already been triggered and a payout has been "
        "issued. Parametric policies pay at most once per triggering event. "
        "Additional consensus results for the same policy do not create "
        "additional payouts."
    )


def _en_telemetry_section(data: ExplanationInput) -> str:
    if not data.readings:
        return "Telemetry data has been received and is being processed."
    readings_str = ", ".join(
        f"{r.source_code}: {r.value}{r.unit} ({r.validation_state})"
        for r in data.readings
    )
    return f"Telemetry received from sources: {readings_str}."


def _en_consensus_section(data: ExplanationInput) -> str:
    if data.consensus and data.consensus.value is not None:
        members_str = ""
        if data.consensus.members:
            members_str = " Sources: " + ", ".join(
                f"{m.get('source_code', '?')}: {m.get('value', '?')}mm "
                f"({m.get('role', 'MEMBER')})"
                for m in data.consensus.members
            ) + "."
        return (
            f"A {data.consensus.member_count}-source consensus was "
            f"established with value {data.consensus.value}mm.{members_str}"
        )
    return "Weather consensus is being computed."


# ============================================================
# Hindi Templates
# ============================================================

def _explain_hindi(data: ExplanationInput) -> ExplanationOutput:
    """Generate Hindi explanation from structured evidence."""
    en_result = _explain_english(data)

    title, body = _translate_to_hindi(data, en_result)

    return ExplanationOutput(
        correlation_id=data.correlation_id,
        language=ExplanationLanguage.HI,
        title=title,
        body=body,
        evidence_summary=en_result.evidence_summary,
        basis_risk_notice=(
            "यह पैरामीट्रिक भुगतान पूर्वनिर्धारित मौसम सूचकांक पर आधारित है "
            "और वास्तविक नुकसान का व्यक्तिगत रूप से आकलन नहीं करता।"
        ),
        is_synthetic=True,
        method="template",
        fallback_used=False,
    )


def _translate_to_hindi(
    data: ExplanationInput,
    en: ExplanationOutput,
) -> tuple[str, str]:
    """Map English template results to Hindi equivalents."""
    if data.payout and data.payout.state == "COMPLETED":
        amount = _format_inr(data.payout.amount_paise)
        title = "सिंथेटिक भुगतान पूर्ण"
        body = (
            f"पॉलिसीधारक {data.policyholder_name}, क्षेत्र {data.region_name} को "
            f"{amount} का सिंथेटिक भुगतान प्राप्त हुआ।"
        )
        if data.consensus and data.consensus.value is not None:
            body += (
                f" मौसम सहमति मान: {data.consensus.value}mm "
                f"(सीमा: {data.trigger.threshold_value}mm)।"
                if data.trigger else ""
            )
        body += (
            " यह राशि सिंथेटिक है। पैरामीट्रिक भुगतान पूर्वनिर्धारित "
            "मौसम सूचकांक पर आधारित है।"
        )
        if data.payout.is_retry:
            body += " यह एक पुनः प्रयास था — कोई अतिरिक्त क्रेडिट नहीं।"
        return title, body

    if data.consensus and data.consensus.state == "NO_CONSENSUS":
        return (
            "मौसम स्रोत असहमत — कोई सहमति नहीं",
            "मौसम स्रोतों ने परस्पर विरोधी आँकड़े दिए। "
            "सहमति के बिना कोई भुगतान नहीं होगा।"
        )

    if data.trigger and data.trigger.outcome == "NOT_MET":
        return (
            "पॉलिसी सीमा पूरी नहीं हुई",
            f"मौसम सहमति मान ने {data.trigger.threshold_value}mm की "
            f"पॉलिसी सीमा को पूरा नहीं किया। कोई भुगतान नहीं।"
        )

    return "टेलीमेट्री प्राप्त", "मौसम डेटा प्राप्त हुआ और संसाधित हो रहा है।"


# ============================================================
# Telugu Templates
# ============================================================

def _explain_telugu(data: ExplanationInput) -> ExplanationOutput:
    """Generate Telugu explanation from structured evidence."""
    en_result = _explain_english(data)

    title, body = _translate_to_telugu(data, en_result)

    return ExplanationOutput(
        correlation_id=data.correlation_id,
        language=ExplanationLanguage.TE,
        title=title,
        body=body,
        evidence_summary=en_result.evidence_summary,
        basis_risk_notice=(
            "ఈ పారామెట్రిక్ చెల్లింపు ముందుగా నిర్ణయించిన వాతావరణ సూచిక "
            "ఆధారంగా ఉంటుంది మరియు వాస్తవ నష్టాన్ని వ్యక్తిగతంగా అంచనా వేయదు."
        ),
        is_synthetic=True,
        method="template",
        fallback_used=False,
    )


def _translate_to_telugu(
    data: ExplanationInput,
    en: ExplanationOutput,
) -> tuple[str, str]:
    """Map English template results to Telugu equivalents."""
    if data.payout and data.payout.state == "COMPLETED":
        amount = _format_inr(data.payout.amount_paise)
        title = "సింథటిక్ చెల్లింపు పూర్తయింది"
        body = (
            f"పాలసీదారు {data.policyholder_name}, ప్రాంతం {data.region_name}కు "
            f"{amount} సింథటిక్ చెల్లింపు జరిగింది."
        )
        body += (
            " అన్ని మొత్తాలు సింథటిక్. పారామెట్రిక్ చెల్లింపు ముందుగా "
            "నిర్ణయించిన వాతావరణ సూచిక ఆధారంగా ఉంటుంది."
        )
        return title, body

    if data.consensus and data.consensus.state == "NO_CONSENSUS":
        return (
            "వాతావరణ మూలాలు అంగీకరించలేదు",
            "వాతావరణ మూలాలు పరస్పర విరుద్ధమైన రీడింగ్‌లను అందించాయి. "
            "ఏకాభిప్రాయం లేకుండా చెల్లింపు జరగదు."
        )

    return "టెలిమెట్రీ అందింది", "వాతావరణ డేటా అందింది, ప్రాసెస్ అవుతోంది."


# ============================================================
# Utility
# ============================================================

def _format_inr(paise: int) -> str:
    """Format paise as INR display string."""
    rupees = paise / 100
    if rupees == int(rupees):
        return f"₹{int(rupees):,}"
    return f"₹{rupees:,.2f}"


def _fallback_explanation(
    data: ExplanationInput,
    language: ExplanationLanguage,
) -> ExplanationOutput:
    """Safe fallback when explanation generation fails."""
    return ExplanationOutput(
        correlation_id=data.correlation_id,
        language=language,
        title="Event Recorded",
        body=(
            "An event has been processed by the deterministic pipeline. "
            "Detailed explanation is temporarily unavailable. "
            "Please refer to the audit trail for complete evidence."
        ),
        evidence_summary={},
        basis_risk_notice=_BASIS_RISK_NOTICE,
        is_synthetic=True,
        method="fallback",
        fallback_used=True,
    )

