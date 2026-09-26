"""
routers/simulations.py — POST /simulations

The primary demo endpoint. Runs the complete PS-F03 pipeline.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.simulation import run_simulation
from schemas.simulation import SimulationRequest, SimulationResponse
from services.auth import get_current_policyholder
from models.policyholder import Policyholder
from models.policy import Policy
from sqlalchemy import select
import uuid as _uuid

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
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> SimulationResponse:
    """
    Run a complete PS-F03 pipeline simulation.

    Exercises: ingestion → validation → deduplication → consensus →
               trigger → settlement → wallet → audit.

    Returns a complete structured result including all pipeline stages.
    """
    try:
        pid = _uuid.UUID(request.policy_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_ID", "message": f"Invalid policy_id: {request.policy_id!r}"},
        )
        
    policy = await db.get(Policy, pid)
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Policy {request.policy_id!r} not found."},
        )
        
    if policy.policyholder_id != policyholder.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this policy")
        
    try:
        return await run_simulation(request=request, db=db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "SIMULATION_ERROR", "message": str(exc)},
        )

