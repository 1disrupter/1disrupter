"""
AlphaAI Contract Manager — Web3 integration with caching and graceful fallback.
Reads contract address + ABI, creates Web3 client, exposes helper methods.
Falls back to mock data when Web3 is unavailable (no RPC configured or contract not deployed).
"""
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger("AlphaAI.ContractManager")

# ── Config ─────────────────────────────────────────────────────

CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS_SEPOLIA", "")
SEPOLIA_RPC_URL = os.environ.get("SEPOLIA_RPC_URL", "")
CHAIN_ID = 11155111
EXPLORER_URL = "https://sepolia.etherscan.io"

# Try loading deployment artifact from Hardhat output
DEPLOYMENT_ARTIFACT_PATH = Path(__file__).parent.parent.parent / "contracts" / "deployments" / "sepolia" / "AlphaAIManager.json"

# ABI path
ABI_MODULE_PATH = Path(__file__).parent.parent / "web3" / "contract_abi.py"


def _load_abi():
    """Load ABI from the contract_abi module."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("contract_abi", str(ABI_MODULE_PATH))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.ALPHA_AI_MANAGER_ABI
    except Exception as e:
        logger.error(f"Failed to load ABI: {e}")
        return []


def _load_deployment_info():
    """Load deployment artifact if available."""
    if DEPLOYMENT_ARTIFACT_PATH.exists():
        try:
            with open(DEPLOYMENT_ARTIFACT_PATH) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load deployment artifact: {e}")
    return None


ABI = _load_abi()
DEPLOYMENT_INFO = _load_deployment_info()

# Resolve contract address (env > deployment artifact > contract_abi module)
if not CONTRACT_ADDRESS and DEPLOYMENT_INFO:
    CONTRACT_ADDRESS = DEPLOYMENT_INFO.get("address", "")
if not CONTRACT_ADDRESS:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("contract_abi", str(ABI_MODULE_PATH))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        CONTRACT_ADDRESS = mod.CONTRACT_ADDRESSES.get("sepolia") or ""
    except Exception:
        pass


# ── Web3 Client ────────────────────────────────────────────────

_w3 = None
_contract = None


def _get_web3():
    global _w3
    if _w3 is not None:
        return _w3
    if not SEPOLIA_RPC_URL:
        return None
    try:
        from web3 import Web3
        _w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL, request_kwargs={"timeout": 10}))
        if _w3.is_connected():
            logger.info("Web3 connected to Sepolia RPC")
            return _w3
        else:
            logger.warning("Web3 failed to connect to Sepolia RPC")
            _w3 = None
            return None
    except ImportError:
        logger.warning("web3 package not installed — using mock mode")
        return None
    except Exception as e:
        logger.error(f"Web3 init error: {e}")
        _w3 = None
        return None


def _get_contract():
    global _contract
    if _contract is not None:
        return _contract
    w3 = _get_web3()
    if not w3 or not CONTRACT_ADDRESS or not ABI:
        return None
    try:
        from web3 import Web3
        _contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=ABI,
        )
        return _contract
    except Exception as e:
        logger.error(f"Contract init error: {e}")
        return None


# ── TTL Cache ──────────────────────────────────────────────────

_cache = {}
CACHE_TTL = 30  # seconds


def _cache_get(key):
    entry = _cache.get(key)
    if entry:
        ts, val = entry
        if (datetime.now(timezone.utc) - ts).total_seconds() < CACHE_TTL:
            return val
        del _cache[key]
    return None


def _cache_set(key, val):
    _cache[key] = (datetime.now(timezone.utc), val)


# ── Public Helpers ─────────────────────────────────────────────

def is_configured():
    """Check if contract deployment is configured."""
    return bool(CONTRACT_ADDRESS and ABI)


def is_live():
    """Check if we can talk to the contract on-chain."""
    return _get_contract() is not None


async def get_contract_status():
    """Get full contract status for admin panel."""
    deployment = DEPLOYMENT_INFO or {}
    w3 = _get_web3()
    block_number = None
    health = "not_configured"

    if w3:
        try:
            block_number = w3.eth.block_number
            health = "ok"
        except Exception as e:
            health = f"rpc_error: {str(e)[:80]}"
    elif CONTRACT_ADDRESS:
        health = "no_rpc"

    return {
        "contract_address": CONTRACT_ADDRESS or None,
        "network": "sepolia",
        "chain_id": CHAIN_ID,
        "deployed": bool(CONTRACT_ADDRESS),
        "verified": deployment.get("verified", False),
        "deployer": deployment.get("deployer"),
        "deployment_tx": deployment.get("txHash"),
        "deployment_block": deployment.get("blockNumber"),
        "deployed_at": deployment.get("deployedAt"),
        "verified_at": deployment.get("verifiedAt"),
        "explorer_url": f"{EXPLORER_URL}/address/{CONTRACT_ADDRESS}" if CONTRACT_ADDRESS else None,
        "rpc_connected": w3.is_connected() if w3 else False,
        "latest_block": block_number,
        "health": health,
        "abi_loaded": len(ABI) > 0,
        "abi_functions": len([a for a in ABI if a.get("type") == "function"]),
    }


async def get_strategy(strategy_id: int):
    """Read strategy from contract. Returns (name, allocated, active) or mock."""
    cache_key = f"strategy_{strategy_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    contract = _get_contract()
    if contract:
        try:
            name, allocated, active = contract.functions.getStrategy(strategy_id).call()
            result = {"name": name, "allocated_wei": allocated, "active": active, "on_chain": True}
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"getStrategy({strategy_id}) error: {e}")

    # Mock fallback
    return {"name": f"Strategy #{strategy_id}", "allocated_wei": 0, "active": False, "on_chain": False}


async def get_strategy_count():
    """Read strategyCount from contract."""
    cached = _cache_get("strategy_count")
    if cached is not None:
        return cached

    contract = _get_contract()
    if contract:
        try:
            count = contract.functions.strategyCount().call()
            _cache_set("strategy_count", count)
            return count
        except Exception as e:
            logger.error(f"strategyCount() error: {e}")

    return 0


async def get_investor_balance(address: str):
    """Read investor balance from contract."""
    cache_key = f"balance_{address}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    contract = _get_contract()
    if contract:
        try:
            from web3 import Web3
            balance = contract.functions.getInvestorBalance(Web3.to_checksum_address(address)).call()
            result = {"balance_wei": balance, "on_chain": True}
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"getInvestorBalance({address}) error: {e}")

    return {"balance_wei": 0, "on_chain": False}


async def get_owner():
    """Read contract owner."""
    cached = _cache_get("owner")
    if cached is not None:
        return cached

    contract = _get_contract()
    if contract:
        try:
            owner = contract.functions.owner().call()
            _cache_set("owner", owner)
            return owner
        except Exception as e:
            logger.error(f"owner() error: {e}")

    return DEPLOYMENT_INFO.get("deployer") if DEPLOYMENT_INFO else None


async def is_strategy_registered(strategy_id: int):
    """Check if strategy exists on-chain."""
    result = await get_strategy(strategy_id)
    return result.get("active", False)


async def get_strategy_performance(strategy_id: int):
    """Read strategy performance attestation from contract."""
    cache_key = f"perf_{strategy_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    contract = _get_contract()
    if contract:
        try:
            perf = contract.functions.getStrategyPerformance(strategy_id).call()
            result = {
                "sharpe": perf[0] / 100,
                "win_rate": perf[1] / 100,
                "drawdown": perf[2] / 100,
                "monthly_pnl": perf[3] / 100,
                "timestamp": perf[4],
                "on_chain": True,
            }
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"getStrategyPerformance({strategy_id}) error: {e}")

    return {"sharpe": 0, "win_rate": 0, "drawdown": 0, "monthly_pnl": 0, "timestamp": 0, "on_chain": False}


async def get_contract_version():
    """Read contract version string."""
    cached = _cache_get("version")
    if cached is not None:
        return cached

    contract = _get_contract()
    if contract:
        try:
            version = contract.functions.contractVersion().call()
            _cache_set("version", version)
            return version
        except Exception as e:
            logger.error(f"contractVersion() error: {e}")

    return "2.0-performance-attestation"


async def update_strategy_performance(
    strategy_id: int, sharpe: float, win_rate: float, drawdown: float, monthly_pnl: float
):
    """
    Write strategy performance to chain (owner-only transaction).
    Returns tx hash on success, None on failure.
    Requires DEPLOYER_PRIVATE_KEY in env for signing.
    """
    contract = _get_contract()
    w3 = _get_web3()
    private_key = os.environ.get("DEPLOYER_PRIVATE_KEY", "")

    if not contract or not w3 or not private_key:
        logger.warning("Cannot write performance: contract/web3/key not configured")
        return None

    try:
        import time
        from web3 import Web3

        # Scale values to int (x100)
        sharpe_int = int(round(sharpe * 100))
        win_rate_int = int(round(win_rate * 100))
        drawdown_int = int(round(drawdown * 100))
        pnl_int = int(round(monthly_pnl * 100))
        ts = int(time.time())

        account = w3.eth.account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address)

        tx = contract.functions.updateStrategyPerformance(
            strategy_id, sharpe_int, win_rate_int, drawdown_int, pnl_int, ts
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
            "chainId": CHAIN_ID,
        })

        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        logger.info(f"Performance updated on-chain for strategy {strategy_id}: tx={tx_hash.hex()}")

        # Invalidate cache
        _cache.pop(f"perf_{strategy_id}", None)

        return {
            "tx_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"],
            "gas_used": receipt["gasUsed"],
            "strategy_id": strategy_id,
            "timestamp": ts,
        }
    except Exception as e:
        logger.error(f"update_strategy_performance({strategy_id}) error: {e}")
        return None
