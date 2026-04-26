import React, { useEffect, useState, useMemo, useCallback } from "react";
import { MapPin, Locate, RefreshCw, ThumbsUp, Flame, Ghost, ShieldCheck, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import {
  Navbar, Footer, BottomTabs, Logo, LogoMark,
  VenueHeroCard, LoadingScreen, ErrorState, EmptyState,
  Button, IconButton, Chip, SectionDivider, useToast,
  Modal, Input,
} from "@/components/v2n";
import { getTopVibes, submitFeedback, submitClaim, checkInVenue } from "@/lib/api";

const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

export default function Home() {
  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [radius, setRadius] = useState(50);
  const [tab, setTab] = useState("home");
  const [claimVenue, setClaimVenue] = useState(null);
  const [fvvBadge, setFvvBadge] = useState(null);
  const toast = useToast();

  const getDeviceId = () => {
    let d = localStorage.getItem("v2n_device_id");
    if (!d) {
      d = "dev_" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      localStorage.setItem("v2n_device_id", d);
    }
    return d;
  };

  const onCheckIn = async (venue) => {
    try {
      const r = await checkInVenue(venue.id, getDeviceId());
      if (r.awarded) {
        toast.success(`+${r.bonus_credits} Vibe Credits — First verified visit today!`);
        setFvvBadge({ venue_id: venue.id, bonus: r.bonus_credits });
      } else if (r.reason === "venue_not_verified") {
        toast.error("Only verified venues award the first-visit bonus.");
      } else if (r.reason === "not_first_visitor") {
        toast.success("Checked in. Someone beat you to the first-visit bonus tonight ✌️");
      } else if (r.reason === "already_rewarded_today") {
        toast.success("You already claimed today's first-visit bonus here.");
      } else {
        toast.success("Checked in.");
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || "Check-in failed");
    }
  };

  const fetchVibes = useCallback(
    async (l = loc, r = radius) => {
      setLoading(true);
      setError(null);
      try {
        const res = await getTopVibes(l.lat, l.lng, r);
        setData(res);
      } catch (e) {
        setError(e.response?.data?.detail || e.message || "Network error");
      } finally {
        setLoading(false);
      }
    },
    [loc, radius]
  );

  useEffect(() => {
    fetchVibes(loc, radius);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
const useMyLocation = () => {
  if (!navigator.geolocation) {
    toast.warn("Geolocation not available on this device.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      setLat(pos.coords.latitude);
      setLng(pos.coords.longitude);
      toast.success("Location updated.");
    },
    (err) => {
      console.warn("Location blocked or failed:", err);
      toast.warn("Please enable location to see venues near you.");
      // IMPORTANT: do NOT set fallback coords here
      // Let the UI stay in 'no location' mode instead of guessing Manhattan
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
};

  
        setLoc(next);
        toast.success("Location locked in.");
        


      <Navbar
        rightSlot={
          <IconButton onClick={useMyLocation} aria-label="Use my location" data-testid="use-location">
            <Locate size={18} />
          </IconButton>
        }
      />

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="v2n-grid absolute inset-0 opacity-30" />
        <div className="mx-auto max-w-6xl px-4 pt-10 pb-6 md:pt-16">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-start gap-5"
          >
            <div className="flex items-center gap-2 rounded-full border border-primary-glow/40 bg-primary/10 px-3 py-1 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
              <Flame size={12} /> Right now near you
            </div>
            <h1 className="font-display text-5xl leading-[0.9] tracking-wider md:text-7xl">
              <span className="v2n-sheen">DON'T GUESS.</span>
              <br />
              <span className="text-white">
                KNOW <span className="text-accent-pink">WHERE</span> TO GO.
              </span>
            </h1>
            <p className="max-w-xl text-sm text-white/60 md:text-base">
              Three perfectly-picked spots, tuned in real time. Powered by crowd signals,
              live feedback and an honest vibe score. <Logo size="xs" /> — find the vibe, go tonight.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <Button
                leftIcon={<MapPin size={16} />}
                size="md"
                variant="primary"
                onClick={useMyLocation}
                data-testid="hero-use-location"
              >
                Use my location
              </Button>
              <Button
                leftIcon={<RefreshCw size={14} />}
                size="md"
                variant="secondary"
                onClick={() => fetchVibes()}
                data-testid="hero-refresh"
              >
                Refresh vibes
              </Button>
              <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/60">
                <span className="text-primary-glow">radius</span>
                <input
                  type="range"
                  min={1}
                  max={100}
                  value={radius}
                  onChange={(e) => setRadius(Number(e.target.value))}
                  onMouseUp={() => fetchVibes(loc, radius)}
                  onTouchEnd={() => fetchVibes(loc, radius)}
                  className="w-32 accent-[#B15CFF]"
                />
                <span className="font-mono text-white">{radius} km</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 pt-1 text-[11px]">
              <Chip tone="purple">Real-time vibe scores</Chip>
              <Chip tone="pink">Top 3. Every time.</Chip>
              <Chip tone="aqua">Bars · Clubs · Live Music</Chip>
              <Chip tone="amber">Crowd signals</Chip>
            </div>
          </motion.div>
        </div>
      </section>

      <SectionDivider label={`Top 3 near ${loc.label}`} />

      {/* Cards */}
      <section className="mx-auto max-w-6xl px-4">
        {loading ? (
          <LoadingScreen />
        ) : error ? (
          <ErrorState
            title="Couldn't reach the vibe engine"
            message={String(error)}
            onRetry={() => fetchVibes()}
          />
        ) : !data || (!data.best_overall && !data.live_music && !data.hidden_gem) ? (
          <EmptyState
            title="No venues in range"
            hint="Try expanding your radius."
            actionLabel="Expand to 100 km"
            onAction={() => { setRadius(100); fetchVibes(loc, 100); }}
          />
        ) : (
          <div className="grid gap-5 md:grid-cols-3">
            {slots.map((s, i) =>
              s.data ? (
                <VenueHeroCard
                  key={s.key}
                  slot={s.key}
                  data={s.data}
                  index={i}
                  onGo={() => window.scrollTo({ top: 0 })}
                />
              ) : null
            )}
          </div>
        )}

        {/* Quick vote bar */}
        {data?.best_overall && (
          <div
            data-testid="quick-vote"
            className="mt-8 flex flex-col items-start gap-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-5 md:flex-row md:items-center md:justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent-pink text-white">
                <LogoMark size={22} />
              </div>
              <div>
                <p className="font-display text-lg tracking-wider text-white">
                  TELL US THE VIBE AT {data.best_overall.venue.name.toUpperCase()}
                </p>
                <p className="text-xs text-white/50">Real votes shift the score in real time.</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="primary"
                leftIcon={<Flame size={14} />}
                onClick={() => handleVote(data.best_overall.venue.id, "busy")}
                data-testid="vote-busy"
              >
                Busy
              </Button>
              <Button
                variant="pink"
                leftIcon={<ThumbsUp size={14} />}
                onClick={() => handleVote(data.best_overall.venue.id, "good")}
                data-testid="vote-good"
              >
                Good
              </Button>
              <Button
                variant="secondary"
                leftIcon={<Ghost size={14} />}
                onClick={() => handleVote(data.best_overall.venue.id, "dead")}
                data-testid="vote-dead"
              >
                Dead
              </Button>
            </div>
          </div>
        )}

        {/* Claim your venue — public entry point */}
        {data?.best_overall && (
          <div
            data-testid="claim-bar"
            className="mt-4 flex flex-col items-start gap-2 rounded-xl2 border border-primary-glow/30 bg-primary/5 p-4 md:flex-row md:items-center md:justify-between"
          >
            <p className="text-xs uppercase tracking-[0.22em] text-white/70">
              Are you the owner of <span className="text-white">{data.best_overall.venue.name}</span>? Claim this venue to unlock lightweight admin tools.
            </p>
            <div className="flex gap-2">
              {data.best_overall.venue.is_verified && (
                <Button
                  variant="aqua"
                  size="sm"
                  leftIcon={<CheckCircle2 size={14} />}
                  onClick={() => onCheckIn(data.best_overall.venue)}
                  data-testid="checkin-btn"
                >
                  Check in · earn +15
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<ShieldCheck size={14} />}
                onClick={() => setClaimVenue(data.best_overall.venue)}
                data-testid="open-claim-modal"
              >
                Claim this venue
              </Button>
            </div>
          </div>
        )}

        {fvvBadge && data?.best_overall?.venue?.id === fvvBadge.venue_id && (
          <div
            data-testid="fvv-badge"
            className="mt-2 inline-flex items-center gap-2 rounded-full border border-glow-aqua/50 bg-glow-aqua/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-glow-aqua"
          >
            <CheckCircle2 size={12} /> First Verified Visit Bonus · +{fvvBadge.bonus}
          </div>
        )}
      </section>

      <Footer />

      <BottomTabs
        activeKey={tab}
        onChange={setTab}
        items={[
          { key: "home", label: "Home", icon: <Flame size={18} /> },
          { key: "map", label: "Map", icon: <MapPin size={18} /> },
          { key: "faves", label: "Faves", icon: <ThumbsUp size={18} /> },
        ]}
      />

      {claimVenue && (
        <ClaimModal
          venue={claimVenue}
          onClose={() => setClaimVenue(null)}
          onSuccess={(res) => {
            if (res.email_delivery?.sent) {
              toast.success("Check your inbox — verification link sent.");
            } else if (res.magic_link) {
              toast.success("Magic link ready (copy it to verify).");
            }
          }}
        />
      )}
    </div>
  );
}

function ClaimModal({ venue, onClose, onSuccess }) {
  const toast = useToast();
  const [form, setForm] = useState({ owner_name: "", email: "", proof: "" });
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  const submit = async () => {
    if (!form.owner_name.trim() || !form.email.trim()) {
      toast.error("Name and email are required");
      return;
    }
    setBusy(true);
    try {
      const res = await submitClaim({
        venue_id: venue.id,
        owner_name: form.owner_name.trim(),
        email: form.email.trim().toLowerCase(),
        proof: form.proof.trim(),
      });
      setResult(res);
      onSuccess?.(res);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Submission failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal
      open
      onClose={onClose}
      title={`CLAIM · ${venue.name.toUpperCase()}`}
      footer={
        result ? (
          <Button variant="primary" onClick={onClose} data-testid="claim-done">Done</Button>
        ) : (
          <>
            <Button variant="secondary" onClick={onClose}>Cancel</Button>
            <Button variant="pink" loading={busy} onClick={submit} data-testid="claim-submit">
              Send magic link
            </Button>
          </>
        )
      }
    >
      {result ? (
        <div className="space-y-3 text-sm" data-testid="claim-result">
          <p className="text-white/85">
            {result.email_delivery?.sent
              ? `We just sent a verification link to ${result.email_delivery.to}. Click it within 30 minutes — single-use.`
              : "Email is in console-only mode on this environment. Use the link below to verify right now:"}
          </p>
          {result.magic_link && (
            <code className="block break-all rounded-xl border border-primary-glow/40 bg-primary/10 p-3 text-[11px] text-glow-aqua" data-testid="claim-magic-link">
              {result.magic_link}
            </code>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <Input
            label="Your name"
            value={form.owner_name}
            onChange={(e) => setForm({ ...form, owner_name: e.target.value })}
            placeholder="Jane Owner"
            data-testid="claim-name"
          />
          <Input
            label="Email for verification"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="jane@laterraza.com"
            data-testid="claim-email"
          />
          <Input
            label="Proof link (website, Instagram, Google listing)"
            value={form.proof}
            onChange={(e) => setForm({ ...form, proof: e.target.value })}
            placeholder="https://instagram.com/laterraza"
            data-testid="claim-proof"
          />
          <p className="text-[11px] text-white/45">
            You'll receive a single-use verification link valid for 30 minutes.
          </p>
        </div>
      )}
    </Modal>
  );
}
