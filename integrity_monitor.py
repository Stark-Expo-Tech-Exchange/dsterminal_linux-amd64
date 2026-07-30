#!/usr/bin/env python3
"""
DSTerminal Integrity Monitor Module
Comprehensive system integrity monitoring with real-time alerts
All reports saved to DSTerminal workspace
"""

import os
import sys
import json
import time
import shutil
import hashlib
import platform
import threading
import glob
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Try to import required packages
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color definitions
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'
    class Back:
        RED = '\033[101m'; GREEN = '\033[102m'; YELLOW = '\033[103m'
        BLUE = '\033[104m'; RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'; DIM = '\033[2m'; NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    class FileSystemEventHandler: pass
    class Observer: 
        def schedule(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
        def join(self): pass

# ==============================
# WORKSPACE MANAGEMENT
# ==============================

def get_workspace_dir() -> Path:
    """Get the DSTerminal workspace directory"""
    home = Path.home()
    workspace = home / "dsterminal_workspace"
    workspace.mkdir(exist_ok=True)
    
    # Create subdirectories for different report types
    (workspace / "integrity_reports").mkdir(exist_ok=True)
    (workspace / "network_reports").mkdir(exist_ok=True)
    (workspace / "compliance_reports").mkdir(exist_ok=True)
    (workspace / "logs").mkdir(exist_ok=True)
    (workspace / "baselines").mkdir(exist_ok=True)
    (workspace / "alerts").mkdir(exist_ok=True)
    (workspace / "quarantine").mkdir(exist_ok=True)
    (workspace / "forensic").mkdir(exist_ok=True)
    (workspace / "auto_quarantine").mkdir(exist_ok=True)
    
    return workspace

WORKSPACE = get_workspace_dir()

# ==============================
# SYSTEM INTEGRITY MONITOR
# ==============================

class SystemIntegrityMonitor:
    def __init__(self):
        # Use DSTerminal workspace directories
        self.workspace = str(WORKSPACE)
        self.db_file = os.path.join(self.workspace, "logs", "system_integrity.db")
        self.report_dir = os.path.join(self.workspace, "integrity_reports")
        self.baseline_dir = os.path.join(self.workspace, "baselines")
        self.alerts_dir = os.path.join(self.workspace, "alerts")
        self.quarantine_dir = os.path.join(self.workspace, "quarantine")
        
        # Get terminal width
        try:
            self.terminal_width = shutil.get_terminal_size().columns
        except:
            self.terminal_width = 80
        
        # Store colorama availability
        self.colorama_available = COLORAMA_AVAILABLE
        
        # Create necessary directories
        for dir_path in [self.report_dir, self.baseline_dir, self.alerts_dir, self.quarantine_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # System paths based on OS
        self.system_paths = self._get_system_paths()
        
        # Initialize alert manager
        self.alert_manager = AlertManager(self)
        self.auto_remediation = AutoRemediation(self)
        
        if self.colorama_available:
            print(f"{Fore.GREEN}✓ System Integrity Monitor initialized{Style.RESET_ALL}")
            print(f"{Fore.CYAN}✓ Workspace: {self.workspace}{Style.RESET_ALL}")
        else:
            print("✓ System Integrity Monitor initialized")
            print(f"✓ Workspace: {self.workspace}")
    
    def _get_system_paths(self):
        """Get critical system paths based on OS"""
        system = platform.system().lower()
        paths = {
            'configs': [],
            'logs': [],
            'databases': [],
            'system_files': [],
            'user_files': []
        }
        
        if system == 'windows':
            paths.update({
                'configs': [
                    os.environ.get('WINDIR', 'C:\\Windows') + '\\System32\\config',
                    os.environ.get('PROGRAMDATA', 'C:\\ProgramData'),
                    os.path.expanduser('~\\AppData\\Local'),
                    os.path.expanduser('~\\AppData\\Roaming'),
                ],
                'logs': [
                    os.environ.get('WINDIR', 'C:\\Windows') + '\\Logs',
                    os.environ.get('WINDIR', 'C:\\Windows') + '\\System32\\LogFiles',
                    os.path.expanduser('~\\AppData\\Local\\Temp'),
                ],
                'databases': [
                    os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Caches'),
                ],
                'system_files': [
                    os.environ.get('WINDIR', 'C:\\Windows') + '\\System32\\drivers\\etc\\hosts',
                    os.environ.get('WINDIR', 'C:\\Windows') + '\\System32\\config\\SAM',
                    os.environ.get('WINDIR', 'C:\\Windows') + '\\System32\\config\\SOFTWARE',
                ]
            })
        elif system == 'linux':
            paths.update({
                'configs': ['/etc', '/var/lib', '/home'],
                'logs': ['/var/log', '/var/log/syslog', '/var/log/auth.log'],
                'databases': ['/var/lib/mysql', '/var/lib/postgresql', '/var/lib/mongodb'],
                'system_files': ['/etc/passwd', '/etc/shadow', '/etc/hosts', '/etc/fstab'],
            })
        elif system == 'darwin':  # macOS
            paths.update({
                'configs': ['/etc', '/Library/Preferences', os.path.expanduser('~/Library/Preferences')],
                'logs': ['/var/log', '/Library/Logs', os.path.expanduser('~/Library/Logs')],
                'databases': ['/usr/local/var/mysql', os.path.expanduser('~/Library/Application Support')],
                'system_files': ['/etc/hosts', '/etc/passwd', '/etc/ssh/sshd_config'],
            })
        
        # Common user directories
        paths['user_files'].extend([
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Desktop'),
        ])
        
        return paths
    
    def _animated_progress_bar(self, current, total, message, width=40):
        """Animated progress bar with gradient effect"""
        percent = (current / total) * 100
        filled = int(width * current // total)
        
        if self.colorama_available:
            if percent < 30:
                bar_color = Fore.CYAN
            elif percent < 70:
                bar_color = Fore.YELLOW
            else:
                bar_color = Fore.GREEN
            
            bar = bar_color + '█' * filled + Fore.WHITE + '░' * (width - filled) + Style.RESET_ALL
        else:
            bar = '█' * filled + '░' * (width - filled)
        
        progress_text = f"{message}: [{bar}] {percent:.1f}% [{current}/{total}]"
        
        terminal_width = shutil.get_terminal_size().columns
        clean_text = progress_text.replace(Fore.CYAN, '').replace(Fore.YELLOW, '').replace(Fore.GREEN, '').replace(Fore.WHITE, '').replace(Style.RESET_ALL, '')
        text_width = len(clean_text)
        padding = max(0, (terminal_width - text_width) // 2)
        
        print(f"\r{' ' * padding}{progress_text}", end='', flush=True)
        
        if current == total:
            print()
    
    def scan_system(self, scan_type='all'):
        """Scan system for files, configs, logs, and databases"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'hostname': platform.node(),
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.machine(),
            },
            'files': [],
            'configs': [],
            'logs': [],
            'databases': [],
            'critical_files': []
        }
        
        if self.colorama_available:
            print(f"{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}{'SYSTEM SCAN INITIALIZED'.center(self.terminal_width)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}\n")
        else:
            print("\n" + "=" * self.terminal_width)
            print("SYSTEM SCAN INITIALIZED".center(self.terminal_width))
            print("=" * self.terminal_width + "\n")
        
        # Scan different categories
        if scan_type in ['all', 'configs']:
            self._scan_category('configs', results)
        
        if scan_type in ['all', 'logs']:
            self._scan_category('logs', results)
        
        if scan_type in ['all', 'databases']:
            self._scan_category('databases', results)
        
        if scan_type in ['all', 'system']:
            self._scan_category('system_files', results, 'critical_files')
        
        if scan_type in ['all', 'user']:
            self._scan_category('user_files', results, 'files')
        
        # Save scan results to workspace
        scan_file = os.path.join(self.report_dir, f'scan_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(scan_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _scan_category(self, category, results, target_key=None):
        """Scan a specific category with progress bar"""
        if target_key is None:
            target_key = category
        
        category_styles = {
            'configs': {'icon': '⚙️', 'title': 'CONFIGURATION FILES'},
            'logs': {'icon': '📋', 'title': 'LOG FILES'},
            'databases': {'icon': '🗄️', 'title': 'DATABASES'},
            'system_files': {'icon': '🔒', 'title': 'CRITICAL SYSTEM FILES'},
            'user_files': {'icon': '👤', 'title': 'USER FILES'}
        }
        
        style = category_styles.get(category, {'icon': '📁', 'title': category.upper()})
        
        if self.colorama_available:
            print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{style['icon']}  SCANNING {style['title']}  {style['icon']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        else:
            print(f"\n{'─' * 60}")
            print(f"SCANNING {style['title']}")
            print(f"{'─' * 60}")
        
        count = 0
        total_paths = len(self.system_paths.get(category, []))
        
        for i, path in enumerate(self.system_paths.get(category, []), 1):
            if os.path.exists(path):
                self._animated_progress_bar(i, total_paths, f"Scanning {category}", 40)
                count += self._scan_directory(path, results[target_key], category)
        
        terminal_width = shutil.get_terminal_size().columns
        print(f"\r{' ' * terminal_width}", end='\r')
        
        if self.colorama_available:
            print(f"\n{Fore.GREEN}✓ Found {count} {category}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")
        else:
            print(f"\n✓ Found {count} {category}")
            print(f"{'─' * 60}\n")
        
        return count
    
    def _scan_directory(self, directory, results_list, category, max_depth=3):
        """Recursively scan a directory with progress"""
        count = 0
        try:
            for root, dirs, files in os.walk(directory):
                depth = root.replace(directory, '').count(os.sep)
                if depth > max_depth:
                    dirs[:] = []
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        file_info = self._get_file_info(file_path)
                        file_info['category'] = category
                        results_list.append(file_info)
                        count += 1
                        
                        if count % 100 == 0 and self.colorama_available:
                            print(f"\r  {Fore.CYAN}Processed {count} files...{Style.RESET_ALL}", end='', flush=True)
                        
                        if len(results_list) > 10000:
                            return count
        except (PermissionError, OSError) as e:
            if self.colorama_available:
                print(f"\n{Fore.RED}Permission denied: {directory}{Style.RESET_ALL}")
        
        return count
    
    def _get_file_info(self, file_path):
        """Get detailed file information"""
        try:
            stat = os.stat(file_path)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'hash': self._calculate_hash(file_path),
                'permissions': self._get_file_permissions(file_path),
                'owner': self._get_file_owner(file_path),
                'extension': os.path.splitext(file_path)[1],
                'is_hidden': self._is_hidden_file(file_path)
            }
        except Exception as e:
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'error': str(e)
            }
    
    def _calculate_hash(self, file_path):
        """Calculate SHA-256 hash of file"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return None
    
    def _get_file_permissions(self, file_path):
        """Get file permissions (platform-specific)"""
        if platform.system().lower() == 'windows':
            try:
                return 'readonly' if not os.access(file_path, os.W_OK) else 'read-write'
            except:
                return 'unknown'
        else:
            try:
                stat = os.stat(file_path)
                return oct(stat.st_mode)[-3:]
            except:
                return 'unknown'
    
    def _get_file_owner(self, file_path):
        """Get file owner"""
        try:
            import pwd
            stat = os.stat(file_path)
            return pwd.getpwuid(stat.st_uid).pw_name
        except:
            try:
                import getpass
                return getpass.getuser()
            except:
                return 'unknown'
    
    def _is_hidden_file(self, file_path):
        """Check if file is hidden"""
        if platform.system().lower() == 'windows':
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(file_path)
                return attrs != -1 and bool(attrs & 2)
            except:
                return os.path.basename(file_path).startswith('.')
        else:
            return os.path.basename(file_path).startswith('.')
    
    def create_baseline(self, scan_results=None):
        """Create a baseline of system state and save to workspace"""
        if scan_results is None:
            scan_results = self.scan_system()
        
        baseline = {
            'created': datetime.now().isoformat(),
            'workspace': self.workspace,
            'system_info': scan_results['system_info'],
            'files': scan_results['files'],
            'configs': scan_results['configs'],
            'logs': scan_results['logs'],
            'databases': scan_results['databases'],
            'critical_files': scan_results['critical_files']
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        baseline_file = os.path.join(self.baseline_dir, f'baseline_{timestamp}.json')
        
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, default=str)
        
        # Also save as latest baseline
        latest_file = os.path.join(self.baseline_dir, 'latest_baseline.json')
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, default=str)
        
        if self.colorama_available:
            print(f"\n{Fore.GREEN}✓ Baseline created successfully{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Saved to: {baseline_file}{Style.RESET_ALL}")
        else:
            print(f"\n✓ Baseline created successfully")
            print(f"Saved to: {baseline_file}")
        
        return baseline
    
    def _load_baseline(self):
        """Load the latest baseline"""
        latest_file = os.path.join(self.baseline_dir, 'latest_baseline.json')
        if os.path.exists(latest_file):
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def check_integrity(self, scan_results=None):
        """Check system integrity against baseline"""
        if scan_results is None:
            scan_results = self.scan_system()
        
        baseline = self._load_baseline()
        
        if not baseline:
            if self.colorama_available:
                print(f"{Fore.YELLOW}No baseline found. Creating initial baseline...{Style.RESET_ALL}")
            else:
                print("No baseline found. Creating initial baseline...")
            self.create_baseline(scan_results)
            return None
        
        if self.colorama_available:
            print(f"\n{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}{'INTEGRITY CHECK IN PROGRESS'.center(self.terminal_width)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}\n")
        else:
            print("\n" + "=" * self.terminal_width)
            print("INTEGRITY CHECK IN PROGRESS".center(self.terminal_width))
            print("=" * self.terminal_width + "\n")
        
        changes = {
            'new_files': [],
            'modified_files': [],
            'deleted_files': [],
            'permission_changes': []
        }
        
        # Create lookup dictionaries
        all_baseline = {}
        all_current = {}
        
        for category in ['files', 'configs', 'logs', 'databases', 'critical_files']:
            for item in baseline.get(category, []):
                all_baseline[item['path']] = item
            for item in scan_results.get(category, []):
                all_current[item['path']] = item
        
        # Check for modifications and deletions
        total_items = len(all_baseline)
        for i, (path, baseline_info) in enumerate(all_baseline.items(), 1):
            self._animated_progress_bar(i, total_items, "Analyzing files")
            
            if path not in all_current:
                changes['deleted_files'].append({
                    'path': path,
                    'baseline_info': baseline_info,
                    'severity': 'HIGH' if baseline_info.get('category') == 'system' else 'MEDIUM'
                })
                continue
            
            current_info = all_current[path]
            
            # Check hash
            if baseline_info.get('hash') != current_info.get('hash'):
                change_type = self._analyze_change(baseline_info, current_info)
                changes['modified_files'].append({
                    'path': path,
                    'baseline': baseline_info,
                    'current': current_info,
                    'change_type': change_type,
                    'severity': self._determine_severity(path, 'modified')
                })
            
            # Check permissions
            if baseline_info.get('permissions') != current_info.get('permissions'):
                changes['permission_changes'].append({
                    'path': path,
                    'old_perms': baseline_info.get('permissions'),
                    'new_perms': current_info.get('permissions')
                })
        
        # Check for new files
        for path, current_info in all_current.items():
            if path not in all_baseline:
                changes['new_files'].append({
                    'path': path,
                    'current_info': current_info,
                    'severity': self._determine_severity(path, 'new')
                })
        
        # Save integrity check results
        integrity_result_file = os.path.join(self.report_dir, f'integrity_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(integrity_result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'workspace': self.workspace,
                'changes': changes,
                'summary': {
                    'new_files': len(changes['new_files']),
                    'modified_files': len(changes['modified_files']),
                    'deleted_files': len(changes['deleted_files']),
                    'permission_changes': len(changes['permission_changes'])
                }
            }, f, indent=2, default=str)
        
        return changes
    
    def _analyze_change(self, baseline, current):
        """Analyze the type of change made to a file"""
        reasons = []
        
        if baseline.get('size') != current.get('size'):
            size_diff = current.get('size', 0) - baseline.get('size', 0)
            if size_diff > 0:
                reasons.append(f"Size increased by {self._format_size(size_diff)}")
            else:
                reasons.append(f"Size decreased by {self._format_size(abs(size_diff))}")
        
        if baseline.get('extension') != current.get('extension'):
            reasons.append(f"Extension changed from {baseline.get('extension')} to {current.get('extension')}")
        
        if not reasons:
            reasons.append("Content modified")
        
        return reasons
    
    def _determine_severity(self, path, change_type):
        """Determine severity of change"""
        path_lower = path.lower()
        
        if any(critical in path_lower for critical in ['system32', 'etc', 'kernel', 'boot', 'windows\\system']):
            return 'CRITICAL'
        elif any(sensitive in path_lower for sensitive in ['config', 'password', 'shadow', 'sam']):
            return 'HIGH'
        elif any(important in path_lower for important in ['log', 'database', 'data']):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def generate_report(self, changes=None, scan_results=None):
        """Generate a text report and save to workspace"""
        if scan_results is None:
            scan_results = self.scan_system()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.report_dir, f'integrity_report_{timestamp}.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DSTERMINAL SYSTEM INTEGRITY REPORT".center(80) + "\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Workspace: {self.workspace}\n")
            f.write(f"Hostname: {scan_results['system_info']['hostname']}\n")
            f.write(f"OS: {scan_results['system_info']['os']} {scan_results['system_info']['os_version']}\n")
            f.write(f"Architecture: {scan_results['system_info']['architecture']}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("SCAN SUMMARY".center(80) + "\n")
            f.write("=" * 80 + "\n\n")
            
            total_files = (len(scan_results['critical_files']) + len(scan_results['configs']) + 
                          len(scan_results['logs']) + len(scan_results['databases']) + 
                          len(scan_results['files']))
            
            f.write(f"Total Files Scanned: {total_files}\n")
            f.write(f"  Critical System Files: {len(scan_results['critical_files'])}\n")
            f.write(f"  Configuration Files: {len(scan_results['configs'])}\n")
            f.write(f"  Log Files: {len(scan_results['logs'])}\n")
            f.write(f"  Databases: {len(scan_results['databases'])}\n")
            f.write(f"  User Files: {len(scan_results['files'])}\n\n")
            
            if changes:
                f.write("=" * 80 + "\n")
                f.write("INTEGRITY FINDINGS".center(80) + "\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"New Files: {len(changes.get('new_files', []))}\n")
                f.write(f"Modified Files: {len(changes.get('modified_files', []))}\n")
                f.write(f"Deleted Files: {len(changes.get('deleted_files', []))}\n")
                f.write(f"Permission Changes: {len(changes.get('permission_changes', []))}\n\n")
                
                if changes.get('modified_files'):
                    f.write("MODIFIED FILES:\n")
                    f.write("-" * 40 + "\n")
                    for item in changes['modified_files'][:20]:
                        f.write(f"  {item['path']}\n")
                        for reason in item.get('change_type', []):
                            f.write(f"    - {reason}\n")
                        f.write(f"    Severity: {item.get('severity', 'LOW')}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write(f"Report saved to: {report_file}\n")
            f.write("=" * 80 + "\n")
        
        if self.colorama_available:
            print(f"{Fore.GREEN}✓ Text report saved to workspace: {report_file}{Style.RESET_ALL}")
        else:
            print(f"✓ Text report saved to workspace: {report_file}")
        
        return report_file
    
    def generate_json_report(self, changes=None, scan_results=None):
        """Generate a JSON report and save to workspace"""
        if scan_results is None:
            scan_results = self.scan_system()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.report_dir, f'integrity_report_{timestamp}.json')
        
        report_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'workspace': self.workspace,
                'version': '3.1.113'
            },
            'system_info': scan_results['system_info'],
            'summary': {
                'total_files': (len(scan_results['critical_files']) + len(scan_results['configs']) + 
                               len(scan_results['logs']) + len(scan_results['databases']) + 
                               len(scan_results['files'])),
                'categories': {
                    'critical_files': len(scan_results['critical_files']),
                    'configs': len(scan_results['configs']),
                    'logs': len(scan_results['logs']),
                    'databases': len(scan_results['databases']),
                    'user_files': len(scan_results['files'])
                }
            }
        }
        
        if changes:
            report_data['changes'] = changes
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        if self.colorama_available:
            print(f"{Fore.GREEN}✓ JSON report saved to workspace: {report_file}{Style.RESET_ALL}")
        else:
            print(f"✓ JSON report saved to workspace: {report_file}")
        
        return report_file
    
    def generate_pdf_report(self, changes=None, scan_results=None):
        """Generate a PDF report and save to workspace"""
        if not PDF_AVAILABLE:
            if self.colorama_available:
                print(f"{Fore.YELLOW}fpdf2 not installed. Install with: pip install fpdf2{Style.RESET_ALL}")
            else:
                print("fpdf2 not installed. Install with: pip install fpdf2")
            return None
        
        if scan_results is None:
            scan_results = self.scan_system()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.report_dir, f'integrity_report_{timestamp}.pdf')
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)
        
        # Title
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, "DSTerminal System Integrity Report", 0, 1, 'C')
        pdf.ln(10)
        
        # Metadata
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, "Report Metadata", 0, 1, 'L')
        pdf.set_font("Helvetica", size=10)
        pdf.cell(40, 6, f"Generated:", 0, 0)
        pdf.cell(0, 6, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, 1)
        pdf.cell(40, 6, f"Workspace:", 0, 0)
        pdf.cell(0, 6, self.workspace, 0, 1)
        pdf.cell(40, 6, f"Hostname:", 0, 0)
        pdf.cell(0, 6, scan_results['system_info']['hostname'], 0, 1)
        pdf.cell(40, 6, f"OS:", 0, 0)
        pdf.cell(0, 6, f"{scan_results['system_info']['os']} {scan_results['system_info']['os_version']}", 0, 1)
        pdf.ln(5)
        
        # Summary
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, "Scan Summary", 0, 1, 'L')
        pdf.set_font("Helvetica", size=10)
        
        total_files = (len(scan_results['critical_files']) + len(scan_results['configs']) + 
                      len(scan_results['logs']) + len(scan_results['databases']) + 
                      len(scan_results['files']))
        
        pdf.cell(0, 6, f"Total Files Scanned: {total_files}", 0, 1)
        pdf.cell(0, 6, f"  Critical System Files: {len(scan_results['critical_files'])}", 0, 1)
        pdf.cell(0, 6, f"  Configuration Files: {len(scan_results['configs'])}", 0, 1)
        pdf.cell(0, 6, f"  Log Files: {len(scan_results['logs'])}", 0, 1)
        pdf.cell(0, 6, f"  Databases: {len(scan_results['databases'])}", 0, 1)
        pdf.cell(0, 6, f"  User Files: {len(scan_results['files'])}", 0, 1)
        pdf.ln(5)
        
        # Findings
        if changes:
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, "Integrity Findings", 0, 1, 'L')
            pdf.set_font("Helvetica", size=10)
            
            new_count = len(changes.get('new_files', []))
            modified_count = len(changes.get('modified_files', []))
            deleted_count = len(changes.get('deleted_files', []))
            
            pdf.cell(0, 6, f"New Files: {new_count}", 0, 1)
            pdf.cell(0, 6, f"Modified Files: {modified_count}", 0, 1)
            pdf.cell(0, 6, f"Deleted Files: {deleted_count}", 0, 1)
            
            severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for change_type in ['new_files', 'modified_files', 'deleted_files']:
                for item in changes.get(change_type, []):
                    severity = item.get('severity', 'LOW')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            pdf.ln(3)
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(0, 6, "Severity Breakdown:", 0, 1)
            pdf.set_font("Helvetica", size=9)
            for severity, count in severity_counts.items():
                if count > 0:
                    pdf.cell(30, 5, f"  {severity}:", 0, 0)
                    pdf.cell(0, 5, str(count), 0, 1)
            pdf.ln(5)
        
        # Footer
        pdf.set_y(-30)
        pdf.set_font("Helvetica", 'I', 8)
        pdf.cell(0, 5, f"Generated by DSTerminal Integrity Monitor v3.1.113", 0, 1, 'C')
        pdf.cell(0, 5, f"Report: {os.path.basename(report_file)}", 0, 1, 'C')
        pdf.cell(0, 5, f"Workspace: {self.workspace}", 0, 1, 'C')
        
        try:
            pdf.output(report_file)
            if self.colorama_available:
                print(f"{Fore.GREEN}✓ PDF report saved to workspace: {report_file}{Style.RESET_ALL}")
            else:
                print(f"✓ PDF report saved to workspace: {report_file}")
            return report_file
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Failed to generate PDF: {e}{Style.RESET_ALL}")
            else:
                print(f"Failed to generate PDF: {e}")
            return None
    
    def generate_all_reports(self, changes, scan_results=None):
        """Generate all report formats and save to workspace"""
        if scan_results is None:
            scan_results = self.scan_system()
        
        reports = {}
        reports['txt'] = self.generate_report(changes, scan_results)
        reports['json'] = self.generate_json_report(changes, scan_results)
        reports['pdf'] = self.generate_pdf_report(changes, scan_results)
        
        if self.colorama_available:
            print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ ALL REPORTS SAVED TO WORKSPACE{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Workspace location: {self.workspace}/integrity_reports/{Style.RESET_ALL}")
        else:
            print("\n" + "="*60)
            print("✓ ALL REPORTS SAVED TO WORKSPACE")
            print("="*60)
            print(f"Workspace location: {self.workspace}/integrity_reports/")
        
        return reports
    
    def full_integrity_check(self):
        """Perform full system integrity check and save reports to workspace"""
        scan_results = self.scan_system()
        changes = self.check_integrity(scan_results)
        
        if changes:
            self._display_changes(changes)
            self.generate_all_reports(changes, scan_results)
            
            if self.colorama_available:
                print(f"\n{Fore.GREEN}✓ Full integrity check complete{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Reports saved to: {self.report_dir}{Style.RESET_ALL}")
            else:
                print(f"\n✓ Full integrity check complete")
                print(f"Reports saved to: {self.report_dir}")
        else:
            if self.colorama_available:
                print(f"\n{Fore.GREEN}System integrity is intact. No changes detected.{Style.RESET_ALL}")
            else:
                print(f"\nSystem integrity is intact. No changes detected.")
        
        return changes
    
    def _display_changes(self, changes):
        """Display changes in console"""
        if self.colorama_available:
            print(f"\n{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}{'INTEGRITY CHECK RESULTS'.center(self.terminal_width)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}\n")
            
            print(f"{Fore.YELLOW}Change Summary:{Style.RESET_ALL}")
            print(f"  New Files: {Fore.GREEN if len(changes['new_files'])==0 else Fore.RED}{len(changes['new_files'])}{Style.RESET_ALL}")
            print(f"  Modified: {Fore.GREEN if len(changes['modified_files'])==0 else Fore.RED}{len(changes['modified_files'])}{Style.RESET_ALL}")
            print(f"  Deleted: {Fore.GREEN if len(changes['deleted_files'])==0 else Fore.RED}{len(changes['deleted_files'])}{Style.RESET_ALL}")
            print(f"  Permission Changes: {Fore.GREEN if len(changes['permission_changes'])==0 else Fore.YELLOW}{len(changes['permission_changes'])}{Style.RESET_ALL}")
        else:
            print("\n" + "=" * self.terminal_width)
            print("INTEGRITY CHECK RESULTS".center(self.terminal_width))
            print("=" * self.terminal_width + "\n")
            print("Change Summary:")
            print(f"  New Files: {len(changes['new_files'])}")
            print(f"  Modified: {len(changes['modified_files'])}")
            print(f"  Deleted: {len(changes['deleted_files'])}")
            print(f"  Permission Changes: {len(changes['permission_changes'])}")
        
        # Show critical changes
        critical_changes = []
        for change_type in ['new_files', 'modified_files', 'deleted_files']:
            for item in changes[change_type]:
                if item.get('severity') in ['CRITICAL', 'HIGH']:
                    critical_changes.append((change_type, item))
        
        if critical_changes:
            if self.colorama_available:
                print(f"\n{Fore.RED}{Style.BRIGHT}CRITICAL/HIGH SEVERITY CHANGES:{Style.RESET_ALL}")
                for change_type, item in critical_changes[:5]:
                    severity_color = Fore.RED if item.get('severity') == 'CRITICAL' else Fore.YELLOW
                    print(f"  {severity_color}[{item.get('severity')}]{Style.RESET_ALL} {item['path']}")
            else:
                print("\nCRITICAL/HIGH SEVERITY CHANGES:")
                for change_type, item in critical_changes[:5]:
                    print(f"  [{item.get('severity')}] {item['path']}")

# ==============================
# ALERT MANAGER
# ==============================

class AlertManager:
    """Manages real-time alerts"""
    
    def __init__(self, integrity_monitor):
        self.integrity_monitor = integrity_monitor
        self.alerts = []
        self.running = False
        self.observer = None
        self.monitored_paths = []
        self._saving = False
        self._printing_error = False
        
        self.alerts_file = os.path.join(integrity_monitor.workspace, "alerts", "alerts.json")
        self.colorama_available = integrity_monitor.colorama_available
        
        # Create alerts directory
        os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
        
        # Load existing alerts
        self._load_alerts()
    
    def _load_alerts(self):
        """Load existing alerts from file"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        self.alerts = json.loads(content)
        except json.JSONDecodeError as e:
            backup_file = self.alerts_file + ".backup"
            try:
                shutil.copy2(self.alerts_file, backup_file)
                if self.colorama_available:
                    print(f"{Fore.YELLOW}⚠ Corrupted alerts file backed up to {backup_file}{Style.RESET_ALL}")
            except:
                pass
            self.alerts = []
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.YELLOW}⚠ Error loading alerts: {e}{Style.RESET_ALL}")
            self.alerts = []
    
    def _save_alerts(self):
        """Save alerts to file with atomic write"""
        if hasattr(self, '_saving') and self._saving:
            return
        self._saving = True
        
        try:
            safe_alerts = []
            for alert in self.alerts:
                safe_alert = {}
                for key, value in alert.items():
                    if hasattr(value, 'isoformat'):
                        safe_alert[key] = value.isoformat()
                    elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        safe_alert[key] = value
                    else:
                        safe_alert[key] = str(value)
                safe_alerts.append(safe_alert)
            
            os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
            
            temp_file = self.alerts_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(safe_alerts, f, indent=2, ensure_ascii=False, default=str)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_file, self.alerts_file)
            
        except Exception as e:
            if not hasattr(self, '_printing_error') or not self._printing_error:
                self._printing_error = True
                if self.colorama_available:
                    print(f"{Fore.RED}Failed to save alerts: {e}{Style.RESET_ALL}")
                else:
                    print(f"Failed to save alerts: {e}")
                self._printing_error = False
        finally:
            self._saving = False
    
    def start_monitoring(self, paths=None):
        """Start real-time monitoring of system-critical locations"""
        if not WATCHDOG_AVAILABLE:
            if self.colorama_available:
                print(f"{Fore.RED}Watchdog not installed. Install with: pip install watchdog{Style.RESET_ALL}")
            else:
                print("Watchdog not installed. Install with: pip install watchdog")
            return
        
        if self.running:
            if self.colorama_available:
                print(f"{Fore.YELLOW}Monitoring already running{Style.RESET_ALL}")
            else:
                print("Monitoring already running")
            return
        
        # Default to user-accessible system-critical paths
        if paths is None:
            system = platform.system().lower()
            if system == 'windows':
                paths = [
                    os.path.expanduser('~\\AppData\\Local'),
                    os.path.expanduser('~\\AppData\\Roaming'),
                    os.path.expanduser('~\\Documents'),
                    os.path.expanduser('~\\Downloads'),
                    os.path.expanduser('~\\Desktop'),
                    'C:\\Windows\\Temp',
                    os.environ.get('TEMP', 'C:\\Temp'),
                ]
                # Only add System32 if running as admin
                try:
                    import ctypes
                    if ctypes.windll.shell32.IsUserAnAdmin():
                        paths.append(os.environ.get('WINDIR', 'C:\\Windows') + '\\System32')
                        paths.append(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'))
                except:
                    pass
            elif system == 'linux':
                paths = [
                    '/etc',
                    '/var/log',
                    '/tmp',
                    os.path.expanduser('~'),
                    '/usr/local',
                ]
            elif system == 'darwin':  # macOS
                paths = [
                    '/etc',
                    '/var/log',
                    '/tmp',
                    os.path.expanduser('~'),
                    '/usr/local',
                ]
            else:
                paths = [os.path.expanduser('~')]
        
        # Filter out paths that don't exist or can't be accessed
        valid_paths = []
        for path in paths:
            if os.path.exists(path):
                try:
                    # Test if we can access the directory
                    os.listdir(path)
                    valid_paths.append(path)
                except (PermissionError, OSError):
                    if self.colorama_available:
                        print(f"{Fore.YELLOW}⚠ Skipping {path} (access denied){Style.RESET_ALL}")
                    else:
                        print(f"⚠ Skipping {path} (access denied)")
        
        if not valid_paths:
            if self.colorama_available:
                print(f"{Fore.RED}No accessible paths to monitor!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Try running as administrator for system-wide monitoring{Style.RESET_ALL}")
            else:
                print("No accessible paths to monitor!")
                print("Try running as administrator for system-wide monitoring")
            return
        
        self.monitored_paths = valid_paths
        self.running = True
        
        self.observer = Observer()
        handler = RealTimeHandler(self)
        
        success_count = 0
        for path in valid_paths:
            try:
                self.observer.schedule(handler, path, recursive=True)
                if self.colorama_available:
                    print(f"{Fore.GREEN}✓ Monitoring: {path}{Style.RESET_ALL}")
                else:
                    print(f"✓ Monitoring: {path}")
                success_count += 1
            except Exception as e:
                if self.colorama_available:
                    print(f"{Fore.RED}✗ Failed to monitor {path}: {e}{Style.RESET_ALL}")
                else:
                    print(f"✗ Failed to monitor {path}: {e}")
        
        if success_count > 0 and self.observer:
            self.observer.start()
            if self.colorama_available:
                print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}✅ REAL-TIME MONITORING STARTED{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Monitoring {success_count} critical system locations{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Press Ctrl+C to stop monitoring{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
            else:
                print("\n✅ REAL-TIME MONITORING STARTED")
                print(f"Monitoring {success_count} critical system locations")
                print("Press Ctrl+C to stop monitoring\n")
        
        if success_count < len(valid_paths):
            if self.colorama_available:
                print(f"{Fore.YELLOW}⚠ Some paths couldn't be monitored. Try running as administrator.{Style.RESET_ALL}")
            else:
                print("⚠ Some paths couldn't be monitored. Try running as administrator.")

        # ==============================
        # MAIN MENU
        # ==============================

    def main_menu():
        """Interactive main menu for integrity monitor"""
        monitor = SystemIntegrityMonitor()
        
        if monitor.colorama_available:
            print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}{'INTEGRITY MONITOR - MAIN MENU'.center(60)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        else:
            print("\n" + "=" * 60)
            print("INTEGRITY MONITOR - MAIN MENU".center(60))
            print("=" * 60)
        
        while True:
            print(f"\n{Fore.YELLOW if monitor.colorama_available else ''}Available Operations:{Style.RESET_ALL if monitor.colorama_available else ''}")
            print("  1. Full System Scan")
            print("  2. Create Baseline")
            print("  3. Check Integrity (Compare with Baseline)")
            print("  4. Full Integrity Check (Scan + Compare + Report)")
            print("  5. Generate Reports (from latest scan)")
            print("  6. Start Real-time Monitoring")
            print("  7. View Recent Alerts")
            print("  8. View Remediation History")
            print("  9. Clear Alert History")
            print("  0. Exit")
            
            choice = input(f"\n{Fore.GREEN if monitor.colorama_available else ''}Select operation: {Style.RESET_ALL if monitor.colorama_available else ''}").strip()
            
            if choice == "1":
                scan_type = input("Scan type (all/configs/logs/databases/system/user): ").strip() or "all"
                monitor.scan_system(scan_type)
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                monitor.create_baseline()
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                monitor.check_integrity()
                input("\nPress Enter to continue...")
                
            elif choice == "4":
                monitor.full_integrity_check()
                input("\nPress Enter to continue...")
                
            elif choice == "5":
                # Generate reports from latest scan
                scan_results = monitor.scan_system()
                changes = monitor.check_integrity(scan_results)
                if changes:
                    monitor.generate_all_reports(changes, scan_results)
                else:
                    monitor.generate_report(None, scan_results)
                    monitor.generate_json_report(None, scan_results)
                input("\nPress Enter to continue...")
                
            elif choice == "6":
                monitor.alert_manager.start_monitoring()
                input("\nPress Enter to continue...")
                
            elif choice == "7":
                alerts = monitor.alert_manager.get_alerts(limit=50)
                # Filter out alerts from the alerts directory
                filtered_alerts = [a for a in alerts if 'alerts' not in str(a.get('path', ''))]
                
                if filtered_alerts:
                    print(f"\n{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                    print(f"{Fore.MAGENTA if monitor.colorama_available else ''}RECENT ALERTS{Style.RESET_ALL if monitor.colorama_available else ''}")
                    print(f"{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                    for alert in filtered_alerts[-20:]:
                        time_str = alert.get('timestamp', datetime.now()).isoformat()[:19] if hasattr(alert.get('timestamp'), 'isoformat') else str(alert.get('timestamp', ''))[:19]
                        severity = alert.get('severity', 'LOW')
                        alert_type = alert.get('type', 'UNKNOWN')
                        path = alert.get('path', 'Unknown')
                        print(f"  [{time_str}] {severity}: {alert_type} - {path}")
                else:
                    print("\nNo alerts found.")
                input("\nPress Enter to continue...")
                
            elif choice == "8":
                history = monitor.auto_remediation.get_remediation_history(20)
                if history:
                    print(f"\n{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                    print(f"{Fore.MAGENTA if monitor.colorama_available else ''}REMEDIATION HISTORY{Style.RESET_ALL if monitor.colorama_available else ''}")
                    print(f"{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                    for entry in history:
                        time_str = entry.get('timestamp', '')[:19]
                        action = entry.get('action_taken', 'UNKNOWN')
                        success = "✓" if entry.get('success') else "✗"
                        path = entry.get('violation', {}).get('path', 'Unknown')
                        print(f"  [{time_str}] {success} {action}: {path}")
                else:
                    print("\nNo remediation history found.")
                input("\nPress Enter to continue...")
                
            elif choice == "9":
                confirm = input("Clear all alert history? (y/N): ").strip().lower()
                if confirm == 'y':
                    monitor.alert_manager.alerts = []
                    monitor.alert_manager._save_alerts()
                    if monitor.colorama_available:
                        print(f"{Fore.GREEN}✓ Alert history cleared{Style.RESET_ALL}")
                    else:
                        print("✓ Alert history cleared")
                input("\nPress Enter to continue...")
                
            elif choice == "0":
                if monitor.alert_manager.running:
                    monitor.alert_manager.stop_monitoring()
                if monitor.colorama_available:
                    print(f"\n{Fore.GREEN}Exiting Integrity Monitor...{Style.RESET_ALL}")
                else:
                    print("\nExiting Integrity Monitor...")
                break
                
            else:
                if monitor.colorama_available:
                    print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                else:
                    print("Invalid choice. Please try again.")
                time.sleep(1)
                        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.running = False
        if self.colorama_available:
            print(f"{Fore.YELLOW}Real-time monitoring stopped{Style.RESET_ALL}")
        else:
            print("Real-time monitoring stopped")
    
    def add_alert(self, alert_type, path, severity="LOW", **kwargs):
        """Add a security alert"""
        try:
            alert = {
                'timestamp': datetime.now(),
                'type': alert_type,
                'path': str(path),
                'severity': severity,
            }
            
            if 'size' in kwargs and kwargs['size'] is not None:
                alert['size'] = kwargs['size']
            if 'src_path' in kwargs:
                alert['src_path'] = str(kwargs['src_path'])
            if 'dest_path' in kwargs:
                alert['dest_path'] = str(kwargs['dest_path'])
            
            self.alerts.append(alert)
            
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-1000:]
            
            self._save_alerts()
            self._display_alert(alert)
            
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Failed to add alert: {e}{Style.RESET_ALL}")
            else:
                print(f"Failed to add alert: {e}")
    
    def _display_alert(self, alert):
        """Display alert in real-time - excludes alerts directory"""
        path = alert.get('path', '')
        
        # Don't show alerts for files in the alerts directory
        if 'alerts' in path or '.tmp' in path or '.backup' in path:
            return
        
        severity_colors = {
            'CRITICAL': Fore.RED + Style.BRIGHT,
            'HIGH': Fore.YELLOW + Style.BRIGHT,
            'MEDIUM': Fore.CYAN,
            'LOW': Fore.GREEN
        }
        
        severity = alert.get('severity', 'LOW')
        color = severity_colors.get(severity, Fore.WHITE)
        
        print(f"\n{Fore.RED}{'!' * 60}{Style.RESET_ALL}")
        print(f"{color}🔔 SECURITY ALERT [{severity}]{Style.RESET_ALL}")
        print(f"{Fore.RED}{'!' * 60}{Style.RESET_ALL}")
        
        timestamp = alert.get('timestamp', datetime.now())
        if hasattr(timestamp, 'isoformat'):
            time_str = timestamp.isoformat()[:19]
        else:
            time_str = str(timestamp)[:19]
        
        print(f"Time: {time_str}")
        print(f"Type: {alert.get('type', 'UNKNOWN')}")
        
        if alert.get('type') == 'MOVED':
            print(f"From: {alert.get('src_path', 'Unknown')}")
            print(f"To: {alert.get('dest_path', 'Unknown')}")
        else:
            print(f"File: {alert.get('path', 'Unknown')}")
        
        if alert.get('size'):
            size = alert['size']
            if isinstance(size, (int, float)):
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                print(f"Size: {size_str}")
        
        print(f"{color}{'!' * 60}{Style.RESET_ALL}\n")
        
        
    def get_alerts(self, severity=None, limit=100):
        """Get recent alerts"""
        if severity:
            return [a for a in self.alerts if a.get('severity') == severity][-limit:]
        return self.alerts[-limit:]

# ==============================
# REAL-TIME HANDLER
# ==============================

class RealTimeHandler(FileSystemEventHandler):
    """Handles real-time file system events"""
    
    def __init__(self, alert_manager):
        self.alert_manager = alert_manager
        self.suspicious_extensions = ['.exe', '.dll', '.vbs', '.ps1', '.sh', '.bin', '.scr']
        self.suspicious_locations = ['temp', 'tmp', 'appdata', 'programdata', 'downloads']
        self.colorama_available = alert_manager.colorama_available
        
    def on_modified(self, event):
        if not event.is_directory:
            if 'alerts.json' in event.src_path or '.tmp' in event.src_path or '.fallback' in event.src_path:
                return
            self._check_file(event.src_path, 'MODIFIED')
    
    def on_created(self, event):
        if not event.is_directory:
            if 'alerts.json' in event.src_path or '.tmp' in event.src_path or '.fallback' in event.src_path:
                return
            self._check_file(event.src_path, 'CREATED')
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._check_file(event.src_path, 'DELETED')
    
    def on_moved(self, event):
        if not event.is_directory:
            self._check_move(event.src_path, event.dest_path)
    
    def _check_file(self, file_path, change_type):
        """Check if file change warrants an alert"""
        # Ignore files in the alerts directory
        if 'alerts' in file_path.lower():
            return
        
        severity = self._determine_severity(file_path)
        
        file_size = None
        if os.path.exists(file_path) and change_type != 'DELETED':
            try:
                file_size = os.path.getsize(file_path)
            except:
                pass
        
        self.alert_manager.add_alert(
            alert_type=change_type,
            path=file_path,
            severity=severity,
            size=file_size
        )
        
    def _check_move(self, src_path, dest_path):
        """Check if file move is suspicious"""
        severity = self._determine_severity(dest_path)
        
        src_suspicious = any(loc in src_path.lower() for loc in self.suspicious_locations)
        dest_suspicious = any(loc in dest_path.lower() for loc in self.suspicious_locations)
        
        if src_suspicious or dest_suspicious:
            severity = 'HIGH'
        
        self.alert_manager.add_alert(
            alert_type='MOVED',
            path=dest_path,
            severity=severity,
            src_path=src_path,
            dest_path=dest_path
        )
    
    def _determine_severity(self, file_path):
        """Determine alert severity based on file path"""
        file_lower = file_path.lower()
        
        critical_paths = ['system32', 'windows\\system', 'etc', 'boot', 'kernel']
        if any(critical in file_lower for critical in critical_paths):
            return 'CRITICAL'
        
        sensitive_paths = ['config', 'password', 'shadow', 'sam', 'database', 'sql']
        if any(sensitive in file_lower for sensitive in sensitive_paths):
            return 'HIGH'
        
        ext = os.path.splitext(file_lower)[1]
        if ext in self.suspicious_extensions:
            if any(loc in file_lower for loc in self.suspicious_locations):
                return 'HIGH'
            return 'MEDIUM'
        
        if 'log' in file_lower or '.log' in file_lower:
            return 'MEDIUM'
        
        return 'LOW'

# ==============================
# AUTO-REMEDIATION
# ==============================

class AutoRemediation:
    """Automatically handle integrity violations"""
    
    def __init__(self, integrity_monitor):
        self.integrity_monitor = integrity_monitor
        self.remediation_log = os.path.join(integrity_monitor.report_dir, 'remediation_log.json')
        self.quarantine_dir = os.path.join(integrity_monitor.report_dir, 'auto_quarantine')
        self.colorama_available = integrity_monitor.colorama_available
        
        os.makedirs(self.quarantine_dir, exist_ok=True)
        self.policies = self._load_policies()
    
    def _load_policies(self):
        """Load remediation policies"""
        policy_file = os.path.join(self.integrity_monitor.report_dir, 'remediation_policies.json')
        
        default_policies = {
            'critical_files': {'action': 'alert_and_restore', 'backup_source': 'baseline', 'notify': True, 'severity_threshold': 'CRITICAL'},
            'suspicious_executables': {'action': 'quarantine', 'notify': True, 'severity_threshold': 'HIGH'},
            'config_changes': {'action': 'alert', 'notify': True, 'severity_threshold': 'MEDIUM'},
            'unauthorized_access': {'action': 'block_and_alert', 'notify': True, 'severity_threshold': 'HIGH'},
            'log_files': {'action': 'alert', 'notify': False, 'severity_threshold': 'LOW'}
        }
        
        if os.path.exists(policy_file):
            try:
                with open(policy_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_policies
        else:
            with open(policy_file, 'w', encoding='utf-8') as f:
                json.dump(default_policies, f, indent=2, default=str)
            return default_policies
    
    def handle_violation(self, violation):
        """Handle integrity violation based on policies"""
        action = self._determine_action(violation)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'violation': violation,
            'action_taken': action,
            'success': False,
            'details': {}
        }
        
        if action == 'quarantine':
            result = self._quarantine_violation(violation, result)
        elif action == 'restore' or action == 'alert_and_restore':
            result = self._restore_from_backup(violation, result)
        elif action == 'alert':
            result['success'] = True
            result['details']['message'] = 'Alert sent'
        elif action == 'block_and_alert':
            result = self._block_violation(violation, result)
        
        self._log_remediation(result)
        
        if self.policies.get(self._get_policy_key(violation), {}).get('notify', False):
            self._notify_admin(result)
        
        return result
    
    def _determine_action(self, violation):
        """Determine appropriate action for violation"""
        path = violation.get('path', '')
        severity = violation.get('severity', 'LOW')
        
        if any(critical in path.lower() for critical in ['system32', 'etc', 'boot', 'kernel']):
            return self.policies.get('critical_files', {}).get('action', 'alert_and_restore')
        
        if any(suspicious in path.lower() for suspicious in ['.exe', '.dll', '.scr', '.vbs', '.ps1']):
            if 'temp' in path.lower() or 'download' in path.lower() or 'appdata' in path.lower():
                return self.policies.get('suspicious_executables', {}).get('action', 'quarantine')
        
        if 'config' in path.lower():
            return self.policies.get('config_changes', {}).get('action', 'alert')
        
        if 'log' in path.lower() or '.log' in path.lower():
            return self.policies.get('log_files', {}).get('action', 'alert')
        
        if severity == 'CRITICAL':
            return 'alert_and_restore'
        elif severity == 'HIGH':
            return 'quarantine'
        elif severity == 'MEDIUM':
            return 'alert'
        else:
            return 'alert'
    
    def _get_policy_key(self, violation):
        """Get policy key based on violation type"""
        path = violation.get('path', '')
        
        if any(critical in path.lower() for critical in ['system32', 'etc', 'boot', 'kernel']):
            return 'critical_files'
        elif any(suspicious in path.lower() for suspicious in ['.exe', '.dll', '.scr', '.vbs', '.ps1']):
            return 'suspicious_executables'
        elif 'config' in path.lower():
            return 'config_changes'
        elif 'log' in path.lower() or '.log' in path.lower():
            return 'log_files'
        else:
            return 'unauthorized_access'
    
    def _quarantine_violation(self, violation, result):
        """Quarantine violating file"""
        try:
            file_path = violation.get('path')
            
            if not os.path.exists(file_path):
                result['success'] = False
                result['details']['error'] = f"File not found: {file_path}"
                return result
            
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            quarantine_path = os.path.join(self.quarantine_dir, f"{timestamp}_{filename}.quarantine")
            
            shutil.move(file_path, quarantine_path)
            
            metadata = {
                'original_path': file_path,
                'quarantine_path': quarantine_path,
                'timestamp': datetime.now().isoformat(),
                'file_size': os.path.getsize(quarantine_path),
                'reason': violation.get('change_type', 'Suspicious change detected')
            }
            
            metadata_file = quarantine_path + '.meta'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            result['success'] = True
            result['details'] = {
                'quarantine_path': quarantine_path,
                'original_path': file_path,
                'file_size': metadata['file_size']
            }
            
            if self.colorama_available:
                print(f"{Fore.YELLOW}✓ File quarantined: {quarantine_path}{Style.RESET_ALL}")
            else:
                print(f"✓ File quarantined: {quarantine_path}")
            
        except Exception as e:
            result['success'] = False
            result['details']['error'] = str(e)
            if self.colorama_available:
                print(f"{Fore.RED}✗ Auto-quarantine failed: {e}{Style.RESET_ALL}")
            else:
                print(f"✗ Auto-quarantine failed: {e}")
        
        return result
    
    def _restore_from_backup(self, violation, result):
        """Restore file from backup or baseline"""
        try:
            file_path = violation.get('path')
            
            baseline = self.integrity_monitor._load_baseline()
            if not baseline:
                result['success'] = False
                result['details']['error'] = "No baseline available for restoration"
                return result
            
            all_files = []
            for category in ['files', 'configs', 'critical_files']:
                all_files.extend(baseline.get(category, []))
            
            baseline_file = next((f for f in all_files if f['path'] == file_path), None)
            
            if not baseline_file:
                result['success'] = False
                result['details']['error'] = f"No baseline data for: {file_path}"
                return result
            
            if os.path.exists(file_path):
                backup_path = file_path + '.backup'
                shutil.copy2(file_path, backup_path)
                result['details']['backup_created'] = backup_path
            
            restore_marker = file_path + '.restored'
            with open(restore_marker, 'w') as f:
                f.write(f"Restored from baseline at {datetime.now().isoformat()}\n")
                f.write(f"Baseline hash: {baseline_file.get('hash', 'Unknown')}\n")
            
            result['success'] = True
            result['details']['message'] = f"File marked for restoration (requires manual restore from backup)"
            result['details']['baseline_hash'] = baseline_file.get('hash')
            
            if self.colorama_available:
                print(f"{Fore.CYAN}ℹ File marked for restoration: {file_path}{Style.RESET_ALL}")
            else:
                print(f"ℹ File marked for restoration: {file_path}")
            
        except Exception as e:
            result['success'] = False
            result['details']['error'] = str(e)
            if self.colorama_available:
                print(f"{Fore.RED}✗ Auto-restore failed: {e}{Style.RESET_ALL}")
            else:
                print(f"✗ Auto-restore failed: {e}")
        
        return result
    
    def _block_violation(self, violation, result):
        """Block access to violating file"""
        try:
            file_path = violation.get('path')
            
            if not os.path.exists(file_path):
                result['success'] = False
                result['details']['error'] = f"File not found: {file_path}"
                return result
            
            if platform.system().lower() == 'windows':
                import ctypes
                FILE_ATTRIBUTE_READONLY = 0x1
                ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_READONLY)
            else:
                current_perms = os.stat(file_path).st_mode
                os.chmod(file_path, current_perms & ~0o222)
            
            block_file = file_path + '.blocked'
            with open(block_file, 'w', encoding='utf-8') as f:
                f.write(f"Blocked at {datetime.now().isoformat()}\n")
                f.write(f"Reason: {violation.get('change_type', 'Unauthorized change detected')}\n")
            
            result['success'] = True
            result['details']['message'] = "File access blocked (read-only)"
            
            if self.colorama_available:
                print(f"{Fore.YELLOW}✓ File access blocked: {file_path}{Style.RESET_ALL}")
            else:
                print(f"✓ File access blocked: {file_path}")
            
        except Exception as e:
            result['success'] = False
            result['details']['error'] = str(e)
            if self.colorama_available:
                print(f"{Fore.RED}✗ Block operation failed: {e}{Style.RESET_ALL}")
            else:
                print(f"✗ Block operation failed: {e}")
        
        return result
    
    def _log_remediation(self, result):
        """Log remediation action"""
        try:
            if os.path.exists(self.remediation_log):
                with open(self.remediation_log, 'r', encoding='utf-8') as f:
                    try:
                        log = json.load(f)
                    except json.JSONDecodeError:
                        log = []
            else:
                log = []
            
            log.append(result)
            
            if len(log) > 1000:
                log = log[-1000:]
            
            with open(self.remediation_log, 'w', encoding='utf-8') as f:
                json.dump(log, f, indent=2, default=str)
                
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Failed to log remediation: {e}{Style.RESET_ALL}")
            else:
                print(f"Failed to log remediation: {e}")
    
    def _notify_admin(self, result):
        """Notify administrator about remediation action"""
        try:
            notification_file = os.path.join(self.integrity_monitor.report_dir, 'notifications.log')
            
            with open(notification_file, 'a', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"NOTIFICATION: {datetime.now().isoformat()}\n")
                f.write(f"Action: {result['action_taken']}\n")
                f.write(f"Success: {result['success']}\n")
                f.write(f"Violation: {result['violation'].get('path', 'Unknown')}\n")
                f.write(f"Severity: {result['violation'].get('severity', 'UNKNOWN')}\n")
                if result.get('details'):
                    f.write(f"Details: {json.dumps(result['details'], default=str)}\n")
                f.write("=" * 60 + "\n\n")
            
            if self.colorama_available:
                print(f"{Fore.BLUE}📧 Notification logged: {notification_file}{Style.RESET_ALL}")
            else:
                print(f"📧 Notification logged: {notification_file}")
                
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Failed to send notification: {e}{Style.RESET_ALL}")
            else:
                print(f"Failed to send notification: {e}")
    
    def get_remediation_history(self, limit=50):
        """Get remediation history"""
        try:
            if os.path.exists(self.remediation_log):
                with open(self.remediation_log, 'r', encoding='utf-8') as f:
                    try:
                        log = json.load(f)
                        return log[-limit:]
                    except json.JSONDecodeError:
                        return []
            return []
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Failed to load remediation history: {e}{Style.RESET_ALL}")
            else:
                print(f"Failed to load remediation history: {e}")
            return []

# ==============================
# MAIN MENU
# ==============================

def main_menu():
    """Interactive main menu for integrity monitor"""
    monitor = SystemIntegrityMonitor()
    
    if monitor.colorama_available:
        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'INTEGRITY MONITOR - MAIN MENU'.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    else:
        print("\n" + "=" * 60)
        print("INTEGRITY MONITOR - MAIN MENU".center(60))
        print("=" * 60)
    
    while True:
        print(f"\n{Fore.YELLOW if monitor.colorama_available else ''}Available Operations:{Style.RESET_ALL if monitor.colorama_available else ''}")
        print("  1. Full System Scan")
        print("  2. Create Baseline")
        print("  3. Check Integrity (Compare with Baseline)")
        print("  4. Full Integrity Check (Scan + Compare + Report)")
        print("  5. Generate Reports (from latest scan)")
        print("  6. Start Real-time Monitoring")
        print("  7. View Recent Alerts")
        print("  8. View Remediation History")
        print("  0. Exit")
        
        choice = input(f"\n{Fore.GREEN if monitor.colorama_available else ''}Select operation: {Style.RESET_ALL if monitor.colorama_available else ''}").strip()
        
        if choice == "1":
            scan_type = input("Scan type (all/configs/logs/databases/system/user): ").strip() or "all"
            monitor.scan_system(scan_type)
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            monitor.create_baseline()
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            monitor.check_integrity()
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            monitor.full_integrity_check()
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # Generate reports from latest scan
            scan_results = monitor.scan_system()
            changes = monitor.check_integrity(scan_results)
            if changes:
                monitor.generate_all_reports(changes, scan_results)
            else:
                monitor.generate_report(None, scan_results)
                monitor.generate_json_report(None, scan_results)
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            monitor.alert_manager.start_monitoring()
            input("\nPress Enter to continue...")
            
        elif choice == "7":
            alerts = monitor.alert_manager.get_alerts(limit=20)
            if alerts:
                print(f"\n{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                print(f"{Fore.MAGENTA if monitor.colorama_available else ''}RECENT ALERTS{Style.RESET_ALL if monitor.colorama_available else ''}")
                print(f"{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                for alert in alerts[-20:]:
                    time_str = alert.get('timestamp', datetime.now()).isoformat()[:19] if hasattr(alert.get('timestamp'), 'isoformat') else str(alert.get('timestamp', ''))[:19]
                    severity = alert.get('severity', 'LOW')
                    alert_type = alert.get('type', 'UNKNOWN')
                    path = alert.get('path', 'Unknown')
                    print(f"  [{time_str}] {severity}: {alert_type} - {path}")
            else:
                print("\nNo alerts found.")
            input("\nPress Enter to continue...")
            
        elif choice == "8":
            history = monitor.auto_remediation.get_remediation_history(20)
            if history:
                print(f"\n{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                print(f"{Fore.MAGENTA if monitor.colorama_available else ''}REMEDIATION HISTORY{Style.RESET_ALL if monitor.colorama_available else ''}")
                print(f"{Fore.CYAN if monitor.colorama_available else ''}{'=' * 60}{Style.RESET_ALL if monitor.colorama_available else ''}")
                for entry in history:
                    time_str = entry.get('timestamp', '')[:19]
                    action = entry.get('action_taken', 'UNKNOWN')
                    success = "✓" if entry.get('success') else "✗"
                    path = entry.get('violation', {}).get('path', 'Unknown')
                    print(f"  [{time_str}] {success} {action}: {path}")
            else:
                print("\nNo remediation history found.")
            input("\nPress Enter to continue...")
            
        elif choice == "0":
            if monitor.colorama_available:
                print(f"\n{Fore.GREEN}Exiting Integrity Monitor...{Style.RESET_ALL}")
            else:
                print("\nExiting Integrity Monitor...")
            break
            
        else:
            if monitor.colorama_available:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            else:
                print("Invalid choice. Please try again.")
            time.sleep(1)

# ==============================
# ENTRY POINT
# ==============================

if __name__ == "__main__":
    print("=" * 60)
    print("DSTERMINAL INTEGRITY MONITOR")
    print("=" * 60)
    print(f"Workspace: {WORKSPACE}")
    print()
    
    main_menu()