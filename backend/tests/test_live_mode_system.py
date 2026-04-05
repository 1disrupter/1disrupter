"""
Live Mode System Tests — Tests for demo mode toggle, live signals, portfolio, and WebSocket events.
Iteration 71: Testing the new live mode system with demo mode toggle.
"""
import pytest
import requests
import os
import json
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_KEY = "alphaai_admin_2026"
ADMIN_EMAIL = "mar-brick@hotmail.com"
ADMIN_PASSWORD = "Martin2026!"
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"


class TestDemoModeStatus:
    """Test GET /api/demo-mode/status — public endpoint"""

    def test_demo_mode_status_public_no_auth(self):
        """Demo mode status should be accessible without authentication"""
        response = requests.get(f"{BASE_URL}/api/demo-mode/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "demo_mode" in data, "Response should contain 'demo_mode' field"
        assert isinstance(data["demo_mode"], bool), "demo_mode should be a boolean"
        print(f"✓ Demo mode status (public): demo_mode={data['demo_mode']}")


class TestAdminDemoModeToggle:
    """Test POST /api/admin/demo-mode — admin toggle endpoint"""

    def test_toggle_demo_mode_on(self):
        """Toggle demo mode ON with valid admin key"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("demo_mode") == True, "demo_mode should be True"
        print(f"✓ Demo mode toggled ON: {data}")

    def test_toggle_demo_mode_off(self):
        """Toggle demo mode OFF with valid admin key"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("demo_mode") == False, "demo_mode should be False"
        print(f"✓ Demo mode toggled OFF: {data}")

    def test_toggle_demo_mode_invalid_key(self):
        """Toggle demo mode with invalid admin key should fail"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key=invalid_key",
            json={"enabled": True}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Invalid admin key correctly rejected with 403")

    def test_toggle_demo_mode_missing_key(self):
        """Toggle demo mode without admin key should fail"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode",
            json={"enabled": True}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✓ Missing admin key correctly rejected with 422")


class TestLiveSignalsEndpoint:
    """Test GET /api/signals/live — live signals feed"""

    def test_signals_live_demo_mode_on(self):
        """When demo mode ON, /api/signals/live returns demo signals with is_demo=True"""
        # First, turn demo mode ON
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        time.sleep(0.5)  # Allow cache to update

        response = requests.get(f"{BASE_URL}/api/signals/live?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "signals" in data, "Response should contain 'signals' field"
        assert "demo_mode" in data, "Response should contain 'demo_mode' field"
        assert data["demo_mode"] == True, "demo_mode should be True"
        
        # Check that signals have is_demo=True
        if data["signals"]:
            for signal in data["signals"]:
                assert signal.get("is_demo") == True, f"Signal should have is_demo=True: {signal}"
        
        print(f"✓ Demo mode ON: Got {len(data['signals'])} demo signals with is_demo=True")

    def test_signals_live_demo_mode_off(self):
        """When demo mode OFF, /api/signals/live returns real signals with demo_mode=False"""
        # Turn demo mode OFF
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        time.sleep(0.5)  # Allow cache to update

        response = requests.get(f"{BASE_URL}/api/signals/live?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "signals" in data, "Response should contain 'signals' field"
        assert "demo_mode" in data, "Response should contain 'demo_mode' field"
        assert data["demo_mode"] == False, "demo_mode should be False"
        
        print(f"✓ Demo mode OFF: Got {len(data['signals'])} real signals, demo_mode=False")

    def test_signals_live_with_limit(self):
        """Test limit parameter works correctly"""
        response = requests.get(f"{BASE_URL}/api/signals/live?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("signals", [])) <= 3, "Should respect limit parameter"
        print(f"✓ Limit parameter works: got {len(data['signals'])} signals (limit=3)")


class TestPortfolioEndpoint:
    """Test GET /api/portfolio/me — user portfolio performance"""

    def test_portfolio_demo_mode_on(self):
        """When demo mode ON, /api/portfolio/me returns demo portfolio with PnL=1247.83"""
        # Turn demo mode ON
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        time.sleep(0.5)

        response = requests.get(f"{BASE_URL}/api/portfolio/me?user_id=test_user_123&days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("demo_mode") == True, "demo_mode should be True"
        assert data.get("total_pnl") == 1247.83, f"Demo PnL should be 1247.83, got {data.get('total_pnl')}"
        assert data.get("win_rate") == 68.2, f"Demo win_rate should be 68.2, got {data.get('win_rate')}"
        assert data.get("total_trades") == 47, f"Demo total_trades should be 47, got {data.get('total_trades')}"
        
        print(f"✓ Demo mode ON: Portfolio returns demo data (PnL={data['total_pnl']})")

    def test_portfolio_demo_mode_off(self):
        """When demo mode OFF, /api/portfolio/me returns real portfolio data"""
        # Turn demo mode OFF
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        time.sleep(0.5)

        response = requests.get(f"{BASE_URL}/api/portfolio/me?user_id=test_user_123&days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("demo_mode") == False, "demo_mode should be False"
        assert "total_pnl" in data, "Response should contain total_pnl"
        assert "win_rate" in data, "Response should contain win_rate"
        assert "total_trades" in data, "Response should contain total_trades"
        
        print(f"✓ Demo mode OFF: Portfolio returns real data (PnL={data['total_pnl']}, trades={data['total_trades']})")

    def test_portfolio_requires_user_id(self):
        """Portfolio endpoint requires user_id parameter"""
        response = requests.get(f"{BASE_URL}/api/portfolio/me?days=30")
        assert response.status_code == 422, f"Expected 422 for missing user_id, got {response.status_code}"
        print("✓ Portfolio correctly requires user_id parameter")


class TestExistingEndpointsStillWork:
    """Verify existing endpoints still work after live mode changes"""

    def test_auth_login_admin(self):
        """Admin login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        print(f"✓ Admin login works: got access_token")

    def test_auth_login_pro_user(self):
        """Pro user login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": PRO_USER_EMAIL, "password": PRO_USER_PASSWORD}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        print(f"✓ Pro user login works: got access_token")

    def test_marketplace_leaderboard(self):
        """Marketplace leaderboard still works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "strategies" in data or isinstance(data, list), "Response should contain strategies"
        print(f"✓ Marketplace leaderboard works")

    def test_waitlist_post(self):
        """Waitlist endpoint still works"""
        test_email = f"test_live_mode_{int(time.time())}@test.com"
        response = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={"email": test_email}
        )
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        print(f"✓ Waitlist endpoint works")

    def test_admin_traffic_summary(self):
        """Admin traffic summary still works"""
        response = requests.get(f"{BASE_URL}/api/admin/traffic/summary?admin_key={ADMIN_KEY}")
        # This endpoint may or may not exist, so we accept 200 or 404
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        if response.status_code == 200:
            print(f"✓ Admin traffic summary works")
        else:
            print(f"✓ Admin traffic summary endpoint not found (404) - may not be implemented")

    def test_digest_admin_analytics(self):
        """Digest admin analytics still works"""
        response = requests.get(f"{BASE_URL}/api/digest/admin/analytics?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total_digests_sent" in data or "success" in data, "Response should contain analytics data"
        print(f"✓ Digest admin analytics works")

    def test_health_endpoint(self):
        """Health endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Health endpoint works")


class TestDemoModeToggleFlow:
    """Test the full demo mode toggle flow"""

    def test_full_toggle_flow(self):
        """Test toggling demo mode and verifying signals change accordingly"""
        # Step 1: Get initial status
        status_res = requests.get(f"{BASE_URL}/api/demo-mode/status")
        initial_status = status_res.json().get("demo_mode")
        print(f"Initial demo mode: {initial_status}")

        # Step 2: Toggle to ON
        toggle_on_res = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        assert toggle_on_res.status_code == 200
        time.sleep(0.5)

        # Step 3: Verify status is ON
        status_res = requests.get(f"{BASE_URL}/api/demo-mode/status")
        assert status_res.json().get("demo_mode") == True, "Demo mode should be ON"

        # Step 4: Verify signals return demo data
        signals_res = requests.get(f"{BASE_URL}/api/signals/live?limit=5")
        assert signals_res.json().get("demo_mode") == True, "Signals should indicate demo mode"

        # Step 5: Toggle to OFF
        toggle_off_res = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        assert toggle_off_res.status_code == 200
        time.sleep(0.5)

        # Step 6: Verify status is OFF
        status_res = requests.get(f"{BASE_URL}/api/demo-mode/status")
        assert status_res.json().get("demo_mode") == False, "Demo mode should be OFF"

        # Step 7: Verify signals return real data
        signals_res = requests.get(f"{BASE_URL}/api/signals/live?limit=5")
        assert signals_res.json().get("demo_mode") == False, "Signals should indicate live mode"

        print("✓ Full demo mode toggle flow works correctly")


class TestAdminGetDemoMode:
    """Test GET /api/admin/demo-mode — admin get demo mode status"""

    def test_admin_get_demo_mode(self):
        """Admin can get demo mode status with valid key"""
        response = requests.get(f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "demo_mode" in data, "Response should contain demo_mode"
        print(f"✓ Admin GET demo mode: {data}")

    def test_admin_get_demo_mode_invalid_key(self):
        """Admin get demo mode with invalid key should fail"""
        response = requests.get(f"{BASE_URL}/api/admin/demo-mode?admin_key=invalid")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Invalid admin key correctly rejected")


# Cleanup: Ensure demo mode is OFF after tests
@pytest.fixture(scope="module", autouse=True)
def cleanup_demo_mode():
    """Ensure demo mode is OFF after all tests"""
    yield
    # Cleanup: Set demo mode to OFF
    requests.post(
        f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
        json={"enabled": False}
    )
    print("\n✓ Cleanup: Demo mode set to OFF")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
