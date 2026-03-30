"""
Tests for Performance Attestor — metric computation, attestation cycle, error handling.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── Metric Computation ─────────────────────────────────────────

def test_compute_sharpe_positive():
    from cron.performance_attestor import compute_sharpe
    returns = [0.01, 0.02, -0.005, 0.015, 0.008, 0.012, -0.003, 0.01]
    sharpe = compute_sharpe(returns)
    assert sharpe > 0
    assert isinstance(sharpe, float)


def test_compute_sharpe_empty():
    from cron.performance_attestor import compute_sharpe
    assert compute_sharpe([]) == 0.0
    assert compute_sharpe([0.01]) == 0.0


def test_compute_sharpe_flat():
    from cron.performance_attestor import compute_sharpe
    assert compute_sharpe([0.01, 0.01, 0.01, 0.01]) == 0.0


def test_compute_win_rate():
    from cron.performance_attestor import compute_win_rate
    assert compute_win_rate([0.01, -0.02, 0.03, 0.005]) == 75.0
    assert compute_win_rate([]) == 0.0
    assert compute_win_rate([-0.01, -0.02]) == 0.0
    assert compute_win_rate([0.01, 0.02]) == 100.0


def test_compute_max_drawdown():
    from cron.performance_attestor import compute_max_drawdown
    curve = [100, 110, 105, 115, 100, 120]
    dd = compute_max_drawdown(curve)
    assert dd > 0
    assert dd == pytest.approx(13.04, abs=0.1)  # 115→100 = 13.04%
    assert compute_max_drawdown([]) == 0.0
    assert compute_max_drawdown([100]) == 0.0


def test_compute_monthly_pnl():
    from cron.performance_attestor import compute_monthly_pnl
    curve = [100, 105, 110, 108, 112]
    pnl = compute_monthly_pnl(curve)
    assert pnl == pytest.approx(12.0, abs=0.1)
    assert compute_monthly_pnl([]) == 0.0


# ── Strategy Metrics Extraction ────────────────────────────────

@pytest.mark.asyncio
async def test_get_strategy_metrics_from_doc():
    from cron.performance_attestor import get_strategy_metrics
    doc = {
        "metrics": {
            "sharpe_ratio": 2.41,
            "win_rate": 67.5,
            "max_drawdown": -12.3,
            "equity_curve": [
                {"value": 10000}, {"value": 10500}, {"value": 10200},
                {"value": 10800}, {"value": 11000}, {"value": 10700},
            ],
        }
    }
    m = await get_strategy_metrics(doc)
    assert m["sharpe"] == 2.41
    assert m["win_rate"] == 67.5
    assert m["drawdown"] == 12.3
    assert isinstance(m["monthly_pnl"], float)


@pytest.mark.asyncio
async def test_get_strategy_metrics_empty():
    from cron.performance_attestor import get_strategy_metrics
    m = await get_strategy_metrics({})
    assert m["sharpe"] == 0.0
    assert m["win_rate"] == 0.0


# ── Attestation Cycle ──────────────────────────────────────────

fake_db = MagicMock()
fake_db.strategies = MagicMock()
fake_db.strategies.find = MagicMock()
fake_db.leaderboard_strategies = MagicMock()
fake_db.leaderboard_strategies.find = MagicMock()
fake_db.performance_attestations = MagicMock()
fake_db.performance_attestations.insert_one = AsyncMock()


@pytest.fixture
def setup_attestor_db():
    from cron import performance_attestor
    performance_attestor.init_db(fake_db)
    yield


@pytest.mark.asyncio
async def test_attestation_cycle_dry_run(setup_attestor_db):
    from cron.performance_attestor import run_attestation_cycle

    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[
        {"name": "BTC Momentum", "metrics": {"sharpe_ratio": 2.1, "win_rate": 65, "max_drawdown": -10, "equity_curve": [{"value": 100}, {"value": 110}]}},
        {"name": "ETH Reversion", "metrics": {"sharpe_ratio": 1.5, "win_rate": 55, "max_drawdown": -15, "equity_curve": [{"value": 100}, {"value": 105}]}},
    ])
    fake_db.strategies.find.return_value = mock_cursor

    mock_admin = MagicMock()
    mock_admin.broadcast_event = AsyncMock()
    with patch("services.admin_events_manager.admin_events_manager", mock_admin):
        result = await run_attestation_cycle(dry_run=True)

    assert result["strategies_processed"] == 2
    assert result["dry_run"] is True
    assert len(result["details"]) == 2
    assert result["details"][0]["status"] == "dry_run"
    assert result["details"][0]["metrics"]["sharpe"] == 2.1


@pytest.mark.asyncio
async def test_attestation_cycle_no_strategies(setup_attestor_db):
    from cron.performance_attestor import run_attestation_cycle

    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[])
    fake_db.strategies.find.return_value = mock_cursor
    fake_db.leaderboard_strategies.find.return_value = mock_cursor

    mock_admin = MagicMock()
    mock_admin.broadcast_event = AsyncMock()
    with patch("services.admin_events_manager.admin_events_manager", mock_admin):
        result = await run_attestation_cycle(dry_run=True)

    assert result["strategies_processed"] == 0


# ── Contract Manager — New Methods ─────────────────────────────

@pytest.mark.asyncio
async def test_get_strategy_performance_mock():
    import services.contract_manager as cm
    original = cm._get_contract
    cm._get_contract = lambda: None
    perf = await cm.get_strategy_performance(0)
    assert perf["on_chain"] is False
    assert perf["sharpe"] == 0
    cm._get_contract = original


@pytest.mark.asyncio
async def test_get_strategy_performance_with_contract():
    import services.contract_manager as cm
    mock_contract = MagicMock()
    mock_contract.functions.getStrategyPerformance.return_value.call.return_value = (241, 6750, 1230, -350, 1711234567)
    original = cm._get_contract
    cm._get_contract = lambda: mock_contract
    cm._cache.clear()

    perf = await cm.get_strategy_performance(0)
    assert perf["sharpe"] == 2.41
    assert perf["win_rate"] == 67.5
    assert perf["drawdown"] == 12.3
    assert perf["monthly_pnl"] == -3.5
    assert perf["on_chain"] is True

    cm._get_contract = original


@pytest.mark.asyncio
async def test_get_contract_version_mock():
    import services.contract_manager as cm
    original = cm._get_contract
    cm._get_contract = lambda: None
    cm._cache.clear()
    version = await cm.get_contract_version()
    assert version == "2.0-performance-attestation"
    cm._get_contract = original


@pytest.mark.asyncio
async def test_update_strategy_performance_no_config():
    import services.contract_manager as cm
    original = cm._get_contract
    cm._get_contract = lambda: None
    result = await cm.update_strategy_performance(0, 2.41, 67.5, 12.3, -3.5)
    assert result is None
    cm._get_contract = original
