import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def drop():
    with open('../railway_vars.json', 'r') as f:
        vars = json.load(f)
    
    url = vars["DATABASE_URL"]
    engine = create_async_engine(url, connect_args={"statement_cache_size": 0})
    
    async with engine.begin() as conn:
        print("Dropping constraint...")
        await conn.execute(text('ALTER TABLE trigger_rules DROP CONSTRAINT IF EXISTS "uq_trigger_rules_definition"'))
        print("Dropped!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(drop())
