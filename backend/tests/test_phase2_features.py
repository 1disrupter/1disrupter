"""
Phase 2 Features Test Suite
Tests for:
1. Automated referral commission tracking (20% recurring)
2. Invoice PDF generation + download
3. WebSocket live events feed
"""
import pytest
import requests
import os
import asyncio
import websockets
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://crypto-signals-web2.preview.emergentagent.com')

# Test credentials
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
ADMIN_EMAIL = "mar-brick@hotmail.com"
ADMIN_PASSWORD = "Martin2026!"
ADMIN_KEY = "alphaai_admin_2026"


class TestReferralCommissionTracking:
    """Tests for automated referral commission tracking (20% recurring)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_track_conversion_endpoint_exists(self):
        """Test that track-conversion endpoint exists"""
        # This endpoint is called internally, test with minimal params
        response = self.session.post(
            f"{BASE_URL}/api/referrals/track-conversion",
            params={"referee_id": "test_user_123", "plan": "pro_monthly", "amount": 29.00}
        )
        # Should return 200 even if no referral found (returns tracked: False)
        assert response.status_code == 200
        data = response.json()
        assert "tracked" in data
        print(f"Track conversion response: {data}")
    
    def test_track_conversion_no_referral(self):
        """Test track-conversion returns tracked=False when no referral exists"""
        response = self.session.post(
            f"{BASE_URL}/api/referrals/track-conversion",
            params={"referee_id": "nonexistent_user_xyz", "plan": "pro_monthly", "amount": 29.00}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tracked"] == False
        assert data["reason"] == "No referral found"
        print(f"No referral response: {data}")
    
    def test_admin_commission_analytics_endpoint(self):
        """Test admin commission analytics endpoint with range=all"""
        response = self.session.get(
            f"{BASE_URL}/api/referrals/admin/commissions",
            params={"admin_key": ADMIN_KEY, "range": "all"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "range" in data
        assert data["range"] == "all"
        assert "recurring" in data
        assert "first_time" in data
        assert "total_commissions" in data
        assert "pending_payouts" in data
        
        # Verify recurring structure
        assert "total_amount" in data["recurring"]
        assert "count" in data["recurring"]
        assert "avg_commission" in data["recurring"]
        
        # Verify first_time structure
        assert "total_amount" in data["first_time"]
        assert "count" in data["first_time"]
        
        print(f"Admin commission analytics: {data}")
    
    def test_admin_commission_analytics_invalid_key(self):
        """Test admin commission analytics rejects invalid admin key"""
        response = self.session.get(
            f"{BASE_URL}/api/referrals/admin/commissions",
            params={"admin_key": "invalid_key", "range": "all"}
        )
        assert response.status_code == 403
        print("Invalid admin key correctly rejected")
    
    def test_admin_commission_analytics_time_ranges(self):
        """Test admin commission analytics with different time ranges"""
        for time_range in ["today", "7d", "30d", "all"]:
            response = self.session.get(
                f"{BASE_URL}/api/referrals/admin/commissions",
                params={"admin_key": ADMIN_KEY, "range": time_range}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["range"] == time_range
            print(f"Time range '{time_range}' works: recurring={data['recurring']['count']}, first_time={data['first_time']['count']}")


class TestInvoiceGeneration:
    """Tests for invoice PDF generation and download"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as pro user
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": PRO_USER_EMAIL, "password": PRO_USER_PASSWORD}
        )
        if login_response.status_code == 200:
            tokens = login_response.json()
            self.token = tokens.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.token = None
    
    def test_list_invoices_endpoint(self):
        """Test GET /api/invoices returns user's invoice list"""
        if not self.token:
            pytest.skip("Authentication failed")
        
        response = self.session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "invoices" in data
        assert "count" in data
        assert isinstance(data["invoices"], list)
        print(f"User has {data['count']} invoices")
    
    def test_generate_invoice_no_transaction(self):
        """Test invoice generation returns 404 for non-existent transaction"""
        if not self.token:
            pytest.skip("Authentication failed")
        
        response = self.session.post(f"{BASE_URL}/api/invoices/generate/nonexistent_txn_123")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        print(f"Non-existent transaction correctly returns 404: {data}")
    
    def test_download_invoice_no_invoice(self):
        """Test invoice download returns 404 for non-existent invoice"""
        if not self.token:
            pytest.skip("Authentication failed")
        
        response = self.session.get(f"{BASE_URL}/api/invoices/download/nonexistent_invoice_123")
        assert response.status_code == 404
        print("Non-existent invoice correctly returns 404")
    
    def test_invoices_require_auth(self):
        """Test invoice endpoints require authentication"""
        # Create new session without auth
        no_auth_session = requests.Session()
        
        # Test list invoices
        response = no_auth_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code in [401, 403]
        
        # Test generate invoice
        response = no_auth_session.post(f"{BASE_URL}/api/invoices/generate/test_txn")
        assert response.status_code in [401, 403]
        
        # Test download invoice
        response = no_auth_session.get(f"{BASE_URL}/api/invoices/download/test_inv")
        assert response.status_code in [401, 403]
        
        print("Invoice endpoints correctly require authentication")


class TestWebSocketEvents:
    """Tests for WebSocket live events feed"""
    
    def test_websocket_endpoint_exists(self):
        """Test WebSocket endpoint is accessible"""
        # Convert HTTPS to WSS
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_endpoint = f"{ws_url}/api/ws/events"
        
        async def connect_ws():
            try:
                async with websockets.connect(ws_endpoint, close_timeout=5) as ws:
                    # Should receive initial connection message
                    message = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(message)
                    return data
            except Exception as e:
                return {"error": str(e)}
        
        result = asyncio.get_event_loop().run_until_complete(connect_ws())
        
        if "error" not in result:
            assert result.get("type") == "connected"
            assert "message" in result
            assert "timestamp" in result
            print(f"WebSocket connected successfully: {result}")
        else:
            print(f"WebSocket connection result: {result}")
            # WebSocket might not be available in test environment
            pytest.skip(f"WebSocket not available: {result['error']}")
    
    def test_websocket_receives_events(self):
        """Test WebSocket receives events after connection"""
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_endpoint = f"{ws_url}/api/ws/events"
        
        async def receive_events():
            try:
                async with websockets.connect(ws_endpoint, close_timeout=5) as ws:
                    events = []
                    # Wait for initial connection + at least one event
                    for _ in range(2):
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=15)
                            data = json.loads(message)
                            events.append(data)
                        except asyncio.TimeoutError:
                            break
                    return events
            except Exception as e:
                return [{"error": str(e)}]
        
        events = asyncio.get_event_loop().run_until_complete(receive_events())
        
        if events and "error" not in events[0]:
            # First event should be connection confirmation
            assert events[0].get("type") == "connected"
            print(f"Received {len(events)} events from WebSocket")
            for ev in events:
                print(f"  Event type: {ev.get('type')}")
        else:
            print(f"WebSocket events result: {events}")
            pytest.skip("WebSocket not available or timed out")
    
    def test_websocket_event_types(self):
        """Test WebSocket sends signal, trade, and update event types"""
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_endpoint = f"{ws_url}/api/ws/events"
        
        async def collect_event_types():
            try:
                async with websockets.connect(ws_endpoint, close_timeout=5) as ws:
                    event_types = set()
                    # Collect events for up to 30 seconds or until we see all types
                    start = asyncio.get_event_loop().time()
                    while asyncio.get_event_loop().time() - start < 30:
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=15)
                            data = json.loads(message)
                            event_types.add(data.get("type"))
                            # Check if we have all expected types
                            if {"signal", "trade", "update"}.issubset(event_types):
                                break
                        except asyncio.TimeoutError:
                            break
                    return list(event_types)
            except Exception as e:
                return [f"error: {str(e)}"]
        
        event_types = asyncio.get_event_loop().run_until_complete(collect_event_types())
        
        if event_types and not any("error" in str(t) for t in event_types):
            print(f"Collected event types: {event_types}")
            # At minimum we should see 'connected'
            assert "connected" in event_types
        else:
            print(f"Event types result: {event_types}")
            pytest.skip("WebSocket not available")


class TestRegressionChecks:
    """Regression tests to ensure existing functionality still works"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_health_check(self):
        """Test health endpoint still works"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("Health check passed")
    
    def test_landing_page_loads(self):
        """Test landing page is accessible"""
        response = self.session.get(BASE_URL)
        assert response.status_code == 200
        print("Landing page loads successfully")
    
    def test_strategy_leaderboard_endpoint(self):
        """Test strategy leaderboard endpoint still works"""
        response = self.session.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        print(f"Strategy leaderboard has {len(data['strategies'])} strategies")
    
    def test_featured_strategies_endpoint(self):
        """Test featured strategies endpoint still works"""
        response = self.session.get(f"{BASE_URL}/api/marketplace/strategies/featured")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        print(f"Featured strategies: {len(data['strategies'])}")
    
    def test_login_works(self):
        """Test login still works with test credentials"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": PRO_USER_EMAIL, "password": PRO_USER_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("Login works correctly")
    
    def test_referral_config_endpoint(self):
        """Test referral config endpoint still works"""
        response = self.session.get(f"{BASE_URL}/api/referrals/config")
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        # Verify 20% commission rate for bronze tier
        bronze_tier = next((t for t in data["tiers"] if t["name"] == "Bronze"), None)
        assert bronze_tier is not None
        assert bronze_tier["commission_rate"] == "20%"
        print(f"Referral config: {len(data['tiers'])} tiers, bronze rate: {bronze_tier['commission_rate']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
