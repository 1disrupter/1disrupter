# My-AlphaAI — Product Requirements Document

## Original Problem Statement
My-AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion with AI-powered research, backtesting, strategy management, real-time signals, and admin monitoring.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + Motor (Async MongoDB) + WebSockets
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, CoinGecko, Resend

## Implemented Features (All Passing — Iterations 25-71)

### Phase 1-6: Core Platform through WebSocket Fix
- Auth (JWT, 2FA, password reset), Dashboard, Strategy Lab, Marketplace, Copy Trading
- Referral, Admin panel, Demo Mode, GPT-5.2 Research, CoinGecko OHLC, Backtest Engine
- Leaderboard, Stripe Pro-Tier Gating, Real-Time WS Alerts, Admin Analytics
- Mobile Optimization, Smart Prefetch, Skeleton Loaders, WS Reconnect Fix

### Phase 7-10: Contract Pipeline, Hero, Waitlist, Exchange Integration
- Hardhat pipeline (Web3 removed for SaaS deployment), High-conversion hero
- Waitlist modal + 3-email Resend drip, Binance Testnet (data only)

### Go-Live + Deployment Fix (Apr 4-5, 2026)
- P0/P1 fixes, Landing page polish, Strategy interactions, PDF invoices, WebSocket events feed
- Bounded DB queries, Web3 removal, Dead code cleanup, Deployment agent: PASS

### Weekly Performance Digest Email (Apr 5, 2026)
- Cron scheduler (Monday 09:00 UTC), branded HTML template, free vs pro gating
- Unsubscribe/resubscribe, delivery logging, admin analytics, manual trigger
- Testing: 19/19 passed (iteration 70), 167 real emails delivered

### Frontend Deployment Fix (Apr 5, 2026)
- Root cause: build/ gitignored, NGINX had nothing to serve
- Fix: Removed build/dist from .gitignore, rebuilt frontend
- Deployment agent: PASS with zero blockers

### Full Live Mode System (Apr 5, 2026)
- **`GET /api/demo-mode/status`**: Public endpoint, frontend syncs on mount + every 30s
- **`GET /api/signals/live`**: Returns real signals from DB when DEMO_MODE=false, synthetic demo when true. Supports user_id param for followed-strategy filtering.
- **`GET /api/portfolio/me`**: Real user portfolio (PnL, win rate, Sharpe, drawdown, trades) when live. Demo portfolio (PnL: $1,247.83) when demo mode ON.
- **WebSocket `/api/ws/events`**: Rewritten to be demo-mode aware. Live mode fetches real signals/trades from DB. Demo mode generates synthetic events. Shows LIVE/DEMO badge.
- **Frontend DemoModeContext**: Syncs with backend `/api/demo-mode/status` on mount. URL param `?demo=true` always forces demo mode. SessionStorage fallback.
- **DashboardPage**: Removed all hardcoded initial signal/performance arrays. Fetches from `/api/signals/live` and `/api/portfolio/me`. Null-safe rendering with loading states.
- **LiveEventsFeed**: Shows real-time LIVE/DEMO badge based on WebSocket connected message.
- **Admin Toggle**: `POST /api/admin/demo-mode?admin_key=...` with `{enabled: true/false}` body. Instant switch, DB-backed with 5s cache TTL.
- Testing: 21/21 backend + all frontend UI checks passed (iteration 71). Zero issues.

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/demo-mode/status` | GET | Public demo mode flag |
| `/api/signals/live` | GET | Live signals (demo-mode aware) |
| `/api/portfolio/me` | GET | User portfolio (demo-mode aware) |
| `/api/admin/demo-mode` | POST | Toggle demo mode (admin) |
| `/api/digest/unsubscribe` | GET | Unsubscribe from weekly digest |
| `/api/digest/admin/analytics` | GET | Digest delivery analytics |
| `/api/digest/admin/trigger` | POST | Manual digest trigger (admin) |
| `/api/marketplace/strategies` | GET | Public strategy listing (paginated) |
| `/api/ws/events` | WS | Live events feed |

## Backlog
- **P2**: Strategy Signal Email/Push Alerts
- **P2**: User Portfolio Performance Dashboard (full page with charts)
- **P3**: Public Strategy Social Cards (dynamic OG images)
- **P3**: Strategy Comparison Tool
- **P3**: Sepolia Smart Contract deployment (awaiting user keys)
- **P3**: Retention analytics, Task queue migration
