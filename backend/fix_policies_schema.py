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
        print("Fixing policies table schema mismatches...")
        
        cols_to_drop_not_null = [
            "trigger_rule_id",
            "name",
            "currency",
            "valid_from",
            "valid_until",
            "updated_at",
            "start_at",
            "end_at"
        ]
        
        for col in cols_to_drop_not_null:
            try:
                await conn.execute(f"ALTER TABLE policies ALTER COLUMN {col} DROP NOT NULL;")
                print(f"Dropped NOT NULL from {col}")
            except Exception as e:
                print(f"Skipped {col} (may not exist or already nullable): {e}")
                
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()
        
if __name__ == "__main__":
    asyncio.run(main())
