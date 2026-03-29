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

## Backlog (P2)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia
