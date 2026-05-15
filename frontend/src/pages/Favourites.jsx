
import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Heart, MapPin } from "lucide-react";

export default function Favourites() {

  const navigate = useNavigate();

  const favourites =
    JSON.parse(localStorage.getItem("v2n_favourites")) || [];

  return (

    <div className="min-h-screen bg-black text-white">

      {/* HEADER */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-white/10 backdrop-blur-xl">

        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-white/70 hover:text-white transition"
        >
          <ArrowLeft size={18} />
          Back
        </button>

        <h1 className="text-xl font-black tracking-[0.2em]">
          FAVOURITES
        </h1>

        <div />

      </div>

      {/* CONTENT */}
      <div className="p-6">

        {favourites.length === 0 ? (

          <div className="text-center py-24">

            <Heart
              className="mx-auto text-fuchsia-500 mb-6"
              size={60}
            />

            <h2 className="text-3xl font-black mb-4">
              No Saved Venues Yet
            </h2>

            <p className="text-white/50">
              Save venues to build your nightlife collection.
            </p>

          </div>

        ) : (

          <div className="grid gap-5">

            {favourites.map((venue) => (

              <div
                key={venue.id}
                className="rounded-[28px] border border-white/10 bg-white/5 backdrop-blur-2xl p-6"
              >

                <div className="flex items-start justify-between">

                  <div>

                    <p className="text-fuchsia-400 text-xs uppercase tracking-[0.2em] mb-2">
                      {venue.tag}
                    </p>

                    <h2 className="text-3xl font-black">
                      {venue.name}
                    </h2>

                    <p className="text-white/60 mt-2">
                      {venue.vibe}
                    </p>

                  </div>

                  <Heart
                    className="text-fuchsia-500"
                    fill="currentColor"
                  />

                </div>

                <div className="flex gap-4 mt-6">

                  <button
                    onClick={() => navigate(`/venue/${venue.id}`)}
                    className="flex-1 py-4 rounded-2xl bg-fuchsia-500 text-white font-black"
                  >
                    VIEW VENUE
                  </button>

                  <button
                    onClick={() =>
                      window.open(
                        `https://www.google.com/maps/dir/?api=1&destination=${venue.lat},${venue.lng}`,
                        "_blank"
                      )
                    }
                    className="px-6 rounded-2xl border border-cyan-400/30 bg-cyan-400/10 text-cyan-300"
                  >
                    <MapPin size={22} />
                  </button>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </div>

  );

}

