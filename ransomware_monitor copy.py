#!/usr/bin/env python3
"""
Ransomware Detection & Monitoring System
Version: 3.1.113
Author: Spark Wilson Spink
Description: Real-time ransomware detection with interactive dashboard
"""

import os
import sys
import time
import threading
import platform
import psutil
import hashlib
import json
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# Try to import rich for beautiful dashboard
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.align import Align
    from rich import box
    from rich.text import Text
    from rich.style import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Colorama fallback
try:
    from colorama import Fore, Style, init
    init()
except ImportError:
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    class Style:
        RESET_ALL = '\033[0m'


class ThreatLevel(Enum):
    """Threat level enumeration"""
    NORMAL = ("NORMAL", Fore.GREEN)
    LOW = ("LOW", Fore.GREEN)
    MEDIUM = ("MEDIUM", Fore.YELLOW)
    HIGH = ("HIGH", Fore.RED)
    CRITICAL = ("CRITICAL", Fore.RED)
    
    def __init__(self, label, color):
        self.label = label
        self.color = color
    
    def __str__(self):
        return f"{self.color}{self.label}{Style.RESET_ALL}"


@dataclass
class FileEvent:
    """File system event data"""
    timestamp: str
    event_type: str
    path: str
    size: int = 0
    extension: str = ""
    is_suspicious: bool = False


@dataclass
class SuspiciousProcess:
    """Suspicious process data"""
    pid: int
    name: str
    cmdline: str
    cpu: float
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RansomwareMonitor:
    """
    Real-time ransomware detection and monitoring system.
    Monitors file system activity, processes, and behavioral patterns.
    """
    
    def __init__(self, session_id=None, log_callback=None, use_rich=True):
        self.session_id = session_id or f"RANSOM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.log_callback = log_callback
        self.use_rich = use_rich and RICH_AVAILABLE
        self.console = Console() if self.use_rich else None
        
        # State
        self.is_running = False
        self.ransomware_detected = False
        self.threat_level = ThreatLevel.NORMAL
        self.alert_callbacks = []
        
        # File monitoring
        self.monitored_dirs = self._get_monitored_dirs()
        self.watched_extensions = self._get_watched_extensions()
        
        # Ransomware indicators
        self.suspicious_extensions = self._get_suspicious_extensions()
        self.suspicious_names = self._get_suspicious_names()
        self.ransomware_processes = self._get_ransomware_processes()
        
        # Data storage
        self.process_history: deque = deque(maxlen=1000)
        self.file_activity_log: deque = deque(maxlen=5000)
        self.suspicious_events: List[FileEvent] = []
        self.detected_processes: List[SuspiciousProcess] = []
        
        # Detection thresholds
        self.FILE_CREATION_RATE_THRESHOLD = 50
        self.RENAME_RATE_THRESHOLD = 30
        self.DELETE_RATE_THRESHOLD = 20
        self.SUSPICIOUS_PROCESS_THRESHOLD = 3
        
        # Statistics
        self.stats = {
            'files_created': 0,
            'files_modified': 0,
            'files_deleted': 0,
            'files_renamed': 0,
            'suspicious_processes': 0,
            'alerts_triggered': 0,
            'last_scan': None,
            'start_time': datetime.now(),
            'total_scans': 0,
            'threats_blocked': 0
        }
        
        # Threading
        self.monitor_thread = None
        self.observer = None
        self._stop_event = threading.Event()
        
        # Initialize
        self._log_message("Ransomware Monitor initialized", "INFO")

    def _get_monitored_dirs(self) -> List[Path]:
        """Get directories to monitor based on OS"""
        home = Path.home()
        if platform.system() == 'Windows':
            return [
                home / 'Documents',
                home / 'Desktop',
                home / 'Downloads',
                home / 'Pictures',
                home / 'Music',
                home / 'Videos',
                home / 'AppData' / 'Local' / 'Temp',
                Path(os.environ.get('TEMP', 'C:\\Temp'))
            ]
        else:
            return [
                home / 'Documents',
                home / 'Desktop',
                home / 'Downloads',
                Path('/tmp'),
                Path('/var/tmp'),
                home / '.local' / 'share'
            ]

    def _get_watched_extensions(self) -> Set[str]:
        """Get file extensions to watch"""
        return {
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.txt', '.rtf', '.odt', '.ods', '.odp',
            '.md', '.tex', '.log',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
            '.mp3', '.mp4', '.avi', '.mkv', '.wav', '.flac',
            '.psd', '.ai', '.eps', '.svg',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            '.xz', '.iso', '.dmg',
            '.exe', '.dll', '.sys', '.bin', '.msi',
            '.app', '.deb', '.rpm',
            '.db', '.sql', '.mdb', '.accdb', '.sqlite',
            '.sqlite3', '.db3',
            '.py', '.java', '.c', '.cpp', '.cs', '.rb',
            '.php', '.asp', '.aspx', '.jsp', '.html', '.css', '.js',
            '.json', '.xml', '.yaml', '.yml', '.conf', '.cfg', '.ini',
            '.sh', '.bat', '.ps1', '.vbs'
        }

    def _get_suspicious_extensions(self) -> Set[str]:
        """Get suspicious file extensions (ransomware indicators)"""
        return {
            '.encrypted', '.enc', '.crypt', '.locked', '.ransom',
            '.worm', '.virus', '.infected', '.crypto', '.crypter',
            '.lol', '.bad', '.hacked', '.breached', '.compromised',
            '.locked', '.encrypt', '.decrypt', '.pay', '.pay2',
            '.key', '.key2', '.key3', '.decryptor', '.cryptor'
        }

    def _get_suspicious_names(self) -> Set[str]:
        """Get suspicious file names (ransom notes)"""
        return {
            'readme.txt', 'howtodecrypt.txt', 'decrypt.txt',
            'payment.txt', 'ransom.txt', 'help.txt',
            '!readme.txt', '!!!readme.txt', 'read_me.txt',
            'recover.txt', 'restore.txt', 'key.txt',
            'recover_files.txt', 'howto.txt', '!!readme!!.txt',
            'decrypt_instructions.txt', 'pay.txt', 'bitcoin.txt'
        }

    def _get_ransomware_processes(self) -> Set[str]:
        """Get known ransomware process names"""
        return {
            'wannacry', 'petya', 'notpetya', 'badrabbit',
            'ryuk', 'conti', 'revil', 'lockbit', 'blackmatter',
            'clop', 'darkangelo', 'darkside', 'doppelpaymer',
            'egregor', 'gandcrab', 'mespinoza', 'netwalker',
            'phobos', 'sodinokibi', 'sunrise', 'thunder',
            'cryptolocker', 'cryptowall', 'torrentlocker',
            'dirtydecrypt', 'jigsaw', 'keRanger', 'leChiffre',
            'mamba', 'nmore', 'omega', 'paris', 'qwerty',
            'satan', 'tease', 'unlock92', 'vip', 'wizard'
        }

    def _log_message(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.log_callback:
            self.log_callback(f"[{timestamp}] [RANSOM] {message}", level)
        else:
            if self.use_rich and self.console:
                colors = {
                    "INFO": "cyan",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "SUCCESS": "green",
                    "DEBUG": "blue"
                }
                color = colors.get(level, "white")
                self.console.print(f"[{timestamp}] [bold {color}][RANSOM][/{color}] {message}")
            else:
                print(f"{Fore.CYAN}[{timestamp}] [RANSOM] {message}{Style.RESET_ALL}")

    def start_monitoring(self) -> bool:
        """Start real-time ransomware monitoring"""
        if self.is_running:
            self._log_message("Ransomware monitor already running", "WARNING")
            return False
        
        self._log_message("Starting Ransomware Monitoring System...", "INFO")
        self._log_message("Monitoring directories:", "INFO")
        for dir_path in self.monitored_dirs:
            if dir_path.exists():
                self._log_message(f"   - {dir_path}", "INFO")
            else:
                self._log_message(f"   - {dir_path} (not found)", "WARNING")
        
        self.is_running = True
        self._stop_event.clear()
        self.stats['start_time'] = datetime.now()
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        if WATCHDOG_AVAILABLE:
            self._start_watchdog()
        else:
            self._log_message("Watchdog not available - using polling mode", "WARNING")
        
        self._log_message("Ransomware monitoring active", "SUCCESS")
        return True

    def _start_watchdog(self):
        """Start watchdog file system observer"""
        try:
            class RansomwareFileHandler(FileSystemEventHandler):
                def __init__(self, monitor):
                    self.monitor = monitor
                
                def on_created(self, event):
                    if not event.is_directory:
                        self.monitor._handle_file_event('created', event.src_path)
                
                def on_modified(self, event):
                    if not event.is_directory:
                        self.monitor._handle_file_event('modified', event.src_path)
                
                def on_deleted(self, event):
                    if not event.is_directory:
                        self.monitor._handle_file_event('deleted', event.src_path)
                
                def on_moved(self, event):
                    if not event.is_directory:
                        self.monitor._handle_file_event('moved', event.src_path, event.dest_path)
            
            self.observer = Observer()
            for dir_path in self.monitored_dirs:
                if dir_path.exists():
                    self.observer.schedule(RansomwareFileHandler(self), str(dir_path), recursive=True)
            self.observer.start()
            self._log_message("File system watcher active", "SUCCESS")
        except Exception as e:
            self._log_message(f"Failed to start watchdog: {str(e)}", "WARNING")

    def _handle_file_event(self, event_type: str, path: str, dest_path: str = None):
        """Handle file system events"""
        try:
            file_path = Path(path)
            
            if file_path.suffix.lower() not in self.watched_extensions:
                return
            
            event = FileEvent(
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                path=str(file_path),
                size=file_path.stat().st_size if file_path.exists() else 0,
                extension=file_path.suffix.lower()
            )
            
            self._check_for_ransomware_patterns(event)
            self.file_activity_log.append(event)
            
            if event_type == 'created':
                self.stats['files_created'] += 1
            elif event_type == 'modified':
                self.stats['files_modified'] += 1
            elif event_type == 'deleted':
                self.stats['files_deleted'] += 1
            elif event_type == 'moved':
                self.stats['files_renamed'] += 1
            
        except Exception as e:
            pass

    def _monitor_loop(self):
        """Main monitoring loop"""
        last_stats_check = datetime.now()
        
        while not self._stop_event.is_set():
            try:
                self._check_processes()
                
                if (datetime.now() - last_stats_check).seconds >= 10:
                    self._check_file_rates()
                    self._update_threat_level()
                    last_stats_check = datetime.now()
                
                time.sleep(2)
                
            except Exception as e:
                self._log_message(f"Monitoring error: {str(e)}", "ERROR")

    def _check_processes(self):
        """Check running processes for ransomware indicators"""
        suspicious = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                    
                    if any(ransom in proc_name for ransom in self.ransomware_processes):
                        suspicious.append(SuspiciousProcess(
                            pid=proc_info['pid'],
                            name=proc_info['name'],
                            cmdline=' '.join(proc_info['cmdline']) if proc_info['cmdline'] else '',
                            cpu=proc_info['cpu_percent'] or 0
                        ))
                    
                    if proc_info['cmdline']:
                        cmdline = ' '.join(proc_info['cmdline']).lower()
                        suspicious_patterns = ['--encrypt', '--ransom', 'decrypt', 'bitcoin', 'monero']
                        if any(pattern in cmdline for pattern in suspicious_patterns):
                            if not any(ransom in proc_name for ransom in self.ransomware_processes):
                                suspicious.append(SuspiciousProcess(
                                    pid=proc_info['pid'],
                                    name=proc_info['name'],
                                    cmdline=cmdline[:100],
                                    cpu=proc_info['cpu_percent'] or 0
                                ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            if suspicious:
                self.stats['suspicious_processes'] += len(suspicious)
                self.detected_processes.extend(suspicious)
                
                self._trigger_alert('suspicious_process', {
                    'count': len(suspicious),
                    'processes': [{'pid': p.pid, 'name': p.name} for p in suspicious]
                })
                
                self._log_message(f"Detected {len(suspicious)} suspicious processes", "WARNING")
                for proc in suspicious[:5]:
                    self._log_message(f"   - {proc.name} (PID: {proc.pid})", "WARNING")
                
                if len(suspicious) >= self.SUSPICIOUS_PROCESS_THRESHOLD:
                    self.ransomware_detected = True
                    self.threat_level = ThreatLevel.CRITICAL
                    self._trigger_alert('ransomware_confirmed', {
                        'processes': [{'pid': p.pid, 'name': p.name} for p in suspicious],
                        'confidence': 'HIGH'
                    })
                    
        except Exception as e:
            pass

    def _check_file_rates(self):
        """Check for abnormal file operation rates"""
        now = datetime.now()
        timeframe = 60
        
        recent_events = [e for e in self.file_activity_log 
                        if (datetime.fromisoformat(e.timestamp) - now).seconds <= timeframe]
        
        created = len([e for e in recent_events if e.event_type == 'created'])
        deleted = len([e for e in recent_events if e.event_type == 'deleted'])
        
        if created > self.FILE_CREATION_RATE_THRESHOLD:
            self._trigger_alert('high_file_creation', {'rate': created})
            self._log_message(f"High file creation: {created} files in {timeframe}s", "WARNING")
            if self.threat_level.value[0] != "CRITICAL":
                self.threat_level = ThreatLevel.HIGH
        
        if deleted > self.DELETE_RATE_THRESHOLD:
            self._trigger_alert('high_file_deletion', {'rate': deleted})
            self._log_message(f"High file deletion: {deleted} files in {timeframe}s", "WARNING")
            if self.threat_level.value[0] != "CRITICAL":
                self.threat_level = ThreatLevel.HIGH

    def _check_for_ransomware_patterns(self, event: FileEvent):
        """Check for ransomware patterns in file events"""
        file_path = Path(event.path)
        file_name = file_path.name.lower()
        
        if file_path.suffix.lower() in self.suspicious_extensions:
            event.is_suspicious = True
            self.suspicious_events.append(event)
            self._trigger_alert('suspicious_extension', {
                'path': event.path,
                'extension': file_path.suffix
            })
            self._log_message(f"Suspicious extension: {file_path.name}", "ERROR")
            self.ransomware_detected = True
            self.threat_level = ThreatLevel.CRITICAL
        
        if file_name in self.suspicious_names:
            event.is_suspicious = True
            self.suspicious_events.append(event)
            self._trigger_alert('suspicious_filename', {
                'path': event.path,
                'name': file_name
            })
            self._log_message(f"Suspicious file: {file_path.name}", "WARNING")
            self.ransomware_detected = True
            if self.threat_level.value[0] != "CRITICAL":
                self.threat_level = ThreatLevel.HIGH
        
        if any(keyword in file_name for keyword in ['decrypt', 'ransom', 'readme', 'howtodecrypt']):
            if any(ext in file_name for ext in ['.txt', '.html', '.hta', '.lnk']):
                event.is_suspicious = True
                self.suspicious_events.append(event)
                self._trigger_alert('ransom_note', {
                    'path': event.path,
                    'name': file_name
                })
                self._log_message(f"Ransom note: {file_path.name}", "ERROR")

    def _update_threat_level(self):
        """Update threat level based on recent activity"""
        if self.ransomware_detected:
            self.threat_level = ThreatLevel.CRITICAL
            return
        
        now = datetime.now()
        recent_suspicious = len([e for e in self.suspicious_events 
                               if (now - datetime.fromisoformat(e.timestamp)).seconds <= 300])
        
        if recent_suspicious > 5:
            self.threat_level = ThreatLevel.HIGH
        elif recent_suspicious > 2:
            self.threat_level = ThreatLevel.MEDIUM
        elif recent_suspicious > 0:
            self.threat_level = ThreatLevel.LOW
        else:
            self.threat_level = ThreatLevel.NORMAL

    def _trigger_alert(self, alert_type: str, data: dict):
        """Trigger alert for ransomware detection"""
        self.stats['alerts_triggered'] += 1
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'data': data,
            'threat_level': self.threat_level.value[0]
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception:
                pass

    def register_alert_callback(self, callback):
        """Register alert callback function"""
        if callable(callback):
            self.alert_callbacks.append(callback)

    def stop_monitoring(self) -> bool:
        """Stop ransomware monitoring"""
        if not self.is_running:
            self._log_message("Monitor not running", "WARNING")
            return False
        
        self._stop_event.set()
        self.is_running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2)
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        self._log_message("Ransomware monitoring stopped", "INFO")
        return True

    def get_status(self) -> dict:
        """Get current monitoring status"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'running': self.is_running,
            'ransomware_detected': self.ransomware_detected,
            'threat_level': self.threat_level.value[0],
            'threat_color': self.threat_level.value[1],
            'uptime': str(uptime).split('.')[0],
            'stats': self.stats,
            'suspicious_events': len(self.suspicious_events),
            'suspicious_processes': len(self.detected_processes),
            'monitored_dirs': len([d for d in self.monitored_dirs if d.exists()]),
            'total_alerts': self.stats['alerts_triggered']
        }

    def get_events(self, limit: int = 100) -> List[FileEvent]:
        """Get recent file events"""
        return list(self.file_activity_log)[-limit:]

    def get_suspicious_events(self, limit: int = 50) -> List[FileEvent]:
        """Get suspicious events"""
        return self.suspicious_events[-limit:]

    def scan_for_ransomware(self, path: str = None) -> List[dict]:
        """Manual scan for ransomware indicators"""
        self._log_message("Starting manual ransomware scan...", "INFO")
        self.stats['total_scans'] += 1
        
        if path is None:
            scan_paths = self.monitored_dirs
        else:
            scan_paths = [Path(path)]
        
        found = []
        
        for scan_path in scan_paths:
            if not scan_path.exists():
                self._log_message(f"Path not found: {scan_path}", "WARNING")
                continue
            
            self._log_message(f"Scanning: {scan_path}", "INFO")
            
            try:
                for root, dirs, files in os.walk(str(scan_path)):
                    if any(skip in root for skip in ['Windows', 'System32', '$Recycle', 'AppData', 'cache']):
                        continue
                    
                    for file in files:
                        file_path = Path(root) / file
                        
                        if file_path.suffix.lower() in self.suspicious_extensions:
                            found.append({
                                'path': str(file_path),
                                'type': 'suspicious_extension',
                                'extension': file_path.suffix
                            })
                        
                        if any(keyword in file.lower() for keyword in ['decrypt', 'ransom', 'readme', 'howtodecrypt']):
                            if file_path.suffix.lower() in ['.txt', '.html', '.hta', '.lnk']:
                                found.append({
                                    'path': str(file_path),
                                    'type': 'ransom_note',
                                    'name': file
                                })
                    
                    if len(found) > 50:
                        break
                    
            except Exception as e:
                continue
        
        self.stats['last_scan'] = datetime.now()
        
        if found:
            self.ransomware_detected = True
            self.threat_level = ThreatLevel.CRITICAL
            self._log_message(f"Found {len(found)} ransomware indicators!", "ERROR")
            print(f"\n{Fore.RED}🚨 RANSOMWARE INDICATORS FOUND: {len(found)}{Style.RESET_ALL}")
            for item in found[:10]:
                print(f"  {Fore.RED}[!] {item['type']}: {Path(item['path']).name}{Style.RESET_ALL}")
            if len(found) > 10:
                print(f"  {Fore.YELLOW}... and {len(found) - 10} more{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}✅ No ransomware indicators found{Style.RESET_ALL}")
            self.ransomware_detected = False
        
        return found

    def display_dashboard(self):
        """Display interactive ransomware monitoring dashboard"""
        if self.use_rich and self.console:
            self._display_rich_dashboard()
        else:
            self._display_simple_dashboard()

    def _display_rich_dashboard(self):
        """Display dashboard using Rich library"""
        status = self.get_status()
        
        layout = Layout()
        layout.split(
            Layout(name="header", size=5),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        header_text = Text("🛡️ RANSOMWARE DETECTION DASHBOARD", style="bold cyan")
        header = Panel(
            Align.center(header_text),
            border_style="bright_blue",
            box=box.DOUBLE
        )
        layout["header"].update(header)
        
        status_color = "red" if status['ransomware_detected'] else "green"
        status_text = "🚨 ACTIVE THREAT" if status['ransomware_detected'] else "✅ SYSTEM CLEAN"
        
        status_table = Table(show_header=False, box=box.ROUNDED)
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Status", f"[{status_color}]{status_text}[/{status_color}]")
        status_table.add_row("Threat Level", f"[{status['threat_color']}]{status['threat_level']}[/{status['threat_color']}]")
        status_table.add_row("Uptime", status['uptime'])
        status_table.add_row("Running", "✅" if status['running'] else "❌")
        status_table.add_row("Monitored Dirs", str(status['monitored_dirs']))
        status_table.add_row("Total Alerts", str(status['total_alerts']))
        
        left_panel = Panel(
            status_table,
            title="Status",
            border_style="bright_blue",
            box=box.HEAVY
        )
        layout["left"].update(left_panel)
        
        stats_table = Table(show_header=False, box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats = status['stats']
        stats_table.add_row("Files Created", str(stats['files_created']))
        stats_table.add_row("Files Modified", str(stats['files_modified']))
        stats_table.add_row("Files Deleted", str(stats['files_deleted']))
        stats_table.add_row("Files Renamed", str(stats['files_renamed']))
        stats_table.add_row("Suspicious Processes", str(status['suspicious_processes']))
        stats_table.add_row("Suspicious Events", str(status['suspicious_events']))
        stats_table.add_row("Scans Performed", str(stats['total_scans']))
        
        right_panel = Panel(
            stats_table,
            title="Statistics",
            border_style="bright_blue",
            box=box.HEAVY
        )
        layout["right"].update(right_panel)
        
        footer_text = Text(
            f"Session: {self.session_id} | "
            f"Started: {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Last Scan: {stats['last_scan'].strftime('%H:%M:%S') if stats['last_scan'] else 'Never'}"
        )
        footer = Panel(
            Align.center(footer_text),
            border_style="bright_blue",
            box=box.HEAVY
        )
        layout["footer"].update(footer)
        
        if status['suspicious_events'] > 0:
            self.console.print()
            self.console.print(Text("Recent Suspicious Events", style="bold red"))
            
            events_table = Table(box=box.ROUNDED)
            events_table.add_column("Time", style="dim")
            events_table.add_column("Type", style="yellow")
            events_table.add_column("File", style="white")
            
            for event in self.get_suspicious_events(5):
                path = Path(event.path)
                events_table.add_row(
                    datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S"),
                    event.event_type,
                    path.name
                )
            self.console.print(events_table)
        
        self.console.print(layout)

    def _display_simple_dashboard(self):
        """Display dashboard without Rich library"""
        status = self.get_status()
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}🛡️  RANSOMWARE DETECTION DASHBOARD{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        status_color = Fore.RED if status['ransomware_detected'] else Fore.GREEN
        status_text = "🚨 ACTIVE THREAT" if status['ransomware_detected'] else "✅ SYSTEM CLEAN"
        print(f"{Fore.YELLOW}Status:{Style.RESET_ALL} {status_color}{status_text}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Threat Level:{Style.RESET_ALL} {status['threat_color']}{status['threat_level']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Uptime:{Style.RESET_ALL} {status['uptime']}")
        
        print(f"\n{Fore.CYAN}Activity Statistics:{Style.RESET_ALL}")
        stats = status['stats']
        print(f"  Files Created: {stats['files_created']}")
        print(f"  Files Modified: {stats['files_modified']}")
        print(f"  Files Deleted: {stats['files_deleted']}")
        print(f"  Files Renamed: {stats['files_renamed']}")
        print(f"  Suspicious Processes: {status['suspicious_processes']}")
        print(f"  Suspicious Events: {status['suspicious_events']}")
        print(f"  Alerts Triggered: {stats['alerts_triggered']}")
        
        if status['suspicious_events'] > 0:
            print(f"\n{Fore.RED}Recent Suspicious Events:{Style.RESET_ALL}")
            for event in self.get_suspicious_events(5):
                print(f"  {Fore.YELLOW}• {event.event_type}: {Path(event.path).name}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    def interactive_menu(self):
        """Interactive menu for ransomware monitoring"""
        while True:
            os.system('cls' if platform.system() == 'Windows' else 'clear')
            
            status = self.get_status()
            
            print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}🛡️  RANSOMWARE DETECTION & MONITORING SYSTEM{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            
            status_color = Fore.RED if status['ransomware_detected'] else Fore.GREEN
            status_text = "🚨 ACTIVE" if status['ransomware_detected'] else "✅ CLEAN"
            print(f"{Fore.YELLOW}Status:{Style.RESET_ALL} {status_color}{status_text}{Style.RESET_ALL} | "
                  f"{Fore.YELLOW}Level:{Style.RESET_ALL} {status['threat_color']}{status['threat_level']}{Style.RESET_ALL} | "
                  f"{Fore.YELLOW}Uptime:{Style.RESET_ALL} {status['uptime']}")
            print(f"{Fore.CYAN}{'-'*80}{Style.RESET_ALL}")
            
            print(f"""
{Fore.GREEN}┌────────────────────────────────────────────────────────────────────┐{Style.RESET_ALL}
{Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}1.{Style.RESET_ALL} Start Monitoring      {Fore.CYAN}2.{Style.RESET_ALL} Stop Monitoring       {Fore.CYAN}3.{Style.RESET_ALL} Scan Now
{Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}4.{Style.RESET_ALL} View Events          {Fore.CYAN}5.{Style.RESET_ALL} View Suspicious      {Fore.CYAN}6.{Style.RESET_ALL} Dashboard
{Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}7.{Style.RESET_ALL} Export Report        {Fore.CYAN}8.{Style.RESET_ALL} Clear Events         {Fore.CYAN}9.{Style.RESET_ALL} Exit
{Fore.GREEN}└────────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
""")
            
            print(f"{Fore.CYAN}Quick Stats:{Style.RESET_ALL}")
            print(f"  Files Changed: {status['stats']['files_created'] + status['stats']['files_modified']} | "
                  f"Deleted: {status['stats']['files_deleted']} | "
                  f"Alerts: {status['stats']['alerts_triggered']}")
            
            choice = input(f"\n{Fore.YELLOW}Select option (1-9): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self.start_monitoring()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '2':
                self.stop_monitoring()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '3':
                self.scan_for_ransomware()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '4':
                events = self.get_events(20)
                print(f"\n{Fore.CYAN}Recent Events:{Style.RESET_ALL}")
                for event in events[-10:]:
                    print(f"  {event.event_type}: {Path(event.path).name}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '5':
                self.display_dashboard()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '6':
                self.display_dashboard()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '7':
                self.export_report()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '8':
                self.suspicious_events.clear()
                self.file_activity_log.clear()
                self._log_message("Events cleared", "INFO")
                print(f"{Fore.GREEN}Events cleared{Style.RESET_ALL}")
                time.sleep(1)
            elif choice == '9':
                if self.is_running:
                    self.stop_monitoring()
                print(f"{Fore.GREEN}Exiting Ransomware Monitor{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Invalid option{Style.RESET_ALL}")
                time.sleep(1)

    def export_report(self, filename: str = None):
        """Export ransomware monitoring report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ransomware_report_{timestamp}.json"
        
        export_dir = Path.home() / "DSTerminal" / "reports"
        export_dir.mkdir(parents=True, exist_ok=True)
        filepath = export_dir / filename
        
        # Helper function to convert datetime to string
        def datetime_to_str(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)
        
        status = self.get_status()
        
        report = {
            'report_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'status': {
                'running': status['running'],
                'ransomware_detected': status['ransomware_detected'],
                'threat_level': status['threat_level'],
                'uptime': status['uptime'],
                'monitored_dirs': status['monitored_dirs'],
                'total_alerts': status['total_alerts']
            },
            'statistics': {
                'files_created': status['stats']['files_created'],
                'files_modified': status['stats']['files_modified'],
                'files_deleted': status['stats']['files_deleted'],
                'files_renamed': status['stats']['files_renamed'],
                'suspicious_processes': status['suspicious_processes'],
                'suspicious_events': status['suspicious_events'],
                'alerts_triggered': status['stats']['alerts_triggered'],
                'total_scans': status['stats']['total_scans'],
                'start_time': status['stats']['start_time'].isoformat() if status['stats']['start_time'] else None,
                'last_scan': status['stats']['last_scan'].isoformat() if status['stats']['last_scan'] else None
            },
            'suspicious_events': [
                {
                    'timestamp': e.timestamp,
                    'type': e.event_type,
                    'path': e.path,
                    'size': e.size,
                    'extension': e.extension,
                    'is_suspicious': e.is_suspicious
                } for e in self.suspicious_events
            ],
            'suspicious_processes': [
                {
                    'pid': p.pid,
                    'name': p.name,
                    'cmdline': p.cmdline,
                    'cpu': p.cpu,
                    'detected_at': p.detected_at
                } for p in self.detected_processes
            ],
            'monitored_directories': [str(d) for d in self.monitored_dirs if d.exists()]
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=datetime_to_str)
            
            self._log_message(f"Report exported: {filepath}", "SUCCESS")
            print(f"\n{Fore.GREEN}✅ Report exported successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📄 Location: {filepath}{Style.RESET_ALL}")
            return str(filepath)
        except Exception as e:
            self._log_message(f"Failed to export report: {str(e)}", "ERROR")
            print(f"\n{Fore.RED}❌ Failed to export report: {str(e)}{Style.RESET_ALL}")
            return None


# ============================================================================
# DSTerminal Integration Functions
# ============================================================================

def integrate_with_dsterminal(dsterminal_instance):
    """
    Integrate ransomware monitor with DSTerminal instance.
    This should be called from DSTerminal's command handler.
    """
    if not hasattr(dsterminal_instance, 'ransomware_monitor'):
        dsterminal_instance.ransomware_monitor = RansomwareMonitor(
            session_id=dsterminal_instance.session_id,
            log_callback=dsterminal_instance.log_message
        )
    return dsterminal_instance.ransomware_monitor


def cmd_ransomware(dsterminal_instance, args):
    """Command handler for ransomware monitoring"""
    if not hasattr(dsterminal_instance, 'ransomware_monitor'):
        dsterminal_instance.ransomware_monitor = RansomwareMonitor(
            session_id=dsterminal_instance.session_id,
            log_callback=dsterminal_instance.log_message
        )
    
    monitor = dsterminal_instance.ransomware_monitor
    
    if not args:
        monitor.display_dashboard()
        return
    
    cmd = args[0].lower()
    
    if cmd == 'start':
        monitor.start_monitoring()
    elif cmd == 'stop':
        monitor.stop_monitoring()
    elif cmd == 'scan':
        path = args[1] if len(args) > 1 else None
        monitor.scan_for_ransomware(path)
    elif cmd == 'status':
        status = monitor.get_status()
        print(f"\n{Fore.CYAN}Ransomware Monitor Status:{Style.RESET_ALL}")
        print(f"  Running: {status['running']}")
        print(f"  Ransomware Detected: {status['ransomware_detected']}")
        print(f"  Threat Level: {status['threat_color']}{status['threat_level']}{Style.RESET_ALL}")
        print(f"  Uptime: {status['uptime']}")
        print(f"  Monitored Directories: {status['monitored_dirs']}")
        print(f"  Total Alerts: {status['total_alerts']}")
    elif cmd == 'dashboard':
        monitor.display_dashboard()
    elif cmd == 'events':
        limit = int(args[1]) if len(args) > 1 else 20
        events = monitor.get_events(limit)
        print(f"\n{Fore.CYAN}Recent File Events:{Style.RESET_ALL}")
        for event in events[-10:]:
            print(f"  {event.event_type}: {Path(event.path).name}")
    elif cmd == 'suspicious':
        events = monitor.get_suspicious_events(10)
        print(f"\n{Fore.RED}Suspicious Events:{Style.RESET_ALL}")
        for event in events:
            print(f"  [!] {event.event_type}: {Path(event.path).name}")
    elif cmd == 'export':
        monitor.export_report()
    elif cmd == 'interactive' or cmd == 'menu':
        monitor.interactive_menu()
    elif cmd in ['help', '?']:
        print(f"""
{Fore.CYAN}Ransomware Monitor Commands:{Style.RESET_ALL}
  start          - Start real-time monitoring
  stop           - Stop monitoring
  scan [path]    - Scan for ransomware indicators
  status         - Show monitoring status
  dashboard      - Display full dashboard
  events [n]     - Show recent events
  suspicious     - Show suspicious events
  export         - Export report
  interactive    - Launch interactive menu
  help           - Show this help
        """)
    else:
        print(f"{Fore.RED}Unknown command: {cmd}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'ransomware help' for available commands{Style.RESET_ALL}")


# ============================================================================
# Standalone Execution
# ============================================================================

def main():
    """Standalone execution with interactive menu"""
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🛡️  RANSOMWARE DETECTION & MONITORING SYSTEM v3.1.113{Style.RESET_ALL}          {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}  {Fore.YELLOW}Developed by: Spark Wilson Spink | © 2024{Style.RESET_ALL}                              {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}Platform: {platform.system()} {platform.release()}{Style.RESET_ALL}                               {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    # Initialize monitor with simple mode
    monitor = RansomwareMonitor(use_rich=False)
    
    # Check dependencies
    if not WATCHDOG_AVAILABLE:
        print(f"{Fore.YELLOW}⚠️ Watchdog not available - installing...{Style.RESET_ALL}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'watchdog'], 
                         capture_output=True)
            print(f"{Fore.GREEN}✅ Watchdog installed. Please restart.{Style.RESET_ALL}")
        except:
            print(f"{Fore.YELLOW}⚠️ Could not install watchdog. Using polling mode.{Style.RESET_ALL}")
    
    # Start interactive menu
    monitor.interactive_menu()


if __name__ == "__main__":
    main()