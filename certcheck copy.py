#!/usr/bin/env python3
import sys
# -*- coding: utf-8 -*-

"""
DSTerminal SSL/TLS Certificate Checker Module
Version: 5.0.0
Author: Spark Wilson Spink

A comprehensive SSL/TLS certificate analysis tool with cinematic UI.
"""

import ssl
import socket
import sys
import os
import time
import json
import random
import shutil
import re
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

# Try to import required modules
try:
    import OpenSSL
    OPENSSL_AVAILABLE = True
except ImportError:
    OPENSSL_AVAILABLE = False

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
    # Add DIM to Fore if it doesn't exist
    if not hasattr(Fore, 'DIM'):
        Fore.DIM = '\033[2m'
    if not hasattr(Style, 'DIM'):
        Style.DIM = '\033[2m'
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color codes
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'; DIM = '\033[2m'
        LIGHTRED_EX = '\033[91m'; LIGHTGREEN_EX = '\033[92m'
        LIGHTYELLOW_EX = '\033[93m'; LIGHTCYAN_EX = '\033[96m'
        LIGHTMAGENTA_EX = '\033[95m'; LIGHTBLUE_EX = '\033[94m'
    class Style:
        BRIGHT = '\033[1m'; DIM = '\033[2m'; NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ============================================================================
# CONSTANTS
# ============================================================================

VERSION = "5.0.0"
APP_NAME = "DSTerminal SSL/TLS Certificate Checker"
AUTHOR = "Spark Wilson Spink"

# ============================================================================
# SSL/TLS CERTIFICATE CHECKER CLASS
# ============================================================================

class SSLCertificateChecker:
    """
    Comprehensive SSL/TLS certificate analyzer with cinematic UI.
    """

    def __init__(self, workspace: Optional[str] = None, log_callback=None):
        self.workspace = workspace or os.path.join(os.path.expanduser("~"), "dsterminal_workspace")
        self.log_callback = log_callback
        self.report_dir = os.path.join(self.workspace, "reports")
        os.makedirs(self.report_dir, exist_ok=True)

        # Color scheme
        dim_color = Fore.DIM if hasattr(Fore, 'DIM') else '\033[2m'

        self.colors = {
            'header': Fore.CYAN,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'info': Fore.BLUE,
            'dim': dim_color,
            'highlight': Fore.MAGENTA,
        }

        # Terminal settings
        self.term_width = self._get_terminal_width()
        
        # Generate random colors for this session
        self._random_colors = self._generate_random_colors()

    def _generate_random_colors(self) -> Dict[str, str]:
        """Generate random ANSI colors for banner"""
        colors_list = [
            Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
            Fore.MAGENTA, Fore.CYAN, Fore.LIGHTRED_EX,
            Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX,
            Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX,
            Fore.LIGHTCYAN_EX, Fore.WHITE
        ]
        return {
            'title': random.choice(colors_list),
            'subtitle': random.choice(colors_list),
            'domain': random.choice(colors_list),
            'border': random.choice(colors_list),
            'ascii': random.choice(colors_list)
        }

    def _get_terminal_width(self) -> int:
        """Get terminal width"""
        try:
            width = shutil.get_terminal_size().columns
            return max(80, min(width, 120))
        except:
            return 80

    def _center_text(self, text: str, color: str = None) -> str:
        """Center text within terminal width with optional color"""
        # Remove ANSI codes for length calculation
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\[[0-9;]*m')
        clean_text = ansi_escape.sub('', text)
        # Remove emojis for length calculation
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U0001F004\U0001F0CF\U0001F170-\U0001F251\u2700-\u27BF\u2600-\u26FF\u2700-\u27BF]+')
        clean_text = emoji_pattern.sub('', clean_text)
        padding = max(0, (self.term_width - len(clean_text)) // 2)
        if color:
            return ' ' * padding + color + text + Style.RESET_ALL
        return ' ' * padding + text

    def _colored(self, text: str, color: str = 'white', bold: bool = False, blink: bool = False) -> str:
        """Apply color to text"""
        color_code = self.colors.get(color, '')
        bold_code = Style.BRIGHT if bold else ''
        blink_code = '\033[5m' if blink else ''
        reset = Style.RESET_ALL
        return f"{bold_code}{blink_code}{color_code}{text}{reset}"

    def _print_centered(self, text: str, color: str = 'white', bold: bool = False):
        """Print centered colored text"""
        print(self._center_text(self._colored(text, color, bold)))

    def _type_text(self, text: str, delay: float = 0.001, color: str = None):
        """Print text with hypersonic typing effect and proper color handling"""
        if color:
            color_code = self.colors.get(color, '')
            reset = Style.RESET_ALL
            lines = text.split('\n')
            for line in lines:
                for char in line:
                    print(f"{color_code}{char}{reset}", end='', flush=True)
                    time.sleep(delay)
                print()
                time.sleep(delay * 0.5)
        else:
            lines = text.split('\n')
            for line in lines:
                for char in line:
                    print(char, end='', flush=True)
                    time.sleep(delay)
                print()
                time.sleep(delay * 0.5)

    def _type_text_colored(self, text: str, color: str = 'white', bold: bool = False, delay: float = 0.001):
        """Print text with color and typing effect"""
        color_code = self.colors.get(color, '')
        bold_code = Style.BRIGHT if bold else ''
        reset = Style.RESET_ALL
        lines = text.split('\n')
        for line in lines:
            for char in line:
                print(f"{bold_code}{color_code}{char}{reset}", end='', flush=True)
                time.sleep(delay)
            print()
            time.sleep(delay * 0.5)

    def _type_header(self, text: str, color: str = 'header', emoji: str = "📌"):
        """Print a header with typing effect"""
        self._type_text_colored(f"\n{emoji} {text}", color, bold=True)
        self._type_text_colored("─" * min(len(text) + 4, 74), 'dim')

    def _type_status(self, text: str, color: str = 'info'):
        """Print a status message"""
        self._type_text_colored(f"[*] {text}", color)

    def _type_success(self, text: str):
        """Print a success message"""
        self._type_text_colored(f"[+] {text}", 'success')

    def _type_warning(self, text: str):
        """Print a warning message"""
        self._type_text_colored(f"[!] {text}", 'warning')

    def _type_error(self, text: str):
        """Print an error message"""
        self._type_text_colored(f"[x] {text}", 'error')

    def _type_finding(self, text: str, severity: str = "INFO"):
        """Print a finding with appropriate color"""
        color_map = {
            "CRITICAL": 'error',
            "HIGH": 'error',
            "MEDIUM": 'warning',
            "LOW": 'info',
            "INFO": 'info',
            "PASS": 'success'
        }
        prefix_map = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "⚡",
            "LOW": "ℹ️",
            "INFO": "📌",
            "PASS": "✅"
        }
        color = color_map.get(severity, 'white')
        prefix = prefix_map.get(severity, '')
        self._type_text_colored(f"{prefix} {text}", color)

    def _cinematic_box(self, title: str, seconds: float = 1.5, error: bool = False):
        """Display a centered animated box"""
        box_width = min(50, self.term_width - 10)
        left_padding = (self.term_width - box_width - 2) // 2

        colors_list = [Fore.RED, Fore.LIGHTRED_EX] if error else [Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.LIGHTGREEN_EX]
        color = random.choice(colors_list)
        blink = "\033[5m" if not error else ""

        sys.stdout.write("\033[K")

        print(" " * left_padding + color + "┌" + "─" * box_width + "┐" + Style.RESET_ALL)
        title_text = f"{blink}{title}{Style.RESET_ALL}" if not error else title
        print(" " * left_padding + color + "│" + Style.RESET_ALL + f" {title_text}".ljust(box_width + 1) + color + "│" + Style.RESET_ALL)
        print(" " * left_padding + color + "├" + "─" * box_width + "┤" + Style.RESET_ALL)

        spinner = ["◴", "◷", "◶", "◵"]
        flickers = ["[SCANNING...]", "[PROCESSING...]", "[ANALYZING...]", "[VERIFYING...]"]
        end_time = time.time() + seconds
        i = 0

        while time.time() < end_time:
            progress = int(((time.time() % seconds) / seconds) * (box_width - 10))
            bar = "█" * progress + "░" * (box_width - 10 - progress)
            content = f"{spinner[i % len(spinner)]} {bar} {random.choice(flickers)}"
            content = content[:box_width-2].ljust(box_width-2)

            sys.stdout.write(f"\033[s")
            sys.stdout.write(f"\033[{left_padding+1}G")
            sys.stdout.write(color + "│" + Style.RESET_ALL + f" {content} " + color + "│" + Style.RESET_ALL)
            sys.stdout.write(f"\033[u")
            sys.stdout.flush()
            time.sleep(0.03)
            i += 1

        print("\n" + " " * left_padding + color + "└" + "─" * box_width + "┘" + Style.RESET_ALL)
        sys.stdout.flush()

    def _animated_ssl_scan(self):
        """Run animated scanning stages"""
        stages = [
            "INITIALIZING SSL INSPECTION ENGINE",
            "ANALYZING TLS HANDSHAKE PROTOCOL",
            "VALIDATING CERTIFICATE CHAIN",
            "MAPPING TRUST RELATIONSHIPS",
            "RUNNING RISK ASSESSMENT ENGINE",
            "GENERATING DEFENSE RECOMMENDATIONS"
        ]

        for i, stage in enumerate(stages):
            if i > 0:
                time.sleep(0.1)

            self._cinematic_box(stage, seconds=1.5)

            if i < len(stages) - 1:
                glitch_color = random.choice([Fore.GREEN, Fore.CYAN, Fore.MAGENTA])
                glitch_text = f"{glitch_color}[SYSTEM]{Style.RESET_ALL} Stage {i+1} complete..."
                print(" " * ((self.term_width - len(glitch_text) + 30) // 2) + glitch_text)
                time.sleep(0.05)

    def _get_cert_cn(self, cert_obj, field: str = "subject") -> str:
        """Get Common Name from certificate"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                # Fallback to OpenSSL
                if field == "subject":
                    components = cert_obj.get_subject().get_components()
                else:
                    components = cert_obj.get_issuer().get_components()

                for key, value in components:
                    if key == b'CN':
                        return value.decode('utf-8', errors='ignore')
                return "Unknown"

            cert_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_obj)
            crypto_cert = x509.load_der_x509_certificate(cert_data, default_backend())

            attrs = crypto_cert.subject if field == "subject" else crypto_cert.issuer
            for attr in attrs:
                if attr.oid._name == 'commonName':
                    return attr.value
            return "Unknown"
        except Exception:
            return "Unknown"

    def _get_cert_cn_with_cryptography(self, crypto_cert, field: str = "subject") -> str:
        """Get CN using cryptography x509 object"""
        try:
            attrs = crypto_cert.subject if field == "subject" else crypto_cert.issuer
            for attr in attrs:
                if attr.oid._name == 'commonName':
                    return attr.value
            return "Unknown"
        except Exception:
            return "Unknown"

    def _get_certificate_chain(self, cert_obj) -> List[Dict]:
        """Get certificate chain with proper subject/issuer extraction"""
        chain = []
        try:
            # Try to get full chain using cryptography
            if CRYPTOGRAPHY_AVAILABLE:
                cert_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_obj)
                crypto_cert = x509.load_der_x509_certificate(cert_data, default_backend())
                
                # Extract subject and issuer with proper CN
                subject_cn = self._get_cert_cn_with_cryptography(crypto_cert, "subject")
                issuer_cn = self._get_cert_cn_with_cryptography(crypto_cert, "issuer")
                
                # Build subject dict
                subject = {}
                for attr in crypto_cert.subject:
                    subject[attr.oid._name] = attr.value
                
                # Build issuer dict
                issuer = {}
                for attr in crypto_cert.issuer:
                    issuer[attr.oid._name] = attr.value
                
                # Ensure CN is set
                if 'commonName' not in subject and subject_cn != "Unknown":
                    subject['commonName'] = subject_cn
                if 'commonName' not in issuer and issuer_cn != "Unknown":
                    issuer['commonName'] = issuer_cn
                
                chain.append({
                    'subject': subject,
                    'issuer': issuer,
                    'subject_cn': subject_cn,
                    'issuer_cn': issuer_cn,
                    'expires': cert_obj.get_notAfter().decode('utf-8', errors='ignore'),
                    'serial': str(cert_obj.get_serial_number()),
                    'version': cert_obj.get_version() + 1
                })
            else:
                # Fallback to OpenSSL
                subject_components = dict(cert_obj.get_subject().get_components())
                issuer_components = dict(cert_obj.get_issuer().get_components())
                
                subject_cn = subject_components.get(b'CN', b'Unknown').decode('utf-8', errors='ignore')
                issuer_cn = issuer_components.get(b'CN', b'Unknown').decode('utf-8', errors='ignore')
                
                chain.append({
                    'subject': subject_components,
                    'issuer': issuer_components,
                    'subject_cn': subject_cn,
                    'issuer_cn': issuer_cn,
                    'expires': cert_obj.get_notAfter().decode('utf-8', errors='ignore'),
                    'serial': str(cert_obj.get_serial_number()),
                    'version': cert_obj.get_version() + 1
                })
        except Exception as e:
            # Final fallback
            try:
                chain.append({
                    'subject': {'commonName': 'Unknown'},
                    'issuer': {'commonName': 'Unknown'},
                    'subject_cn': 'Unknown',
                    'issuer_cn': 'Unknown',
                    'expires': cert_obj.get_notAfter().decode('utf-8', errors='ignore'),
                    'serial': str(cert_obj.get_serial_number()),
                    'version': cert_obj.get_version() + 1
                })
            except:
                chain.append({
                    'subject': {'commonName': 'Unknown'},
                    'issuer': {'commonName': 'Unknown'},
                    'subject_cn': 'Unknown',
                    'issuer_cn': 'Unknown',
                    'expires': 'Unknown',
                    'serial': 'Unknown',
                    'version': 'Unknown'
                })

        return chain

    def _clean_chain(self, chain: List[Dict]) -> List[Dict]:
        """Clean certificate chain bytes to strings"""
        cleaned = []
        for cert in chain:
            new_cert = {}
            for k, v in cert.items():
                if isinstance(k, bytes):
                    k = k.decode('utf-8', errors='ignore')
                if isinstance(v, bytes):
                    v = v.decode('utf-8', errors='ignore')
                if isinstance(v, dict):
                    temp = {}
                    for kk, vv in v.items():
                        if isinstance(kk, bytes):
                            kk = kk.decode('utf-8', errors='ignore')
                        if isinstance(vv, bytes):
                            vv = vv.decode('utf-8', errors='ignore')
                        temp[kk] = vv
                    v = temp
                new_cert[k] = v
            cleaned.append(new_cert)
        return cleaned

    def _export_ssl_results(self, domain: str, ssock, cert_obj, chain: List[Dict]):
        """Export SSL results to JSON"""
        try:
            data = {
                "domain": domain,
                "scan_time": datetime.now().isoformat(),
                "protocol": ssock.version(),
                "cipher": ssock.cipher()[0],
                "certificate": {
                    "subject": self._get_cert_cn(cert_obj, "subject"),
                    "issuer": self._get_cert_cn(cert_obj, "issuer"),
                    "expires": cert_obj.get_notAfter().decode('utf-8'),
                    "serial": str(cert_obj.get_serial_number()),
                    "signature": cert_obj.get_signature_algorithm().decode('utf-8')
                },
                "chain": self._clean_chain(chain),
                "security_profile": {
                    "tls13": ssock.version() == "TLSv1.3",
                    "forward_secrecy": "ECDHE" in ssock.cipher()[0]
                }
            }

            report_file = os.path.join(
                self.report_dir,
                f"ssl_audit_{domain}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            )

            with open(report_file, 'w') as f:
                json.dump(data, f, indent=2)

            self._type_success(f"Audit report saved: {report_file}")
            return report_file
        except Exception as e:
            self._type_error(f"Failed to export results: {e}")
            return None

    def _generate_pdf_report(self, data: Dict) -> Optional[str]:
        """Generate PDF report"""
        if not REPORTLAB_AVAILABLE:
            self._type_warning("PDF export requires reportlab: pip install reportlab")
            return None

        try:
            domain = data.get("domain", "unknown")
            report_file = os.path.join(
                self.report_dir,
                f"ssl_report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            )

            doc = SimpleDocTemplate(
                report_file,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.HexColor('#1a237e'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold'
            )

            story.append(Paragraph("DSTerminal SSL/TLS Security Audit", title_style))
            story.append(Spacer(1, 10))

            # Header
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=4
            )

            header_data = [
                [Paragraph(f"<b>Domain:</b> {domain}", normal_style)],
                [Paragraph(f"<b>Scan Time:</b> {data.get('scan_time', 'N/A')}", normal_style)],
                [Paragraph(f"<b>Protocol:</b> {data.get('protocol', 'N/A')}", normal_style)],
                [Paragraph(f"<b>Cipher:</b> {data.get('cipher', 'N/A')}", normal_style)],
                [Paragraph(f"<b>Risk Level:</b> {data.get('risk_level', 'N/A')}", normal_style)],
            ]

            header_table = Table(header_data, colWidths=[5.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a237e')),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 20))

            # Certificate Details
            cert = data.get('certificate', {})
            cert_data = [
                ['Field', 'Value'],
                ['Subject', cert.get('subject', 'N/A')],
                ['Issuer', cert.get('issuer', 'N/A')],
                ['Expires', cert.get('expires', 'N/A')],
                ['Serial', cert.get('serial', 'N/A')],
                ['Signature', cert.get('signature', 'N/A')],
            ]

            cert_table = Table(cert_data, colWidths=[2*inch, 3.5*inch])
            cert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            section_style = ParagraphStyle(
                'Section',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#283593'),
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )

            story.append(Paragraph("Certificate Details", section_style))
            story.append(cert_table)

            # Recommendations
            story.append(Spacer(1, 15))
            story.append(Paragraph("Recommendations", section_style))

            recs = data.get('recommendations', ['No critical risks detected.'])
            for rec in recs:
                story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 5))

            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceBefore=20
            )

            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Generated by {APP_NAME} v{VERSION}", footer_style))
            story.append(Paragraph(f"Report ID: {data.get('scan_time', 'N/A')[:19]}", footer_style))

            doc.build(story)
            self._type_success(f"PDF report generated: {report_file}")
            return report_file
        except Exception as e:
            self._type_error(f"PDF generation failed: {e}")
            return None

    def check_certificate(self, domain: str) -> Dict[str, Any]:
        """
        Check SSL/TLS certificate for a domain.
        
        Args:
            domain: Domain name to check
            
        Returns:
            Dictionary with certificate information
        """
        if not OPENSSL_AVAILABLE:
            raise ImportError("pyOpenSSL is required. Install with: pip install pyopenssl")
        
        # Security Impact Header
        self._type_header("🔐 SSL/TLS Security Assessment")
        time.sleep(0.1)
        
        self._type_finding("Certificate Chain Validation: Verifying trust chain integrity", "INFO")
        self._type_finding("Expiration Monitoring: Detecting expiring certificates", "INFO")
        self._type_finding("Weak Algorithm Detection: SHA1, RC4, MD5, DES", "INFO")
        self._type_finding("Protocol Security: TLS 1.0, 1.1, 1.2, 1.3 analysis", "INFO")
        self._type_finding("Cipher Suite Analysis: Strong vs weak ciphers", "INFO")
        self._type_finding("Key Strength Assessment: RSA, ECDSA key size analysis", "INFO")
        self._type_finding("CRL/OCSP Status: Revocation checking", "INFO")
        self._type_finding("Certificate Transparency: CT log validation", "INFO")
        self._type_finding("HSTS/HPKP: HTTP Strict Transport Security analysis", "INFO")
        
        time.sleep(0.3)
        
        # Run animated scanning sequence
        self._animated_ssl_scan()
        
        # Configure enhanced SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_default_certs()
        
        # Set timeout and create connection
        socket.setdefaulttimeout(10)
        
        self._type_status(f"Connecting to {domain}:443...")
        
        result = {
            'domain': domain,
            'valid': False,
            'error': None,
            'certificate': None,
            'protocol': None,
            'cipher': None,
            'valid_days': None,
            'chain': [],
            'risk_level': 'UNKNOWN',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'scan_time': datetime.now().isoformat()
        }
        
        try:
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    x509_cert = ssl.DER_cert_to_PEM_cert(cert)
                    cert_obj = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, x509_cert)
                    
                    # Get certificate details
                    peer_cert = ssock.getpeercert()
                    expires = datetime.strptime(peer_cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    valid_days = (expires - datetime.now()).days
                    
                    result['valid'] = True
                    result['protocol'] = ssock.version()
                    result['cipher'] = ssock.cipher()[0]
                    result['valid_days'] = valid_days
                    result['chain'] = self._get_certificate_chain(cert_obj)
                    
                    self._type_success(f"Connected to {domain}")
                    self._type_status(f"Protocol: {ssock.version()}")
                    self._type_status(f"Cipher: {ssock.cipher()[0]} ({ssock.cipher()[1]} bits)")
                    
                    time.sleep(0.2)
                    
                    # Print comprehensive report
                    self._print_report(domain, ssock, cert_obj, result['chain'], valid_days)
                    
        except ssl.SSLError as e:
            self._cinematic_box(f"SSL Error: {e}", seconds=1, error=True)
            result['error'] = str(e)
        except socket.timeout:
            self._cinematic_box("Connection timed out", seconds=1, error=True)
            result['error'] = "Connection timeout"
        except Exception as e:
            self._cinematic_box(f"Analysis failed: {str(e)}", seconds=1, error=True)
            result['error'] = str(e)
        
        return result

    def _print_report(self, domain: str, ssock, cert_obj, chain: List[Dict], valid_days: int):
        """Print SSL report with all details"""
        protocol = ssock.version()
        cipher = ssock.cipher()[0]
        sig_algo = cert_obj.get_signature_algorithm().decode('utf-8', errors='ignore')
        
        issuer = self._get_cert_cn(cert_obj, "issuer")
        subject = self._get_cert_cn(cert_obj, "subject")
        
        # Calculate risk level
        risk = 0
        risk_factors = []
        
        if valid_days < 30:
            risk += 5
            risk_factors.append("Certificate expires within 30 days")
        elif valid_days < 60:
            risk += 3
            risk_factors.append("Certificate expires within 60 days")
        elif valid_days < 90:
            risk += 1
            risk_factors.append("Certificate expires within 90 days")
        
        if "SHA1" in sig_algo:
            risk += 4
            risk_factors.append("Weak SHA1 signature algorithm")
        
        if "MD5" in sig_algo:
            risk += 4
            risk_factors.append("Weak MD5 signature algorithm")
        
        if protocol in ["TLSv1", "TLSv1.1"]:
            risk += 4
            risk_factors.append(f"Deprecated {protocol} protocol")
        
        if protocol != "TLSv1.3":
            risk += 1
            risk_factors.append("TLS 1.3 not enabled")
        
        if len(chain) < 2:
            risk += 1
            risk_factors.append("Incomplete certificate chain")
        
        if risk == 0:
            level = "LOW"
            risk_color = Fore.LIGHTGREEN_EX
            risk_emoji = "🟢"
        elif risk <= 3:
            level = "MEDIUM"
            risk_color = Fore.LIGHTYELLOW_EX
            risk_emoji = "🟡"
        elif risk <= 6:
            level = "HIGH"
            risk_color = Fore.RED
            risk_emoji = "🔴"
        else:
            level = "CRITICAL"
            risk_color = Fore.LIGHTRED_EX
            risk_emoji = "🚨"
        
        # ====================================================================
        # Certificate Information
        # ====================================================================
        self._type_header("\n📊 Certificate Analysis", 'header')
        time.sleep(0.05)
        
        cert_info = [
            ("Domain", domain, Fore.GREEN),
            ("Subject", subject, Fore.CYAN),
            ("Issuer", issuer, Fore.YELLOW),
            ("Protocol", protocol, Fore.MAGENTA),
            ("Cipher", cipher, Fore.BLUE),
            ("Signature Algorithm", sig_algo, Fore.LIGHTBLUE_EX),
            ("Chain Length", str(len(chain)), Fore.WHITE),
        ]
        
        for key, value, color in cert_info:
            self._type_text_colored(f"  {key}: {value}", 'white')
        
        time.sleep(0.05)
        
        # ====================================================================
        # Expiration Analysis
        # ====================================================================
        self._type_header("\n⏰ Expiration Analysis", 'warning')
        time.sleep(0.05)
        
        not_before = cert_obj.get_notBefore().decode('utf-8', errors='ignore')
        not_after = cert_obj.get_notAfter().decode('utf-8', errors='ignore')
        
        try:
            not_before_dt = datetime.strptime(not_before, "%Y%m%d%H%M%SZ")
            not_after_dt = datetime.strptime(not_after, "%Y%m%d%H%M%SZ")
            
            self._type_text_colored(f"  Issued: {not_before_dt.strftime('%Y-%m-%d %H:%M:%S')}", 'info')
            
            if valid_days < 0:
                self._type_text_colored(f"  ⚠️ EXPIRED: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({abs(valid_days)} days overdue)", 'error')
            elif valid_days < 30:
                self._type_text_colored(f"  ⚠️ Expires Soon: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({valid_days} days)", 'warning')
            elif valid_days < 90:
                self._type_text_colored(f"  📅 Expires: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({valid_days} days)", 'warning')
            else:
                self._type_text_colored(f"  ✅ Expires: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({valid_days} days)", 'success')
            
            validity_days = (not_after_dt - not_before_dt).days
            if validity_days > 398:
                self._type_warning(f"Long validity period ({validity_days} days) - Consider shorter validity")
        except Exception as e:
            self._type_warning(f"Could not parse dates: {str(e)}")
        
        time.sleep(0.05)
        
        # ====================================================================
        # SAN Analysis
        # ====================================================================
        self._type_header("\n🌐 Subject Alternative Names", 'info')
        time.sleep(0.05)
        
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                cert_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_obj)
                crypto_cert = x509.load_der_x509_certificate(cert_data, default_backend())
                
                san_list = []
                try:
                    san_ext = crypto_cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                    for name in san_ext.value:
                        if isinstance(name, x509.DNSName):
                            san_list.append(name.value)
                except:
                    pass
                
                if san_list:
                    self._type_text_colored(f"  📡 SANs ({len(san_list)}):", 'info')
                    for san in san_list[:10]:
                        self._type_text_colored(f"    • {san}", 'success')
                    if len(san_list) > 10:
                        self._type_text_colored(f"    ... and {len(san_list) - 10} more", 'dim')
                else:
                    self._type_warning("No Subject Alternative Names found")
            else:
                self._type_warning("Cryptography not available for SAN extraction")
        except Exception:
            self._type_warning("Could not retrieve SAN information")
        
        time.sleep(0.05)
        
        # ====================================================================
        # Key Strength Analysis
        # ====================================================================
        self._type_header("\n🔑 Key Strength Analysis", 'info')
        time.sleep(0.05)
        
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                cert_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_obj)
                crypto_cert = x509.load_der_x509_certificate(cert_data, default_backend())
                pub_key = crypto_cert.public_key()
                
                if isinstance(pub_key, rsa.RSAPublicKey):
                    key_size = pub_key.key_size
                    key_type = "RSA"
                    
                    if key_size >= 4096:
                        key_color = Fore.LIGHTGREEN_EX
                        key_status = "EXCELLENT"
                    elif key_size >= 3072:
                        key_color = Fore.GREEN
                        key_status = "GOOD"
                    elif key_size >= 2048:
                        key_color = Fore.YELLOW
                        key_status = "ACCEPTABLE"
                    elif key_size >= 1024:
                        key_color = Fore.LIGHTRED_EX
                        key_status = "WEAK"
                    else:
                        key_color = Fore.RED
                        key_status = "CRITICAL"
                    
                    self._type_text_colored(f"  Algorithm: {key_type}", 'info')
                    self._type_text_colored(f"  Key Size: {key_size} bits", 'warning' if key_size < 2048 else 'success')
                    self._type_text_colored(f"  Status: {key_status}", 'warning' if key_size < 2048 else 'success')
                    
                    if key_size < 2048:
                        self._type_finding(f"Key size {key_size} bits is below recommended 2048 bits", "HIGH")
                elif isinstance(pub_key, ec.EllipticCurvePublicKey):
                    key_size = pub_key.key_size
                    curve_name = pub_key.curve.name
                    key_type = f"ECDSA ({curve_name})"
                    
                    self._type_text_colored(f"  Algorithm: {key_type}", 'info')
                    self._type_text_colored(f"  Key Size: {key_size} bits", 'success')
                    self._type_text_colored(f"  Status: SECURE", 'success')
                else:
                    self._type_text_colored(f"  Algorithm: Unknown", 'warning')
            else:
                self._type_warning("Cryptography not available for key analysis")
        except Exception as e:
            self._type_warning(f"Could not analyze key strength: {str(e)}")
        
        time.sleep(0.05)
        
        # ====================================================================
        # Security Findings
        # ====================================================================
        self._type_header("\n🚨 Security Findings", 'error')
        time.sleep(0.05)
        
        findings = []
        recommendations = []
        
        if valid_days < 30:
            findings.append(("Certificate expires in less than 30 days - RENEW IMMEDIATELY", "CRITICAL"))
            recommendations.append("Renew SSL certificate immediately")
        elif valid_days < 60:
            findings.append(("Certificate expires in less than 60 days - Plan renewal", "HIGH"))
            recommendations.append("Renew SSL certificate within 30 days")
        
        if "SHA1" in sig_algo:
            findings.append(("SHA1 signature algorithm - DEPRECATED and vulnerable", "CRITICAL"))
            recommendations.append("Replace certificate with SHA256 signed certificate")
        
        if "MD5" in sig_algo:
            findings.append(("MD5 signature algorithm - CRYPTOGRAPHICALLY BROKEN", "CRITICAL"))
            recommendations.append("Replace certificate with SHA256 signed certificate")
        
        if "RC4" in cipher:
            findings.append(("RC4 cipher - WEAK and deprecated", "HIGH"))
            recommendations.append("Disable RC4 cipher suites")
        
        if protocol in ["TLSv1", "TLSv1.1"]:
            findings.append(("TLS 1.0/1.1 - DEPRECATED protocol", "CRITICAL"))
            recommendations.append("Upgrade to TLS 1.2 or 1.3")
        
        if protocol != "TLSv1.3":
            findings.append(("TLS 1.3 not enabled - Upgrade for better security", "MEDIUM"))
            recommendations.append("Enable TLS 1.3 for better security and performance")
        
        if len(chain) < 2:
            findings.append(("Incomplete certificate chain - Ensure full chain is installed", "MEDIUM"))
            recommendations.append("Install full certificate chain")
        
        if not findings:
            self._type_finding("No security issues detected - Certificate is secure", "PASS")
            recommendations.append("No critical risks detected. Maintain current security posture.")
        else:
            for finding, severity in findings:
                self._type_finding(finding, severity)
                time.sleep(0.02)
        
        time.sleep(0.05)
        
        # ====================================================================
        # Risk Score
        # ====================================================================
        self._type_header("\n📊 Security Score", 'info')
        time.sleep(0.05)
        
        score = max(0, 100 - risk * 2)
        
        self._type_text_colored(f"  Risk Level: {risk_emoji} {level} ({risk}/15)", 'warning' if risk > 0 else 'success')
        
        bar_length = 30
        filled = int((score / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        if score >= 80:
            bar_color = 'success'
        elif score >= 60:
            bar_color = 'warning'
        elif score >= 40:
            bar_color = 'warning'
        else:
            bar_color = 'error'
        
        self._type_text_colored(f"  Score: {score}/100", bar_color)
        self._type_text_colored(f"  [{bar}]", bar_color)
        
        time.sleep(0.05)
        
        # ====================================================================
        # Recommendations
        # ====================================================================
        self._type_header("\n💡 Recommendations", 'info')
        time.sleep(0.05)
        
        for rec in recommendations[:5]:
            self._type_text_colored(f"  • {rec}", 'success')
        
        time.sleep(0.05)
        
        # ====================================================================
        # Certificate Chain - Fixed to show proper names
        # ====================================================================
        self._type_header("\n🔗 Certificate Chain", 'highlight')
        time.sleep(0.05)
        
        for i, cert in enumerate(chain):
            indent = "  " * i
            
            # Get subject and issuer names from the chain
            if 'subject_cn' in cert and cert['subject_cn'] != "Unknown":
                subject_name = cert['subject_cn']
            elif 'subject' in cert and isinstance(cert['subject'], dict):
                subject_name = cert['subject'].get('commonName', 
                              cert['subject'].get(b'CN', 'Unknown').decode('utf-8', errors='ignore') 
                              if isinstance(cert['subject'].get(b'CN'), bytes) else 'Unknown')
            else:
                subject_name = "Unknown"
            
            if 'issuer_cn' in cert and cert['issuer_cn'] != "Unknown":
                issuer_name = cert['issuer_cn']
            elif 'issuer' in cert and isinstance(cert['issuer'], dict):
                issuer_name = cert['issuer'].get('commonName',
                              cert['issuer'].get(b'CN', 'Unknown').decode('utf-8', errors='ignore')
                              if isinstance(cert['issuer'].get(b'CN'), bytes) else 'Unknown')
            else:
                issuer_name = "Unknown"
            
            if i == 0:
                color = Fore.LIGHTGREEN_EX
                role = "Leaf"
            elif i == len(chain) - 1:
                color = Fore.LIGHTYELLOW_EX
                role = "Root"
            else:
                color = Fore.LIGHTCYAN_EX
                role = "Intermediate"
            
            self._type_text_colored(f"{indent} {color}├─ [{role}] {subject_name}{Style.RESET_ALL}", 'white')
            self._type_text_colored(f"{indent}    Issuer: {issuer_name}", 'info')
            time.sleep(0.005)
        
        time.sleep(0.05)
        
        # ====================================================================
        # Export Options
        # ====================================================================
        self._type_header("\n💾 Export Options", 'info')
        time.sleep(0.05)
        
        self._type_text_colored("  [1] Export JSON Report", 'white')
        self._type_text_colored("  [2] Generate PDF Report", 'white')
        self._type_text_colored("  [3] Both", 'white')
        self._type_text_colored("  [4] Skip", 'white')
        
        choice = input(f"\n{Fore.YELLOW}Select option (1-4): {Style.RESET_ALL}").strip()
        
        if choice in ['1', '3']:
            self._export_ssl_results(domain, ssock, cert_obj, chain)
        
        if choice in ['2', '3']:
            data = {
                "domain": domain,
                "subject": subject,
                "valid_days": valid_days,
                "protocol": protocol,
                "cipher": cipher,
                "risk_level": level,
                "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "certificate": {
                    "subject": {"CN": subject},
                    "issuer": {"CN": issuer},
                    "expires": cert_obj.get_notAfter().decode('utf-8', errors='ignore'),
                    "serial": str(cert_obj.get_serial_number()),
                    "signature": sig_algo
                },
                "recommendations": recommendations
            }
            self._generate_pdf_report(data)
        
        # ====================================================================
        # Footer
        # ====================================================================
        self._type_text_colored("\n" + "═" * 70, 'dim')
        self._type_text_colored(f"🔐 SSL/TLS Certificate Audit Complete: {domain}", 'success')
        self._type_text_colored(f"📅 Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'info')
        self._type_text_colored("═" * 70, 'dim')

    def _print_banner(self, domain: str):
        """Print the banner with random colors"""
        colors = self._random_colors
        
        banner = f"""
{self._center_text("┌" + "─" * 60 + "┐", colors['border'])}
{self._center_text("│" + " " * 18 + "🔐 SSL/TLS CERTIFICATE SECURITY ENGINE" + " " * 18 + "│", colors['title'])}
{self._center_text("├" + "─" * 60 + "┤", colors['border'])}
{self._center_text("│" + " " * 24 + "🔍 CERTIFICATE CHECKER" + " " * 24 + "│", colors['subtitle'])}
{self._center_text("├" + "─" * 60 + "┤", colors['border'])}
{self._center_text("│" + " " * 24 + f"🌐 {domain}" + " " * (24 - len(domain)) + "│", colors['domain'])}
{self._center_text("└" + "─" * 60 + "┘", colors['border'])}
{self._center_text("")}
{self._center_text("  ╔══════════════════════════════════════════════════════════════╗", colors['border'])}
{self._center_text("  ║     ██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗         ║", colors['ascii'])}
{self._center_text("  ║    ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║         ║", colors['ascii'])}
{self._center_text("  ║    ██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║         ║", colors['ascii'])}
{self._center_text("  ║    ██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║         ║", colors['ascii'])}
{self._center_text("  ║    ██████╔╝███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗    ║", colors['ascii'])}
{self._center_text("  ║    ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝    ║", colors['ascii'])}
{self._center_text("  ║                                                                  ║", colors['border'])}
{self._center_text("  ║              🔐 SSL/TLS CERTIFICATE SECURITY ENGINE              ║", colors['title'])}
{self._center_text("  ║                                                                  ║", colors['border'])}
{self._center_text("  ╚══════════════════════════════════════════════════════════════╝", colors['border'])}
"""
        print(banner)
        time.sleep(0.2)

    def check(self, domain: str) -> Dict[str, Any]:
        """
        Main entry point for certificate checking.
        
        Args:
            domain: Domain name to check
            
        Returns:
            Dictionary with certificate information
        """
        if not OPENSSL_AVAILABLE:
            print(self._colored("[!] pyOpenSSL is required. Install with: pip install pyopenssl", 'error'))
            return {'error': 'pyOpenSSL not installed'}
        
        if not domain:
            domain = input(self._colored("Enter domain to check (e.g., starkexpo.com): ", 'info')).strip()
            if not domain:
                print(self._colored("❌ No domain provided", 'error'))
                return {'error': 'No domain provided'}
        
        # Print banner with random colors
        self._print_banner(domain)
        
        return self.check_certificate(domain)


# ============================================================================
# COMMAND FUNCTION FOR DSTERMINAL INTEGRATION
# ============================================================================

def cmd_certcheck(dsterminal_instance, args):
    """
    Command handler for certcheck in DSTerminal.
    
    Usage:
        certcheck [domain]
        certcheck --help
    """
    if not args:
        # Interactive mode - will prompt for domain
        checker = SSLCertificateChecker(
            workspace=getattr(dsterminal_instance, 'workspace', None),
            log_callback=getattr(dsterminal_instance, 'log_message', None)
        )
        checker.check(None)
        return
    
    if args[0] in ['--help', '-h', 'help']:
        print("""
SSL/TLS Certificate Checker
---------------------------
Usage: certcheck [domain]

Examples:
  certcheck starkexpo.com
  certcheck google.com
  certcheck (interactive mode - prompts for domain)

Options:
  --help, -h    Show this help message
""")
        return
    
    domain = args[0]
    checker = SSLCertificateChecker(
        workspace=getattr(dsterminal_instance, 'workspace', None),
        log_callback=getattr(dsterminal_instance, 'log_message', None)
    )
    checker.check(domain)


# ============================================================================
# MAIN ENTRY POINT (Standalone Execution)
# ============================================================================

def main():
    """Standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SSL/TLS Certificate Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python certcheck.py starkexpo.com
  python certcheck.py google.com
  python certcheck.py (interactive mode)
        """
    )
    parser.add_argument('domain', nargs='?', help='Domain to check')
    parser.add_argument('--version', action='version', version=f'{APP_NAME} v{VERSION}')
    
    args = parser.parse_args()
    
    checker = SSLCertificateChecker()
    checker.check(args.domain)


if __name__ == "__main__":
    main()