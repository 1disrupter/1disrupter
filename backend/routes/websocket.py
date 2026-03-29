"""
AlphaAI WebSocket Routes
Real-time strategy alerts and signal broadcasts.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import asyncio
import random
import logging

from services.alerts_manager import alerts_manager
from services.websocket_manager import manager as ws_manager

logger = logging.getLogger("AlphaAI")

router = APIRouter(prefix="/api")

# ── Mock alert generator for Demo mode ─────────────────────────

MOCK_STRATEGIES = [
    {"id": "demo-1", "name": "BTC Momentum Alpha", "asset": "BTC/USDT"},
    {"id": "demo-2", "name": "ETH Mean Reversion", "asset": "ETH/USDT"},
    {"id": "demo-3", "name": "SOL Breakout Trader", "asset": "SOL/USDT"},
]

MOCK_ACTIONS = [
    ("LONG", "triggered LONG signal", "84"),
    ("SHORT", "triggered SHORT signal", "76"),
    ("CLOSE", "closed position — PnL: +${pnl}", "91"),
    ("TAKE_PROFIT", "hit take-profit target", "95"),
    ("STOP_LOSS", "hit stop-loss — minimal loss", "88"),
]


def _generate_mock_alert():
    strat = random.choice(MOCK_STRATEGIES)
    action_tpl = random.choice(MOCK_ACTIONS)
    pnl = round(random.uniform(50, 1500), 2)
    price = round(random.uniform(60000, 72000) if "BTC" in strat["asset"]
                  else random.uniform(3200, 4000) if "ETH" in strat["asset"]
                  else random.uniform(120, 200), 2)
    msg = f'{strat["name"]} {action_tpl[1].replace("${pnl}", str(pnl))} at ${price:,.2f} (confidence: {action_tpl[2]}%)'
    return {
        "type": "strategy_alert",
        "strategy_id": strat["id"],
        "strategy_name": strat["name"],
        "asset": strat["asset"],
        "action": action_tpl[0],
        "message": msg,
        "confidence": int(action_tpl[2]),
        "price": price,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── WebSocket: Strategy Alerts ─────────────────────────────────

@router.websocket("/ws/alerts/{client_id}")
async def websocket_alerts(websocket: WebSocket, client_id: str):
    """
    Real-time strategy alerts WebSocket.

    client_id formats:
      - "demo-{random}" → Demo mode (mock alerts every 10-20s)
      - "{user_id}:pro"  → Pro user (receives real alerts)
      - "{user_id}:elite" → Elite user (receives real alerts)
      - "{user_id}:free" → Free user (gets upgrade prompt, then disconnect)
    """
    # ── Demo mode ──────────────────────────────────────────────
    if client_id.startswith("demo"):
        await alerts_manager.connect(websocket, client_id, is_demo=True)
        try:
            await websocket.send_json({
                "type": "connected",
                "mode": "demo",
                "message": "Connected to AlphaAI demo alerts stream",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            while True:
                delay = random.randint(10, 20)
                await asyncio.sleep(delay)
                alert = _generate_mock_alert()
                await websocket.send_json(alert)
        except (WebSocketDisconnect, Exception):
            pass
        finally:
            await alerts_manager.disconnect(client_id, is_demo=True)
        return

    # ── Authenticated user ─────────────────────────────────────
    parts = client_id.split(":")
    if len(parts) != 2:
        await websocket.close(code=4000, reason="Invalid client_id format. Use user_id:tier")
        return

    user_id, tier = parts
    tier = tier.lower()

    # Free user → upgrade prompt
    if tier not in ("pro", "elite"):
        await websocket.accept()
        await websocket.send_json({
            "type": "upgrade_required",
            "message": "Real-time strategy alerts require a Pro subscription. Upgrade now for instant signals.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await websocket.close(code=4003, reason="Pro subscription required")
        return

    # Pro / Elite → full connection
    await alerts_manager.connect(websocket, user_id)
    try:
        await websocket.send_json({
            "type": "connected",
            "mode": tier,
            "message": f"Connected to AlphaAI real-time alerts ({tier})",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Keep-alive loop
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=60)
                if data.get("action") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception:
                    break
            except (WebSocketDisconnect, Exception):
                break
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        await alerts_manager.disconnect(user_id)


# ── REST: Alerts status ────────────────────────────────────────

@router.get("/alerts/status")
async def alerts_status():
    stats = alerts_manager.get_stats()
    return {"status": "active", "connections": stats}


# ── REST: Trigger test alert (for testing) ─────────────────────

@router.post("/alerts/test")
async def trigger_test_alert():
    """Broadcasts a test alert to all connected Pro users."""
    alert = _generate_mock_alert()
    alert["type"] = "strategy_alert"
    alert["test"] = True
    for uid in list(alerts_manager.connections.keys()):
        await alerts_manager.send_to_user(uid, alert)
    await alerts_manager.broadcast_demo(alert)
    return {"success": True, "alert": alert, "broadcast_to": alerts_manager.get_stats()}
