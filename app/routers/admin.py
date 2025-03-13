from fastapi import APIRouter, HTTPException, Depends
from app.services.redis_client import redis_async as redis
from app.utils.authentication import get_current_admin_user
from app.models import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/set-ttl")
async def set_custom_ttl(resource_id: str, ttl_minutes: int, current_user: User = Depends(get_current_admin_user)):
    try:
        # Update expiry time in Redis Stream
        expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
        await redis.xadd("resource_stream", {"id": resource_id, "expires_at": expires_at.timestamp()})
        return {"message": f"TTL updated to {ttl_minutes} minutes"}
    except Exception as e:
        raise HTTPException(500, str(e))