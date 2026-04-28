import React, { useEffect, useState, useMemo, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { MapPin, Locate, RefreshCw, ThumbsUp, Flame, Ghost, ShieldCheck, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import {
  Navbar, Footer, BottomTabs, Logo, LogoMark,
  VenueHeroCard, LoadingScreen, ErrorState, EmptyState,
  Button, IconButton, Chip, SectionDivider, useToast,
  Modal, Input,
} from "@/components/v2n";
import { getTopVibes, submitFeedback, submitClaim, checkInVenue, earnReward } from "@/lib/api";
import { getOrCreateUserId, capturePendingReferrer, consumePendingReferrer } from "@/lib/userId";
import { useReferralPing } from "@/lib/useReferralPing";

const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

// Open the device's native maps app with directions to the venue.
function openDirectionsToVenue(data) {
  if (!data?.venue) return;
  const { latitude, longitude, name } = data.venue;
  const q = encodeURIComponent(`${name} @${latitude},${longitude}`);
  const url = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}&destination_place_id=&travelmode=walking&query=${q}`;
  window.open(url, "_blank", "noopener,noreferrer");
}

// Compose the share text + URL for a venue.
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

  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [radius, setRadius] = useState(50);

  // Stable anonymous identity for this device — used as wallet user_id
  // and as the referrer parameter on share links.
  const myUserId = useMemo(() => getOrCreateUserId(), []);

  // On first mount, snatch ?ref=<inviter-id> from the URL (if present) and
  // clean the param. We'll honour it on the user's first credit-eligible
  // action below.
  useEffect(() => {
    capturePendingReferrer();
  }, []);

  // Poll my own wallet every 30s — when referral_credits ticks up,
  // celebrate with a toast on the Home page itself. Auto-pauses when the
  // tab is hidden; resumes immediately on focus.
  useReferralPing(myUserId, toast, 30000);

  // Best-effort: if a pending referrer exists, credit them +5 Vibe Credits
  // on the recipient's first credit-eligible action. Fires at most once
  // per device (consume clears the storage key).
  const honourPendingReferral = useCallback(async () => {
    const inviter = consumePendingReferrer();
    if (!inviter) return;
    try {
      await earnReward(inviter, "referral");
      toast.success("+5 Vibe Credits sent to whoever invited you 💜");
    } catch {
      // Re-stash so we can retry on a future action — but only if storage works.
      // (Intentionally ignored — losing one referral credit isn't fatal.)
    }
  }, [toast]);

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
      // First credit-eligible action of this session → credit any pending inviter.
      honourPendingReferral();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Check-in failed");
    }
  };

  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [radius, setRadius] = useState(50);

  // Stable anonymous identity for this device — used as wallet user_id
  // and as the referrer parameter on share links.
  const myUserId = useMemo(() => getOrCreateUserId(), []);

  // On first mount, snatch ?ref=<inviter-id> from the URL (if present) and
  // clean the param. We'll honour it on the user's first credit-eligible
  // action below.
  useEffect(() => {
    capturePendingReferrer();
  }, []);

  // Poll my own wallet every 30s — when referral_credits ticks up,
  // celebrate with a toast on the Home page itself. Auto-pauses when the
  // tab is hidden; resumes immediately on focus.
  useReferralPing(myUserId, toast, 30000);

  // Best-effort: if a pending referrer exists, credit them +5 Vibe Credits
  // on the recipient's first credit-eligible action. Fires at most once
  // per device (consume clears the storage key).
  const honourPendingReferral = useCallback(async () => {
    const inviter = consumePendingReferrer();
    if (!inviter) return;
    try {
      await earnReward(inviter, "referral");
      toast.success("+5 Vibe Credits sent to whoever invited you 💜");
    } catch {
      // Re-stash so we can retry on a future action — but only if storage works.
      // (Intentionally ignored — losing one referral credit isn't fatal.)
    }
  }, [toast]);

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
      // First credit-eligible action of this session → credit any pending inviter.
      honourPendingReferral();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Check-in failed");
    }
  };


  const fetchVibes = useCallback(
    async (l = loc, r = radius) => {
      try {
        setLoading(true);
        const data = await getTopVibes(l.lat, l.lng, r);
        setVibes(normalizeVibes(data));
      } catch (e) {
        toast.warn(e.response?.data?.detail || e.message || "Network error");
      } finally {
        setLoading(false);
      }
    },
    [loc, radius, toast]
  );

  useEffect(() => {
    fetchVibes(loc, radius);
  }, [fetchVibes, loc, radius]);

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

  const slots = useMemo(
    () => [
      { key: "best_overall", data: data?.best_overall },
      { key: "live_music", data: data?.live_music },
      { key: "hidden_gem", data: data?.hidden_gem },
    ],
    [data]
  );

  const handleShareVenue = useCallback(
    async (data) => {
      const payload = buildShareForVenue(data, myUserId);
      // 1) Try the native share sheet (mobile + a few desktop browsers).
      try {
        if (navigator.share) {
          await navigator.share(payload);
          return;
        }
      } catch (err) {
        // User dismissed the share sheet — that's not an error worth toasting.
        if (err?.name === "AbortError") return;
      }
      // 2) Fallback: copy preformatted text to the clipboard.
      try {
        const body = `${payload.text}`;
        if (navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(body);
        } else {
          // Legacy fallback for very old browsers.
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

  const handleVote = async (venue_id, vote) => {
    try {
      const res = await submitFeedback(venue_id, vote);
      toast.success(`Vote logged. Score: ${res.new_vibe_score.toFixed(2)}`);
      fetchVibes();
      // First credit-eligible action → credit any pending inviter (idempotent).
      honourPendingReferral();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Vote failed");
    }
  };

    }
  }, [registerLocationFn, useMyLocation]);

  return (
    <div className="min-h-screen pb-24 md:pb-0">
      <Navbar
        onMenu={() => {
          // Smooth-scroll to the Top-3 cards section so the menu button
          // actually does something useful on mobile.
          const el = document.getElementById("top-three");
          if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
          else window.scrollTo({ top: 0, behavior: "smooth" });
        }}
        rightSlot={
          <IconButton onClick={useMyLocation} aria-label="Use my location" data-testid="use-location">
            <Locate size={18} />
          </IconButton>
        }
        onAccount={() => navigate("/me")}
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
                {/* hand-painted brushstroke underline */}
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

      {/* Cards */}
      <section id="top-three" className="mx-auto max-w-6xl px-4">
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
                  onGo={openDirectionsToVenue}
                  onShare={handleShareVenue}
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
      </section>


          <div className="flex items-center gap-3">
            <IconButton><Navigation size={18} /></IconButton>
            <IconButton><SlidersHorizontal size={18} /></IconButton>
          </div>
        </div>

        {/* 3‑Card Layout */}
        <div className="grid gap-6 md:grid-cols-3">
          <VibeCard title="Best Overall" data={vibes.best_overall} loading={loading} />
          <VibeCard title="Live Music" data={vibes.live_music} loading={loading} />
          <VibeCard title="Hidden Gem" data={vibes.hidden_gem} loading={loading} />
        </div>
      </section>
      <Footer />

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
            // Build a Google Maps URL centered on the user with markers for the top venues.
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
    </div>
  );
}
