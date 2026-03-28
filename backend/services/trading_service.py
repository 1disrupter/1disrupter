"""
AlphaAI Live Trading Service
Handles live and paper trade execution via Uniswap V3.
"""
import uuid
import random
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from database import db

logger = logging.getLogger("AlphaAI")

# ============= UNISWAP V3 CONSTANTS =============
UNISWAP_V3_ROUTER = {
    "sepolia": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    "mainnet": "0xE592427A0AEce92De3Edee1F18E0157C05861564"
}

WETH_ADDRESS = {
    "sepolia": "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14",
    "mainnet": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
}

TOKEN_ADDRESSES = {
    "WBTC": {"sepolia": "0x29f2D40B0605204364af54EC677bD022dA425d03", "mainnet": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"},
    "USDC": {"sepolia": "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8", "mainnet": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"},
    "LINK": {"sepolia": "0x779877A7B0D9E8603169DdbD7836e478b4624789", "mainnet": "0x514910771AF9Ca656af840dff83E8264EcF986CA"},
}

class LiveTradingService:
    """Service for executing live trades via Uniswap V3"""
    
    def __init__(self):
        self.network = "sepolia"  # Default to testnet for safety
        self.router_address = UNISWAP_V3_ROUTER[self.network]
    
    def get_token_mapping(self, symbol: str) -> dict:
        """Map crypto symbols to token addresses"""
        # Map common symbols to their wrapped versions
        mapping = {
            "BTC": {"token": "WBTC", "decimals": 8},
            "ETH": {"token": "WETH", "decimals": 18},
            "USDC": {"token": "USDC", "decimals": 6},
            "USDT": {"token": "USDT", "decimals": 6},
            "SOL": {"token": "WETH", "decimals": 18},  # SOL not on Ethereum, use ETH as proxy
        }
        return mapping.get(symbol, {"token": "WETH", "decimals": 18})
    
    async def prepare_swap_transaction(
        self,
        wallet_address: str,
        token_in: str,
        token_out: str,
        amount_in: float,
        slippage: float = 0.5
    ) -> dict:
        """Prepare a Uniswap V3 swap transaction for frontend signing"""
        try:
            token_addresses = SEPOLIA_TOKEN_ADDRESSES if self.network == "sepolia" else TOKEN_ADDRESSES
            
            # Get token addresses
            token_in_address = token_addresses.get(token_in)
            token_out_address = token_addresses.get(token_out)
            
            if not token_in_address or not token_out_address:
                raise ValueError(f"Token not supported: {token_in} or {token_out}")
            
            # Calculate amounts with slippage
            # In production, this would query the Uniswap quoter for exact amounts
            min_amount_out = amount_in * (1 - slippage / 100)
            
            # Prepare swap parameters
            # exactInputSingle function selector: 0x414bf389
            swap_params = {
                "router": self.router_address,
                "tokenIn": token_in_address,
                "tokenOut": token_out_address,
                "fee": 3000,  # 0.3% fee tier (most common)
                "recipient": wallet_address,
                "deadline": int((datetime.now(timezone.utc) + timedelta(minutes=20)).timestamp()),
                "amountIn": int(amount_in * (10 ** 18)),  # Convert to wei
                "amountOutMinimum": int(min_amount_out * (10 ** 18)),
                "sqrtPriceLimitX96": 0  # No price limit
            }
            
            # Build transaction data
            # This is a simplified version - in production use web3.py to encode properly
            tx_data = {
                "to": self.router_address,
                "data": self._encode_swap_data(swap_params),
                "value": hex(swap_params["amountIn"]) if token_in == "WETH" else "0x0",
                "chainId": 11155111 if self.network == "sepolia" else 1,
                "gasLimit": hex(300000),  # Estimated gas
            }
            
            return {
                "success": True,
                "transaction": tx_data,
                "params": swap_params,
                "network": self.network,
                "estimated_gas": 300000
            }
            
        except Exception as e:
            logger.error(f"Swap preparation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _encode_swap_data(self, params: dict) -> str:
        """Encode swap function data (simplified)"""
        # In production, use web3.py contract.encodeABI()
        # This is a placeholder that returns the function selector
        return "0x414bf389"  # exactInputSingle selector
    
    async def execute_paper_trade(
        self,
        wallet_address: str,
        symbol: str,
        side: str,
        amount_usd: float,
        current_price: float,
        signal_id: Optional[str] = None
    ) -> dict:
        """Execute a paper trade (simulated)"""
        try:
            # Calculate trade amount
            token_amount = amount_usd / current_price
            
            # Simulate small slippage (0.1-0.3%)
            slippage = random.uniform(0.001, 0.003)
            executed_price = current_price * (1 + slippage if side == "BUY" else 1 - slippage)
            executed_amount = amount_usd / executed_price
            
            # Simulate gas fee ($2-10)
            gas_fee = random.uniform(2, 10)
            
            # Create trade order
            order = TradeOrder(
                wallet_address=wallet_address,
                signal_id=signal_id,
                symbol=symbol,
                side=side,
                amount_usd=amount_usd,
                is_live=False,
                status="confirmed",
                tx_hash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                gas_used=random.randint(150000, 250000),
                gas_price_gwei=random.uniform(20, 50),
                executed_price=executed_price,
                executed_amount=executed_amount,
                fee_paid=gas_fee,
                executed_at=datetime.now(timezone.utc)
            )
            
            # Store trade
            trade_doc = order.model_dump()
            trade_doc["created_at"] = order.created_at
            trade_doc["executed_at"] = order.executed_at
            await db.trades.insert_one(trade_doc)
            
            # Update or create position
            existing_position = await db.positions.find_one({
                "wallet_address": wallet_address,
                "symbol": symbol,
                "is_live": False
            })
            
            if existing_position:
                # Update existing position
                if side == "BUY":
                    new_amount = existing_position["amount"] + executed_amount
                    new_cost = existing_position["amount_usd"] + amount_usd
                    new_entry = new_cost / new_amount
                else:
                    new_amount = existing_position["amount"] - executed_amount
                    new_cost = existing_position["amount_usd"] - amount_usd
                    new_entry = new_cost / new_amount if new_amount > 0 else 0
                
                if new_amount <= 0:
                    # Close position
                    realized_pnl = (executed_price - existing_position["entry_price"]) * existing_position["amount"]
                    await db.positions.delete_one({"id": existing_position["id"]})
                    
                    # Update trade with PnL
                    await db.trades.update_one(
                        {"id": order.id},
                        {"$set": {"pnl": realized_pnl, "pnl_percent": (realized_pnl / existing_position["amount_usd"]) * 100}}
                    )
                else:
                    await db.positions.update_one(
                        {"id": existing_position["id"]},
                        {"$set": {
                            "amount": new_amount,
                            "amount_usd": new_cost,
                            "entry_price": new_entry,
                            "current_price": executed_price,
                            "last_updated": datetime.now(timezone.utc)
                        }}
                    )
            else:
                # Create new position
                position = TradePosition(
                    wallet_address=wallet_address,
                    symbol=symbol,
                    side="LONG" if side == "BUY" else "SHORT",
                    entry_price=executed_price,
                    current_price=executed_price,
                    amount=executed_amount,
                    amount_usd=amount_usd,
                    is_live=False
                )
                await db.positions.insert_one(position.model_dump())
            
            # Update investor paper balance
            await db.investors.update_one(
                {"wallet_address": wallet_address},
                {"$inc": {"paper_balance": -amount_usd if side == "BUY" else amount_usd}}
            )
            
            logger.info(f"Paper trade executed: {side} {symbol} ${amount_usd} for {wallet_address}")
            
            return {
                "success": True,
                "trade_id": order.id,
                "tx_hash": order.tx_hash,
                "executed_price": executed_price,
                "executed_amount": executed_amount,
                "fee_paid": gas_fee,
                "is_live": False,
                "status": "confirmed"
            }
            
        except Exception as e:
            logger.error(f"Paper trade error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_positions(self, wallet_address: str, is_live: Optional[bool] = None) -> List[dict]:
        """Get all positions for a user"""
        query = {"wallet_address": wallet_address}
        if is_live is not None:
            query["is_live"] = is_live
        
        positions = await db.positions.find(query, {"_id": 0}).to_list(100)
        
        # Update current prices and PnL
        for pos in positions:
            # Fetch current price
            prices = await signal_service._fetch_live_prices()
            current_price = next((p["price"] for p in prices if p["symbol"] == pos["symbol"]), pos["current_price"])
            
            # Calculate unrealized PnL
            if pos["side"] == "LONG":
                unrealized_pnl = (current_price - pos["entry_price"]) * pos["amount"]
            else:
                unrealized_pnl = (pos["entry_price"] - current_price) * pos["amount"]
            
            unrealized_pnl_percent = (unrealized_pnl / pos["amount_usd"]) * 100
            
            pos["current_price"] = current_price
            pos["unrealized_pnl"] = round(unrealized_pnl, 2)
            pos["unrealized_pnl_percent"] = round(unrealized_pnl_percent, 2)
            
            # Convert datetime
            if isinstance(pos.get("opened_at"), datetime):
                pos["opened_at"] = pos["opened_at"].isoformat()
            if isinstance(pos.get("last_updated"), datetime):
                pos["last_updated"] = pos["last_updated"].isoformat()
        
        return positions
    
    async def get_trade_history(
        self,
        wallet_address: str,
        is_live: Optional[bool] = None,
        limit: int = 50
    ) -> List[dict]:
        """Get trade history for a user"""
        query = {"wallet_address": wallet_address}
        if is_live is not None:
            query["is_live"] = is_live
        
        trades = await db.trades.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Convert datetimes
        for trade in trades:
            if isinstance(trade.get("created_at"), datetime):
                trade["created_at"] = trade["created_at"].isoformat()
            if isinstance(trade.get("executed_at"), datetime):
                trade["executed_at"] = trade["executed_at"].isoformat()
            if isinstance(trade.get("closed_at"), datetime):
                trade["closed_at"] = trade["closed_at"].isoformat()
        
        return trades
    
    async def get_portfolio_summary(self, wallet_address: str, is_live: bool = False) -> dict:
        """Get portfolio summary with total PnL"""
        positions = await self.get_user_positions(wallet_address, is_live)
        trades = await self.get_trade_history(wallet_address, is_live, 1000)
        
        # Calculate totals
        total_invested = sum(p.get("amount_usd", 0) for p in positions)
        total_unrealized_pnl = sum(p.get("unrealized_pnl", 0) for p in positions)
        total_realized_pnl = sum(t.get("pnl", 0) or 0 for t in trades)
        total_fees = sum(t.get("fee_paid", 0) or 0 for t in trades)
        
        # Win/loss stats
        winning_trades = [t for t in trades if (t.get("pnl") or 0) > 0]
        losing_trades = [t for t in trades if (t.get("pnl") or 0) < 0]
        
        return {
            "wallet_address": wallet_address,
            "is_live": is_live,
            "positions_count": len(positions),
            "total_invested": round(total_invested, 2),
            "total_unrealized_pnl": round(total_unrealized_pnl, 2),
            "total_realized_pnl": round(total_realized_pnl, 2),
            "total_fees_paid": round(total_fees, 2),
            "net_pnl": round(total_unrealized_pnl + total_realized_pnl - total_fees, 2),
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(len(winning_trades) / max(len(trades), 1) * 100, 1)
        }

# Initialize trading service
trading_service = LiveTradingService()

live_trading_service = LiveTradingService()
