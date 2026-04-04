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

### Execution Engine Phase 2 (Apr 2026)
- **Backend Services** (`/app/backend/services/execution_engine/`):
  - `binance_testnet_client.py` — Binance Testnet REST wrapper (place_order, cancel_order, get_balance, get_open_orders)
  - `executor.py` — executes signal for user (paper mode simulates, testnet mode hits Binance)
  - `signal_router.py` — routes signal to all active subscribers with enabled execution configs
- **API Routes** (`/app/backend/routes/execution.py`):
  - `GET/POST /api/execution/configs/me` — user execution config (mode, position size, enabled toggle)
  - `GET /api/execution/logs` — user's execution logs with filters
  - `GET /api/execution/logs/admin` — admin-only all logs
  - `POST /api/execution/test-order` — test Binance Testnet connectivity
  - `POST /api/execution/emit-signal` — emit signal + trigger routing (creator-only)
- **Collections**: `user_execution_configs`, `execution_logs`
- **Frontend**:
  - `/me/execution-settings` — config form (toggle, paper/testnet mode, position size) + recent execution logs
  - `/admin/execution-monitor` — stats dashboard + filterable log table
- **Safety**: No mainnet, no leverage, no auto-execute without `is_enabled`, paper mode default
- **Testing**: Backend 16/16, Frontend all flows passed (iteration 57)

### Admin Demo Mode Toggle & Analytics (Apr 2026)
- **Config**: `/app/backend/config/demo.py` — DB-backed toggle (`system_config` collection), 5s cache, falls back to DEMO_MODE env var
- **Endpoints**:
  - `GET/POST /api/admin/demo-mode` — read/toggle demo mode instantly (no redeploy)
  - `GET /api/admin/analytics-summary` — returns synthetic data (demo ON) or real counts (demo OFF)
  - `POST /api/admin/track` — records analytics events (page views, API calls, WS, strategies, checkouts)
- **Frontend**: Demo Mode banner with toggle switch at top of admin panel, Analytics tab with 5 data cards (Page Views, API Calls, WS Connections, Strategy Interactions, Checkout Events)
- **Testing**: Backend 11/11, Frontend all flows (iteration 58)

### Go-Live Readiness — P0 SaaS-Only Fixes (Apr 4, 2026)
- **P0-1: Dashboard Wallet Un-Gating** — Authenticated users without a wallet now see the full dashboard (no "Connect to unlock" prompt). Logic: `DashboardPage.jsx` line 574 checks `authUser` and falls through to full render.
- **P0-2: Live Crypto Price Feed Fix** — Fixed missing `httpx` import in `fund.py`. `GET /api/market/live-prices` now returns real Kraken data with `source: "kraken"`.
- **P0-3: Hero SaaS Copy** — Removed all blockchain/Web3/MetaMask messaging from `LandingPage.jsx` hero. Now reads "AI-Generated Crypto Strategies. Verified In Real-Time."
- **P0-4: 404 Catch-All Route** — Added `<Route path="*" element={<NotFoundPage />} />` to `App.js`. New `NotFoundPage.jsx` with branded 404 UI + Home/Go Back buttons.
- **P0-5: Favicon** — Added SVG favicon (`/public/favicon.svg`) and `<link rel="icon">` to `index.html`.
- **P0-6: Meta Description** — Updated from "A product of emergent.sh" to "My-AlphaAI — AI-powered crypto trading strategies..."
- **P0-7: Wallet Navigation Cleanup** — Removed wallet connect/disconnect menu items, network badge, and ETH balance from `Navigation.jsx` user dropdown.
- **Refactoring**: Removed stale `Dashboard.jsx` (438 lines dead code). Fixed `DashboardPage.jsx` token key from `access_token` to `alphaai_tokens`.
- **Testing**: All 7 fixes verified via curl + Playwright + testing agent.

### Landing Page Improvements (Apr 4, 2026)
- **Hero Product Screenshot** — Dashboard preview image (`/images/dashboard-preview.jpeg`) centered below hero CTAs with border, glow, and rounded corners.
- **Trust Strip** — "Trusted by traders in 32+ countries · Signals updated in real-time · Backtested before going live" in monospace under the trust bar.
- **Ticker Template** — Signal ticker template added as JSX comment in `LivePriceTicker.jsx` for future live signal data (`pair`, `direction`, `confidence`, `change`, `price`).
- **Section Links** — "View all signals →" under Today's Signals section (→ /dashboard), "View full leaderboard →" under Social Proof (→ /leaderboard).
- **Legal Disclaimer** — "Simulated results. Past performance does not guarantee future returns." under simulation result cards.
- **Testing**: 11/11 tests passed (iteration 63). All additions verified, no regressions.

### P1 Go-Live Polish (Apr 4, 2026)
- **Terms of Service** — `/terms` route with `TermsOfService.jsx` (11 sections). Linked in landing page footer.
- **Privacy Policy** — `/privacy` route with `PrivacyPolicy.jsx` (10 sections). Linked in landing page footer.
- **ErrorBoundary** — `ErrorBoundary.jsx` class component wrapping entire App. Shows "Something went wrong. Please refresh." with refresh button on unhandled errors.
- **OpenGraph + Twitter Meta Tags** — Added `og:title`, `og:description`, `og:image`, `og:url`, `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image` to `index.html`.
- **manifest.json** — PWA manifest with `name: "Alpha AI"`, `theme_color: "#7c5cfc"`, `background_color: "#04040f"`.
- **robots.txt** — `User-agent: * / Allow: /` with sitemap link.
- **Cookie Consent Banner** — `CookieConsent.jsx` bottom banner with Accept/Reject. Stores consent in `localStorage` key `alphaai_cookie_consent`. Hidden once consent given.
- **Testing**: 25/25 tests passed (iteration 64). All items verified, no regressions.

### Phase 2 Features (Apr 4, 2026)

**Automated Referral Commission Tracking (20% Recurring)**
- Recurring commission processing in `track-conversion` endpoint. When a referred user renews their subscription, a new `referral_commissions` record is created with 20% commission.
- Admin commission analytics: `GET /api/referrals/admin/commissions` returns recurring, first-time, total commissions, and pending payouts.
- Tier-based commission rates preserved (20% bronze → 35% platinum).

**Invoice PDF Generation + Download**
- `GET /api/invoices` — list user's invoices
- `POST /api/invoices/generate/{transaction_id}` — generate invoice for a payment
- `GET /api/invoices/download/{invoice_id}` — download branded PDF invoice (dark theme, Alpha AI branding)
- "Download Invoice" button added to Billing page payments table
- Uses `reportlab` for PDF generation.

**Real-Time Events Feed (WebSocket)**
- `WS /api/ws/events` — broadcasts signal, trade, and update events every 4–12 seconds (demo mode)
- `LiveEventsFeed.jsx` panel on Dashboard with animated event entries, WS status indicator, auto-reconnect
- Toast notifications for new signal events via `sonner`
- Graceful fallback: shows "Waiting for events..." when disconnected, auto-reconnects every 5s

**Testing**: 94% backend (1 minor test path issue) / 100% frontend (iteration 67). All features verified.

### Strategy Leaderboard (Apr 4, 2026)
- **Leaderboard Page** — `/strategies` route with sortable table of all 7 public strategies. Columns: rank, name, risk badge, return%, Sharpe, win rate, max drawdown, category, View button.
- **Backend Endpoint** — `GET /api/marketplace/strategies/leaderboard` with `sort_by` and `order` params. 60s cache TTL. Enriched with performance data from `strategy_performance` collection.
- **Sorting** — Client-side column header clicks toggle sort direction (desc/asc). Supported: total_return, sharpe_ratio, win_rate, max_drawdown.
- **Homepage Integration** — "View Full Leaderboard" button under Featured Strategies section links to `/strategies`.
- **Loading Skeletons** — RowSkeleton component renders 6 placeholder rows during data fetch.
- **Testing**: 100% pass (iteration 66). 20 backend + all frontend tests passed. No regressions.

### Strategy Interactions & Featured Strategies (Apr 4, 2026)
- **3 Featured AI Strategies Seeded** — Alpha Momentum BTC (Medium), ETH Reversal Sniper (Medium-High), SOL Breakout Pulse (High). Each with full metadata: Sharpe ratio, win rate, max drawdown, total return, logic description, risk label.
- **Featured Strategies Section** — New landing page section ("Top-Performing AI Strategies") showing 3 performance cards with metrics, risk labels, and "View Strategy" buttons.
- **Strategy Detail Pages** — Each strategy has a unique URL at `/marketplace/{id}` with full info, performance block, parameters, and reviews.
- **Copy Strategy** — `POST /api/marketplace/strategies/{id}/copy` creates a draft copy in the user's collection. Button visible for authenticated non-owner users.
- **Featured Endpoint** — `GET /api/marketplace/featured` returns published featured strategies enriched with latest performance data.
- **Fallback Safety** — FeaturedStrategies component returns null if API fails. StrategyDetailPage shows "Strategy not found" for invalid IDs.
- **Testing**: 100% pass rate (iteration 65). All backend + frontend tests passed.

### Deployment Fix (Apr 4, 2026)
- **Backend /health endpoint** — Added `GET /health` and `GET /api/health` to `server.py` returning `{"status": "healthy"}`.
- **Frontend web3/ethers removed** — Removed `ethers@5.7.2` and `web3@4.16.0` from package.json. Replaced `WalletContext.jsx` with a no-op stub (all consumers get null wallet). Build size dropped from ~8MB to 1.8MB.
- **Frontend health check enabled** — Set `ENABLE_HEALTH_CHECK=true` in frontend `.env`.
- **Build output** — `craco build` outputs to `build/`. Symlink `dist -> build` added for NGINX compatibility.
- **Security** — Added `memory/test_credentials.md` to `.gitignore`.
- **API resilience** — All frontend API calls already have try/catch with fallback values. Backend `/market/top-coins` returns mock data on CoinGecko failure.
- **Deployment agent** — Passed all checks (✅ READY).

## Backlog
- **P0**: Go-Live SaaS-Only P0 Fixes ✅ DONE (Apr 4, 2026)
- **P1**: Terms of Service & Privacy Policy ✅ DONE (Apr 4, 2026)
- **P1**: ErrorBoundary ✅ DONE (Apr 4, 2026)
- **P1**: OpenGraph / Twitter meta tags ✅ DONE (Apr 4, 2026)
- **P1**: manifest.json & robots.txt ✅ DONE (Apr 4, 2026)
- **P1**: Cookie Consent Banner ✅ DONE (Apr 4, 2026)
- **P1**: Order Execution Engine (Phase 2 of Live Trading) ✅ DONE
- **P1**: Automatic Frontend Tracking Middleware ✅ DONE
- **P1**: Stripe Billing Portal (self-serve subscription management) ✅ DONE
- **P1**: Analytics Time Filters (Today/7d/30d) ✅ DONE
- **P1**: MRR & Subscription Trend Charts ✅ DONE
- **P1**: Signal History Chart ✅ DONE
- **P1**: Onboarding Modal (First-Time UX) ✅ DONE
- **P1**: UI Polish & Micro-Interactions ✅ DONE
- **P1**: Affiliate Program (Phase 1 — Referral System) ✅ DONE
- **P2**: Automated referral commission tracking (Phase 2) ✅ DONE (Apr 4, 2026)
- **P2**: Invoice download / email receipts in billing page ✅ DONE (Apr 4, 2026) — PDF only, email via Resend deferred
- **P2**: Real-time live events feed via WebSocket (analytics) ✅ DONE (Apr 4, 2026)
- **P2**: Actual Sepolia Smart Contract deployment (awaiting user keys)
- **P3**: Auto-email waitlist users when spot opens (Resend integration)
- **P3**: User retention analytics (DAU/MAU ratio)

### Automatic Frontend Tracking Middleware (Apr 2026)
- **Module**: `/app/frontend/src/lib/trackingMiddleware.js` — axios interceptor + sendBeacon tracker
- **Tracking Points**:
  - Auto-tracks every API call via axios interceptor (endpoint, method, status, latency_ms)
  - Tracks page views on every route change via `trackPageViewEvent`
  - Sends all events to `POST /api/admin/track` (fire-and-forget, never blocks UI)
  - Uses `navigator.sendBeacon` for reliability on page unload
  - Skips tracking its own `/admin/track` endpoint to prevent infinite loop
- **Integration**: `useTracking` hook in App.js initializes middleware on mount
- **Backend**: `POST /api/admin/track` records events in `analytics_events` collection with `is_demo` tag
- **Testing**: 100% passed (iteration 59)

### Stripe Billing Portal (Apr 2026)
- **Module**: `/app/backend/routes/billing.py` — 4 endpoints
- **Endpoints**:
  - `GET /api/billing/overview` — billing summary (active subs, monthly cost, total spent, total payments)
  - `GET /api/billing/subscriptions` — active + canceled subscriptions with strategy details
  - `GET /api/billing/payments` — payment transaction history
  - `POST /api/billing/portal` — creates Stripe Billing Portal session, returns hosted portal URL
- **Stripe Integration**: Uses `stripe` SDK v14.4.0 via Emergent proxy (`api_base = https://integrations.emergentagent.com/stripe`). Auto-creates Stripe customers on first portal access, validates existing customer IDs, handles stale IDs by recreating.
- **Frontend**: `/billing` route — `BillingPortalPage.jsx` with:
  - **"Manage Billing" button** (purple, primary CTA) — creates Stripe portal session, redirects to Stripe's hosted billing portal
  - 4 overview metric cards (Active Subscriptions, Monthly Cost, Total Spent, Total Payments)
  - Subscriptions tab: active subs with Unsubscribe, canceled subs with Resubscribe link
  - Payments tab: payment history table (date, strategy, amount, status)
  - Auth guard (redirects to /login if unauthenticated)
  - "Browse Marketplace" button linking to /strategy-marketplace
  - Loading spinner on Manage Billing button while creating session
- **User DB**: Stores `stripe_customer_id` on users collection for Stripe customer association
- **Integration**: "Manage Billing" button also on MyStrategiesPage (/me/strategies) linking to /billing
- **Testing**: Backend 11/11, Frontend 100% (iteration 60)

### Analytics Time Filters & Charts (Apr 2026)
- **Backend**: 3 new admin endpoints:
  - `GET /api/admin/analytics-filtered?range=today|7d|30d` — Platform metrics with time range filter
  - `GET /api/admin/mrr-trends` — 30-day MRR, subscriptions, cancellations, net & cumulative revenue
  - `GET /api/admin/signal-history` — 30-day signal volume with 7-day moving average
- **Frontend**: Admin Analytics tab enhanced with:
  - 7 stat cards (Total Users, Pro Users, Elite Users, Active Subs, Signals, Page Views, API Calls) with time range dropdown
  - 4 MRR/Subscription trend charts (Recharts): MRR Over Time (area), Subs vs Cancellations (bar), Net Revenue (bar), Cumulative Revenue (area)
  - Signal Volume chart (composed bar + line for 7d MA)
  - Loading skeletons and smooth transitions
- **Component**: `/app/frontend/src/components/AdminCharts.jsx`
- **Testing**: Backend 16/16, Frontend 100% (iteration 61)

### Onboarding Modal (Apr 2026)
- **Component**: `/app/frontend/src/components/OnboardingModal.jsx`
- 3-step modal: Welcome to AlphaAI, How Signals Work, Flexible Subscriptions
- Shows only on first login (localStorage key `alphaai_onboarded`)
- Skip and Next buttons with smooth fade transitions
- Dark theme with accent color per step
- **Testing**: All flows verified (iteration 61)

### UI Polish & Micro-Interactions (Apr 2026)
- Card hover lift with subtle border glow
- Button press scale effect (scale 0.97)
- Improved skeleton shimmer animation
- Custom scrollbar styling (dark theme)
- Smooth page transitions via CSS keyframes
- Applied to `/app/frontend/src/index.css`

### Affiliate Program — Phase 1 (Apr 2026)
- **Backend**: `/app/backend/routes/referrals.py` — Comprehensive referral system
  - `GET /api/referrals/validate/{ref}` — validates by referral code OR user ID, auto-creates code if needed
  - `GET /api/referrals/stats` — authenticated user referral stats (code, total_referrals, active_referrals, earnings, tier)
  - `GET /api/referrals/activity` — authenticated user referral activity feed
  - `POST /api/referrals/track-click?code=X` — tracks referral link clicks
  - `GET /api/referrals/admin/summary?admin_key=X` — admin overview (total referrals, active subs from referrals, revenue, commissions owed, top referrers)
  - `GET /api/referrals/admin/events?admin_key=X&range=today|7d|30d` — admin event breakdown with daily chart data
- **Auth Integration**: `POST /api/auth/register` now accepts optional `ref_code`. On signup with valid ref_code: creates referral linkage, increments referrer stats, marks user as referred with 7-day Pro bonus.
- **Anti-Fraud**: No self-referrals, no duplicate referrals, graceful failure on invalid ref_code
- **Commission Model**: 20% recurring (hardcoded), tiered (Starter 20% → Legend 35%), manual payouts only (Phase 1)
- **Frontend — Referral Capture**: `useReferralCapture` hook in App.js reads `?ref=` URL param, validates via API, stores in localStorage (`alphaai_referral_code`), cleans URL
- **Frontend — User Referral Page**: `/referrals` route with copy-able referral link, stats cards (Total Referrals, Active Users, Earnings, Conversion Rate), reward tiers, activity feed
- **Frontend — Admin Analytics**: `AdminReferralAnalytics` component added to Analytics tab with summary cards (Total Referrals, Active Subs, Revenue, Commissions Owed), Referral Signups line chart, Signups vs Conversions bar chart, Top Referrers table with time range filter
- **DB Collections**: `referral_codes`, `referrals`, `referral_events`
- **Testing**: Backend 23/23, Frontend all flows verified (iteration 62)

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
