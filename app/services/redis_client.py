
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from config import settings

# Sync Redis for Celery
redis_sync = Redis.from_url(settings.REDIS_URL, decode_responses=True)
# redis_sync = Redis(host='localhost', port=6379, db=0)

# Async Redis for FastAPI
redis_async = AsyncRedis.from_url(settings.REDIS_URL, decode_responses=True)
# redis_async = Redis(host='localhost', port=6379, db=0)
async def get_redis():
    return redis_async