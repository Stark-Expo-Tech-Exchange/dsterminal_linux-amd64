# soc_automated_lab.py - Complete SOC Automated Lab with Process Monitoring
"""
SOC Automated Lab - Enterprise Security Operations Center
Complete security lab environment with:
- 24/7 Real-time Monitoring & Detection
- AI-Powered Threat Hunting
- Automated Incident Response
- Integrated Interactive Dashboard
- Process & Application Monitoring
- Menu-Driven Interface
- Automated Reporting with DSTERMINAL v4.0.0.113 Watermark
- Cross-platform Support
"""

import os
import sys
import time
import json
import hashlib
import threading
import subprocess
import platform
import logging
import re
import shutil
import queue
import signal
import atexit
import random
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

# Try imports with fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Rich imports for advanced UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.syntax import Syntax
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.align import Align
    from rich.live import Live
    from rich.tree import Tree
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.columns import Columns
    from rich.console import Group
    from rich.padding import Padding
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as PDFTable, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.units import inch, cm
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from jinja2 import Template
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False

from soc_enhanced_modules import EnhancedModulesManager

# ============================================================
# CONSTANTS
# ============================================================

VERSION = "v4.0.0.113"
PLATFORM = "DSTERMINAL Cyber Ops Platform"
WATERMARK_TEXT = f"{PLATFORM} {VERSION}"


# ============================================================
# COLOR SUPPORT DETECTION
# ============================================================

def should_use_colors():
    if os.environ.get('NO_COLOR'):
        return False
    if not sys.stdout.isatty():
        return False
    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return bool(mode.value & 0x4)
            return False
        except:
            return False
    return True

USE_COLORS = should_use_colors()


# ============================================================
# COLORS CLASS
# ============================================================

class Colors:
    """ANSI color codes"""
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
    
    @staticmethod
    def init_colors():
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass

Colors.init_colors()


# ============================================================
# ENUMS AND DATA CLASSES
# ============================================================

class LabStatus(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"

class ThreatSeverity(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1
    
    @property
    def color(self) -> str:
        colors = {
            'CRITICAL': Colors.RED,
            'HIGH': Colors.YELLOW,
            'MEDIUM': Colors.BLUE,
            'LOW': Colors.GREEN,
            'INFO': Colors.CYAN
        }
        return colors.get(self.name, Colors.WHITE)

class ThreatCategory(Enum):
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    DATA_EXFIL = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    PERSISTENCE = "persistence"
    LATERAL_MOVEMENT = "lateral_movement"
    RECONNAISSANCE = "reconnaissance"
    ZERO_DAY = "zero_day"
    SUSPICIOUS = "suspicious"
    PROCESS_THREAT = "process_threat"

class ThreatStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    NEUTRALIZED = "neutralized"
    RESOLVED = "resolved"
    MONITORING = "monitoring"

@dataclass
class ProcessInfo:
    """Information about a running process"""
    pid: int
    name: str
    cmdline: str
    start_time: datetime
    duration: float  # seconds
    cpu_percent: float
    memory_mb: float
    status: str
    threats: List['ThreatEvent'] = field(default_factory=list)
    last_scan: Optional[datetime] = None
    is_system_process: bool = False

@dataclass
class ThreatIndicator:
    indicator: str
    indicator_type: str
    severity: ThreatSeverity
    category: ThreatCategory
    description: str
    source: str
    first_seen: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5

@dataclass
class ThreatEvent:
    event_id: str
    timestamp: datetime
    severity: ThreatSeverity
    category: ThreatCategory
    status: ThreatStatus
    source: str
    source_detail: str
    description: str
    indicators: List[ThreatIndicator] = field(default_factory=list)
    affected_assets: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    process_pid: Optional[int] = None
    process_name: Optional[str] = None

@dataclass
class LabResult:
    experiment_id: str
    timestamp: datetime
    name: str
    status: LabStatus
    metrics: Dict[str, Any]
    findings: List[ThreatEvent]
    duration: float

@dataclass
class LabReport:
    report_id: str
    timestamp: datetime
    format: str
    filepath: str
    size: int
    summary: str


# ============================================================
# PROCESS MONITOR - FIXED
# ============================================================
# ============================================================
# PROCESS MONITOR - COMPLETE FIX
# ============================================================

class ProcessMonitor:
    """Monitor running processes and detect threats"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.processes = {}  # pid -> ProcessInfo
        self.process_history = deque(maxlen=10000)
        self.monitoring = False
        self.logger = logging.getLogger('SOC_Lab.ProcessMonitor')
        self.scan_interval = 3  # seconds - faster scanning
        self.threat_detection_enabled = True
        self._scan_thread = None
        self._stop_event = threading.Event()
        self._initial_scan_done = False
        
        # Known suspicious process patterns
        self.suspicious_patterns = {
            'cryptolocker': ['cryptolocker', 'decrypt', 'encrypt', 'ransom'],
            'malware': ['malware', 'virus', 'trojan', 'worm', 'backdoor', 'rootkit'],
            'mining': ['miner', 'mining', 'crypto', 'bitcoin', 'ethereum', 'monero'],
            'keylogger': ['keylog', 'keyboard', 'logger', 'spy', 'hook'],
            'ransomware': ['ransom', 'encrypt', 'decrypt', 'lock', 'pay'],
            'phishing': ['phish', 'login', 'verify', 'update', 'confirm'],
            'suspicious': ['nc', 'netcat', 'nmap', 'masscan', 'sqlmap', 'hydra'],
        }
        
        # Known safe system processes
        self.safe_processes = {
            'windows': [
                'svchost.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe', 
                'lsass.exe', 'services.exe', 'wininit.exe', 'system', 'smss.exe',
                'conhost.exe', 'dwm.exe', 'taskhost.exe', 'spoolsv.exe',
                'SearchIndexer.exe', 'MsMpEng.exe', 'SecurityHealthService.exe',
                'wininit.exe', 'fontdrvhost.exe', 'sihost.exe', 'taskhostw.exe',
                'ctfmon.exe', 'runtimebroker.exe', 'shellhost.exe',
                'MicrosoftEdge.exe', 'SearchHost.exe', 'StartMenuExperienceHost.exe',
                'TextInputHost.exe', 'Widgets.exe', 'SecurityHealthSystray.exe',
                'SystemSettings.exe', 'Settings.exe', 'powershell.exe', 'cmd.exe',
                'conhost.exe', 'WindowsTerminal.exe', 'python.exe', 'python3.exe'
            ],
            'linux': [
                'systemd', 'init', 'kthreadd', 'rcu_sched', 'kworker', 
                'python3', 'python', 'bash', 'sh', 'zsh', 'sshd', 'cron',
                'dbus-daemon', 'NetworkManager', 'polkitd', 'accounts-daemon',
                'gdm', 'Xorg', 'gnome-shell', 'nautilus', 'gnome-terminal'
            ],
            'macos': [
                'launchd', 'kernel_task', 'WindowServer', 'loginwindow', 'Dock',
                'Finder', 'SystemUIServer', 'NotificationCenter', 'cfprefsd',
                'mdworker', 'mds', 'mds_stores', 'Terminal', 'iTerm2'
            ]
        }
        
        # Check if psutil is available
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not installed. Process monitoring disabled.")
            print("âš ï¸ psutil not installed. Install with: pip install psutil")
        else:
            print("âœ… psutil found - Process monitoring available")
    
    def start_monitoring(self):
        """Start process monitoring"""
        if not PSUTIL_AVAILABLE:
            self.logger.error("Cannot start process monitoring: psutil not available")
            return False
        
        if self.monitoring:
            return True
        
        self.monitoring = True
        self._stop_event.clear()
        
        # Do an initial scan immediately
        self._initial_scan_done = False
        self._scan_processes()
        self._initial_scan_done = True
        
        # Start background thread
        self._start_scan_thread()
        # Remove duplicate print - only print once
        return True

    def stop_monitoring(self):
        """Stop process monitoring"""
        self.monitoring = False
        self._stop_event.set()
        if self._scan_thread:
            self._scan_thread.join(timeout=3)
        self.logger.info("Process monitoring stopped")
        print("âœ… Process monitoring stopped")
    
    def _start_scan_thread(self):
        """Start background process scanning thread"""
        def scan_loop():
            self.logger.info("Process scan thread started")
            scan_count = 0
            while self.monitoring and not self._stop_event.is_set():
                try:
                    self._scan_processes()
                    scan_count += 1
                    if scan_count % 10 == 0:
                        self.logger.info(f"Process scan #{scan_count}: {len(self.processes)} processes tracked")
                except Exception as e:
                    self.logger.error(f"Process scan error: {e}")
                
                # Sleep in small intervals to allow quick stop
                for _ in range(self.scan_interval):
                    if self._stop_event.is_set() or not self.monitoring:
                        break
                    time.sleep(1)
            self.logger.info("Process scan thread stopped")
        
        self._scan_thread = threading.Thread(target=scan_loop, daemon=True)
        self._scan_thread.start()
    
    def _scan_processes(self):
        """Scan running processes"""
        if not PSUTIL_AVAILABLE:
            return
        
        current_pids = set()
        new_processes = []
        removed_processes = []
        
        try:
            # Try multiple methods to get processes
            processes_found = 0
            
            # Method 1: Use psutil process_iter
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 
                                            'cpu_percent', 'memory_info', 'status', 'username']):
                try:
                    pid = proc.info['pid']
                    current_pids.add(pid)
                    processes_found += 1
                    name = proc.info.get('name', 'unknown')
                    
                    # Check if process is already tracked
                    if pid in self.processes:
                        # Update existing process
                        proc_info = self.processes[pid]
                        proc_info.duration = time.time() - proc_info.start_time.timestamp()
                        proc_info.cpu_percent = proc.info.get('cpu_percent', 0)
                        if proc.info.get('memory_info'):
                            proc_info.memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        proc_info.status = proc.info.get('status', 'running')
                        proc_info.name = name
                    else:
                        # New process detected
                        create_time = proc.info.get('create_time', time.time())
                        start_time = datetime.fromtimestamp(create_time)
                        
                        cmdline = proc.info.get('cmdline', [])
                        cmdline_str = ' '.join(str(c) for c in cmdline if c) if cmdline else name
                        
                        proc_info = ProcessInfo(
                            pid=pid,
                            name=name,
                            cmdline=cmdline_str[:200],
                            start_time=start_time,
                            duration=time.time() - create_time,
                            cpu_percent=proc.info.get('cpu_percent', 0),
                            memory_mb=proc.info.get('memory_info', psutil._common.pmem(0)).rss / (1024 * 1024) if proc.info.get('memory_info') else 0,
                            status=proc.info.get('status', 'running'),
                            is_system_process=self._is_system_process(name)
                        )
                        
                        self.processes[pid] = proc_info
                        self.process_history.append(proc_info)
                        new_processes.append(proc_info)
                        
                        self.logger.info(f"New process detected: {name} (PID: {pid})")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    self.logger.debug(f"Error processing process: {e}")
                    continue
            
            # Remove processes that no longer exist
            for pid in list(self.processes.keys()):
                if pid not in current_pids:
                    proc_info = self.processes.pop(pid)
                    removed_processes.append(proc_info)
                    self.logger.info(f"Process ended: {proc_info.name} (PID: {pid})")
            
            # If no processes found, try an alternative method on Windows
            if processes_found == 0 and platform.system() == 'Windows':
                self.logger.warning("No processes found with psutil, trying alternative method...")
                try:
                    # Use tasklist command as fallback
                    result = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], 
                                        capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if line.strip():
                                parts = line.strip().split(',')
                                if len(parts) >= 2:
                                    name = parts[0].strip('"')
                                    pid_str = parts[1].strip('"')
                                    try:
                                        pid = int(pid_str)
                                        if pid not in self.processes:
                                            # Add basic process info
                                            proc_info = ProcessInfo(
                                                pid=pid,
                                                name=name,
                                                cmdline=name,
                                                start_time=datetime.now(),
                                                duration=0,
                                                cpu_percent=0,
                                                memory_mb=0,
                                                status='running',
                                                is_system_process=self._is_system_process(name)
                                            )
                                            self.processes[pid] = proc_info
                                            processes_found += 1
                                    except ValueError:
                                        continue
                except Exception as e:
                    self.logger.debug(f"Fallback process scan failed: {e}")
            
            # Log scan summary
            if processes_found > 0:
                self.logger.info(f"Process scan complete: {processes_found} total, "
                            f"{len(new_processes)} new, {len(removed_processes)} removed")
                if not self._initial_scan_done:
                    self._initial_scan_done = True
            else:
                self.logger.warning("No processes found during scan. Check permissions.")
                
        except Exception as e:
            self.logger.error(f"Error scanning processes: {e}")
            
    def _is_system_process(self, name: str) -> bool:
        """Check if process is a system process"""
        if not name:
            return False
        
        name_lower = name.lower()
        
        # Get platform-specific safe processes
        system_procs = []
        if platform.system() == 'Windows':
            system_procs = self.safe_processes.get('windows', [])
        elif platform.system() == 'Linux':
            system_procs = self.safe_processes.get('linux', [])
        elif platform.system() == 'Darwin':
            system_procs = self.safe_processes.get('macos', [])
        
        # Check exact match or partial match
        for p in system_procs:
            if name_lower == p.lower():
                return True
            # Check if the process name ends with the safe process name
            if name_lower.endswith(p.lower()):
                return True
        
        # Check for common system process patterns
        system_patterns = ['system', 'nt authority', 'root', 'sys', 'daemon', 'service']
        try:
            # Check username if possible
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'username']):
                    if proc.info['pid'] == self.processes.get(name_lower, {}).get('pid', 0):
                        username = proc.info.get('username', '').lower()
                        for pattern in system_patterns:
                            if pattern in username:
                                return True
        except:
            pass
        
        return False
    
    def _scan_process_for_threats(self, proc_info: ProcessInfo, proc: psutil.Process):
        """Scan a process for potential threats"""
        if not self.threat_detection_enabled:
            return
        
        threats = []
        name_lower = proc_info.name.lower()
        cmdline_lower = proc_info.cmdline.lower()
        
        # Skip if it's a system process
        if proc_info.is_system_process:
            proc_info.last_scan = datetime.now()
            return
        
        # Check against suspicious patterns
        for threat_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if pattern in name_lower or pattern in cmdline_lower:
                    severity = ThreatSeverity.HIGH
                    if threat_type in ['ransomware', 'cryptolocker']:
                        severity = ThreatSeverity.CRITICAL
                    elif threat_type == 'mining':
                        severity = ThreatSeverity.MEDIUM
                    
                    # Check if this is a new threat
                    existing_threats = [t for t in proc_info.threats if t.category.value == threat_type]
                    if not existing_threats:
                        threat = self._create_process_threat(
                            severity=severity,
                            category=ThreatCategory.PROCESS_THREAT,
                            description=f"Suspicious process detected: {proc_info.name} (Pattern: {pattern})",
                            proc_info=proc_info,
                            threat_type=threat_type
                        )
                        threats.append(threat)
                        self.logger.warning(f"Threat detected in process {proc_info.name}: {threat_type}")
        
        # Check for high resource usage (potential mining or DoS) - only for non-system processes
        if not proc_info.is_system_process:
            if proc_info.cpu_percent > 80 and proc_info.duration > 60:
                threat = self._create_process_threat(
                    severity=ThreatSeverity.MEDIUM,
                    category=ThreatCategory.PROCESS_THREAT,
                    description=f"High CPU usage detected: {proc_info.name} ({proc_info.cpu_percent:.1f}%)",
                    proc_info=proc_info,
                    threat_type="high_cpu"
                )
                threats.append(threat)
            
            if proc_info.memory_mb > 500 and proc_info.duration > 60:
                threat = self._create_process_threat(
                    severity=ThreatSeverity.MEDIUM,
                    category=ThreatCategory.PROCESS_THREAT,
                    description=f"High memory usage detected: {proc_info.name} ({proc_info.memory_mb:.1f} MB)",
                    proc_info=proc_info,
                    threat_type="high_memory"
                )
                threats.append(threat)
        
        # Add threats to process info
        for threat in threats:
            if threat not in proc_info.threats:
                proc_info.threats.append(threat)
        
        proc_info.last_scan = datetime.now()
    
    def _create_process_threat(self, severity: ThreatSeverity, category: ThreatCategory,
                              description: str, proc_info: ProcessInfo, threat_type: str) -> ThreatEvent:
        """Create a threat event for a process"""
        event_id = f"PROC-THREAT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hashlib.md5(description.encode()).hexdigest()[:6]}"
        
        return ThreatEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            status=ThreatStatus.DETECTED,
            source='process_monitor',
            source_detail=f"PID: {proc_info.pid} - {proc_info.name}",
            description=description,
            indicators=[
                ThreatIndicator(
                    indicator=threat_type,
                    indicator_type='process_behavior',
                    severity=severity,
                    category=category,
                    description=f"Process behavior: {threat_type}",
                    source=f"PID: {proc_info.pid}"
                )
            ],
            affected_assets=[proc_info.name],
            suggested_actions=[
                "Review process for legitimacy",
                "Check network connections",
                "Run antivirus scan",
                "Verify digital signature"
            ],
            process_pid=proc_info.pid,
            process_name=proc_info.name
        )
    
    def get_processes(self) -> List[ProcessInfo]:
        """Get all monitored processes"""
        return list(self.processes.values())
    
    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """Get process by PID"""
        return self.processes.get(pid)
    
    def get_threat_processes(self) -> List[ProcessInfo]:
        """Get processes with detected threats"""
        return [p for p in self.processes.values() if p.threats]
    
    def get_statistics(self) -> Dict:
        """Get process monitoring statistics"""
        total = len(self.processes)
        with_threats = len(self.get_threat_processes())
        system_procs = sum(1 for p in self.processes.values() if p.is_system_process)
        user_procs = total - system_procs
        
        return {
            'total_processes': total,
            'processes_with_threats': with_threats,
            'system_processes': system_procs,
            'user_processes': user_procs,
            'is_monitoring': self.monitoring
        }
# ============================================================
# AI THREAT DETECTION ENGINE (Enhanced - Real-time, No False Positives)
# ============================================================
# ============================================================
# AI THREAT DETECTION ENGINE - COMPLETE FIXED VERSION (Fixed Regex)
# ============================================================

class AIThreatDetectionEngine:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.indicators = []
        self.logger = logging.getLogger('SOC_Lab.ThreatEngine')
        self.process_monitor = None
        
        # Known safe files - Windows system files that should never be flagged
        self.safe_files = {
            # Windows System32 safe files
            'radardt.dll': 'Windows RADAR',
            'radarrs.dll': 'Windows RADAR',
            'rstrtmgr.dll': 'Windows Restart Manager',
            'dps.dll': 'Windows Diagnostic Policy Service',
            'microsoft-windows-system-events.dll': 'Windows System Events',
            'windows.ui.xaml.dll': 'Windows UI XAML',
            'windows.ui.dll': 'Windows UI',
            'windows.storage.dll': 'Windows Storage',
            'windows.applicationmodel.dll': 'Windows Application Model',
            'ntdll.dll': 'Windows NT DLL',
            'kernel32.dll': 'Windows Kernel32',
            'kernelbase.dll': 'Windows Kernel Base',
            'user32.dll': 'Windows User32',
            'gdi32.dll': 'Windows GDI32',
            'advapi32.dll': 'Windows AdvAPI32',
            'shell32.dll': 'Windows Shell32',
            'ole32.dll': 'Windows OLE32',
            'comdlg32.dll': 'Windows Common Dialog',
            'winmm.dll': 'Windows Multimedia',
            'ws2_32.dll': 'Windows Winsock2',
            'crypt32.dll': 'Windows Crypto32',
            'secur32.dll': 'Windows Security32',
        }
        
        # Safe file extensions (never flag these)
        self.safe_extensions = [
            '.dll', '.sys', '.cat', '.inf', '.mui', '.manifest', '.ini',
            '.conf', '.config', '.xml', '.xsd', '.xsl', '.dtd',
            '.ttf', '.otf', '.fon', '.pfm', '.pfb',
            '.hlp', '.chm', '.cnt', '.gid',
            '.nls', '.loc', '.prf', '.mpf',
            '.lnk',  # Shortcuts are safe
            '.ps1',  # PowerShell scripts are not inherently malicious
            '.py',   # Python scripts are not inherently malicious
            '.js',   # JavaScript files are not inherently malicious
            '.html', '.htm',  # HTML files are not inherently malicious
            '.css',  # CSS files are safe
            '.json', '.yaml', '.yml', '.toml',  # Config files are safe
            '.md', '.txt', '.log',  # Text files are safe
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',  # Images are safe
            '.mp3', '.mp4', '.avi', '.mov', '.wav',  # Media files are safe
            '.zip', '.tar', '.gz', '.rar', '.7z',  # Archives are safe
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents are safe
            '.exe',  # We'll check specific known-safe EXEs separately
        ]
        
        # Known safe executable names
        self.safe_executables = [
            'svchost.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe',
            'lsass.exe', 'services.exe', 'wininit.exe', 'system',
            'smss.exe', 'conhost.exe', 'dwm.exe', 'taskhost.exe',
            'spoolsv.exe', 'SearchIndexer.exe', 'MsMpEng.exe',
            'SecurityHealthService.exe', 'taskmgr.exe', 'regedit.exe',
            'cmd.exe', 'powershell.exe', 'notepad.exe', 'calc.exe',
            'mspaint.exe', 'snippingtool.exe', 'osk.exe', 'magnify.exe',
            'winword.exe', 'excel.exe', 'powerpnt.exe', 'outlook.exe',
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe',
            'python.exe', 'python3.exe', 'java.exe', 'javaw.exe',
            'node.exe', 'npm.exe', 'git.exe', 'bash.exe', 'wsl.exe',
            'wt.exe', 'WindowsTerminal.exe', 'Code.exe', 'cursor.exe',
            'nmap.exe', 'zenmap.exe', 'ai_threat_intelligence.exe',
        ]
        
        # Safe directory patterns (using simple string matching, not regex)
        self.safe_directories = [
            'c:\\windows', 'c:\\program files', 'c:\\program files (x86)',
            'c:\\users\\appdata\\local\\programs',
            'c:\\users\\appdata\\roaming\\microsoft',
            'c:\\users\\appdata\\local\\microsoft',
            'c:\\users\\appdata\\local\\temp',
            'c:\\python', 'c:\\python3', '/usr/bin', '/usr/local/bin',
            '/opt', '/home/.local', '/home/.config',
            '\\program files\\', '\\program files (x86)\\',
            '\\windows\\system32\\', '\\windows\\syswow64\\',
            'dsterminal_workspace', 'soc_ai_workspace', 'soc_lab_workspace',
        ]
        
        # Known threat patterns - ONLY very specific patterns
        self.threat_patterns = {
            'ransomware': {
                'extensions': ['.encrypted', '.locked', '.ransom'],
                'patterns': ['ransomware', 'cryptolocker', 'wannacry', 'locky', 'petya'],
                'exact_match': True
            },
            'malware': {
                'extensions': ['.virus', '.trojan', '.worm', '.backdoor'],
                'patterns': ['malware_dropper', 'virus_injector', 'trojan_horse'],
                'exact_match': True
            },
            'mining': {
                'patterns': ['cpuminer', 'ccminer', 'xmrig', 'nanominer', 'minerd'],
                'exact_match': True
            },
            'keylogger': {
                'patterns': ['keylogger.exe', 'spyware_agent', 'hook_injector'],
                'exact_match': True
            }
        }
        
        # Workspace directory - don't flag our own files
        self.workspace_dir = workspace_path.lower()
        
        self.logger.info("AI Threat Detection Engine initialized with improved safe file list")
    
    def set_process_monitor(self, process_monitor: ProcessMonitor):
        """Set the process monitor instance"""
        self.process_monitor = process_monitor
    
    def analyze_file(self, filepath: str) -> List[ThreatEvent]:
        """Analyze a file for threats - REAL-TIME with no false positives"""
        events = []
        
        # Quick check - skip if file doesn't exist
        if not os.path.exists(filepath):
            return events
        
        file_info = self._get_file_info(filepath)
        if not file_info:
            return events
        
        # Check if file is safe (known safe file)
        if self._is_safe_file(filepath, file_info):
            return events
        
        # Check if file is in a safe directory
        if self._is_in_safe_directory(filepath):
            return events
        
        # Check if file has safe extension
        if self._has_safe_extension(file_info['extension']):
            return events
        
        # Check if it's a safe executable
        if self._is_safe_executable(file_info['name']):
            return events
        
        # Skip our own workspace files
        if self._is_workspace_file(filepath):
            return events
        
        # Only check files in user directories (Downloads, Desktop, etc.)
        if not self._is_in_user_directory(filepath):
            return events
        
        # Now perform threat analysis - only for truly suspicious files
        findings = self._analyze(filepath, file_info)
        if findings:
            event = self._create_threat_event(
                severity=ThreatSeverity.HIGH,
                category=ThreatCategory.SUSPICIOUS,
                description=f"âš ï¸ Suspicious file detected: {os.path.basename(filepath)}",
                source='file',
                source_detail=filepath,
                indicators=findings
            )
            events.append(event)
            self.logger.warning(f"THREAT DETECTED: {filepath}")
        
        return events
    
    def _is_safe_file(self, filepath: str, file_info: Dict) -> bool:
        """Check if file is known safe"""
        name = file_info['name'].lower()
        
        # Check against known safe files
        if name in self.safe_files:
            return True
        
        # Check for Microsoft signed files
        if 'microsoft' in name or 'windows' in name:
            return True
        
        # Check if it's a legitimate Windows file
        windows_patterns = ['api-ms-', 'ext-ms-', 'msvc', 'vcruntime', 'ucrtbase']
        for pattern in windows_patterns:
            if name.startswith(pattern):
                return True
        
        # Check for our own AI files
        if 'ai_threat' in name.lower() or 'soc_' in name.lower():
            return True
        
        return False
    
    def _is_in_safe_directory(self, filepath: str) -> bool:
        """Check if file is in a safe system directory - SIMPLE STRING MATCHING"""
        filepath_lower = filepath.lower()
        
        # Check each safe directory pattern
        for safe_dir in self.safe_directories:
            # Simple string containment check (no regex)
            if safe_dir in filepath_lower:
                return True
        
        return False
    
    def _has_safe_extension(self, extension: str) -> bool:
        """Check if file has a safe extension"""
        return extension in self.safe_extensions
    
    def _is_safe_executable(self, name: str) -> bool:
        """Check if it's a known safe executable"""
        return name.lower() in self.safe_executables
    
    def _is_workspace_file(self, filepath: str) -> bool:
        """Check if file is in our workspace"""
        return self.workspace_dir in filepath.lower()
    
    def _is_in_user_directory(self, filepath: str) -> bool:
        """Check if file is in a user directory (Downloads, Desktop, etc.)"""
        filepath_lower = filepath.lower()
        
        # Check for user directory patterns
        user_patterns = [
            '\\downloads\\', '\\desktop\\', '\\documents\\', '\\pictures\\',
            '\\videos\\', '\\music\\', '\\projects\\', '\\workspace\\',
            '/downloads/', '/desktop/', '/documents/', '/pictures/',
            '/videos/', '/music/', '/projects/', '/workspace/'
        ]
        
        for pattern in user_patterns:
            if pattern in filepath_lower:
                return True
        
        return False
    
    def _analyze(self, filepath: str, file_info: Dict) -> List[ThreatIndicator]:
        """Analyze file for threats - only truly suspicious patterns"""
        indicators = []
        name = file_info['name'].lower()
        
        # Check for very specific threat patterns only
        for category, patterns in self.threat_patterns.items():
            # Check patterns
            for pattern in patterns.get('patterns', []):
                if patterns.get('exact_match', False):
                    # Exact match required
                    if pattern in name or pattern in name.replace(' ', ''):
                        indicators.append(ThreatIndicator(
                            indicator=pattern,
                            indicator_type='pattern',
                            severity=ThreatSeverity.HIGH,
                            category=ThreatCategory.SUSPICIOUS,
                            description=f"Match: {pattern}",
                            source=filepath,
                            confidence=0.8
                        ))
                else:
                    # Partial match with context
                    if pattern in name:
                        indicators.append(ThreatIndicator(
                            indicator=pattern,
                            indicator_type='pattern',
                            severity=ThreatSeverity.HIGH,
                            category=ThreatCategory.SUSPICIOUS,
                            description=f"Match: {pattern}",
                            source=filepath,
                            confidence=0.7
                        ))
            
            # Check extensions
            for ext in patterns.get('extensions', []):
                if file_info['extension'] == ext:
                    indicators.append(ThreatIndicator(
                        indicator=ext,
                        indicator_type='extension',
                        severity=ThreatSeverity.HIGH,
                        category=ThreatCategory.SUSPICIOUS,
                        description=f"Extension: {ext}",
                        source=filepath,
                        confidence=0.7
                    ))
        
        return indicators
    
    def _get_file_info(self, filepath: str):
        """Get file information"""
        try:
            return {
                'name': os.path.basename(filepath),
                'extension': os.path.splitext(filepath)[1].lower(),
                'size': os.path.getsize(filepath),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)),
                'created': datetime.fromtimestamp(os.path.getctime(filepath))
            }
        except:
            return None

    def _create_threat_event(self, severity: ThreatSeverity, category: ThreatCategory,
                           description: str, source: str, source_detail: str,
                           indicators: List[ThreatIndicator]) -> ThreatEvent:
        """Create a threat event"""
        event_id = f"THREAT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hashlib.md5(description.encode()).hexdigest()[:6]}"
        return ThreatEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            status=ThreatStatus.DETECTED,
            source=source,
            source_detail=source_detail,
            description=description,
            indicators=indicators,
            affected_assets=[source_detail],
            suggested_actions=[
                "Review file for legitimacy",
                "Check file origin",
                "Run antivirus scan",
                "Verify digital signature"
            ]
        )
# ============================================================
# FILE SYSTEM MONITOR (Enhanced)
# ============================================================

class LabMonitor(FileSystemEventHandler):
    def __init__(self, workspace_path: str, ai_engine: AIThreatDetectionEngine, config: Dict):
        self.workspace_path = workspace_path
        self.ai_engine = ai_engine
        self.config = config
        self.event_queue = deque(maxlen=10000)
        self.threat_events = []
        self.monitoring = False
        self.observer = None
        self.logger = logging.getLogger('SOC_Lab.Monitor')
        self.paused = False
        self.stats = {'events_processed': 0, 'files_scanned': 0, 'threats_detected': 0}
        
        self._setup_workspace()
    
    def _setup_workspace(self):
        dirs = ['logs', 'reports', 'quarantine', 'results']
        for d in dirs:
            os.makedirs(os.path.join(self.workspace_path, d), exist_ok=True)
    
    def start_monitoring(self, paths: List[str]) -> bool:
        if not WATCHDOG_AVAILABLE:
            return False
        if self.monitoring:
            return True
        
        try:
            self.monitoring = True
            self.observer = Observer()
            for path in paths:
                if os.path.exists(path):
                    self.observer.schedule(self, path, recursive=True)
            self.observer.start()
            self._start_processing()
            return True
        except Exception as e:
            print(f"âŒ Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.monitoring = False
            return True
        return False
    
    def _start_processing(self):
        def process():
            while self.monitoring:
                if not self.paused and self.event_queue:
                    event = self.event_queue.popleft()
                    self._process_event(event)
                time.sleep(0.1)
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def on_created(self, event):
        if not event.is_directory and not self.paused:
            self.event_queue.append(('created', event.src_path))
    
    def on_modified(self, event):
        if not event.is_directory and not self.paused:
            self.event_queue.append(('modified', event.src_path))
    
    def _process_event(self, event):
        event_type, filepath = event[0], event[1]
        if self._is_workspace_file(filepath) or self._is_system_file(filepath):
            return
        
        if event_type in ['created', 'modified'] and os.path.exists(filepath):
            self.stats['files_scanned'] += 1
            threats = self.ai_engine.analyze_file(filepath)
            if threats:
                self.stats['threats_detected'] += len(threats)
                self.threat_events.extend(threats)
                self.logger.warning(f"THREAT: {filepath}")
    
    def _is_system_file(self, filepath: str) -> bool:
        system_exts = ['.tmp', '.log', '.cache', '.pyc']
        return os.path.splitext(filepath)[1].lower() in system_exts
    
    def _is_workspace_file(self, filepath: str) -> bool:
        return filepath.startswith(self.workspace_path)
    
    def get_statistics(self) -> Dict:
        return {
            'total_alerts': len(self.threat_events),
            'active_threats': len(self.threat_events),
            'events_processed': self.stats['events_processed'],
            'files_scanned': self.stats['files_scanned'],
            'threats_detected': self.stats['threats_detected'],
            'is_monitoring': self.monitoring
        }
    
    def get_threats(self) -> List[Dict]:
        return [{
            'event_id': e.event_id,
            'timestamp': e.timestamp.isoformat(),
            'severity': e.severity.name,
            'category': e.category.value,
            'status': e.status.value,
            'description': e.description,
            'source': e.source_detail
        } for e in self.threat_events]


# ============================================================
# REPORT GENERATOR WITH WATERMARK
# ============================================================

class ReportGenerator:
    """Generate reports in various formats with DSTERMINAL watermark"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.reports_path = os.path.join(workspace_path, 'reports')
        os.makedirs(self.reports_path, exist_ok=True)
        self.logger = logging.getLogger('SOC_Lab.ReportGen')
        self.reports = []  # Track generated reports
        
    def generate_report(self, monitor: LabMonitor, ai_engine: AIThreatDetectionEngine,
                       report_format: str = 'pdf', lab_state: str = 'IDLE',
                       process_monitor: ProcessMonitor = None) -> str:
        """Generate a report in the specified format"""
        
        timestamp = datetime.now()
        report_id = f"RPT-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        filename = f"lab_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.{report_format}"
        filepath = os.path.join(self.reports_path, filename)
        
        # Collect data
        stats = monitor.get_statistics()
        threats = monitor.get_threats()
        process_stats = process_monitor.get_statistics() if process_monitor else {}
        processes = process_monitor.get_processes() if process_monitor else []
        
        # Generate report based on format
        if report_format == 'pdf':
            filepath = self._generate_pdf_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        elif report_format == 'html':
            filepath = self._generate_html_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        elif report_format == 'json':
            filepath = self._generate_json_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        else:  # txt
            filepath = self._generate_txt_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        
        # Track the report
        if filepath and os.path.exists(filepath):
            report = LabReport(
                report_id=report_id,
                timestamp=timestamp,
                format=report_format,
                filepath=filepath,
                size=os.path.getsize(filepath),
                summary=f"Report generated with {len(threats)} threats detected"
            )
            self.reports.append(report)
            return filepath
        
        return None
    
    def _add_watermark(self, canvas_obj, doc):
        """Add DSTERMINAL watermark to PDF pages"""
        canvas_obj.saveState()
        canvas_obj.setFillColor(colors.HexColor('#cccccc'))
        canvas_obj.setFont('Helvetica-Bold', 40)
        canvas_obj.rotate(45)
        canvas_obj.drawString(150, 100, WATERMARK_TEXT)
        canvas_obj.setFillColor(colors.HexColor('#dddddd'))
        canvas_obj.setFont('Helvetica', 20)
        canvas_obj.rotate(-30)
        canvas_obj.drawString(400, -50, WATERMARK_TEXT)
        canvas_obj.restoreState()
    
    def _generate_pdf_report(self, filepath: str, report_id: str, stats: Dict, threats: List, lab_state: str, timestamp: datetime, process_stats: Dict, processes: List) -> str:
        """Generate PDF report with watermark"""
        if not REPORTLAB_AVAILABLE:
            return self._generate_txt_report(filepath.replace('.pdf', '.txt'), report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                title=f"SOC Lab Report - {report_id}"
            )
            
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0066cc'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#004d99'),
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_LEFT,
                spaceAfter=6,
                fontName='Helvetica'
            )
            
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceAfter=4
            )
            
            story = []
            
            # Title
            story.append(Paragraph("SOC Automated Lab Report", title_style))
            story.append(Paragraph(f"Report ID: {report_id}", body_style))
            story.append(Paragraph(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
            story.append(Paragraph(f"System: {platform.node()}", body_style))
            story.append(Spacer(1, 20))
            
            # Summary
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Paragraph(f"Lab State: {lab_state}", body_style))
            story.append(Paragraph(f"Total Alerts: {stats.get('total_alerts', 0)}", body_style))
            story.append(Paragraph(f"Active Threats: {stats.get('active_threats', 0)}", body_style))
            story.append(Paragraph(f"Files Scanned: {stats.get('files_scanned', 0)}", body_style))
            story.append(Paragraph(f"Total Processes: {process_stats.get('total_processes', 0)}", body_style))
            story.append(Paragraph(f"Processes with Threats: {process_stats.get('processes_with_threats', 0)}", body_style))
            story.append(Spacer(1, 20))
            
            # Process Statistics
            if process_stats:
                story.append(Paragraph("Process Monitoring", heading_style))
                proc_data = [
                    ['Metric', 'Value'],
                    ['Total Processes', str(process_stats.get('total_processes', 0))],
                    ['System Processes', str(process_stats.get('system_processes', 0))],
                    ['User Processes', str(process_stats.get('user_processes', 0))],
                    ['Processes with Threats', str(process_stats.get('processes_with_threats', 0))],
                ]
                
                proc_table = PDFTable(proc_data, colWidths=[3*inch, 3*inch])
                proc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ]))
                story.append(proc_table)
                story.append(Spacer(1, 20))
            
            # Statistics Table
            story.append(Paragraph("File System Statistics", heading_style))
            stats_data = [
                ['Metric', 'Value'],
                ['Total Alerts', str(stats.get('total_alerts', 0))],
                ['Active Threats', str(stats.get('active_threats', 0))],
                ['Events Processed', str(stats.get('events_processed', 0))],
                ['Files Scanned', str(stats.get('files_scanned', 0))],
                ['Threats Detected', str(stats.get('threats_detected', 0))],
            ]
            
            stats_table = PDFTable(stats_data, colWidths=[3*inch, 3*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # Running Processes
            if processes:
                story.append(Paragraph("Running Processes", heading_style))
                proc_list_data = [['PID', 'Name', 'Duration', 'CPU%', 'Memory(MB)', 'Threats']]
                for p in processes[:20]:
                    proc_list_data.append([
                        str(p.pid),
                        p.name[:20],
                        f"{int(p.duration // 60)}m {int(p.duration % 60)}s",
                        f"{p.cpu_percent:.1f}",
                        f"{p.memory_mb:.1f}",
                        str(len(p.threats))
                    ])
                
                proc_list_table = PDFTable(proc_list_data, colWidths=[0.8*inch, 1.5*inch, 1.2*inch, 0.8*inch, 1*inch, 0.8*inch])
                proc_list_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(proc_list_table)
            
            # Threats
            if threats:
                story.append(PageBreak())
                story.append(Paragraph("Detected Threats", heading_style))
                threat_data = [['ID', 'Severity', 'Category', 'Description']]
                for t in threats[:20]:
                    threat_data.append([
                        t.get('event_id', '')[:12],
                        t.get('severity', 'INFO'),
                        t.get('category', 'unknown'),
                        t.get('description', '')[:40] + '...'
                    ])
                
                threat_table = PDFTable(threat_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 3*inch])
                threat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ]))
                story.append(threat_table)
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph("â”€" * 80, footer_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"Â© 2024 {PLATFORM} | All Rights Reserved", footer_style))
            story.append(Paragraph(f"Generated by SOC Automated Lab {VERSION}", footer_style))
            story.append(Paragraph("This report is for EDUCATIONAL & AUTHORIZED SECURITY TESTING purposes only.", footer_style))
            
            # Build PDF with watermark
            doc.build(story, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)
            return filepath
            
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return self._generate_txt_report(filepath.replace('.pdf', '.txt'), report_id, stats, threats, lab_state, timestamp, process_stats, processes)
    
    def _generate_html_report(self, filepath: str, report_id: str, stats: Dict, threats: List, lab_state: str, timestamp: datetime, process_stats: Dict, processes: List) -> str:
        """Generate HTML report with watermark"""
        try:
            # Process table rows
            process_rows = ''
            for p in processes[:20]:
                duration = f"{int(p.duration // 60)}m {int(p.duration % 60)}s"
                threat_count = len(p.threats)
                threat_color = 'red' if threat_count > 0 else 'green'
                process_rows += f'<tr><td>{p.pid}</td><td>{p.name[:30]}</td><td>{duration}</td><td>{p.cpu_percent:.1f}%</td><td>{p.memory_mb:.1f}</td><td style="color:{threat_color}">{threat_count}</td></tr>'
            
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SOC Lab Report - {report_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 3px solid #0066cc; padding-bottom: 20px; margin-bottom: 30px; }}
        .watermark {{ position: fixed; bottom: 20px; right: 20px; color: #cccccc; font-size: 12px; transform: rotate(-15deg); opacity: 0.5; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #0066cc; }}
        .summary-card .value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #0066cc; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .severity-CRITICAL {{ color: #dc3545; font-weight: bold; }}
        .severity-HIGH {{ color: #fd7e14; font-weight: bold; }}
        .severity-MEDIUM {{ color: #ffc107; font-weight: bold; }}
        .severity-LOW {{ color: #28a745; font-weight: bold; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="watermark">{WATERMARK_TEXT}</div>
        <div class="header">
            <h1>ðŸ›¡ï¸ SOC Automated Lab Report</h1>
            <p><strong>Report ID:</strong> {report_id}</p>
            <p><strong>Generated:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>System:</strong> {platform.node()}</p>
        </div>
        
        <h2>Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card"><h3>Lab State</h3><div class="value">{lab_state}</div></div>
            <div class="summary-card"><h3>Total Alerts</h3><div class="value">{stats.get('total_alerts', 0)}</div></div>
            <div class="summary-card"><h3>Active Threats</h3><div class="value">{stats.get('active_threats', 0)}</div></div>
            <div class="summary-card"><h3>Files Scanned</h3><div class="value">{stats.get('files_scanned', 0)}</div></div>
            <div class="summary-card"><h3>Processes</h3><div class="value">{process_stats.get('total_processes', 0)}</div></div>
            <div class="summary-card"><h3>Threatened Processes</h3><div class="value">{process_stats.get('processes_with_threats', 0)}</div></div>
        </div>
        
        <h2>Process Monitoring</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Processes</td><td>{process_stats.get('total_processes', 0)}</td></tr>
            <tr><td>System Processes</td><td>{process_stats.get('system_processes', 0)}</td></tr>
            <tr><td>User Processes</td><td>{process_stats.get('user_processes', 0)}</td></tr>
            <tr><td>Processes with Threats</td><td>{process_stats.get('processes_with_threats', 0)}</td></tr>
        </table>
        
        <h2>Running Processes</h2>
        <table>
            <tr><th>PID</th><th>Name</th><th>Duration</th><th>CPU%</th><th>Memory(MB)</th><th>Threats</th></tr>
            {process_rows}
        </table>
        {f'<p><em>... and {len(processes) - 20} more processes</em></p>' if len(processes) > 20 else ''}
        
        <h2>Detected Threats ({len(threats)})</h2>
        <table>
            <tr><th>ID</th><th>Severity</th><th>Category</th><th>Description</th></tr>
            {''.join(f'<tr><td>{t.get("event_id", "")[:12]}</td><td class="severity-{t.get("severity", "INFO")}">{t.get("severity", "INFO")}</td><td>{t.get("category", "unknown")}</td><td>{t.get("description", "")}</td></tr>' for t in threats[:20])}
        </table>
        {f'<p><em>... and {len(threats) - 20} more threats</em></p>' if len(threats) > 20 else ''}
        
        <div class="footer">
            <p>Â© 2024 {PLATFORM} | All Rights Reserved</p>
            <p>Generated by SOC Automated Lab {VERSION}</p>
            <p>This report is for EDUCATIONAL & AUTHORIZED SECURITY TESTING purposes only.</p>
        </div>
    </div>
</body>
</html>'''
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return filepath
            
        except Exception as e:
            self.logger.error(f"HTML generation failed: {e}")
            return self._generate_txt_report(filepath.replace('.html', '.txt'), report_id, stats, threats, lab_state, timestamp, process_stats, processes)
    
    def _generate_json_report(self, filepath: str, report_id: str, stats: Dict, threats: List, lab_state: str, timestamp: datetime, process_stats: Dict, processes: List) -> str:
        """Generate JSON report"""
        try:
            data = {
                'report_id': report_id,
                'timestamp': timestamp.isoformat(),
                'lab_state': lab_state,
                'statistics': stats,
                'process_statistics': process_stats,
                'processes': [
                    {
                        'pid': p.pid,
                        'name': p.name,
                        'duration_seconds': p.duration,
                        'cpu_percent': p.cpu_percent,
                        'memory_mb': p.memory_mb,
                        'status': p.status,
                        'threats_count': len(p.threats),
                        'is_system': p.is_system_process
                    }
                    for p in processes[:50]
                ],
                'threats': threats[:50],
                'watermark': WATERMARK_TEXT,
                'platform': PLATFORM,
                'version': VERSION
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return filepath
            
        except Exception as e:
            self.logger.error(f"JSON generation failed: {e}")
            return None
    
    def _generate_txt_report(self, filepath: str, report_id: str, stats: Dict, threats: List, lab_state: str, timestamp: datetime, process_stats: Dict, processes: List) -> str:
        """Generate TXT report with watermark"""
        try:
            with open(filepath, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("SOC AUTOMATED LAB REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Report ID: {report_id}\n")
                f.write(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"System: {platform.node()}\n")
                f.write(f"Lab State: {lab_state}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("PROCESS MONITORING\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Processes: {process_stats.get('total_processes', 0)}\n")
                f.write(f"System Processes: {process_stats.get('system_processes', 0)}\n")
                f.write(f"User Processes: {process_stats.get('user_processes', 0)}\n")
                f.write(f"Processes with Threats: {process_stats.get('processes_with_threats', 0)}\n\n")
                
                f.write("Running Processes:\n")
                for p in processes[:20]:
                    duration = f"{int(p.duration // 60)}m {int(p.duration % 60)}s"
                    threat_status = "âš ï¸" if p.threats else "âœ…"
                    f.write(f"  [{threat_status}] PID: {p.pid} | {p.name[:30]} | {duration} | CPU: {p.cpu_percent:.1f}% | Mem: {p.memory_mb:.1f}MB\n")
                if len(processes) > 20:
                    f.write(f"  ... and {len(processes) - 20} more processes\n")
                
                f.write("\n" + "-" * 80 + "\n")
                f.write("STATISTICS\n")
                f.write("-" * 80 + "\n")
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")
                
                f.write("\n" + "-" * 80 + "\n")
                f.write("DETECTED THREATS\n")
                f.write("-" * 80 + "\n")
                for t in threats[:20]:
                    f.write(f"[{t.get('severity', 'INFO')}] {t.get('description', '')}\n")
                    f.write(f"  ID: {t.get('event_id', '')}\n")
                    f.write(f"  Category: {t.get('category', 'unknown')}\n")
                    f.write(f"  Status: {t.get('status', '')}\n\n")
                if len(threats) > 20:
                    f.write(f"... and {len(threats) - 20} more threats\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"{WATERMARK_TEXT}\n")
                f.write("=" * 80 + "\n")
                f.write("Â© 2024 DSTERMINAL | All Rights Reserved\n")
                f.write("This report is for EDUCATIONAL & AUTHORIZED SECURITY TESTING purposes only.\n")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"TXT generation failed: {e}")
            return None
    
    def get_reports(self) -> List[LabReport]:
        """Get all generated reports"""
        return self.reports


# ============================================================
# SOC AUTOMATED LAB DASHBOARD
# ============================================================

class SOCLabDashboard:
    def __init__(self, lab: 'SOCAutomatedLab'):
        self.lab = lab
        self.running = False
        self.console = Console() if RICH_AVAILABLE else None
        self.typer = TypeWriter('fast')
        self.notification = ""
        self.notification_time = 0
        self._start_time = datetime.now()
        
        # Check if Rich is actually working
        self.use_rich = RICH_AVAILABLE and self.console is not None
        
        # Colors for the dashboard
        self.colors = {
            'primary': 'bright_green',
            'secondary': 'green',
            'accent': 'bright_red',
            'warning': 'yellow',
            'danger': 'red',
            'info': 'cyan',
            'dim': 'dim',
            'success': 'green',
            'magenta': 'magenta',
        }
        self.fallback_colors = {
            'primary': Colors.GREEN,
            'secondary': Colors.GREEN,
            'accent': Colors.RED,
            'warning': Colors.YELLOW,
            'danger': Colors.RED,
            'info': Colors.CYAN,
            'dim': Colors.DIM,
            'success': Colors.GREEN,
            'magenta': Colors.MAGENTA,
        }
    
    def _get_color(self, color_name: str) -> str:
        if self.use_rich:
            return self.colors.get(color_name, 'white')
        else:
            return self.fallback_colors.get(color_name, Colors.WHITE)
    
    def _get_terminal_width(self) -> int:
        """Get terminal width for centered output"""
        try:
            import shutil
            width = shutil.get_terminal_size().columns
            return min(max(width, 80), 120)
        except:
            return 80
    
    def start_dashboard(self):
        self.running = True
        self._clear_screen()
        self._show_centered_banner()
        
        if RICH_AVAILABLE and self.console:
            self._run_rich_dashboard()
        else:
            self._run_simple_dashboard()
    
    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _get_centered_banner(self) -> Panel:
        banner_text = f"""
    [bold green]â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—      â–ˆâ–ˆâ•—     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— [/bold green]
    [bold green]â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•      â–ˆâ–ˆâ•‘    â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—[/bold green]
    [bold green]â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘           â–ˆâ–ˆâ•‘    â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•[/bold green]
    [bold green]â•šâ•â•â•â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘           â–ˆâ–ˆâ•‘    â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—[/bold green]
    [bold green]â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â•šâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—      â–ˆâ–ˆâ•‘    â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•[/bold green]
    [bold green]â•šâ•â•â•â•â•â•â• â•šâ•â•â•â•â•â•  â•šâ•â•â•â•â•â•      â•šâ•â•    â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â• [/bold green]

    [bold cyan]       SOC AUTOMATED LAB {VERSION}[/bold cyan]
    [dim]â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•[/dim]
    [bold yellow]ðŸ›¡ï¸[/bold yellow] Security Operations Center - 24/7 Monitoring
    [bold yellow]ðŸ›¡ï¸[/bold yellow] 24/7 Cyber risks rapid detection and observation
    [bold yellow]ðŸ“Š[/bold yellow] Process & Application Monitoring
    [bold yellow]ðŸ“„[/bold yellow] Threat Hunting & Automated Reporting 
    [bold red]âš¡[/bold red] For Educational & Authorized Security Testing Purposes
    """
        return Panel(
            banner_text,
            title="[bold cyan]SOC AUTOMATED LAB[/bold cyan]",
            border_style="cyan",
            box=box.HEAVY,
            padding=(1, 2),
            width=80
        )
    
    def _show_centered_banner(self):
        if self.console:
            self.console.print(Align.center(self._get_centered_banner()))
            
            status = "â•" * 78
            self.console.print(f"\n[dim]{status}[/dim]")
            self.console.print(
                Align.center(
                    f"[green]â–º[/green] [dim]System:[/dim] [cyan]ACTIVE[/cyan] "
                    f"[green]â”‚[/green] [dim]Mode:[/dim] [yellow]LAB MODE[/yellow] "
                    f"[green]â”‚[/green] [dim]Version:[/dim] [cyan]{VERSION}[/cyan]"
                )
            )
            self.console.print(f"[dim]{status}[/dim]\n")
    
    def _get_left_panel_content(self) -> str:
        status = self.lab.get_status()
        reports = self.lab.get_reports()
        process_stats = self.lab.get_process_stats()
        
        content = f"""
[{self.colors['info']}]â”Œâ”€ SESSION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]
[{self.colors['primary']}]â”‚[/{self.colors['primary']}] [dim]Time:[/dim] {datetime.now().strftime('%H:%M:%S')}
[{self.colors['primary']}]â”‚[/{self.colors['primary']}] [dim]Date:[/dim] {datetime.now().strftime('%Y-%m-%d')}
[{self.colors['primary']}]â”‚[/{self.colors['primary']}] [dim]Status:[/dim] {'ðŸŸ¢ RUNNING' if status.get('running') else 'ðŸ”´ STOPPED'}
[{self.colors['primary']}]â”‚[/{self.colors['primary']}] [dim]Uptime:[/dim] {status.get('uptime_display', 'N/A')}
[{self.colors['info']}]â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]

[{self.colors['accent']}]â”Œâ”€ STATS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['accent']}]
[{self.colors['accent']}]â”‚[/{self.colors['accent']}] [dim]Alerts:[/dim] {status.get('total_alerts', 0)}
[{self.colors['accent']}]â”‚[/{self.colors['accent']}] [dim]Threats:[/dim] {status.get('active_threats', 0)}
[{self.colors['accent']}]â”‚[/{self.colors['accent']}] [dim]Scanned:[/dim] {status.get('files_scanned', 0)}
[{self.colors['accent']}]â”‚[/{self.colors['accent']}] [dim]Paths:[/dim] {status.get('monitored_paths', 0)}
[{self.colors['accent']}]â”‚[/{self.colors['accent']}] [dim]Processes:[/dim] {process_stats.get('total_processes', 0)}
[{self.colors['accent']}]â”‚[/{self.colors['accent']}] [dim]Threatened:[/dim] {process_stats.get('processes_with_threats', 0)}
[{self.colors['accent']}]â”‚[/{self.colors['accent']}] [dim]Reports:[/dim] {len(reports)}
[{self.colors['accent']}]â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['accent']}]
"""
        return content
    
    def _get_center_panel_content(self) -> str:
        content = f"""
[{self.colors['primary']}]â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]               [{self.colors['info']}]ðŸ“‹ MAIN MENU[/{self.colors['info']}]                 [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]1.[/{self.colors['accent']}] [{self.colors['primary']}]ðŸš€[/{self.colors['primary']}] Start Lab Monitoring     [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]2.[/{self.colors['accent']}] [{self.colors['danger']}]ðŸ›‘[/{self.colors['danger']}] Stop Lab Monitoring      [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]3.[/{self.colors['accent']}] [{self.colors['info']}]ðŸ“Š[/{self.colors['info']}] Show Status             [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]4.[/{self.colors['accent']}] [{self.colors['warning']}]ðŸ”[/{self.colors['warning']}] Run Threat Scan         [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]5.[/{self.colors['accent']}] [{self.colors['magenta']}]ðŸ“„[/{self.colors['magenta']}] Generate Report         [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]6.[/{self.colors['accent']}] [{self.colors['danger']}]ðŸš¨[/{self.colors['danger']}] List Threats            [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]7.[/{self.colors['accent']}] [{self.colors['success']}]ðŸ“Š[/{self.colors['success']}] Show Results            [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]8.[/{self.colors['accent']}] [{self.colors['warning']}]ðŸ“¤[/{self.colors['warning']}] Export Data             [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]p.[/{self.colors['accent']}] [{self.colors['info']}]ðŸ”„[/{self.colors['info']}] View Running Processes  [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]e.[/{self.colors['accent']}] [{self.colors['info']}]ðŸ”§[/{self.colors['info']}] Enhanced Modules       [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]h.[/{self.colors['accent']}] [{self.colors['info']}]â“[/{self.colors['info']}] Help                     [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•‘[/{self.colors['primary']}]  [{self.colors['accent']}]q.[/{self.colors['accent']}] [{self.colors['danger']}]ðŸšª[/{self.colors['danger']}] Exit                     [{self.colors['primary']}]â•‘[/{self.colors['primary']}]
[{self.colors['primary']}]â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•[/{self.colors['primary']}]
"""
        return content
    
    def _get_right_panel_content(self) -> str:
        threats = self.lab.get_threats()
        reports = self.lab.get_reports()
        process_stats = self.lab.get_process_stats()
        processes = self.lab.get_processes()
        
        content = f"""
[{self.colors['info']}]â”Œâ”€ RECENT THREATS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]
"""
        if threats:
            for t in threats[:3]:
                severity = t.get('severity', 'INFO')
                color = Colors.RED if severity == 'CRITICAL' else Colors.YELLOW
                content += f"[{self.colors['info']}]â”‚[/{self.colors['info']}] [{color}]â—[/{color}] {t.get('description', '')[:25]}...\n"
        else:
            content += f"[{self.colors['info']}]â”‚[/{self.colors['info']}] [dim]No threats detected[/dim]\n"
        
        content += f"""
[{self.colors['info']}]â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]

[{self.colors['primary']}]â”Œâ”€ PROCESSES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['primary']}]
[{self.colors['primary']}]â”‚[/{self.colors['primary']}] [dim]Running:[/dim] {process_stats.get('total_processes', 0)}
"""
        if processes:
            top_cpu = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:3]
            for p in top_cpu:
                threat_icon = "âš ï¸" if p.threats else "âœ…"
                content += f"[{self.colors['primary']}]â”‚[/{self.colors['primary']}] {threat_icon} {p.name[:20]} ({p.cpu_percent:.1f}%)\n"
        
        content += f"""
[{self.colors['primary']}]â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['primary']}]

[{self.colors['info']}]â”Œâ”€ REPORTS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]
[{self.colors['info']}]â”‚[/{self.colors['info']}] [dim]Total:[/dim] {len(reports)}
"""
        if reports:
            latest = reports[-1]
            content += f"[{self.colors['info']}]â”‚[/{self.colors['info']}] [dim]Latest:[/dim] {latest.format.upper()}\n"
            content += f"[{self.colors['info']}]â”‚[/{self.colors['info']}] [dim]Size:[/dim] {latest.size // 1024} KB\n"
        
        content += f"""
[{self.colors['info']}]â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]

[{self.colors['info']}]â”Œâ”€ NOTIFICATION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]
[{self.colors['info']}]â”‚[/{self.colors['info']}] [dim]{self.notification if self.notification else 'Ready'}[/dim]
[{self.colors['info']}]â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€[/{self.colors['info']}]
"""
        return content
    
    def _run_rich_dashboard(self):
        """Run the integrated dashboard with proper layout"""
        while self.running:
            self._clear_screen()
            self._show_centered_banner()
            
            left_panel = Panel(
                self._get_left_panel_content(),
                title="[bold green]â–‘ SYSTEM INFO â–‘[/bold green]",
                border_style="green",
                box=box.HEAVY,
                width=35
            )
            
            center_panel = Panel(
                self._get_center_panel_content(),
                title="[bold cyan]â–‘ MAIN MENU â–‘[/bold cyan]",
                border_style="cyan",
                box=box.HEAVY,
                width=45
            )
            
            right_panel = Panel(
                self._get_right_panel_content(),
                title="[bold yellow]â–‘ STATUS â–‘[/bold yellow]",
                border_style="yellow",
                box=box.HEAVY,
                width=35
            )
            
            layout = Layout()
            layout.split_row(
                Layout(Padding(left_panel, (0, 0)), ratio=1),
                Layout(Padding(center_panel, (0, 2)), ratio=2),
                Layout(Padding(right_panel, (0, 0)), ratio=1)
            )
            
            self.console.print(layout)
            
            status = "â•" * 80
            self.console.print(f"\n[dim]{status}[/dim]")
            self.console.print(
                Align.center(
                    f"[green]â–¶[/green] [dim]Select option:[/dim] [yellow]1-8[/yellow] [dim]|[/dim] "
                    f"[yellow]p[/yellow] [dim]Processes[/dim] [dim]|[/dim] "
                    f"[yellow]e[/yellow] [dim]Enhanced[/dim] [dim]|[/dim] "
                    f"[yellow]h[/yellow] [dim]Help[/dim] [dim]|[/dim] [yellow]q[/yellow] [dim]Quit[/dim]"
                )
            )
            self.console.print(f"[dim]{status}[/dim]")
            
            # Show notification if any
            if self.notification and (time.time() - self.notification_time < 5):
                self.console.print(f"\n[bold yellow]ðŸ“Œ {self.notification}[/bold yellow]")
            
            choice = Prompt.ask(
                "\n[bold cyan]â”Œâ”€ Select Option â”€â”€â–º[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "p", "e", "h", "q"],
                default="h"
            )
            
            if choice == "q":
                self._exit_dashboard()
                break
            elif choice == "h":
                self._show_help()
            elif choice == "1":
                self._cmd_start()
            elif choice == "2":
                self._cmd_stop()
            elif choice == "3":
                self._cmd_status()
            elif choice == "4":
                self._cmd_scan()
            elif choice == "5":
                self._cmd_report()
            elif choice == "6":
                self._cmd_threats()
            elif choice == "7":
                self._cmd_results()
            elif choice == "8":
                self._cmd_export()
            elif choice == "p":
                self._cmd_processes()
            elif choice == "e":
                self._cmd_enhanced()
                
    def _cmd_enhanced(self):
        """Show enhanced modules status - Interactive Rich Dashboard"""
        self._clear_screen()
        self._show_centered_banner()
        
        if not self.use_rich or not self.console:
            # Fallback to simple text if Rich not available
            self._cmd_enhanced_simple()
            return
        
        from rich.layout import Layout
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        from rich.align import Align
        
        status = self.lab.get_enhanced_status()
        
        # Create main layout
        layout = Layout()
        layout.split(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )
        
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        layout["left"].split(
            Layout(name="mitre_panel", size=10),
            Layout(name="alerts_panel")
        )
        
        layout["right"].split(
            Layout(name="intel_panel", size=10),
            Layout(name="actions_panel")
        )
        
        # Header
        header_text = Text()
        header_text.append("ðŸ”§ ENHANCED MODULES ", style="bold cyan")
        header_text.append("| ", style="white")
        header_text.append(f"Status: {'ðŸŸ¢ ACTIVE' if status.get('running') else 'ðŸ”´ INACTIVE'}", style="green" if status.get('running') else "red")
        header_text.append(" | ", style="white")
        header_text.append(f"Updated: {datetime.now().strftime('%H:%M:%S')}", style="dim")
        layout["header"].update(Panel(header_text, border_style="cyan"))
        
        # MITRE Panel
        mitre_table = Table(show_header=False, box=box.ROUNDED)
        mitre_table.add_column("Item", style="cyan")
        mitre_table.add_column("Value", style="white")
        
        mitre = status.get('mitre', {})
        mitre_table.add_row("ðŸŽ¯ Techniques", str(mitre.get('techniques', 0)))
        mitre_table.add_row("ðŸ“‹ Tactics", str(mitre.get('tactics', 0)))
        
        # Show top techniques
        mitre_techniques = self.lab.enhanced.mitre.techniques
        if mitre_techniques:
            mitre_table.add_row("ðŸ“ Techniques", "")
            for tech_id, tech in list(mitre_techniques.items())[:3]:
                mitre_table.add_row(f"  â€¢ {tech_id}", tech.get('name', '')[:30])
            if len(mitre_techniques) > 3:
                mitre_table.add_row(f"  ... and {len(mitre_techniques) - 3} more", "")
        
        layout["mitre_panel"].update(Panel(mitre_table, title="ðŸŽ¯ MITRE ATT&CK", border_style="blue"))
        
        # Alerts Panel
        alert_status = status.get('alert_dashboard', {})
        alerts_table = Table(show_header=False, box=box.ROUNDED)
        alerts_table.add_column("Metric", style="cyan")
        alerts_table.add_column("Value", style="white")
        
        alerts_table.add_row("ðŸ“Š Total", str(alert_status.get('alerts', 0)))
        alerts_table.add_row("ðŸ”´ Critical", str(alert_status.get('critical', 0)))
        alerts_table.add_row("ðŸŸ¡ High", str(alert_status.get('high', 0)))
        alerts_table.add_row("ðŸ”µ Medium", str(alert_status.get('medium', 0)))
        
        layout["alerts_panel"].update(Panel(alerts_table, title="ðŸš¨ ALERT DASHBOARD", border_style="red" if alert_status.get('critical', 0) > 0 else "yellow"))
        
        # Threat Intelligence Panel
        intel_table = Table(show_header=False, box=box.ROUNDED)
        intel_table.add_column("IOC Type", style="cyan")
        intel_table.add_column("Malicious", style="red")
        intel_table.add_column("Suspicious", style="yellow")
        
        ioc_stats = status.get('threat_intel', {}).get('iocs', {})
        total_iocs = 0
        
        for ioc_type, categories in ioc_stats.items():
            if isinstance(categories, dict):
                malicious = categories.get('malicious', 0)
                suspicious = categories.get('suspicious', 0)
                if malicious > 0 or suspicious > 0:
                    intel_table.add_row(ioc_type, str(malicious), str(suspicious))
                    total_iocs += malicious + suspicious
        
        if total_iocs == 0:
            intel_table.add_row("ðŸ“­", "No IOCs loaded", "")
        
        layout["intel_panel"].update(Panel(intel_table, title="ðŸ” THREAT INTELLIGENCE", border_style="magenta"))
        
        # Actions Panel - Interactive buttons
        actions = Table(show_header=False, box=box.MINIMAL)
        actions.add_column("Option", style="bold cyan")
        actions.add_column("Description", style="white")
        
        actions.add_row(" [1] Add IOC", "Add indicator of compromise")
        actions.add_row(" [2] Generate Report", "Create enhanced security report")
        actions.add_row(" [3] View Alerts", "Show alert dashboard")
        actions.add_row(" [4] Export IOCs", "Export threat intelligence")
        actions.add_row(" [5] Refresh", "Update status")
        actions.add_row(" [b] Back", "Return to main menu")
        
        layout["actions_panel"].update(Panel(actions, title="ðŸŽ® AVAILABLE ACTIONS", border_style="green"))
        
        # Footer
        footer_text = Text()
        footer_text.append("Select an option: ", style="bold yellow")
        footer_text.append("1-5 | b=back", style="dim")
        
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        self.console.print(layout)
        
        # Get user input
        choice = input("\nâš¡ Enter your choice: ").strip().lower()
        
        if choice == "1":
            self._cmd_ioc_add()
        elif choice == "2":
            self._cmd_enhanced_report()
        elif choice == "3":
            self._cmd_view_alerts()
        elif choice == "4":
            self._cmd_export_iocs()
        elif choice == "5":
            self._cmd_enhanced()  # Refresh
        elif choice == "b" or choice == "back":
            return
        else:
            self._set_notification("âŒ Invalid option", "red")
            time.sleep(1)
            self._cmd_enhanced()

    def _cmd_enhanced_simple(self):
        """Simple text version of enhanced dashboard"""
        status = self.lab.get_enhanced_status()
        
        print("\n" + "â•" * 80)
        print("ðŸ”§ ENHANCED MODULES STATUS".center(80))
        print("â•" * 80)
        print(f"Running: {'âœ…' if status.get('running') else 'âŒ'}")
        print(f"MITRE Techniques: {status.get('mitre', {}).get('techniques', 0)}")
        print(f"MITRE Tactics: {status.get('mitre', {}).get('tactics', 0)}")
        
        alert_status = status.get('alert_dashboard', {})
        print(f"\nAlert Dashboard:")
        print(f"  Status: {'ðŸŸ¢ Active' if alert_status.get('running') else 'ðŸ”´ Inactive'}")
        print(f"  Total Alerts: {alert_status.get('alerts', 0)}")
        print(f"  Critical: {alert_status.get('critical', 0)}")
        print(f"  High: {alert_status.get('high', 0)}")
        print(f"  Medium: {alert_status.get('medium', 0)}")
        
        ioc_stats = status.get('threat_intel', {}).get('iocs', {})
        print(f"\nThreat Intelligence:")
        total_iocs = 0
        for ioc_type, categories in ioc_stats.items():
            if isinstance(categories, dict):
                malicious = categories.get('malicious', 0)
                suspicious = categories.get('suspicious', 0)
                if malicious > 0 or suspicious > 0:
                    print(f"  {ioc_type}: Malicious: {malicious}, Suspicious: {suspicious}")
                    total_iocs += malicious + suspicious
        if total_iocs == 0:
            print("  No IOCs loaded")
        
        print("\n" + "â•" * 80)
        print("Options:")
        print("  [1] Add IOC")
        print("  [2] Generate Enhanced Report")
        print("  [3] View Alerts")
        print("  [4] Export IOCs")
        print("  [5] Refresh")
        print("  [b] Back")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == "1":
            self._cmd_ioc_add()
        elif choice == "2":
            self._cmd_enhanced_report()
        elif choice == "3":
            self._cmd_view_alerts()
        elif choice == "4":
            self._cmd_export_iocs()
        elif choice == "5":
            self._cmd_enhanced()
        elif choice == "b" or choice == "back":
            return
        else:
            self._set_notification("âŒ Invalid option", "red")
            time.sleep(1)
            self._cmd_enhanced()

    def _cmd_export_iocs(self):
        """Export IOCs to file"""
        self._clear_screen()
        self._show_centered_banner()
        
        print("\nðŸ“¤ EXPORT IOCs")
        print("â•" * 80)
        
        iocs = self.lab.enhanced.threat_intel.get_all_iocs()
        
        if not any(iocs.values()):
            print("âŒ No IOCs to export")
            input("\nPress Enter to continue...")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"iocs_{timestamp}.json"
        filepath = os.path.expanduser(f"~/soc_lab_workspace/reports/{filename}")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(iocs, f, indent=2)
        
        print(f"âœ… IOCs exported to: {filepath}")
        
        # Show summary
        print("\nðŸ“Š IOC Summary:")
        for ioc_type, categories in iocs.items():
            if categories:
                malicious = len(categories.get('malicious', []))
                suspicious = len(categories.get('suspicious', []))
                print(f"  {ioc_type}: Malicious: {malicious}, Suspicious: {suspicious}")
        
        input("\nPress Enter to continue...")

    def _cmd_view_alerts(self):
        """View the alert dashboard - Interactive Rich display"""
        self._clear_screen()
        self._show_centered_banner()
        
        if not self.use_rich or not self.console:
            self._cmd_view_alerts_simple()
            return
        
        from rich.layout import Layout
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        from rich.align import Align
        
        # Get alerts
        alerts = self.lab.enhanced.alert_dashboard.get_alerts(limit=50)
        stats = self.lab.enhanced.alert_dashboard.get_stats()
        
        # Create layout
        layout = Layout()
        layout.split(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )
        
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        layout["left"].split(
            Layout(name="stats_panel", size=8),
            Layout(name="alerts_panel")
        )
        
        layout["right"].split(
            Layout(name="filter_panel", size=8),
            Layout(name="actions_panel")
        )
        
        # Header
        header_text = Text()
        header_text.append("ðŸš¨ ALERT DASHBOARD ", style="bold red")
        header_text.append("| ", style="white")
        header_text.append(f"Total: {stats['total']}", style="cyan")
        header_text.append(" | ", style="white")
        header_text.append(f"Updated: {datetime.now().strftime('%H:%M:%S')}", style="dim")
        layout["header"].update(Panel(header_text, border_style="red"))
        
        # Stats Panel
        stats_table = Table(show_header=False, box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("ðŸ“Š Total Alerts", str(stats['total']))
        stats_table.add_row("ðŸ”´ Critical", str(stats['critical']))
        stats_table.add_row("ðŸŸ¡ High", str(stats['high']))
        stats_table.add_row("ðŸ”µ Medium", str(stats['medium']))
        stats_table.add_row("ðŸŸ¢ Low", str(stats['low']))
        
        layout["stats_panel"].update(Panel(stats_table, title="ðŸ“Š STATISTICS", border_style="blue"))
        
        # Alerts Panel
        alerts_table = Table(show_header=True, box=box.MINIMAL)
        alerts_table.add_column("Time", style="dim", width=12)
        alerts_table.add_column("Severity", width=10)
        alerts_table.add_column("Category", width=12)
        alerts_table.add_column("Description", max_width=35)
        
        if alerts:
            for alert in alerts[-15:]:
                severity = alert.get('severity', 'INFO')
                color = self._get_severity_color(severity)
                alerts_table.add_row(
                    alert.get('timestamp', '')[:19],
                    f"[{color}]{severity}[/{color}]",
                    alert.get('category', 'unknown')[:10],
                    alert.get('description', '')[:35]
                )
        else:
            alerts_table.add_row("âœ…", "No alerts", "", "System is clean")
        
        layout["alerts_panel"].update(Panel(alerts_table, title="ðŸ“‹ RECENT ALERTS", border_style="green"))
        
        # Filter Panel
        filter_text = Text()
        filter_text.append("Current Filters:\n", style="bold cyan")
        filters = self.lab.enhanced.alert_dashboard.filters
        filter_text.append(f"  Severity: {filters.get('severity') or 'ALL'}\n", style="white")
        filter_text.append(f"  Category: {filters.get('category') or 'ALL'}\n", style="white")
        filter_text.append(f"  Status: {filters.get('status') or 'ALL'}\n", style="white")
        filter_text.append("\nCommands: [s]et filter | [r]eset", style="dim")
        
        layout["filter_panel"].update(Panel(filter_text, title="ðŸ” FILTERS", border_style="magenta"))
        
        # Actions Panel
        actions = Table(show_header=False, box=box.MINIMAL)
        actions.add_column("Option", style="bold cyan")
        actions.add_column("Description", style="white")
        
        actions.add_row(" [1] Export JSON", "Export alerts as JSON")
        actions.add_row(" [2] Export CSV", "Export alerts as CSV")
        actions.add_row(" [3] Clear All", "Clear all alerts")
        actions.add_row(" [4] Set Filter", "Filter alerts")
        actions.add_row(" [b] Back", "Return to enhanced menu")
        
        layout["actions_panel"].update(Panel(actions, title="ðŸŽ® ACTIONS", border_style="yellow"))
        
        # Footer
        footer_text = Text()
        footer_text.append("Select option: ", style="bold yellow")
        footer_text.append("1-4 | s=filter | r=reset | b=back", style="dim")
        
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        self.console.print(layout)
        
        # Get user input
        choice = input("\nâš¡ Enter your choice: ").strip().lower()
        
        if choice == "1":
            filepath = self.lab.enhanced.alert_dashboard.export_alerts('json')
            print(f"âœ… Alerts exported to: {filepath}")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "2":
            filepath = self.lab.enhanced.alert_dashboard.export_alerts('csv')
            print(f"âœ… Alerts exported to: {filepath}")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "3":
            self.lab.enhanced.alert_dashboard.clear_alerts()
            print("âœ… Alerts cleared")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "4" or choice == "s":
            self._cmd_set_filter()
            self._cmd_view_alerts()
        elif choice == "r":
            self.lab.enhanced.alert_dashboard.reset_filters()
            print("âœ… Filters reset")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "b" or choice == "back":
            return
        else:
            self._cmd_view_alerts()

    def _cmd_view_alerts_simple(self):
        """Simple text version of alert view"""
        alerts = self.lab.enhanced.alert_dashboard.get_alerts(limit=50)
        stats = self.lab.enhanced.alert_dashboard.get_stats()
        
        print("\n" + "â•" * 80)
        print("ðŸš¨ ALERT DASHBOARD".center(80))
        print("â•" * 80)
        
        print(f"Total Alerts: {stats['total']}  |  Critical: {stats['critical']}  |  High: {stats['high']}  |  Medium: {stats['medium']}  |  Low: {stats['low']}")
        print("â”€" * 80)
        
        if not alerts:
            print("\nâœ… No alerts detected".center(80))
        else:
            print(f"{'Time':<20} {'Severity':<10} {'Category':<12} {'Description':<45}")
            print("â”€" * 80)
            
            for alert in alerts[-20:]:
                timestamp = alert.get('timestamp', '')[:19]
                severity = alert.get('severity', 'INFO')
                category = alert.get('category', 'unknown')[:12]
                description = alert.get('description', '')[:45]
                
                # Color severity for terminal
                if severity == 'CRITICAL':
                    severity = f"\033[91m{severity}\033[0m"
                elif severity == 'HIGH':
                    severity = f"\033[93m{severity}\033[0m"
                elif severity == 'MEDIUM':
                    severity = f"\033[94m{severity}\033[0m"
                elif severity == 'LOW':
                    severity = f"\033[92m{severity}\033[0m"
                
                print(f"{timestamp:<20} {severity:<10} {category:<12} {description:<45}")
        
        print("\n" + "â•" * 80)
        print("Options:")
        print("  [1] Export Alerts (JSON)")
        print("  [2] Export Alerts (CSV)")
        print("  [3] Clear Alerts")
        print("  [4] Set Filter")
        print("  [r] Reset Filters")
        print("  [b] Back")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == "1":
            filepath = self.lab.enhanced.alert_dashboard.export_alerts('json')
            print(f"âœ… Alerts exported to: {filepath}")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "2":
            filepath = self.lab.enhanced.alert_dashboard.export_alerts('csv')
            print(f"âœ… Alerts exported to: {filepath}")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "3":
            self.lab.enhanced.alert_dashboard.clear_alerts()
            print("âœ… Alerts cleared")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "4":
            self._cmd_set_filter()
            self._cmd_view_alerts()
        elif choice == "r":
            self.lab.enhanced.alert_dashboard.reset_filters()
            print("âœ… Filters reset")
            input("\nPress Enter to continue...")
            self._cmd_view_alerts()
        elif choice == "b" or choice == "back":
            return
        else:
            self._cmd_view_alerts()

    def _cmd_set_filter(self):
        """Set a filter for alerts"""
        print("\nðŸ” SET FILTER")
        print("â•" * 80)
        print("Filter types: severity, category, status")
        
        filter_type = input("Filter type: ").strip().lower()
        if filter_type not in ['severity', 'category', 'status']:
            print("âŒ Invalid filter type")
            return
        
        filter_value = input("Filter value (leave empty to remove): ").strip()
        if filter_value == "":
            filter_value = None
        
        self.lab.enhanced.alert_dashboard.set_filter(filter_type, filter_value)
        print(f"âœ… Filter set: {filter_type} = {filter_value or 'ALL'}")
        
        input("\nPress Enter to continue...")

    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            'CRITICAL': 'red',
            'HIGH': 'yellow',
            'MEDIUM': 'blue',
            'LOW': 'green',
            'INFO': 'cyan'
        }
        return colors.get(severity, 'white')

    def _cmd_ioc_add(self):
        """Add an IOC to threat intelligence - BEAUTIFUL HACKER STYLE"""
        self._clear_screen()
        self._show_centered_banner()
        
        import random
        from colorama import Fore, Back, Style, init
        init(autoreset=True)
        
        # Get terminal width for centering
        try:
            import shutil
            term_width = shutil.get_terminal_size().columns
            width = min(max(term_width, 80), 120)
        except:
            width = 80
        
        # Glowing colors
        glow_colors = [
            '\033[38;5;46m',   # Bright Green
            '\033[38;5;51m',   # Bright Cyan
            '\033[38;5;201m',  # Bright Magenta
            '\033[38;5;226m',  # Bright Yellow
        ]
        glow = random.choice(glow_colors)
        
        # Helper functions for centering
        def center_text(text, color='', width=width):
            """Center text with optional color"""
            if color:
                text = f"{color}{text}{Style.RESET_ALL}"
            import re
            clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
            padding = max(0, (width - len(clean_text) - 2))
            return f"{glow}â•‘{Style.RESET_ALL}{' ' * (padding // 2)}{text}{' ' * (padding - padding // 2)}{glow}â•‘{Style.RESET_ALL}"
        
        def center_border(char='â•'):
            return f"{glow}â•”{char * (width - 2)}â•—{Style.RESET_ALL}"
        
        def center_border_mid(char='â•'):
            return f"{glow}â• {char * (width - 2)}â•£{Style.RESET_ALL}"
        
        def center_border_bottom(char='â•'):
            return f"{glow}â•š{char * (width - 2)}â•{Style.RESET_ALL}"
        
        # ============================================================
        # TOP BORDER WITH GLOW
        # ============================================================
        print(f"\n{center_border()}")
        print(center_text("ðŸ” ADD INDICATOR OF COMPROMISE (IOC)", Fore.CYAN))
        print(center_border_mid())
        
        # ============================================================
        # WHAT ARE IOCS - Centered
        # ============================================================
        print(center_text("ðŸ“š What are IOCs?", Fore.YELLOW))
        print(center_text("ðŸ›¡ï¸ Indicators of Compromise (IOCs): The Complete Guide What Are IOCs?", Fore.YELLOW))
        print(center_text("Indicators of Compromise (IOCs) are forensic artifacts or pieces of evidence that suggest a system or network has been breached or is under attack. They are the ""digital breadcrumbs"" left behind by cyber attackers that security professionals use to detect, investigate, and respond to security incidents.", Fore.WHITE))
        print(center_text(" ðŸ’¡Think of IOCs like fingerprints at a crime scene â€“ they don't tell you who committed the crime, but they prove that someone was there and help you track them down.", Fore.WHITE))
        print(center_text("Indicators of Compromise are forensic artifacts that indicate", Fore.WHITE))
        print(center_text("a potential security breach. They help detect and respond to threats.", Fore.WHITE))
        print(center_border_mid())
        
        # ============================================================
        # IOC TYPES - Colored Box
        # ============================================================
        print(center_text("ðŸ“‹ IOC Types", Fore.MAGENTA))
        
        # Create a colored table for IOC types
        ioc_types = [
            ("1. hash", "File hash (MD5, SHA-1, SHA-256)", "5d41402abc4b2a76b9719d911017c592"),
            ("2. domain", "Malicious domain name", "malware-phishing.com"),
            ("3. ip", "Malicious IP address", "192.168.1.100"),
            ("4. url", "Malicious URL", "http://bad-site.com/payload.exe"),
            ("5. file", "Suspicious file path", "C:\\Windows\\Temp\\malware.exe"),
            ("6. registry", "Suspicious registry key", "HKLM\\Software\\Microsoft\\Windows\\Run"),
        ]
        
        # Print the table header
        print(f"{glow}â•”{'â•' * (width - 2)}â•—{Style.RESET_ALL}")
        
        for i, (type_name, desc, example) in enumerate(ioc_types):
            # Color code the rows
            if i % 2 == 0:
                row_color = Fore.GREEN
            else:
                row_color = Fore.CYAN
            
            # Format the line
            line = f" {row_color}{type_name:<10}{Style.RESET_ALL} {Fore.WHITE}{desc:<30}{Style.RESET_ALL} {Fore.DIM}{example:<40}{Style.RESET_ALL}"
            # Center the line
            import re
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            padding = max(0, (width - len(clean_line) - 2))
            print(f"{glow}â•‘{Style.RESET_ALL}{' ' * (padding // 2)}{line}{' ' * (padding - padding // 2)}{glow}â•‘{Style.RESET_ALL}")
        
        print(f"{glow}â•š{'â•' * (width - 2)}â•{Style.RESET_ALL}")
        
        # ============================================================
        # TIP - Centered
        # ============================================================
        print(center_text("ðŸ’¡ Tip: Most common IOCs are 'hash' and 'domain'", Fore.YELLOW))
        print(center_border_mid())
        
        # ============================================================
        # INPUT SECTION
        # ============================================================
        print(center_text("IOC Type (hash/domain/ip/url/file/registry):", Fore.CYAN))
        print(center_border_bottom())
        
        # Input prompt
        print(f"\n{Fore.CYAN}â”Œâ”€ {Fore.YELLOW}â”Œâ”€[ {Fore.GREEN}IOC {Fore.CYAN}]{Style.RESET_ALL} {Fore.MAGENTA}SELECT TYPE {Fore.CYAN}â”€â–º{Style.RESET_ALL} ", end="")
        ioc_type = input().strip().lower()
        
        valid_types = ['hash', 'domain', 'ip', 'url', 'file', 'registry']
        if ioc_type not in valid_types:
            print(f"\n{Fore.RED}â•”{'â•' * 50}â•—{Style.RESET_ALL}")
            print(f"{Fore.RED}â•‘  âŒ Invalid IOC type. Please choose from: hash, domain, ip, url, file, registry{Style.RESET_ALL}")
            print(f"{Fore.RED}â•š{'â•' * 50}â•{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        # Examples based on type
        examples = {
            'hash': '5d41402abc4b2a76b9719d911017c592',
            'domain': 'malware-phishing.com',
            'ip': '192.168.1.100',
            'url': 'http://bad-site.com/payload.exe',
            'file': 'C:\\Windows\\Temp\\malware.exe',
            'registry': 'HKLM\\Software\\Microsoft\\Windows\\Run\\Evil'
        }
        
        # ============================================================
        # VALUE INPUT
        # ============================================================
        print(f"\n{Fore.CYAN}â”Œâ”€ {Fore.YELLOW}â”Œâ”€[ {Fore.GREEN}IOC {Fore.CYAN}]{Style.RESET_ALL} {Fore.MAGENTA}ENTER VALUE {Fore.CYAN}â”€â–º{Style.RESET_ALL} ", end="")
        value = input().strip()
        
        if not value:
            print(f"\n{Fore.RED}â•”{'â•' * 50}â•—{Style.RESET_ALL}")
            print(f"{Fore.RED}â•‘  âŒ IOC value cannot be empty{Style.RESET_ALL}")
            print(f"{Fore.RED}â•š{'â•' * 50}â•{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        # ============================================================
        # CATEGORY SELECTION
        # ============================================================
        print(f"\n{center_border()}")
        print(center_text("ðŸ“Š IOC Category", Fore.CYAN))
        print(center_border_mid())
        print(center_text(f" {Fore.RED}[1] Malicious{Style.RESET_ALL}     - Confirmed malicious IOC", Fore.WHITE))
        print(center_text(f" {Fore.YELLOW}[2] Suspicious{Style.RESET_ALL}    - Potentially malicious, needs investigation", Fore.WHITE))
        print(center_text(f" {Fore.GREEN}[3] Clean{Style.RESET_ALL}         - False positive or false alarm", Fore.WHITE))
        print(center_border_bottom())
        
        print(f"\n{Fore.CYAN}â”Œâ”€ {Fore.YELLOW}â”Œâ”€[ {Fore.GREEN}IOC {Fore.CYAN}]{Style.RESET_ALL} {Fore.MAGENTA}CATEGORY (1-3) {Fore.CYAN}â”€â–º{Style.RESET_ALL} ", end="")
        category_choice = input().strip()
        category_map = {'1': 'malicious', '2': 'suspicious', '3': 'clean'}
        category = category_map.get(category_choice, 'malicious')
        
        # Category color
        cat_colors = {
            'malicious': Fore.RED,
            'suspicious': Fore.YELLOW,
            'clean': Fore.GREEN
        }
        
        # ============================================================
        # SOURCE SELECTION
        # ============================================================
        print(f"\n{center_border()}")
        print(center_text("ðŸ“Œ Threat Source", Fore.CYAN))
        print(center_border_mid())
        print(center_text(" [1] Internal detection", Fore.WHITE))
        print(center_text(" [2] External threat intelligence", Fore.WHITE))
        print(center_text(" [3] Security vendor report", Fore.WHITE))
        print(center_text(" [4] Open source feed", Fore.WHITE))
        print(center_text(" [5] Other", Fore.WHITE))
        print(center_border_bottom())
        
        print(f"\n{Fore.CYAN}â”Œâ”€ {Fore.YELLOW}â”Œâ”€[ {Fore.GREEN}IOC {Fore.CYAN}]{Style.RESET_ALL} {Fore.MAGENTA}SOURCE (1-5) {Fore.CYAN}â”€â–º{Style.RESET_ALL} ", end="")
        source_choice = input().strip()
        source_map = {
            '1': 'Internal detection',
            '2': 'External threat intelligence',
            '3': 'Security vendor report',
            '4': 'Open source feed',
            '5': 'Other'
        }
        source = source_map.get(source_choice, 'Unknown')
        
        # ============================================================
        # SUMMARY - Beautiful colored box
        # ============================================================
        print(f"\n{center_border()}")
        print(center_text("ðŸ“‹ IOC Summary", Fore.CYAN))
        print(center_border_mid())
        print(center_text(f"Type:     {Fore.CYAN}{ioc_type}{Style.RESET_ALL}", Fore.WHITE))
        print(center_text(f"Value:    {Fore.YELLOW}{value}{Style.RESET_ALL}", Fore.WHITE))
        print(center_text(f"Category: {cat_colors.get(category, Fore.WHITE)}{category.upper()}{Style.RESET_ALL}", Fore.WHITE))
        print(center_text(f"Source:   {Fore.MAGENTA}{source}{Style.RESET_ALL}", Fore.WHITE))
        print(center_border_bottom())
        
        # ============================================================
        # CONFIRMATION
        # ============================================================
        print(f"\n{Fore.YELLOW}â”Œâ”€ {Fore.CYAN}CONFIRM ADD THIS IOC? {Fore.YELLOW}(y/n) {Fore.CYAN}â”€â–º{Style.RESET_ALL} ", end="")
        confirm = input().strip().lower()
        if confirm != 'y':
            print(f"\n{Fore.RED}â•”{'â•' * 50}â•—{Style.RESET_ALL}")
            print(f"{Fore.RED}â•‘  âŒ IOC addition cancelled{Style.RESET_ALL}")
            print(f"{Fore.RED}â•š{'â•' * 50}â•{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        # ============================================================
        # ADD THE IOC
        # ============================================================
        success = self.lab.add_ioc(ioc_type, value, category)
        
        if success:
            # ============================================================
            # SUCCESS BOX - Beautiful glowing
            # ============================================================
            print(f"\n{center_border()}")
            print(center_text("âœ… IOC ADDED SUCCESSFULLY", Fore.GREEN))
            print(center_border_mid())
            print(center_text(f"Type:     {Fore.CYAN}{ioc_type}{Style.RESET_ALL}", Fore.WHITE))
            print(center_text(f"Value:    {Fore.YELLOW}{value}{Style.RESET_ALL}", Fore.WHITE))
            print(center_text(f"Category: {cat_colors.get(category, Fore.WHITE)}{category.upper()}{Style.RESET_ALL}", Fore.WHITE))
            print(center_text(f"Source:   {Fore.MAGENTA}{source}{Style.RESET_ALL}", Fore.WHITE))
            print(center_text(f"Added:    {Fore.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}", Fore.WHITE))
            print(center_border_bottom())
            
            # ============================================================
            # STATISTICS
            # ============================================================
            stats = self.lab.enhanced.threat_intel.get_ioc_stats()
            
            print(f"\n{center_border()}")
            print(center_text("ðŸ“Š Updated IOC Statistics", Fore.CYAN))
            print(center_border_mid())
            
            has_stats = False
            for ioc_type, categories in stats.items():
                if categories:
                    malicious = categories.get('malicious', 0)
                    suspicious = categories.get('suspicious', 0)
                    clean = categories.get('clean', 0)
                    if malicious > 0 or suspicious > 0 or clean > 0:
                        print(center_text(f"{ioc_type}: {Fore.RED}Malicious: {malicious}{Style.RESET_ALL}, {Fore.YELLOW}Suspicious: {suspicious}{Style.RESET_ALL}, {Fore.GREEN}Clean: {clean}{Style.RESET_ALL}", Fore.WHITE))
                        has_stats = True
            
            if not has_stats:
                print(center_text("No IOCs loaded", Fore.DIM))
            
            print(center_border_bottom())
            
            # ============================================================
            # TEST OPTION
            # ============================================================
            print(f"\n{center_border()}")
            print(center_text("ðŸ” Test This IOC?", Fore.CYAN))
            print(center_border_mid())
            print(center_text(f" {Fore.GREEN}[1] Yes{Style.RESET_ALL} - Scan for this IOC", Fore.WHITE))
            print(center_text(f" {Fore.DIM}[2] No{Style.RESET_ALL}  - Return to menu", Fore.WHITE))
            print(center_border_bottom())
            
            print(f"\n{Fore.CYAN}â”Œâ”€ {Fore.YELLOW}â”Œâ”€[ {Fore.GREEN}IOC {Fore.CYAN}]{Style.RESET_ALL} {Fore.MAGENTA}TEST IOC? {Fore.CYAN}â”€â–º{Style.RESET_ALL} ", end="")
            test_choice = input().strip()
            if test_choice == "1":
                self._cmd_test_ioc(ioc_type, value)
            
        else:
            # ============================================================
            # ERROR BOX
            # ============================================================
            print(f"\n{center_border()}")
            print(center_text("âŒ FAILED TO ADD IOC", Fore.RED))
            print(center_border_mid())
            print(center_text("There was an error adding the IOC. Please try again.", Fore.YELLOW))
            print(center_border_bottom())
        
        input("\nPress Enter to continue...")
        
    def _cmd_test_ioc(self, ioc_type: str = None, ioc_value: str = None):
        """Test an IOC against the system"""
        self._clear_screen()
        self._show_centered_banner()
        
        term_width = self._get_terminal_width()
        
        print("â•”" + "â•" * (term_width - 2) + "â•—")
        print("â•‘" + "ðŸ” IOC TESTING".center(term_width - 2) + "â•‘")
        print("â•š" + "â•" * (term_width - 2) + "â•")
        print("")
        
        # If not provided, get from user
        if not ioc_type or not ioc_value:
            print("ðŸ“‹ IOC Types: hash, domain, ip, url, file, registry".center(term_width))
            print("â”€" * term_width)
            
            ioc_type = input("\033[1;36mâ”Œâ”€ IOC Type â”€â”€â–º \033[0m").strip().lower()
            if ioc_type not in ['hash', 'domain', 'ip', 'url', 'file', 'registry']:
                print("\n\033[91mâŒ Invalid IOC type\033[0m")
                input("\nPress Enter to continue...")
                return
            
            ioc_value = input("\033[1;36mâ”Œâ”€ IOC Value â”€â”€â–º \033[0m").strip()
            if not ioc_value:
                print("\n\033[91mâŒ IOC value cannot be empty\033[0m")
                input("\nPress Enter to continue...")
                return
        
        print(f"\nðŸ” Testing IOC: {ioc_type} = {ioc_value}")
        print("â”€" * term_width)
        
        results = []
        
        # Route to appropriate test based on type
        if ioc_type == 'hash':
            results = self._test_hash_ioc(ioc_value)
        elif ioc_type == 'domain':
            results = self._test_domain_ioc(ioc_value)
        elif ioc_type == 'ip':
            results = self._test_ip_ioc(ioc_value)
        elif ioc_type == 'file':
            results = self._test_file_ioc(ioc_value)
        elif ioc_type == 'registry':
            results = self._test_registry_ioc(ioc_value)
        elif ioc_type == 'url':
            results = self._test_url_ioc(ioc_value)
        
        # Display results
        if results:
            print("\n\033[92mâœ… IOC Test Results:\033[0m")
            for result in results:
                if result.startswith("âœ…") or result.startswith("Found"):
                    print(f"  \033[92m{result}\033[0m")
                elif result.startswith("âŒ") or "not found" in result.lower():
                    print(f"  \033[91m{result}\033[0m")
                elif "Warning" in result or "âš ï¸" in result:
                    print(f"  \033[93m{result}\033[0m")
                else:
                    print(f"  \033[94m{result}\033[0m")
        else:
            print("\n\033[92mâœ… No matches found for this IOC\033[0m")
            print("   This means the IOC was not found on your system.")
        
        print("\n" + "â•" * term_width)
        input("\nPress Enter to continue...")
        
    def _test_hash_ioc(self, file_hash: str) -> List[str]:
        """Test a hash IOC against files on the system - FIXED"""
        results = []
        found_files = []
        
        # Normalize hash (remove spaces, convert to lowercase)
        file_hash = file_hash.strip().lower()
        
        # Search in common directories
        search_dirs = [
            os.path.expanduser('~'),
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Documents'),
        ]
        
        results.append(f"ðŸ” Searching for hash: {file_hash}")
        results.append(f"ðŸ“ Scanning {len(search_dirs)} directories...")
        
        total_scanned = 0
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                try:
                    for root, dirs, files in os.walk(search_dir):
                        # Skip system directories for performance
                        skip_dirs = ['Windows', 'System32', 'Program Files', 'AppData', 'node_modules', '.git']
                        if any(skip in root for skip in skip_dirs):
                            continue
                        
                        for file in files[:50]:  # Limit for performance
                            try:
                                filepath = os.path.join(root, file)
                                total_scanned += 1
                                
                                # Skip large files (> 50MB)
                                if os.path.getsize(filepath) > 50 * 1024 * 1024:
                                    continue
                                
                                # Calculate hash
                                import hashlib
                                with open(filepath, 'rb') as f:
                                    file_data = f.read(8192 * 2)  # Read first 16KB for quick hash
                                    md5_hash = hashlib.md5(file_data).hexdigest()
                                    
                                    # If the first 16KB matches, compute full hash
                                    if file_hash in [md5_hash[:32], file_hash[:32]]:
                                        # Full hash
                                        f.seek(0)
                                        full_data = f.read()
                                        md5_full = hashlib.md5(full_data).hexdigest()
                                        sha1_full = hashlib.sha1(full_data).hexdigest()
                                        sha256_full = hashlib.sha256(full_data).hexdigest()
                                        
                                        if file_hash in [md5_full, sha1_full, sha256_full]:
                                            found_files.append(filepath)
                                            results.append(f"âœ… Found matching file: {filepath}")
                                            results.append(f"  MD5: {md5_full}")
                                            results.append(f"  SHA1: {sha1_full}")
                                            results.append(f"  SHA256: {sha256_full}")
                            except:
                                continue
                except Exception as e:
                    continue
        
        results.append(f"ðŸ“Š Scanned {total_scanned} files")
        
        if not found_files:
            results.append("â„¹ï¸ No matching files found for this hash")
        
        return results

    def _test_domain_ioc(self, domain: str) -> List[str]:
        """Test a domain IOC"""
        results = []
        
        # Check hosts file
        hosts_paths = [
            'C:\\Windows\\System32\\drivers\\etc\\hosts',
            '/etc/hosts'
        ]
        
        for hosts_path in hosts_paths:
            if os.path.exists(hosts_path):
                try:
                    with open(hosts_path, 'r') as f:
                        content = f.read()
                        if domain in content:
                            results.append(f"Domain found in hosts file: {hosts_path}")
                except:
                    pass
        
        # Check if domain resolves
        try:
            import socket
            ip = socket.gethostbyname(domain)
            results.append(f"Domain resolves to IP: {ip}")
        except:
            results.append("Domain does not resolve (may be blocked or non-existent)")
        
        # Check common browsers for references
        browser_paths = [
            os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache'),
            os.path.expanduser('~/Library/Caches/Google/Chrome'),
        ]
        
        for browser_path in browser_paths:
            if os.path.exists(browser_path):
                results.append(f"Browser cache found at: {browser_path}")
        
        return results

    def _test_ip_ioc(self, ip: str) -> List[str]:
        """Test an IP IOC"""
        results = []
        
        # Check firewall rules
        try:
            import subprocess
            if platform.system() == 'Windows':
                result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                                    capture_output=True, text=True, timeout=5)
                if ip in result.stdout:
                    results.append(f"IP found in Windows Firewall rules")
        except:
            pass
        
        # Check if IP is pingable
        try:
            import subprocess
            import platform
            param = '-n' if platform.system() == 'Windows' else '-c'
            result = subprocess.run(['ping', param, '1', ip], 
                                capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                results.append(f"IP is reachable (ping successful)")
            else:
                results.append(f"IP is not reachable (ping failed)")
        except:
            results.append("Could not test IP reachability")
        
        # Check for recent connections
        try:
            import psutil
            for conn in psutil.net_connections():
                if conn.raddr and conn.raddr[0] == ip:
                    results.append(f"Found active connection to IP from PID: {conn.pid}")
        except:
            pass
        
        return results

    def _test_file_ioc(self, filepath: str) -> List[str]:
        """Test a file IOC - FIXED with better formatting"""
        results = []
        
        # Normalize path
        filepath = os.path.normpath(filepath)
        
        if os.path.exists(filepath):
            results.append(f"âœ… File exists: {filepath}")
            
            # Get file info
            try:
                import hashlib
                
                # File size
                size = os.path.getsize(filepath)
                results.append(f"  ðŸ“Š File Size: {size:,} bytes ({size/1024:.2f} KB)")
                
                # Modified time
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                results.append(f"  ðŸ“… Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Created time
                created = datetime.fromtimestamp(os.path.getctime(filepath))
                results.append(f"  ðŸ“… Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Calculate hashes
                with open(filepath, 'rb') as f:
                    data = f.read()
                    md5 = hashlib.md5(data).hexdigest()
                    sha1 = hashlib.sha1(data).hexdigest()
                    sha256 = hashlib.sha256(data).hexdigest()
                
                results.append(f"  ðŸ”‘ MD5: {md5}")
                results.append(f"  ðŸ”‘ SHA1: {sha1}")
                results.append(f"  ðŸ”‘ SHA256: {sha256}")
                
                # Check file permissions
                import stat
                perms = []
                if os.access(filepath, os.R_OK):
                    perms.append("Read")
                if os.access(filepath, os.W_OK):
                    perms.append("Write")
                if os.access(filepath, os.X_OK):
                    perms.append("Execute")
                if perms:
                    results.append(f"  ðŸ”“ Permissions: {', '.join(perms)}")
                    
            except Exception as e:
                results.append(f"  âŒ Error reading file: {e}")
        else:
            results.append(f"âŒ File not found: {filepath}")
            results.append("  ðŸ’¡ This file does not exist on your system")
            
            # Check if parent directory exists
            parent = os.path.dirname(filepath)
            if os.path.exists(parent):
                results.append(f"  â„¹ï¸ Parent directory exists: {parent}")
                # List files in parent directory
                try:
                    files = os.listdir(parent)
                    if files:
                        results.append(f"  ðŸ“ Files in directory:")
                        for f in files[:10]:
                            results.append(f"    â€¢ {f}")
                        if len(files) > 10:
                            results.append(f"    ... and {len(files) - 10} more")
                except:
                    pass
            else:
                results.append(f"  âŒ Parent directory does not exist: {parent}")
        
        return results

    def _test_registry_ioc(self, registry_key: str) -> List[str]:
        """Test a registry IOC - FIXED"""
        results = []
        
        if platform.system() != 'Windows':
            results.append("Registry testing only available on Windows")
            return results
        
        try:
            import winreg
            
            # Normalize the registry key
            # Remove any trailing slashes
            registry_key = registry_key.rstrip('\\')
            
            # Parse registry key
            # Format: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\Run
            # Also support shorter formats like: HKLM\Software\Microsoft\Windows\Run
            
            # Map common abbreviations
            hive_map = {
                'HKCR': winreg.HKEY_CLASSES_ROOT,
                'HKCU': winreg.HKEY_CURRENT_USER,
                'HKLM': winreg.HKEY_LOCAL_MACHINE,
                'HKU': winreg.HKEY_USERS,
                'HKCC': winreg.HKEY_CURRENT_CONFIG,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
            }
            
            # Find which hive is being used
            hive_found = None
            hive_str = None
            subkey = ""
            
            for key_name in hive_map:
                if registry_key.upper().startswith(key_name):
                    hive_str = key_name
                    hive_found = hive_map[key_name]
                    # Get the rest of the path
                    if len(registry_key) > len(key_name):
                        subkey = registry_key[len(key_name):].lstrip('\\')
                    break
            
            if not hive_found:
                results.append("âŒ Invalid registry key format. Use format: HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\Run")
                return results
            
            results.append(f"âœ… Parsed: Hive={hive_str}, Subkey={subkey}")
            
            # Check if the key exists
            try:
                key = winreg.OpenKey(hive_found, subkey, 0, winreg.KEY_READ)
                results.append(f"âœ… Registry key exists: {registry_key}")
                
                # Get values
                i = 0
                value_count = 0
                while True:
                    try:
                        name, value, value_type = winreg.EnumValue(key, i)
                        results.append(f"  ðŸ“ Value: {name} = {value} (Type: {value_type})")
                        value_count += 1
                        i += 1
                    except WindowsError:
                        break
                
                if value_count == 0:
                    results.append("  â„¹ï¸ No values found in this registry key")
                
                winreg.CloseKey(key)
                
            except WindowsError as e:
                if "Cannot find" in str(e) or "The system cannot find the file specified" in str(e):
                    results.append(f"âŒ Registry key not found: {registry_key}")
                    results.append("  ðŸ’¡ This key does not exist on your system")
                else:
                    results.append(f"âŒ Error accessing registry: {e}")
                
        except ImportError:
            results.append("âŒ winreg module not available")
        except Exception as e:
            results.append(f"âŒ Error accessing registry: {e}")
        
        return results

    def _test_url_ioc(self, url: str) -> List[str]:
        """Test a URL IOC"""
        results = []
        
        # Check if URL is accessible
        try:
            import requests
            response = requests.get(url, timeout=5, verify=False)
            if response.status_code == 200:
                results.append(f"âœ… URL is accessible (Status: {response.status_code})")
            else:
                results.append(f"URL returned status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            results.append("âŒ URL is not accessible (Connection Error)")
        except requests.exceptions.Timeout:
            results.append("âŒ URL timed out")
        except Exception as e:
            results.append(f"Error checking URL: {e}")
        
        # Check common browser history files
        history_paths = [
            os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History'),
            os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/History'),
        ]
        
        # Parse domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        if domain:
            results.append(f"Domain from URL: {domain}")
            # Check hosts file for domain
            hosts_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts' if platform.system() == 'Windows' else '/etc/hosts'
            if os.path.exists(hosts_path):
                try:
                    with open(hosts_path, 'r') as f:
                        if domain in f.read():
                            results.append(f"Domain found in hosts file: {hosts_path}")
                except:
                    pass
        
        return results

    def _cmd_list_iocs(self):
        """List all loaded IOCs"""
        self._clear_screen()
        self._show_centered_banner()
        
        print("\n" + "â•" * 80)
        print("ðŸ“Š LOADED IOCs".center(80))
        print("â•" * 80)
        
        iocs = self.lab.enhanced.threat_intel.get_all_iocs()
        
        total_malicious = 0
        total_suspicious = 0
        
        for ioc_type, categories in iocs.items():
            if categories:
                malicious = categories.get('malicious', [])
                suspicious = categories.get('suspicious', [])
                
                if malicious or suspicious:
                    print(f"\nðŸ“ {ioc_type.upper()} ({len(malicious)} malicious, {len(suspicious)} suspicious):")
                    
                    for ioc in malicious[:5]:
                        print(f"  ðŸ”´ {ioc}")
                    if len(malicious) > 5:
                        print(f"    ... and {len(malicious) - 5} more malicious")
                    
                    for ioc in suspicious[:5]:
                        print(f"  ðŸŸ¡ {ioc}")
                    if len(suspicious) > 5:
                        print(f"    ... and {len(suspicious) - 5} more suspicious")
                    
                    total_malicious += len(malicious)
                    total_suspicious += len(suspicious)
        
        if total_malicious == 0 and total_suspicious == 0:
            print("\nðŸ“­ No IOCs loaded")
        else:
            print(f"\nðŸ“Š Total: {total_malicious} malicious, {total_suspicious} suspicious")
        
        print("\n" + "â•" * 80)
        input("\nPress Enter to continue...")
        
    def _cmd_enhanced_report(self):
        """Generate an enhanced report"""
        if not self.lab.running:
            self._set_notification("âŒ Lab is not running", "red")
            return
        
        self._set_notification("ðŸ“Š Generating enhanced report...", "yellow")
        
        print("\nðŸ“Š GENERATING ENHANCED REPORT")
        print("â•" * 80)
        
        result = self.lab.generate_enhanced_report()
        
        if result:
            print(f"âœ… Report generated: {result}")
            print("ðŸ“ Report saved in reports directory")
        else:
            print("âŒ Failed to generate report")
        
        input("\nPress Enter to continue...")
    
    def _show_help(self):
        """Show help"""
        self._clear_screen()
        self._show_centered_banner()
        
        help_text = """
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘  ðŸ“š AVAILABLE COMMANDS                                       â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘  1. Start Lab Monitoring     - Begin 24/7 monitoring        â•‘
â•‘  2. Stop Lab Monitoring      - Stop monitoring              â•‘
â•‘  3. Show Status             - Display current status        â•‘
â•‘  4. Run Threat Scan          - Scan for threats             â•‘
â•‘  5. Generate Report          - Create report                â•‘
â•‘  6. List Threats             - Show detected threats        â•‘
â•‘  7. Show Results             - Show lab results             â•‘
â•‘  8. Export Data              - Export findings              â•‘
â•‘  p. View Processes           - Show running processes       â•‘
â•‘  e. Enhanced Modules         - MITRE, Alerts, Intel         â•‘
â•‘  h. Help                    - Show this help               â•‘
â•‘  q. Exit                    - Exit dashboard               â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"""
        print(help_text)
        input(f"\nPress Enter to continue...")
    
    def _cmd_start(self):
        if self.lab.running:
            self._set_notification("âš ï¸ Lab is already running", "yellow")
            return
        
        self._set_notification("ðŸ”„ Starting lab monitoring...", "yellow")
        success = self.lab.start()
        if success:
            self._set_notification("âœ… Lab started successfully!", "green")
        else:
            self._set_notification("âŒ Failed to start lab", "red")
    
    def _cmd_stop(self):
        if not self.lab.running:
            self._set_notification("âš ï¸ Lab is not running", "yellow")
            return
        
        self._set_notification("ðŸ”„ Stopping lab...", "yellow")
        self.lab.stop()
        self._set_notification("âœ… Lab stopped", "green")
    
    def _cmd_status(self):
        """Show status"""
        status = self.lab.get_status()
        reports = self.lab.get_reports()
        process_stats = self.lab.get_process_stats()
        self._clear_screen()
        self._show_centered_banner()
        
        status_text = f"""
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘  ðŸ“Š LAB STATUS                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘  State:         {status.get('state', 'UNKNOWN')}
â•‘  Running:       {'âœ… YES' if status.get('running') else 'âŒ NO'}
â•‘  Uptime:        {status.get('uptime_display', 'N/A')}
â•‘  Alerts:        {status.get('total_alerts', 0)}
â•‘  Threats:       {status.get('active_threats', 0)}
â•‘  Files Scanned: {status.get('files_scanned', 0)}
â•‘  Monitored:     {status.get('monitored_paths', 0)} paths
â•‘  Processes:     {process_stats.get('total_processes', 0)}
â•‘  Threatened:    {process_stats.get('processes_with_threats', 0)}
â•‘  Reports:       {len(reports)}
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"""
        print(status_text)
        input(f"\nPress Enter to continue...")
    
    def _cmd_scan(self):
        """Run threat scan - SYSTEM WIDE"""
        if not self.lab.running:
            self._set_notification("âŒ Lab is not running. Start it first.", "red")
            return
        
        self._set_notification("ðŸ” Running system-wide threat scan...", "yellow")
        self._clear_screen()
        
        term_width = self._get_terminal_width()
        
        header = "â•”" + "â•" * (term_width - 2) + "â•—"
        title_padded = "â•‘" + "ðŸ” SYSTEM-WIDE THREAT SCAN IN PROGRESS".center(term_width - 2) + "â•‘"
        footer = "â•š" + "â•" * (term_width - 2) + "â•"
        
        print(header)
        print(title_padded)
        print(footer)
        print("")
        
        print("ðŸ“ Scanning System Locations".center(term_width))
        print("â”€" * term_width)
        
        print("ðŸ” Scanning in progress...".center(term_width))
        print("")
        
        spinner_chars = ['â ‹', 'â ™', 'â ¹', 'â ¸', 'â ¼', 'â ´', 'â ¦', 'â §', 'â ‡', 'â ']
        spinner_idx = 0
        
        scan_result = []
        scan_complete = False
        
        def run_scan():
            nonlocal scan_result, scan_complete
            scan_result = self.lab.run_system_scan()
            scan_complete = True
        
        scan_thread = threading.Thread(target=run_scan)
        scan_thread.start()
        
        while not scan_complete:
            spinner = spinner_chars[spinner_idx % len(spinner_chars)]
            status_msg = f"{spinner} Scanning files... Please wait"
            print(f"\r{status_msg.center(term_width)}", end="", flush=True)
            spinner_idx += 1
            time.sleep(0.1)
        
        print("\r" + " " * term_width, end="")
        print("\râœ… Scan complete!".center(term_width))
        print("")
        
        results = scan_result
        
        print("")
        print("â•”" + "â•" * (term_width - 2) + "â•—")
        title_result = "â•‘" + "ðŸ“Š SCAN RESULTS".center(term_width - 2) + "â•‘"
        print(title_result)
        print("â•š" + "â•" * (term_width - 2) + "â•")
        print("")
        
        if results:
            critical = [r for r in results if r.get('severity') == 'CRITICAL']
            high = [r for r in results if r.get('severity') == 'HIGH']
            medium = [r for r in results if r.get('severity') == 'MEDIUM']
            low = [r for r in results if r.get('severity') == 'LOW']
            
            print(f"ðŸš¨ Found {len(results)} threats".center(term_width))
            print("â”€" * term_width)
            
            severity_lines = []
            if critical:
                severity_lines.append(f"ðŸ”´ CRITICAL: {len(critical)}")
            if high:
                severity_lines.append(f"ðŸŸ¡ HIGH: {len(high)}")
            if medium:
                severity_lines.append(f"ðŸ”µ MEDIUM: {len(medium)}")
            if low:
                severity_lines.append(f"ðŸŸ¢ LOW: {len(low)}")
            
            for line in severity_lines:
                print(line.center(term_width))
            print("")
            
            for i, r in enumerate(results[:10], 1):
                threat_line = f"   {i}. {r.get('severity', 'UNKNOWN')} - {r.get('description', '')[:50]}"
                print(threat_line.center(term_width))
                if r.get('source'):
                    source_line = f"      ðŸ“ {r.get('source', '')[:50]}"
                    print(source_line.center(term_width))
                print("")
            
            if len(results) > 10:
                print(f"   ... and {len(results) - 10} more threats".center(term_width))
        else:
            print("âœ… No threats detected - System is clean!".center(term_width))
        
        print("")
        print("â•" * term_width)
        
        self._set_notification(f"âœ… Scan complete. Found {len(results)} threats", "green")
        print("\nPress Enter to continue...".center(term_width))
        input()
    
    def _cmd_report(self):
        """Generate a report"""
        if not self.lab.running:
            self._set_notification("âŒ Lab is not running", "red")
            return
        
        if self.use_rich and self.console:
            format_choice = Prompt.ask(
                "[bold cyan]â”Œâ”€ Report Format â”€â”€â–º[/bold cyan]",
                choices=["pdf", "html", "json", "txt"],
                default="pdf"
            )
        else:
            print("\nâ”Œâ”€ Report Format â”€â”€â–º")
            print("  [pdf] [html] [json] [txt]")
            format_choice = input("Select format (default: pdf): ").strip().lower()
            if not format_choice or format_choice not in ["pdf", "html", "json", "txt"]:
                format_choice = "pdf"
        
        self._set_notification(f"ðŸ“„ Generating {format_choice} report...", "yellow")
        result = self.lab.generate_report(format_choice)
        
        if result:
            print(f"âœ… Report generated: {result}")
            reports = self.lab.get_reports()
            if reports:
                latest = reports[-1]
                print(f"ðŸ“Š Size: {latest.size // 1024} KB")
                print(f"ðŸ”– ID: {latest.report_id}")
            self._set_notification(f"âœ… Report generated: {result}", "green")
        else:
            print("âŒ Failed to generate report")
            self._set_notification("âŒ Failed to generate report", "red")
        
        input("\nPress Enter to continue...")
    
    def _cmd_threats(self):
        """List threats"""
        threats = self.lab.get_threats()
        self._clear_screen()
        self._show_centered_banner()
        
        if not threats:
            print(f"\nâœ… No threats detected")
        else:
            print(f"\nðŸš¨ DETECTED THREATS ({len(threats)})")
            print("â”€" * 80)
            
            for i, t in enumerate(threats[:10], 1):
                print(f"\n{i}. {t.get('severity', 'INFO')} {t.get('description', '')}")
                print(f"   ID: {t.get('event_id', '')}")
                print(f"   Category: {t.get('category', '')}")
                print(f"   Status: {t.get('status', '')}")
                print(f"   Source: {t.get('source', '')}")
            
            if len(threats) > 10:
                print(f"\n... and {len(threats) - 10} more")
        
        input(f"\nPress Enter to continue...")
    
    def _cmd_results(self):
        results = self.lab.get_results()
        self._clear_screen()
        self._show_centered_banner()
        
        if not results:
            print(f"\nâ„¹ï¸ No results yet")
        else:
            print(f"\nðŸ“Š LAB RESULTS")
            print("â”€" * 80)
            
            for r in results[-5:]:
                print(f"\nðŸ”¬ {r.get('name', 'Unknown')}")
                print(f"   ID: {r.get('experiment_id', 'N/A')}")
                print(f"   Status: {r.get('status', 'N/A')}")
                print(f"   Duration: {r.get('duration', 0):.2f}s")
                print(f"   Findings: {len(r.get('findings', []))}")
        
        input(f"\nPress Enter to continue...")
    
    def _cmd_export(self):
        if not self.lab.running:
            self._set_notification("âŒ Lab is not running", "red")
            return
        
        if self.use_rich and self.console:
            export_type = Prompt.ask(
                "[bold cyan]â”Œâ”€ Export Type â”€â”€â–º[/bold cyan]",
                choices=["json", "csv", "all"],
                default="json"
            )
        else:
            print("\nâ”Œâ”€ Export Type â”€â”€â–º")
            print("  [1] JSON  [2] CSV  [3] All")
            choice = input("Select format (1-3, default: 1): ").strip()
            format_map = {'1': 'json', '2': 'csv', '3': 'all'}
            export_type = format_map.get(choice, 'json')
        
        self._set_notification(f"ðŸ“¤ Exporting {export_type} data...", "yellow")
        result = self.lab.export_data(export_type)
        if result:
            print(f"âœ… Exported: {result}")
            self._set_notification(f"âœ… Exported: {result}", "green")
        else:
            print("âŒ Failed to export")
            self._set_notification("âŒ Failed to export", "red")
        
        input("\nPress Enter to continue...")
    
    def _cmd_processes(self):
        """Display running processes"""
        self._clear_screen()
        self._show_centered_banner()
        
        processes = self.lab.get_processes()
        process_stats = self.lab.get_process_stats()
        
        print("â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
        print("â•‘  ðŸ”„ RUNNING PROCESSES                                              â•‘")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        print("")
        
        if not PSUTIL_AVAILABLE:
            print("âš ï¸ psutil is not installed. Process monitoring is disabled.")
            print("   Install with: pip install psutil")
            print("")
            print("â•" * 80)
            input("\nPress Enter to continue...")
            return
        
        print(f"ðŸ“Š Total: {process_stats.get('total_processes', 0)} processes")
        print(f"   System: {process_stats.get('system_processes', 0)} | User: {process_stats.get('user_processes', 0)}")
        
        if process_stats.get('processes_with_threats', 0) > 0:
            print(f"   âš ï¸ Threatened: {process_stats.get('processes_with_threats', 0)}")
        else:
            print(f"   âœ… Threatened: {process_stats.get('processes_with_threats', 0)}")
        
        print(f"   Monitoring: {'âœ… Active' if process_stats.get('is_monitoring', False) else 'âŒ Inactive'}")
        print("")
        
        if processes:
            sorted_procs = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)
            print("â”Œâ”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”")
            print("â”‚ PID â”‚ Name                           â”‚ Duration â”‚ CPU %   â”‚ Memory   â”‚ Threats â”‚")
            print("â”œâ”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤")
            
            for p in sorted_procs[:20]:
                duration = f"{int(p.duration // 60)}m {int(p.duration % 60)}s"
                threat_icon = "âš ï¸" if p.threats else " "
                print(f"â”‚ {str(p.pid):<4} â”‚ {p.name[:30]:<30} â”‚ {duration:>8} â”‚ {p.cpu_percent:>6.1f}% â”‚ {p.memory_mb:>7.1f}MB â”‚ {threat_icon}{len(p.threats):>2}  â”‚")
            
            if len(processes) > 20:
                print(f"â”œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤")
                print(f"â”‚ ... and {len(processes) - 20} more processes")
            
            print("â””â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜")
        else:
            print("   No processes detected")
            print("")
            print("   Possible reasons:")
            print("   1. psutil is not installed (pip install psutil)")
            print("   2. Process monitoring is not running")
            print("   3. Permission issues on your system")
            print("   4. The lab is not fully started")
        
        print("")
        print("â•" * 80)
        input("\nPress Enter to continue...")
    
    def _set_notification(self, message: str, color: str = "white"):
        self.notification = message
        self.notification_time = time.time()
    
    def _exit_dashboard(self):
        self._set_notification("ðŸ‘‹ Exiting dashboard...", "yellow")
        time.sleep(1)
        self.running = False
        if self.lab.running:
            self.lab.stop()
    
    def _run_simple_dashboard(self):
        """Fallback simple dashboard when Rich is not available"""
        while self.running:
            self._clear_screen()
            self._show_centered_banner()
            print("\n[1] Start Lab  [2] Stop Lab  [3] Status  [4] Scan")
            print("[5] Report  [6] Threats  [7] Results  [8] Export")
            print("[p] Processes  [e] Enhanced  [h] Help  [q] Exit\n")
            
            if self.notification and (time.time() - self.notification_time < 5):
                print(f"ðŸ“Œ {self.notification}\n")
            
            choice = input("Select option: ").strip().lower()
            
            if choice == 'q':
                self._exit_dashboard()
                break
            elif choice == 'h':
                self._show_help()
            elif choice == '1':
                self._cmd_start()
            elif choice == '2':
                self._cmd_stop()
            elif choice == '3':
                self._cmd_status()
            elif choice == '4':
                self._cmd_scan()
            elif choice == '5':
                self._cmd_report()
            elif choice == '6':
                self._cmd_threats()
            elif choice == '7':
                self._cmd_results()
            elif choice == '8':
                self._cmd_export()
            elif choice == 'p':
                self._cmd_processes()
            elif choice == 'e':
                self._cmd_enhanced()
            else:
                print("Invalid option. Press Enter to continue...")
                input()
# ============================================================
# TYPEWRITER CLASS (for typing effects)
# ============================================================

class TypeWriter:
    def __init__(self, speed='fast'):
        self.speed_presets = {'slow': (30, 60), 'medium': (15, 35), 'fast': (5, 15), 'instant': (0, 0)}
        self.set_speed(speed)
        self.punctuation_delay = 1.5
        self.typing_enabled = True
        self.use_colors = USE_COLORS
        
    def set_speed(self, speed):
        if speed in self.speed_presets:
            self.min_delay, self.max_delay = self.speed_presets[speed]
        else:
            self.min_delay, self.max_delay = self.speed_presets['fast']
    
    def type_text(self, text, color=Colors.GREEN, newline=True, pen_effect=True):
        if not self.typing_enabled:
            print(text, end='\n' if newline else '')
            return
        
        pause_chars = ['.', ',', '!', '?', ';', ':']
        for i, char in enumerate(text):
            if char == '\n':
                print()
                continue
            else:
                if self.use_colors and color and pen_effect and (i == 0 or text[i-1] == ' '):
                    sys.stdout.write(f"{Colors.BOLD}{color}{char}{Colors.END}")
                elif self.use_colors and color:
                    sys.stdout.write(f"{color}{char}{Colors.END}")
                else:
                    sys.stdout.write(char)
                sys.stdout.flush()
            
            if self.min_delay == 0 and self.max_delay == 0:
                delay = 0
            else:
                delay = random.uniform(self.min_delay, self.max_delay) / 1000.0
                if char in pause_chars:
                    delay *= self.punctuation_delay
                if char == ' ':
                    delay *= 0.7
            time.sleep(delay)
        
        if newline:
            print()
    
    def type_line(self, text, color=Colors.GREEN):
        self.type_text(text, color, newline=True)
    
    def type_banner(self, lines, color=Colors.CYAN):
        original_speed = self.min_delay, self.max_delay
        self.min_delay, self.max_delay = 2, 5
        for line in lines:
            self.type_text(line, color, newline=True, pen_effect=False)
            time.sleep(0.1)
        self.min_delay, self.max_delay = original_speed


# ============================================================
# MAIN SOC AUTOMATED LAB CLASS
# ============================================================

class SOCAutomatedLab:
    def __init__(self, workspace_path: str, config: Dict[str, Any] = None):
        self.workspace_path = workspace_path
        self.config = config or {}
        self.ai_engine = AIThreatDetectionEngine(workspace_path)
        self.monitor = LabMonitor(workspace_path, self.ai_engine, self.config)
        self.process_monitor = ProcessMonitor(workspace_path)
        self.report_generator = ReportGenerator(workspace_path)
        self.running = False
        self.start_time = datetime.now()
        self.results = []
        self.dashboard = None
        self.state = LabStatus.IDLE
        self._report_scheduler = None
        
        self.enhanced = EnhancedModulesManager(workspace_path)
        self.enhanced.start()
        
        # Connect process monitor to AI engine
        self.ai_engine.set_process_monitor(self.process_monitor)
        
        self._setup_logging()
        self._load_config()
        
        if RICH_AVAILABLE:
            self.dashboard = SOCLabDashboard(self)
        else:
            self.dashboard = SOCLabDashboard(self)
        
        atexit.register(self.cleanup)
    
    def run_system_scan(self) -> List[Dict]:
        """Run a system-wide threat scan - CLEAN OUTPUT"""
        scan_paths = self._get_system_scan_paths()
        findings = []
        total_scanned = 0
        max_files_per_dir = 200
        
        for path in scan_paths:
            if os.path.exists(path):
                # Show current path being scanned (one line only)
                print(f"\r   ðŸ“ Scanning: {path[:50]}...".ljust(80), end="", flush=True)
                try:
                    for root, dirs, files in os.walk(path):
                        # Skip system directories
                        skip_dirs = ['windows\\system32', 'windows\\syswow64', 'windows\\winsxs', 
                                    'program files', 'program files (x86)', 'appdata',
                                    'node_modules', '.git', '__pycache__', '.venv', 'venv']
                        if any(skip in root.lower() for skip in skip_dirs):
                            continue
                        
                        for file in files[:max_files_per_dir]:
                            try:
                                filepath = os.path.join(root, file)
                                try:
                                    if os.path.getsize(filepath) > 50 * 1024 * 1024:
                                        continue
                                except:
                                    continue
                                
                                threats = self.ai_engine.analyze_file(filepath)
                                if threats:
                                    findings.extend(threats)
                                total_scanned += 1
                                
                                # Update progress every 50 files
                                if total_scanned % 50 == 0:
                                    print(f"\r   ðŸ“ Scanning: {path[:40]}... | Files: {total_scanned}".ljust(80), end="", flush=True)
                                    
                            except (PermissionError, OSError):
                                continue
                            except Exception as e:
                                self.logger.debug(f"Scan error: {e}")
                                continue
                except Exception as e:
                    self.logger.debug(f"Error scanning {path}: {e}")
                    continue
        
        print("\r" + " " * 80, end="")  # Clear the line
        print(f"\r   âœ… Scan complete! Files scanned: {total_scanned}".ljust(80))
        
        # Create result
        result = LabResult(
            experiment_id=f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(),
            name="System-Wide Scan",
            status=LabStatus.COMPLETED,
            metrics={'files_scanned': total_scanned, 'threats_found': len(findings)},
            findings=findings,
            duration=0
        )
        self.results.append(result)
        
        return [{
            'description': f.description,
            'severity': f.severity.name,
            'source': f.source_detail,
            'category': f.category.value,
            'status': f.status.value
        } for f in findings]
        
    def _get_system_scan_paths(self) -> List[str]:
        """Get system-wide scan paths based on OS"""
        paths = []
        
        if platform.system() == 'Windows':
            # Get all drives
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    # Only include system drives (C:, D:) and avoid network drives
                    if letter in ['C', 'D', 'E', 'F']:
                        paths.append(drive)
            
            # Add common Windows user paths
            home = os.path.expanduser('~')
            user_paths = [
                home,
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Videos'),
                os.path.join(home, 'Music'),
                os.path.join(home, 'Projects'),
                os.path.join(home, 'Workspace'),
            ]
            for path in user_paths:
                if os.path.exists(path) and path not in paths:
                    paths.append(path)
            
        elif platform.system() == 'Linux':
            paths.extend(['/', '/home', '/usr', '/var', '/opt', '/etc'])
            
        elif platform.system() == 'Darwin':  # macOS
            paths.extend(['/', '/Users', '/Applications', '/Library', '/usr', '/var'])
        
        # Remove duplicates and non-existent paths
        paths = list(set([p for p in paths if os.path.exists(p)]))
        return paths

    def _setup_logging(self):
        log_path = os.path.join(self.workspace_path, 'logs', 'soc_lab.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        handler = logging.FileHandler(log_path)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger = logging.getLogger('SOC_Lab')
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _load_config(self):
        default_config = {
            'monitor_paths': [
                os.path.expanduser('~'),
                os.path.expanduser('~/Desktop'),
                os.path.expanduser('~/Downloads'),
                os.path.expanduser('~/Documents'),
            ],
            'exclude_patterns': ['*.tmp', '*.temp', '*.log', '*.cache'],
            'auto_response': True,
            'max_file_size_mb': 100,
            'auto_report_interval': 3600,  # Generate report every hour
            'process_monitoring_enabled': True,
            'process_scan_interval': 10,  # seconds
        }
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
    
    def start(self) -> bool:
        if self.running:
            return True
        
        self.state = LabStatus.INITIALIZING
        monitor_paths = self.config.get('monitor_paths', [])
        
        # Add system paths
        if platform.system() == 'Windows':
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    monitor_paths.append(drive)
        else:
            monitor_paths.extend(['/', '/home', '/usr', '/var'])
        
        monitor_paths = list(set([p for p in monitor_paths if os.path.exists(p)]))
        
        print(f"ðŸ“ Starting monitoring on {len(monitor_paths)} paths...")
        
        # Start file system monitoring
        fs_success = self.monitor.start_monitoring(monitor_paths)
        
        # Start process monitoring
        process_success = True
        if self.config.get('process_monitoring_enabled', True):
            print("ðŸ”„ Starting process monitoring...")
            process_success = self.process_monitor.start_monitoring()
            if process_success:
                self.logger.info("Process monitoring started")
                # Remove the duplicate print here - it's already printed in ProcessMonitor.start_monitoring()
            else:
                self.logger.warning("Process monitoring failed to start")
                print("âš ï¸ Process monitoring failed. Check if psutil is installed.")
        
        if fs_success:
            self.running = True
            self.start_time = datetime.now()
            self.state = LabStatus.RUNNING
            self.logger.info("Lab started")
            
            # Start automatic report generation
            self._start_auto_reporting()
            
            return True
        else:
            self.state = LabStatus.ERROR
            print("âŒ Failed to start lab")
            return False
        

    def stop(self):
        if not self.running:
            return
        
        # Stop auto-reporting
        if self._report_scheduler:
            self._report_scheduler = None
        
        # Stop process monitoring
        self.process_monitor.monitoring = False
        
        # Stop file system monitoring
        self.monitor.stop_monitoring()
        
        # Generate final report
        self.generate_report('pdf')
        
        self.running = False
        self.state = LabStatus.STOPPED
        self.logger.info("Lab stopped")
    
    def _start_auto_reporting(self):
        """Start automatic report generation in background"""
        def auto_report_generator():
            interval = self.config.get('auto_report_interval', 3600)
            formats = ['pdf', 'html', 'json', 'txt']
            format_index = 0
            
            while self.running:
                time.sleep(interval)
                if self.running:
                    try:
                        report_format = formats[format_index % len(formats)]
                        format_index += 1
                        self.generate_report(report_format)
                        self.logger.info(f"Auto report generated: {report_format}")
                    except Exception as e:
                        self.logger.error(f"Auto report failed: {e}")
        
        self._report_scheduler = threading.Thread(target=auto_report_generator, daemon=True)
        self._report_scheduler.start()
        self.logger.info("Auto-reporting started")
    
    def pause(self) -> bool:
        if not self.running:
            return False
        self.state = LabStatus.PAUSED
        self.monitor.paused = True
        self.process_monitor.monitoring = False
        return True
    
    def resume(self) -> bool:
        if not self.running:
            return False
        self.state = LabStatus.RUNNING
        self.monitor.paused = False
        if self.config.get('process_monitoring_enabled', True):
            self.process_monitor.monitoring = True
            self.process_monitor._start_scan_thread()
        return True
    
    def cleanup(self):
        if self.running:
            self.stop()
    
    def run_scan(self) -> List[Dict]:
        print("ðŸ” Scanning...")
        scan_paths = [
            os.path.expanduser('~'),
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Downloads'),
        ]
        
        findings = []
        for path in scan_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files[:50]:
                        try:
                            filepath = os.path.join(root, file)
                            threats = self.ai_engine.analyze_file(filepath)
                            if threats:
                                findings.extend(threats)
                        except:
                            pass
        
        # Create result
        result = LabResult(
            experiment_id=f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(),
            name="Manual Scan",
            status=LabStatus.COMPLETED,
            metrics={'files_scanned': len(findings)},
            findings=findings,
            duration=0
        )
        self.results.append(result)
        
        return [{
            'description': f.description,
            'severity': f.severity.name,
            'source': f.source_detail
        } for f in findings]
    
    def generate_report(self, report_format: str = 'pdf') -> str:
        """Generate a report"""
        stats = self.monitor.get_statistics()
        threats = self.monitor.get_threats()
        lab_state = self.state.value
        
        return self.report_generator.generate_report(
            monitor=self.monitor,
            ai_engine=self.ai_engine,
            report_format=report_format,
            lab_state=lab_state,
            process_monitor=self.process_monitor
        )
    
    def get_reports(self) -> List[LabReport]:
        """Get all generated reports"""
        return self.report_generator.get_reports()
    
    def get_processes(self) -> List[ProcessInfo]:
        """Get all running processes"""
        return self.process_monitor.get_processes()
    
    def get_process_stats(self) -> Dict:
        """Get process monitoring statistics"""
        return self.process_monitor.get_statistics()
    
    def export_data(self, export_type: str = 'json') -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{timestamp}.{export_type}"
        filepath = os.path.join(self.workspace_path, 'reports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.monitor.get_statistics(),
            'process_statistics': self.process_monitor.get_statistics(),
            'threats': self.monitor.get_threats(),
            'processes': [
                {
                    'pid': p.pid,
                    'name': p.name,
                    'duration': p.duration,
                    'cpu_percent': p.cpu_percent,
                    'memory_mb': p.memory_mb,
                    'status': p.status,
                    'threats': len(p.threats)
                }
                for p in self.process_monitor.get_processes()[:50]
            ],
            'results': [{
                'id': r.experiment_id,
                'name': r.name,
                'duration': r.duration,
                'findings': len(r.findings)
            } for r in self.results[-5:]]
        }
        
        if export_type == 'json':
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif export_type == 'csv':
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Event ID', 'Timestamp', 'Severity', 'Category', 'Description'])
                for t in self.monitor.get_threats():
                    writer.writerow([
                        t.get('event_id', ''),
                        t.get('timestamp', ''),
                        t.get('severity', ''),
                        t.get('category', ''),
                        t.get('description', '')
                    ])
        elif export_type == 'all':
            for fmt in ['json', 'csv']:
                self.export_data(fmt)
            return "All formats exported"
        
        return filepath
    
    def get_status(self) -> Dict[str, Any]:
        stats = self.monitor.get_statistics()
        process_stats = self.process_monitor.get_statistics()
        uptime = datetime.now() - self.start_time if self.running else timedelta(0)
        reports = self.get_reports()
        
        return {
            'running': self.running,
            'state': self.state.value,
            'monitoring': self.monitor.monitoring,
            'process_monitoring': self.process_monitor.monitoring,
            'total_alerts': stats['total_alerts'],
            'active_threats': stats['active_threats'],
            'files_scanned': stats['files_scanned'],
            'monitored_paths': len(self.config.get('monitor_paths', [])),
            'total_processes': process_stats.get('total_processes', 0),
            'processes_with_threats': process_stats.get('processes_with_threats', 0),
            'uptime_display': str(uptime).split('.')[0],
            'workspace': self.workspace_path,
            'reports_count': len(reports)
        }
    
    def get_threats(self) -> List[Dict[str, Any]]:
        return self.monitor.get_threats()
    
    def get_results(self) -> List[Dict[str, Any]]:
        return [{
            'experiment_id': r.experiment_id,
            'timestamp': r.timestamp.isoformat(),
            'name': r.name,
            'status': r.status.value,
            'duration': r.duration,
            'findings': r.findings,
            'metrics': r.metrics
        } for r in self.results]




# ======================enhanced integrall======
    def generate_enhanced_report(self) -> str:
        """Generate an enhanced report with all analytics"""
        threats = self.monitor.get_threats()
        stats = self.monitor.get_statistics()
        process_stats = self.process_monitor.get_statistics()
        
        return self.enhanced.generate_full_report(threats, stats, process_stats)

    def add_ioc(self, ioc_type: str, value: str, category: str = 'malicious'):
        """Add an IOC to threat intelligence"""
        return self.enhanced.add_ioc(ioc_type, value, category)

    def get_enhanced_status(self) -> Dict:
        """Get status of enhanced modules"""
        return self.enhanced.get_status()
# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='SOC Automated Lab')
    parser.add_argument('--dashboard', action='store_true', help='Start interactive dashboard')
    parser.add_argument('--start', action='store_true', help='Start the lab')
    parser.add_argument('--stop', action='store_true', help='Stop the lab')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--workspace', default=os.path.expanduser('~/soc_lab_workspace'),
                       help='Workspace directory')
    
    args = parser.parse_args()
    
    lab = SOCAutomatedLab(args.workspace)
    
    if args.dashboard:
        lab.dashboard.start_dashboard()
    elif args.start:
        lab.start()
    elif args.stop:
        lab.stop()
    elif args.status:
        status = lab.get_status()
        print("\n" + "=" * 80)
        print("SOC AUTOMATED LAB STATUS")
        print("=" * 80)
        for key, value in status.items():
            print(f"{key}: {value}")
        print("=" * 80 + "\n")
    elif args.report:
        lab.generate_report()
    else:
        # Default: start dashboard
        lab.dashboard.start_dashboard()

if __name__ == "__main__":
    main()