import json
import redis.asyncio as aioredis

from app.config import settings

_redis_client: aioredis.Redis | None = None

LEADERBOARD_KEY = "leaderboard:top50"


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def get_leaderboard_cache() -> list | None:
    """Returns cached leaderboard data or None on miss."""
    try:
        client = await get_redis()
        data = await client.get(LEADERBOARD_KEY)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


async def set_leaderboard_cache(data: list) -> None:
    """Cache the leaderboard with configured TTL."""
    try:
        client = await get_redis()
        await client.set(
            LEADERBOARD_KEY,
            json.dumps(data),
            ex=settings.LEADERBOARD_CACHE_TTL,
        )
    except Exception:
        pass  # Cache failure is non-fatal


async def invalidate_leaderboard_cache() -> None:
    """Delete the leaderboard cache — called after every new rating."""
    try:
        client = await get_redis()
        await client.delete(LEADERBOARD_KEY)
    except Exception:
        pass  # Non-fatal
