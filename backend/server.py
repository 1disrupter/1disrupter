from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, BackgroundTasks
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
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

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
    
    return {
        "simulation": {
            "is_running": config.get('is_running', False),
            "mode": config.get('mode', 'paper'),
            "start_time": config.get('start_time'),
            "initial_capital": config.get('initial_capital', 10000),
            "current_capital": round(config.get('current_capital', 10000), 2),
            "total_return_percent": round((config.get('current_capital', 10000) - config.get('initial_capital', 10000)) / config.get('initial_capital', 10000) * 100, 2) if config.get('initial_capital', 10000) > 0 else 0
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
        }
    }

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

# ============= ANALYTICS ROUTES =============

@api_router.get("/analytics/overview")
async def get_analytics_overview():
    return {"daily_returns": [round(random.uniform(-2, 4), 2) for _ in range(30)], "monthly_returns": [round(random.uniform(-5, 15), 2) for _ in range(12)], "sharpe_ratio": calculate_sharpe_ratio(), "sortino_ratio": round(random.uniform(1.5, 3.5), 2), "max_drawdown": calculate_max_drawdown(), "win_rate": round(random.uniform(55, 70), 1), "profit_factor": round(random.uniform(1.3, 2.5), 2), "total_trades": random.randint(5000, 15000)}

@api_router.get("/analytics/strategies")
async def get_strategy_analytics():
    return [{"name": "Arbitrage", "return": round(random.uniform(5, 20), 2), "trades": random.randint(500, 2000), "win_rate": round(random.uniform(65, 85), 1)}, {"name": "Momentum Trading", "return": round(random.uniform(10, 30), 2), "trades": random.randint(300, 1000), "win_rate": round(random.uniform(50, 65), 1)}, {"name": "DeFi Yield", "return": round(random.uniform(8, 25), 2), "trades": random.randint(100, 500), "win_rate": round(random.uniform(70, 90), 1)}]

# Include router and middleware
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
