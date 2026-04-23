# Vibe2Nite — Test credentials

## Admin Console (`/admin`)
Simple local-only auth (localStorage-based, identical on CRA and Next.js admins).

| Field | Value |
|---|---|
| Username | `vibe2nite` |
| Password | `nightowl` |

The hint is visible on the login screen. Replace with backend auth when shipping to prod.

## Backend endpoints
No auth required. All endpoints under `/api/*`.

## Test identifiers
- Any opaque `user_id` string can be used when testing `/api/rewards/*` (e.g. `pytest-user-1`). Wallets are created on first access.
- For `/api/intel/ping`, `device_id` is optional; use any short UUID-like string when simulating a device.
- Seeded venue count is **12** (may grow across iterations due to tests — idempotent-unsafe seeder).

## PostgreSQL (local dev only)
| Field | Value |
|---|---|
| User | `vibe2nite` |
| Password | `vibe2nite_dev` |
| Database | `vibe2nite` |
| Port | `5432` |
