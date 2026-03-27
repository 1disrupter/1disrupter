# AlphaAI Fund Platform - Product Requirements Document

## Current Status: Phase 21 Complete - Free Tier + Conversion Hero

### Overview
AlphaAI is an AI-powered crypto signals platform with full trading capabilities. Users can view signals with AI-powered explanations, execute trades (paper or live via Uniswap V3), track portfolio performance, copy trades from top traders, and choose between Free, Pro, and Elite subscription tiers.

**Copyright © 2026 Martin Maughan. All rights reserved.**

---

### Latest Feature: Free Tier System with Pricing (March 2026)

**Tier System:**
- **Free** ($0): Paper trading only, 15-min signal delay, top 10 leaderboard, no copy trading, no live trades, no advanced analytics
- **Pro** ($29/mo or $249/yr): Real-time signals, live trading, copy trading, full leaderboard, follow & be followed, full analytics, push notifications
- **Elite** ($79/mo or $699/yr): Everything in Pro + priority signal delivery, early access to features, higher rate limits, advanced research tools, dedicated support

**Backend Implementation:**
- `user_tier` field added to user model (default "free")
- Tier derived from `is_pro`/`is_elite` booleans for backward compatibility
- Live trading blocked for free users (HTTP 403)
- Leaderboard limited to top 10 for free users
- Copy trading requires Pro/Elite
- 4 Stripe packages: pro_monthly, pro_yearly, elite_monthly, elite_yearly
- Payment flow updates user_tier on successful checkout

**Frontend Implementation:**
- `/pricing` page with Free/Pro/Elite cards, monthly/yearly toggle
- `TierBadge` component in user dropdown and navigation
- `UpgradeBanner` on dashboard for free users
- `PaperTradingBadge` for free users
- `FeatureLock` overlay for restricted features
- `InlineUpgradeCTA` for in-context upgrade prompts
- Trading mode toggle locked for free users (shows lock icon + "Pro" label)
- Leaderboard shows "Top 10 only" upgrade CTA for free users

---

### Latest Feature: Comprehensive Admin Dashboard (March 2026)

**Admin Dashboard Tabs:**
1. **Overview** - System stats, recent signups, recent payments, risk config
2. **Users** - Full user management with search, filters, actions (set plan, activate/deactivate, delete)
3. **Subscriptions** - Subscription management, Stripe sync, manual overrides
4. **Logs** - System logs, webhook logs, audit logs with filters
5. **Features** - Feature toggle switches by category (core, trading, notifications, payments, security, system)
6. **System Tools** - Clear cache, refresh data, rebuild indexes, cleanup tokens/logs, verify subscriptions
7. **Security** - Security overview, admin auth status, audit trail

**Backend API** (`/app/backend/routes/admin.py`):
- All routes protected with admin_key authentication
- Audit logging for all admin actions
- User CRUD operations
- Subscription management with Stripe sync
- Feature toggles persistence
- System maintenance tools

**Security Features:**
- Admin authentication required
- All actions logged to audit trail
- Session management with logout

---

### Previous Feature: Push Notifications for High-Confidence Signals (March 2026)

**Push Notification Features:**
- **High-Confidence Signal Alerts** - Pro/Elite users receive instant notifications for signals with 75%+ confidence
- **Notification Preferences** - Users can customize which alerts they receive
- **Alert Types** - Signal alerts, trade confirmations, price alerts, daily summary, weekly reports
- **Quiet Hours** - Configurable do-not-disturb time window
- **Test Notifications** - Verify push setup is working

**Backend Implementation:**
- `PushNotificationService` in `/app/backend/services/push_notifications.py`
- `notify_pro_users_high_confidence_signal()` - Sends to all Pro/Elite users
- API endpoints: `/api/notifications/config`, `/api/notifications/preferences`, `/api/notifications/test`
- Integration with signal generation triggers notifications automatically

**Frontend UI:**
- `NotificationSettings` component in dashboard
- Toggle switches for each notification type
- PRO badge indicating feature availability
- Quiet Hours time picker

**Note:** Push delivery is MOCKED (logged to console). Configure FCM/APNs/Expo keys for real delivery.

---

### Previous Feature: AI Signal Intelligence (March 2026)

**AI Signal Intelligence Features:**
- **GPT-5.2 Powered Explanations** - Each signal includes detailed AI-generated analysis
- **Trend Analysis** - Direction (bullish/bearish/neutral), strength, timeframe, description
- **Market Sentiment** - Overall sentiment score (-100 to +100), contributing factors, news impact
- **Key Technical Indicators** - RSI, MACD, Moving Averages, Volume analysis, Support/Resistance levels
- **Risk Assessment** - Risk level (low/medium/high), confidence factors
- **Actionable Insights** - Potential catalysts, suggested actions for traders

**Signal Intelligence Service:**
- `SignalIntelligenceService` in `/app/backend/services/signal_intelligence.py`
- GPT-5.2 integration via `emergentintegrations` library
- Fallback rule-based explanation generation when LLM unavailable
- Comprehensive JSON response with structured analysis

**Frontend UI Enhancement:**
- AI explanation summary displayed under each signal with Brain icon
- "View Full AI Analysis" expandable section
- Trend Analysis panel (direction, strength, timeframe)
- Market Sentiment panel (score bar, factors list)
- Key Indicators panel (RSI, MACD, MAs, Volume, S/R levels)
- Risk & Action panel (risk level badge, confidence factors, suggested action)
- Potential Catalysts tags

**API Response Fields Added to Signals:**
```json
{
  "explanation": "One-line summary",
  "reasoning": "Detailed reasoning paragraph",
  "trend_analysis": { "direction", "strength", "timeframe", "description" },
  "market_sentiment": { "overall", "score", "factors", "news_impact" },
  "key_indicators": { "rsi", "macd", "moving_averages", "volume", "support_resistance" },
  "risk_level": "low|medium|high",
  "confidence_factors": ["factor1", "factor2"],
  "potential_catalysts": ["catalyst1", "catalyst2"],
  "suggested_action": "Actionable trading advice"
}
```

---

### Phase 12: Advanced Performance Metrics (March 2026)

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

**Phase 14**: Mobile API v1 ✅
- Versioned API (`/api/v1/` prefix)
- Balanced optimization (pagination, field selection, ETag caching)
- Cross-platform JWT auth with `expires_in`
- Push notification hooks (Expo/FCM/APNs ready)
- Device registration and notification preferences
- Mobile-optimized trading execution

**Phase 15**: AI Signal Intelligence ✅
- GPT-5.2 powered signal explanations
- Trend analysis, market sentiment, key indicators
- Risk assessment and actionable insights
- Expandable UI for full AI analysis

**Phase 16**: Push Notifications ✅
- High-confidence signal alerts (75%+ threshold)
- Notification preferences management
- Quiet hours configuration
- Pro/Elite user targeting

**Phase 17**: Comprehensive Admin Dashboard ✅
- Full user management with actions
- Subscription management with Stripe sync
- Feature toggles by category
- System maintenance tools
- Audit logging for all admin actions
- Security overview

**Phase 18**: Stop-Loss/Take-Profit + Public Leaderboard ✅ NEW
- Stop-Loss orders trigger automatically at price threshold
- Take-Profit orders trigger automatically at price threshold
- Paper and Live trading support
- Order monitoring runs every 5 seconds
- Public Leaderboard with Daily/Weekly/Monthly/All-time tabs
- Sort by P&L, Win Rate, ROI, Total Trades
- Free users see top 10, Pro/Elite see full leaderboard
- Trader profiles with recent trades (Pro/Elite only)

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
- **Push Notifications**: 100% (22/22 tests)
- **AI Signal Intelligence**: 100% (16/16 tests)
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
- **AI**: OpenAI GPT-5.2 (via emergentintegrations)
- **Market Data**: Kraken API

---

### Next Action Items (P0)
1. ~~Execute sample trades to populate metrics demo data~~ DONE
2. ~~Implement email sending for auth verification/reset~~ DONE (Resend integration)
3. ~~Enhance AI Signal Intelligence~~ DONE (GPT-5.2 explanations)
4. ~~Add push notifications for high-confidence signals~~ DONE
5. ~~Brand Identity Integration ("Signal Intelligence System")~~ DONE
6. ~~Copy Trading System~~ DONE
7. ~~Free Tier System with Pricing~~ DONE
8. Deploy smart contract to Sepolia mainnet
9. Configure production Resend API key for live emails
10. Configure FCM/APNs/Expo for real push notifications

### Upcoming Tasks (P1)
- Biometric Authentication for Mobile (Face ID / Touch ID)
- Refactor App.js (~6000+ lines) and server.py (~6100+ lines) into smaller modules

### Future Tasks (P2-P3)
- Mobile App API Optimization (React Native)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia

---

### Known Limitations
- ~~Email sending is mocked (tokens logged to console)~~ Now uses Resend (requires API key)
- Push notifications are MOCKED (logged to console) - Configure FCM/APNs/Expo for real delivery
- Live trading is prepared but uses testnet
- Free tier users see 15-minute delayed signals (AI explanations visible once signals age)

---
Last Updated: March 22, 2026
