# AlphaAI Fund Platform - Product Requirements Document

## Original Problem Statement
Build a fully autonomous AI-powered hedge fund platform where investors deposit capital into a pooled vault managed by AI agents. The system continuously generates, tests, ranks, and deploys trading strategies while providing dashboards, smart contracts, and a marketplace for third-party AI agents.

## User Personas
1. **Crypto Investor** - Passive income through AI-managed trading
2. **DeFi Enthusiast** - Automated yield strategies
3. **AI Developer** - Monetize trading algorithms via marketplace
4. **Fund Administrator** - Oversight of operations and risk

## Core Requirements (Static)
- Multi-agent AI trading system
- Investor wallet integration & portfolio management
- AI Strategy Lab (generation, backtesting, sandbox, deployment)
- Risk Management Engine
- Capital Allocation Engine
- Execution Optimization Layer
- Paper Trading Sandbox
- AI Agent Marketplace
- Admin dashboard with risk controls

## What's Been Implemented (Jan 2026)

### Phase 1 - MVP Core
- ✅ 5 AI Trading Agents (Data, Decision, Strategy, Execution, Risk)
- ✅ Investor Dashboard with wallet connection
- ✅ Fund NAV, deposit/withdraw, performance charts
- ✅ AI Market Analysis (OpenAI GPT-5.2)
- ✅ CoinGecko market data integration
- ✅ Marketplace with revenue sharing

### Phase 2 - Advanced Features (NEW)
- ✅ **AI Research & Strategy Lab**
  - StrategyGeneratorAgent - AI creates new trading strategies
  - BacktestingAgent - Tests on historical data
  - SandboxValidationAgent - Paper trading validation
  - StrategyRankingAgent - Ranks by Sharpe/return/drawdown
  - LiveDeploymentAgent - Deploys top strategies
  - Strategy Pipeline visualization (Generated → Backtested → Sandbox → Live)
  
- ✅ **Risk Management Engine**
  - Configurable max drawdown, position size, daily loss limits
  - Real-time risk status monitoring
  - Auto stop-loss enforcement
  - Risk alert system
  
- ✅ **Capital Allocation Engine**
  - Performance-based allocation
  - Dynamic rebalancing
  - Strategy weighting by Sharpe ratio
  
- ✅ **Execution Optimization Layer**
  - Order splitting simulation
  - Slippage tracking
  - Gas fee optimization
  - DEX routing suggestions
  
- ✅ **Paper Trading Sandbox**
  - $10,000 virtual starting balance
  - Real-time P&L tracking
  - Trade execution simulation
  - Portfolio reset capability

### Tech Stack
- Frontend: React 19, Tailwind CSS, Shadcn UI, Recharts, Framer Motion
- Backend: FastAPI, Motor (async MongoDB)
- AI: OpenAI GPT-5.2 via Emergent LLM key
- Market Data: CoinGecko API

## Prioritized Backlog

### P0 (Critical)
- [ ] Smart contract deployment to Sepolia testnet
- [ ] Real on-chain transactions (deposit/withdraw)
- [ ] ERC-20 ShareToken implementation

### P1 (High)
- [ ] DEX integration (Uniswap V3) for real execution
- [ ] Persistent historical data storage
- [ ] User authentication with sessions
- [ ] WebSocket real-time updates

### P2 (Medium)
- [ ] Actual backtesting with historical price data
- [ ] ML-based strategy parameter optimization
- [ ] Developer sandbox for agent testing
- [ ] Performance leaderboards

### P3 (Nice to have)
- [ ] Mobile responsive improvements
- [ ] Multi-chain support (Polygon, Arbitrum)
- [ ] Governance token & DAO voting
- [ ] Social features

## Next Tasks
1. Create Solidity smart contracts (FundVault, ShareToken, ProfitDistributor)
2. Deploy to Sepolia testnet
3. Integrate real DEX trading via Uniswap V3
4. Implement WebSocket for real-time strategy updates
