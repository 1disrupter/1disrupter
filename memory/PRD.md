# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion by emphasizing the "pain of being late" to market moves. Features include Free Tier (15-min signal delay), Pro/Elite paid tiers, Copy Trading, AI Signal Engine, and a high-conversion landing page.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Framer Motion + Shadcn UI + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **3rd Party**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe (payments), Resend (emails)

## What's Been Implemented

### Phase 1 — Core Platform (DONE)
- JWT auth with email verification (Resend)
- Stripe subscriptions: Free / Pro ($49/mo) / Elite ($99/mo)
- AI Signal Engine with 15-min delay for free users
- Live & Paper Trading, Dashboard, Admin, Leaderboard

### Phase 2 — Copy Trading System (DONE)
- Follow/unfollow traders, Mirror/proportional modes, Stats tracking

### Phase 3 — Conversion & Landing Page (DONE)
- Animated splash screen, "early vs late" marketing, HeroVisualization
- 5-section landing page, pricing with urgency banner

### Phase 4 — Frontend Refactor (DONE — 2026-03-28)
- App.js reduced from 6,696 → 79 lines, 20+ pages extracted

### Phase 5 — Conversion Optimizations (DONE — 2026-03-28)
- "Start Free Demo" CTA, trust proof, updated pricing ($49/$99)

### Phase 6 — Nav & Mobile (DONE — 2026-03-28)
- Simplified public nav, full 13-item auth nav, mobile layout fixes

### Phase 7 — Dashboard Placeholder UI (DONE — 2026-03-28)
- 11 dashboard pages with polished placeholder UI, shared components

### Phase 8 — Backend Monolith Refactor (DONE — 2026-03-29)
- server.py → lightweight router, 20+ route modules, centralized models

### Phase 9 — Global Demo Mode (DONE — 2026-03-29)
- DemoModeContext with sessionStorage persistence
- Toggle in nav header (desktop + mobile), live simulation (3-5s updates)
- PRO gating bypass via effectivePro = demoMode || isPro
- All dashboard pages wired up with live-updating demo data

### Phase 10 — Share Demo Link (DONE — 2026-03-29)
- "Share Demo" button in nav header (desktop + mobile) — visible when demo mode is ON
- Generates shareable URL: `{origin}/dashboard?demo=true`
- Copies to clipboard with toast: "Demo link copied! Share it with anyone to explore AlphaAI instantly."
- `?demo=true` URL param auto-enables Demo Mode on any page load
- Unauthenticated demo visitors get full dashboard navigation
- All 11 dashboard pages accessible without authentication in demo mode
- "Sign Up Free" CTA shown to unauthenticated demo visitors
- Demo mode persists via sessionStorage across page navigation
- Closing banner (X) or toggling OFF disables demo mode and restores normal state

### Admin Route (DONE — 2026-03-28)
- POST /api/auth/admin/create

## File Structure
```
/app/frontend/src/
├── App.js                          # Routing shell + DemoModeProvider
├── components/
│   ├── DemoModeBanner.jsx          # Global demo mode banner
│   ├── PlaceholderUI.jsx
│   ├── Navigation.jsx              # Demo toggle + Share Demo button
│   └── ui/                         # Shadcn components
├── contexts/
│   ├── AuthContext.jsx
│   ├── DemoModeContext.jsx          # ?demo=true detection, shareDemoLink(), live sim
│   └── WalletContext.jsx
├── lib/
│   ├── constants.js, formatters.js, mockData.js
├── pages/                          # All pages demo-mode aware

/app/backend/
├── server.py                       # Lightweight router
├── database/__init__.py, models/schemas.py
├── routes/ (20+ modular files), services/
```

## Credentials
- Admin: `admin@my-alpha-ai.com` / `Admin1234!`
- Test user: `demo_test2@my-alpha-ai.com` / `NewPass1234!`
- Demo URL: `{origin}/dashboard?demo=true`

## Backlog (P2)
- Wire up real backend data to replace mock placeholders
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol to Sepolia mainnet
