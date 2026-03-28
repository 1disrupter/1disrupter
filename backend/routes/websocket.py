"""
AlphaAI WebSocket Route
Real-time signal and price broadcast via WebSocket.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
from services.websocket_manager import manager
from services.signal_service import signal_service

logger = logging.getLogger("AlphaAI")

router = APIRouter(prefix="/api")

@router.websocket("/ws/signals/{client_id}")
async def websocket_signals_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time signal updates.
    Requires Pro or Elite tier.
    
    client_id format: {user_id}:{tier} (e.g., "abc123:pro")
    """
    try:
        # Parse client_id to get user_id and tier
        parts = client_id.split(":")
        if len(parts) != 2:
            await websocket.close(code=4000, reason="Invalid client_id format")
            return
        
        user_id, tier = parts
        tier = tier.lower()
        
        if tier not in ["pro", "elite"]:
            await websocket.close(code=4003, reason="WebSocket requires Pro or Elite subscription")
            return
        
        # Connect using the connection manager
        connected = await ws_manager.connect(websocket, user_id, tier)
        if not connected:
            return
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to AlphaAI real-time signals ({tier})",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Send current signals immediately
        signals = await signal_service.get_realtime_signals(user_id)
        await websocket.send_json({
            "type": "signals",
            "data": signals,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                
                # Handle subscription requests
                if data.get("action") == "subscribe":
                    channel = data.get("channel")
                    if channel:
                        await ws_manager.subscribe(user_id, channel)
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel": channel
                        })
                
                elif data.get("action") == "unsubscribe":
                    channel = data.get("channel")
                    if channel:
                        await ws_manager.unsubscribe(user_id, channel)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "channel": channel
                        })
                
                elif data.get("action") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await ws_manager.disconnect(user_id)
        logger.info(f"WebSocket disconnected: {user_id}")

# WebSocket status endpoint
@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection statistics"""
    counts = ws_manager.get_connection_count()
    return {
        "status": "active",
        "connections": counts,
        "channels": {
            "signals": ws_manager.get_channel_subscribers("signals"),
            "prices": ws_manager.get_channel_subscribers("prices"),
            "trades": ws_manager.get_channel_subscribers("trades")
        }
    }

# ============= NOTIFICATION PREFERENCES ENDPOINTS =============
