import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Key, LogOut, RefreshCw, Sparkles } from "lucide-react";
import {
  Navbar, Footer, Button, Chip, Input, SectionDivider,
  LoadingScreen, EmptyState, useToast,
} from "@/components/v2n";
import { getOwnerMe, getOwnerInbox, setOwnerHandles } from "@/lib/api";

const OWNER_KEY_STORAGE = "v2n_owner_key";

/**
 * Owner-scoped dashboard. Auth = `X-Owner-Key` header. Key is either:
 *   - ?key=vk_... in the URL (emailed deep link), or
 *   - localStorage (persisted after first successful load)
 */
export default function Owner() {
  const [params, setParams] = useSearchParams();
  const toast = useToast();
  const [key, setKey] = useState(() => {
    return params.get("key") || localStorage.getItem(OWNER_KEY_STORAGE) || "";
  });
  const [input, setInput] = useState("");
  const [summary, setSummary] = useState(null);
  const [inbox, setInbox] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [savingHandles, setSavingHandles] = useState(false);
  const [handles, setHandles] = useState({ instagram: "", tiktok: "" });

  const load = async (activeKey) => {
    if (!activeKey) return;
    setLoading(true);
    setError(null);
    try {
      const [me, ib] = await Promise.all([
        getOwnerMe(activeKey),
        getOwnerInbox(activeKey, 10),
      ]);
      setSummary(me);
      setInbox(ib.items || []);
      localStorage.setItem(OWNER_KEY_STORAGE, activeKey);
      const h = me?.venues?.[0]?.social_handles || {};
      setHandles({ instagram: h.instagram || "", tiktok: h.tiktok || "" });
      // Clear ?key= from URL once we've consumed it (keeps link history clean).
      if (params.get("key")) {
        params.delete("key");
        setParams(params, { replace: true });
      }
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || "Invalid key";
      setError(msg);
      toast.error(msg);
      localStorage.removeItem(OWNER_KEY_STORAGE);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (key) load(key); }, [key]);  // eslint-disable-line

  const submitKey = () => {
    const k = input.trim();
    if (!k) return toast.error("Paste your owner key");
    setKey(k);
  };

  const logout = () => {
    localStorage.removeItem(OWNER_KEY_STORAGE);
    setKey("");
    setSummary(null);
    setInbox([]);
  };

  const saveHandles = async () => {
    setSavingHandles(true);
    try {
      await setOwnerHandles(key, {
        instagram: handles.instagram.trim() || null,
        tiktok: handles.tiktok.trim() || null,
      });
      toast.success("Social handles saved.");
      await load(key);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Couldn't save");
    } finally {
      setSavingHandles(false);
    }
  };

  const venue = summary?.venues?.[0];
  const signals = venue?.external_signals;

  const signalRows = useMemo(() => signals ? [
    ["Google busyness", signals.google_score],
    ["Social activity", signals.social_score],
    ["Events / live music", signals.event_score],
    ["Time-of-day", signals.time_score],
    ["User votes", signals.user_votes_score],
  ] : [], [signals]);

  return (
    <div className="min-h-screen bg-background-deep text-white">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-6 flex items-center gap-2 text-[11px] uppercase tracking-[0.3em] text-primary-glow">
          <Sparkles size={14} /> Owner console
        </div>
        <h1 className="font-display text-4xl tracking-widest md:text-5xl">
          VENUE <span className="text-accent-pink">CONTROL ROOM</span>
        </h1>
        <p className="mt-2 text-sm text-white/60">
          Private view for verified venue owners — your live vibe signals, inbox and social handles.
        </p>

        {/* --- Auth gate ---------------------------------------------------- */}
        {!key && (
          <div
            data-testid="owner-auth-card"
            className="mt-10 rounded-xl3 border border-primary-glow/30 bg-white/[0.02] p-8"
          >
            <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
              <Key size={14} /> Sign in with your owner key
            </div>
            <p className="mt-2 text-sm text-white/60">
              Paste the <code className="text-glow-aqua">vk_…</code> key you received after verifying your claim.
            </p>
            <div className="mt-4 flex flex-col gap-3 md:flex-row">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="vk_xxxxxxxxxxxxxxxxxxxxxxxxxxx"
                className="flex-1"
                data-testid="owner-key-input"
              />
              <Button variant="pink" onClick={submitKey} data-testid="owner-key-submit">
                Sign in
              </Button>
            </div>
          </div>
        )}

        {key && loading && !summary && <LoadingScreen />}
        {key && error && !summary && (
          <div className="mt-10">
            <EmptyState title="Invalid or expired key" hint={error} />
            <div className="mt-4 flex justify-center">
              <Button variant="secondary" onClick={logout}>Try a different key</Button>
            </div>
          </div>
        )}

        {/* --- Dashboard ---------------------------------------------------- */}
        {key && summary && venue && (
          <div className="mt-10 space-y-8" data-testid="owner-dashboard">
            <div className="flex flex-wrap items-center gap-3">
              <Chip tone="aqua">verified</Chip>
              <div className="text-sm">
                <div className="font-display text-2xl tracking-wider text-white">{venue.name}</div>
                <div className="text-[11px] uppercase tracking-[0.28em] text-white/55">{venue.category}</div>
              </div>
              <div className="ml-auto flex gap-2">
                <Button size="sm" variant="secondary" leftIcon={<RefreshCw size={14} />} onClick={() => load(key)}>Refresh</Button>
                <Button size="sm" variant="ghost" leftIcon={<LogOut size={14} />} onClick={logout} data-testid="owner-logout">Sign out</Button>
              </div>
            </div>

            {/* Live vibe card */}
            <div
              data-testid="owner-vibe-card"
              className="rounded-xl3 border border-primary-glow/30 bg-gradient-to-br from-primary/15 to-background-deep p-8 shadow-softPurple"
            >
              <div className="flex items-baseline gap-3">
                <span className="font-mono text-6xl text-white">{(venue.vibe_score ?? 0).toFixed(2)}</span>
                <span className="text-[11px] uppercase tracking-[0.28em] text-white/55">live vibe score</span>
              </div>
              <div className="mt-2 flex items-center gap-2 text-sm">
                <Chip tone={
                  venue.crowd_level === "buzzing" ? "pink"
                  : venue.crowd_level === "busy" ? "amber"
                  : venue.crowd_level === "medium" ? "lavender"
                  : "neutral"
                }>{venue.crowd_level || "—"}</Chip>
                <span className="text-white/55 font-mono text-[11px]">
                  last update {venue.last_updated ? new Date(venue.last_updated).toLocaleTimeString() : "—"}
                </span>
              </div>
            </div>

            {/* Signal breakdown */}
            <div>
              <SectionDivider label="External signals" />
              <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {signalRows.length === 0 ? (
                  <div className="col-span-full">
                    <EmptyState title="No signals yet" hint="The Signal Engine refreshes every minute." />
                  </div>
                ) : signalRows.map(([label, val]) => (
                  <div key={label} className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid={`owner-signal-${label.replace(/\W/g,'-').toLowerCase()}`}>
                    <div className="text-[11px] uppercase tracking-[0.22em] text-white/55">{label}</div>
                    <div className="mt-1 flex items-baseline gap-2">
                      <span className="font-mono text-2xl text-white">{(val ?? 0).toFixed(2)}</span>
                      <span className="text-[11px] text-white/40">/ 10</span>
                    </div>
                    <div className="mt-2 h-1.5 rounded-full bg-white/10">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-primary to-accent-pink"
                        style={{ width: `${Math.min(100, ((val ?? 0) / 10) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Social handles */}
            <div>
              <SectionDivider label="Social handles" />
              <p className="mt-2 text-xs text-white/50">
                Wire your IG / TikTok handles to feed the real-time signal engine. Used only when the
                platform-level API key is configured (env var).
              </p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <Input
                  label="Instagram handle"
                  placeholder="@laterraza"
                  value={handles.instagram}
                  onChange={(e) => setHandles({ ...handles, instagram: e.target.value })}
                  data-testid="owner-handle-instagram"
                />
                <Input
                  label="TikTok handle"
                  placeholder="@terraza"
                  value={handles.tiktok}
                  onChange={(e) => setHandles({ ...handles, tiktok: e.target.value })}
                  data-testid="owner-handle-tiktok"
                />
              </div>
              <div className="mt-3">
                <Button variant="primary" loading={savingHandles} onClick={saveHandles} data-testid="owner-handles-save">
                  Save handles
                </Button>
              </div>
            </div>

            {/* Inbox */}
            <div>
              <SectionDivider label="Inbox" />
              {inbox.length === 0 ? (
                <div className="mt-4"><EmptyState title="No messages yet" hint="We'll drop updates here." /></div>
              ) : (
                <ul className="mt-4 space-y-2" data-testid="owner-inbox-list">
                  {inbox.map((m) => (
                    <li
                      key={m.id}
                      className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4"
                      data-testid={`owner-inbox-item-${m.kind}`}
                    >
                      <div className="flex items-center gap-2">
                        <Chip tone="purple">{m.kind.replace("_", " ")}</Chip>
                        <span className="text-white">{m.title}</span>
                        <span className="ml-auto font-mono text-[11px] text-white/45">
                          {new Date(m.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-white/75">{m.body}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
