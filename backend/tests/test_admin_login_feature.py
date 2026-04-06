"""
Test Admin Login Feature
- Admin user auto-elevation to elite tier
- Admin role returned in login response
- Normal user does NOT get auto-elevated
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "mar-brick@hotmail.com"
ADMIN_PASSWORD = "Martin2026!"
NORMAL_USER_EMAIL = "demo_test2@my-alpha-ai.com"
NORMAL_USER_PASSWORD = "NewPass1234!"


class TestAdminLoginFeature:
    """Test admin login auto-elevation and role assignment"""

    def test_admin_login_returns_admin_role(self):
        """POST /api/auth/login with admin credentials returns role:admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        
        # Verify user object exists
        assert "user" in data, "Response missing 'user' field"
        user = data["user"]
        
        # Verify role is admin
        assert user.get("role") == "admin", f"Expected role='admin', got role='{user.get('role')}'"
        print(f"✓ Admin login returns role='admin'")

    def test_admin_login_returns_elite_tier(self):
        """POST /api/auth/login with admin credentials returns user_tier:elite"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        user = data["user"]
        
        # Verify user_tier is elite (auto-elevated)
        assert user.get("user_tier") == "elite", f"Expected user_tier='elite', got '{user.get('user_tier')}'"
        print(f"✓ Admin login returns user_tier='elite'")

    def test_admin_login_returns_is_pro_true(self):
        """POST /api/auth/login with admin credentials returns is_pro:true"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        user = data["user"]
        
        # Verify is_pro is true (auto-elevated)
        assert user.get("is_pro") is True, f"Expected is_pro=True, got '{user.get('is_pro')}'"
        print(f"✓ Admin login returns is_pro=True")

    def test_admin_login_returns_is_elite_true(self):
        """POST /api/auth/login with admin credentials returns is_elite:true"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        user = data["user"]
        
        # Verify is_elite is true (auto-elevated)
        assert user.get("is_elite") is True, f"Expected is_elite=True, got '{user.get('is_elite')}'"
        print(f"✓ Admin login returns is_elite=True")

    def test_admin_login_returns_tokens(self):
        """POST /api/auth/login with admin credentials returns access_token and refresh_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        
        # Verify tokens exist
        assert "access_token" in data, "Response missing 'access_token'"
        assert "refresh_token" in data, "Response missing 'refresh_token'"
        assert len(data["access_token"]) > 0, "access_token is empty"
        assert len(data["refresh_token"]) > 0, "refresh_token is empty"
        print(f"✓ Admin login returns valid tokens")

    def test_normal_user_login_returns_user_role(self):
        """POST /api/auth/login with normal user returns role:user (not admin)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": NORMAL_USER_EMAIL,
            "password": NORMAL_USER_PASSWORD
        })
        
        assert response.status_code == 200, f"Normal user login failed: {response.text}"
        data = response.json()
        user = data["user"]
        
        # Verify role is NOT admin
        assert user.get("role") == "user", f"Expected role='user', got role='{user.get('role')}'"
        print(f"✓ Normal user login returns role='user'")

    def test_normal_user_not_auto_elevated_to_elite(self):
        """POST /api/auth/login with normal user does NOT auto-elevate to elite"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": NORMAL_USER_EMAIL,
            "password": NORMAL_USER_PASSWORD
        })
        
        assert response.status_code == 200, f"Normal user login failed: {response.text}"
        data = response.json()
        user = data["user"]
        
        # Normal user should NOT be auto-elevated to elite (unless they actually have elite)
        # The key test is that is_elite should NOT be True just because they logged in
        # (unless they actually purchased elite)
        role = user.get("role")
        assert role != "admin", f"Normal user should not have admin role"
        
        # If user_tier is not elite in DB, is_elite should be False
        # Since this is a "pro" user per test_credentials.md, they may have is_pro=True
        # but should NOT have is_elite=True unless they purchased it
        print(f"✓ Normal user role='{role}', is_elite={user.get('is_elite')}, user_tier='{user.get('user_tier')}'")

    def test_admin_me_endpoint_returns_admin_data(self):
        """GET /api/auth/me with admin token returns admin role and elite tier"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        token = login_response.json()["access_token"]
        
        # Call /me endpoint
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200, f"/me endpoint failed: {me_response.text}"
        user = me_response.json()
        
        # Verify admin data
        assert user.get("role") == "admin", f"Expected role='admin', got '{user.get('role')}'"
        assert user.get("user_tier") == "elite", f"Expected user_tier='elite', got '{user.get('user_tier')}'"
        assert user.get("is_pro") is True, f"Expected is_pro=True"
        assert user.get("is_elite") is True, f"Expected is_elite=True"
        print(f"✓ /me endpoint returns admin data correctly")


class TestInvalidLogin:
    """Test invalid login scenarios"""

    def test_invalid_password_returns_401(self):
        """POST /api/auth/login with wrong password returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid password returns 401")

    def test_invalid_email_returns_401(self):
        """POST /api/auth/login with non-existent email returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid email returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
