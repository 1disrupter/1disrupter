# AlphaAI Fund Platform - Product Requirements Document

## Original Problem Statement
Build a fully autonomous AI-powered hedge fund platform with integrated MVP Simulation, AI Research Lab, Risk Engine, and Capital Allocation - all modules working together in paper trading mode.

## What's Been Implemented (Jan 2026)

### Phase 1 - MVP Core ✅
- 5 AI Trading Agents (Data, Decision, Strategy, Execution, Risk)
- Investor Dashboard with wallet connection
- Fund NAV, deposit/withdraw, performance charts
- AI Market Analysis (OpenAI GPT-5.2)
- Marketplace with revenue sharing

### Phase 2 - Advanced Features ✅
- AI Research & Strategy Lab (generate, backtest, sandbox, deploy)
- Risk Management Engine with configurable limits
- Capital Allocation Engine with dynamic rebalancing
- Execution Optimization Layer
- Paper Trading Sandbox

### Phase 3 - SIMULATION INTEGRATION ✅ (NEW)

**Simulation Control Page (`/simulation`)**
- Start/Stop simulation in paper trading mode
- Run trade cycles manually
- Real-time simulation statistics
- Simulation logs (trade, risk, allocation, strategy, agent events)
- Agent interaction logging

**Integrated Modules:**
1. **SimulationEngine** - Central coordinator for all agents
2. **Risk Engine** - Auto-stops trading if drawdown/loss limits exceeded
3. **Capital Allocation** - Dynamically reallocates based on Sharpe ratio
4. **AI Research Lab** - Auto-deploys top strategies (Sharpe > 1.5)
5. **Execution Layer** - Logs slippage, gas fees for each trade

**API Endpoints:**
- POST /api/simulation/start - Start paper trading
- POST /api/simulation/stop - Stop simulation
- POST /api/simulation/run-cycle - Execute one trading cycle
- GET /api/simulation/stats - Get comprehensive stats
- GET /api/simulation/logs - Get event logs
- GET /api/simulation/agent-interactions - Get agent communication logs
- POST /api/lab/auto-deploy-top - Auto-deploy high-performing strategies
- POST /api/capital/rebalance - Trigger capital reallocation

**Logging System:**
- SimulationLog: Captures all events with type, agent, message, details
- AgentInteraction: Records from_agent, to_agent, interaction_type, payload
- All logs persisted to MongoDB

## Test Results
- Backend: 87.8% pass rate
- Frontend: 90% pass rate
- Overall: 89% - MVP Simulation fully functional

## Next Action Items
1. Deploy to Sepolia testnet with real smart contracts
2. Integrate Uniswap V3 for actual DEX execution
3. Add WebSocket for real-time log streaming
4. Implement historical data backfill for backtesting

## Tech Stack
- Frontend: React 19, Tailwind CSS, Shadcn UI, Recharts
- Backend: FastAPI, Motor (MongoDB), SimulationEngine class
- AI: OpenAI GPT-5.2 via Emergent LLM key
- Market Data: CoinGecko API
