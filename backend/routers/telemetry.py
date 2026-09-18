"""
routers/telemetry.py — POST /telemetry
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.ids import new_ulid
from services.telemetry import ingest_telemetry
from schemas.telemetry import TelemetryIngestRequest, TelemetryIngestResponse

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post(
    "",
    response_model=TelemetryIngestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {"description": "Duplicate event — idempotently accepted"},
        400: {"description": "Invalid region or source"},
        422: {"description": "Validation error"},
    },
)
async def ingest_telemetry_endpoint(
    request: TelemetryIngestRequest,
    db: AsyncSession = Depends(get_db),
) -> TelemetryIngestResponse:
    """
    Ingest one rainfall telemetry observation.
    Returns 201 for new events, 200 for duplicates.
    """
    correlation_id = new_ulid()

    try:
        result = await ingest_telemetry(
            request=request,
            correlation_id=correlation_id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_TELEMETRY", "message": str(exc)},
        )

    # Return 200 for duplicates (idempotent success), 201 for new
    if result.status == "DUPLICATE":
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result.model_dump(mode="json"),
        )

    return result

