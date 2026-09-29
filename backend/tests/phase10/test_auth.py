import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_valid(async_client: AsyncClient, test_data: dict):
    res = await async_client.get("/me", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res.status_code == 200
    data = res.json()
    assert data["policyholder_id"] == str(test_data["ph_a"].id)

@pytest.mark.asyncio
async def test_auth_missing_jwt(async_client: AsyncClient, test_data: dict):
    res = await async_client.get("/me")
    assert res.status_code in (401, 403)

@pytest.mark.asyncio
async def test_auth_invalid_jwt(async_client: AsyncClient, test_data: dict):
    res = await async_client.get("/me", headers={"Authorization": f"Bearer {test_data['invalid_token']}"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_auth_expired_jwt(async_client: AsyncClient, test_data: dict):
    res = await async_client.get("/me", headers={"Authorization": f"Bearer {test_data['expired_token']}"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_auth_malformed_jwt(async_client: AsyncClient, test_data: dict):
    res = await async_client.get("/me", headers={"Authorization": "Bearer malformed.jwt.token"})
    assert res.status_code == 401
