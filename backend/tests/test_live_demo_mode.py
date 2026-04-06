"""
Test LIVE/DEMO Mode System - Backend API Tests
Tests the mode switching functionality and mode-aware data routing across all endpoints.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_KEY = "alphaai_admin_2026"

class TestSystemModeEndpoints:
    """Tests for GET/POST /api/system/mode - Single source of truth"""
    
    def test_get_system_mode_returns_valid_mode(self):
        """GET /api/system/mode should return { mode: 'live' | 'demo' }"""
        response = requests.get(f"{BASE_URL}/api/system/mode")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "mode" in data, "Response should contain 'mode' field"
        assert data["mode"] in ("live", "demo"), f"Mode should be 'live' or 'demo', got {data['mode']}"
        print(f"✓ GET /api/system/mode returns valid mode: {data['mode']}")
    
    def test_post_system_mode_switches_to_demo(self):
        """POST /api/system/mode with admin_key should switch to demo mode"""
        response = requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "demo"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["mode"] == "demo", f"Expected mode 'demo', got {data['mode']}"
        print(f"✓ POST /api/system/mode switches to DEMO mode")
        
        # Verify the change persisted
        verify = requests.get(f"{BASE_URL}/api/system/mode")
        assert verify.json()["mode"] == "demo", "Mode change did not persist"
        print(f"✓ Mode change persisted correctly")
    
    def test_post_system_mode_switches_to_live(self):
        """POST /api/system/mode with admin_key should switch to live mode"""
        response = requests.post(
            f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}",
            json={"mode": "live"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["mode"] == "live", f"Expected mode 'live', got {data['mode']}"
        print(f"✓ POST /api/system/mode switches to LIVE mode")
    
    def test_post_system_mode_rejects_without_admin_key(self):
        """POST /api/system/mode without admin_key should return 403 or 422"""
        response = requests.post(
            f"{BASE_URL}/api/system/mode",
            json={"mode": "demo"}
        )
        # Should fail - either 403 (forbidden) or 422 (missing required param)
        assert response.status_code in (403, 422), f"Expected 403 or 422, got {response.status_code}"
        print(f"✓ POST /api/system/mode rejects without admin_key (status: {response.status_code})")
    
    def test_post_system_mode_rejects_invalid_admin_key(self):
        """POST /api/system/mode with invalid admin_key should return 403"""
        response = requests.post(
            f"{BASE_URL}/api/system/mode?admin_key=wrong_key",
            json={"mode": "demo"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ POST /api/system/mode rejects invalid admin_key")


class TestAlertsLiveEndpoint:
    """Tests for GET /api/alerts/live - Mode-aware alerts"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Store initial mode and restore after tests"""
        initial = requests.get(f"{BASE_URL}/api/system/mode").json()["mode"]
        yield
        # Restore initial mode
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": initial})
    
    def test_alerts_live_returns_demo_data_in_demo_mode(self):
        """GET /api/alerts/live should return demo data when in DEMO mode"""
        # Switch to demo mode
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "demo"})
        
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "alerts" in data, "Response should contain 'alerts' field"
        assert "mode" in data, "Response should contain 'mode' field"
        assert data["mode"] == "demo", f"Expected mode 'demo', got {data['mode']}"
        
        # Check that alerts have is_demo flag
        if data["alerts"]:
            for alert in data["alerts"]:
                assert alert.get("is_demo") == True, "Demo alerts should have is_demo=True"
        print(f"✓ GET /api/alerts/live returns demo data in DEMO mode ({len(data['alerts'])} alerts)")
    
    def test_alerts_live_returns_real_data_in_live_mode(self):
        """GET /api/alerts/live should return real data when in LIVE mode"""
        # Switch to live mode
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "live"})
        
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "alerts" in data, "Response should contain 'alerts' field"
        assert "mode" in data, "Response should contain 'mode' field"
        assert data["mode"] == "live", f"Expected mode 'live', got {data['mode']}"
        
        # In live mode, alerts should NOT have is_demo=True
        if data["alerts"]:
            for alert in data["alerts"]:
                assert alert.get("is_demo") != True, "Live alerts should not have is_demo=True"
        print(f"✓ GET /api/alerts/live returns real data in LIVE mode ({len(data['alerts'])} alerts)")


class TestEventsLiveEndpoint:
    """Tests for GET /api/events/live - Mode-aware events"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Store initial mode and restore after tests"""
        initial = requests.get(f"{BASE_URL}/api/system/mode").json()["mode"]
        yield
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": initial})
    
    def test_events_live_returns_demo_data_in_demo_mode(self):
        """GET /api/events/live should return demo data when in DEMO mode"""
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "demo"})
        
        response = requests.get(f"{BASE_URL}/api/events/live?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "events" in data, "Response should contain 'events' field"
        assert "mode" in data, "Response should contain 'mode' field"
        assert data["mode"] == "demo", f"Expected mode 'demo', got {data['mode']}"
        
        if data["events"]:
            for event in data["events"]:
                assert event.get("is_demo") == True, "Demo events should have is_demo=True"
        print(f"✓ GET /api/events/live returns demo data in DEMO mode ({len(data['events'])} events)")
    
    def test_events_live_returns_real_data_in_live_mode(self):
        """GET /api/events/live should return real data when in LIVE mode"""
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "live"})
        
        response = requests.get(f"{BASE_URL}/api/events/live?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "events" in data, "Response should contain 'events' field"
        assert "mode" in data, "Response should contain 'mode' field"
        assert data["mode"] == "live", f"Expected mode 'live', got {data['mode']}"
        print(f"✓ GET /api/events/live returns real data in LIVE mode ({len(data['events'])} events)")


class TestAgentsPerformanceEndpoint:
    """Tests for GET /api/agents/performance - Mode-aware agent stats"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Store initial mode and restore after tests"""
        initial = requests.get(f"{BASE_URL}/api/system/mode").json()["mode"]
        yield
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": initial})
    
    def test_agents_performance_returns_demo_data_in_demo_mode(self):
        """GET /api/agents/performance should return demo data with is_demo=true in DEMO mode"""
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "demo"})
        
        response = requests.get(f"{BASE_URL}/api/agents/performance")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "agents" in data, "Response should contain 'agents' field"
        assert "mode" in data, "Response should contain 'mode' field"
        assert data["mode"] == "demo", f"Expected mode 'demo', got {data['mode']}"
        
        if data["agents"]:
            for agent in data["agents"]:
                assert agent.get("is_demo") == True, "Demo agents should have is_demo=True"
        print(f"✓ GET /api/agents/performance returns demo data in DEMO mode ({len(data['agents'])} agents)")
    
    def test_agents_performance_returns_real_data_in_live_mode(self):
        """GET /api/agents/performance should return real data in LIVE mode"""
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "live"})
        
        response = requests.get(f"{BASE_URL}/api/agents/performance")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "agents" in data, "Response should contain 'agents' field"
        assert "mode" in data, "Response should contain 'mode' field"
        assert data["mode"] == "live", f"Expected mode 'live', got {data['mode']}"
        print(f"✓ GET /api/agents/performance returns real data in LIVE mode ({len(data['agents'])} agents)")


class TestAnalyticsSummaryEndpoint:
    """Tests for GET /api/analytics/summary - Mode-aware analytics"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Store initial mode and restore after tests"""
        initial = requests.get(f"{BASE_URL}/api/system/mode").json()["mode"]
        yield
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": initial})
    
    def test_analytics_summary_returns_demo_data_in_demo_mode(self):
        """GET /api/analytics/summary should return demo data in DEMO mode"""
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "demo"})
        
        response = requests.get(f"{BASE_URL}/api/analytics/summary?days=7")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "demo_mode" in data, "Response should contain 'demo_mode' field"
        assert data["demo_mode"] == True, f"Expected demo_mode=True, got {data['demo_mode']}"
        assert "total_signals" in data or "total_conversions" in data, "Response should contain signal/conversion data"
        print(f"✓ GET /api/analytics/summary returns demo data in DEMO mode")
    
    def test_analytics_summary_returns_real_data_in_live_mode(self):
        """GET /api/analytics/summary should return real signal data in LIVE mode"""
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "live"})
        
        response = requests.get(f"{BASE_URL}/api/analytics/summary?days=7")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # In live mode, demo_mode should be False or not present
        assert data.get("demo_mode") != True, "Live mode should not have demo_mode=True"
        print(f"✓ GET /api/analytics/summary returns real data in LIVE mode")


class TestModeConsistencyAcrossEndpoints:
    """Tests to verify mode consistency across all endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Store initial mode and restore after tests"""
        initial = requests.get(f"{BASE_URL}/api/system/mode").json()["mode"]
        yield
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": initial})
    
    def test_all_endpoints_respect_demo_mode(self):
        """All mode-aware endpoints should return demo data when in DEMO mode"""
        # Switch to demo mode
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "demo"})
        
        # Test all endpoints
        endpoints = [
            ("/api/alerts/live", "mode", "demo"),
            ("/api/events/live", "mode", "demo"),
            ("/api/agents/performance", "mode", "demo"),
            ("/api/analytics/summary", "demo_mode", True),
        ]
        
        for endpoint, field, expected in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} failed with {response.status_code}"
            data = response.json()
            actual = data.get(field)
            assert actual == expected, f"{endpoint}: expected {field}={expected}, got {actual}"
            print(f"✓ {endpoint} respects DEMO mode")
    
    def test_all_endpoints_respect_live_mode(self):
        """All mode-aware endpoints should return live data when in LIVE mode"""
        # Switch to live mode
        requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "live"})
        
        # Test all endpoints
        endpoints = [
            ("/api/alerts/live", "mode", "live"),
            ("/api/events/live", "mode", "live"),
            ("/api/agents/performance", "mode", "live"),
        ]
        
        for endpoint, field, expected in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} failed with {response.status_code}"
            data = response.json()
            actual = data.get(field)
            assert actual == expected, f"{endpoint}: expected {field}={expected}, got {actual}"
            print(f"✓ {endpoint} respects LIVE mode")


# Cleanup: Ensure we end in LIVE mode
@pytest.fixture(scope="session", autouse=True)
def cleanup_after_all_tests():
    """Ensure system is in LIVE mode after all tests complete"""
    yield
    requests.post(f"{BASE_URL}/api/system/mode?admin_key={ADMIN_KEY}", json={"mode": "live"})
    print("\n✓ System restored to LIVE mode after tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
