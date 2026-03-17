# AlphaAI Fund Platform - Product Requirements Document

## Current Status: Phase 7 Complete - Project Export Ready

### Overview
AlphaAI is a decentralized AI-powered hedge fund platform that allows investors to deposit capital into a vault managed by autonomous AI trading agents. The platform includes a marketplace for external developers to launch their own trading agents.

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
- **100x Time Acceleration**: Simulate months of trading in seconds
- **Historical Data Loading**: Load BTC/ETH price data for backtesting
- **4 Specialized Trading Agents**:
  - Arbitrage Agent (25% allocation)
  - Momentum Agent (25% allocation)
  - Funding Rate Agent (25% allocation)
  - AI Research Lab (25% allocation, auto-generates strategies)
- **Stress Testing Scenarios**:
  - BTC 30% Drop (24h simulation)
  - ETH Flash Crash 50% (12h simulation)
  - Market Panic Sell 40% (6h simulation)
  - Liquidity Crisis 25% (48h simulation)
- **Real-time Agent Performance Tracking**
- **Export Results** (PDF, CSV, JSON)
- **Risk Management Integration**: Auto-stop at 5% drawdown, position reduction

**Phase 6 - Smart Contract & Live Data (March 2026)** ✅
- **AlphaAIManager.sol Contract**: Full Solidity smart contract for on-chain operations
- **MetaMask Integration**: Real wallet connectivity via ethers.js
- **Live Price Feed**: Real-time crypto prices from Kraken API
- **Event-Driven Agents**: Agents that react to smart contract events automatically
- **Contract Features**:
  - Investor deposit/withdraw functions
  - Strategy management (add, allocate, deallocate)
  - On-chain balance tracking
  - Emergency withdrawal (owner only)

**Phase 7 - Comprehensive Project Export (March 2026)** ✅ NEW
- **Full Technical Documentation PDF**: 43+ page PDF with complete system details
- **7-Point Export Structure**:
  1. Full project overview and concept
  2. All pages and website content
  3. AI agent logic, workflows, and automations
  4. Trading strategies, signal logic, and rules
  5. Backend structure and system architecture
  6. All prompts, configurations, and code
  7. End-to-end system workflow breakdown
- **API Endpoints**:
  - `GET /api/export/comprehensive-pdf` - Download the complete documentation
  - `POST /api/export/regenerate-pdf` - Regenerate the documentation

### API Endpoints Summary

```
Simulation:
- POST /api/simulation/start
- POST /api/simulation/stop
- POST /api/simulation/run-cycle
- POST /api/simulation/switch-mode?mode=X&live_capital=Y
- GET /api/simulation/stats
- GET /api/simulation/logs
- GET /api/simulation/agent-interactions

Reports:
- GET /api/reports/daily
- GET /api/reports/weekly
- GET /api/reports/history

Strategy Lab:
- GET /api/lab/strategies
- POST /api/lab/strategies/generate
- POST /api/lab/strategies/{id}/backtest
- POST /api/lab/strategies/{id}/sandbox
- POST /api/lab/strategies/{id}/deploy
- POST /api/lab/auto-deploy-top
- POST /api/strategies/add-batch?count=N

Risk:
- GET /api/risk/config
- PUT /api/risk/config
- GET /api/risk/alerts
- GET /api/risk/portfolio-status

Capital:
- GET /api/capital/allocations
- POST /api/capital/rebalance

Execution:
- GET /api/execution/stats
- POST /api/execution/simulate  (NEW)

Market:
- GET /api/market/top-coins  (NEW)
- GET /api/market/chart/{symbol}  (NEW)

Investors:
- POST /api/investors/register
- GET /api/investors/{wallet}
- POST /api/investors/deposit
- POST /api/investors/withdraw
- POST /api/investors/toggle-paper-trading/{wallet}  (NEW)

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
- POST /api/paper/reset/{wallet}

Analytics:
- GET /api/analytics/overview
- GET /api/analytics/strategies

AI:
- POST /api/ai/analyze

Marketplace:
- GET /api/marketplace/agents
- POST /api/marketplace/agents
```

### Test Results (March 2026)
- Backend: 93% pass rate
- Frontend: 95% pass rate
- Stress Testing: 100% (20 cycles, 10 strategy generations)
- Edge Cases: 100% handled correctly

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 with Shadcn/UI components
- **Database**: MongoDB (motor async driver)
- **AI Integration**: OpenAI GPT-5.2 (via Emergent LLM Key)
- **Market Data**: Kraken API (live prices)
- **Web3**: ethers.js (frontend), web3.py (backend)
- **Smart Contract**: Solidity 0.8.20+
- **PDF Generation**: ReportLab

### Next Action Items (P0)
1. Deploy AlphaAIManager.sol smart contract to Sepolia testnet
2. Implement JWT-based user authentication
3. Integrate with real DEX (Uniswap V3) for live trade execution
4. Implement real blockchain event listeners (Web3.py subscriptions)

### Future Tasks (P1-P3)
- Security audit of smart contract before mainnet
- WebSocket real-time updates (replace HTTP polling)
- Email notifications for alerts and reports
- Public leaderboard and referral system
- Mobile optimization and responsive design overhaul
- Fiat on-ramp integration (MoonPay)

### Known Limitations
- Trading is currently simulated (paper trading mode)
- Smart contract interactions are simulated until contract is deployed
- User authentication not implemented
- Real DEX execution not integrated

### Files Structure
```
/app/
├── backend/
│   ├── server.py                    # Main FastAPI app (~3,400 lines)
│   ├── generate_comprehensive_report.py  # PDF export generator
│   ├── contracts/AlphaAIManager.sol # Smart contract
│   ├── data/                        # Historical CSV data
│   └── reports/                     # Generated PDF reports
├── frontend/
│   └── src/App.js                   # Main React app (~3,100 lines)
└── memory/
    └── PRD.md                       # This document
```
