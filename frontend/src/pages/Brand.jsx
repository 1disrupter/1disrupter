import React, { useState } from "react";
import {
  Navbar, Footer, Logo, LogoMark,
  Button, IconButton, Chip, BannerChip,
  VibeScoreBadge, StatusIndicator,
  VenueHeroCard, VenueListItem, Modal, useToast,
  Input, SearchBar, Select, Slider,
  LoadingScreen, VenueCardSkeleton, EmptyState, ErrorState,
  Pagination, MapPinIcon,
} from "@/components/v2n";
import { Search, Sparkles, Music2, Users } from "lucide-react";

const COLORS = [
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

const SHADOWS = [
  ["neonPurple", "shadow-neonPurple"],
  ["neonPink", "shadow-neonPink"],
  ["neonAqua", "shadow-neonAqua"],
  ["neonAmber", "shadow-neonAmber"],
  ["neonTeal", "shadow-neonTeal"],
  ["softPurple", "shadow-softPurple"],
  ["hardEdge", "shadow-hardEdge"],
];

const SPACES = [4, 8, 12, 16, 24, 32, 48];

const SAMPLE_VENUE = {
  venue: { id: "sample", name: "La Terraza Rooftop", category: "club", latitude: 40.73, longitude: -73.99 },
  vibe: {
    venue_id: "sample", vibe_score: 9.2, crowd_level: "busy",
    last_updated: new Date().toISOString(),
    signals: { manual_score: 9.2, social_activity: 8.8, user_votes: 8.5, time_prediction: 9.0, venue_boost: 7.5 },
  },
  distance_km: 0.5,
};

function Swatch({ name, hex, token }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(hex);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };
  return (
    <button
      onClick={copy}
      data-testid={`swatch-${token}`}
      className="group relative overflow-hidden rounded-xl2 border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-primary-glow/60"
    >
      <div
        className="mb-3 h-16 w-full rounded-lg ring-1 ring-white/10"
        style={{ background: hex, boxShadow: `0 0 24px ${hex}33` }}
      />
      <div className="text-xs uppercase tracking-[0.22em] text-white/55">{name}</div>
      <div className="mt-1 flex items-center justify-between font-mono text-sm text-white">
        <span>{hex}</span>
        <span className="text-[10px] text-white/50">{copied ? "Copied!" : "Click to copy"}</span>
      </div>
      <div className="mt-1 font-mono text-[10px] text-primary-glow">{token}</div>
    </button>
  );
}

function Section({ id, title, kicker, children }) {
  return (
    <section id={id} className="mb-16 scroll-mt-24">
      <div className="mb-6">
        {kicker && (
          <div className="mb-2 inline-flex items-center gap-1.5 text-[11px] uppercase tracking-[0.3em] text-primary-glow">
            <Sparkles size={12} /> {kicker}
          </div>
        )}
        <h2 className="font-display text-4xl tracking-wider text-white md:text-5xl">{title}</h2>
      </div>
      {children}
    </section>
  );
}

const SAMPLE_CODE = `// Tailwind theme — paste into tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary:    { DEFAULT: "#8A2BE2", glow: "#B15CFF" },
        accent:     { pink: "#FF2EC4", magenta: "#FF4EDB" },
        background: { dark: "#0A0A12", deep: "#05050A" },
        status:     { busy: "#FF9A1F", medium: "#C7A7FF", dead: "#6B6B6B" },
        glow:       { aqua: "#00F5FF", teal: "#00D1C7" },
      },
      boxShadow: {
        neonPurple: "0 0 12px #8A2BE2, 0 0 24px #8A2BE2",
        neonPink:   "0 0 12px #FF2EC4, 0 0 24px #FF2EC4",
        neonAqua:   "0 0 12px #00F5FF, 0 0 24px #00F5FF",
      },
      fontFamily: { vibe: ["Inter", "Outfit", "sans-serif"] },
    },
  },
};`;

export default function Brand({ embedded = false }) {
  const toast = useToast();
  const [modal, setModal] = useState(false);
  const [search, setSearch] = useState("");

  return (
    <div>
      {!embedded && <Navbar />}

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-4 pt-10 md:pt-16">
        <div className="flex items-end justify-between gap-6 border-b border-white/10 pb-8">
          <div>
            <div className="mb-3 inline-flex items-center gap-1.5 text-[11px] uppercase tracking-[0.3em] text-primary-glow">
              <Sparkles size={12} /> The brand kit
            </div>
            <h1 className="font-display text-6xl tracking-wider text-white md:text-8xl">
              VIBE<span className="bg-gradient-to-b from-primary-glow to-accent-pink bg-clip-text text-transparent">2</span>NITE
            </h1>
            <p className="mt-2 text-sm uppercase tracking-[0.3em] text-white/60">
              Find the vibe. <span className="text-accent-pink">Go tonight.</span>
            </p>
          </div>
          <div className="hidden text-right text-xs uppercase tracking-[0.3em] text-white/45 md:block">
            Design tokens · Components<br />Production-ready
          </div>
        </div>

        {/* Table of contents */}
        <nav className="my-8 grid grid-cols-2 gap-2 md:grid-cols-4">
          {[
            ["#colors", "Colours"],
            ["#type", "Typography"],
            ["#effects", "Effects"],
            ["#spacing", "Spacing"],
            ["#logos", "Logos"],
            ["#buttons", "Buttons"],
            ["#cards", "Cards"],
            ["#controls", "Controls"],
            ["#feedback", "Feedback"],
            ["#tailwind", "Tailwind"],
          ].map(([href, label]) => (
            <a
              key={href}
              href={href}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-center text-xs uppercase tracking-[0.22em] text-white/65 transition hover:border-primary-glow/60 hover:text-white"
            >
              {label}
            </a>
          ))}
        </nav>
      </section>

      <div className="mx-auto max-w-6xl px-4">
        {/* COLOURS */}
        <Section id="colors" title="Colour Styles" kicker="01 · Tokens">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
            {COLORS.map(([name, hex, token]) => (
              <Swatch key={token} name={name} hex={hex} token={token} />
            ))}
          </div>
        </Section>

        {/* TYPOGRAPHY */}
        <Section id="type" title="Typography" kicker="02 · Styles">
          <div className="grid gap-4 rounded-xl3 border border-white/10 bg-white/[0.02] p-6 md:grid-cols-2">
            <div>
              <p className="mb-2 text-[11px] uppercase tracking-[0.3em] text-white/50">Display — Bebas Neue</p>
              <p className="font-display text-7xl tracking-wider text-white">VIBE2NITE</p>
              <p className="font-display text-4xl tracking-wider text-white/80">Heading XL</p>
              <p className="font-display text-3xl tracking-wider text-white/70">Heading L</p>
              <p className="font-display text-2xl tracking-wider text-white/60">Heading M</p>
            </div>
            <div className="space-y-3">
              <p className="mb-2 text-[11px] uppercase tracking-[0.3em] text-white/50">Body — Outfit / Inter</p>
              <p className="text-base text-white">
                Body M · The best nightlife spots, scored in real time. Bars, clubs, live music — tuned to tonight.
              </p>
              <p className="text-sm text-white/75">Body S · Used for secondary copy, helper text and captions.</p>
              <p className="text-[11px] uppercase tracking-[0.28em] text-white/55">Label XS · Pills, chips, section headers</p>
              <pre className="overflow-x-auto rounded-lg bg-[#0A0418] p-3 text-xs text-primary-glow">{`font-family: "Outfit", "Inter", sans-serif;\nfont-family: "Bebas Neue", display;`}</pre>
            </div>
          </div>
        </Section>

        {/* LOGOS */}
        <Section id="logos" title="Logo Assets" kicker="03 · Marks">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex flex-col items-center justify-center rounded-xl3 border border-white/10 bg-background-dark p-8">
              <LogoMark size={64} />
              <p className="mt-4 text-xs uppercase tracking-[0.28em] text-white/55">Icon only (pin + V)</p>
            </div>
            <div className="flex flex-col items-center justify-center rounded-xl3 border border-white/10 bg-background-dark p-8">
              <Logo size="lg" />
              <p className="mt-4 text-xs uppercase tracking-[0.28em] text-white/55">Wordmark · Dark (default)</p>
            </div>
            <div className="flex flex-col items-center justify-center rounded-xl3 border border-white/10 bg-white p-8">
              <Logo size="lg" variant="dark" />
              <p className="mt-4 text-xs uppercase tracking-[0.28em] text-background-deep/70">Wordmark · Light bg</p>
            </div>
          </div>
        </Section>

        {/* EFFECTS */}
        <Section id="effects" title="Effect Styles" kicker="04 · Glows">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {SHADOWS.map(([name, cls]) => (
              <div
                key={name}
                data-testid={`shadow-${name}`}
                className={`flex h-28 items-center justify-center rounded-xl2 border border-white/10 bg-background-dark ${cls}`}
              >
                <span className="font-mono text-xs text-white/80">{name}</span>
              </div>
            ))}
          </div>
        </Section>

        {/* SPACING */}
        <Section id="spacing" title="Spacing & Grid" kicker="05 · Scale">
          <div className="flex flex-wrap items-end gap-5 rounded-xl3 border border-white/10 bg-white/[0.02] p-6">
            {SPACES.map((s) => (
              <div key={s} className="flex flex-col items-center gap-2">
                <div
                  className="rounded-md bg-gradient-to-br from-primary to-accent-pink shadow-softPurple"
                  style={{ width: s, height: s }}
                />
                <span className="font-mono text-xs text-white/70">{s}px</span>
              </div>
            ))}
          </div>
        </Section>

        {/* BUTTONS */}
        <Section id="buttons" title="Buttons" kicker="06 · Components">
          <div className="space-y-5 rounded-xl3 border border-white/10 bg-white/[0.02] p-6">
            <div className="flex flex-wrap gap-3">
              <Button variant="primary">Primary</Button>
              <Button variant="pink">Accent Pink</Button>
              <Button variant="aqua">Aqua Glow</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger">Danger</Button>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button size="sm">Small</Button>
              <Button size="md">Medium</Button>
              <Button size="lg">Large</Button>
              <Button loading>Loading</Button>
              <Button disabled>Disabled</Button>
              <IconButton><Search size={16} /></IconButton>
            </div>
            <div className="flex flex-wrap gap-2">
              <Chip tone="purple">Purple</Chip>
              <Chip tone="pink">Pink</Chip>
              <Chip tone="aqua">Aqua</Chip>
              <Chip tone="amber">Amber</Chip>
              <Chip tone="lavender">Lavender</Chip>
              <Chip tone="neutral">Neutral</Chip>
              <BannerChip label="BEST OVERALL" tone="purple" />
              <BannerChip label="LIVE MUSIC" tone="pink" />
              <BannerChip label="HIDDEN GEM" tone="aqua" />
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <StatusIndicator status="packed" icon={<Users size={14} />} label="Packed" />
              <StatusIndicator status="busy" icon={<Users size={14} />} />
              <StatusIndicator status="medium" />
              <StatusIndicator status="dead" />
              <StatusIndicator status="locals" icon={<Music2 size={14} />} label="Live Band" />
              <VibeScoreBadge score={9.2} size="md" />
              <MapPinIcon tone="purple" />
              <MapPinIcon tone="pink" />
              <MapPinIcon tone="aqua" />
              <MapPinIcon tone="amber" />
            </div>
          </div>
        </Section>

        {/* CARDS */}
        <Section id="cards" title="Cards" kicker="07 · Layouts">
          <div className="grid gap-5 md:grid-cols-3">
            <VenueHeroCard slot="best_overall" data={SAMPLE_VENUE} />
            <VenueHeroCard
              slot="live_music"
              data={{ ...SAMPLE_VENUE, venue: { ...SAMPLE_VENUE.venue, name: "El Pimpi Bar", category: "live_music" }, vibe: { ...SAMPLE_VENUE.vibe, vibe_score: 8.7 }, distance_km: 0.3 }}
            />
            <VenueHeroCard
              slot="hidden_gem"
              data={{ ...SAMPLE_VENUE, venue: { ...SAMPLE_VENUE.venue, name: "Local Tapas Spot", category: "bar" }, vibe: { ...SAMPLE_VENUE.vibe, vibe_score: 8.4 }, distance_km: 0.7 }}
            />
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            <VenueListItem data={SAMPLE_VENUE} />
            <VenueListItem data={{ ...SAMPLE_VENUE, venue: { ...SAMPLE_VENUE.venue, name: "Basement 77" }, vibe: { ...SAMPLE_VENUE.vibe, vibe_score: 4.2 } }} />
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <VenueCardSkeleton />
            <VenueCardSkeleton />
            <VenueCardSkeleton />
          </div>
        </Section>

        {/* CONTROLS */}
        <Section id="controls" title="Inputs & Controls" kicker="08 · Forms">
          <div className="grid gap-6 rounded-xl3 border border-white/10 bg-white/[0.02] p-6 md:grid-cols-2">
            <div className="space-y-4">
              <SearchBar value={search} onChange={setSearch} />
              <Input label="Venue name" placeholder="La Terraza Rooftop" />
              <Input label="Email" placeholder="you@vibe.night" leftIcon={<Sparkles size={14} />} />
              <Input label="With error" placeholder="Wrong value" error="Required field" />
              <Select
                label="Category"
                value="club"
                options={[
                  { value: "bar", label: "Bar" },
                  { value: "club", label: "Club" },
                  { value: "live_music", label: "Live Music" },
                ]}
                onChange={() => {}}
              />
            </div>
            <div className="space-y-4">
              <Slider label="Manual Score" value={7.5} onChange={() => {}} />
              <Slider label="Social Activity" value={5.2} onChange={() => {}} />
              <Slider label="Venue Boost" value={3.8} onChange={() => {}} />
              <div className="flex flex-wrap gap-2">
                <Button variant="primary" onClick={() => toast.success("That's the vibe.")}>Toast success</Button>
                <Button variant="pink" onClick={() => toast.error("Something went sideways.")}>Toast error</Button>
                <Button variant="secondary" onClick={() => toast.info("FYI — 3 new spots.")}>Toast info</Button>
                <Button variant="aqua" onClick={() => setModal(true)}>Open modal</Button>
              </div>
              <Pagination page={2} totalPages={5} onChange={() => {}} />
            </div>
          </div>
        </Section>

        {/* FEEDBACK STATES */}
        <Section id="feedback" title="Feedback States" kicker="09 · States">
          <div className="grid gap-5 md:grid-cols-3">
            <EmptyState />
            <ErrorState message="Couldn't fetch the vibe feed." onRetry={() => {}} />
            <div className="rounded-xl3 border border-white/10 bg-white/[0.02] p-4">
              <LoadingScreen label="Loading preview" />
            </div>
          </div>
        </Section>

        {/* TAILWIND */}
        <Section id="tailwind" title="Tailwind Theme" kicker="10 · Config">
          <pre className="overflow-x-auto rounded-xl2 border border-white/10 bg-[#0A0418] p-5 text-xs leading-6 text-primary-glow">
{SAMPLE_CODE}
          </pre>
        </Section>
      </div>

      <Modal
        open={modal}
        onClose={() => setModal(false)}
        title="VIBE CHECK"
        footer={
          <>
            <Button variant="secondary" onClick={() => setModal(false)}>Cancel</Button>
            <Button variant="pink" onClick={() => { toast.success("Locked in."); setModal(false); }}>
              Lock it in
            </Button>
          </>
        }
      >
        <p className="text-sm text-white/75">
          Modals use <code className="text-primary-glow">shadow-neonPurple</code> glow, rounded-xl3, and animated entrance.
          Close with the top-right button, clicking outside, or pressing <kbd>Esc</kbd>.
        </p>
      </Modal>

      <EmbeddedFooter embedded={embedded} />
    </div>
  );
}

function EmbeddedFooter({ embedded }) {
  if (embedded) return null;
  return <Footer />;
}
