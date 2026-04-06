"""
Test Live Signals Page Feature
Tests the new /api/alerts/live endpoint and mode-aware behavior
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_KEY = "alphaai_admin_2026"


class TestLiveSignalsAPI:
    """Tests for GET /api/alerts/live endpoint"""

    def test_get_live_alerts_returns_200(self):
        """GET /api/alerts/live should return 200"""
        response = requests.get(f"{BASE_URL}/api/alerts/live")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "mode" in data
        assert "count" in data
        print(f"✓ GET /api/alerts/live returned {data['count']} alerts in {data['mode']} mode")

    def test_get_live_alerts_with_limit(self):
        """GET /api/alerts/live?limit=5 should respect limit parameter"""
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) <= 5
        print(f"✓ Limit parameter respected: got {len(data['alerts'])} alerts")

    def test_live_alerts_structure(self):
        """Verify alert object structure"""
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=1")
        assert response.status_code == 200
        data = response.json()
        
        if data["alerts"]:
            alert = data["alerts"][0]
            # Check required fields
            assert "action" in alert, "Alert missing 'action' field"
            assert "asset" in alert, "Alert missing 'asset' field"
            assert "message" in alert, "Alert missing 'message' field"
            assert "confidence" in alert, "Alert missing 'confidence' field"
            assert "price" in alert, "Alert missing 'price' field"
            assert "strategy_name" in alert, "Alert missing 'strategy_name' field"
            assert "timestamp" in alert, "Alert missing 'timestamp' field"
            assert "is_demo" in alert, "Alert missing 'is_demo' field"
            
            # Validate action values
            valid_actions = ["LONG", "SHORT", "CLOSE", "TAKE_PROFIT", "STOP_LOSS"]
            assert alert["action"] in valid_actions, f"Invalid action: {alert['action']}"
            
            print(f"✓ Alert structure valid: {alert['action']} {alert['asset']} @ ${alert['price']}")
        else:
            print("⚠ No alerts to validate structure")


class TestLiveSignalsModeAwareness:
    """Tests for mode-aware behavior of /api/alerts/live"""

    @pytest.fixture(autouse=True)
    def restore_live_mode(self):
        """Ensure system is in LIVE mode after each test"""
        yield
        # Restore to LIVE mode
        requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "live"}
        )

    def test_live_mode_returns_real_data(self):
        """In LIVE mode, alerts should have is_demo=false"""
        # Ensure LIVE mode
        requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "live"}
        )
        
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert data["mode"] == "live", f"Expected mode 'live', got '{data['mode']}'"
        
        if data["alerts"]:
            for alert in data["alerts"]:
                assert alert["is_demo"] == False, "Alert should have is_demo=false in LIVE mode"
        
        print(f"✓ LIVE mode: {data['count']} real alerts returned")

    def test_demo_mode_returns_demo_data(self):
        """In DEMO mode, alerts should have is_demo=true"""
        # Switch to DEMO mode
        switch_response = requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "demo"}
        )
        assert switch_response.status_code == 200
        
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert data["mode"] == "demo", f"Expected mode 'demo', got '{data['mode']}'"
        
        if data["alerts"]:
            for alert in data["alerts"]:
                assert alert["is_demo"] == True, "Alert should have is_demo=true in DEMO mode"
        
        print(f"✓ DEMO mode: {data['count']} demo alerts returned")


class TestSystemModeEndpoint:
    """Tests for /api/system/mode endpoint"""

    @pytest.fixture(autouse=True)
    def restore_live_mode(self):
        """Ensure system is in LIVE mode after each test"""
        yield
        requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "live"}
        )

    def test_get_system_mode(self):
        """GET /api/system/mode should return current mode"""
        response = requests.get(f"{BASE_URL}/api/system/mode")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["live", "demo"]
        print(f"✓ Current system mode: {data['mode']}")

    def test_set_system_mode_requires_admin_key(self):
        """POST /api/system/mode without admin_key should fail"""
        response = requests.post(
            f"{BASE_URL}/api/system/mode",
            json={"mode": "demo"}
        )
        assert response.status_code == 422  # Missing required query param
        print("✓ Admin key required for mode switch")

    def test_set_system_mode_rejects_invalid_key(self):
        """POST /api/system/mode with wrong admin_key should fail"""
        response = requests.post(
            f"{BASE_URL}/api/system/mode?admin_key=wrong_key",
            json={"mode": "demo"}
        )
        assert response.status_code == 403
        print("✓ Invalid admin key rejected")

    def test_set_system_mode_to_demo(self):
        """POST /api/system/mode can switch to demo"""
        response = requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "demo"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "demo"
        
        # Verify mode changed
        verify = requests.get(f"{BASE_URL}/api/system/mode")
        assert verify.json()["mode"] == "demo"
        print("✓ System mode switched to DEMO")

    def test_set_system_mode_to_live(self):
        """POST /api/system/mode can switch to live"""
        # First switch to demo
        requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "demo"}
        )
        
        # Then switch back to live
        response = requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "live"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "live"
        
        # Verify mode changed
        verify = requests.get(f"{BASE_URL}/api/system/mode")
        assert verify.json()["mode"] == "live"
        print("✓ System mode switched to LIVE")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
