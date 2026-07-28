#!/usr/bin/env python3
"""
DSTerminal Integrity Monitor Module
Comprehensive system integrity monitoring with real-time alerts
All reports saved to DSTerminal workspace
"""
# At the VERY TOP of integrity_monitor.py, add:
# CRITICAL FIX: Import colorama FIRST
from colorama import Fore, Style, init as colorama_init
colorama_init(autoreset=True)

# Then continue with your existing imports...
try:
    from fpdf import FPDF
    from datetime import datetime
    import textwrap
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
import os
import sys
# Add these imports at the top of your file
try:
    from fpdf import FPDF
    from datetime import datetime
    import textwrap
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: fpdf not installed. PDF reports will not be available.")
    print("Install with: pip install fpdf")

import json
from pathlib import Path
import hashlib
import time
import shutil
import platform
import threading
import glob
from datetime import datetime, timedelta
import psutil  # You'll need to install: pip install psutil
# At the top of integrity_monitor.py, after the other imports, add:
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

# Define COLORAMA_AVAILABLE as a global variable
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback if colorama not installed
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    
    class Back:
        RED = '\033[101m'
        GREEN = '\033[102m'
        YELLOW = '\033[103m'
        BLUE = '\033[104m'
        RESET = '\033[0m'
    
    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'

# Add watchdog for real-time monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy classes so the code doesn't break
    class FileSystemEventHandler:
        def on_modified(self, event): pass
        def on_created(self, event): pass
        def on_deleted(self, event): pass
        def on_moved(self, event): pass
    
    class Observer:
        def schedule(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
        def join(self): pass
    
    if COLORAMA_AVAILABLE:
        print(f"{Fore.YELLOW}⚠ Warning: watchdog not installed. Real-time monitoring will not work.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  Install with: pip install watchdog{Style.RESET_ALL}")
    else:
        print("⚠ Warning: watchdog not installed. Real-time monitoring will not work.")
        print("  Install with: pip install watchdog")


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
            print(f"{Fore.GREEN}✓ Auto-remediation initialized{Style.RESET_ALL}")
        else:
            print("✓ Auto-remediation initialized")
    # ==========================
    # Initialize forensic analyzer
        self.forensic = ForensicAnalyzer(self)
    
        if self.colorama_available:
            print(f"{Fore.GREEN}✓ Forensic Analyzer initialized{Style.RESET_ALL}")
        else:
            print("✓ Forensic Analyzer initialized")
    # ===========================
        if self.colorama_available:
            print(f"{Fore.GREEN}✓ System Integrity Monitor initialized{Style.RESET_ALL}")
            print(f"{Fore.CYAN}✓ Workspace: {self.workspace}{Style.RESET_ALL}")
        else:
            print("✓ System Integrity Monitor initialized")
            print(f"✓ Workspace: {self.workspace}")
    # ==============================
    # cinematic animation log
    # ==============================

    def _animated_spinner(self, stop_event, message, spinner_type='default'):
        """Animated spinner with different styles"""
        spinners = {
            'default': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'braille': ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'],
            'blocks': ['▉', '▊', '▋', '▌', '▍', '▎', '▏', '▎', '▍', '▌', '▋', '▊', '▉'],
            'triangles': ['◢', '◣', '◤', '◥'],
            'circles': ['◐', '◓', '◑', '◒'],
            'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙']
        }
    
        colors = {
            'configs': [Fore.CYAN, Fore.GREEN, Fore.MAGENTA],
            'logs': [Fore.BLUE, Fore.CYAN, Fore.LIGHTBLUE_EX] if self.colorama_available else [Fore.BLUE, Fore.CYAN, Fore.BLUE],
            'databases': [Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX] if self.colorama_available else [Fore.MAGENTA, Fore.MAGENTA, Fore.RED],
            'system': [Fore.RED, Fore.LIGHTRED_EX, Fore.YELLOW] if self.colorama_available else [Fore.RED, Fore.RED, Fore.YELLOW],
            'user': [Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.CYAN] if self.colorama_available else [Fore.GREEN, Fore.GREEN, Fore.CYAN],
            'default': [Fore.CYAN, Fore.GREEN, Fore.MAGENTA]
        }
    
        color_set = colors.get(spinner_type, colors['default'])
        spinner = spinners.get(spinner_type, spinners['default'])
    
        frame = 0
        while not stop_event.is_set():
            left = f"{color_set[0]}{spinner[frame % len(spinner)]}{Style.RESET_ALL}"
            center = f"{color_set[1]}{spinner[(frame + 1) % len(spinner)]}{Style.RESET_ALL}"
            right = f"{color_set[2]}{spinner[(frame + 2) % len(spinner)]}{Style.RESET_ALL}"
        
            terminal_width = shutil.get_terminal_size().columns
            wheels_text = f"{left} {center} {right} {Fore.WHITE}{message}{Style.RESET_ALL}"
        
        # Remove ANSI codes for width calculation
            clean_text = wheels_text.replace(Fore.CYAN, '').replace(Fore.GREEN, '').replace(Fore.MAGENTA, '')
            clean_text = clean_text.replace(Fore.BLUE, '').replace(Fore.LIGHTBLUE_EX, '')
            clean_text = clean_text.replace(Fore.LIGHTMAGENTA_EX, '').replace(Fore.LIGHTRED_EX, '')
            clean_text = clean_text.replace(Fore.RED, '').replace(Fore.YELLOW, '')
            clean_text = clean_text.replace(Fore.WHITE, '').replace(Style.RESET_ALL, '')
            text_width = len(clean_text)
            padding = max(0, (terminal_width - text_width) // 2)
        
            print(f"\r{' ' * padding}{wheels_text}", end='', flush=True)
            frame += 1
            time.sleep(0.1)

    def _animated_scan_line(self, message, duration=2):
        """Animated scan line effect"""
        chars = ['█', '▓', '▒', '░']
        terminal_width = shutil.get_terminal_size().columns
        start_time = time.time()
    
        while time.time() - start_time < duration:
            for char in chars:
                line = f"{Fore.GREEN}{char * 20}{Style.RESET_ALL} {message}"
                padding = max(0, (terminal_width - len(message) - 20) // 2)
                print(f"\r{' ' * padding}{line}", end='', flush=True)
                time.sleep(0.05)
    
        print(f"\r{' ' * terminal_width}", end='\r')

    def _animated_progress_bar(self, current, total, message, width=40):
        """Enhanced animated progress bar with gradient effect"""
        percent = (current / total) * 100
        filled = int(width * current // total)
    
    # Gradient colors based on progress
        if percent < 30:
            bar_color = Fore.CYAN
        elif percent < 70:
            bar_color = Fore.YELLOW
        else:
            bar_color = Fore.GREEN
    
    # Create gradient bar
        bar = ''
        for i in range(width):
            if i < filled:
                if i < width * 0.3:
                    bar += f"{Fore.CYAN}█{Style.RESET_ALL}"
                elif i < width * 0.6:
                    bar += f"{Fore.YELLOW}█{Style.RESET_ALL}"
                else:
                    bar += f"{Fore.GREEN}█{Style.RESET_ALL}"
            else:
                bar += f"{Fore.WHITE}░{Style.RESET_ALL}"
    
    # Spinning wheel
        wheels = ['◴', '◷', '◶', '◵']
        wheel = wheels[int(time.time() * 4) % 4]
    
        progress_text = f"{message}: [{bar}] {percent:.1f}% [{current}/{total}] {wheel}"
    
        terminal_width = shutil.get_terminal_size().columns
        clean_text = progress_text.replace(Fore.CYAN, '').replace(Fore.YELLOW, '').replace(Fore.GREEN, '').replace(Fore.WHITE, '').replace(Style.RESET_ALL, '')
        text_width = len(clean_text)
        padding = max(0, (terminal_width - text_width) // 2)
    
        print(f"\r{' ' * padding}{progress_text}", end='', flush=True)
    
        if current == total:
            print()
    # ==============================
    # SYSTEM PATH DETECTION
    # ==============================
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
    
    # ==============================
    # FILE/DIRECTORY SCANNING
    # ==============================
    def _scan_configs(self, results):
        """Scan configuration files with cinematic animations"""
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'⚙️  SCANNING CONFIGURATION FILES'.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
    
        self._animated_scan_line("Initializing configuration scanner", duration=1)
    
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=self._animated_spinner,
            args=(stop_spinner, "Analyzing configuration files...", 'configs')
        )
        spinner_thread.daemon = True
        spinner_thread.start()
    
        count = 0
        total_paths = len(self.system_paths['configs'])
    
        for i, config_path in enumerate(self.system_paths['configs'], 1):
            if os.path.exists(config_path):
                self._animated_progress_bar(i, total_paths, "Scanning configs", 40)
                count += self._scan_directory(config_path, results['configs'], 'config')
    
        stop_spinner.set()
        spinner_thread.join(timeout=0.5)
    
        terminal_width = shutil.get_terminal_size().columns
        print(f"\r{' ' * terminal_width}", end='\r')
    
        print(f"\n{Fore.GREEN}✓ Found {count} configuration items{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")
    
    def _scan_category(self, category, results, target_key=None):
        """Scan a specific category with cinematic header"""
        if target_key is None:
            target_key = category

        # Category icons and colors
        category_styles = {
            'configs': {'icon': '⚙️', 'title': 'CONFIGURATION FILES', 'color': Fore.CYAN},
            'logs': {'icon': '📋', 'title': 'LOG FILES', 'color': Fore.BLUE},
            'databases': {'icon': '🗄️', 'title': 'DATABASES', 'color': Fore.MAGENTA},
            'system_files': {'icon': '🔒', 'title': 'CRITICAL SYSTEM FILES', 'color': Fore.RED},
            'user_files': {'icon': '👤', 'title': 'USER FILES', 'color': Fore.GREEN}
        }

        style = category_styles.get(category, {'icon': '📁', 'title': category.upper(), 'color': Fore.WHITE})

        if self.colorama_available:
            print(f"\n{style['color']}{'═' * 60}{Style.RESET_ALL}")
            print(f"{style['color']}{Style.BRIGHT}{style['icon']}  SCANNING {style['title']}  {style['icon']}{Style.RESET_ALL}")
            print(f"{style['color']}{'═' * 60}{Style.RESET_ALL}")
        else:
            print(f"\n{'=' * 60}")
            print(f"SCANNING {style['title']}")
            print(f"{'=' * 60}")

        self._animated_scan_line(f"Initializing {category} scanner", duration=1)

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

    def _scan_logs(self, results):
        """Scan log files with cinematic animations"""
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'📋 SCANNING LOG FILES'.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
    
        self._animated_scan_line("Initializing log scanner", duration=1)
    
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=self._animated_spinner,
            args=(stop_spinner, "Processing log files...", 'logs')
        )
        spinner_thread.daemon = True
        spinner_thread.start()
    
        count = 0
        total_paths = len(self.system_paths['logs'])
    
        for i, log_path in enumerate(self.system_paths['logs'], 1):
            if os.path.exists(log_path):
                self._animated_progress_bar(i, total_paths, "Scanning logs", 40)
                count += self._scan_directory(log_path, results['logs'], 'log')
    
        stop_spinner.set()
        spinner_thread.join(timeout=0.5)
    
        terminal_width = shutil.get_terminal_size().columns
        print(f"\r{' ' * terminal_width}", end='\r')
    
        print(f"\n{Fore.GREEN}✓ Found {count} log files{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")

    def _scan_databases(self, results):
        """Scan database files with cinematic animations"""
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'🗄️  SCANNING DATABASES'.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
    
        self._animated_scan_line("Initializing database scanner", duration=1)
    
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=self._animated_spinner,
            args=(stop_spinner, "Querying databases...", 'databases')
        )
        spinner_thread.daemon = True
        spinner_thread.start()
    
        count = 0
        total_paths = len(self.system_paths['databases'])
    
        for i, db_path in enumerate(self.system_paths['databases'], 1):
            if os.path.exists(db_path):
                self._animated_progress_bar(i, total_paths, "Scanning databases", 40)
                count += self._scan_directory(db_path, results['databases'], 'database')
    
        stop_spinner.set()
        spinner_thread.join(timeout=0.5)
    
        terminal_width = shutil.get_terminal_size().columns
        print(f"\r{' ' * terminal_width}", end='\r')
    
        print(f"\n{Fore.GREEN}✓ Found {count} database files{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")

    def _scan_system_files(self, results):
        """Scan critical system files with cinematic animations"""
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'🔒 SCANNING CRITICAL SYSTEM FILES'.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
    
        self._animated_scan_line("Initializing system scanner", duration=1)
    
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=self._animated_spinner,
            args=(stop_spinner, "Checking system integrity...", 'system')
        )
        spinner_thread.daemon = True
        spinner_thread.start()
    
        count = 0
        total_files = len(self.system_paths['system_files'])
    
        for i, file_path in enumerate(self.system_paths['system_files'], 1):
            if os.path.exists(file_path):
                self._animated_progress_bar(i, total_files, "Scanning system files", 40)
                file_info = self._get_file_info(file_path)
                file_info['category'] = 'system'
                results['critical_files'].append(file_info)
                count += 1
    
        stop_spinner.set()
        spinner_thread.join(timeout=0.5)
    
        terminal_width = shutil.get_terminal_size().columns
        print(f"\r{' ' * terminal_width}", end='\r')
    
        print(f"\n{Fore.GREEN}✓ Found {count} critical system files{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")

    def _scan_user_files(self, results):
        """Scan user files with cinematic animations"""
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'👤 SCANNING USER FILES'.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
    
        self._animated_scan_line("Initializing user file scanner", duration=1)
    
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=self._animated_spinner,
            args=(stop_spinner, "Indexing user files...", 'user')
        )
        spinner_thread.daemon = True
        spinner_thread.start()
    
        count = 0
        total_paths = len(self.system_paths['user_files'])
    
        for i, user_path in enumerate(self.system_paths['user_files'], 1):
            if os.path.exists(user_path):
                self._animated_progress_bar(i, total_paths, "Scanning user files", 40)
                count += self._scan_directory(user_path, results['files'], 'user')
    
        stop_spinner.set()
        spinner_thread.join(timeout=0.5)
    
        terminal_width = shutil.get_terminal_size().columns
        print(f"\r{' ' * terminal_width}", end='\r')
    
        print(f"\n{Fore.GREEN}✓ Found {count} user files{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")

    def _print_progress(self, current, total, message):
        """Enhanced progress bar with animations"""
        percent = (current / total) * 100
        bar_length = 40
        filled_length = int(bar_length * current // total)
    
        # Create gradient bar
        bar = ''
        for i in range(bar_length):
            if i < filled_length:
                if i < bar_length * 0.3:
                    bar += f"{Fore.CYAN}█{Style.RESET_ALL}"
                elif i < bar_length * 0.6:
                    bar += f"{Fore.YELLOW}█{Style.RESET_ALL}"
                else:
                    bar += f"{Fore.GREEN}█{Style.RESET_ALL}"
            else:
                bar += f"{Fore.WHITE}░{Style.RESET_ALL}"
    
        # Animated spinner
        spinners = ['◴', '◷', '◶', '◵']
        spinner = spinners[int(time.time() * 4) % 4]
    
        progress_text = f"{message}: [{bar}] {percent:.1f}% [{current}/{total}] {spinner}"
    
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
    
    def _scan_directory(self, directory, results_list, category, max_depth=3):
        """Recursively scan a directory with progress animation"""
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
    
    # ==============================
    # BASELINE MANAGEMENT
    # ==============================
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
        
        # Save baseline to workspace
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
    
    # ==============================
    # INTEGRITY CHECKING
    # ==============================
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
            self._print_progress(i, total_items, "Analyzing files")
            
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
        
        # Save integrity check results to workspace
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
    
    # ==============================
    # REPORT GENERATION
    # ==============================
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
        pdf.cell(0, 5, f"Generated by DSTerminal Integrity Monitor v3..1.113", 0, 1, 'C')
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
    
    # ==============================
    # UTILITY FUNCTIONS
    # ==============================
    def _format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    # ==============================
    # MAIN INTERFACE FUNCTIONS
    # ==============================
    def list_all_files(self, category='all'):
        """List all files by category"""
        scan_results = self.scan_system(category)
        
        if self.colorama_available:
            print(f"\n{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}{'SYSTEM FILE INVENTORY'.center(self.terminal_width)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}\n")
        else:
            print("\n" + "=" * self.terminal_width)
            print("SYSTEM FILE INVENTORY".center(self.terminal_width))
            print("=" * self.terminal_width + "\n")
        
        categories = {
            'critical': scan_results['critical_files'],
            'configs': scan_results['configs'],
            'logs': scan_results['logs'],
            'databases': scan_results['databases'],
            'user': scan_results['files']
        }
        
        if category != 'all':
            categories = {category: categories.get(category, [])}
        
        for cat_name, items in categories.items():
            if items:
                if self.colorama_available:
                    print(f"\n{Fore.YELLOW}{cat_name.upper()} FILES ({len(items)}):{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'-' * 60}{Style.RESET_ALL}")
                else:
                    print(f"\n{cat_name.upper()} FILES ({len(items)}):")
                    print("-" * 60)
                
                for item in sorted(items, key=lambda x: x.get('modified', ''), reverse=True)[:20]:
                    modified = item.get('modified', 'Unknown')[:16] if item.get('modified') else 'Unknown'
                    
                    if self.colorama_available:
                        print(f"{Fore.WHITE}{item['name']}{Style.RESET_ALL}")
                        print(f"  {Fore.CYAN}Path:{Style.RESET_ALL} {item['path']}")
                        print(f"  {Fore.GREEN}Modified:{Style.RESET_ALL} {modified}")
                        print(f"  {Fore.MAGENTA}Size:{Style.RESET_ALL} {self._format_size(item['size'])}")
                    else:
                        print(f"{item['name']}")
                        print(f"  Path: {item['path']}")
                        print(f"  Modified: {modified}")
                        print(f"  Size: {self._format_size(item['size'])}")
                    print()
    
    def full_integrity_check(self):
        """Perform full system integrity check and save reports to workspace"""
        scan_results = self.scan_system()
        changes = self.check_integrity(scan_results)
        
        if changes:
            self._display_changes(changes)
            reports = self.generate_all_reports(changes, scan_results)
            self._display_mitigation_summary(changes)
            
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
    
    def _display_mitigation_summary(self, changes):
        """Display mitigation summary"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for change_type in ['new_files', 'modified_files', 'deleted_files']:
            for item in changes[change_type]:
                severity_counts[item.get('severity', 'LOW')] += 1
        
        if self.colorama_available:
            print(f"\n{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}{'MITIGATION SUMMARY'.center(self.terminal_width)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * self.terminal_width}{Style.RESET_ALL}\n")
            
            print(f"Severity Breakdown:")
            print(f"  [CRITICAL]: {severity_counts['CRITICAL']}")
            print(f"  [HIGH]: {severity_counts['HIGH']}")
            print(f"  [MEDIUM]: {severity_counts['MEDIUM']}")
            print(f"  [LOW]: {severity_counts['LOW']}")
            
            print(f"\n{Fore.YELLOW}Recommended Immediate Actions:{Style.RESET_ALL}")
            if severity_counts['CRITICAL'] > 0:
                print(f"  • {Fore.RED}Investigate CRITICAL changes immediately{Style.RESET_ALL}")
            if severity_counts['HIGH'] > 0:
                print(f"  • {Fore.YELLOW}Review HIGH severity changes soon{Style.RESET_ALL}")
        else:
            print("\n" + "=" * self.terminal_width)
            print("MITIGATION SUMMARY".center(self.terminal_width))
            print("=" * self.terminal_width + "\n")
            print(f"Severity Breakdown:")
            print(f"  [CRITICAL]: {severity_counts['CRITICAL']}")
            print(f"  [HIGH]: {severity_counts['HIGH']}")
            print(f"  [MEDIUM]: {severity_counts['MEDIUM']}")
            print(f"  [LOW]: {severity_counts['LOW']}")
            print("\nRecommended Immediate Actions:")
            if severity_counts['CRITICAL'] > 0:
                print(f"  • Investigate CRITICAL changes immediately")
            if severity_counts['HIGH'] > 0:
                print(f"  • Review HIGH severity changes soon")


# [The rest of your classes remain exactly the same: RealTimeHandler, AlertManager, ForensicAnalyzer, AutoRemediation]
# They will automatically use the workspace directories because they reference self.report_dir, self.baseline_dir, etc.
# which now point to the workspace locations.

class RealTimeHandler(FileSystemEventHandler):
    """Handles real-time file system events"""
    
    def __init__(self, alert_manager):
        self.alert_manager = alert_manager
        self.suspicious_extensions = ['.exe', '.dll', '.vbs', '.ps1', '.sh', '.bin', '.scr']
        self.suspicious_locations = ['temp', 'tmp', 'appdata', 'programdata', 'downloads']
        self.colorama_available = alert_manager.colorama_available
        
    def on_modified(self, event):
        if not event.is_directory:
            # Ignore alert files to prevent recursive alerts
            if 'alerts.json' in event.src_path or '.tmp' in event.src_path or '.fallback' in event.src_path:
                return
            self._check_file(event.src_path, 'MODIFIED')

    def on_created(self, event):
        if not event.is_directory:
        # Ignore alert files
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
        severity = self._determine_severity(file_path)
        
        # Get file size if file exists
        file_size = None
        if os.path.exists(file_path) and change_type != 'DELETED':
            try:
                file_size = os.path.getsize(file_path)
            except:
                pass
        
        # Call alert manager with proper arguments
        self.alert_manager.add_alert(
            alert_type=change_type,
            path=file_path,
            severity=severity,
            size=file_size
        )
    
    def _check_move(self, src_path, dest_path):
        """Check if file move is suspicious"""
        severity = self._determine_severity(dest_path)
        
        # Check if moved to/from suspicious location
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
        
        # Critical system files
        critical_paths = ['system32', 'windows\\system', 'etc', 'boot', 'kernel']
        if any(critical in file_lower for critical in critical_paths):
            return 'CRITICAL'
        
        # Sensitive files
        sensitive_paths = ['config', 'password', 'shadow', 'sam', 'database', 'sql']
        if any(sensitive in file_lower for sensitive in sensitive_paths):
            return 'HIGH'
        
        # Suspicious extensions
        ext = os.path.splitext(file_lower)[1]
        if ext in self.suspicious_extensions:
            if any(loc in file_lower for loc in self.suspicious_locations):
                return 'HIGH'
            return 'MEDIUM'
        
        # Log files
        if 'log' in file_lower or '.log' in file_lower:
            return 'MEDIUM'
        
        return 'LOW'


class AlertManager:
    """Manages real-time alerts"""
    
    def __init__(self, integrity_monitor):
        self.integrity_monitor = integrity_monitor
        self.alerts = []
        self.running = False
        self.observer = None
        self.monitored_paths = []
        self._saving = False  # Add this flag
        self._printing_error = False  # Add this flag

        self.alerts_file = os.path.join("data", "alerts", "alerts.json")
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
            # Backup corrupted file
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
        """Save alerts to file with proper JSON serialization and atomic write"""
        # Add this flag to prevent recursive saves
        if hasattr(self, '_saving'):
            return
        self._saving = True
    
        try:
            # Create safe copy for JSON serialization
            safe_alerts = []
            for alert in self.alerts:
                safe_alert = {}
                for key, value in alert.items():
                    if hasattr(value, 'isoformat'):
                        safe_alert[key] = value.isoformat()
                    elif isinstance(value, bytes):
                        safe_alert[key] = value.decode('utf-8', errors='replace')
                    elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        safe_alert[key] = value
                    else:
                        safe_alert[key] = str(value)
                safe_alerts.append(safe_alert)
        
        # Ensure directory exists
            os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
        
        # Write to a temporary file first, then rename (atomic operation)
            temp_file = self.alerts_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(safe_alerts, f, indent=2, ensure_ascii=False, default=str)
                f.flush()
                os.fsync(f.fileno())
        
        # Atomic rename (prevents partial writes)
            os.replace(temp_file, self.alerts_file)
        
        except Exception as e:
        # Don't print during recursive calls
            if not hasattr(self, '_printing_error'):
                self._printing_error = True
                if self.colorama_available:
                    print(f"{Fore.RED}Failed to save alerts: {e}{Style.RESET_ALL}")
                else:
                    print(f"Failed to save alerts: {e}")
                self._printing_error = False
        
        # Write to fallback file
            fallback_file = self.alerts_file + ".fallback"
            try:
                with open(fallback_file, 'a', encoding='utf-8') as f:
                    f.write(f"{self.alerts[-1] if self.alerts else 'No alerts'}\n")
            except:
                pass
        finally:
            self._saving = False
    # =======================
    def start_monitoring(self, paths=None):
        """Start real-time monitoring"""
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
        
        # Default paths to monitor
        if paths is None:
            paths = [
                os.path.expanduser('~'),  # User home
            ]
        
        self.monitored_paths = paths
        self.running = True
        
        # Start observer
        self.observer = Observer()
        handler = RealTimeHandler(self)
        
        for path in paths:
            if os.path.exists(path):
                try:
                    self.observer.schedule(handler, path, recursive=True)
                    if self.colorama_available:
                        print(f"{Fore.GREEN}Monitoring: {path}{Style.RESET_ALL}")
                    else:
                        print(f"Monitoring: {path}")
                except Exception as e:
                    if self.colorama_available:
                        print(f"{Fore.RED}Failed to monitor {path}: {e}{Style.RESET_ALL}")
        
        if self.observer:
            self.observer.start()
            if self.colorama_available:
                print(f"\n{Fore.GREEN}✅ Real-time monitoring started{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Press Ctrl+C in the terminal to stop monitoring{Style.RESET_ALL}\n")
            else:
                print("\n✅ Real-time monitoring started")
                print("Press Ctrl+C in the terminal to stop monitoring\n")
    
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
        """Add a security alert with proper arguments"""
        try:
            alert = {
                'timestamp': datetime.now(),
                'type': alert_type,
                'path': str(path),
                'severity': severity,
            }
            
            # Add optional fields
            if 'size' in kwargs and kwargs['size'] is not None:
                alert['size'] = kwargs['size']
            if 'src_path' in kwargs:
                alert['src_path'] = str(kwargs['src_path'])
            if 'dest_path' in kwargs:
                alert['dest_path'] = str(kwargs['dest_path'])
            
            # Add to alerts list
            self.alerts.append(alert)
            
            # Keep only last 1000 alerts
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-1000:]
            
            # Save to file
            self._save_alerts()
            
            # Display alert
            self._display_alert(alert)
            
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Failed to add alert: {e}{Style.RESET_ALL}")
            else:
                print(f"Failed to add alert: {e}")
    
    def _display_alert(self, alert):
        """Display alert in real-time"""
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

    def add_alert_with_remediation(self, alert_type, path, severity="LOW", **kwargs):
        """Add alert and trigger auto-remediation if configured"""
    # Add the alert normally
        self.add_alert(alert_type, path, severity, **kwargs)
    
    # Check if auto-remediation should handle this
        if severity in ['CRITICAL', 'HIGH']:
            violation = {
                'path': path,
                'severity': severity,
                'type': alert_type,
                'change_type': kwargs.get('change_type', 'Unknown'),
                'timestamp': datetime.now().isoformat()
            }
        
        # Trigger auto-remediation
            self.integrity_monitor.auto_remediation.handle_violation(violation)

class ForensicAnalyzer:
    """Forensic analyzer for integrity monitoring and incident investigation"""
    
    def __init__(self, integrity_monitor):
        self.integrity_monitor = integrity_monitor
        self.report_dir = integrity_monitor.report_dir
        self.baseline_dir = integrity_monitor.baseline_dir
        self.alerts_dir = integrity_monitor.alerts_dir
        self.colorama_available = integrity_monitor.colorama_available
        
        # Create forensic reports directory
        self.forensic_dir = os.path.join(self.report_dir, 'forensic')
        os.makedirs(self.forensic_dir, exist_ok=True)
    
    def analyze_timeline(self, file_path=None, days=7, start_date=None, end_date=None):
        """Analyze timeline of changes for a specific file or all files"""
        try:
            # Load alerts
            alerts = self.integrity_monitor.alert_manager.alerts
            
            # Set date range
            if start_date is None:
                start_date = datetime.now() - timedelta(days=days)
            if end_date is None:
                end_date = datetime.now()
            
            timeline = []
            
            for alert in alerts:
                alert_time = alert.get('timestamp')
                if isinstance(alert_time, str):
                    alert_time = datetime.fromisoformat(alert_time)
                
                if alert_time and start_date <= alert_time <= end_date:
                    # Filter by file path if specified
                    if file_path is None or file_path in str(alert.get('path', '')):
                        timeline.append({
                            'time': alert_time,
                            'type': 'alert',
                            'data': alert,
                            'severity': alert.get('severity', 'UNKNOWN'),
                            'action': alert.get('type', 'UNKNOWN'),
                            'path': alert.get('path', alert.get('src_path', 'Unknown'))
                        })
            
            # Load baseline changes if available
            baseline_changes = self._get_baseline_changes(start_date, end_date)
            timeline.extend(baseline_changes)
            
            # Sort by time
            timeline.sort(key=lambda x: x['time'])
            
            return timeline
            
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Error analyzing timeline: {e}{Style.RESET_ALL}")
            else:
                print(f"Error analyzing timeline: {e}")
            return []
    
    def _get_baseline_changes(self, start_date, end_date):
        """Get baseline changes within date range"""
        changes = []
        
        try:
            baseline_files = []
            if os.path.exists(self.baseline_dir):
                for file in os.listdir(self.baseline_dir):
                    if file.endswith('.json'):
                        file_path = os.path.join(self.baseline_dir, file)
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        
                        if start_date <= file_time <= end_date:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                baseline = json.load(f)
                                changes.append({
                                    'time': file_time,
                                    'type': 'baseline',
                                    'data': baseline,
                                    'severity': 'INFO',
                                    'action': 'BASELINE_CREATED',
                                    'path': file_path
                                })
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.YELLOW}Could not load baseline changes: {e}{Style.RESET_ALL}")
            else:
                print(f"Could not load baseline changes: {e}")
        
        return changes
    
    def generate_forensic_report(self, file_path=None, days=7, output_format='txt'):
        """Generate comprehensive forensic report"""
        try:
            timeline = self.analyze_timeline(file_path, days)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_name = f'forensic_{timestamp}'
            
            if file_path:
                safe_name = file_path.replace('\\', '_').replace('/', '_').replace(':', '_')
                report_name += f'_{safe_name[:50]}'
            
            if output_format == 'txt':
                report_file = os.path.join(self.forensic_dir, f'{report_name}.txt')
                self._generate_txt_forensic_report(report_file, timeline, file_path, days)
            elif output_format == 'json':
                report_file = os.path.join(self.forensic_dir, f'{report_name}.json')
                self._generate_json_forensic_report(report_file, timeline, file_path, days)
            elif output_format == 'html':
                report_file = os.path.join(self.forensic_dir, f'{report_name}.html')
                self._generate_html_forensic_report(report_file, timeline, file_path, days)
            else:
                report_file = os.path.join(self.forensic_dir, f'{report_name}.txt')
                self._generate_txt_forensic_report(report_file, timeline, file_path, days)
            
            if self.colorama_available:
                print(f"{Fore.GREEN}✓ Forensic report generated: {report_file}{Style.RESET_ALL}")
            else:
                print(f"✓ Forensic report generated: {report_file}")
            
            return report_file
            
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Error generating forensic report: {e}{Style.RESET_ALL}")
            else:
                print(f"Error generating forensic report: {e}")
            return None
    
    def _generate_txt_forensic_report(self, report_file, timeline, file_path, days):
        """Generate text format forensic report"""
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("FORENSIC ANALYSIS REPORT".center(80) + "\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analysis Period: Last {days} days\n")
            f.write(f"Total Events: {len(timeline)}\n")
            if file_path:
                f.write(f"Target File: {file_path}\n")
            f.write("\n")
            
            # Summary statistics
            f.write("=" * 80 + "\n")
            f.write("SUMMARY STATISTICS".center(80) + "\n")
            f.write("=" * 80 + "\n\n")
            
            # Count by severity
            severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
            action_counts = {}
            
            for event in timeline:
                severity = event.get('severity', 'UNKNOWN')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                action = event.get('action', 'UNKNOWN')
                action_counts[action] = action_counts.get(action, 0) + 1
            
            f.write("Severity Distribution:\n")
            for severity, count in severity_counts.items():
                if count > 0:
                    f.write(f"  {severity}: {count}\n")
            
            f.write("\nAction Distribution:\n")
            for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"  {action}: {count}\n")
            
            # Timeline events
            f.write("\n" + "=" * 80 + "\n")
            f.write("EVENT TIMELINE".center(80) + "\n")
            f.write("=" * 80 + "\n\n")
            
            for event in timeline:
                time_str = event['time'].strftime('%Y-%m-%d %H:%M:%S')
                severity = event.get('severity', 'UNKNOWN')
                action = event.get('action', 'UNKNOWN')
                path = event.get('path', 'Unknown')
                
                f.write(f"[{time_str}] [{severity}] {action}: {path}\n")
                
                # Add details if available
                if event['type'] == 'alert':
                    data = event.get('data', {})
                    if data.get('size'):
                        size = data['size']
                        if isinstance(size, (int, float)):
                            if size < 1024:
                                size_str = f"{size} B"
                            elif size < 1024 * 1024:
                                size_str = f"{size/1024:.1f} KB"
                            else:
                                size_str = f"{size/(1024*1024):.1f} MB"
                            f.write(f"    Size: {size_str}\n")
                    
                    if data.get('src_path') and data.get('dest_path'):
                        f.write(f"    From: {data['src_path']}\n")
                        f.write(f"    To: {data['dest_path']}\n")
                
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("End of Report".center(80) + "\n")
            f.write("=" * 80 + "\n")
    
    def _generate_json_forensic_report(self, report_file, timeline, file_path, days):
        """Generate JSON format forensic report"""
        report_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'analysis_period_days': days,
                'total_events': len(timeline),
                'target_file': file_path,
                'version': '3.1.113'
            },
            'summary': self._generate_summary_stats(timeline),
            'timeline': [
                {
                    'timestamp': event['time'].isoformat(),
                    'type': event['type'],
                    'severity': event.get('severity', 'UNKNOWN'),
                    'action': event.get('action', 'UNKNOWN'),
                    'path': event.get('path', 'Unknown'),
                    'data': event.get('data', {})
                }
                for event in timeline
            ]
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
    
    def _generate_html_forensic_report(self, report_file, timeline, file_path, days):
        """Generate HTML format forensic report"""
        summary = self._generate_summary_stats(timeline)
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>DSTerminal Forensic Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h1, h2 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .card.critical {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .card.high {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .card.medium {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .card.low {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .card-number {{
            font-size: 2em;
            font-weight: bold;
        }}
        .card-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .severity-CRITICAL {{ color: #d32f2f; font-weight: bold; }}
        .severity-HIGH {{ color: #f57c00; font-weight: bold; }}
        .severity-MEDIUM {{ color: #fbc02d; }}
        .severity-LOW {{ color: #388e3c; }}
        .timestamp {{
            font-family: monospace;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 DSTerminal Forensic Analysis Report</h1>
        
        <div class="summary">
            <div class="card">
                <div class="card-number">{len(timeline)}</div>
                <div class="card-label">Total Events</div>
            </div>
            <div class="card critical">
                <div class="card-number">{summary.get('CRITICAL', 0)}</div>
                <div class="card-label">Critical Events</div>
            </div>
            <div class="card high">
                <div class="card-number">{summary.get('HIGH', 0)}</div>
                <div class="card-label">High Severity</div>
            </div>
            <div class="card medium">
                <div class="card-number">{summary.get('MEDIUM', 0)}</div>
                <div class="card-label">Medium Severity</div>
            </div>
            <div class="card low">
                <div class="card-number">{summary.get('LOW', 0)}</div>
                <div class="card-label">Low Severity</div>
            </div>
        </div>
        
        <h2>Event Timeline</h2>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Severity</th>
                    <th>Action</th>
                    <th>File Path</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for event in timeline[:500]:  # Limit to 500 events for performance
            time_str = event['time'].strftime('%Y-%m-%d %H:%M:%S')
            severity = event.get('severity', 'UNKNOWN')
            action = event.get('action', 'UNKNOWN')
            path = event.get('path', 'Unknown')
            
            # Truncate long paths
            if len(path) > 60:
                path = path[:57] + "..."
            
            html_content += f"""
                <tr>
                    <td class="timestamp">{time_str}</td>
                    <td class="severity-{severity}">{severity}</td>
                    <td>{action}</td>
                    <td title="{event.get('path', 'Unknown')}">{path}</td>
                </tr>
"""
        
        html_content += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>Generated by DSTerminal Integrity Monitor v3..1.113</p>
            <p>Report ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}</p>
            <p>Analysis Period: Last {days} days</p>
            {f'<p>Target File: {file_path}</p>' if file_path else ''}
        </div>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_summary_stats(self, timeline):
        """Generate summary statistics for forensic report"""
        stats = {
            'total_events': len(timeline),
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'INFO': 0,
            'actions': {}
        }
        
        for event in timeline:
            severity = event.get('severity', 'UNKNOWN')
            if severity in stats:
                stats[severity] = stats.get(severity, 0) + 1
            
            action = event.get('action', 'UNKNOWN')
            stats['actions'][action] = stats['actions'].get(action, 0) + 1
        
        return stats
    
    def find_suspicious_patterns(self, timeline=None, days=7):
        """Find suspicious patterns in event timeline"""
        if timeline is None:
            timeline = self.analyze_timeline(days=days)
        
        patterns = []
        
        # Pattern 1: Multiple file modifications in short time (possible ransomware)
        time_windows = {}
        for event in timeline:
            if event.get('action') == 'MODIFIED':
                hour_key = event['time'].strftime('%Y-%m-%d %H')
                time_windows[hour_key] = time_windows.get(hour_key, 0) + 1
        
        for hour, count in time_windows.items():
            if count > 100:  # More than 100 modifications in an hour
                patterns.append({
                    'type': 'RAPID_MODIFICATIONS',
                    'severity': 'HIGH',
                    'description': f'{count} file modifications detected in hour {hour}',
                    'timestamp': hour,
                    'count': count
                })
        
        # Pattern 2: Suspicious file extensions
        suspicious_extensions = ['.exe', '.dll', '.vbs', '.ps1', '.scr', '.bat']
        extension_counts = {}
        
        for event in timeline:
            if event.get('action') in ['CREATED', 'MODIFIED']:
                path = event.get('path', '')
                ext = os.path.splitext(path)[1].lower()
                if ext in suspicious_extensions:
                    extension_counts[ext] = extension_counts.get(ext, 0) + 1
        
        for ext, count in extension_counts.items():
            if count > 10:  # More than 10 suspicious files
                patterns.append({
                    'type': 'SUSPICIOUS_EXTENSIONS',
                    'severity': 'MEDIUM',
                    'description': f'{count} {ext} files created/modified',
                    'extension': ext,
                    'count': count
                })
        
        # Pattern 3: Files in suspicious locations
        suspicious_locations = ['temp', 'tmp', 'appdata', 'programdata', 'downloads']
        location_counts = {}
        
        for event in timeline:
            if event.get('action') in ['CREATED', 'MODIFIED']:
                path = event.get('path', '').lower()
                for loc in suspicious_locations:
                    if loc in path:
                        location_counts[loc] = location_counts.get(loc, 0) + 1
        
        for loc, count in location_counts.items():
            if count > 20:
                patterns.append({
                    'type': 'SUSPICIOUS_LOCATION',
                    'severity': 'MEDIUM',
                    'description': f'{count} files in {loc} directory',
                    'location': loc,
                    'count': count
                })
        
        # Pattern 4: Deleted critical files
        critical_deletions = []
        for event in timeline:
            if event.get('action') == 'DELETED':
                path = event.get('path', '').lower()
                if any(critical in path for critical in ['system32', 'windows', 'etc', 'boot']):
                    critical_deletions.append(event)
        
        if critical_deletions:
            patterns.append({
                'type': 'CRITICAL_DELETIONS',
                'severity': 'CRITICAL',
                'description': f'{len(critical_deletions)} critical system files deleted',
                'files': [e.get('path') for e in critical_deletions[:5]]
            })
        
        return patterns
    
    def generate_incident_report(self, start_time, end_time, incident_id=None):
        """Generate an incident-specific forensic report"""
        try:
            timeline = self.analyze_timeline(days=None, start_date=start_time, end_date=end_time)
            patterns = self.find_suspicious_patterns(timeline)
            
            incident_id = incident_id or f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            report_file = os.path.join(self.forensic_dir, f'incident_{incident_id}.txt')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"INCIDENT REPORT: {incident_id}".center(80) + "\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Incident ID: {incident_id}\n")
                f.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {(end_time - start_time).total_seconds():.0f} seconds\n")
                f.write(f"Total Events: {len(timeline)}\n\n")
                
                if patterns:
                    f.write("=" * 80 + "\n")
                    f.write("SUSPICIOUS PATTERNS DETECTED".center(80) + "\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for pattern in patterns:
                        f.write(f"[{pattern['severity']}] {pattern['type']}\n")
                        f.write(f"  Description: {pattern['description']}\n")
                        if 'files' in pattern:
                            f.write("  Affected Files:\n")
                            for file in pattern['files'][:10]:
                                f.write(f"    - {file}\n")
                        f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("EVENT TIMELINE".center(80) + "\n")
                f.write("=" * 80 + "\n\n")
                
                for event in timeline:
                    time_str = event['time'].strftime('%Y-%m-%d %H:%M:%S')
                    severity = event.get('severity', 'UNKNOWN')
                    action = event.get('action', 'UNKNOWN')
                    path = event.get('path', 'Unknown')
                    
                    f.write(f"[{time_str}] [{severity}] {action}: {path}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("RECOMMENDATIONS".center(80) + "\n")
                f.write("=" * 80 + "\n\n")
                
                if patterns:
                    for pattern in patterns:
                        if pattern['type'] == 'RAPID_MODIFICATIONS':
                            f.write("• Investigate potential ransomware activity\n")
                            f.write("  - Check for file encryption patterns\n")
                            f.write("  - Review running processes\n")
                            f.write("  - Isolate affected systems\n")
                        elif pattern['type'] == 'CRITICAL_DELETIONS':
                            f.write("• CRITICAL: System files were deleted\n")
                            f.write("  - Run system file checker: sfc /scannow\n")
                            f.write("  - Restore from backup immediately\n")
                            f.write("  - Check for unauthorized access\n")
                        elif pattern['type'] == 'SUSPICIOUS_EXTENSIONS':
                            f.write("• Suspicious executable files detected\n")
                            f.write("  - Scan with antivirus\n")
                            f.write("  - Check running processes\n")
                            f.write("  - Review startup items\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("End of Incident Report".center(80) + "\n")
                f.write("=" * 80 + "\n")
            
            if self.colorama_available:
                print(f"{Fore.GREEN}✓ Incident report generated: {report_file}{Style.RESET_ALL}")
            else:
                print(f"✓ Incident report generated: {report_file}")
            
            return report_file
            
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Error generating incident report: {e}{Style.RESET_ALL}")
            else:
                print(f"Error generating incident report: {e}")
            return None
    
    def export_evidence(self, file_paths, output_dir=None):
        """Export files as forensic evidence (copy to secure location)"""
        if output_dir is None:
            output_dir = os.path.join(self.forensic_dir, 'evidence')
        
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = []
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    # Create evidence filename with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    original_name = os.path.basename(file_path)
                    evidence_name = f"{timestamp}_{original_name}.evidence"
                    evidence_path = os.path.join(output_dir, evidence_name)
                    
                    # Copy file with metadata
                    shutil.copy2(file_path, evidence_path)
                    
                    # Create metadata file
                    metadata = {
                        'original_path': file_path,
                        'exported_time': datetime.now().isoformat(),
                        'file_size': os.path.getsize(file_path),
                        'file_hash': self.integrity_monitor._calculate_hash(file_path),
                        'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    }
                    
                    metadata_file = evidence_path + '.meta'
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, default=str)
                    
                    exported_files.append({
                        'original': file_path,
                        'evidence': evidence_path,
                        'metadata': metadata
                    })
                    
                    if self.colorama_available:
                        print(f"{Fore.GREEN}✓ Evidence exported: {evidence_path}{Style.RESET_ALL}")
                    else:
                        print(f"✓ Evidence exported: {evidence_path}")
                else:
                    if self.colorama_available:
                        print(f"{Fore.YELLOW}⚠ File not found: {file_path}{Style.RESET_ALL}")
                    else:
                        print(f"⚠ File not found: {file_path}")
                        
            except Exception as e:
                if self.colorama_available:
                    print(f"{Fore.RED}✗ Failed to export {file_path}: {e}{Style.RESET_ALL}")
                else:
                    print(f"✗ Failed to export {file_path}: {e}")
        
        return exported_files
    
class AutoRemediation:
    """Automatically handle integrity violations"""
    
    def __init__(self, integrity_monitor):
        self.integrity_monitor = integrity_monitor
        self.remediation_log = os.path.join(integrity_monitor.report_dir, 'remediation_log.json')
        self.quarantine_dir = os.path.join(integrity_monitor.report_dir, 'auto_quarantine')
        self.colorama_available = integrity_monitor.colorama_available
        
        # Create quarantine directory
        os.makedirs(self.quarantine_dir, exist_ok=True)
        
        # Load policies
        self.policies = self._load_policies()
    
    def _load_policies(self):
        """Load remediation policies"""
        policy_file = os.path.join(self.integrity_monitor.report_dir, 'remediation_policies.json')
        
        default_policies = {
            'critical_files': {
                'action': 'alert_and_restore',
                'backup_source': 'baseline',
                'notify': True,
                'severity_threshold': 'CRITICAL'
            },
            'suspicious_executables': {
                'action': 'quarantine',
                'notify': True,
                'severity_threshold': 'HIGH'
            },
            'config_changes': {
                'action': 'alert',
                'notify': True,
                'severity_threshold': 'MEDIUM'
            },
            'unauthorized_access': {
                'action': 'block_and_alert',
                'notify': True,
                'severity_threshold': 'HIGH'
            },
            'log_files': {
                'action': 'alert',
                'notify': False,
                'severity_threshold': 'LOW'
            }
        }
        
        if os.path.exists(policy_file):
            try:
                with open(policy_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                if self.colorama_available:
                    print(f"{Fore.YELLOW}⚠ Could not load policies, using defaults: {e}{Style.RESET_ALL}")
                else:
                    print(f"⚠ Could not load policies, using defaults: {e}")
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
        
        # Log remediation action
        self._log_remediation(result)
        
        # Notify if configured
        if self.policies.get(self._get_policy_key(violation), {}).get('notify', False):
            self._notify_admin(result)
        
        return result
    
    def _determine_action(self, violation):
        """Determine appropriate action for violation"""
        path = violation.get('path', '')
        severity = violation.get('severity', 'LOW')
        
        # Check critical system files
        if any(critical in path.lower() for critical in ['system32', 'etc', 'boot', 'kernel']):
            return self.policies.get('critical_files', {}).get('action', 'alert_and_restore')
        
        # Check suspicious executables
        if any(suspicious in path.lower() for suspicious in ['.exe', '.dll', '.scr', '.vbs', '.ps1']):
            if 'temp' in path.lower() or 'download' in path.lower() or 'appdata' in path.lower():
                return self.policies.get('suspicious_executables', {}).get('action', 'quarantine')
        
        # Check configuration files
        if 'config' in path.lower():
            return self.policies.get('config_changes', {}).get('action', 'alert')
        
        # Check log files
        if 'log' in path.lower() or '.log' in path.lower():
            return self.policies.get('log_files', {}).get('action', 'alert')
        
        # Check severity-based actions
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
            
            # Create quarantine path
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            quarantine_path = os.path.join(self.quarantine_dir, f"{timestamp}_{filename}.quarantine")
            
            # Move file to quarantine
            shutil.move(file_path, quarantine_path)
            
            # Save metadata
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
            
            # Check if we have a backup in baseline
            baseline = self.integrity_monitor._load_baseline()
            if not baseline:
                result['success'] = False
                result['details']['error'] = "No baseline available for restoration"
                return result
            
            # Find file in baseline
            all_files = []
            for category in ['files', 'configs', 'critical_files']:
                all_files.extend(baseline.get(category, []))
            
            baseline_file = next((f for f in all_files if f['path'] == file_path), None)
            
            if not baseline_file:
                result['success'] = False
                result['details']['error'] = f"No baseline data for: {file_path}"
                return result
            
            # Create backup of current file before restore
            if os.path.exists(file_path):
                backup_path = file_path + '.backup'
                shutil.copy2(file_path, backup_path)
                result['details']['backup_created'] = backup_path
            
            # In a real implementation, you'd restore from actual backup
            # This is a placeholder that creates a marker file
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
            
            # Change permissions to read-only (block modification)
            if platform.system().lower() == 'windows':
                # Windows: set read-only attribute
                import ctypes
                FILE_ATTRIBUTE_READONLY = 0x1
                ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_READONLY)
            else:
                # Unix: remove write permissions
                current_perms = os.stat(file_path).st_mode
                os.chmod(file_path, current_perms & ~0o222)  # Remove write for all
            
            # Create block marker
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
            # Load existing log
            if os.path.exists(self.remediation_log):
                with open(self.remediation_log, 'r', encoding='utf-8') as f:
                    try:
                        log = json.load(f)
                    except json.JSONDecodeError:
                        log = []
            else:
                log = []
            
            # Add new entry
            log.append(result)
            
            # Keep last 1000 entries
            if len(log) > 1000:
                log = log[-1000:]
            
            # Save log
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
    
    def restore_from_quarantine(self, quarantine_path):
        """Restore a file from quarantine"""
        try:
            if not os.path.exists(quarantine_path):
                return False, f"Quarantine file not found: {quarantine_path}"
            
            # Load metadata
            metadata_file = quarantine_path + '.meta'
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                original_path = metadata.get('original_path')
            else:
                # Try to extract original path from filename
                original_path = quarantine_path.replace('.quarantine', '')
                if '.quarantine' in original_path:
                    original_path = original_path.split('_', 1)[1] if '_' in original_path else original_path
            
            # Restore file
            shutil.move(quarantine_path, original_path)
            
            # Clean up metadata
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            
            if self.colorama_available:
                print(f"{Fore.GREEN}✓ File restored to: {original_path}{Style.RESET_ALL}")
            else:
                print(f"✓ File restored to: {original_path}")
            
            return True, f"Restored to {original_path}"
            
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}✗ Restore failed: {e}{Style.RESET_ALL}")
            else:
                print(f"✗ Restore failed: {e}")
            return False, str(e)
    
    def list_quarantined_files(self):
        """List all quarantined files"""
        try:
            quarantined = []
            for file in os.listdir(self.quarantine_dir):
                if file.endswith('.quarantine'):
                    file_path = os.path.join(self.quarantine_dir, file)
                    size = os.path.getsize(file_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Try to load metadata
                    metadata_file = file_path + '.meta'
                    original_path = 'Unknown'
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            original_path = metadata.get('original_path', 'Unknown')
                    
                    quarantined.append({
                        'file': file,
                        'path': file_path,
                        'size': size,
                        'modified': modified,
                        'original_path': original_path
                    })
            
            return quarantined
            
        except Exception as e:
            if self.colorama_available:
                print(f"{Fore.RED}Failed to list quarantined files: {e}{Style.RESET_ALL}")
            else:
                print(f"Failed to list quarantined files: {e}")
            return []


# For testing
if __name__ == "__main__":
    print("=" * 60)
    print("DSTERMINAL INTEGRITY MONITOR")
    print("=" * 60)
    print(f"Workspace: {WORKSPACE}")
    print()
    
    # Test initialization
    monitor = SystemIntegrityMonitor()
    print("\n✓ Module loaded successfully")
    print(f"✓ All reports will be saved to: {WORKSPACE}/integrity_reports/")