"""
AlphaAI Backtest Engine
Computes real trading metrics from OHLC price data.
"""
import math
import logging
from typing import List, Dict

logger = logging.getLogger("AlphaAI")


def run_backtest(
    candles: List[Dict],
    strategy_type: str = "momentum",
    initial_capital: float = 100000,
    parameters: Dict = None,
) -> Dict:
    """Run a backtest over OHLC candles and return full metrics + equity curve."""
    if not candles or len(candles) < 10:
        return _empty_result(initial_capital)

    params = parameters or {}
    closes = [c["close"] for c in candles]

    if strategy_type == "momentum":
        signals = _momentum_signals(closes, params)
    elif strategy_type == "mean_reversion":
        signals = _mean_reversion_signals(closes, params)
    elif strategy_type == "breakout":
        signals = _breakout_signals(closes, params)
    else:
        signals = _momentum_signals(closes, params)

    return _simulate_trades(candles, signals, initial_capital)


# ── Strategy signal generators ─────────────────────────────────

def _momentum_signals(closes: List[float], params: Dict) -> List[int]:
    """1 = long, -1 = short, 0 = flat.  SMA crossover momentum."""
    fast = params.get("fast_period", 10)
    slow = params.get("slow_period", 30)
    signals = [0] * len(closes)
    for i in range(slow, len(closes)):
        fast_ma = sum(closes[i - fast:i]) / fast
        slow_ma = sum(closes[i - slow:i]) / slow
        signals[i] = 1 if fast_ma > slow_ma else -1
    return signals


def _mean_reversion_signals(closes: List[float], params: Dict) -> List[int]:
    """Trade when price deviates from moving average by z-score threshold."""
    lookback = params.get("lookback", 20)
    threshold = params.get("zscore_threshold", 1.5)
    signals = [0] * len(closes)
    for i in range(lookback, len(closes)):
        window = closes[i - lookback:i]
        mean = sum(window) / lookback
        std = (sum((x - mean) ** 2 for x in window) / lookback) ** 0.5
        if std == 0:
            continue
        z = (closes[i] - mean) / std
        if z < -threshold:
            signals[i] = 1   # oversold → buy
        elif z > threshold:
            signals[i] = -1  # overbought → sell
        else:
            signals[i] = 0
    return signals


def _breakout_signals(closes: List[float], params: Dict) -> List[int]:
    """Buy on new N-period high, sell on new N-period low."""
    lookback = params.get("lookback", 20)
    signals = [0] * len(closes)
    for i in range(lookback, len(closes)):
        window = closes[i - lookback:i]
        if closes[i] > max(window):
            signals[i] = 1
        elif closes[i] < min(window):
            signals[i] = -1
        else:
            signals[i] = signals[i - 1] if i > 0 else 0
    return signals


# ── Trade simulator ────────────────────────────────────────────

def _simulate_trades(
    candles: List[Dict],
    signals: List[int],
    initial_capital: float,
) -> Dict:
    capital = initial_capital
    position = 0
    entry_price = 0.0
    trades = []
    equity = [{"day": 0, "value": capital, "timestamp": candles[0]["timestamp"]}]
    peak = capital

    for i in range(1, len(candles)):
        price = candles[i]["close"]
        sig = signals[i] if i < len(signals) else 0
        prev_sig = signals[i - 1] if i - 1 < len(signals) else 0

        # Position change
        if sig != prev_sig:
            # Close current position
            if position != 0:
                pnl_pct = (price - entry_price) / entry_price * position
                trade_pnl = capital * 0.1 * pnl_pct  # 10% of capital per trade
                capital += trade_pnl
                trades.append({
                    "entry": entry_price,
                    "exit": price,
                    "side": "long" if position > 0 else "short",
                    "pnl": round(trade_pnl, 2),
                    "pnl_pct": round(pnl_pct * 100, 2),
                })
                position = 0

            # Open new position
            if sig != 0:
                position = sig
                entry_price = price

        equity.append({
            "day": i,
            "value": round(capital, 2),
            "timestamp": candles[i]["timestamp"],
        })
        peak = max(peak, capital)

    # Close any open position at end
    if position != 0 and candles:
        price = candles[-1]["close"]
        pnl_pct = (price - entry_price) / entry_price * position
        trade_pnl = capital * 0.1 * pnl_pct
        capital += trade_pnl
        trades.append({
            "entry": entry_price,
            "exit": price,
            "side": "long" if position > 0 else "short",
            "pnl": round(trade_pnl, 2),
            "pnl_pct": round(pnl_pct * 100, 2),
        })
        equity[-1]["value"] = round(capital, 2)

    return _compute_metrics(trades, equity, initial_capital, capital, candles)


def _compute_metrics(
    trades: List[Dict],
    equity: List[Dict],
    initial_capital: float,
    final_capital: float,
    candles: List[Dict],
) -> Dict:
    total_return = ((final_capital - initial_capital) / initial_capital) * 100
    winners = [t for t in trades if t["pnl"] > 0]
    losers = [t for t in trades if t["pnl"] <= 0]
    win_rate = (len(winners) / len(trades) * 100) if trades else 0

    # Sharpe ratio (annualized from daily equity returns)
    values = [e["value"] for e in equity]
    daily_returns = []
    for i in range(1, len(values)):
        if values[i - 1] > 0:
            daily_returns.append((values[i] - values[i - 1]) / values[i - 1])
    if daily_returns and len(daily_returns) > 1:
        mean_r = sum(daily_returns) / len(daily_returns)
        std_r = (sum((r - mean_r) ** 2 for r in daily_returns) / (len(daily_returns) - 1)) ** 0.5
        sharpe = (mean_r / std_r * math.sqrt(252)) if std_r > 0 else 0
    else:
        sharpe = 0

    # Max drawdown
    peak = values[0]
    max_dd = 0
    for v in values:
        peak = max(peak, v)
        dd = (peak - v) / peak * 100 if peak > 0 else 0
        max_dd = max(max_dd, dd)

    # Profit factor
    gross_profit = sum(t["pnl"] for t in winners)
    gross_loss = abs(sum(t["pnl"] for t in losers))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")

    # Sample equity to max 60 points for frontend chart
    step = max(1, len(equity) // 60)
    sampled_equity = equity[::step]
    if equity and sampled_equity[-1] != equity[-1]:
        sampled_equity.append(equity[-1])

    period_start = candles[0]["timestamp"][:10] if candles else "N/A"
    period_end = candles[-1]["timestamp"][:10] if candles else "N/A"

    return {
        "period": f"{period_start} to {period_end}",
        "initial_capital": initial_capital,
        "final_capital": round(final_capital, 2),
        "total_return": round(total_return, 2),
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown": round(max_dd, 2),
        "win_rate": round(win_rate, 1),
        "total_trades": len(trades),
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else 99.0,
        "avg_win": round(sum(t["pnl"] for t in winners) / len(winners), 2) if winners else 0,
        "avg_loss": round(sum(t["pnl"] for t in losers) / len(losers), 2) if losers else 0,
        "equity_curve": sampled_equity,
        "data_source": "coingecko",
    }


def _empty_result(initial_capital: float) -> Dict:
    return {
        "period": "N/A",
        "initial_capital": initial_capital,
        "final_capital": initial_capital,
        "total_return": 0,
        "sharpe_ratio": 0,
        "max_drawdown": 0,
        "win_rate": 0,
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "profit_factor": 0,
        "avg_win": 0,
        "avg_loss": 0,
        "equity_curve": [{"day": 0, "value": initial_capital}],
        "data_source": "none",
    }
