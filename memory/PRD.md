# AlphaAI — Product Requirements Document

## Original Problem Statement
Build "AlphaAI", a B2C/SaaS crypto trading signals platform optimized for conversion. Features include AI-powered trading signals, demo mode for unauthenticated users, admin analytics, referral system, and multi-tier subscription management.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + Framer Motion + Recharts
- **Backend**: FastAPI + Motor (Async MongoDB) + Background Tasks
- **Integrations**: OpenAI GPT-5.2 (Emergent LLM Key), Stripe, Resend
- **Structure**: Modular backend (routes/, services/, models/), React SPA with contexts/hooks

## What's Been Implemented

### Core Platform
- Landing page with animated brand reveal (splash screen)
- User auth (JWT-based login/register/forgot-password/verify-email)
- Wallet integration (MetaMask/Sepolia)
- Multi-tier subscription (Free/Pro/Elite) with Stripe checkout
- Live price ticker, AI trading signals (GPT-5.2 powered)
- Dashboard with trade execution, SL/TP orders, portfolio tracking

### Demo Mode System
- Global DemoModeContext with `?demo=true` URL activation
- DemoModeBanner showing simulated data notice
- Share Demo button generating shareable URLs
- useApiData hook for conditional real/mock data loading
- All dashboard pages wired to mock data in demo mode

### Dashboard Pages (8 pages wired)
- AI Agents, Event Agents, Marketplace, Strategy Lab
- Research Engine, Simulation, Analytics, Referrals

### Admin
- Admin panel with user management, signal generation, system config
- Admin Analytics dashboard with conversion funnels, referrer tracking
- Goal Tracker widget with K-factor and conversion targets

### Bug Fixes (Current Session — Feb 2026)
- **Fixed global UI interaction blocker**: All action buttons across 6 pages (Agents, Event Agents, Marketplace, Strategy Lab, Research, Simulation) had `disabled` prop making them unclickable with default cursor. Removed `disabled`, added active styling and toast "coming soon" handlers. Verified via testing agent (iteration_25, 19/19 passed).

## Prioritized Backlog

### P2 — Future Tasks
- Phase 3: Biometric Authentication for Mobile (Face ID / Touch ID)
- Phase 4: Mobile App API Optimization (React Native improvements)
- Webhook Delivery Testing via Stripe Dashboard
- Deploy AlphaAIManager.sol Smart Contract to Sepolia mainnet

## Credentials
- Standard user: demo_test2@my-alpha-ai.com / NewPass1234!
- Admin user: admin@my-alpha-ai.com / Admin1234! (admin_key: alphaai_admin_2026)
