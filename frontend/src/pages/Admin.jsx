import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend,
} from "recharts";
import {
  LogOut, Plus, TrendingUp, Database, Sliders, LogIn, Lock, RefreshCw,
  Activity, Radar, CalendarClock, Clock, ThumbsUp,
} from "lucide-react";
import {
  Navbar, Footer, Logo, LogoMark,
  Button, IconButton, Chip, BannerChip,
  Input, SearchBar, Select, Slider,
  Modal, useToast,
  LoadingScreen, EmptyState, ErrorState,
  VibeScoreBadge, StatusIndicator,
} from "@/components/v2n";
import { cx } from "@/lib/cx";
import { listAdminVenues, createVenue, updateSignals, triggerSignalRefresh } from "@/lib/api";

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
  const byCategory = useMemo(() => {
    const m = {};
    venues.forEach((x) => {
      m[x.venue.category] = (m[x.venue.category] || 0) + 1;
    });
    return Object.entries(m).map(([name, value]) => ({ name, value }));
  }, [venues]);

  const byCrowd = useMemo(() => {
    const m = { busy: 0, medium: 0, dead: 0 };
    venues.forEach((x) => { m[x.vibe.crowd_level] = (m[x.vibe.crowd_level] || 0) + 1; });
    return Object.entries(m).map(([name, value]) => ({ name, value }));
  }, [venues]);

  const topScores = useMemo(
    () => [...venues].sort((a, b) => b.vibe.vibe_score - a.vibe.vibe_score).slice(0, 8)
      .map((x) => ({ name: x.venue.name, score: x.vibe.vibe_score })),
    [venues]
  );

  const PIE_COLORS = ["#8A2BE2", "#FF2EC4", "#00F5FF", "#FF9A1F", "#C7A7FF"];

  const avgSignals = useMemo(() => {
    if (!venues.length) return [];
    const keys = ["manual_score", "social_activity", "user_votes", "time_prediction", "venue_boost"];
    return keys.map((k) => ({
      name: k.replace("_", " "),
      value: Number((venues.reduce((s, v) => s + (v.vibe.signals[k] || 0), 0) / venues.length).toFixed(2)),
    }));
  }, [venues]);

  const stats = [
    { label: "Venues tracked", value: venues.length, tone: "purple" },
    { label: "Average score", value: venues.length ? (venues.reduce((s, v) => s + v.vibe.vibe_score, 0) / venues.length).toFixed(2) : "0.0", tone: "pink" },
    { label: "Currently busy", value: venues.filter((v) => v.vibe.crowd_level === "busy").length, tone: "aqua" },
    { label: "Hidden gems", value: venues.filter((v) => v.vibe.vibe_score < 5).length, tone: "amber" },
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
  const filtered = venues.filter((v) =>
    v.venue.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <SearchBar value={query} onChange={setQuery} placeholder="Search venues…" className="md:max-w-sm" />
        <Button variant="pink" leftIcon={<Plus size={14} />} onClick={onAdd} data-testid="admin-add-venue">
          Add venue
        </Button>
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
                <td className="p-3 font-semibold text-white">{x.venue.name}</td>
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
                  <Button size="sm" variant="secondary" onClick={() => onInspect(x)} data-testid={`inspect-${x.venue.id}`}>
                    Inspect
                  </Button>
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
  const rows = [...venues].sort((a, b) => new Date(b.vibe.last_updated) - new Date(a.vibe.last_updated));
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
      toastRef.success(`Signal engine: ${res.refreshed ?? 0}/${res.total ?? 0} venues refreshed`);
      await load();
    } catch (e) {
      toastRef.error(e.response?.data?.detail || "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listAdminVenues();
      setVenues(res.items);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
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
                {view === "overview" ? "OVERVIEW" : view === "venues" ? "VENUES" : "SIGNALS"}
              </h1>
            </div>
            <div className="hidden items-center gap-2 md:flex">
              <Chip tone="purple">Live</Chip>
              <Chip tone="neutral">{venues.length} rows</Chip>
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
            <OverviewPanel venues={venues} />
          ) : view === "venues" ? (
            <VenuesPanel
              venues={venues}
              query={search}
              setQuery={setSearch}
              onAdd={() => setAddOpen(true)}
              onInspect={setInspect}
            />
          ) : (
            <SignalsPanel venues={venues} onInspect={setInspect} />
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
