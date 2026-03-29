"""
AlphaAI Backtest & CoinGecko Integration Tests
Tests the new POST /api/simulation/backtest endpoint with real CoinGecko data
and the updated POST /api/lab/strategies/{id}/backtest endpoint.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSimulationBacktest:
    """Tests for POST /api/simulation/backtest endpoint"""
    
    def test_backtest_btc_momentum_real_data(self):
        """Test backtest with BTC/USDT, momentum strategy, real CoinGecko data"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "BTC/USDT",
            "strategy": "momentum",
            "days": 365,
            "initial_capital": 100000,
            "demo": False
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        
        results = data.get("results", {})
        # Verify data_source is coingecko (real data)
        assert results.get("data_source") == "coingecko", f"Expected data_source=coingecko, got {results.get('data_source')}"
        
        # Verify all required fields are present
        assert "equity_curve" in results, "Missing equity_curve"
        assert "total_return" in results, "Missing total_return"
        assert "sharpe_ratio" in results, "Missing sharpe_ratio"
        assert "max_drawdown" in results, "Missing max_drawdown"
        assert "win_rate" in results, "Missing win_rate"
        assert "total_trades" in results, "Missing total_trades"
        assert "profit_factor" in results, "Missing profit_factor"
        
        # Verify equity_curve is an array with data
        assert isinstance(results["equity_curve"], list), "equity_curve should be a list"
        assert len(results["equity_curve"]) > 0, "equity_curve should not be empty"
        
        print(f"BTC Momentum Backtest: Return={results['total_return']}%, Sharpe={results['sharpe_ratio']}, Trades={results['total_trades']}")
    
    def test_backtest_demo_mode_returns_mock(self):
        """Test backtest with demo=true returns data_source=mock"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "BTC/USDT",
            "strategy": "momentum",
            "days": 365,
            "initial_capital": 100000,
            "demo": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        
        results = data.get("results", {})
        assert results.get("data_source") == "mock", f"Expected data_source=mock in demo mode, got {results.get('data_source')}"
        
        print(f"Demo Mode Backtest: data_source={results['data_source']}")
    
    def test_backtest_eth_usdt(self):
        """Test backtest with ETH/USDT asset"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "ETH/USDT",
            "strategy": "momentum",
            "days": 365,
            "initial_capital": 100000,
            "demo": False
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        
        results = data.get("results", {})
        assert results.get("asset") == "ETH/USDT", f"Expected asset=ETH/USDT, got {results.get('asset')}"
        assert "equity_curve" in results
        
        print(f"ETH/USDT Backtest: Return={results['total_return']}%, Sharpe={results['sharpe_ratio']}")
    
    def test_backtest_sol_usdt(self):
        """Test backtest with SOL/USDT asset"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "SOL/USDT",
            "strategy": "momentum",
            "days": 365,
            "initial_capital": 100000,
            "demo": False
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        
        results = data.get("results", {})
        assert results.get("asset") == "SOL/USDT"
        
        print(f"SOL/USDT Backtest: Return={results['total_return']}%, Sharpe={results['sharpe_ratio']}")
    
    def test_backtest_mean_reversion_strategy(self):
        """Test backtest with mean_reversion strategy"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "BTC/USDT",
            "strategy": "mean_reversion",
            "days": 365,
            "initial_capital": 100000,
            "demo": False
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        
        results = data.get("results", {})
        assert results.get("strategy") == "mean_reversion"
        assert "equity_curve" in results
        
        print(f"Mean Reversion Backtest: Return={results['total_return']}%, Sharpe={results['sharpe_ratio']}")
    
    def test_backtest_breakout_strategy(self):
        """Test backtest with breakout strategy"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "BTC/USDT",
            "strategy": "breakout",
            "days": 365,
            "initial_capital": 100000,
            "demo": False
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        
        results = data.get("results", {})
        assert results.get("strategy") == "breakout"
        assert "equity_curve" in results
        
        print(f"Breakout Backtest: Return={results['total_return']}%, Sharpe={results['sharpe_ratio']}")
    
    def test_backtest_response_structure(self):
        """Verify complete response structure with all required fields"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "BTC/USDT",
            "strategy": "momentum",
            "days": 365,
            "initial_capital": 100000,
            "demo": False
        })
        assert response.status_code == 200
        
        data = response.json()
        results = data.get("results", {})
        
        # Check all required fields
        required_fields = [
            "period", "initial_capital", "final_capital", "total_return",
            "sharpe_ratio", "max_drawdown", "win_rate", "total_trades",
            "winning_trades", "losing_trades", "profit_factor", "avg_win",
            "avg_loss", "equity_curve", "data_source", "asset", "strategy"
        ]
        
        for field in required_fields:
            assert field in results, f"Missing required field: {field}"
        
        # Verify data types
        assert isinstance(results["total_return"], (int, float))
        assert isinstance(results["sharpe_ratio"], (int, float))
        assert isinstance(results["max_drawdown"], (int, float))
        assert isinstance(results["win_rate"], (int, float))
        assert isinstance(results["total_trades"], int)
        assert isinstance(results["equity_curve"], list)
        
        print(f"Response structure validated with {len(required_fields)} fields")


class TestStrategyLabBacktest:
    """Tests for POST /api/lab/strategies/{id}/backtest endpoint"""
    
    def test_generate_and_backtest_strategy(self):
        """Generate a strategy and run backtest on it"""
        # First generate a strategy
        gen_response = requests.post(f"{BASE_URL}/api/lab/strategies/generate", json={
            "strategy_type": "momentum",
            "risk_level": "medium"
        })
        assert gen_response.status_code == 200, f"Generate failed: {gen_response.text}"
        
        gen_data = gen_response.json()
        assert gen_data.get("success") is True
        
        strategy = gen_data.get("strategy", {})
        strategy_id = strategy.get("id")
        assert strategy_id, "Strategy ID not returned"
        
        # Now backtest the strategy
        bt_response = requests.post(f"{BASE_URL}/api/lab/strategies/{strategy_id}/backtest", json={
            "initial_capital": 100000
        })
        assert bt_response.status_code == 200, f"Backtest failed: {bt_response.text}"
        
        bt_data = bt_response.json()
        assert bt_data.get("success") is True
        
        results = bt_data.get("results", {})
        assert "equity_curve" in results, "Missing equity_curve in strategy backtest"
        assert "total_return" in results
        assert "sharpe_ratio" in results
        
        # Strategy Lab backtest uses real CoinGecko data
        assert results.get("data_source") == "coingecko", f"Expected coingecko, got {results.get('data_source')}"
        
        print(f"Strategy Lab Backtest: Return={results['total_return']}%, Sharpe={results['sharpe_ratio']}")


class TestMarketDataService:
    """Tests for market data service functionality"""
    
    def test_backtest_with_short_period(self):
        """Test backtest with minimum 30 days"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "BTC/USDT",
            "strategy": "momentum",
            "days": 30,
            "initial_capital": 100000,
            "demo": False
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        results = data.get("results", {})
        assert len(results.get("equity_curve", [])) > 0
        
        print(f"30-day Backtest: {len(results['equity_curve'])} equity points")
    
    def test_backtest_with_custom_capital(self):
        """Test backtest with custom initial capital"""
        response = requests.post(f"{BASE_URL}/api/simulation/backtest", json={
            "asset": "BTC/USDT",
            "strategy": "momentum",
            "days": 365,
            "initial_capital": 50000,
            "demo": False
        })
        assert response.status_code == 200
        
        data = response.json()
        results = data.get("results", {})
        
        assert results.get("initial_capital") == 50000, f"Expected initial_capital=50000, got {results.get('initial_capital')}"
        
        print(f"Custom Capital Backtest: Initial=${results['initial_capital']}, Final=${results['final_capital']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
