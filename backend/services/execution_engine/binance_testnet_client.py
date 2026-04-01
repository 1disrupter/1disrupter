"""
Binance Testnet REST Client
Wrapper for placing/canceling orders and fetching account data.
Reuses HMAC signing pattern from exchange.py.
"""
import hmac
import time
import hashlib
import logging
import urllib.parse

import httpx

logger = logging.getLogger("AlphaAI.BinanceTestnet")

BINANCE_TESTNET_BASE = "https://testnet.binance.vision"
TIMEOUT = 15


def _sign(params: dict, secret: str) -> dict:
    params["timestamp"] = str(int(time.time() * 1000))
    query = urllib.parse.urlencode(params)
    sig = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = sig
    return params


async def _request(method: str, path: str, api_key: str, secret: str, params: dict | None = None):
    params = _sign(params or {}, secret)
    headers = {"X-MBX-APIKEY": api_key}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        if method == "GET":
            r = await client.get(f"{BINANCE_TESTNET_BASE}{path}", params=params, headers=headers)
        else:
            r = await client.post(f"{BINANCE_TESTNET_BASE}{path}", params=params, headers=headers)

    if r.status_code not in (200, 201):
        logger.error(f"Binance Testnet {method} {path} returned {r.status_code}: {r.text}")
        return {"error": True, "status_code": r.status_code, "detail": r.text}

    return r.json()


async def place_order(api_key: str, secret: str, symbol: str, side: str, quantity: float, order_type: str = "MARKET") -> dict:
    """Place an order on Binance Testnet."""
    params = {
        "symbol": symbol.upper().replace("/", ""),
        "side": side.upper(),
        "type": order_type.upper(),
        "quantity": str(quantity),
    }
    if order_type.upper() == "LIMIT":
        params["timeInForce"] = "GTC"

    result = await _request("POST", "/api/v3/order", api_key, secret, params)
    return result


async def cancel_order(api_key: str, secret: str, symbol: str, order_id: int) -> dict:
    """Cancel an open order."""
    params = {"symbol": symbol.upper().replace("/", ""), "orderId": str(order_id)}
    return await _request("DELETE", "/api/v3/order", api_key, secret, params)


async def get_balance(api_key: str, secret: str) -> list[dict]:
    """Get non-zero balances."""
    result = await _request("GET", "/api/v3/account", api_key, secret)
    if isinstance(result, dict) and result.get("error"):
        return []
    return [
        {"asset": b["asset"], "free": float(b["free"]), "locked": float(b["locked"])}
        for b in result.get("balances", [])
        if float(b["free"]) > 0 or float(b["locked"]) > 0
    ]


async def get_open_orders(api_key: str, secret: str, symbol: str | None = None) -> list[dict]:
    """Get open orders."""
    params = {}
    if symbol:
        params["symbol"] = symbol.upper().replace("/", "")
    result = await _request("GET", "/api/v3/openOrders", api_key, secret, params)
    if isinstance(result, dict) and result.get("error"):
        return []
    return result
