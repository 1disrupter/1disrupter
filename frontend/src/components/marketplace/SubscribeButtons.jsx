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
      await axios.post(`${API}/marketplace/strategies/${strategyId}/subscribe`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success("Subscribed successfully!");
      if (onDone) onDone();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to subscribe");
    }
    setLoading(false);
  };

  return (
    <Button onClick={handle} disabled={loading} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="subscribe-btn">
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Subscribe"}
    </Button>
  );
};

export const UnsubscribeButton = ({ strategyId, token, onDone, size = "default" }) => {
  const [loading, setLoading] = useState(false);

  const handle = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/marketplace/strategies/${strategyId}/unsubscribe`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success("Unsubscribed");
      if (onDone) onDone();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to unsubscribe");
    }
    setLoading(false);
  };

  return (
    <Button onClick={handle} disabled={loading} variant="outline" size={size} className="border-zinc-700 text-zinc-300" data-testid="unsubscribe-btn">
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Unsubscribe"}
    </Button>
  );
};
