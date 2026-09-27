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
    conn = await asyncpg.connect(db_url, statement_cache_size=0)
    
    try:
        row = await conn.fetchrow("SELECT id, name FROM micro_regions LIMIT 1")
        if row:
            print(f"Region ID: {row['id']} (Name: {row['name']})")
        else:
            print("No regions found in database.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()
        
if __name__ == "__main__":
    asyncio.run(main())
