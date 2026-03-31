"""
Test live prices API endpoints - BTC, ETH, XRP, SOL
Tests /api/market/live-prices and /api/live-prices alias
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLivePricesAPI:
    """Live prices endpoint tests for BTC, ETH, XRP, SOL"""
    
    def test_market_live_prices_returns_200(self):
        """GET /api/market/live-prices returns 200"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_market_live_prices_returns_all_four_coins(self):
        """GET /api/market/live-prices returns BTC, ETH, XRP, SOL"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "prices" in data, "Response should have 'prices' field"
        
        prices = data["prices"]
        assert len(prices) >= 4, f"Expected at least 4 coins, got {len(prices)}"
        
        symbols = [p["symbol"] for p in prices]
        assert "BTC" in symbols, "BTC should be in prices"
        assert "ETH" in symbols, "ETH should be in prices"
        assert "XRP" in symbols, "XRP should be in prices"
        assert "SOL" in symbols, "SOL should be in prices"
    
    def test_market_live_prices_correct_fields(self):
        """Each price object has correct fields: id, symbol, name, price, change_24h, volume_24h"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        prices = data["prices"]
        
        required_fields = ["id", "symbol", "name", "price", "change_24h", "volume_24h"]
        
        for coin in prices:
            for field in required_fields:
                assert field in coin, f"Coin {coin.get('symbol', 'unknown')} missing field '{field}'"
    
    def test_market_live_prices_sorted_by_market_cap(self):
        """Prices are sorted by market cap (BTC first, then ETH, XRP, SOL)"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        prices = data["prices"]
        symbols = [p["symbol"] for p in prices]
        
        # Check order: BTC should be first, ETH second, XRP third, SOL fourth
        btc_idx = symbols.index("BTC") if "BTC" in symbols else -1
        eth_idx = symbols.index("ETH") if "ETH" in symbols else -1
        xrp_idx = symbols.index("XRP") if "XRP" in symbols else -1
        sol_idx = symbols.index("SOL") if "SOL" in symbols else -1
        
        assert btc_idx == 0, f"BTC should be first, but is at index {btc_idx}"
        assert eth_idx == 1, f"ETH should be second, but is at index {eth_idx}"
        assert xrp_idx == 2, f"XRP should be third, but is at index {xrp_idx}"
        assert sol_idx == 3, f"SOL should be fourth, but is at index {sol_idx}"
    
    def test_market_live_prices_has_timestamp_and_source(self):
        """Response has timestamp and source fields"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data, "Response should have 'timestamp' field"
        assert "source" in data, "Response should have 'source' field"
        assert data["source"] in ["kraken", "fallback"], f"Source should be 'kraken' or 'fallback', got {data['source']}"
    
    def test_live_prices_alias_returns_200(self):
        """GET /api/live-prices (alias) returns 200"""
        response = requests.get(f"{BASE_URL}/api/live-prices", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_live_prices_alias_returns_same_data(self):
        """GET /api/live-prices returns same coins as /api/market/live-prices"""
        response1 = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        response2 = requests.get(f"{BASE_URL}/api/live-prices", timeout=10)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        symbols1 = set(p["symbol"] for p in data1["prices"])
        symbols2 = set(p["symbol"] for p in data2["prices"])
        
        assert symbols1 == symbols2, f"Alias should return same coins. Got {symbols1} vs {symbols2}"
    
    def test_btc_price_data_valid(self):
        """BTC price data is valid"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        btc = next((p for p in data["prices"] if p["symbol"] == "BTC"), None)
        
        assert btc is not None, "BTC should be in prices"
        assert btc["id"] == "bitcoin", f"BTC id should be 'bitcoin', got {btc['id']}"
        assert btc["name"] == "Bitcoin", f"BTC name should be 'Bitcoin', got {btc['name']}"
        assert isinstance(btc["price"], (int, float)), "BTC price should be numeric"
        assert btc["price"] > 0, "BTC price should be positive"
    
    def test_xrp_price_data_valid(self):
        """XRP price data is valid (newly added coin)"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        xrp = next((p for p in data["prices"] if p["symbol"] == "XRP"), None)
        
        assert xrp is not None, "XRP should be in prices"
        assert xrp["id"] == "xrp", f"XRP id should be 'xrp', got {xrp['id']}"
        assert xrp["name"] == "XRP", f"XRP name should be 'XRP', got {xrp['name']}"
        assert isinstance(xrp["price"], (int, float)), "XRP price should be numeric"
        assert xrp["price"] > 0, "XRP price should be positive"
    
    def test_sol_price_data_valid(self):
        """SOL price data is valid (newly added coin)"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        sol = next((p for p in data["prices"] if p["symbol"] == "SOL"), None)
        
        assert sol is not None, "SOL should be in prices"
        assert sol["id"] == "solana", f"SOL id should be 'solana', got {sol['id']}"
        assert sol["name"] == "Solana", f"SOL name should be 'Solana', got {sol['name']}"
        assert isinstance(sol["price"], (int, float)), "SOL price should be numeric"
        assert sol["price"] > 0, "SOL price should be positive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
