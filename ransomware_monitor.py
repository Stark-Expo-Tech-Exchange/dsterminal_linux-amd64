#!python
# -*- coding: utf-8 -*-


"""
Ransomware Detection & Monitoring System with Backup Recovery
Version: 4.0.0.113
Author: Spark Wilson Spink
Description: Real-time ransomware detection with automatic backup, recovery, and reporting
"""
import sys
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

 

"""
Ransomware Detection & Monitoring System with Backup Recovery
Version: 4.0.0.113
Author: Spark Wilson Spink
Description: Real-time ransomware detection with automatic backup, recovery, and reporting
"""

import sys
import os
import time
import threading
import platform
import hashlib
import json
import socket
import subprocess
import shutil
import re
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

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


import sys
import os
import time
import threading
import platform
import hashlib
import json
import socket
import subprocess
import shutil
import re
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

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
# SETUP COLORS (using colorama or fallback)
# ============================================================
RESET = Colors.END
BOLD = Colors.BOLD
CYAN = Colors.CYAN
YELLOW = Colors.YELLOW
GREEN = Colors.GREEN
RED = Colors.RED
BLUE = Colors.BLUE
MAGENTA = Colors.MAGENTA
DIM = Colors.DIM
BLINK = Colors.BLINK

# ============================================================
# TRY TO IMPORT PSUTIL
# ============================================================
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print(f"{YELLOW}⚠️ psutil not installed. Install with: pip install psutil{RESET}")

# ============================================================
# TRY TO IMPORT RICH
# ============================================================
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
    from rich.style import Style as RichStyle
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

# ============================================================
# TRY TO IMPORT WATCHDOG
# ============================================================
WATCHDOG_AVAILABLE = False
Observer = None
PollingObserver = None
FileSystemEventHandler = None

try:
    from watchdog.observers import Observer, PollingObserver
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    # dummy classes for when watchdog is not available
    class Observer:
        def start(self): pass
        def stop(self): pass
        def join(self): pass
        def schedule(self, *args, **kwargs): pass
    class PollingObserver(Observer): pass
    class FileSystemEventHandler:
        def on_created(self, event): pass
        def on_modified(self, event): pass
        def on_deleted(self, event): pass
        def on_moved(self, event): pass

# ============================================================
# TRY TO IMPORT REPORTLAB
# ============================================================
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as reportlab_colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ThreatLevel(Enum):
    """Threat level enumeration"""
    NORMAL = ("NORMAL", GREEN)
    LOW = ("LOW", GREEN)
    MEDIUM = ("MEDIUM", YELLOW)
    HIGH = ("HIGH", RED)
    CRITICAL = ("CRITICAL", RED)
    
    def __init__(self, label, color):
        self.label = label
        self.color = color
    
    def __str__(self):
        return f"{self.color}{self.label}{RESET}"


@dataclass
class FileEvent:
    """File system event data"""
    timestamp: str
    event_type: str
    path: str
    size: int = 0
    extension: str = ""
    is_suspicious: bool = False
    backup_path: str = ""
    hash: str = ""


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
    Real-time ransomware detection and monitoring system with backup.
    Monitors file system activity, processes, and behavioral patterns.
    """
    
    def __init__(self, session_id=None, log_callback=None, use_rich=True, backup_enabled=True):
        self.session_id = session_id or f"RANSOM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.log_callback = log_callback
        self.use_rich = use_rich and RICH_AVAILABLE
        self.console = Console() if self.use_rich else None
        self.backup_enabled = backup_enabled
        
        # State
        self.is_running = False
        self.ransomware_detected = False
        self.threat_level = ThreatLevel.NORMAL
        self.alert_callbacks = []
        
        # Backup configuration
        self.backup_root = Path.home() / "DSTerminal" / "ransomware_backups"
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir = self.backup_root / "quarantine"
        self.quarantine_dir.mkdir(exist_ok=True)
        self.backup_dir = self.backup_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.recycle_dir = self.backup_root / "recycle_bin"
        self.recycle_dir.mkdir(exist_ok=True)
        
        # Backup stats
        self.backup_stats = {
            'files_backed_up': 0,
            'files_restored': 0,
            'files_quarantined': 0,
            'backup_size_bytes': 0,
            'recycle_bin_size': 0,
            'last_backup': None,
            'total_backups': 0
        }
        
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
        self.deleted_files: List[FileEvent] = []
        
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
        self.polling_thread = None
        self.observer = None
        self._stop_event = threading.Event()
        self.event_queue = deque(maxlen=1000)
        
        # Backup settings - backup all files by default
        self.backup_extensions = set()  # Empty = backup all
        
        # Track seen files for polling
        self.seen_files = {}
        self.poll_interval = 2  # seconds

    def _get_monitored_dirs(self) -> List[Path]:
        """Discover directories to monitor"""
        home = Path.home()
        dirs = []

        if platform.system() == "Windows":
            user_dirs = [
                home / "Documents",
                home / "Desktop",
                home / "Downloads",
                home / "Pictures",
                home / "Music",
                home / "Videos",
                home / "AppData" / "Local" / "Temp",
                home / "AppData" / "Roaming",
                home / "AppData" / "Local",
                home / "OneDrive" if (home / "OneDrive").exists() else None,
                home / "Favorites",
                home / "Links",
                home / "Contacts",
                home / "Searches",
                home / "Saved Games",
                home / "3D Objects",
            ]

            for d in user_dirs:
                if d and d.exists():
                    dirs.append(d)

            common_dirs = [
                Path(os.environ.get("TEMP", "C:\\Temp")),
                Path(os.environ.get("TMP", "C:\\Temp")),
                Path("C:\\ProgramData"),
                Path("C:\\Users\\Public"),
                Path("C:\\Windows\\Temp"),
            ]

            for d in common_dirs:
                if d.exists():
                    try:
                        dirs.append(d)
                    except Exception:
                        pass
        else:
            user_dirs = [
                home,
                home / "Documents",
                home / "Desktop",
                home / "Downloads",
                home / "Pictures",
                home / "Music",
                home / "Videos",
                home / ".local",
                home / ".config",
                home / ".cache",
                home / ".ssh",
                home / ".gnupg",
            ]

            for d in user_dirs:
                if d.exists():
                    dirs.append(d)

            system_dirs = [
                Path("/tmp"),
                Path("/var/tmp"),
                Path("/var/log"),
                Path("/opt"),
                Path("/usr/local"),
            ]

            for d in system_dirs:
                if d.exists():
                    try:
                        dirs.append(d)
                    except Exception:
                        pass

        unique_dirs = []
        seen = set()

        for d in dirs:
            try:
                if str(d) not in seen and d.exists():
                    unique_dirs.append(d)
                    seen.add(str(d))
            except Exception:
                pass

        return unique_dirs
    
    def _get_watched_extensions(self) -> Set[str]:
        """Configure file extension monitoring - empty set = monitor all"""
        return set()
    
    def _should_monitor_file(self, file_path: Path) -> bool:
        """Check if a file should be monitored"""
        # If no extensions specified, monitor all
        if not self.watched_extensions:
            return True
        
        return file_path.suffix.lower() in self.watched_extensions

    def _get_suspicious_extensions(self) -> Set[str]:
        """Load suspicious file extensions commonly associated with ransomware"""
        return {
            '.encrypted', '.enc', '.crypt', '.locked', '.ransom',
            '.worm', '.virus', '.infected', '.crypto', '.crypter',
            '.lol', '.bad', '.hacked', '.breached', '.compromised',
            '.encrypt', '.decrypt', '.pay', '.pay2',
            '.key', '.key2', '.key3', '.decryptor', '.cryptor',
            '.0x', '.1x', '.2x', '.3x', '.4x', '.5x', '.6x', '.7x', '.8x', '.9x'
        }
    
    def _get_suspicious_names(self) -> Set[str]:
        """Load suspicious filenames commonly associated with ransomware notes"""
        return {
            'readme.txt', 'howtodecrypt.txt', 'decrypt.txt',
            'payment.txt', 'ransom.txt', 'help.txt',
            '!readme.txt', '!!!readme.txt', 'read_me.txt',
            'recover.txt', 'restore.txt', 'key.txt',
            'recover_files.txt', 'howto.txt', '!!readme!!.txt',
            'decrypt_instructions.txt', 'pay.txt', 'bitcoin.txt',
            'README.txt', 'READ_ME.txt', 'DECRYPT.txt',
            'HowToDecrypt.txt', 'RansomNote.txt'
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
                    "DEBUG": "blue",
                    "BACKUP": "magenta",
                    "EVENT": "white"
                }
                color = colors.get(level, "white")
                self.console.print(f"[{timestamp}] [bold {color}][RANSOM][/{color}] {message}")
            else:
                print(f"{Fore.CYAN}[{timestamp}] [RANSOM] {message}{Style.RESET_ALL}")

    def create_test_file(self):
        """Create a test file to demonstrate monitoring and backup"""
        test_dir = Path.home() / "Documents"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(test_file, 'w') as f:
                f.write(f"Test file for backup demonstration\n")
                f.write(f"Created: {datetime.now()}\n")
                f.write("This file will be backed up when deleted.\n")
                f.write("=" * 50 + "\n")
                f.write("Ransomware Monitor Test File\n")
                f.write("Delete this file to test backup and restore functionality.\n")
            self._log_message(f"✅ Created test file: {test_file.name}", "SUCCESS")
            print(f"\n{Fore.GREEN}✅ Test file created: {test_file}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📝 Delete this file to test backup and restore.{Style.RESET_ALL}")
            return str(test_file)
        except Exception as e:
            self._log_message(f"⚠️ Failed to create test file: {str(e)}", "WARNING")
            return None
    
    def _backup_file(self, file_path: Path, event_type: str = "deleted") -> Optional[Path]:
        """Create a backup of a file before deletion or modification"""
        if not self.backup_enabled:
            return None

        try:
            if not file_path.exists():
                self._log_message(f"⚠️ File not found for backup: {file_path.name}", "DEBUG")
                return None

            file_size = file_path.stat().st_size
            file_name = file_path.name

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"

            try:
                if event_type == "deleted":
                    backup_dir = self.recycle_dir / file_path.parent.relative_to(file_path.parent.anchor)
                else:
                    backup_dir = self.backup_dir / file_path.parent.relative_to(file_path.parent.anchor)
            except ValueError:
                sanitized_parent = str(file_path.parent).replace(':', '').replace('\\', '_').replace('/', '_')
                if event_type == "deleted":
                    backup_dir = self.recycle_dir / sanitized_parent
                else:
                    backup_dir = self.backup_dir / sanitized_parent

            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            file_hash = self._calculate_hash(file_path)

            self.backup_stats['files_backed_up'] += 1
            self.backup_stats['backup_size_bytes'] += file_size
            self.backup_stats['last_backup'] = datetime.now()
            self.backup_stats['total_backups'] += 1

            if event_type == "deleted":
                self.backup_stats['recycle_bin_size'] += file_size

            self._log_message(f"💾 Backed up: {file_name} ({file_size} bytes)", "BACKUP")
            return backup_path

        except Exception as e:
            self._log_message(f"⚠️ Backup failed for {file_path.name}: {str(e)}", "WARNING")
            return None
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return ""

    def _restore_from_backup(self, backup_path: Path) -> bool:
        """Restore a file from backup"""
        try:
            if not backup_path.exists():
                return False

            parts = backup_path.stem.rsplit('_', 1)
            if len(parts) == 2:
                original_name = parts[0] + backup_path.suffix
            else:
                original_name = backup_path.name

            if self.recycle_dir in backup_path.parents:
                relative = backup_path.relative_to(self.recycle_dir)
                restore_path = Path.home() / relative.parent / original_name
            else:
                relative = backup_path.relative_to(self.backup_dir)
                restore_path = Path.home() / relative.parent / original_name

            restore_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(backup_path, restore_path)

            self.backup_stats['files_restored'] += 1
            self._log_message(f"🔄 Restored: {backup_path.name} -> {restore_path}", "SUCCESS")

            try:
                backup_path.unlink()
            except:
                pass

            return True

        except Exception as e:
            self._log_message(f"⚠️ Restore failed: {str(e)}", "WARNING")
            return False
    
    def _quarantine_file(self, file_path: Path) -> Optional[Path]:
        """Quarantine a suspicious file"""
        try:
            if not file_path.exists():
                return None
            
            quarantine_path = self.quarantine_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.name}"
            
            shutil.move(str(file_path), str(quarantine_path))
            
            self.backup_stats['files_quarantined'] += 1
            self._log_message(f"🚨 Quarantined: {file_path.name}", "ERROR")
            
            return quarantine_path
            
        except Exception as e:
            self._log_message(f"⚠️ Quarantine failed: {str(e)}", "WARNING")
            return None
    
    def start_monitoring(self) -> bool:
        """Start real-time ransomware monitoring"""
        if self.is_running:
            self._log_message("Ransomware monitor already running", "WARNING")
            return False
        
        self._log_message("Starting Ransomware Monitoring System...", "INFO")
        self._log_message(f"Monitoring {len(self.monitored_dirs)} directories", "INFO")
        self._log_message(f"Backup enabled: {self.backup_enabled}", "INFO")
        
        self.is_running = True
        self._stop_event.clear()
        self.stats['start_time'] = datetime.now()
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        if WATCHDOG_AVAILABLE:
            self._start_watchdog()
        else:
            self._log_message("Watchdog not available - using polling mode", "WARNING")
        
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        
        self._log_message("Ransomware monitoring active", "SUCCESS")
        return True

    def _start_watchdog(self):
        """Start watchdog file system observer with backup support"""
        if not WATCHDOG_AVAILABLE:
            self._log_message("⚠️ Watchdog not available - using polling mode", "WARNING")
            return
        
        try:
            class RansomwareFileHandler(FileSystemEventHandler):
                def __init__(self, monitor):
                    self.monitor = monitor
                    self.event_count = 0
                
                def on_created(self, event):
                    if not event.is_directory:
                        self.event_count += 1
                        self.monitor._handle_file_event('created', event.src_path)
                        self.monitor._log_message(f"📁 Created: {Path(event.src_path).name}", "EVENT")
                
                def on_modified(self, event):
                    if not event.is_directory:
                        self.event_count += 1
                        self.monitor._handle_file_event('modified', event.src_path)
                        self.monitor._log_message(f"📝 Modified: {Path(event.src_path).name}", "EVENT")
                
                def on_deleted(self, event):
                    if not event.is_directory:
                        file_path = Path(event.src_path)
                        self.event_count += 1
                        self.monitor._log_message(f"🗑️ Deleted: {file_path.name}", "EVENT")
                        
                        if self.monitor.backup_enabled:
                            backup_path = None
                            
                            # Try to backup if file still exists
                            if file_path.exists():
                                backup_path = self.monitor._backup_file(file_path, "deleted")
                            
                            # Try to recover from seen files
                            if not backup_path:
                                dir_key = str(file_path.parent)
                                if dir_key in self.monitor.seen_files:
                                    if file_path.name in self.monitor.seen_files[dir_key]:
                                        backup_path = self.monitor._backup_polled_file(file_path, file_path.name, file_path.parent)
                            
                            if backup_path:
                                self.monitor._log_message(f"💾 Backed up deleted file: {file_path.name}", "BACKUP")
                            else:
                                self.monitor._log_message(f"⚠️ Could not backup: {file_path.name}", "WARNING")
                        
                        self.monitor._handle_file_event('deleted', event.src_path)
                
                def on_moved(self, event):
                    if not event.is_directory:
                        self.event_count += 1
                        self.monitor._handle_file_event('moved', event.src_path, event.dest_path)
                        self.monitor._log_message(f"↔️ Moved: {Path(event.src_path).name} -> {Path(event.dest_path).name}", "EVENT")
            
            self.observer = PollingObserver()  # More reliable on Windows
            self._log_message("Using PollingObserver for file system monitoring", "INFO")
            
            success_count = 0
            handler = RansomwareFileHandler(self)
            
            for dir_path in self.monitored_dirs:
                try:
                    if dir_path.exists():
                        self.observer.schedule(handler, str(dir_path), recursive=True)
                        success_count += 1
                except Exception as e:
                    self._log_message(f"Could not monitor {dir_path}: {str(e)}", "DEBUG")
            
            if success_count > 0:
                self.observer.start()
                self._log_message(f"✅ File system watcher active ({success_count} directories)", "SUCCESS")
            else:
                self._log_message("⚠️ No directories could be monitored - using polling mode", "WARNING")
                self.observer = None
                
        except Exception as e:
            self._log_message(f"⚠️ Failed to start watchdog: {str(e)}", "WARNING")
            self.observer = None
            
    def _polling_loop(self):
        """Additional polling loop for detecting file changes with backup support"""
        self._log_message("Starting polling loop for extra reliability", "DEBUG")
        
        while not self._stop_event.is_set():
            try:
                for dir_path in self.monitored_dirs[:10]:
                    if not dir_path.exists():
                        continue
                    
                    try:
                        current_files = set()
                        file_info = {}
                        for item in dir_path.iterdir():
                            if item.is_file():
                                current_files.add(item.name)
                                try:
                                    file_info[item.name] = {
                                        'size': item.stat().st_size,
                                        'mtime': item.stat().st_mtime
                                    }
                                except:
                                    pass
                        
                        dir_key = str(dir_path)
                        
                        if dir_key in self.seen_files:
                            for file_name in current_files:
                                if file_name not in self.seen_files[dir_key]:
                                    file_path = dir_path / file_name
                                    self._handle_file_event('created', str(file_path))
                                    self._log_message(f"📁 [Poll] Created: {file_name}", "EVENT")
                            
                            for file_name in self.seen_files[dir_key]:
                                if file_name not in current_files:
                                    file_path = dir_path / file_name
                                    self._log_message(f"🗑️ [Poll] Deleted: {file_name}", "EVENT")
                                    
                                    if self.backup_enabled:
                                        backup_path = self._backup_polled_file(file_path, file_name, dir_path)
                                        if backup_path:
                                            self._log_message(f"💾 [Poll] Backed up deleted file: {file_name}", "BACKUP")
                                        else:
                                            self._log_message(f"⚠️ [Poll] Could not backup: {file_name}", "WARNING")
                                    
                                    self._handle_file_event('deleted', str(file_path))
                        
                        self.seen_files[dir_key] = current_files
                        
                    except Exception:
                        pass
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self._log_message(f"Polling error: {str(e)}", "DEBUG")
                time.sleep(5)

    def _backup_polled_file(self, file_path: Path, file_name: str, dir_path: Path) -> Optional[Path]:
        """Backup a file detected as deleted by polling"""
        if not self.backup_enabled:
            return None

        try:
            if file_path.exists():
                return self._backup_file(file_path, "deleted")

            # Try to recover from Recycle Bin on Windows
            if platform.system() == 'Windows':
                try:
                    recycle_path = Path(os.environ.get('SystemDrive', 'C:')) / '$Recycle.Bin'
                    if recycle_path.exists():
                        for item in recycle_path.rglob(f'*{file_name}*'):
                            if item.is_file() and item.stat().st_size > 0:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                                backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
                                backup_dir = self.recycle_dir / "recovered_from_recycle"
                                backup_dir.mkdir(parents=True, exist_ok=True)
                                backup_path = backup_dir / backup_name

                                shutil.copy2(item, backup_path)
                                self.backup_stats['files_backed_up'] += 1
                                self.backup_stats['backup_size_bytes'] += item.stat().st_size
                                self.backup_stats['recycle_bin_size'] += item.stat().st_size
                                self.backup_stats['total_backups'] += 1

                                self._log_message(f"💾 Recovered from Recycle Bin: {file_name}", "BACKUP")
                                return backup_path
                except Exception:
                    pass

            # Skip temporary files
            if file_path.suffix.lower() in ['.tmp', '.temp', '.log', '.cache']:
                self._log_message(f"⏭️ Skipping temp file: {file_name}", "DEBUG")
                return None

            # Create deletion record
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            backup_dir = self.recycle_dir / "deleted_file_records"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{file_path.stem}_{timestamp}_deleted.txt"

            with open(backup_path, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("DELETED FILE RECORD\n")
                f.write("=" * 60 + "\n")
                f.write(f"File Name: {file_name}\n")
                f.write(f"Original Path: {file_path}\n")
                f.write(f"Directory: {dir_path}\n")
                f.write(f"Date Deleted: {datetime.now()}\n")
                f.write(f"File Extension: {file_path.suffix}\n")
                f.write("-" * 60 + "\n")
                f.write("Note: The original file could not be recovered.\n")
                f.write("This is a record of the deleted file for forensic purposes.\n")
                f.write("=" * 60 + "\n")

            self.backup_stats['files_backed_up'] += 1
            self.backup_stats['total_backups'] += 1

            return backup_path

        except Exception as e:
            self._log_message(f"⚠️ Backup failed for {file_name}: {str(e)}", "WARNING")
            return None

    def _handle_file_event(self, event_type: str, path: str, dest_path: str = None):
        """Handle file system events with backup integration"""
        try:
            file_path = Path(path)
            
            size = 0
            if file_path.exists():
                try:
                    size = file_path.stat().st_size
                except:
                    pass
            
            event = FileEvent(
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                path=str(file_path),
                size=size,
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
                self.deleted_files.append(event)
            elif event_type == 'moved':
                self.stats['files_renamed'] += 1
            
        except Exception as e:
            self._log_message(f"File event error: {str(e)}", "DEBUG")

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
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent']):
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
                
                self._log_message(f"⚠️ Detected {len(suspicious)} suspicious processes", "WARNING")
                for proc in suspicious[:5]:
                    self._log_message(f"   ❗ {proc.name} (PID: {proc.pid})", "WARNING")
                
                if len(suspicious) >= self.SUSPICIOUS_PROCESS_THRESHOLD:
                    self.ransomware_detected = True
                    self.threat_level = ThreatLevel.CRITICAL
                    self._log_message("🚨 CRITICAL: Ransomware activity detected!", "ERROR")
                    
        except Exception:
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
            self._log_message(f"⚠️ High file creation: {created} files in {timeframe}s", "WARNING")
            if self.threat_level.value[0] != "CRITICAL":
                self.threat_level = ThreatLevel.HIGH
        
        if deleted > self.DELETE_RATE_THRESHOLD:
            self._log_message(f"⚠️ High file deletion: {deleted} files in {timeframe}s", "WARNING")
            if self.threat_level.value[0] != "CRITICAL":
                self.threat_level = ThreatLevel.HIGH

    def _check_for_ransomware_patterns(self, event: FileEvent):
        """Check for ransomware patterns in file events"""
        file_path = Path(event.path)
        file_name = file_path.name.lower()
        
        if file_path.suffix.lower() in self.suspicious_extensions:
            event.is_suspicious = True
            self.suspicious_events.append(event)
            self._log_message(f"🚨 Suspicious extension: {file_path.name}", "ERROR")
            self.ransomware_detected = True
            self.threat_level = ThreatLevel.CRITICAL
            if self.backup_enabled and file_path.exists():
                self._quarantine_file(file_path)
        
        if file_name in self.suspicious_names:
            event.is_suspicious = True
            self.suspicious_events.append(event)
            self._log_message(f"🚨 Suspicious file: {file_path.name}", "WARNING")
            self.ransomware_detected = True
            if self.threat_level.value[0] != "CRITICAL":
                self.threat_level = ThreatLevel.HIGH
        
        if any(keyword in file_name for keyword in ['decrypt', 'ransom', 'readme', 'howtodecrypt']):
            if any(ext in file_name for ext in ['.txt', '.html', '.hta', '.lnk']):
                event.is_suspicious = True
                self.suspicious_events.append(event)
                self._log_message(f"📝 Ransom note: {file_path.name}", "ERROR")

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

    def stop_monitoring(self) -> bool:
        """Stop ransomware monitoring"""
        if not self.is_running:
            self._log_message("Monitor not running", "WARNING")
            return False
        
        self._stop_event.set()
        self.is_running = False
        
        if self.observer is not None:
            try:
                self.observer.stop()
                self.observer.join(timeout=2)
            except Exception as e:
                self._log_message(f"Error stopping observer: {str(e)}", "WARNING")
        
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            try:
                self.monitor_thread.join(timeout=2)
            except Exception as e:
                self._log_message(f"Error stopping monitor thread: {str(e)}", "WARNING")
        
        if self.polling_thread is not None and self.polling_thread.is_alive():
            try:
                self.polling_thread.join(timeout=2)
            except Exception:
                pass
        
        self._log_message("Ransomware monitoring stopped", "INFO")
        return True

    def get_status(self) -> dict:
        """Get current monitoring status with backup info"""
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
            'monitored_dirs': len(self.monitored_dirs),
            'total_alerts': self.stats['alerts_triggered'],
            'backup': {
                'enabled': self.backup_enabled,
                'files_backed_up': self.backup_stats['files_backed_up'],
                'files_restored': self.backup_stats['files_restored'],
                'files_quarantined': self.backup_stats['files_quarantined'],
                'backup_size_mb': round(self.backup_stats['backup_size_bytes'] / (1024 * 1024), 2),
                'recycle_bin_size_mb': round(self.backup_stats['recycle_bin_size'] / (1024 * 1024), 2),
                'total_backups': self.backup_stats['total_backups'],
                'backup_dir': str(self.backup_root)
            }
        }

    def get_events(self, limit: int = 100) -> List[FileEvent]:
        """Get recent file events"""
        return list(self.file_activity_log)[-limit:]

    def get_suspicious_events(self, limit: int = 50) -> List[FileEvent]:
        """Get suspicious events"""
        return self.suspicious_events[-limit:]

    def scan_for_ransomware(self, path: str = None) -> List[dict]:
        """Manual scan for ransomware indicators"""
        self._log_message("🔍 Starting manual ransomware scan...", "INFO")
        self.stats['total_scans'] += 1
        
        if path is None:
            scan_paths = self.monitored_dirs[:10]
        else:
            scan_paths = [Path(path)]
        
        found = []
        
        for scan_path in scan_paths:
            if not scan_path.exists():
                continue
            
            self._log_message(f"📂 Scanning: {scan_path}", "INFO")
            
            try:
                for root, dirs, files in os.walk(str(scan_path)):
                    if any(skip in root for skip in ['Windows', 'System32', '$Recycle', 'cache']):
                        continue
                    
                    for file in files:
                        file_path = Path(root) / file
                        
                        if file_path.suffix.lower() in self.suspicious_extensions:
                            found.append({
                                'path': str(file_path),
                                'type': 'suspicious_extension',
                                'extension': file_path.suffix
                            })
                            if self.backup_enabled and file_path.exists():
                                self._quarantine_file(file_path)
                        
                        if any(keyword in file.lower() for keyword in ['decrypt', 'ransom', 'readme', 'howtodecrypt']):
                            if file_path.suffix.lower() in ['.txt', '.html', '.hta', '.lnk']:
                                found.append({
                                    'path': str(file_path),
                                    'type': 'ransom_note',
                                    'name': file
                                })
                    
                    if len(found) > 50:
                        break
                    
            except Exception:
                continue
        
        self.stats['last_scan'] = datetime.now()
        
        if found:
            self.ransomware_detected = True
            self.threat_level = ThreatLevel.CRITICAL
            self._log_message(f"🚨 Found {len(found)} ransomware indicators!", "ERROR")
            print(f"\n{Fore.RED}🚨 RANSOMWARE INDICATORS FOUND: {len(found)}{Style.RESET_ALL}")
            for item in found[:10]:
                print(f"  {Fore.RED}[!] {item['type']}: {Path(item['path']).name}{Style.RESET_ALL}")
            if len(found) > 10:
                print(f"  {Fore.YELLOW}... and {len(found) - 10} more{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}✅ No ransomware indicators found{Style.RESET_ALL}")
            self.ransomware_detected = False
        
        return found

    def restore_file(self, backup_name: str = None) -> bool:
        """Restore files from backup"""
        if not self.backup_enabled:
            self._log_message("Backup is disabled", "WARNING")
            return False
        
        if backup_name:
            backup_path = self.recycle_dir / backup_name
            if not backup_path.exists():
                backup_path = self.backup_dir / backup_name
            if backup_path.exists():
                return self._restore_from_backup(backup_path)
            else:
                self._log_message(f"Backup file not found: {backup_name}", "WARNING")
                return False
        else:
            restored = 0
            for backup_path in self.recycle_dir.rglob("*"):
                if backup_path.is_file():
                    if self._restore_from_backup(backup_path):
                        restored += 1
            self._log_message(f"✅ Restored {restored} files from recycle bin", "SUCCESS")
            return restored > 0

    def clear_backups(self, confirm: bool = True) -> bool:
        """Clear all backups (with confirmation)"""
        if confirm:
            print(f"{Fore.RED}⚠️ WARNING: This will permanently delete all backups!{Style.RESET_ALL}")
            response = input(f"{Fore.YELLOW}Are you sure? (yes/no): {Style.RESET_ALL}")
            if response.lower() != 'yes':
                return False
        
        try:
            for item in self.recycle_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception:
                    pass
            
            for item in self.backup_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception:
                    pass
            
            for item in self.quarantine_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception:
                    pass
            
            self.backup_stats = {
                'files_backed_up': 0,
                'files_restored': 0,
                'files_quarantined': 0,
                'backup_size_bytes': 0,
                'recycle_bin_size': 0,
                'last_backup': None,
                'total_backups': 0
            }
            
            self._log_message("🧹 All backups cleared", "INFO")
            return True
            
        except Exception as e:
            self._log_message(f"Failed to clear backups: {str(e)}", "ERROR")
            return False

    def display_dashboard(self, refresh_rate: float = 0.5):
        """Launch the ransomware monitoring dashboard with left/right layout."""
        if self.use_rich and self.console:
            try:
                self._display_live_dashboard(refresh_rate)
            except KeyboardInterrupt:
                self.console.print("\n[bold yellow]Dashboard closed.[/bold yellow]")
            except Exception as e:
                self._log_message(f"Dashboard error: {e}", "ERROR")
                self._display_simple_dashboard()
        else:
            self._display_simple_dashboard()

    def _display_simple_dashboard(self):
        """Display simple dashboard without Rich"""
        status = self.get_status()
        
        print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}🛡️  RANSOMWARE DETECTION DASHBOARD{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        
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
        
        print(f"\n{Fore.CYAN}Backup Statistics:{Style.RESET_ALL}")
        backup = status['backup']
        print(f"  Backup Enabled: {'✅' if backup['enabled'] else '❌'}")
        print(f"  Files Backed Up: {backup['files_backed_up']}")
        print(f"  Files Quarantined: {backup['files_quarantined']}")
        print(f"  Files Restored: {backup['files_restored']}")
        print(f"  Backup Size: {backup['backup_size_mb']} MB")
        print(f"  Recycle Bin Size: {backup['recycle_bin_size_mb']} MB")
        print(f"  Backup Directory: {backup['backup_dir']}")
        
        if status['suspicious_events'] > 0:
            print(f"\n{Fore.RED}Recent Suspicious Events:{Style.RESET_ALL}")
            for event in self.get_suspicious_events(5):
                print(f"  {Fore.YELLOW}• {event.event_type}: {Path(event.path).name}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
    
    def _display_live_dashboard(self, refresh_rate: float = 0.5):
        """Enterprise-grade live dashboard with bold continuous lines."""
        if not self.use_rich or not self.console:
            self._display_simple_dashboard()
            return

        from rich.align import Align
        from rich.live import Live
        from rich.table import Table
        from rich.text import Text
        from rich.panel import Panel
        from rich.layout import Layout
        from rich import box
        from datetime import datetime

        # Use double border with bold continuous lines
        BOLD_BOX = box.DOUBLE_EDGE

        def build_header():
            header_text = Text("🛡️  DSTERMINAL RANSOMWARE MONITOR", style="bold cyan")
            header_text.append("  |  ", style="bright_blue")
            header_text.append("REAL-TIME THREAT INTELLIGENCE", style="bold white")
            
            header = Panel(
                Align.center(header_text),
                border_style="bright_blue",
                box=BOLD_BOX,
                padding=(1, 2),
            )
            return header

        def build_left_panel(status):
            status_color = "red" if status.get("ransomware_detected", False) else "green"
            status_text = "🚨 ACTIVE THREAT" if status.get("ransomware_detected", False) else "✅ SYSTEM CLEAN"
            
            threat_level = status.get("threat_level", "NORMAL")
            threat_color = status.get("threat_color", "green")
            
            threat_indicator = Text()
            if threat_level == "CRITICAL":
                threat_indicator.append("████████████████████", style="bold red")
                threat_indicator.append(" CRITICAL", style="bold red")
            elif threat_level == "HIGH":
                threat_indicator.append("████████████████", style="bold yellow")
                threat_indicator.append(" HIGH", style="bold yellow")
            elif threat_level == "MEDIUM":
                threat_indicator.append("██████████", style="bold orange1")
                threat_indicator.append(" MEDIUM", style="bold orange1")
            else:
                threat_indicator.append("████", style="bold green")
                threat_indicator.append(" LOW", style="bold green")
            
            table = Table(show_header=False, box=BOLD_BOX, expand=True)
            table.add_column("Metric", style="cyan", width=18)
            table.add_column("Value", style="white")
            
            table.add_row("Status", f"[{status_color}]{status_text}[/{status_color}]")
            table.add_row("Threat Level", f"[{threat_color}]{threat_level}[/{threat_color}]")
            table.add_row("Threat Indicator", threat_indicator)
            table.add_row("Uptime", status.get("uptime", "N/A"))
            table.add_row("Running", "✅" if status.get("running", False) else "❌")
            table.add_row("Monitored Dirs", str(status.get("monitored_dirs", 0)))
            table.add_row("Total Alerts", str(status.get("total_alerts", 0)))
            
            system_table = Table(show_header=False, box=BOLD_BOX, expand=True)
            system_table.add_column("Metric", style="cyan", width=18)
            system_table.add_column("Value", style="white")
            
            system_table.add_row("Platform", platform.system())
            system_table.add_row("Hostname", socket.gethostname())
            system_table.add_row("Session", self.session_id)
            
            left_layout = Layout()
            left_layout.split(
                Layout(Panel(table, title="[bold cyan]📊 System Status[/bold cyan]", border_style="cyan", box=BOLD_BOX), size=12),
                Layout(Panel(system_table, title="[bold blue]💻 System Info[/bold blue]", border_style="blue", box=BOLD_BOX), size=6),
            )
            
            return left_layout

        def build_right_panel(status):
            stats = status.get("stats", {})
            backup = status.get("backup", {})
            
            stats_table = Table(show_header=False, box=BOLD_BOX, expand=True)
            stats_table.add_column("Metric", style="cyan", width=18)
            stats_table.add_column("Value", style="white", justify="right")
            
            stats_table.add_row("📁 Files Created", str(stats.get("files_created", 0)))
            stats_table.add_row("📝 Files Modified", str(stats.get("files_modified", 0)))
            stats_table.add_row("🗑️ Files Deleted", str(stats.get("files_deleted", 0)))
            stats_table.add_row("🔄 Files Renamed", str(stats.get("files_renamed", 0)))
            stats_table.add_row("", "")
            stats_table.add_row("🔍 Suspicious Processes", str(status.get("suspicious_processes", 0)))
            stats_table.add_row("⚠️ Suspicious Events", str(status.get("suspicious_events", 0)))
            stats_table.add_row("🔔 Alerts Triggered", str(stats.get("alerts_triggered", 0)))
            stats_table.add_row("📊 Scans Performed", str(stats.get("total_scans", 0)))
            
            backup_table = Table(show_header=False, box=BOLD_BOX, expand=True)
            backup_table.add_column("Metric", style="cyan", width=18)
            backup_table.add_column("Value", style="white", justify="right")
            
            backup_table.add_row("💾 Backup Enabled", "✅" if backup.get("enabled", False) else "❌")
            backup_table.add_row("Files Backed Up", str(backup.get("files_backed_up", 0)))
            backup_table.add_row("🔒 Quarantined", str(backup.get("files_quarantined", 0)))
            backup_table.add_row("🔄 Restored", str(backup.get("files_restored", 0)))
            backup_table.add_row("📦 Backup Size", f"{backup.get('backup_size_mb', 0.0):.2f} MB")
            backup_table.add_row("♻️ Recycle Bin", f"{backup.get('recycle_bin_size_mb', 0.0):.2f} MB")
            backup_table.add_row("📂 Total Backups", str(backup.get("total_backups", 0)))
            
            right_layout = Layout()
            right_layout.split(
                Layout(Panel(stats_table, title="[bold yellow]📈 Activity Statistics[/bold yellow]", border_style="yellow", box=BOLD_BOX), size=12),
                Layout(Panel(backup_table, title="[bold magenta]💾 Backup & Recovery[/bold magenta]", border_style="magenta", box=BOLD_BOX), size=10),
            )
            
            return right_layout

        def build_events_panel(limit: int = 8):
            events = self.get_events(limit)
            
            table = Table(
                box=BOLD_BOX,
                expand=True,
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Time", style="dim", width=10)
            table.add_column("Type", style="yellow", width=12)
            table.add_column("File", style="white", no_wrap=False)
            
            if not events:
                table.add_row("—", "—", "[dim]No recent events[/dim]")
            else:
                for event in events[-limit:]:
                    if hasattr(event, 'event_type'):
                        event_type = event.event_type
                        path = Path(event.path).name if hasattr(event, 'path') else 'unknown'
                        try:
                            timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")
                        except:
                            timestamp = event.timestamp[:8] if len(event.timestamp) >= 8 else event.timestamp
                    else:
                        event_type = event.get('event_type', 'unknown')
                        path = Path(event.get('path', '')).name
                        timestamp = event.get('timestamp', '')[:8]
                    
                    if event_type == 'created':
                        type_display = "📁 CREATE"
                        color = "green"
                    elif event_type == 'deleted':
                        type_display = "🗑️ DELETE"
                        color = "red"
                    elif event_type == 'modified':
                        type_display = "📝 MODIFY"
                        color = "yellow"
                    elif event_type == 'moved':
                        type_display = "🔄 MOVE"
                        color = "blue"
                    else:
                        type_display = "❓ OTHER"
                        color = "white"
                    
                    if len(path) > 40:
                        path = path[:37] + "..."
                    
                    table.add_row(
                        timestamp,
                        f"[{color}]{type_display}[/{color}]",
                        path
                    )
            
            panel = Panel(
                table,
                title="[bold cyan]🔄 Recent File Events[/bold cyan]",
                border_style="cyan",
                box=BOLD_BOX,
                padding=(1, 2),
            )
            return panel

        def build_footer():
            footer_text = Text()
            footer_text.append("DSTerminal v4.0.0.113", style="dim")
            footer_text.append("  |  ", style="bright_blue")
            footer_text.append(f"Session: {self.session_id}", style="dim")
            footer_text.append("  |  ", style="bright_blue")
            footer_text.append("Press Ctrl+C to exit", style="yellow")
            footer_text.append("  |  ", style="bright_blue")
            footer_text.append(f"Last Backup: {self.backup_stats['last_backup'].strftime('%H:%M:%S') if self.backup_stats['last_backup'] else 'Never'}", style="dim")
            
            footer = Panel(
                Align.center(footer_text),
                border_style="bright_blue",
                box=BOLD_BOX,
                padding=(0, 2),
            )
            return footer

        def build_layout():
            status = self.get_status()
            
            body = Layout()
            body.split_row(
                Layout(build_left_panel(status), ratio=1),
                Layout(build_right_panel(status), ratio=1),
            )
            
            layout = Layout()
            layout.split(
                Layout(build_header(), size=5),
                Layout(body),
                Layout(build_events_panel(), size=10),
                Layout(build_footer(), size=3),
            )
            
            return layout

        try:
            with Live(
                console=self.console,
                refresh_per_second=1 / refresh_rate,
                screen=True,
                transient=False,
                auto_refresh=True,
            ) as live:
                while not self._stop_event.is_set():
                    live.update(build_layout())
                    time.sleep(refresh_rate)
                    
        except KeyboardInterrupt:
            self.console.print("\n[bold yellow]Dashboard closed.[/bold yellow]")
        except Exception as e:
            self._log_message(f"Dashboard error: {e}", "ERROR")
            self._display_simple_dashboard()

    def interactive_menu(self):
        """Interactive menu for ransomware monitoring with backup options"""
        while True:
            os.system('cls' if platform.system() == 'Windows' else 'clear')
            
            status = self.get_status()
            backup = status['backup']
            
            print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}🛡️  RANSOMWARE DETECTION & MONITORING SYSTEM{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
            
            status_color = Fore.RED if status['ransomware_detected'] else Fore.GREEN
            status_text = "🚨 ACTIVE" if status['ransomware_detected'] else "✅ CLEAN"
            print(f"{Fore.YELLOW}Status:{Style.RESET_ALL} {status_color}{status_text}{Style.RESET_ALL} | "
                f"{Fore.YELLOW}Level:{Style.RESET_ALL} {status['threat_color']}{status['threat_level']}{Style.RESET_ALL} | "
                f"{Fore.YELLOW}Uptime:{Style.RESET_ALL} {status['uptime']}")
            print(f"{Fore.CYAN}{'-' * 80}{Style.RESET_ALL}")
            
            print(f"""
    {Fore.GREEN}┌──────────────────────────────────────────────────────────────────────────────────┐{Style.RESET_ALL}
    {Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}1.{Style.RESET_ALL} Start Monitoring      {Fore.CYAN}2.{Style.RESET_ALL} Stop Monitoring       {Fore.CYAN}3.{Style.RESET_ALL} Scan Now
    {Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}4.{Style.RESET_ALL} View Events          {Fore.CYAN}5.{Style.RESET_ALL} View Suspicious      {Fore.CYAN}6.{Style.RESET_ALL} Dashboard
    {Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}7.{Style.RESET_ALL} Export JSON          {Fore.CYAN}8.{Style.RESET_ALL} Export PDF           {Fore.CYAN}9.{Style.RESET_ALL} Export HTML
    {Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}10.{Style.RESET_ALL}Restore Files        {Fore.CYAN}11.{Style.RESET_ALL}Clear Backups         {Fore.CYAN}12.{Style.RESET_ALL}Exit
    {Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}13.{Style.RESET_ALL}Create Test File
    {Fore.GREEN}└──────────────────────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
    """)
            
            print(f"{Fore.CYAN}Quick Stats:{Style.RESET_ALL}")
            print(f"  Files Changed: {status['stats']['files_created'] + status['stats']['files_modified']} | "
                f"Deleted: {status['stats']['files_deleted']} | "
                f"Alerts: {status['stats']['alerts_triggered']}")
            print(f"  💾 Backed Up: {backup['files_backed_up']} | "
                f"🔒 Quarantined: {backup['files_quarantined']} | "
                f"📦 Size: {backup['backup_size_mb']} MB")
            
            choice = input(f"\n{Fore.YELLOW}Select option (1-13): {Style.RESET_ALL}").strip()
            
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
                self._ransomware_events()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '5':
                self._ransomware_suspicious()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '6':
                self.display_dashboard()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '7':
                self.export_report('json')
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '8':
                self.export_report('pdf')
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '9':
                self.export_report('html')
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '10':
                self.restore_file()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '11':
                self.clear_backups()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '12':
                if self.is_running:
                    self.stop_monitoring()
                print(f"{Fore.GREEN}👋 Exiting Ransomware Monitor{Style.RESET_ALL}")
                break
            elif choice == '13':
                self.create_test_file()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Invalid option{Style.RESET_ALL}")
                time.sleep(1)
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def _ransomware_events(self, limit=20):
        """Show recent file events"""
        events = self.get_events(limit)
        
        print(f"\n{Fore.CYAN}Recent Events:{Style.RESET_ALL}")
        if not events:
            print(f"  {Fore.YELLOW}No events recorded yet{Style.RESET_ALL}")
        else:
            for event in events[-10:]:
                event_color = Fore.GREEN if event.event_type == 'created' else Fore.RED if event.event_type == 'deleted' else Fore.YELLOW
                print(f"  {event_color}{event.event_type}: {Path(event.path).name}{Style.RESET_ALL}")
        
        if len(events) > 10:
            print(f"\n{Fore.CYAN}Showing 10 of {len(events)} events. Use 'events <n>' to see more.{Style.RESET_ALL}")

    def _ransomware_suspicious(self, limit=10):
        """Show suspicious events"""
        events = self.get_suspicious_events(limit)
        
        print(f"\n{Fore.RED}Suspicious Events:{Style.RESET_ALL}")
        if not events:
            print(f"  {Fore.GREEN}No suspicious events{Style.RESET_ALL}")
        else:
            for event in events:
                print(f"  [!] {event.event_type}: {Path(event.path).name}")

    def export_report(self, format_type: str = "json", filename: str = None):
        """Export ransomware monitoring report in various formats"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ransomware_report_{timestamp}.{format_type}"
        
        export_dir = Path.home() / "DSTerminal" / "reports"
        export_dir.mkdir(parents=True, exist_ok=True)
        filepath = export_dir / filename
        
        if format_type == "json":
            return self._export_json(filepath)
        elif format_type == "pdf" and REPORTLAB_AVAILABLE:
            return self._export_pdf(filepath)
        elif format_type == "pdf" and not REPORTLAB_AVAILABLE:
            print(f"{Fore.RED}[!] PDF export requires reportlab. Install with: pip install reportlab{Style.RESET_ALL}")
            return None
        elif format_type == "html":
            return self._export_html(filepath)
        else:
            print(f"{Fore.RED}[!] Unsupported format: {format_type}{Style.RESET_ALL}")
            return None

    def _export_json(self, filepath: Path) -> Optional[str]:
        """Export to JSON format"""
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
            'backup': status['backup'],
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
            
            self._log_message(f"JSON report exported: {filepath}", "SUCCESS")
            print(f"\n{Fore.GREEN}✅ JSON report exported successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📂 Location: {filepath}{Style.RESET_ALL}")
            return str(filepath)
        except Exception as e:
            self._log_message(f"Failed to export JSON: {str(e)}", "ERROR")
            return None

    def _export_pdf(self, filepath: Path) -> Optional[str]:
        """Export to PDF format"""
        if not REPORTLAB_AVAILABLE:
            print(f"{Fore.RED}[!] PDF export requires reportlab. Install with: pip install reportlab{Style.RESET_ALL}")
            return None
        
        try:
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1a237e'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold'
            )
            
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#283593'),
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=4,
                fontName='Helvetica'
            )
            
            story.append(Paragraph("Ransomware Detection Report", title_style))
            story.append(Spacer(1, 10))
            
            status = self.get_status()
            header_lines = [
                (f"<b>Report ID:</b> {self.session_id}", normal_style),
                (f"<b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style),
                (f"<b>System:</b> {platform.system()} {platform.release()}", normal_style),
                (f"<b>Hostname:</b> {socket.gethostname()}", normal_style),
                (f"<b>Status:</b> {'🔴 THREAT DETECTED' if self.ransomware_detected else '✅ SYSTEM CLEAN'}", normal_style),
                (f"<b>Threat Level:</b> {status['threat_level']}", normal_style),
                (f"<b>Uptime:</b> {status['uptime']}", normal_style),
                (f"<b>Monitored Directories:</b> {status['monitored_dirs']}", normal_style)
            ]
            
            header_data = []
            for text, style in header_lines:
                header_data.append([Paragraph(text, style)])
            
            header_table = Table(header_data, colWidths=[5.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a237e')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 20))
            
            # Statistics
            story.append(Paragraph("<b>Statistics</b>", header_style))
            stats_data = [
                ['Metric', 'Value'],
                ['Files Created', str(status['stats']['files_created'])],
                ['Files Modified', str(status['stats']['files_modified'])],
                ['Files Deleted', str(status['stats']['files_deleted'])],
                ['Files Renamed', str(status['stats']['files_renamed'])],
                ['Suspicious Processes', str(status['suspicious_processes'])],
                ['Suspicious Events', str(status['suspicious_events'])],
                ['Alerts Triggered', str(status['stats']['alerts_triggered'])],
                ['Total Scans', str(status['stats']['total_scans'])]
            ]
            
            stats_table = Table(stats_data, colWidths=[2.5*inch, 3*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # Backup stats
            story.append(Paragraph("<b>Backup Statistics</b>", header_style))
            backup = status['backup']
            backup_data = [
                ['Metric', 'Value'],
                ['Backup Enabled', 'Yes' if backup['enabled'] else 'No'],
                ['Files Backed Up', str(backup['files_backed_up'])],
                ['Files Quarantined', str(backup['files_quarantined'])],
                ['Files Restored', str(backup['files_restored'])],
                ['Backup Size', f"{backup['backup_size_mb']} MB"],
                ['Recycle Bin Size', f"{backup['recycle_bin_size_mb']} MB"],
            ]
            
            backup_table = Table(backup_data, colWidths=[2.5*inch, 3*inch])
            backup_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(backup_table)
            
            # Suspicious events
            if self.suspicious_events:
                story.append(Spacer(1, 20))
                story.append(Paragraph("<b>Suspicious Events</b>", header_style))
                events_data = [['Time', 'Type', 'File']]
                for event in self.suspicious_events[-10:]:
                    events_data.append([
                        datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S"),
                        event.event_type,
                        Path(event.path).name
                    ])
                
                events_table = Table(events_data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch])
                events_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d32f2f')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(events_table)
            
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceBefore=20
            )
            
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Generated by DSTerminal Ransomware Monitor v4.0.0.113", footer_style))
            story.append(Paragraph(f"Report ID: {self.session_id}", footer_style))
            
            doc.build(story)
            
            print(f"\n{Fore.GREEN}✅ PDF report exported successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📂 Location: {filepath}{Style.RESET_ALL}")
            return str(filepath)
            
        except Exception as e:
            self._log_message(f"Failed to export PDF: {str(e)}", "ERROR")
            print(f"{Fore.RED}[!] PDF export failed: {str(e)}{Style.RESET_ALL}")
            return None

    def _export_html(self, filepath: Path) -> Optional[str]:
        """Export to HTML format"""
        status = self.get_status()
        backup = status['backup']
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ransomware Report - {self.session_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a237e; border-bottom: 3px solid #d32f2f; padding-bottom: 10px; }}
        .header {{ background: linear-gradient(135deg, #1a237e, #283593); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        .table th {{ background: #1a237e; color: white; padding: 10px; text-align: left; }}
        .table td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        .table tr:hover {{ background: #f5f5f5; }}
        .danger {{ background: #ffebee; }}
        .warning {{ background: #fff3e0; }}
        .safe {{ background: #e8f5e9; }}
        .status-critical {{ color: #d32f2f; font-weight: bold; }}
        .status-normal {{ color: #4CAF50; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Ransomware Detection Report</h1>
        <div class="header">
            <p><strong>Report ID:</strong> {self.session_id}</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>System:</strong> {platform.system()} {platform.release()}</p>
            <p><strong>Hostname:</strong> {socket.gethostname()}</p>
            <p><strong>Status:</strong> <span class="{'status-critical' if self.ransomware_detected else 'status-normal'}">{'🔴 THREAT DETECTED' if self.ransomware_detected else '✅ SYSTEM CLEAN'}</span></p>
            <p><strong>Threat Level:</strong> {status['threat_level']}</p>
            <p><strong>Uptime:</strong> {status['uptime']}</p>
        </div>
        
        <h2>Statistics</h2>
        <table class="table">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Files Created</td><td>{status['stats']['files_created']}</td></tr>
            <tr><td>Files Modified</td><td>{status['stats']['files_modified']}</td></tr>
            <tr><td>Files Deleted</td><td>{status['stats']['files_deleted']}</td></tr>
            <tr><td>Files Renamed</td><td>{status['stats']['files_renamed']}</td></tr>
            <tr><td>Suspicious Processes</td><td>{status['suspicious_processes']}</td></tr>
            <tr><td>Suspicious Events</td><td>{status['suspicious_events']}</td></tr>
            <tr><td>Alerts Triggered</td><td>{status['stats']['alerts_triggered']}</td></tr>
            <tr><td>Total Scans</td><td>{status['stats']['total_scans']}</td></tr>
            <tr><td>Monitored Directories</td><td>{status['monitored_dirs']}</td></tr>
        </table>
        
        <h2>Backup Statistics</h2>
        <table class="table">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Backup Enabled</td><td>{'Yes' if backup['enabled'] else 'No'}</td></tr>
            <tr><td>Files Backed Up</td><td>{backup['files_backed_up']}</td></tr>
            <tr><td>Files Quarantined</td><td>{backup['files_quarantined']}</td></tr>
            <tr><td>Files Restored</td><td>{backup['files_restored']}</td></tr>
            <tr><td>Backup Size</td><td>{backup['backup_size_mb']} MB</td></tr>
            <tr><td>Recycle Bin Size</td><td>{backup['recycle_bin_size_mb']} MB</td></tr>
        </table>
        
        <h2>Suspicious Events</h2>
        <table class="table">
            <tr><th>Time</th><th>Type</th><th>File</th></tr>
            {''.join([f'<tr class="danger"><td>{datetime.fromisoformat(e.timestamp).strftime("%H:%M:%S")}</td><td>{e.event_type}</td><td>{Path(e.path).name}</td></tr>' for e in self.suspicious_events[-10:]])}
        </table>
        
        <h2>Suspicious Processes</h2>
        <table class="table">
            <tr><th>PID</th><th>Name</th><th>CPU</th></tr>
            {''.join([f'<tr class="warning"><td>{p.pid}</td><td>{p.name}</td><td>{p.cpu:.1f}%</td></tr>' for p in self.detected_processes[-5:]])}
        </table>
        
        <div class="footer">
            <p>Generated by DSTerminal Ransomware Monitor v4.0.0.113</p>
            <p>Report ID: {self.session_id}</p>
        </div>
    </div>
</body>
</html>"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self._log_message(f"HTML report exported: {filepath}", "SUCCESS")
            print(f"\n{Fore.GREEN}✅ HTML report exported successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📂 Location: {filepath}{Style.RESET_ALL}")
            return str(filepath)
        except Exception as e:
            self._log_message(f"Failed to export HTML: {str(e)}", "ERROR")
            return None


# ============================================================================
# DSTerminal Integration Functions
# ============================================================================

def cmd_ransomware(dsterminal_instance, args):
    """Command handler for ransomware monitoring with backup support"""
    if not hasattr(dsterminal_instance, 'ransomware_monitor'):
        dsterminal_instance.ransomware_monitor = RansomwareMonitor(
            session_id=dsterminal_instance.session_id,
            log_callback=dsterminal_instance.log_message,
            backup_enabled=True
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
        print(f"\n{Fore.CYAN}Backup Status:{Style.RESET_ALL}")
        backup = status['backup']
        print(f"  Enabled: {backup['enabled']}")
        print(f"  Files Backed Up: {backup['files_backed_up']}")
        print(f"  Files Quarantined: {backup['files_quarantined']}")
        print(f"  Files Restored: {backup['files_restored']}")
        print(f"  Backup Size: {backup['backup_size_mb']} MB")
        print(f"  Recycle Bin Size: {backup['recycle_bin_size_mb']} MB")
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
        format_type = args[1] if len(args) > 1 else 'json'
        monitor.export_report(format_type)
    elif cmd == 'restore':
        filename = args[1] if len(args) > 1 else None
        if monitor.restore_file(filename):
            print(f"{Fore.GREEN}✅ Files restored successfully!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No files to restore or file not found.{Style.RESET_ALL}")
    elif cmd == 'clear-backups':
        monitor.clear_backups()
    elif cmd == 'interactive' or cmd == 'menu':
        monitor.interactive_menu()
    elif cmd in ['help', '?']:
        print(f"""
{Fore.CYAN}Ransomware Monitor Commands:{Style.RESET_ALL}
  start          - Start real-time monitoring
  stop           - Stop monitoring
  scan [path]    - Scan for ransomware indicators
  status         - Show monitoring status with backup info
  dashboard      - Display full dashboard
  events [n]     - Show recent events
  suspicious     - Show suspicious events
  export <format> - Export report (json/pdf/html)
  restore [file] - Restore files from backup
  clear-backups  - Clear all backups (with confirmation)
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
{Fore.CYAN}┌──────────────────────────────────────────────────────────────────────────────────────┐{Style.RESET_ALL}
{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}🛡️  RANSOMWARE DETECTION & MONITORING SYSTEM v4.0.0.113{Style.RESET_ALL}          {Fore.CYAN}│{Style.RESET_ALL}
{Fore.CYAN}│{Style.RESET_ALL}  {Fore.YELLOW}Developed by: Spark Wilson Spink | © 2024{Style.RESET_ALL}                              {Fore.CYAN}│{Style.RESET_ALL}
{Fore.CYAN}│{Style.RESET_ALL}  {Fore.CYAN}Platform: {platform.system()} {platform.release()}{Style.RESET_ALL}                               {Fore.CYAN}│{Style.RESET_ALL}
{Fore.CYAN}└──────────────────────────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
    """)
    
    monitor = RansomwareMonitor(use_rich=False, backup_enabled=True)
    
    if not WATCHDOG_AVAILABLE:
        print(f"{Fore.YELLOW}⚠️ Watchdog not available - installing...{Style.RESET_ALL}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'watchdog'], capture_output=True)
            print(f"{Fore.GREEN}✅ Watchdog installed. Please restart.{Style.RESET_ALL}")
        except Exception:
            print(f"{Fore.YELLOW}⚠️ Could not install watchdog. Using polling mode.{Style.RESET_ALL}")
    
    if not REPORTLAB_AVAILABLE:
        print(f"{Fore.YELLOW}⚠️ ReportLab not available - PDF export disabled{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Install with: pip install reportlab{Style.RESET_ALL}")
    
    monitor.interactive_menu()


if __name__ == "__main__":
    main()