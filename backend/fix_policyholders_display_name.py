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
        print("Dropping NOT NULL constraint on display_name...")
        await conn.execute("ALTER TABLE policyholders ALTER COLUMN display_name DROP NOT NULL;")
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()
        
if __name__ == "__main__":
    asyncio.run(main())
