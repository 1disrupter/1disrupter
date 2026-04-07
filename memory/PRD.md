# My-AlphaAI — Product Requirements Document

## Original Problem Statement
Build a production-ready AI-powered crypto trading signal platform with live agent workers, email digests, strategy marketplace, and full LIVE/DEMO mode control.

## Architecture
- **Frontend**: React (CRA + Craco), Tailwind CSS, Framer Motion, Recharts, Shadcn UI
- **Backend**: FastAPI, Motor (Async MongoDB), asyncio background workers
- **Worker**: Standalone `worker.py` for signal generation, agent workers, price broadcasts, strategy alerts, weekly digest, rule engine
- **External Services**: Resend (Email), CoinGecko (Prices), Stripe (Payments), OpenAI/LiteLLM (Signal analysis)
- **Infra**: NGINX reverse proxy, Supervisor (backend + worker + frontend + mongodb)

## What's Been Implemented (Phases 1-13 Complete)
- Full auth, tiered access, strategy marketplace, leaderboard, copy trading, Stripe billing
- 4 AI background agent workers, LIVE/DEMO mode system, WebSocket alerts
- Build automation, Live Signals/Agents/Dashboard/Alerts/Analytics pages
- Admin auto-elevation, admin badge, admin login
- Frontend routing separation (AppLayout + MarketingLayout + RouteGuards)
- Guided Tour for Demo Mode with analytics tracking
- Admin link on marketing header with redirect-after-login flow
- Standalone worker.py with supervisor management
- Admin toggle-demo/toggle-live convenience endpoints
- Enhanced health check (worker heartbeat, signal freshness)

## Phase 14: Deployment Fix (Complete - Feb 2026)
- **Root cause**: `if nginx_conf_dest.exists()` guard silently skipped nginx config copy when the destination file didn't exist in production
- **Fix**: Removed guard, writes to `sites-available` + `sites-enabled` symlink, falls back to `conf.d/default.conf` only if sites-available path doesn't exist
- **Also**: Deploys build to `/usr/share/nginx/html` as fallback alongside `/var/www/html`
- **Also**: `nginx -t` test before reload, proper error logging for each step
- **Env**: `DEMO_MODE=false`, `LIVE_MODE=true`

## Backlog
- P1: Milestone Performance Alerts (Resend emails on ATH, +5% daily, stop-loss)
- P2: Full Portfolio Performance page, Strategy Social Cards, CoinGecko rate-limit mitigation
- P3: Sepolia Smart Contract deployment, retention analytics
- Refactoring: Extract startup lifecycle from server.py; delete unused Navigation.jsx
