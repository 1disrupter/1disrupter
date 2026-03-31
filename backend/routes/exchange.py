"""
My-AlphaAI Exchange Integration — Testnet Only (Phase 1)
Secure API key handling, Binance Testnet validation, balance/position fetching.
"""
import os
import re
import hmac
import time
import hashlib
import logging
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from database import db
from routes.auth import get_current_user

logger = logging.getLogger("AlphaAI.Exchange")

router = APIRouter(prefix="/api/exchange", tags=["Exchange"])

# ── Encryption ──
_KEY = os.environ.get("EXCHANGE_ENCRYPTION_KEY", "")
_fernet = Fernet(_KEY.encode()) if _KEY else None


def _encrypt(text: str) -> str:
    if not _fernet:
        raise RuntimeError("EXCHANGE_ENCRYPTION_KEY not set")
    return _fernet.encrypt(text.encode()).decode()


def _decrypt(token: str) -> str:
    if not _fernet:
        raise RuntimeError("EXCHANGE_ENCRYPTION_KEY not set")
    return _fernet.decrypt(token.encode()).decode()


# ── Rate limit ──
_rate_map: dict[str, list[float]] = {}
RATE_LIMIT = 5
RATE_WINDOW = 60


def _check_rate(user_id: str):
    now = time.time()
    hits = _rate_map.setdefault(user_id, [])
    hits[:] = [t for t in hits if now - t < RATE_WINDOW]
    if len(hits) >= RATE_LIMIT:
        raise HTTPException(429, "Rate limit exceeded. Try again in a minute.")
    hits.append(now)


# ── Binance Testnet helpers ──
BINANCE_TESTNET_BASE = "https://testnet.binance.vision"


def _sign_request(params: dict, secret: str) -> dict:
    params["timestamp"] = str(int(time.time() * 1000))
    query = urllib.parse.urlencode(params)
    sig = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = sig
    return params


async def _binance_get(path: str, api_key: str, secret: str, params: dict | None = None):
    params = _sign_request(params or {}, secret)
    headers = {"X-MBX-APIKEY": api_key}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BINANCE_TESTNET_BASE}{path}", params=params, headers=headers)
    if r.status_code == 401:
        raise HTTPException(400, "Invalid API key or secret")
    if r.status_code != 200:
        raise HTTPException(502, f"Exchange returned {r.status_code}")
    return r.json()


# ── Models ──
class ConnectExchangeRequest(BaseModel):
    exchange: str = Field(..., pattern="^binance_testnet$")
    api_key: str = Field(..., min_length=10, max_length=128)
    secret_key: str = Field(..., min_length=10, max_length=128)


# ── Endpoints ──

@router.post("/connect")
async def connect_exchange(body: ConnectExchangeRequest, user: dict = Depends(get_current_user)):
    """Encrypt and store exchange credentials, then validate."""
    _check_rate(user["id"])

    # Validate against Binance Testnet
    try:
        account = await _binance_get("/api/v3/account", body.api_key, body.secret_key)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(502, "Could not reach exchange. Try again later.")

    # Extract non-zero balances
    balances = [
        {"asset": b["asset"], "free": float(b["free"]), "locked": float(b["locked"])}
        for b in account.get("balances", [])
        if float(b["free"]) > 0 or float(b["locked"]) > 0
    ]

    # Store encrypted keys
    creds = {
        "exchange": "binance_testnet",
        "api_key_enc": _encrypt(body.api_key),
        "secret_key_enc": _encrypt(body.secret_key),
        "connected_at": datetime.now(timezone.utc),
        "last_validated": datetime.now(timezone.utc),
        "status": "valid",
    }
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"exchange_credentials": creds}},
    )

    return {
        "success": True,
        "exchange": "binance_testnet",
        "balances": balances,
    }


@router.delete("/disconnect")
async def disconnect_exchange(user: dict = Depends(get_current_user)):
    """Remove exchange credentials."""
    await db.users.update_one(
        {"id": user["id"]},
        {"$unset": {"exchange_credentials": ""}},
    )
    return {"success": True}


@router.get("/status")
async def exchange_status(user: dict = Depends(get_current_user)):
    """Return connection status (never exposes secret key)."""
    u = await db.users.find_one({"id": user["id"]}, {"_id": 0, "exchange_credentials": 1})
    creds = (u or {}).get("exchange_credentials")
    if not creds:
        return {"connected": False}

    masked_key = "****" + _decrypt(creds["api_key_enc"])[-4:]

    return {
        "connected": True,
        "exchange": creds["exchange"],
        "api_key_masked": masked_key,
        "connected_at": creds["connected_at"],
        "last_validated": creds["last_validated"],
        "status": creds["status"],
    }


@router.post("/validate")
async def validate_exchange(user: dict = Depends(get_current_user)):
    """Re-validate stored keys and fetch fresh balances + positions."""
    _check_rate(user["id"])

    u = await db.users.find_one({"id": user["id"]}, {"_id": 0, "exchange_credentials": 1})
    creds = (u or {}).get("exchange_credentials")
    if not creds:
        raise HTTPException(400, "No exchange connected")

    try:
        api_key = _decrypt(creds["api_key_enc"])
        secret_key = _decrypt(creds["secret_key_enc"])
    except InvalidToken:
        await db.users.update_one({"id": user["id"]}, {"$set": {"exchange_credentials.status": "invalid"}})
        raise HTTPException(400, "Stored keys are corrupted. Please reconnect.")

    try:
        account = await _binance_get("/api/v3/account", api_key, secret_key)
    except HTTPException as e:
        status = "invalid" if e.status_code == 400 else "error"
        await db.users.update_one({"id": user["id"]}, {"$set": {"exchange_credentials.status": status}})
        raise

    balances = [
        {"asset": b["asset"], "free": float(b["free"]), "locked": float(b["locked"])}
        for b in account.get("balances", [])
        if float(b["free"]) > 0 or float(b["locked"]) > 0
    ]

    # Fetch open orders as "positions" (spot testnet has no futures)
    try:
        open_orders = await _binance_get("/api/v3/openOrders", api_key, secret_key)
    except Exception:
        open_orders = []

    positions = [
        {"symbol": o["symbol"], "side": o["side"], "qty": float(o["origQty"]), "price": float(o["price"])}
        for o in open_orders
    ]

    total_balance = sum(b["free"] + b["locked"] for b in balances)

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "exchange_credentials.last_validated": datetime.now(timezone.utc),
            "exchange_credentials.status": "valid",
        }},
    )

    return {
        "success": True,
        "exchange": "binance_testnet",
        "total_balance_usd": round(total_balance, 2),
        "balances": balances,
        "positions": positions,
    }
