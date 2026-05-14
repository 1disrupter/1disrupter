import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Flame } from "lucide-react";
import venues from "../data/venues";

export default function MapView() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">

      {/* Background Glow */}
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_top,rgba(255,0,200,0.18),transparent_40%)] pointer-events-none z-10" />

      {/* Header */}
      <div className="relative z-30 flex items-center justify-between px-6 py-5 border-b border-white/10 backdrop-blur-xl">
        <button
          onClick={() => navigate("/app")}
          className="flex items-center gap-2 text-white/70 hover:text-white transition"
        >
          <ArrowLeft size={18} />
          Back
        </button>

        <h1 className="text-xl font-black tracking-[0.2em]">
          LIVE MAP
        </h1>

        <div />
      </div>

      {/* Map Area */}
      <div className="relative w-full h-screen overflow-hidden">

        {/* REAL GOOGLE MAP */}
        <div className="absolute inset-0 z-0">
          <iframe
            title="Benalmadena Map"
            width="100%"
            height="100%"
            style={{ border: 0 }}
            loading="lazy"
            allowFullScreen
            src="https://www.google.com/maps?q=36.559,-4.436&z=15&output=embed"
          />
        </div>

        {/* Dynamic Venue Hotspots */}
        {venues.map((venue, index) => (
          <div
            key={venue.id}
            className="absolute z-20"
            style={{
              top: `${35 + index * 12}%`,
              left: `${45 + index * 8}%`,
            }}
          >
            <div className="relative">
              <div className="absolute inset-0 animate-ping rounded-full blur-xl w-16 h-16 bg-fuchsia-500/40" />

              <div className="relative w-16 h-16 rounded-full border backdrop-blur-xl flex items-center justify-center shadow-[0_0_60px_rgba(255,0,200,0.8)] bg-fuchsia-500/20 border-fuchsia-400/60">
                <Flame className="text-fuchsia-300" size={28} />
              </div>
            </div>

            <div className="mt-4 rounded-2xl border bg-black/70 backdrop-blur-xl p-4 w-[220px] border-fuchsia-500/30">
              <p className="text-fuchsia-300 text-xs uppercase tracking-[0.2em] mb-2">
                {venue.tag}
              </p>

              <h3 className="text-2xl font-black">
                {venue.name}
              </h3>

              <p className="text-white/60 text-sm mt-1">
                {venue.vibe}
              </p>

              <button
                onClick={() =>
                  window.open(
                    `https://www.google.com/maps/dir/?api=1&destination=${venue.lat},${venue.lng}`,
                    "_blank"
                  )
                }
                className="mt-4 w-full py-3 rounded-xl font-bold bg-fuchsia-500 text-white"
              >
                GET DIRECTIONS
              </button>
            </div>
          </div>
        ))}

      </div>
    </div>
  );
}


