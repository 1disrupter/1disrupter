import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Key, LogOut, RefreshCw, Sparkles, Send, AlertTriangle, UserPlus } from "lucide-react";
import {
  Navbar, Footer, Button, Chip, Input, SectionDivider,
  LoadingScreen, EmptyState, useToast,
} from "@/components/v2n";
import {
  getOwnerMe, getOwnerInbox,
  setOwnerHandlesForVenue, setOwnerWebhooks, testOwnerWebhook,
  requestOwnerTransfer, submitReverify,
} from "@/lib/api";

const OWNER_KEY_STORAGE = "v2n_owner_key";
const LAST_VENUE_STORAGE = "v2n_owner_last_venue";

const SLACK_PREFIX = "https://hooks.slack.com/";
const DISCORD_PREFIX = "https://discord.com/api/webhooks/";

export default function Owner() {
  const [params, setParams] = useSearchParams();
  const toast = useToast();
  const [key, setKey] = useState(
    () => params.get("key") || localStorage.getItem(OWNER_KEY_STORAGE) || ""
  );
  const [input, setInput] = useState("");
  const [summary, setSummary] = useState(null);
  const [inbox, setInbox] = useState([]);
  const [activeVenueId, setActiveVenueId] = useState(
    () => localStorage.getItem(LAST_VENUE_STORAGE) || ""
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Per-venue editor state
  const [handles, setHandles] = useState({ instagram: "", tiktok: "" });
  const [savingHandles, setSavingHandles] = useState(false);
  const [webhooks, setWebhooksState] = useState({ slack_webhook_url: "", discord_webhook_url: "" });
  const [savingHooks, setSavingHooks] = useState(false);
  const [testingHook, setTestingHook] = useState(false);

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
      // Pick the active venue: stored preference if still owned, else first.
      const owned = (me.venues || []).map((v) => v.id);
      const nextActive =
        (activeVenueId && owned.includes(activeVenueId) && activeVenueId) ||
        owned[0] || "";
      setActiveVenueId(nextActive);
      if (nextActive) localStorage.setItem(LAST_VENUE_STORAGE, nextActive);

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

  // Sync editor state whenever the active venue changes
  useEffect(() => {
    if (!summary || !activeVenueId) return;
    const v = (summary.venues || []).find((x) => x.id === activeVenueId);
    if (!v) return;
    setHandles({
      instagram: v.social_handles?.instagram || "",
      tiktok: v.social_handles?.tiktok || "",
    });
    setWebhooksState({
      slack_webhook_url: v.webhooks?.slack_webhook_url || "",
      discord_webhook_url: v.webhooks?.discord_webhook_url || "",
    });
  }, [summary, activeVenueId]);

  const submitKey = () => {
    const k = input.trim();
    if (!k) return toast.error("Paste your owner key");
    setKey(k);
  };

  const logout = () => {
    localStorage.removeItem(OWNER_KEY_STORAGE);
    localStorage.removeItem(LAST_VENUE_STORAGE);
    setKey(""); setSummary(null); setInbox([]); setActiveVenueId("");
  };

  const pickVenue = (id) => {
    setActiveVenueId(id);
    localStorage.setItem(LAST_VENUE_STORAGE, id);
  };

  const saveHandles = async () => {
    if (!activeVenueId) return;
    setSavingHandles(true);
    try {
      await setOwnerHandlesForVenue(key, activeVenueId, {
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

  const validateHook = () => {
    const s = webhooks.slack_webhook_url.trim();
    const d = webhooks.discord_webhook_url.trim();
    if (s && !s.startsWith(SLACK_PREFIX)) {
      toast.error(`Slack URL must start with ${SLACK_PREFIX}`); return null;
    }
    if (d && !d.startsWith(DISCORD_PREFIX)) {
      toast.error(`Discord URL must start with ${DISCORD_PREFIX}`); return null;
    }
    return { s, d };
  };

  const saveHooks = async () => {
    const v = validateHook();
    if (!v || !activeVenueId) return;
    setSavingHooks(true);
    try {
      await setOwnerWebhooks(key, activeVenueId, {
        slack_webhook_url: v.s || null,
        discord_webhook_url: v.d || null,
      });
      toast.success("Webhooks saved.");
      await load(key);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Couldn't save");
    } finally {
      setSavingHooks(false);
    }
  };

  const testHook = async () => {
    if (!activeVenueId) return;
    setTestingHook(true);
    try {
      const r = await testOwnerWebhook(key, activeVenueId);
      toast.success(`Test fired to ${r.targets?.length || 0} channel(s).`);
    } catch (e) {
      toast.error(e.response?.data?.detail || "No webhook configured");
    } finally {
      setTestingHook(false);
    }
  };

  const activeVenue = useMemo(
    () => (summary?.venues || []).find((v) => v.id === activeVenueId) || null,
    [summary, activeVenueId]
  );
  const signals = activeVenue?.external_signals;
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
          Private view for verified venue owners — your live vibe signals, inbox and integrations.
        </p>

        {!key && (
          <div data-testid="owner-auth-card" className="mt-10 rounded-xl3 border border-primary-glow/30 bg-white/[0.02] p-8">
            <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
              <Key size={14} /> Sign in with your owner key
            </div>
            <p className="mt-2 text-sm text-white/60">
              Paste the <code className="text-glow-aqua">vk_…</code> key you received after verifying your claim.
            </p>
            <div className="mt-4 flex flex-col gap-3 md:flex-row">
              <Input value={input} onChange={(e) => setInput(e.target.value)} placeholder="vk_xxxxxxxxxxxxxxxxxxxxxxxxxxx" className="flex-1" data-testid="owner-key-input" />
              <Button variant="pink" onClick={submitKey} data-testid="owner-key-submit">Sign in</Button>
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

        {key && summary && (
          <div className="mt-10 space-y-8" data-testid="owner-dashboard">
            {/* Owner summary strip */}
            <div className="flex flex-wrap items-center gap-3">
              <Chip tone="aqua">verified</Chip>
              <div className="text-sm">
                <div className="font-display text-2xl tracking-wider text-white">{summary.owner.name}</div>
                <div className="text-[11px] uppercase tracking-[0.28em] text-white/55">
                  {summary.owner.email} · {summary.owner.venue_count} venue{summary.owner.venue_count === 1 ? "" : "s"}
                </div>
              </div>
              <div className="ml-auto flex gap-2">
                <Button size="sm" variant="secondary" leftIcon={<RefreshCw size={14} />} onClick={() => load(key)}>Refresh</Button>
                <Button size="sm" variant="ghost" leftIcon={<LogOut size={14} />} onClick={logout} data-testid="owner-logout">Sign out</Button>
              </div>
            </div>

            {/* Venue switcher */}
            {summary.venues.length > 1 && (
              <div data-testid="owner-venue-switcher">
                <SectionDivider label="Your venues" />
                <div className="mt-3 flex flex-wrap gap-2">
                  {summary.venues.map((v) => (
                    <button
                      key={v.id}
                      onClick={() => pickVenue(v.id)}
                      data-testid={`owner-venue-pick-${v.id}`}
                      className={
                        "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-xs uppercase tracking-[0.22em] transition " +
                        (activeVenueId === v.id
                          ? "border-primary-glow/60 bg-primary/15 text-white"
                          : "border-white/10 text-white/55 hover:text-white hover:bg-white/5")
                      }
                    >
                      {v.name}
                      <span className="font-mono text-[10px] text-glow-aqua">{(v.vibe_score ?? 0).toFixed(1)}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeVenue && (
              <>
                {/* Ownership state banners (Iter 16) */}
                {activeVenue.transfer_requested && activeVenue.ownership_active && (
                  <div
                    data-testid="owner-banner-transfer"
                    className="rounded-xl2 border border-accent-pink/50 bg-accent-pink/10 p-4"
                  >
                    <div className="flex items-center gap-2 text-accent-pink">
                      <UserPlus size={14} />
                      <span className="text-[11px] uppercase tracking-[0.28em]">Transfer in progress</span>
                    </div>
                    <p className="mt-1 text-sm text-white/80">
                      Awaiting <code className="text-white">{activeVenue.transfer_email}</code> to accept. They have a
                      single-use magic link, expiring shortly.
                    </p>
                  </div>
                )}
                {!activeVenue.ownership_active && (
                  <div
                    data-testid="owner-banner-expired"
                    className="rounded-xl2 border border-status-busy/60 bg-status-busy/10 p-4"
                  >
                    <div className="flex items-center gap-2 text-status-busy">
                      <AlertTriangle size={14} />
                      <span className="text-[11px] uppercase tracking-[0.28em]">Ownership expired</span>
                    </div>
                    <p className="mt-1 text-sm text-white/80">
                      Ownership of this venue has lapsed. Re-verify to regain access to the console.
                    </p>
                    <Button
                      variant="pink"
                      size="sm"
                      className="mt-3"
                      onClick={async () => {
                        try {
                          const r = await submitReverify({
                            venue_id: activeVenue.id,
                            email: summary.owner.email,
                            owner_name: summary.owner.name,
                            proof: "reverification",
                          });
                          if (r.magic_link) {
                            toast.success("Re-verify link ready — check your email (or use dev link).");
                          } else {
                            toast.success("Re-verify email sent.");
                          }
                        } catch (e) {
                          toast.error(e.response?.data?.detail || "Couldn't start re-verify");
                        }
                      }}
                      data-testid="owner-reverify-btn"
                    >
                      Re-verify ownership
                    </Button>
                  </div>
                )}

                {/* Live vibe card */}
                <div data-testid="owner-vibe-card" className="rounded-xl3 border border-primary-glow/30 bg-gradient-to-br from-primary/15 to-background-deep p-8 shadow-softPurple">
                  <div className="flex items-center gap-3">
                    <span className="font-display text-xl tracking-wider text-white">{activeVenue.name}</span>
                    {activeVenue.is_verified && <Chip tone="aqua">verified ✓</Chip>}
                  </div>
                  <div className="mt-4 flex items-baseline gap-3">
                    <span className="font-mono text-6xl text-white">{(activeVenue.vibe_score ?? 0).toFixed(2)}</span>
                    <span className="text-[11px] uppercase tracking-[0.28em] text-white/55">live vibe score</span>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-sm">
                    <Chip tone={
                      activeVenue.crowd_level === "buzzing" ? "pink"
                      : activeVenue.crowd_level === "busy" ? "amber"
                      : activeVenue.crowd_level === "medium" ? "lavender" : "neutral"
                    }>{activeVenue.crowd_level || "—"}</Chip>
                    <span className="text-white/55 font-mono text-[11px]">
                      last update {activeVenue.last_updated ? new Date(activeVenue.last_updated).toLocaleTimeString() : "—"}
                    </span>
                  </div>
                </div>

                {/* Signals */}
                <div>
                  <SectionDivider label="External signals" />
                  <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {signalRows.length === 0 ? (
                      <div className="col-span-full"><EmptyState title="No signals yet" hint="The Signal Engine refreshes every minute." /></div>
                    ) : signalRows.map(([label, val]) => (
                      <div key={label} className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid={`owner-signal-${label.replace(/\W/g,'-').toLowerCase()}`}>
                        <div className="text-[11px] uppercase tracking-[0.22em] text-white/55">{label}</div>
                        <div className="mt-1 flex items-baseline gap-2">
                          <span className="font-mono text-2xl text-white">{(val ?? 0).toFixed(2)}</span>
                          <span className="text-[11px] text-white/40">/ 10</span>
                        </div>
                        <div className="mt-2 h-1.5 rounded-full bg-white/10">
                          <div className="h-full rounded-full bg-gradient-to-r from-primary to-accent-pink" style={{ width: `${Math.min(100, ((val ?? 0) / 10) * 100)}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Handles */}
                <div>
                  <SectionDivider label="Social handles" />
                  <p className="mt-2 text-xs text-white/50">Used by the real-time signal engine when platform API keys are configured.</p>
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <Input label="Instagram handle" placeholder="@laterraza" value={handles.instagram} onChange={(e) => setHandles({ ...handles, instagram: e.target.value })} data-testid="owner-handle-instagram" />
                    <Input label="TikTok handle" placeholder="@terraza" value={handles.tiktok} onChange={(e) => setHandles({ ...handles, tiktok: e.target.value })} data-testid="owner-handle-tiktok" />
                  </div>
                  <div className="mt-3">
                    <Button variant="primary" loading={savingHandles} disabled={!activeVenue.ownership_active} onClick={saveHandles} data-testid="owner-handles-save">Save handles</Button>
                  </div>
                </div>

                {/* Integrations */}
                <div data-testid="owner-integrations">
                  <SectionDivider label="Integrations" />
                  <p className="mt-2 text-xs text-white/50">
                    Pipe vibe spikes and other events into your team's Slack/Discord channel.
                  </p>
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <Input
                      label="Slack webhook URL"
                      placeholder="https://hooks.slack.com/services/..."
                      value={webhooks.slack_webhook_url}
                      onChange={(e) => setWebhooksState({ ...webhooks, slack_webhook_url: e.target.value })}
                      data-testid="owner-slack-url"
                    />
                    <Input
                      label="Discord webhook URL"
                      placeholder="https://discord.com/api/webhooks/..."
                      value={webhooks.discord_webhook_url}
                      onChange={(e) => setWebhooksState({ ...webhooks, discord_webhook_url: e.target.value })}
                      data-testid="owner-discord-url"
                    />
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Button variant="primary" loading={savingHooks} disabled={!activeVenue.ownership_active} onClick={saveHooks} data-testid="owner-hooks-save">Save webhooks</Button>
                    <Button
                      variant="aqua"
                      leftIcon={<Send size={14} />}
                      loading={testingHook}
                      onClick={testHook}
                      disabled={!activeVenue.ownership_active || (!webhooks.slack_webhook_url && !webhooks.discord_webhook_url)}
                      data-testid="owner-hooks-test"
                    >
                      Test webhook
                    </Button>
                  </div>
                </div>

                {/* Transfer ownership (Iter 16) */}
                <TransferOwnershipBlock
                  apiKey={key}
                  venue={activeVenue}
                  onDone={() => load(key)}
                />
              </>
            )}

            {/* Inbox (owner-scoped) */}
            <div>
              <SectionDivider label="Inbox" />
              {inbox.length === 0 ? (
                <div className="mt-4"><EmptyState title="No messages yet" hint="We'll drop updates here." /></div>
              ) : (
                <ul className="mt-4 space-y-2" data-testid="owner-inbox-list">
                  {inbox.map((m) => (
                    <li key={m.id} className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid={`owner-inbox-item-${m.kind}`}>
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

function TransferOwnershipBlock({ apiKey, venue, onDone }) {
  const toast = useToast();
  const [email, setEmail] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [result, setResult] = React.useState(null);

  const submit = async () => {
    if (!venue.ownership_active) return;
    if (!email.trim()) return toast.error("Enter the new owner's email");
    setBusy(true);
    try {
      const r = await requestOwnerTransfer(apiKey, venue.id, email.trim().toLowerCase());
      setResult(r);
      toast.success("Transfer initiated — new owner got a magic link.");
      onDone?.();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Couldn't start transfer");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div data-testid="owner-transfer-block">
      <SectionDivider label="Ownership" />
      <p className="mt-2 text-xs text-white/50">
        Moving on? Transfer ownership to someone else. They'll receive a single-use link (1h) and immediately inherit the console.
      </p>
      <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]">
        <Input
          placeholder="newowner@venue.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={!venue.ownership_active || venue.transfer_requested}
          data-testid="owner-transfer-email"
        />
        <Button
          variant="pink"
          leftIcon={<UserPlus size={14} />}
          loading={busy}
          onClick={submit}
          disabled={!venue.ownership_active || venue.transfer_requested}
          data-testid="owner-transfer-submit"
        >
          Transfer ownership
        </Button>
      </div>
      {result?.magic_link && (
        <code className="mt-3 block break-all rounded-xl border border-primary-glow/40 bg-primary/10 p-3 text-[11px] text-glow-aqua" data-testid="owner-transfer-link">
          {result.magic_link}
        </code>
      )}
    </div>
  );
}
