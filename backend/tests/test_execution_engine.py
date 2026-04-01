"""
Execution Engine API Tests
Tests for execution config, logs, signal emission, and paper/testnet execution.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
ADMIN_EMAIL = "admin@my-alpha-ai.com"
ADMIN_PASSWORD = "Admin1234!"

# Strategy ID for signal testing (owned by free user)
STRATEGY_ID = "d2dc6982-c6fb-4851-b48e-0130cf7f76da"


class TestExecutionConfigEndpoints:
    """Tests for /api/execution/configs/me endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _login(self, email, password):
        """Helper to login and get token"""
        res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if res.status_code == 200:
            return res.json().get("access_token")
        return None

    def test_get_config_returns_default_for_new_user(self):
        """GET /api/execution/configs/me returns default config for user without existing config"""
        token = self._login(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        assert token, "Login failed for free user"
        
        res = self.session.get(
            f"{BASE_URL}/api/execution/configs/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        # Should have default values
        assert "user_id" in data
        assert "execution_mode" in data
        assert "base_position_size" in data
        assert "is_enabled" in data
        print(f"Config response: {data}")

    def test_get_config_for_pro_user_with_existing_config(self):
        """GET /api/execution/configs/me returns existing config for pro user"""
        token = self._login(PRO_USER_EMAIL, PRO_USER_PASSWORD)
        assert token, "Login failed for pro user"
        
        res = self.session.get(
            f"{BASE_URL}/api/execution/configs/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "user_id" in data
        assert "execution_mode" in data
        print(f"Pro user config: {data}")

    def test_update_config_paper_mode(self):
        """POST /api/execution/configs/me creates/updates config with paper mode"""
        token = self._login(PRO_USER_EMAIL, PRO_USER_PASSWORD)
        assert token, "Login failed for pro user"
        
        res = self.session.post(
            f"{BASE_URL}/api/execution/configs/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "execution_mode": "paper",
                "base_position_size": 0.005,
                "is_enabled": True
            }
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert data["execution_mode"] == "paper"
        assert data["base_position_size"] == 0.005
        assert data["is_enabled"] == True
        print(f"Updated config: {data}")

    def test_update_config_testnet_mode_without_credentials_fails(self):
        """POST /api/execution/configs/me with testnet mode rejects if no valid exchange credentials"""
        token = self._login(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        assert token, "Login failed for free user"
        
        res = self.session.post(
            f"{BASE_URL}/api/execution/configs/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "execution_mode": "testnet",
                "base_position_size": 0.001,
                "is_enabled": True  # Enabling testnet without credentials should fail
            }
        )
        # Should fail with 400 because no exchange credentials
        assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
        assert "Connect and validate" in res.text or "API keys" in res.text
        print(f"Testnet rejection: {res.json()}")

    def test_update_config_requires_auth(self):
        """POST /api/execution/configs/me requires authentication"""
        res = self.session.post(
            f"{BASE_URL}/api/execution/configs/me",
            json={
                "execution_mode": "paper",
                "base_position_size": 0.001,
                "is_enabled": False
            }
        )
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"


class TestExecutionLogsEndpoints:
    """Tests for /api/execution/logs endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _login(self, email, password):
        res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if res.status_code == 200:
            return res.json().get("access_token")
        return None

    def test_get_logs_for_user(self):
        """GET /api/execution/logs returns execution logs for authenticated user"""
        token = self._login(PRO_USER_EMAIL, PRO_USER_PASSWORD)
        assert token, "Login failed for pro user"
        
        res = self.session.get(
            f"{BASE_URL}/api/execution/logs",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "logs" in data
        assert "total" in data
        assert isinstance(data["logs"], list)
        print(f"User logs count: {data['total']}")
        if data["logs"]:
            print(f"Sample log: {data['logs'][0]}")

    def test_get_logs_with_status_filter(self):
        """GET /api/execution/logs with status filter"""
        token = self._login(PRO_USER_EMAIL, PRO_USER_PASSWORD)
        assert token, "Login failed for pro user"
        
        res = self.session.get(
            f"{BASE_URL}/api/execution/logs?status=success",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "logs" in data
        # All logs should have status=success if any exist
        for log in data["logs"]:
            assert log["status"] == "success", f"Expected status=success, got {log['status']}"
        print(f"Success logs count: {data['total']}")

    def test_get_logs_requires_auth(self):
        """GET /api/execution/logs requires authentication"""
        res = self.session.get(f"{BASE_URL}/api/execution/logs")
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"

    def test_admin_logs_endpoint(self):
        """GET /api/execution/logs/admin returns all logs for admin"""
        token = self._login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Login failed for admin"
        
        res = self.session.get(
            f"{BASE_URL}/api/execution/logs/admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "logs" in data
        assert "total" in data
        print(f"Admin logs total: {data['total']}")

    def test_admin_logs_requires_admin_role(self):
        """GET /api/execution/logs/admin requires admin role"""
        token = self._login(PRO_USER_EMAIL, PRO_USER_PASSWORD)
        assert token, "Login failed for pro user"
        
        res = self.session.get(
            f"{BASE_URL}/api/execution/logs/admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 403, f"Expected 403, got {res.status_code}"


class TestSignalEmission:
    """Tests for /api/execution/emit-signal endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _login(self, email, password):
        res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if res.status_code == 200:
            return res.json().get("access_token")
        return None

    def test_emit_signal_by_strategy_creator(self):
        """POST /api/execution/emit-signal emits signal and triggers paper execution"""
        # Free user is the strategy creator
        token = self._login(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        assert token, "Login failed for free user (strategy creator)"
        
        res = self.session.post(
            f"{BASE_URL}/api/execution/emit-signal",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "strategy_id": STRATEGY_ID,
                "symbol": "BTCUSDT",
                "side": "BUY",
                "size": 0.001
            }
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "signal" in data
        assert "executions" in data
        assert "logs" in data
        assert data["signal"]["strategy_id"] == STRATEGY_ID
        assert data["signal"]["symbol"] == "BTCUSDT"
        assert data["signal"]["side"] == "BUY"
        print(f"Signal emitted: {data['signal']['id']}, executions: {data['executions']}")

    def test_emit_signal_by_non_creator_fails(self):
        """POST /api/execution/emit-signal fails for non-creator"""
        # Pro user is NOT the strategy creator
        token = self._login(PRO_USER_EMAIL, PRO_USER_PASSWORD)
        assert token, "Login failed for pro user"
        
        res = self.session.post(
            f"{BASE_URL}/api/execution/emit-signal",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "strategy_id": STRATEGY_ID,
                "symbol": "BTCUSDT",
                "side": "BUY"
            }
        )
        assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
        print(f"Non-creator rejection: {res.json()}")

    def test_emit_signal_invalid_strategy(self):
        """POST /api/execution/emit-signal fails for invalid strategy"""
        token = self._login(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        assert token, "Login failed for free user"
        
        res = self.session.post(
            f"{BASE_URL}/api/execution/emit-signal",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "strategy_id": "invalid-strategy-id",
                "symbol": "BTCUSDT",
                "side": "BUY"
            }
        )
        assert res.status_code == 404, f"Expected 404, got {res.status_code}: {res.text}"

    def test_emit_signal_requires_auth(self):
        """POST /api/execution/emit-signal requires authentication"""
        res = self.session.post(
            f"{BASE_URL}/api/execution/emit-signal",
            json={
                "strategy_id": STRATEGY_ID,
                "symbol": "BTCUSDT",
                "side": "BUY"
            }
        )
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"


class TestTestOrderEndpoint:
    """Tests for /api/execution/test-order endpoint (requires exchange credentials)"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _login(self, email, password):
        res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if res.status_code == 200:
            return res.json().get("access_token")
        return None

    def test_test_order_without_credentials_fails(self):
        """POST /api/execution/test-order fails without exchange credentials"""
        token = self._login(FREE_USER_EMAIL, FREE_USER_PASSWORD)
        assert token, "Login failed for free user"
        
        res = self.session.post(
            f"{BASE_URL}/api/execution/test-order",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "quantity": 0.001
            }
        )
        # Should fail because user has no exchange credentials
        assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
        assert "exchange" in res.text.lower() or "connect" in res.text.lower()
        print(f"Test order rejection: {res.json()}")

    def test_test_order_requires_auth(self):
        """POST /api/execution/test-order requires authentication"""
        res = self.session.post(
            f"{BASE_URL}/api/execution/test-order",
            json={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "quantity": 0.001
            }
        )
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
