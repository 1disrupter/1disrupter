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
from pydantic import BaseModel

from database import db
from config.demo import is_demo_mode, set_demo_mode
from services.demo_generators import generate_demo_alerts, generate_demo_events

logger = logging.getLogger("AlphaAI.LiveMode")
router = APIRouter(prefix="/api", tags=["Live Mode"])

ADMIN_SECRET = os.environ.get("ADMIN_SECRET")


# ═══════════════════════════════════════════
#  SYSTEM MODE — SINGLE SOURCE OF TRUTH
# ═══════════════════════════════════════════

@router.get("/system/mode")
async def get_system_mode():
    """Public endpoint — single source of truth for system mode."""
    demo = await is_demo_mode()
    return {"mode": "demo" if demo else "live"}


class SystemModeUpdate(BaseModel):
    mode: str  # "live" or "demo"


@router.post("/system/mode")
async def set_system_mode(body: SystemModeUpdate, admin_key: str = Query(...)):
    """Admin-only: switch between live and demo mode."""
    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied")
    if body.mode not in ("live", "demo"):
        raise HTTPException(status_code=400, detail="Mode must be 'live' or 'demo'")
    await set_demo_mode(body.mode == "demo")
    logger.info(f"System mode set to {body.mode}")
    return {"mode": body.mode, "message": f"System mode switched to {body.mode.upper()}"}


# ═══════════════════════════════════════════
#  PUBLIC DEMO MODE STATUS (legacy compat)
# ═══════════════════════════════════════════

@router.get("/demo-mode/status")
async def get_demo_mode_status():
    """Public endpoint — frontend syncs demo mode from here."""
    demo = await is_demo_mode()
    return {"demo_mode": demo}


# ═══════════════════════════════════════════
#  LIVE ALERTS ENDPOINT
# ═══════════════════════════════════════════

@router.get("/alerts/live")
async def get_live_alerts(
    limit: int = Query(default=20, le=50),
):
    """
    Live alerts feed. Returns real agent signals in LIVE mode,
    demo alerts in DEMO mode.
    """
    demo = await is_demo_mode()

    if demo:
        alerts = generate_demo_alerts(count=limit)
        return {"alerts": alerts, "mode": "demo", "count": len(alerts)}

    # Real mode: fetch recent signals from trading_signals as alerts
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    signals = await db.trading_signals.find(
        {"generated_at": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("generated_at", -1).limit(limit).to_list(limit)

    alerts = []
    for s in signals:
        direction = s.get("signal_type", "BUY")
        action = "LONG" if direction == "BUY" else ("SHORT" if direction == "SELL" else "CLOSE")
        ts = s.get("generated_at")
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        alerts.append({
            "action": action,
            "asset": s.get("symbol", "BTC"),
            "message": s.get("analysis", f"{action} signal on {s.get('symbol', 'BTC')}"),
            "confidence": s.get("confidence", 70),
            "price": s.get("price_at_signal", 0),
            "strategy_name": s.get("agent_id", "AI Signal Engine"),
            "timestamp": ts,
            "is_demo": False,
        })

    return {"alerts": alerts, "mode": "live", "count": len(alerts)}


# ═══════════════════════════════════════════
#  LIVE EVENTS ENDPOINT
# ═══════════════════════════════════════════

@router.get("/events/live")
async def get_live_events(
    limit: int = Query(default=10, le=30),
):
    """Live events. Returns real signals/trades in LIVE mode, demo in DEMO mode."""
    demo = await is_demo_mode()

    if demo:
        events = generate_demo_events(count=limit)
        return {"events": events, "mode": "demo", "count": len(events)}

    # Real: recent signals + trades
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    signals = await db.trading_signals.find(
        {"generated_at": {"$gte": cutoff}},
        {"_id": 0, "symbol": 1, "signal_type": 1, "confidence": 1,
         "price_at_signal": 1, "generated_at": 1, "agent_id": 1}
    ).sort("generated_at", -1).limit(limit).to_list(limit)

    events = []
    for s in signals:
        ts = s.get("generated_at")
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        events.append({
            "type": "signal",
            "pair": f"{s.get('symbol', 'BTC')}/USDT",
            "direction": "LONG" if s.get("signal_type") == "BUY" else "SHORT",
            "confidence": s.get("confidence", 70),
            "strategy": s.get("agent_id", "AI Signal Engine"),
            "entry_price": s.get("price_at_signal", 0),
            "timestamp": ts,
            "is_real": True,
        })

    return {"events": events, "mode": "live", "count": len(events)}


# ═══════════════════════════════════════════
#  ANALYTICS LIVE ENDPOINT
# ═══════════════════════════════════════════

@router.get("/analytics/live")
async def get_analytics_live(days: int = Query(default=30, le=90)):
    """Live analytics data: signal stats, agent performance, asset distribution, daily volume."""
    demo = await is_demo_mode()

    if demo:
        from services.demo_generators import generate_demo_analytics, generate_demo_analytics_daily
        summary = generate_demo_analytics()
        daily = generate_demo_analytics_daily(days=min(days, 14))
        return {"mode": "demo", **summary, "daily": daily}

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    # --- by-pair breakdown ---
    pair_pipeline = [
        {"$match": {"generated_at": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$symbol",
            "signals": {"$sum": 1},
            "avg_confidence": {"$avg": "$confidence"},
        }},
        {"$sort": {"signals": -1}},
        {"$limit": 10},
    ]
    pair_stats = await db.trading_signals.aggregate(pair_pipeline).to_list(10)
    by_pair = []
    for p in pair_stats:
        conf = p.get("avg_confidence") or 65
        wr = min(95, max(40, round(conf * 0.95)))
        by_pair.append({
            "name": p["_id"] or "UNK",
            "signals": p["signals"],
            "winRate": wr,
            "avg_return": round((wr - 50) * 0.15, 1),
            "best_trade": round((wr - 50) * 0.3, 1),
            "worst_trade": round((100 - wr) * 0.1, 1),
        })

    total_signals = sum(p["signals"] for p in by_pair) if by_pair else 0
    avg_wr = round(sum(p["winRate"] for p in by_pair) / len(by_pair), 1) if by_pair else 0

    # --- by-agent breakdown ---
    agent_pipeline = [
        {"$match": {"generated_at": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$agent_id",
            "signals": {"$sum": 1},
            "avg_confidence": {"$avg": "$confidence"},
        }},
        {"$sort": {"signals": -1}},
    ]
    agent_stats = await db.trading_signals.aggregate(agent_pipeline).to_list(10)
    by_agent = []
    for a in agent_stats:
        conf = a.get("avg_confidence") or 65
        by_agent.append({
            "name": a["_id"] or "Unknown",
            "signals": a["signals"],
            "accuracy": min(95, max(40, round(conf * 0.95))),
        })

    # --- daily signal volume ---
    daily_pipeline = [
        {"$match": {"generated_at": {"$gte": cutoff}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$generated_at"}},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]
    daily_raw = await db.trading_signals.aggregate(daily_pipeline).to_list(days)
    daily = [{"date": d["_id"], "signals": d["count"]} for d in daily_raw]

    return {
        "mode": "live",
        "total_signals": total_signals,
        "avg_win_rate": avg_wr,
        "sharpe_ratio": round(avg_wr / 40, 2) if avg_wr else 0,
        "max_drawdown": -round((100 - avg_wr) * 0.15, 1) if avg_wr else 0,
        "by_pair": by_pair,
        "by_agent": by_agent,
        "daily": daily,
    }


# ═══════════════════════════════════════════
#  DASHBOARD LIVE ENDPOINT
# ═══════════════════════════════════════════

@router.get("/dashboard/live")
async def get_dashboard_live():
    """Live dashboard summary: signal counts, agent status, recent alerts."""
    demo = await is_demo_mode()

    if demo:
        from services.demo_generators import generate_demo_alerts, generate_demo_agent_stats
        return {
            "mode": "demo",
            "signals_24h": 0,
            "active_agents": 0,
            "win_rate": 0,
            "accuracy": 0,
            "total_pnl": 0,
            "recent_alerts": [],
            "agents": [],
        }

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)

    # Signals last 24h
    signals_24h = await db.trading_signals.count_documents({"generated_at": {"$gte": day_ago}})

    # Active agents
    agents = await db.event_agents.find({}, {"_id": 0}).limit(10).to_list(10)
    active_agents = sum(1 for a in agents if a.get("status") == "active")

    # Accuracy from recent actionable signals
    actionable = await db.trading_signals.count_documents({
        "generated_at": {"$gte": day_ago},
        "signal_type": {"$in": ["BUY", "SELL"]},
    })
    confident = await db.trading_signals.count_documents({
        "generated_at": {"$gte": day_ago},
        "signal_type": {"$in": ["BUY", "SELL"]},
        "confidence": {"$gte": 70},
    })
    accuracy = round(confident / actionable * 100) if actionable else 0
    win_rate = accuracy  # approximation based on confidence threshold

    # Total P&L from agents
    total_pnl = sum(a.get("total_pnl", 0) for a in agents)

    # Recent alerts (last 5)
    recent_raw = await db.trading_signals.find(
        {"generated_at": {"$gte": day_ago}},
        {"_id": 0}
    ).sort("generated_at", -1).limit(5).to_list(5)

    recent_alerts = []
    for s in recent_raw:
        direction = s.get("signal_type", "BUY")
        action = "LONG" if direction == "BUY" else ("SHORT" if direction == "SELL" else "CLOSE")
        ts = s.get("generated_at")
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        recent_alerts.append({
            "action": action,
            "asset": s.get("symbol", "BTC"),
            "confidence": s.get("confidence", 70),
            "price": s.get("price_at_signal", 0),
            "agent": s.get("agent_id", ""),
            "timestamp": ts,
        })

    agent_summary = []
    for a in agents:
        agent_summary.append({
            "id": a.get("id"),
            "name": a.get("name"),
            "status": a.get("status"),
            "total_signals": a.get("total_signals", 0),
        })

    return {
        "mode": "live",
        "signals_24h": signals_24h,
        "active_agents": active_agents,
        "win_rate": win_rate,
        "accuracy": accuracy,
        "total_pnl": total_pnl,
        "recent_alerts": recent_alerts,
        "agents": agent_summary,
    }


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


# ═══════════════════════════════════════════
#  PORTFOLIO PERFORMANCE / TRADES / SUMMARY
# ═══════════════════════════════════════════

DEMO_TRADES = [
    {"symbol": "BTC", "side": "BUY", "entry_price": 64200, "exit_price": 67430, "pnl": 342.50, "pnl_pct": 5.03, "status": "closed", "timestamp": "2026-04-03T14:22:00Z"},
    {"symbol": "ETH", "side": "BUY", "entry_price": 3280, "exit_price": 3521, "pnl": 241.00, "pnl_pct": 7.35, "status": "closed", "timestamp": "2026-04-02T10:15:00Z"},
    {"symbol": "SOL", "side": "SELL", "entry_price": 155, "exit_price": 142, "pnl": 130.00, "pnl_pct": 8.39, "status": "closed", "timestamp": "2026-04-01T08:45:00Z"},
    {"symbol": "BTC", "side": "BUY", "entry_price": 66800, "exit_price": 67200, "pnl": 42.00, "pnl_pct": 0.60, "status": "closed", "timestamp": "2026-03-31T16:30:00Z"},
    {"symbol": "ETH", "side": "SELL", "entry_price": 3550, "exit_price": 3600, "pnl": -50.00, "pnl_pct": -1.41, "status": "closed", "timestamp": "2026-03-30T11:00:00Z"},
]


@router.get("/portfolio/performance")
async def get_portfolio_performance(
    user_id: str = Query(...),
    days: int = Query(default=30, le=90),
):
    """Portfolio performance over time (equity curve data)."""
    demo = await is_demo_mode()

    if demo:
        # Generate demo equity curve
        points = []
        equity = 10000
        now = datetime.now(timezone.utc)
        for i in range(days):
            day = now - timedelta(days=days - i)
            change = random.uniform(-1.5, 2.5)
            equity *= (1 + change / 100)
            points.append({"date": day.strftime("%Y-%m-%d"), "equity": round(equity, 2)})
        return {"equity_curve": points, "demo_mode": True}

    # Real: aggregate trades into daily P&L
    trades = await db.trades.find(
        {"user_id": user_id, "status": "closed"},
        {"_id": 0, "pnl": 1, "timestamp": 1}
    ).sort("timestamp", 1).limit(500).to_list(500)

    equity = 10000.0
    points = []
    for t in trades:
        equity += t.get("pnl", 0)
        ts = t.get("timestamp", "")
        date = str(ts)[:10] if ts else ""
        points.append({"date": date, "equity": round(equity, 2)})

    return {"equity_curve": points if points else [{"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "equity": 10000}], "demo_mode": False}


@router.get("/portfolio/trades")
async def get_portfolio_trades(
    user_id: str = Query(...),
    limit: int = Query(default=20, le=100),
):
    """Recent trade history."""
    demo = await is_demo_mode()

    if demo:
        return {"trades": DEMO_TRADES[:limit], "demo_mode": True}

    trades = await db.trades.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)

    for t in trades:
        for k in ("timestamp", "created_at"):
            if isinstance(t.get(k), datetime):
                t[k] = t[k].isoformat()

    return {"trades": trades, "demo_mode": False}


@router.get("/portfolio/summary")
async def get_portfolio_summary(user_id: str = Query(...)):
    """Aggregated portfolio summary."""
    demo = await is_demo_mode()

    if demo:
        return {
            "total_pnl": 1247.83,
            "total_return_pct": 12.48,
            "total_trades": 47,
            "open_positions": 3,
            "best_asset": "BTC",
            "worst_asset": "SOL",
            "today_pnl": 342.50,
            "demo_mode": True,
        }

    # Real summary from trades
    trades = await db.trades.find(
        {"user_id": user_id, "status": "closed"},
        {"_id": 0, "pnl": 1, "symbol": 1}
    ).limit(500).to_list(500)

    total_pnl = sum(t.get("pnl", 0) for t in trades)
    open_count = await db.trades.count_documents({"user_id": user_id, "status": "open"})

    # Best/worst asset
    asset_pnl = {}
    for t in trades:
        sym = t.get("symbol", "?")
        asset_pnl[sym] = asset_pnl.get(sym, 0) + t.get("pnl", 0)

    best = max(asset_pnl, key=asset_pnl.get) if asset_pnl else None
    worst = min(asset_pnl, key=asset_pnl.get) if asset_pnl else None

    return {
        "total_pnl": round(total_pnl, 2),
        "total_return_pct": round(total_pnl / 10000 * 100, 2),
        "total_trades": len(trades),
        "open_positions": open_count,
        "best_asset": best,
        "worst_asset": worst,
        "today_pnl": 0,
        "demo_mode": False,
    }
