"""
Seed 3 featured AI strategies into the marketplace.
Run once: python seed_strategies.py
"""
import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

STRATEGIES = [
    {
        "name": "Alpha Momentum BTC",
        "description": "Trend-following strategy that rides BTC momentum using multi-timeframe moving average crossovers and RSI confirmation. Designed for sustained directional moves.",
        "category": "momentum",
        "parameters": {
            "logic": "momentum",
            "asset": "BTC/USDT",
            "timeframes": ["1h", "4h"],
            "indicators": ["EMA 21/55 crossover", "RSI > 55 for longs"],
            "entry": "EMA crossover confirmed by RSI momentum",
            "exit": "Trailing stop at 2x ATR or RSI divergence",
        },
        "risk_label": "Medium",
        "subscriber_count": 187,
        "avg_rating": 4.6,
        "review_count": 34,
        "perf": {
            "sharpe_ratio": 2.14,
            "win_rate": 62.8,
            "max_drawdown": -11.3,
            "total_return": 47.2,
            "total_trades": 284,
            "avg_trade_pnl": 0.83,
            "period_start": "2025-09-01",
            "period_end": "2026-03-31",
        },
    },
    {
        "name": "ETH Reversal Sniper",
        "description": "Mean-reversion strategy targeting ETH oversold bounces during volatility compression phases. Enters at Bollinger Band extremes with volume divergence confirmation.",
        "category": "mean_reversion",
        "parameters": {
            "logic": "mean_reversion",
            "asset": "ETH/USDT",
            "timeframes": ["15m", "1h"],
            "indicators": ["Bollinger Bands (2σ)", "Volume divergence", "Stochastic RSI"],
            "entry": "Price touches lower BB with stochastic < 20 and decreasing volume",
            "exit": "Mean reversion to BB midline or 1.5% stop-loss",
        },
        "risk_label": "Medium-High",
        "subscriber_count": 142,
        "avg_rating": 4.3,
        "review_count": 21,
        "perf": {
            "sharpe_ratio": 1.87,
            "win_rate": 58.1,
            "max_drawdown": -14.6,
            "total_return": 38.9,
            "total_trades": 412,
            "avg_trade_pnl": 0.47,
            "period_start": "2025-09-01",
            "period_end": "2026-03-31",
        },
    },
    {
        "name": "SOL Breakout Pulse",
        "description": "Breakout detection strategy on SOL that confirms range expansion with volume surges. High-conviction entries on volatility expansion after consolidation.",
        "category": "momentum",
        "parameters": {
            "logic": "breakout",
            "asset": "SOL/USDT",
            "timeframes": ["5m", "1h"],
            "indicators": ["Donchian Channel (20)", "Volume MA ratio > 2x", "ATR expansion"],
            "entry": "Price breaks Donchian high with 2x avg volume confirmation",
            "exit": "Trailing stop at 1.5x ATR or channel re-entry",
        },
        "risk_label": "High",
        "subscriber_count": 96,
        "avg_rating": 4.1,
        "review_count": 15,
        "perf": {
            "sharpe_ratio": 1.52,
            "win_rate": 51.3,
            "max_drawdown": -19.8,
            "total_return": 63.7,
            "total_trades": 531,
            "avg_trade_pnl": 0.60,
            "period_start": "2025-09-01",
            "period_end": "2026-03-31",
        },
    },
]

SYSTEM_CREATOR_ID = "system-alphaai"
SYSTEM_CREATOR_NAME = "AlphaAI System"


async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    strategies_col = db["strategies_mp"]
    performance_col = db["strategy_performance"]

    # Check if already seeded
    existing = await strategies_col.count_documents({"creator_id": SYSTEM_CREATOR_ID, "featured": True})
    if existing >= 3:
        print(f"Already seeded ({existing} featured strategies found). Skipping.")
        client.close()
        return

    # Remove any old system featured strategies to re-seed cleanly
    await strategies_col.delete_many({"creator_id": SYSTEM_CREATOR_ID, "featured": True})
    await performance_col.delete_many({"creator_id": SYSTEM_CREATOR_ID})

    now = datetime.now(timezone.utc).isoformat()

    for s in STRATEGIES:
        strategy_id = str(uuid.uuid4())
        strategy_doc = {
            "id": strategy_id,
            "creator_id": SYSTEM_CREATOR_ID,
            "creator_name": SYSTEM_CREATOR_NAME,
            "name": s["name"],
            "description": s["description"],
            "category": s["category"],
            "parameters": s["parameters"],
            "created_at": now,
            "updated_at": now,
            "is_public": True,
            "status": "published",
            "subscriber_count": s["subscriber_count"],
            "avg_rating": s["avg_rating"],
            "review_count": s["review_count"],
            "featured": True,
            "risk_label": s["risk_label"],
        }
        await strategies_col.insert_one(strategy_doc)
        print(f"  Created strategy: {s['name']} (id={strategy_id})")

        perf_doc = {
            "id": str(uuid.uuid4()),
            "strategy_id": strategy_id,
            "creator_id": SYSTEM_CREATOR_ID,
            **s["perf"],
            "extra": {},
            "uploaded_at": now,
        }
        await performance_col.insert_one(perf_doc)
        print(f"  Created performance record for {s['name']}")

    print(f"\nDone! Seeded {len(STRATEGIES)} featured strategies.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
