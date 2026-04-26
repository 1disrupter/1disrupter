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
  }, []);

  const useMyLocation = () => {
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
      (err) => {
        console.warn("Location blocked or failed:", err);
        toast.warn("Please enable location to see venues near you.");
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  const handleVote = async (venue_id, vote) => {
    try {
      const res = await submitFeedback(venue_id, vote);
      toast.success(`Vote logged. Score: ${res.new_vibe_score.toFixed(2)}`);
      fetchVibes();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Vote failed");
    }
  };

  const slots = useMemo(
    () => [
      { key: "best_overall", data: data?.best_overall },
      { key: "live_music", data: data?.live_music },
      { key: "hidden_gem", data: data?.hidden_gem },
    ],
    [data]
  );

  return (
    <div className="min-h-screen pb-24 md:pb-0">
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
              <Button leftIcon={<MapPin size={16} />} size="md" variant="primary">
                Use My Location
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Add your remaining JSX sections below */}
    </div>
  );
}
