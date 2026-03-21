"""
AlphaAI Demo Data Generator
Generates realistic paper trading data for demonstration purposes
- 30 days of trading history
- Mix of winning/losing trades (realistic ~55% win rate)
- Multiple symbols (BTC, ETH, SOL)
- Proper timestamps and price movements
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone, timedelta
import random
import uuid
import math

# MongoDB connection - will be initialized in main server
db = None

def init_db(database):
    """Initialize database connection"""
    global db
    db = database

router = APIRouter(prefix="/api/demo", tags=["Demo Data"])

# Realistic price ranges and volatility for each symbol
SYMBOLS = {
    "BTC": {"base_price": 67000, "volatility": 0.03, "min": 60000, "max": 75000},
    "ETH": {"base_price": 3500, "volatility": 0.04, "min": 3000, "max": 4000},
    "SOL": {"base_price": 145, "volatility": 0.05, "min": 120, "max": 180}
}

def generate_price_path(symbol: str, days: int = 30) -> list:
    """Generate a realistic price path using geometric Brownian motion"""
    config = SYMBOLS[symbol]
    prices = [config["base_price"]]
    
    # Daily drift and volatility
    drift = 0.0002  # Slight upward bias
    vol = config["volatility"]
    
    for _ in range(days * 24):  # Hourly prices
        last_price = prices[-1]
        # Random walk with drift
        change = last_price * (drift + vol * random.gauss(0, 1) / math.sqrt(24))
        new_price = last_price + change
        # Keep within bounds
        new_price = max(config["min"], min(config["max"], new_price))
        prices.append(new_price)
    
    return prices

def generate_trade(wallet_address: str, symbol: str, price: float, timestamp: datetime, 
                   is_winner: bool, trade_size_usd: float) -> dict:
    """Generate a single realistic trade"""
    side = random.choice(["BUY", "SELL"])
    
    # Calculate amount based on trade size
    amount = trade_size_usd / price
    
    # Generate PnL based on win/loss
    if is_winner:
        pnl_pct = random.uniform(0.5, 4.0)  # 0.5% to 4% gain
    else:
        pnl_pct = random.uniform(-3.0, -0.3)  # 0.3% to 3% loss
    
    pnl = trade_size_usd * (pnl_pct / 100)
    
    # Exit price based on PnL
    if side == "BUY":
        exit_price = price * (1 + pnl_pct / 100)
    else:
        exit_price = price * (1 - pnl_pct / 100)
    
    return {
        "id": str(uuid.uuid4()),
        "wallet_address": wallet_address,
        "symbol": symbol,
        "side": side,
        "amount": round(amount, 8),
        "entry_price": round(price, 2),
        "exit_price": round(exit_price, 2),
        "pnl": round(pnl, 2),
        "pnl_percent": round(pnl_pct, 2),
        "status": "closed",
        "is_live": False,  # Paper trading
        "is_paper": True,
        "timestamp": timestamp,
        "closed_at": timestamp + timedelta(hours=random.randint(1, 12)),
        "signal_confidence": random.randint(65, 95),
        "created_at": timestamp
    }

@router.post("/generate-trades")
async def generate_demo_trades(
    wallet_address: str = Query(..., description="Wallet address to generate trades for"),
    days: int = Query(30, description="Number of days of history"),
    trades_per_day: int = Query(3, description="Average trades per day"),
    starting_balance: float = Query(10000, description="Starting paper balance"),
    win_rate: float = Query(0.55, description="Win rate (0.0-1.0)")
):
    """
    Generate realistic demo paper trades for the specified wallet.
    Creates a mix of winning and losing trades across BTC, ETH, and SOL.
    """
    if win_rate < 0 or win_rate > 1:
        raise HTTPException(status_code=400, detail="Win rate must be between 0 and 1")
    
    # Clear existing demo trades for this wallet
    await db.trades.delete_many({
        "wallet_address": wallet_address,
        "is_paper": True,
        "is_live": False
    })
    
    # Generate price paths for all symbols
    price_paths = {symbol: generate_price_path(symbol, days) for symbol in SYMBOLS}
    
    trades = []
    running_balance = starting_balance
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Generate trades day by day
    for day in range(days):
        # Skip some days randomly (weekends/low activity)
        if random.random() < 0.15:
            continue
        
        # Variable number of trades per day
        num_trades = random.randint(max(1, trades_per_day - 2), trades_per_day + 2)
        
        for _ in range(num_trades):
            # Random time during the day
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            timestamp = start_date + timedelta(days=day, hours=hour, minutes=minute)
            
            # Select random symbol
            symbol = random.choice(list(SYMBOLS.keys()))
            
            # Get price at this time (approximate)
            price_index = day * 24 + hour
            price = price_paths[symbol][min(price_index, len(price_paths[symbol]) - 1)]
            
            # Determine if this trade is a winner
            is_winner = random.random() < win_rate
            
            # Trade size: 5-15% of current balance
            trade_size_pct = random.uniform(0.05, 0.15)
            trade_size = running_balance * trade_size_pct
            
            # Generate trade
            trade = generate_trade(
                wallet_address=wallet_address,
                symbol=symbol,
                price=price,
                timestamp=timestamp,
                is_winner=is_winner,
                trade_size_usd=trade_size
            )
            
            trades.append(trade)
            running_balance += trade["pnl"]
            
            # Ensure balance doesn't go negative
            if running_balance < 1000:
                running_balance = 1000
    
    # Sort trades by timestamp
    trades.sort(key=lambda x: x["timestamp"])
    
    # Insert all trades
    if trades:
        await db.trades.insert_many(trades)
    
    # Update user's paper balance
    await db.users.update_one(
        {"wallet_address": wallet_address},
        {
            "$set": {
                "paper_balance": round(running_balance, 2),
                "paper_pnl": round(running_balance - starting_balance, 2)
            }
        },
        upsert=True
    )
    
    # Also update investors collection for backward compatibility
    await db.investors.update_one(
        {"wallet_address": wallet_address},
        {
            "$set": {
                "paper_balance": round(running_balance, 2),
                "paper_pnl": round(running_balance - starting_balance, 2)
            }
        },
        upsert=True
    )
    
    # Calculate summary stats
    winning_trades = [t for t in trades if t["pnl"] > 0]
    losing_trades = [t for t in trades if t["pnl"] < 0]
    
    total_pnl = sum(t["pnl"] for t in trades)
    total_wins = sum(t["pnl"] for t in winning_trades)
    total_losses = abs(sum(t["pnl"] for t in losing_trades))
    
    return {
        "success": True,
        "message": f"Generated {len(trades)} demo trades over {days} days",
        "summary": {
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(len(winning_trades) / len(trades) * 100, 1) if trades else 0,
            "total_pnl": round(total_pnl, 2),
            "starting_balance": starting_balance,
            "ending_balance": round(running_balance, 2),
            "total_return_pct": round((running_balance - starting_balance) / starting_balance * 100, 2),
            "profit_factor": round(total_wins / total_losses, 2) if total_losses > 0 else 0,
            "avg_win": round(total_wins / len(winning_trades), 2) if winning_trades else 0,
            "avg_loss": round(total_losses / len(losing_trades), 2) if losing_trades else 0
        },
        "period": {
            "start": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
            "end": datetime.now(timezone.utc).isoformat(),
            "days": days
        },
        "symbols_traded": list(set(t["symbol"] for t in trades))
    }

@router.delete("/clear-trades")
async def clear_demo_trades(
    wallet_address: str = Query(..., description="Wallet address to clear trades for")
):
    """Clear all demo paper trades for the specified wallet"""
    result = await db.trades.delete_many({
        "wallet_address": wallet_address,
        "is_paper": True,
        "is_live": False
    })
    
    # Reset user's paper balance
    await db.users.update_one(
        {"wallet_address": wallet_address},
        {"$set": {"paper_balance": 10000.0, "paper_pnl": 0.0}}
    )
    
    await db.investors.update_one(
        {"wallet_address": wallet_address},
        {"$set": {"paper_balance": 10000.0, "paper_pnl": 0.0}}
    )
    
    return {
        "success": True,
        "message": f"Cleared {result.deleted_count} demo trades",
        "paper_balance_reset": 10000.0
    }

@router.get("/status")
async def get_demo_status(
    wallet_address: str = Query(..., description="Wallet address to check")
):
    """Get demo data status for a wallet"""
    trade_count = await db.trades.count_documents({
        "wallet_address": wallet_address,
        "is_paper": True,
        "is_live": False
    })
    
    # Get date range
    oldest = await db.trades.find_one(
        {"wallet_address": wallet_address, "is_paper": True},
        sort=[("timestamp", 1)]
    )
    newest = await db.trades.find_one(
        {"wallet_address": wallet_address, "is_paper": True},
        sort=[("timestamp", -1)]
    )
    
    return {
        "wallet_address": wallet_address,
        "has_demo_data": trade_count > 0,
        "trade_count": trade_count,
        "date_range": {
            "oldest": oldest["timestamp"].isoformat() if oldest else None,
            "newest": newest["timestamp"].isoformat() if newest else None
        } if oldest else None
    }
