#!python
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
    tf.text = "D S T E R M I N A L Â®"
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
    add_slide("ðŸŽ¯ Vision & Mission", [
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
    add_slide("âš ï¸ The Problem", [
        "â€¢ African organizations face increasing cyber threats",
        "â€¢ Limited access to enterprise-grade security tools",
        "â€¢ High cost of commercial security solutions ($50K-$500K/year)",
        "â€¢ Shortage of skilled cybersecurity professionals",
        "â€¢ Slow incident response and threat detection",
        "â€¢ Growing ransomware attacks targeting African businesses",
        "â€¢ Compliance gaps in data protection regulations"
    ])
    
    # ============================================================
    # SLIDE 4: THE OPPORTUNITY
    # ============================================================
    add_slide("ðŸ“ˆ The Opportunity", [
        "â€¢ Africa's cybersecurity market: $3.5B by 2026 (35% CAGR)",
        "â€¢ Malawi's digital economy rapidly expanding",
        "â€¢ 600+ financial institutions need protection",
        "â€¢ 200+ government agencies require security",
        "â€¢ 1,500+ businesses vulnerable to cyber attacks",
        "â€¢ 500,000+ individuals need security awareness",
        "â€¢ $2.5M available in grants and innovation funding"
    ])
    
    # ============================================================
    # SLIDE 5: THE SOLUTION
    # ============================================================
    add_slide("ðŸš€ The Solution: DSTERMINALÂ®", [
        "ALL-IN-ONE CYBERSECURITY PLATFORM",
        "",
        "â€¢ Threat Intelligence",
        "â€¢ Vulnerability Assessment",
        "â€¢ Incident Response",
        "â€¢ Security Hardening",
        "â€¢ Compliance Management",
        "â€¢ Real-time Monitoring",
        "",
        "âœ… Enterprise-grade â€¢ âœ… Open-source â€¢ âœ… Affordable"
    ])
    
    # ============================================================
    # SLIDE 6: PRODUCT MODULES
    # ============================================================
    add_slide("ðŸ”§ Product Modules", [
        "1ï¸âƒ£ Threat Intelligence",
        "   â€¢ SQL Injection Detection & Prevention",
        "   â€¢ Real-time threat feeds",
        "   â€¢ Automated vulnerability scanning",
        "",
        "2ï¸âƒ£ Security Hardening",
        "   â€¢ System hardening automation",
        "   â€¢ Compliance checking (CIS, NIST, ISO)",
        "   â€¢ Configuration management",
        "",
        "3ï¸âƒ£ Incident Response",
        "   â€¢ Automated response playbooks",
        "   â€¢ Forensic analysis tools",
        "   â€¢ Real-time alerting"
    ])
    
    # ============================================================
    # SLIDE 7: TECHNOLOGY
    # ============================================================
    add_slide("âš¡ Technology & Innovation", [
        "â€¢ Modular microservices architecture",
        "â€¢ AI-powered threat detection",
        "â€¢ Real-time telemetry collection",
        "â€¢ Cross-platform compatibility",
        "  (Windows, Linux, macOS)",
        "",
        "TECH STACK:",
        "â€¢ Python â€¢ Rust â€¢ Docker",
        "â€¢ ElasticSearch â€¢ Kafka â€¢ Redis",
        "â€¢ React â€¢ Node.js â€¢ PostgreSQL"
    ])
    
    # ============================================================
    # SLIDE 8: MARKET OPPORTUNITY
    # ============================================================
    add_slide("ðŸŒ Market Opportunity (Malawi & Africa)", [
        "MALAWI MARKET:",
        "â€¢ 40+ banks and financial institutions",
        "â€¢ 200+ government agencies",
        "â€¢ 500+ SMEs with digital presence",
        "â€¢ 100+ educational institutions",
        "",
        "AFRICAN MARKET:",
        "â€¢ 54 countries",
        "â€¢ 1.4B population",
        "â€¢ $3.5B cybersecurity market by 2026",
        "â€¢ 35% annual growth rate"
    ])
    
    # ============================================================
    # SLIDE 9: BUSINESS MODEL
    # ============================================================
    add_slide("ðŸ’° Business Model", [
        "1. SUBSCRIPTION TIERS:",
        "   â€¢ Free Tier: Basic security (5 users)",
        "   â€¢ Pro Tier: $99/month (50 users)",
        "   â€¢ Enterprise Tier: $499/month (Unlimited)",
        "",
        "2. ONE-TIME SERVICES:",
        "   â€¢ Implementation & Training: $5,000",
        "   â€¢ Custom Development: $15,000+",
        "   â€¢ Security Audit: $2,500",
        "",
        "3. PARTNERSHIPS:",
        "   â€¢ Reseller Program (30% commission)",
        "   â€¢ Strategic Alliances"
    ])
    
    # ============================================================
    # SLIDE 10: COMPETITIVE ADVANTAGE
    # ============================================================
    add_slide("ðŸ† Competitive Advantage", [
        "VS TRADITIONAL SOLUTIONS:",
        "",
        "DSTERMINAL vs Competitors:",
        "âœ… 90% lower cost than commercial solutions",
        "âœ… Open-source transparency",
        "âœ… Local support and customization",
        "âœ… African-focused threat intelligence",
        "âœ… Multi-platform compatibility",
        "âœ… Zero vendor lock-in",
        "",
        "DIFFERENTIATORS:",
        "â€¢ African cybersecurity expertise",
        "â€¢ Community-driven development"
    ])
    
    # ============================================================
    # SLIDE 11: GO-TO-MARKET STRATEGY
    # ============================================================
    add_slide("ðŸš€ Go-to-Market Strategy", [
        "PHASE 1: Malawi Launch (Q1 2025)",
        "â€¢ Beta testing with 20 enterprises",
        "â€¢ Strategic partnerships with ISPs",
        "â€¢ Government cybersecurity program",
        "",
        "PHASE 2: Regional Expansion (Q3 2025)",
        "â€¢ Zambia, Zimbabwe, Tanzania",
        "â€¢ Regional reseller network",
        "",
        "PHASE 3: Continental Scale (2026)",
        "â€¢ East and West Africa",
        "â€¢ Pan-African partnerships",
        "",
        "CHANNELS:",
        "Direct Sales â€¢ Resellers â€¢ Online â€¢ Government"
    ])
    
    # ============================================================
    # SLIDE 12: TRACTION
    # ============================================================
    add_slide("ðŸ“Š Traction & Current Stage", [
        "CURRENT STATUS:",
        "â€¢ MVP launched and validated",
        "â€¢ 25 enterprise beta users",
        "â€¢ 300+ individual users",
        "â€¢ 95% user satisfaction rate",
        "",
        "MILESTONES ACHIEVED:",
        "â€¢ Product architecture design",
        "â€¢ Core security modules built",
        "â€¢ SQL injection detection (98% accuracy)",
        "â€¢ Automated hardening (CIS compliance)",
        "",
        "NEXT MILESTONES:",
        "â€¢ Enterprise scalability testing",
        "â€¢ SOC integration"
    ])
    
    # ============================================================
    # SLIDE 13: ROADMAP
    # ============================================================
    add_slide("ðŸ—ºï¸ Product Roadmap", [
        "Q1 2025: Malawi Launch",
        "â€¢ Finalize MVP",
        "â€¢ Onboard 20 enterprise clients",
        "â€¢ Establish local support",
        "",
        "Q2 2025: Feature Expansion",
        "â€¢ AI-powered threat detection",
        "â€¢ Compliance automation",
        "â€¢ Mobile app release",
        "",
        "Q3 2025: Regional Expansion",
        "â€¢ Zambia & Zimbabwe launch",
        "â€¢ Regional partnerships",
        "",
        "Q4 2025: Enterprise Scale",
        "â€¢ Full SOC integration",
        "â€¢ Advanced analytics"
    ])
    
    # ============================================================
    # SLIDE 14: FUNDING REQUEST
    # ============================================================
    add_slide("ðŸ’Ž Funding Request", [
        "RAISING: $1.5M",
        "",
        "USE OF FUNDS:",
        "â€¢ Product Development: 40%",
        "â€¢ Sales & Marketing: 25%",
        "â€¢ Team Expansion: 20%",
        "â€¢ Operations: 10%",
        "â€¢ Contingency: 5%",
        "",
        "INVESTMENT STRUCTURE:",
        "â€¢ Seed Round: $500K",
        "â€¢ Series A: $1M",
        "",
        "VALUATION: $5M Pre-money"
    ])
    
    # ============================================================
    # SLIDE 15: USE OF FUNDS
    # ============================================================
    add_slide("ðŸ“‹ Use of Funds", [
        "PRODUCT DEVELOPMENT ($600K):",
        "â€¢ Core platform enhancements",
        "â€¢ AI/ML integration",
        "â€¢ Mobile app development",
        "â€¢ Security hardening tools",
        "",
        "SALES & MARKETING ($375K):",
        "â€¢ Direct sales team",
        "â€¢ Digital marketing campaign",
        "â€¢ Regional roadshows",
        "",
        "TEAM EXPANSION ($300K):",
        "â€¢ 3 developers",
        "â€¢ 2 sales professionals",
        "â€¢ 1 product manager",
        "",
        "OPERATIONS ($150K):",
        "â€¢ Cloud infrastructure",
        "â€¢ Support team",
        "â€¢ Office expansion"
    ])
    
    # ============================================================
    # SLIDE 16: FINANCIAL PROJECTIONS
    # ============================================================
    add_slide("ðŸ“Š Financial Projections", [
        "REVENUE PROJECTIONS:",
        "â€¢ Year 1 (2025): $250K",
        "â€¢ Year 2 (2026): $1.2M",
        "â€¢ Year 3 (2027): $3.5M",
        "â€¢ Year 4 (2028): $7.8M",
        "",
        "KEY METRICS:",
        "â€¢ Customer Acquisition Cost: $500",
        "â€¢ Lifetime Value: $15,000",
        "â€¢ Churn Rate: <5%",
        "â€¢ Gross Margin: 75%",
        "",
        "BREAK-EVEN:",
        "â€¢ By end of Year 2"
    ])
    
    # ============================================================
    # SLIDE 17: IMPACT
    # ============================================================
    add_slide("ðŸŒŸ Impact", [
        "SECURITY IMPACT:",
        "â€¢ Protect 1M+ digital assets",
        "â€¢ Prevent $500M+ in cyber losses",
        "â€¢ Build African cybersecurity capacity",
        "",
        "SOCIAL IMPACT:",
        "â€¢ Create 50+ jobs",
        "â€¢ Train 1,000+ cybersecurity professionals",
        "â€¢ Develop local cybersecurity talent",
        "",
        "ECONOMIC IMPACT:",
        "â€¢ $10M+ in economic value",
        "â€¢ Support 500+ organizations",
        "â€¢ Strengthen Malawi's digital economy"
    ])
    
    # ============================================================
    # SLIDE 18: TEAM
    # ============================================================
    add_slide("ðŸ‘¥ The Team", [
        "FOUNDER & CEO:",
        "â€¢ 10+ years cybersecurity experience",
        "â€¢ Former Security Architect at major bank",
        "â€¢ Certified Ethical Hacker (CEH)",
        "",
        "KEY HIRES:",
        "â€¢ Lead Developer - Full-stack expert",
        "â€¢ Security Engineer - Penetration testing",
        "â€¢ Product Manager - SaaS experience",
        "â€¢ Sales Director - Enterprise sales",
        "",
        "ADVISORS:",
        "â€¢ Senior cybersecurity experts",
        "â€¢ African tech ecosystem leaders"
    ])
    
    # ============================================================
    # SLIDE 19: WHY INVEST
    # ============================================================
    add_slide("ðŸ’¡ Why Invest in DSTERMINAL", [
        "1. ðŸ’° MASSIVE MARKET OPPORTUNITY",
        "   â€¢ African cybersecurity market: $3.5B",
        "   â€¢ 35% annual growth",
        "",
        "2. ðŸš€ PROVEN PRODUCT",
        "   â€¢ 95% user satisfaction",
        "   â€¢ Working MVP with 25 enterprise clients",
        "",
        "3. ðŸ† COMPETITIVE ADVANTAGE",
        "   â€¢ 90% lower cost than competitors",
        "   â€¢ African-focused threat intelligence",
        "",
        "4. ðŸ’Ž EXPERIENCED TEAM",
        "   â€¢ Deep cybersecurity expertise",
        "   â€¢ Strong industry connections",
        "",
        "5. ðŸ“ˆ SCALABLE BUSINESS MODEL",
        "   â€¢ Recurring revenue",
        "   â€¢ Expandable to 54 African countries"
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
    tf3.text = "ðŸ“§ info@dsterminal.com\nðŸ“ž +265 111 222 333\nðŸŒ www.dsterminal.com"
    tf3.paragraphs[0].font.size = Pt(24)
    tf3.paragraphs[0].font.color.rgb = GOLD
    tf3.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # ============================================================
    # SAVE
    # ============================================================
    output_file = f"DSTERMINAL_Pitch_Deck_{datetime.now().strftime('%Y%m%d')}.pptx"
    prs.save(output_file)
    print(f"âœ… Pitch deck created successfully!")
    print(f"ðŸ“ File: {output_file}")
    print(f"ðŸ“Š Slides: {len(prs.slides)}")
    return output_file

if __name__ == "__main__":
    # Install required package if missing
    try:
        import pptx
    except ImportError:
        print("ðŸ“¦ Installing python-pptx...")
        os.system("pip install python-pptx")
        import pptx
    
    create_dsterminal_pitch_deck()