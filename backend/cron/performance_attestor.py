"""
Performance Attestor — computes strategy metrics and writes them on-chain.
Designed to be called periodically (e.g. every 24h) or triggered via admin API.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("AlphaAI.PerformanceAttestor")

db = None


def init_db(database):
    global db
    db = database


# ── Metric Computation ─────────────────────────────────────────

def compute_sharpe(returns: list[float], risk_free: float = 0.0) -> float:
    """Compute annualized Sharpe ratio from a list of period returns."""
    if not returns or len(returns) < 2:
        return 0.0
    import statistics
    mean = statistics.mean(returns) - risk_free
    std = statistics.stdev(returns)
    if std == 0:
        return 0.0
    return round(mean / std * (252 ** 0.5), 2)  # annualized


def compute_win_rate(returns: list[float]) -> float:
    """Percentage of positive returns."""
    if not returns:
        return 0.0
    wins = sum(1 for r in returns if r > 0)
    return round(wins / len(returns) * 100, 2)


def compute_max_drawdown(equity_curve: list[float]) -> float:
    """Max drawdown as a positive percentage."""
    if not equity_curve or len(equity_curve) < 2:
        return 0.0
    peak = equity_curve[0]
    max_dd = 0.0
    for val in equity_curve:
        if val > peak:
            peak = val
        dd = (peak - val) / peak * 100 if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
    return round(max_dd, 2)


def compute_monthly_pnl(equity_curve: list[float]) -> float:
    """Latest month PnL as percentage. Uses last 30 data points as proxy."""
    if not equity_curve or len(equity_curve) < 2:
        return 0.0
    lookback = min(30, len(equity_curve))
    start = equity_curve[-lookback]
    end = equity_curve[-1]
    if start == 0:
        return 0.0
    return round((end - start) / start * 100, 2)


# ── Strategy Data Extraction ──────────────────────────────────

async def get_strategy_metrics(strategy_doc: dict) -> dict:
    """Extract metrics from a strategy document in the DB."""
    metrics = strategy_doc.get("metrics", {})
    equity = metrics.get("equity_curve", [])
    equity_values = [pt.get("value", pt) if isinstance(pt, dict) else pt for pt in equity]

    # Try to extract returns from equity curve
    returns = []
    for i in range(1, len(equity_values)):
        if equity_values[i - 1] != 0:
            ret = (equity_values[i] - equity_values[i - 1]) / equity_values[i - 1]
            returns.append(ret)

    # Read from nested metrics first, then top-level fields
    sharpe = metrics.get("sharpe_ratio") or strategy_doc.get("sharpe_ratio") or compute_sharpe(returns)
    win_rate = metrics.get("win_rate") or strategy_doc.get("win_rate") or compute_win_rate(returns)
    drawdown = abs(metrics.get("max_drawdown") or strategy_doc.get("max_drawdown") or compute_max_drawdown(equity_values))
    monthly_pnl = compute_monthly_pnl(equity_values) if equity_values else (strategy_doc.get("total_return", 0) / max(1, 12))

    return {
        "sharpe": float(sharpe) if sharpe else 0.0,
        "win_rate": float(win_rate) if win_rate else 0.0,
        "drawdown": float(drawdown) if drawdown else 0.0,
        "monthly_pnl": round(float(monthly_pnl), 2),
    }


# ── Main Attestation Cycle ─────────────────────────────────────

async def run_attestation_cycle(dry_run: bool = False) -> dict:
    """
    Compute metrics for all strategies and write them on-chain.
    Returns summary of results.
    """
    from services.contract_manager import (
        update_strategy_performance,
        is_live,
        CONTRACT_ADDRESS,
    )
    from services.admin_events_manager import admin_events_manager

    results = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "strategies_processed": 0,
        "strategies_updated": 0,
        "strategies_failed": 0,
        "dry_run": dry_run,
        "details": [],
    }

    # Fetch all strategies from DB
    strategies = await db.strategies.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)

    if not strategies:
        # Fallback: try leaderboard strategies which have actual metrics
        strategies = await db.leaderboard_strategies.find(
            {}, {"_id": 0}
        ).to_list(100) if db is not None else []

    contract_live = is_live() and not dry_run

    for idx, strat in enumerate(strategies):
        strat_name = strat.get("name", f"Strategy #{idx}")

        try:
            metrics = await get_strategy_metrics(strat)
            detail = {
                "strategy_id": idx,
                "name": strat_name,
                "metrics": metrics,
                "tx_hash": None,
                "status": "computed",
            }

            if contract_live:
                tx_result = await update_strategy_performance(
                    idx,
                    metrics["sharpe"],
                    metrics["win_rate"],
                    metrics["drawdown"],
                    metrics["monthly_pnl"],
                )
                if tx_result:
                    detail["tx_hash"] = tx_result["tx_hash"]
                    detail["status"] = "attested"
                    results["strategies_updated"] += 1
                else:
                    detail["status"] = "write_failed"
                    results["strategies_failed"] += 1
            else:
                detail["status"] = "dry_run" if dry_run else "no_contract"

            results["details"].append(detail)
            results["strategies_processed"] += 1

        except Exception as e:
            logger.error(f"Attestation failed for {strat_name}: {e}")
            results["details"].append({
                "strategy_id": idx,
                "name": strat_name,
                "status": "error",
                "error": str(e),
            })
            results["strategies_failed"] += 1

    results["completed_at"] = datetime.now(timezone.utc).isoformat()

    # Broadcast admin event
    try:
        await admin_events_manager.broadcast_event({
            "type": "performance_attestation_complete",
            "timestamp": results["completed_at"],
            "metadata": {
                "processed": results["strategies_processed"],
                "updated": results["strategies_updated"],
                "failed": results["strategies_failed"],
                "dry_run": dry_run,
            },
        })
    except Exception:
        pass

    # Store attestation record in DB
    if db is not None:
        await db.performance_attestations.insert_one({
            "timestamp": datetime.now(timezone.utc),
            "strategies_processed": results["strategies_processed"],
            "strategies_updated": results["strategies_updated"],
            "strategies_failed": results["strategies_failed"],
            "dry_run": dry_run,
            "details": results["details"],
        })

    logger.info(
        f"Attestation cycle complete: {results['strategies_processed']} processed, "
        f"{results['strategies_updated']} attested, {results['strategies_failed']} failed"
    )

    return results
