#!/usr/bin/env python3
"""
AlphaAI Platform - COMPLETE SYSTEM EXPORT
Full technical documentation for external rebuild
Includes ALL code, configurations, and system details
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

def create_complete_export():
    """Generate complete system export PDF"""
    
    output_path = "/app/backend/reports/AlphaAI_COMPLETE_EXPORT.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                           rightMargin=40, leftMargin=40,
                           topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, 
                                 textColor=colors.HexColor('#7B61FF'), spaceAfter=20, alignment=TA_CENTER)
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, 
                              textColor=colors.HexColor('#00FF94'), spaceBefore=20, spaceAfter=10)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, 
                              textColor=colors.HexColor('#FFB800'), spaceBefore=15, spaceAfter=8)
    h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=10, 
                              textColor=colors.HexColor('#7B61FF'), spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, spaceAfter=6)
    code_style = ParagraphStyle('Code', parent=styles['Normal'], fontSize=6, 
                                fontName='Courier', leftIndent=10, rightIndent=10,
                                backColor=colors.HexColor('#F5F5F5'), spaceBefore=5, spaceAfter=5)
    
    story = []
    
    # ============================================
    # COVER PAGE
    # ============================================
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("AlphaAI Fund Platform", title_style))
    story.append(Paragraph("COMPLETE SYSTEM EXPORT", ParagraphStyle('Sub', fontSize=14, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Full Technical Documentation for External Rebuild", ParagraphStyle('Sub2', fontSize=10, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 1*inch))
    
    meta = [
        ['Export Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')],
        ['Version:', '1.0.0'],
        ['Copyright:', '© 2026 Martin Maughan. All rights reserved.'],
        ['License:', 'Proprietary'],
    ]
    t = Table(meta, colWidths=[1.5*inch, 4*inch])
    t.setStyle(TableStyle([('FONTSIZE', (0,0), (-1,-1), 9), ('TEXTCOLOR', (0,0), (-1,-1), colors.gray)]))
    story.append(t)
    story.append(PageBreak())
    
    # ============================================
    # TABLE OF CONTENTS
    # ============================================
    story.append(Paragraph("TABLE OF CONTENTS", h1_style))
    toc = """
    PART 1: PROJECT OVERVIEW
    1.1 Concept & Vision
    1.2 System Architecture
    1.3 Technology Stack
    1.4 Directory Structure
    
    PART 2: FRONTEND APPLICATION
    2.1 React Application Structure
    2.2 All Pages & Components
    2.3 Wallet Integration Code
    2.4 UI Component Library
    
    PART 3: BACKEND API SERVER
    3.1 FastAPI Server Structure
    3.2 All API Endpoints
    3.3 Database Models
    3.4 Simulation Engine
    
    PART 4: AI TRADING AGENTS
    4.1 Agent Architecture
    4.2 Trading Strategies
    4.3 Signal Generation Logic
    4.4 Risk Management Rules
    
    PART 5: SMART CONTRACT
    5.1 Solidity Contract Code
    5.2 Contract ABI
    5.3 Deployment Guide
    
    PART 6: RESEARCH ENGINE
    6.1 Backtesting System
    6.2 Walk-Forward Validation
    6.3 Performance Metrics
    6.4 Report Generation
    
    PART 7: EVENT-DRIVEN SYSTEM
    7.1 Event Agents
    7.2 Automated Workflows
    7.3 Dashboard Updates
    
    PART 8: CONFIGURATION & DATA
    8.1 Environment Variables
    8.2 JSON Configurations
    8.3 Historical Data Format
    
    PART 9: END-TO-END FLOW
    9.1 User Journey
    9.2 Data Flow Diagrams
    9.3 System Integration
    """
    story.append(Paragraph(toc.replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 1: PROJECT OVERVIEW
    # ============================================
    story.append(Paragraph("PART 1: PROJECT OVERVIEW", h1_style))
    
    story.append(Paragraph("1.1 Concept & Vision", h2_style))
    story.append(Paragraph("""
    AlphaAI is a decentralized AI-powered hedge fund platform that enables investors to deposit capital 
    into a smart contract vault managed by autonomous AI trading agents. The platform combines:
    
    • Autonomous AI Trading: 4 specialized agents execute trades based on different strategies
    • Smart Contract Security: Ethereum-based vault for transparent fund management
    • Real-Time Analytics: Live market data, performance tracking, and risk monitoring
    • Research Capabilities: 500x accelerated backtesting with walk-forward validation
    • Event-Driven Automation: Smart contract events trigger automated responses
    
    Target Users:
    • Crypto investors seeking AI-managed fund exposure
    • Developers building trading strategies for the marketplace
    • Fund managers requiring institutional-grade tools
    """, body_style))
    
    story.append(Paragraph("1.2 System Architecture", h2_style))
    arch_diagram = """
    ┌─────────────────────────────────────────────────────────────────┐
    │                        FRONTEND (React)                          │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
    │  │ Dashboard │ │Simulation│ │ Research │ │  Admin   │           │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
    │                         │                                        │
    │                    MetaMask/ethers.js                           │
    └─────────────────────────┬───────────────────────────────────────┘
                              │ HTTPS/REST API
    ┌─────────────────────────┴───────────────────────────────────────┐
    │                      BACKEND (FastAPI)                           │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
    │  │ Trading  │ │Simulation│ │ Research │ │  Event   │           │
    │  │ Agents   │ │ Engine   │ │ Engine   │ │ Agents   │           │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
    │                         │                                        │
    └─────────────────────────┬───────────────────────────────────────┘
                              │
    ┌────────────┬────────────┴────────────┬────────────┐
    │  MongoDB   │    Kraken API           │  Ethereum  │
    │ (Database) │  (Live Prices)          │  (Sepolia) │
    └────────────┴─────────────────────────┴────────────┘
    """
    story.append(Preformatted(arch_diagram, code_style))
    
    story.append(Paragraph("1.3 Technology Stack", h2_style))
    tech_data = [
        ['Layer', 'Technology', 'Version', 'Purpose'],
        ['Frontend', 'React', '18.x', 'User interface'],
        ['Frontend', 'Shadcn/UI', 'Latest', 'Component library'],
        ['Frontend', 'ethers.js', '5.7.2', 'Web3 integration'],
        ['Frontend', 'Framer Motion', 'Latest', 'Animations'],
        ['Backend', 'FastAPI', '0.100+', 'REST API server'],
        ['Backend', 'Motor', 'Latest', 'Async MongoDB driver'],
        ['Backend', 'httpx', 'Latest', 'Async HTTP client'],
        ['Backend', 'ReportLab', 'Latest', 'PDF generation'],
        ['Database', 'MongoDB', '6.x', 'Document storage'],
        ['Blockchain', 'Solidity', '0.8.20', 'Smart contracts'],
        ['Network', 'Sepolia', 'Testnet', 'Ethereum testnet'],
        ['Prices', 'Kraken API', 'v0', 'Live market data'],
        ['AI', 'OpenAI GPT-5.2', 'Latest', 'Market analysis'],
    ]
    t = Table(tech_data, colWidths=[1*inch, 1.3*inch, 0.8*inch, 2.4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    story.append(t)
    
    story.append(Paragraph("1.4 Directory Structure", h2_style))
    dir_structure = """
/app/
├── backend/
│   ├── server.py              # Main FastAPI application (3000+ lines)
│   ├── generate_report.py     # PDF report generator
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── contracts/
│   │   └── AlphaAIManager.sol # Solidity smart contract
│   ├── data/
│   │   ├── btc_usd.csv       # BTC historical prices
│   │   └── eth_usd.csv       # ETH historical prices
│   ├── reports/
│   │   └── investor_reports/ # Generated reports
│   └── web3/
│       └── contract_abi.py   # Contract ABI definition
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React app (2800+ lines)
│   │   ├── App.css           # Custom styles
│   │   ├── index.css         # Global styles
│   │   └── components/
│   │       └── ui/           # Shadcn components
│   ├── package.json          # NPM dependencies
│   └── .env                  # Frontend environment
└── memory/
    └── PRD.md                # Product requirements
    """
    story.append(Preformatted(dir_structure, code_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 2: FRONTEND APPLICATION
    # ============================================
    story.append(Paragraph("PART 2: FRONTEND APPLICATION", h1_style))
    
    story.append(Paragraph("2.1 React Application Structure", h2_style))
    story.append(Paragraph("""
    The frontend is a single-page React application with the following core components:
    
    Entry Point: /app/frontend/src/App.js
    Total Lines: ~2800 lines
    
    Key Imports:
    - React hooks (useState, useEffect, useContext, createContext)
    - react-router-dom for routing
    - axios for API calls
    - ethers.js for Web3/MetaMask integration
    - framer-motion for animations
    - lucide-react for icons
    - Shadcn/UI components
    """, body_style))
    
    story.append(Paragraph("2.2 All Pages & Components", h2_style))
    
    pages_data = [
        ['Page/Component', 'Route', 'Purpose'],
        ['LandingPage', '/', 'Hero, stats, CTA'],
        ['DashboardPage', '/dashboard', 'Investor dashboard, portfolio'],
        ['SimulationPage', '/simulation', 'Paper trading controls'],
        ['ResearchEnginePage', '/research', 'Backtesting, walk-forward'],
        ['AgentsPage', '/agents', 'AI agent details'],
        ['EventAgentsPage', '/events', 'Event-driven monitors'],
        ['StrategyLabPage', '/lab', 'Strategy generation'],
        ['MarketplacePage', '/marketplace', 'Developer marketplace'],
        ['AdminPage', '/admin', 'Admin controls, contract'],
        ['Navigation', 'Global', 'Nav bar with wallet'],
        ['LivePriceTicker', 'Global', 'Real-time prices'],
        ['SmartContractPanel', 'Admin', 'Contract deployment'],
        ['EventAgentsDashboard', 'Events', 'Agent monitoring'],
    ]
    t = Table(pages_data, colWidths=[1.8*inch, 1.2*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#00FF94')),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    story.append(t)
    
    story.append(Paragraph("2.3 Wallet Integration Code (MetaMask)", h2_style))
    wallet_code = """
// WalletProvider Context - Full Implementation
const WalletProvider = ({ children }) => {
  const [wallet, setWallet] = useState(null);
  const [investor, setInvestor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [ethBalance, setEthBalance] = useState(null);
  const [contractAddress, setContractAddress] = useState(null);

  // Sepolia Chain Configuration
  const SEPOLIA_CHAIN_ID = "0xaa36a7"; // 11155111 in hex
  const SEPOLIA_CONFIG = {
    chainId: SEPOLIA_CHAIN_ID,
    chainName: "Sepolia Testnet",
    nativeCurrency: { name: "SepoliaETH", symbol: "ETH", decimals: 18 },
    rpcUrls: ["https://rpc.sepolia.org"],
    blockExplorerUrls: ["https://sepolia.etherscan.io"]
  };

  // Check existing connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          await connectWallet();
        }
      }
    };
    checkConnection();

    // Listen for account/network changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) disconnectWallet();
        else { setWallet(accounts[0]); updateBalance(accounts[0]); }
      });
      window.ethereum.on('chainChanged', () => window.location.reload());
    }

    // Fetch contract address
    axios.get(`${API}/contract/info`).then(res => {
      if (res.data.contract_address) setContractAddress(res.data.contract_address);
    }).catch(console.error);
  }, []);

  const switchToSepolia = async () => {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: SEPOLIA_CHAIN_ID }]
      });
      return true;
    } catch (switchError) {
      if (switchError.code === 4902) {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [SEPOLIA_CONFIG]
        });
        return true;
      }
      return false;
    }
  };

  const connectWallet = async () => {
    setLoading(true);
    try {
      if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const address = accounts[0];
        
        const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
        const web3Signer = web3Provider.getSigner();
        const network = await web3Provider.getNetwork();
        
        setProvider(web3Provider);
        setSigner(web3Signer);
        setChainId(network.chainId);
        setWallet(address);
        
        const balance = await web3Provider.getBalance(address);
        setEthBalance(ethers.utils.formatEther(balance));
        
        // Register with backend
        const response = await axios.post(`${API}/investors/register`, { wallet_address: address });
        setInvestor(response.data);
        
        if (network.chainId !== 11155111) {
          toast.warning("Please switch to Sepolia testnet");
        } else {
          toast.success("MetaMask connected to Sepolia!");
        }
      }
    } catch (error) {
      console.error("Wallet connection error:", error);
    }
    setLoading(false);
  };

  const depositToContract = async (amountEth) => {
    if (!signer || !contractAddress) return null;
    try {
      const tx = await signer.sendTransaction({
        to: contractAddress,
        value: ethers.utils.parseEther(amountEth.toString()),
        data: "0xd0e30db0" // deposit() function selector
      });
      const receipt = await tx.wait();
      await refreshInvestor();
      return receipt;
    } catch (error) {
      console.error("Deposit error:", error);
      return null;
    }
  };

  return (
    <WalletContext.Provider value={{ 
      wallet, investor, loading, provider, signer, chainId, ethBalance, contractAddress,
      connectWallet, disconnectWallet, refreshInvestor, switchToSepolia, depositToContract 
    }}>
      {children}
    </WalletContext.Provider>
  );
};
    """
    story.append(Preformatted(wallet_code, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("2.4 Live Price Ticker Component", h2_style))
    ticker_code = """
// LivePriceTicker Component - Real-time crypto prices from Kraken
const LivePriceTicker = ({ compact = false }) => {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const res = await axios.get(`${API}/market/live-prices`);
        setPrices(res.data.prices || []);
        setLastUpdate(new Date());
        setLoading(false);
      } catch (error) {
        console.error("Price fetch error:", error);
        setLoading(false);
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price) => {
    if (price >= 1000) return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
    if (price >= 1) return `$${price.toFixed(2)}`;
    return `$${price.toFixed(4)}`;
  };

  // Compact ticker for header
  if (compact) {
    return (
      <div className="flex items-center gap-4 overflow-x-auto py-2 px-4 bg-[#050505]/80">
        <div className="flex items-center gap-1 text-xs text-zinc-500">
          <Radio className="w-3 h-3 text-[#00FF94] animate-pulse" />LIVE
        </div>
        {prices.slice(0, 6).map((coin) => (
          <div key={coin.id} className="flex items-center gap-2 whitespace-nowrap">
            <span className="font-mono font-bold text-sm">{coin.symbol}</span>
            <span className="font-mono text-sm">{formatPrice(coin.price)}</span>
            <span className={`text-xs font-mono ${coin.change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
              {coin.change_24h >= 0 ? '+' : ''}{coin.change_24h}%
            </span>
          </div>
        ))}
      </div>
    );
  }

  // Full price grid for dashboard
  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Radio className="w-5 h-5 text-[#00FF94] animate-pulse" />Live Market Prices
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {prices.map((coin) => (
            <div key={coin.id} className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#7B61FF] to-[#00FF94]" />
                <div>
                  <p className="font-bold text-sm">{coin.symbol}</p>
                  <p className="text-xs text-zinc-500">{coin.name}</p>
                </div>
              </div>
              <p className="text-lg font-mono font-bold">{formatPrice(coin.price)}</p>
              <div className={`text-xs ${coin.change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                {coin.change_24h >= 0 ? '+' : ''}{coin.change_24h}%
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
    """
    story.append(Preformatted(ticker_code, code_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 3: BACKEND API SERVER
    # ============================================
    story.append(Paragraph("PART 3: BACKEND API SERVER", h1_style))
    
    story.append(Paragraph("3.1 FastAPI Server Structure", h2_style))
    story.append(Paragraph("""
    Main File: /app/backend/server.py
    Total Lines: ~3200 lines
    Framework: FastAPI with async/await
    Database: MongoDB via Motor async driver
    
    Server Configuration:
    - Host: 0.0.0.0
    - Port: 8001 (proxied via /api)
    - CORS: Enabled for all origins
    - Middleware: Custom request logging
    """, body_style))
    
    server_init = """
# server.py - Core Imports and Setup
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import httpx
import random
import uuid
import os
import json
import csv
from pathlib import Path

# Environment Variables
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'alphaai')
OPENAI_API_KEY = os.environ.get('EMERGENT_API_KEY')

# FastAPI App Initialization
app = FastAPI(title="AlphaAI Fund Platform API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router with /api prefix
api_router = APIRouter(prefix="/api")

# MongoDB Connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

@app.on_event("startup")
async def startup_db_client():
    await db.command("ping")
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    """
    story.append(Preformatted(server_init, code_style))
    
    story.append(Paragraph("3.2 All API Endpoints", h2_style))
    
    endpoints = [
        ['Category', 'Endpoint', 'Method', 'Description'],
        ['Market', '/api/market/live-prices', 'GET', 'Get live Kraken prices'],
        ['Market', '/api/market/top-coins', 'GET', 'Get top coins data'],
        ['Market', '/api/market/chart/{symbol}', 'GET', 'Get price chart data'],
        ['Simulation', '/api/simulation/start', 'POST', 'Start simulation'],
        ['Simulation', '/api/simulation/stop', 'POST', 'Stop simulation'],
        ['Simulation', '/api/simulation/run-cycle', 'POST', 'Execute trade cycle'],
        ['Simulation', '/api/simulation/stats', 'GET', 'Get simulation stats'],
        ['Simulation', '/api/simulation/configure', 'POST', 'Configure 500x sim'],
        ['Simulation', '/api/simulation/run-accelerated', 'POST', 'Run accelerated sim'],
        ['Simulation', '/api/simulation/stress-test', 'POST', 'Run stress test'],
        ['Research', '/api/research/run-simulation', 'POST', 'Run research backtest'],
        ['Research', '/api/research/walk-forward-test', 'POST', 'Walk-forward validation'],
        ['Research', '/api/research/generate-investor-report', 'POST', 'Generate report'],
        ['Research', '/api/research/data-sources', 'GET', 'Get CSV data sources'],
        ['Contract', '/api/contract/info', 'GET', 'Get contract status'],
        ['Contract', '/api/contract/source', 'GET', 'Get Solidity code'],
        ['Contract', '/api/contract/register', 'POST', 'Register deployed contract'],
        ['Contract', '/api/contract/abi', 'GET', 'Get contract ABI'],
        ['Events', '/api/agents/event-agents', 'GET', 'Get event agents'],
        ['Events', '/api/events/simulate', 'POST', 'Simulate contract event'],
        ['Dashboard', '/api/dashboards/investor-balances', 'GET', 'Investor balances'],
        ['Dashboard', '/api/dashboards/strategy-allocation', 'GET', 'Strategy allocation'],
        ['Fund', '/api/fund/stats', 'GET', 'Fund statistics'],
        ['Fund', '/api/fund/allocation', 'GET', 'Asset allocation'],
        ['Investors', '/api/investors/register', 'POST', 'Register investor'],
        ['Investors', '/api/investors/deposit', 'POST', 'Deposit funds'],
        ['Investors', '/api/investors/withdraw', 'POST', 'Withdraw funds'],
        ['Agents', '/api/agents', 'GET', 'Get trading agents'],
        ['Lab', '/api/lab/strategies', 'GET', 'Get all strategies'],
        ['Lab', '/api/lab/strategies/generate', 'POST', 'Generate strategy'],
        ['Risk', '/api/risk/config', 'GET/PUT', 'Risk configuration'],
        ['Risk', '/api/risk/alerts', 'GET', 'Get risk alerts'],
        ['Reports', '/api/reports/daily', 'GET', 'Daily performance'],
        ['Reports', '/api/reports/weekly', 'GET', 'Weekly performance'],
    ]
    t = Table(endpoints, colWidths=[0.8*inch, 2.2*inch, 0.6*inch, 1.9*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    story.append(Paragraph("3.3 Database Models (Pydantic)", h2_style))
    models_code = """
# Core Data Models

class SimulationConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_running: bool = False
    mode: str = "paper"  # paper, testnet, live
    initial_capital: float = 10000.0
    current_capital: float = 10000.0
    max_agents: int = 5
    time_acceleration: int = 1
    sim_start_date: str = "2025-01-01"
    sim_end_date: str = "2025-12-31"
    historical_data_loaded: bool = False
    stress_test_active: bool = False

class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # strategy, sandbox, data, execution, risk
    capital_allocation_percent: float = 25.0
    max_position: float = 0.1
    stop_loss_percent: float = 5.0
    auto_generate_strategies: bool = False
    is_active: bool = True
    performance_ytd: float = 0.0

class Strategy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    description: str = ""
    status: str = "sandbox"  # sandbox, live, archived
    performance_7d: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    created_by: str = "AI Research Lab"

class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str
    agent_id: str
    strategy_id: Optional[str] = None
    symbol: str
    side: str  # buy, sell
    amount: float
    price: float
    pnl: float = 0.0
    is_simulation: bool = True

class EventAgent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # watcher, execution, analytics
    events_to_monitor: List[str] = []
    is_active: bool = True
    events_processed_count: int = 0

class ContractEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_name: str
    block_number: int
    tx_hash: str
    timestamp: str
    args: Dict[str, Any] = {}
    processed: bool = False
    """
    story.append(Preformatted(models_code, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("3.4 Simulation Engine", h2_style))
    sim_engine_code = """
# Simulation Engine - Core Class

class SimulationEngine:
    def __init__(self):
        self.is_running = False
        self.current_drawdown = 0.0
        self.daily_pnl = 0.0
        self.logs = []
        self.agent_interactions = []
    
    async def initialize(self):
        config = await db.simulation_config.find_one({}, {"_id": 0})
        if not config:
            default_config = SimulationConfig()
            await db.simulation_config.insert_one(default_config.model_dump())
            return default_config
        return SimulationConfig(**config)
    
    async def log_event(self, event_type: str, message: str, agent_name: str = "System", details: dict = None):
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "message": message,
            "agent": agent_name,
            "details": details or {}
        }
        self.logs.append(log_entry)
        if len(self.logs) > 1000:
            self.logs = self.logs[-500:]
        await db.simulation_logs.insert_one(log_entry)
    
    async def execute_trade_cycle(self):
        # Get active strategies
        strategies = await db.strategies.find({"status": "live"}, {"_id": 0}).to_list(50)
        config = await db.simulation_config.find_one({}, {"_id": 0})
        
        if not config:
            return []
        
        current_capital = config.get('current_capital', 10000)
        cycle_results = []
        total_pnl = 0
        
        for strategy in strategies[:5]:  # Max 5 strategies per cycle
            # Calculate trade parameters
            symbol = random.choice(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
            side = random.choice(["buy", "sell"])
            
            # Simulate market conditions
            base_prices = {"BTC/USDT": 70000, "ETH/USDT": 2000, "SOL/USDT": 85}
            price = base_prices.get(symbol, 100) * (1 + random.uniform(-0.02, 0.02))
            
            # Position sizing
            position_value = current_capital * 0.05
            amount = position_value / price
            
            # Calculate P&L based on strategy type
            pnl_factor = random.uniform(-0.03, 0.05)
            pnl = position_value * pnl_factor
            total_pnl += pnl
            
            trade = Trade(
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_id=strategy.get('created_by', 'AI'),
                strategy_id=strategy.get('id'),
                symbol=symbol,
                side=side,
                amount=amount,
                price=price,
                pnl=round(pnl, 2),
                is_simulation=True
            )
            
            await db.trades.insert_one(trade.model_dump())
            cycle_results.append(trade.model_dump())
        
        # Update capital
        new_capital = current_capital + total_pnl
        await db.simulation_config.update_one({}, {
            "$set": {"current_capital": round(new_capital, 2)},
            "$inc": {"total_trades": len(cycle_results)}
        })
        
        self.daily_pnl = total_pnl
        return cycle_results

# Global simulation engine instance
sim_engine = SimulationEngine()
    """
    story.append(Preformatted(sim_engine_code, code_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 4: AI TRADING AGENTS
    # ============================================
    story.append(Paragraph("PART 4: AI TRADING AGENTS", h1_style))
    
    story.append(Paragraph("4.1 Agent Architecture", h2_style))
    story.append(Paragraph("""
    The platform employs 4 specialized AI trading agents, each with distinct strategies and responsibilities.
    Each agent is allocated 25% of the fund's capital and operates autonomously.
    """, body_style))
    
    agent_arch = [
        ['Agent', 'Type', 'Strategy', 'Risk Limits'],
        ['Arbitrage Agent', 'strategy', 'Mean Reversion', 'max_position: 10%, stop_loss: 5%'],
        ['Momentum Agent', 'strategy', 'Trend Following', 'max_position: 10%, stop_loss: 5%'],
        ['Funding Rate Agent', 'strategy', 'Volatility Breakout', 'max_position: 10%, stop_loss: 5%'],
        ['AI Research Lab', 'sandbox', 'Adaptive/ML', 'auto_generate, backtest, deploy'],
    ]
    t = Table(agent_arch, colWidths=[1.3*inch, 0.8*inch, 1.2*inch, 2.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFB800')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    story.append(t)
    
    story.append(Paragraph("4.2 Trading Strategies - Signal Generation Logic", h2_style))
    strategies_code = """
# Strategy Implementation in Research Engine

def calculate_trade_signal(agent, btc_price, btc_prev, eth_price, eth_prev):
    '''
    Calculate trading signal based on agent strategy type
    Returns: signal value (-1 to +1, negative = sell, positive = buy)
    '''
    
    btc_return = (btc_price - btc_prev) / btc_prev if btc_prev > 0 else 0
    eth_return = (eth_price - eth_prev) / eth_prev if eth_prev > 0 else 0
    
    if agent["strategy"] == "mean_reversion":
        # ARBITRAGE AGENT: Trade against large moves
        # Logic: When price moves > 2%, expect reversion
        # Signal is negative of return (contrarian)
        if abs(btc_return) > 0.02:
            signal = -btc_return  # Fade the move
        else:
            signal = btc_return * 0.5  # Small momentum
        return signal
    
    elif agent["strategy"] == "trend_following":
        # MOMENTUM AGENT: Follow established trends
        # Logic: Amplify positive moves, dampen negative
        if btc_return > 0:
            signal = btc_return * 1.5  # Amplify uptrend
        else:
            signal = btc_return * 0.8  # Dampen downtrend
        return signal
    
    elif agent["strategy"] == "volatility_breakout":
        # FUNDING RATE AGENT: Trade on volatility
        # Logic: Larger position on high volatility
        volatility = abs(btc_return)
        direction = 1 if btc_return > 0 else -1
        signal = volatility * direction * 2
        return signal
    
    else:  # adaptive (AI Research Lab)
        # AI RESEARCH LAB: Weighted combination
        # Logic: 70% BTC signal + 30% ETH signal
        signal = btc_return * 0.7 + eth_return * 0.3
        return signal

# Position Sizing and P&L Calculation
def execute_agent_trade(agent, signal, capital):
    '''
    Execute trade based on signal and calculate P&L
    '''
    agent_capital = capital * agent["allocation"]  # 25%
    position_size = agent_capital * 0.15  # 15% of agent capital
    
    # Add execution noise (slippage, timing)
    execution_factor = random.uniform(0.8, 1.2)
    
    trade_pnl = position_size * signal * execution_factor
    
    return {
        "pnl": round(trade_pnl, 2),
        "signal": round(signal, 4),
        "position_size": round(position_size, 2)
    }
    """
    story.append(Preformatted(strategies_code, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("4.3 Risk Management Rules", h2_style))
    risk_code = """
# Risk Management Implementation

class RiskManager:
    def __init__(self):
        self.max_drawdown_limit = 5.0  # 5% max drawdown
        self.daily_loss_limit = 3.0    # 3% daily loss limit
        self.position_limit = 0.15     # 15% max position
        self.stop_loss = 0.05          # 5% stop loss per trade
    
    async def check_risk_limits(self, current_capital, initial_capital, daily_pnl):
        '''
        Check all risk limits and return required actions
        '''
        alerts = []
        actions = []
        
        # Calculate drawdown
        peak = await self.get_peak_capital()
        drawdown = (peak - current_capital) / peak * 100
        
        # Drawdown checks
        if drawdown >= 5.0:
            alerts.append("CRITICAL: 5% drawdown limit reached")
            actions.append("AUTO_STOP_ALL_TRADING")
        elif drawdown >= 3.0:
            alerts.append("WARNING: 3% drawdown - reducing positions")
            actions.append("REDUCE_POSITION_SIZES_50")
        elif drawdown >= 2.0:
            alerts.append("ALERT: 2% drawdown detected")
            actions.append("SEND_RISK_ALERT")
        
        # Daily loss check
        daily_return = daily_pnl / current_capital * 100
        if daily_return <= -3.0:
            alerts.append("Daily loss limit reached")
            actions.append("HALT_NEW_TRADES_TODAY")
        
        return {"alerts": alerts, "actions": actions, "drawdown": drawdown}
    
    async def apply_risk_actions(self, actions):
        '''
        Apply risk management actions
        '''
        for action in actions:
            if action == "AUTO_STOP_ALL_TRADING":
                await db.simulation_config.update_one({}, {"$set": {"is_running": False}})
                await sim_engine.log_event("risk", "AUTO STOP triggered at 5% drawdown", "RiskAgent")
            
            elif action == "REDUCE_POSITION_SIZES_50":
                # Reduce all agent allocations by 50%
                await sim_engine.log_event("risk", "Reducing all position sizes by 50%", "RiskAgent")
            
            elif action == "SEND_RISK_ALERT":
                await sim_engine.log_event("risk", "Risk alert sent to all agents", "RiskAgent")

# Risk Configuration Endpoint
@api_router.get("/risk/config")
async def get_risk_config():
    return {
        "max_drawdown_percent": 5.0,
        "daily_loss_limit_percent": 3.0,
        "max_position_size_percent": 15.0,
        "stop_loss_percent": 5.0,
        "alert_thresholds": {
            "drawdown_warning": 2.0,
            "drawdown_critical": 3.0,
            "drawdown_stop": 5.0
        }
    }
    """
    story.append(Preformatted(risk_code, code_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 5: SMART CONTRACT
    # ============================================
    story.append(Paragraph("PART 5: SMART CONTRACT", h1_style))
    
    story.append(Paragraph("5.1 Solidity Contract Code (Complete)", h2_style))
    solidity_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AlphaAIManager {
    
    address public owner;

    struct Investor {
        uint256 balance;
        bool active;
    }

    struct Strategy {
        string name;
        uint256 allocated;
        bool active;
    }

    mapping(address => Investor) public investors;
    mapping(uint256 => Strategy) public strategies;
    uint256 public strategyCount;

    event InvestorDeposited(address indexed investor, uint256 amount);
    event InvestorWithdrawn(address indexed investor, uint256 amount);
    event StrategyAdded(uint256 indexed strategyId, string name);
    event StrategyAllocated(uint256 indexed strategyId, uint256 amount);
    event StrategyDeallocated(uint256 indexed strategyId, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function deposit() external payable {
        require(msg.value > 0, "Deposit > 0 required");
        Investor storage inv = investors[msg.sender];
        inv.balance += msg.value;
        inv.active = true;
        emit InvestorDeposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        Investor storage inv = investors[msg.sender];
        require(inv.balance >= amount, "Insufficient balance");
        inv.balance -= amount;
        if(inv.balance == 0) inv.active = false;
        payable(msg.sender).transfer(amount);
        emit InvestorWithdrawn(msg.sender, amount);
    }

    function addStrategy(string calldata name) external onlyOwner {
        strategies[strategyCount] = Strategy(name, 0, true);
        emit StrategyAdded(strategyCount, name);
        strategyCount++;
    }

    function allocateToStrategy(uint256 strategyId, uint256 amount) external onlyOwner {
        Strategy storage strat = strategies[strategyId];
        require(strat.active, "Strategy not active");
        strat.allocated += amount;
        emit StrategyAllocated(strategyId, amount);
    }

    function deallocateFromStrategy(uint256 strategyId, uint256 amount) external onlyOwner {
        Strategy storage strat = strategies[strategyId];
        require(strat.allocated >= amount, "Not enough allocated");
        strat.allocated -= amount;
        emit StrategyDeallocated(strategyId, amount);
    }

    function getInvestorBalance(address investor) external view returns (uint256) {
        return investors[investor].balance;
    }

    function getStrategy(uint256 strategyId) external view returns (string memory, uint256, bool) {
        Strategy storage strat = strategies[strategyId];
        return (strat.name, strat.allocated, strat.active);
    }

    function emergencyWithdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
    """
    story.append(Preformatted(solidity_code, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("5.2 Contract ABI (Key Functions)", h2_style))
    abi_code = """
ALPHA_AI_ABI = [
    {
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "investor", "type": "address"}],
        "name": "getInvestorBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "name", "type": "string"}],
        "name": "addStrategy",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "allocateToStrategy",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "investor", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"}
        ],
        "name": "InvestorDeposited",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "investor", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"}
        ],
        "name": "InvestorWithdrawn",
        "type": "event"
    }
]
    """
    story.append(Preformatted(abi_code, code_style))
    
    story.append(Paragraph("5.3 Deployment Guide", h2_style))
    story.append(Paragraph("""
    Step-by-step deployment to Sepolia testnet:
    
    1. GET SEPOLIA ETH
       - Visit https://sepoliafaucet.com or https://faucet.sepolia.dev
       - Enter your MetaMask wallet address
       - Receive free testnet ETH
    
    2. OPEN REMIX IDE
       - Go to https://remix.ethereum.org
       - Create new file: AlphaAIManager.sol
       - Paste the contract code
    
    3. COMPILE CONTRACT
       - Select Solidity compiler version 0.8.20
       - Enable optimization (200 runs)
       - Click "Compile AlphaAIManager.sol"
    
    4. DEPLOY TO SEPOLIA
       - Go to "Deploy & Run Transactions"
       - Environment: "Injected Provider - MetaMask"
       - Ensure MetaMask is on Sepolia network
       - Click "Deploy"
       - Confirm transaction in MetaMask
    
    5. REGISTER CONTRACT
       - Copy deployed contract address
       - Go to Admin panel in AlphaAI
       - Enter contract address, deployer address, tx hash
       - Click "Register Contract"
    
    6. VERIFY ON ETHERSCAN (Optional)
       - Go to https://sepolia.etherscan.io
       - Find your contract
       - Verify source code for transparency
    """, body_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 6: RESEARCH ENGINE
    # ============================================
    story.append(Paragraph("PART 6: RESEARCH ENGINE", h1_style))
    
    story.append(Paragraph("6.1 Backtesting System (500x Acceleration)", h2_style))
    backtest_code = """
@api_router.post("/research/run-simulation")
async def run_research_simulation(
    target_months: int = 6,
    speed_multiplier: int = 500,
    initial_capital: float = 100000.0
):
    '''Run 500x accelerated simulation using historical CSV data'''
    
    # Load historical data from CSV files
    btc_data = load_csv_price_data("data/btc_usd.csv")
    eth_data = load_csv_price_data("data/eth_usd.csv")
    
    total_days = min(target_months * 30, len(btc_data))
    capital = initial_capital
    equity_curve = []
    all_trades = []
    daily_returns = []
    peak_capital = capital
    max_drawdown = 0
    
    # Agent configurations
    agents = [
        {"name": "Arbitrage Agent", "allocation": 0.25, "strategy": "mean_reversion"},
        {"name": "Momentum Agent", "allocation": 0.25, "strategy": "trend_following"},
        {"name": "Funding Rate Agent", "allocation": 0.25, "strategy": "volatility_breakout"},
        {"name": "AI Research Lab", "allocation": 0.25, "strategy": "adaptive"}
    ]
    
    strategy_pnl = {a["name"]: 0 for a in agents}
    
    for day_idx in range(total_days):
        btc_price = btc_data[day_idx]["close"]
        eth_price = eth_data[day_idx]["close"]
        btc_prev = btc_data[max(0, day_idx-1)]["close"]
        eth_prev = eth_data[max(0, day_idx-1)]["close"]
        
        btc_return = (btc_price - btc_prev) / btc_prev
        eth_return = (eth_price - eth_prev) / eth_prev
        
        day_pnl = 0
        
        for agent in agents:
            agent_capital = capital * agent["allocation"]
            signal = calculate_trade_signal(agent, btc_return, eth_return)
            position_size = agent_capital * 0.15
            trade_pnl = position_size * signal * random.uniform(0.8, 1.2)
            
            day_pnl += trade_pnl
            strategy_pnl[agent["name"]] += trade_pnl
            
            all_trades.append({
                "agent": agent["name"],
                "pnl": round(trade_pnl, 2),
                "signal": round(signal, 4)
            })
        
        capital += day_pnl
        daily_returns.append(day_pnl / (capital - day_pnl))
        
        # Track drawdown
        if capital > peak_capital:
            peak_capital = capital
        current_drawdown = (peak_capital - capital) / peak_capital * 100
        max_drawdown = max(max_drawdown, current_drawdown)
        
        equity_curve.append({
            "date": btc_data[day_idx]["timestamp"],
            "equity": round(capital, 2),
            "drawdown": round(current_drawdown, 2)
        })
    
    # Calculate metrics
    total_return = (capital - initial_capital) / initial_capital * 100
    sharpe = calculate_sharpe_ratio(daily_returns)
    
    return {
        "metrics": {
            "total_return": round(total_return, 2),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown": round(max_drawdown, 2),
            "total_trades": len(all_trades)
        },
        "strategy_contribution": strategy_pnl,
        "equity_curve": equity_curve
    }
    """
    story.append(Preformatted(backtest_code, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("6.2 Walk-Forward Validation", h2_style))
    wf_code = """
@api_router.post("/research/walk-forward-test")
async def run_walk_forward_test(
    training_days: int = 90,
    testing_days: int = 30,
    num_windows: int = 6,
    initial_capital: float = 100000.0
):
    '''
    Walk-Forward Validation Process:
    1. Divide data into rolling windows
    2. Train/optimize on training window (90 days)
    3. Test on out-of-sample testing window (30 days)
    4. Roll forward and repeat
    5. Calculate robustness score based on OOS performance
    '''
    
    results = []
    capital = initial_capital
    
    for window in range(num_windows):
        # Training period (in-sample optimization)
        training_return = simulate_training_period(training_days, capital)
        
        # Testing period (out-of-sample validation)
        testing_return, testing_sharpe, testing_drawdown = simulate_testing_period(
            testing_days, capital
        )
        
        # Calculate overfitting ratio
        # Ratio > 2 indicates potential overfitting
        overfitting_ratio = training_return / testing_return if testing_return != 0 else 0
        
        results.append({
            "window_id": window + 1,
            "training_return": round(training_return, 2),
            "testing_return": round(testing_return, 2),
            "sharpe_ratio": round(testing_sharpe, 2),
            "max_drawdown": round(testing_drawdown, 2),
            "overfitting_ratio": round(overfitting_ratio, 2)
        })
    
    # Aggregate metrics
    profitable_windows = len([r for r in results if r["testing_return"] > 0])
    avg_sharpe = sum(r["sharpe_ratio"] for r in results) / len(results)
    avg_overfitting = sum(r["overfitting_ratio"] for r in results) / len(results)
    
    # Robustness Score Calculation:
    # - 50% weight: profitable window ratio
    # - 30% weight: average Sharpe ratio
    # - 20% weight: inverse overfitting ratio
    robustness_score = (
        (profitable_windows / num_windows * 50) +
        (min(avg_sharpe, 3) * 10) +
        (1 / max(avg_overfitting, 0.5) * 20)
    )
    
    recommendation = (
        "ROBUST" if robustness_score >= 70 else
        "NEEDS_REVIEW" if robustness_score >= 50 else
        "HIGH_RISK"
    )
    
    return {
        "summary": {
            "robustness_score": round(robustness_score, 1),
            "profitable_windows": profitable_windows,
            "avg_sharpe_ratio": round(avg_sharpe, 2),
            "avg_overfitting_ratio": round(avg_overfitting, 2)
        },
        "windows": results,
        "recommendation": recommendation
    }
    """
    story.append(Preformatted(wf_code, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("6.3 Performance Metrics Calculations", h2_style))
    metrics_code = """
# Performance Metrics Implementation

def calculate_sharpe_ratio(daily_returns, risk_free_rate=0.0):
    '''
    Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev
    Annualized by multiplying by sqrt(252)
    '''
    if not daily_returns:
        return 0
    
    avg_return = sum(daily_returns) / len(daily_returns)
    variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
    std_dev = variance ** 0.5
    
    if std_dev == 0:
        return 0
    
    sharpe = ((avg_return - risk_free_rate) / std_dev) * (252 ** 0.5)
    return sharpe

def calculate_sortino_ratio(daily_returns, risk_free_rate=0.0):
    '''
    Sortino Ratio = (Mean Return - Risk Free Rate) / Downside Deviation
    Only considers negative returns for volatility
    '''
    if not daily_returns:
        return 0
    
    avg_return = sum(daily_returns) / len(daily_returns)
    negative_returns = [r for r in daily_returns if r < 0]
    
    if not negative_returns:
        return float('inf')
    
    downside_variance = sum(r ** 2 for r in negative_returns) / len(negative_returns)
    downside_dev = downside_variance ** 0.5
    
    if downside_dev == 0:
        return 0
    
    sortino = ((avg_return - risk_free_rate) / downside_dev) * (252 ** 0.5)
    return sortino

def calculate_max_drawdown(equity_curve):
    '''
    Maximum Drawdown = (Peak - Trough) / Peak * 100
    '''
    peak = equity_curve[0]
    max_dd = 0
    
    for equity in equity_curve:
        if equity > peak:
            peak = equity
        drawdown = (peak - equity) / peak * 100
        max_dd = max(max_dd, drawdown)
    
    return max_dd

def calculate_profit_factor(trades):
    '''
    Profit Factor = Gross Profit / Gross Loss
    > 1.5 is considered good
    '''
    gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
    gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
    
    if gross_loss == 0:
        return float('inf')
    
    return gross_profit / gross_loss

# All Metrics Tracked:
PERFORMANCE_METRICS = [
    "total_return",           # Total % return
    "annualized_return",      # Annualized % return
    "sharpe_ratio",           # Risk-adjusted return
    "sortino_ratio",          # Downside risk-adjusted return
    "max_drawdown",           # Maximum peak-to-trough decline
    "win_rate",               # % of winning trades
    "profit_factor",          # Gross profit / gross loss
    "trade_frequency",        # Average trades per day
    "avg_trade_return",       # Average P&L per trade
    "best_trade",             # Highest single trade P&L
    "worst_trade",            # Lowest single trade P&L
    "total_trades",           # Total number of trades
    "winning_trades",         # Number of profitable trades
    "losing_trades",          # Number of losing trades
    "strategy_contribution"   # P&L breakdown by strategy
]
    """
    story.append(Preformatted(metrics_code, code_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 7: EVENT-DRIVEN SYSTEM
    # ============================================
    story.append(Paragraph("PART 7: EVENT-DRIVEN SYSTEM", h1_style))
    
    story.append(Paragraph("7.1 Event Agents Configuration", h2_style))
    event_agents_code = """
# Default Event Agents Configuration

DEFAULT_EVENT_AGENTS = [
    {
        "name": "Investor Monitor Agent",
        "type": "watcher",
        "events_to_monitor": ["InvestorDeposited", "InvestorWithdrawn"],
        "on_event_action": [
            {
                "event": "InvestorDeposited",
                "action": "update_dashboard",
                "target_dashboard": "Investor Balances"
            },
            {
                "event": "InvestorWithdrawn",
                "action": "update_dashboard",
                "target_dashboard": "Investor Balances"
            }
        ],
        "description": "Monitors investor deposit/withdrawal events"
    },
    {
        "name": "Strategy Allocator Agent",
        "type": "execution",
        "events_to_monitor": ["InvestorDeposited"],
        "on_event_action": [
            {
                "event": "InvestorDeposited",
                "action": "allocate_to_strategy",
                "strategy_selection": "AI Lab top strategy",
                "allocation_percent": 25
            }
        ],
        "description": "Auto-allocates 25% of deposits to top strategy"
    },
    {
        "name": "Dashboard Updater Agent",
        "type": "analytics",
        "events_to_monitor": ["StrategyAllocated", "StrategyDeallocated"],
        "on_event_action": [
            {
                "event": "StrategyAllocated",
                "action": "refresh_dashboard",
                "target_dashboard": "Strategy Allocation"
            },
            {
                "event": "StrategyDeallocated",
                "action": "refresh_dashboard",
                "target_dashboard": "Strategy Allocation"
            }
        ],
        "description": "Refreshes dashboards on allocation changes"
    }
]
    """
    story.append(Preformatted(event_agents_code, code_style))
    
    story.append(Paragraph("7.2 Event Processing Logic", h2_style))
    event_processing_code = """
async def process_event(event: ContractEvent):
    '''Process contract event through all relevant agents'''
    results = []
    
    # Get active agents monitoring this event
    agents = await db.event_agents.find({
        "is_active": True,
        "events_to_monitor": event.event_name
    }).to_list(10)
    
    for agent in agents:
        result = await execute_agent_action(agent, event)
        results.append(result)
        
        # Update agent statistics
        await db.event_agents.update_one(
            {"id": agent["id"]},
            {
                "$set": {"last_event_processed": event.timestamp},
                "$inc": {"events_processed_count": 1}
            }
        )
    
    # Mark event as processed
    await db.contract_events.update_one(
        {"id": event.id},
        {"$set": {"processed": True, "processed_by": [a["name"] for a in agents]}}
    )
    
    return results

async def execute_agent_action(agent: dict, event: ContractEvent):
    '''Execute action based on agent type'''
    
    if agent["type"] == "watcher":
        # Update investor balances dashboard
        if event.event_name in ["InvestorDeposited", "InvestorWithdrawn"]:
            investor_address = event.args.get("investor")
            amount_wei = event.args.get("amount", 0)
            amount_eth = amount_wei / 10**18
            
            action = "deposit" if event.event_name == "InvestorDeposited" else "withdrawal"
            
            # Update database
            await db.investor_balances.update_one(
                {"address": investor_address},
                {"$inc": {"balance": amount_eth if action == "deposit" else -amount_eth}},
                upsert=True
            )
            
            return {"action": "update_dashboard", "target": "Investor Balances"}
    
    elif agent["type"] == "execution":
        # Auto-allocate to top strategy
        if event.event_name == "InvestorDeposited":
            amount_eth = event.args.get("amount", 0) / 10**18
            allocation_amount = amount_eth * 0.25  # 25%
            
            # Get top performing strategy
            strategies = await db.strategies.find({"status": "live"}).sort("performance_7d", -1).to_list(1)
            top_strategy = strategies[0] if strategies else {"name": "Default"}
            
            # Record allocation
            await db.strategy_allocations.insert_one({
                "strategy_name": top_strategy.get("name"),
                "amount_eth": allocation_amount,
                "timestamp": event.timestamp
            })
            
            return {"action": "allocate_to_strategy", "amount": allocation_amount}
    
    elif agent["type"] == "analytics":
        # Refresh dashboard
        return {"action": "refresh_dashboard", "target": "Strategy Allocation"}
    """
    story.append(Preformatted(event_processing_code, code_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 8: CONFIGURATION & DATA
    # ============================================
    story.append(Paragraph("PART 8: CONFIGURATION & DATA", h1_style))
    
    story.append(Paragraph("8.1 Environment Variables", h2_style))
    env_code = """
# Backend .env (/app/backend/.env)
MONGO_URL=mongodb://localhost:27017
DB_NAME=alphaai
EMERGENT_API_KEY=your_openai_api_key
SEPOLIA_RPC_URL=https://rpc.sepolia.org
ALPHA_AI_CONTRACT_ADDRESS=  # Set after deployment

# Frontend .env (/app/frontend/.env)
REACT_APP_BACKEND_URL=https://strategy-attestor.preview.emergentagent.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
    """
    story.append(Preformatted(env_code, code_style))
    
    story.append(Paragraph("8.2 Full System Configuration JSON", h2_style))
    config_json = """
{
  "simulation": {
    "mode": "paper",
    "time_acceleration": 500,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "data_sources": ["/data/btc_usd.csv", "/data/eth_usd.csv"],
    "save_trade_history": true
  },
  "walk_forward_testing": {
    "enabled": true,
    "training_window_days": 90,
    "testing_window_days": 30,
    "num_windows": 6
  },
  "agents": [
    {
      "name": "Arbitrage Agent",
      "type": "strategy",
      "capital_allocation_percent": 25,
      "strategy": "mean_reversion",
      "risk_limits": {"max_position": 0.1, "stop_loss_percent": 5}
    },
    {
      "name": "Momentum Agent",
      "type": "strategy",
      "capital_allocation_percent": 25,
      "strategy": "trend_following",
      "risk_limits": {"max_position": 0.1, "stop_loss_percent": 5}
    },
    {
      "name": "Funding Rate Agent",
      "type": "strategy",
      "capital_allocation_percent": 25,
      "strategy": "volatility_breakout",
      "risk_limits": {"max_position": 0.1, "stop_loss_percent": 5}
    },
    {
      "name": "AI Research Lab",
      "type": "sandbox",
      "capital_allocation_percent": 25,
      "auto_generate_strategies": true,
      "backtest_historical": true,
      "deploy_top_strategies": true
    }
  ],
  "smart_contract": {
    "network": "Sepolia",
    "chain_id": 11155111,
    "contract_name": "AlphaAIManager"
  },
  "event_agents": [
    {
      "name": "Investor Monitor Agent",
      "type": "watcher",
      "events": ["InvestorDeposited", "InvestorWithdrawn"]
    },
    {
      "name": "Strategy Allocator Agent",
      "type": "execution",
      "events": ["InvestorDeposited"],
      "allocation_percent": 25
    },
    {
      "name": "Dashboard Updater Agent",
      "type": "analytics",
      "events": ["StrategyAllocated", "StrategyDeallocated"]
    }
  ],
  "risk_management": {
    "max_drawdown_percent": 5,
    "daily_loss_limit_percent": 3,
    "position_size_limit_percent": 15,
    "stop_loss_percent": 5
  },
  "reporting": {
    "formats": ["pdf", "json"],
    "frequency": "monthly",
    "save_location": "/reports/investor_reports/"
  }
}
    """
    story.append(Preformatted(config_json, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("8.3 Historical Data Format (CSV)", h2_style))
    csv_format = """
# CSV File Format for Historical Price Data
# Location: /app/backend/data/

# btc_usd.csv - Bitcoin price data
Time,Open,High,Low,Close,Volume
2025-01-01 00:00:00,42150.00,42380.50,41890.25,42250.75,15234567890
2025-01-02 00:00:00,42250.75,43100.00,42100.00,42980.50,16543210987
...

# eth_usd.csv - Ethereum price data
Time,Open,High,Low,Close,Volume
2025-01-01 00:00:00,2150.00,2180.50,2120.25,2165.75,8234567890
2025-01-02 00:00:00,2165.75,2210.00,2150.00,2195.50,8543210987
...

# Column Mapping for CSV Loader:
columns_mapping = {
    "timestamp": "Time",
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume"
}

# CSV Loader Function:
def load_csv_price_data(filepath: str) -> List[Dict]:
    data = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "timestamp": row.get("Time", ""),
                "open": float(row.get("Open", 0)),
                "high": float(row.get("High", 0)),
                "low": float(row.get("Low", 0)),
                "close": float(row.get("Close", 0)),
                "volume": float(row.get("Volume", 0))
            })
    return data
    """
    story.append(Preformatted(csv_format, code_style))
    story.append(PageBreak())
    
    # ============================================
    # PART 9: END-TO-END FLOW
    # ============================================
    story.append(Paragraph("PART 9: END-TO-END SYSTEM FLOW", h1_style))
    
    story.append(Paragraph("9.1 User Journey", h2_style))
    story.append(Paragraph("""
    Complete user flow from landing to active trading:
    
    1. LANDING PAGE
       - User arrives at homepage
       - Views fund statistics (NAV, AUM, Sharpe, Returns)
       - Sees live price ticker (BTC, ETH, SOL, etc.)
       - Clicks "Connect Wallet"
    
    2. WALLET CONNECTION
       - MetaMask popup appears
       - User approves connection
       - System checks network (prompts Sepolia switch if needed)
       - User's ETH balance displayed in nav
       - Backend registers user as investor
    
    3. DASHBOARD
       - Portfolio overview (balance, shares, P&L)
       - Live performance chart
       - Asset allocation pie chart
       - Recent trades list
       - AI market analysis (GPT-5.2)
    
    4. SIMULATION (Paper Trading)
       - User can run paper trading simulation
       - Control panel: Start/Stop/Run Cycle
       - View real-time logs and agent interactions
       - Run stress tests (BTC drop, ETH crash)
       - Export results to PDF/CSV
    
    5. RESEARCH
       - Run 500x accelerated backtests
       - Execute walk-forward validation
       - View performance metrics
       - Generate investor reports
    
    6. DEPOSIT (When contract deployed)
       - User enters deposit amount
       - MetaMask prompts transaction
       - Smart contract records deposit
       - Event agent updates balances
       - Strategy allocator distributes funds
    """, body_style))
    
    story.append(Paragraph("9.2 Data Flow Diagram", h2_style))
    data_flow = """
    USER ACTION                    SYSTEM RESPONSE
    ─────────────────────────────────────────────────────────────
    
    Connect Wallet ──────────────► MetaMask Popup
                                   │
                                   ▼
                              Web3Provider Setup
                                   │
                                   ▼
                              POST /api/investors/register
                                   │
                                   ▼
                              MongoDB: Create Investor Doc
                                   │
                                   ▼
                              Return Investor Data ──────► UI Update
    
    ─────────────────────────────────────────────────────────────
    
    Run Simulation ──────────────► POST /api/simulation/start
                                   │
                                   ▼
                              SimulationEngine.start()
                                   │
                                   ▼
                              For each trade cycle:
                                   │
                              ┌────┴────┐
                              │ Agent 1 │──► Execute Trade
                              │ Agent 2 │──► Execute Trade
                              │ Agent 3 │──► Execute Trade
                              │ Agent 4 │──► Execute Trade
                              └────┬────┘
                                   │
                                   ▼
                              Calculate P&L
                                   │
                                   ▼
                              Update MongoDB
                                   │
                                   ▼
                              Log Event
                                   │
                                   ▼
                              Return Results ──────────► UI Update
    
    ─────────────────────────────────────────────────────────────
    
    Contract Event ──────────────► EventListener (future: WebSocket)
    (InvestorDeposited)            │
                                   ▼
                              process_event()
                                   │
                              ┌────┴────┐
                              │ Watcher │──► Update Balances
                              │ Executor│──► Allocate to Strategy
                              │Analytics│──► Refresh Dashboard
                              └────┬────┘
                                   │
                                   ▼
                              MongoDB Updates
                                   │
                                   ▼
                              UI Refresh ──────────────► Dashboard
    """
    story.append(Preformatted(data_flow, code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("9.3 System Integration Points", h2_style))
    integrations = [
        ['Integration', 'Protocol', 'Purpose', 'Status'],
        ['MongoDB', 'TCP/27017', 'Data persistence', 'Active'],
        ['Kraken API', 'HTTPS/REST', 'Live prices', 'Active'],
        ['Sepolia RPC', 'HTTPS/JSON-RPC', 'Blockchain', 'Ready'],
        ['MetaMask', 'Injected Web3', 'Wallet', 'Active'],
        ['OpenAI', 'HTTPS/REST', 'AI analysis', 'Active'],
        ['Etherscan', 'HTTPS', 'Block explorer', 'Linked'],
    ]
    t = Table(integrations, colWidths=[1.3*inch, 1.2*inch, 1.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    story.append(t)
    
    # FINAL PAGE
    story.append(PageBreak())
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("END OF DOCUMENT", ParagraphStyle('End', fontSize=16, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("AlphaAI Fund Platform - Complete System Export", ParagraphStyle('End2', fontSize=10, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", ParagraphStyle('End3', fontSize=8, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("© 2026 Martin Maughan. All rights reserved.", ParagraphStyle('Copyright', fontSize=8, alignment=TA_CENTER, textColor=colors.gray)))
    
    # Build PDF
    doc.build(story)
    return output_path

if __name__ == "__main__":
    path = create_complete_export()
    print(f"Complete Export PDF generated: {path}")
    print(f"File size: {os.path.getsize(path) / 1024:.1f} KB")
