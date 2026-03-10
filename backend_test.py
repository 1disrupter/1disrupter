import requests
import sys
import json
from datetime import datetime

class AlphaAIAPITester:
    def __init__(self, base_url="https://ai-trading-vault.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_wallet = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n=== TESTING BASIC ENDPOINTS ===")
        
        # Test root endpoint
        self.run_test("API Root", "GET", "", 200)
        
        # Test fund stats
        success, fund_stats = self.run_test("Fund Stats", "GET", "fund/stats", 200)
        if success and fund_stats:
            print(f"   Fund NAV: ${fund_stats.get('nav', 0):,.2f}")
            print(f"   Total AUM: ${fund_stats.get('total_aum', 0):,.2f}")
            print(f"   Sharpe Ratio: {fund_stats.get('sharpe_ratio', 0)}")

    def test_investor_endpoints(self):
        """Test investor registration and management"""
        print("\n=== TESTING INVESTOR ENDPOINTS ===")
        
        # Generate test wallet address
        self.test_wallet = f"0x{''.join([f'{i:02x}' for i in range(20)])}"
        print(f"Using test wallet: {self.test_wallet}")
        
        # Register investor
        success, investor = self.run_test(
            "Register Investor", 
            "POST", 
            "investors/register", 
            200,
            {"wallet_address": self.test_wallet}
        )
        
        if success:
            # Get investor details
            self.run_test(
                "Get Investor", 
                "GET", 
                f"investors/{self.test_wallet}", 
                200
            )
            
            # Test deposit
            success, deposit_result = self.run_test(
                "Deposit Funds", 
                "POST", 
                "investors/deposit", 
                200,
                {"wallet_address": self.test_wallet, "amount": 1000}
            )
            
            if success:
                print(f"   Deposit successful: {deposit_result.get('message', '')}")
                
                # Test withdrawal
                self.run_test(
                    "Withdraw Funds", 
                    "POST", 
                    "investors/withdraw", 
                    200,
                    {"wallet_address": self.test_wallet, "amount": 100}
                )

    def test_trading_agents(self):
        """Test trading agents endpoints"""
        print("\n=== TESTING TRADING AGENTS ===")
        
        success, agents = self.run_test("Get Trading Agents", "GET", "agents", 200)
        if success and agents:
            print(f"   Found {len(agents)} trading agents")
            for agent in agents[:3]:  # Show first 3 agents
                print(f"   - {agent.get('name', 'Unknown')}: {agent.get('status', 'unknown')} ({agent.get('type', 'unknown')})")

    def test_trades_endpoints(self):
        """Test trades endpoints"""
        print("\n=== TESTING TRADES ===")
        
        success, trades = self.run_test("Get Recent Trades", "GET", "trades?limit=5", 200)
        if success and trades:
            print(f"   Found {len(trades)} recent trades")
            for trade in trades[:2]:  # Show first 2 trades
                print(f"   - {trade.get('symbol', 'Unknown')}: {trade.get('side', 'unknown')} ${trade.get('price', 0):,.2f}")

    def test_marketplace_endpoints(self):
        """Test marketplace endpoints"""
        print("\n=== TESTING MARKETPLACE ===")
        
        success, marketplace_agents = self.run_test("Get Marketplace Agents", "GET", "marketplace/agents", 200)
        if success and marketplace_agents:
            print(f"   Found {len(marketplace_agents)} marketplace agents")
            for agent in marketplace_agents[:2]:  # Show first 2 agents
                print(f"   - {agent.get('name', 'Unknown')}: {agent.get('performance_30d', 0)}% (30d)")

    def test_ai_analysis(self):
        """Test AI analysis endpoint"""
        print("\n=== TESTING AI ANALYSIS ===")
        
        success, analysis = self.run_test(
            "AI Market Analysis", 
            "POST", 
            "ai/analyze", 
            200,
            {"symbol": "bitcoin", "timeframe": "1d"}
        )
        if success and analysis:
            print(f"   Analysis for {analysis.get('symbol', 'Unknown')}")
            print(f"   Price: ${analysis.get('price', 0):,.2f}")
            print(f"   24h Change: {analysis.get('change_24h', 0):.2f}%")
            analysis_text = analysis.get('analysis', '')
            if analysis_text:
                print(f"   Analysis: {analysis_text[:100]}...")

    def test_risk_alerts(self):
        """Test risk alerts endpoints"""
        print("\n=== TESTING RISK ALERTS ===")
        
        success, alerts = self.run_test("Get Risk Alerts", "GET", "risk/alerts", 200)
        if success and alerts:
            print(f"   Found {len(alerts)} risk alerts")
            for alert in alerts[:2]:  # Show first 2 alerts
                print(f"   - {alert.get('type', 'Unknown')}: {alert.get('severity', 'unknown')} - {alert.get('message', '')[:50]}...")

    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        print("\n=== TESTING ANALYTICS ===")
        
        success, overview = self.run_test("Analytics Overview", "GET", "analytics/overview", 200)
        if success and overview:
            print(f"   Sharpe Ratio: {overview.get('sharpe_ratio', 0)}")
            print(f"   Max Drawdown: {overview.get('max_drawdown', 0)}%")
            print(f"   Total Trades: {overview.get('total_trades', 0):,}")
        
        success, strategies = self.run_test("Strategy Analytics", "GET", "analytics/strategies", 200)
        if success and strategies:
            print(f"   Found {len(strategies)} strategies")

    def test_fund_endpoints(self):
        """Test additional fund endpoints"""
        print("\n=== TESTING FUND ENDPOINTS ===")
        
        self.run_test("Fund Allocation", "GET", "fund/allocation", 200)
        self.run_test("Performance History", "GET", "fund/performance-history", 200)

    def test_market_data_endpoints(self):
        """Test market data endpoints"""
        print("\n=== TESTING MARKET DATA ===")
        
        self.run_test("Top Coins", "GET", "market/top-coins", 200)
        self.run_test("Price Chart", "GET", "market/chart/bitcoin?days=7", 200)

    def test_strategy_lab_endpoints(self):
        """Test Strategy Lab endpoints - NEW FEATURE"""
        print("\n=== TESTING STRATEGY LAB (NEW) ===")
        
        # Get strategies
        success, strategies = self.run_test("Get Lab Strategies", "GET", "lab/strategies", 200)
        if success and strategies:
            print(f"   Found {len(strategies)} strategies")
            for strategy in strategies[:2]:
                print(f"   - {strategy.get('name', 'Unknown')}: {strategy.get('status', 'unknown')} (Sharpe: {strategy.get('sharpe_ratio', 0)})")
        
        # Get strategy rankings
        success, rankings = self.run_test("Get Strategy Rankings", "GET", "lab/rankings", 200)
        if success and rankings:
            print(f"   Found {len(rankings)} ranked strategies")
        
        # Generate new strategy
        success, generated = self.run_test(
            "Generate Strategy", 
            "POST", 
            "lab/strategies/generate", 
            200,
            {"strategy_type": "momentum", "risk_level": "medium"}
        )
        if success and generated:
            strategy_id = generated.get('strategy', {}).get('id')
            print(f"   Generated strategy ID: {strategy_id}")
            
            if strategy_id:
                # Test backtest
                success, backtest = self.run_test(
                    "Backtest Strategy", 
                    "POST", 
                    f"lab/strategies/{strategy_id}/backtest", 
                    200,
                    {"strategy_id": strategy_id, "initial_capital": 10000}
                )
                if success:
                    print(f"   Backtest completed")
                
                # Test sandbox
                success, sandbox = self.run_test(
                    "Start Sandbox", 
                    "POST", 
                    f"lab/strategies/{strategy_id}/sandbox", 
                    200
                )
                if success:
                    print(f"   Sandbox started")

    def test_risk_management_endpoints(self):
        """Test Risk Management Engine endpoints - NEW FEATURE"""
        print("\n=== TESTING RISK MANAGEMENT (NEW) ===")
        
        # Get risk config
        success, config = self.run_test("Get Risk Config", "GET", "risk/config", 200)
        if success and config:
            print(f"   Max Drawdown: {config.get('max_drawdown', 0)}%")
            print(f"   Max Daily Loss: {config.get('max_daily_loss', 0)}%")
            print(f"   Auto Shutdown: {config.get('auto_shutdown_enabled', False)}")
        
        # Get portfolio risk status
        success, status = self.run_test("Get Portfolio Risk Status", "GET", "risk/portfolio-status", 200)
        if success and status:
            print(f"   Current Drawdown: {status.get('current_drawdown', 0)}%")
            print(f"   Risk Level: {status.get('risk_level', 'unknown')}")
            print(f"   Daily P&L: {status.get('daily_pnl', 0)}%")

    def test_capital_allocation_endpoints(self):
        """Test Capital Allocation Engine endpoints - NEW FEATURE"""
        print("\n=== TESTING CAPITAL ALLOCATION (NEW) ===")
        
        # Get capital allocations
        success, allocations = self.run_test("Get Capital Allocations", "GET", "capital/allocations", 200)
        if success and allocations:
            print(f"   Found {len(allocations)} capital allocations")
            for alloc in allocations[:2]:
                print(f"   - {alloc.get('strategy_name', 'Unknown')}: {alloc.get('allocation_percent', 0)}%")
        
        # Test rebalance
        success, rebalance = self.run_test("Rebalance Capital", "POST", "capital/rebalance", 200)
        if success and rebalance:
            print(f"   Rebalance result: {rebalance.get('message', 'Unknown')}")

    def test_execution_optimization_endpoints(self):
        """Test Execution Optimization Layer endpoints - NEW FEATURE"""
        print("\n=== TESTING EXECUTION OPTIMIZATION (NEW) ===")
        
        # Get execution stats
        success, stats = self.run_test("Get Execution Stats", "GET", "execution/stats", 200)
        if success and stats:
            print(f"   Orders Today: {stats.get('total_orders_today', 0)}")
            print(f"   Avg Slippage: {stats.get('avg_slippage', 0)}%")
            print(f"   Avg Gas Fee: ${stats.get('avg_gas_fee', 0)}")
            print(f"   Best Price Rate: {stats.get('best_price_achieved', 0)}%")
        
        # Test execution simulation
        success, simulation = self.run_test(
            "Simulate Execution", 
            "POST", 
            "execution/simulate", 
            200,
            None,  # Using query params
            {'Content-Type': 'application/json'}
        )
        # Try with query params in URL
        success, simulation = self.run_test(
            "Simulate Execution", 
            "POST", 
            "execution/simulate?symbol=BTC/USDT&amount=1.0&side=buy", 
            200
        )
        if success and simulation:
            print(f"   Simulation: {simulation.get('symbol', 'Unknown')} - Price: ${simulation.get('execution_price', 0):,.2f}")

    def test_paper_trading_endpoints(self):
        """Test Paper Trading endpoints - NEW FEATURE"""
        print("\n=== TESTING PAPER TRADING (NEW) ===")
        
        if not self.test_wallet:
            print("   Skipping paper trading tests - no test wallet available")
            return
        
        # Toggle paper trading
        success, toggle = self.run_test(
            "Toggle Paper Trading", 
            "POST", 
            f"investors/toggle-paper-trading?wallet_address={self.test_wallet}", 
            200
        )
        if success:
            print(f"   Paper trading toggled: {toggle.get('is_paper_trading', False)}")
        
        # Execute paper trade
        success, trade = self.run_test(
            "Execute Paper Trade", 
            "POST", 
            "paper/trade", 
            200,
            {
                "wallet_address": self.test_wallet,
                "symbol": "BTC/USDT",
                "side": "buy",
                "amount": 0.1
            }
        )
        if success and trade:
            print(f"   Paper trade executed - P&L: ${trade.get('pnl', 0):.2f}")
        
        # Get paper portfolio
        success, portfolio = self.run_test(
            "Get Paper Portfolio", 
            "GET", 
            f"paper/portfolio/{self.test_wallet}", 
            200
        )
        if success and portfolio:
            print(f"   Paper Balance: ${portfolio.get('paper_balance', 0):,.2f}")
            print(f"   Paper P&L: ${portfolio.get('paper_pnl', 0):.2f}")
            print(f"   Total Trades: {portfolio.get('total_trades', 0)}")
        
        # Reset paper portfolio
        success, reset = self.run_test(
            "Reset Paper Portfolio", 
            "POST", 
            f"paper/reset/{self.test_wallet}", 
            200
        )
        if success:
            print(f"   Paper portfolio reset: {reset.get('message', 'Unknown')}")

def main():
    print("🚀 Starting AlphaAI Fund API Tests")
    print("=" * 50)
    
    tester = AlphaAIAPITester()
    
    # Run all test suites
    tester.test_basic_endpoints()
    tester.test_fund_endpoints()
    tester.test_investor_endpoints()
    tester.test_trading_agents()
    tester.test_trades_endpoints()
    tester.test_marketplace_endpoints()
    tester.test_ai_analysis()
    tester.test_risk_alerts()
    tester.test_analytics_endpoints()
    tester.test_market_data_endpoints()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())