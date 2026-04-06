# My-AlphaAI — Product Requirements Document

## Original Problem Statement
Build a production-ready AI-powered crypto trading signal platform with live agent workers, email digests, strategy marketplace, and full LIVE/DEMO mode control.

## Core Requirements
- Real-time AI trading signals from 4 agent workers (Momentum Scanner, Sentiment Analyzer, Whale Tracker, Volatility Engine)
- CoinGecko-powered live market data
- Weekly performance digest emails via Resend
- Admin-controlled LIVE/DEMO mode toggle affecting all pages
- User authentication with JWT, tiered access (Free/Pro/Elite)
- Strategy marketplace, leaderboard, copy trading
- Stripe-powered billing

## Architecture
- **Frontend**: React (CRA + Craco), Tailwind CSS, Framer Motion, Recharts, Shadcn UI
- **Backend**: FastAPI, Motor (Async MongoDB), asyncio background workers
- **External Services**: Resend (Email), CoinGecko (Prices), Stripe (Payments), OpenAI/LiteLLM (Signal analysis)
- **Infra**: NGINX reverse proxy, Supervisor-managed processes, automated frontend builds on startup

## What's Been Implemented

### Phase 1: Core Platform (Complete)
- User auth (JWT), tiered access, admin panel
- Dashboard with portfolio stats, signal preview, price charts
- Strategy marketplace, leaderboard, copy trading
- Stripe billing integration

### Phase 2: Live Mode & Agent Workers (Complete)
- 4 AI background agent workers generating real signals from CoinGecko data
- Demo mode toggle with admin API control
- Real-time WebSocket alerts
- Weekly Performance Digest email system (Resend + cron)

### Phase 3: Build Automation (Complete - Apr 5-6, 2026)
- Automated frontend build in FastAPI startup hook with yarn → npm fallback chain
- Build artifacts copied to `/var/www/html/` for NGINX serving
- Creates NGINX directory if missing, uses `print()` for deployment-visible logging
- Graceful fallback: if no build tool available, uses pre-committed build artifacts
- Pre-built React bundle committed to git (not gitignored) for production resilience
- Fixed `os` import issue, removed `npx` direct build (unreliable)

### Phase 4: Full LIVE/DEMO Mode System (Complete - Apr 6, 2026)
**Backend:**
- `GET /api/system/mode` — single source of truth for system mode
- `POST /api/system/mode` — admin-only mode switch (live/demo)
- `GET /api/alerts/live` — real agent signals in LIVE, demo alerts in DEMO
- `GET /api/events/live` — real events in LIVE, demo events in DEMO
- `GET /api/agents/performance` — real agent stats in LIVE, demo stats in DEMO
- `GET /api/analytics/summary` — real signal analytics in LIVE, demo analytics in DEMO
- Demo generators: `services/demo_generators.py` (alerts, analytics, agent stats, events)

**Frontend:**
- `useSystemMode()` hook — mode, isDemo, isLive, setMode, loading
- Navigation badge: LIVE MODE (green) / DEMO MODE (purple)
- DemoModeBanner: global purple banner visible only in DEMO mode
- AlertsPage: "Live Alerts" vs "Demo Alerts" with mode-aware data
- AnalyticsPage: "LIVE DATA" vs "DEMO DATA" badge, real charts vs demo charts
- AgentsPage: LIVE/DEMO badge, mode-aware description
- AdminPage: System mode toggle (LIVE/DEMO switch)
- All hardcoded demo text conditionally hidden in LIVE mode

## Key Endpoints
- `GET /api/system/mode` — system mode status
- `POST /api/system/mode?admin_key=...` — toggle mode
- `GET /api/alerts/live` — mode-aware alerts
- `GET /api/events/live` — mode-aware events
- `GET /api/agents/performance` — mode-aware agent stats
- `GET /api/analytics/summary` — mode-aware analytics
- `GET /api/demo-mode/status` — legacy compat

## Key DB Collections
- `system_config` — demo_mode flag (single source of truth)
- `trading_signals` — real signals from agent workers
- `event_agents` — agent configurations
- `analytics_events` — conversion/tracking analytics
- `weekly_digest_logs` — email delivery logs

### Phase 5: Live Signals Page (Complete - Apr 6, 2026)
- Created `/live-signals` route with `LiveSignalsPage.jsx` — dedicated vertical real-time signal feed
- Shows stats bar (Total Signals, Long, Short counts), signal table with action/asset/confidence/agent/price/time
- Mode-aware: LIVE badge with real data, DEMO badge with synthetic data
- Removed toast notifications from WebSocket handler (`useStrategyAlerts.js`)
- Navigation: "Live Signals" in primary nav (Activity icon), Alerts moved to overflow menu
- Auto-refresh: 8s (live), 12s (demo)

### Phase 6: Live Agent Performance Page (Complete - Apr 6, 2026)
- Created `LiveAgentPerformance.jsx` — fetches `GET /api/agents/performance`, displays 4-metric cards (Accuracy, Win Rate, P&L, Trades) per agent
- Rewrote `AgentsPage.jsx`: LIVE mode renders `<LiveAgentPerformance />`, DEMO mode shows clean placeholder
- Removed all demo agent cards, demo stats components, demo imports
- No toasts on the page, auto-refresh every 15s

## Backlog
- P1: Agent Performance Leaderboard (rank by accuracy, win rate, P&L)
- P1: Milestone Performance Alerts (Resend emails on ATH, +5% daily, stop-loss)
- P2: Full Portfolio Performance page with equity curve charts
- P2: Public Strategy Social Cards (dynamic OG images)
- P2: CoinGecko rate-limit mitigation
- P3: Sepolia Smart Contract deployment
- P3: User retention analytics & task queue migration
- Refactoring: Extract startup lifecycle from server.py into startup.py
