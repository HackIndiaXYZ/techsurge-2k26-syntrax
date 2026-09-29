import pytest
import uuid
from sqlalchemy import select
from models.payout import Payout, PayoutStatus
from models.wallet import Wallet
from models.trigger import TriggerEvaluation, TriggerStatus
from services.settlement import settle_payout
from models.consensus import ConsensusResult, ConsensusStatus
import datetime

@pytest.fixture
async def trigger_eval(db, test_data):
    cr = ConsensusResult(
        id=uuid.uuid4(),
        region_id=test_data["region_a"].id,
        metric="rainfall",
        window_start=datetime.datetime.now(datetime.timezone.utc),
        window_end=datetime.datetime.now(datetime.timezone.utc),
        status=ConsensusStatus.REACHED.value,
        quorum=2,
        consensus_value_mm=110.0
    )
    db.add(cr)
    await db.flush()

    te = TriggerEvaluation(
        id=uuid.uuid4(),
        policy_id=test_data["policy_a"].id,
        consensus_result_id=cr.id,
        trigger_status=TriggerStatus.TRIGGERED.value,
        evaluated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(te)
    await db.flush()
    return te

@pytest.mark.asyncio
async def test_settlement_success(db, test_data, trigger_eval):
    policy = test_data["policy_a"]
    payout, status = await settle_payout(trigger_eval, policy, str(uuid.uuid4()), db)
    
    assert status == "NEW"
    assert payout.status == PayoutStatus.SUCCESS.value
    assert payout.amount_paise == 1000000
    
    wallet = await db.scalar(select(Wallet).where(Wallet.id == test_data["wallet_a"].id))
    assert wallet.balance_paise == 1000000 + 1000

@pytest.mark.asyncio
async def test_settlement_duplicate(db, test_data, trigger_eval):
    policy = test_data["policy_a"]
    # First settlement
    p1, s1 = await settle_payout(trigger_eval, policy, str(uuid.uuid4()), db)
    assert s1 == "NEW"
    
    # Second settlement
    p2, s2 = await settle_payout(trigger_eval, policy, str(uuid.uuid4()), db)
    assert s2 == "ALREADY_SETTLED"
    assert p1.id == p2.id

    wallet = await db.scalar(select(Wallet).where(Wallet.id == test_data["wallet_a"].id))
    assert wallet.balance_paise == 1001000

@pytest.mark.asyncio
async def test_settlement_concurrent():
    # This requires true concurrent PostgreSQL transactions
    import asyncio
    import uuid
    import datetime
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy import delete
    import config

    # Create fresh engine for this test's event loop
    settings = config.get_settings()
    local_async_engine = create_async_engine(settings.database_url, pool_size=10, max_overflow=20)
    from models.policyholder import Policyholder
    from models.wallet import Wallet
    from models.region import MicroRegion
    from models.trigger import TriggerEvaluation
    from models.policy import Policy, TriggerRule
    from models.payout import Payout
    from services.settlement import settle_payout
    
    now = datetime.datetime.now(datetime.timezone.utc)
    user_id = uuid.uuid4()
    
    # 1. Setup real committed data using a fresh connection
    async with AsyncSession(local_async_engine) as session:
        ph = Policyholder(auth_user_id=user_id, display_name=f"User {user_id}", phone_verified=True, phone_number=f"+1555{str(user_id)[:6]}", updated_at=now)
        session.add(ph)
        await session.flush()
        
        wallet = Wallet(policyholder_id=ph.id, balance_paise=1000, currency="INR", status="ACTIVE", updated_at=now)
        session.add(wallet)
        await session.flush()
        
        region = MicroRegion(code=f"REG_{str(user_id)[:8]}", name="Test Region", timezone="Asia/Kolkata", active=True, updated_at=now)
        session.add(region)
        await session.flush()
        
        import random
        rule = TriggerRule(metric="rainfall", threshold_operator=">=", threshold_value=100.0, unit="mm", observation_window_minutes=60, version=random.randint(10000, 90000), consensus_quorum=2)
        session.add(rule)
        await session.flush()
        
        policy = Policy(
            policyholder_id=ph.id,
            region_id=region.id,
            trigger_rule_id=rule.id,
            payout_amount_paise=1000000,
            premium_amount_paise=100,
            status="ACTIVE",
            start_at=now,
            end_at=now + datetime.timedelta(days=365),
            name="Policy Concurrency",
            updated_at=now
        )
        session.add(policy)
        await session.flush()
        
        from models.consensus import ConsensusResult
        cr = ConsensusResult(
            region_id=region.id,
            metric="rainfall",
            window_start=now,
            window_end=now,
            status="REACHED",
            consensus_value_mm=110.0,
            quorum=2
        )
        session.add(cr)
        await session.flush()
        
        trigger_eval = TriggerEvaluation(
            policy_id=policy.id,
            consensus_result_id=cr.id,
            trigger_status="TRIGGERED",
            evaluated_at=now
        )
        session.add(trigger_eval)
        await session.flush()
        
        policy_id = policy.id
        trigger_eval_id = trigger_eval.id
        wallet_id = wallet.id
        cr_id = cr.id
        rule_id = rule.id
        region_id = region.id
        ph_id = ph.id
        idem_key = str(uuid.uuid4())

        await session.commit()

    # 2. Run concurrent workers
    async def worker(worker_id):
        async with AsyncSession(local_async_engine) as worker_session:
            try:
                local_trigger = await worker_session.get(TriggerEvaluation, trigger_eval_id)
                local_policy = await worker_session.get(Policy, policy_id)
                p, s = await settle_payout(local_trigger, local_policy, idem_key, worker_session)
                await worker_session.commit()
                return p, s, worker_id
            except Exception as e:
                import traceback
                traceback.print_exc()
                await worker_session.rollback()
                return None, "ERROR", worker_id

    results = await asyncio.gather(*[worker(i) for i in range(5)])
    
    # Exactly one should return NEW
    new_count = sum(1 for p, s, w in results if s == "NEW")
    
    # 3. Cleanup and assertions
    async with AsyncSession(local_async_engine) as session:
        # Check wallet balance
        final_wallet = await session.get(Wallet, wallet_id)
        final_balance = final_wallet.balance_paise
        
        # Cleanup
        from models.wallet import WalletTransaction
        await session.execute(delete(WalletTransaction).where(WalletTransaction.wallet_id == wallet_id))
        await session.execute(delete(Payout).where(Payout.policy_id == policy_id))
        await session.execute(delete(TriggerEvaluation).where(TriggerEvaluation.id == trigger_eval_id))
        await session.execute(delete(ConsensusResult).where(ConsensusResult.id == cr_id))
        await session.execute(delete(Policy).where(Policy.id == policy_id))
        await session.execute(delete(TriggerRule).where(TriggerRule.id == rule_id))
        await session.execute(delete(MicroRegion).where(MicroRegion.id == region_id))
        await session.execute(delete(Wallet).where(Wallet.id == wallet_id))
        await session.execute(delete(Policyholder).where(Policyholder.id == ph_id))
        await session.commit()
        
    assert new_count == 1
    assert final_balance == 1001000

@pytest.mark.asyncio
async def test_settlement_not_triggered_fails(db, test_data):
    policy = test_data["policy_a"]
    
    cr = ConsensusResult(
        id=uuid.uuid4(),
        region_id=test_data["region_a"].id,
        metric="rainfall",
        window_start=datetime.datetime.now(datetime.timezone.utc),
        window_end=datetime.datetime.now(datetime.timezone.utc),
        status=ConsensusStatus.REACHED.value,
        quorum=2,
        consensus_value_mm=90.0
    )
    db.add(cr)
    await db.flush()

    te = TriggerEvaluation(
        id=uuid.uuid4(),
        policy_id=policy.id,
        consensus_result_id=cr.id,
        trigger_status=TriggerStatus.NOT_TRIGGERED.value,
        evaluated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(te)
    await db.flush()
    
    payout, status = await settle_payout(te, policy, str(uuid.uuid4()), db)
    assert status == "SKIPPED"
    assert payout is None
