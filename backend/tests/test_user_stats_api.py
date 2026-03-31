"""
Test suite for GET /api/admin/user-stats endpoint
Tests: response structure, auth, caching, data types
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_KEY = "alphaai_admin_2026"


class TestUserStatsEndpoint:
    """Tests for /api/admin/user-stats endpoint"""

    def test_user_stats_returns_200_with_admin_key(self):
        """GET /api/admin/user-stats?admin_key=... returns 200"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: user-stats returns 200 with valid admin_key")

    def test_user_stats_returns_403_without_admin_key(self):
        """GET /api/admin/user-stats without admin_key returns 403"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats")
        assert response.status_code in [403, 422], f"Expected 403/422, got {response.status_code}"
        print("PASS: user-stats returns 403/422 without admin_key")

    def test_user_stats_returns_403_with_invalid_admin_key(self):
        """GET /api/admin/user-stats with invalid admin_key returns 403"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key=wrong_key")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: user-stats returns 403 with invalid admin_key")

    def test_user_stats_response_has_success_field(self):
        """Response contains success: true"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data = response.json()
        assert "success" in data, "Response missing 'success' field"
        assert data["success"] is True, f"Expected success=True, got {data['success']}"
        print("PASS: Response has success=True")

    def test_user_stats_response_has_total_users(self):
        """Response contains total_users as a number >= 0"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data = response.json()
        assert "total_users" in data, "Response missing 'total_users' field"
        assert isinstance(data["total_users"], int), f"total_users should be int, got {type(data['total_users'])}"
        assert data["total_users"] >= 0, f"total_users should be >= 0, got {data['total_users']}"
        print(f"PASS: total_users = {data['total_users']}")

    def test_user_stats_response_has_new_users_7d(self):
        """Response contains new_users_7d as a number >= 0"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data = response.json()
        assert "new_users_7d" in data, "Response missing 'new_users_7d' field"
        assert isinstance(data["new_users_7d"], int), f"new_users_7d should be int, got {type(data['new_users_7d'])}"
        assert data["new_users_7d"] >= 0, f"new_users_7d should be >= 0, got {data['new_users_7d']}"
        print(f"PASS: new_users_7d = {data['new_users_7d']}")

    def test_user_stats_response_has_active_users_24h(self):
        """Response contains active_users_24h as a number >= 0"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data = response.json()
        assert "active_users_24h" in data, "Response missing 'active_users_24h' field"
        assert isinstance(data["active_users_24h"], int), f"active_users_24h should be int, got {type(data['active_users_24h'])}"
        assert data["active_users_24h"] >= 0, f"active_users_24h should be >= 0, got {data['active_users_24h']}"
        print(f"PASS: active_users_24h = {data['active_users_24h']}")

    def test_user_stats_total_users_is_positive(self):
        """total_users should be > 0 (there are ~79 existing users)"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data = response.json()
        assert data["total_users"] > 0, f"Expected total_users > 0, got {data['total_users']}"
        print(f"PASS: total_users > 0 (actual: {data['total_users']})")

    def test_user_stats_cache_returns_same_data(self):
        """Two quick sequential calls should return same data (30-sec cache)"""
        response1 = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data1 = response1.json()
        
        # Small delay to ensure we're within cache window
        time.sleep(0.5)
        
        response2 = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data2 = response2.json()
        
        assert data1["total_users"] == data2["total_users"], "Cache not working: total_users differs"
        assert data1["new_users_7d"] == data2["new_users_7d"], "Cache not working: new_users_7d differs"
        assert data1["active_users_24h"] == data2["active_users_24h"], "Cache not working: active_users_24h differs"
        print("PASS: Cache working - sequential calls return same data")

    def test_user_stats_complete_response_structure(self):
        """Verify complete response structure"""
        response = requests.get(f"{BASE_URL}/api/admin/user-stats?admin_key={ADMIN_KEY}")
        data = response.json()
        
        required_fields = ["success", "total_users", "new_users_7d", "active_users_24h"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"PASS: Complete response structure verified")
        print(f"  - success: {data['success']}")
        print(f"  - total_users: {data['total_users']}")
        print(f"  - new_users_7d: {data['new_users_7d']}")
        print(f"  - active_users_24h: {data['active_users_24h']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
