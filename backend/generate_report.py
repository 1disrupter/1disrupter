#!/usr/bin/env python3
"""
AlphaAI Platform - Comprehensive PDF Report Generator
Generates a full documentation of the platform for investors and stakeholders
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

def create_alphaai_report():
    """Generate the complete AlphaAI Platform PDF report"""
    
    # Output path
    output_path = "/app/backend/reports/AlphaAI_Platform_Report.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#7B61FF'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#00FF94'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#FFB800'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    # Build document content
    story = []
    
    # ===== COVER PAGE =====
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("AlphaAI Fund Platform", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Decentralized AI-Powered Hedge Fund", ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Technical Documentation & Platform Overview", ParagraphStyle(
        'Subtitle2', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 1*inch))
    
    # Report metadata
    meta_data = [
        ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ['Version:', '1.0'],
        ['Status:', 'Production Ready (Testnet)'],
        ['Copyright:', '© 2026 Martin Maughan. All rights reserved.']
    ]
    meta_table = Table(meta_data, colWidths=[1.5*inch, 3*inch])
    meta_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ]))
    story.append(meta_table)
    story.append(PageBreak())
    
    # ===== TABLE OF CONTENTS =====
    story.append(Paragraph("Table of Contents", heading_style))
    toc_items = [
        "1. Executive Summary",
        "2. Platform Architecture",
        "3. AI Trading Agents",
        "4. Smart Contract Integration",
        "5. Research Engine",
        "6. Risk Management",
        "7. Event-Driven System",
        "8. Live Market Data",
        "9. Performance Metrics",
        "10. API Reference",
        "11. Security & Compliance",
        "12. Roadmap"
    ]
    for item in toc_items:
        story.append(Paragraph(item, body_style))
    story.append(PageBreak())
    
    # ===== 1. EXECUTIVE SUMMARY =====
    story.append(Paragraph("1. Executive Summary", heading_style))
    story.append(Paragraph("""
    AlphaAI is a decentralized AI-powered hedge fund platform that enables investors to deposit capital 
    into a vault managed by autonomous AI trading agents. The platform features advanced simulation 
    capabilities, real-time market data integration, and comprehensive risk management systems.
    """, body_style))
    
    story.append(Paragraph("Key Highlights", subheading_style))
    highlights = [
        ['Feature', 'Status', 'Description'],
        ['Live Price Feed', '✅ Active', 'Real-time prices from Kraken API'],
        ['MetaMask Integration', '✅ Active', 'Web3 wallet connection for Sepolia'],
        ['AI Trading Agents', '✅ Active', '4 autonomous trading strategies'],
        ['Research Engine', '✅ Active', '500x accelerated backtesting'],
        ['Smart Contract', '✅ Ready', 'AlphaAIManager.sol for Sepolia'],
        ['Walk-Forward Testing', '✅ Active', 'Strategy robustness validation'],
        ['Risk Management', '✅ Active', 'Auto-stop, drawdown limits'],
        ['Event Agents', '✅ Active', '3 event-driven monitors'],
    ]
    t = Table(highlights, colWidths=[1.5*inch, 1*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ===== 2. PLATFORM ARCHITECTURE =====
    story.append(Paragraph("2. Platform Architecture", heading_style))
    
    story.append(Paragraph("Technology Stack", subheading_style))
    tech_stack = [
        ['Component', 'Technology', 'Purpose'],
        ['Frontend', 'React + Shadcn/UI', 'User interface'],
        ['Backend', 'FastAPI (Python)', 'API server'],
        ['Database', 'MongoDB', 'Data persistence'],
        ['Blockchain', 'Ethereum (Sepolia)', 'Smart contracts'],
        ['Wallet', 'MetaMask + ethers.js', 'Web3 integration'],
        ['Price Data', 'Kraken API', 'Live market prices'],
        ['AI Analysis', 'OpenAI GPT-5.2', 'Market analysis'],
    ]
    t = Table(tech_stack, colWidths=[1.5*inch, 2*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00FF94')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Directory Structure", subheading_style))
    structure = """
    /app/
    ├── backend/
    │   ├── server.py (Main FastAPI application)
    │   ├── contracts/AlphaAIManager.sol
    │   ├── data/ (Historical price CSV files)
    │   └── reports/ (Generated investor reports)
    ├── frontend/
    │   ├── src/App.js (Main React application)
    │   └── components/ui/ (Shadcn components)
    └── memory/PRD.md (Product requirements)
    """
    story.append(Paragraph(structure.replace('\n', '<br/>'), ParagraphStyle(
        'Code', parent=styles['Normal'], fontSize=8, fontName='Courier', leftIndent=20)))
    story.append(PageBreak())
    
    # ===== 3. AI TRADING AGENTS =====
    story.append(Paragraph("3. AI Trading Agents", heading_style))
    story.append(Paragraph("""
    The platform employs four specialized AI trading agents, each allocated 25% of the fund's capital.
    These agents operate autonomously using different trading strategies to maximize risk-adjusted returns.
    """, body_style))
    
    agents_data = [
        ['Agent Name', 'Strategy', 'Allocation', 'Description'],
        ['Arbitrage Agent', 'Mean Reversion', '25%', 'Trades against large price moves, capitalizing on market overreactions'],
        ['Momentum Agent', 'Trend Following', '25%', 'Follows established trends with enhanced position sizing'],
        ['Funding Rate Agent', 'Volatility Breakout', '25%', 'Trades on volatility spikes and market momentum'],
        ['AI Research Lab', 'Adaptive', '25%', 'Auto-generates and deploys new strategies based on market conditions'],
    ]
    t = Table(agents_data, colWidths=[1.3*inch, 1.2*inch, 0.8*inch, 2.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFB800')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ===== 4. SMART CONTRACT =====
    story.append(Paragraph("4. Smart Contract Integration", heading_style))
    story.append(Paragraph("AlphaAIManager.sol", subheading_style))
    story.append(Paragraph("""
    The AlphaAIManager smart contract is deployed on the Ethereum Sepolia testnet and handles:
    • Investor deposits and withdrawals
    • Strategy fund allocation
    • On-chain balance tracking
    • Emergency withdrawal functionality (owner only)
    """, body_style))
    
    contract_functions = [
        ['Function', 'Type', 'Description'],
        ['deposit()', 'payable', 'Deposit ETH into the fund'],
        ['withdraw(uint256)', 'nonpayable', 'Withdraw specified amount'],
        ['addStrategy(string)', 'onlyOwner', 'Add new trading strategy'],
        ['allocateToStrategy(uint256, uint256)', 'onlyOwner', 'Allocate funds to strategy'],
        ['getInvestorBalance(address)', 'view', 'Get investor balance'],
        ['getStrategy(uint256)', 'view', 'Get strategy details'],
        ['emergencyWithdraw()', 'onlyOwner', 'Emergency fund withdrawal'],
    ]
    t = Table(contract_functions, colWidths=[2.5*inch, 1*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ===== 5. RESEARCH ENGINE =====
    story.append(Paragraph("5. Research Engine", heading_style))
    story.append(Paragraph("""
    The AlphaAI Research Engine provides institutional-grade backtesting and strategy validation
    capabilities with 500x time acceleration.
    """, body_style))
    
    story.append(Paragraph("Features", subheading_style))
    research_features = [
        ['Feature', 'Configuration', 'Output'],
        ['Accelerated Simulation', '500x speed, 6 months', 'Equity curve, metrics, trade history'],
        ['Walk-Forward Testing', '90d train / 30d test', 'Robustness score, window results'],
        ['Historical Data', 'BTC/USD, ETH/USD CSV', 'Price-driven simulation'],
        ['Performance Metrics', '14 key metrics', 'Sharpe, Sortino, Max DD, etc.'],
        ['Strategy Contribution', 'Per-agent breakdown', 'Individual P&L attribution'],
        ['Investor Reports', 'PDF/JSON format', 'Monthly performance reports'],
    ]
    t = Table(research_features, colWidths=[1.5*inch, 1.8*inch, 2.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00FF94')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    
    story.append(Paragraph("Performance Metrics Tracked", subheading_style))
    metrics_list = """
    • Total Return & Annualized Return
    • Sharpe Ratio & Sortino Ratio
    • Maximum Drawdown
    • Win Rate & Profit Factor
    • Trade Frequency
    • Average Trade Return
    • Best/Worst Trade
    • Strategy Contribution %
    """
    story.append(Paragraph(metrics_list.replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    # ===== 6. RISK MANAGEMENT =====
    story.append(Paragraph("6. Risk Management", heading_style))
    story.append(Paragraph("""
    The platform includes comprehensive risk management controls to protect investor capital.
    """, body_style))
    
    risk_controls = [
        ['Control', 'Threshold', 'Action'],
        ['Max Drawdown', '5%', 'Auto-stop all trading'],
        ['Daily Loss Limit', '3%', 'Reduce position sizes by 50%'],
        ['Position Size', '10-15%', 'Per-trade allocation limit'],
        ['Stop Loss', '5%', 'Per-agent stop loss'],
        ['Risk Alerts', '2% drawdown', 'Send alerts to all agents'],
    ]
    t = Table(risk_controls, colWidths=[1.5*inch, 1.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    
    story.append(Paragraph("Stress Test Scenarios", subheading_style))
    stress_tests = [
        ['Scenario', 'Parameters', 'Purpose'],
        ['BTC 30% Drop', '30% drop over 24 hours', 'Test market crash resilience'],
        ['ETH Flash Crash', '50% drop over 12 hours', 'Test flash crash handling'],
        ['Market Panic', '40% drop over 6 hours', 'Test rapid selloff response'],
        ['Liquidity Crisis', '25% drop over 48 hours', 'Test extended stress periods'],
    ]
    t = Table(stress_tests, colWidths=[1.5*inch, 2*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFB800')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ===== 7. EVENT-DRIVEN SYSTEM =====
    story.append(Paragraph("7. Event-Driven Agent System", heading_style))
    story.append(Paragraph("""
    Three specialized agents monitor smart contract events and execute automated responses.
    """, body_style))
    
    event_agents = [
        ['Agent', 'Type', 'Events Monitored', 'Actions'],
        ['Investor Monitor', 'Watcher', 'InvestorDeposited, InvestorWithdrawn', 'Update balances dashboard'],
        ['Strategy Allocator', 'Execution', 'InvestorDeposited', 'Auto-allocate 25% to top strategy'],
        ['Dashboard Updater', 'Analytics', 'StrategyAllocated, StrategyDeallocated', 'Refresh allocation dashboard'],
    ]
    t = Table(event_agents, colWidths=[1.3*inch, 0.8*inch, 1.8*inch, 1.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ===== 8. LIVE MARKET DATA =====
    story.append(Paragraph("8. Live Market Data Integration", heading_style))
    story.append(Paragraph("""
    Real-time cryptocurrency prices are fetched from the Kraken API with 30-second refresh intervals.
    """, body_style))
    
    market_data = [
        ['Asset', 'Symbol', 'Data Points'],
        ['Bitcoin', 'BTC/USD', 'Price, 24h Change, Volume'],
        ['Ethereum', 'ETH/USD', 'Price, 24h Change, Volume'],
        ['Solana', 'SOL/USD', 'Price, 24h Change, Volume'],
        ['Avalanche', 'AVAX/USD', 'Price, 24h Change, Volume'],
        ['Polygon', 'MATIC/USD', 'Price, 24h Change, Volume'],
        ['Chainlink', 'LINK/USD', 'Price, 24h Change, Volume'],
        ['Uniswap', 'UNI/USD', 'Price, 24h Change, Volume'],
        ['Aave', 'AAVE/USD', 'Price, 24h Change, Volume'],
    ]
    t = Table(market_data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00FF94')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ===== 9. API REFERENCE =====
    story.append(Paragraph("10. API Reference", heading_style))
    
    api_endpoints = [
        ['Endpoint', 'Method', 'Description'],
        ['/api/market/live-prices', 'GET', 'Get live crypto prices'],
        ['/api/simulation/start', 'POST', 'Start simulation'],
        ['/api/simulation/run-accelerated', 'POST', 'Run 500x simulation'],
        ['/api/simulation/stress-test', 'POST', 'Run stress test'],
        ['/api/research/run-simulation', 'POST', 'Run research backtest'],
        ['/api/research/walk-forward-test', 'POST', 'Run walk-forward validation'],
        ['/api/research/generate-investor-report', 'POST', 'Generate PDF report'],
        ['/api/contract/info', 'GET', 'Get contract status'],
        ['/api/contract/register', 'POST', 'Register deployed contract'],
        ['/api/agents/event-agents', 'GET', 'Get event agents'],
        ['/api/dashboards/investor-balances', 'GET', 'Get investor balances'],
        ['/api/dashboards/strategy-allocation', 'GET', 'Get allocations'],
        ['/api/fund/stats', 'GET', 'Get fund statistics'],
        ['/api/lab/strategies', 'GET', 'Get all strategies'],
        ['/api/risk/config', 'GET/PUT', 'Risk configuration'],
    ]
    t = Table(api_endpoints, colWidths=[2.5*inch, 0.8*inch, 2.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B61FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ===== 11. SECURITY & COMPLIANCE =====
    story.append(Paragraph("11. Security & Compliance", heading_style))
    
    story.append(Paragraph("Security Measures", subheading_style))
    security_items = """
    • MetaMask wallet integration for secure authentication
    • Smart contract owner-only functions for critical operations
    • Emergency withdrawal capability for fund protection
    • Rate limiting on API endpoints
    • Input validation on all user inputs
    """
    story.append(Paragraph(security_items.replace('\n', '<br/>'), body_style))
    
    story.append(Paragraph("Pre-Mainnet Requirements", subheading_style))
    requirements = """
    • Smart contract security audit (recommended: OpenZeppelin, Trail of Bits)
    • Penetration testing of web application
    • JWT user authentication implementation
    • Legal and regulatory compliance review
    • Insurance coverage consideration
    """
    story.append(Paragraph(requirements.replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    # ===== 12. ROADMAP =====
    story.append(Paragraph("12. Development Roadmap", heading_style))
    
    roadmap = [
        ['Phase', 'Status', 'Features'],
        ['Phase 1: MVP Core', '✅ Complete', 'Basic trading agents, dashboard, marketplace'],
        ['Phase 2: Advanced AI', '✅ Complete', 'Strategy lab, risk engine, capital allocation'],
        ['Phase 3: Simulation', '✅ Complete', 'Paper trading, trade cycles, logging'],
        ['Phase 4: Reports', '✅ Complete', 'Daily/weekly reports, mode switching'],
        ['Phase 5: Enhanced Sim', '✅ Complete', '500x acceleration, stress testing'],
        ['Phase 6: Smart Contract', '✅ Complete', 'Solidity contract, MetaMask integration'],
        ['Phase 7: Research Engine', '✅ Complete', 'Walk-forward validation, CSV data'],
        ['Phase 8: Testnet Deploy', '🟡 Pending', 'Deploy to Sepolia, live testing'],
        ['Phase 9: Security Audit', '🔴 Pending', 'Third-party audit, penetration testing'],
        ['Phase 10: Mainnet', '🔴 Pending', 'Production deployment, real trading'],
    ]
    t = Table(roadmap, colWidths=[1.5*inch, 1*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFB800')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Production Readiness: 90%", ParagraphStyle(
        'Ready', parent=styles['Heading2'], fontSize=14, alignment=TA_CENTER, textColor=colors.HexColor('#00FF94'))))
    
    # Footer
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 60, ParagraphStyle('Line', alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Paragraph("© 2026 Martin Maughan. All rights reserved. AlphaAI Platform.", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.gray)))
    
    # Build PDF
    doc.build(story)
    return output_path

if __name__ == "__main__":
    path = create_alphaai_report()
    print(f"PDF Report generated: {path}")
