"""
services/telemetry.py — Telemetry ingestion, validation, and deduplication.

Responsibilities:
1. Validate a TelemetryIngestRequest (metric/unit/value/region/source)
2. Check deduplication (event_id uniqueness via DB constraint)
3. Persist valid TelemetryEvent
4. Write audit records
5. Return result with status ACCEPTED or DUPLICATE
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.telemetry import TelemetryEvent
from models.region import MicroRegion
from models.source import WeatherSource
from models.audit import AuditEvent, AuditEventType
from schemas.telemetry import TelemetryIngestRequest, TelemetryIngestResponse
from services.audit import write_audit_event
from services.ids import new_ulid


async def ingest_telemetry(
    request: TelemetryIngestRequest,
    correlation_id: str,
    db: AsyncSession,
) -> TelemetryIngestResponse:
    """
    Ingest one telemetry observation.

    Returns:
      TelemetryIngestResponse with status "ACCEPTED" or "DUPLICATE".

    Raises:
      ValueError: if region or source is invalid/unknown.
    """
    received_at = datetime.now(timezone.utc)

    # ── 1. Validate region exists ────────────────────────────────────────────
    region = await db.get(MicroRegion, request.region_id)
    if region is None:
        await write_audit_event(
            db=db,
            event_type=AuditEventType.TELEMETRY_REJECTED,
            entity_type="TELEMETRY",
            entity_id=request.event_id,
            policy_id=None,
            correlation_id=correlation_id,
            status="REJECTED",
            message=f"Unknown region_id: {request.region_id}",
            metadata={"event_id": request.event_id, "source_id": request.source_id},
        )
        raise ValueError(f"Unknown region_id: {request.region_id!r}")

    # ── 2. Validate source exists and is active ──────────────────────────────
    source = await db.get(WeatherSource, request.source_id)
    if source is None or not source.is_active:
        await write_audit_event(
            db=db,
            event_type=AuditEventType.TELEMETRY_REJECTED,
            entity_type="TELEMETRY",
            entity_id=request.event_id,
            policy_id=None,
            correlation_id=correlation_id,
            status="REJECTED",
            message=f"Unknown or inactive source_id: {request.source_id}",
            metadata={"event_id": request.event_id},
        )
        raise ValueError(f"Unknown or inactive source_id: {request.source_id!r}")

    # ── 3. Check for duplicate event_id (fast path before INSERT) ───────────
    existing = await db.scalar(
        select(TelemetryEvent).where(TelemetryEvent.event_id == request.event_id)
    )
    if existing is not None:
        await write_audit_event(
            db=db,
            event_type=AuditEventType.TELEMETRY_DUPLICATE,
            entity_type="TELEMETRY",
            entity_id=request.event_id,
            policy_id=None,
            correlation_id=correlation_id,
            status="DUPLICATE",
            message="Duplicate event_id — already ingested.",
            metadata={"event_id": request.event_id, "source_id": request.source_id},
        )
        return TelemetryIngestResponse(
            status="DUPLICATE",
            event_id=request.event_id,
            correlation_id=correlation_id,
            received_at=received_at,
            message="Event already ingested. Ignored.",
        )

    # ── 4. Persist the telemetry event ───────────────────────────────────────
    event = TelemetryEvent(
        id=new_ulid(),
        event_id=request.event_id,
        source_id=request.source_id,
        region_id=request.region_id,
        metric=request.metric,
        value_mm=request.value,
        unit=request.unit,
        observed_at=request.observed_at,
        received_at=received_at,
        is_valid=True,
        rejection_reason=None,
    )

    try:
        async with db.begin_nested():
            db.add(event)
            await db.flush()  # flush to catch DB-level constraint violations
    except IntegrityError:
        # Race condition: another concurrent request inserted same event_id (savepoint automatically rolled back)
        await write_audit_event(
            db=db,
            event_type=AuditEventType.TELEMETRY_DUPLICATE,
            entity_type="TELEMETRY",
            entity_id=request.event_id,
            policy_id=None,
            correlation_id=correlation_id,
            status="DUPLICATE",
            message="Concurrent duplicate event_id detected via DB constraint.",
            metadata={"event_id": request.event_id},
        )
        return TelemetryIngestResponse(
            status="DUPLICATE",
            event_id=request.event_id,
            correlation_id=correlation_id,
            received_at=received_at,
            message="Event already ingested (concurrent). Ignored.",
        )

    # ── 5. Write audit event ─────────────────────────────────────────────────
    await write_audit_event(
        db=db,
        event_type=AuditEventType.TELEMETRY_RECEIVED,
        entity_type="TELEMETRY",
        entity_id=request.event_id,
        policy_id=None,
        correlation_id=correlation_id,
        status="ACCEPTED",
        message=f"Telemetry accepted: {request.value} mm from {request.source_id}",
        metadata={
            "event_id": request.event_id,
            "source_id": request.source_id,
            "value_mm": request.value,
            "observed_at": request.observed_at.isoformat(),
        },
    )

    return TelemetryIngestResponse(
        status="ACCEPTED",
        event_id=request.event_id,
        correlation_id=correlation_id,
        received_at=received_at,
    )

