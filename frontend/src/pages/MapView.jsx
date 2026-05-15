
import React, { useState } from "react";


import { useNavigate } from "react-router-dom";
import { ArrowLeft, Flame } from "lucide-react";
import venues from "../data/venues";

export default function MapView() {
  const navigate = useNavigate();

const [activeVenue, setActiveVenue] = useState(null);
const [searchTerm, setSearchTerm] = useState("");
const [activeCategory, setActiveCategory] = useState("ALL");
const [searchQuery, setSearchQuery] = useState("");
const filteredVenues = venues.filter((venue) => { 
  const matchesCategory = activeCategory === "ALL"
    ? true
    : venue.type.toLowerCase() === activeCategory.toLowerCase();
  const matchesSearch = 
    venue.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    venue.type.toLowerCase().includes(searchQuery.toLowerCase());
  
  return matchesCategory && matchesSearch;
});




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
   
{/* SEARCH */}
<div className="relative z-30 px-6 pt-4">

  <input
    type="text"
    placeholder="Search venues, music, bars..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    className="w-full rounded-2xl bg-white/5 border border-white/10 px-6 py-4 text-white placeholder:text-white/30 outline-none focus:border-fuchsia-500 backdrop-blur-xl"
  />

</div>

   
{/* FILTERS */}
      
<div className="relative z-30 flex gap-3 overflow-x-auto px-6 py-4 border-b border-white/10 bg-black/40 backdrop-blur-xl">

  {[
    "ALL",
    "Cocktail Bar",
    "Irish Bar",
    "Pub",
    "Beach Bar",
    "Nightclub",
    "Live Music",
  ].map((category) => (

    <button
      key={category}
      onClick={() => setActiveCategory(category)}
      className={`px-5 py-3 rounded-2xl whitespace-nowrap text-sm font-bold transition ${
        activeCategory === category
          ? "bg-fuchsia-500 text-white"
          : "bg-white/5 text-white/60 border border-white/10"
      }`}
    >
      {category}
    </button>

  ))}

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
        

{filteredVenues.slice(0, 5).map((venue, index) => (



  <div
    key={venue.id}
    className="absolute z-20"
    style={{
      top: `${25 + index * 14}%`,
      left: `${20 + index * 15}%`,
    }}
  >

    {/* GLOW PIN */}
    <button
      
onClick={() => navigate(`/venue/${venue.id}`)}


      className="relative"
    >

      <div className="absolute inset-0 animate-ping rounded-full bg-fuchsia-500/40 blur-xl w-10 h-10" />

      <div className="relative w-10 h-10 rounded-full bg-fuchsia-500 border border-fuchsia-300 shadow-[0_0_40px_rgba(255,0,200,0.9)]" />

    </button>

  </div>

))}

{/* ACTIVE VENUE CARD */}
{activeVenue && (

  <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-40 w-[320px] rounded-[30px] border border-fuchsia-500/30 bg-black/80 backdrop-blur-2xl p-6 shadow-[0_0_60px_rgba(255,0,200,0.3)]">

    <p className="text-fuchsia-400 text-xs uppercase tracking-[0.2em] mb-2">
      {activeVenue.tag}
    </p>

    <h2 className="text-3xl font-black mb-2">
      {activeVenue.name}
    </h2>

    <p className="text-white/60 mb-5">
      {activeVenue.vibe}
    </p>

    <button
      onClick={() =>
        window.open(
          `https://www.google.com/maps/dir/?api=1&destination=${activeVenue.lat},${activeVenue.lng}`,
          "_blank"
        )
      }
      className="w-full py-4 rounded-2xl bg-fuchsia-500 text-white font-black"
    >
      GET DIRECTIONS
    </button>

  </div>

)}
</div> 
    </div> 
  ); 
}

        


