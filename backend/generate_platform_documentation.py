#!/usr/bin/env python3
"""
AlphaAI Platform - Complete System Overview & Product Documentation
Professional PDF Generator
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

# Colors
PURPLE = colors.HexColor('#7B61FF')
GREEN = colors.HexColor('#00FF94')
DARK_BG = colors.HexColor('#121212')
GRAY = colors.HexColor('#666666')
LIGHT_GRAY = colors.HexColor('#999999')

def create_styles():
    """Create custom paragraph styles"""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='DocTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        textColor=PURPLE,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Subtitle
    styles.add(ParagraphStyle(
        name='DocSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=40,
        textColor=GRAY,
        alignment=TA_CENTER
    ))
    
    # Section heading
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading1'],
        fontSize=18,
        spaceBefore=25,
        spaceAfter=15,
        textColor=PURPLE,
        fontName='Helvetica-Bold',
        borderPadding=(0, 0, 5, 0),
        borderWidth=0,
        borderColor=PURPLE
    ))
    
    # Subsection heading
    styles.add(ParagraphStyle(
        name='SubHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=16
    ))
    
    # Bullet point
    styles.add(ParagraphStyle(
        name='BulletText',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leftIndent=20,
        leading=14
    ))
    
    # Highlight box text
    styles.add(ParagraphStyle(
        name='HighlightText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=PURPLE,
        fontName='Helvetica-Bold'
    ))
    
    # Footer
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=LIGHT_GRAY,
        alignment=TA_CENTER
    ))
    
    return styles

def add_section(story, title, styles):
    """Add a section heading"""
    story.append(Spacer(1, 10))
    story.append(Paragraph(title, styles['SectionHeading']))
    story.append(Spacer(1, 5))

def add_subsection(story, title, styles):
    """Add a subsection heading"""
    story.append(Paragraph(title, styles['SubHeading']))

def add_body(story, text, styles):
    """Add body text"""
    story.append(Paragraph(text, styles['CustomBody']))

def add_bullets(story, items, styles):
    """Add bullet points"""
    for item in items:
        story.append(Paragraph(f"• {item}", styles['BulletText']))

def add_numbered_list(story, items, styles):
    """Add numbered list"""
    for i, item in enumerate(items, 1):
        story.append(Paragraph(f"{i}. {item}", styles['BulletText']))

def create_highlight_box(content, width=6*inch):
    """Create a highlighted box"""
    data = [[Paragraph(content, ParagraphStyle('BoxText', fontSize=11, textColor=colors.black))]]
    table = Table(data, colWidths=[width])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F3FF')),
        ('BOX', (0, 0), (-1, -1), 1, PURPLE),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return table

def create_metrics_table(metrics):
    """Create a metrics display table"""
    data = [list(metrics.keys()), list(metrics.values())]
    table = Table(data, colWidths=[1.5*inch] * len(metrics))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F0F0F0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    return table

def create_pricing_table():
    """Create pricing comparison table"""
    data = [
        ['Feature', 'Free', 'Pro ($29/mo)', 'Elite ($79/mo)'],
        ['AI Signals', '✓ Delayed (15 min)', '✓ Real-time', '✓ Real-time'],
        ['Signal History', '✓ Limited', '✓ Full Access', '✓ Full Access'],
        ['Performance Stats', '✓ Basic', '✓ Advanced', '✓ Advanced'],
        ['Email Alerts', '✗', '✓', '✓'],
        ['Push Notifications', '✗', '✓', '✓'],
        ['AI Market Analysis', '✗', '✓', '✓ Priority'],
        ['Priority Support', '✗', '✗', '✓'],
        ['Custom Alerts', '✗', '✗', '✓'],
    ]
    
    table = Table(data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    return table

def create_tech_stack_table():
    """Create technical stack table"""
    data = [
        ['Component', 'Technology', 'Purpose'],
        ['Backend', 'FastAPI (Python)', 'API server, business logic'],
        ['Frontend', 'React 18 + Shadcn/UI', 'User interface'],
        ['Database', 'MongoDB', 'Data persistence'],
        ['Payments', 'Stripe', 'Subscription billing'],
        ['Market Data', 'Kraken API', 'Live crypto prices'],
        ['AI Analysis', 'OpenAI GPT-5.2', 'Market insights'],
        ['Web3', 'ethers.js / web3.py', 'Wallet integration'],
    ]
    
    table = Table(data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    return table

def generate_pdf():
    """Generate the complete PDF document"""
    
    # Output path
    output_dir = "/app/backend/reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/AlphaAI_Complete_Documentation.pdf"
    
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = create_styles()
    story = []
    
    # ==================== COVER PAGE ====================
    story.append(Spacer(1, 100))
    story.append(Paragraph("AlphaAI Platform", styles['DocTitle']))
    story.append(Paragraph("Complete System Overview & Product Documentation", styles['DocSubtitle']))
    story.append(Spacer(1, 30))
    
    # Tagline box
    story.append(create_highlight_box(
        "<b>AI-Powered Crypto Signals & Trading Insights Platform</b><br/><br/>"
        "Professional-grade market analysis delivered in real-time"
    ))
    
    story.append(Spacer(1, 50))
    story.append(Paragraph(f"Document Version: 1.0", styles['Footer']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Footer']))
    story.append(Paragraph("Confidential - For Internal Review", styles['Footer']))
    story.append(PageBreak())
    
    # ==================== TABLE OF CONTENTS ====================
    story.append(Paragraph("Table of Contents", styles['SectionHeading']))
    story.append(Spacer(1, 20))
    
    toc_items = [
        "1. Executive Summary",
        "2. Product Overview",
        "3. Key Features",
        "4. User Experience Flow",
        "5. Conversion System",
        "6. Pricing Model",
        "7. Payment System",
        "8. Technical Architecture",
        "9. Current Limitations",
        "10. Future Roadmap",
        "11. Performance Data",
        "12. Branding & Positioning"
    ]
    for item in toc_items:
        story.append(Paragraph(item, styles['CustomBody']))
    
    story.append(PageBreak())
    
    # ==================== 1. EXECUTIVE SUMMARY ====================
    add_section(story, "1. Executive Summary", styles)
    
    add_subsection(story, "What is AlphaAI?", styles)
    add_body(story, 
        "AlphaAI is a Software-as-a-Service (SaaS) platform that provides AI-generated cryptocurrency trading signals "
        "and market insights. The platform analyzes market data in real-time and delivers actionable BUY, SELL, or HOLD "
        "recommendations to help traders make informed decisions.", styles)
    
    story.append(Spacer(1, 10))
    add_subsection(story, "Core Value Proposition", styles)
    story.append(create_highlight_box(
        "<b>\"AI crypto signals + trading insights platform\"</b><br/><br/>"
        "Simplifying cryptocurrency trading through intelligent automation and real-time analysis."
    ))
    
    story.append(Spacer(1, 15))
    add_subsection(story, "Target Users", styles)
    add_bullets(story, [
        "Retail crypto traders seeking data-driven insights",
        "Beginners looking for guidance in volatile markets",
        "Experienced traders wanting to automate signal detection",
        "Portfolio managers tracking multiple assets",
        "Anyone interested in AI-powered financial tools"
    ], styles)
    
    add_subsection(story, "Business Model", styles)
    add_body(story, 
        "AlphaAI operates on a freemium SaaS model with three subscription tiers:", styles)
    add_bullets(story, [
        "<b>Free:</b> Limited access with 15-minute delayed signals",
        "<b>Pro ($29/month):</b> Real-time signals, alerts, and full AI analysis",
        "<b>Elite ($79/month):</b> Priority features, custom alerts, and dedicated support"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== 2. PRODUCT OVERVIEW ====================
    add_section(story, "2. Product Overview", styles)
    
    add_subsection(story, "Dashboard Experience", styles)
    add_body(story, 
        "The AlphaAI dashboard provides a clean, modern interface designed for quick decision-making. "
        "Users can view current market signals, track performance metrics, and access AI-generated market analysis "
        "all from a single screen.", styles)
    
    add_subsection(story, "Today's AI Signals", styles)
    add_body(story, 
        "The core feature displays real-time trading signals for major cryptocurrencies (BTC, ETH, SOL, etc.). "
        "Each signal includes:", styles)
    add_bullets(story, [
        "Asset symbol and current price",
        "Signal type: BUY, SELL, or HOLD",
        "Confidence score (percentage)",
        "Visual color coding (green for BUY, red for SELL, yellow for HOLD)"
    ], styles)
    
    add_subsection(story, "Delayed vs Real-Time Signals", styles)
    add_body(story, 
        "Free users receive signals with a 15-minute delay, while Pro and Elite subscribers "
        "get instant, real-time updates. This delay creates natural conversion pressure while "
        "still providing value to free users.", styles)
    
    add_subsection(story, "Performance Tracking", styles)
    add_body(story, "The dashboard displays key performance metrics:", styles)
    
    # Performance metrics table
    metrics = {
        '30-Day Return': '+12.4%',
        'Win Rate': '68%',
        'Max Drawdown': '4.2%',
        'Total Signals': '847'
    }
    story.append(Spacer(1, 10))
    story.append(create_metrics_table(metrics))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>Note: All performance data is from paper trading simulations</i>", styles['Footer']))
    
    add_subsection(story, "AI Market Summary", styles)
    add_body(story, 
        "An AI-generated text summary provides context for current market conditions, "
        "helping users understand the reasoning behind each signal.", styles)
    
    story.append(PageBreak())
    
    # ==================== 3. KEY FEATURES ====================
    add_section(story, "3. Key Features", styles)
    
    features = [
        ("<b>AI-Generated Signals</b>", 
         "Automated BUY/SELL/HOLD recommendations based on technical analysis, market sentiment, and AI pattern recognition."),
        ("<b>Performance Metrics</b>", 
         "Track returns, win rate, maximum drawdown, and total signals generated over various time periods."),
        ("<b>Signal History</b>", 
         "View recent signals with their outcomes (e.g., 'BTC → BUY → +2.1%') to build trust and demonstrate consistency."),
        ("<b>Missed Trade Indicators</b>", 
         "FOMO-inducing displays showing trades free users missed (e.g., 'Signal triggered 12 mins ago → +1.6%')."),
        ("<b>Upgrade Prompts</b>", 
         "Strategic CTAs throughout the interface encouraging conversion to paid plans."),
        ("<b>Demo Mode</b>", 
         "Users can explore the platform without connecting a wallet, reducing friction to trial."),
        ("<b>Live User Counter</b>", 
         "Social proof showing active users (e.g., '27 users viewing signals right now')."),
        ("<b>Countdown Timer</b>", 
         "Creates urgency with 'Next signal update in: 00:45' countdown."),
    ]
    
    for title, desc in features:
        story.append(Paragraph(title, styles['SubHeading']))
        story.append(Paragraph(desc, styles['CustomBody']))
        story.append(Spacer(1, 5))
    
    story.append(PageBreak())
    
    # ==================== 4. USER EXPERIENCE FLOW ====================
    add_section(story, "4. User Experience Flow", styles)
    
    add_body(story, "The typical user journey through AlphaAI:", styles)
    story.append(Spacer(1, 10))
    
    flow_steps = [
        "<b>Landing:</b> User arrives at homepage, sees value proposition and live signal preview",
        "<b>Entry:</b> Clicks 'Try Demo Mode' or 'Connect Wallet' to access dashboard",
        "<b>Discovery:</b> Views delayed signals (15-min delay for free users)",
        "<b>Engagement:</b> Explores performance metrics, signal history, AI summaries",
        "<b>Conversion Triggers:</b> Sees upgrade prompts, missed trades, social proof",
        "<b>Decision Point:</b> Encounters 2-minute popup or exit-intent modal",
        "<b>Upgrade:</b> Clicks upgrade, completes Stripe checkout ($29/month)",
        "<b>Activation:</b> Instantly unlocks real-time signals and full features",
        "<b>Retention:</b> Continues using platform with live data and alerts"
    ]
    add_numbered_list(story, flow_steps, styles)
    
    story.append(Spacer(1, 20))
    story.append(create_highlight_box(
        "<b>Key Insight:</b> The flow is designed to provide immediate value (free signals) "
        "while creating natural friction (delay) that motivates upgrades."
    ))
    
    story.append(PageBreak())
    
    # ==================== 5. CONVERSION SYSTEM ====================
    add_section(story, "5. Conversion System", styles)
    
    add_body(story, 
        "AlphaAI implements multiple conversion optimization techniques to maximize free-to-paid upgrades:", styles)
    
    add_subsection(story, "Delay Warning Banner", styles)
    add_body(story, 
        "Prominent yellow banner: 'Live signals update every minute — You are viewing a 15 minute delay'. "
        "Creates awareness of the limitation without being aggressive.", styles)
    
    add_subsection(story, "Strategic Upgrade Buttons", styles)
    add_bullets(story, [
        "Large gradient 'Unlock Live Signals' button with glow effect",
        "'Upgrade Now' button in demo mode banner",
        "'Upgrade to Pro' CTA card with feature comparison"
    ], styles)
    
    add_subsection(story, "Locked Features Preview", styles)
    add_body(story, 
        "Blurred cards showing 'Real-Time Alerts' and 'Advanced Analytics' with 'Pro Feature' overlay. "
        "Users can see what they're missing.", styles)
    
    add_subsection(story, "Timed Popup (2 Minutes)", styles)
    add_body(story, 
        "After 2 minutes on the dashboard, an upgrade modal appears with benefits and pricing. "
        "Catches engaged users at peak interest.", styles)
    
    add_subsection(story, "Exit Intent Popup", styles)
    add_body(story, 
        "When user's mouse leaves the viewport (indicating they may leave): 'Wait — unlock live signals before you go'. "
        "Shows what they're missing and active user count.", styles)
    
    add_subsection(story, "Social Proof Elements", styles)
    add_bullets(story, [
        "'27 users viewing signals right now' (randomizes 15-50)",
        "'Pro users received these signals in real-time' under signal history",
        "Active user count in exit popup"
    ], styles)
    
    add_subsection(story, "FOMO Triggers", styles)
    add_body(story, 
        "Under each signal: 'Signal triggered 12 mins ago → +1.6% — You missed this'. "
        "Updates every 20 seconds with realistic timestamps and gains.", styles)
    
    story.append(PageBreak())
    
    # ==================== 6. PRICING MODEL ====================
    add_section(story, "6. Pricing Model", styles)
    
    add_body(story, "AlphaAI offers three subscription tiers designed to maximize conversion and revenue:", styles)
    story.append(Spacer(1, 15))
    
    story.append(create_pricing_table())
    
    story.append(Spacer(1, 20))
    
    add_subsection(story, "Pricing Strategy", styles)
    add_bullets(story, [
        "<b>Free tier:</b> Provides genuine value but with friction (delay) to drive upgrades",
        "<b>Pro tier ($29/mo):</b> Sweet spot pricing for serious retail traders",
        "<b>Elite tier ($79/mo):</b> Premium offering for power users, 3x revenue per customer",
        "<b>Yearly option:</b> $249/year for Pro (Save $99) encourages longer commitments"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== 7. PAYMENT SYSTEM ====================
    add_section(story, "7. Payment System", styles)
    
    add_subsection(story, "Stripe Integration", styles)
    add_body(story, 
        "AlphaAI uses Stripe Checkout for secure, PCI-compliant payment processing. "
        "The integration supports credit cards and is extensible to crypto payments.", styles)
    
    add_subsection(story, "Checkout Flow", styles)
    add_numbered_list(story, [
        "User clicks 'Upgrade Now' button",
        "Selects plan (Monthly $29 or Yearly $249)",
        "Frontend requests checkout session from backend",
        "Backend creates Stripe session with success/cancel URLs",
        "User redirected to Stripe hosted checkout page",
        "After payment, redirected back to dashboard",
        "Frontend polls backend for payment confirmation",
        "Pro status activated immediately upon confirmation"
    ], styles)
    
    add_subsection(story, "Backend Endpoints", styles)
    add_bullets(story, [
        "<b>POST /api/payments/checkout</b> — Create checkout session",
        "<b>GET /api/payments/status/{session_id}</b> — Check payment status",
        "<b>GET /api/payments/packages</b> — List available packages",
        "<b>POST /api/webhook/stripe</b> — Handle Stripe webhooks"
    ], styles)
    
    add_subsection(story, "Data Storage", styles)
    add_body(story, 
        "Payment transactions are stored in MongoDB 'payment_transactions' collection with "
        "session ID, wallet address, amount, status, and timestamps.", styles)
    
    story.append(PageBreak())
    
    # ==================== 8. TECHNICAL ARCHITECTURE ====================
    add_section(story, "8. Technical Architecture", styles)
    
    story.append(create_tech_stack_table())
    
    story.append(Spacer(1, 20))
    
    add_subsection(story, "API Structure", styles)
    add_body(story, "The backend exposes RESTful APIs organized by domain:", styles)
    add_bullets(story, [
        "<b>/api/live-prices</b> — Real-time crypto prices from Kraken",
        "<b>/api/payments/*</b> — Subscription and billing endpoints",
        "<b>/api/users/*</b> — User management and Pro status",
        "<b>/api/simulation/*</b> — Paper trading simulation",
        "<b>/api/lab/*</b> — Strategy lab and backtesting",
        "<b>/api/fund/*</b> — Fund statistics and performance"
    ], styles)
    
    add_subsection(story, "Frontend Architecture", styles)
    add_body(story, 
        "Single-page React application with React Router for navigation. "
        "Uses Shadcn/UI component library for consistent, accessible UI elements. "
        "State management via React hooks and context.", styles)
    
    add_subsection(story, "Database Schema", styles)
    add_bullets(story, [
        "<b>investors</b> — User profiles, wallet addresses, Pro status",
        "<b>payment_transactions</b> — Stripe sessions, payment history",
        "<b>trades</b> — Paper trading history",
        "<b>strategies</b> — AI-generated trading strategies"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== 9. CURRENT LIMITATIONS ====================
    add_section(story, "9. Current Limitations", styles)
    
    add_body(story, 
        "Important: The following limitations should be clearly understood:", styles)
    
    story.append(Spacer(1, 10))
    
    limitations = [
        ("<b>Paper Trading Only</b>", 
         "All trading is simulated. No real trades are executed. Performance metrics are based on "
         "backtesting and paper trading simulations, not actual trading results."),
        ("<b>No Live Execution</b>", 
         "The platform does not connect to exchanges for live trading. Users must manually execute "
         "trades based on signals if they choose to act on them."),
        ("<b>Pro Features UI-Only</b>", 
         "Currently, Pro subscription removes the 15-minute delay indicator and unlocks UI features. "
         "Backend signal differentiation (actually faster signals) is not yet implemented."),
        ("<b>Smart Contract Not Deployed</b>", 
         "The AlphaAIManager.sol contract exists but is not deployed to any network. "
         "Web3 features are simulated."),
        ("<b>No User Authentication</b>", 
         "Authentication is wallet-based only. No email/password login system exists."),
        ("<b>Single Region</b>", 
         "Backend runs in a single region without global distribution or CDN."),
    ]
    
    for title, desc in limitations:
        story.append(Paragraph(title, styles['SubHeading']))
        story.append(Paragraph(desc, styles['CustomBody']))
        story.append(Spacer(1, 5))
    
    story.append(Spacer(1, 15))
    story.append(create_highlight_box(
        "<b>Disclaimer:</b> All performance data shown on the platform is from paper trading "
        "simulations and does not represent actual trading results. Past simulated performance "
        "is not indicative of future results."
    ))
    
    story.append(PageBreak())
    
    # ==================== 10. FUTURE ROADMAP ====================
    add_section(story, "10. Future Roadmap", styles)
    
    add_subsection(story, "Phase 1: Core Improvements (Q2 2026)", styles)
    add_bullets(story, [
        "Implement actual real-time signal differentiation for Pro users",
        "Deploy smart contract to Sepolia testnet for testing",
        "Add JWT-based user authentication",
        "Email notification system for alerts and receipts"
    ], styles)
    
    add_subsection(story, "Phase 2: Trading Integration (Q3 2026)", styles)
    add_bullets(story, [
        "Integrate with Uniswap V3 for live DEX trading",
        "Implement blockchain event listeners",
        "Add copy-trading functionality",
        "WebSocket real-time updates (replace polling)"
    ], styles)
    
    add_subsection(story, "Phase 3: Growth Features (Q4 2026)", styles)
    add_bullets(story, [
        "Referral program with revenue sharing",
        "Public leaderboard for top performers",
        "Mobile app (React Native)",
        "Additional cryptocurrency support"
    ], styles)
    
    add_subsection(story, "Phase 4: Scale (2027)", styles)
    add_bullets(story, [
        "Global CDN deployment",
        "Enterprise API tier",
        "Institutional features",
        "Regulatory compliance (where applicable)"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== 11. PERFORMANCE DATA ====================
    add_section(story, "11. Performance Data", styles)
    
    story.append(create_highlight_box(
        "<b>IMPORTANT:</b> All data below is from PAPER TRADING simulations only. "
        "These are not real trading results and should not be interpreted as such."
    ))
    
    story.append(Spacer(1, 20))
    
    add_subsection(story, "30-Day Performance Summary", styles)
    
    perf_data = [
        ['Metric', 'Value', 'Notes'],
        ['Total Return', '+12.4%', 'Simulated portfolio growth'],
        ['Win Rate', '68%', 'Profitable signals / Total signals'],
        ['Max Drawdown', '-4.2%', 'Largest peak-to-trough decline'],
        ['Total Signals', '847', 'Signals generated in period'],
        ['Avg Signal/Day', '28', 'Across all tracked assets'],
        ['Best Single Trade', '+4.2%', 'BTC BUY signal'],
        ['Worst Single Trade', '-1.8%', 'ETH SELL signal'],
    ]
    
    perf_table = Table(perf_data, colWidths=[1.8*inch, 1.5*inch, 2.7*inch])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(perf_table)
    
    story.append(Spacer(1, 20))
    
    add_subsection(story, "Recent Signal Examples", styles)
    
    signals_data = [
        ['Time', 'Asset', 'Signal', 'Result', 'Status'],
        ['2h ago', 'BTC', 'BUY', '+2.1%', '✓ Profitable'],
        ['4h ago', 'ETH', 'SELL', '+1.4%', '✓ Profitable'],
        ['6h ago', 'SOL', 'BUY', '+3.0%', '✓ Profitable'],
        ['8h ago', 'BTC', 'SELL', '+1.8%', '✓ Profitable'],
        ['12h ago', 'ETH', 'BUY', '-0.6%', '✗ Loss'],
    ]
    
    signals_table = Table(signals_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
    signals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(signals_table)
    
    story.append(PageBreak())
    
    # ==================== 12. BRANDING & POSITIONING ====================
    add_section(story, "12. Branding & Positioning", styles)
    
    add_subsection(story, "Brand Identity", styles)
    
    brand_data = [
        ['Element', 'Details'],
        ['Name', 'AlphaAI'],
        ['Tagline', 'AI-Powered Crypto Signals & Trading Insights'],
        ['Primary Color', '#7B61FF (Purple)'],
        ['Accent Color', '#00FF94 (Green)'],
        ['Typography', 'JetBrains Mono (data), System fonts (UI)'],
        ['Visual Style', 'Dark fintech, clean, minimal'],
    ]
    
    brand_table = Table(brand_data, colWidths=[2*inch, 4*inch])
    brand_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F3FF')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(brand_table)
    
    story.append(Spacer(1, 20))
    
    add_subsection(story, "Positioning Statement", styles)
    story.append(create_highlight_box(
        "<b>AlphaAI is NOT:</b><br/>"
        "• A hedge fund<br/>"
        "• A financial advisor<br/>"
        "• A guaranteed profit system<br/><br/>"
        "<b>AlphaAI IS:</b><br/>"
        "• An AI-powered signals platform<br/>"
        "• A decision-support tool<br/>"
        "• A SaaS subscription service"
    ))
    
    story.append(Spacer(1, 20))
    
    add_subsection(story, "Key Messaging", styles)
    add_bullets(story, [
        "Focus on <b>simplicity</b> — 'AI does the analysis, you make the decisions'",
        "Emphasize <b>accessibility</b> — 'Professional-grade insights for everyone'",
        "Highlight <b>transparency</b> — Clear labeling of paper trading data",
        "Build <b>trust</b> — Show consistent performance, not unrealistic promises"
    ], styles)
    
    # ==================== FINAL PAGE ====================
    story.append(PageBreak())
    story.append(Spacer(1, 100))
    
    story.append(Paragraph("Document Complete", styles['DocTitle']))
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "This document provides a comprehensive overview of the AlphaAI platform, "
        "its features, technical architecture, and business model.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "For questions or additional information, please contact the development team.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 50))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Footer']))
    story.append(Paragraph("AlphaAI Platform © 2026. All Rights Reserved.", styles['Footer']))
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_pdf()
