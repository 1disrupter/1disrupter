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
- Pages updated: Simulation, Research, AI Agents, Event Agents, Strategy Lab, Marketplace, Referrals, Analytics, Conversion Analytics, Leaderboard (mock fallback)
- Shared components: PlaceholderUI.jsx (PageHeader, StatsRow, ComingSoonCard, MockTable, MiniChart)
- Shared mock data: lib/mockData.js

### Admin Route (DONE — 2026-03-28)
- POST /api/auth/admin/create — temporary admin user creation endpoint

### Phase 8 — Backend Monolith Refactor (DONE — 2026-03-29)
- Refactored monolithic server.py (6,200+ lines) into clean modular architecture
- server.py reduced to lightweight router orchestrator (~156 lines)
- 20+ route modules in /app/backend/routes/
- Centralized Pydantic models in /app/backend/models/schemas.py
- Service layer in /app/backend/services/
- Database connection in /app/backend/database/__init__.py
- Fixed all import errors, missing dependencies, and path issues across extracted modules
- All 15+ API endpoint groups verified working (100% pass rate)
- Frontend fully functional with all dashboard pages accessible

## File Structure
```
/app/backend/
├── server.py                       # Lightweight router orchestrator (~156 lines)
├── database/
│   └── __init__.py                 # DB connection, EMERGENT_LLM_KEY, STRIPE_API_KEY
├── models/
│   └── schemas.py                  # All Pydantic models (~507 lines)
├── routes/
│   ├── admin.py                    # Admin dashboard
│   ├── analytics_routes.py         # Analytics tracking
│   ├── auth.py                     # Authentication (JWT, login, register)
│   ├── copy_trading.py             # Copy trading system
│   ├── demo.py                     # Demo/overview endpoints
│   ├── event_agents.py             # Event-driven agent system
│   ├── fund.py                     # Fund stats, investors, market data
│   ├── leaderboard.py              # Leaderboard rankings
│   ├── marketing.py                # Marketing assets, PDF generation
│   ├── metrics.py                  # Platform metrics
│   ├── mobile_v1.py                # Mobile API endpoints
│   ├── notifications.py            # Notification preferences
│   ├── orders.py                   # Order management
│   ├── payments.py                 # Stripe payments
│   ├── referrals.py                # Referral system
│   ├── research.py                 # AI research engine, backtesting
│   ├── signals.py                  # Tiered signal API (free/pro/elite)
│   ├── simulation.py               # Simulation engine
│   ├── strategies.py               # Strategy lab, agent management
│   ├── trading.py                  # Live/paper trading, risk management
│   ├── web3_routes.py              # Smart contract integration
│   └── websocket.py                # WebSocket connections
├── services/
│   ├── copy_trading_service.py
│   ├── email_service.py
│   ├── leaderboard_service.py
│   ├── market_data.py
│   ├── order_manager.py
│   ├── push_notifications.py
│   ├── signal_intelligence.py
│   ├── signal_service.py
│   ├── simulation_service.py
│   ├── trading_service.py
│   └── websocket_manager.py
├── web3/
│   └── contract_abi.py
├── data/
│   ├── btc_usd.csv
│   └── eth_usd.csv

/app/frontend/src/
├── App.js                          # Routing shell (79 lines)
├── components/
│   ├── BrandComponents.jsx
│   ├── LivePriceTicker.jsx
│   ├── Navigation.jsx
│   ├── NotificationSettings.jsx
│   ├── PlaceholderUI.jsx
│   ├── SplashScreen.jsx
│   ├── PerformanceMetrics.jsx
│   ├── ReferralDashboard.jsx
│   └── ui/                         # Shadcn components
├── contexts/
│   ├── AuthContext.jsx
│   └── WalletContext.jsx
├── lib/
│   ├── constants.js
│   ├── formatters.js
│   └── mockData.js
├── pages/
│   ├── AdminPage.jsx
│   ├── AgentsPage.jsx
│   ├── AnalyticsPage.jsx
│   ├── AuthPages.jsx
│   ├── ConversionAnalyticsPage.jsx
│   ├── CopyTradingPage.jsx
│   ├── DashboardPage.jsx
│   ├── EventAgentsPage.jsx
│   ├── LandingPage.jsx
│   ├── LeaderboardPage.jsx
│   ├── MarketplacePage.jsx
│   ├── PricingPage.jsx
│   ├── ReferralPage.jsx
│   ├── ResearchEnginePage.jsx
│   ├── SimulationPage.jsx
│   └── StrategyLabPage.jsx
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
