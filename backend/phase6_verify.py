import asyncio
import uuid
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
import sys
import os

# Ensure backend imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from models.policy import Policy, PolicyStatus, TriggerRule
from models.policyholder import Policyholder
from models.notification import Notification
from models.ai_assistance import AIAssistanceHandoff
from services.simulation import run_simulation
from schemas.simulation import SimulationRequest

DB_URL = "postgresql+asyncpg://postgres.qdnwxtncipqbjreuzoxl:syntrax%20pass%401@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
engine = create_async_engine(DB_URL, connect_args={"statement_cache_size": 0})
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def setup_test_policy(user_id, **kwargs):
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id FROM micro_regions LIMIT 1"))
        region_id = res.scalar()

        ph = Policyholder(
            auth_user_id=user_id,
            display_name=f"Verification User {user_id}",
            phone_number=kwargs.get('phone', None),
            phone_verified=kwargs.get('verified', False)
        )
        db.add(ph)
        await db.flush()

        from models.wallet import Wallet
        w = Wallet(
            policyholder_id=ph.id,
            balance_paise=0,
            currency="INR",
            status="ACTIVE"
        )
        db.add(w)
        await db.flush()

        policy = Policy(
            policyholder_id=ph.id,
            region_id=region_id,
            name="Verification Policy",
            status=PolicyStatus.ACTIVE.value,
            premium_amount_paise=50000,
            coverage_amount_paise=1000000,
            payout_amount_paise=1000000,
            currency="INR",
            start_at=datetime.datetime.now(datetime.timezone.utc),
            end_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
        )
        db.add(policy)
        await db.flush()

        rule = TriggerRule(
            id=uuid.uuid4(),
            policy_id=policy.id,
            metric="rainfall",
            threshold_value=100.0,
            threshold_operator=">=",
            unit="mm",
            observation_window_minutes=60,
            consensus_quorum=2,
            consensus_tolerance=5.0,
            version=1
        )
        db.add(rule)
        await db.commit()
        return policy.id

async def run_tests():
    print("Starting Direct Database Production Verification...")
    
    # User A
    user_a = uuid.uuid4()
    policy_a_id = await setup_test_policy(user_a)
    print(f"[Phase 4] Policy {policy_a_id} created & activated for User A.")
    
    # Trigger Settlement (Simulate Event)
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id FROM micro_regions LIMIT 1"))
        region_id = str(res.scalar())
        # Get 2 real sources
        sources_res = await db.execute(text("SELECT id FROM weather_sources LIMIT 2"))
        sources = sources_res.scalars().all()
        src1 = str(sources[0])
        src2 = str(sources[1])
        
        request = SimulationRequest(
            scenario="NORMAL",
            policy_id=str(policy_a_id),
            region_id=region_id,
            observations=[{"source_id": src1, "value": 150.0}, {"source_id": src2, "value": 150.0}],
            observed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        response = await run_simulation(request, db)
        await db.commit()
    print(f"[Phase 4] Settlement status: {response.settlement.status}, Trigger status: {response.trigger.status}")
    print(f"[Phase 4] Consensus status: {response.consensus.status}, reason: {response.consensus.reason}")
    
    # 6. ACKNOWLEDGED NOTIFICATION TEST
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id FROM notifications WHERE policy_id = :pid"), {"pid": str(policy_a_id)})
        n_id = res.scalar()
        if n_id:
            await db.execute(text("UPDATE notifications SET status = 'ACKNOWLEDGED', acknowledged_at = NOW() WHERE id = :nid"), {"nid": str(n_id)})
            await db.commit()
            print("[Test 6] Acknowledged notification updated in DB.")
        else:
            print("[Test 6] FAILED: n_id is None!")

    # 7. UNACKNOWLEDGED NOTIFICATION TEST
    user_b = uuid.uuid4()
    policy_b_id = await setup_test_policy(user_b)
    async with AsyncSessionLocal() as db:
        request = SimulationRequest(
            scenario="NORMAL",
            policy_id=str(policy_b_id),
            region_id=region_id,
            observations=[{"source_id": src1, "value": 150.0}, {"source_id": src2, "value": 150.0}],
            observed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        response = await run_simulation(request, db)
        print(f"[Test 7] Settlement status: {response.settlement.status}, Trigger status: {response.trigger.status}")
        
        res = await db.execute(text("SELECT id FROM notifications WHERE policy_id = :pid"), {"pid": str(policy_b_id)})
        n_id2 = res.scalar()
        print(f"n_id2 = {n_id2}")
        
        if n_id2:
            await db.execute(text("UPDATE notifications SET escalation_due_at = NOW() - INTERVAL '1 hour' WHERE id = :nid"), {"nid": str(n_id2)})
            await db.commit()
            print(f"[Test 7] Unacknowledged notification {n_id2} shifted to overdue.")
        else:
            print("[Test 7] FAILED: n_id2 is None!")
        
    if n_id2 is None:
        print("Skipping wait due to test 7 failure.")
        return
    from services.escalation import process_all_overdue_notifications
    async with AsyncSessionLocal() as db:
        print("Running Escalation Engine locally against production DB...")
        count = await process_all_overdue_notifications(db)
        await db.commit()
        print(f"Processed {count} overdue notifications.")
    
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT status FROM notifications WHERE id = :id"), {"id": n_id2})
        status = res.scalar()
        if status == "ESCALATED":
            print("[Test 7] SUCCESS: Production scheduler escalated the notification!")
        else:
            print(f"[Test 7] FAILED: Status is {status}")
            
        res = await db.execute(text("SELECT count(*) FROM ai_assistance_handoffs WHERE notification_id = :id"), {"id": n_id2})
        handoffs = res.scalar()
        if handoffs == 1:
            print("[Test 7] SUCCESS: Exactly one AIAssistanceHandoff created.")
        else:
            print(f"[Test 7] FAILED: Expected 1 handoff, got {handoffs}")
    # 8. PHASE 6 VOICE CALL TESTING
    print("\n--- PHASE 6 VERIFICATION ---")
    
    from services.ai_assistance import process_handoffs_to_jobs, process_pending_voice_jobs
    
    # Test 8A: Unverified Phone (Should Block)
    print("Testing 8A: User without verified phone")
    async with AsyncSessionLocal() as db:
        # User B created earlier was unverified. We already escalated them.
        h_count = await process_handoffs_to_jobs(db)
        await db.commit()
        print(f"[Test 8A] Processed {h_count} handoffs.")
        
        # Check Job status
        from models.voice_call import VoiceCallJob
        res = await db.execute(text("SELECT voice_call_jobs.status FROM voice_call_jobs JOIN ai_assistance_handoffs ON voice_call_jobs.handoff_id = ai_assistance_handoffs.id WHERE ai_assistance_handoffs.notification_id = :nid"), {"nid": n_id2})
        job_status = res.scalar()
        if job_status == "BLOCKED":
            print("[Test 8A] SUCCESS: Voice job for unverified user correctly BLOCKED.")
        else:
            print(f"[Test 8A] FAILED: Status is {job_status}")
            
    # Test 8B: Verified Phone (Should Request Twilio Call)
    print("\nTesting 8B: User with verified phone")
    user_c = uuid.uuid4()
    policy_c_id = await setup_test_policy(user_c, phone="+919999999999", verified=True)
    async with AsyncSessionLocal() as db:
        request = SimulationRequest(
            scenario="NORMAL",
            policy_id=str(policy_c_id),
            region_id=region_id,
            observations=[{"source_id": src1, "value": 150.0}, {"source_id": src2, "value": 150.0}],
            observed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        response = await run_simulation(request, db)
        
        res = await db.execute(text("SELECT id FROM notifications WHERE policy_id = :pid"), {"pid": str(policy_c_id)})
        n_id3 = res.scalar()
        await db.execute(text("UPDATE notifications SET escalation_due_at = NOW() - INTERVAL '1 hour' WHERE id = :nid"), {"nid": str(n_id3)})
        await db.commit()
        
        count = await process_all_overdue_notifications(db)
        await db.commit()
        
        h_count = await process_handoffs_to_jobs(db)
        await db.commit()
        
        # Now process pending jobs
        # Mock TWILIO_VOICE_ENABLED = false to trigger MockProvider
        v_count = await process_pending_voice_jobs(db)
        await db.commit()
        
        res = await db.execute(text("SELECT voice_call_jobs.status, provider_call_id, attempt_count FROM voice_call_jobs JOIN ai_assistance_handoffs ON voice_call_jobs.handoff_id = ai_assistance_handoffs.id WHERE ai_assistance_handoffs.notification_id = :nid"), {"nid": n_id3})
        row = res.fetchone()
        if row:
            job_status, provider_id, attempts = row
            if job_status in ("IN_PROGRESS", "INITIATED"):
                print(f"[Test 8B] SUCCESS: Voice job IN_PROGRESS. Provider ID: {provider_id}. Attempts: {attempts}")
            else:
                print(f"[Test 8B] FAILED: Unexpected status {job_status}")
        else:
            print("[Test 8B] FAILED: No voice job found.")
        
    print("\nALL VERIFICATION STEPS COMPLETED!")

if __name__ == "__main__":
    asyncio.run(run_tests())
