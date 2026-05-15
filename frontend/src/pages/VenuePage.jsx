
import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import venues from "../data/venues";
import { ArrowLeft, MapPin, Flame } from "lucide-react";

export default function VenuePage() {

  const { id } = useParams();
  const navigate = useNavigate();

  const venue = venues.find((v) => v.id === Number(id));

const saveVenue = () => {

  const saved =
    JSON.parse(localStorage.getItem("v2n_favourites")) || [];

  const alreadySaved = saved.find((v) => v.id === venue.id);

  if (alreadySaved) return;

  saved.push(venue);

  localStorage.setItem(
    "v2n_favourites",
    JSON.stringify(saved)
  );

  alert(`${venue.name} saved to favourites`);

};


  if (!venue) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        Venue not found.
      </div>
    );
  }

  return (

    <div className="min-h-screen bg-black text-white">

      {/* HERO IMAGE */}
      <div className="relative h-[45vh] overflow-hidden">

        <img
          src="/bars.png"
          alt={venue.name}
          className="w-full h-full object-cover"
        />

        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />

        {/* BACK BUTTON */}
        <button
          onClick={() => navigate(-1)}
          className="absolute top-6 left-6 z-30 flex items-center gap-2 bg-black/60 backdrop-blur-xl px-5 py-3 rounded-2xl border border-white/10"
        >
          <ArrowLeft size={18} />
          Back
        </button>

        {/* VENUE TITLE */}
        <div className="absolute bottom-10 left-8 z-20">

          <p className="text-fuchsia-400 uppercase tracking-[0.25em] text-sm mb-3">
            {venue.tag}
          </p>

          <h1 className="text-5xl md:text-7xl font-black">
            {venue.name}
          </h1>

          <p className="text-xl text-white/70 mt-3">
            {venue.type}
          </p>

        </div>

      </div>

      {/* CONTENT */}
      <div className="px-6 md:px-14 py-10">

        {/* LIVE STATUS */}
        <div className="grid md:grid-cols-3 gap-6 mb-10">

          <div className="rounded-[28px] border border-fuchsia-500/30 bg-white/5 backdrop-blur-2xl p-6">

            <Flame className="text-fuchsia-400 mb-4" size={34} />

            <h3 className="text-2xl font-black mb-2">
              LIVE VIBE
            </h3>

            <p className="text-white/70">
              {venue.vibe}
            </p>

          </div>

          <div className="rounded-[28px] border border-cyan-400/30 bg-white/5 backdrop-blur-2xl p-6">

            <MapPin className="text-cyan-300 mb-4" size={34} />

            <h3 className="text-2xl font-black mb-2">
              LOCATION
            </h3>

            <p className="text-white/70">
              Benalmádena, Spain
            </p>

          </div>

          <div className="rounded-[28px] border border-purple-400/30 bg-white/5 backdrop-blur-2xl p-6">

            <div className="text-purple-300 text-4xl mb-4">
              🎶
            </div>

            <h3 className="text-2xl font-black mb-2">
              MUSIC
            </h3>

            <p className="text-white/70">
              Live DJs • House • Party Vibes
            </p>

          </div>

        </div>

        {/* ABOUT */}
        <div className="rounded-[32px] border border-white/10 bg-white/5 backdrop-blur-2xl p-8 mb-10">

          <h2 className="text-4xl font-black mb-5">
            ABOUT THIS VENUE
          </h2>

          <p className="text-white/70 leading-relaxed text-lg">
            Experience one of Benalmádena’s hottest nightlife destinations with live music, cocktails, vibrant crowds and unforgettable nightlife energy powered by Vibe2nite.
          </p>

        </div>

        {/* ACTION BUTTONS */}
        <div className="flex flex-wrap gap-5">

          <button
            onClick={() =>
              window.open(
                `https://www.google.com/maps/dir/?api=1&destination=${venue.lat},${venue.lng}`,
                "_blank"
              )
            }
            className="px-10 py-5 rounded-3xl bg-gradient-to-r from-fuchsia-500 via-pink-500 to-purple-500 text-lg font-black shadow-[0_0_60px_rgba(255,0,200,0.5)]"
          >
            GET DIRECTIONS
          </button>
       
<button
  onClick={saveVenue}
  className="px-10 py-5 rounded-3xl border border-cyan-400/30 bg-cyan-400/10 text-cyan-300 text-lg font-black"
>
  SAVE VENUE
</button>

<button
  onClick={() => navigate("/owner")}
    className="px-10 py-5 rounded-3xl border border-white/10 bg-white/5 text-white text-lg font-black"
          >
            CLAIM VENUE
          </button>

        </div>

      </div>

    </div>

  );

}


