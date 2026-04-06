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
- AppLayout.jsx: Authenticated nav shell with route guards
- MarketingLayout.jsx: Public nav shell (auth-aware)
- RouteGuards.jsx: ProtectedRoute + PublicOnlyRoute
- App.js refactored with React Router v6 nested routes + Outlet

### Phase 10: Guided Tour for Demo Mode (Complete - Feb 2026)
- **GuidedTour.jsx**: 8-step interactive tour overlay (Welcome, Dashboard, Live Signals, Research, Strategy Lab, AI Agents, Demo Mode badge, Upgrade CTA)
- Auto-starts after 800ms for new demo users (localStorage `alphaTourSeen` key)
- Spotlight highlighting on nav elements with purple glow effect
- Step progress dots with gradient active state
- Back/Next/Skip navigation, Close (X) button
- CTA final step with golden "Upgrade to Pro" button → navigates to /pricing
- "Restart Tour" button in More dropdown (desktop) and mobile menu (demo mode only)
- Does NOT appear in Live Mode or for admin users (useSystemMode check)
- All 15 frontend tests passed (100%)

## Key Endpoints
- GET /api/system/mode, POST /api/system/mode — system mode control
- GET /api/alerts/live, /api/events/live, /api/agents/performance, /api/analytics/live, /api/dashboard/live — mode-aware data
- GET /api/auth/me — user profile

## Key DB Collections
- system_config, trading_signals, event_agents, analytics_events, weekly_digest_logs

## Backlog
- P1: Milestone Performance Alerts (Resend emails on ATH, +5% daily, stop-loss)
- P2: Full Portfolio Performance page with equity curve charts
- P2: Public Strategy Social Cards (dynamic OG images)
- P2: CoinGecko rate-limit mitigation
- P3: Sepolia Smart Contract deployment
- P3: User retention analytics & task queue migration
- Refactoring: Extract startup lifecycle from server.py; delete unused Navigation.jsx
