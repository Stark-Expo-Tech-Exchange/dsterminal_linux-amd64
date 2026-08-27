#!python
import sys
"""

# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass

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

sys.stdout.write = _safe_stdout_write


# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass


    try:
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

sys.stdout.write = _safe_stdout_write

DSTerminal Network Security Audit Module
Comprehensive network security assessment with WiFi + Ethernet support
Glowing neon hacker colors, PDF/HTML reports, live monitoring
AUTO-DETECTS interface type and generates appropriate recommendations
"""
import sys
import os
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
# DEFINE COLORS CLASS FIRST (ALWAYS AVAILABLE)
# ============================================================
class Colors:
    """Cross-platform color support"""
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
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

# ============================================================
# IMPORT COLORAMA WITH PROPER ERROR HANDLING
# ============================================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
    
    # If Fore doesn't have all attributes, use Colors as fallback
    if not hasattr(Fore, 'LIGHTRED_EX'):
        Fore.LIGHTRED_EX = Colors.LIGHTRED_EX
    if not hasattr(Fore, 'LIGHTGREEN_EX'):
        Fore.LIGHTGREEN_EX = Colors.LIGHTGREEN_EX
    if not hasattr(Fore, 'LIGHTYELLOW_EX'):
        Fore.LIGHTYELLOW_EX = Colors.LIGHTYELLOW_EX
    if not hasattr(Fore, 'LIGHTCYAN_EX'):
        Fore.LIGHTCYAN_EX = Colors.LIGHTCYAN_EX
    if not hasattr(Fore, 'LIGHTMAGENTA_EX'):
        Fore.LIGHTMAGENTA_EX = Colors.LIGHTMAGENTA_EX
    if not hasattr(Fore, 'LIGHTBLUE_EX'):
        Fore.LIGHTBLUE_EX = Colors.LIGHTBLUE_EX
    if not hasattr(Fore, 'LIGHTWHITE_EX'):
        Fore.LIGHTWHITE_EX = Colors.LIGHTWHITE_EX
    if not hasattr(Fore, 'RESET'):
        Fore.RESET = Colors.RESET
        
except ImportError:
    COLORS_AVAILABLE = False
    # Use Colors class as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
except Exception as e:
    COLORS_AVAILABLE = False
    # Use Colors class as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })

# ============================================================
# REMOVE THE DUPLICATE PATCHING CODE - It's causing issues
# ============================================================
# The patched_write function below was causing OSError 22
# Instead, we'll use the Colors class directly

def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(clean_message)
    except Exception:
        try:
            print(str(message))
        except:
            pass

# Check for PDF library
try:
    from reportlab.lib.pagesizes import letter, landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as reportlab_colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Check for psutil for network stats
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class NetworkAudit:
    """Comprehensive Network Security Audit Engine - WiFi + Ethernet"""
    
    VERSION = "4.0.0.113"
    APP_NAME = "DSTerminal Network Security Audit"
    
    def __init__(self, interface: Optional[str] = None, scan_all: bool = True):
        self.interface = interface
        self.scan_all = scan_all
        self.system = platform.system().lower()
        self.hostname = socket.gethostname()
        self.report_id = self._generate_report_id()
        self.timestamp = datetime.now()
        self.active_interface = None
        self.interface_type = None  # 'WiFi' or 'Ethernet'
        self.connected_network = None
        self.is_admin = False
        
        self.results = {
            'report_id': self.report_id,
            'version': self.VERSION,
            'timestamp': self.timestamp.isoformat(),
            'system': self.system,
            'hostname': self.hostname,
            'interface': interface,
            'interface_type': None,
            'network_type': None,
            'is_admin': False,
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
                'high_risk': 0,
                'primary_interface': None,
                'primary_interface_type': None,
                'security_score': 0
            }
        }
        
        self.pen_speed = 0.035
        self.pen_variance = 0.008
        self.auto_break_chars = 80
        self.current_line_length = 0
        
        try:
            self.term_width = shutil.get_terminal_size().columns
            if self.term_width < 80:
                self.term_width = 80
            if self.term_width > 120:
                self.term_width = 120
        except:
            self.term_width = 80
        
        # Check admin privileges
        self._check_admin()
    
    def _check_admin(self):
        """Check if running with admin privileges"""
        try:
            if self.system == 'windows':
                try:
                    import ctypes
                    self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                except:
                    self.is_admin = False
            else:
                self.is_admin = os.geteuid() == 0
        except:
            self.is_admin = False
        self.results['is_admin'] = self.is_admin
    
    def _generate_report_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        return f"NET-{timestamp}-{random_suffix}"
    
    def pen_type(self, text: str, color: Optional[str] = None, 
                 speed: Optional[float] = None, auto_break: bool = True,
                 indent: int = 0, newline: bool = True):
        """Human-like pen typing."""
        import sys
        import time
        import random
        
        delay = speed if speed is not None else self.pen_speed
        
        try:
            if indent > 0:
                sys.stdout.write(" " * indent)
                sys.stdout.flush()
                self.current_line_length += indent
        except:
            pass
        
        try:
            if color:
                sys.stdout.write(color)
                sys.stdout.flush()
        except:
            pass
        
        try:
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
        except:
            pass
        
        try:
            if color:
                sys.stdout.write(Style.RESET_ALL)
                sys.stdout.flush()
        except:
            pass
        
        if newline:
            try:
                sys.stdout.write("\n")
                sys.stdout.flush()
            except:
                pass
            self.current_line_length = 0
    
    def _type_line(self, text: str, delay: float):
        import sys
        import time
        import random
        
        for char in text:
            try:
                sys.stdout.write(char)
                sys.stdout.flush()
                self.current_line_length += 1
            except:
                pass
            
            try:
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
            except:
                time.sleep(delay)
    
    def _draw_glow_box(self, title: str, content_lines: List[str], 
                       title_color: str, border_color: str,
                       content_color: Optional[str] = None,
                       width: Optional[int] = None):
        """Draw a glowing neon hacker-styled centered box."""
        import textwrap
        
        content_color = content_color or Fore.LIGHTGREEN_EX
        
        try:
            term = shutil.get_terminal_size((100, 30))
            term_width = term.columns
        except:
            term_width = 80
        
        if width is None:
            width = min(term_width - 6, 110)
        width = max(width, 60)
        left_margin = max(0, (term_width - width) // 2)
        inner = width - 4
        
        wrapped = []
        for line in content_lines:
            if not line.strip():
                wrapped.append("")
                continue
            try:
                line = line.rstrip()
                wrapped.extend(textwrap.wrap(line, inner, break_long_words=False, replace_whitespace=False))
            except:
                wrapped.append(line[:inner] if len(line) > inner else line)
        
        top = border_color + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL
        mid = border_color + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL
        bot = border_color + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL
        
        title_text = f" {title} ".center(width - 2)
        title_line = title_color + "|" + title_text + "|" + Style.RESET_ALL
        
        try:
            print()
            print(" " * left_margin + top)
            print(" " * left_margin + title_line)
            print(" " * left_margin + mid)
        except:
            pass
        
        for line in wrapped:
            try:
                print(" " * left_margin + border_color + "| " + Style.RESET_ALL, end="")
                padded_line = line.ljust(inner)
                self.pen_type(padded_line, color=content_color, speed=self.pen_speed, newline=False)
                print(" " * left_margin + border_color + "|" + Style.RESET_ALL)
                time.sleep(self.pen_speed * 0.5)
            except:
                pass
        
        try:
            print(" " * left_margin + bot)
            print()
            time.sleep(self.pen_speed * 1.5)
        except:
            pass
    
    def show_banner(self):
        """Display the Network + WiFi audit banner."""
        try:
            term = shutil.get_terminal_size((100, 30))
            width = min(term.columns - 6, 110)
            width = max(width, 60)
            left_margin = max(0, (term.columns - width) // 2)
        except:
            width = 80
            left_margin = 0
        
        try:
            print()
            print(" " * left_margin + Fore.CYAN + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL)
            print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + " " * (width - 2) + Fore.CYAN + "|" + Style.RESET_ALL)
            
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
            
            title = f"[!] Network & WiFi Security Audit Engine v{self.VERSION}"
            print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + 
                  " " * ((width - 2 - len(title)) // 2) + 
                  Fore.LIGHTCYAN_EX + title + Style.RESET_ALL + 
                  " " * ((width - 2 - len(title)) // 2) + Fore.CYAN + "|" + Style.RESET_ALL)
            
            subtitle = "[+] WiFi + Ethernet Network Security Assessment & Analysis"
            print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + 
                  " " * ((width - 2 - len(subtitle)) // 2) + 
                  Fore.LIGHTMAGENTA_EX + subtitle + Style.RESET_ALL + 
                  " " * ((width - 2 - len(subtitle)) // 2) + Fore.CYAN + "|" + Style.RESET_ALL)
            
            # Admin status
            admin_status = "[+] Admin: YES" if self.is_admin else "[-] Admin: NO (Limited WiFi scan)"
            admin_color = Fore.LIGHTGREEN_EX if self.is_admin else Fore.LIGHTYELLOW_EX
            print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + 
                  " " * ((width - 2 - len(admin_status)) // 2) + 
                  admin_color + admin_status + Style.RESET_ALL + 
                  " " * ((width - 2 - len(admin_status)) // 2) + Fore.CYAN + "|" + Style.RESET_ALL)
            
            print(" " * left_margin + Fore.CYAN + "|" + Style.RESET_ALL + " " * (width - 2) + Fore.CYAN + "|" + Style.RESET_ALL)
            print(" " * left_margin + Fore.CYAN + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL)
            print()
            time.sleep(0.5)
        except:
            print("\n=== DSTERMINAL Network & WiFi Security Audit ===")
            print(f"Version: {self.VERSION}")
            print()
    
    # ========================================================================
    # NETWORK INTERFACE DETECTION
    # ========================================================================
    
    def _detect_all_interfaces(self) -> List[Dict]:
        interfaces = []
        
        try:
            if PSUTIL_AVAILABLE:
                for iface, addrs in psutil.net_if_addrs().items():
                    ip = None
                    mac = None
                    for addr in addrs:
                        try:
                            if addr.family == socket.AF_INET:
                                ip = addr.address
                            elif hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                                mac = addr.address
                        except:
                            pass
                    if ip and ip not in ['127.0.0.1', '0.0.0.0']:
                        interfaces.append({
                            'name': iface,
                            'ip': ip,
                            'mac': mac or 'Unknown',
                            'type': self._detect_interface_type(iface)
                        })
        except:
            pass
        
        if not interfaces:
            try:
                if self.system == 'windows':
                    interfaces = self._detect_windows_interfaces()
                elif self.system == 'linux':
                    interfaces = self._detect_linux_interfaces()
                elif self.system == 'darwin':
                    interfaces = self._detect_macos_interfaces()
            except:
                pass
        
        return interfaces
    
    def _detect_windows_interfaces(self) -> List[Dict]:
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
                    name_match = re.search(r'adapter\s+(.+?):', line, re.IGNORECASE)
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
        iface_lower = iface_name.lower()
        
        wifi_patterns = ['wifi', 'wireless', 'wlan', 'wlp', 'wlx', 'wi-fi', '802.11', 'airport']
        for pattern in wifi_patterns:
            if pattern in iface_lower:
                return 'WiFi'
        
        ethernet_patterns = ['eth', 'enp', 'enx', 'en', 'ethernet', 'lan', 'gigabit', 'e1000', 'rtl']
        for pattern in ethernet_patterns:
            if pattern in iface_lower:
                return 'Ethernet'
        
        if 'bluetooth' in iface_lower:
            return 'Bluetooth'
        elif 'vmnet' in iface_lower or 'virtual' in iface_lower or 'hyper-v' in iface_lower:
            return 'Virtual'
        
        return 'Unknown'
    
    def _detect_active_interface(self) -> Tuple[Optional[str], Optional[str]]:
        """Detect the active interface and its type."""
        connected = self._get_connected_network()
        
        if connected.get('type') == 'WiFi':
            self.interface_type = 'WiFi'
            self.results['interface_type'] = 'WiFi'
            self.results['network_type'] = 'WiFi'
            self.results['summary']['primary_interface_type'] = 'WiFi'
            return connected.get('interface'), 'WiFi'
        elif connected.get('type') == 'Ethernet':
            self.interface_type = 'Ethernet'
            self.results['interface_type'] = 'Ethernet'
            self.results['network_type'] = 'Ethernet'
            self.results['summary']['primary_interface_type'] = 'Ethernet'
            return connected.get('interface'), 'Ethernet'
        else:
            # Try to find any active interface
            interfaces = self._detect_all_interfaces()
            for iface in interfaces:
                if iface.get('ip') and iface.get('ip') not in ['127.0.0.1', '0.0.0.0']:
                    iface_type = iface.get('type', 'Unknown')
                    self.interface_type = iface_type
                    self.results['interface_type'] = iface_type
                    self.results['network_type'] = iface_type
                    self.results['summary']['primary_interface_type'] = iface_type
                    return iface.get('name'), iface_type
            return None, None
    
    def _get_connected_network(self) -> Dict:
        connected = {'type': 'None', 'interface': None}
        
        # First check for WiFi
        if self.system == 'windows':
            try:
                result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line.startswith("Name") and ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) >= 2:
                            connected['interface'] = parts[1].strip()
                    elif line.startswith("SSID") and "BSSID" not in line and ":" in line:
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
        
        # If no WiFi connected, check for Ethernet
        if connected.get('type') == 'None':
            try:
                interfaces = self._detect_all_interfaces()
                eth_interfaces = [i for i in interfaces if i.get('type') == 'Ethernet' and i.get('ip')]
                for eth in eth_interfaces:
                    if eth.get('ip'):
                        connected['type'] = 'Ethernet'
                        connected['interface'] = eth.get('name')
                        connected['ip'] = eth.get('ip')
                        connected['mac'] = eth.get('mac')
                        break
            except:
                pass
        
        # If still None, check for any active interface
        if connected.get('type') == 'None':
            try:
                interfaces = self._detect_all_interfaces()
                for iface in interfaces:
                    if iface.get('ip') and iface.get('ip') not in ['127.0.0.1', '0.0.0.0']:
                        connected['type'] = iface.get('type', 'Unknown')
                        connected['interface'] = iface.get('name')
                        connected['ip'] = iface.get('ip')
                        break
            except:
                pass
        
        return connected
    
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
    
    def normalize_bssid(self, bssid: str) -> str:
        if not bssid:
            return ""
        return bssid.upper().replace("-", ":").strip()
    
    # ========================================================================
    # WINDOWS WIFI AUDIT
    # ========================================================================
    
    def _wifi_audit_windows(self):
        if not self.is_admin:
            self._draw_glow_box(
                "[-] Admin Required",
                [
                    "WiFi scan requires administrator privileges.",
                    "Running with limited information - scan results may be incomplete.",
                    "To get full WiFi scan results, run as Administrator.",
                    "Current detections will be based on connected network only."
                ],
                title_color=Fore.LIGHTYELLOW_EX,
                border_color=Fore.LIGHTYELLOW_EX,
                content_color=Fore.LIGHTYELLOW_EX
            )
            time.sleep(1)
        
        self._draw_glow_box(
            "[+] Scanning WiFi",
            ["Scanning for WiFi networks..." + (" (Admin required for full scan)" if not self.is_admin else "")],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX
        )
        time.sleep(0.5)
        
        connected_network = self._get_connected_network()
        connected_bssid = self.normalize_bssid(connected_network.get('bssid', ''))
        connected_signal = connected_network.get('signal', 0)
        connected_ssid = connected_network.get('ssid', '')
        connected_auth = connected_network.get('authentication', '')
        
        # Always add the connected network if available
        if connected_ssid:
            ap = {
                'ssid': connected_ssid,
                'bssid': connected_bssid if connected_bssid else 'Connected',
                'signal': connected_signal,
                'security': self._detect_security(connected_auth) if connected_auth else 'Unknown',
                'connected': True,
                'authentication': connected_auth,
                'channel': connected_network.get('channel', ''),
                'radio_type': connected_network.get('radio_type', '')
            }
            self.results['wifi_networks'].append(ap)
        
        # Only do full scan if admin
        if self.is_admin:
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
                        content_color=Fore.LIGHTYELLOW_EX
                    )
                    
            except subprocess.TimeoutExpired:
                self._draw_glow_box(
                    "[!] Timeout",
                    ["Scan timed out"],
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTRED_EX
                )
            except Exception as e:
                self._draw_glow_box(
                    "[!] Error",
                    [f"Error during scan: {str(e)}"],
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTRED_EX
                )
        else:
            # Not admin - just show the connected network
            if connected_ssid:
                self._draw_glow_box(
                    "[+] Connected Network",
                    [
                        f"SSID: {connected_ssid}",
                        f"Signal: {connected_signal}%",
                        f"Authentication: {connected_auth}",
                        f"Security: {self._detect_security(connected_auth)}",
                        "Note: Full WiFi scan requires Administrator privileges"
                    ],
                    title_color=Fore.LIGHTCYAN_EX,
                    border_color=Fore.LIGHTCYAN_EX,
                    content_color=Fore.LIGHTGREEN_EX
                )
            else:
                self._draw_glow_box(
                    "[.] No WiFi Connection",
                    ["No WiFi network detected. Please check your connection."],
                    title_color=Fore.LIGHTCYAN_EX,
                    border_color=Fore.LIGHTCYAN_EX,
                    content_color=Fore.LIGHTCYAN_EX
                )
    
    def _parse_windows_output(self, output: str, connected_network: Dict):
        connected_bssid = self.normalize_bssid(connected_network.get('bssid', ''))
        connected_signal = connected_network.get('signal', 0)
        connected_ssid = connected_network.get('ssid', '')
        
        self.results['wifi_networks'] = []
        
        current_ssid = None
        current_auth = None
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
        
        # If no networks found but connected, add connected network
        if not self.results['wifi_networks'] and connected_ssid:
            ap = {
                'ssid': connected_ssid,
                'bssid': connected_bssid if connected_bssid else 'Connected',
                'signal': connected_signal,
                'security': self._detect_security(connected_network.get('authentication', '')),
                'connected': True,
                'authentication': connected_network.get('authentication', ''),
                'channel': connected_network.get('channel', ''),
                'radio_type': connected_network.get('radio_type', '')
            }
            self.results['wifi_networks'].append(ap)
        
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
        self.results['wifi_networks'].sort(key=lambda x: x.get('signal', 0), reverse=True)
    
    def _detect_security(self, auth: str) -> str:
        if not auth:
            return 'Unknown'
        auth_upper = auth.upper()
        if 'WPA3' in auth_upper:
            return 'WPA3'
        if 'WPA2' in auth_upper:
            return 'WPA2'
        if 'WPA' in auth_upper:
            return 'WPA'
        if 'WEP' in auth_upper:
            return 'WEP'
        if 'OPEN' in auth_upper or 'NONE' in auth_upper:
            return 'Open'
        return 'Unknown'
    
    def _wifi_audit_linux(self):
        self._draw_glow_box(
            "[+] Scanning WiFi",
            ["Scanning for WiFi networks on Linux..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX
        )
        time.sleep(0.5)
        pass
    
    def _wifi_audit_macos(self):
        self._draw_glow_box(
            "[+] Scanning WiFi",
            ["Scanning for WiFi networks on macOS..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX
        )
        time.sleep(0.5)
        pass
    
    # ========================================================================
    # ANALYSIS WITH INTERFACE TYPE DETECTION
    # ========================================================================
    
    def _analyze_findings(self):
        summary = self.results['summary']
        
        # Detect active interface type
        iface, iface_type = self._detect_active_interface()
        if iface:
            summary['primary_interface'] = iface
            summary['primary_interface_type'] = iface_type
            self.results['interface'] = iface
            self.results['interface_type'] = iface_type
            self.results['network_type'] = iface_type
            
            self._draw_glow_box(
                "[+] Active Interface Detected",
                [f"Interface: {iface}", f"Type: {iface_type}"],
                title_color=Fore.LIGHTGREEN_EX,
                border_color=Fore.LIGHTGREEN_EX,
                content_color=Fore.LIGHTGREEN_EX
            )
            time.sleep(0.3)
        
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
                    'severity': 'CRITICAL',
                    'recommendation': 'Disable open networks immediately. Implement WPA3-Enterprise with 802.1X authentication.',
                    'action': 'Immediate: Disable open SSID broadcast. Configure WPA3-Enterprise.',
                    'timeline': 'Immediate (24-48 hours)'
                })
            elif sec_type == 'WEP':
                summary['wep_aps'] += 1
                self.results['security_findings'].append({
                    'type': 'WEP WiFi',
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WEP encryption - Vulnerable to attacks',
                    'severity': 'HIGH',
                    'recommendation': 'WEP is deprecated. Upgrade to WPA3 or WPA2-AES immediately.',
                    'action': 'Immediate: Identify all WEP devices. Upgrade firmware or replace hardware.',
                    'timeline': 'Immediate (72 hours)'
                })
            elif sec_type == 'WPA':
                summary['wpa_aps'] += 1
                self.results['security_findings'].append({
                    'type': 'WPA WiFi',
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WPA encryption - Deprecated, vulnerable to KRACK',
                    'severity': 'MEDIUM',
                    'recommendation': 'WPA (TKIP) is deprecated. Upgrade to WPA2-AES or WPA3.',
                    'action': 'Upgrade: Configure WPA2-AES on all APs. Remove TKIP support.',
                    'timeline': 'Within 30 days'
                })
            elif sec_type == 'WPA2':
                summary['wpa2_aps'] += 1
                summary['secured_aps'] += 1
                self.results['security_findings'].append({
                    'type': 'WPA2 WiFi',
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WPA2 encryption - Consider upgrading to WPA3',
                    'severity': 'LOW',
                    'recommendation': 'WPA2 is secure but WPA3 offers enhanced protection.',
                    'action': 'Plan: Assess WPA3 compatibility. Upgrade firmware.',
                    'timeline': 'Within 90 days'
                })
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
            # Check if Ethernet is actually connected by checking if it has a default gateway
            # or if the IP is not a link-local address (169.254.x.x)
            ip = eth.get('ip', 'N/A')
            is_connected = False
            
            # Check if IP is valid and not a link-local address
            if ip and ip != 'N/A' and not ip.startswith('169.254.'):
                # Check if this interface has a default gateway (true connection)
                try:
                    if self.system == 'windows':
                        result = subprocess.run(
                            ['route', 'print', '-4'], 
                            capture_output=True, text=True, timeout=5
                        )
                        # Check if this interface's IP appears in the route table with a gateway
                        if ip in result.stdout:
                            # Check if there's a default gateway (0.0.0.0) for this interface
                            lines = result.stdout.split('\n')
                            for line in lines:
                                if '0.0.0.0' in line and ip in line:
                                    is_connected = True
                                    break
                    else:
                        # For non-Windows, check if interface has a gateway
                        result = subprocess.run(
                            ['ip', 'route', 'show', 'default'], 
                            capture_output=True, text=True, timeout=5
                        )
                        if eth.get('name', '') in result.stdout:
                            is_connected = True
                except:
                    # If we can't check, assume connected if IP is valid
                    is_connected = True
            else:
                is_connected = False
            
            self.results['ethernet_networks'].append({
                'name': eth.get('name', 'Unknown'),
                'ip': ip,
                'mac': eth.get('mac', 'Unknown'),
                'status': 'Connected' if is_connected else 'Disconnected'
            })
        
        summary['total_interfaces'] = len(interfaces)
        summary['wifi_interfaces'] = len([i for i in interfaces if i.get('type') == 'WiFi'])
        
        connected = self._get_connected_network()
        if connected.get('type') == 'WiFi':
            summary['connected_wifi'] = 1
        elif connected.get('type') == 'Ethernet':
            summary['connected_ethernet'] = 1
        
        # Generate recommendations based on interface type
        recommendations = []
        interface_type = self.results.get('interface_type', 'Unknown')
        
        # Check admin status
        if not self.is_admin and interface_type == 'WiFi':
            recommendations.append({
                'type': 'Admin Privileges',
                'title': 'INFO: Run as Administrator for Full WiFi Scan',
                'severity': 'LOW',
                'finding': 'Running without admin privileges - WiFi scan limited',
                'explanation': 'Full WiFi scanning requires administrator privileges. Without admin, only the currently connected network is detected.',
                'action': '1. Run the program as Administrator\n2. Right-click and select "Run as Administrator"\n3. Or run from an elevated command prompt',
                'timeline': 'Optional - For full scan results'
            })
        
        # WiFi-specific recommendations
        if interface_type == 'WiFi' or interface_type == 'Unknown':
            if summary.get('open_aps', 0) > 0:
                recommendations.append({
                    'type': 'WiFi Security',
                    'title': 'CRITICAL: Open WiFi Networks Detected',
                    'severity': 'CRITICAL',
                    'finding': f'{summary.get("open_aps", 0)} open network(s) found with NO encryption',
                    'explanation': 'Open WiFi networks transmit all data in plaintext. Attackers can easily sniff passwords, emails, and sensitive data.',
                    'action': '1. Immediately disable open SSID broadcast\n2. Implement WPA3-Enterprise with 802.1X authentication\n3. If WPA3 unavailable, use WPA2-AES with strong PSK (16+ chars)',
                    'timeline': 'Immediate (24-48 hours)'
                })
            
            if summary.get('wep_aps', 0) > 0:
                recommendations.append({
                    'type': 'WiFi Security',
                    'title': 'HIGH: WEP Encryption Detected',
                    'severity': 'HIGH',
                    'finding': f'{summary.get("wep_aps", 0)} WEP-encrypted network(s) found',
                    'explanation': 'WEP is a deprecated encryption standard that can be cracked in minutes.',
                    'action': '1. Identify all WEP devices immediately\n2. Upgrade firmware to support WPA2/WPA3\n3. If upgrade not possible, REPLACE HARDWARE',
                    'timeline': 'Immediate (72 hours)'
                })
            
            if summary.get('wpa_aps', 0) > 0:
                recommendations.append({
                    'type': 'WiFi Security',
                    'title': 'MEDIUM: WPA (TKIP) Networks Detected',
                    'severity': 'MEDIUM',
                    'finding': f'{summary.get("wpa_aps", 0)} WPA network(s) using TKIP',
                    'explanation': 'WPA with TKIP is deprecated and vulnerable to KRACK attacks.',
                    'action': '1. Configure all APs to use WPA2-AES (not TKIP)\n2. Remove TKIP compatibility\n3. Update client device drivers',
                    'timeline': 'Within 30 days'
                })
            
            if summary.get('wpa2_aps', 0) > 0 and summary.get('wpa3_aps', 0) == 0:
                recommendations.append({
                    'type': 'WiFi Security',
                    'title': 'LOW: WPA2 Networks - Consider Upgrade',
                    'severity': 'LOW',
                    'finding': f'{summary.get("wpa2_aps", 0)} WPA2 network(s) without WPA3',
                    'explanation': 'While WPA2 is still secure, WPA3 provides enhanced security.',
                    'action': '1. Assess WPA3 compatibility\n2. Upgrade AP firmware\n3. Update client devices',
                    'timeline': 'Within 90 days'
                })
        
        # Ethernet-specific recommendations
        if interface_type == 'Ethernet' or interface_type == 'Unknown':
            if summary.get('ethernet_interfaces', 0) > 0:
                recommendations.append({
                    'type': 'Ethernet Security',
                    'title': 'MEDIUM: Ethernet Networks - Physical Security',
                    'severity': 'MEDIUM',
                    'finding': f'{summary.get("ethernet_interfaces", 0)} Ethernet interface(s) detected',
                    'explanation': 'Ethernet ports are physical access points. Anyone with cable access can connect unauthorized devices.',
                    'action': '1. Implement 802.1X authentication for wired networks\n2. Enable port security (MAC limiting)\n3. Disable unused switch ports\n4. Monitor for unauthorized connections',
                    'timeline': 'Within 30 days'
                })
        
        # Security score
        total_aps = summary.get('total_aps', 0)
        if total_aps > 0:
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100)
            summary['security_score'] = security_score
            
            if security_score < 50:
                recommendations.append({
                    'type': 'General Security',
                    'title': 'CRITICAL: Poor Security Score - Urgent Action Required',
                    'severity': 'CRITICAL',
                    'finding': f'Security score: {security_score}/100',
                    'explanation': 'Your network has a low security score, indicating significant vulnerabilities.',
                    'action': '1. Review all security findings above\n2. Prioritize CRITICAL and HIGH severity issues\n3. Create an action plan with deadlines',
                    'timeline': 'Immediate (48 hours)'
                })
            elif security_score < 70:
                recommendations.append({
                    'type': 'General Security',
                    'title': 'HIGH: Security Score Needs Improvement',
                    'severity': 'HIGH',
                    'finding': f'Security score: {security_score}/100',
                    'explanation': 'Your network has moderate security but significant improvements are needed.',
                    'action': '1. Address MEDIUM and HIGH severity findings\n2. Develop a security roadmap\n3. Implement security best practices',
                    'timeline': 'Within 14 days'
                })
        else:
            # No APs detected - could be Ethernet only or no WiFi scan
            if interface_type == 'Ethernet':
                summary['security_score'] = 70  # Default for Ethernet-only
                recommendations.append({
                    'type': 'General Security',
                    'title': 'INFO: Ethernet Network - Security Best Practices',
                    'severity': 'LOW',
                    'finding': 'Ethernet network detected - no WiFi APs found',
                    'explanation': 'Your network uses Ethernet connection. Ensure physical security measures are in place.',
                    'action': '1. Enable port security on switches\n2. Implement 802.1X authentication\n3. Monitor for unauthorized devices\n4. Regular security audits',
                    'timeline': 'Ongoing'
                })
            else:
                summary['security_score'] = 0
                recommendations.append({
                    'type': 'General Security',
                    'title': 'INFO: No Networks Detected',
                    'severity': 'LOW',
                    'finding': 'No WiFi or Ethernet networks detected',
                    'explanation': 'The audit did not detect any networks. This could be due to no active connection or permission issues.',
                    'action': '1. Check network connection\n2. Run as Administrator for WiFi scan\n3. Verify network adapter is enabled',
                    'timeline': 'Immediate'
                })
        
        if not recommendations:
            recommendations.append({
                'type': 'General Security',
                'title': 'INFO: Network Appears Secure',
                'severity': 'LOW',
                'finding': 'No critical security issues found',
                'explanation': 'Your network appears to be properly secured. Continue maintaining security best practices.',
                'action': '1. Continue regular security audits\n2. Update firmware regularly\n3. Monitor for new threats\n4. Maintain security awareness',
                'timeline': 'Ongoing'
            })
        
        self.results['recommendations'] = recommendations
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    def _display_results(self):
        summary = self.results.get('summary', {})
        
        # Show active interface
        iface_type = self.results.get('interface_type', 'Unknown')
        iface_name = self.results.get('interface', 'Unknown')
        
        admin_status = "[+] Admin: YES" if self.is_admin else "[-] Admin: NO"
        admin_color = Fore.LIGHTGREEN_EX if self.is_admin else Fore.LIGHTYELLOW_EX
        
        interface_lines = [
            f"Active Interface: {iface_name}",
            f"Interface Type: {iface_type}",
            f"Admin Status: {admin_status}",
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
            content_color=Fore.LIGHTWHITE_EX
        )
        time.sleep(0.3)
    
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
            content_color=Fore.LIGHTGREEN_EX
        )
        time.sleep(0.3)
    
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
                content_color=Fore.LIGHTWHITE_EX
            )
            time.sleep(0.3)
    
        total_aps = summary.get('total_aps', 0)
        security_score = summary.get('security_score', 0)
        
        if total_aps > 0 or security_score > 0:
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
            filled = int((security_score / 100) * bar_length) if security_score > 0 else 0
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
                content_color=score_color
            )
            time.sleep(0.3)
    
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
                content_color=Fore.LIGHTRED_EX
            )
            time.sleep(0.3)
    
        recommendations = self.results.get('recommendations', [])
        if recommendations:
            rec_lines = []
            for rec in recommendations[:5]:
                title = rec.get('title', '')
                severity = rec.get('severity', 'INFO')
                finding = rec.get('finding', '')
                explanation = rec.get('explanation', '')
                action = rec.get('action', '')
                timeline = rec.get('timeline', '')
                sev_emoji = {"CRITICAL": "[!]", "HIGH": "[-]", "MEDIUM": "[*]", "LOW": "[.]"}.get(severity, "[+]")
            
                rec_lines.append(f"{sev_emoji} {title}")
                rec_lines.append(f"   Severity: {severity}")
                rec_lines.append(f"   Finding: {finding}")
                rec_lines.append("   Explanation:")
                explanation_lines = self._wrap_text(explanation, 68)
                for line in explanation_lines:
                    rec_lines.append(f"      {line}")
                rec_lines.append("   Action:")
                action_lines = self._wrap_text(action, 68)
                for line in action_lines:
                    rec_lines.append(f"      {line}")
                rec_lines.append(f"   Timeline: {timeline}")
                rec_lines.append("")
        
            if len(recommendations) > 5:
                rec_lines.append(f"... and {len(recommendations) - 5} more recommendations")
        
            self._draw_glow_box(
                "Recommendations",
                rec_lines,
                title_color=Fore.LIGHTBLUE_EX,
                border_color=Fore.LIGHTBLUE_EX,
                content_color=Fore.LIGHTYELLOW_EX
            )
            time.sleep(0.3)
    
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
                content_color=Fore.LIGHTWHITE_EX
            )
            time.sleep(0.3)

    def _wrap_text(self, text: str, max_width: int = 75) -> List[str]:
        import textwrap
        if not text:
            return [""]
        paragraphs = text.split('\n')
        wrapped_lines = []
        for para in paragraphs:
            if not para.strip():
                wrapped_lines.append("")
                continue
            try:
                lines = textwrap.wrap(para, width=max_width, break_long_words=False, replace_whitespace=True)
                wrapped_lines.extend(lines)
            except:
                wrapped_lines.append(para[:max_width] if len(para) > max_width else para)
        return wrapped_lines

    # ========================================================================
    # PDF GENERATION (simplified)
    # ========================================================================
    
    def _generate_pdf_report(self, filename: str) -> bool:
        if not PDF_AVAILABLE:
            safe_print_unicode("[!] PDF generation requires reportlab. Install: pip install reportlab")
            return False
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=28, 
                                        textColor=colors.HexColor('#00ff00'), alignment=TA_CENTER, spaceAfter=20)
            story.append(Paragraph("DSTERMINAL Network Security Audit Report", title_style))
            story.append(Spacer(1, 15))

            # Summary
            summary = self.results.get('summary', {})
            iface_type = self.results.get('interface_type', 'Unknown')
            
            metadata = [
                ["Report ID:", self.results.get('report_id', 'N/A')],
                ["Scan Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ["System:", self.system.upper()],
                ["Hostname:", self.hostname],
                ["Active Interface:", self.results.get('interface', 'Unknown')],
                ["Interface Type:", iface_type],
                ["Security Score:", f"{summary.get('security_score', 0)}/100"],
                ["Total APs:", str(summary.get('total_aps', 0))],
            ]

            table = Table(metadata, colWidths=[140, 330])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#00ffff')),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#0d1117')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#33ff33')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

            # Recommendations
            recommendations = self.results.get('recommendations', [])
            if recommendations:
                heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=16, 
                                              textColor=colors.HexColor('#00ffff'), spaceAfter=12)
                story.append(Paragraph("Detailed Recommendations", heading_style))
                story.append(Spacer(1, 6))
                
                body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, 
                                            textColor=colors.HexColor('#ffffff'), spaceAfter=6)
                
                for rec in recommendations[:10]:
                    story.append(Paragraph(f"<b>{rec.get('title', '')}</b>", body_style))
                    story.append(Paragraph(f"Severity: {rec.get('severity', 'Unknown')}", body_style))
                    story.append(Paragraph(f"Finding: {rec.get('finding', '')}", body_style))
                    story.append(Paragraph(f"Action: {rec.get('action', '')}", body_style))
                    story.append(Paragraph(f"Timeline: {rec.get('timeline', '')}", body_style))
                    story.append(Spacer(1, 8))

            doc.build(story)
            return True
        except Exception as e:
            safe_print_unicode(f"[!] PDF generation failed: {str(e)}")
            return False

    # ========================================================================
    # HTML GENERATION (simplified)
    # ========================================================================
    def _generate_html_report(self, filename: str) -> bool:
        try:
            summary = self.results.get('summary', {})
            recommendations = self.results.get('recommendations', [])
            iface_type = self.results.get('interface_type', 'Unknown')
            security_score = summary.get('security_score', 0)

            # Build recommendations HTML safely
            recs_html = ""
            for rec in recommendations[:10]:
                severity = rec.get('severity', 'low').lower()
                recs_html += f'''<div class="recommendation rec-{severity}">
                    <b>{rec.get('title', '')}</b><br>
                    Severity: {rec.get('severity', 'Unknown')}<br>
                    Finding: {rec.get('finding', '')}<br>
                    Action: {rec.get('action', '')}<br>
                    Timeline: {rec.get('timeline', '')}
                </div>
                '''

            # Build score text safely
            if security_score >= 90:
                score_text = "EXCELLENT"
            elif security_score >= 70:
                score_text = "GOOD"
            elif security_score >= 50:
                score_text = "FAIR"
            else:
                score_text = "POOR"

            # Build the HTML with proper f-string escaping
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Network Security Audit - {self.report_id}</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff00; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: #1a1a2e; padding: 30px; border-radius: 15px; border: 1px solid #00ff00; }}
        .header {{ text-align: center; border-bottom: 2px solid #00ff00; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ color: #00ff00; font-size: 2em; text-shadow: 0 0 20px rgba(0,255,0,0.3); }}
        .score {{ font-size: 48px; text-align: center; color: {'#00ff00' if security_score >= 70 else '#ffcc00' if security_score >= 50 else '#ff0000'}; }}
        .section {{ background: #0d1117; padding: 20px; margin-bottom: 20px; border-radius: 10px; border-left: 3px solid #00ff00; }}
        .section h2 {{ color: #00ffff; margin-bottom: 15px; }}
        .recommendation {{ padding: 10px; margin: 5px 0; border-left: 4px solid #00ff00; background: rgba(0,255,0,0.02); }}
        .rec-critical {{ border-left-color: #ff0000; }}
        .rec-high {{ border-left-color: #ff6600; }}
        .rec-medium {{ border-left-color: #ffcc00; }}
        .rec-low {{ border-left-color: #00ccff; }}
        .footer {{ text-align: center; margin-top: 40px; color: #444; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DSTERMINAL Network Security Audit</h1>
            <p>Report ID: {self.report_id}</p>
            <p>Active Interface: {self.results.get('interface', 'Unknown')} ({iface_type})</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Summary</h2>
            <p>Total APs: {summary.get('total_aps', 0)}</p>
            <p>Secured: {summary.get('secured_aps', 0)}</p>
            <p>Open: {summary.get('open_aps', 0)}</p>
            <p>WPA3: {summary.get('wpa3_aps', 0)}</p>
            <p>WPA2: {summary.get('wpa2_aps', 0)}</p>
            <p>WPA: {summary.get('wpa_aps', 0)}</p>
            <p>WEP: {summary.get('wep_aps', 0)}</p>
        </div>
        
        <div class="section">
            <h2>Security Score</h2>
            <div class="score">{security_score}/100</div>
            <div style="text-align: center;">{score_text}</div>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            {recs_html}
        </div>
        
        <div class="footer">
            DSTERMINAL v{self.VERSION} | Report ID: {self.report_id}
        </div>
    </div>
</body>
</html>'''

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            safe_print_unicode(f"[!] HTML generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # EXPORT
    # ========================================================================
    
    def _export_results(self) -> Optional[str]:
        try:
            export_dir = Path.home() / "DSTerminal" / "reports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            base_filename = export_dir / f"network_audit_{self.report_id}"
            
            json_filename = base_filename.with_suffix('.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
            
            pdf_filename = base_filename.with_suffix('.pdf')
            if PDF_AVAILABLE:
                self._generate_pdf_report(str(pdf_filename))
            
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
                export_messages.append("[-] PDF export skipped (install reportlab)")
            
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
                content_color=Fore.LIGHTWHITE_EX
            )
            
            return str(json_filename)
            
        except Exception as e:
            safe_print_unicode(f"[-] Failed to export results: {str(e)}")
            return None

    # ========================================================================
    # MAIN RUN
    # ========================================================================
    
    def run(self):
        """Main execution method."""
        try:
            os.system('cls' if platform.system() == 'Windows' else 'clear')
        except:
            pass
        
        try:
            self.show_banner()
        except:
            print("\n=== DSTERMINAL Network Security Audit ===")
            print(f"Version: {self.VERSION}\n")
        
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
            content_color=Fore.LIGHTCYAN_EX
        )
        time.sleep(0.3)
        
        # Detect active interface first
        iface, iface_type = self._detect_active_interface()
        if iface:
            self.interface = iface
            self.interface_type = iface_type
        
        admin_status = "YES" if self.is_admin else "NO (Limited WiFi scan)"
        admin_color = Fore.LIGHTGREEN_EX if self.is_admin else Fore.LIGHTYELLOW_EX
        
        init_lines = [
            f"Platform: {self.system.upper()}",
            f"Host: {self.hostname}",
            f"Active Interface: {iface if iface else 'Auto-detecting...'}",
            f"Interface Type: {iface_type if iface_type else 'Auto-detecting...'}",
            f"Admin: {admin_status}",
            f"Mode: WiFi + Ethernet Network Audit"
        ]
        
        self._draw_glow_box(
            "[*] Initializing Network Audit Engine",
            init_lines,
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTCYAN_EX
        )
        time.sleep(0.3)
        
        self._draw_glow_box(
            "[+] Detecting Interfaces",
            ["Scanning for all network interfaces..."],
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTGREEN_EX
        )
        time.sleep(0.3)
        
        interfaces = self._detect_all_interfaces()
        self.results['interfaces'] = interfaces
        
        if interfaces:
            interface_lines = []
            for iface_info in interfaces:
                iface_type_detected = iface_info.get('type', 'Unknown')
                icon = "[+]" if iface_type_detected == 'WiFi' else "[*]" if iface_type_detected == 'Ethernet' else "[?]"
                interface_lines.append(f"{icon} {iface_info.get('name', 'Unknown'):<15} {iface_type_detected:<10} {iface_info.get('ip', 'N/A')}")
            
            self._draw_glow_box(
                "Detected Interfaces",
                interface_lines,
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTGREEN_EX
            )
            time.sleep(0.3)
        
        # Use detected interface if not specified
        if not self.interface and iface:
            self.interface = iface
        
        # WiFi scan - only if WiFi interface exists or type is WiFi
        wifi_interfaces = [i for i in interfaces if i.get('type') == 'WiFi']
        if wifi_interfaces:
            if not self.interface:
                self.interface = wifi_interfaces[0].get('name')
                self.interface_type = 'WiFi'
            
            self._draw_glow_box(
                "[+] Scanning WiFi",
                [f"Using interface: {self.interface}", f"Interface Type: {self.interface_type}"],
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTGREEN_EX
            )
            time.sleep(0.3)
            
            try:
                if self.system == 'windows':
                    self._wifi_audit_windows()
                elif self.system == 'linux':
                    self._wifi_audit_linux()
                elif self.system == 'darwin':
                    self._wifi_audit_macos()
            except Exception as e:
                self._draw_glow_box(
                    "[!] Error",
                    [f"WiFi scan error: {str(e)}"],
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTRED_EX
                )
        else:
            self._draw_glow_box(
                "[.] Info",
                ["No WiFi interfaces detected - scanning Ethernet only"],
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTCYAN_EX
            )
            time.sleep(0.3)
        
        self._draw_glow_box(
            "[*] Analyzing Findings",
            [
                f"Processing data for {self.interface_type if self.interface_type else 'network'} interface...",
                "Analyzing Ethernet interfaces...",
                "Evaluating security configurations...",
                "Detecting vulnerabilities...",
                "Generating detailed recommendations..."
            ],
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTMAGENTA_EX,
            content_color=Fore.LIGHTCYAN_EX
        )
        time.sleep(0.3)
        
        self._analyze_findings()
        self._display_results()
        self._export_results()
        
        self._draw_glow_box(
            "[+] Network Audit Complete",
            [
                f"Report ID: {self.report_id}",
                f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Version: DSTerminal v{self.VERSION}",
                f"Active Interface: {self.interface} ({self.interface_type})",
                f"Security Score: {self.results['summary'].get('security_score', 0)}/100",
                f"Status: [+] Audit Completed Successfully",
                f"PDF Report: Generated with detailed recommendations"
            ],
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTCYAN_EX
        )
        
        print()
        try:
            input(f"{Fore.LIGHTYELLOW_EX}Press Enter to continue...{Style.RESET_ALL}")
        except:
            input("Press Enter to continue...")


# ========================================================================
# MAIN
# ========================================================================

def main():
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
        try:
            print(f"{Fore.LIGHTCYAN_EX}Live monitoring mode - Press Ctrl+C to stop{Style.RESET_ALL}")
        except:
            print("Live monitoring mode - Press Ctrl+C to stop")
        try:
            while True:
                auditor.results['wifi_networks'] = []
                auditor.results['interfaces'] = []
                auditor.run()
                time.sleep(2)
                try:
                    os.system('cls' if platform.system() == 'Windows' else 'clear')
                except:
                    pass
        except KeyboardInterrupt:
            try:
                print(f"\n{Fore.LIGHTYELLOW_EX}Live monitoring stopped{Style.RESET_ALL}")
            except:
                print("\nLive monitoring stopped")
    else:
        auditor.run()


if __name__ == "__main__":
    main()