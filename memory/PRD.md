# Vibe2Nite — PRD

## Problem Statement
Real-time nightlife recommendation engine (Vibe2Nite). Neon-brand web experience consisting of:
- Postgres/FastAPI backend with weighted Vibe Score
- Consumer home UI (Top 3 tonight) matching the promo image
- Full design system / brand kit page (in-app reference)
- Admin dashboard (venues, signals, overview charts)
- Exact Tailwind theme using the supplied palette

## Architecture
- **Backend**: FastAPI 0.115 + SQLAlchemy 2.0 + Alembic + PostgreSQL 15 (supervisor-managed)
- **Frontend**: React 18 + CRA/craco + Tailwind 3 + react-router-dom + framer-motion + Recharts + lucide-react
- Modular layering, all API paths under `/api`
- Admin auth: client-side local password (MVP) — replace before prod

## Brand System (locked, do not change)
| Token | Hex |
|---|---|
| Primary / Neon Purple | `#8A2BE2` |
| Primary / Glow Purple | `#B15CFF` |
| Accent / Electric Pink | `#FF2EC4` |
| Accent / Magenta | `#FF4EDB` |
| Glow / Aqua | `#00F5FF` |
| Glow / Teal | `#00D1C7` |
| Background / Midnight | `#0A0A12` |
| Background / Deep | `#05050A` |
| Status / Busy (Amber) | `#FF9A1F` |
| Status / Medium (Lavender) | `#C7A7FF` |
| Status / Dead (Grey) | `#6B6B6B` |

Fonts: **Bebas Neue** (display) + **Outfit / Inter** (body).
Shadows: `neonPurple`, `neonPink`, `neonAqua`, `neonAmber`, `neonTeal`, `softPurple`, `hardEdge`.
Spacing scale: 4 / 8 / 12 / 16 / 24 / 32 / 48.
Radii: rounded-xl (12) / xl2 (18) / xl3 (22).

## Implemented
### Iteration 1 (backend)
- [x] FastAPI factory, Alembic migrations applied, Postgres seeded with 12 NYC venues
- [x] `GET /api/vibes/top` + `POST /api/feedback` + `/api/admin/*` + `/api/health`
- [x] Branded Swagger UI at `GET /api/docs`
- [x] 19/19 pytest backend suite green

### Iteration 2 (frontend)
- [x] React app with Tailwind using the exact brand palette
- [x] `/` consumer page — promo-matched hero, 3 VenueHeroCards (best_overall/live_music/hidden_gem) with banner chips, score badges, status + category chips, colour-matched Go buttons, mobile bottom-tabs, quick-vote bar wired to `/api/feedback`
- [x] `/brand` full design system — colour swatches (click-to-copy hex), typography showcase, 3 logo variants, 7 effect/glow tokens, spacing scale, all Buttons/Chips/BannerChips/StatusIndicators/MapPins/VibeScoreBadges, Cards (hero + list + skeleton), Inputs/Search/Select/Slider, Modal, Toasts (success/error/info), Empty/Error/Loading states, Pagination, Tailwind config code block
- [x] `/admin` console — login (vibe2nite/nightowl), sidebar nav, Overview with 4 Recharts panels (top scores bar, avg signals line, category mix donut, crowd distribution bar) + 4 stat tiles, Venues table with category chips + Inspect, Signal Inspector modal with 4 sliders and live-computed score preview, Add Venue modal, Signals log panel, logout
- [x] ToastProvider, Suspense+lazy, route-split
- [x] 14/14 frontend Playwright flows green (see iteration_2.json)

## Backlog (P1/P2)
- [ ] **Backend auth** on `/admin/*` (JWT) + rate-limit `/feedback` (per-IP)
- [ ] `DELETE /api/admin/venues/{id}` for clean teardown
- [ ] Replace client-side admin creds with real backend login
- [ ] Share Vibe Score formula between JS + Python (single source of truth)
- [ ] Client-side lat/lng bounds validation in AddVenueModal
- [ ] Pagination in venues table (> 50 rows)
- [ ] Real social-activity ingestion (Instagram/TikTok)
- [ ] Time-prediction ML model
- [ ] PostGIS 2dsphere index
- [ ] WebSocket "Vibe Pulse" for live score updates
- [ ] React Native / Expo app (deferred this round — components are RN-portable)
- [ ] React Router v7 future flags to silence console warnings

## Next Tasks
1. Wire real auth + rate-limit
2. Ship RN/Expo scaffold (locally runnable)
3. Social-signal ingestion pipeline
