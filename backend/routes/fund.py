"""
AlphaAI Fund & Investor Routes
Investor registration, fund stats, portfolio, and root endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
from database import db, logger
from models.schemas import Investor, InvestorCreate, DepositRequest, WithdrawRequest, StatusCheck, StatusCheckCreate
from services.signal_service import signal_service

router = APIRouter(prefix="/api")

# ============= INVESTOR ROUTES =============

@router.post("/investors/register", response_model=Investor)
async def register_investor(input: InvestorCreate):
    existing = await db.investors.find_one({"wallet_address": input.wallet_address}, {"_id": 0})
    if existing:
        for key in ['created_at', 'updated_at']:
            if isinstance(existing.get(key), str):
                existing[key] = datetime.fromisoformat(existing[key])
        return Investor(**existing)
    investor = Investor(wallet_address=input.wallet_address)
    doc = investor.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.investors.insert_one(doc)
    return investor

@router.get("/investors/{wallet_address}", response_model=Investor)
async def get_investor(wallet_address: str):
    investor = await db.investors.find_one({"wallet_address": wallet_address}, {"_id": 0})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    for key in ['created_at', 'updated_at']:
        if isinstance(investor.get(key), str):
            investor[key] = datetime.fromisoformat(investor[key])
    return Investor(**investor)

@router.post("/investors/deposit")
async def deposit_funds(request: DepositRequest):
    if request.amount < 100:
        raise HTTPException(status_code=400, detail="Minimum deposit is $100")
    investor = await db.investors.find_one({"wallet_address": request.wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    nav_per_share = calculate_nav() / 10000
    new_shares = request.amount / nav_per_share
    await db.investors.update_one({"wallet_address": request.wallet_address}, {"$inc": {"balance": request.amount, "shares": new_shares, "total_deposited": request.amount}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "message": f"Deposited ${request.amount}", "shares_received": round(new_shares, 4), "tx_hash": f"0x{uuid.uuid4().hex}"}

@router.post("/investors/withdraw")
async def withdraw_funds(request: WithdrawRequest):
    investor = await db.investors.find_one({"wallet_address": request.wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    if investor['balance'] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    nav_per_share = calculate_nav() / 10000
    shares_to_redeem = request.amount / nav_per_share
    await db.investors.update_one({"wallet_address": request.wallet_address}, {"$inc": {"balance": -request.amount, "shares": -shares_to_redeem, "total_withdrawn": request.amount}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "message": f"Withdrawn ${request.amount}", "shares_redeemed": round(shares_to_redeem, 4), "tx_hash": f"0x{uuid.uuid4().hex}"}

# ============= FUND ROUTES =============

@router.get("/")
async def root():
    return {"message": "AlphaAI Fund Platform API"}

@router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

@router.get("/fund/stats")
async def get_fund_stats():
    config = await db.simulation_config.find_one({}, {"_id": 0})
    nav = config.get('current_capital', 10000) * 100 if config else calculate_nav()
    return {
        "nav": round(nav, 2),
        "nav_change_24h": round(random.uniform(-2.5, 5.0), 2),
        "nav_change_7d": round(random.uniform(-5.0, 12.0), 2),
        "total_investors": await db.investors.count_documents({}),
        "total_aum": round(nav * 1.5, 2),
        "sharpe_ratio": calculate_sharpe_ratio(),
        "max_drawdown": calculate_max_drawdown(),
        "daily_return": round(random.uniform(-1.0, 2.5), 2),
        "monthly_return": round(random.uniform(-3.0, 15.0), 2),
        "yearly_return": round(random.uniform(20.0, 80.0), 2),
        "active_strategies": await db.strategies.count_documents({"is_active": True}) or 5,
        "total_trades_24h": config.get('total_trades', 0) if config else random.randint(50, 200),
        "simulation_running": config.get('is_running', False) if config else False
    }

@router.get("/fund/allocation")
async def get_fund_allocation():
    return [
        {"name": "Bitcoin (BTC)", "value": 35, "color": "#F7931A"},
        {"name": "Ethereum (ETH)", "value": 25, "color": "#627EEA"},
        {"name": "Stablecoins", "value": 20, "color": "#00FF94"},
        {"name": "DeFi Tokens", "value": 12, "color": "#7B61FF"},
        {"name": "Altcoins", "value": 8, "color": "#FF6B6B"}
    ]

@router.get("/fund/performance-history")
async def get_performance_history():
    data = []
    base_value = 100
    for i in range(30):
        base_value *= (1 + random.uniform(-0.02, 0.04))
        data.append({"date": (datetime.now(timezone.utc) - timedelta(days=30-i)).strftime("%Y-%m-%d"), "value": round(base_value, 2), "btc": round(base_value * random.uniform(0.9, 1.1), 2)})
    return data

# ============= MARKET DATA ROUTES =============

@router.get("/market/top-coins")
async def get_top_coins_endpoint():
    """Get top 20 coins by market cap from CoinGecko"""
    coins = await get_top_coins()
    if not coins:
        # Return mock data if CoinGecko is unavailable
        mock_coins = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 45000, "market_cap": 880000000000, "price_change_percentage_24h": 2.5},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 2500, "market_cap": 300000000000, "price_change_percentage_24h": 1.8},
            {"id": "solana", "symbol": "sol", "name": "Solana", "current_price": 100, "market_cap": 45000000000, "price_change_percentage_24h": 5.2},
            {"id": "avalanche", "symbol": "avax", "name": "Avalanche", "current_price": 35, "market_cap": 14000000000, "price_change_percentage_24h": 3.1},
            {"id": "polygon", "symbol": "matic", "name": "Polygon", "current_price": 0.8, "market_cap": 8000000000, "price_change_percentage_24h": -1.2},
        ]
        return mock_coins
    return coins

@router.get("/market/chart/{symbol}")
async def get_market_chart_endpoint(symbol: str, days: int = 30):
    """Get price chart data for a coin"""
    chart_data = await get_market_chart(symbol.lower(), days)
    if not chart_data:
        # Return mock chart data if CoinGecko is unavailable
        base_price = 45000 if symbol.lower() == "bitcoin" else 2500 if symbol.lower() == "ethereum" else 100
        mock_prices = []
        for i in range(days):
            timestamp = int((datetime.now(timezone.utc) - timedelta(days=days-i)).timestamp() * 1000)
            price = base_price * (1 + random.uniform(-0.05, 0.05))
            mock_prices.append([timestamp, round(price, 2)])
        return {"prices": mock_prices}
    return chart_data

@router.get("/market/live-prices")
async def get_live_prices():
    """Get live prices for major cryptocurrencies from Kraken"""
    try:
        async with httpx.AsyncClient() as client:
            # Use Kraken API - no rate limits for public endpoints
            response = await client.get(
                "https://api.kraken.com/0/public/Ticker",
                params={"pair": "XBTUSD,ETHUSD,SOLUSD,AVAXUSD,MATICUSD,LINKUSD,UNIUSD,AAVEUSD"},
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {})
                
                symbol_map = {
                    "XXBTZUSD": ("BTC", "Bitcoin"),
                    "XETHZUSD": ("ETH", "Ethereum"),
                    "SOLUSD": ("SOL", "Solana"),
                    "AVAXUSD": ("AVAX", "Avalanche"),
                    "MATICUSD": ("MATIC", "Polygon"),
                    "LINKUSD": ("LINK", "Chainlink"),
                    "UNIUSD": ("UNI", "Uniswap"),
                    "AAVEUSD": ("AAVE", "Aave")
                }
                
                prices = []
                for pair, ticker_data in result.items():
                    if pair in symbol_map:
                        symbol, name = symbol_map[pair]
                        current_price = float(ticker_data.get('c', ['0'])[0])
                        open_price = float(ticker_data.get('o', '0'))
                        volume = float(ticker_data.get('v', ['0', '0'])[1])
                        
                        # Calculate 24h change
                        change_24h = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0
                        
                        prices.append({
                            "id": name.lower(),
                            "symbol": symbol,
                            "name": name,
                            "price": round(current_price, 2 if current_price >= 1 else 4),
                            "change_24h": round(change_24h, 2),
                            "volume_24h": volume * current_price,
                            "market_cap": 0  # Kraken doesn't provide market cap
                        })
                
                if prices:
                    # Sort by a rough market cap estimate
                    cap_order = {"BTC": 1, "ETH": 2, "SOL": 3, "AVAX": 4, "LINK": 5, "MATIC": 6, "UNI": 7, "AAVE": 8}
                    prices.sort(key=lambda x: cap_order.get(x["symbol"], 99))
                    
                    return {
                        "prices": prices,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "source": "kraken"
                    }
    except Exception as e:
        print(f"Kraken API error: {e}")
    
    # Fallback - should rarely happen
    return {
        "prices": [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "price": 70000, "change_24h": 0, "volume_24h": 0, "market_cap": 0},
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum", "price": 2000, "change_24h": 0, "volume_24h": 0, "market_cap": 0},
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "fallback"
    }

# Alias for /market/live-prices - used by dashboard
@router.get("/live-prices")
async def get_live_prices_alias():
    """Alias endpoint for /market/live-prices - used by dashboard signals"""
    return await get_live_prices()

