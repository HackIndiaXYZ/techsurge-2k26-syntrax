import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def fix_one(cmd):
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text(cmd))
            await session.commit()
            print(f"OK: {cmd}")
        except Exception as e:
            print(f"SKIP: {cmd} -> {type(e).__name__}: {e}")

async def run():
    fixes = [
        "ALTER TABLE wallets ALTER COLUMN status DROP DEFAULT",
        "ALTER TABLE wallets ALTER COLUMN status TYPE TEXT USING status::TEXT",
        "ALTER TABLE wallet_transactions ALTER COLUMN direction TYPE TEXT USING direction::TEXT",
        "ALTER TABLE telemetry_events ALTER COLUMN validation_state TYPE TEXT USING validation_state::TEXT",
        "ALTER TABLE trigger_rules ALTER COLUMN threshold_operator TYPE TEXT USING threshold_operator::TEXT",
    ]
    for cmd in fixes:
        await fix_one(cmd)
    print("Done!")

asyncio.run(run())
