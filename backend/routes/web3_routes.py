"""
AlphaAI Web3 & Smart Contract Routes
Contract deployment, interaction, and blockchain integration.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
import random
from database import db, logger
from services.simulation_service import simulation_engine as sim_engine

# Load contract ABI from local file (avoid clash with web3 pip package)
import importlib.util
_abi_spec = importlib.util.spec_from_file_location("contract_abi", str(Path(__file__).parent.parent / "web3" / "contract_abi.py"))
_abi_mod = importlib.util.module_from_spec(_abi_spec)
_abi_spec.loader.exec_module(_abi_mod)
ALPHA_AI_ABI = _abi_mod.ALPHA_AI_MANAGER_ABI
SEPOLIA_CONFIG = _abi_mod.SEPOLIA_CONFIG
CONTRACT_ADDRESSES = _abi_mod.CONTRACT_ADDRESSES

CONTRACT_ADDRESS = CONTRACT_ADDRESSES.get("sepolia")
SEPOLIA_RPC = SEPOLIA_CONFIG.get("rpc_url", "https://sepolia.infura.io/v3/")

router = APIRouter(prefix="/api")

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

@router.get("/contract/info")
async def get_contract_info():
    """Get smart contract deployment information"""
    from services.contract_manager import get_contract_status, CONTRACT_ADDRESS as cm_address
    
    # Try live status first
    status = await get_contract_status()
    
    if status.get("deployed"):
        return {
            "deployed": True,
            "network": "sepolia",
            "chain_id": 11155111,
            "contract_address": status["contract_address"],
            "explorer_url": status["explorer_url"],
            "verified": status.get("verified", False),
            "deployer": status.get("deployer"),
            "deployed_at": status.get("deployed_at"),
            "rpc_connected": status.get("rpc_connected", False),
            "health": status.get("health"),
            "contract_source": "/api/contract/source",
        }
    
    # Fallback — not yet deployed
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    if contract_info and contract_info.get("deployed"):
        return contract_info
    
    return {
        "deployed": False,
        "network": "sepolia",
        "chain_id": 11155111,
        "contract_address": cm_address or CONTRACT_ADDRESS,
        "explorer_url": "https://sepolia.etherscan.io",
        "rpc_url": SEPOLIA_RPC,
        "contract_source": "/api/contract/source",
        "message": "Contract ready for deployment to Sepolia testnet",
    }

@router.get("/contract/source")
async def get_contract_source():
    """Get the Solidity source code for the AlphaAI Manager contract"""
    contract_path = Path(__file__).parent.parent / "contracts" / "AlphaAIManager.sol"
    
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

@router.post("/contract/register")
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

@router.get("/contract/balance/{wallet_address}")
async def get_on_chain_balance(wallet_address: str):
    """Get investor's on-chain balance from the smart contract"""
    from services.contract_manager import get_investor_balance, is_live, CONTRACT_ADDRESS as cm_addr
    
    if is_live():
        result = await get_investor_balance(wallet_address)
        return {
            "wallet_address": wallet_address,
            "on_chain_balance_wei": result["balance_wei"],
            "on_chain_balance_eth": round(result["balance_wei"] / 10**18, 6),
            "contract_address": cm_addr,
            "contract_deployed": True,
            "on_chain": result["on_chain"],
        }
    
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    if not contract_info or not contract_info.get('deployed'):
        return {
            "wallet_address": wallet_address,
            "on_chain_balance": 0,
            "on_chain_balance_eth": 0,
            "contract_deployed": False,
            "message": "Contract not yet deployed. Using simulated balance."
        }
    
    simulated_balance = random.uniform(0, 5) * 10**18
    return {
        "wallet_address": wallet_address,
        "on_chain_balance_wei": int(simulated_balance),
        "on_chain_balance_eth": round(simulated_balance / 10**18, 6),
        "contract_address": contract_info.get('contract_address'),
        "contract_deployed": True,
        "on_chain": False,
    }

@router.get("/contract/strategies")
async def get_on_chain_strategies():
    """Get strategies registered on-chain"""
    from services.contract_manager import get_strategy, get_strategy_count, is_live, CONTRACT_ADDRESS as cm_addr
    
    if is_live():
        count = await get_strategy_count()
        strats = []
        for i in range(min(count, 20)):
            s = await get_strategy(i)
            strats.append({"id": i, "name": s["name"], "allocated_wei": s["allocated_wei"], "allocated_eth": round(s["allocated_wei"] / 10**18, 4), "active": s["active"]})
        return {
            "contract_deployed": True,
            "contract_address": cm_addr,
            "strategy_count": count,
            "strategies": strats,
            "on_chain": True,
        }
    
    contract_info = await db.contract_info.find_one({}, {"_id": 0})
    if not contract_info or not contract_info.get('deployed'):
        strategies = await db.strategies.find({"status": "live"}, {"_id": 0}).to_list(10)
        return {
            "contract_deployed": False,
            "strategies": [{"id": i, "name": s.get('name'), "allocated": s.get('capital_allocated', 0), "active": True} for i, s in enumerate(strategies)],
            "message": "Strategies from simulation. Deploy contract for on-chain data."
        }
    
    return {
        "contract_deployed": True,
        "contract_address": contract_info.get('contract_address'),
        "strategy_count": 0,
        "strategies": [],
        "on_chain": False,
        "message": "Contract deployed but RPC not configured. Add SEPOLIA_RPC_URL to .env.",
    }

@router.post("/contract/prepare-deposit")
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

@router.post("/contract/prepare-withdraw")
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

@router.get("/contract/events")
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

@router.get("/contract/deployment-guide")
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

@router.get("/contract/abi")
async def get_contract_abi():
    """Get the full contract ABI for frontend integration"""
    return {
        "contract_name": "AlphaAIManager",
        "abi": ALPHA_AI_ABI,
        "network": "sepolia",
        "chain_id": 11155111
    }

# ============= EVENT-DRIVEN AGENT SYSTEM =============
