"""
routers/voice.py — Webhook handlers for Twilio voice calls.
"""
import logging
import os
import uuid
import datetime

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.voice_call import VoiceCallJob, CallLog, VoiceCallStatus
from models.audit import AuditEvent, AuditEventType
from twilio.request_validator import RequestValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/voice/webhook", tags=["Voice Webhooks"])

def _validate_twilio_signature(request: Request, form_data: dict) -> bool:
    """Validates the Twilio webhook signature."""
    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        return False
        
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not auth_token:
        # If no auth token is configured, we can't securely validate.
        # Fail safe: reject.
        return False
        
    validator = RequestValidator(auth_token)
    
    # Twilio needs the exact URL they requested, including query params.
    # We must construct it safely. Often request.url is sufficient, 
    # but behind proxies, it might need tweaking. Using request.url directly for MVP.
    url = str(request.url)
    
    # Twilio webhook uses the form data
    return validator.validate(url, form_data, signature)

# State mapping
TWILIO_TO_INTERNAL_STATUS = {
    "queued": VoiceCallStatus.CALLING.value,
    "initiated": VoiceCallStatus.CALLING.value,
    "ringing": VoiceCallStatus.RINGING.value,
    "in-progress": VoiceCallStatus.ANSWERED.value,
    "completed": VoiceCallStatus.COMPLETED.value,
    "busy": VoiceCallStatus.BUSY.value,
    "no-answer": VoiceCallStatus.NO_ANSWER.value,
    "canceled": VoiceCallStatus.CANCELED.value,
    "failed": VoiceCallStatus.FAILED.value,
}

STATE_RANKS = {
    VoiceCallStatus.PENDING.value: 0,
    VoiceCallStatus.CLAIMED.value: 1,
    VoiceCallStatus.REQUESTED.value: 2,
    VoiceCallStatus.CALLING.value: 3,
    VoiceCallStatus.RINGING.value: 4,
    VoiceCallStatus.ANSWERED.value: 5,
    VoiceCallStatus.COMPLETED.value: 6,
    VoiceCallStatus.BUSY.value: 6,
    VoiceCallStatus.NO_ANSWER.value: 6,
    VoiceCallStatus.CANCELED.value: 6,
    VoiceCallStatus.FAILED.value: 6,
    VoiceCallStatus.FAILED_FINAL.value: 6,
    VoiceCallStatus.RETRY_PENDING.value: 6,
}

@router.post("/status")
async def twilio_status_webhook(
    request: Request,
    event_id: str, # This is the ai_assistance_handoff_id or related notification_id mapped to the job
    db: AsyncSession = Depends(get_db)
):
    """
    Handles Twilio status callbacks.
    """
    # 1. Read form data
    form_data = dict(await request.form())
    
    # 2. Authenticate
    if not _validate_twilio_signature(request, form_data):
        logger.warning(f"Invalid Twilio signature for event_id: {event_id}")
        
        # Log audit event for rejection
        audit = AuditEvent(
            correlation_id=uuid.uuid4(),
            entity_type="voice_webhook",
            event_type=AuditEventType.VOICE_WEBHOOK_REJECTED.value,
            actor="twilio",
            metadata_={"event_id": event_id, "form_data": form_data},
            status="REJECTED",
            message="Invalid webhook signature.",
            occurred_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(audit)
        await db.commit()
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")

    # Audit accepted webhook
    audit_accept = AuditEvent(
        correlation_id=uuid.uuid4(),
        entity_type="voice_webhook",
        event_type=AuditEventType.VOICE_WEBHOOK_ACCEPTED.value,
        actor="twilio",
        metadata_={"event_id": event_id},
        status="ACCEPTED",
        occurred_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(audit_accept)

    # 3. Find the VoiceCallJob (Idempotent correlation)
    call_sid = form_data.get("CallSid")
    twilio_status = form_data.get("CallStatus")
    
    try:
        handoff_uuid = uuid.UUID(event_id)
    except ValueError:
        logger.error(f"Invalid event_id UUID format: {event_id}")
        await db.commit()
        return PlainTextResponse("OK") # Return 200 so Twilio stops retrying invalid data

    stmt = select(VoiceCallJob).where(VoiceCallJob.handoff_id == handoff_uuid)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        logger.warning(f"VoiceCallJob not found for handoff {handoff_uuid}")
        await db.commit()
        return PlainTextResponse("OK")
        
    # Verify SID matches if we already have one
    if job.provider_call_id and job.provider_call_id != call_sid:
        logger.warning(f"Call SID mismatch. Expected {job.provider_call_id}, got {call_sid}")
        await db.commit()
        return PlainTextResponse("OK")

    if not job.provider_call_id:
        # If we didn't save the SID yet (e.g. out of order or race), save it
        job.provider_call_id = call_sid

    # 4. Record Immutable Call Log
    # Ensure idempotency: check if this event already exists with the exact same payload
    log_stmt = select(CallLog).where(
        CallLog.voice_call_job_id == job.id,
        CallLog.provider_call_id == call_sid,
        CallLog.provider_status == twilio_status
    )
    existing_logs = (await db.execute(log_stmt)).scalars().all()
    
    is_duplicate = False
    for el in existing_logs:
        if el.payload_metadata == form_data:
            is_duplicate = True
            break
            
    if not is_duplicate:
        call_log = CallLog(
            voice_call_job_id=job.id,
            provider_call_id=call_sid,
            provider="twilio",
            event_type="TWILIO_WEBHOOK",
            provider_status=twilio_status,
            occurred_at=datetime.datetime.now(datetime.timezone.utc),
            payload_metadata=form_data
        )
        db.add(call_log)
    
    # 5. Determine State Transition
    new_status = TWILIO_TO_INTERNAL_STATUS.get(twilio_status)
    if new_status:
        current_rank = STATE_RANKS.get(job.status, 0)
        new_rank = STATE_RANKS.get(new_status, 0)
        
        # Only progress forward, ignore out of order regressions
        if new_rank > current_rank:
            old_status = job.status
            job.status = new_status
            
            # Update specific timestamps
            now = datetime.datetime.now(datetime.timezone.utc)
            if new_status == VoiceCallStatus.CALLING.value and not job.started_at:
                job.started_at = now
            elif new_status == VoiceCallStatus.ANSWERED.value and not job.answered_at:
                job.answered_at = now
            elif new_status == VoiceCallStatus.COMPLETED.value and not job.completed_at:
                job.completed_at = now
            elif new_status in [VoiceCallStatus.FAILED.value, VoiceCallStatus.BUSY.value, VoiceCallStatus.NO_ANSWER.value, VoiceCallStatus.CANCELED.value] and not job.failed_at:
                job.failed_at = now
                
            # Audit State Transition
            audit_transition = AuditEvent(
                correlation_id=uuid.uuid4(),
                entity_type="voice_call_job",
                entity_id=job.id,
                event_type=AuditEventType.VOICE_CALL_STATE_TRANSITION.value,
                actor="twilio",
                metadata_={
                    "old_status": old_status,
                    "new_status": new_status,
                    "provider_call_id": call_sid,
                    "provider_status": twilio_status
                },
                status="SUCCESS",
                message=f"Transitioned from {old_status} to {new_status}",
                occurred_at=datetime.datetime.now(datetime.timezone.utc)
            )
            db.add(audit_transition)

            # Map the exact audit event type based on new_status
            event_type_mapping = {
                VoiceCallStatus.RINGING.value: AuditEventType.VOICE_CALL_RINGING.value,
                VoiceCallStatus.ANSWERED.value: AuditEventType.VOICE_CALL_ANSWERED.value,
                VoiceCallStatus.COMPLETED.value: AuditEventType.VOICE_CALL_COMPLETED.value,
                VoiceCallStatus.FAILED.value: AuditEventType.VOICE_CALL_FAILED.value,
                VoiceCallStatus.BUSY.value: AuditEventType.VOICE_CALL_BUSY.value,
                VoiceCallStatus.NO_ANSWER.value: AuditEventType.VOICE_CALL_NO_ANSWER.value
            }
            if new_status in event_type_mapping:
                audit_status = AuditEvent(
                    correlation_id=uuid.uuid4(),
                    entity_type="voice_call_job",
                    entity_id=job.id,
                    event_type=event_type_mapping[new_status],
                    actor="twilio",
                    status="SUCCESS",
                    metadata_={"call_sid": call_sid, "handoff_id": str(job.handoff_id)},
                    occurred_at=datetime.datetime.now(datetime.timezone.utc)
                )
                db.add(audit_status)

    await db.commit()
    return PlainTextResponse("OK")


@router.post("/gather")
async def twilio_gather_webhook(
    request: Request,
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Handles user input from Twilio <Gather>.
    """
    form_data = dict(await request.form())
    
    if not _validate_twilio_signature(request, form_data):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")

    digits = form_data.get("Digits", "")
    
    # Basic logic: 1 to acknowledge, 2 to repeat, 3 to end
    # For now, we just return empty TwiML, allowing it to complete, 
    # or handle the logic. 
    # Real logic would verify the job, update Notification state, etc.
    # MVP: We just accept the webhook safely.
    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
    return HTMLResponse(content=twiml, media_type="text/xml")
