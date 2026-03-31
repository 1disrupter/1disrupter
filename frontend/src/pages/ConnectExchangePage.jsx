import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Check, AlertTriangle, Loader2, Shield, Unplug } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { useAuth } from "../contexts/AuthContext";

const API = process.env.REACT_APP_BACKEND_URL;

const EXCHANGES = [
  { id: "binance_testnet", label: "Binance Testnet", tag: "Testnet" },
];

export default function ConnectExchangePage() {
  const { user, tokens } = useAuth();
  const navigate = useNavigate();
  const [exchange, setExchange] = useState("binance_testnet");
  const [apiKey, setApiKey] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState(true);

  const headers = { Authorization: `Bearer ${tokens?.access_token}`, "Content-Type": "application/json" };

  useEffect(() => {
    if (!tokens?.access_token) { setLoadingStatus(false); return; }
    fetch(`${API}/api/exchange/status`, { headers: { Authorization: `Bearer ${tokens.access_token}` } })
      .then(r => r.json())
      .then(d => setStatus(d))
      .catch(() => {})
      .finally(() => setLoadingStatus(false));
  }, [tokens]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!apiKey || !secretKey || sending) return;
    setSending(true);
    setResult(null);
    try {
      const res = await fetch(`${API}/api/exchange/connect`, {
        method: "POST", headers,
        body: JSON.stringify({ exchange, api_key: apiKey, secret_key: secretKey }),
      });
      const data = await res.json();
      if (!res.ok) { setResult({ ok: false, msg: data.detail || "Connection failed" }); setSending(false); return; }
      setResult({ ok: true, balances: data.balances });
      setApiKey(""); setSecretKey("");
      toast.success("Exchange connected successfully");
      // Refresh status
      const sr = await fetch(`${API}/api/exchange/status`, { headers: { Authorization: `Bearer ${tokens.access_token}` } });
      if (sr.ok) setStatus(await sr.json());
    } catch { setResult({ ok: false, msg: "Network error. Please try again." }); }
    setSending(false);
  };

  const handleDisconnect = async () => {
    try {
      await fetch(`${API}/api/exchange/disconnect`, { method: "DELETE", headers });
      setStatus(null); setResult(null);
      toast.success("Exchange disconnected");
    } catch { toast.error("Failed to disconnect"); }
  };

  if (!user && !loadingStatus) {
    return (
      <div className="min-h-screen pt-28 px-4 text-center" data-testid="exchange-auth-required">
        <Shield className="w-12 h-12 mx-auto mb-4 text-zinc-600" />
        <h2 className="text-xl font-bold text-white mb-2">Authentication Required</h2>
        <p className="text-zinc-500 text-sm mb-6">Please log in to connect your exchange.</p>
        <Link to="/login"><Button className="bg-[#7B61FF] hover:bg-[#6A50E5]">Log In</Button></Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-28 px-4 pb-16" data-testid="connect-exchange-page">
      <div className="max-w-lg mx-auto">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <Link to="/dashboard" className="inline-flex items-center text-xs text-zinc-500 hover:text-white mb-6 transition-colors">
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5" /> Back to Dashboard
          </Link>

          <h1 className="text-2xl font-bold font-['Outfit'] tracking-tight text-white mb-1" data-testid="exchange-page-title">
            Connect Exchange
          </h1>
          <p className="text-sm text-zinc-500 mb-8">Link your exchange account to view balances and positions. Testnet only — no live trading.</p>

          {/* Already connected */}
          {status?.connected && (
            <Card className="bg-[#0A0A0A] border-zinc-800 mb-8" data-testid="exchange-connected-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-[#00FF94]/10 flex items-center justify-center">
                      <Check className="w-4 h-4 text-[#00FF94]" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">Binance Testnet</p>
                      <p className="text-xs text-zinc-500">Key: {status.api_key_masked}</p>
                    </div>
                  </div>
                  <span className={`text-xs font-mono px-2 py-1 rounded ${status.status === 'valid' ? 'bg-[#00FF94]/10 text-[#00FF94]' : 'bg-red-400/10 text-red-400'}`} data-testid="exchange-status-badge">
                    {status.status}
                  </span>
                </div>
                <p className="text-[11px] text-zinc-600 mb-4">Connected {new Date(status.connected_at).toLocaleDateString()}</p>
                <button onClick={handleDisconnect} className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition-colors" data-testid="exchange-disconnect-btn">
                  <Unplug className="w-3.5 h-3.5" /> Disconnect
                </button>
              </CardContent>
            </Card>
          )}

          {/* Connection form */}
          <Card className="bg-[#0A0A0A] border-zinc-800" data-testid="exchange-connect-form">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{status?.connected ? "Reconnect Exchange" : "Enter API Credentials"}</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Exchange selector */}
                <div>
                  <label className="block text-xs text-zinc-500 uppercase tracking-wider mb-2">Exchange</label>
                  <div className="flex gap-3">
                    {EXCHANGES.map(ex => (
                      <button key={ex.id} type="button" onClick={() => setExchange(ex.id)}
                        className={`flex-1 py-3 px-4 border text-sm font-medium transition-colors ${exchange === ex.id ? 'border-[#7B61FF] bg-[#7B61FF]/10 text-white' : 'border-zinc-800 text-zinc-500 hover:border-zinc-700'}`}
                        data-testid={`exchange-option-${ex.id}`}>
                        {ex.label} <span className="text-[10px] ml-1 text-zinc-600">{ex.tag}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* API Key */}
                <div>
                  <label className="block text-xs text-zinc-500 uppercase tracking-wider mb-2">API Key</label>
                  <Input value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="Enter your API key"
                    className="bg-[#050505] border-zinc-800 h-11" data-testid="exchange-api-key-input" />
                </div>

                {/* Secret Key */}
                <div>
                  <label className="block text-xs text-zinc-500 uppercase tracking-wider mb-2">Secret Key</label>
                  <Input type="password" value={secretKey} onChange={e => setSecretKey(e.target.value)} placeholder="Enter your secret key"
                    className="bg-[#050505] border-zinc-800 h-11" data-testid="exchange-secret-key-input" />
                </div>

                {/* Security note */}
                <div className="flex items-start gap-2 p-3 bg-[#7B61FF]/5 border border-[#7B61FF]/10">
                  <Shield className="w-4 h-4 text-[#7B61FF] mt-0.5 shrink-0" />
                  <p className="text-[11px] text-zinc-400">Your keys are encrypted at rest and never logged. Secret keys are never sent back to the browser after submission.</p>
                </div>

                {/* Result */}
                {result && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className={`p-4 border ${result.ok ? 'border-[#00FF94]/20 bg-[#00FF94]/5' : 'border-red-400/20 bg-red-400/5'}`}
                    data-testid="exchange-result">
                    {result.ok ? (
                      <div>
                        <p className="text-sm text-[#00FF94] font-medium flex items-center gap-2" data-testid="exchange-success-msg">
                          <Check className="w-4 h-4" /> Exchange connected successfully
                        </p>
                        {result.balances?.length > 0 && (
                          <div className="mt-3 space-y-1">
                            <p className="text-[11px] text-zinc-500 uppercase tracking-wider">Balances</p>
                            {result.balances.slice(0, 8).map(b => (
                              <div key={b.asset} className="flex justify-between text-xs">
                                <span className="text-zinc-400">{b.asset}</span>
                                <span className="text-white font-mono">{b.free.toFixed(b.free < 1 ? 8 : 2)}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-red-400 flex items-center gap-2" data-testid="exchange-error-msg">
                        <AlertTriangle className="w-4 h-4" /> {result.msg}
                      </p>
                    )}
                  </motion.div>
                )}

                <Button type="submit" disabled={!apiKey || !secretKey || sending}
                  className="w-full h-12 bg-[#7B61FF] hover:bg-[#6A50E5] disabled:bg-zinc-800 disabled:text-zinc-500"
                  data-testid="exchange-connect-btn">
                  {sending ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Validating...</> : "Connect Exchange"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
