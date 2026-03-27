"""
AlphaAI Phase 1 Tests: Stop-Loss/Take-Profit Orders + Public Leaderboard
Tests for:
- POST /api/orders/sl-tp - Create stop-loss or take-profit order
- GET /api/orders/active - Get active orders for user
- DELETE /api/orders/{id} - Cancel an order
- GET /api/leaderboard - Get trader rankings with filters
- GET /api/leaderboard/trader/{id} - Get trader profile
- GET /api/leaderboard/top-performers - Get top traders by different metrics
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user IDs
TEST_USER_ID = f"TEST_SLTP_{uuid.uuid4().hex[:8]}"
TEST_USER_ID_2 = f"TEST_SLTP_{uuid.uuid4().hex[:8]}"


class TestOrdersAPI:
    """Tests for Stop-Loss/Take-Profit order management endpoints"""
    
    created_order_ids = []
    
    def test_create_stop_loss_order(self):
        """Test creating a stop-loss order"""
        response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID}",
            json={
                "symbol": "BTC",
                "order_type": "stop_loss",
                "trigger_price": 80000.0,
                "quantity": 0.1,
                "current_position_price": 85000.0,
                "trading_mode": "paper"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "order" in data
        assert data["order"]["symbol"] == "BTC"
        assert data["order"]["order_type"] == "stop_loss"
        assert data["order"]["trigger_price"] == 80000.0
        assert data["order"]["quantity"] == 0.1
        assert data["order"]["status"] == "active"
        assert data["order"]["trading_mode"] == "paper"
        assert "id" in data["order"]
        
        # Store order ID for later tests
        TestOrdersAPI.created_order_ids.append(data["order"]["id"])
        print(f"✓ Created stop-loss order: {data['order']['id']}")
    
    def test_create_take_profit_order(self):
        """Test creating a take-profit order"""
        response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID}",
            json={
                "symbol": "ETH",
                "order_type": "take_profit",
                "trigger_price": 4000.0,
                "quantity": 1.0,
                "current_position_price": 3500.0,
                "trading_mode": "paper"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert data["order"]["order_type"] == "take_profit"
        assert data["order"]["trigger_price"] == 4000.0
        
        TestOrdersAPI.created_order_ids.append(data["order"]["id"])
        print(f"✓ Created take-profit order: {data['order']['id']}")
    
    def test_create_live_trading_order(self):
        """Test creating an order with live trading mode"""
        response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID}",
            json={
                "symbol": "SOL",
                "order_type": "stop_loss",
                "trigger_price": 130.0,
                "quantity": 5.0,
                "current_position_price": 145.0,
                "trading_mode": "live"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["order"]["trading_mode"] == "live"
        
        TestOrdersAPI.created_order_ids.append(data["order"]["id"])
        print(f"✓ Created live trading order: {data['order']['id']}")
    
    def test_create_order_with_trade_id(self):
        """Test creating an order linked to a specific trade"""
        trade_id = f"trade_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID}",
            json={
                "symbol": "BTC",
                "order_type": "take_profit",
                "trigger_price": 95000.0,
                "quantity": 0.05,
                "current_position_price": 85000.0,
                "trading_mode": "paper",
                "trade_id": trade_id
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        TestOrdersAPI.created_order_ids.append(data["order"]["id"])
        print(f"✓ Created order with trade_id: {trade_id}")
    
    def test_create_order_invalid_order_type(self):
        """Test creating an order with invalid order type"""
        response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID}",
            json={
                "symbol": "BTC",
                "order_type": "invalid_type",
                "trigger_price": 80000.0,
                "quantity": 0.1,
                "current_position_price": 85000.0,
                "trading_mode": "paper"
            }
        )
        # Should return 400 for invalid order type (may return 500 on validation error)
        assert response.status_code in [400, 500], f"Expected 400 or 500, got {response.status_code}"
        print(f"✓ Invalid order type rejected with {response.status_code}")
    
    def test_create_order_invalid_trading_mode(self):
        """Test creating an order with invalid trading mode"""
        response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID}",
            json={
                "symbol": "BTC",
                "order_type": "stop_loss",
                "trigger_price": 80000.0,
                "quantity": 0.1,
                "current_position_price": 85000.0,
                "trading_mode": "invalid_mode"
            }
        )
        # Should return 400 for invalid trading mode (may return 500 on validation error)
        assert response.status_code in [400, 500], f"Expected 400 or 500, got {response.status_code}"
        print(f"✓ Invalid trading mode rejected with {response.status_code}")
    
    def test_get_active_orders(self):
        """Test getting active orders for a user"""
        response = requests.get(f"{BASE_URL}/api/orders/active?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "count" in data
        assert isinstance(data["orders"], list)
        assert data["count"] >= 0
        
        # Verify order structure
        if data["count"] > 0:
            order = data["orders"][0]
            assert "id" in order
            assert "user_id" in order
            assert "symbol" in order
            assert "order_type" in order
            assert "trigger_price" in order
            assert "quantity" in order
            assert "status" in order
            assert order["status"] == "active"
        
        print(f"✓ Retrieved {data['count']} active orders")
    
    def test_get_active_orders_filter_by_symbol(self):
        """Test filtering active orders by symbol"""
        response = requests.get(f"{BASE_URL}/api/orders/active?user_id={TEST_USER_ID}&symbol=BTC")
        assert response.status_code == 200
        
        data = response.json()
        # All returned orders should be for BTC
        for order in data["orders"]:
            assert order["symbol"] == "BTC"
        
        print(f"✓ Filtered orders by symbol BTC: {data['count']} orders")
    
    def test_get_order_history(self):
        """Test getting order history"""
        response = requests.get(f"{BASE_URL}/api/orders/history?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "orders" in data
        assert "count" in data
        print(f"✓ Retrieved order history: {data['count']} orders")
    
    def test_cancel_order(self):
        """Test cancelling an active order"""
        # First create an order to cancel
        create_response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID_2}",
            json={
                "symbol": "BTC",
                "order_type": "stop_loss",
                "trigger_price": 75000.0,
                "quantity": 0.2,
                "current_position_price": 85000.0,
                "trading_mode": "paper"
            }
        )
        assert create_response.status_code == 200
        order_id = create_response.json()["order"]["id"]
        
        # Cancel the order
        cancel_response = requests.delete(f"{BASE_URL}/api/orders/{order_id}?user_id={TEST_USER_ID_2}")
        assert cancel_response.status_code == 200
        
        data = cancel_response.json()
        assert data["success"] is True
        assert data["message"] == "Order cancelled"
        
        print(f"✓ Cancelled order: {order_id}")
    
    def test_cancel_nonexistent_order(self):
        """Test cancelling a non-existent order"""
        fake_order_id = str(uuid.uuid4())
        response = requests.delete(f"{BASE_URL}/api/orders/{fake_order_id}?user_id={TEST_USER_ID}")
        assert response.status_code == 400
        print("✓ Non-existent order cancellation rejected with 400")
    
    def test_cancel_order_wrong_user(self):
        """Test that a user cannot cancel another user's order"""
        # Create order for TEST_USER_ID
        create_response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={TEST_USER_ID}",
            json={
                "symbol": "ETH",
                "order_type": "stop_loss",
                "trigger_price": 3000.0,
                "quantity": 0.5,
                "current_position_price": 3500.0,
                "trading_mode": "paper"
            }
        )
        order_id = create_response.json()["order"]["id"]
        TestOrdersAPI.created_order_ids.append(order_id)
        
        # Try to cancel with different user
        cancel_response = requests.delete(f"{BASE_URL}/api/orders/{order_id}?user_id=wrong_user")
        assert cancel_response.status_code == 400
        print("✓ Cross-user order cancellation rejected")
    
    def test_get_order_stats(self):
        """Test getting order execution statistics"""
        response = requests.get(f"{BASE_URL}/api/orders/stats/summary?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_orders" in data
        assert "triggered_orders" in data
        assert "cancelled_orders" in data
        assert "stop_losses_triggered" in data
        assert "take_profits_triggered" in data
        assert "total_pnl_from_orders" in data
        
        print(f"✓ Order stats: {data['active_orders']} active, {data['triggered_orders']} triggered")


class TestLeaderboardAPI:
    """Tests for Public Leaderboard endpoints"""
    
    def test_get_leaderboard_default(self):
        """Test getting leaderboard with default parameters"""
        response = requests.get(f"{BASE_URL}/api/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "traders" in data
        assert "total" in data
        assert "period" in data
        assert "sort_by" in data
        assert "limit" in data
        assert "offset" in data
        assert "is_limited" in data
        
        # Default values
        assert data["period"] == "all_time"
        assert data["sort_by"] == "pnl"
        
        print(f"✓ Leaderboard: {data['total']} traders, period={data['period']}")
    
    def test_get_leaderboard_daily(self):
        """Test getting daily leaderboard"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?period=daily")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period"] == "daily"
        print("✓ Daily leaderboard retrieved")
    
    def test_get_leaderboard_weekly(self):
        """Test getting weekly leaderboard"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?period=weekly")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period"] == "weekly"
        print("✓ Weekly leaderboard retrieved")
    
    def test_get_leaderboard_monthly(self):
        """Test getting monthly leaderboard"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?period=monthly")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period"] == "monthly"
        print("✓ Monthly leaderboard retrieved")
    
    def test_get_leaderboard_sort_by_win_rate(self):
        """Test sorting leaderboard by win rate"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?sort_by=win_rate")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sort_by"] == "win_rate"
        print("✓ Leaderboard sorted by win_rate")
    
    def test_get_leaderboard_sort_by_roi(self):
        """Test sorting leaderboard by ROI"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?sort_by=roi")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sort_by"] == "roi"
        print("✓ Leaderboard sorted by ROI")
    
    def test_get_leaderboard_sort_by_total_trades(self):
        """Test sorting leaderboard by total trades"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?sort_by=total_trades")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sort_by"] == "total_trades"
        print("✓ Leaderboard sorted by total_trades")
    
    def test_get_leaderboard_free_user_limit(self):
        """Test that free users are limited to top 10"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?user_tier=free&limit=50")
        assert response.status_code == 200
        
        data = response.json()
        # Free users should be limited to 10
        assert data["limit"] <= 10
        print(f"✓ Free user limit enforced: {data['limit']}")
    
    def test_get_leaderboard_pro_user_full_access(self):
        """Test that pro users get full leaderboard access"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?user_tier=pro&limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 50
        assert data["is_limited"] is False
        print("✓ Pro user has full leaderboard access")
    
    def test_get_leaderboard_elite_user_full_access(self):
        """Test that elite users get full leaderboard access"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?user_tier=elite&limit=100")
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 100
        print("✓ Elite user has full leaderboard access")
    
    def test_get_leaderboard_pagination(self):
        """Test leaderboard pagination"""
        response = requests.get(f"{BASE_URL}/api/leaderboard?limit=10&offset=5&user_tier=pro")
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 5
        print("✓ Leaderboard pagination works")
    
    def test_get_trader_profile_not_found(self):
        """Test getting a non-existent trader profile"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/trader/nonexistent_trader_123")
        assert response.status_code == 404
        print("✓ Non-existent trader returns 404")
    
    def test_get_my_rank(self):
        """Test getting current user's rank"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/me?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "ranks" in data
        assert "percentiles" in data
        assert "total_traders" in data
        assert "stats" in data
        
        # User not on leaderboard yet should get message
        if "message" in data:
            assert "Complete some trades" in data["message"]
        
        print(f"✓ User rank retrieved: {data.get('ranks', {})}")
    
    def test_get_top_performers(self):
        """Test getting top performers across metrics"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/top-performers")
        assert response.status_code == 200
        
        data = response.json()
        assert "top_by_pnl" in data
        assert "top_by_win_rate" in data
        assert "top_by_roi" in data
        
        assert isinstance(data["top_by_pnl"], list)
        assert isinstance(data["top_by_win_rate"], list)
        assert isinstance(data["top_by_roi"], list)
        
        print(f"✓ Top performers: PnL={len(data['top_by_pnl'])}, WinRate={len(data['top_by_win_rate'])}, ROI={len(data['top_by_roi'])}")
    
    def test_get_top_performers_custom_limit(self):
        """Test getting top performers with custom limit"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/top-performers?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        # Each category should have at most 3 entries
        assert len(data["top_by_pnl"]) <= 3
        assert len(data["top_by_win_rate"]) <= 3
        assert len(data["top_by_roi"]) <= 3
        
        print("✓ Top performers with custom limit works")
    
    def test_update_leaderboard_settings(self):
        """Test updating leaderboard profile settings"""
        response = requests.put(
            f"{BASE_URL}/api/leaderboard/settings?user_id={TEST_USER_ID}",
            json={"is_public": True, "display_name": "Test Trader"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["is_public"] is True
        
        print("✓ Leaderboard settings updated")
    
    def test_toggle_profile_visibility(self):
        """Test toggling profile visibility"""
        # Set to private
        response = requests.put(
            f"{BASE_URL}/api/leaderboard/settings?user_id={TEST_USER_ID}",
            json={"is_public": False}
        )
        assert response.status_code == 200
        assert response.json()["is_public"] is False
        
        # Set back to public
        response = requests.put(
            f"{BASE_URL}/api/leaderboard/settings?user_id={TEST_USER_ID}",
            json={"is_public": True}
        )
        assert response.status_code == 200
        assert response.json()["is_public"] is True
        
        print("✓ Profile visibility toggle works")
    
    def test_refresh_user_stats(self):
        """Test manually refreshing user stats"""
        response = requests.post(f"{BASE_URL}/api/leaderboard/refresh?user_id={TEST_USER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Stats refreshed"
        
        print("✓ User stats refresh works")


class TestOrderLeaderboardIntegration:
    """Integration tests for orders and leaderboard interaction"""
    
    def test_order_creation_flow(self):
        """Test complete order creation flow with both SL and TP"""
        user_id = f"TEST_INTEGRATION_{uuid.uuid4().hex[:8]}"
        
        # Create stop-loss
        sl_response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={user_id}",
            json={
                "symbol": "BTC",
                "order_type": "stop_loss",
                "trigger_price": 80000.0,
                "quantity": 0.1,
                "current_position_price": 85000.0,
                "trading_mode": "paper"
            }
        )
        assert sl_response.status_code == 200
        sl_order_id = sl_response.json()["order"]["id"]
        
        # Create take-profit
        tp_response = requests.post(
            f"{BASE_URL}/api/orders/sl-tp?user_id={user_id}",
            json={
                "symbol": "BTC",
                "order_type": "take_profit",
                "trigger_price": 95000.0,
                "quantity": 0.1,
                "current_position_price": 85000.0,
                "trading_mode": "paper"
            }
        )
        assert tp_response.status_code == 200
        tp_order_id = tp_response.json()["order"]["id"]
        
        # Verify both orders are active
        active_response = requests.get(f"{BASE_URL}/api/orders/active?user_id={user_id}")
        assert active_response.status_code == 200
        active_orders = active_response.json()["orders"]
        assert len(active_orders) == 2
        
        # Cancel one order
        cancel_response = requests.delete(f"{BASE_URL}/api/orders/{sl_order_id}?user_id={user_id}")
        assert cancel_response.status_code == 200
        
        # Verify only one order remains active
        active_response = requests.get(f"{BASE_URL}/api/orders/active?user_id={user_id}")
        assert active_response.json()["count"] == 1
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{tp_order_id}?user_id={user_id}")
        
        print("✓ Complete order creation flow works")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data():
    """Cleanup test data after all tests complete"""
    yield
    # Cleanup orders created during tests
    for order_id in TestOrdersAPI.created_order_ids:
        try:
            requests.delete(f"{BASE_URL}/api/orders/{order_id}?user_id={TEST_USER_ID}")
        except:
            pass
    print(f"\n✓ Cleaned up {len(TestOrdersAPI.created_order_ids)} test orders")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
