"""
AlphaAI Performance Metrics API Tests
Tests for:
- Compliance endpoints (paper/live)
- Performance summary endpoints
- Equity curve endpoints (daily/trades)
- Sharpe ratio with benchmark
- Daily PnL breakdown
- Combined metrics
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestComplianceEndpoints:
    """Test compliance labeling endpoints"""
    
    def test_paper_compliance_info(self):
        """GET /api/metrics/compliance/paper - Paper trading compliance info"""
        response = requests.get(f"{BASE_URL}/api/metrics/compliance/paper")
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "paper"
        assert data["is_real_money"] == False
        assert data["label"] == "PAPER TRADING"
        assert data["badge_color"] == "#7B61FF"
        assert "disclaimer_short" in data
        assert "disclaimer_full" in data
        assert "risk_warnings" in data
        assert isinstance(data["risk_warnings"], list)
        assert len(data["risk_warnings"]) > 0
        print(f"✅ Paper compliance: {data['label']}")
    
    def test_live_compliance_info(self):
        """GET /api/metrics/compliance/live - Live trading compliance info"""
        response = requests.get(f"{BASE_URL}/api/metrics/compliance/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "live"
        assert data["is_real_money"] == True
        assert data["label"] == "LIVE TRADING"
        assert data["badge_color"] == "#FF4444"
        assert "Real funds at risk" in data["disclaimer_short"]
        assert "risk_warnings" in data
        assert len(data["risk_warnings"]) >= 4
        print(f"✅ Live compliance: {data['label']}")
    
    def test_invalid_mode_compliance(self):
        """GET /api/metrics/compliance/invalid - Should return 400"""
        response = requests.get(f"{BASE_URL}/api/metrics/compliance/invalid")
        assert response.status_code == 400
        print("✅ Invalid mode returns 400")


class TestPerformanceSummary:
    """Test performance summary endpoints"""
    
    def test_paper_summary(self):
        """GET /api/metrics/summary?mode=paper - Paper trading summary"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", params={
            "wallet_address": "demo",
            "mode": "paper"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "paper"
        assert data["is_simulated"] == True
        assert data["compliance_label"] == "PAPER TRADING"
        assert "period_start" in data
        assert "period_end" in data
        assert "starting_equity" in data
        assert "current_equity" in data
        assert "total_return_pct" in data
        assert "total_pnl" in data
        assert "total_trades" in data
        assert "winning_trades" in data
        assert "losing_trades" in data
        assert "win_rate" in data
        assert "sharpe_ratio" in data
        assert "max_drawdown" in data
        print(f"✅ Paper summary: equity={data['current_equity']}, return={data['total_return_pct']}%")
    
    def test_live_summary(self):
        """GET /api/metrics/summary?mode=live - Live trading summary"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", params={
            "wallet_address": "demo",
            "mode": "live"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "live"
        assert data["is_simulated"] == False
        assert data["compliance_label"] == "LIVE TRADING"
        print(f"✅ Live summary: equity={data['current_equity']}, return={data['total_return_pct']}%")
    
    def test_summary_with_custom_days(self):
        """GET /api/metrics/summary with custom days parameter"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", params={
            "wallet_address": "demo",
            "mode": "paper",
            "days": 7
        })
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "paper"
        print(f"✅ Summary with 7 days period")
    
    def test_summary_missing_wallet(self):
        """GET /api/metrics/summary without wallet_address - Should return 422"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", params={
            "mode": "paper"
        })
        assert response.status_code == 422
        print("✅ Missing wallet returns 422")


class TestEquityCurve:
    """Test equity curve endpoints"""
    
    def test_daily_equity_curve_paper(self):
        """GET /api/metrics/equity-curve/daily?mode=paper - Daily equity curve"""
        response = requests.get(f"{BASE_URL}/api/metrics/equity-curve/daily", params={
            "wallet_address": "demo",
            "mode": "paper"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "paper"
        assert data["compliance_label"] == "PAPER TRADING"
        assert data["is_simulated"] == True
        assert "period_days" in data
        assert "starting_equity" in data
        assert "ending_equity" in data
        assert "total_pnl" in data
        assert "total_return_pct" in data
        assert "equity_curve" in data
        assert isinstance(data["equity_curve"], list)
        
        # Check equity curve structure
        if len(data["equity_curve"]) > 0:
            point = data["equity_curve"][0]
            assert "date" in point
            assert "equity" in point
            assert "daily_pnl" in point
            assert "daily_return_pct" in point
            assert "cumulative_pnl" in point
            assert "cumulative_return_pct" in point
            assert "trade_count" in point
        
        print(f"✅ Daily equity curve: {len(data['equity_curve'])} data points")
    
    def test_daily_equity_curve_live(self):
        """GET /api/metrics/equity-curve/daily?mode=live - Live daily equity"""
        response = requests.get(f"{BASE_URL}/api/metrics/equity-curve/daily", params={
            "wallet_address": "demo",
            "mode": "live"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "live"
        assert data["compliance_label"] == "LIVE TRADING"
        assert data["is_simulated"] == False
        print(f"✅ Live daily equity curve: {len(data['equity_curve'])} data points")
    
    def test_trade_level_equity_paper(self):
        """GET /api/metrics/equity-curve/trades?mode=paper - Trade-level equity"""
        response = requests.get(f"{BASE_URL}/api/metrics/equity-curve/trades", params={
            "wallet_address": "demo",
            "mode": "paper"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "paper"
        assert data["compliance_label"] == "PAPER TRADING"
        assert "total_trades" in data
        assert "starting_equity" in data
        assert "ending_equity" in data
        assert "trade_equity" in data
        assert isinstance(data["trade_equity"], list)
        
        print(f"✅ Trade-level equity: {data['total_trades']} trades")
    
    def test_trade_level_equity_with_limit(self):
        """GET /api/metrics/equity-curve/trades with limit parameter"""
        response = requests.get(f"{BASE_URL}/api/metrics/equity-curve/trades", params={
            "wallet_address": "demo",
            "mode": "paper",
            "limit": 50
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["trade_equity"]) <= 50
        print(f"✅ Trade-level equity with limit=50")


class TestSharpeMetrics:
    """Test Sharpe ratio and risk metrics endpoints"""
    
    def test_sharpe_metrics_paper(self):
        """GET /api/metrics/sharpe?mode=paper - Sharpe metrics"""
        response = requests.get(f"{BASE_URL}/api/metrics/sharpe", params={
            "wallet_address": "demo",
            "mode": "paper",
            "include_benchmark": True
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "paper"
        assert data["compliance_label"] == "PAPER TRADING"
        assert data["is_simulated"] == True
        assert "period_days" in data
        assert "metrics" in data
        
        metrics = data["metrics"]
        assert "sharpe_ratio" in metrics
        assert "sortino_ratio" in metrics
        assert "risk_free_rate" in metrics
        assert "annualized_return" in metrics
        assert "annualized_volatility" in metrics
        assert "max_drawdown" in metrics
        assert "max_drawdown_duration_days" in metrics
        assert "calmar_ratio" in metrics
        
        print(f"✅ Sharpe metrics: sharpe={metrics['sharpe_ratio']}, sortino={metrics['sortino_ratio']}")
    
    def test_sharpe_with_benchmark(self):
        """GET /api/metrics/sharpe with BTC benchmark comparison"""
        response = requests.get(f"{BASE_URL}/api/metrics/sharpe", params={
            "wallet_address": "demo",
            "mode": "paper",
            "include_benchmark": True
        })
        assert response.status_code == 200
        
        data = response.json()
        metrics = data["metrics"]
        assert "benchmark_comparison" in metrics
        
        benchmark = metrics["benchmark_comparison"]
        if benchmark:
            assert benchmark["name"] == "BTC Buy-and-Hold"
            assert "sharpe_ratio" in benchmark
            assert "annualized_return" in benchmark
            assert "annualized_volatility" in benchmark
            assert "alpha" in benchmark
            assert "outperforming" in benchmark
            print(f"✅ Benchmark comparison: alpha={benchmark['alpha']}%, outperforming={benchmark['outperforming']}")
        else:
            print("✅ Benchmark comparison included (no data)")
    
    def test_sharpe_without_benchmark(self):
        """GET /api/metrics/sharpe without benchmark"""
        response = requests.get(f"{BASE_URL}/api/metrics/sharpe", params={
            "wallet_address": "demo",
            "mode": "paper",
            "include_benchmark": False
        })
        assert response.status_code == 200
        
        data = response.json()
        metrics = data["metrics"]
        # Benchmark should be None when not requested
        assert metrics.get("benchmark_comparison") is None
        print("✅ Sharpe without benchmark")
    
    def test_sharpe_custom_risk_free_rate(self):
        """GET /api/metrics/sharpe with custom risk-free rate"""
        response = requests.get(f"{BASE_URL}/api/metrics/sharpe", params={
            "wallet_address": "demo",
            "mode": "paper",
            "risk_free_rate": 0.05
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["metrics"]["risk_free_rate"] == 0.05
        print("✅ Sharpe with custom risk-free rate (5%)")


class TestDailyPnL:
    """Test daily PnL breakdown endpoints"""
    
    def test_daily_pnl_paper(self):
        """GET /api/metrics/daily-pnl?mode=paper - Daily PnL breakdown"""
        response = requests.get(f"{BASE_URL}/api/metrics/daily-pnl", params={
            "wallet_address": "demo",
            "mode": "paper"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "paper"
        assert data["compliance_label"] == "PAPER TRADING"
        assert data["is_simulated"] == True
        assert "period_days" in data
        assert "total_pnl" in data
        assert "profitable_days" in data
        assert "losing_days" in data
        assert "win_day_rate" in data
        assert "avg_daily_pnl" in data
        assert "daily_pnl" in data
        assert isinstance(data["daily_pnl"], list)
        
        print(f"✅ Daily PnL: total={data['total_pnl']}, profitable_days={data['profitable_days']}")
    
    def test_daily_pnl_live(self):
        """GET /api/metrics/daily-pnl?mode=live - Live daily PnL"""
        response = requests.get(f"{BASE_URL}/api/metrics/daily-pnl", params={
            "wallet_address": "demo",
            "mode": "live"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "live"
        assert data["compliance_label"] == "LIVE TRADING"
        print(f"✅ Live daily PnL: total={data['total_pnl']}")


class TestCombinedMetrics:
    """Test combined paper+live metrics endpoint"""
    
    def test_combined_metrics(self):
        """GET /api/metrics/combined - Combined paper and live metrics"""
        response = requests.get(f"{BASE_URL}/api/metrics/combined", params={
            "wallet_address": "demo"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "period_days" in data
        assert "paper" in data
        assert "live" in data
        assert "comparison" in data
        
        # Check paper section
        paper = data["paper"]
        assert "summary" in paper
        assert "compliance" in paper
        assert paper["summary"]["mode"] == "paper"
        assert paper["compliance"]["label"] == "PAPER TRADING"
        
        # Check live section
        live = data["live"]
        assert "summary" in live
        assert "compliance" in live
        assert live["summary"]["mode"] == "live"
        assert live["compliance"]["label"] == "LIVE TRADING"
        
        # Check comparison
        comparison = data["comparison"]
        assert "paper_outperforms_live" in comparison
        assert "return_difference" in comparison
        assert "sharpe_difference" in comparison
        assert "note" in comparison
        
        print(f"✅ Combined metrics: paper_return={paper['summary']['total_return_pct']}%, live_return={live['summary']['total_return_pct']}%")
    
    def test_combined_metrics_custom_days(self):
        """GET /api/metrics/combined with custom days"""
        response = requests.get(f"{BASE_URL}/api/metrics/combined", params={
            "wallet_address": "demo",
            "days": 7
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 7
        print("✅ Combined metrics with 7 days period")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_nonexistent_wallet(self):
        """Test metrics for non-existent wallet - should return empty data"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", params={
            "wallet_address": "nonexistent_wallet_12345",
            "mode": "paper"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_trades"] == 0
        assert data["total_pnl"] == 0.0
        print("✅ Non-existent wallet returns empty data")
    
    def test_invalid_mode_summary(self):
        """Test summary with invalid mode"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", params={
            "wallet_address": "demo",
            "mode": "invalid"
        })
        assert response.status_code == 400
        print("✅ Invalid mode returns 400")
    
    def test_negative_days(self):
        """Test with negative days parameter"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", params={
            "wallet_address": "demo",
            "mode": "paper",
            "days": -1
        })
        # Should either return 422 or handle gracefully
        assert response.status_code in [200, 422]
        print("✅ Negative days handled")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
