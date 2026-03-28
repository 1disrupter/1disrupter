import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Bot, Cpu } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter
} from "../components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import { useWallet } from "../contexts/WalletContext";
import { API } from "../lib/constants";

const MarketplacePage = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const { wallet } = useWallet();
  const [newAgent, setNewAgent] = useState({ name: '', description: '', strategy: '', min_investment: 100 });

  useEffect(() => {
    axios.get(`${API}/marketplace/agents`).then(res => setAgents(res.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleSubmitAgent = async () => {
    if (!wallet) { toast.error("Connect wallet first"); return; }
    try {
      await axios.post(`${API}/marketplace/agents`, { ...newAgent, developer_address: wallet });
      toast.success("Agent submitted for review!");
      setShowSubmitDialog(false);
    } catch (error) { toast.error("Failed to submit agent"); }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div><h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="marketplace-title">AI Agent Marketplace</h1><p className="text-zinc-400 mt-1">Discover and deploy community-built strategies</p></div>
          <Button onClick={() => setShowSubmitDialog(true)} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="submit-agent-btn"><Cpu className="w-4 h-4 mr-2" />Submit Your Agent</Button>
        </div>

        <Card className="glass-card mb-8 border-[#7B61FF]/30" data-testid="revenue-info">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="flex-1"><h3 className="text-lg font-semibold mb-2">Developer Revenue Model</h3><p className="text-zinc-400 text-sm">Deploy your AI trading agent and earn 90% of subscriber fees.</p></div>
              <div className="flex gap-8">
                <div className="text-center"><p className="text-3xl font-bold text-[#00FF94]">90%</p><p className="text-xs text-zinc-500">Developer Share</p></div>
                <div className="text-center"><p className="text-3xl font-bold text-zinc-400">10%</p><p className="text-xs text-zinc-500">Platform Fee</p></div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? Array(3).fill(0).map((_, i) => (<Card key={i} className="glass-card animate-pulse"><CardContent className="p-6 h-[250px]" /></Card>)) : agents.map((agent) => (
            <Card key={agent.id} className="glass-card card-hover" data-testid={`marketplace-agent-${agent.id}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center"><Bot className="w-6 h-6 text-white" /></div>
                  <Badge className="bg-[#00FF94]/20 text-[#00FF94]">{agent.total_subscribers} subscribers</Badge>
                </div>
                <h3 className="text-lg font-semibold mb-2">{agent.name}</h3>
                <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{agent.description}</p>
                <div className="flex items-center justify-between text-sm mb-4"><span className="text-zinc-500">30D Return</span><span className={`font-mono ${agent.performance_30d >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{agent.performance_30d >= 0 ? '+' : ''}{agent.performance_30d}%</span></div>
                <Button className="w-full mt-4 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] hover:bg-[#7B61FF]/30" data-testid={`subscribe-${agent.id}`}>Subscribe</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <DialogContent className="bg-[#121212] border-zinc-800" data-testid="submit-agent-dialog">
          <DialogHeader><DialogTitle>Submit Your AI Agent</DialogTitle></DialogHeader>
          <div className="space-y-4 py-4">
            <Input placeholder="Agent Name" value={newAgent.name} onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })} className="bg-[#050505] border-zinc-800" data-testid="agent-name-input" />
            <Input placeholder="Description" value={newAgent.description} onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })} className="bg-[#050505] border-zinc-800" data-testid="agent-description-input" />
            <Select value={newAgent.strategy} onValueChange={(v) => setNewAgent({ ...newAgent, strategy: v })}>
              <SelectTrigger className="bg-[#050505] border-zinc-800" data-testid="agent-strategy-select"><SelectValue placeholder="Select strategy" /></SelectTrigger>
              <SelectContent className="bg-[#121212] border-zinc-800">
                <SelectItem value="Momentum Trading">Momentum Trading</SelectItem>
                <SelectItem value="Arbitrage">Arbitrage</SelectItem>
                <SelectItem value="Yield Farming">Yield Farming</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setShowSubmitDialog(false)}>Cancel</Button><Button onClick={handleSubmitAgent} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="submit-agent-confirm-btn">Submit</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MarketplacePage;
