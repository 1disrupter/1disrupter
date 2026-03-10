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