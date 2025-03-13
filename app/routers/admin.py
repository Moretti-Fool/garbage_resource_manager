from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.services.redis_client import redis_async as redis
from app.utils.authentication import get_current_admin_user
from app.models import User, AuditLog
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
async def admin_dashboard(
    current_admin: User  = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):  
    try:
        audit_log = AuditLog(
            event="ADMIN_DASHBOARD_ACCESS",
            user_id=current_admin.id,
            details=f"Admin {current_admin.email} accessed dashboard"
        )
        db.add(audit_log)
        await db.commit()
        return {"message": f"Welcome Admin {current_admin.email}!"}
    except Exception as e:
        await db.rollback()  # Prevents partial commits on failure
        raise HTTPException(500, str(e))


@router.get("/auditlog")
async def get_audit_log(
    current_admin: User  = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):

    try:
        audit_logs = await db.execute(select(AuditLog))
        audit_log = audit_logs.scalars().all() 
        audit_log_entry = AuditLog(
            event="ADMIN_VIEWED_AUDIT_LOG",
            user_id=current_admin.id,
            details=f"ADMIN {current_admin.email} VIEWED AUDIT_LOG"
        )
        db.add(audit_log_entry)
        await db.commit()
        return audit_log
    except Exception as e:
        await db.rollback()  # Prevents partial commits on failure
        raise HTTPException(500, str(e))



@router.post("/set-ttl")
async def set_custom_ttl(resource_id: str, 
                        ttl_minutes: int,
                        db: AsyncSession = Depends(get_db), 
                        current_admin: User = Depends(get_current_admin_user)):
    try:
        # Update expiry time in Redis Stream
        expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
        await redis.xadd("resource_stream", {"id": resource_id, "expires_at": expires_at.timestamp()})
        audit_log_entry = AuditLog(
            event="SET CUSTOM TTL",
            user_id=current_admin.id,
            details=f"ADMIN {current_admin.email} CHANGED TLL OF {resource_id} TO {ttl_minutes}"
        )
        db.add(audit_log_entry)
        await db.commit()
        return {"message": f"TTL updated to {ttl_minutes} minutes"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))

