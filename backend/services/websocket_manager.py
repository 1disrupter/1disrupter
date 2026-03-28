"""
AlphaAI WebSocket Connection Manager
Manages real-time signal broadcast to connected clients.
"""
from fastapi import WebSocket
from typing import Dict, Set
from collections import defaultdict
import asyncio
import json
import logging

logger = logging.getLogger("AlphaAI")

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections grouped by tier and wallet
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {
            "pro": {},      # wallet_address -> WebSocket
            "elite": {},    # wallet_address -> WebSocket
        }
        # Track connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
        # Subscription channels
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # channel -> set of wallet_addresses
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, wallet_address: str, tier: str) -> bool:
        """Accept and register a WebSocket connection"""
        if tier not in ["pro", "elite"]:
            await websocket.close(code=4003, reason="WebSocket requires Pro or Elite subscription")
            return False
        
        await websocket.accept()
        
        async with self._lock:
            # Close existing connection if any
            if wallet_address in self.active_connections[tier]:
                try:
                    await self.active_connections[tier][wallet_address].close()
                except:
                    pass
            
            self.active_connections[tier][wallet_address] = websocket
            self.connection_metadata[wallet_address] = {
                "tier": tier,
                "connected_at": datetime.now(timezone.utc).isoformat(),
                "subscriptions": set()
            }
            
            # Auto-subscribe to default channels
            self.subscriptions["signals"].add(wallet_address)
            self.subscriptions["prices"].add(wallet_address)
            self.connection_metadata[wallet_address]["subscriptions"] = {"signals", "prices"}
        
        logger.info(f"WebSocket connected: {wallet_address} (tier: {tier})")
        return True
    
    async def disconnect(self, wallet_address: str):
        """Remove a WebSocket connection"""
        async with self._lock:
            for tier in ["pro", "elite"]:
                if wallet_address in self.active_connections[tier]:
                    del self.active_connections[tier][wallet_address]
            
            # Remove from all subscriptions
            for channel in self.subscriptions:
                self.subscriptions[channel].discard(wallet_address)
            
            if wallet_address in self.connection_metadata:
                del self.connection_metadata[wallet_address]
        
        logger.info(f"WebSocket disconnected: {wallet_address}")
    
    async def subscribe(self, wallet_address: str, channel: str):
        """Subscribe to a specific channel"""
        async with self._lock:
            self.subscriptions[channel].add(wallet_address)
            if wallet_address in self.connection_metadata:
                self.connection_metadata[wallet_address]["subscriptions"].add(channel)
    
    async def unsubscribe(self, wallet_address: str, channel: str):
        """Unsubscribe from a channel"""
        async with self._lock:
            self.subscriptions[channel].discard(wallet_address)
            if wallet_address in self.connection_metadata:
                self.connection_metadata[wallet_address]["subscriptions"].discard(channel)
    
    async def send_personal(self, wallet_address: str, message: dict):
        """Send a message to a specific connection"""
        for tier in ["pro", "elite"]:
            if wallet_address in self.active_connections[tier]:
                try:
                    await self.active_connections[tier][wallet_address].send_json(message)
                    return True
                except Exception as e:
                    logger.error(f"Error sending to {wallet_address}: {e}")
                    await self.disconnect(wallet_address)
        return False
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast a message to all subscribers of a channel"""
        subscribers = list(self.subscriptions.get(channel, set()))
        tasks = []
        
        for wallet_address in subscribers:
            tasks.append(self.send_personal(wallet_address, message))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            logger.debug(f"Broadcast to {channel}: {success_count}/{len(tasks)} delivered")
    
    async def broadcast_to_tier(self, tier: str, message: dict):
        """Broadcast a message to all connections of a specific tier"""
        if tier not in self.active_connections:
            return
        
        connections = list(self.active_connections[tier].items())
        for wallet_address, websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {wallet_address}: {e}")
                await self.disconnect(wallet_address)
    
    async def broadcast_all(self, message: dict):
        """Broadcast to all Pro and Elite connections"""
        await self.broadcast_to_tier("pro", message)
        await self.broadcast_to_tier("elite", message)
    
    def get_connection_count(self) -> dict:
        """Get count of active connections"""
        return {
            "pro": len(self.active_connections["pro"]),
            "elite": len(self.active_connections["elite"]),
            "total": len(self.active_connections["pro"]) + len(self.active_connections["elite"])
        }
    
    def get_channel_subscribers(self, channel: str) -> int:
        """Get number of subscribers for a channel"""
        return len(self.subscriptions.get(channel, set()))

# Singleton WebSocket manager instance
manager = ConnectionManager()
