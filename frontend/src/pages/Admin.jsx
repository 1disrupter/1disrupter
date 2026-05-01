
import { useToast } from "../components/v2n";
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { updateVenue } from "../lib/api";
import {
  BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend,
} from "recharts";
import {
  LogOut, Plus, TrendingUp, Database, Sliders, LogIn, Lock, RefreshCw,
  Activity, Radar, CalendarClock, Clock, ThumbsUp,
  TrendingDown, Minus, Zap, AlertTriangle, Gem, Music2,
  Palette, Settings as SettingsIcon,
  ShieldCheck,
} from "lucide-react";
import {
  Navbar, Footer, Logo, LogoMark,
  Button, IconButton, Chip, BannerChip,
  Input, SearchBar, Select, Slider,
  Modal, useToast,
  LoadingScreen, EmptyState, ErrorState,
  VibeScoreBadge, StatusIndicator,
} from "../components/v2n";
import { cx } from "../lib/cx";
import {
  listAdminVenues, createVenue, updateSignals, triggerSignalRefresh,
  getForecast, getTouristFlags, getLiveMusic,
  listClaims, reviewClaim, getProviderStatus, getRecentWebhooks,
  adminExpireOwnership,
} from "../lib/api";

const ADMIN_CREDS = { user: "vibe2nite", pass: "nightowl" };
const STORAGE_KEY = "v2n_admin_session";

// ---------------------------------------------------------------------------
// Login
// ---------------------------------------------------------------------------
function Login({ onSuccess }) {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [err, setErr] = useState("");
  const toast = useToast();

  const submit = (e) => {
    e.preventDefault();
    if (user === ADMIN_CREDS.user && pass === ADMIN_CREDS.pass) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ user, t: Date.now() }));
      toast.success("Welcome back, curator.");
      onSuccess?.();
    } else {
      setErr("Invalid credentials");
    }
  };

  return (
    <div>
      <Navbar />
      <div className="mx-auto flex min-h-[70vh] max-w-md items-center justify-center px-4">
        <form
          onSubmit={submit}
          data-testid="admin-login-form"
          className="w-full rounded-xl3 border border-primary-glow/30 bg-background-dark/95 p-8 shadow-softPurple"
        >
          <div className="mb-6 flex flex-col items-center gap-3 text-center">
            <LogoMark size={56} />
            <Logo size="md" />
            <p className="text-xs uppercase tracking-[0.3em] text-white/55">Admin Console</p>
          </div>
          <div className="space-y-4">
            <Input
              label="Username"
              value={user}
              onChange={(e) => setUser(e.target.value)}
              placeholder="vibe2nite"
              leftIcon={<LogIn size={14} />}
              autoFocus
              data-testid="login-username"
            />
            <Input
              label="Password"
              type="password"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
              placeholder="••••••••"
              leftIcon={<Lock size={14} />}
              error={err || undefined}
              data-testid="login-password"
            />
            <Button variant="primary" size="lg" className="w-full" type="submit" data-testid="login-submit">
              Enter the Vibe
            </Button>
            <p className="text-center text-[11px] text-white/40">
              Hint: <code className="text-primary-glow">vibe2nite</code> / <code className="text-primary-glow">nightowl</code>
            </p>
          </div>
        </form>
      </div>
      <Footer />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------
function Sidebar({ active, onChange, onLogout }) {
  const items = [
    { key: "overview", label: "Overview", icon: <TrendingUp size={16} /> },
    { key: "venues", label: "Venues", icon: <Database size={16} /> },
    { key: "signals", label: "Signals", icon: <Sliders size={16} /> },
    { key: "claims", label: "Claims", icon: <ShieldCheck size={16} /> },
    { key: "settings", label: "Settings", icon: <SettingsIcon size={16} /> },
  ];
  return (
    <aside className="hidden w-60 shrink-0 border-r border-white/5 bg-background-deep/60 p-4 md:block">
      <div className="mb-6 flex items-center gap-2 px-2">
        <LogoMark size={22} />
        <Logo size="xs" />
      </div>
      <nav className="flex flex-col gap-1">
        {items.map((it) => (
          <button
            key={it.key}
            onClick={() => onChange(it.key)}
            data-testid={`sidebar-${it.key}`}
            className={cx(
              "flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm transition",
              active === it.key
                ? "bg-primary/20 text-white border border-primary-glow/50 shadow-[0_0_16px_-4px_rgba(177,92,255,0.7)]"
                : "text-white/60 hover:bg-white/5 hover:text-white border border-transparent"
            )}
          >
            {it.icon}
            {it.label}
          </button>
        ))}
      </nav>
      <div className="mt-6 border-t border-white/5 pt-4">
        <Button variant="ghost" size="sm" leftIcon={<LogOut size={14} />} onClick={onLogout} data-testid="sidebar-logout">
          Log out
        </Button>
      </div>
    </aside>
  );
}

// ---------------------------------------------------------------------------
// Overview (charts)
// ---------------------------------------------------------------------------
function OverviewPanel({ venues }) {
  // Wrap in useMemo so downstream useMemos get a stable reference-equal
  // dep when `venues` hasn't changed (otherwise a fresh array is created
  // on every render and downstream charts recompute unnecessarily).
  const safeVenues = useMemo(
    () => (Array.isArray(venues) ? venues : []),
    [venues]
  );

  const byCategory = useMemo(() => {
    const m = {};
    safeVenues.forEach((x) => {
      m[x.venue.category] = (m[x.venue.category] || 0) + 1;
    });
    return Object.entries(m).map(([name, value]) => ({ name, value }));
  }, [safeVenues]);

  const byCrowd = useMemo(() => {
    const m = { busy: 0, medium: 0, dead: 0 };
    safeVenues.forEach((x) => { m[x.vibe.crowd_level] = (m[x.vibe.crowd_level] || 0) + 1; });
    return Object.entries(m).map(([name, value]) => ({ name, value }));
  }, [safeVenues]);

  const topScores = useMemo(
    () => [...safeVenues].sort((a, b) => b.vibe.vibe_score - a.vibe.vibe_score).slice(0, 8)
      .map((x) => ({ name: x.venue.name, score: x.vibe.vibe_score })),
    [safeVenues]
  );

  const PIE_COLORS = ["#8A2BE2", "#FF2EC4", "#00F5FF", "#FF9A1F", "#C7A7FF"];

  const avgSignals = useMemo(() => {
    if (!safeVenues.length) return [];
    const keys = ["manual_score", "social_activity", "user_votes", "time_prediction", "venue_boost"];
    return keys.map((k) => ({
      name: k.replace("_", " "),
      value: Number((safeVenues.reduce((s, v) => s + (v.vibe.signals[k] || 0), 0) / safeVenues.length).toFixed(2)),
    }));
  }, [safeVenues]);

  const stats = [
    { label: "Venues tracked", value: safeVenues.length, tone: "purple" },
    { label: "Average score", value: safeVenues.length ? (safeVenues.reduce((s, v) => s + v.vibe.vibe_score, 0) / safeVenues.length).toFixed(2) : "0.0", tone: "pink" },
    { label: "Currently busy", value: safeVenues.filter((v) => v.vibe.crowd_level === "busy").length, tone: "aqua" },
    { label: "Hidden gems", value: safeVenues.filter((v) => v.vibe.vibe_score < 5).length, tone: "amber" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {stats.map((s) => {
          const tone = {
            purple: "from-primary/25 to-primary-glow/10 border-primary-glow/40",
            pink: "from-accent-pink/25 to-accent-magenta/10 border-accent-pink/40",
            aqua: "from-glow-aqua/25 to-glow-teal/10 border-glow-aqua/40",
            amber: "from-status-busy/25 to-status-busy/5 border-status-busy/40",
          }[s.tone];
          return (
            <div
              key={s.label}
              data-testid={`stat-${s.label}`}
              className={cx(
                "rounded-xl2 border bg-gradient-to-br p-4",
                tone
              )}
            >
              <p className="text-[11px] uppercase tracking-[0.22em] text-white/60">{s.label}</p>
              <p className="mt-2 font-display text-4xl tracking-wider text-white">{s.value}</p>
            </div>
          );
        })}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
          <p className="mb-3 text-[11px] uppercase tracking-[0.28em] text-white/55">Top scores</p>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={topScores} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid stroke="#1c1330" vertical={false} />
                <XAxis dataKey="name" stroke="#6f5a94" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={60} />
                <YAxis stroke="#6f5a94" tick={{ fontSize: 10 }} domain={[0, 10]} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
                <Bar dataKey="score" fill="#B15CFF" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
          <p className="mb-3 text-[11px] uppercase tracking-[0.28em] text-white/55">Average signals</p>
          <div className="h-64">
            <ResponsiveContainer>
              <LineChart data={avgSignals} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid stroke="#1c1330" vertical={false} />
                <XAxis dataKey="name" stroke="#6f5a94" tick={{ fontSize: 10 }} />
                <YAxis stroke="#6f5a94" tick={{ fontSize: 10 }} domain={[0, 10]} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
                <Line type="monotone" dataKey="value" stroke="#FF2EC4" strokeWidth={3} dot={{ r: 4, fill: "#00F5FF" }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
          <p className="mb-3 text-[11px] uppercase tracking-[0.28em] text-white/55">Category mix</p>
          <div className="h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={byCategory} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={4}>
                  {byCategory.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Legend wrapperStyle={{ color: "#fff", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.2em" }} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
          <p className="mb-3 text-[11px] uppercase tracking-[0.28em] text-white/55">Crowd distribution</p>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={byCrowd} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid stroke="#1c1330" vertical={false} />
                <XAxis dataKey="name" stroke="#6f5a94" tick={{ fontSize: 11 }} />
                <YAxis stroke="#6f5a94" tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {byCrowd.map((d, i) => (
                    <Cell
                      key={i}
                      fill={d.name === "busy" ? "#FF9A1F" : d.name === "medium" ? "#C7A7FF" : "#6B6B6B"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Venues table
// ---------------------------------------------------------------------------
function VenuesPanel({ venues, onAdd, onInspect, query, setQuery }) {
  const toast = useToast();
  const [verifiedOnly, setVerifiedOnly] = React.useState(false);
  const safeVenues = Array.isArray(venues) ? venues : [];
  const filtered = safeVenues.filter((v) =>
    v.venue.name.toLowerCase().includes(query.toLowerCase()) &&
    (!verifiedOnly || v.venue.is_verified)
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <SearchBar value={query} onChange={setQuery} placeholder="Search venues…" className="md:max-w-sm" />
        <div className="flex items-center gap-2">
          <button
            onClick={() => setVerifiedOnly((v) => !v)}
            data-testid="admin-verified-filter"
            className={cx(
              "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs uppercase tracking-[0.22em] transition",
              verifiedOnly
                ? "border-glow-aqua/60 bg-glow-aqua/10 text-glow-aqua shadow-neonAqua"
                : "border-white/10 text-white/55 hover:text-white hover:bg-white/5"
            )}
          >
            Verified only
          </button>
          <Button variant="pink" leftIcon={<Plus size={14} />} onClick={onAdd} data-testid="admin-add-venue">
            Add venue
          </Button>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl2 border border-white/10">
        <table className="min-w-full text-sm">
          <thead className="bg-white/[0.03] text-left text-[11px] uppercase tracking-[0.22em] text-white/55">
            <tr>
              <th className="p-3">Name</th>
              <th className="p-3">Category</th>
              <th className="p-3">Score</th>
              <th className="p-3">Crowd</th>
              <th className="p-3">Lat / Lng</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((x, i) => (
              <tr
                key={x.venue.id}
                data-testid={`venue-row-${x.venue.id}`}
                className={cx("border-t border-white/5", i % 2 ? "bg-white/[0.01]" : "")}
              >
                <td className="p-3 font-semibold text-white">
                  <span className="inline-flex items-center gap-2">
                    {x.venue.name}
                    {x.venue.is_verified && (
                      <span
                        data-testid={`admin-verified-${x.venue.id}`}
                        title="Verified venue"
                        className="inline-flex items-center gap-1 rounded-full border border-glow-aqua/50 bg-glow-aqua/10 px-1.5 py-0.5 text-[9px] uppercase tracking-[0.2em] text-glow-aqua"
                      >
                        ✓ verified
                      </span>
                    )}
                  </span>
                </td>
                <td className="p-3">
                  <Chip tone={x.venue.category === "live_music" ? "pink" : x.venue.category === "club" ? "purple" : "aqua"}>
                    {x.venue.category.replace("_", " ")}
                  </Chip>
                </td>
                <td className="p-3">
                  <span className="font-mono text-primary-glow">{x.vibe.vibe_score.toFixed(2)}</span>
                </td>
                <td className="p-3">
                  <StatusIndicator status={x.vibe.crowd_level} />
                </td>
                <td className="p-3 font-mono text-xs text-white/55">
                  {x.venue.latitude.toFixed(3)}, {x.venue.longitude.toFixed(3)}
                </td>
                <td className="p-3 text-right">
                  <div className="flex justify-end gap-2">
                    {x.venue.is_verified && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={async () => {
                          if (!window.confirm(`Expire ownership for "${x.venue.name}"?`)) return;
                          try {
                            const r = await adminExpireOwnership(x.venue.id, "admin");
                            toast.success(`Ownership expired (${r.affected} claim${r.affected === 1 ? "" : "s"}).`);
                          } catch (e) {
                            toast.error(e.response?.data?.detail || "Couldn't expire");
                          }
                        }}
                        data-testid={`expire-${x.venue.id}`}
                      >
                        Expire
                      </Button>
                    )}
                    <Button size="sm" variant="secondary" onClick={() => onInspect(x)} data-testid={`inspect-${x.venue.id}`}>
                      Inspect
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
            {!filtered.length && (
              <tr>
                <td colSpan={6} className="p-10">
                  <EmptyState title="No venues match" hint="Try a different query." />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Venue intelligence (forecast + tourist flag + live-music)
// ---------------------------------------------------------------------------
const TREND_META = {
  rising:  { icon: <TrendingUp size={14} />,   tone: "text-glow-aqua",   label: "Rising" },
  peaking: { icon: <Zap size={14} />,          tone: "text-accent-pink", label: "Peaking" },
  falling: { icon: <TrendingDown size={14} />, tone: "text-status-dead", label: "Falling" },
  steady:  { icon: <Minus size={14} />,        tone: "text-white/70",    label: "Steady" },
};
const LABEL_META = {
  tourist_trap: { icon: <AlertTriangle size={14} />, tone: "text-status-busy",    label: "Tourist trap" },
  local_gem:    { icon: <Gem size={14} />,           tone: "text-glow-aqua",      label: "Local gem" },
  neutral:      { icon: <Minus size={14} />,         tone: "text-white/65",       label: "Neutral" },
};

function VenueIntelligencePanel({ venueId }) {
  const [data, setData] = React.useState({ loading: true });
  React.useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [forecast, flags, live] = await Promise.all([
          getForecast(venueId),
          getTouristFlags(),
          getLiveMusic(true),  // include all so we can look up our venue
        ]);
        if (!alive) return;
        const flagItems = Array.isArray(flags?.items) ? flags.items : [];
        const liveItems = Array.isArray(live?.items) ? live.items : [];
        const myFlag = flagItems.find((x) => x.venue_id === venueId);
        const myLive = liveItems.find((x) => x.venue_id === venueId);
        setData({ loading: false, forecast, flag: myFlag, live: myLive });
      } catch (e) {
        if (alive) setData({ loading: false, error: e.message });
      }
    })();
    return () => { alive = false; };
  }, [venueId]);

  if (data.loading) {
    return (
      <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4 text-xs text-white/55">
        Loading intelligence…
      </div>
    );
  }

  const trend = TREND_META[data.forecast?.trend] || TREND_META.steady;
  const lbl = LABEL_META[data.flag?.label] || LABEL_META.neutral;
  const live = data.live;

  return (
    <div
      data-testid="venue-intelligence-panel"
      className="space-y-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-4"
    >
      <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
        <Activity size={12} /> Venue intelligence
      </div>
      <div className="grid grid-cols-3 gap-3 text-xs">
        <div>
          <p className="mb-1 text-[10px] uppercase tracking-[0.22em] text-white/45">Forecast</p>
          <p className={cx("flex items-center gap-1.5 font-semibold", trend.tone)} data-testid="intel-forecast">
            {trend.icon} {trend.label}
          </p>
          <p className="mt-0.5 font-mono text-[10px] text-white/45">
            Δ next hr {data.forecast?.delta_next_hour?.toFixed(2) ?? "0.00"}
          </p>
        </div>
        <div>
          <p className="mb-1 text-[10px] uppercase tracking-[0.22em] text-white/45">Crowd type</p>
          <p className={cx("flex items-center gap-1.5 font-semibold", lbl.tone)} data-testid="intel-flag">
            {lbl.icon} {lbl.label}
          </p>
          {data.flag?.reason && (
            <p className="mt-0.5 text-[10px] text-white/45 line-clamp-2">{data.flag.reason}</p>
          )}
        </div>
        <div>
          <p className="mb-1 text-[10px] uppercase tracking-[0.22em] text-white/45">Live music</p>
          <p
            className={cx(
              "flex items-center gap-1.5 font-semibold",
              live?.live_music ? "text-accent-pink" : "text-white/55"
            )}
            data-testid="intel-live-music"
          >
            <Music2 size={14} />
            {live?.live_music ? "Likely tonight" : "Not tonight"}
          </p>
          <p className="mt-0.5 font-mono text-[10px] text-white/45">
            conf {Math.round((live?.confidence || 0) * 100)}%
          </p>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// External signals panel (read-only — fed by the background scheduler)
// ---------------------------------------------------------------------------
const SIGNAL_META = {
  google_score:     { label: "Google busyness",  icon: <Radar size={14} />,         tone: "text-primary-glow", bar: "bg-primary-glow" },
  social_score:     { label: "Social activity",  icon: <Activity size={14} />,      tone: "text-accent-pink",  bar: "bg-accent-pink" },
  event_score:      { label: "Live events",      icon: <CalendarClock size={14} />, tone: "text-status-busy",  bar: "bg-status-busy" },
  time_score:       { label: "Time pattern",     icon: <Clock size={14} />,         tone: "text-glow-aqua",    bar: "bg-glow-aqua" },
  user_votes_score: { label: "Recent votes",     icon: <ThumbsUp size={14} />,      tone: "text-status-medium",bar: "bg-status-medium" },
};

function ExternalSignalsPanel({ ext }) {
  if (!ext) {
    return (
      <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4 text-center text-xs text-white/55">
        Signal engine hasn't run for this venue yet. Wait a few seconds or trigger a refresh.
      </div>
    );
  }
  const when = ext.updated_at ? new Date(ext.updated_at).toLocaleTimeString() : "—";
  return (
    <div
      data-testid="external-signals-panel"
      className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4"
    >
      <div className="mb-3 flex items-center justify-between text-[11px] uppercase tracking-[0.28em]">
        <span className="flex items-center gap-1.5 text-primary-glow">
          <Activity size={12} /> Signal engine
        </span>
        <span className="text-white/45">updated {when}</span>
      </div>
      <ul className="space-y-2">
        {Object.entries(SIGNAL_META).map(([k, meta]) => {
          const v = Number(ext[k] ?? 0);
          const pct = Math.max(0, Math.min(100, (v / 10) * 100));
          return (
            <li key={k} data-testid={`ext-signal-${k}`} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className={cx("flex items-center gap-1.5", meta.tone)}>
                  {meta.icon} {meta.label}
                </span>
                <span className="font-mono text-white">{v.toFixed(2)}</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                <div
                  className={cx("h-full rounded-full transition-all", meta.bar)}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Signal inspector
// ---------------------------------------------------------------------------
function SignalInspector({ item, onClose, onSaved }) {
  const toast = useToast();
  const [signals, setSignals] = useState(item.vibe.signals);
  const [saving, setSaving] = useState(false);

  const localScore = useMemo(() => {
    const s = signals;
    const v = s.manual_score * 0.25 + s.social_activity * 0.25 + s.user_votes * 0.25 +
      s.time_prediction * 0.15 + s.venue_boost * 0.10;
    return Math.min(Math.max(v, 0), 10);
  }, [signals]);

  const save = async () => {
    setSaving(true);
    try {
      const res = await updateSignals(item.venue.id, {
        manual_score: signals.manual_score,
        social_activity: signals.social_activity,
        time_prediction: signals.time_prediction,
        venue_boost: signals.venue_boost,
      });
      toast.success(`Saved. New score: ${res.vibe_score.toFixed(2)}`);
      onSaved?.();
      onClose();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const fields = [
    ["manual_score", "Manual Score"],
    ["social_activity", "Social Activity"],
    ["time_prediction", "Time Prediction"],
    ["venue_boost", "Venue Boost"],
  ];

  return (
    <Modal
      open
      onClose={onClose}
      title={item.venue.name.toUpperCase()}
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="pink" loading={saving} onClick={save} data-testid="save-signals">
            Save signals
          </Button>
        </>
      }
    >
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          {fields.map(([k, label]) => (
            <Slider
              key={k}
              label={label}
              value={signals[k]}
              onChange={(v) => setSignals((s) => ({ ...s, [k]: v }))}
            />
          ))}
          <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-xs text-white/55">
            <p>
              <span className="text-white/75">user_votes</span> is driven by <code className="text-primary-glow">/feedback</code> and
              cannot be set manually. Current value: <b className="text-white">{signals.user_votes.toFixed(2)}</b>
            </p>
          </div>
        </div>
        <div className="space-y-4">
          <div className="flex flex-col items-center gap-4 rounded-xl2 border border-primary-glow/30 bg-primary/5 p-6">
            <BannerChip label="LIVE PREVIEW" tone="purple" />
            <VibeScoreBadge score={localScore} size="lg" />
            <StatusIndicator
              status={localScore >= 8 ? "busy" : localScore >= 5 ? "medium" : "dead"}
            />
            <p className="text-center text-[11px] uppercase tracking-[0.22em] text-white/55">
              Score is computed client-side the same way as the backend
            </p>
          </div>
          <ExternalSignalsPanel ext={item.external_signals} />
          <VenueIntelligencePanel venueId={item.venue.id} />
        </div>
      </div>
    </Modal>
  );
}

// ---------------------------------------------------------------------------
// Add venue modal
// ---------------------------------------------------------------------------
function AddVenueModal({ open, onClose, onCreated }) {
  const toast = useToast();
  const [form, setForm] = useState({
    name: "", category: "bar", latitude: 40.73, longitude: -73.99,
  });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (!form.name.trim()) {
      toast.error("Name required"); return;
    }
    setSaving(true);
    try {
      await createVenue({
        name: form.name.trim(),
        category: form.category,
        latitude: Number(form.latitude),
        longitude: Number(form.longitude),
      });
      toast.success(`${form.name} added.`);
      onCreated?.();
      onClose();
      setForm({ name: "", category: "bar", latitude: 40.73, longitude: -73.99 });
    } catch (e) {
      toast.error(e.response?.data?.detail || "Create failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="NEW VENUE"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="primary" loading={saving} onClick={save} data-testid="create-venue-submit">
            Create
          </Button>
        </>
      }
    >
      <div className="grid gap-4 md:grid-cols-2">
        <Input
          label="Name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          placeholder="La Terraza Rooftop"
          data-testid="new-venue-name"
        />
        <Select
          label="Category"
          value={form.category}
          onChange={(v) => setForm({ ...form, category: v })}
          options={[
            { value: "bar", label: "Bar" },
            { value: "club", label: "Club" },
            { value: "live_music", label: "Live Music" },
          ]}
        />
        <Input
          label="Latitude"
          type="number"
          step="0.0001"
          value={form.latitude}
          onChange={(e) => setForm({ ...form, latitude: e.target.value })}
        />
        <Input
          label="Longitude"
          type="number"
          step="0.0001"
          value={form.longitude}
          onChange={(e) => setForm({ ...form, longitude: e.target.value })}
        />
      </div>
    </Modal>
  );
}

// ---------------------------------------------------------------------------
// Signals panel (global logs)
// ---------------------------------------------------------------------------
function SignalsPanel({ venues, onInspect }) {
  const safeVenues = Array.isArray(venues) ? venues : [];
  const rows = [...safeVenues].sort((a, b) => new Date(b.vibe.last_updated) - new Date(a.vibe.last_updated));
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-white/55">
        <Sliders size={12} className="text-primary-glow" /> Recent signal activity
      </div>
      <div className="rounded-xl2 border border-white/10 bg-white/[0.02]">
        <ul>
          {rows.map((x) => (
            <li key={x.venue.id} className="flex items-center justify-between gap-3 border-b border-white/5 p-4 last:border-0">
              <div>
                <p className="font-semibold text-white">{x.venue.name}</p>
                <p className="font-mono text-[11px] text-white/45">
                  {new Date(x.vibe.last_updated).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <VibeScoreBadge score={x.vibe.vibe_score} size="sm" />
                <StatusIndicator status={x.vibe.crowd_level} />
                <Button size="sm" variant="secondary" onClick={() => onInspect(x)}>
                  Tune
                </Button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Claims panel (venue owner claims + provider status + webhook log)
// ---------------------------------------------------------------------------
function ClaimsPanel() {
  const toast = useToast();
  const [claims, setClaims] = React.useState([]);
  const [providers, setProviders] = React.useState([]);
  const [webhooks, setWebhooks] = React.useState({ configured: {}, recent: [] });
  const [filter, setFilter] = React.useState("");
  const [loading, setLoading] = React.useState(true);
  const [busyId, setBusyId] = React.useState(null);

  const load = React.useCallback(async () => {
    setLoading(true);
    try {
      const [c, p, w] = await Promise.all([
        listClaims(filter || undefined),
        getProviderStatus(),
        getRecentWebhooks(20),
      ]);
      setClaims(Array.isArray(c?.items) ? c.items : []);
      setProviders(Array.isArray(p?.providers) ? p.providers : []);
      setWebhooks({
        configured: (w && typeof w.configured === "object" && w.configured) ? w.configured : {},
        recent: Array.isArray(w?.recent) ? w.recent : [],
      });
    } catch (e) {
      toast.error(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [filter, toast]);

  React.useEffect(() => { load(); }, [load]);

  const review = async (id, action) => {
    setBusyId(id);
    try {
      await reviewClaim(id, action, "admin");
      toast.success(`Claim ${action === "approve" ? "approved" : "rejected"}.`);
      await load();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Review failed");
    } finally {
      setBusyId(null);
    }
  };

  const statusTone = (s) => ({
    pending: "neutral",
    email_sent: "purple",
    verified: "aqua",
    rejected: "pink",
  }[s] || "neutral");

  const safeClaims = Array.isArray(claims) ? claims : [];
  const safeProviders = Array.isArray(providers) ? providers : [];
  const safeConfigured = (webhooks && webhooks.configured) || {};
  const safeRecent = Array.isArray(webhooks?.recent) ? webhooks.recent : [];

  return (
    <div className="space-y-6" data-testid="admin-claims-panel">
      {/* Filter + refresh */}
      <div className="flex flex-wrap items-center gap-2">
        <Chip tone="purple">admin-only</Chip>
        {["", "pending", "email_sent", "verified", "rejected"].map((k) => (
          <button
            key={k || "all"}
            onClick={() => setFilter(k)}
            data-testid={`claims-filter-${k || "all"}`}
            className={cx(
              "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs uppercase tracking-[0.22em] transition",
              filter === k
                ? "border-primary-glow/60 bg-primary/15 text-white"
                : "border-white/10 text-white/55 hover:text-white hover:bg-white/5"
            )}
          >
            {k || "all"}
          </button>
        ))}
        <Button size="sm" variant="secondary" leftIcon={<RefreshCw size={14} />} onClick={load} data-testid="claims-refresh">
          Refresh
        </Button>
      </div>

      {/* Provider status */}
      <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid="providers-panel">
        <div className="mb-3 flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
          <Radar size={12} /> Provider status
        </div>
        <ul className="grid gap-2 md:grid-cols-2">
          {safeProviders.map((p) => (
            <li
              key={p.provider}
              data-testid={`provider-${p.provider}`}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2 text-sm"
            >
              <div className="flex items-center gap-2">
                <Chip tone={p.mode === "live" ? "aqua" : "neutral"}>{p.mode}</Chip>
                <span className="text-white">{p.provider}</span>
                <span className="text-[11px] uppercase tracking-[0.2em] text-white/45">{p.category}</span>
              </div>
              <code className="text-[11px] text-white/45">{p.env_var}</code>
            </li>
          ))}
        </ul>
      </div>

      {/* Webhook log */}
      <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid="webhooks-panel">
        <div className="mb-3 flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
          <Activity size={12} /> Webhook events
          <span className="ml-auto text-white/45">
            {Object.entries(safeConfigured).map(([k, v]) => (
              <span key={k} className={cx("ml-2", v ? "text-glow-aqua" : "text-white/35")}>{k}:{v ? "on" : "off"}</span>
            ))}
          </span>
        </div>
        {safeRecent.length === 0 ? (
          <p className="text-xs text-white/45">No recent events. Dispatcher is {Object.values(safeConfigured).some(Boolean) ? "armed" : "idle (no URL configured)"}.</p>
        ) : (
          <ul className="space-y-1.5 text-xs">
            {safeRecent.map((e, i) => (
              <li key={e.id ?? `${e.event_type}-${e.created_at ?? i}`} className="flex items-center gap-2">
                <Chip tone={e.ok ? "aqua" : "pink"}>{e.event_type}</Chip>
                <span className="text-white/80">{e.title}</span>
                {!e.ok && <span className="text-accent-pink">· {e.error}</span>}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Claims table */}
      <div className="overflow-hidden rounded-xl2 border border-white/10">
        <table className="min-w-full text-sm">
          <thead className="bg-white/[0.03] text-left text-[11px] uppercase tracking-[0.22em] text-white/55">
            <tr>
              <th className="p-3">Venue</th>
              <th className="p-3">Owner</th>
              <th className="p-3">Status</th>
              <th className="p-3">Proof</th>
              <th className="p-3">Submitted</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="p-6 text-center text-xs text-white/45">Loading…</td></tr>
            ) : safeClaims.length === 0 ? (
              <tr><td colSpan={6} className="p-10"><EmptyState title="No claims yet" hint="Owners can submit via /claims/submit." /></td></tr>
            ) : safeClaims.map((c, i) => (
              <tr key={c.id} className={cx("border-t border-white/5", i % 2 ? "bg-white/[0.01]" : "")} data-testid={`claim-row-${c.id}`}>
                <td className="p-3 font-mono text-[11px] text-white/70">{c.venue_id.slice(0, 8)}…</td>
                <td className="p-3">
                  <div className="text-white">{c.owner_name}</div>
                  <div className="text-[11px] text-white/50">{c.email}</div>
                </td>
                <td className="p-3"><Chip tone={statusTone(c.status)}>{c.status.replace("_", " ")}</Chip></td>
                <td className="p-3 max-w-[220px] truncate text-xs text-glow-aqua">
                  {c.proof ? <a href={c.proof} target="_blank" rel="noreferrer">{c.proof}</a> : "—"}
                </td>
                <td className="p-3 font-mono text-[11px] text-white/55">
                  {new Date(c.created_at).toLocaleString()}
                </td>
                <td className="p-3 text-right">
                  {c.status === "verified" || c.status === "rejected" ? (
                    <span className="text-[11px] text-white/35">
                      {c.reviewed_at ? `reviewed ${new Date(c.reviewed_at).toLocaleString()}` : "self-verified"}
                    </span>
                  ) : (
                    <div className="flex justify-end gap-2">
                      <Button size="sm" variant="secondary" onClick={() => review(c.id, "reject")} disabled={busyId === c.id} data-testid={`claim-reject-${c.id}`}>
                        Reject
                      </Button>
                      <Button size="sm" variant="pink" onClick={() => review(c.id, "approve")} disabled={busyId === c.id} data-testid={`claim-approve-${c.id}`}>
                        Approve
                      </Button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Settings (internal — Brand Kit lives here now)
// ---------------------------------------------------------------------------
const BrandKit = React.lazy(() => import("@/pages/Brand"));

function SettingsPanel() {
  const [sub, setSub] = useState("brand");
  const subs = [
    { key: "brand", label: "Brand Kit", icon: <Palette size={14} /> },
  ];
  return (
    <div className="space-y-5" data-testid="admin-settings-panel">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-2xl tracking-wider text-white">SETTINGS</h2>
        <Chip tone="purple">admin-only</Chip>
      </div>

      <div className="flex flex-wrap gap-2">
        {subs.map((s) => (
          <button
            key={s.key}
            onClick={() => setSub(s.key)}
            data-testid={`settings-sub-${s.key}`}
            className={cx(
              "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-xs uppercase tracking-[0.22em] transition",
              sub === s.key
                ? "border-primary-glow/60 bg-primary/15 text-white"
                : "border-white/10 text-white/55 hover:text-white hover:bg-white/5"
            )}
          >
            {s.icon}
            {s.label}
          </button>
        ))}
      </div>

      {sub === "brand" && (
        <div
          className="rounded-2xl border border-white/10 bg-background-deep/50 overflow-hidden"
          data-testid="admin-brandkit"
        >
          <React.Suspense fallback={<LoadingScreen label="Loading brand kit…" />}>
            <BrandKit embedded />
          </React.Suspense>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Admin root
// ---------------------------------------------------------------------------
export default function Admin() {
  const [auth, setAuth] = useState(() => !!localStorage.getItem(STORAGE_KEY));
  const [view, setView] = useState("overview");
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [inspect, setInspect] = useState(null);
  const [addOpen, setAddOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const toastRef = useToast();
  const navigate = useNavigate();

  const runRefresh = async () => {
    setRefreshing(true);
    try {
      const res = await triggerSignalRefresh();
      toast.success(`Signal engine: ${res.refreshed ?? 0}/${res.total ?? 0} venues refreshed`);
      await load();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listAdminVenues();
      setVenues(Array.isArray(res?.items) ? res.items : []);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      setVenues([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (auth) load();
  }, [auth]);

  if (!auth) return <Login onSuccess={() => setAuth(true)} />;

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setAuth(false);
    navigate("/admin");
  };
  
const handleRename = async (venue) => {
  const newName = prompt("Enter new venue name:", venue.name);
  if (!newName) return;

  try {
    await updateVenue(venue.id, { name: newName });
alert("Venue updated"); 
fetchVenues(); // ✅ this is enough
    
  } catch (e) {
    alert("Update failed");
  }
};
  
  const safeVenues = Array.isArray(venues) ? venues : [];

  return (
    <div>
      <Navbar
        rightSlot={
          <IconButton aria-label="Log out" onClick={logout} data-testid="admin-logout">
            <LogOut size={16} />
          </IconButton>
        }
      />
      <div className="mx-auto flex max-w-7xl gap-0 px-0 md:px-4">
        <Sidebar active={view} onChange={setView} onLogout={logout} />
        <main className="flex-1 px-4 py-6 md:px-6">
          <header className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.3em] text-primary-glow">Admin</p>
              <h1 className="font-display text-4xl tracking-wider text-white">
                {view === "overview" ? "OVERVIEW" : view === "venues" ? "VENUES" : view === "settings" ? "SETTINGS" : view === "claims" ? "CLAIMS" : "SIGNALS"}
              </h1>
            </div>
            <div className="hidden items-center gap-2 md:flex">
              <Chip tone="purple">Live</Chip>
              <Chip tone="neutral">
                {Array.isArray(venues) ? venues.length : 0} rows
              </Chip>
              <Button
                size="sm"
                variant="secondary"
                leftIcon={<RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />}
                onClick={runRefresh}
                disabled={refreshing}
                data-testid="admin-refresh-signals"
              >
                {refreshing ? "Refreshing…" : "Refresh signals"}
              </Button>
            </div>
          </header>

          {loading ? (
            <LoadingScreen label="Loading venues…" />
          ) : error ? (
            <ErrorState message={String(error)} onRetry={load} />
          ) : view === "overview" ? (
            <OverviewPanel venues={safeVenues} />
          ) : view === "venues" ? (
            <VenuesPanel
              venues={safeVenues}
              query={search}
              setQuery={setSearch}
              onAdd={() => setAddOpen(true)}
              onInspect={setInspect}
            />
          ) : view === "settings" ? (
            <SettingsPanel />
          ) : view === "claims" ? (
            <ClaimsPanel />
          ) : (
            <SignalsPanel venues={safeVenues} onInspect={setInspect} />
          )}
        </main>
      </div>

      {inspect && (
        <SignalInspector
          item={inspect}
          onClose={() => setInspect(null)}
          onSaved={load}
        />
      )}
      <AddVenueModal
        open={addOpen}
        onClose={() => setAddOpen(false)}
        onCreated={load}
      />
      <Footer />
    </div>
  );
}
