# VIBE2NITE · Admin (Next.js 14 · App Router · TypeScript · Tailwind)

Desktop-first curator console for the Vibe2Nite backend. Consumes existing
`/api/admin/*` endpoints and the vibes-extras endpoints.

---

## Quick start

```bash
cd /app/admin-next
yarn install                                 # already done in repo
yarn dev                                     # → http://localhost:3100
# or
NEXT_PUBLIC_API_URL="https://<your-backend>" yarn dev
```

Demo credentials (client-side auth — replace before prod):

```
username: vibe2nite
password: nightowl
```

---

## Project layout

```
admin-next/
├── next.config.mjs
├── postcss.config.js
├── tailwind.config.ts
├── tsconfig.json
├── .env.local              # NEXT_PUBLIC_API_URL=...
└── src/
    ├── app/
    │   ├── layout.tsx      # root layout + Providers
    │   ├── globals.css     # neon gradients + fonts
    │   ├── providers.tsx   # React Query provider
    │   ├── page.tsx        # redirect → /admin/overview
    │   ├── login/
    │   │   └── page.tsx    # branded login form
    │   └── admin/
    │       ├── layout.tsx  # auth guard + Sidebar
    │       ├── overview/page.tsx   # stat tiles + 4 Recharts panels
    │       ├── venues/page.tsx     # search, table, add-modal, inspect
    │       └── signals/page.tsx    # per-venue signal bars, last-updated
    ├── components/
    │   ├── Logo.tsx        # VIBE2NITE wordmark + pin mark
    │   ├── Sidebar.tsx     # Sidebar + Topbar
    │   ├── InspectorModal.tsx  # edit · signal engine · live preview · intel
    │   └── ui.tsx          # Button, Chip, Input, Select, Slider
    ├── hooks/
    │   └── useAuth.ts      # localStorage-backed session hook
    └── lib/
        ├── api.ts          # typed fetch client
        └── cn.ts           # clsx + tailwind-merge
```

---

## Pages

| Route | Purpose | Endpoints used |
|---|---|---|
| `/login` | Demo auth (vibe2nite / nightowl) | — |
| `/admin/overview` | 4 stat tiles + Top-scores bar + Avg signals line + Category pie + Crowd bar | `GET /api/admin/venues`, `POST /api/admin/signals/refresh` |
| `/admin/venues` | Search, table, +Add venue, Inspect → modal | `GET /api/admin/venues`, `POST /api/admin/venues`, `PATCH /api/admin/venues/{id}/signals`, `POST /api/admin/signals/refresh` |
| `/admin/signals` | Per-venue progress bars + last-updated, sortable | `GET /api/admin/venues`, `POST /api/admin/signals/refresh` |

### Inspector Modal

- **Left** — editable sliders for `manual_score`, `social_activity`, `time_prediction`, `venue_boost`
- **Middle** — Signal Engine read-out with 5 progress bars + `updated_at`
- **Right** — Live Preview score + Crowd label + Intelligence block (Forecast · Crowd type · Live music) wired to `/vibes/forecast`, `/vibes/tourist-flags`, `/vibes/live-music`

---

## Brand theme

`tailwind.config.ts` exports the exact tokens used by the web + mobile apps:

| Token | Hex |
|---|---|
| `primary` | `#8A2BE2` |
| `primary.glow` | `#B15CFF` |
| `accent.pink` | `#FF2EC4` |
| `accent.magenta` | `#FF4EDB` |
| `glow.aqua` | `#00F5FF` |
| `glow.teal` | `#00D1C7` |
| `background.dark` | `#0A0A12` |
| `background.deep` | `#05050A` |
| `status.busy` | `#FF9A1F` |
| `status.medium` | `#C7A7FF` |
| `status.dead` | `#6B6B6B` |

Shadows: `shadow-neonPurple`, `shadow-neonPink`, `shadow-neonAqua`, `shadow-softPurple`.

---

## Data fetching

- **@tanstack/react-query** — 30 s stale time, 1 retry.
- Mutations (`updateSignals`, `triggerSignalRefresh`, `createVenue`) invalidate `["admin-venues"]` on success.

---

## Production

```bash
yarn build
NEXT_PUBLIC_API_URL="https://api.yourhost" yarn start
```

Deploy to Vercel / Railway / any Node host. The preview environment currently
runs the React CRA frontend on port 3000, so this Next.js app uses **3100** to
avoid collisions; adjust in `package.json` if needed.
