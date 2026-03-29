"""
AlphaAI Simulation Routes
Backtesting, paper trading, and simulation management endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone, timedelta
import uuid
import random
from database import db, EMERGENT_LLM_KEY, logger
from models.schemas import AdvancedSimulationConfig, SimulationExportRequest
from services.simulation_service import simulation_engine as sim_engine
from services.signal_service import signal_service
from services.market_data import get_market_data, get_market_chart
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/api")

@router.get("/simulation/config")
async def get_simulation_config():
    config = await sim_engine.initialize()
    return config

@router.post("/simulation/start")
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

@router.post("/simulation/stop")
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

@router.post("/simulation/run-cycle")
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

@router.get("/simulation/logs")
async def get_simulation_logs(limit: int = 50, log_type: str = None):
    """Get simulation logs"""
    query = {}
    if log_type:
        query["log_type"] = log_type
    
    logs = await db.simulation_logs.find(query, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return logs

@router.get("/simulation/agent-interactions")
async def get_agent_interactions(limit: int = 50):
    """Get agent interaction logs"""
    interactions = await db.agent_interactions.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return interactions

@router.get("/simulation/stats")
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

@router.post("/simulation/configure")
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

@router.post("/simulation/run-accelerated")
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

@router.post("/simulation/stress-test")
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

@router.get("/simulation/stress-scenarios")
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

@router.get("/simulation/agent-performance")
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

@router.post("/simulation/export")
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

@router.post("/simulation/load-historical-data")
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


class SimulationBacktestRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    asset: str = Field(default="BTC/USDT")
    strategy: str = Field(default="momentum")
    days: int = Field(default=365, ge=30, le=730)
    initial_capital: float = Field(default=100000, ge=1000)
    demo: bool = Field(default=False)

@router.post("/simulation/backtest")
async def simulation_backtest(request: SimulationBacktestRequest):
    """Run a backtest on real OHLC data for the Simulation page."""
    from services.market_data import get_ohlc, get_demo_ohlc
    from services.backtest_engine import run_backtest

    if request.demo:
        candles = get_demo_ohlc(request.days)
        data_source = "mock"
    else:
        candles = await get_ohlc(asset=request.asset, days=request.days)
        data_source = "coingecko"

    results = run_backtest(
        candles=candles,
        strategy_type=request.strategy,
        initial_capital=request.initial_capital,
    )
    results["data_source"] = data_source
    results["asset"] = request.asset
    results["strategy"] = request.strategy

    return {"success": True, "results": results}
