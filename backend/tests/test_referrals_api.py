"""
AlphaAI Referral System API Tests
Tests for:
- GET /api/referrals/config - Public referral program configuration
- POST /api/referrals/create-code - Create referral code (authenticated)
- GET /api/referrals/stats - Get referral statistics (authenticated)
- GET /api/referrals/activity - Get referral activity history (authenticated)
- GET /api/referrals/earnings - Get earnings breakdown (authenticated)
- GET /api/referrals/validate-code - Validate referral code (public)
- POST /api/referrals/track-click - Track referral link click (public)
- POST /api/referrals/track-signup - Track referred user signup
- POST /api/referrals/track-conversion - Track subscription conversion
- GET /api/referrals/leaderboard - Get top referrers (public)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://alpha-refactor-1.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test123456"
KNOWN_REFERRAL_CODE = "VGHG2FAH"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestPublicReferralEndpoints:
    """Tests for public referral endpoints (no auth required)"""
    
    def test_get_referral_config(self, api_client):
        """GET /api/referrals/config - Get referral program configuration"""
        response = api_client.get(f"{BASE_URL}/api/referrals/config")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify tiers structure
        assert "tiers" in data
        assert len(data["tiers"]) == 4  # Bronze, Silver, Gold, Platinum
        
        # Verify tier data
        tier_names = [t["name"] for t in data["tiers"]]
        assert "Bronze" in tier_names
        assert "Silver" in tier_names
        assert "Gold" in tier_names
        assert "Platinum" in tier_names
        
        # Verify commission rates (20% -> 35%)
        bronze = next(t for t in data["tiers"] if t["name"] == "Bronze")
        platinum = next(t for t in data["tiers"] if t["name"] == "Platinum")
        assert bronze["commission_rate"] == "20%"
        assert platinum["commission_rate"] == "35%"
        
        # Verify bonuses
        assert data["referrer_bonus"] == "7 days free Pro"
        assert data["referee_bonus"] == "7 days free Pro"
        
        # Verify payout settings
        assert data["min_payout"] == "$25.0"
        assert "paypal" in data["payout_methods"]
        assert "crypto" in data["payout_methods"]
        assert "bank_transfer" in data["payout_methods"]
        
        print("✅ GET /api/referrals/config - Config returned with correct tiers and bonuses")
    
    def test_validate_referral_code_valid(self, api_client):
        """GET /api/referrals/validate-code - Validate a valid referral code"""
        response = api_client.get(f"{BASE_URL}/api/referrals/validate-code?code={KNOWN_REFERRAL_CODE}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert data["code"] == KNOWN_REFERRAL_CODE
        assert "referrer" in data  # Masked email
        assert "bonus" in data
        assert "7 days" in data["bonus"]
        
        print(f"✅ GET /api/referrals/validate-code - Code {KNOWN_REFERRAL_CODE} is valid")
    
    def test_validate_referral_code_invalid(self, api_client):
        """GET /api/referrals/validate-code - Validate an invalid referral code"""
        response = api_client.get(f"{BASE_URL}/api/referrals/validate-code?code=INVALIDCODE123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        
        print("✅ GET /api/referrals/validate-code - Invalid code returns valid=false")
    
    def test_track_referral_click_valid(self, api_client):
        """POST /api/referrals/track-click - Track click on valid referral link"""
        response = api_client.post(f"{BASE_URL}/api/referrals/track-click?code={KNOWN_REFERRAL_CODE}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == True
        
        print(f"✅ POST /api/referrals/track-click - Click tracked for code {KNOWN_REFERRAL_CODE}")
    
    def test_track_referral_click_invalid(self, api_client):
        """POST /api/referrals/track-click - Track click on invalid referral link"""
        response = api_client.post(f"{BASE_URL}/api/referrals/track-click?code=INVALIDCODE")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == False
        assert "reason" in data
        
        print("✅ POST /api/referrals/track-click - Invalid code returns tracked=false")
    
    def test_get_leaderboard(self, api_client):
        """GET /api/referrals/leaderboard - Get top referrers"""
        response = api_client.get(f"{BASE_URL}/api/referrals/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leaderboard" in data
        assert isinstance(data["leaderboard"], list)
        
        # If there are entries, verify structure
        if len(data["leaderboard"]) > 0:
            entry = data["leaderboard"][0]
            assert "rank" in entry
            assert "email" in entry  # Masked
            assert "referrals" in entry
            assert "tier" in entry
            assert "tier_color" in entry
        
        print(f"✅ GET /api/referrals/leaderboard - Returned {len(data['leaderboard'])} entries")
    
    def test_get_leaderboard_with_limit(self, api_client):
        """GET /api/referrals/leaderboard - Get leaderboard with custom limit"""
        response = api_client.get(f"{BASE_URL}/api/referrals/leaderboard?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leaderboard" in data
        assert len(data["leaderboard"]) <= 5
        
        print("✅ GET /api/referrals/leaderboard - Limit parameter works")


class TestAuthenticatedReferralEndpoints:
    """Tests for authenticated referral endpoints"""
    
    def test_create_referral_code(self, authenticated_client):
        """POST /api/referrals/create-code - Create or get referral code"""
        response = authenticated_client.post(f"{BASE_URL}/api/referrals/create-code")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "code" in data
        assert "link" in data
        assert "message" in data
        assert len(data["code"]) == 8  # 8 character code
        assert "ref=" in data["link"]
        
        print(f"✅ POST /api/referrals/create-code - Code: {data['code']}")
    
    def test_get_referral_stats(self, authenticated_client):
        """GET /api/referrals/stats - Get referral statistics"""
        response = authenticated_client.get(f"{BASE_URL}/api/referrals/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields
        assert "referral_code" in data
        assert "referral_link" in data
        assert "tier" in data
        assert "tier_color" in data
        assert "commission_rate" in data
        assert "total_referrals" in data
        assert "pending_referrals" in data
        assert "converted_referrals" in data
        assert "total_earnings" in data
        assert "pending_earnings" in data
        assert "available_earnings" in data
        assert "free_days_earned" in data
        
        # Verify tier is valid
        assert data["tier"] in ["Bronze", "Silver", "Gold", "Platinum"]
        
        # Verify commission rate is in valid range (0.20 - 0.35)
        assert 0.20 <= data["commission_rate"] <= 0.35
        
        # Verify next_tier structure if not at max tier
        if data["tier"] != "Platinum":
            assert "next_tier" in data
            if data["next_tier"]:
                assert "label" in data["next_tier"]
                assert "commission_rate" in data["next_tier"]
                assert "referrals_needed" in data["next_tier"]
        
        print(f"✅ GET /api/referrals/stats - Tier: {data['tier']}, Commission: {data['commission_rate']*100}%")
    
    def test_get_referral_activity(self, authenticated_client):
        """GET /api/referrals/activity - Get referral activity history"""
        response = authenticated_client.get(f"{BASE_URL}/api/referrals/activity")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "activity" in data
        assert "total" in data
        assert isinstance(data["activity"], list)
        
        # If there are activities, verify structure
        if len(data["activity"]) > 0:
            activity = data["activity"][0]
            assert "id" in activity
            assert "type" in activity
            assert "status" in activity
            assert "timestamp" in activity
        
        print(f"✅ GET /api/referrals/activity - {len(data['activity'])} activities")
    
    def test_get_referral_activity_with_pagination(self, authenticated_client):
        """GET /api/referrals/activity - Test pagination parameters"""
        response = authenticated_client.get(f"{BASE_URL}/api/referrals/activity?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "activity" in data
        assert len(data["activity"]) <= 5
        
        print("✅ GET /api/referrals/activity - Pagination works")
    
    def test_get_earnings_breakdown(self, authenticated_client):
        """GET /api/referrals/earnings - Get earnings breakdown"""
        response = authenticated_client.get(f"{BASE_URL}/api/referrals/earnings")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields
        assert "total_earnings" in data
        assert "pending_earnings" in data
        assert "available_earnings" in data
        assert "paid_out" in data
        assert "monthly_breakdown" in data
        assert "by_plan" in data
        
        # Verify types
        assert isinstance(data["total_earnings"], (int, float))
        assert isinstance(data["pending_earnings"], (int, float))
        assert isinstance(data["available_earnings"], (int, float))
        assert isinstance(data["paid_out"], (int, float))
        assert isinstance(data["monthly_breakdown"], list)
        assert isinstance(data["by_plan"], dict)
        
        print(f"✅ GET /api/referrals/earnings - Total: ${data['total_earnings']}")
    
    def test_stats_without_auth_fails(self, api_client):
        """GET /api/referrals/stats - Should fail without auth"""
        # Remove auth header
        api_client.headers.pop("Authorization", None)
        response = api_client.get(f"{BASE_URL}/api/referrals/stats")
        
        assert response.status_code == 401
        
        print("✅ GET /api/referrals/stats - Correctly requires authentication")


class TestReferralTrackingFlow:
    """Tests for the complete referral tracking flow"""
    
    def test_track_signup_new_user(self, api_client):
        """POST /api/referrals/track-signup - Track new user signup"""
        unique_id = str(uuid.uuid4())
        
        response = api_client.post(
            f"{BASE_URL}/api/referrals/track-signup",
            params={
                "code": KNOWN_REFERRAL_CODE,
                "referee_id": f"test-referee-{unique_id}",
                "referee_email": f"referee-{unique_id}@test.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == True
        assert data["referee_bonus_days"] == 7
        assert "message" in data
        
        print(f"✅ POST /api/referrals/track-signup - New user tracked with 7 days bonus")
    
    def test_track_signup_duplicate_user(self, api_client):
        """POST /api/referrals/track-signup - Duplicate user should not be tracked"""
        # Use a fixed ID that was already tracked
        response = api_client.post(
            f"{BASE_URL}/api/referrals/track-signup",
            params={
                "code": KNOWN_REFERRAL_CODE,
                "referee_id": "test-referee-123",  # Already tracked
                "referee_email": "referee@test.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == False
        assert "reason" in data
        
        print("✅ POST /api/referrals/track-signup - Duplicate user correctly rejected")
    
    def test_track_signup_invalid_code(self, api_client):
        """POST /api/referrals/track-signup - Invalid code should not track"""
        response = api_client.post(
            f"{BASE_URL}/api/referrals/track-signup",
            params={
                "code": "INVALIDCODE",
                "referee_id": "new-user-123",
                "referee_email": "new@test.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == False
        assert "reason" in data
        
        print("✅ POST /api/referrals/track-signup - Invalid code correctly rejected")
    
    def test_track_conversion(self, api_client):
        """POST /api/referrals/track-conversion - Track subscription conversion"""
        # First create a new signup
        unique_id = str(uuid.uuid4())
        signup_response = api_client.post(
            f"{BASE_URL}/api/referrals/track-signup",
            params={
                "code": KNOWN_REFERRAL_CODE,
                "referee_id": f"convert-test-{unique_id}",
                "referee_email": f"convert-{unique_id}@test.com"
            }
        )
        
        # Now track conversion
        response = api_client.post(
            f"{BASE_URL}/api/referrals/track-conversion",
            params={
                "referee_id": f"convert-test-{unique_id}",
                "plan": "pro_monthly",
                "amount": 29.00
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == True
        assert "commission_amount" in data
        assert "commission_rate" in data
        assert "referrer_bonus_days" in data
        
        # Verify commission calculation (20% of $29 = $5.80)
        assert data["commission_rate"] == 0.2  # Bronze tier
        assert abs(data["commission_amount"] - 5.80) < 0.01
        assert data["referrer_bonus_days"] == 7
        
        print(f"✅ POST /api/referrals/track-conversion - Commission: ${data['commission_amount']:.2f}")
    
    def test_track_conversion_no_referral(self, api_client):
        """POST /api/referrals/track-conversion - Non-referred user should not track"""
        response = api_client.post(
            f"{BASE_URL}/api/referrals/track-conversion",
            params={
                "referee_id": "non-existent-user",
                "plan": "pro_monthly",
                "amount": 29.00
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tracked"] == False
        assert "reason" in data
        
        print("✅ POST /api/referrals/track-conversion - Non-referred user correctly rejected")


class TestTierProgression:
    """Tests for tier commission rates"""
    
    def test_tier_commission_rates(self, api_client):
        """Verify tier commission rates are correct"""
        response = api_client.get(f"{BASE_URL}/api/referrals/config")
        
        assert response.status_code == 200
        data = response.json()
        
        tiers = {t["name"]: t for t in data["tiers"]}
        
        # Verify commission rates
        assert tiers["Bronze"]["commission_rate"] == "20%"
        assert tiers["Bronze"]["min_referrals"] == 0
        
        assert tiers["Silver"]["commission_rate"] == "25%"
        assert tiers["Silver"]["min_referrals"] == 6
        
        assert tiers["Gold"]["commission_rate"] == "30%"
        assert tiers["Gold"]["min_referrals"] == 16
        
        assert tiers["Platinum"]["commission_rate"] == "35%"
        assert tiers["Platinum"]["min_referrals"] == 50
        
        print("✅ Tier commission rates verified: Bronze 20% -> Silver 25% -> Gold 30% -> Platinum 35%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
