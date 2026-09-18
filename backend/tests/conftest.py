"""
tests/conftest.py — Test fixtures for PS-F03 backend integration tests.

Uses an in-memory SQLite database for speed and isolation.
Each test gets a fresh, clean database.

NOTE: SQLite is used for testing ONLY.
Production uses PostgreSQL (provisioned by Akshaya).
"""
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from models import Base
from seeds.seed_demo_data import seed

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use the default event loop policy."""
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    """
    Yields a fresh async DB session backed by in-memory SQLite.
    Creates all tables and seeds demo data for each test.
    Rolls back after the test.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        # Seed demo data
        await seed(session)
        await session.commit()

        yield session

        # Cleanup: drop all tables after test
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

