import json
import asyncio
import asyncpg
import sys

async def main():
    with open('../railway_vars.json', 'r') as f:
        vars = json.load(f)
    
    db_url = vars.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found")
        sys.exit(1)
        
    db_url = db_url.replace("postgresql+asyncpg://", "postgres://").replace("postgresql://", "postgres://")
    conn = await asyncpg.connect(db_url)
    
    try:
        val = await conn.fetchval("SELECT version_num FROM alembic_version")
        print(f"alembic_version: {val}")
    except Exception as e:
        print(f"Error checking alembic_version: {e}")
    finally:
        await conn.close()
        
if __name__ == "__main__":
    asyncio.run(main())
