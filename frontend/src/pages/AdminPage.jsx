import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  Activity, Check, Clock, Cpu, DollarSign, Gauge,
  LogOut, RefreshCw, ScrollText, Settings, Shield, Users, BarChart3,
  Copy, ExternalLink, FileCode, Rocket, Target, Terminal, Wallet
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { ScrollArea } from "../components/ui/scroll-area";
import { Switch } from "../components/ui/switch";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle
} from "../components/ui/dialog";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from "../components/ui/dropdown-menu";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import { BrandLockup } from "../components/BrandComponents";
import { API } from "../lib/constants";

const SmartContractPanel = () => {
  const [contractInfo, setContractInfo] = useState(null);
  const [deploymentGuide, setDeploymentGuide] = useState(null);
  const [contractAddress, setContractAddress] = useState('');
  const [deployerAddress, setDeployerAddress] = useState('');
  const [txHash, setTxHash] = useState('');
  const [registering, setRegistering] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [sourceCode, setSourceCode] = useState('');

  useEffect(() => {
    axios.get(`${API}/contract/info`).then(res => setContractInfo(res.data)).catch(console.error);
    axios.get(`${API}/contract/deployment-guide`).then(res => setDeploymentGuide(res.data)).catch(console.error);
  }, []);

  const fetchSourceCode = async () => {
    try {
      const res = await axios.get(`${API}/contract/source`);
      setSourceCode(res.data.source);
      setShowCode(true);
    } catch (error) {
      toast.error("Failed to fetch source code");
    }
  };

  const registerContract = async () => {
    if (!contractAddress || !deployerAddress || !txHash) {
      toast.error("Please fill all fields");
      return;
    }
    setRegistering(true);
    try {
      const res = await axios.post(`${API}/contract/register?contract_address=${contractAddress}&deployer_address=${deployerAddress}&tx_hash=${txHash}`);
      toast.success(res.data.message);
      setContractInfo({ ...contractInfo, deployed: true, contract_address: contractAddress });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Registration failed");
    }
    setRegistering(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  return (
    <Card className="glass-card mt-8 border-[#7B61FF]/30" data-testid="smart-contract-panel">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileCode className="w-5 h-5 text-[#7B61FF]" />
          Smart Contract (Sepolia Testnet)
        </CardTitle>
        <CardDescription>Deploy and manage the AlphaAI Manager contract on Ethereum</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Contract Status */}
        <div className="flex items-center gap-4 mb-6 p-4 rounded-lg bg-[#050505] border border-zinc-800">
          <div className={`w-3 h-3 rounded-full ${contractInfo?.deployed ? 'bg-[#00FF94]' : 'bg-[#FFB800]'}`} />
          <div className="flex-1">
            <p className="font-medium">{contractInfo?.deployed ? 'Contract Deployed' : 'Contract Not Deployed'}</p>
            <p className="text-sm text-zinc-400">
              {contractInfo?.deployed 
                ? <a href={`https://sepolia.etherscan.io/address/${contractInfo.contract_address}`} target="_blank" rel="noopener noreferrer" className="text-[#7B61FF] hover:underline">{contractInfo.contract_address}</a>
                : 'Deploy to Sepolia testnet to enable on-chain transactions'}
            </p>
          </div>
          <Badge className={contractInfo?.deployed ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-[#FFB800]/20 text-[#FFB800]'}>
            {contractInfo?.network?.toUpperCase() || 'SEPOLIA'}
          </Badge>
        </div>

        {/* Deployment Steps */}
        {!contractInfo?.deployed && deploymentGuide && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Rocket className="w-5 h-5 text-[#FFB800]" />
              Deployment Steps
            </h3>
            <div className="space-y-3">
              {deploymentGuide.steps?.map((step, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[#050505] border border-zinc-800">
                  <div className="w-6 h-6 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {step.step}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{step.title}</p>
                    <p className="text-xs text-zinc-400">{step.description}</p>
                    {step.links && (
                      <div className="mt-1 flex gap-2">
                        {step.links.map((link, j) => (
                          <a key={j} href={link} target="_blank" rel="noopener noreferrer" className="text-xs text-[#7B61FF] hover:underline flex items-center gap-1">
                            <ExternalLink className="w-3 h-3" />{link.split('/')[2]}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Contract Source */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Terminal className="w-5 h-5 text-[#00FF94]" />
              Contract Source Code
            </h3>
            <div className="flex gap-2">
              <Button onClick={fetchSourceCode} variant="outline" size="sm" className="rounded-full border-zinc-700">
                {showCode ? 'Refresh' : 'View Code'}
              </Button>
              {showCode && (
                <Button onClick={() => copyToClipboard(sourceCode)} variant="outline" size="sm" className="rounded-full border-zinc-700">
                  <Copy className="w-4 h-4 mr-1" />Copy
                </Button>
              )}
            </div>
          </div>
          {showCode && (
            <div className="bg-[#050505] border border-zinc-800 rounded-lg p-4 max-h-[300px] overflow-auto">
              <pre className="text-xs text-zinc-300 font-mono whitespace-pre-wrap">{sourceCode}</pre>
            </div>
          )}
        </div>

        {/* Register Deployed Contract */}
        {!contractInfo?.deployed && (
          <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Check className="w-5 h-5 text-[#00FF94]" />
              Register Deployed Contract
            </h3>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="text-sm text-zinc-400 block mb-1">Contract Address</label>
                <Input 
                  placeholder="0x..." 
                  value={contractAddress} 
                  onChange={e => setContractAddress(e.target.value)}
                  className="bg-[#121212] border-zinc-700 font-mono text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 block mb-1">Deployer Address</label>
                <Input 
                  placeholder="0x..." 
                  value={deployerAddress}
                  onChange={e => setDeployerAddress(e.target.value)}
                  className="bg-[#121212] border-zinc-700 font-mono text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 block mb-1">Transaction Hash</label>
                <Input 
                  placeholder="0x..." 
                  value={txHash}
                  onChange={e => setTxHash(e.target.value)}
                  className="bg-[#121212] border-zinc-700 font-mono text-sm"
                />
              </div>
            </div>
            <Button 
              onClick={registerContract} 
              disabled={registering}
              className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
            >
              {registering ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-2" />}
              Register Contract
            </Button>
          </div>
        )}

        {/* Contract Functions (if deployed) */}
        {contractInfo?.deployed && (
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
              <h4 className="font-medium mb-2 flex items-center gap-2">
                <Wallet className="w-4 h-4 text-[#00FF94]" />Investor Functions
              </h4>
              <p className="text-xs text-zinc-400 mb-2">deposit(), withdraw(), getInvestorBalance()</p>
              <Button size="sm" variant="outline" className="rounded-full border-[#00FF94]/50 text-[#00FF94]">
                <ExternalLink className="w-3 h-3 mr-1" />View on Etherscan
              </Button>
            </div>
            <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
              <h4 className="font-medium mb-2 flex items-center gap-2">
                <Target className="w-4 h-4 text-[#7B61FF]" />Strategy Functions
              </h4>
              <p className="text-xs text-zinc-400 mb-2">addStrategy(), allocateToStrategy(), getStrategy()</p>
              <Button size="sm" variant="outline" className="rounded-full border-[#7B61FF]/50 text-[#7B61FF]">
                <ExternalLink className="w-3 h-3 mr-1" />View on Etherscan
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Event-Driven Agents Dashboard Component

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [adminKey, setAdminKey] = useState(localStorage.getItem('adminKey') || '');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Overview state
  const [dashboardData, setDashboardData] = useState(null);
  const [systemStats, setSystemStats] = useState(null);
  
  // Users state
  const [users, setUsers] = useState([]);
  const [userSearch, setUserSearch] = useState('');
  const [userPlanFilter, setUserPlanFilter] = useState('all');
  const [userStatusFilter, setUserStatusFilter] = useState('all');
  const [usersPage, setUsersPage] = useState(1);
  const [usersTotal, setUsersTotal] = useState(0);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDetailOpen, setUserDetailOpen] = useState(false);
  
  // Subscriptions state
  const [subscriptions, setSubscriptions] = useState([]);
  const [subsPage, setSubsPage] = useState(1);
  const [subsTotal, setSubsTotal] = useState(0);
  
  // Logs state
  const [logs, setLogs] = useState([]);
  const [logCategory, setLogCategory] = useState('all');
  const [logSeverity, setLogSeverity] = useState('all');
  const [logsPage, setLogsPage] = useState(1);
  const [logsTotal, setLogsTotal] = useState(0);
  const [auditLogs, setAuditLogs] = useState([]);
  
  // Features state
  const [features, setFeatures] = useState([]);
  const [featureCategories, setFeatureCategories] = useState({});
  
  // Legacy fund stats for overview
  const [fundStats, setFundStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [agents, setAgents] = useState([]);
  const [riskConfig, setRiskConfig] = useState(null);

  const ADMIN_API = `${API}/admin`;

  // Admin authentication
  const authenticateAdmin = async () => {
    if (!adminKey) {
      toast.error('Please enter admin key');
      return;
    }
    try {
      const res = await axios.get(`${ADMIN_API}/dashboard?admin_key=${adminKey}`);
      if (res.data) {
        setIsAuthenticated(true);
        localStorage.setItem('adminKey', adminKey);
        toast.success('Admin access granted');
        loadAllData();
      }
    } catch (error) {
      toast.error('Invalid admin key');
      setIsAuthenticated(false);
    }
  };

  // Load all data
  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadDashboard(),
        loadSystemStats(),
        loadUsers(),
        loadSubscriptions(),
        loadLogs(),
        loadFeatures(),
        loadLegacyData()
      ]);
    } catch (error) {
      console.error('Error loading admin data:', error);
    }
    setLoading(false);
  };

  const loadDashboard = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/dashboard?admin_key=${adminKey}`);
      setDashboardData(res.data);
    } catch (error) { console.error('Dashboard load error:', error); }
  };

  const loadSystemStats = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/system/stats?admin_key=${adminKey}`);
      setSystemStats(res.data);
    } catch (error) { console.error('System stats load error:', error); }
  };

  const loadUsers = async () => {
    try {
      const params = new URLSearchParams({ admin_key: adminKey, page: usersPage, limit: 20 });
      if (userSearch) params.append('search', userSearch);
      if (userPlanFilter !== 'all') params.append('plan', userPlanFilter);
      if (userStatusFilter !== 'all') params.append('status', userStatusFilter);
      const res = await axios.get(`${ADMIN_API}/users?${params}`);
      setUsers(res.data.users);
      setUsersTotal(res.data.total);
    } catch (error) { console.error('Users load error:', error); }
  };

  const loadSubscriptions = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/subscriptions?admin_key=${adminKey}&page=${subsPage}`);
      setSubscriptions(res.data.subscriptions);
      setSubsTotal(res.data.total);
    } catch (error) { console.error('Subscriptions load error:', error); }
  };

  const loadLogs = async () => {
    try {
      const params = new URLSearchParams({ admin_key: adminKey, page: logsPage, limit: 50 });
      if (logCategory !== 'all') params.append('category', logCategory);
      if (logSeverity !== 'all') params.append('severity', logSeverity);
      const res = await axios.get(`${ADMIN_API}/logs?${params}`);
      setLogs(res.data.logs);
      setLogsTotal(res.data.total);
      
      // Load audit logs
      const auditRes = await axios.get(`${ADMIN_API}/logs/audit?admin_key=${adminKey}&limit=20`);
      setAuditLogs(auditRes.data.logs);
    } catch (error) { console.error('Logs load error:', error); }
  };

  const loadFeatures = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/features?admin_key=${adminKey}`);
      setFeatures(res.data.features);
      setFeatureCategories(res.data.categories);
    } catch (error) { console.error('Features load error:', error); }
  };

  const loadLegacyData = async () => {
    try {
      const [statsRes, alertsRes, agentsRes, configRes] = await Promise.all([
        axios.get(`${API}/fund/stats`),
        axios.get(`${API}/risk/alerts`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/risk/config`)
      ]);
      setFundStats(statsRes.data);
      setAlerts(alertsRes.data);
      setAgents(agentsRes.data);
      setRiskConfig(configRes.data);
    } catch (error) { console.error('Legacy data load error:', error); }
  };

  // User actions
  const handleUserAction = async (userId, action, reason = '') => {
    try {
      await axios.post(`${ADMIN_API}/users/action?admin_key=${adminKey}`, {
        user_id: userId,
        action: action,
        reason: reason
      });
      toast.success(`Action '${action}' completed`);
      loadUsers();
      loadDashboard();
    } catch (error) {
      toast.error(`Action failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  const viewUserDetails = async (userId) => {
    try {
      const res = await axios.get(`${ADMIN_API}/users/${userId}?admin_key=${adminKey}`);
      setSelectedUser(res.data);
      setUserDetailOpen(true);
    } catch (error) {
      toast.error('Failed to load user details');
    }
  };

  // Subscription actions
  const syncSubscription = async (userId) => {
    try {
      await axios.post(`${ADMIN_API}/subscriptions/sync/${userId}?admin_key=${adminKey}`);
      toast.success('Subscription synced');
      loadSubscriptions();
    } catch (error) {
      toast.error('Sync failed');
    }
  };

  const overrideSubscription = async (userId, plan, reason) => {
    try {
      await axios.post(`${ADMIN_API}/subscriptions/override?admin_key=${adminKey}`, {
        user_id: userId,
        plan: plan,
        reason: reason
      });
      toast.success(`Subscription set to ${plan}`);
      loadSubscriptions();
      loadUsers();
    } catch (error) {
      toast.error('Override failed');
    }
  };

  // Feature toggle
  const toggleFeature = async (featureId, enabled) => {
    try {
      await axios.put(`${ADMIN_API}/features?admin_key=${adminKey}`, {
        feature_id: featureId,
        enabled: enabled
      });
      toast.success(`Feature ${enabled ? 'enabled' : 'disabled'}`);
      loadFeatures();
    } catch (error) {
      toast.error('Toggle failed');
    }
  };

  // System tools
  const runSystemTool = async (tool) => {
    try {
      const res = await axios.post(`${ADMIN_API}/system/tools?admin_key=${adminKey}`, { tool });
      if (res.data.success) {
        toast.success(res.data.message);
      } else {
        toast.error(res.data.message);
      }
      loadSystemStats();
    } catch (error) {
      toast.error('Tool execution failed');
    }
  };

  // Effects
  useEffect(() => {
    if (adminKey && localStorage.getItem('adminKey')) {
      authenticateAdmin();
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadUsers();
    }
  }, [userSearch, userPlanFilter, userStatusFilter, usersPage, isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      loadLogs();
    }
  }, [logCategory, logSeverity, logsPage, isAuthenticated]);

  // Auth screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <Card className="glass-card w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-6 h-6 text-[#7B61FF]" />
              Admin Authentication
            </CardTitle>
            <CardDescription>Enter your admin key to access the dashboard</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              type="password"
              placeholder="Admin Key"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && authenticateAdmin()}
              className="bg-[#050505] border-zinc-800"
              data-testid="admin-key-input"
            />
            <Button onClick={authenticateAdmin} className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/80" data-testid="admin-login-btn">
              Access Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        {/* Header with Brand Identity */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-6">
            <BrandLockup size="large" showSubtitle={true} />
            <div className="h-10 w-px bg-zinc-800" />
            <div>
              <h1 className="text-2xl font-bold font-['Outfit']" data-testid="admin-title">
                System Admin
              </h1>
              <p className="text-zinc-500 text-sm">Administrative Console</p>
            </div>
          </div>
          <Button variant="outline" onClick={() => { setIsAuthenticated(false); localStorage.removeItem('adminKey'); }} className="border-zinc-700">
            <LogOut className="w-4 h-4 mr-2" /> Logout
          </Button>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-[#121212] border border-zinc-800 p-1 flex-wrap h-auto">
            <TabsTrigger value="overview" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-overview">Overview</TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-users">Users</TabsTrigger>
            <TabsTrigger value="subscriptions" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-subscriptions">Subscriptions</TabsTrigger>
            <TabsTrigger value="logs" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-logs">Logs</TabsTrigger>
            <TabsTrigger value="features" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-features">Features</TabsTrigger>
            <TabsTrigger value="tools" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-tools">System Tools</TabsTrigger>
            <TabsTrigger value="security" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-security">Security</TabsTrigger>
          </TabsList>

          {/* OVERVIEW TAB */}
          <TabsContent value="overview" className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="glass-card" data-testid="stat-total-users">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Total Users</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#00FF94]">{systemStats?.users?.total || 0}</p>
                  <p className="text-xs text-zinc-500 mt-1">+{systemStats?.users?.new_24h || 0} today</p>
                </CardContent>
              </Card>
              <Card className="glass-card" data-testid="stat-pro-users">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Pro Users</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#7B61FF]">{systemStats?.users?.pro || 0}</p>
                  <p className="text-xs text-zinc-500 mt-1">{systemStats?.users?.elite || 0} Elite</p>
                </CardContent>
              </Card>
              <Card className="glass-card" data-testid="stat-active-subs">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Active Subscriptions</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">{systemStats?.subscriptions?.active || 0}</p>
                </CardContent>
              </Card>
              <Card className="glass-card" data-testid="stat-signals">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Signals (24h)</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">{systemStats?.signals?.last_24h || 0}</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Users className="w-5 h-5 text-[#7B61FF]" />
                    Recent Signups
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboardData?.recent_signups?.map((user, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#050505]">
                        <span className="text-sm truncate">{user.email}</span>
                        <div className="flex items-center gap-2">
                          {user.is_pro && <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-xs">PRO</Badge>}
                          <span className="text-xs text-zinc-500">{new Date(user.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <DollarSign className="w-5 h-5 text-[#00FF94]" />
                    Recent Payments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboardData?.recent_payments?.map((payment, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#050505]">
                        <span className="text-sm truncate">{payment.user_email || payment.session_id?.slice(0, 20)}</span>
                        <div className="flex items-center gap-2">
                          <Badge className="bg-[#00FF94]/20 text-[#00FF94] text-xs">${payment.amount}</Badge>
                          <span className="text-xs text-zinc-500">{payment.package_id}</span>
                        </div>
                      </div>
                    ))}
                    {(!dashboardData?.recent_payments || dashboardData.recent_payments.length === 0) && (
                      <p className="text-zinc-500 text-center py-4">No recent payments</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Legacy sections */}
            {riskConfig && (
              <Card className="glass-card">
                <CardHeader><CardTitle className="flex items-center gap-2"><Gauge className="w-5 h-5 text-[#FF6B6B]" />Risk Configuration</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-4 gap-4">
                    <div><label className="text-sm text-zinc-400 block mb-1">Max Drawdown %</label><p className="text-lg font-mono">{riskConfig.max_drawdown}%</p></div>
                    <div><label className="text-sm text-zinc-400 block mb-1">Max Position Size %</label><p className="text-lg font-mono">{riskConfig.max_position_size}%</p></div>
                    <div><label className="text-sm text-zinc-400 block mb-1">Max Daily Loss %</label><p className="text-lg font-mono">{riskConfig.max_daily_loss}%</p></div>
                    <div><label className="text-sm text-zinc-400 block mb-1">Stop Loss %</label><p className="text-lg font-mono">{riskConfig.stop_loss}%</p></div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* USERS TAB */}
          <TabsContent value="users" className="space-y-6">
            {/* Filters */}
            <Card className="glass-card">
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-4">
                  <Input
                    placeholder="Search users..."
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                    className="bg-[#050505] border-zinc-800 max-w-xs"
                    data-testid="user-search"
                  />
                  <Select value={userPlanFilter} onValueChange={setUserPlanFilter}>
                    <SelectTrigger className="w-32 bg-[#050505] border-zinc-800"><SelectValue placeholder="Plan" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Plans</SelectItem>
                      <SelectItem value="free">Free</SelectItem>
                      <SelectItem value="pro">Pro</SelectItem>
                      <SelectItem value="elite">Elite</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={userStatusFilter} onValueChange={setUserStatusFilter}>
                    <SelectTrigger className="w-32 bg-[#050505] border-zinc-800"><SelectValue placeholder="Status" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                      <SelectItem value="verified">Verified</SelectItem>
                      <SelectItem value="unverified">Unverified</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={loadUsers} className="border-zinc-700">
                    <RefreshCw className="w-4 h-4 mr-2" /> Refresh
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Users Table */}
            <Card className="glass-card">
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-zinc-800">
                        <th className="text-left p-4 text-zinc-500 text-sm">Email</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Name</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Plan</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Status</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Created</th>
                        <th className="text-right p-4 text-zinc-500 text-sm">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id} className="border-b border-zinc-800/50 hover:bg-[#050505]/50" data-testid={`user-row-${user.id}`}>
                          <td className="p-4 text-sm">{user.email}</td>
                          <td className="p-4 text-sm text-zinc-400">{user.name || '-'}</td>
                          <td className="p-4">
                            <Badge className={user.is_elite ? 'bg-[#FFB800]/20 text-[#FFB800]' : user.is_pro ? 'bg-[#7B61FF]/20 text-[#7B61FF]' : 'bg-zinc-700 text-zinc-400'}>
                              {user.is_elite ? 'Elite' : user.is_pro ? 'Pro' : 'Free'}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <Badge className={user.is_verified ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                              {user.is_verified ? 'Verified' : 'Unverified'}
                            </Badge>
                          </td>
                          <td className="p-4 text-sm text-zinc-400">{new Date(user.created_at).toLocaleDateString()}</td>
                          <td className="p-4 text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm"><Settings className="w-4 h-4" /></Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end" className="bg-[#121212] border-zinc-800">
                                <DropdownMenuItem onClick={() => viewUserDetails(user.id)}>View Details</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'set_free')}>Set Free</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'set_pro')}>Set Pro</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'set_elite')}>Set Elite</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, user.is_active === false ? 'activate' : 'deactivate')}>
                                  {user.is_active === false ? 'Activate' : 'Deactivate'}
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'delete')} className="text-red-400">Delete User</DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="p-4 border-t border-zinc-800 flex items-center justify-between">
                  <p className="text-sm text-zinc-500">Total: {usersTotal} users</p>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => setUsersPage(p => Math.max(1, p - 1))} disabled={usersPage === 1}>Prev</Button>
                    <Button variant="outline" size="sm" onClick={() => setUsersPage(p => p + 1)} disabled={users.length < 20}>Next</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* SUBSCRIPTIONS TAB */}
          <TabsContent value="subscriptions" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-[#00FF94]" />
                  Subscription Management
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-zinc-800">
                        <th className="text-left p-4 text-zinc-500 text-sm">User</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Plan</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Status</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Expires</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Override</th>
                        <th className="text-right p-4 text-zinc-500 text-sm">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {subscriptions.map((sub, i) => (
                        <tr key={i} className="border-b border-zinc-800/50">
                          <td className="p-4 text-sm">{sub.user_email}</td>
                          <td className="p-4">
                            <Badge className={sub.plan === 'elite' ? 'bg-[#FFB800]/20 text-[#FFB800]' : 'bg-[#7B61FF]/20 text-[#7B61FF]'}>
                              {sub.plan}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <Badge className={sub.status === 'active' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                              {sub.status}
                            </Badge>
                          </td>
                          <td className="p-4 text-sm text-zinc-400">
                            {sub.expires_at ? new Date(sub.expires_at).toLocaleDateString() : '-'}
                          </td>
                          <td className="p-4">
                            {sub.admin_override && <Badge className="bg-yellow-500/20 text-yellow-400">Manual</Badge>}
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex gap-2 justify-end">
                              <Button size="sm" variant="outline" onClick={() => syncSubscription(sub.user_id)} className="border-zinc-700">
                                Sync
                              </Button>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button size="sm" variant="outline" className="border-zinc-700">Override</Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="bg-[#121212] border-zinc-800">
                                  <DropdownMenuItem onClick={() => overrideSubscription(sub.user_id, 'free', 'Admin override')}>Set Free</DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => overrideSubscription(sub.user_id, 'pro', 'Admin override')}>Set Pro</DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => overrideSubscription(sub.user_id, 'elite', 'Admin override')}>Set Elite</DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* LOGS TAB */}
          <TabsContent value="logs" className="space-y-6">
            <div className="flex gap-4 mb-4">
              <Select value={logCategory} onValueChange={setLogCategory}>
                <SelectTrigger className="w-40 bg-[#050505] border-zinc-800"><SelectValue placeholder="Category" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="backend">Backend</SelectItem>
                  <SelectItem value="webhook">Webhook</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                  <SelectItem value="auth">Auth</SelectItem>
                  <SelectItem value="payment">Payment</SelectItem>
                </SelectContent>
              </Select>
              <Select value={logSeverity} onValueChange={setLogSeverity}>
                <SelectTrigger className="w-32 bg-[#050505] border-zinc-800"><SelectValue placeholder="Severity" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ScrollText className="w-5 h-5 text-[#7B61FF]" />
                  System Logs
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  {logs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No logs found</p>
                  ) : (
                    <div className="space-y-2 font-mono text-sm">
                      {logs.map((log, i) => (
                        <div key={i} className={`p-2 rounded ${log.severity === 'error' ? 'bg-red-500/10' : log.severity === 'warning' ? 'bg-yellow-500/10' : 'bg-[#050505]'}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-zinc-500">{new Date(log.timestamp).toLocaleString()}</span>
                            <Badge className={log.severity === 'error' ? 'bg-red-500/20 text-red-400' : log.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-zinc-700 text-zinc-400'}>
                              {log.severity || 'info'}
                            </Badge>
                            <Badge className="bg-zinc-800 text-zinc-400">{log.category}</Badge>
                          </div>
                          <p className="text-zinc-300">{log.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Audit Logs */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-[#FFB800]" />
                  Admin Audit Log
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {auditLogs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No audit logs</p>
                  ) : (
                    <div className="space-y-2">
                      {auditLogs.map((log, i) => (
                        <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium">{log.action}</span>
                            <span className="text-xs text-zinc-500">{new Date(log.timestamp).toLocaleString()}</span>
                          </div>
                          <p className="text-xs text-zinc-400">By: {log.admin_email}</p>
                          {log.target_id && <p className="text-xs text-zinc-500">Target: {log.target_type}/{log.target_id}</p>}
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* FEATURES TAB */}
          <TabsContent value="features" className="space-y-6">
            {Object.entries(featureCategories).map(([category, categoryFeatures]) => (
              <Card key={category} className="glass-card">
                <CardHeader>
                  <CardTitle className="capitalize">{category} Features</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {categoryFeatures.map((feature) => (
                      <div key={feature.feature_id} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800">
                        <div>
                          <p className="font-medium">{feature.name}</p>
                          <p className="text-sm text-zinc-500">{feature.description}</p>
                        </div>
                        <Switch
                          checked={feature.enabled}
                          onCheckedChange={(checked) => toggleFeature(feature.feature_id, checked)}
                          data-testid={`toggle-${feature.feature_id}`}
                        />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* SYSTEM TOOLS TAB */}
          <TabsContent value="tools" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-[#7B61FF]" />
                    Maintenance Tools
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button onClick={() => runSystemTool('clear_cache')} variant="outline" className="w-full justify-start border-zinc-700">
                    <RefreshCw className="w-4 h-4 mr-2" /> Clear Cache
                  </Button>
                  <Button onClick={() => runSystemTool('refresh_data')} variant="outline" className="w-full justify-start border-zinc-700">
                    <Activity className="w-4 h-4 mr-2" /> Refresh Data
                  </Button>
                  <Button onClick={() => runSystemTool('rebuild_indexes')} variant="outline" className="w-full justify-start border-zinc-700">
                    <BarChart3 className="w-4 h-4 mr-2" /> Rebuild Indexes
                  </Button>
                  <Button onClick={() => runSystemTool('cleanup_expired_tokens')} variant="outline" className="w-full justify-start border-zinc-700">
                    <Clock className="w-4 h-4 mr-2" /> Cleanup Expired Tokens
                  </Button>
                  <Button onClick={() => runSystemTool('cleanup_old_logs')} variant="outline" className="w-full justify-start border-zinc-700">
                    <ScrollText className="w-4 h-4 mr-2" /> Cleanup Old Logs
                  </Button>
                  <Button onClick={() => runSystemTool('verify_subscriptions')} variant="outline" className="w-full justify-start border-zinc-700">
                    <Check className="w-4 h-4 mr-2" /> Verify Subscriptions
                  </Button>
                </CardContent>
              </Card>

              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-[#00FF94]" />
                    System Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Database Collections</p>
                    <p className="font-mono">{systemStats?.system?.database_collections?.length || 0}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Last Signal Generation</p>
                    <p className="font-mono text-sm">{systemStats?.system?.last_signal_generation ? new Date(systemStats.system.last_signal_generation).toLocaleString() : 'N/A'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Total Signals</p>
                    <p className="font-mono">{systemStats?.signals?.total || 0}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Total Trades</p>
                    <p className="font-mono">{systemStats?.trades?.total || 0}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* SECURITY TAB */}
          <TabsContent value="security" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-[#FF6B6B]" />
                  Security Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-1">Admin Auth</p>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#00FF94]" />
                      <span className="text-[#00FF94]">Protected</span>
                    </div>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-1">Audit Logging</p>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#00FF94]" />
                      <span className="text-[#00FF94]">Active</span>
                    </div>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-1">Rate Limiting</p>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#00FF94]" />
                      <span className="text-[#00FF94]">Enabled</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                  <p className="font-medium mb-2">Admin Access Requirements</p>
                  <ul className="text-sm text-zinc-400 space-y-1">
                    <li>• All admin routes require admin_key parameter</li>
                    <li>• All admin actions are logged to audit trail</li>
                    <li>• User deletion requires confirmation</li>
                    <li>• Subscription overrides are tracked with reason</li>
                  </ul>
                </div>

                <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                  <p className="font-medium text-yellow-400 mb-2">Security Recommendation</p>
                  <p className="text-sm text-zinc-400">For production, implement proper JWT-based admin authentication with role-based access control (RBAC).</p>
                </div>
              </CardContent>
            </Card>

            {/* Recent Audit Activity */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Recent Admin Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {auditLogs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No recent admin activity</p>
                  ) : (
                    <div className="space-y-2">
                      {auditLogs.slice(0, 10).map((log, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#050505]">
                          <div>
                            <p className="text-sm font-medium">{log.action}</p>
                            <p className="text-xs text-zinc-500">{log.admin_email} • {log.target_type}</p>
                          </div>
                          <span className="text-xs text-zinc-500">{new Date(log.timestamp).toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* User Detail Dialog */}
        <Dialog open={userDetailOpen} onOpenChange={setUserDetailOpen}>
          <DialogContent className="bg-[#121212] border-zinc-800 max-w-2xl">
            <DialogHeader>
              <DialogTitle>User Details</DialogTitle>
            </DialogHeader>
            {selectedUser && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><p className="text-sm text-zinc-500">Email</p><p>{selectedUser.user?.email}</p></div>
                  <div><p className="text-sm text-zinc-500">Name</p><p>{selectedUser.user?.name || '-'}</p></div>
                  <div><p className="text-sm text-zinc-500">ID</p><p className="font-mono text-sm">{selectedUser.user?.id}</p></div>
                  <div><p className="text-sm text-zinc-500">Created</p><p>{new Date(selectedUser.user?.created_at).toLocaleString()}</p></div>
                </div>
                <div className="flex gap-2">
                  <Badge className={selectedUser.user?.is_verified ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                    {selectedUser.user?.is_verified ? 'Verified' : 'Unverified'}
                  </Badge>
                  <Badge className={selectedUser.user?.is_elite ? 'bg-[#FFB800]/20 text-[#FFB800]' : selectedUser.user?.is_pro ? 'bg-[#7B61FF]/20 text-[#7B61FF]' : 'bg-zinc-700 text-zinc-400'}>
                    {selectedUser.user?.is_elite ? 'Elite' : selectedUser.user?.is_pro ? 'Pro' : 'Free'}
                  </Badge>
                </div>
                {selectedUser.subscription && (
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-2">Subscription</p>
                    <p>Plan: {selectedUser.subscription.plan}</p>
                    <p>Status: {selectedUser.subscription.status}</p>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Smart Contract Section */}
        <div className="mt-8">
          <SmartContractPanel />
        </div>
      </div>
    </div>
  );
};

// Smart Contract Panel Component

export default AdminPage;
