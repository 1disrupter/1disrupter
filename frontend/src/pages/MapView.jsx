
import React, { useEffect, useState } from "react";





import { useNavigate } from "react-router-dom";
import { ArrowLeft, Flame } from "lucide-react";
import venues from "../data/venues";

export default function MapView() {
  
const [liveVenues, setLiveVenues] = useState(venues);

useEffect(() => {

  const interval = setInterval(() => {

    setLiveVenues((prev) =>
      prev.map((venue) => {

        const fluctuation =
          Math.floor(Math.random() * 7) - 3;

        let updatedScore =
          venue.busyScore + fluctuation;

        updatedScore = Math.max(
          55,
          Math.min(100, updatedScore)
        );

        return {
          ...venue,
          busyScore: updatedScore,
        };

      })
    );

  }, 4000);

  return () => clearInterval(interval);

}, []);



  const navigate = useNavigate();

const [activeVenue, setActiveVenue] = useState(null);
const [searchTerm, setSearchTerm] = useState("");
const [activeCategory, setActiveCategory] = useState("ALL");
const [searchQuery, setSearchQuery] = useState("");
  
const getHeatStyles = (score) => {

  if (score >= 95) {
    return {
      glow: "bg-red-500/50",
      core: "bg-red-500 border-red-300",
      pulse: "animate-ping",
    };
  }

  if (score >= 85) {
    return {
      glow: "bg-orange-500/50",
      core: "bg-orange-500 border-orange-300",
      pulse: "animate-pulse",
    };
  }

  if (score >= 70) {
    return {
      glow: "bg-green-500/40",
      core: "bg-green-500 border-green-300",
      pulse: "",
    };
  }

  return {
    glow: "bg-cyan-500/30",
    core: "bg-cyan-500 border-cyan-300",
    pulse: "",
  };

};


const filteredVenues = liveVenues.filter((venue) => {
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
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_top,rgba(255,0,200,0.6),transparent_40%)] pointer-events-none z-1" />

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
      
{/* LIVE HEAT LEGEND */}
      
<div className="relative z-30 px-6 py-4">

  <div className="inline-flex flex-wrap items-center gap-3 rounded-3xl border border-white/10 bg-black/60 backdrop-blur-2xl px-5 py-4">

    <div className="flex items-center gap-2 text-sm">
      <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
      <span className="text-white/70">
        🔥 Packed
      </span>
    </div>

    <div className="flex items-center gap-2 text-sm">
      <div className="w-3 h-3 rounded-full bg-orange-500 animate-pulse" />
      <span className="text-white/70">
        🟠 Busy
      </span>
    </div>

    <div className="flex items-center gap-2 text-sm">
      <div className="w-3 h-3 rounded-full bg-green-500" />
      <span className="text-white/70">
        🟢 Good Vibes
      </span>
    </div>

    <div className="flex items-center gap-2 text-sm">
      <div className="w-3 h-3 rounded-full bg-cyan-400" />
      <span className="text-white/70">
        🌙 Chill
      </span>
    </div>

  </div>

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
        
{filteredVenues.slice(0, 5).map((venue, index) => {

  const heat = getHeatStyles(venue.busyScore);

  return (








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

<div
  className={`absolute inset-0 rounded-full blur-xl w-10 h-10 ${heat.glow} ${heat.pulse}`}
/>

<div
  className={`relative w-14 h-14 rounded-full border shadow-[0_0_40px_rgba(255,255,255,0.3)] flex items-center justify-center text-white font-black text-sm ${heat.core}`}
>
  {venue.busyScore}%
</div>



  

      

    </button>

  </div>

  );

})}




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

<p className="mt-2 text-fuchsia-400 font-black">
  LIVE CROWD: {activeVenue.busyScore}%
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

        


