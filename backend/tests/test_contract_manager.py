"""
Tests for Contract Manager — ABI loading, status, helpers, caching.
"""
import pytest
import json
import time
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path


@pytest.fixture(autouse=True)
def clear_cache():
    from services.contract_manager import _cache
    _cache.clear()
    yield
    _cache.clear()


# ── ABI & Config ───────────────────────────────────────────────

def test_abi_loaded():
    from services.contract_manager import ABI
    assert isinstance(ABI, list)
    assert len(ABI) > 0
    fn_names = [a.get("name") for a in ABI if a.get("type") == "function"]
    assert "addStrategy" in fn_names
    assert "getStrategy" in fn_names
    assert "getInvestorBalance" in fn_names


def test_is_configured_no_address():
    import services.contract_manager as cm
    original = cm.CONTRACT_ADDRESS
    cm.CONTRACT_ADDRESS = ""
    assert cm.is_configured() is False
    cm.CONTRACT_ADDRESS = original


def test_is_configured_with_address():
    import services.contract_manager as cm
    original = cm.CONTRACT_ADDRESS
    cm.CONTRACT_ADDRESS = "0x1234567890abcdef1234567890abcdef12345678"
    assert cm.is_configured() is True
    cm.CONTRACT_ADDRESS = original


# ── Status ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_contract_status_no_rpc():
    import services.contract_manager as cm
    original_addr = cm.CONTRACT_ADDRESS
    cm.CONTRACT_ADDRESS = ""
    status = await cm.get_contract_status()
    assert status["network"] == "sepolia"
    assert status["chain_id"] == 11155111
    assert "health" in status
    assert "abi_loaded" in status
    cm.CONTRACT_ADDRESS = original_addr


@pytest.mark.asyncio
async def test_get_contract_status_with_address():
    import services.contract_manager as cm
    original = cm.CONTRACT_ADDRESS
    cm.CONTRACT_ADDRESS = "0xAbCdEf0123456789AbCdEf0123456789AbCdEf01"
    status = await cm.get_contract_status()
    assert status["deployed"] is True
    assert status["contract_address"] == "0xAbCdEf0123456789AbCdEf0123456789AbCdEf01"
    cm.CONTRACT_ADDRESS = original


# ── Helpers (mock fallback) ────────────────────────────────────

@pytest.mark.asyncio
async def test_get_strategy_mock():
    import services.contract_manager as cm
    # With no contract connected, should return mock
    original_get = cm._get_contract
    cm._get_contract = lambda: None
    result = await cm.get_strategy(0)
    assert result["name"] == "Strategy #0"
    assert result["on_chain"] is False
    cm._get_contract = original_get


@pytest.mark.asyncio
async def test_get_strategy_count_mock():
    import services.contract_manager as cm
    original_get = cm._get_contract
    cm._get_contract = lambda: None
    count = await cm.get_strategy_count()
    assert count == 0
    cm._get_contract = original_get


@pytest.mark.asyncio
async def test_get_investor_balance_mock():
    import services.contract_manager as cm
    original_get = cm._get_contract
    cm._get_contract = lambda: None
    result = await cm.get_investor_balance("0x0000000000000000000000000000000000000000")
    assert result["balance_wei"] == 0
    assert result["on_chain"] is False
    cm._get_contract = original_get


@pytest.mark.asyncio
async def test_is_strategy_registered_mock():
    import services.contract_manager as cm
    original_get = cm._get_contract
    cm._get_contract = lambda: None
    assert await cm.is_strategy_registered(999) is False
    cm._get_contract = original_get


@pytest.mark.asyncio
async def test_get_owner_mock():
    import services.contract_manager as cm
    original_get = cm._get_contract
    cm._get_contract = lambda: None
    owner = await cm.get_owner()
    # Should return deployer from DEPLOYMENT_INFO or None
    assert owner is None or isinstance(owner, str)
    cm._get_contract = original_get


# ── Caching ────────────────────────────────────────────────────

def test_cache_set_get():
    from services.contract_manager import _cache_set, _cache_get
    _cache_set("test_key", {"value": 42})
    result = _cache_get("test_key")
    assert result == {"value": 42}


def test_cache_miss():
    from services.contract_manager import _cache_get
    result = _cache_get("nonexistent_key")
    assert result is None


def test_cache_ttl_expiry():
    from services.contract_manager import _cache, _cache_set, _cache_get, CACHE_TTL
    from datetime import datetime, timezone, timedelta

    _cache_set("expire_test", "data")
    # Manually expire the entry
    ts, val = _cache["expire_test"]
    _cache["expire_test"] = (ts - timedelta(seconds=CACHE_TTL + 1), val)
    result = _cache_get("expire_test")
    assert result is None


# ── Web3 Fallback ──────────────────────────────────────────────

def test_get_web3_no_rpc():
    import services.contract_manager as cm
    original = cm.SEPOLIA_RPC_URL
    cm.SEPOLIA_RPC_URL = ""
    cm._w3 = None
    result = cm._get_web3()
    assert result is None
    cm.SEPOLIA_RPC_URL = original


def test_get_contract_no_web3():
    import services.contract_manager as cm
    cm._contract = None
    original_web3 = cm._get_web3
    cm._get_web3 = lambda: None
    result = cm._get_contract()
    assert result is None
    cm._get_web3 = original_web3


# ── With Mock Contract ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_strategy_with_contract():
    import services.contract_manager as cm

    mock_contract = MagicMock()
    mock_contract.functions.getStrategy.return_value.call.return_value = ("TestStrat", 1000000, True)
    original = cm._get_contract
    cm._get_contract = lambda: mock_contract

    result = await cm.get_strategy(0)
    assert result["name"] == "TestStrat"
    assert result["allocated_wei"] == 1000000
    assert result["active"] is True
    assert result["on_chain"] is True

    cm._get_contract = original


@pytest.mark.asyncio
async def test_get_strategy_count_with_contract():
    import services.contract_manager as cm

    mock_contract = MagicMock()
    mock_contract.functions.strategyCount.return_value.call.return_value = 3
    original = cm._get_contract
    cm._get_contract = lambda: mock_contract

    count = await cm.get_strategy_count()
    assert count == 3

    cm._get_contract = original


@pytest.mark.asyncio
async def test_get_investor_balance_with_contract():
    import services.contract_manager as cm

    mock_contract = MagicMock()
    mock_contract.functions.getInvestorBalance.return_value.call.return_value = 5000000000000000000
    original = cm._get_contract
    cm._get_contract = lambda: mock_contract

    result = await cm.get_investor_balance("0xAbCdEf0123456789AbCdEf0123456789AbCdEf01")
    assert result["balance_wei"] == 5000000000000000000
    assert result["on_chain"] is True

    cm._get_contract = original


# ── Error Handling ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_strategy_contract_error():
    import services.contract_manager as cm

    mock_contract = MagicMock()
    mock_contract.functions.getStrategy.return_value.call.side_effect = Exception("RPC timeout")
    original = cm._get_contract
    cm._get_contract = lambda: mock_contract

    result = await cm.get_strategy(0)
    assert result["on_chain"] is False  # Falls back to mock
    assert result["name"] == "Strategy #0"

    cm._get_contract = original
