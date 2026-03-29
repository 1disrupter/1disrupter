# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion. Features include AI-powered trading signals, demo mode for unauthenticated users, admin analytics, referral system, and multi-tier subscription management.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Framer Motion + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, Resend
- **Structure**: Modular backend (routes/, services/, models/), React SPA with contexts/hooks

## What's Been Implemented

### Core Platform
- Landing page with animated brand reveal (splash screen)
- User auth (JWT-based login/register/forgot-password/verify-email)
- Wallet integration (MetaMask/Sepolia)
- Multi-tier subscription (Free/Pro/Elite) with Stripe checkout
- Live price ticker, AI trading signals (GPT-5.2 powered)
- Dashboard with trade execution, SL/TP orders, portfolio tracking

### Demo Mode System
- Global DemoModeContext with `?demo=true` URL activation
- DemoModeBanner showing simulated data notice
- Share Demo button generating shareable URLs
- useApiData hook for conditional real/mock data loading
- All dashboard pages wired to mock data in demo mode

### Dashboard Pages — All Functional (6 pages enhanced Feb 2026)
1. **Research Engine** — GPT-5.2 AI-powered market analysis with asset selector (BTC/ETH/SOL), trend/confidence/risk/indicators display. Backend endpoint: POST /api/research/ai-query
2. **Strategy Lab** — Generate strategies (momentum/mean_reversion/arbitrage/yield/funding), backtest with metrics (Sharpe, return, drawdown, win rate), strategy rankings table
3. **AI Agents** — Configure modal (asset, timeframe, risk level, signal frequency), View Signals modal (LONG/SHORT signals with confidence), saved configs shown as badges
4. **Event Agents** — Pause/Resume toggle, View Log modal with timestamped entries, macro events modal (6 upcoming events with impact levels and expected volatility)
5. **Marketplace** — Preview modal with description, monthly returns chart, metrics (Sharpe, Max DD, Win Rate), Install functionality with search filtering
6. **Simulation** — Backtest tab with pair/strategy selectors, equity curve visualization, PnL metrics (Total Return, Sharpe, Max Drawdown, Win Rate, Profit Factor)

### Admin
- Admin panel with user management, signal generation, system config
- Admin Analytics dashboard with conversion funnels, referrer tracking
- Goal Tracker widget with K-factor and conversion targets

### Bug Fixes
- Fixed global UI interaction blocker: removed `disabled` prop from all action buttons across 6 pages (Feb 2026)

## Prioritized Backlog

### P2 — Future Tasks
- Phase 3: Biometric Authentication for Mobile (Face ID / Touch ID)
- Phase 4: Mobile App API Optimization (React Native improvements)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia mainnet

## Credentials
- Standard user: demo_test2@my-alpha-ai.com / NewPass1234!
- Admin user: admin@my-alpha-ai.com / Admin1234! (admin_key: alphaai_admin_2026)
