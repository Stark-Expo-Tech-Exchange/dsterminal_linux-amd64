#!/usr/bin/env python3
"""
DSTerminal Network Security Audit Module
Comprehensive network security assessment with WiFi + Ethernet support
Glowing neon hacker colors, PDF/HTML reports, live monitoring
"""
import sys
if sys.platform == 'win32':
    import os
    import msvcrt
    # Ensure stdout is properly set
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', errors='ignore')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', errors='ignore')
        
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

# Check for psutil for network stats
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class NetworkAudit:
    """Comprehensive Network Security Audit Engine - WiFi + Ethernet"""
    
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
    APP_NAME = "DSTerminal Network Security Audit"
    
    def __init__(self, interface: Optional[str] = None, scan_all: bool = True):
        self.interface = interface
        self.scan_all = scan_all
        self.system = platform.system().lower()
        self.hostname = socket.gethostname()
        self.report_id = self._generate_report_id()
        self.timestamp = datetime.now()
        
        # Extended results structure - WiFi + Ethernet
        self.results = {
            'report_id': self.report_id,
            'version': self.VERSION,
            'timestamp': self.timestamp.isoformat(),
            'system': self.system,
            'hostname': self.hostname,
            'interface': interface,
            'network_type': None,
            'interfaces': [],
            'wifi_networks': [],
            'ethernet_networks': [],
            'security_findings': [],
            'recommendations': [],
            'summary': {
                'total_interfaces': 0,
                'wifi_interfaces': 0,
                'ethernet_interfaces': 0,
                'connected_wifi': 0,
                'connected_ethernet': 0,
                'open_wifi_networks': 0,
                'secured_wifi_networks': 0,
                'rogue_aps': 0,
                'total_aps': 0,
                'secured_aps': 0,
                'open_aps': 0,
                'wep_aps': 0,
                'wpa_aps': 0,
                'wpa2_aps': 0,
                'wpa3_aps': 0,
                'highest_signal': 0,
                'high_risk': 0
            }
        }
        self._last_export_key = None
        self._last_export_path = None
        
        # Pen typing settings
        self.pen_speed = 0.035
        self.pen_variance = 0.008
        self.auto_break_chars = 80
        self.current_line_length = 0
        
        # Get terminal width
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
        return f"NET-{timestamp}-{random_suffix}"
    
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
        
        if indent > 0:
            sys.stdout.write(" " * indent)
            sys.stdout.flush()
            self.current_line_length += indent
        
        if color:
            if glow:
                sys.stdout.write(self.BOLD)
            if blink:
                sys.stdout.write(self.BLINK_ON)
            sys.stdout.write(color)
            sys.stdout.flush()
        
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
    # GLOWING NEON BOX DRAWING - FIXED UTF-8
    # ========================================================================
    
    def _draw_glow_box(self, title: str, content_lines: List[str], 
                       title_color: str, border_color: str,
                       content_color: Optional[str] = None,
                       width: Optional[int] = None,
                       blink_title: bool = False,
                       glow_border: bool = True):
        """Draw a glowing neon hacker-styled centered box."""
        import textwrap
        
        content_color = content_color or Fore.LIGHTGREEN_EX
        term = shutil.get_terminal_size((100, 30))
        
        if width is None:
            width = min(term.columns - 6, 110)
        width = max(width, 60)
        left_margin = max(0, (term.columns - width) // 2)
        inner = width - 4
        
        wrapped = []
        for line in content_lines:
            if not line.strip():
                wrapped.append("")
                continue
            line = line.rstrip()
            wrapped.extend(textwrap.wrap(line, inner, break_long_words=False, replace_whitespace=False))
        
        glow_prefix = self.BOLD if glow_border else ""
        
        # Use simple ASCII box characters
        top = glow_prefix + border_color + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL
        mid = glow_prefix + border_color + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL
        bot = glow_prefix + border_color + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL
        
        title_text = f" {title} ".center(width - 2)
        title_prefix = self.BOLD
        if blink_title:
            title_prefix += self.BLINK_ON
        title_line = title_prefix + title_color + "|" + title_text + "|" + Style.RESET_ALL
        if blink_title:
            title_line += self.BLINK_OFF
        
        print()
        print(" " * left_margin + top)
        print(" " * left_margin + title_line)
        print(" " * left_margin + mid)
        
        for line in wrapped:
            border_prefix = glow_prefix if glow_border else ""
            print(" " * left_margin + border_prefix + border_color + "| " + Style.RESET_ALL, end="")
            padded_line = line.ljust(inner)
            self.pen_type(padded_line, color=content_color, speed=self.pen_speed, newline=False, glow=True)
            print(" " * left_margin + border_prefix + border_color + "|" + Style.RESET_ALL)
            time.sleep(self.pen_speed * 0.5)
        
        print(" " * left_margin + bot)
        print()
        time.sleep(self.pen_speed * 1.5)
    
    # ========================================================================
    # BANNER - NETWORK + WIFI FOCUSED - FIXED UTF-8
    # ========================================================================
    
    def show_banner(self):
        """Display the Network + WiFi audit banner."""
        import shutil
        
        term = shutil.get_terminal_size((100, 30))
        width = min(term.columns - 6, 110)
        width = max(width, 60)
        left_margin = max(0, (term.columns - width) // 2)
        
        print()
        print(" " * left_margin + Fore.CYAN + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL)
        print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + " " * (width - 2) + Fore.CYAN + "|" + Style.RESET_ALL)
        
        # ASCII Art - Network + WiFi (simplified)
        ascii_art = [
            "    [++]   [==] [=======] [========] [==]    [==] [=======] [========] [==]  [==]",
            "    [++]  [==] [=======] [========] [==]    [==] [=======] [========] [==] [==] ",
            "    [==] [==] [=======]     [==]   [==] [=] [==] [==]   [==] [========] [=======] ",
            "    [==] [==] [=======]     [==]   [==] [=] [==] [==]   [==] [========] [=======] ",
            "    [==] [==] [=======]   [==]   [=] [=] [=] [=] [=]   [=] [========] [==]  [==]",
            "    [==]  [==] [=======] [========] [==]    [==] [==]   [==] [========] [==]  [==]"
        ]
        
        max_len = max(len(line) for line in ascii_art)
        for line in ascii_art:
            padding = (width - max_len - 10) // 2
            print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + 
                  " " * padding + Fore.LIGHTGREEN_EX + line + Style.RESET_ALL + 
                  " " * (width - max_len - padding - 10) + Fore.CYAN + "|" + Style.RESET_ALL)
        
        # Title - Network + WiFi Security Audit
        title = f"[!] Network & WiFi Security Audit Engine v{self.VERSION}"
        print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + 
              " " * ((width - 2 - len(title)) // 2) + 
              Fore.LIGHTCYAN_EX + title + Style.RESET_ALL + 
              " " * ((width - 2 - len(title)) // 2) + Fore.CYAN + "|" + Style.RESET_ALL)
        
        # Subtitle - WiFi + Ethernet
        subtitle = "[+] WiFi + Ethernet Network Security Assessment & Analysis"
        print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + 
              " " * ((width - 2 - len(subtitle)) // 2) + 
              Fore.LIGHTMAGENTA_EX + subtitle + Style.RESET_ALL + 
              " " * ((width - 2 - len(subtitle)) // 2) + Fore.CYAN + "|" + Style.RESET_ALL)
        
        # Bottom border
        print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + " " * (width - 2) + Fore.CYAN + "|" + Style.RESET_ALL)
        print(" " * left_margin + Fore.CYAN + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL)
        print()
        time.sleep(0.5)
    
    # ========================================================================
    # NETWORK INTERFACE DETECTION (WiFi + Ethernet)
    # ========================================================================
    
    def _detect_all_interfaces(self) -> List[Dict]:
        """Detect all network interfaces (WiFi + Ethernet)."""
        interfaces = []
        
        try:
            if PSUTIL_AVAILABLE:
                for iface, addrs in psutil.net_if_addrs().items():
                    ip = None
                    mac = None
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            ip = addr.address
                        elif addr.family == psutil.AF_LINK:
                            mac = addr.address
                    if ip and ip not in ['127.0.0.1', '0.0.0.0']:
                        interfaces.append({
                            'name': iface,
                            'ip': ip,
                            'mac': mac or 'Unknown',
                            'type': self._detect_interface_type(iface)
                        })
        except:
            pass
        
        # Fallback: use OS commands
        if not interfaces:
            if self.system == 'windows':
                interfaces = self._detect_windows_interfaces()
            elif self.system == 'linux':
                interfaces = self._detect_linux_interfaces()
            elif self.system == 'darwin':
                interfaces = self._detect_macos_interfaces()
        
        return interfaces
    
    def _detect_windows_interfaces(self) -> List[Dict]:
        """Detect interfaces on Windows."""
        interfaces = []
        try:
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=10)
            current_iface = None
            current_mac = None
            current_ip = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if 'adapter' in line.lower():
                    if current_iface and current_ip:
                        interfaces.append({
                            'name': current_iface,
                            'ip': current_ip,
                            'mac': current_mac or 'Unknown',
                            'type': self._detect_interface_type(current_iface)
                        })
                    name_match = re.search(r'adapter\s+(.+?):', line)
                    current_iface = name_match.group(1).strip() if name_match else None
                    current_mac = None
                    current_ip = None
                elif 'physical address' in line.lower():
                    mac_match = re.search(r'([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}', line)
                    current_mac = mac_match.group(0).replace('-', ':') if mac_match else None
                elif 'ipv4' in line.lower() or 'ip address' in line.lower():
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match and ip_match.group(1) not in ['127.0.0.1', '0.0.0.0']:
                        current_ip = ip_match.group(1)
            
            if current_iface and current_ip:
                interfaces.append({
                    'name': current_iface,
                    'ip': current_ip,
                    'mac': current_mac or 'Unknown',
                    'type': self._detect_interface_type(current_iface)
                })
        except:
            pass
        return interfaces
    
    def _detect_linux_interfaces(self) -> List[Dict]:
        """Detect interfaces on Linux."""
        interfaces = []
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True, timeout=10)
            current_iface = None
            current_mac = None
            current_ip = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith(('eth', 'wlan', 'enp', 'wlp')):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        current_iface = parts[1].strip()
                        mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]+)', line)
                        if mac_match:
                            current_mac = mac_match.group(1).upper()
                elif 'inet ' in line and current_iface:
                    ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match and ip_match.group(1) not in ['127.0.0.1', '0.0.0.0']:
                        current_ip = ip_match.group(1)
                        interfaces.append({
                            'name': current_iface,
                            'ip': current_ip,
                            'mac': current_mac or 'Unknown',
                            'type': self._detect_interface_type(current_iface)
                        })
                        current_ip = None
        except:
            pass
        return interfaces
    
    def _detect_macos_interfaces(self) -> List[Dict]:
        """Detect interfaces on macOS."""
        interfaces = []
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=10)
            current_iface = None
            current_mac = None
            current_ip = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith(' '):
                    iface_match = re.match(r'^([a-z0-9]+):', line)
                    if iface_match:
                        if current_iface and current_ip:
                            interfaces.append({
                                'name': current_iface,
                                'ip': current_ip,
                                'mac': current_mac or 'Unknown',
                                'type': self._detect_interface_type(current_iface)
                            })
                        current_iface = iface_match.group(1)
                        current_mac = None
                        current_ip = None
                elif 'ether' in line and current_iface:
                    mac_match = re.search(r'ether\s+([0-9a-fA-F:]+)', line)
                    if mac_match:
                        current_mac = mac_match.group(1).upper()
                elif 'inet ' in line and current_iface:
                    ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match and ip_match.group(1) not in ['127.0.0.1', '0.0.0.0']:
                        current_ip = ip_match.group(1)
            
            if current_iface and current_ip:
                interfaces.append({
                    'name': current_iface,
                    'ip': current_ip,
                    'mac': current_mac or 'Unknown',
                    'type': self._detect_interface_type(current_iface)
                })
        except:
            pass
        return interfaces
    
    def _detect_interface_type(self, iface_name: str) -> str:
        """Detect if interface is WiFi, Ethernet, or other."""
        iface_lower = iface_name.lower()
        
        wifi_patterns = ['wifi', 'wireless', 'wlan', 'wlp', 'wlx', 'wi-fi', '802.11']
        for pattern in wifi_patterns:
            if pattern in iface_lower:
                return 'WiFi'
        
        ethernet_patterns = ['eth', 'enp', 'enx', 'en', 'ethernet', 'lan', 'gigabit']
        for pattern in ethernet_patterns:
            if pattern in iface_lower:
                return 'Ethernet'
        
        if 'bluetooth' in iface_lower:
            return 'Bluetooth'
        elif 'vmnet' in iface_lower or 'virtual' in iface_lower:
            return 'Virtual'
        
        return 'Unknown'
    
    def _get_connected_network(self) -> Dict:
        """Get currently connected network info."""
        connected = {'type': 'None'}
        
        # Check WiFi connection
        if self.system == 'windows':
            try:
                result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line.startswith("SSID") and "BSSID" not in line and ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) >= 2:
                            ssid = parts[1].strip()
                            if ssid and ssid != "SSID":
                                connected['type'] = 'WiFi'
                                connected['ssid'] = ssid
                    elif "Signal" in line and "%" in line:
                        m = re.search(r"(\d+)%", line)
                        if m:
                            connected['signal'] = int(m.group(1))
                    elif "Authentication" in line and ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) >= 2:
                            connected['authentication'] = parts[1].strip()
                    elif "State" in line and ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) >= 2 and 'connected' in parts[1].lower():
                            connected['state'] = 'connected'
            except:
                pass
        
        # Check Ethernet connection
        try:
            interfaces = self._detect_all_interfaces()
            eth_interfaces = [i for i in interfaces if i.get('type') == 'Ethernet']
            for eth in eth_interfaces:
                if eth.get('ip'):
                    connected['type'] = 'Ethernet'
                    connected['ip'] = eth.get('ip')
                    connected['mac'] = eth.get('mac')
                    break
        except:
            pass
        
        return connected
    
    def _detect_windows_interface(self) -> Optional[str]:
        """Detect Windows WiFi interface."""
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
    
    def normalize_bssid(self, bssid: str) -> str:
        """Normalize BSSID format."""
        if not bssid:
            return ""
        return bssid.upper().replace("-", ":").strip()
    
    # ========================================================================
    # TYPING HELPERS
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
            "CRITICAL": "[!]",
            "HIGH": "[-]",
            "MEDIUM": "[*]",
            "LOW": "[.]",
            "INFO": "[+]"
        }
        color = severity_colors.get(severity, Fore.LIGHTWHITE_EX)
        prefix = severity_prefix.get(severity, "")
        self.pen_type(f"{prefix} {text}", color=color, glow=True)
    
    # ========================================================================
    # WINDOWS WIFI AUDIT
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
                "[-] Warning",
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
            "[+] Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.5)
        
        connected_network = self._get_connected_network()
        connected_bssid = self.normalize_bssid(connected_network.get('bssid', ''))
        connected_signal = connected_network.get('signal', 0)
        connected_ssid = connected_network.get('ssid', '')
        
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], 
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                result = subprocess.run(
                    ['netsh', 'wlan', 'show', 'networks'], 
                    capture_output=True, text=True, timeout=30
                )
            
            if result.stdout.strip():
                self._parse_windows_output(result.stdout, connected_network)
            else:
                self._draw_glow_box(
                    "[-] No Networks Found",
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
                "[!] Timeout",
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
                "[!] Error",
                [f"Error during scan: {str(e)}"],
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
        
        if not self.results['wifi_networks'] and connected_ssid:
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
            self.results['wifi_networks'].append(ap)
    
    def _parse_windows_output(self, output: str, connected_network: Dict):
        """Parse Windows netsh output."""
        connected_bssid = self.normalize_bssid(connected_network.get('bssid', ''))
        connected_signal = connected_network.get('signal', 0)
        connected_ssid = connected_network.get('ssid', '')
        
        self.results['wifi_networks'] = []
        
        current_ssid = None
        current_auth = None
        current_encryption = None
        current_bssid = None
        current_signal = None
        current_channel = None
        
        for line in output.split('\n'):
            line = line.rstrip()
            if not line:
                continue
            
            ssid_match = re.match(r'^\s*SSID\s+\d+\s+:\s+(.+)$', line, re.IGNORECASE)
            if ssid_match:
                if current_bssid and current_ssid:
                    self.results['wifi_networks'].append({
                        'ssid': current_ssid,
                        'bssid': current_bssid,
                        'signal': current_signal or 0,
                        'security': self._detect_security(current_auth),
                        'authentication': current_auth or 'Unknown',
                        'channel': current_channel
                    })
                current_ssid = ssid_match.group(1).strip()
                current_auth = None
                current_bssid = None
                current_signal = None
                current_channel = None
                continue
            
            if current_ssid:
                auth_match = re.match(r'^\s*Authentication\s+:\s+(.+)$', line, re.IGNORECASE)
                if auth_match:
                    current_auth = auth_match.group(1).strip()
                    continue
                
                bssid_match = re.match(r'^\s*BSSID\s+\d+\s+:\s+([0-9A-Fa-f:]+)$', line, re.IGNORECASE)
                if bssid_match:
                    if current_bssid:
                        self.results['wifi_networks'].append({
                            'ssid': current_ssid,
                            'bssid': current_bssid,
                            'signal': current_signal or 0,
                            'security': self._detect_security(current_auth),
                            'authentication': current_auth or 'Unknown',
                            'channel': current_channel
                        })
                    current_bssid = self.normalize_bssid(bssid_match.group(1))
                    current_signal = None
                    current_channel = None
                    continue
                
                if current_bssid:
                    signal_match = re.match(r'^\s*Signal\s+:\s+(\d+)%$', line, re.IGNORECASE)
                    if signal_match:
                        current_signal = int(signal_match.group(1))
                        continue
                    
                    channel_match = re.match(r'^\s*Channel\s+:\s+(\d+)$', line, re.IGNORECASE)
                    if channel_match:
                        current_channel = int(channel_match.group(1))
                        continue
        
        if current_ssid and current_bssid:
            self.results['wifi_networks'].append({
                'ssid': current_ssid,
                'bssid': current_bssid,
                'signal': current_signal or 0,
                'security': self._detect_security(current_auth),
                'authentication': current_auth or 'Unknown',
                'channel': current_channel
            })
        
        # Deduplicate
        unique_aps = {}
        for ap in self.results['wifi_networks']:
            bssid = ap.get('bssid', '')
            if bssid and bssid != 'Unknown':
                if bssid in unique_aps:
                    existing = unique_aps[bssid]
                    if ap.get('signal', 0) > existing.get('signal', 0):
                        unique_aps[bssid] = ap
                else:
                    unique_aps[bssid] = ap
        
        self.results['wifi_networks'] = list(unique_aps.values())
        
        # Sort by signal strength
        self.results['wifi_networks'].sort(key=lambda x: x.get('signal', 0), reverse=True)
    
    def _detect_security(self, auth: str) -> str:
        """Detect security type from authentication string."""
        if not auth:
            return 'Unknown'
        if 'WPA3' in auth:
            return 'WPA3'
        if 'WPA2' in auth:
            return 'WPA2'
        if 'WPA' in auth:
            return 'WPA'
        if 'WEP' in auth:
            return 'WEP'
        if 'Open' in auth or 'None' in auth:
            return 'Open'
        return 'Unknown'
    
    def _wifi_audit_linux(self):
        """Linux WiFi audit implementation."""
        self._draw_glow_box(
            "[+] Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.5)
        pass
    
    def _wifi_audit_macos(self):
        """macOS WiFi audit implementation."""
        self._draw_glow_box(
            "[+] Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.5)
        pass
    
    # ========================================================================
    # ANALYSIS
    # ========================================================================
    
    def _analyze_findings(self):
        """Analyze network findings (WiFi + Ethernet)."""
        summary = self.results['summary']
        
        wifi_networks = self.results.get('wifi_networks', [])
        summary['total_aps'] = len(wifi_networks)
        
        for ap in wifi_networks:
            sec = ap.get('security', 'Unknown')
            sec_type = self._detect_security(sec)
            ap['security_type'] = sec_type
            
            if sec_type == 'Open':
                summary['open_aps'] += 1
                summary['open_wifi_networks'] += 1
                self.results['security_findings'].append({
                    'type': 'Open WiFi',
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'Open network - No encryption',
                    'severity': 'CRITICAL'
                })
            elif sec_type == 'WEP':
                summary['wep_aps'] += 1
                self.results['security_findings'].append({
                    'type': 'WEP WiFi',
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WEP encryption - Vulnerable to attacks',
                    'severity': 'HIGH'
                })
            elif sec_type == 'WPA':
                summary['wpa_aps'] += 1
                self.results['security_findings'].append({
                    'type': 'WPA WiFi',
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WPA encryption - Deprecated, vulnerable to KRACK',
                    'severity': 'MEDIUM'
                })
            elif sec_type == 'WPA2':
                summary['wpa2_aps'] += 1
                summary['secured_aps'] += 1
            elif sec_type == 'WPA3':
                summary['wpa3_aps'] += 1
                summary['secured_aps'] += 1
            else:
                summary['secured_aps'] += 1
            
            signal = ap.get('signal', 0)
            if signal > summary['highest_signal']:
                summary['highest_signal'] = signal
        
        summary['secured_wifi_networks'] = summary['secured_aps']
        
        interfaces = self.results.get('interfaces', [])
        eth_interfaces = [i for i in interfaces if i.get('type') == 'Ethernet']
        summary['ethernet_interfaces'] = len(eth_interfaces)
        
        for eth in eth_interfaces:
            self.results['ethernet_networks'].append({
                'name': eth.get('name', 'Unknown'),
                'ip': eth.get('ip', 'N/A'),
                'mac': eth.get('mac', 'Unknown'),
                'status': 'Connected' if eth.get('ip') and eth.get('ip') != 'N/A' else 'Disconnected'
            })
        
        summary['total_interfaces'] = len(interfaces)
        summary['wifi_interfaces'] = len([i for i in interfaces if i.get('type') == 'WiFi'])
        
        connected = self._get_connected_network()
        if connected.get('type') == 'WiFi':
            summary['connected_wifi'] = 1
        elif connected.get('type') == 'Ethernet':
            summary['connected_ethernet'] = 1
        
        # Generate comprehensive recommendations
        recommendations = []
        
        if summary.get('open_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': '[!] Open WiFi networks detected - Disable open networks or implement WPA3',
                'explanation': 'Open WiFi networks have NO encryption. All traffic is transmitted in plaintext, making it easy for attackers to sniff passwords, emails, and sensitive data.',
                'action': 'Disable open networks immediately and implement WPA3-Enterprise encryption. If WPA3 is not available, use WPA2-AES with a strong passphrase.',
                'timeline': 'Immediate (CRITICAL)',
                'severity': 'CRITICAL'
            })
        
        if summary.get('wep_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': '[!] WEP encryption detected - Upgrade to WPA3 immediately',
                'explanation': 'WEP is a 20+ year old encryption standard that has been COMPROMISED. Attackers can crack WEP keys in minutes using tools like Aircrack-ng.',
                'action': 'Upgrade all WEP networks to WPA3 or at minimum WPA2-AES immediately.',
                'timeline': 'Immediate (CRITICAL)',
                'severity': 'CRITICAL'
            })
        
        if summary.get('wpa_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': '[-] WPA encryption detected - Upgrade to WPA2/WPA3',
                'explanation': 'WPA is vulnerable to KRACK attacks and has known security weaknesses.',
                'action': 'Upgrade to WPA2 or WPA3. Use AES encryption instead of TKIP.',
                'timeline': 'Within 30 days (HIGH)',
                'severity': 'HIGH'
            })
        
        if summary.get('wpa2_aps', 0) > 0 and summary.get('wpa3_aps', 0) == 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': '[.] WPA2 detected - Consider upgrading to WPA3',
                'explanation': 'While WPA2 is still considered secure, WPA3 offers enhanced protection against dictionary attacks.',
                'action': 'Upgrade to WPA3 on compatible devices. Ensure WPA2-AES with strong passwords.',
                'timeline': 'Within 90 days (MEDIUM)',
                'severity': 'MEDIUM'
            })
        
        if summary.get('ethernet_interfaces', 0) > 0:
            recommendations.append({
                'type': 'Ethernet Security',
                'title': '[.] Ethernet networks detected - Ensure physical security',
                'explanation': 'Ethernet ports are PHYSICAL access points. Anyone with cable access can connect unauthorized devices.',
                'action': 'Implement 802.1X authentication, enable port security, disable unused ports.',
                'timeline': 'Within 30 days (HIGH)',
                'severity': 'HIGH'
            })
        
        if summary.get('rogue_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': '[!] Rogue Access Points detected - Investigate and remove unauthorized APs',
                'explanation': 'Rogue APs are UNAUTHORIZED access points that bypass security controls.',
                'action': 'Identify rogue APs using WiFi scanning tools, physically locate them, and remove them immediately.',
                'timeline': 'Immediate (CRITICAL)',
                'severity': 'CRITICAL'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'General',
                'title': '[+] No critical security issues found - Continue monitoring',
                'explanation': 'Your network appears to be properly secured. Continue regular security audits.',
                'action': 'Continue monitoring, conduct regular security audits.',
                'timeline': 'Ongoing (LOW)',
                'severity': 'LOW'
            })
        
        self.results['recommendations'] = recommendations
    
    # ========================================================================
    # DISPLAY RESULTS - FIXED UTF-8
    # ========================================================================
    
    def _display_results(self):
        """Display audit results with glowing neon effects."""
        summary = self.results.get('summary', {})
    
        # Network Interfaces Summary
        interface_lines = [
            f"Total Interfaces: {summary.get('total_interfaces', 0)}",
            f"WiFi Interfaces: {summary.get('wifi_interfaces', 0)}",
            f"Ethernet Interfaces: {summary.get('ethernet_interfaces', 0)}",
            f"Connected WiFi: {'Yes' if summary.get('connected_wifi', 0) > 0 else 'No'}",
            f"Connected Ethernet: {'Yes' if summary.get('connected_ethernet', 0) > 0 else 'No'}"
        ]
    
        self._draw_glow_box(
            "Network Interfaces",
            interface_lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
    
        # WiFi Summary
        wifi_lines = [
            f"Total Access Points: {summary.get('total_aps', 0)}",
            f"Secured Networks: {summary.get('secured_aps', 0)}",
            f"Open Networks: {summary.get('open_aps', 0)}",
            f"WEP Networks: {summary.get('wep_aps', 0)}",
            f"WPA Networks: {summary.get('wpa_aps', 0)}",
            f"WPA2 Networks: {summary.get('wpa2_aps', 0)}",
            f"WPA3 Networks: {summary.get('wpa3_aps', 0)}",
            f"Highest Signal: {summary.get('highest_signal', 0)}%"
        ]
    
        self._draw_glow_box(
            "WiFi Networks",
            wifi_lines,
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTMAGENTA_EX,
            content_color=Fore.LIGHTGREEN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
    
        # Ethernet Networks
        eth_networks = self.results.get('ethernet_networks', [])
        if eth_networks:
            eth_lines = []
            for eth in eth_networks[:10]:
                eth_lines.append(f"{eth.get('name', 'Unknown')} - {eth.get('ip', 'N/A')} ({eth.get('status', 'Unknown')})")
        
            self._draw_glow_box(
                "Ethernet Networks",
                eth_lines if eth_lines else ["No Ethernet networks detected"],
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTWHITE_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
    
        # Security Score
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
            bar = "#" * filled + "." * (bar_length - filled)
        
            score_lines = [
                f"Score: {security_score}/100",
                f"Status: {status_text}",
                f"[{bar}]"
            ]
        
            self._draw_glow_box(
                "Security Score",
                score_lines,
                title_color=Fore.LIGHTYELLOW_EX,
                border_color=Fore.LIGHTYELLOW_EX,
                content_color=score_color,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
    
        # Security Findings
        findings = self.results.get('security_findings', [])
        if findings:
            finding_lines = []
            for finding in findings[:10]:
                severity = finding.get('severity', 'INFO')
                emoji = {"CRITICAL": "[!]", "HIGH": "[-]", "MEDIUM": "[*]", "LOW": "[.]"}.get(severity, "[+]")
                finding_text = f"{emoji} [{severity}] {finding.get('finding', '')} ({finding.get('ap', 'Unknown')})"
                wrapped_finding = self._wrap_text(finding_text, 75)
                finding_lines.extend(wrapped_finding)
        
            if len(findings) > 10:
                finding_lines.append(f"... and {len(findings) - 10} more findings")
        
            self._draw_glow_box(
                "Security Findings",
                finding_lines,
                title_color=Fore.LIGHTRED_EX,
                border_color=Fore.LIGHTRED_EX,
                content_color=Fore.LIGHTRED_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
    
        # Recommendations with Full Explanations
        recommendations = self.results.get('recommendations', [])
        if recommendations:
            rec_lines = []
            for rec in recommendations[:5]:
                title = rec.get('title', '')
                explanation = rec.get('explanation', '')
                action = rec.get('action', '')
                timeline = rec.get('timeline', '')
            
                rec_lines.append(f"{title}")
                rec_lines.append("  +-- Explanation:")
                explanation_lines = self._wrap_text(explanation, 72)
                for line in explanation_lines:
                    rec_lines.append(f"     {line}")
                rec_lines.append("     -> Action:")
                action_lines = self._wrap_text(action, 72)
                for line in action_lines:
                    rec_lines.append(f"       {line}")
                rec_lines.append(f"     -> Timeline: {timeline}")
                rec_lines.append("")
        
            if len(recommendations) > 5:
                rec_lines.append(f"... and {len(recommendations) - 5} more recommendations")
        
            self._draw_glow_box(
                "Recommendations",
                rec_lines,
                title_color=Fore.LIGHTBLUE_EX,
                border_color=Fore.LIGHTBLUE_EX,
                content_color=Fore.LIGHTYELLOW_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
    
        # Access Points
        wifi_networks = self.results.get('wifi_networks', [])
        if wifi_networks:
            ap_lines = []
            for ap in wifi_networks[:15]:
                ssid = ap.get('ssid', '<Hidden>')[:20]
                bssid = ap.get('bssid', 'Unknown')[:17]
                signal = ap.get('signal', 0)
                security = ap.get('security_type', ap.get('security', 'Unknown'))[:10]
                signal_indicator = "[+]" if signal > 70 else "[*]" if signal > 40 else "[-]"
                security_color = Fore.LIGHTGREEN_EX if security in ['WPA2', 'WPA3'] else Fore.LIGHTYELLOW_EX if security == 'WPA' else Fore.LIGHTRED_EX
            
                ap_lines.append(f"{signal_indicator} {ssid:<20} {security_color}{security:<8}{Style.RESET_ALL} {signal:>3}% {bssid}")
        
            if len(wifi_networks) > 15:
                ap_lines.append(f"... and {len(wifi_networks) - 15} more")
        
            self._draw_glow_box(
                f"Access Points ({len(wifi_networks)})",
                ap_lines,
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTWHITE_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)

    def _wrap_text(self, text: str, max_width: int = 75) -> List[str]:
        """Wrap text to fit within a specified width."""
        import textwrap
    
        if not text:
            return [""]
    
        paragraphs = text.split('\n')
        wrapped_lines = []
    
        for para in paragraphs:
            if not para.strip():
                wrapped_lines.append("")
                continue
        
            lines = textwrap.wrap(para, width=max_width, break_long_words=False, replace_whitespace=True)
            wrapped_lines.extend(lines)
    
        return wrapped_lines

    # ========================================================================
    # EXPORT - FIXED UTF-8
    # ========================================================================
    
    def _export_results(self) -> Optional[str]:
        """Export results to multiple formats with proper formatting."""
        try:
            export_dir = Path.home() / "DSTerminal" / "reports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            base_filename = export_dir / f"network_audit_{self.report_id}"
            
            # JSON Export
            json_filename = base_filename.with_suffix('.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
            
            # PDF Export
            pdf_filename = base_filename.with_suffix('.pdf')
            if PDF_AVAILABLE:
                self._generate_pdf_report(str(pdf_filename))
            
            # HTML Export
            html_filename = base_filename.with_suffix('.html')
            self._generate_html_report(str(html_filename))
            
            def format_path(path_str: str, max_width: int = 80) -> List[str]:
                if len(path_str) <= max_width:
                    return [path_str]
                
                parts = path_str.split('\\')
                lines = []
                current_line = parts[0] if parts else ""
                
                for part in parts[1:]:
                    if len(current_line) + len(part) + 1 <= max_width:
                        current_line += "\\" + part
                    else:
                        lines.append(current_line)
                        current_line = part
                
                if current_line:
                    lines.append(current_line)
                
                return lines
            
            export_messages = []
            
            json_path = str(json_filename)
            json_lines = format_path(json_path)
            export_messages.append("[+] JSON Report:")
            export_messages.extend([f"   {line}" for line in json_lines])
            
            if PDF_AVAILABLE:
                pdf_path = str(pdf_filename)
                pdf_lines = format_path(pdf_path)
                export_messages.append("[+] PDF Report:")
                export_messages.extend([f"   {line}" for line in pdf_lines])
            else:
                export_messages.append("[-] PDF export skipped")
            
            html_path = str(html_filename)
            html_lines = format_path(html_path)
            export_messages.append("[+] HTML Report:")
            export_messages.extend([f"   {line}" for line in html_lines])
            
            try:
                import webbrowser
                webbrowser.open(f"file://{html_filename}")
                export_messages.append("[+] HTML report opened in browser")
            except:
                pass
            
            self._draw_glow_box(
                "Export Results",
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
            print(f"{Fore.LIGHTYELLOW_EX}[-] Failed to export results: {str(e)}{Style.RESET_ALL}")
            return None

    def _generate_pdf_report(self, filename: str) -> bool:
        """Generate PDF report with both WiFi and Ethernet findings."""
        if not PDF_AVAILABLE:
            print(f"{Fore.LIGHTYELLOW_EX}[-] PDF generation requires reportlab. Install: pip install reportlab{Style.RESET_ALL}")
            return False

        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            class WatermarkedDocTemplate(SimpleDocTemplate):
                def __init__(self, filename, **kwargs):
                    super().__init__(filename, **kwargs)
                    self.report_id = self._generate_report_id()
        
                def _generate_report_id(self):
                    ts = datetime.now().strftime("%Y%m%d%H%M%S")
                    return f"NET-PDF-{ts}"

            def add_watermark(canvas_obj, doc_obj):
                canvas_obj.saveState()
                canvas_obj.setFont('Helvetica-Bold', 60)
                canvas_obj.setFillColor(colors.HexColor('#1a1a2e'))
                canvas_obj.setFillAlpha(0.08)
                canvas_obj.saveState()
                page_width, page_height = A4
                canvas_obj.translate(page_width / 2, page_height / 2)
                canvas_obj.rotate(45)
                canvas_obj.drawCentredString(0, 0, "DSTERMINAL")
                canvas_obj.restoreState()
                canvas_obj.setFont('Helvetica', 25)
                canvas_obj.setFillAlpha(0.06)
                canvas_obj.drawCentredString(page_width / 2, 50, f"v{self.VERSION}")
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

            # ============================================================
            # CUSTOM STYLES - BRIGHT AND VISIBLE
            # ============================================================
        
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
                fontSize=14,
                textColor=colors.HexColor('#cccccc'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica'
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#00ffff'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )

            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#ffffff'),
                alignment=TA_LEFT,
                spaceAfter=6,
                fontName='Helvetica'
            )

            rec_title_style = ParagraphStyle(
                'RecTitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#ffcc00'),
                alignment=TA_LEFT,
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )

            rec_label_style = ParagraphStyle(
                'RecLabel',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#00ffff'),
                alignment=TA_LEFT,
                spaceAfter=2,
                fontName='Helvetica-Bold'
            )

            rec_text_style = ParagraphStyle(
                'RecText',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#ffffff'),
                alignment=TA_LEFT,
                spaceAfter=8,
                fontName='Helvetica',
                leftIndent=20
            )

            critical_style = ParagraphStyle(
                'Critical',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#ff0000'),
                alignment=TA_LEFT,
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )

            high_style = ParagraphStyle(
                'High',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#ff6600'),
                alignment=TA_LEFT,
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )

            medium_style = ParagraphStyle(
                'Medium',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#ffcc00'),
                alignment=TA_LEFT,
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )

            low_style = ParagraphStyle(
                'Low',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#00ff00'),
                alignment=TA_LEFT,
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )

            story.append(Paragraph("DSTERMINAL Cyber-Ops Platform", title_style))
            story.append(Paragraph("Network & WiFi Security Audit Report", subtitle_style))
            story.append(Spacer(1, 15))

            summary = self.results.get('summary', {})
            metadata_data = [
                ["Report ID:", self.results.get('report_id', 'N/A')],
                ["Generated By:", f"DSTERMINAL Cyber-Ops Platform v{self.VERSION}"],
                ["Scan Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ["System:", self.system.upper()],
                ["Hostname:", self.hostname],
                ["Interface:", self.interface or "Auto-detected"],
                ["Total APs:", str(summary.get('total_aps', 0))],
                ["WiFi Interfaces:", str(summary.get('wifi_interfaces', 0))],
                ["Ethernet Interfaces:", str(summary.get('ethernet_interfaces', 0))],
            ]

            metadata_table = Table(metadata_data, colWidths=[140, 330])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#00ffff')),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#0d1117')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#33ff33')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ]))
            story.append(metadata_table)
            story.append(Spacer(1, 20))

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
                ['Connected WiFi', 'Yes' if summary.get('connected_wifi', 0) > 0 else 'No'],
                ['Connected Ethernet', 'Yes' if summary.get('connected_ethernet', 0) > 0 else 'No'],
                ['Rogue APs', str(summary.get('rogue_aps', 0))],
            ]

            summary_table = Table(summary_data, colWidths=[200, 100])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ff00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#333333')),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            eth_networks = self.results.get('ethernet_networks', [])
            if eth_networks:
                story.append(Paragraph("Ethernet Networks", heading_style))
                eth_data = [['Interface', 'IP Address', 'MAC Address', 'Status']]
                for eth in eth_networks[:20]:
                    eth_data.append([
                        eth.get('name', 'Unknown'),
                        eth.get('ip', 'N/A'),
                        eth.get('mac', 'Unknown'),
                        eth.get('status', 'Unknown')
                    ])
            
                eth_table = Table(eth_data, colWidths=[100, 120, 130, 80])
                eth_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ffff')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0d1117')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#333333')),
                ]))
                story.append(eth_table)
                story.append(Spacer(1, 20))

            recommendations = self.results.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("Recommendations", heading_style))
                story.append(Spacer(1, 6))
            
                for rec in recommendations:
                    title = rec.get('title', '')
                    explanation = rec.get('explanation', '')
                    action = rec.get('action', '')
                    timeline = rec.get('timeline', '')
                    severity = rec.get('severity', 'MEDIUM')
                
                    if severity == 'CRITICAL':
                        sev_style = critical_style
                        sev_label = "[!] CRITICAL"
                    elif severity == 'HIGH':
                        sev_style = high_style
                        sev_label = "[-] HIGH"
                    elif severity == 'MEDIUM':
                        sev_style = medium_style
                        sev_label = "[*] MEDIUM"
                    else:
                        sev_style = low_style
                        sev_label = "[+] LOW"
                
                    story.append(Paragraph(f"[{sev_label}]", sev_style))
                
                    clean_title = title.replace('[!]', '').replace('[-]', '').replace('[*]', '').replace('[+]', '').strip()
                    story.append(Paragraph(f"<b>{clean_title}</b>", rec_title_style))
                
                    story.append(Paragraph("<b>Explanation:</b>", rec_label_style))
                    for line in self._wrap_text(explanation, 90):
                        story.append(Paragraph(line, rec_text_style))
                
                    story.append(Paragraph("<b>Action:</b>", rec_label_style))
                    for line in self._wrap_text(action, 90):
                        story.append(Paragraph(line, rec_text_style))
                
                    story.append(Paragraph(f"<b>Timeline:</b> {timeline}", rec_label_style))
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("-" * 80, body_style))
                    story.append(Spacer(1, 6))

            findings = self.results.get('security_findings', [])
            if findings:
                story.append(PageBreak())
                story.append(Paragraph("Security Findings", heading_style))
                story.append(Spacer(1, 6))
            
                for finding in findings[:20]:
                    severity = finding.get('severity', 'UNKNOWN')
                    color_map = {
                        'CRITICAL': colors.red,
                        'HIGH': colors.orange,
                        'MEDIUM': colors.blue,
                        'LOW': colors.green
                    }
                    sev_color = color_map.get(severity, colors.grey)
                
                    finding_style = ParagraphStyle(
                        f'Finding_{severity}',
                        parent=styles['Normal'],
                        textColor=sev_color,
                        fontName='Helvetica-Bold',
                        fontSize=10,
                        alignment=TA_LEFT,
                        spaceAfter=4
                    )
                
                    finding_text = f"<b>[{severity}]</b> {finding.get('finding', '')} <i>({finding.get('ap', 'Unknown')})</i>"
                    story.append(Paragraph(finding_text, finding_style))
                    story.append(Spacer(1, 2))

            aps = self.results.get('wifi_networks', [])
            if aps:
                story.append(Spacer(1, 10))
                story.append(Paragraph("WiFi Access Points", heading_style))
                ap_data = [['SSID', 'BSSID', 'Signal', 'Security', 'Channel']]
                for ap in aps[:30]:
                    ap_data.append([
                        ap.get('ssid', 'Unknown')[:25],
                        ap.get('bssid', 'Unknown')[:17],
                        f"{ap.get('signal', 0)}%",
                        ap.get('security_type', ap.get('security', 'Unknown'))[:10],
                        str(ap.get('channel', 'N/A'))
                    ])
        
                ap_table = Table(ap_data, colWidths=[120, 90, 50, 60, 50])
                ap_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ff00')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0d1117')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#333333')),
                ]))
                story.append(ap_table)

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
                story.append(Spacer(1, 10))
            
                from reportlab.platypus import Table, TableStyle
                bar_data = [[f"{security_score}%"]]
                bar_table = Table(bar_data, colWidths=[security_score * 3], rowHeights=[20])
                bar_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#00ff00')),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                ]))
                story.append(bar_table)

            current_year = datetime.now().year
        
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceAfter=4
            )
        
            footer_bold_style = ParagraphStyle(
                'FooterBold',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#888888'),
                alignment=TA_CENTER,
                spaceAfter=2,
                fontName='Helvetica-Bold'
            )
        
            footer_divider_style = ParagraphStyle(
                'FooterDivider',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#444444'),
                alignment=TA_CENTER,
                spaceAfter=6
            )
        
            story.append(Spacer(1, 30))
            story.append(Paragraph("-" * 80, footer_divider_style))
        
            story.append(Paragraph(
                f"<b>STARK EXPO TECH EXCHANGE LTD</b>",
                footer_bold_style
            ))
        
            story.append(Paragraph(
                f"DSTerminal v{self.VERSION}  |  (c) {current_year} Stark Expo Tech Exchange LTD  |  All Rights Reserved",
                footer_style
            ))
        
            story.append(Paragraph(
                f"Report ID: {doc.report_id}  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                footer_style
            ))
        
            story.append(Paragraph(
                f"Powered by DSTERMINAL Cyber-Ops Platform",
                footer_style
            ))

            doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
            return True

        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[!] PDF generation failed: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False

    def _generate_html_report(self, filename: str) -> bool:
        """Generate HTML report with both WiFi and Ethernet findings."""
        try:
            summary = self.results.get('summary', {})
            findings = self.results.get('security_findings', [])
            recommendations = self.results.get('recommendations', [])
            aps = self.results.get('wifi_networks', [])
            eth_networks = self.results.get('ethernet_networks', [])

            total_aps = summary.get('total_aps', 0)
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100) if total_aps > 0 else 0

            # Build findings HTML
            findings_html = ""
            if findings:
                findings_html = '<div class="section">\n<h2>[!] Security Findings</h2>\n'
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

            # Build recommendations HTML with full details
            recs_html = ""
            if recommendations:
                recs_html = '<div class="section">\n<h2>[+] Recommendations</h2>\n'
                for rec in recommendations:
                    recs_html += f'''
                <div class="recommendation">
                    <div class="rec-title">{rec.get('title', '')}</div>
                    <div class="rec-explanation"><strong>Explanation:</strong> {rec.get('explanation', '')}</div>
                    <div class="rec-action"><strong>Action:</strong> {rec.get('action', '')}</div>
                    <div class="rec-timeline"><strong>Timeline:</strong> {rec.get('timeline', '')}</div>
                </div>
                '''
                recs_html += '</div>\n'

            # Build Ethernet networks HTML
            eth_html = ""
            if eth_networks:
                eth_html = f'<div class="section">\n<h2>[*] Ethernet Networks ({len(eth_networks)})</h2>\n'
                eth_html += '''
                <table class="ap-table">
                    <thead>
                        <tr>
                            <th>Interface</th>
                            <th>IP Address</th>
                            <th>MAC Address</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                '''
                for eth in eth_networks[:20]:
                    eth_html += f'''
                    <tr>
                        <td>{eth.get('name', 'Unknown')}</td>
                        <td>{eth.get('ip', 'N/A')}</td>
                        <td style="font-family: monospace;">{eth.get('mac', 'Unknown')}</td>
                        <td><span class="status-badge { 'status-secure' if eth.get('status') == 'Connected' else 'status-warning' }">{eth.get('status', 'Unknown')}</span></td>
                    </tr>
                '''
                eth_html += '''
                    </tbody>
                </table>
            </div>
            '''

            # Build WiFi access points HTML
            aps_html = ""
            if aps:
                aps_html = f'<div class="section">\n<h2>[+] WiFi Access Points ({len(aps)})</h2>\n'
                aps_html += '''
                <table class="ap-table">
                    <thead>
                        <tr>
                            <th>SSID</th>
                            <th>BSSID</th>
                            <th>Signal</th>
                            <th>Security</th>
                            <th>Channel</th>
                        </tr>
                    </thead>
                    <tbody>
                '''
                for ap in aps[:50]:
                    ssid = ap.get('ssid', 'Unknown')[:30]
                    bssid = ap.get('bssid', 'Unknown')
                    signal = ap.get('signal', 0)
                    security_type = ap.get('security_type', ap.get('security', 'Unknown'))
                    channel = ap.get('channel', 'N/A')
            
                    badge_class = 'status-secure' if security_type in ['WPA2', 'WPA3'] else 'status-warning' if security_type == 'WPA' else 'status-open'
            
                    aps_html += f'''
                    <tr>
                        <td>{ssid}</td>
                        <td style="font-family: monospace;">{bssid}</td>
                        <td>{signal}%</td>
                        <td><span class="status-badge {badge_class}">{security_type}</span></td>
                        <td>{channel}</td>
                    </tr>
                '''
                if len(aps) > 50:
                    aps_html += f'<tr><td colspan="5" style="text-align: center; color: #666;">... and {len(aps) - 50} more access points</td></tr>'
                aps_html += '''
                    </tbody>
                </table>
            </div>
            '''

            html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network & WiFi Security Audit Report - ''' + self.report_id + '''</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 20px;
            min-height: 100vh;
        }
        .watermark {
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
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(26, 26, 46, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 40px rgba(0, 255, 0, 0.08);
            position: relative;
            z-index: 1;
            border: 1px solid rgba(0, 255, 0, 0.15);
        }
        .header {
            text-align: center;
            border-bottom: 2px solid rgba(0, 255, 0, 0.2);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #00ff00;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            letter-spacing: 3px;
        }
        .header .report-id {
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
            padding: 5px 15px;
            display: inline-block;
            border: 1px solid rgba(0, 255, 0, 0.1);
            border-radius: 20px;
        }
        .section {
            background: rgba(13, 17, 23, 0.8);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 3px solid #00ff00;
        }
        .section h2 {
            color: #00ffff;
            font-size: 1.4em;
            margin-bottom: 15px;
            letter-spacing: 2px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .summary-card {
            background: rgba(0, 255, 0, 0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid rgba(0, 255, 0, 0.08);
        }
        .summary-card .value {
            font-size: 28px;
            font-weight: bold;
            color: #00ff00;
        }
        .summary-card .label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .finding {
            padding: 12px 15px;
            margin: 8px 0;
            border-radius: 5px;
            border-left: 4px solid #666;
            background: rgba(255, 255, 255, 0.02);
        }
        .finding.critical { border-left-color: #ff0000; }
        .finding.high { border-left-color: #ff6600; }
        .finding.medium { border-left-color: #ffcc00; }
        .finding.low { border-left-color: #00ccff; }
        .finding .severity {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-right: 10px;
        }
        .severity-critical { background: #ff0000; color: white; }
        .severity-high { background: #ff6600; color: white; }
        .severity-medium { background: #ffcc00; color: black; }
        .severity-low { background: #00ccff; color: black; }
        .recommendation {
            padding: 15px;
            margin: 8px 0;
            border-radius: 5px;
            background: rgba(0, 255, 0, 0.03);
            border-left: 3px solid #00ff00;
        }
        .recommendation .rec-title {
            font-weight: bold;
            color: #f0f6fc;
            font-size: 1.05em;
            margin-bottom: 5px;
        }
        .recommendation .rec-explanation {
            color: #8b949e;
            font-size: 0.9em;
            margin: 3px 0;
        }
        .recommendation .rec-action {
            color: #58a6ff;
            font-size: 0.9em;
            margin: 3px 0;
        }
        .recommendation .rec-timeline {
            color: #d29922;
            font-size: 0.85em;
            margin-top: 3px;
            font-weight: 500;
        }
        .score-bar {
            width: 100%;
            height: 35px;
            background: #1a1a2e;
            border-radius: 17px;
            overflow: hidden;
            margin: 15px 0;
            border: 1px solid rgba(0, 255, 0, 0.1);
        }
        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff0000, #ffcc00, #00ff00);
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
        .ap-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 13px;
        }
        .ap-table th {
            background: rgba(0, 255, 0, 0.1);
            color: #00ff00;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid rgba(0, 255, 0, 0.2);
        }
        .ap-table td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }
        .status-badge {
            display: inline-block;
            padding: 2px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }
        .status-secure { background: rgba(0, 255, 0, 0.2); color: #00ff00; }
        .status-open { background: rgba(255, 0, 0, 0.2); color: #ff0000; }
        .status-warning { background: rgba(255, 204, 0, 0.2); color: #ffcc00; }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(0, 255, 0, 0.1);
            color: #444;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <div class="watermark">DSTERMINAL</div>

    <div class="container">
        <div class="header">
            <h1>[+] Network & WiFi Security Audit</h1>
            <div class="report-id">[+] Report ID: ''' + self.report_id + '''</div>
            <div style="color: #444; font-size: 0.85em; margin-top: 8px;">
                Generated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''
            </div>
        </div>

        <div class="section">
            <h2>[+] Audit Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="value">''' + str(summary.get('total_aps', 0)) + '''</div>
                    <div class="label">Total Access Points</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #00ff00;">''' + str(summary.get('secured_aps', 0)) + '''</div>
                    <div class="label">Secured Networks</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #ff0000;">''' + str(summary.get('open_aps', 0)) + '''</div>
                    <div class="label">Open Networks</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #58a6ff;">''' + str(summary.get('wifi_interfaces', 0)) + '''</div>
                    <div class="label">WiFi Interfaces</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #3fb950;">''' + str(summary.get('ethernet_interfaces', 0)) + '''</div>
                    <div class="label">Ethernet Interfaces</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #d29922;">''' + str(summary.get('rogue_aps', 0)) + '''</div>
                    <div class="label">Rogue APs</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>[+] Security Distribution</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>WPA3: <span style="color: #00ff00;">''' + str(summary.get('wpa3_aps', 0)) + '''</span></div>
                <div>WPA2: <span style="color: #33ff33;">''' + str(summary.get('wpa2_aps', 0)) + '''</span></div>
                <div>WPA: <span style="color: #ffcc00;">''' + str(summary.get('wpa_aps', 0)) + '''</span></div>
                <div>WEP: <span style="color: #ff6600;">''' + str(summary.get('wep_aps', 0)) + '''</span></div>
                <div>Open: <span style="color: #ff0000;">''' + str(summary.get('open_aps', 0)) + '''</span></div>
            </div>
        </div>

        <div class="section">
            <h2>[+] Security Score</h2>
            <div style="font-size: 48px; text-align: center; color: ''' + ('#00ff00' if security_score >= 70 else '#ffcc00' if security_score >= 50 else '#ff0000') + ''';">
                ''' + str(security_score) + '''%
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: ''' + str(security_score) + '''%;">
                    ''' + str(security_score) + '''%
                </div>
            </div>
            <div style="text-align: center; color: ''' + ('#00ff00' if security_score >= 70 else '#ffcc00' if security_score >= 50 else '#ff0000') + ''';">
                ''' + ('EXCELLENT' if security_score >= 90 else 'GOOD' if security_score >= 70 else 'FAIR' if security_score >= 50 else 'POOR') + '''
            </div>
        </div>

        ''' + eth_html + aps_html + findings_html + recs_html + '''

        <div class="footer">
            <p>Generated by <strong>DSTERMINAL v''' + self.VERSION + '''</strong> Network & WiFi Security Audit Engine</p>
            <p>Report ID: ''' + self.report_id + '''</p>
        </div>
    </div>
</body>
</html>'''

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True

        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[!] HTML generation failed: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # MAIN RUN - FIXED UTF-8
    # ========================================================================
    
    def run(self):
        """Main execution method."""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        self.show_banner()
        
        # Network Security Impact Assessment
        self._draw_glow_box(
            "[+] Network Security Impact Assessment",
            [
                "WiFi Network Analysis: SSID, BSSID, channel, signal strength",
                "Ethernet Network Analysis: Interface detection, IP, MAC",
                "Rogue Access Point Detection: Identifying unauthorized APs",
                "Security Protocol Analysis: WEP, WPA, WPA2, WPA3 evaluation",
                "Signal Intelligence: Physical location mapping",
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
        
        # Initialization
        init_lines = [
            f"Platform: {self.system.upper()}",
            f"Host: {self.hostname}",
            f"Interface: {self.interface if self.interface else 'Auto-detecting...'}",
            f"Mode: WiFi + Ethernet Network Audit"
        ]
        
        self._draw_glow_box(
            "[*] Initializing Network Audit Engine",
            init_lines,
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTCYAN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        # Detect all interfaces
        self._draw_glow_box(
            "[+] Detecting Interfaces",
            ["Scanning for all network interfaces..."],
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTGREEN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        # Detect interfaces
        interfaces = self._detect_all_interfaces()
        self.results['interfaces'] = interfaces
        
        # Display detected interfaces
        if interfaces:
            interface_lines = []
            for iface in interfaces:
                iface_type = iface.get('type', 'Unknown')
                icon = "[+]" if iface_type == 'WiFi' else "[*]" if iface_type == 'Ethernet' else "[?]"
                interface_lines.append(f"{icon} {iface.get('name', 'Unknown'):<15} {iface_type:<10} {iface.get('ip', 'N/A')}")
            
            self._draw_glow_box(
                "Detected Interfaces",
                interface_lines,
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTGREEN_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
        
        # Auto-detect WiFi interface if not provided
        if not self.interface:
            if self.system == "windows":
                self.interface = self._detect_windows_interface()
            elif self.system == "linux":
                self.interface = self._detect_linux_interface()
            elif self.system == "darwin":
                self.interface = self._detect_macos_interface()
        
        # WiFi scan
        wifi_interfaces = [i for i in interfaces if i.get('type') == 'WiFi']
        if wifi_interfaces:
            if not self.interface:
                self.interface = wifi_interfaces[0].get('name')
            
            self._draw_glow_box(
                "[+] Scanning WiFi",
                [f"Using interface: {self.interface}"],
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTGREEN_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
            
            if self.system == 'windows':
                self._wifi_audit_windows()
            elif self.system == 'linux':
                self._wifi_audit_linux()
            elif self.system == 'darwin':
                self._wifi_audit_macos()
        else:
            self._draw_glow_box(
                "[.] Info",
                ["No WiFi interfaces detected - scanning Ethernet only"],
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTCYAN_EX,
                width=None,
                blink_title=True,
                glow_border=True
            )
            time.sleep(0.3)
        
        # Analyze findings
        self._draw_glow_box(
            "[*] Analyzing Findings",
            [
                "Processing WiFi network data...",
                "Analyzing Ethernet interfaces...",
                "Evaluating security configurations...",
                "Detecting vulnerabilities..."
            ],
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTMAGENTA_EX,
            content_color=Fore.LIGHTCYAN_EX,
            width=None,
            blink_title=True,
            glow_border=True
        )
        time.sleep(0.3)
        
        self._analyze_findings()
        
        # Display results
        self._display_results()
        
        # Export
        self._export_results()
        
        # Footer
        self._draw_glow_box(
            "[+] Network Audit Complete",
            [
                f"Report ID: {self.report_id}",
                f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Version: DSTerminal v{self.VERSION}",
                f"Status: [+] WiFi + Ethernet Audit Completed"
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
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Network Security Audit Tool - WiFi + Ethernet')
    parser.add_argument('-i', '--interface', help='Network interface to use')
    parser.add_argument('--no-colors', action='store_true', help='Disable colors')
    parser.add_argument('--speed', type=float, default=0.035, 
                       help='Typing speed in seconds per character (default: 0.035)')
    parser.add_argument('--live', action='store_true', help='Live monitoring mode')
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
    
    auditor = NetworkAudit(args.interface)
    auditor.pen_speed = args.speed
    
    if args.live:
        print(f"{Fore.LIGHTCYAN_EX}Live monitoring mode - Press Ctrl+C to stop{Style.RESET_ALL}")
        try:
            while True:
                auditor.results['wifi_networks'] = []
                auditor.results['interfaces'] = []
                auditor.run()
                time.sleep(2)
                os.system('cls' if platform.system() == 'Windows' else 'clear')
        except KeyboardInterrupt:
            print(f"\n{Fore.LIGHTYELLOW_EX}Live monitoring stopped{Style.RESET_ALL}")
    else:
        auditor.run()


if __name__ == "__main__":
    main()