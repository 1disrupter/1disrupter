"""
Order Executor
Executes a single signal for a specific user's execution config.
Determines order size, calls Binance Testnet, logs the result.
"""
import uuid
import logging
from datetime import datetime, timezone

from database import db
from services.execution_engine.binance_testnet_client import place_order

logger = logging.getLogger("AlphaAI.Executor")

execution_logs_col = db["execution_logs"]


async def execute_for_user(signal: dict, user_config: dict, api_key: str, api_secret: str) -> dict:
    """
    Execute a signal for a single user.

    Args:
        signal: The strategy signal (symbol, side, size, etc.)
        user_config: The user_execution_config document
        api_key: Decrypted Binance API key
        api_secret: Decrypted Binance API secret

    Returns:
        execution_log dict
    """
    now = datetime.now(timezone.utc).isoformat()
    log_id = str(uuid.uuid4())

    symbol = signal.get("symbol", "").upper().replace("/", "")
    side = signal.get("side", "BUY").upper()

    # Determine order size
    quantity = signal.get("size")
    if not quantity:
        quantity = user_config.get("base_position_size", 0.001)

    request_payload = {
        "symbol": symbol,
        "side": side,
        "quantity": float(quantity),
        "type": "MARKET",
    }

    log_entry = {
        "id": log_id,
        "signal_id": signal.get("id", ""),
        "user_id": user_config["user_id"],
        "strategy_id": signal.get("strategy_id", ""),
        "exchange": "binance_testnet",
        "execution_mode": user_config.get("execution_mode", "paper"),
        "request_payload": request_payload,
        "response_payload": None,
        "status": "pending",
        "error_message": None,
        "created_at": now,
    }

    try:
        if user_config.get("execution_mode") == "paper":
            # Paper mode: simulate success without hitting exchange
            response = {
                "paper": True,
                "symbol": symbol,
                "side": side,
                "quantity": float(quantity),
                "status": "FILLED",
                "simulated": True,
            }
            log_entry["response_payload"] = response
            log_entry["status"] = "success"
            logger.info(f"Paper executed: {side} {quantity} {symbol} for user={user_config['user_id']}")

        elif user_config.get("execution_mode") == "testnet":
            # Testnet mode: real Binance Testnet order
            result = await place_order(api_key, api_secret, symbol, side, float(quantity))

            if isinstance(result, dict) and result.get("error"):
                log_entry["response_payload"] = result
                log_entry["status"] = "failed"
                log_entry["error_message"] = result.get("detail", "Unknown error")
                logger.error(f"Testnet order failed: {result}")
            else:
                log_entry["response_payload"] = result
                log_entry["status"] = "success"
                logger.info(f"Testnet executed: {side} {quantity} {symbol} for user={user_config['user_id']}, orderId={result.get('orderId')}")
        else:
            log_entry["status"] = "skipped"
            log_entry["error_message"] = f"Unknown execution_mode: {user_config.get('execution_mode')}"

    except Exception as e:
        log_entry["status"] = "failed"
        log_entry["error_message"] = str(e)
        logger.exception(f"Execution error for user={user_config['user_id']}")

    await execution_logs_col.insert_one(log_entry)
    log_entry.pop("_id", None)
    return log_entry
