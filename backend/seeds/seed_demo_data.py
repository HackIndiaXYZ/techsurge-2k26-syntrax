"""
seeds/seed_demo_data.py — Demo data seeder for PS-F03.

Creates the fixed demo fixtures required for the four hackathon scenarios:
  - 1 MicroRegion: Kaveri Delta
  - 3 WeatherSources: source-a, source-b, source-c
  - 1 Policy: policy-kaveri-2026
  - 1 TriggerRule: rainfall >= 100 mm / 60 min
  - 1 Wallet: wallet-kaveri-2026 (starting balance: 0 paise)

Safe to run multiple times — uses INSERT ... ON CONFLICT DO NOTHING pattern.

DO NOT seed real credentials, real API keys, or real account data.
"""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from models.region import MicroRegion
from models.source import WeatherSource
from models.policy import Policy, PolicyStatus, TriggerRule
from models.wallet import Wallet


import uuid

REGION_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
POLICY_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
WALLET_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")

SOURCE_IDS = [
    uuid.UUID("00000000-0000-0000-0000-000000000010"),
    uuid.UUID("00000000-0000-0000-0000-000000000011"),
    uuid.UUID("00000000-0000-0000-0000-000000000012"),
]
SOURCE_NAMES = {
    uuid.UUID("00000000-0000-0000-0000-000000000010"): "Kaveri Delta Station Alpha",
    uuid.UUID("00000000-0000-0000-0000-000000000011"): "Kaveri Delta Station Beta",
    uuid.UUID("00000000-0000-0000-0000-000000000012"): "Kaveri Delta Station Gamma",
}

PAYOUT_PAISE = 1_000_000   # ₹10,000 — integer only


async def seed(db: AsyncSession) -> None:
    """
    Idempotent seed function.
    Inserts demo fixtures if they don't already exist.
    Uses ON CONFLICT DO NOTHING for PostgreSQL.
    For SQLite (testing), uses get() + conditional add.
    """
    import logging
    logger = logging.getLogger(__name__)

    # ── MicroRegion ──────────────────────────────────────────────────────────
    existing_region = await db.get(MicroRegion, REGION_ID)
    if not existing_region:
        db.add(MicroRegion(
            id=REGION_ID,
            code="KAVERI-001",
            name="Kaveri Delta",
        ))
        await db.flush()
        logger.info(f"Seeded MicroRegion: {REGION_ID}")

    # ── WeatherSources ───────────────────────────────────────────────────────
    for sid in SOURCE_IDS:
        existing_src = await db.get(WeatherSource, sid)
        if not existing_src:
            db.add(WeatherSource(
                id=sid,
                code=SOURCE_NAMES[sid],
                enabled=True,
            ))
    await db.flush()
    logger.info(f"Seeded WeatherSources: {SOURCE_IDS}")

    # ── Policy ───────────────────────────────────────────────────────────────
    existing_policy = await db.get(Policy, POLICY_ID)
    if not existing_policy:
        db.add(Policy(
            id=POLICY_ID,
            region_id=REGION_ID,
            name="Kaveri Delta Flood Parametric Insurance 2026",
            status=PolicyStatus.ACTIVE,
            payout_amount_paise=PAYOUT_PAISE,   # 1,000,000 paise = ₹10,000 — integer
            currency="INR",
            valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
            valid_until=datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        ))
        await db.flush()
        logger.info(f"Seeded Policy: {POLICY_ID}")

        # ── TriggerRule ──────────────────────────────────────────────────────
        from services.ids import new_ulid
        db.add(TriggerRule(
            id=uuid.UUID("00000000-0000-0000-0000-000000000004"),
            policy_id=POLICY_ID,
            metric="rainfall",
            threshold_value=100.0,
            threshold_operator=">=",
            unit="mm",
            observation_window_minutes=60,
            consensus_quorum=2,
            consensus_tolerance=5.0,
        ))
        await db.flush()
        logger.info(f"Seeded TriggerRule for policy: {POLICY_ID}")

    # ── Wallet ───────────────────────────────────────────────────────────────
    existing_wallet = await db.get(Wallet, WALLET_ID)
    if not existing_wallet:
        db.add(Wallet(
            id=WALLET_ID,
            policy_id=POLICY_ID,
            currency="INR",
            balance_paise=0,    # Starting balance: 0 paise — integer
        ))
        await db.flush()
        logger.info(f"Seeded Wallet: {WALLET_ID} (balance: 0 paise)")

    logger.info("Demo seed complete.")


async def reset_wallet_balance(db: AsyncSession) -> None:
    """
    Reset wallet balance to 0 for a fresh demo run.
    Does NOT delete audit trail or payout history.
    Use only for local development reset.
    """
    wallet = await db.get(Wallet, WALLET_ID)
    if wallet:
        wallet.balance_paise = 0
        await db.flush()

