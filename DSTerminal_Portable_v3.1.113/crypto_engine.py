#!/usr/bin/env python3
"""
DSTERMINAL - ENCRYPTION SUITE [EDITION]
Dashboard Layout with Multi-Panel Design
Interactive cinematic mode with real-time encryption visualization
QR Code Key Management Integration - CROSS PLATFORM
Human-like typing feedback system
DIRECTORY/FOLDER ENCRYPTION SUPPORT
"""
import os
import sys
import ctypes

# Enable ANSI support for Windows 10/11
if sys.platform == 'win32':
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# Force disable colors if needed (uncomment if needed)
# os.environ['NO_COLOR'] = '1'

# Check if we should use colors
def should_use_colors():
    """Determine if we should use ANSI colors"""
    # Check if NO_COLOR environment variable is set
    if os.environ.get('NO_COLOR'):
        return False
    
    # Check if we're in a terminal
    if not sys.stdout.isatty():
        return False
    
    # Check for Windows
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # Check if ENABLE_VIRTUAL_TERMINAL_PROCESSING is set
                return bool(mode.value & 0x4)
            return False
        except:
            return False
    
    return True

# Set a global flag
USE_COLORS = should_use_colors()

import time
import hashlib
import shutil
import base64
import random
import threading
import tempfile
import platform
import subprocess
import json
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet

# Try to import QR code dependencies with better error handling
try:
    import qrcode
    from PIL import Image
    import cv2
    import numpy as np
    QR_DEPS_AVAILABLE = True
    QR_METHOD = 'opencv'
except ImportError as e:
    QR_DEPS_AVAILABLE = False
    QR_METHOD = None
    print(f"⚠️ QR Code dependencies not available: {e}")
    print(f"💡 Install with: pip install qrcode[pil] pillow opencv-python-headless")

# Try to import report generation libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORT_AVAILABLE = True
except ImportError:
    REPORT_AVAILABLE = False
    print("⚠️ Report generation unavailable. Install: pip install reportlab")
USE_COLORS = False
# ANSI color codes for terminal effects
# ANSI color codes for terminal effects
class Colors:
    """Cross-platform color support with Windows fallback"""
    
    # Color definitions - works on most modern terminals
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLACK = '\033[90m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    DIM = '\033[2m'
    BLINK = '\033[5m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    @staticmethod
    def init_colors():
        """Initialize color support for Windows"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
    
    @staticmethod
    def strip(text):
        """Strip ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# Initialize colors on Windows
Colors.init_colors()
# Add this helper function
def strip_ansi(text):
    """Strip ANSI escape sequences from text"""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# Override the print function to strip colors if needed
import builtins
original_print = builtins.print

def safe_print(*args, **kwargs):
    """Print with ANSI codes stripped if colors are disabled"""
    if not Colors.ENABLED:
        args = [strip_ansi(str(arg)) for arg in args]
    original_print(*args, **kwargs)

# Uncomment to use safe_print
# builtins.print = safe_print

class TypeWriter:
    """Human-like typing simulation with realistic delays"""
    
    def __init__(self, speed='medium'):
        self.speed_presets = {
            'slow': (40, 80),
            'medium': (20, 40),
            'fast': (10, 20),
            'instant': (0, 0)
        }
        self.set_speed(speed)
        self.punctuation_delay = 1.5
        self.typing_enabled = True
        self._stop_typing = False
    
    def set_speed(self, speed):
        if speed in self.speed_presets:
            self.min_delay, self.max_delay = self.speed_presets[speed]
        else:
            self.min_delay, self.max_delay = self.speed_presets['medium']
    
    def type_text(self, text, color=Colors.GREEN, newline=True, pause_between_chars=True):
        # Strip colors if USE_COLORS is False
        if not USE_COLORS:
            text = strip_ansi(text)
            color = ''
        
        if not self.typing_enabled:
            print(f"{text}", end='\n' if newline else '')
            return
        
        pause_chars = ['.', ',', '!', '?', ';', ':', '...']
        
        for i, char in enumerate(text):
            if self._stop_typing:
                break
            
            if char == '\n':
                print()
                continue
            else:
                if USE_COLORS and color:
                    sys.stdout.write(f"{color}{char}{Colors.END}")
                else:
                    sys.stdout.write(char)
                sys.stdout.flush()
            
            if self.min_delay == 0 and self.max_delay == 0:
                delay = 0
            else:
                delay = random.randint(self.min_delay, self.max_delay) / 1000.0
            
            if char in pause_chars and pause_between_chars:
                delay *= self.punctuation_delay
            
            if random.random() < 0.02:
                delay += random.randint(50, 150) / 1000.0
            
            time.sleep(delay)
        
        if newline:
            print()
    
    def type_line(self, text, color=Colors.GREEN):
        self.type_text(text, color, newline=True)
    
    def type_block(self, lines, color=Colors.GREEN, delay_between_lines=0.3):
        for line in lines:
            self.type_line(line, color)
            if delay_between_lines > 0:
                time.sleep(delay_between_lines)
    
    def type_animated(self, text, color=Colors.GREEN, duration=0.5):
        if not self.typing_enabled:
            print(f"{text}")
            return
        
        cursor_chars = ['|', '/', '-', '\\\\']
        cursor_idx = 0
        
        display_text = text if USE_COLORS else strip_ansi(text)
        
        for i in range(len(display_text) + 1):
            if self._stop_typing:
                break
            
            sys.stdout.write('\r')
            if USE_COLORS and color:
                sys.stdout.write(f"{color}{display_text[:i]}{Colors.DIM}{cursor_chars[cursor_idx % len(cursor_chars)]}{Colors.END}")
            else:
                sys.stdout.write(f"{display_text[:i]}{cursor_chars[cursor_idx % len(cursor_chars)]}")
            sys.stdout.flush()
            
            cursor_idx += 1
            time.sleep(duration / (len(display_text) + 1))
        
        sys.stdout.write('\r')
        if USE_COLORS and color:
            sys.stdout.write(f"{color}{display_text}{Colors.END}")
        else:
            sys.stdout.write(display_text)
        sys.stdout.flush()
        print()
    
    def stop_typing(self):
        self._stop_typing = True
    
    def reset(self):
        self._stop_typing = False
class MatrixRain:
    """Cinematic matrix rain effect"""
    
    def __init__(self, width=60, height=10):
        self.width = width
        self.height = height
        self.chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self.typer = TypeWriter('fast')
        
    def render_frame(self, duration=0.1, with_typing=True):
        frame = []
        for i in range(self.height):
            line = ''
            for j in range(self.width):
                if random.random() > 0.7:
                    char = random.choice(self.chars)
                    line += f"{Colors.GREEN}{char}{Colors.END}"
                else:
                    line += ' '
            frame.append(line)
        
        try:
            sys.stdout.write('\033[{}A'.format(self.height))
            sys.stdout.flush()
        except:
            pass
        
        if with_typing and self.typer.typing_enabled:
            for line in frame:
                self.typer.type_text(line, color=Colors.GREEN, newline=True, pause_between_chars=False)
        else:
            for line in frame:
                print(line)
        time.sleep(duration)

# Cross-platform paths
class Paths:
    """Cross-platform file paths for different operating systems"""
    
    @staticmethod
    def get_config_dir():
        system = platform.system()
        if system == 'Windows':
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = os.path.join(base_dir, 'DSTerminal')
        elif system == 'Darwin':
            base_dir = os.path.expanduser('~/Library/Application Support')
            config_dir = os.path.join(base_dir, 'DSTerminal')
        else:
            base_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            config_dir = os.path.join(base_dir, 'dsterminal')
        return config_dir
    
    @staticmethod
    def get_data_dir():
        system = platform.system()
        if system == 'Windows':
            base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            data_dir = os.path.join(base_dir, 'DSTerminal', 'Data')
        elif system == 'Darwin':
            base_dir = os.path.expanduser('~/Library/Application Support')
            data_dir = os.path.join(base_dir, 'DSTerminal', 'Data')
        else:
            base_dir = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
            data_dir = os.path.join(base_dir, 'dsterminal')
        return data_dir
    
    @staticmethod
    def get_workspace_dir():
        """Get the workspace directory (current working directory)"""
        return os.getcwd()
    
    @staticmethod
    def get_key_file():
        return os.path.join(Paths.get_config_dir(), 'dsterminal_key')
    
    @staticmethod
    def get_qr_dir():
        return os.path.join(Paths.get_data_dir(), 'qr_codes')
    
    @staticmethod
    def get_backup_dir():
        return os.path.join(Paths.get_data_dir(), 'backups')
    
    @staticmethod
    def get_encrypted_dir():
        return os.path.join(Paths.get_data_dir(), 'encrypted_dirs')
    
    @staticmethod
    def get_reports_dir():
        """Get reports directory in the workspace"""
        workspace = Paths.get_workspace_dir()
        reports_dir = os.path.join(workspace, 'dsterminal_workspace', 'reports', 'encryption_reports')
        return reports_dir
    
KEY_FILE = Paths.get_key_file()
QR_CODE_DIR = Paths.get_qr_dir()
BACKUP_DIR = Paths.get_backup_dir()
ENCRYPTED_DIR = Paths.get_encrypted_dir()
REPORTS_DIR = Paths.get_reports_dir()

# Create reports directory
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR, mode=0o700, exist_ok=True)

class ReportGenerator:
    """Generate PDF and HTML reports for encryption/decryption operations"""
    
    VERSION = "v3.1.113"
    WATERMARK = f"DSTERMINAL {VERSION}"
    FOOTER = "Stark Expo Tech Exchange | Encrypt with Caution"
    
    def __init__(self):
        self.typer = TypeWriter('fast')
        self.reports_dir = REPORTS_DIR  # This will now use the new path
        
        # Ensure reports directory exists
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir, mode=0o700, exist_ok=True)
    
    def generate_test_report(self, operation_type, details):
        """Generate test report with special formatting"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"dsterminal_test_report_{timestamp}"
        
        pdf_path = os.path.join(self.reports_dir, f"{base_filename}.pdf")
        html_path = os.path.join(self.reports_dir, f"{base_filename}.html")
        
        # Generate PDF test report
        if REPORT_AVAILABLE:
            try:
                self._generate_pdf(pdf_path, f"TEST: {operation_type}", details)
                self.typer.type_text(f"📄 Test Report (PDF): {pdf_path}", color=Colors.CYAN)
            except Exception as e:
                self.typer.type_text(f"⚠️ PDF generation failed: {e}", color=Colors.YELLOW)
        
        # Generate HTML test report
        try:
            self._generate_html(html_path, f"TEST: {operation_type}", details)
            self.typer.type_text(f"🌐 Test Report (HTML): {html_path}", color=Colors.CYAN)
        except Exception as e:
            self.typer.type_text(f"⚠️ HTML generation failed: {e}", color=Colors.YELLOW)
        
        return {'pdf': pdf_path if os.path.exists(pdf_path) else None, 
                'html': html_path if os.path.exists(html_path) else None}

    def generate_report(self, operation_type, details):
        """Generate both PDF and HTML reports"""
        if details.get('test_mode', False):
            return self.generate_test_report(operation_type, details)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"dsterminal_report_{timestamp}"
        
        pdf_path = os.path.join(self.reports_dir, f"{base_filename}.pdf")
        html_path = os.path.join(self.reports_dir, f"{base_filename}.html")
        
        # Generate PDF
        if REPORT_AVAILABLE:
            try:
                self._generate_pdf(pdf_path, operation_type, details)
                self.typer.type_text(f"📄 PDF Report: {pdf_path}", color=Colors.CYAN)
            except Exception as e:
                self.typer.type_text(f"⚠️ PDF generation failed: {e}", color=Colors.YELLOW)
        else:
            self.typer.type_text("⚠️ PDF generation unavailable (install reportlab)", color=Colors.YELLOW)
        
        # Generate HTML
        try:
            self._generate_html(html_path, operation_type, details)
            self.typer.type_text(f"🌐 HTML Report: {html_path}", color=Colors.CYAN)
        except Exception as e:
            self.typer.type_text(f"⚠️ HTML generation failed: {e}", color=Colors.YELLOW)
        
        return {'pdf': pdf_path if os.path.exists(pdf_path) else None, 
                'html': html_path if os.path.exists(html_path) else None}

    def _generate_pdf(self, filepath, operation_type, details):
        """Generate PDF report"""
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00ff00'),
            alignment=1,  # Center
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#00ccff'),
            spaceAfter=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        warning_style = ParagraphStyle(
            'Warning',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#ff0000'),
            spaceAfter=6
        )
        
        story = []
        
        # Title
        story.append(Paragraph(f"DSTERMINAL {self.VERSION}", title_style))
        story.append(Paragraph("Encryption Report", title_style))
        story.append(Spacer(1, 12))
        
        # Watermark
        story.append(Paragraph(f"<font color='#666666' size='8'>Document ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}</font>", body_style))
        story.append(Spacer(1, 12))
        
        # Report Info
        story.append(Paragraph("REPORT INFORMATION", heading_style))
        story.append(Paragraph(f"Operation Type: <b>{operation_type}</b>", body_style))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
        story.append(Paragraph(f"System: {platform.system()} {platform.release()}", body_style))
        story.append(Spacer(1, 12))
        
        # Key Information
        story.append(Paragraph("ENCRYPTION KEY INFORMATION", heading_style))
        key_info = details.get('key_info', {})
        story.append(Paragraph(f"Key ID: {key_info.get('key_id', 'N/A')}", body_style))
        story.append(Paragraph(f"Key Location: {key_info.get('key_location', 'N/A')}", body_style))
        story.append(Paragraph(f"Key Format: Fernet (AES-256)", body_style))
        
        # Show partial key for verification
        full_key = key_info.get('full_key', '')
        if full_key:
            masked_key = full_key[:20] + "..." + full_key[-10:]
            story.append(Paragraph(f"Key (masked): {masked_key}", body_style))
        story.append(Spacer(1, 12))
        
        # Operation Details
        story.append(Paragraph("OPERATION DETAILS", heading_style))
        story.append(Paragraph(f"Target: {details.get('target', 'N/A')}", body_style))
        story.append(Paragraph(f"Total Files: {details.get('total_files', 0)}", body_style))
        story.append(Paragraph(f"Total Size: {details.get('total_size', 'N/A')}", body_style))
        story.append(Spacer(1, 12))
        
        # File List
        files = details.get('files', [])
        if files:
            story.append(Paragraph("FILES PROCESSED", heading_style))
            # Create table
            data = [['#', 'Filename', 'Status', 'Size']]
            for idx, f in enumerate(files[:50], 1):  # Limit to 50 files for PDF
                data.append([str(idx), f.get('name', 'Unknown'), 
                            f.get('status', 'Processed'), 
                            f.get('size', 'N/A')])
            if len(files) > 50:
                data.append(['...', f'... and {len(files)-50} more files', '', ''])
            
            table = Table(data, colWidths=[0.5*inch, 3*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003300')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00ff00')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666666')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("RECOMMENDATIONS", heading_style))
        story.append(Paragraph("• Always keep your encryption key in a secure location", body_style))
        story.append(Paragraph("• Create multiple backups of your encryption key", body_style))
        story.append(Paragraph("• Use the QR code export feature for secure key sharing", body_style))
        story.append(Paragraph("• Regularly verify your encrypted data integrity", body_style))
        story.append(Paragraph("• Store encrypted containers in a safe location", body_style))
        story.append(Spacer(1, 12))
        
        # Warning
        story.append(Paragraph("<b><font color='red'>⚠️ ENCRYPT WITH CAUTION</font></b>", warning_style))
        story.append(Paragraph("<font color='red'>• Losing your encryption key means losing your data permanently</font>", warning_style))
        story.append(Paragraph("<font color='red'>• Always test decryption before deleting original files</font>", warning_style))
        story.append(Paragraph("<font color='red'>• Use strong passwords and secure storage for your keys</font>", warning_style))
        story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 36))
        story.append(Paragraph(f"<font color='#666666' size='8'>{self.WATERMARK}</font>", body_style))
        story.append(Paragraph(f"<font color='#666666' size='8'>{self.FOOTER}</font>", body_style))
        story.append(Paragraph(f"<font color='#666666' size='8'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>", body_style))
        
        doc.build(story)
    
    def _generate_html(self, filepath, operation_type, details):
        """Generate HTML report"""
        key_info = details.get('key_info', {})
        full_key = key_info.get('full_key', '')
        masked_key = full_key[:20] + "..." + full_key[-10:] if full_key else 'N/A'
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSTERMINAL Encryption Report</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            margin: 40px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #111;
            padding: 30px;
            border: 1px solid #00ff00;
            border-radius: 10px;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #00ff00;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 28px;
            font-weight: bold;
            color: #00ff00;
            text-shadow: 0 0 20px rgba(0,255,0,0.3);
        }}
        .subtitle {{
            color: #00ccff;
            font-size: 18px;
        }}
        .watermark {{
            color: #333;
            font-size: 12px;
            text-align: right;
        }}
        .section {{
            margin: 25px 0;
            padding: 15px;
            background: #1a1a1a;
            border-left: 3px solid #00ccff;
            border-radius: 5px;
        }}
        .section-title {{
            color: #00ccff;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .info-row {{
            display: flex;
            padding: 5px 0;
            border-bottom: 1px solid #222;
        }}
        .info-label {{
            color: #888;
            width: 200px;
            font-weight: bold;
        }}
        .info-value {{
            color: #00ff00;
            flex: 1;
        }}
        .file-list {{
            background: #0a0a0a;
            padding: 10px;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .file-item {{
            padding: 3px 10px;
            border-bottom: 1px solid #1a1a1a;
            font-size: 12px;
            color: #aaa;
        }}
        .file-item .status {{
            color: #00ff00;
            float: right;
        }}
        .warning {{
            background: #1a0000;
            border: 1px solid #ff0000;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .warning-title {{
            color: #ff0000;
            font-weight: bold;
            font-size: 16px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333;
            text-align: center;
            color: #666;
            font-size: 11px;
        }}
        .recommendation {{
            color: #aaa;
            padding: 5px 0;
            padding-left: 20px;
        }}
        .recommendation:before {{
            content: "▸ ";
            color: #00ccff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">DSTERMINAL {self.VERSION}</div>
            <div class="subtitle">Encryption Report</div>
            <div class="watermark">Document ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}</div>
        </div>
        
        <div class="section">
            <div class="section-title">📋 REPORT INFORMATION</div>
            <div class="info-row">
                <span class="info-label">Operation:</span>
                <span class="info-value">{operation_type}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Date/Time:</span>
                <span class="info-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">System:</span>
                <span class="info-value">{platform.system()} {platform.release()}</span>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">🔑 ENCRYPTION KEY INFORMATION</div>
            <div class="info-row">
                <span class="info-label">Key ID:</span>
                <span class="info-value">{key_info.get('key_id', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Key Location:</span>
                <span class="info-value">{key_info.get('key_location', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Key Format:</span>
                <span class="info-value">Fernet (AES-256)</span>
            </div>
            <div class="info-row">
                <span class="info-label">Key (masked):</span>
                <span class="info-value" style="color:#ffcc00;font-size:11px;">{masked_key}</span>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📁 OPERATION DETAILS</div>
            <div class="info-row">
                <span class="info-label">Target:</span>
                <span class="info-value">{details.get('target', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Total Files:</span>
                <span class="info-value">{details.get('total_files', 0)}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Total Size:</span>
                <span class="info-value">{details.get('total_size', 'N/A')}</span>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📄 FILES PROCESSED</div>
            <div class="file-list">
                {''.join([f'<div class="file-item">📎 {f.get("name", "Unknown")} <span class="status">{f.get("status", "Processed")}</span></div>' for f in details.get('files', [])[:100]])}
                {f'<div class="file-item" style="color:#666;">... and {len(details.get("files", []))-100} more files</div>' if len(details.get('files', [])) > 100 else ''}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">💡 RECOMMENDATIONS</div>
            <div class="recommendation">Always keep your encryption key in a secure location</div>
            <div class="recommendation">Create multiple backups of your encryption key</div>
            <div class="recommendation">Use the QR code export feature for secure key sharing</div>
            <div class="recommendation">Regularly verify your encrypted data integrity</div>
            <div class="recommendation">Store encrypted containers in a safe location</div>
        </div>
        
        <div class="warning">
            <div class="warning-title">⚠️ ENCRYPT WITH CAUTION</div>
            <div style="color:#ff6666;padding:5px 0;">• Losing your encryption key means losing your data permanently</div>
            <div style="color:#ff6666;padding:5px 0;">• Always test decryption before deleting original files</div>
            <div style="color:#ff6666;padding:5px 0;">• Use strong passwords and secure storage for your keys</div>
        </div>
        
        <div class="footer">
            <div>DSTERMINAL {self.VERSION}</div>
            <div>{self.FOOTER}</div>
            <div style="font-size:9px;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

class PlatformUtils:
    """Cross-platform utility functions"""
    
    @staticmethod
    def clear_screen():
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
    
    @staticmethod
    def get_terminal_size():
        try:
            return shutil.get_terminal_size((80, 24))
        except:
            return (80, 24)
    
    @staticmethod
    def copy_to_clipboard(text):
        try:
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['clip'], input=text.encode('utf-8'), check=True, shell=True)
                return True
            elif system == 'Darwin':
                subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
                return True
            else:
                try:
                    subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
                    return True
                except:
                    try:
                        subprocess.run(['xsel', '-b'], input=text.encode('utf-8'), check=True)
                        return True
                    except:
                        try:
                            import pyperclip
                            pyperclip.copy(text)
                            return True
                        except:
                            return False
        except:
            return False
    
    @staticmethod
    def get_platform_info():
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'is_windows': platform.system() == 'Windows',
            'is_mac': platform.system() == 'Darwin',
            'is_linux': platform.system() == 'Linux'
        }
    
    @staticmethod
    def create_directories():
        dirs = [KEY_FILE, QR_CODE_DIR, BACKUP_DIR, ENCRYPTED_DIR, REPORTS_DIR]
        for d in dirs:
            dir_path = os.path.dirname(d)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, mode=0o700, exist_ok=True)
        for d in [QR_CODE_DIR, BACKUP_DIR, ENCRYPTED_DIR, REPORTS_DIR]:
            if not os.path.exists(d):
                os.makedirs(d, mode=0o700, exist_ok=True)
        
        # Ensure workspace reports directory exists
        workspace_reports = os.path.join(os.getcwd(), 'dsterminal_workspace', 'reports', 'encryption_reports')
        if not os.path.exists(workspace_reports):
            os.makedirs(workspace_reports, mode=0o700, exist_ok=True)
            

class HackerDashboard:
    """Hacker-style dashboard with multi-panel layout and typing effects"""
    
    def __init__(self):
        self.term_width = PlatformUtils.get_terminal_size().columns
        self.term_height = PlatformUtils.get_terminal_size().lines
        self.left_panel = []
        self.right_panel = []
        self.stats = {}
        self.animations = []
        self.matrix_rain = MatrixRain(20, 5)
        self.typer = TypeWriter('fast')
        
        # Panel configuration - 50/50 split
        self.panel_ratios = {
            'left': 0.50,
            'right': 0.50
        }
        self.max_panel_width = 35
        self.max_panel_height = 18
        
    def set_stats(self, stats):
        self.stats = stats
    
    def add_animation(self, animation_func):
        self.animations.append(animation_func)
    
    def draw_border(self, width, char='─', style='single'):
        if style == 'single':
            return f"┌{char * (width-2)}┐"
        elif style == 'double':
            return f"╔{char * (width-2)}╗"
        elif style == 'rounded':
            return f"╭{char * (width-2)}╮"
        return f"┌{char * (width-2)}┐"
    
    def draw_panel(self, title, content, width, color=Colors.CYAN, border_style='single'):
        if width < 10:
            width = 10
        
        # Ensure content is a list
        if content is None:
            content = []
        
        lines = []
        if border_style == 'single':
            lines.append(f"{color}┌{'─' * (width-2)}┐{Colors.END}")
        elif border_style == 'double':
            lines.append(f"{color}╔{'═' * (width-2)}╗{Colors.END}")
        elif border_style == 'rounded':
            lines.append(f"{color}╭{'─' * (width-2)}╮{Colors.END}")
        
        # Title - centered
        title_line = f"{color}│{Colors.END}{Colors.BOLD}{title.center(width-2)}{Colors.END}{color}│{Colors.END}"
        lines.append(title_line)
        
        if border_style == 'single':
            lines.append(f"{color}├{'─' * (width-2)}┤{Colors.END}")
        elif border_style == 'double':
            lines.append(f"{color}╟{'─' * (width-2)}╢{Colors.END}")
        elif border_style == 'rounded':
            lines.append(f"{color}├{'─' * (width-2)}┤{Colors.END}")
        
        # Content - LEFT ALIGNED
        for item in content:
            if item is None:
                item = ""
            if len(item) > width - 4:
                for i in range(0, len(item), width - 4):
                    chunk = item[i:i + width - 4]
                    lines.append(f"{color}│{Colors.END} {chunk.ljust(width-4)} {color}│{Colors.END}")
            else:
                lines.append(f"{color}│{Colors.END} {item.ljust(width-4)} {color}│{Colors.END}")
        
        if border_style == 'single':
            lines.append(f"{color}└{'─' * (width-2)}┘{Colors.END}")
        elif border_style == 'double':
            lines.append(f"{color}╚{'═' * (width-2)}╝{Colors.END}")
        elif border_style == 'rounded':
            lines.append(f"{color}╰{'─' * (width-2)}╯{Colors.END}")
        
        return lines
    
    def render_dashboard(self, with_typing=True, panel_ratios=None):
        """Render dashboard with left-aligned panels and triple spacing"""
        PlatformUtils.clear_screen()
        
        if panel_ratios is None:
            panel_ratios = self.panel_ratios
        
        self.term_width = PlatformUtils.get_terminal_size().columns
        self.term_height = PlatformUtils.get_terminal_size().lines
        
        # Triple spacing between panels (6 spaces)
        spacing = 100
        min_panel_width = 50
        max_panel_width = self.max_panel_width
        max_panel_height = self.max_panel_height  # Use class variable
        
        # Calculate widths
        available_width = self.term_width - spacing
        left_width = min(int(available_width * panel_ratios['left']), max_panel_width)
        right_width = min(available_width - left_width, max_panel_width)
        
        # Ensure minimum widths
        if left_width < min_panel_width:
            left_width = min_panel_width
        if right_width < min_panel_width:
            right_width = min_panel_width
        
        # Prepare content - ensure they return lists
        left_content = self.prepare_left_panel()
        right_content = self.prepare_right_panel()
        
        # Ensure content is a list
        if left_content is None:
            left_content = []
        if right_content is None:
            right_content = []
        
        # Limit content to max height
        if len(left_content) > max_panel_height:
            left_content = left_content[:max_panel_height]
        if len(right_content) > max_panel_height:
            right_content = right_content[:max_panel_height]
        
        # Draw panels
        left_panel = self.draw_panel(" 🔐 SYSTEM STATUS ", left_content, left_width, Colors.GREEN, 'single')
        right_panel = self.draw_panel(" 📊 LIVE STATS ", right_content, right_width, Colors.MAGENTA, 'rounded')
        
        max_height = max(len(left_panel), len(right_panel))
        left_panel += [''] * (max_height - len(left_panel))
        right_panel += [''] * (max_height - len(right_panel))
        
        self.print_header(with_typing)
        
        # Print panels with triple spacing
        for i in range(max_height):
            left_line = left_panel[i] if i < len(left_panel) else ''
            right_line = right_panel[i] if i < len(right_panel) else ''
            
            left_line = left_line.ljust(left_width)
            right_line = right_line.ljust(right_width)
            
            # Triple spacing (6 spaces)
            print(f"{left_line}{' ' * spacing}{right_line}")
        
        self.print_footer(with_typing)
        
    def prepare_left_panel(self):
        """Prepare left panel content"""
        content = []
        
        if self.stats.get('encryption_ready', False):
            content.append(f"{Colors.GREEN}●{Colors.END} Encryption: {Colors.GREEN}ACTIVE{Colors.END}")
            content.append(f"  {Colors.DIM}Key: {self.stats.get('key_id', 'N/A')[:16]}...{Colors.END}")
        else:
            content.append(f"{Colors.RED}●{Colors.END} Encryption: {Colors.RED}INACTIVE{Colors.END}")
        
        content.append(f"{Colors.CYAN}▶{Colors.END} Encrypted Files: {self.stats.get('encrypted_count', 0)}")
        content.append(f"{Colors.YELLOW}▶{Colors.END} QR Codes: {self.stats.get('qr_count', 0)}")
        content.append(f"{Colors.MAGENTA}▶{Colors.END} Encrypted Dirs: {self.stats.get('encrypted_dirs', 0)}")
        
        content.append(f"{Colors.DIM}▶{Colors.END} Platform: {platform.system()}")
        content.append(f"{Colors.DIM}▶{Colors.END} Term: {self.term_width}x{self.term_height}")
        
        if self.stats.get('key_exists', False):
            content.append(f"{Colors.GREEN}✓{Colors.END} Key Found: {self.stats.get('key_location', 'N/A')}")
        else:
            content.append(f"{Colors.RED}✗{Colors.END} Key Missing")
        
        if QR_DEPS_AVAILABLE:
            content.append(f"{Colors.GREEN}✓{Colors.END} QR Module: {Colors.GREEN}READY{Colors.END}")
        else:
            content.append(f"{Colors.RED}✗{Colors.END} QR Module: {Colors.RED}MISSING{Colors.END}")
        
        if REPORT_AVAILABLE:
            content.append(f"{Colors.GREEN}✓{Colors.END} Reports: {Colors.GREEN}ENABLED{Colors.END}")
        else:
            content.append(f"{Colors.YELLOW}⚠{Colors.END} Reports: {Colors.YELLOW}DISABLED{Colors.END}")
        
        return content
    
    def prepare_right_panel(self):
        """Prepare right panel content"""
        content = []
        
        # Combine stats and commands in right panel
        content.append(f"  {Colors.CYAN}▶{Colors.END} Uptime: {self.stats.get('uptime', '00:00:00')}")
        content.append(f"  {Colors.CYAN}▶{Colors.END} Reports: {self.stats.get('reports_count', 0)}")
        content.append("")
        content.append(f"{Colors.BOLD}{Colors.YELLOW}RECENT ACTIVITY{Colors.END}")
        
        recent_activity = self.stats.get('recent_activity', ['No activity'])
        for activity in recent_activity:
            content.append(f"  {Colors.DIM}•{Colors.END} {activity}")
        
        content.append("")
        # content.append(f"{Colors.BOLD}{Colors.CYAN}COMMANDS{Colors.END}")
        # content.append(f"{Colors.GREEN}  [01] Setup System      [02] Encrypt File{Colors.END}")
        # content.append(f"{Colors.GREEN}  [03] Decrypt File      [04] Encrypt Dir{Colors.END}")
        # content.append(f"{Colors.GREEN}  [05] Decrypt Dir       [06] Backup Key{Colors.END}")
        # content.append(f"{Colors.CYAN}  [07] QR Generate       [08] Export Key{Colors.END}")
        # content.append(f"{Colors.CYAN}  [09] Import Key        [10] List Files{Colors.END}")
        # content.append(f"{Colors.CYAN}  [11] File Info         [12] Verify System{Colors.END}")
        # content.append(f"{Colors.MAGENTA}  [13] Reports           [14] QR Import{Colors.END}")
        # content.append(f"{Colors.MAGENTA}  [15] QR Restore        [16] QR List{Colors.END}")
        # content.append(f"{Colors.MAGENTA}  [17] Clean QR          [18] Encrypted Dirs{Colors.END}")
        # content.append(f"{Colors.YELLOW}  [19] Debug Info        [20] Encrypt Test{Colors.END}")
        # content.append(f"{Colors.YELLOW}  [21] Decrypt Test      [00] Exit{Colors.END}")
        
        return content
    
    def print_header(self, with_typing=True):
        """Print the header with banner"""
        # Centered ASCII banner
        banner_lines = [
            f"{Colors.GREEN}{Colors.BOLD}",
            "╔═══════════════════════════════════════════════════════════════════════════╗",
            "║  ██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗        ║",
            "║  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║        ║",
            "║  ██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║        ║",
            "║  ██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║        ║",
            "║  ██████╔╝███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗   ║",
            "║  ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝   ║",
            "╚═══════════════════════════════════════════════════════════════════════════╝",
            f"{Colors.END}"
        ]
        
        # Center the banner
        for line in banner_lines:
            if line.startswith(Colors.GREEN):
                clean_line = line.replace(Colors.GREEN, '').replace(Colors.BOLD, '').replace(Colors.END, '')
                if clean_line:
                    padding = max(0, (self.term_width - len(clean_line)) // 2)
                    print(' ' * padding + line)
                else:
                    print(line)
            else:
                print(line)
        
        qr_status = f"{Colors.GREEN}READY{Colors.END}" if QR_DEPS_AVAILABLE else f"{Colors.RED}NOT AVAILABLE{Colors.END}"
        report_status = f"{Colors.GREEN}ENABLED{Colors.END}" if REPORT_AVAILABLE else f"{Colors.RED}DISABLED{Colors.END}"
        status = f"{Colors.DIM}SYSTEM: {platform.system()} {platform.release()} | ENCRYPTION MODE STATUS: {Colors.GREEN}ACTIVE{Colors.DIM} | QR: {qr_status}{Colors.DIM} | REPORTS: {report_status}{Colors.DIM} | TERMINAL: {self.term_width}x{self.term_height}{Colors.END}"
        status_line = status.center(self.term_width)
        separator = f"{Colors.DIM}{'═' * self.term_width}{Colors.END}"
        
        if with_typing:
            self.typer.type_text(status_line, color=Colors.DIM, newline=True, pause_between_chars=False)
            self.typer.type_text(separator, color=Colors.DIM, newline=True, pause_between_chars=False)
        else:
            print(status_line)
            print(separator)
    
    def print_footer(self, with_typing=True):
        """Print the footer"""
        footer_lines = [
            f"{Colors.DIM}{'═' * self.term_width}{Colors.END}",
            f"{Colors.YELLOW}[00] EXIT  {Colors.CYAN}[01-21] COMMANDS  {Colors.MAGENTA}[Ctrl+C] ENCRYPTION TERMINATION{Colors.END}",
            f"{Colors.DIM}└── DSTERMINAL v3.1.113 ── ENHANCED ENCRYPTION EDITION ── ENCRYPT WITH CAUTION ──{Colors.END}"
        ]
        
        if with_typing:
            for line in footer_lines:
                self.typer.type_text(line, color=Colors.DIM, newline=True, pause_between_chars=False)
        else:
            for line in footer_lines:
                print(line)

class RotatingBox:
    """Animated rotating box with content and typing effects"""
    
    def __init__(self, width=40, title=""):
        self.width = min(width, shutil.get_terminal_size((80, 20)).columns - 4)
        self.title = title
        self.frames = 0
        self.typer = TypeWriter('fast')
        
    def render(self, content_lines, color=Colors.CYAN, with_typing=True):
        max_line_len = max([len(line.replace(Colors.END, '').replace(Colors.BOLD, '')) for line in content_lines] + [0])
        self.width = max(self.width, max_line_len + 4)
        self.width = min(self.width, shutil.get_terminal_size((80, 20)).columns - 4)
        
        lines = []
        
        if self.frames % 8 < 4:
            border_char = '─'
            corner_char = '┌'
            corner_end = '┐'
        else:
            border_char = '─'
            corner_char = '╭'
            corner_end = '╮'
        
        lines.append(f"{color}{corner_char}{border_char}{self.title.center(self.width-4, border_char)}{border_char}{corner_end}{Colors.END}")
        
        for line in content_lines:
            padding = self.width - len(line.replace(Colors.END, '').replace(Colors.BOLD, '')) - 2
            if padding < 0:
                padding = 0
            lines.append(f"{color}│{Colors.END} {line.ljust(self.width-2)} {color}│{Colors.END}")
        
        if self.frames % 8 < 4:
            border_char = '─'
            corner_char = '└'
            corner_end = '┘'
        else:
            border_char = '─'
            corner_char = '╰'
            corner_end = '╯'
        
        lines.append(f"{color}{corner_char}{border_char * (self.width-2)}{corner_end}{Colors.END}")
        
        if with_typing and self.typer.typing_enabled:
            for line in lines:
                self.typer.type_text(line, newline=True, pause_between_chars=False)
        else:
            for line in lines:
                print(line)
        
        self.frames += 1

class AnimatedTable:
    """Animated table with rotating columns and typing effects"""
    
    def __init__(self, headers):
        self.headers = headers
        self.rotation = 0
        self.typer = TypeWriter('fast')
        
    def render(self, rows, color=Colors.YELLOW, with_typing=True):
        col_widths = [len(h) for h in self.headers]
        for row in rows:
            for i, cell in enumerate(row):
                clean_cell = str(cell).replace(Colors.END, '').replace(Colors.BOLD, '')
                col_widths[i] = max(col_widths[i], len(clean_cell))
        
        total_width = sum(col_widths) + len(self.headers) * 3 - 1
        max_width = shutil.get_terminal_size((80, 20)).columns - 4
        
        if total_width > max_width:
            scale = (max_width - len(self.headers) * 3) / sum(col_widths)
            col_widths = [max(3, int(w * scale)) for w in col_widths]
            total_width = sum(col_widths) + len(self.headers) * 3 - 1
        
        if self.rotation % 2 == 0:
            separator = f"{color}├{'─┼─'.join(['─' * w for w in col_widths])}┤{Colors.END}"
        else:
            separator = f"{color}╞{'═╪═'.join(['═' * w for w in col_widths])}╡{Colors.END}"
        
        header_line = ''
        for i, h in enumerate(self.headers):
            header_line += f" {h.center(col_widths[i])} "
            if i < len(self.headers)-1:
                header_line += f"{color}│{Colors.END}"
        
        lines = [
            f"{color}┌{'─' * (sum(col_widths) + len(self.headers)*3 - 1)}┐{Colors.END}",
            f"{color}│{Colors.END}{header_line}{color}│{Colors.END}",
            separator
        ]
        
        for row in rows:
            row_line = ''
            for i, cell in enumerate(row):
                clean_cell = str(cell).replace(Colors.END, '').replace(Colors.BOLD, '')
                row_line += f" {str(cell).ljust(col_widths[i])} "
                if i < len(row)-1:
                    row_line += f"{color}│{Colors.END}"
            lines.append(f"{color}│{Colors.END}{row_line}{color}│{Colors.END}")
        
        lines.append(f"{color}└{'─' * (sum(col_widths) + len(self.headers)*3 - 1)}┘{Colors.END}")
        
        if with_typing and self.typer.typing_enabled:
            for line in lines:
                self.typer.type_text(line, newline=True, pause_between_chars=False)
        else:
            for line in lines:
                print(line)
        
        self.rotation += 1

class QRCodeManager:
    """QR Code management for encryption keys - using OpenCV for detection"""
    
    def __init__(self, crypto_engine):
        self.crypto = crypto_engine
        self.qr_dir = QR_CODE_DIR
        self.available = QR_DEPS_AVAILABLE
        self.method = QR_METHOD
        self.typer = TypeWriter('fast')
        
        if not os.path.exists(self.qr_dir):
            os.makedirs(self.qr_dir, mode=0o700, exist_ok=True)
        
        if not self.available:
            self.typer.type_text("⚠️ QR Code features are disabled. Missing dependencies.", color=Colors.YELLOW)
            self.typer.type_text("💡 Install: pip install qrcode[pil] pillow opencv-python-headless", color=Colors.CYAN)
    
    def generate_qr_code(self, key_data=None, filename=None):
        """Generate QR code from encryption key"""
        if not self.available:
            self.typer.type_text("❌ QR Code feature unavailable. Missing dependencies.", color=Colors.RED)
            self.typer.type_text("💡 Install: pip install qrcode[pil] pillow opencv-python-headless", color=Colors.CYAN)
            return None
            
        if key_data is None:
            if not os.path.exists(KEY_FILE):
                self.typer.type_text("❌ No encryption key found", color=Colors.RED)
                self.typer.type_text("Run 'Setup Encryption System' first.", color=Colors.YELLOW)
                return None
            
            with open(KEY_FILE, "r") as f:
                key_data = f.read().strip()
        
        try:
            self.typer.type_text("📱 Generating QR code...", color=Colors.YELLOW)
            time.sleep(0.5)
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=5,
                border=2,
            )
            qr.add_data(key_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"dsterminal_key_{timestamp}.png"
            
            if not os.path.exists(self.qr_dir):
                os.makedirs(self.qr_dir, mode=0o700, exist_ok=True)
            
            filepath = os.path.join(self.qr_dir, filename)
            img.save(filepath)
            
            ascii_qr = self._generate_ascii_qr(qr)
            
            self.typer.type_text("✅ QR code generated successfully!", color=Colors.GREEN)
            
            return {
                'filepath': filepath,
                'image': img,
                'ascii': ascii_qr,
                'key_id': hashlib.sha256(key_data.encode()).hexdigest()[:16]
            }
        except Exception as e:
            self.typer.type_text(f"❌ Failed to generate QR code: {str(e)}", color=Colors.RED)
            return None
    
    def _generate_ascii_qr(self, qr):
        """Generate ASCII representation of QR code"""
        matrix = qr.modules
        size = len(matrix)
        
        ascii_lines = []
        ascii_lines.append("┌" + "─" * (size * 2 + 2) + "┐")
        
        for row in matrix:
            line = "│ "
            for cell in row:
                line += "██" if cell else "  "
            line += " │"
            ascii_lines.append(line)
        
        ascii_lines.append("└" + "─" * (size * 2 + 2) + "┘")
        
        return "\n".join(ascii_lines)
    
    def scan_qr_code(self, image_path=None):
        """Scan QR code from image file using OpenCV"""
        if not self.available:
            self.typer.type_text("❌ QR Code scanning unavailable. Missing dependencies.", color=Colors.RED)
            self.typer.type_text("💡 Install: pip install opencv-python-headless pillow", color=Colors.CYAN)
            return None
            
        if image_path is None:
            if os.path.exists(self.qr_dir):
                qr_files = [f for f in os.listdir(self.qr_dir) if f.endswith('.png')]
                if qr_files:
                    qr_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.qr_dir, x)), reverse=True)
                    image_path = os.path.join(self.qr_dir, qr_files[0])
                    self.typer.type_text(f"📷 Using most recent QR code: {qr_files[0]}", color=Colors.CYAN)
                else:
                    self.typer.type_text(f"❌ No QR code images found in {self.qr_dir}", color=Colors.RED)
                    return None
            else:
                self.typer.type_text(f"❌ QR code directory not found", color=Colors.RED)
                return None
        
        if not os.path.exists(image_path):
            self.typer.type_text(f"❌ QR code image not found: {image_path}", color=Colors.RED)
            return None
        
        try:
            self.typer.type_text("🔍 Scanning QR code with OpenCV...", color=Colors.YELLOW)
            time.sleep(0.5)
            
            img = cv2.imread(image_path)
            if img is None:
                self.typer.type_text("❌ Failed to read image", color=Colors.RED)
                return None
            
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            
            if not data:
                self.typer.type_text("❌ No QR code found in image", color=Colors.RED)
                return None
            
            qr_data = data.strip()
            self.typer.type_text(f"📊 QR data length: {len(qr_data)} characters", color=Colors.DIM)
            
            try:
                test_cipher = Fernet(qr_data.encode())
                test_data = b"DSTerminal_qr_test"
                encrypted = test_cipher.encrypt(test_data)
                decrypted = test_cipher.decrypt(encrypted)
                
                if test_data == decrypted:
                    key_id = hashlib.sha256(qr_data.encode()).hexdigest()[:16]
                    self.typer.type_text("✅ QR code scanned successfully!", color=Colors.GREEN)
                    return {
                        'key': qr_data,
                        'key_id': key_id,
                        'source': image_path,
                        'valid': True
                    }
                else:
                    self.typer.type_text("❌ QR code data validation failed", color=Colors.RED)
                    return None
                    
            except Exception as e:
                self.typer.type_text(f"❌ Invalid key format in QR code: {str(e)}", color=Colors.RED)
                return None
                
        except Exception as e:
            self.typer.type_text(f"❌ Failed to scan QR code: {str(e)}", color=Colors.RED)
            return None
    
    def import_key_from_qr(self, image_path=None):
        """Import encryption key by scanning QR code"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " QR KEY IMPORT ")
        
        self.typer.type_text("🔍 Scanning QR code for encryption key...", color=Colors.YELLOW)
        
        for i in range(5):
            sys.stdout.write(f"\r{Colors.GREEN}[{'=' * i}{' ' * (4 - i)}] Scanning{'.' * (i % 3 + 1)}  {Colors.END}")
            sys.stdout.flush()
            time.sleep(0.3)
        print()
        
        result = self.scan_qr_code(image_path)
        
        if not result:
            content = [
                f"{Colors.RED}❌ QR SCAN FAILED{Colors.END}",
                "",
                f"{Colors.YELLOW}Could not extract a valid encryption key{Colors.END}",
                f"{Colors.CYAN}Make sure the QR code contains a valid Fernet key{Colors.END}"
            ]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return False
        
        self.typer.type_text(f"✅ QR Code scanned successfully!", color=Colors.GREEN)
        self.typer.type_text(f"Key ID: {result['key_id']}", color=Colors.CYAN)
        self.typer.type_text(f"Source: {result['source']}", color=Colors.CYAN)
        
        key_dir = os.path.dirname(KEY_FILE)
        if not os.path.exists(key_dir):
            os.makedirs(key_dir, mode=0o700, exist_ok=True)
            
        with open(KEY_FILE, "w") as f:
            f.write(result['key'])
        
        try:
            os.chmod(KEY_FILE, 0o600)
        except:
            pass
        
        self.crypto.cipher = Fernet(result['key'].encode())
        
        content = [
            f"{Colors.GREEN}✅ KEY IMPORTED SUCCESSFULLY{Colors.END}",
            f"{Colors.BOLD}Key ID:{Colors.END} {Colors.CYAN}{result['key_id']}{Colors.END}",
            f"{Colors.BOLD}Source:{Colors.END} {result['source']}",
            f"{Colors.BOLD}Location:{Colors.END} {KEY_FILE}",
            "",
            f"{Colors.GREEN}✓ Encryption system now uses the imported key{Colors.END}"
        ]
        box.render(content, color=Colors.GREEN, with_typing=True)
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        return True
    
    def export_key_as_qr(self):
        """Export encryption key as QR code"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " QR KEY EXPORT ")
        
        if not self.available:
            content = [
                f"{Colors.RED}❌ QR Code feature unavailable{Colors.END}",
                "",
                f"{Colors.YELLOW}Missing required dependencies:{Colors.END}",
                f"{Colors.CYAN}• qrcode[pil]{Colors.END}",
                f"{Colors.CYAN}• pillow{Colors.END}",
                f"{Colors.CYAN}• opencv-python-headless{Colors.END}",
                "",
                f"{Colors.CYAN}💡 Install with: pip install qrcode[pil] pillow opencv-python-headless{Colors.END}"
            ]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        if not os.path.exists(KEY_FILE):
            content = [
                f"{Colors.RED}❌ No encryption key found{Colors.END}",
                f"{Colors.YELLOW}Run 'Setup Encryption System' first.{Colors.END}"
            ]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        with open(KEY_FILE, "r") as f:
            key = f.read().strip()
        
        self.typer.type_text("📱 Generating QR code for your encryption key...", color=Colors.YELLOW)
        
        result = self.generate_qr_code(key)
        
        if not result:
            content = [
                f"{Colors.RED}❌ QR CODE GENERATION FAILED{Colors.END}",
                "",
                f"{Colors.YELLOW}Could not generate QR code{Colors.END}"
            ]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        key_id = result['key_id']
        
        content = [
            f"{Colors.GREEN}✅ QR CODE GENERATED{Colors.END}",
            f"{Colors.BOLD}Key ID:{Colors.END} {Colors.CYAN}{key_id}{Colors.END}",
            f"{Colors.BOLD}Saved as:{Colors.END} {result['filepath']}",
            "",
            f"{Colors.YELLOW}ASCII QR Code:{Colors.END}",
            "",
            result['ascii'],
            "",
            f"{Colors.RED}⚠️  Share this QR code securely with recipients{Colors.END}",
            f"{Colors.RED}⚠️  Anyone who scans this QR gets your encryption key{Colors.END}",
            "",
            f"{Colors.CYAN}To import this key, use 'Import Key from QR' option{Colors.END}"
        ]
        box.render(content, color=Colors.YELLOW, with_typing=True)
        
        if PlatformUtils.copy_to_clipboard(key):
            self.typer.type_text("✓ Key copied to clipboard! (Not the QR code)", color=Colors.GREEN)
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
    
    def list_qr_codes(self):
        """List all generated QR codes"""
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " QR CODE INVENTORY ")
        
        if not os.path.exists(self.qr_dir):
            content = [f"{Colors.YELLOW}QR directory not found: {self.qr_dir}{Colors.END}"]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        qr_files = [f for f in os.listdir(self.qr_dir) if f.endswith('.png')]
        
        if not qr_files:
            content = [f"{Colors.YELLOW}No QR codes found in {self.qr_dir}{Colors.END}"]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        headers = ["#", "File", "Size", "Created"]
        rows = []
        
        for i, file in enumerate(sorted(qr_files, key=lambda x: os.path.getmtime(os.path.join(self.qr_dir, x)), reverse=True), 1):
            filepath = os.path.join(self.qr_dir, file)
            size = os.path.getsize(filepath)
            size_str = f"{size/1024:.1f} KB"
            created = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
            rows.append([f"{i}", f"📱 {file}", size_str, created])
        
        table = AnimatedTable(headers)
        table.render(rows, with_typing=True)
        
        self.typer.type_text(f"Total QR codes: {len(qr_files)}", color=Colors.CYAN)
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def restore_key_from_backup_qr(self):
        """Emergency restore encryption key from QR code backup"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " EMERGENCY KEY RESTORE ")
        
        if not self.available:
            content = [
                f"{Colors.RED}❌ QR Code feature unavailable{Colors.END}",
                "",
                f"{Colors.YELLOW}Cannot restore from QR without QR dependencies{Colors.END}",
                f"{Colors.CYAN}💡 Install: pip install qrcode[pil] pillow opencv-python-headless{Colors.END}"
            ]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        content = [
            f"{Colors.RED}⚠️  EMERGENCY KEY RESTORE{Colors.END}",
            "",
            f"{Colors.YELLOW}This will restore your encryption key from a QR code backup{Colors.END}",
            f"{Colors.YELLOW}Use this if you've lost your key file or forgotten it{Colors.END}",
            "",
            f"{Colors.CYAN}Do you have a QR code image saved?{Colors.END}"
        ]
        box.render(content, color=Colors.RED, with_typing=True)
        
        print(f"\n{Colors.GREEN}1.{Colors.END} Use existing QR code from directory")
        print(f"{Colors.GREEN}2.{Colors.END} Provide path to QR code image")
        print(f"{Colors.GREEN}3.{Colors.END} Cancel")
        
        choice = input(f"\n{Colors.YELLOW}Select option [1-3]: {Colors.END}").strip()
        
        if choice == '1':
            if not os.path.exists(self.qr_dir):
                self.typer.type_text("❌ QR directory not found", color=Colors.RED)
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                return
                
            qr_files = [f for f in os.listdir(self.qr_dir) if f.endswith('.png')]
            if not qr_files:
                self.typer.type_text("❌ No QR codes found", color=Colors.RED)
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                return
            
            self.typer.type_text("Available QR codes:", color=Colors.CYAN)
            for i, file in enumerate(sorted(qr_files, key=lambda x: os.path.getmtime(os.path.join(self.qr_dir, x)), reverse=True), 1):
                filepath = os.path.join(self.qr_dir, file)
                created = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
                print(f"  {i}. {file} ({created})")
            
            try:
                idx = int(input(f"\n{Colors.YELLOW}Select QR code [1-{len(qr_files)}]: {Colors.END}")) - 1
                if 0 <= idx < len(qr_files):
                    qr_path = os.path.join(self.qr_dir, qr_files[idx])
                    self.import_key_from_qr(qr_path)
                else:
                    self.typer.type_text("❌ Please select and chose what you want to do in the menu list.", color=Colors.RED)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            except ValueError:
                self.typer.type_text("❌ Please select and chose what you want to do in the menu list.", color=Colors.RED)
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                
        elif choice == '2':
            path = input(f"{Colors.CYAN}Path to QR code image: {Colors.END}").strip()
            if os.path.exists(path):
                self.import_key_from_qr(path)
            else:
                self.typer.type_text(f"❌ File not found: {path}", color=Colors.RED)
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        else:
            self.typer.type_text("Restore cancelled", color=Colors.YELLOW)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

class DirectoryEncryptor:
    """Handle directory/folder encryption and decryption"""
    
    def __init__(self, crypto_engine):
        self.crypto = crypto_engine
        self.typer = TypeWriter('fast')
        self.encrypted_dir = ENCRYPTED_DIR
        self.manifest_file = "manifest.json"
        self.exclude_patterns = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
        self.report_gen = ReportGenerator()
        
        # Ensure encrypted directory exists with proper permissions
        if not os.path.exists(self.encrypted_dir):
            try:
                os.makedirs(self.encrypted_dir, mode=0o700, exist_ok=True)
                self.typer.type_text(f"✅ Created encrypted directory: {self.encrypted_dir}", color=Colors.GREEN)
            except Exception as e:
                self.typer.type_text(f"⚠️ Could not create encrypted directory: {e}", color=Colors.YELLOW)
        
        # Also ensure the directory is writable
        if os.path.exists(self.encrypted_dir):
            try:
                test_file = os.path.join(self.encrypted_dir, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                self.typer.type_text(f"⚠️ Encrypted directory is not writable: {e}", color=Colors.RED)
                
    def should_exclude(self, filepath):
        filename = os.path.basename(filepath)
        for pattern in self.exclude_patterns:
            if pattern in filename:
                return True
        return False
    
    def get_file_tree(self, directory):
        file_tree = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                if not self.should_exclude(full_path):
                    rel_path = os.path.relpath(full_path, directory)
                    file_tree.append({
                        'path': full_path,
                        'rel_path': rel_path,
                        'size': os.path.getsize(full_path),
                        'modified': os.path.getmtime(full_path)
                    })
        return file_tree
        
    def encrypt_directory(self, directory_path, progress_callback=None):
        """Encrypt directory - Cross-platform using ZIP (most compatible)"""
        
        if not self.crypto.cipher:
            self.typer.type_text("❌ Encryption not initialized. Setup encryption first.", color=Colors.RED)
            return False, None
        
        if not os.path.exists(directory_path):
            self.typer.type_text(f"❌ Directory not found: {directory_path}", color=Colors.RED)
            return False, None
        
        if not os.path.isdir(directory_path):
            self.typer.type_text(f"❌ Path is not a directory: {directory_path}", color=Colors.RED)
            return False, None
        
        self.typer.type_text(f"📂 Scanning directory: {directory_path}", color=Colors.CYAN)
        file_tree = self.get_file_tree(directory_path)
        
        if not file_tree:
            self.typer.type_text("⚠️ No files found to encrypt", color=Colors.YELLOW)
            return False, None
        
        total_files = len(file_tree)
        self.typer.type_text(f"📁 Found {total_files} files to encrypt", color=Colors.GREEN)
        
        dir_name = os.path.basename(directory_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use ZIP format for maximum cross-platform compatibility
        encrypted_container = os.path.join(self.encrypted_dir, f"{dir_name}_{timestamp}.enc_dir.zip")
        
        temp_dir = tempfile.mkdtemp(prefix="dsterminal_enc_")
        processed_files = []
        
        try:
            metadata = {
                'original_name': dir_name,
                'original_path': directory_path,
                'encrypted_date': datetime.now().isoformat(),
                'total_files': total_files,
                'total_size': sum(f['size'] for f in file_tree),
                'format': 'zip',
                'platform': platform.system(),
                'files': []
            }
            
            for idx, file_info in enumerate(file_tree, 1):
                rel_path = file_info['rel_path']
                enc_file_path = os.path.join(temp_dir, rel_path + '.enc')
                
                os.makedirs(os.path.dirname(enc_file_path), exist_ok=True)
                
                try:
                    with open(file_info['path'], 'rb') as f:
                        data = f.read()
                    
                    encrypted_data = self.crypto.cipher.encrypt(data)
                    
                    with open(enc_file_path, 'wb') as f:
                        f.write(encrypted_data)
                    
                    metadata['files'].append({
                        'path': rel_path,
                        'encrypted': True
                    })
                    
                    processed_files.append({
                        'name': rel_path,
                        'status': 'Encrypted',
                        'size': self.crypto.human_readable_size(file_info['size'])
                    })
                    
                    if progress_callback:
                        progress_callback(idx, total_files, rel_path)
                    
                    if idx % 10 == 0 or idx == total_files:
                        self.typer.type_text(f"  Progress: {idx}/{total_files} files encrypted", color=Colors.DIM)
                        
                except Exception as e:
                    self.typer.type_text(f"  ⚠️ Failed to encrypt {rel_path}: {str(e)}", color=Colors.RED)
            
            manifest_path = os.path.join(temp_dir, self.manifest_file)
            with open(manifest_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.typer.type_text("📦 Creating encrypted container...", color=Colors.YELLOW)
            
            # Always use ZIP format (cross-platform compatible)
            import zipfile
            with zipfile.ZipFile(encrypted_container, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            shutil.rmtree(temp_dir)
            
            manifest_backup = os.path.join(self.encrypted_dir, f"{dir_name}_{timestamp}_manifest.json")
            with open(manifest_backup, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.typer.type_text(f"✅ Directory encrypted successfully!", color=Colors.GREEN)
            self.typer.type_text(f"   Container: {encrypted_container}", color=Colors.CYAN)
            self.typer.type_text(f"   Format: ZIP (cross-platform)", color=Colors.CYAN)
            self.typer.type_text(f"   Total files: {total_files}", color=Colors.CYAN)
            self.typer.type_text(f"   Total size: {self.crypto.human_readable_size(metadata['total_size'])}", color=Colors.CYAN)
            
            self.crypto.add_activity(f"Encrypted directory: {dir_name} ({total_files} files)")
            
            # Generate report
            self.typer.type_text("📊 Generating report...", color=Colors.YELLOW)
            key_info = self.crypto.get_key_info()
            report_details = {
                'target': directory_path,
                'total_files': total_files,
                'total_size': self.crypto.human_readable_size(metadata['total_size']),
                'files': processed_files,
                'key_info': key_info,
                'format': 'ZIP',
                'platform': platform.system()
            }
            self.report_gen.generate_report("DIRECTORY ENCRYPTION", report_details)
            
            return True, encrypted_container
            
        except Exception as e:
            self.typer.type_text(f"❌ Failed to encrypt directory: {str(e)}", color=Colors.RED)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False, None
        
    def decrypt_directory(self, encrypted_container, output_dir=None):
        """Decrypt directory - Auto-detects format (ZIP or TAR) for cross-platform compatibility"""
        
        if not self.crypto.cipher:
            self.typer.type_text("❌ Decryption not initialized. Setup encryption first.", color=Colors.RED)
            return False
        
        if not os.path.exists(encrypted_container):
            self.typer.type_text(f"❌ Container not found: {encrypted_container}", color=Colors.RED)
            return False
        
        temp_dir = tempfile.mkdtemp(prefix="dsterminal_dec_")
        processed_files = []
        
        try:
            self.typer.type_text(f"📦 Extracting container...", color=Colors.YELLOW)
            
            # Auto-detect format
            extracted = False
            format_used = "unknown"
            
            # Try ZIP first (most common)
            try:
                import zipfile
                with zipfile.ZipFile(encrypted_container, 'r') as zipf:
                    zipf.extractall(temp_dir)
                extracted = True
                format_used = "ZIP"
                self.typer.type_text(f"   ✅ Detected and extracted as ZIP archive", color=Colors.GREEN)
            except:
                pass
            
            # If ZIP failed, try TAR.GZ
            if not extracted:
                try:
                    import tarfile
                    with tarfile.open(encrypted_container, 'r:gz') as tarf:
                        tarf.extractall(temp_dir)
                    extracted = True
                    format_used = "TAR.GZ"
                    self.typer.type_text(f"   ✅ Detected and extracted as TAR.GZ archive", color=Colors.GREEN)
                except:
                    pass
            
            # If TAR.GZ failed, try TAR
            if not extracted:
                try:
                    import tarfile
                    with tarfile.open(encrypted_container, 'r:') as tarf:
                        tarf.extractall(temp_dir)
                    extracted = True
                    format_used = "TAR"
                    self.typer.type_text(f"   ✅ Detected and extracted as TAR archive", color=Colors.GREEN)
                except:
                    pass
            
            if not extracted:
                self.typer.type_text(f"   ❌ Could not extract container (unsupported format)", color=Colors.RED)
                shutil.rmtree(temp_dir)
                return False
            
            # Check what was extracted
            extracted_items = os.listdir(temp_dir)
            if not extracted_items:
                self.typer.type_text("❌ Empty container", color=Colors.RED)
                shutil.rmtree(temp_dir)
                return False
            
            # Find the extracted directory (might be in a subfolder)
            extracted_dir = temp_dir
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                extracted_dir = os.path.join(temp_dir, extracted_items[0])
            
            # Find manifest file
            manifest_path = os.path.join(extracted_dir, self.manifest_file)
            if not os.path.exists(manifest_path):
                # Search for manifest in subdirectories
                for root, dirs, files in os.walk(extracted_dir):
                    if self.manifest_file in files:
                        manifest_path = os.path.join(root, self.manifest_file)
                        extracted_dir = root
                        break
                
                if not os.path.exists(manifest_path):
                    self.typer.type_text("❌ Manifest not found in container", color=Colors.RED)
                    shutil.rmtree(temp_dir)
                    return False
            
            # Load manifest
            with open(manifest_path, 'r') as f:
                metadata = json.load(f)
            
            # Determine output directory
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(encrypted_container), 
                                        f"{metadata['original_name']}_decrypted")
            
            os.makedirs(output_dir, exist_ok=True)
            
            total_files = len(metadata['files'])
            self.typer.type_text(f"📁 Decrypting {total_files} files...", color=Colors.CYAN)
            
            decrypted_count = 0
            for idx, file_info in enumerate(metadata['files'], 1):
                if not file_info.get('encrypted', True):
                    continue
                
                enc_path = os.path.join(extracted_dir, file_info['path'] + '.enc')
                dec_path = os.path.join(output_dir, file_info['path'])
                
                if not os.path.exists(enc_path):
                    self.typer.type_text(f"  ⚠️ Encrypted file not found: {file_info['path']}", color=Colors.RED)
                    continue
                
                try:
                    os.makedirs(os.path.dirname(dec_path), exist_ok=True)
                    
                    with open(enc_path, 'rb') as f:
                        encrypted_data = f.read()
                    
                    decrypted_data = self.crypto.cipher.decrypt(encrypted_data)
                    
                    with open(dec_path, 'wb') as f:
                        f.write(decrypted_data)
                    
                    decrypted_count += 1
                    processed_files.append({
                        'name': file_info['path'],
                        'status': 'Decrypted',
                        'size': self.crypto.human_readable_size(os.path.getsize(dec_path))
                    })
                    
                    if idx % 10 == 0 or idx == total_files:
                        self.typer.type_text(f"  Progress: {idx}/{total_files} files decrypted", color=Colors.DIM)
                        
                except Exception as e:
                    self.typer.type_text(f"  ❌ Failed to decrypt {file_info['path']}: {str(e)}", color=Colors.RED)
            
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            
            self.typer.type_text(f"✅ Directory decrypted successfully!", color=Colors.GREEN)
            self.typer.type_text(f"   Output: {output_dir}", color=Colors.CYAN)
            self.typer.type_text(f"   Files decrypted: {decrypted_count}/{total_files}", color=Colors.CYAN)
            self.typer.type_text(f"   Format: {format_used} (auto-detected)", color=Colors.CYAN)
            
            self.crypto.add_activity(f"Decrypted directory: {metadata['original_name']} ({decrypted_count} files)")
            
            # Generate report
            self.typer.type_text("📊 Generating report...", color=Colors.YELLOW)
            key_info = self.crypto.get_key_info()
            total_size = 0
            for root, dirs, files in os.walk(output_dir):
                for f in files:
                    f_path = os.path.join(root, f)
                    total_size += os.path.getsize(f_path)
            
            report_details = {
                'target': encrypted_container,
                'total_files': decrypted_count,
                'total_size': self.crypto.human_readable_size(total_size),
                'files': processed_files,
                'key_info': key_info,
                'format': format_used,
                'platform': platform.system()
            }
            self.report_gen.generate_report("DIRECTORY DECRYPTION", report_details)
            
            return True
            
        except Exception as e:
            self.typer.type_text(f"❌ Failed to decrypt directory: {str(e)}", color=Colors.RED)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False
    
    def list_encrypted_directories(self):
        """List encrypted directories - Supports multiple formats"""
        if not os.path.exists(self.encrypted_dir):
            return []
        
        containers = []
        for file in os.listdir(self.encrypted_dir):
            # Support all formats: .enc_dir, .enc_dir.zip, .enc_dir.tar.gz, .enc_dir.tgz
            if (file.endswith('.enc_dir.zip') or 
                file.endswith('.enc_dir.tar.gz') or 
                file.endswith('.enc_dir.tgz') or 
                file.endswith('.enc_dir')):
                full_path = os.path.join(self.encrypted_dir, file)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                
                # Detect format
                if file.endswith('.zip'):
                    fmt = "ZIP"
                elif file.endswith('.tar.gz') or file.endswith('.tgz'):
                    fmt = "TAR.GZ"
                else:
                    fmt = "Unknown"
                
                containers.append({
                    'name': file,
                    'path': full_path,
                    'size': size,
                    'size_human': self.crypto.human_readable_size(size),
                    'modified': modified.strftime("%Y-%m-%d %H:%M:%S"),
                    'format': fmt
                })
        
        return sorted(containers, key=lambda x: x['modified'], reverse=True)
     
class CryptoEngine:
    """Main encryption engine with QR code integration - cross-platform with typing effects"""

    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.cipher = None
        self.matrix = MatrixRain()
        self.qr_manager = QRCodeManager(self)
        self.dashboard = HackerDashboard()
        self.dir_encryptor = DirectoryEncryptor(self)
        self.report_gen = ReportGenerator()
        self.typer = TypeWriter('fast')
        self.start_time = datetime.now()
        self.last_action = None
        self.recent_activity = []
        self.reports_count = 0
        
        # delete original folder/dir/file confirm first
        self.secure_delete_enabled = False  # Default: OFF for safety
        self.secure_delete_passes = 3       # Number of overwrite passes
        self.auto_delete_original = False   # Default: ask user each time
        
        # Add deletion log
        self.deletion_log = []
        
        # Ensure ALL directories exist
        PlatformUtils.create_directories()
        
        # Explicitly create encrypted_dirs directory
        if not os.path.exists(ENCRYPTED_DIR):
            try:
                os.makedirs(ENCRYPTED_DIR, mode=0o700, exist_ok=True)
                print(f"✅ Created encrypted directory: {ENCRYPTED_DIR}")
            except Exception as e:
                print(f"⚠️ Could not create encrypted directory: {e}")
        
        # Ensure reports directory exists in workspace
        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR, mode=0o700, exist_ok=True)
        
        # Also ensure the data directory exists
        data_dir = Paths.get_data_dir()
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, mode=0o700, exist_ok=True)
        
        self.init_cipher()
        self.update_stats()
        
        if QR_DEPS_AVAILABLE:
            print()
            time.sleep(1)
        else:
            print()
            self.typer.type_text("⚠️ QR Code features are disabled.", color=Colors.YELLOW)
            self.typer.type_text("💡 To enable QR features, install missing dependencies:", color=Colors.CYAN)
            self.typer.type_text("   pip install qrcode[pil] pillow opencv-python-headless", color=Colors.CYAN)
            time.sleep(3)

    def main(self):
        """Main entry point for CryptoEngine - Full interactive dashboard"""
        
        while True:
            # Clear screen and show the crypto dashboard
            PlatformUtils.clear_screen()
            self.show_dashboard(with_typing=False)
            
            # Show the crypto menu overlay
            print(f"\n{Colors.DIM}╔═══════════════════════════════════════════════════════════════════════════════════════╗")
            print(f"║  {Colors.CYAN}┌───────────────────────────────────────────────────────────────────────────────────┐{Colors.DIM}║")
            print(f"║  {Colors.CYAN}│  {Colors.GREEN}01{Colors.CYAN} Setup System     {Colors.GREEN}02{Colors.CYAN} Encrypt File   {Colors.GREEN}03{Colors.CYAN} Decrypt File   {Colors.GREEN}04{Colors.CYAN} Encrypt Dir  │{Colors.DIM}║")
            print(f"║  {Colors.CYAN}│  {Colors.GREEN}05{Colors.CYAN} Decrypt Dir      {Colors.GREEN}06{Colors.CYAN} Backup Key     {Colors.GREEN}07{Colors.CYAN} QR Generate    {Colors.GREEN}08{Colors.CYAN} Export Key   │{Colors.DIM}║")
            print(f"║  {Colors.CYAN}│  {Colors.GREEN}09{Colors.CYAN} Import Key       {Colors.GREEN}10{Colors.CYAN} List Files     {Colors.GREEN}11{Colors.CYAN} File Info      {Colors.GREEN}12{Colors.CYAN} Verify Sys  │{Colors.DIM}║")
            print(f"║  {Colors.CYAN}│  {Colors.GREEN}13{Colors.CYAN} Reports          {Colors.GREEN}14{Colors.CYAN} QR Import      {Colors.GREEN}15{Colors.CYAN} QR Restore     {Colors.GREEN}16{Colors.CYAN} QR List     │{Colors.DIM}║")
            print(f"║  {Colors.CYAN}│  {Colors.GREEN}17{Colors.CYAN} Clean QR         {Colors.GREEN}18{Colors.CYAN} Encrypted Dirs {Colors.GREEN}19{Colors.CYAN} Debug Info     {Colors.GREEN}20{Colors.CYAN} Encrypt Test│{Colors.DIM}║")
            print(f"║  {Colors.CYAN}│  {Colors.GREEN}21{Colors.CYAN} Decrypt Test     {Colors.GREEN}00{Colors.CYAN} Return to DSTERMINAL                                │{Colors.DIM}║")
            print(f"║  {Colors.CYAN}└───────────────────────────────────────────────────────────────────────────────────┘{Colors.DIM}║")
            print(f"╚═══════════════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            choice = input(f"\n{Colors.GREEN}└──[{Colors.YELLOW}CRYPTO{Colors.GREEN}]{Colors.END} # ").strip()
            
            # ============================================================
            # CRYPTO MENU OPTIONS
            # ============================================================
            if choice == '01' or choice == '1':
                self.encrypt_setup()
            elif choice == '02' or choice == '2':
                filename = input(f"{Colors.CYAN}File to encrypt: {Colors.END}").strip()
                if filename:
                    self.encrypt_file(filename)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice == '03' or choice == '3':
                filename = input(f"{Colors.CYAN}File to decrypt: {Colors.END}").strip()
                if filename:
                    self.decrypt_file(filename)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice == '04' or choice == '4':
                self.encrypt_directory()
            elif choice == '05' or choice == '5':
                self.decrypt_directory()
            elif choice == '06' or choice == '6':
                self.crypto_backup()
            elif choice == '07' or choice == '7':
                self.qr_generate()
            elif choice == '08' or choice == '8':
                self.export_encryption_key()
            elif choice == '09' or choice == '9':
                self.import_encryption_key()
            elif choice == '10':
                self.crypto_list()
            elif choice == '11':
                self.crypto_info()
            elif choice == '12':
                self.crypto_verify()
            elif choice == '13':
                self.list_reports()
            elif choice == '14':
                self.qr_import()
            elif choice == '15':
                self.qr_restore()
            elif choice == '16':
                self.qr_list()
            elif choice == '17':
                if os.path.exists(QR_CODE_DIR):
                    self.qr_list()
                    confirm = input(f"\n{Colors.RED}Delete all QR codes? (y/N): {Colors.END}").strip().lower()
                    if confirm == 'y':
                        count = 0
                        for f in os.listdir(QR_CODE_DIR):
                            if f.endswith('.png'):
                                try:
                                    os.remove(os.path.join(QR_CODE_DIR, f))
                                    count += 1
                                except:
                                    pass
                        self.typer.type_text(f"✅ Deleted {count} QR codes", color=Colors.GREEN)
                        self.add_activity(f"Cleaned {count} QR codes")
                        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                else:
                    self.typer.type_text("❌ QR directory not found", color=Colors.RED)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice == '18':
                self.list_encrypted_dirs()
            elif choice == '19':
                self.typer.type_text("DEBUG INFO", color=Colors.RED)
                info = PlatformUtils.get_platform_info()
                for key, value in info.items():
                    self.typer.type_text(f"{key}: {value}", color=Colors.CYAN)
                self.typer.type_text(f"KEY_FILE: {KEY_FILE}", color=Colors.CYAN)
                self.typer.type_text(f"QR_CODE_DIR: {QR_CODE_DIR}", color=Colors.CYAN)
                self.typer.type_text(f"BACKUP_DIR: {BACKUP_DIR}", color=Colors.CYAN)
                self.typer.type_text(f"ENCRYPTED_DIR: {ENCRYPTED_DIR}", color=Colors.CYAN)
                self.typer.type_text(f"REPORTS_DIR: {REPORTS_DIR}", color=Colors.CYAN)
                self.typer.type_text(f"Key exists: {os.path.exists(KEY_FILE)}", color=Colors.CYAN)
                self.typer.type_text(f"QR dir exists: {os.path.exists(QR_CODE_DIR)}", color=Colors.CYAN)
                self.typer.type_text(f"Encrypted dir exists: {os.path.exists(ENCRYPTED_DIR)}", color=Colors.CYAN)
                self.typer.type_text(f"Reports dir exists: {os.path.exists(REPORTS_DIR)}", color=Colors.CYAN)
                self.typer.type_text(f"QR Method: {QR_METHOD}", color=Colors.CYAN)
                self.typer.type_text(f"Report Available: {REPORT_AVAILABLE}", color=Colors.CYAN)
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice == '20':
                self.encrypt_test()
            elif choice == '21':
                self.decrypt_test()
            elif choice == '00' or choice == '0':
                print(f"\n{Colors.YELLOW}Returning to DSTERMINAL...{Colors.END}")
                time.sleep(0.5)
                break
            else:
                self.typer.type_text("Invalid option. Please select a valid command.", color=Colors.RED)
                time.sleep(1)  
                
    def get_key_info(self):
        """Get encryption key information for reports"""
        key_info = {
            'key_id': 'N/A',
            'key_location': KEY_FILE,
            'full_key': ''
        }
        
        if os.path.exists(KEY_FILE):
            try:
                with open(KEY_FILE, 'r') as f:
                    key = f.read().strip()
                    key_info['key_id'] = hashlib.sha256(key.encode()).hexdigest()[:16]
                    key_info['full_key'] = key
            except:
                pass
        
        return key_info
    
    def update_stats(self):
        key_exists = os.path.exists(KEY_FILE)
        key_id = None
        if key_exists:
            try:
                with open(KEY_FILE, "r") as f:
                    key = f.read().strip()
                    key_id = hashlib.sha256(key.encode()).hexdigest()[:16]
            except:
                pass
        
        qr_count = 0
        if os.path.exists(QR_CODE_DIR):
            qr_count = len([f for f in os.listdir(QR_CODE_DIR) if f.endswith('.png')])
        
        encrypted_count = 0
        for root, dirs, files in os.walk(self.base_dir):
            encrypted_count += len([f for f in files if f.endswith('.enc')])
        
        encrypted_dirs = 0
        if os.path.exists(ENCRYPTED_DIR):
            encrypted_dirs = len([f for f in os.listdir(ENCRYPTED_DIR) 
                                 if f.endswith('.enc_dir') or f.endswith('.enc_dir.zip') or f.endswith('.enc_dir.tar.gz')])
        
        # Count reports
        self.reports_count = 0
        if os.path.exists(REPORTS_DIR):
            self.reports_count = len([f for f in os.listdir(REPORTS_DIR) if f.endswith('.pdf') or f.endswith('.html')])
        
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        
        self.dashboard.set_stats({
            'encryption_ready': key_exists and self.cipher is not None,
            'key_id': key_id,
            'key_exists': key_exists,
            'key_location': KEY_FILE,
            'qr_count': qr_count,
            'encrypted_count': encrypted_count,
            'encrypted_dirs': encrypted_dirs,
            'reports_count': self.reports_count,
            'cipher_ready': self.cipher is not None,
            'uptime': uptime,
            'memory_usage': 'N/A',
            'cpu_usage': 'N/A',
            'last_action': self.last_action,
            'recent_activity': self.recent_activity[-5:]
        })
    
    def add_activity(self, activity):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recent_activity.append(f"[{timestamp}] {activity}")
        if len(self.recent_activity) > 10:
            self.recent_activity = self.recent_activity[-10:]
        self.last_action = activity
        self.update_stats()
    
    def init_cipher(self):
        if os.path.exists(KEY_FILE):
            try:
                with open(KEY_FILE, "r") as f:
                    key = f.read().strip()
                    self.cipher = Fernet(key.encode())
                    self.add_activity("Cipher initialized")
            except:
                self.cipher = None
                self.add_activity("Cipher initialization failed")

    def human_readable_size(self, size):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    def secure_delete(self, file_path, passes=3):
        """Securely delete a file by overwriting it multiple times with verification"""
        try:
            # Normalize path to handle spaces and special characters
            file_path = os.path.normpath(file_path)
            
            if not os.path.exists(file_path):
                print(f"{Colors.YELLOW}⚠️  File not found: {file_path}{Colors.END}")
                return False
            
            # Get absolute path to avoid any confusion
            file_path = os.path.abspath(file_path)
            print(f"{Colors.DIM}   Path: {file_path}{Colors.END}")
            
            # Check if file is accessible
            if not os.access(file_path, os.W_OK):
                print(f"{Colors.RED}❌ File is not writable: {file_path}{Colors.END}")
                return False
            
            # Get file size
            size = os.path.getsize(file_path)
            
            # For very small files, just do one pass with random data
            if size < 1024:  # Less than 1KB
                passes = 1
            
            # Close any open handles to the file
            import gc
            gc.collect()
            time.sleep(0.2)
            
            # Try to delete the file first to check if it's locked
            try:
                os.remove(file_path)
                # If successful, we're done
                if not os.path.exists(file_path):
                    print(f"{Colors.GREEN}✓ File deleted (no secure overwrite needed){Colors.END}")
                    return True
            except PermissionError:
                # File is locked, try to unlock it
                print(f"{Colors.YELLOW}⚠️  File is locked. Attempting to unlock...{Colors.END}")
                pass
            except Exception as e:
                print(f"{Colors.DIM}   Cannot delete directly: {e}{Colors.END}")
            
            # Try to open the file with exclusive write access
            try:
                # Use a more robust approach - open in binary mode with proper flushing
                with open(file_path, "r+b") as f:
                    # First pass: overwrite with random data
                    for i in range(passes):
                        f.seek(0)
                        bytes_written = 0
                        chunk_size = 1024 * 1024  # 1MB chunks
                        while bytes_written < size:
                            chunk = os.urandom(min(chunk_size, size - bytes_written))
                            f.write(chunk)
                            bytes_written += len(chunk)
                        f.flush()
                        os.fsync(f.fileno())
                        f.seek(0)
                        print(f"{Colors.DIM}   Pass {i+1}/{passes} complete{Colors.END}")
                    
                    # Final pass: overwrite with zeros
                    f.seek(0)
                    bytes_written = 0
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while bytes_written < size:
                        chunk = b'\x00' * min(chunk_size, size - bytes_written)
                        f.write(chunk)
                        bytes_written += len(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Close any remaining handles
                gc.collect()
                time.sleep(0.2)
                
            except PermissionError as e:
                print(f"{Colors.RED}❌ Permission denied: {file_path}{Colors.END}")
                print(f"{Colors.YELLOW}⚠️  The file may be open in another program.{Colors.END}")
                print(f"{Colors.CYAN}💡 Try closing the file in any open programs and try again.{Colors.END}")
                return False
            except Exception as e:
                print(f"{Colors.RED}❌ Error during secure overwrite: {e}{Colors.END}")
                return False
            
            # Now delete the file
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to remove file after overwrite: {e}{Colors.END}")
                # Try one more time with a different approach
                try:
                    import subprocess
                    if platform.system() == 'Windows':
                        # Use PowerShell to force delete
                        cmd = f'powershell -Command "Remove-Item -Path \'{file_path}\' -Force -ErrorAction SilentlyContinue"'
                        subprocess.run(cmd, shell=True, capture_output=True)
                    else:
                        # Use rm -f on Unix
                        subprocess.run(['rm', '-f', file_path])
                except:
                    pass
            
            # Verify deletion
            time.sleep(0.2)
            if not os.path.exists(file_path):
                print(f"{Colors.GREEN}✓ File securely deleted: {os.path.basename(file_path)}{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ File still exists after deletion attempt{Colors.END}")
                print(f"{Colors.YELLOW}⚠️  Original file kept for safety{Colors.END}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Unexpected error in secure_delete: {str(e)}{Colors.END}")
            return False
        
    def show_dashboard(self, with_typing=True):
        self.update_stats()
        self.dashboard.render_dashboard(with_typing)
        
    def show_banner(self):
        self.show_dashboard()

    def animate_encryption(self, filename, operation="ENCRYPTING"):
        """Fixed animation that doesn't overlap with dashboard"""
        
        # Don't clear screen - just show animation overlay
        print("\n" + "="*60)
        print(f"{Colors.BOLD}{operation} {filename}{Colors.END}")
        print("="*60)
        
        # Progress bar animation - 8 steps
        for i in range(8):
            progress = (i + 1) * 12.5
            bar_length = 30
            filled = int(bar_length * progress // 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # Status messages
            status_msgs = [
                "▶ Initializing encryption vectors...",
                "▶ Generating round keys...",
                "▶ Applying substitution boxes...",
                "▶ Mixing data blocks...",
                "▶ Finalizing operation...",
                "▶ Verifying integrity...",
                "▶ Compressing output...",
                "▶ Complete!"
            ]
            
            # Clear just the progress area (not the whole screen)
            sys.stdout.write('\033[7A')  # Move up 7 lines
            sys.stdout.write('\033[J')    # Clear from cursor to end
            
            print(f"Progress: [{bar}] {progress:.1f}%")
            print(f"Status: {status_msgs[i] if i < len(status_msgs) else 'Processing...'}")
            
            time.sleep(0.15)
        
        print(f"\n{Colors.GREEN}✓ {operation} COMPLETE{Colors.END}")
        
    def animate_directory_encryption(self, directory, total_files, operation="ENCRYPTING"):
        """Directory animation with 1-minute Matrix rain for decryption"""
        
        # Print a clean header for the operation
        print(f"\n{Colors.YELLOW}┌────────────── {operation} DIRECTORY ──────────────┐{Colors.END}")
        
        # Progress bar
        for i in range(7):
            progress = (i + 1) * 14
            bar_length = 40
            filled = int(bar_length * min(progress, 100) // 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            status_messages = [
                "Scanning directory structure...",
                "Building file tree...",
                "Initializing encryption pipeline...",
                "Encrypting files...",
                "Creating secure container...",
                "Finalizing encryption...",
                "Complete!"
            ]
            
            if i > 0:
                sys.stdout.write('\033[2A')
                sys.stdout.write('\033[J')
            
            print(f"│ {Colors.CYAN}Progress: [{bar}] {min(progress, 100):.1f}%{Colors.END}")
            print(f"│ {Colors.DIM}Status: {status_messages[i]}{Colors.END}")
            
            time.sleep(0.2)
        
        print(f"{Colors.YELLOW}└──────────────────────────────────────────────────┘{Colors.END}")
        print(f"\n{Colors.GREEN}✓ {operation} COMPLETE{Colors.END}")
        
        # For DECRYPTION operations, show Matrix rain for 1 minute
        if "DECRYPT" in operation.upper():
            print(f"\n{Colors.MAGENTA}╔════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.MAGENTA}║              DECRYPTING                                                 ║{Colors.END}")
            print(f"{Colors.MAGENTA}║           Visualizing data flow                                         ║{Colors.END}")
            print(f"{Colors.MAGENTA}╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            # Show Matrix rain for 60 seconds
            self.show_matrix_rain_animated(duration=60, height=10, width=80)
            
            print(f"\n{Colors.GREEN}✓ Decryption completed after 60 seconds{Colors.END}")
        else:
            # For encryption, show shorter Matrix rain (5 seconds)
            print(f"\n{Colors.MAGENTA}╔════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.MAGENTA}║         PROGRESS VISUALIZATION                       ║{Colors.END}")
            print(f"{Colors.MAGENTA}╚════════════════════════════════════════════════════╝{Colors.END}")
            self.show_matrix_rain_animated(duration=5, height=8, width=60)
            print(f"\n{Colors.GREEN}✓ Visualization complete{Colors.END}")
                
    def show_matrix_rain_animated(self, duration=5, height=10, width=80):
        """Show animated Matrix rain for specified duration"""
        
        # Calculate frames needed (one frame every 0.15 seconds)
        frames = int(duration / 0.15)
        
        # Matrix characters
        chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        
        # Track "drops" for more realistic effect
        drops = {j: random.randint(-height, 0) for j in range(width)}
        drop_speeds = {j: random.randint(1, 4) for j in range(width)}
        drop_lengths = {j: random.randint(3, 8) for j in range(width)}
        
        start_time = time.time()
        frame_count = 0
        
        # Show timer
        print(f"\n{Colors.DIM}Time remaining: {duration:.0f} seconds{Colors.END}")
        print(f"{Colors.DIM}Press Ctrl+C to skip{Colors.END}\n")
        
        try:
            while time.time() - start_time < duration:
                # Calculate remaining time
                elapsed = time.time() - start_time
                remaining = duration - elapsed
                
                # Clear the matrix area (height + header/footer)
                if frame_count > 0:
                    sys.stdout.write(f'\033[{height + 3}A')  # height + timer + remaining
                    sys.stdout.write('\033[J')
                
                # Update timer
                print(f"{Colors.DIM}⏱ PROCESSING...: {remaining:.1f} seconds{Colors.END}")
                
                # Generate Matrix rain frame
                matrix_frame = []
                for i in range(height):
                    line = ''
                    for j in range(width):
                        # Update drops
                        if i == drops[j]:
                            # Bright head of the drop
                            char = random.choice(chars)
                            line += f"{Colors.GREEN}{Colors.BOLD}{char}{Colors.END}"
                        elif drops[j] - drop_lengths[j] < i < drops[j]:
                            # Body of the drop
                            char = random.choice(chars)
                            # Gradient effect - brighter near head
                            if i > drops[j] - 3:
                                line += f"{Colors.GREEN}{char}{Colors.END}"
                            else:
                                line += f"{Colors.DIM}{char}{Colors.END}"
                        else:
                            # Random background characters
                            if random.random() > 0.92:
                                char = random.choice(chars)
                                line += f"{Colors.DIM}{char}{Colors.END}"
                            else:
                                line += ' '
                    matrix_frame.append(line)
                
                # Print the frame
                for line in matrix_frame:
                    print(line)
                
                # Update drops for next frame
                for j in range(width):
                    if drops[j] >= height:
                        # Reset drop at top
                        drops[j] = -drop_lengths[j] - random.randint(0, 5)
                        drop_speeds[j] = random.randint(1, 4)
                        drop_lengths[j] = random.randint(3, 8)
                    else:
                        # Move drop down
                        drops[j] += drop_speeds[j] * 0.5
                
                frame_count += 1
                time.sleep(0.15)
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⚠️ Process interrupted by user{Colors.END}")
            # Clear the matrix area
            sys.stdout.write(f'\033[{height + 3}A')
            sys.stdout.write('\033[J')
            return
        
        # Clear the matrix area after completion
        sys.stdout.write(f'\033[{height + 3}A')
        sys.stdout.write('\033[J')
        
    def encrypt_setup(self):
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " ENCRYPTION SETUP ")
        
        self.typer.type_text("INITIALIZING SECURE ENCRYPTION SYSTEM", color=Colors.YELLOW, newline=True)
        self.typer.type_text("═══════════════════════════════════════════════════════", color=Colors.RED, newline=True)

        if os.path.exists(KEY_FILE):
            with open(KEY_FILE) as f:
                key = f.read().strip()
            key_id = hashlib.sha256(key.encode()).hexdigest()[:16]
            
            content = [
                f"{Colors.GREEN}✅ EXISTING KEY FOUND{Colors.END}",
                f"{Colors.BOLD}Key ID:{Colors.END} {Colors.CYAN}{key_id}{Colors.END}",
                f"{Colors.BOLD}Location:{Colors.END} {KEY_FILE}",
                f"{Colors.BOLD}Status:{Colors.END} {Colors.GREEN}ACTIVE{Colors.END}"
            ]
            box.render(content, color=Colors.GREEN, with_typing=True)
            self.add_activity("Setup checked - key exists")
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return

        self.typer.type_text("▶ Generating quantum-resistant encryption key...", color=Colors.YELLOW)
        time.sleep(1)
        
        for i in range(3):
            self.typer.type_text(f"   Entropy pool: {''.join(random.choices('01', k=20))}", color=Colors.CYAN)
            time.sleep(1.3)
        
        key = Fernet.generate_key().decode()
        
        key_dir = os.path.dirname(KEY_FILE)
        if not os.path.exists(key_dir):
            os.makedirs(key_dir, mode=0o700, exist_ok=True)
        
        with open(KEY_FILE, "w") as f:
            f.write(key)
        
        try:
            os.chmod(KEY_FILE, 0o600)
        except:
            pass
        
        key_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        
        content = [
            f"{Colors.GREEN}✅ NEW ENCRYPTION KEY GENERATED{Colors.END}",
            f"{Colors.BOLD}Key ID:{Colors.END} {Colors.CYAN}{key_id}{Colors.END}",
            f"{Colors.BOLD}Location:{Colors.END} {KEY_FILE}",
            f"{Colors.BOLD}Permissions:{Colors.END} {Colors.YELLOW}600 (user only){Colors.END}",
            "",
            f"{Colors.RED}⚠️  KEEP THIS KEY SAFE!{Colors.END}",
            f"{Colors.CYAN}💡 Use QR code export to share securely{Colors.END}"
        ]
        box.render(content, color=Colors.GREEN, with_typing=True)
        
        self.init_cipher()
        self.add_activity("New encryption key generated")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def crypto_status(self):
        self.show_dashboard(with_typing=True)
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def encrypt_test(self):
        """Run encryption test with Matrix rain - not overlapping"""
        print(f"\n{Colors.YELLOW}ENCRYPTION SYSTEM TEST{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")

        test_file = os.path.join(self.base_dir, "crypto_test.txt")
        
        # Create test file
        with open(test_file, "w") as f:
            f.write("DSTerminal encryption test - DIR ENCRYPTION\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("Classified: TOP SECRET\n")
        
        print(f"{Colors.GREEN}✓ Test file created{Colors.END}")
        time.sleep(1.5)
        
        # Encrypt with animation (Matrix rain included but separate)
        self.encrypt_file("crypto_test.txt")
        enc = test_file + ".enc"
        
        if os.path.exists(enc):
            print(f"{Colors.GREEN}✓ Encryption successful{Colors.END}")
            time.sleep(1.5)
            
            # Show Matrix rain in a separate block
            # print(f"\n{Colors.MAGENTA}╔════════════════════════════════════════════════════╗{Colors.END}")
            # print(f"{Colors.MAGENTA}║         DECRYPTION VISUALIZATION...                 ║{Colors.END}")
            # print(f"{Colors.MAGENTA}╚════════════════════════════════════════════════════╝{Colors.END}")
            
            # Show Matrix rain
            # for frame in range(3):
            #     if frame > 0:
            #         sys.stdout.write('\033[6A')
            #         sys.stdout.write('\033[J')
                
            #     for i in range(6):
            #         line = ''
            #         for j in range(50):
            #             if random.random() > 0.6:
            #                 char = random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'])
            #                 if random.random() > 0.3:
            #                     line += f"{Colors.GREEN}{char}{Colors.END}"
            #                 else:
            #                     line += f"{Colors.DIM}{char}{Colors.END}"
            #             else:
            # #                 line += ' '
            #         print(line)
            #     time.sleep(1.15)
            
            # # Clear Matrix rain
            # sys.stdout.write('\033[6A')
            # sys.stdout.write('\033[J')
            # print(f"{Colors.GREEN}✓ Visualization complete{Colors.END}")
            
            # Decrypt the test file
            self.decrypt_file("crypto_test.txt.enc")
            print(f"{Colors.GREEN}✓ Decryption successful{Colors.END}")
            
            # Verify integrity
            with open(test_file, "r") as f:
                content = f.read()
            print(f"{Colors.CYAN}✓ Data integrity verified{Colors.END}")
            
            # Generate test report
            print(f"{Colors.YELLOW}📊 Generating test report...{Colors.END}")
            key_info = self.get_key_info()
            report_details = {
                'target': 'Test File',
                'total_files': 1,
                'total_size': self.human_readable_size(os.path.getsize(test_file)),
                'files': [
                    {'name': 'crypto_test.txt', 'status': 'Encrypted → Decrypted', 
                    'size': self.human_readable_size(os.path.getsize(test_file))}
                ],
                'key_info': key_info,
                'test_mode': True
            }
            self.report_gen.generate_report("ENCRYPTION TEST", report_details)
        
        # Cleanup
        for f in [test_file, enc]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                    print(f"{Colors.DIM}✓ Cleaned up: {f}{Colors.END}")
                except:
                    pass
        
        self.add_activity("Encryption test completed")
        print(f"\n{Colors.GREEN}PROCESS SUCCESSFUL!{Colors.END}")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        
    def decrypt_test(self):
        """Run decryption test with typing effects and report generation"""
        PlatformUtils.clear_screen()
        self.typer.type_text("DECRYPTION SYSTEM TEST", color=Colors.YELLOW, newline=True)
        self.typer.type_text("═══════════════════════════════════════════════════════", color=Colors.RED, newline=True)

        # Check if there are encrypted files to test with
        encrypted_files = []
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith(".enc"):
                    encrypted_files.append(os.path.join(root, file))
        
        if not encrypted_files:
            self.typer.type_text("⚠️ No encrypted files found to test decryption.", color=Colors.YELLOW)
            self.typer.type_text("Run 'Encrypt Test' first to create a test file.", color=Colors.CYAN)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        self.typer.type_text(f"📁 Found {len(encrypted_files)} encrypted files", color=Colors.CYAN)
        time.sleep(1.5)
        
        # Test decrypt the first encrypted file
        test_file = encrypted_files[0]
        self.typer.type_text(f"🔓 Testing decryption on: {os.path.basename(test_file)}", color=Colors.GREEN)
        time.sleep(1.5)
        
        self.animate_encryption(os.path.basename(test_file), "DECRYPTING")
        
        # Decrypt the file
        self.decrypt_file(os.path.basename(test_file))
        
        # Check if decryption was successful
        decrypted_file = test_file.replace(".enc", "")
        if os.path.exists(decrypted_file):
            self.typer.type_text("✅ Decryption test successful!", color=Colors.GREEN)
            
            # Generate test report
            self.typer.type_text("📊 Generating test report...", color=Colors.YELLOW)
            key_info = self.get_key_info()
            report_details = {
                'target': os.path.basename(test_file),
                'total_files': 1,
                'total_size': self.human_readable_size(os.path.getsize(decrypted_file)),
                'files': [
                    {'name': os.path.basename(decrypted_file), 'status': 'Decrypted', 
                    'size': self.human_readable_size(os.path.getsize(decrypted_file))}
                ],
                'key_info': key_info,
                'test_mode': True
            }
            self.report_gen.generate_report("DECRYPTION TEST", report_details)
            
            # Cleanup (remove decrypted file)
            try:
                os.remove(decrypted_file)
                self.typer.type_text(f"✓ Cleaned up: {os.path.basename(decrypted_file)}", color=Colors.DIM)
            except:
                pass
        else:
            self.typer.type_text("❌ Decryption test failed!", color=Colors.RED)
        
        self.add_activity("Decryption test completed")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        
    def encrypt_file(self, filename):
        if not self.cipher:
            self.typer.type_text("[!] Encryption not initialized", color=Colors.RED)
            return

        path = os.path.join(self.base_dir, filename)
        path = os.path.normpath(path)  # Normalize path

        if not os.path.exists(path):
            self.typer.type_text("[!] File not found", color=Colors.RED)
            return
        
        # Show animation during encryption
        self.animate_encryption(filename, "ENCRYPTING")

        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            self.typer.type_text(f"[!] Failed to read file: {e}", color=Colors.RED)
            return
        
        original_size = len(data)
        
        try:
            encrypted = self.cipher.encrypt(data)
        except Exception as e:
            self.typer.type_text(f"[!] Encryption failed: {e}", color=Colors.RED)
            return
        
        enc_file = path + ".enc"
        
        try:
            with open(enc_file, "wb") as f:
                f.write(encrypted)
        except Exception as e:
            self.typer.type_text(f"[!] Failed to write encrypted file: {e}", color=Colors.RED)
            return
        
        encrypted_size = len(encrypted)
        
        print(f"\n{Colors.GREEN}✅ File encrypted successfully!{Colors.END}")
        print(f"   Output: {enc_file}")
        print(f"   Original: {self.human_readable_size(original_size)} → Encrypted: {self.human_readable_size(encrypted_size)}")
        
        # Verify encrypted file is valid - FIXED
        try:
            # First check if the file exists and has content
            if not os.path.exists(enc_file):
                raise Exception("Encrypted file not created")
            
            file_size = os.path.getsize(enc_file)
            if file_size == 0:
                raise Exception("Encrypted file is empty")
            
            # Read the entire encrypted file to verify
            with open(enc_file, 'rb') as f:
                full_encrypted_data = f.read()
            
            # Try to decrypt the full data
            test_decrypt = self.cipher.decrypt(full_encrypted_data)
            
            # Verify the decrypted data matches the original
            if test_decrypt == data:
                print(f"{Colors.GREEN}✓ Encryption verified successfully!{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Verification warning: Decrypted data doesn't match original{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}❌ Encryption verification failed: {str(e)}{Colors.END}")
            print(f"{Colors.YELLOW}⚠️  Encrypted file may be corrupted. Keeping original file.{Colors.END}")
            # Delete the potentially corrupted encrypted file
            try:
                if os.path.exists(enc_file):
                    os.remove(enc_file)
                    print(f"{Colors.DIM}✓ Removed corrupted encrypted file{Colors.END}")
            except:
                pass
            return
        
        # Simple deletion option
        print(f"\n{Colors.YELLOW}Delete original file?{Colors.END}")
        print(f"  {Colors.DIM}Warning: This is irreversible!{Colors.END}")
        choice = input(f"{Colors.CYAN}Delete original? (y/N): {Colors.END}").strip().lower()

        if choice == 'y':
            # Show the file path clearly
            print(f"\n{Colors.YELLOW}File to delete: {path}{Colors.END}")
            verify = input(f"{Colors.RED}⚠️  Confirm deletion of {os.path.basename(path)}? (yes/NO): {Colors.END}").strip().lower()
            if verify == 'yes':
                # Try to close any handles to the file
                import gc
                gc.collect()
                
                # Wait a moment for any locks to clear
                time.sleep(0.5)
                
                print(f"{Colors.YELLOW}🔒 Securely deleting original...{Colors.END}")
                
                # Try secure delete first
                success = self.secure_delete(path, passes=3)
                
                # If secure delete failed, try force delete on Windows
                if not success and platform.system() == 'Windows':
                    print(f"{Colors.YELLOW}🔄 Secure delete failed. Attempting force delete...{Colors.END}")
                    if self.force_delete_file_windows(path):
                        success = True
                
                # Final verification
                if success and not os.path.exists(path):
                    print(f"{Colors.GREEN}✓ Original file securely deleted{Colors.END}")
                    self.add_activity(f"Securely deleted original: {filename}")
                else:
                    # If file still exists, try one more time
                    if os.path.exists(path):
                        print(f"{Colors.RED}❌ File still exists!{Colors.END}")
                        print(f"{Colors.YELLOW}⚠️  Original file kept for safety{Colors.END}")
                        # Try to open the file to see what's holding it
                        try:
                            import psutil
                            for proc in psutil.process_iter(['pid', 'name']):
                                try:
                                    for item in proc.open_files():
                                        if path.lower() in item.path.lower():
                                            print(f"{Colors.DIM}   File is open in: {proc.info['name']} (PID: {proc.info['pid']}){Colors.END}")
                                            break
                                except:
                                    pass
                        except:
                            pass
            else:
                print(f"{Colors.GREEN}✓ Original file kept (user cancelled){Colors.END}")
        else:
            print(f"{Colors.GREEN}✓ Original file kept (safe){Colors.END}")
        
        # Generate report
        self.typer.type_text("📊 Generating report...", color=Colors.YELLOW)
        key_info = self.get_key_info()
        report_details = {
            'target': filename,
            'total_files': 1,
            'total_size': self.human_readable_size(original_size),
            'files': [{'name': filename, 'status': 'Encrypted', 'size': self.human_readable_size(original_size)}],
            'key_info': key_info,
            'original_deleted': choice == 'y' and verify == 'yes'
        }
        self.report_gen.generate_report("FILE ENCRYPTION", report_details)
        
    def decrypt_file(self, filename):
        """Decrypt file with Matrix rain visualization"""
        
        if not self.cipher:
            self.typer.type_text("[!] Encryption not initialized", color=Colors.RED)
            return

        path = os.path.join(self.base_dir, filename)

        if not os.path.exists(path):
            self.typer.type_text("[!] File not found", color=Colors.RED)
            return
        
        # Show animation with Matrix rain for decryption
        print(f"\n{Colors.YELLOW}🔓 DECRYPTING FILE: {filename}{Colors.END}")
        
        with open(path, "rb") as f:
            data = f.read()

        try:
            decrypted = self.cipher.decrypt(data)
            out_file = path.replace(".enc", "")
            
            with open(out_file, "wb") as f:
                f.write(decrypted)
            
            self.add_activity(f"Decrypted: {filename}")
            
            print(f"\n{Colors.GREEN}✅ File decrypted successfully!{Colors.END}")
            print(f"   Output: {out_file}")
            
            # Show 60-second Matrix rain for decryption
            print(f"\n{Colors.MAGENTA}╔════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.MAGENTA}║              DECRYPTION MODE                                                 ║{Colors.END}")
            print(f"{Colors.MAGENTA}║           Visualizing data flow                                              ║{Colors.END}")
            print(f"{Colors.MAGENTA}╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            self.show_matrix_rain_animated(duration=60, height=10, width=80)
                        
            # Generate report
            self.typer.type_text("📊 Generating report...", color=Colors.YELLOW)
            key_info = self.get_key_info()
            report_details = {
                'target': filename,
                'total_files': 1,
                'total_size': self.human_readable_size(len(decrypted)),
                'files': [{'name': out_file, 'status': 'Decrypted', 'size': self.human_readable_size(len(decrypted))}],
                'key_info': key_info
            }
            self.report_gen.generate_report("FILE DECRYPTION", report_details)
            
        except Exception as e:
            self.typer.type_text(f"❌ Decryption failed: {e}", color=Colors.RED)
                
    def encrypt_directory(self):
        print(f"\n{Colors.YELLOW}📂 DIRECTORY ENCRYPTION{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")
        
        if not self.cipher:
            self.typer.type_text("❌ Encryption not initialized. Setup encryption first.", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        directory_path = input(f"{Colors.CYAN}Enter directory path to encrypt: {Colors.END}").strip()
        
        if not directory_path:
            self.typer.type_text("❌ No directory specified", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        directory_path = os.path.expanduser(directory_path)
        
        if not os.path.exists(directory_path):
            self.typer.type_text(f"❌ Directory not found: {directory_path}", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        if not os.path.isdir(directory_path):
            self.typer.type_text(f"❌ Path is not a directory: {directory_path}", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        # Get ALL files in directory for tracking
        all_files = []
        total_size = 0
        for root, dirs, files in os.walk(directory_path):
            for f in files:
                try:
                    file_path = os.path.join(root, f)
                    size = os.path.getsize(file_path)
                    all_files.append(file_path)
                    total_size += size
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠️  Could not read: {file_path} - {e}{Colors.END}")
        
        total_files = len(all_files)
        
        print(f"📂 Directory: {directory_path}")
        print(f"📁 Files: {total_files}")
        print(f"📊 Size: {self.human_readable_size(total_size)}")
        
        # Ask about deletion BEFORE encryption
        print(f"\n{Colors.YELLOW}⚠️  After encryption, original files will remain unless deleted{Colors.END}")
        print(f"{Colors.CYAN}Deletion options:{Colors.END}")
        print(f"  1. Keep all original files (safe)")
        print(f"  2. Securely delete ALL original files after encryption (irreversible)")
        print(f"  3. Ask for each file individually (recommended for large directories)")
        print(f"  4. Skip deletion (keep all files)")
        
        delete_choice = input(f"\n{Colors.YELLOW}Choose option [1-4]: {Colors.END}").strip()
        
        if delete_choice not in ['1', '2', '3', '4']:
            delete_choice = '1'
            print(f"{Colors.YELLOW}Defaulting to 'Keep all files'{Colors.END}")
        
        confirm = input(f"\n{Colors.RED}⚠️  Encrypt this directory? (y/N): {Colors.END}").strip().lower()
        if confirm != 'y':
            self.typer.type_text("Encryption cancelled", color=Colors.YELLOW)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        # Show animation
        self.animate_directory_encryption(directory_path, total_files, "ENCRYPTING")
        
        # Track successfully encrypted files
        encrypted_files = []
        
        def progress_callback(current, total, filename):
            if current % 10 == 0 or current == total:
                print(f"  [{current}/{total}] {filename}")
                encrypted_files.append(filename)
        
        # Perform encryption - get both success and container_path
        success, container_path = self.dir_encryptor.encrypt_directory(directory_path, progress_callback)
        
        if success:
            print(f"\n{Colors.GREEN}✅ Directory encryption completed successfully!{Colors.END}")
            if container_path:
                print(f"   Container: {container_path}")
            
            # Handle deletion based on choice
            if delete_choice == '2':
                # Delete ALL original files
                self._delete_original_directory_files(directory_path, all_files, "all")
            elif delete_choice == '3':
                # Ask for each file individually
                self._delete_original_directory_files(directory_path, all_files, "individual")
            else:
                print(f"{Colors.GREEN}✓ Original files kept (safe){Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Directory encryption failed{Colors.END}")
            print(f"{Colors.YELLOW}⚠️  Original files kept for safety{Colors.END}")
            
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        
    def decrypt_directory(self):
        """Decrypt directory with 1-minute Matrix rain visualization"""
        
        # Don't clear screen - work within the dashboard
        print(f"\n{Colors.YELLOW}📂 DIRECTORY DECRYPTION{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")
        
        if not self.cipher:
            self.typer.type_text("❌ Decryption not initialized. Setup encryption first.", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        containers = self.dir_encryptor.list_encrypted_directories()
        
        if not containers:
            self.typer.type_text("❌ No encrypted directories found", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        print(f"\n{Colors.GREEN}Available encrypted containers:{Colors.END}")
        for idx, container in enumerate(containers, 1):
            format_info = f" ({container.get('format', 'Unknown')})" if container.get('format') else ""
            print(f"  {idx}. {container['name']}{format_info} ({container['size_human']})")
        
        choice = input(f"\n{Colors.CYAN}Select container [1-{len(containers)}] or enter path: {Colors.END}").strip()
        
        container_path = None
        if choice.isdigit() and 1 <= int(choice) <= len(containers):
            container_path = containers[int(choice) - 1]['path']
        elif os.path.exists(choice):
            container_path = choice
        else:
            self.typer.type_text("❌ Invalid selection", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        print(f"{Colors.CYAN}📦 Container:{Colors.END} {container_path}")
        print(f"{Colors.CYAN}📁 Size:{Colors.END} {self.human_readable_size(os.path.getsize(container_path))}")
        
        confirm = input(f"\n{Colors.RED}⚠️  Decrypt this container? (y/N): {Colors.END}").strip().lower()
        if confirm != 'y':
            self.typer.type_text("Decryption cancelled", color=Colors.YELLOW)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        output_dir = input(f"{Colors.CYAN}Output directory (press ENTER for default): {Colors.END}").strip()
        if not output_dir:
            output_dir = None
        else:
            output_dir = os.path.expanduser(output_dir)
        
        # Show animation with 60-second Matrix rain for decryption
        self.animate_directory_encryption(container_path, 1, "DECRYPTING")
        
        success = self.dir_encryptor.decrypt_directory(container_path, output_dir)
        
        if success:
            print(f"\n{Colors.GREEN}✅ Directory decryption completed successfully!{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Directory decryption failed{Colors.END}")
        
        # Wait for user input, but DON'T clear the screen
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        
        # Update stats and refresh dashboard (but don't clear again)
        self.update_stats()
    
    def list_encrypted_dirs(self):
        """List encrypted directories - Calls DirectoryEncryptor method"""
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " ENCRYPTED DIRECTORIES ")
        
        # Call the method from DirectoryEncryptor
        containers = self.dir_encryptor.list_encrypted_directories()
        
        if not containers:
            content = [f"{Colors.YELLOW}No encrypted directories found.{Colors.END}"]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        headers = ["#", "Container", "Size", "Modified", "Format"]
        rows = []
        
        for i, container in enumerate(containers, 1):
            rows.append([
                f"{i}",
                f"📦 {container['name'][:30]}",
                container['size_human'],
                container['modified'],
                container.get('format', 'Unknown')
            ])
        
        table = AnimatedTable(headers)
        table.render(rows, with_typing=True)
        
        self.typer.type_text(f"Total containers: {len(containers)}", color=Colors.CYAN)
        self.typer.type_text(f"Location: {ENCRYPTED_DIR}", color=Colors.DIM)
        
        self.add_activity("Listed encrypted directories")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        
    def crypto_list(self):
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " ENCRYPTED FILES INVENTORY ")
        
        encrypted = []
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith(".enc"):
                    path = os.path.join(root, file)
                    encrypted.append(path)

        if not encrypted:
            content = [f"{Colors.YELLOW}No encrypted files found.{Colors.END}"]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return

        headers = ["#", "File", "Size", "Modified"]
        rows = []
        
        for i, file in enumerate(encrypted, 1):
            size = self.human_readable_size(os.path.getsize(file))
            mod = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M")
            filename = os.path.basename(file)
            if len(filename) > 20:
                filename = filename[:17] + "..."
            rows.append([f"{i}", f"🔒 {filename}", size, mod])
        
        table = AnimatedTable(headers)
        table.render(rows, with_typing=True)
        self.add_activity("Listed encrypted files")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def crypto_info(self, filename=None):
        PlatformUtils.clear_screen()
        
        if not filename:
            filename = input(f"{Colors.CYAN}Encrypted file: {Colors.END}").strip()

        if not filename.endswith(".enc"):
            filename += ".enc"

        path = os.path.join(self.base_dir, filename)

        if not os.path.exists(path):
            self.typer.type_text("[!] File not found", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return

        box = RotatingBox(60, " ENCRYPTION INFO ")
        
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            data = f.read()

        sha256 = hashlib.sha256(data).hexdigest()
        md5 = hashlib.md5(data).hexdigest()

        content = [
            f"{Colors.BOLD}File:{Colors.END} {filename}",
            f"{Colors.BOLD}Path:{Colors.END} {path}",
            f"{Colors.BOLD}Size:{Colors.END} {self.human_readable_size(size)}",
            f"{Colors.BOLD}SHA256:{Colors.END} {sha256[:32]}...",
            f"{Colors.BOLD}MD5:{Colors.END} {md5[:16]}..."
        ]
        box.render(content, color=Colors.CYAN, with_typing=True)

        self.typer.type_text("🔍 Encryption Analysis", color=Colors.YELLOW)
        self.typer.type_text("──────────────────────────────────────────────────", color=Colors.CYAN)
        
        try:
            base64.urlsafe_b64decode(data)
            self.typer.type_text("✓ Format: Fernet (AES-256)", color=Colors.GREEN)
        except Exception:
            self.typer.type_text("✗ Format: Unknown", color=Colors.RED)

        self.typer.type_text("🛡️ Integrity Check", color=Colors.YELLOW)
        self.typer.type_text("──────────────────────────────────────────────────", color=Colors.CYAN)

        if not self.cipher:
            self.typer.type_text("⚠️ Key not loaded — cannot verify integrity", color=Colors.RED)
        else:
            try:
                self.cipher.decrypt(data)
                self.typer.type_text("✅ File integrity: VALID", color=Colors.GREEN)
                self.typer.type_text("   Authentication tag verified", color=Colors.CYAN)
            except Exception:
                self.typer.type_text("❌ File integrity: FAILED", color=Colors.RED)

        self.add_activity(f"Checked info for: {filename}")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def crypto_verify(self):
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " SYSTEM VERIFICATION ")
        
        checks = []
        
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE) as f:
                key = f.read().strip()
            try:
                Fernet(key.encode())
                checks.append(f"{Colors.GREEN}✓ Key format valid{Colors.END}")
            except:
                checks.append(f"{Colors.RED}✗ Invalid key{Colors.END}")
        else:
            checks.append(f"{Colors.RED}✗ Key file missing{Colors.END}")

        if self.cipher:
            checks.append(f"{Colors.GREEN}✓ Cipher initialized{Colors.END}")
            
            test = b"dsterminal test data"
            try:
                enc = self.cipher.encrypt(test)
                dec = self.cipher.decrypt(enc)
                if test == dec:
                    checks.append(f"{Colors.GREEN}✓ Self-test PASSED{Colors.END}")
                else:
                    checks.append(f"{Colors.RED}✗ Self-test FAILED{Colors.END}")
            except:
                checks.append(f"{Colors.RED}✗ Encryption test failed{Colors.END}")
        else:
            checks.append(f"{Colors.RED}✗ Cipher not initialized{Colors.END}")

        if os.path.exists(QR_CODE_DIR):
            checks.append(f"{Colors.GREEN}✓ QR directory exists{Colors.END}")
        else:
            checks.append(f"{Colors.YELLOW}⚠️ QR directory not found{Colors.END}")
        
        if os.path.exists(ENCRYPTED_DIR):
            checks.append(f"{Colors.GREEN}✓ Encrypted dir storage exists{Colors.END}")
        else:
            checks.append(f"{Colors.YELLOW}⚠️ Encrypted dir storage not found{Colors.END}")
        
        if os.path.exists(REPORTS_DIR):
            checks.append(f"{Colors.GREEN}✓ Reports directory exists{Colors.END}")
        else:
            checks.append(f"{Colors.YELLOW}⚠️ Reports directory not found{Colors.END}")
        
        if QR_DEPS_AVAILABLE:
            checks.append(f"{Colors.GREEN}✓ QR dependencies installed{Colors.END}")
        else:
            checks.append(f"{Colors.RED}✗ QR dependencies missing{Colors.END}")
        
        if REPORT_AVAILABLE:
            checks.append(f"{Colors.GREEN}✓ Report generation enabled{Colors.END}")
        else:
            checks.append(f"{Colors.RED}✗ Report generation unavailable{Colors.END}")
        
        box.render(checks, color=Colors.YELLOW, with_typing=True)
        self.add_activity("System verification completed")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def crypto_backup(self):
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " KEY BACKUP ")
        
        if not os.path.exists(KEY_FILE):
            content = [f"{Colors.RED}No key found to backup{Colors.END}"]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return

        with open(KEY_FILE) as f:
            key = f.read()

        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR, mode=0o700, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = os.path.join(BACKUP_DIR, f"dsterminal_key_{timestamp}.backup")
        
        self.typer.type_text("▶ Creating secure backup...", color=Colors.YELLOW)
        time.sleep(1)
        
        with open(backup, "w") as f:
            f.write(key)
        
        try:
            os.chmod(backup, 0o600)
        except:
            pass
        
        content = [
            f"{Colors.GREEN}✅ Backup created successfully{Colors.END}",
            f"{Colors.BOLD}Location:{Colors.END} {backup}",
            f"{Colors.BOLD}Permissions:{Colors.END} 600",
            "",
            f"{Colors.YELLOW}⚠️ Store this backup securely!{Colors.END}",
            f"{Colors.CYAN}💡 Consider generating a QR code backup too{Colors.END}"
        ]
        box.render(content, color=Colors.GREEN, with_typing=True)
        self.add_activity("Key backup created")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def import_encryption_key(self, key_string=None):
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " IMPORT ENCRYPTION KEY ")
        
        if not key_string:
            self.typer.type_text("▶ Paste the encryption key you received:", color=Colors.YELLOW)
            self.typer.type_text("  (The key looks like: gAAAAAB...)", color=Colors.CYAN)
            key_string = input(f"\n{Colors.GREEN}Key: {Colors.END}").strip()
        
        try:
            test_cipher = Fernet(key_string.encode())
            test_data = b"DSTerminal_key_import_test"
            encrypted = test_cipher.encrypt(test_data)
            decrypted = test_cipher.decrypt(encrypted)
            
            if test_data == decrypted:
                key_dir = os.path.dirname(KEY_FILE)
                if not os.path.exists(key_dir):
                    os.makedirs(key_dir, mode=0o700, exist_ok=True)
                
                with open(KEY_FILE, "w") as f:
                    f.write(key_string)
                
                try:
                    os.chmod(KEY_FILE, 0o600)
                except:
                    pass
                
                self.cipher = Fernet(key_string.encode())
                
                key_id = hashlib.sha256(key_string.encode()).hexdigest()[:16]
                
                content = [
                    f"{Colors.GREEN}✅ ENCRYPTION KEY IMPORTED SUCCESSFULLY{Colors.END}",
                    f"{Colors.BOLD}Key ID:{Colors.END} {Colors.CYAN}{key_id}{Colors.END}",
                    f"{Colors.BOLD}Location:{Colors.END} {KEY_FILE}",
                    "",
                    f"{Colors.GREEN}✓ You can now decrypt files encrypted with this key{Colors.END}"
                ]
                box.render(content, color=Colors.GREEN, with_typing=True)
                
                self.add_activity("Key imported from string")
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                return True
            else:
                raise ValueError("Test decryption failed")
                
        except Exception as e:
            content = [
                f"{Colors.RED}❌ INVALID KEY FORMAT{Colors.END}",
                "",
                f"{Colors.YELLOW}The key you provided is not valid.{Colors.END}",
                f"{Colors.CYAN}Make sure you copied the ENTIRE key string.{Colors.END}",
                "",
                f"{Colors.RED}Error: {str(e)}{Colors.END}"
            ]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return False

    def export_encryption_key(self):
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " EXPORT ENCRYPTION KEY ")
        
        if not os.path.exists(KEY_FILE):
            content = [
                f"{Colors.RED}❌ No encryption key found{Colors.END}",
                f"{Colors.YELLOW}Run 'Setup Encryption System' first.{Colors.END}"
            ]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        with open(KEY_FILE, "r") as f:
            key = f.read().strip()
        
        key_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        
        content = [
            f"{Colors.GREEN}✅ YOUR ENCRYPTION KEY{Colors.END}",
            f"{Colors.BOLD}Key ID:{Colors.END} {Colors.CYAN}{key_id}{Colors.END}",
            "",
            f"{Colors.YELLOW}╔════════════════════════════════════════════════════════╗{Colors.END}",
            f"{Colors.BOLD}{key}{Colors.END}",
            f"{Colors.YELLOW}╚════════════════════════════════════════════════════════╝{Colors.END}",
            "",
            f"{Colors.RED}⚠️  COPY THIS KEY EXACTLY AS SHOWN ABOVE{Colors.END}",
            f"{Colors.RED}⚠️  Share it securely with the recipient{Colors.END}",
            "",
            f"{Colors.CYAN}The recipient should use 'Import Key' option{Colors.END}",
            f"{Colors.CYAN}💡 Or use QR code export for easier sharing{Colors.END}"
        ]
        box.render(content, color=Colors.YELLOW, with_typing=True)
        
        if PlatformUtils.copy_to_clipboard(key):
            self.typer.type_text("✓ Key copied to clipboard!", color=Colors.GREEN)
        else:
            self.typer.type_text("Tip: Install 'pyperclip' for auto-copy: pip install pyperclip", color=Colors.YELLOW)
        
        self.add_activity("Key exported")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def list_reports(self):
        """List all generated reports"""
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " REPORT INVENTORY ")
        
        if not os.path.exists(REPORTS_DIR):
            content = [f"{Colors.YELLOW}Reports directory not found: {REPORTS_DIR}{Colors.END}"]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        reports = []
        for f in os.listdir(REPORTS_DIR):
            if f.endswith('.pdf') or f.endswith('.html'):
                full_path = os.path.join(REPORTS_DIR, f)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                reports.append({
                    'name': f,
                    'path': full_path,
                    'size': self.human_readable_size(size),
                    'modified': modified.strftime("%Y-%m-%d %H:%M:%S"),
                    'type': 'PDF' if f.endswith('.pdf') else 'HTML'
                })
        
        if not reports:
            content = [f"{Colors.YELLOW}No reports found.{Colors.END}"]
            box.render(content, color=Colors.RED, with_typing=True)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        headers = ["#", "File", "Type", "Size", "Modified"]
        rows = []
        
        for i, report in enumerate(sorted(reports, key=lambda x: x['modified'], reverse=True), 1):
            rows.append([
                f"{i}",
                f"📄 {report['name'][:30]}",
                report['type'],
                report['size'],
                report['modified']
            ])
        
        table = AnimatedTable(headers)
        table.render(rows, with_typing=True)
        
        self.typer.type_text(f"Total reports: {len(reports)}", color=Colors.CYAN)
        self.typer.type_text(f"Location: {REPORTS_DIR}", color=Colors.DIM)
        
        self.add_activity("Listed reports")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def qr_generate(self):
        self.qr_manager.export_key_as_qr()
        self.add_activity("QR code generated")
    
    def qr_import(self):
        self.qr_manager.import_key_from_qr()
        self.add_activity("QR code imported")
    
    def qr_list(self):
        self.qr_manager.list_qr_codes()
        self.add_activity("Listed QR codes")
    
    def qr_restore(self):
        self.qr_manager.restore_key_from_backup_qr()
        self.add_activity("Emergency restore attempted")
    
    def _delete_encrypted_originals(self, directory_path, file_list, mode="all"):
        """Delete original files after encryption with safety checks"""
        
        print(f"\n{Colors.YELLOW}🔒 Processing original file deletion...{Colors.END}")
        
        deleted_count = 0
        kept_count = 0
        
        for file_info in file_list:
            original_path = file_info['path']
            encrypted_path = original_path + '.enc'
            
            # Verify encrypted file exists
            if not os.path.exists(encrypted_path):
                print(f"{Colors.YELLOW}⚠️  Encrypted version not found for: {original_path}{Colors.END}")
                kept_count += 1
                continue
            
            # Verify encrypted file has content
            if os.path.getsize(encrypted_path) == 0:
                print(f"{Colors.RED}❌ Encrypted file is empty for: {original_path}{Colors.END}")
                kept_count += 1
                continue
            
            # Ask individually if mode is 'individual'
            if mode == "individual":
                print(f"\n{Colors.CYAN}File: {original_path}{Colors.END}")
                print(f"  Size: {self.human_readable_size(file_info['size'])}")
                choice = input(f"{Colors.YELLOW}Delete original? (y/N/keep all/delete all): {Colors.END}").strip().lower()
                
                if choice == 'keep all':
                    mode = "none"
                    break
                elif choice == 'delete all':
                    mode = "all"
                elif choice != 'y':
                    print(f"{Colors.GREEN}✓ Keeping: {original_path}{Colors.END}")
                    kept_count += 1
                    continue
            
            if mode == "all" or mode == "individual" and choice == 'y':
                # Secure delete the original file
                try:
                    # Verify encryption integrity first
                    with open(encrypted_path, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Test decrypt a small portion to verify
                    test_data = self.cipher.decrypt(encrypted_data[:min(1024, len(encrypted_data))])
                    
                    print(f"{Colors.YELLOW}🔒 Securely deleting: {os.path.basename(original_path)}{Colors.END}")
                    self.secure_delete(original_path, passes=3)
                    
                    if not os.path.exists(original_path):
                        deleted_count += 1
                        print(f"{Colors.GREEN}✓ Deleted: {os.path.basename(original_path)}{Colors.END}")
                        self.add_activity(f"Securely deleted original: {os.path.basename(original_path)}")
                    else:
                        print(f"{Colors.RED}❌ Failed to delete: {os.path.basename(original_path)}{Colors.END}")
                        kept_count += 1
                        
                except Exception as e:
                    print(f"{Colors.RED}❌ Error deleting {original_path}: {e}{Colors.END}")
                    kept_count += 1
        
        print(f"\n{Colors.GREEN}📊 Deletion Summary:{Colors.END}")
        print(f"  {Colors.GREEN}✓ Deleted: {deleted_count} files{Colors.END}")
        print(f"  {Colors.YELLOW}⚠️  Kept: {kept_count} files{Colors.END}")

    def _delete_original_directory_files(self, directory_path, all_files, mode="all"):
        """Delete original files after directory encryption with robust deletion"""
        
        print(f"\n{Colors.YELLOW}🔒 Processing original file deletion...{Colors.END}")
        print(f"{Colors.DIM}Total files to process: {len(all_files)}{Colors.END}")
        
        # Get the encrypted container name
        dir_name = os.path.basename(directory_path)
        encrypted_dir = ENCRYPTED_DIR
        
        # Find the most recent encrypted container for this directory (any format)
        containers = []
        if os.path.exists(encrypted_dir):
            for f in os.listdir(encrypted_dir):
                # Support all formats
                if (f.startswith(dir_name) and 
                    (f.endswith('.enc_dir') or 
                    f.endswith('.enc_dir.zip') or 
                    f.endswith('.enc_dir.tar.gz') or 
                    f.endswith('.enc_dir.tgz'))):
                    full_path = os.path.join(encrypted_dir, f)
                    containers.append({
                        'name': f,
                        'path': full_path,
                        'mtime': os.path.getmtime(full_path)
                    })
        
        if not containers:
            print(f"{Colors.RED}❌ No encrypted container found for this directory!{Colors.END}")
            print(f"{Colors.YELLOW}⚠️  Original files kept for safety{Colors.END}")
            return
        
        # Use the most recent container
        latest = sorted(containers, key=lambda x: x['mtime'], reverse=True)[0]
        container_path = latest['path']
        
        # Detect format
        if latest['name'].endswith('.zip'):
            fmt = "ZIP"
        elif latest['name'].endswith('.tar.gz') or latest['name'].endswith('.tgz'):
            fmt = "TAR.GZ"
        else:
            fmt = "Unknown"
        
        print(f"{Colors.CYAN}📦 Found encrypted container: {os.path.basename(container_path)}{Colors.END}")
        print(f"{Colors.DIM}   Format: {fmt}{Colors.END}")
        
        # Verify container exists and has content
        if not os.path.exists(container_path) or os.path.getsize(container_path) == 0:
            print(f"{Colors.RED}❌ Encrypted container is invalid!{Colors.END}")
            print(f"{Colors.YELLOW}⚠️  Original files kept for safety{Colors.END}")
            return
        
        deleted_count = 0
        kept_count = 0
        skipped_count = 0
        failed_count = 0
        
        # Ask for confirmation before mass deletion
        if mode == "all" and len(all_files) > 10:
            print(f"\n{Colors.RED}⚠️  You are about to delete {len(all_files)} files!{Colors.END}")
            confirm = input(f"{Colors.RED}Type 'DELETE ALL' to confirm: {Colors.END}").strip()
            if confirm != 'DELETE ALL':
                print(f"{Colors.GREEN}✓ Deletion cancelled - all files kept{Colors.END}")
                return
        
        # Process each file
        for idx, file_path in enumerate(all_files, 1):
            # Get relative path for display
            rel_path = os.path.relpath(file_path, directory_path)
            
            # Check if this is a system file that shouldn't be deleted
            filename = os.path.basename(file_path)
            if filename in ['.DS_Store', 'Thumbs.db', 'desktop.ini']:
                print(f"{Colors.DIM}  ⏭ Skipping system file: {filename}{Colors.END}")
                skipped_count += 1
                continue
            
            # Ask individually if mode is 'individual'
            if mode == "individual":
                print(f"\n{Colors.CYAN}[{idx}/{len(all_files)}] File: {rel_path}{Colors.END}")
                print(f"  Size: {self.human_readable_size(os.path.getsize(file_path))}")
                choice = input(f"{Colors.YELLOW}Delete original? (y/N/a=delete all/k=keep all): {Colors.END}").strip().lower()
                
                if choice == 'a':
                    mode = "all"
                    print(f"{Colors.YELLOW}Switched to 'delete all' mode{Colors.END}")
                elif choice == 'k':
                    mode = "none"
                    print(f"{Colors.GREEN}Switched to 'keep all' mode{Colors.END}")
                    break
                elif choice != 'y':
                    print(f"{Colors.GREEN}✓ Keeping: {rel_path}{Colors.END}")
                    kept_count += 1
                    continue
            
            if mode == "all":
                # Try to delete the original file with multiple methods
                try:
                    print(f"{Colors.YELLOW}🔒 Deleting [{idx}/{len(all_files)}]: {rel_path}{Colors.END}")
                    
                    # First try secure delete
                    success = self.secure_delete(file_path, passes=3)
                    
                    # If secure delete failed, try force delete on Windows
                    if not success and platform.system() == 'Windows':
                        print(f"{Colors.YELLOW}🔄 Secure delete failed. Attempting force delete...{Colors.END}")
                        if self.force_delete_file_windows(file_path):
                            success = True
                    
                    # Verify deletion
                    if success and not os.path.exists(file_path):
                        deleted_count += 1
                        print(f"{Colors.GREEN}✓ Deleted: {rel_path}{Colors.END}")
                        self.add_activity(f"Securely deleted original: {rel_path}")
                    else:
                        # One more attempt with normal deletion
                        try:
                            os.remove(file_path)
                            time.sleep(0.1)
                            if not os.path.exists(file_path):
                                deleted_count += 1
                                print(f"{Colors.GREEN}✓ Deleted (normal): {rel_path}{Colors.END}")
                            else:
                                print(f"{Colors.RED}❌ Failed to delete: {rel_path}{Colors.END}")
                                failed_count += 1
                        except Exception as e2:
                            print(f"{Colors.RED}❌ Failed to delete: {rel_path} - {e2}{Colors.END}")
                            failed_count += 1
                            
                except Exception as e:
                    print(f"{Colors.RED}❌ Error deleting {rel_path}: {e}{Colors.END}")
                    failed_count += 1
        
        # Summary
        print(f"\n{Colors.GREEN}📊 Deletion Summary:{Colors.END}")
        print(f"  {Colors.GREEN}✓ Securely deleted: {deleted_count} files{Colors.END}")
        if failed_count > 0:
            print(f"  {Colors.RED}❌ Failed to delete: {failed_count} files{Colors.END}")
        if kept_count > 0:
            print(f"  {Colors.YELLOW}⚠️  Kept: {kept_count} files{Colors.END}")
        if skipped_count > 0:
            print(f"  {Colors.DIM}⏭ Skipped: {skipped_count} system files{Colors.END}")
        print(f"  {Colors.CYAN}📦 Encrypted container: {container_path}{Colors.END}")
        print(f"  {Colors.DIM}   Format: {fmt}{Colors.END}")
        
        if deleted_count > 0:
            print(f"\n{Colors.RED}⚠️  Remember: Deleted files are IRRECOVERABLE!{Colors.END}")
            print(f"{Colors.CYAN}💡 Keep your encryption key safe to access encrypted data{Colors.END}")
        
        # If many files failed, offer to retry
        if failed_count > 0:
            retry = input(f"\n{Colors.YELLOW}Some files failed to delete. Retry? (y/N): {Colors.END}").strip().lower()
            if retry == 'y':
                print(f"{Colors.CYAN}🔄 Retrying failed deletions...{Colors.END}")
                # Get list of files that still exist
                remaining = []
                for file_path in all_files:
                    if os.path.exists(file_path):
                        remaining.append(file_path)
                if remaining:
                    self._delete_remaining_files(remaining)
                            
    def secure_delete_with_verification(self, file_path, passes=3):
        """Secure delete with verification that file is actually gone"""
        
        if not os.path.exists(file_path):
            return False
        
        try:
            # Get file info before deletion
            original_size = os.path.getsize(file_path)
            original_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                original_hash.update(f.read())
            
            # Perform secure deletion
            self.secure_delete(file_path, passes)
            
            # Verify file is gone
            if not os.path.exists(file_path):
                print(f"{Colors.GREEN}✓ File securely deleted and verified{Colors.END}")
                self.deletion_log.append({
                    'file': file_path,
                    'size': original_size,
                    'hash': original_hash.hexdigest()[:16],
                    'timestamp': datetime.now().isoformat(),
                    'passes': passes
                })
                return True
            else:
                print(f"{Colors.RED}❌ File still exists after deletion attempt{Colors.END}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Secure deletion failed: {e}{Colors.END}")
            return False

    def secure_delete_windows(self, file_path, passes=3):
        """Windows-specific secure deletion using cipher or sdelete if available"""
        try:
            import subprocess
            
            # Try using Windows cipher command (built-in)
            try:
                # cipher /w:path - overwrites free space on the drive
                drive = os.path.splitdrive(file_path)[0] + "\\"
                subprocess.run(['cipher', '/w', drive], 
                            capture_output=True, 
                            timeout=60,
                            shell=True)
                print(f"{Colors.GREEN}✓ Used Windows cipher command{Colors.END}")
            except:
                pass
            
            # Fallback to manual overwrite
            self.secure_delete(file_path, passes)
            
        except Exception as e:
            print(f"{Colors.RED}❌ Windows secure deletion failed: {e}{Colors.END}")
            # Fallback to regular deletion
            try:
                os.remove(file_path)
                print(f"{Colors.GREEN}✓ File deleted (not securely){Colors.END}")
            except:
                pass
    
    def force_delete_file_windows(self, file_path):
        """Force delete a file on Windows using multiple methods"""
        if platform.system() != 'Windows':
            return False
        
        file_path = os.path.abspath(file_path)
        
        # Method 1: Try normal delete with retry
        for attempt in range(3):
            try:
                os.remove(file_path)
                time.sleep(0.1)
                if not os.path.exists(file_path):
                    print(f"{Colors.GREEN}✓ File deleted (attempt {attempt+1}){Colors.END}")
                    return True
            except:
                time.sleep(0.2)
        
        # Method 2: Use PowerShell
        try:
            import subprocess
            cmd = f'powershell -Command "Remove-Item -Path \'{file_path}\' -Force -ErrorAction SilentlyContinue"'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            time.sleep(0.2)
            if not os.path.exists(file_path):
                print(f"{Colors.GREEN}✓ File deleted via PowerShell{Colors.END}")
                return True
        except:
            pass
        
        # Method 3: Use Windows API via ctypes
        try:
            import ctypes
            from ctypes import wintypes
            
            # Try to delete on close
            GENERIC_WRITE = 0x40000000
            FILE_SHARE_READ = 0x00000001
            FILE_SHARE_WRITE = 0x00000002
            OPEN_EXISTING = 3
            FILE_FLAG_DELETE_ON_CLOSE = 0x04000000
            
            handle = ctypes.windll.kernel32.CreateFileW(
                file_path,
                GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                FILE_FLAG_DELETE_ON_CLOSE,
                None
            )
            
            if handle != -1:
                ctypes.windll.kernel32.CloseHandle(handle)
                time.sleep(0.2)
                if not os.path.exists(file_path):
                    print(f"{Colors.GREEN}✓ File deleted via Windows API{Colors.END}")
                    return True
        except:
            pass
        
        return False

    def _delete_remaining_files(self, remaining_files):
        """Delete files that survived the first deletion attempt"""
        
        print(f"\n{Colors.YELLOW}🔒 Attempting to delete {len(remaining_files)} remaining files...{Colors.END}")
        
        deleted_count = 0
        failed_count = 0
        
        for idx, file_path in enumerate(remaining_files, 1):
            rel_path = os.path.basename(file_path)
            print(f"{Colors.DIM}  [{idx}/{len(remaining_files)}] {rel_path}{Colors.END}")
            
            # Try force delete on Windows
            if platform.system() == 'Windows':
                if self.force_delete_file_windows(file_path):
                    deleted_count += 1
                    print(f"{Colors.GREEN}✓ Deleted: {rel_path}{Colors.END}")
                    continue
            
            # Try normal delete
            try:
                os.remove(file_path)
                time.sleep(0.1)
                if not os.path.exists(file_path):
                    deleted_count += 1
                    print(f"{Colors.GREEN}✓ Deleted: {rel_path}{Colors.END}")
                    continue
            except:
                pass
            
            # Try using secure delete as last resort
            try:
                if self.secure_delete(file_path, passes=1):
                    deleted_count += 1
                    print(f"{Colors.GREEN}✓ Deleted: {rel_path}{Colors.END}")
                    continue
            except:
                pass
            
            failed_count += 1
            print(f"{Colors.RED}❌ Could not delete: {rel_path}{Colors.END}")
        
        print(f"\n{Colors.GREEN}📊 Retry Summary:{Colors.END}")
        print(f"  {Colors.GREEN}✓ Deleted: {deleted_count} files{Colors.END}")
        if failed_count > 0:
            print(f"  {Colors.RED}❌ Still failed: {failed_count} files{Colors.END}")
            print(f"{Colors.YELLOW}💡 These files may be open in another program.{Colors.END}")
            print(f"{Colors.CYAN}   Close any programs that might be using them and try again.{Colors.END}")
            
if __name__ == "__main__":
    try:
        # Create and run the crypto engine
        crypto = CryptoEngine()
        crypto.main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}⚠️  Termination initiated{Colors.END}")
        time.sleep(1.5)
        sys.exit(0)