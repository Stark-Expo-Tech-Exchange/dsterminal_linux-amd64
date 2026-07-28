# create_pitch_deck.py
"""
DSTERMINAL INVESTOR PITCH DECK GENERATOR
Creates a professional PowerPoint presentation
Requires: pip install python-pptx
"""

import os
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

def create_dsterminal_pitch_deck():
    """Generate the complete DSTERMINAL pitch deck"""
    
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    
    # Color scheme
    DARK_BLUE = RGBColor(10, 20, 40)
    CYAN = RGBColor(0, 255, 255)
    WHITE = RGBColor(255, 255, 255)
    GREEN = RGBColor(0, 255, 100)
    GOLD = RGBColor(255, 215, 0)
    
    def add_slide(title, content_lines, slide_num=None):
        """Add a slide with title and content"""
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        
        # Title
        title_box = slide.shapes.title
        title_box.text = title
        title_box.text_frame.paragraphs[0].font.size = Pt(44)
        title_box.text_frame.paragraphs[0].font.bold = True
        title_box.text_frame.paragraphs[0].font.color.rgb = CYAN
        
        # Content
        content_box = slide.placeholders[1]
        tf = content_box.text_frame
        tf.text = "\n".join(content_lines)
        for para in tf.paragraphs:
            para.font.size = Pt(24)
            para.font.color.rgb = WHITE
            para.space_after = Pt(12)
        
        return slide
    
    # ============================================================
    # SLIDE 1: COVER
    # ============================================================
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank slide
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BLUE
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(11), Inches(2))
    tf = title_box.text_frame
    tf.text = "D S T E R M I N A L ®"
    tf.paragraphs[0].font.size = Pt(72)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = CYAN
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(11), Inches(1))
    tf2 = sub_box.text_frame
    tf2.text = "Next-Generation Cybersecurity Operations Platform"
    tf2.paragraphs[0].font.size = Pt(32)
    tf2.paragraphs[0].font.color.rgb = WHITE
    tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # Tagline
    tag_box = slide.shapes.add_textbox(Inches(1), Inches(5.2), Inches(11), Inches(0.8))
    tf3 = tag_box.text_frame
    tf3.text = "Enterprise-Grade Threat Intelligence & Incident Response"
    tf3.paragraphs[0].font.size = Pt(20)
    tf3.paragraphs[0].font.color.rgb = GOLD
    tf3.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # Footer
    footer_box = slide.shapes.add_textbox(Inches(1), Inches(6.8), Inches(11), Inches(0.5))
    tf4 = footer_box.text_frame
    tf4.text = "Malawi | Africa | Global"
    tf4.paragraphs[0].font.size = Pt(16)
    tf4.paragraphs[0].font.color.rgb = WHITE
    tf4.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # ============================================================
    # SLIDE 2: VISION & MISSION
    # ============================================================
    add_slide("🎯 Vision & Mission", [
        "VISION:",
        "To become Africa's leading cybersecurity operations platform,",
        "protecting critical digital infrastructure across the continent.",
        "",
        "MISSION:",
        "Empower organizations with enterprise-grade security tools,",
        "democratize threat intelligence, and build Africa's",
        "cybersecurity resilience through innovation and education."
    ])
    
    # ============================================================
    # SLIDE 3: THE PROBLEM
    # ============================================================
    add_slide("⚠️ The Problem", [
        "• African organizations face increasing cyber threats",
        "• Limited access to enterprise-grade security tools",
        "• High cost of commercial security solutions ($50K-$500K/year)",
        "• Shortage of skilled cybersecurity professionals",
        "• Slow incident response and threat detection",
        "• Growing ransomware attacks targeting African businesses",
        "• Compliance gaps in data protection regulations"
    ])
    
    # ============================================================
    # SLIDE 4: THE OPPORTUNITY
    # ============================================================
    add_slide("📈 The Opportunity", [
        "• Africa's cybersecurity market: $3.5B by 2026 (35% CAGR)",
        "• Malawi's digital economy rapidly expanding",
        "• 600+ financial institutions need protection",
        "• 200+ government agencies require security",
        "• 1,500+ businesses vulnerable to cyber attacks",
        "• 500,000+ individuals need security awareness",
        "• $2.5M available in grants and innovation funding"
    ])
    
    # ============================================================
    # SLIDE 5: THE SOLUTION
    # ============================================================
    add_slide("🚀 The Solution: DSTERMINAL®", [
        "ALL-IN-ONE CYBERSECURITY PLATFORM",
        "",
        "• Threat Intelligence",
        "• Vulnerability Assessment",
        "• Incident Response",
        "• Security Hardening",
        "• Compliance Management",
        "• Real-time Monitoring",
        "",
        "✅ Enterprise-grade • ✅ Open-source • ✅ Affordable"
    ])
    
    # ============================================================
    # SLIDE 6: PRODUCT MODULES
    # ============================================================
    add_slide("🔧 Product Modules", [
        "1️⃣ Threat Intelligence",
        "   • SQL Injection Detection & Prevention",
        "   • Real-time threat feeds",
        "   • Automated vulnerability scanning",
        "",
        "2️⃣ Security Hardening",
        "   • System hardening automation",
        "   • Compliance checking (CIS, NIST, ISO)",
        "   • Configuration management",
        "",
        "3️⃣ Incident Response",
        "   • Automated response playbooks",
        "   • Forensic analysis tools",
        "   • Real-time alerting"
    ])
    
    # ============================================================
    # SLIDE 7: TECHNOLOGY
    # ============================================================
    add_slide("⚡ Technology & Innovation", [
        "• Modular microservices architecture",
        "• AI-powered threat detection",
        "• Real-time telemetry collection",
        "• Cross-platform compatibility",
        "  (Windows, Linux, macOS)",
        "",
        "TECH STACK:",
        "• Python • Rust • Docker",
        "• ElasticSearch • Kafka • Redis",
        "• React • Node.js • PostgreSQL"
    ])
    
    # ============================================================
    # SLIDE 8: MARKET OPPORTUNITY
    # ============================================================
    add_slide("🌍 Market Opportunity (Malawi & Africa)", [
        "MALAWI MARKET:",
        "• 40+ banks and financial institutions",
        "• 200+ government agencies",
        "• 500+ SMEs with digital presence",
        "• 100+ educational institutions",
        "",
        "AFRICAN MARKET:",
        "• 54 countries",
        "• 1.4B population",
        "• $3.5B cybersecurity market by 2026",
        "• 35% annual growth rate"
    ])
    
    # ============================================================
    # SLIDE 9: BUSINESS MODEL
    # ============================================================
    add_slide("💰 Business Model", [
        "1. SUBSCRIPTION TIERS:",
        "   • Free Tier: Basic security (5 users)",
        "   • Pro Tier: $99/month (50 users)",
        "   • Enterprise Tier: $499/month (Unlimited)",
        "",
        "2. ONE-TIME SERVICES:",
        "   • Implementation & Training: $5,000",
        "   • Custom Development: $15,000+",
        "   • Security Audit: $2,500",
        "",
        "3. PARTNERSHIPS:",
        "   • Reseller Program (30% commission)",
        "   • Strategic Alliances"
    ])
    
    # ============================================================
    # SLIDE 10: COMPETITIVE ADVANTAGE
    # ============================================================
    add_slide("🏆 Competitive Advantage", [
        "VS TRADITIONAL SOLUTIONS:",
        "",
        "DSTERMINAL vs Competitors:",
        "✅ 90% lower cost than commercial solutions",
        "✅ Open-source transparency",
        "✅ Local support and customization",
        "✅ African-focused threat intelligence",
        "✅ Multi-platform compatibility",
        "✅ Zero vendor lock-in",
        "",
        "DIFFERENTIATORS:",
        "• African cybersecurity expertise",
        "• Community-driven development"
    ])
    
    # ============================================================
    # SLIDE 11: GO-TO-MARKET STRATEGY
    # ============================================================
    add_slide("🚀 Go-to-Market Strategy", [
        "PHASE 1: Malawi Launch (Q1 2025)",
        "• Beta testing with 20 enterprises",
        "• Strategic partnerships with ISPs",
        "• Government cybersecurity program",
        "",
        "PHASE 2: Regional Expansion (Q3 2025)",
        "• Zambia, Zimbabwe, Tanzania",
        "• Regional reseller network",
        "",
        "PHASE 3: Continental Scale (2026)",
        "• East and West Africa",
        "• Pan-African partnerships",
        "",
        "CHANNELS:",
        "Direct Sales • Resellers • Online • Government"
    ])
    
    # ============================================================
    # SLIDE 12: TRACTION
    # ============================================================
    add_slide("📊 Traction & Current Stage", [
        "CURRENT STATUS:",
        "• MVP launched and validated",
        "• 25 enterprise beta users",
        "• 300+ individual users",
        "• 95% user satisfaction rate",
        "",
        "MILESTONES ACHIEVED:",
        "• Product architecture design",
        "• Core security modules built",
        "• SQL injection detection (98% accuracy)",
        "• Automated hardening (CIS compliance)",
        "",
        "NEXT MILESTONES:",
        "• Enterprise scalability testing",
        "• SOC integration"
    ])
    
    # ============================================================
    # SLIDE 13: ROADMAP
    # ============================================================
    add_slide("🗺️ Product Roadmap", [
        "Q1 2025: Malawi Launch",
        "• Finalize MVP",
        "• Onboard 20 enterprise clients",
        "• Establish local support",
        "",
        "Q2 2025: Feature Expansion",
        "• AI-powered threat detection",
        "• Compliance automation",
        "• Mobile app release",
        "",
        "Q3 2025: Regional Expansion",
        "• Zambia & Zimbabwe launch",
        "• Regional partnerships",
        "",
        "Q4 2025: Enterprise Scale",
        "• Full SOC integration",
        "• Advanced analytics"
    ])
    
    # ============================================================
    # SLIDE 14: FUNDING REQUEST
    # ============================================================
    add_slide("💎 Funding Request", [
        "RAISING: $1.5M",
        "",
        "USE OF FUNDS:",
        "• Product Development: 40%",
        "• Sales & Marketing: 25%",
        "• Team Expansion: 20%",
        "• Operations: 10%",
        "• Contingency: 5%",
        "",
        "INVESTMENT STRUCTURE:",
        "• Seed Round: $500K",
        "• Series A: $1M",
        "",
        "VALUATION: $5M Pre-money"
    ])
    
    # ============================================================
    # SLIDE 15: USE OF FUNDS
    # ============================================================
    add_slide("📋 Use of Funds", [
        "PRODUCT DEVELOPMENT ($600K):",
        "• Core platform enhancements",
        "• AI/ML integration",
        "• Mobile app development",
        "• Security hardening tools",
        "",
        "SALES & MARKETING ($375K):",
        "• Direct sales team",
        "• Digital marketing campaign",
        "• Regional roadshows",
        "",
        "TEAM EXPANSION ($300K):",
        "• 3 developers",
        "• 2 sales professionals",
        "• 1 product manager",
        "",
        "OPERATIONS ($150K):",
        "• Cloud infrastructure",
        "• Support team",
        "• Office expansion"
    ])
    
    # ============================================================
    # SLIDE 16: FINANCIAL PROJECTIONS
    # ============================================================
    add_slide("📊 Financial Projections", [
        "REVENUE PROJECTIONS:",
        "• Year 1 (2025): $250K",
        "• Year 2 (2026): $1.2M",
        "• Year 3 (2027): $3.5M",
        "• Year 4 (2028): $7.8M",
        "",
        "KEY METRICS:",
        "• Customer Acquisition Cost: $500",
        "• Lifetime Value: $15,000",
        "• Churn Rate: <5%",
        "• Gross Margin: 75%",
        "",
        "BREAK-EVEN:",
        "• By end of Year 2"
    ])
    
    # ============================================================
    # SLIDE 17: IMPACT
    # ============================================================
    add_slide("🌟 Impact", [
        "SECURITY IMPACT:",
        "• Protect 1M+ digital assets",
        "• Prevent $500M+ in cyber losses",
        "• Build African cybersecurity capacity",
        "",
        "SOCIAL IMPACT:",
        "• Create 50+ jobs",
        "• Train 1,000+ cybersecurity professionals",
        "• Develop local cybersecurity talent",
        "",
        "ECONOMIC IMPACT:",
        "• $10M+ in economic value",
        "• Support 500+ organizations",
        "• Strengthen Malawi's digital economy"
    ])
    
    # ============================================================
    # SLIDE 18: TEAM
    # ============================================================
    add_slide("👥 The Team", [
        "FOUNDER & CEO:",
        "• 10+ years cybersecurity experience",
        "• Former Security Architect at major bank",
        "• Certified Ethical Hacker (CEH)",
        "",
        "KEY HIRES:",
        "• Lead Developer - Full-stack expert",
        "• Security Engineer - Penetration testing",
        "• Product Manager - SaaS experience",
        "• Sales Director - Enterprise sales",
        "",
        "ADVISORS:",
        "• Senior cybersecurity experts",
        "• African tech ecosystem leaders"
    ])
    
    # ============================================================
    # SLIDE 19: WHY INVEST
    # ============================================================
    add_slide("💡 Why Invest in DSTERMINAL", [
        "1. 💰 MASSIVE MARKET OPPORTUNITY",
        "   • African cybersecurity market: $3.5B",
        "   • 35% annual growth",
        "",
        "2. 🚀 PROVEN PRODUCT",
        "   • 95% user satisfaction",
        "   • Working MVP with 25 enterprise clients",
        "",
        "3. 🏆 COMPETITIVE ADVANTAGE",
        "   • 90% lower cost than competitors",
        "   • African-focused threat intelligence",
        "",
        "4. 💎 EXPERIENCED TEAM",
        "   • Deep cybersecurity expertise",
        "   • Strong industry connections",
        "",
        "5. 📈 SCALABLE BUSINESS MODEL",
        "   • Recurring revenue",
        "   • Expandable to 54 African countries"
    ])
    
    # ============================================================
    # SLIDE 20: CLOSING
    # ============================================================
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BLUE
    
    # Main text
    close_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(11), Inches(4))
    tf = close_box.text_frame
    tf.text = "Join us in securing Africa's\n\n"
    tf.paragraphs[0].font.size = Pt(48)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = WHITE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    tf2 = tf.add_paragraph()
    tf2.text = "digital future"
    tf2.font.size = Pt(48)
    tf2.font.bold = True
    tf2.font.color.rgb = CYAN
    tf2.alignment = PP_ALIGN.CENTER
    
    # Contact
    contact_box = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(11), Inches(1.5))
    tf3 = contact_box.text_frame
    tf3.text = "📧 info@dsterminal.com\n📞 +265 111 222 333\n🌐 www.dsterminal.com"
    tf3.paragraphs[0].font.size = Pt(24)
    tf3.paragraphs[0].font.color.rgb = GOLD
    tf3.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # ============================================================
    # SAVE
    # ============================================================
    output_file = f"DSTERMINAL_Pitch_Deck_{datetime.now().strftime('%Y%m%d')}.pptx"
    prs.save(output_file)
    print(f"✅ Pitch deck created successfully!")
    print(f"📁 File: {output_file}")
    print(f"📊 Slides: {len(prs.slides)}")
    return output_file

if __name__ == "__main__":
    # Install required package if missing
    try:
        import pptx
    except ImportError:
        print("📦 Installing python-pptx...")
        os.system("pip install python-pptx")
        import pptx
    
    create_dsterminal_pitch_deck()