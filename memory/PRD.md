# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion. Features include AI-powered trading signals, demo mode for unauthenticated users, admin analytics, referral system, multi-tier subscription management, and a strategy leaderboard.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Framer Motion + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, Resend, CoinGecko (OHLC market data)
- **Structure**: Modular backend (routes/, services/, models/), React SPA with contexts/hooks

## What's Been Implemented

### Core Platform
- Landing page with animated brand reveal
- User auth (JWT-based login/register/forgot-password/verify-email)
- Wallet integration (MetaMask/Sepolia)
- Multi-tier subscription (Free/Pro/Elite) with Stripe checkout
- Live price ticker, AI trading signals (GPT-5.2 powered)
- Dashboard with trade execution, SL/TP orders, portfolio tracking

### Demo Mode System
- Global DemoModeContext with `?demo=true` URL activation
- DemoModeBanner, Share Demo, useApiData hook
- All pages work with mock data in demo mode

### Dashboard Pages — All Functional
1. **Research Engine** — GPT-5.2 AI market analysis
2. **Strategy Lab** — Generate strategies, backtest with real CoinGecko OHLC, auto-push to leaderboard
3. **AI Agents** — Configure modal, View Signals modal
4. **Event Agents** — Pause/Resume, View Log, macro events
5. **Marketplace** — Preview modal with performance chart, Install
6. **Simulation** — Backtest with real CoinGecko OHLC, auto-push to leaderboard

### Strategy Leaderboard (Feb 2026)
- **Page**: `/leaderboard` with top-3 podium and sortable rankings table
- **Sorting**: Sharpe ratio (default), Total Return, Max Drawdown, Win Rate
- **Detail Modal**: Equity curve chart, metrics grid, parameters, data source badge
- **Integration**: Auto-populated by Strategy Lab and Simulation backtests
- **Backend**: GET/POST /api/leaderboard/strategies, strategy_leaderboard MongoDB collection
- **Demo Mode**: 8 static mock strategies with "Demo Mode — Mock Data" badge

### CoinGecko Integration
- `services/market_data.py`: OHLC fetcher with 10-min TTL cache
- `services/backtest_engine.py`: Momentum, mean reversion, breakout strategies
- Computes: Sharpe, max drawdown, win rate, return, profit factor, equity curve

### Admin
- Admin panel, Admin Analytics dashboard, Goal Tracker widget

## Key API Endpoints
- `GET /api/leaderboard/strategies` — Ranked strategy list (sortable, paginated, demo flag)
- `POST /api/leaderboard/strategies` — Add/update leaderboard entry
- `GET /api/leaderboard/strategies/{id}` — Strategy detail with equity curve
- `POST /api/simulation/backtest` — Real OHLC backtest
- `POST /api/lab/strategies/{id}/backtest` — Strategy backtest with real data
- `POST /api/research/ai-query` — GPT-5.2 market analysis

## Prioritized Backlog

### P2 — Future Tasks
- Phase 3: Biometric Authentication for Mobile
- Phase 4: Mobile App API Optimization
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol to Sepolia mainnet

## Credentials
- Standard user: demo_test2@my-alpha-ai.com / NewPass1234!
- Admin user: admin@my-alpha-ai.com / Admin1234! (admin_key: alphaai_admin_2026)
