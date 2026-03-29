"""
AlphaAI Strategy Alerts Connection Manager
Manages WebSocket connections for real-time strategy alert broadcasts.
"""
from fastapi import WebSocket
from typing import Dict
import asyncio
import logging

logger = logging.getLogger("AlphaAI")


class AlertsManager:
    """Manages WebSocket connections for real-time strategy alerts."""

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}  # user_id -> WebSocket
        self.demo_connections: Dict[str, WebSocket] = {}  # demo_id -> WebSocket
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str, is_demo: bool = False):
        await websocket.accept()
        async with self._lock:
            target = self.demo_connections if is_demo else self.connections
            old = target.get(user_id)
            if old:
                try:
                    await old.close()
                except Exception:
                    pass
            target[user_id] = websocket
        logger.info(f"Alerts WS connected: {user_id} (demo={is_demo})")

    async def disconnect(self, user_id: str, is_demo: bool = False):
        async with self._lock:
            target = self.demo_connections if is_demo else self.connections
            target.pop(user_id, None)
        logger.info(f"Alerts WS disconnected: {user_id} (demo={is_demo})")

    async def send_to_user(self, user_id: str, message: dict) -> bool:
        ws = self.connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
                return True
            except Exception:
                await self.disconnect(user_id)
        return False

    async def broadcast_to_users(self, user_ids: list, message: dict):
        tasks = [self.send_to_user(uid, message) for uid in user_ids]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_demo(self, message: dict):
        disconnected = []
        for did, ws in list(self.demo_connections.items()):
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(did)
        for did in disconnected:
            await self.disconnect(did, is_demo=True)

    def get_stats(self) -> dict:
        return {
            "pro_connections": len(self.connections),
            "demo_connections": len(self.demo_connections),
            "total": len(self.connections) + len(self.demo_connections),
        }


alerts_manager = AlertsManager()
