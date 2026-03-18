# AlphaAI Fund Platform - Product Requirements Document

## Current Status: Phase 8 Complete - High-Conversion Dashboard

### Overview
AlphaAI is a decentralized AI-powered hedge fund platform repositioned as a B2C/SaaS tool for "AI crypto signals + automated trading insights". The platform allows users to view AI-generated trading signals, track performance, and access advanced features via a Pro subscription.

**Copyright © 2026 Martin Maughan. All rights reserved. AlphaAI Platform.**

### All Implemented Features

**Phase 1 - MVP Core** ✅
- 5 AI Trading Agents (DataCollector, Decision, Strategy, Execution, Risk)
- Investor Dashboard with wallet connection
- Fund NAV, deposit/withdraw functionality
- AI Market Analysis (GPT-5.2 via Emergent LLM Key)
- Marketplace with 90/10 revenue sharing

**Phase 2 - Advanced Features** ✅
- AI Research & Strategy Lab
- Risk Management Engine (drawdown, loss limits, position sizes)
- Capital Allocation Engine (dynamic allocation to top performers)
- Execution Optimization Layer (slippage, gas optimization)
- Paper Trading Sandbox

**Phase 3 - Simulation Integration** ✅
- Simulation Control Page
- Trade cycle execution
- Comprehensive logging
- Agent interaction tracking

**Phase 4 - Reports & Live Mode** ✅
- Daily Performance Reports
- Weekly Performance Reports
- Mode Switching (Paper → Testnet → Live)
- Batch Strategy Generation
- New Agent Addition

**Phase 5 - Enhanced Simulation (March 2026)** ✅
- 100x Time Acceleration
- Historical Data Loading for backtesting
- 4 Specialized Trading Agents
- Stress Testing Scenarios
- Real-time Agent Performance Tracking
- Export Results (PDF, CSV, JSON)
- Risk Management Integration

**Phase 6 - Smart Contract & Live Data (March 2026)** ✅
- AlphaAIManager.sol Contract
- MetaMask Integration via ethers.js
- Live Price Feed from Kraken API
- Event-Driven Agents

**Phase 7 - Marketing Assets (March 2026)** ✅
- Full Technical Documentation PDF (43+ pages)
- AI-Powered Image Generation (Gemini Nano Banana)
- AI-Powered Video Generation (Sora 2)
- AI Voiceover Generation (OpenAI TTS)
- High-Converting Viral Ads (9:16 format for TikTok/Reels)

**Phase 8 - High-Conversion Dashboard (March 2026)** ✅ NEW
- **Conversion-Focused Dashboard Redesign**:
  - Demo Mode (try without wallet)
  - Demo Mode Banner (purple)
  - Delayed Signals Warning (yellow, 15 min delay)
  - Today's AI Signals (BTC, ETH, SOL with live prices)
  - Performance Section (+12.4% return, 68% win rate, etc.)
  - AI Market Summary
  - Upgrade CTA with "Unlock Live Signals" ($29/month)
  - Locked Pro Features Preview (Real-Time Alerts, Advanced Analytics)
  - 2-Minute Upgrade Popup Modal
  - Show/Hide Advanced Options toggle
- **Live Price Integration**: Real-time prices from Kraken API
- **Testing**: 100% pass rate (14/14 UI elements, 12/12 API tests)

### API Endpoints Summary

```
Dashboard & Prices:
- GET /api/live-prices (alias for market/live-prices)
- GET /api/market/live-prices

Simulation:
- POST /api/simulation/start
- POST /api/simulation/stop
- POST /api/simulation/run-cycle
- POST /api/simulation/switch-mode
- GET /api/simulation/stats
- GET /api/simulation/logs
- GET /api/simulation/agent-interactions

Reports:
- GET /api/reports/daily
- GET /api/reports/weekly
- GET /api/reports/history
- GET /api/report/download (PDF)

Strategy Lab:
- GET /api/lab/strategies
- POST /api/lab/strategies/generate
- POST /api/lab/strategies/{id}/backtest
- POST /api/lab/strategies/{id}/sandbox
- POST /api/lab/strategies/{id}/deploy
- POST /api/lab/auto-deploy-top

Risk:
- GET /api/risk/config
- PUT /api/risk/config
- GET /api/risk/alerts
- GET /api/risk/portfolio-status

Capital:
- GET /api/capital/allocations
- POST /api/capital/rebalance

Investors:
- POST /api/investors/register
- GET /api/investors/{wallet}
- POST /api/investors/deposit
- POST /api/investors/withdraw

Fund:
- GET /api/fund/stats
- GET /api/fund/allocation
- GET /api/fund/performance-history

Agents:
- GET /api/agents
- POST /api/agents/add

Trading:
- GET /api/trades
- POST /api/paper/trade
- GET /api/paper/portfolio/{wallet}

Marketing Assets:
- GET /api/marketing/image/{filename}
- GET /api/marketing/video/{filename}
- GET /api/marketing/ads-v2/preview
- GET /api/marketing/preview
```

### Test Results (March 2026)
- Backend: 100% pass rate (12/12 API tests)
- Frontend: 100% pass rate (14/14 UI elements verified)
- Dashboard Elements Verified:
  - Demo Mode button and banner
  - Delayed signals warning
  - AI Signals section with live prices
  - Performance metrics
  - AI Market Summary
  - Upgrade CTA card
  - Locked Pro features
  - Upgrade popup modal
  - Advanced options toggle

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 with Shadcn/UI components
- **Database**: MongoDB (motor async driver)
- **AI Integration**: OpenAI GPT-5.2, Sora 2, TTS (via Emergent LLM Key)
- **Image Generation**: Gemini Nano Banana (via Emergent LLM Key)
- **Market Data**: Kraken API (live prices)
- **Web3**: ethers.js (frontend), web3.py (backend)
- **Smart Contract**: Solidity 0.8.20+
- **PDF Generation**: ReportLab
- **Video Processing**: ffmpeg

### Next Action Items (P0)
1. Deploy AlphaAIManager.sol smart contract to Sepolia testnet
2. Implement JWT-based user authentication
3. Integrate with real DEX (Uniswap V3) for live trade execution
4. Implement real blockchain event listeners (Web3.py subscriptions)
5. Add Stripe integration for Pro subscription payments

### Future Tasks (P1-P3)
- Security audit of smart contract before mainnet
- WebSocket real-time updates (replace HTTP polling)
- Email notifications for alerts and reports
- Public leaderboard and referral system
- Mobile optimization and responsive design overhaul
- Fiat on-ramp integration (MoonPay)

### Refactoring Needed (Technical Debt)
- Extract React components from App.js (3200+ lines) into separate files
- Break down server.py (3900+ lines) into FastAPI routers
- Created but not integrated:
  - `/app/frontend/src/contexts/WalletContext.jsx`
  - `/app/frontend/src/pages/Dashboard.jsx`

### Known Limitations
- Trading is currently simulated (paper trading mode)
- Smart contract interactions are simulated until contract is deployed
- User authentication not implemented (wallet-based only)
- Real DEX execution not integrated
- Pro subscription payment not integrated

### Files Structure
```
/app/
├── backend/
│   ├── server.py                    # Main FastAPI app (~3,900 lines)
│   ├── contracts/AlphaAIManager.sol # Smart contract
│   ├── data/                        # Historical CSV data
│   ├── reports/                     # Generated PDF reports
│   ├── marketing_assets/            # Marketing images, videos, ads
│   └── tests/                       # Backend tests
├── frontend/
│   └── src/
│       ├── App.js                   # Main React app (~3,200 lines)
│       ├── contexts/WalletContext.jsx  # Extracted wallet context (new)
│       └── pages/Dashboard.jsx      # Extracted dashboard (new)
└── memory/
    └── PRD.md                       # This document
```

### 3rd Party Integrations
- **Kraken API**: Live cryptocurrency price data
- **OpenAI GPT-5.2**: AI market analysis (via Emergent LLM Key)
- **OpenAI Sora 2**: Video generation (via Emergent LLM Key)
- **OpenAI TTS**: Text-to-speech voiceover (via Emergent LLM Key)
- **Gemini Nano Banana**: Image generation (via Emergent LLM Key)
- **ethers.js**: Frontend MetaMask integration
- **web3.py**: Backend smart contract interaction

---
Last Updated: March 18, 2026
