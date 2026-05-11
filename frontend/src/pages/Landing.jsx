
import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Music,
  Martini,
  MapPin,
  Trophy,
  Users,
  Star,
} from "lucide-react";

export default function Landing() {

  const navigate = useNavigate();

  return (
    <div className="bg-[#02030A] text-white overflow-hidden">

      {/* HERO */}
      <section className="relative min-h-screen overflow-hidden">

        {/* Background */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-50"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1800&auto=format&fit=crop')",
          }}
        />

        <div className="absolute inset-0 bg-black/65" />

        {/* Neon Glows */}
        <div className="absolute top-[-200px] left-[-120px] w-[700px] h-[700px] bg-fuchsia-500/50 blur-[150px] rounded-full" />

        <div className="absolute bottom-[-200px] right-[-120px] w-[700px] h-[700px] bg-cyan-400/40 blur-[150px] rounded-full" />

        {/* NAV */}
        <div className="relative z-30 flex items-center justify-between px-6 md:px-16 py-8">

          {/* Logo */}
          <div className="flex items-center gap-4">

            <div className="w-16 h-16 rounded-full border border-pink-500/50 flex items-center justify-center shadow-[0_0_40px_rgba(255,0,200,0.8)] bg-black/30 backdrop-blur-xl">

              <span className="text-fuchsia-400 text-4xl font-black">
                V
              </span>

            </div>

            <div>

              <h1 className="text-4xl font-black tracking-tight">
                VIBE<span className="text-fuchsia-500">2</span>NITE
              </h1>

              <p className="text-xs tracking-[0.3em] uppercase text-cyan-300">
                Live The Nite. Own The Vibe.
              </p>

            </div>

          </div>

          {/* Menu */}
          <div className="hidden md:flex items-center gap-10 text-sm uppercase tracking-[0.2em] text-white/70">

            <button className="hover:text-fuchsia-400 transition">
              Home
            </button>

            <button className="hover:text-fuchsia-400 transition">
              Features
            </button>

            <button className="hover:text-fuchsia-400 transition">
              Venues
            </button>

            <button className="hover:text-fuchsia-400 transition">
              Contact
            </button>

          </div>

          {/* CTA */}
          <button
            onClick={() => navigate("/app")}
            className="hidden md:block px-7 py-3 rounded-2xl bg-gradient-to-r from-fuchsia-500 via-pink-500 to-purple-500 font-bold shadow-[0_0_45px_rgba(255,0,200,0.7)] hover:scale-105 transition"
          >
            OPEN APP
          </button>

        </div>

        {/* MAIN HERO */}
        <div className="relative z-20 max-w-7xl mx-auto px-6 md:px-16 pt-10 md:pt-20 grid md:grid-cols-2 gap-12 items-center">

          {/* LEFT */}
          <div>

            <p className="uppercase tracking-[0.35em] text-cyan-300 text-sm mb-5">
              Real-time nightlife discovery
            </p>

            <h1 className="text-6xl md:text-8xl font-black tracking-[-0.05em] leading-[0.92] mb-6">

              LIVE THE NITE.

              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-300 via-pink-500 to-purple-400 drop-shadow-[0_0_35px_rgba(255,0,200,0.9)]">
                OWN THE VIBE.
              </span>

            </h1>

            <p className="text-xl text-white/75 leading-relaxed max-w-xl mb-10">
              Discover the best nightlife, bars, music and social spots in Benalmádena — live.
            </p>

            {/* Features */}
            <div className="grid grid-cols-2 gap-4 mb-10">

              <div className="bg-white/5 backdrop-blur-2xl border border-fuchsia-500/30 rounded-3xl p-5 shadow-[0_0_30px_rgba(255,0,200,0.15)]">

                <Users className="text-fuchsia-400 mb-3" size={28} />

                <h3 className="font-bold text-lg mb-2">
                  Live Crowds
                </h3>

                <p className="text-white/60 text-sm">
                  Real-time nightlife energy and crowd signals.
                </p>

              </div>

              <div className="bg-white/5 backdrop-blur-2xl border border-cyan-400/30 rounded-3xl p-5 shadow-[0_0_30px_rgba(0,255,255,0.12)]">

                <Trophy className="text-cyan-300 mb-3" size={28} />

                <h3 className="font-bold text-lg mb-2">
                  Rewards
                </h3>

                <p className="text-white/60 text-sm">
                  Earn rewards and unlock nightlife perks.
                </p>

              </div>

            </div>

            {/* Buttons */}
            <div className="flex flex-wrap gap-5">

              <button
                onClick={() => navigate("/app")}
                className="px-10 py-5 rounded-3xl bg-gradient-to-r from-fuchsia-500 via-pink-500 to-purple-500 text-lg font-black shadow-[0_0_50px_rgba(255,0,200,0.7)] hover:scale-105 transition"
              >
                OPEN APP
              </button>

              <button
                onClick={() => navigate("/explore")}
                className="px-10 py-5 rounded-3xl border border-cyan-400/40 bg-cyan-400/10 text-cyan-300 text-lg font-black hover:bg-cyan-400/20 transition"
              >
                EXPLORE VENUES
              </button>

            </div>

          </div>

          {/* RIGHT */}
          <div className="relative flex justify-center">

            {/* Phone Glow */}
            <div className="absolute w-[500px] h-[500px] bg-fuchsia-500/40 blur-[140px] rounded-full" />

            {/* Phone */}
            <img
              src="/landing-phone.png"
              alt="Vibe2nite App"
              className="relative z-20 w-full max-w-[540px] rotate-[8deg] drop-shadow-[0_0_120px_rgba(255,0,200,0.9)]"
            />

          </div>

        </div>

      </section>

      {/* FEATURE STRIP */}
      <section className="relative z-20 max-w-7xl mx-auto px-6 md:px-16 -mt-10">

        <div className="grid md:grid-cols-4 gap-5">

          {[
            {
              icon: <MapPin size={26} />,
              title: "Live Vibes",
              text: "See what's busy right now",
              color: "text-cyan-300",
            },
            {
              icon: <Users size={26} />,
              title: "Real Crowds",
              text: "Live nightlife energy",
              color: "text-fuchsia-400",
            },
            {
              icon: <Trophy size={26} />,
              title: "Earn Rewards",
              text: "Unlock perks and offers",
              color: "text-yellow-300",
            },
            {
              icon: <Star size={26} />,
              title: "Top Venues",
              text: "Best nightlife spots nearby",
              color: "text-purple-300",
            },
          ].map((item, i) => (

            <div
              key={i}
              className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl p-6 shadow-[0_0_35px_rgba(255,0,200,0.12)]"
            >

              <div className={`${item.color} mb-4`}>
                {item.icon}
              </div>

              <h3 className="font-bold text-xl mb-2">
                {item.title}
              </h3>

              <p className="text-white/60">
                {item.text}
              </p>

            </div>

          ))}

        </div>

      </section>

      {/* VENUE TYPES */}
      <section className="py-24 px-6 md:px-16">

        <div className="max-w-7xl mx-auto">

          <h2 className="text-5xl md:text-6xl font-black text-center mb-16 tracking-tight">

            EXPLORE THE VIBE

          </h2>

          <div className="grid md:grid-cols-3 gap-8">

            {/* Bars */}
            <div className="group relative overflow-hidden rounded-[32px] border border-fuchsia-500/30 h-[420px] shadow-[0_0_45px_rgba(255,0,200,0.2)]">

              <img
                src="/bars.jpg"
                alt="Bars"
                className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition duration-700"
              />

              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent" />

              <div className="absolute bottom-0 p-8">

                <Martini className="text-fuchsia-400 mb-4" size={42} />

                <h3 className="text-5xl font-black mb-3">
                  BARS
                </h3>

                <p className="text-white/70 text-lg">
                  Cocktails • Lounges • Social vibes
                </p>

              </div>

            </div>

            {/* Clubs */}
            <div className="group relative overflow-hidden rounded-[32px] border border-cyan-400/30 h-[420px] shadow-[0_0_45px_rgba(0,255,255,0.18)]">

              <img
                src="/clubs.jpg"
                alt="Clubs"
                className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition duration-700"
              />

              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent" />

              <div className="absolute bottom-0 p-8">

                <Users className="text-cyan-300 mb-4" size={42} />

                <h3 className="text-5xl font-black mb-3">
                  NITE CLUBS
                </h3>

                <p className="text-white/70 text-lg">
                  DJs • Dance floors • Energy
                </p>

              </div>

            </div>

            {/* Music */}
            <div className="group relative overflow-hidden rounded-[32px] border border-purple-400/30 h-[420px] shadow-[0_0_45px_rgba(180,0,255,0.2)]">

              <img
                src="/music.jpg"
                alt="Music"
                className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition duration-700"
              />

              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent" />

              <div className="absolute bottom-0 p-8">

                <Music className="text-purple-300 mb-4" size={42} />

                <h3 className="text-5xl font-black mb-3">
                  LIVE MUSIC
                </h3>

                <p className="text-white/70 text-lg">
                  Bands • Acoustic • Events
                </p>

              </div>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}

