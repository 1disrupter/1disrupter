# My-AlphaAI — Product Requirements Document

## Original Problem Statement
My-AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion with AI-powered research, backtesting, strategy management, real-time signals, and admin monitoring.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + Motor (Async MongoDB) + WebSockets
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, CoinGecko, Resend

## Implemented Features (All Passing — Iterations 25-70)

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
- **Root Cause**: React build directory (`/app/frontend/build/`) was never generated — NGINX served its default page
- **Fix**: Ran `craco build`, verified output (index.html, JS/CSS bundles), confirmed `dist -> build` symlink
- **Additional fixes**: Bounded remaining unbounded queries in `leaderboard_service.py` (trades query: 10000 → 2000 with projection) and `leaderboard.py` (users query: 10000 → 5000 with projection)
- **Deployment agent**: `status: pass` — zero findings, zero blockers

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/digest/unsubscribe` | GET | Unsubscribe from weekly digest |
| `/api/digest/admin/analytics` | GET | Digest delivery analytics |
| `/api/digest/admin/trigger` | POST | Manual digest trigger (admin) |
| `/api/marketplace/strategies` | GET | Public strategy listing (paginated) |
| `/api/marketplace/strategies/leaderboard` | GET | Leaderboard (cached 60s) |
| `/api/waitlist` | POST | Waitlist signup + email drip |
| `/api/invoices/download/{id}` | GET | PDF invoice download |

## Backlog
- **P2**: Strategy Signal Email/Push Alerts
- **P2**: User Portfolio Performance Dashboard
- **P3**: Public Strategy Social Cards (dynamic OG images)
- **P3**: Strategy Comparison Tool
- **P3**: Sepolia Smart Contract deployment (awaiting user keys)
- **P3**: Retention analytics, Task queue migration
