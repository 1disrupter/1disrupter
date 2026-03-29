"""
AlphaAI WebSocket Strategy Alerts Tests
Tests for real-time WebSocket alerts feature including:
- Demo mode WebSocket connection and mock alert streaming
- Free user upgrade_required message and 4003 close code
- Pro user successful connection
- REST endpoints for alerts status and test broadcast
"""
import pytest
import requests
import asyncio
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
WS_URL = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")

# Test credentials
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"


class TestAlertsRESTEndpoints:
    """Tests for REST endpoints related to alerts"""
    
    def test_alerts_status_returns_connection_stats(self):
        """GET /api/alerts/status returns connection statistics"""
        response = requests.get(f"{BASE_URL}/api/alerts/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "active"
        assert "connections" in data
        assert "pro_connections" in data["connections"]
        assert "demo_connections" in data["connections"]
        assert "total" in data["connections"]
        print(f"✓ Alerts status: {data}")
    
    def test_alerts_test_broadcasts_alert(self):
        """POST /api/alerts/test broadcasts a test alert and returns alert payload"""
        response = requests.post(f"{BASE_URL}/api/alerts/test")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "alert" in data
        alert = data["alert"]
        
        # Verify alert structure
        assert alert["type"] == "strategy_alert"
        assert "strategy_id" in alert
        assert "strategy_name" in alert
        assert "asset" in alert
        assert "action" in alert
        assert "message" in alert
        assert "confidence" in alert
        assert "price" in alert
        assert "timestamp" in alert
        assert alert.get("test") is True
        
        assert "broadcast_to" in data
        print(f"✓ Test alert broadcast: {alert['action']} - {alert['strategy_name']}")


class TestWebSocketDemoMode:
    """Tests for WebSocket demo mode connections"""
    
    @pytest.mark.asyncio
    async def test_demo_websocket_connects_and_receives_connected_event(self):
        """WebSocket /api/ws/alerts/demo-{id} connects and sends 'connected' event"""
        try:
            import websockets
        except ImportError:
            pytest.skip("websockets library not installed")
        
        ws_url = f"{WS_URL}/api/ws/alerts/demo-test123"
        
        async with websockets.connect(ws_url, open_timeout=30) as ws:
            # Should receive connected event first
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            
            assert data["type"] == "connected"
            assert data["mode"] == "demo"
            assert "message" in data
            assert "timestamp" in data
            print(f"✓ Demo WebSocket connected: {data['message']}")
    
    @pytest.mark.asyncio
    async def test_demo_websocket_streams_mock_alerts(self):
        """WebSocket /api/ws/alerts/demo-{id} streams mock 'strategy_alert' events every 10-20 seconds"""
        try:
            import websockets
        except ImportError:
            pytest.skip("websockets library not installed")
        
        ws_url = f"{WS_URL}/api/ws/alerts/demo-stream-test"
        
        async with websockets.connect(ws_url, open_timeout=30) as ws:
            # First message is connected event
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            assert data["type"] == "connected"
            
            # Wait for first mock alert (should come within 10-20 seconds)
            msg = await asyncio.wait_for(ws.recv(), timeout=25)
            alert = json.loads(msg)
            
            assert alert["type"] == "strategy_alert"
            assert "strategy_id" in alert
            assert "strategy_name" in alert
            assert "asset" in alert
            assert alert["action"] in ["LONG", "SHORT", "CLOSE", "TAKE_PROFIT", "STOP_LOSS"]
            assert "message" in alert
            assert "confidence" in alert
            assert "price" in alert
            assert "timestamp" in alert
            print(f"✓ Demo alert received: {alert['action']} - {alert['strategy_name']} at ${alert['price']}")


class TestWebSocketFreeUser:
    """Tests for WebSocket free user behavior"""
    
    @pytest.mark.asyncio
    async def test_free_user_websocket_sends_upgrade_required_and_closes(self):
        """WebSocket /api/ws/alerts/{user_id}:free sends 'upgrade_required' message then closes with code 4003"""
        try:
            import websockets
        except ImportError:
            pytest.skip("websockets library not installed")
        
        ws_url = f"{WS_URL}/api/ws/alerts/someuser:free"
        
        try:
            async with websockets.connect(ws_url, open_timeout=30) as ws:
                # Should receive upgrade_required message
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(msg)
                
                assert data["type"] == "upgrade_required"
                assert "message" in data
                assert "Pro" in data["message"] or "upgrade" in data["message"].lower()
                print(f"✓ Free user received upgrade message: {data['message']}")
                
                # Connection should close with code 4003
                try:
                    await asyncio.wait_for(ws.recv(), timeout=2)
                except websockets.exceptions.ConnectionClosed as e:
                    assert e.code == 4003
                    print(f"✓ Free user connection closed with code 4003")
        except websockets.exceptions.ConnectionClosed as e:
            # Connection closed immediately after upgrade message
            assert e.code == 4003
            print(f"✓ Free user connection closed with code 4003")


class TestWebSocketProUser:
    """Tests for WebSocket pro user behavior"""
    
    @pytest.mark.asyncio
    async def test_pro_user_websocket_connects_successfully(self):
        """WebSocket /api/ws/alerts/{user_id}:pro connects successfully and sends 'connected' event with mode='pro'"""
        try:
            import websockets
        except ImportError:
            pytest.skip("websockets library not installed")
        
        ws_url = f"{WS_URL}/api/ws/alerts/testuser123:pro"
        
        async with websockets.connect(ws_url, open_timeout=30) as ws:
            # Should receive connected event
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            
            assert data["type"] == "connected"
            assert data["mode"] == "pro"
            assert "user_id" in data
            assert data["user_id"] == "testuser123"
            assert "message" in data
            assert "timestamp" in data
            print(f"✓ Pro user WebSocket connected: {data['message']}")
    
    @pytest.mark.asyncio
    async def test_elite_user_websocket_connects_successfully(self):
        """WebSocket /api/ws/alerts/{user_id}:elite connects successfully"""
        try:
            import websockets
        except ImportError:
            pytest.skip("websockets library not installed")
        
        ws_url = f"{WS_URL}/api/ws/alerts/eliteuser:elite"
        
        async with websockets.connect(ws_url, open_timeout=30) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            
            assert data["type"] == "connected"
            assert data["mode"] == "elite"
            print(f"✓ Elite user WebSocket connected: {data['message']}")


class TestWebSocketInvalidFormat:
    """Tests for invalid WebSocket client_id formats"""
    
    @pytest.mark.asyncio
    async def test_invalid_client_id_format_closes_connection(self):
        """WebSocket with invalid client_id format closes connection (HTTP 403 or code 4000)"""
        try:
            import websockets
            from websockets.exceptions import InvalidStatus
        except ImportError:
            pytest.skip("websockets library not installed")
        
        ws_url = f"{WS_URL}/api/ws/alerts/invalidformat"
        
        try:
            async with websockets.connect(ws_url, open_timeout=30) as ws:
                await asyncio.wait_for(ws.recv(), timeout=5)
        except InvalidStatus as e:
            # Server rejects connection before WebSocket handshake completes
            assert e.response.status_code in [403, 400]
            print(f"✓ Invalid format connection rejected with HTTP {e.response.status_code}")
        except websockets.exceptions.ConnectionClosed as e:
            assert e.code == 4000
            print(f"✓ Invalid format connection closed with code 4000")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
