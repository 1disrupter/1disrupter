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

### Phase 3: Admin Traffic Analytics + Real-Time Event Streaming
- Event Logging, Aggregated Summary, Timeseries, Raw Events endpoints
- Global Frontend Tracking + Component-Level Tracking
- Admin Dashboard at `/admin/traffic` with KPIs, charts, funnel, system health
- WebSocket admin event stream at `/api/ws/admin/events`
- Live Event Stream panel with pause/resume, filters, auto-scroll

### Phase 3c: Responsive Navigation Fix (March 29, 2026)
- **Priority-based nav split**: 5 primary items (Dashboard, Leaderboard, Research, Strategy Lab, Alerts) always visible
- **"More" dropdown**: 8 overflow items (Simulation, AI Agents, Event Agents, Marketplace, Copy Trading, Following, Referrals, Pricing) + 3 admin items (Admin Panel, Demo Analytics, Traffic)
- **Responsive breakpoints**: `xl` for Demo toggle, `md` for hamburger menu
- **No horizontal overflow** at 1024px, 1366px, or 1920px
- **Mobile hamburger menu** with all items at < 768px

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
- Iterations 25-33: All passing (100% success rate except 1 minor fix applied)

## Backlog (P2)
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia
