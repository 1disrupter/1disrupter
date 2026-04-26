import React, { useEffect, useState, useCallback, useMemo } from "react";
import { MapPin, Locate, Flame } from "lucide-react";
import { motion } from "framer-motion";
import {
  Navbar,
  Logo,
  Button,
  IconButton,
  useToast,
} from "@/components/v2n";
import { getTopVibes } from "@/lib/api";

const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

export default function Home() {
  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [data, setData] = useState(null);
  const [radius] = useState(50);
  const toast = useToast();

  const fetchVibes = useCallback(
    async (l = loc, r = radius) => {
      try {
        const res = await getTopVibes(l.lat, l.lng, r);
        setData(res);
      } catch (e) {
        toast.warn(e.response?.data?.detail || e.message || "Network error");
      }
    },
    [loc, radius, toast]
  );

  // eslint-disable-next-line react-hooks/exhaustive-deps
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
      () => {
        toast.warn("Please enable location to see venues near you.");
      },
      { enableHighAccuracy: true, timeout: 8000 }
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

  return (
    <div className="min-h-screen pb-24 md:pb-0">
      <Navbar
        rightSlot={
          <IconButton
            onClick={useMyLocation}
            aria-label="Use my location"
            data-testid="use-location"
          >
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
              Three perfectly-picked spots, tuned in real time. Powered by crowd
              signals, live feedback and an honest vibe score. <Logo size="xs" /> — find the vibe, go tonight.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <Button leftIcon={<MapPin size={16} />} size="md" variant="primary">
                Use My Location
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}

