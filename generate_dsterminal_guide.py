#!python
"""
DSTerminal Cyber-Ops Platform - Complete User Guide PDF Generator
Version: 4.0.0.113
Author: Spark Wilson Spink
Organization: Stark Expo Tech Exchange
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import textwrap

# Register fonts if available (optional)
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
except:
    pass

def hex_with_alpha(hex_color, alpha=1.0):
    """Create a color from hex with alpha transparency"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return Color(r, g, b, alpha=alpha)

# Color scheme - High contrast for white background
COLORS = {
    'primary': colors.HexColor('#0a0e1a'),
    'secondary': colors.HexColor('#1a2332'),
    'accent': colors.HexColor('#00cc88'),      # Brighter green
    'accent2': colors.HexColor('#0066cc'),     # Dark blue for headings
    'warning': colors.HexColor('#cc0000'),     # Dark red
    'warning2': colors.HexColor('#cc6600'),    # Dark orange
    'text': colors.HexColor('#1a1a2e'),        # Dark text for white bg
    'text_dim': colors.HexColor('#444466'),    # Darker dim text
    'header_bg': colors.HexColor('#0a0e1a'),
    'footer_bg': colors.HexColor('#0a0e1a'),
    'border': colors.HexColor('#00cc88'),
    'table_header': colors.HexColor('#0066cc'), # Blue table header
    'code_bg': colors.HexColor('#f0f4f8'),      # Light gray for code
    'code_text': colors.HexColor('#003366'),    # Dark blue for code
}

# Colors with alpha for watermarks - lighter for white bg
WATERMARK_COLOR = hex_with_alpha('#0066cc', 0.06)
WATERMARK_COLOR_LIGHT = hex_with_alpha('#0066cc', 0.04)
FOOTER_COLOR = hex_with_alpha('#00cc88', 0.5)

# Global page counter
page_counter = {'count': 0}

def header(canvas, doc, content):
    """Draw page header"""
    canvas.saveState()
    
    # Header background - dark
    canvas.setFillColor(COLORS['header_bg'])
    canvas.rect(0, 800, 595, 80, fill=1)
    
    # Header border - cyber green accent
    canvas.setStrokeColor(COLORS['accent'])
    canvas.setLineWidth(2)
    canvas.line(0, 800, 595, 800)
    
    # Title - bright green on dark bg
    canvas.setFillColor(COLORS['accent'])
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawString(50, 830, "DSTERMINAL Cyber-Ops Platform")
    
    canvas.setFillColor(colors.HexColor('#8899aa'))
    canvas.setFont('Helvetica', 9)
    canvas.drawString(50, 812, "AI-Powered Cybersecurity Operations Terminal")
    
    # Version on right
    canvas.setFillColor(colors.HexColor('#8899aa'))
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(545, 830, "v4.0.0.113")
    canvas.drawRightString(545, 812, "Â© 2024 Stark Expo Tech Exchange")
    
    # Header line
    canvas.setStrokeColor(COLORS['accent2'])
    canvas.setLineWidth(1)
    canvas.line(0, 798, 595, 798)
    
    canvas.restoreState()

def footer(canvas, doc, content):
    """Draw page footer"""
    global page_counter
    page_counter['count'] += 1
    
    canvas.saveState()
    
    # Footer background - dark
    canvas.setFillColor(COLORS['footer_bg'])
    canvas.rect(0, 0, 595, 40, fill=1)
    
    # Footer border
    canvas.setStrokeColor(COLORS['accent'])
    canvas.setLineWidth(1)
    canvas.line(0, 40, 595, 40)
    
    # Footer text
    canvas.setFillColor(colors.HexColor('#8899aa'))
    canvas.setFont('Helvetica', 7)
    canvas.drawString(50, 18, "DSTERMINAL Cyber-Ops Platform | AI-Powered Security Operations")
    
    # Page number
    canvas.drawRightString(545, 18, f"Page {page_counter['count']}")
    
    # Bottom right
    canvas.setFillColor(FOOTER_COLOR)
    canvas.setFont('Helvetica', 6)
    canvas.drawString(50, 6, "For authorized use only. All activities are monitored.")
    
    canvas.restoreState()

def watermark(canvas, doc, content):
    """Draw diagonal watermark"""
    canvas.saveState()
    canvas.setFillColor(WATERMARK_COLOR)
    canvas.setFont('Helvetica-Bold', 60)
    
    # Diagonal watermark
    canvas.translate(300, 400)
    canvas.rotate(45)
    canvas.drawString(-200, -100, "DSTERMINAL v4.0.0.113")
    canvas.drawString(-200, -50, "CYBER-OPS PLATFORM")
    
    # Additional watermark pattern
    canvas.setFont('Helvetica', 20)
    canvas.setFillColor(WATERMARK_COLOR_LIGHT)
    for i in range(-4, 5):
        canvas.drawString(-300 + (i * 150), -200 + (i * 80), "AI-POWERED SECURITY")
    
    canvas.restoreState()

def sidebar(canvas, doc, content):
    """Draw decorative sidebar"""
    canvas.saveState()
    
    # Left sidebar accent
    left_color = hex_with_alpha('#0066cc', 0.08)
    right_color = hex_with_alpha('#00cc88', 0.08)
    
    canvas.setFillColor(left_color)
    canvas.rect(0, 40, 4, 760, fill=1)
    
    canvas.setFillColor(right_color)
    canvas.rect(591, 40, 4, 760, fill=1)
    
    canvas.restoreState()

def first_page(canvas, doc):
    """Draw everything on first page"""
    header(canvas, doc, None)
    footer(canvas, doc, None)
    watermark(canvas, doc, None)
    sidebar(canvas, doc, None)

def later_pages(canvas, doc):
    """Draw everything on later pages"""
    header(canvas, doc, None)
    footer(canvas, doc, None)
    watermark(canvas, doc, None)
    sidebar(canvas, doc, None)

def create_title_style():
    """Create title styles with high contrast"""
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=36,
        textColor=COLORS['accent'],
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    chapter_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COLORS['accent2'],
        alignment=TA_LEFT,
        spaceAfter=16,
        spaceBefore=24,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=COLORS['text'],
        alignment=TA_LEFT,
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )
    
    subsection_style = ParagraphStyle(
        'SubsectionTitle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=COLORS['accent2'],
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10.5,
        textColor=COLORS['text'],
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=0,
        leading=15,
        fontName='Helvetica'
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLORS['code_text'],
        alignment=TA_LEFT,
        spaceAfter=3,
        spaceBefore=3,
        leading=11,
        fontName='Courier',
        backColor=COLORS['code_bg']
    )
    
    return {
        'title': title_style,
        'chapter': chapter_style,
        'section': section_style,
        'subsection': subsection_style,
        'body': body_style,
        'code': code_style,
        'normal': styles['Normal']
    }


def create_ascii_banner():
    """Create DSTERMINAL ASCII banner (correct spelling)"""
    return [
        "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—",
        "â•‘                                                                        â•‘",
        "â•‘  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ•—  â•‘",
        "â•‘  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â•‘",
        "â•‘  â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•”â–ˆâ–ˆâ–ˆâ–ˆâ•”â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â–ˆâ–ˆâ•— â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘  â•‘",
        "â•‘  â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â•šâ•â•â•â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘  â•‘",
        "â•‘  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ•â• â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â•‘",
        "â•‘  â•šâ•â•â•â•â•â• â•šâ•â•â•â•â•â•â•   â•šâ•â•   â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•     â•šâ•â•â•šâ•â•â•šâ•â•  â•šâ•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•‘",
        "â•‘                                                                        â•‘",
        "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•",
        "                        [ ENCRYPTION SUITE v4.0.0.113 - EDITION ]"
    ]


def generate_pdf():
    """Generate the complete DSTerminal user guide PDF"""
    global page_counter
    page_counter['count'] = 0
    
    # Get absolute path for the PDF in the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "DSTerminal_User_Guide_v4.0.0.113.pdf")
    
    print(f"ðŸ“„ Generating PDF at: {filename}")
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=100,
        bottomMargin=60,
        title="DSTERMINAL Cyber-Ops Platform User Guide"
    )
    
    styles = create_title_style()
    story = []
    
    # ====================================================================
    # COVER PAGE
    # ====================================================================
    story.append(Spacer(1, 2*inch))
    
    story.append(Paragraph("DSTERMINAL", styles['title']))
    story.append(Paragraph("Cyber-Ops Platform", styles['title']))
    story.append(Spacer(1, 0.3*inch))
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['body'],
        fontSize=16,
        textColor=COLORS['text_dim'],
        alignment=TA_CENTER
    )
    story.append(Paragraph("AI-Powered Cybersecurity Operations Terminal", subtitle_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Complete User Guide", subtitle_style))
    
    story.append(Spacer(1, 0.5*inch))
    
    line_style = ParagraphStyle(
        'Line',
        parent=styles['body'],
        fontSize=10,
        textColor=COLORS['accent'],
        alignment=TA_CENTER
    )
    story.append(Paragraph("â•" * 60, line_style))
    
    story.append(Spacer(1, 0.5*inch))
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['body'],
        fontSize=11,
        textColor=COLORS['text_dim'],
        alignment=TA_CENTER
    )
    story.append(Paragraph("<b>Version:</b> 4.0.0.113", info_style))
    story.append(Paragraph("<b>Platforms:</b> Windows / Linux (macOS Coming Soon)", info_style))
    story.append(Paragraph("<b>Developer:</b> Spark Wilson Spink", info_style))
    story.append(Paragraph("<b>Powered by:</b> Stark Expo Tech Exchange", info_style))
    story.append(Paragraph("<b>Date:</b> " + datetime.now().strftime("%B %d, %Y"), info_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['body'],
        fontSize=10,
        textColor=COLORS['warning'],
        alignment=TA_CENTER
    )
    story.append(Paragraph("âš ï¸ FOR AUTHORIZED USE ONLY - ALL ACTIVITIES ARE MONITORED âš ï¸", warning_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    banner_style = ParagraphStyle(
        'Banner',
        parent=styles['code'],
        fontSize=6,
        textColor=COLORS['accent'],
        alignment=TA_CENTER,
        leading=8
    )
    for line in create_ascii_banner():
        story.append(Paragraph(line, banner_style))
    
    story.append(PageBreak())
    
    # ====================================================================
    # TABLE OF CONTENTS
    # ====================================================================
    story.append(Paragraph("TABLE OF CONTENTS", styles['chapter']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("â•" * 50, styles['body']))
    story.append(Spacer(1, 0.2*inch))
    
    toc_items = [
        ("1. INTRODUCTION", 1),
        ("   1.1 What is DSTerminal?", 1),
        ("   1.2 Key Capabilities", 1),
        ("   1.3 Who Is DSTerminal For?", 1),
        ("   1.4 AI-Powered Features", 1),
        ("2. SYSTEM REQUIREMENTS", 2),
        ("   2.1 Windows", 2),
        ("   2.2 Linux", 2),
        ("3. INSTALLATION & FIRST LAUNCH", 3),
        ("   3.1 Windows Installation", 3),
        ("   3.2 Linux Installation", 3),
        ("4. INITIALIZATION STAGES", 4),
        ("   4.1 Stage 1: Core System Bootstrap", 4),
        ("   4.2 Stage 2: Multi-Color Dashboard", 4),
        ("   4.3 Stage 3: System Ready", 4),
        ("5. UNDERSTANDING THE INTERFACE", 5),
        ("   5.1 Command Prompt Structure", 5),
        ("   5.2 Command Categories", 5),
        ("   5.3 Module Dashboard", 5),
        ("6. GETTING HELP", 6),
        ("   6.1 Help Command", 6),
        ("   6.2 Help by Category", 6),
        ("   6.3 Command Reference Cards", 6),
        ("7. MODULE GUIDE", 7),
        ("   7.1 Complete Module List", 7),
        ("   7.2 VirusTotal", 7),
        ("   7.3 SQL Injection Lab", 7),
        ("   7.4 System Hardening", 7),
        ("   7.5 Cryptography", 8),
        ("   7.6 Web Security", 8),
        ("   7.7 Ransomware Monitor", 8),
        ("   7.8 Reconnaissance", 8),
        ("   7.9 Exploit Check", 8),
        ("   7.10 Financial Forensics", 9),
        ("   7.11 WiFi Audit", 9),
        ("8. COMMON WORKFLOWS", 9),
        ("   8.1 Security Assessment", 9),
        ("   8.2 Incident Response", 9),
        ("   8.3 Penetration Testing", 10),
        ("   8.4 Compliance Audit", 10),
        ("   8.5 Daily SOC Operations", 10),
        ("   8.6 Encryption", 10),
        ("9. REPORT GENERATION", 11),
        ("   9.1 Report Types", 11),
        ("   9.2 Report Location", 11),
        ("   9.3 Sample Report", 11),
        ("10. BEST PRACTICES", 12),
        ("   10.1 Security Best Practices", 12),
        ("   10.2 Performance Optimization", 12),
        ("   10.3 Common Mistakes", 12),
        ("11. TROUBLESHOOTING", 13),
        ("   11.1 Common Issues", 13),
        ("   11.2 Log Location", 13),
        ("   11.3 Support Resources", 13),
        ("12. GLOSSARY", 14),
        ("   12.1 Key Terms", 14),
        ("   12.2 Module Glossary", 14),
        ("13. GETTING STARTED CHECKLIST", 15),
        ("14. QUICK REFERENCE CARD", 16),
        ("15. CONTACT & SUPPORT", 17),
    ]
    
    for item, page in toc_items:
        toc_style = ParagraphStyle(
            'TOC',
            parent=styles['body'],
            fontSize=10,
            textColor=COLORS['text'] if not item.startswith("   ") else COLORS['text_dim'],
            alignment=TA_LEFT,
            fontName='Helvetica' if not item.startswith("   ") else 'Helvetica'
        )
        dots = "." * (55 - len(item) - len(str(page)))
        story.append(Paragraph(f"{item} {dots} {page}", toc_style))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 1: INTRODUCTION
    # ====================================================================
    story.append(Paragraph("1. INTRODUCTION", styles['chapter']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("1.1 What is DSTerminal?", styles['section']))
    story.append(Paragraph(
        "DSTerminal Cyber-Ops Platform is an AI-powered, unified cybersecurity "
        "operations terminal that integrates over 15 security disciplines into "
        "a single, cohesive command-line interface. It serves as a comprehensive "
        "security operations center (SOC) in a terminal, combining threat intelligence, "
        "vulnerability assessment, incident response, network security, cryptography, "
        "forensics, and educational tools.",
        styles['body']
    ))
    
    story.append(Paragraph("1.2 Key Capabilities", styles['section']))
    capabilities = [
        ("ðŸ” Threat Intelligence", "Real-time IOC feeds, VirusTotal integration, APT tracking"),
        ("ðŸ›¡ï¸ Vulnerability Assessment", "Exploit checking, CVE scanning, web security testing"),
        ("ðŸ” Encryption & Cryptography", "AES-256-GCM, QR key sharing, quantum-resistant keys"),
        ("ðŸ“¡ Network Security", "Port scanning, WiFi auditing, traffic analysis"),
        ("ðŸ”„ Incident Response", "Ransomware monitoring, file integrity, forensic analysis"),
        ("ðŸ’° Financial Forensics", "Money laundering detection, fraud investigation"),
        ("ðŸŽ“ Security Education", "SQL Injection Learning Lab, interactive training"),
    ]
    
    # Fixed: Use item[0] and item[1] to access tuple elements
    cap_data = [[f"<b>{item[0]}</b>", item[1]] for item in capabilities]
    cap_table = Table(cap_data, colWidths=[120, 350])
    cap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(cap_table)
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("1.3 Who Is DSTerminal For?", styles['section']))
    audience = [
        ("SOC Analysts", "Real-time monitoring, threat hunting, incident response"),
        ("Penetration Testers", "Reconnaissance, exploitation, reporting"),
        ("Security Engineers", "System hardening, compliance auditing"),
        ("IT Professionals", "Network security, vulnerability management"),
        ("Students", "Learning cybersecurity through hands-on labs"),
        ("Organizations", "Comprehensive security operations"),
    ]
    
    # Fixed: Use item[0] and item[1] to access tuple elements
    aud_data = [[f"<b>{item[0]}</b>", item[1]] for item in audience]
    aud_table = Table(aud_data, colWidths=[130, 340])
    aud_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['accent2']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(aud_table)
    
    story.append(Paragraph("1.4 AI-Powered Features", styles['section']))
    ai_features = [
        ("ðŸ§  AI Scoring", "Risk assessment with machine learning"),
        ("ðŸ¤– Smart Command Suggestions", "Tab completion with context awareness"),
        ("ðŸ“Š Predictive Analytics", "Anomaly detection and threat prediction"),
        ("ðŸŽ¯ Intelligent Reconnaissance", "Automated asset discovery"),
        ("ðŸ”® Zero-Day Intelligence", "Real-time CVE monitoring"),
    ]
    
    # Fixed: Use item[0] and item[1] to access tuple elements
    ai_data = [[f"<b>{item[0]}</b>", item[1]] for item in ai_features]
    ai_table = Table(ai_data, colWidths=[140, 330])
    ai_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(ai_table)
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 2: SYSTEM REQUIREMENTS
    # ====================================================================
    story.append(Paragraph("2. SYSTEM REQUIREMENTS", styles['chapter']))
    
    story.append(Paragraph("2.1 Windows", styles['section']))
    win_req = [
        ("Component", "Minimum", "Recommended"),
        ("OS", "Windows 10 (64-bit)", "Windows 11 (64-bit)"),
        ("CPU", "Intel i5 / AMD Ryzen 5", "Intel i7 / AMD Ryzen 7"),
        ("RAM", "8 GB", "16 GB+"),
        ("Disk", "2 GB free", "5 GB free"),
        ("Network", "Internet connection", "High-speed internet"),
        ("Permissions", "Administrator", "Administrator"),
    ]
    win_table = Table(win_req, colWidths=[120, 150, 200])
    win_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['table_header']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(win_table)
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Windows Dependencies:</b>", styles['subsection']))
    story.append(Paragraph("â€¢ Windows 10/11 (64-bit)", styles['body']))
    story.append(Paragraph("â€¢ PowerShell 5.0+", styles['body']))
    story.append(Paragraph("â€¢ .NET Framework 4.7.2+", styles['body']))
    story.append(Paragraph("â€¢ Web browser (for SQL Lab)", styles['body']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("2.2 Linux", styles['section']))
    lin_req = [
        ("Component", "Minimum", "Recommended"),
        ("OS", "Ubuntu 20.04+ / Debian 11+", "Ubuntu 22.04+"),
        ("CPU", "Intel i5 / AMD Ryzen 5", "Intel i7 / AMD Ryzen 7"),
        ("RAM", "4 GB", "8 GB+"),
        ("Disk", "2 GB free", "5 GB free"),
        ("Network", "Internet connection", "High-speed internet"),
        ("Permissions", "Sudo access", "Sudo access"),
    ]
    lin_table = Table(lin_req, colWidths=[120, 150, 200])
    lin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['table_header']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(lin_table)
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Linux Dependencies:</b>", styles['subsection']))
    story.append(Paragraph("â€¢ Python 3.8+", styles['body']))
    story.append(Paragraph("â€¢ pip3", styles['body']))
    story.append(Paragraph("â€¢ nmap", styles['body']))
    story.append(Paragraph("â€¢ openssl", styles['body']))
    story.append(Paragraph("â€¢ curl/wget", styles['body']))
    story.append(Paragraph("â€¢ Web browser", styles['body']))
    
    code_lines = [
        "sudo apt update",
        "sudo apt install -y python3 python3-pip nmap openssl curl wget",
        "pip3 install --user python-nmap pyopenssl cryptography requests beautifulsoup4"
    ]
    story.append(Paragraph("<b>Install Dependencies (Linux):</b>", styles['subsection']))
    for line in code_lines:
        story.append(Paragraph(line, styles['code']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 3: INSTALLATION & FIRST LAUNCH
    # ====================================================================
    story.append(Paragraph("3. INSTALLATION & FIRST LAUNCH", styles['chapter']))
    
    story.append(Paragraph("3.1 Windows Installation", styles['section']))
    story.append(Paragraph("<b>Step 1: Download</b>", styles['subsection']))
    story.append(Paragraph("1. Visit the official DSTerminal download portal", styles['body']))
    story.append(Paragraph("2. Download the latest Windows installer (DSTerminal_Setup.exe)", styles['body']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Step 2: Install</b>", styles['subsection']))
    install_steps = [
        "1. Double-click DSTerminal_Setup.exe",
        "2. Accept the license agreement",
        "3. Choose installation directory (default: C:\\Program Files\\DSTerminal)",
        "4. Select components (recommended: Full Installation)",
        "5. Click 'Install'",
        "6. Wait for installation to complete",
        "7. Click 'Finish'"
    ]
    for step in install_steps:
        story.append(Paragraph(step, styles['body']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Step 3: First Launch (Windows)</b>", styles['subsection']))
    story.append(Paragraph("<b>Option A: Desktop Shortcut (Recommended)</b>", styles['body']))
    story.append(Paragraph("1. Double-click the DSTerminal icon on your desktop", styles['body']))
    story.append(Paragraph("2. If prompted by User Account Control (UAC), click 'Yes'", styles['body']))
    
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph("<b>Option B: Start Menu</b>", styles['body']))
    story.append(Paragraph("1. Click Start Menu", styles['body']))
    story.append(Paragraph("2. Search for 'DSTerminal'", styles['body']))
    story.append(Paragraph("3. Click the app icon", styles['body']))
    
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph("<b>Option C: Run as Administrator</b>", styles['body']))
    story.append(Paragraph("1. Right-click the DSTerminal icon", styles['body']))
    story.append(Paragraph("2. Select 'Run as administrator'", styles['body']))
    story.append(Paragraph("3. Click 'Yes' on the UAC prompt", styles['body']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Initial Startup Sequence</b>", styles['subsection']))
    init_output = [
        "â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”",
        "â”‚  DSTERMINAL CYBER-OPS PLATFORM                                 â”‚",
        "â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                 â”‚",
        "â”‚  [â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ] 100%              â”‚",
        "â”‚                                                                 â”‚",
        "â”‚  âœ… System Initializing...                                     â”‚",
        "â”‚  âœ… Encryption Suite v4.0.0.113 loaded                           â”‚",
        "â”‚  âœ… SQL Injection Lab initialized                              â”‚",
        "â”‚  âœ… Forensic Analyzer initialized                              â”‚",
        "â”‚  âœ… System Integrity Monitor initialized                       â”‚",
        "â”‚                                                                 â”‚",
        "â”‚  ðŸ”¹ OP-21C2BF @ soc-terminal : ~$                             â”‚",
        "â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜"
    ]
    for line in init_output:
        story.append(Paragraph(line, styles['code']))
    
    story.append(PageBreak())
    story.append(Paragraph("3.2 Linux Installation", styles['section']))
    story.append(Paragraph("<b>Step 1: Download</b>", styles['subsection']))
    story.append(Paragraph("wget https://dsterminal.com/downloads/dsterminal-linux-amd64.deb", styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Step 2: Install</b>", styles['subsection']))
    story.append(Paragraph("<b>Debian/Ubuntu (.deb)</b>", styles['body']))
    story.append(Paragraph("sudo dpkg -i dsterminal-linux-amd64.deb", styles['code']))
    story.append(Paragraph("sudo apt-get install -f  # Fix dependencies", styles['code']))
    
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph("<b>RHEL/CentOS/Fedora (.rpm)</b>", styles['body']))
    story.append(Paragraph("sudo rpm -ivh dsterminal-linux-amd64.rpm", styles['code']))
    
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph("<b>Universal (AppImage)</b>", styles['body']))
    story.append(Paragraph("chmod +x dsterminal.AppImage", styles['code']))
    story.append(Paragraph("./dsterminal.AppImage", styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Step 3: First Launch (Linux)</b>", styles['subsection']))
    story.append(Paragraph("# Run DSTerminal", styles['code']))
    story.append(Paragraph("dsterminal", styles['code']))
    story.append(Paragraph("# Or run with sudo for full features", styles['code']))
    story.append(Paragraph("sudo dsterminal", styles['code']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 4: INITIALIZATION STAGES
    # ====================================================================
    story.append(Paragraph("4. INITIALIZATION STAGES", styles['chapter']))
    
    story.append(Paragraph("4.1 Stage 1: Core System Bootstrap", styles['section']))
    story.append(Paragraph("<b>What Happens</b>", styles['subsection']))
    story.append(Paragraph("â€¢ ASCII Banner - DSTERMINAL branding display", styles['body']))
    story.append(Paragraph("â€¢ Encryption Suite - Core cryptographic engine loads", styles['body']))
    story.append(Paragraph("â€¢ Operator ID - Unique operator identifier assigned", styles['body']))
    story.append(Paragraph("â€¢ Session ID - Unique session tracking created", styles['body']))
    story.append(Paragraph("â€¢ Timestamp - System start time recorded", styles['body']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Components Initialized</b>", styles['subsection']))
    story.append(Paragraph("âœ… SQL Injection Lab database", styles['body']))
    story.append(Paragraph("âœ… Bundled SQLMap integration", styles['body']))
    story.append(Paragraph("âœ… Auto-remediation engine", styles['body']))
    story.append(Paragraph("âœ… Forensic Analyzer", styles['body']))
    story.append(Paragraph("âœ… System Integrity Monitor", styles['body']))
    story.append(Paragraph("âœ… Workspace created", styles['body']))
    
    story.append(Spacer(1, 0.1*inch))
    stage1_lines = [
        "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—",
        "â•‘  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ•—â•‘",
        "â•‘  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ•—â•‘",
        "â•‘  â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•”â–ˆâ–ˆâ–ˆâ–ˆâ•”â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â–ˆâ–ˆâ•—â•‘",
        "â•‘  â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â•šâ•â•â•â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•—â•‘",
        "â•‘  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ•â• â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ–ˆâ–ˆâ–ˆâ–ˆâ•‘",
        "â•‘  â•šâ•â•â•â•â•â• â•šâ•â•â•â•â•â•â•   â•šâ•â•   â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•     â•šâ•â•â•šâ•â•â•šâ•â•  â•šâ•â•â•â•â•‘",
        "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•",
        "                        [ ENCRYPTION SUITE v4.0.0.113 - EDITION ]",
        "",
        "âœ… System Initializatizing...",
        "   Operator ID: OP-21C2BF",
        "   Session ID: SESSION-856B6",
        "   Start Time: 2026-07-22 14:21:14"
    ]
    for line in stage1_lines:
        story.append(Paragraph(line, styles['code']))
    
    story.append(PageBreak())
    story.append(Paragraph("4.2 Stage 2: Multi-Color Dashboard", styles['section']))
    story.append(Paragraph("<b>Metrics Panel (Left)</b>", styles['subsection']))
    metrics = [
        "â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”",
        "â”‚   ðŸ“Š METRICS PANEL       â”‚",
        "â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤",
        "â”‚ â€¢ Alerts/h:    247       â”‚",
        "â”‚ â€¢ Incidents:   12        â”‚",
        "â”‚ â€¢ MTTR:        4.2m      â”‚",
        "â”‚ â€¢ Uptime:      99.97%    â”‚",
        "â”‚ â€¢ Risk Score:  76/100    â”‚",
        "â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜"
    ]
    for line in metrics:
        story.append(Paragraph(line, styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Intelligence Panel (Right)</b>", styles['subsection']))
    intel = [
        "â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”",
        "â”‚   ðŸ“¡ INTELLIGENCE        â”‚",
        "â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤",
        "â”‚ â€¢ New IOCs:  47          â”‚",
        "â”‚ â€¢ Campaign:  APT29       â”‚",
        "â”‚ â€¢ TTPs Updated           â”‚",
        "â”‚ â€¢ Zero-day:  CVE-2024    â”‚",
        "â”‚ â€¢ Patch:     83%         â”‚",
        "â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜"
    ]
    for line in intel:
        story.append(Paragraph(line, styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status Bar</b>", styles['subsection']))
    status_lines = [
        "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—",
        "â•‘     Defensive Security Terminal v4.0.0.113 | Windows 10                  â•‘",
        "â•‘     Developer: Spark Wilson Spink | Â© 2024 | Powered by Stark Expo Tech Exchange â•‘",
        "â•‘     Type 'help' for available commands:                                                 â•‘",
        "â•‘     CLI Mode: ADMIN ðŸ”’                             â•‘",
        "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
    ]
    for line in status_lines:
        story.append(Paragraph(line, styles['code']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("4.3 Stage 3: System Ready", styles['section']))
    story.append(Paragraph("<b>Ready State Indicators</b>", styles['subsection']))
    story.append(Paragraph("[14:24:08] DESKTOP-UT7D76J [PROD] NORMAL [SESSION-856B6]", styles['code']))
    story.append(Paragraph("ðŸ”¹ OP-21C2BF @ soc-terminal : ~$", styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>What the Prompt Means</b>", styles['subsection']))
    prompt_info = [
        ("[14:24:08]", "Current time"),
        ("DESKTOP-UT7D76J", "Hostname"),
        ("[PROD]", "Production environment"),
        ("NORMAL", "System status"),
        ("[SESSION-856B6]", "Unique session ID"),
        ("ðŸ”¹", "Operator indicator"),
        ("OP-21C2BF", "Operator ID"),
        ("@ soc-terminal", "SOC terminal context"),
        (":~$", "Ready for input"),
    ]
    prompt_data = [[f"<b>{item}</b>", desc] for item, desc in prompt_info]
    prompt_table = Table(prompt_data, colWidths=[150, 320])
    prompt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(prompt_table)
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 5: UNDERSTANDING THE INTERFACE
    # ====================================================================
    story.append(Paragraph("5. UNDERSTANDING THE INTERFACE", styles['chapter']))
    
    story.append(Paragraph("5.1 Command Prompt Structure", styles['section']))
    story.append(Paragraph("[Timestamp] HOSTNAME [ENVIRONMENT] STATUS [SESSION-ID]", styles['code']))
    story.append(Paragraph("ðŸ”¹ OPERATOR @ soc-terminal : ~$ [COMMAND]", styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Example:</b>", styles['subsection']))
    story.append(Paragraph("[15:47:17] DESKTOP-UT7D76J [PROD] NORMAL [SESSION-F339E]", styles['code']))
    story.append(Paragraph("ðŸ”¹ OP-285A78 @ soc-terminal : ~$ help", styles['code']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("5.2 Command Categories", styles['section']))
    story.append(Paragraph("<b>Core Commands</b>", styles['subsection']))
    core_commands = [
        ("help", "Show all available commands"),
        ("clear", "Clear terminal screen"),
        ("exit", "Exit DSTerminal"),
        ("system status", "Show system health"),
    ]
    core_data = [[f"<b>{cmd}</b>", desc] for cmd, desc in core_commands]
    core_table = Table(core_data, colWidths=[120, 350])
    core_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['accent2']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(core_table)
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Tab Completion</b>", styles['subsection']))
    story.append(Paragraph("DSTerminal supports Tab Completion for all commands:", styles['body']))
    story.append(Paragraph("1. Start typing a command", styles['body']))
    story.append(Paragraph("2. Press TAB for suggestions", styles['body']))
    story.append(Paragraph("3. Auto-completes command names", styles['body']))
    story.append(Paragraph("4. Shows available parameters", styles['body']))
    
    story.append(Paragraph("<b>Example:</b>", styles['subsection']))
    story.append(Paragraph("Type: syste[TAB]", styles['code']))
    story.append(Paragraph("Suggests: system, system scan, system status, system list...", styles['code']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("5.3 Module Dashboard", styles['section']))
    story.append(Paragraph("<b>SOC Terminal Dashboard</b>", styles['subsection']))
    
    soc_lines = [
        "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—                                        â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—                                          â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—",
        "â•‘   ðŸ“Š METRICS PANEL    â•‘                                        â•‘                                                                            â•‘                                          â•‘   ðŸ“¡ INTELLIGENCE      â•‘",
        "â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£                                        â•‘     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•—  â–ˆâ–ˆâ•—            â•‘                                           â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£",
        "â•‘ â€¢ Alerts/h:    247    â•‘                                        â•‘     â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•            â•‘                                           â•‘ â€¢ New IOCs:  47       â•‘",
        "â•‘ â€¢ Incidents:   12     â•‘                                        â•‘     â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ•”â–ˆâ–ˆâ•— â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â•šâ–ˆâ–ˆâ–ˆâ•”â•             â•‘                                           â•‘ â€¢ Campaign:  APT29    â•‘",
        "â•‘ â€¢ MTTR:        4.2m   â•‘                                        â•‘     â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•   â–ˆâ–ˆâ•”â–ˆâ–ˆâ•—             â•‘                                           â•‘ â€¢ TTPs Updated        â•‘",
        "â•‘ â€¢ Uptime:      99.97% â•‘                                        â•‘     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘ â•šâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â• â–ˆâ–ˆâ•—            â•‘                                           â•‘ â€¢ Zero-day:  CVE-2024 â•‘",
        "â•‘ â€¢ Risk Score:  76/100 â•‘                                        â•‘     â•šâ•â•â•â•â•â• â•šâ•â•     â•šâ•â•     â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•â•â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•            â•‘                                           â•‘ â€¢ Patch:     83%      â•‘",
        "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•                                        â•‘                                                                            â•‘                                          â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•",
        "                                                                    â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£",
        "                                                                    â•‘     Defensive Security Terminal v4.0.0.113 | Windows 10                  â•‘",
        "                                                                    â•‘     Developer: Spark Wilson Spink | Â© 2024 | Powered by Stark Expo Tech Exchange     â•‘",
        "                                                                    â•‘     Type 'help' for available commands:                                                 â•‘",
        "                                                                    â•‘     CLI Mode: ADMIN ðŸ”’                             â•‘",
        "                                                                    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
    ]
    for line in soc_lines:
        story.append(Paragraph(line, styles['code']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 6: GETTING HELP
    # ====================================================================
    story.append(Paragraph("6. GETTING HELP", styles['chapter']))
    
    story.append(Paragraph("6.1 Help Command", styles['section']))
    story.append(Paragraph("The most important command for new users:", styles['body']))
    story.append(Paragraph("help", styles['code']))
    
    story.append(Paragraph("<b>Help Output Sections</b>", styles['subsection']))
    help_lines = [
        "â”Œâ”€ðŸ”¥ CORE SECURITYâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”",
        "â”‚ system scan -All               System threat scan              â”‚",
        "â”‚ system                         System security management      â”‚",
        "â”‚ system help                    Show system command help        â”‚",
        "â”‚ system scan                    Run system security scan        â”‚",
        "â”‚ system status                  Show system scan status         â”‚",
        "â”‚ net -n mon                     Live network monitoring         â”‚",
        "â”‚ exploitcheck                   Check for critical CVEs         â”‚",
        "â”‚ vtscan                         VirusTotal file analysis        â”‚",
        "â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜",
        "",
        "â”Œâ”€ðŸŒ NETWORK TOOLSâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”",
        "â”‚ nmap <TARGET>                  Basic port scan                 â”‚",
        "â”‚ nmap -sV <TARGET>              Service/version detection       â”‚",
        "â”‚ nmap -A <TARGET>               Aggressive OS and service       â”‚",
        "â”‚ portsweep [IP]                 Scan target for open ports      â”‚",
        "â”‚ traceroute [IP]                Network path analysis           â”‚",
        "â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜"
    ]
    for line in help_lines:
        story.append(Paragraph(line, styles['code']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("6.2 Help by Category", styles['section']))
    help_categories = [
        ("help core", "Core security commands"),
        ("help network", "Network tools"),
        ("help crypto", "Encryption commands"),
        ("help forensics", "Forensics tools"),
        ("help web", "Web security"),
        ("help system", "System management"),
    ]
    help_data = [[f"<b>{cmd}</b>", desc] for cmd, desc in help_categories]
    help_table = Table(help_data, colWidths=[120, 350])
    help_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(help_table)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("6.3 Command Reference Cards", styles['section']))
    story.append(Paragraph("<b>Essential First Commands</b>", styles['subsection']))
    first_cmds = [
        ("help", "Shows all commands"),
        ("system status", "Shows system health"),
        ("scan-quick", "Quick security scan"),
        ("dst-version", "Shows version info"),
        ("clear", "Clears terminal"),
        ("exit", "Exits DSTerminal"),
    ]
    first_data = [[f"<b>{cmd}</b>", desc] for cmd, desc in first_cmds]
    first_table = Table(first_data, colWidths=[120, 350])
    first_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['accent2']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(first_table)
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Pro Tips</b>", styles['subsection']))
    story.append(Paragraph("ðŸ’¡ Use Tab for command completion", styles['body']))
    story.append(Paragraph("âš¡ Combine commands with '&&'", styles['body']))
    story.append(Paragraph("ðŸ”§ Check /var/log/dsterminal for logs", styles['body']))
    story.append(Paragraph("ðŸŒ Access web interface at https://www.dsterminal.com", styles['body']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 7: MODULE GUIDE
    # ====================================================================
    story.append(Paragraph("7. MODULE GUIDE", styles['chapter']))
    
    story.append(Paragraph("7.1 Complete Module List", styles['section']))
    module_list = [
        ("1", "VirusTotal", "vt-scan", "Threat intelligence"),
        ("2", "SQL Injection", "sqllab / sqlmap", "SQL injection testing"),
        ("3", "Network Security", "nmap / net", "Port scanning, network analysis"),
        ("4", "System Hardening", "harden", "System security configuration"),
        ("5", "Cryptography", "encrypt / decrypt", "File encryption/decryption"),
        ("6", "Web Security", "websec", "Web application testing"),
        ("7", "Forensics", "forensics", "Digital forensics"),
        ("8", "Reconnaissance", "recon", "Intelligence gathering"),
        ("9", "Metasploit", "msfconsole", "Exploitation framework"),
        ("10", "Ransomware Monitor", "rmon", "Ransomware detection"),
        ("11", "WiFi Audit", "wifi-audit", "Wireless security"),
        ("12", "MAC Spoofing", "macspoof", "Privacy/anonymity"),
        ("13", "Exploit Check", "exploitcheck", "Vulnerability assessment"),
        ("14", "Financial Forensics", "dst-investigate", "Fraud investigation"),
        ("15", "Certificate Check", "certcheck", "SSL/TLS auditing"),
    ]
    module_data = [[n, f"<b>{name}</b>", cmd, desc] for n, name, cmd, desc in module_list]
    module_table = Table(module_data, colWidths=[30, 100, 120, 200])
    module_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['table_header']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(module_table)
    
    story.append(PageBreak())
    story.append(Paragraph("7.2 VirusTotal (vt-scan)", styles['section']))
    story.append(Paragraph("<b>Command:</b> vt-scan", styles['body']))
    story.append(Paragraph("<b>Dashboard:</b>", styles['subsection']))
    vt_lines = [
        "â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”",
        "â”‚ ðŸ” OPERATION SELECTION                                     â”‚",
        "â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤",
        "â”‚ 1. Hash Lookup (VT Intelligence)                              â”‚",
        "â”‚ 2. File Scan (Upload & Analyze)                              â”‚",
        "â”‚ 3. Bulk Scan Folder                                       â”‚",
        "â”‚ 4. Check Previous Scan                                    â”‚",
        "â”‚ 5. View Quarantine                                       â”‚",
        "â”‚ 0. Exit & Shutdown                                        â”‚",
        "â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜"
    ]
    for line in vt_lines:
        story.append(Paragraph(line, styles['code']))
    
    story.append(Paragraph("<b>Examples:</b>", styles['subsection']))
    story.append(Paragraph("# Hash lookup for suspicious file", styles['code']))
    story.append(Paragraph("vt-scan --hash d41d8cd98f00b204e9800998ecf8427e", styles['code']))
    story.append(Paragraph("# Scan a suspicious executable", styles['code']))
    story.append(Paragraph("vt-scan --file C:\\Users\\stark\\Downloads\\suspicious.exe", styles['code']))
    
    story.append(PageBreak())
    story.append(Paragraph("7.3 SQL Injection Lab (sqllab)", styles['section']))
    story.append(Paragraph("<b>Command:</b> sqllab", styles['body']))
    story.append(Paragraph("<b>Lab Information:</b>", styles['subsection']))
    sql_lines = [
        "â•­â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•®",
        "â”‚ ðŸ“‹ Lab Information:                                         â”‚",
        "â”‚                                                             â”‚",
        "â”‚ ðŸ‘¥ Available Users:                                         â”‚",
        "â”‚   â€¢ admin (Role: administrator, Dept: IT Security)          â”‚",
        "â”‚   â€¢ john_doe (Role: user, Dept: Sales)                      â”‚",
        "â”‚   â€¢ jane_smith (Role: user, Dept: Marketing)                â”‚",
        "â”‚   â€¢ bob_wilson (Role: user, Dept: Engineering)              â”‚",
        "â”‚   â€¢ ... and 6 more users                                    â”‚",
        "â”‚                                                             â”‚",
        "â”‚ ðŸ”‘ Admin Credentials:                                       â”‚",
        "â”‚   Username: admin                                           â”‚",
        "â”‚   Password: admin123                                        â”‚",
        "â”‚                                                             â”‚",
        "â”‚ ðŸ’‰ SQL Injection Techniques Available:                      â”‚",
        "â”‚   â€¢ Basic SQL Injection                                     â”‚",
        "â”‚   â€¢ Union-Based SQL Injection                               â”‚",
        "â”‚   â€¢ Error-Based SQL Injection                               â”‚",
        "â”‚   â€¢ Boolean-Based Blind SQL Injection                       â”‚",
        "â”‚   â€¢ Time-Based Blind SQL Injection                          â”‚",
        "â”‚   â€¢ Stacked Queries SQL Injection                           â”‚",
        "â•°â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•¯"
    ]
    for line in sql_lines:
        story.append(Paragraph(line, styles['code']))
    
    story.append(Paragraph("<b>SQL Injection Examples:</b>", styles['subsection']))
    story.append(Paragraph("# Basic Authentication Bypass", styles['code']))
    story.append(Paragraph("Username: ' OR '1'='1' --", styles['code']))
    story.append(Paragraph("Password: anything", styles['code']))
    story.append(Paragraph("# Union-Based Extraction", styles['code']))
    story.append(Paragraph("' UNION SELECT username, password FROM users --", styles['code']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 8: COMMON WORKFLOWS
    # ====================================================================
    story.append(Paragraph("8. COMMON WORKFLOWS", styles['chapter']))
    
    story.append(Paragraph("8.1 Security Assessment Workflow", styles['section']))
    story.append(Paragraph("<b>Step 1: Reconnaissance</b>", styles['subsection']))
    story.append(Paragraph("# Quick system assessment", styles['code']))
    story.append(Paragraph("dst-recon", styles['code']))
    story.append(Paragraph("# Select option 1", styles['code']))
    story.append(Paragraph("# Or full recon", styles['code']))
    story.append(Paragraph("dst-recon-full", styles['code']))
    
    story.append(Paragraph("<b>Step 2: Vulnerability Scan</b>", styles['subsection']))
    story.append(Paragraph("# Local exploit check", styles['code']))
    story.append(Paragraph("exploitcheck", styles['code']))
    story.append(Paragraph("# Select option 1", styles['code']))
    story.append(Paragraph("# Web security scan", styles['code']))
    story.append(Paragraph("websec", styles['code']))
    story.append(Paragraph("# Select option 1", styles['code']))
    
    story.append(Paragraph("<b>Step 3: Hardening</b>", styles['subsection']))
    story.append(Paragraph("# Apply hardening", styles['code']))
    story.append(Paragraph("harden-cinematic", styles['code']))
    story.append(Paragraph("# Select all modules", styles['code']))
    story.append(Paragraph("Selection: all", styles['code']))
    story.append(Paragraph("# Execute hardening", styles['code']))
    story.append(Paragraph("â”Œâ”€[ SELECT OPTION ]â”€â”", styles['code']))
    story.append(Paragraph("â””â”€>> 3", styles['code']))
    
    story.append(Paragraph("<b>Step 4: Monitoring</b>", styles['subsection']))
    story.append(Paragraph("# Start real-time monitoring", styles['code']))
    story.append(Paragraph("rmon start", styles['code']))
    story.append(Paragraph("# Generate report", styles['code']))
    story.append(Paragraph("rmon export pdf", styles['code']))
    
    story.append(PageBreak())
    story.append(Paragraph("8.2 Incident Response Workflow", styles['section']))
    story.append(Paragraph("<b>Detection</b>", styles['subsection']))
    story.append(Paragraph("# Check for ransomware indicators", styles['code']))
    story.append(Paragraph("rmon-scan", styles['code']))
    story.append(Paragraph("# Review alerts", styles['code']))
    story.append(Paragraph("rmon events", styles['code']))
    
    story.append(Paragraph("<b>Investigation</b>", styles['subsection']))
    story.append(Paragraph("# Launch financial forensics", styles['code']))
    story.append(Paragraph("dst-investigate", styles['code']))
    story.append(Paragraph("# Check certificate status", styles['code']))
    story.append(Paragraph("certcheck", styles['code']))
    
    story.append(Paragraph("<b>Containment & Recovery</b>", styles['subsection']))
    story.append(Paragraph("# Apply hardening", styles['code']))
    story.append(Paragraph("harden-cinematic", styles['code']))
    story.append(Paragraph("# Generate incident report", styles['code']))
    story.append(Paragraph("rmon export pdf", styles['code']))
    
    story.append(PageBreak())
    story.append(Paragraph("8.3 Penetration Testing Workflow", styles['section']))
    story.append(Paragraph("<b>Phase 1: Reconnaissance</b>", styles['subsection']))
    story.append(Paragraph("# Full recon on target", styles['code']))
    story.append(Paragraph("dst-recon-full", styles['code']))
    story.append(Paragraph("# Network mapping", styles['code']))
    story.append(Paragraph("nmap -A target.com", styles['code']))
    
    story.append(Paragraph("<b>Phase 2: Scanning & Enumeration</b>", styles['subsection']))
    story.append(Paragraph("# Vulnerability scan", styles['code']))
    story.append(Paragraph("exploitcheck --target target.com", styles['code']))
    story.append(Paragraph("# Web application testing", styles['code']))
    story.append(Paragraph("websec", styles['code']))
    
    story.append(Paragraph("<b>Phase 3: Exploitation</b>", styles['subsection']))
    story.append(Paragraph("# Launch Metasploit", styles['code']))
    story.append(Paragraph("msfconsole", styles['code']))
    
    story.append(Paragraph("<b>Phase 4: Reporting</b>", styles['subsection']))
    story.append(Paragraph("# Generate comprehensive report", styles['code']))
    story.append(Paragraph("# Use export options from each module", styles['code']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 9: REPORT GENERATION
    # ====================================================================
    story.append(Paragraph("9. REPORT GENERATION", styles['chapter']))
    
    story.append(Paragraph("9.1 Report Types", styles['section']))
    report_formats = [
        ("JSON", "--json", "Data import/export, automation"),
        ("PDF", "--pdf", "Documentation, compliance"),
        ("HTML", "--html", "Web viewing, sharing"),
    ]
    fmt_data = [[f"<b>{fmt}</b>", cmd, desc] for fmt, cmd, desc in report_formats]
    fmt_table = Table(fmt_data, colWidths=[70, 120, 280])
    fmt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['table_header']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(fmt_table)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("9.2 Report Location", styles['section']))
    story.append(Paragraph("<b>Windows:</b>", styles['body']))
    story.append(Paragraph("C:\\Users\\[USERNAME]\\dsterminal_workspace\\reports\\", styles['code']))
    story.append(Paragraph("<b>Linux:</b>", styles['body']))
    story.append(Paragraph("/home/[USERNAME]/dsterminal_workspace/reports/", styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>File Naming Convention:</b>", styles['subsection']))
    story.append(Paragraph("[module]_report_[YYYYMMDD]_[HHMMSS].format", styles['code']))
    story.append(Paragraph("Example:", styles['code']))
    story.append(Paragraph("ransomware_report_20260722_154453.pdf", styles['code']))
    story.append(Paragraph("hardening_20260722_142115.pdf", styles['code']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 10: BEST PRACTICES
    # ====================================================================
    story.append(Paragraph("10. BEST PRACTICES", styles['chapter']))
    
    story.append(Paragraph("10.1 Security Best Practices", styles['section']))
    story.append(Paragraph("<b>Before Using DSTerminal</b>", styles['subsection']))
    before_practices = [
        ("âœ… Get Authorization", "Always have written permission"),
        ("âœ… Document Activities", "Keep audit trails"),
        ("âœ… Use Proper Credentials", "Run as admin/sudo when needed"),
        ("âœ… Secure Your Workspace", "Protect report files"),
        ("âœ… Regular Updates", "Keep DSTerminal updated"),
    ]
    before_data = [[f"<b>{p}</b>", desc] for p, desc in before_practices]
    before_table = Table(before_data, colWidths=[130, 340])
    before_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(before_table)
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>During Usage</b>", styles['subsection']))
    during_practices = [
        ("âœ… Start with Help", "Learn before using"),
        ("âœ… Use Tab Completion", "Faster, fewer errors"),
        ("âœ… Monitor Resource Usage", "Watch CPU/RAM"),
        ("âœ… Generate Reports", "Document findings"),
        ("âœ… Verify Results", "Double-check critical findings"),
    ]
    during_data = [[f"<b>{p}</b>", desc] for p, desc in during_practices]
    during_table = Table(during_data, colWidths=[130, 340])
    during_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['accent2']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(during_table)
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>After Usage</b>", styles['subsection']))
    after_practices = [
        ("âœ… Logout Properly", "Use exit command"),
        ("âœ… Secure Reports", "Encrypt sensitive reports"),
        ("âœ… Share Findings", "Report to security team"),
        ("âœ… Update Knowledge", "Learn from findings"),
    ]
    after_data = [[f"<b>{p}</b>", desc] for p, desc in after_practices]
    after_table = Table(after_data, colWidths=[130, 340])
    after_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(after_table)
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 11: TROUBLESHOOTING
    # ====================================================================
    story.append(Paragraph("11. TROUBLESHOOTING", styles['chapter']))
    
    story.append(Paragraph("11.1 Common Issues", styles['section']))
    story.append(Paragraph("<b>Issue: DSTerminal Won't Start</b>", styles['subsection']))
    story.append(Paragraph("<b>Windows:</b>", styles['body']))
    story.append(Paragraph("â€¢ Run as Administrator", styles['body']))
    story.append(Paragraph("â€¢ Check antivirus", styles['body']))
    story.append(Paragraph("â€¢ Reinstall", styles['body']))
    story.append(Paragraph("<b>Linux:</b>", styles['body']))
    story.append(Paragraph("â€¢ Check permissions: chmod +x dsterminal", styles['code']))
    story.append(Paragraph("â€¢ Check dependencies", styles['code']))
    story.append(Paragraph("â€¢ Run with sudo", styles['code']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Issue: Feature Not Working</b>", styles['subsection']))
    story.append(Paragraph("â€¢ No Network Scan: Install nmap, check internet, check firewall", styles['body']))
    story.append(Paragraph("â€¢ Encryption Fails: Check permissions, generate new key, check disk space", styles['body']))
    story.append(Paragraph("â€¢ Ransomware Monitor Fails: Run as admin, check workspace path, restart service", styles['body']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("11.2 Log Location", styles['section']))
    story.append(Paragraph("<b>Windows:</b>", styles['body']))
    story.append(Paragraph("C:\\Users\\[USERNAME]\\dsterminal_workspace\\logs\\", styles['code']))
    story.append(Paragraph("<b>Linux:</b>", styles['body']))
    story.append(Paragraph("/home/[USERNAME]/dsterminal_workspace/logs/", styles['code']))
    story.append(Paragraph("<b>Log File Format:</b>", styles['body']))
    story.append(Paragraph("dsterminal_YYYYMMDD.log", styles['code']))
    story.append(Paragraph("Example: dsterminal_20260722.log", styles['code']))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("11.3 Support Resources", styles['section']))
    story.append(Paragraph("â€¢ Help Command: help in terminal", styles['body']))
    story.append(Paragraph("â€¢ Built-in Manual: Command reference", styles['body']))
    story.append(Paragraph("â€¢ Online Docs: https://www.dsterminal.com/docs", styles['body']))
    story.append(Paragraph("â€¢ Email: support@dsterminal.com", styles['body']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 12: GLOSSARY
    # ====================================================================
    story.append(Paragraph("12. GLOSSARY", styles['chapter']))
    
    story.append(Paragraph("12.1 Key Terms", styles['section']))
    key_terms = [
        ("SOC", "Security Operations Center"),
        ("IOC", "Indicator of Compromise"),
        ("TTP", "Tactics, Techniques, Procedures"),
        ("MTTR", "Mean Time to Respond"),
        ("CVE", "Common Vulnerabilities and Exposures"),
        ("AES", "Advanced Encryption Standard"),
        ("GCM", "Galois/Counter Mode"),
        ("LAA", "Locally Administered Address"),
        ("SIP", "System Integrity Protection"),
    ]
    term_data = [[f"<b>{term}</b>", desc] for term, desc in key_terms]
    term_table = Table(term_data, colWidths=[80, 390])
    term_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(term_table)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("12.2 Module Glossary", styles['section']))
    mod_terms = [
        ("VirusTotal", "Threat intelligence platform"),
        ("SQLMap", "SQL injection testing tool"),
        ("Nmap", "Network mapping tool"),
        ("Metasploit", "Exploitation framework"),
        ("Nikto", "Web server scanner"),
        ("ClamAV", "Antivirus engine"),
    ]
    mod_term_data = [[f"<b>{term}</b>", desc] for term, desc in mod_terms]
    mod_term_table = Table(mod_term_data, colWidths=[80, 390])
    mod_term_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['accent2']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(mod_term_table)
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 13: GETTING STARTED CHECKLIST
    # ====================================================================
    story.append(Paragraph("13. GETTING STARTED CHECKLIST", styles['chapter']))
    
    story.append(Paragraph("<b>First Launch</b>", styles['section']))
    story.append(Paragraph("â˜ Download DSTerminal installer", styles['body']))
    story.append(Paragraph("â˜ Install with default settings", styles['body']))
    story.append(Paragraph("â˜ Launch as Administrator (Windows) / sudo (Linux)", styles['body']))
    story.append(Paragraph("â˜ Wait for all 3 initialization stages", styles['body']))
    story.append(Paragraph("â˜ Type help to view all commands", styles['body']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>First Steps</b>", styles['section']))
    story.append(Paragraph("â˜ Try system status to check health", styles['body']))
    story.append(Paragraph("â˜ Try scan-quick for quick system scan", styles['body']))
    story.append(Paragraph("â˜ Explore websec for web security testing", styles['body']))
    story.append(Paragraph("â˜ Test sqllab for SQL injection learning", styles['body']))
    story.append(Paragraph("â˜ Generate first report", styles['body']))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Regular Usage</b>", styles['section']))
    story.append(Paragraph("â˜ Monitor daily with rmon", styles['body']))
    story.append(Paragraph("â˜ Run periodic vulnerability scans", styles['body']))
    story.append(Paragraph("â˜ Keep modules updated", styles['body']))
    story.append(Paragraph("â˜ Generate reports for documentation", styles['body']))
    story.append(Paragraph("â˜ Review findings and apply fixes", styles['body']))
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 14: QUICK REFERENCE CARD
    # ====================================================================
    story.append(Paragraph("14. QUICK REFERENCE CARD", styles['chapter']))
    
    story.append(Paragraph("<b>Essential Commands</b>", styles['section']))
    qr_cmds = [
        ("help", "Show all commands"),
        ("system status", "System health"),
        ("scan-quick", "Quick scan"),
        ("vt-scan", "VirusTotal"),
        ("sqllab", "SQL Lab"),
        ("nmap", "Network scan"),
        ("harden", "Hardening"),
        ("encrypt", "Encrypt files"),
        ("websec", "Web security"),
        ("rmon", "Ransomware monitor"),
        ("wifi-audit", "WiFi audit"),
        ("exploitcheck", "Vulnerability check"),
        ("dst-investigate", "Financial forensics"),
        ("certcheck", "SSL audit"),
        ("exit", "Exit DSTerminal"),
    ]
    qr_data = [[f"<b>{cmd}</b>", desc] for cmd, desc in qr_cmds]
    qr_table = Table(qr_data, colWidths=[140, 330])
    qr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(qr_table)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Module Shortcuts</b>", styles['section']))
    shortcuts = [
        ("sys", "system"),
        ("scan", "system scan"),
        ("ws", "websec"),
        ("enc", "encrypt"),
        ("rec", "recon"),
        ("rmon", "ransomware monitor"),
    ]
    short_data = [[f"<b>{short}</b>", full] for short, full in shortcuts]
    short_table = Table(short_data, colWidths=[100, 370])
    short_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['accent2']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(short_table)
    
    story.append(PageBreak())
    
    # ====================================================================
    # CHAPTER 15: CONTACT & SUPPORT
    # ====================================================================
    story.append(Paragraph("15. CONTACT & SUPPORT", styles['chapter']))
    
    story.append(Paragraph("<b>Developer Information</b>", styles['section']))
    dev_info = [
        ("Developer", "Spark Wilson Spink"),
        ("Organization", "Stark Expo Tech Exchange"),
        ("Email", "support@dsterminal.com"),
        ("Website", "https://www.dsterminal.com"),
        ("Version", "v4.0.0.113"),
        ("License", "Commercial / Educational"),
    ]
    dev_data = [[f"<b>{item}</b>", value] for item, value in dev_info]
    dev_table = Table(dev_data, colWidths=[120, 350])
    dev_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['code_bg']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(dev_table)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Disclaimer</b>", styles['section']))
    story.append(Paragraph(
        "âš ï¸ NOTICE: DSTerminal is designed for use in LEGITIMATE and AUTHORIZED "
        "environments ONLY. Always obtain proper authorization before scanning systems. "
        "Unauthorized testing is illegal and unethical. All activities are logged for "
        "audit purposes.",
        styles['body']
    ))
    
    # ====================================================================
    # FINAL PAGE
    # ====================================================================
    story.append(PageBreak())
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("DSTERMINAL", styles['title']))
    story.append(Paragraph("Cyber-Ops Platform", styles['title']))
    story.append(Spacer(1, 0.3*inch))
    
    footer_style = ParagraphStyle(
        'FooterText',
        parent=styles['body'],
        fontSize=12,
        textColor=COLORS['text_dim'],
        alignment=TA_CENTER
    )
    story.append(Paragraph("""
    <i>Empowering cybersecurity professionals with AI-driven defense operations.</i>
    """, footer_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("â•" * 50, styles['body']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Â© 2024 Stark Expo Tech Exchange", footer_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    story.append(Paragraph("Document Version: 1.0", footer_style))
    story.append(Paragraph("Based on DSTerminal v4.0.0.113", footer_style))
    
    # ====================================================================
    # Build PDF with header/footer functions
    # ====================================================================
    doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
    
    print(f"\nâœ… PDF Generated Successfully!")
    print(f"ðŸ“„ File: {filename}")
    print(f"ðŸ“ Pages: {page_counter['count']}")
    print(f"ðŸ“… Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nðŸ“Š Document Statistics:")
    print(f"   â€¢ Total Pages: {page_counter['count']}")
    print(f"   â€¢ Chapters: 15")
    print(f"   â€¢ Modules: 15")
    print(f"   â€¢ Commands: 50+")
    print(f"   â€¢ Tables: 20+")
    print(f"   â€¢ Code Blocks: 60+")
    print("\nðŸ” Document Features:")
    print("   â€¢ Diagonal Watermark")
    print("   â€¢ Custom Headers & Footers")
    print("   â€¢ Cyber Security Theme")
    print("   â€¢ Professional Formatting")
    print("   â€¢ Complete Module Coverage")


if __name__ == "__main__":
    generate_pdf()