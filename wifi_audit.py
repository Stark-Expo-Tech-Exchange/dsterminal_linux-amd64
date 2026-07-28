#!/usr/bin/env python3
"""
DSTerminal WiFi Security Audit Module
Standalone version with glowing neon hacker colors, PDF/HTML reports
"""

import os
import sys
import platform
import subprocess
import re
import socket
import time
import random
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import hashlib

# Colorama for cross-platform colors
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    # Fallback color codes
    class Fore:
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        RESET = '\033[0m'
        LIGHTRED_EX = '\033[91m'
        LIGHTGREEN_EX = '\033[92m'
        LIGHTYELLOW_EX = '\033[93m'
        LIGHTCYAN_EX = '\033[96m'
        LIGHTMAGENTA_EX = '\033[95m'
        LIGHTBLUE_EX = '\033[94m'
        LIGHTWHITE_EX = '\033[97m'
    
    class Style:
        RESET_ALL = '\033[0m'
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
    
    COLORS_AVAILABLE = False

# Check for PDF library
try:
    from reportlab.lib.pagesizes import letter, landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[!] ReportLab not installed. PDF export disabled. Install with: pip install reportlab")


class WiFiAudit:
    """Comprehensive WiFi security audit engine with glowing neon hacker colors"""
    
    # Glowing neon color schemes
    NEON_COLORS = {
        'green': Fore.LIGHTGREEN_EX,
        'red': Fore.LIGHTRED_EX,
        'cyan': Fore.LIGHTCYAN_EX,
        'magenta': Fore.LIGHTMAGENTA_EX,
        'yellow': Fore.LIGHTYELLOW_EX,
        'blue': Fore.LIGHTBLUE_EX,
        'white': Fore.LIGHTWHITE_EX,
    }
    
    # Blinking effect (using ANSI)
    BLINK_ON = '\033[5m'
    BLINK_OFF = '\033[25m'
    BOLD = '\033[1m'
    
    VERSION = "4.0.0.113"
    APP_NAME = "DSTerminal WiFi Security Audit"
    
    def __init__(self, interface: Optional[str] = None):
        self.interface = interface
        self.system = platform.system().lower()
        self.hostname = socket.gethostname()
        self.report_id = self._generate_report_id()
        self.timestamp = datetime.now()
        
        self.results = {
            'report_id': self.report_id,
            'version': self.VERSION,
            'timestamp': self.timestamp.isoformat(),
            'system': self.system,
            'hostname': self.hostname,
            'interface': interface,
            'access_points': [],
            'security_findings': [],
            'recommendations': [],
            'summary': {
                'total_aps': 0,
                'secured_aps': 0,
                'open_aps': 0,
                'wep_aps': 0,
                'wpa_aps': 0,
                'wpa2_aps': 0,
                'wpa3_aps': 0,
                'highest_signal': 0,
                'rogue_aps': 0
            }
        }
        self._last_export_key = None
        self._last_export_path = None
        
        # Pen typing settings - CONSTANT SPEED
        self.pen_speed = 0.035
        self.pen_variance = 0.008
        self.auto_break_chars = 80
        self.current_line_length = 0
        
        # Get terminal width for centering
        try:
            self.term_width = shutil.get_terminal_size().columns
            if self.term_width < 80:
                self.term_width = 80
            if self.term_width > 120:
                self.term_width = 120
        except:
            self.term_width = 80
    
    def _generate_report_id(self) -> str:
        """Generate a unique report ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        return f"WIFI-{timestamp}-{random_suffix}"
    
    # ========================================================================
    # GLOWING NEON COLOR HELPERS
    # ========================================================================
    
    def _glow(self, text: str, color: str, blink: bool = False, bold: bool = True) -> str:
        """Apply glowing neon effect to text."""
        result = ""
        if bold:
            result += self.BOLD
        if blink:
            result += self.BLINK_ON
        result += color
        result += text
        result += Style.RESET_ALL
        if blink:
            result += self.BLINK_OFF
        return result
    
    def _colorize(self, text: str, color: str) -> str:
        """Simple colorize without glow."""
        return color + text + Style.RESET_ALL
    
    # ========================================================================
    # HUMAN-LIKE PEN TYPING ENGINE
    # ========================================================================
    
    def pen_type(self, text: str, color: Optional[str] = None, 
                 speed: Optional[float] = None, auto_break: bool = True,
                 indent: int = 0, newline: bool = True, glow: bool = False,
                 blink: bool = False, bold: bool = False):
        """Human-like pen typing with glowing neon effects."""
        import sys
        import time
        import random
        
        delay = speed if speed is not None else self.pen_speed
        
        # Add indent
        if indent > 0:
            sys.stdout.write(" " * indent)
            sys.stdout.flush()
            self.current_line_length += indent
        
        # Apply effects
        if color:
            if glow:
                sys.stdout.write(self.BOLD)
            if blink:
                sys.stdout.write(self.BLINK_ON)
            sys.stdout.write(color)
            sys.stdout.flush()
        
        # Process text with auto line breaks
        if auto_break and len(text) > self.auto_break_chars:
            words = text.split()
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 > self.auto_break_chars:
                    self._type_line(current_line.rstrip(), delay)
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    if indent > 0:
                        sys.stdout.write(" " * indent)
                        sys.stdout.flush()
                    current_line = word + " "
                else:
                    current_line += word + " "
            
            if current_line:
                self._type_line(current_line.rstrip(), delay)
        else:
            self._type_line(text, delay)
        
        # Reset effects
        if color:
            if blink:
                sys.stdout.write(self.BLINK_OFF)
            sys.stdout.write(Style.RESET_ALL)
            sys.stdout.flush()
        
        if newline:
            sys.stdout.write("\n")
            sys.stdout.flush()
            self.current_line_length = 0
    
    def _type_line(self, text: str, delay: float):
        """Type a single line with human-like rhythm."""
        import sys
        import time
        import random
        
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            self.current_line_length += 1
            
            if char in ".!?,":
                time.sleep(delay * 1.8)
            elif char in ";:":
                time.sleep(delay * 1.3)
            elif char == " ":
                time.sleep(delay * 0.6)
            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                time.sleep(delay * 1.15)
            else:
                time.sleep(delay + (random.random() - 0.5) * self.pen_variance)
    
    # ========================================================================
    # GLOWING NEON BOX DRAWING WITH PROPER SPACING
    # ========================================================================
    
    def _draw_glow_box(self, title: str, content_lines: List[str], 
                       title_color: str, border_color: str,
                       content_color: Optional[str] = None,
                       width: Optional[int] = None,
                       blink_title: bool = False,
                       glow_border: bool = True):
        """
        Draw a glowing neon hacker-styled centered box with proper spacing.
        """
        import textwrap
        
        content_color = content_color or Fore.LIGHTGREEN_EX
        
        term = shutil.get_terminal_size((100, 30))
        
        if width is None:
            width = min(term.columns - 6, 110)
        
        width = max(width, 60)
        left_margin = max(0, (term.columns - width) // 2)
        inner = width - 4
        
        # Wrap content with proper spacing
        wrapped = []
        for line in content_lines:
            if not line.strip():
                wrapped.append("")
                continue
            # Remove any trailing spaces from the line before wrapping
            line = line.rstrip()
            wrapped.extend(
                textwrap.wrap(
                    line,
                    inner,
                    break_long_words=False,
                    replace_whitespace=False
                )
            )
        
        # Build box parts with glow
        glow_prefix = self.BOLD if glow_border else ""
        top = glow_prefix + border_color + "╔" + "═" * (width - 2) + "╗" + Style.RESET_ALL
        mid = glow_prefix + border_color + "╠" + "═" * (width - 2) + "╣" + Style.RESET_ALL
        bot = glow_prefix + border_color + "╚" + "═" * (width - 2) + "╝" + Style.RESET_ALL
        
        title_text = f" {title} ".center(width - 2)
        title_prefix = self.BOLD
        if blink_title:
            title_prefix += self.BLINK_ON
        title_line = title_prefix + title_color + "║" + title_text + "║" + Style.RESET_ALL
        if blink_title:
            title_line += self.BLINK_OFF
        
        # Print box
        print()
        print(" " * left_margin + top)
        print(" " * left_margin + title_line)
        print(" " * left_margin + mid)
        
        for line in wrapped:
            border_prefix = glow_prefix if glow_border else ""
            print(" " * left_margin + border_prefix + border_color + "║ " + Style.RESET_ALL, end="")
            
            # Center content within the box - pad to full inner width
            padded_line = line.ljust(inner)
            self.pen_type(
                padded_line,
                color=content_color,
                speed=self.pen_speed,
                newline=False,
                glow=True
            )
            
            print(" " * left_margin + border_prefix + border_color + "║" + Style.RESET_ALL)
            time.sleep(self.pen_speed * 0.5)
        
        print(" " * left_margin + bot)
        print()
        time.sleep(self.pen_speed * 1.5)
    
    # ========================================================================
    # BANNER WITH PROPER ASCII SPACING
    # ========================================================================
    
    def show_banner(self):
        """Display the WiFi audit banner with proper ASCII spacing."""
        import shutil
        
        # Get terminal dimensions
        term = shutil.get_terminal_size((100, 30))
        width = min(term.columns - 6, 110)
        width = max(width, 60)
        left_margin = max(0, (term.columns - width) // 2)
        
        # Print top border
        print()
        print(" " * left_margin + Fore.CYAN + "╔" + "═" * (width - 2) + "╗" + Style.RESET_ALL)
        print(" " * left_margin + Fore.CYAN + "║" + Style.RESET_ALL + " " * (width - 2) + Fore.CYAN + "║" + Style.RESET_ALL)
        
        # ASCII Art - properly spaced
        ascii_art = [
            "    ██╗    ██╗██╗███████╗██╗    █████╗ ██╗   ██╗██████╗ ██╗████████╗",
            "    ██║    ██║██║██╔════╝██║   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝",
            "    ██║ █╗ ██║██║█████╗  ██║   ███████║██║   ██║██   ██╔██║   ██║   ",
            "    ██║███╗██║██║██╔══╝  ██║   ██╔══██║██║   ██║██   ██╗██║   ██║   ",
            "    ╚███╔███╔╝██║██║     ██║   ██║  ██║╚██████╔╝██║█║██║██║   ██║   ",
            "     ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   "
        ]
        
        # Calculate the maximum line length for proper spacing
        max_len = max(len(line) for line in ascii_art)
        
        for line in ascii_art:
            # Calculate padding to center the ASCII art within the box
            padding = (width - max_len - 10) // 2
            print(" " * left_margin + Fore.CYAN + "║" + Style.RESET_ALL + 
                  " " * padding + Fore.LIGHTGREEN_EX + line + Style.RESET_ALL + 
                  " " * (width - max_len - padding - 10) + Fore.CYAN + "║" + Style.RESET_ALL)
        
        # Title
        title = f"🔐 WiFi Security Audit Engine v{self.VERSION}"
        print(" " * left_margin + Fore.CYAN + "║" + Style.RESET_ALL + 
              " " * ((width - 2 - len(title)) // 2) + 
              Fore.LIGHTCYAN_EX + title + Style.RESET_ALL + 
              " " * ((width - 2 - len(title)) // 2) + Fore.CYAN + "║" + Style.RESET_ALL)
        
        # Bottom border
        print(" " * left_margin + Fore.CYAN + "║" + Style.RESET_ALL + " " * (width - 2) + Fore.CYAN + "║" + Style.RESET_ALL)
        print(" " * left_margin + Fore.CYAN + "╚" + "═" * (width - 2) + "╝" + Style.RESET_ALL)
        print()
        time.sleep(0.5)
    
    # ========================================================================
    # GET CONNECTED NETWORK - REFRESHED EACH SCAN
    # ========================================================================
    
    def _get_connected_network(self) -> Dict:
        """Get currently connected WiFi network info."""
        connected = {}
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.splitlines():
                line = line.strip()
                
                # SSID - skip if it's "SSID" header
                if line.startswith("SSID") and "BSSID" not in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        ssid = parts[1].strip()
                        if ssid and ssid != "SSID":
                            connected["ssid"] = ssid
                
                # BSSID - extract MAC address
                elif "BSSID" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        bssid = parts[1].strip()
                        if bssid and bssid != "BSSID":
                            connected["bssid"] = self.normalize_bssid(bssid)
                
                # Signal strength
                elif "Signal" in line and "%" in line:
                    m = re.search(r"(\d+)%", line)
                    if m:
                        connected["signal"] = int(m.group(1))
                
                # Authentication
                elif "Authentication" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        connected["authentication"] = parts[1].strip()
                
                # Radio type
                elif "Radio type" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        connected["radio_type"] = parts[1].strip()
                
                # Channel
                elif "Channel" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        connected["channel"] = parts[1].strip()
                
        except Exception as e:
            pass
        
        return connected
    
    def normalize_bssid(self, bssid: str) -> str:
        """Normalize BSSID format for comparison."""
        if not bssid:
            return ""
        return bssid.upper().replace("-", ":").strip()
    
    # ========================================================================
    # TYPING HELPERS WITH GLOW
    # ========================================================================
    
    def pen_status(self, text: str, color: str = Fore.LIGHTCYAN_EX, glow: bool = True):
        self.pen_type(f"[*] {text}", color=color, glow=glow)
    
    def pen_success(self, text: str, color: str = Fore.LIGHTGREEN_EX, glow: bool = True):
        self.pen_type(f"[+] {text}", color=color, glow=glow)
    
    def pen_error(self, text: str, color: str = Fore.LIGHTRED_EX, glow: bool = True):
        self.pen_type(f"[!] {text}", color=color, glow=glow)
    
    def pen_warning(self, text: str, color: str = Fore.LIGHTYELLOW_EX, glow: bool = True):
        self.pen_type(f"[?] {text}", color=color, glow=glow)
    
    def pen_finding(self, text: str, severity: str = "INFO"):
        severity_colors = {
            "CRITICAL": Fore.LIGHTRED_EX,
            "HIGH": Fore.LIGHTYELLOW_EX,
            "MEDIUM": Fore.LIGHTCYAN_EX,
            "LOW": Fore.LIGHTGREEN_EX,
            "INFO": Fore.LIGHTWHITE_EX
        }
        severity_prefix = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "🔍",
            "LOW": "ℹ️",
            "INFO": "📌"
        }
        color = severity_colors.get(severity, Fore.LIGHTWHITE_EX)
        prefix = severity_prefix.get(severity, "")
        self.pen_type(f"{prefix} {text}", color=color, glow=True)
    
    # ========================================================================
    # PLATFORM-SPECIFIC INTERFACE DETECTION
    # ========================================================================
    
    def _detect_windows_interface(self) -> Optional[str]:
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n'):
                if 'Name' in line and ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        iface_name = parts[1].strip()
                        if iface_name and iface_name != 'Name':
                            return iface_name
        except:
            pass
        return None
    
    def _detect_linux_interface(self) -> Optional[str]:
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    return line.split()[0]
        except:
            pass
        return None
    
    def _detect_macos_interface(self) -> Optional[str]:
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=10)
            current_iface = None
            for line in result.stdout.split('\n'):
                if line and not line.startswith(' '):
                    iface = line.split(':')[0]
                    if iface and iface != 'lo0' and 'awdl' not in iface:
                        current_iface = iface
                elif current_iface and 'status: active' in line:
                    return current_iface
        except:
            pass
        return None
    
    # ========================================================================
    # WINDOWS WIFI AUDIT IMPLEMENTATION
    # ========================================================================
    
    def _wifi_audit_windows(self):
        """Windows WiFi audit implementation."""
        import ctypes
        
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            is_admin = False
        
        if not is_admin:
            self._draw_glow_box(
                "⚠️ Warning",
                ["Running without admin privileges - scan results may be limited"],
                title_color=Fore.LIGHTYELLOW_EX,
                border_color=Fore.LIGHTYELLOW_EX,
                content_color=Fore.LIGHTYELLOW_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
        
        self._draw_glow_box(
            "📡 Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.5)
        
        # Get connected network info - REFRESHED EACH SCAN
        connected_network = self._get_connected_network()
        connected_bssid = self.normalize_bssid(connected_network.get('bssid', ''))
        connected_signal = connected_network.get('signal', 0)
        connected_ssid = connected_network.get('ssid', '')
        
        # Scan for networks
        try:
            # First try with mode=bssid to get BSSID details
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], 
                capture_output=True, text=True, timeout=30
            )
            
            # If that fails or returns empty, try without mode
            if result.returncode != 0 or not result.stdout.strip():
                result = subprocess.run(
                    ['netsh', 'wlan', 'show', 'networks'], 
                    capture_output=True, text=True, timeout=30
                )
            
            if result.stdout.strip():
                self._parse_windows_output(result.stdout, connected_network)
            else:
                self._draw_glow_box(
                    "⚠️ No Networks Found",
                    ["No network data received. Check your WiFi adapter."],
                    title_color=Fore.LIGHTYELLOW_EX,
                    border_color=Fore.LIGHTYELLOW_EX,
                    content_color=Fore.LIGHTYELLOW_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                
        except subprocess.TimeoutExpired:
            self._draw_glow_box(
                "❌ Timeout",
                ["Scan timed out"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
        except Exception as e:
            self._draw_glow_box(
                "❌ Error",
                [f"Error during scan: {str(e)}"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
        
        # If we found no access points but have connected network info, add it
        if not self.results['access_points'] and connected_ssid:
            ap = {
                'ssid': connected_ssid,
                'bssid': connected_bssid if connected_bssid else 'Unknown',
                'signal': connected_signal,
                'security': connected_network.get('security', 'Unknown'),
                'connected': True,
                'authentication': connected_network.get('authentication', ''),
                'channel': connected_network.get('channel', ''),
                'radio_type': connected_network.get('radio_type', '')
            }
            self.results['access_points'].append(ap)
    
    def _parse_windows_output(self, output: str, connected_network: Dict):
        """Parse Windows netsh output using a state-machine approach."""
        connected_bssid = self.normalize_bssid(connected_network.get('bssid', ''))
        connected_signal = connected_network.get('signal', 0)
        connected_ssid = connected_network.get('ssid', '')
        
        # Clear existing access points
        self.results['access_points'] = []
        
        # State machine variables
        current_ssid = None
        current_auth = None
        current_encryption = None
        current_network_type = None
        
        bssid_entries = []
        current_bssid = None
        current_signal = None
        current_channel = None
        current_radio_type = None
        current_band = None
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.rstrip()
            
            if not line:
                continue
            
            # Check for SSID header - "SSID 1 : SomeNetwork"
            ssid_match = re.match(r'^\s*SSID\s+\d+\s+:\s+(.+)$', line, re.IGNORECASE)
            if ssid_match:
                # If we have a previous BSSID, save it
                if current_bssid and current_ssid:
                    bssid_entries.append({
                        'ssid': current_ssid,
                        'auth': current_auth,
                        'encryption': current_encryption,
                        'network_type': current_network_type,
                        'bssid': current_bssid,
                        'signal': current_signal,
                        'channel': current_channel,
                        'radio_type': current_radio_type,
                        'band': current_band
                    })
                
                # Start new SSID section
                current_ssid = ssid_match.group(1).strip()
                current_auth = None
                current_encryption = None
                current_network_type = None
                current_bssid = None
                current_signal = None
                current_channel = None
                current_radio_type = None
                current_band = None
                continue
            
            # Check for Authentication
            if current_ssid:
                auth_match = re.match(r'^\s*Authentication\s+:\s+(.+)$', line, re.IGNORECASE)
                if auth_match:
                    current_auth = auth_match.group(1).strip()
                    continue
                
                # Check for Encryption
                enc_match = re.match(r'^\s*Encryption\s+:\s+(.+)$', line, re.IGNORECASE)
                if enc_match:
                    current_encryption = enc_match.group(1).strip()
                    continue
                
                # Check for Network type
                net_match = re.match(r'^\s*Network type\s+:\s+(.+)$', line, re.IGNORECASE)
                if net_match:
                    current_network_type = net_match.group(1).strip()
                    continue
                
                # Check for BSSID header
                bssid_match = re.match(r'^\s*BSSID\s+\d+\s+:\s+([0-9A-Fa-f:]+)$', line, re.IGNORECASE)
                if bssid_match:
                    # If we have a previous BSSID in this SSID section, save it
                    if current_bssid and current_ssid:
                        bssid_entries.append({
                            'ssid': current_ssid,
                            'auth': current_auth,
                            'encryption': current_encryption,
                            'network_type': current_network_type,
                            'bssid': current_bssid,
                            'signal': current_signal,
                            'channel': current_channel,
                            'radio_type': current_radio_type,
                            'band': current_band
                        })
                    
                    current_bssid = self.normalize_bssid(bssid_match.group(1))
                    current_signal = None
                    current_channel = None
                    current_radio_type = None
                    current_band = None
                    continue
                
                # Check for Signal (only if we're inside a BSSID block)
                if current_bssid:
                    signal_match = re.match(r'^\s*Signal\s+:\s+(\d+)%$', line, re.IGNORECASE)
                    if signal_match:
                        current_signal = int(signal_match.group(1))
                        continue
                    
                    # Check for Channel
                    channel_match = re.match(r'^\s*Channel\s+:\s+(\d+)$', line, re.IGNORECASE)
                    if channel_match:
                        current_channel = int(channel_match.group(1))
                        continue
                    
                    # Check for Radio type
                    radio_match = re.match(r'^\s*Radio type\s+:\s+(.+)$', line, re.IGNORECASE)
                    if radio_match:
                        current_radio_type = radio_match.group(1).strip()
                        continue
                    
                    # Check for Band
                    band_match = re.match(r'^\s*Band\s+:\s+(.+)$', line, re.IGNORECASE)
                    if band_match:
                        current_band = band_match.group(1).strip()
                        continue
        
        # Don't forget the last BSSID
        if current_bssid and current_ssid:
            bssid_entries.append({
                'ssid': current_ssid,
                'auth': current_auth,
                'encryption': current_encryption,
                'network_type': current_network_type,
                'bssid': current_bssid,
                'signal': current_signal,
                'channel': current_channel,
                'radio_type': current_radio_type,
                'band': current_band
            })
        
        # ============================================================
        # Build AP objects from parsed entries
        # ============================================================
        for entry in bssid_entries:
            # Determine security type from auth
            security = 'Unknown'
            if entry['auth']:
                if 'WPA3' in entry['auth']:
                    security = 'WPA3'
                elif 'WPA2' in entry['auth']:
                    security = 'WPA2'
                elif 'WPA' in entry['auth']:
                    security = 'WPA'
                elif 'WEP' in entry['auth']:
                    security = 'WEP'
                elif 'Open' in entry['auth'] or 'None' in entry['auth']:
                    security = 'Open'
            
            ap = {
                'ssid': entry['ssid'] if entry['ssid'] else '<Hidden>',
                'bssid': entry['bssid'],
                'signal': entry['signal'] if entry['signal'] is not None else 0,
                'security': security,
                'authentication': entry['auth'] if entry['auth'] else 'Unknown',
                'encryption': entry['encryption'] if entry['encryption'] else 'Unknown',
                'channel': entry['channel'] if entry['channel'] is not None else None,
                'radio_type': entry['radio_type'] if entry['radio_type'] else None,
                'band': entry['band'] if entry['band'] else None,
                'connected': False
            }
            
            # Check if this is the connected network
            if connected_bssid and entry['bssid'] == connected_bssid:
                ap['connected'] = True
                if connected_signal > 0:
                    ap['signal'] = connected_signal
                if connected_ssid:
                    ap['ssid'] = connected_ssid
            elif connected_ssid and ap['ssid'] == connected_ssid and not connected_bssid:
                ap['connected'] = True
                if connected_signal > 0:
                    ap['signal'] = connected_signal
            
            self.results['access_points'].append(ap)
        
        # ============================================================
        # If connected AP wasn't found, add it from connected_network
        # ============================================================
        if connected_bssid:
            found = any(ap.get('bssid') == connected_bssid for ap in self.results['access_points'])
            if not found and connected_ssid:
                ap = {
                    'ssid': connected_ssid,
                    'bssid': connected_bssid,
                    'signal': connected_signal,
                    'security': connected_network.get('security', 'Unknown'),
                    'authentication': connected_network.get('authentication', 'Unknown'),
                    'connected': True
                }
                self.results['access_points'].append(ap)
        
        # ============================================================
        # Deduplicate - keep only unique BSSIDs
        # ============================================================
        unique_aps = {}
        for ap in self.results['access_points']:
            bssid = ap.get('bssid', '')
            if bssid and bssid != 'Unknown':
                if bssid in unique_aps:
                    # Merge if needed (keep connected, better security, higher signal)
                    existing = unique_aps[bssid]
                    if ap.get('connected') and not existing.get('connected'):
                        unique_aps[bssid] = ap
                    elif ap.get('security') != 'Unknown' and existing.get('security') == 'Unknown':
                        unique_aps[bssid] = ap
                    elif ap.get('signal', 0) > existing.get('signal', 0):
                        unique_aps[bssid] = ap
                else:
                    unique_aps[bssid] = ap
        
        self.results['access_points'] = list(unique_aps.values())
        
        # ============================================================
        # Ensure connected AP is correctly marked and sorted
        # ============================================================
        for ap in self.results['access_points']:
            if ap.get('bssid') == connected_bssid:
                ap['connected'] = True
                if connected_ssid:
                    ap['ssid'] = connected_ssid
                if connected_signal > 0:
                    ap['signal'] = connected_signal
                break
        
        # Sort so connected AP is first
        self.results['access_points'].sort(
            key=lambda ap: (
                not ap.get('connected', False),
                -ap.get('signal', 0)
            )
        )
    def _wifi_audit_linux(self):
        """Linux WiFi audit implementation."""
        self._draw_glow_box(
            "📡 Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.5)
        
        try:
            iwconfig_result = subprocess.run(['iwconfig', self.interface],
                                             capture_output=True, text=True, timeout=10)
            if "unassociated" in iwconfig_result.stdout:
                self._draw_glow_box(
                    "ℹ️ Info",
                    ["Interface not associated with any network"],
                    title_color=Fore.LIGHTCYAN_EX,
                    border_color=Fore.LIGHTCYAN_EX,
                    content_color=Fore.LIGHTCYAN_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
            
            scan_result = subprocess.run(['sudo', 'iwlist', self.interface, 'scan'], 
                                        capture_output=True, text=True, timeout=30)
            
            if scan_result.returncode != 0:
                self._draw_glow_box(
                    "⚠️ Permission",
                    ["Scan may require root privileges. Trying without sudo..."],
                    title_color=Fore.LIGHTYELLOW_EX,
                    border_color=Fore.LIGHTYELLOW_EX,
                    content_color=Fore.LIGHTYELLOW_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                scan_result = subprocess.run(['iwlist', self.interface, 'scan'], 
                                            capture_output=True, text=True, timeout=30)
            
            if scan_result.returncode != 0:
                self._draw_glow_box(
                    "❌ Error",
                    ["Scan failed. Try running with sudo."],
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTRED_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                return
            
            output = scan_result.stdout
            cells = output.split('Cell ')
            
            self._draw_glow_box(
                "🔍 Analyzing",
                ["Analyzing discovered networks..."],
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTCYAN_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.5)
            
            for cell in cells[1:]:
                ap = {}
                
                # BSSID - FULL MAC ADDRESS
                addr_match = re.search(r'Address: ([0-9a-fA-F:]+)', cell, re.IGNORECASE)
                if addr_match:
                    ap['bssid'] = self.normalize_bssid(addr_match.group(1))
                else:
                    addr_match2 = re.search(r'([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})', cell, re.IGNORECASE)
                    if addr_match2:
                        ap['bssid'] = self.normalize_bssid(addr_match2.group(1))
                
                # ESSID
                essid_match = re.search(r'ESSID:"([^"]+)"', cell)
                ap['ssid'] = essid_match.group(1) if essid_match else '<Hidden>'
                
                # Channel
                channel_match = re.search(r'Channel:(\d+)', cell)
                if channel_match:
                    ap['channel'] = int(channel_match.group(1))
                
                # Signal
                quality_match = re.search(r'Quality=(\d+)/(\d+)', cell)
                if quality_match:
                    quality = int(quality_match.group(1))
                    max_quality = int(quality_match.group(2))
                    ap['signal'] = int((quality / max_quality) * 100)
                
                # Security
                if 'WPA2' in cell or 'IEEE 802.11i' in cell:
                    ap['security'] = 'WPA2'
                elif 'WPA' in cell:
                    ap['security'] = 'WPA'
                elif 'WEP' in cell:
                    ap['security'] = 'WEP'
                else:
                    ap['security'] = 'Open'
                
                if ap:
                    self.results['access_points'].append(ap)
            
        except subprocess.TimeoutExpired:
            self._draw_glow_box(
                "❌ Timeout",
                ["Scan timed out"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
        except Exception as e:
            self._draw_glow_box(
                "❌ Error",
                [f"Error during scan: {str(e)}"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
    
    def _wifi_audit_macos(self):
        """macOS WiFi audit implementation."""
        self._draw_glow_box(
            "📡 Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.5)
        
        try:
            airport_path = None
            for path in ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
                        '/usr/sbin/airport']:
                if os.path.exists(path):
                    airport_path = path
                    break
            
            if not airport_path:
                self._draw_glow_box(
                    "⚠️ Airport Not Found",
                    ["Airport command not found"],
                    title_color=Fore.LIGHTYELLOW_EX,
                    border_color=Fore.LIGHTYELLOW_EX,
                    content_color=Fore.LIGHTYELLOW_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                return
            
            scan_result = subprocess.run([airport_path, '-s'], capture_output=True, text=True, timeout=30)
            
            if scan_result.returncode != 0:
                self._draw_glow_box(
                    "❌ Scan Failed",
                    ["Failed to scan networks"],
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTRED_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                return
            
            lines = scan_result.stdout.split('\n')
            
            if len(lines) > 1:
                header = lines[0]
                columns = ['SSID', 'BSSID', 'RSSI', 'CHANNEL', 'SECURITY']
                col_positions = {}
                
                for col in columns:
                    pos = header.find(col)
                    if pos != -1:
                        col_positions[col] = pos
                
                self._draw_glow_box(
                    "🔍 Analyzing",
                    ["Analyzing discovered networks..."],
                    title_color=Fore.LIGHTCYAN_EX,
                    border_color=Fore.LIGHTCYAN_EX,
                    content_color=Fore.LIGHTCYAN_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                time.sleep(0.5)
                
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    
                    ap = {}
                    
                    # SSID
                    if 'SSID' in col_positions:
                        ssid_start = col_positions['SSID']
                        ssid_end = col_positions.get('BSSID', len(line))
                        ap['ssid'] = line[ssid_start:ssid_end].strip()
                        if ap['ssid'] and ap['ssid'] == 'SSID':
                            continue
                    
                    # BSSID - FULL MAC ADDRESS
                    if 'BSSID' in col_positions:
                        bssid_start = col_positions['BSSID']
                        bssid_end = col_positions.get('RSSI', len(line))
                        bssid = line[bssid_start:bssid_end].strip()
                        if bssid and ':' in bssid:
                            ap['bssid'] = self.normalize_bssid(bssid)
                    
                    # RSSI
                    if 'RSSI' in col_positions:
                        rssi_start = col_positions['RSSI']
                        rssi_end = col_positions.get('CHANNEL', len(line))
                        rssi = line[rssi_start:rssi_end].strip()
                        if rssi:
                            try:
                                ap['signal'] = int(rssi)
                            except:
                                pass
                    
                    # Channel
                    if 'CHANNEL' in col_positions:
                        channel_start = col_positions['CHANNEL']
                        channel_end = col_positions.get('SECURITY', len(line))
                        channel = line[channel_start:channel_end].strip()
                        if channel:
                            try:
                                ap['channel'] = int(channel.split()[0])
                            except:
                                pass
                    
                    # Security
                    if 'SECURITY' in col_positions:
                        sec_start = col_positions['SECURITY']
                        sec = line[sec_start:].strip()
                        if sec:
                            ap['security'] = sec
                            if 'WPA3' in sec:
                                ap['security_type'] = 'WPA3'
                            elif 'WPA2' in sec:
                                ap['security_type'] = 'WPA2'
                            elif 'WPA' in sec:
                                ap['security_type'] = 'WPA'
                            elif 'WEP' in sec:
                                ap['security_type'] = 'WEP'
                            elif sec == 'NONE' or 'Open' in sec:
                                ap['security_type'] = 'Open'
                    
                    if ap and 'ssid' in ap:
                        self.results['access_points'].append(ap)
            
        except subprocess.TimeoutExpired:
            self._draw_glow_box(
                "❌ Timeout",
                ["Scan timed out"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
        except Exception as e:
            self._draw_glow_box(
                "❌ Error",
                [f"Error during scan: {str(e)}"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
    
    # ========================================================================
    # ANALYSIS
    # ========================================================================
    
    def _analyze_wifi_findings(self):
        """Analyze WiFi findings and generate security recommendations."""
        aps = self.results.get('access_points', [])
        
        self.results['summary']['total_aps'] = len(aps)
        
        security_counts = {'Open': 0, 'WEP': 0, 'WPA': 0, 'WPA2': 0, 'WPA3': 0, 'Unknown': 0}
        
        for ap in aps:
            sec = ap.get('security', 'Unknown')
            
            if 'WPA3' in sec:
                sec_type = 'WPA3'
            elif 'WPA2' in sec:
                sec_type = 'WPA2'
            elif 'WPA' in sec:
                sec_type = 'WPA'
            elif 'WEP' in sec:
                sec_type = 'WEP'
            elif sec == 'Open' or sec == 'NONE' or sec == 'None':
                sec_type = 'Open'
            else:
                sec_type = 'Unknown'
            
            ap['security_type'] = sec_type
            security_counts[sec_type] = security_counts.get(sec_type, 0) + 1
            
            # Security findings
            if sec_type == 'Open':
                self.results['security_findings'].append({
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'Open network - No encryption',
                    'severity': 'CRITICAL'
                })
            elif sec_type == 'WEP':
                self.results['security_findings'].append({
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WEP encryption - Vulnerable to attacks',
                    'severity': 'HIGH'
                })
            elif sec_type == 'WPA':
                self.results['security_findings'].append({
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WPA encryption - Deprecated, vulnerable to KRACK',
                    'severity': 'MEDIUM'
                })
            
            # Rogue AP detection
            ssid = ap.get('ssid', '')
            if ssid and ssid != '<Hidden>':
                same_ssid_aps = [a for a in aps if a.get('ssid') == ssid]
                if len(same_ssid_aps) > 1:
                    for other_ap in same_ssid_aps:
                        if other_ap.get('security_type') == 'Open' and ap.get('security_type') != 'Open':
                            self.results['security_findings'].append({
                                'ap': ssid,
                                'bssid': other_ap.get('bssid', 'Unknown'),
                                'finding': 'Potential rogue AP - Duplicate SSID with different security',
                                'severity': 'CRITICAL'
                            })
                            self.results['summary']['rogue_aps'] += 1
        
        self.results['summary']['secured_aps'] = len(aps) - security_counts.get('Open', 0)
        self.results['summary']['open_aps'] = security_counts.get('Open', 0)
        self.results['summary']['wep_aps'] = security_counts.get('WEP', 0)
        self.results['summary']['wpa_aps'] = security_counts.get('WPA', 0)
        self.results['summary']['wpa2_aps'] = security_counts.get('WPA2', 0)
        self.results['summary']['wpa3_aps'] = security_counts.get('WPA3', 0)
        
        # Recommendations
        recommendations = []
        if security_counts.get('Open', 0) > 0:
            recommendations.append("🔴 Open networks detected - Disable open networks or implement WPA3 encryption")
        if security_counts.get('WEP', 0) > 0:
            recommendations.append("🔴 WEP encryption detected - Upgrade to WPA3 immediately")
        if security_counts.get('WPA', 0) > 0:
            recommendations.append("🟡 WPA encryption detected - Upgrade to WPA2/WPA3")
        if self.results['summary'].get('rogue_aps', 0) > 0:
            recommendations.append("🔴 Rogue Access Points detected - Investigate and remove unauthorized APs")
        if security_counts.get('WPA3', 0) == 0 and security_counts.get('WPA2', 0) > 0:
            recommendations.append("🟢 WPA2 detected - Consider upgrading to WPA3")
        if not recommendations:
            recommendations.append("✅ No critical security issues found - Continue monitoring")
        
        self.results['recommendations'] = recommendations
    
    # ========================================================================
    # DISPLAY RESULTS WITH GLOWING NEON
    # ========================================================================
    
    def _display_results(self):
        """Display audit results with glowing neon effects."""
        summary = self.results.get('summary', {})
        
        # Summary Box - Glowing Cyan
        summary_lines = [
            f"Total Access Points: {summary.get('total_aps', 0)}",
            f"Secured Networks: {summary.get('secured_aps', 0)}",
            f"Open Networks: {summary.get('open_aps', 0)}",
            f"WEP Networks: {summary.get('wep_aps', 0)}",
            f"WPA Networks: {summary.get('wpa_aps', 0)}",
            f"WPA2 Networks: {summary.get('wpa2_aps', 0)}",
            f"WPA3 Networks: {summary.get('wpa3_aps', 0)}",
            f"Rogue APs Detected: {summary.get('rogue_aps', 0)}"
        ]
        
        self._draw_glow_box(
            "📊 WiFi Audit Summary",
            summary_lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        # Security Distribution - Glowing Magenta
        security_lines = [
            f"WPA3: {summary.get('wpa3_aps', 0)}  {'█' * min(summary.get('wpa3_aps', 0), 20)}",
            f"WPA2: {summary.get('wpa2_aps', 0)}  {'█' * min(summary.get('wpa2_aps', 0), 20)}",
            f"WPA:  {summary.get('wpa_aps', 0)}   {'█' * min(summary.get('wpa_aps', 0), 20)}",
            f"WEP:  {summary.get('wep_aps', 0)}   {'█' * min(summary.get('wep_aps', 0), 20)}",
            f"Open: {summary.get('open_aps', 0)}  {'█' * min(summary.get('open_aps', 0), 20)}"
        ]
        
        self._draw_glow_box(
            "🔐 Security Distribution",
            security_lines,
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTMAGENTA_EX,
            content_color=Fore.LIGHTGREEN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        # Security Score - Glowing Yellow/Green
        total_aps = summary.get('total_aps', 0)
        if total_aps > 0:
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100)
            
            if security_score >= 90:
                score_color = Fore.LIGHTGREEN_EX
                status_text = "EXCELLENT"
            elif security_score >= 70:
                score_color = Fore.LIGHTYELLOW_EX
                status_text = "GOOD"
            elif security_score >= 50:
                score_color = Fore.LIGHTMAGENTA_EX
                status_text = "FAIR"
            else:
                score_color = Fore.LIGHTRED_EX
                status_text = "POOR"
            
            bar_length = 30
            filled = int((security_score / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            score_lines = [
                f"Score: {security_score}/100",
                f"Status: {status_text}",
                f"[{bar}]"
            ]
            
            self._draw_glow_box(
                "📊 Security Score",
                score_lines,
                title_color=Fore.LIGHTYELLOW_EX,
                border_color=Fore.LIGHTYELLOW_EX,
                content_color=score_color,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
        
        # Security Findings - Glowing Red
        findings = self.results.get('security_findings', [])
        if findings:
            finding_lines = []
            for finding in findings[:10]:
                severity = finding.get('severity', 'INFO')
                emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "🔍", "LOW": "ℹ️"}.get(severity, "📌")
                finding_lines.append(f"{emoji} [{severity}] {finding.get('finding', '')} ({finding.get('ap', 'Unknown')})")
            
            if len(findings) > 10:
                finding_lines.append(f"... and {len(findings) - 10} more findings")
            
            self._draw_glow_box(
                "🚨 Security Findings",
                finding_lines,
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
        
        # Recommendations - Glowing Blue
        recommendations = self.results.get('recommendations', [])
        if recommendations:
            rec_lines = []
            for rec in recommendations[:5]:
                rec_lines.append(rec)
            if len(recommendations) > 5:
                rec_lines.append(f"... and {len(recommendations) - 5} more recommendations")
            
            self._draw_glow_box(
                "💡 Recommendations",
                rec_lines,
                title_color=Fore.LIGHTBLUE_EX,
                border_color=Fore.LIGHTBLUE_EX,
                content_color=Fore.LIGHTYELLOW_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
        
        # Access Points - Glowing White/Cyan - FIXED
        access_points = self.results.get('access_points', [])
        if access_points:
            ap_lines = []
            for ap in access_points[:15]:
                # Get SSID
                ssid = ap.get('ssid', '<Hidden>')
                if not ssid or ssid == '' or ssid == 'SSID':
                    ssid = '<Hidden>'
                # Check if SSID looks like a MAC address (contains colons)
                if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', ssid):
                    ssid = '<Hidden>'
                ssid = ssid[:20]  # Truncate to 20 chars
                
                # Get BSSID - FULL MAC - NO TRUNCATION
                bssid = ap.get('bssid', 'Unknown')
                if not bssid or bssid == '':
                    bssid = 'Unknown'
                
                # Get signal
                signal = ap.get('signal', 0)
                if signal is None:
                    signal = 0
                try:
                    signal = int(signal)
                except (ValueError, TypeError):
                    signal = 0
                signal_str = f"{signal}%"
                
                # Get security
                security = ap.get('security_type', ap.get('security', 'Unknown'))
                if not security or security == '':
                    security = 'Unknown'
                security = security[:10]  # Truncate to 10 chars
                
                # Signal indicator
                sig = signal
                sig_indicator = "📶" if sig > 70 else "📡" if sig > 40 else "📻"
                
                # Connected indicator
                connected = "🔗 " if ap.get('connected', False) else ""
                
                # Format the line - ensure proper spacing
                # SSID column width: 20 chars, BSSID column width: 17 chars
                ap_lines.append(f"{sig_indicator} {connected}{ssid:<20} {bssid:<17} {signal_str:>4} {security}")
            
            if len(access_points) > 15:
                ap_lines.append(f"... and {len(access_points) - 15} more")
            
            self._draw_glow_box(
                f"📡 Access Points ({len(access_points)})",
                ap_lines,
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTWHITE_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
    
    # ========================================================================
    # PDF REPORT GENERATION
    # ========================================================================
    
    def _generate_pdf_report(self, filename: str) -> bool:
        """Generate PDF report with DSTerminal v4.0.0.113 watermark."""
        if not PDF_AVAILABLE:
            print(f"{Fore.LIGHTYELLOW_EX}⚠️ PDF generation requires reportlab. Install: pip install reportlab{Style.RESET_ALL}")
            return False
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.pdfgen import canvas
            
            class WatermarkedDocTemplate(SimpleDocTemplate):
                def __init__(self, filename, **kwargs):
                    super().__init__(filename, **kwargs)
                    self.report_id = self._generate_report_id()
                
                def _generate_report_id(self):
                    ts = datetime.now().strftime("%Y%m%d%H%M%S")
                    return f"WIFI-PDF-{ts}"
                
                def afterFlowable(self, flowable):
                    pass
            
            def add_watermark(canvas_obj, doc_obj):
                canvas_obj.saveState()
                
                # Main watermark
                canvas_obj.setFont('Helvetica-Bold', 60)
                canvas_obj.setFillColor(colors.HexColor('#1a1a2e'))
                canvas_obj.setFillAlpha(0.08)
                canvas_obj.saveState()
                page_width, page_height = A4
                canvas_obj.translate(page_width / 2, page_height / 2)
                canvas_obj.rotate(45)
                canvas_obj.drawCentredString(0, 0, "DSTERMINAL")
                canvas_obj.restoreState()
                
                # Version watermark
                canvas_obj.setFont('Helvetica', 25)
                canvas_obj.setFillAlpha(0.06)
                canvas_obj.drawCentredString(page_width / 2, 50, f"v{WiFiAudit.VERSION}")
                
                # Footer with Report ID
                canvas_obj.setFont('Helvetica', 8)
                canvas_obj.setFillAlpha(0.6)
                canvas_obj.setFillColor(colors.HexColor('#666666'))
                footer_text = f"Report ID: {doc_obj.report_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                canvas_obj.drawCentredString(page_width / 2, 20, footer_text)
                
                canvas_obj.restoreState()
            
            doc = WatermarkedDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=colors.HexColor('#00ff00'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#888888'),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#00ffff'),
                spaceAfter=15,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#e0e0e0'),
                alignment=TA_LEFT,
                spaceAfter=6,
                fontName='Helvetica'
            )
            
            # Title
            story.append(Paragraph("DSTERMINAL Cyber-Ops Platform", title_style))
            story.append(Paragraph("WiFi Security Audit Report", subtitle_style))
            story.append(Spacer(1, 15))
            
            # Report Metadata
            metadata_data = [
                ["Report ID:", doc.report_id],
                ["Generated By:", f"DSTERMINAL Cyber-Ops Platform v{WiFiAudit.VERSION}"],
                ["Classification:", "CONFIDENTIAL - Security Team Only"],
                ["Scan Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ["System:", self.system.upper()],
                ["Hostname:", self.hostname],
                ["Interface:", self.interface or "Auto-detected"],
            ]
            
            metadata_table = Table(metadata_data, colWidths=[140, 330])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#00ffff')),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#0d1117')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#33ff33')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ]))
            story.append(metadata_table)
            story.append(Spacer(1, 25))
            
            # Summary
            summary = self.results.get('summary', {})
            story.append(Paragraph("Audit Summary", heading_style))
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Access Points', str(summary.get('total_aps', 0))],
                ['Secured Networks', str(summary.get('secured_aps', 0))],
                ['Open Networks', str(summary.get('open_aps', 0))],
                ['WEP Networks', str(summary.get('wep_aps', 0))],
                ['WPA Networks', str(summary.get('wpa_aps', 0))],
                ['WPA2 Networks', str(summary.get('wpa2_aps', 0))],
                ['WPA3 Networks', str(summary.get('wpa3_aps', 0))],
                ['Rogue APs Detected', str(summary.get('rogue_aps', 0))],
            ]
            
            summary_table = Table(summary_data, colWidths=[200, 100])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ff00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Security Findings
            findings = self.results.get('security_findings', [])
            if findings:
                story.append(Paragraph("Security Findings", heading_style))
                story.append(Spacer(1, 6))
                
                for finding in findings:
                    severity = finding.get('severity', 'UNKNOWN')
                    color_map = {
                        'CRITICAL': colors.red,
                        'HIGH': colors.orange,
                        'MEDIUM': colors.blue,
                        'LOW': colors.green,
                        'INFO': colors.grey
                    }
                    severity_style = ParagraphStyle(
                        f'Severity_{severity}',
                        parent=styles['Normal'],
                        textColor=color_map.get(severity, colors.black),
                        fontName='Helvetica-Bold',
                        fontSize=10
                    )
                    finding_text = f"<b>[{severity}]</b> {finding.get('finding', '')} <i>({finding.get('ap', 'Unknown')})</i>"
                    story.append(Paragraph(finding_text, severity_style))
                    story.append(Spacer(1, 4))
                story.append(Spacer(1, 10))
            
            # Recommendations
            recommendations = self.results.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("Recommendations", heading_style))
                story.append(Spacer(1, 6))
                
                for rec in recommendations:
                    clean_rec = rec.replace('🔴', '[CRITICAL]').replace('🟡', '[MEDIUM]').replace('🟢', '[LOW]').replace('✅', '[OK]')
                    story.append(Paragraph(f"• {clean_rec}", styles['Normal']))
                    story.append(Spacer(1, 4))
                story.append(Spacer(1, 10))
            
            # Access Points
            aps = self.results.get('access_points', [])
            if aps:
                story.append(Paragraph("Access Points", heading_style))
                story.append(Spacer(1, 6))
                
                ap_data = [['SSID', 'BSSID', 'Signal', 'Security', 'Channel']]
                for ap in aps[:50]:
                    ssid = ap.get('ssid', 'Unknown')[:30]
                    bssid = ap.get('bssid', 'Unknown')[:17]
                    signal = f"{ap.get('signal', 0)}%"
                    security = ap.get('security_type', ap.get('security', 'Unknown'))[:10]
                    channel = str(ap.get('channel', 'N/A'))
                    
                    if ap.get('connected', False):
                        ssid = f"🔗 {ssid}"
                    
                    ap_data.append([ssid, bssid, signal, security[:10], channel])
                
                ap_table = Table(ap_data, colWidths=[120, 90, 60, 70, 50])
                ap_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ff00')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(ap_table)
            
            # Security Score
            total_aps = summary.get('total_aps', 0)
            if total_aps > 0:
                story.append(Spacer(1, 20))
                story.append(PageBreak())
                story.append(Paragraph("Security Score Dashboard", heading_style))
                story.append(Spacer(1, 6))
                
                secured = summary.get('secured_aps', 0)
                security_score = int((secured / total_aps) * 100) if total_aps > 0 else 0
                
                score_style = ParagraphStyle(
                    'ScoreStyle',
                    parent=styles['Normal'],
                    fontSize=48,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#00ff00'),
                    fontName='Helvetica-Bold'
                )
                
                score_status = "EXCELLENT" if security_score >= 90 else "GOOD" if security_score >= 70 else "FAIR" if security_score >= 50 else "POOR"
                status_color = colors.green if security_score >= 90 else colors.orange if security_score >= 70 else colors.red
                
                status_style = ParagraphStyle(
                    'StatusStyle',
                    parent=styles['Normal'],
                    fontSize=24,
                    alignment=TA_CENTER,
                    textColor=status_color,
                    fontName='Helvetica-Bold'
                )
                
                story.append(Paragraph(f"{security_score} / 100", score_style))
                story.append(Spacer(1, 6))
                story.append(Paragraph(score_status, status_style))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph("─" * 80, footer_style))
            story.append(Paragraph(f"Generated by DSTerminal v{WiFiAudit.VERSION} WiFi Security Audit Engine", footer_style))
            story.append(Paragraph(f"Report ID: {doc.report_id}", footer_style))
            
            doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
            return True
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}❌ PDF generation failed: {str(e)}{Style.RESET_ALL}")
            return False
    
    # ========================================================================
    # HTML REPORT GENERATION
    # ========================================================================
    
    def _generate_html_report(self, filename: str) -> bool:
        """Generate HTML report with DSTerminal v4.0.0.113 watermark."""
        try:
            summary = self.results.get('summary', {})
            findings = self.results.get('security_findings', [])
            recommendations = self.results.get('recommendations', [])
            aps = self.results.get('access_points', [])
            
            total_aps = summary.get('total_aps', 0)
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100) if total_aps > 0 else 0
            
            # Build findings HTML safely
            findings_html = ""
            if findings:
                findings_html = '<div class="section">\n<h2>🚨 Security Findings</h2>\n'
                for finding in findings[:20]:
                    severity = finding.get('severity', 'UNKNOWN').lower()
                    findings_html += f'''
            <div class="finding {severity}">
                <span class="severity severity-{severity}">{finding.get('severity', 'UNKNOWN')}</span>
                {finding.get('finding', '')}
                <span style="color: #666; font-size: 0.9em;">({finding.get('ap', 'Unknown')})</span>
            </div>
            '''
                if len(findings) > 20:
                    findings_html += f'<div style="color: #666; font-style: italic; margin-top: 10px;">... and {len(findings) - 20} more findings</div>'
                findings_html += '</div>\n'
            
            # Build recommendations HTML safely
            recs_html = ""
            if recommendations:
                recs_html = '<div class="section">\n<h2>💡 Recommendations</h2>\n'
                for rec in recommendations:
                    recs_html += f'<div class="recommendation">{rec}</div>\n'
                recs_html += '</div>\n'
            
            # Build access points HTML safely
            aps_html = ""
            if aps:
                aps_html = f'<div class="section">\n<h2>📡 Access Points ({len(aps)})</h2>\n'
                aps_html += '''
            <table class="ap-table">
                <thead>
                    <tr>
                        <th>SSID</th>
                        <th>BSSID</th>
                        <th>Signal</th>
                        <th>Security</th>
                        <th>Channel</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
            '''
                for ap in aps[:50]:
                    ssid = ap.get('ssid', 'Unknown')[:30]
                    bssid = ap.get('bssid', 'Unknown')
                    signal = ap.get('signal', 0)
                    security_type = ap.get('security_type', ap.get('security', 'Unknown'))
                    
                    # Determine status badge class
                    if security_type in ['WPA2', 'WPA3']:
                        badge_class = 'status-secure'
                    elif security_type == 'WPA':
                        badge_class = 'status-warning'
                    else:
                        badge_class = 'status-open'
                    
                    connected = ap.get('connected', False)
                    connected_html = '<span class="connected-badge">🔗 CONNECTED</span>' if connected else '—'
                    
                    aps_html += f'''
                    <tr>
                        <td>{ssid}</td>
                        <td style="font-family: monospace;">{bssid}</td>
                        <td>{signal}%</td>
                        <td><span class="status-badge {badge_class}">{security_type}</span></td>
                        <td>{ap.get('channel', 'N/A')}</td>
                        <td>{connected_html}</td>
                    </tr>
            '''
                if len(aps) > 50:
                    aps_html += f'<tr><td colspan="6" style="text-align: center; color: #666;">... and {len(aps) - 50} more access points</td></tr>'
                aps_html += '''
                </tbody>
            </table>
        </div>
        '''
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WiFi Security Audit Report - {self.report_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 20px;
            min-height: 100vh;
            position: relative;
        }}
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 120px;
            opacity: 0.04;
            color: #00ff00;
            pointer-events: none;
            z-index: 0;
            font-weight: bold;
            letter-spacing: 15px;
            white-space: nowrap;
            user-select: none;
        }}
        .watermark-version {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            font-size: 18px;
            opacity: 0.08;
            color: #00ff00;
            pointer-events: none;
            z-index: 0;
            font-weight: bold;
            letter-spacing: 3px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(26, 26, 46, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 40px rgba(0, 255, 0, 0.08);
            position: relative;
            z-index: 1;
            border: 1px solid rgba(0, 255, 0, 0.15);
            backdrop-filter: blur(10px);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid rgba(0, 255, 0, 0.2);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #00ff00;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            letter-spacing: 3px;
        }}
        .header .subtitle {{
            color: #33ff33;
            font-size: 1.2em;
            opacity: 0.7;
            margin-top: 5px;
        }}
        .header .report-id {{
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
            padding: 5px 15px;
            display: inline-block;
            border: 1px solid rgba(0, 255, 0, 0.1);
            border-radius: 20px;
        }}
        .section {{
            background: rgba(13, 17, 23, 0.8);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 3px solid #00ff00;
        }}
        .section h2 {{
            color: #00ffff;
            font-size: 1.4em;
            margin-bottom: 15px;
            letter-spacing: 2px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .summary-card {{
            background: rgba(0, 255, 0, 0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid rgba(0, 255, 0, 0.08);
        }}
        .summary-card .value {{
            font-size: 28px;
            font-weight: bold;
            color: #00ff00;
        }}
        .summary-card .label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        .finding {{
            padding: 12px 15px;
            margin: 8px 0;
            border-radius: 5px;
            border-left: 4px solid #666;
            background: rgba(255, 255, 255, 0.02);
        }}
        .finding.critical {{ border-left-color: #ff0000; }}
        .finding.high {{ border-left-color: #ff6600; }}
        .finding.medium {{ border-left-color: #ffcc00; }}
        .finding.low {{ border-left-color: #00ccff; }}
        .finding .severity {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-right: 10px;
        }}
        .severity-critical {{ background: #ff0000; color: white; }}
        .severity-high {{ background: #ff6600; color: white; }}
        .severity-medium {{ background: #ffcc00; color: black; }}
        .severity-low {{ background: #00ccff; color: black; }}
        .recommendation {{
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            background: rgba(0, 255, 0, 0.03);
            border-left: 3px solid #00ff00;
        }}
        .score-bar {{
            width: 100%;
            height: 35px;
            background: #1a1a2e;
            border-radius: 17px;
            overflow: hidden;
            margin: 15px 0;
            border: 1px solid rgba(0, 255, 0, 0.1);
        }}
        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #ff0000, #ffcc00, #00ff00);
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
        }}
        .ap-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 13px;
        }}
        .ap-table th {{
            background: rgba(0, 255, 0, 0.1);
            color: #00ff00;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid rgba(0, 255, 0, 0.2);
        }}
        .ap-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }}
        .ap-table tr:hover {{
            background: rgba(0, 255, 0, 0.03);
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(0, 255, 0, 0.1);
            color: #444;
            font-size: 11px;
        }}
        .footer a {{
            color: #00ff00;
            text-decoration: none;
        }}
        .status-badge {{
            display: inline-block;
            padding: 2px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}
        .status-secure {{ background: rgba(0, 255, 0, 0.2); color: #00ff00; }}
        .status-open {{ background: rgba(255, 0, 0, 0.2); color: #ff0000; }}
        .status-warning {{ background: rgba(255, 204, 0, 0.2); color: #ffcc00; }}
        .connected-badge {{
            color: #00ff00;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="watermark">DSTERMINAL</div>
    <div class="watermark-version">v{WiFiAudit.VERSION}</div>
    
    <div class="container">
        <div class="header">
            <h1>🔐 WiFi Security Audit</h1>
            <div class="subtitle">DSTERMINAL Cyber-Ops Platform v{WiFiAudit.VERSION}</div>
            <div class="report-id">📄 Report ID: {self.report_id}</div>
            <div style="color: #444; font-size: 0.85em; margin-top: 8px;">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Audit Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="value">{summary.get('total_aps', 0)}</div>
                    <div class="label">Total Access Points</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #00ff00;">{summary.get('secured_aps', 0)}</div>
                    <div class="label">Secured Networks</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #ff0000;">{summary.get('open_aps', 0)}</div>
                    <div class="label">Open Networks</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #ff6600;">{summary.get('rogue_aps', 0)}</div>
                    <div class="label">Rogue APs Detected</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔐 Security Distribution</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>WPA3: <span style="color: #00ff00;">{summary.get('wpa3_aps', 0)}</span></div>
                <div>WPA2: <span style="color: #33ff33;">{summary.get('wpa2_aps', 0)}</span></div>
                <div>WPA: <span style="color: #ffcc00;">{summary.get('wpa_aps', 0)}</span></div>
                <div>WEP: <span style="color: #ff6600;">{summary.get('wep_aps', 0)}</span></div>
                <div>Open: <span style="color: #ff0000;">{summary.get('open_aps', 0)}</span></div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Security Score</h2>
            <div style="font-size: 48px; text-align: center; color: {'#00ff00' if security_score >= 70 else '#ffcc00' if security_score >= 50 else '#ff0000'};">
                {security_score}%
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {security_score}%;">
                    {security_score}%
                </div>
            </div>
            <div style="text-align: center; color: {'#00ff00' if security_score >= 70 else '#ffcc00' if security_score >= 50 else '#ff0000'};">
                {'EXCELLENT' if security_score >= 90 else 'GOOD' if security_score >= 70 else 'FAIR' if security_score >= 50 else 'POOR'}
            </div>
        </div>
        
        {findings_html}
        {recs_html}
        {aps_html}
        
        <div class="footer">
            <p>Generated by <strong>DSTERMINAL v{WiFiAudit.VERSION}</strong> WiFi Security Audit Engine</p>
            <p>Report ID: {self.report_id}</p>
            <p style="color: #333; margin-top: 5px;">© 2024 Stark Expo Tech Exchange LTD | All Rights Reserved</p>
        </div>
    </div>
</body>
</html>"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}❌ HTML generation failed: {str(e)}{Style.RESET_ALL}")
            return False
    
    # ========================================================================
    # EXPORT
    # ========================================================================
    
    def _export_results(self) -> Optional[str]:
        """Export results to multiple formats."""
        try:
            export_key = self.results.get('timestamp', '')
            if hasattr(self, '_last_export_key') and self._last_export_key == export_key:
                return self._last_export_path if hasattr(self, '_last_export_path') else None
            
            export_dir = Path.home() / "DSTerminal" / "reports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            base_filename = export_dir / f"wifi_audit_{self.report_id}"
            
            exported_files = []
            export_messages = []
            
            # JSON Export
            json_filename = base_filename.with_suffix('.json')
            with open(json_filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            exported_files.append(str(json_filename))
            # Shorten the path for display
            json_display = str(json_filename).replace(str(export_dir), "~/DSTerminal/reports")
            export_messages.append(f"✅ JSON Report: {json_display}")
            
            # PDF Export
            pdf_filename = base_filename.with_suffix('.pdf')
            if self._generate_pdf_report(str(pdf_filename)):
                exported_files.append(str(pdf_filename))
                pdf_display = str(pdf_filename).replace(str(export_dir), "~/DSTerminal/reports")
                export_messages.append(f"✅ PDF Report: {pdf_display}")
            else:
                export_messages.append(f"⚠️ PDF export skipped")
            
            # HTML Export
            html_filename = base_filename.with_suffix('.html')
            if self._generate_html_report(str(html_filename)):
                exported_files.append(str(html_filename))
                html_display = str(html_filename).replace(str(export_dir), "~/DSTerminal/reports")
                export_messages.append(f"✅ HTML Report: {html_display}")
                
                # Open HTML in browser
                try:
                    import webbrowser
                    webbrowser.open(f"file://{html_filename}")
                    export_messages.append(f"🌐 HTML report opened in browser")
                except:
                    pass
            else:
                export_messages.append(f"⚠️ HTML export skipped")
            
            self._last_export_key = export_key
            self._last_export_path = str(json_filename)
            
            # Display export messages in a box with proper formatting
            self._draw_glow_box(
                "📄 Export Results",
                export_messages,
                title_color=Fore.LIGHTGREEN_EX,
                border_color=Fore.LIGHTGREEN_EX,
                content_color=Fore.LIGHTWHITE_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            
            return str(json_filename)
            
        except Exception as e:
            print(f"{Fore.LIGHTYELLOW_EX}⚠️ Failed to export results: {str(e)}{Style.RESET_ALL}")
            return None
    
    # ========================================================================
    # MAIN RUN
    # ========================================================================
    
    def run(self):
        """Main execution method with glowing neon effects."""
        # Clear screen
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
        # Show banner
        self.show_banner()
        
        # Security Impact Assessment - Glowing Magenta
        self._draw_glow_box(
            "🔐 Security Impact Assessment",
            [
                "Rogue Access Point Detection: Identifying unauthorized APs for MITM protection",
                "Security Protocol Analysis: WEP, WPA, WPA2, WPA3 evaluation",
                "Signal Intelligence: Physical location mapping for device detection",
                "Compliance Verification: PCI-DSS, HIPAA, and regulatory standards"
            ],
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTMAGENTA_EX,
            content_color=Fore.LIGHTCYAN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        # Initialization - Glowing Yellow
        init_lines = [
            f"Platform: {self.system.upper()}",
            f"Host: {self.hostname}",
            f"Interface: {self.interface if self.interface else 'Auto-detecting...'}"
        ]
        
        self._draw_glow_box(
            "🔧 Initializing Audit Engine",
            init_lines,
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTCYAN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        # Auto-detect interface if not provided
        if not self.interface:
            if self.system == "windows":
                self.interface = self._detect_windows_interface()
            elif self.system == "linux":
                self.interface = self._detect_linux_interface()
            elif self.system == "darwin":
                self.interface = self._detect_macos_interface()
            
            if self.interface:
                self._draw_glow_box(
                    "📡 Interface Detected",
                    [f"Interface: {self.interface}"],
                    title_color=Fore.LIGHTGREEN_EX,
                    border_color=Fore.LIGHTGREEN_EX,
                    content_color=Fore.LIGHTGREEN_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                time.sleep(0.3)
            else:
                self._draw_glow_box(
                    "❌ Error",
                    ["No wireless interface detected"],
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTRED_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                return
        
        # Platform-specific scan
        try:
            if self.system == "windows":
                self._draw_glow_box(
                    "📡 Platform Detection",
                    ["Using Windows native WiFi API"],
                    title_color=Fore.LIGHTCYAN_EX,
                    border_color=Fore.LIGHTCYAN_EX,
                    content_color=Fore.LIGHTGREEN_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                time.sleep(0.3)
                self._wifi_audit_windows()
            elif self.system == "linux":
                self._draw_glow_box(
                    "📡 Platform Detection",
                    ["Using Linux iwconfig/iwlist"],
                    title_color=Fore.LIGHTCYAN_EX,
                    border_color=Fore.LIGHTCYAN_EX,
                    content_color=Fore.LIGHTGREEN_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                time.sleep(0.3)
                self._wifi_audit_linux()
            elif self.system == "darwin":
                self._draw_glow_box(
                    "📡 Platform Detection",
                    ["Using macOS airport utility"],
                    title_color=Fore.LIGHTCYAN_EX,
                    border_color=Fore.LIGHTCYAN_EX,
                    content_color=Fore.LIGHTGREEN_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                time.sleep(0.3)
                self._wifi_audit_macos()
            else:
                self._draw_glow_box(
                    "❌ Unsupported Platform",
                    [f"Platform: {self.system} is not supported"],
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTRED_EX,
                    width=None,
                    blink_title=True,
                    glow_border=True
                )
                return
        except Exception as e:
            self._draw_glow_box(
                "❌ Error",
                [f"Error during WiFi audit: {str(e)}"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            return
        
        # Analysis - Glowing Magenta
        self._draw_glow_box(
            "🔬 Analyzing Findings",
            [
                "Processing access point data...",
                "Evaluating security configurations...",
                "Detecting rogue access points...",
                "Generating threat intelligence..."
            ],
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTMAGENTA_EX,
            content_color=Fore.LIGHTCYAN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        self._analyze_wifi_findings()
        
        # Display results
        self._display_results()
        
        # Export - Now with proper path formatting
        export_path = self._export_results()
        
        # Only show export complete if we actually exported something
        if export_path:
            # The export box is already shown inside _export_results
            pass
        else:
            self._draw_glow_box(
                "⚠️ Export Failed",
                ["Failed to export results"],
                title_color=Fore.LIGHTYELLOW_EX,
                border_color=Fore.LIGHTYELLOW_EX,
                content_color=Fore.LIGHTYELLOW_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
        
        # Footer - Glowing Cyan
        self._draw_glow_box(
            "🔐 WiFi Security Audit Complete",
            [
                f"Report ID: {self.report_id}",
                f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Version: DSTerminal v{self.VERSION}"
            ],
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTCYAN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        
        print()
        input(f"{Fore.LIGHTYELLOW_EX}Press Enter to continue...{Style.RESET_ALL}")


# ========================================================================
# MAIN
# ========================================================================

def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WiFi Security Audit Tool')
    parser.add_argument('-i', '--interface', help='Network interface to use')
    parser.add_argument('--no-colors', action='store_true', help='Disable colors')
    parser.add_argument('--speed', type=float, default=0.035, 
                       help='Typing speed in seconds per character (default: 0.035)')
    parser.add_argument('--live', action='store_true', help='Live monitoring mode (refreshes every 2 seconds)')
    args = parser.parse_args()
    
    if args.no_colors:
        global Fore, Style, COLORS_AVAILABLE
        class Fore:
            RESET = ''
            LIGHTGREEN_EX = ''
            LIGHTRED_EX = ''
            LIGHTCYAN_EX = ''
            LIGHTMAGENTA_EX = ''
            LIGHTBLUE_EX = ''
            LIGHTYELLOW_EX = ''
            GREEN = ''
            RED = ''
            YELLOW = ''
            CYAN = ''
            WHITE = ''
        class Style:
            RESET_ALL = ''
        COLORS_AVAILABLE = False
    
    auditor = WiFiAudit(args.interface)
    auditor.pen_speed = args.speed
    
    if args.live:
        # Live monitoring mode
        print(f"{Fore.LIGHTCYAN_EX}Live monitoring mode - Press Ctrl+C to stop{Style.RESET_ALL}")
        try:
            while True:
                auditor.results['access_points'] = []
                auditor.run()
                time.sleep(2)
                os.system('cls' if platform.system() == 'Windows' else 'clear')
        except KeyboardInterrupt:
            print(f"\n{Fore.LIGHTYELLOW_EX}Live monitoring stopped{Style.RESET_ALL}")
    else:
        auditor.run()


if __name__ == "__main__":
    main()