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

### Phase 1-8: Core Platform through True LIVE Mode (Complete)
- Full auth, tiered access, strategy marketplace, leaderboard, copy trading, Stripe billing
- 4 AI background agent workers, demo mode toggle, WebSocket alerts, weekly digest
- Build automation, LIVE/DEMO mode system, Live Signals/Agents/Dashboard/Alerts/Analytics pages
- Admin auto-elevation, admin badge, admin login

### Phase 9: Frontend Routing Separation & Route Guards (Complete - Feb 2026)
- AppLayout.jsx + MarketingLayout.jsx + RouteGuards.jsx
- React Router v6 nested routes with Outlet pattern

### Phase 10: Guided Tour for Demo Mode (Complete - Feb 2026)
- 8-step interactive tour: Welcome → Dashboard → Live Signals → Research → Strategy Lab → AI Agents → Demo Badge → Upgrade CTA
- Spotlight highlighting, auto-start for new users, localStorage persistence, Restart Tour button

### Phase 11: Tour Analytics Tracking (Complete - Feb 2026)
- **Backend**: `POST /api/analytics/tour` logs events (step_view, step_next, step_back, skip, complete, cta_click, restart) with session_id to `tour_events` collection
- **Backend**: `GET /api/analytics/tour/summary?days=N` returns aggregated funnel, dropoff, daily trends, completion/CTA rates
- **Frontend**: GuidedTour.jsx fires analytics at every interaction (auto-start, next, back, skip, CTA, restart)
- **Admin Page**: TourAnalyticsPage.jsx at `/admin/tour-analytics` — KPI cards (Starts, Completions, CTA Clicks, Skip Rate), Step Funnel chart, Drop-off Points chart, Daily Activity area chart, Step Breakdown table with retention bars
- Tour Analytics link in More dropdown → Admin section
- 20/20 backend tests + all frontend tests passed

## Key Endpoints
- GET/POST /api/system/mode — system mode control
- GET /api/alerts/live, /api/events/live, /api/agents/performance, /api/analytics/live, /api/dashboard/live
- POST /api/analytics/tour — track tour events
- GET /api/analytics/tour/summary — aggregated tour analytics
- GET /api/auth/me — user profile

## Key DB Collections
- system_config, trading_signals, event_agents, analytics_events, weekly_digest_logs
- **tour_events** — guided tour interaction tracking (event_type, step_id, step_index, session_id, timestamp, date)

## Backlog
- P1: Milestone Performance Alerts (Resend emails on ATH, +5% daily, stop-loss)
- P2: Full Portfolio Performance page with equity curve charts
- P2: Public Strategy Social Cards (dynamic OG images)
- P2: CoinGecko rate-limit mitigation
- P3: Sepolia Smart Contract deployment
- P3: User retention analytics & task queue migration
- Refactoring: Extract startup lifecycle from server.py; delete unused Navigation.jsx
