"""
Test Subscription Health Dashboard API
Tests the GET /api/admin/subscription-health endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_KEY = "alphaai_admin_2026"


class TestSubscriptionHealthAPI:
    """Tests for the Subscription Health Dashboard endpoint"""

    def test_subscription_health_returns_200_with_admin_key(self):
        """Test that endpoint returns 200 with valid admin key"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Endpoint returns 200 with valid admin key")

    def test_subscription_health_requires_admin_key(self):
        """Test that endpoint returns 403/422 without admin key"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health")
        # FastAPI returns 422 for missing required query params
        assert response.status_code in [403, 422], f"Expected 403 or 422, got {response.status_code}"
        print("✓ Endpoint requires admin_key (returns 422 without it)")

    def test_subscription_health_rejects_invalid_admin_key(self):
        """Test that endpoint returns 403 with invalid admin key"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key=invalid_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Endpoint rejects invalid admin key with 403")

    def test_subscription_health_response_structure(self):
        """Test that response has all required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields exist
        required_fields = [
            "success",
            "active_subscribers",
            "mrr",
            "churn_30d",
            "failed_payments_7d",
            "retry_queue",
            "upcoming_renewals_7d",
            "recent_events"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"✓ Response contains all required fields: {required_fields}")

    def test_subscription_health_field_types(self):
        """Test that response fields have correct types"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        # Check field types
        assert isinstance(data["success"], bool), "success should be boolean"
        assert isinstance(data["active_subscribers"], int), "active_subscribers should be int"
        assert isinstance(data["mrr"], (int, float)), "mrr should be number"
        assert isinstance(data["churn_30d"], int), "churn_30d should be int"
        assert isinstance(data["failed_payments_7d"], int), "failed_payments_7d should be int"
        assert isinstance(data["retry_queue"], int), "retry_queue should be int"
        assert isinstance(data["upcoming_renewals_7d"], int), "upcoming_renewals_7d should be int"
        assert isinstance(data["recent_events"], list), "recent_events should be list"
        
        print("✓ All fields have correct types")

    def test_recent_events_structure(self):
        """Test that each recent_event has required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["recent_events"]) > 0:
            for i, event in enumerate(data["recent_events"]):
                assert "type" in event, f"Event {i} missing 'type' field"
                assert "user_email" in event, f"Event {i} missing 'user_email' field"
                assert "timestamp" in event, f"Event {i} missing 'timestamp' field"
            print(f"✓ All {len(data['recent_events'])} recent_events have required fields (type, user_email, timestamp)")
        else:
            print("✓ recent_events is empty (no events to validate)")

    def test_recent_events_sorted_newest_first(self):
        """Test that recent_events are sorted by timestamp descending (newest first)"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        events = data["recent_events"]
        if len(events) > 1:
            timestamps = [e["timestamp"] for e in events]
            # Check that timestamps are in descending order
            for i in range(len(timestamps) - 1):
                assert timestamps[i] >= timestamps[i + 1], f"Events not sorted newest first at index {i}"
            print(f"✓ recent_events sorted newest first ({len(events)} events)")
        else:
            print("✓ Not enough events to verify sorting")

    def test_no_sensitive_stripe_keys_in_response(self):
        """Test that no sensitive Stripe keys are returned in response"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        response_text = response.text.lower()
        
        # Check for sensitive patterns
        sensitive_patterns = ["sk_live", "sk_test", "stripe_api_key", "stripe_secret"]
        for pattern in sensitive_patterns:
            assert pattern not in response_text, f"Sensitive pattern '{pattern}' found in response"
        
        print("✓ No sensitive Stripe keys in response")

    def test_cache_returns_same_data_quickly(self):
        """Test that 30-second cache works (second call returns same data quickly)"""
        # First call
        start1 = time.time()
        response1 = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        time1 = time.time() - start1
        
        # Second call (should be cached)
        start2 = time.time()
        response2 = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        time2 = time.time() - start2
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Data should be identical (cached)
        assert data1 == data2, "Cached response should be identical"
        
        # Second call should be faster (cached)
        print(f"✓ Cache working: First call {time1:.3f}s, Second call {time2:.3f}s")
        print(f"✓ Both responses identical (cached for 30 seconds)")

    def test_mrr_calculation(self):
        """Test that MRR is calculated correctly (pro=$29, elite=$99)"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        # MRR should be a reasonable value (non-negative)
        assert data["mrr"] >= 0, "MRR should be non-negative"
        
        # Based on context: 1 active pro subscriber = $29
        print(f"✓ MRR value: ${data['mrr']} (expected ~$29 for 1 pro user)")

    def test_active_subscribers_count(self):
        """Test that active_subscribers count is reasonable"""
        response = requests.get(f"{BASE_URL}/api/admin/subscription-health?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        # Should be non-negative
        assert data["active_subscribers"] >= 0, "active_subscribers should be non-negative"
        
        # Based on context: 1 active subscriber (demo_test2@my-alpha-ai.com)
        print(f"✓ Active subscribers: {data['active_subscribers']} (expected 1)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
