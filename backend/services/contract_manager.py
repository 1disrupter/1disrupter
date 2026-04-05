"""
AlphaAI Contract Manager — Pure mock stub for SaaS-only deployment.
No Web3/blockchain dependencies. All helpers return mock/empty data.
When blockchain support is needed (Phase 3), restore web3 integration.
"""
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger("AlphaAI.ContractManager")

CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS_SEPOLIA", "")
CHAIN_ID = 11155111
EXPLORER_URL = "https://sepolia.etherscan.io"


def is_configured():
    return bool(CONTRACT_ADDRESS)


def is_live():
    return False


async def get_contract_status():
    return {
        "contract_address": CONTRACT_ADDRESS or None,
        "network": "sepolia",
        "chain_id": CHAIN_ID,
        "deployed": bool(CONTRACT_ADDRESS),
        "verified": False,
        "deployer": None,
        "deployment_tx": None,
        "deployment_block": None,
        "deployed_at": None,
        "verified_at": None,
        "explorer_url": f"{EXPLORER_URL}/address/{CONTRACT_ADDRESS}" if CONTRACT_ADDRESS else None,
        "rpc_connected": False,
        "latest_block": None,
        "health": "mock_mode",
        "abi_loaded": False,
        "abi_functions": 0,
    }


async def get_strategy(strategy_id: int):
    return {"name": f"Strategy #{strategy_id}", "allocated_wei": 0, "active": False, "on_chain": False}


async def get_strategy_count():
    return 0


async def get_investor_balance(address: str):
    return {"balance_wei": 0, "on_chain": False}


async def get_owner():
    return None


async def is_strategy_registered(strategy_id: int):
    return False


async def get_strategy_performance(strategy_id: int):
    return {"sharpe": 0, "win_rate": 0, "drawdown": 0, "monthly_pnl": 0, "timestamp": 0, "on_chain": False}


async def get_contract_version():
    return "2.0-mock-saas-only"


async def update_strategy_performance(strategy_id: int, sharpe: float, win_rate: float, drawdown: float, monthly_pnl: float):
    logger.info("update_strategy_performance called in mock mode — no-op")
    return None
