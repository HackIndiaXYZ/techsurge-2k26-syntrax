import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def fix_one(cmd, description):
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text(cmd))
            await session.commit()
            print(f"OK: {description}")
        except Exception as e:
            print(f"SKIP: {description} -> {type(e).__name__}")

async def run():
    # Step 1: Drop old FK constraint on wallets
    await fix_one(
        "ALTER TABLE wallets DROP CONSTRAINT IF EXISTS fk_wallet_policyholder",
        "Drop fk_wallet_policyholder"
    )

    # Step 2: Drop any other FK on policy_id
    await fix_one(
        "ALTER TABLE wallets DROP CONSTRAINT IF EXISTS wallets_policy_id_fkey",
        "Drop wallets_policy_id_fkey"
    )

    # Step 3: Add new FK pointing to policies
    await fix_one(
        "ALTER TABLE wallets ADD CONSTRAINT fk_wallet_policy "
        "FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE RESTRICT",
        "Add fk_wallet_policy"
    )

    # Step 4: Fix wallet data
    await fix_one(
        "UPDATE wallets SET policy_id = 'e5000000-0000-0000-0000-000000000001' "
        "WHERE id = 'f6000000-0000-0000-0000-000000000001'",
        "Fix wallet policy_id"
    )

    # Step 5: Update weather source codes
    await fix_one(
        "UPDATE weather_sources SET code = 'open-meteo', kind = 'API' "
        "WHERE id = 'c3000000-0000-0000-0000-000000000001'",
        "Set source 1 = open-meteo"
    )
    await fix_one(
        "UPDATE weather_sources SET code = 'accuweather', kind = 'API' "
        "WHERE id = 'c3000000-0000-0000-0000-000000000002'",
        "Set source 2 = accuweather"
    )
    await fix_one(
        "UPDATE weather_sources SET code = 'imd', kind = 'API' "
        "WHERE id = 'c3000000-0000-0000-0000-000000000003'",
        "Set source 3 = imd"
    )

    print("\nAll fixes applied!")

asyncio.run(run())
