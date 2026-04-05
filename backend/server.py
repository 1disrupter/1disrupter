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
from services.alerts_manager import alerts_manager
from services.rule_engine import rule_engine_loop, init_db as init_rule_engine_db, get_active_alerts

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
# web3_routes disabled for SaaS-only deployment (Phase 2 Web3)
# from routes.web3_routes import router as web3_router
from routes.event_agents import router as event_agents_router
from routes.marketing import router as marketing_router
from routes.payments import router as payments_router
from routes.analytics_routes import router as analytics_router
from routes.websocket import router as websocket_router
from routes.notifications import router as notifications_router
from routes.follow_notifications import router as follow_notif_router
from routes.traffic import router as traffic_router, init_db as init_traffic_db
from routes.mobile_optimization import router as mobile_opt_router, init_db as init_mobile_opt_db
from routes.subscription import router as subscription_router, init_db as init_subscription_db
from routes.attestation import router as attestation_router, init_db as init_attestation_db
from routes.beta import router as beta_router
from routes.exchange import router as exchange_router
from routes.marketplace import router as marketplace_router
from routes.marketplace_billing import router as marketplace_billing_router
from routes.execution import router as execution_router
from routes.billing import router as billing_router
from routes.invoices import router as invoices_router
from routes.ws_events import router as ws_events_router
from routes.waitlist import router as waitlist_router
from routes.digest import router as digest_router
from routes.live_mode import router as live_mode_router
from routes.agents_api import router as agents_api_router
from services.stripe_webhook_handler import init_db as init_webhook_handler_db
from cron.performance_attestor import init_db as init_attestor_db

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
# web3_router disabled for SaaS-only deployment
# app.include_router(web3_router)
app.include_router(event_agents_router)
app.include_router(marketing_router)
app.include_router(payments_router)
app.include_router(analytics_router)
app.include_router(websocket_router)
app.include_router(notifications_router)
app.include_router(follow_notif_router)
app.include_router(traffic_router)
app.include_router(mobile_opt_router)
app.include_router(subscription_router)
app.include_router(attestation_router)
app.include_router(beta_router)
app.include_router(exchange_router)
app.include_router(marketplace_router)
app.include_router(marketplace_billing_router)
app.include_router(execution_router)
app.include_router(billing_router)
app.include_router(invoices_router)
app.include_router(ws_events_router)
app.include_router(waitlist_router)
app.include_router(digest_router)
app.include_router(live_mode_router)
app.include_router(agents_api_router)


# ============= HEALTH CHECK =============
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy"}

async def signal_generation_task():
    """Periodically generates AI trading signals."""
    while True:
        try:
            await signal_service.generate_signals()
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
                    await manager.broadcast_all({
                        "type": "price_update",
                        "data": prices
                    })
        except Exception as e:
            logger.error(f"Price broadcast error: {e}")
        await asyncio.sleep(30)


async def strategy_alerts_task():
    """Periodically generates strategy alerts for followed strategies."""
    import random
    from datetime import datetime, timezone
    from routes.follow_notifications import notify_followers

    ALERT_TEMPLATES = [
        ("{name} triggered LONG signal at ${price:,.2f} (confidence: {conf}%)", "signal"),
        ("{name} triggered SHORT signal at ${price:,.2f} (confidence: {conf}%)", "signal"),
        ("{name} closed position — PnL: +${pnl:,.2f} (+{pct:.1f}%)", "signal"),
        ("{name} hit take-profit target — total P&L: +${pnl:,.2f}", "signal"),
    ]

    while True:
        try:
            # Find strategies that have followers
            followed_ids = await db.followed_strategies.distinct("strategy_id")
            if followed_ids:
                # Pick a random strategy to generate an alert for
                strategy_id = random.choice(followed_ids)
                strat = await db.strategy_leaderboard.find_one({"id": strategy_id}, {"_id": 0})
                if strat:
                    name = strat.get("name", strategy_id[:8])
                    asset = strat.get("asset", "BTC/USDT")
                    price = round(random.uniform(60000, 72000) if "BTC" in asset
                                  else random.uniform(3200, 4000) if "ETH" in asset
                                  else random.uniform(100, 300), 2)
                    tpl, ntype = random.choice(ALERT_TEMPLATES)
                    msg = tpl.format(
                        name=name, price=price,
                        conf=random.randint(70, 95),
                        pnl=round(random.uniform(100, 2000), 2),
                        pct=round(random.uniform(1, 8), 1),
                    )
                    await notify_followers(strategy_id, msg, ntype)
                    logger.info(f"Strategy alert generated for {strategy_id[:8]}")
        except Exception as e:
            logger.error(f"Strategy alert task error: {e}")
        # Run every 60-120 seconds
        await asyncio.sleep(random.randint(60, 120))


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
    init_traffic_db(db)
    init_rule_engine_db(db)
    init_mobile_opt_db(db)
    init_subscription_db(db)
    init_attestation_db(db)
    init_webhook_handler_db(db)
    init_attestor_db(db)

    # Init demo mode config
    from config.demo import init_db as init_demo_config_db
    init_demo_config_db(db)

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
    await db.followed_strategies.create_index([("user_id", 1), ("strategy_id", 1)], unique=True)
    await db.notifications_inbox.create_index([("user_id", 1), ("created_at", -1)])
    await db.traffic_events.create_index([("timestamp", -1)])
    await db.traffic_events.create_index([("type", 1, )])
    await db.traffic_events.create_index([("user_id", 1)])
    await db.stripe_webhook_events.create_index("event_id", unique=True)
    await db.analytics_events.create_index([("timestamp", -1)])
    await db.analytics_events.create_index([("event_type", 1)])
    await db.stripe_webhook_events.create_index([("processed_at", -1)])
    await db.waitlist.create_index("email", unique=True)

    # Create indexes for weekly digest
    await db.weekly_digest_logs.create_index([("sent_at", -1)])
    await db.weekly_digest_logs.create_index([("user_id", 1)])
    await db.digest_preferences.create_index("email", unique=True)

    # ── Deploy frontend build to NGINX html directory ──
    # Production NGINX serves from /var/www/html/ — copy React build there
    # Also install custom nginx.conf for SPA routing
    import shutil
    import subprocess
    build_dir = Path(__file__).parent.parent / "frontend" / "build"
    nginx_dir = Path("/var/www/html")
    nginx_conf_src = Path(__file__).parent.parent / "frontend" / "nginx.conf"
    nginx_conf_dest = Path("/etc/nginx/sites-available/default")

    if build_dir.exists() and nginx_dir.exists():
        try:
            for item in nginx_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            for item in build_dir.iterdir():
                dest = nginx_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            logger.info(f"Deployed frontend build to {nginx_dir}")
        except Exception as e:
            logger.warning(f"Could not copy frontend build to nginx: {e}")

    # Install custom nginx config for SPA routing + API proxy
    if nginx_conf_src.exists() and nginx_conf_dest.exists():
        try:
            shutil.copy2(nginx_conf_src, nginx_conf_dest)
            subprocess.run(["nginx", "-s", "reload"], capture_output=True, timeout=5)
            logger.info("Installed custom nginx.conf and reloaded NGINX")
        except Exception as e:
            logger.warning(f"Could not install nginx config: {e}")

    # Start background tasks
    asyncio.create_task(signal_generation_task())
    asyncio.create_task(price_broadcast_task())
    asyncio.create_task(strategy_alerts_task())
    asyncio.create_task(rule_engine_loop())

    from cron.weekly_digest import start_weekly_digest_scheduler
    asyncio.create_task(start_weekly_digest_scheduler())

    from cron.agent_workers import start_agent_workers
    asyncio.create_task(start_agent_workers())

    logger.info("AlphaAI Platform started successfully")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Clean up database connections on shutdown."""
    logger.info("AlphaAI Platform shutting down...")
    client.close()
    logger.info("Database connection closed")
