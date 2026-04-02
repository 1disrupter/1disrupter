"""
Admin Traffic Analytics API Tests
Tests for POST /api/admin/events, GET /api/admin/traffic/summary, 
GET /api/admin/traffic/timeseries, GET /api/admin/traffic/events
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://alpha-trading-hub.preview.emergentagent.com')
ADMIN_KEY = "alphaai_admin_2026"
WRONG_ADMIN_KEY = "wrong_key_123"


class TestTrafficEventsEndpoint:
    """Tests for POST /api/admin/events"""
    
    def test_post_event_anonymous(self):
        """POST /api/admin/events without auth creates anonymous event"""
        unique_type = f"test_anon_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/admin/events",
            json={"type": unique_type, "metadata": {"test": True, "source": "pytest"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "event_id" in data
        assert isinstance(data["event_id"], str)
        
        # Verify event was created with user_id=null
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": unique_type}
        )
        assert verify_response.status_code == 200
        events = verify_response.json()["events"]
        assert len(events) == 1
        assert events[0]["user_id"] is None
    
    def test_post_event_with_auth(self):
        """POST /api/admin/events with Bearer token sets user_id"""
        # Login to get token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "demo_test2@my-alpha-ai.com", "password": "NewPass1234!"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        unique_type = f"test_auth_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/admin/events",
            json={"type": unique_type, "metadata": {"test": True, "source": "pytest_auth"}},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "event_id" in data
        
        # Verify event was created with correct user_id
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": unique_type}
        )
        assert verify_response.status_code == 200
        events = verify_response.json()["events"]
        assert len(events) == 1
        assert events[0]["user_id"] == user_id
    
    def test_post_event_demo_mode_tagging(self):
        """POST /api/admin/events tags demo mode events with metadata.demo=true"""
        unique_type = f"test_demo_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/admin/events",
            json={"type": unique_type, "metadata": {"demo": True, "path": "/test"}}
        )
        assert response.status_code == 200
        
        # Verify demo flag is preserved
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": unique_type}
        )
        assert verify_response.status_code == 200
        events = verify_response.json()["events"]
        assert len(events) == 1
        assert events[0]["metadata"]["demo"] is True


class TestTrafficSummaryEndpoint:
    """Tests for GET /api/admin/traffic/summary"""
    
    def test_summary_with_valid_admin_key(self):
        """GET /api/admin/traffic/summary returns all metric fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/summary",
            params={"admin_key": ADMIN_KEY, "range": "24h"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "range", "total_events", "unique_users", "page_views", "api_calls",
            "ws_connections", "ws_disconnections", "strategy_views", "follows",
            "unfollows", "signals_delivered", "upgrade_prompts", "checkout_starts",
            "checkout_successes", "errors", "demo_sessions", "avg_latency_ms", "p95_latency_ms"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify range is correct
        assert data["range"] == "24h"
        
        # Verify numeric fields are integers
        assert isinstance(data["total_events"], int)
        assert isinstance(data["unique_users"], int)
        assert isinstance(data["page_views"], int)
    
    def test_summary_with_wrong_admin_key(self):
        """GET /api/admin/traffic/summary returns 403 with wrong admin_key"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/summary",
            params={"admin_key": WRONG_ADMIN_KEY, "range": "24h"}
        )
        assert response.status_code == 403
        assert "Admin access denied" in response.json()["detail"]
    
    def test_summary_different_ranges(self):
        """GET /api/admin/traffic/summary works with different range values"""
        for range_val in ["24h", "7d", "30d"]:
            response = requests.get(
                f"{BASE_URL}/api/admin/traffic/summary",
                params={"admin_key": ADMIN_KEY, "range": range_val}
            )
            assert response.status_code == 200
            assert response.json()["range"] == range_val


class TestTrafficTimeseriesEndpoint:
    """Tests for GET /api/admin/traffic/timeseries"""
    
    def test_timeseries_with_valid_admin_key(self):
        """GET /api/admin/traffic/timeseries returns time-bucketed series"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/timeseries",
            params={"admin_key": ADMIN_KEY, "range": "24h"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "range" in data
        assert "series" in data
        assert data["range"] == "24h"
        assert isinstance(data["series"], list)
        
        # If there are events, verify series structure
        if len(data["series"]) > 0:
            first_bucket = data["series"][0]
            assert "time" in first_bucket
    
    def test_timeseries_with_wrong_admin_key(self):
        """GET /api/admin/traffic/timeseries returns 403 with wrong admin_key"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/timeseries",
            params={"admin_key": WRONG_ADMIN_KEY, "range": "24h"}
        )
        assert response.status_code == 403


class TestTrafficEventsListEndpoint:
    """Tests for GET /api/admin/traffic/events"""
    
    def test_events_with_valid_admin_key(self):
        """GET /api/admin/traffic/events returns paginated events"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "page": 1, "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination fields
        assert "events" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        assert isinstance(data["events"], list)
        assert isinstance(data["total"], int)
        assert data["page"] == 1
        assert data["pages"] >= 1
        
        # Verify event structure if events exist
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "id" in event
            assert "type" in event
            assert "timestamp" in event
            assert "metadata" in event
    
    def test_events_with_type_filter(self):
        """GET /api/admin/traffic/events supports type filter parameter"""
        # First create a specific event type
        unique_type = f"filter_test_{uuid.uuid4().hex[:8]}"
        requests.post(
            f"{BASE_URL}/api/admin/events",
            json={"type": unique_type, "metadata": {"test": True}}
        )
        
        # Filter by that type
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": unique_type}
        )
        assert response.status_code == 200
        data = response.json()
        
        # All returned events should be of the filtered type
        for event in data["events"]:
            assert event["type"] == unique_type
    
    def test_events_with_wrong_admin_key(self):
        """GET /api/admin/traffic/events returns 403 with wrong admin_key"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": WRONG_ADMIN_KEY}
        )
        assert response.status_code == 403
    
    def test_events_pagination(self):
        """GET /api/admin/traffic/events pagination works correctly"""
        # Get first page
        response1 = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "page": 1, "limit": 5}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # If there are multiple pages, verify page 2 is different
        if data1["pages"] > 1:
            response2 = requests.get(
                f"{BASE_URL}/api/admin/traffic/events",
                params={"admin_key": ADMIN_KEY, "page": 2, "limit": 5}
            )
            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["page"] == 2
            
            # Events should be different
            if len(data1["events"]) > 0 and len(data2["events"]) > 0:
                assert data1["events"][0]["id"] != data2["events"][0]["id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
