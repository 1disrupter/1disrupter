"""
Live Mode Routes — Public demo mode status, live signals, user portfolio.
These endpoints respect the DEMO_MODE flag from config/demo.py.
When DEMO_MODE=false → return real data from DB.
When DEMO_MODE=true  → return demo/synthetic data.
"""
import os
import logging
import random
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from database import db
from config.demo import is_demo_mode

logger = logging.getLogger("AlphaAI.LiveMode")
router = APIRouter(prefix="/api", tags=["Live Mode"])


# ═══════════════════════════════════════════
#  PUBLIC DEMO MODE STATUS
# ═══════════════════════════════════════════

@router.get("/demo-mode/status")
async def get_demo_mode_status():
    """Public endpoint — frontend syncs demo mode from here."""
    demo = await is_demo_mode()
    return {"demo_mode": demo}


# ═══════════════════════════════════════════
#  LIVE SIGNALS ENDPOINT
# ═══════════════════════════════════════════

DEMO_SIGNALS = [
    {"symbol": "BTC", "signal_type": "BUY", "confidence": 87, "price_at_signal": 67432,
     "analysis": "Strong bullish momentum with volume confirmation", "risk_level": "medium"},
    {"symbol": "ETH", "signal_type": "HOLD", "confidence": 72, "price_at_signal": 3521,
     "analysis": "Consolidating near support — waiting for breakout", "risk_level": "low"},
    {"symbol": "SOL", "signal_type": "SELL", "confidence": 65, "price_at_signal": 142,
     "analysis": "Bearish divergence on RSI, taking profits", "risk_level": "high"},
]


@router.get("/signals/live")
async def get_live_signals(
    limit: int = Query(default=20, le=50),
    user_id: Optional[str] = None,
):
    """
    Live signals feed.  Returns real signals when DEMO_MODE=false,
    otherwise returns synthetic demo signals.
    """
    demo = await is_demo_mode()

    if demo:
        # Return demo signals with jittered values
        now = datetime.now(timezone.utc)
        signals = []
        for s in DEMO_SIGNALS:
            jitter = random.uniform(-0.02, 0.02)
            signals.append({
                **s,
                "price_at_signal": round(s["price_at_signal"] * (1 + jitter), 2),
                "confidence": min(99, max(50, s["confidence"] + random.randint(-3, 3))),
                "generated_at": (now - timedelta(minutes=random.randint(1, 30))).isoformat(),
                "is_demo": True,
            })
        return {"signals": signals, "demo_mode": True, "count": len(signals)}

    # ── Real mode: fetch from trading_signals collection ──
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    query = {"generated_at": {"$gte": cutoff}}

    # If user_id provided, optionally filter by followed strategies
    followed_sids = []
    if user_id:
        follows = await db.followed_strategies.find(
            {"user_id": user_id}, {"_id": 0, "strategy_id": 1}
        ).to_list(50)
        followed_sids = [f["strategy_id"] for f in follows]
        if followed_sids:
            query["strategy_id"] = {"$in": followed_sids}

    signals = await db.trading_signals.find(
        query, {"_id": 0}
    ).sort("generated_at", -1).limit(limit).to_list(limit)

    # Serialize datetimes
    for s in signals:
        for k in ("generated_at", "expires_at"):
            if isinstance(s.get(k), datetime):
                s[k] = s[k].isoformat()

    # If no real signals yet, return an empty list (not demo data)
    return {
        "signals": signals,
        "demo_mode": False,
        "count": len(signals),
        "followed_strategies": len(followed_sids) if user_id else None,
    }


# ═══════════════════════════════════════════
#  USER PORTFOLIO PERFORMANCE
# ═══════════════════════════════════════════

DEMO_PORTFOLIO = {
    "total_pnl": 1247.83,
    "total_return_pct": 12.48,
    "win_rate": 68.2,
    "total_trades": 47,
    "winning_trades": 32,
    "losing_trades": 15,
    "sharpe_ratio": 1.82,
    "max_drawdown": 4.2,
    "current_equity": 11247.83,
    "starting_equity": 10000.0,
    "best_trade": {"symbol": "BTC", "pnl": 342.50, "pnl_pct": 3.4},
    "worst_trade": {"symbol": "SOL", "pnl": -128.20, "pnl_pct": -1.3},
}


@router.get("/portfolio/me")
async def get_my_portfolio(
    user_id: str = Query(...),
    days: int = Query(default=30, le=90),
):
    """
    User-specific portfolio performance from their followed strategies' trades.
    Returns real data when DEMO_MODE=false, demo data otherwise.
    """
    demo = await is_demo_mode()

    if demo:
        return {**DEMO_PORTFOLIO, "demo_mode": True, "user_id": user_id, "period_days": days}

    # ── Real mode ──
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    # Get user's followed strategy IDs
    follows = await db.followed_strategies.find(
        {"user_id": user_id}, {"_id": 0, "strategy_id": 1}
    ).to_list(50)
    followed_sids = [f["strategy_id"] for f in follows]

    # Fetch trades for this user (from trades collection)
    trade_query = {"user_id": user_id}
    if cutoff_str:
        trade_query["$or"] = [
            {"timestamp": {"$gte": cutoff_str}},
            {"timestamp": {"$gte": cutoff}},
            {"created_at": {"$gte": cutoff_str}},
            {"created_at": {"$gte": cutoff}},
        ]

    trades = await db.trades.find(
        trade_query,
        {"_id": 0, "pnl": 1, "pnl_percent": 1, "symbol": 1, "timestamp": 1, "status": 1}
    ).sort("timestamp", -1).limit(500).to_list(500)

    if not trades:
        return {
            "total_pnl": 0, "total_return_pct": 0, "win_rate": 0,
            "total_trades": 0, "winning_trades": 0, "losing_trades": 0,
            "sharpe_ratio": 0, "max_drawdown": 0,
            "current_equity": 10000, "starting_equity": 10000,
            "best_trade": None, "worst_trade": None,
            "demo_mode": False, "user_id": user_id, "period_days": days,
            "followed_strategies": len(followed_sids),
        }

    total_pnl = sum(t.get("pnl", 0) for t in trades)
    winners = [t for t in trades if t.get("pnl", 0) > 0]
    losers = [t for t in trades if t.get("pnl", 0) < 0]
    win_rate = round(len(winners) / len(trades) * 100, 1) if trades else 0

    starting_eq = 10000.0
    current_eq = starting_eq + total_pnl

    # Best / worst trade
    best = max(trades, key=lambda t: t.get("pnl", 0)) if trades else None
    worst = min(trades, key=lambda t: t.get("pnl", 0)) if trades else None

    # Simple Sharpe approximation
    pnls = [t.get("pnl", 0) for t in trades]
    avg_pnl = sum(pnls) / len(pnls) if pnls else 0
    std_pnl = (sum((p - avg_pnl) ** 2 for p in pnls) / len(pnls)) ** 0.5 if len(pnls) > 1 else 1
    sharpe = round(avg_pnl / std_pnl * (252 ** 0.5), 2) if std_pnl > 0 else 0

    # Max drawdown
    running = starting_eq
    peak = starting_eq
    max_dd = 0
    for t in reversed(trades):
        running += t.get("pnl", 0)
        peak = max(peak, running)
        dd = (peak - running) / peak * 100 if peak > 0 else 0
        max_dd = max(max_dd, dd)

    return {
        "total_pnl": round(total_pnl, 2),
        "total_return_pct": round(total_pnl / starting_eq * 100, 2),
        "win_rate": win_rate,
        "total_trades": len(trades),
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "sharpe_ratio": sharpe,
        "max_drawdown": round(max_dd, 2),
        "current_equity": round(current_eq, 2),
        "starting_equity": starting_eq,
        "best_trade": {"symbol": best.get("symbol"), "pnl": round(best.get("pnl", 0), 2), "pnl_pct": round(best.get("pnl_percent", 0), 2)} if best else None,
        "worst_trade": {"symbol": worst.get("symbol"), "pnl": round(worst.get("pnl", 0), 2), "pnl_pct": round(worst.get("pnl_percent", 0), 2)} if worst else None,
        "demo_mode": False,
        "user_id": user_id,
        "period_days": days,
        "followed_strategies": len(followed_sids),
    }
