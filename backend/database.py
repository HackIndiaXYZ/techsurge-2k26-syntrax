"""
database.py — Async SQLAlchemy engine and session factory.

Provides:
  - async_engine: SQLAlchemy async engine
  - AsyncSessionLocal: async session factory
  - get_db(): FastAPI dependency that yields a database session
  - create_all_tables(): utility to create tables (dev only; prod uses Alembic)
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import get_settings

settings = get_settings()

# ── Engine ───────────────────────────────────────────────────────────────────
# echo=False in production; set True locally for SQL debug.
async_engine = create_async_engine(
    settings.database_url,
    echo=(settings.environment == "development"),
    pool_pre_ping=True,         # detect stale connections
    pool_size=5,
    max_overflow=10,
)

# ── Session factory ──────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── FastAPI dependency ───────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency. Yields an async DB session and guarantees close.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Dev utility ──────────────────────────────────────────────────────────────
async def create_all_tables() -> None:
    """
    Create all tables based on SQLAlchemy metadata.
    For development/testing ONLY.
    Production schema is managed by Alembic (coordinated with Akshaya).
    """
    from models.base import Base  # local import to avoid circular deps

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def ping_db() -> bool:
    """Returns True if the database is reachable."""
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

