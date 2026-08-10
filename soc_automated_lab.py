#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import codecs
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

# ============================================================
# FIX CONSOLE ENCODING FOR WINDOWS
# ============================================================

def fix_console_encoding():
    """Fix console encoding for Windows to display UTF-8 box drawing characters"""
    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleCP(65001)
            kernel32.SetConsoleOutputCP(65001)
            
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                if not (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING):
                    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
            
            if sys.stdout.encoding != 'utf-8':
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass

# Apply encoding fix
fix_console_encoding()

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
    pid: int
    name: str
    cmdline: str
    start_time: datetime
    duration: float
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
# PROCESS MONITOR - COMPLETE FIXED VERSION
# ============================================================

class ProcessMonitor:
    """Monitor running processes and detect threats"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.processes = {}
        self.process_history = deque(maxlen=10000)
        self.monitoring = False
        self.logger = logging.getLogger('SOC_Lab.ProcessMonitor')
        self.scan_interval = 3
        self.threat_detection_enabled = True
        self._scan_thread = None
        self._stop_event = threading.Event()
        self._initial_scan_done = False
        
        self.suspicious_patterns = {
            'cryptolocker': ['cryptolocker', 'decrypt', 'encrypt', 'ransom'],
            'malware': ['malware', 'virus', 'trojan', 'worm', 'backdoor', 'rootkit'],
            'mining': ['miner', 'mining', 'crypto', 'bitcoin', 'ethereum', 'monero'],
            'keylogger': ['keylog', 'keyboard', 'logger', 'spy', 'hook'],
            'ransomware': ['ransom', 'encrypt', 'decrypt', 'lock', 'pay'],
            'phishing': ['phish', 'login', 'verify', 'update', 'confirm'],
            'suspicious': ['nc', 'netcat', 'nmap', 'masscan', 'sqlmap', 'hydra'],
        }
        
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
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not installed. Process monitoring disabled.")
            print("⚠️ psutil not installed. Install with: pip install psutil")
        else:
            print("✅ psutil found - Process monitoring available")
    
    def start_monitoring(self):
        if not PSUTIL_AVAILABLE:
            self.logger.error("Cannot start process monitoring: psutil not available")
            return False
        
        if self.monitoring:
            return True
        
        self.monitoring = True
        self._stop_event.clear()
        self._initial_scan_done = False
        self._scan_processes()
        self._initial_scan_done = True
        self._start_scan_thread()
        return True

    def stop_monitoring(self):
        self.monitoring = False
        self._stop_event.set()
        if self._scan_thread:
            self._scan_thread.join(timeout=3)
        self.logger.info("Process monitoring stopped")
        print("✅ Process monitoring stopped")
    
    def _start_scan_thread(self):
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
                
                for _ in range(self.scan_interval):
                    if self._stop_event.is_set() or not self.monitoring:
                        break
                    time.sleep(1)
            self.logger.info("Process scan thread stopped")
        
        self._scan_thread = threading.Thread(target=scan_loop, daemon=True)
        self._scan_thread.start()
    
    def _scan_processes(self):
        if not PSUTIL_AVAILABLE:
            return
        
        current_pids = set()
        new_processes = []
        removed_processes = []
        
        try:
            processes_found = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time',
                                            'cpu_percent', 'memory_info', 'status', 'username']):
                try:
                    pid = proc.info['pid']
                    current_pids.add(pid)
                    processes_found += 1
                    name = proc.info.get('name', 'unknown')
                    
                    if pid in self.processes:
                        proc_info = self.processes[pid]
                        proc_info.duration = time.time() - proc_info.start_time.timestamp()
                        proc_info.cpu_percent = proc.info.get('cpu_percent', 0)
                        if proc.info.get('memory_info'):
                            proc_info.memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        proc_info.status = proc.info.get('status', 'running')
                        proc_info.name = name
                    else:
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
            
            for pid in list(self.processes.keys()):
                if pid not in current_pids:
                    proc_info = self.processes.pop(pid)
                    removed_processes.append(proc_info)
                    self.logger.info(f"Process ended: {proc_info.name} (PID: {pid})")
            
            if processes_found == 0 and platform.system() == 'Windows':
                self.logger.warning("No processes found with psutil, trying alternative method...")
                try:
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
        if not name:
            return False
        
        name_lower = name.lower()
        
        system_procs = []
        if platform.system() == 'Windows':
            system_procs = self.safe_processes.get('windows', [])
        elif platform.system() == 'Linux':
            system_procs = self.safe_processes.get('linux', [])
        elif platform.system() == 'Darwin':
            system_procs = self.safe_processes.get('macos', [])
        
        for p in system_procs:
            if name_lower == p.lower():
                return True
            if name_lower.endswith(p.lower()):
                return True
        
        system_patterns = ['system', 'nt authority', 'root', 'sys', 'daemon', 'service']
        try:
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
        if not self.threat_detection_enabled:
            return
        
        threats = []
        name_lower = proc_info.name.lower()
        cmdline_lower = proc_info.cmdline.lower()
        
        if proc_info.is_system_process:
            proc_info.last_scan = datetime.now()
            return
        
        for threat_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if pattern in name_lower or pattern in cmdline_lower:
                    severity = ThreatSeverity.HIGH
                    if threat_type in ['ransomware', 'cryptolocker']:
                        severity = ThreatSeverity.CRITICAL
                    elif threat_type == 'mining':
                        severity = ThreatSeverity.MEDIUM
                    
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
        
        for threat in threats:
            if threat not in proc_info.threats:
                proc_info.threats.append(threat)
        
        proc_info.last_scan = datetime.now()
    
    def _create_process_threat(self, severity: ThreatSeverity, category: ThreatCategory,
                              description: str, proc_info: ProcessInfo, threat_type: str) -> ThreatEvent:
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
        return list(self.processes.values())
    
    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        return self.processes.get(pid)
    
    def get_threat_processes(self) -> List[ProcessInfo]:
        return [p for p in self.processes.values() if p.threats]
    
    def get_statistics(self) -> Dict:
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
# AI THREAT DETECTION ENGINE - FIXED VERSION
# ============================================================

class AIThreatDetectionEngine:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.indicators = []
        self.logger = logging.getLogger('SOC_Lab.ThreatEngine')
        self.process_monitor = None
        
        self.safe_files = {
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
        
        self.safe_extensions = [
            '.dll', '.sys', '.cat', '.inf', '.mui', '.manifest', '.ini',
            '.conf', '.config', '.xml', '.xsd', '.xsl', '.dtd',
            '.ttf', '.otf', '.fon', '.pfm', '.pfb',
            '.hlp', '.chm', '.cnt', '.gid',
            '.nls', '.loc', '.prf', '.mpf',
            '.lnk', '.ps1', '.py', '.js', '.html', '.htm',
            '.css', '.json', '.yaml', '.yml', '.toml',
            '.md', '.txt', '.log', '.png', '.jpg', '.jpeg',
            '.gif', '.bmp', '.svg', '.mp3', '.mp4', '.avi',
            '.mov', '.wav', '.zip', '.tar', '.gz', '.rar',
            '.7z', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.ppt', '.pptx'
        ]
        
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
        
        self.workspace_dir = workspace_path.lower()
        self.logger.info("AI Threat Detection Engine initialized")
    
    def set_process_monitor(self, process_monitor: ProcessMonitor):
        self.process_monitor = process_monitor
    
    def analyze_file(self, filepath: str) -> List[ThreatEvent]:
        events = []
        
        if not os.path.exists(filepath):
            return events
        
        file_info = self._get_file_info(filepath)
        if not file_info:
            return events
        
        if self._is_safe_file(filepath, file_info):
            return events
        
        if self._is_in_safe_directory(filepath):
            return events
        
        if self._has_safe_extension(file_info['extension']):
            return events
        
        if self._is_safe_executable(file_info['name']):
            return events
        
        if self._is_workspace_file(filepath):
            return events
        
        if not self._is_in_user_directory(filepath):
            return events
        
        findings = self._analyze(filepath, file_info)
        if findings:
            event = self._create_threat_event(
                severity=ThreatSeverity.HIGH,
                category=ThreatCategory.SUSPICIOUS,
                description=f"⚠️ Suspicious file detected: {os.path.basename(filepath)}",
                source='file',
                source_detail=filepath,
                indicators=findings
            )
            events.append(event)
            self.logger.warning(f"THREAT DETECTED: {filepath}")
        
        return events
    
    def _is_safe_file(self, filepath: str, file_info: Dict) -> bool:
        name = file_info['name'].lower()
        
        if name in self.safe_files:
            return True
        
        if 'microsoft' in name or 'windows' in name:
            return True
        
        windows_patterns = ['api-ms-', 'ext-ms-', 'msvc', 'vcruntime', 'ucrtbase']
        for pattern in windows_patterns:
            if name.startswith(pattern):
                return True
        
        if 'ai_threat' in name.lower() or 'soc_' in name.lower():
            return True
        
        return False
    
    def _is_in_safe_directory(self, filepath: str) -> bool:
        filepath_lower = filepath.lower()
        
        for safe_dir in self.safe_directories:
            if safe_dir in filepath_lower:
                return True
        
        return False
    
    def _has_safe_extension(self, extension: str) -> bool:
        return extension in self.safe_extensions
    
    def _is_safe_executable(self, name: str) -> bool:
        return name.lower() in self.safe_executables
    
    def _is_workspace_file(self, filepath: str) -> bool:
        return self.workspace_dir in filepath.lower()
    
    def _is_in_user_directory(self, filepath: str) -> bool:
        filepath_lower = filepath.lower()
        
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
        indicators = []
        name = file_info['name'].lower()
        
        for category, patterns in self.threat_patterns.items():
            for pattern in patterns.get('patterns', []):
                if patterns.get('exact_match', False):
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
# FILE SYSTEM MONITOR
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
            print(f"❌ Failed to start monitoring: {e}")
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
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.reports_path = os.path.join(workspace_path, 'reports')
        os.makedirs(self.reports_path, exist_ok=True)
        self.logger = logging.getLogger('SOC_Lab.ReportGen')
        self.reports = []
        
    def generate_report(self, monitor: LabMonitor, ai_engine: AIThreatDetectionEngine,
                       report_format: str = 'pdf', lab_state: str = 'IDLE',
                       process_monitor: ProcessMonitor = None) -> str:
        
        timestamp = datetime.now()
        report_id = f"RPT-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        filename = f"lab_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.{report_format}"
        filepath = os.path.join(self.reports_path, filename)
        
        stats = monitor.get_statistics()
        threats = monitor.get_threats()
        process_stats = process_monitor.get_statistics() if process_monitor else {}
        processes = process_monitor.get_processes() if process_monitor else []
        
        if report_format == 'pdf':
            filepath = self._generate_pdf_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        elif report_format == 'html':
            filepath = self._generate_html_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        elif report_format == 'json':
            filepath = self._generate_json_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        else:
            filepath = self._generate_txt_report(filepath, report_id, stats, threats, lab_state, timestamp, process_stats, processes)
        
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
            
            story.append(Paragraph("SOC Automated Lab Report", title_style))
            story.append(Paragraph(f"Report ID: {report_id}", body_style))
            story.append(Paragraph(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
            story.append(Paragraph(f"System: {platform.node()}", body_style))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Paragraph(f"Lab State: {lab_state}", body_style))
            story.append(Paragraph(f"Total Alerts: {stats.get('total_alerts', 0)}", body_style))
            story.append(Paragraph(f"Active Threats: {stats.get('active_threats', 0)}", body_style))
            story.append(Paragraph(f"Files Scanned: {stats.get('files_scanned', 0)}", body_style))
            story.append(Paragraph(f"Total Processes: {process_stats.get('total_processes', 0)}", body_style))
            story.append(Paragraph(f"Processes with Threats: {process_stats.get('processes_with_threats', 0)}", body_style))
            story.append(Spacer(1, 20))
            
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
            
            story.append(Spacer(1, 30))
            story.append(Paragraph("─" * 80, footer_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"© 2024 {PLATFORM} | All Rights Reserved", footer_style))
            story.append(Paragraph(f"Generated by SOC Automated Lab {VERSION}", footer_style))
            story.append(Paragraph("This report is for EDUCATIONAL & AUTHORIZED SECURITY TESTING purposes only.", footer_style))
            
            doc.build(story, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)
            return filepath
            
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return self._generate_txt_report(filepath.replace('.pdf', '.txt'), report_id, stats, threats, lab_state, timestamp, process_stats, processes)
    
    def _generate_html_report(self, filepath: str, report_id: str, stats: Dict, threats: List, lab_state: str, timestamp: datetime, process_stats: Dict, processes: List) -> str:
        try:
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
            <h1>SOC Automated Lab Report</h1>
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
            <p>© 2024 {PLATFORM} | All Rights Reserved</p>
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
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filepath
            
        except Exception as e:
            self.logger.error(f"JSON generation failed: {e}")
            return None
    
    def _generate_txt_report(self, filepath: str, report_id: str, stats: Dict, threats: List, lab_state: str, timestamp: datetime, process_stats: Dict, processes: List) -> str:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
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
                    threat_status = "⚠️" if p.threats else "✅"
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
                f.write(f"© 2024 {PLATFORM} | All Rights Reserved\n")
                f.write("This report is for EDUCATIONAL & AUTHORIZED SECURITY TESTING purposes only.\n")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"TXT generation failed: {e}")
            return None
    
    def get_reports(self) -> List[LabReport]:
        return self.reports

# ============================================================
# TYPEWRITER CLASS
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
# SOC LAB DASHBOARD - FIXED UTF-8
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
        self.use_rich = RICH_AVAILABLE and self.console is not None
        
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
    
    def _get_centered_banner(self):
        if RICH_AVAILABLE and self.console:
            banner_text = f"""
[bold green]██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     
[bold green]██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     
[bold green]██║  ██║█████╗     ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     
[bold green]██║  ██║██╔══╝     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     
[bold green]██████╔╝███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
[bold green]╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝

[bold cyan]       SOC AUTOMATED LAB {VERSION}[/bold cyan]
[dim]────────────────────────────────────────────────────────────────────────────────[/dim]
[bold yellow]🛡️[/bold yellow] Security Operations Center - 24/7 Monitoring
[bold yellow]🛡️[/bold yellow] 24/7 Cyber risks rapid detection and observation
[bold yellow]📊[/bold yellow] Process & Application Monitoring
[bold yellow]📄[/bold yellow] Threat Hunting & Automated Reporting 
[bold red]⚡[/bold red] For Educational & Authorized Security Testing Purposes
"""
            return Panel(
                banner_text,
                title="[bold cyan]SOC AUTOMATED LAB[/bold cyan]",
                border_style="cyan",
                box=box.HEAVY,
                padding=(1, 2),
                width=80
            )
        else:
            # Fallback text banner
            return f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗
║         SOC AUTOMATED LAB {VERSION}                                  ║
║         Security Operations Center - 24/7 Monitoring                ║
║         For Educational & Authorized Security Testing Only           ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
"""
    
    def _show_centered_banner(self):
        if self.console and RICH_AVAILABLE:
            self.console.print(Align.center(self._get_centered_banner()))
            
            status = "─" * 78
            self.console.print(f"\n[dim]{status}[/dim]")
            self.console.print(
                Align.center(
                    f"[green]▶[/green] [dim]System:[/dim] [cyan]ACTIVE[/cyan] "
                    f"[green]│[/green] [dim]Mode:[/dim] [yellow]LAB MODE[/yellow] "
                    f"[green]│[/green] [dim]Version:[/dim] [cyan]{VERSION}[/cyan]"
                )
            )
            self.console.print(f"[dim]{status}[/dim]\n")
        else:
            print(self._get_centered_banner())
            print("─" * 78)
            print(f"▶ System: ACTIVE │ Mode: LAB MODE │ Version: {VERSION}")
            print("─" * 78)
            print()
    
    def _get_left_panel_content(self) -> str:
        status = self.lab.get_status()
        reports = self.lab.get_reports()
        process_stats = self.lab.get_process_stats()
        
        content = f"""
[{self.colors['info']}]┌── SESSION ──────────────────[/{self.colors['info']}]
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Time:[/dim] {datetime.now().strftime('%H:%M:%S')}
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Date:[/dim] {datetime.now().strftime('%Y-%m-%d')}
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Status:[/dim] {'🟢 RUNNING' if status.get('running') else '🔴 STOPPED'}
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Uptime:[/dim] {status.get('uptime_display', 'N/A')}
[{self.colors['info']}]└──────────────────────────────────[/{self.colors['info']}]

[{self.colors['accent']}]┌── STATS ────────────────────[/{self.colors['accent']}]
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Alerts:[/dim] {status.get('total_alerts', 0)}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Threats:[/dim] {status.get('active_threats', 0)}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Scanned:[/dim] {status.get('files_scanned', 0)}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Paths:[/dim] {status.get('monitored_paths', 0)}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Processes:[/dim] {process_stats.get('total_processes', 0)}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Threatened:[/dim] {process_stats.get('processes_with_threats', 0)}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Reports:[/dim] {len(reports)}
[{self.colors['accent']}]└──────────────────────────────────[/{self.colors['accent']}]
"""
        return content
    
    def _get_center_panel_content(self) -> str:
        content = f"""
[{self.colors['primary']}]╔══════════════════════════════════════╗
[{self.colors['primary']}]║               [{self.colors['info']}]📋 MAIN MENU[/{self.colors['info']}]                 ║
[{self.colors['primary']}]║──────────────────────────────────║
[{self.colors['primary']}]║  [{self.colors['accent']}]1.[/{self.colors['accent']}] [{self.colors['primary']}]🚀[/{self.colors['primary']}] Start Lab Monitoring     ║
[{self.colors['primary']}]║  [{self.colors['accent']}]2.[/{self.colors['accent']}] [{self.colors['danger']}]🛑[/{self.colors['danger']}] Stop Lab Monitoring      ║
[{self.colors['primary']}]║  [{self.colors['accent']}]3.[/{self.colors['accent']}] [{self.colors['info']}]📊[/{self.colors['info']}] Show Status             ║
[{self.colors['primary']}]║  [{self.colors['accent']}]4.[/{self.colors['accent']}] [{self.colors['warning']}]🔍[/{self.colors['warning']}] Run Threat Scan         ║
[{self.colors['primary']}]║  [{self.colors['accent']}]5.[/{self.colors['accent']}] [{self.colors['magenta']}]📄[/{self.colors['magenta']}] Generate Report         ║
[{self.colors['primary']}]║  [{self.colors['accent']}]6.[/{self.colors['accent']}] [{self.colors['danger']}]🚨[/{self.colors['danger']}] List Threats            ║
[{self.colors['primary']}]║  [{self.colors['accent']}]7.[/{self.colors['accent']}] [{self.colors['success']}]📊[/{self.colors['success']}] Show Results            ║
[{self.colors['primary']}]║  [{self.colors['accent']}]8.[/{self.colors['accent']}] [{self.colors['warning']}]📤[/{self.colors['warning']}] Export Data             ║
[{self.colors['primary']}]║──────────────────────────────────║
[{self.colors['primary']}]║  [{self.colors['accent']}]p.[/{self.colors['accent']}] [{self.colors['info']}]🔍[/{self.colors['info']}] View Running Processes  ║
[{self.colors['primary']}]║  [{self.colors['accent']}]e.[/{self.colors['accent']}] [{self.colors['info']}]🔧[/{self.colors['info']}] Enhanced Modules       ║
[{self.colors['primary']}]║  [{self.colors['accent']}]h.[/{self.colors['accent']}] [{self.colors['info']}]❓[/{self.colors['info']}] Help                     ║
[{self.colors['primary']}]║  [{self.colors['accent']}]q.[/{self.colors['accent']}] [{self.colors['danger']}]🚪[/{self.colors['danger']}] Exit                     ║
[{self.colors['primary']}]╚══════════════════════════════════════╝
"""
        return content
    
    def _get_right_panel_content(self) -> str:
        threats = self.lab.get_threats()
        reports = self.lab.get_reports()
        process_stats = self.lab.get_process_stats()
        processes = self.lab.get_processes()
        
        content = f"""
[{self.colors['info']}]┌── RECENT THREATS ────────────[/{self.colors['info']}]
"""
        if threats:
            for t in threats[:3]:
                severity = t.get('severity', 'INFO')
                color = 'red' if severity == 'CRITICAL' else 'yellow'
                content += f"[{self.colors['info']}]│[/{self.colors['info']}] [{color}]●[/{color}] {t.get('description', '')[:25]}...\n"
        else:
            content += f"[{self.colors['info']}]│[/{self.colors['info']}] [dim]No threats detected[/dim]\n"
        
        content += f"""
[{self.colors['info']}]└──────────────────────────────────[/{self.colors['info']}]

[{self.colors['primary']}]┌── PROCESSES ─────────────────[/{self.colors['primary']}]
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Running:[/dim] {process_stats.get('total_processes', 0)}
"""
        if processes:
            top_cpu = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:3]
            for p in top_cpu:
                threat_icon = "⚠️" if p.threats else "✅"
                content += f"[{self.colors['primary']}]│[/{self.colors['primary']}] {threat_icon} {p.name[:20]} ({p.cpu_percent:.1f}%)\n"
        
        content += f"""
[{self.colors['primary']}]└──────────────────────────────────[/{self.colors['primary']}]

[{self.colors['info']}]┌── REPORTS ────────────────────[/{self.colors['info']}]
[{self.colors['info']}]│[/{self.colors['info']}] [dim]Total:[/dim] {len(reports)}
"""
        if reports:
            latest = reports[-1]
            content += f"[{self.colors['info']}]│[/{self.colors['info']}] [dim]Latest:[/dim] {latest.format.upper()}\n"
            content += f"[{self.colors['info']}]│[/{self.colors['info']}] [dim]Size:[/dim] {latest.size // 1024} KB\n"
        
        content += f"""
[{self.colors['info']}]└──────────────────────────────────[/{self.colors['info']}]

[{self.colors['info']}]┌── NOTIFICATION ───────────────[/{self.colors['info']}]
[{self.colors['info']}]│[/{self.colors['info']}] [dim]{self.notification if self.notification else 'Ready'}[/dim]
[{self.colors['info']}]└──────────────────────────────────[/{self.colors['info']}]
"""
        return content
    
    def _run_rich_dashboard(self):
        while self.running:
            self._clear_screen()
            self._show_centered_banner()
            
            left_panel = Panel(
                self._get_left_panel_content(),
                title="[bold green]▪ SYSTEM INFO ▪[/bold green]",
                border_style="green",
                box=box.HEAVY,
                width=35
            )
            
            center_panel = Panel(
                self._get_center_panel_content(),
                title="[bold cyan]▪ MAIN MENU ▪[/bold cyan]",
                border_style="cyan",
                box=box.HEAVY,
                width=45
            )
            
            right_panel = Panel(
                self._get_right_panel_content(),
                title="[bold yellow]▪ STATUS ▪[/bold yellow]",
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
            
            status = "─" * 80
            self.console.print(f"\n[dim]{status}[/dim]")
            self.console.print(
                Align.center(
                    f"[green]▶[/green] [dim]Select option:[/dim] [yellow]1-8[/yellow] [dim]|[/dim] "
                    f"[yellow]p[/yellow] [dim]Processes[/dim] [dim]|[/dim] "
                    f"[yellow]e[/yellow] [dim]Enhanced[/dim] [dim]|[/dim] "
                    f"[yellow]h[/yellow] [dim]Help[/dim] [dim]|[/dim] [yellow]q[/yellow] [dim]Quit[/dim]"
                )
            )
            self.console.print(f"[dim]{status}[/dim]")
            
            if self.notification and (time.time() - self.notification_time < 5):
                self.console.print(f"\n[bold yellow]📌 {self.notification}[/bold yellow]")
            
            choice = Prompt.ask(
                "\n[bold cyan]┌── Select Option ──►[/bold cyan]",
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
    
    # ============================================================
    # COMMAND HANDLERS
    # ============================================================
    
    def _cmd_start(self):
        if self.lab.running:
            self._set_notification("⚠️ Lab is already running", "yellow")
            return
        
        self._set_notification("🔌 Starting lab monitoring...", "yellow")
        success = self.lab.start()
        if success:
            self._set_notification("✅ Lab started successfully!", "green")
        else:
            self._set_notification("❌ Failed to start lab", "red")
    
    def _cmd_stop(self):
        if not self.lab.running:
            self._set_notification("⚠️ Lab is not running", "yellow")
            return
        
        self._set_notification("🔌 Stopping lab...", "yellow")
        self.lab.stop()
        self._set_notification("✅ Lab stopped", "green")
    
    def _cmd_status(self):
        status = self.lab.get_status()
        reports = self.lab.get_reports()
        process_stats = self.lab.get_process_stats()
        self._clear_screen()
        self._show_centered_banner()
        
        status_text = f"""
{Colors.CYAN}┌── LAB STATUS ─────────────────────────────────────┐
│                                                          │
│  State:         {status.get('state', 'UNKNOWN')}                        │
│  Running:       {'✅ YES' if status.get('running') else '❌ NO'}                       │
│  Uptime:        {status.get('uptime_display', 'N/A')}                         │
│  Alerts:        {status.get('total_alerts', 0)}                         │
│  Threats:       {status.get('active_threats', 0)}                         │
│  Files Scanned: {status.get('files_scanned', 0)}                         │
│  Monitored:     {status.get('monitored_paths', 0)} paths                   │
│  Processes:     {process_stats.get('total_processes', 0)}                         │
│  Threatened:    {process_stats.get('processes_with_threats', 0)}                         │
│  Reports:       {len(reports)}                         │
└──────────────────────────────────────────────────────────┘{Colors.END}
"""
        print(status_text)
        input("\nPress Enter to continue...")
    
    def _cmd_scan(self):
        if not self.lab.running:
            self._set_notification("❌ Lab is not running. Start it first.", "red")
            return
        
        self._set_notification("🔍 Running system-wide threat scan...", "yellow")
        self._clear_screen()
        
        term_width = self._get_terminal_width()
        
        header = "┌" + "─" * (term_width - 2) + "┐"
        title_padded = "│" + "🔍 SYSTEM-WIDE THREAT SCAN IN PROGRESS".center(term_width - 2) + "│"
        footer = "└" + "─" * (term_width - 2) + "┘"
        
        print(header)
        print(title_padded)
        print(footer)
        print("")
        print("📁 Scanning System Locations".center(term_width))
        print("─" * term_width)
        print("🔍 Scanning in progress...".center(term_width))
        print("")
        
        scan_result = []
        scan_complete = False
        
        def run_scan():
            nonlocal scan_result, scan_complete
            scan_result = self.lab.run_system_scan()
            scan_complete = True
        
        scan_thread = threading.Thread(target=run_scan)
        scan_thread.start()
        
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        spinner_idx = 0
        
        while not scan_complete:
            spinner = spinner_chars[spinner_idx % len(spinner_chars)]
            status_msg = f"{spinner} Scanning files... Please wait"
            print(f"\r{status_msg.center(term_width)}", end="", flush=True)
            spinner_idx += 1
            time.sleep(0.1)
        
        print("\r" + " " * term_width, end="")
        print("\r✅ Scan complete!".center(term_width))
        print("")
        
        results = scan_result
        
        print("")
        print("┌" + "─" * (term_width - 2) + "┐")
        title_result = "│" + "📊 SCAN RESULTS".center(term_width - 2) + "│"
        print(title_result)
        print("└" + "─" * (term_width - 2) + "┘")
        print("")
        
        if results:
            critical = [r for r in results if r.get('severity') == 'CRITICAL']
            high = [r for r in results if r.get('severity') == 'HIGH']
            medium = [r for r in results if r.get('severity') == 'MEDIUM']
            low = [r for r in results if r.get('severity') == 'LOW']
            
            print(f"🚨 Found {len(results)} threats".center(term_width))
            print("─" * term_width)
            
            severity_lines = []
            if critical:
                severity_lines.append(f"🔴 CRITICAL: {len(critical)}")
            if high:
                severity_lines.append(f"🟡 HIGH: {len(high)}")
            if medium:
                severity_lines.append(f"🔵 MEDIUM: {len(medium)}")
            if low:
                severity_lines.append(f"🟢 LOW: {len(low)}")
            
            for line in severity_lines:
                print(line.center(term_width))
            print("")
            
            for i, r in enumerate(results[:10], 1):
                threat_line = f"   {i}. {r.get('severity', 'UNKNOWN')} - {r.get('description', '')[:50]}"
                print(threat_line.center(term_width))
                if r.get('source'):
                    source_line = f"      📁 {r.get('source', '')[:50]}"
                    print(source_line.center(term_width))
                print("")
            
            if len(results) > 10:
                print(f"   ... and {len(results) - 10} more threats".center(term_width))
        else:
            print("✅ No threats detected - System is clean!".center(term_width))
        
        print("")
        print("─" * term_width)
        
        self._set_notification(f"✅ Scan complete. Found {len(results)} threats", "green")
        print("\nPress Enter to continue...".center(term_width))
        input()
    
    def _cmd_report(self):
        if not self.lab.running:
            self._set_notification("❌ Lab is not running", "red")
            return
        
        if self.use_rich and self.console:
            format_choice = Prompt.ask(
                "[bold cyan]┌── Report Format ──►[/bold cyan]",
                choices=["pdf", "html", "json", "txt"],
                default="pdf"
            )
        else:
            print("\n┌── Report Format ──►")
            print("  [pdf] [html] [json] [txt]")
            format_choice = input("Select format (default: pdf): ").strip().lower()
            if not format_choice or format_choice not in ["pdf", "html", "json", "txt"]:
                format_choice = "pdf"
        
        self._set_notification(f"📄 Generating {format_choice} report...", "yellow")
        result = self.lab.generate_report(format_choice)
        
        if result:
            print(f"✅ Report generated: {result}")
            reports = self.lab.get_reports()
            if reports:
                latest = reports[-1]
                print(f"📊 Size: {latest.size // 1024} KB")
                print(f"🔖 ID: {latest.report_id}")
            self._set_notification(f"✅ Report generated: {result}", "green")
        else:
            print("❌ Failed to generate report")
            self._set_notification("❌ Failed to generate report", "red")
        
        input("\nPress Enter to continue...")
    
    def _cmd_threats(self):
        threats = self.lab.get_threats()
        self._clear_screen()
        self._show_centered_banner()
        
        if not threats:
            print(f"\n✅ No threats detected")
        else:
            print(f"\n🚨 DETECTED THREATS ({len(threats)})")
            print("─" * 80)
            
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
            print(f"\nℹ️ No results yet")
        else:
            print(f"\n📊 LAB RESULTS")
            print("─" * 80)
            
            for r in results[-5:]:
                print(f"\n🔬 {r.get('name', 'Unknown')}")
                print(f"   ID: {r.get('experiment_id', 'N/A')}")
                print(f"   Status: {r.get('status', 'N/A')}")
                print(f"   Duration: {r.get('duration', 0):.2f}s")
                print(f"   Findings: {len(r.get('findings', []))}")
        
        input(f"\nPress Enter to continue...")
    
    def _cmd_export(self):
        if not self.lab.running:
            self._set_notification("❌ Lab is not running", "red")
            return
        
        if self.use_rich and self.console:
            export_type = Prompt.ask(
                "[bold cyan]┌── Export Type ──►[/bold cyan]",
                choices=["json", "csv", "all"],
                default="json"
            )
        else:
            print("\n┌── Export Type ──►")
            print("  [1] JSON  [2] CSV  [3] All")
            choice = input("Select format (1-3, default: 1): ").strip()
            format_map = {'1': 'json', '2': 'csv', '3': 'all'}
            export_type = format_map.get(choice, 'json')
        
        self._set_notification(f"📤 Exporting {export_type} data...", "yellow")
        result = self.lab.export_data(export_type)
        if result:
            print(f"✅ Exported: {result}")
            self._set_notification(f"✅ Exported: {result}", "green")
        else:
            print("❌ Failed to export")
            self._set_notification("❌ Failed to export", "red")
        
        input("\nPress Enter to continue...")
    
    def _cmd_processes(self):
        self._clear_screen()
        self._show_centered_banner()
        
        processes = self.lab.get_processes()
        process_stats = self.lab.get_process_stats()
        
        print(f"{Colors.CYAN}┌── RUNNING PROCESSES ─────────────────────────────────┐")
        print(f"│  🔍 Process Monitoring Status                                 │")
        print(f"└──────────────────────────────────────────────────────────┘{Colors.END}")
        print("")
        
        if not PSUTIL_AVAILABLE:
            print("⚠️ psutil is not installed. Process monitoring is disabled.")
            print("   Install with: pip install psutil")
            print("")
            print("─" * 80)
            input("\nPress Enter to continue...")
            return
        
        print(f"📊 Total: {process_stats.get('total_processes', 0)} processes")
        print(f"   System: {process_stats.get('system_processes', 0)} | User: {process_stats.get('user_processes', 0)}")
        
        if process_stats.get('processes_with_threats', 0) > 0:
            print(f"   ⚠️ Threatened: {process_stats.get('processes_with_threats', 0)}")
        else:
            print(f"   ✅ Threatened: {process_stats.get('processes_with_threats', 0)}")
        
        print(f"   Monitoring: {'✅ Active' if process_stats.get('is_monitoring', False) else '❌ Inactive'}")
        print("")
        
        if processes:
            sorted_procs = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)
            print("┌─────┬──────────────────────────────┬──────────┬─────────┬──────────┬──────────┐")
            print("│ PID │ Name                         │ Duration │ CPU %   │ Memory   │ Threats │")
            print("├─────┼──────────────────────────────┼──────────┼─────────┼──────────┼──────────┤")
            
            for p in sorted_procs[:20]:
                duration = f"{int(p.duration // 60)}m {int(p.duration % 60)}s"
                threat_icon = "⚠️" if p.threats else " "
                print(f"│ {str(p.pid):<4} │ {p.name[:30]:<30} │ {duration:>8} │ {p.cpu_percent:>6.1f}% │ {p.memory_mb:>7.1f}MB │ {threat_icon}{len(p.threats):>2}  │")
            
            if len(processes) > 20:
                print(f"├─────┴──────────────────────────────┴──────────┴─────────┴──────────┴──────────┤")
                print(f"│ ... and {len(processes) - 20} more processes                                      │")
            
            print("└─────┴──────────────────────────────┴──────────┴─────────┴──────────┴──────────┘")
        else:
            print("   No processes detected")
            print("")
            print("   Possible reasons:")
            print("   2. Process monitoring is not running")
            print("   3. Permission issues on your system")
            print("   4. The lab is not fully started")
        
        print("")
        print("─" * 80)
        input("\nPress Enter to continue...")
    
    def _cmd_enhanced(self):
        self._clear_screen()
        self._show_centered_banner()
        print("\n🔧 ENHANCED MODULES")
        print("─" * 80)
        print("Enhanced modules are available through the main menu.")
        print("Use the main menu options to access enhanced features.")
        input("\nPress Enter to continue...")
    
    def _show_help(self):
        self._clear_screen()
        self._show_centered_banner()
        
        help_text = f"""
{Colors.CYAN}┌── AVAILABLE COMMANDS ────────────────────────────────────┐
│                                                          │
│  1. Start Lab Monitoring     - Begin 24/7 monitoring    │
│  2. Stop Lab Monitoring      - Stop monitoring          │
│  3. Show Status             - Display current status    │
│  4. Run Threat Scan          - Scan for threats         │
│  5. Generate Report          - Create report            │
│  6. List Threats             - Show detected threats    │
│  7. Show Results             - Show lab results         │
│  8. Export Data              - Export findings          │
│  p. View Processes           - Show running processes   │
│  e. Enhanced Modules         - Enhanced features        │
│  h. Help                    - Show this help           │
│  q. Exit                    - Exit dashboard           │
└──────────────────────────────────────────────────────────┘{Colors.END}
"""
        print(help_text)
        input(f"\nPress Enter to continue...")
    
    def _cmd_start(self):
        if self.lab.running:
            self._set_notification("⚠️ Lab is already running", "yellow")
            return
        
        self._set_notification("🔌 Starting lab monitoring...", "yellow")
        success = self.lab.start()
        if success:
            self._set_notification("✅ Lab started successfully!", "green")
        else:
            self._set_notification("❌ Failed to start lab", "red")
    
    def _cmd_stop(self):
        if not self.lab.running:
            self._set_notification("⚠️ Lab is not running", "yellow")
            return
        
        self._set_notification("🔌 Stopping lab...", "yellow")
        self.lab.stop()
        self._set_notification("✅ Lab stopped", "green")
    
    def _set_notification(self, message: str, color: str = "white"):
        self.notification = message
        self.notification_time = time.time()
    
    def _exit_dashboard(self):
        self._set_notification("👋 Exiting dashboard...", "yellow")
        time.sleep(1)
        self.running = False
        if self.lab.running:
            self.lab.stop()
    
    def _run_simple_dashboard(self):
        while self.running:
            self._clear_screen()
            self._show_centered_banner()
            print("\n[1] Start Lab  [2] Stop Lab  [3] Status  [4] Scan")
            print("[5] Report  [6] Threats  [7] Results  [8] Export")
            print("[p] Processes  [e] Enhanced  [h] Help  [q] Exit\n")
            
            if self.notification and (time.time() - self.notification_time < 5):
                print(f"📌 {self.notification}\n")
            
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
        
        try:
            self.enhanced = EnhancedModulesManager(workspace_path)
            self.enhanced.start()
        except:
            self.enhanced = None
        
        self.ai_engine.set_process_monitor(self.process_monitor)
        
        self._setup_logging()
        self._load_config()
        
        self.dashboard = SOCLabDashboard(self)
        
        atexit.register(self.cleanup)
    
    def run_system_scan(self) -> List[Dict]:
        scan_paths = self._get_system_scan_paths()
        findings = []
        total_scanned = 0
        max_files_per_dir = 200
        
        for path in scan_paths:
            if os.path.exists(path):
                print(f"\r   📁 Scanning: {path[:50]}...".ljust(80), end="", flush=True)
                try:
                    for root, dirs, files in os.walk(path):
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
                                
                                if total_scanned % 50 == 0:
                                    print(f"\r   📁 Scanning: {path[:40]}... | Files: {total_scanned}".ljust(80), end="", flush=True)
                                    
                            except (PermissionError, OSError):
                                continue
                            except Exception as e:
                                self.logger.debug(f"Scan error: {e}")
                                continue
                except Exception as e:
                    self.logger.debug(f"Error scanning {path}: {e}")
                    continue
        
        print("\r" + " " * 80, end="")
        print(f"\r   ✅ Scan complete! Files scanned: {total_scanned}".ljust(80))
        
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
        paths = []
        
        if platform.system() == 'Windows':
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    if letter in ['C', 'D', 'E', 'F']:
                        paths.append(drive)
            
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
            
        elif platform.system() == 'Darwin':
            paths.extend(['/', '/Users', '/Applications', '/Library', '/usr', '/var'])
        
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
            'auto_report_interval': 3600,
            'process_monitoring_enabled': True,
            'process_scan_interval': 10,
        }
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
    
    def start(self) -> bool:
        if self.running:
            return True
        
        self.state = LabStatus.INITIALIZING
        monitor_paths = self.config.get('monitor_paths', [])
        
        if platform.system() == 'Windows':
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    monitor_paths.append(drive)
        else:
            monitor_paths.extend(['/', '/home', '/usr', '/var'])
        
        monitor_paths = list(set([p for p in monitor_paths if os.path.exists(p)]))
        
        print(f"📁 Starting monitoring on {len(monitor_paths)} paths...")
        
        fs_success = self.monitor.start_monitoring(monitor_paths)
        
        process_success = True
        if self.config.get('process_monitoring_enabled', True):
            print("🔌 Starting process monitoring...")
            process_success = self.process_monitor.start_monitoring()
            if process_success:
                self.logger.info("Process monitoring started")
            else:
                self.logger.warning("Process monitoring failed to start")
                print("⚠️ Process monitoring failed. Check if psutil is installed.")
        
        if fs_success:
            self.running = True
            self.start_time = datetime.now()
            self.state = LabStatus.RUNNING
            self.logger.info("Lab started")
            
            self._start_auto_reporting()
            
            return True
        else:
            self.state = LabStatus.ERROR
            print("❌ Failed to start lab")
            return False
        

    def stop(self):
        if not self.running:
            return
        
        if self._report_scheduler:
            self._report_scheduler = None
        
        self.process_monitor.monitoring = False
        
        self.monitor.stop_monitoring()
        
        self.generate_report('pdf')
        
        self.running = False
        self.state = LabStatus.STOPPED
        self.logger.info("Lab stopped")
    
    def _start_auto_reporting(self):
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
        print("🔍 Scanning...")
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
        return self.report_generator.get_reports()
    
    def get_processes(self) -> List[ProcessInfo]:
        return self.process_monitor.get_processes()
    
    def get_process_stats(self) -> Dict:
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
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif export_type == 'csv':
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
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

    def generate_enhanced_report(self) -> str:
        if self.enhanced:
            threats = self.monitor.get_threats()
            stats = self.monitor.get_statistics()
            process_stats = self.process_monitor.get_statistics()
            return self.enhanced.generate_full_report(threats, stats, process_stats)
        return "Enhanced modules not available"

    def add_ioc(self, ioc_type: str, value: str, category: str = 'malicious'):
        if self.enhanced:
            return self.enhanced.add_ioc(ioc_type, value, category)
        return False

    def get_enhanced_status(self) -> Dict:
        if self.enhanced:
            return self.enhanced.get_status()
        return {'running': False, 'error': 'Enhanced modules not available'}

# ============================================================
# MAIN ENTRY POINT
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
        lab.dashboard.start_dashboard()

if __name__ == "__main__":
    main()