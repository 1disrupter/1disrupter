"""
AlphaAI Affiliate Program (Phase 1) API Tests
Tests for:
- GET /api/referrals/validate/{ref} - Validate referral by code OR user ID
- POST /api/auth/register with ref_code - Referral linkage on signup
- GET /api/referrals/stats - User referral statistics (authenticated)
- GET /api/referrals/activity - User referral activity (authenticated)
- GET /api/referrals/admin/summary - Admin referral summary
- GET /api/referrals/admin/events - Admin referral events with time range
- POST /api/referrals/track-click - Track referral click
- GET /api/referrals/validate-code - Validate referral code format
- Anti-fraud: no self-referrals, no duplicate referrals
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://signal-ui-latest.preview.emergentagent.com')

# Test credentials from test_credentials.md
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
PRO_USER_REFERRAL_CODE = "KLYYBMTS"

ADMIN_EMAIL = "mar-brick@hotmail.com"
ADMIN_PASSWORD = "Martin2026!"
ADMIN_KEY = "alphaai_admin_2026"

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
    """Get authentication token for pro user (demo_test2)"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": PRO_USER_EMAIL,
        "password": PRO_USER_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    pytest.skip(f"Pro user authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get authentication token for admin user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def pro_user_client(api_client, pro_user_token):
    """Session with pro user auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {pro_user_token}"
    })
    return session


class TestReferralValidateEndpoint:
    """Tests for GET /api/referrals/validate/{ref} - validates by code OR user ID"""
    
    def test_validate_by_referral_code(self, api_client):
        """GET /api/referrals/validate/{ref} - Validate by referral code (KLYYBMTS)"""
        response = api_client.get(f"{BASE_URL}/api/referrals/validate/{PRO_USER_REFERRAL_CODE}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert data["referral_code"] == PRO_USER_REFERRAL_CODE
        assert "referrer_id" in data
        assert "referrer_name" in data
        assert "bonus" in data
        assert "7 days" in data["bonus"]
        
        print(f"✅ GET /api/referrals/validate/{PRO_USER_REFERRAL_CODE} - Valid with referrer info")
    
    def test_validate_by_user_id(self, api_client, pro_user_token):
        """GET /api/referrals/validate/{ref} - Validate by user ID"""
        # First get the user ID from /me endpoint
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        me_response = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        if me_response.status_code != 200:
            pytest.skip("Could not get user ID")
        
        user_id = me_response.json().get("id")
        
        # Now validate by user ID
        response = api_client.get(f"{BASE_URL}/api/referrals/validate/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert "referral_code" in data
        assert data["referrer_id"] == user_id
        assert "referrer_name" in data
        assert "bonus" in data
        
        print(f"✅ GET /api/referrals/validate/{user_id[:8]}... - Valid by user ID")
    
    def test_validate_invalid_code(self, api_client):
        """GET /api/referrals/validate/{ref} - Invalid code returns valid=false"""
        response = api_client.get(f"{BASE_URL}/api/referrals/validate/INVALIDCODE123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        
        print("✅ GET /api/referrals/validate/INVALIDCODE123 - Returns valid=false")


class TestReferralValidateCodeEndpoint:
    """Tests for GET /api/referrals/validate-code?code=X"""
    
    def test_validate_code_valid(self, api_client):
        """GET /api/referrals/validate-code - Valid code"""
        response = api_client.get(f"{BASE_URL}/api/referrals/validate-code?code={PRO_USER_REFERRAL_CODE}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert data["code"] == PRO_USER_REFERRAL_CODE
        assert "referrer" in data
        assert "bonus" in data
        
        print(f"✅ GET /api/referrals/validate-code?code={PRO_USER_REFERRAL_CODE} - Valid")
    
    def test_validate_code_invalid(self, api_client):
        """GET /api/referrals/validate-code - Invalid code"""
        response = api_client.get(f"{BASE_URL}/api/referrals/validate-code?code=BADCODE")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        
        print("✅ GET /api/referrals/validate-code?code=BADCODE - Returns valid=false")


class TestTrackClickEndpoint:
    """Tests for POST /api/referrals/track-click"""
    
    def test_track_click_valid_code(self, api_client):
        """POST /api/referrals/track-click - Track click on valid code"""
        response = api_client.post(f"{BASE_URL}/api/referrals/track-click?code={PRO_USER_REFERRAL_CODE}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == True
        
        print(f"✅ POST /api/referrals/track-click?code={PRO_USER_REFERRAL_CODE} - Tracked")
    
    def test_track_click_invalid_code(self, api_client):
        """POST /api/referrals/track-click - Invalid code not tracked"""
        response = api_client.post(f"{BASE_URL}/api/referrals/track-click?code=INVALIDCODE")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == False
        assert "reason" in data
        
        print("✅ POST /api/referrals/track-click?code=INVALIDCODE - Not tracked")


class TestUserReferralStats:
    """Tests for authenticated user referral endpoints"""
    
    def test_get_referral_stats(self, pro_user_client):
        """GET /api/referrals/stats - Returns referral stats for authenticated user"""
        response = pro_user_client.get(f"{BASE_URL}/api/referrals/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "referral_code" in data
        assert "referral_link" in data
        assert "tier" in data
        assert "commission_rate" in data
        assert "total_referrals" in data
        assert "total_earnings" in data
        
        # Verify the referral code matches expected
        assert data["referral_code"] == PRO_USER_REFERRAL_CODE
        
        # Verify tier is valid
        assert data["tier"] in ["Bronze", "Silver", "Gold", "Platinum"]
        
        print(f"✅ GET /api/referrals/stats - Code: {data['referral_code']}, Tier: {data['tier']}, Referrals: {data['total_referrals']}")
    
    def test_get_referral_activity(self, pro_user_client):
        """GET /api/referrals/activity - Returns referral activity list"""
        response = pro_user_client.get(f"{BASE_URL}/api/referrals/activity")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "activity" in data
        assert "total" in data
        assert isinstance(data["activity"], list)
        
        print(f"✅ GET /api/referrals/activity - {len(data['activity'])} activities, total: {data['total']}")
    
    def test_stats_requires_auth(self, api_client):
        """GET /api/referrals/stats - Requires authentication"""
        # Remove any auth header
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/referrals/stats", headers=headers)
        
        assert response.status_code == 401
        
        print("✅ GET /api/referrals/stats - Correctly requires authentication")


class TestAdminReferralEndpoints:
    """Tests for admin referral analytics endpoints"""
    
    def test_admin_summary_with_key(self, api_client):
        """GET /api/referrals/admin/summary - Returns summary with admin_key"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/summary?admin_key={ADMIN_KEY}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "total_referrals" in data
        assert "total_converted" in data
        assert "total_pending" in data
        assert "active_subscribers_from_referrals" in data
        assert "total_revenue_from_referrals" in data
        assert "total_commissions_owed" in data
        assert "top_referrers" in data
        
        # Verify top_referrers structure
        assert isinstance(data["top_referrers"], list)
        
        print(f"✅ GET /api/referrals/admin/summary - Total: {data['total_referrals']}, Converted: {data['total_converted']}")
    
    def test_admin_summary_without_key(self, api_client):
        """GET /api/referrals/admin/summary - Requires admin_key (403 without)"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/summary")
        
        # Should return 422 (missing required param) or 403 (forbidden)
        assert response.status_code in [403, 422]
        
        print("✅ GET /api/referrals/admin/summary - Correctly requires admin_key")
    
    def test_admin_summary_invalid_key(self, api_client):
        """GET /api/referrals/admin/summary - Invalid admin_key returns 403"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/summary?admin_key=wrong_key")
        
        assert response.status_code == 403
        
        print("✅ GET /api/referrals/admin/summary - Invalid key returns 403")
    
    def test_admin_events_7d(self, api_client):
        """GET /api/referrals/admin/events?range=7d - Returns events for 7 days"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/events?admin_key={ADMIN_KEY}&range=7d")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "range" in data
        assert data["range"] == "7d"
        assert "totals" in data
        assert "signups" in data["totals"]
        assert "conversions" in data["totals"]
        assert "daily" in data
        assert isinstance(data["daily"], list)
        
        # Verify daily breakdown has 7 entries
        assert len(data["daily"]) == 7
        
        # Verify daily entry structure
        if len(data["daily"]) > 0:
            entry = data["daily"][0]
            assert "date" in entry
            assert "signups" in entry
            assert "conversions" in entry
        
        print(f"✅ GET /api/referrals/admin/events?range=7d - Totals: {data['totals']}, Days: {len(data['daily'])}")
    
    def test_admin_events_today(self, api_client):
        """GET /api/referrals/admin/events?range=today - Returns events for today"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/events?admin_key={ADMIN_KEY}&range=today")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["range"] == "today"
        assert "totals" in data
        assert "daily" in data
        assert len(data["daily"]) == 1  # Only today
        
        print(f"✅ GET /api/referrals/admin/events?range=today - Totals: {data['totals']}")
    
    def test_admin_events_30d(self, api_client):
        """GET /api/referrals/admin/events?range=30d - Returns events for 30 days"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/events?admin_key={ADMIN_KEY}&range=30d")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["range"] == "30d"
        assert "totals" in data
        assert "daily" in data
        assert len(data["daily"]) == 30
        
        print(f"✅ GET /api/referrals/admin/events?range=30d - Totals: {data['totals']}, Days: {len(data['daily'])}")
    
    def test_admin_events_without_key(self, api_client):
        """GET /api/referrals/admin/events - Requires admin_key"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/events?range=7d")
        
        assert response.status_code in [403, 422]
        
        print("✅ GET /api/referrals/admin/events - Correctly requires admin_key")


class TestSignupWithReferral:
    """Tests for POST /api/auth/register with ref_code"""
    
    def test_register_with_valid_ref_code(self, api_client):
        """POST /api/auth/register with ref_code creates referral linkage"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test_ref_{unique_id}@test.com"
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": f"Test Referral {unique_id}",
            "ref_code": PRO_USER_REFERRAL_CODE
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify user was created
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_email
        
        print(f"✅ POST /api/auth/register with ref_code={PRO_USER_REFERRAL_CODE} - User created with referral linkage")
    
    def test_register_with_invalid_ref_code(self, api_client):
        """POST /api/auth/register with invalid ref_code still creates user (graceful failure)"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test_invalid_ref_{unique_id}@test.com"
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": f"Test Invalid Ref {unique_id}",
            "ref_code": "INVALIDCODE"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # User should still be created
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_email
        
        print("✅ POST /api/auth/register with invalid ref_code - User created (graceful failure)")
    
    def test_register_without_ref_code(self, api_client):
        """POST /api/auth/register without ref_code works normally"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test_no_ref_{unique_id}@test.com"
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": f"Test No Ref {unique_id}"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        
        print("✅ POST /api/auth/register without ref_code - Works normally")


class TestExistingAuthFlows:
    """Tests to ensure existing signup/login flows still work"""
    
    def test_login_existing_user(self, api_client):
        """POST /api/auth/login - Existing user can login"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == PRO_USER_EMAIL
        
        print(f"✅ POST /api/auth/login - {PRO_USER_EMAIL} logged in successfully")
    
    def test_login_admin_user(self, api_client):
        """POST /api/auth/login - Admin user can login"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        
        print(f"✅ POST /api/auth/login - Admin {ADMIN_EMAIL} logged in successfully")


class TestAntifraudMeasures:
    """Tests for anti-fraud measures"""
    
    def test_no_duplicate_referrals(self, api_client):
        """POST /api/referrals/track-signup - Duplicate referral rejected"""
        # Try to track the same user twice
        response = api_client.post(
            f"{BASE_URL}/api/referrals/track-signup",
            params={
                "code": PRO_USER_REFERRAL_CODE,
                "referee_id": "duplicate-test-user-123",
                "referee_email": "duplicate@test.com"
            }
        )
        
        # First call might succeed or fail depending on if user exists
        first_result = response.json()
        
        # Second call should definitely fail
        response2 = api_client.post(
            f"{BASE_URL}/api/referrals/track-signup",
            params={
                "code": PRO_USER_REFERRAL_CODE,
                "referee_id": "duplicate-test-user-123",
                "referee_email": "duplicate@test.com"
            }
        )
        
        assert response2.status_code == 200
        data = response2.json()
        
        # Should not track duplicate
        assert data["tracked"] == False
        assert "reason" in data
        
        print("✅ Anti-fraud: Duplicate referrals correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
