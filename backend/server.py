"""
AlphaAI Fund Platform — Server Entry Point
Lightweight orchestrator that registers routers and manages app lifecycle.
"""
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import db, client, logger

# ============= SERVICE IMPORTS =============
from services.signal_service import signal_service
from services.websocket_manager import manager

# ============= ROUTE IMPORTS =============
from routes.auth import router as auth_router, init_db as init_auth_db
from routes.admin import router as admin_router, init_db as init_admin_db
from routes.leaderboard import router as leaderboard_router, init_db as init_leaderboard_db
from routes.orders import router as orders_router, init_db as init_orders_db
from routes.metrics import router as metrics_router, init_db as init_metrics_db
from routes.demo import router as demo_router, init_db as init_demo_db
from routes.referrals import router as referrals_router, init_db as init_referrals_db
from routes.mobile_v1 import router as mobile_router, init_db as init_mobile_db
from routes.copy_trading import router as copy_trading_router, init_db as init_copy_db

# New modular routes (extracted from monolith)
from routes.simulation import router as simulation_router
from routes.strategies import router as strategies_router
from routes.fund import router as fund_router
from routes.signals import router as signals_router
from routes.trading import router as trading_router
from routes.research import router as research_router
from routes.web3_routes import router as web3_router
from routes.event_agents import router as event_agents_router
from routes.marketing import router as marketing_router
from routes.payments import router as payments_router
from routes.analytics_routes import router as analytics_router
from routes.websocket import router as websocket_router
from routes.notifications import router as notifications_router

# ============= APP SETUP =============
app = FastAPI(title="AlphaAI Fund Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= REGISTER ROUTERS =============
# Pre-existing routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(leaderboard_router)
app.include_router(orders_router)
app.include_router(metrics_router)
app.include_router(demo_router)
app.include_router(referrals_router)
app.include_router(mobile_router)
app.include_router(copy_trading_router)

# New modular routers
app.include_router(fund_router)
app.include_router(signals_router)
app.include_router(simulation_router)
app.include_router(strategies_router)
app.include_router(trading_router)
app.include_router(research_router)
app.include_router(web3_router)
app.include_router(event_agents_router)
app.include_router(marketing_router)
app.include_router(payments_router)
app.include_router(analytics_router)
app.include_router(websocket_router)
app.include_router(notifications_router)


# ============= BACKGROUND TASKS =============
async def signal_generation_task():
    """Periodically generates AI trading signals."""
    while True:
        try:
            await signal_service.generate_ai_signal()
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
        await asyncio.sleep(300)


async def price_broadcast_task():
    """Broadcasts live prices to WebSocket clients."""
    while True:
        try:
            if manager.active_connections:
                from services.market_data import get_top_coins
                prices = await get_top_coins()
                if prices:
                    await manager.broadcast({
                        "type": "price_update",
                        "data": prices
                    })
        except Exception as e:
            logger.error(f"Price broadcast error: {e}")
        await asyncio.sleep(30)


# ============= LIFECYCLE EVENTS =============
@app.on_event("startup")
async def startup_db_client():
    """Initialize database indexes and background tasks on startup."""
    logger.info("AlphaAI Platform starting up...")

    # Initialize existing route/service db connections
    init_auth_db(db)
    init_admin_db(db)
    init_leaderboard_db(db)
    init_orders_db(db)
    init_metrics_db(db)
    init_demo_db(db)
    init_referrals_db(db)
    init_mobile_db(db)
    init_copy_db(db)

    # Create indexes
    await db.users.create_index("email", unique=True, sparse=True)
    await db.users.create_index("wallet_address", sparse=True)
    await db.signals.create_index("created_at")
    await db.signals.create_index("symbol")
    await db.trades.create_index("wallet_address")
    await db.simulations.create_index("wallet_address")
    await db.research_queries.create_index("created_at")
    await db.event_agents.create_index("created_at")
    await db.copy_relationships.create_index([("copier_id", 1), ("trader_id", 1)], unique=True)

    # Start background tasks
    asyncio.create_task(signal_generation_task())
    asyncio.create_task(price_broadcast_task())

    logger.info("AlphaAI Platform started successfully")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Clean up database connections on shutdown."""
    logger.info("AlphaAI Platform shutting down...")
    client.close()
    logger.info("Database connection closed")
