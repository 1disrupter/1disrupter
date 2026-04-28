import React, { useEffect, useState, useMemo, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  MapPin, Locate, RefreshCw, ThumbsUp, Flame, Ghost,
  ShieldCheck, CheckCircle2, Navigation, SlidersHorizontal
} from "lucide-react";
import { motion } from "framer-motion";

import {
  Navbar, Footer, BottomTabs, Logo, LogoMark,
  VenueHeroCard, LoadingScreen, ErrorState, EmptyState,
  Button, IconButton, Chip, SectionDivider, useToast,
  Modal, Input,
} from "@/components/v2n";

import {
  getTopVibes, submitFeedback, submitClaim,
  checkInVenue, earnReward
} from "@/lib/api";

import {
  getOrCreateUserId, capturePendingReferrer,
  consumePendingReferrer
} from "@/lib/userId";

import { useReferralPing } from "@/lib/useReferralPing";

const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

// Open native maps
function openDirectionsToVenue(data) {
  if (!data?.venue) return;
  const { latitude, longitude, name } = data.venue;
  const q = encodeURIComponent(`${name} @${latitude},${longitude}`);
  const url = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}&travelmode=walking&query=${q}`;
  window.open(url, "_blank", "noopener,noreferrer");
}

// Build share payload
function buildShareForVenue(data, myUserId) {
  const { venue, vibe, distance_km } = data;
  const score = vibe.vibe_score.toFixed(1);
  const flame = vibe.vibe_score >= 8 ? "🔥" : vibe.vibe_score >= 5 ? "✨" : "🌙";
  const minsRaw = distance_km != null ? Math.max(1, Math.round((distance_km / 5) * 60)) : null;
  const distLine = minsRaw ? `${minsRaw} min away` : "Nearby";
  const cat = {
    club: "Live DJ",
    bar: "Chill Vibes",
    live_music: "Live Band",
  }[venue.category] || "Vibes";

  const params = new URLSearchParams({ v: venue.id });
  if (myUserId) params.set("ref", myUserId);

  const link = `${window.location.origin}/?${params.toString()}`;
  const text =
    `${flame} ${venue.name} is a ${score} vibe right now\n` +
    `📍 ${distLine} · ${cat}\n` +
    `Find tonight's vibe → ${link}`;

  return { title: `${venue.name} · Vibe ${score}`, text, url: link };
}

export default function Home() {
  const navigate = useNavigate();
  const toast = useToast();

  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [radius, setRadius] = useState(50);
  const [loading, setLoading] = useState(false);
  const [vibes, setVibes] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState("home");

  const myUserId = useMemo(() => getOrCreateUserId(), []);

  // Capture ?ref=
  useEffect(() => {
    capturePendingReferrer();
  }, []);

  // Referral ping
  useReferralPing(myUserId, toast, 30000);

  // Honour pending referral
  const honourPendingReferral = useCallback(async () => {
    const inviter = consumePendingReferrer();
    if (!inviter) return;
    try {
      await earnReward(inviter, "referral");
      toast.success("+5 Vibe Credits sent to whoever invited you 💜");
    } catch {}
  }, [toast]);

  // Device ID
  const getDeviceId = () => {
    let d = localStorage.getItem("v2n_device_id");
    if (!d) {
      d = "dev_" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      localStorage.setItem("v2n_device_id", d);
    }
    return d;
  };

  // Check-in
  const onCheckIn = async (venue) => {
    try {
      const r = await checkInVenue(venue.id, getDeviceId());
      if (r.awarded) {
        toast.success(`+${r.bonus_credits} Vibe Credits — First verified visit today!`);
      } else if (r.reason === "venue_not_verified") {
        toast.error("Only verified venues award the first-visit bonus.");
      } else if (r.reason === "not_first_visitor") {
        toast.success("Checked in. Someone beat you to the first-visit bonus tonight ✌️");
      } else if (r.reason === "already_rewarded_today") {
        toast.success("You already claimed today's first-visit bonus here.");
      } else {
        toast.success("Checked in.");
      }
      honourPendingReferral();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Check-in failed");
    }
  };

  // Fetch vibes
  const fetchVibes = useCallback(
    async (l = loc, r = radius) => {
      try {
        setLoading(true);
        const data = await getTopVibes(l.lat, l.lng, r);
        setVibes(data);
        setError(null);
      } catch (e) {
        setError(e.response?.data?.detail || e.message || "Network error");
      } finally {
        setLoading(false);
      }
    },
    [loc, radius, toast]
  );

  useEffect(() => {
    fetchVibes(loc, radius);
  }, [fetchVibes, loc, radius]);

  // Use my location
  const useMyLocation = useCallback(() => {
    if (!navigator.geolocation) {
      toast.warn("Geolocation not available on this device.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const next = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          label: "Your Location",
        };
        setLoc(next);
        toast.success("Location updated.");
        fetchVibes(next, radius);
      },
      () => toast.warn("Please enable location to see venues near you."),
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }, [toast, radius, fetchVibes]);

  // Slots
  const slots = useMemo(
    () => [
      { key: "best_overall", data: vibes?.best_overall },
      { key: "live_music", data: vibes?.live_music },
      { key: "hidden_gem", data: vibes?.hidden_gem },
    ],
    [vibes]
  );

  // Share venue
  const handleShareVenue = useCallback(
    async (data) => {
      const payload = buildShareForVenue(data, myUserId);
      try {
        if (navigator.share) {
          await navigator.share(payload);
          return;
        }
      } catch (err) {
        if (err?.name === "AbortError") return;
      }

      try {
        const body = `${payload.text}`;
        if (navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(body);
        } else {
          const ta = document.createElement("textarea");
          ta.value = body;
          ta.setAttribute("readonly", "");
          ta.style.position = "fixed";
          ta.style.opacity = "0";
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
        }
        toast.success("Vibe copied — paste it in your group chat 💜");
      } catch {
        toast.error("Couldn't copy. Long-press to select instead.");
      }
    },
    [toast, myUserId]
  );

  // Vote
  const handleVote = async (venue_id, vote) => {
    try {
      const res = await submitFeedback(venue_id, vote);
      toast.success(`Vote logged. Score: ${res.new_vibe_score.toFixed(2)}`);
      fetchVibes();
      honourPendingReferral();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Vote failed");
    }
  };

  return (
    <div className="min-h-screen pb-24 md:pb-0">
      <Navbar
        onMenu={() => {
          const el = document.getElementById("top-three");
          if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
          else window.scrollTo({ top: 0, behavior: "smooth" });
        }}
        rightSlot={
          <IconButton onClick={useMyLocation} aria-label="Use my location">
            <Locate size={18} />
          </IconButton>
        }
        onAccount={() => navigate("/me")}
      />

      {/* HERO */}
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
              <span className="v2n-sheen">DON'T GUESS</span>
              <br />
              <span className="text-white">WHERE TO GO.</span>
              <br />
              <span className="relative mt-2 inline-block origin-bottom-left -rotate-[4deg]">
                <span
                  className="relative z-10 text-accent-pink"
                  style={{
                    textShadow:
                      "0 0 32px rgba(255,46,196,0.55), 0 0 8px rgba(255,46,196,0.85)",
                  }}
                >
                  KNOW.
                </span>

                <svg
                  aria-hidden
                  viewBox="0 0 320 22"
                  preserveAspectRatio="none"
                  className="absolute left-[-4%] top-full h-3 w-[108%] md:h-4"
                  style={{
                    filter:
                      "drop-shadow(0 0 14px rgba(255,46,196,0.65)) drop-shadow(0 0 4px rgba(255,46,196,0.95))",
                  }}
                >
                  <path
                    d="M3 12 C 35 5, 80 4, 130 9 S 220 16, 270 8 C 295 5, 312 9, 318 13 L 316 19 C 280 13, 230 18, 175 16 S 70 11, 18 17 C 11 17, 4 16, 2 15 Z"
                    fill="#FF2EC4"
                  />
                </svg>
              </span>
            </h1>

            <p className="max-w-xl text-sm text-white/60 md:text-base">
              Three perfectly-picked spots, tuned in real time. Powered by crowd
              signals, live feedback and an honest vibe score. <Logo size="xs" /> — find the vibe, go tonight.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <Button
                leftIcon={<MapPin size={16} />}
                size="md"
                variant="primary"
                onClick={useMyLocation}
              >
                Use My Location
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      <SectionDivider label={`Top 3 near ${loc.label}`} />

      {/* CARDS */}
      <section id="top-three" className="mx-auto max-w-6xl px-4">
        {loading ? (
          <LoadingScreen />
        ) : error ? (
          <ErrorState
            title="Couldn't reach the vibe engine"
            message={String(error)}
            onRetry={() => fetchVibes()}
          />
        ) : !vibes || (!vibes.best_overall && !vibes.live_music && !vibes.hidden_gem) ? (
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
                  onGo={openDirectionsToVenue}
                  onShare={handleShareVenue}
                />
              ) : null
            )}
          </div>
        )}

        {/* QUICK VOTE */}
        {vibes?.best_overall && (
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
                  TELL US THE VIBE AT {vibes.best_overall.venue.name.toUpperCase()}
                </p>
                <p className="text-xs text-white/50">Real votes shift the score in real time.</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                variant="primary"
                leftIcon={<Flame size={14} />}
                onClick={() => handleVote(vibes.best_overall.venue.id, "busy")}
                data-testid="vote-busy"
              >
                Busy
              </Button>

              <Button
                variant="pink"
                leftIcon={<ThumbsUp size={14} />}
                onClick={() => handleVote(vibes.best_overall.venue.id, "good")}
                data-testid="vote-good"
              >
                Good
              </Button>

              <Button
                variant="secondary"
                leftIcon={<Ghost size={14} />}
                onClick={() => handleVote(vibes.best_overall.venue.id, "dead")}
                data-testid="vote-dead"
              >
                Dead
              </Button>
            </div>
          </div>
        )}
      </section>

      {/* RADIUS SLIDER */}
      <section className="mx-auto max-w-6xl px-4 mt-12">
        <label className="text-white/60 text-sm">Search Radius: {radius} km</label>
        <input
          type="range"
          min="5"
          max="100"
          value={radius}
          onChange={(e) => setRadius(Number(e.target.value))}
          className="w-full mt-2 accent-accent-pink"
        />
      </section>

      {/* FOOTER */}
      <footer className="mx-auto max-w-6xl px-4 mt-16 pb-10 text-white/40 text-xs">
        <Logo size="xs" /> Vibe2Nite — Find the vibe, go tonight.
      </footer>

      <BottomTabs
        activeKey={tab}
        onChange={(k) => {
          setTab(k);
          if (k === "home") {
            window.scrollTo({ top: 0, behavior: "smooth" });
          } else if (k === "map") {
            const pins = slots.map((s) => s.data).filter(Boolean);
            if (!pins.length) {
              toast.warn("No venues to show on the map yet.");
              return;
            }
            const center = `${loc.lat},${loc.lng}`;
            const query = pins
              .map((p) => `${p.venue.name} @${p.venue.latitude},${p.venue.longitude}`)
              .join(" | ");
            const url = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}&center=${center}`;
            window.open(url, "_blank", "noopener,noreferrer");
          } else if (k === "faves") {
            toast.success("Favourites coming soon — claim a venue to track it from the owner console.");
          }
        }}
        items={[
          { key: "home", label: "Home", icon: <Flame size={18} /> },
          { key: "map", label: "Map", icon: <MapPin size={18} /> },
          { key: "faves", label: "Faves", icon: <ThumbsUp size={18} /> },
        ]}
      />
    </div>
  );
}

