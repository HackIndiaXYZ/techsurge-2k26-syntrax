"""
services/telemetry.py — Telemetry ingestion, validation, and deduplication.

Uses DB column names: source_event_id, value, validation_state
"""
import uuid as uuid_mod
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.telemetry import TelemetryEvent
from models.region import MicroRegion
from models.source import WeatherSource
from models.audit import AuditEventType
from schemas.telemetry import TelemetryIngestRequest, TelemetryIngestResponse
from services.audit import write_audit_event
from services.ids import new_uuid


async def ingest_telemetry(
    request: TelemetryIngestRequest,
    correlation_id: str,
    db: AsyncSession,
) -> TelemetryIngestResponse:
    """Ingest one telemetry observation."""
    received_at = datetime.now(timezone.utc)

    # Convert string IDs to UUID
    try:
        region_uuid = uuid_mod.UUID(str(request.region_id))
    except ValueError:
        raise ValueError(f"Invalid region_id format: {request.region_id!r}")
    try:
        source_uuid = uuid_mod.UUID(str(request.source_id))
    except ValueError:
        raise ValueError(f"Invalid source_id format: {request.source_id!r}")

    # 1. Validate region exists
    region = await db.get(MicroRegion, region_uuid)
    if region is None:
        await write_audit_event(
            db=db,
            event_type=AuditEventType.TELEMETRY_REJECTED,
            entity_type="TELEMETRY",
            entity_id=str(new_uuid()),
            status="REJECTED",
            correlation_id=correlation_id,
            message=f"Unknown region_id: {request.region_id}",
            metadata={"event_id": request.event_id, "source_id": request.source_id},
        )
        raise ValueError(f"Unknown region_id: {request.region_id!r}")

    # 2. Validate source exists and is active
    source = await db.get(WeatherSource, source_uuid)
    if source is None or not source.is_active:
        await write_audit_event(
            db=db,
            event_type=AuditEventType.TELEMETRY_REJECTED,
            entity_type="TELEMETRY",
            entity_id=str(new_uuid()),
            status="REJECTED",
            correlation_id=correlation_id,
            message=f"Unknown or inactive source_id: {request.source_id}",
            metadata={"event_id": request.event_id},
        )
        raise ValueError(f"Unknown or inactive source_id: {request.source_id!r}")

    # 3. Check for duplicate (using source_event_id)
    existing = await db.scalar(
        select(TelemetryEvent).where(TelemetryEvent.source_event_id == request.event_id)
    )
    if existing is not None:
        return TelemetryIngestResponse(
            status="DUPLICATE",
            event_id=request.event_id,
            correlation_id=correlation_id,
            received_at=received_at,
            message="Event already ingested. Ignored.",
        )

    # 4. Persist the telemetry event
    event = TelemetryEvent(
        id=new_uuid(),
        source_event_id=request.event_id,
        source_id=source_uuid,
        region_id=region_uuid,
        metric=request.metric,
        value=request.value,
        unit=request.unit,
        observed_at=request.observed_at,
        window_start=request.observed_at,
        window_end=request.observed_at,
        received_at=received_at,
        validation_state="ACCEPTED",
    )

    try:
        async with db.begin_nested():
            db.add(event)
            await db.flush()
    except IntegrityError as exc:
        import logging
        logging.getLogger(__name__).warning(f"Telemetry INSERT IntegrityError: {exc}")
        return TelemetryIngestResponse(
            status="DUPLICATE",
            event_id=request.event_id,
            correlation_id=correlation_id,
            received_at=received_at,
            message="Source event already processed concurrently.",
        )

    await write_audit_event(
        db=db,
        event_type=AuditEventType.TELEMETRY_RECEIVED,
        entity_type="TELEMETRY",
        entity_id=str(event.id),
        status="ACCEPTED",
        correlation_id=correlation_id,
        metadata={"source_id": request.source_id, "value": request.value}
    )

    return TelemetryIngestResponse(
        status="ACCEPTED",
        event_id=request.event_id,
        correlation_id=correlation_id,
        received_at=received_at,
    )
