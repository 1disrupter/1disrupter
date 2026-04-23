# -*- coding: utf-8 -*-
"""Vibe Pulse — WebSocket manager for live venue updates.

Clients subscribe by venue_id; producers (feedback, scheduler, offers)
broadcast JSON events to every connected socket for that venue.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("vibe2nite.ws")


class VibeConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()
        self._main_loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Record the server's main event loop so we can dispatch broadcasts
        to it from other async contexts (e.g. asyncio.run in sync routes)."""
        self._main_loop = loop

    async def connect(self, venue_id: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._rooms.setdefault(venue_id, set()).add(ws)
        logger.info("ws connect venue=%s count=%d", venue_id, len(self._rooms[venue_id]))

    async def disconnect(self, venue_id: str, ws: WebSocket) -> None:
        async with self._lock:
            bucket = self._rooms.get(venue_id)
            if bucket and ws in bucket:
                bucket.discard(ws)
                if not bucket:
                    self._rooms.pop(venue_id, None)

    def room_size(self, venue_id: str) -> int:
        return len(self._rooms.get(venue_id, ()))

    async def broadcast(self, venue_id: str, event: dict[str, Any]) -> int:
        """Send event JSON to every socket subscribed to venue_id. Returns count delivered."""
        payload = json.dumps(event)
        delivered = 0
        dead: list[WebSocket] = []
        async with self._lock:
            sockets = list(self._rooms.get(venue_id, ()))
        for ws in sockets:
            try:
                await ws.send_text(payload)
                delivered += 1
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                bucket = self._rooms.get(venue_id)
                if bucket:
                    for ws in dead:
                        bucket.discard(ws)
                    if not bucket:
                        self._rooms.pop(venue_id, None)
        return delivered

    def broadcast_sync(self, venue_id: str, event: dict[str, Any]) -> None:
        """Fire-and-forget from sync/other-loop code paths. If we have a bound
        main loop, schedule there (so sockets on that loop actually receive
        the frame). Otherwise fall back to a fresh loop — best-effort only."""
        loop = self._main_loop
        if loop is not None and loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast(venue_id, event), loop)
            return
        try:
            running = asyncio.get_running_loop()
            running.create_task(self.broadcast(venue_id, event))
        except RuntimeError:
            try:
                asyncio.run(self.broadcast(venue_id, event))
            except Exception:
                pass


manager = VibeConnectionManager()
