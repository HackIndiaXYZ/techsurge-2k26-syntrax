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
    BackendEventContract,
    FrontendAIResponse,
    VoiceCallRequest,
    VoiceCallResult
)
from .anomaly import score_telemetry_anomaly
from .explainer import explain_event
from .localizer import generate_settlement_message
from .voice import execute_voice_assistance

router = APIRouter(prefix="/v1/ai", tags=["AI Advisory"])


@router.post("/anomaly", response_model=AnomalyOutput)
def analyze_anomaly(payload: AnomalyInput) -> AnomalyOutput:
    """Analyze a consensus window for statistical anomalies."""
    try:
        return score_telemetry_anomaly(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=ExplanationOutput)
def generate_explanation(
    payload: ExplanationInput, 
    language: ExplanationLanguage = ExplanationLanguage.EN
) -> ExplanationOutput:
    """Generate a human-readable explanation of a pipeline event."""
    try:
        return explain_event(payload, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notify", response_model=SettlementNotificationOutput)
def create_settlement_notification(payload: SettlementNotificationInput) -> SettlementNotificationOutput:
    """Generate a local-language notification for a completed settlement."""
    try:
        return generate_settlement_message(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/event", response_model=FrontendAIResponse)
def process_backend_event(event: BackendEventContract) -> FrontendAIResponse:
    """Process a canonical backend event into a unified frontend AI response.
    
    This is the primary integration point for the frontend to get all AI features
    (anomaly detection, explanation, and notification) in a single call based
    on the backend's deterministic event state.
    """
    from .adapter import (
        map_event_to_anomaly_input, 
        map_event_to_explanation_input, 
        map_event_to_notification_input,
        map_event_to_voice_request
    )
    
    response = FrontendAIResponse(event_id=event.event_id)
    
    try:
        # 1. Anomaly
        anom_input = map_event_to_anomaly_input(event)
        if anom_input:
            response.anomaly = score_telemetry_anomaly(anom_input)
            
        # 2. Explanation (English, Hindi, Telugu)
        exp_input = map_event_to_explanation_input(event)
        response.explanation_en = explain_event(exp_input, ExplanationLanguage.EN)
        response.explanation_hi = explain_event(exp_input, ExplanationLanguage.HI)
        response.explanation_te = explain_event(exp_input, ExplanationLanguage.TE)
        
        # 3. Notification (If settled)
        notif_input = map_event_to_notification_input(event)
        if notif_input:
            # Generate English
            response.notification_en = generate_settlement_message(notif_input)
            
            # Generate Hindi
            notif_input.language = ExplanationLanguage.HI
            response.notification_hi = generate_settlement_message(notif_input)
            
            # Generate Telugu
            notif_input.language = ExplanationLanguage.TE
            response.notification_te = generate_settlement_message(notif_input)
            
        # 4. Voice Assistance Status
        voice_req = map_event_to_voice_request(event, phone_number="NOT_PROVIDED")
        if voice_req:
            response.voice_assistance = {
                "enabled": True,
                "status": "PENDING_PHONE_NUMBER", # Frontend needs to provide it for actual call
                "language": "en-IN"
            }
        else:
            response.voice_assistance = {
                "enabled": False,
                "status": "NOT_REQUIRED"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return response

@router.post("/voice/call", response_model=VoiceCallResult)
def initiate_voice_call(request: VoiceCallRequest) -> VoiceCallResult:
    """Initiate an outbound voice assistance call."""
    try:
        return execute_voice_assistance(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

