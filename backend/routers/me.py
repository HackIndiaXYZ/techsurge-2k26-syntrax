from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from database import get_db
from services.auth import get_current_policyholder
from models.policyholder import Policyholder
from models.policy import Policy

router = APIRouter(prefix="/me", tags=["Identity"])

@router.get("")
async def get_my_identity(
    policyholder: Policyholder = Depends(get_current_policyholder),
    db: AsyncSession = Depends(get_db)
):
    # Fetch policies and wallet
    ph = await db.scalar(
        select(Policyholder)
        .where(Policyholder.id == policyholder.id)
        .options(
            selectinload(Policyholder.policies),
            selectinload(Policyholder.wallet)
        )
    )
    
    policies = ph.policies if ph else []
    
    return {
        "policyholder_id": str(ph.id) if ph else str(policyholder.id),
        "display_name": ph.display_name if ph else policyholder.display_name,
        "phone_number": ph.phone_number if ph else policyholder.phone_number,
        "phone_verified": ph.phone_verified if ph else policyholder.phone_verified,
        "wallet_id": str(ph.wallet.id) if ph and ph.wallet else None,
        "policies": [
            {
                "policy_id": str(p.id)
            }
            for p in policies
        ]
    }
