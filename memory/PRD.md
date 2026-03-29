# AlphaAI — Product Requirements Document

## Original Problem Statement
AlphaAI is a B2C/SaaS crypto trading signals platform optimized for conversion. The platform provides AI-powered research, backtesting, strategy management, and real-time trading signals.

## User Personas
- **Free Users**: Limited features (1 strategy follow, delayed signals, basic leaderboard)
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
- AI Agents, Event Agents, Strategy Lab, Marketplace, Copy Trading, Referral system
- Admin panel + analytics
- Demo Mode (`?demo=true`) global bypass

### Phase 2: Intelligence & Data
- GPT-5.2 Research Engine, CoinGecko OHLC Integration, Backtest Engine
- Strategy Leaderboard (Sharpe ratio ranking)
- Follow Strategy System + In-App Notifications
- Stripe Pro-Tier Gating
- Real-Time Strategy Alerts (WebSocket)

### Phase 3: Admin Traffic Analytics
- Event Logging System (`POST /api/admin/events`)
- Aggregated Summary, Timeseries, Raw Events endpoints
- Global Frontend Tracking (page_view, error capture)
- Component-Level Tracking (strategy_view, follow/unfollow, ws_connect/disconnect, signal, upgrade_prompt, checkout_start)
- Admin Dashboard at `/admin/traffic` with KPIs, charts, conversion funnel, system health

### Phase 3b: Real-Time Admin Event Streaming (NEW — March 29, 2026)
- **WebSocket endpoint** `GET /api/ws/admin/events` — broadcasts traffic events to connected admins in real-time
- **AdminEventsManager** — thread-safe connection manager with demo-only filtering
- **Non-blocking broadcast** — events POSTed to `/api/admin/events` are broadcast via `asyncio.create_task`
- **Live Event Stream panel** — embedded in `/admin/traffic` with:
  - Scrollable event feed (newest at bottom, auto-scroll)
  - Connection status indicator (Connected/Reconnecting/Disconnected)
  - Pause/Resume toggle with visual banner
  - Clear button
  - Event type filter (multi-select)
  - Demo vs Live filter
  - Exponential backoff reconnection (max 8 attempts)
  - Heartbeat/ping-pong keep-alive

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
| `/api/admin/traffic/stream-status` | GET | Admin WS connection stats |
| `/api/ws/admin/events` | WS | Real-time admin event stream |

## Database Collections
- `users`, `strategies`, `strategy_leaderboard`, `followed_strategies`
- `notifications_inbox`, `research_queries`, `simulations`
- `traffic_events` (type, user_id, timestamp, metadata)

## Test Results
- Iterations 25-32: All passing (100% success rate)
- Iteration 32: 23 backend + all frontend tests for admin streaming

## Backlog (P2)
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia
