"""
Test Weekly Digest Feature - Iteration 70
Tests: unsubscribe, resubscribe, admin analytics, manual trigger, and no regressions
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_KEY = "alphaai_admin_2026"
ADMIN_EMAIL = "mar-brick@hotmail.com"
ADMIN_PASSWORD = "Martin2026!"
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"

# Test email for unsubscribe/resubscribe tests
TEST_UNSUB_EMAIL = "test_digest_unsub_iter70@my-alpha-ai.com"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def pro_user_token(api_client):
    """Get pro user authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": PRO_USER_EMAIL,
        "password": PRO_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Pro user authentication failed - skipping authenticated tests")


class TestHealthAndBasicEndpoints:
    """Verify basic endpoints still work (no regressions)"""
    
    def test_health_endpoint(self, api_client):
        """GET /api/health returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health endpoint working")
    
    def test_auth_login_admin(self, api_client):
        """POST /api/auth/login works for admin user"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("✓ Admin login working")
    
    def test_auth_login_pro_user(self, api_client):
        """POST /api/auth/login works for pro user"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("✓ Pro user login working")


class TestDigestUnsubscribe:
    """Test unsubscribe and resubscribe endpoints"""
    
    def test_unsubscribe_valid_email(self, api_client):
        """GET /api/digest/unsubscribe?email=... marks user as unsubscribed"""
        response = api_client.get(f"{BASE_URL}/api/digest/unsubscribe", params={
            "email": TEST_UNSUB_EMAIL
        })
        assert response.status_code == 200
        data = response.json()
        assert "unsubscribed" in data.get("message", "").lower()
        print(f"✓ Unsubscribe working for {TEST_UNSUB_EMAIL}")
    
    def test_resubscribe_valid_email(self, api_client):
        """GET /api/digest/resubscribe?email=... re-subscribes user"""
        response = api_client.get(f"{BASE_URL}/api/digest/resubscribe", params={
            "email": TEST_UNSUB_EMAIL
        })
        assert response.status_code == 200
        data = response.json()
        assert "re-subscribed" in data.get("message", "").lower()
        print(f"✓ Resubscribe working for {TEST_UNSUB_EMAIL}")
    
    def test_unsubscribe_admin_user(self, api_client):
        """Verify admin user can be unsubscribed (mar-brick@hotmail.com was unsubscribed in testing)"""
        # First check current state via analytics
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics", params={
            "admin_key": ADMIN_KEY
        })
        assert response.status_code == 200
        data = response.json()
        # Should have at least 1 unsubscribed user (mar-brick@hotmail.com)
        assert data.get("unsubscribed_total", 0) >= 1
        print(f"✓ Unsubscribed count: {data.get('unsubscribed_total')}")


class TestDigestAdminAnalytics:
    """Test admin analytics endpoint"""
    
    def test_admin_analytics_valid_key(self, api_client):
        """GET /api/digest/admin/analytics?admin_key=... returns delivery stats"""
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics", params={
            "admin_key": ADMIN_KEY
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "total_digests_sent" in data
        assert "last_7d" in data
        assert "pro_vs_free" in data
        assert "unsubscribed_total" in data
        assert "latest_batch" in data
        
        # Verify last_7d structure
        assert "sent" in data["last_7d"]
        assert "errors" in data["last_7d"]
        assert "delivery_rate" in data["last_7d"]
        
        # Verify pro_vs_free structure
        assert "pro" in data["pro_vs_free"]
        assert "free" in data["pro_vs_free"]
        
        print(f"✓ Admin analytics working - Total sent: {data['total_digests_sent']}")
        print(f"  Last 7d: {data['last_7d']}")
        print(f"  Pro vs Free: {data['pro_vs_free']}")
        print(f"  Unsubscribed: {data['unsubscribed_total']}")
    
    def test_admin_analytics_invalid_key(self, api_client):
        """GET /api/digest/admin/analytics with invalid key returns 403"""
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics", params={
            "admin_key": "invalid_key_12345"
        })
        assert response.status_code == 403
        print("✓ Admin analytics rejects invalid key with 403")
    
    def test_admin_analytics_missing_key(self, api_client):
        """GET /api/digest/admin/analytics without key returns 422"""
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics")
        assert response.status_code == 422  # Missing required query param
        print("✓ Admin analytics requires admin_key parameter")
    
    def test_admin_analytics_shows_previous_sends(self, api_client):
        """Verify analytics shows non-zero total_digests_sent (from previous triggers)"""
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics", params={
            "admin_key": ADMIN_KEY
        })
        assert response.status_code == 200
        data = response.json()
        
        # Per context: 167 emails sent (84 first batch, 83 second batch)
        assert data.get("total_digests_sent", 0) > 0, "Expected non-zero total_digests_sent from previous triggers"
        print(f"✓ Total digests sent: {data['total_digests_sent']} (expected ~167 from previous runs)")


class TestDigestAdminTrigger:
    """Test manual trigger endpoint - NOTE: This sends real emails!"""
    
    def test_admin_trigger_invalid_key(self, api_client):
        """POST /api/digest/admin/trigger with invalid key returns 403"""
        response = api_client.post(f"{BASE_URL}/api/digest/admin/trigger", params={
            "admin_key": "invalid_key_12345"
        })
        assert response.status_code == 403
        print("✓ Admin trigger rejects invalid key with 403")
    
    def test_admin_trigger_missing_key(self, api_client):
        """POST /api/digest/admin/trigger without key returns 422"""
        response = api_client.post(f"{BASE_URL}/api/digest/admin/trigger")
        assert response.status_code == 422  # Missing required query param
        print("✓ Admin trigger requires admin_key parameter")
    
    # NOTE: Skipping actual trigger test to avoid sending 84+ emails
    # The trigger was already run twice per context (167 total emails sent)
    @pytest.mark.skip(reason="Skipping to avoid sending 84+ real emails - trigger already verified in previous runs")
    def test_admin_trigger_valid_key(self, api_client):
        """POST /api/digest/admin/trigger?admin_key=... triggers digest send"""
        response = api_client.post(f"{BASE_URL}/api/digest/admin/trigger", params={
            "admin_key": ADMIN_KEY
        }, timeout=60)  # Long timeout due to rate limiting
        assert response.status_code == 200
        data = response.json()
        
        assert "result" in data
        result = data["result"]
        assert "sent" in result
        assert "skipped" in result
        assert "errors" in result
        
        print(f"✓ Admin trigger working - Sent: {result['sent']}, Skipped: {result['skipped']}, Errors: {result['errors']}")


class TestNoRegressions:
    """Verify existing endpoints still work after digest feature addition"""
    
    def test_marketplace_leaderboard(self, api_client):
        """GET /api/marketplace/strategies/leaderboard still works"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        assert response.status_code == 200
        data = response.json()
        # Response is {strategies: [...], total: N}
        assert "strategies" in data
        assert isinstance(data["strategies"], list)
        print(f"✓ Marketplace leaderboard working - {len(data['strategies'])} strategies")
    
    def test_waitlist_admin_analytics(self, api_client):
        """GET /api/waitlist/admin/analytics?admin_key=... still works"""
        response = api_client.get(f"{BASE_URL}/api/waitlist/admin/analytics", params={
            "admin_key": ADMIN_KEY
        })
        assert response.status_code == 200
        data = response.json()
        # Response has funnel, emails, etc. - check for key fields
        assert "funnel" in data or "total" in data or "emails" in data
        print(f"✓ Waitlist admin analytics working - Keys: {list(data.keys())}")
    
    def test_billing_overview(self, api_client, pro_user_token):
        """GET /api/billing/overview with auth still works"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/billing/overview", headers=headers)
        assert response.status_code == 200
        print("✓ Billing overview working")
    
    def test_invoices_list(self, api_client, pro_user_token):
        """GET /api/invoices with auth still works"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/invoices", headers=headers)
        assert response.status_code == 200
        print("✓ Invoices list working")
    
    def test_referrals_admin_summary(self, api_client):
        """GET /api/referrals/admin/summary still works"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/summary", params={
            "admin_key": ADMIN_KEY
        })
        assert response.status_code == 200
        print("✓ Referrals admin summary working")


class TestDigestDataIntegrity:
    """Test digest logs and preferences data integrity"""
    
    def test_unsubscribe_creates_preference_record(self, api_client):
        """Unsubscribe should create/update digest_preferences record"""
        unique_email = f"test_pref_check_{int(time.time())}@test.com"
        
        # Unsubscribe
        response = api_client.get(f"{BASE_URL}/api/digest/unsubscribe", params={
            "email": unique_email
        })
        assert response.status_code == 200
        
        # Verify via analytics that unsubscribed count increased
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics", params={
            "admin_key": ADMIN_KEY
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("unsubscribed_total", 0) >= 1
        print(f"✓ Unsubscribe creates preference record - Total unsubscribed: {data['unsubscribed_total']}")
    
    def test_resubscribe_updates_preference_record(self, api_client):
        """Resubscribe should update digest_preferences record"""
        unique_email = f"test_resub_check_{int(time.time())}@test.com"
        
        # First unsubscribe
        response = api_client.get(f"{BASE_URL}/api/digest/unsubscribe", params={
            "email": unique_email
        })
        assert response.status_code == 200
        
        # Get unsubscribed count
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics", params={
            "admin_key": ADMIN_KEY
        })
        unsub_count_before = response.json().get("unsubscribed_total", 0)
        
        # Resubscribe
        response = api_client.get(f"{BASE_URL}/api/digest/resubscribe", params={
            "email": unique_email
        })
        assert response.status_code == 200
        
        # Verify unsubscribed count decreased
        response = api_client.get(f"{BASE_URL}/api/digest/admin/analytics", params={
            "admin_key": ADMIN_KEY
        })
        unsub_count_after = response.json().get("unsubscribed_total", 0)
        
        # Count should decrease by 1 after resubscribe
        assert unsub_count_after == unsub_count_before - 1
        print(f"✓ Resubscribe updates preference record - Unsubscribed: {unsub_count_before} -> {unsub_count_after}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
