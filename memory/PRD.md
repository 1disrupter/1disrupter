# AlphaAI — Product Requirements Document

## Original Problem Statement
AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion. The platform provides AI-powered research, backtesting, strategy management, real-time trading signals, and comprehensive admin monitoring.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + Motor (Async MongoDB) + WebSockets
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, CoinGecko, Resend

## Implemented Features (All Passing — Iterations 25-34)

### Phase 1: Core Platform
- User auth (JWT, 2FA, password reset, email verification), Dashboard, AI Agents, Event Agents
- Strategy Lab, Marketplace, Copy Trading, Referral system, Admin panel + analytics
- Demo Mode (`?demo=true`) global bypass

### Phase 2: Intelligence & Data
- GPT-5.2 Research Engine, CoinGecko OHLC Integration, Backtest Engine
- Strategy Leaderboard, Follow Strategy + Notifications, Stripe Pro-Tier Gating
- Real-Time Strategy Alerts (WebSocket)

### Phase 3: Admin Analytics + Monitoring
- Event Logging (`POST /api/admin/events`), Summary/Timeseries/Raw Events endpoints
- Global + Component-Level Frontend Tracking
- Admin Dashboard `/admin/traffic` with KPIs, charts, funnel, system health
- WebSocket admin event stream `/api/ws/admin/events`
- Live Event Stream panel with pause/resume, filters, auto-scroll

### Phase 3d: Alerting System (March 29, 2026)
- **Rule Engine** — Background task running every 5s, evaluating 6 rules:
  1. Error Spike (10+ errors in 60s)
  2. Traffic Surge (100+ page views or 200+ API calls in 60s)
  3. WebSocket Disconnect Storm (15+ disconnects in 30s)
  4. Strategy Alert Flood (20+ signals from same strategy in 30s)
  5. Checkout Failure Spike (5+ failed checkouts in 10min)
  6. Suspicious User Behavior (50+ API calls from same user in 10s)
- **Alert Events** — Inserted into `traffic_events` with type="alert", broadcast to admin WS
- **Cooldown** — 120s per alert type to prevent spam
- **Founder Email Alerts** — Via Resend, suppressed in Demo Mode, 3-retry logic
- **UI Enhancements**:
  - ALERT ACTIVE badge with pulse animation
  - Active Alerts banner with alert type badges
  - Red-styled alert lines in live feed (bold, icon, left border)
  - Pin-to-top for 10 seconds
  - "Alerts Only" filter option
  - Sound toggle button
  - Alert count badge in live stream header
  - Red-highlighted rows in raw events table

### Phase 3e: Responsive Navigation (March 29, 2026)
- Priority-based nav: 5 primary items + "More" dropdown
- No overflow at 1024px, 1366px, 1920px
- Mobile hamburger menu at < 768px

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/admin/events` | POST | Log traffic event |
| `/api/admin/traffic/summary` | GET | Aggregated metrics |
| `/api/admin/traffic/timeseries` | GET | Time-bucketed charts |
| `/api/admin/traffic/events` | GET | Paginated raw events |
| `/api/admin/traffic/active-alerts` | GET | Currently triggered alert types |
| `/api/admin/traffic/stream-status` | GET | Admin WS stats |
| `/api/ws/admin/events` | WS | Real-time admin event stream |

## Backlog (P2)
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia
