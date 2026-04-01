import { useState } from "react";
import { Star, ChevronDown, ChevronUp, Send, Loader2 } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ReviewsList = ({ reviews = [], strategyId, token, isOwner, onReviewAdded }) => {
  const [showAll, setShowAll] = useState(false);
  const [reviewText, setReviewText] = useState("");
  const [reviewRating, setReviewRating] = useState(5);
  const [submitting, setSubmitting] = useState(false);

  const displayed = showAll ? reviews : reviews.slice(0, 3);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) { toast.error("Please sign in to review"); return; }
    setSubmitting(true);
    try {
      await axios.post(`${API}/marketplace/strategies/${strategyId}/review`,
        { rating: reviewRating, comment: reviewText.trim() },
        { headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` } }
      );
      toast.success("Review submitted!");
      setReviewText("");
      setReviewRating(5);
      if (onReviewAdded) onReviewAdded();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit review");
    }
    setSubmitting(false);
  };

  return (
    <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="reviews-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <Star className="w-4 h-4 text-[#7B61FF]" /> Reviews ({reviews.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {reviews.length === 0 ? (
          <p className="text-zinc-600 text-xs py-4 text-center">No reviews yet. Be the first!</p>
        ) : (
          <div className="space-y-3">
            {displayed.map((r, i) => (
              <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/20" data-testid={`review-item-${i}`}>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-300 font-medium">{r.user_name}</span>
                    <div className="flex items-center gap-0.5">
                      {[...Array(5)].map((_, j) => (
                        <Star key={j} className={`w-3 h-3 ${j < r.rating ? "text-amber-400 fill-current" : "text-zinc-700"}`} />
                      ))}
                    </div>
                  </div>
                  <span className="text-[10px] text-zinc-600">{r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}</span>
                </div>
                {r.comment && <p className="text-xs text-zinc-500 mt-1">{r.comment}</p>}
              </div>
            ))}
            {reviews.length > 3 && (
              <button onClick={() => setShowAll(!showAll)} className="text-xs text-[#7B61FF] flex items-center gap-1 mx-auto mt-2">
                {showAll ? <><ChevronUp className="w-3 h-3" /> Show less</> : <><ChevronDown className="w-3 h-3" /> Show all {reviews.length} reviews</>}
              </button>
            )}
          </div>
        )}

        {/* Review form */}
        {token && !isOwner && (
          <form onSubmit={handleSubmit} className="mt-4 pt-4 border-t border-zinc-800/50" data-testid="review-form">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xs text-zinc-500">Your rating:</span>
              <div className="flex gap-0.5">
                {[1, 2, 3, 4, 5].map(v => (
                  <button key={v} type="button" onClick={() => setReviewRating(v)} data-testid={`rating-star-${v}`}>
                    <Star className={`w-4 h-4 cursor-pointer transition-colors ${v <= reviewRating ? "text-amber-400 fill-current" : "text-zinc-700 hover:text-zinc-500"}`} />
                  </button>
                ))}
              </div>
            </div>
            <div className="flex gap-2">
              <input
                value={reviewText}
                onChange={e => setReviewText(e.target.value)}
                placeholder="Write a review..."
                className="flex-1 h-9 px-3 bg-[#050505] border border-zinc-800 rounded text-sm text-zinc-300 placeholder-zinc-600 outline-none focus:border-[#7B61FF]/50"
                data-testid="review-input"
              />
              <Button type="submit" disabled={submitting} size="sm" className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 h-9" data-testid="submit-review-btn">
                {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              </Button>
            </div>
          </form>
        )}
      </CardContent>
    </Card>
  );
};

export default ReviewsList;
