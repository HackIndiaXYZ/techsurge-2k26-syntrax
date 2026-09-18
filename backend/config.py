"""
config.py — Application configuration for PS-F03 backend.

Reads settings from environment variables (.env file or system environment).
Uses pydantic-settings for type-safe configuration.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://postgres:changeme@localhost:5432/syntrax_ps_f03"
    )

    # ── Server ──────────────────────────────────────────────────────────────
    port: int = 8000
    environment: str = "development"

    # ── CORS ────────────────────────────────────────────────────────────────
    allowed_origins: List[str] = ["http://localhost:3000"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # ── Internal / Dev auth ─────────────────────────────────────────────────
    # TBD: Replace with real auth before production.
    internal_api_key: str = "changeme-dev-only"

    # ── Demo seeding ────────────────────────────────────────────────────────
    seed_on_startup: bool = False

    # ── Business rules (hardcoded for PS-F03; read-only) ───────────────────
    # These are frozen demo values and are NOT configurable in production.
    # They are exposed here only for testing convenience.
    RAINFALL_THRESHOLD_MM: float = 100.0
    OBSERVATION_WINDOW_MINUTES: int = 60
    CONSENSUS_TOLERANCE_MM: float = 5.0
    CONSENSUS_QUORUM: int = 2
    DEMO_PAYOUT_PAISE: int = 1_000_000   # ₹10,000 in paise (integer)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()

