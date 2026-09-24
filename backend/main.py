"""
main.py — FastAPI application entry point for PS-F03 backend.

Registers all routers and configures CORS, lifespan, and exception handlers.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from routers import health, telemetry, simulations, policies, payouts, wallets, audit, me

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup/shutdown lifecycle.

    Startup:
    - Optionally create DB tables (dev only; production uses Alembic).
    - Optionally seed demo data.
    """
    logger.info("SYNTRAX PS-F03 backend starting up...")
    logger.info(f"Environment: {settings.environment}")

    if settings.environment == "development":
        # In development, create tables if they don't exist.
        # In production, Alembic handles schema — never call create_all in prod.
        try:
            from database import create_all_tables
            await create_all_tables()
            logger.info("DB tables verified/created.")
        except Exception as exc:
            logger.warning(f"DB table creation skipped (DB may not be available): {exc}")

    if settings.seed_on_startup:
        try:
            from seeds.seed_demo_data import seed
            from database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                await seed(session)
                await session.commit()
            logger.info("Demo seed data loaded.")
        except Exception as exc:
            logger.warning(f"Seeding skipped: {exc}")

    from services.polling import start_polling, stop_polling
    start_polling()

    yield

    stop_polling()
    logger.info("SYNTRAX PS-F03 backend shutting down.")



# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="SYNTRAX PS-F03 Backend",
    description=(
        "Autonomous Parametric Climate Insurance & Instant Settlement Engine. "
        "HACKATHON PROTOTYPE — no real money, no real payments."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = list(settings.allowed_origins)
if "https://terrafluxapp.xyz" in origins and "https://www.terrafluxapp.xyz" not in origins:
    origins.append("https://www.terrafluxapp.xyz")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please check server logs.",
            "details": {},
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(telemetry.router)
app.include_router(simulations.router)
app.include_router(policies.router)
app.include_router(payouts.router)
app.include_router(wallets.router)
app.include_router(audit.router)
app.include_router(me.router)

from routers import weather
app.include_router(weather.router)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai.router import router as ai_router
app.include_router(ai_router)
logger.info("AI router mounted successfully.")

# ── Dev entrypoint ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=(settings.environment == "development"),
        log_level="info",
    )

