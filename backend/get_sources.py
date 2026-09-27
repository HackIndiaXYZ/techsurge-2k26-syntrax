import json
import asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

async def go():
    with open('../railway_vars.json', 'r') as f:
        vars = json.load(f)
    
    url = vars['DATABASE_URL'].replace('postgresql://', 'postgresql+asyncpg://')
    engine = create_async_engine(url, connect_args={"statement_cache_size": 0})
    
    async with engine.connect() as conn:
        res = await conn.execute(sa.text("SELECT id FROM weather_sources LIMIT 3"))
        print([str(r[0]) for r in res.fetchall()])

if __name__ == '__main__':
    asyncio.run(go())
