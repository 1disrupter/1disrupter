# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion. Features: Free Tier (15-min delay), Pro/Elite paid tiers, Copy Trading, AI Signal Engine, high-conversion landing page, demo mode for viral sharing.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Framer Motion + Shadcn UI + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **3rd Party**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, Resend

## Implementation History

### Phase 1-3 — Core, Copy Trading, Landing (DONE)
### Phase 4-6 — Frontend Refactor, Conversion, Nav/Mobile (DONE — 2026-03-28)
### Phase 7 — Dashboard Placeholder UI (DONE — 2026-03-28)
### Phase 8 — Backend Monolith Refactor (DONE — 2026-03-29)
### Phase 9 — Global Demo Mode + Share Demo + Analytics Tracking (DONE — 2026-03-29)

### Phase 10 — Real Data Wiring (DONE — 2026-03-29)
All 8 dashboard pages wired with real backend API calls via shared `useApiData()` hook:
- **SimulationPage** → `/api/simulation/stats`, `/api/simulation/config`
- **AgentsPage** → `/api/agents`
- **EventAgentsPage** → `/api/agents/event-agents`
- **StrategyLabPage** → `/api/lab/strategies`
- **MarketplacePage** → `/api/lab/strategies`
- **ResearchEnginePage** → `/api/research/reports`, `/api/research/metrics`
- **ReferralPage** → `/api/referrals/stats`, `/api/referrals/activity`
- **AnalyticsPage** → `/api/analytics/summary`

Each page implements: loading skeleton → real data fetch → error fallback with retry → demo mode override.

### Phase 11 — Admin Analytics Dashboard (DONE — 2026-03-29)
- **Backend**: `GET /api/admin/analytics?admin_key=...&period=24h|7d|30d|all`
  - MongoDB aggregation pipeline on `analytics_events` collection
  - 60-second server-side cache for expensive queries
  - Metrics: demo opens, signup/pro conversion rates, K-factor, top referrers, pages per session, event breakdown
- **Frontend**: `/admin/analytics` page with:
  - 4 KPI cards (Demo Opens, Demo→Signup%, Demo→Pro%, K-Factor)
  - Demo Opens Over Time area chart
  - Entry Pages horizontal bar chart
  - Event Breakdown pie chart
  - Top Referrers list
  - Live Events stream (15s polling)
  - Conversion Funnel visualization
  - Time period filters (24h/7d/30d/all)
- **Access**: Admin-only via admin_key query parameter

## Key New Files
- `/app/frontend/src/lib/useApiData.js` — Shared fetch hook with skip/token/default
- `/app/frontend/src/pages/AdminAnalyticsPage.jsx` — Admin analytics dashboard
- `/app/frontend/src/components/PlaceholderUI.jsx` — Added LoadingSkeleton, ErrorState

## Credentials
- Admin: `admin@my-alpha-ai.com` / `Admin1234!`
- Admin key: `alphaai_admin_2026`
- Test user: `demo_test2@my-alpha-ai.com` / `NewPass1234!`
- Demo URL: `{origin}/dashboard?demo=true`

## Backlog (P2)
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol to Sepolia mainnet
