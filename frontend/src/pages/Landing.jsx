
import React from "react";
import { useNavigate } from "react-router-dom";

export default function Landing() {

  const navigate = useNavigate();

  return (
    <div className="bg-[#02030A] text-white overflow-x-hidden">

      {/* GLOBAL BACKGROUND */}
      <div className="fixed inset-0 z-0">

        <div className="absolute inset-0 bg-[#02030A]" />

        <div className="absolute top-[-300px] left-[-200px] w-[900px] h-[900px] bg-fuchsia-500/30 blur-[180px] rounded-full" />

        <div className="absolute bottom-[-300px] right-[-200px] w-[900px] h-[900px] bg-cyan-400/20 blur-[180px] rounded-full" />

      </div>

      <div className="relative z-10">

        {/* ================= HERO ================= */}

        <section className="relative min-h-screen overflow-hidden px-6 md:px-14 pt-8">

          {/* HERO BG */}
          <div
            className="absolute inset-0 bg-cover bg-center opacity-50"
            style={{
              backgroundImage: "url('/hero-bg.jpg')",
            }}
          />

          <div className="absolute inset-0 bg-black/70" />

          {/* NAV */}
          <div className="relative z-20 flex items-center justify-between">

            {/* LOGO */}
            <div className="flex items-center gap-4">

              <div className="w-16 h-16 rounded-full border border-fuchsia-500/40 flex items-center justify-center shadow-[0_0_40px_rgba(255,0,200,0.9)]">

                <span className="text-fuchsia-400 text-4xl font-black">
                  V
                </span>

              </div>

              <div>

                <h1 className="text-4xl font-black">
                  VIBE<span className="text-fuchsia-500">2</span>NITE
                </h1>

                <p className="uppercase tracking-[0.3em] text-xs text-cyan-300">
                  Live The Nite. Own The Vibe.
                </p>

              </div>

            </div>

            {/* MENU */}
            <div className="hidden md:flex items-center gap-10 uppercase text-sm tracking-[0.2em] text-white/70">

              <button>Home</button>
              <button>Features</button>
              <button>For Venues</button>
              <button>Partners</button>
              <button>Contact</button>

            </div>

            {/* CTA */}
            <button
              className="hidden md:block px-7 py-3 rounded-2xl bg-gradient-to-r from-fuchsia-500 via-pink-500 to-purple-500 font-bold shadow-[0_0_45px_rgba(255,0,200,0.8)]"
            >
              DOWNLOAD APP
            </button>

          </div>

          {/* HERO CONTENT */}
          <div className="relative z-20 grid md:grid-cols-2 gap-10 items-center pt-14">

            {/* LEFT */}
            <div>

              <h1 className="text-6xl md:text-8xl font-black leading-[0.9] tracking-[-0.05em] mb-6">

                LIVE THE NITE.

                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-300 via-pink-500 to-purple-400 drop-shadow-[0_0_40px_rgba(255,0,200,1)]">
                  OWN THE VIBE.
                </span>

              </h1>

              <p className="text-xl text-white/75 max-w-xl mb-8 leading-relaxed">
                Real-time vibe scores. Live crowds. The hottest spots near you — right now.
              </p>

              {/* ICON STRIP */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">

                <div className="text-center">
                  <div className="text-cyan-300 text-4xl mb-2">◉</div>
                  <p className="text-xs uppercase text-white/70">
                    Live Vibes
                  </p>
                </div>

                <div className="text-center">
                  <div className="text-fuchsia-400 text-4xl mb-2">◎</div>
                  <p className="text-xs uppercase text-white/70">
                    Real Crowds
                  </p>
                </div>

                <div className="text-center">
                  <div className="text-yellow-300 text-4xl mb-2">◇</div>
                  <p className="text-xs uppercase text-white/70">
                    Rewards
                  </p>
                </div>

                <div className="text-center">
                  <div className="text-purple-300 text-4xl mb-2">▣</div>
                  <p className="text-xs uppercase text-white/70">
                    Check-ins
                  </p>
                </div>

              </div>

              {/* BUTTONS */}
              <div className="flex flex-wrap gap-5">

                <button
                  onClick={() => navigate("/app")}
                  className="px-10 py-5 rounded-3xl bg-gradient-to-r from-fuchsia-500 via-pink-500 to-purple-500 text-lg font-black shadow-[0_0_60px_rgba(255,0,200,1)]"
                >
                  DOWNLOAD FREE
                </button>

                <button className="px-8 py-5 rounded-3xl border border-white/20 bg-white/5 backdrop-blur-xl font-bold">
                  App Store
                </button>

                <button className="px-8 py-5 rounded-3xl border border-white/20 bg-white/5 backdrop-blur-xl font-bold">
                  Google Play
                </button>

              </div>

            </div>

            {/* RIGHT PHONE */}
            <div className="relative flex justify-center">

              {/* GLOW */}
              <div className="absolute w-[550px] h-[550px] bg-fuchsia-500/40 blur-[140px] rounded-full" />

              {/* PHONE */}
              <img
                src="/landing-phone.png"
                alt="Vibe2nite App"
                className="relative z-20 w-full max-w-[520px] rotate-[8deg] drop-shadow-[0_0_120px_rgba(255,0,200,1)]"
              />

            </div>

          </div>

        </section>

        {/* ================= FEATURE STRIP ================= */}

        <section className="px-6 md:px-14 py-8">

          <div className="rounded-[40px] border border-fuchsia-500/30 bg-white/5 backdrop-blur-2xl p-10 shadow-[0_0_60px_rgba(255,0,200,0.15)]">

            <p className="text-center text-fuchsia-400 uppercase tracking-[0.3em] text-sm mb-4">
              BUILT FOR NIGHTLIFE
            </p>

            <h2 className="text-center text-4xl md:text-5xl font-black mb-12">
              EVERYTHING YOU NEED FOR AN EPIC NIGHT OUT
            </h2>

            <div className="grid md:grid-cols-5 gap-8 text-center">

              <div>
                <div className="text-fuchsia-400 text-5xl mb-4">▥</div>
                <h3 className="font-bold mb-2">LIVE VIBE SCORES</h3>
              </div>

              <div>
                <div className="text-cyan-300 text-5xl mb-4">◎</div>
                <h3 className="font-bold mb-2">FIND YOUR CROWD</h3>
              </div>

              <div>
                <div className="text-fuchsia-400 text-5xl mb-4">▣</div>
                <h3 className="font-bold mb-2">SCAN & CHECK IN</h3>
              </div>

              <div>
                <div className="text-pink-300 text-5xl mb-4">◇</div>
                <h3 className="font-bold mb-2">EARN REWARDS</h3>
              </div>

              <div>
                <div className="text-purple-300 text-5xl mb-4">✦</div>
                <h3 className="font-bold mb-2">VENUE PARTNERS</h3>
              </div>

            </div>

          </div>

        </section>

        {/* ================= VENUE TYPES ================= */}

        <section className="px-6 md:px-14 py-10">

          <h2 className="text-center text-5xl font-black mb-12">
            EXPLORE BY VENUE TYPE
          </h2>

          <div className="grid md:grid-cols-3 gap-8">

            {/* BARS */}
            <div className="relative overflow-hidden rounded-[32px] border border-fuchsia-500/30 h-[420px]">

              <img
                src="/bars.jpg"
                alt="Bars"
                className="absolute inset-0 w-full h-full object-cover"
              />

              <div className="absolute inset-0 bg-black/50" />

              <div className="absolute bottom-0 p-8">

                <h3 className="text-5xl font-black mb-3">
                  BARS
                </h3>

                <p className="text-white/70">
                  Cocktail bars • pubs • lounges
                </p>

              </div>

            </div>

            {/* CLUBS */}
            <div className="relative overflow-hidden rounded-[32px] border border-cyan-400/30 h-[420px]">

              <img
                src="/clubs.jpg"
                alt="Clubs"
                className="absolute inset-0 w-full h-full object-cover"
              />

              <div className="absolute inset-0 bg-black/50" />

              <div className="absolute bottom-0 p-8">

                <h3 className="text-5xl font-black mb-3">
                  NITE CLUBS
                </h3>

                <p className="text-white/70">
                  DJs • dance floors • energy
                </p>

              </div>

            </div>

            {/* MUSIC */}
            <div className="relative overflow-hidden rounded-[32px] border border-purple-400/30 h-[420px]">

              <img
                src="/music.jpg"
                alt="Music"
                className="absolute inset-0 w-full h-full object-cover"
              />

              <div className="absolute inset-0 bg-black/50" />

              <div className="absolute bottom-0 p-8">

                <h3 className="text-5xl font-black mb-3">
                  LIVE MUSIC
                </h3>

                <p className="text-white/70">
                  Bands • acoustic • events
                </p>

              </div>

            </div>

          </div>

        </section>

{/* ================= LIVE STATS ================= */}

<section className="px-6 md:px-14 py-8">

  <div className="rounded-[36px] border border-fuchsia-500/20 bg-white/5 backdrop-blur-2xl p-8 shadow-[0_0_60px_rgba(255,0,200,0.12)]">

    <div className="grid md:grid-cols-5 gap-8 text-center">

      {/* Stat */}
      <div>

        <div className="text-fuchsia-400 text-5xl font-black mb-2">
          25K+
        </div>

        <p className="uppercase tracking-[0.2em] text-xs text-white/60">
          Nights Lived
        </p>

      </div>

      {/* Stat */}
      <div>

        <div className="text-cyan-300 text-5xl font-black mb-2">
          12K+
        </div>

        <p className="uppercase tracking-[0.2em] text-xs text-white/60">
          Check-ins Today
        </p>

      </div>

      {/* Stat */}
      <div>

        <div className="text-pink-400 text-5xl font-black mb-2">
          350+
        </div>

        <p className="uppercase tracking-[0.2em] text-xs text-white/60">
          Venues Growing
        </p>

      </div>

      {/* Stat */}
      <div>

        <div className="text-purple-300 text-5xl font-black mb-2">
          50K+
        </div>

        <p className="uppercase tracking-[0.2em] text-xs text-white/60">
          Rewards Earned
        </p>

      </div>

      {/* Stat */}
      <div>

        <div className="text-yellow-300 text-5xl font-black mb-2">
          4.8★
        </div>

        <p className="uppercase tracking-[0.2em] text-xs text-white/60">
          App Rating
        </p>

      </div>

    </div>

  </div>

</section>


      </div>

    </div>
  );
}


