"""
AlphaAI Worker — Standalone background process for signal generation,
agent workers, price broadcasts, strategy alerts, and cron jobs.

Usage:  python worker.py
Runs continuously alongside the FastAPI API server.
"""
import asyncio
import logging
import os
import sys
import signal as signal_mod
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from database import db, client, logger
from config.demo import init_db as init_demo_config_db, is_demo_mode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
worker_logger = logging.getLogger("AlphaAI.Worker")

_shutdown = False


def handle_shutdown(signum, frame):
    global _shutdown
    worker_logger.info(f"Received signal {signum}, shutting down gracefully...")
    _shutdown = True


signal_mod.signal(signal_mod.SIGTERM, handle_shutdown)
signal_mod.signal(signal_mod.SIGINT, handle_shutdown)


async def signal_generation_loop():
    """Periodically generates AI trading signals."""
    from services.signal_service import signal_service
    worker_logger.info("Signal generation loop started (every 300s)")
    while not _shutdown:
        try:
            await signal_service.generate_signals()
            worker_logger.info("Signal generation cycle complete")
        except Exception as e:
            worker_logger.error(f"Signal generation error: {e}")
        await asyncio.sleep(300)


async def agent_workers_loop():
    """Runs the 4 AI agent workers on schedule."""
    from cron.agent_workers import start_agent_workers
    worker_logger.info("Agent workers started")
    try:
        await start_agent_workers()
    except Exception as e:
        worker_logger.error(f"Agent workers error: {e}")


async def price_broadcast_loop():
    """Broadcasts live prices to WebSocket clients every 30s."""
    from services.websocket_manager import manager
    from services.market_data import get_top_coins
    worker_logger.info("Price broadcast loop started (every 30s)")
    while not _shutdown:
        try:
            if manager.active_connections:
                prices = await get_top_coins()
                if prices:
                    await manager.broadcast_all({"type": "price_update", "data": prices})
        except Exception as e:
            worker_logger.error(f"Price broadcast error: {e}")
        await asyncio.sleep(30)


async def strategy_alerts_loop():
    """Generates strategy alerts for followed strategies."""
    import random
    from datetime import datetime, timezone
    from routes.follow_notifications import notify_followers
    worker_logger.info("Strategy alerts loop started (every 60-120s)")

    ALERT_TEMPLATES = [
        ("{name} triggered LONG signal at ${price:,.2f} (confidence: {conf}%)", "signal"),
        ("{name} triggered SHORT signal at ${price:,.2f} (confidence: {conf}%)", "signal"),
        ("{name} closed position — PnL: +${pnl:,.2f} (+{pct:.1f}%)", "signal"),
        ("{name} hit take-profit target — total P&L: +${pnl:,.2f}", "signal"),
    ]

    while not _shutdown:
        try:
            followed_ids = await db.followed_strategies.distinct("strategy_id")
            if followed_ids:
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
        except Exception as e:
            worker_logger.error(f"Strategy alert error: {e}")
        await asyncio.sleep(random.randint(60, 120))


async def weekly_digest_loop():
    """Runs the weekly digest email scheduler."""
    from cron.weekly_digest import start_weekly_digest_scheduler
    worker_logger.info("Weekly digest scheduler started")
    try:
        await start_weekly_digest_scheduler()
    except Exception as e:
        worker_logger.error(f"Weekly digest error: {e}")


async def rule_engine():
    """Runs the alert rule engine."""
    from services.rule_engine import rule_engine_loop, init_db as init_rule_db
    init_rule_db(db)
    worker_logger.info("Rule engine started")
    try:
        await rule_engine_loop()
    except Exception as e:
        worker_logger.error(f"Rule engine error: {e}")


async def worker_heartbeat():
    """Writes heartbeat to DB so the API health check can verify worker is running."""
    worker_logger.info("Worker heartbeat started (every 60s)")
    while not _shutdown:
        try:
            from datetime import datetime, timezone
            await db.system_config.update_one(
                {"key": "worker_heartbeat"},
                {"$set": {
                    "key": "worker_heartbeat",
                    "last_beat": datetime.now(timezone.utc).isoformat(),
                    "pid": os.getpid(),
                    "status": "running",
                }},
                upsert=True,
            )
        except Exception as e:
            worker_logger.error(f"Heartbeat error: {e}")
        await asyncio.sleep(60)


async def main():
    worker_logger.info("=" * 60)
    worker_logger.info("AlphaAI Worker starting up...")
    worker_logger.info(f"  DEMO_MODE = {os.getenv('DEMO_MODE', 'not set')}")
    worker_logger.info(f"  LIVE_MODE = {os.getenv('LIVE_MODE', 'not set')}")
    worker_logger.info(f"  PID       = {os.getpid()}")
    worker_logger.info("=" * 60)

    init_demo_config_db(db)

    demo = await is_demo_mode()
    worker_logger.info(f"System mode: {'DEMO' if demo else 'LIVE'}")

    tasks = [
        asyncio.create_task(signal_generation_loop()),
        asyncio.create_task(agent_workers_loop()),
        asyncio.create_task(price_broadcast_loop()),
        asyncio.create_task(strategy_alerts_loop()),
        asyncio.create_task(weekly_digest_loop()),
        asyncio.create_task(rule_engine()),
        asyncio.create_task(worker_heartbeat()),
    ]

    worker_logger.info(f"Worker started with {len(tasks)} background tasks")

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        worker_logger.info("Worker interrupted")
    finally:
        worker_logger.info("Worker shutting down...")
        client.close()
        worker_logger.info("Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
