# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion. Features include AI-powered trading signals, demo mode, admin analytics, referral system, multi-tier subscription with Stripe, strategy leaderboard, follow strategy with notifications, and pro-tier feature gating.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Framer Motion + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe (checkout/webhook/billing portal), Resend, CoinGecko (OHLC)
- **Structure**: Modular backend (routes/, services/, models/), React SPA with contexts/hooks

## What's Been Implemented

### Core Platform
- Landing page, User auth (JWT), Wallet integration (MetaMask/Sepolia)
- Multi-tier subscription (Free/Pro/Elite) with Stripe checkout/webhook/billing portal
- Live price ticker, AI trading signals (GPT-5.2)
- Dashboard with trade execution, SL/TP orders, portfolio tracking

### Demo Mode System
- Global DemoModeContext with `?demo=true`, DemoModeBanner, Share Demo, useApiData hook

### Dashboard Pages — All Functional
1. **Research Engine** — GPT-5.2 AI market analysis
2. **Strategy Lab** — Generate + backtest with real CoinGecko OHLC, auto-push to leaderboard
3. **AI Agents** — Configure modal, View Signals modal
4. **Event Agents** — Pause/Resume, View Log, macro events
5. **Marketplace** — Preview modal, performance chart, Install
6. **Simulation** — Backtest with real CoinGecko OHLC, auto-push to leaderboard

### Strategy Leaderboard
- Top-3 podium, sortable rankings table (Sharpe/Return/MaxDD/WinRate)
- Strategy detail modal with equity curve
- **Follow/Unfollow buttons** on every row and detail modal

### Follow Strategy System (Feb 2026)
- POST /api/strategies/{id}/follow + /unfollow + GET /api/strategies/following
- Free tier: 1 follow max, Pro: unlimited
- Automatic notification on follow
- Following page (/following) with strategy cards, metrics, Unfollow buttons
- Demo mode: static mock following data

### In-App Notifications (Feb 2026)
- NotificationBell component in nav with unread count badge
- Dropdown showing recent notifications with mark-read support
- GET /api/notifications/inbox + POST /{id}/read + POST /read-all
- notify_followers() function for strategy signal broadcasts
- Demo mode: static mock notifications

### Pro-Tier Feature Gating (Feb 2026)
- Backend is_pro() helper checks user_tier
- UpgradeModal component → Stripe checkout
- 403 response with upgrade message for gated features
- GET /api/user/pro-status returns tier info and follow limits
- Demo mode bypasses all gating

### CoinGecko Integration
- services/market_data.py: OHLC fetcher with 10-min TTL cache
- services/backtest_engine.py: Momentum/mean_reversion/breakout strategies
- Computes: Sharpe, max drawdown, win rate, return, profit factor, equity curve

### Admin
- Admin panel, Admin Analytics dashboard, Goal Tracker widget

## Key API Endpoints
- `POST /api/strategies/{id}/follow` + `/unfollow` — Follow system
- `GET /api/strategies/following` — List followed strategies
- `GET /api/notifications/inbox` — Notification inbox with unread count
- `POST /api/notifications/{id}/read` + `/read-all` — Mark notifications
- `GET /api/user/pro-status` — Pro tier check
- `GET /api/leaderboard/strategies` — Ranked strategy list
- `POST /api/simulation/backtest` — Real OHLC backtest
- `POST /api/lab/strategies/{id}/backtest` — Strategy backtest
- `POST /api/research/ai-query` — GPT-5.2 market analysis
- `POST /api/payments/checkout` — Stripe checkout session

## MongoDB Collections
- users, strategies, strategy_leaderboard, followed_strategies, notifications_inbox, analytics_events, analytics_goals

## Prioritized Backlog

### P2 — Future Tasks
- Phase 3: Biometric Authentication for Mobile
- Phase 4: Mobile App API Optimization
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol to Sepolia mainnet

## Credentials
- Standard user (Pro): demo_test2@my-alpha-ai.com / NewPass1234!
- Free tier user: test_free_user_iter29@my-alpha-ai.com / TestPass123!
- Admin user: admin@my-alpha-ai.com / Admin1234! (admin_key: alphaai_admin_2026)
