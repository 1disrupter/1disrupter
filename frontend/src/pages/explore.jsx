import React from "react";
import VibeCard from "../components/VibeCard";

export default function Explore() {

  const venues = [
    {
      venue: {
        id: "101",
        name: "Ocean Club",
        image_url:
          "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1200&auto=format&fit=crop",
      },
      vibe: { vibe_score: 9.2 },
      distance_km: 1,
      tagline: "Beach Club · DJs",
    },

    {
      venue: {
        id: "102",
        name: "Sky Lounge",
        image_url:
          "https://images.unsplash.com/photo-1496024840928-4c417adf211d?q=80&w=1200&auto=format&fit=crop",
      },
      vibe: { vibe_score: 8.7 },
      distance_km: 2,
      tagline: "Cocktails · Rooftop",
    },

    {
      venue: {
        id: "103",
        name: "Electric Bar",
        image_url:
          "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?q=80&w=1200&auto=format&fit=crop",
      },
      vibe: { vibe_score: 8.9 },
      distance_km: 3,
      tagline: "Live Music · Late Night",
    },
  ];

  return (
    <div className="min-h-screen bg-black text-white p-4">

      <h1 className="text-4xl font-bold mb-6">
        Explore More Venues
      </h1>

      <div className="grid gap-5 md:grid-cols-3">

        {venues.map((venue, i) => (
          <VibeCard
            key={i}
            title="Trending"
            data={venue}
          />
        ))}

      </div>

    </div>
  );
}
