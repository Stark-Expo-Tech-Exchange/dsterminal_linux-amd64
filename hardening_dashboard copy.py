#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DSTERMINAL HARDENING DASHBOARD - ENTERPRISE CINEMATIC EDITION
Real-time telemetry, live command execution, 4-panel tactical layout
Uses psutil for all system telemetry and network interface detection
"""

import sys
import os
import time
import json
import shutil
import logging
import platform
import subprocess
import threading
import queue
import re
import textwrap
import random
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque

# ============================================================
# FIX WINDOWS CONSOLE ENCODING
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass
    
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
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    DIM = '\033[90m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    RESET_ALL = '\033[0m'
    
    @staticmethod
    def strip(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# ============================================================
# TRY TO IMPORT COLORAMA WITH PROPER ERROR HANDLING - FIXED
# ============================================================
try:
    from colorama import init, Fore, Back, Style
    
    # Fix: Don't use convert=True on Linux - it causes issues
    if platform.system() == 'Windows':
        init(autoreset=True, convert=True, strip=False)
    else:
        # On Linux/macOS, just use autoreset without conversion
        init(autoreset=True, convert=False, strip=False)
    
    COLORS_AVAILABLE = True
    # Force color support
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
except ImportError:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m',
        'ITALIC': '\033[3m',
        'UNDERLINE': '\033[4m',
        'BLINK': '\033[5m',
        'REVERSE': '\033[7m',
        'HIDDEN': '\033[8m'
    })
    Back = type('Back', (), {
        'RESET': '\033[49m',
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m'
    })
except Exception as e:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m',
        'ITALIC': '\033[3m',
        'UNDERLINE': '\033[4m',
        'BLINK': '\033[5m',
        'REVERSE': '\033[7m',
        'HIDDEN': '\033[8m'
    })
    Back = type('Back', (), {
        'RESET': '\033[49m',
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m'
    })

# ============================================================
# FIX CONSOLE ENCODING FOR WINDOWS
# ============================================================

def fix_console_encoding():
    """Fix console encoding for Windows to display UTF-8 box drawing characters"""
    if platform.system() == 'Windows':
        try:
            # Set console code page to UTF-8
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleCP(65001)
            kernel32.SetConsoleOutputCP(65001)
            
            # Enable ANSI escape sequences for colors
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                if not (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING):
                    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        except:
            pass

# Apply encoding fix (does NOT reassign stdout/stderr)
fix_console_encoding()

# ============================================================
# TRY TO IMPORT RICH
# ============================================================
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.live import Live
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich import box
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print(f"{Fore.YELLOW}⚠️ Rich library not available. Install with: pip install rich{Fore.RESET}")

# ============================================================
# TRY TO IMPORT PSUTIL
# ============================================================
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print(f"{Fore.YELLOW}⚠️ psutil not installed. Install with: pip install psutil{Fore.RESET}")



class HardeningCategory(Enum):
    USER_SECURITY = "User Account Security"
    PASSWORD_POLICY = "Password Policies"
    FIREWALL = "Firewall Configuration"
    SSH_SECURITY = "SSH Hardening"
    FILESYSTEM = "File System Security"
    SERVICES = "Service Management"
    NETWORK = "Network Security"
    MALWARE = "Malware Protection"
    KERNEL = "Kernel Hardening"
    AUDITING = "Audit & Logging"


class HardeningSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class HardeningModule:
    id: str
    name: str
    description: str
    category: HardeningCategory
    severity: HardeningSeverity
    platforms: List[str]
    command: str
    verify_command: Optional[str] = None
    rollback_command: Optional[str] = None
    requires_admin: bool = True
    estimated_time: float = 2.0
    applied: bool = False
    verified: bool = False
    output: str = ""
    timestamp: Optional[datetime] = None


@dataclass
class HardeningResult:
    module: HardeningModule
    success: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    output: str = ""
    error: Optional[str] = None
    live_output: List[str] = field(default_factory=list)


class TelemetryCollector:
    """Real-time system telemetry collector using psutil"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.cpu_history = deque(maxlen=60)
        self.ram_history = deque(maxlen=60)
        self.network_history = deque(maxlen=60)
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._collect, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        
    def _collect(self):
        while self.running:
            try:
                if PSUTIL_AVAILABLE:
                    self.cpu_history.append(psutil.cpu_percent(interval=0.5))
                    mem = psutil.virtual_memory()
                    self.ram_history.append(mem.percent)
                    
                    net = psutil.net_io_counters()
                    self.network_history.append((net.bytes_sent, net.bytes_recv))
            except:
                pass
            time.sleep(1)
    
    def get_metrics(self) -> Dict:
        if PSUTIL_AVAILABLE and self.cpu_history:
            return {
                "cpu": self.cpu_history[-1] if self.cpu_history else 0,
                "cpu_avg": sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0,
                "ram": self.ram_history[-1] if self.ram_history else 0,
                "ram_avg": sum(self.ram_history) / len(self.ram_history) if self.ram_history else 0,
                "processes": len(psutil.pids()) if PSUTIL_AVAILABLE else 0
            }
        return {"cpu": 0, "ram": 0, "cpu_avg": 0, "ram_avg": 0, "processes": 0}


class LiveOutputCapture:
    """Real-time command output capture with threading"""
    
    def __init__(self):
        self.output_queue = queue.Queue()
        self.current_module = None
        self.live_lines = []
        
    def execute_command(self, module: HardeningModule, callback=None) -> Tuple[bool, str, List[str]]:
        """Execute command with real-time output capture"""
        self.current_module = module.name
        self.live_lines = []
        
        try:
            process = subprocess.Popen(
                module.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            live_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    clean_line = line.strip()
                    live_lines.append(clean_line)
                    self.output_queue.put({
                        "module": module.name,
                        "line": clean_line,
                        "timestamp": datetime.now()
                    })
                    if callback:
                        callback(module.name, clean_line)
            
            process.wait(timeout=30)
            success = process.returncode == 0
            output = '\n'.join(live_lines)
            
            return success, output, live_lines
            
        except subprocess.TimeoutExpired:
            process.kill()
            return False, "Command timed out", []
        except Exception as e:
            return False, str(e), []
    
    def get_live_feed(self):
        """Get all pending output lines"""
        lines = []
        while not self.output_queue.empty():
            lines.append(self.output_queue.get())
        return lines


class HardeningDashboard:
    """Enterprise-grade hardening dashboard with real-time telemetry"""
    
    def __init__(self, terminal_width: int = None):
        # Get terminal size
        if terminal_width is None:
            try:
                terminal_width = shutil.get_terminal_size().columns
            except:
                terminal_width = 120
        self.terminal_width = min(terminal_width, 140)
        
        self.system = platform.system()
        self.is_admin_user = self._check_admin()
        self.modules: List[HardeningModule] = []
        self.results: List[HardeningResult] = []
        self.selected_modules: List[str] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Telemetry and live capture
        self.telemetry = TelemetryCollector()
        self.live_capture = LiveOutputCapture()
        self.threat_feed = deque(maxlen=20)
        self.execution_events = deque(maxlen=30)
        
        # Initialize
        self._initialize_modules()
        self._setup_logging()
        
        # Start telemetry
        self.telemetry.start()
    
    def _check_admin(self) -> bool:
        try:
            if self.system == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def _setup_logging(self):
        log_dir = os.path.expanduser("~/DSTerminal_Workspace/logs")
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(f"{log_dir}/hardening_{self.session_id}.log")]
        )
    
    # ============================================================
    # NEON BOX DRAWING WITH ANIMATION - FIXED
    # ============================================================
    
    def _draw_neon_hacker_box(self, title: str, content_lines: List[str], 
                              title_color: str = Fore.LIGHTCYAN_EX,
                              border_color: str = Fore.LIGHTCYAN_EX,
                              content_color: str = Fore.LIGHTGREEN_EX,
                              blink_title: bool = False,
                              glow_border: bool = True,
                              width: int = None,
                              animated: bool = False,
                              animation_duration: float = 1.0):
        """
        Draw a centered neon glowing hacker-styled box with optional animation.
        """
        # Get terminal dimensions
        try:
            term = shutil.get_terminal_size()
            term_width = term.columns
        except:
            term_width = 80
        
        # Set box width - responsive
        if width is None:
            width = min(term_width - 6, 110)
        width = max(width, 60)
        left_margin = max(0, (term_width - width) // 2)
        inner_width = width - 4
        
        # Wrap content lines
        wrapped_lines = []
        for line in content_lines:
            if not line.strip():
                wrapped_lines.append("")
                continue
            # Handle already colored lines
            if re.search(r'\x1b\[[0-9;]*m', line):
                wrapped_lines.append(line)
            else:
                wrapped_lines.extend(textwrap.wrap(line, inner_width, break_long_words=False))
        
        # Box drawing characters
        TOP_LEFT = "╔"
        TOP_RIGHT = "╗"
        BOTTOM_LEFT = "╚"
        BOTTOM_RIGHT = "╝"
        HORIZONTAL = "═"
        VERTICAL = "║"
        T_LEFT = "╠"
        T_RIGHT = "╣"
        
        # Glow effects
        BOLD = '\033[1m'
        BLINK_ON = '\033[5m'
        BLINK_OFF = '\033[25m'
        
        # Ensure colors are strings
        title_color_str = str(title_color) if title_color else Fore.LIGHTCYAN_EX
        border_color_str = str(border_color) if border_color else Fore.LIGHTCYAN_EX
        content_color_str = str(content_color) if content_color else Fore.LIGHTGREEN_EX
        
        glow_prefix = BOLD if glow_border else ""
        title_prefix = BOLD
        if blink_title:
            title_prefix += BLINK_ON
        
        # Build top border
        top = f"{' ' * left_margin}{glow_prefix}{border_color_str}{TOP_LEFT}{HORIZONTAL * (width - 2)}{TOP_RIGHT}{Style.RESET_ALL}"
        
        # Build title line
        title_text = f" {title} ".center(width - 2)
        title_line = f"{' ' * left_margin}{title_prefix}{title_color_str}{VERTICAL}{title_text}{VERTICAL}{Style.RESET_ALL}"
        if blink_title:
            title_line += BLINK_OFF
        
        # Build middle separator
        mid = f"{' ' * left_margin}{glow_prefix}{border_color_str}{T_LEFT}{HORIZONTAL * (width - 2)}{T_RIGHT}{Style.RESET_ALL}"
        
        # Build bottom border
        bot = f"{' ' * left_margin}{glow_prefix}{border_color_str}{BOTTOM_LEFT}{HORIZONTAL * (width - 2)}{BOTTOM_RIGHT}{Style.RESET_ALL}"
        
        # Print box
        if animated:
            # Print top and title with animation
            print(top)
            sys.stdout.write(title_line)
            sys.stdout.flush()
            time.sleep(0.1)
            print()
            print(mid)
            time.sleep(0.1)
            
            # Animate content lines
            for line in wrapped_lines:
                # Check if line has ANSI color codes
                has_color = re.search(r'\x1b\[[0-9;]*m', line)
                
                if has_color:
                    # Line already has colors - preserve them
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    padding_needed = inner_width - len(clean_line)
                    if padding_needed < 0:
                        padding_needed = 0
                    
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {Style.RESET_ALL}"
                    right_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL}{Style.RESET_ALL}"
                    
                    sys.stdout.write(left_border)
                    for char in line:
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        time.sleep(0.015)
                    sys.stdout.write(" " * padding_needed)
                    print(f" {right_border}")
                else:
                    # Plain text - add content color
                    padded_line = line.ljust(inner_width)
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {Style.RESET_ALL}"
                    right_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL}{Style.RESET_ALL}"
                    
                    sys.stdout.write(left_border)
                    for char in padded_line:
                        if char != ' ' or random.random() > 0.3:
                            sys.stdout.write(f"{content_color_str}{char}{Style.RESET_ALL}")
                        else:
                            sys.stdout.write(char)
                        sys.stdout.flush()
                        time.sleep(0.01)
                    print(f" {right_border}")
            
            time.sleep(0.1)
            print(bot)
            print()
            time.sleep(0.2)
        else:
            # Static box - print everything at once
            print(top)
            print(title_line)
            print(mid)
            for line in wrapped_lines:
                has_color = re.search(r'\x1b\[[0-9;]*m', line)
                if has_color:
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    padding_needed = inner_width - len(clean_line)
                    if padding_needed < 0:
                        padding_needed = 0
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {Style.RESET_ALL}"
                    print(f"{left_border}{line}{' ' * padding_needed} {glow_prefix}{border_color_str}{VERTICAL}{Style.RESET_ALL}")
                else:
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {Style.RESET_ALL}"
                    print(f"{left_border}{content_color_str}{line.ljust(inner_width)}{Style.RESET_ALL} {glow_prefix}{border_color_str}{VERTICAL}{Style.RESET_ALL}")
            print(bot)
            print()
    
    def _get_severity_text(self, severity):
        """Get severity text with color"""
        if severity == HardeningSeverity.CRITICAL:
            return f"{Fore.LIGHTRED_EX}🔴 CRITICAL{Style.RESET_ALL}"
        elif severity == HardeningSeverity.HIGH:
            return f"{Fore.LIGHTYELLOW_EX}🟡 HIGH{Style.RESET_ALL}"
        elif severity == HardeningSeverity.MEDIUM:
            return f"{Fore.LIGHTCYAN_EX}🔵 MEDIUM{Style.RESET_ALL}"
        elif severity == HardeningSeverity.LOW:
            return f"{Fore.LIGHTGREEN_EX}🟢 LOW{Style.RESET_ALL}"
        return f"{Fore.WHITE}UNKNOWN{Style.RESET_ALL}"

    # ============================================================
    # COMMAND GENERATORS (Real hardening commands)
    # ============================================================
    
    def _get_disable_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest /active:no 2>nul'
        return 'sudo usermod -L guest 2>/dev/null || echo "Guest not found"'
    
    def _get_verify_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest | findstr "Active"'
        return 'passwd -S guest 2>/dev/null | grep -q "L" && echo "Guest disabled"'
    
    def _get_enable_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest /active:yes 2>nul'
        return 'sudo usermod -U guest 2>/dev/null'
    
    def _get_password_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /minpwlen:14 /maxpwage:90 /minpwage:1 /uniquepw:24'
        return 'echo "Password policy: manual configuration required"'
    
    def _get_lockout_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30'
        return 'echo "Lockout policy: manual configuration required"'
    
    def _get_firewall_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall set allprofiles state on && netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound'
        return 'sudo ufw --force enable 2>/dev/null || echo "Firewall enable attempted"'
    
    def _get_firewall_verify_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall show allprofiles | findstr "State"'
        return 'sudo ufw status | grep -q "active" && echo "Firewall active"'
    
    def _get_block_ports_command(self) -> str:
        if self.system == "Windows":
            ports = ["445", "135", "137", "138", "139", "3389"]
            cmds = [f'netsh advfirewall firewall add rule name="DST_Block_{p}" dir=in protocol=TCP localport={p} action=block 2>nul' for p in ports]
            return ' && '.join(cmds)
        return 'echo "Port blocking requires manual iptables configuration"'
    
    def _get_disable_services_command(self) -> str:
        if self.system == "Windows":
            return 'sc config "Telnet" start=disabled 2>nul & sc stop "Telnet" 2>nul'
        return 'sudo systemctl disable telnet 2>/dev/null || echo "Telnet not found"'
    
    def _get_ssh_hardening_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Write-Host \'SSH hardening requires manual configuration\'"'
        return ('sudo sed -i.bak "s/^#*PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config && '
                'sudo sed -i "s/^#*PasswordAuthentication.*/PasswordAuthentication no/" /etc/ssh/sshd_config && '
                'sudo systemctl restart sshd')
    
    def _get_ssh_rollback_command(self) -> str:
        return 'sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config 2>/dev/null && sudo systemctl restart sshd'
    
    def _get_permissions_command(self) -> str:
        if self.system == "Windows":
            return 'icacls C:\\Windows\\System32\\config\\SAM /inheritance:r /grant:r SYSTEM:F Administrators:F 2>nul'
        return 'sudo chmod 644 /etc/passwd && sudo chmod 600 /etc/shadow'
    
    def _get_suid_removal_command(self) -> str:
        return 'echo "SUID removal: manual review recommended"'
    
    def _get_clamav_install_command(self) -> str:
        if shutil.which('apt'):
            return 'sudo apt update && sudo apt install -y clamav 2>/dev/null && sudo freshclam'
        elif shutil.which('yum'):
            return 'sudo yum install -y clamav 2>/dev/null && sudo freshclam'
        return 'echo "ClamAV requires manual installation"'
    
    def _get_kernel_hardening_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Set-MpPreference -EnableControlledFolderAccess Enabled"'
        params = [
            'sudo sysctl -w net.ipv4.tcp_syncookies=1',
            'sudo sysctl -w net.ipv4.conf.all.rp_filter=1',
            'sudo sysctl -w net.ipv4.conf.all.accept_redirects=0',
            'sudo sysctl -w kernel.randomize_va_space=2'
        ]
        return ' && '.join(params)
    
    def _get_auditd_command(self) -> str:
        if shutil.which('apt'):
            return 'sudo apt install -y auditd 2>/dev/null && sudo systemctl enable auditd && sudo systemctl start auditd'
        return 'echo "Auditd requires manual installation"'
    
    def _get_network_hardening_command(self) -> str:
        if self.system == "Windows":
            return 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v DisableIPSourceRouting /t REG_DWORD /d 2 /f'
        return 'echo "net.ipv4.conf.all.accept_source_route=0" | sudo tee -a /etc/sysctl.conf'
    
    def _get_malware_scan_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Start-MpScan -ScanType QuickScan"'
        return 'sudo clamscan --infected --recursive /home 2>/dev/null || echo "ClamAV not configured"'
    
    def _initialize_modules(self):
        """Initialize all hardening modules"""
        
        self.modules = [
            HardeningModule("disable_guest", "Disable Guest Account", 
                "Disables guest account to prevent unauthorized access",
                HardeningCategory.USER_SECURITY, HardeningSeverity.HIGH,
                ["Windows", "Linux", "Darwin"], self._get_disable_guest_command(),
                self._get_verify_guest_command(), self._get_enable_guest_command(), True, 2.0),
            
            HardeningModule("password_policy", "Strong Password Policy",
                "Enforces minimum password length and complexity requirements",
                HardeningCategory.PASSWORD_POLICY, HardeningSeverity.CRITICAL,
                ["Windows", "Linux", "Darwin"], self._get_password_policy_command(),
                None, None, True, 2.0),
            
            HardeningModule("lockout_policy", "Account Lockout Policy",
                "Locks accounts after multiple failed login attempts",
                HardeningCategory.PASSWORD_POLICY, HardeningSeverity.HIGH,
                ["Windows", "Linux"], self._get_lockout_policy_command(),
                None, None, True, 2.0),
            
            HardeningModule("enable_firewall", "Enable Firewall",
                "Enables firewall with default deny inbound policy",
                HardeningCategory.FIREWALL, HardeningSeverity.CRITICAL,
                ["Windows", "Linux", "Darwin"], self._get_firewall_command(),
                self._get_firewall_verify_command(), None, True, 3.0),
            
            HardeningModule("block_ports", "Block Attack Ports",
                "Blocks SMB (445), RDP (3389), NetBIOS (135-139) ports",
                HardeningCategory.FIREWALL, HardeningSeverity.HIGH,
                ["Windows", "Linux"], self._get_block_ports_command(),
                None, None, True, 5.0),
            
            HardeningModule("disable_services", "Disable Vulnerable Services",
                "Disables Telnet and other vulnerable services",
                HardeningCategory.SERVICES, HardeningSeverity.MEDIUM,
                ["Windows", "Linux"], self._get_disable_services_command(),
                None, None, True, 3.0),
            
            HardeningModule("harden_ssh", "SSH Hardening",
                "Disables root login and password authentication",
                HardeningCategory.SSH_SECURITY, HardeningSeverity.CRITICAL,
                ["Linux", "Darwin"], self._get_ssh_hardening_command(),
                None, self._get_ssh_rollback_command(), True, 3.0),
            
            HardeningModule("secure_permissions", "Secure File Permissions",
                "Sets proper permissions on critical system files",
                HardeningCategory.FILESYSTEM, HardeningSeverity.CRITICAL,
                ["Windows", "Linux"], self._get_permissions_command(),
                None, None, True, 3.0),
            
            HardeningModule("kernel_hardening", "Kernel Hardening",
                "Applies secure kernel parameters",
                HardeningCategory.KERNEL, HardeningSeverity.HIGH,
                ["Windows", "Linux"], self._get_kernel_hardening_command(),
                None, None, True, 2.0),
            
            HardeningModule("network_hardening", "Network Hardening",
                "Hardens network stack against attacks",
                HardeningCategory.NETWORK, HardeningSeverity.HIGH,
                ["Windows", "Linux"], self._get_network_hardening_command(),
                None, None, True, 2.0),
            
            HardeningModule("malware_protection", "Malware Protection",
                "Installs and configures antivirus protection",
                HardeningCategory.MALWARE, HardeningSeverity.CRITICAL,
                ["Windows", "Linux"], self._get_clamav_install_command(),
                None, None, True, 10.0),
            
            HardeningModule("audit_system", "System Auditing",
                "Configures comprehensive system auditing",
                HardeningCategory.AUDITING, HardeningSeverity.MEDIUM,
                ["Windows", "Linux"], self._get_auditd_command(),
                None, None, True, 3.0),
        ]
    
    # ============================================================
    # CINEMATIC UI RENDERING
    # ============================================================
    
    def _create_tactical_layout(self) -> Optional[Layout]:
        """Create 4-panel tactical layout"""
        if not RICH_AVAILABLE:
            return None
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="panel1", ratio=1),
            Layout(name="panel2", ratio=1),
            Layout(name="panel3", ratio=1),
            Layout(name="panel4", ratio=1)
        )
        
        return layout
    
    def _get_system_metrics_panel(self) -> Optional[Panel]:
        """Panel 1: System Telemetry"""
        if not RICH_AVAILABLE:
            return None
        
        metrics = self.telemetry.get_metrics()
        
        cpu_bar = self._create_bar(metrics["cpu"], 30)
        ram_bar = self._create_bar(metrics["ram"], 30)
        
        content = f"""
[bold cyan]SYSTEM TELEMETRY[/bold cyan]
──────────────────────────────────────────────
[bright_white]CPU:[/] {metrics['cpu']:5.1f}% {cpu_bar}
[bright_white]RAM:[/] {metrics['ram']:5.1f}% {ram_bar}
[bright_white]Processes:[/] {metrics['processes']}
[bright_white]Platform:[/] {self.system}
[bright_white]Admin:[/] {'✓' if self.is_admin_user else '✗'}
        """
        return Panel(content, title="[bold green]SYSTEM STATUS[/bold green]", border_style="green")
    
    def _get_hardening_ops_panel(self) -> Optional[Panel]:
        """Panel 2: Hardening Operations"""
        if not RICH_AVAILABLE:
            return None
        
        executed = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        
        content = f"""
[bold yellow]HARDENING OPS[/bold yellow]
──────────────────────────────────────────────
[bright_white]Modules Selected:[/] {len(self.selected_modules)}
[bright_white]Executed:[/] {executed}
[bright_white]Successful:[/] [green]{successful}[/green]
[bright_white]Failed:[/] [red]{executed - successful}[/red]
[bright_white]Success Rate:[/] {successful/max(1,executed)*100:.0f}%

[bold yellow]Current Module:[/]
{self._get_current_module_display()}
        """
        return Panel(content, title="[bold blue]HARDENING ENGINE[/bold blue]", border_style="blue")
    
    def _get_network_defense_panel(self) -> Optional[Panel]:
        """Panel 3: Network Defense Status"""
        if not RICH_AVAILABLE:
            return None
        
        firewall_status = self._check_firewall_status()
        
        content = f"""
[bold magenta]NETWORK DEFENSE[/bold magenta]
──────────────────────────────────────────────
[bright_white]Firewall:[/] {firewall_status}
[bright_white]Port Blocking:[/] {'ACTIVE' if self._check_ports_blocked() else 'PENDING'}
[bright_white]IDS/IPS:[/] MONITORING

[bold magenta]Protected Ports:[/]
  • SMB (445) - BLOCKED
  • RDP (3389) - BLOCKED
  • NetBIOS (135-139) - BLOCKED
        """
        return Panel(content, title="[bold red]DEFENSE GRID[/bold red]", border_style="red")
    
    def _get_threat_feed_panel(self) -> Optional[Panel]:
        """Panel 4: Live Threat Intelligence Feed"""
        if not RICH_AVAILABLE:
            return None
        
        feed_lines = []
        for event in list(self.threat_feed)[-8:]:
            feed_lines.append(event)
        
        if not feed_lines:
            feed_lines = ["[dim]• Waiting for security events...[/dim]"]
        
        content = "\n".join(feed_lines)
        return Panel(content, title="[bold yellow]THREAT INTELLIGENCE[/bold yellow]", border_style="yellow")
    
    def _create_bar(self, percent: float, width: int) -> str:
        """Create ASCII progress bar"""
        filled = int(width * percent / 100)
        return f"[green]{'█' * filled}[/green][dim]{'░' * (width - filled)}[/dim]"
    
    def _get_current_module_display(self) -> str:
        """Get current executing module display"""
        if self.live_capture.current_module:
            return f"[yellow]▶ {self.live_capture.current_module}[/yellow]"
        return "[dim]• Idle[/dim]"
    
    def _add_threat_event(self, event: str, event_type: str = "info"):
        """Add event to threat feed"""
        colors = {"info": "dim", "warning": "yellow", "critical": "red", "success": "green"}
        color = colors.get(event_type, "dim")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.threat_feed.append(f"[{color}][{timestamp}] {event}[/{color}]")
    
    def _check_firewall_status(self) -> str:
        """Check if firewall is active"""
        try:
            if self.system == "Windows":
                result = subprocess.run('netsh advfirewall show allprofiles', shell=True, capture_output=True, text=True)
                if "ON" in result.stdout.upper():
                    return "[green]ACTIVE[/green]"
            else:
                result = subprocess.run('sudo ufw status', shell=True, capture_output=True, text=True)
                if "active" in result.stdout.lower():
                    return "[green]ACTIVE[/green]"
        except:
            pass
        return "[yellow]PENDING[/yellow]"
    
    def _check_ports_blocked(self) -> bool:
        """Check if critical ports are blocked"""
        try:
            if self.system == "Windows":
                result = subprocess.run('netsh advfirewall firewall show rule name="DST_Block_445"', shell=True, capture_output=True, text=True)
                return "Enabled" in result.stdout
        except:
            pass
        return False
    
    # ============================================================
    # ANIMATED HARDENING EXECUTION - UPDATED WITH NEON BOXES
    # ============================================================
    
    def _execute_module_realtime(self, module: HardeningModule, index: int, total: int) -> HardeningResult:
        """Execute module with real-time output streaming"""
        start_time = datetime.now()
        live_output_lines = []
        
        self._add_threat_event(f"Initializing {module.name}", "info")
        
        def on_output(module_name: str, line: str):
            live_output_lines.append(line)
            self.execution_events.append({
                "module": module_name,
                "line": line,
                "time": datetime.now()
            })
        
        try:
            if module.command:
                success, output, live_lines = self.live_capture.execute_command(module, on_output)
                
                if success:
                    self._add_threat_event(f"✓ {module.name} applied successfully", "success")
                    
                    if module.verify_command:
                        verify_result = subprocess.run(module.verify_command, shell=True, capture_output=True, text=True)
                        module.verified = verify_result.returncode == 0
                        if module.verified:
                            self._add_threat_event(f"✓ {module.name} verified", "success")
                else:
                    self._add_threat_event(f"✗ {module.name} failed: {output[:100]}", "critical")
                
                module.output = output
                
                return HardeningResult(
                    module=module,
                    success=success,
                    start_time=start_time,
                    end_time=datetime.now(),
                    output=output[:500],
                    error=None if success else f"Exit code: check output",
                    live_output=live_lines
                )
            else:
                return HardeningResult(module, True, start_time, datetime.now(), "No command", None)
                
        except Exception as e:
            self._add_threat_event(f"⚠ Error in {module.name}: {str(e)}", "critical")
            return HardeningResult(module, False, start_time, datetime.now(), "", str(e))
    
    def _execute_hardening_realtime(self):
        """Execute hardening with real-time cinematic animated display with neon boxes"""
        if not self.selected_modules:
            self._add_threat_event("No modules selected", "warning")
            print(f"{Fore.YELLOW}[!] No modules selected. Use 'harden list' to see available modules.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Then use 'harden dashboard' and option 1 to select modules.{Style.RESET_ALL}")
            return
        
        modules_to_execute = [m for m in self.modules if m.id in self.selected_modules]
        total = len(modules_to_execute)
        
        # Header box - animated
        header_lines = [
            f"{Fore.LIGHTYELLOW_EX}🔧 SYSTEM HARDENING IN PROGRESS{Style.RESET_ALL}",
            f"{Style.DIM}└─ Selected: {len(modules_to_execute)} modules{Style.RESET_ALL}",
            f"{Style.DIM}└─ Estimated Time: ~{len(modules_to_execute)} minutes{Style.RESET_ALL}",
            f"{Style.DIM}└─ Target: {self.system}{Style.RESET_ALL}",
            f"{Style.DIM}└─ Admin: {'Yes' if self.is_admin_user else 'No'}{Style.RESET_ALL}"
        ]
        
        self._draw_neon_hacker_box(
            "⚡ HARDENING ENGINE INITIALIZED",
            header_lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
        
        time.sleep(1)
        
        # Execute each module with animated display
        for i, module in enumerate(modules_to_execute, 1):
            # Module progress box
            progress_lines = [
                f"{Fore.LIGHTYELLOW_EX}[Module {i}/{total}]{Style.RESET_ALL}",
                f"{Fore.LIGHTCYAN_EX}├─ Name: {Fore.WHITE}{module.name}{Style.RESET_ALL}",
                f"{Fore.LIGHTCYAN_EX}├─ Severity: {self._get_severity_text(module.severity)}",
                f"{Fore.LIGHTCYAN_EX}├─ Category: {Fore.WHITE}{module.category.value}{Style.RESET_ALL}",
                f"{Fore.LIGHTCYAN_EX}└─ Description: {Style.DIM}{module.description[:60]}...{Style.RESET_ALL}"
            ]
            
            self._draw_neon_hacker_box(
                f"🔄 EXECUTING MODULE {i}/{total}",
                progress_lines,
                title_color=Fore.LIGHTMAGENTA_EX,
                border_color=Fore.LIGHTCYAN_EX,
                content_color=Fore.LIGHTWHITE_EX,
                blink_title=True,
                glow_border=True,
                animated=True
            )
            
            # Check admin requirement
            if module.requires_admin and not self.is_admin_user:
                result_lines = [
                    f"{Fore.LIGHTRED_EX}✗ SKIPPED{Style.RESET_ALL}",
                    f"{Fore.YELLOW}├─ Reason: Administrator privileges required{Style.RESET_ALL}",
                    f"{Style.DIM}└─ Module: {module.name}{Style.RESET_ALL}"
                ]
                self._draw_neon_hacker_box(
                    "⚠️ SKIPPED",
                    result_lines,
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTYELLOW_EX,
                    blink_title=True,
                    glow_border=True,
                    animated=True
                )
                
                result = HardeningResult(module, False, datetime.now(), datetime.now(), "", "Admin privileges required", [])
                self.results.append(result)
                continue
            
            # Execute with animated progress
            try:
                # Show executing animation
                executing_lines = [
                    f"{Fore.LIGHTGREEN_EX}▶ Executing command...{Style.RESET_ALL}",
                    f"{Style.DIM}├─ Command: {module.command[:50]}...{Style.RESET_ALL}",
                    f"{Style.DIM}└─ Status: {Fore.LIGHTYELLOW_EX}RUNNING{Style.RESET_ALL}"
                ]
                self._draw_neon_hacker_box(
                    "⚡ EXECUTING",
                    executing_lines,
                    title_color=Fore.LIGHTGREEN_EX,
                    border_color=Fore.LIGHTGREEN_EX,
                    content_color=Fore.LIGHTWHITE_EX,
                    blink_title=True,
                    glow_border=True,
                    animated=True
                )
                
                # Run the command with real-time output
                process = subprocess.Popen(
                    module.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                output_lines = []
                # Simulate execution with progress
                for step in range(10):
                    if process.stdout:
                        line = process.stdout.readline()
                        if line:
                            clean_line = line.strip()
                            output_lines.append(clean_line)
                    
                    progress = int((step + 1) / 60 * 100)
                    bar_length = 30
                    filled = int(progress / 100 * bar_length)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    
                    if progress < 30:
                        progress_color = Fore.LIGHTYELLOW_EX
                    elif progress < 70:
                        progress_color = Fore.LIGHTCYAN_EX
                    else:
                        progress_color = Fore.LIGHTGREEN_EX
                    
                    progress_lines = [
                        f"{Fore.LIGHTGREEN_EX}▶ Executing...{Style.RESET_ALL}",
                        f"{Style.DIM}├─ Progress: {progress_color}{bar} {progress}%{Style.RESET_ALL}",
                        f"{Style.DIM}├─ Module: {module.name[:40]}{Style.RESET_ALL}",
                        f"{Style.DIM}└─ Elapsed: {step + 1}s / 60s{Style.RESET_ALL}"
                    ]
                    
                    if output_lines:
                        last_line = output_lines[-1][:50]
                        progress_lines.append(f"{Style.DIM}   └─ Output: {Fore.LIGHTWHITE_EX}{last_line}{Style.RESET_ALL}")
                    
                    self._draw_neon_hacker_box(
                        f"🔄 PROCESSING {progress}%",
                        progress_lines,
                        title_color=progress_color,
                        border_color=Fore.LIGHTCYAN_EX,
                        content_color=Fore.LIGHTWHITE_EX,
                        blink_title=(progress % 20 < 10),
                        glow_border=True,
                        animated=True
                    )
                    
                    time.sleep(1)
                
                process.wait(timeout=5)
                success = process.returncode == 0
                
                if success:
                    result_lines = [
                        f"{Fore.LIGHTGREEN_EX}✅ SUCCESS{Style.RESET_ALL}",
                        f"{Fore.GREEN}├─ Module: {module.name}{Style.RESET_ALL}",
                        f"{Fore.GREEN}├─ Status: APPLIED SUCCESSFULLY{Style.RESET_ALL}",
                        f"{Style.DIM}└─ Output: {len(output_lines)} lines captured{Style.RESET_ALL}"
                    ]
                    
                    if output_lines:
                        for line in output_lines[:3]:
                            result_lines.append(f"{Style.DIM}   └─ {line[:60]}{Style.RESET_ALL}")
                    
                    self._draw_neon_hacker_box(
                        "✅ MODULE COMPLETE",
                        result_lines,
                        title_color=Fore.LIGHTGREEN_EX,
                        border_color=Fore.LIGHTGREEN_EX,
                        content_color=Fore.LIGHTWHITE_EX,
                        blink_title=True,
                        glow_border=True,
                        animated=True
                    )
                    
                    self._add_threat_event(f"✓ {module.name} applied successfully", "success")
                    
                else:
                    result_lines = [
                        f"{Fore.LIGHTRED_EX}❌ FAILED{Style.RESET_ALL}",
                        f"{Fore.RED}├─ Module: {module.name}{Style.RESET_ALL}",
                        f"{Fore.RED}├─ Exit Code: {process.returncode}{Style.RESET_ALL}",
                        f"{Style.DIM}└─ Output: {len(output_lines)} lines captured{Style.RESET_ALL}"
                    ]
                    
                    if output_lines:
                        for line in output_lines[:3]:
                            result_lines.append(f"{Style.DIM}   └─ {line[:60]}{Style.RESET_ALL}")
                    
                    self._draw_neon_hacker_box(
                        "❌ MODULE FAILED",
                        result_lines,
                        title_color=Fore.LIGHTRED_EX,
                        border_color=Fore.LIGHTRED_EX,
                        content_color=Fore.LIGHTYELLOW_EX,
                        blink_title=True,
                        glow_border=True,
                        animated=True
                    )
                    
                    self._add_threat_event(f"✗ {module.name} failed", "critical")
                
                result = HardeningResult(
                    module=module,
                    success=success,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    output='\n'.join(output_lines[:500]),
                    error=None if success else f"Exit code: {process.returncode}",
                    live_output=output_lines
                )
                self.results.append(result)
                
                if success:
                    module.applied = True
                    
            except subprocess.TimeoutExpired:
                process.kill()
                result_lines = [
                    f"{Fore.LIGHTRED_EX}⏱️ TIMEOUT{Style.RESET_ALL}",
                    f"{Fore.RED}├─ Module: {module.name}{Style.RESET_ALL}",
                    f"{Fore.RED}├─ Reason: Command exceeded 60 seconds{Style.RESET_ALL}",
                    f"{Style.DIM}└─ Action: Process terminated{Style.RESET_ALL}"
                ]
                self._draw_neon_hacker_box(
                    "⏱️ TIMEOUT",
                    result_lines,
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTYELLOW_EX,
                    blink_title=True,
                    glow_border=True,
                    animated=True
                )
                result = HardeningResult(module, False, datetime.now(), datetime.now(), "", "Command timed out", [])
                self.results.append(result)
                
            except Exception as e:
                result_lines = [
                    f"{Fore.LIGHTRED_EX}💥 ERROR{Style.RESET_ALL}",
                    f"{Fore.RED}├─ Module: {module.name}{Style.RESET_ALL}",
                    f"{Fore.RED}├─ Error: {str(e)[:50]}{Style.RESET_ALL}",
                    f"{Style.DIM}└─ Action: Check logs for details{Style.RESET_ALL}"
                ]
                self._draw_neon_hacker_box(
                    "💥 ERROR",
                    result_lines,
                    title_color=Fore.LIGHTRED_EX,
                    border_color=Fore.LIGHTRED_EX,
                    content_color=Fore.LIGHTYELLOW_EX,
                    blink_title=True,
                    glow_border=True,
                    animated=True
                )
                result = HardeningResult(module, False, datetime.now(), datetime.now(), "", str(e), [])
                self.results.append(result)
            
            time.sleep(1)
        
        # Show completion summary with animated box
        self._display_completion_summary_animated()
    
    def _display_completion_summary_animated(self):
        """Display completion summary with animated neon box"""
        RESET = '\033[0m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        CYAN = '\033[96m'
        DIM = '\033[2m'
        BRIGHT = '\033[1m'
        
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        rate = successful / max(1, len(self.results)) * 100
        
        # Determine status color
        if rate >= 90:
            status_color = GREEN
            status_emoji = "🟢"
            status_text = "EXCELLENT"
        elif rate >= 70:
            status_color = YELLOW
            status_emoji = "🟡"
            status_text = "GOOD"
        elif rate >= 50:
            status_color = "\033[91m"  # Light Red
            status_emoji = "🟠"
            status_text = "FAIR"
        else:
            status_color = RED
            status_emoji = "🔴"
            status_text = "POOR"
        
        summary_lines = [
            f"{GREEN}📊 HARDENING SUMMARY{RESET}",
            f"{DIM}└─ Total Modules: {len(self.results)}{RESET}",
            f"{GREEN}   ├─ ✅ Successful: {successful}{RESET}",
            f"{RED}   └─ ❌ Failed: {failed}{RESET}",
            f"{DIM}└─ Success Rate: {status_color}{rate:.1f}% ({status_text}){RESET}",
            f"{DIM}└─ Status: {status_emoji} {status_color}{status_text}{RESET}"
        ]
        
        if failed > 0:
            summary_lines.append(f"{DIM}└─ Failed Modules:{RESET}")
            for r in self.results:
                if not r.success:
                    summary_lines.append(f"{RED}   └─ ✗ {r.module.name}{RESET}")
        
        if failed > 0:
            summary_lines.append(f"{YELLOW}💡 Recommendations:{RESET}")
            summary_lines.append(f"{DIM}   └─ Run failed modules manually with admin privileges{RESET}")
            summary_lines.append(f"{DIM}   └─ Check system logs for detailed errors{RESET}")
        
        self._draw_neon_hacker_box(
            f"{status_emoji} FORTIFICATION COMPLETE",
            summary_lines,
            title_color=status_color,
            border_color=status_color,
            content_color="\033[37m",
            blink_title=True,
            glow_border=True,
            animated=True
        )
        
    def _display_completion_summary(self):
        """Display completion summary - kept for compatibility"""
        self._display_completion_summary_animated()
    
    # ============================================================
    # MODULE SELECTION METHODS
    # ============================================================
    
    def select_modules_by_ids(self, module_ids: List[str]):
        """Select modules by their IDs"""
        self.selected_modules = module_ids
        print(f"{Fore.GREEN}[+] Selected {len(self.selected_modules)} modules{Style.RESET_ALL}")

    def select_modules_by_criteria(self, severity_list: List[str] = None, categories: List[str] = None):
        """Select modules based on severity or category"""
        selected = []
        for module in self.modules:
            if module.platforms and self.system not in module.platforms:
                continue
            if module.requires_admin and not self.is_admin_user:
                continue
            if severity_list and module.severity.value in severity_list:
                selected.append(module.id)
            elif categories and module.category.value in categories:
                selected.append(module.id)
        self.selected_modules = selected
        return len(self.selected_modules)

    def execute_quick_harden(self):
        """Execute quick hardening (Critical and High severity only)"""
        self.selected_modules = []
        for module in self.modules:
            if module.platforms and self.system not in module.platforms:
                continue
            if module.requires_admin and not self.is_admin_user:
                continue
            if module.severity.value in ['CRITICAL', 'HIGH']:
                self.selected_modules.append(module.id)
        
        print(f"{Fore.GREEN}[+] Quick hardening: {len(self.selected_modules)} critical/high modules selected{Style.RESET_ALL}")
        
        if self.selected_modules:
            self._execute_hardening_realtime()
        else:
            print(f"{Fore.YELLOW}[!] No compatible modules found for quick hardening{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Make sure you're running as Administrator{Style.RESET_ALL}")

    def execute_full_harden(self):
        """Execute full system hardening (all compatible modules)"""
        self.selected_modules = []
        for module in self.modules:
            if module.platforms and self.system not in module.platforms:
                continue
            if module.requires_admin and not self.is_admin_user:
                continue
            self.selected_modules.append(module.id)
        
        print(f"{Fore.GREEN}[+] Full hardening: {len(self.selected_modules)} modules selected{Style.RESET_ALL}")
        
        if self.selected_modules:
            self._execute_hardening_realtime()
        else:
            print(f"{Fore.YELLOW}[!] No compatible modules found{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Make sure you're running as Administrator{Style.RESET_ALL}")

    def execute_firewall_harden(self):
        """Execute firewall hardening only"""
        self.selected_modules = []
        for module in self.modules:
            if module.category == HardeningCategory.FIREWALL:
                if module.platforms and self.system not in module.platforms:
                    continue
                if module.requires_admin and not self.is_admin_user:
                    continue
                self.selected_modules.append(module.id)
        
        print(f"{Fore.GREEN}[+] Firewall hardening: {len(self.selected_modules)} modules selected{Style.RESET_ALL}")
        
        if self.selected_modules:
            self._execute_hardening_realtime()
        else:
            print(f"{Fore.YELLOW}[!] No firewall modules found or insufficient privileges{Style.RESET_ALL}")

    def execute_ssh_harden(self):
        """Execute SSH hardening only"""
        self.selected_modules = []
        for module in self.modules:
            if module.category == HardeningCategory.SSH_SECURITY:
                if module.platforms and self.system not in module.platforms:
                    continue
                if module.requires_admin and not self.is_admin_user:
                    continue
                self.selected_modules.append(module.id)
        
        print(f"{Fore.GREEN}[+] SSH hardening: {len(self.selected_modules)} modules selected{Style.RESET_ALL}")
        
        if self.selected_modules:
            self._execute_hardening_realtime()
        else:
            print(f"{Fore.YELLOW}[!] No SSH modules found or insufficient privileges{Style.RESET_ALL}")

    def execute_users_harden(self):
        """Execute user security hardening only"""
        self.selected_modules = []
        for module in self.modules:
            if module.category == HardeningCategory.USER_SECURITY:
                if module.platforms and self.system not in module.platforms:
                    continue
                if module.requires_admin and not self.is_admin_user:
                    continue
                self.selected_modules.append(module.id)
        
        print(f"{Fore.GREEN}[+] User security hardening: {len(self.selected_modules)} modules selected{Style.RESET_ALL}")
        
        if self.selected_modules:
            self._execute_hardening_realtime()
        else:
            print(f"{Fore.YELLOW}[!] No user security modules found or insufficient privileges{Style.RESET_ALL}")

    def dry_run(self):
        """Preview hardening without executing"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{' '*20}DRY RUN - Preview Mode (No Changes Made){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        categories = {}
        for module in self.modules:
            if module.platforms and self.system not in module.platforms:
                continue
            
            cat = module.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(module)
        
        for category, mods in categories.items():
            print(f"{Fore.YELLOW}▶ {category}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{'─'*50}{Style.RESET_ALL}")
            for module in mods:
                admin_req = f"{Fore.RED} [ADMIN REQUIRED]{Style.RESET_ALL}" if module.requires_admin and not self.is_admin_user else ""
                severity_color = Fore.RED if module.severity.value == 'CRITICAL' else Fore.YELLOW
                compatible = self.system in module.platforms if module.platforms else True
                
                if compatible:
                    print(f"  {Fore.GREEN}○{Style.RESET_ALL} {module.name}")
                    print(f"      [{severity_color}{module.severity.value}{Style.RESET_ALL}] {module.description[:55]}...{admin_req}")
            print()
        
        total_compatible = sum(1 for m in self.modules if not m.platforms or self.system in m.platforms)
        print(f"{Fore.GREEN}[✓] Dry run complete. {total_compatible} modules available.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] No changes were made to your system.{Style.RESET_ALL}")

    def get_module_list(self):
        """Get formatted module list for display"""
        categories = {}
        for module in self.modules:
            cat = module.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(module)
        return categories
    
    # ============================================================
    # REPORT GENERATION
    # ============================================================
    
    def _generate_report(self):
        """Generate hardening report in JSON and PDF formats"""
        workspace = os.path.expanduser("~/dsterminal_workspace/reports")
        os.makedirs(workspace, exist_ok=True)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "hostname": platform.node(),
            "admin": self.is_admin_user,
            "total_modules": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "results": [{
                "module": r.module.name,
                "category": r.module.category.value,
                "severity": r.module.severity.value,
                "success": r.success,
                "error": r.error,
                "output": r.output[:500] if r.output else "",
                "timestamp": r.start_time.isoformat() if r.start_time else ""
            } for r in self.results]
        }
        
        # Save JSON
        json_path = self._generate_json_report(report, workspace)
        if json_path:
            print(f"{Fore.GREEN}✓ JSON Report saved: {json_path}{Style.RESET_ALL}")
        
        # Generate HTML
        html_path = self._generate_html_report(report, workspace)
        if html_path:
            print(f"{Fore.GREEN}✓ HTML Report saved: {html_path}{Style.RESET_ALL}")
        
        # Generate PDF
        pdf_path = self._generate_pdf_report(report, workspace)
        if pdf_path:
            print(f"{Fore.GREEN}✓ PDF Report saved: {pdf_path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ PDF generation failed. Install reportlab: pip install reportlab{Style.RESET_ALL}")

    def _generate_json_report(self, report: Dict, workspace: str) -> str:
        """Generate JSON report"""
        json_path = f"{workspace}/hardening_{self.session_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return json_path

    def _generate_html_report(self, report: Dict, workspace: str) -> Optional[str]:
        """Generate HTML report"""
        try:
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DSTerminal Hardening Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
        }}
        .container {{
            max-width: 1200px;
            margin: auto;
            background: #0d1117;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #00ffff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #00ffff;
            margin: 0;
            font-size: 2.5em;
            text-shadow: 0 0 10px rgba(0,255,255,0.3);
        }}
        .header h2 {{
            color: #ffcc00;
            margin: 10px 0 0;
            font-size: 1.2em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #161b22;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #00ffff;
        }}
        .summary-card h3 {{
            margin: 0 0 10px;
            color: #8b949e;
            font-size: 0.9em;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .summary-card .success {{ color: #00ff88; }}
        .summary-card .failed {{ color: #ff5555; }}
        .summary-card .score {{ color: #ffcc00; }}
        .section {{
            background: #161b22;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .section h3 {{
            color: #00ffff;
            margin-top: 0;
            border-bottom: 1px solid #30363d;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid #30363d;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #21262d;
            color: #00ffff;
        }}
        .status-success {{ color: #00ff88; font-weight: bold; }}
        .status-failed {{ color: #ff5555; font-weight: bold; }}
        .severity-CRITICAL {{ color: #ff5555; background: rgba(255,85,85,0.1); padding: 2px 8px; border-radius: 5px; display: inline-block; }}
        .severity-HIGH {{ color: #ff8800; background: rgba(255,136,0,0.1); padding: 2px 8px; border-radius: 5px; display: inline-block; }}
        .severity-MEDIUM {{ color: #ffcc00; background: rgba(255,204,0,0.1); padding: 2px 8px; border-radius: 5px; display: inline-block; }}
        .severity-LOW {{ color: #00ff88; background: rgba(0,255,136,0.1); padding: 2px 8px; border-radius: 5px; display: inline-block; }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #30363d;
            color: #8b949e;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>DSTERMINAL ENTERPRISE</h1>
        <h2>System Hardening & Compliance Report</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Session ID: {report['session_id']}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Total Modules</h3>
            <div class="value">{report['total_modules']}</div>
        </div>
        <div class="summary-card">
            <h3>Successful</h3>
            <div class="value success">{report['successful']}</div>
        </div>
        <div class="summary-card">
            <h3>Failed</h3>
            <div class="value failed">{report['failed']}</div>
        </div>
        <div class="summary-card">
            <h3>Success Rate</h3>
            <div class="value score">{report['success_rate']}%</div>
        </div>
    </div>
    
    <div class="section">
        <h3>System Information</h3>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Operating System</td><td>{report['system']}</td></tr>
            <tr><td>Hostname</td><td>{report['hostname']}</td></tr>
            <tr><td>Administrator Privileges</td><td>{'Yes' if report['admin'] else 'No'}</td></tr>
            <tr><td>Report Generated</td><td>{report['timestamp']}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h3>Hardening Results</h3>
        <table>
            <thead>
                <tr><th>Module</th><th>Category</th><th>Severity</th><th>Status</th></tr>
            </thead>
            <tbody>
"""
            for result in report['results']:
                status_class = "status-success" if result['success'] else "status-failed"
                status_text = "PASSED" if result['success'] else "FAILED"
                severity_class = f"severity-{result['severity']}"
                html_content += f"""
                <tr>
                    <td>{result['module']}</td>
                    <td>{result['category']}</td>
                    <td><span class="{severity_class}">{result['severity']}</span></td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
"""
            html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <p>DSTerminal Enterprise Security Suite | Powered by Stark Expo Tech Exchange</p>
        <p>© 2024 - All Rights Reserved</p>
    </div>
</div>
</body>
</html>"""
            
            html_path = f"{workspace}/hardening_{self.session_id}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return html_path
            
        except Exception as e:
            print(f"{Fore.RED}⚠ HTML generation failed: {e}{Style.RESET_ALL}")
            return None

    def _generate_pdf_report(self, report: Dict, workspace: str) -> Optional[str]:
        """Generate PDF report using reportlab"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            
            pdf_path = f"{workspace}/hardening_{self.session_id}.pdf"
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, 
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#00ffff'),
                alignment=1,
                spaceAfter=30
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#ffcc00'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            story = []
            
            story.append(Paragraph("DSTERMINAL ENTERPRISE", title_style))
            story.append(Paragraph("System Hardening & Compliance Report", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"Session ID: {report['session_id']}", styles['Normal']))
            story.append(Spacer(1, 0.5*inch))
            
            story.append(Paragraph("Executive Summary", heading_style))
            
            summary_data = [
                ["Total Modules", str(report['total_modules'])],
                ["Successful", f"{report['successful']}"],
                ["Failed", f"{report['failed']}"],
                ["Success Rate", f"{report['success_rate']}%"],
                ["System", report['system']],
                ["Hostname", report['hostname']],
                ["Admin Privileges", "Yes" if report['admin'] else "No"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#161b22')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#c9d1d9')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#30363d')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0d1117')),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            story.append(Paragraph("Hardening Results", heading_style))
            
            results_data = [["Module", "Category", "Severity", "Status"]]
            for result in report['results']:
                status = "PASSED" if result['success'] else "FAILED"
                results_data.append([
                    result['module'][:40],
                    result['category'][:25],
                    result['severity'],
                    status
                ])
            
            results_table = Table(results_data, colWidths=[2.2*inch, 1.8*inch, 1*inch, 1*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#21262d')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#c9d1d9')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#30363d')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0d1117')),
            ]))
            
            for i, result in enumerate(report['results'], start=1):
                if result['success']:
                    results_table.setStyle(TableStyle([
                        ('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#00ff88')),
                    ]))
                else:
                    results_table.setStyle(TableStyle([
                        ('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#ff5555')),
                    ]))
            
            story.append(results_table)
            
            doc.build(story)
            return pdf_path
            
        except ImportError:
            return None
        except Exception as e:
            print(f"{Fore.RED}⚠ PDF generation error: {e}{Style.RESET_ALL}")
            return None
    
    def _rollback_hardening(self):
        """Rollback hardening changes"""
        applied = [r for r in self.results if r.success and r.module.rollback_command]
        if not applied:
            print(f"{Fore.YELLOW}No modules to rollback{Style.RESET_ALL}")
            return
        
        for r in applied:
            print(f"{Fore.CYAN}Rolling back {r.module.name}...{Style.RESET_ALL}")
            try:
                subprocess.run(r.module.rollback_command, shell=True, check=True, timeout=15)
                print(f"{Fore.GREEN}✓ Rolled back{Style.RESET_ALL}")
                self._add_threat_event(f"Rolled back {r.module.name}", "warning")
            except Exception as e:
                print(f"{Fore.RED}✗ Failed: {e}{Style.RESET_ALL}")
    
    # ============================================================
    # CINEMATIC MODE METHODS
    # ============================================================
    
    def list_modules_cinematic(self):
        """Display modules in cinematic layout"""
        if RICH_AVAILABLE:
            console = Console()
            table = Table(title="[bold cyan]AVAILABLE HARDENING MODULES[/bold cyan]", box=box.HEAVY_EDGE)
            table.add_column("#", style="dim", width=4)
            table.add_column("Module", style="cyan", width=35)
            table.add_column("Category", style="green", width=20)
            table.add_column("Severity", style="yellow", width=10)
            table.add_column("Compat", justify="center", width=6)
            
            for i, m in enumerate(self.modules, 1):
                compat = "✓" if not m.platforms or self.system in m.platforms else "✗"
                severity_color = "red" if m.severity == HardeningSeverity.CRITICAL else "yellow"
                table.add_row(str(i), m.name[:32], m.category.value[:18], f"[{severity_color}]{m.severity.value[0]}[/{severity_color}]", compat)
            
            console.print(table)
        else:
            print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}AVAILABLE HARDENING MODULES{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
            for i, m in enumerate(self.modules, 1):
                compat = "✓" if not m.platforms or self.system in m.platforms else "✗"
                print(f"{i:2d}. {m.name[:40]:40s} [{m.severity.value}] [{compat}]")
    
    def show_status_cinematic(self):
        """Show status in cinematic layout"""
        if RICH_AVAILABLE:
            console = Console()
            layout = self._create_tactical_layout()
            if layout:
                layout["header"].update(Panel("[bold green]DSTERMINAL HARDENING STATUS[/bold green]", border_style="green"))
                layout["panel1"].update(self._get_system_metrics_panel())
                layout["panel2"].update(self._get_hardening_ops_panel())
                layout["panel3"].update(self._get_network_defense_panel())
                layout["panel4"].update(self._get_threat_feed_panel())
                console.print(layout)
            else:
                self._show_status_fallback()
        else:
            self._show_status_fallback()
    
    def _show_status_fallback(self):
        """Fallback status display"""
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}HARDENING STATUS{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"System: {self.system} | Admin: {self.is_admin_user}")
        print(f"Modules: {len(self.modules)} | Selected: {len(self.selected_modules)}")
        print(f"Executed: {len(self.results)} | Success: {sum(1 for r in self.results if r.success)}")
    
    def run_cinematic(self):
        """Main cinematic dashboard with visible menu"""
        if not RICH_AVAILABLE:
            print(f"{Fore.YELLOW}[!] Rich library not available. Using fallback mode.{Style.RESET_ALL}")
            self.run()
            return
        
        console = Console()
        
        # Try to clear, but handle errors gracefully
        try:
            console.clear()
        except Exception:
            # If clear fails, just print some newlines to create space
            print("\n" * 3)
        
        while True:
            try:
                console.clear()
            except Exception:
                # If clear fails, print newlines
                print("\n" * 3)
            
            try:
                # Header
                header = Panel(
                    "[bold cyan]DSTERMINAL HARDENING DASHBOARD v3.0[/bold cyan]\n"
                    f"[dim]Enterprise Security Suite | Session: {self.session_id}[/dim]",
                    border_style="cyan"
                )
                console.print(header)
                
                # Create a table for metrics
                metrics_table = Table(title="[bold green]SYSTEM STATUS[/bold green]", box=box.HEAVY_EDGE)
                metrics_table.add_column("Metric", style="cyan", width=15)
                metrics_table.add_column("Value", style="white", width=20)
                
                metrics = self.telemetry.get_metrics()
                metrics_table.add_row("CPU", f"{metrics['cpu']:.1f}%")
                metrics_table.add_row("RAM", f"{metrics['ram']:.1f}%")
                metrics_table.add_row("Processes", str(metrics['processes']))
                metrics_table.add_row("Platform", self.system)
                metrics_table.add_row("Admin", "✓" if self.is_admin_user else "✗")
                metrics_table.add_row("Selected Modules", str(len(self.selected_modules)))
                
                console.print(metrics_table)
                
                # Hardening progress table
                progress_table = Table(title="[bold yellow]HARDENING PROGRESS[/bold yellow]", box=box.HEAVY_EDGE)
                progress_table.add_column("Pillar", style="cyan", width=30)
                progress_table.add_column("Progress", style="green", width=40)
                progress_table.add_column("Status", style="white", width=15)
                
                for pillar in self.modules[:8]:
                    status = "✅" if pillar.applied else "⏳"
                    progress_table.add_row(pillar.name[:28], "[green]Pending[/green]", status)
                
                console.print(progress_table)
                
                # ============================================================
                # VISIBLE MENU - Using ASCII box drawing characters (compatible)
                # ============================================================
                menu_panel = Panel(
                    """
        [bold yellow]+-------------------------------------------------------------+
        |                         M E N U   O P T I O N S                         |
        +-----------------------------------------------------------------+
        |                                                                  |
        |   [bold green][1][/bold green]  Select Modules      - Choose hardening modules        |
        |   [bold green][2][/bold green]  View Selected       - Show current selection         |
        |   [bold green][3][/bold green]  Execute Hardening   - Run hardening now              |
        |   [bold green][4][/bold green]  View Results        - Show execution results         |
        |   [bold green][5][/bold green]  Generate Report     - Create audit report            |
        |   [bold yellow][6][/bold yellow]  Rollback Changes    - Revert hardening              |
        |   [bold cyan][7][/bold cyan]  List All Modules     - Display all modules            |
        |   [bold cyan][8][/bold cyan]  Show Status          - Current system status          |
        |   [bold red][9][/bold red]  Exit Dashboard        - Return to terminal             |
        |                                                                  |
        +-----------------------------------------------------------------+
                    """,
                    title="[bold cyan]MAIN MENU[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
                
                console.print(menu_panel)
                
                # Footer
                footer = Panel(
                    "[dim]Type the number (1-9) and press Enter to select an option[/dim]",
                    border_style="dim"
                )
                console.print(footer)
                
                # Get user input
                choice = console.input("\n[bold cyan][ SELECT OPTION ] >> [/bold cyan]").strip()
                
                if choice == '1':
                    self._select_modules_interactive()
                elif choice == '2':
                    self._view_selected_modules()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '3':
                    if not self.selected_modules:
                        console.print("[red]No modules selected! Please select modules first (option 1)[/red]")
                        console.input("\n[dim]Press Enter to continue...[/dim]")
                    else:
                        self._execute_hardening_realtime()
                        console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '4':
                    self._view_results()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '5':
                    self._generate_report()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '6':
                    self._rollback_hardening()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '7':
                    self.list_modules_cinematic()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '8':
                    self.show_status_cinematic()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '9':
                    console.print("\n[bold green]Exiting dashboard...[/bold green]")
                    break
                else:
                    console.print("[red]Invalid option! Please enter a number between 1 and 9[/red]")
                    time.sleep(1.5)
                    
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Exiting dashboard...[/bold yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                console.print("[dim]Press Enter to continue...[/dim]")
                try:
                    input()
                except:
                    pass
                  
    def run(self):
        """Legacy run method for fallback"""
        try:
            while True:
                self._clear_screen()
                self._display_header()
                
                menu = f"""
{Fore.CYAN}[1]{Fore.RESET} Select Modules
{Fore.CYAN}[2]{Fore.RESET} View Selected
{Fore.CYAN}[3]{Fore.RESET} Execute Hardening
{Fore.CYAN}[4]{Fore.RESET} View Results
{Fore.CYAN}[5]{Fore.RESET} Generate Report
{Fore.CYAN}[6]{Fore.RESET} Rollback
{Fore.CYAN}[7]{Fore.RESET} List Modules
{Fore.CYAN}[8]{Fore.RESET} Status
{Fore.CYAN}[9]{Fore.RESET} Exit
"""
                print(menu)
                choice = input(f"\n{Fore.CYAN}Select: {Fore.RESET}").strip()
                
                if choice == '1':
                    self._select_modules_interactive()
                elif choice == '2':
                    self._view_selected_modules()
                    input("\nPress Enter...")
                elif choice == '3':
                    self._execute_hardening_realtime()
                    input("\nPress Enter...")
                elif choice == '4':
                    self._view_results()
                    input("\nPress Enter...")
                elif choice == '5':
                    self._generate_report()
                    input("\nPress Enter...")
                elif choice == '6':
                    self._rollback_hardening()
                    input("\nPress Enter...")
                elif choice == '7':
                    self.list_modules_cinematic()
                    input("\nPress Enter...")
                elif choice == '8':
                    self.show_status_cinematic()
                    input("\nPress Enter...")
                elif choice == '9':
                    break
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted{Fore.RESET}")
        finally:
            self.telemetry.stop()
    
    # ============================================================
    # LEGACY METHODS FOR COMPATIBILITY
    # ============================================================
    
    def _select_modules_interactive(self):
        """Interactive module selection"""
        self._clear_screen()
        self._display_header()
        
        categories = {}
        for module in self.modules:
            cat = module.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(module)
        
        print(f"\n{Fore.CYAN}{'='*self.terminal_width}")
        print(self._center_text("MODULE SELECTION"))
        print(f"{'='*self.terminal_width}{Fore.RESET}\n")
        
        idx = 1
        for category, mods in categories.items():
            print(f"\n{Fore.YELLOW}▶ {category}{Fore.RESET}")
            print(f"{Fore.WHITE}{'─'*50}{Fore.RESET}")
            for m in mods:
                selected = "✓" if m.id in self.selected_modules else "○"
                severity_color = Fore.RED if m.severity == HardeningSeverity.CRITICAL else Fore.YELLOW
                print(f"  [{selected}] {Fore.GREEN}{idx:2d}{Fore.RESET}. {m.name:40s} [{severity_color}{m.severity.value}{Fore.RESET}]")
                idx += 1
        
        print(f"\n{Fore.CYAN}Commands: all, clear, back, or numbers (e.g., 1,3,5-8){Fore.RESET}")
        choice = input(f"\n{Fore.GREEN}Selection:{Fore.RESET} ").strip().lower()
        
        if choice == 'all':
            self.selected_modules = [m.id for m in self.modules if not (m.requires_admin and not self.is_admin_user)]
        elif choice == 'clear':
            self.selected_modules = []
        elif choice != 'back':
            try:
                indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if '-' in part:
                        s, e = part.split('-')
                        indices.extend(range(int(s), int(e) + 1))
                    else:
                        indices.append(int(part))
                for i in indices:
                    if 1 <= i <= len(self.modules):
                        m = self.modules[i - 1]
                        if m.id not in self.selected_modules:
                            self.selected_modules.append(m.id)
            except:
                print(f"{Fore.RED}Invalid selection{Fore.RESET}")
    
    def _view_selected_modules(self):
        self._clear_screen()
        self._display_header()
        
        if not self.selected_modules:
            print(f"{Fore.YELLOW}No modules selected{Fore.RESET}")
        else:
            selected = [m for m in self.modules if m.id in self.selected_modules]
            for i, m in enumerate(selected, 1):
                status = f"{Fore.GREEN}✓{Fore.RESET}" if m.applied else f"{Fore.YELLOW}○{Fore.RESET}"
                print(f"  {status} {i:2d}. {m.name}")
    
    def _view_results(self):
        self._clear_screen()
        self._display_header()
        
        if not self.results:
            print(f"{Fore.YELLOW}No results{Fore.RESET}")
        else:
            for i, r in enumerate(self.results, 1):
                status = f"{Fore.GREEN}✓{Fore.RESET}" if r.success else f"{Fore.RED}✗{Fore.RESET}"
                duration = (r.end_time - r.start_time).total_seconds() if r.end_time else 0
                print(f"  {status} {i:2d}. {r.module.name} [{duration:.1f}s]")
                if r.error:
                    print(f"      {Fore.RED}Error: {r.error}{Fore.RESET}")
    
    def _display_header(self):
        header = f"""
{Fore.GREEN}{'='*self.terminal_width}
{self._center_text('DSTERMINAL HARDENING DASHBOARD v3.0')}
{self._center_text('Enterprise Security Suite')}
{'='*self.terminal_width}{Fore.RESET}
{Fore.YELLOW}System: {self.system} | Admin: {self.is_admin_user} | Session: {self.session_id[-8:]}{Fore.RESET}
"""
        print(header)
    
    def _center_text(self, text: str) -> str:
        return text.center(self.terminal_width)
    
    def _clear_screen(self):
        os.system('cls' if self.system == 'Windows' else 'clear')
    
    def stop(self):
        """Stop all background threads"""
        self.telemetry.stop()


# ============================================================
# MAIN EXECUTION - FIXED
# ============================================================

if __name__ == "__main__":
    try:
        dashboard = HardeningDashboard()
        
        # Check if running interactively or with arguments
        if len(sys.argv) > 1:
            # Command line mode
            import argparse
            parser = argparse.ArgumentParser(description='Hardening Dashboard')
            parser.add_argument('--quick', action='store_true', help='Run quick hardening')
            parser.add_argument('--full', action='store_true', help='Run full hardening')
            parser.add_argument('--list', action='store_true', help='List modules')
            args = parser.parse_args()
            
            if args.list:
                dashboard.list_modules_cinematic()
            elif args.quick:
                dashboard.execute_quick_harden()
            elif args.full:
                dashboard.execute_full_harden()
            else:
                # No args - show help
                print("Usage: python hardening_dashboard.py [--quick] [--full] [--list]")
        else:
            # Interactive mode - use the dashboard
            if RICH_AVAILABLE:
                dashboard.run_cinematic()
            else:
                print(f"{Fore.YELLOW}Rich library not available. Install with: pip install rich{Fore.RESET}")
                dashboard.run()
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
        # Don't exit immediately - allow cleanup
        try:
            time.sleep(0.5)
        except:
            pass
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        # Pause before exit so user can see error
        try:
            input("Press Enter to exit...")
        except:
            pass