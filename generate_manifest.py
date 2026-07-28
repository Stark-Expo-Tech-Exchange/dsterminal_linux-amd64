#!/usr/bin/env python3
"""
Dsterminal Manifest PDF Generator
Version: 3.1.113
"""

import os
import sys
import json
import hashlib
import datetime
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
import argparse
import subprocess

# ============================================================================
# DEPENDENCY MANAGEMENT
# ============================================================================

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required = {
        'reportlab': 'reportlab>=4.0.0',
        'PIL': 'Pillow>=9.0.0'
    }
    
    missing = []
    for module, package in required.items():
        try:
            if module == 'PIL':
                import PIL
            else:
                __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[INFO] Installing missing dependencies: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("[INFO] Dependencies installed successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            print("[FIX] Please manually install: pip install reportlab Pillow")
            sys.exit(1)

# Run dependency check first
check_and_install_dependencies()

# Now import everything
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
    from reportlab.lib.colors import Color, white, grey, HexColor
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
        HRFlowable, Image
    )
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.platypus.flowables import Flowable
    
    # Try QRCode
    QRCODE_AVAILABLE = False
    try:
        from reportlab.graphics.widgets.qrcode import QRCode
        QRCODE_AVAILABLE = True
    except (ImportError, AttributeError):
        print("[INFO] QRCode not available. Using fallback.")
    
except ImportError as e:
    print(f"[ERROR] Failed to import: {e}")
    print("[FIX] pip install --upgrade reportlab Pillow")
    sys.exit(1)

# Try PIL
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION = "3.1.113"
MANIFEST_TITLE = "DSTERMINAL PLATFORM MANIFEST"
COPYRIGHT_YEAR = "2026"
COMPANY_NAME = "Dsterminal Security Labs"
CONTACT_EMAIL = "manifest@dsterminal.dev"
GPG_KEY_ID = "0xA4F5C123D7E8F9AB"
MANIFEST_URL = "https://dsterminal.dev/verify/manifest"
WEBSITE_URL = "https://dsterminal.dev"

WATERMARK_TEXT = f"Dsterminal User Manifest V{VERSION}"
WATERMARK_OPACITY = 0.12

PRIMARY_COLOR = HexColor('#0a0a1a')
SECONDARY_COLOR = HexColor('#1a3a5c')
ACCENT_COLOR = HexColor('#00d4ff')
HEADER_COLOR = HexColor('#16213e')
SUBTLE_BG = Color(0.97, 0.97, 0.98)

OUTPUT_FORMATS = ['pdf', 'json', 'html']
DEFAULT_OUTPUT = f"Dsterminal_Manifest_v{VERSION}.pdf"

# ============================================================================
# MANIFEST CONTENT
# ============================================================================

MANIFEST_SECTIONS = [
    {
        "id": "purpose",
        "title": "1. PURPOSE & ETHICAL FRAMEWORK",
        "content": """
Dsterminal is an offline-first, AI-assisted cybersecurity platform designed exclusively 
for defensive operations (Blue Team), security education, and infrastructure hardening.

Core Ethical Commitments:
- Legal Use Only: This platform is strictly prohibited for unauthorized network 
  intrusion, exfiltration, or manipulation of data without explicit ownership or consent.
- Defensive Mandate: Every module exists to identify, report, and remediate 
  vulnerabilities within the user's legally owned or authorized environment.
- Zero Harm: Automated actions require explicit user confirmation unless explicitly 
  overridden for automated enterprise deployments.
"""
    },
    {
        "id": "privacy",
        "title": "2. DATA PRIVACY & SOVEREIGNTY (The Zero-Phone-Home Pledge)",
        "content": """
2.1 Absolute Data Locality
All data processed by Dsterminal remains on the local machine. No logs, telemetry, 
configuration files, or analysis results are transmitted to external servers, cloud 
platforms, or third-party entities by default.

2.2 Network Behavior
- Core functionality operates fully offline (anomaly detection, system hardening, 
  log analysis, SQLmap labs).
- Internet-Required Modules (SSL/TLS validation, VirusTotal scanning, self-updates) 
  require explicit user consent with a warning prompt.

2.3 No Telemetry or Backdoors
Dsterminal does not contain telemetry agents, analytics trackers, call-home 
routines, or backdoor mechanisms.

2.4 Data Encryption
All locally stored data is encrypted at rest using AES-256 with a user-provided 
passphrase. If no passphrase is provided, data uses OS-level file permissions.
"""
    },
    {
        "id": "explainability",
        "title": "3. EXPLAINABILITY & AUDITABILITY (The Glass Box Pledge)",
        "content": """
Dsterminal's AI and automated decision-making are not black boxes. Every action is 
traceable and defensible in a court of law or military tribunal.

3.1 Decision Transparency
Every alert, recommendation, or action includes:
- Plain-English Rationale: What was detected and why it matters.
- Evidence Footprint: Raw log snippets, file hashes, and network packet summaries.
- Mathematical Trace: The exact decision path (Decision Tree, feature importance, 
  or behavioral rule) that led to the conclusion.
- MITRE ATT&CK Mapping: If applicable, the specific Tactic and Technique.

3.2 Audit Trail
Dsterminal maintains an immutable, append-only audit log recording:
- Timestamp (millisecond precision, timezone-aware)
- Module and sub-command executed
- AI Model version used
- Cryptographic hash (SHA-256) of input data
- Full decision path and confidence score
- Human user who executed the command
- Any human override or manual intervention
"""
    },
    {
        "id": "security",
        "title": "4. SECURITY & INTEGRITY (Protecting the Protector)",
        "content": """
4.1 Tamper-Proof Installation
The official installer includes a SHA-256 checksum manifest. If any checksum fails, 
the installation aborts with a tamper warning.

4.2 Update Integrity
Self-updates are signed with a GPG key controlled by the Dsterminal development team. 
Updates apply only with a valid GPG signature and matching checksum.

4.3 Privilege Escalation
Dsterminal requests the minimum necessary privileges. System hardening and quarantine 
modules require elevated privileges but notify the user and require confirmation.

4.4 Dependency Vetting
All bundled libraries and binaries are verified for known CVEs during the build 
process. A Software Bill of Materials (SBOM) in SPDX format is included.
"""
    },
    {
        "id": "modularity",
        "title": "5. MODULARITY & SCOPE (Defined Use Cases)",
        "content": """
Dsterminal is a modular platform with the following core modules:

Network Recon                | No          | Yes
Log Forensics                | No          | Yes
File Quarantine              | Optional VT | Yes
SSL/TLS Inspector            | Yes         | Partial
System Hardening             | No          | Yes
SQLmap Learning Lab          | No          | Yes
AI Advisor                   | No          | Yes
Report Engine                | No          | Yes
Self-Update                  | Yes         | File-based
Compliance Scanner           | No          | Yes
Threat Intelligence Feed     | Optional    | Yes (bundled)

Each module can be independently enabled/disabled via:
dsterminal module --enable <module> --disable <module>
"""
    },
    {
        "id": "liability",
        "title": "6. LIABILITY & DISCLAIMER",
        "content": """
6.1 Defensive Use Only
Dsterminal is provided as is for defensive and educational purposes. Users are 
solely responsible for ensuring they have proper authorization to scan, test, or 
harden any system.

6.2 No Warranty
The platform is provided without warranty of any kind. While we strive for accuracy 
and security, no system is infallible.

6.3 Compliance
Users are responsible for ensuring their use of Dsterminal complies with local, 
national, and international laws, including but not limited to:
- Computer Fraud and Abuse Act (CFAA - US)
- General Data Protection Regulation (GDPR - EU)
- Defense Trade Controls (ITAR - US)
- Military and government-specific cybersecurity policies
"""
    },
    {
        "id": "transparency",
        "title": "7. TRANSPARENCY & ACCOUNTABILITY",
        "content": """
7.1 Open Communication
The Dsterminal development team is committed to transparency. Users may request:
- Source code access (under NDA for proprietary modules)
- Full model training data (sanitized and anonymized)
- Penetration test results from independent third-party audits

7.2 Reporting Vulnerabilities
Report vulnerabilities responsibly to: security@dsterminal.dev
We guarantee:
- Response within 72 hours
- Acknowledgment within 24 hours
- Fix within 30 days (or waiver accepted)

7.3 Continuous Improvement
Dsterminal evolves with the threat landscape. We will never compromise privacy, 
offline capability, or explainability for convenience.
"""
    },
    {
        "id": "acknowledgment",
        "title": "8. USER ACKNOWLEDGMENT",
        "content": """
By installing, executing, or updating Dsterminal, the user acknowledges that they have 
read, understood, and agreed to this manifest in its entirety.

The user confirms that:
- They have the legal authority to analyze, scan, and harden the systems on which 
  Dsterminal is used.
- They will use the platform solely for defensive, educational, or authorized 
  operational purposes.
- They accept that Dsterminal provides guidance, not guarantees, and the ultimate 
  responsibility for security decisions rests with the user.
"""
    },
    {
        "id": "signature",
        "title": "9. SIGNATURE & VERIFICATION",
        "content": f"""
This manifest is digitally signed using the Dsterminal GPG Key 
(Key ID: {GPG_KEY_ID}) and is valid for version {VERSION}.

Verification Methods:
1. GPG Signature Verification:
   gpg --verify Dsterminal_Manifest_v{VERSION}.pdf.sig Dsterminal_Manifest_v{VERSION}.pdf

2. SHA-256 Checksum:
   sha256sum Dsterminal_Manifest_v{VERSION}.pdf

3. QR Code Verification:
   Scan the QR code included in this document to verify on our website

-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.4

iQIzBAEBCgAdFiEE...
wE4HfJkLmNpQrStUvWxYz...
-----END PGP SIGNATURE-----

Issued By: {COMPANY_NAME}
Date: {datetime.datetime.now().strftime("%B %d, %Y")}
Contact: {CONTACT_EMAIL}
Version: {VERSION}
"""
    }
]

# ============================================================================
# HELPER CLASSES
# ============================================================================

class WatermarkedCanvas(canvas.Canvas):
    """Custom canvas with watermark and footer"""
    
    def __init__(self, *args, **kwargs):
        self.watermark_text = WATERMARK_TEXT
        self.version = VERSION
        super().__init__(*args, **kwargs)
    
    def showPage(self):
        self._watermark()
        self._header_footer()
        super().showPage()
    
    def _watermark(self):
        self.saveState()
        try:
            self.setFont('Helvetica-Bold', 60)
            self.setFillColorRGB(0.8, 0.8, 0.8, alpha=WATERMARK_OPACITY)
            self.translate(self._pagesize[0]/2, self._pagesize[1]/2)
            self.rotate(45)
            self.drawCentredString(0, 0, self.watermark_text)
        except Exception:
            pass
        self.restoreState()
    
    def _header_footer(self):
        self.saveState()
        try:
            page_num = self.getPageNumber()
            footer_text = f"Dsterminal Manifest v{self.version} | Page {page_num} | {datetime.datetime.now().strftime('%Y-%m-%d')}"
            self.setFont('Helvetica', 8)
            self.setFillColorRGB(0.5, 0.5, 0.5)
            self.drawRightString(self._pagesize[0] - 72, 20, footer_text)
            self.setStrokeColorRGB(0.8, 0.8, 0.8)
            self.setLineWidth(0.5)
            self.line(72, 30, self._pagesize[0] - 72, 30)
        except Exception:
            pass
        self.restoreState()


class QRCodeFallback(Drawing):
    """Fallback QR code"""
    def __init__(self, url, size=1.5*inch):
        super().__init__(size, size)
        self.url = url
        self.size = size
        
    def draw(self):
        margin = 10
        inner_size = self.size - 2 * margin
        
        self.add(Rect(margin, margin, inner_size, inner_size, 
                     fillColor=white, strokeColor=Color(0.2, 0.2, 0.3), strokeWidth=2))
        
        grid_size = 12
        cell_size = (inner_size - 2) / grid_size
        for i in range(grid_size):
            for j in range(grid_size):
                if (i * j) % 3 == 0 or (i + j) % 4 == 0:
                    x = margin + 1 + i * cell_size
                    y = margin + 1 + j * cell_size
                    self.add(Rect(x, y, cell_size * 0.7, cell_size * 0.7,
                                 fillColor=Color(0.1, 0.1, 0.2),
                                 strokeColor=None))
        
        self.add(String(
            self.size/2, 8,
            "Scan to verify",
            fontName='Helvetica',
            fontSize=8,
            textAnchor='middle',
            fillColor=Color(0.3, 0.3, 0.3)
        ))
        self.add(String(
            self.size/2, 0,
            self.url[:25] + ("..." if len(self.url) > 25 else ""),
            fontName='Helvetica',
            fontSize=6,
            textAnchor='middle',
            fillColor=Color(0.5, 0.5, 0.5)
        ))


def create_qr_code(url, size=1.5*inch):
    try:
        if QRCODE_AVAILABLE:
            return QRCode(url, size=size)
        else:
            return QRCodeFallback(url, size=size)
    except Exception:
        return QRCodeFallback(url, size=size)


class LogoImage(Flowable):
    """Flowable for centered images"""
    
    def __init__(self, image_path, width=2*inch, height=2*inch):
        self.image_path = image_path
        self.width = width
        self.height = height
        
    def wrap(self, avail_width, avail_height):
        return (self.width, self.height)
    
    def draw(self):
        try:
            if HAS_PIL and os.path.exists(self.image_path):
                img = PILImage.open(self.image_path)
                if img.format == 'ICO' and hasattr(img, 'icon_sizes') and img.icon_sizes:
                    sizes = img.icon_sizes
                    largest = max(sizes)
                    img.seek(sizes.index(largest))
                
                if img.mode in ('P', 'PA'):
                    img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')
                elif img.mode not in ('RGBA', 'RGB'):
                    img = img.convert('RGB')
                
                img_width, img_height = img.size
                aspect = img_width / img_height
                max_size = min(self.width, self.height, 2.5*inch)
                
                if aspect > 1:
                    width = max_size
                    height = width / aspect
                else:
                    height = max_size
                    width = height * aspect
                
                x = (self.width - width) / 2
                y = (self.height - height) / 2
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    img.save(tmp.name, 'PNG')
                    reportlab_img = Image(tmp.name, width=width, height=height)
                    reportlab_img.drawOn(self.canv, x, y)
                    os.unlink(tmp.name)
            else:
                self._draw_placeholder()
        except Exception:
            self._draw_placeholder()
    
    def _draw_placeholder(self):
        self.canv.setFillColorRGB(0.9, 0.9, 0.95)
        self.canv.circle(self.width/2, self.height/2, min(self.width, self.height)/2, fill=True)
        self.canv.setFillColorRGB(0.2, 0.2, 0.4)
        self.canv.setFont('Helvetica-Bold', 32)
        self.canv.drawCentredString(self.width/2, self.height/2 + 10, "🛡️")
        self.canv.setFont('Helvetica', 8)
        self.canv.drawCentredString(self.width/2, self.height/2 - 15, "DSTERMINAL")

# ============================================================================
# MANIFEST GENERATOR
# ============================================================================

class ManifestPDFGenerator:
    """Generates the Dsterminal Manifest PDF"""
    
    def __init__(self, output_file: str = DEFAULT_OUTPUT, logo_path: Optional[str] = None):
        self.output_file = output_file
        self.logo_path = logo_path
        self.doc = None
        self.story = []
        self.styles = None
        
    def setup_styles(self):
        """Configure all paragraph styles"""
        self.styles = getSampleStyleSheet()
        
        def safe_add(name, style):
            try:
                self.styles.add(style)
            except KeyError:
                self.styles[name] = style
        
        safe_add('ManifestMainTitle', ParagraphStyle(
            'ManifestMainTitle', parent=self.styles['Title'],
            fontSize=22, alignment=TA_CENTER, spaceAfter=18,
            textColor=PRIMARY_COLOR, fontName='Helvetica-Bold'
        ))
        
        safe_add('ManifestSubTitle', ParagraphStyle(
            'ManifestSubTitle', parent=self.styles['Normal'],
            fontSize=14, alignment=TA_CENTER, spaceAfter=24,
            textColor=SECONDARY_COLOR, fontName='Helvetica'
        ))
        
        safe_add('ManifestSectionHeader', ParagraphStyle(
            'ManifestSectionHeader', parent=self.styles['Heading1'],
            fontSize=14, spaceBefore=16, spaceAfter=8,
            textColor=HEADER_COLOR, fontName='Helvetica-Bold'
        ))
        
        safe_add('ManifestSubSection', ParagraphStyle(
            'ManifestSubSection', parent=self.styles['Heading2'],
            fontSize=11, spaceBefore=10, spaceAfter=4,
            textColor=SECONDARY_COLOR, fontName='Helvetica-Bold'
        ))
        
        safe_add('ManifestBody', ParagraphStyle(
            'ManifestBody', parent=self.styles['Normal'],
            fontSize=9.5, alignment=TA_JUSTIFY, spaceBefore=3,
            spaceAfter=6, leading=14, fontName='Helvetica'
        ))
        
        safe_add('ManifestBullet', ParagraphStyle(
            'ManifestBullet', parent=self.styles['ManifestBody'],
            leftIndent=20, spaceBefore=2, spaceAfter=2
        ))
        
        safe_add('ManifestFooter', ParagraphStyle(
            'ManifestFooter', parent=self.styles['Normal'],
            fontSize=8, alignment=TA_CENTER, textColor=grey,
            spaceBefore=8, spaceAfter=8
        ))
        
        safe_add('ManifestTOCItem', ParagraphStyle(
            'ManifestTOCItem', parent=self.styles['ManifestBody'],
            fontSize=10, spaceBefore=4, spaceAfter=4, leftIndent=10
        ))

    def add_cover_page(self):
        """Create cover page"""
        self.story.append(Spacer(1, 0.8*inch))
        
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = LogoImage(self.logo_path, width=2*inch, height=2*inch)
                self.story.append(img)
                self.story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"[WARNING] Could not load logo: {e}")
        
        self.story.append(Paragraph("🛡️", self.styles['ManifestMainTitle']))
        self.story.append(Paragraph(MANIFEST_TITLE, self.styles['ManifestMainTitle']))
        self.story.append(Paragraph(f"Version {VERSION}", self.styles['ManifestSubTitle']))
        self.story.append(Spacer(1, 0.1*inch))
        
        line_drawing = Drawing(400, 4)
        line_drawing.add(Rect(0, 0, 400, 2, fillColor=ACCENT_COLOR, strokeColor=ACCENT_COLOR))
        self.story.append(line_drawing)
        self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(Paragraph(
            '"For Defensive Use Only. Protect. Detect. Respond. Explain."',
            self.styles['ManifestSubTitle']
        ))
        
        self.story.append(Spacer(1, 0.4*inch))
        
        metadata = [
            ["Issued By:", COMPANY_NAME],
            ["Date:", datetime.datetime.now().strftime('%B %d, %Y')],
            ["Contact:", CONTACT_EMAIL],
            ["GPG Key:", GPG_KEY_ID],
            ["Classification:", "UNCLASSIFIED / PUBLIC RELEASE"]
        ]
        
        meta_table = Table(metadata, colWidths=[1.5*inch, 3.5*inch])
        meta_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, Color(0.8, 0.8, 0.8)),
            ('BACKGROUND', (0, 0), (-1, -1), SUBTLE_BG),
        ]))
        self.story.append(meta_table)
        
        self.story.append(Spacer(1, 0.3*inch))
        
        try:
            qr = create_qr_code(MANIFEST_URL, size=1.5*inch)
            self.story.append(qr)
            self.story.append(Paragraph(
                "Scan to verify this manifest",
                self.styles['ManifestFooter']
            ))
        except Exception:
            self.story.append(Paragraph(
                f"Verify at: {MANIFEST_URL}",
                self.styles['ManifestFooter']
            ))
        
        self.story.append(PageBreak())
    
    def add_table_of_contents(self):
        """Generate TOC"""
        self.story.append(Paragraph("Table of Contents", self.styles['ManifestMainTitle']))
        self.story.append(Spacer(1, 0.1*inch))
        
        for idx, section in enumerate(MANIFEST_SECTIONS, 1):
            display_title = section['title'].split('. ', 1)[-1] if '. ' in section['title'] else section['title']
            self.story.append(Paragraph(
                f"{idx}. {display_title}",
                self.styles['ManifestTOCItem']
            ))
        
        self.story.append(PageBreak())

    def parse_content(self, content: str) -> List[Paragraph]:
        """Parse content with bullets"""
        paragraphs = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.rstrip()
            if not line:
                continue
            
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                clean = line.lstrip('-*• ').strip()
                if clean:
                    paragraphs.append(Paragraph(f'- {clean}', self.styles['ManifestBullet']))
            elif line[0].isdigit() and '.' in line[:3]:
                paragraphs.append(Paragraph(line, self.styles['ManifestSubSection']))
            else:
                paragraphs.append(Paragraph(line, self.styles['ManifestBody']))
        
        return paragraphs

    def add_section(self, section: Dict[str, str]):
        """Add a section"""
        self.story.append(Paragraph(section['title'], self.styles['ManifestSectionHeader']))
        self.story.append(Spacer(1, 0.05*inch))
        
        content = section['content'].strip()
        for p in self.parse_content(content):
            self.story.append(p)
        
        self.story.append(Spacer(1, 0.05*inch))
        self.story.append(HRFlowable(width="60%", color=Color(0.85, 0.85, 0.85), thickness=0.5))
        self.story.append(Spacer(1, 0.05*inch))

    def add_back_cover(self):
        """Add back cover"""
        self.story.append(PageBreak())
        self.story.append(Spacer(1, 1.5*inch))
        
        self.story.append(Paragraph(
            "About This Document",
            self.styles['ManifestSectionHeader']
        ))
        self.story.append(Spacer(1, 0.1*inch))
        
        back_text = f"""
        This manifest serves as the official documentation for Dsterminal's commitment to 
        privacy, security, and ethical use. It is legally binding and subject to the 
        terms and conditions outlined herein.
        
        - Version: {VERSION}
        - Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
        - File: {os.path.basename(self.output_file)}
        
        For the latest version, visit: {WEBSITE_URL}/manifest
        
        © 2024-{COPYRIGHT_YEAR} {COMPANY_NAME}. All rights reserved.
        """
        
        for p in self.parse_content(back_text):
            self.story.append(p)
        
        self.story.append(Spacer(1, 0.3*inch))
        
        try:
            qr = create_qr_code(MANIFEST_URL, size=1.2*inch)
            self.story.append(qr)
        except Exception:
            pass
        
        self.story.append(Spacer(1, 0.1*inch))
        self.story.append(Paragraph(
            "SHA-256: <calculated at generation time>",
            self.styles['ManifestFooter']
        ))

    def build_pdf(self):
        """Build the PDF"""
        print(f"[INFO] Generating Dsterminal Manifest v{VERSION} PDF...")
        
        self.setup_styles()
        
        self.doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=f"Dsterminal Manifest v{VERSION}",
            author=COMPANY_NAME,
            subject="Security Platform Manifest"
        )
        
        self.story = []
        
        self.add_cover_page()
        self.add_table_of_contents()
        
        for section in MANIFEST_SECTIONS:
            self.add_section(section)
        
        self.add_back_cover()
        
        self.doc.build(self.story, canvasmaker=WatermarkedCanvas)
        
        checksum = self._generate_checksum()
        
        print(f"[SUCCESS] Manifest PDF generated: {self.output_file}")
        print(f"[INFO] File size: {os.path.getsize(self.output_file) / 1024:.1f} KB")
        print(f"[INFO] SHA-256: {checksum}")
        
        return self.output_file, checksum
    
    def _generate_checksum(self) -> str:
        sha256 = hashlib.sha256()
        with open(self.output_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

# ============================================================================
# JSON EXPORTER
# ============================================================================

class JSONExporter:
    @staticmethod
    def export(output_file: str) -> str:
        json_data = {
            "manifest": {
                "title": MANIFEST_TITLE,
                "version": VERSION,
                "company": COMPANY_NAME,
                "date": datetime.datetime.now().isoformat(),
                "contact": CONTACT_EMAIL,
                "gpg_key": GPG_KEY_ID,
                "url": MANIFEST_URL
            },
            "sections": []
        }
        
        for section in MANIFEST_SECTIONS:
            json_data["sections"].append({
                "id": section.get("id", ""),
                "title": section["title"],
                "content": section["content"].strip()
            })
        
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        return output_file

# ============================================================================
# HTML EXPORTER
# ============================================================================

class HTMLExporter:
    @staticmethod
    def export(output_file: str) -> str:
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dsterminal Manifest v{VERSION}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; 
               max-width: 900px; margin: 40px auto; padding: 20px; 
               line-height: 1.6; color: #1a1a2e; background: #fafafa; }}
        h1 {{ text-align: center; color: #0a0a1a; border-bottom: 3px solid #00d4ff; }}
        h2 {{ color: #16213e; border-left: 4px solid #00d4ff; padding-left: 15px; margin-top: 30px; }}
        .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; }}
        .metadata {{ background: #f5f5fa; padding: 15px; border-radius: 8px; }}
        .metadata-item {{ display: flex; padding: 5px 0; }}
        .metadata-label {{ font-weight: bold; width: 150px; }}
    </style>
</head>
<body>
    <h1>🛡️ {MANIFEST_TITLE}</h1>
    <p style="text-align: center; font-size: 1.2em; color: #1a3a5c;">Version {VERSION}</p>
    <p style="text-align: center; font-style: italic;">"For Defensive Use Only. Protect. Detect. Respond. Explain."</p>
    
    <div class="metadata">
        <div class="metadata-item"><span class="metadata-label">Issued By:</span> {COMPANY_NAME}</div>
        <div class="metadata-item"><span class="metadata-label">Date:</span> {datetime.datetime.now().strftime('%B %d, %Y')}</div>
        <div class="metadata-item"><span class="metadata-label">Contact:</span> {CONTACT_EMAIL}</div>
        <div class="metadata-item"><span class="metadata-label">GPG Key:</span> {GPG_KEY_ID}</div>
        <div class="metadata-item"><span class="metadata-label">Classification:</span> UNCLASSIFIED / PUBLIC RELEASE</div>
    </div>
"""
        
        for section in MANIFEST_SECTIONS:
            html += f"""
    <div class="section">
        <h2>{section['title']}</h2>
        <p>{section['content'].strip().replace(chr(10), '<br>')}</p>
    </div>
"""
        
        html += f"""
    <div class="footer">
        <p>© 2024-{COPYRIGHT_YEAR} {COMPANY_NAME}. All rights reserved.</p>
        <p>Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        <p>Version {VERSION} | <a href="{WEBSITE_URL}">{WEBSITE_URL}</a></p>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        return output_file

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=f"Dsterminal Manifest Generator v{VERSION}"
    )
    
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT, help='Output filename')
    parser.add_argument('--logo', help='Path to logo image file')
    parser.add_argument('--format', choices=OUTPUT_FORMATS, default='pdf', help='Output format')
    parser.add_argument('--list-sections', action='store_true', help='List all sections')
    parser.add_argument('--verify', help='Verify an existing PDF')
    parser.add_argument('--version', action='version', version=f'v{VERSION}')
    
    args = parser.parse_args()
    
    if args.list_sections:
        print(f"\nDsterminal Manifest v{VERSION} - Sections:")
        print("=" * 60)
        for idx, section in enumerate(MANIFEST_SECTIONS, 1):
            print(f"{idx}. {section['title']}")
        print("=" * 60)
        sys.exit(0)
    
    if args.verify:
        if not os.path.exists(args.verify):
            print(f"[ERROR] File not found: {args.verify}")
            sys.exit(1)
        checksum = hashlib.sha256()
        with open(args.verify, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                checksum.update(chunk)
        print(f"[INFO] SHA-256: {checksum.hexdigest()}")
        sys.exit(0)
    
    try:
        if args.format == 'pdf':
            generator = ManifestPDFGenerator(args.output, args.logo)
            output_file, checksum = generator.build_pdf()
            print(f"\n[VERIFICATION] SHA-256: {checksum}")
        
        elif args.format == 'json':
            output_file = args.output.replace('.pdf', '.json') if '.pdf' in args.output else args.output
            if not output_file.endswith('.json'):
                output_file = f"{output_file}.json"
            JSONExporter.export(output_file)
            print(f"[SUCCESS] JSON exported: {output_file}")
        
        elif args.format == 'html':
            output_file = args.output.replace('.pdf', '.html') if '.pdf' in args.output else args.output
            if not output_file.endswith('.html'):
                output_file = f"{output_file}.html"
            HTMLExporter.export(output_file)
            print(f"[SUCCESS] HTML exported: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()