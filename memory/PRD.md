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
- AI Agents management
- Event Agents (news-driven)
- Strategy Lab (create/run strategies)
- Marketplace
- Copy Trading
- Referral system
- Admin panel + analytics
- Demo Mode (`?demo=true`) global bypass

### Phase 2: Intelligence & Data
- **GPT-5.2 Research Engine** — real AI-powered crypto research (`/api/research/ai-query`)
- **CoinGecko OHLC Integration** — real historical data for backtesting (`services/market_data.py`)
- **Backtest Engine** — Sharpe ratio, drawdown, win rate calculations (`services/backtest_engine.py`)
- **Strategy Leaderboard** — ranked by Sharpe ratio with real data (`/leaderboard`)
- **Follow Strategy System** — follow/unfollow with Pro gating (`/api/strategies/{id}/follow`)
- **In-App Notifications** — inbox with read/unread (`/api/notifications/inbox`)
- **Stripe Pro-Tier Gating** — checkout, subscription management, upgrade modal
- **Real-Time Strategy Alerts (WebSocket)** — live signals for Pro users, demo mock streaming (`/api/ws/alerts/{client_id}`)

## Key Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login` | POST | User login |
| `/api/auth/register` | POST | User registration |
| `/api/research/ai-query` | POST | GPT-5.2 research |
| `/api/simulation/backtest` | POST | CoinGecko backtests |
| `/api/leaderboard/strategies` | GET | Strategy rankings |
| `/api/strategies/{id}/follow` | POST | Follow strategy |
| `/api/notifications/inbox` | GET | User notifications |
| `/api/alerts/status` | GET | WebSocket connection stats |
| `/api/alerts/test` | POST | Broadcast test alert |
| `/api/ws/alerts/{client_id}` | WS | Real-time strategy alerts |

## Database Schema
- `users`: auth, profile, stripe IDs, subscription tier
- `strategies`: parameters, metrics, timestamps
- `strategy_leaderboard`: ranked strategies with Sharpe data
- `followed_strategies`: user_id + strategy_id
- `notifications_inbox`: user_id, message, type, read status
- `research_queries`: AI research history
- `simulations`: backtest results

## Demo Mode
- URL param `?demo=true` activates globally
- Bypasses auth, Stripe gating, and external API limits
- Returns mock/static data for all features
- WebSocket streams mock alerts every 10-20 seconds

## Test Results
- Iterations 25-30: All passing (100% success rate)
- Backend: REST + WebSocket endpoints fully tested
- Frontend: All UI flows verified

## Backlog (P2)
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia
