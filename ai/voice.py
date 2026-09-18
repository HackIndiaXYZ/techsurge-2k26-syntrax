"""
SYNTRAX AI Layer — Voice Assistance

Generates voice call scripts and orchestrates outbound calls for policyholder acknowledgement.
Advisory and accessibility only. Never authorizes a settlement.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

from .schemas import (
    CallState,
    CallPurpose,
    ExplanationLanguage,
    VoiceCallRequest,
    VoiceCallScript,
    VoiceCallResult,
)

logger = logging.getLogger(__name__)

def _format_inr(paise: int) -> str:
    """Format paise as INR display string for speech."""
    rupees = paise // 100
    return f"{rupees:,} rupees"

def _generate_script(request: VoiceCallRequest) -> VoiceCallScript:
    """Generate a template-based script matching the required language and intent."""
    
    amount_speech = _format_inr(request.settlement_amount_paise)
    
    if request.language == ExplanationLanguage.HI:
        opening_message = (
            f"नमस्ते। यह टेराफ्लक्स (TerraFlux) जलवायु सुरक्षा सहायक है। "
            f"आपके डिजिटल वॉलेट में {amount_speech} का वर्षा सुरक्षा निपटान जमा कर दिया गया है। "
            f"यह निपटान इसलिए शुरू किया गया क्योंकि विश्वसनीय वर्षा मापन {request.consensus_value} मिलीमीटर था, "
            f"जो आपकी {request.threshold_value} मिलीमीटर की सीमा से अधिक है। "
            f"आपके वॉलेट अधिसूचना की अभी तक पुष्टि नहीं हुई है।"
        )
        repeat_message = f"विश्वसनीय वर्षा {request.consensus_value} मिलीमीटर थी। {amount_speech} का भुगतान हो चुका है।"
        acknowledgement_prompt = "निपटान की पुष्टि करने के लिए 1 दबाएं, विवरण फिर से सुनने के लिए 2 दबाएं, या कॉल समाप्त करने के लिए 3 दबाएं।"
        fallback_message = "मुझे समझ नहीं आया। कृपया 1, 2, या 3 दबाएं।"
    
    elif request.language == ExplanationLanguage.TE:
        opening_message = (
            f"నమస్కారం. ఇది టెర్రాఫ్లక్స్ (TerraFlux) వాతావరణ రక్షణ సహాయకం. "
            f"మీ వర్షపాత రక్షణ చెల్లింపు {amount_speech} ఇప్పటికే మీ డిజిటల్ వాలెట్‌లో జమ చేయబడింది. "
            f"విశ్వసనీయ వర్షపాతం {request.consensus_value} మిల్లీమీటర్లుగా నమోదు కావడం వల్ల ఈ చెల్లింపు జరిగింది, "
            f"ఇది మీ {request.threshold_value} మిల్లీమీటర్ల పరిమితిని మించిపోయింది. "
            f"మీ వాలెట్ నోటిఫికేషన్ ఇంకా ధృవీకరించబడలేదు."
        )
        repeat_message = f"వర్షపాతం {request.consensus_value} మిల్లీమీటర్లు. {amount_speech} చెల్లింపు పూర్తయింది."
        acknowledgement_prompt = "చెల్లింపును ధృవీకరించడానికి 1 నొక్కండి, వివరాలను మళ్లీ వినడానికి 2 నొక్కండి, లేదా కాల్ ముగించడానికి 3 నొక్కండి."
        fallback_message = "నాకు అర్థం కాలేదు. దయచేసి 1, 2, లేదా 3 నొక్కండి."
        
    else:  # Default EN
        opening_message = (
            f"Hello. This is the TerraFlux climate protection assistant. "
            f"Your rainfall protection settlement of {amount_speech} has already been credited to your digital wallet. "
            f"The settlement was triggered because the trusted rainfall measurement was {request.consensus_value} millimetres, "
            f"exceeding your {request.threshold_value} millimetre threshold. "
            f"Your wallet notification has not yet been acknowledged."
        )
        repeat_message = (
            f"The trusted rainfall was {request.consensus_value} millimetres. "
            f"{amount_speech} has been credited."
        )
        acknowledgement_prompt = (
            "Press 1 to acknowledge the settlement, press 2 to hear the details again, or press 3 to end the call."
        )
        fallback_message = "I did not understand that. Please press 1, 2, or 3."

    return VoiceCallScript(
        event_id=request.event_id,
        language=request.language,
        purpose=request.purpose,
        opening_message=opening_message,
        repeat_message=repeat_message,
        acknowledgement_prompt=acknowledgement_prompt,
        fallback_message=fallback_message,
        actions={
            "1": "ACKNOWLEDGE",
            "2": "REPEAT",
            "3": "END"
        }
    )


class VoiceProvider(ABC):
    @abstractmethod
    def make_call(self, request: VoiceCallRequest, script: VoiceCallScript) -> VoiceCallResult:
        pass


class MockVoiceProvider(VoiceProvider):
    """Deterministic mock provider for testing and safe local runs."""
    
    def make_call(self, request: VoiceCallRequest, script: VoiceCallScript) -> VoiceCallResult:
        logger.info(f"Mock calling {request.phone_number} with script: {script.opening_message}")
        
        # Simulate an immediate successful connection and acknowledgement 
        # (in a real async system this happens via callbacks/webhooks)
        return VoiceCallResult(
            event_id=request.event_id,
            provider="mock",
            provider_call_id=f"mock_call_{request.event_id}",
            status=CallState.INITIATED,
            language=request.language
        )


class TwilioVoiceProvider(VoiceProvider):
    """Twilio Programmable Voice outbound caller."""
    
    def __init__(self):
        # We load env lazily to not break tests if Twilio is unavailable
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.api_key = os.environ.get("TWILIO_API_KEY")
        self.api_secret = os.environ.get("TWILIO_API_SECRET")
        self.from_number = os.environ.get("TWILIO_FROM_NUMBER")
        self.webhook_base = os.environ.get("TWILIO_WEBHOOK_BASE_URL", "")
        self.enabled = os.environ.get("TWILIO_VOICE_ENABLED", "false").lower() == "true"
        
        # In a real environment, we'd setup the client. 
        # To avoid strictly requiring the library to run tests, we conditionally import.
        self.client = None
        if self.enabled and self.account_sid:
            try:
                from twilio.rest import Client
                if self.api_key and self.api_secret:
                    self.client = Client(self.api_key, self.api_secret, self.account_sid)
                else:
                    auth_token = os.environ.get("TWILIO_AUTH_TOKEN") # Fallback for standard auth
                    self.client = Client(self.account_sid, auth_token)
            except ImportError:
                logger.error("Twilio python library is not installed.")

    def make_call(self, request: VoiceCallRequest, script: VoiceCallScript) -> VoiceCallResult:
        if not self.enabled or not self.client:
            return VoiceCallResult(
                event_id=request.event_id,
                provider="twilio",
                status=CallState.FAILED,
                language=request.language,
                error_code="TWILIO_NOT_CONFIGURED",
                error_message="Twilio voice is disabled or unconfigured."
            )
            
        try:
            # We generate TwiML for the outbound call.
            # In a production setup, Twilio calls a webhook URL to get the TwiML.
            # For this MVP, if a webhook URL is configured we pass it, otherwise we use Twiml directly.
            
            # Map explanation language to Twilio locales
            locale_map = {
                ExplanationLanguage.EN: "en-IN",
                ExplanationLanguage.HI: "hi-IN",
                ExplanationLanguage.TE: "te-IN"
            }
            voice_locale = locale_map.get(request.language, "en-IN")
            
            # Pure TwiML approach (twiml parameter directly on creation)
            twiml = f"""
            <Response>
                <Gather numDigits="1" action="{self.webhook_base}/v1/ai/voice/webhook/gather?event_id={request.event_id}" method="POST">
                    <Say language="{voice_locale}" voice="Polly.Aditi">{script.opening_message}</Say>
                    <Say language="{voice_locale}" voice="Polly.Aditi">{script.acknowledgement_prompt}</Say>
                </Gather>
                <Say language="{voice_locale}" voice="Polly.Aditi">{script.fallback_message}</Say>
            </Response>
            """
            
            call = self.client.calls.create(
                twiml=twiml,
                to=request.phone_number,
                from_=self.from_number,
                status_callback=f"{self.webhook_base}/v1/ai/voice/webhook/status?event_id={request.event_id}",
                status_callback_event=["initiated", "ringing", "answered", "completed"]
            )
            
            return VoiceCallResult(
                event_id=request.event_id,
                provider="twilio",
                provider_call_id=call.sid,
                status=CallState.INITIATED,
                language=request.language
            )
            
        except Exception as e:
            logger.exception("Failed to create Twilio call")
            return VoiceCallResult(
                event_id=request.event_id,
                provider="twilio",
                status=CallState.FAILED,
                language=request.language,
                error_code="TWILIO_CALL_FAILED",
                error_message=str(e)
            )


# In-memory deduplication set for MVP idempotency
# (voice-call:{event_id}:{purpose})
_call_execution_keys = set()

def execute_voice_assistance(request: VoiceCallRequest, force_provider: Optional[VoiceProvider] = None) -> VoiceCallResult:
    """
    Main entrypoint for AI Voice Assistance.
    Evaluates idempotency, generates script, and places outbound call.
    """
    
    # 1. Idempotency Check
    execution_key = f"voice-call:{request.event_id}:{request.purpose}"
    if execution_key in _call_execution_keys:
        return VoiceCallResult(
            event_id=request.event_id,
            provider="system",
            status=CallState.NOT_REQUIRED,
            language=request.language,
            error_code="DUPLICATE_CALL",
            error_message="A call for this event and purpose has already been requested."
        )
        
    _call_execution_keys.add(execution_key)
    
    # 2. Script Generation
    script = _generate_script(request)
    
    # 3. Provider Selection
    if force_provider:
        provider = force_provider
    elif os.environ.get("TWILIO_VOICE_ENABLED", "false").lower() == "true":
        provider = TwilioVoiceProvider()
    else:
        provider = MockVoiceProvider()
        
    # 4. Execute
    return provider.make_call(request, script)


