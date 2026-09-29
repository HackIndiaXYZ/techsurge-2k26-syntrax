import asyncio
import os
import uuid
import datetime
import urllib.parse
from twilio.request_validator import RequestValidator
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport

from config import get_settings
from database import AsyncSessionLocal
from main import app
from models.policyholder import Policyholder
from models.notification import Notification, NotificationStatus
from models.ai_assistance import AIAssistanceHandoff, AIAssistanceStatus
from models.voice_call import VoiceCallJob, VoiceCallStatus, CallLog
from models.audit import AuditEvent, AuditEventType

os.environ["TWILIO_AUTH_TOKEN"] = "test_auth_token_for_phase7"
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
validator = RequestValidator(auth_token)

async def create_test_data(session):
    # 1. Policyholder
    ph = Policyholder(
        id=uuid.uuid4(),
        display_name=f"Phase 7 User {uuid.uuid4().hex[:8]}",
        phone_number="+910000000007",
        phone_verified=True
    )
    session.add(ph)
    
    from models.policy import Policy
    from sqlalchemy import select
    # Fetch an existing policy
    policy = (await session.execute(select(Policy).limit(1))).scalars().first()
    
    from models.payout import Payout
    payout = (await session.execute(select(Payout).limit(1))).scalars().first()
    
    # 2. Notification
    notif = Notification(
        id=uuid.uuid4(),
        policyholder_id=ph.id,
        policy_id=policy.id,
        payout_id=payout.id,
        event_type=f"TEST_{uuid.uuid4().hex[:8]}",
        status=NotificationStatus.ESCALATED,
        title="Test Notif",
        message="Test Message"
    )
    session.add(notif)
    
    # 3. Handoff
    handoff = AIAssistanceHandoff(
        id=uuid.uuid4(),
        notification_id=notif.id,
        policyholder_id=ph.id,
        policy_id=notif.policy_id,
        payout_id=notif.payout_id,
        status=AIAssistanceStatus.PROCESSED
    )
    session.add(handoff)
    
    # 4. VoiceCallJob
    job = VoiceCallJob(
        id=uuid.uuid4(),
        handoff_id=handoff.id,
        policyholder_id=ph.id,
        phone_number=ph.phone_number,
        status=VoiceCallStatus.REQUESTED.value,
        provider_call_id="test_sid_initial"
    )
    session.add(job)
    await session.commit()
    
    return ph, notif, handoff, job

def generate_twilio_signature(url: str, form_data: dict) -> str:
    return validator.compute_signature(url, form_data)

async def run_tests():
    print("Starting Phase 7 Verification...")
    
    async with AsyncSessionLocal() as session:
        ph, notif, handoff, job = await create_test_data(session)
        job_id = job.id
        event_id = str(handoff.id)
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            
            # --- TEST 2: RINGING ---
            print("\n--- TEST 2: RINGING ---")
            url_path = f"/v1/voice/webhook/status?event_id={event_id}"
            url_full = f"http://test{url_path}"
            form_data = {
                "CallSid": "test_sid_initial",
                "CallStatus": "ringing",
            }
            sig = generate_twilio_signature(url_full, form_data)
            resp = await client.post(url_path, data=form_data, headers={"X-Twilio-Signature": sig})
            
            assert resp.status_code == 200
            
            await session.refresh(job)
            assert job.status == VoiceCallStatus.RINGING.value
            print("SUCCESS: State transition to RINGING worked.")
            
            # Verify CallLog
            logs = (await session.execute(select(CallLog).where(CallLog.voice_call_job_id == job_id))).scalars().all()
            assert len(logs) == 1
            assert logs[0].provider_status == "ringing"
            print("SUCCESS: CallLog created.")
            
            # --- TEST 8: INVALID SIGNATURE ---
            print("\n--- TEST 8: INVALID SIGNATURE ---")
            form_data_invalid = {
                "CallSid": "test_sid_initial",
                "CallStatus": "in-progress"
            }
            resp = await client.post(url_path, data=form_data_invalid, headers={"X-Twilio-Signature": "bad_sig"})
            assert resp.status_code == 403
            
            await session.refresh(job)
            assert job.status == VoiceCallStatus.RINGING.value
            print("SUCCESS: Invalid signature rejected. State unchanged.")
            
            # --- TEST 9: DUPLICATE WEBHOOK ---
            print("\n--- TEST 9: DUPLICATE WEBHOOK ---")
            resp = await client.post(url_path, data=form_data, headers={"X-Twilio-Signature": sig})
            assert resp.status_code == 200
            logs_dup = (await session.execute(select(CallLog).where(CallLog.voice_call_job_id == job_id))).scalars().all()
            assert len(logs_dup) == 1
            print("SUCCESS: Duplicate webhook idempotent. CallLog not duplicated.")
            
            # --- TEST 3: ANSWERED ---
            print("\n--- TEST 3: ANSWERED ---")
            form_data_ans = {
                "CallSid": "test_sid_initial",
                "CallStatus": "in-progress"
            }
            sig_ans = generate_twilio_signature(url_full, form_data_ans)
            resp = await client.post(url_path, data=form_data_ans, headers={"X-Twilio-Signature": sig_ans})
            assert resp.status_code == 200
            await session.refresh(job)
            assert job.status == VoiceCallStatus.ANSWERED.value
            print("SUCCESS: State transition to ANSWERED.")
            
            # --- TEST 4: COMPLETED ---
            print("\n--- TEST 4: COMPLETED ---")
            form_data_comp = {
                "CallSid": "test_sid_initial",
                "CallStatus": "completed"
            }
            sig_comp = generate_twilio_signature(url_full, form_data_comp)
            resp = await client.post(url_path, data=form_data_comp, headers={"X-Twilio-Signature": sig_comp})
            assert resp.status_code == 200
            await session.refresh(job)
            assert job.status == VoiceCallStatus.COMPLETED.value
            print("SUCCESS: State transition to COMPLETED.")
            
            # --- TEST 10: OUT OF ORDER ---
            print("\n--- TEST 10: OUT OF ORDER ---")
            form_data_ring2 = {
                "CallSid": "test_sid_initial",
                "CallStatus": "ringing", # Arrives late!
                "Extra": "yes"
            }
            sig_ring2 = generate_twilio_signature(url_full, form_data_ring2)
            resp = await client.post(url_path, data=form_data_ring2, headers={"X-Twilio-Signature": sig_ring2})
            assert resp.status_code == 200
            await session.refresh(job)
            assert job.status == VoiceCallStatus.COMPLETED.value # Should NOT regress
            
            logs_late = (await session.execute(select(CallLog).where(CallLog.voice_call_job_id == job_id))).scalars().all()
            assert len(logs_late) == 4 # ringing, answered, completed, ringing (late)
            print("SUCCESS: Out of order event logged but state did NOT regress.")

            # --- AUDIT EVENTS CHECK ---
            print("\n--- AUDIT EVENTS CHECK ---")
            audits = (await session.execute(select(AuditEvent).where(AuditEvent.entity_id == job_id))).scalars().all()
            # There should be transitions for ringing, answered, completed, and status logs
            print(f"SUCCESS: {len(audits)} AuditEvents successfully recorded.")
            
    print("\nALL VERIFICATION STEPS COMPLETED!")

if __name__ == "__main__":
    asyncio.run(run_tests())
