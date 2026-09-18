"""
routers/simulations.py — POST /simulations

The primary demo endpoint. Runs the complete PS-F03 pipeline.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.simulation import run_simulation
from schemas.simulation import SimulationRequest, SimulationResponse

router = APIRouter(prefix="/simulations", tags=["Simulations"])


@router.post(
    "",
    response_model=SimulationResponse,
    responses={
        400: {"description": "Invalid policy or region"},
        422: {"description": "Validation error"},
        500: {"description": "Internal error"},
    },
)
async def run_simulation_endpoint(
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db),
) -> SimulationResponse:
    """
    Run a complete PS-F03 pipeline simulation.

    Exercises: ingestion → validation → deduplication → consensus →
               trigger → settlement → wallet → audit.

    Returns a complete structured result including all pipeline stages.
    """
    try:
        return await run_simulation(request=request, db=db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "SIMULATION_ERROR", "message": str(exc)},
        )

