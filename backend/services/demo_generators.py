"""
Demo Data Generators — Clean helpers for generating synthetic data across all domains.
These ONLY run when system mode == "demo".
"""
import random
from datetime import datetime, timezone, timedelta

PAIRS = ["BTC", "ETH", "SOL", "AVAX", "LINK", "DOGE"]
STRATEGIES = ["Alpha Momentum BTC", "ETH Reversal Sniper", "SOL Breakout Pulse", "Volatility Edge"]


def generate_demo_alerts(count=10):
    """Generate synthetic strategy alerts."""
    actions = ["LONG", "SHORT", "CLOSE", "TAKE_PROFIT", "STOP_LOSS"]
    alerts = []
    now = datetime.now(timezone.utc)
    for i in range(count):
        asset = random.choice(PAIRS)
        action = random.choice(actions)
        alerts.append({
            "action": action,
            "asset": asset,
            "message": _alert_message(action, asset),
            "confidence": random.randint(60, 95),
            "price": round(random.uniform(0.5, 70000), 2),
            "strategy_name": random.choice(STRATEGIES),
            "timestamp": (now - timedelta(seconds=random.randint(10, 3600))).isoformat(),
            "is_demo": True,
        })
    return alerts


def _alert_message(action, asset):
    messages = {
        "LONG": f"Bullish breakout detected on {asset} — entering long position",
        "SHORT": f"Bearish divergence on {asset} — opening short",
        "CLOSE": f"Take profit target reached on {asset} — closing position",
        "TAKE_PROFIT": f"TP hit on {asset} — locking in +{random.uniform(1, 8):.1f}% gains",
        "STOP_LOSS": f"SL triggered on {asset} — limiting drawdown to -{random.uniform(0.5, 3):.1f}%",
    }
    return messages.get(action, f"Signal fired on {asset}")


def generate_demo_analytics():
    """Generate synthetic analytics summary."""
    return {
        "total_signals": random.randint(60, 120),
        "avg_win_rate": round(random.uniform(58, 78), 1),
        "win_rate_change": f"+{random.uniform(0.5, 3):.1f}%",
        "sharpe_ratio": round(random.uniform(1.2, 2.5), 2),
        "max_drawdown": round(-random.uniform(3, 12), 1),
        "by_pair": [
            {"name": "BTC", "signals": random.randint(15, 30), "winRate": random.randint(65, 80), "avg_return": round(random.uniform(1.5, 5), 1), "best_trade": round(random.uniform(5, 15), 1), "worst_trade": round(random.uniform(1, 5), 1)},
            {"name": "ETH", "signals": random.randint(12, 25), "winRate": random.randint(60, 75), "avg_return": round(random.uniform(1, 4), 1), "best_trade": round(random.uniform(4, 10), 1), "worst_trade": round(random.uniform(1, 4), 1)},
            {"name": "SOL", "signals": random.randint(8, 20), "winRate": random.randint(62, 78), "avg_return": round(random.uniform(2, 6), 1), "best_trade": round(random.uniform(6, 15), 1), "worst_trade": round(random.uniform(2, 6), 1)},
            {"name": "AVAX", "signals": random.randint(5, 15), "winRate": random.randint(55, 70), "avg_return": round(random.uniform(1, 4), 1), "best_trade": round(random.uniform(3, 8), 1), "worst_trade": round(random.uniform(1, 5), 1)},
            {"name": "DOGE", "signals": random.randint(3, 10), "winRate": random.randint(50, 65), "avg_return": round(random.uniform(0.5, 3), 1), "best_trade": round(random.uniform(2, 6), 1), "worst_trade": round(random.uniform(1, 4), 1)},
        ],
        "is_demo": True,
    }


def generate_demo_analytics_daily(days=14):
    """Generate synthetic daily analytics breakdown."""
    now = datetime.now(timezone.utc)
    daily = []
    for i in range(days):
        day = now - timedelta(days=days - 1 - i)
        daily.append({
            "date": day.strftime("%Y-%m-%d"),
            "views": random.randint(80, 350),
            "clicks": random.randint(20, 80),
            "conversions": random.randint(2, 15),
        })
    return daily


def generate_demo_agent_stats():
    """Generate synthetic agent performance stats."""
    agents = [
        {"id": "momentum-scanner", "name": "Momentum Scanner", "type": "technical"},
        {"id": "sentiment-analyzer", "name": "Sentiment Analyzer", "type": "nlp"},
        {"id": "whale-tracker", "name": "Whale Tracker", "type": "on-chain"},
        {"id": "volatility-engine", "name": "Volatility Engine", "type": "statistical"},
    ]
    result = []
    for a in agents:
        result.append({
            **a,
            "accuracy": random.randint(65, 92),
            "win_rate": round(random.uniform(55, 80), 1),
            "total_pnl": round(random.uniform(-500, 5000), 2),
            "signals_today": random.randint(5, 30),
            "total_signals": random.randint(80, 400),
            "avg_confidence": round(random.uniform(65, 90), 1),
            "status": "active",
            "is_demo": True,
        })
    return result


def generate_demo_events(count=5):
    """Generate synthetic live events."""
    events = []
    now = datetime.now(timezone.utc)
    for i in range(count):
        etype = random.choice(["signal", "trade", "update"])
        if etype == "signal":
            pair = random.choice(PAIRS)
            events.append({
                "type": "signal",
                "pair": f"{pair}/USDT",
                "direction": random.choice(["LONG", "SHORT"]),
                "confidence": round(random.uniform(60, 95), 1),
                "strategy": random.choice(STRATEGIES),
                "entry_price": round(random.uniform(0.5, 70000), 2),
                "timestamp": (now - timedelta(seconds=random.randint(5, 300))).isoformat(),
                "is_demo": True,
            })
        elif etype == "trade":
            pair = random.choice(PAIRS)
            events.append({
                "type": "trade",
                "pair": f"{pair}/USDT",
                "direction": random.choice(["LONG", "SHORT"]),
                "pnl_pct": round(random.uniform(-3, 8), 2),
                "status": "closed",
                "strategy": random.choice(STRATEGIES),
                "timestamp": (now - timedelta(seconds=random.randint(5, 300))).isoformat(),
                "is_demo": True,
            })
        else:
            messages = [
                "Strategy recalibration complete",
                "New support level detected for BTC",
                "Volatility compression on ETH",
                "Risk model updated",
            ]
            events.append({
                "type": "update",
                "message": random.choice(messages),
                "strategy": random.choice(STRATEGIES),
                "timestamp": (now - timedelta(seconds=random.randint(5, 300))).isoformat(),
                "is_demo": True,
            })
    return events
