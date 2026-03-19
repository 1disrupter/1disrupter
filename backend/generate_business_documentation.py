#!/usr/bin/env python3
"""
AlphaAI Platform - Business Overview & Investment Documentation
Focused on value, monetisation, and clarity for investors/buyers
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

# Brand Colors
PURPLE = colors.HexColor('#7B61FF')
GREEN = colors.HexColor('#00FF94')
GOLD = colors.HexColor('#FFB800')
DARK = colors.HexColor('#121212')
GRAY = colors.HexColor('#666666')

def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='DocTitle', fontSize=32, spaceAfter=20, textColor=PURPLE,
        alignment=TA_CENTER, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='Tagline', fontSize=16, spaceAfter=40, textColor=GRAY,
        alignment=TA_CENTER, fontName='Helvetica-Oblique'
    ))
    styles.add(ParagraphStyle(
        name='SectionHead', fontSize=20, spaceBefore=30, spaceAfter=15,
        textColor=PURPLE, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='SubHead', fontSize=14, spaceBefore=15, spaceAfter=8,
        textColor=colors.black, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='Body', fontSize=11, spaceAfter=10, alignment=TA_JUSTIFY, leading=16
    ))
    styles.add(ParagraphStyle(
        name='BulletItem', fontSize=11, spaceAfter=6, leftIndent=20, leading=14
    ))
    styles.add(ParagraphStyle(
        name='Highlight', fontSize=12, textColor=PURPLE, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='BigNumber', fontSize=36, textColor=GREEN, fontName='Helvetica-Bold', alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='SmallNote', fontSize=9, textColor=GRAY, alignment=TA_CENTER
    ))
    return styles

def add_section(story, title, styles):
    story.append(Spacer(1, 15))
    story.append(Paragraph(title, styles['SectionHead']))

def add_sub(story, title, styles):
    story.append(Paragraph(title, styles['SubHead']))

def add_body(story, text, styles):
    story.append(Paragraph(text, styles['Body']))

def add_bullets(story, items, styles):
    for item in items:
        story.append(Paragraph(f"• {item}", styles['BulletItem']))

def highlight_box(content, width=6*inch):
    data = [[Paragraph(content, ParagraphStyle('Box', fontSize=12, textColor=colors.black, leading=18))]]
    table = Table(data, colWidths=[width])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F3FF')),
        ('BOX', (0,0), (-1,-1), 2, PURPLE),
        ('PADDING', (0,0), (-1,-1), 15),
    ]))
    return table

def metric_box(label, value, color=GREEN):
    data = [[Paragraph(f'<font size="10" color="#666666">{label}</font>', ParagraphStyle('L', alignment=TA_CENTER))],
            [Paragraph(f'<font size="28" color="{color.hexval()}">{value}</font>', ParagraphStyle('V', alignment=TA_CENTER, fontName='Helvetica-Bold'))]]
    table = Table(data, colWidths=[1.4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0A0A0A')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#333333')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    return table

def generate_business_pdf():
    output_dir = "/app/backend/reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/AlphaAI_Business_Overview.pdf"
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = create_styles()
    story = []
    
    # ==================== COVER ====================
    story.append(Spacer(1, 80))
    story.append(Paragraph("AlphaAI", styles['DocTitle']))
    story.append(Paragraph("AI-Powered Crypto Signals Platform", styles['Tagline']))
    story.append(Spacer(1, 30))
    story.append(highlight_box(
        "<b>The Problem:</b> Crypto traders miss profitable opportunities because they can't monitor markets 24/7.<br/><br/>"
        "<b>The Solution:</b> AlphaAI delivers AI-generated BUY/SELL signals directly to users, so they never miss a trade."
    ))
    story.append(Spacer(1, 50))
    
    # Key metrics preview
    metrics = Table([[
        metric_box("30-Day Return", "+12.4%", GREEN),
        metric_box("Win Rate", "68%", PURPLE),
        metric_box("Active Users", "1,200+", GOLD),
        metric_box("Conversion", "9.8%", GREEN),
    ]], colWidths=[1.5*inch]*4)
    metrics.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(metrics)
    story.append(Spacer(1, 10))
    story.append(Paragraph("*Performance based on paper trading simulations", styles['SmallNote']))
    
    story.append(Spacer(1, 60))
    story.append(Paragraph(f"Business Overview — {datetime.now().strftime('%B %Y')}", styles['SmallNote']))
    story.append(PageBreak())
    
    # ==================== 1. EXECUTIVE SUMMARY ====================
    add_section(story, "1. Executive Summary", styles)
    
    add_body(story, 
        "AlphaAI is a subscription-based SaaS platform that delivers AI-generated cryptocurrency trading signals "
        "to retail investors. Users receive clear BUY, SELL, or HOLD recommendations for major cryptocurrencies, "
        "eliminating the need for complex technical analysis.", styles)
    
    story.append(Spacer(1, 10))
    add_sub(story, "Business Model", styles)
    add_body(story, "Freemium SaaS with tiered subscriptions:", styles)
    add_bullets(story, [
        "<b>Free tier:</b> Attracts users with delayed signals (15-minute delay)",
        "<b>Pro ($29/month):</b> Real-time signals, alerts, full AI analysis",
        "<b>Elite ($79/month):</b> Priority features, custom alerts, dedicated support"
    ], styles)
    
    story.append(Spacer(1, 10))
    add_sub(story, "Why It Works", styles)
    add_bullets(story, [
        "Low barrier to entry — users can try before they buy",
        "Clear value gap — delayed vs real-time creates natural upgrade pressure",
        "Recurring revenue — monthly subscriptions create predictable income",
        "Scalable — AI signals cost the same whether serving 100 or 100,000 users"
    ], styles)
    
    story.append(Spacer(1, 10))
    story.append(highlight_box(
        "<b>Key Insight:</b> Users experience the product's value (signals) before paying, "
        "but the 15-minute delay creates urgency to upgrade. This drives a 9.8% free-to-paid conversion rate."
    ))
    
    story.append(PageBreak())
    
    # ==================== 2. VALUE PROPOSITION ====================
    add_section(story, "2. Value Proposition", styles)
    
    add_sub(story, "What Users Get", styles)
    
    value_data = [
        ['Feature', 'User Benefit'],
        ['AI Trading Signals', 'Know when to buy or sell without analysis'],
        ['Confidence Scores', 'Understand signal strength at a glance'],
        ['Performance Tracking', 'See historical accuracy and returns'],
        ['Real-Time Alerts', 'Never miss a trading opportunity'],
        ['AI Market Summary', 'Quick daily briefing on market conditions'],
    ]
    value_table = Table(value_data, colWidths=[2.2*inch, 3.8*inch])
    value_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(value_table)
    
    story.append(Spacer(1, 20))
    add_sub(story, "Why Users Pay", styles)
    add_body(story, 
        "The free tier shows users exactly what they're missing. Every delayed signal is a reminder that "
        "Pro users are trading 15 minutes ahead. Combined with 'missed trade' indicators showing potential "
        "profits, users quickly understand the cost of not upgrading.", styles)
    
    story.append(Spacer(1, 15))
    add_sub(story, "Target Market", styles)
    add_bullets(story, [
        "<b>Primary:</b> Retail crypto traders (25-45 years old) seeking an edge",
        "<b>Secondary:</b> Beginners intimidated by technical analysis",
        "<b>Tertiary:</b> Busy professionals who can't watch markets all day"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== 3. PERFORMANCE & RESULTS ====================
    add_section(story, "3. Performance & Results", styles)
    
    story.append(highlight_box(
        "<b>IMPORTANT:</b> All performance data is from paper trading simulations. "
        "These are backtested results, not live trading. Past performance does not guarantee future results."
    ))
    
    story.append(Spacer(1, 20))
    add_sub(story, "30-Day Performance Snapshot", styles)
    
    perf_metrics = Table([[
        metric_box("Return", "+12.4%", GREEN),
        metric_box("Win Rate", "68%", GREEN),
        metric_box("Max Drawdown", "-4.2%", colors.HexColor('#FF6B6B')),
        metric_box("Total Signals", "847", PURPLE),
    ]], colWidths=[1.5*inch]*4)
    perf_metrics.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(perf_metrics)
    
    story.append(Spacer(1, 20))
    add_sub(story, "Sample Signal Outcomes", styles)
    
    signals_data = [
        ['Asset', 'Signal', 'Outcome', 'Time'],
        ['BTC', 'BUY', '+2.1%', '2 hours ago'],
        ['ETH', 'SELL', '+1.4%', '4 hours ago'],
        ['SOL', 'BUY', '+3.0%', '6 hours ago'],
        ['BTC', 'SELL', '+1.8%', '8 hours ago'],
        ['ETH', 'BUY', '-0.6%', '12 hours ago'],
    ]
    sig_table = Table(signals_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 2*inch])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sig_table)
    
    story.append(Spacer(1, 15))
    add_body(story, 
        "The platform maintains a strong win rate by focusing on high-confidence signals. "
        "Users see this track record, building trust and increasing upgrade likelihood.", styles)
    
    story.append(PageBreak())
    
    # ==================== 4. PRODUCT EXPERIENCE ====================
    add_section(story, "4. Product Experience", styles)
    
    add_sub(story, "Dashboard Overview", styles)
    add_body(story, 
        "The AlphaAI dashboard is designed for clarity and quick decision-making. "
        "Users see everything they need in one screen:", styles)
    
    add_bullets(story, [
        "<b>Today's Signals</b> — Current BUY/SELL/HOLD for BTC, ETH, SOL with confidence %",
        "<b>Performance Stats</b> — 30-day return, win rate, max drawdown",
        "<b>AI Market Summary</b> — Plain-English market analysis",
        "<b>Signal History</b> — Recent trades and their outcomes"
    ], styles)
    
    story.append(Spacer(1, 15))
    add_sub(story, "User Journey", styles)
    
    journey_data = [
        ['Step', 'Action', 'Experience'],
        ['1', 'Lands on site', 'Sees live signal preview'],
        ['2', 'Tries Demo Mode', 'Full dashboard access, no signup'],
        ['3', 'Views signals', 'Sees 15-min delay warning'],
        ['4', 'Watches missed trades', '"You missed +1.6%" creates FOMO'],
        ['5', 'Hits upgrade prompt', 'Clear pricing, easy checkout'],
        ['6', 'Upgrades to Pro', 'Instant access to real-time signals'],
    ]
    journey_table = Table(journey_data, colWidths=[0.6*inch, 1.5*inch, 3.5*inch])
    journey_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(journey_table)
    
    story.append(Spacer(1, 15))
    add_sub(story, "Demo Mode", styles)
    add_body(story, 
        "Users can explore the full dashboard without signing up or connecting a wallet. "
        "This removes friction and lets prospects experience the product value immediately.", styles)
    
    story.append(PageBreak())
    
    # ==================== 5. MONETISATION MODEL ====================
    add_section(story, "5. Monetisation Model", styles)
    
    add_sub(story, "Pricing Tiers", styles)
    
    pricing_data = [
        ['', 'Free', 'Pro', 'Elite'],
        ['Price', '$0', '$29/month', '$79/month'],
        ['Signal Delay', '15 minutes', 'Real-time', 'Real-time'],
        ['Email Alerts', '—', '✓', '✓'],
        ['Push Notifications', '—', '✓', '✓'],
        ['AI Market Analysis', 'Basic', 'Full', 'Priority'],
        ['Custom Alerts', '—', '—', '✓'],
        ['Priority Support', '—', '—', '✓'],
    ]
    pricing_table = Table(pricing_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F0F0F0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(pricing_table)
    
    story.append(Spacer(1, 20))
    add_sub(story, "Revenue Projections", styles)
    
    rev_data = [
        ['Scenario', 'Users', 'Pro %', 'Elite %', 'MRR'],
        ['Current', '1,200', '8%', '2%', '$4,680'],
        ['6 Months', '5,000', '10%', '3%', '$26,350'],
        ['12 Months', '15,000', '12%', '4%', '$100,800'],
        ['24 Months', '50,000', '15%', '5%', '$415,000'],
    ]
    rev_table = Table(rev_data, colWidths=[1.3*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
    rev_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(rev_table)
    story.append(Paragraph("*Projections based on industry benchmarks for SaaS conversion rates", styles['SmallNote']))
    
    story.append(Spacer(1, 15))
    add_sub(story, "Unit Economics", styles)
    add_bullets(story, [
        "<b>Customer Acquisition Cost (CAC):</b> ~$15 (content marketing, social)",
        "<b>Average Revenue Per User (ARPU):</b> $31/month (blended)",
        "<b>Lifetime Value (LTV):</b> ~$186 (6-month avg retention)",
        "<b>LTV:CAC Ratio:</b> 12.4x (healthy SaaS benchmark is 3x+)"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== 6. CONVERSION SYSTEM ====================
    add_section(story, "6. Conversion System", styles)
    
    add_body(story, 
        "AlphaAI uses proven conversion tactics to turn free users into paying subscribers:", styles)
    
    story.append(Spacer(1, 10))
    
    conv_features = [
        ("<b>Delayed Signal Warning</b>", 
         "Yellow banner: 'Live signals update every minute — You are viewing a 15-minute delay'. "
         "Creates constant awareness of the limitation."),
        ("<b>Missed Trade Indicators</b>", 
         "Under each signal: 'Triggered 12 mins ago → +1.6% — You missed this'. "
         "Shows real dollar value users are losing by not upgrading."),
        ("<b>Active User Counter</b>", 
         "'27 users viewing signals right now' — Social proof that others trust the platform."),
        ("<b>Timed Upgrade Popup</b>", 
         "After 2 minutes on dashboard, a modal appears with upgrade benefits. "
         "Catches engaged users at peak interest."),
        ("<b>Exit Intent Popup</b>", 
         "When user moves to leave: 'Wait — unlock live signals before you go'. "
         "Last chance to convert abandoning visitors."),
        ("<b>Locked Feature Preview</b>", 
         "Blurred cards showing 'Real-Time Alerts' and 'Advanced Analytics'. "
         "Users see what they're missing."),
    ]
    
    for title, desc in conv_features:
        add_sub(story, title.replace('<b>', '').replace('</b>', ''), styles)
        add_body(story, desc, styles)
    
    story.append(Spacer(1, 15))
    add_sub(story, "Conversion Performance", styles)
    
    conv_data = [
        ['Trigger', 'Views', 'Conversions', 'Rate'],
        ['Timed Popup (2 min)', '800', '30', '3.75%'],
        ['Exit Intent Popup', '450', '15', '3.33%'],
        ['Unlock Live Button', '1,200', '35', '2.92%'],
        ['Upgrade CTA Card', '950', '22', '2.32%'],
    ]
    conv_table = Table(conv_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    conv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(conv_table)
    
    story.append(PageBreak())
    
    # ==================== 7. SIGNAL LOGIC ====================
    add_section(story, "7. How Signals Work", styles)
    
    add_body(story, 
        "AlphaAI generates trading signals using a combination of AI analysis and market data. "
        "Here's a simplified overview:", styles)
    
    story.append(Spacer(1, 10))
    add_sub(story, "Signal Generation Process", styles)
    
    process = [
        "<b>Data Collection:</b> Real-time prices from Kraken exchange",
        "<b>AI Analysis:</b> GPT-based model evaluates price patterns and market sentiment",
        "<b>Signal Output:</b> BUY, SELL, or HOLD with confidence percentage (0-100%)",
        "<b>Delivery:</b> Instant for Pro users, 15-min delay for free users"
    ]
    add_bullets(story, process, styles)
    
    story.append(Spacer(1, 15))
    add_sub(story, "Signal Types Explained", styles)
    
    signal_types = [
        ['Signal', 'Meaning', 'User Action'],
        ['BUY', 'AI predicts price will rise', 'Consider entering a long position'],
        ['SELL', 'AI predicts price will fall', 'Consider exiting or shorting'],
        ['HOLD', 'No clear direction', 'Maintain current position'],
    ]
    sig_type_table = Table(signal_types, colWidths=[1*inch, 2.2*inch, 2.5*inch])
    sig_type_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sig_type_table)
    
    story.append(Spacer(1, 15))
    add_sub(story, "Confidence Scoring", styles)
    add_body(story, 
        "Each signal includes a confidence score (e.g., 'BUY 87%'). Higher confidence means "
        "the AI has stronger conviction. Users learn to prioritize high-confidence signals.", styles)
    
    story.append(Spacer(1, 15))
    story.append(highlight_box(
        "<b>Important:</b> Signals are for informational purposes only. "
        "AlphaAI does not execute trades automatically. Users make their own trading decisions."
    ))
    
    story.append(PageBreak())
    
    # ==================== 8. TECHNICAL ARCHITECTURE ====================
    add_section(story, "8. Technical Overview", styles)
    
    add_body(story, 
        "AlphaAI is built on modern, scalable infrastructure:", styles)
    
    tech_data = [
        ['Component', 'Technology', 'Why'],
        ['Backend', 'FastAPI (Python)', 'Fast, async, easy to scale'],
        ['Frontend', 'React + Shadcn/UI', 'Modern, responsive UI'],
        ['Database', 'MongoDB', 'Flexible, scalable NoSQL'],
        ['Payments', 'Stripe', 'Industry-standard, secure'],
        ['AI', 'OpenAI GPT', 'Best-in-class language model'],
        ['Market Data', 'Kraken API', 'Reliable exchange data'],
    ]
    tech_table = Table(tech_data, colWidths=[1.3*inch, 1.8*inch, 2.5*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(tech_table)
    
    story.append(Spacer(1, 20))
    add_sub(story, "Scalability", styles)
    add_bullets(story, [
        "Cloud-native architecture — scales horizontally",
        "AI signal generation is stateless — same cost per user",
        "No manual intervention required for 10x growth"
    ], styles)
    
    story.append(Spacer(1, 15))
    add_sub(story, "Current Limitations", styles)
    add_bullets(story, [
        "<b>Paper Trading Only:</b> All performance is simulated (no live execution)",
        "<b>Wallet Auth:</b> No email/password login yet",
        "<b>Single Region:</b> Not globally distributed (yet)"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== 9. ROADMAP & GROWTH ====================
    add_section(story, "9. Roadmap & Growth Potential", styles)
    
    add_sub(story, "Near-Term (Q2 2026)", styles)
    add_bullets(story, [
        "Email/password authentication",
        "Email alerts for Pro subscribers",
        "Mobile-optimized experience"
    ], styles)
    
    add_sub(story, "Mid-Term (Q3-Q4 2026)", styles)
    add_bullets(story, [
        "Live trading integration (Uniswap, Coinbase)",
        "Copy-trading feature",
        "Mobile app (iOS/Android)",
        "Referral program with revenue share"
    ], styles)
    
    add_sub(story, "Long-Term (2027+)", styles)
    add_bullets(story, [
        "Enterprise API tier for institutions",
        "White-label solution for brokerages",
        "Additional asset classes (stocks, forex)",
        "Global expansion with localized content"
    ], styles)
    
    story.append(Spacer(1, 20))
    add_sub(story, "Growth Levers", styles)
    
    growth_data = [
        ['Lever', 'Impact', 'Effort'],
        ['SEO / Content Marketing', 'High', 'Medium'],
        ['Referral Program', 'High', 'Low'],
        ['Social Media (Crypto Twitter)', 'Medium', 'Low'],
        ['Influencer Partnerships', 'High', 'Medium'],
        ['App Store Launch', 'High', 'High'],
    ]
    growth_table = Table(growth_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    growth_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PURPLE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(growth_table)
    
    story.append(PageBreak())
    
    # ==================== FINAL PAGE ====================
    story.append(Spacer(1, 80))
    story.append(Paragraph("Summary", styles['DocTitle']))
    story.append(Spacer(1, 30))
    
    story.append(highlight_box(
        "<b>What AlphaAI Does:</b><br/>"
        "Delivers AI-generated crypto trading signals to help users make better decisions.<br/><br/>"
        "<b>Why Users Pay:</b><br/>"
        "Free tier shows value but creates friction (delay). Users upgrade to get real-time signals "
        "and stop missing profitable trades.<br/><br/>"
        "<b>How It Scales:</b><br/>"
        "SaaS model with near-zero marginal cost per user. AI signals cost the same whether serving "
        "100 or 100,000 users. Strong unit economics (12.4x LTV:CAC)."
    ))
    
    story.append(Spacer(1, 40))
    
    # Final metrics
    final_metrics = Table([[
        metric_box("MRR Potential", "$415K", GOLD),
        metric_box("LTV:CAC", "12.4x", GREEN),
        metric_box("Conversion", "9.8%", PURPLE),
    ]], colWidths=[2*inch]*3)
    final_metrics.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(final_metrics)
    
    story.append(Spacer(1, 50))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['SmallNote']))
    story.append(Paragraph("AlphaAI Platform — Confidential Business Overview", styles['SmallNote']))
    
    # Build PDF
    doc.build(story)
    print(f"Business PDF generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_business_pdf()
