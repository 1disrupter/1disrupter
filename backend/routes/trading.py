"""
AlphaAI Trading Routes
Live trading, paper trading, agents, risk management, and execution.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
import random
from database import db, logger
from models.schemas import (
    AIAnalysisRequest, PaperTradeRequest, TradingAgent, MarketplaceAgent, Trade,
    RiskConfig, RiskAlert, MarketplaceAgentCreate
)
from services.trading_service import live_trading_service
from services.simulation_service import simulation_engine as sim_engine

router = APIRouter(prefix="/api")

# ============= LIVE TRADING API ENDPOINTS =============

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

@router.post("/trading/execute")
async def execute_trade(request: ExecuteTradeRequest):
    """Execute a trade (paper or live)"""
    try:
        # Validate user exists
        investor = await db.investors.find_one({"wallet_address": request.wallet_address})
        if not investor:
            raise HTTPException(status_code=404, detail="Wallet not registered")
        
        # Tier check: Free users cannot execute live trades
        if request.is_live:
            user = await db.users.find_one({"wallet_address": request.wallet_address}, {"_id": 0, "user_tier": 1, "is_pro": 1, "is_elite": 1})
            is_pro = (user and (user.get("is_pro") or user.get("is_elite") or user.get("user_tier") in ("pro", "elite"))) or investor.get("is_pro") or investor.get("is_elite")
            if not is_pro:
                raise HTTPException(status_code=403, detail="Live trading requires Pro or Elite subscription. Free users can only paper trade.")
        
        # Check paper balance for paper trades
        if not request.is_live:
            if investor.get("paper_balance", 0) < request.amount_usd:
                raise HTTPException(status_code=400, detail=f"Insufficient paper balance. Available: ${investor.get('paper_balance', 0):.2f}")
        
        # Get current price
        prices = await signal_service._fetch_live_prices()
        current_price = next((p["price"] for p in prices if p["symbol"] == request.symbol), None)
        
        if not current_price:
            raise HTTPException(status_code=400, detail=f"Could not fetch price for {request.symbol}")
        
        if request.is_live:
            # Prepare live swap transaction for frontend signing
            token_mapping = trading_service.get_token_mapping(request.symbol)
            
            if request.side == "BUY":
                token_in = "USDC"
                token_out = token_mapping["token"]
                amount_in = request.amount_usd
            else:
                token_in = token_mapping["token"]
                token_out = "USDC"
                amount_in = request.amount_usd / current_price
            
            tx_data = await trading_service.prepare_swap_transaction(
                wallet_address=request.wallet_address,
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                slippage=request.slippage_tolerance
            )
            
            if not tx_data.get("success"):
                raise HTTPException(status_code=500, detail=tx_data.get("error", "Transaction preparation failed"))
            
            # Create pending order
            order = TradeOrder(
                wallet_address=request.wallet_address,
                signal_id=request.signal_id,
                symbol=request.symbol,
                side=request.side,
                amount_usd=request.amount_usd,
                slippage_tolerance=request.slippage_tolerance,
                is_live=True,
                status="pending_signature"
            )
            
            await db.trades.insert_one(order.model_dump())
            
            return {
                "success": True,
                "trade_id": order.id,
                "status": "pending_signature",
                "is_live": True,
                "transaction": tx_data["transaction"],
                "network": tx_data["network"],
                "estimated_gas": tx_data["estimated_gas"],
                "current_price": current_price,
                "message": "Transaction prepared. Sign with your wallet to execute."
            }
        else:
            # Execute paper trade
            result = await trading_service.execute_paper_trade(
                wallet_address=request.wallet_address,
                symbol=request.symbol,
                side=request.side,
                amount_usd=request.amount_usd,
                current_price=current_price,
                signal_id=request.signal_id
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error", "Trade execution failed"))
            
            # Trigger copy trading for followers
            try:
                from services.copy_trading_service import process_trader_trade
                # Find user_id from wallet address
                user_record = await db.users.find_one({"wallet_address": request.wallet_address}, {"id": 1, "_id": 0})
                if user_record:
                    trade_data = {
                        "trade_id": result.get("trade_id", ""),
                        "symbol": request.symbol,
                        "side": request.side,
                        "amount_usd": request.amount_usd,
                        "executed_price": result.get("executed_price", current_price),
                        "is_live": False
                    }
                    asyncio.create_task(process_trader_trade(user_record["id"], trade_data))
            except Exception as copy_err:
                logger.warning(f"Copy trade trigger error (non-blocking): {copy_err}")
            
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trading/confirm")
async def confirm_live_trade(trade_id: str, tx_hash: str):
    """Confirm a live trade after blockchain confirmation"""
    try:
        trade = await db.trades.find_one({"id": trade_id})
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        if trade.get("status") != "pending_signature":
            raise HTTPException(status_code=400, detail=f"Trade already processed: {trade.get('status')}")
        
        # Update trade with confirmation
        await db.trades.update_one(
            {"id": trade_id},
            {"$set": {
                "status": "confirmed",
                "tx_hash": tx_hash,
                "executed_at": datetime.now(timezone.utc)
            }}
        )
        
        return {
            "success": True,
            "trade_id": trade_id,
            "tx_hash": tx_hash,
            "status": "confirmed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade confirmation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading/positions")
async def get_positions(wallet_address: str, is_live: Optional[bool] = None):
    """Get user's open positions"""
    positions = await trading_service.get_user_positions(wallet_address, is_live)
    return {"positions": positions, "count": len(positions)}

@router.get("/trading/history")
async def get_trade_history(
    wallet_address: str,
    is_live: Optional[bool] = None,
    limit: int = Query(default=50, le=200)
):
    """Get user's trade history"""
    trades = await trading_service.get_trade_history(wallet_address, is_live, limit)
    return {"trades": trades, "count": len(trades)}

@router.get("/trading/portfolio")
async def get_portfolio(wallet_address: str, is_live: bool = False):
    """Get portfolio summary with PnL"""
    summary = await trading_service.get_portfolio_summary(wallet_address, is_live)
    return summary

@router.post("/trading/close-position")
async def close_position(request: ClosePositionRequest):
    """Close an open position"""
    try:
        position = await db.positions.find_one({
            "id": request.position_id,
            "wallet_address": request.wallet_address
        })
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        # Get current price
        prices = await signal_service._fetch_live_prices()
        current_price = next((p["price"] for p in prices if p["symbol"] == position["symbol"]), position["current_price"])
        
        # Execute closing trade
        close_side = "SELL" if position["side"] == "LONG" else "BUY"
        
        result = await trading_service.execute_paper_trade(
            wallet_address=request.wallet_address,
            symbol=position["symbol"],
            side=close_side,
            amount_usd=position["amount"] * current_price,
            current_price=current_price
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Position close failed"))
        
        # Calculate realized PnL
        if position["side"] == "LONG":
            realized_pnl = (current_price - position["entry_price"]) * position["amount"]
        else:
            realized_pnl = (position["entry_price"] - current_price) * position["amount"]
        
        # Delete position
        await db.positions.delete_one({"id": request.position_id})
        
        return {
            "success": True,
            "position_id": request.position_id,
            "realized_pnl": round(realized_pnl, 2),
            "realized_pnl_percent": round((realized_pnl / position["amount_usd"]) * 100, 2),
            "close_price": current_price,
            "trade_id": result["trade_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Position close error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading/mode")
async def get_trading_mode(wallet_address: str):
    """Get user's trading mode preference"""
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        return {"mode": "simulation", "is_live_enabled": False}
    
    return {
        "mode": "live" if investor.get("is_live_trading", False) else "simulation",
        "is_live_enabled": investor.get("is_live_trading", False),
        "paper_balance": investor.get("paper_balance", 10000)
    }

@router.post("/trading/mode")
async def set_trading_mode(wallet_address: str, mode: str):
    """Set user's trading mode (simulation or live)"""
    if mode not in ["simulation", "live"]:
        raise HTTPException(status_code=400, detail="Mode must be 'simulation' or 'live'")
    
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Wallet not registered")
    
    is_live = mode == "live"
    
    await db.investors.update_one(
        {"wallet_address": wallet_address},
        {"$set": {"is_live_trading": is_live}}
    )
    
    return {
        "success": True,
        "mode": mode,
        "is_live_enabled": is_live,
        "message": f"Trading mode set to {mode}"
    }

@router.get("/trading/supported-tokens")
async def get_supported_tokens():
    """Get list of supported tokens for trading"""
    return {
        "tokens": [
            {"symbol": "BTC", "name": "Bitcoin", "wrapped": "WBTC", "supported": True},
            {"symbol": "ETH", "name": "Ethereum", "wrapped": "WETH", "supported": True},
            {"symbol": "SOL", "name": "Solana", "wrapped": None, "supported": False, "note": "SOL not available on Ethereum. Use as ETH proxy."},
            {"symbol": "USDC", "name": "USD Coin", "wrapped": None, "supported": True},
            {"symbol": "USDT", "name": "Tether", "wrapped": None, "supported": True},
        ],
        "network": trading_service.network,
        "dex": "Uniswap V3"
    }

# ============= AGENTS ROUTES =============
# New trading agents system is in routes/agents_api.py
# This legacy endpoint redirects to the new system

@router.get("/agents")
async def get_trading_agents():
    """Legacy agents endpoint — delegates to agents_api."""
    from routes.agents_api import list_agents
    return await list_agents()

# ============= TRADES ROUTES =============

@router.get("/trades", response_model=List[Trade])
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

@router.get("/risk/config")
async def get_risk_config():
    config = await db.risk_config.find_one({}, {"_id": 0})
    if not config:
        default_config = RiskConfig()
        doc = default_config.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.risk_config.insert_one(doc)
        return default_config
    return config

@router.put("/risk/config")
async def update_risk_config(config: RiskConfig):
    doc = config.model_dump()
    doc['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.risk_config.update_one({}, {"$set": doc}, upsert=True)
    await sim_engine.log_event("risk", "Risk configuration updated", agent_name="RiskAgent", details={"max_drawdown": config.max_drawdown, "max_daily_loss": config.max_daily_loss})
    return {"success": True, "config": doc}

@router.get("/risk/alerts", response_model=List[RiskAlert])
async def get_risk_alerts():
    alerts = await db.risk_alerts.find({"resolved": False}, {"_id": 0}).to_list(100)
    if not alerts:
        return []
    for alert in alerts:
        if isinstance(alert.get('timestamp'), str):
            alert['timestamp'] = datetime.fromisoformat(alert['timestamp'])
    return [RiskAlert(**a) for a in alerts]

@router.post("/risk/alerts/{alert_id}/resolve")
async def resolve_risk_alert(alert_id: str):
    result = await db.risk_alerts.update_one({"id": alert_id}, {"$set": {"resolved": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    await sim_engine.log_event("risk", f"Alert {alert_id} resolved", agent_name="RiskAgent")
    return {"success": True}

@router.get("/risk/portfolio-status")
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

@router.get("/capital/allocations")
async def get_capital_allocations():
    return await sim_engine.dynamic_capital_allocation()

@router.post("/capital/rebalance")
async def rebalance_capital():
    allocations = await sim_engine.dynamic_capital_allocation()
    return {"success": True, "message": f"Capital rebalanced across {len(allocations)} strategies", "allocations": allocations}

# ============= EXECUTION ROUTES =============

@router.get("/execution/stats")
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

@router.post("/execution/simulate")
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

@router.get("/marketplace/agents", response_model=List[MarketplaceAgent])
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

@router.post("/marketplace/agents", response_model=MarketplaceAgent)
async def submit_marketplace_agent(input: MarketplaceAgentCreate):
    agent = MarketplaceAgent(**input.model_dump())
    doc = agent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.marketplace_agents.insert_one(doc)
    return agent

# ============= AI ANALYSIS ROUTES =============

@router.post("/ai/analyze")
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

@router.post("/paper/trade")
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

@router.get("/paper/portfolio/{wallet_address}")
async def get_paper_portfolio(wallet_address: str):
    investor = await db.investors.find_one({"wallet_address": wallet_address}, {"_id": 0})
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    paper_trades = await db.trades.find({"is_paper": True}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    return {"paper_balance": investor.get('paper_balance', 10000), "paper_pnl": investor.get('paper_pnl', 0), "initial_balance": 10000, "return_percent": round((investor.get('paper_balance', 10000) - 10000) / 100, 2), "total_trades": len(paper_trades), "recent_trades": paper_trades[:10]}

@router.post("/paper/reset/{wallet_address}")
async def reset_paper_portfolio(wallet_address: str):
    await db.investors.update_one({"wallet_address": wallet_address}, {"$set": {"paper_balance": 10000, "paper_pnl": 0}})
    return {"success": True, "message": "Paper portfolio reset to $10,000"}

@router.post("/investors/toggle-paper-trading/{wallet_address}")
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
