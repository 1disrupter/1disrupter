"""
AlphaAI Event Agent Routes
Event-driven agent system for automated market monitoring and response.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import random
from database import db, EMERGENT_LLM_KEY, logger
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/api")

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

@router.get("/agents/event-agents")
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

@router.post("/agents/event-agents/toggle/{agent_id}")
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

@router.post("/events/simulate")
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

@router.get("/dashboards/investor-balances")
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

@router.get("/dashboards/strategy-allocation")
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

@router.get("/events/recent")
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

@router.get("/integration/config")
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

@router.get("/export/comprehensive-pdf")
