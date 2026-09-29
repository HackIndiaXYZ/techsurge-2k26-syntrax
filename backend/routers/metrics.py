from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from database import get_db

router = APIRouter(prefix="/metrics", tags=["Research Instrumentation"])

@router.get("")
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """
    Research-grade instrumentation endpoint to measure TerraFlux behavior.
    """
    # 1. Total Policies
    total_policies = await db.scalar(select(text("COUNT(id) FROM policies")))

    # 2. Total Payouts
    total_payouts = await db.scalar(select(text("COUNT(id) FROM payouts WHERE status = 'SUCCESS'")))
    
    # 3. Time savings: e2e settlement time vs traditional 14-day human adjuster
    # Measure average time between consensus window_end and payout completed_at
    avg_settlement_seconds = await db.scalar(
        select(text("AVG(EXTRACT(EPOCH FROM (p.completed_at - c.window_end))) "
                    "FROM payouts p "
                    "JOIN trigger_evaluations t ON p.trigger_evaluation_id = t.id "
                    "JOIN consensus_results c ON t.consensus_result_id = c.id "
                    "WHERE p.status = 'SUCCESS' AND p.completed_at IS NOT NULL"))
    )
    
    # 4. Total coverage disbursed
    total_disbursed = await db.scalar(
        select(text("SUM(amount_paise) FROM payouts WHERE status = 'SUCCESS'"))
    )
    
    # Traditional human adjuster latency in seconds (14 days)
    TRADITIONAL_LATENCY_SEC = 14 * 24 * 60 * 60
    
    if avg_settlement_seconds is not None:
        time_saved_seconds = TRADITIONAL_LATENCY_SEC - avg_settlement_seconds
    else:
        avg_settlement_seconds = 0
        time_saved_seconds = 0

    return {
        "total_policies": total_policies,
        "total_successful_payouts": total_payouts,
        "total_disbursed_paise": total_disbursed or 0,
        "avg_settlement_time_seconds": float(avg_settlement_seconds),
        "traditional_settlement_time_seconds": float(TRADITIONAL_LATENCY_SEC),
        "avg_time_saved_vs_traditional_seconds": float(time_saved_seconds),
        "acceleration_factor": float(TRADITIONAL_LATENCY_SEC / avg_settlement_seconds) if avg_settlement_seconds > 0 else 0
    }
