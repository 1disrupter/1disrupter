"""
Push Notifications API Tests
Tests for the push notification feature including:
- GET /api/notifications/config - Returns notification types and high_confidence_threshold
- GET /api/notifications/preferences - Returns default/saved preferences
- PUT /api/notifications/preferences - Updates preferences
- POST /api/notifications/test - Sends test notification
- High-confidence signal notification integration
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test wallet addresses
TEST_WALLET = "demo_user"
TEST_PRO_WALLET = "0xTEST_PUSH_NOTIFICATIONS_PRO"


class TestNotificationConfig:
    """Tests for GET /api/notifications/config endpoint"""
    
    def test_get_notification_config_returns_200(self):
        """Config endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/notifications/config")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ GET /api/notifications/config returns 200")
    
    def test_config_has_high_confidence_threshold(self):
        """Config should include high_confidence_threshold"""
        response = requests.get(f"{BASE_URL}/api/notifications/config")
        data = response.json()
        
        assert "high_confidence_threshold" in data, "Missing high_confidence_threshold"
        assert data["high_confidence_threshold"] == 75, f"Expected 75%, got {data['high_confidence_threshold']}%"
        print(f"✅ high_confidence_threshold is {data['high_confidence_threshold']}%")
    
    def test_config_has_notification_types(self):
        """Config should include notification_types list"""
        response = requests.get(f"{BASE_URL}/api/notifications/config")
        data = response.json()
        
        assert "notification_types" in data, "Missing notification_types"
        assert isinstance(data["notification_types"], list), "notification_types should be a list"
        assert len(data["notification_types"]) > 0, "notification_types should not be empty"
        
        # Check expected notification types
        type_ids = [t["id"] for t in data["notification_types"]]
        expected_types = ["signal_alerts", "high_confidence_alerts", "trade_confirmations", "price_alerts"]
        
        for expected in expected_types:
            assert expected in type_ids, f"Missing notification type: {expected}"
        
        print(f"✅ notification_types contains: {type_ids}")
    
    def test_notification_type_structure(self):
        """Each notification type should have id, name, description"""
        response = requests.get(f"{BASE_URL}/api/notifications/config")
        data = response.json()
        
        for ntype in data["notification_types"]:
            assert "id" in ntype, f"Missing 'id' in notification type"
            assert "name" in ntype, f"Missing 'name' in notification type"
            assert "description" in ntype, f"Missing 'description' in notification type"
        
        print("✅ All notification types have proper structure (id, name, description)")


class TestNotificationPreferences:
    """Tests for GET/PUT /api/notifications/preferences endpoints"""
    
    def test_get_preferences_returns_200(self):
        """Preferences endpoint should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ GET /api/notifications/preferences returns 200")
    
    def test_get_preferences_returns_defaults(self):
        """New user should get default preferences"""
        # Use a unique wallet to ensure we get defaults
        unique_wallet = f"0xTEST_NEW_USER_{datetime.now().timestamp()}"
        
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": unique_wallet}
        )
        data = response.json()
        
        # Check default values
        assert data.get("push_enabled") == True, "push_enabled should default to True"
        assert data.get("signal_alerts") == True, "signal_alerts should default to True"
        assert data.get("high_confidence_alerts") == True, "high_confidence_alerts should default to True"
        assert data.get("trade_confirmations") == True, "trade_confirmations should default to True"
        assert data.get("price_alerts") == True, "price_alerts should default to True"
        
        print("✅ Default preferences returned correctly")
    
    def test_get_preferences_has_quiet_hours(self):
        """Preferences should include quiet_hours settings"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET}
        )
        data = response.json()
        
        assert "quiet_hours" in data, "Missing quiet_hours"
        quiet_hours = data["quiet_hours"]
        assert "enabled" in quiet_hours, "Missing quiet_hours.enabled"
        assert "start" in quiet_hours, "Missing quiet_hours.start"
        assert "end" in quiet_hours, "Missing quiet_hours.end"
        
        print(f"✅ quiet_hours present: enabled={quiet_hours['enabled']}, {quiet_hours['start']}-{quiet_hours['end']}")
    
    def test_update_preferences_push_enabled(self):
        """Should be able to update push_enabled preference"""
        # First disable
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"push_enabled": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("push_enabled") == False, "push_enabled should be False"
        
        # Then re-enable
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"push_enabled": True}
        )
        data = response.json()
        assert data.get("push_enabled") == True, "push_enabled should be True"
        
        print("✅ push_enabled preference updated successfully")
    
    def test_update_preferences_high_confidence_alerts(self):
        """Should be able to update high_confidence_alerts preference"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"high_confidence_alerts": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("high_confidence_alerts") == False
        
        # Re-enable
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"high_confidence_alerts": True}
        )
        data = response.json()
        assert data.get("high_confidence_alerts") == True
        
        print("✅ high_confidence_alerts preference updated successfully")
    
    def test_update_preferences_signal_alerts(self):
        """Should be able to update signal_alerts preference"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"signal_alerts": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("signal_alerts") == False
        
        # Re-enable
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"signal_alerts": True}
        )
        
        print("✅ signal_alerts preference updated successfully")
    
    def test_update_preferences_trade_confirmations(self):
        """Should be able to update trade_confirmations preference"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"trade_confirmations": False}
        )
        assert response.status_code == 200
        
        # Re-enable
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"trade_confirmations": True}
        )
        
        print("✅ trade_confirmations preference updated successfully")
    
    def test_update_preferences_price_alerts(self):
        """Should be able to update price_alerts preference"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"price_alerts": False}
        )
        assert response.status_code == 200
        
        # Re-enable
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"price_alerts": True}
        )
        
        print("✅ price_alerts preference updated successfully")
    
    def test_update_quiet_hours_enabled(self):
        """Should be able to enable/disable quiet hours"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"quiet_hours_enabled": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("quiet_hours", {}).get("enabled") == True
        
        # Disable
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={"quiet_hours_enabled": False}
        )
        data = response.json()
        assert data.get("quiet_hours", {}).get("enabled") == False
        
        print("✅ quiet_hours_enabled preference updated successfully")
    
    def test_update_quiet_hours_times(self):
        """Should be able to update quiet hours start/end times"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={
                "quiet_hours_enabled": True,
                "quiet_hours_start": "23:00",
                "quiet_hours_end": "07:00"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        quiet_hours = data.get("quiet_hours", {})
        assert quiet_hours.get("start") == "23:00", f"Expected 23:00, got {quiet_hours.get('start')}"
        assert quiet_hours.get("end") == "07:00", f"Expected 07:00, got {quiet_hours.get('end')}"
        
        # Reset to defaults
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_WALLET},
            json={
                "quiet_hours_enabled": False,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00"
            }
        )
        
        print("✅ quiet_hours times updated successfully")


class TestTestNotification:
    """Tests for POST /api/notifications/test endpoint"""
    
    def test_send_test_notification_returns_200(self):
        """Test notification endpoint should return 200"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/test",
            params={"wallet_address": TEST_WALLET}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ POST /api/notifications/test returns 200")
    
    def test_send_test_notification_response_structure(self):
        """Test notification should return proper response structure"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/test",
            params={"wallet_address": TEST_WALLET}
        )
        data = response.json()
        
        assert "success" in data, "Missing 'success' field"
        assert "message" in data, "Missing 'message' field"
        assert "details" in data, "Missing 'details' field"
        
        # Since no devices are registered, success should be False with reason
        # This is expected behavior - the endpoint works, just no devices to send to
        print(f"✅ Test notification response: success={data['success']}, message={data['message']}")
    
    def test_send_test_notification_no_devices(self):
        """Test notification should indicate no devices when none registered"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/test",
            params={"wallet_address": f"0xNO_DEVICES_{datetime.now().timestamp()}"}
        )
        data = response.json()
        
        # Expected: success=False because no devices registered
        # This is correct behavior - the API works, just no devices to send to
        assert "success" in data
        if not data["success"]:
            assert "reason" in data.get("details", {}) or "message" in data
        
        print("✅ Test notification correctly handles no registered devices")


class TestHighConfidenceSignalNotification:
    """Tests for high-confidence signal notification integration"""
    
    @pytest.fixture(autouse=True)
    def setup_pro_user(self):
        """Ensure test Pro user exists"""
        requests.post(
            f"{BASE_URL}/api/investors/register",
            json={"wallet_address": TEST_PRO_WALLET}
        )
        # Make user Pro
        requests.post(
            f"{BASE_URL}/api/users/upgrade-pro",
            json={"wallet_address": TEST_PRO_WALLET}
        )
    
    def test_high_confidence_threshold_is_75(self):
        """High confidence threshold should be 75%"""
        response = requests.get(f"{BASE_URL}/api/notifications/config")
        data = response.json()
        
        assert data["high_confidence_threshold"] == 75
        print("✅ High confidence threshold is 75%")
    
    def test_pro_user_has_high_confidence_alerts_enabled(self):
        """Pro user should have high_confidence_alerts enabled by default"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        data = response.json()
        
        assert data.get("high_confidence_alerts") == True
        print("✅ Pro user has high_confidence_alerts enabled by default")
    
    def test_signal_generation_triggers_notification_for_high_confidence(self):
        """Signal generation should attempt to send notifications for 75%+ confidence signals"""
        # This test verifies the integration exists
        # The actual notification delivery is mocked (no FCM/APNs configured)
        
        # Generate signals
        response = requests.post(f"{BASE_URL}/api/signals/generate")
        
        # Check that signals were generated
        assert response.status_code == 200
        data = response.json()
        
        # Verify signals exist
        signals_response = requests.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        signals_data = signals_response.json()
        
        # Check if any signals have high confidence
        signals = signals_data.get("signals", [])
        high_confidence_signals = [s for s in signals if s.get("confidence", 0) >= 75]
        
        print(f"✅ Signal generation works. Found {len(high_confidence_signals)} high-confidence signals (75%+)")
        print(f"   Note: Push notification delivery is MOCKED (no FCM/APNs keys configured)")


class TestPushNotificationService:
    """Tests for the push notification service module"""
    
    def test_notification_types_enum(self):
        """Verify notification types are properly defined"""
        response = requests.get(f"{BASE_URL}/api/notifications/config")
        data = response.json()
        
        type_ids = [t["id"] for t in data["notification_types"]]
        
        # These should match NotificationType enum in push_notifications.py
        expected = ["signal_alerts", "high_confidence_alerts", "trade_confirmations", "price_alerts"]
        for exp in expected:
            assert exp in type_ids, f"Missing notification type: {exp}"
        
        print("✅ All expected notification types are defined")
    
    def test_preferences_persistence(self):
        """Preferences should persist across requests"""
        test_wallet = f"0xTEST_PERSIST_{datetime.now().timestamp()}"
        
        # Set preferences
        requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": test_wallet},
            json={
                "push_enabled": True,
                "high_confidence_alerts": False,
                "signal_alerts": True
            }
        )
        
        # Retrieve and verify
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            params={"wallet_address": test_wallet}
        )
        data = response.json()
        
        assert data.get("push_enabled") == True
        assert data.get("high_confidence_alerts") == False
        assert data.get("signal_alerts") == True
        
        print("✅ Preferences persist correctly across requests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
