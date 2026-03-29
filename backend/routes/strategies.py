"""
AlphaAI Strategy & Agent Routes
Strategy lab, trading modes, agent management, and AI reports.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
import random
from database import db, EMERGENT_LLM_KEY, logger
from models.schemas import StrategyGenerateRequest, BacktestRequest
from services.signal_service import signal_service
from services.trading_service import live_trading_service
from services.simulation_service import simulation_engine as sim_engine
from services.market_data import calculate_sharpe_ratio
from models.schemas import StrategyGenerateRequest, BacktestRequest, Strategy
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/api")

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

@router.get("/reports/weekly")
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

@router.get("/reports/history")
async def get_report_history(limit: int = 10):
    """Get historical reports"""
    reports = await db.reports.find({}, {"_id": 0}).sort("generated_at", -1).to_list(limit)
    return reports

@router.post("/simulation/switch-mode")
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

@router.post("/agents/add")
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

@router.post("/strategies/add-batch")
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

@router.post("/lab/auto-deploy-top")
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

@router.get("/lab/strategies")
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

@router.post("/lab/strategies/generate")
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

class BacktestBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 10000.0

@router.post("/lab/strategies/{strategy_id}/backtest")
async def backtest_strategy(strategy_id: str, request: BacktestBody):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    from services.market_data import get_ohlc
    from services.backtest_engine import run_backtest

    asset = strategy.get("parameters", {}).get("asset", "BTC")
    candles = await get_ohlc(asset=asset, days=365)
    backtest_results = run_backtest(
        candles=candles,
        strategy_type=strategy.get("type", "momentum"),
        initial_capital=request.initial_capital,
        parameters=strategy.get("parameters", {}),
    )
    backtest_results["period"] = f"{request.start_date or backtest_results['period'].split(' to ')[0]} to {request.end_date or backtest_results['period'].split(' to ')[-1]}"

    await db.strategies.update_one({"id": strategy_id}, {"$set": {
        "status": "backtested",
        "backtest_results": {k: v for k, v in backtest_results.items() if k != "equity_curve"},
        "sharpe_ratio": backtest_results["sharpe_ratio"],
        "total_return": backtest_results["total_return"],
        "max_drawdown": backtest_results["max_drawdown"],
        "win_rate": backtest_results["win_rate"],
    }})

    await sim_engine.log_event("strategy", f"Backtest complete for '{strategy['name']}': Return {backtest_results['total_return']}%, Sharpe {backtest_results['sharpe_ratio']}", strategy_id=strategy_id, agent_name="BacktestingAgent", details={k: v for k, v in backtest_results.items() if k != "equity_curve"})
    await sim_engine.log_agent_interaction("BacktestingAgent", "SandboxValidationAgent", "data", {"strategy_id": strategy_id, "sharpe": backtest_results["sharpe_ratio"], "return": backtest_results["total_return"]})

    return {"success": True, "strategy_id": strategy_id, "results": backtest_results}

@router.post("/lab/strategies/{strategy_id}/sandbox")
async def start_sandbox_testing(strategy_id: str):
    strategy = await db.strategies.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    sandbox_results = {"started_at": datetime.now(timezone.utc).isoformat(), "paper_trades": 0, "paper_pnl": 0, "status": "running"}
    await db.strategies.update_one({"id": strategy_id}, {"$set": {"status": "sandbox", "sandbox_results": sandbox_results, "is_active": True}})
    
    await sim_engine.log_event("strategy", f"Sandbox testing started for '{strategy['name']}'", strategy_id=strategy_id, agent_name="SandboxValidationAgent")
    await sim_engine.log_agent_interaction("SandboxValidationAgent", "StrategyRankingAgent", "data", {"strategy_id": strategy_id, "action": "sandbox_started"})
    
    return {"success": True, "message": "Sandbox testing started", "strategy_id": strategy_id}

@router.post("/lab/strategies/{strategy_id}/deploy")
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

@router.post("/lab/strategies/{strategy_id}/stop")
async def stop_strategy(strategy_id: str):
    result = await db.strategies.update_one({"id": strategy_id}, {"$set": {"status": "stopped", "is_active": False, "capital_allocated": 0}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    await sim_engine.log_event("strategy", f"Strategy stopped", strategy_id=strategy_id, agent_name="LiveDeploymentAgent")
    return {"success": True, "message": "Strategy stopped"}

@router.get("/lab/rankings")
async def get_strategy_rankings():
    strategies = await db.strategies.find({"status": {"$in": ["live", "sandbox", "backtested"]}}, {"_id": 0}).to_list(100)
    ranked = sorted(strategies, key=lambda x: (x.get('sharpe_ratio', 0), x.get('total_return', 0)), reverse=True)
    
    for i, s in enumerate(ranked):
        await db.strategies.update_one({"id": s['id']}, {"$set": {"rank": i + 1}})
    
    return [{"rank": i+1, "id": s.get('id'), "name": s.get('name'), "type": s.get('type'), "status": s.get('status'), "sharpe_ratio": s.get('sharpe_ratio', 0), "total_return": s.get('total_return', 0), "max_drawdown": s.get('max_drawdown', 0), "win_rate": s.get('win_rate', 0), "capital_allocated": s.get('capital_allocated', 0)} for i, s in enumerate(ranked)]

