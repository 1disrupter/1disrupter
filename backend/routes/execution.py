"""
Execution Engine API Routes
User config, logs, test orders, signal triggering.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid
import logging

from database import db
from routes.auth import get_current_user
from services.execution_engine.signal_router import route_signal
from services.execution_engine.executor import execute_for_user
from services.execution_engine.binance_testnet_client import place_order, get_balance

import os
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("AlphaAI.Execution")
router = APIRouter(prefix="/api/execution", tags=["Execution"])

configs_col = db["user_execution_configs"]
logs_col = db["execution_logs"]
signals_col = db["strategy_signals"]

_KEY = os.environ.get("EXCHANGE_ENCRYPTION_KEY", "")
_fernet = Fernet(_KEY.encode()) if _KEY else None


def _decrypt(token: str) -> str:
    if not _fernet:
        raise RuntimeError("EXCHANGE_ENCRYPTION_KEY not set")
    return _fernet.decrypt(token.encode()).decode()


# ═══════════════════════════════════════════
#  Models
# ═══════════════════════════════════════════

class ExecutionConfigUpdate(BaseModel):
    execution_mode: str = Field("paper", pattern="^(paper|testnet|none)$")
    base_position_size: float = Field(0.001, gt=0, le=10)
    max_risk_per_trade: Optional[float] = Field(None, ge=0, le=1)
    is_enabled: bool = Field(False)

class TestOrderRequest(BaseModel):
    symbol: str = Field("BTCUSDT", min_length=2, max_length=20)
    side: str = Field("BUY", pattern="^(BUY|SELL)$")
    quantity: float = Field(0.001, gt=0, le=1)

class EmitSignalRequest(BaseModel):
    strategy_id: str
    symbol: str
    side: str = Field("BUY", pattern="^(BUY|SELL)$")
    size: Optional[float] = None
    time_in_force: Optional[str] = None
    extra_params: dict = Field(default_factory=dict)


# ═══════════════════════════════════════════
#  Execution Config
# ═══════════════════════════════════════════

@router.get("/configs/me")
async def get_my_config(user: dict = Depends(get_current_user)):
    """Get current user's execution config."""
    cfg = await configs_col.find_one({"user_id": user["id"]}, {"_id": 0})
    if not cfg:
        return {
            "user_id": user["id"],
            "exchange": "binance_testnet",
            "execution_mode": "paper",
            "base_position_size": 0.001,
            "max_risk_per_trade": None,
            "is_enabled": False,
            "exists": False,
        }
    cfg["exists"] = True
    return cfg


@router.post("/configs/me")
async def update_my_config(body: ExecutionConfigUpdate, user: dict = Depends(get_current_user)):
    """Create or update execution config."""
    # If enabling testnet mode, verify exchange is connected
    if body.execution_mode == "testnet" and body.is_enabled:
        u = await db.users.find_one({"id": user["id"]}, {"_id": 0, "exchange_credentials": 1})
        creds = (u or {}).get("exchange_credentials")
        if not creds or creds.get("status") != "valid":
            raise HTTPException(400, "Connect and validate your Binance Testnet API keys first (Settings > Exchange)")

    now = datetime.now(timezone.utc).isoformat()
    update = {
        "user_id": user["id"],
        "exchange": "binance_testnet",
        "execution_mode": body.execution_mode,
        "base_position_size": body.base_position_size,
        "max_risk_per_trade": body.max_risk_per_trade,
        "is_enabled": body.is_enabled,
        "updated_at": now,
    }

    existing = await configs_col.find_one({"user_id": user["id"]})
    if existing:
        await configs_col.update_one({"user_id": user["id"]}, {"$set": update})
    else:
        update["id"] = str(uuid.uuid4())
        update["created_at"] = now
        await configs_col.insert_one(update)

    result = await configs_col.find_one({"user_id": user["id"]}, {"_id": 0})
    return result


# ═══════════════════════════════════════════
#  Execution Logs
# ═══════════════════════════════════════════

@router.get("/logs")
async def get_logs(
    user: dict = Depends(get_current_user),
    strategy_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """Get execution logs. Admins see all, users see their own."""
    query = {}
    if user.get("role") != "admin":
        query["user_id"] = user["id"]
    if strategy_id:
        query["strategy_id"] = strategy_id
    if status:
        query["status"] = status

    cursor = logs_col.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return {"logs": items, "total": len(items)}


@router.get("/logs/admin")
async def get_admin_logs(
    user: dict = Depends(get_current_user),
    user_id: Optional[str] = Query(None),
    strategy_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """Admin-only: get all execution logs with filters."""
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")

    query = {}
    if user_id:
        query["user_id"] = user_id
    if strategy_id:
        query["strategy_id"] = strategy_id
    if status:
        query["status"] = status

    cursor = logs_col.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    total = await logs_col.count_documents(query)
    return {"logs": items, "total": total}


# ═══════════════════════════════════════════
#  Test Order
# ═══════════════════════════════════════════

@router.post("/test-order")
async def test_order(body: TestOrderRequest, user: dict = Depends(get_current_user)):
    """Place a small test order on Binance Testnet to validate connectivity."""
    u = await db.users.find_one({"id": user["id"]}, {"_id": 0, "exchange_credentials": 1})
    creds = (u or {}).get("exchange_credentials")
    if not creds or creds.get("status") != "valid":
        raise HTTPException(400, "No valid exchange connection. Connect your Binance Testnet keys first.")

    try:
        api_key = _decrypt(creds["api_key_enc"])
        api_secret = _decrypt(creds["secret_key_enc"])
    except (InvalidToken, KeyError):
        raise HTTPException(400, "Stored keys are corrupted. Please reconnect.")

    result = await place_order(api_key, api_secret, body.symbol, body.side, body.quantity)

    # Log it
    now = datetime.now(timezone.utc).isoformat()
    log_entry = {
        "id": str(uuid.uuid4()),
        "signal_id": "test_order",
        "user_id": user["id"],
        "strategy_id": "manual_test",
        "exchange": "binance_testnet",
        "execution_mode": "testnet",
        "request_payload": {"symbol": body.symbol, "side": body.side, "quantity": body.quantity},
        "response_payload": result,
        "status": "failed" if (isinstance(result, dict) and result.get("error")) else "success",
        "error_message": result.get("detail") if isinstance(result, dict) and result.get("error") else None,
        "created_at": now,
    }
    await logs_col.insert_one(log_entry)

    is_error = isinstance(result, dict) and result.get("error")
    if is_error:
        raise HTTPException(502, f"Test order failed: {result.get('detail', 'Unknown error')}")

    return {"success": True, "order": result}


# ═══════════════════════════════════════════
#  Signal Emission & Routing
# ═══════════════════════════════════════════

@router.post("/emit-signal")
async def emit_signal(body: EmitSignalRequest, user: dict = Depends(get_current_user)):
    """
    Emit a strategy signal and trigger the execution engine.
    Only the strategy creator can emit signals.
    """
    from database import db as _db
    strategy = await _db["strategies_mp"].find_one({"id": body.strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(404, "Strategy not found")
    if strategy["creator_id"] != user["id"]:
        raise HTTPException(403, "Only the strategy creator can emit signals")

    now = datetime.now(timezone.utc).isoformat()
    signal = {
        "id": str(uuid.uuid4()),
        "strategy_id": body.strategy_id,
        "symbol": body.symbol.upper().replace("/", ""),
        "side": body.side.upper(),
        "size": body.size,
        "time_in_force": body.time_in_force,
        "extra_params": body.extra_params,
        "created_at": now,
        "processed": False,
        "execution_count": 0,
    }
    await signals_col.insert_one(signal)
    signal.pop("_id", None)

    # Route signal to subscribers
    logs = await route_signal(signal["id"])

    return {
        "signal": signal,
        "executions": len(logs),
        "logs": logs,
    }
