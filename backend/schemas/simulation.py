"""
schemas/simulation.py — Simulation request/response schemas.

POST /simulations is the primary demo endpoint.
The response exposes the complete pipeline result for the frontend.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ── Request ──────────────────────────────────────────────────────────────────

class ObservationInput(BaseModel):
    """One weather source's rainfall reading for a simulation."""
    source_id: str = Field(..., min_length=1, max_length=64)
    value: float = Field(..., ge=0.0, description="Rainfall in mm")


class SimulationRequest(BaseModel):
    """
    Request body for POST /simulations.
    scenario is informational — the actual pipeline logic runs regardless.
    """
    scenario: str = Field(
        ...,
        description="NORMAL | CORRUPTED_SOURCE | NO_CONSENSUS | DUPLICATE_REPLAY"
    )
    policy_id: str = Field(..., min_length=1, max_length=64)
    region_id: str = Field(..., min_length=1, max_length=64)
    observations: list[ObservationInput] = Field(
        ..., min_length=1, description="One entry per weather source"
    )
    observed_at: datetime = Field(..., description="Observation window anchor (UTC)")

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, v: str) -> str:
        valid = {
            "NORMAL",
            "CORRUPTED_SOURCE",
            "NO_CONSENSUS",
            "DUPLICATE_REPLAY",
            "BELOW_THRESHOLD",    # consensus reached but rainfall < 100mm → NOT_TRIGGERED
        }
        if v.upper() not in valid:
            raise ValueError(f"Invalid scenario '{v}'. Must be one of {valid}.")
        return v.upper()


# ── Response sub-schemas ──────────────────────────────────────────────────────

class ObservationResult(BaseModel):
    source_id: str
    value: float
    status: str           # "ACCEPTED" | "REJECTED" | "DUPLICATE"
    rejection_reason: str | None = None


class TelemetryResult(BaseModel):
    submitted: int
    accepted: int
    rejected: int
    duplicates: int
    observations: list[ObservationResult]


class ConsensusResult(BaseModel):
    status: str                                # "REACHED" | "NO_CONSENSUS"
    median_all_sources: float | None = None
    consensus_value_mm: float | None = None
    accepted_sources: list[str] = []
    outlier_sources: list[str] = []
    reason: str | None = None


class TriggerResult(BaseModel):
    status: str                                # "TRIGGERED" | "NOT_TRIGGERED" | "TRIGGER_BLOCKED_NO_CONSENSUS"
    threshold_mm: float
    consensus_value_mm: float | None = None
    reason: str


class SettlementResult(BaseModel):
    status: str                                # "SUCCESS" | "DUPLICATE" | "SKIPPED" | "FAILED"
    payout_id: str | None = None
    idempotency_status: str | None = None      # "NEW" | "ALREADY_SETTLED"
    payout_amount_paise: int | None = None
    payout_amount_inr_display: str | None = None
    reason: str | None = None


class WalletResult(BaseModel):
    wallet_id: str | None = None
    balance_before_paise: int | None = None
    balance_after_paise: int | None = None
    credited: bool


class LatencyResult(BaseModel):
    observed_at: datetime
    received_at: datetime
    trigger_evaluated_at: datetime | None = None
    payout_completed_at: datetime | None = None
    detection_latency_ms: int | None = None
    settlement_latency_ms: int | None = None
    end_to_end_latency_ms: int | None = None


# ── Full response ─────────────────────────────────────────────────────────────

class SimulationResponse(BaseModel):
    """
    Complete pipeline result returned by POST /simulations.
    The frontend uses this to display every step of the demo.
    AI module can use this event schema for explanation (post-settlement, read-only).
    """
    correlation_id: str
    scenario: str
    policy_id: str

    telemetry: TelemetryResult
    consensus: ConsensusResult
    trigger: TriggerResult
    settlement: SettlementResult
    wallet: WalletResult

    audit_id: str | None = None
    latency: LatencyResult | None = None

    # AI event schema — available for Sanju's module (TBD: delivery mechanism)
    # Contains all structured information needed for AI explanation.
    ai_event: dict[str, Any] | None = Field(
        default=None,
        description="Structured event payload for AI module (delivery mechanism TBD)"
    )

