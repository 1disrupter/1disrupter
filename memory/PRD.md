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

---

## Iteration 3 — Signal Engine (2026-04-23)

### Implemented
- [x] New ORM model `VenueSignals` (1:1 with Venue) + Alembic migration
- [x] `app/services/signals/` package with 6 modules: `google_busyness`, `social_activity`, `event_signals`, `time_patterns`, `user_feedback_signal` (real — reads `FeedbackLog` in 120-min window), `signal_engine` (composer), `_common` (helpers)
- [x] `app/services/scheduler.py` — APScheduler `AsyncIOScheduler` running `refresh_all_signals` every 5 minutes (+ immediate run on startup); per-venue helper `refresh_venue_signals`
- [x] Extended `scoring.py` with `calculate_vibe_score_from_signals(signals, manual_score, venue_boost)` — original `compute_vibe_score` UNTOUCHED
- [x] Scheduler wired into FastAPI `@app.on_event("startup"/"shutdown")`
- [x] `GET /api/admin/venues` now returns `external_signals` per item (all 5 scores + updated_at)
- [x] New endpoint `POST /api/admin/signals/refresh` for on-demand refresh
- [x] `POST /api/feedback` invokes `refresh_venue_signals` post-commit so response.new_vibe_score matches the published value (fixes iteration-3 desync)
- [x] Admin UI: `ExternalSignalsPanel` in Inspector modal (5 coloured progress bars), "Refresh signals" header button
- [x] Tests: 32/32 backend pass (iteration_4.json)

### Remaining backlog additions (P2)
- [ ] Mirror or deprecate `vibe.signals.user_votes` in `/admin/venues` (stale legacy mirror)
- [ ] Replace `asyncio.run` hack in `apply_feedback` with proper async route
- [ ] Config-drive `user_feedback_signal.WINDOW_MIN`
- [ ] Real external-API integration per signal module (Google Popular Times, IG/TikTok velocity, event providers)

---

## Iteration 5 — Vibes Extras (2026-04-23)

### Implemented (purely additive — no existing code modified)
- [x] `GET /api/vibes/directions?venue_id&user_lat&user_lng` — walking ETA, distance, URL-encoded Google Maps deeplink (`provider=stub` until `GOOGLE_MAPS_API_KEY` set)
- [x] `GET /api/vibes/heatmap` (optional `?categories=`) — 0–10 heat score = 0.4·google + 0.3·social + 0.2·votes + 0.1·events
- [x] `GET /api/vibes/live-music` (optional `?include_all=true`) — flagged when `category=live_music` + `event_score≥3` OR `event_score≥6.5`; confidence ∈ [0,1]
- [x] `GET /api/vibes/tourist-flags` — `tourist_trap` / `local_gem` / `neutral` with buckets + per-venue reason
- [x] `GET /api/vibes/forecast` (optional `?venue_id`) — smooth cosine hour-curve + day boost → `rising/peaking/falling/steady`
- [x] `GET /api/vibes/top3` — filter by `vibe`, optional distance penalty (0.05/km), `avoid_tourist_traps` (exclusion) or soft −2 penalty
- [x] Admin Inspector modal shows new **Venue Intelligence** panel with Forecast / Crowd type / Live music cards
- [x] `api.js` adds `getForecast`, `getTouristFlags`, `getLiveMusic`, `getHeatmap`
- [x] Tests: **56/56 backend pytest pass**, frontend cross-check pass (iteration_5.json)

### Remaining backlog additions (P2)
- [ ] Plug in real Google Places Distance Matrix when `GOOGLE_MAPS_API_KEY` provided
- [ ] Replace stubbed social/event signals with real providers (IG velocity, Bandsintown, Songkick)
- [ ] Persist vibe-score history for true trajectory-based forecasts (instead of time-curve heuristic)
- [ ] Heatmap pagination for large cities
- [ ] Surface heatmap and live-music on the consumer `/` page (currently admin-only visibility)
