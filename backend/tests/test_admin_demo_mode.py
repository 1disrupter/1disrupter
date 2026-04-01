"""
Admin Demo Mode & Analytics Tests
Tests for demo mode toggle and analytics-summary endpoints.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_KEY = "alphaai_admin_2026"


class TestDemoModeEndpoints:
    """Tests for GET/POST /api/admin/demo-mode"""

    def test_get_demo_mode_returns_status(self):
        """GET /api/admin/demo-mode returns current demo mode status"""
        response = requests.get(f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "demo_mode" in data, "Response should contain 'demo_mode' key"
        assert isinstance(data["demo_mode"], bool), "demo_mode should be a boolean"
        print(f"✓ GET /api/admin/demo-mode: demo_mode={data['demo_mode']}")

    def test_get_demo_mode_requires_admin_key(self):
        """GET /api/admin/demo-mode requires valid admin key"""
        response = requests.get(f"{BASE_URL}/api/admin/demo-mode?admin_key=invalid_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ GET /api/admin/demo-mode rejects invalid admin key")

    def test_toggle_demo_mode_on(self):
        """POST /api/admin/demo-mode can enable demo mode"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["demo_mode"] == True, "demo_mode should be True after enabling"
        assert "message" in data, "Response should contain message"
        print(f"✓ POST /api/admin/demo-mode enabled: {data['message']}")

    def test_toggle_demo_mode_off(self):
        """POST /api/admin/demo-mode can disable demo mode"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["demo_mode"] == False, "demo_mode should be False after disabling"
        print(f"✓ POST /api/admin/demo-mode disabled: {data['message']}")

    def test_toggle_demo_mode_requires_admin_key(self):
        """POST /api/admin/demo-mode requires valid admin key"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key=wrong_key",
            json={"enabled": True}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ POST /api/admin/demo-mode rejects invalid admin key")


class TestAnalyticsSummaryEndpoints:
    """Tests for GET /api/admin/analytics-summary"""

    def test_analytics_summary_demo_mode_on(self):
        """GET /api/admin/analytics-summary returns synthetic data when demo mode is on"""
        # First enable demo mode
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        
        response = requests.get(f"{BASE_URL}/api/admin/analytics-summary?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify demo mode flag
        assert data.get("demo_mode") == True, "demo_mode should be True"
        assert data.get("source") == "synthetic", "source should be 'synthetic'"
        
        # Verify all analytics categories exist
        assert "page_views" in data, "Should have page_views"
        assert "api_calls" in data, "Should have api_calls"
        assert "ws_connections" in data, "Should have ws_connections"
        assert "strategy_interactions" in data, "Should have strategy_interactions"
        assert "checkout_events" in data, "Should have checkout_events"
        
        # Verify page_views structure
        pv = data["page_views"]
        assert "today" in pv and "week" in pv and "month" in pv
        assert pv["today"] > 0, "Synthetic data should have non-zero page views"
        
        print(f"✓ GET /api/admin/analytics-summary (demo mode ON): source={data['source']}, page_views.today={pv['today']}")

    def test_analytics_summary_demo_mode_off(self):
        """GET /api/admin/analytics-summary returns real data when demo mode is off"""
        # First disable demo mode
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        
        response = requests.get(f"{BASE_URL}/api/admin/analytics-summary?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify demo mode flag
        assert data.get("demo_mode") == False, "demo_mode should be False"
        assert data.get("source") == "real", "source should be 'real'"
        
        # Verify all analytics categories exist
        assert "page_views" in data, "Should have page_views"
        assert "api_calls" in data, "Should have api_calls"
        assert "ws_connections" in data, "Should have ws_connections"
        assert "strategy_interactions" in data, "Should have strategy_interactions"
        assert "checkout_events" in data, "Should have checkout_events"
        
        print(f"✓ GET /api/admin/analytics-summary (demo mode OFF): source={data['source']}")

    def test_analytics_summary_requires_admin_key(self):
        """GET /api/admin/analytics-summary requires valid admin key"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-summary?admin_key=bad_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ GET /api/admin/analytics-summary rejects invalid admin key")


class TestTrackEndpoint:
    """Tests for POST /api/admin/track"""

    def test_track_event_records_event(self):
        """POST /api/admin/track records an analytics event"""
        response = requests.post(
            f"{BASE_URL}/api/admin/track",
            json={
                "event_type": "page_view",
                "metadata": {"path": "/test-page", "referrer": "test"}
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("tracked") == True, "tracked should be True"
        assert "demo_mode" in data, "Response should include demo_mode status"
        print(f"✓ POST /api/admin/track: tracked={data['tracked']}, demo_mode={data['demo_mode']}")

    def test_track_event_with_different_types(self):
        """POST /api/admin/track accepts different event types"""
        event_types = ["api_call", "ws_connect", "strategy_view", "checkout_initiated"]
        for event_type in event_types:
            response = requests.post(
                f"{BASE_URL}/api/admin/track",
                json={"event_type": event_type, "metadata": {"test": True}}
            )
            assert response.status_code == 200, f"Failed for event_type={event_type}: {response.text}"
        print(f"✓ POST /api/admin/track accepts multiple event types: {event_types}")


class TestDemoModeTogglePersistence:
    """Tests for demo mode toggle persistence"""

    def test_demo_mode_toggle_persists(self):
        """Demo mode toggle persists across requests"""
        # Enable demo mode
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        
        # Verify it's enabled
        response = requests.get(f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}")
        assert response.json()["demo_mode"] == True, "Demo mode should be enabled"
        
        # Disable demo mode
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        
        # Verify it's disabled
        response = requests.get(f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}")
        assert response.json()["demo_mode"] == False, "Demo mode should be disabled"
        
        # Re-enable for default state
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        
        print("✓ Demo mode toggle persists correctly across requests")


# Cleanup: Ensure demo mode is ON after tests
@pytest.fixture(scope="module", autouse=True)
def cleanup_demo_mode():
    yield
    # Re-enable demo mode after all tests
    requests.post(
        f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
        json={"enabled": True}
    )
