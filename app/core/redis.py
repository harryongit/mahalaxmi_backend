import logging
import redis.asyncio as redis
import fakeredis.aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

_initialized = False
redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


async def get_redis():
    """Return the Redis client, falling back to an in-memory store when Redis is unavailable."""
    global _initialized, redis_client
    if _initialized:
        return redis_client
    _initialized = True
    try:
        await redis_client.ping()
        logger.info("Redis connected at %s", settings.REDIS_URL)
    except Exception as e:
        logger.warning("Redis unavailable (%s) — using in-memory store (dev mode)", e)
        redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    return redis_client