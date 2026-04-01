import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { Activity, CheckCircle, XCircle, Clock, Filter, ChevronDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useAuth } from "../contexts/AuthContext";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATUS_COLOR = { success: "bg-[#00FF94]/15 text-[#00FF94]", failed: "bg-red-400/15 text-red-400", pending: "bg-amber-400/15 text-amber-400", skipped: "bg-zinc-800 text-zinc-400" };
const STATUS_ICON = { success: CheckCircle, failed: XCircle, pending: Clock, skipped: Clock };

const ExecutionMonitorPage = () => {
  const { user, tokens } = useAuth();
  const token = tokens?.access_token;
  const navigate = useNavigate();

  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");

  const headers = { Authorization: `Bearer ${token}` };

  const fetchLogs = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: "100" });
      if (statusFilter) params.set("status", statusFilter);

      // Try admin endpoint first, fall back to user endpoint
      let res;
      try {
        res = await axios.get(`${API}/execution/logs/admin?${params}`, { headers });
      } catch {
        res = await axios.get(`${API}/execution/logs?${params}`, { headers });
      }
      setLogs(res.data.logs || []);
      setTotal(res.data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [token, statusFilter]);

  useEffect(() => {
    if (!token) { navigate("/login"); return; }
    fetchLogs();
  }, [token, fetchLogs, navigate]);

  const stats = {
    total: logs.length,
    success: logs.filter(l => l.status === "success").length,
    failed: logs.filter(l => l.status === "failed").length,
    paper: logs.filter(l => l.execution_mode === "paper").length,
    testnet: logs.filter(l => l.execution_mode === "testnet").length,
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="execution-monitor-page">
      <div className="max-w-5xl mx-auto space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold font-['Outfit'] text-white" data-testid="monitor-title">Execution Monitor</h1>
          <p className="text-sm text-zinc-500 mt-1">Real-time execution log monitoring</p>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {[
            { label: "Total", value: stats.total, color: "text-white" },
            { label: "Success", value: stats.success, color: "text-[#00FF94]" },
            { label: "Failed", value: stats.failed, color: "text-red-400" },
            { label: "Paper", value: stats.paper, color: "text-zinc-400" },
            { label: "Testnet", value: stats.testnet, color: "text-[#7B61FF]" },
          ].map(s => (
            <Card key={s.label} className="bg-[#0A0A0A] border-zinc-800/50">
              <CardContent className="p-3 text-center">
                <p className="text-[10px] text-zinc-600 uppercase">{s.label}</p>
                <p className={`text-lg font-bold font-mono ${s.color}`}>{s.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 pointer-events-none" />
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="h-9 pl-9 pr-8 bg-[#0A0A0A] border border-zinc-800 rounded-md text-sm text-zinc-300 appearance-none cursor-pointer"
              data-testid="status-filter"
            >
              <option value="">All Status</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="skipped">Skipped</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 pointer-events-none" />
          </div>
          <span className="text-xs text-zinc-600 font-mono">{total} records</span>
        </div>

        {/* Log table */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="logs-table-card">
          <CardContent className="p-0">
            {loading ? (
              <div className="p-6 space-y-3">
                {[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-zinc-900 rounded animate-pulse" />)}
              </div>
            ) : logs.length === 0 ? (
              <p className="text-zinc-600 text-xs py-12 text-center">No execution logs found</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs" data-testid="logs-table">
                  <thead>
                    <tr className="border-b border-zinc-800/50">
                      <th className="text-left py-3 px-4 text-zinc-600 font-medium">Time</th>
                      <th className="text-left py-3 px-4 text-zinc-600 font-medium">Order</th>
                      <th className="text-left py-3 px-4 text-zinc-600 font-medium">Strategy</th>
                      <th className="text-left py-3 px-4 text-zinc-600 font-medium">Mode</th>
                      <th className="text-left py-3 px-4 text-zinc-600 font-medium">Status</th>
                      <th className="text-left py-3 px-4 text-zinc-600 font-medium">Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((l, i) => {
                      const Icon = STATUS_ICON[l.status] || Clock;
                      return (
                        <tr key={l.id} className="border-b border-zinc-800/20 hover:bg-white/[0.02]" data-testid={`log-row-${i}`}>
                          <td className="py-2.5 px-4 text-zinc-500 font-mono whitespace-nowrap">
                            {l.created_at ? new Date(l.created_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "—"}
                          </td>
                          <td className="py-2.5 px-4 text-zinc-300 font-mono">
                            {l.request_payload?.side} {l.request_payload?.quantity} {l.request_payload?.symbol}
                          </td>
                          <td className="py-2.5 px-4 text-zinc-500 font-mono">{l.strategy_id === "manual_test" ? "manual" : l.strategy_id?.substring(0, 8)}</td>
                          <td className="py-2.5 px-4">
                            <Badge className="bg-zinc-800 text-zinc-400 text-[10px]">{l.execution_mode}</Badge>
                          </td>
                          <td className="py-2.5 px-4">
                            <div className="flex items-center gap-1">
                              <Icon className={`w-3 h-3 ${l.status === "success" ? "text-[#00FF94]" : l.status === "failed" ? "text-red-400" : "text-zinc-500"}`} />
                              <Badge className={`text-[10px] ${STATUS_COLOR[l.status] || STATUS_COLOR.skipped}`}>{l.status}</Badge>
                            </div>
                          </td>
                          <td className="py-2.5 px-4 text-red-400/60 text-[10px] max-w-[200px] truncate">{l.error_message || "—"}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ExecutionMonitorPage;
