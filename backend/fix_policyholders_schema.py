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
        print("Adding missing columns to policyholders table...")
        
        # Check if auth_user_id exists
        cols = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name = 'policyholders'")
        col_names = [c['column_name'] for c in cols]
        
        if 'auth_user_id' not in col_names:
            print("Adding auth_user_id...")
            await conn.execute("ALTER TABLE policyholders ADD COLUMN auth_user_id UUID")
            await conn.execute("ALTER TABLE policyholders ADD CONSTRAINT uq_policyholder_auth_user UNIQUE (auth_user_id)")
        
        if 'phone_number' not in col_names:
            print("Adding phone_number...")
            await conn.execute("ALTER TABLE policyholders ADD COLUMN phone_number TEXT")
            
        if 'phone_verified' not in col_names:
            print("Adding phone_verified...")
            await conn.execute("ALTER TABLE policyholders ADD COLUMN phone_verified BOOLEAN NOT NULL DEFAULT false")
            
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()
        
if __name__ == "__main__":
    asyncio.run(main())
