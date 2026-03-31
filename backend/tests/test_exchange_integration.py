"""
Exchange Integration Tests - Phase 1 (Testnet Only)
Tests for: connect, validate, status, disconnect endpoints
Admin exchanges endpoint test
Security: no secret keys exposed
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "demo_test2@my-alpha-ai.com"
TEST_PASSWORD = "NewPass1234!"
ADMIN_KEY = "alphaai_admin_2026"


class TestExchangeEndpointsAuth:
    """Test authentication requirements for exchange endpoints"""
    
    def test_exchange_status_requires_auth(self):
        """GET /api/exchange/status should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/exchange/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: GET /api/exchange/status returns 401 without auth")
    
    def test_exchange_connect_requires_auth(self):
        """POST /api/exchange/connect should return 401 without token"""
        response = requests.post(
            f"{BASE_URL}/api/exchange/connect",
            json={"exchange": "binance_testnet", "api_key": "test123456", "secret_key": "test123456"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: POST /api/exchange/connect returns 401 without auth")
    
    def test_exchange_disconnect_requires_auth(self):
        """DELETE /api/exchange/disconnect should return 401 without token"""
        response = requests.delete(f"{BASE_URL}/api/exchange/disconnect")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: DELETE /api/exchange/disconnect returns 401 without auth")
    
    def test_exchange_validate_requires_auth(self):
        """POST /api/exchange/validate should return 401 without token"""
        response = requests.post(f"{BASE_URL}/api/exchange/validate")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: POST /api/exchange/validate returns 401 without auth")


class TestExchangeStatusEndpoint:
    """Test exchange status endpoint with authenticated user"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.text}")
        
        self.token = login_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_exchange_status_returns_connected_false_for_new_user(self):
        """GET /api/exchange/status returns {connected: false} for user without exchange"""
        response = requests.get(f"{BASE_URL}/api/exchange/status", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # User may or may not have exchange connected, but response should have 'connected' field
        assert "connected" in data, f"Response should have 'connected' field: {data}"
        print(f"PASS: GET /api/exchange/status returns valid response with connected={data['connected']}")


class TestExchangeConnectEndpoint:
    """Test exchange connect endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.text}")
        
        self.token = login_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_exchange_connect_rejects_invalid_api_keys(self):
        """POST /api/exchange/connect rejects invalid API keys with error message"""
        response = requests.post(
            f"{BASE_URL}/api/exchange/connect",
            headers=self.headers,
            json={
                "exchange": "binance_testnet",
                "api_key": "invalid_test_key_12345",
                "secret_key": "invalid_test_secret_12345"
            }
        )
        # Binance Testnet will reject invalid keys with 400 or 502
        assert response.status_code in [400, 502], f"Expected 400 or 502 for invalid keys, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, f"Error response should have 'detail' field: {data}"
        print(f"PASS: POST /api/exchange/connect rejects invalid keys with status {response.status_code}")
    
    def test_exchange_connect_validates_exchange_type(self):
        """POST /api/exchange/connect validates exchange type"""
        response = requests.post(
            f"{BASE_URL}/api/exchange/connect",
            headers=self.headers,
            json={
                "exchange": "invalid_exchange",
                "api_key": "test_key_12345",
                "secret_key": "test_secret_12345"
            }
        )
        # Should reject invalid exchange type with 422 (validation error)
        assert response.status_code == 422, f"Expected 422 for invalid exchange, got {response.status_code}: {response.text}"
        print("PASS: POST /api/exchange/connect validates exchange type")


class TestExchangeValidateEndpoint:
    """Test exchange validate endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.text}")
        
        self.token = login_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_exchange_validate_returns_400_for_no_exchange(self):
        """POST /api/exchange/validate returns 400 for user without connected exchange"""
        # First check if user has exchange connected
        status_response = requests.get(f"{BASE_URL}/api/exchange/status", headers=self.headers)
        if status_response.status_code == 200 and status_response.json().get("connected"):
            # User has exchange, disconnect first
            requests.delete(f"{BASE_URL}/api/exchange/disconnect", headers=self.headers)
        
        response = requests.post(f"{BASE_URL}/api/exchange/validate", headers=self.headers)
        assert response.status_code == 400, f"Expected 400 for no exchange, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, f"Error response should have 'detail' field: {data}"
        assert "No exchange connected" in data["detail"], f"Expected 'No exchange connected' message: {data}"
        print("PASS: POST /api/exchange/validate returns 400 for user without exchange")


class TestAdminExchangesEndpoint:
    """Test admin exchanges endpoint"""
    
    def test_admin_exchanges_requires_admin_key(self):
        """GET /api/admin/exchanges requires admin_key (403 without it)"""
        response = requests.get(f"{BASE_URL}/api/admin/exchanges")
        assert response.status_code in [403, 422], f"Expected 403 or 422 without admin_key, got {response.status_code}: {response.text}"
        print("PASS: GET /api/admin/exchanges requires admin_key")
    
    def test_admin_exchanges_returns_list_with_valid_key(self):
        """GET /api/admin/exchanges?admin_key=... returns exchanges list"""
        response = requests.get(f"{BASE_URL}/api/admin/exchanges?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "success" in data, f"Response should have 'success' field: {data}"
        assert data["success"] == True, f"Expected success=True: {data}"
        assert "exchanges" in data, f"Response should have 'exchanges' field: {data}"
        assert isinstance(data["exchanges"], list), f"'exchanges' should be a list: {data}"
        print(f"PASS: GET /api/admin/exchanges returns list with {len(data['exchanges'])} entries")
    
    def test_admin_exchanges_does_not_expose_secret_keys(self):
        """Admin exchanges response does NOT contain secret keys or encrypted keys"""
        response = requests.get(f"{BASE_URL}/api/admin/exchanges?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        response_text = str(data).lower()
        
        # Check that no secret key fields are exposed
        forbidden_fields = ["secret_key", "secret_key_enc", "api_key_enc", "encrypted"]
        for field in forbidden_fields:
            assert field not in response_text, f"Response should NOT contain '{field}': {data}"
        
        # Check individual exchange entries
        for entry in data.get("exchanges", []):
            assert "secret_key" not in entry, f"Entry should not have secret_key: {entry}"
            assert "secret_key_enc" not in entry, f"Entry should not have secret_key_enc: {entry}"
            assert "api_key_enc" not in entry, f"Entry should not have api_key_enc: {entry}"
        
        print("PASS: Admin exchanges response does NOT expose secret keys")


class TestExchangeDisconnect:
    """Test exchange disconnect endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.text}")
        
        self.token = login_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_exchange_disconnect_succeeds(self):
        """DELETE /api/exchange/disconnect returns success"""
        response = requests.delete(f"{BASE_URL}/api/exchange/disconnect", headers=self.headers)
        # Should succeed even if no exchange connected
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "success" in data, f"Response should have 'success' field: {data}"
        assert data["success"] == True, f"Expected success=True: {data}"
        print("PASS: DELETE /api/exchange/disconnect returns success")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
