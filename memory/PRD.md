# AlphaAI Fund Platform - Product Requirements Document

## Original Problem Statement
Build a decentralized AI-powered hedge fund platform where investors deposit capital into a vault that autonomous AI trading agents manage. The platform also allows external developers to launch their own trading AI agents and earn revenue through a marketplace.

## User Personas
1. **Crypto Investor** - Wants passive income through AI-managed trading
2. **DeFi Enthusiast** - Interested in automated yield strategies
3. **AI Developer** - Wants to monetize trading algorithms through marketplace
4. **Fund Administrator** - Needs oversight of trading operations and risk

## Core Requirements (Static)
- Multi-agent AI trading system
- Investor wallet integration
- Deposit/Withdraw functionality
- Fund NAV tracking
- Portfolio allocation management
- AI Agent Marketplace
- Admin risk monitoring dashboard
- Real-time analytics

## What's Been Implemented (Jan 2026)

### Backend (FastAPI + MongoDB)
- ✅ Investor registration and management APIs
- ✅ Deposit/Withdraw functionality with share calculation
- ✅ Fund stats, NAV, allocation endpoints
- ✅ 5 AI Trading Agents (Data, Decision, Strategy, Execution, Risk)
- ✅ AI Market Analysis using OpenAI GPT-5.2 (Emergent LLM key)
- ✅ CoinGecko market data integration
- ✅ Trade logging system
- ✅ Risk alerts management
- ✅ Marketplace agents CRUD
- ✅ Analytics/performance metrics

### Frontend (React + Tailwind + Shadcn UI)
- ✅ Landing page with hero, stats, features
- ✅ Glassmorphism navigation
- ✅ Wallet connection (MetaMask + Demo mode)
- ✅ Investor Dashboard with charts
- ✅ AI Agents page with analysis feature
- ✅ Marketplace with agent submission
- ✅ Analytics page with metrics
- ✅ Admin dashboard with alerts

### Design System
- ✅ Dark theme (Obsidian background)
- ✅ Outfit/Inter/JetBrains Mono fonts
- ✅ Electric Purple (#7B61FF) primary
- ✅ Neon Green (#00FF94) secondary
- ✅ Glassmorphism cards
- ✅ Responsive layout

## Prioritized Backlog

### P0 (Critical)
- [ ] Smart contract deployment (Solidity)
- [ ] Real wallet transactions on testnet
- [ ] On-chain share token (ERC-20)

### P1 (High)
- [ ] Real trading execution via DEX APIs
- [ ] Historical performance persistence
- [ ] User authentication/sessions
- [ ] Email notifications for alerts

### P2 (Medium)
- [ ] Backtesting simulation engine
- [ ] Paper trading mode
- [ ] Developer agent sandbox
- [ ] Social features (leaderboards)

### P3 (Nice to have)
- [ ] Mobile app (React Native)
- [ ] Multi-chain support
- [ ] Governance token
- [ ] DAO voting

## Technical Stack
- Frontend: React 19, Tailwind CSS, Shadcn UI, Recharts, Framer Motion
- Backend: FastAPI, Motor (async MongoDB)
- AI: OpenAI GPT-5.2 via Emergent LLM key
- Market Data: CoinGecko API
- Wallet: ethers.js, web3.js

## Next Tasks
1. Deploy FundVault smart contract to Sepolia testnet
2. Implement real USDC deposit/withdraw
3. Add investor authentication
4. Connect to DEX for real trade execution
