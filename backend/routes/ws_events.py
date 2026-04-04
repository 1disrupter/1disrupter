"""
WebSocket Live Events Feed — Real-time strategy signals, trades, and updates.
Broadcasts events to all connected clients. Graceful disconnect handling.
"""
import asyncio
import json
import random
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

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
#  EVENT TYPES
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


# ═══════════════════════════════════════════
#  WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════

@router.websocket("/api/ws/events")
async def websocket_events(ws: WebSocket):
    await manager.connect(ws)
    try:
        # Send initial connection event
        await ws.send_json({
            "type": "connected",
            "message": "Live events feed connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        while True:
            # Generate random events at intervals (demo mode)
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

    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error(f"WS error: {e}")
        manager.disconnect(ws)
