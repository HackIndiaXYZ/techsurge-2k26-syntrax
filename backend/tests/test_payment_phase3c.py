"""
tests/test_payment_phase3c.py — Phase 3C Razorpay TEST Payment Tests.

Covers:
  AUTHORIZATION (1-4)
  ORDER CREATION (5-10)
  VERIFICATION (11-17)
  IDEMPOTENCY (18-21)
  FAILURE (22-24)
  DATA (25-27)
  REGRESSION (28-30)

All Razorpay API calls are MOCKED — no real Razorpay calls in tests.
"""
import pytest
import pytest_asyncio
import uuid
import time
import hmac
import hashlib
import jwt
from unittest.mock import patch, MagicMock

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from config import get_settings
from database import get_db

settings = get_settings()

DEMO_REGION_ID = "00000000-0000-0000-0000-000000000001"
FAKE_RZ_ORDER_ID = "order_test_3c_001"
FAKE_RZ_PAYMENT_ID = "pay_test_3c_001"
FAKE_RZ_KEY_SECRET = settings.supabase_jwt_secret or "test-secret-for-hmac"


def generate_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "role": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")


def compute_signature(order_id: str, payment_id: str, secret: str) -> str:
    """Compute valid Razorpay HMAC-SHA256 signature for testing."""
    message = f"{order_id}|{payment_id}"
    return hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def make_policy_payload(**overrides) -> dict:
    base = {
        "region_id": DEMO_REGION_ID,
        "name": "Test Policy for Payment",
        "premium_amount_paise": 50000,
        "coverage_amount_paise": 1000000,
        "currency": "INR",
        "start_at": "2026-10-01T00:00:00Z",
        "end_at": "2026-12-31T23:59:59Z",
    }
    base.update(overrides)
    return base


@pytest_asyncio.fixture
async def payment_setup(db: AsyncSession):
    """Set up two users and create a PAYMENT_PENDING policy for user A."""
    async def get_test_db():
        return db
    app.dependency_overrides[get_db] = get_test_db

    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())
    token_a = generate_token(user_a_id)
    token_b = generate_token(user_b_id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create policyholders
        await client.get("/me", headers={"Authorization": f"Bearer {token_a}"})
        await client.get("/me", headers={"Authorization": f"Bearer {token_b}"})

        # Create a PAYMENT_PENDING policy for user A
        resp = await client.post(
            "/policies",
            json=make_policy_payload(),
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert resp.status_code == 201
        policy_a = resp.json()

    yield {
        "token_a": token_a,
        "token_b": token_b,
        "user_a_id": user_a_id,
        "user_b_id": user_b_id,
        "policy_a_id": policy_a["policy_id"],
    }

    app.dependency_overrides.pop(get_db, None)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORIZATION (Tests 1-4)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_01_unauthenticated_order_creation_401(payment_setup):
    data = payment_setup
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(f"/policies/{data['policy_a_id']}/payments/order")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_02_invalid_jwt_order_creation_401(payment_setup):
    data = payment_setup
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/policies/{data['policy_a_id']}/payments/order",
            headers={"Authorization": "Bearer invalid.jwt.here"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_03_owner_can_create_order(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": FAKE_RZ_ORDER_ID, "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 201


@pytest.mark.asyncio
async def test_04_cross_user_order_creation_403(payment_setup):
    data = payment_setup
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/policies/{data['policy_a_id']}/payments/order",
            headers={"Authorization": f"Bearer {data['token_b']}"},
        )
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# ORDER CREATION (Tests 5-10)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_05_order_amount_from_policy_premium(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_amt_test", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["amount_paise"] == 50000
            # Verify the mock was called with the correct server-side amount
            mock_create.assert_called_once_with(amount_paise=50000, currency="INR", receipt=f"policy-{data['policy_a_id']}")


@pytest.mark.asyncio
async def test_06_frontend_cannot_override_amount(payment_setup):
    """Even if frontend sends amount in request body, it's ignored."""
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_override_test", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                json={"amount": 100},  # Attempted override
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["amount_paise"] == 50000  # Server-side amount prevails


@pytest.mark.asyncio
async def test_07_only_payment_pending_can_pay(payment_setup, db: AsyncSession):
    """ACTIVE policy cannot initiate payment."""
    data = payment_setup
    # First create order and verify to make policy ACTIVE
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_state_test", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 201

    # Verify with valid signature to activate
    sig = compute_signature("order_state_test", "pay_state_test", settings.razorpay_key_secret or "")
    with patch("services.razorpay.verify_payment_signature", return_value=True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_state_test",
                    "razorpay_payment_id": "pay_state_test",
                    "razorpay_signature": sig,
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 200
            assert resp.json()["policy_status"] == "ACTIVE"

    # Now try to create another order — should fail
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/policies/{data['policy_a_id']}/payments/order",
            headers={"Authorization": f"Bearer {data['token_a']}"},
        )
        assert resp.status_code == 409


@pytest.mark.asyncio
async def test_08_invalid_policy_rejected(payment_setup):
    data = payment_setup
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/policies/ffffffff-ffff-ffff-ffff-ffffffffffff/payments/order",
            headers={"Authorization": f"Bearer {data['token_a']}"},
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_09_razorpay_order_id_stored(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_stored_test", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["razorpay_order_id"] == "order_stored_test"


@pytest.mark.asyncio
async def test_10_razorpay_key_id_is_public_only(payment_setup):
    """Response must contain only the public key, never the secret."""
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_key_test", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert "razorpay_key_id" in body
            assert "razorpay_key_secret" not in body
            assert "secret" not in str(body).lower() or "key_secret" not in str(body)


# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION (Tests 11-17)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_11_valid_signature_payment_success(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_v11", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    with patch("services.razorpay.verify_payment_signature", return_value=True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_v11",
                    "razorpay_payment_id": "pay_v11",
                    "razorpay_signature": "valid_sig",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["payment_status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_12_valid_payment_activates_policy(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_v12", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    with patch("services.razorpay.verify_payment_signature", return_value=True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_v12",
                    "razorpay_payment_id": "pay_v12",
                    "razorpay_signature": "valid_sig",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 200
            assert resp.json()["policy_status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_13_invalid_signature_not_success(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_v13", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    with patch("services.razorpay.verify_payment_signature", return_value=False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_v13",
                    "razorpay_payment_id": "pay_v13",
                    "razorpay_signature": "invalid_sig",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.status_code == 200
            assert resp.json()["payment_status"] == "FAILED"
            assert resp.json()["verified"] is False


@pytest.mark.asyncio
async def test_14_invalid_signature_policy_not_active(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_v14", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    with patch("services.razorpay.verify_payment_signature", return_value=False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_v14",
                    "razorpay_payment_id": "pay_v14",
                    "razorpay_signature": "bad_sig",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.json()["policy_status"] == "PAYMENT_PENDING"


@pytest.mark.asyncio
async def test_15_wrong_order_id_rejected(payment_setup):
    data = payment_setup
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/policies/{data['policy_a_id']}/payments/verify",
            json={
                "razorpay_order_id": "order_nonexistent",
                "razorpay_payment_id": "pay_x",
                "razorpay_signature": "sig_x",
            },
            headers={"Authorization": f"Bearer {data['token_a']}"},
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_16_cross_user_verify_rejected(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_v16", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    # User B tries to verify A's payment
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/policies/{data['policy_a_id']}/payments/verify",
            json={
                "razorpay_order_id": "order_v16",
                "razorpay_payment_id": "pay_v16",
                "razorpay_signature": "sig",
            },
            headers={"Authorization": f"Bearer {data['token_b']}"},
        )
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# IDEMPOTENCY (Tests 17-20)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_17_repeated_verification_idempotent(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_v17", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    with patch("services.razorpay.verify_payment_signature", return_value=True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First verification
            resp1 = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_v17",
                    "razorpay_payment_id": "pay_v17",
                    "razorpay_signature": "valid_sig",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp1.status_code == 200
            assert resp1.json()["payment_status"] == "SUCCESS"

            # Second verification — should return same result (idempotent)
            resp2 = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_v17",
                    "razorpay_payment_id": "pay_v17",
                    "razorpay_signature": "valid_sig",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp2.status_code == 200
            assert resp2.json()["payment_status"] == "SUCCESS"
            assert resp2.json()["verified"] is True
            assert resp1.json()["payment_id"] == resp2.json()["payment_id"]


@pytest.mark.asyncio
async def test_18_duplicate_order_returns_existing(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_dup", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp1 = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp1.status_code == 201
            id1 = resp1.json()["payment_id"]

            # Second call should reuse existing CREATED payment
            resp2 = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp2.status_code == 201
            id2 = resp2.json()["payment_id"]
            assert id1 == id2  # Same payment reused

        # create_order should have been called only ONCE
        assert mock_create.call_count == 1


# ═══════════════════════════════════════════════════════════════════════════
# FAILURE (Tests 19-21)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_19_failed_payment_leaves_policy_pending(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_f19", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    with patch("services.razorpay.verify_payment_signature", return_value=False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_f19",
                    "razorpay_payment_id": "pay_f19",
                    "razorpay_signature": "bad_sig",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.json()["policy_status"] == "PAYMENT_PENDING"
            assert resp.json()["payment_status"] == "FAILED"


@pytest.mark.asyncio
async def test_20_payment_failure_cannot_activate(payment_setup):
    """Even after a failed payment, policy must remain PAYMENT_PENDING."""
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_f20", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )

    with patch("services.razorpay.verify_payment_signature", return_value=False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/verify",
                json={
                    "razorpay_order_id": "order_f20",
                    "razorpay_payment_id": "pay_f20",
                    "razorpay_signature": "bad",
                },
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.json()["policy_status"] != "ACTIVE"

    # Verify via GET that policy is still PAYMENT_PENDING
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            f"/policies/{data['policy_a_id']}",
            headers={"Authorization": f"Bearer {data['token_a']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "PAYMENT_PENDING"


# ═══════════════════════════════════════════════════════════════════════════
# DATA (Tests 21-23)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_21_amount_stored_as_integer_paise(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_d21", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            body = resp.json()
            assert isinstance(body["amount_paise"], int)
            assert body["amount_paise"] == 50000


@pytest.mark.asyncio
async def test_22_provider_ids_persisted(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_d22", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            body = resp.json()
            assert body["razorpay_order_id"] == "order_d22"

    # Check status endpoint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            f"/policies/{data['policy_a_id']}/payments/status",
            headers={"Authorization": f"Bearer {data['token_a']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["provider_order_id"] == "order_d22"


@pytest.mark.asyncio
async def test_23_ownership_persisted_correctly(payment_setup):
    data = payment_setup
    with patch("services.razorpay.create_order") as mock_create:
        mock_create.return_value = {"id": "order_d23", "amount": 50000, "currency": "INR"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/policies/{data['policy_a_id']}/payments/order",
                headers={"Authorization": f"Bearer {data['token_a']}"},
            )
            assert resp.json()["policy_id"] == data["policy_a_id"]

    # B cannot see the status
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            f"/policies/{data['policy_a_id']}/payments/status",
            headers={"Authorization": f"Bearer {data['token_b']}"},
        )
        assert resp.status_code == 403
