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
import { getTopVibes, submitFeedback, submitClaim, checkInVenue, earnReward,getWallet } from "@/lib/api";
import { getOrCreateUserId, capturePendingReferrer, consumePendingReferrer } from "@/lib/userId";
import { useReferralPing } from "@/lib/useReferralPing";

import QRScanner from "../components/QRScanner";

const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

// Open the device's native maps app with directions to the venue.
// On mobile this hands off to Apple/Google Maps; on desktop it opens
// Google Maps in a new tab. Pure client-side, no API key required.
function openDirectionsToVenue(data) {
  if (!data?.venue) return;
  const { latitude, longitude } = data.venue;
  const url = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}&travelmode=walking`;
  window.open(url, "_blank", "noopener,noreferrer");
}


// Compose the share text + URL for a venue. The URL carries:
//   ?v=<venue-id>   → forward-compatible deep link to highlight the venue
//   ?ref=<my-uuid>  → so the inviter can be credited Vibe Credits when the
//                     recipient takes their first credit-eligible action
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
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [radius, setRadius] = useState(50);
  const [tab, setTab] = useState("home");
  const [claimVenue, setClaimVenue] = useState(null);
  const [fvvBadge, setFvvBadge] = useState(null);
  const [showScanner, setShowScanner] = useState(false);
  const [showWallet, setShowWallet] = useState(false);
  const [showRewards, setShowRewards] = useState(false);

const [tokens, setTokens] = useState(() => {
  return Number(localStorage.getItem("v2n_tokens") || 0);
});
  
  const toast = useToast();
  
  // Stable anonymous identity for this device — used as wallet user_id
  // and as the referrer parameter on share links.
  const myUserId = useMemo(() => getOrCreateUserId(), []);
  useEffect(() => {
  async function loadWallet() {
    try {
      const wallet = await getWallet(myUserId);

      const balance = wallet?.credits || 0;

      setTokens(balance);

      localStorage.setItem("v2n_tokens", balance);
    } catch (e) {
      console.warn("Wallet load failed");
    }
  }

  loadWallet();
}, [myUserId]);
 

  // On first mount, snatch ?ref=<inviter-id> from the URL (if present) and
  // clean the param. We'll honour it on the user's first credit-eligible
  // action below.
  useEffect(() => {
    capturePendingReferrer();
  }, []);

  // Poll my own wallet every 30s — when referral_credits ticks up,
  // celebrate with a toast on the Home page itself. Auto-pauses when the
  // tab is hidden; resumes immediately on focus.
 // useReferralPing(myUserId, toast, 30000);

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
      toast.warn("Geolocation not available. Using Manhattan.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const next = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          label: "My location",
        };
        setLoc(next);
        toast.success("Location locked in.");
        fetchVibes(next, radius);
      },
      () => toast.error("Could not read your location."),
      { timeout: 6000 }
    );
  };

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
<section className="relative overflow-hidden"> <div className="v2n-grid absolute inset-0 opacity-30 pointer-events-none" /> <div className="relative z-10 mx-auto max-w-6xl px-4 pt-10 pb-6 md:pt-16"> <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}  className="flex flex-col items-start gap-5" > <div className="flex items-center gap-2 rounded-full border border-primary-glow/40 bg-primary/10 px-3 py-1 text-[11px] uppercase tracking-[0.28em] text-primary-glow"> <Flame size={12} /> Right now near you </div> <h1 className="font-display text-5xl leading-[0.9] tracking-wider md:text-7xl"> <span className="v2n-sheen">DON'T GUESS</span> <br /> <span className="text-white">WHERE TO GO.</span> <br /> <span className="relative mt-2 inline-block origin-bottom-left -rotate-[4deg]"> <span className="relative z-10 text-accent-pink" style={{ textShadow: "0 0 32px rgba(255,46,196,0.55), 0 0 8px rgba(255,46,196,0.85)", }} > KNOW. </span> {/* hand-painted brushstroke underline */} <svg aria-hidden viewBox="0 0 320 22" preserveAspectRatio="none" className="absolute left-[-4%] top-full h-3 w-[108%] md:h-4" style={{ filter: "drop-shadow(0 0 14px rgba(255,46,196,0.65)) drop-shadow(0 0 4px rgba(255,46,196,0.95))", }} > <path d="M3 12 C 35 5, 80 4, 130 9 S 220 16, 270 8 C 295 5, 312 9, 318 13 L 316 19 C 280 13, 230 18, 175 16 S 70 11, 18 17 C 11 17, 4 16, 2 15 Z" fill="#FF2EC4" /> </svg> </span> </h1> <p className="max-w-xl text-sm text-white/60 md:text-base"> Three perfectly-picked spots, tuned in real time. Powered by crowd signals, live feedback and an honest vibe score. <Logo size="xs" /> — find the vibe, go tonight. </p> <button onClick={() => { console.log("clicked"); setShowWallet(true); }} className="relative z-20 mt-4 inline-flex items-center gap-2 rounded-full border border-primary-glow/40 bg-primary/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-primary-glow" > 💰 Tokens <span className="font-mono text-white text-sm"> {tokens} </span> </button> <div className="flex flex-wrap items-center gap-3"> <Button leftIcon={<MapPin size={16} />} size="md" variant="primary" onClick={useMyLocation} data-testid="hero-use-location" > Use my location </Button> <Button leftIcon={<RefreshCw size={14} />} size="md" variant="secondary" onClick={() => fetchVibes()} data-testid="hero-refresh" > Refresh vibes </Button> <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/60"> <span className="text-primary-glow">radius</span> <input type="range" min={1} max={100} value={radius} onChange={(e) => setRadius(Number(e.target.value))} onMouseUp={() => fetchVibes(loc, radius)} onTouchEnd={() => fetchVibes(loc, radius)} className="w-32 accent-[#B15CFF]" /> <span className="font-mono text-white">{radius} km</span> </div> </div> <div className="flex flex-wrap gap-2 pt-1 text-[11px]"> <Chip tone="purple">Real-time vibe scores</Chip> <Chip tone="pink">Top 3. Every time.</Chip> <Chip tone="aqua">Bars · Clubs · Live Music</Chip> <Chip tone="amber">Crowd signals</Chip> </div> </motion.div> </div> </section>
      <SectionDivider label={`Top 3 near ${loc.label}`} />
<div className="mx-auto max-w-6xl px-4 mb-4 flex justify-end">
  <Button
    variant="secondary"
    onClick={() => setShowScanner(true)}
  >
    Scan at Venue
  </Button>
</div>
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
      {showScanner && (
  <QRScanner
    onClose={() => setShowScanner(false)}
    onCheckInSuccess={(result) => {
      const earned = result?.reward?.tokens || 0;
      const group = result?.group_size || 1;

      setTokens((prev) => {
  const next = prev + earned;
  localStorage.setItem("v2n_tokens", next);
  return next;
});

      toast.success(`+${earned} tokens · ${group} people here 🔥`);

      fetchVibes();
    }}
  />
)}
   

{showWallet && (
 <WalletModal
  tokens={tokens}
  onClose={() => setShowWallet(false)}
  setShowRewards={setShowRewards}
/> 
)}   
      {showRewards && (
  <RewardsModal
    tokens={tokens}
    setTokens={setTokens}
    onClose={() => setShowRewards(false)}
  />
)}
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
function RewardsModal({ tokens, setTokens, onClose }) {
  const [activeReward, setActiveReward] = useState(null);
  const rewards = [
    { id: 1, name: "Free Shot", cost: 50 },
    { id: 2, name: "VIP Entry", cost: 200 },
    { id: 3, name: "2-for-1 Cocktails", cost: 80 },
  ];

  const redeemReward = (reward) => {
    if (tokens < reward.cost) {
      alert("Not enough tokens");
      return;
    }

    const next = tokens - reward.cost;

    setTokens(next);

    localStorage.setItem("v2n_tokens", next);

    const code =
  "V2N-" +
  Math.random().toString(36).substring(2, 8).toUpperCase();

const redemption = {
  ...reward,
  code,
  redeemed_at: new Date().toISOString(),
  status: "ACTIVE",
};

localStorage.setItem(
  "v2n_last_reward",
  JSON.stringify(redemption)
);

setActiveReward(redemption);
  };

  return (
    <div className="fixed inset-0 z-[9999] bg-black/95 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-black border border-white/10 p-6 rounded-xl">
        <h2 className="text-white text-2xl mb-5 text-center">
          Rewards Marketplace
        </h2>

        
         {activeReward ? (
  <div className="text-center space-y-4">
    
    <p className="text-2xl text-primary-glow">
      🔥 Reward Redeemed
    </p>

    <p className="text-white text-lg">
      {activeReward.name}
    </p>

    <div className="border border-primary-glow/40 rounded-xl p-4 bg-primary/10">
      <p className="text-xs text-white/60 mb-2">
        SHOW THIS TO STAFF
      </p>

      <p className="text-3xl font-mono text-primary-glow tracking-widest">
        {activeReward.code}
      </p>
    </div>

    <p className="text-xs text-white/40">
      Redeemed just now
    </p>
  </div>
) : (
  <div className="space-y-3">
    {rewards.map((reward) => (
      <div
        key={reward.id}
        className="flex items-center justify-between border border-white/10 rounded-lg p-3"
      >
        <div>
          <p className="text-white">
            {reward.name}
          </p>

          <p className="text-sm text-primary-glow">
            {reward.cost} tokens
          </p>
        </div>

        <button
          onClick={() => redeemReward(reward)}
          className="bg-primary-glow text-black px-3 py-2 rounded font-semibold"
        >
          Redeem
        </button>
      </div>
    ))}
  </div>
)} 
          <button
          onClick={onClose}
          className="w-full mt-5 text-white border border-white/20 px-4 py-2 rounded"
        >
          Close
        </button>
      </div>
    </div>
  );
}      
function WalletModal({ tokens, onClose, setShowRewards }) {
  const savedReward = JSON.parse(
    const markRewardUsed = () => {
  const updated = {
    ...savedReward,
    status: "USED",
  };

  localStorage.setItem(
    "v2n_last_reward",
    JSON.stringify(updated)
  );

  window.location.reload();
};
  localStorage.getItem("v2n_last_reward") || "null"
);
  return (
    <div className="fixed inset-0 z-[9999] bg-black/95 flex items-center justify-center">
      <div className="bg-black border border-white/10 p-6 rounded-xl text-center">
        <p className="text-white text-xl mb-2">YOUR TOKENS</p>

        <p className="text-primary-glow text-3xl font-mono">
          {tokens}
        </p>
      {savedReward && (
  <div className="mt-4 border border-primary-glow/30 bg-primary/5 rounded-xl p-4 text-left">
    <p className="text-xs uppercase tracking-widest text-primary-glow mb-3">
      Active Reward
    </p>

    <p className="text-white text-lg">
      {savedReward.name}
    </p>
<p
  className={`text-xs mt-1 uppercase tracking-widest ${
    savedReward.status === "USED"
      ? "text-red-400"
      : "text-green-400"
  }`}
>
  {savedReward.status}
</p>
    <p className="text-primary-glow font-mono text-2xl mt-2">
      {savedReward.code}
    </p>

    <p className="text-xs text-white/40 mt-2">
      Redeemed recently
    </p>
    {savedReward.status !== "USED" && (
  <button
    onClick={markRewardUsed}
    className="mt-3 w-full border border-red-500/40 text-red-400 px-3 py-2 rounded"
  >
    Mark as Used
  </button>
)}
  </div>
)}  
<div className="mt-4 flex flex-col gap-3">
  <button
    onClick={() => {
  onClose();
  setShowRewards(true);
}}
    className="text-black bg-primary-glow px-4 py-2 rounded font-semibold"
  >
    Spend Tokens
  </button>

  <button
    onClick={onClose}
    className="text-white border px-4 py-2 rounded"
  >
    Close
  </button>
</div>
        
      </div>
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
