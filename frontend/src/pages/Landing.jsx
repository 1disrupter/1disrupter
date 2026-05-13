
import React from "react";
import { useNavigate } from "react-router-dom";

export default function Landing() {

  const navigate = useNavigate();

  return (
    
<div className="min-h-screen overflow-x-hidden bg-black text-white relative">

 
  {/* CONTENT */}
  
  <div className="relative z-10">
    







        {/* ================= HERO ================= */}

        <section className="relative min-h-screen overflow-hidden px-6 md:px-14 pt-8">

          {/* HERO BG */}
          <div
            className="absolute inset-0 bg-cover bg-center opacity-100"
            style={{
              backgroundImage: "url('/hero-bg.png')",
            }}
          />

          <div className="absolute inset-0 bg-black/40" />

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
                  <span className="block text-xs text-fuchsia-400 mt-1 tracking-[0.2em]"> 
                    COMING SOON
                  </span> 
                </button>
                

                <button className="px-8 py-5 rounded-3xl border border-white/20 bg-white/5 backdrop-blur-xl font-bold">
                  Google Play
                <span className="block text-xs text-cyan-300 mt-1 tracking-[0.2em]"> 
                  COMING SOON
                </span>
                </button>

              </div>

            </div>

{/* RIGHT VISUALS */}
<div className="relative flex items-center justify-center min-h-[700px]">

  {/* Background Glow */}
  <div className="absolute w-[420px] h-[420px] 
bg-fuchsia-500/20 blur-[120px] glow-pulse

 rounded-full" />

  {/* Floating Phone */}
  <div className="relative z-20">

    <img
      src="/landing-phone.png"
      alt="Vibe2nite App"
      
className="
  float-slow    
  w-[320px]
  md:w-[420px]
  rotate-[8deg]
  relative z-30
  drop-shadow-[0_0_120px_rgba(255,0,200,0.45)]
  hover:scale-[1.03]
  transition duration-500
"


    />

  </div>

  {/* Floating Venue Card */}
  <div className="
    absolute
    left-0
    top-[18%]
    w-[240px]
    rounded-[28px]
    border border-fuchsia-400/50
    bg-black/55
    backdrop-blur-[20px]
    overflow-hidden
    shadow-[0_0_40px_rgba(255,0,200,0.25)]
    
hover:-translate-y-3
hover:scale-[1.02]
transition-all
duration-500


  ">

    <img
      src="/bars.png"
      alt="Electric Avenue"
      className="h-[140px] w-full object-cover"
    />

    <div className="p-5">

      <div className="flex items-center justify-between mb-3">

        <span className="text-fuchsia-400 text-xs uppercase tracking-[0.2em]">
          Cocktail Lounge
        </span>

        <span className="text-cyan-300 text-xs font-bold">
          LIVE
        </span>

      </div>

      <h3 className="text-2xl font-black mb-2">
        ELECTRIC AVENUE
      </h3>

      <div className="flex justify-between text-sm text-white/70">

        <span>92% Vibe</span>
        <span>428 inside</span>

      </div>

    </div>

  </div>

  {/* Floating Club Card */}
  <div className="
    absolute
    right-0
    bottom-[12%]
    w-[240px]
    rounded-[28px]
    border border-cyan-300/50
    bg-black/55
    backdrop-blur-[20px]
    overflow-hidden
    shadow-[0_0_40px_rgba(0,217,255,0.2)]
    
hover:-translate-y-3
hover:scale-[1.02]
transition-all
duration-500


  ">

    <img
      src="/clubs.png"
      alt="Neon District"
      className="h-[140px] w-full object-cover"
    />

    <div className="p-5">

      <div className="flex items-center justify-between mb-3">

        <span className="text-cyan-300 text-xs uppercase tracking-[0.2em]">
          Nite Club
        </span>

        <span className="text-fuchsia-400 text-xs font-bold">
          HOT
        </span>

      </div>

      <h3 className="text-2xl font-black mb-2">
        NEON DISTRICT
      </h3>

      <div className="flex justify-between text-sm text-white/70">

        <span>97% Vibe</span>
        <span>812 inside</span>

      </div>

    </div>

  </div>

</div>


           



          </div>

        </section>

        
{/* ================= FEATURE STRIP ================= */}

<section className="px-6 md:px-14 py-8">

  <div className="rounded-[40px] border border-fuchsia-500/30 bg-white/5 backdrop-blur-2xl p-10 shadow-[0_0_60px_rgba(255,0,200,0.15)]">

    {/* Heading */}
    <div className="text-center mb-14">

      <p className="text-fuchsia-400 uppercase tracking-[0.35em] text-sm mb-5">
        DON'T GUESS WHERE TO GO. KNOW.
      </p>

      <h2 className="text-4xl md:text-6xl font-black leading-[1]">
        REAL-TIME NIGHTLIFE
        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 via-pink-500 to-cyan-300">
          INTELLIGENCE
        </span>
      </h2>

    </div>

    {/* Cards */}
    <div className="grid grid-cols-1 md:grid-cols-5 gap-8 text-center">

      {/* Card 1 */}
      <div>

        <div className="text-fuchsia-400 text-5xl mb-4">▥</div>

        <h3 className="font-bold mb-3 text-lg">
          REAL-TIME DATA
        </h3>

        <p className="text-white/60 text-sm leading-relaxed">
          Live crowd levels, wait times & venue activity updated every minute.
        </p>

      </div>

      {/* Card 2 */}
      <div>

        <div className="text-cyan-300 text-5xl mb-4">◎</div>

        <h3 className="font-bold mb-3 text-lg">
          VIBE SCORE
        </h3>

        <p className="text-white/60 text-sm leading-relaxed">
          AI analyzes music, crowd energy and trends in real-time.
        </p>

      </div>

      {/* Card 3 */}
      <div>

        <div className="text-fuchsia-400 text-5xl mb-4">▣</div>

        <h3 className="font-bold mb-3 text-lg">
          SMART RECS
        </h3>

        <p className="text-white/60 text-sm leading-relaxed">
          Get personalized nightlife recommendations based on your vibe.
        </p>

      </div>

      {/* Card 4 */}
      <div>

        <div className="text-pink-300 text-5xl mb-4">◇</div>

        <h3 className="font-bold mb-3 text-lg">
          DISCOVER MORE
        </h3>

        <p className="text-white/60 text-sm leading-relaxed">
          Find hidden gems, upcoming events and the hottest spots before they peak.
        </p>

      </div>

      {/* Card 5 */}
      <div>

        <div className="text-purple-300 text-5xl mb-4">✦</div>

        <h3 className="font-bold mb-3 text-lg">
          OWN THE NIGHT
        </h3>

        <p className="text-white/60 text-sm leading-relaxed">
          Save favorite spots, share with friends and make every night legendary.
        </p>

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
            
<div className="group relative overflow-hidden rounded-[32px]

 border border-fuchsia-500/30 h-[420px]">

              <img
                src="/bars.png"
                alt="Bars"
                
className="
  absolute
  inset-0
  w-full
  h-full
  object-cover
  scale-100
  group-hover:scale-110
  transition-transform
  duration-[4000ms]
"

              />

              <div className="absolute inset-0
bg-gradient-to-t from-black via-black/40 to-black/10

" />

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
             
<div className="group relative overflow-hidden rounded-[32px]

border border-cyan-400/30 h-[420px]">

              <img
                src="/clubs.png"
                alt="Clubs"
            
className="
  absolute
  inset-0
  w-full
  h-full
  object-cover
  scale-100
  group-hover:scale-110
  transition-transform
  duration-[4000ms]
"


              />

              <div className="absolute inset-0
bg-gradient-to-t from-black via-black/40 to-black/10

" />

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
            
<div className="group relative overflow-hidden rounded-[32px]

 border border-purple-400/30 h-[420px]">

              <img
                src="/music.png"
                alt="Music"
              
className="
  absolute
  inset-0
  w-full
  h-full
  object-cover
  scale-100
  group-hover:scale-110
  transition-transform
  duration-[4000ms]
"


              />

              <div className="absolute inset-0 
bg-gradient-to-t from-black via-black/40 to-black/10

" />

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
{/* ================= VENUE OWNER CTA ================= */}

<section className="px-6 md:px-14 py-10">

  <div className="relative overflow-hidden rounded-[40px] border border-fuchsia-500/30 min-h-[420px] shadow-[0_0_70px_rgba(255,0,200,0.18)]">

    {/* Background Image */}
    <img
      src="/owner.png"
      alt="Venue Owner"
      className="absolute inset-0 w-full h-full object-cover"
    />

    {/* Overlay */}
    <div className="absolute inset-0 bg-black/65" />

    {/* Neon Glow */}
    <div className="absolute top-[-120px] right-[-120px] w-[400px] h-[400px] bg-fuchsia-500/30 blur-[120px] rounded-full" />

    {/* Content */}
    <div className="relative z-20 p-10 md:p-16 max-w-3xl">

      <p className="uppercase tracking-[0.3em] text-cyan-300 text-sm mb-5">
        FOR VENUES
      </p>

      <h2 className="text-5xl md:text-7xl font-black leading-[0.92] tracking-[-0.05em] mb-6">

        OWN A BAR,
        CLUB OR
        LIVE VENUE?

      </h2>

      <p className="text-xl text-white/75 leading-relaxed mb-10 max-w-2xl">
        Get discovered live by nightlife crowds, promote your venue,
        increase footfall and become part of the Vibe2nite network.
      </p>

      {/* Buttons */}
      <div className="flex flex-wrap gap-5">

        <button
          onClick={() => navigate("/owner")}
          className="px-10 py-5 rounded-3xl bg-gradient-to-r from-fuchsia-500 via-pink-500 to-purple-500 text-lg font-black shadow-[0_0_60px_rgba(255,0,200,1)] hover:scale-105 transition"
        >
          CLAIM YOUR VENUE
        </button>

        <button
          className="px-10 py-5 rounded-3xl border border-cyan-400/40 bg-cyan-400/10 text-cyan-300 text-lg font-black hover:bg-cyan-400/20 transition"
        >
        
<button
  onClick={() =>
    document.getElementById("venues")?.scrollIntoView({
      behavior: "smooth",
    })
  }
  className="px-10 py-5 rounded-3xl border border-cyan-400/40 bg-cyan-400/10 text-cyan-300 text-lg font-black hover:bg-cyan-400/20 transition"
>
  LEARN MORE
  
</button>

  
        

      </div>

    </div>

  </div>

</section>

{/* ================= WHY JOIN VIBE2NITE ================= */}

<section className="px-6 md:px-14 py-12">

  <div className="rounded-[40px] border border-fuchsia-500/20 bg-white/5 backdrop-blur-2xl p-10 md:p-16 shadow-[0_0_60px_rgba(255,0,200,0.12)]">

    <div className="max-w-5xl mx-auto text-center">

      <p className="uppercase tracking-[0.35em] text-cyan-300 text-sm mb-5">
        WHY VIBE2NITE?
      </p>

      <h2 className="text-5xl md:text-7xl font-black leading-[0.95] tracking-[-0.05em] mb-8">

        HELPING NIGHTLIFE
        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 via-pink-500 to-cyan-300">
          COME ALIVE
        </span>

      </h2>

      <p className="text-xl text-white/75 leading-relaxed mb-10 max-w-4xl mx-auto">
        Vibe2nite was created to help bars, clubs and live music venues increase visibility, attract more customers and bring real nightlife energy back into local venues.
      </p>

      <p className="text-lg text-white/60 leading-relaxed mb-14 max-w-4xl mx-auto">
        We help tourists and locals discover the best places to go based on live crowd activity, atmosphere, music and real-time vibe scores — making it easier to find the perfect night out for every age group and every vibe.
      </p>

      {/* BENEFITS */}
      <div className="grid md:grid-cols-4 gap-8 text-center">

        <div>
          <div className="text-fuchsia-400 text-5xl mb-4">🔥</div>
          <h3 className="font-black text-lg mb-2">
            MORE FOOTFALL
          </h3>
          <p className="text-white/60 text-sm">
            Bring more people directly to your venue.
          </p>
        </div>

        <div>
          <div className="text-cyan-300 text-5xl mb-4">📍</div>
          <h3 className="font-black text-lg mb-2">
            LIVE DISCOVERY
          </h3>
          <p className="text-white/60 text-sm">
            Help users find your venue in real-time.
          </p>
        </div>

        <div>
          <div className="text-pink-400 text-5xl mb-4">🎶</div>
          <h3 className="font-black text-lg mb-2">
            PROMOTE EVENTS
          </h3>
          <p className="text-white/60 text-sm">
            Showcase DJs, live music and nightlife experiences.
          </p>
        </div>

        <div>
          <div className="text-purple-300 text-5xl mb-4">⚡</div>
          <h3 className="font-black text-lg mb-2">
            GROW YOUR BRAND
          </h3>
          <p className="text-white/60 text-sm">
            Become part of the Vibe2nite nightlife network.
          </p>
        </div>

      </div>

    </div>

  </div>

</section>


{/* ================= FOUNDING VENUES WAITLIST ================= */}

<section
  id="venues"
  className="px-6 md:px-14 py-20"
>



  <div className="relative overflow-hidden rounded-[40px] border border-cyan-400/20 bg-black/60 backdrop-blur-2xl p-10 md:p-16 shadow-[0_0_80px_rgba(0,217,255,0.12)]">

    {/* Glow */}
    <div className="absolute top-[-100px] left-[-100px] w-[300px] h-[300px] bg-cyan-400/20 blur-[120px] rounded-full" />

    <div className="relative z-20">

      <p className="uppercase tracking-[0.4em] text-cyan-300 text-sm mb-5">
        FOUNDING VENUES
      </p>

      <h2 className="text-5xl md:text-7xl font-black leading-[0.92] tracking-[-0.05em] mb-6">

        JOIN THE
        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-fuchsia-400 to-pink-500">
          WAITLIST
        </span>

      </h2>

      <p className="text-xl text-white/70 max-w-3xl leading-relaxed mb-12">
        We’re onboarding a limited number of bars, clubs and live venues for the first Vibe2nite launch in Benalmádena.
      </p>

      {/* FORM */}
      
<form
  action="https://formspree.io/f/xgodqvyp"
  method="POST"
  className="grid md:grid-cols-2 gap-6"
>



        <input
          type="text"
          name="venue"
          placeholder="Venue Name"
          className="bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-white placeholder:text-white/30 outline-none focus:border-fuchsia-500"
        />

        <input
          type="text"
          name="contact"
          placeholder="Contact Name"
          className="bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-white placeholder:text-white/30 outline-none focus:border-fuchsia-500"
        />

        <input
          type="email"
          name="email"
          placeholder="Email Address"
          className="bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-white placeholder:text-white/30 outline-none focus:border-fuchsia-500"
        />

        <input
          type="text"
          name="phone"
          placeholder="WhatsApp / Phone"
          className="bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-white placeholder:text-white/30 outline-none focus:border-fuchsia-500"
        />

        <select
          name="venueType"
          className="bg-black border border-white/10 rounded-2xl px-6 py-5 text-white outline-none focus:border-fuchsia-500"
        >
          <option>Venue Type</option>
          <option>Bar</option>
          <option>Nightclub</option>
          <option>Cocktail Lounge</option>
          <option>Live Music Venue</option>
          <option>DJ / Promoter</option>
        </select>

        <input
          type="text"
          name="city"
          placeholder="City"
          className="bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-white placeholder:text-white/30 outline-none focus:border-fuchsia-500"
        />

        <textarea
          name="message"
          placeholder="Tell us about your venue..."
          rows="5"
          className="md:col-span-2 bg-white/5 border border-white/10 rounded-2xl px-6 py-5 text-white placeholder:text-white/30 outline-none focus:border-fuchsia-500"
        />

        <button
          type="submit"
          className="md:col-span-2 py-6 rounded-3xl bg-gradient-to-r from-fuchsia-500 via-pink-500 to-cyan-400 text-xl font-black shadow-[0_0_60px_rgba(255,0,200,0.4)] hover:scale-[1.02] transition"
        >
          JOIN FOUNDING VENUES
        </button>

      </form>

    </div>

  </div>

</section>




{/* ================= ENTER THE APP ================= */}

<section className="px-6 md:px-14 py-24">

  <div className="text-center">

    <p className="uppercase tracking-[0.4em] text-cyan-300 text-sm mb-6">
      THE NIGHT IS LIVE
    </p>

    <h2 className="text-6xl md:text-8xl font-black leading-[0.9] tracking-[-0.05em] mb-10">

      ENTER THE
      <span className="block text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 via-pink-500 to-cyan-300">
        VIBE WORLD
      </span>

    </h2>

    <p className="text-xl text-white/70 max-w-3xl mx-auto mb-16">
      Real crowds. Real venues. Real nightlife energy happening live around you.
    </p>

    {/* ENTER APP PORTAL */}
    <div className="mt-20 flex justify-center">

      <button
        onClick={() => navigate("/app")}
        
className="
  group
  relative
 px-10 md:px-20
  py-8 md:py-10
  rounded-full
  overflow-hidden
  bg-black/80
  backdrop-blur-2xl
  border border-fuchsia-500/40
  shadow-[0_0_120px_rgba(255,0,200,0.35)]
  hover:scale-[1.04]
  transition-all
  duration-700
"


      >

        {/* Glow */}
        
<div className="absolute -inset-10 bg-gradient-to-r from-fuchsia-500/20 via-pink-500/10 to-cyan-400/20 blur-[80px] opacity-60 group-hover:opacity-100 transition duration-700" />


        <div className="absolute inset-0 bg-gradient-to-r from-fuchsia-500/20 via-pink-500/20 to-cyan-400/20 opacity-0 group-hover:opacity-100 transition duration-500" />

        <div className="relative z-20">

          <p className="text-xs uppercase tracking-[0.4em] text-cyan-300 mb-2">
            ENTER THE LIVE EXPERIENCE
          </p>

          <h3 className=" 
text-5xl md:text-7xl

font-black text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 via-pink-500 to-cyan-300">
            ENTER VIBE2NITE
          </h3>

        </div>

      </button>

    </div>

  </div>

</section>
    
  </div>
  
</div>    

  );
}

