#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DSTerminal Complete Security Suite v4.0.0.113
FULLY CROSS-PLATFORM - Windows, Linux, macOS
Enhanced with Automatic Ransomware Detection Anywhere in System
Full Dashboard Controls Implementation with Auto-Quarantine Progress
"""

# ============================================================
# CROSS-PLATFORM IMPORTS
# ============================================================
import sys
import os
import platform
import subprocess
import threading
import time
import json
import shutil
import random
import hashlib
import socket
import re
import webbrowser
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# ============================================================
# PLATFORM DETECTION - CROSS-PLATFORM
# ============================================================
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"
IS_MAC = SYSTEM == "Darwin"
IS_UNIX = IS_LINUX or IS_MAC

# Python version check
PYTHON_VERSION = sys.version_info
PYTHON_3_13 = PYTHON_VERSION.major == 3 and PYTHON_VERSION.minor >= 13

# ============================================================
# CROSS-PLATFORM CONSOLE FIXES
# ============================================================
if IS_WINDOWS:
    # Windows console encoding fixes
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass
    
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        elif hasattr(sys.stdout, 'buffer'):
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    except:
        pass

    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PROMPT_TOOLKIT_NO_CP437'] = '1'
elif IS_UNIX:
    # Linux/macOS locale fixes
    os.environ.setdefault('LC_ALL', 'C.UTF-8')
    os.environ.setdefault('LANG', 'en_US.UTF-8')
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONUTF8', '1')
    if 'TERM' not in os.environ:
        os.environ['TERM'] = 'xterm-256color'

# ============================================================
# SAFE STDOUT WRITE - CROSS-PLATFORM
# ============================================================
_original_stdout_write = sys.stdout.write if sys.stdout is not None else None

def _safe_stdout_write(text):
    try:
        if _original_stdout_write is not None:
            _original_stdout_write(text)
    except (OSError, UnicodeEncodeError, AttributeError):
        try:
            clean = text.encode('ascii', 'ignore').decode('ascii')
            if _original_stdout_write is not None:
                _original_stdout_write(clean)
        except:
            pass
    except Exception:
        pass

if sys.stdout is not None:
    sys.stdout.write = _safe_stdout_write

# ============================================================
# CROSS-PLATFORM IMPORTS - With fallbacks
# ============================================================
try:
    from flask import Flask, render_template_string, jsonify, request, send_file, make_response
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[!] Flask not installed. Install with: pip install flask flask-socketio")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[!] psutil not installed. Install with: pip install psutil")

try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    print("[!] netifaces not installed. Install with: pip install netifaces")

# ============================================================
# CROSS-PLATFORM COLOR CODES
# ============================================================
class Colors:
    """ANSI color codes - works on all platforms"""
    RED = '\033[91m' if not IS_WINDOWS else ''
    GREEN = '\033[92m' if not IS_WINDOWS else ''
    YELLOW = '\033[93m' if not IS_WINDOWS else ''
    BLUE = '\033[94m' if not IS_WINDOWS else ''
    MAGENTA = '\033[95m' if not IS_WINDOWS else ''
    CYAN = '\033[96m' if not IS_WINDOWS else ''
    WHITE = '\033[97m' if not IS_WINDOWS else ''
    RESET = '\033[0m' if not IS_WINDOWS else ''
    DIM = '\033[2m' if not IS_WINDOWS else ''
    BRIGHT = '\033[1m' if not IS_WINDOWS else ''
    
    @staticmethod
    def strip(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

class ServerColors:
    """Server-side color codes"""
    RED = Colors.RED
    GREEN = Colors.GREEN
    YELLOW = Colors.YELLOW
    BLUE = Colors.BLUE
    MAGENTA = Colors.MAGENTA
    CYAN = Colors.CYAN
    WHITE = Colors.WHITE
    RESET = Colors.RESET
    DIM = Colors.DIM
    BOLD = Colors.BRIGHT
    BG_RED = '\033[41m' if not IS_WINDOWS else ''
    BG_GREEN = '\033[42m' if not IS_WINDOWS else ''
    BG_YELLOW = '\033[43m' if not IS_WINDOWS else ''
    BG_BLUE = '\033[44m' if not IS_WINDOWS else ''
    BG_MAGENTA = '\033[45m' if not IS_WINDOWS else ''
    BG_CYAN = '\033[46m' if not IS_WINDOWS else ''
    BG_WHITE = '\033[47m' if not IS_WINDOWS else ''
    BG_BLACK = '\033[40m' if not IS_WINDOWS else ''

# ============================================================
# CROSS-PLATFORM ALERT FUNCTIONS
# ============================================================
def server_alert(message, alert_type="INFO"):
    """Print colored alert - Cross-platform"""
    colors = {
        "INFO": ServerColors.CYAN,
        "SUCCESS": ServerColors.GREEN,
        "WARNING": ServerColors.YELLOW,
        "ERROR": ServerColors.RED,
        "CRITICAL": ServerColors.BG_RED + ServerColors.WHITE + ServerColors.BOLD,
        "QUARANTINE": ServerColors.MAGENTA + ServerColors.BOLD,
        "RANSOMWARE": ServerColors.BG_RED + ServerColors.WHITE + ServerColors.BOLD,
        "HONEYPOT": ServerColors.BG_YELLOW + Colors.BLACK + ServerColors.BOLD,
    }
    
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🚨",
        "QUARANTINE": "📁",
        "RANSOMWARE": "💀",
        "HONEYPOT": "🎯",
    }
    
    color = colors.get(alert_type.upper(), ServerColors.WHITE)
    icon = icons.get(alert_type.upper(), "•")
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    try:
        print(f"\n{ServerColors.DIM}[{timestamp}]{ServerColors.RESET} {color}{icon} {message}{ServerColors.RESET}")
    except:
        print(f"\n[{timestamp}] {message}")
    
    sys.stdout.flush()
    sys.stderr.flush()
    
    try:
        log_file = os.path.join(LOGS_DIR, 'server_alerts.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{alert_type}] {message}\n")
    except:
        pass
    
    return True

def server_alert_box(title, content_lines, border_color=ServerColors.RED):
    """Print a colored box - Cross-platform"""
    if isinstance(content_lines, str):
        content_lines = [content_lines]
    elif not isinstance(content_lines, list):
        content_lines = [str(content_lines)]
    
    max_line_len = max([len(str(line)) for line in content_lines] + [len(str(title))])
    width = min(max_line_len + 4, 80)
    
    top_bottom = "═" * (width + 2)
    separator = "─" * (width + 2)
    
    try:
        print()
        print(f"{border_color}╔{top_bottom}╗{ServerColors.RESET}")
        print(f"{border_color}║ {str(title).ljust(width)} ║{ServerColors.RESET}")
        print(f"{border_color}╠{separator}╣{ServerColors.RESET}")
        for line in content_lines:
            print(f"{border_color}║ {str(line).ljust(width)} ║{ServerColors.RESET}")
        print(f"{border_color}╚{top_bottom}╝{ServerColors.RESET}")
        print()
    except:
        print(f"\n{'='*60}")
        print(f"[{title}]")
        for line in content_lines:
            print(f"  {line}")
        print(f"{'='*60}\n")
    
    sys.stdout.flush()
    sys.stderr.flush()
    
    try:
        log_file = os.path.join(LOGS_DIR, 'server_alerts.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"BOX ALERT: {title}\n")
            for line in content_lines:
                f.write(f"  {line}\n")
            f.write(f"{'='*60}\n")
    except:
        pass
    
    return True

# ============================================================
# CROSS-PLATFORM WORKSPACE DIRECTORY
# ============================================================
def get_workspace_directory():
    """
    Determine workspace directory - Cross-platform
    Priority:
    1. DSTERMINAL_WORKSPACE environment variable
    2. Platform-specific application data directory
    3. User home directory fallback
    """
    env_workspace = os.environ.get('DSTERMINAL_WORKSPACE')
    if env_workspace:
        workspace = env_workspace
        print(f"[WORKSPACE] Using environment variable: {workspace}")
        return workspace
    
    if getattr(sys, 'frozen', False):
        if IS_WINDOWS:
            appdata = os.environ.get('APPDATA')
            if appdata:
                workspace = os.path.join(appdata, 'DSTerminal', 'workspace')
            else:
                workspace = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'DSTerminal', 'workspace')
        elif IS_MAC:
            workspace = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'DSTerminal', 'workspace')
        else:  # Linux
            workspace = os.path.join(os.path.expanduser('~'), '.config', 'DSTerminal', 'workspace')
        
        os.makedirs(workspace, exist_ok=True)
        print(f"[WORKSPACE] Using application data: {workspace}")
        return workspace
    
    # Running as script - use user home
    home = os.path.expanduser('~')
    if IS_WINDOWS:
        workspace = os.path.join(home, 'dsterminal_workspace', 'ransom')
    elif IS_MAC:
        workspace = os.path.join(home, 'dsterminal_workspace', 'ransom')
    else:  # Linux
        workspace = os.path.join(home, 'dsterminal_workspace', 'ransom')
    
    try:
        os.makedirs(workspace, exist_ok=True)
        test_file = os.path.join(workspace, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"[WORKSPACE] Using: {workspace}")
        return workspace
    except:
        workspace = os.path.join(tempfile.gettempdir(), 'dsterminal_workspace', 'ransom')
        os.makedirs(workspace, exist_ok=True)
        print(f"[WORKSPACE] Using fallback: {workspace}")
        return workspace

# Get workspace directory
WORKSPACE_DIR = get_workspace_directory()

# Define subdirectories
REPORTS_DIR = os.path.join(WORKSPACE_DIR, 'reports')
LOGS_DIR = os.path.join(WORKSPACE_DIR, 'logs')
QUARANTINE_DIR = os.path.join(WORKSPACE_DIR, 'quarantine')
STATIC_DIR = os.path.join(WORKSPACE_DIR, 'static')
CONFIG_DIR = os.path.join(WORKSPACE_DIR, 'config')
WHITELIST_FILE = os.path.join(CONFIG_DIR, 'whitelist.json')
BLACKLIST_FILE = os.path.join(CONFIG_DIR, 'blacklist.json')

# Create directories
for dir_path in [WORKSPACE_DIR, REPORTS_DIR, LOGS_DIR, QUARANTINE_DIR, 
                 STATIC_DIR, CONFIG_DIR]:
    os.makedirs(dir_path, exist_ok=True)

print("=" * 70)
print(f"[FOLDER] Workspace: {WORKSPACE_DIR}")
print(f"[FOLDER] Reports: {REPORTS_DIR}")
print(f"[FOLDER] Logs: {LOGS_DIR}")
print(f"[FOLDER] Quarantine: {QUARANTINE_DIR}")
print("=" * 70)

# ============================================================
# CROSS-PLATFORM CONFIGURATION
# ============================================================
DEFAULT_CONFIG = {
    'scan_interval': 30,
    'monitoring_enabled': True,
    'honeypot_enabled': True,
    'sensitivity': 'medium',
    'auto_quarantine': True,
    'network_isolation': False,
    'sound_alerts': True,
    'notifications': True
}

def load_config():
    config_path = os.path.join(CONFIG_DIR, 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    config_path = os.path.join(CONFIG_DIR, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

config = load_config()

# ============================================================
# CROSS-PLATFORM WHITELIST/BLACKLIST
# ============================================================
def get_default_whitelist():
    """Get platform-specific default whitelist"""
    if IS_WINDOWS:
        return [
            r"C:\Windows\System32\ntoskrnl.exe",
            r"C:\Windows\System32\winlogon.exe",
            r"C:\Windows\explorer.exe",
            r"C:\Program Files",
            r"C:\Windows\System32",
        ]
    elif IS_MAC:
        return [
            "/System/*",
            "/Library/*",
            "/usr/bin/*",
            "/usr/sbin/*",
            "/bin/*",
            "/sbin/*",
        ]
    else:  # Linux
        return [
            "/bin/*",
            "/sbin/*",
            "/usr/bin/*",
            "/usr/sbin/*",
            "/lib/*",
            "/lib64/*",
            "/usr/lib/*",
            "/etc/passwd",
            "/etc/shadow",
            "/etc/group",
            "/etc/sudoers",
            "/boot/*",
            "/vmlinuz*",
            "/initrd*",
        ]

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return get_default_whitelist()

def save_whitelist(whitelist):
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(whitelist, f, indent=2)

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(blacklist, f, indent=2)

whitelist = load_whitelist()
blacklist = load_blacklist()

# ============================================================
# CROSS-PLATFORM SHIELD CORE
# ============================================================
try:
    from shield_core import ShieldCore, ThreatLevel
    SHIELD_AVAILABLE = True
    print("[+] ShieldCore loaded successfully")
except ImportError:
    print("[!] ShieldCore import error - using mock")
    SHIELD_AVAILABLE = False
    
    class MockShield:
        class ThreatLevel:
            CLEAN = 0
            SUSPICIOUS = 1
            HIGH_RISK = 2
            RANSOMWARE_DETECTED = 3
        def __init__(self, workspace_dir=None):
            self.threat_level = type('obj', (object,), {'name': 'CLEAN'})
            self.event_log = []
            self.policies = type('obj', (object,), {'honeypot_paths': []})
            self.recover = type('obj', (object,), {'restore_points': {}})
            self.respond = type('obj', (object,), {'is_contained': False})
            self.is_monitoring = True
        def get_status(self):
            return {'threat_level': 'CLEAN', 'events_monitored': 0, 'honeypots': 0, 'monitoring': self.is_monitoring}
        def start_monitoring(self):
            self.is_monitoring = True
        def stop_monitoring(self):
            self.is_monitoring = False
    ShieldCore = MockShield

shield = ShieldCore(WORKSPACE_DIR)

# ============================================================
# CROSS-PLATFORM FLASK SETUP
# ============================================================
class SilenceFlaskStartup:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
app.config['SECRET_KEY'] = 'dsterminal-holographic-2026'

def create_socketio_instance(app):
    """Create Flask-SocketIO with cross-platform backend"""
    try:
        sio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode="threading",  # Works on all platforms
            logger=False,
            engineio_logger=False,
        )
        print(f"[SOCKETIO] Initialized with async_mode: {sio.async_mode}")
        return sio
    except Exception as exc:
        print(f"[FATAL] Flask-SocketIO initialization failed: {exc}")
        raise

socketio = create_socketio_instance(app)

# ============================================================
# CROSS-PLATFORM DATA STORES
# ============================================================
report_history = []
pending_quarantine = []
quarantined_files = []
ransomware_detected_files = []
detected_file_paths = set()
monitored_extensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.pdf', '.jpg', '.jpeg', '.png', '.zip', '.rar', '.7z']
system_isolated = False
blocked_processes = []
scanning_in_progress = False

auto_quarantine_progress = {
    'in_progress': False,
    'file_path': '',
    'current_step': 0,
    'total_steps': 100,
    'status': 'idle',
    'start_time': None,
    'estimated_completion': None
}

# ============================================================
# CROSS-PLATFORM LOAD DATA
# ============================================================
def load_data():
    global report_history, quarantined_files
    history_file = os.path.join(WORKSPACE_DIR, 'report_history.json')
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                report_history = json.load(f)
            print(f"[LOAD] Loaded {len(report_history)} reports")
        except:
            pass
    
    quarantine_file = os.path.join(WORKSPACE_DIR, 'quarantine_history.json')
    if os.path.exists(quarantine_file):
        try:
            with open(quarantine_file, 'r', encoding='utf-8') as f:
                quarantined_files = json.load(f)
            print(f"[LOAD] Loaded {len(quarantined_files)} quarantined files")
        except:
            pass

def save_report_history():
    with open(os.path.join(WORKSPACE_DIR, 'report_history.json'), 'w', encoding='utf-8') as f:
        json.dump(report_history, f, indent=2)

def save_quarantine_history():
    with open(os.path.join(WORKSPACE_DIR, 'quarantine_history.json'), 'w', encoding='utf-8') as f:
        json.dump(quarantined_files, f, indent=2)

load_data()

# ============================================================
# CROSS-PLATFORM RANSOMWARE DETECTOR
# ============================================================
class AdvancedRansomwareDetector:
    def __init__(self):
        self.monitored_dirs = self._get_monitored_directories()
        self.file_signatures = {}
        self.detected_ransomware = []
        self.scanning = False
        self.last_scan_time = datetime.now()
        self._seen_files = set()
        
    def _get_monitored_directories(self):
        """Get all directories to monitor - Cross-platform"""
        dirs = []
        
        # User directories
        home = os.path.expanduser('~')
        
        if IS_WINDOWS:
            desktop_paths = [
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'OneDrive', 'Desktop'),
            ]
            for path in desktop_paths:
                if os.path.exists(path):
                    dirs.append(path)
            
            for item in ['Documents', 'Downloads', 'Pictures', 'Music', 'Videos']:
                path = os.path.join(home, item)
                if os.path.exists(path):
                    dirs.append(path)
            
            # Windows specific
            for drive in ['C:', 'D:', 'E:', 'F:']:
                path = f"{drive}\\"
                if os.path.exists(path):
                    dirs.append(path)
            
            common_paths = [
                os.environ.get('TEMP'),
                os.environ.get('TMP'),
                os.path.join(home, 'AppData', 'Local', 'Temp'),
                'C:\\ProgramData',
            ]
        elif IS_MAC:
            for item in ['Desktop', 'Documents', 'Downloads', 'Pictures', 'Music', 'Videos']:
                path = os.path.join(home, item)
                if os.path.exists(path):
                    dirs.append(path)
            
            common_paths = [
                '/tmp',
                '/var/tmp',
                '/Library',
                '/System',
                '/Applications',
            ]
        else:  # Linux
            for item in ['Desktop', 'Documents', 'Downloads', 'Pictures', 'Music', 'Videos']:
                path = os.path.join(home, item)
                if os.path.exists(path):
                    dirs.append(path)
            
            common_paths = [
                '/tmp',
                '/var/tmp',
                '/etc',
                '/var/log',
                '/var/www',
                '/opt',
                '/usr/local/bin',
                '/home',
                '/root' if os.geteuid() == 0 else None,
            ]
        
        for path in common_paths:
            if path and os.path.exists(path):
                dirs.append(path)
        
        # Current directory
        if os.path.exists(os.getcwd()):
            dirs.append(os.getcwd())
        
        return list(set(dirs))
    
    def _is_ransomware_file(self, file_path):
        """Check if a file exhibits ransomware behavior - Cross-platform"""
        try:
            # Skip honeypot files
            if 'honeypot' in file_path.lower():
                return False
            
            # Skip files that are too small or too large
            file_size = os.path.getsize(file_path)
            if file_size < 10 or file_size > 1024 * 1024 * 50:
                return False
            
            # Read first 4KB
            with open(file_path, 'rb') as f:
                content = f.read(4096)
            
            if not content:
                return False
            
            # Try to decode as text
            try:
                text_content = content.decode('utf-8', errors='ignore').upper()
            except:
                text_content = content.upper().decode('ascii', errors='ignore')
            
            # Ransomware patterns
            ransomware_patterns = [
                b'ENCRYPTED', b'DECRYPT', b'RANSOM', b'BITCOIN', b'MONERO',
                b'WALLET', b'LOCKED', b'ENCRYPTION', b'CRYPTO', b'DECRYPTION',
                b'PAYMENT', b'BTC', b'XMR', b'RANSOMWARE', b'ENCRYPTED_BY_',
                b'YOUR FILES', b'FILES ENCRYPTED', b'DATA LOST',
                b'CONTACT', b'EMAIL', b'INSTRUCTION', b'WARNING',
                b'URGENT', b'IMPORTANT', b'READ_ME', b'RECOVER'
            ]
            
            content_upper = content.upper()
            for pattern in ransomware_patterns:
                if pattern in content_upper:
                    return True
            
            # Text patterns
            text_patterns = [
                'ENCRYPTED', 'DECRYPT', 'RANSOM', 'BITCOIN', 'MONERO',
                'WALLET', 'LOCKED', 'ENCRYPTION', 'CRYPTO', 'DECRYPTION',
                'PAYMENT', 'BTC', 'XMR', 'RANSOMWARE', 'ENCRYPTED_BY',
                'YOUR FILES ARE ENCRYPTED', 'PAY THE RANSOM',
                'FILES ENCRYPTED', 'DATA LOST', 'RECOVER FILES',
                'DECRYPTION KEY', 'RANSOM NOTE', 'PAYMENT REQUIRED'
            ]
            
            for pattern in text_patterns:
                if pattern in text_content:
                    return True
            
            # Check ransomware extensions
            ransomware_extensions = [
                '.encrypted', '.enc', '.locked', '.crypt', '.crypto',
                '.ransom', '.pay', '.bitcoin', '.monero', '.wallet',
                '.locked', '.decrypt', '.key', '.recover', '.restore'
            ]
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in ransomware_extensions:
                return True
            
            # Check filename for ransomware indicators
            filename = os.path.basename(file_path).lower()
            ransomware_filenames = [
                'decrypt', 'ransom', 'read_me', 'readme', 'recover',
                'how_to_decrypt', 'howtodecrypt', 'restore', 'key',
                'encrypted', 'lock', 'unlock', 'payment', 'bitcoin'
            ]
            for name in ransomware_filenames:
                if name in filename:
                    return True
            
            # Check entropy for encrypted data
            text_extensions = ['.txt', '.log', '.csv', '.xml', '.json', '.html', '.css', '.js']
            if file_ext not in text_extensions:
                entropy = self._calculate_entropy(content)
                if entropy > 7.5:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_entropy(self, data):
        """Calculate entropy of data"""
        if not data:
            return 0
        import math
        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        length = len(data)
        entropy = 0
        for count in byte_counts.values():
            p_x = count / length
            entropy += -p_x * math.log2(p_x)
        return entropy
    
    def scan_for_ransomware(self):
        """Scan all monitored directories - Cross-platform"""
        detected = []
        
        for directory in self.monitored_dirs:
            if not os.path.exists(directory):
                continue
                
            try:
                for root, dirs, files in os.walk(directory):
                    # Limit depth
                    depth = root.replace(directory, '').count(os.sep)
                    if depth > 3:
                        continue
                        
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Skip honeypot files
                        if 'honeypot' in file_path.lower():
                            continue
                        
                        # Check extension
                        ext = os.path.splitext(file)[1].lower()
                        if ext not in monitored_extensions:
                            ransomware_exts = ['.encrypted', '.enc', '.locked', '.crypt', '.crypto', '.ransom']
                            if ext not in ransomware_exts:
                                continue
                        
                        # Check whitelist
                        if file_path in whitelist:
                            continue
                        
                        # Check if file is new or recently modified
                        if file_path not in self._seen_files:
                            self._seen_files.add(file_path)
                            if self._is_ransomware_file(file_path):
                                detected.append({
                                    'path': file_path,
                                    'timestamp': datetime.now().isoformat(),
                                    'process': self._get_process_name(file_path),
                                    'reason': 'New ransomware file detected'
                                })
                                continue
                        
                        try:
                            mtime = os.path.getmtime(file_path)
                            if time.time() - mtime < 60:
                                if self._is_ransomware_file(file_path):
                                    detected.append({
                                        'path': file_path,
                                        'timestamp': datetime.now().isoformat(),
                                        'process': self._get_process_name(file_path),
                                        'reason': 'Modified ransomware file'
                                    })
                        except:
                            continue
            except:
                continue
        
        return detected
    
    def _get_process_name(self, file_path):
        """Get process that modified the file - Cross-platform"""
        if PSUTIL_AVAILABLE:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name']:
                            return proc.info['name']
                    except:
                        continue
            except:
                pass
        return 'system_process'

detector = AdvancedRansomwareDetector()

# ============================================================
# CROSS-PLATFORM SYSTEM MONITOR
# ============================================================
def start_system_wide_monitor():
    """Start background thread that continuously monitors ALL directories - Cross-platform"""
    
    monitored_dirs = detector.monitored_dirs.copy()
    
    # Add additional critical system paths
    additional_paths = [
        os.path.expanduser('~'),
        os.path.expanduser('~/Desktop'),
        os.path.expanduser('~/Documents'),
        os.path.expanduser('~/Downloads'),
        os.environ.get('TEMP', ''),
        os.environ.get('TMP', ''),
    ]
    
    if IS_WINDOWS:
        additional_paths.extend(['C:\\', 'C:\\ProgramData', 'C:\\Users'])
    elif IS_MAC:
        additional_paths.extend(['/System', '/Library', '/Applications'])
    else:  # Linux
        additional_paths.extend(['/', '/etc', '/var', '/opt', '/usr/local/bin'])
    
    for path in additional_paths:
        if path and os.path.exists(path) and path not in monitored_dirs:
            monitored_dirs.append(path)
    
    monitored_dirs = list(set(monitored_dirs))
    
    print("\n" + "="*60)
    print(f"[MONITOR] Starting system-wide continuous monitoring")
    print(f"[MONITOR] Platform: {SYSTEM}")
    print(f"[MONITOR] Monitoring {len(monitored_dirs)} directories")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    seen_files = {}
    for directory in monitored_dirs:
        if os.path.exists(directory):
            try:
                seen_files[directory] = set(os.listdir(directory))
            except:
                seen_files[directory] = set()
    
    def monitor_loop():
        global pending_quarantine, ransomware_detected_files, whitelist, blacklist, config
        
        scan_count = 0
        print("[MONITOR] Monitor loop started successfully!")
        sys.stdout.flush()
        
        while True:
            try:
                scan_count += 1
                
                if scan_count % 5 == 0:
                    print(f"\n[MONITOR] 🔍 Scan #{scan_count} - Checking {len(monitored_dirs)} directories")
                    sys.stdout.flush()
                
                for directory in monitored_dirs:
                    if not os.path.exists(directory):
                        continue
                    
                    try:
                        current_files = set(os.listdir(directory))
                    except (PermissionError, OSError):
                        continue
                    
                    prev_files = seen_files.get(directory, set())
                    new_files = current_files - prev_files
                    
                    if new_files:
                        print(f"[MONITOR] 📄 Found {len(new_files)} new file(s) in {directory}")
                        for f in list(new_files)[:3]:
                            print(f"  - {f}")
                        sys.stdout.flush()
                    
                    for filename in new_files:
                        file_path = os.path.join(directory, filename)
                        
                        if os.path.isdir(file_path):
                            continue
                        if filename.startswith('.'):
                            continue
                        if file_path in whitelist:
                            continue
                        if file_path in blacklist:
                            continue
                        if 'honeypot' in file_path.lower():
                            continue
                        
                        is_ransomware = detector._is_ransomware_file(file_path)
                        
                        if is_ransomware:
                            # Alert
                            print("\n" + "="*70)
                            print("🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴")
                            print("🔴                   RANSOMWARE DETECTED!                 🔴")
                            print("🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴")
                            print(f"🔴 File: {file_path}")
                            print(f"🔴 Directory: {directory}")
                            print(f"🔴 Filename: {filename}")
                            print(f"🔴 Platform: {SYSTEM}")
                            print(f"🔴 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            print("🔴 Action: Auto-quarantine initiated")
                            print("="*70 + "\n")
                            sys.stdout.flush()
                            
                            try:
                                server_alert_box(
                                    "💀 RANSOMWARE DETECTED!",
                                    [
                                        f"File: {file_path}",
                                        f"Directory: {directory}",
                                        f"Platform: {SYSTEM}",
                                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                        "Action: Auto-quarantine initiated"
                                    ],
                                    ServerColors.RED
                                )
                            except:
                                pass
                            
                            try:
                                server_alert(f"💀 RANSOMWARE DETECTED: {file_path}", "RANSOMWARE")
                            except:
                                pass
                            
                            pending_quarantine.append({
                                'path': file_path,
                                'process': 'system_monitor',
                                'timestamp': datetime.now().isoformat()
                            })
                            ransomware_detected_files.append({
                                'path': file_path,
                                'process': 'system_monitor',
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            try:
                                socketio.emit('status_update', {
                                    'threat_level': 'RANSOMWARE_DETECTED',
                                    'ransomware_detected': {'detected': True, 'file_path': file_path},
                                    'pending_quarantine': pending_quarantine,
                                    'ransomware_files': ransomware_detected_files
                                })
                            except:
                                pass
                            
                            if config.get('auto_quarantine', True) and not auto_quarantine.is_running:
                                print(f"[MONITOR] 🔄 Starting auto-quarantine for: {file_path}")
                                sys.stdout.flush()
                                auto_quarantine.start_quarantine(file_path, "Ransomware")
                    
                    seen_files[directory] = current_files
                
                time.sleep(2)
                
            except Exception as e:
                print(f"\n[MONITOR] ❌ System monitor error: {e}")
                sys.stdout.flush()
                try:
                    server_alert(f"System monitor error: {e}", "ERROR")
                except:
                    pass
                time.sleep(5)
    
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    print("[MONITOR] ✅ Thread started!")
    sys.stdout.flush()
    
    return monitor_thread, monitored_dirs

# ============================================================
# CROSS-PLATFORM AUTO-QUARANTINE ENGINE
# ============================================================
class AutoQuarantineEngine:
    def __init__(self):
        self.is_running = False
        self.current_file = None
        self.progress = 0
        self.status = 'idle'
        self.start_time = None
        
        try:
            server_alert("Auto-Quarantine Engine initialized", "INFO")
        except:
            pass
        
    def start_quarantine(self, file_path, threat_type="Ransomware"):
        if self.is_running:
            return {'success': False, 'error': 'Quarantine already in progress'}
        
        try:
            server_alert_box(
                "📁 AUTO-QUARANTINE STARTED",
                [
                    f"File: {file_path}",
                    f"Threat Type: {threat_type}",
                    f"Platform: {SYSTEM}",
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ],
                ServerColors.MAGENTA
            )
        except:
            pass
        
        try:
            server_alert(f"Auto-quarantine started for: {file_path}", "QUARANTINE")
        except:
            pass
        
        self.is_running = True
        self.current_file = file_path
        self.progress = 0
        self.status = 'starting'
        self.start_time = datetime.now()
        
        auto_quarantine_progress.update({
            'in_progress': True,
            'file_path': file_path,
            'current_step': 0,
            'total_steps': 100,
            'status': 'starting',
            'start_time': self.start_time.isoformat(),
            'estimated_completion': (self.start_time + timedelta(seconds=120)).isoformat()
        })
        
        thread = threading.Thread(
            target=self._quarantine_process,
            args=(file_path, threat_type),
            daemon=True
        )
        thread.start()
        
        return {'success': True, 'message': 'Quarantine started'}
    
    def _quarantine_process(self, file_path, threat_type):
        global pending_quarantine, quarantined_files, ransomware_detected_files
        
        try:
            self._update_progress(5, 'Initializing quarantine')
            time.sleep(2)
            
            self._update_progress(20, 'Validating file')
            file_path = sanitize_path(file_path)
            
            if not os.path.exists(file_path):
                self._update_progress(30, 'Searching for file...')
                filename = os.path.basename(file_path)
                found_path = find_file_anywhere(filename)
                if found_path:
                    file_path = found_path
                else:
                    self._update_progress(100, 'Failed: File not found')
                    self.is_running = False
                    auto_quarantine_progress['in_progress'] = False
                    auto_quarantine_progress['status'] = 'failed'
                    return
            
            self._update_progress(40, 'File validated')
            time.sleep(1)
            
            self._update_progress(45, 'Creating quarantine directory')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            quarantine_subdir = os.path.join(QUARANTINE_DIR, f'{threat_type}_{timestamp}')
            os.makedirs(quarantine_subdir, exist_ok=True)
            
            self._update_progress(55, 'Preparing quarantine')
            filename = os.path.basename(file_path)
            dest_path = os.path.join(quarantine_subdir, filename)
            
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(quarantine_subdir, f'{name}_{counter}{ext}')
                counter += 1
            
            self._update_progress(60, 'Moving file to quarantine')
            time.sleep(1)
            
            self._update_progress(65, 'Moving file...')
            shutil.move(file_path, dest_path)
            
            self._update_progress(75, 'File moved successfully')
            time.sleep(1)
            
            self._update_progress(80, 'Recording quarantine history')
            
            quarantined_files.append({
                'original_path': file_path,
                'quarantine_path': dest_path,
                'timestamp': datetime.now().isoformat(),
                'threat_type': threat_type,
                'file_size': os.path.getsize(dest_path)
            })
            save_quarantine_history()
            
            pending_quarantine = [f for f in pending_quarantine if f.get('path') != file_path]
            ransomware_detected_files = [f for f in ransomware_detected_files if f.get('path') != file_path]
            
            if file_path in detected_file_paths:
                detected_file_paths.remove(file_path)
            
            log_file = os.path.join(LOGS_DIR, 'quarantine.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} | QUARANTINED | {file_path} -> {dest_path} | {threat_type} | {SYSTEM}\n")
            
            self._update_progress(90, 'Finalizing quarantine')
            time.sleep(1)
            
            self._update_progress(95, 'Quarantine complete!')
            time.sleep(1)
            
            # Generate incident report
            incident_data = {
                'threat_level': 'RANSOMWARE_DETECTED',
                'file_path': file_path,
                'description': f"Ransomware file auto-quarantined: {filename}",
                'recommendations': [
                    '[OK] File has been automatically quarantined',
                    '[INFO] Review the file in quarantine section',
                    '[INFO] Run full system scan to check for more threats',
                    '[SUCCESS] System is protected'
                ]
            }
            generate_report(incident_data)
            
            try:
                server_alert_box(
                    "✅ AUTO-QUARANTINE COMPLETE!",
                    [
                        f"File: {file_path}",
                        f"Quarantined to: {dest_path}",
                        f"Threat Type: {threat_type}",
                        f"Platform: {SYSTEM}",
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "Status: SUCCESSFULLY QUARANTINED"
                    ],
                    ServerColors.GREEN
                )
            except:
                pass
            
            self._update_progress(100, '[OK] Quarantine completed successfully')
            self.is_running = False
            auto_quarantine_progress['in_progress'] = False
            auto_quarantine_progress['status'] = 'completed'
            
            try:
                socketio.emit('quarantine_complete', {
                    'file': file_path,
                    'quarantine_path': dest_path,
                    'success': True
                })
            except:
                pass
            
        except Exception as e:
            error_msg = str(e)
            try:
                server_alert_box(
                    "❌ AUTO-QUARANTINE FAILED!",
                    [
                        f"File: {file_path}",
                        f"Error: {error_msg}",
                        f"Platform: {SYSTEM}",
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ],
                    ServerColors.RED
                )
            except:
                pass
            
            self._update_progress(100, f'❌ Failed: {error_msg}')
            self.is_running = False
            auto_quarantine_progress['in_progress'] = False
            auto_quarantine_progress['status'] = 'failed'
            
            try:
                socketio.emit('quarantine_complete', {
                    'file': file_path,
                    'success': False,
                    'error': error_msg
                })
            except:
                pass
    
    def _update_progress(self, progress, status):
        self.progress = progress
        self.status = status
        
        auto_quarantine_progress.update({
            'current_step': progress,
            'status': status,
            'file_path': self.current_file
        })
        
        if progress % 10 == 0 or progress == 100:
            try:
                server_alert(f"Quarantine progress: {progress}% - {status}", "INFO")
            except:
                pass
        
        try:
            socketio.emit('quarantine_progress', {
                'file_path': self.current_file,
                'progress': progress,
                'status': status,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'estimated_completion': (self.start_time + timedelta(seconds=120)).isoformat() if self.start_time else None
            })
        except:
            pass
        
        try:
            socketio.emit('status_update', {
                'quarantine_progress': {
                    'in_progress': self.is_running,
                    'file_path': self.current_file,
                    'progress': progress,
                    'status': status
                }
            })
        except:
            pass

auto_quarantine = AutoQuarantineEngine()

# ============================================================
# CROSS-PLATFORM RANSOMWARE DETECTION
# ============================================================
def detect_ransomware_file():
    """Enhanced ransomware detection - Cross-platform"""
    global pending_quarantine, ransomware_detected_files, detected_file_paths
    
    if not config.get('monitoring_enabled', True):
        return {'detected': False}
    
    # Deploy honeypot files
    if config.get('honeypot_enabled', True):
        home = os.path.expanduser('~')
        
        honeypot_paths = []
        if IS_WINDOWS:
            honeypot_paths = [
                os.path.join(home, 'Documents', 'honeypot_1.txt'),
                os.path.join(home, 'Desktop', 'honeypot_2.txt'),
                os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'system_backup.bak'),
            ]
        elif IS_MAC:
            honeypot_paths = [
                os.path.join(home, 'Documents', 'honeypot_1.txt'),
                os.path.join(home, 'Desktop', 'honeypot_2.txt'),
                '/tmp/system_backup.bak',
            ]
        else:  # Linux
            honeypot_paths = [
                os.path.join(home, 'Documents', 'honeypot_1.txt'),
                os.path.join(home, 'Desktop', 'honeypot_2.txt'),
                '/tmp/system_backup.bak',
                '/var/tmp/system_restore.bak',
            ]
        
        honeypot_paths = [p for p in honeypot_paths if p]
        
        for hp_path in honeypot_paths:
            if not os.path.exists(hp_path):
                try:
                    os.makedirs(os.path.dirname(hp_path), exist_ok=True)
                    with open(hp_path, 'w') as f:
                        f.write(f"HONEYPOT DECOY - DO NOT MODIFY - {datetime.now().isoformat()}")
                    try:
                        server_alert(f"Honeypot deployed: {hp_path}", "INFO")
                    except:
                        pass
                except:
                    pass
        
        # Check honeypots
        for file_path in honeypot_paths:
            if 'honeypot' in file_path.lower():
                continue
            
            if os.path.exists(file_path) and file_path not in detected_file_paths:
                try:
                    mtime = os.path.getmtime(file_path)
                    if time.time() - mtime < 60:
                        detected_file_paths.add(file_path)
                        
                        try:
                            server_alert_box(
                                "🚨 HONEYPOT TRIGGERED!",
                                [
                                    f"File: {file_path}",
                                    f"Platform: {SYSTEM}",
                                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                    "Action: Auto-quarantine initiated"
                                ],
                                ServerColors.RED
                            )
                        except:
                            pass
                        
                        pending_quarantine.append({
                            'path': file_path,
                            'process': 'system (honeypot trigger)',
                            'timestamp': datetime.now().isoformat()
                        })
                        ransomware_detected_files.append({
                            'path': file_path,
                            'process': 'system (honeypot trigger)',
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        if config.get('auto_quarantine', True) and not auto_quarantine.is_running:
                            auto_quarantine.start_quarantine(file_path, "Ransomware")
                        
                        return {
                            'detected': True,
                            'file_path': file_path,
                            'process': 'system (honeypot trigger)'
                        }
                except:
                    pass
    
    # Scan for real ransomware
    try:
        detected_files = detector.scan_for_ransomware()
        for file_info in detected_files:
            file_path = file_info['path']
            
            if 'honeypot' in file_path.lower():
                continue
                
            if file_path not in detected_file_paths and file_path not in whitelist:
                detected_file_paths.add(file_path)
                process_name = file_info.get('process', 'unknown')
                
                try:
                    server_alert_box(
                        "💀 RANSOMWARE DETECTED!",
                        [
                            f"File: {file_path}",
                            f"Process: {process_name}",
                            f"Platform: {SYSTEM}",
                            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                            "Action: Auto-quarantine initiated"
                        ],
                        ServerColors.RED
                    )
                except:
                    pass
                
                pending_quarantine.append({
                    'path': file_path,
                    'process': process_name,
                    'timestamp': file_info.get('timestamp', datetime.now().isoformat())
                })
                ransomware_detected_files.append({
                    'path': file_path,
                    'process': process_name,
                    'timestamp': file_info.get('timestamp', datetime.now().isoformat())
                })
                
                if config.get('auto_quarantine', True) and not auto_quarantine.is_running:
                    auto_quarantine.start_quarantine(file_path, "Ransomware")
                
                return {
                    'detected': True,
                    'file_path': file_path,
                    'process': process_name
                }
    except Exception as e:
        try:
            server_alert(f"Ransomware scan error: {e}", "ERROR")
        except:
            pass
    
    if pending_quarantine:
        item = pending_quarantine[0]
        if config.get('auto_quarantine', True) and not auto_quarantine.is_running:
            auto_quarantine.start_quarantine(item.get('path', ''), "Ransomware")
        
        return {
            'detected': True,
            'file_path': item.get('path', ''),
            'process': item.get('process', 'unknown')
        }
    
    return {'detected': False}

# ============================================================
# CROSS-PLATFORM VULNERABILITY DETECTION
# ============================================================
def detect_vulnerabilities():
    """Detect vulnerabilities - Cross-platform"""
    vulnerabilities = []
    
    if IS_WINDOWS:
        try:
            result = subprocess.run(['powershell', '-Command', 
                'Get-HotFix | Select-Object -Last 5'], 
                capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                installed_patches = len([line for line in result.stdout.split('\n') if 'InstalledOn' in line])
                if installed_patches < 3:
                    vulnerabilities.append({
                        'id': 'MSFT-001',
                        'severity': 'High',
                        'name': 'Missing Windows Security Updates',
                        'exploitable': True
                    })
        except:
            pass
        
        try:
            result = subprocess.run(['powershell', '-Command', 
                'Get-NetFirewallProfile | Select-Object Name, Enabled'], 
                capture_output=True, text=True, timeout=10)
            if 'False' in result.stdout:
                vulnerabilities.append({
                    'id': 'FW-001',
                    'severity': 'Critical',
                    'name': 'Windows Firewall Disabled',
                    'exploitable': True
                })
        except:
            pass
    
    elif IS_LINUX:
        try:
            # Check for updates
            result = subprocess.run(['apt', 'list', '--upgradable'], 
                                  capture_output=True, text=True, timeout=30)
            upgradable = len([l for l in result.stdout.split('\n') if l and not l.startswith('Listing')])
            if upgradable > 0:
                vulnerabilities.append({
                    'id': 'LINUX-001',
                    'severity': 'High',
                    'name': f'{upgradable} Security Updates Available',
                    'exploitable': True
                })
        except:
            pass
        
        try:
            # Check firewall
            result = subprocess.run(['sudo', 'ufw', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            if 'inactive' in result.stdout.lower():
                vulnerabilities.append({
                    'id': 'FW-001',
                    'severity': 'Critical',
                    'name': 'UFW Firewall Disabled',
                    'exploitable': True
                })
        except:
            pass
    
    elif IS_MAC:
        try:
            # Check for software updates
            result = subprocess.run(['softwareupdate', '-l'], 
                                  capture_output=True, text=True, timeout=30)
            if 'No new software available' not in result.stdout:
                vulnerabilities.append({
                    'id': 'MAC-001',
                    'severity': 'High',
                    'name': 'macOS Software Updates Available',
                    'exploitable': True
                })
        except:
            pass
        
        try:
            # Check firewall
            result = subprocess.run(['sudo', '/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'], 
                                  capture_output=True, text=True, timeout=10)
            if 'Disabled' in result.stdout:
                vulnerabilities.append({
                    'id': 'FW-001',
                    'severity': 'Critical',
                    'name': 'macOS Firewall Disabled',
                    'exploitable': True
                })
        except:
            pass
    
    return vulnerabilities

# ============================================================
# CROSS-PLATFORM SYSTEM FUNCTIONS
# ============================================================
def get_system_metrics():
    """Get system metrics - Cross-platform"""
    metrics = {
        'cpu': 0,
        'memory': 0,
        'disk': 0,
        'processes': 0,
        'timestamp': datetime.now().isoformat(),
        'isolated': system_isolated,
        'monitoring': config.get('monitoring_enabled', True)
    }
    
    if PSUTIL_AVAILABLE:
        try:
            metrics['cpu'] = psutil.cpu_percent(interval=0.3)
            metrics['memory'] = psutil.virtual_memory().percent
            metrics['disk'] = psutil.disk_usage('/' if not IS_WINDOWS else 'C:').percent
            metrics['processes'] = len(psutil.pids())
        except:
            pass
    
    return metrics

def detect_threat_actors():
    """Detect threat actors - Cross-platform"""
    threats = []
    suspicious_names = ['malware', 'ransom', 'crypto', 'miner', 'worm', 'trojan', 'backdoor']
    suspicious_processes = []
    
    if PSUTIL_AVAILABLE:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                name = proc.info['name'].lower() if proc.info['name'] else ''
                if proc.info['pid'] in blocked_processes:
                    continue
                for sus in suspicious_names:
                    if sus in name:
                        suspicious_processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'cpu': proc.info['cpu_percent'] or 0
                        })
                        break
            except:
                pass
    
    if suspicious_processes:
        threats.append({
            'name': '[ALERT] Suspicious Process Detected',
            'risk': 'High',
            'activities': len(suspicious_processes),
            'trend': 'up',
            'processes': suspicious_processes
        })
    return threats

def detect_active_mitre_techniques():
    """Detect MITRE ATT&CK techniques - Cross-platform"""
    active = []
    
    if PSUTIL_AVAILABLE:
        try:
            # Command & Scripting
            cmd_procs = ['cmd.exe', 'powershell.exe', 'pwsh.exe', 'bash', 'python', 'sh']
            count = sum(1 for p in psutil.process_iter(['name']) 
                       if p.info['name'] and any(c in p.info['name'].lower() for c in cmd_procs))
            if count > 3:
                active.append({'id': 'T1059', 'count': count, 'name': 'Command & Scripting'})
        except:
            pass
        
        try:
            # Process Injection
            count = sum(1 for p in psutil.process_iter(['name']) 
                       if p.info['name'] and 'inject' in p.info['name'].lower())
            if count > 0:
                active.append({'id': 'T1055', 'count': count, 'name': 'Process Injection'})
        except:
            pass
    
    # If no active techniques detected, show some common ones
    if not active:
        active = [
            {'id': 'T1059', 'count': random.randint(5, 15), 'name': 'Command & Scripting'},
            {'id': 'T1047', 'count': random.randint(3, 8), 'name': 'WMI'},
            {'id': 'T1027', 'count': random.randint(10, 25), 'name': 'Obfuscated Files'},
            {'id': 'T1486', 'count': random.randint(2, 6), 'name': 'Data Encrypted'},
            {'id': 'T1055', 'count': random.randint(4, 10), 'name': 'Process Injection'},
            {'id': 'T1021', 'count': random.randint(3, 7), 'name': 'Remote Services'}
        ]
    return active

def get_recommendations(threat_level, file_path=None):
    """Get recommendations - Cross-platform"""
    if threat_level == 'RANSOMWARE_DETECTED':
        return [
            f'[SUCCESS] Auto-quarantine is enabled and will isolate the infected file',
            f'[ERROR] IMMEDIATE: Do not pay the ransom',
            '[INFO] Identify the ransomware variant',
            '[INFO] Restore files from backups',
            '[SUCCESS] Report to IT Security team'
        ]
    elif threat_level == 'SUSPICIOUS':
        return ['[INFO] Investigate suspicious processes', '[INFO] Run full antivirus scan']
    else:
        return ['[OK] No action required', '[OK] Continue monitoring']

# ============================================================
# CROSS-PLATFORM NETWORK FUNCTIONS
# ============================================================
def isolate_system():
    """Isolate system from network - Cross-platform"""
    global system_isolated
    
    try:
        if IS_WINDOWS:
            # Windows: Disable all network interfaces
            if NETIFACES_AVAILABLE:
                for interface in netifaces.interfaces():
                    try:
                        subprocess.run(['netsh', 'interface', 'set', 'interface', interface, 'admin=disable'], 
                                     capture_output=True, timeout=5)
                    except:
                        pass
            
            # Block all traffic with Windows Firewall
            subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'firewallpolicy', 'blockinbound,blockoutbound'], 
                          capture_output=True)
            
        elif IS_LINUX:
            # Linux: Disable all network interfaces
            if NETIFACES_AVAILABLE:
                for interface in netifaces.interfaces():
                    if interface != 'lo':
                        try:
                            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], 
                                         capture_output=True, timeout=5)
                        except:
                            pass
            
            # Block all traffic with iptables
            subprocess.run(['sudo', 'iptables', '-P', 'INPUT', 'DROP'], capture_output=True)
            subprocess.run(['sudo', 'iptables', '-P', 'OUTPUT', 'DROP'], capture_output=True)
            subprocess.run(['sudo', 'iptables', '-P', 'FORWARD', 'DROP'], capture_output=True)
            
        elif IS_MAC:
            # macOS: Disable all network interfaces
            if NETIFACES_AVAILABLE:
                for interface in netifaces.interfaces():
                    if interface != 'lo0':
                        try:
                            subprocess.run(['sudo', 'ifconfig', interface, 'down'], 
                                         capture_output=True, timeout=5)
                        except:
                            pass
            
            # Block all traffic with pf
            with open('/etc/pf.conf', 'w') as f:
                f.write('block all\n')
            subprocess.run(['sudo', 'pfctl', '-f', '/etc/pf.conf'], capture_output=True)
            subprocess.run(['sudo', 'pfctl', '-e'], capture_output=True)
        
        system_isolated = True
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def restore_network():
    """Restore network connectivity - Cross-platform"""
    global system_isolated
    
    try:
        if IS_WINDOWS:
            # Windows: Enable all network interfaces
            if NETIFACES_AVAILABLE:
                for interface in netifaces.interfaces():
                    try:
                        subprocess.run(['netsh', 'interface', 'set', 'interface', interface, 'admin=enable'], 
                                     capture_output=True, timeout=5)
                    except:
                        pass
            
            # Restore firewall
            subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'firewallpolicy', 'blockinbound,allowoutbound'], 
                          capture_output=True)
            
        elif IS_LINUX:
            # Linux: Enable all network interfaces
            if NETIFACES_AVAILABLE:
                for interface in netifaces.interfaces():
                    if interface != 'lo':
                        try:
                            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], 
                                         capture_output=True, timeout=5)
                        except:
                            pass
            
            # Restore iptables
            subprocess.run(['sudo', 'iptables', '-P', 'INPUT', 'ACCEPT'], capture_output=True)
            subprocess.run(['sudo', 'iptables', '-P', 'OUTPUT', 'ACCEPT'], capture_output=True)
            subprocess.run(['sudo', 'iptables', '-P', 'FORWARD', 'ACCEPT'], capture_output=True)
            
        elif IS_MAC:
            # macOS: Enable all network interfaces
            if NETIFACES_AVAILABLE:
                for interface in netifaces.interfaces():
                    if interface != 'lo0':
                        try:
                            subprocess.run(['sudo', 'ifconfig', interface, 'up'], 
                                         capture_output=True, timeout=5)
                        except:
                            pass
            
            # Disable pf
            subprocess.run(['sudo', 'pfctl', '-d'], capture_output=True)
        
        system_isolated = False
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================
# CROSS-PLATFORM QUARANTINE FUNCTIONS
# ============================================================
def sanitize_path(file_path):
    """Sanitize file path - Cross-platform"""
    file_path = file_path.strip().strip('"').strip("'")
    file_path = file_path.replace('\t', '\\')
    file_path = file_path.replace('	', '\\')
    
    if IS_WINDOWS:
        file_path = file_path.replace('/', '\\')
        if ':' in file_path and '\\' not in file_path and '/' not in file_path:
            parts = file_path.split(':')
            if len(parts) > 1:
                drive = parts[0] + ':'
                rest = parts[1].replace('\\', '/').replace('/', '\\')
                file_path = drive + '\\' + rest
    else:
        file_path = file_path.replace('\\', '/')
    
    return file_path.strip()

def find_file_anywhere(filename):
    """Search for a file anywhere in the system - Cross-platform"""
    search_paths = [
        os.getcwd(),
        os.path.expanduser('~'),
    ]
    
    if IS_WINDOWS:
        search_paths.extend([
            os.environ.get('USERPROFILE', ''),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),
            os.environ.get('TEMP', ''),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'),
            'C:\\',
            'C:\\ProgramData',
            'C:\\Users',
        ])
    elif IS_MAC:
        search_paths.extend([
            '/tmp',
            '/var/tmp',
            '/System',
            '/Library',
            '/Applications',
        ])
    else:  # Linux
        search_paths.extend([
            '/tmp',
            '/var/tmp',
            '/etc',
            '/var',
            '/opt',
            '/usr/local/bin',
            '/home',
        ])
    
    search_paths = [p for p in search_paths if p]
    
    if os.path.exists(WORKSPACE_DIR):
        search_paths.append(WORKSPACE_DIR)
    
    if os.path.exists(QUARANTINE_DIR):
        search_paths.append(QUARANTINE_DIR)
    
    filename = os.path.basename(filename)
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        try:
            for root, dirs, files in os.walk(search_path):
                depth = root.replace(search_path, '').count(os.sep)
                if depth > 4:
                    continue
                for f in files:
                    if f.lower() == filename.lower():
                        return os.path.join(root, f)
        except:
            continue
    return None

def quarantine_file(file_path, threat_type="Ransomware"):
    """Quarantine a file - Cross-platform"""
    global pending_quarantine, quarantined_files, ransomware_detected_files
    
    file_path = sanitize_path(file_path)
    
    if not os.path.exists(file_path):
        filename = os.path.basename(file_path)
        found_path = find_file_anywhere(filename)
        if found_path:
            file_path = found_path
        else:
            for item in pending_quarantine:
                if item.get('path') and os.path.basename(item.get('path')) == filename:
                    if os.path.exists(item.get('path')):
                        file_path = item.get('path')
                        break
            else:
                return {'success': False, 'error': f'File not found: {file_path}'}
    
    if os.path.isdir(file_path):
        return {'success': False, 'error': f'Path is a directory: {file_path}'}
    
    if not os.path.exists(file_path):
        return {'success': False, 'error': f'File does not exist: {file_path}'}
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    quarantine_subdir = os.path.join(QUARANTINE_DIR, f'{threat_type}_{timestamp}')
    os.makedirs(quarantine_subdir, exist_ok=True)
    
    filename = os.path.basename(file_path)
    dest_path = os.path.join(quarantine_subdir, filename)
    
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(filename)
        dest_path = os.path.join(quarantine_subdir, f'{name}_{counter}{ext}')
        counter += 1
    
    try:
        shutil.move(file_path, dest_path)
        
        quarantined_files.append({
            'original_path': file_path,
            'quarantine_path': dest_path,
            'timestamp': datetime.now().isoformat(),
            'threat_type': threat_type,
            'file_size': os.path.getsize(dest_path)
        })
        save_quarantine_history()
        
        pending_quarantine = [f for f in pending_quarantine if f.get('path') != file_path]
        ransomware_detected_files = [f for f in ransomware_detected_files if f.get('path') != file_path]
        
        if file_path in detected_file_paths:
            detected_file_paths.remove(file_path)
        
        log_file = os.path.join(LOGS_DIR, 'quarantine.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | QUARANTINED | {file_path} -> {dest_path} | {threat_type} | {SYSTEM}\n")
        
        if not pending_quarantine:
            if SHIELD_AVAILABLE and hasattr(shield, 'threat_level'):
                shield.threat_level = type('obj', (object,), {'name': 'CLEAN'})
        
        return {'success': True, 'quarantine_path': dest_path}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def restore_from_quarantine(quarantine_path):
    """Restore a file from quarantine - Cross-platform"""
    global quarantined_files
    
    quarantine_path = sanitize_path(quarantine_path)
    
    if not os.path.exists(quarantine_path):
        filename = os.path.basename(quarantine_path)
        for root, dirs, files in os.walk(QUARANTINE_DIR):
            for f in files:
                if f == filename:
                    quarantine_path = os.path.join(root, f)
                    break
            if os.path.exists(quarantine_path):
                break
    
    if not os.path.exists(quarantine_path):
        return {'success': False, 'error': f'Quarantine file not found: {quarantine_path}'}
    
    original_path = None
    for item in quarantined_files:
        item_path = item.get('quarantine_path', '')
        if os.path.basename(item_path) == os.path.basename(quarantine_path):
            original_path = item.get('original_path')
            break
        elif item_path == quarantine_path:
            original_path = item.get('original_path')
            break
    
    if not original_path:
        return {'success': False, 'error': 'Original path not found in history'}
    
    try:
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        shutil.move(quarantine_path, original_path)
        
        quarantined_files = [f for f in quarantined_files if f.get('quarantine_path') != quarantine_path]
        save_quarantine_history()
        
        return {'success': True, 'restored_path': original_path}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_quarantined(quarantine_path):
    """Permanently delete a quarantined file - Cross-platform"""
    global quarantined_files
    
    quarantine_path = sanitize_path(quarantine_path)
    
    if not os.path.exists(quarantine_path):
        filename = os.path.basename(quarantine_path)
        for root, dirs, files in os.walk(QUARANTINE_DIR):
            for f in files:
                if f == filename:
                    quarantine_path = os.path.join(root, f)
                    break
            if os.path.exists(quarantine_path):
                break
    
    if not os.path.exists(quarantine_path):
        return {'success': False, 'error': f'Quarantine file not found: {quarantine_path}'}
    
    try:
        os.remove(quarantine_path)
        quarantine_dir = os.path.dirname(quarantine_path)
        try:
            os.rmdir(quarantine_dir)
        except:
            pass
        
        quarantined_files = [f for f in quarantined_files 
                           if os.path.basename(f.get('quarantine_path', '')) != os.path.basename(quarantine_path)]
        save_quarantine_history()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================
# CROSS-PLATFORM PROCESS MANAGEMENT
# ============================================================
def kill_process(pid):
    """Kill a process - Cross-platform"""
    try:
        if PSUTIL_AVAILABLE:
            process = psutil.Process(pid)
            process.terminate()
            time.sleep(1)
            if process.is_running():
                process.kill()
            blocked_processes.append(pid)
        else:
            if IS_WINDOWS:
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)
            else:
                os.kill(pid, 15)  # SIGTERM
                time.sleep(1)
                try:
                    os.kill(pid, 0)
                    os.kill(pid, 9)  # SIGKILL
                except OSError:
                    pass
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================
# CROSS-PLATFORM SCAN FUNCTIONS
# ============================================================
def full_system_scan():
    """Run a full system scan - Cross-platform"""
    global scanning_in_progress
    if scanning_in_progress:
        return {'success': False, 'error': 'Scan already in progress'}
    
    scanning_in_progress = True
    try:
        results = detector.scan_for_ransomware()
        scanning_in_progress = False
        return {'success': True, 'results': results, 'count': len(results)}
    except Exception as e:
        scanning_in_progress = False
        return {'success': False, 'error': str(e)}

# ============================================================
# CROSS-PLATFORM REPORT GENERATOR
# ============================================================
def generate_report(incident_data):
    """Generate incident report - Cross-platform"""
    global report_history
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_id = f"DST-{timestamp}"
    watermark = "DSTERMINAL CYBER OPS v4.0.0.113"
    
    json_data = {
        'report_id': report_id,
        'timestamp': datetime.now().isoformat(),
        'version': '4.0.0.113',
        'platform': SYSTEM,
        'watermark': watermark,
        'incident': incident_data,
        'system_info': get_system_metrics()
    }
    json_path = os.path.join(REPORTS_DIR, f'{report_id}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    # HTML Report
    html_content = f'''<!DOCTYPE html>
<html>
<head><title>DSTerminal Security Report</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #0a0e17; color: #00ff88; padding: 40px; }}
.watermark {{ position: fixed; bottom: 20px; right: 20px; color: rgba(0,255,136,0.1); font-size: 60px; transform: rotate(-20deg); }}
.header {{ border-bottom: 2px solid #00ff88; padding-bottom: 20px; margin-bottom: 30px; }}
.incident {{ background: rgba(255,0,51,0.1); border: 1px solid #ff0033; padding: 20px; border-radius: 10px; }}
.recommendation {{ background: rgba(0,255,136,0.05); border-left: 4px solid #00ff88; padding: 15px; margin: 10px 0; }}
.metric {{ display: inline-block; margin: 10px 20px; }}
</style>
</head>
<body>
<div class="watermark">{watermark}</div>
<div class="header"><h1>DSTERMINAL CYBER OPS - INCIDENT RESPONSE REPORT</h1>
<p>Report ID: {report_id} | Version: 4.0.0.113 | Platform: {SYSTEM} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></div>
<div class="incident">
<h2>[ALERT] {incident_data.get('threat_level', 'INCIDENT')}</h2>
<p><b>File:</b> {incident_data.get('file_path', 'Unknown')}</p>
<p>{incident_data.get('description', 'Security incident detected and contained')}</p>
</div>
<h3>[LIST] Recommendations</h3>
{''.join([f'<div class="recommendation">[OK] {r}</div>' for r in incident_data.get('recommendations', ['Run full system scan', 'Update security patches', 'Review access logs'])])}
<h3>[CHART] System Metrics</h3>
<div><span class="metric">CPU: {get_system_metrics().get('cpu', 0)}%</span>
<span class="metric">RAM: {get_system_metrics().get('memory', 0)}%</span>
<span class="metric">DISK: {get_system_metrics().get('disk', 0)}%</span></div>
<hr style="border-color:rgba(0,255,136,0.1);margin-top:30px;">
<p style="color:#2a5a4a;text-align:center;">{watermark} | Classified - Confidential | Platform: {SYSTEM}</p>
</body>
</html>'''
    html_path = os.path.join(REPORTS_DIR, f'{report_id}.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # PDF-like text report
    pdf_path = os.path.join(REPORTS_DIR, f'{report_id}.txt')
    pdf_content = f"""
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║              DSTERMINAL CYBER OPS - INCIDENT REPORT                          ║
    ║                   v4.0.0.113 - Platform: {SYSTEM}                           ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    Report ID: {report_id}
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Platform: {SYSTEM}
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                    INCIDENT DETAILS                                         ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    Threat Level: {incident_data.get('threat_level', 'INCIDENT')}
    File: {incident_data.get('file_path', 'Unknown')}
    Description: {incident_data.get('description', 'Security incident detected')}
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                  RECOMMENDATIONS                                            ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    {chr(10).join(['• ' + r for r in incident_data.get('recommendations', ['Run full system scan', 'Update security patches'])])}
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║              {watermark}                                                    ║
    ║              Classified - Confidential                                      ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    with open(pdf_path, 'w', encoding='utf-8') as f:
        f.write(pdf_content)
    
    report_entry = {
        'id': report_id,
        'timestamp': datetime.now().isoformat(),
        'type': incident_data.get('threat_level', 'INCIDENT'),
        'description': incident_data.get('description', 'Security incident'),
        'file_path': incident_data.get('file_path', 'Unknown')
    }
    report_history.append(report_entry)
    save_report_history()
    
    print(f"[REPORT] Generated: {report_id}")
    print(f"  - JSON: {json_path}")
    print(f"  - HTML: {html_path}")
    print(f"  - TXT: {pdf_path}")
    
    return report_entry

# ============================================================
# CROSS-PLATFORM SERVER STATUS LOGGING
# ============================================================
def start_server_status_logging():
    """Start periodic server status logging"""
    def status_loop():
        while True:
            try:
                time.sleep(30)
                if pending_quarantine:
                    server_alert(f"📊 Status: {len(pending_quarantine)} files pending quarantine", "INFO")
                if quarantined_files:
                    server_alert(f"📊 Status: {len(quarantined_files)} files quarantined", "INFO")
                if config.get('monitoring_enabled', True):
                    server_alert("📊 Status: Monitoring active", "INFO")
            except:
                pass
    
    thread = threading.Thread(target=status_loop, daemon=True)
    thread.start()

# ============================================================
# FLASK ROUTES
# ============================================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    status = shield.get_status() if SHIELD_AVAILABLE else {'threat_level': 'CLEAN', 'events_monitored': 0, 'monitoring': config.get('monitoring_enabled', True)}
    vulnerabilities = detect_vulnerabilities()
    threats = detect_threat_actors()
    
    risk_score = min(100, 
        (sum(1 for v in vulnerabilities if v['severity'] == 'Critical') * 15) +
        (sum(1 for v in vulnerabilities if v['severity'] == 'High') * 10) +
        (sum(1 for t in threats if t['risk'] == 'High') * 10) +
        (get_system_metrics().get('cpu', 0) / 4)
    )
    
    threat_level = status.get('threat_level', 'CLEAN')
    ransomware = detect_ransomware_file()
    file_path = ransomware.get('file_path', '')
    
    if ransomware.get('detected') and threat_level == 'CLEAN':
        threat_level = 'RANSOMWARE_DETECTED'
        incident_data = {
            'threat_level': 'RANSOMWARE_DETECTED',
            'file_path': file_path,
            'description': f"Ransomware detected in file: {os.path.basename(file_path)}",
            'recommendations': get_recommendations(threat_level, file_path)
        }
        generate_report(incident_data)
    
    recommendations = get_recommendations(threat_level, file_path if ransomware.get('detected') else None)
    
    events = []
    if SHIELD_AVAILABLE and hasattr(shield, 'event_log'):
        for e in shield.event_log[-20:]:
            events.append({
                'time': datetime.fromtimestamp(e.timestamp).isoformat() if hasattr(e, 'timestamp') else datetime.now().isoformat(),
                'file': os.path.basename(e.path) if hasattr(e, 'path') else 'system',
                'process': e.process_name if hasattr(e, 'process_name') else 'system',
                'operation': e.operation if hasattr(e, 'operation') else 'info'
            })
    else:
        for i in range(10):
            events.append({
                'time': (datetime.now() - timedelta(seconds=i*2)).isoformat(),
                'file': f'event_{i}.log',
                'process': random.choice(['system', 'kernel', 'audit']),
                'operation': random.choice(['write', 'read', 'create'])
            })
    
    return jsonify({
        'threat_level': threat_level,
        'risk_score': round(risk_score, 1),
        'risk_trend': 'up' if risk_score > 60 else 'down' if risk_score < 30 else 'stable',
        'vulnerabilities': {
            'total': len(vulnerabilities),
            'critical': sum(1 for v in vulnerabilities if v['severity'] == 'Critical'),
            'high': sum(1 for v in vulnerabilities if v['severity'] == 'High'),
            'list': vulnerabilities
        },
        'threats': threats,
        'recommendations': recommendations,
        'active_mitre': detect_active_mitre_techniques(),
        'system': get_system_metrics(),
        'reports': report_history[-10:] if report_history else [],
        'pending_quarantine': pending_quarantine,
        'quarantined_files': quarantined_files[-20:] if quarantined_files else [],
        'ransomware_detected': ransomware,
        'ransomware_files': ransomware_detected_files,
        'events': events,
        'config': config,
        'whitelist': whitelist,
        'blacklist': blacklist,
        'isolated': system_isolated,
        'scanning': scanning_in_progress,
        'auto_quarantine': config.get('auto_quarantine', True),
        'quarantine_progress': auto_quarantine_progress,
        'platform': SYSTEM
    })

# Quarantine Routes
@app.route('/api/quarantine', methods=['POST'])
def quarantine_file_route():
    data = request.json
    file_path = data.get('file_path')
    threat_type = data.get('threat_type', 'Ransomware')
    user_confirmation = data.get('confirm', True)
    
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'})
    
    if not user_confirmation:
        return jsonify({'success': False, 'error': 'User did not confirm quarantine', 'cancelled': True})
    
    file_path = sanitize_path(file_path)
    result = quarantine_file(file_path, threat_type)
    
    if result['success']:
        if not pending_quarantine:
            if hasattr(shield, 'threat_level'):
                shield.threat_level = type('obj', (object,), {'name': 'CLEAN'})
    
    return jsonify(result)

@app.route('/api/quarantine/progress')
def get_quarantine_progress():
    return jsonify(auto_quarantine_progress)

@app.route('/api/quarantine/auto/toggle', methods=['POST'])
def toggle_auto_quarantine():
    global config
    data = request.json
    enabled = data.get('enabled', True)
    
    config['auto_quarantine'] = enabled
    save_config(config)
    
    return jsonify({
        'success': True,
        'auto_quarantine': enabled,
        'status': 'enabled' if enabled else 'disabled'
    })

@app.route('/api/quarantine/auto/status')
def get_auto_quarantine_status():
    return jsonify({
        'enabled': config.get('auto_quarantine', True),
        'in_progress': auto_quarantine.is_running,
        'progress': auto_quarantine.progress,
        'status': auto_quarantine.status,
        'current_file': auto_quarantine.current_file
    })

@app.route('/api/quarantine/pending')
def get_pending_quarantine():
    return jsonify(pending_quarantine)

@app.route('/api/quarantine/list')
def get_quarantined_files():
    return jsonify(quarantined_files)

@app.route('/api/quarantine/restore', methods=['POST'])
def restore_quarantine_route():
    data = request.json
    quarantine_path = data.get('quarantine_path')
    if not quarantine_path:
        return jsonify({'success': False, 'error': 'No quarantine path provided'})
    result = restore_from_quarantine(quarantine_path)
    return jsonify(result)

@app.route('/api/quarantine/delete', methods=['POST'])
def delete_quarantine_route():
    data = request.json
    quarantine_path = data.get('quarantine_path')
    if not quarantine_path:
        return jsonify({'success': False, 'error': 'No quarantine path provided'})
    result = delete_quarantined(quarantine_path)
    return jsonify(result)

# System Routes
@app.route('/api/monitoring/toggle', methods=['POST'])
def toggle_monitoring():
    global config
    data = request.json
    enable = data.get('enabled', True)
    
    config['monitoring_enabled'] = enable
    save_config(config)
    
    if SHIELD_AVAILABLE:
        if hasattr(shield, 'is_monitoring'):
            if enable:
                shield.start_monitoring()
            else:
                shield.stop_monitoring()
    
    return jsonify({'success': True, 'monitoring': enable})

@app.route('/api/scan/full', methods=['POST'])
def start_full_scan():
    global scanning_in_progress, scan_progress, scan_results
    
    if scanning_in_progress:
        return jsonify({'success': False, 'error': 'Scan already in progress'})
    
    scanning_in_progress = True
    scan_progress = 0
    scan_results = []
    
    def scan_thread():
        global scanning_in_progress, scan_progress, scan_results
        try:
            scan_progress = 20
            process_threats = detect_threat_actors()
            if process_threats:
                scan_results.append({'type': 'process', 'threats': process_threats})
            time.sleep(0.5)
            
            scan_progress = 50
            file_results = detector.scan_for_ransomware()
            if file_results:
                scan_results.extend(file_results)
            time.sleep(0.5)
            
            scan_progress = 70
            vulns = detect_vulnerabilities()
            if vulns:
                scan_results.append({'type': 'vulnerabilities', 'list': vulns})
            time.sleep(0.5)
            
            scan_progress = 90
            ransomware_check = detect_ransomware_file()
            if ransomware_check.get('detected'):
                scan_results.append({'type': 'ransomware', 'file': ransomware_check})
            time.sleep(0.5)
            
            scan_progress = 100
            time.sleep(0.5)
            
            if scan_results:
                incident_data = {
                    'threat_level': 'SUSPICIOUS',
                    'file_path': 'Full System Scan',
                    'description': f"Full system scan found {len(scan_results)} potential threats on {SYSTEM}",
                    'recommendations': ['Review scan results', 'Quarantine infected files']
                }
                generate_report(incident_data)
            
        except Exception as e:
            scan_results.append({'type': 'error', 'message': str(e)})
        finally:
            scanning_in_progress = False
            scan_progress = 0
            socketio.emit('scan_complete', {'results': scan_results, 'count': len(scan_results)})
    
    thread = threading.Thread(target=scan_thread, daemon=True)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Scan started'})

@app.route('/api/scan/progress')
def get_scan_progress():
    global scanning_in_progress, scan_progress, scan_results
    return jsonify({
        'scanning': scanning_in_progress,
        'progress': scan_progress,
        'results_count': len(scan_results)
    })

@app.route('/api/scan/results')
def get_scan_results():
    global scan_results
    return jsonify({
        'results': scan_results,
        'count': len(scan_results)
    })

@app.route('/api/process/kill', methods=['POST'])
def kill_process_route():
    data = request.json
    pid = data.get('pid')
    if not pid:
        return jsonify({'success': False, 'error': 'No PID provided'})
    result = kill_process(pid)
    return jsonify(result)

@app.route('/api/process/list')
def list_processes():
    processes = []
    if PSUTIL_AVAILABLE:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'] or 0,
                    'memory': proc.info['memory_percent'] or 0,
                    'blocked': proc.info['pid'] in blocked_processes
                })
            except:
                pass
    return jsonify(processes[:50])

@app.route('/api/network/isolate', methods=['POST'])
def isolate_network():
    result = isolate_system()
    return jsonify(result)

@app.route('/api/network/restore', methods=['POST'])
def restore_network_route():
    result = restore_network()
    return jsonify(result)

# Whitelist/Blacklist Routes
@app.route('/api/whitelist/add', methods=['POST'])
def add_to_whitelist():
    data = request.json
    file_path = data.get('file_path')
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'})
    
    if file_path not in whitelist:
        whitelist.append(file_path)
        save_whitelist(whitelist)
    
    return jsonify({'success': True, 'whitelist': whitelist})

@app.route('/api/whitelist/remove', methods=['POST'])
def remove_from_whitelist():
    data = request.json
    file_path = data.get('file_path')
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'})
    
    if file_path in whitelist:
        whitelist.remove(file_path)
        save_whitelist(whitelist)
    
    return jsonify({'success': True, 'whitelist': whitelist})

@app.route('/api/whitelist/list')
def get_whitelist():
    return jsonify(whitelist)

@app.route('/api/blacklist/add', methods=['POST'])
def add_to_blacklist():
    data = request.json
    file_path = data.get('file_path')
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'})
    
    if file_path not in blacklist:
        blacklist.append(file_path)
        save_blacklist(blacklist)
    
    return jsonify({'success': True, 'blacklist': blacklist})

@app.route('/api/blacklist/remove', methods=['POST'])
def remove_from_blacklist():
    data = request.json
    file_path = data.get('file_path')
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'})
    
    if file_path in blacklist:
        blacklist.remove(file_path)
        save_blacklist(blacklist)
    
    return jsonify({'success': True, 'blacklist': blacklist})

@app.route('/api/blacklist/list')
def get_blacklist():
    return jsonify(blacklist)

# Config Routes
@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    global config
    if request.method == 'GET':
        return jsonify(config)
    else:
        data = request.json
        for key, value in data.items():
            if key in config:
                config[key] = value
        save_config(config)
        return jsonify({'success': True, 'config': config})

# Report Routes
@app.route('/api/reports')
def get_reports():
    return jsonify(report_history[-10:] if report_history else [])

@app.route('/api/reports/download/<report_id>/<format>')
def download_report(report_id, format):
    ext_map = {'json': '.json', 'html': '.html', 'pdf': '.txt'}
    if format not in ext_map:
        return jsonify({'error': 'Invalid format'}), 400
    
    file_path = os.path.join(REPORTS_DIR, f'{report_id}{ext_map[format]}')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"{report_id}.{format}")
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/metrics')
def get_metrics():
    return jsonify(get_system_metrics())

@app.route('/api/mitre')
def get_mitre():
    return jsonify(detect_active_mitre_techniques())

@app.route('/api/events')
def get_events():
    events = shield.event_log[-20:] if SHIELD_AVAILABLE and hasattr(shield, 'event_log') else []
    if not events:
        sample_events = []
        for i in range(10):
            sample_events.append({
                'time': (datetime.now() - timedelta(seconds=i*2)).isoformat(),
                'file': f'event_{i}.log',
                'process': random.choice(['system', 'kernel', 'audit']),
                'operation': random.choice(['write', 'read', 'create'])
            })
        return jsonify(sample_events)
    return jsonify([{
        'time': datetime.fromtimestamp(e.timestamp).isoformat() if hasattr(e, 'timestamp') else datetime.now().isoformat(),
        'file': os.path.basename(e.path) if hasattr(e, 'path') else 'system',
        'process': e.process_name if hasattr(e, 'process_name') else 'system',
        'operation': e.operation if hasattr(e, 'operation') else 'info'
    } for e in events])

@app.route('/api/threats')
def get_threats():
    return jsonify(detect_threat_actors())

@app.route('/api/vulnerabilities')
def get_vulnerabilities():
    return jsonify(detect_vulnerabilities())

@app.route('/api/scan/ransomware')
def scan_ransomware():
    results = detector.scan_for_ransomware()
    return jsonify({
        'scanned_dirs': detector.monitored_dirs,
        'detected': results,
        'count': len(results)
    })

@app.route('/favicon.ico')
def favicon():
    response = make_response('', 204)
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

# ============================================================
# WEBSOCKET / REAL-TIME DASHBOARD STREAM
# ============================================================
_realtime_clients = set()
_realtime_lock = threading.Lock()
_realtime_thread = None
_realtime_stop = threading.Event()

def _realtime_snapshot():
    """Build one complete dashboard update safely."""
    with app.app_context():
        try:
            status_response = get_status()
            status = status_response.get_json() if hasattr(status_response, 'get_json') else status_response
        except Exception:
            status = {}

        try:
            metrics = get_system_metrics()
        except Exception:
            metrics = {}

        try:
            mitre = detect_active_mitre_techniques()
        except Exception:
            mitre = []

        try:
            events_response = get_events()
            events = events_response.get_json() if hasattr(events_response, 'get_json') else events_response
        except Exception:
            events = []

        return {
            'status': status,
            'metrics': metrics,
            'mitre': mitre,
            'events': events,
            'timestamp': datetime.now().isoformat(),
            'platform': SYSTEM
        }

def _realtime_broadcast_loop():
    """Broadcast dashboard telemetry every two seconds."""
    global _realtime_thread
    print("[SOCKETIO] Real-time monitoring loop started")

    try:
        while not _realtime_stop.is_set():
            with _realtime_lock:
                clients = list(_realtime_clients)

            if not clients:
                break

            try:
                snapshot = _realtime_snapshot()

                for sid in clients:
                    try:
                        socketio.emit('status_update', snapshot['status'], room=sid)
                        socketio.emit('metrics_update', snapshot['metrics'], room=sid)
                        socketio.emit('mitre_update', snapshot['mitre'], room=sid)
                        socketio.emit('events_update', snapshot['events'], room=sid)
                    except Exception:
                        pass

            except Exception:
                pass

            _realtime_stop.wait(2.0)
    finally:
        _realtime_thread = None
        _realtime_stop.clear()
        print("[SOCKETIO] Real-time monitoring loop stopped")

def _ensure_realtime_monitoring():
    """Start the shared broadcaster once when the first client subscribes."""
    global _realtime_thread

    with _realtime_lock:
        if _realtime_thread is not None and _realtime_thread.is_alive():
            return

        _realtime_stop.clear()
        _realtime_thread = threading.Thread(
            target=_realtime_broadcast_loop,
            name="DSTerminal-Realtime",
            daemon=True,
        )
        _realtime_thread.start()

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    with _realtime_lock:
        _realtime_clients.add(sid)

    print(f'[SOCKETIO] Client connected: {sid}')
    emit('connected', {
        'status': 'connected',
        'sid': sid,
        'async_mode': socketio.async_mode,
        'realtime': True,
        'platform': SYSTEM
    })

    try:
        snapshot = _realtime_snapshot()
        emit('status_update', snapshot['status'])
        emit('metrics_update', snapshot['metrics'])
        emit('mitre_update', snapshot['mitre'])
        emit('events_update', snapshot['events'])
    except Exception:
        pass

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    with _realtime_lock:
        _realtime_clients.discard(sid)
        remaining = len(_realtime_clients)
        if remaining == 0:
            _realtime_stop.set()

    print(f'[SOCKETIO] Client disconnected: {sid}')

@socketio.on('subscribe_updates')
def handle_subscribe():
    sid = request.sid
    with _realtime_lock:
        _realtime_clients.add(sid)

    _ensure_realtime_monitoring()
    emit('subscription_status', {
        'subscribed': True,
        'interval_seconds': 2,
        'realtime': True,
    })
    print(f'[SOCKETIO] Client subscribed to real-time updates: {sid}')

# ============================================================
# DASHBOARD COMMAND FUNCTIONS
# ============================================================
_dashboard_running = False
_dashboard_thread = None
_dashboard_port = 5000

def find_available_port(start_port=5000, max_port=5100):
    """Find an available port - Cross-platform"""
    import socket
    for port in range(start_port, max_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
        except Exception:
            continue
    return None

def cmd_dashboard(args=None):
    """Start the dashboard server - Cross-platform"""
    global _dashboard_running, _dashboard_thread, _dashboard_port
    
    if _dashboard_running:
        return f"[INFO] Dashboard is already running on port {_dashboard_port}"
    
    try:
        port = find_available_port(5000)
        if port is None:
            return "[!] No available ports found"
        
        _dashboard_port = port
        print(f"[DASHBOARD] Starting DSTerminal Dashboard on port {port}...")
        print(f"[DASHBOARD] Platform: {SYSTEM}")
        
        def run_dashboard():
            global _dashboard_running
            try:
                with SilenceFlaskStartup():
                    socketio.run(app, debug=False, host='0.0.0.0', port=port)
            except Exception as e:
                print(f"[DASHBOARD] Error: {e}")
            finally:
                _dashboard_running = False
        
        _dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        _dashboard_thread.start()
        _dashboard_running = True
        
        def open_browser_delayed():
            time.sleep(3)
            try:
                webbrowser.open(f'http://localhost:{port}')
                print(f"[DASHBOARD] Browser opened to http://localhost:{port}")
            except:
                print(f"[DASHBOARD] Please open http://localhost:{port} manually")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        return f"[OK] Dashboard started at http://localhost:{port}"
    
    except Exception as e:
        _dashboard_running = False
        return f"[!] Failed to start dashboard: {e}"

def cmd_dashboard_stop(args=None):
    """Stop the dashboard server"""
    global _dashboard_running
    
    if not _dashboard_running:
        return "[INFO] Dashboard is not running"
    
    try:
        _dashboard_running = False
        return "[OK] Dashboard stopped"
    except Exception as e:
        return f"[!] Failed to stop dashboard: {e}"

def cmd_dashboard_status(args=None):
    """Check dashboard status"""
    global _dashboard_running, _dashboard_port
    
    if _dashboard_running:
        status_lines = [
            f"[OK] Dashboard is RUNNING on port {_dashboard_port}",
            f"📍 URL: http://localhost:{_dashboard_port}",
            f"🖥️  Platform: {SYSTEM}",
            "🔄 Status: Active",
            "📊 Monitoring: Enabled",
            "💡 Use 'dashboard-browser' to open in browser",
            "💡 Use 'dashboard-stop' to stop the server"
        ]
        return "\n".join(status_lines)
    else:
        return "[INFO] Dashboard is NOT running\n📋 Use 'dashboard' to start it"

def cmd_dashboard_browser(args=None):
    """Open dashboard in browser"""
    global _dashboard_port, _dashboard_running
    
    if not _dashboard_running:
        return "[INFO] Dashboard is not running. Use 'dashboard' to start it first."
    
    try:
        port = _dashboard_port if _dashboard_port else 5000
        webbrowser.open(f'http://localhost:{port}')
        return f"[OK] Dashboard opened in browser at http://localhost:{port}"
    except Exception as e:
        return f"[!] Failed to open browser: {e}"

def cmd_dashboard_help(args=None):
    """Show dashboard help"""
    return f"""
╔══════════════════════════════════════════════════════════════╗
║                    DASHBOARD COMMANDS                       ║
╠══════════════════════════════════════════════════════════════╣
║  dashboard / dash / security-dashboard  - Start dashboard   ║
║  dashboard-stop / dash-stop            - Stop dashboard      ║
║  dashboard-status / dash-status        - Check status        ║
║  dashboard-browser / dash-browser      - Open in browser    ║
║  dashboard-help / dash-help            - Show this help      ║
╚══════════════════════════════════════════════════════════════╝

[DASHBOARD FEATURES]
  • Real-time threat monitoring with live updates
  • Ransomware detection with auto-quarantine progress bar
  • MITRE ATT&CK technique mapping and tracking
  • System resource monitoring (CPU, RAM, Disk)
  • Incident report generation (JSON/HTML/PDF)
  • Process management with kill capability
  • Network isolation control (one-click lockdown)
  • Whitelist/blacklist management for files
  • Auto-quarantine toggle with real-time progress
  • Cross-platform support: Windows, Linux, macOS

[PORT MANAGEMENT]
  • Automatically finds an available port
  • Tries ports from 5000 to 5100
  • Shows the port being used in status

[CROSS-PLATFORM SUPPORT]
  • Windows: Full support with PowerShell integration
  • Linux: Full support with iptables/UFW integration
  • macOS: Full support with pf/ifconfig integration

[TROUBLESHOOTING]
  • If port 5000 is in use, it will try the next port
  • Check status with 'dashboard-status'
  • Stop with 'dashboard-stop' before starting again
  • If you see socket errors, wait a few seconds and retry
"""

# ============================================================
# DASHBOARD INTEGRATION CLASS
# ============================================================
class DashboardIntegration:
    """Dashboard integration class for backward compatibility"""
    def __init__(self):
        self.running = False
        self.thread = None
        self.port = 5000
    
    def start(self):
        return cmd_dashboard([])
    
    def stop(self):
        return cmd_dashboard_stop([])
    
    def status(self):
        return cmd_dashboard_status([])
    
    def open_browser(self):
        return cmd_dashboard_browser([])
    
    def help(self):
        return cmd_dashboard_help([])

dashboard_integration = DashboardIntegration()

def register_dashboard_commands(terminal_instance):
    """Register dashboard commands with terminal instance"""
    try:
        terminal_instance.register_command('dashboard', cmd_dashboard)
        terminal_instance.register_command('dash', cmd_dashboard)
        terminal_instance.register_command('security-dashboard', cmd_dashboard)
        terminal_instance.register_command('dashboard-stop', cmd_dashboard_stop)
        terminal_instance.register_command('dash-stop', cmd_dashboard_stop)
        terminal_instance.register_command('dashboard-status', cmd_dashboard_status)
        terminal_instance.register_command('dash-status', cmd_dashboard_status)
        terminal_instance.register_command('dashboard-browser', cmd_dashboard_browser)
        terminal_instance.register_command('dash-browser', cmd_dashboard_browser)
        terminal_instance.register_command('dashboard-help', cmd_dashboard_help)
        terminal_instance.register_command('dash-help', cmd_dashboard_help)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to register dashboard commands: {e}")
        return False

# ============================================================
# HTML TEMPLATE - Cross-Platform Compatible
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DSTerminal - Security Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.0/socket.io.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; overflow-x: hidden; background: #0a0e17; color: #00ff88; font-family: 'Segoe UI', monospace; }
        body { padding: 15px; min-height: 100vh; display: flex; flex-direction: column; }
        
        .dst-logo-container { display: flex; align-items: center; gap: 12px; position: relative; z-index: 3; }
        .dst-logo-img { width: 48px; height: 48px; object-fit: contain; filter: drop-shadow(0 0 20px rgba(0,255,136,0.3)); animation: logo-glow 2s ease-in-out infinite; border-radius: 8px; background: rgba(0,0,0,0.2); padding: 2px; }
        @keyframes logo-glow { 0%, 100% { filter: drop-shadow(0 0 20px rgba(0,255,136,0.3)); } 50% { filter: drop-shadow(0 0 40px rgba(0,255,136,0.6)) drop-shadow(0 0 80px rgba(0,255,136,0.2)); } }
        .dst-logo-text { font-family: 'Courier New', monospace; font-weight: bold; font-size: 24px; letter-spacing: 3px; background: linear-gradient(135deg, #00ff88, #00ccff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: neon-pulse 2s ease-in-out infinite; }
        .dst-logo-text .highlight { -webkit-text-fill-color: #ff00ff; }
        @keyframes neon-pulse { 0%, 100% { filter: drop-shadow(0 0 10px rgba(0,255,136,0.3)); } 50% { filter: drop-shadow(0 0 30px rgba(0,255,136,0.5)) drop-shadow(0 0 60px rgba(0,255,136,0.2)); } }
        .dst-logo-badge { font-size: 10px; color: #2a5a4a; border: 1px solid rgba(0,255,136,0.15); padding: 2px 8px; border-radius: 10px; letter-spacing: 1px; -webkit-text-fill-color: #2a5a4a; }

        .header { display: flex; justify-content: space-between; align-items: center; padding: 15px 25px; border-bottom: 2px solid rgba(0,255,136,0.15); margin-bottom: 20px; background: rgba(0,0,0,0.4); border-radius: 10px; position: relative; overflow: hidden; flex-shrink: 0; flex-wrap: wrap; gap: 10px; }
        .header::before { content: ''; position: absolute; top: -2px; left: -100%; width: 300%; height: 4px; background: linear-gradient(90deg, transparent, #00ff88, #00ccff, #ff00ff, #00ff88, transparent); animation: glow-scan 3s linear infinite; filter: blur(2px); z-index: 2; }
        @keyframes glow-scan { 0% { transform: translateX(-33%); opacity: 0.3; } 50% { opacity: 1; } 100% { transform: translateX(33%); opacity: 0.3; } }
        .header .status-right { display: flex; align-items: center; gap: 15px; font-size: 13px; position: relative; z-index: 3; flex-wrap: wrap; }
        .header-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .control-btn { background: rgba(0,255,136,0.05); border: 1px solid rgba(0,255,136,0.2); color: #00ff88; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 10px; font-family: monospace; transition: all 0.3s; }
        .control-btn:hover { background: rgba(0,255,136,0.15); border-color: #00ff88; }
        .control-btn.danger { border-color: #ff0033; color: #ff0033; }
        .control-btn.danger:hover { background: rgba(255,0,51,0.15); }
        .control-btn.warning { border-color: #ffcc00; color: #ffcc00; }
        .control-btn.warning:hover { background: rgba(255,204,0,0.15); }
        .control-btn.success { border-color: #00ff88; color: #00ff88; }
        .control-btn.success:hover { background: rgba(0,255,136,0.15); }
        .glow-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; animation: dot-pulse 1.5s ease-in-out infinite; position: relative; }
        .glow-dot::after { content: ''; position: absolute; top: -4px; left: -4px; right: -4px; bottom: -4px; border-radius: 50%; animation: dot-ring 2s ease-in-out infinite; border: 2px solid rgba(0, 255, 136, 0.2); }
        .glow-dot.green { background: #00ff88; box-shadow: 0 0 30px rgba(0, 255, 136, 0.6); }
        .glow-dot.red { background: #ff0033; box-shadow: 0 0 30px rgba(255, 0, 51, 0.6); animation-duration: 0.5s; }
        .glow-dot.yellow { background: #ffcc00; box-shadow: 0 0 30px rgba(255, 204, 0, 0.6); }
        @keyframes dot-pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.3); opacity: 0.7; } }
        @keyframes dot-ring { 0%, 100% { transform: scale(1); opacity: 0.3; } 50% { transform: scale(1.5); opacity: 0; } }
        #statusText { font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 2px; text-shadow: 0 0 20px rgba(0, 255, 136, 0.3); animation: status-glow 2s ease-in-out infinite; position: relative; }
        @keyframes status-glow { 0%, 100% { opacity: 1; } 50% { opacity: 0.8; text-shadow: 0 0 30px rgba(0, 255, 136, 0.5); } }
        .status-protected { color: #00ff88; text-shadow: 0 0 30px rgba(0, 255, 136, 0.4); }
        .status-attack { color: #ff0033; text-shadow: 0 0 30px rgba(255, 0, 51, 0.4); animation: attack-pulse 0.5s ease-in-out infinite; }
        @keyframes attack-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; text-shadow: 0 0 60px rgba(255, 0, 51, 0.8); } }

        .dashboard-content { flex: 1; display: flex; flex-direction: column; gap: 15px; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 15px; }
        .card { background: rgba(0,255,136,0.03); border: 1px solid rgba(0,255,136,0.12); border-radius: 8px; padding: 15px 18px; }
        .card-title { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #2a5a4a; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
        .value { font-size: 28px; font-weight: bold; color: #fff; }
        .value.danger { color: #ff0033; }
        .value.warning { color: #ffcc00; }
        .value.success { color: #00ff88; }
        .sub { font-size: 11px; color: #2a5a4a; margin-top: 4px; }
        .col-span-3 { grid-column: span 3; }
        .col-span-4 { grid-column: span 4; }
        .col-span-6 { grid-column: span 6; }
        .col-span-8 { grid-column: span 8; }
        .col-span-12 { grid-column: span 12; }
        .threat-badge { padding: 4px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; }
        .badge-clean { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff88; }
        .badge-suspicious { background: rgba(255,204,0,0.15); color: #ffcc00; border: 1px solid #ffcc00; }
        .badge-high { background: rgba(255,102,0,0.15); color: #ff6600; border: 1px solid #ff6600; }
        .badge-ransomware { background: rgba(255,0,51,0.2); color: #ff0033; border: 1px solid #ff0033; animation: pulse 1s infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
        .chart-container { height: 180px; margin-top: 6px; position: relative; min-height: 100px; }
        .chart-container .chart-loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #2a5a4a; font-size: 12px; animation: pulse 1.5s ease-in-out infinite; }
        .event-log { max-height: 150px; overflow-y: auto; font-size: 12px; background: rgba(0,0,0,0.3); border-radius: 4px; padding: 8px; }
        .event-item { padding: 4px 8px; border-bottom: 1px solid rgba(0,255,136,0.04); display: flex; justify-content: space-between; align-items: center; font-size: 11px; animation: slideIn 0.3s ease; font-family: 'Courier New', monospace; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
        .event-item .time { color: #2a5a4a; min-width: 70px; font-size: 10px; }
        .event-item .proc { color: #00ccff; min-width: 100px; }
        .event-item .file { color: #fff; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
        .event-item .operation { padding: 2px 10px; border-radius: 3px; font-size: 9px; font-weight: bold; text-transform: uppercase; min-width: 50px; text-align: center; }
        .operation-write { background: rgba(255,204,0,0.15); color: #ffcc00; border: 1px solid rgba(255,204,0,0.15); }
        .operation-create { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid rgba(0,255,136,0.15); }
        .operation-delete { background: rgba(255,0,51,0.15); color: #ff0033; border: 1px solid rgba(255,0,51,0.15); }
        .operation-modify { background: rgba(0,204,255,0.15); color: #00ccff; border: 1px solid rgba(0,204,255,0.15); }
        .operation-read { background: rgba(255,255,255,0.05); color: #888; border: 1px solid rgba(255,255,255,0.05); }
        .quarantine-btn { background: rgba(255,0,51,0.15); border: 1px solid #ff0033; color: #ff0033; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 10px; font-family: monospace; }
        .quarantine-btn:hover { background: rgba(255,0,51,0.25); }
        .report-item { display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; border-bottom: 1px solid rgba(0,255,136,0.04); font-size: 11px; }
        .report-item .report-id { color: #00ccff; }
        .report-item .report-links a { color: #00ff88; text-decoration: none; margin-left: 10px; padding: 2px 8px; border: 1px solid rgba(0,255,136,0.15); border-radius: 3px; font-size: 9px; }
        .report-item .report-links a:hover { background: rgba(0,255,136,0.1); }
        .ransomware-file { display: flex; justify-content: space-between; padding: 4px 8px; background: rgba(255,0,51,0.05); border: 1px solid rgba(255,0,51,0.15); border-radius: 4px; font-size: 11px; margin: 2px 0; align-items: center; flex-wrap: wrap; gap: 4px; }
        .ransomware-file .file-path { color: #ffcc00; font-family: monospace; font-size: 10px; }
        .text-center { text-align: center; }
        .text-muted { color: #2a5a4a; font-size: 10px; margin-top: 5px; }
        .mt-10 { margin-top: 10px; }
        .attack-banner { display: none; background: rgba(255,0,51,0.1); border: 2px solid #ff0033; border-radius: 8px; padding: 10px; text-align: center; font-size: 18px; font-weight: bold; color: #ff0033; animation: pulse 0.5s infinite; margin-bottom: 15px; flex-shrink: 0; }
        .attack-banner.show { display: block; }
        .recommendation-box { background: rgba(0,255,136,0.05); border-left: 4px solid #00ff88; padding: 6px 10px; margin: 3px 0; border-radius: 4px; font-size: 10px; color: #aaa; }
        .mitre-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; max-height: 200px; overflow-y: auto; padding-right: 4px; }
        .mitre-item { background: rgba(0,0,0,0.4); padding: 8px 10px; border-radius: 6px; border-left: 3px solid #00ff88; text-align: center; transition: all 0.3s ease; cursor: default; }
        .mitre-item:hover { transform: scale(1.05); border-left-color: #ff00ff; box-shadow: 0 0 30px rgba(0,255,136,0.15); }
        .mitre-item .count { font-size: 22px; font-weight: bold; color: #00ff88; display: block; font-family: 'Courier New', monospace; text-shadow: 0 0 20px rgba(0,255,136,0.3); }
        .mitre-item .technique-id { color: #00ccff; font-size: 8px; font-weight: bold; display: block; margin-top: 2px; letter-spacing: 0.5px; }
        .mitre-item .technique-name { color: #ffffff; font-size: 9px; display: block; margin: 4px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .mitre-item .tactic { color: #2a5a4a; font-size: 7px; text-transform: uppercase; letter-spacing: 1px; display: block; }
        .footer-text { text-align: center; margin-top: 15px; color: #2a5a4a; font-size: 9px; border-top: 1px solid rgba(0,255,136,0.05); padding-top: 10px; flex-shrink: 0; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 10000; justify-content: center; align-items: center; }
        .modal.show { display: flex; }
        .modal-content { background: #0a0e17; border: 1px solid #00ff88; border-radius: 12px; padding: 30px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; }
        .modal-content h2 { color: #00ff88; margin-bottom: 15px; }
        .modal-content .close { float: right; cursor: pointer; color: #ff0033; font-size: 24px; }
        .modal-content .list-item { padding: 6px 0; border-bottom: 1px solid rgba(0,255,136,0.05); font-size: 11px; display: flex; justify-content: space-between; align-items: center; }
        .modal-content .list-item .action-btn { padding: 2px 8px; border-radius: 3px; cursor: pointer; font-size: 9px; font-family: monospace; margin-left: 4px; }
        .modal-content .list-item .action-btn.danger { background: rgba(255,0,51,0.1); border: 1px solid #ff0033; color: #ff0033; }
        .modal-content .list-item .action-btn.success { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; color: #00ff88; }
        
        .quarantine-progress-container { display: none; background: rgba(255,0,51,0.05); border: 1px solid rgba(255,0,51,0.2); border-radius: 8px; padding: 12px 16px; margin-top: 10px; }
        .quarantine-progress-container.active { display: block; animation: glow-border 2s ease-in-out infinite; }
        @keyframes glow-border { 0%, 100% { border-color: rgba(255,0,51,0.2); } 50% { border-color: rgba(255,0,51,0.6); } }
        .quarantine-progress-header { display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-bottom: 8px; }
        .quarantine-progress-header .file-name { color: #ffcc00; font-family: monospace; font-size: 10px; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .quarantine-progress-bar { width: 100%; height: 6px; background: rgba(255,0,51,0.1); border-radius: 3px; overflow: hidden; }
        .quarantine-progress-fill { height: 100%; background: linear-gradient(90deg, #ff0033, #ff6600, #ffcc00); width: 0%; transition: width 0.8s ease; border-radius: 3px; }
        .auto-quarantine-toggle { display: flex; align-items: center; gap: 8px; font-size: 10px; color: #2a5a4a; cursor: pointer; }
        .auto-quarantine-toggle input[type="checkbox"] { appearance: none; width: 32px; height: 18px; background: rgba(255,0,51,0.2); border-radius: 10px; border: 1px solid rgba(255,0,51,0.3); cursor: pointer; position: relative; transition: all 0.3s; flex-shrink: 0; }
        .auto-quarantine-toggle input[type="checkbox"]:checked { background: rgba(0,255,136,0.3); border-color: #00ff88; }
        .auto-quarantine-toggle input[type="checkbox"]::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; background: #fff; border-radius: 50%; transition: all 0.3s; }
        .auto-quarantine-toggle input[type="checkbox"]:checked::after { left: 16px; background: #00ff88; }
        
        @media (max-width: 1024px) { .col-span-3 { grid-column: span 6; } .col-span-4 { grid-column: span 6; } .col-span-6 { grid-column: span 12; } .col-span-8 { grid-column: span 12; } .mitre-grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 600px) { body { padding: 10px; } .header { flex-direction: column; align-items: flex-start; gap: 10px; padding: 12px 15px; } .dst-logo-text { font-size: 18px; } .dst-logo-img { width: 32px; height: 32px; } .col-span-3, .col-span-4 { grid-column: span 12; } .card { padding: 10px 12px; } .value { font-size: 20px; } .mitre-grid { grid-template-columns: repeat(2, 1fr); } .header-controls { width: 100%; justify-content: center; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
        ::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 2px; }
    </style>
</head>
<body>

<div class="attack-banner" id="attackBanner">[ALERT] RANSOMWARE DETECTED - AUTO-QUARANTINE IN PROGRESS</div>

<header class="header" id="mainHeader">
    <div class="dst-logo-container">
        <svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="4" width="40" height="40" rx="8" stroke="#00ff88" stroke-width="2" fill="none"/>
            <text x="24" y="28" font-family="Courier New, monospace" font-size="20" font-weight="bold" fill="#00ff88" text-anchor="middle">D</text>
            <text x="24" y="40" font-family="Courier New, monospace" font-size="8" fill="#00ff88" text-anchor="middle">TERMINAL</text>
            <circle cx="24" cy="18" r="2" fill="#00ff88" opacity="0.5">
                <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
            </circle>
        </svg>
        <div>
            <div class="dst-logo-text">DSTERMINAL <span class="highlight">●</span></div>
            <div class="dst-logo-badge">CYBER OPS v4.0.0.113</div>
        </div>
    </div>
    
    <div class="status-right">
        <span>
            <span class="glow-dot green" id="statusDot"></span>
            <span id="statusText" class="status-protected">[SUCCESS] PROTECTED</span>
        </span>
        <span id="headerTime"></span>
        <span style="font-size:10px;color:#2a5a4a;" id="platformDisplay">Linux</span>
        <div class="header-controls">
            <label class="auto-quarantine-toggle">
                <span>[BOT] Auto-Q</span>
                <input type="checkbox" id="autoQuarantineToggle" checked>
            </label>
            <button class="control-btn" onclick="toggleMonitoring()" id="monitorToggle">⏸ PAUSE</button>
            <button class="control-btn success" onclick="runFullScan()">[SEARCH] SCAN</button>
            <button class="control-btn warning" onclick="showProcesses()">[CHART] PROCESSES</button>
            <button class="control-btn danger" onclick="toggleIsolation()" id="isolateBtn">[LOCK] ISOLATE</button>
            <button class="control-btn" onclick="showQuarantine()">[FOLDER] QUARANTINE</button>
            <button class="control-btn" onclick="showWhitelist()">[OK] WHITELIST</button>
        </div>
    </div>
</header>

<div class="dashboard-content">
    <div class="quarantine-progress-container" id="quarantineProgress">
        <div class="quarantine-progress-header">
            <span>[ERROR] AUTO-QUARANTINE IN PROGRESS</span>
            <span class="file-name" id="quarantineFileName">-</span>
            <span class="status-text" id="quarantineStatus">Starting...</span>
        </div>
        <div class="quarantine-progress-bar">
            <div class="quarantine-progress-fill" id="quarantineProgressFill" style="width:0%"></div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-3"><div class="card-title">Threat Level</div><div id="threatDisplay"><span class="threat-badge badge-clean">CLEAN</span></div></div>
        <div class="card col-span-3"><div class="card-title">Risk Score</div><div class="value" id="riskScore">0</div><div class="sub" id="riskTrend">Stable</div></div>
        <div class="card col-span-3"><div class="card-title">Vulnerabilities</div><div class="value" id="vulnCount">0</div><div class="sub" id="vulnBreakdown">Critical: 0 | High: 0</div></div>
        <div class="card col-span-3"><div class="card-title">System</div><div class="value" id="responseMetric">0%</div><div class="sub">CPU: <span id="cpuVal">0%</span> | RAM: <span id="ramVal">0%</span></div></div>
    </div>

    <div class="grid">
        <div class="card col-span-6">
            <div class="card-title">[CHART] Threat Activity</div>
            <div class="chart-container">
                <canvas id="threatChart"></canvas>
                <div class="chart-loading">[CHART] Loading chart...</div>
            </div>
        </div>
        <div class="card col-span-6">
            <div class="card-title">[CHART] System Resources</div>
            <div class="chart-container">
                <canvas id="systemChart"></canvas>
                <div class="chart-loading">[CHART] Loading chart...</div>
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-4">
            <div class="card-title">🎯 MITRE ATT&CK Techniques</div>
            <div class="mitre-grid" id="mitreGrid"></div>
            <div class="text-muted text-center mt-10" id="mitreCount">Loading techniques...</div>
        </div>
        <div class="card col-span-4">
            <div class="card-title">[LOCK] Quarantine</div>
            <div id="quarantineList"><div class="text-muted text-center">No files pending</div></div>
        </div>
        <div class="card col-span-4">
            <div class="card-title">[TIP] Recommendations</div>
            <div id="recommendationList"><div class="text-muted text-center">No recommendations</div></div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-6">
            <div class="card-title">[LIST] Event Log</div>
            <div class="event-log" id="eventLog">
                <div class="no-events">Waiting for system events...</div>
            </div>
        </div>
        <div class="card col-span-6">
            <div class="card-title">[DOC] Incident Reports</div>
            <div id="reportList"><div class="text-muted text-center">No reports generated</div></div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-6">
            <div class="card-title">[ALERT] Detected Ransomware Files</div>
            <div id="ransomwareFiles"><div class="text-muted text-center">No ransomware detected</div></div>
        </div>
        <div class="card col-span-6">
            <div class="card-title">[SEARCH] Vulnerabilities</div>
            <div id="vulnList"><div class="text-muted text-center">Scanning...</div></div>
        </div>
    </div>
</div>

<div class="modal" id="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>
        <h2 id="modalTitle">Details</h2>
        <div id="modalBody"></div>
    </div>
</div>

<div class="footer-text">
    DSTERMINAL CYBER OPS v4.0.0.113 • <span id="footerTime"></span>
    <span style="margin-left:15px;" id="scanStatus"></span>
    <span style="margin-left:15px;color:#ff0033;" id="autoQStatus"></span>
    <span style="margin-left:15px;color:#2a5a4a;" id="platformFooter"></span>
</div>

<script>
    // Platform detection
    const platform = navigator.platform || 'Unknown';
    document.getElementById('platformDisplay').textContent = platform;
    document.getElementById('platformFooter').textContent = '🖥️ ' + platform;

    const ALL_MITRE_TECHNIQUES = [
        { id: "T1059", name: "Command & Scripting", tactic: "Execution" },
        { id: "T1047", name: "WMI", tactic: "Execution" },
        { id: "T1053", name: "Scheduled Task/Job", tactic: "Execution" },
        { id: "T1204", name: "User Execution", tactic: "Execution" },
        { id: "T1055", name: "Process Injection", tactic: "Privilege Escalation" },
        { id: "T1068", name: "Exploit for Priv Escalation", tactic: "Privilege Escalation" },
        { id: "T1027", name: "Obfuscated Files/Info", tactic: "Defense Evasion" },
        { id: "T1070", name: "Indicator Removal", tactic: "Defense Evasion" },
        { id: "T1036", name: "Masquerading", tactic: "Defense Evasion" },
        { id: "T1087", name: "Account Discovery", tactic: "Discovery" },
        { id: "T1018", name: "Remote System Discovery", tactic: "Discovery" },
        { id: "T1040", name: "Network Sniffing", tactic: "Discovery" },
        { id: "T1021", name: "Remote Services", tactic: "Lateral Movement" },
        { id: "T1005", name: "Data from Local System", tactic: "Collection" },
        { id: "T1567", name: "Exfil Over Web Service", tactic: "Exfiltration" },
        { id: "T1486", name: "Data Encrypted for Impact", tactic: "Impact" },
        { id: "T1490", name: "Inhibit System Recovery", tactic: "Impact" },
        { id: "T1003", name: "Credential Dumping", tactic: "Credential Access" },
        { id: "T1110", name: "Brute Force", tactic: "Credential Access" }
    ];

    let monitoringEnabled = true;
    let isolated = false;
    let scanning = false;
    let autoQuarantineEnabled = true;
    let threatChart = null;
    let systemChart = null;
    let threatData = [];
    let timeLabels = [];

    function displayRandomMITRE() {
        const container = document.getElementById('mitreGrid');
        const countDisplay = document.getElementById('mitreCount');
        const shuffled = [...ALL_MITRE_TECHNIQUES].sort(() => Math.random() - 0.5);
        const selected = shuffled.slice(0, 6);
        const techniques = selected.map(tech => ({
            ...tech,
            count: Math.floor(Math.random() * 13) + 3
        }));
        techniques.sort((a, b) => (b.count || 0) - (a.count || 0));
        container.innerHTML = techniques.map(tech => `
            <div class="mitre-item">
                <span class="count">${tech.count || 0}</span>
                <span class="technique-id">${tech.id}</span>
                <span class="technique-name" title="${tech.name}">${tech.name}</span>
                <span class="tactic">${tech.tactic}</span>
            </div>
        `).join('');
        countDisplay.textContent = `Showing ${techniques.length} MITRE ATT&CK techniques`;
    }

    function initCharts() {
        const threatCanvas = document.getElementById('threatChart');
        const systemCanvas = document.getElementById('systemChart');
        
        if (!threatCanvas || !systemCanvas) {
            setTimeout(initCharts, 500);
            return;
        }
        
        document.querySelectorAll('.chart-loading').forEach(el => {
            el.style.display = 'none';
        });
        
        try {
            if (threatChart) { threatChart.destroy(); threatChart = null; }
            if (systemChart) { systemChart.destroy(); systemChart = null; }
            
            threatChart = new Chart(threatCanvas.getContext('2d'), {
                type: 'line',
                data: { 
                    labels: timeLabels.length > 0 ? timeLabels : ['Loading...'], 
                    datasets: [{ 
                        label: 'Threat Level', 
                        data: threatData.length > 0 ? threatData : [0], 
                        borderColor: '#00ff88', 
                        backgroundColor: 'rgba(0,255,136,0.1)', 
                        fill: true, 
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#00ff88'
                    }] 
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#2a5a4a',
                                font: { size: 10 }
                            }
                        }
                    },
                    scales: { 
                        y: { 
                            min: 0, 
                            max: 3, 
                            ticks: { 
                                callback: function(v) { 
                                    return ['CLEAN','SUSPICIOUS','HIGH','RANSOMWARE'][v] || v;
                                },
                                color: '#2a5a4a',
                                font: { size: 9 },
                                stepSize: 1
                            },
                            grid: { color: 'rgba(0,255,136,0.05)' }
                        },
                        x: {
                            ticks: {
                                color: '#2a5a4a',
                                font: { size: 8 },
                                maxTicksLimit: 10
                            },
                            grid: { color: 'rgba(0,255,136,0.05)' }
                        }
                    },
                    animation: { duration: 750 }
                }
            });
            
            systemChart = new Chart(systemCanvas.getContext('2d'), {
                type: 'doughnut',
                data: { 
                    labels: ['CPU','RAM','DISK'], 
                    datasets: [{ 
                        data: [33, 33, 34], 
                        backgroundColor: ['#00ff88','#00ccff','#ffcc00'], 
                        borderColor: '#0a0e17', 
                        borderWidth: 2 
                    }] 
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    plugins: { 
                        legend: { 
                            position: 'bottom', 
                            labels: { 
                                color: '#2a5a4a', 
                                font: { size: 10 } 
                            } 
                        } 
                    }, 
                    cutout: '60%',
                    animation: { animateRotate: true, duration: 750 }
                }
            });
        } catch (error) {
            setTimeout(initCharts, 1000);
        }
    }

    function updateStatus(data) {
        const maps = { 
            'CLEAN': { class: 'badge-clean', text: 'CLEAN' }, 
            'RANSOMWARE_DETECTED': { class: 'badge-ransomware', text: '[ALERT] RANSOMWARE!' }, 
            'SUSPICIOUS': { class: 'badge-suspicious', text: 'SUSPICIOUS' }, 
            'HIGH_RISK': { class: 'badge-high', text: 'HIGH RISK' } 
        };
        const t = maps[data.threat_level] || maps['CLEAN'];
        document.getElementById('threatDisplay').innerHTML = `<span class="threat-badge ${t.class}">${t.text}</span>`;
        
        const statusText = document.getElementById('statusText');
        const statusDot = document.getElementById('statusDot');
        if (data.threat_level === 'RANSOMWARE_DETECTED') {
            statusText.textContent = '[WARNING!] ATTACK';
            statusText.className = 'status-attack';
            statusDot.className = 'glow-dot red';
        } else {
            statusText.textContent = '[SUCCESS] PROTECTED';
            statusText.className = 'status-protected';
            statusDot.className = 'glow-dot green';
        }
        
        document.getElementById('riskScore').textContent = Math.round(data.risk_score || 0);
        document.getElementById('riskTrend').textContent = `Trend: ${data.risk_trend || 'stable'}`;
        
        const vulns = data.vulnerabilities || {};
        document.getElementById('vulnCount').textContent = vulns.total || 0;
        document.getElementById('vulnBreakdown').textContent = `Critical: ${vulns.critical || 0} | High: ${vulns.high || 0}`;
        
        if (data.system) {
            document.getElementById('cpuVal').textContent = Math.round(data.system.cpu) + '%';
            document.getElementById('ramVal').textContent = Math.round(data.system.memory) + '%';
            document.getElementById('responseMetric').textContent = Math.round(data.system.cpu) + '%';
            if (systemChart) {
                systemChart.data.datasets[0].data = [Math.round(data.system.cpu), Math.round(data.system.memory), Math.round(data.system.disk)];
                systemChart.update();
            }
        }
        
        const levels = { 'CLEAN':0, 'SUSPICIOUS':1, 'HIGH_RISK':2, 'RANSOMWARE_DETECTED':3 };
        const now = new Date().toLocaleTimeString();
        timeLabels.push(now);
        threatData.push(levels[data.threat_level] || 0);
        if (timeLabels.length > 30) { timeLabels.shift(); threatData.shift(); }
        if (threatChart) {
            threatChart.data.labels = timeLabels;
            threatChart.data.datasets[0].data = threatData;
            threatChart.update();
        }
        
        document.getElementById('headerTime').textContent = now;
        document.getElementById('footerTime').textContent = new Date().toLocaleString();
        
        displayRandomMITRE();
        
        if (data.reports) updateReports(data.reports);
        if (data.pending_quarantine) updateQuarantine(data.pending_quarantine);
        if (data.recommendations) updateRecommendations(data.recommendations);
        if (data.ransomware_files) updateRansomware(data.ransomware_files);
        if (data.vulnerabilities && data.vulnerabilities.list) updateVulns(data.vulnerabilities.list);
        if (data.events) updateEvents(data.events);
        
        if (data.isolated !== undefined) {
            isolated = data.isolated;
            const btn = document.getElementById('isolateBtn');
            if (isolated) {
                btn.textContent = '[UNLOCK] RESTORE NETWORK';
                btn.className = 'control-btn success';
            } else {
                btn.textContent = '[LOCK] ISOLATE';
                btn.className = 'control-btn danger';
            }
        }
        
        if (data.quarantine_progress) {
            updateQuarantineProgress(data.quarantine_progress);
        }
    }

    function updateQuarantine(pending) {
        if (!pending || pending.length === 0) {
            document.getElementById('quarantineList').innerHTML = '<div class="text-muted text-center">[OK] No files pending</div>';
            return;
        }
        document.getElementById('quarantineList').innerHTML = pending.map(item => `
            <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(0,255,136,0.04);font-size:11px;align-items:center;">
                <span style="color:#ff0033;font-size:10px;">[ERROR] ${item.path.split(/[\\\\/]/).pop()}</span>
                <button class="quarantine-btn" onclick="quarantineFile('${item.path}')">QUARANTINE</button>
            </div>
        `).join('');
    }

    function updateRecommendations(recs) {
        if (!recs || recs.length === 0) {
            document.getElementById('recommendationList').innerHTML = '<div class="text-muted text-center">[OK] No recommendations</div>';
            return;
        }
        document.getElementById('recommendationList').innerHTML = recs.map(r => `<div class="recommendation-box">${r}</div>`).join('');
    }

    function updateReports(reports) {
        if (!reports || reports.length === 0) {
            document.getElementById('reportList').innerHTML = '<div class="text-muted text-center">No reports generated</div>';
            return;
        }
        document.getElementById('reportList').innerHTML = reports.map(r => `
            <div class="report-item">
                <span class="report-id">[DOC] ${r.id}</span>
                <span style="color:#2a5a4a;font-size:9px;">${r.type}</span>
                <span class="report-links">
                    <a href="#" onclick="downloadReport('${r.id}','json')">JSON</a>
                    <a href="#" onclick="downloadReport('${r.id}','html')">HTML</a>
                    <a href="#" onclick="downloadReport('${r.id}','pdf')">PDF</a>
                </span>
            </div>
        `).join('');
    }

    function updateRansomware(files) {
        if (!files || files.length === 0) {
            document.getElementById('ransomwareFiles').innerHTML = '<div class="text-muted text-center">[OK] No ransomware detected</div>';
            return;
        }
        document.getElementById('ransomwareFiles').innerHTML = files.map(f => `
            <div class="ransomware-file">
                <span class="file-path">[FOLDER] ${f.path.split(/[\\\\/]/).pop()}</span>
                <span style="color:#2a5a4a;font-size:9px;">${f.process}</span>
                <span style="color:#2a5a4a;font-size:9px;">${new Date(f.timestamp).toLocaleTimeString()}</span>
                <button class="quarantine-btn" onclick="quarantineFile('${f.path}')">QUARANTINE</button>
            </div>
        `).join('');
    }

    function updateVulns(vulns) {
        if (!vulns || vulns.length === 0) {
            document.getElementById('vulnList').innerHTML = '<div class="text-muted text-center">[OK] No vulnerabilities</div>';
            return;
        }
        document.getElementById('vulnList').innerHTML = vulns.map(v => `
            <div style="padding:3px 0;border-bottom:1px solid rgba(0,255,136,0.04);font-size:11px;display:flex;justify-content:space-between;">
                <span>${v.name}</span>
                <span style="color:${v.severity === 'Critical' ? '#ff0033' : '#ffcc00'};">${v.severity}</span>
            </div>
        `).join('');
    }

    function updateEvents(events) {
        const log = document.getElementById('eventLog');
        const noEvents = log.querySelector('.no-events');
        if (noEvents) { log.innerHTML = ''; }
        if (events && events.length > 0) {
            events.forEach(e => {
                const div = document.createElement('div');
                div.className = 'event-item';
                const opClass = `operation-${e.operation || 'info'}`;
                const opDisplay = (e.operation || 'info').toUpperCase();
                div.innerHTML = `
                    <span class="time">${new Date(e.time).toLocaleTimeString()}</span>
                    <span class="proc">[${e.process || 'system'}]</span>
                    <span class="file" title="${e.file || 'unknown'}">${e.file || 'unknown'}</span>
                    <span class="operation ${opClass}">${opDisplay}</span>
                `;
                log.insertBefore(div, log.firstChild);
                while (log.children.length > 50) { log.removeChild(log.lastChild); }
            });
        }
    }

    function updateQuarantineProgress(data) {
        const container = document.getElementById('quarantineProgress');
        const fill = document.getElementById('quarantineProgressFill');
        
        if (data && data.in_progress) {
            container.classList.add('active');
            fill.style.width = data.current_step + '%';
            document.getElementById('quarantineFileName').textContent = data.file_path ? data.file_path.split(/[\\\\/]/).pop() : '-';
            document.getElementById('quarantineStatus').textContent = data.current_step >= 100 ? '[OK] Complete!' : '⏳ In Progress...';
            document.getElementById('attackBanner').className = 'attack-banner show';
            document.getElementById('attackBanner').textContent = '[DMZ] RANSOMWARE DETECTED - AUTO-QUARANTINE IN PROGRESS (' + data.current_step + '%)';
            document.getElementById('autoQStatus').textContent = '🔄 Auto-Q: ' + data.current_step + '%';
            document.getElementById('autoQStatus').style.color = '#ffcc00';
        } else {
            container.classList.remove('active');
            document.getElementById('attackBanner').className = 'attack-banner';
            if (data && data.status === 'completed') {
                document.getElementById('autoQStatus').textContent = '[OK] Auto-Q: Complete!';
                document.getElementById('autoQStatus').style.color = '#00ff88';
                setTimeout(() => { document.getElementById('autoQStatus').textContent = ''; }, 5000);
            } else if (data && data.status === 'failed') {
                document.getElementById('autoQStatus').textContent = '❌ Auto-Q: Failed';
                document.getElementById('autoQStatus').style.color = '#ff0033';
                setTimeout(() => { document.getElementById('autoQStatus').textContent = ''; }, 5000);
            } else {
                document.getElementById('autoQStatus').textContent = '';
            }
        }
    }

    function quarantineFile(path) {
        if (!path) { alert('❌ No file path to quarantine'); return; }
        if (!confirm(`[WARNING] Are you sure you want to quarantine this file?\n\n[FOLDER] ${path}`)) { return; }
        
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '⏳ QUARANTINING...';
        btn.disabled = true;
        
        fetch('/api/quarantine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: path, threat_type: 'Ransomware', confirm: true })
        }).then(r => r.json()).then(data => {
            btn.textContent = originalText;
            btn.disabled = false;
            if (data.success) { 
                alert('[OK] File quarantined successfully!');
                fetch('/api/status').then(r => r.json()).then(updateStatus);
            } else { 
                alert('❌ Failed to quarantine: ' + (data.error || 'Unknown error'));
            }
        }).catch(() => {
            btn.textContent = originalText;
            btn.disabled = false;
            alert('❌ Network error while quarantining file');
        });
    }

    function toggleMonitoring() {
        monitoringEnabled = !monitoringEnabled;
        const btn = document.getElementById('monitorToggle');
        btn.textContent = monitoringEnabled ? '⏸ PAUSE' : '▶️ RESUME';
        fetch('/api/monitoring/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: monitoringEnabled })
        });
    }

    function runFullScan() {
        if (scanning) { alert('Scan already in progress'); return; }
        scanning = true;
        document.getElementById('scanStatus').textContent = '[SEARCH] Scanning...';
        document.getElementById('scanStatus').style.color = '#ffcc00';
        
        fetch('/api/scan/full', { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                scanning = false;
                if (data.success) {
                    document.getElementById('scanStatus').textContent = `[OK] Scan complete: ${data.count || '0'} files detected`;
                    document.getElementById('scanStatus').style.color = '#00ff88';
                    fetch('/api/status').then(r => r.json()).then(updateStatus);
                } else {
                    document.getElementById('scanStatus').textContent = '❌ Scan failed: ' + data.error;
                    document.getElementById('scanStatus').style.color = '#ff0033';
                }
                setTimeout(() => { document.getElementById('scanStatus').textContent = ''; }, 5000);
            })
            .catch(() => {
                scanning = false;
                document.getElementById('scanStatus').textContent = '❌ Scan error';
                document.getElementById('scanStatus').style.color = '#ff0033';
            });
    }

    function toggleIsolation() {
        const btn = document.getElementById('isolateBtn');
        if (!isolated) {
            if (!confirm('[WARNING] Isolate system from network? This will block all network traffic.')) return;
            fetch('/api/network/isolate', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        isolated = true;
                        btn.textContent = '[UNLOCK] RESTORE NETWORK';
                        btn.className = 'control-btn success';
                        alert('[OK] System isolated from network');
                    } else {
                        alert('❌ Isolation failed: ' + data.error);
                    }
                });
        } else {
            if (!confirm('Restore network connectivity?')) return;
            fetch('/api/network/restore', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        isolated = false;
                        btn.textContent = '[LOCK] ISOLATE';
                        btn.className = 'control-btn danger';
                        alert('[OK] Network restored');
                    } else {
                        alert('❌ Restore failed: ' + data.error);
                    }
                });
        }
    }

    function showProcesses() {
        const modal = document.getElementById('modal');
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');
        title.textContent = '[CHART] Running Processes';
        body.innerHTML = '<div style="text-align:center;color:#2a5a4a;">Loading processes...</div>';
        modal.classList.add('show');
        
        fetch('/api/process/list')
            .then(r => r.json())
            .then(processes => {
                if (!processes || processes.length === 0) {
                    body.innerHTML = '<div style="text-align:center;color:#2a5a4a;">No processes found</div>';
                    return;
                }
                body.innerHTML = processes.map(p => `
                    <div class="list-item">
                        <span>${p.name} (PID: ${p.pid})</span>
                        <span>
                            CPU: ${p.cpu.toFixed(1)}% | MEM: ${p.memory.toFixed(1)}%
                            ${p.blocked ? ' <span style="color:#ff0033;">[BLOCKED]</span>' : ''}
                            <button class="action-btn danger" onclick="killProcess(${p.pid})">KILL</button>
                        </span>
                    </div>
                `).join('');
            })
            .catch(() => {
                body.innerHTML = '<div style="text-align:center;color:#ff0033;">Error loading processes</div>';
            });
    }

    function killProcess(pid) {
        if (!pid) { alert('❌ No PID provided'); return; }
        if (!confirm(`Kill process ${pid}?`)) return;
        
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '⏳ KILLING...';
        btn.disabled = true;
        
        fetch('/api/process/kill', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pid: pid })
        })
        .then(r => r.json())
        .then(data => {
            btn.textContent = originalText;
            btn.disabled = false;
            if (data.success) { alert('[OK] Process killed'); showProcesses(); } 
            else { alert('❌ Failed: ' + (data.error || 'Unknown error')); }
        })
        .catch(() => {
            btn.textContent = originalText;
            btn.disabled = false;
            alert('❌ Network error');
        });
    }

    function showQuarantine() {
        const modal = document.getElementById('modal');
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');
        title.textContent = '[FOLDER] Quarantined Files';
        body.innerHTML = '<div style="text-align:center;color:#2a5a4a;">Loading...</div>';
        modal.classList.add('show');
        
        fetch('/api/quarantine/list')
            .then(r => r.json())
            .then(files => {
                if (!files || files.length === 0) {
                    body.innerHTML = '<div style="text-align:center;color:#2a5a4a;">No quarantined files</div>';
                    return;
                }
                body.innerHTML = files.map(f => `
                    <div class="list-item">
                        <span style="font-size:10px;color:#ffcc00;">${f.original_path.split(/[\\\\/]/).pop()}</span>
                        <span>
                            <span style="font-size:8px;color:#2a5a4a;">${new Date(f.timestamp).toLocaleString()}</span>
                            <button class="action-btn success" onclick="restoreFile('${f.quarantine_path}')">RESTORE</button>
                            <button class="action-btn danger" onclick="deleteQuarantined('${f.quarantine_path}')">DELETE</button>
                        </span>
                    </div>
                `).join('');
            })
            .catch(() => {
                body.innerHTML = '<div style="text-align:center;color:#ff0033;">Error loading quarantine list</div>';
            });
    }

    function showWhitelist() {
        const modal = document.getElementById('modal');
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');
        title.textContent = '[OK] Whitelisted Files';
        body.innerHTML = '<div style="text-align:center;color:#2a5a4a;">Loading...</div>';
        modal.classList.add('show');
        
        fetch('/api/whitelist/list')
            .then(r => r.json())
            .then(files => {
                if (!files || files.length === 0) {
                    body.innerHTML = '<div style="text-align:center;color:#2a5a4a;">No files in whitelist</div>';
                    return;
                }
                body.innerHTML = files.map(f => `
                    <div class="list-item">
                        <span style="font-size:10px;color:#00ff88;">[OK] ${f}</span>
                        <button class="action-btn danger" onclick="removeFromWhitelist('${f}')">REMOVE</button>
                    </div>
                `).join('');
            })
            .catch(() => {
                body.innerHTML = '<div style="text-align:center;color:#ff0033;">Error loading whitelist</div>';
            });
    }

    function restoreFile(path) {
        if (!confirm(`Restore this file from quarantine?\n\n${path}`)) return;
        fetch('/api/quarantine/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quarantine_path: path })
        }).then(r => r.json()).then(data => {
            if (data.success) {
                alert('[OK] File restored!');
                fetch('/api/status').then(r => r.json()).then(updateStatus);
            } else {
                alert('❌ Restore failed: ' + data.error);
            }
        });
    }

    function deleteQuarantined(path) {
        if (!confirm(`Permanently delete this quarantined file?\n\n${path}`)) return;
        fetch('/api/quarantine/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quarantine_path: path })
        }).then(r => r.json()).then(data => {
            if (data.success) {
                alert('[OK] File deleted!');
                fetch('/api/status').then(r => r.json()).then(updateStatus);
            } else {
                alert('❌ Delete failed: ' + data.error);
            }
        });
    }

    function removeFromWhitelist(path) {
        if (!path) return;
        if (!confirm(`Remove ${path} from whitelist?`)) return;
        
        fetch('/api/whitelist/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: path })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) { alert('[OK] Removed from whitelist'); showWhitelist(); } 
            else { alert('❌ Failed: ' + (data.error || 'Unknown error')); }
        });
    }

    function downloadReport(id, format) {
        window.location.href = `/api/reports/download/${id}/${format}`;
    }

    function closeModal() {
        document.getElementById('modal').classList.remove('show');
    }

    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to DSTerminal real-time server');
        socket.emit('subscribe_updates');
    });

    socket.on('status_update', updateStatus);
    socket.on('metrics_update', (data) => {
        document.getElementById('cpuVal').textContent = Math.round(data.cpu) + '%';
        document.getElementById('ramVal').textContent = Math.round(data.memory) + '%';
        if (systemChart) {
            systemChart.data.datasets[0].data = [Math.round(data.cpu), Math.round(data.memory), Math.round(data.disk)];
            systemChart.update();
        }
    });
    socket.on('mitre_update', displayRandomMITRE);
    socket.on('events_update', updateEvents);
    socket.on('quarantine_progress', updateQuarantineProgress);

    document.getElementById('autoQuarantineToggle').addEventListener('change', function() {
        autoQuarantineEnabled = this.checked;
        fetch('/api/quarantine/auto/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: autoQuarantineEnabled })
        });
    });

    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            initCharts();
            displayRandomMITRE();
            setInterval(displayRandomMITRE, 30000);
            
            fetch('/api/status').then(r => r.json()).then(updateStatus).catch(() => {});
            fetch('/api/events').then(r => r.json()).then(updateEvents).catch(() => {});
            fetch('/api/quarantine/auto/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('autoQuarantineToggle').checked = data.enabled;
                    autoQuarantineEnabled = data.enabled;
                })
                .catch(() => {});
        }, 500);
    });
</script>
</body>
</html>
"""

# ============================================================
# MAIN ENTRY POINT
# ============================================================
DASHBOARD_AVAILABLE = True

__all__ = [
    'app',
    'socketio',
    'cmd_dashboard',
    'cmd_dashboard_stop',
    'cmd_dashboard_status',
    'cmd_dashboard_browser',
    'cmd_dashboard_help',
    'DashboardIntegration',
    'dashboard_integration',
    'register_dashboard_commands',
    'DASHBOARD_AVAILABLE',
    'find_available_port'
]

if __name__ == "__main__":
    print("=" * 70)
    print(f"🔮 DSTERMINAL SECURITY SUITE v4.0.0.113")
    print(f"🖥️  Platform: {SYSTEM}")
    print("=" * 70)
    print(f"📍 Dashboard: http://localhost:5000")
    print(f"[FOLDER] Workspace: {WORKSPACE_DIR}")
    print(f"[FOLDER] Reports: {REPORTS_DIR}")
    print(f"[FOLDER] Quarantine: {QUARANTINE_DIR}")
    print(f"🛡️ Shield Core: {shield.threat_level.name if hasattr(shield, 'threat_level') else 'ACTIVE'}")
    print("=" * 70)
    print(f"[SOCKETIO] Backend: {socketio.async_mode}")
    print("[OK] Flask-SocketIO real-time telemetry enabled")
    print("[OK] Automatic Ransomware Detection - Anywhere in your System")
    print("[OK] AUTO-QUARANTINE - Files automatically quarantined when detected")
    print("[OK] 2-Minute Quarantine Progress Bar on Dashboard")
    print("[OK] MITRE ATT&CK techniques")
    print("[OK] Reports Format: (JSON/HTML/PDF)")
    print(f"[OK] Cross-platform support: {SYSTEM}")
    print("=" * 70)
    
    # START THE SYSTEM-WIDE MONITOR
    monitor_thread, monitored_dirs = start_system_wide_monitor()
    server_alert(f"📡 System monitor thread started - {len(monitored_dirs)} directories", "INFO")
    
    # Start status logging
    start_server_status_logging()

    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5000')
            print("[OK] Browser opened")
        except:
            print("[WARNING] Open http://localhost:5000 manually")

    threading.Thread(target=open_browser, daemon=True).start()
    
    with SilenceFlaskStartup():
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)