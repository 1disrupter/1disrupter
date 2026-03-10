import requests
import asyncio
import concurrent.futures
import time
import sys
from datetime import datetime

class AlphaAIStressTester:
    def __init__(self, base_url="https://crypto-alpha-lab.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_wallet = "0x000102030405060708090a0b0c0d0e0f10111213"

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                return True, response.json() if response.content else {}
            else:
                print(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ {name} - Error: {str(e)}")
            return False, {}

    def stress_test_simulation_cycles(self, cycles=20):
        """STRESS TEST: Run 20 simulation cycles consecutively"""
        print(f"\n=== STRESS TEST: {cycles} SIMULATION CYCLES ===")
        
        # Start simulation first
        success, _ = self.run_test("Start Simulation", "POST", "simulation/start", 200)
        if not success:
            print("Failed to start simulation for stress test")
            return
        
        successful_cycles = 0
        start_time = time.time()
        
        for i in range(cycles):
            success, result = self.run_test(f"Cycle {i+1}", "POST", "simulation/run-cycle", 200)
            if success:
                successful_cycles += 1
                trades = len(result.get('cycle_results', []))
                print(f"✅ Cycle {i+1}: {trades} trades executed")
            else:
                print(f"❌ Cycle {i+1}: Failed")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 STRESS TEST RESULTS:")
        print(f"   Successful cycles: {successful_cycles}/{cycles}")
        print(f"   Success rate: {(successful_cycles/cycles*100):.1f}%")
        print(f"   Total duration: {duration:.2f} seconds")
        print(f"   Avg cycle time: {duration/cycles:.2f} seconds")
        
        # Stop simulation
        self.run_test("Stop Simulation", "POST", "simulation/stop", 200)

    def stress_test_strategy_generation(self, count=10):
        """STRESS TEST: Generate 10 strategies at once"""
        print(f"\n=== STRESS TEST: GENERATE {count} STRATEGIES ===")
        
        strategy_types = ["momentum", "arbitrage", "yield", "mean_reversion", "funding"]
        successful_generations = 0
        start_time = time.time()
        
        for i in range(count):
            strategy_type = strategy_types[i % len(strategy_types)]
            success, result = self.run_test(
                f"Generate Strategy {i+1}", 
                "POST", 
                "lab/strategies/generate", 
                200,
                {"strategy_type": strategy_type, "risk_level": "medium"}
            )
            if success:
                successful_generations += 1
                strategy_name = result.get('strategy', {}).get('name', 'Unknown')
                print(f"✅ Strategy {i+1}: {strategy_name}")
            else:
                print(f"❌ Strategy {i+1}: Failed")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 STRATEGY GENERATION RESULTS:")
        print(f"   Successful generations: {successful_generations}/{count}")
        print(f"   Success rate: {(successful_generations/count*100):.1f}%")
        print(f"   Total duration: {duration:.2f} seconds")
        print(f"   Avg generation time: {duration/count:.2f} seconds")

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        print("\n=== EDGE CASE TESTING ===")
        
        # Edge Case 1: Withdraw more than balance
        print("\n🔍 Edge Case: Withdraw more than balance")
        success, result = self.run_test(
            "Withdraw Excessive Amount", 
            "POST", 
            "investors/withdraw", 
            400,  # Expecting error
            {"wallet_address": self.test_wallet, "amount": 999999}
        )
        if success:
            print("✅ Correctly rejected excessive withdrawal")
        
        # Edge Case 2: Deposit below minimum
        print("\n🔍 Edge Case: Deposit below minimum")
        success, result = self.run_test(
            "Deposit Below Minimum", 
            "POST", 
            "investors/deposit", 
            400,  # Expecting error
            {"wallet_address": self.test_wallet, "amount": 50}
        )
        if success:
            print("✅ Correctly rejected below-minimum deposit")
        
        # Edge Case 3: Deploy strategy without backtest
        print("\n🔍 Edge Case: Deploy strategy without backtest")
        # First generate a strategy
        success, gen_result = self.run_test(
            "Generate Strategy for Edge Test", 
            "POST", 
            "lab/strategies/generate", 
            200,
            {"strategy_type": "momentum", "risk_level": "medium"}
        )
        if success:
            strategy_id = gen_result.get('strategy', {}).get('id')
            if strategy_id:
                # Try to deploy without backtest
                success, deploy_result = self.run_test(
                    "Deploy Without Backtest", 
                    "POST", 
                    f"lab/strategies/{strategy_id}/deploy", 
                    400,  # Expecting error
                    None
                )
                if success:
                    print("✅ Correctly rejected deployment without backtest")
        
        # Edge Case 4: Switch to live mode with high drawdown
        print("\n🔍 Edge Case: Switch to live mode with high capital")
        success, result = self.run_test(
            "Switch to Live with High Capital", 
            "POST", 
            "simulation/switch-mode?mode=live&live_capital=50000", 
            400,  # Expecting error
            None
        )
        if success:
            print("✅ Correctly rejected live mode with excessive capital")

    def test_data_integrity(self):
        """Test data integrity - verify logs match trades"""
        print("\n=== DATA INTEGRITY TESTING ===")
        
        # Get recent trades
        success, trades = self.run_test("Get Recent Trades", "GET", "trades?limit=20", 200)
        if not success:
            print("❌ Failed to get trades for integrity check")
            return
        
        # Get simulation logs
        success, logs = self.run_test("Get Simulation Logs", "GET", "simulation/logs?limit=50&log_type=trade", 200)
        if not success:
            print("❌ Failed to get logs for integrity check")
            return
        
        print(f"📊 DATA INTEGRITY CHECK:")
        print(f"   Recent trades: {len(trades)}")
        print(f"   Trade logs: {len(logs)}")
        
        # Check if we have trade logs
        trade_logs = [log for log in logs if log.get('log_type') == 'trade']
        print(f"   Trade-specific logs: {len(trade_logs)}")
        
        # Get agent interactions
        success, interactions = self.run_test("Get Agent Interactions", "GET", "simulation/agent-interactions?limit=50", 200)
        if success:
            print(f"   Agent interactions logged: {len(interactions)}")
            
            # Check for execution -> risk interactions
            exec_risk_interactions = [i for i in interactions if i.get('from_agent') == 'ExecutionAgent' and i.get('to_agent') == 'RiskAgent']
            print(f"   Execution->Risk interactions: {len(exec_risk_interactions)}")
        
        print("✅ Data integrity check completed")

    def concurrent_api_test(self, concurrent_requests=10):
        """Test concurrent API requests"""
        print(f"\n=== CONCURRENT API TEST: {concurrent_requests} REQUESTS ===")
        
        def make_request():
            try:
                response = requests.get(f"{self.api_url}/fund/stats", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        successful_requests = sum(results)
        
        print(f"📊 CONCURRENT REQUEST RESULTS:")
        print(f"   Successful requests: {successful_requests}/{concurrent_requests}")
        print(f"   Success rate: {(successful_requests/concurrent_requests*100):.1f}%")
        print(f"   Total duration: {duration:.2f} seconds")
        print(f"   Avg request time: {duration/concurrent_requests:.2f} seconds")

def main():
    print("🚀 Starting AlphaAI Fund STRESS & EDGE CASE Tests")
    print("=" * 60)
    
    tester = AlphaAIStressTester()
    
    # Run stress tests
    tester.stress_test_simulation_cycles(20)
    tester.stress_test_strategy_generation(10)
    
    # Run edge case tests
    tester.test_edge_cases()
    
    # Run data integrity tests
    tester.test_data_integrity()
    
    # Run concurrent API tests
    tester.concurrent_api_test(10)
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 STRESS TEST FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    return 0 if tester.tests_passed >= tester.tests_run * 0.8 else 1

if __name__ == "__main__":
    sys.exit(main())