import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from seeds.seed_demo_data import seed

async def go():
    with open('../railway_vars.json', 'r') as f:
        vars = json.load(f)
    
    url = vars['DATABASE_URL'].replace('postgresql://', 'postgresql+asyncpg://')
    engine = create_async_engine(url, connect_args={"statement_cache_size": 0})
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as db:
        await seed(db)
        await db.commit()

if __name__ == '__main__':
    asyncio.run(go())
