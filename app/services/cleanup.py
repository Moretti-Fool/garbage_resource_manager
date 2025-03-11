import asyncio
from datetime import datetime
from app.database import get_db
from app.models import Resource, AuditLog
from app.services.redis_client import redis_async as redis

async def garbage_collector():
    while True:
        try:
            # Read events from Redis Stream
            events = await redis.xread({"resource_stream": "0-0"}, block=0, count=100)
            
            async for db in get_db():  # Proper async session handling
                for stream in events:
                    stream_name, messages = stream
                    for message in messages:
                        event_id, data = message
                        resource_id = data["id"]
                        expires_at = datetime.fromtimestamp(float(data["expires_at"]))

                        if datetime.now() > expires_at:
                            resource = await db.get(Resource, resource_id)
                            if resource:
                                # Add audit log entry
                                db.add(AuditLog(
                                    event="Deleted expired resource",
                                    user_id=resource.user_id,  # Fix: Use user_id correctly
                                    details=f"Resource {resource.filename} expired and was deleted."
                                ))

                                # Delete resource
                                await db.delete(resource)
                                await db.commit()

                                # Now delete from Redis Stream (AFTER commit)
                                await redis.xdel("resource_stream", event_id)
        except Exception as e:
            print(f"Cleanup error: {e}")

        await asyncio.sleep(60)  # Run every minute
