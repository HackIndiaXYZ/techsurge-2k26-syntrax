from fastapi import APIRouter
from typing import List, Dict, Any
import time

from config import get_settings
from services.polling import registry

router = APIRouter(prefix="/weather", tags=["Weather"])
settings = get_settings()

@router.get("/sources", response_model=List[Dict[str, Any]])
async def get_weather_sources():
    """Get the current health and status of all configured weather providers."""
    providers = registry._providers
    results = []
    for p in providers:
        start_time = time.monotonic()
        is_healthy = await p.health_check()
        latency_ms = int((time.monotonic() - start_time) * 1000)
        
        results.append({
            "name": p.name,
            "status": "ONLINE" if is_healthy else "OFFLINE",
            "latency_ms": latency_ms
        })
    return results

@router.post("/poll")
async def trigger_poll():
    """Manually trigger a weather poll."""
    from services.polling import poll_weather_once
    await poll_weather_once()
    return {"status": "success", "message": "Poll triggered successfully"}

