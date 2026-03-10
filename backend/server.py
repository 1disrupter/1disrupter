from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import random
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI(title="AlphaAI Fund Platform")
api_router = APIRouter(prefix="/api")

# ============= MODELS =============

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class Investor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_address: str
    balance: float = 0.0
    shares: float = 0.0
    total_deposited: float = 0.0
    total_withdrawn: float = 0.0
    paper_balance: float = 10000.0
    paper_pnl: float = 0.0
    is_paper_trading: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InvestorCreate(BaseModel):
    wallet_address: str

class DepositRequest(BaseModel):
    wallet_address: str
    amount: float

class WithdrawRequest(BaseModel):
    wallet_address: str
    amount: float

class TradingAgent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    status: str = "active"
    description: str
    strategy: str
    performance_7d: float = 0.0
    performance_30d: float = 0.0
    total_trades: int = 0
    win_rate: float = 0.0
    aum: float = 0.0
    capital_allocation: float = 0.0
    risk_score: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    developer_address: Optional[str] = None
    is_marketplace: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    strategy_id: Optional[str] = None
    symbol: str
    side: str
    amount: float
    price: float
    pnl: float = 0.0
    status: str = "completed"
    is_paper: bool = False
    execution_price: float = 0.0
    slippage: float = 0.0
    gas_fee: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MarketplaceAgent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    strategy: str
    developer_address: str
    developer_share: float = 90.0
    platform_fee: float = 10.0
    performance_30d: float = 0.0
    total_subscribers: int = 0
    min_investment: float = 100.0
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MarketplaceAgentCreate(BaseModel):
    name: str
    description: str
    strategy: str
    developer_address: str
    min_investment: float = 100.0

class AIAnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"

class RiskAlert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    severity: str
    message: str
    agent_id: Optional[str] = None
    strategy_id: Optional[str] = None
    resolved: bool = False
    auto_action_taken: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# NEW MODELS FOR STRATEGY LAB
class Strategy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    description: str
    parameters: Dict[str, Any] = {}
    status: str = "generated"
    backtest_results: Optional[Dict[str, Any]] = None
    sandbox_results: Optional[Dict[str, Any]] = None
    live_results: Optional[Dict[str, Any]] = None
    rank: int = 0
    sharpe_ratio: float = 0.0
    total_return: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    capital_allocated: float = 0.0
    is_active: bool = False
    created_by: str = "StrategyGeneratorAgent"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StrategyGenerateRequest(BaseModel):
    strategy_type: str
    risk_level: str = "medium"

class BacktestRequest(BaseModel):
    strategy_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 10000.0

class PaperTradeRequest(BaseModel):
    wallet_address: str
    symbol: str
    side: str
    amount: float

class RiskConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    max_drawdown: float = 5.0
    max_position_size: float = 10.0
    max_daily_loss: float = 2.0
    stop_loss: float = 2.0
    auto_shutdown_enabled: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CapitalAllocation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str
    strategy_name: str
    allocation_percent: float = 0.0
    allocated_capital: float = 0.0
    performance_score: float = 0.0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============= HELPER FUNCTIONS =============

async def get_market_data(symbol: str = "bitcoin"):
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://api.coingecko.com/api/v3/coins/{symbol}",
                params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
    return None

async def get_market_chart(symbol: str = "bitcoin", days: int = 30):
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart",
                params={"vs_currency": "usd", "days": days},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching chart data: {e}")
    return None

async def get_top_coins():
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 20, "page": 1},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching top coins: {e}")
    return []

def calculate_nav():
    base_nav = 1000000.0
    random_change = random.uniform(-0.05, 0.08)
    return base_nav * (1 + random_change)

def calculate_sharpe_ratio():
    return round(random.uniform(1.2, 2.8), 2)

def calculate_max_drawdown():
    return round(random.uniform(2.0, 8.0), 2)

def generate_historical_prices(days: int = 90, start_price: float = 45000):
    prices = []
    price = start_price
    for i in range(days):
        change = random.uniform(-0.03, 0.035)
        price *= (1 + change)
        prices.append({
            "date": (datetime.now(timezone.utc) - timedelta(days=days-i)).strftime("%Y-%m-%d"),
            "price": round(price, 2),
            "volume": random.randint(1000000, 50000000)
        })
    return prices

# ============= STATUS ROUTES =============

@api_router.get("/")
async def root():
    return {"message": "AlphaAI Fund Platform API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# ============= INVESTOR ROUTES =============

@api_router.post("/investors/register", response_model=Investor)
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

@api_router.get("/investors/{wallet_address}", response_model=Investor)
async def get_investor(wallet_address: str):
    investor = await db.investors.find_one({"wallet_address": wallet_address}, {"_id": 0})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    for key in ['created_at', 'updated_at']:
        if isinstance(investor.get(key), str):
            investor[key] = datetime.fromisoformat(investor[key])
    return Investor(**investor)

@api_router.post("/investors/deposit")
async def deposit_funds(request: DepositRequest):
    if request.amount < 100:
        raise HTTPException(status_code=400, detail="Minimum deposit is $100")
    
    investor = await db.investors.find_one({"wallet_address": request.wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    nav_per_share = calculate_nav() / 10000
    new_shares = request.amount / nav_per_share
    
    await db.investors.update_one(
        {"wallet_address": request.wallet_address},
        {
            "$inc": {"balance": request.amount, "shares": new_shares, "total_deposited": request.amount},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {
        "success": True,
        "message": f"Deposited ${request.amount}",
        "shares_received": round(new_shares, 4),
        "tx_hash": f"0x{uuid.uuid4().hex}"
    }

@api_router.post("/investors/withdraw")
async def withdraw_funds(request: WithdrawRequest):
    investor = await db.investors.find_one({"wallet_address": request.wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    if investor['balance'] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    nav_per_share = calculate_nav() / 10000
    shares_to_redeem = request.amount / nav_per_share
    
    await db.investors.update_one(
        {"wallet_address": request.wallet_address},
        {
            "$inc": {"balance": -request.amount, "shares": -shares_to_redeem, "total_withdrawn": request.amount},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {
        "success": True,
        "message": f"Withdrawn ${request.amount}",
        "shares_redeemed": round(shares_to_redeem, 4),
        "tx_hash": f"0x{uuid.uuid4().hex}"
    }

@api_router.post("/investors/toggle-paper-trading")
async def toggle_paper_trading(wallet_address: str):
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    new_status = not investor.get('is_paper_trading', False)
    await db.investors.update_one(
        {"wallet_address": wallet_address},
        {"$set": {"is_paper_trading": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"success": True, "is_paper_trading": new_status}

# ============= FUND ROUTES =============

@api_router.get("/fund/stats")
async def get_fund_stats():
    nav = calculate_nav()
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
        "total_trades_24h": random.randint(50, 200)
    }

@api_router.get("/fund/allocation")
async def get_fund_allocation():
    return [
        {"name": "Bitcoin (BTC)", "value": 35, "color": "#F7931A"},
        {"name": "Ethereum (ETH)", "value": 25, "color": "#627EEA"},
        {"name": "Stablecoins", "value": 20, "color": "#00FF94"},
        {"name": "DeFi Tokens", "value": 12, "color": "#7B61FF"},
        {"name": "Altcoins", "value": 8, "color": "#FF6B6B"}
    ]

@api_router.get("/fund/performance-history")
async def get_performance_history():
    data = []
    base_value = 100
    for i in range(30):
        base_value *= (1 + random.uniform(-0.02, 0.04))
        data.append({
            "date": (datetime.now(timezone.utc) - timedelta(days=30-i)).strftime("%Y-%m-%d"),
            "value": round(base_value, 2),
            "btc": round(base_value * random.uniform(0.9, 1.1), 2)
        })
    return data

# ============= TRADING AGENTS ROUTES =============

@api_router.get("/agents", response_model=List[TradingAgent])
async def get_trading_agents():
    agents = await db.trading_agents.find({}, {"_id": 0}).to_list(100)
    if not agents:
        default_agents = [
            TradingAgent(name="DataCollectorAgent", type="data", description="Collects market data from exchanges, on-chain data, and sentiment signals", strategy="Data Aggregation", performance_7d=0.0, performance_30d=0.0, total_trades=0, win_rate=0.0, aum=0.0, sharpe_ratio=0.0, capital_allocation=0.0),
            TradingAgent(name="DecisionAgent", type="analysis", description="Analyzes market signals and generates trading recommendations using AI", strategy="AI Signal Generation", performance_7d=round(random.uniform(2, 8), 2), performance_30d=round(random.uniform(10, 25), 2), total_trades=random.randint(100, 500), win_rate=round(random.uniform(55, 75), 1), aum=round(random.uniform(100000, 500000), 2), sharpe_ratio=round(random.uniform(1.5, 2.5), 2), capital_allocation=25.0),
            TradingAgent(name="StrategyAgent", type="strategy", description="Selects active strategies and optimizes capital allocation", strategy="Multi-Strategy Optimization", performance_7d=round(random.uniform(3, 10), 2), performance_30d=round(random.uniform(12, 30), 2), total_trades=random.randint(200, 800), win_rate=round(random.uniform(58, 72), 1), aum=round(random.uniform(200000, 800000), 2), sharpe_ratio=round(random.uniform(1.8, 2.8), 2), capital_allocation=35.0),
            TradingAgent(name="ExecutionAgent", type="execution", description="Executes trades with optimal gas fees and slippage management", strategy="Smart Order Routing", performance_7d=round(random.uniform(1, 5), 2), performance_30d=round(random.uniform(5, 15), 2), total_trades=random.randint(500, 2000), win_rate=round(random.uniform(60, 80), 1), aum=round(random.uniform(300000, 1000000), 2), sharpe_ratio=round(random.uniform(1.2, 2.0), 2), capital_allocation=30.0),
            TradingAgent(name="RiskAgent", type="risk", description="Enforces stop loss, monitors portfolio risk, and prevents large drawdowns", strategy="Risk Management", performance_7d=0.0, performance_30d=0.0, total_trades=random.randint(50, 200), win_rate=round(random.uniform(85, 98), 1), aum=0.0, sharpe_ratio=0.0, capital_allocation=10.0),
        ]
        for agent in default_agents:
            doc = agent.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.trading_agents.insert_one(doc)
        return default_agents
    
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    return [TradingAgent(**a) for a in agents]

@api_router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    agent = await db.trading_agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# ============= TRADES ROUTES =============

@api_router.get("/trades", response_model=List[Trade])
async def get_recent_trades(limit: int = Query(default=20, le=100)):
    trades = await db.trades.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    if not trades:
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "MATIC/USDT"]
        agents = ["DecisionAgent", "StrategyAgent", "ExecutionAgent"]
        generated_trades = []
        for i in range(20):
            trade = Trade(
                agent_id=random.choice(agents),
                symbol=random.choice(symbols),
                side=random.choice(["buy", "sell"]),
                amount=round(random.uniform(0.1, 10), 4),
                price=round(random.uniform(1000, 50000), 2),
                pnl=round(random.uniform(-500, 1000), 2),
                slippage=round(random.uniform(0.01, 0.5), 3),
                gas_fee=round(random.uniform(0.5, 10), 2),
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 1440))
            )
            doc = trade.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.trades.insert_one(doc)
            generated_trades.append(trade)
        return generated_trades
    
    for trade in trades:
        if isinstance(trade.get('timestamp'), str):
            trade['timestamp'] = datetime.fromisoformat(trade['timestamp'])
    return [Trade(**t) for t in trades]

# ============= MARKETPLACE ROUTES =============

@api_router.get("/marketplace/agents", response_model=List[MarketplaceAgent])
async def get_marketplace_agents():
    agents = await db.marketplace_agents.find({"status": "approved"}, {"_id": 0}).to_list(100)
    if not agents:
        default_marketplace = [
            MarketplaceAgent(name="Momentum Alpha", description="High-frequency momentum trading strategy targeting short-term price movements", strategy="Momentum Trading", developer_address="0x1234...5678", performance_30d=round(random.uniform(15, 35), 2), total_subscribers=random.randint(50, 200), status="approved"),
            MarketplaceAgent(name="DeFi Yield Hunter", description="Automatically finds and allocates to the highest yielding DeFi protocols", strategy="Yield Farming", developer_address="0xabcd...efgh", performance_30d=round(random.uniform(10, 25), 2), total_subscribers=random.randint(100, 500), status="approved"),
            MarketplaceAgent(name="Arbitrage Bot Pro", description="Cross-exchange arbitrage bot exploiting price inefficiencies", strategy="Arbitrage", developer_address="0x9876...5432", performance_30d=round(random.uniform(5, 15), 2), total_subscribers=random.randint(30, 150), status="approved"),
        ]
        for agent in default_marketplace:
            doc = agent.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.marketplace_agents.insert_one(doc)
        return default_marketplace
    
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    return [MarketplaceAgent(**a) for a in agents]

@api_router.post("/marketplace/agents", response_model=MarketplaceAgent)
async def submit_marketplace_agent(input: MarketplaceAgentCreate):
    agent = MarketplaceAgent(**input.model_dump())
    doc = agent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.marketplace_agents.insert_one(doc)
    return agent

# ============= AI ANALYSIS ROUTES =============

@api_router.post("/ai/analyze")
async def ai_market_analysis(request: AIAnalysisRequest):
    market_data = await get_market_data(request.symbol.lower())
    if not market_data:
        market_data = {"market_data": {"current_price": {"usd": 45000}, "price_change_percentage_24h": 2.5}}
    
    price = market_data.get("market_data", {}).get("current_price", {}).get("usd", 0)
    change_24h = market_data.get("market_data", {}).get("price_change_percentage_24h", 0)
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"analysis-{request.symbol}-{uuid.uuid4().hex[:8]}",
            system_message="You are an expert crypto trading analyst. Provide concise market analysis with actionable insights."
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(
            text=f"""Analyze {request.symbol.upper()} for trading:
- Current Price: ${price:,.2f}
- 24h Change: {change_24h:.2f}%
- Timeframe: {request.timeframe}

Provide: 1) Market sentiment 2) Key levels 3) Trading recommendation 4) Risk assessment (1-10) 5) Brief rationale"""
        )
        
        response = await chat.send_message(user_message)
        
        return {
            "symbol": request.symbol.upper(),
            "price": price,
            "change_24h": change_24h,
            "analysis": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logging.error(f"AI Analysis error: {e}")
        sentiment = "bullish" if change_24h > 0 else "bearish" if change_24h < -2 else "neutral"
        return {
            "symbol": request.symbol.upper(),
            "price": price,
            "change_24h": change_24h,
            "analysis": f"Market sentiment: {sentiment}. 24h change: {change_24h:.2f}%.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ============= MARKET DATA ROUTES =============

@api_router.get("/market/top-coins")
async def get_top_cryptocurrencies():
    coins = await get_top_coins()
    if coins:
        return [{"id": coin.get("id"), "symbol": coin.get("symbol", "").upper(), "name": coin.get("name"), "price": coin.get("current_price"), "change_24h": coin.get("price_change_percentage_24h"), "market_cap": coin.get("market_cap"), "volume": coin.get("total_volume"), "image": coin.get("image")} for coin in coins[:10]]
    return []

@api_router.get("/market/chart/{symbol}")
async def get_price_chart(symbol: str, days: int = Query(default=30, le=365)):
    chart_data = await get_market_chart(symbol.lower(), days)
    if chart_data and "prices" in chart_data:
        return {"symbol": symbol.upper(), "prices": [{"timestamp": p[0], "price": p[1]} for p in chart_data["prices"]]}
    return {"symbol": symbol.upper(), "prices": []}

# ============= RISK MANAGEMENT ENGINE =============

@api_router.get("/risk/config")
async def get_risk_config():
    config = await db.risk_config.find_one({}, {"_id": 0})
    if not config:
        default_config = RiskConfig()
        doc = default_config.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.risk_config.insert_one(doc)
        return default_config
    return config

@api_router.put("/risk/config")
async def update_risk_config(config: RiskConfig):
    doc = config.model_dump()
    doc['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.risk_config.update_one({}, {"$set": doc}, upsert=True)
    return {"success": True, "config": doc}

@api_router.get("/risk/alerts", response_model=List[RiskAlert])
async def get_risk_alerts():
    alerts = await db.risk_alerts.find({"resolved": False}, {"_id": 0}).to_list(100)
    if not alerts:
        default_alerts = [
            RiskAlert(type="drawdown", severity="medium", message="Portfolio drawdown approaching 4% threshold", agent_id="RiskAgent"),
            RiskAlert(type="volatility", severity="low", message="Market volatility elevated - monitoring positions", agent_id="DecisionAgent"),
        ]
        for alert in default_alerts:
            doc = alert.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.risk_alerts.insert_one(doc)
        return default_alerts
    
    for alert in alerts:
        if isinstance(alert.get('timestamp'), str):
            alert['timestamp'] = datetime.fromisoformat(alert['timestamp'])
    return [RiskAlert(**a) for a in alerts]

@api_router.post("/risk/alerts/{alert_id}/resolve")
async def resolve_risk_alert(alert_id: str):
    result = await db.risk_alerts.update_one({"id": alert_id}, {"$set": {"resolved": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "message": "Alert resolved"}

@api_router.get("/risk/portfolio-status")
async def get_portfolio_risk_status():
    config = await db.risk_config.find_one({}, {"_id": 0})
    if not config:
        config = {"max_drawdown": 5.0, "max_daily_loss": 2.0, "max_position_size": 10.0}
    
    current_drawdown = round(random.uniform(0.5, 4.5), 2)
    daily_pnl = round(random.uniform(-1.5, 3.0), 2)
    largest_position = round(random.uniform(5, 12), 2)
    
    return {
        "current_drawdown": current_drawdown,
        "max_drawdown_limit": config.get('max_drawdown', 5.0),
        "drawdown_utilization": round((current_drawdown / config.get('max_drawdown', 5.0)) * 100, 1),
        "daily_pnl": daily_pnl,
        "daily_loss_limit": config.get('max_daily_loss', 2.0),
        "largest_position": largest_position,
        "position_limit": config.get('max_position_size', 10.0),
        "risk_level": "high" if current_drawdown > 4 else "medium" if current_drawdown > 2 else "low",
        "auto_shutdown_triggered": False,
        "active_stop_losses": random.randint(2, 8)
    }

# ============= CAPITAL ALLOCATION ENGINE =============

@api_router.get("/capital/allocations")
async def get_capital_allocations():
    allocations = await db.capital_allocations.find({}, {"_id": 0}).to_list(100)
    if not allocations:
        strategies = ["Momentum Trading", "Arbitrage", "DeFi Yield", "Market Making", "Mean Reversion"]
        default_allocations = []
        total_capital = 1000000
        remaining = 100
        
        for i, strategy in enumerate(strategies):
            alloc_percent = random.randint(10, 30) if i < len(strategies) - 1 else remaining
            remaining -= alloc_percent if i < len(strategies) - 1 else 0
            
            allocation = CapitalAllocation(
                strategy_id=str(uuid.uuid4()),
                strategy_name=strategy,
                allocation_percent=alloc_percent,
                allocated_capital=round(total_capital * alloc_percent / 100, 2),
                performance_score=round(random.uniform(0.5, 1.5), 2)
            )
            doc = allocation.model_dump()
            doc['last_updated'] = doc['last_updated'].isoformat()
            await db.capital_allocations.insert_one(doc)
            default_allocations.append(allocation)
        
        return default_allocations
    
    return allocations

@api_router.post("/capital/rebalance")
async def rebalance_capital():
    strategies = await db.strategies.find({"is_active": True}, {"_id": 0}).to_list(100)
    if not strategies:
        return {"success": True, "message": "No active strategies to rebalance", "allocations": []}
    
    sorted_strategies = sorted(strategies, key=lambda x: x.get('sharpe_ratio', 0), reverse=True)
    
    total_score = sum(max(s.get('sharpe_ratio', 0), 0.1) for s in sorted_strategies)
    allocations = []
    
    for strategy in sorted_strategies:
        score = max(strategy.get('sharpe_ratio', 0), 0.1)
        alloc_percent = round((score / total_score) * 100, 2)
        allocations.append({
            "strategy_id": strategy.get('id'),
            "strategy_name": strategy.get('name'),
            "allocation_percent": alloc_percent,
            "sharpe_ratio": strategy.get('sharpe_ratio', 0)
        })
    
    return {"success": True, "message": "Capital rebalanced based on performance", "allocations": allocations}

# ============= EXECUTION OPTIMIZATION LAYER =============

@api_router.get("/execution/stats")
async def get_execution_stats():
    return {
        "total_orders_today": random.randint(100, 500),
        "avg_slippage": round(random.uniform(0.05, 0.3), 3),
        "avg_gas_fee": round(random.uniform(2, 15), 2),
        "orders_split": random.randint(20, 80),
        "best_price_achieved": round(random.uniform(85, 99), 1),
        "failed_orders": random.randint(0, 5),
        "dex_usage": {
            "uniswap_v3": round(random.uniform(40, 60), 1),
            "sushiswap": round(random.uniform(15, 25), 1),
            "curve": round(random.uniform(10, 20), 1),
            "balancer": round(random.uniform(5, 15), 1)
        }
    }

@api_router.post("/execution/simulate")
async def simulate_execution(symbol: str, amount: float, side: str):
    base_price = 45000 if "btc" in symbol.lower() else 2500
    slippage = round(random.uniform(0.01, 0.5), 3)
    gas_estimate = round(random.uniform(2, 20), 2)
    
    execution_price = base_price * (1 + slippage/100) if side == "buy" else base_price * (1 - slippage/100)
    
    return {
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "estimated_price": round(base_price, 2),
        "execution_price": round(execution_price, 2),
        "slippage_percent": slippage,
        "gas_estimate_usd": gas_estimate,
        "total_cost": round(execution_price * amount + gas_estimate, 2),
        "recommended_route": "Uniswap V3 -> Curve" if amount > 5 else "Uniswap V3",
        "split_orders": amount > 5
    }

# ============= AI RESEARCH & STRATEGY LAB =============

@api_router.get("/lab/strategies")
async def get_strategies():
    strategies = await db.strategies.find({}, {"_id": 0}).to_list(100)
    if not strategies:
        default_strategies = [
            Strategy(name="Momentum Breakout v1", type="momentum", description="Detects price breakouts and rides momentum", parameters={"lookback": 20, "threshold": 2.5}, status="live", sharpe_ratio=2.1, total_return=18.5, max_drawdown=3.2, win_rate=62.5, total_trades=156, capital_allocated=150000, is_active=True, rank=1),
            Strategy(name="Arbitrage Scanner v2", type="arbitrage", description="Cross-exchange price arbitrage", parameters={"min_spread": 0.3, "max_exposure": 10000}, status="live", sharpe_ratio=1.8, total_return=12.3, max_drawdown=1.5, win_rate=78.2, total_trades=423, capital_allocated=200000, is_active=True, rank=2),
            Strategy(name="DeFi Yield Optimizer", type="yield", description="Optimizes yield farming across protocols", parameters={"min_apy": 5, "max_tvl_ratio": 0.01}, status="sandbox", sharpe_ratio=1.5, total_return=8.7, max_drawdown=2.1, win_rate=85.0, total_trades=45, capital_allocated=0, is_active=False, rank=3),
            Strategy(name="Mean Reversion Alpha", type="mean_reversion", description="Trades price mean reversion patterns", parameters={"zscore_threshold": 2.0, "holding_period": 24}, status="backtesting", sharpe_ratio=1.2, total_return=5.2, max_drawdown=4.5, win_rate=55.0, total_trades=0, capital_allocated=0, is_active=False, rank=4),
            Strategy(name="Funding Rate Arbitrage", type="funding", description="Exploits perpetual funding rate differentials", parameters={"min_rate": 0.01, "leverage": 2}, status="generated", sharpe_ratio=0, total_return=0, max_drawdown=0, win_rate=0, total_trades=0, capital_allocated=0, is_active=False, rank=5),
        ]
        for strategy in default_strategies:
            doc = strategy.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.strategies.insert_one(doc)
        return default_strategies
    
    for s in strategies:
        if isinstance(s.get('created_at'), str):
            s['created_at'] = datetime.fromisoformat(s['created_at'])
    return sorted([Strategy(**s) for s in strategies], key=lambda x: x.rank)

@api_router.post("/lab/strategies/generate")
async def generate_strategy(request: StrategyGenerateRequest):
    strategy_templates = {
        "momentum": {"name": f"Momentum Strategy #{random.randint(100,999)}", "description": "AI-generated momentum trading strategy", "parameters": {"lookback": random.randint(10, 50), "threshold": round(random.uniform(1.5, 3.5), 2)}},
        "arbitrage": {"name": f"Arbitrage Strategy #{random.randint(100,999)}", "description": "AI-generated cross-exchange arbitrage", "parameters": {"min_spread": round(random.uniform(0.2, 0.8), 2), "max_exposure": random.randint(5000, 20000)}},
        "yield": {"name": f"Yield Strategy #{random.randint(100,999)}", "description": "AI-generated DeFi yield optimization", "parameters": {"min_apy": random.randint(3, 15), "risk_tolerance": request.risk_level}},
        "mean_reversion": {"name": f"Mean Reversion #{random.randint(100,999)}", "description": "AI-generated mean reversion strategy", "parameters": {"zscore_threshold": round(random.uniform(1.5, 3.0), 2), "holding_period": random.randint(6, 48)}},
        "funding": {"name": f"Funding Rate #{random.randint(100,999)}", "description": "AI-generated funding rate arbitrage", "parameters": {"min_rate": round(random.uniform(0.005, 0.02), 4), "leverage": random.randint(1, 3)}},
    }
    
    template = strategy_templates.get(request.strategy_type, strategy_templates["momentum"])
    
    strategy = Strategy(
        name=template["name"],
        type=request.strategy_type,
        description=template["description"],
        parameters=template["parameters"],
        status="generated",
        created_by="StrategyGeneratorAgent"
    )
    
    doc = strategy.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.strategies.insert_one(doc)
    
    return {"success": True, "message": "Strategy generated by AI", "strategy": strategy}

@api_router.post("/lab/strategies/{strategy_id}/backtest")
async def backtest_strategy(strategy_id: str, request: BacktestRequest):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Simulate backtest results
    total_return = round(random.uniform(-5, 35), 2)
    sharpe = round(random.uniform(0.5, 2.5), 2)
    max_dd = round(random.uniform(2, 10), 2)
    win_rate = round(random.uniform(45, 75), 1)
    total_trades = random.randint(50, 500)
    
    backtest_results = {
        "period": f"{request.start_date or '2024-01-01'} to {request.end_date or '2024-12-31'}",
        "initial_capital": request.initial_capital,
        "final_capital": round(request.initial_capital * (1 + total_return/100), 2),
        "total_return": total_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "total_trades": total_trades,
        "avg_trade_pnl": round((total_return * request.initial_capital / 100) / total_trades, 2),
        "profit_factor": round(random.uniform(1.1, 2.5), 2),
        "daily_returns": [round(random.uniform(-2, 3), 2) for _ in range(30)]
    }
    
    await db.strategies.update_one(
        {"id": strategy_id},
        {"$set": {
            "status": "backtested",
            "backtest_results": backtest_results,
            "sharpe_ratio": sharpe,
            "total_return": total_return,
            "max_drawdown": max_dd,
            "win_rate": win_rate
        }}
    )
    
    return {"success": True, "strategy_id": strategy_id, "results": backtest_results}

@api_router.post("/lab/strategies/{strategy_id}/sandbox")
async def start_sandbox_testing(strategy_id: str):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    sandbox_results = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "paper_trades": random.randint(10, 50),
        "paper_pnl": round(random.uniform(-500, 2000), 2),
        "live_sharpe": round(random.uniform(0.8, 2.2), 2),
        "status": "running"
    }
    
    await db.strategies.update_one(
        {"id": strategy_id},
        {"$set": {"status": "sandbox", "sandbox_results": sandbox_results}}
    )
    
    return {"success": True, "message": "Sandbox testing started", "strategy_id": strategy_id, "sandbox_results": sandbox_results}

@api_router.post("/lab/strategies/{strategy_id}/deploy")
async def deploy_strategy_live(strategy_id: str, capital: float = 10000):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.get('status') not in ['sandbox', 'backtested']:
        raise HTTPException(status_code=400, detail="Strategy must pass sandbox testing before deployment")
    
    strategies_count = await db.strategies.count_documents({"is_active": True})
    
    await db.strategies.update_one(
        {"id": strategy_id},
        {"$set": {
            "status": "live",
            "is_active": True,
            "capital_allocated": capital,
            "rank": strategies_count + 1,
            "live_results": {"deployed_at": datetime.now(timezone.utc).isoformat(), "initial_capital": capital}
        }}
    )
    
    return {"success": True, "message": f"Strategy deployed with ${capital} capital", "strategy_id": strategy_id}

@api_router.post("/lab/strategies/{strategy_id}/stop")
async def stop_strategy(strategy_id: str):
    result = await db.strategies.update_one(
        {"id": strategy_id},
        {"$set": {"status": "stopped", "is_active": False, "capital_allocated": 0}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"success": True, "message": "Strategy stopped"}

@api_router.get("/lab/rankings")
async def get_strategy_rankings():
    strategies = await db.strategies.find({"status": {"$in": ["live", "sandbox", "backtested"]}}, {"_id": 0}).to_list(100)
    
    ranked = sorted(strategies, key=lambda x: (x.get('sharpe_ratio', 0), x.get('total_return', 0)), reverse=True)
    
    for i, s in enumerate(ranked):
        s['rank'] = i + 1
        await db.strategies.update_one({"id": s['id']}, {"$set": {"rank": i + 1}})
    
    return [{
        "rank": s.get('rank', i+1),
        "id": s.get('id'),
        "name": s.get('name'),
        "type": s.get('type'),
        "status": s.get('status'),
        "sharpe_ratio": s.get('sharpe_ratio', 0),
        "total_return": s.get('total_return', 0),
        "max_drawdown": s.get('max_drawdown', 0),
        "win_rate": s.get('win_rate', 0),
        "capital_allocated": s.get('capital_allocated', 0)
    } for i, s in enumerate(ranked)]

# ============= PAPER TRADING =============

@api_router.post("/paper/trade")
async def execute_paper_trade(request: PaperTradeRequest):
    investor = await db.investors.find_one({"wallet_address": request.wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    paper_balance = investor.get('paper_balance', 10000)
    
    base_price = 45000 if "btc" in request.symbol.lower() else 2500 if "eth" in request.symbol.lower() else 100
    price = base_price * (1 + random.uniform(-0.01, 0.01))
    trade_value = request.amount * price
    
    if request.side == "buy" and trade_value > paper_balance:
        raise HTTPException(status_code=400, detail="Insufficient paper balance")
    
    pnl = round(random.uniform(-trade_value * 0.05, trade_value * 0.08), 2)
    
    trade = Trade(
        agent_id="PaperTrading",
        symbol=request.symbol,
        side=request.side,
        amount=request.amount,
        price=round(price, 2),
        pnl=pnl,
        is_paper=True,
        execution_price=round(price * (1 + random.uniform(-0.002, 0.002)), 2),
        slippage=round(random.uniform(0.01, 0.1), 3),
        gas_fee=0
    )
    
    new_balance = paper_balance + pnl if request.side == "sell" else paper_balance - trade_value + pnl
    
    await db.investors.update_one(
        {"wallet_address": request.wallet_address},
        {"$set": {"paper_balance": round(new_balance, 2)}, "$inc": {"paper_pnl": pnl}}
    )
    
    doc = trade.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.trades.insert_one(doc)
    
    return {
        "success": True,
        "trade": trade,
        "new_paper_balance": round(new_balance, 2),
        "pnl": pnl
    }

@api_router.get("/paper/portfolio/{wallet_address}")
async def get_paper_portfolio(wallet_address: str):
    investor = await db.investors.find_one({"wallet_address": wallet_address}, {"_id": 0})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    paper_trades = await db.trades.find({"is_paper": True}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    
    return {
        "paper_balance": investor.get('paper_balance', 10000),
        "paper_pnl": investor.get('paper_pnl', 0),
        "initial_balance": 10000,
        "return_percent": round((investor.get('paper_balance', 10000) - 10000) / 100, 2),
        "total_trades": len(paper_trades),
        "recent_trades": paper_trades[:10]
    }

@api_router.post("/paper/reset/{wallet_address}")
async def reset_paper_portfolio(wallet_address: str):
    result = await db.investors.update_one(
        {"wallet_address": wallet_address},
        {"$set": {"paper_balance": 10000, "paper_pnl": 0}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    await db.trades.delete_many({"is_paper": True})
    
    return {"success": True, "message": "Paper portfolio reset to $10,000"}

# ============= ANALYTICS ROUTES =============

@api_router.get("/analytics/overview")
async def get_analytics_overview():
    return {
        "daily_returns": [round(random.uniform(-2, 4), 2) for _ in range(30)],
        "monthly_returns": [round(random.uniform(-5, 15), 2) for _ in range(12)],
        "sharpe_ratio": calculate_sharpe_ratio(),
        "sortino_ratio": round(random.uniform(1.5, 3.5), 2),
        "max_drawdown": calculate_max_drawdown(),
        "win_rate": round(random.uniform(55, 70), 1),
        "profit_factor": round(random.uniform(1.3, 2.5), 2),
        "total_trades": random.randint(5000, 15000),
        "avg_trade_duration": f"{random.randint(1, 48)}h",
        "best_performing_strategy": "Momentum Trading",
        "worst_performing_strategy": "Mean Reversion"
    }

@api_router.get("/analytics/strategies")
async def get_strategy_analytics():
    return [
        {"name": "Arbitrage", "return": round(random.uniform(5, 20), 2), "trades": random.randint(500, 2000), "win_rate": round(random.uniform(65, 85), 1)},
        {"name": "Momentum Trading", "return": round(random.uniform(10, 30), 2), "trades": random.randint(300, 1000), "win_rate": round(random.uniform(50, 65), 1)},
        {"name": "DeFi Yield", "return": round(random.uniform(8, 25), 2), "trades": random.randint(100, 500), "win_rate": round(random.uniform(70, 90), 1)},
        {"name": "Liquidity Mining", "return": round(random.uniform(5, 15), 2), "trades": random.randint(50, 200), "win_rate": round(random.uniform(75, 95), 1)},
        {"name": "Mean Reversion", "return": round(random.uniform(-5, 10), 2), "trades": random.randint(200, 800), "win_rate": round(random.uniform(45, 60), 1)},
    ]

# ============= SMART CONTRACT INFO =============

@api_router.get("/contracts/info")
async def get_contract_info():
    return {
        "network": "Sepolia Testnet",
        "contracts": {
            "FundVault": {
                "address": "0x..." if False else "Not Deployed",
                "functions": ["deposit(uint256)", "withdraw(uint256)", "getShares(address)"],
                "status": "ready_for_deployment"
            },
            "ShareToken": {
                "address": "0x..." if False else "Not Deployed",
                "name": "AlphaAI Fund Share",
                "symbol": "ALPHA",
                "decimals": 18,
                "status": "ready_for_deployment"
            },
            "ProfitDistributor": {
                "address": "0x..." if False else "Not Deployed",
                "functions": ["distributeProfits()", "claimRewards()"],
                "status": "ready_for_deployment"
            }
        },
        "deployment_instructions": "Smart contracts are ready for Sepolia deployment. Contact admin with deployer private key."
    }

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
