# My-AlphaAI — Product Requirements Document

## Original Problem Statement
My-AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion with AI-powered research, backtesting, strategy management, real-time signals, and admin monitoring.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + Motor (Async MongoDB) + WebSockets
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, CoinGecko, Resend

## Implemented Features (All Passing — Iterations 25-70)

### Phase 1: Core Platform
- Auth (JWT, 2FA, password reset, email verification), Dashboard, Agents, Strategy Lab
- Marketplace, Copy Trading, Referral, Admin panel, Demo Mode

### Phase 2: Intelligence & Data
- GPT-5.2 Research, CoinGecko OHLC, Backtest Engine, Strategy Leaderboard
- Follow Strategy + Notifications, Stripe Pro-Tier Gating, Real-Time Strategy Alerts (WS)

### Phase 3: Admin Analytics + Monitoring
- Event Logging, Summary/Timeseries/Raw Events, Frontend Tracking
- Admin Dashboard, WebSocket admin event stream, Live Event Stream panel
- Rule Engine (6 anomaly rules), Alert events, Founder email alerts

### Phase 4-6: Mobile Optimization + Performance + WebSocket Fix
- Bootstrap/Refresh endpoints, Prefetch engine, Skeleton loaders, Pull-to-refresh
- WS three-state reconnect, Stripe webhook handler (9 event types)

### Phase 7: Contract Pipeline (Ready, Web3 removed for SaaS deployment)

### Phase 8-10: Hero Redesign, Beta Spots, Waitlist, Exchange Integration
- High-conversion hero, dynamic beta counter, waitlist modal, subscription health
- Binance Testnet connectivity (data only)

### Execution Engine Phase 2 + Admin Demo Toggle (Apr 2026)
- Paper/Testnet modes, signal routing, DB-backed demo toggle, analytics events

### Go-Live Readiness (Apr 4, 2026)
- P0 fixes, P1 polish (ToS, Privacy, ErrorBoundary, OG tags, manifest, cookies)
- Landing page improvements, strategy interactions, waitlist automation, Phase 2 features

### Deployment Fix — P0 Blockers (Apr 5, 2026)
- Bounded DB queries, web3/blockchain removal, dead code cleanup
- Testing: 18/18 passed (iteration 69)

### Weekly Performance Digest Email (Apr 5, 2026)
- **Cron Scheduler**: Background loop checks every 60s, fires Mondays at 09:00 UTC. Uses `_last_digest_week` guard to prevent duplicate sends.
- **Data Collection**: Top 5 strategies by 7-day return from `strategies_mp` + `strategy_performance`. Per-user followed-strategy performance from `followed_strategies` + `strategy_leaderboard`.
- **Free vs Pro Gating**: Free users see top 3 global strategies + blurred rows + "Upgrade to Pro" CTA. Pro users see full global + personalized metrics (Sharpe, win rate, signals).
- **Email Template**: Dark-themed HTML matching AlphaAI brand. Sections: header, global top strategies table, personalized followed strategies (or discovery CTA), upgrade banner (free), dashboard/leaderboard CTAs, footer with unsubscribe.
- **Unsubscribe**: `GET /api/digest/unsubscribe?email=...` + `GET /api/digest/resubscribe?email=...`. Uses `digest_preferences` collection.
- **Delivery Logging**: `weekly_digest_logs` collection — user_id, email, is_pro, strategy_count, status, week_label, sent_at.
- **Admin Analytics**: `GET /api/digest/admin/analytics?admin_key=...` — total sent, last 7d stats, pro vs free distribution, unsubscribed count, latest batch info, open_rate placeholder.
- **Manual Trigger**: `POST /api/digest/admin/trigger?admin_key=...` — admin-only immediate send for testing.
- **Rate Limiting**: 0.2s delay between sends to avoid Resend rate limits.
- **Testing**: 19/19 passed (iteration 70). 167 real emails delivered, 100% delivery rate. Zero regressions.

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/digest/unsubscribe` | GET | Unsubscribe from weekly digest |
| `/api/digest/resubscribe` | GET | Re-subscribe to weekly digest |
| `/api/digest/admin/analytics` | GET | Digest delivery analytics |
| `/api/digest/admin/trigger` | POST | Manual digest trigger (admin) |
| `/api/marketplace/strategies` | GET | Public strategy listing (paginated) |
| `/api/marketplace/strategies/leaderboard` | GET | Leaderboard (cached 60s) |
| `/api/waitlist` | POST | Waitlist signup + email drip |
| `/api/invoices/download/{id}` | GET | PDF invoice download |
| `/api/billing/overview` | GET | Billing summary |

## Backlog
- **P2**: Actual Sepolia Smart Contract deployment (awaiting user keys)
- **P2**: Strategy Signal Email/Push Alerts (email when followed strategy fires signal)
- **P2**: User Portfolio Performance Dashboard (aggregated P&L across followed strategies)
- **P3**: Public Strategy Social Cards (dynamic OG images for sharing)
- **P3**: Strategy Comparison Tool (side-by-side metrics)
- **P3**: User retention analytics (DAU/MAU ratio)
- **P3**: Background task queue migration (asyncio.sleep → Celery/Redis)
