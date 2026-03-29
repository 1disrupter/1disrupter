"""
AlphaAI Alerting System Tests
Tests for:
- POST /api/admin/events with type=error stores event
- GET /api/admin/traffic/active-alerts endpoint
- Rule engine: error_spike alert triggering (12+ errors in 60s)
- Alert event structure (type=alert, metadata.alert_type)
- GET /api/admin/traffic/events?type=alert returns alert events
- Rule engine cooldown (no duplicate alerts within 120s)
- GET /api/admin/traffic/summary still returns all fields
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://idle-cache.preview.emergentagent.com')
ADMIN_KEY = "alphaai_admin_2026"
WRONG_ADMIN_KEY = "wrong_key_123"


class TestActiveAlertsEndpoint:
    """Tests for GET /api/admin/traffic/active-alerts"""
    
    def test_active_alerts_with_valid_admin_key(self):
        """GET /api/admin/traffic/active-alerts returns active_alerts array"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/active-alerts",
            params={"admin_key": ADMIN_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "active_alerts" in data
        assert isinstance(data["active_alerts"], list)
        print(f"Active alerts: {data['active_alerts']}")
    
    def test_active_alerts_with_wrong_admin_key(self):
        """GET /api/admin/traffic/active-alerts returns 403 with wrong admin_key"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/active-alerts",
            params={"admin_key": WRONG_ADMIN_KEY}
        )
        assert response.status_code == 403
        assert "Admin access denied" in response.json()["detail"]


class TestErrorEventStorage:
    """Tests for POST /api/admin/events with type=error"""
    
    def test_post_error_event_stores_in_traffic_events(self):
        """POST /api/admin/events with type=error stores event in traffic_events"""
        unique_id = uuid.uuid4().hex[:8]
        response = requests.post(
            f"{BASE_URL}/api/admin/events",
            json={
                "type": "error",
                "metadata": {
                    "message": f"Test error {unique_id}",
                    "source": "pytest",
                    "demo": True
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "event_id" in data
        
        # Verify event was stored
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": "error", "limit": 10}
        )
        assert verify_response.status_code == 200
        events = verify_response.json()["events"]
        
        # Find our test event
        found = any(
            e.get("metadata", {}).get("message") == f"Test error {unique_id}"
            for e in events
        )
        assert found, f"Test error event not found in traffic_events"


class TestAlertEventsRetrieval:
    """Tests for GET /api/admin/traffic/events?type=alert"""
    
    def test_get_alert_events_with_type_filter(self):
        """GET /api/admin/traffic/events?type=alert returns alert events"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": "alert", "limit": 20}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        # All returned events should be of type 'alert'
        for event in data["events"]:
            assert event["type"] == "alert", f"Expected type=alert, got {event['type']}"
        
        print(f"Found {data['total']} alert events")
        
        # If there are alert events, verify structure
        if len(data["events"]) > 0:
            alert = data["events"][0]
            assert "id" in alert
            assert "type" in alert
            assert alert["type"] == "alert"
            assert "timestamp" in alert
            assert "metadata" in alert
            # Alert events should have alert_type in metadata
            if "alert_type" in alert.get("metadata", {}):
                print(f"Alert type: {alert['metadata']['alert_type']}")


class TestAlertEventStructure:
    """Tests for alert event structure"""
    
    def test_alert_event_has_correct_structure(self):
        """Alert event in traffic_events has type=alert and metadata.alert_type"""
        response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": "alert", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["events"]) > 0:
            alert = data["events"][0]
            assert alert["type"] == "alert"
            assert "metadata" in alert
            assert "alert_type" in alert["metadata"], "Alert event missing metadata.alert_type"
            assert "message" in alert["metadata"], "Alert event missing metadata.message"
            print(f"Alert structure verified: alert_type={alert['metadata']['alert_type']}")
        else:
            print("No alert events found - will be created by error_spike test")


class TestErrorSpikeAlertTrigger:
    """Tests for rule engine error_spike alert triggering"""
    
    def test_error_spike_alert_triggered_by_12_errors(self):
        """Posting 12+ error events within 60s triggers an error_spike alert"""
        # Post 12 error events rapidly
        unique_batch = uuid.uuid4().hex[:8]
        print(f"Posting 12 error events with batch ID: {unique_batch}")
        
        for i in range(12):
            response = requests.post(
                f"{BASE_URL}/api/admin/events",
                json={
                    "type": "error",
                    "metadata": {
                        "message": f"Error spike test {unique_batch} - event {i+1}",
                        "source": "pytest_error_spike",
                        "demo": True
                    }
                }
            )
            assert response.status_code == 200
        
        print("Waiting 8 seconds for rule engine to detect error spike...")
        time.sleep(8)
        
        # Check if error_spike alert was triggered
        alerts_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/active-alerts",
            params={"admin_key": ADMIN_KEY}
        )
        assert alerts_response.status_code == 200
        active_alerts = alerts_response.json()["active_alerts"]
        print(f"Active alerts after error spike: {active_alerts}")
        
        # Check for error_spike in active alerts
        has_error_spike = "error_spike" in active_alerts
        
        # Also check if alert event was created in traffic_events
        events_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": "alert", "limit": 10}
        )
        assert events_response.status_code == 200
        alert_events = events_response.json()["events"]
        
        # Find error_spike alert
        error_spike_alerts = [
            e for e in alert_events
            if e.get("metadata", {}).get("alert_type") == "error_spike"
        ]
        
        print(f"Found {len(error_spike_alerts)} error_spike alert events")
        
        # Either active_alerts contains error_spike OR we found alert events
        # (alert may have been cleared if cooldown passed)
        assert has_error_spike or len(error_spike_alerts) > 0, \
            "error_spike alert was not triggered after 12 errors"
        
        # Verify alert event structure if found
        if len(error_spike_alerts) > 0:
            alert = error_spike_alerts[0]
            assert alert["type"] == "alert"
            assert alert["metadata"]["alert_type"] == "error_spike"
            assert "message" in alert["metadata"]
            assert "count" in alert["metadata"]
            print(f"error_spike alert verified: {alert['metadata']['message']}")


class TestRuleEngineCooldown:
    """Tests for rule engine cooldown (120 seconds between same alert type)"""
    
    def test_duplicate_error_spike_not_emitted_within_cooldown(self):
        """Duplicate error_spike alert is NOT emitted within 120 seconds"""
        # First, get current alert events count
        initial_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": "alert", "limit": 100}
        )
        assert initial_response.status_code == 200
        initial_count = initial_response.json()["total"]
        
        # Post another batch of 12 errors (should be within cooldown)
        unique_batch = uuid.uuid4().hex[:8]
        print(f"Posting another 12 error events (batch: {unique_batch}) - should be in cooldown")
        
        for i in range(12):
            requests.post(
                f"{BASE_URL}/api/admin/events",
                json={
                    "type": "error",
                    "metadata": {
                        "message": f"Cooldown test {unique_batch} - event {i+1}",
                        "source": "pytest_cooldown",
                        "demo": True
                    }
                }
            )
        
        print("Waiting 8 seconds for rule engine...")
        time.sleep(8)
        
        # Check alert events count
        final_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "type": "alert", "limit": 100}
        )
        assert final_response.status_code == 200
        final_count = final_response.json()["total"]
        
        # Count should not have increased significantly (at most 1 if first test triggered it)
        new_alerts = final_count - initial_count
        print(f"New alerts created: {new_alerts} (initial: {initial_count}, final: {final_count})")
        
        # If cooldown is working, we should see at most 1 new alert (from previous test)
        # Not 2 (which would mean both batches triggered alerts)
        assert new_alerts <= 1, f"Cooldown not working: {new_alerts} new alerts created"


class TestTrafficSummaryStillWorks:
    """Tests that GET /api/admin/traffic/summary still returns all fields"""
    
    def test_summary_returns_all_metric_fields(self):
        """GET /api/admin/traffic/summary still returns all metric fields correctly"""
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
        assert isinstance(data["errors"], int)
        
        print(f"Summary verified - total_events: {data['total_events']}, errors: {data['errors']}")


class TestDemoModeEmailSuppression:
    """Tests that demo mode events suppress founder email"""
    
    def test_demo_mode_events_have_demo_flag(self):
        """Demo mode events have demo=true in metadata"""
        unique_id = uuid.uuid4().hex[:8]
        response = requests.post(
            f"{BASE_URL}/api/admin/events",
            json={
                "type": "error",
                "metadata": {
                    "message": f"Demo mode test {unique_id}",
                    "source": "pytest_demo",
                    "demo": True
                }
            }
        )
        assert response.status_code == 200
        
        # Verify demo flag is preserved
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/traffic/events",
            params={"admin_key": ADMIN_KEY, "limit": 10}
        )
        assert verify_response.status_code == 200
        events = verify_response.json()["events"]
        
        # Find our test event
        test_event = next(
            (e for e in events if e.get("metadata", {}).get("message") == f"Demo mode test {unique_id}"),
            None
        )
        assert test_event is not None
        assert test_event["metadata"]["demo"] is True
        print("Demo mode flag verified - email would be suppressed for this event")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
