# My-AlphaAI — Product Requirements Document

## Original Problem Statement
My-AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion with AI-powered research, backtesting, strategy management, real-time signals, and admin monitoring.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + Motor (Async MongoDB) + WebSockets
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, CoinGecko, Resend

## Implemented Features (All Passing — Iterations 25-35)

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
- **Bootstrap Endpoint** (`GET /api/mobile/bootstrap`) — Lightweight single-call init returning user profile, followed strategies, unread alerts, feature flags, strategy summary. Works in demo mode. <120ms total.
- **Mobile Refresh** (`POST /api/mobile/refresh`) — Lightweight token refresh for mobile sessions.
- **Mobile API Client** — `fetchWithRetry` (exponential backoff, 3 retries), `fetchCached` (localStorage + TTL), `queueOfflineEvent` / `flushOfflineQueue` (offline event queue).
- **Mobile Cache** — localStorage wrapper with TTL per key (bootstrap: 2min, strategies: 5min, followed: 3min, alerts: 1min). Invalidated on login/logout.
- **WebSocket Reconnection** — Reconnects on `visibilitychange` (app resume) and `online` event (network recovery). Exponential backoff with 8 max attempts.
- **MobileNetworkBanner** — Offline (red) and Reconnecting (yellow) banners with smooth animations.
- **MobileBottomNav** — Sticky bottom nav (Dashboard, Leaderboard, Alerts, Settings) visible below md breakpoint.
- **MobileSettingsPage** (`/settings`) — Clear cache, refresh data, alert sounds toggle, compact mode toggle, cache status display.
- **Compact Mode** — CSS class that reduces padding/spacing globally.
- **Safe Area Support** — CSS env() for notch/home indicator on iOS.

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/mobile/bootstrap` | GET | Mobile initialization (demo + auth) |
| `/api/mobile/refresh` | POST | Lightweight token refresh |
| `/api/admin/events` | POST | Log traffic event |
| `/api/admin/traffic/summary` | GET | Aggregated metrics |
| `/api/admin/traffic/active-alerts` | GET | Active alert types |
| `/api/ws/admin/events` | WS | Admin event stream |
| `/api/ws/alerts/{client_id}` | WS | Strategy alerts |

### Phase 5: Smart Prefetching & Performance Polish (March 29, 2026)
- **Smart Prefetch Engine** (`smartPrefetch.js`) — Background data fetching with safety guards: runs only when network online, app idle (requestIdleCallback 300ms), cache cold/expired, battery not low. Cancels on navigation via AbortController.
  - Page rules: Leaderboard (top 3 strategies + details), Dashboard (followed strategies), Alerts (bootstrap warm).
  - Hover/touch prefetch on strategy rows and podium cards.
- **TTL Cache Enhancements** — Extended `mobileCache.js` TTL_MAP: strategy_detail: 5min, metadata: 10min, alerts: 30s, chart: 2min.
- **Skeleton Loaders** (`SkeletonLoaders.jsx`) — ChartSkeleton, StatsSkeleton, AlertCardSkeleton, AlertListSkeleton, HeaderSkeleton, LeaderboardRowSkeleton, PodiumSkeleton, StrategyDetailSkeleton. All with `data-testid`.
- **Virtualized Alert Lists** — `react-window` v2.2.7 `List` component activates when alert count > 20 (VIRTUALIZE_THRESHOLD).
- **Compact Mode** — Toggle on Leaderboard (persisted to localStorage). Reduces cell padding in strategy table.
- **Pull-to-Refresh** — Touch-based pull-to-refresh on Leaderboard page (80px threshold).
- **Offline Behavior** — Offline banner on Leaderboard and Alerts. Cached data shown. Follow/Unfollow buttons disabled when offline.
- **usePrefetch Hook** — Integrated in App.js TrackingWrapper. Starts/stops prefetching on route changes.
- **Strategy Detail Modal** — Smooth animated metrics reveal + equity curve bar animation.

### Phase 6.1: WebSocket Reconnect Loop Fix (March 29, 2026)
- **Root Cause**: `useStrategyAlerts` initialized `connected = false`. For unauthenticated/non-demo users, no WS was attempted, so `connected` stayed `false` and `MobileNetworkBanner` showed "Reconnecting..." permanently.
- **Fix**: Three-state connected: `null` (no attempt) → `true` (connected) → `false` (disconnected). Banner only triggers on `wsConnected === false` (strict).
- **Additional Fixes by Testing Agent**: Moved `setConnected(false)` after code-1000 check (prevented Pro user banner flash), added `upgradeRequiredRef` to prevent Free user infinite reconnect loop on code 4003.
- **Safety Guards**: Rapid-close detection (< 500ms), fast-failure pause after 5 failures (30s cooldown), exponential backoff with increased base delay for server-down scenarios.
- **Backend**: Added try/except wrapping around entire WS handler, increased timeout from 60s to 90s.

- **Comprehensive Webhook Handler** (`services/stripe_webhook_handler.py`) — Processes all 9 Stripe event types: checkout.session.completed, customer.subscription.created/updated/deleted, invoice.payment_succeeded/failed, customer.subscription.trial_will_end, charge.refunded, charge.dispute.created.
- **Subscription State Machine** — Full lifecycle: active, trialing, past_due, canceled, flagged. Each transition updates user.subscription_status, user_tier, is_pro, subscription_end.
- **Idempotency** — Duplicate event detection via `stripe_webhook_events` collection with unique event_id index.
- **Admin Stream Integration** — All webhook events broadcast to `/api/ws/admin/events` (stripe_event_received, subscription_activated/updated/canceled, payment_failed, refund_processed, dispute_created).
- **Founder Email Alerts** — Triggered on: signature failure, unhandled events, payment failure, refund, dispute. Suppressed in demo mode.
- **Test Simulation Endpoint** — `POST /api/webhook/stripe/test?admin_key=...` for admin-only event simulation without real Stripe.
- **Subscription Status API** — `GET /api/subscription/status` (auth/demo), `GET /api/subscription/webhook-events?admin_key=...` (admin).
- **Mobile Bootstrap Updated** — Includes subscription_status and subscription_end in user object.
- **Backend Tests** — 16 unit tests + 21 API integration tests, 100% pass rate.

### Phase 7: AlphaAIManager.sol Deployment Pipeline & Contract Integration (March 29, 2026)
- **Hardhat Project** (`/app/contracts/`) — Compiles AlphaAIManager.sol (Solidity 0.8.20, optimizer 200 runs). Pinned to Hardhat v2.28.6. Reads keys from `backend/.env`.
- **Deploy Script** (`scripts/deploy.js`) — Mainnet blocked, validates RPC/balance, saves deployment artifact to `deployments/sepolia/`, auto-updates `backend/.env` and `web3/contract_abi.py`.
- **Verify Script** (`scripts/verify.js`) — Etherscan verification with 3x retry. Updates artifact with verification timestamp.
- **Contract Manager Service** (`services/contract_manager.py`) — Web3 integration layer with TTL cache (30s), graceful mock fallback when RPC unavailable. Helpers: `get_strategy`, `get_strategy_count`, `get_investor_balance`, `get_owner`, `is_strategy_registered`, `get_contract_status`.
- **Admin Contract Status** — `GET /api/admin/contract/status` returns health, deployment info, verification status, ABI function count, RPC connectivity.
- **Admin Traffic Page** — Contract status card with address (clickable Etherscan link), verification badge, health indicator, ABI function count.
- **Mobile Bootstrap** — Includes `contract.address` and `contract.network` in bootstrap response.
- **Web3 Routes Updated** — `/api/contract/info`, `/api/contract/strategies`, `/api/contract/balance/{wallet}` use real contract_manager when available, fall back to DB/mock.
- **Tests**: 19 contract_manager unit tests + 35 total backend tests, 100% pass.
- **Status**: Pipeline ready. Contract NOT deployed yet — awaiting user credentials (DEPLOYER_PRIVATE_KEY, SEPOLIA_RPC_URL, ETHERSCAN_API_KEY).
- **Deployment README** at `/app/contracts/README.md` with full instructions.

### Branding Update: AlphaAI → My-AlphaAI (Mar 2026)
- **Scope**: All user-visible text updated from "AlphaAI" to "My-AlphaAI" across navbar, footer, splash screen, auth pages, landing page, dashboard, admin, pricing, referral, upgrade modal, demo mode, and HTML title tag.
- **Unchanged**: Colors, logo icon, layout, routes, backend logic, code comments, smart contract name.
- **Testing**: 18/18 passed (iteration 49).

## Backlog
- **P1**: Order Execution Engine (Phase 2 of Live Trading)
- **P2**: Actual Sepolia Smart Contract deployment (awaiting user keys)
- **P3**: MRR trend chart for subscription health dashboard (Recharts)
- **P3**: Auto-email waitlist users when spot opens (Resend integration)
- **P3**: User retention analytics (DAU/MAU ratio)

### Strategy Marketplace Backend (Apr 2026)
- **Module**: `/app/backend/routes/marketplace.py` — standalone, does not touch Strategy Lab
- **Collections**: `strategies_mp`, `strategy_performance`, `strategy_signals`, `strategy_subscriptions`, `strategy_reviews`, `creator_payouts`, `automation_webhooks`
- **Endpoints** (all under `/api/marketplace`):
  - `POST /strategies/create` — draft mode
  - `POST /strategies/{id}/publish` / `unpublish` — marketplace visibility
  - `GET /strategies` — public listing with filters (category, creator, sort by popularity/performance/newest/rating)
  - `GET /strategies/{id}` — full detail (metadata + performance + signals + reviews)
  - `POST /strategies/{id}/performance` — upload performance data (creator only)
  - `POST /strategies/{id}/subscribe` / `unsubscribe` — subscription management
  - `GET /me/strategies` — user's active subscriptions (enriched with strategy data)
  - `GET /me/created` — creator's own strategies
  - `POST /strategies/{id}/review` — rating + comment (one per user, no self-review)
- **Marketplace Frontend v2** (Apr 2026):
  - `/strategy-marketplace` — Browse published strategies with category/sort filters, search, pagination. Cards enriched with WR/Sharpe/Return metrics.
  - `/marketplace/:id` — Strategy detail with PerformanceBlock, EquityCurveChart (SVG), SignalsTable, ReviewsList with form, Subscribe/Unsubscribe buttons, Parameters display.
  - `/creator/strategies` — Creator dashboard with summary stats (Total, Published, Subscribers), Published/Draft sections, create form, publish/unpublish actions.
  - `/me/strategies` — User subscriptions page with active subs and Unsubscribe button.
  - Reusable components: `StrategyCard`, `StrategyPerformanceBlock`, `SignalsTable`, `ReviewsList`, `SubscribeButtons`, `EquityCurveChart` in `/app/frontend/src/components/marketplace/`.
### Stripe Billing for Strategy Marketplace (Apr 2026)
- **Module**: `/app/backend/routes/marketplace_billing.py`
- **Endpoints**:
  - `POST /api/marketplace/strategies/{id}/checkout` — creates Stripe Checkout session ($9.99/mo), returns redirect URL
  - `GET /api/marketplace/checkout/status/{session_id}` — polls Stripe for payment status, creates subscription on success
  - `POST /api/webhook/stripe` — handles Stripe webhook events (payment confirmation)
  - `POST /api/marketplace/strategies/{id}/cancel-subscription` — cancels active subscription
- **Frontend**: Subscribe button redirects to Stripe Checkout. On return, polls status and shows success/failure toast. Unsubscribe calls cancel-subscription endpoint.
- **Collections**: `payment_transactions` (checkout session tracking)
- **Testing**: Backend 12/12, Frontend all flows verified (iteration 56)

### Phase 10: Exchange Integration — Testnet Only (Mar 2026)
- **Backend**: 5 new endpoints — `POST /api/exchange/connect` (validates + encrypts + stores keys), `POST /api/exchange/validate` (re-validates, fetches balances/positions), `GET /api/exchange/status` (connection status, masked key only), `DELETE /api/exchange/disconnect`, `GET /api/admin/exchanges` (admin view, no secrets).
- **Security**: Fernet encryption at rest (EXCHANGE_ENCRYPTION_KEY in .env), rate limiting (5/60s/user), secret keys never returned after submission, never logged.
- **Frontend**: `/connect-exchange` page with auth guard, exchange selector (Binance Testnet), API/Secret key inputs, security note, success/error states.
- **Dashboard**: Exchange Account card (balances, positions) if connected, "Connect Exchange" CTA if not.
- **Admin Panel**: "Exchanges" tab with table (user, exchange, status, last validated).
- **No trading**: Connectivity + data only. No orders, no live trading.
- **Testing**: 100% passed (iteration 50). Backend 12/12, frontend all UI verified.

### Free Demo Flow Fix (Mar 2026)
- **`/demo` route**: Sets sessionStorage + redirects to `/dashboard?demo=true`. No auth required.
- **Pricing page**: Free tier button changed from disabled "Current Plan" to enabled "Start Free Demo" linking to `/demo`.
- **Homepage hero**: "Start Free Demo" button added next to "Join Free Beta Access" CTA, subtle purple outline style, links to `/demo`. Visible on desktop and mobile.
- **Dashboard banner**: Updated to "You are in Demo Mode — upgrade to unlock real-time signals and live trading." with purple Upgrade CTA button.
- **Behavior**: Demo mode bypasses all subscription/auth checks. Uses mock data only. Pro features locked. No redirect to /upgrade.
- **Testing**: 13/13 passed (iteration 51). Pricing page re-verified iteration 52 (8/8). Hero button verified iteration 53 (7/7).

### Phase 8.3: Subscription Health Dashboard (Feb 2026)
- **Backend**: `GET /api/admin/subscription-health` — returns active_subscribers, MRR ($29/pro + $99/elite), 30d churn, 7d failed payments, retry queue, 7d upcoming renewals, and 20 most recent subscription events. Cached 30 seconds.
- **Frontend**: New "Sub Health" tab in Admin Panel with 6 color-coded metric cards (green/purple/red/amber) and a Recent Subscription Events table sorted newest first with color-coded event types.
- **UI**: Loading skeletons, error state with retry, subtle framer-motion entrance animations, mobile responsive (2-col → 6-col grid).
- **Testing**: 15/15 tests passed (iteration 44).

### Bug Fix: LivePriceTicker Z-Index Overlap (Feb 2026)
- **Issue**: Price ticker completely hidden behind fixed navbar (both at y=0) and hero background layers
- **Root Cause**: Page wrapper had no padding-top to account for fixed navbar (h=90px). Ticker started at y=0, same as navbar.
- **Fix**: Added `pt-[92px]` to LandingPage wrapper, `relative z-40` + solid `bg-[#050505]` to ticker, reduced hero padding. Stacking: navbar (z-50, fixed y=0) → ticker (z-40, y=92) → hero (auto, y=137)
- **Testing**: 16/16 passed (iteration 46)

### Ticker Extension: XRP + SOL (Mar 2026)
- **Backend**: Added XRP (`XXRPZUSD`) and SOL to Kraken API query, symbol_map, sort order, and fallback data in `/api/market/live-prices`.
- **Frontend**: Ticker now displays BTC, ETH, XRP, SOL with consistent formatting. Mobile: horizontal scroll for overflow.
- **Layout verified**: Navbar (z-50, y=0) → Ticker (z-40, y=92) → Hero (auto, y=137). Zero overlap.
- **Testing**: All tests passed (iteration 47).

### Phase 9: Live User Stats Admin Card (Mar 2026)
- **Backend**: `GET /api/admin/user-stats` — returns `total_users`, `new_users_7d`, `active_users_24h` from MongoDB. 30-second in-memory cache. No external API calls.
- **Frontend**: "Live User Stats" card in Admin overview tab with 3 animated metrics: Total Users (purple), New Users 7d (blue), Active 24h (green). Loading skeletons and error handling with retry.
- **Testing**: All tests passed (iteration 48).

### Phase 8: High-Conversion Hero Section Redesign (Feb 2026)
- **Hero Section** — Complete redesign with premium fintech aesthetic (dark theme, purple accents). Left-aligned asymmetric layout with institutional-grade Live Metrics Terminal.
- **Headline**: "AI-Generated Crypto Strategies. Verified On-Chain." — clear value proposition.
- **Sub-headline**: Explains on-chain verification of Sharpe ratio, win rate, drawdown.
- **Micro-copy**: "Transparent metrics. Immutable records. Built for traders who verify."
- **CTAs**: "Join Free Beta Access (Limited Spots)" → /register, "View Live Metrics" → /leaderboard.
- **Trust Bar**: 4 credibility points (Verified On-Chain, Transparent Metrics, Built for Serious Traders, Zero Hype Real Data).
- **Live Metrics Terminal**: Real-time styled terminal showing Alpha Engine V4 metrics with pulsing Live indicator. Hidden on mobile.
- **Responsive**: Full mobile optimization with stacked CTAs, stacked trust items, hidden terminal.
- **Testing**: 17/17 tests passed (iteration 41).

### Phase 8.1: Dynamic Beta Spots Counter (Feb 2026)
- **Backend**: `GET /api/public/beta-spots` — public endpoint returning `{total, used, remaining}`. Reads `BETA_SPOTS_TOTAL` from env (default 50). Counts users with `is_beta_tester: true`.
- **User Model**: Added `is_beta_tester` field (boolean). Set to `true` on new registration via `/api/auth/register`.
- **Frontend**: Fetches beta spots on load + polls every 30s. Displays "Spots Remaining: X" with green dot. Amber pulse when <=5 remaining. CTA disabled with "Beta Full — Join Waitlist" when 0 remaining.
- **No fake scarcity**: Counter reflects real signups only.
- **Testing**: 14/14 tests passed (iteration 42).

### Phase 8.2: Waitlist System (Feb 2026)
- **Backend**: `POST /api/public/waitlist` — accepts `{email, note?}`, validates email format, rate limits 3/IP/hour, stores in `waitlist` collection with unique email index. Idempotent on duplicates.
- **Backend Admin**: `GET /api/admin/waitlist` — returns all entries sorted newest first, excludes IP field.
- **Frontend Modal**: When beta full (remaining<=0), CTA becomes "Join Waitlist" opening a premium dark-themed modal with email input, optional note textarea, inline validation, and success state.
- **Admin Panel**: New "Waitlist" tab with table (email, note, date) and client-side CSV export.
- **Testing**: 17/17 tests passed (iteration 43). 2 backend pytest cases hit rate limit during sequential testing — expected behavior, not bugs.
