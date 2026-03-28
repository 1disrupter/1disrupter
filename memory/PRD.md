# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion by emphasizing the "pain of being late" to market moves. Features include Free Tier (15-min signal delay), Pro/Elite paid tiers, Copy Trading, AI Signal Engine, and a high-conversion landing page.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Framer Motion + Shadcn UI
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **3rd Party**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe (payments), Resend (emails)

## What's Been Implemented

### Phase 1 — Core Platform (DONE)
- JWT auth with email verification (Resend)
- Stripe subscriptions: Free / Pro ($29/mo) / Elite ($79/mo)
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
- 20 files extracted to pages/, components/, lib/, contexts/
- All pages compile and render correctly

### Conversion Optimizations (DONE — 2026-03-28)
- Hero CTA → "Start Free Demo"
- Trust proof: "68% Win Rate — updated daily"
- CTA trust line: "No credit card required. Free tier included. Cancel anytime."
- Today's Entries: "Entries You Already Missed Today" + red LIVE urgency tag
- Pricing urgency banner: "Every 15 minutes without Pro, you miss another entry."
- Pricing heading: "Choose Your Edge"

## File Structure
```
/app/frontend/src/
├── App.js                          # Routing shell (79 lines)
├── components/
│   ├── BrandComponents.jsx         # BrandLockup, PoweredByTag
│   ├── LivePriceTicker.jsx         # Live crypto price feed
│   ├── Navigation.jsx              # Main nav bar
│   ├── NotificationSettings.jsx    # Push notification prefs
│   ├── SplashScreen.jsx            # Cinematic splash
│   ├── PerformanceMetrics.jsx
│   ├── ReferralDashboard.jsx
│   └── ui/                         # Shadcn components
├── contexts/
│   ├── AuthContext.jsx
│   └── WalletContext.jsx           # Canonical wallet provider
├── lib/
│   ├── constants.js                # API, BACKEND_URL
│   └── formatters.js               # formatCurrency, formatAddress
├── pages/
│   ├── AdminPage.jsx               # Admin dashboard + SmartContractPanel
│   ├── AgentsPage.jsx              # AI Agents
│   ├── AnalyticsPage.jsx           # Analytics
│   ├── AuthPages.jsx               # Login/Register/Forgot/Reset/Verify
│   ├── ConversionAnalyticsPage.jsx
│   ├── CopyTradingPage.jsx         # Copy trading
│   ├── DashboardPage.jsx           # Main dashboard
│   ├── EventAgentsPage.jsx         # Event agents
│   ├── LandingPage.jsx             # Landing page + HeroVisualization
│   ├── LeaderboardPage.jsx
│   ├── MarketplacePage.jsx
│   ├── PricingPage.jsx             # Tier system + pricing
│   ├── ReferralPage.jsx
│   ├── ResearchEnginePage.jsx
│   ├── SimulationPage.jsx
│   └── StrategyLabPage.jsx
```

## Key DB Schema
- `users`: id, email, name, user_tier (free/pro/elite), is_pro, is_elite, wallet_address
- `copy_relationships`: copier_id, trader_id, mode, allocation_percent, max_per_trade, status, stats

## Credentials
- Test user: `demo_test2@my-alpha-ai.com` / `NewPass1234!`

## Backlog (P2)
- Phase 5: Biometric Auth for Mobile (Face ID / Touch ID)
- Phase 6: Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol to Sepolia mainnet
- Backend server.py refactor (6,232 lines → multiple route files)
