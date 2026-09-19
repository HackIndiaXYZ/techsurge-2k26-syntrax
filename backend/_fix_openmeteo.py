import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as session:
        await session.execute(text(
            "UPDATE weather_sources SET code = 'openmeteo' "
            "WHERE code = 'open-meteo'"
        ))
        await session.commit()
        print("Fixed OpenMeteo DB code")

asyncio.run(run())
