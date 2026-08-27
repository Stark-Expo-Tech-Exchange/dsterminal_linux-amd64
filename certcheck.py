#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DSTerminal SSL/TLS Certificate Checker Module
Version: 5.0.0
Author: Spark Wilson Spink

A comprehensive SSL/TLS certificate analysis tool with cinematic UI.
"""
import sys
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

# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass

# Define the safe stdout write function
_original_stdout_write = sys.stdout.write

def _safe_stdout_write(text):
    try:
        _original_stdout_write(text)
    except OSError as e:
        if e.errno == 22:
            try:
                clean = text.encode("ascii", "ignore").decode("ascii")
                _original_stdout_write(clean)
            except:
                pass
        else:
            raise
    except UnicodeEncodeError:
        try:
            clean = text.encode("ascii", "ignore").decode("ascii")
            _original_stdout_write(clean)
        except:
            pass

# Apply the fix
sys.stdout.write = _safe_stdout_write

# ============================================================
# FIX WINDOWS CONSOLE ENCODING - MUST BE FIRST
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass
    
    # Fix stdout encoding
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        else:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    except:
        pass

# ============================================================
# ANSI COLOR DEFINITIONS (ALWAYS AVAILABLE)
# ============================================================
class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    DIM = '\033[2m'
    BRIGHT = '\033[1m'
    LIGHTRED_EX = '\033[91m'
    LIGHTGREEN_EX = '\033[92m'
    LIGHTYELLOW_EX = '\033[93m'
    LIGHTCYAN_EX = '\033[96m'
    LIGHTMAGENTA_EX = '\033[95m'
    LIGHTBLUE_EX = '\033[94m'
    LIGHTWHITE_EX = '\033[97m'
    
    @staticmethod
    def strip(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# ============================================================
# TRY TO IMPORT COLORAMA WITH PROPER ERROR HANDLING
# ============================================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True, convert=True, strip=False)
    COLORS_AVAILABLE = True
    # Force color support
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Add DIM to Fore if it doesn't exist
    if not hasattr(Fore, 'DIM'):
        Fore.DIM = '\033[2m'
    if not hasattr(Style, 'DIM'):
        Style.DIM = '\033[2m'
except ImportError:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m',
        'NORMAL': '\033[22m'
    })
except Exception as e:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m',
        'NORMAL': '\033[22m'
    })

# ============================================================
# TRY TO IMPORT REQUIRED MODULES
# ============================================================
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

# ============================================================
# TRY TO IMPORT REPORTLAB FOR PDF GENERATION
# ============================================================
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as reportlab_colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ============================================================
# SIMPLE SAFE PRINT FUNCTION
# ============================================================
def safe_print_unicode(text):
    try:
        # Try to encode to the console's encoding
        sys.stdout.write(text)
    except UnicodeEncodeError:
        # Fallback to ASCII with replacement
        encoded_text = text.encode('ascii', 'ignore').decode('ascii')
        sys.stdout.write(encoded_text)
    except OSError as e:
        # Handle the specific OSError
        if e.errno == 22:  # Invalid argument
            # Try encoding and decoding with replacement
            try:
                clean_text = text.encode('utf-8', 'ignore').decode('utf-8')
                sys.stdout.write(clean_text)
            except:
                # Last resort: strip all non-ASCII
                clean_text = ''.join(char for char in text if ord(char) < 128)
                sys.stdout.write(clean_text)
        else:
            raise

    
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
        
        # Track terminal size for responsive updates
        self._last_terminal_width = self.term_width
        self._last_terminal_height = self._get_terminal_height()

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

    def _get_terminal_height(self) -> int:
        """Get terminal height"""
        try:
            height = shutil.get_terminal_size().lines
            return max(24, height)
        except:
            return 24

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
        """Display a centered animated box - RESPONSIVE"""
        # Recalculate terminal width for responsiveness
        self.term_width = self._get_terminal_width()
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
        """Run animated scanning stages - RESPONSIVE"""
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
                self.term_width = self._get_terminal_width()
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
        
        # ====================================================================
        # RANDOM SECURITY HEADER - One randomly selected each run
        # ====================================================================
        security_headers = [
            {
                'title': "🔐 SSL/TLS Security Assessment - Certificate Trust & Identity Verification",
                'subtitle': "Validating digital identities through cryptographic trust chains"
            },
            {
                'title': "🛡️ Certificate Chain Integrity Analysis - Trust Anchor Verification",
                'subtitle': "Mapping trust relationships from root CA to leaf certificate"
            },
            {
                'title': "🔑 Cryptographic Identity Verification - SSL/TLS Handshake Analysis",
                'subtitle': "Ensuring secure channel establishment through key exchange"
            },
            {
                'title': "📜 Digital Certificate Forensics - PKI Trust Validation",
                'subtitle': "Analyzing certificate structure, signatures and chain of trust"
            },
            {
                'title': "🛡️ TLS Security Posture Assessment - Attack Surface Analysis",
                'subtitle': "Identifying protocol weaknesses and cryptographic vulnerabilities"
            },
            {
                'title': "🔒 Public Key Infrastructure Audit - Certificate Lifecycle Analysis",
                'subtitle': "Examining issuance, expiration, and revocation mechanisms"
            },
            {
                'title': "🎯 Identity Assurance Verification - Domain Validation & Authentication",
                'subtitle': "Confirming server identity through certificate attributes and SANs"
            },
            {
                'title': "⚡ Cipher Suite & Protocol Security Analysis - TLS Configuration Audit",
                'subtitle': "Evaluating encryption strength and protocol hardening status"
            },
            {
                'title': "🔐 Digital Signature Verification - Certificate Authenticity Check",
                'subtitle': "Validating cryptographic signatures and algorithm strength"
            },
            {
                'title': "🛡️ Enterprise SSL/TLS Security Scan - Compliance & Hardening Assessment",
                'subtitle': "Verifying security controls against industry best practices"
            },
            {
                'title': "🔍 Advanced Threat Detection - Certificate Anomaly & Malware Analysis",
                'subtitle': "Detecting compromised certificates and potential MITM attacks"
            },
            {
                'title': "⚖️ Regulatory Compliance Verification - SSL/TLS Security Standards Audit",
                'subtitle': "Validating compliance with PCI-DSS, HIPAA, GDPR, and NIST standards"
            },
            {
                'title': "🔬 Cryptographic Protocol Analysis - TLS/SSL Implementation Review",
                'subtitle': "Examining protocol implementations for security flaws and weaknesses"
            },
            {
                'title': "🔄 Certificate Chain Optimization - Performance & Security Balancing",
                'subtitle': "Optimizing certificate chain length and cryptographic operations"
            },
            {
                'title': "🌐 Multi-Domain Certificate Assessment - SAN and Wildcard Validation",
                'subtitle': "Validating subject alternative names and wildcard certificate security"
            },
            {
                'title': "⏳ Historical Certificate Analysis - Security Trend & Evolution Tracking",
                'subtitle': "Analyzing certificate history and cryptographic evolution patterns"
            },
            {
                'title': "📊 Risk Scoring & Prioritization - Certificate Security Posture Assessment",
                'subtitle': "Quantifying risk levels and prioritizing remediation actions"
            },
            {
                'title': "🔧 Automated Certificate Management - Lifecycle Automation Assessment",
                'subtitle': "Evaluating automated renewal and deployment mechanisms"
            },
            {
                'title': "🛡️ Zero Trust Architecture - Certificate-Based Access Control Verification",
                'subtitle': "Validating certificate-based identity and access control mechanisms"
            },
            {
                'title': "📈 Certificate Performance Impact - SSL/TLS Overhead Analysis",
                'subtitle': "Measuring performance implications and optimization opportunities"
            },
            {
                'title': "🔐 Quantum-Safe Cryptography - Post-Quantum Certificate Readiness",
                'subtitle': "Assessing certificate readiness for quantum-resistant algorithms"
            },
            {
                'title': "🔄 Continuous Compliance Monitoring - Real-Time Certificate Health Check",
                'subtitle': "Ongoing monitoring and alerting for certificate security status"
            },
            {
                'title': "📋 Certificate Inventory Management - Asset Discovery & Tracking",
                'subtitle': "Identifying and cataloging all certificates in the environment"
            },
            {
                'title': "🔒 Hardware Security Module Integration - HSM Certificate Security",
                'subtitle': "Validating HSM-based key storage and cryptographic operations"
            },
            {
                'title': "🌍 International Security Standards - Global Certificate Compliance Check",
                'subtitle': "Ensuring compliance with international cryptographic standards"
            },
            {
                'title': "🔄 Certificate Replacement Planning - Migration & Transition Strategies",
                'subtitle': "Planning and executing certificate replacements and upgrades"
            },
            {
                'title': "📊 Security Metrics & KPIs - Certificate Security Performance Dashboard",
                'subtitle': "Measuring and tracking certificate security key performance indicators"
            },
            {
                'title': "🔐 Mutual TLS Authentication - Two-Way Certificate Verification",
                'subtitle': "Validating bidirectional client-server certificate authentication"
            },
            {
                'title': "🛡️ Incident Response Readiness - Certificate Compromise Recovery Planning",
                'subtitle': "Preparing for and responding to certificate security incidents"
            },
            {
                'title': "📈 Certificate Expiry Forecasting - Predictive Analytics for Certificate Lifecycle",
                'subtitle': "Using predictive analytics to forecast and prevent certificate expirations"
            },
            {
                'title': "🔗 Certificate Dependency Mapping - Application & Service Dependency Analysis",
                'subtitle': "Mapping certificate dependencies across applications and services"
            },
            {
                'title': "⚡ Automated Vulnerability Remediation - Certificate Security Auto-Healing",
                'subtitle': "Implementing automated remediation for certificate vulnerabilities"
            }
        ]
        
        # Select a random header for this run
        import random
        selected_header = random.choice(security_headers)
        
        # Display the selected header with typing effect
        self._type_header(selected_header['title'], 'header')
        time.sleep(0.05)
        self._type_text_colored(f"  {selected_header['subtitle']}", 'dim')
        time.sleep(0.05)
        
        # ====================================================================
        # SECURITY IMPACT HEADERS - One Randomly Selected from Pool
        # ====================================================================
        impact_headers_pool = [
            # Certificate Chain & Trust
            {
                'title': 'Certificate Chain & Trust Validation',
                'lines': [
                    "Certificate Chain Validation: Verifying trust chain integrity from root CA to leaf",
                    "Root CA Trust Verification: Establishing certificate authority trust anchor and authenticity",
                    "Intermediate Certificate Validation: Chain of trust verification and path building validation",
                    "Certificate Path Construction: Building and validating complete trust chain hierarchy",
                    "Cross-Certificate Validation: Verifying cross-signing and bridge CA relationships"
                ]
            },
            
            # Certificate Revocation
            {
                'title': 'Certificate Revocation & Status Checking',
                'lines': [
                    "Certificate Revocation Status: Checking CRL and OCSP for real-time certificate validity",
                    "CRL/OCSP Status: Real-time certificate revocation and validity checking mechanisms",
                    "Certificate Revocation List: CRL validation, freshness, completeness and distribution",
                    "OCSP Stapling: Online Certificate Status Protocol verification and caching optimization",
                    "Revocation Status: Real-time certificate validity and revocation monitoring and alerting",
                    "OCSP Must-Staple: Enforcement of OCSP stapling requirements and compliance"
                ]
            },
            
            # Expiration & Lifecycle
            {
                'title': 'Certificate Expiration & Lifecycle Management',
                'lines': [
                    "Expiration Monitoring: Detecting expiring certificates before they expire with proactive alerts",
                    "Certificate Validity Period Analysis: Time-based certificate lifespan verification and tracking",
                    "Grace Period Detection: Identifying certificate renewal window and expiration risk assessment",
                    "Certificate Lifecycle Management: End-to-end expiration risk assessment and monitoring",
                    "Certificate Issue Date: Certificate creation and freshness verification and validation",
                    "Certificate Not Before Date: Validity start date verification and time synchronization",
                    "Certificate Not After Date: Validity end date and expiration verification and forecasting"
                ]
            },
            
            # Cryptographic Algorithms
            {
                'title': 'Cryptographic Algorithm & Cipher Analysis',
                'lines': [
                    "Weak Algorithm Detection: SHA1, RC4, MD5, DES and deprecated cipher identification",
                    "Strong Algorithm Verification: Modern cryptographic standards and algorithm strength validation",
                    "Cipher Suite Analysis: Evaluating strong vs weak cipher configurations and preferences",
                    "Cryptographic Strength Assessment: Algorithm security grading, hardening and recommendations",
                    "RC4 Cipher Vulnerability: Weak stream cipher detection, mitigation and removal",
                    "FREAK Vulnerability: Export-grade cipher suite and man-in-the-middle risk assessment"
                ]
            },
            
            # Protocol Security
            {
                'title': 'Protocol Security & TLS Compliance',
                'lines': [
                    "Protocol Security Analysis: TLS 1.0, 1.1, 1.2, 1.3 version evaluation and security posture",
                    "TLS Protocol Compliance: Security protocol version verification and enforcement policies",
                    "SSL/TLS Vulnerability Assessment: Known protocol weaknesses and attack vector identification",
                    "Protocol Downgrade Detection: TLS version fallback vulnerability identification and prevention",
                    "BEAST Attack Vulnerability: TLS 1.0 CBC cipher block chaining vulnerability assessment",
                    "POODLE Vulnerability: SSLv3/TLS protocol weakness and mitigation assessment and patching",
                    "TLS Renegotiation Attack: Secure renegotiation extension verification and vulnerability check"
                ]
            },
            
            # Key Management
            {
                'title': 'Key Management & PKI Security',
                'lines': [
                    "Key Strength Assessment: RSA, ECDSA key size analysis and cryptographic strength verification",
                    "Private Key Security: Key storage, generation and management verification and best practices",
                    "Public Key Infrastructure: Key pair validation and certificate authority trust establishment",
                    "Key Exchange Security: Diffie-Hellman and ECDHE parameter strength analysis and configuration",
                    "Logjam Vulnerability: Diffie-Hellman export-grade cipher vulnerability analysis and mitigation",
                    "DROWN Vulnerability: Cross-protocol vulnerability and legacy protocol detection and remediation",
                    "Heartbleed Detection: OpenSSL vulnerability verification, patching and exposure assessment"
                ]
            },
            
            # Certificate Transparency
            {
                'title': 'Certificate Transparency & Public Auditability',
                'lines': [
                    "Certificate Transparency: CT log validation and public auditability verification",
                    "CT Log Verification: Signed Certificate Timestamp validation, integrity and freshness",
                    "Certificate Transparency Logs: Public log inclusion, verification and monitoring",
                    "CT Compliance: Browser CT policy compliance and enforcement checking for all major browsers",
                    "CT Log Submission: Verification of certificate submission to multiple CT logs",
                    "SCT Verification: Signed Certificate Timestamp validation and proof of inclusion"
                ]
            },
            
            # Security Headers & Policies
            {
                'title': 'Security Headers & Policy Enforcement',
                'lines': [
                    "HSTS/HPKP Analysis: HTTP Strict Transport Security and certificate pinning evaluation",
                    "Security Policy Enforcement: HSTS implementation and header verification and configuration",
                    "Certificate Pinning: HPKP and public key pinning policy evaluation and implementation",
                    "Security Headers Analysis: HTTP security header configuration validation and recommendations",
                    "CAA Record Validation: DNS Certification Authority Authorization checking and enforcement",
                    "CA Authorization: Certificate Authority Authorization record verification and compliance",
                    "Security Best Practice: Industry standard compliance and hardening verification and guidance"
                ]
            },
            
            # Certificate Validation Types
            {
                'title': 'Certificate Validation & Verification',
                'lines': [
                    "Extended Validation: EV certificate validation and verification checks for high assurance",
                    "Domain Validation: DV certificate verification and domain control validation checks",
                    "Organization Validation: OV certificate verification and business entity validation",
                    "Certificate Purpose: Key usage, extended key usage and purpose analysis and verification",
                    "Certificate Subject Analysis: DN and organizational attribute verification and validation",
                    "Subject Alternative Name: SAN validation and multi-domain verification and coverage",
                    "Wildcard Certificate Security: DNS wildcard certificate risk assessment and management",
                    "Self-Signed Certificate Detection: Untrusted certificate identification and risk assessment",
                    "Expired Certificate Detection: Past validity period certificate identification and handling"
                ]
            },
            
            # Vulnerability Assessment
            {
                'title': 'Vulnerability Assessment & Exploit Detection',
                'lines': [
                    "Vulnerability Assessment: Certificate misconfiguration and weakness detection and analysis",
                    "CRIME Attack Detection: Compression-based information leakage vulnerability assessment",
                    "BREACH Attack Detection: HTTP compression information leakage vulnerability and mitigation",
                    "Secure Renegotiation: TLS renegotiation vulnerability assessment and secure implementation",
                    "Certificate Hostname Mismatch: Domain name verification and matching validation",
                    "Certificate Fingerprint Analysis: SHA-1, SHA-256 fingerprint verification and comparison",
                    "Certificate Serial Number: Unique identifier and tracking verification and management"
                ]
            },
            
            # Compliance & Standards
            {
                'title': 'Compliance & Standards Verification',
                'lines': [
                    "Compliance Validation: PCI-DSS, HIPAA, GDPR, and regulatory certificate compliance checking",
                    "International Standards Compliance: Global cryptographic compliance and standards verification",
                    "Certificate Automation: Automated renewal, deployment verification and CI/CD integration",
                    "Certificate Monitoring: Continuous monitoring and alerting configuration and management",
                    "Certificate Inventory: Complete certificate asset discovery, tracking and management",
                    "Continuous Compliance Monitoring: Real-time certificate health monitoring and alerting",
                    "Security Metrics Dashboard: Certificate performance KPI tracking and reporting"
                ]
            },
            
            # Advanced Security
            {
                'title': 'Advanced Security & Modern Architecture',
                'lines': [
                    "Zero Trust Architecture: Certificate-based access control and identity verification",
                    "Mutual TLS Authentication: Client-server two-way certificate verification and validation",
                    "Quantum-Safe Readiness: Post-quantum cryptography certificate readiness and migration planning",
                    "Performance Impact Analysis: SSL/TLS overhead, optimization assessment and performance tuning",
                    "Certificate Dependency Mapping: Application and service dependency analysis and impact assessment",
                    "Incident Response Readiness: Certificate compromise recovery planning and incident handling",
                    "Certificate Replacement Planning: Migration and transition strategy assessment and execution"
                ]
            },
            
            # Additional Security Headers
            {
                'title': 'Additional Security Assessments',
                'lines': [
                    "Certificate Version Analysis: X.509 version compatibility and feature assessment",
                    "Certificate Transparency Monitoring: Continuous CT log monitoring and anomaly detection",
                    "TLS Session Resumption: Session ticket and session ID security analysis and management",
                    "Perfect Forward Secrecy: PFS cipher suite availability and enforcement verification",
                    "Certificate Subject Alternative Name: SAN coverage and completeness validation",
                    "Certificate Organization Validation: OV certificate business validation and verification",
                    "Certificate Domain Control Validation: DCV method security and implementation review",
                    "Certificate Extended Validation: EV certificate enhanced validation and verification checks",
                    "Secure Sockets Layer: SSL protocol security assessment and deprecation verification",
                    "Transport Layer Security: TLS protocol security assessment and modern implementation review"
                ]
            }
        ]

        # Randomly select ONE impact header block
        import random
        selected_impact = random.choice(impact_headers_pool)

        # Display the selected block header
        self._type_finding(f"📋 {selected_impact['title']}", "INFO")
        time.sleep(0.02)

        # Display all lines in the selected block
        for line in selected_impact['lines']:
            self._type_finding(f"  ├─ {line}", "INFO")
            time.sleep(0.015)  # Slight delay between lines

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
            'scan_time': datetime.now().isoformat(),
            'security_header': selected_header['title'],
            'impact_header_title': selected_impact['title'],  # Store the impact block title
            'impact_header_lines': selected_impact['lines']   # Store all impact lines
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
        """Print SSL report with all details - CENTERED & RESPONSIVE with glitch boxes"""
        # Recalculate terminal width for responsiveness
        self.term_width = self._get_terminal_width()
        
        protocol = ssock.version()
        cipher = ssock.cipher()[0]
        sig_algo = cert_obj.get_signature_algorithm().decode('utf-8', errors='ignore')
        
        issuer = self._get_cert_cn(cert_obj, "issuer")
        subject = self._get_cert_cn(cert_obj, "subject")
        
        # ====================================================================
        # RANDOM SECURITY HEADERS FOR REPORT
        # ====================================================================
        report_headers = [
            {
                'title': "📊 Certificate Security Analysis Report",
                'subtitle': "Comprehensive SSL/TLS certificate assessment and risk analysis"
            },
            {
                'title': "📋 PKI Trust Assessment Results",
                'subtitle': "Detailed certificate chain validation and trust path analysis"
            },
            {
                'title': "🔍 SSL/TLS Configuration Audit Report",
                'subtitle': "Protocol, cipher, and cryptographic strength evaluation"
            },
            {
                'title': "🛡️ Security Posture Assessment Results",
                'subtitle': "Vulnerability identification and remediation recommendations"
            },
            {
                'title': "📊 Certificate Lifecycle Analysis Report",
                'subtitle': "Expiration tracking, renewal planning, and risk assessment"
            },
            {
                'title': "🔐 Identity Verification & Authentication Results",
                'subtitle': "Domain validation, SAN verification, and trust establishment"
            },
            {
                'title': "📜 Cryptographic Signature & Algorithm Analysis",
                'subtitle': "Strength assessment of signatures, hashes, and key exchange"
            },
            {
                'title': "⚡ Protocol & Cipher Suite Security Review",
                'subtitle': "TLS protocol hardening and cipher configuration analysis"
            },
            {
                'title': "🎯 Attack Surface & Vulnerability Assessment",
                'subtitle': "Identifying security weaknesses and compliance gaps"
            },
            {
                'title': "🔒 Enterprise SSL/TLS Security Scorecard",
                'subtitle': "Comprehensive security posture and hardening recommendations"
            }
        ]
        
        selected_header = random.choice(report_headers)
        
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
        # GLITCH BOX HELPER - Creates blinking colored boxes
        # ====================================================================
        def glitch_box(title, content, color=Fore.CYAN, blink=False):
            """Create a glitch-style box with blinking effect"""
            width = min(70, self.term_width - 8)
            blink_code = '\033[5m' if blink else ''
            reset = Style.RESET_ALL
            border_color = color
            
            box_lines = []
            box_lines.append(f"{border_color}┌{'─' * (width - 2)}┐{reset}")
            if title:
                title_text = f" {title} "
                padding = (width - 2 - len(title_text)) // 2
                box_lines.append(f"{border_color}│{reset}{' ' * padding}{blink_code}{color}{title_text}{reset}{' ' * (width - 2 - len(title_text) - padding)}{border_color}│{reset}")
                box_lines.append(f"{border_color}├{'─' * (width - 2)}┤{reset}")
            
            content_lines = content.split('\n')
            for line in content_lines:
                if len(line) > width - 4:
                    line = line[:width-7] + '...'
                padding = (width - 2 - len(line)) // 2
                box_lines.append(f"{border_color}│{reset}{' ' * padding}{line}{' ' * (width - 2 - len(line) - padding)}{border_color}│{reset}")
            
            box_lines.append(f"{border_color}└{'─' * (width - 2)}┘{reset}")
            return '\n'.join(box_lines)
        
        # ====================================================================
        # DISPLAY EACH SECTION IN A GLITCH BOX
        # ====================================================================
        
        # Header Box
        header_text = f"{selected_header['title']}\n{selected_header['subtitle']}"
        print(glitch_box("📋 SECURITY REPORT", header_text, Fore.CYAN, True))
        time.sleep(0.1)
        
        # Certificate Info Box
        cert_text = ""
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
            cert_text += f"{color}{key}:{Style.RESET_ALL} {color}{value}{Style.RESET_ALL}\n"
        print(glitch_box("📊 Certificate Analysis", cert_text.rstrip(), Fore.LIGHTBLUE_EX, False))
        time.sleep(0.05)
        
        # Expiration Analysis Box
        not_before = cert_obj.get_notBefore().decode('utf-8', errors='ignore')
        not_after = cert_obj.get_notAfter().decode('utf-8', errors='ignore')
        exp_text = ""
        not_before_dt = None
        not_after_dt = None
        try:
            not_before_dt = datetime.strptime(not_before, "%Y%m%d%H%M%SZ")
            not_after_dt = datetime.strptime(not_after, "%Y%m%d%H%M%SZ")
            exp_text += f"  Issued: {not_before_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if valid_days < 0:
                exp_text += f"{Fore.RED}  ⚠️ EXPIRED: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({abs(valid_days)} days overdue){Style.RESET_ALL}\n"
            elif valid_days < 30:
                exp_text += f"{Fore.LIGHTYELLOW_EX}  ⚠️ Expires Soon: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({valid_days} days){Style.RESET_ALL}\n"
            elif valid_days < 90:
                exp_text += f"{Fore.YELLOW}  📅 Expires: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({valid_days} days){Style.RESET_ALL}\n"
            else:
                exp_text += f"{Fore.GREEN}  ✅ Expires: {not_after_dt.strftime('%Y-%m-%d %H:%M:%S')} ({valid_days} days){Style.RESET_ALL}\n"
            
            validity_days = (not_after_dt - not_before_dt).days
            if validity_days > 398:
                exp_text += f"{Fore.YELLOW}  ⚠️ Long validity period ({validity_days} days){Style.RESET_ALL}\n"
        except Exception as e:
            exp_text += f"  Could not parse dates: {str(e)}\n"
        
        print(glitch_box("⏰ Expiration Analysis", exp_text.rstrip(), Fore.LIGHTYELLOW_EX, False))
        time.sleep(0.05)
        
        # SAN Analysis Box
        san_text = ""
        san_list = []
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                cert_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_obj)
                crypto_cert = x509.load_der_x509_certificate(cert_data, default_backend())
                try:
                    san_ext = crypto_cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                    for name in san_ext.value:
                        if isinstance(name, x509.DNSName):
                            san_list.append(name.value)
                except:
                    pass
                
                if san_list:
                    san_text += f"  📡 SANs ({len(san_list)}):\n"
                    for san in san_list[:10]:
                        san_text += f"    • {san}\n"
                    if len(san_list) > 10:
                        san_text += f"    ... and {len(san_list) - 10} more\n"
                else:
                    san_text += "  No Subject Alternative Names found\n"
            else:
                san_text += "  Cryptography not available for SAN extraction\n"
        except Exception:
            san_text += "  Could not retrieve SAN information\n"
        
        print(glitch_box("🌐 Subject Alternative Names", san_text.rstrip(), Fore.LIGHTBLUE_EX, False))
        time.sleep(0.05)
        
        # Key Strength Analysis Box
        key_text = ""
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                cert_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_obj)
                crypto_cert = x509.load_der_x509_certificate(cert_data, default_backend())
                pub_key = crypto_cert.public_key()
                
                if isinstance(pub_key, rsa.RSAPublicKey):
                    key_size = pub_key.key_size
                    key_type = "RSA"
                    
                    if key_size >= 4096:
                        key_status = "EXCELLENT"
                        key_color = Fore.LIGHTGREEN_EX
                    elif key_size >= 3072:
                        key_status = "GOOD"
                        key_color = Fore.GREEN
                    elif key_size >= 2048:
                        key_status = "ACCEPTABLE"
                        key_color = Fore.YELLOW
                    elif key_size >= 1024:
                        key_status = "WEAK"
                        key_color = Fore.LIGHTRED_EX
                    else:
                        key_status = "CRITICAL"
                        key_color = Fore.RED
                    
                    key_text += f"  Algorithm: {key_type}\n"
                    key_text += f"  Key Size: {key_size} bits\n"
                    key_text += f"  Status: {key_status}\n"
                elif isinstance(pub_key, ec.EllipticCurvePublicKey):
                    key_size = pub_key.key_size
                    curve_name = pub_key.curve.name
                    key_text += f"  Algorithm: ECDSA ({curve_name})\n"
                    key_text += f"  Key Size: {key_size} bits\n"
                    key_text += f"  Status: SECURE\n"
                else:
                    key_text += "  Algorithm: Unknown\n"
            else:
                key_text += "  Cryptography not available for key analysis\n"
        except Exception as e:
            key_text += f"  Could not analyze key strength: {str(e)}\n"
        
        print(glitch_box("🔑 Key Strength Analysis", key_text.rstrip(), Fore.LIGHTMAGENTA_EX, False))
        time.sleep(0.05)
        
        # Security Findings Box
        findings_text = ""
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
            findings_text += "  ✅ No security issues detected - Certificate is secure\n"
            recommendations.append("No critical risks detected. Maintain current security posture.")
        else:
            for finding, severity in findings:
                if severity == "CRITICAL":
                    findings_text += f"{Fore.RED}  🚨 {finding}{Style.RESET_ALL}\n"
                elif severity == "HIGH":
                    findings_text += f"{Fore.LIGHTRED_EX}  ⚠️ {finding}{Style.RESET_ALL}\n"
                else:
                    findings_text += f"{Fore.YELLOW}  ⚡ {finding}{Style.RESET_ALL}\n"
        
        print(glitch_box("🚨 Security Findings", findings_text.rstrip(), Fore.RED, True))
        time.sleep(0.05)
        
        # Risk Score Box
        score = max(0, 100 - risk * 2)
        bar_length = min(30, self.term_width - 30)
        filled = int((score / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        if score >= 80:
            bar_color = Fore.LIGHTGREEN_EX
        elif score >= 60:
            bar_color = Fore.LIGHTYELLOW_EX
        elif score >= 40:
            bar_color = Fore.YELLOW
        else:
            bar_color = Fore.LIGHTRED_EX
        
        risk_text = f"  Risk Level: {risk_emoji} {level} ({risk}/15)\n"
        risk_text += f"  Score: {score}/100\n"
        risk_text += f"  {bar_color}[{bar}]{Style.RESET_ALL}"
        
        print(glitch_box("📊 Security Score", risk_text, Fore.CYAN, False))
        time.sleep(0.05)
        
        # Recommendations Box
        rec_text = ""
        for rec in recommendations[:5]:
            rec_text += f"  • {rec}\n"
        
        print(glitch_box("💡 Recommendations", rec_text.rstrip(), Fore.LIGHTBLUE_EX, False))
        time.sleep(0.05)
        
        # Certificate Chain Box
        chain_text = ""
        for i, cert in enumerate(chain):
            indent = "  " * i
            
            if 'subject_cn' in cert and cert['subject_cn'] != "Unknown":
                subject_name = cert['subject_cn']
            elif 'subject' in cert and isinstance(cert['subject'], dict):
                subject_name = cert['subject'].get('commonName', 'Unknown')
            else:
                subject_name = "Unknown"
            
            if 'issuer_cn' in cert and cert['issuer_cn'] != "Unknown":
                issuer_name = cert['issuer_cn']
            elif 'issuer' in cert and isinstance(cert['issuer'], dict):
                issuer_name = cert['issuer'].get('commonName', 'Unknown')
            else:
                issuer_name = "Unknown"
            
            if i == 0:
                role = "Leaf"
                color = Fore.LIGHTGREEN_EX
            elif i == len(chain) - 1:
                role = "Root"
                color = Fore.LIGHTYELLOW_EX
            else:
                role = "Intermediate"
                color = Fore.LIGHTCYAN_EX
            
            chain_text += f"{indent} {color}├─ [{role}] {subject_name}{Style.RESET_ALL}\n"
            chain_text += f"{indent}    Issuer: {issuer_name}\n"
        
        print(glitch_box("🔗 Certificate Chain", chain_text.rstrip(), Fore.MAGENTA, False))
        time.sleep(0.05)
        
        # ====================================================================
        # EXPORT OPTIONS - Updated with HTML and Both options
        # ====================================================================
        export_text = "  [1] Export JSON Report\n  [2] Generate PDF Report\n  [3] Generate HTML Report\n  [4] Both (PDF + HTML)\n  [5] Skip"
        print(glitch_box("💾 Export Options", export_text, Fore.LIGHTGREEN_EX, True))
        time.sleep(0.05)
        
        choice = input(f"\n{Fore.YELLOW}Select option (1-5): {Style.RESET_ALL}").strip()
        
        # Prepare data for reports
        data = {
            "domain": domain,
            "subject": subject,
            "issuer": issuer,
            "valid_days": valid_days,
            "protocol": protocol,
            "cipher": cipher,
            "signature": sig_algo,
            "risk_level": level,
            "risk_score": risk,
            "risk_emoji": risk_emoji,
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "certificate": {
                "subject": {"CN": subject},
                "issuer": {"CN": issuer},
                "expires": cert_obj.get_notAfter().decode('utf-8', errors='ignore'),
                "serial": str(cert_obj.get_serial_number()),
                "signature": sig_algo
            },
            "findings": findings,
            "recommendations": recommendations,
            "chain": chain,
            "san_list": san_list,
            "security_header": selected_header['title'],
            "issued": not_before_dt.strftime('%Y-%m-%d %H:%M:%S') if not_before_dt else 'N/A',
            "expires": not_after_dt.strftime('%Y-%m-%d %H:%M:%S') if not_after_dt else 'N/A'
        }
        
        if choice in ['1', '4']:
            self._export_ssl_results(domain, ssock, cert_obj, chain)
        
        if choice in ['2', '4']:
            self._generate_pdf_report_dashboard(data)
        
        if choice in ['3', '4']:
            self._generate_html_report(data)
        
        # ====================================================================
        # Footer
        # ====================================================================
        print("\n" + "═" * min(70, self.term_width))
        print(f"{Fore.GREEN}🔐 SSL/TLS Certificate Audit Complete: {domain}{Style.RESET_ALL}".center(min(70, self.term_width)))
        print(f"{Fore.CYAN}📅 Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}".center(min(70, self.term_width)))
        print("═" * min(70, self.term_width))

    def _generate_pdf_report_dashboard(self, data: Dict) -> Optional[str]:
        """Generate interactive dashboard-style PDF report with DSTerminal watermark and dark blue background"""
        if not REPORTLAB_AVAILABLE:
            self._type_warning("PDF export requires reportlab: pip install reportlab")
            return None

        try:
            domain = data.get("domain", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                self.report_dir,
                f"ssl_dashboard_{domain}_{timestamp}.pdf"
            )

            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
                PageBreak, Image, KeepTogether
            )
            from reportlab.lib.utils import ImageReader
            import io

            # ============================================================
            # DSTERMINAL CERTIFICATE AUTHENTICATION WATERMARK
            # ============================================================
            class WatermarkedDocTemplate(SimpleDocTemplate):
                def __init__(self, filename, **kw):
                    SimpleDocTemplate.__init__(self, filename, **kw)
                
                def handle_pageBegin(self):
                    """Add watermark and dark blue background on each page"""
                    self.canv.saveState()
                    
                    # ============================================================
                    # DARK BLUE BACKGROUND
                    # ============================================================
                    page_width = self.pagesize[0]
                    page_height = self.pagesize[1]
                    
                    # Draw dark blue background
                    self.canv.setFillColorRGB(0.05, 0.05, 0.15)  # Dark blue (#0d1b2a)
                    self.canv.rect(0, 0, page_width, page_height, stroke=0, fill=1)
                    
                    # ============================================================
                    # CERTIFICATE AUTHENTICATION WATERMARK
                    # ============================================================
                    center_x = page_width / 2
                    center_y = page_height / 2
                    radius = min(page_width, page_height) * 0.35
                    
                    # Draw circular stamp
                    self.canv.setStrokeColorRGB(0.0, 0.8, 0.2, 0.12)
                    self.canv.setLineWidth(1)
                    p = self.canv.beginPath()
                    p.circle(center_x, center_y, radius)
                    self.canv.drawPath(p, stroke=1, fill=0)
                    
                    # Inner circle
                    p = self.canv.beginPath()
                    p.circle(center_x, center_y, radius * 0.85)
                    self.canv.drawPath(p, stroke=1, fill=0)
                    
                    # Star pattern
                    self.canv.setFillColorRGB(0.0, 0.8, 0.2, 0.06)
                    for i in range(8):
                        angle = i * 45
                        x = center_x + radius * 0.7 * (0.5 + 0.5 * (i % 2 == 0))
                        y = center_y + radius * 0.7 * (0.5 + 0.5 * (i % 2 == 0))
                        p = self.canv.beginPath()
                        p.circle(x, y, 2)
                        self.canv.drawPath(p, stroke=0, fill=1)
                    
                    # Watermark text
                    self.canv.setFillColorRGB(0.0, 0.8, 0.2, 0.08)
                    self.canv.setFont('Helvetica-Bold', 20)
                    
                    self.canv.translate(center_x, center_y)
                    self.canv.rotate(-30)
                    self.canv.drawCentredString(0, 0, "DSTerminal")
                    self.canv.setFont('Helvetica', 12)
                    self.canv.rotate(30)
                    self.canv.drawCentredString(0, -18, "Certificate")
                    self.canv.drawCentredString(0, -32, "Authentication")
                    
                    self.canv.restoreState()
                    
                    SimpleDocTemplate.handle_pageBegin(self)

            # Create document
            doc = WatermarkedDocTemplate(
                report_file,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50,
                title="DSTerminal SSL/TLS Security Report Findings",
                author="DSTerminal Security Suite"
            )

            styles = getSampleStyleSheet()

            # ============================================================
            # DASHBOARD STYLES - HIGH VISIBILITY ON DARK BLUE
            # ============================================================
            
            header_style = ParagraphStyle(
                'DashboardHeader',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#00ff41'),  # Bright green
                alignment=TA_CENTER,
                spaceAfter=15,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'DashboardSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#00ccff'),  # Bright cyan
                alignment=TA_CENTER,
                spaceAfter=25,
                fontName='Helvetica'
            )
            
            section_title_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading3'],
                fontSize=16,
                textColor=colors.HexColor('#00ff41'),  # Bright green
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            
            card_title_style = ParagraphStyle(
                'CardTitle',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.HexColor('#00d4ff'),  # Bright cyan
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )
            
            card_value_style = ParagraphStyle(
                'CardValue',
                parent=styles['Normal'],
                fontSize=15,
                textColor=colors.HexColor('#ffffff'),  # White
                spaceAfter=3,
                fontName='Helvetica-Bold'
            )
            
            card_label_style = ParagraphStyle(
                'CardLabel',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#8899bb'),  # Light blue-grey
                spaceAfter=2,
                fontName='Helvetica'
            )
            
            # Finding styles with high visibility on dark blue
            finding_critical = ParagraphStyle(
                'FindingCritical',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#ff4444'),  # Bright red
                spaceAfter=4,
                fontName='Helvetica-Bold',
                leftIndent=10,
                backColor=colors.HexColor('#2a0000')  # Dark red background
            )
            
            finding_high = ParagraphStyle(
                'FindingHigh',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#ff8800'),  # Bright orange
                spaceAfter=4,
                fontName='Helvetica-Bold',
                leftIndent=10,
                backColor=colors.HexColor('#2a0a00')  # Dark orange background
            )
            
            finding_medium = ParagraphStyle(
                'FindingMedium',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#ffcc00'),  # Bright yellow
                spaceAfter=4,
                fontName='Helvetica-Bold',
                leftIndent=10,
                backColor=colors.HexColor('#2a2a00')  # Dark yellow background
            )
            
            finding_low = ParagraphStyle(
                'FindingLow',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#00ccff'),  # Bright cyan
                spaceAfter=4,
                fontName='Helvetica',
                leftIndent=10
            )
            
            finding_pass = ParagraphStyle(
                'FindingPass',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#00ff41'),  # Bright green
                spaceAfter=4,
                fontName='Helvetica-Bold',
                leftIndent=10
            )
            
            # Normal text - HIGH VISIBILITY on dark blue
            normal_style = ParagraphStyle(
                'DashboardNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#e0e8f0'),  # Light blue-white
                spaceAfter=4,
                fontName='Helvetica'
            )
            
            # Bold normal text
            bold_normal = ParagraphStyle(
                'BoldNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#ffffff'),  # White
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )
            
            # Highlight text
            highlight_style = ParagraphStyle(
                'Highlight',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#00ff41'),  # Bright green
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )
            
            # Recommendation text with action steps
            rec_style = ParagraphStyle(
                'Recommendation',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#ffffff'),  # White
                spaceAfter=6,
                fontName='Helvetica',
                leftIndent=15
            )
            
            rec_action_style = ParagraphStyle(
                'RecAction',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#00ccff'),  # Bright cyan
                spaceAfter=4,
                fontName='Helvetica',
                leftIndent=30
            )
            
            # Info box style
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#88ddff'),  # Light blue
                spaceAfter=4,
                fontName='Helvetica',
                leftIndent=15
            )

            story = []

            # ============================================================
            # DASHBOARD HEADER
            # ============================================================
            
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("🛡️ SSL/TLS SECURITY Report Findings", header_style))
            story.append(Paragraph(f"Domain: {domain} | Generated: {data.get('scan_time', 'N/A')}", subtitle_style))
            story.append(Spacer(1, 0.1*inch))
            
            separator = "═" * 80
            story.append(Paragraph(f"<font color='#00ff41'>{separator}</font>", normal_style))
            story.append(Spacer(1, 0.1*inch))

            # ============================================================
            # STATUS CARDS
            # ============================================================
            
            risk_level = data.get('risk_level', 'UNKNOWN')
            risk_score = data.get('risk_score', 0)
            valid_days = data.get('valid_days', 0)
            
            if risk_level == 'CRITICAL':
                risk_color = '#ff2222'
                risk_icon = '🚨'
            elif risk_level == 'HIGH':
                risk_color = '#ff8800'
                risk_icon = '🔴'
            elif risk_level == 'MEDIUM':
                risk_color = '#ffcc00'
                risk_icon = '🟡'
            elif risk_level == 'LOW':
                risk_color = '#00ff41'
                risk_icon = '🟢'
            else:
                risk_color = '#8899bb'
                risk_icon = '❓'
            
            card_data = [
                [
                    Paragraph("🔐", card_title_style),
                    Paragraph("📅", card_title_style),
                    Paragraph("🔑", card_title_style),
                    Paragraph("🛡️", card_title_style)
                ],
                [
                    Paragraph(f"<b>{domain[:25]}</b>", card_value_style),
                    Paragraph(f"<b>{valid_days}</b>", card_value_style),
                    Paragraph(f"<b>{data.get('protocol', 'N/A')}</b>", card_value_style),
                    Paragraph(f"<b>{risk_level}</b>", card_value_style)
                ],
                [
                    Paragraph("Domain", card_label_style),
                    Paragraph("Days Left", card_label_style),
                    Paragraph("Protocol", card_label_style),
                    Paragraph("Risk Level", card_label_style)
                ]
            ]
            
            status_table = Table(card_data, colWidths=[1.4*inch, 1.2*inch, 1.4*inch, 1.2*inch])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0a1525')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2a4a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
                ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#0a1525')),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#ffffff')),
                ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#0a1525')),
                ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#8899bb')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2a4a6a')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            story.append(status_table)
            story.append(Spacer(1, 0.15*inch))

            # ============================================================
            # RISK SCORE PROGRESS BAR
            # ============================================================
            
            story.append(Paragraph("SECURITY SCORE", section_title_style))
            
            bar_length = 50
            filled = int((risk_score / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            if risk_score >= 80:
                bar_color = '#00ff41'
            elif risk_score >= 60:
                bar_color = '#ffcc00'
            elif risk_score >= 40:
                bar_color = '#ff8800'
            else:
                bar_color = '#ff4444'
            
            story.append(Paragraph(f"<font color='{bar_color}'>{bar}</font>", normal_style))
            story.append(Paragraph(f"<font color='{bar_color}'><b>{risk_score}/100</b></font>", card_value_style))
            story.append(Spacer(1, 0.1*inch))

            # ============================================================
            # CERTIFICATE DETAILS
            # ============================================================
            
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Paragraph("📋 CERTIFICATE DETAILS", section_title_style))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Spacer(1, 0.05*inch))
            
            cert_info_data = [
                ['Subject', data.get('subject', 'N/A'), '#00d4ff'],
                ['Issuer', data.get('issuer', 'N/A'), '#ffcc00'],
                ['Protocol', data.get('protocol', 'N/A'), '#00ff41'],
                ['Cipher', data.get('cipher', 'N/A'), '#ff8800'],
                ['Signature', data.get('signature', 'N/A'), '#00ccff'],
                ['Valid Days', f"{data.get('valid_days', 0)} days", '#00ff41' if valid_days > 60 else '#ffcc00' if valid_days > 30 else '#ff4444'],
            ]
            
            cert_rows = []
            for label, value, color in cert_info_data:
                cert_rows.append([
                    Paragraph(f"<b>{label}</b>", bold_normal),
                    Paragraph(f"<font color='{color}'>{value}</font>", normal_style)
                ])
            
            cert_table = Table(cert_rows, colWidths=[1.8*inch, 3.8*inch])
            cert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0a1525')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2a4a6a')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(cert_table)
            story.append(Spacer(1, 0.15*inch))

            # ============================================================
            # SECURITY FINDINGS - WITH EXPLANATIONS
            # ============================================================
            
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Paragraph("🚨 SECURITY FINDINGS", section_title_style))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Spacer(1, 0.05*inch))
            
            findings = data.get('findings', [])
            if findings:
                for finding, severity in findings:
                    if severity == 'CRITICAL':
                        style = finding_critical
                        prefix = "🔴 CRITICAL: "
                    elif severity == 'HIGH':
                        style = finding_high
                        prefix = "🟠 HIGH: "
                    elif severity == 'MEDIUM':
                        style = finding_medium
                        prefix = "🟡 MEDIUM: "
                    elif severity == 'LOW':
                        style = finding_low
                        prefix = "🔵 LOW: "
                    else:
                        style = finding_pass
                        prefix = "✅ PASS: "
                    
                    story.append(Paragraph(f"{prefix}{finding}", style))
                    story.append(Spacer(1, 0.02*inch))
                    
                    # Add explanation for specific findings
                    if "certificate chain" in finding.lower():
                        story.append(Paragraph("📘 <i>What this means: The certificate chain is incomplete. Browsers may show trust warnings.</i>", info_style))
                        story.append(Paragraph("🔧 <i>Fix: Download and install the intermediate certificates from your CA provider.</i>", info_style))
                    elif "expires in less than" in finding.lower():
                        story.append(Paragraph("📘 <i>What this means: Your certificate will expire soon. Renewal is required.</i>", info_style))
                        story.append(Paragraph("🔧 <i>Fix: Contact your certificate provider to renew and install the new certificate.</i>", info_style))
                    elif "SHA1" in finding or "MD5" in finding:
                        story.append(Paragraph("📘 <i>What this means: Weak cryptographic algorithms are being used. They are vulnerable to attacks.</i>", info_style))
                        story.append(Paragraph("🔧 <i>Fix: Request a new certificate with SHA256 signature algorithm.</i>", info_style))
                    elif "RC4" in finding:
                        story.append(Paragraph("📘 <i>What this means: RC4 cipher is weak and deprecated. It should not be used.</i>", info_style))
                        story.append(Paragraph("🔧 <i>Fix: Update your server configuration to disable RC4 cipher suites.</i>", info_style))
                    elif "TLS 1.0/1.1" in finding:
                        story.append(Paragraph("📘 <i>What this means: Deprecated TLS versions are vulnerable to protocol attacks.</i>", info_style))
                        story.append(Paragraph("🔧 <i>Fix: Update server to support only TLS 1.2 and 1.3.</i>", info_style))
                    elif "TLS 1.3 not enabled" in finding:
                        story.append(Paragraph("📘 <i>What this means: TLS 1.3 offers better security and performance than older versions.</i>", info_style))
                        story.append(Paragraph("🔧 <i>Fix: Enable TLS 1.3 in your web server configuration.</i>", info_style))
                    story.append(Spacer(1, 0.03*inch))
            else:
                story.append(Paragraph("✅ No security issues detected. Certificate is secure.", finding_pass))
            
            story.append(Spacer(1, 0.1*inch))

            # ============================================================
            # RECOMMENDATIONS WITH ACTION STEPS
            # ============================================================
            
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Paragraph("💡 RECOMMENDATIONS & ACTION PLAN", section_title_style))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Spacer(1, 0.05*inch))
            
            recs = data.get('recommendations', ['No critical risks detected.'])
            action_counter = 1
            for rec in recs:
                story.append(Paragraph(f"▸ <b>Recommendation {action_counter}:</b> {rec}", rec_style))
                story.append(Spacer(1, 0.02*inch))
                
                # Add detailed action steps based on recommendation type
                if "Renew SSL certificate" in rec or "renew" in rec.lower():
                    story.append(Paragraph("   📋 <b>Action Steps:</b>", bold_normal))
                    story.append(Paragraph("     1. Contact your certificate provider (e.g., Let's Encrypt, DigiCert, Comodo)", rec_action_style))
                    story.append(Paragraph("     2. Generate a new CSR (Certificate Signing Request)", rec_action_style))
                    story.append(Paragraph("     3. Complete domain validation", rec_action_style))
                    story.append(Paragraph("     4. Download the new certificate and intermediate chain", rec_action_style))
                    story.append(Paragraph("     5. Install the new certificate on your server", rec_action_style))
                    story.append(Paragraph("     6. Test the new certificate using this tool: certcheck <domain>", rec_action_style))
                elif "Replace certificate with SHA256" in rec:
                    story.append(Paragraph("   📋 <b>Action Steps:</b>", bold_normal))
                    story.append(Paragraph("     1. Request a new certificate from your CA with SHA256 signature", rec_action_style))
                    story.append(Paragraph("     2. Use tools like OpenSSL to verify: openssl x509 -in cert.pem -text -noout", rec_action_style))
                    story.append(Paragraph("     3. Look for 'Signature Algorithm: sha256WithRSAEncryption'", rec_action_style))
                    story.append(Paragraph("     4. Install and test the new certificate", rec_action_style))
                elif "Disable RC4" in rec:
                    story.append(Paragraph("   📋 <b>Action Steps:</b>", bold_normal))
                    story.append(Paragraph("     1. Locate your server's SSL/TLS configuration file", rec_action_style))
                    story.append(Paragraph("     2. For Apache: SSLCipherSuite HIGH:!RC4:!aNULL:!eNULL", rec_action_style))
                    story.append(Paragraph("     3. For Nginx: ssl_ciphers HIGH:!RC4:!aNULL:!eNULL", rec_action_style))
                    story.append(Paragraph("     4. Restart your web server and verify changes", rec_action_style))
                elif "Upgrade to TLS" in rec or "Enable TLS" in rec:
                    story.append(Paragraph("   📋 <b>Action Steps:</b>", bold_normal))
                    story.append(Paragraph("     1. Check your server's TLS configuration", rec_action_style))
                    story.append(Paragraph("     2. For Apache: SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1", rec_action_style))
                    story.append(Paragraph("     3. For Nginx: ssl_protocols TLSv1.2 TLSv1.3;", rec_action_style))
                    story.append(Paragraph("     4. Test with: openssl s_client -connect domain.com:443 -tls1_3", rec_action_style))
                elif "Install full certificate chain" in rec or "full chain" in rec.lower():
                    story.append(Paragraph("   📋 <b>Action Steps:</b>", bold_normal))
                    story.append(Paragraph("     1. Download the intermediate certificates from your CA", rec_action_style))
                    story.append(Paragraph("     2. Create a chain file: cat certificate.crt intermediate.crt > fullchain.crt", rec_action_style))
                    story.append(Paragraph("     3. Configure your server to use the full chain file", rec_action_style))
                    story.append(Paragraph("     4. For Nginx: ssl_trusted_certificate /path/to/fullchain.crt;", rec_action_style))
                    story.append(Paragraph("     5. Restart server and verify with: certcheck <domain>", rec_action_style))
                elif "No critical risks" in rec:
                    story.append(Paragraph("   📋 <b>Maintenance Steps:</b>", bold_normal))
                    story.append(Paragraph("     1. Monitor certificate expiry with automated alerts", rec_action_style))
                    story.append(Paragraph("     2. Set up certificate renewal reminders 30 days before expiry", rec_action_style))
                    story.append(Paragraph("     3. Use certbot or other automation for Let's Encrypt renewals", rec_action_style))
                    story.append(Paragraph("     4. Regularly run security audits: certcheck <domain>", rec_action_style))
                else:
                    story.append(Paragraph("   📋 <b>Action Steps:</b>", bold_normal))
                    story.append(Paragraph("     1. Review your SSL/TLS configuration", rec_action_style))
                    story.append(Paragraph("     2. Test with: certcheck <domain>", rec_action_style))
                    story.append(Paragraph("     3. Consult your security team for implementation", rec_action_style))
                
                story.append(Spacer(1, 0.05*inch))
                action_counter += 1
            
            story.append(Spacer(1, 0.1*inch))

            # ============================================================
            # SUBJECT ALTERNATIVE NAMES
            # ============================================================
            
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Paragraph("🌐 SUBJECT ALTERNATIVE NAMES (SANs)", section_title_style))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Spacer(1, 0.05*inch))
            
            san_list = data.get('san_list', ['No SANs found'])
            if san_list and san_list != ['No SANs found']:
                for san in san_list[:10]:
                    story.append(Paragraph(f"▸ {san}", normal_style))
                
                if len(san_list) > 10:
                    story.append(Paragraph(f"▸ ... and {len(san_list) - 10} more", normal_style))
            else:
                story.append(Paragraph("No Subject Alternative Names found", normal_style))
            
            story.append(Spacer(1, 0.1*inch))

            # ============================================================
            # CERTIFICATE CHAIN
            # ============================================================
            
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Paragraph("🔗 CERTIFICATE CHAIN", section_title_style))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Spacer(1, 0.05*inch))
            
            chain = data.get('chain', [])
            if chain:
                for i, cert in enumerate(chain):
                    indent = "  " * i
                    subject_name = cert.get('subject_cn', 'Unknown')
                    issuer_name = cert.get('issuer_cn', 'Unknown')
                    
                    if i == 0:
                        role = "Leaf"
                        color = '#00ff41'
                    elif i == len(chain) - 1:
                        role = "Root"
                        color = '#ffcc00'
                    else:
                        role = "Intermediate"
                        color = '#00d4ff'
                    
                    story.append(Paragraph(f"{indent}├─ <font color='{color}'><b>[{role}]</b></font> {subject_name}", normal_style))
                    story.append(Paragraph(f"{indent}    <font color='#8899bb'>Issuer:</font> {issuer_name}", normal_style))
                    story.append(Spacer(1, 0.02*inch))
                
                # Add chain validation explanation
                if len(chain) < 2:
                    story.append(Paragraph("⚠️ <b>Incomplete Chain Detected!</b>", finding_high))
                    story.append(Paragraph("   Your certificate chain is missing intermediate certificates.", normal_style))
                    story.append(Paragraph("   <b>How to fix:</b> Download intermediate certificates from your CA and concatenate them with your certificate.", normal_style))
            else:
                story.append(Paragraph("No certificate chain information available", normal_style))
            
            story.append(Spacer(1, 0.1*inch))

            # ============================================================
            # SECURITY TIPS & BEST PRACTICES
            # ============================================================
            
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Paragraph("🛡️ SECURITY BEST PRACTICES", section_title_style))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            story.append(Spacer(1, 0.05*inch))
            
            tips = [
                "🔒 Use TLS 1.3 on all servers for best security and performance",
                "📅 Set up automated certificate renewal at least 30 days before expiry",
                "🔑 Use RSA 2048+ or ECDSA 256+ for strong cryptography",
                "🛡️ Implement HSTS (HTTP Strict Transport Security) headers",
                "📋 Monitor Certificate Transparency logs at crt.sh",
                "🔍 Regularly test with: certcheck <your-domain>",
                "⚡ Enable OCSP stapling for faster revocation checking",
                "📊 Use Qualys SSL Labs for public security testing"
            ]
            
            for tip in tips:
                story.append(Paragraph(f"▸ {tip}", normal_style))
                story.append(Spacer(1, 0.02*inch))
            
            story.append(Spacer(1, 0.1*inch))

            # ============================================================
            # FOOTER
            # ============================================================
            
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))
            
            footer_style = ParagraphStyle(
                'DashboardFooter',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#6688aa'),
                alignment=TA_CENTER,
                spaceBefore=10,
                fontName='Helvetica'
            )
            
            story.append(Paragraph(f"Generated by DSTerminal Security Suite v5.0.0", footer_style))
            story.append(Paragraph(f"Report ID: {timestamp} | Domain: {domain}", footer_style))
            story.append(Paragraph("🔒 This report is digitally authenticated by DSTerminal Certificate Authority", footer_style))
            story.append(Paragraph("© 2024 DSTerminal Security Platform - Stark Expo Tech Exchange", footer_style))
            story.append(Paragraph(f"<font color='#00ff41'>═</font>" * 80, normal_style))

            # Build the document
            doc.build(story)
            self._type_success(f"Dashboard PDF report generated: {report_file}")
            return report_file
        except Exception as e:
            self._type_error(f"PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_html_report(self, data: Dict) -> Optional[str]:
        """Generate a beautiful dark-themed HTML report with all findings"""
        try:
            domain = data.get("domain", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                self.report_dir,
                f"ssl_report_{domain}_{timestamp}.html"
            )

            risk_level = data.get('risk_level', 'UNKNOWN')
            risk_score = data.get('risk_score', 0)
            valid_days = data.get('valid_days', 0)
            
            risk_icon = {
                'CRITICAL': '🚨',
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }.get(risk_level, '❓')

            # Determine risk color
            if risk_level == 'CRITICAL':
                risk_color = '#ff2222'
                risk_bg = '#2a0000'
            elif risk_level == 'HIGH':
                risk_color = '#ff8800'
                risk_bg = '#2a0a00'
            elif risk_level == 'MEDIUM':
                risk_color = '#ffcc00'
                risk_bg = '#2a2a00'
            elif risk_level == 'LOW':
                risk_color = '#00ff41'
                risk_bg = '#002a00'
            else:
                risk_color = '#8899bb'
                risk_bg = '#1a1a2a'
                risk_icon = '❓'
            
            # Build findings HTML
            findings_html = ""
            findings = data.get('findings', [])
            if findings:
                for finding, severity in findings:
                    if severity == 'CRITICAL':
                        badge = '<span class="badge badge-critical">CRITICAL</span>'
                        icon = '🚨'
                    elif severity == 'HIGH':
                        badge = '<span class="badge badge-high">HIGH</span>'
                        icon = '🔴'
                    elif severity == 'MEDIUM':
                        badge = '<span class="badge badge-medium">MEDIUM</span>'
                        icon = '🟡'
                    elif severity == 'LOW':
                        badge = '<span class="badge badge-low">LOW</span>'
                        icon = '🔵'
                    else:
                        badge = '<span class="badge badge-pass">PASS</span>'
                        icon = '✅'
                    
                    findings_html += f'''
                    <div class="finding-item">
                        <div class="finding-header">
                            {badge}
                            <span class="finding-icon">{icon}</span>
                            <span class="finding-text">{finding}</span>
                        </div>
                    '''
                    
                    # Add explanation for specific findings
                    if "certificate chain" in finding.lower():
                        findings_html += '''
                        <div class="finding-explanation">
                            <div class="explanation-title">📘 What this means:</div>
                            <div class="explanation-text">The certificate chain is incomplete. Browsers may show trust warnings.</div>
                            <div class="explanation-title">🔧 How to fix:</div>
                            <div class="explanation-text">Download and install the intermediate certificates from your CA provider.</div>
                        </div>
                        '''
                    elif "expires in less than" in finding.lower():
                        findings_html += '''
                        <div class="finding-explanation">
                            <div class="explanation-title">📘 What this means:</div>
                            <div class="explanation-text">Your certificate will expire soon. Renewal is required.</div>
                            <div class="explanation-title">🔧 How to fix:</div>
                            <div class="explanation-text">Contact your certificate provider to renew and install the new certificate.</div>
                        </div>
                        '''
                    elif "SHA1" in finding or "MD5" in finding:
                        findings_html += '''
                        <div class="finding-explanation">
                            <div class="explanation-title">📘 What this means:</div>
                            <div class="explanation-text">Weak cryptographic algorithms are being used. They are vulnerable to attacks.</div>
                            <div class="explanation-title">🔧 How to fix:</div>
                            <div class="explanation-text">Request a new certificate with SHA256 signature algorithm.</div>
                        </div>
                        '''
                    elif "RC4" in finding:
                        findings_html += '''
                        <div class="finding-explanation">
                            <div class="explanation-title">📘 What this means:</div>
                            <div class="explanation-text">RC4 cipher is weak and deprecated. It should not be used.</div>
                            <div class="explanation-title">🔧 How to fix:</div>
                            <div class="explanation-text">Update your server configuration to disable RC4 cipher suites.</div>
                        </div>
                        '''
                    elif "TLS 1.0/1.1" in finding:
                        findings_html += '''
                        <div class="finding-explanation">
                            <div class="explanation-title">📘 What this means:</div>
                            <div class="explanation-text">Deprecated TLS versions are vulnerable to protocol attacks.</div>
                            <div class="explanation-title">🔧 How to fix:</div>
                            <div class="explanation-text">Update server to support only TLS 1.2 and 1.3.</div>
                        </div>
                        '''
                    elif "TLS 1.3 not enabled" in finding:
                        findings_html += '''
                        <div class="finding-explanation">
                            <div class="explanation-title">📘 What this means:</div>
                            <div class="explanation-text">TLS 1.3 offers better security and performance than older versions.</div>
                            <div class="explanation-title">🔧 How to fix:</div>
                            <div class="explanation-text">Enable TLS 1.3 in your web server configuration.</div>
                        </div>
                        '''
                    findings_html += '</div>'
            else:
                findings_html = '<div class="finding-item"><span class="finding-text">✅ No security issues detected. Certificate is secure.</span></div>'
            
            # Build recommendations HTML
            recs_html = ""
            recs = data.get('recommendations', ['No critical risks detected.'])
            action_counter = 1
            for rec in recs:
                recs_html += f'''
                <div class="recommendation-item">
                    <div class="rec-title">▸ <strong>Recommendation {action_counter}:</strong> {rec}</div>
                '''
                
                # Add action steps based on recommendation type
                if "Renew SSL certificate" in rec or "renew" in rec.lower():
                    recs_html += '''
                    <div class="action-steps">
                        <div class="action-title">📋 Action Steps:</div>
                        <ol>
                            <li>Contact your certificate provider (e.g., Let's Encrypt, DigiCert, Comodo)</li>
                            <li>Generate a new CSR (Certificate Signing Request)</li>
                            <li>Complete domain validation</li>
                            <li>Download the new certificate and intermediate chain</li>
                            <li>Install the new certificate on your server</li>
                            <li>Test the new certificate using this tool: certcheck &lt;domain&gt;</li>
                        </ol>
                    </div>
                    '''
                elif "Replace certificate with SHA256" in rec:
                    recs_html += '''
                    <div class="action-steps">
                        <div class="action-title">📋 Action Steps:</div>
                        <ol>
                            <li>Request a new certificate from your CA with SHA256 signature</li>
                            <li>Use tools like OpenSSL to verify: openssl x509 -in cert.pem -text -noout</li>
                            <li>Look for 'Signature Algorithm: sha256WithRSAEncryption'</li>
                            <li>Install and test the new certificate</li>
                        </ol>
                    </div>
                    '''
                elif "Disable RC4" in rec:
                    recs_html += '''
                    <div class="action-steps">
                        <div class="action-title">📋 Action Steps:</div>
                        <ol>
                            <li>Locate your server's SSL/TLS configuration file</li>
                            <li>For Apache: SSLCipherSuite HIGH:!RC4:!aNULL:!eNULL</li>
                            <li>For Nginx: ssl_ciphers HIGH:!RC4:!aNULL:!eNULL</li>
                            <li>Restart your web server and verify changes</li>
                        </ol>
                    </div>
                    '''
                elif "Upgrade to TLS" in rec or "Enable TLS" in rec:
                    recs_html += '''
                    <div class="action-steps">
                        <div class="action-title">📋 Action Steps:</div>
                        <ol>
                            <li>Check your server's TLS configuration</li>
                            <li>For Apache: SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1</li>
                            <li>For Nginx: ssl_protocols TLSv1.2 TLSv1.3;</li>
                            <li>Test with: openssl s_client -connect domain.com:443 -tls1_3</li>
                        </ol>
                    </div>
                    '''
                elif "Install full certificate chain" in rec or "full chain" in rec.lower():
                    recs_html += '''
                    <div class="action-steps">
                        <div class="action-title">📋 Action Steps:</div>
                        <ol>
                            <li>Download the intermediate certificates from your CA</li>
                            <li>Create a chain file: cat certificate.crt intermediate.crt > fullchain.crt</li>
                            <li>Configure your server to use the full chain file</li>
                            <li>For Nginx: ssl_trusted_certificate /path/to/fullchain.crt;</li>
                            <li>Restart server and verify with: certcheck &lt;domain&gt;</li>
                        </ol>
                    </div>
                    '''
                elif "No critical risks" in rec:
                    recs_html += '''
                    <div class="action-steps">
                        <div class="action-title">📋 Maintenance Steps:</div>
                        <ol>
                            <li>Monitor certificate expiry with automated alerts</li>
                            <li>Set up certificate renewal reminders 30 days before expiry</li>
                            <li>Use certbot or other automation for Let's Encrypt renewals</li>
                            <li>Regularly run security audits: certcheck &lt;domain&gt;</li>
                        </ol>
                    </div>
                    '''
                else:
                    recs_html += '''
                    <div class="action-steps">
                        <div class="action-title">📋 Action Steps:</div>
                        <ol>
                            <li>Review your SSL/TLS configuration</li>
                            <li>Test with: certcheck &lt;domain&gt;</li>
                            <li>Consult your security team for implementation</li>
                        </ol>
                    </div>
                    '''
                
                recs_html += '</div>'
                action_counter += 1
            
            # Build SAN list
            san_html = ""
            san_list = data.get('san_list', ['No SANs found'])
            if san_list and san_list != ['No SANs found']:
                for san in san_list[:10]:
                    san_html += f'<li class="san-item">{san}</li>'
                if len(san_list) > 10:
                    san_html += f'<li class="san-item">... and {len(san_list) - 10} more</li>'
            else:
                san_html = '<li class="san-item">No Subject Alternative Names found</li>'
            
            # Build certificate chain HTML
            chain_html = ""
            chain = data.get('chain', [])
            if chain:
                for i, cert in enumerate(chain):
                    indent = "  " * i
                    subject_name = cert.get('subject_cn', 'Unknown')
                    issuer_name = cert.get('issuer_cn', 'Unknown')
                    
                    if i == 0:
                        role = "Leaf"
                        color = '#00ff41'
                    elif i == len(chain) - 1:
                        role = "Root"
                        color = '#ffcc00'
                    else:
                        role = "Intermediate"
                        color = '#00d4ff'
                    
                    chain_html += f'''
                    <div class="chain-item" style="padding-left: {i * 20}px;">
                        <span class="chain-role" style="color: {color};">├─ [{role}]</span>
                        <span class="chain-subject">{subject_name}</span>
                        <div class="chain-issuer" style="padding-left: 25px; color: #8899bb;">Issuer: {issuer_name}</div>
                    </div>
                    '''
                
                if len(chain) < 2:
                    chain_html += '''
                    <div class="chain-warning" style="margin-top: 15px; padding: 10px; background: #2a0a00; border-left: 3px solid #ff8800; border-radius: 4px;">
                        <div style="color: #ff8800; font-weight: bold;">⚠️ Incomplete Chain Detected!</div>
                        <div style="color: #e0e8f0; margin-top: 5px;">Your certificate chain is missing intermediate certificates.</div>
                        <div style="color: #e0e8f0; margin-top: 5px;"><strong>How to fix:</strong> Download intermediate certificates from your CA and concatenate them with your certificate.</div>
                    </div>
                    '''
            else:
                chain_html = '<div class="chain-item">No certificate chain information available</div>'
            
            # Build tips HTML
            tips = [
                "🔒 Use TLS 1.3 on all servers for best security and performance",
                "📅 Set up automated certificate renewal at least 30 days before expiry",
                "🔑 Use RSA 2048+ or ECDSA 256+ for strong cryptography",
                "🛡️ Implement HSTS (HTTP Strict Transport Security) headers",
                "📋 Monitor Certificate Transparency logs at crt.sh",
                "🔍 Regularly test with: certcheck <your-domain>",
                "⚡ Enable OCSP stapling for faster revocation checking",
                "📊 Use Qualys SSL Labs for public security testing"
            ]
            tips_html = ""
            for tip in tips:
                tips_html += f'<li class="tip-item">{tip}</li>'
            
            html_content = f'''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DSTerminal SSL/TLS Security Report - {domain}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
                background: #0a1525;
                color: #e0e8f0;
                padding: 20px;
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: linear-gradient(145deg, #0d1b2a, #0a1525);
                border-radius: 16px;
                padding: 30px;
                border: 1px solid #1a2a4a;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            }}
            
            .header {{
                text-align: center;
                padding: 20px 0 30px 0;
                border-bottom: 2px solid #1a2a4a;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                font-size: 28px;
                color: #00ff41;
                font-weight: bold;
                margin-bottom: 8px;
            }}
            
            .header .subtitle {{
                font-size: 14px;
                color: #00ccff;
            }}
            
            .header .meta {{
                font-size: 12px;
                color: #6688aa;
                margin-top: 10px;
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin-bottom: 25px;
            }}
            
            .card {{
                background: #0a1525;
                border-radius: 12px;
                padding: 16px 20px;
                border: 1px solid #1a2a4a;
                text-align: center;
            }}
            
            .card .icon {{
                font-size: 22px;
                margin-bottom: 4px;
            }}
            
            .card .value {{
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
            }}
            
            .card .label {{
                font-size: 11px;
                color: #6688aa;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 2px;
            }}
            
            .section {{
                margin-top: 25px;
            }}
            
            .section-title {{
                font-size: 18px;
                color: #00ff41;
                font-weight: bold;
                padding-bottom: 10px;
                border-bottom: 2px solid #1a2a4a;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .section-title .count {{
                font-size: 12px;
                color: #6688aa;
                font-weight: normal;
            }}
            
            .cert-detail {{
                display: flex;
                padding: 8px 0;
                border-bottom: 1px solid #0d1b2a;
            }}
            
            .cert-detail .label {{
                width: 140px;
                font-weight: bold;
                color: #ffffff;
                flex-shrink: 0;
            }}
            
            .cert-detail .value {{
                color: #e0e8f0;
            }}
            
            .cert-detail .value.highlight {{
                color: #00ff41;
            }}
            
            .finding-item {{
                background: #0a1525;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 10px;
                border-left: 3px solid #1a2a4a;
            }}
            
            .finding-header {{
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }}
            
            .badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            
            .badge-critical {{
                background: #ff2222;
                color: #ffffff;
            }}
            
            .badge-high {{
                background: #ff8800;
                color: #ffffff;
            }}
            
            .badge-medium {{
                background: #ffcc00;
                color: #1a1a2a;
            }}
            
            .badge-low {{
                background: #00ccff;
                color: #1a1a2a;
            }}
            
            .badge-pass {{
                background: #00ff41;
                color: #1a1a2a;
            }}
            
            .finding-icon {{
                font-size: 16px;
            }}
            
            .finding-text {{
                color: #e0e8f0;
                font-size: 13px;
            }}
            
            .finding-explanation {{
                margin-top: 8px;
                padding: 10px 14px;
                background: #0d1b2a;
                border-radius: 6px;
                border-left: 3px solid #00ccff;
            }}
            
            .explanation-title {{
                font-size: 12px;
                font-weight: bold;
                color: #00ccff;
                margin-top: 4px;
            }}
            
            .explanation-title:first-child {{
                margin-top: 0;
            }}
            
            .explanation-text {{
                font-size: 12px;
                color: #c0d0e0;
                margin-left: 4px;
                margin-bottom: 4px;
            }}
            
            .recommendation-item {{
                background: #0a1525;
                border-radius: 8px;
                padding: 14px 16px;
                margin-bottom: 12px;
                border-left: 3px solid #00d4ff;
            }}
            
            .rec-title {{
                color: #e0e8f0;
                font-size: 13px;
                margin-bottom: 6px;
            }}
            
            .action-steps {{
                margin-top: 6px;
                padding: 10px 14px;
                background: #0d1b2a;
                border-radius: 6px;
            }}
            
            .action-title {{
                font-size: 12px;
                font-weight: bold;
                color: #00ccff;
                margin-bottom: 4px;
            }}
            
            .action-steps ol {{
                margin-left: 20px;
                color: #c0d0e0;
                font-size: 12px;
            }}
            
            .action-steps ol li {{
                margin-bottom: 2px;
            }}
            
            .san-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                list-style: none;
                padding: 0;
            }}
            
            .san-item {{
                background: #0d1b2a;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 13px;
                color: #c0d0e0;
                border: 1px solid #1a2a4a;
            }}
            
            .chain-item {{
                padding: 4px 0;
                font-size: 13px;
            }}
            
            .chain-role {{
                font-weight: bold;
                margin-right: 6px;
            }}
            
            .chain-subject {{
                color: #e0e8f0;
            }}
            
            .chain-issuer {{
                font-size: 12px;
            }}
            
            .tips-list {{
                list-style: none;
                padding: 0;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 8px;
            }}
            
            .tip-item {{
                background: #0d1b2a;
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 13px;
                color: #c0d0e0;
                border-left: 2px solid #00d4ff;
            }}
            
            .progress-bar {{
                background: #0a1525;
                border-radius: 8px;
                height: 20px;
                overflow: hidden;
                margin: 8px 0;
                border: 1px solid #1a2a4a;
            }}
            
            .progress-fill {{
                height: 100%;
                border-radius: 8px;
                transition: width 0.5s ease;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 8px;
                font-size: 11px;
                font-weight: bold;
                color: #0a1525;
            }}
            
            .risk-indicator {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: bold;
            }}
            
            .risk-critical {{
                background: #ff2222;
                color: #ffffff;
            }}
            
            .risk-high {{
                background: #ff8800;
                color: #ffffff;
            }}
            
            .risk-medium {{
                background: #ffcc00;
                color: #1a1a2a;
            }}
            
            .risk-low {{
                background: #00ff41;
                color: #1a1a2a;
            }}
            
            .risk-unknown {{
                background: #6688aa;
                color: #ffffff;
            }}
            
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #1a2a4a;
                text-align: center;
                font-size: 11px;
                color: #6688aa;
            }}
            
            .footer .brand {{
                color: #00ff41;
                font-weight: bold;
            }}
            
            @media (max-width: 600px) {{
                .container {{ padding: 16px; }}
                .grid {{ grid-template-columns: repeat(2, 1fr); }}
                .cert-detail {{ flex-direction: column; padding: 6px 0; }}
                .cert-detail .label {{ width: 100%; }}
                .tips-list {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>🛡️ SSL/TLS Security Report</h1>
            <div class="subtitle">{domain}</div>
            <div class="meta">Generated: {data.get('scan_time', 'N/A')} | Report ID: {timestamp}</div>
        </div>
        
        <!-- STATUS CARDS -->
        <div class="grid">
            <div class="card">
                <div class="icon">🔐</div>
                <div class="value">{domain[:25]}</div>
                <div class="label">Domain</div>
            </div>
            <div class="card">
                <div class="icon">📅</div>
                <div class="value">{valid_days}</div>
                <div class="label">Days Left</div>
            </div>
            <div class="card">
                <div class="icon">🔑</div>
                <div class="value">{data.get('protocol', 'N/A')}</div>
                <div class="label">Protocol</div>
            </div>
            <div class="card">
                <div class="icon">🛡️</div>
                <div class="value"><span class="risk-indicator risk-{risk_level.lower()}">{risk_icon} {risk_level}</span></div>
                <div class="label">Risk Level</div>
            </div>
        </div>
        
        <!-- SECURITY SCORE -->
        <div class="section">
            <div class="section-title">📊 Security Score</div>
            <div style="font-size: 24px; font-weight: bold; color: {'#00ff41' if risk_score >= 80 else '#ffcc00' if risk_score >= 60 else '#ff8800' if risk_score >= 40 else '#ff4444'};">
                {risk_score}/100
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {risk_score}%; background: {'#00ff41' if risk_score >= 80 else '#ffcc00' if risk_score >= 60 else '#ff8800' if risk_score >= 40 else '#ff4444'};">
                    {risk_score}%
                </div>
            </div>
        </div>
        
        <!-- CERTIFICATE DETAILS -->
        <div class="section">
            <div class="section-title">📋 Certificate Details</div>
            <div class="cert-detail"><span class="label">Subject</span><span class="value">{data.get('subject', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Issuer</span><span class="value">{data.get('issuer', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Protocol</span><span class="value">{data.get('protocol', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Cipher</span><span class="value">{data.get('cipher', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Signature</span><span class="value">{data.get('signature', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Valid Days</span><span class="value highlight">{valid_days} days</span></div>
            <div class="cert-detail"><span class="label">Issued</span><span class="value">{data.get('issued', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Expires</span><span class="value">{data.get('expires', 'N/A')}</span></div>
        </div>
        
        <!-- EXPIRATION ANALYSIS -->
        <div class="section">
            <div class="section-title">⏰ Expiration Analysis</div>
            <div class="cert-detail"><span class="label">Issued</span><span class="value">{data.get('issued', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Expires</span><span class="value">{data.get('expires', 'N/A')}</span></div>
            <div class="cert-detail"><span class="label">Days Remaining</span><span class="value highlight">{valid_days} days</span></div>
        </div>
        
        <!-- SECURITY FINDINGS -->
        <div class="section">
            <div class="section-title">🚨 Security Findings <span class="count">({len(findings)})</span></div>
            {findings_html}
        </div>
        
        <!-- RECOMMENDATIONS -->
        <div class="section">
            <div class="section-title">💡 Recommendations <span class="count">({len(recs)})</span></div>
            {recs_html}
        </div>
        
        <!-- SUBJECT ALTERNATIVE NAMES -->
        <div class="section">
            <div class="section-title">🌐 Subject Alternative Names (SANs)</div>
            <ul class="san-list">
                {san_html}
            </ul>
        </div>
        
        <!-- CERTIFICATE CHAIN -->
        <div class="section">
            <div class="section-title">🔗 Certificate Chain</div>
            {chain_html}
        </div>
        
        <!-- SECURITY TIPS -->
        <div class="section">
            <div class="section-title">🛡️ Security Best Practices</div>
            <ul class="tips-list">
                {tips_html}
            </ul>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <div>Generated by <span class="brand">DSTerminal Security Suite v5.0.0</span></div>
            <div>Report ID: {timestamp} | Domain: {domain}</div>
            <div>🔒 This report is digitally authenticated by DSTerminal Certificate Authority</div>
            <div>© 2024 DSTerminal Security Platform - Stark Expo Tech Exchange</div>
        </div>
    </div>
    </body>
    </html>'''

            # Write the HTML file
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self._type_success(f"HTML report generated: {report_file}")
            return report_file
        except Exception as e:
            self._type_error(f"HTML report generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _print_banner(self, domain: str):
        """Print the banner with random colors - RESPONSIVE & CENTERED"""
        self.term_width = self._get_terminal_width()
        colors = self._random_colors
        
        banner = f"""
    {self._center_text("┌" + "─" * 60 + "┐", colors['border'])}
    {self._center_text("│" + " " * 18 + "🔐 CA TRUST CERTIFICATE MODULE" + " " * 18 + "│", colors['title'])}
    {self._center_text("├" + "─" * 60 + "┤", colors['border'])}
    {self._center_text("│" + " " * 24 + "🔍 CA TRUST VERIFICATION" + " " * 24 + "│", colors['subtitle'])}
    {self._center_text("├" + "─" * 60 + "┤", colors['border'])}
    {self._center_text("│" + " " * 24 + f"🌐 {domain}" + " " * (24 - len(domain)) + "│", colors['domain'])}
    {self._center_text("└" + "─" * 60 + "┘", colors['border'])}
    {self._center_text("")}
    {self._center_text("  ╔══════════════════════════════════════════════════════════════╗", colors['border'])}
    {self._center_text("  ║     ██████╗  █████╗     ████████╗██████╗ ██╗   ██╗███████╗████████╗    ║", colors['ascii'])}
    {self._center_text("  ║    ██╔════╝ ██╔══██╗    ╚══██╔══╝██╔══██╗██║   ██║██╔════╝╚══██╔══╝    ║", colors['ascii'])}
    {self._center_text("  ║    ██║      ███████║       ██║   ██████╔╝██║   ██║███████╗   ██║       ║", colors['ascii'])}
    {self._center_text("  ║    ██║      ██╔══██║       ██║   ██╔══██╗██║   ██║╚════██║   ██║       ║", colors['ascii'])}
    {self._center_text("  ║    ╚██████╗ ██║  ██║       ██║   ██║  ██║╚██████╔╝███████║   ██║       ║", colors['ascii'])}
    {self._center_text("  ║     ╚═════╝ ╚═╝  ╚═╝       ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ║", colors['ascii'])}
    {self._center_text("  ║                                                                             ║", colors['border'])}
    {self._center_text("  ║              🔐 CA TRUST CERTIFICATE SECURITY MODULE                       ║", colors['title'])}
    {self._center_text("  ║                                                                             ║", colors['border'])}
    {self._center_text("  ╚══════════════════════════════════════════════════════════════╝", colors['border'])}
    """
        print(banner)
        time.sleep(0.2)

    def _validate_domain(self, domain: str) -> bool:
        """
        Validate that the input is a proper domain name.
        
        Args:
            domain: Domain name to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        
        # Remove any protocol prefixes
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^ftp://', '', domain)
        domain = re.sub(r'^wss?://', '', domain)
        
        # Remove trailing slashes
        domain = domain.rstrip('/')
        
        # Remove port numbers
        domain = re.sub(r':\d+$', '', domain)
        
        # Remove path components
        domain = domain.split('/')[0]
        
        # Domain regex pattern
        pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,24}$'
        
        if re.match(pattern, domain):
            return True
        
        # Check for IP address
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ip_pattern, domain):
            return True
        
        # Check for localhost
        if domain.lower() in ['localhost', '127.0.0.1', '::1']:
            return True
        
        return False

    def _clean_domain(self, domain: str) -> str:
        """
        Clean and normalize domain input.
        
        Args:
            domain: Raw domain input
            
        Returns:
            Cleaned domain string
        """
        import re
        
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^ftp://', '', domain)
        domain = re.sub(r'^wss?://', '', domain)
        domain = domain.rstrip('/')
        domain = re.sub(r':\d+$', '', domain)
        domain = domain.split('/')[0]
        domain = domain.strip()
        
        return domain

    def check(self, domain: str) -> Dict[str, Any]:
        """
        Main entry point for certificate checking with domain validation.
        
        Args:
            domain: Domain name to check
            
        Returns:
            Dictionary with certificate information
        """
        if not OPENSSL_AVAILABLE:
            print(self._colored("[!] pyOpenSSL is required. Install with: pip install pyopenssl", 'error'))
            return {'error': 'pyOpenSSL not installed'}
        
        # If no domain provided, prompt for one
        if not domain:
            while True:
                domain = input(self._colored("Enter domain to check (e.g., starkexpo.com): ", 'info')).strip()
                
                if not domain:
                    print(self._colored("❌ No domain provided. Please enter a valid domain.", 'error'))
                    continue
                
                cleaned_domain = self._clean_domain(domain)
                
                if self._validate_domain(cleaned_domain):
                    domain = cleaned_domain
                    break
                else:
                    print(self._colored(f"❌ Invalid domain: '{domain}'", 'error'))
                    print(self._colored("   Please enter a valid domain (e.g., starkexpo.com, google.com)", 'info'))
                    print(self._colored("   Examples of valid domains:", 'dim'))
                    print(self._colored("     • example.com", 'dim'))
                    print(self._colored("     • sub.example.co.uk", 'dim'))
                    print(self._colored("     • 192.168.1.1 (IP address)", 'dim'))
                    print(self._colored("     • localhost (local testing)", 'dim'))
                    continue
        else:
            cleaned_domain = self._clean_domain(domain)
            
            if not self._validate_domain(cleaned_domain):
                print(self._colored(f"❌ Invalid domain: '{domain}'", 'error'))
                print(self._colored("   Please provide a valid domain (e.g., starkexpo.com, google.com)", 'info'))
                
                while True:
                    domain = input(self._colored("Enter valid domain: ", 'info')).strip()
                    if not domain:
                        print(self._colored("❌ No domain provided.", 'error'))
                        continue
                    
                    cleaned_domain = self._clean_domain(domain)
                    if self._validate_domain(cleaned_domain):
                        domain = cleaned_domain
                        break
                    else:
                        print(self._colored(f"❌ Invalid domain: '{domain}'", 'error'))
                        continue
            else:
                domain = cleaned_domain
        
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