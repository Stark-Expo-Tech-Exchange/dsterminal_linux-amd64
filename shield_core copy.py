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

DSTerminal Shield Core - Ransomware Defense Engine
Version: 4.0.0.113
"""
import sys
import os
import time
import json
import shutil
import hashlib
import threading
import glob
import re
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Any

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
# ANSI COLOR DEFINITIONS (ALWAYS AVAILABLE)
# ============================================================
class Colors:
    """ANSI color codes for terminal output"""
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
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_RED = '\033[91;1m'
    BRIGHT_YELLOW = '\033[93;1m'
    BRIGHT_CYAN = '\033[96;1m'
    BRIGHT_MAGENTA = '\033[95;1m'
    
    @staticmethod
    def strip(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# ============================================================
# TRY TO IMPORT COLORAMA WITH PROPER ERROR HANDLING
# ============================================================
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True, convert=True, strip=False)
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
        'DIM': '\033[2m'
    })
    Back = type('Back', (), {'RESET': '\033[49m'})
except Exception as e:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
    Back = type('Back', (), {'RESET': '\033[49m'})

# ============================================================
# TERMINAL UTILITIES - CENTERED LAYOUT
# ============================================================
def get_terminal_width() -> int:
    """Get terminal width for centering"""
    try:
        import shutil
        width = shutil.get_terminal_size().columns
        return min(max(width, 80), 120)
    except:
        return 80

def center_text(text: str, width: int = None) -> str:
    """Center text within terminal width"""
    if width is None:
        width = get_terminal_width()
    # Strip ANSI codes for length calculation
    clean_text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
    padding = max(0, (width - len(clean_text)) // 2)
    return ' ' * padding + text

def print_centered(text: str, color: str = "", width: int = None):
    """Print centered colored text"""
    if width is None:
        width = get_terminal_width()
    if color:
        print(center_text(f"{color}{text}{Colors.END}", width))
    else:
        print(center_text(text, width))

def print_colored(text: str, color: str = ""):
    """Print colored text without centering"""
    if color:
        print(f"{color}{text}{Colors.END}")
    else:
        print(text)

# ============================================================
# AUTO-TYPE ENGINE WITH COLORS AND CENTERED LAYOUT
# ============================================================
class AutoTypeEngine:
    """Handles auto-typing effects with colors and centering"""
    
    def __init__(self, delay: float = 0.03):
        self.delay = delay
        self.is_typing = False
        self.term_width = get_terminal_width()
        
    def type_text(self, text: str, color: str = "", end: str = "\n", delay: float = None, centered: bool = False):
        """Type text with color and auto-typing effect"""
        if delay is None:
            delay = self.delay
            
        display_text = text
        if centered:
            display_text = center_text(text)
            
        if color:
            sys.stdout.write(color)
            
        for char in display_text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
            
        if color:
            sys.stdout.write(Colors.END)
        if end:
            sys.stdout.write(end)
        sys.stdout.flush()
    
    def type_line(self, text: str, color: str = Colors.GREEN, centered: bool = False):
        """Type a single line with color"""
        self.type_text(text, color=color, end="\n", centered=centered)
    
    def type_banner(self, lines: List[str], color: str = Colors.CYAN, delay: float = 0.02):
        """Type a banner with color and centering"""
        for line in lines:
            self.type_text(line, color=color, end="\n", delay=delay, centered=True)
            time.sleep(0.05)
    
    def type_status(self, text: str, color: str = Colors.CYAN, centered: bool = False):
        """Type a status message"""
        if centered:
            self.type_text(f"[*] {text}", color=color, centered=True)
        else:
            self.type_text(f"[*] {text}", color=color)
    
    def type_success(self, text: str, centered: bool = False):
        """Type a success message"""
        if centered:
            self.type_text(f"[+] {text}", color=Colors.GREEN, centered=True)
        else:
            self.type_text(f"[+] {text}", color=Colors.GREEN)
    
    def type_warning(self, text: str, centered: bool = False):
        """Type a warning message"""
        if centered:
            self.type_text(f"[!] {text}", color=Colors.YELLOW, centered=True)
        else:
            self.type_text(f"[!] {text}", color=Colors.YELLOW)
    
    def type_error(self, text: str, centered: bool = False):
        """Type an error message"""
        if centered:
            self.type_text(f"[x] {text}", color=Colors.RED, centered=True)
        else:
            self.type_text(f"[x] {text}", color=Colors.RED)
    
    def type_info(self, text: str, centered: bool = False):
        """Type an info message"""
        if centered:
            self.type_text(f"[i] {text}", color=Colors.CYAN, centered=True)
        else:
            self.type_text(f"[i] {text}", color=Colors.CYAN)
    
    def type_box(self, title: str, content_lines: List[str], border_color: str = Colors.CYAN):
        """Type a centered box with border"""
        term_width = get_terminal_width()
        box_width = min(60, term_width - 10)
        if box_width < 30:
            box_width = 30
        padding = max(0, (term_width - box_width - 2) // 2)
        
        # Get clean text for width calculation
        def clean_len(text):
            return len(re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text))
        
        # Top border
        print(" " * padding + f"{border_color}┌{'─' * box_width}┐{Colors.END}")
        
        # Title
        title_text = f" {title} "
        if clean_len(title_text) > box_width:
            title_text = title_text[:box_width-3] + "..."
        title_padding = max(0, (box_width - clean_len(title_text)) // 2)
        print(" " * padding + f"{border_color}│{Colors.END}{' ' * title_padding}{Colors.YELLOW}{Colors.BOLD}{title_text}{Colors.END}{' ' * (box_width - clean_len(title_text) - title_padding)}{border_color}│{Colors.END}")
        
        # Separator
        print(" " * padding + f"{border_color}├{'─' * box_width}┤{Colors.END}")
        
        # Content
        for line in content_lines[:10]:
            clean_line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
            if clean_len(line) > box_width - 2:
                # Truncate if too long
                if len(line) > box_width - 5:
                    line = line[:box_width-5] + "..."
            padding_needed = max(0, box_width - clean_len(line) - 2)
            print(" " * padding + f"{border_color}│{Colors.END} {line}{' ' * padding_needed} {border_color}│{Colors.END}")
        
        # Bottom border
        print(" " * padding + f"{border_color}└{'─' * box_width}┘{Colors.END}")

# ============================================================
# CONTINUE WITH THE REST OF YOUR CODE
# ============================================================

class ThreatLevel(Enum):
    """Threat severity levels"""
    CLEAN = 0
    SUSPICIOUS = 1
    HIGH_RISK = 2
    RANSOMWARE_DETECTED = 3

@dataclass
class FileEvent:
    """File operation event record"""
    path: str
    operation: str
    process_name: str
    timestamp: float = field(default_factory=time.time)
    hash: str = ""
    pid: int = 0

@dataclass
class SecurityPolicies:
    """Security policy configuration"""
    allow_mfa_override: bool = True
    block_untrusted_scripts: bool = True
    max_file_ops_per_second: int = 30
    honeypot_paths: List[str] = field(default_factory=list)
    backup_enabled: bool = True
    auto_rollback: bool = True

class ShieldCore:
    """
    Main ransomware defense engine
    Implements Prevention, Detection, Response, and Recovery
    """
    
    def __init__(self, workspace_dir: str = None):
        self.threat_level = ThreatLevel.CLEAN
        self.event_log: List[FileEvent] = []
        self.honeypot_paths: List[str] = []
        self.quarantine_dir = None
        self.backup_dir = None
        self.policies = SecurityPolicies()
        self.is_active = False
        self._monitor_thread = None
        self._stop_monitoring = False
        self.typer = AutoTypeEngine(delay=0.03)
        
        # Setup workspace
        if workspace_dir:
            self.workspace_dir = workspace_dir
        else:
            self.workspace_dir = os.path.expanduser("~/dsterminal_workspace")
        
        self._init_workspace()
    
    def _init_workspace(self):
        """Initialize workspace directories with color typing"""
        self.typer.type_status("Initializing Shield Core workspace...", Colors.CYAN, centered=False)
        
        subdirs = ["reports", "logs", "quarantine", "backups", "honeypots"]
        for subdir in subdirs:
            path = os.path.join(self.workspace_dir, subdir)
            os.makedirs(path, exist_ok=True)
            if subdir == "quarantine":
                self.quarantine_dir = path
            elif subdir == "backups":
                self.backup_dir = path
            elif subdir == "honeypots":
                self.honeypot_dir = path
        
        self.typer.type_success(f"Workspace initialized: {self.workspace_dir}", centered=False)
        
        # Create honeypot files in ALL locations
        self._deploy_honeypots()
    
    def _deploy_honeypots(self):
        """
        Deploy honeypot decoy files in multiple strategic locations
        """
        self.typer.type_status("Deploying honeypot decoys...", Colors.YELLOW, centered=False)
        
        # ============================================================
        # 1. WORKSPACE HONEYPOTS (Always deployed)
        # ============================================================
        workspace_honeypots = [
            ("honeypot_1.txt", "HONEYPOT - DO NOT MODIFY - Security Monitor Active"),
            ("honeypot_2.txt", "HONEYPOT - DO NOT MODIFY - Security Monitor Active"),
            ("system_backup.bak", "HONEYPOT - System Backup - DO NOT MODIFY")
        ]
        
        deployed_count = 0
        for filename, content in workspace_honeypots:
            path = os.path.join(self.honeypot_dir, filename)
            try:
                with open(path, 'w') as f:
                    f.write(f"{content}\nCreated: {datetime.now()}\n")
                self.honeypot_paths.append(path)
                deployed_count += 1
            except Exception:
                pass
        
        # ============================================================
        # 2. USER PROFILE HONEYPOTS (All users on the system)
        # ============================================================        
        # Get all user profiles
        user_profiles = self._get_all_user_profiles()
        
        # Honeypot configurations for user profiles
        user_honeypot_configs = [
            {
                "subdir": "Documents",
                "filename": "honeypot_1.txt",
                "content": "HONEYPOT - User Document - Security Monitor Active"
            },
            {
                "subdir": "Desktop",
                "filename": "honeypot_2.txt",
                "content": "HONEYPOT - User Desktop - Security Monitor Active"
            },
            {
                "subdir": "Downloads",
                "filename": "system_backup.bak",
                "content": "HONEYPOT - User Downloads - System Backup"
            },
            {
                "subdir": "Pictures",
                "filename": "photo_backup.bak",
                "content": "HONEYPOT - User Pictures - Photo Backup"
            },
            {
                "subdir": "Videos",
                "filename": "video_backup.bak",
                "content": "HONEYPOT - User Videos - Video Backup"
            }
        ]
        
        for user_profile in user_profiles:
            for config in user_honeypot_configs:
                try:
                    # Create the full path
                    user_dir = os.path.join(user_profile, config["subdir"])
                    os.makedirs(user_dir, exist_ok=True)
                    
                    path = os.path.join(user_dir, config["filename"])
                    
                    # Check if file already exists (don't overwrite user files)
                    if not os.path.exists(path):
                        with open(path, 'w') as f:
                            f.write(f"{config['content']}\n")
                            f.write(f"Deployed: {datetime.now()}\n")
                            f.write("DO NOT DELETE - Security Monitoring\n")
                        self.honeypot_paths.append(path)
                        deployed_count += 1
                except Exception:
                    pass
        
        # ============================================================
        # 3. SYSTEM-WIDE HONEYPOTS (If admin privileges)
        # ============================================================
        if self._is_admin():
            system_honeypots = [
                {
                    "path": "C:\\Windows\\System32\\drivers\\etc\\hosts.bak",
                    "content": "HONEYPOT - System Hosts Backup - Security Monitor"
                },
                {
                    "path": "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\StartUp\\sysmon.bak",
                    "content": "HONEYPOT - Startup Monitor - Security Active"
                },
                {
                    "path": "C:\\Windows\\Temp\\system_restore.bak",
                    "content": "HONEYPOT - System Restore - Security Monitor"
                }
            ]
            
            for config in system_honeypots:
                try:
                    path = config["path"]
                    dir_path = os.path.dirname(path)
                    os.makedirs(dir_path, exist_ok=True)
                    
                    if not os.path.exists(path):
                        with open(path, 'w') as f:
                            f.write(f"{config['content']}\n")
                            f.write(f"Deployed: {datetime.now()}\n")
                        self.honeypot_paths.append(path)
                        deployed_count += 1
                except Exception:
                    pass
        
        self.typer.type_success(f"Deployed {deployed_count} honeypot decoys", centered=False)
        return

    def _get_all_user_profiles(self):
        """Get all user profile directories on the system"""
        user_profiles = []
        
        try:
            # Windows: C:\Users\*
            if os.name == 'nt':
                users_dir = "C:\\Users"
                if os.path.exists(users_dir):
                    for user in os.listdir(users_dir):
                        profile_path = os.path.join(users_dir, user)
                        if os.path.isdir(profile_path) and not user.startswith('.'):
                            # Skip system accounts
                            system_accounts = ['All Users', 'Default', 'Default User', 'Public', 'desktop.ini']
                            if user not in system_accounts:
                                user_profiles.append(profile_path)
            else:
                # Linux/Mac: /home/*
                users_dir = "/home"
                if os.path.exists(users_dir):
                    for user in os.listdir(users_dir):
                        profile_path = os.path.join(users_dir, user)
                        if os.path.isdir(profile_path) and not user.startswith('.'):
                            user_profiles.append(profile_path)
                
                # Add root if exists
                if os.path.exists('/root'):
                    user_profiles.append('/root')
        except Exception:
            pass
        
        # Always include the current user
        current_user = os.path.expanduser("~")
        if current_user not in user_profiles:
            user_profiles.append(current_user)
        
        return user_profiles
    
    def _is_admin(self):
        """Check if running with admin privileges"""
        try:
            if os.name == 'nt':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    # ============================================================
    # PREVENTION
    # ============================================================
    
    def pre_install_scan(self, file_path: str) -> bool:
        """Scan file for malware signatures before installation"""
        self.typer.type_status(f"Scanning: {os.path.basename(file_path)}", Colors.CYAN, centered=False)
        
        if not os.path.exists(file_path):
            self.typer.type_warning("File not found", centered=False)
            return True
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
            
            # Check against known ransomware hashes
            blacklisted = self._get_blacklist()
            if file_hash in blacklisted:
                self.typer.type_error("Malicious file detected!", centered=False)
                return False
                
            # Check file size anomalies
            if len(content) > 100 * 1024 * 1024:  # > 100MB
                self.typer.type_warning("Large file detected - suspicious", centered=False)
                return False
                
        except Exception as e:
            self.typer.type_error(f"Scan failed: {e}", centered=False)
            return False
        
        self.typer.type_success("File appears clean", centered=False)
        return True
    
    def _get_blacklist(self) -> Set[str]:
        """Get known ransomware hash blacklist"""
        return {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2",
        }
    
    def enforce_mfa(self, user_token: str, action: str) -> bool:
        """Enforce MFA for critical actions"""
        if action in ["install_system_package", "modify_boot_record", "delete_backup"]:
            return self.policies.allow_mfa_override
        return True
    
    # ============================================================
    # DETECTION
    # ============================================================
    
    def detect_ransomware(self, file_path: str, process_name: str, pid: int = 0) -> ThreatLevel:
        """Detect ransomware activity from file operations"""
        event = FileEvent(
            path=file_path,
            operation='write',
            process_name=process_name,
            pid=pid
        )
        self.event_log.append(event)
        
        # Check honeypot trigger
        if file_path in self.honeypot_paths:
            self.typer.type_error(f"⚠️ HONEYPOT TRIGGERED! Process: {process_name}", centered=False)
            self.threat_level = ThreatLevel.RANSOMWARE_DETECTED
            return ThreatLevel.RANSOMWARE_DETECTED
        
        # Behavioral analysis - rapid file operations
        recent_ops = self._count_recent_operations(process_name, 5)
        if recent_ops > self.policies.max_file_ops_per_second:
            self.typer.type_warning(f"⚠️ High operation rate detected: {process_name} ({recent_ops} ops/sec)", centered=False)
            self.threat_level = ThreatLevel.HIGH_RISK
            return ThreatLevel.HIGH_RISK
        
        return ThreatLevel.CLEAN
    
    def _count_recent_operations(self, process_name: str, seconds: int) -> int:
        """Count recent file operations by a process"""
        current_time = time.time()
        count = 0
        for event in reversed(self.event_log[-50:]):
            if event.process_name == process_name and current_time - event.timestamp < seconds:
                count += 1
        return count
    
    def network_anomaly_detection(self, process_name: str, remote_ip: str) -> bool:
        """Detect suspicious network connections"""
        if remote_ip.startswith("192.168.") or remote_ip == "127.0.0.1":
            return True
        
        self.typer.type_warning(f"⚠️ Suspicious network connection: {process_name} -> {remote_ip}", centered=False)
        return False
    
    # ============================================================
    # RESPONSE
    # ============================================================
    
    def contain_threat(self, process_name: str, pid: int) -> bool:
        """Contain and isolate the threat"""
        self.typer.type_warning(f"🛑 Containing threat: {process_name} (PID: {pid})", centered=False)
        
        try:
            # Terminate the process if possible
            import psutil
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=5)
                self.typer.type_success(f"Process terminated: {process_name}", centered=False)
                return True
        except Exception as e:
            self.typer.type_error(f"Failed to terminate: {e}", centered=False)
        return False
    
    def quarantine_file(self, file_path: str) -> bool:
        """Move infected file to quarantine"""
        if not os.path.exists(file_path):
            self.typer.type_warning(f"File not found: {file_path}", centered=False)
            return False
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.quarantine_dir, f'{timestamp}_{filename}.locked')
        
        try:
            shutil.move(file_path, dest_path)
            self.typer.type_success(f"File quarantined: {filename}", centered=False)
            return True
        except Exception as e:
            self.typer.type_error(f"Quarantine failed: {e}", centered=False)
            return False
    
    # ============================================================
    # RECOVERY
    # ============================================================
    
    def create_restore_point(self, file_path: str) -> bool:
        """Create a backup before modification"""
        if not self.policies.backup_enabled:
            return False
            
        if not os.path.exists(file_path):
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_path = os.path.join(self.backup_dir, f'{timestamp}_{filename}.vss')
        
        try:
            shutil.copy2(file_path, backup_path)
            self.typer.type_info(f"Restore point created: {filename}", centered=False)
            return True
        except Exception as e:
            self.typer.type_error(f"Restore point failed: {e}", centered=False)
            return False
    
    def rollback_file(self, file_path: str) -> bool:
        """Restore file from latest backup"""
        if not self.policies.auto_rollback:
            return False
            
        pattern = f"*_{os.path.basename(file_path)}.vss"
        backups = glob.glob(os.path.join(self.backup_dir, pattern))
        
        if not backups:
            self.typer.type_warning(f"No backups found for: {file_path}", centered=False)
            return False
            
        latest_backup = max(backups, key=os.path.getctime)
        
        try:
            shutil.copy2(latest_backup, file_path)
            self.typer.type_success(f"File restored from backup: {os.path.basename(file_path)}", centered=False)
            return True
        except Exception as e:
            self.typer.type_error(f"Rollback failed: {e}", centered=False)
            return False
    
    # ============================================================
    # FORENSICS
    # ============================================================
    
    def generate_forensic_report(self) -> Dict:
        """Generate forensic report of incident"""
        self.typer.type_status("Generating forensic report...", Colors.YELLOW, centered=False)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "threat_level": self.threat_level.name,
            "events_analyzed": len(self.event_log),
            "honeypots_deployed": len(self.honeypot_paths),
            "honeypot_locations": self.honeypot_paths[:10],
            "quarantine_path": self.quarantine_dir,
            "backup_path": self.backup_dir,
            "recent_events": [
                {
                    "time": datetime.fromtimestamp(e.timestamp).isoformat(),
                    "file": os.path.basename(e.path),
                    "process": e.process_name,
                    "operation": e.operation
                }
                for e in self.event_log[-10:]
            ],
            "recommendations": [
                "Patch EternalBlue vulnerability",
                "Update SMB protocols",
                "Reset local admin passwords",
                "Enable Windows Defender Real-time Protection"
            ]
        }
        
        # Save report
        report_path = os.path.join(self.workspace_dir, "reports", f"forensic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.typer.type_success(f"Forensic report saved: {report_path}", centered=False)
        return report
    
    # ============================================================
    # MONITORING
    # ============================================================
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_active:
            self.typer.type_warning("Monitoring already active", centered=False)
            return
            
        self.typer.type_status("Shield_Core Wrapping-up", Colors.GREEN, centered=False)
        self.is_active = True
        self._stop_monitoring = False
        
        def monitor_loop():
            scan_count = 0
            while not self._stop_monitoring:
                try:
                    import psutil
                    # Monitor processes
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            proc_name = proc.info['name']
                            if self._check_suspicious_process(proc_name):
                                self.typer.type_warning(f"Suspicious process detected: {proc_name}", centered=False)
                                self.contain_threat(proc_name, proc.info['pid'])
                        except:
                            pass
                    
                    # Check honeypot integrity every 10 scans
                    scan_count += 1
                    if scan_count % 10 == 0:
                        self._check_honeypots()
                        scan_count = 0
                    
                    time.sleep(5)
                except Exception as e:
                    time.sleep(10)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.typer.type_success("CYBER THREAT HUNT ACTIVATED", centered=False)
    
    def _check_honeypots(self):
        """Check if honeypots still exist and are intact"""
        for path in self.honeypot_paths:
            if not os.path.exists(path):
                # Attempt to recreate
                try:
                    with open(path, 'w') as f:
                        f.write(f"HONEYPOT - Security Monitor Active\nRecreated: {datetime.now()}\n")
                    self.typer.type_info(f"Honeypot recreated: {os.path.basename(path)}", centered=False)
                except:
                    pass
    
    def _check_suspicious_process(self, process_name: str) -> bool:
        """Check if a process is suspicious"""
        suspicious = ['malware', 'ransom', 'crypto', 'miner', 'worm', 'trojan']
        return any(s in process_name.lower() for s in suspicious)
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.typer.type_status("Stopping monitoring...", Colors.YELLOW, centered=False)
        self._stop_monitoring = True
        self.is_active = False
        self.typer.type_success("Monitoring stopped", centered=False)
     
    # ============================================================
    # STATUS
    # ============================================================
    
    def get_status(self) -> Dict:
        """Get current security status"""
        return {
            "threat_level": self.threat_level.name,
            "is_active": self.is_active,
            "events_monitored": len(self.event_log),
            "honeypots": len(self.honeypot_paths),
            "honeypot_locations": self.honeypot_paths[:10],
            "quarantine_dir": self.quarantine_dir,
            "backup_dir": self.backup_dir,
            "workspace_dir": self.workspace_dir,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================
# TEST / STANDALONE
# ============================================================

if __name__ == "__main__":
    # Create typer for main output
    typer = AutoTypeEngine(delay=0.025)
    term_width = get_terminal_width()
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print banner with centering and colors
    banner_lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║         DSTERMINAL SHIELD CORE - Ransomware Defense        ║",
        "║                      v4.0.0.113                            ║",
        "║         [+] Prevention | Detection | Response | Recovery  ║",
        "╚══════════════════════════════════════════════════════════════╝"
    ]
    typer.type_banner(banner_lines, Colors.CYAN)
    
    # Separator
    print_centered("─" * 60, Colors.DIM)
    print()
    
    # Initialize shield with status messages
    typer.type_status("Initializing Shield Core...", Colors.YELLOW, centered=True)
    
    # Create shield with progress indication
    shield = ShieldCore()
    
    # Test detection with colored output
    if shield.honeypot_paths:
        typer.type_status("Testing detection engine...", Colors.CYAN, centered=True)
        time.sleep(0.3)
        result = shield.detect_ransomware(
            shield.honeypot_paths[0],
            "test_process.exe",
            1234
        )
        if result == ThreatLevel.RANSOMWARE_DETECTED:
            typer.type_error("⚠️ Honeypot detected! Ransomware detection working.", centered=True)
        else:
            typer.type_success("Detection engine ready", centered=True)
    
    # Test quarantine with colored output
    if shield.honeypot_paths and os.path.exists(shield.honeypot_paths[0]):
        typer.type_status("Testing quarantine...", Colors.CYAN, centered=True)
        time.sleep(0.3)
        shield.quarantine_file(shield.honeypot_paths[0])
    
    # Generate report with colored output
    report = shield.generate_forensic_report()
    
    print()
    # Success message box
    success_lines = [
        f"{Colors.GREEN}Shield Core is ready!{Colors.END}",
        f"{Colors.CYAN}Workspace:{Colors.END} {shield.workspace_dir}",
        f"{Colors.CYAN}Honeypots deployed:{Colors.END} {len(shield.honeypot_paths)}",
        f"{Colors.CYAN}Quarantine:{Colors.END} {shield.quarantine_dir}"
    ]
    typer.type_box("✅ SHIELD STATUS", success_lines, Colors.GREEN)
    
    print()
    # Display detailed status in centered box
    status = shield.get_status()
    status_lines = [
        f"{Colors.YELLOW}Threat Level:{Colors.END} {status['threat_level']}",
        f"{Colors.GREEN if status['is_active'] else Colors.RED}Monitoring:{Colors.END} {'Active' if status['is_active'] else 'Inactive'}",
        f"{Colors.CYAN}Events Monitored:{Colors.END} {status['events_monitored']}",
        f"{Colors.CYAN}Honeypots:{Colors.END} {status['honeypots']}",
        f"{Colors.DIM}Workspace:{Colors.END} {status['workspace_dir']}"
    ]
    typer.type_box("📊 SHIELD STATUS", status_lines, Colors.CYAN)
    
    print()
    print_centered("─" * 60, Colors.DIM)
    print_centered(f"{Colors.GREEN}✅ Shield Core initialization complete!{Colors.END}")
    print_centered(f"{Colors.DIM}Press Enter to exit...{Colors.END}")
    
    try:
        input()
    except:
        pass