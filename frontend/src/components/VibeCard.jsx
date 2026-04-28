export default function VibeCard({ title, data }) {
  if (!data) return null;

  const isPlaceholder = data.placeholder;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <h4 className="text-xs uppercase tracking-wide text-accent-pink mb-1">
        {title}
      </h4>

      <h3 className="font-semibold text-lg">
        {data.name || "Coming soon"}
      </h3>

      <p className="text-white/50 text-sm">
        {data.address || ""}
      </p>

      <div className="flex items-center justify-between mt-3">
        <span className="text-accent-pink font-bold text-xl">
          {data.score || 0}
        </span>
        <span className="text-white/40 text-xs uppercase tracking-wide">
          vibe score
        </span>
      </div>

      <button
        disabled={isPlaceholder}
        className={`mt-3 w-full py-2 rounded-lg font-semibold ${
          isPlaceholder
            ? "bg-white/10 text-white/40 cursor-not-allowed"
            : "bg-accent-pink text-black"
        }`}
      >
        {isPlaceholder ? "Coming Soon" : "GO HERE"}
      </button>
    </div>
  );
}
