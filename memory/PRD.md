# My-AlphaAI — Product Requirements Document

## Original Problem Statement
My-AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion with AI-powered research, backtesting, strategy management, real-time signals, and admin monitoring.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + Motor (Async MongoDB) + WebSockets
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, CoinGecko, Resend

## Implemented Features (All Passing — Iterations 25-69)

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
- Responsive Navigation (priority split + More dropdown)

### Phase 4: Mobile API Optimization (March 29, 2026)
- Bootstrap Endpoint, Mobile Refresh, Mobile API Client, Mobile Cache
- WebSocket Reconnection, MobileNetworkBanner, MobileBottomNav
- MobileSettingsPage, Compact Mode, Safe Area Support

### Phase 5: Smart Prefetching & Performance Polish (March 29, 2026)
- Smart Prefetch Engine, TTL Cache, Skeleton Loaders, Virtualized Alert Lists
- Compact Mode, Pull-to-Refresh, Offline Behavior, usePrefetch Hook

### Phase 6.1: WebSocket Reconnect Loop Fix (March 29, 2026)
- Three-state connected: null → true → false. Rapid-close detection, cooldown guards.

### Phase 6.2: Stripe Webhook Handler
- 9 event types, subscription state machine, idempotency, admin stream, founder alerts

### Phase 7: AlphaAI Manager Contract Pipeline (March 29, 2026)
- Hardhat project, deploy/verify scripts, contract manager service
- **Status**: Pipeline ready but Web3 code removed for SaaS-only deployment

### Phase 8: Hero Section Redesign + Beta Spots + Waitlist (Feb-Mar 2026)
- High-conversion hero, dynamic beta spots counter, waitlist modal, subscription health dashboard

### Phase 9-10: Live User Stats, Exchange Integration (Mar 2026)
- Admin user stats card, Binance Testnet connectivity (data only, no trading)

### Execution Engine Phase 2 (Apr 2026)
- Paper/Testnet modes, signal routing, execution configs, admin monitor

### Admin Demo Mode Toggle & Analytics (Apr 2026)
- DB-backed toggle, analytics events, synthetic/real data modes

### Go-Live Readiness (Apr 4, 2026)
- P0 fixes (404 page, favicon, dashboard un-gating, live prices, hero copy)
- P1 polish (ToS, Privacy, ErrorBoundary, OG tags, manifest, robots.txt, cookies)
- Landing page improvements (screenshots, trust strip, legal disclaimers)
- Strategy interactions (3 featured strategies, leaderboard, copy strategy)
- Waitlist automation (3-email Resend drip)
- Phase 2 features (20% referral commissions, PDF invoices, WebSocket events feed)

### Deployment Fix — P0 Blockers (Apr 5, 2026)
- **Bounded DB queries**: Fixed `strategies.py` weekly report to use date filters (`$gte` on timestamp) with 2000-doc limit instead of unbounded `to_list(5000)`. Added warning logs for truncated results.
- **Web3/blockchain removal**: Deleted `/app/backend/contracts/` (AlphaAIManager.sol), `/app/backend/web3/` (contract_abi.py), `/app/backend/routes/web3_routes.py`. Rewrote `contract_manager.py` as pure mock stub with zero web3 imports.
- **Dead code cleanup**: Deleted 8 unused `generate_*.py` scripts (kept 5 that are referenced by marketing.py/payments.py).
- **Deployment agent**: Passes all checks — no blockchain deps, no hardcoded secrets, no unbounded queries.
- **Testing**: 18/18 tests passed (iteration 69). All core endpoints verified. Frontend serves React app correctly.

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/mobile/bootstrap` | GET | Mobile initialization (demo + auth) |
| `/api/mobile/refresh` | POST | Lightweight token refresh |
| `/api/admin/events` | POST | Log traffic event |
| `/api/admin/traffic/summary` | GET | Aggregated metrics |
| `/api/ws/alerts/{client_id}` | WS | Strategy alerts |
| `/api/marketplace/strategies` | GET | Public strategy listing (paginated) |
| `/api/marketplace/strategies/leaderboard` | GET | Leaderboard with performance (cached 60s) |
| `/api/waitlist` | POST | Waitlist signup + email drip |
| `/api/invoices/download/{id}` | GET | PDF invoice download |
| `/api/billing/overview` | GET | Billing summary |

## Backlog
- **P2**: Actual Sepolia Smart Contract deployment (awaiting user keys — restore web3 when needed)
- **P3**: User retention analytics (DAU/MAU ratio)
- **P3**: Background task queue migration (asyncio.sleep → Celery/Redis for waitlist drip reliability)
