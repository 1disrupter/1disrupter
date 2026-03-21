# AlphaAI Fund Platform - Product Requirements Document

## Current Status: Phase 10 Complete - Live Trading System

### Overview
AlphaAI is an AI-powered crypto signals platform with full trading capabilities. Users can view signals, execute trades (paper or live via Uniswap V3), and track portfolio performance.

**Copyright © 2026 Martin Maughan. All rights reserved.**

---

### Latest Feature: Live Trading System (March 2026)

**Trading Capabilities:**
- **Paper Trading**: Simulated trades with $10,000 starting balance
- **Live Trading**: Uniswap V3 integration (Sepolia testnet)
- **Trade Execution**: One-click from AI signals
- **Portfolio Tracking**: Real-time PnL, positions, history

**Trading API Endpoints:**
- `POST /api/trading/execute` - Execute trade (paper or live)
- `GET /api/trading/positions` - Get open positions
- `GET /api/trading/portfolio` - Get portfolio with PnL
- `GET /api/trading/history` - Get trade history
- `GET/POST /api/trading/mode` - Get/set trading mode
- `GET /api/trading/supported-tokens` - List supported tokens

**Frontend Trading UI:**
- Trading Mode Toggle (Simulation ↔ Live)
- "Execute" button on each BUY/SELL signal
- Trade confirmation modal with amount selection
- Open positions display with unrealized PnL
- Portfolio summary card

---

### All Implemented Features

**Phase 1-7**: Core MVP, AI Agents, Simulation, Reports, Smart Contracts, Marketing Assets

**Phase 8**: High-Conversion Dashboard
- Today's AI Signals with live Kraken prices
- Performance metrics, AI Summary
- Upgrade CTAs, 2-minute popup, exit intent

**Phase 9**: Stripe Pro Subscription
- Monthly ($29) and Yearly ($249) plans
- Stripe Checkout integration
- Pro status activation

**Phase 10**: Live Trading System ✅ NEW
- Paper trading with simulated execution
- Uniswap V3 live trading preparation
- Trade execution from signals
- Portfolio and PnL tracking

---

### API Summary

```
Trading:
- POST /api/trading/execute
- GET /api/trading/positions
- GET /api/trading/portfolio  
- GET /api/trading/history
- GET/POST /api/trading/mode
- GET /api/trading/supported-tokens
- POST /api/trading/close-position
- POST /api/trading/confirm

Signals (Tiered):
- GET /api/signals/free (15-min delay)
- GET /api/signals/pro (real-time)
- GET /api/signals/tiered (auto-detect tier)
- GET /api/signals/history

Payments:
- POST /api/payments/checkout
- GET /api/payments/status/{session_id}
- GET /api/payments/packages

Analytics:
- POST /api/analytics/track
- GET /api/analytics/summary
- GET /api/analytics/daily
```

---

### Test Results (March 2026)
- **Trading Backend**: 100% (16/16 tests)
- **Trading Frontend**: 100% (6/6 UI tests)
- **Overall**: All systems operational

---

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Shadcn/UI
- **Database**: MongoDB
- **Payments**: Stripe
- **Trading**: Uniswap V3 (Sepolia testnet)
- **AI**: OpenAI GPT-5.2
- **Market Data**: Kraken API

---

### Next Action Items (P0)
1. Deploy smart contract to Sepolia mainnet
2. Enable live Uniswap V3 execution
3. Add email notifications for trades
4. Implement stop-loss/take-profit orders

### Future Tasks (P1-P3)
- Copy trading feature
- Mobile app
- Public leaderboard
- Referral program

---

### Known Limitations
- Live trading is prepared but uses testnet
- Paper trading is simulated (no real execution)
- SOL trades use ETH as proxy (SOL not on Ethereum)

---
Last Updated: March 19, 2026
