import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as session:
        # First check actual columns
        r0 = await session.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = 'micro_regions' ORDER BY ordinal_position"
        ))
        print("=== micro_regions schema ===")
        for row in r0:
            print(f"  {row[0]}: {row[1]}")

        r = await session.execute(text("SELECT id, code, kind, enabled FROM weather_sources"))
        print("\n=== weather_sources data ===")
        for row in r:
            print(f"  id={row[0]}, code={row[1]!r}, kind={row[2]!r}, enabled={row[3]}")

        r2 = await session.execute(text("SELECT id, name, status, payout_amount_paise, region_id FROM policies"))
        print("\n=== policies data ===")
        for row in r2:
            print(f"  id={row[0]}, name={row[1]!r}, status={row[2]!r}, payout={row[3]}, region={row[4]}")

        r3 = await session.execute(text("SELECT * FROM micro_regions"))
        cols = r3.keys()
        print(f"\n=== micro_regions data (cols: {list(cols)}) ===")
        for row in r3:
            print(f"  {dict(row._mapping)}")

        r4 = await session.execute(text("SELECT id, metric, threshold_operator, threshold_value, policy_id FROM trigger_rules"))
        print("\n=== trigger_rules data ===")
        for row in r4:
            print(f"  id={row[0]}, metric={row[1]!r}, op={row[2]!r}, threshold={row[3]}, policy={row[4]}")

        r5 = await session.execute(text("SELECT id, policy_id, balance_paise FROM wallets"))
        print("\n=== wallets data ===")
        for row in r5:
            print(f"  id={row[0]}, policy_id={row[1]}, balance={row[2]}")

asyncio.run(run())
