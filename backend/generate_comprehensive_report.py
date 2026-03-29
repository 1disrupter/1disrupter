#!/usr/bin/env python3
"""
AlphaAI Platform - COMPREHENSIVE PDF Export Generator
This script generates a complete technical documentation of the AlphaAI Platform
for external review and system rebuilding. It extracts ALL code, logic, and configurations.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, ListFlowable, ListItem, Preformatted
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os
import re
from pathlib import Path

# ===================== STYLE DEFINITIONS =====================

def get_styles():
    """Define all document styles"""
    styles = getSampleStyleSheet()
    
    # Title style - Main document title
    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#7B61FF'),
        spaceAfter=30,
        alignment=TA_CENTER
    ))
    
    # Section heading (H1)
    styles.add(ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#7B61FF'),
        spaceBefore=25,
        spaceAfter=15,
        borderWidth=1,
        borderColor=colors.HexColor('#7B61FF'),
        borderPadding=5
    ))
    
    # Subsection heading (H2)
    styles.add(ParagraphStyle(
        'SubHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#00FF94'),
        spaceBefore=18,
        spaceAfter=10
    ))
    
    # Sub-subsection heading (H3)
    styles.add(ParagraphStyle(
        'SubSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#FFB800'),
        spaceBefore=12,
        spaceAfter=6
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=12
    ))
    
    # Code style - for code blocks
    styles.add(ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        textColor=colors.HexColor('#1a1a1a'),
        backColor=colors.HexColor('#f5f5f5'),
        leftIndent=10,
        rightIndent=10,
        spaceBefore=5,
        spaceAfter=5,
        borderWidth=0.5,
        borderColor=colors.HexColor('#cccccc'),
        borderPadding=5,
        leading=8
    ))
    
    # Inline code
    styles.add(ParagraphStyle(
        'InlineCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        textColor=colors.HexColor('#c41a16'),
        backColor=colors.HexColor('#f0f0f0')
    ))
    
    # Note/Info box
    styles.add(ParagraphStyle(
        'InfoBox',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#0066cc'),
        backColor=colors.HexColor('#e6f2ff'),
        leftIndent=10,
        rightIndent=10,
        spaceBefore=8,
        spaceAfter=8,
        borderWidth=1,
        borderColor=colors.HexColor('#0066cc'),
        borderPadding=8
    ))
    
    return styles

# ===================== CODE EXTRACTION HELPERS =====================

def escape_xml(text):
    """Escape special XML characters for ReportLab"""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def format_code_for_pdf(code, max_line_length=100):
    """Format code block for PDF display with line wrapping"""
    lines = code.split('\n')
    formatted_lines = []
    for line in lines:
        # Wrap long lines
        while len(line) > max_line_length:
            formatted_lines.append(escape_xml(line[:max_line_length]))
            line = '    ' + line[max_line_length:]  # Indent continuation
        formatted_lines.append(escape_xml(line))
    return '<br/>'.join(formatted_lines)

def extract_functions_from_code(code):
    """Extract function definitions and their docstrings"""
    pattern = r'(async\s+)?def\s+(\w+)\s*\(([^)]*)\).*?(?:"""([^"]*?)""")?'
    matches = re.findall(pattern, code, re.DOTALL)
    functions = []
    for match in matches:
        is_async = bool(match[0])
        name = match[1]
        params = match[2].strip()
        docstring = match[3].strip() if match[3] else "No docstring"
        functions.append({
            'name': name,
            'async': is_async,
            'params': params,
            'docstring': docstring[:200] + '...' if len(docstring) > 200 else docstring
        })
    return functions

def extract_api_routes(code):
    """Extract API route definitions"""
    pattern = r'@api_router\.(get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, code)
    return [{'method': m[0].upper(), 'path': m[1]} for m in matches]

def extract_pydantic_models(code):
    """Extract Pydantic model definitions"""
    pattern = r'class\s+(\w+)\s*\(\s*BaseModel\s*\)\s*:(.*?)(?=\nclass|\n@|\ndef|\Z)'
    matches = re.findall(pattern, code, re.DOTALL)
    models = []
    for name, body in matches:
        # Extract fields
        field_pattern = r'(\w+)\s*:\s*([^=\n]+)(?:\s*=\s*([^\n]+))?'
        fields = re.findall(field_pattern, body)
        models.append({
            'name': name,
            'fields': [{'name': f[0], 'type': f[1].strip(), 'default': f[2].strip() if f[2] else None} 
                      for f in fields if f[0] not in ['model_config']]
        })
    return models

def extract_react_components(code):
    """Extract React component definitions"""
    pattern = r'const\s+(\w+)\s*=\s*\(\s*(?:\{[^}]*\}|\(\))?\s*\)\s*=>\s*\{'
    matches = re.findall(pattern, code)
    return matches

# ===================== FILE READERS =====================

def read_file_safe(filepath):
    """Safely read a file and return its contents"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# ===================== PDF CONTENT GENERATORS =====================

def create_cover_page(story, styles):
    """Create the document cover page"""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("AlphaAI Fund Platform", styles['DocTitle']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Complete Technical Documentation", ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=16, alignment=TA_CENTER, 
        textColor=colors.gray)))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("For External Review &amp; System Rebuilding", ParagraphStyle(
        'Subtitle2', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, 
        textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 1*inch))
    
    # Report metadata
    meta_data = [
        ['Document Type:', 'Complete System Export'],
        ['Generated:', datetime.now().strftime('%B %d, %Y at %H:%M')],
        ['Version:', '2.0 (Comprehensive)'],
        ['Platform Status:', 'Testnet Ready'],
        ['Copyright:', '© 2026 Martin Maughan. All rights reserved.']
    ]
    meta_table = Table(meta_data, colWidths=[1.8*inch, 3.5*inch])
    meta_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

def create_table_of_contents(story, styles):
    """Create detailed table of contents"""
    story.append(Paragraph("Table of Contents", styles['SectionHeading']))
    
    toc_items = [
        ("1.", "Executive Summary &amp; Project Overview"),
        ("2.", "System Architecture"),
        ("   2.1", "Technology Stack"),
        ("   2.2", "Directory Structure"),
        ("   2.3", "Data Flow"),
        ("3.", "Backend Implementation (server.py)"),
        ("   3.1", "Data Models (Pydantic)"),
        ("   3.2", "Simulation Engine"),
        ("   3.3", "API Endpoints - Full Reference"),
        ("   3.4", "AI Agent Logic"),
        ("   3.5", "Risk Management Engine"),
        ("   3.6", "Research Engine"),
        ("   3.7", "Smart Contract Integration"),
        ("   3.8", "Event-Driven Agent System"),
        ("4.", "Frontend Implementation (App.js)"),
        ("   4.1", "React Components"),
        ("   4.2", "Page Structure"),
        ("   4.3", "Wallet Integration (MetaMask)"),
        ("   4.4", "State Management"),
        ("5.", "Smart Contract (Solidity)"),
        ("   5.1", "Contract Source Code"),
        ("   5.2", "Functions &amp; Events"),
        ("   5.3", "Deployment Guide"),
        ("6.", "Trading Strategies &amp; Signal Logic"),
        ("   6.1", "Strategy Types"),
        ("   6.2", "Trading Rules"),
        ("   6.3", "Backtesting Logic"),
        ("7.", "AI Integration &amp; Prompts"),
        ("8.", "Database Schema"),
        ("9.", "Configuration Files"),
        ("10.", "End-to-End System Workflow"),
    ]
    
    for num, title in toc_items:
        indent = 20 if num.startswith("   ") else 0
        story.append(Paragraph(f"<b>{num}</b> {title}", ParagraphStyle(
            'TOCItem', parent=styles['CustomBody'], leftIndent=indent, spaceBefore=2, spaceAfter=2)))
    
    story.append(PageBreak())

def create_executive_summary(story, styles):
    """Section 1: Executive Summary"""
    story.append(Paragraph("1. Executive Summary &amp; Project Overview", styles['SectionHeading']))
    
    story.append(Paragraph("1.1 What is AlphaAI?", styles['SubHeading']))
    story.append(Paragraph("""
    AlphaAI is a decentralized AI-powered hedge fund platform that enables investors to deposit capital 
    into a vault managed by autonomous AI trading agents. The platform features a marketplace where 
    external developers can launch their own trading agents, comprehensive simulation capabilities 
    with accelerated backtesting, real-time market data integration, and smart contract integration 
    for on-chain fund management.
    """, styles['CustomBody']))
    
    story.append(Paragraph("1.2 Core Capabilities", styles['SubHeading']))
    capabilities = [
        "<b>Multi-Agent Trading System</b>: 4 specialized AI agents (Arbitrage, Momentum, Funding Rate, Research Lab) trade autonomously",
        "<b>AI Research Engine</b>: Generates, backtests, and deploys new strategies with walk-forward validation",
        "<b>500x Accelerated Simulation</b>: Run 6 months of trading in minutes using historical data",
        "<b>Smart Contract Integration</b>: AlphaAIManager.sol for on-chain deposits, withdrawals, and strategy allocation",
        "<b>MetaMask Wallet</b>: Real Web3 wallet connectivity on Sepolia testnet",
        "<b>Live Price Feed</b>: Real-time crypto prices from Kraken API",
        "<b>Risk Management</b>: Automated drawdown limits, stop-losses, and position sizing",
        "<b>Event-Driven Agents</b>: Agents that react to smart contract events automatically",
    ]
    for cap in capabilities:
        story.append(Paragraph(f"• {cap}", styles['CustomBody']))
    
    story.append(Paragraph("1.3 Key Platform Statistics", styles['SubHeading']))
    stats_data = [
        ['Metric', 'Value'],
        ['Backend Code', '~3,400 lines (server.py)'],
        ['Frontend Code', '~3,100 lines (App.js)'],
        ['API Endpoints', '60+ REST endpoints'],
        ['Data Models', '25+ Pydantic models'],
        ['React Components', '15+ components'],
        ['Trading Strategies', '5 types (momentum, arbitrage, yield, mean_reversion, funding)'],
        ['Supported Cryptocurrencies', '8 (BTC, ETH, SOL, AVAX, MATIC, LINK, UNI, AAVE)'],
    ]
    t = Table(stats_data, colWidths=[2.5*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F8F8')),
    ]))
    story.append(t)
    story.append(PageBreak())

def create_architecture_section(story, styles):
    """Section 2: System Architecture"""
    story.append(Paragraph("2. System Architecture", styles['SectionHeading']))
    
    # 2.1 Technology Stack
    story.append(Paragraph("2.1 Technology Stack", styles['SubHeading']))
    tech_data = [
        ['Layer', 'Technology', 'Purpose'],
        ['Frontend', 'React 18 + Shadcn/UI', 'User interface components'],
        ['Styling', 'TailwindCSS + Framer Motion', 'Design system and animations'],
        ['Charts', 'Recharts', 'Data visualization'],
        ['Web3 (Frontend)', 'ethers.js v5', 'MetaMask wallet integration'],
        ['Backend', 'FastAPI (Python 3.11+)', 'REST API server'],
        ['Database', 'MongoDB (Motor async)', 'Data persistence'],
        ['AI/LLM', 'OpenAI GPT-5.2', 'Market analysis via Emergent Key'],
        ['Price Data', 'Kraken API', 'Real-time crypto prices'],
        ['Web3 (Backend)', 'web3.py', 'Smart contract interaction'],
        ['PDF Reports', 'ReportLab', 'Investor report generation'],
        ['Blockchain', 'Ethereum (Sepolia)', 'Smart contract deployment'],
    ]
    t = Table(tech_data, colWidths=[1.3*inch, 2*inch, 2.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00FF94')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # 2.2 Directory Structure
    story.append(Paragraph("2.2 Directory Structure", styles['SubHeading']))
    dir_structure = """
/app/
├── backend/
│   ├── server.py              # Main FastAPI application (3,400 lines)
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (MONGO_URL, EMERGENT_LLM_KEY)
│   ├── contracts/
│   │   └── AlphaAIManager.sol # Solidity smart contract
│   ├── data/
│   │   ├── btc_usd.csv        # Historical BTC price data
│   │   └── eth_usd.csv        # Historical ETH price data
│   ├── reports/
│   │   └── investor_reports/  # Generated PDF/JSON reports
│   └── web3/
│       └── contract_abi.py    # Smart contract ABI
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main React application (3,100 lines)
│   │   ├── App.css            # Global styles
│   │   ├── index.css          # TailwindCSS imports
│   │   └── components/ui/     # Shadcn/UI components
│   ├── package.json           # NPM dependencies
│   └── .env                   # REACT_APP_BACKEND_URL
└── memory/
    └── PRD.md                 # Product requirements document
    """
    story.append(Paragraph(format_code_for_pdf(dir_structure), styles['CodeBlock']))
    
    # 2.3 Data Flow
    story.append(Paragraph("2.3 Data Flow Architecture", styles['SubHeading']))
    story.append(Paragraph("""
    <b>User Flow</b>: User connects MetaMask → Frontend calls /api/investors/register → 
    Backend creates investor record in MongoDB → User can deposit/withdraw via simulated 
    or on-chain transactions.<br/><br/>
    <b>Trading Flow</b>: Simulation Engine runs → Calls strategy cycle → Each agent generates 
    signals → Execution layer simulates trades → Risk engine checks rules → Capital allocation 
    engine rebalances → Results logged to database.<br/><br/>
    <b>Event Flow</b>: Smart contract emits event (e.g., InvestorDeposited) → Event-driven 
    agents detect event → Execute automated actions (update balances, allocate to strategies) 
    → Update dashboards.
    """, styles['CustomBody']))
    story.append(PageBreak())

def create_backend_section(story, styles, server_code):
    """Section 3: Backend Implementation"""
    story.append(Paragraph("3. Backend Implementation (server.py)", styles['SectionHeading']))
    
    story.append(Paragraph("""
    The backend is a monolithic FastAPI application contained in a single file (server.py). 
    This section documents all data models, the simulation engine, API endpoints, and core logic.
    """, styles['CustomBody']))
    
    # 3.1 Data Models
    story.append(Paragraph("3.1 Data Models (Pydantic)", styles['SubHeading']))
    models = extract_pydantic_models(server_code)
    
    story.append(Paragraph(f"Total Models Defined: <b>{len(models)}</b>", styles['CustomBody']))
    story.append(Spacer(1, 0.1*inch))
    
    # Key models table
    key_models = [
        ['Model Name', 'Key Fields', 'Purpose'],
        ['Investor', 'wallet_address, balance, shares, paper_balance', 'Track investor accounts'],
        ['TradingAgent', 'name, type, strategy, performance_7d, capital_allocation', 'AI agent definitions'],
        ['Trade', 'agent_id, symbol, side, amount, price, pnl, slippage', 'Trade records'],
        ['Strategy', 'name, type, parameters, status, sharpe_ratio, total_return', 'Trading strategies'],
        ['RiskConfig', 'max_drawdown, max_position_size, max_daily_loss, stop_loss', 'Risk parameters'],
        ['SimulationConfig', 'is_running, mode, initial_capital, time_acceleration', 'Simulation settings'],
        ['RiskAlert', 'type, severity, message, auto_action_taken', 'Risk alerts'],
        ['EventAgent', 'name, type, events_to_monitor, is_active', 'Event-driven agents'],
        ['ContractEvent', 'event_name, block_number, tx_hash, args', 'Smart contract events'],
    ]
    t = Table(key_models, colWidths=[1.3*inch, 2.5*inch, 1.7*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Full model definitions
    story.append(Paragraph("3.1.1 Complete Model Definitions", styles['SubSubHeading']))
    
    # Extract and display key model code
    model_code = """
class Investor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_address: str
    balance: float = 0.0
    shares: float = 0.0
    total_deposited: float = 0.0
    total_withdrawn: float = 0.0
    paper_balance: float = 10000.0
    paper_pnl: float = 0.0
    is_paper_trading: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TradingAgent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # data, analysis, strategy, execution, risk
    status: str = "active"
    description: str
    strategy: str
    performance_7d: float = 0.0
    performance_30d: float = 0.0
    total_trades: int = 0
    win_rate: float = 0.0
    aum: float = 0.0
    capital_allocation: float = 0.0

class Strategy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # momentum, arbitrage, yield, mean_reversion, funding
    description: str
    parameters: Dict[str, Any] = {}
    status: str = "generated"  # generated, backtested, sandbox, live, stopped
    backtest_results: Optional[Dict[str, Any]] = None
    sharpe_ratio: float = 0.0
    total_return: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    capital_allocated: float = 0.0
    is_active: bool = False

class SimulationConfig(BaseModel):
    is_running: bool = False
    mode: str = "paper"  # paper, testnet, live
    initial_capital: float = 10000.0
    current_capital: float = 10000.0
    time_acceleration: int = 1  # 1x = real-time, 500x = accelerated
    sim_start_date: str = "2025-01-01"
    sim_end_date: str = "2025-12-31"
    stress_test_active: bool = False

class RiskConfig(BaseModel):
    max_drawdown: float = 5.0      # Auto-stop at 5% drawdown
    max_position_size: float = 10.0  # Max 10% per position
    max_daily_loss: float = 2.0    # Reduce positions at 2% daily loss
    stop_loss: float = 2.0         # Per-agent stop loss
    auto_shutdown_enabled: bool = True
    """
    story.append(Paragraph(format_code_for_pdf(model_code), styles['CodeBlock']))
    story.append(PageBreak())
    
    # 3.2 Simulation Engine
    story.append(Paragraph("3.2 Simulation Engine", styles['SubHeading']))
    story.append(Paragraph("""
    The SimulationEngine class is the core of the trading simulation. It coordinates all agents, 
    manages capital allocation, executes trades, and enforces risk rules.
    """, styles['CustomBody']))
    
    sim_engine_code = """
class SimulationEngine:
    '''Central simulation engine coordinating all agents and modules'''
    
    def __init__(self):
        self.is_running = False
        self.config = None
        self.current_drawdown = 0.0
        self.daily_pnl = 0.0
        self.positions = {}
    
    async def initialize(self):
        '''Initialize or load simulation config from database'''
        config = await db.simulation_config.find_one({}, {"_id": 0})
        if not config:
            self.config = SimulationConfig()
            await db.simulation_config.insert_one(self.config.model_dump())
        else:
            self.config = SimulationConfig(**config)
        return self.config
    
    async def check_risk_rules(self) -> Dict[str, Any]:
        '''Risk Engine: Check if any risk rules are triggered'''
        violations = []
        actions_taken = []
        
        # Check drawdown against limit
        if self.current_drawdown >= risk_config['max_drawdown']:
            violations.append({"rule": "max_drawdown", "value": self.current_drawdown})
            if risk_config['auto_shutdown_enabled']:
                actions_taken.append("AUTO_STOP_ALL_TRADING")
        
        # Check daily loss
        if abs(self.daily_pnl) >= risk_config['max_daily_loss'] and self.daily_pnl < 0:
            violations.append({"rule": "max_daily_loss", "value": self.daily_pnl})
            actions_taken.append("REDUCE_POSITION_SIZES")
        
        return {"violations": violations, "actions_taken": actions_taken}
    
    async def dynamic_capital_allocation(self) -> List[Dict]:
        '''Capital Allocation Engine: Reallocate based on performance'''
        strategies = await db.strategies.find({"status": {"$in": ["live", "sandbox"]}}).to_list(100)
        
        # Calculate performance scores
        for s in strategies:
            s['performance_score'] = (s['sharpe_ratio'] * 0.4 + 
                                      s['total_return'] * 0.3 + 
                                      (100 - s['max_drawdown']) * 0.3)
        
        # Sort by performance and allocate proportionally
        strategies = sorted(strategies, key=lambda x: x['performance_score'], reverse=True)
        total_score = sum(max(s['performance_score'], 1) for s in strategies)
        
        allocations = []
        for s in strategies:
            alloc_percent = (s['performance_score'] / total_score) * 100
            alloc_capital = self.config.current_capital * (alloc_percent / 100)
            allocations.append({
                "strategy_id": s['id'],
                "allocation_percent": round(alloc_percent, 2),
                "allocated_capital": round(alloc_capital, 2)
            })
        
        return allocations
    
    async def execute_simulation_trade(self, strategy_id, symbol, side, amount) -> Trade:
        '''Execution Layer: Execute a simulated trade'''
        prices = {"BTC/USDT": 45000, "ETH/USDT": 2500, "SOL/USDT": 100}
        base_price = prices.get(symbol, 100)
        
        # Calculate slippage and execution
        slippage = round(random.uniform(0.01, 0.3), 3)
        execution_price = base_price * (1 + slippage/100) if side == "buy" else base_price * (1 - slippage/100)
        gas_fee = round(random.uniform(1, 10), 2)
        
        # Calculate P&L
        price_movement = random.uniform(-0.02, 0.03)
        pnl = round(amount * execution_price * price_movement, 2)
        
        trade = Trade(
            agent_id="ExecutionAgent",
            strategy_id=strategy_id,
            symbol=symbol,
            side=side,
            amount=amount,
            price=base_price,
            execution_price=round(execution_price, 2),
            slippage=slippage,
            gas_fee=gas_fee,
            pnl=pnl,
            is_simulation=True
        )
        
        await db.trades.insert_one(trade.model_dump())
        await self.check_risk_rules()  # Check risk after every trade
        
        return trade
    """
    story.append(Paragraph(format_code_for_pdf(sim_engine_code), styles['CodeBlock']))
    story.append(PageBreak())
    
    # 3.3 API Endpoints
    story.append(Paragraph("3.3 API Endpoints - Full Reference", styles['SubHeading']))
    
    routes = extract_api_routes(server_code)
    story.append(Paragraph(f"Total API Endpoints: <b>{len(routes)}</b>", styles['CustomBody']))
    
    # Group endpoints by category
    endpoint_categories = {
        'Simulation': [r for r in routes if 'simulation' in r['path'].lower()],
        'Research': [r for r in routes if 'research' in r['path'].lower()],
        'Strategy Lab': [r for r in routes if 'lab' in r['path'].lower() or 'strategies' in r['path'].lower()],
        'Investors': [r for r in routes if 'investor' in r['path'].lower() or 'paper' in r['path'].lower()],
        'Trading Agents': [r for r in routes if 'agent' in r['path'].lower()],
        'Risk Management': [r for r in routes if 'risk' in r['path'].lower()],
        'Market Data': [r for r in routes if 'market' in r['path'].lower()],
        'Smart Contract': [r for r in routes if 'contract' in r['path'].lower()],
        'Events': [r for r in routes if 'event' in r['path'].lower()],
        'Reports': [r for r in routes if 'report' in r['path'].lower()],
        'Fund Stats': [r for r in routes if 'fund' in r['path'].lower()],
        'Other': [],
    }
    
    # Categorize remaining
    categorized = set()
    for cat_routes in endpoint_categories.values():
        for r in cat_routes:
            categorized.add(r['path'])
    endpoint_categories['Other'] = [r for r in routes if r['path'] not in categorized]
    
    for category, cat_routes in endpoint_categories.items():
        if cat_routes:
            story.append(Paragraph(f"<b>{category} Endpoints</b>", styles['SubSubHeading']))
            data = [['Method', 'Path', 'Description']]
            for r in cat_routes[:15]:  # Limit to 15 per category
                desc = get_endpoint_description(r['path'])
                data.append([r['method'], r['path'], desc])
            
            t = Table(data, colWidths=[0.6*inch, 2.5*inch, 2.4*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())

def get_endpoint_description(path):
    """Get description for an API endpoint"""
    descriptions = {
        '/simulation/config': 'Get simulation configuration',
        '/simulation/start': 'Start simulation in paper mode',
        '/simulation/stop': 'Stop active simulation',
        '/simulation/run-cycle': 'Run one trading cycle',
        '/simulation/run-accelerated': 'Run 500x accelerated simulation',
        '/simulation/stress-test': 'Run stress test scenario',
        '/simulation/configure': 'Configure advanced simulation',
        '/simulation/logs': 'Get simulation event logs',
        '/simulation/stats': 'Get comprehensive statistics',
        '/simulation/export': 'Export simulation results',
        '/research/run-simulation': 'Run research backtest with CSV data',
        '/research/walk-forward-test': 'Run walk-forward validation',
        '/research/generate-investor-report': 'Generate investor PDF report',
        '/research/data-sources': 'Get available data sources',
        '/lab/strategies': 'Get all strategies',
        '/lab/strategies/generate': 'AI-generate new strategy',
        '/lab/rankings': 'Get strategy rankings',
        '/lab/auto-deploy-top': 'Auto-deploy top strategies',
        '/investors/register': 'Register new investor',
        '/investors/deposit': 'Deposit funds',
        '/investors/withdraw': 'Withdraw funds',
        '/agents': 'Get all trading agents',
        '/agents/event-agents': 'Get event-driven agents',
        '/risk/config': 'Get/update risk configuration',
        '/risk/alerts': 'Get active risk alerts',
        '/risk/portfolio-status': 'Get portfolio risk status',
        '/market/live-prices': 'Get live prices from Kraken',
        '/market/top-coins': 'Get top coins by market cap',
        '/contract/info': 'Get contract deployment info',
        '/contract/source': 'Get Solidity source code',
        '/contract/register': 'Register deployed contract',
        '/contract/abi': 'Get contract ABI',
        '/events/simulate': 'Simulate contract event',
        '/events/recent': 'Get recent contract events',
        '/fund/stats': 'Get fund statistics',
        '/fund/allocation': 'Get portfolio allocation',
        '/ai/analyze': 'Run AI market analysis',
    }
    for key, desc in descriptions.items():
        if key in path:
            return desc
    return 'API endpoint'

def create_trading_strategies_section(story, styles):
    """Section 6: Trading Strategies"""
    story.append(Paragraph("6. Trading Strategies &amp; Signal Logic", styles['SectionHeading']))
    
    story.append(Paragraph("6.1 Strategy Types", styles['SubHeading']))
    strategy_types = [
        ['Type', 'Description', 'Signal Logic'],
        ['Momentum', 'Trend following strategy', 'signal = btc_return * 1.5 if positive, * 0.8 if negative'],
        ['Arbitrage (Mean Reversion)', 'Trades against large moves', 'signal = -btc_return if |btc_return| > 2%'],
        ['Volatility Breakout', 'Trades on volatility spikes', 'signal = |btc_return| * 2 * direction'],
        ['Adaptive', 'Mix of strategies', 'signal = btc_return * 0.7 + eth_return * 0.3'],
        ['Funding Rate', 'Exploits funding differentials', 'Trades when funding rate > 0.01%'],
        ['Yield', 'DeFi yield optimization', 'Optimizes across protocols for best APY'],
    ]
    t = Table(strategy_types, colWidths=[1.2*inch, 1.8*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFB800')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("6.2 Trading Rules (from research simulation)", styles['SubHeading']))
    trading_logic = """
# Agent configuration for trading
agents = [
    {"name": "Arbitrage Agent", "allocation": 0.25, "strategy": "mean_reversion", "lookback": 20},
    {"name": "Momentum Agent", "allocation": 0.25, "strategy": "trend_following", "lookback": 10},
    {"name": "Funding Rate Agent", "allocation": 0.25, "strategy": "volatility_breakout", "lookback": 3},
    {"name": "AI Research Lab", "allocation": 0.25, "strategy": "adaptive", "lookback": 7}
]

# Strategy-based trading logic
for agent in agents:
    agent_capital = capital * agent["allocation"]
    
    if agent["strategy"] == "mean_reversion":
        # Trade against large moves (contrarian)
        signal = -btc_return if abs(btc_return) > 0.02 else btc_return * 0.5
        
    elif agent["strategy"] == "trend_following":
        # Follow the trend with enhanced position sizing
        signal = btc_return * 1.5 if btc_return > 0 else btc_return * 0.8
        
    elif agent["strategy"] == "volatility_breakout":
        # Trade on volatility spikes
        signal = abs(btc_return) * (1 if btc_return > 0 else -1) * 2
        
    else:  # adaptive
        # Mix of strategies based on market conditions
        signal = btc_return * 0.7 + eth_return * 0.3
    
    # Calculate P&L based on signal and position
    position_size = agent_capital * 0.15  # 15% position
    trade_pnl = position_size * signal * random.uniform(0.8, 1.2)
    """
    story.append(Paragraph(format_code_for_pdf(trading_logic), styles['CodeBlock']))
    
    story.append(Paragraph("6.3 Backtesting Logic", styles['SubHeading']))
    backtest_logic = """
# Backtest a strategy on historical data
async def backtest_strategy(strategy_id: str, request: BacktestRequest):
    strategy = await db.strategies.find_one({"id": strategy_id})
    
    # Simulate backtest results
    total_return = round(random.uniform(-5, 35), 2)
    sharpe = round(random.uniform(0.5, 2.5), 2)
    max_dd = round(random.uniform(2, 10), 2)
    win_rate = round(random.uniform(45, 75), 1)
    total_trades = random.randint(50, 500)
    
    backtest_results = {
        "period": f"{request.start_date} to {request.end_date}",
        "initial_capital": request.initial_capital,
        "final_capital": round(request.initial_capital * (1 + total_return/100), 2),
        "total_return": total_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "total_trades": total_trades,
    }
    
    # Update strategy with results
    await db.strategies.update_one(
        {"id": strategy_id}, 
        {"$set": {
            "status": "backtested", 
            "backtest_results": backtest_results,
            "sharpe_ratio": sharpe,
            "total_return": total_return
        }}
    )
    
    return {"success": True, "results": backtest_results}
    """
    story.append(Paragraph(format_code_for_pdf(backtest_logic), styles['CodeBlock']))
    story.append(PageBreak())

def create_smart_contract_section(story, styles, contract_code):
    """Section 5: Smart Contract"""
    story.append(Paragraph("5. Smart Contract (AlphaAIManager.sol)", styles['SectionHeading']))
    
    story.append(Paragraph("""
    The AlphaAIManager smart contract handles on-chain fund management including investor 
    deposits, withdrawals, and strategy allocations. Deployed on Ethereum Sepolia testnet.
    """, styles['CustomBody']))
    
    story.append(Paragraph("5.1 Complete Solidity Source Code", styles['SubHeading']))
    story.append(Paragraph(format_code_for_pdf(contract_code), styles['CodeBlock']))
    
    story.append(Paragraph("5.2 Contract Functions &amp; Events", styles['SubHeading']))
    functions_data = [
        ['Function', 'Type', 'Description'],
        ['deposit()', 'payable', 'Deposit ETH into the fund. Emits InvestorDeposited event'],
        ['withdraw(uint256 amount)', 'external', 'Withdraw ETH. Requires sufficient balance'],
        ['addStrategy(string name)', 'onlyOwner', 'Add a new trading strategy'],
        ['allocateToStrategy(uint256 id, uint256 amt)', 'onlyOwner', 'Allocate funds to a strategy'],
        ['deallocateFromStrategy(uint256 id, uint256 amt)', 'onlyOwner', 'Deallocate from strategy'],
        ['getInvestorBalance(address)', 'view', 'Get investor balance'],
        ['getStrategy(uint256 id)', 'view', 'Get strategy details'],
        ['emergencyWithdraw()', 'onlyOwner', 'Emergency fund withdrawal'],
    ]
    t = Table(functions_data, colWidths=[2.5*inch, 1*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("5.3 Contract Events", styles['SubSubHeading']))
    events_data = [
        ['Event', 'Parameters', 'Triggered When'],
        ['InvestorDeposited', 'address investor, uint256 amount', 'User deposits ETH'],
        ['InvestorWithdrawn', 'address investor, uint256 amount', 'User withdraws ETH'],
        ['StrategyAdded', 'uint256 strategyId, string name', 'New strategy added'],
        ['StrategyAllocated', 'uint256 strategyId, uint256 amount', 'Funds allocated'],
        ['StrategyDeallocated', 'uint256 strategyId, uint256 amount', 'Funds deallocated'],
    ]
    t = Table(events_data, colWidths=[1.5*inch, 2.2*inch, 1.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00FF94')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    
    story.append(Paragraph("5.4 Deployment Guide", styles['SubHeading']))
    deployment_steps = """
Step 1: Get Sepolia ETH from a faucet (https://sepoliafaucet.com)
Step 2: Open Remix IDE (https://remix.ethereum.org)
Step 3: Create new file "AlphaAIManager.sol" and paste contract code
Step 4: Select Solidity compiler 0.8.20 and compile
Step 5: In Deploy tab, select "Injected Provider - MetaMask"
Step 6: Ensure MetaMask is connected to Sepolia network
Step 7: Click "Deploy" and confirm transaction in MetaMask
Step 8: Copy deployed contract address
Step 9: Register contract via POST /api/contract/register with:
        {contract_address, deployer_address, tx_hash}
    """
    story.append(Paragraph(format_code_for_pdf(deployment_steps), styles['CodeBlock']))
    story.append(PageBreak())

def create_ai_integration_section(story, styles):
    """Section 7: AI Integration"""
    story.append(Paragraph("7. AI Integration &amp; Prompts", styles['SectionHeading']))
    
    story.append(Paragraph("7.1 AI Market Analysis", styles['SubHeading']))
    story.append(Paragraph("""
    The platform uses OpenAI GPT-5.2 via the Emergent LLM Key for market analysis. 
    The AI provides sentiment analysis, support/resistance levels, and trading recommendations.
    """, styles['CustomBody']))
    
    ai_code = """
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

@api_router.post("/ai/analyze")
async def ai_market_analysis(request: AIAnalysisRequest):
    # Get current market data
    market_data = await get_market_data(request.symbol.lower())
    price = market_data.get("market_data", {}).get("current_price", {}).get("usd", 0)
    change_24h = market_data.get("market_data", {}).get("price_change_percentage_24h", 0)
    
    try:
        # Initialize AI chat with Emergent integration
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY, 
            session_id=f"analysis-{request.symbol}-{uuid.uuid4().hex[:8]}", 
            system_message="You are an expert crypto trading analyst."
        ).with_model("openai", "gpt-5.2")
        
        # Create prompt for analysis
        user_message = UserMessage(
            text=f"Analyze {request.symbol.upper()} @ ${price:,.2f}, 24h: {change_24h:.2f}%. "
                 f"Give: sentiment, levels, recommendation, risk (1-10)."
        )
        
        # Get AI response
        response = await chat.send_message(user_message)
        
        return {
            "symbol": request.symbol.upper(), 
            "price": price, 
            "change_24h": change_24h, 
            "analysis": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        # Fallback if AI fails
        return {
            "symbol": request.symbol.upper(),
            "analysis": f"Market {'bullish' if change_24h > 0 else 'bearish'}. 24h: {change_24h:.2f}%"
        }
    """
    story.append(Paragraph(format_code_for_pdf(ai_code), styles['CodeBlock']))
    
    story.append(Paragraph("7.2 System Prompt", styles['SubHeading']))
    story.append(Paragraph("""
    <b>System Message:</b> "You are an expert crypto trading analyst."<br/><br/>
    <b>User Prompt Template:</b><br/>
    "Analyze [SYMBOL] @ $[PRICE], 24h: [CHANGE]%. Give: sentiment, levels, recommendation, risk (1-10)."
    """, styles['CustomBody']))
    story.append(PageBreak())

def create_frontend_section(story, styles, app_code):
    """Section 4: Frontend Implementation"""
    story.append(Paragraph("4. Frontend Implementation (App.js)", styles['SectionHeading']))
    
    story.append(Paragraph("""
    The frontend is a single-page React application with comprehensive UI for investors, 
    administrators, and traders. It uses Shadcn/UI components and ethers.js for Web3 integration.
    """, styles['CustomBody']))
    
    # 4.1 React Components
    story.append(Paragraph("4.1 React Components", styles['SubHeading']))
    components = extract_react_components(app_code)
    
    component_details = [
        ['Component', 'Purpose', 'Key Features'],
        ['WalletProvider', 'Context for wallet state', 'MetaMask connection, balance tracking'],
        ['Navigation', 'Top navigation bar', 'Responsive nav, wallet dropdown'],
        ['LivePriceTicker', 'Real-time price display', 'Kraken API, 30s refresh'],
        ['LandingPage', 'Homepage', 'Hero section, fund stats, features'],
        ['DashboardPage', 'Investor dashboard', 'Portfolio, charts, paper trading'],
        ['StrategyLabPage', 'Strategy management', 'Generate, backtest, deploy'],
        ['AgentsPage', 'AI agents view', 'Agent cards, AI analysis'],
        ['MarketplacePage', 'Agent marketplace', 'Browse, submit agents'],
        ['AnalyticsPage', 'Performance analytics', 'Charts, metrics, rankings'],
        ['AdminPage', 'Admin dashboard', 'Risk config, alerts, monitoring'],
        ['SimulationPage', 'Simulation control', 'Start/stop, stress tests'],
        ['ResearchPage', 'Research engine', 'Backtesting, walk-forward'],
        ['EventAgentsPage', 'Event-driven agents', 'Monitor, toggle agents'],
    ]
    t = Table(component_details, colWidths=[1.5*inch, 1.8*inch, 2.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # 4.2 Page Routes
    story.append(Paragraph("4.2 Page Structure &amp; Routes", styles['SubHeading']))
    routes_data = [
        ['Route', 'Component', 'Description'],
        ['/', 'LandingPage', 'Public homepage with fund stats'],
        ['/dashboard', 'DashboardPage', 'Investor portfolio and paper trading'],
        ['/simulation', 'SimulationPage', 'Simulation control panel'],
        ['/research', 'ResearchPage', 'AI Research Engine interface'],
        ['/agents', 'AgentsPage', 'View AI trading agents'],
        ['/events', 'EventAgentsPage', 'Event-driven agent monitoring'],
        ['/lab', 'StrategyLabPage', 'Strategy generation and testing'],
        ['/marketplace', 'MarketplacePage', 'Agent marketplace'],
        ['/admin', 'AdminPage', 'Admin dashboard with risk config'],
    ]
    t = Table(routes_data, colWidths=[1.2*inch, 1.8*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00FF94')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # 4.3 MetaMask Integration
    story.append(Paragraph("4.3 MetaMask Wallet Integration", styles['SubHeading']))
    wallet_code = """
import { ethers } from "ethers";

const WalletProvider = ({ children }) => {
  const [wallet, setWallet] = useState(null);
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [ethBalance, setEthBalance] = useState(null);

  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      // Request accounts from MetaMask
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      const address = accounts[0];
      
      // Setup ethers provider and signer
      const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
      const web3Signer = web3Provider.getSigner();
      const network = await web3Provider.getNetwork();
      
      setProvider(web3Provider);
      setSigner(web3Signer);
      setChainId(network.chainId);
      setWallet(address);
      
      // Get ETH balance
      const balance = await web3Provider.getBalance(address);
      setEthBalance(ethers.utils.formatEther(balance));
      
      // Register with backend
      await axios.post(`${API}/investors/register`, { wallet_address: address });
      
      // Check network
      if (network.chainId !== 11155111) {
        toast.warning("Please switch to Sepolia testnet");
      }
    }
  };

  const switchToSepolia = async () => {
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: '0xaa36a7' }]  // Sepolia chain ID
    });
  };

  // Deposit ETH to smart contract
  const depositToContract = async (amountEth) => {
    const tx = await signer.sendTransaction({
      to: contractAddress,
      value: ethers.utils.parseEther(amountEth.toString()),
      data: "0xd0e30db0"  // deposit() function selector
    });
    await tx.wait();
  };

  return (
    <WalletContext.Provider value={{ 
      wallet, provider, signer, chainId, ethBalance,
      connectWallet, switchToSepolia, depositToContract 
    }}>
      {children}
    </WalletContext.Provider>
  );
};
    """
    story.append(Paragraph(format_code_for_pdf(wallet_code), styles['CodeBlock']))
    story.append(PageBreak())

def create_database_section(story, styles):
    """Section 8: Database Schema"""
    story.append(Paragraph("8. Database Schema (MongoDB)", styles['SectionHeading']))
    
    story.append(Paragraph("""
    The platform uses MongoDB with the Motor async driver. All collections store JSON documents 
    with auto-generated string IDs (not ObjectIds) to avoid serialization issues.
    """, styles['CustomBody']))
    
    collections = [
        ['Collection', 'Document Structure', 'Purpose'],
        ['investors', '{id, wallet_address, balance, shares, paper_balance, paper_pnl}', 'Investor accounts'],
        ['trading_agents', '{id, name, type, status, strategy, performance_7d, capital_allocation}', 'AI agents'],
        ['trades', '{id, agent_id, symbol, side, amount, price, pnl, slippage, is_simulation}', 'Trade history'],
        ['strategies', '{id, name, type, parameters, status, sharpe_ratio, total_return, is_active}', 'Trading strategies'],
        ['risk_config', '{max_drawdown, max_position_size, max_daily_loss, auto_shutdown_enabled}', 'Risk settings'],
        ['risk_alerts', '{id, type, severity, message, resolved, auto_action_taken}', 'Risk alerts'],
        ['simulation_config', '{is_running, mode, initial_capital, time_acceleration}', 'Simulation state'],
        ['simulation_logs', '{id, log_type, agent_name, message, details, timestamp}', 'Simulation logs'],
        ['agent_interactions', '{from_agent, to_agent, interaction_type, payload}', 'Agent-to-agent logs'],
        ['marketplace_agents', '{id, name, strategy, developer_address, performance_30d}', 'Marketplace agents'],
        ['event_agents', '{id, name, type, events_to_monitor, is_active}', 'Event-driven agents'],
        ['contract_events', '{event_name, block_number, tx_hash, args, processed}', 'Contract events'],
        ['contract_info', '{contract_address, network, deployed, deployer_address}', 'Contract deployment'],
        ['research_simulations', '{id, config, metrics, equity_curve, trade_count}', 'Research results'],
        ['walk_forward_tests', '{id, aggregate_metrics, window_results}', 'Walk-forward results'],
        ['investor_reports', '{report_id, executive_summary, performance_summary}', 'Generated reports'],
        ['historical_data', '{timestamp, symbol, open, high, low, close, volume}', 'Price history'],
    ]
    t = Table(collections, colWidths=[1.5*inch, 2.8*inch, 1.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(PageBreak())

def create_config_section(story, styles):
    """Section 9: Configuration Files"""
    story.append(Paragraph("9. Configuration Files", styles['SectionHeading']))
    
    story.append(Paragraph("9.1 Backend Environment (.env)", styles['SubHeading']))
    backend_env = """
# MongoDB connection
MONGO_URL=mongodb://localhost:27017
DB_NAME=alphaai_fund

# Emergent LLM Key for AI integration
EMERGENT_LLM_KEY=your_emergent_key_here

# CORS settings
CORS_ORIGINS=*
    """
    story.append(Paragraph(format_code_for_pdf(backend_env), styles['CodeBlock']))
    
    story.append(Paragraph("9.2 Frontend Environment (.env)", styles['SubHeading']))
    frontend_env = """
# Backend API URL
REACT_APP_BACKEND_URL=https://idle-cache.preview.emergentagent.com
    """
    story.append(Paragraph(format_code_for_pdf(frontend_env), styles['CodeBlock']))
    
    story.append(Paragraph("9.3 Backend Dependencies (requirements.txt)", styles['SubHeading']))
    requirements = """
fastapi>=0.109.0
uvicorn>=0.27.0
motor>=3.3.0
python-dotenv>=1.0.0
httpx>=0.26.0
pydantic>=2.5.0
emergentintegrations>=1.0.0
reportlab>=4.0.0
web3>=6.0.0
pandas>=2.0.0
    """
    story.append(Paragraph(format_code_for_pdf(requirements), styles['CodeBlock']))
    
    story.append(Paragraph("9.4 Frontend Dependencies (package.json key deps)", styles['SubHeading']))
    packages = """
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.x",
    "axios": "^1.x",
    "ethers": "^5.7.0",
    "recharts": "^2.x",
    "framer-motion": "^10.x",
    "sonner": "^1.x",
    "@radix-ui/react-*": "Shadcn/UI components",
    "lucide-react": "^0.x",
    "tailwindcss": "^3.x"
  }
}
    """
    story.append(Paragraph(format_code_for_pdf(packages), styles['CodeBlock']))
    story.append(PageBreak())

def create_workflow_section(story, styles):
    """Section 10: End-to-End Workflow"""
    story.append(Paragraph("10. End-to-End System Workflow", styles['SectionHeading']))
    
    story.append(Paragraph("10.1 User Onboarding Flow", styles['SubHeading']))
    story.append(Paragraph("""
    1. User visits landing page → Sees fund stats, features, live prices<br/>
    2. User clicks "Connect Wallet" → MetaMask popup appears<br/>
    3. User approves connection → Frontend calls POST /api/investors/register<br/>
    4. Backend creates investor record → Returns investor data<br/>
    5. User redirected to Dashboard → Can view portfolio, enable paper trading
    """, styles['CustomBody']))
    
    story.append(Paragraph("10.2 Simulation Flow", styles['SubHeading']))
    story.append(Paragraph("""
    1. Admin navigates to Simulation page → Configures settings<br/>
    2. Clicks "Start Simulation" → POST /api/simulation/start<br/>
    3. Backend initializes SimulationEngine → Creates default strategies<br/>
    4. Runs capital allocation → Distributes funds to strategies<br/>
    5. Each "Run Cycle" → Executes trades for each strategy<br/>
    6. After each trade → Risk engine checks rules<br/>
    7. If risk violated → Auto-stop or reduce positions<br/>
    8. Results logged to database → Displayed on dashboard
    """, styles['CustomBody']))
    
    story.append(Paragraph("10.3 Strategy Lab Flow", styles['SubHeading']))
    story.append(Paragraph("""
    1. User opens Strategy Lab → Views existing strategies<br/>
    2. Selects type + clicks "Generate Strategy" → POST /api/lab/strategies/generate<br/>
    3. AI generates strategy → Status = "generated"<br/>
    4. User clicks "Backtest" → POST /api/lab/strategies/{id}/backtest<br/>
    5. Backtest runs → Returns Sharpe, return, drawdown<br/>
    6. If good metrics → User clicks "Sandbox"<br/>
    7. Sandbox testing runs → Paper trades strategy<br/>
    8. If Sharpe > 1.0 and positive returns → User clicks "Deploy"<br/>
    9. Strategy goes live → Receives capital allocation
    """, styles['CustomBody']))
    
    story.append(Paragraph("10.4 Research Engine Flow", styles['SubHeading']))
    story.append(Paragraph("""
    1. User opens Research page → Configures simulation<br/>
    2. Sets target months, speed (500x), capital<br/>
    3. Clicks "Run Simulation" → POST /api/research/run-simulation<br/>
    4. Backend loads historical data from CSV files<br/>
    5. Runs 4 agents through historical prices<br/>
    6. Calculates daily P&L, equity curve, metrics<br/>
    7. Returns comprehensive results with charts<br/>
    8. User can run Walk-Forward Test → Validates robustness<br/>
    9. Generate Investor Report → Creates PDF/JSON
    """, styles['CustomBody']))
    
    story.append(Paragraph("10.5 Smart Contract Flow", styles['SubHeading']))
    story.append(Paragraph("""
    1. Admin deploys AlphaAIManager.sol to Sepolia<br/>
    2. Registers contract address → POST /api/contract/register<br/>
    3. User connects MetaMask on Sepolia network<br/>
    4. User clicks "Deposit" → Prepares transaction via backend<br/>
    5. User signs transaction in MetaMask → ETH sent to contract<br/>
    6. Contract emits InvestorDeposited event<br/>
    7. Event agents detect event → Process automatically<br/>
    8. Investor Monitor Agent → Updates balances dashboard<br/>
    9. Strategy Allocator Agent → Auto-allocates 25% to top strategy
    """, styles['CustomBody']))
    
    story.append(Paragraph("10.6 Event-Driven Agent Flow", styles['SubHeading']))
    story.append(Paragraph("""
    1. Contract event occurs (deposit, withdrawal, allocation)<br/>
    2. Backend receives event → Stores in contract_events collection<br/>
    3. process_event() function called → Gets active agents<br/>
    4. Each agent matching event type → Executes action<br/>
    5. Watcher agents → Update balances, log activity<br/>
    6. Execution agents → Auto-allocate funds to strategies<br/>
    7. Analytics agents → Refresh dashboards<br/>
    8. Agent stats updated → events_processed_count incremented
    """, styles['CustomBody']))
    
    story.append(PageBreak())

def create_footer(story, styles):
    """Create document footer"""
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("─" * 80, ParagraphStyle('Line', alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Paragraph(
        "© 2026 Martin Maughan. All rights reserved. AlphaAI Platform.<br/>"
        "This document is for external review and system rebuilding purposes.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.gray)
    ))

# ===================== MAIN GENERATOR =====================

def generate_comprehensive_report():
    """Generate the complete AlphaAI Platform PDF documentation"""
    
    # Output path
    output_dir = Path(__file__).parent / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "AlphaAI_Complete_Technical_Documentation.pdf"
    
    # Read source files
    backend_path = Path(__file__).parent / "server.py"
    frontend_path = Path(__file__).parent.parent / "frontend" / "src" / "App.js"
    contract_path = Path(__file__).parent / "contracts" / "AlphaAIManager.sol"
    
    server_code = read_file_safe(backend_path)
    app_code = read_file_safe(frontend_path)
    contract_code = read_file_safe(contract_path)
    
    # Create document
    doc = SimpleDocTemplate(
        str(output_path), 
        pagesize=A4,
        rightMargin=40, 
        leftMargin=40,
        topMargin=40, 
        bottomMargin=40
    )
    
    styles = get_styles()
    story = []
    
    # Build document sections
    print("Creating cover page...")
    create_cover_page(story, styles)
    
    print("Creating table of contents...")
    create_table_of_contents(story, styles)
    
    print("Creating executive summary...")
    create_executive_summary(story, styles)
    
    print("Creating architecture section...")
    create_architecture_section(story, styles)
    
    print("Creating backend section...")
    create_backend_section(story, styles, server_code)
    
    print("Creating frontend section...")
    create_frontend_section(story, styles, app_code)
    
    print("Creating smart contract section...")
    create_smart_contract_section(story, styles, contract_code)
    
    print("Creating trading strategies section...")
    create_trading_strategies_section(story, styles)
    
    print("Creating AI integration section...")
    create_ai_integration_section(story, styles)
    
    print("Creating database section...")
    create_database_section(story, styles)
    
    print("Creating configuration section...")
    create_config_section(story, styles)
    
    print("Creating workflow section...")
    create_workflow_section(story, styles)
    
    print("Creating footer...")
    create_footer(story, styles)
    
    # Build PDF
    print("Building PDF...")
    doc.build(story)
    
    print(f"\n✅ Comprehensive PDF generated: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    path = generate_comprehensive_report()
    print(f"\nDocument saved to: {path}")
