import React, { useEffect, useState, useCallback } from "react";
import { MapPin, Locate, Flame, Navigation, SlidersHorizontal } from "lucide-react";
import { motion } from "framer-motion";
import {
  Navbar,
  Logo,
  Button,
  IconButton,
  Card,
  CardBody,
  CardHeader,
  useToast,
} from "@/components/v2n";
import { getTopVibes } from "@/lib/api";

const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

export default function Home() {
  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [radius, setRadius] = useState(50);
  const [vibes, setVibes] = useState([]);
  const toast = useToast();

  const fetchVibes = useCallback(
    async (l = loc, r = radius) => {
      try {
        const data = await getTopVibes(l.lat, l.lng, r);
        setVibes(data || []);
      } catch (e) {
        toast.warn(e.response?.data?.detail || e.message || "Network error");
      }
    },
    [loc, radius, toast]
  );

  useEffect(() => {
    fetchVibes(loc, radius);
  }, [fetchVibes, loc, radius]);

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

  return (
    <div className="min-h-screen pb-24 md:pb-0">
      {/* NAVBAR */}
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

      {/* TONIGHT FEED */}
      <section className="mx-auto max-w-6xl px-4 mt-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-2xl tracking-wide">Tonight</h2>

          <div className="flex items-center gap-3">
            <IconButton>
              <Navigation size={18} />
            </IconButton>

            <IconButton>
              <SlidersHorizontal size={18} />
            </IconButton>
          </div>
        </div>

        {vibes.length === 0 && (
          <p className="text-white/50 text-sm">No vibes found in this area.</p>
        )}

        <div className="grid gap-4 md:grid-cols-3">
          {vibes.map((v, i) => (
            <Card key={i} className="bg-white/5 border-white/10">
              <CardHeader>
                <h3 className="font-semibold text-lg">{v.name}</h3>
                <p className="text-white/50 text-sm">{v.address}</p>
              </CardHeader>

              <CardBody>
                <div className="flex items-center justify-between">
                  <span className="text-accent-pink font-bold text-xl">
                    {v.score}
                  </span>
                  <span className="text-white/40 text-xs uppercase tracking-wide">
                    vibe score
                  </span>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
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
          className="w-full mt-2"
        />
      </section>

      {/* FOOTER */}
      <footer className="mx-auto max-w-6xl px-4 mt-16 pb-10 text-white/40 text-xs">
        <Logo size="xs" /> Vibe2Nite — Find the vibe, go tonight.
      </footer>
    </div>
  );
}

