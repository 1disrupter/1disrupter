"""
AlphaAI Copy Trading Service
Handles trade mirroring between traders and their followers.
- Auto-copy: immediately replicate trades using allocation percentage
- Manual-copy: send notification and wait for approval
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("AlphaAI.CopyTrading")

db = None


def init_db(database):
    global db
    db = database
    logger.info("Copy trading service initialized")


async def follow_trader(copier_id: str, trader_id: str, mode: str = "auto",
                        allocation_percent: float = 10, max_per_trade: float = 500) -> dict:
    """Create a copy relationship between a copier and a trader."""
    if copier_id == trader_id:
        return {"success": False, "error": "You cannot copy yourself"}

    # Check circular: trader_id already copies copier_id
    circular = await db.copy_relationships.find_one({
        "copier_id": trader_id,
        "trader_id": copier_id,
        "status": {"$in": ["active", "paused"]}
    })
    if circular:
        return {"success": False, "error": "Circular copying detected. This trader already follows you."}

    # Check if already following
    existing = await db.copy_relationships.find_one({
        "copier_id": copier_id,
        "trader_id": trader_id,
        "status": {"$in": ["active", "paused"]}
    })
    if existing:
        return {"success": False, "error": "You are already following this trader"}

    # Validate copier is Pro/Elite
    copier = await db.users.find_one({"id": copier_id}, {"_id": 0})
    if not copier:
        return {"success": False, "error": "User not found"}
    if not copier.get("is_pro") and not copier.get("is_elite"):
        return {"success": False, "error": "Copy trading requires Pro or Elite subscription"}

    # Validate trader exists and is public
    trader_stats = await db.trader_stats.find_one({"user_id": trader_id}, {"_id": 0})
    if not trader_stats or not trader_stats.get("is_public", False):
        return {"success": False, "error": "Trader not found or profile is private"}

    # Clamp allocation and max
    allocation_percent = max(1, min(100, allocation_percent))
    max_per_trade = max(1, min(100000, max_per_trade))

    relationship = {
        "id": str(uuid.uuid4()),
        "copier_id": copier_id,
        "trader_id": trader_id,
        "mode": mode if mode in ("auto", "manual") else "auto",
        "allocation_percent": allocation_percent,
        "max_per_trade": max_per_trade,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stats": {"trades_copied": 0, "total_pnl": 0.0}
    }

    await db.copy_relationships.insert_one(relationship)
    # Remove _id before returning
    relationship.pop("_id", None)

    logger.info(f"Copy relationship created: {copier_id} -> {trader_id} ({mode})")
    return {"success": True, "relationship": relationship}


async def unfollow_trader(relationship_id: str, copier_id: str) -> dict:
    """Remove a copy relationship."""
    rel = await db.copy_relationships.find_one({"id": relationship_id, "copier_id": copier_id})
    if not rel:
        return {"success": False, "error": "Relationship not found"}

    await db.copy_relationships.update_one(
        {"id": relationship_id},
        {"$set": {"status": "removed", "removed_at": datetime.now(timezone.utc).isoformat()}}
    )
    # Also reject any pending trades
    await db.pending_copy_trades.update_many(
        {"copy_relationship_id": relationship_id, "status": "pending"},
        {"$set": {"status": "rejected", "resolved_at": datetime.now(timezone.utc).isoformat()}}
    )

    logger.info(f"Copy relationship removed: {relationship_id}")
    return {"success": True, "message": "Unfollowed trader"}


async def update_settings(relationship_id: str, copier_id: str,
                          mode: Optional[str] = None,
                          allocation_percent: Optional[float] = None,
                          max_per_trade: Optional[float] = None,
                          status: Optional[str] = None) -> dict:
    """Update copy settings for a relationship."""
    rel = await db.copy_relationships.find_one({"id": relationship_id, "copier_id": copier_id})
    if not rel:
        return {"success": False, "error": "Relationship not found"}

    updates = {}
    if mode and mode in ("auto", "manual"):
        updates["mode"] = mode
    if allocation_percent is not None:
        updates["allocation_percent"] = max(1, min(100, allocation_percent))
    if max_per_trade is not None:
        updates["max_per_trade"] = max(1, min(100000, max_per_trade))
    if status and status in ("active", "paused"):
        updates["status"] = status

    if not updates:
        return {"success": False, "error": "No valid fields to update"}

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.copy_relationships.update_one({"id": relationship_id}, {"$set": updates})

    updated = await db.copy_relationships.find_one({"id": relationship_id}, {"_id": 0})
    return {"success": True, "relationship": updated}


async def get_following(copier_id: str) -> list:
    """Get list of traders that a user follows."""
    rels = await db.copy_relationships.find(
        {"copier_id": copier_id, "status": {"$in": ["active", "paused"]}},
        {"_id": 0}
    ).to_list(100)

    # Enrich with trader info
    for rel in rels:
        trader_stats = await db.trader_stats.find_one({"user_id": rel["trader_id"]}, {"_id": 0})
        if trader_stats:
            rel["trader_display_name"] = trader_stats.get("display_name", f"Trader_{rel['trader_id'][:6]}")
            rel["trader_stats"] = trader_stats.get("stats", {})
        else:
            rel["trader_display_name"] = f"Trader_{rel['trader_id'][:6]}"
            rel["trader_stats"] = {}

    return rels


async def get_followers(trader_id: str) -> list:
    """Get list of followers for a trader."""
    rels = await db.copy_relationships.find(
        {"trader_id": trader_id, "status": {"$in": ["active", "paused"]}},
        {"_id": 0}
    ).to_list(100)

    for rel in rels:
        user = await db.users.find_one({"id": rel["copier_id"]}, {"_id": 0, "name": 1, "id": 1})
        if user:
            rel["copier_name"] = user.get("name", f"User_{rel['copier_id'][:6]}")
        else:
            rel["copier_name"] = f"User_{rel['copier_id'][:6]}"

    return rels


async def get_pending_trades(copier_id: str) -> list:
    """Get pending copy trades awaiting manual approval."""
    return await db.pending_copy_trades.find(
        {"copier_id": copier_id, "status": "pending"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)


async def approve_trade(trade_id: str, copier_id: str) -> dict:
    """Approve a pending manual copy trade and execute it."""
    pending = await db.pending_copy_trades.find_one({"id": trade_id, "copier_id": copier_id})
    if not pending:
        return {"success": False, "error": "Pending trade not found"}
    if pending["status"] != "pending":
        return {"success": False, "error": f"Trade already {pending['status']}"}

    # Execute the copy trade
    result = await _execute_copy_trade(pending)

    status = "approved" if result.get("success") else "failed"
    await db.pending_copy_trades.update_one(
        {"id": trade_id},
        {"$set": {"status": status, "resolved_at": datetime.now(timezone.utc).isoformat(),
                  "result": result}}
    )

    if result.get("success"):
        # Update relationship stats
        await db.copy_relationships.update_one(
            {"id": pending["copy_relationship_id"]},
            {"$inc": {"stats.trades_copied": 1}}
        )

    return {"success": True, "trade_status": status, "result": result}


async def reject_trade(trade_id: str, copier_id: str) -> dict:
    """Reject a pending manual copy trade."""
    pending = await db.pending_copy_trades.find_one({"id": trade_id, "copier_id": copier_id})
    if not pending:
        return {"success": False, "error": "Pending trade not found"}
    if pending["status"] != "pending":
        return {"success": False, "error": f"Trade already {pending['status']}"}

    await db.pending_copy_trades.update_one(
        {"id": trade_id},
        {"$set": {"status": "rejected", "resolved_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "message": "Trade rejected"}


async def process_trader_trade(trader_id: str, trade_data: dict):
    """
    Called after a trader executes a trade.
    Finds all followers and replicates or queues the trade.
    """
    followers = await db.copy_relationships.find(
        {"trader_id": trader_id, "status": "active"}
    ).to_list(1000)

    if not followers:
        return

    logger.info(f"Processing copy trades for {len(followers)} followers of {trader_id}")

    for rel in followers:
        try:
            # Calculate scaled amount
            original_amount = trade_data.get("amount_usd", 0)
            scaled_amount = original_amount * (rel["allocation_percent"] / 100)
            scaled_amount = min(scaled_amount, rel["max_per_trade"])
            scaled_amount = round(scaled_amount, 2)

            if scaled_amount < 1:
                continue

            copy_trade = {
                "id": str(uuid.uuid4()),
                "copy_relationship_id": rel["id"],
                "copier_id": rel["copier_id"],
                "trader_id": trader_id,
                "original_trade_id": trade_data.get("trade_id", ""),
                "symbol": trade_data.get("symbol", ""),
                "side": trade_data.get("side", ""),
                "original_amount": original_amount,
                "scaled_amount": scaled_amount,
                "current_price": trade_data.get("executed_price", 0),
                "is_live": trade_data.get("is_live", False),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            if rel["mode"] == "auto":
                copy_trade["status"] = "executing"
                await db.pending_copy_trades.insert_one(copy_trade)
                result = await _execute_copy_trade(copy_trade)

                status = "executed" if result.get("success") else "failed"
                await db.pending_copy_trades.update_one(
                    {"id": copy_trade["id"]},
                    {"$set": {"status": status, "resolved_at": datetime.now(timezone.utc).isoformat(),
                              "result": result}}
                )
                if result.get("success"):
                    await db.copy_relationships.update_one(
                        {"id": rel["id"]},
                        {"$inc": {"stats.trades_copied": 1}}
                    )
                    logger.info(f"Auto-copied trade for {rel['copier_id']}: {copy_trade['symbol']} {copy_trade['side']} ${scaled_amount}")
            else:
                # Manual mode: queue for approval
                copy_trade["status"] = "pending"
                await db.pending_copy_trades.insert_one(copy_trade)
                logger.info(f"Queued manual copy trade for {rel['copier_id']}: {copy_trade['symbol']} {copy_trade['side']} ${scaled_amount}")

        except Exception as e:
            logger.error(f"Error processing copy trade for {rel['copier_id']}: {e}")


async def _execute_copy_trade(copy_trade: dict) -> dict:
    """Execute a copy trade using the existing paper trade engine."""
    try:
        copier_id = copy_trade["copier_id"]
        symbol = copy_trade["symbol"]
        side = copy_trade["side"]
        amount_usd = copy_trade["scaled_amount"]
        current_price = copy_trade.get("current_price", 0)

        # Get copier's wallet/investor info
        user = await db.users.find_one({"id": copier_id}, {"_id": 0})
        if not user:
            return {"success": False, "error": "Copier user not found"}

        wallet = user.get("wallet_address")
        if not wallet:
            # Use user id as wallet for paper trading
            wallet = f"copy_{copier_id[:12]}"

        # Check paper balance
        investor = await db.investors.find_one({"wallet_address": wallet})
        if not investor:
            # Create investor record for paper trading
            investor = {
                "wallet_address": wallet,
                "paper_balance": 10000,
                "paper_pnl": 0,
                "is_paper_trading": True
            }
            await db.investors.insert_one(investor)
            investor.pop("_id", None)

        paper_balance = investor.get("paper_balance", 0)
        if side.upper() == "BUY" and paper_balance < amount_usd:
            return {"success": False, "error": f"Insufficient balance. Available: ${paper_balance:.2f}, Needed: ${amount_usd:.2f}"}

        # Fetch current price if not provided
        if not current_price or current_price <= 0:
            # Use a simple price lookup
            prices_coll = await db.signals.find_one({"symbol": symbol}, {"_id": 0, "current_price": 1})
            current_price = prices_coll.get("current_price", 100) if prices_coll else 100

        import random
        # Simulate execution (same as paper trade engine)
        slippage = random.uniform(0.001, 0.003)
        executed_price = current_price * (1 + slippage if side.upper() == "BUY" else 1 - slippage)
        executed_amount = amount_usd / executed_price
        gas_fee = random.uniform(2, 10)

        trade_id = str(uuid.uuid4())
        trade_doc = {
            "id": trade_id,
            "wallet_address": wallet,
            "symbol": symbol,
            "side": side.upper(),
            "amount_usd": amount_usd,
            "is_live": False,
            "status": "confirmed",
            "tx_hash": f"0xcopy_{''.join(random.choices('0123456789abcdef', k=58))}",
            "executed_price": executed_price,
            "executed_amount": executed_amount,
            "fee_paid": gas_fee,
            "is_copy_trade": True,
            "original_trade_id": copy_trade.get("original_trade_id", ""),
            "copier_id": copier_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

        await db.trades.insert_one(trade_doc)

        # Update balance
        if side.upper() == "BUY":
            await db.investors.update_one(
                {"wallet_address": wallet},
                {"$inc": {"paper_balance": -amount_usd}}
            )
        else:
            await db.investors.update_one(
                {"wallet_address": wallet},
                {"$inc": {"paper_balance": amount_usd}}
            )

        return {
            "success": True,
            "trade_id": trade_id,
            "executed_price": round(executed_price, 2),
            "executed_amount": round(executed_amount, 6),
            "amount_usd": amount_usd
        }

    except Exception as e:
        logger.error(f"Copy trade execution error: {e}")
        return {"success": False, "error": str(e)}
