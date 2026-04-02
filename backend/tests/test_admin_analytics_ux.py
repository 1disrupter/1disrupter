"""
Test Admin Analytics UX Enhancements
- Analytics Time Filters (Today/7d/30d) via /api/admin/analytics-filtered
- MRR & Subscription Trend Charts via /api/admin/mrr-trends
- Signal History Chart via /api/admin/signal-history
- All endpoints require admin_key authentication
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_KEY = "alphaai_admin_2026"


class TestAnalyticsFiltered:
    """Test /api/admin/analytics-filtered endpoint with range filters"""

    def test_analytics_filtered_requires_admin_key(self):
        """Endpoint should require admin_key authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-filtered")
        assert response.status_code == 422 or response.status_code == 403, f"Expected 422 or 403, got {response.status_code}"
        print("PASS: analytics-filtered requires admin_key")

    def test_analytics_filtered_invalid_admin_key(self):
        """Endpoint should reject invalid admin_key"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-filtered?admin_key=invalid_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: analytics-filtered rejects invalid admin_key")

    def test_analytics_filtered_today(self):
        """Test range=today returns platform metrics"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-filtered?admin_key={ADMIN_KEY}&range=today")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify required fields
        assert "range" in data, "Missing 'range' field"
        assert data["range"] == "today", f"Expected range='today', got {data['range']}"
        assert "total_users" in data, "Missing 'total_users' field"
        assert "pro_users" in data, "Missing 'pro_users' field"
        assert "elite_users" in data, "Missing 'elite_users' field"
        assert "active_subscriptions" in data, "Missing 'active_subscriptions' field"
        assert "signals" in data, "Missing 'signals' field"
        assert "page_views" in data, "Missing 'page_views' field"
        assert "api_calls" in data, "Missing 'api_calls' field"
        assert "demo_mode" in data, "Missing 'demo_mode' field"
        
        print(f"PASS: analytics-filtered range=today returns all fields. demo_mode={data['demo_mode']}")

    def test_analytics_filtered_7d(self):
        """Test range=7d returns platform metrics"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-filtered?admin_key={ADMIN_KEY}&range=7d")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["range"] == "7d", f"Expected range='7d', got {data['range']}"
        assert isinstance(data["total_users"], int), "total_users should be int"
        assert isinstance(data["pro_users"], int), "pro_users should be int"
        assert isinstance(data["elite_users"], int), "elite_users should be int"
        assert isinstance(data["active_subscriptions"], int), "active_subscriptions should be int"
        assert isinstance(data["signals"], int), "signals should be int"
        assert isinstance(data["page_views"], int), "page_views should be int"
        assert isinstance(data["api_calls"], int), "api_calls should be int"
        
        print(f"PASS: analytics-filtered range=7d returns valid data types")

    def test_analytics_filtered_30d(self):
        """Test range=30d returns platform metrics"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-filtered?admin_key={ADMIN_KEY}&range=30d")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["range"] == "30d", f"Expected range='30d', got {data['range']}"
        assert "total_users" in data
        assert "pro_users" in data
        assert "elite_users" in data
        assert "active_subscriptions" in data
        assert "signals" in data
        assert "page_views" in data
        assert "api_calls" in data
        
        print(f"PASS: analytics-filtered range=30d returns all fields")

    def test_analytics_filtered_invalid_range(self):
        """Test invalid range parameter is rejected"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-filtered?admin_key={ADMIN_KEY}&range=invalid")
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for invalid range, got {response.status_code}"
        print("PASS: analytics-filtered rejects invalid range parameter")


class TestMRRTrends:
    """Test /api/admin/mrr-trends endpoint"""

    def test_mrr_trends_requires_admin_key(self):
        """Endpoint should require admin_key authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/mrr-trends")
        assert response.status_code == 422 or response.status_code == 403, f"Expected 422 or 403, got {response.status_code}"
        print("PASS: mrr-trends requires admin_key")

    def test_mrr_trends_invalid_admin_key(self):
        """Endpoint should reject invalid admin_key"""
        response = requests.get(f"{BASE_URL}/api/admin/mrr-trends?admin_key=invalid_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: mrr-trends rejects invalid admin_key")

    def test_mrr_trends_returns_30_days(self):
        """Test mrr-trends returns 30 days of trend data"""
        response = requests.get(f"{BASE_URL}/api/admin/mrr-trends?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "demo_mode" in data, "Missing 'demo_mode' field"
        assert "trends" in data, "Missing 'trends' field"
        assert isinstance(data["trends"], list), "trends should be a list"
        assert len(data["trends"]) == 30, f"Expected 30 days of data, got {len(data['trends'])}"
        
        print(f"PASS: mrr-trends returns 30 days of data. demo_mode={data['demo_mode']}")

    def test_mrr_trends_data_structure(self):
        """Test each trend entry has required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/mrr-trends?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        # Check first entry structure
        if data["trends"]:
            entry = data["trends"][0]
            assert "date" in entry, "Missing 'date' field in trend entry"
            assert "mrr" in entry, "Missing 'mrr' field in trend entry"
            assert "new_subscriptions" in entry, "Missing 'new_subscriptions' field"
            assert "cancellations" in entry, "Missing 'cancellations' field"
            assert "net_revenue" in entry, "Missing 'net_revenue' field"
            assert "cumulative_revenue" in entry, "Missing 'cumulative_revenue' field"
            
            # Verify data types
            assert isinstance(entry["mrr"], (int, float)), "mrr should be numeric"
            assert isinstance(entry["new_subscriptions"], int), "new_subscriptions should be int"
            assert isinstance(entry["cancellations"], int), "cancellations should be int"
            assert isinstance(entry["net_revenue"], (int, float)), "net_revenue should be numeric"
            assert isinstance(entry["cumulative_revenue"], (int, float)), "cumulative_revenue should be numeric"
            
        print("PASS: mrr-trends entries have correct structure and data types")


class TestSignalHistory:
    """Test /api/admin/signal-history endpoint"""

    def test_signal_history_requires_admin_key(self):
        """Endpoint should require admin_key authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/signal-history")
        assert response.status_code == 422 or response.status_code == 403, f"Expected 422 or 403, got {response.status_code}"
        print("PASS: signal-history requires admin_key")

    def test_signal_history_invalid_admin_key(self):
        """Endpoint should reject invalid admin_key"""
        response = requests.get(f"{BASE_URL}/api/admin/signal-history?admin_key=invalid_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: signal-history rejects invalid admin_key")

    def test_signal_history_returns_30_days(self):
        """Test signal-history returns 30 days of signal data"""
        response = requests.get(f"{BASE_URL}/api/admin/signal-history?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "demo_mode" in data, "Missing 'demo_mode' field"
        assert "signals" in data, "Missing 'signals' field"
        assert isinstance(data["signals"], list), "signals should be a list"
        assert len(data["signals"]) == 30, f"Expected 30 days of data, got {len(data['signals'])}"
        
        print(f"PASS: signal-history returns 30 days of data. demo_mode={data['demo_mode']}")

    def test_signal_history_data_structure(self):
        """Test each signal entry has count and ma7 (7-day moving average)"""
        response = requests.get(f"{BASE_URL}/api/admin/signal-history?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        # Check first entry structure
        if data["signals"]:
            entry = data["signals"][0]
            assert "date" in entry, "Missing 'date' field in signal entry"
            assert "count" in entry, "Missing 'count' field in signal entry"
            assert "ma7" in entry, "Missing 'ma7' (7-day moving average) field"
            
            # Verify data types
            assert isinstance(entry["count"], int), "count should be int"
            assert isinstance(entry["ma7"], (int, float)), "ma7 should be numeric"
            
        print("PASS: signal-history entries have count and ma7 fields with correct types")


class TestExistingEndpoints:
    """Test that existing admin endpoints still work"""

    def test_analytics_summary_still_works(self):
        """Existing analytics-summary endpoint should still work"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics-summary?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "demo_mode" in data, "Missing 'demo_mode' field"
        assert "page_views" in data, "Missing 'page_views' field"
        assert "api_calls" in data, "Missing 'api_calls' field"
        
        print("PASS: analytics-summary endpoint still works")

    def test_admin_dashboard_still_works(self):
        """Existing admin dashboard endpoint should still work"""
        response = requests.get(f"{BASE_URL}/api/admin/dashboard?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "summary" in data, "Missing 'summary' field"
        
        print("PASS: admin dashboard endpoint still works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
