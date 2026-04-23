# Vibe2Nite — PRD

## Problem Statement
Production-ready FastAPI backend for a nightlife app ("Vibe2Nite") that returns real-time nightlife recommendations based on a weighted "Vibe Score".

## Architecture
- **Stack:** FastAPI + MongoDB (motor async driver)
- **Routing:** All endpoints prefixed with `/api` (Kubernetes ingress requirement)
- **Storage:** Two MongoDB collections — `venues`, `vibes` (1:1 linked by `venue_id`)
- **Seed:** 10 sample NYC venues auto-seeded on startup if DB is empty

## Core Requirements (static)
1. `GET /api/vibes/top?lat&lng` → `{ best_overall, live_music, hidden_gem }`
2. `POST /api/feedback` → body `{ venue_id, vote: "busy"|"dead"|"good" }`
3. Weighted vibe score:
   - manual_score 0.25 + social_activity 0.25 + user_votes 0.25 + time_prediction 0.15 + venue_boost 0.10 (capped at 10)
4. Crowd bands: ≥8 busy · ≥5 medium · <5 dead
5. Top-3 logic: highest = best_overall · best live_music (fallback to best_overall) · lowest = hidden_gem

## Implemented (2026-04-23)
- [x] `GET /api/health` — service ping
- [x] `GET /api/vibes/top` with haversine radius filter (default 50km, configurable via `radius_km`)
- [x] `POST /api/feedback` — mutates `user_votes` signal (+1 busy / +0.5 good / −1 dead), recomputes score & crowd
- [x] `GET /api/venues` — helper to list all seeded venues with vibes
- [x] Pydantic validation (category, vote, lat/lng ranges)
- [x] Mongo unique indexes on `venues.id` and `vibes.venue_id`
- [x] UUID ids (no ObjectId leakage), `_id` excluded from all projections
- [x] CORS enabled (permissive, suitable for dev)

## Backlog (P1/P2)
- [ ] Real social-signal ingestion (Instagram/TikTok hashtag activity)
- [ ] Time-of-day prediction model (replace static `time_prediction` signal)
- [ ] Auth for feedback (rate limit / one vote per user per hour)
- [ ] Geospatial index (2dsphere) for production-scale radius queries
- [ ] Admin CRUD for venues
- [ ] Frontend (map view, vibe cards, live updates)

## Next Tasks
1. Decide on social-signal source & integrate
2. Add frontend if desired (React map + vibe cards)
3. Add auth layer before exposing feedback publicly
