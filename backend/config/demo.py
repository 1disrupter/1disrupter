"""
Demo Mode Config — DB-backed toggle for instant switching without redeploy.
Falls back to DEMO_MODE env var, then defaults to True.
"""
import os
import time
import logging

logger = logging.getLogger("AlphaAI.DemoConfig")

_cache = {"value": None, "ts": 0}
_CACHE_TTL = 5  # seconds — short TTL so toggle feels instant

_db = None


def init_db(database):
    global _db
    _db = database


async def is_demo_mode() -> bool:
    """Check if demo mode is active. DB value wins over env."""
    now = time.time()
    if _cache["value"] is not None and now - _cache["ts"] < _CACHE_TTL:
        return _cache["value"]

    if _db is not None:
        try:
            doc = await _db.system_config.find_one({"key": "demo_mode"}, {"_id": 0})
            if doc is not None:
                val = doc.get("enabled", True)
                _cache["value"] = val
                _cache["ts"] = now
                return val
        except Exception as e:
            logger.warning(f"Failed to read demo_mode from DB: {e}")

    env_val = os.getenv("DEMO_MODE", "true").lower() == "true"
    _cache["value"] = env_val
    _cache["ts"] = now
    return env_val


async def set_demo_mode(enabled: bool):
    """Persist demo mode toggle to DB."""
    if _db is None:
        raise RuntimeError("DB not initialized")

    await _db.system_config.update_one(
        {"key": "demo_mode"},
        {"$set": {"key": "demo_mode", "enabled": enabled, "updated_at": time.time()}},
        upsert=True,
    )
    _cache["value"] = enabled
    _cache["ts"] = time.time()
    logger.info(f"Demo mode set to {enabled}")


def sync_is_demo_mode() -> bool:
    """Synchronous check (uses cache only, no DB hit)."""
    if _cache["value"] is not None:
        return _cache["value"]
    return os.getenv("DEMO_MODE", "true").lower() == "true"
