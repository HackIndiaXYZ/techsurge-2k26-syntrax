import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as session:
        r = await session.execute(text("""
            SELECT column_name, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_name = 'payouts'
        """))
        print("payouts columns:")
        for row in r.fetchall():
            print(f"  {row[0]}: nullable={row[1]}, type={row[2]}")

        r = await session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'payouts'::regclass
        """))
        print("\npayouts constraints:")
        for row in r.fetchall():
            print(f"  {row[0]} ({row[1]}): {row[2]}")

asyncio.run(run())
