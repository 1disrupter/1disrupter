
import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Flame, Music, Martini } from "lucide-react";

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

        {/* HOTSPOT 1 */}
        <div className="absolute z-20 top-[42%] left-[52%]">

          <div className="relative">

            <div className="absolute inset-0 animate-ping rounded-full bg-fuchsia-500/40 blur-xl w-20 h-20" />

            <div className="relative w-20 h-20 rounded-full bg-fuchsia-500/30 border border-fuchsia-400/60 backdrop-blur-xl flex items-center justify-center shadow-[0_0_60px_rgba(255,0,200,0.8)]">

              <Flame className="text-fuchsia-300" size={34} />

            </div>

          </div>

          <div className="mt-4 rounded-2xl border border-fuchsia-500/30 bg-black/70 backdrop-blur-xl p-4 w-[220px]">

            <p className="text-fuchsia-400 text-xs uppercase tracking-[0.2em] mb-2">
              HOT NOW
            </p>

            <h3 className="text-2xl font-black">
              Hole in the Wall
            </h3>

            <p className="text-white/60 text-sm mt-1">
              97% Vibe · Packed
            </p>

            <button
              onClick={() =>
                window.open(
                  "https://www.google.com/maps/dir/?api=1&destination=36.559,-4.436",
                  "_blank"
                )
              }
              className="mt-4 w-full py-3 rounded-xl bg-fuchsia-500 text-white font-bold"
            >
              GET DIRECTIONS
            </button>

          </div>

        </div>

        {/* HOTSPOT 2 */}
        <div className="absolute z-20 top-[58%] left-[65%]">

          <div className="relative">

            <div className="absolute inset-0 animate-ping rounded-full bg-cyan-400/40 blur-xl w-16 h-16" />

            <div className="relative w-16 h-16 rounded-full bg-cyan-400/20 border border-cyan-300/60 flex items-center justify-center shadow-[0_0_60px_rgba(0,217,255,0.8)]">

              <Music className="text-cyan-300" size={28} />

            </div>

          </div>

          <div className="mt-4 rounded-2xl border border-cyan-400/30 bg-black/70 backdrop-blur-xl p-4 w-[220px]">

            <p className="text-cyan-300 text-xs uppercase tracking-[0.2em] mb-2">
              LIVE MUSIC
            </p>

            <h3 className="text-2xl font-black">
              Sky Lounge
            </h3>

            <p className="text-white/60 text-sm mt-1">
              89% Vibe · Acoustic Night
            </p>

            <button
              className="mt-4 w-full py-3 rounded-xl bg-cyan-400 text-black font-bold"
            >
              GET DIRECTIONS
            </button>

          </div>

        </div>

        {/* HOTSPOT 3 */}
        <div className="absolute z-20 top-[70%] left-[25%]">

          <div className="relative">

            <div className="absolute inset-0 animate-ping rounded-full bg-purple-400/40 blur-xl w-16 h-16" />

            <div className="relative w-16 h-16 rounded-full bg-purple-500/20 border border-purple-300/60 flex items-center justify-center shadow-[0_0_60px_rgba(180,0,255,0.7)]">

              <Martini className="text-purple-300" size={28} />

            </div>

          </div>

          <div className="mt-4 rounded-2xl border border-purple-400/30 bg-black/70 backdrop-blur-xl p-4 w-[220px]">

            <p className="text-purple-300 text-xs uppercase tracking-[0.2em] mb-2">
              TRENDING
            </p>

            <h3 className="text-2xl font-black">
              Electric Avenue
            </h3>

            <p className="text-white/60 text-sm mt-1">
              91% Vibe · Cocktail Lounge
            </p>

            <button
              className="mt-4 w-full py-3 rounded-xl bg-purple-500 text-white font-bold"
            >
              GET DIRECTIONS
            </button>

          </div>

        </div>

      </div>

    </div>

  );
}



