# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion by emphasizing the "pain of being late" to market moves. Features include Free Tier (15-min signal delay), Pro/Elite paid tiers, Copy Trading, AI Signal Engine, and a high-conversion landing page.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Framer Motion + Shadcn UI + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **3rd Party**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe (payments), Resend (emails)

## What's Been Implemented

### Phase 1-3 — Core Platform, Copy Trading, Landing Page (DONE)
### Phase 4-6 — Frontend Refactor, Conversion Optimizations, Nav & Mobile (DONE — 2026-03-28)
### Phase 7 — Dashboard Placeholder UI (DONE — 2026-03-28)
### Phase 8 — Backend Monolith Refactor (DONE — 2026-03-29)
### Phase 9 — Global Demo Mode (DONE — 2026-03-29)
### Phase 10 — Share Demo Link (DONE — 2026-03-29)

### Phase 11 — Demo Link Analytics (DONE — 2026-03-29)
- `lib/analytics.js` — swappable abstraction (`analytics.track()`) for PostHog/Mixpanel/custom backend
- Fires `demo_link_opened` event on `?demo=true` URL detection, once per session (sessionStorage guard)
- Payload: timestamp, referrer, userAgent, path, isAuthenticated
- Non-blocking: fire-and-forget with `keepalive: true`, queued retry on network failure
- Backend: `POST /api/analytics/events` batch endpoint stores events in `analytics_events` collection
- Verified: event stored in MongoDB with all fields

## Key Files
- `/app/frontend/src/lib/analytics.js` — Analytics abstraction
- `/app/frontend/src/contexts/DemoModeContext.jsx` — Demo mode + analytics tracking
- `/app/backend/routes/analytics_routes.py` — Batch events endpoint

## Credentials
- Admin: `admin@my-alpha-ai.com` / `Admin1234!`
- Test user: `demo_test2@my-alpha-ai.com` / `NewPass1234!`
- Demo URL: `{origin}/dashboard?demo=true`

## Backlog (P2)
- Wire up real backend data to replace mock placeholders
- Biometric Authentication for Mobile
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol to Sepolia mainnet
