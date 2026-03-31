"""
Admin WebSocket Event Streaming Tests
Tests for WebSocket /api/ws/admin/events and GET /api/admin/traffic/stream-status
"""
import pytest
import requests
import asyncio
import websockets
from websockets.exceptions import InvalidStatus
import json
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://alpha-ai-preview.preview.emergentagent.com')
WS_BASE_URL = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
ADMIN_KEY = "alphaai_admin_2026"
WRONG_ADMIN_KEY = "wrong_key_123"


class TestStreamStatusEndpoint:
    """Tests for GET /api/admin/traffic/stream-status"""
    
    def test_stream_status_with_valid_admin_key(self):
        """GET /api/admin/traffic/stream-status returns connection stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/stream-status",
            params={"admin_key": ADMIN_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "status" in data
        assert "connections" in data
        assert data["status"] == "active"
        
        # Verify connections structure
        connections = data["connections"]
        assert "admin_connections" in connections
        assert "demo_only" in connections
        assert isinstance(connections["admin_connections"], int)
        assert isinstance(connections["demo_only"], int)
    
    def test_stream_status_with_wrong_admin_key(self):
        """GET /api/admin/traffic/stream-status returns 403 with wrong admin_key"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/stream-status",
            params={"admin_key": WRONG_ADMIN_KEY}
        )
        assert response.status_code == 403
        assert "Admin access denied" in response.json()["detail"]


class TestWebSocketConnection:
    """Tests for WebSocket /api/ws/admin/events connection"""
    
    @pytest.mark.asyncio
    async def test_ws_connect_with_valid_admin_key(self):
        """WebSocket connects with valid admin_key and sends 'connected' message"""
        ws_url = f"{WS_BASE_URL}/api/ws/admin/events?admin_key={ADMIN_KEY}"
        
        async with websockets.connect(ws_url, open_timeout=15) as ws:
            # Should receive connected message
            message = await asyncio.wait_for(ws.recv(), timeout=10)
            data = json.loads(message)
            
            assert data["type"] == "connected"
            assert "conn_id" in data
            assert "message" in data
            assert "timestamp" in data
            assert data["demo_only"] is False
            assert "Connected to admin event stream" in data["message"]
    
    @pytest.mark.asyncio
    async def test_ws_connect_with_demo_only_filter(self):
        """WebSocket connects with demo_only=true filter"""
        ws_url = f"{WS_BASE_URL}/api/ws/admin/events?admin_key={ADMIN_KEY}&demo_only=true"
        
        async with websockets.connect(ws_url, open_timeout=15) as ws:
            message = await asyncio.wait_for(ws.recv(), timeout=10)
            data = json.loads(message)
            
            assert data["type"] == "connected"
            assert data["demo_only"] is True
    
    @pytest.mark.asyncio
    async def test_ws_reject_without_admin_key(self):
        """WebSocket rejects connection without admin_key (HTTP 403 or close code 4003)"""
        ws_url = f"{WS_BASE_URL}/api/ws/admin/events"
        
        try:
            async with websockets.connect(ws_url, open_timeout=10) as ws:
                # Should be closed immediately
                await asyncio.wait_for(ws.recv(), timeout=5)
                pytest.fail("Expected connection to be rejected")
        except InvalidStatus as e:
            # Server rejects before WebSocket handshake completes with HTTP 403
            assert e.response.status_code == 403
        except websockets.exceptions.ConnectionClosed as e:
            # Or closes with code 4003 after handshake
            assert e.code == 4003
    
    @pytest.mark.asyncio
    async def test_ws_reject_with_wrong_admin_key(self):
        """WebSocket rejects connection with wrong admin_key (HTTP 403 or close code 4003)"""
        ws_url = f"{WS_BASE_URL}/api/ws/admin/events?admin_key={WRONG_ADMIN_KEY}"
        
        try:
            async with websockets.connect(ws_url, open_timeout=10) as ws:
                await asyncio.wait_for(ws.recv(), timeout=5)
                pytest.fail("Expected connection to be rejected")
        except InvalidStatus as e:
            # Server rejects before WebSocket handshake completes with HTTP 403
            assert e.response.status_code == 403
        except websockets.exceptions.ConnectionClosed as e:
            # Or closes with code 4003 after handshake
            assert e.code == 4003
    
    @pytest.mark.asyncio
    async def test_ws_ping_pong(self):
        """WebSocket responds to ping with pong"""
        ws_url = f"{WS_BASE_URL}/api/ws/admin/events?admin_key={ADMIN_KEY}"
        
        async with websockets.connect(ws_url, open_timeout=15) as ws:
            # Receive connected message first
            await asyncio.wait_for(ws.recv(), timeout=10)
            
            # Send ping
            await ws.send(json.dumps({"action": "ping"}))
            
            # Should receive pong
            message = await asyncio.wait_for(ws.recv(), timeout=10)
            data = json.loads(message)
            
            assert data["type"] == "pong"
            assert "timestamp" in data


class TestWebSocketEventBroadcast:
    """Tests for WebSocket event broadcasting"""
    
    @pytest.mark.asyncio
    async def test_ws_receives_posted_event(self):
        """When POST /api/admin/events creates an event, connected WS client receives it"""
        ws_url = f"{WS_BASE_URL}/api/ws/admin/events?admin_key={ADMIN_KEY}"
        
        async with websockets.connect(ws_url, open_timeout=15) as ws:
            # Receive connected message first
            await asyncio.wait_for(ws.recv(), timeout=10)
            
            # Post an event
            unique_type = f"ws_test_{uuid.uuid4().hex[:8]}"
            post_response = requests.post(
                f"{BASE_URL}/api/admin/events",
                json={"type": unique_type, "metadata": {"test": True, "source": "ws_broadcast_test"}}
            )
            assert post_response.status_code == 200
            event_id = post_response.json()["event_id"]
            
            # Should receive the event via WebSocket (may need to skip other events)
            received_event = None
            for _ in range(10):  # Try up to 10 messages
                message = await asyncio.wait_for(ws.recv(), timeout=10)
                data = json.loads(message)
                if data.get("type") == unique_type:
                    received_event = data
                    break
            
            assert received_event is not None, f"Did not receive event with type {unique_type}"
            assert received_event["id"] == event_id
            assert received_event["metadata"]["test"] is True
            assert received_event["metadata"]["source"] == "ws_broadcast_test"
            assert "timestamp" in received_event
    
    @pytest.mark.asyncio
    async def test_multiple_ws_clients_receive_same_event(self):
        """Multiple admin WS connections receive the same event broadcast"""
        ws_url = f"{WS_BASE_URL}/api/ws/admin/events?admin_key={ADMIN_KEY}"
        
        async with websockets.connect(ws_url, open_timeout=15) as ws1, websockets.connect(ws_url, open_timeout=15) as ws2:
            # Receive connected messages
            await asyncio.wait_for(ws1.recv(), timeout=10)
            await asyncio.wait_for(ws2.recv(), timeout=10)
            
            # Post an event
            unique_type = f"multi_ws_test_{uuid.uuid4().hex[:8]}"
            post_response = requests.post(
                f"{BASE_URL}/api/admin/events",
                json={"type": unique_type, "metadata": {"multi_client": True}}
            )
            assert post_response.status_code == 200
            event_id = post_response.json()["event_id"]
            
            # Both clients should receive the event (may need to skip other events)
            async def find_event(ws, target_type):
                for _ in range(10):
                    message = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(message)
                    if data.get("type") == target_type:
                        return data
                return None
            
            data1 = await find_event(ws1, unique_type)
            data2 = await find_event(ws2, unique_type)
            
            assert data1 is not None, "Client 1 did not receive the event"
            assert data2 is not None, "Client 2 did not receive the event"
            assert data1["id"] == event_id
            assert data2["id"] == event_id
            assert data1["type"] == unique_type
            assert data2["type"] == unique_type
    
    @pytest.mark.asyncio
    async def test_demo_only_filter_receives_demo_events(self):
        """WS client with demo_only=true receives demo events"""
        ws_url_demo = f"{WS_BASE_URL}/api/ws/admin/events?admin_key={ADMIN_KEY}&demo_only=true"
        
        async with websockets.connect(ws_url_demo, open_timeout=15) as ws_demo:
            # Receive connected message
            connected_msg = await asyncio.wait_for(ws_demo.recv(), timeout=10)
            connected_data = json.loads(connected_msg)
            assert connected_data["demo_only"] is True
            
            # Post a demo event
            demo_type = f"demo_filter_test_{uuid.uuid4().hex[:8]}"
            requests.post(
                f"{BASE_URL}/api/admin/events",
                json={"type": demo_type, "metadata": {"demo": True}}
            )
            
            # Demo client should receive the demo event
            received_demo = None
            for _ in range(10):
                message = await asyncio.wait_for(ws_demo.recv(), timeout=10)
                data = json.loads(message)
                if data.get("type") == demo_type:
                    received_demo = data
                    break
            
            assert received_demo is not None, "Demo client did not receive demo event"
            assert received_demo["metadata"]["demo"] is True


class TestPostEventsEndpoint:
    """Tests for POST /api/admin/events (extended tests)"""
    
    def test_post_event_various_types(self):
        """POST /api/admin/events accepts various event types and returns event_id"""
        event_types = [
            "page_view", "api_call", "strategy_view", "follow", "unfollow",
            "signal", "ws_connect", "ws_disconnect", "upgrade_prompt",
            "checkout_start", "checkout_success", "error"
        ]
        
        for event_type in event_types:
            response = requests.post(
                f"{BASE_URL}/api/admin/events",
                json={"type": event_type, "metadata": {"test": True, "source": "type_test"}}
            )
            assert response.status_code == 200, f"Failed for type: {event_type}"
            data = response.json()
            assert data["success"] is True
            assert "event_id" in data
            assert isinstance(data["event_id"], str)
            assert len(data["event_id"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
