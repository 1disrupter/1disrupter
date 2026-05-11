import React from "react";
import { useNavigate } from "react-router-dom";

export default function Landing() {

  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">

      {/* HERO */}
      <section className="relative min-h-screen flex items-center px-6 md:px-16">

        {/* Background */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#050510] via-[#090014] to-black opacity-100" />

        {/* Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-pink-500/20 blur-[140px]" />

        <div className="relative z-10 max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">

          {/* LEFT */}
          <div>
<p className="text-cyan-400 tracking-[0.3em] uppercase text-sm mb-4">
  Real-time nightlife discovery
</p>

<h1 className="text-5xl md:text-7xl font-black leading-tight mb-6">

  Discover the best nightlife,
  bars, music and social spots
  in Benalmádena — live.

</h1>

<p className="text-pink-500 text-2xl md:text-3xl font-bold tracking-wide mb-6">
  LIVE THE NITE. OWN THE VIBE.
</p>

<p className="text-white/70 text-lg max-w-xl mb-8">
  Real-time vibe scores, live crowd energy, rewards
  and venue discovery — all in one app.
</p>
           
            <div className="flex flex-wrap gap-4">

              <button
                onClick={() => navigate("/app")}
                className="bg-pink-500 hover:bg-pink-400 transition px-8 py-4 rounded-xl text-lg font-bold"
              >
                OPEN APP
              </button>

              <button
                onClick={() => navigate("/explore")}
                className="border border-pink-500 text-pink-400 px-8 py-4 rounded-xl text-lg font-bold hover:bg-pink-500/10"
              >
                EXPLORE VENUES
              </button>

            </div>

          </div>

          {/* RIGHT */}
          <div className="relative flex justify-center">

            <img
              src="/landing-phone.png"
              alt="Vibe2nite App"
              className="w-full max-w-md drop-shadow-[0_0_50px_rgba(255,0,150,0.35)]"
            />

          </div>

        </div>

      </section>

      {/* VENUE TYPES */}
      <section className="px-6 md:px-16 py-24">

        <div className="max-w-7xl mx-auto">

          <p className="text-pink-500 uppercase tracking-[0.3em] text-sm mb-4 text-center">
            Explore by vibe
          </p>

          <h2 className="text-5xl font-black text-center mb-16">
            FIND YOUR SCENE
          </h2>

          <div className="grid md:grid-cols-3 gap-8">

            {/* BARS */}
            <div className="rounded-3xl overflow-hidden border border-pink-500/20 bg-white/5">

              <img
                src="/bars.jpg"
                alt="Bars"
                className="h-64 w-full object-cover"
              />

              <div className="p-6">

                <h3 className="text-3xl font-bold mb-3">
                  Bars
                </h3>

                <p className="text-white/60 mb-6">
                  Cocktail bars, chill spots and social vibes.
                </p>

                <button
                  onClick={() => navigate("/explore")}
                  className="w-full bg-pink-500 py-3 rounded-xl font-bold"
                >
                  Explore Bars
                </button>

              </div>

            </div>

            {/* CLUBS */}
            <div className="rounded-3xl overflow-hidden border border-cyan-400/20 bg-white/5">

              <img
                src="/clubs.jpg"
                alt="Clubs"
                className="h-64 w-full object-cover"
              />

              <div className="p-6">

                <h3 className="text-3xl font-bold mb-3">
                  Nite Clubs
                </h3>

                <p className="text-white/60 mb-6">
                  Big energy, DJs and packed dance floors.
                </p>

                <button
                  onClick={() => navigate("/explore")}
                  className="w-full bg-cyan-400 text-black py-3 rounded-xl font-bold"
                >
                  Explore Clubs
                </button>

              </div>

            </div>

            {/* LIVE MUSIC */}
            <div className="rounded-3xl overflow-hidden border border-purple-500/20 bg-white/5">

              <img
                src="/music.jpg"
                alt="Live Music"
                className="h-64 w-full object-cover"
              />

              <div className="p-6">

                <h3 className="text-3xl font-bold mb-3">
                  Live Music
                </h3>

                <p className="text-white/60 mb-6">
                  Bands, acoustic sets and unforgettable nights.
                </p>

                <button
                  onClick={() => navigate("/explore")}
                  className="w-full bg-purple-500 py-3 rounded-xl font-bold"
                >
                  Explore Music
                </button>

              </div>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}
