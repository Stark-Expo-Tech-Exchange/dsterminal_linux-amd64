#!python
import sys
"""
DSTerminal Network Security Audit Module
Comprehensive network security assessment with WiFi + Ethernet support
Glowing neon hacker colors, PDF/HTML reports, live monitoring
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
# FIX: REMOVE stdout/stderr manipulation - Let Colorama handle it
# ============================================================

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

# Try to import colorama
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
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
        connected = {'type': 'None'}
        
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
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            is_admin = False
        
        if not is_admin:
            self._draw_glow_box(
                "[-] Warning",
                ["Running without admin privileges - scan results may be limited"],
                title_color=Fore.LIGHTYELLOW_EX,
                border_color=Fore.LIGHTYELLOW_EX,
                content_color=Fore.LIGHTYELLOW_EX
            )
            time.sleep(0.3)
        
        self._draw_glow_box(
            "[+] Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX
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
        self._draw_glow_box(
            "[+] Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX
        )
        time.sleep(0.5)
        pass
    
    def _wifi_audit_macos(self):
        self._draw_glow_box(
            "[+] Scanning",
            ["Scanning for WiFi networks..."],
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTYELLOW_EX,
            content_color=Fore.LIGHTYELLOW_EX
        )
        time.sleep(0.5)
        pass
    
    # ========================================================================
    # ANALYSIS
    # ========================================================================
    
    def _analyze_findings(self):
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
                    'severity': 'CRITICAL',
                    'recommendation': 'Disable open networks immediately. Implement WPA3-Enterprise with 802.1X authentication. If WPA3 is not available, use WPA2-AES with a strong passphrase (minimum 16 characters). Consider implementing a captive portal with authentication.',
                    'action': 'Immediate: Disable open SSID broadcast. Configure WPA3-Enterprise. If WPA3 unavailable, WPA2-AES with strong PSK.',
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
                    'recommendation': 'WEP is a deprecated encryption standard that can be cracked in minutes. Immediately upgrade all WEP networks to WPA3 or WPA2-AES. WEP should be considered COMPROMISED and not used for any sensitive data.',
                    'action': 'Immediate: Identify all WEP devices. Upgrade firmware to support WPA2/WPA3. If upgrade not possible, replace hardware immediately.',
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
                    'recommendation': 'WPA (TKIP) is deprecated and vulnerable to KRACK attacks. Upgrade to WPA2-AES or WPA3. Ensure all devices support AES encryption instead of TKIP.',
                    'action': 'Upgrade: Configure WPA2-AES on all APs. Remove TKIP support. Update client device drivers.',
                    'timeline': 'Within 30 days'
                })
            elif sec_type == 'WPA2':
                summary['wpa2_aps'] += 1
                summary['secured_aps'] += 1
                # Add WPA2 recommendations even though it's secure
                self.results['security_findings'].append({
                    'type': 'WPA2 WiFi',
                    'ap': ap.get('ssid', 'Unknown'),
                    'bssid': ap.get('bssid', 'Unknown'),
                    'finding': 'WPA2 encryption - Consider upgrading to WPA3 for enhanced security',
                    'severity': 'LOW',
                    'recommendation': 'While WPA2 is still considered secure, WPA3 offers enhanced protection against dictionary attacks and provides forward secrecy. Consider upgrading to WPA3 on compatible devices.',
                    'action': 'Plan: Assess WPA3 compatibility. Upgrade firmware on APs. Update client devices to support WPA3.',
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
        
        # Generate comprehensive recommendations from findings
        recommendations = []
        
        # Check for open networks
        if summary.get('open_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': 'CRITICAL: Open WiFi Networks Detected',
                'severity': 'CRITICAL',
                'finding': f'{summary.get("open_aps", 0)} open network(s) found with NO encryption',
                'explanation': 'Open WiFi networks transmit all data in plaintext. Attackers can easily sniff passwords, emails, and sensitive data using simple tools. This is a CRITICAL security risk.',
                'action': '1. Immediately disable open SSID broadcast\n2. Implement WPA3-Enterprise with 802.1X authentication\n3. If WPA3 unavailable, use WPA2-AES with strong PSK (16+ chars)\n4. Consider captive portal for guest access',
                'timeline': 'Immediate (24-48 hours)'
            })
        
        # Check for WEP networks
        if summary.get('wep_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': 'HIGH: WEP Encryption Detected',
                'severity': 'HIGH',
                'finding': f'{summary.get("wep_aps", 0)} WEP-encrypted network(s) found',
                'explanation': 'WEP is a deprecated encryption standard that can be cracked in minutes using tools like Aircrack-ng. It provides NO real security against modern attacks.',
                'action': '1. Identify all WEP devices immediately\n2. Upgrade firmware to support WPA2/WPA3\n3. If upgrade not possible, REPLACE HARDWARE\n4. Use WPA3-Enterprise for highest security',
                'timeline': 'Immediate (72 hours)'
            })
        
        # Check for WPA networks
        if summary.get('wpa_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': 'MEDIUM: WPA (TKIP) Networks Detected',
                'severity': 'MEDIUM',
                'finding': f'{summary.get("wpa_aps", 0)} WPA network(s) using TKIP',
                'explanation': 'WPA with TKIP is deprecated and vulnerable to KRACK attacks. Attackers can decrypt traffic and inject data into the network.',
                'action': '1. Configure all APs to use WPA2-AES (not TKIP)\n2. Remove TKIP compatibility\n3. Update client device drivers\n4. Consider WPA3 for future-proofing',
                'timeline': 'Within 30 days'
            })
        
        # Check for WPA2 networks
        if summary.get('wpa2_aps', 0) > 0 and summary.get('wpa3_aps', 0) == 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': 'LOW: WPA2 Networks - Consider Upgrade',
                'severity': 'LOW',
                'finding': f'{summary.get("wpa2_aps", 0)} WPA2 network(s) without WPA3',
                'explanation': 'While WPA2 is still secure, WPA3 provides enhanced security including protection against dictionary attacks and forward secrecy.',
                'action': '1. Assess WPA3 compatibility for all devices\n2. Upgrade AP firmware to support WPA3\n3. Update client devices to WPA3\n4. Plan transition over 90 days',
                'timeline': 'Within 90 days'
            })
        
        # Check for Ethernet networks
        if summary.get('ethernet_interfaces', 0) > 0:
            recommendations.append({
                'type': 'Ethernet Security',
                'title': 'MEDIUM: Ethernet Networks - Physical Security',
                'severity': 'MEDIUM',
                'finding': f'{summary.get("ethernet_interfaces", 0)} Ethernet interface(s) detected',
                'explanation': 'Ethernet ports are physical access points. Anyone with cable access can connect unauthorized devices to the network.',
                'action': '1. Implement 802.1X authentication for wired networks\n2. Enable port security (MAC limiting)\n3. Disable unused switch ports\n4. Monitor for unauthorized connections',
                'timeline': 'Within 30 days'
            })
        
        # Rogue AP detection
        if summary.get('rogue_aps', 0) > 0:
            recommendations.append({
                'type': 'WiFi Security',
                'title': 'CRITICAL: Rogue Access Points Detected',
                'severity': 'CRITICAL',
                'finding': f'{summary.get("rogue_aps", 0)} unauthorized AP(s) found',
                'explanation': 'Rogue APs are unauthorized access points that bypass security controls. They can be used for man-in-the-middle attacks and data exfiltration.',
                'action': '1. Identify rogue APs using WiFi scanning tools\n2. Physically locate them\n3. Remove them immediately\n4. Investigate how they were connected\n5. Review physical security policy',
                'timeline': 'Immediate (24 hours)'
            })
        
        # Security score-based recommendations
        total_aps = summary.get('total_aps', 0)
        if total_aps > 0:
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100)
            
            if security_score < 50:
                recommendations.append({
                    'type': 'General Security',
                    'title': 'CRITICAL: Poor Security Score - Urgent Action Required',
                    'severity': 'CRITICAL',
                    'finding': f'Security score: {security_score}/100',
                    'explanation': 'Your network has a low security score, indicating significant vulnerabilities that need immediate attention.',
                    'action': '1. Review all security findings above\n2. Prioritize CRITICAL and HIGH severity issues\n3. Create an action plan with deadlines\n4. Conduct weekly security reviews\n5. Implement security awareness training',
                    'timeline': 'Immediate (48 hours)'
                })
            elif security_score < 70:
                recommendations.append({
                    'type': 'General Security',
                    'title': 'HIGH: Security Score Needs Improvement',
                    'severity': 'HIGH',
                    'finding': f'Security score: {security_score}/100',
                    'explanation': 'Your network has moderate security but significant improvements are needed to achieve a secure posture.',
                    'action': '1. Address MEDIUM and HIGH severity findings\n2. Develop a security roadmap\n3. Implement security best practices\n4. Regular monitoring and auditing',
                    'timeline': 'Within 14 days'
                })
        
        # Add general best practice recommendations if no specific findings
        if not recommendations:
            recommendations.append({
                'type': 'General Security',
                'title': 'INFO: Network Appears Secure - Maintain Best Practices',
                'severity': 'LOW',
                'finding': 'No critical security issues found',
                'explanation': 'Your network appears to be properly secured. Continue maintaining security best practices.',
                'action': '1. Continue regular security audits\n2. Update firmware regularly\n3. Monitor for new threats\n4. Maintain security awareness\n5. Review security policies annually',
                'timeline': 'Ongoing (LOW)'
            })
        
        self.results['recommendations'] = recommendations
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    def _display_results(self):
        summary = self.results.get('summary', {})
    
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
    # PDF GENERATION - COMPLETE WITH DETAILED RECOMMENDATIONS
    # ========================================================================
    
    def _generate_pdf_report(self, filename: str) -> bool:
        """Generate PDF report with both WiFi and Ethernet findings and detailed recommendations."""
        if not PDF_AVAILABLE:
            safe_print_unicode("[!] PDF generation requires reportlab. Install: pip install reportlab")
            return False

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            doc = SimpleDocTemplate(
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

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#00ffff'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )

            subheading_style = ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.HexColor('#ffcc00'),
                spaceAfter=8,
                spaceBefore=8,
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
                spaceAfter=6,
                fontName='Helvetica',
                leftIndent=20
            )

            severity_styles = {
                'CRITICAL': ParagraphStyle(
                    'Critical',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#ff0000'),
                    alignment=TA_LEFT,
                    spaceAfter=4,
                    fontName='Helvetica-Bold'
                ),
                'HIGH': ParagraphStyle(
                    'High',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#ff6600'),
                    alignment=TA_LEFT,
                    spaceAfter=4,
                    fontName='Helvetica-Bold'
                ),
                'MEDIUM': ParagraphStyle(
                    'Medium',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#ffcc00'),
                    alignment=TA_LEFT,
                    spaceAfter=4,
                    fontName='Helvetica-Bold'
                ),
                'LOW': ParagraphStyle(
                    'Low',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#00ff00'),
                    alignment=TA_LEFT,
                    spaceAfter=4,
                    fontName='Helvetica-Bold'
                )
            }

            story.append(Paragraph("DSTERMINAL Network Security Audit Report", title_style))
            story.append(Spacer(1, 15))

            summary = self.results.get('summary', {})
            metadata_data = [
                ["Report ID:", self.results.get('report_id', 'N/A')],
                ["Scan Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ["System:", self.system.upper()],
                ["Hostname:", self.hostname],
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

            # Summary Table
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

            # Security Score
            total_aps = summary.get('total_aps', 0)
            if total_aps > 0:
                secured = summary.get('secured_aps', 0)
                security_score = int((secured / total_aps) * 100)
                
                story.append(Paragraph("Security Score", heading_style))
                score_style = ParagraphStyle(
                    'ScoreStyle',
                    parent=styles['Normal'],
                    fontSize=48,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#00ff00' if security_score >= 70 else '#ffcc00' if security_score >= 50 else '#ff0000'),
                    fontName='Helvetica-Bold'
                )
                status_text = "EXCELLENT" if security_score >= 90 else "GOOD" if security_score >= 70 else "FAIR" if security_score >= 50 else "POOR"
                story.append(Paragraph(f"{security_score}/100 - {status_text}", score_style))
                story.append(Spacer(1, 10))

            # Ethernet Networks
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

            # WiFi Access Points
            aps = self.results.get('wifi_networks', [])
            if aps:
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
                story.append(Spacer(1, 20))

            # Security Findings
            findings = self.results.get('security_findings', [])
            if findings:
                story.append(PageBreak())
                story.append(Paragraph("Security Findings", heading_style))
                story.append(Spacer(1, 6))
            
                for finding in findings[:20]:
                    severity = finding.get('severity', 'UNKNOWN')
                    sev_style = severity_styles.get(severity, severity_styles['MEDIUM'])
                    
                    finding_text = f"<b>[{severity}]</b> {finding.get('finding', '')} <i>({finding.get('ap', 'Unknown')})</i>"
                    story.append(Paragraph(finding_text, sev_style))
                    
                    # Add recommendation for this finding
                    if 'recommendation' in finding:
                        rec_text = f"<b>Recommendation:</b> {finding.get('recommendation', '')}"
                        story.append(Paragraph(rec_text, body_style))
                    
                    story.append(Spacer(1, 4))

            # DETAILED RECOMMENDATIONS SECTION
            recommendations = self.results.get('recommendations', [])
            if recommendations:
                story.append(PageBreak())
                story.append(Paragraph("DETAILED RECOMMENDATIONS", heading_style))
                story.append(Spacer(1, 6))
                story.append(Paragraph(
                    "The following recommendations are prioritized based on the security findings identified during the audit.",
                    body_style
                ))
                story.append(Spacer(1, 10))

                # Sort recommendations by severity
                severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                sorted_recs = sorted(
                    recommendations,
                    key=lambda x: severity_order.get(x.get('severity', 'LOW'), 4)
                )

                for i, rec in enumerate(sorted_recs[:15], 1):
                    severity = rec.get('severity', 'MEDIUM')
                    title = rec.get('title', '')
                    finding = rec.get('finding', '')
                    explanation = rec.get('explanation', '')
                    action = rec.get('action', '')
                    timeline = rec.get('timeline', '')

                    # Severity badge
                    sev_style = severity_styles.get(severity, severity_styles['MEDIUM'])
                    story.append(Paragraph(f"Recommendation #{i}", heading_style))
                    story.append(Paragraph(f"<b>{title}</b>", rec_title_style))
                    story.append(Paragraph(f"<b>Severity:</b> {severity}", sev_style))
                    
                    if finding:
                        story.append(Paragraph(f"<b>Finding:</b> {finding}", rec_label_style))
                    
                    story.append(Paragraph("<b>Explanation:</b>", rec_label_style))
                    for line in self._wrap_text(explanation, 90):
                        story.append(Paragraph(line, rec_text_style))
                    
                    story.append(Paragraph("<b>Action Plan:</b>", rec_label_style))
                    for line in self._wrap_text(action, 90):
                        story.append(Paragraph(line, rec_text_style))
                    
                    story.append(Paragraph(f"<b>Timeline:</b> {timeline}", rec_label_style))
                    story.append(Spacer(1, 8))
                    story.append(Paragraph("-" * 80, body_style))
                    story.append(Spacer(1, 4))

            # Footer
            current_year = datetime.now().year
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceAfter=4
            )
        
            story.append(Spacer(1, 30))
            story.append(Paragraph("-" * 80, footer_style))
            story.append(Paragraph(
                f"DSTerminal v{self.VERSION}  |  (c) {current_year} Stark Expo Tech Exchange LTD  |  All Rights Reserved",
                footer_style
            ))
            story.append(Paragraph(
                f"Report ID: {self.report_id}  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                footer_style
            ))

            doc.build(story)
            return True

        except Exception as e:
            safe_print_unicode(f"[!] PDF generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # HTML GENERATION - COMPLETE WITH DETAILED RECOMMENDATIONS
    # ========================================================================
    
    def _generate_html_report(self, filename: str) -> bool:
        """Generate HTML report with both WiFi and Ethernet findings and detailed recommendations."""
        try:
            summary = self.results.get('summary', {})
            findings = self.results.get('security_findings', [])
            recommendations = self.results.get('recommendations', [])
            aps = self.results.get('wifi_networks', [])
            eth_networks = self.results.get('ethernet_networks', [])

            total_aps = summary.get('total_aps', 0)
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100) if total_aps > 0 else 0

            # Build findings HTML with recommendations
            findings_html = ""
            if findings:
                findings_html = '<div class="section">\n<h2>[!] Security Findings</h2>\n'
                for finding in findings[:20]:
                    severity = finding.get('severity', 'UNKNOWN').lower()
                    rec = finding.get('recommendation', '')
                    findings_html += f'''
                <div class="finding {severity}">
                    <span class="severity severity-{severity}">{finding.get('severity', 'UNKNOWN')}</span>
                    {finding.get('finding', '')}
                    <span style="color: #666; font-size: 0.9em;">({finding.get('ap', 'Unknown')})</span>
                    {f'<br><span style="color: #58a6ff; font-size: 0.9em;">Recommendation: {rec}</span>' if rec else ''}
                </div>
                '''
                if len(findings) > 20:
                    findings_html += f'<div style="color: #666; font-style: italic; margin-top: 10px;">... and {len(findings) - 20} more findings</div>'
                findings_html += '</div>\n'

            # Build detailed recommendations HTML
            recs_html = ""
            if recommendations:
                recs_html = '<div class="section">\n<h2>[+] DETAILED RECOMMENDATIONS</h2>\n'
                recs_html += '<p style="color: #8b949e; margin-bottom: 15px;">The following recommendations are prioritized based on the security findings identified during the audit.</p>\n'
                
                # Sort by severity
                severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                sorted_recs = sorted(
                    recommendations,
                    key=lambda x: severity_order.get(x.get('severity', 'LOW'), 4)
                )
                
                for i, rec in enumerate(sorted_recs[:15], 1):
                    severity = rec.get('severity', 'MEDIUM')
                    sev_class = severity.lower()
                    recs_html += f'''
                <div class="recommendation severity-{sev_class}">
                    <div class="rec-number">Recommendation #{i}</div>
                    <div class="rec-title">{rec.get('title', '')}</div>
                    <div class="rec-severity severity-{sev_class}">Severity: {severity}</div>
                    <div class="rec-finding"><strong>Finding:</strong> {rec.get('finding', '')}</div>
                    <div class="rec-explanation"><strong>Explanation:</strong> {rec.get('explanation', '')}</div>
                    <div class="rec-action"><strong>Action Plan:</strong> {rec.get('action', '')}</div>
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
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(26, 26, 46, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 40px rgba(0, 255, 0, 0.08);
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
            border-left: 4px solid #00ff00;
        }
        .recommendation.severity-critical { border-left-color: #ff0000; }
        .recommendation.severity-high { border-left-color: #ff6600; }
        .recommendation.severity-medium { border-left-color: #ffcc00; }
        .recommendation.severity-low { border-left-color: #00ccff; }
        .recommendation .rec-number {
            font-size: 12px;
            color: #666;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .recommendation .rec-title {
            font-weight: bold;
            color: #f0f6fc;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        .recommendation .rec-severity {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin: 5px 0;
        }
        .recommendation .rec-severity.severity-critical { background: #ff0000; color: white; }
        .recommendation .rec-severity.severity-high { background: #ff6600; color: white; }
        .recommendation .rec-severity.severity-medium { background: #ffcc00; color: black; }
        .recommendation .rec-severity.severity-low { background: #00ccff; color: black; }
        .recommendation .rec-finding,
        .recommendation .rec-explanation,
        .recommendation .rec-action,
        .recommendation .rec-timeline {
            margin: 4px 0;
            color: #c9d1d9;
            font-size: 0.9em;
        }
        .recommendation .rec-finding strong,
        .recommendation .rec-explanation strong,
        .recommendation .rec-action strong,
        .recommendation .rec-timeline strong {
            color: #58a6ff;
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
            safe_print_unicode(f"[!] HTML generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # EXPORT
    # ========================================================================
    
    def _export_results(self) -> Optional[str]:
        """Export results to multiple formats."""
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
            for iface in interfaces:
                iface_type = iface.get('type', 'Unknown')
                icon = "[+]" if iface_type == 'WiFi' else "[*]" if iface_type == 'Ethernet' else "[?]"
                interface_lines.append(f"{icon} {iface.get('name', 'Unknown'):<15} {iface_type:<10} {iface.get('ip', 'N/A')}")
            
            self._draw_glow_box(
                "Detected Interfaces",
                interface_lines,
                title_color=Fore.LIGHTCYAN_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTGREEN_EX
            )
            time.sleep(0.3)
        
        if not self.interface:
            try:
                if self.system == "windows":
                    self.interface = self._detect_windows_interface()
                elif self.system == "linux":
                    self.interface = self._detect_linux_interface()
                elif self.system == "darwin":
                    self.interface = self._detect_macos_interface()
            except:
                pass
        
        wifi_interfaces = [i for i in interfaces if i.get('type') == 'WiFi']
        if wifi_interfaces:
            if not self.interface:
                self.interface = wifi_interfaces[0].get('name')
            
            self._draw_glow_box(
                "[+] Scanning WiFi",
                [f"Using interface: {self.interface}"],
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
                "Processing WiFi network data...",
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
                f"Status: [+] WiFi + Ethernet Audit Completed",
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