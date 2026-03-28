"""
AlphaAI Fund Platform - Comprehensive API Tests
Tests all backend endpoints including:
- Simulation Engine (start/stop/run-cycle/stats/switch-mode)
- Strategy Lab (strategies/generate/backtest/sandbox/deploy/auto-deploy)
- Risk Management (config/alerts/portfolio-status)
- Capital Allocation (allocations/rebalance)
- Execution Optimization (stats/simulate - NEW)
- Market Data (top-coins - NEW)
- Investor Management (register/deposit/withdraw/toggle-paper-trading - NEW)
- Fund Management (stats/allocation/performance-history)
- Trading Agents (agents/trades)
- Reports (daily/weekly)
"""

import pytest
import requests
import os
import random
import string

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://alpha-refactor-1.preview.emergentagent.com').rstrip('/')

# Test wallet for investor operations
TEST_WALLET = f"0xTEST{''.join(random.choices(string.hexdigits.lower(), k=36))}"


class TestHealthAndRoot:
    """Basic health check tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ API Root: {data['message']}")


class TestSimulationEngine:
    """Simulation Engine endpoint tests"""
    
    def test_get_simulation_config(self):
        """Test getting simulation configuration"""
        response = requests.get(f"{BASE_URL}/api/simulation/config")
        assert response.status_code == 200
        data = response.json()
        assert "is_running" in data
        assert "mode" in data
        print(f"✅ Simulation Config: mode={data['mode']}, running={data['is_running']}")
    
    def test_start_simulation(self):
        """Test starting simulation"""
        response = requests.post(f"{BASE_URL}/api/simulation/start")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        print(f"✅ Start Simulation: {data.get('message', 'OK')}")
    
    def test_get_simulation_stats(self):
        """Test getting simulation statistics"""
        response = requests.get(f"{BASE_URL}/api/simulation/stats")
        assert response.status_code == 200
        data = response.json()
        assert "simulation" in data
        assert "trading" in data
        assert "strategies" in data
        assert "risk" in data
        print(f"✅ Simulation Stats: capital=${data['simulation']['current_capital']}, trades={data['trading']['total_trades']}")
    
    def test_run_simulation_cycle(self):
        """Test running a simulation cycle"""
        response = requests.post(f"{BASE_URL}/api/simulation/run-cycle")
        assert response.status_code == 200
        data = response.json()
        # May return success=False if simulation not running, which is valid
        print(f"✅ Run Cycle: success={data.get('success')}, message={data.get('message', 'OK')}")
    
    def test_stop_simulation(self):
        """Test stopping simulation"""
        response = requests.post(f"{BASE_URL}/api/simulation/stop")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        print(f"✅ Stop Simulation: {data.get('message', 'OK')}")
    
    def test_switch_mode_paper(self):
        """Test switching to paper trading mode"""
        response = requests.post(f"{BASE_URL}/api/simulation/switch-mode?mode=paper")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["mode"] == "paper"
        print(f"✅ Switch Mode to Paper: {data['message']}")
    
    def test_switch_mode_testnet(self):
        """Test switching to testnet mode"""
        response = requests.post(f"{BASE_URL}/api/simulation/switch-mode?mode=testnet")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["mode"] == "testnet"
        print(f"✅ Switch Mode to Testnet: {data['message']}")
    
    def test_switch_mode_invalid(self):
        """Test switching to invalid mode returns error"""
        response = requests.post(f"{BASE_URL}/api/simulation/switch-mode?mode=invalid")
        assert response.status_code == 400
        print("✅ Invalid mode correctly rejected")
    
    def test_get_simulation_logs(self):
        """Test getting simulation logs"""
        response = requests.get(f"{BASE_URL}/api/simulation/logs?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Simulation Logs: {len(data)} entries")
    
    def test_get_agent_interactions(self):
        """Test getting agent interactions"""
        response = requests.get(f"{BASE_URL}/api/simulation/agent-interactions?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Agent Interactions: {len(data)} entries")


class TestStrategyLab:
    """Strategy Lab endpoint tests"""
    
    def test_get_strategies(self):
        """Test getting all strategies"""
        response = requests.get(f"{BASE_URL}/api/lab/strategies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Strategies: {len(data)} strategies found")
        return data
    
    def test_generate_strategy(self):
        """Test generating a new strategy"""
        payload = {"strategy_type": "momentum", "risk_level": "medium"}
        response = requests.post(f"{BASE_URL}/api/lab/strategies/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "strategy" in data
        print(f"✅ Generated Strategy: {data['strategy']['name']}")
        return data["strategy"]["id"]
    
    def test_get_strategy_rankings(self):
        """Test getting strategy rankings"""
        response = requests.get(f"{BASE_URL}/api/lab/rankings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "rank" in data[0]
            assert "sharpe_ratio" in data[0]
        print(f"✅ Strategy Rankings: {len(data)} ranked strategies")
    
    def test_auto_deploy_top_strategies(self):
        """Test auto-deploying top strategies"""
        response = requests.post(f"{BASE_URL}/api/lab/auto-deploy-top")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        print(f"✅ Auto Deploy: {data.get('deployed_count', 0)} strategies deployed")


class TestRiskManagement:
    """Risk Management endpoint tests"""
    
    def test_get_risk_config(self):
        """Test getting risk configuration"""
        response = requests.get(f"{BASE_URL}/api/risk/config")
        assert response.status_code == 200
        data = response.json()
        assert "max_drawdown" in data
        assert "max_daily_loss" in data
        print(f"✅ Risk Config: max_drawdown={data['max_drawdown']}%, max_daily_loss={data['max_daily_loss']}%")
    
    def test_update_risk_config(self):
        """Test updating risk configuration"""
        payload = {
            "max_drawdown": 5.0,
            "max_position_size": 10.0,
            "max_daily_loss": 2.0,
            "stop_loss": 2.0,
            "auto_shutdown_enabled": True
        }
        response = requests.put(f"{BASE_URL}/api/risk/config", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✅ Risk Config Updated")
    
    def test_get_risk_alerts(self):
        """Test getting risk alerts"""
        response = requests.get(f"{BASE_URL}/api/risk/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Risk Alerts: {len(data)} active alerts")
    
    def test_get_portfolio_risk_status(self):
        """Test getting portfolio risk status"""
        response = requests.get(f"{BASE_URL}/api/risk/portfolio-status")
        assert response.status_code == 200
        data = response.json()
        assert "current_drawdown" in data
        assert "risk_level" in data
        print(f"✅ Portfolio Risk: drawdown={data['current_drawdown']}%, level={data['risk_level']}")


class TestCapitalAllocation:
    """Capital Allocation endpoint tests"""
    
    def test_get_capital_allocations(self):
        """Test getting capital allocations"""
        response = requests.get(f"{BASE_URL}/api/capital/allocations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Capital Allocations: {len(data)} allocations")
    
    def test_rebalance_capital(self):
        """Test rebalancing capital"""
        response = requests.post(f"{BASE_URL}/api/capital/rebalance")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        print(f"✅ Capital Rebalance: {data.get('message', 'OK')}")


class TestExecutionOptimization:
    """Execution Optimization endpoint tests"""
    
    def test_get_execution_stats(self):
        """Test getting execution statistics"""
        response = requests.get(f"{BASE_URL}/api/execution/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_orders_today" in data
        assert "avg_slippage" in data
        print(f"✅ Execution Stats: orders={data['total_orders_today']}, slippage={data['avg_slippage']}%")
    
    def test_simulate_trade_execution(self):
        """Test simulating trade execution - NEW ENDPOINT"""
        payload = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "amount": 0.1
        }
        response = requests.post(f"{BASE_URL}/api/execution/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "simulation" in data
        sim = data["simulation"]
        assert "estimated_execution_price" in sim
        assert "estimated_slippage" in sim
        assert "estimated_gas_fee" in sim
        print(f"✅ Execution Simulate: price=${sim['estimated_execution_price']}, slippage={sim['estimated_slippage']}%")
    
    def test_simulate_trade_execution_sell(self):
        """Test simulating sell trade execution"""
        payload = {
            "symbol": "ETH/USDT",
            "side": "sell",
            "amount": 1.0
        }
        response = requests.post(f"{BASE_URL}/api/execution/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Execution Simulate (Sell): route={data['simulation']['best_route']}")


class TestMarketData:
    """Market Data endpoint tests"""
    
    def test_get_top_coins(self):
        """Test getting top coins - NEW ENDPOINT"""
        response = requests.get(f"{BASE_URL}/api/market/top-coins")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check structure of first coin
        coin = data[0]
        assert "id" in coin
        assert "symbol" in coin
        assert "current_price" in coin
        print(f"✅ Top Coins: {len(data)} coins, first={coin['name']} @ ${coin['current_price']}")


class TestInvestorManagement:
    """Investor Management endpoint tests"""
    
    def test_register_investor(self):
        """Test registering a new investor"""
        payload = {"wallet_address": TEST_WALLET}
        response = requests.post(f"{BASE_URL}/api/investors/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["wallet_address"] == TEST_WALLET
        print(f"✅ Investor Registered: {TEST_WALLET[:10]}...")
    
    def test_get_investor(self):
        """Test getting investor details"""
        response = requests.get(f"{BASE_URL}/api/investors/{TEST_WALLET}")
        assert response.status_code == 200
        data = response.json()
        assert data["wallet_address"] == TEST_WALLET
        print(f"✅ Get Investor: balance=${data['balance']}, shares={data['shares']}")
    
    def test_deposit_funds(self):
        """Test depositing funds"""
        payload = {"wallet_address": TEST_WALLET, "amount": 500.0}
        response = requests.post(f"{BASE_URL}/api/investors/deposit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "shares_received" in data
        print(f"✅ Deposit: ${payload['amount']}, shares={data['shares_received']}")
    
    def test_deposit_below_minimum(self):
        """Test deposit below minimum returns error"""
        payload = {"wallet_address": TEST_WALLET, "amount": 50.0}
        response = requests.post(f"{BASE_URL}/api/investors/deposit", json=payload)
        assert response.status_code == 400
        print("✅ Below minimum deposit correctly rejected")
    
    def test_withdraw_funds(self):
        """Test withdrawing funds"""
        payload = {"wallet_address": TEST_WALLET, "amount": 100.0}
        response = requests.post(f"{BASE_URL}/api/investors/withdraw", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Withdraw: ${payload['amount']}, shares_redeemed={data['shares_redeemed']}")
    
    def test_toggle_paper_trading(self):
        """Test toggling paper trading mode - NEW ENDPOINT"""
        response = requests.post(f"{BASE_URL}/api/investors/toggle-paper-trading/{TEST_WALLET}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "is_paper_trading" in data
        print(f"✅ Toggle Paper Trading: is_paper_trading={data['is_paper_trading']}")
    
    def test_toggle_paper_trading_again(self):
        """Test toggling paper trading mode back"""
        response = requests.post(f"{BASE_URL}/api/investors/toggle-paper-trading/{TEST_WALLET}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Toggle Paper Trading Again: is_paper_trading={data['is_paper_trading']}")
    
    def test_toggle_paper_trading_invalid_wallet(self):
        """Test toggling paper trading for non-existent wallet"""
        response = requests.post(f"{BASE_URL}/api/investors/toggle-paper-trading/0xINVALID123")
        assert response.status_code == 404
        print("✅ Invalid wallet correctly rejected for toggle")


class TestFundManagement:
    """Fund Management endpoint tests"""
    
    def test_get_fund_stats(self):
        """Test getting fund statistics"""
        response = requests.get(f"{BASE_URL}/api/fund/stats")
        assert response.status_code == 200
        data = response.json()
        assert "nav" in data
        assert "total_aum" in data
        assert "sharpe_ratio" in data
        print(f"✅ Fund Stats: NAV=${data['nav']}, AUM=${data['total_aum']}, Sharpe={data['sharpe_ratio']}")
    
    def test_get_fund_allocation(self):
        """Test getting fund allocation"""
        response = requests.get(f"{BASE_URL}/api/fund/allocation")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        total = sum(item["value"] for item in data)
        assert total == 100  # Should sum to 100%
        print(f"✅ Fund Allocation: {len(data)} assets, total={total}%")
    
    def test_get_performance_history(self):
        """Test getting performance history"""
        response = requests.get(f"{BASE_URL}/api/fund/performance-history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✅ Performance History: {len(data)} data points")


class TestTradingAgents:
    """Trading Agents endpoint tests"""
    
    def test_get_agents(self):
        """Test getting trading agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✅ Trading Agents: {len(data)} agents")
    
    def test_get_trades(self):
        """Test getting recent trades"""
        response = requests.get(f"{BASE_URL}/api/trades?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Recent Trades: {len(data)} trades")


class TestReports:
    """Reports endpoint tests"""
    
    def test_get_daily_report(self):
        """Test getting daily report"""
        response = requests.get(f"{BASE_URL}/api/reports/daily")
        assert response.status_code == 200
        data = response.json()
        assert "report_type" in data
        assert data["report_type"] == "daily"
        assert "summary" in data
        assert "trading" in data
        print(f"✅ Daily Report: PnL=${data['summary']['daily_pnl']}, trades={data['trading']['total_trades']}")
    
    def test_get_weekly_report(self):
        """Test getting weekly report"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly")
        assert response.status_code == 200
        data = response.json()
        assert "report_type" in data
        assert data["report_type"] == "weekly"
        assert "summary" in data
        print(f"✅ Weekly Report: PnL=${data['summary']['weekly_pnl']}, Sharpe={data['summary']['sharpe_ratio']}")
    
    def test_get_report_history(self):
        """Test getting report history"""
        response = requests.get(f"{BASE_URL}/api/reports/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Report History: {len(data)} reports")


class TestMarketplace:
    """Marketplace endpoint tests"""
    
    def test_get_marketplace_agents(self):
        """Test getting marketplace agents"""
        response = requests.get(f"{BASE_URL}/api/marketplace/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Marketplace Agents: {len(data)} agents")


class TestAnalytics:
    """Analytics endpoint tests"""
    
    def test_get_analytics_overview(self):
        """Test getting analytics overview"""
        response = requests.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "sharpe_ratio" in data
        assert "win_rate" in data
        print(f"✅ Analytics: Sharpe={data['sharpe_ratio']}, Win Rate={data['win_rate']}%")


class TestPaperTrading:
    """Paper Trading endpoint tests"""
    
    def test_get_paper_portfolio(self):
        """Test getting paper portfolio"""
        response = requests.get(f"{BASE_URL}/api/paper/portfolio/{TEST_WALLET}")
        assert response.status_code == 200
        data = response.json()
        assert "paper_balance" in data
        print(f"✅ Paper Portfolio: balance=${data['paper_balance']}")
    
    def test_execute_paper_trade(self):
        """Test executing paper trade"""
        payload = {
            "wallet_address": TEST_WALLET,
            "symbol": "BTC/USDT",
            "side": "buy",
            "amount": 0.01
        }
        response = requests.post(f"{BASE_URL}/api/paper/trade", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Paper Trade: PnL=${data['pnl']}, new_balance=${data['new_paper_balance']}")
    
    def test_reset_paper_portfolio(self):
        """Test resetting paper portfolio"""
        response = requests.post(f"{BASE_URL}/api/paper/reset/{TEST_WALLET}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✅ Paper Portfolio Reset")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
