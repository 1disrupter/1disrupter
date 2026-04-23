/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}", "./public/index.html"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "#8A2BE2", glow: "#B15CFF" },
        accent: { pink: "#FF2EC4", magenta: "#FF4EDB" },
        background: { dark: "#0A0A12", deep: "#05050A" },
        status: { busy: "#FF9A1F", medium: "#C7A7FF", dead: "#6B6B6B" },
        glow: { aqua: "#00F5FF", teal: "#00D1C7" },
      },
      boxShadow: {
        neonPurple: "0 0 12px #8A2BE2, 0 0 24px #8A2BE2",
        neonPink: "0 0 12px #FF2EC4, 0 0 24px #FF2EC4",
        neonAqua: "0 0 12px #00F5FF, 0 0 24px #00F5FF",
        neonAmber: "0 0 10px #FF9A1F, 0 0 22px #FF9A1F",
        neonTeal: "0 0 10px #00D1C7, 0 0 22px #00D1C7",
        softPurple: "0 10px 40px -10px rgba(138,43,226,0.55)",
        hardEdge: "0 0 0 1px #B15CFF, 0 0 0 2px rgba(177,92,255,0.25)",
      },
      fontFamily: {
        vibe: ["Outfit", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Bebas Neue", "Outfit", "sans-serif"],
      },
      borderRadius: { xl2: "18px", xl3: "22px" },
      keyframes: {
        "vibe-pulse": {
          "0%,100%": { opacity: "1", filter: "brightness(1)" },
          "50%": { opacity: ".85", filter: "brightness(1.3)" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        sheen: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
      animation: {
        "vibe-pulse": "vibe-pulse 2.4s ease-in-out infinite",
        "fade-up": "fade-up .45s ease-out both",
        sheen: "sheen 2.5s linear infinite",
      },
    },
  },
  plugins: [],
};
