"""
AlphaAI Authentication API Tests
Tests for:
- User Registration (POST /api/auth/register)
- User Login (POST /api/auth/login)
- Token Refresh (POST /api/auth/refresh)
- Get Current User (GET /api/auth/me)
- Password Reset Flow (POST /api/auth/forgot-password, /api/auth/reset-password)
- Email Verification (POST /api/auth/verify-email)
- 2FA Enable/Verify/Disable (POST /api/auth/2fa/enable, /verify, /disable)
- Link Wallet (POST /api/auth/link-wallet)
- WebSocket Status (GET /api/ws/status)
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://crypto-signals-web2.preview.emergentagent.com')

# Test data
TEST_USER_PREFIX = "TEST_AUTH_"
TEST_EMAIL = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
TEST_PASSWORD = "TestPassword123!"
TEST_NAME = "Test Auth User"


class TestAuthRegistration:
    """Test user registration endpoint"""
    
    def test_register_new_user(self):
        """POST /api/auth/register - Register new user successfully"""
        unique_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "refresh_token" in data, "Response should contain refresh_token"
        assert "user" in data, "Response should contain user object"
        assert data["token_type"] == "bearer"
        
        # Verify user data
        user = data["user"]
        assert user["email"] == unique_email.lower()
        assert user["name"] == TEST_NAME
        assert user["is_verified"] == False
        assert user["is_pro"] == False
        assert user["has_2fa"] == False
        assert "id" in user
        assert "created_at" in user
        
        print(f"✓ User registered: {unique_email}")
        return data
    
    def test_register_duplicate_email(self):
        """POST /api/auth/register - Reject duplicate email"""
        unique_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        
        # First registration
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response1.status_code == 200
        
        # Duplicate registration
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "name": "Another User"
        })
        
        assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}"
        assert "already registered" in response2.json().get("detail", "").lower()
        print("✓ Duplicate email rejected correctly")
    
    def test_register_invalid_email(self):
        """POST /api/auth/register - Reject invalid email format"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "invalid-email",
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        
        assert response.status_code == 422, f"Expected 422 for invalid email, got {response.status_code}"
        print("✓ Invalid email rejected correctly")
    
    def test_register_short_password(self):
        """POST /api/auth/register - Reject password < 8 chars"""
        unique_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "short",
            "name": TEST_NAME
        })
        
        assert response.status_code == 422, f"Expected 422 for short password, got {response.status_code}"
        print("✓ Short password rejected correctly")


class TestAuthLogin:
    """Test user login endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a test user for login tests"""
        self.test_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
        self.user_data = response.json()
    
    def test_login_success(self):
        """POST /api/auth/login - Login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.test_email,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == self.test_email.lower()
        print(f"✓ Login successful for {self.test_email}")
    
    def test_login_wrong_password(self):
        """POST /api/auth/login - Reject wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.test_email,
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        assert "invalid" in response.json().get("detail", "").lower()
        print("✓ Wrong password rejected correctly")
    
    def test_login_nonexistent_user(self):
        """POST /api/auth/login - Reject nonexistent user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@alphaai.com",
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Nonexistent user rejected correctly")


class TestTokenRefresh:
    """Test token refresh endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a test user and get tokens"""
        self.test_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
        self.tokens = response.json()
    
    def test_refresh_token_success(self):
        """POST /api/auth/refresh - Get new tokens with valid refresh token"""
        # Wait a second to ensure different token timestamps
        time.sleep(1)
        
        response = requests.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": self.tokens["refresh_token"]
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        
        # Refresh token should be different (old one is revoked)
        assert data["refresh_token"] != self.tokens["refresh_token"], "Refresh token should be rotated"
        print("✓ Token refresh successful")
    
    def test_refresh_invalid_token(self):
        """POST /api/auth/refresh - Reject invalid refresh token"""
        response = requests.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": "invalid_token_here"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid refresh token rejected correctly")


class TestGetCurrentUser:
    """Test get current user endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a test user and get tokens"""
        self.test_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
        self.tokens = response.json()
    
    def test_get_me_success(self):
        """GET /api/auth/me - Get current user with valid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.tokens['access_token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["email"] == self.test_email.lower()
        assert data["name"] == TEST_NAME
        assert "id" in data
        assert "is_verified" in data
        assert "is_pro" in data
        assert "has_2fa" in data
        print("✓ Get current user successful")
    
    def test_get_me_no_token(self):
        """GET /api/auth/me - Reject request without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Request without token rejected correctly")
    
    def test_get_me_invalid_token(self):
        """GET /api/auth/me - Reject request with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid token rejected correctly")


class TestPasswordReset:
    """Test password reset flow"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a test user"""
        self.test_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
    
    def test_forgot_password_existing_user(self):
        """POST /api/auth/forgot-password - Request reset for existing user"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": self.test_email
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert "message" in response.json()
        print("✓ Forgot password request successful")
    
    def test_forgot_password_nonexistent_user(self):
        """POST /api/auth/forgot-password - Returns success even for nonexistent (prevents enumeration)"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "nonexistent@alphaai.com"
        })
        
        # Should return 200 to prevent email enumeration
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Forgot password for nonexistent user handled correctly (no enumeration)")
    
    def test_reset_password_invalid_token(self):
        """POST /api/auth/reset-password - Reject invalid reset token"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": "invalid_reset_token",
            "new_password": "NewPassword123!"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid reset token rejected correctly")


class TestEmailVerification:
    """Test email verification endpoint"""
    
    def test_verify_email_invalid_token(self):
        """POST /api/auth/verify-email - Reject invalid verification token"""
        response = requests.post(f"{BASE_URL}/api/auth/verify-email", json={
            "token": "invalid_verification_token"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid verification token rejected correctly")


class TestTwoFactorAuth:
    """Test 2FA endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a test user and get tokens"""
        self.test_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
        self.tokens = response.json()
        self.headers = {"Authorization": f"Bearer {self.tokens['access_token']}"}
    
    def test_enable_2fa(self):
        """POST /api/auth/2fa/enable - Enable 2FA returns secret and QR code"""
        response = requests.post(
            f"{BASE_URL}/api/auth/2fa/enable",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "secret" in data, "Response should contain TOTP secret"
        assert "qr_code" in data, "Response should contain QR code"
        assert "backup_codes" in data, "Response should contain backup codes"
        assert len(data["backup_codes"]) == 8, "Should have 8 backup codes"
        assert data["qr_code"].startswith("data:image/png;base64,")
        print("✓ 2FA enable returns secret and QR code")
    
    def test_enable_2fa_no_auth(self):
        """POST /api/auth/2fa/enable - Reject without authentication"""
        response = requests.post(f"{BASE_URL}/api/auth/2fa/enable")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ 2FA enable without auth rejected correctly")
    
    def test_verify_2fa_invalid_code(self):
        """POST /api/auth/2fa/verify - Reject invalid TOTP code"""
        # First enable 2FA
        enable_response = requests.post(
            f"{BASE_URL}/api/auth/2fa/enable",
            headers=self.headers
        )
        assert enable_response.status_code == 200
        
        # Try to verify with invalid code
        response = requests.post(
            f"{BASE_URL}/api/auth/2fa/verify",
            headers=self.headers,
            json={"totp_code": "000000"}
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid 2FA code rejected correctly")
    
    def test_disable_2fa_not_enabled(self):
        """POST /api/auth/2fa/disable - Reject when 2FA not enabled"""
        response = requests.post(
            f"{BASE_URL}/api/auth/2fa/disable",
            headers=self.headers,
            json={"totp_code": "123456"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Disable 2FA when not enabled rejected correctly")


class TestLinkWallet:
    """Test wallet linking endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a test user and get tokens"""
        self.test_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
        self.tokens = response.json()
        self.headers = {"Authorization": f"Bearer {self.tokens['access_token']}"}
    
    def test_link_wallet_success(self):
        """POST /api/auth/link-wallet - Link wallet successfully"""
        wallet_address = f"0x{uuid.uuid4().hex[:40]}"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/link-wallet",
            headers=self.headers,
            json={"wallet_address": wallet_address}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert "wallet_address" in data
        assert data["wallet_address"] == wallet_address.lower()
        
        # Verify wallet is linked by getting user
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert me_response.status_code == 200
        assert me_response.json()["wallet_address"] == wallet_address.lower()
        print("✓ Wallet linked successfully")
    
    def test_link_wallet_no_auth(self):
        """POST /api/auth/link-wallet - Reject without authentication"""
        response = requests.post(
            f"{BASE_URL}/api/auth/link-wallet",
            json={"wallet_address": "0x1234567890abcdef1234567890abcdef12345678"}
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Link wallet without auth rejected correctly")


class TestWebSocketStatus:
    """Test WebSocket status endpoint"""
    
    def test_ws_status(self):
        """GET /api/ws/status - Get WebSocket connection statistics"""
        response = requests.get(f"{BASE_URL}/api/ws/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "active"
        assert "connections" in data
        assert "pro" in data["connections"]
        assert "elite" in data["connections"]
        assert "total" in data["connections"]
        print("✓ WebSocket status endpoint working")


class TestLogout:
    """Test logout endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a test user and get tokens"""
        self.test_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
        self.tokens = response.json()
        self.headers = {"Authorization": f"Bearer {self.tokens['access_token']}"}
    
    def test_logout_success(self):
        """POST /api/auth/logout - Logout successfully"""
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert "message" in response.json()
        print("✓ Logout successful")
    
    def test_logout_no_auth(self):
        """POST /api/auth/logout - Reject without authentication"""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Logout without auth rejected correctly")


class TestEndToEndAuthFlow:
    """Test complete authentication flow"""
    
    def test_full_auth_flow(self):
        """Complete auth flow: register -> login -> get me -> refresh -> logout"""
        unique_email = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@alphaai.com"
        
        # 1. Register
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert register_response.status_code == 200
        register_data = register_response.json()
        user_id = register_data["user"]["id"]
        print(f"✓ Step 1: Registered user {unique_email}")
        
        # 2. Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        print("✓ Step 2: Logged in successfully")
        
        # 3. Get current user
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["id"] == user_id
        print("✓ Step 3: Got current user")
        
        # 4. Refresh token
        refresh_response = requests.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]
        print("✓ Step 4: Refreshed token")
        
        # 5. Verify new token works
        me_response2 = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        assert me_response2.status_code == 200
        print("✓ Step 5: New token works")
        
        # 6. Logout
        logout_response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        assert logout_response.status_code == 200
        print("✓ Step 6: Logged out")
        
        print("✓ Full auth flow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
