"""
tests/test_policy_lifecycle_phase3b.py — Phase 3B Policy Lifecycle Tests.

Covers:
1. Authenticated user can create their own policy
2. Unauthenticated policy creation → 401
3. Invalid JWT → 401
4. Policy belongs to authenticated policyholder
5. User cannot create policy for another policyholder
6. User cannot access another user's policy (preserved from 3A)
7. Premium stored as integer paise
8. Coverage stored as integer paise
9. Invalid monetary values rejected
10. start_at < end_at enforced
11. Newly created paid policy is PAYMENT_PENDING
12. Caller cannot directly force ACTIVE
13. Valid foreign keys required (region must exist)
14. Empty-state user still receives policies=[]
15. Existing Phase 3A authorization tests continue passing
16. All Phase 0–2 tests continue passing
"""
import pytest
import pytest_asyncio
import uuid
import time
import jwt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from config import get_settings
from database import get_db

settings = get_settings()

DEMO_REGION_ID = "00000000-0000-0000-0000-000000000001"


def generate_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "role": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")


def make_valid_policy_payload(**overrides) -> dict:
    """Generate a valid policy creation payload, with optional overrides."""
    base = {
        "region_id": DEMO_REGION_ID,
        "name": "Test Rainfall Policy",
        "premium_amount_paise": 50000,  # ₹500
        "coverage_amount_paise": 1000000,  # ₹10,000
        "currency": "INR",
        "start_at": "2026-10-01T00:00:00Z",
        "end_at": "2026-12-31T23:59:59Z",
    }
    base.update(overrides)
    return base


@pytest_asyncio.fixture
async def auth_setup(db: AsyncSession):
    """Set up two authenticated users for testing."""
    async def get_test_db():
        return db
    app.dependency_overrides[get_db] = get_test_db

    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())

    token_a = generate_token(user_a_id)
    token_b = generate_token(user_b_id)

    # Create policyholder profiles via /me
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_a = await client.get("/me", headers={"Authorization": f"Bearer {token_a}"})
        assert resp_a.status_code == 200

        resp_b = await client.get("/me", headers={"Authorization": f"Bearer {token_b}"})
        assert resp_b.status_code == 200

    yield {
        "token_a": token_a,
        "token_b": token_b,
        "user_a_id": user_a_id,
        "user_b_id": user_b_id,
    }

    app.dependency_overrides.pop(get_db, None)


# ─── TEST 1: Authenticated user can create their own policy ────────────────
@pytest.mark.asyncio
async def test_create_policy_authenticated(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["policy_id"]
        assert body["name"] == "Test Rainfall Policy"
        assert body["status"] == "PAYMENT_PENDING"


# ─── TEST 2: Unauthenticated policy creation → 401 ────────────────────────
@pytest.mark.asyncio
async def test_create_policy_unauthenticated(auth_setup):
    payload = make_valid_policy_payload()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload)
        assert resp.status_code == 401


# ─── TEST 3: Invalid JWT → 401 ────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_policy_invalid_jwt(auth_setup):
    payload = make_valid_policy_payload()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": "Bearer invalid.jwt.here"})
        assert resp.status_code == 401


# ─── TEST 4: Created policy belongs to authenticated policyholder ──────────
@pytest.mark.asyncio
async def test_created_policy_belongs_to_caller(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create policy as user A
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 201
        policy_id = resp.json()["policy_id"]

        # User A can access it
        resp_get = await client.get(f"/policies/{policy_id}", headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp_get.status_code == 200


# ─── TEST 5: User cannot create policy for another policyholder ────────────
# (Policy is always auto-assigned to the caller via JWT; no policyholder_id in request)
@pytest.mark.asyncio
async def test_policy_auto_assigned_to_caller(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 201
        policy_id = resp.json()["policy_id"]

        # User B cannot access A's policy
        resp_b = await client.get(f"/policies/{policy_id}", headers={"Authorization": f"Bearer {data['token_b']}"})
        assert resp_b.status_code == 403


# ─── TEST 6: Cross-user access rejected (preserved from Phase 3A) ─────────
@pytest.mark.asyncio
async def test_cross_user_policy_access_rejected(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # A creates
        resp_a = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp_a.status_code == 201
        policy_a_id = resp_a.json()["policy_id"]

        # B creates
        resp_b = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_b']}"})
        assert resp_b.status_code == 201
        policy_b_id = resp_b.json()["policy_id"]

        # A tries B's → 403
        resp_ab = await client.get(f"/policies/{policy_b_id}", headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp_ab.status_code == 403

        # B tries A's → 403
        resp_ba = await client.get(f"/policies/{policy_a_id}", headers={"Authorization": f"Bearer {data['token_b']}"})
        assert resp_ba.status_code == 403


# ─── TEST 7: Premium stored as integer paise ──────────────────────────────
@pytest.mark.asyncio
async def test_premium_stored_as_integer_paise(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload(premium_amount_paise=75000)  # ₹750
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["premium_amount_paise"] == 75000
        assert isinstance(body["premium_amount_paise"], int)
        assert body["premium_amount_inr_display"] == "₹750"


# ─── TEST 8: Coverage stored as integer paise ─────────────────────────────
@pytest.mark.asyncio
async def test_coverage_stored_as_integer_paise(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload(coverage_amount_paise=2000000)  # ₹20,000
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["coverage_amount_paise"] == 2000000
        assert isinstance(body["coverage_amount_paise"], int)
        assert body["coverage_amount_inr_display"] == "₹20,000"


# ─── TEST 9: Invalid monetary values rejected ─────────────────────────────
@pytest.mark.asyncio
async def test_invalid_monetary_values_rejected(auth_setup):
    data = auth_setup
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Zero premium
        payload = make_valid_policy_payload(premium_amount_paise=0)
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 422

        # Negative coverage
        payload = make_valid_policy_payload(coverage_amount_paise=-100)
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 422


# ─── TEST 10: start_at < end_at enforced ──────────────────────────────────
@pytest.mark.asyncio
async def test_dates_validation_start_before_end(auth_setup):
    data = auth_setup
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # end_at before start_at
        payload = make_valid_policy_payload(
            start_at="2026-12-31T23:59:59Z",
            end_at="2026-10-01T00:00:00Z",
        )
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 422

        # Same start and end
        payload = make_valid_policy_payload(
            start_at="2026-10-01T00:00:00Z",
            end_at="2026-10-01T00:00:00Z",
        )
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 422


# ─── TEST 11: Newly created paid policy is PAYMENT_PENDING ────────────────
@pytest.mark.asyncio
async def test_new_policy_status_is_payment_pending(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "PAYMENT_PENDING"
        # NOT ACTIVE — requires payment verification in Phase 3C


# ─── TEST 12: Caller cannot directly force ACTIVE ─────────────────────────
@pytest.mark.asyncio
async def test_cannot_force_active_status(auth_setup):
    data = auth_setup
    # Even if someone adds status to the request body, it's ignored
    payload = make_valid_policy_payload()
    payload["status"] = "ACTIVE"  # Attempt to force ACTIVE
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        # Should succeed but status should be PAYMENT_PENDING regardless
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "PAYMENT_PENDING"


# ─── TEST 13: Valid foreign keys required (region must exist) ──────────────
@pytest.mark.asyncio
async def test_invalid_region_rejected(auth_setup):
    data = auth_setup
    payload = make_valid_policy_payload(region_id="ffffffff-ffff-ffff-ffff-ffffffffffff")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/policies", json=payload, headers={"Authorization": f"Bearer {data['token_a']}"})
        assert resp.status_code == 404


# ─── TEST 14: Empty-state user still receives policies=[] ─────────────────
@pytest.mark.asyncio
async def test_empty_state_user(auth_setup):
    data = auth_setup
    # user_a just had /me called, no policies created yet via test
    # Create a fresh user with no policies
    fresh_user = str(uuid.uuid4())
    token = generate_token(fresh_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        body = resp.json()
        assert "policies" in body
        assert len(body["policies"]) == 0
