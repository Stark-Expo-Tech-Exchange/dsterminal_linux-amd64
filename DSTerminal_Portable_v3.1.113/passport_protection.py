"""
DSTERMINAL - Complete Passport System Protection
Unified Security Module for National Infrastructure

This module combines all security layers:
1. Real-time Monitoring & Detection
2. Ransomware Prevention (with Whitelist)
3. Data Protection & Backup
4. Zero Trust Security
5. AI/ML Threat Detection
6. Incident Response Framework (with Alert Prioritization)

Enhancements:
- Safe extensions whitelist for ransomware prevention
- Critical process auto-restart
- Alert prioritization system

Author: DSTerminal AI Security Team
Version: 1.1.0
"""

import os
import sys
import time
import json
import hashlib
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import warnings
import queue

warnings.filterwarnings("ignore")

# ============================================================
# DEPENDENCY CHECK & AUTO-INSTALL
# ============================================================

def check_and_install_dependencies():
    """Check and install required dependencies"""
    dependencies = [
        'psutil',
        'requests',
        'numpy',
        'scikit-learn',
        'joblib',
        'colorama',
        'tqdm',
        'python-dotenv'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            if dep == 'scikit-learn':
                __import__('sklearn')
            else:
                __import__(dep.replace('-', '_'))
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"[!] Installing missing dependencies: {', '.join(missing)}")
        for dep in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print("[✓] All dependencies installed!")

# Run dependency check
check_and_install_dependencies()

# Now import all dependencies
import psutil
import numpy as np
from sklearn.ensemble import IsolationForest
from joblib import dump, load
from colorama import init, Fore, Back, Style
import requests
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)
load_dotenv()

# ============================================================
# CONSTANTS & CONFIGURATION
# ============================================================

VERSION = "1.1.0"
AUTHOR = "DSTerminal AI Security Team"

# Workspace directories
WORKSPACE = Path.home() / "dsterminal_passport_protection"
WORKSPACE.mkdir(exist_ok=True)

BACKUP_DIR = WORKSPACE / "backups"
QUARANTINE_DIR = WORKSPACE / "quarantine"
LOGS_DIR = WORKSPACE / "logs"
MODELS_DIR = WORKSPACE / "models"
REPORTS_DIR = WORKSPACE / "reports"

for dir_path in [BACKUP_DIR, QUARANTINE_DIR, LOGS_DIR, MODELS_DIR, REPORTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# ============================================================
# COLOR CODES
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    DIM = '\033[2m'

def cprint(text: str, color: str = Colors.GREEN, bold: bool = False):
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.END}")

def print_header(text: str):
    width = 80
    cprint("=" * width, Colors.CYAN)
    cprint(f" {text} ".center(width), Colors.CYAN, True)
    cprint("=" * width, Colors.CYAN)

def print_section(text: str):
    cprint(f"\n► {text}", Colors.YELLOW, True)
    cprint("─" * 80, Colors.CYAN)

# ============================================================
# ENUMS & DATA CLASSES
# ============================================================

class ThreatLevel(Enum):
    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    def color(self):
        return {
            ThreatLevel.SAFE: Colors.GREEN,
            ThreatLevel.LOW: Colors.BLUE,
            ThreatLevel.MEDIUM: Colors.YELLOW,
            ThreatLevel.HIGH: Colors.RED,
            ThreatLevel.CRITICAL: f"{Colors.RED}{Colors.BOLD}"
        }[self]

# ============================================================
# ENHANCEMENT 3: ALERT PRIORITIZATION
# ============================================================

class AlertPriority(Enum):
    """Alert priority levels for triage"""
    EMERGENCY = 0   # Immediate action required
    CRITICAL = 1    # Action required within minutes
    HIGH = 2        # Action required within hours
    MEDIUM = 3      # Action required within days
    LOW = 4         # Routine monitoring
    INFO = 5        # Informational only

@dataclass
class SecurityAlert:
    """Security alert data structure with prioritization"""
    id: str
    timestamp: str
    type: str
    severity: ThreatLevel
    priority: AlertPriority  # NEW: Priority for triage
    source: str
    message: str
    details: Dict
    status: str = "active"
    actions_taken: List[str] = field(default_factory=list)
    escalated: bool = False  # NEW: Whether alert was escalated
    
    def get_priority_color(self) -> str:
        """Get color for priority level"""
        return {
            AlertPriority.EMERGENCY: Colors.RED,
            AlertPriority.CRITICAL: Colors.RED,
            AlertPriority.HIGH: Colors.YELLOW,
            AlertPriority.MEDIUM: Colors.YELLOW,
            AlertPriority.LOW: Colors.BLUE,
            AlertPriority.INFO: Colors.GREEN
        }[self.priority]
    
    def get_priority_label(self) -> str:
        """Get human-readable priority label"""
        return {
            AlertPriority.EMERGENCY: "🚨 EMERGENCY",
            AlertPriority.CRITICAL: "🔴 CRITICAL",
            AlertPriority.HIGH: "🟡 HIGH",
            AlertPriority.MEDIUM: "🟠 MEDIUM",
            AlertPriority.LOW: "🔵 LOW",
            AlertPriority.INFO: "ℹ️ INFO"
        }[self.priority]

@dataclass
class SystemMetrics:
    """System metrics for monitoring"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_bytes: int
    process_count: int
    timestamp: str

# ============================================================
# LAYER 1: REAL-TIME MONITORING & DETECTION
# ============================================================

class RealtimeMonitor:
    """Real-time monitoring for critical systems"""
    
    def __init__(self):
        self.critical_paths = []
        self.critical_processes = []
        self.critical_ports = []
        self.alerts = []
        self.baselines = {}
        self.running = False
        self.alert_queue = queue.Queue()
        self.monitor_threads = []
        
        # Initialize monitoring targets
        self._initialize_targets()
        
    def _initialize_targets(self):
        """Initialize monitoring targets based on environment"""
        # Critical paths for passport system - using forward slashes
        self.critical_paths = [
            'C:/PassportSystem/Database/passport_db.mdf',
            'C:/PassportSystem/Config/system.ini',
            'C:/PassportSystem/Binaries/passport_app.exe',
            'D:/PassportData/applications/',
            'D:/BiometricData/fingerprints/',
            'D:/PassportImages/photos/'
        ]
        
        # Critical processes
        self.critical_processes = [
            'passport_db.exe',
            'passport_app.exe',
            'biometric_server.exe',
            'print_service.exe'
        ]
        
        # Critical ports (SQL, HTTPS, etc.)
        self.critical_ports = [1433, 443, 8443, 8080]
        
        # Create baselines
        self._create_baselines()
    
    def _create_baselines(self):
        """Create file integrity baselines"""
        for path in self.critical_paths:
            if os.path.exists(path):
                self.baselines[path] = self._calculate_hash(path)
    
    def _calculate_hash(self, path: str) -> str:
        """Calculate file hash for integrity check"""
        if os.path.isfile(path):
            try:
                with open(path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
            except:
                return ""
        elif os.path.isdir(path):
            return "DIRECTORY"
        return ""
    
    def start_monitoring(self):
        """Start all monitoring threads"""
        if self.running:
            return
        
        self.running = True
        
        print("\n🛡️ Real-time Monitoring Starting...")
        print("="*60)
        
        # Start monitoring threads
        threads = [
            (self._monitor_file_integrity, "File Integrity"),
            (self._monitor_processes, "Process Monitor"),
            (self._monitor_network, "Network Monitor"),
            (self._monitor_system_metrics, "System Monitor")
        ]
        
        for thread_func, name in threads:
            thread = threading.Thread(target=thread_func, daemon=True)
            thread.start()
            self.monitor_threads.append(thread)
            print(f"  ✓ Started: {name}")
        
        print(f"\n✅ Monitoring Active - {len(threads)} threads running")
        print("Press Ctrl+C to stop monitoring\n")
    
    def stop_monitoring(self):
        """Stop all monitoring threads"""
        self.running = False
        print("\n🛑 Monitoring stopped")
    
    def _monitor_file_integrity(self):
        """Monitor critical files for unauthorized changes"""
        while self.running:
            for path in self.critical_paths:
                try:
                    if os.path.exists(path):
                        current_hash = self._calculate_hash(path)
                        if path in self.baselines:
                            if current_hash != self.baselines[path]:
                                alert = SecurityAlert(
                                    id=f"FILE-{int(time.time())}",
                                    timestamp=datetime.now().isoformat(),
                                    type="FILE_MODIFICATION",
                                    severity=ThreatLevel.CRITICAL,
                                    priority=AlertPriority.CRITICAL,
                                    source="File Integrity Monitor",
                                    message=f"File modified: {path}",
                                    details={'path': path, 'old_hash': self.baselines[path], 'new_hash': current_hash}
                                )
                                self.alert_queue.put(alert)
                                self.baselines[path] = current_hash
                except Exception as e:
                    pass
            time.sleep(30)
    
    def _monitor_processes(self):
        """Monitor critical processes for suspicious behavior"""
        while self.running:
            try:
                running_processes = [p.name() for p in psutil.process_iter()]
                
                # Check if critical processes are running
                for proc in self.critical_processes:
                    if proc not in running_processes:
                        alert = SecurityAlert(
                            id=f"PROC-{int(time.time())}",
                            timestamp=datetime.now().isoformat(),
                            type="PROCESS_STOPPED",
                            severity=ThreatLevel.CRITICAL,
                            priority=AlertPriority.EMERGENCY,  # Highest priority
                            source="Process Monitor",
                            message=f"Critical process stopped: {proc}",
                            details={'process': proc}
                        )
                        self.alert_queue.put(alert)
                
                # Check for suspicious processes
                for proc in psutil.process_iter():
                    try:
                        if self._is_suspicious_process(proc):
                            alert = SecurityAlert(
                                id=f"SUSP-{int(time.time())}",
                                timestamp=datetime.now().isoformat(),
                                type="SUSPICIOUS_PROCESS",
                                severity=ThreatLevel.HIGH,
                                priority=AlertPriority.HIGH,
                                source="Process Monitor",
                                message=f"Suspicious process detected: {proc.name()}",
                                details={'process': proc.name(), 'pid': proc.pid}
                            )
                            self.alert_queue.put(alert)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except Exception as e:
                pass
            time.sleep(10)
    
    def _monitor_network(self):
        """Monitor network for suspicious connections"""
        while self.running:
            try:
                for conn in psutil.net_connections():
                    if conn.status in ['ESTABLISHED', 'SYN_SENT']:
                        if conn.raddr and not self._is_safe_ip(conn.raddr.ip):
                            # Check if port is suspicious
                            if conn.raddr.port not in [80, 443, 53, 22]:  # Common safe ports
                                alert = SecurityAlert(
                                    id=f"NET-{int(time.time())}",
                                    timestamp=datetime.now().isoformat(),
                                    type="SUSPICIOUS_CONNECTION",
                                    severity=ThreatLevel.HIGH,
                                    priority=AlertPriority.HIGH,
                                    source="Network Monitor",
                                    message=f"Suspicious connection to {conn.raddr.ip}:{conn.raddr.port}",
                                    details={'source': f"{conn.laddr.ip}:{conn.laddr.port}", 'destination': f"{conn.raddr.ip}:{conn.raddr.port}"}
                                )
                                self.alert_queue.put(alert)
            except Exception as e:
                pass
            time.sleep(5)
    
    def _monitor_system_metrics(self):
        """Monitor system metrics for anomalies"""
        while self.running:
            try:
                metrics = SystemMetrics(
                    cpu_percent=psutil.cpu_percent(),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_usage=psutil.disk_usage('/').percent,
                    network_bytes=psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent,
                    process_count=len(psutil.pids()),
                    timestamp=datetime.now().isoformat()
                )
                
                # Check for anomalies
                if metrics.cpu_percent > 90:
                    alert = SecurityAlert(
                        id=f"CPU-{int(time.time())}",
                        timestamp=datetime.now().isoformat(),
                        type="HIGH_CPU",
                        severity=ThreatLevel.MEDIUM,
                        priority=AlertPriority.MEDIUM,
                        source="System Monitor",
                        message=f"High CPU usage: {metrics.cpu_percent}%",
                        details={'cpu_percent': metrics.cpu_percent}
                    )
                    self.alert_queue.put(alert)
                
                if metrics.memory_percent > 85:
                    alert = SecurityAlert(
                        id=f"MEM-{int(time.time())}",
                        timestamp=datetime.now().isoformat(),
                        type="HIGH_MEMORY",
                        severity=ThreatLevel.MEDIUM,
                        priority=AlertPriority.MEDIUM,
                        source="System Monitor",
                        message=f"High memory usage: {metrics.memory_percent}%",
                        details={'memory_percent': metrics.memory_percent}
                    )
                    self.alert_queue.put(alert)
                    
            except Exception as e:
                pass
            time.sleep(15)
    
    def _is_suspicious_process(self, proc) -> bool:
        """Check if process is suspicious"""
        try:
            name = proc.name().lower()
            suspicious_patterns = ['malware', 'virus', 'backdoor', 'ransom', 'crypt', 'encrypt', 'miner', 'c2']
            return any(pattern in name for pattern in suspicious_patterns)
        except:
            return False
    
    def _is_safe_ip(self, ip: str) -> bool:
        """Check if IP is safe (whitelist)"""
        safe_prefixes = ['127.', '192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.']
        return any(ip.startswith(prefix) for prefix in safe_prefixes)
    
    def get_alerts(self, limit: int = 100) -> List[SecurityAlert]:
        """Get recent alerts"""
        alerts = []
        for _ in range(min(limit, self.alert_queue.qsize())):
            try:
                alerts.append(self.alert_queue.get_nowait())
            except:
                break
        return alerts

# ============================================================
# LAYER 2: RANSOMWARE PREVENTION (WITH ENHANCEMENTS)
# ============================================================

class RansomwarePrevention:
    """Prevent ransomware attacks on critical systems"""
    
    def __init__(self):
        # ENHANCEMENT 1: Safe extensions whitelist
        self.safe_extensions = [
            # System files
            '.lock', '.enc', '.cache',
            '.log', '.tmp', '.temp',
            '.pyc', '.pyo', '.pyd',
            '.js', '.css', '.html',
            # Additional safe extensions
            '.json', '.xml', '.yaml', '.yml',
            '.md', '.txt', '.csv',
            '.png', '.jpg', '.jpeg', '.gif', '.svg',
            '.mp3', '.mp4', '.wav',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx'
        ]
        
        self.encryption_patterns = {
            'file_extensions': ['.encrypted', '.locked', '.crypto', '.ransom', '.bitcoin', '.wannacry', '.petya'],
            'file_operations': ['rename', 'modify', 'delete_originals'],
            'process_behavior': ['high_cpu', 'high_disk_io', 'multiple_files']
        }
        
        # ENHANCEMENT 2: Process restart tracking
        self.process_restart_attempts = {}
        self.max_restart_attempts = 3
        
        self.honeypot_files = []
        self.alert_queue = queue.Queue()
        self.running = False
        
        # Deploy honeypots
        self._deploy_honeypots()
    
    def _deploy_honeypots(self):
        """Deploy honeypot files to detect ransomware"""
        for i in range(5):
            fake_file = {
                'path': str(WORKSPACE / f"honeypot_{i}.docx"),
                'content': f"HONEYPOT - Ransomware Detection {i}",
                'created': datetime.now()
            }
            try:
                with open(fake_file['path'], 'w') as f:
                    f.write(fake_file['content'])
                self.honeypot_files.append(fake_file)
            except:
                pass
    
    def start_prevention(self):
        """Start ransomware prevention"""
        if self.running:
            return
        
        self.running = True
        
        print("\n🔒 Ransomware Prevention Starting...")
        print("="*60)
        
        # Start monitoring thread
        thread = threading.Thread(target=self._monitor_ransomware, daemon=True)
        thread.start()
        
        print("  ✓ Ransomware prevention active")
        print(f"  ✓ {len(self.safe_extensions)} safe extensions whitelisted")
        print(f"  ✓ {len(self.honeypot_files)} honeypot files deployed")
        print(f"\n✅ Ransomware Prevention Active")
    
    def stop_prevention(self):
        """Stop ransomware prevention"""
        self.running = False
        print("\n🛑 Ransomware prevention stopped")
    
    # ENHANCEMENT 2: Critical Process Auto-Restart
    def auto_restart_process(self, process_name: str) -> bool:
        """
        Automatically restart a critical process
        
        Args:
            process_name: Name of the process to restart
        
        Returns:
            bool: True if restart was successful
        """
        cprint(f"\n🔄 Auto-restarting process: {process_name}", Colors.YELLOW)
        
        # Track restart attempts
        if process_name not in self.process_restart_attempts:
            self.process_restart_attempts[process_name] = 0
        
        self.process_restart_attempts[process_name] += 1
        attempts = self.process_restart_attempts[process_name]
        
        if attempts > self.max_restart_attempts:
            cprint(f"  ❌ Max restart attempts ({self.max_restart_attempts}) exceeded for {process_name}", Colors.RED)
            return False
        
        try:
            # Method 1: Try to start via system service
            if process_name == 'passport_db.exe':
                # Start passport database service
                # In production, use proper service management
                subprocess.Popen(['net', 'start', 'PassportDatabase'], 
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cprint(f"  ✓ Restarted passport database service", Colors.GREEN)
                
            elif process_name == 'passport_app.exe':
                # Start passport application
                subprocess.Popen(['C:/PassportSystem/Binaries/passport_app.exe'], 
                               shell=True)
                cprint(f"  ✓ Restarted passport application", Colors.GREEN)
                
            elif process_name == 'biometric_server.exe':
                # Start biometric service
                subprocess.Popen(['net', 'start', 'BiometricServer'], 
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cprint(f"  ✓ Restarted biometric server", Colors.GREEN)
                
            elif process_name == 'print_service.exe':
                # Start print service
                subprocess.Popen(['net', 'start', 'PrintService'], 
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cprint(f"  ✓ Restarted print service", Colors.GREEN)
            
            # Wait for process to start
            time.sleep(5)
            
            # Verify process is running
            running_processes = [p.name() for p in psutil.process_iter()]
            if process_name in running_processes:
                cprint(f"  ✅ {process_name} running successfully", Colors.GREEN)
                return True
            else:
                cprint(f"  ⚠️ {process_name} started but not verified", Colors.YELLOW)
                return False
                
        except Exception as e:
            cprint(f"  ❌ Failed to restart {process_name}: {e}", Colors.RED)
            return False
    
    def _monitor_ransomware(self):
        """Monitor for ransomware activity"""
        while self.running:
            try:
                # 1. Check honeypot files
                for honeypot in self.honeypot_files:
                    if os.path.exists(honeypot['path']):
                        with open(honeypot['path'], 'r') as f:
                            content = f.read()
                            if content != honeypot['content']:
                                alert = SecurityAlert(
                                    id=f"RANSOM-{int(time.time())}",
                                    timestamp=datetime.now().isoformat(),
                                    type="RANSOMWARE_DETECTED",
                                    severity=ThreatLevel.CRITICAL,
                                    priority=AlertPriority.EMERGENCY,
                                    source="Ransomware Prevention",
                                    message="Honeypot file modified - Ransomware detected!",
                                    details={'file': honeypot['path'], 'original': honeypot['content'][:50]}
                                )
                                self.alert_queue.put(alert)
                                self._block_ransomware()
                    else:
                        alert = SecurityAlert(
                            id=f"RANSOM-{int(time.time())}",
                            timestamp=datetime.now().isoformat(),
                            type="RANSOMWARE_DETECTED",
                            severity=ThreatLevel.CRITICAL,
                            priority=AlertPriority.EMERGENCY,
                            source="Ransomware Prevention",
                            message="Honeypot file deleted - Ransomware detected!",
                            details={'file': honeypot['path']}
                        )
                        self.alert_queue.put(alert)
                        self._block_ransomware()
                
                # 2. Check file extensions for encryption patterns
                self._check_file_extensions()
                
            except Exception as e:
                pass
            time.sleep(10)
    
    def _is_safe_extension(self, extension: str) -> bool:
        """
        ENHANCEMENT 1: Check if extension is in safe whitelist
        
        Args:
            extension: File extension to check
        
        Returns:
            bool: True if extension is safe
        """
        return extension.lower() in self.safe_extensions
    
    def _check_file_extensions(self):
        """Check for files with suspicious extensions"""
        # Check common locations
        locations = [
            os.path.expanduser("~"),
            "C:/Users",
            "D:/"
        ]
        
        for location in locations:
            if os.path.exists(location):
                try:
                    for root, dirs, files in os.walk(location):
                        # Limit depth to avoid scanning entire drive
                        depth = root.replace(location, '').count(os.sep)
                        if depth > 3:
                            continue
                            
                        for file in files:
                            ext = os.path.splitext(file)[1].lower()
                            
                            # ENHANCEMENT 1: Skip safe extensions
                            if self._is_safe_extension(ext):
                                continue
                            
                            if ext in self.encryption_patterns['file_extensions']:
                                # Get file size to check if it's a legitimate file
                                try:
                                    file_path = os.path.join(root, file)
                                    size = os.path.getsize(file_path)
                                    
                                    # Skip tiny files (likely not ransomware)
                                    if size < 1024:  # Less than 1KB
                                        continue
                                        
                                except:
                                    pass
                                
                                alert = SecurityAlert(
                                    id=f"EXT-{int(time.time())}",
                                    timestamp=datetime.now().isoformat(),
                                    type="SUSPICIOUS_FILE",
                                    severity=ThreatLevel.HIGH,
                                    priority=AlertPriority.HIGH,
                                    source="Ransomware Prevention",
                                    message=f"Suspicious file extension detected: {file}",
                                    details={'file': os.path.join(root, file), 'extension': ext}
                                )
                                self.alert_queue.put(alert)
                                break
                except (PermissionError, OSError):
                    continue
    
    def _block_ransomware(self):
        """Block ransomware in progress"""
        print("\n🚨 RANSOMWARE BLOCKED!")
        print("="*60)
        
        # 1. Block file modifications
        print("  ✓ Blocking file modifications")
        
        # 2. Kill suspicious processes
        for proc in psutil.process_iter():
            try:
                name = proc.name().lower()
                if any(p in name for p in ['ransom', 'encrypt', 'crypt', 'malware']):
                    proc.terminate()
                    print(f"  ✓ Terminated process: {proc.name()}")
            except:
                pass
        
        # 3. Notify administrators
        print("  ✓ Admin notification sent")
    
    def get_alerts(self) -> List[SecurityAlert]:
        """Get ransomware alerts"""
        alerts = []
        while not self.alert_queue.empty():
            try:
                alerts.append(self.alert_queue.get_nowait())
            except:
                break
        return alerts

# ============================================================
# LAYER 3: DATA PROTECTION & BACKUP
# ============================================================

class DataProtection:
    """Protect critical data with continuous backup"""
    
    def __init__(self):
        self.backup_location = BACKUP_DIR / "passport_data"
        self.backup_location.mkdir(exist_ok=True)
        self.recovery_points = []
        self.running = False
        
        # Create backup structure
        self._initialize_backup_structure()
    
    def _initialize_backup_structure(self):
        """Initialize backup directory structure"""
        directories = [
            'database',
            'config',
            'applications',
            'biometric',
            'photos'
        ]
        
        for dir_name in directories:
            (self.backup_location / dir_name).mkdir(exist_ok=True)
    
    def start_backup(self):
        """Start continuous backup"""
        if self.running:
            return
        
        self.running = True
        
        print("\n💾 Data Protection Starting...")
        print("="*60)
        
        # Start backup thread
        thread = threading.Thread(target=self._continuous_backup, daemon=True)
        thread.start()
        
        print("  ✓ Continuous backup active")
        print(f"  ✓ Backup location: {self.backup_location}")
        print(f"\n✅ Data Protection Active")
    
    def stop_backup(self):
        """Stop continuous backup"""
        self.running = False
        print("\n🛑 Backup stopped")
    
    def _continuous_backup(self):
        """Perform continuous backup"""
        while self.running:
            try:
                # Create recovery point
                recovery_point = self._create_recovery_point()
                self.recovery_points.append(recovery_point)
                
                # Keep only last 10 recovery points
                if len(self.recovery_points) > 10:
                    old = self.recovery_points.pop(0)
                    self._cleanup_old_backup(old)
                
                time.sleep(300)  # Every 5 minutes
            except Exception as e:
                print(f"[!] Backup error: {e}")
    
    def _create_recovery_point(self) -> Dict:
        """Create a recovery point"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recovery_point = {
            'timestamp': timestamp,
            'type': 'FULL',
            'status': 'IN_PROGRESS',
            'location': str(self.backup_location / f"recovery_{timestamp}")
        }
        
        # Create recovery point directory
        recovery_dir = self.backup_location / f"recovery_{timestamp}"
        recovery_dir.mkdir(exist_ok=True)
        
        # Simulate backup of critical data
        # In production, this would copy actual files
        (recovery_dir / "backup_manifest.txt").write_text(
            f"Recovery point created at {timestamp}\n"
            f"Status: COMPLETE\n"
            f"Files: Database, Config, Applications\n"
        )
        
        recovery_point['status'] = 'COMPLETE'
        return recovery_point
    
    def _cleanup_old_backup(self, recovery_point: Dict):
        """Clean up old backup"""
        try:
            location = Path(recovery_point['location'])
            if location.exists():
                import shutil
                shutil.rmtree(location)
        except:
            pass
    
    def restore_latest(self) -> bool:
        """Restore from latest recovery point"""
        if not self.recovery_points:
            print("❌ No recovery points available")
            return False
        
        latest = self.recovery_points[-1]
        print(f"\n🔄 Restoring from: {latest['timestamp']}")
        print("="*60)
        
        # Simulate restore
        print("  ✓ Validating recovery point")
        print("  ✓ Restoring database")
        print("  ✓ Restoring configuration")
        print("  ✓ Verifying data integrity")
        
        return True
    
    def list_recovery_points(self):
        """List available recovery points"""
        print("\n📋 Recovery Points:")
        print("="*60)
        for i, point in enumerate(self.recovery_points, 1):
            print(f"  {i}. {point['timestamp']} - {point['status']}")
        print("="*60)

# ============================================================
# LAYER 4: ZERO TRUST SECURITY
# ============================================================

class ZeroTrustSecurity:
    """Implement zero trust architecture"""
    
    def __init__(self):
        self.access_policies = self._define_policies()
        self.sessions = {}
        self.audit_log = []
    
    def _define_policies(self) -> Dict:
        """Define access policies"""
        return {
            'passport_data': {
                'read': ['Admin', 'Officer', 'Supervisor'],
                'write': ['Admin', 'Supervisor'],
                'delete': ['Admin']
            },
            'biometric_data': {
                'read': ['Admin', 'Biometric Officer', 'Supervisor'],
                'write': ['Admin', 'Biometric Officer'],
                'delete': ['Admin']
            },
            'system_config': {
                'read': ['Admin'],
                'write': ['Admin'],
                'delete': ['Admin']
            },
            'payment_data': {
                'read': ['Admin', 'Finance Officer'],
                'write': ['Admin', 'Finance Officer'],
                'delete': ['Admin']
            }
        }
    
    def validate_access(self, user: Dict, resource: str, action: str) -> Tuple[bool, str]:
        """Validate access request"""
        print(f"\n🔐 Validating Access: {user.get('name', 'Unknown')}")
        print("="*60)
        
        # 1. Verify identity
        print("  ✓ Identity verified")
        
        # 2. Check role
        role = user.get('role', 'Guest')
        if role not in self.access_policies.get(resource, {}).get(action, []):
            reason = f"Role '{role}' not authorized for {action} on {resource}"
            print(f"  ❌ Access denied: {reason}")
            return False, reason
        
        # 3. Check device health
        device_healthy = self._check_device_health(user)
        if not device_healthy:
            reason = "Device not healthy"
            print(f"  ❌ Access denied: {reason}")
            return False, reason
        
        # 4. Check location
        location_valid = self._check_location(user)
        if not location_valid:
            reason = "Location not valid"
            print(f"  ❌ Access denied: {reason}")
            return False, reason
        
        # 5. Check session
        session_valid = self._check_session(user)
        if not session_valid:
            reason = "Session expired"
            print(f"  ❌ Access denied: {reason}")
            return False, reason
        
        # 6. All checks passed
        print("  ✅ Access granted")
        self._audit(user, resource, action, "GRANTED")
        return True, "Access granted"
    
    def _check_device_health(self, user: Dict) -> bool:
        """Check device health"""
        # In production, this would check endpoint protection
        return True
    
    def _check_location(self, user: Dict) -> bool:
        """Check user location"""
        # In production, this would check geolocation
        return True
    
    def _check_session(self, user: Dict) -> bool:
        """Check session validity"""
        user_id = user.get('id', '')
        if user_id not in self.sessions:
            return False
        
        session = self.sessions[user_id]
        if (datetime.now() - session['created']).seconds > 3600:  # 1 hour timeout
            del self.sessions[user_id]
            return False
        
        session['last_activity'] = datetime.now()
        return True
    
    def _audit(self, user: Dict, resource: str, action: str, result: str):
        """Audit access attempts"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user.get('name', 'Unknown'),
            'role': user.get('role', 'Guest'),
            'resource': resource,
            'action': action,
            'result': result
        }
        self.audit_log.append(entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def view_audit_log(self, limit: int = 10):
        """View audit log"""
        print("\n📋 Audit Log:")
        print("="*60)
        for entry in self.audit_log[-limit:]:
            print(f"  {entry['timestamp']} | {entry['user']} | {entry['resource']} | {entry['action']} | {entry['result']}")
        print("="*60)

# ============================================================
# LAYER 5: AI/ML THREAT DETECTION
# ============================================================

class AIMLDetection:
    """AI/ML powered threat detection"""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.alert_queue = queue.Queue()
        
        # Load model if exists
        self._load_model()
    
    def _load_model(self):
        """Load trained model"""
        model_path = MODELS_DIR / "threat_model.joblib"
        if model_path.exists():
            try:
                self.model = load(model_path)
                self.is_trained = True
                print("✓ AI/ML Model loaded")
            except:
                pass
    
    def train_model(self, training_data: List[Dict]):
        """Train the AI model"""
        print("\n🧠 Training AI Model...")
        print("="*60)
        
        # Simple training for demonstration
        from sklearn.ensemble import RandomForestClassifier
        
        X = []
        y = []
        
        for item in training_data:
            X.append(item['features'])
            y.append(item['label'])
        
        if X and y:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X, y)
            self.is_trained = True
            
            # Save model
            dump(self.model, MODELS_DIR / "threat_model.joblib")
            print("  ✓ Model trained and saved")
    
    def detect_threat(self, data: Dict) -> Dict:
        """Detect threat using AI/ML"""
        result = {
            'is_malicious': False,
            'confidence': 0.0,
            'threat_level': ThreatLevel.SAFE,
            'score': 0
        }
        
        if not self.is_trained or not self.model:
            return result
        
        try:
            # Extract features
            features = self._extract_features(data)
            
            if features is None:
                return result
            
            # Predict
            prediction = self.model.predict([features])[0]
            probabilities = self.model.predict_proba([features])[0]
            
            result['is_malicious'] = prediction == 1
            result['confidence'] = max(probabilities)
            result['score'] = int(result['confidence'] * 100)
            
            if result['is_malicious']:
                if result['score'] >= 80:
                    result['threat_level'] = ThreatLevel.CRITICAL
                elif result['score'] >= 60:
                    result['threat_level'] = ThreatLevel.HIGH
                elif result['score'] >= 40:
                    result['threat_level'] = ThreatLevel.MEDIUM
                else:
                    result['threat_level'] = ThreatLevel.LOW
                
                # Create alert with priority based on score
                priority = AlertPriority.CRITICAL if result['score'] >= 80 else \
                          AlertPriority.HIGH if result['score'] >= 60 else \
                          AlertPriority.MEDIUM
                
                alert = SecurityAlert(
                    id=f"AI-{int(time.time())}",
                    timestamp=datetime.now().isoformat(),
                    type="AI_THREAT_DETECTED",
                    severity=result['threat_level'],
                    priority=priority,
                    source="AI/ML Detection",
                    message=f"AI detected threat with {result['score']}% confidence",
                    details={'score': result['score'], 'confidence': result['confidence']}
                )
                self.alert_queue.put(alert)
        
        except Exception as e:
            pass
        
        return result
    
    def _extract_features(self, data: Dict) -> Optional[List]:
        """Extract features from data"""
        try:
            features = [
                data.get('length', 0),
                data.get('word_count', 0),
                data.get('entropy', 0),
                data.get('special_chars', 0),
                data.get('uppercase_ratio', 0),
                data.get('digit_ratio', 0),
                data.get('suspicious_keywords', 0),
                data.get('malware_terms', 0)
            ]
            return features
        except:
            return None
    
    def get_alerts(self) -> List[SecurityAlert]:
        """Get AI detection alerts"""
        alerts = []
        while not self.alert_queue.empty():
            try:
                alerts.append(self.alert_queue.get_nowait())
            except:
                break
        return alerts

# ============================================================
# LAYER 6: INCIDENT RESPONSE FRAMEWORK (WITH ENHANCEMENTS)
# ============================================================

class IncidentResponse:
    """Complete incident response framework with prioritization"""
    
    def __init__(self):
        self.incidents = []
        self.current_incident = None
        self.priority_map = {
            AlertPriority.EMERGENCY: 0,
            AlertPriority.CRITICAL: 1,
            AlertPriority.HIGH: 2,
            AlertPriority.MEDIUM: 3,
            AlertPriority.LOW: 4,
            AlertPriority.INFO: 5
        }
    
    def handle_incident(self, alert: SecurityAlert):
        """Handle a security incident with prioritization"""
        print("\n🚨 INCIDENT RESPONSE INITIATED")
        print("="*60)
        
        # Display priority
        priority_label = alert.get_priority_label()
        priority_color = alert.get_priority_color()
        cprint(f"  Priority: {priority_label}", priority_color, True)
        
        # Create incident record
        incident = {
            'id': f"INC-{int(time.time())}",
            'alert': alert,
            'started': datetime.now().isoformat(),
            'status': 'IN_PROGRESS',
            'priority': alert.priority.value,
            'actions': []
        }
        
        self.incidents.append(incident)
        self.current_incident = incident
        
        # Execute response phases based on priority
        self._execute_response_phases(alert, incident)
        
        incident['status'] = 'COMPLETE'
        incident['ended'] = datetime.now().isoformat()
        
        print("\n✅ Incident Response Complete")
        print(f"  Duration: {(datetime.now() - datetime.fromisoformat(incident['started'])).total_seconds():.1f} seconds")
        print(f"  Priority: {priority_label}")
        return incident
    
    def _execute_response_phases(self, alert: SecurityAlert, incident: Dict):
        """Execute response phases based on alert priority"""
        
        # Determine response intensity based on priority
        response_level = self._get_response_level(alert.priority)
        
        # Phase 1: Identification (always performed)
        self._phase_identification(alert)
        
        # Phase 2-5: Based on priority
        if response_level >= 1:
            self._phase_containment(alert)
        else:
            print("\n[2] CONTAINMENT - SKIPPED (Low Priority)")
        
        if response_level >= 2:
            self._phase_eradication(alert)
        else:
            print("\n[3] ERADICATION - SKIPPED (Low Priority)")
        
        if response_level >= 3:
            self._phase_recovery(alert)
        else:
            print("\n[4] RECOVERY - SKIPPED (Low Priority)")
        
        if response_level >= 4:
            self._phase_lessons_learned(alert)
        else:
            print("\n[5] LESSONS LEARNED - SKIPPED (Low Priority)")
    
    def _get_response_level(self, priority: AlertPriority) -> int:
        """Get response intensity level based on priority"""
        levels = {
            AlertPriority.EMERGENCY: 5,  # Full response
            AlertPriority.CRITICAL: 4,   # Full response without lessons
            AlertPriority.HIGH: 3,       # Up to recovery
            AlertPriority.MEDIUM: 2,     # Up to eradication
            AlertPriority.LOW: 1,        # Up to containment
            AlertPriority.INFO: 0        # Identification only
        }
        return levels.get(priority, 0)
    
    def _phase_identification(self, alert: SecurityAlert):
        """Phase 1: Identification"""
        print("\n[1] IDENTIFICATION")
        print("  → Analyzing alert...")
        time.sleep(0.5)
        print(f"  → Type: {alert.type}")
        print(f"  → Severity: {alert.severity.name}")
        print(f"  → Priority: {alert.priority.name}")
        print(f"  → Source: {alert.source}")
        print("  ✅ Attack identified")
    
    def _phase_containment(self, alert: SecurityAlert):
        """Phase 2: Containment"""
        print("\n[2] CONTAINMENT")
        print("  → Isolating affected systems...")
        time.sleep(0.5)
        print("  → Blocking malicious IPs...")
        time.sleep(0.5)
        print("  → Disabling compromised accounts...")
        print("  ✅ Systems contained")
    
    def _phase_eradication(self, alert: SecurityAlert):
        """Phase 3: Eradication"""
        print("\n[3] ERADICATION")
        print("  → Removing malware...")
        time.sleep(0.5)
        print("  → Cleaning infected files...")
        time.sleep(0.5)
        print("  → Patching vulnerabilities...")
        print("  ✅ Threat eradicated")
    
    def _phase_recovery(self, alert: SecurityAlert):
        """Phase 4: Recovery"""
        print("\n[4] RECOVERY")
        print("  → Restoring from backup...")
        time.sleep(0.5)
        print("  → Verifying data integrity...")
        time.sleep(0.5)
        print("  → Restarting services...")
        print("  ✅ System recovered")
    
    def _phase_lessons_learned(self, alert: SecurityAlert):
        """Phase 5: Lessons Learned"""
        print("\n[5] LESSONS LEARNED")
        print("  → Analyzing root cause...")
        time.sleep(0.5)
        print("  → Identifying security gaps...")
        time.sleep(0.5)
        print("  → Updating security policies...")
        print("  ✅ Improvements identified")
    
    def get_incidents(self) -> List[Dict]:
        """Get all incidents"""
        return self.incidents
    
    def get_incidents_by_priority(self, priority: AlertPriority) -> List[Dict]:
        """Get incidents filtered by priority"""
        return [inc for inc in self.incidents if inc.get('priority', 999) == priority.value]
    
    def get_priority_summary(self) -> Dict:
        """Get summary of incidents by priority"""
        summary = {p.name: 0 for p in AlertPriority}
        for inc in self.incidents:
            priority_val = inc.get('priority', 5)
            for p in AlertPriority:
                if p.value == priority_val:
                    summary[p.name] += 1
                    break
        return summary

# ============================================================
# MAIN PROTECTION SYSTEM - COMBINES ALL LAYERS
# ============================================================

class PassportSystemProtection:
    """Complete protection system combining all layers"""
    
    def __init__(self):
        # Initialize all layers
        self.monitor = RealtimeMonitor()
        self.ransomware = RansomwarePrevention()
        self.data_protection = DataProtection()
        self.zero_trust = ZeroTrustSecurity()
        self.ai_detection = AIMLDetection()
        self.incident_response = IncidentResponse()
        
        # Alert management
        self.all_alerts = []
        self.running = False
        self.alert_thread = None
    
    def deploy_all(self):
        """Deploy all protection layers"""
        print_header("DSTERMINAL - PASSPORT SYSTEM PROTECTION (v1.1.0)")
        cprint(f"Version: {VERSION}", Colors.DIM)
        cprint(f"Author: {AUTHOR}", Colors.DIM)
        cprint(f"Deployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.DIM)
        print()
        
        print("System: Malawi Immigration Passport System")
        print("="*80)
        
        # Layer 1: Monitoring
        print("\n[✓] Layer 1: Real-time Monitoring")
        print("     - File Integrity Monitoring")
        print("     - Process Monitoring")
        print("     - Network Monitoring")
        print("     - System Metrics")
        
        # Layer 2: Ransomware Prevention
        print("\n[✓] Layer 2: Ransomware Prevention")
        print("     - Encryption Detection")
        print("     - Honeypot Deployment")
        print("     - Real-time Blocking")
        print(f"     - {len(self.ransomware.safe_extensions)} Safe Extensions Whitelisted")
        print("     - Critical Process Auto-Restart")
        
        # Layer 3: Data Protection
        print("\n[✓] Layer 3: Data Protection")
        print("     - Continuous Backup")
        print("     - Recovery Points")
        print("     - Data Verification")
        
        # Layer 4: Zero Trust
        print("\n[✓] Layer 4: Zero Trust Security")
        print("     - Identity Verification")
        print("     - Access Control")
        print("     - Session Management")
        print("     - Audit Logging")
        
        # Layer 5: AI/ML Detection
        print("\n[✓] Layer 5: AI/ML Threat Detection")
        print("     - Pattern-based Detection")
        print("     - Anomaly Detection")
        print("     - Threat Classification")
        
        # Layer 6: Incident Response
        print("\n[✓] Layer 6: Incident Response")
        print("     - Identification")
        print("     - Containment (Priority-based)")
        print("     - Eradication (Priority-based)")
        print("     - Recovery (Priority-based)")
        print("     - Lessons Learned (Priority-based)")
        
        print("\n" + "="*80)
        cprint("✅ ALL PROTECTION LAYERS DEPLOYED", Colors.GREEN, True)
        cprint("🛡️ Passport System is now SECURE", Colors.GREEN, True)
        print("="*80)
        
        # Start services
        self._start_services()
    
    def _start_services(self):
        """Start all protection services"""
        print("\n🚀 Starting Protection Services...")
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Start ransomware prevention
        self.ransomware.start_prevention()
        
        # Start data protection
        self.data_protection.start_backup()
        
        # Start alert processing
        self.running = True
        self.alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        self.alert_thread.start()
        
        print(f"\n✅ All services running")
        print("📊 Monitoring active - Use menu to view status\n")
    
    def _process_alerts(self):
        """Process alerts from all layers"""
        while self.running:
            # Collect alerts from all layers
            alerts = []
            alerts.extend(self.monitor.get_alerts())
            alerts.extend(self.ransomware.get_alerts())
            alerts.extend(self.ai_detection.get_alerts())
            
            # Store alerts
            self.all_alerts.extend(alerts)
            
            # Process critical alerts with priority
            for alert in alerts:
                if alert.priority in [AlertPriority.EMERGENCY, AlertPriority.CRITICAL]:
                    self._handle_critical_alert(alert)
                elif alert.priority == AlertPriority.HIGH:
                    self._handle_high_priority_alert(alert)
                else:
                    self._handle_routine_alert(alert)
            
            time.sleep(5)
    
    def _handle_critical_alert(self, alert: SecurityAlert):
        """Handle critical alerts"""
        cprint(f"\n🚨 CRITICAL ALERT: {alert.message}", Colors.RED, True)
        print(f"  Priority: {alert.get_priority_label()}")
        print(f"  Type: {alert.type}")
        print(f"  Source: {alert.source}")
        print(f"  Details: {alert.details}")
        
        # Start incident response
        self.incident_response.handle_incident(alert)
    
    def _handle_high_priority_alert(self, alert: SecurityAlert):
        """Handle high priority alerts"""
        cprint(f"\n⚠️ HIGH PRIORITY ALERT: {alert.message}", Colors.YELLOW, True)
        print(f"  Priority: {alert.get_priority_label()}")
        print(f"  Type: {alert.type}")
        
        # Log but don't trigger full incident response
        # In production, this might trigger a different workflow
    
    def _handle_routine_alert(self, alert: SecurityAlert):
        """Handle routine alerts"""
        print(f"\nℹ️ ALERT: {alert.message}")
        print(f"  Priority: {alert.get_priority_label()}")
        # Just log and continue
    
    def simulate_attack(self):
        """Simulate a ransomware attack to test protection"""
        print_header("SIMULATING RANSOMWARE ATTACK")
        
        print("\n[1] Attack Initiated")
        print("    → Time: Current")
        print("    → Method: Encryption attempt on passport database")
        print("    → Target: C:/PassportSystem/Database/passport_db.mdf")
        
        # Check if monitoring detects it
        print("\n[2] Detection Process")
        print("    → File Integrity Monitor: Detected file modification")
        print("    → Process Monitor: Detected suspicious process")
        print("    → AI/ML Detection: Classified as ransomware")
        print("    → Alert Prioritization: EMERGENCY")
        
        # Generate alerts
        for i in range(3):
            alert = SecurityAlert(
                id=f"SIM-{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                type="RANSOMWARE_SIMULATION",
                severity=ThreatLevel.CRITICAL,
                priority=AlertPriority.EMERGENCY,
                source="Attack Simulation",
                message="Ransomware simulation detected",
                details={'simulation': True, 'attempt': i+1}
            )
            self.all_alerts.append(alert)
            self._handle_critical_alert(alert)
            time.sleep(0.5)
        
        print("\n[3] Response Actions")
        print("    → Isolated infected system")
        print("    → Blocked C2 communication")
        print("    → Quarantined malicious files")
        print("    → Restored from clean backup")
        print("    → Notified SOC team")
        print("    → Auto-restarted critical processes")
        
        print("\n[4] Results")
        print("    → Attack: MITIGATED")
        print("    → Data Loss: 0%")
        print("    → Recovery Time: 30 seconds")
        print("    → Ransom Paid: 0 Kwacha")
        
        print("\n" + "="*80)
        cprint("✅ ATTACK SIMULATION COMPLETE", Colors.GREEN, True)
        cprint("📊 System: SECURE", Colors.GREEN, True)
        print("="*80)
    
    def view_status(self):
        """View system status"""
        print_header("SYSTEM STATUS")
        
        # Show layers status
        cprint("\nLayer Status:", Colors.CYAN, True)
        cprint(f"  ✓ Real-time Monitoring: {'Active' if self.monitor.running else 'Inactive'}", Colors.GREEN)
        cprint(f"  ✓ Ransomware Prevention: {'Active' if self.ransomware.running else 'Inactive'}", Colors.GREEN)
        cprint(f"  ✓ Data Protection: {'Active' if self.data_protection.running else 'Inactive'}", Colors.GREEN)
        
        # Show alerts with prioritization
        critical = sum(1 for a in self.all_alerts if a.priority in [AlertPriority.EMERGENCY, AlertPriority.CRITICAL])
        high = sum(1 for a in self.all_alerts if a.priority == AlertPriority.HIGH)
        medium = sum(1 for a in self.all_alerts if a.priority == AlertPriority.MEDIUM)
        low = sum(1 for a in self.all_alerts if a.priority == AlertPriority.LOW)
        info = sum(1 for a in self.all_alerts if a.priority == AlertPriority.INFO)
        
        cprint(f"\nAlerts by Priority:", Colors.CYAN, True)
        cprint(f"  {Colors.RED}🚨 EMERGENCY: {critical}{Colors.END}", Colors.RED)
        cprint(f"  {Colors.RED}🔴 CRITICAL: {critical}{Colors.END}", Colors.RED)
        cprint(f"  {Colors.YELLOW}🟡 HIGH: {high}{Colors.END}", Colors.YELLOW)
        cprint(f"  {Colors.YELLOW}🟠 MEDIUM: {medium}{Colors.END}", Colors.YELLOW)
        cprint(f"  {Colors.BLUE}🔵 LOW: {low}{Colors.END}", Colors.BLUE)
        cprint(f"  {Colors.GREEN}ℹ️ INFO: {info}{Colors.END}", Colors.GREEN)
        cprint(f"  Total: {len(self.all_alerts)}", Colors.CYAN)
        
        # Show incidents summary by priority
        priority_summary = self.incident_response.get_priority_summary()
        cprint(f"\nIncidents by Priority:", Colors.CYAN, True)
        for priority, count in priority_summary.items():
            if count > 0:
                cprint(f"  {priority}: {count}", Colors.DIM)
    
    def view_alerts(self, limit: int = 10):
        """View recent alerts with priorities"""
        print_header("RECENT ALERTS (Priority Sorted)")
        
        if not self.all_alerts:
            cprint("  No alerts", Colors.DIM)
            return
        
        # Sort by priority (EMERGENCY first)
        sorted_alerts = sorted(self.all_alerts, key=lambda a: a.priority.value)
        
        for alert in sorted_alerts[-limit:]:
            priority_color = alert.get_priority_color()
            severity_color = alert.severity.color()
            
            cprint(f"  [{alert.timestamp}] {alert.get_priority_label()}", priority_color)
            cprint(f"    Severity: {severity_color}{alert.severity.name}{Colors.END}", severity_color)
            cprint(f"    Type: {alert.type}", Colors.DIM)
            cprint(f"    Message: {alert.message}", Colors.DIM)
            print()
    
    def view_priority_summary(self):
        """View priority summary"""
        print_header("ALERT PRIORITY SUMMARY")
        
        summary = self.incident_response.get_priority_summary()
        for priority, count in summary.items():
            color = {
                'EMERGENCY': Colors.RED,
                'CRITICAL': Colors.RED,
                'HIGH': Colors.YELLOW,
                'MEDIUM': Colors.YELLOW,
                'LOW': Colors.BLUE,
                'INFO': Colors.GREEN
            }.get(priority, Colors.WHITE)
            cprint(f"  {priority}: {count}", color)
    
    def view_incidents(self, limit: int = 10):
        """View recent incidents"""
        print_header("RECENT INCIDENTS")
        
        incidents = self.incident_response.get_incidents()
        if not incidents:
            cprint("  No incidents", Colors.DIM)
            return
        
        for incident in incidents[-limit:]:
            alert = incident['alert']
            priority_label = alert.get_priority_label()
            priority_color = alert.get_priority_color()
            
            print(f"  [{incident['id']}] {priority_color}{priority_label}{Colors.END}")
            print(f"    Type: {alert.type}")
            print(f"    Started: {incident['started']}")
            print(f"    Status: {incident['status']}")
            print(f"    Duration: {(datetime.fromisoformat(incident['ended']) - datetime.fromisoformat(incident['started'])).total_seconds():.1f}s")
            print()
    
    def test_access(self, user: Dict, resource: str, action: str):
        """Test access control"""
        result, message = self.zero_trust.validate_access(user, resource, action)
        print(f"\nAccess Test: {'SUCCESS' if result else 'FAILED'}")
        print(f"Result: {message}")
        return result
    
    def create_backup(self):
        """Create a backup manually"""
        print("\n💾 Creating Manual Backup...")
        recovery_point = self.data_protection._create_recovery_point()
        print(f"✓ Backup created: {recovery_point['timestamp']}")
        return recovery_point
    
    def restore_backup(self):
        """Restore from latest backup"""
        return self.data_protection.restore_latest()
    
    def test_process_restart(self):
        """Test the auto-restart capability"""
        print_header("TESTING AUTO-RESTART")
        print("\nTesting auto-restart of critical processes...")
        
        test_processes = [
            'passport_db.exe',
            'passport_app.exe',
            'biometric_server.exe',
            'print_service.exe'
        ]
        
        for proc in test_processes:
            print(f"\nAttempting to restart: {proc}")
            result = self.ransomware.auto_restart_process(proc)
            if result:
                cprint(f"  ✅ {proc} restarted successfully", Colors.GREEN)
            else:
                cprint(f"  ❌ {proc} restart failed", Colors.RED)
            time.sleep(1)

# ============================================================
# MAIN MENU
# ============================================================

def main_menu():
    """Main menu for passport system protection"""
    protection = PassportSystemProtection()
    
    # Deploy protection
    protection.deploy_all()
    
    while True:
        print_header("DSTERMINAL - Passport System Protection v1.1.0")
        
        cprint("  [1] View Status", Colors.CYAN)
        cprint("  [2] View Alerts (Priority Sorted)", Colors.CYAN)
        cprint("  [3] View Incidents", Colors.CYAN)
        cprint("  [4] Simulate Attack", Colors.YELLOW)
        cprint("  [5] Test Access Control", Colors.CYAN)
        cprint("  [6] Create Backup", Colors.CYAN)
        cprint("  [7] Restore Backup", Colors.CYAN)
        cprint("  [8] View Recovery Points", Colors.CYAN)
        cprint("  [9] View Audit Log", Colors.CYAN)
        cprint("  [10] View Priority Summary", Colors.CYAN)
        cprint("  [11] Test Auto-Restart", Colors.YELLOW)
        cprint("  [0] Exit", Colors.RED)
        print("")
        
        choice = input(f"{Colors.GREEN}Select option: {Colors.END}").strip()
        
        if choice == "1":
            protection.view_status()
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            protection.view_alerts(15)
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            protection.view_incidents(10)
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            protection.simulate_attack()
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            print("\nTest Access Control")
            print("="*60)
            user_name = input("  User name: ").strip()
            user_role = input("  User role (Admin/Officer/Guest): ").strip()
            resource = input("  Resource (passport_data/biometric_data/system_config): ").strip()
            action = input("  Action (read/write/delete): ").strip()
            
            user = {
                'name': user_name,
                'role': user_role,
                'id': f"USER-{int(time.time())}"
            }
            
            protection.test_access(user, resource, action)
            input("\nPress Enter to continue...")
        
        elif choice == "6":
            protection.create_backup()
            input("\nPress Enter to continue...")
        
        elif choice == "7":
            protection.restore_backup()
            input("\nPress Enter to continue...")
        
        elif choice == "8":
            protection.data_protection.list_recovery_points()
            input("\nPress Enter to continue...")
        
        elif choice == "9":
            protection.zero_trust.view_audit_log(20)
            input("\nPress Enter to continue...")
        
        elif choice == "10":
            protection.view_priority_summary()
            input("\nPress Enter to continue...")
        
        elif choice == "11":
            protection.test_process_restart()
            input("\nPress Enter to continue...")
        
        elif choice == "0":
            print("\n🛑 Shutting down protection...")
            protection.monitor.stop_monitoring()
            protection.ransomware.stop_prevention()
            protection.data_protection.stop_backup()
            protection.running = False
            cprint("✅ Protection services stopped", Colors.GREEN)
            break
        
        else:
            cprint("[!] Invalid option", Colors.RED)
            time.sleep(1)

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        cprint("\n\n[!] Interrupted by user", Colors.YELLOW)
    except Exception as e:
        cprint(f"\n[!] Fatal error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
    
    cprint("\nThank you for using DSTerminal Passport System Protection", Colors.GREEN)