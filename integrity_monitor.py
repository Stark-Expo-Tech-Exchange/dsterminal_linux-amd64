#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DSTerminal Integrity Monitor Module
Comprehensive system integrity monitoring with real-time alerts
All reports saved to DSTerminal workspace
"""

import sys
import os
import json
from pathlib import Path
import hashlib
import time
import shutil
import platform
import threading
import glob
from datetime import datetime, timedelta
import re

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
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    DIM = '\033[2m'
    BRIGHT = '\033[1m'
    LIGHTRED_EX = '\033[91m'
    LIGHTGREEN_EX = '\033[92m'
    LIGHTYELLOW_EX = '\033[93m'
    LIGHTCYAN_EX = '\033[96m'
    LIGHTMAGENTA_EX = '\033[95m'
    LIGHTBLUE_EX = '\033[94m'
    LIGHTWHITE_EX = '\033[97m'
    
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
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
except ImportError:
    COLORS_AVAILABLE = False
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
    Back = type('Back', (), {
        'RESET': '\033[49m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m'
    })

# ============================================================
# TRY TO IMPORT PSUTIL
# ============================================================
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ============================================================
# TRY TO IMPORT WATCHDOG
# ============================================================
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
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

# ============================================================
# WORKSPACE MANAGEMENT
# ============================================================

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


# ============================================================
# SYSTEM INTEGRITY MONITOR - MAIN CLASS
# ============================================================

class SystemIntegrityMonitor:
    def __init__(self):
        self.workspace = str(WORKSPACE)
        self.db_file = os.path.join(self.workspace, "logs", "system_integrity.db")
        self.report_dir = os.path.join(self.workspace, "integrity_reports")
        self.baseline_dir = os.path.join(self.workspace, "baselines")
        self.alerts_dir = os.path.join(self.workspace, "alerts")
        self.quarantine_dir = os.path.join(self.workspace, "quarantine")
        
        try:
            self.terminal_width = shutil.get_terminal_size().columns
        except:
            self.terminal_width = 80
        
        self.colorama_available = COLORS_AVAILABLE
        
        for dir_path in [self.report_dir, self.baseline_dir, self.alerts_dir, self.quarantine_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        self.system_paths = self._get_system_paths()
        self.alert_manager = AlertManager(self)
        self.auto_remediation = AutoRemediation(self)
        self.forensic = ForensicAnalyzer(self)
        
        if self.colorama_available:
            print(f"{Fore.GREEN}✓ Auto-remediation initialized{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Forensic Analyzer initialized{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ System Integrity Monitor initialized{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  Workspace: {self.workspace}{Style.RESET_ALL}")
        else:
            print("✓ Auto-remediation initialized")
            print("✓ Forensic Analyzer initialized")
            print("✓ System Integrity Monitor initialized")
            print(f"  Workspace: {self.workspace}")

    # ============================================================
    # THEMED SCAN METHODS WITH BOLD CONTINUOUS BOX DRAWING
    # ============================================================
    def _display_alert_box(self, message: str, alert_type: str = "INFO", blink: bool = True):
        """
        Display a colored neon animated blinking box centered in the terminal.
        
        Args:
            message: The message to display
            alert_type: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO', 'SUCCESS'
            blink: Whether to animate the blink effect
        """
        import shutil
        import time
        
        # ANSI blink codes
        BLINK_ON = '\033[5m'
        BLINK_OFF = '\033[25m'
        
        # Color mapping
        colors = {
            'CRITICAL': {'fg': Fore.RED + Style.BRIGHT, 'border': Fore.RED, 'icon': '🚨'},
            'HIGH': {'fg': Fore.YELLOW + Style.BRIGHT, 'border': Fore.YELLOW, 'icon': '⚠️'},
            'MEDIUM': {'fg': Fore.MAGENTA + Style.BRIGHT, 'border': Fore.MAGENTA, 'icon': '🔶'},
            'LOW': {'fg': Fore.CYAN + Style.BRIGHT, 'border': Fore.CYAN, 'icon': '🔷'},
            'INFO': {'fg': Fore.LIGHTCYAN_EX, 'border': Fore.CYAN, 'icon': 'ℹ️'},
            'SUCCESS': {'fg': Fore.GREEN + Style.BRIGHT, 'border': Fore.GREEN, 'icon': '✅'}
        }
        
        color = colors.get(alert_type, colors['INFO'])
        
        try:
            term = shutil.get_terminal_size((100, 30))
            term_width = term.columns
        except:
            term_width = 80
        
        # Box width - responsive
        box_width = min(term_width - 6, 90)
        box_width = max(box_width, 60)
        left_margin = max(0, (term_width - box_width) // 2)
        inner = box_width - 4
        
        # Box drawing characters
        TOP_LEFT = '┏'
        TOP_RIGHT = '┓'
        BOTTOM_LEFT = '┗'
        BOTTOM_RIGHT = '┛'
        HORIZONTAL = '━'
        VERTICAL = '┃'
        T_RIGHT = '┣'
        T_LEFT = '┫'
        
        # Prepare message lines
        lines = message.split('\n')
        wrapped_lines = []
        for line in lines:
            if not line.strip():
                wrapped_lines.append("")
                continue
            # Truncate if too long
            if len(line) > inner:
                wrapped_lines.append(line[:inner-3] + "...")
            else:
                wrapped_lines.append(line)
        
        # Ensure minimum height
        if len(wrapped_lines) < 3:
            wrapped_lines = [""] + wrapped_lines + [""]
        
        # Build box parts
        top = color['border'] + TOP_LEFT + HORIZONTAL * (box_width - 2) + TOP_RIGHT + Style.RESET_ALL
        mid = color['border'] + T_RIGHT + HORIZONTAL * (box_width - 2) + T_LEFT + Style.RESET_ALL
        bot = color['border'] + BOTTOM_LEFT + HORIZONTAL * (box_width - 2) + BOTTOM_RIGHT + Style.RESET_ALL
        
        # Title
        title_text = f" {color['icon']} {alert_type} ALERT {color['icon']} ".center(box_width - 2)
        
        def render_box(blink_state: bool = True):
            """Render the box with optional blink"""
            blink_char = BLINK_ON if blink_state and blink else BLINK_OFF
            
            # Clear area
            sys.stdout.write('\r' + ' ' * term_width + '\r')
            
            # Print top
            print(" " * left_margin + top)
            
            # Print title with blink
            print(" " * left_margin + color['border'] + VERTICAL + Style.RESET_ALL + 
                f"{blink_char}{color['fg']}{title_text}{Style.RESET_ALL}{BLINK_OFF}" + 
                color['border'] + VERTICAL + Style.RESET_ALL)
            
            # Print separator
            print(" " * left_margin + mid)
            
            # Print content lines
            for line in wrapped_lines:
                if line.strip():
                    print(" " * left_margin + color['border'] + VERTICAL + Style.RESET_ALL + 
                        f"  {color['fg']}{line}{Style.RESET_ALL}" + 
                        " " * (inner - len(line)) + 
                        color['border'] + VERTICAL + Style.RESET_ALL)
                else:
                    print(" " * left_margin + color['border'] + VERTICAL + Style.RESET_ALL + 
                        " " * inner + 
                        color['border'] + VERTICAL + Style.RESET_ALL)
            
            # Print bottom
            print(" " * left_margin + bot)
            sys.stdout.flush()
        
        # Animated blink loop
        if blink:
            try:
                for _ in range(8):  # Blink 8 times (4 cycles)
                    render_box(True)
                    time.sleep(0.2)
                    render_box(False)
                    time.sleep(0.2)
            except KeyboardInterrupt:
                pass
            finally:
                # Final render with blink off
                render_box(False)
                print()  # Add extra newline
        else:
            render_box(False)
            print()

        # ==============================================================

    def _draw_glow_box(self, title: str, content_lines: list, 
                       title_color: str, border_color: str,
                       content_color: str = None, width: int = None):
        """Draw a glowing neon hacker-styled centered box with bold continuous lines."""
        import textwrap
        
        content_color = content_color or Fore.LIGHTGREEN_EX
        
        try:
            term = shutil.get_terminal_size((100, 30))
            term_width = term.columns
        except:
            term_width = 80
        
        if width is None:
            width = min(term_width - 6, 110)
        width = max(width, 60)
        left_margin = max(0, (term_width - width) // 2)
        inner = width - 4
        
        wrapped = []
        for line in content_lines:
            if not line.strip():
                wrapped.append("")
                continue
            try:
                line = line.rstrip()
                wrapped.extend(textwrap.wrap(line, inner, break_long_words=False, replace_whitespace=False))
            except:
                wrapped.append(line[:inner] if len(line) > inner else line)
        
        # Bold continuous box drawing
        TOP_LEFT = '┏'
        TOP_RIGHT = '┓'
        BOTTOM_LEFT = '┗'
        BOTTOM_RIGHT = '┛'
        HORIZONTAL = '━'
        VERTICAL = '┃'
        T_RIGHT = '┣'
        T_LEFT = '┫'
        
        top = border_color + TOP_LEFT + HORIZONTAL * (width - 2) + TOP_RIGHT + Style.RESET_ALL
        mid = border_color + T_RIGHT + HORIZONTAL * (width - 2) + T_LEFT + Style.RESET_ALL
        bot = border_color + BOTTOM_LEFT + HORIZONTAL * (width - 2) + BOTTOM_RIGHT + Style.RESET_ALL
        
        title_text = f" {title} ".center(width - 2)
        title_line = title_color + VERTICAL + title_text + VERTICAL + Style.RESET_ALL
        
        try:
            print()
            print(" " * left_margin + top)
            print(" " * left_margin + title_line)
            print(" " * left_margin + mid)
        except:
            pass
        
        for line in wrapped:
            try:
                print(" " * left_margin + border_color + VERTICAL + " " + Style.RESET_ALL, end="")
                padded_line = line.ljust(inner)
                print(f"{content_color}{padded_line}{Style.RESET_ALL}", end="")
                print(" " * left_margin + border_color + VERTICAL + Style.RESET_ALL)
                time.sleep(0.01)
            except:
                pass
        
        try:
            print(" " * left_margin + bot)
            print()
            time.sleep(0.3)
        except:
            pass

    def _animated_spinner(self, stop_event, message, spinner_type='default'):
        """Animated spinner with different styles"""
        spinners = {
            'default': ['◴', '◷', '◶', '◵'],
            'braille': ['⠾', '⠽', '⠻', '⠟', '⠯', '⠷'],
            'blocks': ['▉', '▊', '▋', '▌', '▍', '▎', '▏', '▎', '▍', '▌', '▋', '▊'],
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

    def _animated_progress_bar(self, current, total, message, width=40):
        """Enhanced animated progress bar with gradient effect"""
        if total <= 0:
            total = 1
        
        percent = (current / total) * 100
        filled = int(width * current // total) if total > 0 else 0
    
        if percent < 30:
            bar_color = Fore.CYAN
        elif percent < 70:
            bar_color = Fore.YELLOW
        else:
            bar_color = Fore.GREEN
    
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

    def _scan_category(self, category, results, target_key=None):
        """Scan a specific category with hacker-themed box display"""
        if target_key is None:
            target_key = category

        category_styles = {
            'configs': {'icon': '⚙️', 'title': 'CONFIGURATION FILES', 'color': Fore.CYAN},
            'logs': {'icon': '📋', 'title': 'LOG FILES', 'color': Fore.BLUE},
            'databases': {'icon': '🗄️', 'title': 'DATABASES', 'color': Fore.MAGENTA},
            'system_files': {'icon': '🔒', 'title': 'CRITICAL SYSTEM FILES', 'color': Fore.RED},
            'user_files': {'icon': '👤', 'title': 'USER FILES', 'color': Fore.GREEN}
        }

        style = category_styles.get(category, {'icon': '📁', 'title': category.upper(), 'color': Fore.WHITE})
        
        # Display hacker-themed box
        display_lines = [
            f"{style['icon']}  SCANNING {style['title']}  {style['icon']}"
        ]
        
        self._draw_glow_box(
            style['title'],
            display_lines,
            title_color=style['color'],
            border_color=style['color'],
            content_color=style['color']
        )

        count = 0
        total_paths = len(self.system_paths.get(category, []))
        
        if total_paths == 0:
            total_paths = 1

        for i, path in enumerate(self.system_paths.get(category, []), 1):
            if os.path.exists(path):
                self._animated_progress_bar(i, total_paths, f"Scanning {category}", 40)
                count += self._scan_directory(path, results[target_key], category)

        terminal_width = shutil.get_terminal_size().columns
        print(f"\r{' ' * terminal_width}", end='\r')

        result_lines = [f" Found {count} {category} files"]
        self._draw_glow_box(
            "✓ COMPLETE",
            result_lines,
            title_color=Fore.GREEN,
            border_color=Fore.GREEN,
            content_color=Fore.LIGHTGREEN_EX
        )

        return count

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
        elif system == 'darwin':
            paths.update({
                'configs': ['/etc', '/Library/Preferences', os.path.expanduser('~/Library/Preferences')],
                'logs': ['/var/log', '/Library/Logs', os.path.expanduser('~/Library/Logs')],
                'databases': ['/usr/local/var/mysql', os.path.expanduser('~/Library/Application Support')],
                'system_files': ['/etc/hosts', '/etc/passwd', '/etc/ssh/sshd_config'],
            })
        
        paths['user_files'].extend([
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Desktop'),
        ])
        
        return paths

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
        
        # Display hacker-themed header
        header_lines = [
            "⚡ SYSTEM SCAN INITIALIZED ⚡",
            f"Target: {platform.node()}",
            f"OS: {platform.system()} {platform.release()}",
            f"Arch: {platform.machine()}"
        ]
        self._draw_glow_box(
            "🔍 INTEGRITY SCAN",
            header_lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTGREEN_EX
        )
        
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
        
        # Show completion
        completion_lines = [
            f"✓ Scan completed successfully",
            f"✓ Results saved to workspace",
            f"📁 {scan_file}"
        ]
        self._draw_glow_box(
            "✅ SCAN COMPLETE",
            completion_lines,
            title_color=Fore.GREEN,
            border_color=Fore.GREEN,
            content_color=Fore.LIGHTGREEN_EX
        )
        
        return results

    def create_baseline(self, scan_results=None):
        """Create a baseline of system state"""
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
        
        latest_file = os.path.join(self.baseline_dir, 'latest_baseline.json')
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, default=str)
        
        lines = [f"✓ Baseline created successfully", f"📁 {baseline_file}"]
        self._draw_glow_box(
            "📊 BASELINE CREATED",
            lines,
            title_color=Fore.CYAN,
            border_color=Fore.CYAN,
            content_color=Fore.LIGHTGREEN_EX
        )
        
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
            lines = ["No baseline found. Creating initial baseline..."]
            self._draw_glow_box(
                "⚠️ NO BASELINE",
                lines,
                title_color=Fore.YELLOW,
                border_color=Fore.YELLOW,
                content_color=Fore.YELLOW
            )
            self.create_baseline(scan_results)
            return None
        
        lines = ["🔍 Analyzing system integrity..."]
        self._draw_glow_box(
            "🔍 INTEGRITY CHECK",
            lines,
            title_color=Fore.MAGENTA,
            border_color=Fore.MAGENTA,
            content_color=Fore.LIGHTCYAN_EX
        )
        
        changes = {
            'new_files': [],
            'modified_files': [],
            'deleted_files': [],
            'permission_changes': []
        }
        
        all_baseline = {}
        all_current = {}
        
        for category in ['files', 'configs', 'logs', 'databases', 'critical_files']:
            for item in baseline.get(category, []):
                all_baseline[item['path']] = item
            for item in scan_results.get(category, []):
                all_current[item['path']] = item
        
        total_items = len(all_baseline)
        if total_items == 0:
            total_items = 1
            
        for i, (path, baseline_info) in enumerate(all_baseline.items(), 1):
            self._animated_progress_bar(i, total_items, "Analyzing files", 40)
            
            if path not in all_current:
                changes['deleted_files'].append({
                    'path': path,
                    'baseline_info': baseline_info,
                    'severity': 'HIGH' if baseline_info.get('category') == 'system' else 'MEDIUM'
                })
                continue
            
            current_info = all_current[path]
            
            if baseline_info.get('hash') != current_info.get('hash'):
                change_type = self._analyze_change(baseline_info, current_info)
                changes['modified_files'].append({
                    'path': path,
                    'baseline': baseline_info,
                    'current': current_info,
                    'change_type': change_type,
                    'severity': self._determine_severity(path, 'modified')
                })
            
            if baseline_info.get('permissions') != current_info.get('permissions'):
                changes['permission_changes'].append({
                    'path': path,
                    'old_perms': baseline_info.get('permissions'),
                    'new_perms': current_info.get('permissions')
                })
        
        for path, current_info in all_current.items():
            if path not in all_baseline:
                changes['new_files'].append({
                    'path': path,
                    'current_info': current_info,
                    'severity': self._determine_severity(path, 'new')
                })
        
        # ============================================================
        # DISPLAY RESULTS WITH ANIMATED ALERT BOX
        # ============================================================
        
        # Count changes and violations
        total_changes = len(changes['new_files']) + len(changes['modified_files']) + len(changes['deleted_files']) + len(changes['permission_changes'])
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for change_type in ['new_files', 'modified_files', 'deleted_files']:
            for item in changes[change_type]:
                severity = item.get('severity', 'LOW')
                if severity == 'CRITICAL':
                    critical_count += 1
                elif severity == 'HIGH':
                    high_count += 1
                elif severity == 'MEDIUM':
                    medium_count += 1
                elif severity == 'LOW':
                    low_count += 1
        
        # Permission changes
        permission_changes = len(changes['permission_changes'])
        
        # Determine if there are any violations
        has_violations = (critical_count > 0 or high_count > 0 or medium_count > 0 or low_count > 0)
        has_critical = critical_count > 0
        has_high = high_count > 0
        
        # Show animated alert based on findings
        if has_critical:
            alert_msg = f"""
    🚨 CRITICAL INTEGRITY VIOLATIONS DETECTED!

    Total Changes: {total_changes}
    CRITICAL: {critical_count}
    HIGH: {high_count}
    MEDIUM: {medium_count}
    LOW: {low_count}
    Permission Changes: {permission_changes}
    
    ⚠️  IMMEDIATE ACTION REQUIRED!
    • Review critical changes immediately
    • Check for unauthorized modifications
    • Verify system integrity
    • Run full antivirus scan
    • Isolate system if necessary
    """
            self._display_alert_box(alert_msg, "CRITICAL", blink=True)
        elif has_high:
            alert_msg = f"""
    ⚠️  HIGH INTEGRITY VIOLATIONS DETECTED!

    Total Changes: {total_changes}
    HIGH: {high_count}
    MEDIUM: {medium_count}
    LOW: {low_count}
    Permission Changes: {permission_changes}
    
    🔍 Action Required:
    • Review high severity changes ASAP
    • Verify file integrity
    • Check for suspicious activity
    • Monitor for further changes
    • Investigate root cause
    """
            self._display_alert_box(alert_msg, "HIGH", blink=True)
        elif has_violations and total_changes > 0:
            alert_msg = f"""
    🔍 INTEGRITY CHANGES DETECTED

    Total Changes: {total_changes}
    New Files: {len(changes['new_files'])}
    Modified: {len(changes['modified_files'])}
    Deleted: {len(changes['deleted_files'])}
    Permission Changes: {permission_changes}
    
    📋 Review the report for details
    • Check modified files
    • Verify new files are legitimate
    • Review deleted files
    """
            self._display_alert_box(alert_msg, "INFO", blink=False)
        else:
            alert_msg = """
    ✅ SYSTEM INTEGRITY VERIFIED

    ✓ No changes detected
    ✓ System is secure
    ✓ All integrity checks passed
    
    📋 Continue normal operations
    🔄 Regular monitoring active
    """
            self._display_alert_box(alert_msg, "SUCCESS", blink=False)
        
        # Also show the summary box for reference
        summary_lines = [
            f"📊 New Files: {len(changes['new_files'])}",
            f"📝 Modified: {len(changes['modified_files'])}",
            f"🗑️ Deleted: {len(changes['deleted_files'])}",
            f"🔑 Permission Changes: {permission_changes}"
        ]
        self._draw_glow_box(
            "📊 INTEGRITY CHECK RESULTS",
            summary_lines,
            title_color=Fore.LIGHTCYAN_EX,
            border_color=Fore.LIGHTCYAN_EX,
            content_color=Fore.LIGHTGREEN_EX
        )
        
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
        """Generate a text report"""
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
                f.write("INTEGRITY FINDINGS\n")
                f.write("-" * 40 + "\n\n")
                f.write(f"New Files: {len(changes.get('new_files', []))}\n")
                f.write(f"Modified Files: {len(changes.get('modified_files', []))}\n")
                f.write(f"Deleted Files: {len(changes.get('deleted_files', []))}\n")
                f.write(f"Permission Changes: {len(changes.get('permission_changes', []))}\n\n")
        
        lines = [f"✓ Text report saved: {report_file}"]
        self._draw_glow_box(
            "📄 REPORT GENERATED",
            lines,
            title_color=Fore.CYAN,
            border_color=Fore.CYAN,
            content_color=Fore.LIGHTGREEN_EX
        )
        
        return report_file

    def generate_json_report(self, changes=None, scan_results=None):
        """Generate a JSON report"""
        if scan_results is None:
            scan_results = self.scan_system()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.report_dir, f'integrity_report_{timestamp}.json')
        
        report_data = {
            'metadata': {'generated': datetime.now().isoformat(), 'workspace': self.workspace},
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
        
        lines = [f"✓ JSON report saved: {report_file}"]
        self._draw_glow_box(
            "📄 JSON REPORT GENERATED",
            lines,
            title_color=Fore.CYAN,
            border_color=Fore.CYAN,
            content_color=Fore.LIGHTGREEN_EX
        )
        
        return report_file

    def generate_pdf_report(self, changes=None, scan_results=None):
        """Generate a PDF report"""
        lines = ["⚠️ PDF generation requires reportlab/fpdf2", "Install: pip install fpdf2"]
        self._draw_glow_box(
            "⚠️ PDF NOT AVAILABLE",
            lines,
            title_color=Fore.YELLOW,
            border_color=Fore.YELLOW,
            content_color=Fore.YELLOW
        )
        return None

    def generate_all_reports(self, changes, scan_results=None):
        """Generate all report formats"""
        if scan_results is None:
            scan_results = self.scan_system()
        
        reports = {}
        reports['txt'] = self.generate_report(changes, scan_results)
        reports['json'] = self.generate_json_report(changes, scan_results)
        reports['pdf'] = self.generate_pdf_report(changes, scan_results)
        
        lines = [
            "✓ All reports saved to workspace",
            f"📁 {self.report_dir}"
        ]
        self._draw_glow_box(
            "📊 ALL REPORTS GENERATED",
            lines,
            title_color=Fore.GREEN,
            border_color=Fore.GREEN,
            content_color=Fore.LIGHTGREEN_EX
        )
        
        return reports

    def full_integrity_check(self):
        """Perform full system integrity check"""
        scan_results = self.scan_system()
        changes = self.check_integrity(scan_results)
        
        if changes:
            self.generate_all_reports(changes, scan_results)
            lines = ["✓ Full integrity check complete", f"📁 Reports saved to: {self.report_dir}"]
            self._draw_glow_box(
                "✅ INTEGRITY CHECK COMPLETE",
                lines,
                title_color=Fore.GREEN,
                border_color=Fore.GREEN,
                content_color=Fore.LIGHTGREEN_EX
            )
        else:
            lines = ["✓ System integrity is intact. No changes detected."]
            self._draw_glow_box(
                "✅ SYSTEM CLEAN",
                lines,
                title_color=Fore.GREEN,
                border_color=Fore.GREEN,
                content_color=Fore.LIGHTGREEN_EX
            )
        
        return changes


# ============================================================
# ALERT MANAGER
# ============================================================

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
        
        os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
        self._load_alerts()
    
    def _load_alerts(self):
        """Load existing alerts from file"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        self.alerts = json.loads(content)
        except:
            self.alerts = []
    
    def _save_alerts(self):
        """Save alerts to file"""
        if hasattr(self, '_saving'):
            return
        self._saving = True
        
        try:
            os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
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
            
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(safe_alerts, f, indent=2, ensure_ascii=False, default=str)
        except:
            pass
        finally:
            self._saving = False
    
    def start_monitoring(self, paths=None):
        """Start real-time monitoring"""
        if not WATCHDOG_AVAILABLE:
            print(f"{Fore.RED}⚠️ Watchdog not installed. Install: pip install watchdog{Style.RESET_ALL}")
            return
        
        if self.running:
            print(f"{Fore.YELLOW}⚠️ Monitoring already running{Style.RESET_ALL}")
            return
        
        if paths is None:
            paths = [os.path.expanduser('~')]
        
        self.monitored_paths = paths
        self.running = True
        
        self.observer = Observer()
        handler = RealTimeHandler(self)
        
        for path in paths:
            if os.path.exists(path):
                try:
                    self.observer.schedule(handler, path, recursive=True)
                    print(f"{Fore.GREEN}✓ Monitoring: {path}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}✗ Failed to monitor {path}: {e}{Style.RESET_ALL}")
        
        if self.observer:
            self.observer.start()
            print(f"\n{Fore.GREEN}✓ Real-time monitoring started{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Press Ctrl+C to stop monitoring{Style.RESET_ALL}\n")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.running = False
        print(f"{Fore.YELLOW}✓ Real-time monitoring stopped{Style.RESET_ALL}")
    
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
            print(f"{Fore.RED}✗ Failed to add alert: {e}{Style.RESET_ALL}")
    
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
        
        alert_lines = [
            f"🔴 [{severity}] {alert.get('type', 'UNKNOWN')}",
            f"📁 {alert.get('path', 'Unknown')}"
        ]
        
        if alert.get('size'):
            size = alert['size']
            if isinstance(size, (int, float)):
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                alert_lines.append(f"📦 Size: {size_str}")
        
        self.integrity_monitor._draw_glow_box(
            f"🚨 SECURITY ALERT [{severity}]",
            alert_lines,
            title_color=color,
            border_color=color,
            content_color=color
        )
    
    def get_alerts(self, severity=None, limit=100):
        """Get recent alerts"""
        if severity:
            return [a for a in self.alerts if a.get('severity') == severity][-limit:]
        return self.alerts[-limit:]


# ============================================================
# REAL TIME HANDLER
# ============================================================

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


# ============================================================
# FORENSIC ANALYZER
# ============================================================

class ForensicAnalyzer:
    """Forensic analyzer for integrity monitoring"""
    
    def __init__(self, integrity_monitor):
        self.integrity_monitor = integrity_monitor
        self.report_dir = integrity_monitor.report_dir
        self.forensic_dir = os.path.join(self.report_dir, 'forensic')
        self.colorama_available = integrity_monitor.colorama_available
        os.makedirs(self.forensic_dir, exist_ok=True)
    
    def analyze_timeline(self, file_path=None, days=7):
        """Analyze timeline of changes"""
        try:
            alerts = self.integrity_monitor.alert_manager.alerts
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
            
            timeline = []
            for alert in alerts:
                alert_time = alert.get('timestamp')
                if isinstance(alert_time, str):
                    alert_time = datetime.fromisoformat(alert_time)
                
                if alert_time and start_date <= alert_time <= end_date:
                    if file_path is None or file_path in str(alert.get('path', '')):
                        timeline.append({
                            'time': alert_time,
                            'type': 'alert',
                            'data': alert,
                            'severity': alert.get('severity', 'UNKNOWN'),
                            'action': alert.get('type', 'UNKNOWN'),
                            'path': alert.get('path', alert.get('src_path', 'Unknown'))
                        })
            
            timeline.sort(key=lambda x: x['time'])
            return timeline
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error analyzing timeline: {e}{Style.RESET_ALL}")
            return []
    
    def generate_forensic_report(self, file_path=None, days=7):
        """Generate comprehensive forensic report"""
        try:
            timeline = self.analyze_timeline(file_path, days)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(self.forensic_dir, f'forensic_{timestamp}.txt')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("FORENSIC ANALYSIS REPORT".center(80) + "\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Analysis Period: Last {days} days\n")
                f.write(f"Total Events: {len(timeline)}\n\n")
                
                severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
                for event in timeline:
                    severity = event.get('severity', 'UNKNOWN')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                f.write("Severity Distribution:\n")
                for severity, count in severity_counts.items():
                    if count > 0:
                        f.write(f"  {severity}: {count}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("EVENT TIMELINE".center(80) + "\n")
                f.write("=" * 80 + "\n\n")
                
                for event in timeline:
                    time_str = event['time'].strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{time_str}] [{event.get('severity', 'UNKNOWN')}] {event.get('action', 'UNKNOWN')}: {event.get('path', 'Unknown')}\n")
            
            lines = [f"✓ Forensic report generated: {report_file}"]
            self.integrity_monitor._draw_glow_box(
                "🔍 FORENSIC REPORT",
                lines,
                title_color=Fore.MAGENTA,
                border_color=Fore.MAGENTA,
                content_color=Fore.LIGHTGREEN_EX
            )
            
            return report_file
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error generating forensic report: {e}{Style.RESET_ALL}")
            return None


# ============================================================
# AUTO REMEDIATION
# ============================================================

class AutoRemediation:
    """Automatically handle integrity violations"""
    
    def __init__(self, integrity_monitor):
        self.integrity_monitor = integrity_monitor
        self.quarantine_dir = os.path.join(integrity_monitor.report_dir, 'auto_quarantine')
        self.colorama_available = integrity_monitor.colorama_available
        os.makedirs(self.quarantine_dir, exist_ok=True)
    
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
            
            result['success'] = True
            result['details'] = {
                'quarantine_path': quarantine_path,
                'original_path': file_path
            }
            
            print(f"{Fore.YELLOW}✓ File quarantined: {quarantine_path}{Style.RESET_ALL}")
            
        except Exception as e:
            result['success'] = False
            result['details']['error'] = str(e)
            print(f"{Fore.RED}✗ Auto-quarantine failed: {e}{Style.RESET_ALL}")
        
        return result
    
    def handle_violation(self, violation):
        """Handle integrity violation"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'violation': violation,
            'action_taken': 'quarantine',
            'success': False,
            'details': {}
        }
        return self._quarantine_violation(violation, result)
    
    def restore_from_quarantine(self, quarantine_path):
        """Restore a file from quarantine"""
        try:
            if not os.path.exists(quarantine_path):
                return False, f"Quarantine file not found: {quarantine_path}"
            
            original_path = quarantine_path.replace('.quarantine', '')
            shutil.move(quarantine_path, original_path)
            
            print(f"{Fore.GREEN}✓ File restored to: {original_path}{Style.RESET_ALL}")
            return True, f"Restored to {original_path}"
            
        except Exception as e:
            print(f"{Fore.RED}✗ Restore failed: {e}{Style.RESET_ALL}")
            return False, str(e)
    
    def list_quarantined_files(self):
        """List all quarantined files"""
        try:
            quarantined = []
            for file in os.listdir(self.quarantine_dir):
                if file.endswith('.quarantine'):
                    file_path = os.path.join(self.quarantine_dir, file)
                    quarantined.append({
                        'file': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
            return quarantined
        except Exception as e:
            print(f"{Fore.RED}✗ Failed to list quarantined files: {e}{Style.RESET_ALL}")
            return []


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DSTERMINAL INTEGRITY MONITOR")
    print("=" * 60)
    print(f"Workspace: {WORKSPACE}")
    print()
    
    monitor = SystemIntegrityMonitor()
    print("\n✓ Module loaded successfully")
    print(f"✓ All reports saved to: {WORKSPACE}/integrity_reports/")