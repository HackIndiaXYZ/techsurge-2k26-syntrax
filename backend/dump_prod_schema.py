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
        print("--- TABLE SCHEMAS ---")
        tables_query = """
            SELECT table_name, column_name, is_nullable, data_type, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """
        columns = await conn.fetch(tables_query)
        current_table = None
        for col in columns:
            if col['table_name'] != current_table:
                current_table = col['table_name']
                print(f"\nTABLE: {current_table}")
            default_str = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}){default_str}")

        print("\n--- CONSTRAINTS ---")
        constraints_query = """
            SELECT 
                tc.table_name, 
                tc.constraint_name, 
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            WHERE tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_type;
        """
        constraints = await conn.fetch(constraints_query)
        for c in constraints:
            print(f"  {c['table_name']}.{c['column_name']} -> {c['constraint_name']} ({c['constraint_type']})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()
        
if __name__ == "__main__":
    asyncio.run(main())
