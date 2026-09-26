import pytest
import pytest_asyncio
import uuid
import time
import jwt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from config import get_settings
from database import get_db, AsyncSessionLocal
from models.policyholder import Policyholder
from models.policy import Policy, PolicyStatus
from models.region import MicroRegion

settings = get_settings()

def generate_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "role": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")


@pytest_asyncio.fixture
async def setup_users_and_policies(db: AsyncSession):
    async def get_test_db():
        return db
    app.dependency_overrides[get_db] = get_test_db
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())
    
    # Create user A profile by calling /me
    token_a = generate_token(user_a_id)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_a = await client.get("/me", headers={"Authorization": f"Bearer {token_a}"})
        assert resp_a.status_code == 200
        ph_a_id = resp_a.json()["policyholder_id"]

    # Create user B profile by calling /me
    token_b = generate_token(user_b_id)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_b = await client.get("/me", headers={"Authorization": f"Bearer {token_b}"})
        assert resp_b.status_code == 200
        ph_b_id = resp_b.json()["policyholder_id"]

    # Create policy for A
    region_id = uuid.UUID("00000000-0000-0000-0000-000000000001") # demo region exists in seed
    
    # Manually create policies
    policy_a = Policy(
        policyholder_id=uuid.UUID(ph_a_id),
        region_id=region_id,
        name="Test Policy A",
        currency="INR",
        payout_amount_paise=10000,
        status=PolicyStatus.ACTIVE
    )
    db.add(policy_a)
    
    policy_b = Policy(
        policyholder_id=uuid.UUID(ph_b_id),
        region_id=region_id,
        name="Test Policy B",
        currency="INR",
        payout_amount_paise=20000,
        status=PolicyStatus.ACTIVE
    )
    db.add(policy_b)
    await db.commit()
    await db.refresh(policy_a)
    await db.refresh(policy_b)
    
    return {
        "token_a": token_a,
        "policy_a_id": str(policy_a.id),
        "token_b": token_b,
        "policy_b_id": str(policy_b.id),
        "user_a_id": user_a_id
    }

@pytest.mark.asyncio
async def test_authz_user_a_can_access_own_policy(setup_users_and_policies):
    data = setup_users_and_policies
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/policies/{data['policy_a_id']}", headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_authz_user_b_can_access_own_policy(setup_users_and_policies):
    data = setup_users_and_policies
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/policies/{data['policy_b_id']}", headers={"Authorization": f"Bearer {data['token_b']}"})
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_authz_cross_access_rejected(setup_users_and_policies):
    data = setup_users_and_policies
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # A tries to get B
        resp1 = await client.get(f"/policies/{data['policy_b_id']}", headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp1.status_code == 403
        
        # B tries to get A
        resp2 = await client.get(f"/policies/{data['policy_a_id']}", headers={"Authorization": f"Bearer {data['token_b']}"})
        assert resp2.status_code == 403

@pytest.mark.asyncio
async def test_authz_unauthenticated_rejected(setup_users_and_policies):
    data = setup_users_and_policies
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/policies/{data['policy_a_id']}")
        assert resp.status_code == 401

@pytest.mark.asyncio
async def test_authz_invalid_jwt_rejected(setup_users_and_policies):
    data = setup_users_and_policies
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/policies/{data['policy_a_id']}", headers={"Authorization": "Bearer invalid.jwt"})
        assert resp.status_code == 401

@pytest.mark.asyncio
async def test_authz_user_no_policies_empty_state(db: AsyncSession):
    async def get_test_db():
        return db
    app.dependency_overrides[get_db] = get_test_db
    # TEST 7: A user with no policies receives a valid empty response rather than an error.
    user_id = str(uuid.uuid4())
    token = generate_token(user_id)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # /me will create the policyholder, but NO policies
        resp = await client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        
        data = resp.json()
        assert "policies" in data
        assert len(data["policies"]) == 0 # Valid empty response

@pytest.mark.asyncio
async def test_authz_user_a_can_run_simulation_on_own_policy(setup_users_and_policies):
    data = setup_users_and_policies
    payload = {
        "scenario": "NORMAL",
        "policy_id": data['policy_a_id'],
        "region_id": "00000000-0000-0000-0000-000000000001",
        "observations": [
            {"source_id": "00000000-0000-0000-0000-000000000010", "value": 110},
        ],
        "observed_at": "2026-09-18T10:00:00Z"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/simulations", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        # Note: it might fail with 404/400 if setup is incomplete for simulation, but it MUST NOT return 401/403
        assert resp.status_code not in [401, 403]

@pytest.mark.asyncio
async def test_authz_cross_access_simulation_rejected(setup_users_and_policies):
    data = setup_users_and_policies
    payload = {
        "scenario": "NORMAL",
        "policy_id": data['policy_b_id'], # A trying to simulate B
        "region_id": "00000000-0000-0000-0000-000000000001",
        "observations": [
            {"source_id": "00000000-0000-0000-0000-000000000010", "value": 110},
        ],
        "observed_at": "2026-09-18T10:00:00Z"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/simulations", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 403

