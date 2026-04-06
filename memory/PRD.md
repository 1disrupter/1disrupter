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
- Automated frontend build in FastAPI startup hook with yarn -> npm fallback chain
- Build artifacts copied to /var/www/html/ for NGINX serving
- Graceful fallback: if no build tool available, uses pre-committed build artifacts

### Phase 4: Full LIVE/DEMO Mode System (Complete - Apr 6, 2026)
- GET/POST /api/system/mode — single source of truth for system mode
- Mode-aware endpoints for alerts, events, agents, analytics
- Demo generators: services/demo_generators.py
- useSystemMode() hook, DemoModeBanner, mode badges on all pages

### Phase 5: Live Signals Page (Complete - Apr 6, 2026)
- /live-signals route with real-time vertical signal feed
- Stats bar, signal table, mode-aware LIVE/DEMO badges, auto-refresh

### Phase 6: Live Agent Performance Page (Complete - Apr 6, 2026)
- LiveAgentPerformance.jsx with 4-metric cards per agent
- Agents page renders live component in LIVE mode, placeholder in DEMO

### Phase 7: Admin Login & Auto-Elevation (Complete - Apr 6, 2026)
- Admin users auto-elevated to elite tier with is_pro=true, is_elite=true
- Admin Badge (purple Shield), Admin Login link in mobile menu
- useSystemMode() overrides demo mode to live for admin users

### Phase 8: True LIVE Mode for Alerts, Analytics, Dashboard (Complete - Apr 6, 2026)
- LiveAlerts.jsx, LiveAnalytics.jsx, LiveDashboard.jsx
- Backend endpoints: /api/analytics/live, /api/dashboard/live
- All pages: no demo imports in LIVE mode

### Phase 9: Frontend Routing Separation & Route Guards (Complete - Feb 2026)
- **AppLayout.jsx**: Authenticated navigation shell (Dashboard, Live Signals, Research, Strategy Lab, AI Agents, More dropdown with Alerts/Simulation/Event Agents/Marketplace/Copy Trading/Following/Referrals/Leaderboard/Pricing + Admin section, user dropdown, system mode badge, DemoModeBanner, MobileBottomNav)
- **MarketingLayout.jsx**: Public navigation shell (Home, Leaderboard, Pricing, Sign In/Get Started; shows "Dashboard" button for already-authenticated users)
- **RouteGuards.jsx**: ProtectedRoute (redirects to /login unless authenticated or in demo mode), PublicOnlyRoute (redirects to /dashboard if already authenticated)
- **App.js refactored**: React Router v6 nested routes with <Outlet /> pattern. Public routes wrapped in MarketingLayout, authenticated routes wrapped in ProtectedRoute + AppLayout
- Old monolithic Navigation.jsx no longer used in routing (retained in codebase for reference)
- MobileBottomNav only appears on authenticated app routes
- All 14 frontend tests passed (100%)

## Key Endpoints
- GET /api/system/mode — system mode status
- POST /api/system/mode?admin_key=... — toggle mode
- GET /api/alerts/live — mode-aware alerts
- GET /api/events/live — mode-aware events
- GET /api/agents/performance — mode-aware agent stats
- GET /api/analytics/live — mode-aware analytics
- GET /api/dashboard/live — mode-aware dashboard
- GET /api/auth/me — user profile

## Key DB Collections
- system_config — demo_mode flag
- trading_signals — real signals from agent workers
- event_agents — agent configurations
- analytics_events — conversion/tracking analytics
- weekly_digest_logs — email delivery logs

## Backlog
- P1: Milestone Performance Alerts (Resend emails on ATH, +5% daily, stop-loss)
- P2: Full Portfolio Performance page with equity curve charts
- P2: Public Strategy Social Cards (dynamic OG images)
- P2: CoinGecko rate-limit mitigation
- P3: Sepolia Smart Contract deployment
- P3: User retention analytics & task queue migration
- Refactoring: Extract startup lifecycle from server.py into startup.py
- Cleanup: Delete unused Navigation.jsx once layout split is fully validated
