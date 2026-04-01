"""
Signal Router
Routes a strategy signal to all subscribed users with execution enabled.
"""
import logging

from cryptography.fernet import Fernet, InvalidToken
import os

from database import db

from services.execution_engine.executor import execute_for_user

logger = logging.getLogger("AlphaAI.SignalRouter")

signals_col = db["strategy_signals"]
subscriptions_col = db["strategy_subscriptions"]
configs_col = db["user_execution_configs"]

_KEY = os.environ.get("EXCHANGE_ENCRYPTION_KEY", "")
_fernet = Fernet(_KEY.encode()) if _KEY else None


def _decrypt(token: str) -> str:
    if not _fernet:
        raise RuntimeError("EXCHANGE_ENCRYPTION_KEY not set")
    return _fernet.decrypt(token.encode()).decode()


async def route_signal(signal_id: str) -> list[dict]:
    """
    Route a signal to all active subscribers with execution enabled.

    Returns list of execution logs created.
    """
    # Load signal
    signal = await signals_col.find_one({"id": signal_id}, {"_id": 0})
    if not signal:
        logger.warning(f"Signal {signal_id} not found")
        return []

    strategy_id = signal["strategy_id"]

    # Find active subscriptions
    subs = await subscriptions_col.find(
        {"strategy_id": strategy_id, "status": "active"}
    ).to_list(length=500)

    if not subs:
        logger.info(f"No active subscribers for strategy {strategy_id}")
        return []

    user_ids = [s["user_id"] for s in subs]
    logs = []

    # Fetch execution configs for all subscribed users
    configs = {}
    async for cfg in configs_col.find({"user_id": {"$in": user_ids}, "is_enabled": True}, {"_id": 0}):
        configs[cfg["user_id"]] = cfg

    for sub in subs:
        uid = sub["user_id"]
        cfg = configs.get(uid)
        if not cfg:
            logger.debug(f"User {uid} has no enabled execution config, skipping")
            continue

        # Load exchange credentials
        user_doc = await db.users.find_one({"id": uid}, {"_id": 0, "exchange_credentials": 1})
        creds = (user_doc or {}).get("exchange_credentials")

        if cfg["execution_mode"] == "testnet":
            if not creds or creds.get("status") != "valid":
                logger.warning(f"User {uid} has no valid exchange credentials for testnet execution")
                continue
            try:
                api_key = _decrypt(creds["api_key_enc"])
                api_secret = _decrypt(creds["secret_key_enc"])
            except (InvalidToken, KeyError):
                logger.error(f"Failed to decrypt credentials for user {uid}")
                continue
        else:
            # Paper mode doesn't need real credentials
            api_key = ""
            api_secret = ""

        log = await execute_for_user(signal, cfg, api_key, api_secret)
        logs.append(log)

    # Mark signal as processed
    await signals_col.update_one(
        {"id": signal_id},
        {"$set": {"processed": True, "execution_count": len(logs)}}
    )

    logger.info(f"Signal {signal_id} routed: {len(logs)} executions")
    return logs
