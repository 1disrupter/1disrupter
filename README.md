# 🟣 VIBE2NITE API

**Find the vibe. Go tonight.**

Real-time nightlife recommendation engine. Given your coordinates, Vibe2Nite returns three curated spots: **best overall**, **live music**, and a **hidden gem** — all ranked by a weighted **Vibe Score**.

---

## 🎨 Brand

All generated surfaces (API docs, admin responses, assets) use the Vibe2Nite palette:

| Token | Hex | Use |
|---|---|---|
| Neon Purple (primary) | `#A260FF` | Brand, GET verbs, CTAs |
| Electric Violet | `#8A49FF` | Deep gradients |
| Electric Pink | `#FF3BA7` | Accent, POST verbs, highlights |
| Soft Lavender | `#C9B6FF` | Secondary text |
| Teal / Aqua | `#40E0FF` | Glow, links, section titles |
| Warm Amber | `#FFB347` | `busy` / `packed` states, PATCH |
| Midnight | `#05020D` | Background |
| Card | `#11071F` | Surface |

Typography: **Bebas Neue** (display) + **Space Grotesk** (body). Logo follows the promo style: white `VIBE`, gradient `2`, white `NITE`.

Branded Swagger UI is served at **`GET /api/docs`**.

---

## 🧱 Stack

- **FastAPI** 0.115
- **SQLAlchemy 2.0** (ORM, typed mapped columns)
- **Alembic** (migrations)
- **PostgreSQL 15**
- **Pydantic v2** (+ `pydantic-settings`)
- **Uvicorn** (ASGI, managed by supervisor)

---

## 📁 Project structure

```
backend/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── <revision>_initial_schema.py
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI factory
│   ├── seed.py              # Seed script (python -m app.seed)
│   ├── core/
│   │   ├── config.py        # Settings (env-driven)
│   │   ├── database.py      # Engine, Session, Base
│   │   └── docs.py          # Branded Swagger renderer
│   ├── models/              # SQLAlchemy ORM
│   │   ├── venue.py
│   │   ├── vibe.py
│   │   └── feedback.py
│   ├── schemas/             # Pydantic I/O
│   │   ├── vibe.py
│   │   └── feedback.py
│   ├── services/            # Pure business logic
│   │   ├── scoring.py       # Weighted score + crowd bands
│   │   ├── geo.py           # Haversine
│   │   ├── recommendations.py
│   │   └── feedback_service.py
│   ├── routers/             # HTTP surface
│   │   ├── vibes.py
│   │   ├── feedback.py
│   │   └── admin.py
│   └── static/
│       └── vibe2nite.css    # Branded docs CSS
├── requirements.txt
├── server.py                # supervisor entrypoint (imports app.main:app)
└── .env                     # DATABASE_URL, APP_NAME, ...
```

---

## 🔌 API surface

All endpoints are prefixed with **`/api`** (K8s ingress requirement).

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/api/health`                            | Heartbeat |
| `GET`  | `/api/docs`                              | Branded Swagger UI |
| `GET`  | `/api/openapi.json`                      | OpenAPI 3.1 schema |
| `GET`  | `/api/vibes/top?lat&lng&radius_km=50`    | Top-3 recommendations |
| `POST` | `/api/feedback`                          | Submit a vote (`busy`/`dead`/`good`) |
| `GET`  | `/api/admin/venues`                      | List all venues + vibes |
| `POST` | `/api/admin/venues`                      | Create a venue |
| `PATCH`| `/api/admin/venues/{venue_id}/signals`   | Update manual signals |

### Response shape of `/api/vibes/top`

```json
{
  "best_overall": { "venue": {...}, "vibe": {...}, "distance_km": 0.62 },
  "live_music":   { "venue": {...}, "vibe": {...}, "distance_km": 0.83 },
  "hidden_gem":   { "venue": {...}, "vibe": {...}, "distance_km": 3.66 }
}
```

### Selection rules
1. **best_overall** = highest `vibe_score` within `radius_km`
2. **live_music**   = highest `vibe_score` where `category == live_music`; if none exist, falls back to `best_overall`
3. **hidden_gem**   = lowest `vibe_score` within `radius_km`

---

## 🔢 Vibe Score

```
score = manual_score   * 0.25
      + social_activity* 0.25
      + user_votes     * 0.25
      + time_prediction* 0.15
      + venue_boost    * 0.10
```
Capped at `10`, floored at `0`.

**Crowd bands**: `≥ 8 busy` · `≥ 5 medium` · `< 5 dead`.

Voting deltas applied to `user_votes`:

| Vote | Δ |
|---|---|
| `busy` | +1.0 |
| `good` | +0.5 |
| `dead` | −1.0 |

---

## 🚀 Local setup

```bash
# 1. Postgres must be running (already supervised in this env)
pg_isready -h 127.0.0.1 -p 5432

# 2. Install deps
pip install -r backend/requirements.txt

# 3. Migrate & seed
cd backend
alembic upgrade head
python -m app.seed

# 4. Run (supervisor already does this)
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

---

## 🧪 Smoke tests

```bash
# Health
curl http://localhost:8001/api/health

# Top-3 near Times Square
curl "http://localhost:8001/api/vibes/top?lat=40.73&lng=-73.99"

# Submit feedback
curl -X POST http://localhost:8001/api/feedback \
  -H 'Content-Type: application/json' \
  -d '{"venue_id":"<uuid>","vote":"busy"}'
```

---

## 📝 Migrations

```bash
# Create a new revision after editing models
alembic revision --autogenerate -m "add new column"

# Apply
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

---

## 🗺 Roadmap

- [ ] Auth on `/admin/*` and rate-limit on `/feedback`
- [ ] Real social-signal ingestion (Instagram/TikTok hashtag velocity)
- [ ] Time-prediction ML model (replace static `time_prediction`)
- [ ] PostGIS `gist` index for large-scale geo queries
- [ ] WebSocket "Vibe Pulse" pushing score changes live
- [ ] Mobile clients (iOS / Android) matching this brand system
