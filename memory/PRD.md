# AlphaAI Fund Platform - Product Requirements Document

## Current Status: Phase 12 Complete - Advanced Performance Metrics

### Overview
AlphaAI is an AI-powered crypto signals platform with full trading capabilities. Users can view signals, execute trades (paper or live via Uniswap V3), and track portfolio performance.

**Copyright © 2026 Martin Maughan. All rights reserved.**

---

### Latest Feature: Advanced Performance Metrics (March 2026)

**Performance Metrics Features:**
- **Paper vs Live Separation** - Clear distinction between simulated and real trading results
- **Equity Curve Charts** - Daily overview + trade-by-trade detail
- **Sharpe Ratio** with BTC Buy-and-Hold benchmark comparison
- **Sortino Ratio** (downside-only volatility)
- **Calmar Ratio** (return/max drawdown)
- **Daily PnL** breakdown with winning/losing days
- **Compliance Labels** - "PAPER TRADING" (purple) / "LIVE TRADING" (red) badges
- **Expandable Disclaimers** with full risk warnings
- **Demo Data Generator** - Populates realistic 30-day paper trading history

**Metrics API Endpoints:**
- `GET /api/metrics/compliance/{mode}` - Get compliance labels and disclaimers
- `GET /api/metrics/summary` - Complete performance summary
- `GET /api/metrics/equity-curve/daily` - Daily equity curve data
- `GET /api/metrics/equity-curve/trades` - Trade-level equity changes
- `GET /api/metrics/sharpe` - Sharpe/Sortino/Calmar with benchmark
- `GET /api/metrics/daily-pnl` - Daily PnL breakdown
- `GET /api/metrics/combined` - Paper + Live side-by-side comparison
- `POST /api/demo/generate-trades` - Generate realistic demo trading data
- `DELETE /api/demo/clear-trades` - Clear demo data
- `GET /api/demo/status` - Check demo data status

**Frontend Dashboard:**
- Side-by-side Paper vs Live performance cards
- Tabbed navigation: Overview | Equity Curves | Risk Metrics | Daily P&L
- Period selector (7D, 30D, 90D)
- Interactive charts with tooltips
- Compliance badges and expandable disclaimers

---

### Phase 11: Full Authentication System
- Email/Password JWT authentication
- Email verification for signups
- Optional 2FA (TOTP) with QR code
- Password reset flow
- WebSocket endpoint for Pro users

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

**Phase 10**: Live Trading System
- Paper trading with simulated execution
- Uniswap V3 live trading preparation

**Phase 11**: Full Authentication System ✅
- Email/Password JWT authentication
- Email verification, 2FA, password reset

**Phase 12**: Advanced Performance Metrics ✅ NEW
- Paper vs Live trading separation
- Equity curves, Sharpe ratio, Daily PnL
- Compliance badges and disclaimers

**Phase 14**: Mobile API v1 ✅ NEW
- Versioned API (`/api/v1/` prefix)
- Balanced optimization (pagination, field selection, ETag caching)
- Cross-platform JWT auth with `expires_in`
- Push notification hooks (Expo/FCM/APNs ready)
- Device registration and notification preferences
- Mobile-optimized trading execution

---

### API Summary

```
Mobile API v1 (/api/v1/):
- GET /health, /ping, /config
- POST /auth/login, /auth/refresh
- GET /auth/me?fields=id,name
- GET /signals?page=1&limit=20&fields=id,symbol
- GET /signals/latest
- GET /portfolio/summary
- GET /portfolio/positions?status=open
- POST /trading/execute
- POST /devices/register
- GET /devices
- PUT /devices/{id}/token
- GET/PUT /notifications/preferences
- GET /metrics/summary

Referrals:
- GET /api/referrals/config
- POST /api/referrals/create-code
- GET /api/referrals/stats
- GET /api/referrals/activity
- GET /api/referrals/earnings
- GET /api/referrals/validate-code
- POST /api/referrals/track-click
- POST /api/referrals/track-signup
- POST /api/referrals/track-conversion
- GET /api/referrals/leaderboard
- POST /api/referrals/request-payout

Performance Metrics:
- GET /api/metrics/compliance/{mode}
- GET /api/metrics/summary
- GET /api/metrics/equity-curve/daily
- GET /api/metrics/equity-curve/trades
- GET /api/metrics/sharpe
- GET /api/metrics/daily-pnl
- GET /api/metrics/combined

Authentication:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- GET /api/auth/me
- POST /api/auth/2fa/enable|verify|disable

Trading:
- POST /api/trading/execute
- GET /api/trading/positions
- GET /api/trading/portfolio

Signals:
- GET /api/signals/tiered
- GET /api/signals/free
- GET /api/signals/pro

Payments:
- POST /api/payments/checkout
- GET /api/payments/status/{session_id}
```

---

### Test Results (March 2026)
- **Mobile API v1**: 100% (34/34 tests)
- **Referral Backend**: 100% (19/19 tests)
- **Metrics Backend**: 100% (22/22 tests)
- **Auth Backend**: 100% (26/26 tests)
- **Overall**: All systems operational

---

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Shadcn/UI + Recharts
- **Database**: MongoDB
- **Auth**: JWT (python-jose) + TOTP (pyotp)
- **Payments**: Stripe
- **Trading**: Uniswap V3 (Sepolia testnet)
- **AI**: OpenAI GPT-5.2
- **Market Data**: Kraken API

---

### Next Action Items (P0)
1. ~~Execute sample trades to populate metrics demo data~~ ✅ DONE
2. ~~Implement email sending for auth verification/reset~~ ✅ DONE (Resend integration)
3. Deploy smart contract to Sepolia mainnet
4. Configure production Resend API key for live emails

### Upcoming Tasks (P1)
- Add email notifications for trades and Pro signal alerts
- Implement stop-loss/take-profit orders
- Complete WebSocket frontend integration

### Future Tasks (P2-P3)
- Copy trading feature
- Public leaderboard
- Referral program
- Mobile app optimization

---

### Known Limitations
- ~~Email sending is mocked (tokens logged to console)~~ Now uses Resend (requires API key)
- Live trading is prepared but uses testnet
- Metrics show 0% return for demo (need trades executed)

---
Last Updated: March 21, 2026
