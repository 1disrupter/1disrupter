"""
AlphaAI Simulation Engine
Backtesting and paper trading simulation with multi-agent strategies.
"""
import uuid
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from database import db

from models.schemas import Trade, SimulationConfig

logger = logging.getLogger("AlphaAI")

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


simulation_engine = SimulationEngine()
