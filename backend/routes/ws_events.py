"""
WebSocket Live Events Feed — Real-time strategy signals, trades, and updates.
When DEMO_MODE=true  → broadcasts synthetic events on a timer.
When DEMO_MODE=false → broadcasts real signals from DB + synthetic filler at reduced rate.
"""
import asyncio
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from database import db
from config.demo import is_demo_mode

logger = logging.getLogger("AlphaAI.Events")
router = APIRouter(tags=["WebSocket Events"])


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        logger.info(f"WS connected ({len(self.active)} active)")

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        logger.info(f"WS disconnected ({len(self.active)} active)")

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


# ═══════════════════════════════════════════
#  EVENT GENERATORS
# ═══════════════════════════════════════════

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT"]
DIRECTIONS = ["LONG", "SHORT"]
STRATEGIES = ["Alpha Momentum BTC", "ETH Reversal Sniper", "SOL Breakout Pulse"]


def _generate_signal_event():
    pair = random.choice(PAIRS)
    direction = random.choice(DIRECTIONS)
    confidence = round(random.uniform(60, 95), 1)
    return {
        "type": "signal",
        "pair": pair,
        "direction": direction,
        "confidence": confidence,
        "strategy": random.choice(STRATEGIES),
        "entry_price": round(random.uniform(0.5, 70000), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _generate_trade_event():
    pair = random.choice(PAIRS)
    pnl = round(random.uniform(-3, 8), 2)
    return {
        "type": "trade",
        "pair": pair,
        "direction": random.choice(DIRECTIONS),
        "pnl_pct": pnl,
        "status": "closed",
        "strategy": random.choice(STRATEGIES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _generate_update_event():
    messages = [
        "Strategy recalibration complete — parameters optimized",
        "New support level detected for BTC at $67,200",
        "Volatility compression detected on ETH — breakout imminent",
        "SOL momentum divergence — monitoring for reversal signal",
        "Risk model updated — drawdown limits tightened",
        "Market regime shift detected — switching to defensive mode",
    ]
    return {
        "type": "update",
        "message": random.choice(messages),
        "strategy": random.choice(STRATEGIES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _fetch_real_signals(since_minutes: int = 5) -> list:
    """Fetch recent real signals from trading_signals collection."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    signals = await db.trading_signals.find(
        {"generated_at": {"$gte": cutoff}},
        {"_id": 0, "symbol": 1, "signal_type": 1, "confidence": 1,
         "price_at_signal": 1, "generated_at": 1, "analysis": 1}
    ).sort("generated_at", -1).limit(5).to_list(5)

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
            "strategy": "AI Signal Engine",
            "entry_price": s.get("price_at_signal", 0),
            "timestamp": ts or datetime.now(timezone.utc).isoformat(),
            "is_real": True,
        })
    return events


async def _fetch_real_trades(since_minutes: int = 10) -> list:
    """Fetch recent closed trades from trades collection."""
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=since_minutes)).isoformat()
    trades = await db.trades.find(
        {"status": "closed", "timestamp": {"$gte": cutoff}},
        {"_id": 0, "symbol": 1, "pnl_percent": 1, "side": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(5).to_list(5)

    events = []
    for t in trades:
        events.append({
            "type": "trade",
            "pair": f"{t.get('symbol', 'BTC')}/USDT",
            "direction": t.get("side", "LONG"),
            "pnl_pct": round(t.get("pnl_percent", 0), 2),
            "status": "closed",
            "strategy": "AI Signal Engine",
            "timestamp": str(t.get("timestamp", "")),
            "is_real": True,
        })
    return events


# ═══════════════════════════════════════════
#  WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════

_last_real_check = None


@router.websocket("/api/ws/events")
async def websocket_events(ws: WebSocket):
    await manager.connect(ws)
    try:
        demo = await is_demo_mode()
        await ws.send_json({
            "type": "connected",
            "message": "Live events feed connected",
            "demo_mode": demo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        while True:
            demo = await is_demo_mode()

            if demo:
                # Full demo mode — synthetic events every 4-12s
                await asyncio.sleep(random.uniform(4, 12))
                event_generators = [
                    (_generate_signal_event, 0.4),
                    (_generate_trade_event, 0.3),
                    (_generate_update_event, 0.3),
                ]
                r = random.random()
                cumulative = 0
                for gen, weight in event_generators:
                    cumulative += weight
                    if r <= cumulative:
                        event = gen()
                        break
                else:
                    event = _generate_signal_event()
                await manager.broadcast(event)
            else:
                # Live mode — check for real signals/trades, supplement with updates
                await asyncio.sleep(random.uniform(8, 20))

                real_signals = await _fetch_real_signals(since_minutes=2)
                real_trades = await _fetch_real_trades(since_minutes=5)

                if real_signals:
                    for ev in real_signals[:2]:
                        await manager.broadcast(ev)
                        await asyncio.sleep(0.5)

                if real_trades:
                    for ev in real_trades[:2]:
                        await manager.broadcast(ev)
                        await asyncio.sleep(0.5)

                # Always send a periodic update so the feed doesn't go silent
                if not real_signals and not real_trades:
                    await manager.broadcast(_generate_update_event())

    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error(f"WS error: {e}")
        manager.disconnect(ws)
