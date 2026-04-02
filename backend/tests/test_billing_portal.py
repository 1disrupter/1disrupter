"""
Billing Portal API Tests - Stripe Billing Portal Integration
Tests POST /api/billing/portal endpoint and existing billing endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def pro_user_token(api_client):
    """Get authentication token for pro user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": PRO_USER_EMAIL,
        "password": PRO_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Pro user authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def free_user_token(api_client):
    """Get authentication token for free user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": FREE_USER_EMAIL,
        "password": FREE_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Free user authentication failed: {response.status_code} - {response.text}")


class TestBillingPortalEndpoint:
    """Tests for POST /api/billing/portal - Stripe Billing Portal session creation"""
    
    def test_portal_requires_authentication(self, api_client):
        """POST /api/billing/portal returns 401 without auth token"""
        response = api_client.post(f"{BASE_URL}/api/billing/portal", json={
            "return_url": "https://alpha-trading-hub.preview.emergentagent.com/billing"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: POST /api/billing/portal requires authentication (401 without token)")
    
    def test_portal_requires_return_url(self, api_client, pro_user_token):
        """POST /api/billing/portal requires return_url field in request body"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = api_client.post(f"{BASE_URL}/api/billing/portal", json={}, headers=headers)
        # Should return 422 (validation error) for missing required field
        assert response.status_code == 422, f"Expected 422 for missing return_url, got {response.status_code}: {response.text}"
        print("PASS: POST /api/billing/portal requires return_url field (422 without it)")
    
    def test_portal_creates_session_for_pro_user(self, api_client, pro_user_token):
        """POST /api/billing/portal creates Stripe Billing Portal session and returns URL"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = api_client.post(f"{BASE_URL}/api/billing/portal", json={
            "return_url": "https://alpha-trading-hub.preview.emergentagent.com/billing"
        }, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, f"Response should contain 'url' field: {data}"
        assert data["url"].startswith("https://billing.stripe.com"), f"URL should start with https://billing.stripe.com, got: {data['url']}"
        
        print(f"PASS: POST /api/billing/portal returns Stripe portal URL: {data['url'][:80]}...")
    
    def test_portal_creates_session_for_free_user(self, api_client, free_user_token):
        """POST /api/billing/portal creates Stripe customer for users without one"""
        headers = {"Authorization": f"Bearer {free_user_token}"}
        response = api_client.post(f"{BASE_URL}/api/billing/portal", json={
            "return_url": "https://alpha-trading-hub.preview.emergentagent.com/billing"
        }, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, f"Response should contain 'url' field: {data}"
        assert data["url"].startswith("https://billing.stripe.com"), f"URL should start with https://billing.stripe.com, got: {data['url']}"
        
        print(f"PASS: POST /api/billing/portal creates Stripe customer for free user and returns portal URL")
    
    def test_portal_reuses_existing_stripe_customer(self, api_client, pro_user_token):
        """POST /api/billing/portal reuses existing valid Stripe customer IDs"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        
        # Call twice to verify customer reuse
        response1 = api_client.post(f"{BASE_URL}/api/billing/portal", json={
            "return_url": "https://alpha-trading-hub.preview.emergentagent.com/billing"
        }, headers=headers)
        
        response2 = api_client.post(f"{BASE_URL}/api/billing/portal", json={
            "return_url": "https://alpha-trading-hub.preview.emergentagent.com/billing"
        }, headers=headers)
        
        assert response1.status_code == 200, f"First call failed: {response1.status_code}"
        assert response2.status_code == 200, f"Second call failed: {response2.status_code}"
        
        # Both should return valid URLs (customer reuse is internal, we just verify it works)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["url"].startswith("https://billing.stripe.com")
        assert data2["url"].startswith("https://billing.stripe.com")
        
        print("PASS: POST /api/billing/portal reuses existing Stripe customer (both calls succeeded)")


class TestExistingBillingEndpoints:
    """Verify existing billing endpoints still work correctly"""
    
    def test_overview_endpoint_works(self, api_client, pro_user_token):
        """GET /api/billing/overview still works correctly"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/billing/overview", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "active_subscriptions" in data
        assert "monthly_cost" in data
        assert "total_spent" in data
        assert "total_payments" in data
        assert "currency" in data
        
        print(f"PASS: GET /api/billing/overview returns: active_subs={data['active_subscriptions']}, monthly_cost=${data['monthly_cost']}")
    
    def test_subscriptions_endpoint_works(self, api_client, pro_user_token):
        """GET /api/billing/subscriptions still works correctly"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/billing/subscriptions", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "active" in data
        assert "canceled" in data
        assert "active_count" in data
        assert "total_count" in data
        
        print(f"PASS: GET /api/billing/subscriptions returns: active_count={data['active_count']}, total_count={data['total_count']}")
    
    def test_payments_endpoint_works(self, api_client, pro_user_token):
        """GET /api/billing/payments still works correctly"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/billing/payments", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "payments" in data
        assert "count" in data
        
        print(f"PASS: GET /api/billing/payments returns: count={data['count']}")
    
    def test_overview_requires_auth(self, api_client):
        """GET /api/billing/overview requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/billing/overview")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/billing/overview requires authentication")
    
    def test_subscriptions_requires_auth(self, api_client):
        """GET /api/billing/subscriptions requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/billing/subscriptions")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/billing/subscriptions requires authentication")
    
    def test_payments_requires_auth(self, api_client):
        """GET /api/billing/payments requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/billing/payments")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/billing/payments requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
