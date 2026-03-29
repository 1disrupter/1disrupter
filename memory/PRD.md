# AlphaAI — Product Requirements Document

## Original Problem Statement
AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion. The platform provides AI-powered research, backtesting, strategy management, and real-time trading signals.

## User Personas
- **Free Users**: Access limited features (1 strategy follow, delayed signals, basic leaderboard)
- **Pro Users ($29/mo)**: Unlimited follows, real-time alerts, full backtesting, AI research
- **Elite Users**: All Pro features + priority support, advanced analytics
- **Demo Users**: Full preview via `?demo=true` URL parameter, no auth required

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + Motor (Async MongoDB) + WebSockets
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, CoinGecko Public API

## Implemented Features (All Passing)

### Phase 1: Core Platform
- User authentication (JWT, 2FA, password reset, email verification)
- Dashboard with portfolio stats, AI signals, chart
- AI Agents management, Event Agents (news-driven)
- Strategy Lab, Marketplace, Copy Trading, Referral system
- Admin panel + analytics
- Demo Mode (`?demo=true`) global bypass

### Phase 2: Intelligence & Data
- **GPT-5.2 Research Engine** — real AI-powered crypto research
- **CoinGecko OHLC Integration** — real historical data for backtesting
- **Backtest Engine** — Sharpe ratio, drawdown, win rate calculations
- **Strategy Leaderboard** — ranked by Sharpe ratio with real data
- **Follow Strategy System** — follow/unfollow with Pro gating
- **In-App Notifications** — inbox with read/unread
- **Stripe Pro-Tier Gating** — checkout, subscription management
- **Real-Time Strategy Alerts (WebSocket)** — live signals for Pro users, demo mock streaming

### Phase 3: Admin Traffic Analytics (NEW — March 29, 2026)
- **Event Logging System** — `POST /api/admin/events` accepts page_view, api_call, strategy_view, follow, unfollow, signal, ws_connect, ws_disconnect, upgrade_prompt, checkout_start, checkout_success, error events
- **Aggregated Summary** — `GET /api/admin/traffic/summary` with 18 metric fields over 24h/7d/30d ranges
- **Timeseries Data** — `GET /api/admin/traffic/timeseries` for time-bucketed charts
- **Raw Event Table** — `GET /api/admin/traffic/events` with pagination and type filtering
- **Global Frontend Tracking** — `useTracking` hook auto-fires page_view on route changes, captures errors globally
- **Component-Level Tracking** — UpgradeModal (upgrade_prompt, checkout_start), useStrategyAlerts (ws_connect, ws_disconnect, signal), LeaderboardPage (strategy_view, follow, unfollow), FollowingPage (unfollow)
- **Admin Dashboard** — `/admin/traffic` with 6 KPI cards, 2 charts, conversion funnel, system health, raw event table
- **Access Control** — Admin-only via admin_key query parameter

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login` | POST | User login |
| `/api/research/ai-query` | POST | GPT-5.2 research |
| `/api/simulation/backtest` | POST | CoinGecko backtests |
| `/api/leaderboard/strategies` | GET | Strategy rankings |
| `/api/strategies/{id}/follow` | POST | Follow strategy |
| `/api/notifications/inbox` | GET | User notifications |
| `/api/alerts/status` | GET | WebSocket connection stats |
| `/api/ws/alerts/{client_id}` | WS | Real-time strategy alerts |
| `/api/admin/events` | POST | Log traffic event |
| `/api/admin/traffic/summary` | GET | Aggregated traffic metrics |
| `/api/admin/traffic/timeseries` | GET | Time-bucketed chart data |
| `/api/admin/traffic/events` | GET | Paginated raw events |

## Database Collections
- `users`, `strategies`, `strategy_leaderboard`, `followed_strategies`
- `notifications_inbox`, `research_queries`, `simulations`
- `traffic_events` (NEW — type, user_id, timestamp, metadata)

## Test Results
- Iterations 25-31: All passing (100% success rate)

## Backlog (P2)
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia
