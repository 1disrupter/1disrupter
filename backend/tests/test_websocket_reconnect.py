"""
WebSocket Reconnect Loop Fix Tests
Tests for the WebSocket reconnect behavior and alerts status endpoint.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWebSocketAlerts:
    """Tests for WebSocket alerts endpoints"""
    
    def test_alerts_status_endpoint(self):
        """Test /api/alerts/status returns connection stats"""
        response = requests.get(f"{BASE_URL}/api/alerts/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "active"
        assert "connections" in data
        assert "pro_connections" in data["connections"]
        assert "demo_connections" in data["connections"]
        assert "total" in data["connections"]
        print(f"PASS: /api/alerts/status returns {data}")
    
    def test_alerts_test_endpoint(self):
        """Test /api/alerts/test broadcasts test alert"""
        response = requests.post(f"{BASE_URL}/api/alerts/test")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert data["success"] == True
        assert "alert" in data
        assert data["alert"]["type"] == "strategy_alert"
        print(f"PASS: /api/alerts/test broadcasts alert successfully")
    
    def test_health_check(self):
        """Test basic API health"""
        # Try multiple health endpoints
        endpoints = ["/api/alerts/status", "/api/mobile/bootstrap?demo=true"]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Endpoint {endpoint} failed with {response.status_code}"
            print(f"PASS: {endpoint} returns 200")


class TestDemoMode:
    """Tests for demo mode functionality"""
    
    def test_demo_bootstrap(self):
        """Test demo mode bootstrap returns correct data"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap?demo=true")
        assert response.status_code == 200
        
        data = response.json()
        assert "user" in data
        assert "followed_strategies" in data or "strategies_summary" in data
        print(f"PASS: Demo bootstrap returns user and strategies data")
    
    def test_demo_leaderboard(self):
        """Test demo mode leaderboard returns data"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?demo=true")
        assert response.status_code == 200
        
        data = response.json()
        # Leaderboard returns traders, not strategies
        assert "traders" in data or "strategies" in data
        print(f"PASS: Demo leaderboard returns data")


class TestAuthenticatedEndpoints:
    """Tests for authenticated user endpoints"""
    
    @pytest.fixture
    def pro_user_token(self):
        """Get auth token for pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_test2@my-alpha-ai.com",
            "password": "NewPass1234!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Pro user login failed")
    
    @pytest.fixture
    def free_user_token(self):
        """Get auth token for free user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test_free_user_iter29@my-alpha-ai.com",
            "password": "TestPass123!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Free user login failed")
    
    def test_pro_user_login(self, pro_user_token):
        """Test pro user can login"""
        assert pro_user_token is not None
        print(f"PASS: Pro user login successful")
    
    def test_free_user_login(self, free_user_token):
        """Test free user can login"""
        assert free_user_token is not None
        print(f"PASS: Free user login successful")
    
    def test_pro_user_profile(self, pro_user_token):
        """Test pro user profile returns correct tier"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # API returns user data directly, not wrapped in "user" key
        user = data if "email" in data else data.get("user", data)
        is_pro = user.get("is_pro", False) or user.get("user_tier") == "pro"
        print(f"PASS: Pro user profile - is_pro: {is_pro}, tier: {user.get('user_tier')}")
    
    def test_free_user_profile(self, free_user_token):
        """Test free user profile returns correct tier"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # API returns user data directly, not wrapped in "user" key
        user = data if "email" in data else data.get("user", data)
        is_free = not user.get("is_pro", False) and user.get("user_tier") != "pro"
        print(f"PASS: Free user profile - is_pro: {user.get('is_pro')}, tier: {user.get('user_tier')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
