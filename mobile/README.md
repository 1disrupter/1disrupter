# VIBE2NITE · Mobile (Expo · React Native · TypeScript)

Stunning, neon, dark-mode mobile app for finding tonight's vibe — Top-3
recommendations, live heat map, live-music flags, local gems, tourist traps,
vibe forecast, directions and 1-tap feedback.

Runs on iOS + Android via [Expo](https://expo.dev/).

---

## Quick start

```bash
cd /app/mobile
yarn install                                    # already done in repo
EXPO_PUBLIC_API_URL="https://<your-backend>" yarn start
```

Then scan the QR code with **Expo Go** on your device, or press `i`/`a` to
open the iOS/Android simulator.

> Default `apiUrl` is baked into `app.json → expo.extra.apiUrl`. Override at
> runtime with `EXPO_PUBLIC_API_URL`.

---

## Project layout

```
mobile/
├── App.tsx                       # Providers + RN Navigation entry
├── app.json                      # Expo config (iOS/Android bundle ids, plugins)
├── babel.config.js
├── tsconfig.json
└── src/
    ├── theme.ts                  # Brand colour / spacing / shadow tokens
    ├── config.ts                 # API base URL + default location
    ├── lib/api.ts                # Typed fetch client hitting /api/*
    ├── navigation/
    │   └── RootTabs.tsx          # Bottom tabs + stack
    ├── screens/
    │   ├── TonightScreen.tsx     # Top-3 feed + category tabs + directions
    │   ├── MapScreen.tsx         # Heat-map pins + bottom-sheet details
    │   ├── VenueDetailScreen.tsx # Full card + 1-tap feedback
    │   └── SettingsScreen.tsx    # About / Backend / Links
    └── components/
        ├── Logo.tsx              # VIBE2NITE wordmark + pin icon
        ├── GlowButton.tsx        # Pill, gradient, neon shadow
        ├── Chip.tsx              # Chip, TrendBadge, TouristFlagBadge, LiveMusicBadge
        ├── CategoryTabs.tsx      # All / Bars / Clubs / Live Music
        ├── VibeScoreBadge.tsx    # Big score + crowd dot + sparkline
        └── VenueCard.tsx         # Hero card used in Tonight feed
```

---

## Screens

| Screen       | What it shows | Endpoints used |
|--------------|--------------|----------------|
| Tonight      | Top-3 cards, trend/tourist/live badges, distance, 1-tap directions | `/vibes/top3`, `/vibes/forecast`, `/vibes/tourist-flags`, `/vibes/live-music`, `/vibes/directions` |
| Map          | Full-screen dark map, heat-coloured pins, bottom-sheet venue detail    | `/vibes/heatmap`, `/vibes/forecast`, `/vibes/tourist-flags`, `/vibes/live-music`, `/vibes/directions` |
| Venue Detail | Big score, crowd label, trend, sparkline placeholder, **1-tap votes** | `/vibes/forecast`, `/vibes/tourist-flags`, `/vibes/live-music`, **`POST /feedback`** |
| Settings     | About, backend URL, API-docs link                                      | —              |

All data fetching goes through **@tanstack/react-query** — pull-to-refresh
invalidates every query.

---

## Theme

`src/theme.ts` is the single source of truth:

| Token | Hex |
|---|---|
| Neon Purple | `#8A2BE2` |
| Glow Purple | `#B15CFF` |
| Electric Pink | `#FF2EC4` |
| Magenta | `#FF4EDB` |
| Aqua | `#00F5FF` |
| Teal | `#00D1C7` |
| Amber | `#FF9A1F` |
| Lavender | `#C7A7FF` |
| Midnight bg | `#05050A` |

Three boxShadow presets (`neonPurple` / `neonPink` / `neonAqua`) mirror the
web Tailwind config.

---

## Building for stores

```bash
npx expo prebuild          # generate native iOS/Android projects
eas build --profile production --platform ios
eas build --profile production --platform android
```

See [EAS docs](https://docs.expo.dev/eas/) for signing & submission.

---

## Maps notes

Uses [`react-native-maps`](https://github.com/react-native-maps/react-native-maps) so Android ships with Google Maps out of the box. For iOS, Apple Maps works by default; add a Google Maps API key in `app.json → ios.config.googleMapsApiKey` if you want Google Maps there too. Marker pulses & heat colours are handled with plain RN views — no extra native libs required.
