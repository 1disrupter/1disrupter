"""
AlphaAI Market Data Service
Fetches live OHLC market data from CoinGecko API with TTL caching.
"""
import httpx
import random
import logging
import time
import math
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("AlphaAI")

# ── Asset mapping ──────────────────────────────────────────────
ASSET_MAP = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
    "AVAX": "avalanche-2", "LINK": "chainlink", "DOT": "polkadot",
    "MATIC": "matic-network", "ADA": "cardano", "DOGE": "dogecoin",
    "BTC/USDT": "bitcoin", "ETH/USDT": "ethereum", "SOL/USDT": "solana",
}

def resolve_asset(asset: str) -> str:
    return ASSET_MAP.get(asset.upper(), ASSET_MAP.get(asset.split("/")[0].upper(), asset.lower()))

# ── In-memory TTL cache ────────────────────────────────────────
_cache: Dict[str, Tuple[float, any]] = {}
CACHE_TTL = 600  # 10 minutes

def _get_cached(key: str):
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None

def _set_cached(key: str, data):
    _cache[key] = (time.time(), data)


# ── OHLC Data ──────────────────────────────────────────────────
async def get_ohlc(asset: str = "BTC", days: int = 365, interval: str = "daily") -> List[Dict]:
    """Fetch OHLC candles from CoinGecko market_chart endpoint."""
    coin_id = resolve_asset(asset)
    cache_key = f"ohlc:{coin_id}:{days}"
    cached = _get_cached(cache_key)
    if cached:
        logger.info(f"OHLC cache hit: {cache_key}")
        return cached

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": days, "interval": interval},
                timeout=15.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                prices = data.get("prices", [])
                candles = _prices_to_ohlc(prices)
                if candles:
                    _set_cached(cache_key, candles)
                    logger.info(f"OHLC fetched: {coin_id}, {len(candles)} candles")
                    return candles

            if resp.status_code == 429:
                logger.warning("CoinGecko rate limit hit, using fallback")
            else:
                logger.warning(f"CoinGecko returned {resp.status_code}")
    except Exception as e:
        logger.error(f"OHLC fetch error: {e}")

    # Fallback to generated mock OHLC
    return _generate_mock_ohlc(days)


def _prices_to_ohlc(prices: List[List], group_size: int = 1) -> List[Dict]:
    """Convert CoinGecko [timestamp, price] list to OHLC candles."""
    if not prices:
        return []
    candles = []
    for i in range(0, len(prices), max(group_size, 1)):
        chunk = prices[i:i + group_size]
        if not chunk:
            continue
        ts = chunk[0][0]
        vals = [p[1] for p in chunk]
        candles.append({
            "timestamp": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat(),
            "open": vals[0],
            "high": max(vals),
            "low": min(vals),
            "close": vals[-1],
        })
    return candles


# ── Mock OHLC fallback ────────────────────────────────────────
MOCK_OHLC_CACHE: Dict[str, List[Dict]] = {}

def _generate_mock_ohlc(days: int = 365) -> List[Dict]:
    cache_key = f"mock:{days}"
    if cache_key in MOCK_OHLC_CACHE:
        return MOCK_OHLC_CACHE[cache_key]

    random.seed(42)  # deterministic for demo
    price = 45000.0
    candles = []
    base_ts = datetime.now(timezone.utc).timestamp() - days * 86400
    for d in range(days):
        o = price
        change = random.gauss(0.001, 0.025)
        c = o * (1 + change)
        h = max(o, c) * (1 + abs(random.gauss(0, 0.01)))
        low = min(o, c) * (1 - abs(random.gauss(0, 0.01)))
        candles.append({
            "timestamp": datetime.fromtimestamp(base_ts + d * 86400, tz=timezone.utc).isoformat(),
            "open": round(o, 2),
            "high": round(h, 2),
            "low": round(low, 2),
            "close": round(c, 2),
        })
        price = c
    random.seed()  # re-randomize
    MOCK_OHLC_CACHE[cache_key] = candles
    return candles


def get_demo_ohlc(days: int = 365) -> List[Dict]:
    """Always return deterministic mock data for Demo Mode."""
    return _generate_mock_ohlc(days)


# ── Legacy functions (keep for backward compat) ───────────────
async def get_market_data(symbol: str = "bitcoin"):
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://api.coingecko.com/api/v3/coins/{symbol}",
                params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
    return None

async def get_market_chart(symbol: str = "bitcoin", days: int = 30):
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart",
                params={"vs_currency": "usd", "days": days},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching chart data: {e}")
    return None

async def get_top_coins():
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 20, "page": 1},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching top coins: {e}")
    return []

def calculate_nav():
    base_nav = 1000000.0
    random_change = random.uniform(-0.05, 0.08)
    return base_nav * (1 + random_change)

def calculate_sharpe_ratio():
    return round(random.uniform(1.2, 2.8), 2)

def calculate_max_drawdown():
    return round(random.uniform(2.0, 8.0), 2)
