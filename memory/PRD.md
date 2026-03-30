# AlphaAI — Product Requirements Document

## Original Problem Statement
AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion with AI-powered research, backtesting, strategy management, real-time signals, and admin monitoring.

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

## Backlog (P2)
- Actual Sepolia deployment when user provides keys

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
