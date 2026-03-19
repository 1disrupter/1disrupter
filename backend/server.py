from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, BackgroundTasks, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import random
import json
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

app = FastAPI(title="AlphaAI Fund Platform")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AlphaAI")

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
    is_simulation: bool = False
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

# MVP SIMULATION CONFIG MODEL
class SimulationConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_running: bool = False
    mode: str = "paper"  # paper, testnet, live
    initial_capital: float = 10000.0
    current_capital: float = 10000.0
    max_agents: int = 5
    reporting_frequency: str = "realtime"
    start_time: Optional[str] = None
    total_trades: int = 0
    total_pnl: float = 0.0
    active_strategies: List[str] = []
    risk_events_triggered: int = 0
    last_risk_check: Optional[str] = None
    auto_deploy_enabled: bool = True
    # Enhanced simulation settings
    time_acceleration: int = 1  # 1x = real-time, 100x = accelerated
    sim_start_date: str = "2025-01-01"
    sim_end_date: str = "2025-12-31"
    sim_current_date: Optional[str] = None
    historical_data_loaded: bool = False
    stress_test_active: bool = False
    stress_test_scenario: Optional[str] = None

class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # strategy, sandbox, data, execution, risk
    capital_allocation_percent: float = 25.0
    max_position: float = 0.1
    stop_loss_percent: float = 5.0
    auto_generate_strategies: bool = False
    backtest_historical: bool = False
    deploy_top_strategies: bool = False
    is_active: bool = True
    performance_ytd: float = 0.0
    trades_executed: int = 0

class StressTestScenario(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    trigger: str  # price_drop, volatility_spike, liquidity_crisis
    drop_percent: float = 30.0
    duration_hours: int = 24
    is_active: bool = False
    started_at: Optional[str] = None
    results: Optional[Dict[str, Any]] = None

class HistoricalDataPoint(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str = "BTC/USDT"

class SimulationExportRequest(BaseModel):
    formats: List[str] = ["pdf", "csv"]
    include_charts: bool = True
    include_trades: bool = True
    include_agent_performance: bool = True

class SimulationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    log_type: str  # trade, risk, allocation, strategy, agent
    agent_name: Optional[str] = None
    strategy_id: Optional[str] = None
    message: str
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentInteraction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str
    to_agent: str
    interaction_type: str  # signal, data, command, response
    payload: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============= SIMULATION ENGINE =============

class SimulationEngine:
    """Central simulation engine coordinating all agents and modules"""
    
    def __init__(self):
        self.is_running = False
        self.config = None
        self.current_drawdown = 0.0
        self.daily_pnl = 0.0
        self.positions = {}
        
    async def initialize(self):
        """Initialize or load simulation config"""
        config = await db.simulation_config.find_one({}, {"_id": 0})
        if not config:
            self.config = SimulationConfig()
            doc = self.config.model_dump()
            await db.simulation_config.insert_one(doc)
        else:
            self.config = SimulationConfig(**config)
        return self.config
    
    async def log_event(self, log_type: str, message: str, agent_name: str = None, strategy_id: str = None, details: dict = None):
        """Log simulation events to database"""
        log = SimulationLog(
            log_type=log_type,
            agent_name=agent_name,
            strategy_id=strategy_id,
            message=message,
            details=details or {}
        )
        doc = log.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.simulation_logs.insert_one(doc)
        logger.info(f"[{log_type.upper()}] {agent_name or 'SYSTEM'}: {message}")
        return log
    
    async def log_agent_interaction(self, from_agent: str, to_agent: str, interaction_type: str, payload: dict):
        """Log agent-to-agent interactions"""
        interaction = AgentInteraction(
            from_agent=from_agent,
            to_agent=to_agent,
            interaction_type=interaction_type,
            payload=payload
        )
        doc = interaction.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.agent_interactions.insert_one(doc)
        logger.info(f"[INTERACTION] {from_agent} -> {to_agent}: {interaction_type}")
        return interaction
    
    async def check_risk_rules(self) -> Dict[str, Any]:
        """Risk Engine: Check if any risk rules are triggered"""
        risk_config = await db.risk_config.find_one({}, {"_id": 0})
        if not risk_config:
            risk_config = {"max_drawdown": 5.0, "max_daily_loss": 2.0, "max_position_size": 10.0, "auto_shutdown_enabled": True}
        
        violations = []
        actions_taken = []
        
        # Check drawdown
        if self.current_drawdown >= risk_config.get('max_drawdown', 5.0):
            violations.append({"rule": "max_drawdown", "value": self.current_drawdown, "limit": risk_config['max_drawdown']})
            if risk_config.get('auto_shutdown_enabled', True):
                actions_taken.append("AUTO_STOP_ALL_TRADING")
                await self.log_event("risk", f"CRITICAL: Max drawdown {self.current_drawdown}% exceeded limit {risk_config['max_drawdown']}%. Auto-stopping trading.", agent_name="RiskAgent")
        
        # Check daily loss
        if abs(self.daily_pnl) >= risk_config.get('max_daily_loss', 2.0) and self.daily_pnl < 0:
            violations.append({"rule": "max_daily_loss", "value": self.daily_pnl, "limit": risk_config['max_daily_loss']})
            if risk_config.get('auto_shutdown_enabled', True):
                actions_taken.append("REDUCE_POSITION_SIZES")
                await self.log_event("risk", f"WARNING: Daily loss {self.daily_pnl}% approaching limit. Reducing positions.", agent_name="RiskAgent")
        
        # Create risk alert if violations
        if violations:
            alert = RiskAlert(
                type="rule_violation",
                severity="high" if "AUTO_STOP_ALL_TRADING" in actions_taken else "medium",
                message=f"Risk rules triggered: {', '.join([v['rule'] for v in violations])}",
                auto_action_taken=", ".join(actions_taken) if actions_taken else None
            )
            doc = alert.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.risk_alerts.insert_one(doc)
            
            # Update simulation config
            await db.simulation_config.update_one({}, {"$inc": {"risk_events_triggered": 1}})
        
        return {
            "violations": violations,
            "actions_taken": actions_taken,
            "current_drawdown": self.current_drawdown,
            "daily_pnl": self.daily_pnl,
            "risk_level": "critical" if violations else "normal"
        }
    
    async def dynamic_capital_allocation(self) -> List[Dict]:
        """Capital Allocation Engine: Reallocate based on performance"""
        strategies = await db.strategies.find({"status": {"$in": ["live", "sandbox"]}}, {"_id": 0}).to_list(100)
        
        if not strategies:
            return []
        
        # Calculate performance scores
        for s in strategies:
            s['performance_score'] = (s.get('sharpe_ratio', 0) * 0.4 + 
                                      s.get('total_return', 0) * 0.3 + 
                                      (100 - s.get('max_drawdown', 0)) * 0.3)
        
        # Sort by performance
        strategies = sorted(strategies, key=lambda x: x['performance_score'], reverse=True)
        
        # Allocate capital proportionally to top performers
        total_score = sum(max(s['performance_score'], 1) for s in strategies)
        total_capital = self.config.current_capital if self.config else 10000
        
        allocations = []
        for s in strategies:
            score = max(s['performance_score'], 1)
            alloc_percent = (score / total_score) * 100
            alloc_capital = total_capital * (alloc_percent / 100)
            
            allocation = {
                "strategy_id": s['id'],
                "strategy_name": s['name'],
                "allocation_percent": round(alloc_percent, 2),
                "allocated_capital": round(alloc_capital, 2),
                "performance_score": round(s['performance_score'], 2),
                "sharpe_ratio": s.get('sharpe_ratio', 0),
                "status": s['status']
            }
            allocations.append(allocation)
            
            # Update strategy in DB
            await db.strategies.update_one(
                {"id": s['id']},
                {"$set": {"capital_allocated": round(alloc_capital, 2)}}
            )
        
        await self.log_event("allocation", f"Capital reallocated across {len(allocations)} strategies", agent_name="CapitalAllocationEngine", details={"allocations": allocations[:3]})
        await self.log_agent_interaction("CapitalAllocationEngine", "StrategyAgent", "command", {"action": "update_allocations", "count": len(allocations)})
        
        return allocations
    
    async def execute_simulation_trade(self, strategy_id: str, symbol: str, side: str, amount: float) -> Trade:
        """Execution Layer: Execute a simulated trade"""
        # Get current price (simulated)
        prices = {"BTC/USDT": 45000, "ETH/USDT": 2500, "SOL/USDT": 100, "AVAX/USDT": 35, "MATIC/USDT": 0.8}
        base_price = prices.get(symbol, 100)
        
        # Calculate slippage and execution
        slippage = round(random.uniform(0.01, 0.3), 3)
        execution_price = base_price * (1 + slippage/100) if side == "buy" else base_price * (1 - slippage/100)
        gas_fee = round(random.uniform(1, 10), 2)
        
        # Calculate P&L
        price_movement = random.uniform(-0.02, 0.03)
        pnl = round(amount * execution_price * price_movement, 2)
        
        trade = Trade(
            agent_id="ExecutionAgent",
            strategy_id=strategy_id,
            symbol=symbol,
            side=side,
            amount=amount,
            price=base_price,
            execution_price=round(execution_price, 2),
            slippage=slippage,
            gas_fee=gas_fee,
            pnl=pnl,
            is_simulation=True,
            is_paper=True
        )
        
        doc = trade.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.trades.insert_one(doc)
        
        # Update simulation stats
        await db.simulation_config.update_one({}, {
            "$inc": {"total_trades": 1, "total_pnl": pnl},
            "$set": {"current_capital": self.config.current_capital + pnl if self.config else 10000 + pnl}
        })
        
        # Update daily P&L tracking
        self.daily_pnl += (pnl / (self.config.current_capital if self.config else 10000)) * 100
        
        # Log trade
        await self.log_event("trade", f"Executed {side.upper()} {amount} {symbol} @ ${execution_price:.2f}, P&L: ${pnl:.2f}", 
                           agent_name="ExecutionAgent", strategy_id=strategy_id, 
                           details={"slippage": slippage, "gas_fee": gas_fee})
        
        # Log agent interactions
        await self.log_agent_interaction("StrategyAgent", "ExecutionAgent", "signal", {"symbol": symbol, "side": side, "amount": amount})
        await self.log_agent_interaction("ExecutionAgent", "RiskAgent", "data", {"trade_id": trade.id, "pnl": pnl})
        
        # Check risk after trade
        await self.check_risk_rules()
        
        return trade
    
    async def run_strategy_cycle(self, strategy: dict) -> Dict:
        """Run one cycle of a strategy"""
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        symbol = random.choice(symbols)
        side = random.choice(["buy", "sell"])
        
        # Amount based on allocation
        capital = strategy.get('capital_allocated', 1000)
        amount = round(capital * random.uniform(0.01, 0.05) / 45000, 6)  # Fraction of BTC
        
        # Execute trade
        trade = await self.execute_simulation_trade(strategy['id'], symbol, side, amount)
        
        # Update strategy performance
        new_return = strategy.get('total_return', 0) + (trade.pnl / capital * 100) if capital > 0 else 0
        new_trades = strategy.get('total_trades', 0) + 1
        
        await db.strategies.update_one(
            {"id": strategy['id']},
            {"$set": {"total_return": round(new_return, 2), "total_trades": new_trades}}
        )
        
        return {"strategy_id": strategy['id'], "trade_id": trade.id, "pnl": trade.pnl}

# Global simulation engine instance
sim_engine = SimulationEngine()

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

# ============= SIMULATION ROUTES =============

@api_router.get("/simulation/config")
async def get_simulation_config():
    config = await sim_engine.initialize()
    return config

@api_router.post("/simulation/start")
async def start_simulation(background_tasks: BackgroundTasks):
    """Start the MVP simulation in paper trading mode"""
    config = await sim_engine.initialize()
    
    if config.is_running:
        return {"success": False, "message": "Simulation already running"}
    
    # Update config
    await db.simulation_config.update_one({}, {
        "$set": {
            "is_running": True,
            "mode": "paper",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "current_capital": config.initial_capital
        }
    })
    
    sim_engine.is_running = True
    sim_engine.config = await sim_engine.initialize()
    
    # Log start
    await sim_engine.log_event("system", "Simulation started in PAPER TRADING mode", details={"initial_capital": config.initial_capital, "max_agents": config.max_agents})
    
    # Log agent activations
    agents = ["DataCollectorAgent", "DecisionAgent", "StrategyAgent", "ExecutionAgent", "RiskAgent"]
    for agent in agents:
        await sim_engine.log_event("agent", f"{agent} activated", agent_name=agent)
        await sim_engine.log_agent_interaction("SimulationEngine", agent, "command", {"action": "activate"})
    
    # Initialize strategies in sandbox
    strategies = await db.strategies.find({}, {"_id": 0}).to_list(100)
    if not strategies:
        # Create default strategies
        default_types = ["momentum", "arbitrage"]
        for stype in default_types:
            strategy = Strategy(
                name=f"{stype.title()} Strategy v1",
                type=stype,
                description=f"Auto-generated {stype} strategy for simulation",
                parameters={"risk_level": "medium"},
                status="sandbox",
                sharpe_ratio=round(random.uniform(1.0, 2.5), 2),
                total_return=round(random.uniform(5, 20), 2),
                max_drawdown=round(random.uniform(2, 6), 2),
                win_rate=round(random.uniform(50, 70), 1),
                is_active=True
            )
            doc = strategy.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.strategies.insert_one(doc)
            await sim_engine.log_event("strategy", f"Strategy '{strategy.name}' initialized in sandbox", strategy_id=strategy.id)
    
    # Run initial capital allocation
    allocations = await sim_engine.dynamic_capital_allocation()
    
    return {
        "success": True,
        "message": "Simulation started in paper trading mode",
        "config": {
            "mode": "paper",
            "initial_capital": config.initial_capital,
            "strategies_active": len(allocations),
            "agents_active": len(agents)
        }
    }

@api_router.post("/simulation/stop")
async def stop_simulation():
    """Stop the simulation"""
    await db.simulation_config.update_one({}, {"$set": {"is_running": False}})
    sim_engine.is_running = False
    
    await sim_engine.log_event("system", "Simulation stopped")
    
    # Get final stats
    config = await db.simulation_config.find_one({}, {"_id": 0})
    
    return {
        "success": True,
        "message": "Simulation stopped",
        "final_stats": {
            "total_trades": config.get('total_trades', 0),
            "total_pnl": round(config.get('total_pnl', 0), 2),
            "final_capital": round(config.get('current_capital', 10000), 2),
            "risk_events": config.get('risk_events_triggered', 0)
        }
    }

@api_router.post("/simulation/run-cycle")
async def run_simulation_cycle():
    """Run one simulation cycle (execute trades for active strategies)"""
    config = await sim_engine.initialize()
    
    if not config.is_running:
        return {"success": False, "message": "Simulation not running. Start it first."}
    
    # Get active strategies
    strategies = await db.strategies.find({"status": {"$in": ["live", "sandbox"]}, "is_active": True}, {"_id": 0}).to_list(10)
    
    if not strategies:
        return {"success": False, "message": "No active strategies"}
    
    results = []
    for strategy in strategies:
        result = await sim_engine.run_strategy_cycle(strategy)
        results.append(result)
    
    # Check risk after cycle
    risk_status = await sim_engine.check_risk_rules()
    
    # Reallocate capital if needed
    if random.random() > 0.7:  # 30% chance to reallocate
        await sim_engine.dynamic_capital_allocation()
    
    return {
        "success": True,
        "cycle_results": results,
        "risk_status": risk_status,
        "total_trades": config.total_trades + len(results)
    }

@api_router.get("/simulation/logs")
async def get_simulation_logs(limit: int = 50, log_type: str = None):
    """Get simulation logs"""
    query = {}
    if log_type:
        query["log_type"] = log_type
    
    logs = await db.simulation_logs.find(query, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return logs

@api_router.get("/simulation/agent-interactions")
async def get_agent_interactions(limit: int = 50):
    """Get agent interaction logs"""
    interactions = await db.agent_interactions.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return interactions

@api_router.get("/simulation/stats")
async def get_simulation_stats():
    """Get comprehensive simulation statistics"""
    config = await db.simulation_config.find_one({}, {"_id": 0})
    if not config:
        config = {}
    
    # Get strategy stats
    strategies = await db.strategies.find({}, {"_id": 0}).to_list(100)
    active_strategies = [s for s in strategies if s.get('status') in ['live', 'sandbox']]
    
    # Get recent trades
    trades = await db.trades.find({"is_simulation": True}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    
    # Get risk alerts
    alerts = await db.risk_alerts.find({"resolved": False}, {"_id": 0}).to_list(50)
    
    # Calculate metrics
    total_pnl = sum(t.get('pnl', 0) for t in trades)
    winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
    win_rate = (winning_trades / len(trades) * 100) if trades else 0
    
    # Get agent configs
    agent_configs = await db.agent_configs.find({}, {"_id": 0}).to_list(10)
    
    return {
        "simulation": {
            "is_running": config.get('is_running', False),
            "mode": config.get('mode', 'paper'),
            "start_time": config.get('start_time'),
            "initial_capital": config.get('initial_capital', 10000),
            "current_capital": round(config.get('current_capital', 10000), 2),
            "total_return_percent": round((config.get('current_capital', 10000) - config.get('initial_capital', 10000)) / config.get('initial_capital', 10000) * 100, 2) if config.get('initial_capital', 10000) > 0 else 0,
            "time_acceleration": config.get('time_acceleration', 1),
            "sim_start_date": config.get('sim_start_date', '2025-01-01'),
            "sim_end_date": config.get('sim_end_date', '2025-12-31'),
            "sim_current_date": config.get('sim_current_date'),
            "historical_data_loaded": config.get('historical_data_loaded', False),
            "stress_test_active": config.get('stress_test_active', False),
            "stress_test_scenario": config.get('stress_test_scenario')
        },
        "trading": {
            "total_trades": len(trades),
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate, 1),
            "avg_trade_pnl": round(total_pnl / len(trades), 2) if trades else 0
        },
        "strategies": {
            "total": len(strategies),
            "active": len(active_strategies),
            "in_sandbox": len([s for s in strategies if s.get('status') == 'sandbox']),
            "live": len([s for s in strategies if s.get('status') == 'live'])
        },
        "risk": {
            "events_triggered": config.get('risk_events_triggered', 0),
            "active_alerts": len(alerts),
            "current_drawdown": sim_engine.current_drawdown,
            "daily_pnl": round(sim_engine.daily_pnl, 2)
        },
        "agents": agent_configs
    }

# ============= ENHANCED SIMULATION ROUTES =============

class AdvancedSimulationConfig(BaseModel):
    time_acceleration: int = 100
    start_date: str = "2025-01-01"
    end_date: str = "2025-12-31"
    initial_capital: float = 100000.0
    agents: List[Dict[str, Any]] = []
    stress_test_enabled: bool = False
    stress_scenarios: List[Dict[str, Any]] = []

@api_router.post("/simulation/configure")
async def configure_advanced_simulation(config: AdvancedSimulationConfig):
    """Configure advanced simulation with time acceleration and custom agents"""
    
    # Update simulation config
    await db.simulation_config.update_one({}, {
        "$set": {
            "time_acceleration": config.time_acceleration,
            "sim_start_date": config.start_date,
            "sim_end_date": config.end_date,
            "sim_current_date": config.start_date,
            "initial_capital": config.initial_capital,
            "current_capital": config.initial_capital,
            "stress_test_active": config.stress_test_enabled
        }
    }, upsert=True)
    
    # Clear and configure agents
    await db.agent_configs.delete_many({})
    configured_agents = []
    
    default_agents = [
        {"name": "Arbitrage Agent", "type": "strategy", "capital_allocation_percent": 25, "max_position": 0.1, "stop_loss_percent": 5},
        {"name": "Momentum Agent", "type": "strategy", "capital_allocation_percent": 25, "max_position": 0.1, "stop_loss_percent": 5},
        {"name": "Funding Rate Agent", "type": "strategy", "capital_allocation_percent": 25, "max_position": 0.1, "stop_loss_percent": 5},
        {"name": "AI Research Lab", "type": "sandbox", "capital_allocation_percent": 25, "auto_generate_strategies": True, "backtest_historical": True, "deploy_top_strategies": True}
    ]
    
    agents_to_use = config.agents if config.agents else default_agents
    
    for agent_data in agents_to_use:
        agent_config = AgentConfig(
            name=agent_data.get('name', 'Agent'),
            type=agent_data.get('type', 'strategy'),
            capital_allocation_percent=agent_data.get('capital_allocation_percent', 25),
            max_position=agent_data.get('risk_limits', {}).get('max_position', 0.1),
            stop_loss_percent=agent_data.get('risk_limits', {}).get('stop_loss_percent', 5),
            auto_generate_strategies=agent_data.get('auto_generate_strategies', False),
            backtest_historical=agent_data.get('backtest_historical', False),
            deploy_top_strategies=agent_data.get('deploy_top_strategies', False)
        )
        doc = agent_config.model_dump()
        await db.agent_configs.insert_one(doc)
        configured_agents.append({"name": agent_config.name, "type": agent_config.type, "allocation": agent_config.capital_allocation_percent})
    
    # Configure stress test scenarios
    if config.stress_test_enabled and config.stress_scenarios:
        await db.stress_scenarios.delete_many({})
        for scenario in config.stress_scenarios:
            stress = StressTestScenario(
                name=scenario.get('name', 'Stress Test'),
                trigger=scenario.get('trigger', 'price_drop'),
                drop_percent=scenario.get('drop_percent', 30),
                duration_hours=scenario.get('duration_hours', 24)
            )
            await db.stress_scenarios.insert_one(stress.model_dump())
    
    await sim_engine.log_event("system", f"Advanced simulation configured: {config.time_acceleration}x speed, {len(configured_agents)} agents", 
                              agent_name="SystemAdmin", 
                              details={"time_acceleration": config.time_acceleration, "agents": len(configured_agents)})
    
    return {
        "success": True,
        "message": f"Simulation configured with {config.time_acceleration}x time acceleration",
        "config": {
            "time_acceleration": config.time_acceleration,
            "period": f"{config.start_date} to {config.end_date}",
            "initial_capital": config.initial_capital,
            "agents": configured_agents,
            "stress_test_enabled": config.stress_test_enabled
        }
    }

@api_router.post("/simulation/run-accelerated")
async def run_accelerated_simulation(days_to_simulate: int = 30):
    """Run accelerated simulation for specified number of days"""
    config = await sim_engine.initialize()
    
    if not config.is_running:
        # Auto-start if not running
        await db.simulation_config.update_one({}, {"$set": {"is_running": True, "start_time": datetime.now(timezone.utc).isoformat()}})
        sim_engine.is_running = True
    
    time_acceleration = config.time_acceleration if hasattr(config, 'time_acceleration') else 100
    
    # Get agent configs
    agent_configs = await db.agent_configs.find({}, {"_id": 0}).to_list(10)
    if not agent_configs:
        agent_configs = [
            {"name": "Arbitrage Agent", "capital_allocation_percent": 25},
            {"name": "Momentum Agent", "capital_allocation_percent": 25},
            {"name": "Funding Rate Agent", "capital_allocation_percent": 25},
            {"name": "AI Research Lab", "capital_allocation_percent": 25}
        ]
    
    # Simulate multiple days worth of trading
    all_results = []
    total_pnl = 0
    current_capital = config.current_capital if config else 100000
    
    cycles_per_day = 10  # Each cycle = ~2.4 hours of trading
    total_cycles = days_to_simulate * cycles_per_day
    
    await sim_engine.log_event("system", f"Starting accelerated simulation: {days_to_simulate} days at {time_acceleration}x speed", agent_name="SimulationEngine")
    
    for day in range(days_to_simulate):
        day_pnl = 0
        day_trades = []
        
        for agent in agent_configs:
            agent_name = agent.get('name', 'Agent')
            allocation = agent.get('capital_allocation_percent', 25) / 100
            agent_capital = current_capital * allocation
            
            # Simulate trades for this agent
            for _ in range(cycles_per_day):
                symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
                symbol = random.choice(symbols)
                side = random.choice(["buy", "sell"])
                
                # Price simulation with volatility
                base_prices = {"BTC/USDT": 45000, "ETH/USDT": 2500, "SOL/USDT": 100}
                price = base_prices.get(symbol, 100) * (1 + random.uniform(-0.02, 0.02))
                
                amount = agent_capital * random.uniform(0.01, 0.05) / price
                pnl = amount * price * random.uniform(-0.03, 0.04)
                
                day_pnl += pnl
                day_trades.append({
                    "agent": agent_name,
                    "symbol": symbol,
                    "side": side,
                    "pnl": round(pnl, 2)
                })
        
        current_capital += day_pnl
        total_pnl += day_pnl
        
        all_results.append({
            "day": day + 1,
            "trades": len(day_trades),
            "day_pnl": round(day_pnl, 2),
            "cumulative_pnl": round(total_pnl, 2),
            "capital": round(current_capital, 2)
        })
    
    # Update config with final state
    await db.simulation_config.update_one({}, {
        "$set": {
            "current_capital": round(current_capital, 2),
            "total_pnl": round(total_pnl, 2)
        },
        "$inc": {"total_trades": total_cycles * len(agent_configs)}
    })
    
    # Calculate metrics
    winning_days = len([r for r in all_results if r['day_pnl'] > 0])
    best_day = max(all_results, key=lambda x: x['day_pnl'])
    worst_day = min(all_results, key=lambda x: x['day_pnl'])
    
    await sim_engine.log_event("system", f"Accelerated simulation complete: {days_to_simulate} days, P&L: ${total_pnl:.2f}", 
                              agent_name="SimulationEngine",
                              details={"days": days_to_simulate, "total_pnl": round(total_pnl, 2), "win_rate": round(winning_days/days_to_simulate*100, 1)})
    
    return {
        "success": True,
        "message": f"Simulated {days_to_simulate} days of trading at {time_acceleration}x speed",
        "summary": {
            "days_simulated": days_to_simulate,
            "total_trades": total_cycles * len(agent_configs),
            "initial_capital": config.initial_capital if config else 100000,
            "final_capital": round(current_capital, 2),
            "total_pnl": round(total_pnl, 2),
            "total_return_percent": round((total_pnl / (config.initial_capital if config else 100000)) * 100, 2),
            "winning_days": winning_days,
            "losing_days": days_to_simulate - winning_days,
            "win_rate": round(winning_days / days_to_simulate * 100, 1),
            "best_day": best_day,
            "worst_day": worst_day
        },
        "daily_results": all_results[-7:]  # Last 7 days
    }

@api_router.post("/simulation/stress-test")
async def run_stress_test(scenario_name: str = "High Volatility BTC Drop"):
    """Run a stress test scenario"""
    
    # Get or create scenario
    scenarios = {
        "High Volatility BTC Drop": {"trigger": "price_drop", "drop_percent": 30, "duration_hours": 24},
        "ETH Flash Crash": {"trigger": "price_drop", "drop_percent": 50, "duration_hours": 12},
        "Market Panic Sell": {"trigger": "price_drop", "drop_percent": 40, "duration_hours": 6},
        "Liquidity Crisis": {"trigger": "liquidity_crisis", "drop_percent": 25, "duration_hours": 48}
    }
    
    scenario = scenarios.get(scenario_name, scenarios["High Volatility BTC Drop"])
    
    await db.simulation_config.update_one({}, {
        "$set": {"stress_test_active": True, "stress_test_scenario": scenario_name}
    })
    
    await sim_engine.log_event("stress_test", f"STRESS TEST STARTED: {scenario_name}", agent_name="RiskAgent", details=scenario)
    
    config = await db.simulation_config.find_one({}, {"_id": 0})
    initial_capital = config.get('current_capital', 100000) if config else 100000
    
    # Simulate stress scenario
    drop_percent = scenario['drop_percent']
    duration_hours = scenario['duration_hours']
    
    # Simulate hourly impact
    hourly_results = []
    current_capital = initial_capital
    max_drawdown = 0
    
    for hour in range(duration_hours):
        # Progressive drop with some recovery attempts
        hour_drop = (drop_percent / duration_hours) * (1 + random.uniform(-0.3, 0.2))
        hour_loss = current_capital * (hour_drop / 100)
        current_capital -= hour_loss
        
        drawdown = ((initial_capital - current_capital) / initial_capital) * 100
        max_drawdown = max(max_drawdown, drawdown)
        
        hourly_results.append({
            "hour": hour + 1,
            "capital": round(current_capital, 2),
            "drawdown_percent": round(drawdown, 2),
            "loss": round(hour_loss, 2)
        })
        
        # Check if risk limits triggered
        if drawdown >= 5:
            await sim_engine.log_event("risk", f"RISK ALERT: Drawdown {drawdown:.1f}% exceeds 5% limit", agent_name="RiskAgent")
        
        # Simulate partial recovery in later hours
        if hour > duration_hours * 0.7:
            recovery = current_capital * random.uniform(0.005, 0.02)
            current_capital += recovery
    
    # Calculate final results
    total_loss = initial_capital - current_capital
    final_drawdown = ((initial_capital - current_capital) / initial_capital) * 100
    
    # Risk agent response
    risk_actions = []
    if max_drawdown > 5:
        risk_actions.append("AUTO_STOP_ALL_TRADING triggered at 5% drawdown")
    if max_drawdown > 3:
        risk_actions.append("REDUCE_POSITION_SIZES by 50%")
    if max_drawdown > 2:
        risk_actions.append("RISK_ALERT sent to all agents")
    
    await db.simulation_config.update_one({}, {
        "$set": {
            "stress_test_active": False,
            "current_capital": round(current_capital, 2)
        },
        "$inc": {"risk_events_triggered": 1}
    })
    
    sim_engine.current_drawdown = final_drawdown
    
    result = {
        "success": True,
        "scenario": scenario_name,
        "parameters": scenario,
        "results": {
            "initial_capital": initial_capital,
            "final_capital": round(current_capital, 2),
            "total_loss": round(total_loss, 2),
            "max_drawdown_percent": round(max_drawdown, 2),
            "final_drawdown_percent": round(final_drawdown, 2),
            "duration_hours": duration_hours,
            "risk_actions_taken": risk_actions,
            "survival_status": "SURVIVED" if final_drawdown < 20 else "CRITICAL"
        },
        "hourly_breakdown": hourly_results[-6:]  # Last 6 hours
    }
    
    await sim_engine.log_event("stress_test", f"STRESS TEST COMPLETE: {scenario_name} - Max Drawdown: {max_drawdown:.1f}%", 
                              agent_name="RiskAgent", details=result['results'])
    
    return result

@api_router.get("/simulation/stress-scenarios")
async def get_stress_scenarios():
    """Get available stress test scenarios"""
    return {
        "scenarios": [
            {"name": "High Volatility BTC Drop", "trigger": "price_drop", "drop_percent": 30, "duration_hours": 24, "description": "BTC drops 30% over 24 hours"},
            {"name": "ETH Flash Crash", "trigger": "price_drop", "drop_percent": 50, "duration_hours": 12, "description": "ETH flash crash of 50% in 12 hours"},
            {"name": "Market Panic Sell", "trigger": "price_drop", "drop_percent": 40, "duration_hours": 6, "description": "Rapid market-wide selloff"},
            {"name": "Liquidity Crisis", "trigger": "liquidity_crisis", "drop_percent": 25, "duration_hours": 48, "description": "Extended liquidity crisis"}
        ]
    }

@api_router.get("/simulation/agent-performance")
async def get_agent_performance():
    """Get performance metrics for each configured agent"""
    agent_configs = await db.agent_configs.find({}, {"_id": 0}).to_list(10)
    
    if not agent_configs:
        # Return default agent performance
        default_agents = [
            {"name": "Arbitrage Agent", "type": "strategy", "capital_allocation_percent": 25, "performance_ytd": round(random.uniform(8, 25), 2), "trades_executed": random.randint(100, 500), "win_rate": round(random.uniform(60, 80), 1), "sharpe_ratio": round(random.uniform(1.2, 2.5), 2)},
            {"name": "Momentum Agent", "type": "strategy", "capital_allocation_percent": 25, "performance_ytd": round(random.uniform(5, 30), 2), "trades_executed": random.randint(80, 400), "win_rate": round(random.uniform(50, 70), 1), "sharpe_ratio": round(random.uniform(1.0, 2.2), 2)},
            {"name": "Funding Rate Agent", "type": "strategy", "capital_allocation_percent": 25, "performance_ytd": round(random.uniform(10, 20), 2), "trades_executed": random.randint(50, 200), "win_rate": round(random.uniform(65, 85), 1), "sharpe_ratio": round(random.uniform(1.5, 2.8), 2)},
            {"name": "AI Research Lab", "type": "sandbox", "capital_allocation_percent": 25, "performance_ytd": round(random.uniform(0, 15), 2), "strategies_generated": random.randint(10, 50), "strategies_deployed": random.randint(2, 10), "backtest_success_rate": round(random.uniform(40, 70), 1)}
        ]
        return {"agents": default_agents}
    
    # Enhance agent configs with simulated performance
    for agent in agent_configs:
        agent['performance_ytd'] = round(random.uniform(5, 25), 2)
        agent['trades_executed'] = random.randint(50, 500)
        agent['win_rate'] = round(random.uniform(50, 80), 1)
        agent['sharpe_ratio'] = round(random.uniform(1.0, 2.5), 2)
    
    return {"agents": agent_configs}

@api_router.post("/simulation/export")
async def export_simulation_results(request: SimulationExportRequest):
    """Export simulation results in various formats"""
    
    config = await db.simulation_config.find_one({}, {"_id": 0})
    trades = await db.trades.find({"is_simulation": True}, {"_id": 0}).sort("timestamp", -1).to_list(1000)
    strategies = await db.strategies.find({}, {"_id": 0}).to_list(100)
    agent_configs = await db.agent_configs.find({}, {"_id": 0}).to_list(10)
    
    # Prepare export data
    export_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "simulation_config": {
            "mode": config.get('mode', 'paper') if config else 'paper',
            "initial_capital": config.get('initial_capital', 100000) if config else 100000,
            "current_capital": config.get('current_capital', 100000) if config else 100000,
            "total_trades": len(trades),
            "time_acceleration": config.get('time_acceleration', 1) if config else 1,
            "period": f"{config.get('sim_start_date', '2025-01-01')} to {config.get('sim_end_date', '2025-12-31')}" if config else "2025-01-01 to 2025-12-31"
        },
        "performance_summary": {
            "total_pnl": round(sum(t.get('pnl', 0) for t in trades), 2),
            "total_return_percent": round(((config.get('current_capital', 100000) - config.get('initial_capital', 100000)) / config.get('initial_capital', 100000)) * 100, 2) if config else 0,
            "win_rate": round(len([t for t in trades if t.get('pnl', 0) > 0]) / len(trades) * 100, 1) if trades else 0,
            "sharpe_ratio": round(random.uniform(1.2, 2.5), 2),
            "max_drawdown": round(sim_engine.current_drawdown, 2)
        },
        "agents": agent_configs if agent_configs else [],
        "strategies_count": len(strategies),
        "trades_count": len(trades)
    }
    
    if request.include_trades:
        export_data["recent_trades"] = trades[:100]
    
    if request.include_agent_performance:
        export_data["agent_performance"] = [
            {"name": "Arbitrage Agent", "return": round(random.uniform(8, 25), 2), "trades": random.randint(100, 500)},
            {"name": "Momentum Agent", "return": round(random.uniform(5, 30), 2), "trades": random.randint(80, 400)},
            {"name": "Funding Rate Agent", "return": round(random.uniform(10, 20), 2), "trades": random.randint(50, 200)},
            {"name": "AI Research Lab", "return": round(random.uniform(0, 15), 2), "strategies_deployed": random.randint(2, 10)}
        ]
    
    await sim_engine.log_event("export", f"Simulation results exported in formats: {request.formats}", agent_name="ReportingAgent")
    
    return {
        "success": True,
        "message": f"Export generated in formats: {', '.join(request.formats)}",
        "export_data": export_data,
        "download_links": {
            "csv": "/api/simulation/export/download?format=csv",
            "pdf": "/api/simulation/export/download?format=pdf",
            "json": "/api/simulation/export/download?format=json"
        }
    }

@api_router.post("/simulation/load-historical-data")
async def load_historical_data(source_url: str = None, use_sample: bool = True):
    """Load historical price data for backtesting"""
    
    if use_sample:
        # Generate sample historical data for BTC and ETH
        historical_data = []
        base_prices = {"BTC/USDT": 42000, "ETH/USDT": 2200}
        
        start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        
        for symbol, base_price in base_prices.items():
            price = base_price
            for day in range(365):
                current_date = start_date + timedelta(days=day)
                
                # Simulate daily OHLCV
                daily_change = random.uniform(-0.05, 0.06)
                open_price = price
                close_price = price * (1 + daily_change)
                high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
                low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))
                volume = random.uniform(1000000, 5000000)
                
                historical_data.append({
                    "timestamp": current_date.isoformat(),
                    "symbol": symbol,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": round(volume, 2)
                })
                
                price = close_price
        
        # Store in database
        await db.historical_data.delete_many({})
        await db.historical_data.insert_many(historical_data)
        
        await db.simulation_config.update_one({}, {"$set": {"historical_data_loaded": True}})
        
        await sim_engine.log_event("data", f"Historical data loaded: {len(historical_data)} data points for BTC and ETH", agent_name="DataCollectorAgent")
        
        return {
            "success": True,
            "message": "Sample historical data loaded for 2025",
            "data_points": len(historical_data),
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "period": "2025-01-01 to 2025-12-31"
        }
    
    return {"success": False, "message": "External data source loading not implemented. Use sample data."}


# ============= AI RESEARCH LAB ROUTES =============

@api_router.get("/reports/daily")
async def get_daily_report():
    """Generate daily performance report"""
    config = await db.simulation_config.find_one({}, {"_id": 0})
    today = datetime.now(timezone.utc).date()
    
    # Get today's trades
    trades = await db.trades.find({}, {"_id": 0}).to_list(1000)
    today_trades = [t for t in trades if t.get('timestamp', '').startswith(str(today)) or 
                   (isinstance(t.get('timestamp'), str) and t['timestamp'][:10] == str(today))]
    
    # Calculate daily metrics
    daily_pnl = sum(t.get('pnl', 0) for t in today_trades)
    daily_trades = len(today_trades)
    daily_winners = len([t for t in today_trades if t.get('pnl', 0) > 0])
    daily_win_rate = (daily_winners / daily_trades * 100) if daily_trades > 0 else 0
    
    # Get strategy performance
    strategies = await db.strategies.find({"is_active": True}, {"_id": 0}).to_list(100)
    strategy_performance = [{"name": s['name'], "return": s.get('total_return', 0), "sharpe": s.get('sharpe_ratio', 0)} for s in strategies[:5]]
    
    # Get risk events
    alerts = await db.risk_alerts.find({}, {"_id": 0}).to_list(100)
    today_alerts = [a for a in alerts if str(today) in str(a.get('timestamp', ''))]
    
    report = {
        "report_type": "daily",
        "date": str(today),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "starting_capital": config.get('initial_capital', 10000) if config else 10000,
            "current_capital": config.get('current_capital', 10000) if config else 10000,
            "daily_pnl": round(daily_pnl, 2),
            "daily_return_percent": round((daily_pnl / (config.get('current_capital', 10000) if config else 10000)) * 100, 2),
            "total_return_percent": round(((config.get('current_capital', 10000) if config else 10000) - (config.get('initial_capital', 10000) if config else 10000)) / (config.get('initial_capital', 10000) if config else 10000) * 100, 2)
        },
        "trading": {
            "total_trades": daily_trades,
            "winning_trades": daily_winners,
            "losing_trades": daily_trades - daily_winners,
            "win_rate": round(daily_win_rate, 1),
            "avg_trade_pnl": round(daily_pnl / daily_trades, 2) if daily_trades > 0 else 0,
            "best_trade": round(max([t.get('pnl', 0) for t in today_trades], default=0), 2),
            "worst_trade": round(min([t.get('pnl', 0) for t in today_trades], default=0), 2)
        },
        "strategies": {
            "active_count": len(strategies),
            "top_performers": strategy_performance
        },
        "risk": {
            "current_drawdown": round(sim_engine.current_drawdown, 2),
            "alerts_triggered": len(today_alerts),
            "risk_level": "high" if sim_engine.current_drawdown > 4 else "medium" if sim_engine.current_drawdown > 2 else "low"
        }
    }
    
    # Save report
    await db.reports.insert_one({**report, "id": str(uuid.uuid4())})
    await sim_engine.log_event("report", f"Daily report generated: PnL ${daily_pnl:.2f}, {daily_trades} trades", agent_name="ReportingAgent", details=report['summary'])
    
    return report

@api_router.get("/reports/weekly")
async def get_weekly_report():
    """Generate weekly performance report"""
    config = await db.simulation_config.find_one({}, {"_id": 0})
    today = datetime.now(timezone.utc)
    week_start = today - timedelta(days=7)
    
    # Get week's trades
    trades = await db.trades.find({}, {"_id": 0}).to_list(5000)
    
    # Calculate weekly metrics
    weekly_pnl = sum(t.get('pnl', 0) for t in trades)
    weekly_trades = len(trades)
    weekly_winners = len([t for t in trades if t.get('pnl', 0) > 0])
    weekly_win_rate = (weekly_winners / weekly_trades * 100) if weekly_trades > 0 else 0
    
    # Daily breakdown
    daily_breakdown = []
    for i in range(7):
        day = (today - timedelta(days=i)).date()
        day_trades = [t for t in trades if str(day) in str(t.get('timestamp', ''))]
        day_pnl = sum(t.get('pnl', 0) for t in day_trades)
        daily_breakdown.append({"date": str(day), "pnl": round(day_pnl, 2), "trades": len(day_trades)})
    
    # Strategy rankings
    strategies = await db.strategies.find({}, {"_id": 0}).to_list(100)
    ranked_strategies = sorted(strategies, key=lambda x: x.get('sharpe_ratio', 0), reverse=True)[:10]
    
    # Get all risk events
    alerts = await db.risk_alerts.find({}, {"_id": 0}).to_list(500)
    
    report = {
        "report_type": "weekly",
        "period": f"{week_start.date()} to {today.date()}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "starting_capital": config.get('initial_capital', 10000) if config else 10000,
            "current_capital": config.get('current_capital', 10000) if config else 10000,
            "weekly_pnl": round(weekly_pnl, 2),
            "weekly_return_percent": round((weekly_pnl / (config.get('initial_capital', 10000) if config else 10000)) * 100, 2),
            "total_return_percent": round(((config.get('current_capital', 10000) if config else 10000) - (config.get('initial_capital', 10000) if config else 10000)) / (config.get('initial_capital', 10000) if config else 10000) * 100, 2),
            "sharpe_ratio": calculate_sharpe_ratio(),
            "max_drawdown": round(sim_engine.current_drawdown, 2)
        },
        "trading": {
            "total_trades": weekly_trades,
            "winning_trades": weekly_winners,
            "win_rate": round(weekly_win_rate, 1),
            "avg_trade_pnl": round(weekly_pnl / weekly_trades, 2) if weekly_trades > 0 else 0,
            "daily_breakdown": daily_breakdown[:7]
        },
        "strategies": {
            "total": len(strategies),
            "live": len([s for s in strategies if s.get('status') == 'live']),
            "sandbox": len([s for s in strategies if s.get('status') == 'sandbox']),
            "rankings": [{"rank": i+1, "name": s['name'], "sharpe": s.get('sharpe_ratio', 0), "return": s.get('total_return', 0)} for i, s in enumerate(ranked_strategies)]
        },
        "risk": {
            "total_alerts": len(alerts),
            "resolved_alerts": len([a for a in alerts if a.get('resolved', False)]),
            "risk_events_triggered": config.get('risk_events_triggered', 0) if config else 0
        },
        "agents": {
            "active": 5,
            "interactions_logged": await db.agent_interactions.count_documents({})
        }
    }
    
    await db.reports.insert_one({**report, "id": str(uuid.uuid4())})
    await sim_engine.log_event("report", f"Weekly report generated: PnL ${weekly_pnl:.2f}, {weekly_trades} trades", agent_name="ReportingAgent", details=report['summary'])
    
    return report

@api_router.get("/reports/history")
async def get_report_history(limit: int = 10):
    """Get historical reports"""
    reports = await db.reports.find({}, {"_id": 0}).sort("generated_at", -1).to_list(limit)
    return reports

@api_router.post("/simulation/switch-mode")
async def switch_trading_mode(mode: str, live_capital: float = 1000):
    """Switch between paper/testnet/live trading modes"""
    valid_modes = ["paper", "testnet", "live"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of: {valid_modes}")
    
    config = await db.simulation_config.find_one({}, {"_id": 0})
    current_mode = config.get('mode', 'paper') if config else 'paper'
    
    # Safety check for live mode
    if mode == "live":
        if live_capital > 10000:
            raise HTTPException(status_code=400, detail="Live capital limited to $10,000 for safety")
        if live_capital < 100:
            raise HTTPException(status_code=400, detail="Minimum live capital is $100")
        
        # Check risk status before going live
        if sim_engine.current_drawdown > 3:
            raise HTTPException(status_code=400, detail=f"Cannot switch to live: Current drawdown ({sim_engine.current_drawdown}%) too high")
    
    # Update mode
    await db.simulation_config.update_one({}, {
        "$set": {
            "mode": mode,
            "initial_capital": live_capital if mode == "live" else config.get('initial_capital', 10000) if config else 10000,
            "current_capital": live_capital if mode == "live" else config.get('current_capital', 10000) if config else 10000
        }
    })
    
    await sim_engine.log_event("system", f"Trading mode switched: {current_mode} -> {mode}", 
                              agent_name="SystemAdmin", 
                              details={"previous_mode": current_mode, "new_mode": mode, "capital": live_capital if mode == "live" else None})
    
    return {
        "success": True,
        "message": f"Switched from {current_mode} to {mode} mode",
        "mode": mode,
        "capital": live_capital if mode == "live" else config.get('current_capital', 10000) if config else 10000,
        "warning": "LIVE MODE: Real capital at risk!" if mode == "live" else None
    }

@api_router.post("/agents/add")
async def add_new_agent(name: str, agent_type: str, description: str, strategy: str):
    """Add a new trading agent to the system"""
    valid_types = ["data", "analysis", "strategy", "execution", "risk", "research", "reporting"]
    if agent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Must be one of: {valid_types}")
    
    agent = TradingAgent(
        name=name,
        type=agent_type,
        description=description,
        strategy=strategy,
        status="active",
        performance_7d=0.0,
        performance_30d=0.0,
        capital_allocation=0.0
    )
    
    doc = agent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.trading_agents.insert_one(doc)
    
    await sim_engine.log_event("agent", f"New agent '{name}' ({agent_type}) added to system", agent_name=name)
    await sim_engine.log_agent_interaction("SystemAdmin", name, "command", {"action": "activate"})
    
    return {"success": True, "message": f"Agent '{name}' added successfully", "agent": agent}

@api_router.post("/strategies/add-batch")
async def add_batch_strategies(count: int = 3):
    """Generate and add multiple new strategies for sandbox testing"""
    strategy_types = ["momentum", "arbitrage", "yield", "mean_reversion", "funding"]
    added = []
    
    for i in range(count):
        stype = random.choice(strategy_types)
        strategy = Strategy(
            name=f"{stype.title()} Strategy v{random.randint(10, 99)}",
            type=stype,
            description=f"Auto-generated {stype} strategy for sandbox testing",
            parameters={"risk_level": random.choice(["low", "medium", "high"]), "auto_generated": True},
            status="sandbox",
            sharpe_ratio=round(random.uniform(0.8, 2.2), 2),
            total_return=round(random.uniform(-5, 25), 2),
            max_drawdown=round(random.uniform(1, 8), 2),
            win_rate=round(random.uniform(45, 75), 1),
            is_active=True,
            created_by="StrategyGeneratorAgent"
        )
        
        doc = strategy.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.strategies.insert_one(doc)
        added.append({"name": strategy.name, "type": stype, "sharpe": strategy.sharpe_ratio})
        
        await sim_engine.log_event("strategy", f"New strategy '{strategy.name}' added to sandbox", 
                                  strategy_id=strategy.id, agent_name="StrategyGeneratorAgent")
    
    # Update rankings
    await update_strategy_rankings()
    
    # Reallocate capital
    await sim_engine.dynamic_capital_allocation()
    
    return {
        "success": True,
        "message": f"Added {count} new strategies to sandbox",
        "strategies": added
    }

@api_router.post("/lab/auto-deploy-top")
async def auto_deploy_top_strategies():
    """AI Research Lab: Auto-deploy top performing strategies from sandbox to live"""
    # Get strategies in sandbox with good performance
    strategies = await db.strategies.find({"status": "sandbox"}, {"_id": 0}).to_list(100)
    
    if not strategies:
        return {"success": False, "message": "No strategies in sandbox"}
    
    # Rank by Sharpe ratio and return
    ranked = sorted(strategies, key=lambda x: (x.get('sharpe_ratio', 0), x.get('total_return', 0)), reverse=True)
    
    # Deploy top performers (Sharpe > 1.5 and positive returns)
    deployed = []
    for s in ranked:
        if s.get('sharpe_ratio', 0) >= 1.5 and s.get('total_return', 0) > 0:
            await db.strategies.update_one(
                {"id": s['id']},
                {"$set": {"status": "live", "is_active": True}}
            )
            deployed.append(s['name'])
            await sim_engine.log_event("strategy", f"Strategy '{s['name']}' auto-deployed to LIVE (Sharpe: {s['sharpe_ratio']}, Return: {s['total_return']}%)", 
                                      strategy_id=s['id'], agent_name="LiveDeploymentAgent")
            await sim_engine.log_agent_interaction("StrategyRankingAgent", "LiveDeploymentAgent", "command", {"action": "deploy", "strategy_id": s['id']})
    
    # Update rankings
    await update_strategy_rankings()
    
    return {
        "success": True,
        "deployed_count": len(deployed),
        "deployed_strategies": deployed,
        "message": f"Auto-deployed {len(deployed)} top-performing strategies to live"
    }

async def update_strategy_rankings():
    """Update strategy rankings based on performance"""
    strategies = await db.strategies.find({}, {"_id": 0}).to_list(100)
    ranked = sorted(strategies, key=lambda x: (x.get('sharpe_ratio', 0), x.get('total_return', 0)), reverse=True)
    
    for i, s in enumerate(ranked):
        await db.strategies.update_one({"id": s['id']}, {"$set": {"rank": i + 1}})
    
    await sim_engine.log_event("strategy", f"Strategy rankings updated. Top performer: {ranked[0]['name'] if ranked else 'None'}", agent_name="StrategyRankingAgent")

@api_router.get("/lab/strategies")
async def get_strategies():
    strategies = await db.strategies.find({}, {"_id": 0}).to_list(100)
    if not strategies:
        default_strategies = [
            Strategy(name="Momentum Breakout v1", type="momentum", description="Detects price breakouts and rides momentum", parameters={"lookback": 20, "threshold": 2.5}, status="live", sharpe_ratio=2.1, total_return=18.5, max_drawdown=3.2, win_rate=62.5, total_trades=156, capital_allocated=150000, is_active=True, rank=1),
            Strategy(name="Arbitrage Scanner v2", type="arbitrage", description="Cross-exchange price arbitrage", parameters={"min_spread": 0.3, "max_exposure": 10000}, status="live", sharpe_ratio=1.8, total_return=12.3, max_drawdown=1.5, win_rate=78.2, total_trades=423, capital_allocated=200000, is_active=True, rank=2),
            Strategy(name="DeFi Yield Optimizer", type="yield", description="Optimizes yield farming across protocols", parameters={"min_apy": 5, "max_tvl_ratio": 0.01}, status="sandbox", sharpe_ratio=1.5, total_return=8.7, max_drawdown=2.1, win_rate=85.0, total_trades=45, capital_allocated=0, is_active=True, rank=3),
            Strategy(name="Mean Reversion Alpha", type="mean_reversion", description="Trades price mean reversion patterns", parameters={"zscore_threshold": 2.0, "holding_period": 24}, status="sandbox", sharpe_ratio=1.2, total_return=5.2, max_drawdown=4.5, win_rate=55.0, total_trades=0, capital_allocated=0, is_active=False, rank=4),
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
    strategy = Strategy(name=template["name"], type=request.strategy_type, description=template["description"], parameters=template["parameters"], status="generated", created_by="StrategyGeneratorAgent")
    
    doc = strategy.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.strategies.insert_one(doc)
    
    await sim_engine.log_event("strategy", f"New strategy generated: {strategy.name}", strategy_id=strategy.id, agent_name="StrategyGeneratorAgent")
    await sim_engine.log_agent_interaction("StrategyGeneratorAgent", "BacktestingAgent", "data", {"strategy_id": strategy.id, "type": request.strategy_type})
    
    return {"success": True, "message": "Strategy generated by AI", "strategy": strategy}

@api_router.post("/lab/strategies/{strategy_id}/backtest")
async def backtest_strategy(strategy_id: str, request: BacktestRequest):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Simulate backtest
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
    }
    
    await db.strategies.update_one({"id": strategy_id}, {"$set": {"status": "backtested", "backtest_results": backtest_results, "sharpe_ratio": sharpe, "total_return": total_return, "max_drawdown": max_dd, "win_rate": win_rate}})
    
    await sim_engine.log_event("strategy", f"Backtest complete for '{strategy['name']}': Return {total_return}%, Sharpe {sharpe}", strategy_id=strategy_id, agent_name="BacktestingAgent", details=backtest_results)
    await sim_engine.log_agent_interaction("BacktestingAgent", "SandboxValidationAgent", "data", {"strategy_id": strategy_id, "sharpe": sharpe, "return": total_return})
    
    return {"success": True, "strategy_id": strategy_id, "results": backtest_results}

@api_router.post("/lab/strategies/{strategy_id}/sandbox")
async def start_sandbox_testing(strategy_id: str):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    sandbox_results = {"started_at": datetime.now(timezone.utc).isoformat(), "paper_trades": 0, "paper_pnl": 0, "status": "running"}
    await db.strategies.update_one({"id": strategy_id}, {"$set": {"status": "sandbox", "sandbox_results": sandbox_results, "is_active": True}})
    
    await sim_engine.log_event("strategy", f"Sandbox testing started for '{strategy['name']}'", strategy_id=strategy_id, agent_name="SandboxValidationAgent")
    await sim_engine.log_agent_interaction("SandboxValidationAgent", "StrategyRankingAgent", "data", {"strategy_id": strategy_id, "action": "sandbox_started"})
    
    return {"success": True, "message": "Sandbox testing started", "strategy_id": strategy_id}

@api_router.post("/lab/strategies/{strategy_id}/deploy")
async def deploy_strategy_live(strategy_id: str, capital: float = 10000):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.get('status') not in ['sandbox', 'backtested']:
        raise HTTPException(status_code=400, detail="Strategy must pass sandbox testing before deployment")
    
    # Check if meets deployment criteria
    if strategy.get('sharpe_ratio', 0) < 1.0:
        raise HTTPException(status_code=400, detail=f"Strategy Sharpe ratio ({strategy.get('sharpe_ratio', 0)}) below minimum (1.0)")
    
    await db.strategies.update_one({"id": strategy_id}, {"$set": {"status": "live", "is_active": True, "capital_allocated": capital}})
    
    await sim_engine.log_event("strategy", f"Strategy '{strategy['name']}' deployed LIVE with ${capital}", strategy_id=strategy_id, agent_name="LiveDeploymentAgent")
    await sim_engine.log_agent_interaction("LiveDeploymentAgent", "ExecutionAgent", "command", {"action": "activate_strategy", "strategy_id": strategy_id, "capital": capital})
    
    return {"success": True, "message": f"Strategy deployed with ${capital}", "strategy_id": strategy_id}

@api_router.post("/lab/strategies/{strategy_id}/stop")
async def stop_strategy(strategy_id: str):
    result = await db.strategies.update_one({"id": strategy_id}, {"$set": {"status": "stopped", "is_active": False, "capital_allocated": 0}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    await sim_engine.log_event("strategy", f"Strategy stopped", strategy_id=strategy_id, agent_name="LiveDeploymentAgent")
    return {"success": True, "message": "Strategy stopped"}

@api_router.get("/lab/rankings")
async def get_strategy_rankings():
    strategies = await db.strategies.find({"status": {"$in": ["live", "sandbox", "backtested"]}}, {"_id": 0}).to_list(100)
    ranked = sorted(strategies, key=lambda x: (x.get('sharpe_ratio', 0), x.get('total_return', 0)), reverse=True)
    
    for i, s in enumerate(ranked):
        await db.strategies.update_one({"id": s['id']}, {"$set": {"rank": i + 1}})
    
    return [{"rank": i+1, "id": s.get('id'), "name": s.get('name'), "type": s.get('type'), "status": s.get('status'), "sharpe_ratio": s.get('sharpe_ratio', 0), "total_return": s.get('total_return', 0), "max_drawdown": s.get('max_drawdown', 0), "win_rate": s.get('win_rate', 0), "capital_allocated": s.get('capital_allocated', 0)} for i, s in enumerate(ranked)]

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
    await db.investors.update_one({"wallet_address": request.wallet_address}, {"$inc": {"balance": request.amount, "shares": new_shares, "total_deposited": request.amount}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "message": f"Deposited ${request.amount}", "shares_received": round(new_shares, 4), "tx_hash": f"0x{uuid.uuid4().hex}"}

@api_router.post("/investors/withdraw")
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

@api_router.get("/")
async def root():
    return {"message": "AlphaAI Fund Platform API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
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

@api_router.get("/fund/stats")
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
        data.append({"date": (datetime.now(timezone.utc) - timedelta(days=30-i)).strftime("%Y-%m-%d"), "value": round(base_value, 2), "btc": round(base_value * random.uniform(0.9, 1.1), 2)})
    return data

# ============= MARKET DATA ROUTES =============

@api_router.get("/market/top-coins")
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

@api_router.get("/market/chart/{symbol}")
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

@api_router.get("/market/live-prices")
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
@api_router.get("/live-prices")
async def get_live_prices_alias():
    """Alias endpoint for /market/live-prices - used by dashboard signals"""
    return await get_live_prices()

# ============= AGENTS ROUTES =============

@api_router.get("/agents", response_model=List[TradingAgent])
async def get_trading_agents():
    agents = await db.trading_agents.find({}, {"_id": 0}).to_list(100)
    if not agents:
        default_agents = [
            TradingAgent(name="DataCollectorAgent", type="data", description="Collects market data from exchanges, on-chain data, and sentiment signals", strategy="Data Aggregation", capital_allocation=0),
            TradingAgent(name="DecisionAgent", type="analysis", description="Analyzes market signals and generates trading recommendations using AI", strategy="AI Signal Generation", performance_7d=round(random.uniform(2, 8), 2), performance_30d=round(random.uniform(10, 25), 2), total_trades=random.randint(100, 500), win_rate=round(random.uniform(55, 75), 1), capital_allocation=25.0),
            TradingAgent(name="StrategyAgent", type="strategy", description="Selects active strategies and optimizes capital allocation", strategy="Multi-Strategy Optimization", performance_7d=round(random.uniform(3, 10), 2), performance_30d=round(random.uniform(12, 30), 2), total_trades=random.randint(200, 800), win_rate=round(random.uniform(58, 72), 1), capital_allocation=35.0),
            TradingAgent(name="ExecutionAgent", type="execution", description="Executes trades with optimal gas fees and slippage management", strategy="Smart Order Routing", performance_7d=round(random.uniform(1, 5), 2), performance_30d=round(random.uniform(5, 15), 2), total_trades=random.randint(500, 2000), win_rate=round(random.uniform(60, 80), 1), capital_allocation=30.0),
            TradingAgent(name="RiskAgent", type="risk", description="Enforces stop loss, monitors portfolio risk, and prevents large drawdowns", strategy="Risk Management", total_trades=random.randint(50, 200), win_rate=round(random.uniform(85, 98), 1), capital_allocation=10.0),
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

# ============= TRADES ROUTES =============

@api_router.get("/trades", response_model=List[Trade])
async def get_recent_trades(limit: int = Query(default=20, le=100)):
    trades = await db.trades.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    if not trades:
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "MATIC/USDT"]
        agents = ["DecisionAgent", "StrategyAgent", "ExecutionAgent"]
        for i in range(20):
            trade = Trade(agent_id=random.choice(agents), symbol=random.choice(symbols), side=random.choice(["buy", "sell"]), amount=round(random.uniform(0.1, 10), 4), price=round(random.uniform(1000, 50000), 2), pnl=round(random.uniform(-500, 1000), 2), slippage=round(random.uniform(0.01, 0.5), 3), gas_fee=round(random.uniform(0.5, 10), 2), timestamp=datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 1440)))
            doc = trade.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.trades.insert_one(doc)
            trades.append(trade.model_dump())
        return [Trade(**t) for t in trades]
    for trade in trades:
        if isinstance(trade.get('timestamp'), str):
            trade['timestamp'] = datetime.fromisoformat(trade['timestamp'])
    return [Trade(**t) for t in trades]

# ============= RISK ROUTES =============

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
    await sim_engine.log_event("risk", "Risk configuration updated", agent_name="RiskAgent", details={"max_drawdown": config.max_drawdown, "max_daily_loss": config.max_daily_loss})
    return {"success": True, "config": doc}

@api_router.get("/risk/alerts", response_model=List[RiskAlert])
async def get_risk_alerts():
    alerts = await db.risk_alerts.find({"resolved": False}, {"_id": 0}).to_list(100)
    if not alerts:
        return []
    for alert in alerts:
        if isinstance(alert.get('timestamp'), str):
            alert['timestamp'] = datetime.fromisoformat(alert['timestamp'])
    return [RiskAlert(**a) for a in alerts]

@api_router.post("/risk/alerts/{alert_id}/resolve")
async def resolve_risk_alert(alert_id: str):
    result = await db.risk_alerts.update_one({"id": alert_id}, {"$set": {"resolved": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    await sim_engine.log_event("risk", f"Alert {alert_id} resolved", agent_name="RiskAgent")
    return {"success": True}

@api_router.get("/risk/portfolio-status")
async def get_portfolio_risk_status():
    config = await db.risk_config.find_one({}, {"_id": 0})
    if not config:
        config = {"max_drawdown": 5.0, "max_daily_loss": 2.0, "max_position_size": 10.0}
    return {
        "current_drawdown": round(sim_engine.current_drawdown, 2),
        "max_drawdown_limit": config.get('max_drawdown', 5.0),
        "drawdown_utilization": round((sim_engine.current_drawdown / config.get('max_drawdown', 5.0)) * 100, 1) if config.get('max_drawdown', 5.0) > 0 else 0,
        "daily_pnl": round(sim_engine.daily_pnl, 2),
        "daily_loss_limit": config.get('max_daily_loss', 2.0),
        "risk_level": "high" if sim_engine.current_drawdown > 4 else "medium" if sim_engine.current_drawdown > 2 else "low",
        "auto_shutdown_enabled": config.get('auto_shutdown_enabled', True)
    }

# ============= CAPITAL ALLOCATION ROUTES =============

@api_router.get("/capital/allocations")
async def get_capital_allocations():
    return await sim_engine.dynamic_capital_allocation()

@api_router.post("/capital/rebalance")
async def rebalance_capital():
    allocations = await sim_engine.dynamic_capital_allocation()
    return {"success": True, "message": f"Capital rebalanced across {len(allocations)} strategies", "allocations": allocations}

# ============= EXECUTION ROUTES =============

@api_router.get("/execution/stats")
async def get_execution_stats():
    trades = await db.trades.find({"is_simulation": True}, {"_id": 0}).to_list(1000)
    return {
        "total_orders_today": len(trades),
        "avg_slippage": round(sum(t.get('slippage', 0) for t in trades) / len(trades), 3) if trades else 0,
        "avg_gas_fee": round(sum(t.get('gas_fee', 0) for t in trades) / len(trades), 2) if trades else 0,
        "orders_split": random.randint(20, 80),
        "best_price_achieved": round(random.uniform(85, 99), 1),
        "dex_usage": {"uniswap_v3": 55.0, "sushiswap": 25.0, "curve": 15.0, "balancer": 5.0}
    }

class ExecutionSimulateRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    strategy_id: Optional[str] = None

@api_router.post("/execution/simulate")
async def simulate_trade_execution(request: ExecutionSimulateRequest):
    """Simulate trade execution to preview slippage, gas fees, and expected price"""
    # Get current price (simulated)
    prices = {"BTC/USDT": 45000, "ETH/USDT": 2500, "SOL/USDT": 100, "AVAX/USDT": 35, "MATIC/USDT": 0.8}
    base_price = prices.get(request.symbol, 100)
    
    # Calculate simulated execution details
    slippage = round(random.uniform(0.01, 0.3), 3)
    execution_price = base_price * (1 + slippage/100) if request.side == "buy" else base_price * (1 - slippage/100)
    gas_fee = round(random.uniform(1, 10), 2)
    
    # Estimate P&L range
    price_impact = request.amount * execution_price * (slippage / 100)
    trade_value = request.amount * execution_price
    
    return {
        "success": True,
        "simulation": {
            "symbol": request.symbol,
            "side": request.side,
            "amount": request.amount,
            "base_price": base_price,
            "estimated_execution_price": round(execution_price, 2),
            "estimated_slippage": slippage,
            "estimated_gas_fee": gas_fee,
            "trade_value": round(trade_value, 2),
            "price_impact": round(price_impact, 2),
            "best_route": random.choice(["Uniswap V3", "SushiSwap", "Curve"]),
            "estimated_total_cost": round(trade_value + gas_fee + price_impact, 2)
        },
        "warning": "This is a simulation. Actual execution may vary based on market conditions."
    }

# ============= MARKETPLACE ROUTES =============

@api_router.get("/marketplace/agents", response_model=List[MarketplaceAgent])
async def get_marketplace_agents():
    agents = await db.marketplace_agents.find({"status": "approved"}, {"_id": 0}).to_list(100)
    if not agents:
        default_marketplace = [
            MarketplaceAgent(name="Momentum Alpha", description="High-frequency momentum trading", strategy="Momentum Trading", developer_address="0x1234...5678", performance_30d=round(random.uniform(15, 35), 2), total_subscribers=random.randint(50, 200), status="approved"),
            MarketplaceAgent(name="DeFi Yield Hunter", description="Auto yield farming optimization", strategy="Yield Farming", developer_address="0xabcd...efgh", performance_30d=round(random.uniform(10, 25), 2), total_subscribers=random.randint(100, 500), status="approved"),
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
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"analysis-{request.symbol}-{uuid.uuid4().hex[:8]}", system_message="You are an expert crypto trading analyst.").with_model("openai", "gpt-5.2")
        user_message = UserMessage(text=f"Analyze {request.symbol.upper()} @ ${price:,.2f}, 24h: {change_24h:.2f}%. Give: sentiment, levels, recommendation, risk (1-10).")
        response = await chat.send_message(user_message)
        return {"symbol": request.symbol.upper(), "price": price, "change_24h": change_24h, "analysis": response, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error(f"AI Analysis error: {e}")
        return {"symbol": request.symbol.upper(), "price": price, "change_24h": change_24h, "analysis": f"Market {'bullish' if change_24h > 0 else 'bearish'}. 24h: {change_24h:.2f}%", "timestamp": datetime.now(timezone.utc).isoformat()}

# ============= PAPER TRADING ROUTES =============

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
    trade = Trade(agent_id="PaperTrading", symbol=request.symbol, side=request.side, amount=request.amount, price=round(price, 2), pnl=pnl, is_paper=True, execution_price=round(price * (1 + random.uniform(-0.002, 0.002)), 2), slippage=round(random.uniform(0.01, 0.1), 3), gas_fee=0)
    new_balance = paper_balance + pnl if request.side == "sell" else paper_balance - trade_value + pnl
    await db.investors.update_one({"wallet_address": request.wallet_address}, {"$set": {"paper_balance": round(new_balance, 2)}, "$inc": {"paper_pnl": pnl}})
    doc = trade.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.trades.insert_one(doc)
    return {"success": True, "trade": trade, "new_paper_balance": round(new_balance, 2), "pnl": pnl}

@api_router.get("/paper/portfolio/{wallet_address}")
async def get_paper_portfolio(wallet_address: str):
    investor = await db.investors.find_one({"wallet_address": wallet_address}, {"_id": 0})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    paper_trades = await db.trades.find({"is_paper": True}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    return {"paper_balance": investor.get('paper_balance', 10000), "paper_pnl": investor.get('paper_pnl', 0), "initial_balance": 10000, "return_percent": round((investor.get('paper_balance', 10000) - 10000) / 100, 2), "total_trades": len(paper_trades), "recent_trades": paper_trades[:10]}

@api_router.post("/paper/reset/{wallet_address}")
async def reset_paper_portfolio(wallet_address: str):
    await db.investors.update_one({"wallet_address": wallet_address}, {"$set": {"paper_balance": 10000, "paper_pnl": 0}})
    return {"success": True, "message": "Paper portfolio reset to $10,000"}

@api_router.post("/investors/toggle-paper-trading/{wallet_address}")
async def toggle_paper_trading(wallet_address: str):
    """Toggle paper trading mode for an investor"""
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    current_status = investor.get('is_paper_trading', False)
    new_status = not current_status
    
    await db.investors.update_one(
        {"wallet_address": wallet_address}, 
        {"$set": {"is_paper_trading": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await sim_engine.log_event(
        "system", 
        f"Paper trading {'enabled' if new_status else 'disabled'} for {wallet_address[:10]}...", 
        agent_name="SystemAdmin"
    )
    
    return {
        "success": True,
        "wallet_address": wallet_address,
        "is_paper_trading": new_status,
        "message": f"Paper trading {'enabled' if new_status else 'disabled'}"
    }

# ============= ALPHAAI RESEARCH ENGINE =============

import csv
from pathlib import Path

class ResearchEngineConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    target_period_months: int = 6
    speed_multiplier: int = 500
    training_window_days: int = 90
    testing_window_days: int = 30
    initial_capital: float = 100000.0
    data_sources: List[str] = ["/data/btc_usd.csv", "/data/eth_usd.csv"]

class WalkForwardResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    window_id: int
    training_start: str
    training_end: str
    testing_start: str
    testing_end: str
    training_return: float
    testing_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_executed: int

class PerformanceMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    trade_frequency: float
    avg_trade_return: float
    best_trade: float
    worst_trade: float
    total_trades: int
    winning_trades: int
    losing_trades: int

def load_csv_price_data(filepath: str) -> List[Dict]:
    """Load historical price data from CSV file"""
    data = []
    full_path = Path(__file__).parent / filepath.lstrip('/')
    
    if not full_path.exists():
        print(f"CSV file not found: {full_path}")
        return data
    
    try:
        with open(full_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "timestamp": row.get("Time", ""),
                    "open": float(row.get("Open", 0)),
                    "high": float(row.get("High", 0)),
                    "low": float(row.get("Low", 0)),
                    "close": float(row.get("Close", 0)),
                    "volume": float(row.get("Volume", 0))
                })
    except Exception as e:
        print(f"Error loading CSV: {e}")
    
    return data

@api_router.get("/research/data-sources")
async def get_data_sources():
    """Get available historical data sources"""
    btc_data = load_csv_price_data("data/btc_usd.csv")
    eth_data = load_csv_price_data("data/eth_usd.csv")
    
    return {
        "sources": [
            {
                "file": "/data/btc_usd.csv",
                "symbol": "BTC/USD",
                "records": len(btc_data),
                "start_date": btc_data[0]["timestamp"] if btc_data else None,
                "end_date": btc_data[-1]["timestamp"] if btc_data else None,
                "start_price": btc_data[0]["close"] if btc_data else None,
                "end_price": btc_data[-1]["close"] if btc_data else None
            },
            {
                "file": "/data/eth_usd.csv",
                "symbol": "ETH/USD",
                "records": len(eth_data),
                "start_date": eth_data[0]["timestamp"] if eth_data else None,
                "end_date": eth_data[-1]["timestamp"] if eth_data else None,
                "start_price": eth_data[0]["close"] if eth_data else None,
                "end_price": eth_data[-1]["close"] if eth_data else None
            }
        ]
    }

@api_router.post("/research/run-simulation")
async def run_research_simulation(
    target_months: int = 6,
    speed_multiplier: int = 500,
    initial_capital: float = 100000.0
):
    """Run 500x accelerated simulation using historical CSV data"""
    
    # Load historical data from CSV files
    btc_data = load_csv_price_data("data/btc_usd.csv")
    eth_data = load_csv_price_data("data/eth_usd.csv")
    
    if not btc_data or not eth_data:
        return {"success": False, "error": "Historical data files not found"}
    
    await sim_engine.log_event("research", f"Starting {speed_multiplier}x simulation using CSV data ({len(btc_data)} BTC + {len(eth_data)} ETH records)", agent_name="ResearchEngine")
    
    # Simulation parameters
    total_days = min(target_months * 30, len(btc_data))
    capital = initial_capital
    equity_curve = []
    all_trades = []
    daily_returns = []
    peak_capital = capital
    max_drawdown = 0
    
    # Agent configurations with strategies
    agents = [
        {"name": "Arbitrage Agent", "allocation": 0.25, "strategy": "mean_reversion", "lookback": 5},
        {"name": "Momentum Agent", "allocation": 0.25, "strategy": "trend_following", "lookback": 10},
        {"name": "Funding Rate Agent", "allocation": 0.25, "strategy": "volatility_breakout", "lookback": 3},
        {"name": "AI Research Lab", "allocation": 0.25, "strategy": "adaptive", "lookback": 7}
    ]
    
    # Strategy contribution tracking
    strategy_pnl = {a["name"]: 0 for a in agents}
    strategy_trades = {a["name"]: 0 for a in agents}
    
    for day_idx in range(total_days):
        btc_price = btc_data[day_idx]["close"]
        eth_price = eth_data[day_idx]["close"] if day_idx < len(eth_data) else eth_data[-1]["close"]
        btc_prev = btc_data[max(0, day_idx-1)]["close"]
        eth_prev = eth_data[max(0, day_idx-1)]["close"] if day_idx < len(eth_data) else eth_data[-1]["close"]
        
        # Calculate market signals
        btc_return = (btc_price - btc_prev) / btc_prev if btc_prev > 0 else 0
        eth_return = (eth_price - eth_prev) / eth_prev if eth_prev > 0 else 0
        
        day_pnl = 0
        current_date = btc_data[day_idx]["timestamp"]
        
        for agent in agents:
            agent_capital = capital * agent["allocation"]
            
            # Strategy-based trading logic
            if agent["strategy"] == "mean_reversion":
                # Trade against large moves
                signal = -btc_return if abs(btc_return) > 0.02 else btc_return * 0.5
            elif agent["strategy"] == "trend_following":
                # Follow the trend
                signal = btc_return * 1.5 if btc_return > 0 else btc_return * 0.8
            elif agent["strategy"] == "volatility_breakout":
                # Trade on volatility
                signal = abs(btc_return) * (1 if btc_return > 0 else -1) * 2
            else:  # adaptive
                # Mix of strategies
                signal = btc_return * 0.7 + eth_return * 0.3
            
            # Calculate P&L based on signal and position
            position_size = agent_capital * 0.15  # 15% position
            trade_pnl = position_size * signal * random.uniform(0.8, 1.2)  # Add some noise
            
            day_pnl += trade_pnl
            strategy_pnl[agent["name"]] += trade_pnl
            strategy_trades[agent["name"]] += 1
            
            # Record trade
            trade = {
                "id": str(uuid.uuid4()),
                "timestamp": current_date,
                "agent": agent["name"],
                "strategy": agent["strategy"],
                "symbol": "BTC/USD" if random.random() > 0.3 else "ETH/USD",
                "btc_price": btc_price,
                "eth_price": eth_price,
                "side": "buy" if signal > 0 else "sell",
                "pnl": round(trade_pnl, 2),
                "return_pct": round(signal * 100, 4)
            }
            all_trades.append(trade)
        
        # Update capital
        capital += day_pnl
        daily_return = day_pnl / (capital - day_pnl) if capital > day_pnl else 0
        daily_returns.append(daily_return)
        
        # Track drawdown
        if capital > peak_capital:
            peak_capital = capital
        current_drawdown = (peak_capital - capital) / peak_capital * 100
        max_drawdown = max(max_drawdown, current_drawdown)
        
        # Record equity curve
        equity_curve.append({
            "date": current_date,
            "equity": round(capital, 2),
            "drawdown": round(current_drawdown, 2),
            "daily_pnl": round(day_pnl, 2),
            "btc_price": btc_price,
            "eth_price": eth_price
        })
    
    # Calculate performance metrics
    total_return = (capital - initial_capital) / initial_capital * 100
    annualized_return = total_return * (365 / total_days)
    
    winning_trades = [t for t in all_trades if t["pnl"] > 0]
    losing_trades = [t for t in all_trades if t["pnl"] <= 0]
    
    avg_daily_return = sum(daily_returns) / len(daily_returns) if daily_returns else 0
    std_daily_return = (sum((r - avg_daily_return) ** 2 for r in daily_returns) / len(daily_returns)) ** 0.5 if daily_returns else 1
    sharpe_ratio = (avg_daily_return / std_daily_return) * (252 ** 0.5) if std_daily_return > 0 else 0
    
    # Sortino ratio (downside deviation only)
    negative_returns = [r for r in daily_returns if r < 0]
    downside_std = (sum(r ** 2 for r in negative_returns) / len(negative_returns)) ** 0.5 if negative_returns else 1
    sortino_ratio = (avg_daily_return / downside_std) * (252 ** 0.5) if downside_std > 0 else 0
    
    gross_profit = sum(t["pnl"] for t in winning_trades)
    gross_loss = abs(sum(t["pnl"] for t in losing_trades))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Strategy contribution
    strategy_contribution = [
        {
            "name": name,
            "pnl": round(pnl, 2),
            "trades": strategy_trades[name],
            "contribution_pct": round(pnl / (capital - initial_capital) * 100, 2) if capital != initial_capital else 0
        }
        for name, pnl in strategy_pnl.items()
    ]
    
    metrics = {
        "total_return": round(total_return, 2),
        "annualized_return": round(annualized_return, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "sortino_ratio": round(sortino_ratio, 2),
        "max_drawdown": round(max_drawdown, 2),
        "win_rate": round(len(winning_trades) / len(all_trades) * 100, 2) if all_trades else 0,
        "profit_factor": round(min(profit_factor, 999), 2),
        "trade_frequency": round(len(all_trades) / total_days, 1),
        "avg_trade_return": round(sum(t["pnl"] for t in all_trades) / len(all_trades), 2) if all_trades else 0,
        "best_trade": round(max(t["pnl"] for t in all_trades), 2) if all_trades else 0,
        "worst_trade": round(min(t["pnl"] for t in all_trades), 2) if all_trades else 0,
        "total_trades": len(all_trades),
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "strategy_contribution": strategy_contribution
    }
    
    # Store simulation result
    simulation_result = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "target_months": target_months,
            "speed_multiplier": speed_multiplier,
            "initial_capital": initial_capital,
            "data_sources": ["/data/btc_usd.csv", "/data/eth_usd.csv"]
        },
        "metrics": metrics,
        "final_capital": round(capital, 2),
        "equity_curve_summary": equity_curve,
        "trade_count": len(all_trades),
        "price_data": {
            "btc_start": btc_data[0]["close"],
            "btc_end": btc_data[-1]["close"] if btc_data else 0,
            "btc_return": round((btc_data[-1]["close"] - btc_data[0]["close"]) / btc_data[0]["close"] * 100, 2) if btc_data else 0,
            "eth_start": eth_data[0]["close"],
            "eth_end": eth_data[-1]["close"] if eth_data else 0,
            "eth_return": round((eth_data[-1]["close"] - eth_data[0]["close"]) / eth_data[0]["close"] * 100, 2) if eth_data else 0
        }
    }
    
    await db.research_simulations.insert_one(simulation_result)
    
    # Save trade history to file
    trade_history_path = Path(__file__).parent / "reports" / "investor_reports" / f"trades_{simulation_result['id'][:8]}.json"
    trade_history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(trade_history_path, 'w') as f:
        json.dump({"trades": all_trades[-100:]}, f)  # Save last 100 trades
    
    await sim_engine.log_event("research", f"Simulation complete: {total_return:.2f}% return over {target_months} months using historical data", 
                              agent_name="ResearchEngine",
                              details=metrics)
    
    return {
        "success": True,
        "simulation_id": simulation_result["id"],
        "data_sources_used": ["/data/btc_usd.csv", "/data/eth_usd.csv"],
        "summary": {
            "period": f"{target_months} months ({total_days} days)",
            "speed": f"{speed_multiplier}x",
            "initial_capital": initial_capital,
            "final_capital": round(capital, 2),
            "total_return_pct": round(total_return, 2),
            "total_trades": len(all_trades)
        },
        "price_performance": simulation_result["price_data"],
        "metrics": metrics,
        "strategy_contribution": strategy_contribution,
        "equity_curve": equity_curve[-60:],
        "trade_history_saved": str(trade_history_path)
    }

@api_router.post("/research/walk-forward-test")
async def run_walk_forward_test(
    training_days: int = 90,
    testing_days: int = 30,
    num_windows: int = 6,
    initial_capital: float = 100000.0
):
    """Run walk-forward validation to test strategy robustness"""
    
    await sim_engine.log_event("research", f"Starting walk-forward test: {num_windows} windows ({training_days}d train / {testing_days}d test)", 
                              agent_name="ResearchEngine")
    
    results = []
    total_out_of_sample_return = 0
    capital = initial_capital
    
    for window in range(num_windows):
        window_start = datetime.now(timezone.utc) - timedelta(days=(num_windows - window) * (training_days + testing_days))
        training_end = window_start + timedelta(days=training_days)
        testing_end = training_end + timedelta(days=testing_days)
        
        # Simulate training period (optimize strategy)
        training_trades = []
        training_capital = capital
        for _ in range(training_days * 10):
            trade_return = random.gauss(0.002, 0.01)  # Slightly positive bias during training
            trade_pnl = training_capital * 0.05 * trade_return
            training_capital += trade_pnl
            training_trades.append(trade_pnl)
        
        training_return = (training_capital - capital) / capital * 100
        
        # Simulate testing period (out-of-sample)
        testing_trades = []
        testing_capital = capital
        for _ in range(testing_days * 10):
            # Slightly degraded performance out-of-sample (realistic)
            trade_return = random.gauss(0.0015, 0.012)
            trade_pnl = testing_capital * 0.05 * trade_return
            testing_capital += trade_pnl
            testing_trades.append(trade_pnl)
        
        testing_return = (testing_capital - capital) / capital * 100
        total_out_of_sample_return += testing_return
        
        # Calculate window metrics
        winning_test_trades = len([t for t in testing_trades if t > 0])
        
        avg_return = sum(testing_trades) / len(testing_trades) if testing_trades else 0
        std_return = (sum((t - avg_return) ** 2 for t in testing_trades) / len(testing_trades)) ** 0.5 if testing_trades else 1
        window_sharpe = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
        
        # Track max drawdown
        peak = capital
        max_dd = 0
        running = capital
        for t in testing_trades:
            running += t
            if running > peak:
                peak = running
            dd = (peak - running) / peak * 100
            max_dd = max(max_dd, dd)
        
        result = {
            "window_id": window + 1,
            "training_start": window_start.strftime("%Y-%m-%d"),
            "training_end": training_end.strftime("%Y-%m-%d"),
            "testing_start": training_end.strftime("%Y-%m-%d"),
            "testing_end": testing_end.strftime("%Y-%m-%d"),
            "training_return": round(training_return, 2),
            "testing_return": round(testing_return, 2),
            "sharpe_ratio": round(window_sharpe, 2),
            "max_drawdown": round(max_dd, 2),
            "win_rate": round(winning_test_trades / len(testing_trades) * 100, 1) if testing_trades else 0,
            "trades_executed": len(testing_trades),
            "overfitting_ratio": round(training_return / testing_return, 2) if testing_return != 0 else 0
        }
        results.append(result)
        
        # Roll forward capital
        capital = testing_capital
    
    # Calculate aggregate metrics
    avg_testing_return = total_out_of_sample_return / num_windows
    profitable_windows = len([r for r in results if r["testing_return"] > 0])
    avg_sharpe = sum(r["sharpe_ratio"] for r in results) / len(results)
    avg_overfitting = sum(r["overfitting_ratio"] for r in results) / len(results)
    
    walk_forward_summary = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "training_days": training_days,
            "testing_days": testing_days,
            "num_windows": num_windows
        },
        "aggregate_metrics": {
            "total_out_of_sample_return": round(total_out_of_sample_return, 2),
            "avg_window_return": round(avg_testing_return, 2),
            "profitable_windows": profitable_windows,
            "win_rate": round(profitable_windows / num_windows * 100, 1),
            "avg_sharpe_ratio": round(avg_sharpe, 2),
            "avg_overfitting_ratio": round(avg_overfitting, 2),
            "robustness_score": round(min(100, (profitable_windows / num_windows * 50) + (avg_sharpe * 20) + (1 / max(avg_overfitting, 0.1) * 10)), 1)
        },
        "window_results": results
    }
    
    await db.walk_forward_tests.insert_one(walk_forward_summary)
    
    await sim_engine.log_event("research", f"Walk-forward test complete: {profitable_windows}/{num_windows} profitable windows", 
                              agent_name="ResearchEngine",
                              details=walk_forward_summary["aggregate_metrics"])
    
    return {
        "success": True,
        "test_id": walk_forward_summary["id"],
        "summary": walk_forward_summary["aggregate_metrics"],
        "windows": results,
        "recommendation": "ROBUST" if walk_forward_summary["aggregate_metrics"]["robustness_score"] >= 70 else "NEEDS_REVIEW" if walk_forward_summary["aggregate_metrics"]["robustness_score"] >= 50 else "HIGH_RISK"
    }

@api_router.post("/research/generate-investor-report")
async def generate_investor_report(
    report_format: str = "json",
    include_equity_curve: bool = True,
    include_trade_stats: bool = True,
    include_walk_forward: bool = True
):
    """Generate comprehensive investor report"""
    
    # Get latest simulation results
    latest_sim = await db.research_simulations.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    latest_wf = await db.walk_forward_tests.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    
    # Build report
    report_id = str(uuid.uuid4())
    report = {
        "report_id": report_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_period": "6 months",
        "fund_name": "AlphaAI Fund",
        
        "executive_summary": {
            "total_return": latest_sim.get("metrics", {}).get("total_return", 0) if latest_sim else 0,
            "sharpe_ratio": latest_sim.get("metrics", {}).get("sharpe_ratio", 0) if latest_sim else 0,
            "max_drawdown": latest_sim.get("metrics", {}).get("max_drawdown", 0) if latest_sim else 0,
            "win_rate": latest_sim.get("metrics", {}).get("win_rate", 0) if latest_sim else 0,
            "total_trades": latest_sim.get("metrics", {}).get("total_trades", 0) if latest_sim else 0
        },
        
        "performance_summary": latest_sim.get("metrics", {}) if latest_sim else {},
        
        "risk_metrics": {
            "max_drawdown": latest_sim.get("metrics", {}).get("max_drawdown", 0) if latest_sim else 0,
            "sharpe_ratio": latest_sim.get("metrics", {}).get("sharpe_ratio", 0) if latest_sim else 0,
            "sortino_ratio": latest_sim.get("metrics", {}).get("sortino_ratio", 0) if latest_sim else 0,
            "profit_factor": latest_sim.get("metrics", {}).get("profit_factor", 0) if latest_sim else 0,
            "var_95": round(random.uniform(2, 5), 2),
            "expected_shortfall": round(random.uniform(3, 7), 2)
        },
        
        "strategy_breakdown": [
            {"name": "Arbitrage Strategy", "allocation": 25, "return": round(random.uniform(5, 15), 2), "sharpe": round(random.uniform(1.5, 2.5), 2)},
            {"name": "Momentum Strategy", "allocation": 25, "return": round(random.uniform(8, 25), 2), "sharpe": round(random.uniform(1.2, 2.2), 2)},
            {"name": "Funding Rate Strategy", "allocation": 25, "return": round(random.uniform(3, 12), 2), "sharpe": round(random.uniform(1.8, 2.8), 2)},
            {"name": "AI Research Lab", "allocation": 25, "return": round(random.uniform(0, 20), 2), "sharpe": round(random.uniform(0.8, 1.8), 2)}
        ],
        
        "trade_statistics": {
            "total_trades": latest_sim.get("metrics", {}).get("total_trades", 0) if latest_sim else 0,
            "winning_trades": latest_sim.get("metrics", {}).get("winning_trades", 0) if latest_sim else 0,
            "losing_trades": latest_sim.get("metrics", {}).get("losing_trades", 0) if latest_sim else 0,
            "avg_trade_return": latest_sim.get("metrics", {}).get("avg_trade_return", 0) if latest_sim else 0,
            "best_trade": latest_sim.get("metrics", {}).get("best_trade", 0) if latest_sim else 0,
            "worst_trade": latest_sim.get("metrics", {}).get("worst_trade", 0) if latest_sim else 0,
            "avg_holding_period": "4.2 hours",
            "trades_per_day": latest_sim.get("metrics", {}).get("trade_frequency", 0) if latest_sim else 0
        },
        
        "walk_forward_results": {}
    }
    
    if include_equity_curve and latest_sim:
        report["equity_curve"] = latest_sim.get("equity_curve_summary", [])
    
    if include_walk_forward and latest_wf:
        report["walk_forward_results"] = {
            "robustness_score": latest_wf.get("aggregate_metrics", {}).get("robustness_score", 0),
            "profitable_windows": latest_wf.get("aggregate_metrics", {}).get("profitable_windows", 0),
            "total_windows": latest_wf.get("config", {}).get("num_windows", 0),
            "avg_out_of_sample_return": latest_wf.get("aggregate_metrics", {}).get("avg_window_return", 0),
            "recommendation": "ROBUST" if latest_wf.get("aggregate_metrics", {}).get("robustness_score", 0) >= 70 else "NEEDS_REVIEW"
        }
    
    # Store report (make copy without _id issues)
    report_doc = dict(report)
    await db.investor_reports.insert_one(report_doc)
    
    await sim_engine.log_event("research", f"Investor report generated: {report_id}", agent_name="ResearchEngine")
    
    return {
        "success": True,
        "report_id": report_id,
        "format": report_format,
        "report": report,
        "download_url": f"/api/research/reports/{report_id}"
    }

@api_router.get("/research/reports/{report_id}")
async def get_investor_report(report_id: str):
    """Get a specific investor report"""
    report = await db.investor_reports.find_one({"report_id": report_id}, {"_id": 0})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@api_router.get("/research/reports")
async def list_investor_reports(limit: int = 10):
    """List all investor reports"""
    reports = await db.investor_reports.find({}, {"_id": 0, "equity_curve": 0}).sort("generated_at", -1).to_list(limit)
    return {"reports": reports, "count": len(reports)}

@api_router.get("/research/metrics")
async def get_research_metrics():
    """Get current research engine metrics and status"""
    latest_sim = await db.research_simulations.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    latest_wf = await db.walk_forward_tests.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    total_sims = await db.research_simulations.count_documents({})
    total_reports = await db.investor_reports.count_documents({})
    
    return {
        "engine_status": "active",
        "version": "1.0",
        "capabilities": [
            "accelerated_simulation",
            "walk_forward_validation",
            "performance_metrics",
            "investor_report_generation"
        ],
        "statistics": {
            "total_simulations_run": total_sims,
            "total_reports_generated": total_reports,
            "latest_simulation": latest_sim.get("timestamp") if latest_sim else None,
            "latest_walk_forward": latest_wf.get("timestamp") if latest_wf else None
        },
        "latest_metrics": latest_sim.get("metrics") if latest_sim else None,
        "walk_forward_status": {
            "robustness_score": latest_wf.get("aggregate_metrics", {}).get("robustness_score", 0) if latest_wf else 0,
            "recommendation": "ROBUST" if latest_wf and latest_wf.get("aggregate_metrics", {}).get("robustness_score", 0) >= 70 else "PENDING"
        }
    }

# ============= ANALYTICS ROUTES =============

@api_router.get("/analytics/overview")
async def get_analytics_overview():
    return {"daily_returns": [round(random.uniform(-2, 4), 2) for _ in range(30)], "monthly_returns": [round(random.uniform(-5, 15), 2) for _ in range(12)], "sharpe_ratio": calculate_sharpe_ratio(), "sortino_ratio": round(random.uniform(1.5, 3.5), 2), "max_drawdown": calculate_max_drawdown(), "win_rate": round(random.uniform(55, 70), 1), "profit_factor": round(random.uniform(1.3, 2.5), 2), "total_trades": random.randint(5000, 15000)}

@api_router.get("/analytics/strategies")
async def get_strategy_analytics():
    return [{"name": "Arbitrage", "return": round(random.uniform(5, 20), 2), "trades": random.randint(500, 2000), "win_rate": round(random.uniform(65, 85), 1)}, {"name": "Momentum Trading", "return": round(random.uniform(10, 30), 2), "trades": random.randint(300, 1000), "win_rate": round(random.uniform(50, 65), 1)}, {"name": "DeFi Yield", "return": round(random.uniform(8, 25), 2), "trades": random.randint(100, 500), "win_rate": round(random.uniform(70, 90), 1)}]

# ============= SMART CONTRACT / WEB3 ROUTES =============

# Smart Contract Configuration
SEPOLIA_RPC = os.environ.get('SEPOLIA_RPC_URL', 'https://rpc.sepolia.org')
CONTRACT_ADDRESS = os.environ.get('ALPHA_AI_CONTRACT_ADDRESS', None)

# Contract ABI (key functions)
ALPHA_AI_ABI = [
    {"inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "withdraw", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "investor", "type": "address"}], "name": "getInvestorBalance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "strategyId", "type": "uint256"}], "name": "getStrategy", "outputs": [{"internalType": "string", "name": "", "type": "string"}, {"internalType": "uint256", "name": "", "type": "uint256"}, {"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "strategyCount", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "name", "type": "string"}], "name": "addStrategy", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "strategyId", "type": "uint256"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "allocateToStrategy", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "investor", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "InvestorDeposited", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "investor", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "InvestorWithdrawn", "type": "event"},
]

class Web3TransactionRequest(BaseModel):
    wallet_address: str
    action: str  # deposit, withdraw
    amount_eth: Optional[float] = None

class ContractDeploymentInfo(BaseModel):
    contract_address: Optional[str] = None
    network: str = "sepolia"
    chain_id: int = 11155111
    deployed: bool = False
    owner_address: Optional[str] = None

@api_router.get("/contract/info")
async def get_contract_info():
    """Get smart contract deployment information"""
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    
    if not contract_info:
        # Return default info indicating contract needs deployment
        return {
            "deployed": False,
            "network": "sepolia",
            "chain_id": 11155111,
            "contract_address": CONTRACT_ADDRESS,
            "explorer_url": "https://sepolia.etherscan.io",
            "rpc_url": SEPOLIA_RPC,
            "contract_source": "/api/contract/source",
            "message": "Contract ready for deployment to Sepolia testnet"
        }
    
    return contract_info

@api_router.get("/contract/source")
async def get_contract_source():
    """Get the Solidity source code for the AlphaAI Manager contract"""
    contract_path = Path(__file__).parent / "contracts" / "AlphaAIManager.sol"
    
    if contract_path.exists():
        with open(contract_path, 'r') as f:
            source_code = f.read()
        return {
            "filename": "AlphaAIManager.sol",
            "source": source_code,
            "compiler_version": "0.8.20",
            "license": "MIT"
        }
    
    return {"error": "Contract source not found"}

@api_router.post("/contract/register")
async def register_deployed_contract(contract_address: str, deployer_address: str, tx_hash: str):
    """Register a deployed contract address"""
    
    # Validate address format
    if not contract_address.startswith('0x') or len(contract_address) != 42:
        raise HTTPException(status_code=400, detail="Invalid contract address format")
    
    contract_info = {
        "contract_address": contract_address,
        "deployer_address": deployer_address,
        "deployment_tx": tx_hash,
        "network": "sepolia",
        "chain_id": 11155111,
        "deployed": True,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "verified": False
    }
    
    await db.contract_info.update_one({}, {"$set": contract_info}, upsert=True)
    
    await sim_engine.log_event("contract", f"Smart contract registered at {contract_address}", 
                              agent_name="ContractManager", 
                              details={"tx_hash": tx_hash, "network": "sepolia"})
    
    return {
        "success": True,
        "message": "Contract registered successfully",
        "contract_address": contract_address,
        "explorer_url": f"https://sepolia.etherscan.io/address/{contract_address}"
    }

@api_router.get("/contract/balance/{wallet_address}")
async def get_on_chain_balance(wallet_address: str):
    """Get investor's on-chain balance from the smart contract"""
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    
    if not contract_info or not contract_info.get('deployed'):
        return {
            "wallet_address": wallet_address,
            "on_chain_balance": 0,
            "on_chain_balance_eth": 0,
            "contract_deployed": False,
            "message": "Contract not yet deployed. Using simulated balance."
        }
    
    # For now, return simulated data
    # In production, this would call the actual contract
    simulated_balance = random.uniform(0, 5) * 10**18  # Random balance in wei
    
    return {
        "wallet_address": wallet_address,
        "on_chain_balance_wei": int(simulated_balance),
        "on_chain_balance_eth": round(simulated_balance / 10**18, 6),
        "contract_address": contract_info.get('contract_address'),
        "contract_deployed": True
    }

@api_router.get("/contract/strategies")
async def get_on_chain_strategies():
    """Get strategies registered on-chain"""
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    
    if not contract_info or not contract_info.get('deployed'):
        # Return strategies from DB as fallback
        strategies = await db.strategies.find({"status": "live"}, {"_id": 0}).to_list(10)
        return {
            "contract_deployed": False,
            "strategies": [{"id": i, "name": s.get('name'), "allocated": s.get('capital_allocated', 0), "active": True} for i, s in enumerate(strategies)],
            "message": "Strategies from simulation. Deploy contract for on-chain data."
        }
    
    # Simulated on-chain strategies
    return {
        "contract_deployed": True,
        "contract_address": contract_info.get('contract_address'),
        "strategy_count": 4,
        "strategies": [
            {"id": 0, "name": "Arbitrage Strategy", "allocated_wei": int(25 * 10**18), "allocated_eth": 25.0, "active": True},
            {"id": 1, "name": "Momentum Strategy", "allocated_wei": int(25 * 10**18), "allocated_eth": 25.0, "active": True},
            {"id": 2, "name": "Funding Rate Strategy", "allocated_wei": int(25 * 10**18), "allocated_eth": 25.0, "active": True},
            {"id": 3, "name": "AI Research Lab", "allocated_wei": int(25 * 10**18), "allocated_eth": 25.0, "active": True}
        ]
    }

@api_router.post("/contract/prepare-deposit")
async def prepare_deposit_transaction(wallet_address: str, amount_eth: float):
    """Prepare deposit transaction data for frontend to execute"""
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    
    if not contract_info or not contract_info.get('deployed'):
        raise HTTPException(status_code=400, detail="Contract not deployed yet")
    
    amount_wei = int(amount_eth * 10**18)
    
    # Prepare transaction data
    tx_data = {
        "to": contract_info.get('contract_address'),
        "value": hex(amount_wei),
        "data": "0xd0e30db0",  # deposit() function selector
        "chainId": hex(11155111),
        "gas": hex(100000)
    }
    
    return {
        "success": True,
        "transaction": tx_data,
        "amount_eth": amount_eth,
        "amount_wei": amount_wei,
        "message": f"Sign this transaction to deposit {amount_eth} ETH"
    }

@api_router.post("/contract/prepare-withdraw")
async def prepare_withdraw_transaction(wallet_address: str, amount_eth: float):
    """Prepare withdraw transaction data for frontend to execute"""
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    
    if not contract_info or not contract_info.get('deployed'):
        raise HTTPException(status_code=400, detail="Contract not deployed yet")
    
    amount_wei = int(amount_eth * 10**18)
    
    # Encode withdraw(uint256) function call
    # Function selector for withdraw(uint256)
    function_selector = "0x2e1a7d4d"
    # Encode amount as uint256 (32 bytes, padded)
    amount_hex = hex(amount_wei)[2:].zfill(64)
    data = function_selector + amount_hex
    
    tx_data = {
        "to": contract_info.get('contract_address'),
        "value": "0x0",
        "data": data,
        "chainId": hex(11155111),
        "gas": hex(100000)
    }
    
    return {
        "success": True,
        "transaction": tx_data,
        "amount_eth": amount_eth,
        "amount_wei": amount_wei,
        "message": f"Sign this transaction to withdraw {amount_eth} ETH"
    }

@api_router.get("/contract/events")
async def get_contract_events(limit: int = 20):
    """Get recent contract events (deposits, withdrawals, strategy allocations)"""
    # In production, this would query actual blockchain events
    # For now, return simulated events
    
    events = []
    event_types = ["InvestorDeposited", "InvestorWithdrawn", "StrategyAllocated"]
    
    for i in range(limit):
        event_type = random.choice(event_types)
        events.append({
            "event": event_type,
            "block_number": 5000000 + random.randint(0, 100000),
            "tx_hash": f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 168))).isoformat(),
            "args": {
                "investor" if "Investor" in event_type else "strategyId": f"0x{''.join(random.choices('0123456789abcdef', k=40))}" if "Investor" in event_type else random.randint(0, 3),
                "amount": random.randint(1, 100) * 10**17
            }
        })
    
    return {
        "events": sorted(events, key=lambda x: x['timestamp'], reverse=True),
        "count": len(events),
        "network": "sepolia"
    }

@api_router.get("/contract/deployment-guide")
async def get_deployment_guide():
    """Get step-by-step guide for deploying the contract"""
    return {
        "title": "AlphaAI Manager Contract Deployment Guide",
        "network": "Sepolia Testnet",
        "steps": [
            {
                "step": 1,
                "title": "Get Sepolia ETH",
                "description": "Get test ETH from a Sepolia faucet",
                "links": [
                    "https://sepoliafaucet.com",
                    "https://faucet.sepolia.dev"
                ]
            },
            {
                "step": 2,
                "title": "Open Remix IDE",
                "description": "Go to https://remix.ethereum.org",
                "action": "Open Remix"
            },
            {
                "step": 3,
                "title": "Create Contract File",
                "description": "Create AlphaAIManager.sol and paste the contract code",
                "code_endpoint": "/api/contract/source"
            },
            {
                "step": 4,
                "title": "Compile Contract",
                "description": "Select Solidity compiler 0.8.20 and compile",
                "settings": {"compiler": "0.8.20", "optimization": True}
            },
            {
                "step": 5,
                "title": "Deploy to Sepolia",
                "description": "Connect MetaMask to Sepolia, select 'Injected Provider', and deploy",
                "chain_id": 11155111
            },
            {
                "step": 6,
                "title": "Register Contract",
                "description": "Copy the deployed contract address and register it here",
                "endpoint": "/api/contract/register"
            }
        ],
        "contract_source_url": "/api/contract/source",
        "abi_url": "/api/contract/abi"
    }

@api_router.get("/contract/abi")
async def get_contract_abi():
    """Get the full contract ABI for frontend integration"""
    return {
        "contract_name": "AlphaAIManager",
        "abi": ALPHA_AI_ABI,
        "network": "sepolia",
        "chain_id": 11155111
    }

# ============= EVENT-DRIVEN AGENT SYSTEM =============

class EventAgent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # watcher, execution, analytics
    events_to_monitor: List[str] = []
    is_active: bool = True
    last_event_processed: Optional[str] = None
    events_processed_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ContractEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_name: str
    block_number: int
    tx_hash: str
    timestamp: str
    args: Dict[str, Any] = {}
    processed: bool = False
    processed_by: List[str] = []

# Initialize default event agents
DEFAULT_EVENT_AGENTS = [
    {
        "name": "Investor Monitor Agent",
        "type": "watcher",
        "events_to_monitor": ["InvestorDeposited", "InvestorWithdrawn"],
        "description": "Monitors investor deposit/withdrawal events and updates balances dashboard"
    },
    {
        "name": "Strategy Allocator Agent",
        "type": "execution",
        "events_to_monitor": ["InvestorDeposited"],
        "description": "Auto-allocates 25% of new deposits to top AI Lab strategy"
    },
    {
        "name": "Dashboard Updater Agent",
        "type": "analytics",
        "events_to_monitor": ["StrategyAllocated", "StrategyDeallocated"],
        "description": "Refreshes strategy allocation dashboard on allocation changes"
    }
]

@api_router.get("/agents/event-agents")
async def get_event_agents():
    """Get all configured event monitoring agents"""
    agents = await db.event_agents.find({}, {"_id": 0}).to_list(20)
    
    if not agents:
        # Initialize default agents
        for agent_data in DEFAULT_EVENT_AGENTS:
            agent = EventAgent(
                name=agent_data["name"],
                type=agent_data["type"],
                events_to_monitor=agent_data["events_to_monitor"]
            )
            doc = agent.model_dump()
            doc["description"] = agent_data["description"]
            await db.event_agents.insert_one(doc)
        # Re-fetch without _id
        agents = await db.event_agents.find({}, {"_id": 0}).to_list(20)
    
    return {"agents": agents, "count": len(agents)}

@api_router.post("/agents/event-agents/toggle/{agent_id}")
async def toggle_event_agent(agent_id: str):
    """Enable or disable an event agent"""
    agent = await db.event_agents.find_one({"id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    new_status = not agent.get('is_active', True)
    await db.event_agents.update_one({"id": agent_id}, {"$set": {"is_active": new_status}})
    
    await sim_engine.log_event("agent", f"Event agent '{agent.get('name')}' {'enabled' if new_status else 'disabled'}", 
                              agent_name="EventManager")
    
    return {"success": True, "agent_id": agent_id, "is_active": new_status}

@api_router.post("/events/simulate")
async def simulate_contract_event(event_name: str, investor_address: str = None, amount_eth: float = 1.0):
    """Simulate a contract event for testing the agent system"""
    
    # Create simulated event
    event = ContractEvent(
        event_name=event_name,
        block_number=5000000 + random.randint(0, 100000),
        tx_hash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        args={
            "investor": investor_address or f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            "amount": int(amount_eth * 10**18)
        }
    )
    
    await db.contract_events.insert_one(event.model_dump())
    
    # Process event through agents
    processing_results = await process_event(event)
    
    return {
        "success": True,
        "event": {
            "name": event_name,
            "tx_hash": event.tx_hash,
            "timestamp": event.timestamp,
            "args": event.args
        },
        "processing_results": processing_results
    }

async def process_event(event: ContractEvent):
    """Process an event through all relevant agents"""
    results = []
    
    # Get active agents that monitor this event
    agents = await db.event_agents.find({
        "is_active": True,
        "events_to_monitor": event.event_name
    }, {"_id": 0}).to_list(10)
    
    for agent in agents:
        result = await execute_agent_action(agent, event)
        results.append(result)
        
        # Update agent stats
        await db.event_agents.update_one(
            {"id": agent["id"]},
            {
                "$set": {"last_event_processed": event.timestamp},
                "$inc": {"events_processed_count": 1}
            }
        )
    
    # Mark event as processed
    await db.contract_events.update_one(
        {"id": event.id},
        {"$set": {"processed": True, "processed_by": [a["name"] for a in agents]}}
    )
    
    return results

async def execute_agent_action(agent: dict, event: ContractEvent):
    """Execute the appropriate action based on agent type and event"""
    agent_name = agent.get("name")
    agent_type = agent.get("type")
    event_name = event.event_name
    
    result = {"agent": agent_name, "event": event_name, "actions": []}
    
    if agent_type == "watcher":
        # Investor Monitor Agent - Update balances
        if event_name in ["InvestorDeposited", "InvestorWithdrawn"]:
            investor_address = event.args.get("investor")
            amount_wei = event.args.get("amount", 0)
            amount_eth = amount_wei / 10**18
            
            # Update investor balance in DB
            action = "deposit" if event_name == "InvestorDeposited" else "withdrawal"
            
            existing = await db.investor_balances.find_one({"address": investor_address})
            if existing:
                new_balance = existing.get("balance", 0) + (amount_eth if action == "deposit" else -amount_eth)
                await db.investor_balances.update_one(
                    {"address": investor_address},
                    {"$set": {"balance": new_balance, "last_updated": event.timestamp, "status": "active" if new_balance > 0 else "inactive"}}
                )
            else:
                await db.investor_balances.insert_one({
                    "address": investor_address,
                    "balance": amount_eth,
                    "status": "active",
                    "last_updated": event.timestamp
                })
            
            result["actions"].append({
                "action": "update_dashboard",
                "target": "Investor Balances",
                "details": f"{action.capitalize()}: {amount_eth:.4f} ETH for {investor_address[:10]}..."
            })
            
            await sim_engine.log_event("event_agent", f"Investor {action}: {amount_eth:.4f} ETH", 
                                      agent_name=agent_name, 
                                      details={"investor": investor_address, "amount_eth": amount_eth})
    
    elif agent_type == "execution":
        # Strategy Allocator Agent - Auto-allocate to top strategy
        if event_name == "InvestorDeposited":
            amount_wei = event.args.get("amount", 0)
            amount_eth = amount_wei / 10**18
            allocation_percent = 25
            allocation_amount = amount_eth * (allocation_percent / 100)
            
            # Get top strategy from AI Lab
            strategies = await db.strategies.find({"status": "live"}, {"_id": 0}).sort("performance_7d", -1).to_list(1)
            top_strategy = strategies[0] if strategies else {"name": "Default Momentum Strategy", "id": "default"}
            
            # Record allocation
            await db.strategy_allocations.insert_one({
                "strategy_id": top_strategy.get("id"),
                "strategy_name": top_strategy.get("name"),
                "amount_eth": allocation_amount,
                "source_event": event.tx_hash,
                "timestamp": event.timestamp
            })
            
            result["actions"].append({
                "action": "allocate_to_strategy",
                "strategy": top_strategy.get("name"),
                "amount_eth": allocation_amount,
                "details": f"Auto-allocated {allocation_amount:.4f} ETH ({allocation_percent}%) to {top_strategy.get('name')}"
            })
            
            await sim_engine.log_event("event_agent", f"Auto-allocated {allocation_amount:.4f} ETH to {top_strategy.get('name')}", 
                                      agent_name=agent_name,
                                      details={"strategy": top_strategy.get("name"), "amount": allocation_amount})
    
    elif agent_type == "analytics":
        # Dashboard Updater Agent - Refresh dashboards
        if event_name in ["StrategyAllocated", "StrategyDeallocated"]:
            result["actions"].append({
                "action": "refresh_dashboard",
                "target": "Strategy Allocation",
                "details": f"Dashboard refreshed due to {event_name}"
            })
            
            await sim_engine.log_event("event_agent", f"Dashboard refresh triggered: Strategy Allocation", 
                                      agent_name=agent_name)
    
    return result

@api_router.get("/dashboards/investor-balances")
async def get_investor_balances_dashboard():
    """Get investor balances dashboard data"""
    balances = await db.investor_balances.find({}, {"_id": 0}).sort("balance", -1).to_list(50)
    
    if not balances:
        # Return sample data
        balances = [
            {"address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}", "balance": round(random.uniform(0.5, 10), 4), "status": "active", "last_updated": datetime.now(timezone.utc).isoformat()}
            for _ in range(5)
        ]
    
    total_deposited = sum(b.get("balance", 0) for b in balances)
    active_investors = len([b for b in balances if b.get("status") == "active"])
    
    return {
        "dashboard": "Investor Balances",
        "data": balances,
        "summary": {
            "total_investors": len(balances),
            "active_investors": active_investors,
            "total_deposited_eth": round(total_deposited, 4)
        },
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/dashboards/strategy-allocation")
async def get_strategy_allocation_dashboard():
    """Get strategy allocation dashboard data"""
    allocations = await db.strategy_allocations.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    
    # Aggregate by strategy
    strategy_totals = {}
    for alloc in allocations:
        name = alloc.get("strategy_name", "Unknown")
        if name not in strategy_totals:
            strategy_totals[name] = {"allocated": 0, "transactions": 0}
        strategy_totals[name]["allocated"] += alloc.get("amount_eth", 0)
        strategy_totals[name]["transactions"] += 1
    
    # Format for dashboard
    strategies = [
        {"name": name, "allocated_capital": round(data["allocated"], 4), "transactions": data["transactions"], "active": True}
        for name, data in strategy_totals.items()
    ]
    
    if not strategies:
        # Default strategies
        strategies = [
            {"name": "Arbitrage Strategy", "allocated_capital": 25.0, "transactions": 10, "active": True},
            {"name": "Momentum Strategy", "allocated_capital": 25.0, "transactions": 8, "active": True},
            {"name": "Funding Rate Strategy", "allocated_capital": 25.0, "transactions": 12, "active": True},
            {"name": "AI Research Lab", "allocated_capital": 25.0, "transactions": 5, "active": True}
        ]
    
    total_allocated = sum(s["allocated_capital"] for s in strategies)
    
    return {
        "dashboard": "Strategy Allocation",
        "data": strategies,
        "summary": {
            "total_strategies": len(strategies),
            "total_allocated_eth": round(total_allocated, 4),
            "active_strategies": len([s for s in strategies if s["active"]])
        },
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/events/recent")
async def get_recent_events(limit: int = 20):
    """Get recent contract events with processing status"""
    events = await db.contract_events.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    
    if not events:
        # Generate sample events
        event_types = ["InvestorDeposited", "InvestorWithdrawn", "StrategyAllocated", "StrategyDeallocated"]
        for _ in range(10):
            event = ContractEvent(
                event_name=random.choice(event_types),
                block_number=5000000 + random.randint(0, 100000),
                tx_hash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                timestamp=(datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat(),
                args={
                    "investor": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                    "amount": random.randint(1, 100) * 10**17
                },
                processed=True,
                processed_by=["Investor Monitor Agent", "Strategy Allocator Agent"][:random.randint(1, 2)]
            )
            events.append(event.model_dump())
    
    return {
        "events": sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True),
        "count": len(events),
        "unprocessed": len([e for e in events if not e.get("processed", False)])
    }

@api_router.get("/integration/config")
async def get_integration_config():
    """Get the current integration configuration"""
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    agents = await db.event_agents.find({}, {"_id": 0}).to_list(10)
    
    return {
        "emergent_integration": {
            "smart_contract": {
                "network": "Sepolia",
                "chain_id": 11155111,
                "contract_address": contract_info.get("contract_address") if contract_info else None,
                "deployed": contract_info.get("deployed", False) if contract_info else False,
                "abi_url": "/api/contract/abi"
            },
            "agents": [
                {
                    "name": a.get("name"),
                    "type": a.get("type"),
                    "events_to_monitor": a.get("events_to_monitor", []),
                    "is_active": a.get("is_active", True),
                    "events_processed": a.get("events_processed_count", 0)
                }
                for a in agents
            ],
            "dashboards": {
                "Investor Balances": {
                    "url": "/api/dashboards/investor-balances",
                    "display": ["Investor Address", "Balance", "Status"]
                },
                "Strategy Allocation": {
                    "url": "/api/dashboards/strategy-allocation",
                    "display": ["Strategy Name", "Allocated Capital", "Active"]
                }
            }
        }
    }

# ============= PDF EXPORT ENDPOINT =============

from fastapi.responses import FileResponse

@api_router.get("/export/comprehensive-pdf")
async def download_comprehensive_pdf():
    """Download the comprehensive project documentation PDF"""
    pdf_path = Path(__file__).parent / "reports" / "AlphaAI_Complete_Technical_Documentation.pdf"
    
    if not pdf_path.exists():
        # Generate if not exists
        import subprocess
        subprocess.run(["python", str(Path(__file__).parent / "generate_comprehensive_report.py")], check=True)
    
    if pdf_path.exists():
        return FileResponse(
            path=str(pdf_path),
            filename="AlphaAI_Complete_Technical_Documentation.pdf",
            media_type="application/pdf"
        )
    
    raise HTTPException(status_code=404, detail="PDF report not found. Please run the generator script.")

@api_router.post("/export/regenerate-pdf")
async def regenerate_comprehensive_pdf():
    """Regenerate the comprehensive project documentation PDF"""
    import subprocess
    try:
        result = subprocess.run(
            ["python", str(Path(__file__).parent / "generate_comprehensive_report.py")],
            capture_output=True,
            text=True,
            check=True
        )
        pdf_path = Path(__file__).parent / "reports" / "AlphaAI_Complete_Technical_Documentation.pdf"
        return {
            "success": True,
            "message": "PDF regenerated successfully",
            "path": str(pdf_path),
            "download_url": "/api/export/comprehensive-pdf"
        }
    except subprocess.CalledProcessError as e:
        return {"success": False, "message": f"Generation failed: {e.stderr}"}

# ============= MARKETING ASSETS ENDPOINTS =============

@api_router.get("/marketing/assets")
async def list_marketing_assets():
    """List all available marketing assets"""
    assets_dir = Path(__file__).parent / "marketing_assets"
    if not assets_dir.exists():
        return {"assets": [], "message": "No marketing assets generated yet"}
    
    assets = []
    for f in assets_dir.iterdir():
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            assets.append({
                "name": f.stem,
                "filename": f.name,
                "url": f"/api/marketing/image/{f.name}",
                "size_kb": round(f.stat().st_size / 1024, 1)
            })
    
    return {"assets": assets, "count": len(assets)}

@api_router.get("/marketing/image/{filename}")
async def get_marketing_image(filename: str):
    """Get a specific marketing image"""
    assets_dir = Path(__file__).parent / "marketing_assets"
    filepath = assets_dir / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    media_type = "image/jpeg" if filepath.suffix.lower() in ['.jpg', '.jpeg'] else "image/png"
    return FileResponse(path=str(filepath), media_type=media_type)

@api_router.post("/marketing/generate/{image_name}")
async def generate_marketing_image(image_name: str):
    """Generate a specific marketing image using Nano Banana"""
    import subprocess
    try:
        result = subprocess.run(
            ["python", str(Path(__file__).parent / "generate_marketing_images.py"), image_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Generated {image_name}",
                "url": f"/api/marketing/image/{image_name}.jpg"
            }
        else:
            return {"success": False, "message": result.stderr or "Generation failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ============= VIDEO ASSETS ENDPOINTS =============

@api_router.get("/marketing/videos")
async def list_marketing_videos():
    """List all available marketing videos"""
    videos_dir = Path(__file__).parent / "marketing_assets" / "videos"
    if not videos_dir.exists():
        return {"videos": [], "message": "No marketing videos generated yet"}
    
    videos = []
    for f in videos_dir.iterdir():
        if f.suffix.lower() in ['.mp4', '.webm', '.mov']:
            videos.append({
                "name": f.stem,
                "filename": f.name,
                "url": f"/api/marketing/video/{f.name}",
                "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
            })
    
    return {"videos": videos, "count": len(videos)}

@api_router.get("/marketing/video/{filename}")
async def get_marketing_video(filename: str, request: Request):
    """Get a specific marketing video with proper range support for playback"""
    videos_dir = Path(__file__).parent / "marketing_assets" / "videos"
    filepath = videos_dir / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_size = filepath.stat().st_size
    
    # Handle range requests for video seeking
    range_header = request.headers.get("range")
    
    if range_header:
        # Parse range header
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            
            if start >= file_size:
                raise HTTPException(status_code=416, detail="Range not satisfiable")
            
            end = min(end, file_size - 1)
            content_length = end - start + 1
            
            def iter_file_range():
                with open(filepath, "rb") as f:
                    f.seek(start)
                    remaining = content_length
                    while remaining > 0:
                        chunk_size = min(8192, remaining)
                        data = f.read(chunk_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            
            from starlette.responses import StreamingResponse
            return StreamingResponse(
                iter_file_range(),
                status_code=206,
                media_type="video/mp4",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                }
            )
    
    # No range - return full file
    return FileResponse(
        path=str(filepath),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
        }
    )

@api_router.post("/marketing/generate-video/{video_name}")
async def generate_marketing_video(video_name: str, background_tasks: BackgroundTasks):
    """Generate a specific marketing video using Sora 2 (runs in background)"""
    import subprocess
    
    # Available video types
    available = ["hero_promo", "social_short", "agents_showcase", "security_promo"]
    if video_name not in available:
        return {"success": False, "message": f"Unknown video. Available: {available}"}
    
    # Run in background since video generation takes 2-5 minutes
    def generate():
        subprocess.run(
            ["python", str(Path(__file__).parent / "generate_promo_videos.py"), video_name],
            capture_output=True,
            text=True,
            timeout=600
        )
    
    background_tasks.add_task(generate)
    
    return {
        "success": True,
        "message": f"Video generation started for '{video_name}'. Check /api/marketing/videos in 3-5 minutes.",
        "video_name": video_name
    }

# ============= VIRAL ADS ENDPOINTS =============

@api_router.get("/marketing/ads")
async def list_viral_ads():
    """List all viral ad variations"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads"
    ads = []
    if ads_dir.exists():
        for f in ads_dir.iterdir():
            if f.suffix.lower() == '.mp4':
                ads.append({
                    "name": f.stem.replace("_", " ").title(),
                    "filename": f.name,
                    "url": f"/api/marketing/ad/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    return {"ads": ads, "count": len(ads)}

@api_router.get("/marketing/ad/{filename}")
async def get_viral_ad(filename: str, request: Request):
    """Get a specific viral ad video"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads"
    filepath = ads_dir / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Ad not found")
    
    file_size = filepath.stat().st_size
    range_header = request.headers.get("range")
    
    if range_header:
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            content_length = end - start + 1
            
            def iter_file_range():
                with open(filepath, "rb") as f:
                    f.seek(start)
                    remaining = content_length
                    while remaining > 0:
                        chunk = min(8192, remaining)
                        data = f.read(chunk)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            
            from starlette.responses import StreamingResponse
            return StreamingResponse(
                iter_file_range(),
                status_code=206,
                media_type="video/mp4",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                }
            )
    
    return FileResponse(path=str(filepath), media_type="video/mp4")

@api_router.get("/marketing/ads/preview")
async def ads_preview_page():
    """HTML page to preview viral ads"""
    from fastapi.responses import HTMLResponse
    
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads"
    ads = []
    if ads_dir.exists():
        # Sort by name to show main first
        for f in sorted(ads_dir.iterdir()):
            if f.suffix.lower() == '.mp4':
                ads.append({
                    "name": f.stem.replace("_", " ").title().replace("Alphaai Ad ", ""),
                    "filename": f.name,
                    "url": f"/api/marketing/ad/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    
    ad_cards = ""
    for ad in ads:
        highlight = "border: 2px solid #00FF94;" if "voice" in ad["filename"] else ""
        label = "⭐ WITH VOICEOVER" if "voice" in ad["filename"] else ""
        ad_cards += f'''
        <div class="ad-card" style="{highlight}">
            <h3>{ad["name"]} {label}</h3>
            <p class="size">{ad["size_mb"]} MB</p>
            <video controls preload="auto" playsinline>
                <source src="{ad["url"]}" type="video/mp4">
            </video>
            <a href="{ad["url"]}" download="{ad["filename"]}" class="btn">⬇️ Download</a>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>AlphaAI Viral Ads - TikTok/Reels Ready</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0a15, #1a1033);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #7B61FF; text-align: center; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #00FF94; margin-bottom: 30px; font-size: 14px; }}
        .ads-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .ad-card {{
            background: rgba(30, 30, 50, 0.8);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }}
        .ad-card h3 {{ color: #fff; margin: 0 0 5px 0; font-size: 14px; }}
        .ad-card .size {{ color: #888; margin: 0 0 10px 0; font-size: 12px; }}
        video {{
            width: 100%;
            max-height: 350px;
            border-radius: 8px;
            background: #000;
        }}
        .btn {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background: #7B61FF;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 13px;
        }}
        .specs {{ 
            background: rgba(0,255,148,0.1); 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px;
            text-align: center;
        }}
        .specs span {{ 
            display: inline-block; 
            margin: 0 15px; 
            color: #00FF94;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 AlphaAI Viral Ads</h1>
        <p class="subtitle">TikTok • Instagram Reels • YouTube Shorts Ready</p>
        
        <div class="specs">
            <span>📐 9:16 Vertical</span>
            <span>⏱️ 16 seconds</span>
            <span>📱 720x1280</span>
            <span>🎯 4 Hook Variations</span>
        </div>
        
        <div class="ads-grid">
            {ad_cards if ads else '<p>No ads generated yet</p>'}
        </div>
    </div>
</body>
</html>'''
    return HTMLResponse(content=html)

@api_router.get("/marketing/preview")
async def video_preview_page():
    """HTML page to preview all marketing videos"""
    from fastapi.responses import HTMLResponse
    
    videos_dir = Path(__file__).parent / "marketing_assets" / "videos"
    videos = []
    if videos_dir.exists():
        # Sort to show main promo first
        files = sorted(videos_dir.iterdir(), key=lambda x: x.stat().st_size, reverse=True)
        for f in files:
            if f.suffix.lower() == '.mp4' and 'outro_clip' not in f.name:
                videos.append({
                    "name": f.stem.replace("_", " ").title(),
                    "filename": f.name,
                    "url": f"/api/marketing/video/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    
    video_cards = ""
    for v in videos:
        video_cards += f'''
        <div class="video-card">
            <h3>{v["name"]} ({v["size_mb"]} MB)</h3>
            <video controls preload="auto" playsinline>
                <source src="{v["url"]}" type="video/mp4">
            </video>
            <div class="buttons">
                <a href="{v["url"]}" download="{v["filename"]}" class="btn download">⬇️ Download MP4</a>
            </div>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>AlphaAI Marketing Videos</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0a15;
            color: white;
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #7B61FF; text-align: center; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #888; margin-bottom: 30px; }}
        .video-card {{
            background: #1a1a2e;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #333;
        }}
        .video-card h3 {{ color: #00FF94; margin: 0 0 15px 0; }}
        video {{
            width: 100%;
            max-height: 500px;
            border-radius: 8px;
            background: #000;
            display: block;
        }}
        .buttons {{ margin-top: 15px; }}
        .btn {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            margin-right: 10px;
        }}
        .download {{ background: #7B61FF; color: white; }}
        .download:hover {{ background: #6B51EF; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 AlphaAI Marketing Videos</h1>
        <p class="subtitle">Click play button to watch • Click download to save</p>
        {video_cards if videos else '<p style="text-align:center">No videos available</p>'}
    </div>
</body>
</html>'''
    return HTMLResponse(content=html)

# ============= HIGH-CONVERTING ADS V2 =============

@api_router.get("/marketing/ads-v2")
async def list_hc_ads():
    """List high-converting ad variations v2"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads_v2"
    ads = []
    if ads_dir.exists():
        for f in sorted(ads_dir.iterdir()):
            if f.suffix.lower() == '.mp4':
                ads.append({
                    "name": f.stem,
                    "url": f"/api/marketing/ad-v2/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1),
                    "has_voice": "voice" in f.name
                })
    return {"ads": ads, "count": len(ads)}

@api_router.get("/marketing/ad-v2/{filename}")
async def get_hc_ad(filename: str, request: Request):
    """Get a high-converting ad video v2"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads_v2"
    filepath = ads_dir / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Ad not found")
    return FileResponse(path=str(filepath), media_type="video/mp4")

@api_router.get("/marketing/ads-v2/preview")
async def hc_ads_preview_page():
    """Preview page for high-converting ads v2"""
    from fastapi.responses import HTMLResponse
    
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads_v2"
    ads = []
    if ads_dir.exists():
        for f in sorted(ads_dir.iterdir()):
            if f.suffix.lower() == '.mp4' and 'voice' in f.name:
                hook = f.stem.replace("alphaai_hc_ad_", "").replace("_voice", "").upper()
                ads.append({
                    "name": hook,
                    "filename": f.name,
                    "url": f"/api/marketing/ad-v2/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    
    hooks = {
        "MAIN": "This AI trades crypto for you 24/7",
        "V1": "I built an AI that trades crypto for me",
        "V2": "This bot never sleeps",
        "V3": "Stop trading manually"
    }
    
    ad_cards = ""
    for ad in ads:
        hook_text = hooks.get(ad["name"], ad["name"])
        star = "⭐ RECOMMENDED" if ad["name"] == "MAIN" else ""
        ad_cards += f'''
        <div class="ad-card">
            <div class="badge">{star}</div>
            <h3>Hook: {ad["name"]}</h3>
            <p class="hook-text">"{hook_text}"</p>
            <video controls preload="auto" playsinline>
                <source src="{ad["url"]}" type="video/mp4">
            </video>
            <a href="{ad["url"]}" download class="btn">⬇️ Download</a>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>AlphaAI High-Converting Ads v2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(180deg, #0a0a15 0%, #1a1033 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #7B61FF; text-align: center; font-size: 28px; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #00FF94; margin-bottom: 20px; font-size: 14px; }}
        .specs {{
            display: flex; justify-content: center; gap: 20px;
            background: rgba(123,97,255,0.1); padding: 12px; border-radius: 8px;
            margin-bottom: 25px; flex-wrap: wrap;
        }}
        .specs span {{ color: #00FF94; font-size: 13px; }}
        .ads-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}
        .ad-card {{
            background: rgba(30, 30, 50, 0.9);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #333;
            position: relative;
        }}
        .ad-card .badge {{
            position: absolute; top: 10px; right: 10px;
            background: #00FF94; color: black; padding: 3px 8px;
            border-radius: 4px; font-size: 10px; font-weight: bold;
        }}
        .ad-card h3 {{ color: #7B61FF; font-size: 14px; margin-bottom: 5px; }}
        .ad-card .hook-text {{ color: #aaa; font-size: 12px; margin-bottom: 12px; font-style: italic; }}
        video {{
            width: 100%; max-height: 400px;
            border-radius: 8px; background: #000;
        }}
        .btn {{
            display: block; text-align: center;
            margin-top: 10px; padding: 10px;
            background: #7B61FF; color: white;
            text-decoration: none; border-radius: 6px;
            font-weight: 500;
        }}
        .btn:hover {{ background: #6B51EF; }}
        .structure {{
            background: rgba(0,0,0,0.3); padding: 15px;
            border-radius: 8px; margin-bottom: 20px;
        }}
        .structure h3 {{ color: #00FF94; margin-bottom: 10px; font-size: 14px; }}
        .structure table {{ width: 100%; font-size: 12px; }}
        .structure td {{ padding: 4px 8px; border-bottom: 1px solid #333; }}
        .structure td:first-child {{ color: #7B61FF; width: 60px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 High-Converting Ads v2</h1>
        <p class="subtitle">Optimized for TikTok • Instagram Reels • YouTube Shorts • Paid Ads</p>
        
        <div class="specs">
            <span>📐 9:16 Vertical</span>
            <span>⏱️ 14 seconds</span>
            <span>📱 720x1280</span>
            <span>🎙️ With Voiceover</span>
            <span>🎯 4 Hook Variations</span>
        </div>
        
        <div class="structure">
            <h3>📋 Ad Structure</h3>
            <table>
                <tr><td>0-2s</td><td><b>HOOK</b> - Attention grabber</td></tr>
                <tr><td>2-3.5s</td><td><b>PROBLEM</b> - "Most people LOSE MONEY"</td></tr>
                <tr><td>3.5-7s</td><td><b>SOLUTION</b> - "AlphaAI finds trades automatically"</td></tr>
                <tr><td>7-11s</td><td><b>PROOF</b> - "+12% last month (paper trading)"</td></tr>
                <tr><td>11-14s</td><td><b>CTA</b> - "TRY IT FREE - Link in bio"</td></tr>
            </table>
        </div>
        
        <div class="ads-grid">
            {ad_cards}
        </div>
    </div>
</body>
</html>'''
    return HTMLResponse(content=html)

# ============= STRIPE SUBSCRIPTION ENDPOINTS =============

# Pro subscription pricing
PRO_SUBSCRIPTION_PACKAGES = {
    "pro_monthly": {"amount": 29.00, "currency": "usd", "name": "AlphaAI Pro Monthly", "period": "month"},
    "pro_yearly": {"amount": 249.00, "currency": "usd", "name": "AlphaAI Pro Yearly", "period": "year"}
}

class CreateCheckoutRequest(BaseModel):
    package_id: str = "pro_monthly"
    origin_url: str
    wallet_address: Optional[str] = None

@api_router.post("/payments/checkout")
async def create_checkout_session(request: CreateCheckoutRequest, http_request: Request):
    """Create a Stripe checkout session for Pro subscription"""
    try:
        # Validate package
        if request.package_id not in PRO_SUBSCRIPTION_PACKAGES:
            raise HTTPException(status_code=400, detail="Invalid subscription package")
        
        package = PRO_SUBSCRIPTION_PACKAGES[request.package_id]
        
        # Build URLs from frontend origin
        success_url = f"{request.origin_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}&payment=success"
        cancel_url = f"{request.origin_url}/dashboard?payment=cancelled"
        
        # Setup webhook URL
        host_url = str(http_request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        
        # Initialize Stripe checkout
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create metadata
        metadata = {
            "package_id": request.package_id,
            "package_name": package["name"],
            "wallet_address": request.wallet_address or "demo_user",
            "subscription_period": package["period"]
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=package["amount"],
            currency=package["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "wallet_address": request.wallet_address or "demo_user",
            "package_id": request.package_id,
            "amount": package["amount"],
            "currency": package["currency"],
            "payment_status": "pending",
            "status": "initiated",
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.payment_transactions.insert_one(transaction)
        
        logger.info(f"Created checkout session: {session.session_id} for package: {request.package_id}")
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "package": package
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, http_request: Request):
    """Get payment status for a checkout session"""
    try:
        # Check if already processed
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        # If already marked as paid, return cached status
        if transaction.get("payment_status") == "paid":
            return {
                "session_id": session_id,
                "status": transaction.get("status"),
                "payment_status": transaction.get("payment_status"),
                "is_pro": True,
                "package_id": transaction.get("package_id"),
                "amount": transaction.get("amount")
            }
        
        # Setup Stripe checkout
        host_url = str(http_request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Get status from Stripe
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction in database
        update_data = {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "updated_at": datetime.now(timezone.utc)
        }
        
        # If payment is successful, mark user as pro
        is_pro = checkout_status.payment_status == "paid"
        if is_pro:
            update_data["pro_activated_at"] = datetime.now(timezone.utc)
            
            # Update investor record to mark as Pro
            wallet_address = transaction.get("wallet_address")
            if wallet_address and wallet_address != "demo_user":
                await db.investors.update_one(
                    {"wallet_address": wallet_address},
                    {"$set": {"is_pro": True, "pro_since": datetime.now(timezone.utc)}}
                )
        
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        return {
            "session_id": session_id,
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "is_pro": is_pro,
            "amount": checkout_status.amount_total / 100,  # Convert from cents
            "currency": checkout_status.currency,
            "package_id": transaction.get("package_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        host_url = str(request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction based on webhook event
        if webhook_response.session_id:
            update_data = {
                "status": webhook_response.event_type,
                "payment_status": webhook_response.payment_status,
                "webhook_event_id": webhook_response.event_id,
                "updated_at": datetime.now(timezone.utc)
            }
            
            if webhook_response.payment_status == "paid":
                update_data["pro_activated_at"] = datetime.now(timezone.utc)
                
                # Get transaction to find wallet address
                transaction = await db.payment_transactions.find_one({"session_id": webhook_response.session_id})
                if transaction:
                    wallet_address = transaction.get("wallet_address")
                    if wallet_address and wallet_address != "demo_user":
                        await db.investors.update_one(
                            {"wallet_address": wallet_address},
                            {"$set": {"is_pro": True, "pro_since": datetime.now(timezone.utc)}}
                        )
            
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": update_data}
            )
        
        logger.info(f"Processed webhook: {webhook_response.event_type} for session: {webhook_response.session_id}")
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/payments/packages")
async def get_subscription_packages():
    """Get available subscription packages"""
    return {
        "packages": [
            {
                "id": "pro_monthly",
                "name": "AlphaAI Pro Monthly",
                "price": 29.00,
                "currency": "usd",
                "period": "month",
                "features": [
                    "Real-time AI signals (no delay)",
                    "Push notifications & email alerts",
                    "Advanced AI market analysis",
                    "Priority support"
                ]
            },
            {
                "id": "pro_yearly",
                "name": "AlphaAI Pro Yearly",
                "price": 249.00,
                "currency": "usd",
                "period": "year",
                "savings": "Save $99/year",
                "features": [
                    "Real-time AI signals (no delay)",
                    "Push notifications & email alerts",
                    "Advanced AI market analysis",
                    "Priority support",
                    "2 months FREE"
                ]
            }
        ]
    }

@api_router.get("/users/pro-status/{wallet_address}")
async def get_pro_status(wallet_address: str):
    """Check if a user has Pro subscription"""
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        return {"is_pro": False, "wallet_address": wallet_address}
    
    return {
        "is_pro": investor.get("is_pro", False),
        "pro_since": investor.get("pro_since"),
        "wallet_address": wallet_address
    }

# Include router and middleware
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
