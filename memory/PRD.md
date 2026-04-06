# My-AlphaAI — Product Requirements Document

## Original Problem Statement
Build a production-ready AI-powered crypto trading signal platform with live agent workers, email digests, strategy marketplace, and full LIVE/DEMO mode control.

## Architecture
- **Frontend**: React (CRA + Craco), Tailwind CSS, Framer Motion, Recharts, Shadcn UI
- **Backend**: FastAPI, Motor (Async MongoDB), asyncio background workers
- **Worker**: Standalone `worker.py` running signal generation, agent workers, price broadcasts, strategy alerts, weekly digest, rule engine, and heartbeat
- **External Services**: Resend (Email), CoinGecko (Prices), Stripe (Payments), OpenAI/LiteLLM (Signal analysis)
- **Infra**: NGINX reverse proxy, Supervisor-managed processes (backend, frontend, worker, mongodb)

## What's Been Implemented

### Phases 1-11 (Complete — see previous PRD versions)

### Phase 12: Admin Link on Marketing Header (Complete)
- Admin link on public marketing nav, redirect-after-login flow

### Phase 13: Production Deploy with Worker + Live Mode (Complete - Feb 2026)
- **`.env`**: `DEMO_MODE=false`, `LIVE_MODE=true`
- **DB**: `system_config.demo_mode.enabled = false` (live mode active)
- **Admin Toggle Routes**: `POST /api/admin/toggle-demo?admin_key=...` and `POST /api/admin/toggle-live?admin_key=...` — convenience endpoints for instant mode switching
- **Standalone Worker** (`worker.py`): Runs 7 background tasks — signal generation (every 300s), 4 AI agent workers, price broadcast (every 30s), strategy alerts (every 60-120s), weekly digest scheduler, rule engine, heartbeat (every 60s)
- **Worker Supervisor**: Added `/etc/supervisor/conf.d/worker.conf` — `autorestart=true`, shares env with API
- **Worker Heartbeat**: Writes to `system_config.worker_heartbeat` every 60s so API can verify worker health
- **Enhanced Health Check** (`GET /api/health`): Returns mode, worker status (running/stale + heartbeat age), signal freshness (latest signal age + agent + symbol), total signal count
- Signal freshness: handles timezone-naive datetimes from MongoDB
- Worker generates real-time signals (BTC, ETH, SOL, AVAX) via Momentum Scanner + Sentiment Analyzer agents
- All verified: mode=live, worker=running, signals=fresh, total_signals=6153+

## Key Processes (Production)
1. `uvicorn server:app --host 0.0.0.0 --port 8001` — FastAPI API
2. `python worker.py` — Background worker (signals, agents, cron)
3. Both share same `.env` and MongoDB

## Key Endpoints
- `GET /api/health` — Detailed health (mode, worker, signals, totals)
- `GET /health` — Simple health check
- `POST /api/admin/toggle-demo?admin_key=...` — Enable demo mode
- `POST /api/admin/toggle-live?admin_key=...` — Enable live mode
- `GET/POST /api/system/mode` — System mode read/write
- `POST /api/analytics/tour` — Tour event tracking
- `GET /api/analytics/tour/summary` — Tour analytics

## Key DB Collections
- system_config (demo_mode, worker_heartbeat)
- trading_signals, event_agents, analytics_events, tour_events, weekly_digest_logs

## Backlog
- P1: Milestone Performance Alerts (Resend emails on ATH, +5% daily, stop-loss)
- P2: Full Portfolio Performance page with equity curve charts
- P2: Public Strategy Social Cards (dynamic OG images)
- P2: CoinGecko rate-limit mitigation
- P3: Sepolia Smart Contract deployment
- P3: User retention analytics & task queue migration
- Refactoring: Extract startup lifecycle from server.py; delete unused Navigation.jsx
