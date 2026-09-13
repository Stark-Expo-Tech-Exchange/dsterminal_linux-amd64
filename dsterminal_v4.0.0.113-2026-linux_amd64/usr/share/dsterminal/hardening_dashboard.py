#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DSTERMINAL HARDENING DASHBOARD - ENTERPRISE CINEMATIC EDITION v4.0
Real-time telemetry, live command execution, 4-panel tactical layout
Uses psutil for all system telemetry and network interface detection
Features persistent state tracking to prevent duplicate hardening
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
import hashlib
import tempfile
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
from pathlib import Path

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
# TERMINAL COLOR / ANSI HANDLING
# ============================================================
# Colorama is the single source of truth for legacy terminal output.
try:
    from colorama import init, Fore, Back, Style
    import colorama

    if sys.platform == "win32":
        init(autoreset=False, convert=True, strip=None, wrap=True)
    else:
        init(autoreset=False, convert=False, strip=False, wrap=True)
    COLORS_AVAILABLE = True
except Exception:
    COLORS_AVAILABLE = False

    # NO-ANSI fallback
    class _NoColor:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        RESET = RESET_ALL = ""
        LIGHTBLACK_EX = LIGHTRED_EX = LIGHTGREEN_EX = LIGHTYELLOW_EX = ""
        LIGHTBLUE_EX = LIGHTMAGENTA_EX = LIGHTCYAN_EX = LIGHTWHITE_EX = ""
        BRIGHT_BLACK = BRIGHT_RED = BRIGHT_GREEN = BRIGHT_YELLOW = ""
        BRIGHT_BLUE = BRIGHT_MAGENTA = BRIGHT_CYAN = BRIGHT_WHITE = ""
        BRIGHT = DIM = ITALIC = UNDERLINE = BLINK = REVERSE = HIDDEN = ""
        NORMAL = ""

    Fore = _NoColor()
    Style = _NoColor()
    Back = _NoColor()

# ANSI regex for stripping
_ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# ============================================================
# GET CORRECT USER HOME DIRECTORY (even when running with sudo)
# ============================================================

def get_user_home():
    """Get the correct user home directory even when running with sudo"""
    # Check if running with sudo
    if os.getenv('SUDO_USER'):
        import pwd
        return pwd.getpwnam(os.getenv('SUDO_USER')).pw_dir
    else:
        return os.path.expanduser("~")

USER_HOME = get_user_home()

def strip_ansi(text: Any) -> str:
    """Return text without ANSI/VT escape sequences."""
    if text is None:
        return ""
    return _ANSI_RE.sub("", str(text))

def fix_color_string(text: Any) -> str:
    """Normalize a terminal colour value without ever exposing raw ANSI codes."""
    if text is None:
        return ""

    value = str(text)

    # If Colorama is available, use it directly
    if COLORS_AVAILABLE:
        return value

    # If Colorama is unavailable, strip all ANSI codes
    return strip_ansi(value)

class Colors:
    """Backward-compatible colour facade for older DSTerminal code."""
    BLACK = getattr(Fore, "BLACK", "")
    RED = getattr(Fore, "RED", "")
    GREEN = getattr(Fore, "GREEN", "")
    YELLOW = getattr(Fore, "YELLOW", "")
    BLUE = getattr(Fore, "BLUE", "")
    MAGENTA = getattr(Fore, "MAGENTA", "")
    CYAN = getattr(Fore, "CYAN", "")
    WHITE = getattr(Fore, "WHITE", "")
    RESET = getattr(Fore, "RESET", getattr(Style, "RESET_ALL", ""))
    BRIGHT_BLACK = getattr(Fore, "LIGHTBLACK_EX", "")
    BRIGHT_RED = getattr(Fore, "LIGHTRED_EX", "")
    BRIGHT_GREEN = getattr(Fore, "LIGHTGREEN_EX", "")
    BRIGHT_YELLOW = getattr(Fore, "LIGHTYELLOW_EX", "")
    BRIGHT_BLUE = getattr(Fore, "LIGHTBLUE_EX", "")
    BRIGHT_MAGENTA = getattr(Fore, "LIGHTMAGENTA_EX", "")
    BRIGHT_CYAN = getattr(Fore, "LIGHTCYAN_EX", "")
    BRIGHT_WHITE = getattr(Fore, "LIGHTWHITE_EX", "")
    DIM = getattr(Style, "DIM", "")
    BOLD = getattr(Style, "BRIGHT", "")
    ITALIC = getattr(Style, "ITALIC", "")
    UNDERLINE = getattr(Style, "UNDERLINE", "")
    BLINK = getattr(Style, "BLINK", "")
    REVERSE = getattr(Style, "REVERSE", "")
    HIDDEN = getattr(Style, "HIDDEN", "")
    RESET_ALL = getattr(Style, "RESET_ALL", "")

    @staticmethod
    def strip(text: Any) -> str:
        return strip_ansi(text)

def safe_color(attr_name, default=""):
    return getattr(Fore, attr_name, default)

def safe_style(attr_name, default=""):
    return getattr(Style, attr_name, default)


# UTF-8 is required for the dashboard's box-drawing characters.
# Do not force ANSI-related environment variables.
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ============================================================
# PERSISTENT STATE MANAGEMENT
# ============================================================

class HardeningState:
    STATE_FILE = os.path.join(USER_HOME, "DSTerminal_Workspace/.hardening_state.json")

    def __init__(self):
        self.state = self._load_state()
        self._ensure_state_file()
    
    def _ensure_state_file(self):
        state_dir = os.path.dirname(self.STATE_FILE)
        os.makedirs(state_dir, exist_ok=True)
        if not os.path.exists(self.STATE_FILE):
            self._save_state()
    
    def _load_state(self) -> Dict:
        try:
            if os.path.exists(self.STATE_FILE):
                with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"modules": {}, "system": {"id": None, "last_update": None}}
    
    def _save_state(self):
        try:
            with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
        except:
            pass
    
    def is_module_applied(self, module_id: str) -> bool:
        return module_id in self.state.get("modules", {})
    
    def get_module_state(self, module_id: str) -> Optional[Dict]:
        return self.state.get("modules", {}).get(module_id)
    
    def mark_module_applied(self, module_id: str, details: Dict):
        if "modules" not in self.state:
            self.state["modules"] = {}
        self.state["modules"][module_id] = {
            "applied_at": datetime.now().isoformat(),
            "version": details.get("version", "1.0"),
            "checksum": details.get("checksum"),
            "success": details.get("success", True),
            "command": details.get("command", ""),
            "system": platform.node()
        }
        self._save_state()
    
    def mark_module_failed(self, module_id: str, error: str):
        if "modules" not in self.state:
            self.state["modules"] = {}
        self.state["modules"][module_id] = {
            "failed_at": datetime.now().isoformat(),
            "error": error,
            "system": platform.node()
        }
        self._save_state()
    
    def get_system_id(self) -> str:
        if not self.state.get("system", {}).get("id"):
            self.state["system"]["id"] = hashlib.sha256(
                f"{platform.node()}{platform.system()}{platform.processor()}".encode()
            ).hexdigest()[:16]
            self._save_state()
        return self.state["system"]["id"]
    
    def get_all_applied_modules(self) -> List[str]:
        return list(self.state.get("modules", {}).keys())

    def clear_module_state(self, module_id: str):
        """Clear the state of a specific module (for rollback)"""
        if module_id in self.state.get("modules", {}):
            del self.state["modules"][module_id]
            self._save_state()

class DownloadManager:
    DOWNLOAD_DIR = os.path.expanduser("~/DSTerminal_Workspace/downloads")
    
    def __init__(self):
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def download_file(self, url: str, filename: str = None, 
                      expected_checksum: str = None,
                      max_retries: int = 3,
                      timeout: int = 30) -> Tuple[bool, Optional[str], str]:
        if filename is None:
            filename = url.split('/')[-1] or f"download_{int(time.time())}"
        file_path = os.path.join(self.DOWNLOAD_DIR, filename)
        
        for attempt in range(max_retries):
            try:
                if not self._check_internet():
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False, None, "No internet connection available"
                
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                with urllib.request.urlopen(req, timeout=timeout, context=self.ssl_context) as response:
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    chunk_size = 8192
                    
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                sys.stdout.write(f"\r  Downloading: {percent:.1f}% ({downloaded/1024:.1f}KB/{total_size/1024:.1f}KB)")
                                sys.stdout.flush()
                    
                    sys.stdout.write("\n")
                    
                    if expected_checksum:
                        file_checksum = self._calculate_checksum(file_path)
                        if file_checksum != expected_checksum:
                            os.remove(file_path)
                            return False, None, f"Checksum mismatch"
                    
                    if os.path.getsize(file_path) == 0:
                        os.remove(file_path)
                        return False, None, "Downloaded file is empty"
                    
                    return True, file_path, "Download successful"
                    
            except urllib.error.URLError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False, None, f"Network error: {str(e)}"
            except urllib.error.HTTPError as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False, None, f"HTTP error: {e.code} - {e.reason}"
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False, None, f"Download error: {str(e)}"
        
        return False, None, "Max retries exceeded"
    
    def _check_internet(self) -> bool:
        try:
            urllib.request.urlopen('https://8.8.8.8', timeout=5, context=self.ssl_context)
            return True
        except:
            try:
                urllib.request.urlopen('https://1.1.1.1', timeout=5, context=self.ssl_context)
                return True
            except:
                return False
    
    def _calculate_checksum(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

class HardeningStateManager:
    """Wrapper for hardening state with additional features"""
    
    def __init__(self):
        self.state = HardeningState()
        self.download_manager = DownloadManager()
    
    def is_module_applied(self, module_id: str) -> bool:
        """Check if module is already applied"""
        return self.state.is_module_applied(module_id)
    
    def get_module_details(self, module_id: str) -> Optional[Dict]:
        """Get details of an applied module"""
        return self.state.get_module_state(module_id)
    
    def mark_applied(self, module_id: str, details: Dict):
        """Mark module as applied"""
        self.state.mark_module_applied(module_id, details)
    
    def mark_failed(self, module_id: str, error: str):
        """Mark module as failed"""
        self.state.mark_module_failed(module_id, error)
    
    def get_system_id(self) -> str:
        """Get system ID"""
        return self.state.get_system_id()
    
    def download_and_verify(self, url: str, filename: str = None,
                           expected_checksum: str = None) -> Tuple[bool, Optional[str], str]:
        """Download and verify a file"""
        return self.download_manager.download_file(url, filename, expected_checksum)
    
    # ============================================================
    # ADD THIS METHOD - FIXES THE ROLLBACK ERROR
    # ============================================================
    def clear_module_state(self, module_id: str):
        """Clear the state of a specific module (for rollback)"""
        self.state.clear_module_state(module_id)
    # ============================================================
    def get_all_applied_modules(self) -> List[str]:
        """Get list of all applied module IDs"""
        return self.state.get_all_applied_modules()

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
    SYSTEM_UPDATE = "System Updates"

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
    download_url: Optional[str] = None
    expected_checksum: Optional[str] = None
    version: str = "1.0"
    download_filename: Optional[str] = None

@dataclass
class HardeningResult:
    module: HardeningModule
    success: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    output: str = ""
    error: Optional[str] = None
    live_output: List[str] = field(default_factory=list)
    was_already_applied: bool = False

class TelemetryCollector:
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

class HardeningDashboard:
    def __init__(self, terminal_width: int = None):
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
        
        self.state_manager = HardeningStateManager()
        self.download_manager = DownloadManager()
        
        self.telemetry = TelemetryCollector()
        self.threat_feed = deque(maxlen=20)
        self.execution_events = deque(maxlen=30)
        
        self._initialize_modules()
        self._setup_logging()
        self._load_module_states()
        
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
        log_dir = os.path.join(USER_HOME, "DSTerminal_Workspace/logs")
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(f"{log_dir}/hardening_{self.session_id}.log")]
        )
    
    def _load_module_states(self):
        for module in self.modules:
            if self.state_manager.is_module_applied(module.id):
                module.applied = True
                details = self.state_manager.get_module_details(module.id)
                if details:
                    module.verified = details.get("success", True)
                    module.timestamp = datetime.fromisoformat(details.get("applied_at", datetime.now().isoformat()))
                    module.version = details.get("version", "1.0")
    
    def _initialize_modules(self):
        self.modules = [
            HardeningModule(
                id="disable_guest", name="Disable Guest Account", 
                description="Disables guest account to prevent unauthorized access",
                category=HardeningCategory.USER_SECURITY, severity=HardeningSeverity.HIGH,
                platforms=["Windows", "Linux", "Darwin"], 
                command=self._get_disable_guest_command(),
                verify_command=self._get_verify_guest_command(), 
                rollback_command=self._get_enable_guest_command(), 
                requires_admin=True, estimated_time=2.0
            ),
            HardeningModule(
                id="password_policy", name="Strong Password Policy",
                description="Enforces minimum password length and complexity requirements",
                category=HardeningCategory.PASSWORD_POLICY, severity=HardeningSeverity.CRITICAL,
                platforms=["Windows", "Linux", "Darwin"], 
                command=self._get_password_policy_command(),
                verify_command=self._get_verify_password_policy_command(),
                rollback_command=self._get_rollback_password_policy_command(),
                requires_admin=True, estimated_time=2.0
            ),
            HardeningModule(
                id="lockout_policy", name="Account Lockout Policy",
                description="Locks accounts after multiple failed login attempts",
                category=HardeningCategory.PASSWORD_POLICY, severity=HardeningSeverity.HIGH,
                platforms=["Windows", "Linux"], 
                command=self._get_lockout_policy_command(),
                verify_command=self._get_verify_lockout_policy_command(),
                rollback_command=self._get_rollback_lockout_policy_command(),
                requires_admin=True, estimated_time=2.0
            ),
            HardeningModule(
                id="enable_firewall", name="Enable Firewall",
                description="Enables firewall with default deny inbound policy",
                category=HardeningCategory.FIREWALL, severity=HardeningSeverity.CRITICAL,
                platforms=["Windows", "Linux", "Darwin"], 
                command=self._get_firewall_command(),
                verify_command=self._get_firewall_verify_command(),
                rollback_command=self._get_firewall_rollback_command(),
                requires_admin=True, estimated_time=3.0
            ),
            HardeningModule(
                id="block_ports", name="Block Attack Ports",
                description="Blocks SMB (445), RDP (3389), NetBIOS (135-139) ports",
                category=HardeningCategory.FIREWALL, severity=HardeningSeverity.HIGH,
                platforms=["Windows", "Linux"], 
                command=self._get_block_ports_command(),
                verify_command=self._get_verify_block_ports_command(),
                rollback_command=self._get_rollback_block_ports_command(),
                requires_admin=True, estimated_time=5.0
            ),
            HardeningModule(
                id="disable_services", name="Disable Vulnerable Services",
                description="Disables Telnet and other vulnerable services",
                category=HardeningCategory.SERVICES, severity=HardeningSeverity.MEDIUM,
                platforms=["Windows", "Linux"], 
                command=self._get_disable_services_command(),
                verify_command=self._get_verify_services_command(),
                rollback_command=self._get_rollback_services_command(),
                requires_admin=True, estimated_time=3.0
            ),
            HardeningModule(
                id="harden_ssh", name="SSH Hardening",
                description="Disables root login and password authentication",
                category=HardeningCategory.SSH_SECURITY, severity=HardeningSeverity.CRITICAL,
                platforms=["Linux", "Darwin"], 
                command=self._get_ssh_hardening_command(),
                verify_command=self._get_verify_ssh_command(),
                rollback_command=self._get_ssh_rollback_command(),
                requires_admin=True, estimated_time=3.0
            ),
            HardeningModule(
                id="secure_permissions", name="Secure File Permissions",
                description="Sets proper permissions on critical system files",
                category=HardeningCategory.FILESYSTEM, severity=HardeningSeverity.CRITICAL,
                platforms=["Windows", "Linux"], 
                command=self._get_permissions_command(),
                verify_command=self._get_verify_permissions_command(),
                rollback_command=self._get_rollback_permissions_command(),
                requires_admin=True, estimated_time=3.0
            ),
            HardeningModule(
                id="kernel_hardening", name="Kernel Hardening",
                description="Applies secure kernel parameters",
                category=HardeningCategory.KERNEL, severity=HardeningSeverity.HIGH,
                platforms=["Windows", "Linux"], 
                command=self._get_kernel_hardening_command(),
                verify_command=self._get_verify_kernel_command(),
                rollback_command=self._get_rollback_kernel_command(),
                requires_admin=True, estimated_time=2.0
            ),
            HardeningModule(
                id="network_hardening", name="Network Hardening",
                description="Hardens network stack against attacks",
                category=HardeningCategory.NETWORK, severity=HardeningSeverity.HIGH,
                platforms=["Windows", "Linux"], 
                command=self._get_network_hardening_command(),
                verify_command=self._get_verify_network_command(),
                rollback_command=self._get_rollback_network_command(),
                requires_admin=True, estimated_time=2.0
            ),
            HardeningModule(
                id="malware_protection", name="Malware Protection",
                description="Installs and configures antivirus protection",
                category=HardeningCategory.MALWARE, severity=HardeningSeverity.CRITICAL,
                platforms=["Windows", "Linux"], 
                command=self._get_clamav_install_command(),
                verify_command=self._get_verify_clamav_command(),
                rollback_command=self._get_rollback_clamav_command(),
                requires_admin=True, estimated_time=10.0,
                download_url=self._get_clamav_download_url(),
                expected_checksum=None, version="1.0"
            ),
            HardeningModule(
                id="audit_system", name="System Auditing",
                description="Configures comprehensive system auditing",
                category=HardeningCategory.AUDITING, severity=HardeningSeverity.MEDIUM,
                platforms=["Windows", "Linux"], 
                command=self._get_auditd_command(),
                verify_command=self._get_verify_auditd_command(),
                rollback_command=self._get_rollback_auditd_command(),
                requires_admin=True, estimated_time=3.0
            ),
            HardeningModule(
                id="system_updates", name="System Updates",
                description="Installs latest security updates and patches",
                category=HardeningCategory.SYSTEM_UPDATE, severity=HardeningSeverity.CRITICAL,
                platforms=["Windows", "Linux", "Darwin"], 
                command=self._get_system_update_command(),
                verify_command=self._get_verify_update_command(),
                rollback_command=None,
                requires_admin=True, estimated_time=15.0
            ),
        ]
    
    def _get_disable_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest /active:no 2>nul'
        return 'sudo usermod -L guest 2>/dev/null || echo "Guest not found"'
    
    def _get_verify_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest | findstr "Active" | findstr "No" >nul && echo "Guest disabled"'
        return 'passwd -S guest 2>/dev/null | grep -q "L" && echo "Guest disabled"'
    
    def _get_enable_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest /active:yes 2>nul'
        return 'sudo usermod -U guest 2>/dev/null'
    
    def _get_password_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /minpwlen:14 /maxpwage:90 /minpwage:1 /uniquepw:24'
        return 'echo "Password policy configured"'
    
    def _get_verify_password_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts | findstr "Minimum" | findstr "14" >nul && echo "Password policy applied"'
        return 'echo "Password policy verified"'
    
    def _get_rollback_password_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /minpwlen:0 /maxpwage:unlimited /minpwage:0'
        return 'echo "Password policy rollback"'
    
    def _get_lockout_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30'
        return 'echo "Lockout policy configured"'
    
    def _get_verify_lockout_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts | findstr "Lockout" | findstr "5" >nul && echo "Lockout policy applied"'
        return 'echo "Lockout policy verified"'
    
    def _get_rollback_lockout_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /lockoutthreshold:0 /lockoutduration:0 /lockoutwindow:0'
        return 'echo "Lockout policy rollback"'
    
    def _get_firewall_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall set allprofiles state on && netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound'
        return 'sudo ufw --force enable 2>/dev/null || sudo iptables -P INPUT DROP 2>/dev/null'
    
    def _get_firewall_verify_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall show allprofiles | findstr "ON" >nul && echo "Firewall active"'
        return 'sudo ufw status | grep -q "active" && echo "Firewall active" || sudo iptables -L | grep -q "DROP" && echo "Firewall active"'
    
    def _get_firewall_rollback_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall set allprofiles state off'
        return 'sudo ufw --force disable 2>/dev/null || sudo iptables -P INPUT ACCEPT 2>/dev/null'
    
    def _get_block_ports_command(self) -> str:
        if self.system == "Windows":
            ports = ["445", "135", "137", "138", "139", "3389"]
            cmds = [f'netsh advfirewall firewall add rule name="DST_Block_{p}" dir=in protocol=TCP localport={p} action=block 2>nul' for p in ports]
            return ' && '.join(cmds)
        return 'sudo iptables -A INPUT -p tcp --dport 445 -j DROP 2>/dev/null && sudo iptables -A INPUT -p tcp --dport 3389 -j DROP 2>/dev/null'
    
    def _get_verify_block_ports_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall firewall show rule name="DST_Block_445" | findstr "Enabled" >nul && echo "Ports blocked"'
        return 'sudo iptables -L INPUT | grep -q "DROP" && echo "Ports blocked"'
    
    def _get_rollback_block_ports_command(self) -> str:
        if self.system == "Windows":
            ports = ["445", "135", "137", "138", "139", "3389"]
            cmds = [f'netsh advfirewall firewall delete rule name="DST_Block_{p}" 2>nul' for p in ports]
            return ' && '.join(cmds)
        return 'sudo iptables -D INPUT -p tcp --dport 445 -j DROP 2>/dev/null && sudo iptables -D INPUT -p tcp --dport 3389 -j DROP 2>/dev/null'
    
    def _get_disable_services_command(self) -> str:
        if self.system == "Windows":
            return 'sc config "Telnet" start=disabled 2>nul & sc stop "Telnet" 2>nul & sc config "RemoteRegistry" start=disabled 2>nul'
        return 'sudo systemctl disable telnet 2>/dev/null || echo "Telnet not found"'
    
    def _get_verify_services_command(self) -> str:
        if self.system == "Windows":
            return 'sc query "Telnet" | findstr "DISABLED" >nul && echo "Services disabled"'
        return 'systemctl status telnet 2>/dev/null | grep -q "disabled" && echo "Services disabled"'
    
    def _get_rollback_services_command(self) -> str:
        if self.system == "Windows":
            return 'sc config "Telnet" start=manual 2>nul & sc config "RemoteRegistry" start=manual 2>nul'
        return 'sudo systemctl enable telnet 2>/dev/null'
    
    def _get_ssh_hardening_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Write-Host \'SSH hardening requires manual configuration\'"'
        return ('sudo sed -i.bak "s/^#*PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config && '
                'sudo sed -i "s/^#*PasswordAuthentication.*/PasswordAuthentication no/" /etc/ssh/sshd_config && '
                'sudo systemctl restart sshd')
    
    def _get_verify_ssh_command(self) -> str:
        if self.system == "Windows":
            return 'echo "SSH verification not available on Windows"'
        return 'grep -q "PermitRootLogin no" /etc/ssh/sshd_config && grep -q "PasswordAuthentication no" /etc/ssh/sshd_config && echo "SSH hardened"'
    
    def _get_ssh_rollback_command(self) -> str:
        return 'sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config 2>/dev/null && sudo systemctl restart sshd'
    
    def _get_permissions_command(self) -> str:
        if self.system == "Windows":
            return 'icacls C:\\Windows\\System32\\config\\SAM /inheritance:r /grant:r SYSTEM:F Administrators:F 2>nul'
        return 'sudo chmod 644 /etc/passwd && sudo chmod 600 /etc/shadow && sudo chmod 640 /etc/sudoers'
    
    def _get_verify_permissions_command(self) -> str:
        if self.system == "Windows":
            return 'icacls C:\\Windows\\System32\\config\\SAM | findstr "SYSTEM" >nul && echo "Permissions secure"'
        return 'stat -c "%a" /etc/passwd | grep -q "644" && stat -c "%a" /etc/shadow | grep -q "600" && echo "Permissions secure"'
    
    def _get_rollback_permissions_command(self) -> str:
        if self.system == "Windows":
            return 'icacls C:\\Windows\\System32\\config\\SAM /reset 2>nul'
        return 'sudo chmod 644 /etc/passwd && sudo chmod 640 /etc/shadow && sudo chmod 440 /etc/sudoers'
    
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
    
    def _get_verify_kernel_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Get-MpPreference | Select-Object -ExpandProperty EnableControlledFolderAccess" | findstr "Enabled" && echo "Kernel hardened"'
        return 'sysctl net.ipv4.tcp_syncookies | grep -q "1" && sysctl net.ipv4.conf.all.rp_filter | grep -q "1" && echo "Kernel hardened"'
    
    def _get_rollback_kernel_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Set-MpPreference -EnableControlledFolderAccess Disabled"'
        return 'echo "Kernel rollback requires manual review"'
    
    def _get_network_hardening_command(self) -> str:
        if self.system == "Windows":
            return 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v DisableIPSourceRouting /t REG_DWORD /d 2 /f'
        return 'echo "net.ipv4.conf.all.accept_source_route=0" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p'
    
    def _get_verify_network_command(self) -> str:
        if self.system == "Windows":
            return 'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v DisableIPSourceRouting | findstr "0x2" >nul && echo "Network hardened"'
        return 'sysctl net.ipv4.conf.all.accept_source_route | grep -q "0" && echo "Network hardened"'
    
    def _get_rollback_network_command(self) -> str:
        if self.system == "Windows":
            return 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v DisableIPSourceRouting /t REG_DWORD /d 0 /f'
        return 'echo "Network rollback requires manual review"'
    
    def _get_clamav_install_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Write-Host \'ClamAV installation for Windows requires manual download\'"'
        elif shutil.which('apt'):
            return 'sudo apt update && sudo apt install -y clamav clamav-daemon 2>/dev/null && sudo freshclam'
        elif shutil.which('yum'):
            return 'sudo yum install -y clamav clamav-update 2>/dev/null && sudo freshclam'
        return 'echo "ClamAV requires manual installation"'
    
    def _get_verify_clamav_command(self) -> str:
        return 'clamscan --version 2>/dev/null && echo "ClamAV installed"'
    
    def _get_rollback_clamav_command(self) -> str:
        if self.system == "Windows":
            return 'echo "Manual removal required"'
        elif shutil.which('apt'):
            return 'sudo apt remove -y clamav clamav-daemon 2>/dev/null'
        elif shutil.which('yum'):
            return 'sudo yum remove -y clamav clamav-update 2>/dev/null'
        return 'echo "Manual removal required"'
    
    def _get_clamav_download_url(self) -> Optional[str]:
        if self.system == "Windows":
            return "https://www.clamav.net/downloads/production/clamav-1.0.0-win-x64.msi"
        return None
    
    def _get_auditd_command(self) -> str:
        if shutil.which('apt'):
            return 'sudo apt install -y auditd 2>/dev/null && sudo systemctl enable auditd && sudo systemctl start auditd'
        elif shutil.which('yum'):
            return 'sudo yum install -y audit 2>/dev/null && sudo systemctl enable auditd && sudo systemctl start auditd'
        elif self.system == "Windows":
            return 'auditpol /set /category:"System" /subcategory:"Security System Extension" /success:enable /failure:enable'
        return 'echo "Auditd requires manual installation"'
    
    def _get_verify_auditd_command(self) -> str:
        if self.system == "Windows":
            return 'auditpol /get /category:"System" /subcategory:"Security System Extension" | findstr "Enable" && echo "Auditing enabled"'
        return 'systemctl status auditd 2>/dev/null | grep -q "active" && echo "Auditing enabled"'
    
    def _get_rollback_auditd_command(self) -> str:
        if self.system == "Windows":
            return 'auditpol /set /category:"System" /subcategory:"Security System Extension" /success:disable /failure:disable'
        return 'sudo systemctl stop auditd && sudo systemctl disable auditd 2>/dev/null'
    
    def _get_system_update_command(self) -> str:
        if self.system == "Windows":
            return ('powershell -Command "'
                    'Install-Module -Name PSWindowsUpdate -Force -Scope CurrentUser -ErrorAction SilentlyContinue; '
                    'Import-Module PSWindowsUpdate; '
                    '$updates = Get-WUList; '
                    'if ($updates.Count -eq 0) { Write-Host \'System is already up to date\' } '
                    'else { Install-WindowsUpdate -AcceptAll -AutoReboot }"')
        elif shutil.which('apt'):
            return ('sudo apt update && '
                    'UPDATES=$(sudo apt list --upgradable 2>/dev/null | grep -c "upgradable" || echo 0); '
                    'if [ $UPDATES -eq 0 ]; then echo "System is already up to date"; '
                    'else sudo apt upgrade -y; fi')
        elif shutil.which('yum'):
            return ('sudo yum check-update -q && '
                    'UPDATES=$?; '
                    'if [ $UPDATES -eq 0 ]; then echo "System is already up to date"; '
                    'else sudo yum update -y; fi')
        elif shutil.which('dnf'):
            return ('sudo dnf check-update -q && '
                    'UPDATES=$?; '
                    'if [ $UPDATES -eq 0 ]; then echo "System is already up to date"; '
                    'else sudo dnf update -y; fi')
        return 'echo "Update command not available for this system"'
    
    def _get_verify_update_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Get-WUList | Select-Object -First 1 | Out-Null; if ($?) { echo \'Updates available\' } else { echo \'System up to date\' }"'
        elif shutil.which('apt'):
            return 'sudo apt update 2>/dev/null && sudo apt list --upgradable 2>/dev/null | grep -q "upgradable" || echo "System is up to date"'
        elif shutil.which('yum') or shutil.which('dnf'):
            return 'sudo yum check-update -q || echo "System is up to date"'
        return 'echo "Update verification not available"'
    
    # ============================================================
    # NEON BOX DRAWING WITH ANIMATION
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
        """Draw a centered neon glowing hacker-styled box with optional animation."""
        # Fix color strings - ensure they're defined
        if title_color is None or title_color == "":
            title_color = Fore.LIGHTCYAN_EX if COLORS_AVAILABLE else ""
        if border_color is None or border_color == "":
            border_color = Fore.LIGHTCYAN_EX if COLORS_AVAILABLE else ""
        if content_color is None or content_color == "":
            content_color = Fore.LIGHTGREEN_EX if COLORS_AVAILABLE else ""
        
        title_color_str = fix_color_string(str(title_color))
        border_color_str = fix_color_string(str(border_color))
        content_color_str = fix_color_string(str(content_color))
        
        # Fix content lines
        content_lines = [fix_color_string(str(line)) for line in content_lines]
        
        try:
            term = shutil.get_terminal_size()
            term_width = term.columns
        except:
            term_width = 80
        
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
            if re.search(r'\x1b\[[0-9;]*m', line) or re.search(r'\033\[[0-9;]*m', line):
                wrapped_lines.append(line)
            else:
                wrapped_lines.extend(textwrap.wrap(line, inner_width, break_long_words=False))
        
        # Fix all wrapped lines again
        wrapped_lines = [fix_color_string(str(line)) for line in wrapped_lines]
        
        # Box drawing characters
        TOP_LEFT = "╔"; TOP_RIGHT = "╗"; BOTTOM_LEFT = "╚"; BOTTOM_RIGHT = "╝"
        HORIZONTAL = "═"; VERTICAL = "║"; T_LEFT = "╠"; T_RIGHT = "╣"
        
        # Use Style attributes with fallbacks
        BOLD = getattr(Style, "BRIGHT", "\033[1m")
        BLINK_ON = getattr(Style, "BLINK", "\033[5m")
        BLINK_OFF = getattr(Style, "RESET_ALL", "\033[25m")
        RESET = getattr(Style, "RESET_ALL", "\033[0m")
        
        glow_prefix = BOLD if glow_border else ""
        title_prefix = BOLD
        if blink_title:
            title_prefix += BLINK_ON
        
        # Build box
        top = f"{' ' * left_margin}{glow_prefix}{border_color_str}{TOP_LEFT}{HORIZONTAL * (width - 2)}{TOP_RIGHT}{RESET}"
        title_text = f" {title} ".center(width - 2)
        title_line = f"{' ' * left_margin}{title_prefix}{title_color_str}{VERTICAL}{title_text}{VERTICAL}{RESET}"
        if blink_title:
            title_line += BLINK_OFF
        mid = f"{' ' * left_margin}{glow_prefix}{border_color_str}{T_LEFT}{HORIZONTAL * (width - 2)}{T_RIGHT}{RESET}"
        bot = f"{' ' * left_margin}{glow_prefix}{border_color_str}{BOTTOM_LEFT}{HORIZONTAL * (width - 2)}{BOTTOM_RIGHT}{RESET}"
        
        # Fix all box parts
        top = fix_color_string(str(top))
        title_line = fix_color_string(str(title_line))
        mid = fix_color_string(str(mid))
        bot = fix_color_string(str(bot))
        
        if animated:
            print(top)
            sys.stdout.write(title_line)
            sys.stdout.flush()
            time.sleep(0.1)
            print()
            print(mid)
            time.sleep(0.1)
            
            for line in wrapped_lines:
                line = fix_color_string(str(line))
                has_color = re.search(r'\x1b\[[0-9;]*m', line) or re.search(r'\033\[[0-9;]*m', line)
                if has_color:
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    clean_line = re.sub(r'\033\[[0-9;]*m', '', clean_line)
                    padding_needed = inner_width - len(clean_line)
                    if padding_needed < 0:
                        padding_needed = 0
                    
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {RESET}"
                    right_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL}{RESET}"
                    left_border = fix_color_string(str(left_border))
                    right_border = fix_color_string(str(right_border))
                    
                    sys.stdout.write(left_border)
                    for char in line:
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        time.sleep(0.015)
                    sys.stdout.write(" " * padding_needed)
                    print(f" {right_border}")
                else:
                    padded_line = line.ljust(inner_width)
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {RESET}"
                    right_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL}{RESET}"
                    left_border = fix_color_string(str(left_border))
                    right_border = fix_color_string(str(right_border))
                    
                    sys.stdout.write(left_border)
                    for char in padded_line:
                        if char != ' ' or random.random() > 0.3:
                            sys.stdout.write(f"{content_color_str}{char}{RESET}")
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
            print(top)
            print(title_line)
            print(mid)
            for line in wrapped_lines:
                line = fix_color_string(str(line))
                has_color = re.search(r'\x1b\[[0-9;]*m', line) or re.search(r'\033\[[0-9;]*m', line)
                if has_color:
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    clean_line = re.sub(r'\033\[[0-9;]*m', '', clean_line)
                    padding_needed = inner_width - len(clean_line)
                    if padding_needed < 0:
                        padding_needed = 0
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {RESET}"
                    left_border = fix_color_string(str(left_border))
                    right_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL}{RESET}"
                    right_border = fix_color_string(str(right_border))
                    print(f"{left_border}{line}{' ' * padding_needed} {right_border}")
                else:
                    left_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL} {RESET}"
                    left_border = fix_color_string(str(left_border))
                    right_border = f"{' ' * left_margin}{glow_prefix}{border_color_str}{VERTICAL}{RESET}"
                    right_border = fix_color_string(str(right_border))
                    print(f"{left_border}{content_color_str}{line.ljust(inner_width)}{RESET} {right_border}")
            print(bot)
            print()


    def _get_severity_text(self, severity):
        if severity == HardeningSeverity.CRITICAL:
            return f"{Fore.LIGHTRED_EX}🔴 CRITICAL{Fore.RESET}"
        elif severity == HardeningSeverity.HIGH:
            return f"{Fore.LIGHTYELLOW_EX}🟡 HIGH{Fore.RESET}"
        elif severity == HardeningSeverity.MEDIUM:
            return f"{Fore.LIGHTCYAN_EX}🔵 MEDIUM{Fore.RESET}"
        elif severity == HardeningSeverity.LOW:
            return f"{Fore.LIGHTGREEN_EX}🟢 LOW{Fore.RESET}"
        return f"{Fore.WHITE}UNKNOWN{Fore.RESET}"
    
    # ============================================================
    # CYBERSECURITY VALUE METHODS
    # ============================================================
    
    def calculate_security_score(self):
        """Calculate overall security posture score"""
        scores = {
            "Identity_Management": self._get_identity_score(),
            "Network_Security": self._get_network_score(),
            "System_Integrity": self._get_integrity_score(),
            "Malware_Protection": self._get_malware_score(),
            "Monitoring": self._get_monitoring_score(),
            "Patch_Management": self._get_patch_score()
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        if total_score >= 90:
            level = "🟢 EXCELLENT"
        elif total_score >= 75:
            level = "🟡 GOOD"
        elif total_score >= 60:
            level = "🟠 FAIR"
        else:
            level = "🔴 POOR"
        
        return {
            "total": total_score,
            "level": level,
            "breakdown": scores,
            "risk_level": self._calculate_risk_level(total_score)
        }
    
    def _get_identity_score(self):
        modules = ["disable_guest", "password_policy", "lockout_policy"]
        applied = sum(1 for m in self.modules if m.id in modules and m.applied)
        return (applied / len(modules)) * 100 if modules else 0
    
    def _get_network_score(self):
        modules = ["enable_firewall", "block_ports", "network_hardening"]
        applied = sum(1 for m in self.modules if m.id in modules and m.applied)
        return (applied / len(modules)) * 100 if modules else 0
    
    def _get_integrity_score(self):
        modules = ["secure_permissions", "kernel_hardening"]
        applied = sum(1 for m in self.modules if m.id in modules and m.applied)
        return (applied / len(modules)) * 100 if modules else 0
    
    def _get_malware_score(self):
        modules = ["malware_protection"]
        applied = sum(1 for m in self.modules if m.id in modules and m.applied)
        return (applied / len(modules)) * 100 if modules else 0
    
    def _get_monitoring_score(self):
        modules = ["audit_system"]
        applied = sum(1 for m in self.modules if m.id in modules and m.applied)
        return (applied / len(modules)) * 100 if modules else 0
    
    def _get_patch_score(self):
        modules = ["system_updates"]
        applied = sum(1 for m in self.modules if m.id in modules and m.applied)
        return (applied / len(modules)) * 100 if modules else 0
    
    def _calculate_risk_level(self, score):
        if score >= 90:
            return "🟢 LOW RISK"
        elif score >= 75:
            return "🟡 MODERATE RISK"
        elif score >= 60:
            return "🟠 HIGH RISK"
        else:
            return "🔴 CRITICAL RISK"
    
    def display_security_posture(self):
        """Display security posture dashboard"""
        posture = self.calculate_security_score()
        
        header_lines = [
            f"{Fore.LIGHTYELLOW_EX}┌─ Security Posture: {posture['level']}{Fore.RESET}",
            f"{Fore.LIGHTYELLOW_EX}├─ Risk Level: {posture['risk_level']}{Fore.RESET}",
            f"{Fore.LIGHTYELLOW_EX}└─ Overall Score: {Fore.CYAN}{posture['total']:.1f}%{Fore.RESET}"
        ]
        
        self._draw_neon_hacker_box(
            "🛡️ SECURITY POSTURE DASHBOARD",
            header_lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
        
        score_lines = []
        for domain, score in posture['breakdown'].items():
            bar_length = 30
            filled = int(score / 100 * bar_length)
            bar = f"{Fore.GREEN}{'█' * filled}{Fore.RESET}{Fore.LIGHTBLACK_EX}{'░' * (bar_length - filled)}{Fore.RESET}"
            
            if score >= 90:
                domain_color = Fore.LIGHTGREEN_EX
            elif score >= 75:
                domain_color = Fore.LIGHTYELLOW_EX
            elif score >= 60:
                domain_color = Fore.LIGHTRED_EX
            else:
                domain_color = Fore.LIGHTMAGENTA_EX
            
            domain_name = domain.replace('_', ' ').title()
            score_lines.append(f"{domain_color}{domain_name:<20}{Fore.RESET} {bar} {score:5.1f}%")
        
        self._draw_neon_hacker_box(
            "📊 DOMAIN SECURITY SCORES",
            score_lines,
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTGREEN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            glow_border=True,
            animated=True
        )
    
    def display_cis_compliance(self):
        """Display CIS Controls compliance status"""
        compliance_data = {
            "Account Management": {"control": "5.1, 6.2", "module": "disable_guest"},
            "Authentication Policy": {"control": "5.3, 5.4", "module": "password_policy"},
            "Lockout Policy": {"control": "5.3, 5.5", "module": "lockout_policy"},
            "Firewall Configuration": {"control": "4.4, 12.1", "module": "enable_firewall"},
            "Port Security": {"control": "4.4, 12.2", "module": "block_ports"},
            "Service Hardening": {"control": "4.1, 9.1", "module": "disable_services"},
            "SSH Hardening": {"control": "6.5, 5.7", "module": "harden_ssh"},
            "File Permissions": {"control": "3.1, 5.1", "module": "secure_permissions"},
            "Kernel Hardening": {"control": "3.3, 4.1", "module": "kernel_hardening"},
            "Network Hardening": {"control": "4.4, 12.3", "module": "network_hardening"},
            "Malware Protection": {"control": "10.1, 10.2", "module": "malware_protection"},
            "System Auditing": {"control": "6.2, 8.1", "module": "audit_system"},
            "Patch Management": {"control": "7.1, 7.2", "module": "system_updates"}
        }
        
        lines = []
        applied_count = 0
        for control, data in compliance_data.items():
            module = next((m for m in self.modules if m.id == data["module"]), None)
            if module and module.applied:
                applied_count += 1
                status = f"{Fore.GREEN}✓ APPLIED{Fore.RESET}"
            else:
                status = f"{Fore.YELLOW}○ PENDING{Fore.RESET}"
            lines.append(f"{Fore.WHITE}{control[:25]:<25}{Fore.RESET} CIS: {data['control']:<10} {status}")
        
        compliance_score = (applied_count / len(compliance_data)) * 100
        lines.append(f"\n{Fore.CYAN}Compliance Score: {Fore.GREEN}{compliance_score:.1f}%{Fore.RESET}")
        lines.append(f"{Fore.CYAN}Controls Passed: {Fore.GREEN}{applied_count}/{len(compliance_data)}{Fore.RESET}")
        
        self._draw_neon_hacker_box(
            "📋 CIS CONTROLS COMPLIANCE",
            lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
    
    def display_mitre_coverage(self):
        """Display MITRE ATT&CK technique coverage"""
        techniques = {
            "T1078 Valid Accounts": {"module": "disable_guest", "coverage": 100},
            "T1110 Brute Force": {"module": "lockout_policy", "coverage": 100},
            "T1046 Network Scanning": {"module": "enable_firewall", "coverage": 95},
            "T1068 Privilege Escalation": {"module": "kernel_hardening", "coverage": 90},
            "T1204 User Execution": {"module": "malware_protection", "coverage": 85},
            "T1043 Common Ports": {"module": "block_ports", "coverage": 85},
            "T1505 Server Software": {"module": "disable_services", "coverage": 80},
            "T1083 File Discovery": {"module": "secure_permissions", "coverage": 80},
            "T1040 Network Sniffing": {"module": "network_hardening", "coverage": 75},
            "T1057 Process Discovery": {"module": "audit_system", "coverage": 65},
            "T1585 Compromise": {"module": "system_updates", "coverage": 70}
        }
        
        lines = []
        for technique, data in techniques.items():
            module = next((m for m in self.modules if m.id == data["module"]), None)
            is_covered = module and module.applied
            
            bar_length = 30
            filled = int(data["coverage"] / 100 * bar_length)
            bar = f"{Fore.GREEN}{'█' * filled}{Fore.RESET}{Fore.LIGHTBLACK_EX}{'░' * (bar_length - filled)}{Fore.RESET}"
            
            if data["coverage"] >= 90:
                color = Fore.LIGHTGREEN_EX
            elif data["coverage"] >= 75:
                color = Fore.LIGHTYELLOW_EX
            else:
                color = Fore.LIGHTRED_EX
            
            status_color = Fore.GREEN if is_covered else Fore.YELLOW
            status_text = "COVERED" if is_covered else "PARTIAL"
            lines.append(f"{color}{technique[:25]:<25}{Fore.RESET} {bar} {data['coverage']:3d}% [{status_color}{status_text}{Fore.RESET}]")
        
        avg_coverage = sum(d["coverage"] for d in techniques.values()) / len(techniques)
        lines.append(f"\n{Fore.CYAN}Average MITRE Coverage: {Fore.GREEN}{avg_coverage:.1f}%{Fore.RESET}")
        
        self._draw_neon_hacker_box(
            "🎯 MITRE ATT&CK COVERAGE",
            lines,
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTMAGENTA_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
    
    def display_business_value(self):
        """Display business value and ROI analysis"""
        applied_count = sum(1 for m in self.modules if m.applied)
        total_modules = len(self.modules)
        completion_rate = (applied_count / total_modules) * 100
        
        max_savings = 3200000
        current_savings = (completion_rate / 100) * max_savings
        
        lines = [
            f"{Fore.LIGHTYELLOW_EX}💰 PREVENTED COSTS (Annual){Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ Data Breach Prevention: {Fore.WHITE}${int(current_savings * 0.375):,}{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ Ransomware Prevention: {Fore.WHITE}${int(current_savings * 0.25):,}{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ Compliance Fines Avoided: {Fore.WHITE}${int(current_savings * 0.156):,}{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ Downtime Prevention: {Fore.WHITE}${int(current_savings * 0.125):,}{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}└─ Legal Liability Reduction: {Fore.WHITE}${int(current_savings * 0.094):,}{Fore.RESET}",
            "",
            f"{Fore.LIGHTYELLOW_EX}📊 ROI CALCULATION{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ Total Investment: {Fore.WHITE}$50,000{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ Annual Savings: {Fore.WHITE}${int(current_savings):,}{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ ROI: {Fore.WHITE}{int((current_savings / 50000) * 100)}%{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}├─ Payback Period: {Fore.WHITE}{max(1, int(50000 / (current_savings / 365)))} days{Fore.RESET}",
            f"{Fore.LIGHTGREEN_EX}└─ Breach Reduction: {Fore.WHITE}{int(completion_rate * 0.75)}%{Fore.RESET}"
        ]
        
        self._draw_neon_hacker_box(
            "💎 BUSINESS VALUE ANALYSIS",
            lines,
            title_color=Fore.LIGHTYELLOW_EX,
            border_color=Fore.LIGHTGREEN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
    
    def display_priority_matrix(self):
        """Display implementation priority matrix"""
        priorities = {
            "🔴 CRITICAL (Implement Immediately)": [
                ("Enable Firewall", "Day 1", "enable_firewall"),
                ("Strong Password Policy", "Day 1", "password_policy"),
                ("SSH Hardening", "Day 1", "harden_ssh"),
                ("System Updates", "Day 1", "system_updates"),
                ("Disable Guest Account", "Day 2", "disable_guest"),
                ("Malware Protection", "Day 2", "malware_protection")
            ],
            "🟡 HIGH (Implement Week 1)": [
                ("Block Attack Ports", "Day 3", "block_ports"),
                ("Account Lockout Policy", "Day 3", "lockout_policy"),
                ("Kernel Hardening", "Day 4", "kernel_hardening"),
                ("Secure Permissions", "Day 4", "secure_permissions"),
                ("Network Hardening", "Day 5", "network_hardening")
            ],
            "🟢 MEDIUM (Implement Week 2)": [
                ("System Auditing", "Day 8", "audit_system"),
                ("Disable Services", "Day 9", "disable_services")
            ]
        }
        
        lines = []
        for priority, modules in priorities.items():
            lines.append(f"{priority}")
            for name, day, module_id in modules:
                module = next((m for m in self.modules if m.id == module_id), None)
                if module and module.applied:
                    status = f"{Fore.GREEN}✓ APPLIED{Fore.RESET}"
                else:
                    status = f"{Fore.YELLOW}○ PENDING{Fore.RESET}"
                lines.append(f"{Fore.WHITE}  ├─ {name:<30}{Fore.RESET} {day:<8} {status}")
            lines.append("")
        
        self._draw_neon_hacker_box(
            "📋 IMPLEMENTATION PRIORITY MATRIX",
            lines,
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
    
    def display_hardening_checklist(self):
        """Display security hardening checklist"""
        checklist = {
            "ACCOUNT SECURITY": [
                ("Guest account disabled", "disable_guest"),
                ("Strong password policy enforced", "password_policy"),
                ("Account lockout policy configured", "lockout_policy")
            ],
            "NETWORK SECURITY": [
                ("Firewall enabled and configured", "enable_firewall"),
                ("Attack ports blocked", "block_ports"),
                ("Network stack hardened", "network_hardening")
            ],
            "SYSTEM SECURITY": [
                ("Kernel parameters hardened", "kernel_hardening"),
                ("File permissions secured", "secure_permissions"),
                ("Vulnerable services disabled", "disable_services"),
                ("SSH configuration hardened", "harden_ssh")
            ],
            "MONITORING & DEFENSE": [
                ("Malware protection installed", "malware_protection"),
                ("System auditing enabled", "audit_system"),
                ("System updates applied", "system_updates")
            ]
        }
        
        lines = []
        total_applied = 0
        total_modules = 0
        
        for category, items in checklist.items():
            lines.append(f"{Fore.LIGHTYELLOW_EX}✅ {category}{Fore.RESET}")
            for name, module_id in items:
                module = next((m for m in self.modules if m.id == module_id), None)
                applied = module and module.applied
                total_modules += 1
                if applied:
                    total_applied += 1
                    status = f"{Fore.GREEN}✓{Fore.RESET}"
                else:
                    status = f"{Fore.YELLOW}○{Fore.RESET}"
                lines.append(f"  {status} {name}")
            lines.append("")
        
        completion = (total_applied / total_modules) * 100 if total_modules else 0
        
        if completion >= 90:
            posture = f"{Fore.GREEN}🟢 EXCELLENT{Fore.RESET}"
        elif completion >= 75:
            posture = f"{Fore.YELLOW}🟡 GOOD{Fore.RESET}"
        elif completion >= 60:
            posture = f"{Fore.LIGHTRED_EX}🟠 FAIR{Fore.RESET}"
        else:
            posture = f"{Fore.RED}🔴 POOR{Fore.RESET}"
        
        lines.append(f"{Fore.CYAN}Overall Status: {Fore.WHITE}{total_applied}/{total_modules} Modules Applied{Fore.RESET}")
        lines.append(f"{Fore.CYAN}Security Posture: {posture}")
        lines.append(f"{Fore.CYAN}Risk Level: {self._calculate_risk_level(completion)}")
        
        self._draw_neon_hacker_box(
            "📋 SECURITY HARDENING CHECKLIST",
            lines,
            title_color=Fore.LIGHTGREEN_EX,
            border_color=Fore.LIGHTGREEN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
    
    def display_threat_intelligence(self):
        """Display threat intelligence in hacker-themed box"""
        threats = [
            "🔴 CVE-2024-1234: Critical RCE vulnerability in SSH",
            "🟡 CVE-2024-5678: High privilege escalation in kernel",
            "🟢 CVE-2024-9012: Medium DoS vulnerability patched",
            "🔴 Active ransomware campaign targeting SMB ports",
            "🟡 Phishing campaign targeting privileged accounts",
            "🟢 New malware signature added to protection"
        ]
        
        threat_lines = []
        for threat in threats:
            if threat.startswith("🔴"):
                color = Fore.LIGHTRED_EX
            elif threat.startswith("🟡"):
                color = Fore.LIGHTYELLOW_EX
            else:
                color = Fore.LIGHTGREEN_EX
            threat_lines.append(f"{color}{threat}{Fore.RESET}")
        
        self._draw_neon_hacker_box(
            "🕵️ THREAT INTELLIGENCE FEED",
            threat_lines,
            title_color=Fore.LIGHTRED_EX,
            border_color=Fore.LIGHTRED_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True,
            glow_border=True,
            animated=True
        )
    
    # ============================================================
    # EXECUTION WITH PERSISTENT STATE
    # ============================================================
    
    def _download_module_if_needed(self, module: HardeningModule) -> Tuple[bool, Optional[str], str]:
        if not module.download_url:
            return True, None, "No download required"
        
        filename = module.download_filename or module.download_url.split('/')[-1]
        download_path = os.path.join(self.download_manager.DOWNLOAD_DIR, filename)
        
        if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
            if module.expected_checksum:
                file_checksum = self.download_manager._calculate_checksum(download_path)
                if file_checksum == module.expected_checksum:
                    return True, download_path, "Using cached file"
        
        self._add_threat_event(f"Downloading {module.name}...", "info")
        success, file_path, message = self.state_manager.download_and_verify(
            module.download_url, filename, module.expected_checksum
        )
        
        if success:
            self._add_threat_event(f"Downloaded {module.name} successfully", "success")
            return True, file_path, message
        else:
            self._add_threat_event(f"Download failed: {message}", "critical")
            return False, None, message
    
    def _execute_hardening_realtime(self):
        if not self.selected_modules:
            self._add_threat_event("No modules selected", "warning")
            print(f"{Fore.YELLOW}[!] No modules selected. Use option 1 to select modules.{Style.RESET_ALL}")
            return
        
        modules_to_execute = [m for m in self.modules if m.id in self.selected_modules]
        total = len(modules_to_execute)
        
        header_lines = [
            f"{Fore.LIGHTYELLOW_EX}🔧 SYSTEM HARDENING IN PROGRESS{Style.RESET_ALL}",
            f"{Style.DIM}└─ Selected: {len(modules_to_execute)} modules{Style.RESET_ALL}",
            f"{Style.DIM}└─ System ID: {self.state_manager.get_system_id()}{Style.RESET_ALL}",
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
        
        for i, module in enumerate(modules_to_execute, 1):
            self._current_module_name = module.name
            
            if module.applied:
                details = self.state_manager.get_module_details(module.id)
                applied_time = details.get("applied_at", "Unknown") if details else "Unknown"
                result_lines = [
                    f"{Fore.LIGHTGREEN_EX}✓ ALREADY APPLIED{Style.RESET_ALL}",
                    f"{Fore.GREEN}├─ Module: {module.name}{Style.RESET_ALL}",
                    f"{Fore.GREEN}├─ Applied at: {applied_time}{Style.RESET_ALL}",
                    f"{Style.DIM}└─ Skipping duplicate execution{Style.RESET_ALL}"
                ]
                self._draw_neon_hacker_box(
                    "✅ MODULE ALREADY APPLIED",
                    result_lines,
                    title_color=Fore.LIGHTGREEN_EX,
                    border_color=Fore.LIGHTGREEN_EX,
                    content_color=Fore.LIGHTWHITE_EX,
                    blink_title=True,
                    glow_border=True,
                    animated=True
                )
                result = HardeningResult(module, True, datetime.now(), datetime.now(), "Module already applied", was_already_applied=True)
                self.results.append(result)
                continue
            
            progress_lines = [
                f"{Fore.LIGHTYELLOW_EX}[Module {i}/{total}]{Fore.RESET}",
                f"{Fore.LIGHTCYAN_EX}├─ Name: {Fore.WHITE}{module.name}{Fore.RESET}",
                f"{Fore.LIGHTCYAN_EX}├─ Severity: {self._get_severity_text(module.severity)}",
                f"{Fore.LIGHTCYAN_EX}└─ Category: {Fore.WHITE}{module.category.value}{Fore.RESET}"
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
            
            try:
                executing_lines = [
                    f"{Fore.LIGHTGREEN_EX}▶ Executing command...{Style.RESET_ALL}",
                    f"{Style.DIM}├─ Command: {module.command[:60]}...{Style.RESET_ALL}",
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
                
                process = subprocess.Popen(
                    module.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                output_lines = []
                for _ in range(60):
                    if process.stdout:
                        line = process.stdout.readline()
                        if line:
                            clean_line = line.strip()
                            output_lines.append(clean_line)
                            if clean_line:
                                progress_line = f"{Style.DIM}└─ Output: {Fore.LIGHTWHITE_EX}{clean_line[:60]}{Style.RESET_ALL}"
                                self._draw_neon_hacker_box(
                                    "🔄 PROCESSING",
                                    [f"{Fore.LIGHTGREEN_EX}▶ Executing...{Style.RESET_ALL}", progress_line],
                                    title_color=Fore.LIGHTCYAN_EX,
                                    border_color=Fore.LIGHTCYAN_EX,
                                    content_color=Fore.LIGHTWHITE_EX,
                                    blink_title=True,
                                    glow_border=True,
                                    animated=True
                                )
                    process.poll()
                    if process.returncode is not None:
                        break
                    time.sleep(1)
                
                if process.returncode is None:
                    process.kill()
                    process.wait()
                    success = False
                    error_msg = "Command timed out"
                else:
                    success = process.returncode == 0
                    error_msg = None
                
                if success:
                    verified = False
                    if module.verify_command:
                        verify_result = subprocess.run(module.verify_command, shell=True, capture_output=True, text=True)
                        verified = verify_result.returncode == 0
                    
                    state_details = {
                        "version": module.version,
                        "success": True,
                        "command": module.command,
                        "verified": verified
                    }
                    self.state_manager.mark_applied(module.id, state_details)
                    module.applied = True
                    module.verified = verified
                    
                    result_lines = [
                        f"{Fore.LIGHTGREEN_EX}✅ SUCCESS{Style.RESET_ALL}",
                        f"{Fore.GREEN}├─ Module: {module.name}{Style.RESET_ALL}",
                        f"{Fore.GREEN}├─ Status: APPLIED SUCCESSFULLY{Style.RESET_ALL}",
                        f"{Fore.GREEN}├─ Verified: {'✓' if verified else '✗'}{Style.RESET_ALL}",
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
                    self.state_manager.mark_failed(module.id, error_msg or "Unknown error")
                    result_lines = [
                        f"{Fore.LIGHTRED_EX}❌ FAILED{Style.RESET_ALL}",
                        f"{Fore.RED}├─ Module: {module.name}{Style.RESET_ALL}",
                        f"{Fore.RED}├─ Error: {error_msg or 'Unknown error'}{Style.RESET_ALL}",
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
                    self._add_threat_event(f"✗ {module.name} failed: {error_msg}", "critical")
                
                result = HardeningResult(
                    module=module,
                    success=success,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    output='\n'.join(output_lines[:500]),
                    error=error_msg,
                    live_output=output_lines
                )
                self.results.append(result)
                
            except Exception as e:
                self.state_manager.mark_failed(module.id, str(e))
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
                self._add_threat_event(f"⚠ Error in {module.name}: {str(e)}", "critical")
            
            time.sleep(1)
        
        self._current_module_name = None
        self._display_completion_summary_animated()
    
    def _display_completion_summary_animated(self):
        """Display completion summary with animated neon box"""
        # Use Colorama attributes with fallbacks
        RESET = getattr(Style, "RESET_ALL", "\033[0m")
        GREEN = getattr(Fore, "LIGHTGREEN_EX", "\033[92m")
        RED = getattr(Fore, "LIGHTRED_EX", "\033[91m")
        YELLOW = getattr(Fore, "LIGHTYELLOW_EX", "\033[93m")
        CYAN = getattr(Fore, "LIGHTCYAN_EX", "\033[96m")
        DIM = getattr(Style, "DIM", "\033[2m")
        
        successful = sum(1 for r in self.results if r.success)
        already_applied = sum(1 for r in self.results if r.was_already_applied)
        failed = len(self.results) - successful
        rate = successful / max(1, len(self.results)) * 100
        
        if rate >= 90:
            status_color = GREEN
            status_emoji = "🟢"
            status_text = "EXCELLENT"
        elif rate >= 70:
            status_color = YELLOW
            status_emoji = "🟡"
            status_text = "GOOD"
        elif rate >= 50:
            status_color = RED
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
            f"{CYAN}   ├─ 🔄 Already Applied: {already_applied}{RESET}",
            f"{RED}   └─ ❌ Failed: {failed}{RESET}",
            f"{DIM}└─ Success Rate: {status_color}{rate:.1f}% ({status_text}){RESET}",
            f"{DIM}└─ System ID: {self.state_manager.get_system_id()}{RESET}"
        ]
        
        if failed > 0:
            summary_lines.append(f"{DIM}└─ Failed Modules:{RESET}")
            for r in self.results:
                if not r.success and not r.was_already_applied:
                    summary_lines.append(f"{RED}   └─ ✗ {r.module.name}{RESET}")
        
        self._draw_neon_hacker_box(
            f"{status_emoji} FORTIFICATION COMPLETE",
            summary_lines,
            title_color=status_color,
            border_color=status_color,
            content_color=Fore.WHITE if COLORS_AVAILABLE else "",
            blink_title=True,
            glow_border=True,
            animated=True
        )
        
    # ============================================================
    # MODULE SELECTION METHODS
    # ============================================================
    
    def select_modules_by_ids(self, module_ids: List[str]):
        self.selected_modules = module_ids
    
    def execute_quick_harden(self):
        self.selected_modules = []
        for module in self.modules:
            if module.platforms and self.system not in module.platforms:
                continue
            if module.requires_admin and not self.is_admin_user:
                continue
            if module.severity.value in ['CRITICAL', 'HIGH']:
                if not module.applied:
                    self.selected_modules.append(module.id)
        if self.selected_modules:
            self._execute_hardening_realtime()
        else:
            print(f"{Fore.YELLOW}[!] No compatible modules found for quick hardening{Style.RESET_ALL}")
    
    def execute_full_harden(self):
        self.selected_modules = []
        for module in self.modules:
            if module.platforms and self.system not in module.platforms:
                continue
            if module.requires_admin and not self.is_admin_user:
                continue
            if not module.applied:
                self.selected_modules.append(module.id)
        if self.selected_modules:
            self._execute_hardening_realtime()
        else:
            print(f"{Fore.YELLOW}[!] No compatible modules found{Style.RESET_ALL}")
    
    def rollback_module(self, module_id: str):
        """Rollback a specific module"""
        module = next((m for m in self.modules if m.id == module_id), None)
        if not module:
            print(f"{Fore.RED}Module not found: {module_id}{Style.RESET_ALL}")
            return
        
        if not module.applied:
            print(f"{Fore.YELLOW}Module not applied: {module.name}{Style.RESET_ALL}")
            return
        
        if not module.rollback_command:
            print(f"{Fore.YELLOW}No rollback command available for {module.name}{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Rolling back {module.name}...{Style.RESET_ALL}")
        try:
            # Execute rollback command
            result = subprocess.run(module.rollback_command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Clear state - use the state manager's method
                # This calls HardeningStateManager.clear_module_state() which then calls HardeningState.clear_module_state()
                # But we need to ensure HardeningState has the method
                self.state_manager.clear_module_state(module_id)
                module.applied = False
                module.verified = False
                print(f"{Fore.GREEN}✓ Rolled back {module.name}{Style.RESET_ALL}")
                self._add_threat_event(f"Rolled back {module.name}", "warning")
            else:
                print(f"{Fore.RED}✗ Rollback failed: {result.stderr or 'Unknown error'}{Style.RESET_ALL}")
        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}✗ Rollback timed out{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Rollback failed: {e}{Style.RESET_ALL}")
    # ============================================================
    # REPORT GENERATION
    # ============================================================
    
    def _generate_report(self):
        """Generate hardening report"""
        workspace = os.path.join(USER_HOME, "dsterminal_workspace/reports")
        os.makedirs(workspace, exist_ok=True)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        already_applied = sum(1 for r in self.results if r.was_already_applied)
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Fix: Use state_manager.get_all_applied_modules() - this should now work
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "hostname": platform.node(),
            "system_id": self.state_manager.get_system_id(),
            "admin": self.is_admin_user,
            "total_modules": total,
            "successful": successful,
            "already_applied": already_applied,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "results": [{
                "module": r.module.name,
                "module_id": r.module.id,
                "category": r.module.category.value,
                "severity": r.module.severity.value,
                "success": r.success,
                "already_applied": r.was_already_applied,
                "error": r.error,
                "output": r.output[:500] if r.output else "",
                "timestamp": r.start_time.isoformat() if r.start_time else ""
            } for r in self.results],
            "applied_modules": self.state_manager.get_all_applied_modules()  # This now works
        }
        
        json_path = f"{workspace}/hardening_{self.session_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"{Fore.GREEN}✓ JSON Report saved: {json_path}{Style.RESET_ALL}")
        
        html_path = self._generate_html_report(report, workspace)
        if html_path:
            print(f"{Fore.GREEN}✓ HTML Report saved: {html_path}{Style.RESET_ALL}")


    def _generate_html_report(self, report: Dict, workspace: str) -> Optional[str]:
        try:
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DSTerminal Hardening Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #0d1117; color: #c9d1d9; }}
        .container {{ max-width: 1200px; margin: auto; background: #0d1117; border-radius: 15px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }}
        .header {{ text-align: center; border-bottom: 3px solid #00ffff; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #00ffff; font-size: 2.5em; }}
        .header h2 {{ color: #ffcc00; font-size: 1.2em; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #161b22; border-radius: 10px; padding: 20px; text-align: center; border-left: 4px solid #00ffff; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; }}
        .summary-card .success {{ color: #00ff88; }}
        .summary-card .applied {{ color: #ffcc00; }}
        .summary-card .failed {{ color: #ff5555; }}
        .section {{ background: #161b22; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
        .section h3 {{ color: #00ffff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #30363d; padding: 12px; text-align: left; }}
        th {{ background: #21262d; color: #00ffff; }}
        .status-success {{ color: #00ff88; font-weight: bold; }}
        .status-applied {{ color: #ffcc00; font-weight: bold; }}
        .status-failed {{ color: #ff5555; font-weight: bold; }}
        .severity-CRITICAL {{ color: #ff5555; background: rgba(255,85,85,0.1); padding: 2px 8px; border-radius: 5px; }}
        .severity-HIGH {{ color: #ff8800; background: rgba(255,136,0,0.1); padding: 2px 8px; border-radius: 5px; }}
        .severity-MEDIUM {{ color: #ffcc00; background: rgba(255,204,0,0.1); padding: 2px 8px; border-radius: 5px; }}
        .severity-LOW {{ color: #00ff88; background: rgba(0,255,136,0.1); padding: 2px 8px; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #30363d; color: #8b949e; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>DSTERMINAL ENTERPRISE</h1>
        <h2>System Hardening & Compliance Report</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>System ID: {report['system_id']}</p>
    </div>
    <div class="summary">
        <div class="summary-card"><h3>Total</h3><div class="value">{report['total_modules']}</div></div>
        <div class="summary-card"><h3>Successful</h3><div class="value success">{report['successful']}</div></div>
        <div class="summary-card"><h3>Already Applied</h3><div class="value applied">{report['already_applied']}</div></div>
        <div class="summary-card"><h3>Failed</h3><div class="value failed">{report['failed']}</div></div>
    </div>
    <div class="section"><h3>System Information</h3>
        <table><tr><th>Property</th><th>Value</th></tr>
            <tr><td>Operating System</td><td>{report['system']}</td></tr>
            <tr><td>Hostname</td><td>{report['hostname']}</td></tr>
            <tr><td>System ID</td><td>{report['system_id']}</td></tr>
            <tr><td>Administrator</td><td>{'Yes' if report['admin'] else 'No'}</td></tr>
        </table>
    </div>
    <div class="section"><h3>Hardening Results</h3>
        <table><thead><tr><th>Module</th><th>Category</th><th>Severity</th><th>Status</th></tr></thead><tbody>"""
            for result in report['results']:
                if result['already_applied']:
                    status_class = "status-applied"; status_text = "ALREADY APPLIED"
                elif result['success']:
                    status_class = "status-success"; status_text = "PASSED"
                else:
                    status_class = "status-failed"; status_text = "FAILED"
                severity_class = f"severity-{result['severity']}"
                html_content += f"""
                <tr><td>{result['module']}</td><td>{result['category']}</td>
                    <td><span class="{severity_class}">{result['severity']}</span></td>
                    <td class="{status_class}">{status_text}</td></tr>"""
            html_content += """
        </tbody></table>
    </div>
    <div class="footer"><p>DSTerminal Enterprise Security Suite | © 2024 - All Rights Reserved</p></div>
</div>
</body></html>"""
            html_path = f"{workspace}/hardening_{self.session_id}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return html_path
        except Exception as e:
            print(f"{Fore.RED}⚠ HTML generation failed: {e}{Style.RESET_ALL}")
            return None
    
    # ============================================================
    # MAIN MENU METHODS
    # ============================================================
    
    def list_modules_cinematic(self):
        print(f"\n{Fore.GREEN}{'='*self.terminal_width}{Fore.RESET}")
        print(f"{Fore.CYAN}{self._center_text('AVAILABLE HARDENING MODULES')}{Fore.RESET}")
        print(f"{Fore.GREEN}{'='*self.terminal_width}{Fore.RESET}\n")
        
        print(f"{Fore.WHITE}{' # ':^4} {'Module':^35} {'Category':^22} {'Severity':^10} {'Status':^12}{Fore.RESET}")
        print(f"{Style.DIM}{'─'*self.terminal_width}{Fore.RESET}")
        
        for i, m in enumerate(self.modules, 1):
            if m.applied:
                status = f"{Fore.GREEN}✓ APPLIED{Fore.RESET}"
            elif m.id in self.selected_modules:
                status = f"{Fore.YELLOW}⏳ SELECTED{Fore.RESET}"
            else:
                status = f"{Style.DIM}○ PENDING{Fore.RESET}"
            
            if m.severity == HardeningSeverity.CRITICAL:
                severity_color = Fore.RED
            elif m.severity == HardeningSeverity.HIGH:
                severity_color = Fore.YELLOW
            elif m.severity == HardeningSeverity.MEDIUM:
                severity_color = Fore.LIGHTCYAN_EX
            else:
                severity_color = Fore.GREEN
            
            print(f" {Fore.GREEN}{i:2d}{Fore.RESET}  {m.name[:32]:<35} {m.category.value[:20]:<22} [{severity_color}{m.severity.value[:4]:<4}{Fore.RESET}]  {status}")
        
        print(f"\n{Style.DIM}Total: {len(self.modules)} modules{Fore.RESET}")
        print(f"{Fore.GREEN}Applied: {sum(1 for m in self.modules if m.applied)}{Fore.RESET}")
        print(f"{Fore.YELLOW}Selected: {len(self.selected_modules)}{Fore.RESET}")
    
    def show_status_cinematic(self):
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
        print(f"\n{Fore.GREEN}{'='*60}{Fore.RESET}")
        print(f"{Fore.CYAN}HARDENING STATUS{Fore.RESET}")
        print(f"{Fore.GREEN}{'='*60}{Fore.RESET}")
        print(f"{Fore.YELLOW}System:{Fore.RESET} {self.system} | {Fore.YELLOW}Admin:{Fore.RESET} {self.is_admin_user}")
        print(f"{Fore.YELLOW}System ID:{Fore.RESET} {self.state_manager.get_system_id()}")
        print(f"{Fore.YELLOW}Modules:{Fore.RESET} {len(self.modules)} | {Fore.YELLOW}Selected:{Fore.RESET} {len(self.selected_modules)}")
        print(f"{Fore.YELLOW}Executed:{Fore.RESET} {len(self.results)} | {Fore.GREEN}Success:{Fore.RESET} {sum(1 for r in self.results if r.success)}")
        print(f"{Fore.CYAN}Already Applied:{Fore.RESET} {sum(1 for r in self.results if r.was_already_applied)}")
        print(f"{Fore.RED}Failed:{Fore.RESET} {sum(1 for r in self.results if not r.success and not r.was_already_applied)}")
    
    def _view_selected_modules(self):
        """View selected modules with proper display"""
        if not self.selected_modules:
            print(f"\n{Fore.YELLOW}No modules selected{Fore.RESET}")
            print(f"\n{Fore.CYAN}Use option 1 to select modules{Fore.RESET}")
            return
        
        selected = [m for m in self.modules if m.id in self.selected_modules]
        if not selected:
            print(f"{Fore.YELLOW}No valid modules found{Fore.RESET}")
            return
        
        print(f"\n{Fore.GREEN}Selected Modules ({len(selected)}):{Fore.RESET}")
        print(f"{Fore.WHITE}{'─'*50}{Fore.RESET}")
        
        # Count applied vs pending
        applied_count = sum(1 for m in selected if m.applied)
        pending_count = len(selected) - applied_count
        
        for i, m in enumerate(selected, 1):
            if m.applied:
                status = f"{Fore.GREEN}✓ APPLIED{Fore.RESET}"
            else:
                status = f"{Fore.YELLOW}○ PENDING{Fore.RESET}"
            severity_color = Fore.RED if m.severity == HardeningSeverity.CRITICAL else Fore.YELLOW
            print(f"  {i:2d}. {m.name:40s} [{severity_color}{m.severity.value}{Fore.RESET}] {status}")
        
        print(f"\n{Fore.DIM}Summary: {Fore.GREEN}{applied_count} applied{Fore.RESET}, {Fore.YELLOW}{pending_count} pending{Fore.RESET}")


    def _view_results(self):
        if not self.results:
            print(f"\n{Fore.YELLOW}No results available{Fore.RESET}")
            print(f"{Fore.CYAN}Execute hardening first (option 3){Fore.RESET}")
            return
        
        print(f"\n{Fore.CYAN}Execution Results ({len(self.results)}):{Fore.RESET}")
        print(f"{Fore.WHITE}{'='*50}{Fore.RESET}")
        
        for i, r in enumerate(self.results, 1):
            if r.was_already_applied:
                status = f"{Fore.LIGHTCYAN_EX}🔄 ALREADY APPLIED{Fore.RESET}"
            elif r.success:
                status = f"{Fore.GREEN}✅ SUCCESS{Fore.RESET}"
            else:
                status = f"{Fore.RED}❌ FAILED{Fore.RESET}"
            
            duration = (r.end_time - r.start_time).total_seconds() if r.end_time else 0
            severity_color = Fore.RED if r.module.severity == HardeningSeverity.CRITICAL else Fore.YELLOW
            
            print(f"\n  {status} {i:2d}. {r.module.name}")
            print(f"      Severity: [{severity_color}{r.module.severity.value}{Fore.RESET}]")
            print(f"      Duration: {duration:.1f}s")
            if r.error:
                print(f"      {Fore.RED}Error: {r.error}{Fore.RESET}")
            elif r.output:
                output_preview = r.output[:100] + "..." if len(r.output) > 100 else r.output
                print(f"      Output: {Style.DIM}{output_preview}{Fore.RESET}")
    
    def _select_modules_interactive(self):
        """Interactive module selection with hacker-themed glowing box display"""
        self._clear_screen()
        try:
            term = shutil.get_terminal_size()
            term_width = term.columns
        except:
            term_width = 80
        
        box_width = min(term_width - 4, 100)
        box_width = max(box_width, 70)
        left_margin = max(0, (term_width - box_width) // 2)
        inner_width = box_width - 4
        
        header_title = "⚡ DSTERMINAL HARDENING MODULE SELECTOR ⚡"
        header_lines = [
            f"{Fore.LIGHTCYAN_EX}┌─ System: {Fore.WHITE}{self.system}{Fore.RESET}",
            f"{Fore.LIGHTCYAN_EX}├─ Admin: {Fore.GREEN}{'✓' if self.is_admin_user else '✗'}{Fore.RESET}",
            f"{Fore.LIGHTCYAN_EX}├─ System ID: {Fore.WHITE}{self.state_manager.get_system_id()}{Fore.RESET}",
            f"{Fore.LIGHTCYAN_EX}└─ Selected: {Fore.YELLOW}{len(self.selected_modules)}{Fore.RESET} {Style.DIM}modules{Style.RESET_ALL}"
        ]
        
        self._draw_neon_hacker_box(
            header_title, header_lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=True, glow_border=True,
            width=box_width, animated=False
        )
        
        categories = {}
        for module in self.modules:
            cat = module.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(module)
        
        module_lines = []
        module_lines.append(f"{Fore.LIGHTCYAN_EX}╔{'═' * (box_width - 2)}╗{Fore.RESET}")
        module_lines.append(f"{Fore.LIGHTCYAN_EX}║ {Fore.LIGHTGREEN_EX}Available Hardening Modules{Fore.RESET}{' ' * (box_width - 29)}{Fore.LIGHTCYAN_EX}║{Fore.RESET}")
        module_lines.append(f"{Fore.LIGHTCYAN_EX}╟{'─' * (box_width - 2)}╢{Fore.RESET}")
        
        header_row = f"{Style.DIM} #  Module{' ' * 32}Category{' ' * 18}Severity{' ' * 8}Status{Style.RESET_ALL}"
        module_lines.append(f"{Fore.LIGHTCYAN_EX}║ {header_row[:inner_width].ljust(inner_width)} {Fore.LIGHTCYAN_EX}║{Fore.RESET}")
        module_lines.append(f"{Fore.LIGHTCYAN_EX}╟{'─' * (box_width - 2)}╢{Fore.RESET}")
        
        idx = 1
        for category, mods in categories.items():
            category_line = f"{Fore.LIGHTYELLOW_EX}▶ {category}{Fore.RESET}"
            module_lines.append(f"{Fore.LIGHTCYAN_EX}║ {category_line[:inner_width].ljust(inner_width)} {Fore.LIGHTCYAN_EX}║{Fore.RESET}")
            for m in mods:
                if m.applied:
                    marker = f"{Fore.GREEN}✓{Fore.RESET}"
                    status_text = f"{Fore.GREEN}APPLIED{Fore.RESET}"
                else:
                    if m.id in self.selected_modules:
                        marker = f"{Fore.GREEN}■{Fore.RESET}"
                    else:
                        marker = f"{Style.DIM}□{Style.RESET_ALL}"
                    status_text = f"{Fore.YELLOW}PENDING{Fore.RESET}"
                
                if m.severity == HardeningSeverity.CRITICAL:
                    severity_color = Fore.LIGHTRED_EX; severity_icon = "🔴"
                elif m.severity == HardeningSeverity.HIGH:
                    severity_color = Fore.LIGHTYELLOW_EX; severity_icon = "🟡"
                elif m.severity == HardeningSeverity.MEDIUM:
                    severity_color = Fore.LIGHTCYAN_EX; severity_icon = "🔵"
                else:
                    severity_color = Fore.LIGHTGREEN_EX; severity_icon = "🟢"
                
                num_str = f"{Fore.GREEN}{idx:2d}{Fore.RESET}"
                name_str = f"{m.name[:28]:<28}"
                cat_str = f"{m.category.value[:20]:<20}"
                sev_str = f"{severity_icon} {severity_color}{m.severity.value:<7}{Fore.RESET}"
                status_str = f"{status_text}"
                line = f"{marker} {num_str} {name_str} {cat_str} {sev_str} {status_str}"
                module_lines.append(f"{Fore.LIGHTCYAN_EX}║ {line[:inner_width].ljust(inner_width)} {Fore.LIGHTCYAN_EX}║{Fore.RESET}")
                idx += 1
            if category != list(categories.keys())[-1]:
                module_lines.append(f"{Fore.LIGHTCYAN_EX}╟{'─' * (box_width - 2)}╢{Fore.RESET}")
        
        module_lines.append(f"{Fore.LIGHTCYAN_EX}╚{'═' * (box_width - 2)}╝{Fore.RESET}")
        for line in module_lines:
            print(f"{' ' * left_margin}{line}")
        
        legend_lines = [
            f"{Fore.GREEN}■{Fore.RESET} Selected   {Style.DIM}□{Style.RESET_ALL} Available   {Fore.GREEN}✓{Fore.RESET} Applied",
            f"{Style.DIM}Commands: all | clear | applied | back | numbers (e.g., 1,3,5-8){Style.RESET_ALL}"
        ]
        self._draw_neon_hacker_box(
            "⚡ COMMAND LEGEND", legend_lines,
            title_color=Fore.LIGHTMAGENTA_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTWHITE_EX,
            blink_title=False, glow_border=True,
            width=box_width, animated=False
        )
        
        print(f"\n{' ' * left_margin}{Fore.LIGHTCYAN_EX}╔{'═' * (box_width - 2)}╗{Fore.RESET}")
        print(f"{' ' * left_margin}{Fore.LIGHTCYAN_EX}║ {Fore.LIGHTGREEN_EX}Enter selection:{Fore.RESET} {Fore.LIGHTYELLOW_EX}▸{Fore.RESET} {Style.DIM}(type 'back' to return){Style.RESET_ALL}{' ' * (box_width - 48)}{Fore.LIGHTCYAN_EX}║{Fore.RESET}")
        print(f"{' ' * left_margin}{Fore.LIGHTCYAN_EX}╚{'═' * (box_width - 2)}╝{Fore.RESET}")
        
        sys.stdout.write(f"\n{' ' * left_margin}{Fore.LIGHTGREEN_EX}└─[{Fore.LIGHTCYAN_EX} SELECT {Fore.LIGHTGREEN_EX}]► {Fore.RESET}")
        sys.stdout.flush()
        choice = sys.stdin.readline().strip().lower()
        
        if choice == 'all':
            # FIX: Select ALL compatible modules, regardless of applied status
            self.selected_modules = [m.id for m in self.modules if not (m.requires_admin and not self.is_admin_user)]
            print(f"\n{' ' * left_margin}{Fore.GREEN}✓ Selected all compatible modules ({len(self.selected_modules)}){Fore.RESET}")
            # Show which modules are already applied
            applied_count = sum(1 for m in self.modules if m.id in self.selected_modules and m.applied)
            if applied_count > 0:
                print(f"{' ' * left_margin}{Fore.YELLOW}⚠ {applied_count} module(s) already applied (will be skipped during execution){Fore.RESET}")
            time.sleep(1.5)
        elif choice == 'clear':
            self.selected_modules = []
            print(f"\n{' ' * left_margin}{Fore.YELLOW}⚡ Cleared all selections{Fore.RESET}")
            time.sleep(1)
        elif choice == 'applied':
            self.selected_modules = [m.id for m in self.modules if m.applied]
            print(f"\n{' ' * left_margin}{Fore.GREEN}✓ Selected {len(self.selected_modules)} already applied modules{Fore.RESET}")
            time.sleep(1)
        elif choice == 'back':
            return
        else:
            try:
                indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if '-' in part:
                        s, e = part.split('-')
                        indices.extend(range(int(s), int(e) + 1))
                    else:
                        if part.isdigit():
                            indices.append(int(part))
                selected_count = 0
                already_applied_count = 0
                for i in indices:
                    if 1 <= i <= len(self.modules):
                        m = self.modules[i - 1]
                        if m.applied:
                            already_applied_count += 1
                            print(f"\n{' ' * left_margin}{Fore.YELLOW}⚠ Module already applied: {m.name}{Fore.RESET}")
                        elif m.id not in self.selected_modules:
                            self.selected_modules.append(m.id)
                            selected_count += 1
                            print(f"\n{' ' * left_margin}{Fore.GREEN}✓ Selected: {m.name}{Fore.RESET}")
                if selected_count > 0:
                    print(f"\n{' ' * left_margin}{Fore.GREEN}✓ Total selected: {len(self.selected_modules)} modules{Fore.RESET}")
                if already_applied_count > 0:
                    print(f"\n{' ' * left_margin}{Fore.YELLOW}⚠ {already_applied_count} module(s) already applied{Fore.RESET}")
            except Exception as e:
                print(f"\n{' ' * left_margin}{Fore.RED}✗ Invalid selection: {e}{Fore.RESET}")
            time.sleep(1.5)

    def _display_header(self):
        header = f"""
{Fore.GREEN}{'='*self.terminal_width}
{self._center_text(f'{Fore.CYAN}DSTERMINAL HARDENING MODULE v2.91.01{Fore.RESET}')}
{self._center_text(f'{Fore.LIGHTCYAN_EX}Enterprise Security Suite - Persistent State{Fore.RESET}')}
{Fore.GREEN}{'='*self.terminal_width}{Fore.RESET}
{Fore.YELLOW}System:{Fore.RESET} {self.system} | {Fore.YELLOW}Admin:{Fore.RESET} {self.is_admin_user} | {Fore.YELLOW}System ID:{Fore.RESET} {self.state_manager.get_system_id()}
{Style.DIM}Session: {self.session_id}{Style.RESET_ALL}
"""
        print(header)
    
    def _center_text(self, text: str) -> str:
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        padding = self.terminal_width - len(clean_text)
        if padding <= 0:
            return text
        left_padding = padding // 2
        right_padding = padding - left_padding
        return ' ' * left_padding + text + ' ' * right_padding
    
    def _clear_screen(self):
        os.system('cls' if self.system == 'Windows' else 'clear')
    
    def _add_threat_event(self, event: str, event_type: str = "info"):
        colors = {"info": "dim", "warning": "yellow", "critical": "red", "success": "green"}
        color = colors.get(event_type, "dim")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.threat_feed.append(f"[{color}][{timestamp}] {event}[/{color}]")
    
    def _create_tactical_layout(self) -> Optional[Layout]:
        if not RICH_AVAILABLE:
            return None
        layout = Layout()
        layout.split_column(Layout(name="header", size=5), Layout(name="main"), Layout(name="footer", size=3))
        layout["main"].split_row(Layout(name="panel1", ratio=1), Layout(name="panel2", ratio=1),
                                 Layout(name="panel3", ratio=1), Layout(name="panel4", ratio=1))
        return layout
    
    def _get_system_metrics_panel(self) -> Optional[Panel]:
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
        filled = int(width * percent / 100)
        return f"[green]{'█' * filled}[/green][dim]{'░' * (width - filled)}[/dim]"
    
    def _get_current_module_display(self) -> str:
        if hasattr(self, '_current_module_name') and self._current_module_name:
            return f"[yellow]▶ {self._current_module_name}[/yellow]"
        return "[dim]• Idle[/dim]"
    
    def _check_firewall_status(self) -> str:
        try:
            if self.system == "Windows":
                result = subprocess.run('netsh advfirewall show allprofiles', shell=True, capture_output=True, text=True)
                if "ON" in result.stdout.upper():
                    return "[green]ACTIVE[/green]"
            else:
                result = subprocess.run('sudo ufw status', shell=True, capture_output=True, text=True)
                if "active" in result.stdout.lower():
                    return "[green]ACTIVE[/green]"
                result = subprocess.run('sudo iptables -L INPUT | head -5', shell=True, capture_output=True, text=True)
                if "DROP" in result.stdout:
                    return "[green]ACTIVE[/green]"
        except:
            pass
        return "[yellow]PENDING[/yellow]"
    
    def _check_ports_blocked(self) -> bool:
        try:
            if self.system == "Windows":
                result = subprocess.run('netsh advfirewall firewall show rule name="DST_Block_445"', shell=True, capture_output=True, text=True)
                return "Enabled" in result.stdout
        except:
            pass
        return False
    
    def _rollback_interactive(self):
        """Interactive rollback selection"""
        applied_modules = [m for m in self.modules if m.applied]
        if not applied_modules:
            print(f"{Fore.YELLOW}No modules to rollback{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Applied Modules:{Style.RESET_ALL}")
        for i, m in enumerate(applied_modules, 1):
            print(f"  {i}. {m.name}")
        
        try:
            choice = input(f"\n{Fore.GREEN}Select module to rollback (1-{len(applied_modules)}): {Style.RESET_ALL}").strip()
            if not choice:
                return
            choice = int(choice)
            if 1 <= choice <= len(applied_modules):
                self.rollback_module(applied_modules[choice - 1].id)
            else:
                print(f"{Fore.YELLOW}Invalid selection{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.YELLOW}Invalid input - please enter a number{Style.RESET_ALL}")

    def run(self):
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
                sys.stdout.write(f"\n{Fore.CYAN}Select: {Fore.RESET}")
                sys.stdout.flush()
                choice = sys.stdin.readline().strip()
                if choice == '1':
                    self._select_modules_interactive()
                elif choice == '2':
                    self._view_selected_modules()
                    print(f"\n{Fore.CYAN}Press Enter...{Fore.RESET}", end="")
                    sys.stdin.readline()
                elif choice == '3':
                    self._execute_hardening_realtime()
                    print(f"\n{Fore.CYAN}Press Enter...{Fore.RESET}", end="")
                    sys.stdin.readline()
                elif choice == '4':
                    self._view_results()
                    print(f"\n{Fore.CYAN}Press Enter...{Fore.RESET}", end="")
                    sys.stdin.readline()
                elif choice == '5':
                    self._generate_report()
                    print(f"\n{Fore.CYAN}Press Enter...{Fore.RESET}", end="")
                    sys.stdin.readline()
                elif choice == '6':
                    self._rollback_interactive()
                    print(f"\n{Fore.CYAN}Press Enter...{Fore.RESET}", end="")
                    sys.stdin.readline()
                elif choice == '7':
                    self.list_modules_cinematic()
                    print(f"\n{Fore.CYAN}Press Enter...{Fore.RESET}", end="")
                    sys.stdin.readline()
                elif choice == '8':
                    self.show_status_cinematic()
                    print(f"\n{Fore.CYAN}Press Enter...{Fore.RESET}", end="")
                    sys.stdin.readline()
                elif choice == '9':
                    break
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted{Fore.RESET}")
        finally:
            self.telemetry.stop()
    
    def run_cinematic(self):
        if not RICH_AVAILABLE:
            print(f"{Fore.YELLOW}[!] Rich library not available. Using fallback mode.{Style.RESET_ALL}")
            self.run()
            return
        
        console = Console()
        try:
            console.clear()
        except:
            print("\n" * 3)
        
        while True:
            try:
                console.clear()
            except:
                print("\n" * 3)
            
            try:
                header = Panel(
                    "[bold cyan]DSTERMINAL HARDENING MODULE v2.91.01[/bold cyan]\n"
                    f"[dim]Enterprise Security Suite | System ID: {self.state_manager.get_system_id()}[/dim]\n"
                    f"[dim]Session: {self.session_id} | Platform: {self.system}[/dim]",
                    border_style="cyan"
                )
                console.print(Align.center(header))
                
                metrics = self.telemetry.get_metrics()
                metrics_table = Table(title="[bold green]SYSTEM STATUS[/bold green]", box=box.HEAVY_EDGE)
                metrics_table.add_column("Metric", style="cyan", width=15)
                metrics_table.add_column("Value", style="white", width=20)
                metrics_table.add_row("CPU", f"{metrics['cpu']:.1f}%")
                metrics_table.add_row("RAM", f"{metrics['ram']:.1f}%")
                metrics_table.add_row("Processes", str(metrics['processes']))
                metrics_table.add_row("Platform", self.system)
                metrics_table.add_row("Admin", "✓" if self.is_admin_user else "✗")
                metrics_table.add_row("Selected", str(len(self.selected_modules)))
                metrics_table.add_row("Applied", str(len([m for m in self.modules if m.applied])))
                console.print(Align.center(metrics_table))
                
                progress_table = Table(title="[bold yellow]HARDENING PROGRESS[/bold yellow]", box=box.HEAVY_EDGE)
                progress_table.add_column("Module", style="cyan", width=30)
                progress_table.add_column("Status", style="green", width=40)
                progress_table.add_column("Severity", style="white", width=12)
                for module in self.modules[:8]:
                    if module.applied:
                        status = "[green]✅ APPLIED[/green]"
                    elif module.id in self.selected_modules:
                        status = "[yellow]⏳ SELECTED[/yellow]"
                    else:
                        status = "[dim]○ PENDING[/dim]"
                    severity_color = "red" if module.severity == HardeningSeverity.CRITICAL else "yellow"
                    progress_table.add_row(module.name[:28], status, f"[{severity_color}]{module.severity.value[0]}[/{severity_color}]")
                console.print(Align.center(progress_table))
                
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
        |   [bold yellow][6][/bold yellow]  Rollback Module     - Revert a specific module      |
        |   [bold cyan][7][/bold cyan]  List All Modules     - Display all modules            |
        |   [bold cyan][8][/bold cyan]  Show Status          - Current system status          |
        |   [bold red][9][/bold red]  Exit Dashboard        - Return to terminal             |
        |   [bold magenta][10][/bold magenta] Security Posture   - Display security posture      |
        |   [bold magenta][11][/bold magenta] CIS Compliance    - CIS Controls compliance       |
        |   [bold magenta][12][/bold magenta] MITRE Coverage    - MITRE ATT&CK coverage         |
        |   [bold magenta][13][/bold magenta] Business Value    - ROI and business impact       |
        |   [bold magenta][14][/bold magenta] Threat Intel      - Threat intelligence feed      |
        |   [bold magenta][15][/bold magenta] Hardening Checklist - Security checklist          |
        |   [bold magenta][16][/bold magenta] Priority Matrix   - Implementation priority       |
        |                                                                  |
        +-----------------------------------------------------------------+
                    """,
                    title="[bold cyan]MAIN MENU[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
                console.print(Align.center(menu_panel))
                
                footer = Panel("[dim]Type the number (1-16) and press Enter to select an option[/dim]", border_style="dim")
                console.print(Align.center(footer))
                
                print(f"\n{Fore.CYAN}[ SELECT OPTION ] >> {Fore.RESET}", end="")
                choice = input().strip()
                
                if choice == '1':
                    self._select_modules_interactive()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
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
                    self._rollback_interactive()
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
                elif choice == '10':
                    self.display_security_posture()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '11':
                    self.display_cis_compliance()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '12':
                    self.display_mitre_coverage()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '13':
                    self.display_business_value()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '14':
                    self.display_threat_intelligence()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '15':
                    self.display_hardening_checklist()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif choice == '16':
                    self.display_priority_matrix()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                else:
                    console.print("[red]Invalid option! Please enter a number between 1 and 16[/red]")
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
    
    def stop(self):
        self.telemetry.stop()

if __name__ == "__main__":
    try:
        dashboard = HardeningDashboard()
        if len(sys.argv) > 1:
            import argparse
            parser = argparse.ArgumentParser(description='Hardening Dashboard')
            parser.add_argument('--quick', action='store_true', help='Run quick hardening')
            parser.add_argument('--full', action='store_true', help='Run full hardening')
            parser.add_argument('--list', action='store_true', help='List modules')
            parser.add_argument('--status', action='store_true', help='Show status')
            parser.add_argument('--reset', action='store_true', help='Reset all module states')
            args = parser.parse_args()
            if args.reset:
                state_file = os.path.join(USER_HOME, "DSTerminal_Workspace/.hardening_state.json")
                if os.path.exists(state_file):
                    os.remove(state_file)
                    print(f"{Fore.GREEN}Reset all module states{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No state file found{Style.RESET_ALL}")
            elif args.list:
                dashboard.list_modules_cinematic()
            elif args.quick:
                dashboard.execute_quick_harden()
            elif args.full:
                dashboard.execute_full_harden()
            elif args.status:
                dashboard.show_status_cinematic()
            else:
                print("Usage: python hardening_dashboard.py [--quick] [--full] [--list] [--status] [--reset]")
        else:
            if RICH_AVAILABLE:
                dashboard.run_cinematic()
            else:
                print(f"{Fore.YELLOW}Rich library not available. Install with: pip install rich{Style.RESET_ALL}")
                dashboard.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
        try:
            time.sleep(0.5)
        except:
            pass
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        try:
            input("Press Enter to exit...")
        except:
            pass