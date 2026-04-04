"""
Trading API Tests for AlphaAI Fund Platform
Tests live trading capability via Uniswap V3 integration
- Trading mode (simulation/live)
- Paper trade execution
- Positions management
- Portfolio summary with PnL
- Trade history
- Supported tokens
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://crypto-signals-web2.preview.emergentagent.com').rstrip('/')

# Test wallet with Pro status
TEST_WALLET = "0xTestProUser123"
TEST_WALLET_NEW = f"0xTestTrading{int(time.time())}"


class TestTradingMode:
    """Tests for trading mode endpoints"""
    
    def test_get_trading_mode(self):
        """GET /api/trading/mode - Get user's trading mode"""
        response = requests.get(f"{BASE_URL}/api/trading/mode?wallet_address={TEST_WALLET}")
        assert response.status_code == 200
        
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["simulation", "live"]
        assert "is_live_enabled" in data
        assert "paper_balance" in data
        print(f"✓ Trading mode: {data['mode']}, Paper balance: ${data['paper_balance']}")
    
    def test_set_trading_mode_simulation(self):
        """POST /api/trading/mode - Set mode to simulation"""
        response = requests.post(
            f"{BASE_URL}/api/trading/mode?wallet_address={TEST_WALLET}&mode=simulation"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["mode"] == "simulation"
        assert data["is_live_enabled"] == False
        print(f"✓ Set trading mode to simulation")
    
    def test_set_trading_mode_live(self):
        """POST /api/trading/mode - Set mode to live"""
        response = requests.post(
            f"{BASE_URL}/api/trading/mode?wallet_address={TEST_WALLET}&mode=live"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["mode"] == "live"
        assert data["is_live_enabled"] == True
        print(f"✓ Set trading mode to live")
        
        # Reset back to simulation
        requests.post(f"{BASE_URL}/api/trading/mode?wallet_address={TEST_WALLET}&mode=simulation")
    
    def test_set_invalid_trading_mode(self):
        """POST /api/trading/mode - Invalid mode should fail"""
        response = requests.post(
            f"{BASE_URL}/api/trading/mode?wallet_address={TEST_WALLET}&mode=invalid"
        )
        assert response.status_code == 400
        print(f"✓ Invalid mode rejected correctly")


class TestTradeExecution:
    """Tests for trade execution endpoints"""
    
    def test_execute_paper_trade_buy(self):
        """POST /api/trading/execute - Execute paper BUY trade"""
        response = requests.post(
            f"{BASE_URL}/api/trading/execute",
            json={
                "wallet_address": TEST_WALLET,
                "symbol": "BTC",
                "side": "BUY",
                "amount_usd": 25.0,
                "is_live": False
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "trade_id" in data
        assert "tx_hash" in data
        assert "executed_price" in data
        assert "executed_amount" in data
        assert data["is_live"] == False
        assert data["status"] == "confirmed"
        print(f"✓ Paper BUY trade executed: {data['trade_id'][:8]}... at ${data['executed_price']:.2f}")
    
    def test_execute_paper_trade_sell(self):
        """POST /api/trading/execute - Execute paper SELL trade"""
        response = requests.post(
            f"{BASE_URL}/api/trading/execute",
            json={
                "wallet_address": TEST_WALLET,
                "symbol": "ETH",
                "side": "SELL",
                "amount_usd": 25.0,
                "is_live": False
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["is_live"] == False
        print(f"✓ Paper SELL trade executed: {data['trade_id'][:8]}...")
    
    def test_execute_trade_with_slippage(self):
        """POST /api/trading/execute - Trade with custom slippage"""
        response = requests.post(
            f"{BASE_URL}/api/trading/execute",
            json={
                "wallet_address": TEST_WALLET,
                "symbol": "SOL",
                "side": "BUY",
                "amount_usd": 10.0,
                "is_live": False,
                "slippage_tolerance": 1.0
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print(f"✓ Trade with 1% slippage executed")
    
    def test_execute_trade_unregistered_wallet(self):
        """POST /api/trading/execute - Unregistered wallet should fail"""
        response = requests.post(
            f"{BASE_URL}/api/trading/execute",
            json={
                "wallet_address": "0xUnregisteredWallet999",
                "symbol": "BTC",
                "side": "BUY",
                "amount_usd": 100.0
            }
        )
        assert response.status_code == 404
        print(f"✓ Unregistered wallet rejected correctly")


class TestPositions:
    """Tests for positions endpoints"""
    
    def test_get_positions(self):
        """GET /api/trading/positions - Get open positions"""
        response = requests.get(
            f"{BASE_URL}/api/trading/positions?wallet_address={TEST_WALLET}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "positions" in data
        assert "count" in data
        assert isinstance(data["positions"], list)
        
        if data["count"] > 0:
            pos = data["positions"][0]
            assert "symbol" in pos
            assert "side" in pos
            assert "entry_price" in pos
            assert "current_price" in pos
            assert "unrealized_pnl" in pos
            print(f"✓ Found {data['count']} positions")
        else:
            print(f"✓ No open positions (count: 0)")
    
    def test_get_positions_paper_only(self):
        """GET /api/trading/positions - Filter paper positions"""
        response = requests.get(
            f"{BASE_URL}/api/trading/positions?wallet_address={TEST_WALLET}&is_live=false"
        )
        assert response.status_code == 200
        
        data = response.json()
        for pos in data["positions"]:
            assert pos["is_live"] == False
        print(f"✓ Paper positions filter working")


class TestPortfolio:
    """Tests for portfolio endpoints"""
    
    def test_get_portfolio_summary(self):
        """GET /api/trading/portfolio - Get portfolio with PnL"""
        response = requests.get(
            f"{BASE_URL}/api/trading/portfolio?wallet_address={TEST_WALLET}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "wallet_address" in data
        assert "positions_count" in data
        assert "total_invested" in data
        assert "total_unrealized_pnl" in data
        assert "total_realized_pnl" in data
        assert "total_fees_paid" in data
        assert "net_pnl" in data
        assert "total_trades" in data
        assert "win_rate" in data
        
        print(f"✓ Portfolio: {data['positions_count']} positions, Net PnL: ${data['net_pnl']:.2f}, Win rate: {data['win_rate']}%")
    
    def test_get_portfolio_live_vs_paper(self):
        """GET /api/trading/portfolio - Compare live vs paper"""
        # Paper portfolio
        paper_res = requests.get(
            f"{BASE_URL}/api/trading/portfolio?wallet_address={TEST_WALLET}&is_live=false"
        )
        assert paper_res.status_code == 200
        paper_data = paper_res.json()
        assert paper_data["is_live"] == False
        
        # Live portfolio
        live_res = requests.get(
            f"{BASE_URL}/api/trading/portfolio?wallet_address={TEST_WALLET}&is_live=true"
        )
        assert live_res.status_code == 200
        live_data = live_res.json()
        assert live_data["is_live"] == True
        
        print(f"✓ Paper vs Live portfolio separation working")


class TestTradeHistory:
    """Tests for trade history endpoints"""
    
    def test_get_trade_history(self):
        """GET /api/trading/history - Get trade history"""
        response = requests.get(
            f"{BASE_URL}/api/trading/history?wallet_address={TEST_WALLET}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "trades" in data
        assert "count" in data
        
        if data["count"] > 0:
            trade = data["trades"][0]
            assert "id" in trade
            assert "symbol" in trade
            assert "side" in trade
            assert "amount_usd" in trade
            assert "executed_price" in trade
            assert "status" in trade
            assert "created_at" in trade
            print(f"✓ Found {data['count']} trades in history")
        else:
            print(f"✓ No trade history (count: 0)")
    
    def test_get_trade_history_with_limit(self):
        """GET /api/trading/history - With limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/trading/history?wallet_address={TEST_WALLET}&limit=5"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["trades"]) <= 5
        print(f"✓ Trade history limit working")


class TestSupportedTokens:
    """Tests for supported tokens endpoint"""
    
    def test_get_supported_tokens(self):
        """GET /api/trading/supported-tokens - Get supported tokens"""
        response = requests.get(f"{BASE_URL}/api/trading/supported-tokens")
        assert response.status_code == 200
        
        data = response.json()
        assert "tokens" in data
        assert "network" in data
        assert "dex" in data
        
        # Verify expected tokens
        symbols = [t["symbol"] for t in data["tokens"]]
        assert "BTC" in symbols
        assert "ETH" in symbols
        assert "SOL" in symbols
        assert "USDC" in symbols
        
        # Verify network
        assert data["network"] in ["sepolia", "mainnet"]
        assert data["dex"] == "Uniswap V3"
        
        print(f"✓ Supported tokens: {', '.join(symbols)}, Network: {data['network']}")


class TestEndToEndTradingFlow:
    """End-to-end trading flow tests"""
    
    def test_complete_trading_flow(self):
        """Test complete trading flow: mode -> execute -> positions -> portfolio"""
        # 1. Register new wallet
        reg_res = requests.post(
            f"{BASE_URL}/api/investors/register",
            json={"wallet_address": TEST_WALLET_NEW}
        )
        assert reg_res.status_code == 200
        print(f"✓ Step 1: Registered wallet {TEST_WALLET_NEW[:12]}...")
        
        # 2. Check initial trading mode
        mode_res = requests.get(
            f"{BASE_URL}/api/trading/mode?wallet_address={TEST_WALLET_NEW}"
        )
        assert mode_res.status_code == 200
        assert mode_res.json()["mode"] == "simulation"
        print(f"✓ Step 2: Initial mode is simulation")
        
        # 3. Execute a paper trade
        trade_res = requests.post(
            f"{BASE_URL}/api/trading/execute",
            json={
                "wallet_address": TEST_WALLET_NEW,
                "symbol": "BTC",
                "side": "BUY",
                "amount_usd": 100.0
            }
        )
        assert trade_res.status_code == 200
        trade_data = trade_res.json()
        assert trade_data["success"] == True
        trade_id = trade_data["trade_id"]
        print(f"✓ Step 3: Executed BUY trade {trade_id[:8]}...")
        
        # 4. Check positions
        pos_res = requests.get(
            f"{BASE_URL}/api/trading/positions?wallet_address={TEST_WALLET_NEW}"
        )
        assert pos_res.status_code == 200
        pos_data = pos_res.json()
        assert pos_data["count"] >= 1
        print(f"✓ Step 4: Position created, count: {pos_data['count']}")
        
        # 5. Check portfolio
        port_res = requests.get(
            f"{BASE_URL}/api/trading/portfolio?wallet_address={TEST_WALLET_NEW}"
        )
        assert port_res.status_code == 200
        port_data = port_res.json()
        assert port_data["total_trades"] >= 1
        print(f"✓ Step 5: Portfolio shows {port_data['total_trades']} trades")
        
        # 6. Check trade history
        hist_res = requests.get(
            f"{BASE_URL}/api/trading/history?wallet_address={TEST_WALLET_NEW}"
        )
        assert hist_res.status_code == 200
        hist_data = hist_res.json()
        assert hist_data["count"] >= 1
        print(f"✓ Step 6: Trade history shows {hist_data['count']} trades")
        
        print(f"\n✓ Complete trading flow test PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
