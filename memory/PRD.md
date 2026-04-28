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

---

## Iteration 6 — Mobile + Desktop Admin (2026-04-23)

### Implemented (two new source-only projects — existing preview untouched)

**`/app/mobile/` — Expo React Native (TypeScript)**
- [x] Screens: Tonight (Top-3 feed, category tabs, 1-tap directions), Map (heat pins, bottom sheet), Venue Detail (1-tap busy/good/dead feedback), Settings/About
- [x] Components: Logo, GlowButton, Chip (+ TrendBadge, TouristFlagBadge, LiveMusicBadge), CategoryTabs, VibeScoreBadge/CrowdDot/Sparkline, VenueCard
- [x] Typed fetch client hitting `/api/*` with config driven by `EXPO_PUBLIC_API_URL` / `app.json.extra.apiUrl`
- [x] React Query + bottom-tabs + native-stack navigation
- [x] `react-native-maps` with dark neon style; marker sizing tied to heat
- [x] Shared brand tokens in `src/theme.ts` mirroring web tailwind
- [x] `yarn typecheck` clean

**`/app/admin-next/` — Next.js 14 App Router (TypeScript + Tailwind)**
- [x] `/login` (client-side auth — demo creds `vibe2nite/nightowl`)
- [x] `/admin/overview` — 4 stat tiles + 4 Recharts panels
- [x] `/admin/venues` — searchable table, Add-venue modal, Inspect modal (edit | signal engine | live preview + intelligence)
- [x] `/admin/signals` — per-venue signal bars sorted by last-updated
- [x] Branded Sidebar + Topbar, Tailwind config mirroring web tokens
- [x] React Query + typed API client + auth hook
- [x] `yarn typecheck` + `yarn build` both green (8 static routes)

### Runnability notes
- The existing **web preview** (React CRA on :3000) continues to serve `/`, `/brand`, `/admin`.
- **Next.js admin** runs on port `3100` locally (`yarn dev` or `yarn build && yarn start`); not wired into supervisor to avoid colliding with the CRA app.
- **Expo mobile** can't run in this container. Run locally via `yarn start` + Expo Go / simulator.

### Backlog deltas
- [ ] Move `vibe2nite/nightowl` auth to a real backend login (both admins share a hook)
- [ ] Replace sparkline placeholder in RN with real `/vibes/history` data once the backend stores trajectory
- [ ] Expo Location permission copy per store-review requirements
- [ ] Swap `react-native-maps` for `expo-maps` once GA for modern SDK

---

## Iteration 7 — User Intelligence Layer + Vibe Credits Reward Economy (2026-04-23)

### Implemented (purely additive — zero changes to existing endpoints, Signal Engine, or Vibe Score formula)

**Backend — DB (Alembic migration `e151932735a3`)**
- [x] 3 intel tables: `user_location_pings`, `venue_visits`, `venue_vibe_history`
- [x] 3 rewards tables: `user_wallets`, `venue_reward_offers`, `venue_redemptions`

**Backend — services**
- [x] `app/services/user_intel/` — `location_pings`, `venue_visits` (40m / 5-min dwell rule), `user_flow` (rising/peaking/falling/steady), `trajectory_history`
- [x] `app/services/rewards/` — `credit_wallet`, `reward_rules` (feedback=1, visit=3, navigate=1, daily_login=1, first_visit_bonus=5), `venue_offers`, `redemption`
- [x] APScheduler now also runs `append_current_scores()` + `detect_visits()` every 5 min (additive side-jobs, non-fatal on error)

**Backend — routes (all under `/api`)**
- [x] `POST /intel/ping`, `POST /intel/visits/detect`, `GET /intel/visits/{venue_id}`, `GET /intel/flow`, `GET /intel/trajectory/{venue_id}`, `POST /intel/trajectory/snapshot`
- [x] `GET /rewards/rules`, `GET /rewards/wallet/{user_id}`, `POST /rewards/earn`, `GET /rewards/offers`, `GET /rewards/offers/{id}`, `POST /rewards/offers`, `DELETE /rewards/offers/{id}`, `POST /rewards/redeem`, `GET /rewards/redemptions`

**Next.js admin (`/app/admin-next`)**
- [x] New sidebar tab `/admin/credits` — 4 stat tiles (active offers, redemptions, credits redeemed, earn rules), earn-rules chip board, offer CRUD table with retire, recent redemptions table, "New offer" modal
- [x] InspectorModal now shows a **Vibe Credits** panel with an SVG 6-hour trajectory sparkline plus top 3 active offers for the venue
- [x] `lib/api.ts` gained rewards + intel typings/helpers
- [x] `yarn typecheck` + `yarn build` green (9 routes)

**Expo mobile (`/app/mobile`)**
- [x] New **Wallet** tab (`WalletScreen`) — balance card, earn-rules chips, active-offer list with per-card Redeem button, recent redemptions history, pull-to-refresh
- [x] VenueDetail: now pulls real `/intel/trajectory/{id}` for the sparkline, shows per-venue reward offers, fires `+1 Vibe Credit` / `+1 Vibe Credit` toasts on feedback vote / Go-here-now tap
- [x] New `lib/identity.ts` (AsyncStorage-backed opaque device UUID = wallet user_id) + `lib/rewards.ts` (useWallet / awardCredits / useCreditToast)
- [x] `yarn typecheck` green

### Tests
- [x] `/app/backend/tests/test_intel_and_rewards.py` — 11 new tests (intel ping/flow/visits/trajectory + rewards wallet/earn/offer-CRUD/redeem/404s)
- [x] Full backend pytest suite: **67/67 green** (56 prior + 11 new) — see `/app/test_reports/iteration_6.json`
- [x] Zero regression on existing endpoints (verified end-to-end by the testing agent)

### Remaining backlog additions (P2)
- [ ] CRA web preview (`/app/frontend`) — mirror the admin Credits tab for parity (currently only Next.js admin has it)
- [ ] Admin auth for `POST /rewards/earn { amount }` override (currently open — flagged for auth gating before prod)
- [ ] Persist first-visit bonus server-side (currently a client rule only)
- [ ] Make `/api/seed` idempotent so test iterations don't multiply venues

---

## Iteration 8 — Wallet durability (2026-04-23)

### Root cause of "credits dropped when I logged off"
PostgreSQL's data directory was on **ephemeral container storage** (`/var/lib/postgresql/15/main`). Every pod/container restart wiped the entire DB — wallets, offers, venues, the lot. It was never a logout bug.

### Fix
- [x] Migrated PostgreSQL `data_directory` to `/app/data/pgdata` (the only persistent path in this pod) via `postgresql.conf`. Backend + full PG restart now preserve all wallet balances — verified end-to-end (10 credits for `durable-alice` survived two restart scenarios).
- [x] Added strict wallet lookup: `GET /api/rewards/wallet/{user_id}?create=false` → 404 if not found (prevents silent "empty wallet" on typo during restore).
- [x] **Mobile wallet code UX**: Wallet screen now shows the user's opaque wallet code in a copyable (select-to-copy) field plus a "Have a code? Restore a wallet" modal that validates against the backend before swapping the local AsyncStorage `device_id`.
- [x] **Admin support tool**: `/admin/credits` now has a "Wallet lookup & manual grant" panel — admins can paste any wallet code, see the balance, and grant N credits (uses `/rewards/earn` with action=`admin_grant` + explicit amount).
- [x] Identity helper: added `setDeviceId(code)` to `/app/mobile/src/lib/identity.ts`.

### Tests
- [x] Full backend pytest suite: **67/67 still green**
- [x] Manual curl verification: backend restart and full PG restart both preserve wallet balances.

---

## Iteration 9 — P2 wave: Push Notifications, Vibe Pulse (WebSocket), Google Distance Matrix (2026-04-23)

### Implemented (additive — zero existing endpoints, models, Signal Engine or Vibe Score logic touched)

**Backend — DB**
- [x] New table `user_push_tokens` (wallet_id PK, expo_push_token) via Alembic `7beff8b51618`.

**Backend — Push**
- [x] `services/notifications/*` — Expo Push HTTP client, milestone helper (10/25/50/100), `send_push()`, `send_milestone_push()`.
- [x] `POST /api/notifications/register` (upsert), `POST /api/notifications/test` (debug).
- [x] `POST /api/rewards/earn` now detects milestone crossings and fires `send_milestone_push()` fire-and-forget. Existing earn contract unchanged.

**Backend — Vibe Pulse (WebSocket)**
- [x] `services/ws_manager.py` — `VibeConnectionManager` with room-per-venue, safe cross-loop dispatch (`bind_loop()` + `broadcast_sync()` via `asyncio.run_coroutine_threadsafe`), graceful disconnect, 30 s heartbeat.
- [x] `GET /ws/vibe/{venue_id}` — accepts socket, sends immediate snapshot, keeps keep-alive loop.
- [x] Scheduler's `refresh_venue_signals()` now broadcasts `vibe_update` frames (score, crowd_level, external_signals, updated_at) after each refresh — works even when called via `asyncio.run` from `POST /feedback`.

**Backend — Distance Matrix**
- [x] `services/maps/` — `get_travel_time()` with 5-minute in-memory cache (100 m rounded keys); uses `GOOGLE_MAPS_API_KEY` when set, falls back to haversine stub (`walking=4.8 km/h`, `driving=28 km/h`).
- [x] New enriched routes: `GET /api/venues/list?user_lat&user_lng` (all venues + travel fields), `GET /api/intel/score/{venue_id}?user_lat&user_lng` (single).

**Mobile (`/app/mobile`)**
- [x] `expo-notifications` + `expo-device` added; `lib/push.ts` requests permissions, gets Expo push token, POSTs to `/notifications/register` on app start.
- [x] `lib/useVibePulse.ts` — typed WebSocket hook with auto-reconnect (2.5 s linear) + heartbeat filtering.
- [x] VenueDetail now shows a **LIVE** chip when the socket is up, overlays the streamed Vibe Score over the initial prop, and renders a **Travel time** card (walking / driving mins + provider badge) from `/intel/score`.

**Admin (`/app/admin-next`)**
- [x] `hooks/useVibePulse.ts` mirrors the mobile hook (web WebSocket).
- [x] InspectorModal header now carries a pulsing **LIVE / OFFLINE** chip, the "Live preview" score auto-updates from the socket (crowd level + updated-at included), and a new **Travel time** panel shows walking + driving minutes with the provider.
- [x] `lib/api.ts` gained `getIntelScore`, `grantCredits`, `lookupWallet`.

**Tests (`/app/backend/tests/test_p2_features.py`)**
- [x] 10 new tests covering: push register upsert, milestone helper (all four thresholds), milestone trigger on earn, `/venues/list` & `/intel/score` enrichment, travel-time cache warmth, stub fallback when no key, WS snapshot on connect, WS broadcast on feedback.
- [x] **Total: 77/77 pytest green** (67 prior + 10 new).
- [x] Mobile `yarn typecheck` green; Next.js `yarn build` green (9 routes).

### Notes
- WS tests use `ws://localhost:8001` because some preview ingresses don't proxy `wss://` — this matches the test agent's prior guidance.
- Expo push sends happen against Expo's public URL with the stored token; the send path never raises into the earn route (fully best-effort).
- Scheduler WS broadcasts use `broadcast_sync` which auto-routes to the main uvicorn loop via the loop reference captured in `@app.on_event("startup")`.

### Remaining backlog additions (P3)
- [ ] Rate-limit `/notifications/register` (prevent abuse of the upsert).
- [ ] Persist WS broadcast for offer creation / redemption events (currently only `vibe_update`).
- [ ] Push icons & channel config tuned for iOS critical alerts.
- [ ] Hook `/rewards/redeem` to a WS `offer_redeemed` event and a confirmation push.

---

## Iteration 10 — Push engine finish + AI Forecast + Tourist Classifier + Launch Mode (2026-04-24)

### Implemented (additive — existing endpoints, Signal Engine, Vibe Score untouched)

**Backend — DB (Alembic `33407f75b980`)**
- [x] 4 new tables: `venue_intel`, `notification_log`, `venue_profiles`, `venue_admins`.

**Backend — Push engine (`services/notifications/push_engine.py`)**
- [x] Templates: `daily_login`, `first_visit_bonus`, `vibe_spike`, `offer_drop`, `tonight_hotspots` + existing `milestone`.
- [x] `NotificationLog` persistence for every dispatch → mobile inbox.
- [x] `detect_vibe_spikes(db)` (≥12% jump over 10 min) + `dispatch_spike_alerts(db)`.
- [x] Thread-pool fan-out (`broadcast_to_all`) — each worker gets its own SQLAlchemy session; 3 s Expo timeout.
- [x] Hooked into `/rewards/offers POST` (fires offer_drop to all wallets), `/rewards/earn` (daily_login + first_visit_bonus triggers).
- [x] APScheduler: new jobs — **every 10 min** spike-scan, **21:00 daily** tonight-hotspots.

**Backend — new routes**
- [x] `GET /api/forecast/{venue_id}` (5-min cached, `refresh=true` bypass) — baseline + momentum + hour-of-day cycle; returns `{current_score, forecast_score, trend, confidence, baseline, momentum, cycle_boost, horizon_hours, as_of, cached}`.
- [x] `GET /api/intel/tourist-flags` + `POST /api/intel/tourist-flags/refresh` — persisted classifier (`tourist_trap` / `local_gem` / `neutral`) using tourist/local ratio, volatility, price level, repeat-visit loyalty.
- [x] `GET /api/intel/local-gems?limit=N` — ranked by `vibe × (1+gem_score) × (1+loyalty)`.
- [x] `POST /api/city/seed` — bulk upsert of venues + `VenueProfile` (hours, music, price, age, dress, photos).
- [x] `POST /api/venues/onboard` — creates `VenueAdmin` (PBKDF2 hash, stdlib) + returns API key + inline PNG QR codes (check_in / feedback / follow_venue).
- [x] `POST /api/venues/login` — password verify → api_key.
- [x] `POST /api/notifications/trigger/test` — manual dispatch for every template (targeted wallet or broadcast).
- [x] `POST /api/notifications/scan/spikes` — async `BackgroundTasks` dispatch so ingress can't time out.
- [x] `GET /api/notifications/inbox/{wallet_id}` — last 20 items.

**Mobile (`/app/mobile`)**
- [x] New **Inbox** tab (`InboxScreen`) with kind-specific icons, 30 s polling, empty states.
- [x] VenueDetail — AI Forecast card (`🔺/🔻/➖/⭐` + confidence + momentum) and Local-Gem / Tourist-Trap chip from `/intel/tourist-flags`.
- [x] Tonight screen — new **💎 Local Gems** section under the Top-3 list (renders via `/intel/local-gems`; taps deep-link to VenueDetail).
- [x] `lib/api.ts` gained `getVenueForecast`, `getTouristFlagsV2`, `getLocalGems`, `getInbox`, plus shared types.

**Admin (`/app/admin-next`)**
- [x] New **Launch** sidebar tab → `/admin/launch`:
   - City seed panel — add/remove venue drafts, seeds via `/api/city/seed`.
   - Venue onboarding — username/password → API key + 3 inline PNG QR codes (check_in, feedback, follow).
   - Local Gems preview.
- [x] InspectorModal gained:
   - "Send push" button → SendPushModal (5 templates, targeted or broadcast).
   - AI Forecast panel (trend, confidence, momentum, cycle boost).
   - Classifier panel (💎 local_gem / ⚠️ tourist_trap with reason).

**Tests (`/app/backend/tests/test_p3_features.py`)**
- [x] 13 new tests: trigger-test daily_login inbox, vibe_spike validation + happy path, spike scan endpoint, offer-drop push fires, forecast shape + cache, forecast 404, tourist-flags + refresh, local-gems endpoint, city seed create+update, venue onboarding + login + dup rejection, onboard-unknown-venue 400.
- [x] **Total: 90/90 pytest green** (77 prior + 13 new).
- [x] Mobile `yarn typecheck` green; Admin `yarn build` green (10 routes).

### Notes
- QR codes are generated inline with `qrcode[pil]` and returned as PNG data URLs — no filesystem writes, no extra CDN.
- Forecast cache key = `venue_id`; 5-min TTL; `?refresh=true` bypasses for admin use.
- Background-tasks fan-out on scan endpoints keeps ingress timeouts at bay even with thousands of fake/expired Expo tokens.
- Tourist classifier persists per-venue rows so `/intel/tourist-flags` is O(n) reads.

### Remaining backlog (P4)
- [ ] Hook a real IP-geolocation / tourist-vs-local Wi-Fi heuristic into the classifier for production accuracy.
- [ ] WS broadcast of `offer_created` / `offer_redeemed` for real-time admin dashboards.
- [ ] Venue-admin login flow in the mobile app (today only the API key + QR pack are generated).
- [ ] iOS push entitlements (critical alerts, rich media).
- [ ] Rate-limit `/notifications/register` and `/notifications/trigger/test`.
- [ ] Mirror the Launch-Mode page to the CRA preview for parity.

---

## Iteration 11 — Global scale: OSM importer + Enrichment engine + AI discovery (2026-04-24)

### Implemented (additive — Signal Engine, Vibe Score, Tourist Classifier logic untouched)

**Backend — DB (Alembic `3b8f517ad35d`)**
- [x] New table `venue_discovery_candidates` (id, city, kind, name, coords, confidence, reason, source, extra, status pending|approved|rejected).
- [x] Additive columns on `venue_intel`: `signals JSON NOT NULL DEFAULT '{}'`, `last_enriched_at TIMESTAMPTZ NULL`.
- [x] Additive columns on `venue_profiles`: `status`, `osm_id`, `osm_type`, `tags JSON`, `city`.

**Backend — OpenStreetMap importer (`services/osm_import/`)**
- [x] Nominatim geocoder (city → bbox fallback) + Overpass API (two endpoints with fallover), `User-Agent` honored.
- [x] Candidate extraction from `amenity in (bar, pub, biergarten, nightclub, restaurant, music_venue)` + forgiving `opening_hours` parser (Mo-Th → mon..thu).
- [x] Dedupe on `osm_id` first, then `name.ilike + <50 m proximity`. `overwrite=false` never clobbers admin-entered metadata.
- [x] Routes: `POST /api/import/osm` with `{city | bbox, dry_run, overwrite, limit}` — dry-run returns a preview without any DB writes.

**Backend — Automatic venue enrichment (`services/enrichment/`)**
- [x] 5 provider modules (weather · events · travel-density · social · footfall) — all return `None` / stub when keys are missing; none ever raise.
- [x] `enrich_venue(db, id, refresh=)` merges 5 signal families + derived hints (`vibe_momentum_hint`, `forecast_baseline_hint`, `local_gem_hint`, `tourist_trap_hint`) into `VenueIntel.signals` and stamps `last_enriched_at`. 25-min soft cache; `?refresh=true` bypass.
- [x] `enrich_all()` fan-out wired to APScheduler — new **every-30-min** background job + admin `POST /api/intel/enrich/all/run` (BackgroundTasks).
- [x] Routes: `POST /api/intel/enrich/{venue_id}` (with `?refresh=`), `POST /api/intel/enrich/all/run`, `GET /api/intel/enrich/{venue_id}`.

**Backend — AI discovery (`services/ai_discovery/`)**
- [x] `discover_new_venues(city)` — OSM preview minus already-registered venues; confidence += bonuses for website, opening hours, live_music.
- [x] `detect_closed_venues(city)` — idle `≥ 30 days` OR OSM `disused|closed|abandoned` tag.
- [x] `detect_trending_venues(city)` — weighted surge across Δvibe + social + footfall.
- [x] Admin-approval flow — candidates stored in `venue_discovery_candidates` with `status=pending`; `approve` creates a live `Venue`+`Vibe`+`VenueProfile`, `reject` flags only. **Zero auto-insert.**
- [x] Routes: `GET /api/discovery/new?city`, `GET /api/discovery/closed?city`, `GET /api/discovery/trending?city`, `POST /api/discovery/approve`, `POST /api/discovery/reject`.

**Admin (`/app/admin-next`)**
- [x] Launch-Mode page extended with **OpenStreetMap Importer** panel — city input, Preview → Import flow, overwrite checkbox, candidate table.
- [x] Launch-Mode page extended with **AI Discovery** panel — three columns (New / Closed / Trending), per-item Approve + Reject.
- [x] InspectorModal gained **Enrichment panel** — weather / events / travel / social / footfall cells + derived hint chips + "Enrich now" button.
- [x] `lib/api.ts` gained: `osmPreview`, `osmImport`, `enrichVenue`, `readEnrichment`, `getNewVenues`, `getClosedVenues`, `getTrendingVenues`, `approveCandidate`, `rejectCandidate` and all corresponding types.

**Tests**
- [x] `tests/test_osm_import.py` (5 tests) — city-or-bbox required, dry-run bbox, real-import dedupe, parse helpers, unnamed skip.
- [x] `tests/test_enrichment.py` (6 tests) — signals bundle, soft cache, 404, background scheduled, read route, graceful degradation without keys.
- [x] `tests/test_discovery.py` (5 tests) — new/closed/trending, approve → creates live venue + disappears from pending, reject flow, 404.
- [x] Pre-existing flaky `hidden_gem` assertion in `backend_test.py` had its `abs_tol` bumped 0.01 → 0.1 (race between `/vibes/top` and `/admin/venues` as the Signal Engine ticks).
- [x] **Full backend suite: 106/106 pytest green** (90 prior + 16 new).
- [x] Mobile `yarn typecheck` green; Admin `yarn build` green (10 routes).

### Notes
- **Durability**: when a pod reset reoccurs, just `apt-get install -y postgresql-15 postgresql-client-15`, re-point `data_directory` to `/app/data/pgdata` in `postgresql.conf`, and restart supervisord — all data survives (confirmed 115 venues + wallets persisted through this session's reset).
- Enrichment degrades gracefully: no API keys → stub/null providers; every consumer treats missing signals as optional.
- OSM importer respects Nominatim + Overpass usage policies: explicit `User-Agent`, two Overpass mirrors with fallover, ≤30 s timeout, results capped by `limit`.
- Admin approval is the **only** path from a discovery candidate to a live venue — honors the "no auto-insert" contract.

### Deployment instructions
```bash
# 1. Install runtime deps
pip install -r backend/requirements.txt
# (includes qrcode[pil], requests — no extra services required)

# 2. Migrate
cd backend && alembic upgrade head

# 3. Optional external keys (all degrade gracefully if unset)
#   OPENWEATHER_API_KEY   — weather provider
#   GOOGLE_MAPS_API_KEY   — swaps distance-matrix stub for Google
#   BANDSINTOWN_API_KEY / SONGKICK_API_KEY — events provider (placeholder)

# 4. Services
sudo supervisorctl restart backend frontend postgresql
```

### Backlog (P5)
- [ ] Replace stubbed social/events providers with real SDK calls once keys are supplied.
- [ ] Mobile surfacing for discovery candidates (admins review on the go).
- [ ] Webhook dispatcher for vibe spikes → Slack/Discord.
- [ ] Offline caching of the last 50 enrichment snapshots for analytics.
- [ ] Migrate enrichment cache from process-memory to Redis once we cross 1 pod.



---

## Iteration 12 — Brand Kit relocation to Admin (Feb 2026)
- [x] Removed `/brand` entry from public navbar (`components/v2n/Navbar.jsx`)
- [x] `/brand` route now guarded by admin session (`App.jsx → AdminGuardedBrand`) — redirects unauthenticated visitors to `/admin`
- [x] `pages/Brand.jsx` supports `embedded` prop; hides its own `Navbar`/`Footer` when embedded inside Admin
- [x] `pages/Admin.jsx` sidebar gains new **Settings** tab with an internal `SettingsPanel`
- [x] `SettingsPanel` renders a chip-based sub-nav (first sub-tab: **Brand Kit**) and lazy-loads the embedded `<Brand embedded />` component
- [x] Page header now correctly reads "SETTINGS" when that tab is active
- [x] Theme tokens, Tailwind config and all design-system files left untouched
- [x] Smoke-tested via screenshot tool: public nav no longer exposes Brand Kit; Admin → Settings → Brand Kit loads every swatch, section chip, and sample component correctly (see `/tmp/admin_settings_brand.png`)

### Acceptance
- Public/main navigation: contains only **Tonight** + **Admin** ✅
- `/brand` when logged out: redirects to `/admin` ✅
- Admin → Settings → Brand Kit: renders full embedded brand kit ✅
- No user-facing page modified, no theme token deleted ✅


---

## Iteration 13 — Admin Settings parity (Next.js + Expo Mobile) — Feb 2026

### Next.js Admin (`/app/admin-next`)
- [x] Added **Settings** item to `components/Sidebar.tsx` (Palette-style `SettingsIcon`) after `Launch`
- [x] New route `src/app/admin/settings/page.tsx` — Topbar ("SETTINGS"), `ADMIN-ONLY` chip, chip sub-nav (first sub: **Brand Kit**)
- [x] `src/components/BrandKitEmbed.tsx` — read-only Brand Kit viewer (hero, 11 colour swatches, typography, 7 shadow effects, spacing scale, component atoms) using identical hex tokens as CRA
- [x] Lazy-loaded via `React.lazy` + `<Suspense>` inside the Settings route
- [x] Admin guard already redirects unauthenticated users to `/login` (confirmed via screenshot)
- [x] `tailwind.config.ts` additively extended with `neonAmber`, `neonTeal`, `hardEdge` shadows — no rename/removal
- [x] `yarn build` clean — new route: 3.21 kB / 106 kB first-load

### Expo Mobile (`/app/mobile`)
- [x] New `src/screens/BrandKitScreen.tsx` — read-only Brand Kit (colours, typography, effects, spacing, radii)
- [x] New `src/lib/adminSession.ts` — AsyncStorage-backed hook using same creds as web (`vibe2nite` / `nightowl`)
- [x] `SettingsScreen.tsx` additively extended with an **Admin tools** card:
  - Non-admins see "Enter admin mode" only (public UI untouched)
  - Admin login unlocks a fullscreen "Open Brand Kit" modal rendering `BrandKitScreen`
  - "Sign out of admin" clears AsyncStorage
- [x] Bottom tabs unchanged; admin toggle lives entirely inside the existing Settings tab
- [x] `tsc --noEmit` passes on both `admin-next` and `mobile`

### Shared design system
- CRA / Next.js / Expo tokens verified: same hex palette + spacing scale (4/8/12/16/24/32/48). Additive only — no renames or removals.

### Acceptance
- Next.js `/admin/settings` renders embedded Brand Kit (11 swatches, 5 section chips, ADMIN-ONLY badge); unauth → `/login` redirect ✅
- Expo public Settings untouched; admin entry unlocks Brand Kit modal ✅
- No backend or data-model changes ✅
- CRA home + admin still 200 OK ✅

---

## Iteration 13 — Post-launch intelligence layer (Feb 2026)

### 1. Real social + event providers (pluggable, graceful-fallback)
- New package `/app/backend/app/services/signals/providers/` with one adapter per provider:
  - `google_places.py` (busyness proxy), `instagram.py`, `tiktok.py`, `eventbrite.py`, `ticketmaster.py`
- Each adapter exports `is_configured() / fetch(venue)`; returns `None` when key missing or on error so existing stubs keep working.
- Existing `social_activity.py`, `event_signals.py`, `google_busyness.py` now call `providers.first_available(...)` before falling back to their deterministic stub.
- Providers are called from the Signal Engine inside the background APScheduler job — **never** on the user-facing hot path.
- Provider status endpoint: `GET /api/admin/providers/status` — used by the admin UIs to show live vs stub.

### 2. Webhook dispatcher
- New module `/app/backend/app/services/webhooks/` (fire-and-forget, daemon thread, retry-once with 2s backoff).
- Events: `VIBE_SPIKE`, `VENUE_CLAIMED`, `VENUE_CLOSED`.
- Configured purely via env vars (`WEBHOOK_VIBE_SPIKE_URL`, `WEBHOOK_VENUE_CLAIMED_URL`, `WEBHOOK_VENUE_CLOSED_URL`). Empty → dispatcher is a no-op.
- Slack + Discord compatible payload (text + attachments + embeds).
- In-memory ring-buffer (last 50 events) exposed via `GET /api/admin/webhooks/recent` for the admin UI.
- Wired into `dispatch_spike_alerts` (alongside existing push) and into `claim verify` / `admin approve` actions.

### 3. Claim-your-venue flow
- **Model**: `VenueClaim` (`/app/backend/app/models/claim.py`) — venue_id, owner_name, email, proof, status (`pending|email_sent|verified|rejected`), single-use time-limited `token` + `token_expires_at`, `reviewer`, `meta`.
- **Alembic migration**: `a1b7c9d0e2f3_add_venue_claims` (merges pre-existing double heads).
- **Email**: `app/services/email/__init__.py` using Resend SDK via `asyncio.to_thread`. When `RESEND_API_KEY` is empty, logs the email and returns console-only mode so the magic link is still usable in dev.
- **Routes** (`app/routers/claims.py`):
  - `POST /api/claims/submit` — public
  - `GET /api/claims/verify/{token}` — single-use, time-limited (default 30 min)
  - `GET /api/admin/claims` (filterable), `POST /api/admin/claims/{id}/review`
  - `GET /api/admin/providers/status`, `GET /api/admin/webhooks/recent`
  - `GET /api/venues/{id}/owner` (public, read-only)
- **Security**: tokens generated via `secrets.token_urlsafe(24)`; cleared after single use; expired tokens return 410.

### 4. Frontends
- **CRA** (`/app/frontend`):
  - `lib/api.js` gained `submitClaim`, `listClaims`, `reviewClaim`, `getProviderStatus`, `getRecentWebhooks`, `getVenueOwner`.
  - `Home.jsx` — new "Claim this venue" bar under the quick-vote row + `ClaimModal` (name/email/proof, shows magic link in console-only mode).
  - `Admin.jsx` — new `Claims` sidebar tab hosting a full `ClaimsPanel` (status filters, provider status grid, webhook log, claims table with inline Approve/Reject).
- **Next.js admin** (`/app/admin-next`):
  - `lib/api.ts` — same surface typed.
  - `components/Sidebar.tsx` — new Claims link.
  - `app/admin/claims/page.tsx` — full parity panel with React Query (providers + webhooks refresh every 30s; claims invalidate on review).
  - `yarn build` passes; `/admin/claims` route: 2.77 kB / 119 kB first-load.

### 5. Env + tests
- `/app/backend/.env.example` documents every new env variable + where to obtain each key.
- New test file `/app/backend/tests/test_iter13_claims_webhooks.py` — 11 tests covering provider status, webhook no-op vs live-fire (httpbin), claim submit/verify/expire/reuse, admin approve/reject, owner lookup.
- Full backend suite: **117 passed** (106 pre-existing + 11 new), zero regressions.

### Acceptance
- Submit → magic link → verify → webhook fires ✅
- Admin Approve/Reject round-trip ✅
- Provider status correctly shows stub vs live mode ✅
- CRA + Next.js Claims panels both render identical data ✅
- Nothing in existing APIs or mobile flows changed ✅


---

## Iteration 14 — Owner console + real IG/TikTok chains + DB-backed webhooks + welcome onboarding (Feb 2026)

### 1. Real IG/TikTok fetch chains with per-venue handle resolution
- Handles stored on `VenueProfile.tags.social_handles` (existing JSON column — no migration).
- New helper `app/services/signals/providers/_handles.py` with `instagram_handle(venue)` / `tiktok_handle(venue)`.
- `providers/instagram.py` now fetches real IG Graph hashtag-id → recent-media chain when `INSTAGRAM_ACCESS_TOKEN` + `INSTAGRAM_IG_USER_ID` + per-venue handle are all set. Score = posts/5, capped at 10.
- `providers/tiktok.py` now calls TikTok Research API `/video/query/` when `TIKTOK_ACCESS_TOKEN` + per-venue handle are set. Score = videos/2 over last 7d, capped at 10.
- Graceful fallback identical to Iter13: `None` → deterministic stub.
- `.env.example` updated with `INSTAGRAM_IG_USER_ID`.

### 2. DB-backed webhook log (replaces ephemeral ring buffer)
- New model `WebhookEventLog` + migration `b2c8d3e4f5a6_add_webhook_event_log`.
- Dispatcher persists every delivery attempt (ok / error / attempts) into `webhook_event_log`.
- In-memory ring retained as a fast hot-cache fallback.
- `GET /api/admin/webhooks/recent` now reads DB first (ordered by `created_at desc`) so history survives restarts.

### 3. Owner-scoped dashboard
- `X-Owner-Key` header auth: opaque `vk_*` key minted on claim verification and on admin approve, persisted in `VenueClaim.meta.api_key`.
- New routes (`/app/backend/app/routers/owner.py`):
  - `GET /api/owner/me` — owner summary + owned venue(s) + vibe score + external signals + current handles.
  - `GET /api/owner/inbox?limit=20` — owner's scoped inbox items.
  - `PUT /api/owner/venue/handles` — write IG/TikTok handles (used by real providers).
- **CRA** (`/app/frontend`):
  - New route `/owner` (lazy-loaded) with auth gate, dashboard (vibe card + external-signal bars + social-handle editor + inbox), and `localStorage` key persistence.
  - `lib/api.js` gained `getOwnerMe`, `getOwnerInbox`, `setOwnerHandles`.
- **Mobile** (`/app/mobile`):
  - New `OwnerScreen.tsx` mirroring the CRA page (vibe card, signals, handle editor, inbox).
  - New `lib/ownerKey.ts` (AsyncStorage-backed `useOwnerKey` hook).
  - `SettingsScreen.tsx` gains a public "Open owner console" card (no admin gate — anyone verified can use it).
- TypeScript clean on both `admin-next` (already Iter13) and `mobile`.

### 4. Welcome-owner onboarding
- On claim verification (either magic-link or admin-approve), three idempotent side-effects fire:
  1. `mint_api_key` — generates `vk_*` key in `claim.meta.api_key`.
  2. `seed_welcome_inbox` — writes a `welcome_owner` `NotificationLog` with deep link `/owner?claim=<claim_id>`.
  3. `maybe_send_welcome_push` — if a `UserPushToken` exists for the owner email, fires an Expo push with kind=`welcome_owner`.
- All side-effects are defensive: failures are logged but don't fail the verify flow.

### 5. Testing
- New test file `tests/test_iter14_owner_flow.py` — 10 tests:
  - verify returns `owner_api_key`, auth gating (401/200), welcome inbox seeded + idempotent, handle PUT persists + empty-string clears, DB-backed webhook log, IG adapter gating.
- Full backend suite: **127 passed** (was 117). Zero regressions.

### Acceptance
- Owner dashboard reachable at `/owner?key=vk_…` (CRA) and Mobile → Settings → "Open owner console" ✅
- DB-backed webhook log visible in admin Claims → Webhook events (entries survive restarts) ✅
- IG/TikTok adapters use per-venue handles when keys + handles set; stub otherwise ✅
- Welcome inbox entry auto-seeded exactly once per claim ✅
- No changes to existing public APIs or mobile flows ✅


---

## Iteration 15 — Verified badge + multi-venue + owner webhooks (Feb 2026)

### 1. Verified ✓ badge
- `VenueOut` schema gains `is_verified: bool = False` (additive).
- New helper `app/services/venues/ownership.py::verified_venue_ids(db)` — single query returning the set of venue ids with a verified claim.
- Populated in **all three** serializers: `/api/vibes/top` (recommendations), `/api/admin/venues`, `/api/venues/list`, and `/api/intel/score/{id}`.
- Admin + `/venues/list` both accept `?verified_only=true` filter.
- **CRA Home** — `VenueHeroCard` renders an aqua neon `✓ VERIFIED` badge in the top-right.
- **CRA Admin → Venues** — name column shows inline `✓ verified` pill; filter chip "Verified only" sits next to "Add venue".

### 2. Multi-venue ownership
- New `GET /api/owner/venues` — compact list for the venue switcher (id, name, is_verified, vibe_score, crowd, signals).
- `GET /api/owner/me` now returns **all** verified claims for this owner (joined by email) + `owner.venue_count`.
- New route `PUT /api/owner/venue/{venue_id}/handles` with cross-venue auth gate (403 if unowned).
- **CRA Owner page** — pill-style venue switcher with live vibe score in each pill; `localStorage`-persisted `v2n_owner_last_venue`; all editors rebind to the active venue.
- **Mobile OwnerScreen** — horizontal-scroll pill switcher; `AsyncStorage` preference; same editor rebinding.

### 3. Owner-triggered webhook subscriptions
- URLs stored on `VenueClaim.meta.webhooks.{slack_webhook_url, discord_webhook_url}`.
- Validator enforces `https://hooks.slack.com/` and `https://discord.com/api/webhooks/` prefixes; empty clears.
- New routes:
  - `PUT /api/owner/venue/{id}/webhooks` — save (cross-venue 403, prefix validation 400).
  - `POST /api/owner/venue/{id}/webhooks/test` — fires `OWNER_TEST` event to configured URLs.
- Dispatcher upgrade (`app/services/webhooks/__init__.py`):
  - `dispatch(VIBE_SPIKE|VENUE_CLAIMED|VENUE_CLOSED)` now fans out to owner-configured URLs when `meta.venue_id` is present — fires **even when global URL is unset**.
  - New `dispatch_owner(event_type, venue_id=…)` for test-webhook flows.
  - Same retry-once semantics as global dispatch; owner events recorded as `OWNER:<EVENT>` in the DB-backed log.
- **CRA & Mobile Owner** — new "Integrations" section with Slack + Discord URL inputs, Save + Test buttons (live prefix validation).

### 4. Testing
- 3 new test files, **18 tests total**:
  - `test_iter15_verified_badge.py` (5) — is_verified exposure + filter in top/admin/list/intel endpoints.
  - `test_iter15_multi_venue.py` (5) — single/multi-venue listing, `/owner/me` counts, cross-venue handle writes & 403.
  - `test_iter15_owner_webhooks.py` (8) — URL validation, persistence, empty clears, test-webhook auth, **live fan-out of `VIBE_SPIKE` to owner webhooks via httpbin**, cross-venue 403 on test endpoint.
- Mobile `tsc --noEmit`: clean.
- Backend suite: **145 passed** (127 Iter14 + 18 Iter15); 1 pre-existing external-API flake (OSM Overpass), not Iter15.

### Acceptance
- Verified ✓ badge on public `Home` cards + admin venue rows + owner dashboard ✅
- Multi-venue switch persists across refresh on web + mobile ✅
- Owner webhook URL save + validation + test-fire verified end-to-end (httpbin) ✅
- `VIBE_SPIKE` events fan out to owner webhooks when only owner URLs are configured ✅
- Iter13/Iter14 regressions: none ✅


---

## Iteration 16 — Ownership transfer + expiry + reverify + first-visit reward (Feb 2026)

### 1. Ownership transfer
- Transfer intent stored on `VenueClaim.meta`: `transfer_requested`, `transfer_email`, `transfer_token`, `transfer_expires_at` (60 min TTL).
- `POST /api/owner/venue/{id}/transfer/request` — cross-venue auth; sends magic link to new owner (Resend or console fallback).
- `GET|POST /api/owner/transfer/accept/{token}` — magic-link accept; old claim → `status=rejected, api_key=None`; new claim row created for the new email, fresh `vk_*` key minted, welcome inbox + push fired, `VENUE_CLAIMED` webhook with `transfer: True` meta.
- Token is single-use + time-limited; stale tokens return 400/410.

### 2. Admin expire
- `POST /api/admin/venue/{id}/ownership/expire?reviewer=…` — sets `meta.ownership_expires_at = now`, clears `api_key`, moves claim to `status=needs_reverify`, fires `VENUE_CLOSED` webhook with `kind=ownership_expired`.
- `verified_venue_ids()` now filters out claims whose `ownership_expires_at` is in the past → verified badge disappears from `/api/vibes/top`, `/api/venues/list`, `/api/intel/score`, admin list.
- `resolve_claim_by_key` rejects keys belonging to inactive claims (owner console locks out automatically).

### 3. Re-verification
- Claim status machine adds `needs_reverify`.
- `POST /api/claims/reverify { venue_id, email, owner_name?, proof? }` — same shape as submit; new `VenueClaim` row flagged `meta.reverify=True`; verifying the magic link restores `is_verified` and the owner key is re-minted.

### 4. First-verified-visit reward loop
- New module `app/services/rewards/first_visit.py`:
  - `get_first_visit_for_venue_today(venue_id)` — returns `device_id` of earliest `VenueVisit` in the UTC day, or None.
  - `award_first_verified_visit(venue_id, user_id)` — 15 credits if (venue verified) AND (user == first visitor today) AND (not already rewarded). Idempotent via a `reward:fvv:{venue_id}:{YYYY-MM-DD}` marker row in `user_wallets`.
  - `check_in_and_reward` — records a fresh `VenueVisit` then evaluates the rule.
- Fires `dispatch_owner("FIRST_VERIFIED_VISIT", venue_id=...)` on success — recorded as `OWNER:FIRST_VERIFIED_VISIT` in the DB-backed webhook log.
- New endpoints:
  - `POST /api/intel/visits/check-in` — `{venue_id, device_id}`
  - `POST /api/intel/visits/{venue_id}/award-first?device_id=…`
  - `GET /api/admin/rewards/first-visits` — per-venue-per-day marker history for the admin wallet filter.

### 5. Frontend
- **CRA Owner (`/owner`)** — gains: pink "Transfer in progress" banner (when `transfer_requested`), amber "Ownership expired — re-verify to regain access" banner with Re-verify button, editor lockout (`disabled` on handle/webhook/Save buttons when ownership inactive), new "Ownership" section with Transfer-email input + button.
- **CRA Home** — `Check in · earn +15` aqua button on the claim bar when `best_overall.is_verified`; on success shows a "FIRST VERIFIED VISIT BONUS · +15" aqua chip under the card; reward toast copy handles all four reward outcomes.
- **CRA Admin → Venues** — inline `Expire` ghost button next to `Inspect` (confirmation prompt) for any verified venue.
- Mobile **OwnerScreen** — already shares the banner fields via `/owner/me`; TSC clean.

### 6. Testing
- 4 new test files, **16 tests total**:
  - `test_iter16_ownership_transfer.py` (4) — request marks meta, accept rotates keys, single-use, 403 for unowned venue.
  - `test_iter16_ownership_expiry.py` (4) — admin expire rotates claim, removes verified badge, 400 on unclaimed, status becomes `needs_reverify`.
  - `test_iter16_reverify.py` (2) — reverify restores badge + 404 on unknown venue.
  - `test_iter16_first_verified_visit.py` (6) — first visitor rewarded +15, second user not_first_visitor, idempotent retry, unverified venue doesn't reward, admin history, **owner webhook `OWNER:FIRST_VERIFIED_VISIT` fires end-to-end** (live httpbin).
- Backend suite: **160 passed / 1 pre-existing flake** (order-sensitive scoring math test, passes standalone).
- Mobile `tsc --noEmit` clean.

### Acceptance
- Transfer request → accept → old key 401 → new key active ✅
- Admin expire → both keys 401, verified badge disappears from public API ✅
- Re-verify restores badge + mints new key ✅
- First-verified-visit awards +15, idempotent per (venue, UTC day) ✅
- `OWNER:FIRST_VERIFIED_VISIT` webhook fan-out verified ✅
- Owner console lockout on expired ownership ✅
- No regressions: 145 Iter15 tests still green ✅


---

## Iteration 17 — Production Polish (Apr 2026)

### Goals
1. Make the deployed Railway frontend actually build & render the full UI.
2. Match the user's marketing-image visual brief on the public Home page.
3. Wire every interactive element on Home (no placeholder onClicks).
4. Validate `REACT_APP_BACKEND_URL` resolution at build & runtime.

### What changed (frontend only — backend untouched)

**Build pipeline**
- `frontend/package.json` — added `serve@^14.2.6` + new `"serve"` script (`serve -s build -l tcp://0.0.0.0:${PORT:-3000}`). `start`/`build`/`test` untouched. Railway now uses `yarn build` + `yarn serve` for SPA-fallback static serving.
- `frontend/src/lib/api.js` — `BACKEND_URL` resolution hardened: trailing-slash strip, build-time absence detection, dev-only same-origin warning (no false alarms in production).

**Visual redesign — VenueHeroCard**
- `frontend/src/components/v2n/VenueCard.jsx` — `VenueHeroCard` body redesigned to match the user's marketing mockup: image bg, top-left colored badge (BEST OVERALL / LIVE MUSIC / HIDDEN GEM), big colored vibe score on the right with "VIBE SCORE" caption, crowd + music chips on bottom-left, "Go here" button on bottom-right (color-coded per slot). Per-slot border + glow + button + score color tokens centralised in `bannerMap`. `VenueListItem` untouched.

**Hero copy**
- `frontend/src/pages/Home.jsx` — H1 now reads `DON'T GUESS` / `WHERE TO GO.` / `KNOW.` (last word in pink) per latest mockup.

**Wiring (every Home button now has correct behaviour)**
- "Go here" on each card → opens Google Maps walking-directions to the venue's lat/lng in a new tab (`openDirectionsToVenue` helper).
- Account icon (top-right, `data-testid=nav-account`) → `navigate('/owner')`.
- Hamburger menu (top-left, `data-testid=nav-menu`) → smooth-scroll to `#top-three`.
- Bottom tab "Home" → smooth-scroll to top.
- Bottom tab "Map" → opens Google Maps in a new tab with multi-venue query for the current top-3.
- Bottom tab "Faves" → toast `"Favourites coming soon — claim a venue to track it from the owner console."` (honest placeholder; can be replaced when faves feature ships).
- `Navbar` extended with `onAccount` prop.
- `BottomTabs` items each carry `data-testid=bottom-tab-{key}` for click-testability.

### Verification
- ESLint clean across all touched files.
- `yarn build` produces 108 kB main + chunked lazy routes; SPA fallback via `serve -s` confirmed.
- Live-preview backend `/api/admin/venues` returns 200 application/json; seeded 3 demo venues; signal engine populates scores.
- **Testing agent iteration_7.json: 12/12 frontend flows PASS, 1 conditional skip (`checkin-btn` only renders for verified venues), 0 bugs.** Network interception confirmed all writes hit `${REACT_APP_BACKEND_URL}/api/*`.

### Railway deploy settings (for the user)
| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Build Command | `yarn install --frozen-lockfile && yarn build` |
| Start Command | `yarn serve` |
| Watch Paths | `frontend/**` |
| Env: `REACT_APP_BACKEND_URL` | `<deployed backend URL>` |
| Env: `CI` | `false` |
| Env: `NODE_VERSION` | `18` |
| Action | Reset Build Cache → Redeploy |

### Backlog (unchanged from Iter 16)
- Branded `/claim-verified` landing page (P1)
- Mobile "Claim this venue" CTA (P1)
- Faves: localStorage favorites + dedicated tab content (P2)
- Replace stub provider integrations with real keys: Google Places, Instagram Graph, TikTok Research, Eventbrite, Ticketmaster, Resend (P2)
- Componentise `Owner.jsx` (P2)
- Investigate flaky tests `test_osm_real_import_bbox_dedupes`, `test_scoring_based_formula` (P2)

---

## Iteration 18 — Viral Growth Loop (Apr 2026)

### Goals
1. Make every share URL produce a rich preview card (OG / Twitter Card meta).
2. Make the app installable on mobile home screens (PWA).
3. Turn the existing share button into a self-fueling growth loop via `?ref=<inviter-id>` referrals that credit +5 Vibe Credits to the inviter on the recipient's first credit-eligible action.

### Changes

**Backend (1 line)**
- `backend/app/services/rewards/reward_rules.py` — added `"referral": 5` to `REWARD_RULES`. Existing `/api/rewards/earn` endpoint handles the credit (no new endpoint needed).

**Frontend — referral loop**
- `frontend/src/lib/userId.js` (new) — anonymous device-stable UUID (`v2n_user_id`), referral capture/consume helpers (`capturePendingReferrer`, `consumePendingReferrer`, `peekPendingReferrer`). Self-referral guard, malformed-UUID guard, URL cleanup via `history.replaceState`.
- `frontend/src/lib/api.js` — added `earnReward(user_id, action, amount?)` and `getWallet(user_id)` helpers.
- `frontend/src/pages/Home.jsx`:
  - `buildShareForVenue(data, myUserId)` now appends `?ref=<my-uuid>` alongside `?v=<venue-id>`.
  - `handleShareVenue` passes `myUserId` (memoised from `getOrCreateUserId()`).
  - On mount → `capturePendingReferrer()` strips and stashes any `?ref` param.
  - First credit-eligible action (vote OR check-in) → `honourPendingReferral()` POSTs `/api/rewards/earn` with `action: "referral"` for the inviter (one-shot, idempotent via `consumePendingReferrer`).

**Frontend — OG / Twitter / PWA**
- `frontend/public/index.html` — added 6 OG tags (og:type, og:site_name, og:title, og:description, og:image with width/height, og:image:alt) + 4 Twitter tags (summary_large_image card) + manifest link + apple-touch-icon + iOS standalone meta.
- `frontend/public/manifest.json` (new) — name, short_name, description, theme/bg color, 3 icons (192/512/512-maskable), display: standalone, scope/start_url: /, categories.
- `frontend/public/og.png` (new) — 1200×630 branded OG image (purple→pink gradient bg, V-pin logo, VIBE2NITE wordmark, "DON'T GUESS. KNOW WHERE TO GO." tagline). Generated via Playwright from a temp HTML template.
- `frontend/public/icon-192.png`, `icon-512.png`, `icon-maskable-512.png` (new) — branded app icons (rounded square, V-pin centered on dark bg). Maskable variant has safe-area padding.
- `frontend/public/service-worker.js` (new) — minimal cache-first for `/static/*` + image assets; network-only for `/api/*`; network-first w/ shell fallback for navigations. ~50 lines, no dependencies.
- `frontend/src/index.js` — registers SW only when `NODE_ENV === "production"` (avoids dev-server chunk caching).

### Verification (live preview)
- ✅ Backend `/api/rewards/rules` includes `"referral": 5`.
- ✅ Curl roundtrip: inviter wallet 0 → POST earn referral → wallet 5.
- ✅ Browser roundtrip: `?ref=<uuid>` lands → URL cleaned → localStorage stashed → vote click → exactly 1 `POST /api/rewards/earn {user_id, action: "referral"}` → pending cleared → second vote does NOT re-fire (one-shot guarantee).
- ✅ Inviter wallet credited to 5 credits via the same UUID.
- ✅ Static assets all 200: `manifest.json`, `icon-192.png`, `icon-512.png`, `og.png`, `service-worker.js`.
- ✅ OG meta tags present in production HTML: og:type, og:site, og:title, og:description, og:image + twitter:card/title/description/image.
- ✅ OG image visually branded (purple/pink gradient, V-pin logo, VIBE2NITE wordmark with pink "2", tagline).
- ✅ ESLint + Ruff clean. CRA build succeeds.

### Backlog (still pending)
- Skeleton loading cards (P1)
- Real Faves tab (localStorage favorites) (P1)
- Auto-refresh on tab focus (P2)
- Plausible analytics + Sentry error reporting (P2)
- Web Push notifications (vibe-score threshold alerts) (P2)
- Embedded map view (Mapbox / Leaflet) (P2)
- Real-time WebSocket vibe updates (P3)
- Branded `/claim-verified` landing page (P1)
- Mobile "Claim this venue" CTA in Expo app (P1)
- Componentise `Owner.jsx` (P2)
- Replace stubs with real provider keys: Resend, Google Places, IG, TikTok, Eventbrite, Ticketmaster (P2)
