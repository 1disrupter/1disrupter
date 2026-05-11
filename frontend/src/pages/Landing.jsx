import React from "react";
import { useNavigate } from "react-router-dom";

export default function Landing() {

  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">

{/* HERO */}
<section className="relative min-h-screen overflow-hidden 
bg-[#02030A]

">

  {/* Background image */}
  <div
    className="absolute inset-0 bg-cover bg-center opacity-40"
    style={{
      backgroundImage:
        "url('https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1600&auto=format&fit=crop')",
    }}
  />

  {/* Dark overlay */}
  <div className="absolute inset-0 bg-black/60" />

  {/* Neon glows */}
  <div className="absolute top-[-150px] left-[-100px] w-[500px] h-[500px] bg-pink-500/30 blur-[140px] rounded-full" />

  <div className="absolute bottom-[-150px] right-[-100px] w-[500px] h-[500px] bg-cyan-500/20 blur-[160px] rounded-full" />

  {/* Navbar */}
  <div className="relative z-20 flex items-center justify-between px-6 md:px-14 py-6">

    {/* Logo */}
    <div className="flex items-center gap-3">

      <div className="w-14 h-14 rounded-full border border-pink-500/40 flex items-center justify-center shadow-[0_0_30px_rgba(217,70,239,0.5)]">

        <span className="text-pink-500 text-3xl font-black">
          V
        </span>

      </div>

      <div>

        <h2 className="text-3xl font-black tracking-wide">
          VIBE<span className="text-pink-500">2</span>NITE
        </h2>

        <p className="text-xs tracking-[0.25em] text-cyan-400 uppercase">
          Live the Nite. Own the Vibe.
        </p>

      </div>

    </div>

    {/* Nav */}
    <div className="hidden md:flex items-center gap-10 text-sm uppercase tracking-widest text-white/70">

      <button className="hover:text-pink-400 transition">
        Home
      </button>

      <button className="hover:text-pink-400 transition">
        Features
      </button>

      <button className="hover:text-pink-400 transition">
        For Venues
      </button>

      <button className="hover:text-pink-400 transition">
        Contact
      </button>

    </div>

    {/* CTA */}
    <button
      onClick={() => navigate("/app")}
      className="hidden md:block px-6 py-3 rounded-xl bg-gradient-to-r from-pink-500 to-purple-500 font-bold shadow-[0_0_30px_rgba(217,70,239,0.45)] hover:scale-105 transition"
    >
      OPEN APP
    </button>

  </div>

  {/* Main hero */}
  <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-14 pt-10 md:pt-20 grid md:grid-cols-2 gap-12 items-center">

    {/* LEFT */}
    <div>

      <p className="uppercase tracking-[0.35em] text-cyan-400 text-sm mb-6">
        Real-time nightlife discovery
      </p>

      <h1 className="text-6xl md:text-8xl font-black leading-[0.95] mb-6">

        LIVE THE NITE.

        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-pink-400 via-pink-500 to-purple-500 drop-shadow-[0_0_30px_rgba(217,70,239,0.5)]">
          OWN THE VIBE.
        </span>

      </h1>

      <p className="text-xl text-white/70 leading-relaxed max-w-xl mb-8">
        Discover the best nightlife, bars, music and social spots in Benalmádena — live.
      </p>

      {/* Features */}
      <div className="grid grid-cols-2 gap-4 mb-10">

        <div className="bg-white/5 backdrop-blur-xl border border-pink-500/20 rounded-2xl p-4">

          <p className="text-pink-400 text-sm uppercase mb-2">
            Live Vibes
          </p>

          <p className="text-white/70 text-sm">
            Real-time crowd energy and vibe scores.
          </p>

        </div>

        <div className="bg-white/5 backdrop-blur-xl border border-cyan-500/20 rounded-2xl p-4">

          <p className="text-cyan-400 text-sm uppercase mb-2">
            Venue Rewards
          </p>

          <p className="text-white/70 text-sm">
            Earn points, rewards and exclusive perks.
          </p>

        </div>

      </div>

      {/* Buttons */}
      <div className="flex flex-wrap gap-4">

        <button
          onClick={() => navigate("/app")}
          className="px-8 py-4 rounded-2xl bg-gradient-to-r from-pink-500 to-purple-500 font-bold text-lg shadow-[0_0_40px_rgba(217,70,239,0.45)] hover:scale-105 transition"
        >
          OPEN APP
        </button>

        <button
          onClick={() => navigate("/explore")}
          className="px-8 py-4 rounded-2xl border border-cyan-400/40 bg-cyan-400/10 text-cyan-300 font-bold text-lg hover:bg-cyan-400/20 transition"
        >
          EXPLORE VENUES
        </button>

      </div>

    </div>

    {/* RIGHT */}
    <div className="relative flex justify-center">

      {/* Glow behind phone */}
      <div className="absolute w-[420px] h-[420px] bg-pink-500/30 blur-[120px] rounded-full" />

      {/* Phone image */}
      <img
        src="/landing-phone.png"
        alt="Vibe2nite App"
        className="relative z-10 w-full max-w-[500px] rotate-[8deg] drop-shadow-[0_0_60px_rgba(217,70,239,0.55)]"
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
