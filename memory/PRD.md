# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion. Features include AI-powered trading signals, demo mode for unauthenticated users, admin analytics, referral system, and multi-tier subscription management.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Framer Motion + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, Resend, CoinGecko (OHLC market data)
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

### Dashboard Pages — All Functional
1. **Research Engine** — GPT-5.2 AI-powered market analysis with asset selector, trend/confidence/risk/indicators
2. **Strategy Lab** — Generate strategies, backtest with REAL CoinGecko OHLC data, equity curve, data source badge
3. **AI Agents** — Configure modal (asset, timeframe, risk, frequency), View Signals modal
4. **Event Agents** — Pause/Resume toggle, View Log, macro events modal
5. **Marketplace** — Preview modal with description, returns chart, metrics, Install
6. **Simulation** — Backtest with REAL CoinGecko OHLC data, equity curve, data source badge

### CoinGecko Integration (Feb 2026)
- `services/market_data.py`: OHLC fetcher with 10-min TTL cache, asset mapping (BTC→bitcoin, ETH→ethereum, SOL→solana)
- `services/backtest_engine.py`: Real strategy backtesting (momentum SMA crossover, mean reversion z-score, breakout N-period)
- Computes: Sharpe ratio, max drawdown, win rate, total return, profit factor, equity curve
- Demo Mode: deterministic mock OHLC fallback, no external API calls
- Frontend badges: "Data: CoinGecko" (real) or "Demo Mode — Mock Data" (demo)

### Admin
- Admin panel with user management, signal generation, system config
- Admin Analytics dashboard with conversion funnels, referrer tracking
- Goal Tracker widget with K-factor and conversion targets

## Key API Endpoints
- `POST /api/simulation/backtest` — Real OHLC backtest (asset, strategy, days, initial_capital, demo)
- `POST /api/lab/strategies/{id}/backtest` — Strategy backtest with real CoinGecko data
- `POST /api/research/ai-query` — GPT-5.2 market analysis
- `GET/POST /api/admin/analytics` — Admin analytics

## Prioritized Backlog

### P2 — Future Tasks
- Phase 3: Biometric Authentication for Mobile (Face ID / Touch ID)
- Phase 4: Mobile App API Optimization (React Native improvements)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia mainnet

## Credentials
- Standard user: demo_test2@my-alpha-ai.com / NewPass1234!
- Admin user: admin@my-alpha-ai.com / Admin1234! (admin_key: alphaai_admin_2026)
