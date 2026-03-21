"""
AlphaAI Performance Metrics API
- Separate Paper vs Live trading metrics
- Equity curve (daily + trade-level)
- Sharpe ratio with benchmark comparison
- Daily PnL tracking
- Compliance labeling
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
import math
import logging

logger = logging.getLogger("AlphaAI.Metrics")

# MongoDB connection - will be initialized in main server
db = None

def init_db(database):
    """Initialize database connection"""
    global db
    db = database

router = APIRouter(prefix="/api/metrics", tags=["Performance Metrics"])

# ============= MODELS =============

class DailyEquityPoint(BaseModel):
    """Daily equity snapshot"""
    date: str
    equity: float
    daily_pnl: float
    daily_return_pct: float
    cumulative_pnl: float
    cumulative_return_pct: float
    trade_count: int

class TradeEquityPoint(BaseModel):
    """Trade-level equity point"""
    timestamp: str
    equity_before: float
    equity_after: float
    pnl: float
    pnl_pct: float
    symbol: str
    side: str
    trade_id: str

class SharpeMetrics(BaseModel):
    """Sharpe ratio and risk metrics"""
    sharpe_ratio: float
    sortino_ratio: float
    risk_free_rate: float = 0.02  # 2% annual
    annualized_return: float
    annualized_volatility: float
    max_drawdown: float
    max_drawdown_duration_days: int
    calmar_ratio: float  # annualized return / max drawdown
    benchmark_comparison: Optional[Dict[str, Any]] = None

class DailyPnL(BaseModel):
    """Daily PnL breakdown"""
    date: str
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    trade_count: int
    winning_trades: int
    losing_trades: int
    best_trade: Optional[float] = None
    worst_trade: Optional[float] = None

class PerformanceSummary(BaseModel):
    """Complete performance summary for a trading mode"""
    mode: str  # "paper" or "live"
    is_simulated: bool
    compliance_label: str
    period_start: str
    period_end: str
    starting_equity: float
    current_equity: float
    total_return_pct: float
    total_pnl: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    best_day: Optional[Dict[str, Any]] = None
    worst_day: Optional[Dict[str, Any]] = None

class ComplianceInfo(BaseModel):
    """Compliance and transparency information"""
    mode: str
    is_real_money: bool
    label: str
    badge_color: str
    disclaimer_short: str
    disclaimer_full: str
    risk_warnings: List[str]

# ============= HELPER FUNCTIONS =============

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate annualized Sharpe ratio"""
    if len(returns) < 2:
        return 0.0
    
    # Convert annual risk-free to daily
    daily_rf = (1 + risk_free_rate) ** (1/365) - 1
    
    excess_returns = [r - daily_rf for r in returns]
    avg_excess = sum(excess_returns) / len(excess_returns)
    
    # Standard deviation
    if len(excess_returns) < 2:
        return 0.0
    variance = sum((r - avg_excess) ** 2 for r in excess_returns) / (len(excess_returns) - 1)
    std_dev = math.sqrt(variance) if variance > 0 else 0.0001
    
    # Annualize (sqrt(252) for trading days)
    sharpe = (avg_excess / std_dev) * math.sqrt(252) if std_dev > 0 else 0.0
    return round(sharpe, 2)

def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sortino ratio (only downside deviation)"""
    if len(returns) < 2:
        return 0.0
    
    daily_rf = (1 + risk_free_rate) ** (1/365) - 1
    excess_returns = [r - daily_rf for r in returns]
    avg_excess = sum(excess_returns) / len(excess_returns)
    
    # Only negative returns for downside deviation
    negative_returns = [r for r in excess_returns if r < 0]
    if len(negative_returns) < 2:
        return 0.0 if avg_excess <= 0 else 10.0  # Cap at 10 if no negative returns
    
    downside_variance = sum(r ** 2 for r in negative_returns) / len(negative_returns)
    downside_std = math.sqrt(downside_variance) if downside_variance > 0 else 0.0001
    
    sortino = (avg_excess / downside_std) * math.sqrt(252) if downside_std > 0 else 0.0
    return round(min(sortino, 10.0), 2)  # Cap at 10

def calculate_max_drawdown(equity_curve: List[float]) -> tuple:
    """Calculate maximum drawdown and duration"""
    if len(equity_curve) < 2:
        return 0.0, 0
    
    peak = equity_curve[0]
    max_dd = 0.0
    max_dd_duration = 0
    current_dd_start = 0
    
    for i, equity in enumerate(equity_curve):
        if equity > peak:
            peak = equity
            current_dd_start = i
        
        dd = (peak - equity) / peak * 100 if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
            max_dd_duration = i - current_dd_start
    
    return round(max_dd, 2), max_dd_duration

def get_compliance_info(mode: str) -> ComplianceInfo:
    """Get compliance labels and disclaimers"""
    if mode == "live":
        return ComplianceInfo(
            mode="live",
            is_real_money=True,
            label="LIVE TRADING",
            badge_color="#FF4444",
            disclaimer_short="Real funds at risk. Past performance does not guarantee future results.",
            disclaimer_full="""
IMPORTANT RISK DISCLOSURE:

You are viewing LIVE TRADING results involving REAL FUNDS. 

• Past performance is NOT indicative of future results
• Cryptocurrency trading involves substantial risk of loss
• You could lose some or all of your invested capital
• Only trade with funds you can afford to lose
• AlphaAI signals are not financial advice
• Always conduct your own research before trading
• Results shown include fees but may not reflect all costs

By continuing, you acknowledge these risks and agree to our Terms of Service.
            """.strip(),
            risk_warnings=[
                "Real funds are at risk",
                "Cryptocurrency is highly volatile",
                "Past performance ≠ future results",
                "Not financial advice",
                "You may lose your entire investment"
            ]
        )
    else:
        return ComplianceInfo(
            mode="paper",
            is_real_money=False,
            label="PAPER TRADING",
            badge_color="#7B61FF",
            disclaimer_short="Simulated results. No real funds involved.",
            disclaimer_full="""
PAPER TRADING DISCLOSURE:

You are viewing SIMULATED trading results. NO REAL FUNDS are involved.

• These results are hypothetical and for educational purposes only
• Paper trading does not account for market impact or slippage
• Actual trading results may differ significantly
• Simulated environments may not reflect real market conditions
• Past simulated performance does not guarantee future results
• Starting balance: $10,000 (virtual)

Paper trading is useful for learning but is not a substitute for real trading experience.
            """.strip(),
            risk_warnings=[
                "Simulated results only",
                "Does not reflect real market conditions",
                "No slippage or market impact included",
                "For educational purposes"
            ]
        )

# ============= API ROUTES =============

@router.get("/compliance/{mode}")
async def get_compliance_labels(mode: str):
    """Get compliance and transparency labels for a trading mode"""
    if mode not in ["paper", "live"]:
        raise HTTPException(status_code=400, detail="Mode must be 'paper' or 'live'")
    
    return get_compliance_info(mode)

@router.get("/summary")
async def get_performance_summary(
    wallet_address: str = Query(..., description="User wallet address"),
    mode: str = Query("paper", description="Trading mode: paper or live"),
    days: int = Query(30, description="Number of days to analyze")
):
    """Get complete performance summary for paper or live trading"""
    if mode not in ["paper", "live"]:
        raise HTTPException(status_code=400, detail="Mode must be 'paper' or 'live'")
    
    is_live = mode == "live"
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get trades for the period
    trades = await db.trades.find({
        "wallet_address": wallet_address,
        "is_live": is_live,
        "timestamp": {"$gte": cutoff_date}
    }, {"_id": 0}).sort("timestamp", 1).to_list(10000)
    
    if not trades:
        # Return empty summary
        compliance = get_compliance_info(mode)
        return PerformanceSummary(
            mode=mode,
            is_simulated=not is_live,
            compliance_label=compliance.label,
            period_start=cutoff_date.isoformat(),
            period_end=datetime.now(timezone.utc).isoformat(),
            starting_equity=10000.0 if not is_live else 0.0,
            current_equity=10000.0 if not is_live else 0.0,
            total_return_pct=0.0,
            total_pnl=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            avg_win=0.0,
            avg_loss=0.0,
            profit_factor=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0
        )
    
    # Calculate metrics
    starting_equity = 10000.0 if not is_live else trades[0].get("equity_before", 0)
    
    # Get current equity from user
    user = await db.users.find_one({"wallet_address": wallet_address}, {"_id": 0})
    if not user:
        user = await db.investors.find_one({"wallet_address": wallet_address}, {"_id": 0})
    
    current_equity = user.get("paper_balance", 10000.0) if not is_live else user.get("balance", 0)
    
    # PnL calculations
    total_pnl = sum(t.get("pnl", 0) or 0 for t in trades)
    winning_trades = [t for t in trades if (t.get("pnl") or 0) > 0]
    losing_trades = [t for t in trades if (t.get("pnl") or 0) < 0]
    
    total_wins = sum(t.get("pnl", 0) for t in winning_trades)
    total_losses = abs(sum(t.get("pnl", 0) for t in losing_trades))
    
    avg_win = total_wins / len(winning_trades) if winning_trades else 0
    avg_loss = total_losses / len(losing_trades) if losing_trades else 0
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    # Calculate daily returns for Sharpe
    daily_pnls = {}
    for trade in trades:
        date = trade.get("timestamp", datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        daily_pnls[date] = daily_pnls.get(date, 0) + (trade.get("pnl") or 0)
    
    # Convert to returns
    equity = starting_equity
    daily_returns = []
    for date in sorted(daily_pnls.keys()):
        pnl = daily_pnls[date]
        ret = pnl / equity if equity > 0 else 0
        daily_returns.append(ret)
        equity += pnl
    
    sharpe = calculate_sharpe_ratio(daily_returns)
    
    # Equity curve for drawdown
    equity_curve = [starting_equity]
    running_equity = starting_equity
    for trade in trades:
        running_equity += trade.get("pnl", 0) or 0
        equity_curve.append(running_equity)
    
    max_dd, _ = calculate_max_drawdown(equity_curve)
    
    # Best/worst days
    best_day = max(daily_pnls.items(), key=lambda x: x[1]) if daily_pnls else None
    worst_day = min(daily_pnls.items(), key=lambda x: x[1]) if daily_pnls else None
    
    compliance = get_compliance_info(mode)
    
    return PerformanceSummary(
        mode=mode,
        is_simulated=not is_live,
        compliance_label=compliance.label,
        period_start=cutoff_date.isoformat(),
        period_end=datetime.now(timezone.utc).isoformat(),
        starting_equity=round(starting_equity, 2),
        current_equity=round(current_equity, 2),
        total_return_pct=round((current_equity - starting_equity) / starting_equity * 100, 2) if starting_equity > 0 else 0,
        total_pnl=round(total_pnl, 2),
        total_trades=len(trades),
        winning_trades=len(winning_trades),
        losing_trades=len(losing_trades),
        win_rate=round(len(winning_trades) / len(trades) * 100, 1) if trades else 0,
        avg_win=round(avg_win, 2),
        avg_loss=round(avg_loss, 2),
        profit_factor=round(profit_factor, 2),
        sharpe_ratio=sharpe,
        max_drawdown=max_dd,
        best_day={"date": best_day[0], "pnl": round(best_day[1], 2)} if best_day else None,
        worst_day={"date": worst_day[0], "pnl": round(worst_day[1], 2)} if worst_day else None
    )

@router.get("/equity-curve/daily")
async def get_daily_equity_curve(
    wallet_address: str = Query(..., description="User wallet address"),
    mode: str = Query("paper", description="Trading mode: paper or live"),
    days: int = Query(30, description="Number of days")
):
    """Get daily equity curve with PnL breakdown"""
    is_live = mode == "live"
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get trades
    trades = await db.trades.find({
        "wallet_address": wallet_address,
        "is_live": is_live,
        "timestamp": {"$gte": cutoff_date}
    }, {"_id": 0}).sort("timestamp", 1).to_list(10000)
    
    # Group by day
    starting_equity = 10000.0 if not is_live else 0
    daily_data = {}
    
    for trade in trades:
        date = trade.get("timestamp", datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        if date not in daily_data:
            daily_data[date] = {"pnl": 0, "count": 0}
        daily_data[date]["pnl"] += trade.get("pnl", 0) or 0
        daily_data[date]["count"] += 1
    
    # Build equity curve
    equity_curve = []
    running_equity = starting_equity
    cumulative_pnl = 0
    
    # Fill in all days
    current_date = cutoff_date.date()
    end_date = datetime.now(timezone.utc).date()
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        day_data = daily_data.get(date_str, {"pnl": 0, "count": 0})
        
        daily_pnl = day_data["pnl"]
        daily_return = (daily_pnl / running_equity * 100) if running_equity > 0 else 0
        
        cumulative_pnl += daily_pnl
        running_equity += daily_pnl
        cumulative_return = ((running_equity - starting_equity) / starting_equity * 100) if starting_equity > 0 else 0
        
        equity_curve.append(DailyEquityPoint(
            date=date_str,
            equity=round(running_equity, 2),
            daily_pnl=round(daily_pnl, 2),
            daily_return_pct=round(daily_return, 2),
            cumulative_pnl=round(cumulative_pnl, 2),
            cumulative_return_pct=round(cumulative_return, 2),
            trade_count=day_data["count"]
        ))
        
        current_date += timedelta(days=1)
    
    compliance = get_compliance_info(mode)
    
    return {
        "mode": mode,
        "compliance_label": compliance.label,
        "is_simulated": not is_live,
        "period_days": days,
        "starting_equity": starting_equity,
        "ending_equity": running_equity,
        "total_pnl": round(cumulative_pnl, 2),
        "total_return_pct": round(cumulative_return, 2),
        "equity_curve": equity_curve
    }

@router.get("/equity-curve/trades")
async def get_trade_level_equity(
    wallet_address: str = Query(..., description="User wallet address"),
    mode: str = Query("paper", description="Trading mode: paper or live"),
    limit: int = Query(100, description="Max trades to return")
):
    """Get trade-by-trade equity changes"""
    is_live = mode == "live"
    
    trades = await db.trades.find({
        "wallet_address": wallet_address,
        "is_live": is_live
    }, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    
    trades.reverse()  # Oldest first
    
    starting_equity = 10000.0 if not is_live else 0
    trade_equity = []
    running_equity = starting_equity
    
    for trade in trades:
        pnl = trade.get("pnl", 0) or 0
        equity_before = running_equity
        equity_after = running_equity + pnl
        pnl_pct = (pnl / equity_before * 100) if equity_before > 0 else 0
        
        trade_equity.append(TradeEquityPoint(
            timestamp=trade.get("timestamp", datetime.now(timezone.utc)).isoformat(),
            equity_before=round(equity_before, 2),
            equity_after=round(equity_after, 2),
            pnl=round(pnl, 2),
            pnl_pct=round(pnl_pct, 2),
            symbol=trade.get("symbol", ""),
            side=trade.get("side", ""),
            trade_id=trade.get("id", "")
        ))
        
        running_equity = equity_after
    
    compliance = get_compliance_info(mode)
    
    return {
        "mode": mode,
        "compliance_label": compliance.label,
        "is_simulated": not is_live,
        "total_trades": len(trade_equity),
        "starting_equity": starting_equity,
        "ending_equity": round(running_equity, 2),
        "trade_equity": trade_equity
    }

@router.get("/sharpe")
async def get_sharpe_metrics(
    wallet_address: str = Query(..., description="User wallet address"),
    mode: str = Query("paper", description="Trading mode: paper or live"),
    days: int = Query(30, description="Number of days"),
    risk_free_rate: float = Query(0.02, description="Annual risk-free rate"),
    include_benchmark: bool = Query(True, description="Include BTC benchmark comparison")
):
    """Get Sharpe ratio and advanced risk metrics with optional benchmark"""
    is_live = mode == "live"
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get trades
    trades = await db.trades.find({
        "wallet_address": wallet_address,
        "is_live": is_live,
        "timestamp": {"$gte": cutoff_date}
    }, {"_id": 0}).sort("timestamp", 1).to_list(10000)
    
    # Calculate daily returns
    starting_equity = 10000.0 if not is_live else 0
    daily_pnls = {}
    
    for trade in trades:
        date = trade.get("timestamp", datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        daily_pnls[date] = daily_pnls.get(date, 0) + (trade.get("pnl") or 0)
    
    equity = starting_equity
    daily_returns = []
    equity_curve = [starting_equity]
    
    for date in sorted(daily_pnls.keys()):
        pnl = daily_pnls[date]
        ret = pnl / equity if equity > 0 else 0
        daily_returns.append(ret)
        equity += pnl
        equity_curve.append(equity)
    
    # Calculate metrics
    sharpe = calculate_sharpe_ratio(daily_returns, risk_free_rate)
    sortino = calculate_sortino_ratio(daily_returns, risk_free_rate)
    max_dd, max_dd_duration = calculate_max_drawdown(equity_curve)
    
    # Annualized return and volatility
    total_return = (equity - starting_equity) / starting_equity if starting_equity > 0 else 0
    annualized_return = ((1 + total_return) ** (365 / max(days, 1)) - 1) * 100
    
    if daily_returns:
        avg_daily_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - avg_daily_return) ** 2 for r in daily_returns) / max(len(daily_returns) - 1, 1)
        daily_volatility = math.sqrt(variance)
        annualized_volatility = daily_volatility * math.sqrt(252) * 100
    else:
        annualized_volatility = 0
    
    calmar = annualized_return / max_dd if max_dd > 0 else 0
    
    # Benchmark comparison (BTC buy-and-hold)
    benchmark = None
    if include_benchmark:
        # Simulate BTC performance over same period
        # Using approximate historical volatility
        btc_daily_return = 0.0015  # ~0.15% average daily
        btc_daily_volatility = 0.04  # ~4% daily volatility
        
        btc_returns = [btc_daily_return for _ in range(len(daily_returns))] if daily_returns else []
        btc_sharpe = calculate_sharpe_ratio(btc_returns, risk_free_rate)
        btc_total_return = ((1 + btc_daily_return) ** len(btc_returns) - 1) * 100 if btc_returns else 0
        
        benchmark = {
            "name": "BTC Buy-and-Hold",
            "sharpe_ratio": btc_sharpe,
            "annualized_return": round(btc_total_return * (365 / max(days, 1)), 2),
            "annualized_volatility": round(btc_daily_volatility * math.sqrt(252) * 100, 2),
            "alpha": round(annualized_return - btc_total_return * (365 / max(days, 1)), 2),
            "outperforming": sharpe > btc_sharpe
        }
    
    compliance = get_compliance_info(mode)
    
    return {
        "mode": mode,
        "compliance_label": compliance.label,
        "is_simulated": not is_live,
        "period_days": days,
        "metrics": SharpeMetrics(
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            risk_free_rate=risk_free_rate,
            annualized_return=round(annualized_return, 2),
            annualized_volatility=round(annualized_volatility, 2),
            max_drawdown=max_dd,
            max_drawdown_duration_days=max_dd_duration,
            calmar_ratio=round(calmar, 2),
            benchmark_comparison=benchmark
        )
    }

@router.get("/daily-pnl")
async def get_daily_pnl(
    wallet_address: str = Query(..., description="User wallet address"),
    mode: str = Query("paper", description="Trading mode: paper or live"),
    days: int = Query(30, description="Number of days")
):
    """Get daily PnL breakdown"""
    is_live = mode == "live"
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get trades
    trades = await db.trades.find({
        "wallet_address": wallet_address,
        "is_live": is_live,
        "timestamp": {"$gte": cutoff_date}
    }, {"_id": 0}).sort("timestamp", 1).to_list(10000)
    
    # Group by day
    daily_data = {}
    
    for trade in trades:
        date = trade.get("timestamp", datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        if date not in daily_data:
            daily_data[date] = {
                "realized_pnl": 0,
                "trades": [],
                "winning": 0,
                "losing": 0
            }
        
        pnl = trade.get("pnl", 0) or 0
        daily_data[date]["realized_pnl"] += pnl
        daily_data[date]["trades"].append(pnl)
        
        if pnl > 0:
            daily_data[date]["winning"] += 1
        elif pnl < 0:
            daily_data[date]["losing"] += 1
    
    # Build response
    daily_pnl_list = []
    
    for date in sorted(daily_data.keys()):
        data = daily_data[date]
        trades_pnl = data["trades"]
        
        daily_pnl_list.append(DailyPnL(
            date=date,
            realized_pnl=round(data["realized_pnl"], 2),
            unrealized_pnl=0,  # Would need position data for unrealized
            total_pnl=round(data["realized_pnl"], 2),
            trade_count=len(trades_pnl),
            winning_trades=data["winning"],
            losing_trades=data["losing"],
            best_trade=round(max(trades_pnl), 2) if trades_pnl else None,
            worst_trade=round(min(trades_pnl), 2) if trades_pnl else None
        ))
    
    compliance = get_compliance_info(mode)
    
    # Summary stats
    total_pnl = sum(d.realized_pnl for d in daily_pnl_list)
    profitable_days = sum(1 for d in daily_pnl_list if d.realized_pnl > 0)
    losing_days = sum(1 for d in daily_pnl_list if d.realized_pnl < 0)
    
    return {
        "mode": mode,
        "compliance_label": compliance.label,
        "is_simulated": not is_live,
        "period_days": days,
        "total_pnl": round(total_pnl, 2),
        "profitable_days": profitable_days,
        "losing_days": losing_days,
        "win_day_rate": round(profitable_days / max(len(daily_pnl_list), 1) * 100, 1),
        "avg_daily_pnl": round(total_pnl / max(len(daily_pnl_list), 1), 2),
        "daily_pnl": daily_pnl_list
    }

@router.get("/combined")
async def get_combined_metrics(
    wallet_address: str = Query(..., description="User wallet address"),
    days: int = Query(30, description="Number of days")
):
    """Get combined paper and live trading metrics for side-by-side comparison"""
    # Get both paper and live summaries
    paper_summary = await get_performance_summary(wallet_address, "paper", days)
    live_summary = await get_performance_summary(wallet_address, "live", days)
    
    paper_compliance = get_compliance_info("paper")
    live_compliance = get_compliance_info("live")
    
    return {
        "period_days": days,
        "paper": {
            "summary": paper_summary,
            "compliance": paper_compliance
        },
        "live": {
            "summary": live_summary,
            "compliance": live_compliance
        },
        "comparison": {
            "paper_outperforms_live": paper_summary.total_return_pct > live_summary.total_return_pct,
            "return_difference": round(paper_summary.total_return_pct - live_summary.total_return_pct, 2),
            "sharpe_difference": round(paper_summary.sharpe_ratio - live_summary.sharpe_ratio, 2),
            "note": "Paper trading results are simulated and may not reflect real market conditions"
        }
    }
