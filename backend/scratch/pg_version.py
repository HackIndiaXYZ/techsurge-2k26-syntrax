import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import get_settings

async def main():
    engine = create_async_engine(get_settings().DATABASE_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT version()'))
        print(res.scalar())
    await engine.dispose()

asyncio.run(main())
