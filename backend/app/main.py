# -*- coding: utf-8 -*-
"""Vibe2Nite — FastAPI application factory."""
import os

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.docs import render_branded_docs

# Routers
from app.routers import (
    admin, feedback, vibes, vibes_extras, intel, rewards,
    notifications, ws, venues_ext, forecast as forecast_router,
    intel_flags, launch as launch_router, global_scale,
    claims as claims_router, owner as owner_router
)

# Scheduler
from app.services.scheduler import start_scheduler, stop_scheduler

# WebSocket manager (new)
from app.websocket.manager import manager as ws_manager

settings = get_settings()


# ---------------------------------------------------------------------------
# OpenAPI description (Markdown)
# ---------------------------------------------------------------------------
DESCRIPTION = """
**Real-time nightlife recommendations powered by the Vibe Score.**

Vibe2Nite ranks venues using a weighted mix of signals — *manual score*,
*social activity*, *user votes*, *time prediction* and *venue boost* — and
returns the three spots worth your night: **best overall**, **live music**,
and a **hidden gem**.

---
### Vibe Score
Capped at **10**. Crowd levels: `≥ 8 busy` · `≥ 5 medium` · `< 5 dead`.
""".strip()


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=__version__,
        description=DESCRIPTION,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    # CORS — allow custom domain, production Vercel URL, all Vercel previews,
    # and local dev. Regex covers every preview deploy without a redeploy.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://vibe2nite.com",
            "https://www.vibe2nite.com",
            "https://api.vibe2nite.com",
            "https://1disrupter.vercel.app",
            "http://localhost:3000",
            "http://localhost:3001",
        ],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static brand assets
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/api/static", StaticFiles(directory=static_dir), name="static")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # -----------------------------------------------------------------------
    # Routers (FIXED INDENTATION)
    # -----------------------------------------------------------------------
    app.include_router(vibes.router, prefix="/api")
    app.include_router(vibes_extras.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")
    app.include_router(intel.router, prefix="/api")
    app.include_router(rewards.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")
    app.include_router(venues_ext.router, prefix="/api")
    app.include_router(forecast_router.router, prefix="/api")
    app.include_router(intel_flags.router, prefix="/api")
    app.include_router(launch_router.city_router, prefix="/api")
    app.include_router(launch_router.venues_router, prefix="/api")
    app.include_router(launch_router.triggers_router, prefix="/api")
    app.include_router(launch_router.inbox_router, prefix="/api")
    app.include_router(global_scale.osm_router, prefix="/api")
    app.include_router(global_scale.enrich_router, prefix="/api")
    app.include_router(global_scale.discovery_router, prefix="/api")
    app.include_router(claims_router.router, prefix="/api")
    app.include_router(owner_router.router, prefix="/api")

    # WebSocket router
    app.include_router(ws.router)

    # Health
    @app.get("/api/health", tags=["meta"], summary="Service heartbeat")
    def health():
        from datetime import datetime, timezone
        return {
            "status": "ok",
            "service": "vibe2nite",
            "version": __version__,
            "time": datetime.now(timezone.utc).isoformat(),
        }

    # Branded docs
    @app.get("/api/docs", include_in_schema=False)
    def branded_docs():
        return render_branded_docs(
            app,
            openapi_url="/api/openapi.json",
            brand_css_url="/api/static/vibe2nite.css",
        )

    @app.get("/docs", include_in_schema=False)
    def docs_redirect():
        return RedirectResponse(url="/api/docs")

    @app.get("/admin/listAdminVenues", include_in_schema=False)
    def list_admin_venues_redirect():
        return RedirectResponse(url="/api/admin/venues")

    @app.get("/api", include_in_schema=False)
    def api_root():
        return RedirectResponse(url="/api/docs")

    # -----------------------------------------------------------------------
    # Background Schedulers (startup + shutdown)
    # -----------------------------------------------------------------------
    @app.on_event("startup")
    async def _v2n_startup() -> None:
        import asyncio
        from app.services.ws_manager import manager as _wsm
        from app.services.vibe_updater import run_vibe_updater

        _wsm.bind_loop(asyncio.get_event_loop())
        start_scheduler()

        # Start vibe updater (every 5 minutes)
        asyncio.create_task(run_vibe_updater())

    @app.on_event("shutdown")
    async def _v2n_shutdown() -> None:
        stop_scheduler()

    return app


# ---------------------------------------------------------------------------
# Create app instance
# ---------------------------------------------------------------------------
app = create_app()


# ---------------------------------------------------------------------------
# WebSocket endpoint (new real-time vibe channel)
# ---------------------------------------------------------------------------
@app.websocket("/ws/vibe")
async def vibe_socket(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        ws_manager.disconnect(websocket)


