"""
Marketplace Billing API Tests - Stripe Checkout Integration
Tests: checkout, status polling, cancel-subscription endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"

# Known strategy ID owned by free user
STRATEGY_ID = "d2dc6982-c6fb-4851-b48e-0130cf7f76da"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def free_user_token(api_client):
    """Get token for free user (strategy creator)"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": FREE_USER_EMAIL,
        "password": FREE_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Free user login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def pro_user_token(api_client):
    """Get token for pro user (subscriber)"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": PRO_USER_EMAIL,
        "password": PRO_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Pro user login failed: {response.status_code} - {response.text}")


class TestCheckoutEndpoint:
    """Tests for POST /api/marketplace/strategies/{id}/checkout"""
    
    def test_checkout_returns_stripe_url_for_valid_subscriber(self, api_client, pro_user_token):
        """Pro user (not owner) should get a Stripe checkout URL"""
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/{STRATEGY_ID}/checkout",
            json={"origin_url": "https://alpha-trading-hub.preview.emergentagent.com"},
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        
        # Could be 200 (success) or 409 (already subscribed)
        if response.status_code == 200:
            data = response.json()
            assert "url" in data, "Response should contain checkout URL"
            assert "session_id" in data, "Response should contain session_id"
            assert data["url"].startswith("https://checkout.stripe.com"), f"URL should be Stripe checkout: {data['url']}"
            print(f"SUCCESS: Checkout URL returned: {data['url'][:80]}...")
        elif response.status_code == 409:
            data = response.json()
            assert "Already subscribed" in data.get("detail", ""), "409 should indicate already subscribed"
            print(f"INFO: User already subscribed (expected behavior)")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")
    
    def test_checkout_rejects_self_subscription(self, api_client, free_user_token):
        """Creator cannot subscribe to their own strategy"""
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/{STRATEGY_ID}/checkout",
            json={"origin_url": "https://alpha-trading-hub.preview.emergentagent.com"},
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        
        assert response.status_code == 400, f"Expected 400 for self-subscription, got {response.status_code}"
        data = response.json()
        assert "own strategy" in data.get("detail", "").lower(), f"Error should mention own strategy: {data}"
        print(f"SUCCESS: Self-subscription correctly rejected")
    
    def test_checkout_requires_authentication(self, api_client):
        """Checkout should require authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/{STRATEGY_ID}/checkout",
            json={"origin_url": "https://alpha-trading-hub.preview.emergentagent.com"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"SUCCESS: Unauthenticated request rejected with {response.status_code}")
    
    def test_checkout_returns_404_for_invalid_strategy(self, api_client, pro_user_token):
        """Checkout should return 404 for non-existent strategy"""
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/invalid-strategy-id-12345/checkout",
            json={"origin_url": "https://alpha-trading-hub.preview.emergentagent.com"},
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        
        assert response.status_code == 404, f"Expected 404 for invalid strategy, got {response.status_code}"
        print(f"SUCCESS: Invalid strategy returns 404")


class TestCancelSubscriptionEndpoint:
    """Tests for POST /api/marketplace/strategies/{id}/cancel-subscription"""
    
    def test_cancel_returns_404_when_no_active_subscription(self, api_client, pro_user_token):
        """Cancel should return 404 when user has no active subscription"""
        # Use a strategy the pro user is NOT subscribed to
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/{STRATEGY_ID}/cancel-subscription",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        
        # Could be 200 (if subscribed) or 404 (if not subscribed)
        if response.status_code == 404:
            data = response.json()
            assert "No active subscription" in data.get("detail", ""), f"404 should indicate no subscription: {data}"
            print(f"SUCCESS: Cancel correctly returns 404 when no subscription exists")
        elif response.status_code == 200:
            data = response.json()
            assert "canceled" in data.get("message", "").lower(), f"200 should confirm cancellation: {data}"
            print(f"INFO: Subscription was canceled (user was subscribed)")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")
    
    def test_cancel_requires_authentication(self, api_client):
        """Cancel should require authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/{STRATEGY_ID}/cancel-subscription"
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"SUCCESS: Unauthenticated cancel rejected with {response.status_code}")


class TestStatusPollingEndpoint:
    """Tests for GET /api/marketplace/checkout/status/{session_id}"""
    
    def test_status_returns_404_for_invalid_session(self, api_client, pro_user_token):
        """Status polling should return 404 for non-existent session"""
        response = api_client.get(
            f"{BASE_URL}/api/marketplace/checkout/status/invalid_session_12345",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        
        assert response.status_code == 404, f"Expected 404 for invalid session, got {response.status_code}"
        data = response.json()
        assert "not found" in data.get("detail", "").lower(), f"Error should indicate not found: {data}"
        print(f"SUCCESS: Invalid session returns 404")
    
    def test_status_requires_authentication(self, api_client):
        """Status polling should require authentication"""
        response = api_client.get(
            f"{BASE_URL}/api/marketplace/checkout/status/some_session_id"
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"SUCCESS: Unauthenticated status request rejected with {response.status_code}")


class TestMarketplaceListingStillWorks:
    """Verify existing marketplace endpoints still work"""
    
    def test_marketplace_listing_loads(self, api_client):
        """Marketplace listing should still work"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies")
        
        assert response.status_code == 200, f"Marketplace listing failed: {response.status_code}"
        data = response.json()
        assert "strategies" in data, "Response should contain strategies list"
        assert isinstance(data["strategies"], list), "Strategies should be a list"
        print(f"SUCCESS: Marketplace listing returns {len(data['strategies'])} strategies")
    
    def test_strategy_detail_loads(self, api_client):
        """Strategy detail page should still work"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/{STRATEGY_ID}")
        
        assert response.status_code == 200, f"Strategy detail failed: {response.status_code}"
        data = response.json()
        assert "strategy" in data, "Response should contain strategy"
        assert data["strategy"]["id"] == STRATEGY_ID, "Strategy ID should match"
        print(f"SUCCESS: Strategy detail loads for {data['strategy']['name']}")


class TestCreatorDashboardStillWorks:
    """Verify creator dashboard endpoints still work"""
    
    def test_creator_strategies_loads(self, api_client, free_user_token):
        """Creator strategies endpoint should still work"""
        response = api_client.get(
            f"{BASE_URL}/api/marketplace/me/created",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        
        assert response.status_code == 200, f"Creator strategies failed: {response.status_code}"
        data = response.json()
        assert "strategies" in data, "Response should contain strategies"
        print(f"SUCCESS: Creator dashboard returns {len(data['strategies'])} strategies")


class TestMySubscriptionsStillWorks:
    """Verify my subscriptions endpoint still works"""
    
    def test_my_subscriptions_loads(self, api_client, pro_user_token):
        """My subscriptions endpoint should still work"""
        response = api_client.get(
            f"{BASE_URL}/api/marketplace/me/strategies",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        
        assert response.status_code == 200, f"My subscriptions failed: {response.status_code}"
        data = response.json()
        assert "subscriptions" in data, "Response should contain subscriptions"
        print(f"SUCCESS: My subscriptions returns {len(data['subscriptions'])} subscriptions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
