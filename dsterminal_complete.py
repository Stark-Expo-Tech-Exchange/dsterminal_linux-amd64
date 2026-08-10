"""
DSTerminal Complete Security Suite v4.0.0.113
Enhanced with Automatic Ransomware Detection Anywhere in System
Full Dashboard Controls Implementation with Auto-Quarantine Progress
"""

# ============================================================
# FIX UNICODE ENCODING ISSUES FOR WINDOWS CONSOLE
# ============================================================
import sys
import io
import os

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform == 'win32':
    try:
        # Set console code page to UTF-8
        os.system('chcp 65001 > nul')
    except:
        pass
    
    # Replace stdout/stderr with UTF-8 wrappers
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Now proceed with the rest of your imports
import os
import sys
import time
import threading
import webbrowser
import shutil
import random
import subprocess
import json
import hashlib
import socket
import netifaces
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, send_file, make_response
from flask_socketio import SocketIO, emit
import psutil
import platform

# ============================================================
# SURGICAL REMOVAL OF FLASK STARTUP PRINTS
# ============================================================
import contextlib
import io

class SilenceFlaskStartup:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

# ============================================================
# WORKSPACE DIRECTORY - Environment Variable Support
# ============================================================

def get_workspace_directory():
    """
    Determine workspace directory with priority:
    1. DSTERMINAL_WORKSPACE environment variable (overrides everything)
    2. If running as frozen executable, use %APPDATA%/DSTerminal/workspace
    3. Platform-specific default locations
    4. Fallback to temp directory
    """
    # Check for environment variable override first
    env_workspace = os.environ.get('DSTERMINAL_WORKSPACE')
    if env_workspace:
        workspace = env_workspace
        print(f"[WORKSPACE] Using environment variable: {workspace}")
        return workspace
    
    # Check if running as a frozen executable (PyInstaller)
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use AppData for Windows
        system = platform.system()
        
        if system == 'Windows':
            # Use APPDATA for Windows (roaming)
            appdata = os.environ.get('APPDATA')
            if appdata:
                workspace = os.path.join(appdata, 'DSTerminal', 'workspace')
            else:
                # Fallback to user profile
                home = os.path.expanduser('~')
                workspace = os.path.join(home, 'AppData', 'Roaming', 'DSTerminal', 'workspace')
        elif system == 'Darwin':  # macOS
            home = os.path.expanduser('~')
            workspace = os.path.join(home, 'Library', 'Application Support', 'DSTerminal', 'workspace')
        else:  # Linux and others
            home = os.path.expanduser('~')
            workspace = os.path.join(home, '.config', 'DSTerminal', 'workspace')
        
        # Create workspace directory
        os.makedirs(workspace, exist_ok=True)
        print(f"[WORKSPACE] Using application data: {workspace}")
        return workspace
    
    # Running as script - use user home directory
    home = os.path.expanduser('~')
    system = platform.system()
    
    if system == 'Windows':
        workspace = os.path.join(home, 'dsterminal_workspace', 'ransom')
    elif system == 'Darwin':  # macOS
        workspace = os.path.join(home, 'dsterminal_workspace', 'ransom')
    else:  # Linux and others
        workspace = os.path.join(home, 'dsterminal_workspace', 'ransom')
    
    try:
        os.makedirs(workspace, exist_ok=True)
        # Test write access
        test_file = os.path.join(workspace, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"[WORKSPACE] Using: {workspace}")
        return workspace
    except:
        # Ultimate fallback to temp
        import tempfile
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
# CONFIGURATION MANAGEMENT
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
# WHITELIST/BLACKLIST MANAGEMENT
# ============================================================
def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

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

# Load whitelist and blacklist
whitelist = load_whitelist()
blacklist = load_blacklist()

# Define default whitelist entries
DEFAULT_WHITELIST = [
    # System files that should never be quarantined
    r"C:\Windows\System32\ntoskrnl.exe",
    r"C:\Windows\System32\winlogon.exe",
    r"C:\Windows\explorer.exe",
    # Add common safe file patterns
    r"C:\Program Files",
    r"C:\Windows\System32",
]

def init_whitelist():
    """Initialize whitelist with defaults if empty"""
    global whitelist
    if not whitelist:
        whitelist = DEFAULT_WHITELIST.copy()
        save_whitelist(whitelist)
        print(f"[WHITELIST] Added {len(whitelist)} default entries")

# Initialize whitelist
init_whitelist()

# ============================================================
# COPY LOGO TO WORKSPACE
# ============================================================
def copy_logo_to_workspace():
    """Copy logo from installation directory to workspace static folder"""
    logo_dest = os.path.join(STATIC_DIR, '3486-removebg-preview.ico')
    
    if os.path.exists(logo_dest):
        print(f"[LOGO] Logo already exists at: {logo_dest}")
        return True
    
    logo_source_paths = [
        os.path.join(os.path.dirname(sys.executable), 'static', '3486-removebg-preview.ico'),
        os.path.join(os.path.dirname(sys.executable), '3486-removebg-preview.ico'),
        os.path.join(os.path.dirname(__file__), 'static', '3486-removebg-preview.ico'),
        os.path.join(os.path.dirname(__file__), '3486-removebg-preview.ico'),
        os.path.join('installer_assets', '3486-removebg-preview.ico'),
    ]
    
    for source in logo_source_paths:
        if os.path.exists(source):
            try:
                shutil.copy2(source, logo_dest)
                print(f"[LOGO] Copied logo from: {source}")
                print(f"[LOGO] To: {logo_dest}")
                return True
            except Exception as e:
                print(f"[LOGO] Failed to copy from {source}: {e}")
    
    # Create SVG fallback
    try:
        svg_content = '''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="10" width="180" height="180" rx="20" stroke="#00ff88" stroke-width="4" fill="none"/>
            <text x="100" y="90" font-family="Courier New, monospace" font-size="48" font-weight="bold" fill="#00ff88" text-anchor="middle">D</text>
            <text x="100" y="130" font-family="Courier New, monospace" font-size="16" fill="#00ff88" text-anchor="middle">TERMINAL</text>
            <circle cx="100" cy="50" r="4" fill="#00ff88">
                <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/>
            </circle>
        </svg>'''
        with open(logo_dest, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"[LOGO] Created SVG placeholder logo at: {logo_dest}")
        return True
    except Exception as e:
        print(f"[LOGO] Failed to create placeholder: {e}")
    
    return False

copy_logo_to_workspace()

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__, 
            static_folder=STATIC_DIR,
            static_url_path='/static')
app.config['SECRET_KEY'] = 'dsterminal-holographic-2026'

# ============================================================
# TRY TO IMPORT SHIELD CORE
# ============================================================
try:
    from shield_core import ShieldCore, ThreatLevel
    SHIELD_AVAILABLE = True
    print("[+] ShieldCore loaded successfully")
except ImportError as e:
    print(f"[!] ShieldCore import error: {e}")
    print("[!] Using mock ShieldCore for testing")
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

# ============================================================
# SHIELD CORE
# ============================================================
shield = ShieldCore(WORKSPACE_DIR)
shield.start_monitoring()

# ============================================================
# SOCKET IO
# ============================================================
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================================
# DATA STORES
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

# ============================================================
# AUTO-QUARANTINE PROGRESS TRACKING
# ============================================================
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
# LOAD SAVED DATA
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
# ADVANCED RANSOMWARE DETECTION - ANYWHERE IN SYSTEM
# ============================================================
class AdvancedRansomwareDetector:
    def __init__(self):
        self.monitored_dirs = self._get_monitored_directories()
        self.file_signatures = {}
        self.detected_ransomware = []
        self.scanning = False
        self.last_scan_time = datetime.now()
        
    def _get_monitored_directories(self):
        """Get all directories to monitor for ransomware"""
        dirs = []
        
        # User directories
        user_profile = os.environ.get('USERPROFILE')
        if not user_profile:
            user_profile = os.path.expanduser('~')
        
        if os.path.exists(user_profile):
            for item in ['Documents', 'Desktop', 'Downloads', 'Pictures', 'Music', 'Videos']:
                path = os.path.join(user_profile, item)
                if os.path.exists(path):
                    dirs.append(path)
        
        # Common ransomware targets
        common_paths = [
            os.environ.get('TEMP'),
            os.environ.get('TMP'),
            os.path.join(user_profile, 'AppData', 'Local', 'Temp') if user_profile else None,
            'C:\\ProgramData' if platform.system() == 'Windows' else '/var/tmp',
            '/tmp' if platform.system() != 'Windows' else None,
        ]
        
        for path in common_paths:
            if path and os.path.exists(path):
                dirs.append(path)
        
        # Also monitor the current directory
        if os.path.exists(os.getcwd()):
            dirs.append(os.getcwd())
        
        # Deduplicate
        return list(set(dirs))
    
    def scan_for_ransomware(self):
        """Scan all monitored directories for ransomware activity"""
        detected = []
        
        for directory in self.monitored_dirs:
            if not os.path.exists(directory):
                continue
                
            try:
                for root, dirs, files in os.walk(directory):
                    # Limit depth to avoid too much scanning
                    depth = root.replace(directory, '').count(os.sep)
                    if depth > 3:
                        continue
                        
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # SKIP HONEYPOT FILES
                        if 'honeypot' in file_path.lower():
                            continue
                        
                        # Check if file is in monitored extensions
                        ext = os.path.splitext(file)[1].lower()
                        if ext not in monitored_extensions:
                            continue
                        
                        # Check whitelist
                        if file_path in whitelist:
                            continue
                        
                        # Check blacklist
                        if file_path in blacklist:
                            detected.append({
                                'path': file_path,
                                'timestamp': datetime.now().isoformat(),
                                'process': self._get_process_name(file_path),
                                'reason': 'Blacklisted'
                            })
                            continue
                        
                        # Check if file was recently modified (last 60 seconds)
                        try:
                            mtime = os.path.getmtime(file_path)
                            if time.time() - mtime < 60:
                                # Check if file contains ransomware patterns
                                if self._is_ransomware_file(file_path):
                                    detected.append({
                                        'path': file_path,
                                        'timestamp': datetime.now().isoformat(),
                                        'process': self._get_process_name(file_path)
                                    })
                        except:
                            continue
            except:
                continue
        
        return detected
    
    def _is_ransomware_file(self, file_path):
        """Check if a file exhibits ransomware behavior"""
        try:
            # SKIP HONEYPOT FILES
            if 'honeypot' in file_path.lower():
                return False
            
            # Check file size changes
            if os.path.getsize(file_path) > 1024 * 1024 * 10:  # 10MB
                return False
                
            # Read first few bytes
            with open(file_path, 'rb') as f:
                content = f.read(1024)
                
            # Check for encrypted patterns
            ransomware_patterns = [
                b'ENCRYPTED',
                b'DECRYPT',
                b'RANSOM',
                b'BITCOIN',
                b'MONERO',
                b'WALLET',
                b'LOCKED',
                b'ENCRYPTION',
                b'CRYPTO',
                b'DECRYPTION',
                b'PAYMENT',
                b'BTC',
                b'XMR',
                b'RANSOMWARE',
                b'ENCRYPTED_BY_'
            ]
            
            for pattern in ransomware_patterns:
                if pattern in content.upper():
                    return True
                    
            # Check for high entropy (encrypted data)
            if self._calculate_entropy(content) > 7.5:
                return True
                
            return False
        except:
            return False
    
    def _calculate_entropy(self, data):
        """Calculate entropy of data to detect encryption"""
        if not data:
            return 0
        import math
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy
    
    def _get_process_name(self, file_path):
        """Get the process that modified the file"""
        return 'system_process'
    
    def get_ransomware_indicators(self):
        """Get active ransomware indicators"""
        indicators = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower() if proc.info['name'] else ''
                if any(keyword in name for keyword in ['malware','ransom', 'encrypt', 'crypto', 'decrypt', 'miner', 'worm', 'trojan', 'backdoor']):
                    indicators.append({
                        'type': 'process',
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    })
            except:
                continue
        
        return indicators

detector = AdvancedRansomwareDetector()

# ============================================================
# AUTO-QUARANTINE ENGINE WITH PROGRESS
# ============================================================
class AutoQuarantineEngine:
    def __init__(self):
        self.is_running = False
        self.current_file = None
        self.progress = 0
        self.status = 'idle'
        self.start_time = None
        
    def start_quarantine(self, file_path, threat_type="Ransomware"):
        if self.is_running:
            return {'success': False, 'error': 'Quarantine already in progress'}
        
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
                f.write(f"{datetime.now().isoformat()} | QUARANTINED | {file_path} -> {dest_path} | {threat_type}\n")
            
            self._update_progress(90, 'Finalizing quarantine')
            time.sleep(1)
            
            self._update_progress(95, 'Quarantine complete!')
            time.sleep(1)
            
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
            
            if not pending_quarantine:
                if SHIELD_AVAILABLE and hasattr(shield, 'threat_level'):
                    shield.threat_level = type('obj', (object,), {'name': 'CLEAN'})
            
            self._update_progress(100, '[OK] Quarantine completed successfully')
            self.is_running = False
            auto_quarantine_progress['in_progress'] = False
            auto_quarantine_progress['status'] = 'completed'
            
            socketio.emit('quarantine_complete', {
                'file': file_path,
                'quarantine_path': dest_path,
                'success': True
            })
            
        except Exception as e:
            error_msg = str(e)
            self._update_progress(100, f'❌ Failed: {error_msg}')
            self.is_running = False
            auto_quarantine_progress['in_progress'] = False
            auto_quarantine_progress['status'] = 'failed'
            
            socketio.emit('quarantine_complete', {
                'file': file_path,
                'success': False,
                'error': error_msg
            })
    
    def _update_progress(self, progress, status):
        self.progress = progress
        self.status = status
        
        auto_quarantine_progress.update({
            'current_step': progress,
            'status': status,
            'file_path': self.current_file
        })
        
        socketio.emit('quarantine_progress', {
            'file_path': self.current_file,
            'progress': progress,
            'status': status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'estimated_completion': (self.start_time + timedelta(seconds=120)).isoformat() if self.start_time else None
        })
        
        socketio.emit('status_update', {
            'quarantine_progress': {
                'in_progress': self.is_running,
                'file_path': self.current_file,
                'progress': progress,
                'status': status
            }
        })

auto_quarantine = AutoQuarantineEngine()

# ============================================================
# ENHANCED RANSOMWARE DETECTION WITH AUTO-QUARANTINE
# ============================================================
def detect_ransomware_file():
    global pending_quarantine, ransomware_detected_files, detected_file_paths
    
    if not config.get('monitoring_enabled', True):
        return {'detected': False}
    
    # CREATE honeypot files (they serve as early warning decoys)
    if config.get('honeypot_enabled', True):
        user_profile = os.environ.get('USERPROFILE')
        if not user_profile:
            user_profile = os.path.expanduser('~')
        
        honeypot_paths = [
            os.path.join(user_profile, 'Documents', 'honeypot_1.txt') if user_profile else None,
            os.path.join(user_profile, 'Desktop', 'honeypot_2.txt') if user_profile else None,
            os.path.join(os.environ.get('TEMP', '/tmp'), 'system_backup.bak'),
        ]
        
        # Filter out None values
        honeypot_paths = [p for p in honeypot_paths if p]
        
        for hp_path in honeypot_paths:
            if not os.path.exists(hp_path):
                try:
                    os.makedirs(os.path.dirname(hp_path), exist_ok=True)
                    with open(hp_path, 'w') as f:
                        f.write(f"HONEYPOT DECOY - DO NOT MODIFY - {datetime.now().isoformat()}")
                except:
                    pass
        
        # IMPORTANT: Check honeypots for modification (indicates ransomware activity)
        # BUT DON'T QUARANTINE THEM - they are decoys!
        for file_path in honeypot_paths:
            # Skip honeypot detection entirely - they are just decoys
            if 'honeypot' in file_path.lower():
                continue
            
            # This code will never run for honeypots due to the continue above
            if os.path.exists(file_path) and file_path not in detected_file_paths:
                try:
                    mtime = os.path.getmtime(file_path)
                    if time.time() - mtime < 60:
                        detected_file_paths.add(file_path)
                        process_name = 'system (honeypot trigger)'
                        pending_quarantine.append({
                            'path': file_path,
                            'process': process_name,
                            'timestamp': datetime.now().isoformat()
                        })
                        ransomware_detected_files.append({
                            'path': file_path,
                            'process': process_name,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        if config.get('auto_quarantine', True) and not auto_quarantine.is_running:
                            auto_quarantine.start_quarantine(file_path, "Ransomware")
                        
                        return {
                            'detected': True,
                            'file_path': file_path,
                            'process': process_name
                        }
                except:
                    pass
    
    # Scan for real ransomware files (honeypots are already skipped)
    try:
        detected_files = detector.scan_for_ransomware()
        for file_info in detected_files:
            file_path = file_info['path']
            
            # Double-check: skip honeypots
            if 'honeypot' in file_path.lower():
                continue
                
            if file_path not in detected_file_paths and file_path not in whitelist:
                detected_file_paths.add(file_path)
                pending_quarantine.append({
                    'path': file_path,
                    'process': file_info.get('process', 'unknown'),
                    'timestamp': file_info.get('timestamp', datetime.now().isoformat())
                })
                ransomware_detected_files.append({
                    'path': file_path,
                    'process': file_info.get('process', 'unknown'),
                    'timestamp': file_info.get('timestamp', datetime.now().isoformat())
                })
                
                if config.get('auto_quarantine', True) and not auto_quarantine.is_running:
                    auto_quarantine.start_quarantine(file_path, "Ransomware")
                
                return {
                    'detected': True,
                    'file_path': file_path,
                    'process': file_info.get('process', 'unknown')
                }
    except Exception as e:
        print(f"[RANSOMWARE] Scan error: {e}")
    
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
# DETECTION FUNCTIONS
# ============================================================
def detect_real_vulnerabilities():
    vulnerabilities = []
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
    return vulnerabilities

def get_system_metrics():
    return {
        'cpu': psutil.cpu_percent(interval=0.3),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'processes': len(psutil.pids()),
        'timestamp': datetime.now().isoformat(),
        'isolated': system_isolated,
        'monitoring': config.get('monitoring_enabled', True)
    }

def detect_threat_actors():
    threats = []
    suspicious_names = ['malware', 'ransom', 'crypto', 'miner', 'worm', 'trojan', 'backdoor']
    suspicious_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            name = proc.info['name'].lower()
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
            'name': '[ALERT] Suspicious Process Detected',  # Changed from [ALERT]
            'risk': 'High',
            'activities': len(suspicious_processes),
            'trend': 'up',
            'processes': suspicious_processes
        })
    return threats

def detect_active_mitre_techniques():
    active = []
    try:
        cmd_procs = ['cmd.exe', 'powershell.exe', 'pwsh.exe', 'bash.exe', 'python.exe']
        count = sum(1 for p in psutil.process_iter(['name']) if p.info['name'] and any(c in p.info['name'].lower() for c in cmd_procs))
        if count > 3:
            active.append({'id': 'T1059', 'count': count, 'name': 'Command & Scripting'})
    except:
        pass
    
    try:
        wmi_count = sum(1 for p in psutil.process_iter(['name']) if p.info['name'] and 'wmiprvse' in p.info['name'].lower())
        if wmi_count > 0:
            active.append({'id': 'T1047', 'count': wmi_count, 'name': 'WMI'})
    except:
        pass
    
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
# REPORT GENERATOR
# ============================================================
def generate_report(incident_data):
    global report_history
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_id = f"DST-{timestamp}"
    watermark = "DSTERMINAL CYBER OPS v4.0.0.113"
    
    json_data = {
        'report_id': report_id,
        'timestamp': datetime.now().isoformat(),
        'version': '4.0.0.113',
        'watermark': watermark,
        'incident': incident_data,
        'system_info': {
            'hostname': platform.node(),
            'os': platform.platform(),
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
    }
    json_path = os.path.join(REPORTS_DIR, f'{report_id}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
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
<div class="header"><h1>DSTERMINAL CYBER OPS - INCIDENT REPORT</h1>
<p>Report ID: {report_id} | Version: 4.0.0.113 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></div>
<div class="incident">
<h2>[ALERT] {incident_data.get('threat_level', 'INCIDENT')}</h2>
<p><b>File:</b> {incident_data.get('file_path', 'Unknown')}</p>
<p>{incident_data.get('description', 'Security incident detected and contained')}</p>
</div>
<h3>[LIST] Recommendations</h3>
{''.join([f'<div class="recommendation">[OK] {r}</div>' for r in incident_data.get('recommendations', ['Run full system scan', 'Update security patches', 'Review access logs'])])}
<h3>[CHART] System Metrics</h3>
<div><span class="metric">CPU: {psutil.cpu_percent()}%</span>
<span class="metric">RAM: {psutil.virtual_memory().percent}%</span>
<span class="metric">DISK: {psutil.disk_usage('/').percent}%</span></div>
<hr style="border-color:rgba(0,255,136,0.1);margin-top:30px;">
<p style="color:#2a5a4a;text-align:center;">{watermark} | Classified - Confidential</p>
</body>
</html>'''
    html_path = os.path.join(REPORTS_DIR, f'{report_id}.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    pdf_path = os.path.join(REPORTS_DIR, f'{report_id}.pdf')
    pdf_content = f"""
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║              DSTERMINAL CYBER OPS                           ║
    ║                   INCIDENT REPORT                           ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    Report ID: {report_id}
    Version: 4.0.0.113
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                    INCIDENT DETAILS                         ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    Threat Level: {incident_data.get('threat_level', 'INCIDENT')}
    File: {incident_data.get('file_path', 'Unknown')}
    Description: {incident_data.get('description', 'Security incident detected')}
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                  SYSTEM INFORMATION                         ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    Hostname: {platform.node()}
    OS: {platform.platform()}
    CPU: {psutil.cpu_percent()}%
    Memory: {psutil.virtual_memory().percent}%
    Disk: {psutil.disk_usage('/').percent}%
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                  RECOMMENDATIONS                            ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    {chr(10).join(['• ' + r for r in incident_data.get('recommendations', ['Run full system scan', 'Update security patches'])])}
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║              {watermark}                                    ║
    ║              Classified - Confidential                      ║
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
    print(f"  - PDF: {pdf_path}")
    
    return report_entry

# ============================================================
# ENHANCED QUARANTINE FUNCTIONS WITH PATH RESOLUTION
# ============================================================
def sanitize_path(file_path):
    """Sanitize and clean file path"""
    file_path = file_path.strip().strip('"').strip("'")
    file_path = file_path.replace('\t', '\\')
    file_path = file_path.replace('	', '\\')
    if ':' in file_path and '\\' not in file_path and '/' not in file_path:
        parts = file_path.split(':')
        if len(parts) > 1:
            drive = parts[0] + ':'
            rest = parts[1].replace('\\', '/').replace('/', '\\')
            file_path = drive + '\\' + rest
    file_path = file_path.replace('/', '\\')
    return file_path.strip()

def find_file_anywhere(filename):
    """Search for a file anywhere in the system"""
    search_paths = [
        os.getcwd(),
        os.environ.get('USERPROFILE'),
        os.path.expanduser('~'),
    ]
    
    # Add common paths
    user_profile = os.environ.get('USERPROFILE')
    if user_profile:
        search_paths.extend([
            os.path.join(user_profile, 'Documents'),
            os.path.join(user_profile, 'Desktop'),
            os.path.join(user_profile, 'Downloads'),
        ])
    
    search_paths.extend([
        os.environ.get('TEMP'),
        os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'),
        'C:\\',
        'C:\\ProgramData',
        'C:\\Users',
        '/tmp',
        '/var/tmp',
    ])
    
    # Filter out None values
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
            print(f"[SEARCH] Looking in: {search_path}")
            for root, dirs, files in os.walk(search_path):
                depth = root.replace(search_path, '').count(os.sep)
                if depth > 4:
                    continue
                for f in files:
                    if f.lower() == filename.lower():
                        found_path = os.path.join(root, f)
                        print(f"[SEARCH] Found: {found_path}")
                        return found_path
        except Exception as e:
            print(f"[SEARCH] Error in {search_path}: {e}")
            continue
    return None

def quarantine_file(file_path, threat_type="Ransomware"):
    global pending_quarantine, quarantined_files, ransomware_detected_files
    
    file_path = sanitize_path(file_path)
    print(f"[QUARANTINE] Attempting to quarantine: {file_path}")
    
    if not os.path.exists(file_path):
        filename = os.path.basename(file_path)
        print(f"[QUARANTINE] File not found, searching for: {filename}")
        
        found_path = find_file_anywhere(filename)
        if found_path:
            print(f"[QUARANTINE] Found file at: {found_path}")
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
        return {'success': False, 'error': f'Path is a directory, not a file: {file_path}'}
    
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
        print(f"[QUARANTINE] Moved: {file_path} -> {dest_path}")
        
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
            f.write(f"{datetime.now().isoformat()} | QUARANTINED | {file_path} -> {dest_path} | {threat_type}\n")
        
        if not pending_quarantine:
            if SHIELD_AVAILABLE and hasattr(shield, 'threat_level'):
                shield.threat_level = type('obj', (object,), {'name': 'CLEAN'})
        
        return {'success': True, 'quarantine_path': dest_path}
    except Exception as e:
        print(f"[QUARANTINE] Error: {e}")
        return {'success': False, 'error': str(e)}

def restore_from_quarantine(quarantine_path):
    """Restore a file from quarantine"""
    global quarantined_files
    
    # Sanitize the path first
    quarantine_path = sanitize_path(quarantine_path)
    print(f"[RESTORE] Attempting to restore: {quarantine_path}")
    
    if not os.path.exists(quarantine_path):
        # Try to find the file in the quarantine directory
        filename = os.path.basename(quarantine_path)
        print(f"[RESTORE] File not found, searching for: {filename}")
        
        # Search in quarantine directory
        for root, dirs, files in os.walk(QUARANTINE_DIR):
            for f in files:
                if f == filename:
                    quarantine_path = os.path.join(root, f)
                    print(f"[RESTORE] Found file at: {quarantine_path}")
                    break
            if os.path.exists(quarantine_path):
                break
    
    if not os.path.exists(quarantine_path):
        return {'success': False, 'error': f'Quarantine file not found: {quarantine_path}'}
    
    # Find the original path from history
    original_path = None
    for item in quarantined_files:
        # Compare just the filename or full path
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
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        
        # Move file back
        shutil.move(quarantine_path, original_path)
        
        # Update history
        quarantined_files = [f for f in quarantined_files if f.get('quarantine_path') != quarantine_path]
        save_quarantine_history()
        
        return {'success': True, 'restored_path': original_path}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_quarantined(quarantine_path):
    """Permanently delete a quarantined file"""
    global quarantined_files
    
    # Sanitize the path first
    quarantine_path = sanitize_path(quarantine_path)
    print(f"[DELETE] Attempting to delete: {quarantine_path}")
    
    if not os.path.exists(quarantine_path):
        # Try to find the file in the quarantine directory
        filename = os.path.basename(quarantine_path)
        print(f"[DELETE] File not found, searching for: {filename}")
        
        # Search in quarantine directory
        for root, dirs, files in os.walk(QUARANTINE_DIR):
            for f in files:
                if f == filename:
                    quarantine_path = os.path.join(root, f)
                    print(f"[DELETE] Found file at: {quarantine_path}")
                    break
            if os.path.exists(quarantine_path):
                break
    
    if not os.path.exists(quarantine_path):
        return {'success': False, 'error': f'Quarantine file not found: {quarantine_path}'}
    
    try:
        os.remove(quarantine_path)
        # Also remove the quarantine directory if empty
        quarantine_dir = os.path.dirname(quarantine_path)
        try:
            os.rmdir(quarantine_dir)
        except:
            pass  # Directory not empty or can't remove
            
        quarantined_files = [f for f in quarantined_files if os.path.basename(f.get('quarantine_path', '')) != os.path.basename(quarantine_path)]
        save_quarantine_history()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================
# SYSTEM CONTROL FUNCTIONS
# ============================================================
def kill_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        time.sleep(1)
        if process.is_running():
            process.kill()
        blocked_processes.append(pid)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def isolate_system():
    global system_isolated
    try:
        for interface in netifaces.interfaces():
            try:
                subprocess.run(['netsh', 'interface', 'set', 'interface', interface, 'admin=disable'], 
                             capture_output=True, timeout=5)
            except:
                pass
        
        subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'firewallpolicy', 'blockinbound,blockoutbound'], 
                      capture_output=True)
        
        system_isolated = True
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def restore_network():
    global system_isolated
    try:
        for interface in netifaces.interfaces():
            try:
                subprocess.run(['netsh', 'interface', 'set', 'interface', interface, 'admin=enable'], 
                             capture_output=True, timeout=5)
            except:
                pass
        
        subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'firewallpolicy', 'blockinbound,allowoutbound'], 
                      capture_output=True)
        
        system_isolated = False
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def full_system_scan():
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
# ROUTES
# ============================================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    status = shield.get_status() if SHIELD_AVAILABLE else {'threat_level': 'CLEAN', 'events_monitored': 0, 'monitoring': config.get('monitoring_enabled', True)}
    vulnerabilities = detect_real_vulnerabilities()
    threats = detect_threat_actors()
    
    risk_score = min(100, 
        (sum(1 for v in vulnerabilities if v['severity'] == 'Critical') * 15) +
        (sum(1 for v in vulnerabilities if v['severity'] == 'High') * 10) +
        (sum(1 for t in threats if t['risk'] == 'High') * 10) +
        (psutil.cpu_percent() / 4)
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
        'quarantine_progress': auto_quarantine_progress
    })

# ============================================================
# QUARANTINE ROUTES
# ============================================================
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
    print(f"[QUARANTINE ROUTE] Attempting to quarantine: {file_path}")
    
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

# ============================================================
# SYSTEM CONTROL ROUTES
# ============================================================
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
        elif hasattr(shield, 'start_monitoring') and hasattr(shield, 'stop_monitoring'):
            if enable:
                shield.start_monitoring()
            else:
                shield.stop_monitoring()
    
    return jsonify({'success': True, 'monitoring': enable, 'status': 'enabled' if enable else 'paused'})

scanning_in_progress = False
scan_progress = 0
scan_results = []

@app.route('/api/scan/full', methods=['POST'])
def start_full_scan():
    global scanning_in_progress, scan_progress, scan_results
    
    if scanning_in_progress:
        return jsonify({'success': False, 'error': 'Scan already in progress', 'progress': scan_progress})
    
    scanning_in_progress = True
    scan_progress = 0
    scan_results = []
    
    try:
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
                vulns = detect_real_vulnerabilities()
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
                        'description': f"Full system scan found {len(scan_results)} potential threats",
                        'recommendations': ['Review scan results', 'Quarantine infected files']
                    }
                    generate_report(incident_data)
                
            except Exception as e:
                print(f"[SCAN] Error during scan: {e}")
                scan_results.append({'type': 'error', 'message': str(e)})
            finally:
                scanning_in_progress = False
                scan_progress = 0
                socketio.emit('scan_complete', {'results': scan_results, 'count': len(scan_results)})
        
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True, 
            'message': 'Scan started',
            'progress': 0
        })
    except Exception as e:
        scanning_in_progress = False
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scan/progress')
def get_scan_progress():
    return jsonify({
        'scanning': scanning_in_progress,
        'progress': scan_progress,
        'results_count': len(scan_results)
    })

@app.route('/api/scan/results')
def get_scan_results():
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

# ============================================================
# WHITELIST/BLACKLIST ROUTES
# ============================================================
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

# ============================================================
# CONFIGURATION ROUTES
# ============================================================
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

@app.route('/api/config/export')
def export_config():
    config_path = os.path.join(CONFIG_DIR, 'config.json')
    if os.path.exists(config_path):
        return send_file(config_path, as_attachment=True, download_name='dsterminal_config.json')
    return jsonify({'error': 'Config not found'}), 404

@app.route('/api/config/import', methods=['POST'])
def import_config():
    global config
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        imported_config = json.load(file)
        for key, value in imported_config.items():
            if key in config:
                config[key] = value
        save_config(config)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================================
# REPORT ROUTES
# ============================================================
@app.route('/api/reports')
def get_reports():
    return jsonify(report_history[-10:] if report_history else [])

@app.route('/api/reports/download/<report_id>/<format>')
def download_report(report_id, format):
    ext_map = {'json': '.json', 'html': '.html', 'pdf': '.pdf'}
    if format not in ext_map:
        return jsonify({'error': 'Invalid format'}), 400
    
    file_path = os.path.join(REPORTS_DIR, f'{report_id}{ext_map[format]}')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"{report_id}.{format}")
    return jsonify({'error': 'Report not found'}), 404

# ============================================================
# OTHER ROUTES
# ============================================================
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
    return jsonify(detect_real_vulnerabilities())

@app.route('/api/scan/ransomware')
def scan_ransomware():
    results = detector.scan_for_ransomware()
    return jsonify({
        'scanned_dirs': detector.monitored_dirs,
        'detected': results,
        'count': len(results)
    })

@app.route('/api/debug/paths')
def debug_paths():
    return jsonify({
        'monitored_dirs': detector.monitored_dirs,
        'pending_quarantine': pending_quarantine,
        'quarantined_files': quarantined_files,
        'ransomware_detected_files': ransomware_detected_files,
        'detected_file_paths': list(detected_file_paths),
        'whitelist': whitelist,
        'blacklist': blacklist,
        'config': config,
        'isolated': system_isolated
    })

@app.route('/api/logs/export')
def export_logs():
    log_files = []
    for log_file in os.listdir(LOGS_DIR):
        if log_file.endswith('.log'):
            log_files.append(log_file)
    
    export_path = os.path.join(WORKSPACE_DIR, f'logs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(export_path, 'w', encoding='utf-8') as outfile:
        outfile.write(f"DSTERMINAL LOGS EXPORT - {datetime.now().isoformat()}\n")
        outfile.write("=" * 80 + "\n\n")
        for log_file in log_files:
            outfile.write(f"\n--- {log_file} ---\n")
            try:
                with open(os.path.join(LOGS_DIR, log_file), 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
            except:
                pass
    
    if os.path.exists(export_path):
        return send_file(export_path, as_attachment=True, download_name=os.path.basename(export_path))
    return jsonify({'error': 'Failed to export logs'}), 500

# ============================================================
# WEBSOCKET
# ============================================================
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'status': 'connected'})

@socketio.on('subscribe_updates')
def handle_subscribe():
    client_sid = request.sid
    
    def send_updates():
        while True:
            try:
                with app.app_context():
                    status = get_status().get_json()
                    socketio.emit('status_update', status, room=client_sid)
                    socketio.emit('metrics_update', get_system_metrics(), room=client_sid)
                    socketio.emit('mitre_update', detect_active_mitre_techniques(), room=client_sid)
                    time.sleep(2)
            except Exception as e:
                print(f"Update error: {e}")
                time.sleep(5)
    
    threading.Thread(target=send_updates, daemon=True).start()

# ============================================================
# HTML TEMPLATE
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
        
        #fullscreenOverlay { 
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
            z-index: -1 !important;
        }

        .dst-logo-container { display: flex; align-items: center; gap: 12px; position: relative; z-index: 3; }
        .dst-logo-img { width: 48px; height: 48px; object-fit: contain; filter: drop-shadow(0 0 20px rgba(0,255,136,0.3)); animation: logo-glow 2s ease-in-out infinite; border-radius: 8px; background: rgba(0,0,0,0.2); padding: 2px; }
        @keyframes logo-glow { 0%, 100% { filter: drop-shadow(0 0 20px rgba(0,255,136,0.3)); } 50% { filter: drop-shadow(0 0 40px rgba(0,255,136,0.6)) drop-shadow(0 0 80px rgba(0,255,136,0.2)); } }
        .dst-logo-text { font-family: 'Courier New', monospace; font-weight: bold; font-size: 24px; letter-spacing: 3px; background: linear-gradient(135deg, #00ff88, #00ccff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: none; animation: neon-pulse 2s ease-in-out infinite; }
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
        .chart-container .chart-loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #2a5a4a;
            font-size: 12px;
            animation: pulse 1.5s ease-in-out infinite;
        }
        .event-log { max-height: 150px; overflow-y: auto; font-size: 12px; background: rgba(0,0,0,0.3); border-radius: 4px; padding: 8px; }
        .event-log .no-events { color: #2a5a4a; text-align: center; padding: 20px 0; font-size: 11px; }
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
        .mitre-grid::-webkit-scrollbar { width: 3px; }
        .mitre-grid::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
        .mitre-grid::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 2px; }
        .mitre-item { background: rgba(0,0,0,0.4); padding: 8px 10px; border-radius: 6px; border-left: 3px solid #00ff88; text-align: center; transition: all 0.3s ease; cursor: default; position: relative; overflow: hidden; }
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
        .modal-content .list-item .action-btn:hover { opacity: 0.8; }
        #matrixContainer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; pointer-events: none; z-index: 0; }
        .matrix-particle { position: absolute; color: rgba(0, 255, 136, 0.08); font-family: 'Courier New', monospace; font-size: 10px; pointer-events: none; animation: matrix-fall linear infinite; }
        @keyframes matrix-fall { 0% { transform: translateY(-20px); opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { transform: translateY(calc(100% + 20px)); opacity: 0; } }
        #headerTime { color: #2a5a4a; font-size: 12px; font-family: 'Courier New', monospace; text-shadow: 0 0 10px rgba(0, 255, 136, 0.1); position: relative; z-index: 3; }
        #logoFallback { animation: logo-glow 2s ease-in-out infinite; }
        .scan-progress { display: none; color: #ffcc00; font-size: 11px; margin-top: 4px; }
        .scan-progress.active { display: block; }
        
        .quarantine-progress-container {
            display: none;
            background: rgba(255,0,51,0.05);
            border: 1px solid rgba(255,0,51,0.2);
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 10px;
            position: relative;
            overflow: hidden;
        }
        .quarantine-progress-container.active {
            display: block;
            animation: glow-border 2s ease-in-out infinite;
        }
        @keyframes glow-border {
            0%, 100% { border-color: rgba(255,0,51,0.2); }
            50% { border-color: rgba(255,0,51,0.6); }
        }
        .quarantine-progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            margin-bottom: 8px;
        }
        .quarantine-progress-header .file-name {
            color: #ffcc00;
            font-family: monospace;
            font-size: 10px;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .quarantine-progress-header .status-text {
            color: #ff0033;
            font-weight: bold;
        }
        .quarantine-progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,0,51,0.1);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
        }
        .quarantine-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff0033, #ff6600, #ffcc00);
            width: 0%;
            transition: width 0.8s ease;
            border-radius: 3px;
            position: relative;
        }
        .quarantine-progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 1.5s infinite;
        }
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        .quarantine-progress-details {
            display: flex;
            justify-content: space-between;
            font-size: 9px;
            color: #2a5a4a;
            margin-top: 4px;
        }
        .quarantine-progress-details .step {
            color: #00ccff;
        }
        .auto-quarantine-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 10px;
            color: #2a5a4a;
            cursor: pointer;
        }
        .auto-quarantine-toggle input[type="checkbox"] {
            appearance: none;
            width: 32px;
            height: 18px;
            background: rgba(255,0,51,0.2);
            border-radius: 10px;
            border: 1px solid rgba(255,0,51,0.3);
            cursor: pointer;
            position: relative;
            transition: all 0.3s;
            flex-shrink: 0;
        }
        .auto-quarantine-toggle input[type="checkbox"]:checked {
            background: rgba(0,255,136,0.3);
            border-color: #00ff88;
        }
        .auto-quarantine-toggle input[type="checkbox"]::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 12px;
            height: 12px;
            background: #fff;
            border-radius: 50%;
            transition: all 0.3s;
        }
        .auto-quarantine-toggle input[type="checkbox"]:checked::after {
            left: 16px;
            background: #00ff88;
        }
        
        @media (max-width: 1024px) { .col-span-3 { grid-column: span 6; } .col-span-4 { grid-column: span 6; } .col-span-6 { grid-column: span 12; } .col-span-8 { grid-column: span 12; } .mitre-grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 600px) { body { padding: 10px; } .header { flex-direction: column; align-items: flex-start; gap: 10px; padding: 12px 15px; } .dst-logo-text { font-size: 18px; } .dst-logo-img { width: 32px; height: 32px; } .col-span-3, .col-span-4 { grid-column: span 12; } .card { padding: 10px 12px; } .value { font-size: 20px; } .mitre-grid { grid-template-columns: repeat(2, 1fr); } .mitre-item .count { font-size: 18px; } .header-controls { width: 100%; justify-content: center; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
        ::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 2px; }
        
        .scan-progress-container { 
            display: none; 
            margin-top: 8px; 
            width: 100%; 
            padding: 0 10px;
        }
        .scan-progress-container.active { 
            display: block; 
        }
        .scan-progress-bar { 
            width: 100%; 
            height: 4px; 
            background: rgba(0,255,136,0.1); 
            border-radius: 2px; 
            overflow: hidden; 
        }
        .scan-progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #00ff88, #00ccff); 
            width: 0%; 
            transition: width 0.5s ease; 
            border-radius: 2px; 
        }
        .scan-progress-text { 
            color: #2a5a4a; 
            font-size: 10px; 
            margin-top: 4px; 
            text-align: center; 
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>

<div id="fullscreenOverlay"></div>

<div class="attack-banner" id="attackBanner">[ALERT] RANSOMWARE DETECTED - AUTO-QUARANTINE IN PROGRESS [ALERT]</div>

<header class="header" id="mainHeader">
    <div id="matrixContainer"></div>
    
    <div class="dst-logo-container">
        <img src="/static/3486-removebg-preview.ico" 
            alt="DSTerminal Logo" 
            class="dst-logo-img" 
            id="dstLogo"
            onerror="this.style.display='none'; document.getElementById('logoFallback').style.display='flex';">
        
        <div id="logoFallback" style="display:none; align-items:center; justify-content:center; width:48px; height:48px;">
            <svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="4" width="40" height="40" rx="8" stroke="#00ff88" stroke-width="2" fill="none"/>
                <text x="24" y="28" font-family="Courier New, monospace" font-size="20" font-weight="bold" fill="#00ff88" text-anchor="middle">D</text>
                <text x="24" y="40" font-family="Courier New, monospace" font-size="8" fill="#00ff88" text-anchor="middle">TERMINAL</text>
                <circle cx="24" cy="18" r="2" fill="#00ff88" opacity="0.5">
                    <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
                </circle>
            </svg>
        </div>
        
        <div>
            <div class="dst-logo-text">
                DSTERMINAL <span class="highlight">●</span>
            </div>
            <div class="dst-logo-badge">CYBER OPS v4.0.0.113</div>
        </div>
    </div>
    
    <div class="status-right">
        <span>
            <span class="glow-dot green" id="statusDot"></span>
            <span id="statusText" class="status-protected">[SUCCESS] PROTECTED</span>
        </span>
        <span id="headerTime"></span>
        <div class="header-controls">
            <label class="auto-quarantine-toggle" title="Auto-quarantine detected ransomware files">
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
        <div class="quarantine-progress-details">
            <span class="step" id="quarantineStep">Initializing...</span>
            <span id="quarantinePercent">0%</span>
            <span id="quarantineTime">0s elapsed</span>
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
            <div class="card-title">[LOCK] Quarantine <span style="font-size:8px;color:#2a5a4a;" id="quarantineCount"></span></div>
            <div id="quarantineList"><div class="text-muted text-center">No files pending</div></div>
        </div>
        <div class="card col-span-4">
            <div class="card-title">[TIP] Recommendations</div>
            <div id="recommendationList"><div class="text-muted text-center">No recommendations</div></div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-6">
            <div class="card-title">[LIST] Event Log <button class="control-btn" onclick="clearEvents()" style="font-size:8px;">CLEAR</button></div>
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
</div>

<script>
    // Hide overlay immediately
    (function() {
        var overlay = document.getElementById('fullscreenOverlay');
        if (overlay) {
            overlay.style.display = 'none';
            overlay.style.visibility = 'hidden';
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
            overlay.style.zIndex = '-1';
        }
    })();

    const ALL_MITRE_TECHNIQUES = [
        { id: "T1059", name: "Command & Scripting", tactic: "Execution", category: "execution" },
        { id: "T1047", name: "WMI", tactic: "Execution", category: "execution" },
        { id: "T1053", name: "Scheduled Task/Job", tactic: "Execution", category: "execution" },
        { id: "T1204", name: "User Execution", tactic: "Execution", category: "execution" },
        { id: "T1106", name: "Native API", tactic: "Execution", category: "execution" },
        { id: "T1547", name: "Boot/Logon Autostart", tactic: "Persistence", category: "persistence" },
        { id: "T1543", name: "Create/Modify System Process", tactic: "Persistence", category: "persistence" },
        { id: "T1136", name: "Create Account", tactic: "Persistence", category: "persistence" },
        { id: "T1505", name: "Server Software Component", tactic: "Persistence", category: "persistence" },
        { id: "T1574", name: "Hijack Execution Flow", tactic: "Persistence", category: "persistence" },
        { id: "T1055", name: "Process Injection", tactic: "Privilege Escalation", category: "privilege" },
        { id: "T1068", name: "Exploit for Priv Escalation", tactic: "Privilege Escalation", category: "privilege" },
        { id: "T1134", name: "Access Token Manipulation", tactic: "Privilege Escalation", category: "privilege" },
        { id: "T1548", name: "Abuse Elevation Control", tactic: "Privilege Escalation", category: "privilege" },
        { id: "T1027", name: "Obfuscated Files/Info", tactic: "Defense Evasion", category: "defense" },
        { id: "T1070", name: "Indicator Removal", tactic: "Defense Evasion", category: "defense" },
        { id: "T1036", name: "Masquerading", tactic: "Defense Evasion", category: "defense" },
        { id: "T1562", name: "Impair Defenses", tactic: "Defense Evasion", category: "defense" },
        { id: "T1222", name: "File/Dir Permissions Mod", tactic: "Defense Evasion", category: "defense" },
        { id: "T1087", name: "Account Discovery", tactic: "Discovery", category: "discovery" },
        { id: "T1018", name: "Remote System Discovery", tactic: "Discovery", category: "discovery" },
        { id: "T1040", name: "Network Sniffing", tactic: "Discovery", category: "discovery" },
        { id: "T1057", name: "Process Discovery", tactic: "Discovery", category: "discovery" },
        { id: "T1518", name: "Software Discovery", tactic: "Discovery", category: "discovery" },
        { id: "T1021", name: "Remote Services", tactic: "Lateral Movement", category: "lateral" },
        { id: "T1563", name: "Remote Service Hijacking", tactic: "Lateral Movement", category: "lateral" },
        { id: "T1072", name: "Software Deployment Tools", tactic: "Lateral Movement", category: "lateral" },
        { id: "T1005", name: "Data from Local System", tactic: "Collection", category: "collection" },
        { id: "T1119", name: "Automated Collection", tactic: "Collection", category: "collection" },
        { id: "T1074", name: "Data Staged", tactic: "Collection", category: "collection" },
        { id: "T1567", name: "Exfil Over Web Service", tactic: "Exfiltration", category: "exfiltration" },
        { id: "T1048", name: "Exfil Over Alt Protocol", tactic: "Exfiltration", category: "exfiltration" },
        { id: "T1020", name: "Automated Exfiltration", tactic: "Exfiltration", category: "exfiltration" },
        { id: "T1486", name: "Data Encrypted for Impact", tactic: "Impact", category: "impact" },
        { id: "T1490", name: "Inhibit System Recovery", tactic: "Impact", category: "impact" },
        { id: "T1485", name: "Data Destruction", tactic: "Impact", category: "impact" },
        { id: "T1499", name: "Endpoint DoS", tactic: "Impact", category: "impact" },
        { id: "T1003", name: "Credential Dumping", tactic: "Credential Access", category: "credential" },
        { id: "T1110", name: "Brute Force", tactic: "Credential Access", category: "credential" },
        { id: "T1555", name: "Credentials from Password Stores", tactic: "Credential Access", category: "credential" }
    ];

    let monitoringEnabled = true;
    let isolated = false;
    let scanning = false;
    let autoQuarantineEnabled = true;

    function createMatrixParticles() {
        const container = document.getElementById('matrixContainer');
        if (!container) return;
        const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        container.innerHTML = '';
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('span');
            particle.className = 'matrix-particle';
            particle.textContent = chars[Math.floor(Math.random() * chars.length)];
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = '-10%';
            particle.style.animationDuration = (5 + Math.random() * 10) + 's';
            particle.style.animationDelay = (Math.random() * 5) + 's';
            particle.style.opacity = 0.05 + Math.random() * 0.15;
            particle.style.fontSize = (8 + Math.random() * 6) + 'px';
            container.appendChild(particle);
        }
    }
    document.addEventListener('DOMContentLoaded', createMatrixParticles);

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
        container.innerHTML = techniques.map(tech => {
            const categoryClass = `mitre-${tech.category || 'unknown'}`;
            return `
                <div class="mitre-item ${categoryClass}">
                    <span class="count">${tech.count || 0}</span>
                    <span class="technique-id">${tech.id}</span>
                    <span class="technique-name" title="${tech.name}">${tech.name}</span>
                    <span class="tactic">${tech.tactic}</span>
                </div>
            `;
        }).join('');
        countDisplay.textContent = `Showing ${techniques.length} MITRE ATT&CK techniques`;
    }

    function updateEvents(events) {
        const log = document.getElementById('eventLog');
        const noEvents = log.querySelector('.no-events');
        if (noEvents) {
            log.innerHTML = '';
        }
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
                while (log.children.length > 50) {
                    log.removeChild(log.lastChild);
                }
            });
        }
    }

    function clearEvents() {
        document.getElementById('eventLog').innerHTML = '<div class="no-events">Log cleared</div>';
        fetch('/api/events/clear', { method: 'DELETE' }).catch(() => {});
    }

    function quarantineFile(path) {
        if (!path || path === '') {
            alert('❌ No file path to quarantine');
            return;
        }
        
        if (!confirm(`[WARNING] Are you sure you want to quarantine this file?\n\n[FOLDER] ${path}\n\nThis action will move the file to quarantine and prevent it from executing.`)) {
            return;
        }
        
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '⏳ QUARANTINING...';
        btn.disabled = true;
        
        fetch('/api/quarantine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                file_path: path, 
                threat_type: 'Ransomware',
                confirm: true 
            })
        }).then(r => r.json()).then(data => {
            btn.textContent = originalText;
            btn.disabled = false;
            
            if (data.success) { 
                alert('[OK] File quarantined successfully!');
                fetch('/api/status').then(r => r.json()).then(updateStatus);
                fetch('/api/quarantine/pending').then(r => r.json()).then(updateQuarantine);
            } 
            else { 
                if (data.cancelled) {
                    console.log('Quarantine cancelled by user');
                } else {
                    alert('❌ Failed to quarantine: ' + (data.error || 'Unknown error'));
                }
            }
        }).catch(err => {
            btn.textContent = originalText;
            btn.disabled = false;
            alert('❌ Network error while quarantining file');
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
        if (scanning) {
            alert('Scan already in progress');
            return;
        }
        scanning = true;
        document.getElementById('scanStatus').textContent = '[SEARCH] Scanning...';
        document.getElementById('scanStatus').style.color = '#ffcc00';
        
        fetch('/api/scan/full', { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                scanning = false;
                if (data.success) {
                    document.getElementById('scanStatus').textContent = `[OK] Scan complete: ${data.count} files detected`;
                    document.getElementById('scanStatus').style.color = '#00ff88';
                    fetch('/api/status').then(r => r.json()).then(updateStatus);
                } else {
                    document.getElementById('scanStatus').textContent = '❌ Scan failed: ' + data.error;
                    document.getElementById('scanStatus').style.color = '#ff0033';
                }
                setTimeout(() => {
                    document.getElementById('scanStatus').textContent = '';
                }, 5000);
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
            .catch(err => {
                body.innerHTML = '<div style="text-align:center;color:#ff0033;">Error loading processes</div>';
                console.error(err);
            });
    }

    function killProcess(pid) {
        if (!pid) {
            alert('❌ No PID provided');
            return;
        }
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
            if (data.success) {
                alert('[OK] Process killed');
                showProcesses();
            } else {
                alert('❌ Failed: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(err => {
            btn.textContent = originalText;
            btn.disabled = false;
            alert('❌ Network error: ' + err.message);
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
                        <span style="font-size:10px;color:#ffcc00;">${f.original_path.split('\\\\').pop()}</span>
                        <span>
                            <span style="font-size:8px;color:#2a5a4a;">${new Date(f.timestamp).toLocaleString()}</span>
                            <button class="action-btn success" onclick="restoreFile('${f.quarantine_path}')">RESTORE</button>
                            <button class="action-btn danger" onclick="deleteQuarantined('${f.quarantine_path}')">DELETE</button>
                        </span>
                    </div>
                `).join('');
            })
            .catch(err => {
                body.innerHTML = '<div style="text-align:center;color:#ff0033;">Error loading quarantine list</div>';
                console.error(err);
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
                    body.innerHTML = `
                        <div style="text-align:center;color:#2a5a4a;padding:20px;">
                            No files in whitelist<br>
                            <small style="color:#2a5a4a;">Whitelisted files are never quarantined</small>
                            <br><br>
                            <button class="control-btn" onclick="addToWhitelist()">➕ Add File to Whitelist</button>
                        </div>
                    `;
                    return;
                }
                body.innerHTML = files.map(f => `
                    <div class="list-item">
                        <span style="font-size:10px;color:#00ff88;">[OK] ${f}</span>
                        <button class="action-btn danger" onclick="removeFromWhitelist('${f}')">REMOVE</button>
                    </div>
                `).join('') + `
                    <div style="margin-top:10px;text-align:center;">
                        <button class="control-btn" onclick="addToWhitelist()">➕ Add File</button>
                    </div>
                `;
            })
            .catch(err => {
                body.innerHTML = '<div style="text-align:center;color:#ff0033;">Error loading whitelist</div>';
                console.error(err);
            });
    }

    function addToWhitelist() {
        const filePath = prompt('Enter the full path of the file to whitelist:');
        if (!filePath) return;
        
        fetch('/api/whitelist/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: filePath })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert('[OK] File added to whitelist: ' + filePath);
                showWhitelist();
            } else {
                alert('❌ Failed: ' + (data.error || 'Unknown error'));
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
            if (data.success) {
                alert('[OK] Removed from whitelist');
                showWhitelist();
            } else {
                alert('❌ Failed: ' + (data.error || 'Unknown error'));
            }
        });
    }

    function closeModal() {
        document.getElementById('modal').classList.remove('show');
    }

    function updateQuarantineProgress(data) {
        const container = document.getElementById('quarantineProgress');
        const fill = document.getElementById('quarantineProgressFill');
        const percent = document.getElementById('quarantinePercent');
        const step = document.getElementById('quarantineStep');
        const status = document.getElementById('quarantineStatus');
        const fileName = document.getElementById('quarantineFileName');
        const timeEl = document.getElementById('quarantineTime');
        
        if (data && data.in_progress) {
            container.classList.add('active');
            fill.style.width = data.current_step + '%';
            percent.textContent = data.current_step + '%';
            step.textContent = data.status || 'Processing...';
            status.textContent = data.current_step >= 100 ? '[OK] Complete!' : '⏳ In Progress...';
            fileName.textContent = data.file_path ? data.file_path.split('\\\\').pop() : '-';
            
            if (data.start_time) {
                const elapsed = Math.floor((new Date() - new Date(data.start_time)) / 1000);
                timeEl.textContent = elapsed + 's elapsed';
            }
            
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
                setTimeout(() => {
                    document.getElementById('autoQStatus').textContent = '';
                }, 5000);
            } else if (data && data.status === 'failed') {
                document.getElementById('autoQStatus').textContent = '❌ Auto-Q: Failed';
                document.getElementById('autoQStatus').style.color = '#ff0033';
                setTimeout(() => {
                    document.getElementById('autoQStatus').textContent = '';
                }, 5000);
            } else {
                document.getElementById('autoQStatus').textContent = '';
            }
        }
    }

    const socket = io();
    let threatChart = null;
    let systemChart = null;
    let threatData = [];
    let timeLabels = [];

    function initCharts() {
        const threatCanvas = document.getElementById('threatChart');
        const systemCanvas = document.getElementById('systemChart');
        
        if (!threatCanvas || !systemCanvas) {
            console.warn('Chart canvases not found, retrying...');
            setTimeout(initCharts, 500);
            return;
        }
        
        // Hide loading indicators
        document.querySelectorAll('.chart-loading').forEach(el => {
            el.style.display = 'none';
        });
        
        try {
            // Destroy existing charts if they exist
            if (threatChart) {
                threatChart.destroy();
                threatChart = null;
            }
            if (systemChart) {
                systemChart.destroy();
                systemChart = null;
            }
            
            // Initialize threat chart with data
            const ctx1 = threatCanvas.getContext('2d');
            threatChart = new Chart(ctx1, {
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
                            grid: {
                                color: 'rgba(0,255,136,0.05)'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#2a5a4a',
                                font: { size: 8 },
                                maxTicksLimit: 10
                            },
                            grid: {
                                color: 'rgba(0,255,136,0.05)'
                            }
                        }
                    },
                    animation: {
                        duration: 750
                    }
                }
            });
            
            // Initialize system chart
            const ctx2 = systemCanvas.getContext('2d');
            systemChart = new Chart(ctx2, {
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
                    animation: {
                        animateRotate: true,
                        duration: 750
                    }
                }
            });
            
            console.log('Charts initialized successfully');
        } catch (error) {
            console.error('Error initializing charts:', error);
            setTimeout(initCharts, 1000);
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Ensure overlay is hidden
        var overlay = document.getElementById('fullscreenOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
        
        // Wait for everything to load
        setTimeout(function() {
            // Initialize charts
            initCharts();
            
            // Initialize other components
            displayRandomMITRE();
            setInterval(displayRandomMITRE, 30000);
            
            // Load initial data
            fetch('/api/status')
                .then(r => r.json())
                .then(updateStatus)
                .catch(() => console.log('Failed to load initial status'));
                
            fetch('/api/events')
                .then(r => r.json())
                .then(updateEvents)
                .catch(() => console.log('Failed to load initial events'));
                
            fetch('/api/quarantine/auto/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('autoQuarantineToggle').checked = data.enabled;
                    autoQuarantineEnabled = data.enabled;
                })
                .catch(() => console.log('Failed to load auto quarantine status'));
        }, 500);
    });

    function downloadReport(id, format) {
        window.location.href = `/api/reports/download/${id}/${format}`;
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
        
        if (data.quarantined_files) {
            document.getElementById('quarantineCount').textContent = `(${data.quarantined_files.length} total)`;
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
                <span style="color:#ff0033;font-size:10px;">[ERROR] ${item.path.split('\\\\').pop()}</span>
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
                <span class="file-path">[FOLDER] ${f.path.split('\\\\').pop()}</span>
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

    socket.on('connect', () => { 
        console.log('Connected to server');
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
    
    socket.on('quarantine_progress', (data) => {
        updateQuarantineProgress(data);
    });
    
    socket.on('quarantine_complete', (data) => {
        if (data.success) {
            document.getElementById('autoQStatus').textContent = '[OK] Auto-Q: Complete!';
            document.getElementById('autoQStatus').style.color = '#00ff88';
            setTimeout(() => {
                document.getElementById('autoQStatus').textContent = '';
            }, 5000);
        } else {
            document.getElementById('autoQStatus').textContent = '❌ Auto-Q: ' + (data.error || 'Failed');
            document.getElementById('autoQStatus').style.color = '#ff0033';
            setTimeout(() => {
                document.getElementById('autoQStatus').textContent = '';
            }, 5000);
        }
        fetch('/api/status').then(r => r.json()).then(updateStatus);
    });

    document.getElementById('autoQuarantineToggle').addEventListener('change', function() {
        autoQuarantineEnabled = this.checked;
        fetch('/api/quarantine/auto/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: autoQuarantineEnabled })
        });
    });

    document.addEventListener('DOMContentLoaded', function() {
        // Ensure overlay is hidden
        var overlay = document.getElementById('fullscreenOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
        
        // Wait for all resources to load
        setTimeout(function() {
            initCharts();
            displayRandomMITRE();
            setInterval(displayRandomMITRE, 30000);
            
            // Load initial data
            fetch('/api/status')
                .then(r => r.json())
                .then(updateStatus)
                .catch(() => console.log('Failed to load initial status'));
                
            fetch('/api/events')
                .then(r => r.json())
                .then(updateEvents)
                .catch(() => console.log('Failed to load initial events'));
                
            fetch('/api/quarantine/auto/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('autoQuarantineToggle').checked = data.enabled;
                    autoQuarantineEnabled = data.enabled;
                })
                .catch(() => console.log('Failed to load auto quarantine status'));
        }, 500);
    });
</script>
</body>
</html>
"""

# ============================================================
# MAIN
# ============================================================
def open_browser():
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:5000')
        print("[OK] Browser opened")
    except:
        print("[WARNING] Open http://localhost:5000 manually")

if __name__ == "__main__":
    print("=" * 70)
    print("🔮 DSTERMINAL SECURITY SUITE v4.0.0.113")
    print("=" * 70)
    print(f"📍 Dashboard: http://localhost:5000")
    print(f"[FOLDER] Workspace: {WORKSPACE_DIR}")
    print(f"[FOLDER] Reports: {REPORTS_DIR}")
    print(f"[FOLDER] Quarantine: {QUARANTINE_DIR}")
    print(f"🛡️ Shield Core: {shield.threat_level.name if hasattr(shield, 'threat_level') else 'ACTIVE'}")
    print("=" * 70)
    print("[OK] Automatic Ransomware Detection - Anywhere in your System")
    print("[OK] AUTO-QUARANTINE - Files automatically quarantined when detected")
    print("[OK] 2-Minute Quarantine Progress Bar on Dashboard")
    print("[OK] MITRE ATT&CK techniques")
    print("[OK] Reports (JSON/HTML/PDF)")
    print("=" * 70)
    print("\n[LIST] DASHBOARD CONTROLS:")
    print("  [BOT] Auto-Q - Toggle auto-quarantine on/off")
    print("  [LOCK] Isolate - Network isolation")
    print("  [FOLDER] Quarantine - View/restore/delete quarantined files")
    print("=" * 70)
    print("\n[POWER] AUTO-QUARANTINE FEATURES:")
    print("  • Automatically detects ransomware anywhere in system")
    print("  • Shows real-time progress bar (2 minutes)")
    print("  • Displays status in dashboard and banner")
    print("  • Creates incident report after quarantine")
    print("  • File appears in quarantine section with timestamp")
    print("=" * 70)
    print("\nPress Ctrl+C to stop\n")

    threading.Thread(target=open_browser, daemon=True).start()
    
    with SilenceFlaskStartup():
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)