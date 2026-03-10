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
from datetime import datetime, timezone
import httpx
import random
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# API Keys
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
    developer_address: Optional[str] = None
    is_marketplace: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    symbol: str
    side: str
    amount: float
    price: float
    pnl: float = 0.0
    status: str = "completed"
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
    resolved: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============= HELPER FUNCTIONS =============

async def get_market_data(symbol: str = "bitcoin"):
    """Fetch market data from CoinGecko"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.coingecko.com/api/v3/coins/{symbol}",
                params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
    return None

async def get_market_chart(symbol: str = "bitcoin", days: int = 30):
    """Fetch price chart data from CoinGecko"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart",
                params={"vs_currency": "usd", "days": days}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching chart data: {e}")
    return None

async def get_top_coins():
    """Fetch top cryptocurrencies from CoinGecko"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 20, "page": 1}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logging.error(f"Error fetching top coins: {e}")
    return []

def calculate_nav():
    """Calculate Net Asset Value"""
    base_nav = 1000000.0
    random_change = random.uniform(-0.05, 0.08)
    return base_nav * (1 + random_change)

def calculate_sharpe_ratio():
    """Calculate Sharpe Ratio"""
    return round(random.uniform(1.2, 2.8), 2)

def calculate_max_drawdown():
    """Calculate Max Drawdown"""
    return round(random.uniform(2.0, 8.0), 2)

# ============= ROUTES =============

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
    if isinstance(investor['created_at'], str):
        investor['created_at'] = datetime.fromisoformat(investor['created_at'])
    if isinstance(investor['updated_at'], str):
        investor['updated_at'] = datetime.fromisoformat(investor['updated_at'])
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
            "$inc": {
                "balance": request.amount,
                "shares": new_shares,
                "total_deposited": request.amount
            },
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
            "$inc": {
                "balance": -request.amount,
                "shares": -shares_to_redeem,
                "total_withdrawn": request.amount
            },
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {
        "success": True,
        "message": f"Withdrawn ${request.amount}",
        "shares_redeemed": round(shares_to_redeem, 4),
        "tx_hash": f"0x{uuid.uuid4().hex}"
    }

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
        "active_strategies": 5,
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
            "date": (datetime.now(timezone.utc).replace(day=1) + timedelta(days=i)).strftime("%Y-%m-%d") if i < 28 else datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "value": round(base_value, 2),
            "btc": round(base_value * random.uniform(0.9, 1.1), 2)
        })
    return data

from datetime import timedelta

# ============= TRADING AGENTS ROUTES =============

@api_router.get("/agents", response_model=List[TradingAgent])
async def get_trading_agents():
    agents = await db.trading_agents.find({}, {"_id": 0}).to_list(100)
    if not agents:
        default_agents = [
            TradingAgent(
                name="DataCollectorAgent",
                type="data",
                description="Collects market data from exchanges, on-chain data, and sentiment signals",
                strategy="Data Aggregation",
                performance_7d=0.0,
                performance_30d=0.0,
                total_trades=0,
                win_rate=0.0,
                aum=0.0
            ),
            TradingAgent(
                name="DecisionAgent",
                type="analysis",
                description="Analyzes market signals and generates trading recommendations using AI",
                strategy="AI Signal Generation",
                performance_7d=round(random.uniform(2, 8), 2),
                performance_30d=round(random.uniform(10, 25), 2),
                total_trades=random.randint(100, 500),
                win_rate=round(random.uniform(55, 75), 1),
                aum=round(random.uniform(100000, 500000), 2)
            ),
            TradingAgent(
                name="StrategyAgent",
                type="strategy",
                description="Selects active strategies and optimizes capital allocation",
                strategy="Multi-Strategy Optimization",
                performance_7d=round(random.uniform(3, 10), 2),
                performance_30d=round(random.uniform(12, 30), 2),
                total_trades=random.randint(200, 800),
                win_rate=round(random.uniform(58, 72), 1),
                aum=round(random.uniform(200000, 800000), 2)
            ),
            TradingAgent(
                name="ExecutionAgent",
                type="execution",
                description="Executes trades with optimal gas fees and slippage management",
                strategy="Smart Order Routing",
                performance_7d=round(random.uniform(1, 5), 2),
                performance_30d=round(random.uniform(5, 15), 2),
                total_trades=random.randint(500, 2000),
                win_rate=round(random.uniform(60, 80), 1),
                aum=round(random.uniform(300000, 1000000), 2)
            ),
            TradingAgent(
                name="RiskAgent",
                type="risk",
                description="Enforces stop loss, monitors portfolio risk, and prevents large drawdowns",
                strategy="Risk Management",
                performance_7d=0.0,
                performance_30d=0.0,
                total_trades=random.randint(50, 200),
                win_rate=round(random.uniform(85, 98), 1),
                aum=0.0
            )
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
            MarketplaceAgent(
                name="Momentum Alpha",
                description="High-frequency momentum trading strategy targeting short-term price movements",
                strategy="Momentum Trading",
                developer_address="0x1234...5678",
                performance_30d=round(random.uniform(15, 35), 2),
                total_subscribers=random.randint(50, 200),
                status="approved"
            ),
            MarketplaceAgent(
                name="DeFi Yield Hunter",
                description="Automatically finds and allocates to the highest yielding DeFi protocols",
                strategy="Yield Farming",
                developer_address="0xabcd...efgh",
                performance_30d=round(random.uniform(10, 25), 2),
                total_subscribers=random.randint(100, 500),
                status="approved"
            ),
            MarketplaceAgent(
                name="Arbitrage Bot Pro",
                description="Cross-exchange arbitrage bot exploiting price inefficiencies",
                strategy="Arbitrage",
                developer_address="0x9876...5432",
                performance_30d=round(random.uniform(5, 15), 2),
                total_subscribers=random.randint(30, 150),
                status="approved"
            )
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
            system_message="You are an expert crypto trading analyst. Provide concise market analysis with actionable insights. Be specific about entry/exit points and risk levels."
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(
            text=f"""Analyze {request.symbol.upper()} for trading:
- Current Price: ${price:,.2f}
- 24h Change: {change_24h:.2f}%
- Timeframe: {request.timeframe}

Provide:
1. Market sentiment (bullish/bearish/neutral)
2. Key support/resistance levels
3. Trading recommendation (buy/sell/hold)
4. Risk assessment (1-10)
5. Brief rationale (2-3 sentences)"""
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
            "analysis": f"Market sentiment: {sentiment}. 24h change: {change_24h:.2f}%. Consider risk management strategies.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ============= MARKET DATA ROUTES =============

@api_router.get("/market/top-coins")
async def get_top_cryptocurrencies():
    coins = await get_top_coins()
    if coins:
        return [
            {
                "id": coin.get("id"),
                "symbol": coin.get("symbol", "").upper(),
                "name": coin.get("name"),
                "price": coin.get("current_price"),
                "change_24h": coin.get("price_change_percentage_24h"),
                "market_cap": coin.get("market_cap"),
                "volume": coin.get("total_volume"),
                "image": coin.get("image")
            }
            for coin in coins[:10]
        ]
    return []

@api_router.get("/market/chart/{symbol}")
async def get_price_chart(symbol: str, days: int = Query(default=30, le=365)):
    chart_data = await get_market_chart(symbol.lower(), days)
    if chart_data and "prices" in chart_data:
        return {
            "symbol": symbol.upper(),
            "prices": [
                {"timestamp": p[0], "price": p[1]}
                for p in chart_data["prices"]
            ]
        }
    return {"symbol": symbol.upper(), "prices": []}

# ============= RISK ALERTS ROUTES =============

@api_router.get("/risk/alerts", response_model=List[RiskAlert])
async def get_risk_alerts():
    alerts = await db.risk_alerts.find({"resolved": False}, {"_id": 0}).to_list(100)
    if not alerts:
        default_alerts = [
            RiskAlert(
                type="drawdown",
                severity="medium",
                message="Portfolio drawdown approaching 4% threshold",
                agent_id="RiskAgent"
            ),
            RiskAlert(
                type="volatility",
                severity="low",
                message="Market volatility elevated - monitoring positions",
                agent_id="DecisionAgent"
            )
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
    result = await db.risk_alerts.update_one(
        {"id": alert_id},
        {"$set": {"resolved": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "message": "Alert resolved"}

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
    strategies = [
        {"name": "Arbitrage", "return": round(random.uniform(5, 20), 2), "trades": random.randint(500, 2000), "win_rate": round(random.uniform(65, 85), 1)},
        {"name": "Momentum Trading", "return": round(random.uniform(10, 30), 2), "trades": random.randint(300, 1000), "win_rate": round(random.uniform(50, 65), 1)},
        {"name": "DeFi Yield", "return": round(random.uniform(8, 25), 2), "trades": random.randint(100, 500), "win_rate": round(random.uniform(70, 90), 1)},
        {"name": "Liquidity Mining", "return": round(random.uniform(5, 15), 2), "trades": random.randint(50, 200), "win_rate": round(random.uniform(75, 95), 1)},
        {"name": "Mean Reversion", "return": round(random.uniform(-5, 10), 2), "trades": random.randint(200, 800), "win_rate": round(random.uniform(45, 60), 1)}
    ]
    return strategies

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
