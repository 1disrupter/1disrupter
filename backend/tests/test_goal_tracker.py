"""
Goal Tracker API Tests
Tests for GET/POST /api/admin/analytics/goals endpoints
and trends_24h field in /api/admin/analytics
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_KEY = "alphaai_admin_2026"

class TestGoalTrackerEndpoints:
    """Tests for Goal Tracker API endpoints"""
    
    def test_get_goals_returns_default_targets(self):
        """GET /api/admin/analytics/goals returns goal targets"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have all 3 target fields
        assert "k_factor_target" in data, "Missing k_factor_target"
        assert "demo_signup_target" in data, "Missing demo_signup_target"
        assert "demo_pro_target" in data, "Missing demo_pro_target"
        
        # Values should be numeric
        assert isinstance(data["k_factor_target"], (int, float))
        assert isinstance(data["demo_signup_target"], (int, float))
        assert isinstance(data["demo_pro_target"], (int, float))
        print(f"GET goals returned: {data}")
    
    def test_get_goals_requires_admin_key(self):
        """GET /api/admin/analytics/goals without admin_key returns 403/422"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics/goals")
        assert response.status_code in [403, 422], f"Expected 403/422, got {response.status_code}"
        print("GET goals without admin_key correctly rejected")
    
    def test_get_goals_wrong_admin_key(self):
        """GET /api/admin/analytics/goals with wrong key returns 403"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics/goals?admin_key=wrong_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("GET goals with wrong admin_key correctly rejected")
    
    def test_post_goals_saves_and_returns_targets(self):
        """POST /api/admin/analytics/goals saves new targets and returns them"""
        payload = {
            "k_factor_target": 1.5,
            "demo_signup_target": 20.0,
            "demo_pro_target": 8.0
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "saved", f"Expected status='saved', got {data}"
        assert data.get("k_factor_target") == 1.5, f"k_factor_target mismatch: {data}"
        assert data.get("demo_signup_target") == 20.0, f"demo_signup_target mismatch: {data}"
        assert data.get("demo_pro_target") == 8.0, f"demo_pro_target mismatch: {data}"
        print(f"POST goals saved: {data}")
        
        # Verify persistence with GET
        get_response = requests.get(f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data.get("k_factor_target") == 1.5, "k_factor_target not persisted"
        assert get_data.get("demo_signup_target") == 20.0, "demo_signup_target not persisted"
        assert get_data.get("demo_pro_target") == 8.0, "demo_pro_target not persisted"
        print("Goals persisted correctly")
    
    def test_post_goals_validates_k_factor_max(self):
        """POST validates k_factor_target is between 0-5 (max boundary)"""
        payload = {
            "k_factor_target": 6.0,  # Invalid: > 5
            "demo_signup_target": 15.0,
            "demo_pro_target": 5.0
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, f"Expected 422 for k_factor > 5, got {response.status_code}: {response.text}"
        print("k_factor_target > 5 correctly rejected with 422")
    
    def test_post_goals_validates_k_factor_min(self):
        """POST validates k_factor_target is between 0-5 (min boundary)"""
        payload = {
            "k_factor_target": -1.0,  # Invalid: < 0
            "demo_signup_target": 15.0,
            "demo_pro_target": 5.0
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, f"Expected 422 for k_factor < 0, got {response.status_code}: {response.text}"
        print("k_factor_target < 0 correctly rejected with 422")
    
    def test_post_goals_validates_demo_signup_max(self):
        """POST validates demo_signup_target is between 0-100 (max boundary)"""
        payload = {
            "k_factor_target": 1.0,
            "demo_signup_target": 150.0,  # Invalid: > 100
            "demo_pro_target": 5.0
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, f"Expected 422 for demo_signup > 100, got {response.status_code}: {response.text}"
        print("demo_signup_target > 100 correctly rejected with 422")
    
    def test_post_goals_validates_demo_signup_min(self):
        """POST validates demo_signup_target is between 0-100 (min boundary)"""
        payload = {
            "k_factor_target": 1.0,
            "demo_signup_target": -5.0,  # Invalid: < 0
            "demo_pro_target": 5.0
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, f"Expected 422 for demo_signup < 0, got {response.status_code}: {response.text}"
        print("demo_signup_target < 0 correctly rejected with 422")
    
    def test_post_goals_validates_demo_pro_max(self):
        """POST validates demo_pro_target is between 0-100"""
        payload = {
            "k_factor_target": 1.0,
            "demo_signup_target": 15.0,
            "demo_pro_target": 200.0  # Invalid: > 100
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, f"Expected 422 for demo_pro > 100, got {response.status_code}: {response.text}"
        print("demo_pro_target > 100 correctly rejected with 422")
    
    def test_post_goals_requires_admin_key(self):
        """POST /api/admin/analytics/goals without admin_key returns 403/422"""
        payload = {"k_factor_target": 1.0, "demo_signup_target": 15.0, "demo_pro_target": 5.0}
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [403, 422], f"Expected 403/422, got {response.status_code}"
        print("POST goals without admin_key correctly rejected")


class TestAnalyticsTrends24h:
    """Tests for trends_24h field in /api/admin/analytics"""
    
    def test_analytics_returns_trends_24h(self):
        """GET /api/admin/analytics returns trends_24h field"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics?admin_key={ADMIN_KEY}&period=30d")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "trends_24h" in data, f"Missing trends_24h field in response: {list(data.keys())}"
        
        trends = data["trends_24h"]
        # Should have all trend fields
        assert "k_factor" in trends, "Missing k_factor in trends_24h"
        assert "k_factor_prev" in trends, "Missing k_factor_prev in trends_24h"
        assert "demo_signup_rate" in trends, "Missing demo_signup_rate in trends_24h"
        assert "demo_signup_rate_prev" in trends, "Missing demo_signup_rate_prev in trends_24h"
        assert "demo_pro_rate" in trends, "Missing demo_pro_rate in trends_24h"
        assert "demo_pro_rate_prev" in trends, "Missing demo_pro_rate_prev in trends_24h"
        
        print(f"trends_24h returned: {trends}")
    
    def test_analytics_trends_24h_all_periods(self):
        """GET /api/admin/analytics returns trends_24h for all period values"""
        for period in ["24h", "7d", "30d", "all"]:
            response = requests.get(f"{BASE_URL}/api/admin/analytics?admin_key={ADMIN_KEY}&period={period}")
            assert response.status_code == 200, f"Period {period}: Expected 200, got {response.status_code}"
            
            data = response.json()
            assert "trends_24h" in data, f"Period {period}: Missing trends_24h"
            print(f"Period {period}: trends_24h present")


class TestGoalTrackerCleanup:
    """Reset goals to defaults after tests"""
    
    def test_reset_goals_to_defaults(self):
        """Reset goals to default values"""
        payload = {
            "k_factor_target": 1.0,
            "demo_signup_target": 15.0,
            "demo_pro_target": 5.0
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/analytics/goals?admin_key={ADMIN_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Failed to reset goals: {response.text}"
        print("Goals reset to defaults")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
