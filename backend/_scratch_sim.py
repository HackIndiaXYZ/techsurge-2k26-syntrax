import asyncio
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from models import Base
from seeds.seed_demo_data import seed
from services.simulation import run_simulation
from schemas.simulation import SimulationRequest, ObservationInput
from seeds.seed_demo_data import POLICY_ID, REGION_ID, SOURCE_IDS

async def run_e2e_sim():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with session_factory() as db:
        await seed(db)
        await db.commit()
        
        request = SimulationRequest(
            scenario="NORMAL",
            policy_id=str(POLICY_ID),
            region_id=str(REGION_ID),
            observations=[
                ObservationInput(source_id=str(SOURCE_IDS[0]), value=110.0),
                ObservationInput(source_id=str(SOURCE_IDS[1]), value=108.0),
                ObservationInput(source_id=str(SOURCE_IDS[2]), value=111.0),
            ],
            observed_at=datetime(2026, 9, 18, 11, 0, 0, tzinfo=timezone.utc),
        )
        
        response = await run_simulation(request=request, db=db)
        with open("sim_output.json", "w", encoding="utf-8") as f:
            f.write(response.model_dump_json(indent=2))
        print("SIMULATION RESULT written to sim_output.json")

if __name__ == "__main__":
    asyncio.run(run_e2e_sim())
