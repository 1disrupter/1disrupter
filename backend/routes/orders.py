"""
AlphaAI Orders API Routes
Stop-Loss and Take-Profit order management endpoints.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from enum import Enum

from services.order_manager import (
    order_manager, init_db as init_order_db,
    CreateSLTPRequest, OrderType, TradingMode, OrderStatus
)

logger = logging.getLogger("AlphaAI.Orders")

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Database reference
db = None

def init_db(database):
    global db
    db = database
    init_order_db(database)

# ============= REQUEST MODELS =============

class CreateOrderRequest(BaseModel):
    symbol: str
    order_type: str  # "stop_loss" or "take_profit"
    trigger_price: float
    quantity: float
    current_position_price: float
    trading_mode: str = "paper"  # "paper" or "live"
    trade_id: Optional[str] = None

class ModifyOrderRequest(BaseModel):
    trigger_price: Optional[float] = None
    quantity: Optional[float] = None

# ============= ENDPOINTS =============

@router.post("/sl-tp")
async def create_sltp_order(
    request: CreateOrderRequest,
    user_id: str = Query(..., description="User ID")
):
    """Create a new Stop-Loss or Take-Profit order"""
    try:
        # Validate order type
        try:
            order_type = OrderType(request.order_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid order type. Use 'stop_loss' or 'take_profit'")
        
        # Validate trading mode
        try:
            trading_mode = TradingMode(request.trading_mode)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid trading mode. Use 'paper' or 'live'")
        
        # Create the request object
        sltp_request = CreateSLTPRequest(
            symbol=request.symbol,
            order_type=order_type,
            trigger_price=request.trigger_price,
            quantity=request.quantity,
            current_position_price=request.current_position_price,
            trading_mode=trading_mode,
            trade_id=request.trade_id
        )
        
        result = await order_manager.create_order(user_id, sltp_request)
        return result
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
async def get_active_orders(
    user_id: str = Query(..., description="User ID"),
    symbol: Optional[str] = None
):
    """Get all active SL/TP orders for a user"""
    orders = await order_manager.get_active_orders(user_id, symbol)
    return {"orders": orders, "count": len(orders)}

@router.get("/history")
async def get_order_history(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100)
):
    """Get order history including triggered and cancelled orders"""
    orders = await order_manager.get_order_history(user_id, limit)
    return {"orders": orders, "count": len(orders)}

@router.get("/{order_id}")
async def get_order(
    order_id: str,
    user_id: str = Query(..., description="User ID")
):
    """Get a specific order by ID"""
    order = await db.orders.find_one(
        {"id": order_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.put("/{order_id}")
async def modify_order(
    order_id: str,
    request: ModifyOrderRequest,
    user_id: str = Query(..., description="User ID")
):
    """Modify an active order"""
    result = await order_manager.modify_order(
        user_id=user_id,
        order_id=order_id,
        new_trigger_price=request.trigger_price,
        new_quantity=request.quantity
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/{order_id}")
async def cancel_order(
    order_id: str,
    user_id: str = Query(..., description="User ID")
):
    """Cancel an active order"""
    result = await order_manager.cancel_order(user_id, order_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/stats/summary")
async def get_order_stats(
    user_id: str = Query(..., description="User ID")
):
    """Get order execution statistics for a user"""
    # Count orders by status
    active_count = await db.orders.count_documents(
        {"user_id": user_id, "status": OrderStatus.ACTIVE.value}
    )
    triggered_count = await db.orders.count_documents(
        {"user_id": user_id, "status": OrderStatus.TRIGGERED.value}
    )
    cancelled_count = await db.orders.count_documents(
        {"user_id": user_id, "status": OrderStatus.CANCELLED.value}
    )
    
    # Get P&L from triggered orders
    triggered_orders = await db.orders.find(
        {"user_id": user_id, "status": OrderStatus.TRIGGERED.value}
    ).to_list(1000)
    
    total_pnl = sum(o.get("pnl", 0) for o in triggered_orders)
    sl_triggered = sum(1 for o in triggered_orders if o.get("order_type") == OrderType.STOP_LOSS.value)
    tp_triggered = sum(1 for o in triggered_orders if o.get("order_type") == OrderType.TAKE_PROFIT.value)
    
    return {
        "active_orders": active_count,
        "triggered_orders": triggered_count,
        "cancelled_orders": cancelled_count,
        "stop_losses_triggered": sl_triggered,
        "take_profits_triggered": tp_triggered,
        "total_pnl_from_orders": total_pnl
    }
