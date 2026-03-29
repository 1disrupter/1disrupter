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
- Live & Paper Trading
- Dashboard with portfolio tracking
- Admin dashboard
- Leaderboard with tier restrictions

### Phase 2 — Copy Trading System (DONE)
- Follow/unfollow traders
- Mirror/proportional copy modes
- Stats tracking (copy_relationships collection)

### Phase 3 — Conversion & Landing Page (DONE)
- Animated cinematic splash screen (SplashScreen.jsx)
- Aggressive "early vs late" marketing copy
- HeroVisualization with candlestick chart
- 5-section landing page: Hero, Missed vs Captured, Free vs Paid Gap, Today's Signals, Social Proof, Final CTA
- Pricing page with urgency banner

### Phase 4 — Frontend Refactor (DONE — 2026-03-28)
- App.js reduced from 6,696 → 79 lines (routing shell)
- 20+ files extracted to pages/, components/, lib/, contexts/

### Phase 5 — Conversion Optimizations (DONE — 2026-03-28)
- Hero CTA → "Start Free Demo"
- Trust proof: "68% Win Rate — updated daily"
- CTA trust line: "No credit card required. Free tier included. Cancel anytime."
- Today's Entries: "Entries You Already Missed Today" + red LIVE urgency tag
- Pricing urgency banner + "Choose Your Edge" heading
- Pro = $49/mo, Elite = $99/mo (all references updated)

### Phase 6 — Nav & Mobile (DONE — 2026-03-28)
- Unauthenticated nav: Home | Leaderboard | Pricing | Sign In | Get Started
- Authenticated nav: Full 13-item dashboard nav
- Mobile: Hero text first, chart hidden on small screens

### Phase 7 — Dashboard Placeholder UI (DONE — 2026-03-28)
- All 11 dashboard pages updated with polished placeholder UI
- Consistent pattern: PageHeader + StatsRow + Mock data/charts/tables
- Shared components: PlaceholderUI.jsx, mockData.js

### Phase 8 — Backend Monolith Refactor (DONE — 2026-03-29)
- server.py reduced to lightweight router orchestrator (~156 lines)
- 20+ route modules in /app/backend/routes/
- Centralized Pydantic models in /app/backend/models/schemas.py
- Service layer in /app/backend/services/
- All 15+ API endpoint groups verified working

### Phase 9 — Global Demo Mode (DONE — 2026-03-29)
- DemoModeContext provider with global state (sessionStorage persistence)
- Toggle in nav header (desktop + mobile) with pill-shaped switch UI
- Subtle global banner: "Demo Mode: Data simulated for preview." with close button
- Live simulation: mock data updates every 3-5 seconds (signals, portfolio, agents, chart)
- PRO gating bypass: effectivePro = demoMode || isPro unlocks all features visually
- Pages wired up: Dashboard, Simulation, AI Agents, Event Agents, Strategy Lab, Marketplace, Research, Leaderboard, Copy Trading, Referrals
- Disabled real actions: trade execution shows toast in demo mode
- Upgrade banners hidden when demo mode is active

### Admin Route (DONE — 2026-03-28)
- POST /api/auth/admin/create — temporary admin user creation endpoint

## File Structure
```
/app/backend/
├── server.py                       # Lightweight router orchestrator
├── database/__init__.py            # DB connection, keys
├── models/schemas.py               # All Pydantic models
├── routes/                         # 20+ modular route files
├── services/                       # Business logic services
├── web3/contract_abi.py
├── data/ (btc_usd.csv, eth_usd.csv)

/app/frontend/src/
├── App.js                          # Routing shell + DemoModeProvider
├── components/
│   ├── DemoModeBanner.jsx          # Global demo mode banner (NEW)
│   ├── PlaceholderUI.jsx
│   ├── Navigation.jsx              # Demo toggle in nav (UPDATED)
│   └── ui/                         # Shadcn components
├── contexts/
│   ├── AuthContext.jsx
│   ├── DemoModeContext.jsx          # Global demo mode state (NEW)
│   └── WalletContext.jsx
├── lib/
│   ├── constants.js
│   ├── formatters.js
│   └── mockData.js
├── pages/                          # All dashboard pages (demo-mode aware)
```

## Credentials
- Admin: `admin@my-alpha-ai.com` / `Admin1234!`
- Test user: `demo_test2@my-alpha-ai.com` / `NewPass1234!`

## Backlog (P2)
- Wire up real backend data to replace mock placeholders across dashboard
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol to Sepolia mainnet
