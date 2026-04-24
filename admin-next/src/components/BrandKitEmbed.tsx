"use client";
/**
 * Read-only Brand Kit viewer — Next.js embedded variant.
 * Mirrors /app/frontend/src/pages/Brand.jsx (CRA embedded mode) using the
 * same hex tokens. This component has no Navbar/Footer of its own so it
 * drops cleanly into Admin → Settings.
 */
import * as React from "react";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/cn";
import { Chip, Button } from "@/components/ui";

const COLORS: Array<[string, string, string]> = [
  ["Primary / Neon Purple", "#8A2BE2", "primary"],
  ["Primary / Glow Purple", "#B15CFF", "primary-glow"],
  ["Accent / Electric Pink", "#FF2EC4", "accent-pink"],
  ["Accent / Magenta", "#FF4EDB", "accent-magenta"],
  ["Glow / Aqua", "#00F5FF", "glow-aqua"],
  ["Glow / Teal", "#00D1C7", "glow-teal"],
  ["Background / Midnight", "#0A0A12", "background-dark"],
  ["Background / Deep", "#05050A", "background-deep"],
  ["Status / Busy (Amber)", "#FF9A1F", "status-busy"],
  ["Status / Medium (Lavender)", "#C7A7FF", "status-medium"],
  ["Status / Dead (Grey)", "#6B6B6B", "status-dead"],
];

const SHADOWS: Array<[string, string]> = [
  ["neonPurple", "shadow-neonPurple"],
  ["neonPink", "shadow-neonPink"],
  ["neonAqua", "shadow-neonAqua"],
  ["neonAmber", "shadow-neonAmber"],
  ["neonTeal", "shadow-neonTeal"],
  ["softPurple", "shadow-softPurple"],
  ["hardEdge", "shadow-hardEdge"],
];

const SPACES = [4, 8, 12, 16, 24, 32, 48];

function Swatch({ name, hex, token }: { name: string; hex: string; token: string }) {
  const [copied, setCopied] = React.useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(hex);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };
  return (
    <button
      onClick={copy}
      data-testid={`next-swatch-${token}`}
      className="group relative overflow-hidden rounded-xl2 border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-primary-glow/60"
    >
      <div
        className="mb-3 h-16 rounded-xl border border-white/10"
        style={{ background: hex }}
      />
      <div className="flex items-center justify-between">
        <span className="text-[11px] uppercase tracking-[0.22em] text-white/60">{name}</span>
        <span className="text-[11px] text-white/40">{copied ? "copied" : "click to copy"}</span>
      </div>
      <div className="mt-1 flex items-center justify-between">
        <code className="font-mono text-sm text-white">{hex}</code>
        <code className="text-[10px] text-primary-glow">{token}</code>
      </div>
    </button>
  );
}

function Section({ id, kicker, title, children }: { id: string; kicker: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="space-y-4 scroll-mt-24" data-testid={`next-brand-section-${id}`}>
      <div className="flex items-center gap-2">
        <Sparkles size={14} className="text-primary-glow" />
        <span className="text-[11px] uppercase tracking-[0.3em] text-primary-glow">{kicker}</span>
      </div>
      <h2 className="font-display text-3xl tracking-wider text-white">{title}</h2>
      {children}
    </section>
  );
}

export default function BrandKitEmbed() {
  const sections = [
    ["colours", "Colours"], ["typography", "Typography"],
    ["effects", "Effects"], ["spacing", "Spacing"],
    ["components", "Components"],
  ] as const;

  return (
    <div className="space-y-10 p-6" data-testid="next-brandkit-embed">
      {/* Hero */}
      <div className="rounded-xl3 border border-primary-glow/30 bg-gradient-to-br from-primary/10 to-background-deep p-8 shadow-softPurple">
        <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.3em] text-primary-glow">
          <Sparkles size={14} /> The brand kit
        </div>
        <h1 className="mt-3 font-display text-5xl tracking-widest text-white md:text-6xl">
          VIBE<span className="text-accent-pink">2</span>NITE
        </h1>
        <p className="mt-2 text-sm uppercase tracking-[0.3em] text-white/70">
          Find the vibe. <span className="text-accent-pink">Go tonight.</span>
        </p>
        <div className="mt-6 flex flex-wrap gap-2">
          {sections.map(([id, label]) => (
            <a key={id} href={`#${id}`}>
              <Chip tone="neutral">{label}</Chip>
            </a>
          ))}
        </div>
      </div>

      {/* Colours */}
      <Section id="colours" kicker="01 — tokens" title="COLOUR STYLES">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
          {COLORS.map(([n, h, t]) => (
            <Swatch key={t} name={n} hex={h} token={t} />
          ))}
        </div>
      </Section>

      {/* Typography */}
      <Section id="typography" kicker="02 — type" title="TYPOGRAPHY">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-6">
            <p className="text-[11px] uppercase tracking-[0.28em] text-white/55">Display — Bebas Neue</p>
            <p className="mt-2 font-display text-6xl tracking-wider text-white">TONIGHT.</p>
            <p className="mt-1 font-display text-3xl tracking-wider text-primary-glow">HEADLINES.</p>
          </div>
          <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-6">
            <p className="text-[11px] uppercase tracking-[0.28em] text-white/55">Body — Outfit / Inter</p>
            <p className="mt-2 text-lg text-white">
              The weighted Vibe Score ranks venues live, every minute.
            </p>
            <p className="mt-3 text-sm text-white/60">
              Captions, labels, and tabular text. Monospace for scores & coordinates.
            </p>
          </div>
        </div>
      </Section>

      {/* Effects */}
      <Section id="effects" kicker="03 — glow" title="EFFECTS & SHADOWS">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {SHADOWS.map(([name, cls]) => (
            <div
              key={name}
              className={cn("flex h-24 items-center justify-center rounded-xl2 border border-white/10 bg-white/[0.03] text-xs uppercase tracking-[0.22em] text-white/80", cls)}
              data-testid={`next-shadow-${name}`}
            >
              {name}
            </div>
          ))}
        </div>
      </Section>

      {/* Spacing */}
      <Section id="spacing" kicker="04 — grid" title="SPACING SCALE">
        <div className="flex flex-wrap items-end gap-3">
          {SPACES.map((s) => (
            <div key={s} className="flex flex-col items-center gap-1 text-[10px] uppercase tracking-[0.2em] text-white/55">
              <div className="w-10 rounded bg-gradient-to-br from-primary to-accent-pink" style={{ height: s }} />
              {s}px
            </div>
          ))}
        </div>
      </Section>

      {/* Components */}
      <Section id="components" kicker="05 — atoms" title="COMPONENTS">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
            <p className="mb-3 text-[11px] uppercase tracking-[0.28em] text-white/55">Buttons</p>
            <div className="flex flex-wrap gap-2">
              <Button variant="primary" size="md">Primary</Button>
              <Button variant="pink" size="md">Pink</Button>
              <Button variant="aqua" size="md">Aqua</Button>
              <Button variant="secondary" size="md">Secondary</Button>
              <Button variant="ghost" size="md">Ghost</Button>
            </div>
          </div>
          <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
            <p className="mb-3 text-[11px] uppercase tracking-[0.28em] text-white/55">Chips</p>
            <div className="flex flex-wrap gap-2">
              <Chip tone="neutral">Neutral</Chip>
              <Chip tone="purple">Purple</Chip>
              <Chip tone="pink">Pink</Chip>
              <Chip tone="aqua">Aqua</Chip>
              <Chip tone="amber">Busy</Chip>
              <Chip tone="lavender">Medium</Chip>
            </div>
          </div>
        </div>
      </Section>

      <p className="pb-8 text-center text-[10px] uppercase tracking-[0.3em] text-white/35">
        Brand Kit · read-only · admin surface
      </p>
    </div>
  );
}
