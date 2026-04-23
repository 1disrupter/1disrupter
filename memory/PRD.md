# Vibe2Nite — PRD

## Problem Statement
Production-ready FastAPI backend for a nightlife app ("Vibe2Nite") that returns real-time nightlife recommendations via a weighted Vibe Score, with brand styling applied consistently across API docs and admin-facing surfaces.

## Architecture (2026-04-23 rewrite)
- **FastAPI 0.115** + **SQLAlchemy 2.0** + **Alembic** + **PostgreSQL 15**
- Postgres runs under supervisor (program `postgresql`) on 127.0.0.1:5432
- Modular layout: `app/core`, `app/models`, `app/schemas`, `app/services`, `app/routers`, `app/static`
- All HTTP paths prefixed with `/api` (K8s ingress requirement)
- Branded Swagger UI at `/api/docs` with custom CSS matching the promo palette

## Brand System
| Token | Hex |
|---|---|
| Neon Purple (primary) | `#A260FF` |
| Electric Violet | `#8A49FF` |
| Electric Pink | `#FF3BA7` |
| Soft Lavender | `#C9B6FF` |
| Teal / Aqua | `#40E0FF` |
| Warm Amber | `#FFB347` |
| Midnight | `#05020D` |
| Card | `#11071F` |

Fonts: Bebas Neue (display) + Space Grotesk (body). Logo: white `VIBE`, gradient `2` (purple→pink), white `NITE`.

## Core Requirements (static)
1. `GET /api/vibes/top?lat&lng&radius_km=50` → `{ best_overall, live_music, hidden_gem }`
2. `POST /api/feedback` → body `{ venue_id, vote: "busy"|"dead"|"good" }`
3. Weighted vibe score (0–10, capped): 0.25·manual + 0.25·social + 0.25·votes + 0.15·time + 0.10·boost
4. Crowd bands: ≥8 busy · ≥5 medium · <5 dead
5. Top-3 selection: highest / best live_music (fallback to best_overall) / lowest

## Implemented (2026-04-23)
- [x] FastAPI app factory + modular backend
- [x] Postgres via supervisor; Alembic initial migration applied
- [x] SQLAlchemy models: `venues`, `vibes`, `feedback_log` (audit)
- [x] `GET /api/health`, `GET /api/vibes/top`, `POST /api/feedback`
- [x] Admin: `GET/POST /api/admin/venues`, `PATCH /api/admin/venues/{id}/signals`
- [x] Haversine radius filter + live_music fallback logic
- [x] Seed script (`python -m app.seed`) with 12 NYC venues
- [x] Branded Swagger UI at `/api/docs` + CSS at `/api/static/vibe2nite.css`
- [x] README with architecture, routes, migration & smoke-test instructions
- [x] 19/19 backend pytest cases green (see `/app/backend/tests/backend_test.py`)

## Backlog (P1/P2)
- [ ] **Auth** on `/admin/*` routes (JWT or session); require admin role
- [ ] **Rate-limit** `/feedback` (per-IP or per-device fingerprint)
- [ ] **DELETE /api/admin/venues/{id}** (for teardown/admin ops)
- [ ] Real **social-signal ingestion** (Instagram/TikTok velocity)
- [ ] Time-prediction ML model to replace static `time_prediction` signal
- [ ] PostGIS `2dsphere`/GIST index for geo at scale
- [ ] WebSocket "Vibe Pulse" — push score changes live
- [ ] Harden CORS (restrict origins before prod)
- [ ] Frontend (map + vibe cards) matching the promo UI
- [ ] Remove `Base.metadata.create_all` once Alembic is the sole source of truth

## Next Tasks
1. Decide on auth strategy for `/admin/*`
2. Add rate-limit middleware to `/feedback`
3. Build mobile-first frontend matching promo mockups
