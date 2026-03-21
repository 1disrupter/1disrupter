# AlphaAI Fund Platform - Product Requirements Document

## Current Status: Phase 11 Complete - Full Authentication System

### Overview
AlphaAI is an AI-powered crypto signals platform with full trading capabilities. Users can view signals, execute trades (paper or live via Uniswap V3), and track portfolio performance.

**Copyright © 2026 Martin Maughan. All rights reserved.**

---

### Latest Feature: Full Authentication System (March 2026)

**Authentication Features:**
- **Email/Password Registration & Login** with JWT tokens
- **Email Verification** for new signups (token-based)
- **Optional 2FA (TOTP)** with QR code and backup codes
- **Password Reset Flow** with secure tokens
- **Wallet Linking** - Connect Web3 wallet to account

**Auth API Endpoints:**
- `POST /api/auth/register` - Register with email/password
- `POST /api/auth/login` - Login (supports 2FA)
- `POST /api/auth/refresh` - Refresh JWT tokens
- `POST /api/auth/logout` - Logout (revoke tokens)
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/verify-email` - Verify email with token
- `POST /api/auth/2fa/enable` - Enable 2FA (returns QR code)
- `POST /api/auth/2fa/verify` - Verify 2FA setup
- `POST /api/auth/2fa/disable` - Disable 2FA
- `POST /api/auth/link-wallet` - Link Web3 wallet

**WebSocket Real-Time Updates:**
- `WS /ws/signals/{client_id}` - Real-time signals for Pro/Elite
- `GET /api/ws/status` - WebSocket connection statistics

**Frontend Auth Pages:**
- Login page with email/password and 2FA support
- Register page with password strength indicator
- Forgot password page
- Reset password page (token-based)
- Email verification page

---

### Phase 10: Live Trading System
- Paper trading with simulated execution
- Uniswap V3 live trading preparation
- Trade execution from signals
- Portfolio and PnL tracking

**Trading API Endpoints:**
- `POST /api/trading/execute` - Execute trade (paper or live)
- `GET /api/trading/positions` - Get open positions
- `GET /api/trading/portfolio` - Get portfolio with PnL
- `GET /api/trading/history` - Get trade history
- `GET/POST /api/trading/mode` - Get/set trading mode
- `GET /api/trading/supported-tokens` - List supported tokens

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

**Phase 10**: Live Trading System
- Paper trading with simulated execution
- Uniswap V3 live trading preparation

**Phase 11**: Full Authentication System ✅ NEW
- Email/Password JWT authentication
- Email verification for signups
- Optional 2FA (TOTP) with QR code
- Password reset flow
- WebSocket endpoint for Pro users

---

### API Summary

```
Authentication:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/forgot-password
- POST /api/auth/reset-password
- POST /api/auth/verify-email
- POST /api/auth/2fa/enable
- POST /api/auth/2fa/verify
- POST /api/auth/2fa/disable
- POST /api/auth/link-wallet

WebSocket:
- WS /ws/signals/{client_id}
- GET /api/ws/status

Trading:
- POST /api/trading/execute
- GET /api/trading/positions
- GET /api/trading/portfolio  
- GET /api/trading/history
- GET/POST /api/trading/mode
- GET /api/trading/supported-tokens

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
- **Auth Backend**: 100% (26/26 tests)
- **Auth Frontend**: 100% (8/8 UI tests)
- **Trading Backend**: 100% (16/16 tests)
- **Trading Frontend**: 100% (6/6 UI tests)
- **Overall**: All systems operational

---

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Shadcn/UI
- **Database**: MongoDB
- **Auth**: JWT (python-jose) + TOTP (pyotp)
- **Payments**: Stripe
- **Trading**: Uniswap V3 (Sepolia testnet)
- **AI**: OpenAI GPT-5.2
- **Market Data**: Kraken API

---

### Next Action Items (P0)
1. Implement email sending for verification/reset (currently logged)
2. Deploy smart contract to Sepolia mainnet
3. Enable live Uniswap V3 execution

### Upcoming Tasks (P1)
- Add email notifications for trades and Pro signal alerts
- Implement stop-loss/take-profit orders
- Complete WebSocket frontend integration for live price updates

### Future Tasks (P2-P3)
- Copy trading feature
- Public leaderboard
- Referral program
- Mobile app optimization

---

### Known Limitations
- Email sending is mocked (tokens logged to console)
- Live trading is prepared but uses testnet
- Paper trading is simulated (no real execution)
- SOL trades use ETH as proxy (SOL not on Ethereum)

---
Last Updated: March 21, 2026
