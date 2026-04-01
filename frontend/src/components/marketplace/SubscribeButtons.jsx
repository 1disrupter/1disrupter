import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import { useState } from "react";
import { Button } from "../ui/button";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const SubscribeButton = ({ strategyId, token, onDone }) => {
  const [loading, setLoading] = useState(false);

  const handle = async () => {
    if (!token) { toast.error("Please sign in to subscribe"); return; }
    setLoading(true);
    try {
      const origin = window.location.origin;
      const res = await axios.post(
        `${API}/marketplace/strategies/${strategyId}/checkout`,
        { origin_url: origin },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (res.data.url) {
        window.location.href = res.data.url;
      } else {
        toast.error("Failed to create checkout session");
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail === "Already subscribed to this strategy") {
        toast.info("You are already subscribed");
        if (onDone) onDone();
      } else {
        toast.error(detail || "Failed to start checkout");
      }
    }
    setLoading(false);
  };

  return (
    <Button onClick={handle} disabled={loading} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="subscribe-btn">
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Subscribe — $9.99/mo"}
    </Button>
  );
};

export const UnsubscribeButton = ({ strategyId, token, onDone, size = "default" }) => {
  const [loading, setLoading] = useState(false);

  const handle = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/marketplace/strategies/${strategyId}/cancel-subscription`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success("Subscription canceled");
      if (onDone) onDone();
    } catch (err) {
      // Fallback to old unsubscribe for free subs
      try {
        await axios.post(`${API}/marketplace/strategies/${strategyId}/unsubscribe`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success("Unsubscribed");
        if (onDone) onDone();
      } catch (err2) {
        toast.error(err2.response?.data?.detail || "Failed to unsubscribe");
      }
    }
    setLoading(false);
  };

  return (
    <Button onClick={handle} disabled={loading} variant="outline" size={size} className="border-zinc-700 text-zinc-300" data-testid="unsubscribe-btn">
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Unsubscribe"}
    </Button>
  );
};
