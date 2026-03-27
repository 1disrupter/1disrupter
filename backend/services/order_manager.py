"""
AlphaAI Order Manager Service
Handles Stop-Loss and Take-Profit order monitoring and execution.
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger("AlphaAI.OrderManager")

# Database reference
db = None

def init_db(database):
    global db
    db = database

class OrderType(str, Enum):
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TradingMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"

class SLTPOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    trade_id: Optional[str] = None
    symbol: str  # BTC, ETH, SOL
    order_type: OrderType
    trigger_price: float
    quantity: float
    current_position_price: float  # Entry price
    trading_mode: TradingMode = TradingMode.PAPER
    status: OrderStatus = OrderStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    triggered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    execution_price: Optional[float] = None
    pnl: Optional[float] = None
    notes: Optional[str] = None

class CreateSLTPRequest(BaseModel):
    symbol: str
    order_type: OrderType
    trigger_price: float
    quantity: float
    current_position_price: float
    trading_mode: TradingMode = TradingMode.PAPER
    trade_id: Optional[str] = None

class OrderManagerService:
    """Service for managing Stop-Loss and Take-Profit orders"""
    
    def __init__(self):
        self.monitoring_task = None
        self.is_running = False
        self.check_interval = 5  # seconds
        self.current_prices: Dict[str, float] = {}
    
    async def create_order(self, user_id: str, request: CreateSLTPRequest) -> Dict[str, Any]:
        """Create a new SL/TP order"""
        order = SLTPOrder(
            user_id=user_id,
            symbol=request.symbol.upper(),
            order_type=request.order_type,
            trigger_price=request.trigger_price,
            quantity=request.quantity,
            current_position_price=request.current_position_price,
            trading_mode=request.trading_mode,
            trade_id=request.trade_id
        )
        
        # Validate order
        if request.order_type == OrderType.STOP_LOSS:
            # Stop-loss should be below current price for long positions
            if request.trigger_price >= request.current_position_price:
                logger.warning(f"Stop-loss price {request.trigger_price} should be below entry {request.current_position_price}")
        elif request.order_type == OrderType.TAKE_PROFIT:
            # Take-profit should be above current price for long positions
            if request.trigger_price <= request.current_position_price:
                logger.warning(f"Take-profit price {request.trigger_price} should be above entry {request.current_position_price}")
        
        # Store in database
        order_doc = order.model_dump()
        await db.orders.insert_one(order_doc)
        
        logger.info(f"Created {order.order_type.value} order for {order.symbol} at {order.trigger_price}")
        
        return {
            "success": True,
            "order": {
                "id": order.id,
                "symbol": order.symbol,
                "order_type": order.order_type.value,
                "trigger_price": order.trigger_price,
                "quantity": order.quantity,
                "status": order.status.value,
                "trading_mode": order.trading_mode.value,
                "created_at": order.created_at.isoformat()
            }
        }
    
    async def get_active_orders(self, user_id: str, symbol: Optional[str] = None) -> List[Dict]:
        """Get all active orders for a user"""
        query = {"user_id": user_id, "status": OrderStatus.ACTIVE.value}
        if symbol:
            query["symbol"] = symbol.upper()
        
        orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
        return orders
    
    async def get_order_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get order history including triggered and cancelled orders"""
        orders = await db.orders.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return orders
    
    async def cancel_order(self, user_id: str, order_id: str) -> Dict[str, Any]:
        """Cancel an active order"""
        result = await db.orders.update_one(
            {"id": order_id, "user_id": user_id, "status": OrderStatus.ACTIVE.value},
            {"$set": {
                "status": OrderStatus.CANCELLED.value,
                "cancelled_at": datetime.now(timezone.utc)
            }}
        )
        
        if result.modified_count == 0:
            return {"success": False, "message": "Order not found or already processed"}
        
        logger.info(f"Cancelled order {order_id}")
        return {"success": True, "message": "Order cancelled"}
    
    async def modify_order(self, user_id: str, order_id: str, 
                          new_trigger_price: Optional[float] = None,
                          new_quantity: Optional[float] = None) -> Dict[str, Any]:
        """Modify an active order"""
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        if new_trigger_price is not None:
            update_data["trigger_price"] = new_trigger_price
        if new_quantity is not None:
            update_data["quantity"] = new_quantity
        
        result = await db.orders.update_one(
            {"id": order_id, "user_id": user_id, "status": OrderStatus.ACTIVE.value},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return {"success": False, "message": "Order not found or already processed"}
        
        logger.info(f"Modified order {order_id}")
        return {"success": True, "message": "Order modified"}
    
    async def update_prices(self, prices: Dict[str, float]):
        """Update current market prices"""
        self.current_prices = prices
    
    async def check_and_trigger_orders(self):
        """Check all active orders against current prices and trigger if conditions met"""
        if not self.current_prices:
            return
        
        active_orders = await db.orders.find(
            {"status": OrderStatus.ACTIVE.value}
        ).to_list(1000)
        
        for order in active_orders:
            symbol = order["symbol"]
            current_price = self.current_prices.get(symbol)
            
            if current_price is None:
                continue
            
            trigger_price = order["trigger_price"]
            order_type = order["order_type"]
            should_trigger = False
            
            if order_type == OrderType.STOP_LOSS.value:
                # Trigger stop-loss when price drops to or below trigger
                if current_price <= trigger_price:
                    should_trigger = True
            elif order_type == OrderType.TAKE_PROFIT.value:
                # Trigger take-profit when price rises to or above trigger
                if current_price >= trigger_price:
                    should_trigger = True
            
            if should_trigger:
                await self._execute_order(order, current_price)
    
    async def _execute_order(self, order: Dict, execution_price: float):
        """Execute a triggered order"""
        user_id = order["user_id"]
        symbol = order["symbol"]
        quantity = order["quantity"]
        order_type = order["order_type"]
        trading_mode = order["trading_mode"]
        entry_price = order["current_position_price"]
        
        # Calculate P&L
        pnl = (execution_price - entry_price) * quantity
        if order_type == OrderType.STOP_LOSS.value:
            # Stop-loss usually means a loss
            pnl = abs(pnl) * -1 if execution_price < entry_price else pnl
        
        # Update order status
        await db.orders.update_one(
            {"id": order["id"]},
            {"$set": {
                "status": OrderStatus.TRIGGERED.value,
                "triggered_at": datetime.now(timezone.utc),
                "execution_price": execution_price,
                "pnl": pnl
            }}
        )
        
        # Execute the trade based on mode
        if trading_mode == TradingMode.PAPER.value:
            # Update paper trading balance
            await db.users.update_one(
                {"id": user_id},
                {"$inc": {"paper_pnl": pnl}}
            )
            
            # Record the trade
            trade_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "symbol": symbol,
                "side": "sell",  # SL/TP closes positions
                "quantity": quantity,
                "price": execution_price,
                "pnl": pnl,
                "order_id": order["id"],
                "order_type": order_type,
                "trading_mode": trading_mode,
                "timestamp": datetime.now(timezone.utc)
            }
            await db.trades.insert_one(trade_record)
        
        # Send notification
        try:
            from services.push_notifications import push_service
            emoji = "🛑" if order_type == OrderType.STOP_LOSS.value else "🎯"
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            
            await push_service.send_to_user(
                user_id=user_id,
                title=f"{emoji} {order_type.replace('_', ' ').title()} Triggered",
                body=f"{symbol} @ ${execution_price:,.2f} | P&L: {pnl_str}",
                data={
                    "type": "order_triggered",
                    "order_id": order["id"],
                    "symbol": symbol,
                    "screen": "trades"
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send order trigger notification: {e}")
        
        logger.info(f"Executed {order_type} for {symbol} at {execution_price}, P&L: {pnl:.2f}")
        
        # Update trader stats for leaderboard
        await self._update_trader_stats(user_id, pnl, order_type)
    
    async def _update_trader_stats(self, user_id: str, pnl: float, order_type: str):
        """Update trader statistics after order execution"""
        is_win = pnl > 0
        
        await db.trader_stats.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "stats.total_pnl": pnl,
                    "stats.total_trades": 1,
                    "stats.wins": 1 if is_win else 0,
                    "stats.losses": 0 if is_win else 1
                },
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )
    
    async def start_monitoring(self):
        """Start the background price monitoring task"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Order monitoring started")
    
    async def stop_monitoring(self):
        """Stop the background monitoring task"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Order monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background loop to check orders"""
        while self.is_running:
            try:
                await self.check_and_trigger_orders()
            except Exception as e:
                logger.error(f"Error in order monitoring: {e}")
            
            await asyncio.sleep(self.check_interval)

# Singleton instance
order_manager = OrderManagerService()

def get_order_manager() -> OrderManagerService:
    return order_manager
