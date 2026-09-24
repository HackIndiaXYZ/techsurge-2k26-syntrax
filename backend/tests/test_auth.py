import pytest
import jwt
from httpx import AsyncClient
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from main import app
from config import get_settings
import time

settings = get_settings()
# TBD: Need a real token to test valid case. We will mock it using the secret.

def generate_test_token(secret: str, expired: bool = False) -> str:
    payload = {
        "sub": "test-user-id",
        "role": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) - 3600 if expired else int(time.time()) + 3600
    }
    return jwt.encode(payload, secret, algorithm="HS256")

@pytest.mark.asyncio
async def test_auth_no_header():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/policies/e410b037-9755-4424-814a-50269f4711db")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth_malformed_header():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/policies/e410b037-9755-4424-814a-50269f4711db", headers={"Authorization": "Malformed token"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth_invalid_jwt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/policies/e410b037-9755-4424-814a-50269f4711db", headers={"Authorization": "Bearer invalid.jwt.token"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth_expired_jwt():
    secret = settings.supabase_jwt_secret
    expired_token = generate_test_token(secret, expired=True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/policies/e410b037-9755-4424-814a-50269f4711db", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth_wrong_signature():
    token = generate_test_token("wrong-secret")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/policies/e410b037-9755-4424-814a-50269f4711db", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
