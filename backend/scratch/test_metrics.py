import asyncio
from httpx import AsyncClient, ASGITransport
from main import app

async def test_metrics():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/metrics")
        print("Status:", response.status_code)
        print("Response:", response.json())

if __name__ == "__main__":
    asyncio.run(test_metrics())
