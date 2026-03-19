# AlphaAI Fund Platform - Product Requirements Document

## Current Status: Phase 9 Complete - Stripe Pro Subscription

### Overview
AlphaAI is a decentralized AI-powered hedge fund platform repositioned as a B2C/SaaS tool for "AI crypto signals + automated trading insights". Users can view AI-generated trading signals, track performance, and upgrade to Pro subscription ($29/month or $249/year) via Stripe Checkout.

**Copyright © 2026 Martin Maughan. All rights reserved. AlphaAI Platform.**

### All Implemented Features

**Phase 1-7** ✅ (See previous documentation)
- AI Trading Agents, Simulation, Reports, Smart Contracts, Marketing Assets

**Phase 8 - High-Conversion Dashboard (March 2026)** ✅
- Conversion-Focused Dashboard Redesign
- Demo Mode for wallet-free viewing
- Today's AI Signals with live Kraken prices
- Performance metrics, AI Summary
- Upgrade CTAs and locked Pro features preview
- 2-Minute Upgrade Popup Modal

**Phase 9 - Stripe Pro Subscription (March 2026)** ✅ NEW
- **Stripe Checkout Integration**:
  - Monthly Plan: $29/month
  - Yearly Plan: $249/year (Save $99 - 2 months FREE)
  - Secure checkout via Stripe hosted page
  - Payment status polling with auto Pro activation
  - Webhook support for payment events
- **Payment Endpoints**:
  - `POST /api/payments/checkout` - Create Stripe checkout session
  - `GET /api/payments/status/{session_id}` - Get payment status
  - `GET /api/payments/packages` - Get available packages
  - `GET /api/users/pro-status/{wallet}` - Check Pro status
  - `POST /api/webhook/stripe` - Handle Stripe webhooks
- **Database**: `payment_transactions` collection for tracking
- **Frontend Integration**:
  - Package selection UI (Monthly/Yearly toggle)
  - Dynamic "Upgrade Now" button text
  - Payment return handling with status polling
  - Pro status persistence

### API Endpoints Summary

```
Payments (NEW):
- POST /api/payments/checkout
- GET /api/payments/status/{session_id}
- GET /api/payments/packages
- GET /api/users/pro-status/{wallet_address}
- POST /api/webhook/stripe

Dashboard & Prices:
- GET /api/live-prices
- GET /api/market/live-prices

(See previous PRD for complete API list)
```

### Test Results (March 2026)
- **Stripe Backend**: 100% (10/10 tests passed)
- **Stripe Frontend**: 100% (17/17 UI elements verified)
- **Dashboard**: 100% (14/14 UI elements, 12/12 API tests)

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 with Shadcn/UI
- **Database**: MongoDB (motor async driver)
- **Payments**: Stripe Checkout (via emergentintegrations)
- **AI Integration**: OpenAI GPT-5.2, Sora 2, TTS, Gemini Nano Banana
- **Market Data**: Kraken API (live prices)
- **Web3**: ethers.js (frontend), web3.py (backend)

### Next Action Items (P0)
1. Deploy `AlphaAIManager.sol` to Sepolia testnet
2. Implement JWT-based user authentication
3. Add Pro feature unlocks (real-time signals, no delay)
4. Integrate real DEX (Uniswap V3) for live trades

### Future Tasks (P1-P3)
- Email notifications for payment receipts
- Subscription management (cancel, upgrade/downgrade)
- WebSocket real-time updates
- Public leaderboard and referral system
- Mobile optimization

### Known Limitations
- Trading is simulated (paper trading mode)
- Smart contract interactions are mocked
- User authentication is wallet-based only
- Pro features unlock UI changes only (real-time signals backend not yet differentiated)

### Files Structure
```
/app/
├── backend/
│   ├── server.py                    # Main FastAPI (~4200 lines, includes Stripe)
│   ├── contracts/AlphaAIManager.sol
│   ├── tests/test_stripe_payments.py  # NEW
│   └── marketing_assets/
├── frontend/
│   └── src/
│       ├── App.js                   # Main React (~3350 lines)
│       ├── contexts/WalletContext.jsx
│       └── pages/Dashboard.jsx
├── test_reports/
│   ├── iteration_6.json             # Dashboard tests
│   └── pytest/stripe_pytest_results.xml  # Stripe tests
└── memory/
    └── PRD.md
```

### 3rd Party Integrations
- **Stripe**: Payment processing (via emergentintegrations)
- **Kraken API**: Live cryptocurrency prices
- **OpenAI**: GPT-5.2, Sora 2, TTS (via Emergent LLM Key)
- **Gemini Nano Banana**: Image generation (via Emergent LLM Key)
- **ethers.js**: MetaMask integration
- **web3.py**: Smart contract interaction

---
Last Updated: March 18, 2026
