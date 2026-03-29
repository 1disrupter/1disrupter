"""
AlphaAI Admin Events WebSocket Manager
Manages admin connections for real-time event streaming on the traffic dashboard.
"""
from fastapi import WebSocket
from typing import Dict
import asyncio
import logging

logger = logging.getLogger("AlphaAI.AdminEvents")


class AdminEventsManager:
    """Manages WebSocket connections for real-time admin event streaming."""

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}  # conn_id -> WebSocket
        self.demo_filter: Dict[str, bool] = {}       # conn_id -> True if demo-only
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, conn_id: str, demo_only: bool = False):
        await websocket.accept()
        async with self._lock:
            old = self.connections.get(conn_id)
            if old:
                try:
                    await old.close()
                except Exception:
                    pass
            self.connections[conn_id] = websocket
            self.demo_filter[conn_id] = demo_only
        logger.info(f"Admin events WS connected: {conn_id} (demo_only={demo_only})")

    async def disconnect(self, conn_id: str):
        async with self._lock:
            self.connections.pop(conn_id, None)
            self.demo_filter.pop(conn_id, None)
        logger.info(f"Admin events WS disconnected: {conn_id}")

    async def broadcast_event(self, event: dict):
        """Broadcast a traffic event to all connected admin clients."""
        is_demo_event = event.get("metadata", {}).get("demo", False)
        disconnected = []

        for conn_id, ws in list(self.connections.items()):
            # If admin is in demo-only mode, skip non-demo events
            if self.demo_filter.get(conn_id) and not is_demo_event:
                continue
            try:
                await ws.send_json(event)
            except Exception:
                disconnected.append(conn_id)

        for conn_id in disconnected:
            await self.disconnect(conn_id)

    def get_stats(self) -> dict:
        return {
            "admin_connections": len(self.connections),
            "demo_only": sum(1 for v in self.demo_filter.values() if v),
        }


admin_events_manager = AdminEventsManager()
