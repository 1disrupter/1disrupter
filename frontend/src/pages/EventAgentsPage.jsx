import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  Activity, ArrowDown, Check, Cpu, Minus, Pause,
  PieChart, Play, Plus, Target, Wallet, Zap
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { ScrollArea } from "../components/ui/scroll-area";
import { API } from "../lib/constants";

const EventAgentsDashboard = () => {
  const [eventAgents, setEventAgents] = useState([]);
  const [recentEvents, setRecentEvents] = useState([]);
  const [investorBalances, setInvestorBalances] = useState({ data: [], summary: {} });
  const [strategyAllocation, setStrategyAllocation] = useState({ data: [], summary: {} });
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, eventsRes, balancesRes, allocRes] = await Promise.all([
        axios.get(`${API}/agents/event-agents`),
        axios.get(`${API}/events/recent`),
        axios.get(`${API}/dashboards/investor-balances`),
        axios.get(`${API}/dashboards/strategy-allocation`)
      ]);
      setEventAgents(agentsRes.data.agents || []);
      setRecentEvents(eventsRes.data.events || []);
      setInvestorBalances(balancesRes.data);
      setStrategyAllocation(allocRes.data);
    } catch (error) {
      console.error("Failed to fetch event data:", error);
    }
  };

  const toggleAgent = async (agentId) => {
    try {
      await axios.post(`${API}/agents/event-agents/toggle/${agentId}`);
      fetchData();
      toast.success("Agent status updated");
    } catch (error) {
      toast.error("Failed to toggle agent");
    }
  };

  const simulateEvent = async (eventName) => {
    setSimulating(true);
    try {
      const res = await axios.post(`${API}/events/simulate?event_name=${eventName}&amount_eth=${(Math.random() * 5 + 0.5).toFixed(2)}`);
      toast.success(`Event simulated: ${eventName}`);
      fetchData();
    } catch (error) {
      toast.error("Failed to simulate event");
    }
    setSimulating(false);
  };

  const getAgentTypeColor = (type) => {
    switch(type) {
      case 'watcher': return 'text-blue-400 bg-blue-400/20';
      case 'execution': return 'text-[#00FF94] bg-[#00FF94]/20';
      case 'analytics': return 'text-[#FFB800] bg-[#FFB800]/20';
      default: return 'text-zinc-400 bg-zinc-700';
    }
  };

  const getEventColor = (eventName) => {
    if (eventName.includes('Deposited')) return 'text-[#00FF94]';
    if (eventName.includes('Withdrawn')) return 'text-red-400';
    if (eventName.includes('Allocated')) return 'text-[#7B61FF]';
    return 'text-zinc-400';
  };

  return (
    <div className="space-y-6">
      {/* Event Agents Status */}
      <Card className="glass-card border-[#00FF94]/30" data-testid="event-agents-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-[#00FF94]" />
            Event-Driven Agents
          </CardTitle>
          <CardDescription>Smart contract event monitors and automated actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            {eventAgents.map((agent) => (
              <div key={agent.id} className="p-4 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`event-agent-${agent.id}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${agent.is_active ? 'bg-[#00FF94]' : 'bg-zinc-500'}`} />
                    <span className="font-medium text-sm">{agent.name}</span>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => toggleAgent(agent.id)} className="h-6 w-6 p-0">
                    {agent.is_active ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                  </Button>
                </div>
                <Badge className={getAgentTypeColor(agent.type)}>{agent.type}</Badge>
                <p className="text-xs text-zinc-500 mt-2">{agent.description || `Monitors: ${agent.events_to_monitor?.join(', ')}`}</p>
                <div className="flex items-center justify-between mt-3 text-xs">
                  <span className="text-zinc-500">Events processed</span>
                  <span className="font-mono text-[#00FF94]">{agent.events_processed_count || 0}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Event Simulation */}
          <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#FFB800]" />
              Simulate Contract Events
            </h4>
            <div className="flex flex-wrap gap-2">
              <Button 
                onClick={() => simulateEvent('InvestorDeposited')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-[#00FF94]/50 text-[#00FF94]"
              >
                <Plus className="w-3 h-3 mr-1" />Deposit
              </Button>
              <Button 
                onClick={() => simulateEvent('InvestorWithdrawn')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-red-400/50 text-red-400"
              >
                <Minus className="w-3 h-3 mr-1" />Withdrawal
              </Button>
              <Button 
                onClick={() => simulateEvent('StrategyAllocated')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-[#7B61FF]/50 text-[#7B61FF]"
              >
                <Target className="w-3 h-3 mr-1" />Allocate
              </Button>
              <Button 
                onClick={() => simulateEvent('StrategyDeallocated')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-zinc-500/50 text-zinc-400"
              >
                <ArrowDown className="w-3 h-3 mr-1" />Deallocate
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dashboards Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Investor Balances Dashboard */}
        <Card className="glass-card" data-testid="investor-balances-dashboard">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wallet className="w-5 h-5 text-[#00FF94]" />
              Investor Balances
            </CardTitle>
            <div className="flex gap-4 mt-2">
              <div className="text-center">
                <p className="text-2xl font-bold font-mono text-[#00FF94]">{investorBalances.summary?.total_deposited_eth?.toFixed(2) || '0.00'}</p>
                <p className="text-xs text-zinc-500">Total ETH</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold font-mono">{investorBalances.summary?.active_investors || 0}</p>
                <p className="text-xs text-zinc-500">Active Investors</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px]">
              <div className="space-y-2">
                {investorBalances.data?.map((investor, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${investor.status === 'active' ? 'bg-[#00FF94]' : 'bg-zinc-500'}`} />
                      <span className="font-mono text-xs">{investor.address?.slice(0, 10)}...{investor.address?.slice(-6)}</span>
                    </div>
                    <span className="font-mono text-sm text-[#00FF94]">{investor.balance?.toFixed(4)} ETH</span>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Strategy Allocation Dashboard */}
        <Card className="glass-card" data-testid="strategy-allocation-dashboard">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-[#7B61FF]" />
              Strategy Allocation
            </CardTitle>
            <div className="flex gap-4 mt-2">
              <div className="text-center">
                <p className="text-2xl font-bold font-mono text-[#7B61FF]">{strategyAllocation.summary?.total_allocated_eth?.toFixed(2) || '0.00'}</p>
                <p className="text-xs text-zinc-500">Total Allocated</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold font-mono">{strategyAllocation.summary?.active_strategies || 0}</p>
                <p className="text-xs text-zinc-500">Active Strategies</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px]">
              <div className="space-y-2">
                {strategyAllocation.data?.map((strategy, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${strategy.active ? 'bg-[#7B61FF]' : 'bg-zinc-500'}`} />
                      <span className="text-sm">{strategy.name}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-mono text-sm text-[#7B61FF]">{strategy.allocated_capital?.toFixed(2)} ETH</span>
                      <p className="text-xs text-zinc-500">{strategy.transactions} txns</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Recent Events Log */}
      <Card className="glass-card" data-testid="recent-events-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-[#FFB800]" />
            Recent Contract Events
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[200px]">
            <div className="space-y-2">
              {recentEvents.slice(0, 10).map((event, i) => (
                <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                  <div className="flex items-center gap-3">
                    <Badge className={`${getEventColor(event.event_name)} bg-opacity-20`}>{event.event_name}</Badge>
                    <span className="font-mono text-xs text-zinc-500">{event.tx_hash?.slice(0, 14)}...</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-400">{new Date(event.timestamp).toLocaleTimeString()}</span>
                    {event.processed && <Check className="w-3 h-3 text-[#00FF94]" />}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

// Event Agents Page Wrapper
const EventAgentsPage = () => {
  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-4xl font-bold mb-2 font-['Outfit']">Event-Driven Agents</h1>
          <p className="text-zinc-400">Smart contract event monitors with automated actions and dashboards</p>
        </motion.div>
        <EventAgentsDashboard />
      </div>
    </div>
  );
};

// Research Engine Page

export default EventAgentsPage;
