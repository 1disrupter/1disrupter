import React from "react";
import { FaMusic, FaStar, FaBuilding } from "react-icons/fa";

export default function VibeCard({ title, data, loading }) {
  // Skeleton mode
  if (loading) {
    return (
      <div className="rounded-xl bg-white/5 border border-white/10 p-4 animate-pulse">
        <div className="h-4 w-24 bg-white/10 rounded mb-3"></div>
        <div className="h-8 w-16 bg-white/10 rounded mb-2"></div>
        <div className="h-3 w-32 bg-white/10 rounded mb-1"></div>
        <div className="h-3 w-20 bg-white/10 rounded mb-4"></div>
        <div className="h-10 w-full bg-white/10 rounded"></div>
      </div>
    );
  }

  if (!data) return null;

  // Icon selection based on card type
  const icon =
    title === "Live Music" ? (
      <FaMusic className="text-accent-pink text-xl" />
    ) : title === "Hidden Gem" ? (
      <FaStar className="text-accent-pink text-xl" />
    ) : (
      <FaBuilding className="text-accent-pink text-xl" />
    );

  return (
    <div className="rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-white/10 p-4 shadow-lg backdrop-blur-md">
      {/* Title + Icon */}
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <h4 className="text-xs uppercase tracking-wide text-accent-pink">
          {title}
        </h4>
      </div>

      {/* Venue Name */}
      <h3 className="font-semibold text-lg mb-1">
        {data.venue_name || data.venue?.name || "Coming soon"}
      </h3>

      {/* Tagline */}
      <p className="text-white/60 text-sm mb-3">
        {data.tagline || ""}
      </p>

      {/* Animated Vibe Score */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-4xl font-bold text-accent-pink animate-pulse">
          {data.vibe_score || data.vibe?.vibe_score || 0}
        </span>
        <span className="text-white/40 text-xs uppercase tracking-wide">
          vibe score
        </span>
      </div>

      {/* Distance */}
      <p className="text-white/50 text-sm mb-4">
        {data.distance ||
          (data.distance_km
            ? `${Math.round(data.distance_km)} min away`
            : "")}
      </p>

      {/* Button */}
      <button className="w-full py-2 rounded-lg font-semibold bg-accent-pink text-black hover:bg-pink-400 transition">
        GO HERE
      </button>
    </div>
  );
}

