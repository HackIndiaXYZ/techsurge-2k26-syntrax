import logging
import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from models.ai_assistance import AIAssistanceHandoff, AIAssistanceStatus
from models.voice_call import VoiceCallJob, VoiceCallStatus
from models.policyholder import Policyholder
from models.policy import Policy, TriggerRule
from models.payout import Payout
from models.trigger import TriggerEvaluation
from models.consensus import ConsensusResult
from models.notification import Notification

from ai.schemas import VoiceCallRequest, ExplanationLanguage
from ai.voice import execute_voice_assistance

logger = logging.getLogger(__name__)

async def process_handoffs_to_jobs(db: AsyncSession) -> int:
    """
    Step 1: Converts PENDING AIAssistanceHandoffs into VoiceCallJobs.
    Ensures that only users with a verified phone number get a PENDING job.
    Otherwise, marks it BLOCKED.
    """
    stmt = (
        select(AIAssistanceHandoff)
        .options(selectinload(AIAssistanceHandoff.policyholder))
        .where(AIAssistanceHandoff.status == AIAssistanceStatus.PENDING.value)
        .with_for_update(skip_locked=True)
    )
    result = await db.execute(stmt)
    handoffs = result.scalars().all()

    processed = 0
    for handoff in handoffs:
        ph = handoff.policyholder
        
        # Check verified phone
        if not ph.phone_verified or not ph.phone_number:
            job_status = VoiceCallStatus.BLOCKED.value
            phone = "UNAVAILABLE"
            last_err = "Policyholder missing verified phone number."
        else:
            job_status = VoiceCallStatus.PENDING.value
            phone = ph.phone_number
            last_err = None

        job = VoiceCallJob(
            handoff_id=handoff.id,
            policyholder_id=ph.id,
            phone_number=phone,
            status=job_status,
            last_error=last_err
        )
        db.add(job)
        handoff.status = AIAssistanceStatus.PROCESSED.value
        processed += 1

    return processed


async def process_pending_voice_jobs(db: AsyncSession) -> int:
    """
    Step 2: Picks up PENDING/RETRY_PENDING VoiceCallJobs and executes them via the voice layer.
    """
    stmt = (
        select(VoiceCallJob)
        .options(
            selectinload(VoiceCallJob.handoff).selectinload(AIAssistanceHandoff.notification),
            selectinload(VoiceCallJob.handoff).selectinload(AIAssistanceHandoff.policy),
            selectinload(VoiceCallJob.handoff).selectinload(AIAssistanceHandoff.payout)
        )
        .where(VoiceCallJob.status.in_([VoiceCallStatus.PENDING.value, VoiceCallStatus.RETRY_PENDING.value]))
        .with_for_update(skip_locked=True)
    )
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    processed = 0
    for job in jobs:
        # Atomic claim
        job.status = VoiceCallStatus.CLAIMED.value
        job.attempt_count += 1
        await db.flush()

        try:
            # 1. Fetch deterministic context
            handoff = job.handoff
            policy = handoff.policy
            payout = handoff.payout
            notification = handoff.notification
            
            # Fetch rule for threshold
            rule_res = await db.execute(
                select(TriggerRule).where(TriggerRule.policy_id == policy.id)
            )
            rule = rule_res.scalar_one_or_none()
            if not rule:
                raise ValueError(f"No TriggerRule found for policy {policy.id}")
                
            # Fetch trigger eval for consensus context
            eval_res = await db.execute(
                select(TriggerEvaluation).where(TriggerEvaluation.policy_id == policy.id).order_by(TriggerEvaluation.evaluated_at.desc())
            )
            evaluation = eval_res.scalars().first()
            if not evaluation:
                raise ValueError(f"No TriggerEvaluation found for policy {policy.id}")
                
            # Fetch consensus
            consensus_res = await db.execute(
                select(ConsensusResult).where(ConsensusResult.id == evaluation.consensus_result_id)
            )
            consensus = consensus_res.scalar_one_or_none()
            if not consensus or consensus.consensus_value_mm is None:
                raise ValueError(f"Valid ConsensusResult not found for evaluation {evaluation.id}")

            # 2. Build Request
            # (Note: we map Notification language to ExplanationLanguage later, default to EN for now)
            req = VoiceCallRequest(
                event_id=str(notification.id), # Use notification ID as unique event context
                settlement_id=str(payout.id),
                language=ExplanationLanguage.EN,
                phone_number=job.phone_number,
                settlement_amount_paise=payout.amount_paise,
                consensus_value=float(consensus.consensus_value_mm),
                threshold_value=float(rule.threshold_value),
                acknowledgement_status=notification.status
            )
            
            job.call_script_metadata = req.model_dump(mode='json')
            job.status = VoiceCallStatus.REQUESTED.value
            await db.flush()
            
            # 3. Call Voice Provider
            # We don't block the DB transaction completely on this network call if we can avoid it,
            # but for MVP synchronous execution is okay given short timeouts.
            result = execute_voice_assistance(req)
            
            if result.provider_call_id:
                job.provider_call_id = result.provider_call_id
                
            if result.status == "FAILED":
                # Handle retry logic
                if job.attempt_count >= 3:
                    job.status = VoiceCallStatus.FAILED_FINAL.value
                else:
                    job.status = VoiceCallStatus.RETRY_PENDING.value
                job.last_error = f"{result.error_code}: {result.error_message}"
            else:
                job.status = VoiceCallStatus.CALLING.value # Or INITIATED
                
        except Exception as e:
            logger.exception(f"Error processing voice call job {job.id}")
            if job.attempt_count >= 3:
                job.status = VoiceCallStatus.FAILED_FINAL.value
            else:
                job.status = VoiceCallStatus.RETRY_PENDING.value
            job.last_error = str(e)
            
        processed += 1

    return processed
