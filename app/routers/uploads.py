from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.services.redis_client import redis_async as redis
from app.models import Resource, User, AuditLog
from app.database import get_db
from app.utils.authentication import get_current_user
import uuid

router = APIRouter(tags=["Upload"])

@router.post("/upload")
async def upload_file(
    file: UploadFile, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Generate unique resource ID
        resource_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=2)  #Use UTC time
        
        #Prepare data for batch commit
        resource = Resource(
            id=resource_id,
            filename=file.filename,
            expires_at=expires_at,
            user_id=current_user.id
        )

        audit_log = AuditLog(
            event="File Uploaded",
            user_id=current_user.id,
            details=f"User {current_user.id} uploaded file '{file.filename}'."
        )

        # Add both objects before committing
        db.add(resource)
        db.add(audit_log)
        await db.commit()
        await db.refresh(resource)
        # push to Redis Stream
        await redis.xadd(
            "resource_stream",
            {"id": resource_id, "expires_at": expires_at.timestamp()}
        )

        #  Schedule notification (1 minute before expiry)
        notification_time = expires_at - timedelta(minutes=1) 
        # notification_time = expires_at - timedelta(minutes=1)
        await redis.zadd(
            "notifications",
            {resource_id: notification_time.timestamp()}
        )

        return {"resource_id": resource_id}

    except Exception as e:
        await db.rollback()  # Prevents partial commits on failure
        raise HTTPException(500, str(e))
