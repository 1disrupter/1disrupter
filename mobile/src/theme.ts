/**
 * Vibe2Nite brand theme — single source of truth for colours, typography,
 * spacing and shadow tokens. Values mirror the web brand kit (`/app/frontend`
 * & `tailwind.config.js`). Do not change without coordinating with design.
 */
export const colors = {
  primary: "#8A2BE2",
  primaryGlow: "#B15CFF",
  pink: "#FF2EC4",
  magenta: "#FF4EDB",
  aqua: "#00F5FF",
  teal: "#00D1C7",
  amber: "#FF9A1F",
  lavender: "#C7A7FF",
  dead: "#6B6B6B",
  bg: "#05050A",
  bgAlt: "#0A0A12",
  card: "#11071F",
  border: "#2A1846",
  text: "#F5EFFF",
  textMuted: "#9C8FBF",
  textFaint: "rgba(255,255,255,0.45)",
} as const;

export const radius = {
  sm: 8,
  md: 14,
  lg: 18,
  xl: 22,
  pill: 999,
} as const;

export const spacing = { xxs: 4, xs: 8, sm: 12, md: 16, lg: 24, xl: 32, xxl: 48 } as const;

export const font = {
  display: "System", // use RN default; swap to Bebas Neue via expo-font if desired
  body: "System",
} as const;

export const shadow = {
  neonPurple: {
    shadowColor: colors.primary,
    shadowOpacity: 0.8,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 0 },
    elevation: 10,
  },
  neonPink: {
    shadowColor: colors.pink,
    shadowOpacity: 0.8,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 0 },
    elevation: 10,
  },
  neonAqua: {
    shadowColor: colors.aqua,
    shadowOpacity: 0.8,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 0 },
    elevation: 10,
  },
} as const;

export type ThemeColors = typeof colors;
