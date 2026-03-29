"""
Mobile Optimization API Tests
Tests for GET /api/mobile/bootstrap and POST /api/mobile/refresh endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"


class TestMobileBootstrapDemo:
    """Tests for GET /api/mobile/bootstrap with demo mode"""

    def test_bootstrap_demo_returns_200(self):
        """GET /api/mobile/bootstrap?demo=true returns 200"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Bootstrap demo returns 200")

    def test_bootstrap_demo_has_user_object(self):
        """Demo bootstrap returns user object with correct fields"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        data = response.json()
        
        assert "user" in data, "Missing 'user' field"
        user = data["user"]
        assert user.get("id") == "demo-user", f"Expected demo-user, got {user.get('id')}"
        assert user.get("name") == "Demo Trader", f"Expected Demo Trader, got {user.get('name')}"
        assert user.get("email") == "demo@alphaai.com", f"Expected demo@alphaai.com, got {user.get('email')}"
        assert user.get("user_tier") == "pro", f"Expected pro tier, got {user.get('user_tier')}"
        assert user.get("is_pro") == True, f"Expected is_pro=True, got {user.get('is_pro')}"
        print("PASS: Bootstrap demo has correct user object")

    def test_bootstrap_demo_has_followed_strategies(self):
        """Demo bootstrap returns followed_strategies array"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        data = response.json()
        
        assert "followed_strategies" in data, "Missing 'followed_strategies' field"
        strategies = data["followed_strategies"]
        assert isinstance(strategies, list), "followed_strategies should be a list"
        assert len(strategies) == 3, f"Expected 3 strategies, got {len(strategies)}"
        
        # Check first strategy structure
        first = strategies[0]
        assert "id" in first, "Strategy missing 'id'"
        assert "name" in first, "Strategy missing 'name'"
        assert "asset" in first, "Strategy missing 'asset'"
        print("PASS: Bootstrap demo has followed_strategies")

    def test_bootstrap_demo_has_unread_alerts(self):
        """Demo bootstrap returns unread_alerts count"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        data = response.json()
        
        assert "unread_alerts" in data, "Missing 'unread_alerts' field"
        assert isinstance(data["unread_alerts"], int), "unread_alerts should be int"
        assert data["unread_alerts"] == 3, f"Expected 3 unread alerts, got {data['unread_alerts']}"
        print("PASS: Bootstrap demo has unread_alerts")

    def test_bootstrap_demo_has_feature_flags(self):
        """Demo bootstrap returns feature_flags object"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        data = response.json()
        
        assert "feature_flags" in data, "Missing 'feature_flags' field"
        flags = data["feature_flags"]
        assert flags.get("demo_mode") == True, "Expected demo_mode=True"
        assert flags.get("mobile_optimized") == True, "Expected mobile_optimized=True"
        assert flags.get("real_time_alerts") == True, "Expected real_time_alerts=True"
        assert flags.get("strategy_lab") == True, "Expected strategy_lab=True"
        print("PASS: Bootstrap demo has feature_flags")

    def test_bootstrap_demo_has_strategies_summary(self):
        """Demo bootstrap returns strategies_summary object"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        data = response.json()
        
        assert "strategies_summary" in data, "Missing 'strategies_summary' field"
        summary = data["strategies_summary"]
        assert "total" in summary, "Missing 'total' in strategies_summary"
        assert "top_performer" in summary, "Missing 'top_performer' in strategies_summary"
        assert summary["total"] == 12, f"Expected total=12, got {summary['total']}"
        
        top = summary["top_performer"]
        assert "name" in top, "Missing 'name' in top_performer"
        assert "sharpe" in top, "Missing 'sharpe' in top_performer"
        print("PASS: Bootstrap demo has strategies_summary")

    def test_bootstrap_demo_has_timestamp(self):
        """Demo bootstrap returns timestamp"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        data = response.json()
        
        assert "timestamp" in data, "Missing 'timestamp' field"
        assert isinstance(data["timestamp"], str), "timestamp should be string"
        print("PASS: Bootstrap demo has timestamp")


class TestMobileBootstrapAuth:
    """Tests for GET /api/mobile/bootstrap with authentication"""

    @pytest.fixture
    def auth_token(self):
        """Get auth token for pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code} - {response.text}")
        tokens = response.json()
        return tokens.get("access_token"), tokens.get("refresh_token")

    def test_bootstrap_without_auth_returns_401(self):
        """GET /api/mobile/bootstrap without auth or demo returns 401"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Bootstrap without auth returns 401")

    def test_bootstrap_with_invalid_token_returns_401(self):
        """GET /api/mobile/bootstrap with invalid token returns 401"""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Bootstrap with invalid token returns 401")

    def test_bootstrap_with_valid_token_returns_200(self, auth_token):
        """GET /api/mobile/bootstrap with valid Bearer token returns 200"""
        access_token, _ = auth_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Bootstrap with valid token returns 200")

    def test_bootstrap_auth_has_correct_user_data(self, auth_token):
        """Authenticated bootstrap returns correct user name and email"""
        access_token, _ = auth_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap", headers=headers)
        data = response.json()
        
        assert "user" in data, "Missing 'user' field"
        user = data["user"]
        assert user.get("email") == PRO_USER_EMAIL, f"Expected {PRO_USER_EMAIL}, got {user.get('email')}"
        assert "id" in user, "Missing user id"
        assert "user_tier" in user, "Missing user_tier"
        print("PASS: Bootstrap auth has correct user data")


class TestMobileRefresh:
    """Tests for POST /api/mobile/refresh endpoint"""

    @pytest.fixture
    def refresh_token(self):
        """Get refresh token for pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code} - {response.text}")
        tokens = response.json()
        return tokens.get("refresh_token")

    def test_refresh_without_body_returns_400(self):
        """POST /api/mobile/refresh without body returns 400"""
        response = requests.post(f"{BASE_URL}/api/mobile/refresh")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Refresh without body returns 400")

    def test_refresh_without_token_returns_400(self):
        """POST /api/mobile/refresh without refresh_token returns 400"""
        response = requests.post(f"{BASE_URL}/api/mobile/refresh", json={})
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "refresh_token required" in data.get("detail", ""), f"Unexpected error: {data}"
        print("PASS: Refresh without token returns 400")

    def test_refresh_with_invalid_token_returns_401(self):
        """POST /api/mobile/refresh with invalid token returns 401"""
        response = requests.post(f"{BASE_URL}/api/mobile/refresh", json={
            "refresh_token": "invalid_refresh_token_12345"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Refresh with invalid token returns 401")

    def test_refresh_with_valid_token_returns_new_access_token(self, refresh_token):
        """POST /api/mobile/refresh with valid refresh_token returns new access_token"""
        response = requests.post(f"{BASE_URL}/api/mobile/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Missing 'access_token' in response"
        assert "token_type" in data, "Missing 'token_type' in response"
        assert "user_tier" in data, "Missing 'user_tier' in response"
        assert data["token_type"] == "bearer", f"Expected bearer, got {data['token_type']}"
        assert isinstance(data["access_token"], str), "access_token should be string"
        assert len(data["access_token"]) > 0, "access_token should not be empty"
        print("PASS: Refresh with valid token returns new access_token")

    def test_refresh_returns_user_tier(self, refresh_token):
        """POST /api/mobile/refresh returns user_tier field"""
        response = requests.post(f"{BASE_URL}/api/mobile/refresh", json={
            "refresh_token": refresh_token
        })
        data = response.json()
        
        assert "user_tier" in data, "Missing 'user_tier' in response"
        # Pro user should have pro tier
        assert data["user_tier"] in ["free", "pro", "elite"], f"Invalid user_tier: {data['user_tier']}"
        print(f"PASS: Refresh returns user_tier: {data['user_tier']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
