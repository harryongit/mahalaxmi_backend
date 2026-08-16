import logging
import redis.asyncio as redis
import fakeredis.aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_instance = None

async def get_redis():
    """Return the Redis client, falling back to an in-memory store when Redis is unavailable."""
    global _redis_instance
    if _redis_instance is not None:
        return _redis_instance

    try:
        client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await client.ping()
        logger.info("Redis connected at %s", settings.REDIS_URL)
        _redis_instance = client
    except Exception as e:
        logger.warning("Redis unavailable (%s) -> using in-memory store (dev mode)", e)
        _redis_instance = fakeredis.aioredis.FakeRedis(decode_responses=True)
        
    return _redis_instance
