import asyncio
import pytest
import pytest_asyncio
import uuid
import datetime
import jwt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import app
from database import async_engine, AsyncSessionLocal
from config import get_settings

settings = get_settings()

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()

@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncSession:
    """
    Yields a DB session connected to the real PostgreSQL instance.
    Every test runs in a nested transaction and is rolled back.
    """
    conn = await async_engine.connect()
    trans = await conn.begin()
    
    session_factory = async_sessionmaker(
        bind=conn,
        expire_on_commit=False,
        class_=AsyncSession,
        join_transaction_mode="create_savepoint"
    )
    session = session_factory()
    
    yield session
    
    await session.close()
    await trans.rollback()
    await conn.close()

@pytest_asyncio.fixture
async def async_client(db: AsyncSession) -> AsyncClient:
    """
    FastAPI testing client.
    Overrides the database dependency to use the test session with SAVEPOINTs.
    """
    from database import get_db
    
    async def override_get_db():
        yield db
        
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
        
    app.dependency_overrides.clear()

def create_mock_jwt(sub: str, expired: bool = False, invalid: bool = False) -> str:
    secret = settings.supabase_jwt_secret
    if invalid:
        secret = "wrong_secret"
    
    exp = datetime.datetime.now(datetime.timezone.utc)
    if expired:
        exp -= datetime.timedelta(hours=1)
    else:
        exp += datetime.timedelta(hours=1)
        
    payload = {
        "sub": sub,
        "exp": exp,
        "user_metadata": {"full_name": "Test User"}
    }
    return jwt.encode(payload, secret, algorithm="HS256")

@pytest_asyncio.fixture
async def test_data(db: AsyncSession):
    now = datetime.datetime.now(datetime.timezone.utc)
    
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    
    from models.policyholder import Policyholder
    ph_a = Policyholder(auth_user_id=user_a_id, display_name=f"User A {user_a_id}", phone_verified=True, phone_number=f"+1555{str(user_a_id)[:6]}", updated_at=now)
    ph_b = Policyholder(auth_user_id=user_b_id, display_name=f"User B {user_b_id}", phone_verified=True, phone_number=f"+1555{str(user_b_id)[:6]}", updated_at=now)
    db.add_all([ph_a, ph_b])
    await db.flush()
    
    from models.wallet import Wallet
    wallet_a = Wallet(policyholder_id=ph_a.id, balance_paise=1000, currency="INR", status="ACTIVE", updated_at=now)
    wallet_b = Wallet(policyholder_id=ph_b.id, balance_paise=2000, currency="INR", status="ACTIVE", updated_at=now)
    db.add_all([wallet_a, wallet_b])
    await db.flush()
    
    from models.region import MicroRegion
    region_a = MicroRegion(name="Test Region A", code=f"REG_A_{uuid.uuid4().hex[:8]}", timezone="Asia/Kolkata", updated_at=now)
    db.add_all([region_a])
    await db.flush()

    from models.policy import TriggerRule
    rule_a = TriggerRule(metric="rainfall", threshold_operator=">=", threshold_value=100.0, unit="mm", observation_window_minutes=60, consensus_quorum=2, version=uuid.uuid4().int % 10000 + 10)
    db.add_all([rule_a])
    await db.flush()

    from models.policy import Policy, PolicyStatus
    policy_a = Policy(policyholder_id=ph_a.id, region_id=region_a.id, trigger_rule_id=rule_a.id, name="Policy A", status=PolicyStatus.ACTIVE.value, premium_amount_paise=100, payout_amount_paise=1000000, updated_at=now, start_at=now, end_at=now + datetime.timedelta(days=365))
    policy_b = Policy(policyholder_id=ph_b.id, region_id=region_a.id, trigger_rule_id=rule_a.id, name="Policy B", status=PolicyStatus.ACTIVE.value, premium_amount_paise=100, payout_amount_paise=1000000, updated_at=now, start_at=now, end_at=now + datetime.timedelta(days=365))
    db.add_all([policy_a, policy_b])
    await db.flush()
    
    rule_a.policy_id = policy_a.id
    await db.flush()
    
    return {
        "user_a_id": user_a_id,
        "user_b_id": user_b_id,
        "token_a": create_mock_jwt(str(user_a_id)),
        "token_b": create_mock_jwt(str(user_b_id)),
        "invalid_token": create_mock_jwt(str(user_a_id), invalid=True),
        "expired_token": create_mock_jwt(str(user_a_id), expired=True),
        "ph_a": ph_a,
        "ph_b": ph_b,
        "wallet_a": wallet_a,
        "wallet_b": wallet_b,
        "region_a": region_a,
        "rule_a": rule_a,
        "policy_a": policy_a,
        "policy_b": policy_b,
    }
