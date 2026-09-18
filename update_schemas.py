import re

with open('ai/schemas.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add wallet_acknowledgement_status to BackendEventContract
replacement1 = """    idempotency_status: Optional[str] = None
    wallet_acknowledgement_status: str = "PENDING"
"""
content = content.replace('    idempotency_status: Optional[str] = None\n', replacement1)

# Add voice_assistance to FrontendAIResponse
replacement2 = """    notification_te: Optional[SettlementNotificationOutput] = None
    voice_assistance: Optional[dict] = None
"""
content = content.replace('    notification_te: Optional[SettlementNotificationOutput] = None\n', replacement2)

# Add new Schemas at the end
new_schemas = """
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
"""

content += new_schemas

with open('ai/schemas.py', 'w', encoding='utf-8') as f:
    f.write(content)
