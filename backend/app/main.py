# -*- coding: utf-8 -*-
"""Vibe2Nite — FastAPI application factory."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.docs import render_branded_docs
from app.routers import admin, feedback, vibes
from app.routers import vibes_extras
from app.routers import intel, rewards
from app.routers import notifications, ws, venues_ext
from app.routers import forecast as forecast_router
from app.routers import intel_flags, launch as launch_router
from app.routers import global_scale
from app.routers import claims as claims_router
from app.services.scheduler import start_scheduler, stop_scheduler

settings = get_settings()

# ---------------------------------------------------------------------------
# OpenAPI description (Markdown, shown inside the branded Swagger header)
# ---------------------------------------------------------------------------
DESCRIPTION = """
**Real-time nightlife recommendations powered by the Vibe Score.**

Vibe2Nite ranks venues using a weighted mix of signals — *manual score*,
*social activity*, *user votes*, *time prediction* and *venue boost* — and
returns the three spots worth your night: **best overall**, **live music**,
and a **hidden gem**.

---
### Vibe Score
```
score = manual_score*0.25 + social_activity*0.25 + user_votes*0.25 + time_prediction*0.15 + venue_boost*0.10
```
Capped at **10**. Crowd levels: `≥ 8 busy` · `≥ 5 medium` · `< 5 dead`.
""".strip()


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=__version__,
        description=DESCRIPTION,
        docs_url=None,        # replaced by custom branded docs
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static brand assets
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/api/static", StaticFiles(directory=static_dir), name="static")

    # Ensure tables exist (migrations are the source of truth, but this keeps
    # dev-boot resilient even before alembic runs).
    Base.metadata.create_all(bind=engine)

    # Routers — every business path under /api for ingress routing
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
    # WebSocket router — no prefix (clients connect to /ws/vibe/{id})
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

    @app.get("/api", include_in_schema=False)
    def api_root():
        return RedirectResponse(url="/api/docs")

    # Background signal-refresh scheduler
    @app.on_event("startup")
    async def _v2n_startup() -> None:
        import asyncio
        from app.services.ws_manager import manager as _wsm
        _wsm.bind_loop(asyncio.get_event_loop())
        start_scheduler()

    @app.on_event("shutdown")
    async def _v2n_shutdown() -> None:
        stop_scheduler()

    return app


app = create_app()
