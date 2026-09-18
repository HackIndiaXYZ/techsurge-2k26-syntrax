"""
SYNTRAX AI Layer — FastAPI Router

Provides the HTTP API interface for the AI advisory layer.
These endpoints are called by the backend deterministic core.
"""

from fastapi import APIRouter, HTTPException

from .schemas import (
    AnomalyInput,
    AnomalyOutput,
    ExplanationInput,
    ExplanationOutput,
    ExplanationLanguage,
    SettlementNotificationInput,
    SettlementNotificationOutput,
)
from .anomaly import score_telemetry_anomaly
from .explainer import explain_event
from .localizer import generate_settlement_message

router = APIRouter(prefix="/v1/ai", tags=["AI Advisory"])


@router.post("/anomaly", response_model=AnomalyOutput)
def analyze_anomaly(payload: AnomalyInput) -> AnomalyOutput:
    """Analyze a consensus window for statistical anomalies.
    
    Advisory only. Does not reject or accept telemetry.
    """
    try:
        return score_telemetry_anomaly(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=ExplanationOutput)
def generate_explanation(
    payload: ExplanationInput, 
    language: ExplanationLanguage = ExplanationLanguage.EN
) -> ExplanationOutput:
    """Generate a human-readable explanation of a pipeline event.
    
    Reads structured evidence. Does not invent facts.
    """
    try:
        return explain_event(payload, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notify", response_model=SettlementNotificationOutput)
def create_settlement_notification(payload: SettlementNotificationInput) -> SettlementNotificationOutput:
    """Generate a local-language notification for a completed settlement.
    
    Post-settlement communication only.
    """
    try:
        return generate_settlement_message(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
