# My-AlphaAI — Product Requirements Document

## Original Problem Statement
Build a production-ready AI-powered crypto trading signal platform with live agent workers, email digests, strategy marketplace, and full LIVE/DEMO mode control.

## Architecture
- **Frontend**: React (CRA + Craco), Tailwind CSS, Framer Motion, Recharts, Shadcn UI
- **Backend**: FastAPI, Motor (Async MongoDB), asyncio background workers
- **External Services**: Resend (Email), CoinGecko (Prices), Stripe (Payments), OpenAI/LiteLLM (Signal analysis)

## What's Been Implemented

### Phases 1-8: Core Platform through True LIVE Mode (Complete)
- Full auth, tiered access, strategy marketplace, leaderboard, copy trading, Stripe billing
- 4 AI background agent workers, demo mode toggle, WebSocket alerts, weekly digest
- Build automation, LIVE/DEMO mode system, Live Signals/Agents/Dashboard/Alerts/Analytics pages
- Admin auto-elevation, admin badge, admin login

### Phase 9: Frontend Routing Separation & Route Guards (Complete)
- AppLayout.jsx + MarketingLayout.jsx + RouteGuards.jsx
- React Router v6 nested routes with Outlet pattern

### Phase 10: Guided Tour for Demo Mode (Complete)
- 8-step interactive tour with spotlight highlighting, localStorage persistence, Restart Tour button

### Phase 11: Tour Analytics Tracking (Complete)
- POST /api/analytics/tour + GET /api/analytics/tour/summary
- TourAnalyticsPage at /admin/tour-analytics with KPIs, funnel, dropoff, daily charts

### Phase 12: Admin Link on Marketing Header (Complete - Feb 2026)
- Desktop: Shield icon + "Admin" text link in marketing nav, subtle zinc-500 with purple hover
- Mobile: Full-width row item below "Get Started" in hamburger menu
- Always visible on public pages (/, /leaderboard, /pricing), hidden inside app shell
- Redirect flow: /admin → /login (with state.from) → after login → /admin
- Fixed PublicOnlyRoute to respect location.state.from for redirect-after-login flows
- 12/12 frontend tests passed

## Backlog
- P1: Milestone Performance Alerts (Resend emails on ATH, +5% daily, stop-loss)
- P2: Full Portfolio Performance page with equity curve charts
- P2: Public Strategy Social Cards (dynamic OG images)
- P2: CoinGecko rate-limit mitigation
- P3: Sepolia Smart Contract deployment
- P3: User retention analytics & task queue migration
- Refactoring: Extract startup lifecycle from server.py; delete unused Navigation.jsx
