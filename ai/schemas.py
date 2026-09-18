"""
SYNTRAX AI Layer — Shared Pydantic Schemas

These schemas define the exact data contracts between the AI advisory layer
and the backend deterministic core. All schemas are structured for:
  1. Clear input/output boundaries
  2. Deterministic fallback values
  3. Explicit confidence scores and limitation disclosures

CRITICAL: These schemas are for ADVISORY outputs only. They must never
carry authority to approve, reject, or modify financial decisions.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================

class AnomalyLevel(str, Enum):
    """Advisory anomaly classification. Not authoritative."""
    NORMAL = "NORMAL"
    SUSPICIOUS = "SUSPICIOUS"
    ANOMALOUS = "ANOMALOUS"


class ExplanationLanguage(str, Enum):
    """Supported languages for human-readable output."""
    EN = "en"
    HI = "hi"
    TE = "te"


# ============================================================
# Telemetry Anomaly Detection — Input/Output
# ============================================================

class TelemetryReading(BaseModel):
    """A single source reading for anomaly analysis."""
    source_id: str = Field(..., description="UUID of the weather source")
    source_code: str = Field(..., description="Human-readable source code, e.g. SYN-SRC-A")
    value: float = Field(..., description="Measurement value (e.g. rainfall in mm)")
    unit: str = Field(default="mm", description="Measurement unit")
    observed_at: datetime = Field(..., description="When the observation was recorded")
    validation_state: str = Field(
        default="ACCEPTED",
        description="Backend validation state: ACCEPTED, REJECTED, DUPLICATE"
    )


class AnomalyInput(BaseModel):
    """Input for anomaly detection: all readings for a single consensus window."""
    region_id: str = Field(..., description="UUID of the micro-region")
    metric: str = Field(default="RAINFALL_MM", description="Metric being measured")
    window_start: datetime = Field(..., description="Measurement window start")
    window_end: datetime = Field(..., description="Measurement window end")
    readings: list[TelemetryReading] = Field(
        ..., min_length=1, max_length=10,
        description="All source readings for this window"
    )


class AnomalyScore(BaseModel):
    """Advisory anomaly assessment for a single source reading.

    This score is NEVER used to accept or reject telemetry.
    The deterministic validation pipeline is authoritative.
    """
    source_code: str
    value: float
    anomaly_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="0.0 = normal, 1.0 = highly anomalous. Advisory only."
    )
    anomaly_level: AnomalyLevel
    deviation_from_median: float = Field(
        ..., description="Absolute deviation from peer median in measurement units"
    )
    z_score: Optional[float] = Field(
        None, description="Standard score if enough data points (>=3)"
    )
    explanation: str = Field(
        ..., description="Human-readable reason for the score"
    )


class AnomalyOutput(BaseModel):
    """Complete anomaly analysis result for a consensus window."""
    region_id: str
    metric: str
    window_start: datetime
    window_end: datetime
    source_scores: list[AnomalyScore]
    peer_median: float = Field(..., description="Median of all valid readings")
    peer_spread: float = Field(..., description="Max - min of valid readings")
    reading_count: int
    is_advisory: bool = Field(
        default=True,
        description="Always True. This output is advisory, never authoritative."
    )
    method: str = Field(
        default="statistical_zscore",
        description="Algorithm used. No LLM involved."
    )
    fallback_used: bool = Field(
        default=False,
        description="True if the primary method failed and a fallback was used"
    )


# ============================================================
# Event Explanation — Input/Output
# ============================================================

class ConsensusInfo(BaseModel):
    """Consensus result data for explanation generation."""
    state: str = Field(..., description="ACHIEVED, NO_CONSENSUS, PENDING, EXPIRED")
    value: Optional[float] = Field(None, description="Consensus value if achieved")
    unit: str = Field(default="mm")
    member_count: int = Field(default=0)
    members: list[dict] = Field(
        default_factory=list,
        description="List of {source_code, value, role} dicts"
    )


class TriggerInfo(BaseModel):
    """Trigger evaluation data for explanation generation."""
    outcome: str = Field(
        ..., description="TRIGGERED, NOT_MET, NOT_ELIGIBLE, NO_CONSENSUS, ALREADY_TRIGGERED, EXPIRED"
    )
    reason_code: str
    threshold_value: float
    threshold_operator: str = Field(default="GTE")
    threshold_unit: str = Field(default="mm")
    window_minutes: int = Field(default=60)


class PayoutInfo(BaseModel):
    """Payout data for explanation generation."""
    state: str = Field(..., description="PENDING, PROCESSING, COMPLETED, FAILED")
    amount_paise: int
    currency: str = Field(default="INR")
    idempotency_key: Optional[str] = None
    is_retry: bool = Field(default=False)


class WalletInfo(BaseModel):
    """Wallet data for explanation generation."""
    balance_before_paise: int
    balance_after_paise: int
    currency: str = Field(default="INR")


class ExplanationInput(BaseModel):
    """Structured evidence for generating a human-readable explanation.

    CRITICAL: The AI reads this evidence. It does NOT produce it.
    All data comes from the deterministic pipeline's persisted records.
    The AI must not invent, modify, or reinterpret evidence.
    """
    correlation_id: str = Field(..., description="Links all events in the causal chain")
    policy_id: str
    policyholder_name: str = Field(default="SYN-HOLDER-001")
    region_name: str = Field(default="Kurnool Synthetic Micro-Region")
    metric: str = Field(default="RAINFALL_MM")
    readings: list[TelemetryReading] = Field(default_factory=list)
    consensus: Optional[ConsensusInfo] = None
    trigger: Optional[TriggerInfo] = None
    payout: Optional[PayoutInfo] = None
    wallet: Optional[WalletInfo] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExplanationOutput(BaseModel):
    """Human-readable explanation of a deterministic pipeline event.

    Generated from structured evidence only. No invented facts.
    """
    correlation_id: str
    language: ExplanationLanguage = Field(default=ExplanationLanguage.EN)
    title: str = Field(..., description="Short summary headline")
    body: str = Field(..., description="Full explanation paragraph(s)")
    evidence_summary: dict = Field(
        default_factory=dict,
        description="Key facts extracted from input (not invented)"
    )
    basis_risk_notice: str = Field(
        default="This parametric payout is based on the predefined weather index "
                "and does not individually assess actual loss.",
        description="Mandatory basis risk disclosure"
    )
    is_synthetic: bool = Field(
        default=True,
        description="Always True. All data and payouts are synthetic."
    )
    method: str = Field(
        default="template",
        description="Explanation generation method. 'template' = deterministic, 'llm' = AI-generated."
    )
    fallback_used: bool = Field(default=False)


# ============================================================
# Local-Language Settlement Notification — Input/Output
# ============================================================

class SettlementNotificationInput(BaseModel):
    """Input for generating a post-settlement notification message.

    This is called AFTER settlement is completed. The AI only
    communicates the already-established result.
    """
    policyholder_name: str
    region_name: str
    payout_amount_paise: int
    currency: str = Field(default="INR")
    payout_state: str = Field(..., description="Must be COMPLETED")
    consensus_value: float
    consensus_unit: str = Field(default="mm")
    threshold_value: float
    language: ExplanationLanguage = Field(default=ExplanationLanguage.EN)


class SettlementNotificationOutput(BaseModel):
    """Structured settlement notification suitable for voice TTS or display.

    The message communicates an already-completed payout. It does NOT
    authorize or modify the payout in any way.
    """
    message: str = Field(..., description="Human-readable notification text")
    language: ExplanationLanguage
    amount_display: str = Field(..., description="Formatted amount, e.g. '₹10,000'")
    is_synthetic: bool = Field(
        default=True,
        description="Always True. Must be stated in any voice output."
    )
    basis_risk_notice: str = Field(
        default="This parametric payout is based on the predefined weather index "
                "and does not individually assess actual loss."
    )
    fallback_used: bool = Field(default=False)
    method: str = Field(default="template")



# ============================================================
# Canonical Unified Event Contract
# ============================================================

class BackendEventContract(BaseModel):
    """The canonical event contract accepted from the authoritative backend."""
    event_id: str
    policy_id: str
    timestamp: str | datetime
    
    # Telemetry
    source_observations: list[dict] = Field(default_factory=list)
    validated_observations: list[dict] = Field(default_factory=list)
    
    # Consensus
    consensus_value: Optional[float] = None
    consensus_status: str = "PENDING"
    outlier_sources: list[str] = Field(default_factory=list)
    
    # Trigger
    trigger_status: str = "PENDING"
    trigger_reason: Optional[str] = None
    
    # Settlement
    payout_amount_paise: Optional[int] = None
    settlement_status: str = "PENDING"
    idempotency_status: Optional[str] = None
    wallet_acknowledgement_status: str = "PENDING"


class FrontendAIResponse(BaseModel):
    """The unified AI response consumable by the frontend."""
    event_id: str
    
    # Metadata boundaries
    is_advisory: bool = True
    is_synthetic: bool = True
    fallback_used: bool = False
    basis_risk_notice: str = (
        "The prototype settles against a predefined weather index; the index does not "
        "guarantee that the payout equals the policyholder's actual loss."
    )
    
    # Analysis blocks
    anomaly: Optional[AnomalyOutput] = None
    explanation_en: Optional[ExplanationOutput] = None
    explanation_hi: Optional[ExplanationOutput] = None
    explanation_te: Optional[ExplanationOutput] = None
    notification_en: Optional[SettlementNotificationOutput] = None
    notification_hi: Optional[SettlementNotificationOutput] = None
    notification_te: Optional[SettlementNotificationOutput] = None
    voice_assistance: Optional[dict] = None

# ============================================================
# Voice Assistance - Input/Output
# ============================================================

class CallState(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    INITIATED = "INITIATED"
    RINGING = "RINGING"
    CONNECTED = "CONNECTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REPEATED = "REPEATED"
    ENDED = "ENDED"
    FAILED = "FAILED"

class CallPurpose(str, Enum):
    SETTLEMENT_ACKNOWLEDGEMENT = "SETTLEMENT_ACKNOWLEDGEMENT"

class VoiceCallRequest(BaseModel):
    event_id: str
    settlement_id: Optional[str] = None
    language: ExplanationLanguage = ExplanationLanguage.EN
    phone_number: str
    purpose: CallPurpose = CallPurpose.SETTLEMENT_ACKNOWLEDGEMENT
    settlement_amount_paise: int
    consensus_value: float
    threshold_value: float
    acknowledgement_status: str = "NOT_ACKNOWLEDGED"

class VoiceCallScript(BaseModel):
    event_id: str
    language: ExplanationLanguage
    purpose: CallPurpose
    opening_message: str
    repeat_message: str
    acknowledgement_prompt: str
    fallback_message: str
    actions: dict = Field(default_factory=dict)

class VoiceCallResult(BaseModel):
    event_id: str
    provider: str
    provider_call_id: Optional[str] = None
    status: CallState
    language: ExplanationLanguage
    acknowledgement_result: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
