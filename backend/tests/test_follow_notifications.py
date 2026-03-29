"""
Test Follow Strategy + In-App Notifications + Pro Gating
Tests: Follow/Unfollow endpoints, Notifications inbox, Demo endpoints, Free-tier gating
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
# Note: demo_test2@my-alpha-ai.com was upgraded to Pro, using new free user
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"
ADMIN_EMAIL = "admin@my-alpha-ai.com"
ADMIN_PASSWORD = "Admin1234!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def free_user_token(api_client):
    """Get auth token for free tier user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": FREE_USER_EMAIL,
        "password": FREE_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Free user login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get auth token for admin user (elite tier)"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


class TestDemoEndpoints:
    """Demo endpoints (no auth required)"""
    
    def test_demo_following_returns_mock_data(self, api_client):
        """GET /api/strategies/following/demo returns mock following data"""
        response = api_client.get(f"{BASE_URL}/api/strategies/following/demo")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "following" in data
        assert len(data["following"]) == 2  # demo-1 and demo-2
        assert data["count"] == 2
        assert data["is_pro"] is True
        
        # Verify structure of demo following data
        for strat in data["following"]:
            assert "id" in strat
            assert "name" in strat
            assert "type" in strat
            assert "asset" in strat
            assert "metrics" in strat
            assert "followed_at" in strat
    
    def test_demo_notifications_returns_mock_data(self, api_client):
        """GET /api/notifications/inbox/demo returns mock notifications"""
        response = api_client.get(f"{BASE_URL}/api/notifications/inbox/demo")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notifications" in data
        assert len(data["notifications"]) == 4  # 4 demo notifications
        assert "unread_count" in data
        assert data["unread_count"] == 2  # 2 unread in demo
        
        # Verify notification structure
        for notif in data["notifications"]:
            assert "id" in notif
            assert "strategy_id" in notif
            assert "message" in notif
            assert "type" in notif
            assert "read" in notif
            assert "created_at" in notif


class TestFollowEndpointsAuth:
    """Follow/Unfollow endpoints require auth"""
    
    def test_follow_without_auth_returns_401(self, api_client):
        """POST /api/strategies/{id}/follow without auth returns 401"""
        response = api_client.post(f"{BASE_URL}/api/strategies/test-strat/follow")
        assert response.status_code == 401
    
    def test_unfollow_without_auth_returns_401(self, api_client):
        """POST /api/strategies/{id}/unfollow without auth returns 401"""
        response = api_client.post(f"{BASE_URL}/api/strategies/test-strat/unfollow")
        assert response.status_code == 401
    
    def test_following_list_without_auth_returns_401(self, api_client):
        """GET /api/strategies/following without auth returns 401"""
        response = api_client.get(f"{BASE_URL}/api/strategies/following")
        assert response.status_code == 401
    
    def test_following_ids_without_auth_returns_401(self, api_client):
        """GET /api/strategies/following/ids without auth returns 401"""
        response = api_client.get(f"{BASE_URL}/api/strategies/following/ids")
        assert response.status_code == 401


class TestNotificationEndpointsAuth:
    """Notification endpoints require auth"""
    
    def test_inbox_without_auth_returns_401(self, api_client):
        """GET /api/notifications/inbox without auth returns 401"""
        response = api_client.get(f"{BASE_URL}/api/notifications/inbox")
        assert response.status_code == 401
    
    def test_mark_read_without_auth_returns_401(self, api_client):
        """POST /api/notifications/{id}/read without auth returns 401"""
        response = api_client.post(f"{BASE_URL}/api/notifications/test-notif/read")
        assert response.status_code == 401
    
    def test_mark_all_read_without_auth_returns_401(self, api_client):
        """POST /api/notifications/read-all without auth returns 401"""
        response = api_client.post(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 401


class TestProStatus:
    """Pro status endpoint"""
    
    def test_pro_status_without_auth_returns_401(self, api_client):
        """GET /api/user/pro-status without auth returns 401"""
        response = api_client.get(f"{BASE_URL}/api/user/pro-status")
        assert response.status_code == 401
    
    def test_free_user_pro_status(self, api_client, free_user_token):
        """GET /api/user/pro-status for free user returns correct tier info"""
        response = api_client.get(
            f"{BASE_URL}/api/user/pro-status",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_pro"] is False
        assert data["tier"] == "free"
        assert data["follow_limit"] == 1
    
    def test_admin_user_pro_status(self, api_client, admin_token):
        """GET /api/user/pro-status for admin (elite) returns correct tier info"""
        response = api_client.get(
            f"{BASE_URL}/api/user/pro-status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_pro"] is True
        assert data["tier"] == "elite"
        assert data["follow_limit"] is None  # Unlimited for pro/elite


class TestFollowWorkflow:
    """Follow/Unfollow workflow with auth"""
    
    def test_follow_strategy_creates_entry_and_notification(self, api_client, admin_token):
        """POST /api/strategies/{id}/follow creates follow entry and notification"""
        strategy_id = "TEST_follow_strat_1"
        
        # First unfollow to ensure clean state
        api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/unfollow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Follow the strategy
        response = api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/follow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["following"] is True
        assert "followed" in data["message"].lower() or "following" in data["message"].lower()
        
        # Verify it appears in following list
        following_response = api_client.get(
            f"{BASE_URL}/api/strategies/following/ids",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert following_response.status_code == 200
        assert strategy_id in following_response.json()["ids"]
        
        # Cleanup
        api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/unfollow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
    
    def test_follow_already_following_returns_success(self, api_client, admin_token):
        """POST /api/strategies/{id}/follow when already following returns success"""
        strategy_id = "TEST_follow_strat_2"
        
        # Follow first
        api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/follow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Follow again
        response = api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/follow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["following"] is True
        assert "already" in data["message"].lower()
        
        # Cleanup
        api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/unfollow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
    
    def test_unfollow_strategy_removes_entry(self, api_client, admin_token):
        """POST /api/strategies/{id}/unfollow removes follow entry"""
        strategy_id = "TEST_unfollow_strat"
        
        # Follow first
        api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/follow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Unfollow
        response = api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/unfollow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["following"] is False
        
        # Verify it's removed from following list
        following_response = api_client.get(
            f"{BASE_URL}/api/strategies/following/ids",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert following_response.status_code == 200
        assert strategy_id not in following_response.json()["ids"]
    
    def test_unfollow_not_following_returns_success(self, api_client, admin_token):
        """POST /api/strategies/{id}/unfollow when not following returns success"""
        strategy_id = "TEST_never_followed"
        
        response = api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/unfollow",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["following"] is False


class TestFreeTierGating:
    """Free tier follow limit gating"""
    
    def test_free_tier_first_follow_succeeds(self, api_client, free_user_token):
        """Free tier user can follow 1 strategy"""
        strategy_id = "TEST_free_tier_strat_1"
        
        # Clean up any existing follows first
        api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/unfollow",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        
        # Get current following count and unfollow all
        following_response = api_client.get(
            f"{BASE_URL}/api/strategies/following/ids",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        if following_response.status_code == 200:
            for sid in following_response.json().get("ids", []):
                api_client.post(
                    f"{BASE_URL}/api/strategies/{sid}/unfollow",
                    headers={"Authorization": f"Bearer {free_user_token}"}
                )
        
        # Now follow one strategy
        response = api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id}/follow",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["following"] is True
    
    def test_free_tier_second_follow_returns_403(self, api_client, free_user_token):
        """Free tier user gets 403 on second follow attempt"""
        strategy_id_2 = "TEST_free_tier_strat_2"
        
        # Try to follow a second strategy
        response = api_client.post(
            f"{BASE_URL}/api/strategies/{strategy_id_2}/follow",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        assert response.status_code == 403
        data = response.json()
        assert "upgrade" in data["detail"].lower() or "pro" in data["detail"].lower()
        assert "1" in data["detail"] or "limited" in data["detail"].lower()
    
    def test_free_tier_cleanup(self, api_client, free_user_token):
        """Cleanup: unfollow all strategies for free user"""
        following_response = api_client.get(
            f"{BASE_URL}/api/strategies/following/ids",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        if following_response.status_code == 200:
            for sid in following_response.json().get("ids", []):
                api_client.post(
                    f"{BASE_URL}/api/strategies/{sid}/unfollow",
                    headers={"Authorization": f"Bearer {free_user_token}"}
                )


class TestFollowingList:
    """GET /api/strategies/following returns enriched data"""
    
    def test_following_list_returns_strategy_details(self, api_client, admin_token):
        """GET /api/strategies/following returns list with metrics"""
        response = api_client.get(
            f"{BASE_URL}/api/strategies/following",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "following" in data
        assert "count" in data
        assert "is_pro" in data
        assert isinstance(data["following"], list)


class TestNotificationWorkflow:
    """Notification inbox and mark read workflow"""
    
    def test_inbox_returns_notifications(self, api_client, admin_token):
        """GET /api/notifications/inbox returns notifications with unread count"""
        response = api_client.get(
            f"{BASE_URL}/api/notifications/inbox",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notifications" in data
        assert "unread_count" in data
        assert isinstance(data["notifications"], list)
        assert isinstance(data["unread_count"], int)
    
    def test_mark_all_read_clears_unread(self, api_client, admin_token):
        """POST /api/notifications/read-all marks all as read"""
        response = api_client.post(
            f"{BASE_URL}/api/notifications/read-all",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "marked" in data
        
        # Verify unread count is 0
        inbox_response = api_client.get(
            f"{BASE_URL}/api/notifications/inbox",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert inbox_response.status_code == 200
        assert inbox_response.json()["unread_count"] == 0


class TestLeaderboardIntegration:
    """Verify leaderboard demo mode still works"""
    
    def test_leaderboard_demo_returns_8_strategies(self, api_client):
        """GET /api/leaderboard/strategies?demo=true returns 8 strategies"""
        response = api_client.get(f"{BASE_URL}/api/leaderboard/strategies", params={"demo": True})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["strategies"]) == 8
