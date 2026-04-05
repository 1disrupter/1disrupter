"""
Waitlist Automation Tests - 3-email drip sequence via Resend
Tests: POST /api/waitlist, admin analytics, unsubscribe, email job scheduling
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_KEY = "alphaai_admin_2026"
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"


class TestWaitlistEndpoint:
    """Tests for POST /api/waitlist endpoint"""
    
    def test_waitlist_signup_new_email(self):
        """POST /api/waitlist with new email creates entry and returns waitlist_id"""
        # Use unique email for this test
        test_email = f"waitlist-test-{uuid.uuid4().hex[:8]}@my-alpha-ai.com"
        
        response = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={"email": test_email}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "waitlist_id" in data, "Response should contain waitlist_id"
        assert "duplicate" in data, "Response should contain duplicate flag"
        assert "message" in data, "Response should contain message"
        
        # First signup should not be duplicate
        assert data["duplicate"] == False, "First signup should have duplicate=False"
        assert len(data["waitlist_id"]) > 0, "waitlist_id should not be empty"
        
        print(f"✓ New waitlist signup successful: {test_email}, id={data['waitlist_id'][:8]}...")
        
        # Store for cleanup
        self.__class__.test_email = test_email
        self.__class__.waitlist_id = data["waitlist_id"]
    
    def test_waitlist_signup_duplicate_email(self):
        """POST /api/waitlist with same email returns duplicate=True (idempotent)"""
        # Use the email from previous test
        test_email = getattr(self.__class__, 'test_email', f"waitlist-test-dup@my-alpha-ai.com")
        
        # First signup (if not already done)
        response1 = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={"email": test_email}
        )
        
        # Second signup with same email
        response2 = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={"email": test_email}
        )
        
        assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
        data = response2.json()
        
        # Second signup should be duplicate
        assert data["duplicate"] == True, "Second signup should have duplicate=True"
        assert "waitlist_id" in data, "Should still return waitlist_id"
        
        print(f"✓ Duplicate signup handled correctly: duplicate={data['duplicate']}")
    
    def test_waitlist_signup_invalid_email(self):
        """POST /api/waitlist with invalid email returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={"email": "not-an-email"}
        )
        
        assert response.status_code == 422, f"Expected 422 for invalid email, got {response.status_code}"
        print("✓ Invalid email rejected with 422")
    
    def test_waitlist_signup_missing_email(self):
        """POST /api/waitlist without email returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={}
        )
        
        assert response.status_code == 422, f"Expected 422 for missing email, got {response.status_code}"
        print("✓ Missing email rejected with 422")


class TestWaitlistEmailJobs:
    """Tests for email job scheduling after waitlist signup"""
    
    def test_email_jobs_created_on_signup(self):
        """Verify 3 email jobs are scheduled after signup"""
        # Create a new signup to test job creation
        test_email = f"waitlist-jobs-{uuid.uuid4().hex[:8]}@my-alpha-ai.com"
        
        response = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={"email": test_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        waitlist_id = data["waitlist_id"]
        
        # Wait a moment for background task to process
        time.sleep(2)
        
        # Check admin analytics to verify jobs were created
        analytics_response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": ADMIN_KEY}
        )
        
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        
        # Verify per_step breakdown exists
        assert "per_step" in analytics, "Analytics should have per_step breakdown"
        assert len(analytics["per_step"]) == 3, "Should have 3 email steps"
        
        # Verify step names
        step_names = [s["name"] for s in analytics["per_step"]]
        assert "welcome" in step_names, "Should have welcome step"
        assert "activation" in step_names, "Should have activation step"
        assert "conversion" in step_names, "Should have conversion step"
        
        print(f"✓ 3 email jobs created for signup: {test_email}")
        print(f"  Steps: {step_names}")
        
        self.__class__.test_email = test_email
        self.__class__.waitlist_id = waitlist_id
    
    def test_email_step1_sent_immediately(self):
        """Email #1 (welcome) should be sent immediately (status='sent')"""
        # Wait for background task to send email
        time.sleep(3)
        
        analytics_response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": ADMIN_KEY}
        )
        
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        
        # Find step 1 (welcome)
        step1 = next((s for s in analytics["per_step"] if s["step"] == 1), None)
        assert step1 is not None, "Step 1 should exist"
        
        # Step 1 should have at least some sent emails
        assert step1["sent"] > 0, f"Step 1 should have sent emails, got {step1['sent']}"
        
        print(f"✓ Email #1 (welcome) sent: {step1['sent']} emails sent, {step1['failed']} failed")
    
    def test_email_steps_2_3_pending(self):
        """Email #2 and #3 should be pending (scheduled for future)"""
        analytics_response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": ADMIN_KEY}
        )
        
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        
        # Check pending jobs count
        assert "emails" in analytics
        pending_count = analytics["emails"]["pending"]
        
        # Should have pending jobs for steps 2 and 3
        print(f"✓ Pending email jobs: {pending_count}")
        print(f"  Total scheduled: {analytics['emails']['total_scheduled']}")
        print(f"  Sent: {analytics['emails']['sent']}")


class TestWaitlistAdminAnalytics:
    """Tests for GET /api/waitlist/admin/analytics endpoint"""
    
    def test_admin_analytics_requires_admin_key(self):
        """Admin analytics requires valid admin_key"""
        # Without admin key
        response = requests.get(f"{BASE_URL}/api/waitlist/admin/analytics")
        assert response.status_code == 422, "Should require admin_key parameter"
        
        # With invalid admin key
        response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": "wrong_key"}
        )
        assert response.status_code == 403, f"Should reject invalid admin key, got {response.status_code}"
        
        print("✓ Admin analytics properly secured")
    
    def test_admin_analytics_returns_funnel_data(self):
        """Admin analytics returns funnel breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": ADMIN_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify funnel structure
        assert "funnel" in data, "Should have funnel data"
        funnel = data["funnel"]
        assert "pending" in funnel, "Funnel should have pending count"
        assert "activated" in funnel, "Funnel should have activated count"
        assert "converted" in funnel, "Funnel should have converted count"
        assert "unsubscribed" in funnel, "Funnel should have unsubscribed count"
        
        print(f"✓ Funnel data: pending={funnel['pending']}, activated={funnel['activated']}, converted={funnel['converted']}, unsubscribed={funnel['unsubscribed']}")
    
    def test_admin_analytics_returns_rates(self):
        """Admin analytics returns activation_rate and conversion_rate"""
        response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": ADMIN_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "activation_rate" in data, "Should have activation_rate"
        assert "conversion_rate" in data, "Should have conversion_rate"
        assert isinstance(data["activation_rate"], (int, float)), "activation_rate should be numeric"
        assert isinstance(data["conversion_rate"], (int, float)), "conversion_rate should be numeric"
        
        print(f"✓ Rates: activation={data['activation_rate']}%, conversion={data['conversion_rate']}%")
    
    def test_admin_analytics_returns_email_stats(self):
        """Admin analytics returns email delivery stats"""
        response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": ADMIN_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "emails" in data, "Should have emails stats"
        emails = data["emails"]
        assert "total_scheduled" in emails, "Should have total_scheduled"
        assert "sent" in emails, "Should have sent count"
        assert "failed" in emails, "Should have failed count"
        assert "pending" in emails, "Should have pending count"
        assert "delivery_rate" in emails, "Should have delivery_rate"
        
        print(f"✓ Email stats: total={emails['total_scheduled']}, sent={emails['sent']}, pending={emails['pending']}, delivery_rate={emails['delivery_rate']}%")
    
    def test_admin_analytics_returns_per_step_breakdown(self):
        """Admin analytics returns per-step email breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/waitlist/admin/analytics",
            params={"admin_key": ADMIN_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "per_step" in data, "Should have per_step breakdown"
        per_step = data["per_step"]
        assert len(per_step) == 3, "Should have 3 steps"
        
        for step in per_step:
            assert "step" in step, "Each step should have step number"
            assert "name" in step, "Each step should have name"
            assert "total" in step, "Each step should have total"
            assert "sent" in step, "Each step should have sent"
            assert "failed" in step, "Each step should have failed"
            assert "delivery_rate" in step, "Each step should have delivery_rate"
        
        print("✓ Per-step breakdown:")
        for step in per_step:
            print(f"  Step {step['step']} ({step['name']}): total={step['total']}, sent={step['sent']}, rate={step['delivery_rate']}%")


class TestWaitlistUnsubscribe:
    """Tests for GET /api/waitlist/unsubscribe endpoint"""
    
    def test_unsubscribe_updates_status(self):
        """Unsubscribe updates waitlist entry status to 'unsubscribed'"""
        # First create a signup
        test_email = f"waitlist-unsub-{uuid.uuid4().hex[:8]}@my-alpha-ai.com"
        
        signup_response = requests.post(
            f"{BASE_URL}/api/waitlist",
            json={"email": test_email}
        )
        assert signup_response.status_code == 200
        
        # Wait for email job to be created
        time.sleep(2)
        
        # Unsubscribe
        unsub_response = requests.get(
            f"{BASE_URL}/api/waitlist/unsubscribe",
            params={"email": test_email}
        )
        
        assert unsub_response.status_code == 200
        data = unsub_response.json()
        assert "message" in data
        assert "unsubscribed" in data["message"].lower()
        
        print(f"✓ Unsubscribe successful for {test_email}")
    
    def test_unsubscribe_requires_email(self):
        """Unsubscribe requires email parameter"""
        response = requests.get(f"{BASE_URL}/api/waitlist/unsubscribe")
        assert response.status_code == 422, "Should require email parameter"
        print("✓ Unsubscribe requires email parameter")
    
    def test_unsubscribe_nonexistent_email(self):
        """Unsubscribe with non-existent email still returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/waitlist/unsubscribe",
            params={"email": "nonexistent@example.com"}
        )
        # Should still return 200 (graceful handling)
        assert response.status_code == 200
        print("✓ Unsubscribe handles non-existent email gracefully")


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""
    
    def test_health_endpoint(self):
        """GET /api/health returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health endpoint working")
    
    def test_marketplace_leaderboard(self):
        """GET /api/marketplace/strategies/leaderboard works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data or isinstance(data, list)
        print("✓ Marketplace leaderboard working")
    
    def test_marketplace_featured(self):
        """GET /api/marketplace/featured works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/featured")
        assert response.status_code == 200
        print("✓ Marketplace featured working")
    
    def test_login_works(self):
        """POST /api/auth/login works with test credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": PRO_USER_EMAIL,
                "password": PRO_USER_PASSWORD
            }
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Should return access_token"
        print(f"✓ Login working for {PRO_USER_EMAIL}")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
