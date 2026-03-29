"""
AlphaAI Market Data Service
Fetches live market data from CoinGecko API.
"""
import httpx
import random
import logging
from datetime import datetime, timezone
from typing import List, Dict

logger = logging.getLogger("AlphaAI")

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

# ============= SIMULATION ROUTES =============
