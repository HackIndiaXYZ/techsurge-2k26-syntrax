import logging
from sqlalchemy.ext.asyncio import AsyncSession
from models.policy import Policy
from services.consensus import run_consensus, SourceObservation
from services.trigger import evaluate_trigger
from services.settlement import settle_payout

logger = logging.getLogger(__name__)

async def process_weather_event(
    observations: list[SourceObservation],
    policy: Policy,
    region_id: str,
    correlation_id: str,
    db: AsyncSession
):
    """
    Core backend orchestration path:
    consensus -> trigger -> settlement -> wallet -> notification.
    """
    logger.info(f"Orchestrating weather event for policy {policy.id} with {len(observations)} observations.")
    
    # 1. Consensus
    consensus_record = await run_consensus(
        observations=observations,
        policy_id=policy.id,
        region_id=region_id,
        correlation_id=correlation_id,
        db=db
    )

    # 2. Trigger Evaluation
    trigger_record = await evaluate_trigger(
        consensus_result=consensus_record,
        policy=policy,
        correlation_id=correlation_id,
        db=db
    )

    # 3. Settlement -> Wallet -> Notification
    ts = trigger_record.trigger_status
    if ts == "TRIGGERED":
        payout, idempotency_status = await settle_payout(
            trigger_evaluation=trigger_record,
            policy=policy,
            correlation_id=correlation_id,
            db=db
        )
        return consensus_record, trigger_record, payout, idempotency_status

    return consensus_record, trigger_record, None, "SKIPPED"
