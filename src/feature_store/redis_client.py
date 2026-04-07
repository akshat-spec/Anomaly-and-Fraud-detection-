"""Async Redis client wrapper for the fraud-detection feature store."""

import json
import logging
import os
from typing import Any, Dict, Optional

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Return a shared async Redis connection (lazy singleton)."""
    global _pool
    if _pool is None:
        _pool = aioredis.from_url(
            REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
        logger.info("Redis connection pool created (%s).", REDIS_URL)
    return _pool


async def set_user_features(
    user_id: str,
    features: Dict[str, Any],
    ttl: int = 600,
) -> None:
    """Store point-in-time features for a user with a TTL (seconds)."""
    r = await get_redis()
    key = f"user:{user_id}:features"
    await r.set(key, json.dumps(features), ex=ttl)
    logger.debug("SET %s  TTL=%ds", key, ttl)


async def get_user_features(user_id: str) -> Dict[str, Any]:
    """Merge point-in-time features + window features into one dict.

    Returns an empty dict if no data is cached.
    """
    r = await get_redis()

    point_key = f"user:{user_id}:features"
    window_key = f"user:{user_id}:window_features"

    point_raw = await r.get(point_key)
    window_raw = await r.get(window_key)

    merged: Dict[str, Any] = {}
    if point_raw:
        merged.update(json.loads(point_raw))
    if window_raw:
        merged.update(json.loads(window_raw))

    return merged


async def set_window_features(
    user_id: str,
    features: Dict[str, Any],
    ttl: int = 1800,
) -> None:
    """Store windowed aggregation features for a user."""
    r = await get_redis()
    key = f"user:{user_id}:window_features"
    await r.set(key, json.dumps(features), ex=ttl)
    logger.debug("SET %s  TTL=%ds", key, ttl)


async def close() -> None:
    """Gracefully close the Redis pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Redis connection pool closed.")
