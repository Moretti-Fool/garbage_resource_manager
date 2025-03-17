import logging
import asyncio
from celery import Celery
from redis.asyncio import Redis as aioredis
# from redis.asyncio import Redis, ConnectionPool
from config import settings
from app.database import SessionLocal
from datetime import datetime
from app.utils.email import send_email_async
from app.utils.get_resource_info import get_resource_filename, get_resource_email

logger = logging.getLogger(__name__)


celery = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['celery_tasks.tasks']
)

celery.conf.beat_schedule = {
    "check-notifications-every-10-seconds": {
        "task": "celery_tasks.tasks.check_pending_notifications",
        "schedule": 10.0,
    },
}



@celery.task
def send_verification_email(email: str, verification_link: str):
    """Sends email verification link."""
    subject = "Verify Your Email"
    body = f"""
    <html>
        <body>
            <p>Click the link below to verify your email:</p>
            <a href="{verification_link}">Verify Email</a>
        </body>
    </html>
    """
    success = asyncio.run(send_email_async(email, subject, body))
    
    # Changed: Mask email in logs
    masked_email = f"{email[:3]}***@***{email.split('@')[-1][-3:]}"
    if success:
        logger.info(f"Verification email sent to {masked_email}")
    else:
        logger.error(f"Failed to send verification email to {masked_email}")


@celery.task
def resource_uploaded_mail(email: str, filename: str):
    """Sends email when resource is uploaded."""
    subject = "Resource Uploaded"
    body = f"""
    <html>
        <body>
            <p>You have uploaded {filename} on {datetime.now()}:</p>
        </body>
    </html>
    """
    success = asyncio.run(send_email_async(email, subject, body))
    
    # Changed: Mask email in logs
    masked_email = f"{email[:3]}***@***{email.split('@')[-1][-3:]}"
    if success:
        logger.info(f"Resource notification email sent to {masked_email}")
    else:
        logger.error(f"Failed to send email to {masked_email}")

    

    
@celery.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def check_pending_notifications(self):
    try:
        asyncio.run(async_check_pending_notifications())
    except Exception as e:
        logger.error(f"Task failed after retries: {e}")
        raise

async def async_check_pending_notifications():
    now = datetime.now().timestamp()
    
    # Initialize async Redis client
    async with aioredis.from_url(settings.REDIS_URL) as redis_client:
        # Fetch expiring resources from Redis
        resource_ids = await redis_client.zrangebyscore("notifications", 0, now)
        
        # Process each resource
        async with SessionLocal() as db_session:
            for resource_id_bytes in resource_ids:
                resource_id = resource_id_bytes.decode("utf-8")
                try:
                    filename = await get_resource_filename(db_session, resource_id)
                    mail = await get_resource_email(db_session, resource_id)
                    if not filename or not mail:
                        logger.warning(f"Resource {resource_id} not found")
                        continue

                    # Send email (mock implementation)
                    success = await send_email_async(
                        mail,
                        "Resource Expiry Alert",
                        f"Your resource '{filename}' is expiring soon!"
                    )

                    if success:
                        await redis_client.zrem("notifications", resource_id)
                        logger.info(f"Notification sent for {resource_id}")
                    else:
                        logger.error(f"Failed to send email for {resource_id}")

                except Exception as e:
                    logger.error(f"Error processing {resource_id}: {e}")
                    await db_session.rollback()


