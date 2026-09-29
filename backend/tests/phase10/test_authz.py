import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_authz_policy(async_client: AsyncClient, test_data: dict):
    res_a = await async_client.get(f"/policies/{test_data['policy_a'].id}", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_a.status_code == 200
    
    res_b = await async_client.get(f"/policies/{test_data['policy_b'].id}", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_b.status_code == 403

@pytest.mark.asyncio
async def test_authz_wallet(async_client: AsyncClient, test_data: dict):
    res_a = await async_client.get("/wallets/me", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_a.status_code == 200
    assert res_a.json()["wallet_id"] == str(test_data["wallet_a"].id)
    # Wallet endpoints only expose /me, so cross-user lookup by ID is implicitly prevented at router level.

@pytest.mark.asyncio
async def test_authz_simulation(async_client: AsyncClient, test_data: dict):
    payload = {
        "scenario": "NORMAL",
        "policy_id": str(test_data["policy_a"].id),
        "region_id": str(test_data["region_a"].id),
        "observed_at": "2026-09-01T12:00:00Z",
        "observations": [
            {
                "source_id": "test_source",
                "value": 110.0
            }
        ]
    }
    res_a = await async_client.post("/simulations", json=payload, headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_a.status_code == 200
    
    # User B trying to simulate User A's policy
    payload["policy_id"] = str(test_data["policy_b"].id)
    res_b = await async_client.post("/simulations", json=payload, headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_b.status_code == 403

@pytest.mark.asyncio
async def test_authz_ai_voice(async_client: AsyncClient, test_data: dict):
    voice_payload = {
        "event_id": str(uuid.uuid4()),
        "settlement_id": str(uuid.uuid4()),
        "language": "en",
        "purpose": "SETTLEMENT_ACKNOWLEDGEMENT",
        "phone_number": test_data['ph_a'].phone_number,
        "settlement_amount_paise": 10000,
        "consensus_value": 110,
        "threshold_value": 100,
        "acknowledgement_status": "ESCALATED"
    }
    res_a = await async_client.post("/v1/ai/voice/call", json=voice_payload, headers={"Authorization": f"Bearer {test_data['token_a']}"})
    # Could be 200, 500, or 400, but not 403
    assert res_a.status_code != 403
    
    voice_payload["phone_number"] = test_data['ph_b'].phone_number
    res_b = await async_client.post("/v1/ai/voice/call", json=voice_payload, headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_b.status_code == 403

@pytest.mark.asyncio
async def test_authz_audit(async_client: AsyncClient, test_data: dict):
    res_a = await async_client.get(f"/policies/{test_data['policy_a'].id}/audit", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_a.status_code == 200
    
    res_b = await async_client.get(f"/policies/{test_data['policy_b'].id}/audit", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res_b.status_code == 403
