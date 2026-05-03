import React, { useEffect, useState, useMemo, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  MapPin,
  Locate,
  RefreshCw,
  ThumbsUp,
  Flame,
  Ghost,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { motion } from "framer-motion";

import {
  Navbar,
  Footer,
  BottomTabs,
  Logo,
  LogoMark,
  VenueHeroCard,
  LoadingScreen,
  ErrorState,
  EmptyState,
  Button,
  IconButton,
  Chip,
  SectionDivider,
  useToast,
  Modal,
  Input,
} from "@/components/v2n";

import {
  getTopVibes,
  submitFeedback,
  submitClaim,
  checkInVenue,
  earnReward,
} from "@/lib/api";

import {
  getOrCreateUserId,
  capturePendingReferrer,
  consumePendingReferrer,
} from "@/lib/userId";

import { useReferralPing } from "@/lib/useReferralPing";
import QRScanner from "../components/QRScanner";

const DEFAULT_LOCATION = {
  lat: 40.73,
  lng: -73.99,
  label: "Manhattan, NY",
};

// Open directions
function openDirectionsToVenue(data) {
  if (!data?.venue) return;
  const { latitude, longitude } = data.venue;
  const url = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}&travelmode=walking`;
  window.open(url, "_blank", "noopener,noreferrer");
}

// share helper
function buildShareForVenue(data, myUserId) {
  const { venue, vibe, distance_km } = data;
  const score = vibe.vibe_score.toFixed(1);
  const flame =
    vibe.vibe_score >= 8 ? "🔥" : vibe.vibe_score >= 5 ? "✨" : "🌙";

  const minsRaw =
    distance_km != null
      ? Math.max(1, Math.round((distance_km / 5) * 60))
      : null;

  const distLine = minsRaw ? `${minsRaw} min away` : "Nearby";

  const cat =
    {
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
};

export default function Home() {
  const navigate = useNavigate();
  const toast = useToast();

  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [radius, setRadius] = useState(50);
  const [tab, setTab] = useState("home");
  const [claimVenue, setClaimVenue] = useState(null);
  const [fvvBadge, setFvvBadge] = useState(null);

  // 🔥 FIXED: Hook is now INSIDE component (this was breaking build)
  const [showScanner, setShowScanner] = useState(false);

  const myUserId = useMemo(() => getOrCreateUserId(), []);

  useEffect(() => {
    capturePendingReferrer();
  }, []);

  useReferralPing(myUserId, toast, 30000);

  const honourPendingReferral = useCallback(async () => {
    const inviter = consumePendingReferrer();
    if (!inviter) return;

    try {
      await earnReward(inviter, "referral");
      toast.success(
        "+5 Vibe Credits sent to whoever invited you 💜"
      );
    } catch (e) {
      // ignore
    }
  }, [toast]);

  const getDeviceId = () => {
    return "device-id-placeholder";
  };

  const onCheckIn = async (venue) => {
    await checkInVenue(venue.id);
    await honourPendingReferral();
    toast.success("Checked in 🔥");
  };

  const useMyLocation = () => {
    navigator.geolocation.getCurrentPosition((pos) => {
      setLoc({
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        label: "My Location",
      });
    });
  };

  const handleVote = async (venue_id, vote) => {
    await submitFeedback(venue_id, vote);
  };

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorState message={error} />;
  if (!data?.length) return <EmptyState />;

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-900/20 to-black">
      <Navbar rightSlot={<Locate size={18} />} />

      {/* Scanner toggle example */}
      {showScanner && (
        <QRScanner onClose={() => setShowScanner(false)} />
      )}

      {/* Content */}
      <Footer />
    </div>
  );
}

// ---------------- MODAL ----------------

function ClaimModal({ venue, onClose, onSuccess }) {
  const submit = async () => {
    await submitClaim(venue.id);
    onSuccess();
  };

  return (
    <Modal open onClose={onClose}>
      <div className="p-4">
        <h2 className="text-white text-lg">Claim Venue</h2>
        <Button onClick={submit}>Submit Claim</Button>
      </div>
    </Modal>
  );
}
