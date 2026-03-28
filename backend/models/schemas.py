"""
AlphaAI Pydantic Models
All request/response schemas used across the platform.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

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
    is_pro: bool = False
    is_elite: bool = False
    pro_since: Optional[datetime] = None
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

# ============= LIVE TRADING MODELS =============
class TradeOrder(BaseModel):
    """Trade order for execution"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_address: str
    signal_id: Optional[str] = None
    symbol: str  # BTC, ETH, SOL
    side: str  # BUY or SELL
    amount_usd: float
    slippage_tolerance: float = 0.5  # 0.5%
    is_live: bool = False  # False = paper trade
    status: str = "pending"  # pending, submitted, confirmed, failed, cancelled
    tx_hash: Optional[str] = None
    gas_used: Optional[int] = None
    gas_price_gwei: Optional[float] = None
    executed_price: Optional[float] = None
    executed_amount: Optional[float] = None
    fee_paid: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

class TradePosition(BaseModel):
    """Open trading position"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_address: str
    symbol: str
    side: str  # LONG or SHORT
    entry_price: float
    current_price: float
    amount: float
    amount_usd: float
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0
    is_live: bool = False
    opened_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============= TRADING REQUEST MODELS =============
class ExecuteTradeRequest(BaseModel):
    wallet_address: str
    symbol: str
    side: str  # BUY or SELL
    amount_usd: float
    signal_id: Optional[str] = None
    is_live: bool = False  # False = paper trading
    slippage_tolerance: float = 0.5

class ClosePositionRequest(BaseModel):
    wallet_address: str
    position_id: str
    is_live: bool = False


# ============= ADVANCED SIMULATION MODELS =============
class AdvancedSimulationConfig(BaseModel):
    time_acceleration: int = 100
    start_date: str = "2025-01-01"
    end_date: str = "2025-12-31"
    initial_capital: float = 100000.0
    agents: List[Dict[str, Any]] = []
    stress_test_enabled: bool = False
    stress_scenarios: List[Dict[str, Any]] = []


# ============= RESEARCH ENGINE MODELS =============
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


# ============= WEB3 MODELS =============
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


# ============= EVENT AGENT MODELS =============
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


# ============= CHECKOUT MODELS =============
class CreateCheckoutRequest(BaseModel):
    package_id: str = "pro_monthly"
    origin_url: str
    wallet_address: Optional[str] = None
    user_email: Optional[str] = None


# ============= ANALYTICS MODELS =============
class AnalyticsEvent(BaseModel):
    event_type: str  # 'view', 'click', 'conversion', 'dismiss'
    feature: str     # 'exit_popup', 'timed_popup', 'unlock_btn', 'upgrade_cta', 'missed_trade', 'social_proof'
    variant: Optional[str] = 'default'  # For A/B testing variants
    session_id: Optional[str] = None
    wallet_address: Optional[str] = None
    metadata: Optional[dict] = None


# ============= NOTIFICATION MODELS =============
class NotificationPreferencesUpdate(BaseModel):
    push_enabled: Optional[bool] = None
    signal_alerts: Optional[bool] = None
    high_confidence_alerts: Optional[bool] = None
    trade_confirmations: Optional[bool] = None
    price_alerts: Optional[bool] = None
    daily_summary: Optional[bool] = None
    weekly_report: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"


# ============= EXECUTION MODELS =============
class ExecutionSimulateRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    strategy_id: Optional[str] = None

