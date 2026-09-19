import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import AsyncSessionLocal
from config import get_settings
from models.policy import Policy
from models.source import WeatherSource
from providers.registry import ProviderRegistry
from providers.openmeteo import OpenMeteoProvider
from providers.accuweather import AccuWeatherProvider
from providers.imd import IMDProvider
from services.telemetry import ingest_telemetry
from services.consensus import run_consensus, SourceObservation
from services.trigger import evaluate_trigger
from services.settlement import settle_payout
from schemas.telemetry import TelemetryIngestRequest
from services.ids import new_ulid

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize provider registry
registry = ProviderRegistry()
registry.register(OpenMeteoProvider(base_url=settings.openmeteo_base_url, timeout_seconds=settings.provider_timeout_seconds))
registry.register(AccuWeatherProvider(api_key=settings.accuweather_api_key, base_url=settings.accuweather_base_url, timeout_seconds=settings.provider_timeout_seconds))
registry.register(IMDProvider(api_key=settings.imd_api_key, base_url=settings.imd_api_base_url, timeout_seconds=settings.provider_timeout_seconds))

_is_polling = False
_polling_task = None

async def poll_weather_once():
    """Polls all weather providers and pushes through the pipeline."""
    logger.info("Polling weather providers...")

    async with AsyncSessionLocal() as db:
        # Get active policy
        policy = await db.scalar(
            select(Policy)
            .where(Policy.status == "ACTIVE")
        )
        if not policy:
            logger.warning("No active policy found. Skipping poll.")
            return

        region_id = policy.region_id

        # Get ALL enabled sources (weather_sources has no region_id FK)
        sources = await db.scalars(
            select(WeatherSource).where(WeatherSource.enabled == True)
        )
        source_map = {}
        for s in sources:
            source_map[s.code.lower()] = s.id

        if not source_map:
            logger.warning("No active sources found. Skipping poll.")
            return

        # Fetch from providers
        lat = settings.default_latitude
        lon = settings.default_longitude

        results = await registry.fetch_all(lat, lon)

        correlation_id = new_ulid()
        accepted_observations = []

        for result in results:
            if result.success and result.observation:
                obs = result.observation
                source_name_lower = obs.source_name.lower()

                # Match provider name to DB source code
                db_source_id = source_map.get(source_name_lower)
                if not db_source_id:
                    # Try partial matching
                    for key, sid in source_map.items():
                        if source_name_lower in key or key in source_name_lower:
                            db_source_id = sid
                            break
                    if not db_source_id:
                        logger.warning(f"No DB source found for provider {obs.source_name}. Skipping.")
                        continue

                rainfall_mm = obs.rainfall_1h_mm or 0.0

                event_id = f"{correlation_id}-{db_source_id}"
                ingest_req = TelemetryIngestRequest(
                    event_id=event_id,
                    source_id=str(db_source_id),
                    region_id=str(region_id),
                    observed_at=obs.observed_at,
                    metric="rainfall",
                    value=rainfall_mm,
                    unit="mm"
                )

                try:
                    await ingest_telemetry(ingest_req, correlation_id, db)
                    accepted_observations.append(SourceObservation(
                        source_id=str(db_source_id), 
                        value_mm=rainfall_mm, 
                        observed_at=obs.observed_at
                    ))
                except Exception as e:
                    logger.error(f"Failed to ingest telemetry for {obs.source_name}: {e}")

        await db.commit()

        if not accepted_observations:
            logger.warning("No successful observations to process.")
            return

        # Run consensus and trigger
        async with db.begin():
            consensus_record = await run_consensus(
                observations=accepted_observations,
                policy_id=policy.id,
                region_id=region_id,
                correlation_id=correlation_id,
                db=db
            )

            trigger_record = await evaluate_trigger(
                consensus_result=consensus_record,
                policy=policy,
                correlation_id=correlation_id,
                db=db
            )

            ts = trigger_record.trigger_status
            if ts == "TRIGGERED":
                await settle_payout(
                    trigger_evaluation=trigger_record,
                    policy=policy,
                    correlation_id=correlation_id,
                    db=db
                )

        logger.info(f"Poll complete. Consensus: {consensus_record.status}, Trigger: {trigger_record.trigger_status}")

async def _polling_loop():
    global _is_polling
    _is_polling = True
    while _is_polling:
        try:
            await poll_weather_once()
        except Exception as e:
            logger.exception(f"Error in polling loop: {e}")

        await asyncio.sleep(settings.polling_interval_seconds)

def start_polling():
    global _polling_task
    if _polling_task is None:
        _polling_task = asyncio.create_task(_polling_loop())
        logger.info("Started background weather polling.")

def stop_polling():
    global _is_polling, _polling_task
    _is_polling = False
    if _polling_task:
        _polling_task.cancel()
        _polling_task = None
        logger.info("Stopped background weather polling.")
