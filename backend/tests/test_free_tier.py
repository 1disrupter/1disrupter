"""
AlphaAI Free Tier Implementation Tests
Tests for:
- GET /api/auth/me returns user_tier field
- GET /api/payments/packages returns 4 packages (pro_monthly, pro_yearly, elite_monthly, elite_yearly)
- POST /api/trading/execute blocks live trades for free users (403)
- GET /api/leaderboard returns max 10 traders for user_tier=free
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"


class TestAuthMeUserTier:
    """Test that /api/auth/me returns user_tier field"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    def test_auth_me_returns_user_tier(self, auth_token):
        """GET /api/auth/me should return user_tier field"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Auth/me failed: {response.text}"
        data = response.json()
        
        # Verify user_tier field exists
        assert "user_tier" in data, "user_tier field missing from /api/auth/me response"
        
        # Verify user_tier is one of the valid values
        assert data["user_tier"] in ["free", "pro", "elite"], f"Invalid user_tier: {data['user_tier']}"
        
        # For demo_test2 user, should be 'pro' based on is_pro=true
        print(f"User tier: {data['user_tier']}")
        print(f"is_pro: {data.get('is_pro')}")
        print(f"is_elite: {data.get('is_elite')}")
    
    def test_auth_me_has_required_fields(self, auth_token):
        """Verify /api/auth/me returns all required fields"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "email", "name", "is_verified", "is_pro", "is_elite", "has_2fa", "user_tier"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestPaymentsPackages:
    """Test GET /api/payments/packages returns 4 packages"""
    
    def test_packages_endpoint_returns_4_packages(self):
        """GET /api/payments/packages should return 4 packages"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200, f"Packages endpoint failed: {response.text}"
        data = response.json()
        
        assert "packages" in data, "packages field missing from response"
        packages = data["packages"]
        
        assert len(packages) == 4, f"Expected 4 packages, got {len(packages)}"
        
        # Verify package IDs
        package_ids = [p["id"] for p in packages]
        expected_ids = ["pro_monthly", "pro_yearly", "elite_monthly", "elite_yearly"]
        
        for expected_id in expected_ids:
            assert expected_id in package_ids, f"Missing package: {expected_id}"
        
        print(f"Package IDs: {package_ids}")
    
    def test_pro_monthly_package_details(self):
        """Verify pro_monthly package has correct price"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200
        data = response.json()
        
        pro_monthly = next((p for p in data["packages"] if p["id"] == "pro_monthly"), None)
        assert pro_monthly is not None, "pro_monthly package not found"
        
        assert pro_monthly["price"] == 29.00, f"Expected $29, got ${pro_monthly['price']}"
        assert pro_monthly["tier"] == "pro", f"Expected tier 'pro', got '{pro_monthly['tier']}'"
        assert pro_monthly["period"] == "month", f"Expected period 'month', got '{pro_monthly['period']}'"
        
        print(f"Pro Monthly: ${pro_monthly['price']}/month")
    
    def test_elite_monthly_package_details(self):
        """Verify elite_monthly package has correct price"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200
        data = response.json()
        
        elite_monthly = next((p for p in data["packages"] if p["id"] == "elite_monthly"), None)
        assert elite_monthly is not None, "elite_monthly package not found"
        
        assert elite_monthly["price"] == 79.00, f"Expected $79, got ${elite_monthly['price']}"
        assert elite_monthly["tier"] == "elite", f"Expected tier 'elite', got '{elite_monthly['tier']}'"
        
        print(f"Elite Monthly: ${elite_monthly['price']}/month")
    
    def test_yearly_packages_have_savings(self):
        """Verify yearly packages have savings info"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200
        data = response.json()
        
        pro_yearly = next((p for p in data["packages"] if p["id"] == "pro_yearly"), None)
        elite_yearly = next((p for p in data["packages"] if p["id"] == "elite_yearly"), None)
        
        assert pro_yearly is not None, "pro_yearly package not found"
        assert elite_yearly is not None, "elite_yearly package not found"
        
        # Check prices
        assert pro_yearly["price"] == 249.00, f"Expected $249, got ${pro_yearly['price']}"
        assert elite_yearly["price"] == 699.00, f"Expected $699, got ${elite_yearly['price']}"
        
        print(f"Pro Yearly: ${pro_yearly['price']}/year")
        print(f"Elite Yearly: ${elite_yearly['price']}/year")


class TestTradingExecuteTierRestriction:
    """Test POST /api/trading/execute blocks live trades for free users"""
    
    def test_live_trade_blocked_for_free_user(self):
        """Free users should get 403 when trying to execute live trades"""
        # Use a wallet address that doesn't have Pro status
        free_wallet = "0xFREE_TEST_WALLET_NO_PRO_STATUS"
        
        # First register the wallet
        requests.post(f"{BASE_URL}/api/investors/register", json={
            "wallet_address": free_wallet
        })
        
        # Try to execute a live trade
        response = requests.post(f"{BASE_URL}/api/trading/execute", json={
            "wallet_address": free_wallet,
            "symbol": "BTC",
            "side": "BUY",
            "amount_usd": 100,
            "is_live": True  # Live trade
        })
        
        # Should be blocked with 403
        assert response.status_code == 403, f"Expected 403 for free user live trade, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data
        assert "Pro" in data["detail"] or "Elite" in data["detail"] or "Free" in data["detail"].lower(), \
            f"Error message should mention tier restriction: {data['detail']}"
        
        print(f"Free user live trade blocked: {data['detail']}")
    
    def test_paper_trade_allowed_for_free_user(self):
        """Free users should be able to execute paper trades"""
        free_wallet = "0xFREE_TEST_WALLET_PAPER_TRADE"
        
        # Register the wallet
        requests.post(f"{BASE_URL}/api/investors/register", json={
            "wallet_address": free_wallet
        })
        
        # Try to execute a paper trade
        response = requests.post(f"{BASE_URL}/api/trading/execute", json={
            "wallet_address": free_wallet,
            "symbol": "BTC",
            "side": "BUY",
            "amount_usd": 100,
            "is_live": False  # Paper trade
        })
        
        # Paper trade should succeed (200) or fail for other reasons (not 403)
        assert response.status_code != 403, f"Paper trade should not be blocked by tier: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True, f"Paper trade should succeed: {data}"
            print(f"Paper trade executed successfully")
        else:
            print(f"Paper trade response: {response.status_code} - {response.text}")


class TestLeaderboardTierRestriction:
    """Test GET /api/leaderboard returns max 10 traders for free users"""
    
    def test_leaderboard_free_tier_limit(self):
        """Free users should see max 10 traders on leaderboard"""
        response = requests.get(f"{BASE_URL}/api/leaderboard", params={
            "user_tier": "free",
            "limit": 50  # Request more than 10
        })
        
        assert response.status_code == 200, f"Leaderboard failed: {response.text}"
        data = response.json()
        
        # Check if there's a limit applied for free users
        traders = data.get("traders", data.get("leaderboard", []))
        
        # Free users should see max 10 traders
        if len(traders) > 0:
            assert len(traders) <= 10, f"Free users should see max 10 traders, got {len(traders)}"
            print(f"Free tier leaderboard: {len(traders)} traders (max 10)")
        
        # Verify the limit is set to 10 for free users (even if requested 50)
        assert data.get("limit") == 10, f"Free tier limit should be 10, got {data.get('limit')}"
        
        print(f"Leaderboard response keys: {data.keys()}")
    
    def test_leaderboard_pro_tier_full_access(self):
        """Pro users should see full leaderboard"""
        response = requests.get(f"{BASE_URL}/api/leaderboard", params={
            "user_tier": "pro",
            "limit": 50
        })
        
        assert response.status_code == 200, f"Leaderboard failed: {response.text}"
        data = response.json()
        
        traders = data.get("traders", data.get("leaderboard", []))
        
        # Pro users should see more than 10 if available
        print(f"Pro tier leaderboard: {len(traders)} traders")
        
        # Check for full access flag
        if "is_limited" in data:
            assert data["is_limited"] == False, "Pro tier should have is_limited=False"


class TestLoginFlow:
    """Test login flow still works"""
    
    def test_login_with_test_credentials(self):
        """Login with demo_test2@my-alpha-ai.com / NewPass1234!"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        assert "access_token" in data, "access_token missing from login response"
        assert "user" in data, "user missing from login response"
        
        user = data["user"]
        assert user["email"] == PRO_USER_EMAIL, f"Email mismatch: {user['email']}"
        assert "user_tier" in user, "user_tier missing from user object"
        
        print(f"Login successful: {user['email']} (tier: {user['user_tier']})")
    
    def test_login_returns_user_tier_in_response(self):
        """Login response should include user_tier"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json()
        
        user = data["user"]
        assert "user_tier" in user, "user_tier missing from login response user object"
        assert user["user_tier"] in ["free", "pro", "elite"], f"Invalid user_tier: {user['user_tier']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
