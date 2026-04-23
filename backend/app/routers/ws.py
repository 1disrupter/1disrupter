# -*- coding: utf-8 -*-
"""WebSocket routes — live Vibe Pulse updates."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.database import SessionLocal
from app.models import Venue, Vibe
from app.services.ws_manager import manager

router = APIRouter(tags=["ws"])


def _snapshot(venue_id: str) -> dict:
    db = SessionLocal()
    try:
        v = db.get(Venue, venue_id)
        vibe = db.get(Vibe, venue_id) if v else None
        if not v or not vibe:
            return {"type": "snapshot", "venue_id": venue_id, "missing": True}
        return {
            "type": "snapshot",
            "venue_id": v.id,
            "name": v.name,
            "category": v.category.value if hasattr(v.category, "value") else v.category,
            "vibe_score": float(vibe.vibe_score or 0.0),
            "crowd_level": vibe.crowd_level.value if hasattr(vibe.crowd_level, "value") else vibe.crowd_level,
            "last_updated": (vibe.last_updated or datetime.now(timezone.utc)).isoformat(),
        }
    finally:
        db.close()


@router.websocket("/ws/vibe/{venue_id}")
async def vibe_pulse(ws: WebSocket, venue_id: str) -> None:
    await manager.connect(venue_id, ws)
    try:
        # First frame: current snapshot so client can paint immediately.
        await ws.send_json(_snapshot(venue_id))
        # Keep-alive loop — we mostly push from producers, but listen to pings.
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=30)
                if msg == "ping":
                    await ws.send_text("pong")
            except asyncio.TimeoutError:
                # proactive heartbeat
                await ws.send_json({"type": "heartbeat", "ts": datetime.now(timezone.utc).isoformat()})
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await manager.disconnect(venue_id, ws)
