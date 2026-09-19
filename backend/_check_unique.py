import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as session:
        # Check constraints on telemetry_events
        r = await session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'telemetry_events'::regclass
        """))
        print("telemetry_events constraints:")
        for row in r.fetchall():
            print(f"  {row[0]} ({row[1]}): {row[2]}")

        # Check existing telemetry events count
        r = await session.execute(text("SELECT COUNT(*) FROM telemetry_events"))
        print(f"\nTotal telemetry events: {r.scalar()}")

        # Check for duplicates in source_event_id
        r = await session.execute(text("""
            SELECT source_event_id, COUNT(*)
            FROM telemetry_events
            GROUP BY source_event_id
            HAVING COUNT(*) > 1
            LIMIT 5
        """))
        dups = r.fetchall()
        if dups:
            print(f"\nDuplicate source_event_ids: {dups}")
        else:
            print("\nNo duplicate source_event_ids")

asyncio.run(run())
