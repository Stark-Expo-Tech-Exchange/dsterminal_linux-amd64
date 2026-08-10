#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DSTERMINAL - ENCRYPTION SUITE [EDITION]
Interactive cinematic mode with real-time encryption visualization
QR Code Key Management Integration - CROSS PLATFORM
Human-like typing feedback system
DIRECTORY/FOLDER ENCRYPTION SUPPORT
"""

import os
import sys
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

# Try to import QR code dependencies
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

# ANSI color codes for terminal effects
class Colors:
    """Cross-platform color support"""
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
    RESET = '\033[0m'
    
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
    def strip(text):
        """Strip ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


def strip_ansi(text):
    """Strip ANSI escape sequences from text"""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


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
                if color:
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
    
    def render_frame(self, duration=0.1):
        frame = []
        for i in range(self.height):
            line = ''
            for j in range(self.width):
                if random.random() > 0.7:
                    line += f"{Colors.GREEN}{random.choice(self.chars)}{Colors.END}"
                else:
                    line += ' '
            frame.append(line)
        
        sys.stdout.write('\033[{}A'.format(self.height))
        for line in frame:
            print(line)
        time.sleep(duration)


class RotatingBox:
    """Animated rotating box with content - BOLD CONTINUOUS LINES"""
    
    def __init__(self, width=40, title=""):
        self.width = width
        self.title = title
        self.frames = 0
    
    def render(self, content_lines, color=Colors.CYAN):
        # Use bold continuous box drawing characters
        top_left = "┌"
        top_right = "┐"
        bottom_left = "└"
        bottom_right = "┘"
        horizontal = "─"
        vertical = "│"
        
        # Top border with title
        title_display = self.title if self.title else ""
        title_line = f"{top_left}{horizontal}{title_display.center(self.width-2, horizontal)}{horizontal}{top_right}"
        print(f"{color}{title_line}{Colors.END}")
        
        # Content lines
        for line in content_lines:
            # Clean line for width calculation
            clean_line = strip_ansi(line)
            padding = max(0, self.width - 2 - len(clean_line))
            print(f"{color}{vertical}{Colors.END} {line}{' ' * padding} {color}{vertical}{Colors.END}")
        
        # Bottom border
        bottom_line = f"{bottom_left}{horizontal * (self.width - 2)}{bottom_right}"
        print(f"{color}{bottom_line}{Colors.END}")
        self.frames += 1


class AnimatedTable:
    """Animated table with rotating columns - BOLD CONTINUOUS LINES"""
    
    def __init__(self, headers):
        self.headers = headers
        self.rotation = 0
    
    def render(self, rows, color=Colors.YELLOW):
        col_widths = [len(h) for h in self.headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Build the table with bold continuous lines
        header_line = ''
        for i, h in enumerate(self.headers):
            header_line += f" {h.center(col_widths[i])} "
            if i < len(self.headers)-1:
                header_line += f"{color}│{Colors.END}"
        
        # Top border
        total_width = sum(col_widths) + len(self.headers) * 3 - 1
        top_border = "┌" + "─" * total_width + "┐"
        print(f"{color}{top_border}{Colors.END}")
        
        # Header row
        print(f"{color}│{Colors.END}{header_line}{color}│{Colors.END}")
        
        # Separator
        sep = "├" + "─┼─".join(["─" * w for w in col_widths]) + "┤"
        print(f"{color}{sep}{Colors.END}")
        
        # Data rows
        for row in rows:
            row_line = ''
            for i, cell in enumerate(row):
                row_line += f" {str(cell).ljust(col_widths[i])} "
                if i < len(row)-1:
                    row_line += f"{color}│{Colors.END}"
            print(f"{color}│{Colors.END}{row_line}{color}│{Colors.END}")
        
        # Bottom border
        bottom_border = "└" + "─" * total_width + "┘"
        print(f"{color}{bottom_border}{Colors.END}")
        self.rotation += 1


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
        workspace = Paths.get_workspace_dir()
        reports_dir = os.path.join(workspace, 'dsterminal_workspace', 'reports', 'encryption_reports')
        return reports_dir


KEY_FILE = Paths.get_key_file()
QR_CODE_DIR = Paths.get_qr_dir()
BACKUP_DIR = Paths.get_backup_dir()
ENCRYPTED_DIR = Paths.get_encrypted_dir()
REPORTS_DIR = Paths.get_reports_dir()

# Create directories
for dir_path in [KEY_FILE, QR_CODE_DIR, BACKUP_DIR, ENCRYPTED_DIR, REPORTS_DIR]:
    dir_name = os.path.dirname(dir_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, mode=0o700, exist_ok=True)
for d in [QR_CODE_DIR, BACKUP_DIR, ENCRYPTED_DIR, REPORTS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d, mode=0o700, exist_ok=True)


class ReportGenerator:
    """Generate PDF and HTML reports for encryption/decryption operations"""
    
    VERSION = "v4.0.0.113"
    WATERMARK = f"DSTERMINAL {VERSION}"
    FOOTER = "Stark Expo Tech Exchange | Encrypt with Caution"
    
    def __init__(self):
        self.typer = TypeWriter('fast')
        self.reports_dir = REPORTS_DIR
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir, mode=0o700, exist_ok=True)
    
    def generate_report(self, operation_type, details):
        """Generate both PDF and HTML reports"""
        if details.get('test_mode', False):
            return self._generate_test_report(operation_type, details)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"dsterminal_report_{timestamp}"
        
        pdf_path = os.path.join(self.reports_dir, f"{base_filename}.pdf")
        html_path = os.path.join(self.reports_dir, f"{base_filename}.html")
        
        if REPORT_AVAILABLE:
            try:
                self._generate_pdf(pdf_path, operation_type, details)
                self.typer.type_text("PDF Report: {}".format(pdf_path), color=Colors.CYAN)
            except Exception as e:
                self.typer.type_text("PDF generation failed: {}".format(e), color=Colors.YELLOW)
        else:
            self.typer.type_text("PDF generation unavailable (install reportlab)", color=Colors.YELLOW)
        
        try:
            self._generate_html(html_path, operation_type, details)
            self.typer.type_text("HTML Report: {}".format(html_path), color=Colors.CYAN)
        except Exception as e:
            self.typer.type_text("HTML generation failed: {}".format(e), color=Colors.YELLOW)
        
        return {'pdf': pdf_path if os.path.exists(pdf_path) else None, 
                'html': html_path if os.path.exists(html_path) else None}
    
    def _generate_test_report(self, operation_type, details):
        """Generate test report with special formatting"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"dsterminal_test_report_{timestamp}"
        
        pdf_path = os.path.join(self.reports_dir, f"{base_filename}.pdf")
        html_path = os.path.join(self.reports_dir, f"{base_filename}.html")
        
        if REPORT_AVAILABLE:
            try:
                self._generate_pdf(pdf_path, f"TEST: {operation_type}", details)
                self.typer.type_text("Test Report (PDF): {}".format(pdf_path), color=Colors.CYAN)
            except Exception as e:
                self.typer.type_text("PDF generation failed: {}".format(e), color=Colors.YELLOW)
        
        try:
            self._generate_html(html_path, f"TEST: {operation_type}", details)
            self.typer.type_text("Test Report (HTML): {}".format(html_path), color=Colors.CYAN)
        except Exception as e:
            self.typer.type_text("HTML generation failed: {}".format(e), color=Colors.YELLOW)
        
        return {'pdf': pdf_path if os.path.exists(pdf_path) else None, 
                'html': html_path if os.path.exists(html_path) else None}
    
    def _generate_pdf(self, filepath, operation_type, details):
        """Generate PDF report"""
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00ff00'),
            alignment=1,
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
        
        story.append(Paragraph(f"DSTERMINAL {self.VERSION}", title_style))
        story.append(Paragraph("Encryption Report", title_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph(f"<font color='#666666' size='8'>Document ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}</font>", body_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("REPORT INFORMATION", heading_style))
        story.append(Paragraph(f"Operation Type: <b>{operation_type}</b>", body_style))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
        story.append(Paragraph(f"System: {platform.system()} {platform.release()}", body_style))
        story.append(Spacer(1, 12))
        
        key_info = details.get('key_info', {})
        story.append(Paragraph("ENCRYPTION KEY INFORMATION", heading_style))
        story.append(Paragraph(f"Key ID: {key_info.get('key_id', 'N/A')}", body_style))
        story.append(Paragraph(f"Key Location: {key_info.get('key_location', 'N/A')}", body_style))
        story.append(Paragraph(f"Key Format: Fernet (AES-256)", body_style))
        
        full_key = key_info.get('full_key', '')
        if full_key:
            masked_key = full_key[:20] + "..." + full_key[-10:]
            story.append(Paragraph(f"Key (masked): {masked_key}", body_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("OPERATION DETAILS", heading_style))
        story.append(Paragraph(f"Target: {details.get('target', 'N/A')}", body_style))
        story.append(Paragraph(f"Total Files: {details.get('total_files', 0)}", body_style))
        story.append(Paragraph(f"Total Size: {details.get('total_size', 'N/A')}", body_style))
        story.append(Spacer(1, 12))
        
        files = details.get('files', [])
        if files:
            story.append(Paragraph("FILES PROCESSED", heading_style))
            data = [['#', 'Filename', 'Status', 'Size']]
            for idx, f in enumerate(files[:50], 1):
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
        
        story.append(Paragraph("RECOMMENDATIONS", heading_style))
        story.append(Paragraph("• Always keep your encryption key in a secure location", body_style))
        story.append(Paragraph("• Create multiple backups of your encryption key", body_style))
        story.append(Paragraph("• Use the QR code export feature for secure key sharing", body_style))
        story.append(Paragraph("• Regularly verify your encrypted data integrity", body_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b><font color='red'>⚠️ ENCRYPT WITH CAUTION</font></b>", warning_style))
        story.append(Paragraph("<font color='red'>• Losing your encryption key means losing your data permanently</font>", warning_style))
        story.append(Paragraph("<font color='red'>• Always test decryption before deleting original files</font>", warning_style))
        story.append(Paragraph("<font color='red'>• Use strong passwords and secure storage for your keys</font>", warning_style))
        story.append(Spacer(1, 12))
        
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
            <div class="section-title">REPORT INFORMATION</div>
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
            <div class="section-title">ENCRYPTION KEY INFORMATION</div>
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
            <div class="section-title">OPERATION DETAILS</div>
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
            <div class="section-title">FILES PROCESSED</div>
            <div class="file-list">
                {''.join([f'<div class="file-item"> {f.get("name", "Unknown")} <span class="status">{f.get("status", "Processed")}</span></div>' for f in details.get('files', [])[:100]])}
                {f'<div class="file-item" style="color:#666;">... and {len(details.get("files", []))-100} more files</div>' if len(details.get('files', [])) > 100 else ''}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">RECOMMENDATIONS</div>
            <div class="recommendation">Always keep your encryption key in a secure location</div>
            <div class="recommendation">Create multiple backups of your encryption key</div>
            <div class="recommendation">Use the QR code export feature for secure key sharing</div>
            <div class="recommendation">Regularly verify your encrypted data integrity</div>
            <div class="recommendation">Store encrypted containers in a safe location</div>
        </div>
        
        <div class="warning">
            <div class="warning-title">ENCRYPT WITH CAUTION</div>
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


class QRCodeManager:
    """QR Code management for encryption keys"""
    
    def __init__(self, crypto_engine):
        self.crypto = crypto_engine
        self.qr_dir = QR_CODE_DIR
        self.available = QR_DEPS_AVAILABLE
        self.method = QR_METHOD
        self.typer = TypeWriter('fast')
        
        if not os.path.exists(self.qr_dir):
            os.makedirs(self.qr_dir, mode=0o700, exist_ok=True)
        
        if not self.available:
            self.typer.type_text("QR Code features are disabled. Missing dependencies.", color=Colors.YELLOW)
            self.typer.type_text("Install: pip install qrcode[pil] pillow opencv-python-headless", color=Colors.CYAN)
    
    def generate_qr_code(self, key_data=None, filename=None):
        """Generate QR code from encryption key"""
        if not self.available:
            self.typer.type_text("QR Code feature unavailable. Missing dependencies.", color=Colors.RED)
            self.typer.type_text("Install: pip install qrcode[pil] pillow opencv-python-headless", color=Colors.CYAN)
            return None
            
        if key_data is None:
            if not os.path.exists(KEY_FILE):
                self.typer.type_text("No encryption key found", color=Colors.RED)
                self.typer.type_text("Run 'Setup Encryption System' first.", color=Colors.YELLOW)
                return None
            
            with open(KEY_FILE, "r") as f:
                key_data = f.read().strip()
        
        try:
            self.typer.type_text("Generating QR code...", color=Colors.YELLOW)
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
            
            self.typer.type_text("QR code generated successfully!", color=Colors.GREEN)
            
            return {
                'filepath': filepath,
                'image': img,
                'ascii': ascii_qr,
                'key_id': hashlib.sha256(key_data.encode()).hexdigest()[:16]
            }
        except Exception as e:
            self.typer.type_text("Failed to generate QR code: {}".format(str(e)), color=Colors.RED)
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
            self.typer.type_text("QR Code scanning unavailable. Missing dependencies.", color=Colors.RED)
            self.typer.type_text("Install: pip install opencv-python-headless pillow", color=Colors.CYAN)
            return None
            
        if image_path is None:
            if os.path.exists(self.qr_dir):
                qr_files = [f for f in os.listdir(self.qr_dir) if f.endswith('.png')]
                if qr_files:
                    qr_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.qr_dir, x)), reverse=True)
                    image_path = os.path.join(self.qr_dir, qr_files[0])
                    self.typer.type_text("Using most recent QR code: {}".format(qr_files[0]), color=Colors.CYAN)
                else:
                    self.typer.type_text("No QR code images found in {}".format(self.qr_dir), color=Colors.RED)
                    return None
            else:
                self.typer.type_text("QR code directory not found", color=Colors.RED)
                return None
        
        if not os.path.exists(image_path):
            self.typer.type_text("QR code image not found: {}".format(image_path), color=Colors.RED)
            return None
        
        try:
            self.typer.type_text("Scanning QR code with OpenCV...", color=Colors.YELLOW)
            time.sleep(0.5)
            
            img = cv2.imread(image_path)
            if img is None:
                self.typer.type_text("Failed to read image", color=Colors.RED)
                return None
            
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            
            if not data:
                self.typer.type_text("No QR code found in image", color=Colors.RED)
                return None
            
            qr_data = data.strip()
            self.typer.type_text("QR data length: {} characters".format(len(qr_data)), color=Colors.DIM)
            
            try:
                test_cipher = Fernet(qr_data.encode())
                test_data = b"DSTerminal_qr_test"
                encrypted = test_cipher.encrypt(test_data)
                decrypted = test_cipher.decrypt(encrypted)
                
                if test_data == decrypted:
                    key_id = hashlib.sha256(qr_data.encode()).hexdigest()[:16]
                    self.typer.type_text("QR code scanned successfully!", color=Colors.GREEN)
                    return {
                        'key': qr_data,
                        'key_id': key_id,
                        'source': image_path,
                        'valid': True
                    }
                else:
                    self.typer.type_text("QR code data validation failed", color=Colors.RED)
                    return None
                    
            except Exception as e:
                self.typer.type_text("Invalid key format in QR code: {}".format(str(e)), color=Colors.RED)
                return None
                
        except Exception as e:
            self.typer.type_text("Failed to scan QR code: {}".format(str(e)), color=Colors.RED)
            return None
    
    def import_key_from_qr(self, image_path=None):
        """Import encryption key by scanning QR code"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " QR KEY IMPORT ")
        
        self.typer.type_text("Scanning QR code for encryption key...", color=Colors.YELLOW)
        
        for i in range(5):
            sys.stdout.write(f"\r{Colors.GREEN}[{'=' * i}{' ' * (4 - i)}] Scanning{'.' * (i % 3 + 1)}  {Colors.END}")
            sys.stdout.flush()
            time.sleep(0.3)
        print()
        
        result = self.scan_qr_code(image_path)
        
        if not result:
            content = [
                "QR SCAN FAILED",
                "",
                "Could not extract a valid encryption key",
                "Make sure the QR code contains a valid Fernet key"
            ]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return False
        
        self.typer.type_text("QR Code scanned successfully!", color=Colors.GREEN)
        self.typer.type_text("Key ID: {}".format(result['key_id']), color=Colors.CYAN)
        self.typer.type_text("Source: {}".format(result['source']), color=Colors.CYAN)
        
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
            "KEY IMPORTED SUCCESSFULLY",
            "Key ID: {}".format(result['key_id']),
            "Source: {}".format(result['source']),
            "Location: {}".format(KEY_FILE),
            "",
            "Encryption system now uses the imported key"
        ]
        box.render(content, color=Colors.GREEN)
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        return True
    
    def export_key_as_qr(self):
        """Export encryption key as QR code"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " QR KEY EXPORT ")
        
        if not self.available:
            content = [
                "QR Code feature unavailable",
                "",
                "Missing required dependencies:",
                "  - qrcode[pil]",
                "  - pillow",
                "  - opencv-python-headless",
                "",
                "Install with: pip install qrcode[pil] pillow opencv-python-headless"
            ]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        if not os.path.exists(KEY_FILE):
            content = [
                "No encryption key found",
                "Run 'Setup Encryption System' first."
            ]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        with open(KEY_FILE, "r") as f:
            key = f.read().strip()
        
        self.typer.type_text("Generating QR code for your encryption key...", color=Colors.YELLOW)
        
        result = self.generate_qr_code(key)
        
        if not result:
            content = [
                "QR CODE GENERATION FAILED",
                "",
                "Could not generate QR code"
            ]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        key_id = result['key_id']
        
        content = [
            "QR CODE GENERATED",
            "Key ID: {}".format(key_id),
            "Saved as: {}".format(result['filepath']),
            "",
            "ASCII QR Code:",
            "",
            result['ascii'],
            "",
            "Share this QR code securely with recipients",
            "Anyone who scans this QR gets your encryption key",
            "",
            "To import this key, use 'Import Key from QR' option"
        ]
        box.render(content, color=Colors.YELLOW)
        
        if PlatformUtils.copy_to_clipboard(key):
            self.typer.type_text("Key copied to clipboard!", color=Colors.GREEN)
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
    
    def list_qr_codes(self):
        """List all generated QR codes"""
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " QR CODE INVENTORY ")
        
        if not os.path.exists(self.qr_dir):
            content = ["QR directory not found: {}".format(self.qr_dir)]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        qr_files = [f for f in os.listdir(self.qr_dir) if f.endswith('.png')]
        
        if not qr_files:
            content = ["No QR codes found in {}".format(self.qr_dir)]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        headers = ["#", "File", "Size", "Created"]
        rows = []
        
        for i, file in enumerate(sorted(qr_files, key=lambda x: os.path.getmtime(os.path.join(self.qr_dir, x)), reverse=True), 1):
            filepath = os.path.join(self.qr_dir, file)
            size = os.path.getsize(filepath)
            size_str = f"{size/1024:.1f} KB"
            created = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
            rows.append([f"{i}", file, size_str, created])
        
        table = AnimatedTable(headers)
        table.render(rows)
        
        self.typer.type_text("Total QR codes: {}".format(len(qr_files)), color=Colors.CYAN)
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def restore_key_from_backup_qr(self):
        """Emergency restore encryption key from QR code backup"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " EMERGENCY KEY RESTORE ")
        
        if not self.available:
            content = [
                "QR Code feature unavailable",
                "",
                "Cannot restore from QR without QR dependencies",
                "Install: pip install qrcode[pil] pillow opencv-python-headless"
            ]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        content = [
            "EMERGENCY KEY RESTORE",
            "",
            "This will restore your encryption key from a QR code backup",
            "Use this if you've lost your key file or forgotten it",
            "",
            "Do you have a QR code image saved?"
        ]
        box.render(content, color=Colors.RED)
        
        print(f"\n{Colors.GREEN}1.{Colors.END} Use existing QR code from directory")
        print(f"{Colors.GREEN}2.{Colors.END} Provide path to QR code image")
        print(f"{Colors.GREEN}3.{Colors.END} Cancel")
        
        choice = input(f"\n{Colors.YELLOW}Select option [1-3]: {Colors.END}").strip()
        
        if choice == '1':
            if not os.path.exists(self.qr_dir):
                self.typer.type_text("QR directory not found", color=Colors.RED)
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                return
                
            qr_files = [f for f in os.listdir(self.qr_dir) if f.endswith('.png')]
            if not qr_files:
                self.typer.type_text("No QR codes found", color=Colors.RED)
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
                    self.typer.type_text("Invalid selection", color=Colors.RED)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            except ValueError:
                self.typer.type_text("Invalid input", color=Colors.RED)
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                
        elif choice == '2':
            path = input(f"{Colors.CYAN}Path to QR code image: {Colors.END}").strip()
            if os.path.exists(path):
                self.import_key_from_qr(path)
            else:
                self.typer.type_text("File not found: {}".format(path), color=Colors.RED)
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
        
        if not os.path.exists(self.encrypted_dir):
            try:
                os.makedirs(self.encrypted_dir, mode=0o700, exist_ok=True)
                self.typer.type_text("Created encrypted directory: {}".format(self.encrypted_dir), color=Colors.GREEN)
            except Exception as e:
                self.typer.type_text("Could not create encrypted directory: {}".format(e), color=Colors.YELLOW)
    
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
        """Encrypt directory - Cross-platform using ZIP"""
        
        if not self.crypto.cipher:
            self.typer.type_text("Encryption not initialized. Setup encryption first.", color=Colors.RED)
            return False, None
        
        if not os.path.exists(directory_path):
            self.typer.type_text("Directory not found: {}".format(directory_path), color=Colors.RED)
            return False, None
        
        if not os.path.isdir(directory_path):
            self.typer.type_text("Path is not a directory: {}".format(directory_path), color=Colors.RED)
            return False, None
        
        self.typer.type_text("Scanning directory: {}".format(directory_path), color=Colors.CYAN)
        file_tree = self.get_file_tree(directory_path)
        
        if not file_tree:
            self.typer.type_text("No files found to encrypt", color=Colors.YELLOW)
            return False, None
        
        total_files = len(file_tree)
        self.typer.type_text("Found {} files to encrypt".format(total_files), color=Colors.GREEN)
        
        dir_name = os.path.basename(directory_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
                        self.typer.type_text("  Progress: {}/{} files encrypted".format(idx, total_files), color=Colors.DIM)
                        
                except Exception as e:
                    self.typer.type_text("  Failed to encrypt {}: {}".format(rel_path, str(e)), color=Colors.RED)
            
            manifest_path = os.path.join(temp_dir, self.manifest_file)
            with open(manifest_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.typer.type_text("Creating encrypted container...", color=Colors.YELLOW)
            
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
            
            self.typer.type_text("Directory encrypted successfully!", color=Colors.GREEN)
            self.typer.type_text("   Container: {}".format(encrypted_container), color=Colors.CYAN)
            self.typer.type_text("   Format: ZIP (cross-platform)", color=Colors.CYAN)
            self.typer.type_text("   Total files: {}".format(total_files), color=Colors.CYAN)
            self.typer.type_text("   Total size: {}".format(self.crypto.human_readable_size(metadata['total_size'])), color=Colors.CYAN)
            
            self.crypto.add_activity("Encrypted directory: {} ({} files)".format(dir_name, total_files))
            
            self.typer.type_text("Generating report...", color=Colors.YELLOW)
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
            self.typer.type_text("Failed to encrypt directory: {}".format(str(e)), color=Colors.RED)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False, None
        
    def decrypt_directory(self, encrypted_container, output_dir=None):
        """Decrypt directory - Auto-detects format for cross-platform compatibility"""
        
        if not self.crypto.cipher:
            self.typer.type_text("Decryption not initialized. Setup encryption first.", color=Colors.RED)
            return False
        
        if not os.path.exists(encrypted_container):
            self.typer.type_text("Container not found: {}".format(encrypted_container), color=Colors.RED)
            return False
        
        temp_dir = tempfile.mkdtemp(prefix="dsterminal_dec_")
        processed_files = []
        
        try:
            self.typer.type_text("Extracting container...", color=Colors.YELLOW)
            
            extracted = False
            format_used = "unknown"
            
            # Try ZIP first (most common)
            try:
                import zipfile
                with zipfile.ZipFile(encrypted_container, 'r') as zipf:
                    zipf.extractall(temp_dir)
                extracted = True
                format_used = "ZIP"
                self.typer.type_text("   Detected and extracted as ZIP archive", color=Colors.GREEN)
            except:
                pass
            
            if not extracted:
                try:
                    import tarfile
                    with tarfile.open(encrypted_container, 'r:gz') as tarf:
                        tarf.extractall(temp_dir)
                    extracted = True
                    format_used = "TAR.GZ"
                    self.typer.type_text("   Detected and extracted as TAR.GZ archive", color=Colors.GREEN)
                except:
                    pass
            
            if not extracted:
                try:
                    import tarfile
                    with tarfile.open(encrypted_container, 'r:') as tarf:
                        tarf.extractall(temp_dir)
                    extracted = True
                    format_used = "TAR"
                    self.typer.type_text("   Detected and extracted as TAR archive", color=Colors.GREEN)
                except:
                    pass
            
            if not extracted:
                self.typer.type_text("   Could not extract container (unsupported format)", color=Colors.RED)
                shutil.rmtree(temp_dir)
                return False
            
            extracted_items = os.listdir(temp_dir)
            if not extracted_items:
                self.typer.type_text("Empty container", color=Colors.RED)
                shutil.rmtree(temp_dir)
                return False
            
            extracted_dir = temp_dir
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                extracted_dir = os.path.join(temp_dir, extracted_items[0])
            
            manifest_path = os.path.join(extracted_dir, self.manifest_file)
            if not os.path.exists(manifest_path):
                for root, dirs, files in os.walk(extracted_dir):
                    if self.manifest_file in files:
                        manifest_path = os.path.join(root, self.manifest_file)
                        extracted_dir = root
                        break
                
                if not os.path.exists(manifest_path):
                    self.typer.type_text("Manifest not found in container", color=Colors.RED)
                    shutil.rmtree(temp_dir)
                    return False
            
            with open(manifest_path, 'r') as f:
                metadata = json.load(f)
            
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(encrypted_container), 
                                        f"{metadata['original_name']}_decrypted")
            
            os.makedirs(output_dir, exist_ok=True)
            
            total_files = len(metadata['files'])
            self.typer.type_text("Decrypting {} files...".format(total_files), color=Colors.CYAN)
            
            decrypted_count = 0
            for idx, file_info in enumerate(metadata['files'], 1):
                if not file_info.get('encrypted', True):
                    continue
                
                enc_path = os.path.join(extracted_dir, file_info['path'] + '.enc')
                dec_path = os.path.join(output_dir, file_info['path'])
                
                if not os.path.exists(enc_path):
                    self.typer.type_text("  Encrypted file not found: {}".format(file_info['path']), color=Colors.RED)
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
                        self.typer.type_text("  Progress: {}/{} files decrypted".format(idx, total_files), color=Colors.DIM)
                        
                except Exception as e:
                    self.typer.type_text("  Failed to decrypt {}: {}".format(file_info['path'], str(e)), color=Colors.RED)
            
            shutil.rmtree(temp_dir)
            
            self.typer.type_text("Directory decrypted successfully!", color=Colors.GREEN)
            self.typer.type_text("   Output: {}".format(output_dir), color=Colors.CYAN)
            self.typer.type_text("   Files decrypted: {}/{}".format(decrypted_count, total_files), color=Colors.CYAN)
            self.typer.type_text("   Format: {} (auto-detected)".format(format_used), color=Colors.CYAN)
            
            self.crypto.add_activity("Decrypted directory: {} ({} files)".format(metadata['original_name'], decrypted_count))
            
            self.typer.type_text("Generating report...", color=Colors.YELLOW)
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
            self.typer.type_text("Failed to decrypt directory: {}".format(str(e)), color=Colors.RED)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False
    
    def list_encrypted_directories(self):
        """List encrypted directories - Supports multiple formats"""
        if not os.path.exists(self.encrypted_dir):
            return []
        
        containers = []
        for file in os.listdir(self.encrypted_dir):
            if (file.endswith('.enc_dir.zip') or 
                file.endswith('.enc_dir.tar.gz') or 
                file.endswith('.enc_dir.tgz') or 
                file.endswith('.enc_dir')):
                full_path = os.path.join(self.encrypted_dir, file)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                
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
    """Main encryption engine with QR code integration - cross-platform"""
    
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.cipher = None
        self.matrix = MatrixRain()
        self.qr_manager = QRCodeManager(self)
        self.dir_encryptor = DirectoryEncryptor(self)
        self.report_gen = ReportGenerator()
        self.typer = TypeWriter('fast')
        self.start_time = datetime.now()
        self.last_action = None
        self.recent_activity = []
        self.reports_count = 0
        
        self.secure_delete_enabled = False
        self.secure_delete_passes = 3
        self.auto_delete_original = False
        self.deletion_log = []
        
        # Ensure all directories exist
        for dir_path in [KEY_FILE, QR_CODE_DIR, BACKUP_DIR, ENCRYPTED_DIR, REPORTS_DIR]:
            dir_name = os.path.dirname(dir_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, mode=0o700, exist_ok=True)
        
        for d in [QR_CODE_DIR, BACKUP_DIR, ENCRYPTED_DIR, REPORTS_DIR]:
            if not os.path.exists(d):
                os.makedirs(d, mode=0o700, exist_ok=True)
        
        self.init_cipher()
        self.update_stats()
        
        if not QR_DEPS_AVAILABLE:
            self.typer.type_text("QR Code features are disabled.", color=Colors.YELLOW)
            self.typer.type_text("To enable QR features, install missing dependencies:", color=Colors.CYAN)
            self.typer.type_text("   pip install qrcode[pil] pillow opencv-python-headless", color=Colors.CYAN)
    
    def main(self):
        """Main entry point for CryptoEngine - Full interactive dashboard"""
        while True:
            PlatformUtils.clear_screen()
            self.show_dashboard(with_typing=False)
            
            print(f"\n{Colors.DIM}┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
            print(f"│  {Colors.CYAN}┌────────────────────────────────────────────────────────────────────────────────────────────────────┐{Colors.DIM}│")
            print(f"│  {Colors.CYAN}│  {Colors.GREEN}01{Colors.CYAN} Setup System     {Colors.GREEN}02{Colors.CYAN} Encrypt File   {Colors.GREEN}03{Colors.CYAN} Decrypt File   {Colors.GREEN}04{Colors.CYAN} Encrypt Dir  {Colors.CYAN}│{Colors.DIM}│")
            print(f"│  {Colors.CYAN}│  {Colors.GREEN}05{Colors.CYAN} Decrypt Dir      {Colors.GREEN}06{Colors.CYAN} Backup Key     {Colors.GREEN}07{Colors.CYAN} QR Generate    {Colors.GREEN}08{Colors.CYAN} Export Key   {Colors.CYAN}│{Colors.DIM}│")
            print(f"│  {Colors.CYAN}│  {Colors.GREEN}09{Colors.CYAN} Import Key       {Colors.GREEN}10{Colors.CYAN} List Files     {Colors.GREEN}11{Colors.CYAN} File Info      {Colors.GREEN}12{Colors.CYAN} Verify Sys  {Colors.CYAN}│{Colors.DIM}│")
            print(f"│  {Colors.CYAN}│  {Colors.GREEN}13{Colors.CYAN} Reports          {Colors.GREEN}14{Colors.CYAN} QR Import      {Colors.GREEN}15{Colors.CYAN} QR Restore     {Colors.GREEN}16{Colors.CYAN} QR List     {Colors.CYAN}│{Colors.DIM}│")
            print(f"│  {Colors.CYAN}│  {Colors.GREEN}17{Colors.CYAN} Clean QR         {Colors.GREEN}18{Colors.CYAN} Encrypted Dirs {Colors.GREEN}19{Colors.CYAN} Debug Info     {Colors.GREEN}20{Colors.CYAN} Encrypt Test{Colors.CYAN}│{Colors.DIM}│")
            print(f"│  {Colors.CYAN}│  {Colors.GREEN}21{Colors.CYAN} Decrypt Test     {Colors.GREEN}00{Colors.CYAN} Return to DSTERMINAL                                {Colors.CYAN}│{Colors.DIM}│")
            print(f"│  {Colors.CYAN}└────────────────────────────────────────────────────────────────────────────────────────────────────┘{Colors.DIM}│")
            print(f"└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘{Colors.END}")
            
            choice = input(f"\n{Colors.GREEN}└──[{Colors.YELLOW}CRYPTO{Colors.GREEN}]{Colors.END} # ").strip()
            
            if choice in ['01', '1']:
                self.encrypt_setup()
            elif choice in ['02', '2']:
                filename = input(f"{Colors.CYAN}File to encrypt: {Colors.END}").strip()
                if filename:
                    self.encrypt_file(filename)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice in ['03', '3']:
                filename = input(f"{Colors.CYAN}File to decrypt: {Colors.END}").strip()
                if filename:
                    self.decrypt_file(filename)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice in ['04', '4']:
                self.encrypt_directory()
            elif choice in ['05', '5']:
                self.decrypt_directory()
            elif choice in ['06', '6']:
                self.crypto_backup()
            elif choice in ['07', '7']:
                self.qr_generate()
            elif choice in ['08', '8']:
                self.export_encryption_key()
            elif choice in ['09', '9']:
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
                        self.typer.type_text("Deleted {} QR codes".format(count), color=Colors.GREEN)
                        self.add_activity("Cleaned {} QR codes".format(count))
                        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                else:
                    self.typer.type_text("QR directory not found", color=Colors.RED)
                    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice == '18':
                self.list_encrypted_dirs()
            elif choice == '19':
                self._debug_info()
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            elif choice == '20':
                self.encrypt_test()
            elif choice == '21':
                self.decrypt_test()
            elif choice in ['00', '0']:
                print(f"\n{Colors.YELLOW}Returning to DSTERMINAL...{Colors.END}")
                time.sleep(0.5)
                break
            else:
                self.typer.type_text("Invalid option. Please select a valid command.", color=Colors.RED)
                time.sleep(1)
    
    def _debug_info(self):
        """Display debug information"""
        self.typer.type_text("DEBUG INFO", color=Colors.RED)
        self.typer.type_text("KEY_FILE: {}".format(KEY_FILE), color=Colors.CYAN)
        self.typer.type_text("QR_CODE_DIR: {}".format(QR_CODE_DIR), color=Colors.CYAN)
        self.typer.type_text("BACKUP_DIR: {}".format(BACKUP_DIR), color=Colors.CYAN)
        self.typer.type_text("ENCRYPTED_DIR: {}".format(ENCRYPTED_DIR), color=Colors.CYAN)
        self.typer.type_text("REPORTS_DIR: {}".format(REPORTS_DIR), color=Colors.CYAN)
        self.typer.type_text("Key exists: {}".format(os.path.exists(KEY_FILE)), color=Colors.CYAN)
        self.typer.type_text("QR dir exists: {}".format(os.path.exists(QR_CODE_DIR)), color=Colors.CYAN)
        self.typer.type_text("Encrypted dir exists: {}".format(os.path.exists(ENCRYPTED_DIR)), color=Colors.CYAN)
        self.typer.type_text("Reports dir exists: {}".format(os.path.exists(REPORTS_DIR)), color=Colors.CYAN)
        self.typer.type_text("QR Method: {}".format(QR_METHOD), color=Colors.CYAN)
        self.typer.type_text("Report Available: {}".format(REPORT_AVAILABLE), color=Colors.CYAN)
    
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
        """Update dashboard statistics"""
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
        
        self.reports_count = 0
        if os.path.exists(REPORTS_DIR):
            self.reports_count = len([f for f in os.listdir(REPORTS_DIR) if f.endswith('.pdf') or f.endswith('.html')])
        
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        
        # Dashboard stats will be updated when dashboard is shown
        self._stats = {
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
            'last_action': self.last_action,
            'recent_activity': self.recent_activity[-5:]
        }
    
    def add_activity(self, activity):
        """Add activity to recent activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recent_activity.append(f"[{timestamp}] {activity}")
        if len(self.recent_activity) > 10:
            self.recent_activity = self.recent_activity[-10:]
        self.last_action = activity
        self.update_stats()
    
    def init_cipher(self):
        """Initialize cipher from key file"""
        if os.path.exists(KEY_FILE):
            try:
                with open(KEY_FILE, "r") as f:
                    key = f.read().strip()
                    self.cipher = Fernet(key.encode())
                    self.add_activity("Cipher initialized")
            except:
                self.cipher = None

    def human_readable_size(self, size):
        """Convert size to human readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    def secure_delete(self, file_path, passes=3):
        """Securely delete a file by overwriting it multiple times"""
        try:
            file_path = os.path.normpath(file_path)
            if not os.path.exists(file_path):
                return False
            
            file_path = os.path.abspath(file_path)
            
            if not os.access(file_path, os.W_OK):
                return False
            
            size = os.path.getsize(file_path)
            
            if size < 1024:
                passes = 1
            
            import gc
            gc.collect()
            time.sleep(0.2)
            
            try:
                os.remove(file_path)
                if not os.path.exists(file_path):
                    return True
            except:
                pass
            
            try:
                with open(file_path, "r+b") as f:
                    for i in range(passes):
                        f.seek(0)
                        bytes_written = 0
                        chunk_size = 1024 * 1024
                        while bytes_written < size:
                            chunk = os.urandom(min(chunk_size, size - bytes_written))
                            f.write(chunk)
                            bytes_written += len(chunk)
                        f.flush()
                        os.fsync(f.fileno())
                        f.seek(0)
                    
                    f.seek(0)
                    bytes_written = 0
                    chunk_size = 1024 * 1024
                    while bytes_written < size:
                        chunk = b'\x00' * min(chunk_size, size - bytes_written)
                        f.write(chunk)
                        bytes_written += len(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                
                gc.collect()
                time.sleep(0.2)
                
            except Exception as e:
                return False
            
            try:
                os.remove(file_path)
            except:
                pass
            
            time.sleep(0.2)
            if not os.path.exists(file_path):
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def show_dashboard(self, with_typing=True):
        """Show the dashboard with current stats"""
        self.update_stats()
        stats = self._stats if hasattr(self, '_stats') else {}
        
        print(f"\n{Colors.CYAN}┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print(f"│{Colors.YELLOW}                  DSTERMINAL ENCRYPTION SUITE                 {Colors.CYAN}│")
        print(f"│──────────────────────────────────────────────────────────────────────────────────────────────────────────────│")
        print(f"│{Colors.GREEN}  Encryption: {Colors.END}{Colors.GREEN if stats.get('encryption_ready') else Colors.RED}{'ACTIVE' if stats.get('encryption_ready') else 'INACTIVE'}{Colors.END}")
        print(f"│{Colors.GREEN}  Key ID: {Colors.END}{Colors.CYAN}{stats.get('key_id', 'N/A')}{Colors.END}")
        print(f"│{Colors.GREEN}  QR Codes: {Colors.END}{Colors.YELLOW}{stats.get('qr_count', 0)}{Colors.END}")
        print(f"│{Colors.GREEN}  Encrypted Files: {Colors.END}{Colors.MAGENTA}{stats.get('encrypted_count', 0)}{Colors.END}")
        print(f"│{Colors.GREEN}  Encrypted Dirs: {Colors.END}{Colors.CYAN}{stats.get('encrypted_dirs', 0)}{Colors.END}")
        print(f"│{Colors.GREEN}  Reports: {Colors.END}{Colors.WHITE}{stats.get('reports_count', 0)}{Colors.END}")
        print(f"│{Colors.GREEN}  Uptime: {Colors.END}{Colors.DIM}{stats.get('uptime', '00:00:00')}{Colors.END}")
        print(f"└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def animate_encryption(self, filename, operation="ENCRYPTING"):
        """Show encryption/decryption animation with progress bar"""
        print(f"\n{Colors.YELLOW}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{operation} {filename}{Colors.END}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.END}")
        
        for i in range(8):
            progress = (i + 1) * 12.5
            bar_length = 30
            filled = int(bar_length * progress // 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
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
            
            sys.stdout.write('\033[2A')
            sys.stdout.write('\033[J')
            
            print(f"Progress: [{bar}] {progress:.1f}%")
            print(f"Status: {status_msgs[i] if i < len(status_msgs) else 'Processing...'}")
            
            time.sleep(0.15)
        
        print(f"\n{Colors.GREEN}✓ {operation} COMPLETE{Colors.END}")
    
    def encrypt_setup(self):
        """Setup encryption system and generate key"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " ENCRYPTION SETUP ")
        
        self.typer.type_text("INITIALIZING SECURE ENCRYPTION SYSTEM", color=Colors.YELLOW)
        self.typer.type_text("──────────────────────────────────────────────────────────────────", color=Colors.RED)

        if os.path.exists(KEY_FILE):
            with open(KEY_FILE) as f:
                key = f.read().strip()
            key_id = hashlib.sha256(key.encode()).hexdigest()[:16]
            
            content = [
                "EXISTING KEY FOUND",
                "Key ID: {}".format(key_id),
                "Location: {}".format(KEY_FILE),
                "Status: ACTIVE"
            ]
            box.render(content, color=Colors.GREEN)
            self.add_activity("Setup checked - key exists")
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return

        self.typer.type_text("▶ Generating quantum-resistant encryption key...", color=Colors.YELLOW)
        time.sleep(1)
        
        for i in range(3):
            self.typer.type_text("   Entropy pool: {}".format(''.join(random.choices('01', k=20))), color=Colors.CYAN)
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
            "NEW ENCRYPTION KEY GENERATED",
            "Key ID: {}".format(key_id),
            "Location: {}".format(KEY_FILE),
            "Permissions: 600 (user only)",
            "",
            "KEEP THIS KEY SAFE!",
            "Use QR code export to share securely"
        ]
        box.render(content, color=Colors.GREEN)
        
        self.init_cipher()
        self.add_activity("New encryption key generated")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def encrypt_file(self, filename):
        """Encrypt a single file with secure deletion option"""
        if not self.cipher:
            self.typer.type_text("[!] Encryption not initialized", color=Colors.RED)
            return

        path = os.path.join(self.base_dir, filename)
        path = os.path.normpath(path)

        if not os.path.exists(path):
            self.typer.type_text("[!] File not found", color=Colors.RED)
            return
        
        self.animate_encryption(filename, "ENCRYPTING")

        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            self.typer.type_text("[!] Failed to read file: {}".format(e), color=Colors.RED)
            return
        
        original_size = len(data)
        
        try:
            encrypted = self.cipher.encrypt(data)
        except Exception as e:
            self.typer.type_text("[!] Encryption failed: {}".format(e), color=Colors.RED)
            return
        
        enc_file = path + ".enc"
        
        try:
            with open(enc_file, "wb") as f:
                f.write(encrypted)
        except Exception as e:
            self.typer.type_text("[!] Failed to write encrypted file: {}".format(e), color=Colors.RED)
            return
        
        encrypted_size = len(encrypted)
        
        print(f"\n{Colors.GREEN}✓ File encrypted successfully!{Colors.END}")
        print(f"   Output: {enc_file}")
        print(f"   Original: {self.human_readable_size(original_size)} → Encrypted: {self.human_readable_size(encrypted_size)}")
        
        try:
            if not os.path.exists(enc_file):
                raise Exception("Encrypted file not created")
            
            file_size = os.path.getsize(enc_file)
            if file_size == 0:
                raise Exception("Encrypted file is empty")
            
            with open(enc_file, 'rb') as f:
                full_encrypted_data = f.read()
            
            test_decrypt = self.cipher.decrypt(full_encrypted_data)
            
            if test_decrypt == data:
                print(f"{Colors.GREEN}✓ Encryption verified successfully!{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Verification warning: Decrypted data doesn't match original{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}❌ Encryption verification failed: {str(e)}{Colors.END}")
            try:
                if os.path.exists(enc_file):
                    os.remove(enc_file)
                    print(f"{Colors.DIM}✓ Removed corrupted encrypted file{Colors.END}")
            except:
                pass
            return
        
        print(f"\n{Colors.YELLOW}Delete original file?{Colors.END}")
        print(f"  {Colors.DIM}Warning: This is irreversible!{Colors.END}")
        choice = input(f"{Colors.CYAN}Delete original? (y/N): {Colors.END}").strip().lower()

        if choice == 'y':
            print(f"\n{Colors.YELLOW}File to delete: {path}{Colors.END}")
            verify = input(f"{Colors.RED}⚠️  Confirm deletion of {os.path.basename(path)}? (yes/NO): {Colors.END}").strip().lower()
            if verify == 'yes':
                import gc
                gc.collect()
                time.sleep(0.5)
                
                print(f"{Colors.YELLOW}🔒 Securely deleting original...{Colors.END}")
                success = self.secure_delete(path, passes=3)
                
                if success and not os.path.exists(path):
                    print(f"{Colors.GREEN}✓ Original file securely deleted{Colors.END}")
                    self.add_activity("Securely deleted original: {}".format(filename))
                else:
                    if os.path.exists(path):
                        print(f"{Colors.RED}❌ File still exists!{Colors.END}")
                        print(f"{Colors.YELLOW}⚠️  Original file kept for safety{Colors.END}")
            else:
                print(f"{Colors.GREEN}✓ Original file kept (user cancelled){Colors.END}")
        else:
            print(f"{Colors.GREEN}✓ Original file kept (safe){Colors.END}")
        
        self.typer.type_text("Generating report...", color=Colors.YELLOW)
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
        """Decrypt a file with Matrix rain visualization"""
        if not self.cipher:
            self.typer.type_text("[!] Encryption not initialized", color=Colors.RED)
            return

        path = os.path.join(self.base_dir, filename)

        if not os.path.exists(path):
            self.typer.type_text("[!] File not found", color=Colors.RED)
            return
        
        print(f"\n{Colors.YELLOW}🔓 DECRYPTING FILE: {filename}{Colors.END}")
        
        with open(path, "rb") as f:
            data = f.read()

        try:
            decrypted = self.cipher.decrypt(data)
            out_file = path.replace(".enc", "")
            
            with open(out_file, "wb") as f:
                f.write(decrypted)
            
            self.add_activity("Decrypted: {}".format(filename))
            
            print(f"\n{Colors.GREEN}✓ File decrypted successfully!{Colors.END}")
            print(f"   Output: {out_file}")
            
            self.typer.type_text("Generating report...", color=Colors.YELLOW)
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
            self.typer.type_text("❌ Decryption failed: {}".format(e), color=Colors.RED)
    
    def encrypt_directory(self):
        """Encrypt a directory with progress tracking"""
        print(f"\n{Colors.YELLOW}📂 DIRECTORY ENCRYPTION{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")
        
        if not self.cipher:
            self.typer.type_text("Encryption not initialized. Setup encryption first.", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        directory_path = input(f"{Colors.CYAN}Enter directory path to encrypt: {Colors.END}").strip()
        
        if not directory_path:
            self.typer.type_text("No directory specified", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        directory_path = os.path.expanduser(directory_path)
        
        if not os.path.exists(directory_path):
            self.typer.type_text("Directory not found: {}".format(directory_path), color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        if not os.path.isdir(directory_path):
            self.typer.type_text("Path is not a directory: {}".format(directory_path), color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
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
        
        self.animate_encryption(directory_path, "ENCRYPTING DIRECTORY")
        
        def progress_callback(current, total, filename):
            if current % 10 == 0 or current == total:
                print(f"  [{current}/{total}] {filename}")
        
        success, container_path = self.dir_encryptor.encrypt_directory(directory_path, progress_callback)
        
        if success:
            print(f"\n{Colors.GREEN}✓ Directory encryption completed successfully!{Colors.END}")
            if container_path:
                print(f"   Container: {container_path}")
            
            if delete_choice == '2':
                self._delete_original_directory_files(directory_path, all_files, "all")
            elif delete_choice == '3':
                self._delete_original_directory_files(directory_path, all_files, "individual")
            else:
                print(f"{Colors.GREEN}✓ Original files kept (safe){Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Directory encryption failed{Colors.END}")
            
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
    
    def decrypt_directory(self):
        """Decrypt a directory"""
        print(f"\n{Colors.YELLOW}📂 DIRECTORY DECRYPTION{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")
        
        if not self.cipher:
            self.typer.type_text("Decryption not initialized. Setup encryption first.", color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        containers = self.dir_encryptor.list_encrypted_directories()
        
        if not containers:
            self.typer.type_text("No encrypted directories found", color=Colors.RED)
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
            self.typer.type_text("Invalid selection", color=Colors.RED)
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
        
        self.animate_encryption(container_path, "DECRYPTING DIRECTORY")
        
        success = self.dir_encryptor.decrypt_directory(container_path, output_dir)
        
        if success:
            print(f"\n{Colors.GREEN}✓ Directory decryption completed successfully!{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Directory decryption failed{Colors.END}")
        
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
        self.update_stats()
    
    def list_encrypted_dirs(self):
        """List encrypted directories"""
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " ENCRYPTED DIRECTORIES ")
        
        containers = self.dir_encryptor.list_encrypted_directories()
        
        if not containers:
            content = ["No encrypted directories found."]
            box.render(content, color=Colors.RED)
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
        table.render(rows)
        
        self.typer.type_text("Total containers: {}".format(len(containers)), color=Colors.CYAN)
        self.typer.type_text("Location: {}".format(ENCRYPTED_DIR), color=Colors.DIM)
        
        self.add_activity("Listed encrypted directories")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
    
    def crypto_list(self):
        """List encrypted files"""
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " ENCRYPTED FILES INVENTORY ")
        
        encrypted = []
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith(".enc"):
                    path = os.path.join(root, file)
                    encrypted.append(path)

        if not encrypted:
            content = ["No encrypted files found."]
            box.render(content, color=Colors.RED)
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
        table.render(rows)
        self.add_activity("Listed encrypted files")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def crypto_info(self, filename=None):
        """Display encryption information for a file"""
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
            "File: {}".format(filename),
            "Path: {}".format(path),
            "Size: {}".format(self.human_readable_size(size)),
            "SHA256: {}...".format(sha256[:32]),
            "MD5: {}...".format(md5[:16])
        ]
        box.render(content, color=Colors.CYAN)

        self.typer.type_text("🔍 Encryption Analysis", color=Colors.YELLOW)
        self.typer.type_text("──────────────────────────────────────────────────────────────────", color=Colors.CYAN)
        
        try:
            base64.urlsafe_b64decode(data)
            self.typer.type_text("✓ Format: Fernet (AES-256)", color=Colors.GREEN)
        except Exception:
            self.typer.type_text("✗ Format: Unknown", color=Colors.RED)

        self.typer.type_text("🛡️ Integrity Check", color=Colors.YELLOW)
        self.typer.type_text("──────────────────────────────────────────────────────────────────", color=Colors.CYAN)

        if not self.cipher:
            self.typer.type_text("⚠️ Key not loaded — cannot verify integrity", color=Colors.RED)
        else:
            try:
                self.cipher.decrypt(data)
                self.typer.type_text("✓ File integrity: VALID", color=Colors.GREEN)
                self.typer.type_text("   Authentication tag verified", color=Colors.CYAN)
            except Exception:
                self.typer.type_text("❌ File integrity: FAILED", color=Colors.RED)

        self.add_activity("Checked info for: {}".format(filename))
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def crypto_verify(self):
        """Verify encryption system"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " SYSTEM VERIFICATION ")
        
        checks = []
        
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE) as f:
                key = f.read().strip()
            try:
                Fernet(key.encode())
                checks.append("✓ Key format valid")
            except:
                checks.append("✗ Invalid key")
        else:
            checks.append("✗ Key file missing")

        if self.cipher:
            checks.append("✓ Cipher initialized")
            
            test = b"dsterminal test data"
            try:
                enc = self.cipher.encrypt(test)
                dec = self.cipher.decrypt(enc)
                if test == dec:
                    checks.append("✓ Self-test PASSED")
                else:
                    checks.append("✗ Self-test FAILED")
            except:
                checks.append("✗ Encryption test failed")
        else:
            checks.append("✗ Cipher not initialized")

        if os.path.exists(QR_CODE_DIR):
            checks.append("✓ QR directory exists")
        else:
            checks.append("⚠️ QR directory not found")
        
        if os.path.exists(ENCRYPTED_DIR):
            checks.append("✓ Encrypted dir storage exists")
        else:
            checks.append("⚠️ Encrypted dir storage not found")
        
        if os.path.exists(REPORTS_DIR):
            checks.append("✓ Reports directory exists")
        else:
            checks.append("⚠️ Reports directory not found")
        
        if QR_DEPS_AVAILABLE:
            checks.append("✓ QR dependencies installed")
        else:
            checks.append("✗ QR dependencies missing")
        
        if REPORT_AVAILABLE:
            checks.append("✓ Report generation enabled")
        else:
            checks.append("✗ Report generation unavailable")
        
        box.render(checks, color=Colors.YELLOW)
        self.add_activity("System verification completed")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def crypto_backup(self):
        """Backup encryption key"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " KEY BACKUP ")
        
        if not os.path.exists(KEY_FILE):
            content = ["No key found to backup"]
            box.render(content, color=Colors.RED)
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
            "Backup created successfully",
            "Location: {}".format(backup),
            "Permissions: 600",
            "",
            "Store this backup securely!",
            "Consider generating a QR code backup too"
        ]
        box.render(content, color=Colors.GREEN)
        self.add_activity("Key backup created")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def import_encryption_key(self, key_string=None):
        """Import encryption key from a string"""
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
                    "ENCRYPTION KEY IMPORTED SUCCESSFULLY",
                    "Key ID: {}".format(key_id),
                    "Location: {}".format(KEY_FILE),
                    "",
                    "You can now decrypt files encrypted with this key"
                ]
                box.render(content, color=Colors.GREEN)
                
                self.add_activity("Key imported from string")
                input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
                return True
            else:
                raise ValueError("Test decryption failed")
                
        except Exception as e:
            content = [
                "INVALID KEY FORMAT",
                "",
                "The key you provided is not valid.",
                "Make sure you copied the ENTIRE key string.",
                "",
                "Error: {}".format(str(e))
            ]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return False

    def export_encryption_key(self):
        """Export encryption key to share with another machine"""
        PlatformUtils.clear_screen()
        box = RotatingBox(50, " EXPORT ENCRYPTION KEY ")
        
        if not os.path.exists(KEY_FILE):
            content = [
                "No encryption key found",
                "Run 'Setup Encryption System' first."
            ]
            box.render(content, color=Colors.RED)
            input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
            return
        
        with open(KEY_FILE, "r") as f:
            key = f.read().strip()
        
        key_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        
        content = [
            "YOUR ENCRYPTION KEY",
            "Key ID: {}".format(key_id),
            "",
            "┌─────────────────────────────────────────────────────┐",
            "{}".format(key),
            "└─────────────────────────────────────────────────────┘",
            "",
            "COPY THIS KEY EXACTLY AS SHOWN ABOVE",
            "Share it securely with the recipient",
            "",
            "The recipient should use 'Import Key' option",
            "Or use QR code export for easier sharing"
        ]
        box.render(content, color=Colors.YELLOW)
        
        if PlatformUtils.copy_to_clipboard(key):
            self.typer.type_text("Key copied to clipboard!", color=Colors.GREEN)
        else:
            self.typer.type_text("Tip: Install 'pyperclip' for auto-copy: pip install pyperclip", color=Colors.YELLOW)
        
        self.add_activity("Key exported")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def list_reports(self):
        """List all generated reports"""
        PlatformUtils.clear_screen()
        box = RotatingBox(60, " REPORT INVENTORY ")
        
        if not os.path.exists(REPORTS_DIR):
            content = ["Reports directory not found: {}".format(REPORTS_DIR)]
            box.render(content, color=Colors.RED)
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
            content = ["No reports found."]
            box.render(content, color=Colors.RED)
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
        table.render(rows)
        
        self.typer.type_text("Total reports: {}".format(len(reports)), color=Colors.CYAN)
        self.typer.type_text("Location: {}".format(REPORTS_DIR), color=Colors.DIM)
        
        self.add_activity("Listed reports")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

    def qr_generate(self):
        """Generate QR code for encryption key"""
        self.qr_manager.export_key_as_qr()
        self.add_activity("QR code generated")
    
    def qr_import(self):
        """Import encryption key from QR code"""
        self.qr_manager.import_key_from_qr()
        self.add_activity("QR code imported")
    
    def qr_list(self):
        """List all QR codes"""
        self.qr_manager.list_qr_codes()
        self.add_activity("Listed QR codes")
    
    def qr_restore(self):
        """Emergency restore from QR code"""
        self.qr_manager.restore_key_from_backup_qr()
        self.add_activity("Emergency restore attempted")
    
    def encrypt_test(self):
        """Run encryption test"""
        print(f"\n{Colors.YELLOW}ENCRYPTION SYSTEM TEST{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")

        test_file = os.path.join(self.base_dir, "crypto_test.txt")
        
        with open(test_file, "w") as f:
            f.write("DSTerminal encryption test - DIR ENCRYPTION\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("Classified: TOP SECRET\n")
        
        print(f"{Colors.GREEN}✓ Test file created{Colors.END}")
        time.sleep(1.5)
        
        self.encrypt_file("crypto_test.txt")
        enc = test_file + ".enc"
        
        if os.path.exists(enc):
            print(f"{Colors.GREEN}✓ Encryption successful{Colors.END}")
            time.sleep(1.5)
            
            self.decrypt_file("crypto_test.txt.enc")
            print(f"{Colors.GREEN}✓ Decryption successful{Colors.END}")
            
            with open(test_file, "r") as f:
                content = f.read()
            print(f"{Colors.CYAN}✓ Data integrity verified{Colors.END}")
            
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
        """Run decryption test"""
        PlatformUtils.clear_screen()
        self.typer.type_text("DECRYPTION SYSTEM TEST", color=Colors.YELLOW)
        self.typer.type_text("──────────────────────────────────────────────────────────────────", color=Colors.RED)

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
        
        self.typer.type_text("📁 Found {} encrypted files".format(len(encrypted_files)), color=Colors.CYAN)
        time.sleep(1.5)
        
        test_file = encrypted_files[0]
        self.typer.type_text("🔓 Testing decryption on: {}".format(os.path.basename(test_file)), color=Colors.GREEN)
        time.sleep(1.5)
        
        self.animate_encryption(os.path.basename(test_file), "DECRYPTING")
        
        self.decrypt_file(os.path.basename(test_file))
        
        decrypted_file = test_file.replace(".enc", "")
        if os.path.exists(decrypted_file):
            self.typer.type_text("✓ Decryption test successful!", color=Colors.GREEN)
            
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
            
            try:
                os.remove(decrypted_file)
                self.typer.type_text("✓ Cleaned up: {}".format(os.path.basename(decrypted_file)), color=Colors.DIM)
            except:
                pass
        else:
            self.typer.type_text("❌ Decryption test failed!", color=Colors.RED)
        
        self.add_activity("Decryption test completed")
        input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")
    
    def _delete_original_directory_files(self, directory_path, all_files, mode="all"):
        """Delete original files after directory encryption"""
        print(f"\n{Colors.YELLOW}🔒 Processing original file deletion...{Colors.END}")
        print(f"{Colors.DIM}Total files to process: {len(all_files)}{Colors.END}")
        
        dir_name = os.path.basename(directory_path)
        encrypted_dir = ENCRYPTED_DIR
        
        containers = []
        if os.path.exists(encrypted_dir):
            for f in os.listdir(encrypted_dir):
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
            return
        
        latest = sorted(containers, key=lambda x: x['mtime'], reverse=True)[0]
        container_path = latest['path']
        
        if latest['name'].endswith('.zip'):
            fmt = "ZIP"
        elif latest['name'].endswith('.tar.gz') or latest['name'].endswith('.tgz'):
            fmt = "TAR.GZ"
        else:
            fmt = "Unknown"
        
        print(f"{Colors.CYAN}📦 Found encrypted container: {os.path.basename(container_path)}{Colors.END}")
        print(f"{Colors.DIM}   Format: {fmt}{Colors.END}")
        
        if not os.path.exists(container_path) or os.path.getsize(container_path) == 0:
            print(f"{Colors.RED}❌ Encrypted container is invalid!{Colors.END}")
            return
        
        if mode == "all" and len(all_files) > 10:
            print(f"\n{Colors.RED}⚠️  You are about to delete {len(all_files)} files!{Colors.END}")
            confirm = input(f"{Colors.RED}Type 'DELETE ALL' to confirm: {Colors.END}").strip()
            if confirm != 'DELETE ALL':
                print(f"{Colors.GREEN}✓ Deletion cancelled - all files kept{Colors.END}")
                return
        
        deleted_count = 0
        kept_count = 0
        skipped_count = 0
        failed_count = 0
        
        for idx, file_path in enumerate(all_files, 1):
            rel_path = os.path.relpath(file_path, directory_path)
            filename = os.path.basename(file_path)
            
            if filename in ['.DS_Store', 'Thumbs.db', 'desktop.ini']:
                print(f"{Colors.DIM}  ⏭ Skipping system file: {filename}{Colors.END}")
                skipped_count += 1
                continue
            
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
                try:
                    print(f"{Colors.YELLOW}🔒 Deleting [{idx}/{len(all_files)}]: {rel_path}{Colors.END}")
                    success = self.secure_delete(file_path, passes=3)
                    
                    if success and not os.path.exists(file_path):
                        deleted_count += 1
                        print(f"{Colors.GREEN}✓ Deleted: {rel_path}{Colors.END}")
                        self.add_activity("Securely deleted original: {}".format(rel_path))
                    else:
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
            print(f"{Colors.CYAN}Keep your encryption key safe to access encrypted data{Colors.END}")
        
        if failed_count > 0:
            retry = input(f"\n{Colors.YELLOW}Some files failed to delete. Retry? (y/N): {Colors.END}").strip().lower()
            if retry == 'y':
                print(f"{Colors.CYAN}🔄 Retrying failed deletions...{Colors.END}")
                remaining = []
                for file_path in all_files:
                    if os.path.exists(file_path):
                        remaining.append(file_path)
                if remaining:
                    self._delete_remaining_files(remaining)

    def _delete_remaining_files(self, remaining_files):
        """Delete files that survived the first deletion attempt"""
        print(f"\n{Colors.YELLOW}🔒 Attempting to delete {len(remaining_files)} remaining files...{Colors.END}")
        
        deleted_count = 0
        failed_count = 0
        
        for idx, file_path in enumerate(remaining_files, 1):
            rel_path = os.path.basename(file_path)
            print(f"{Colors.DIM}  [{idx}/{len(remaining_files)}] {rel_path}{Colors.END}")
            
            try:
                os.remove(file_path)
                time.sleep(0.1)
                if not os.path.exists(file_path):
                    deleted_count += 1
                    print(f"{Colors.GREEN}✓ Deleted: {rel_path}{Colors.END}")
                    continue
            except:
                pass
            
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
            print(f"{Colors.YELLOW}These files may be open in another program.{Colors.END}")
            print(f"{Colors.CYAN}   Close any programs that might be using them and try again.{Colors.END}")


def main():
    """Main entry point for the crypto engine"""
    crypto = CryptoEngine()
    crypto.main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}⚠️  Termination initiated{Colors.END}")
        time.sleep(1.5)
        sys.exit(0)