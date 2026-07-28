# deletion_protection.py
"""
DSTerminal - Deletion Protection Module
<<<<<<< HEAD
Contains: BackupDatabase, EncryptionManager, DSTerminalMonitor, 
          RestoreManager, ServiceManager
=======
Import this into the main DSTerminal class.
Contains: BackupDatabase, EncryptionManager, DSTerminalMonitor, 
           RestoreManager, ServiceManager
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
"""

import os
import sys
import time
import shutil
import hashlib
import json
import threading
import sqlite3
import tempfile
import signal
import atexit
import fnmatch
import platform
import logging
import re
from datetime import datetime
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Any

<<<<<<< HEAD
# ============================================================
# 1. IMPORTS FIRST
# ============================================================

=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    print("Error: watchdog is required. Install with: pip install watchdog")
<<<<<<< HEAD
    WATCHDOG_AVAILABLE = False
=======
    sys.exit(1)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


<<<<<<< HEAD
# ============================================================
# 2. SIMPLE WORKSPACE CLASS
# ============================================================

class SimpleWorkspace:
    """Simple workspace for file operations"""
    def __init__(self, base_path):
        self.base_path = base_path
        self._create_dirs()
    
    def _create_dirs(self):
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'database'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'backups'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'temp'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'backups_protected'), exist_ok=True)
    
    def get_database_path(self):
        return os.path.join(self.base_path, 'database', 'dsterminal.db')
    
    def get_backup_path(self, category='other'):
        path = os.path.join(self.base_path, 'backups', category)
        os.makedirs(path, exist_ok=True)
        return path
    
    def get_log_path(self):
        return os.path.join(self.base_path, 'logs', 'dsterminal.log')
    
    def get_key_path(self):
        return os.path.join(self.base_path, 'database', 'key.key')
    
    def get_path(self, name):
        return os.path.join(self.base_path, name)
    
    def cleanup_temp_files(self, max_age_hours=24):
        temp_dir = os.path.join(self.base_path, 'temp')
        if os.path.exists(temp_dir):
            cutoff = time.time() - (max_age_hours * 3600)
            for f in os.listdir(temp_dir):
                fp = os.path.join(temp_dir, f)
                if os.path.isfile(fp) and os.path.getmtime(fp) < cutoff:
                    try:
                        os.remove(fp)
                    except:
                        pass


# ============================================================
# 3. PLATFORM DETECTION
# ============================================================
=======
# =========================
# 🌍 Cross-Platform Detection
# =========================
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

class PlatformDetector:
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == 'Windows'
        self.is_linux = self.system == 'Linux'
        self.is_macos = self.system == 'Darwin'

    def get_trash_paths(self) -> List[str]:
        home = os.path.expanduser('~')
        if self.is_linux:
            return [
                os.path.join(home, '.local/share/Trash/files'),
                os.path.join(home, '.local/share/Trash/info'),
                os.path.join(home, '.Trash'),
                '/tmp'
            ]
        elif self.is_macos:
            return [
                os.path.join(home, '.Trash'),
                '/tmp',
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads')
            ]
        elif self.is_windows:
            paths = [
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Documents'),
                os.environ.get('TEMP', 'C:\\Windows\\Temp'),
                os.environ.get('TMP', 'C:\\Windows\\Temp')
            ]
            onedrive = os.path.join(home, 'OneDrive')
            if os.path.exists(onedrive):
                paths.extend([
                    os.path.join(onedrive, 'Desktop'),
                    os.path.join(onedrive, 'Downloads'),
                    os.path.join(onedrive, 'Documents')
                ])
            return [p for p in paths if os.path.exists(p)]
        else:
            return ['/tmp']

    def get_desktop_path(self) -> str:
        home = os.path.expanduser('~')
        if self.is_windows:
            onedrive_desktop = os.path.join(home, 'OneDrive', 'Desktop')
            if os.path.exists(onedrive_desktop):
                return onedrive_desktop
            return os.path.join(home, 'Desktop')
        else:
            return os.path.join(home, 'Desktop')

    def get_downloads_path(self) -> str:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

    def normalize_path(self, path: str) -> str:
        return os.path.normpath(path)

    def is_trash_path(self, path: str) -> bool:
        path_normalized = self.normalize_path(path).lower()
        if self.is_linux or self.is_macos:
            trash_indicators = ['.local/share/trash', '.trash', '/tmp']
        elif self.is_windows:
            trash_indicators = ['$recycle.bin', '\\temp', '\\windows\\temp']
        else:
            trash_indicators = []
        for indicator in trash_indicators:
            if indicator in path_normalized:
                return True
        return False

    def get_system_info(self) -> Dict[str, str]:
        info = {
            'system': self.system,
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
<<<<<<< HEAD
            'hostname': platform.node(),
=======
            'hostname': platform.socket().gethostname() if hasattr(platform, 'socket') else '',
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            'user': os.getlogin() if hasattr(os, 'getlogin') else ''
        }
        if self.is_linux:
            try:
                import distro
                info['distro'] = f"{distro.name()} {distro.version()}"
            except:
                info['distro'] = 'Linux'
        elif self.is_macos:
            info['distro'] = f"macOS {platform.mac_ver()[0]}"
        elif self.is_windows:
            info['distro'] = f"Windows {platform.win32_ver()[0]}"
        return info


<<<<<<< HEAD
# ============================================================
# 4. DATABASE SYSTEM
# ============================================================
=======
# =========================
# 💾 Database System
# =========================
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

class BackupDatabase:
    def __init__(self, workspace):
        self.workspace = workspace
        self.db_path = workspace.get_database_path()
        self.conn = None
        self._init_database()

    def _init_database(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                category TEXT NOT NULL,
                encryption_status TEXT DEFAULT 'none',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                restore_count INTEGER DEFAULT 0,
                last_restored TIMESTAMP,
                metadata TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                status TEXT NOT NULL,
                files_processed INTEGER DEFAULT 0,
                bytes_processed INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds REAL,
                metadata TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deletion_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_hash TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                backed_up BOOLEAN DEFAULT FALSE,
                backup_id INTEGER,
                FOREIGN KEY (backup_id) REFERENCES backups (id)
            )
        ''')
        cursor.execute("PRAGMA table_info(backups)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'last_restored' not in columns:
            cursor.execute('ALTER TABLE backups ADD COLUMN last_restored TIMESTAMP')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backups_hash ON backups(file_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backups_created ON backups(created_at)')
        self.conn.commit()

    def add_backup(self, backup_data: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO backups
            (original_path, backup_path, filename, file_hash, file_size, category, encryption_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            backup_data['original_path'],
            backup_data['backup_path'],
            backup_data['filename'],
            backup_data['file_hash'],
            backup_data['file_size'],
            backup_data['category'],
            backup_data.get('encryption_status', 'none'),
            json.dumps(backup_data.get('metadata', {}))
        ))
        self.conn.commit()
        return cursor.lastrowid

    def add_deletion_event(self, file_path: str, file_hash: str, backup_id: int = None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO deletion_events
            (file_path, file_hash, backed_up, backup_id)
            VALUES (?, ?, ?, ?)
        ''', (file_path, file_hash, backup_id is not None, backup_id))
        self.conn.commit()

    def start_operation(self, operation_type: str, metadata: Dict[str, Any] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO operations (operation_type, status, metadata)
            VALUES (?, 'running', ?)
        ''', (operation_type, json.dumps(metadata or {})))
        self.conn.commit()
        return cursor.lastrowid

    def complete_operation(self, operation_id: int, status: str,
                          files_processed: int = 0, bytes_processed: int = 0):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE operations
            SET status = ?,
                files_processed = ?,
                bytes_processed = ?,
                completed_at = CURRENT_TIMESTAMP,
                duration_seconds = CAST((julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 86400 AS REAL)
            WHERE id = ?
        ''', (status, files_processed, bytes_processed, operation_id))
        self.conn.commit()

    def find_backup_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM backups WHERE file_hash = ?', (file_hash,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def version_exists(self, file_hash: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM backups WHERE file_hash = ?', (file_hash,))
        return cursor.fetchone() is not None

    def get_statistics(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as total_backups, COALESCE(SUM(file_size), 0) as total_size FROM backups')
        row = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) as today_deletions FROM deletion_events WHERE date(detected_at) = date('now')")
        del_row = cursor.fetchone()
        return {
            'total_backups': row['total_backups'] or 0,
            'total_size': row['total_size'] or 0,
            'deletions_today': del_row['today_deletions'] or 0
        }

    def close(self):
        if self.conn:
            self.conn.close()


<<<<<<< HEAD
# ============================================================
# 5. ENCRYPTION SYSTEM
# ============================================================
=======
# =========================
# 🔐 Encryption System
# =========================
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

class EncryptionManager:
    def __init__(self, workspace):
        self.workspace = workspace
        self.key_file = workspace.get_key_path()
        self.cipher = None
        if CRYPTO_AVAILABLE:
            self._load_or_create_key()

    def _load_or_create_key(self):
        if not CRYPTO_AVAILABLE:
            return
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        self.cipher = Fernet(key)

    def encrypt_file(self, filepath: str) -> str:
        if not CRYPTO_AVAILABLE or not self.cipher:
            return filepath
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted_data = self.cipher.encrypt(data)
        encrypted_path = filepath + '.encrypted'
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        return encrypted_path

    def decrypt_file(self, encrypted_path: str) -> str:
        if not CRYPTO_AVAILABLE or not self.cipher:
            return encrypted_path
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        decrypted_path = encrypted_path.replace('.encrypted', '')
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)
        return decrypted_path


<<<<<<< HEAD
# ============================================================
# 6. MONITOR HANDLER
# ============================================================

class DSTerminalMonitor(FileSystemEventHandler):
    def __init__(self, config: Dict[str, Any], workspace, interactive: bool = True, ui=None, verbose: bool = True):
=======
# =========================
# 📊 Advanced Monitor Handler
# =========================

class DSTerminalMonitor(FileSystemEventHandler):
    def __init__(self, config: Dict[str, Any], workspace, interactive: bool = True, ui=None):
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        self.config = config
        self.workspace = workspace
        self.interactive = interactive
        self.ui = ui
<<<<<<< HEAD
        self.verbose = verbose
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        self.db = BackupDatabase(workspace)
        self.encryption = EncryptionManager(workspace)
        self.platform_detector = PlatformDetector()
        self.stats = defaultdict(int)
        self.deletion_events = []
        self.honeypots = []
        self.protected_paths = set()
<<<<<<< HEAD
        self.observer = None
        self._setup_logging()
        self._setup_console_output()
        
        # Pause/Resume state
        self.paused = False
        self._was_paused = False
        self.pause_lock = threading.Lock()
        self._event_queue = []
        self._last_event_time = time.time()
        self.start_time = datetime.now()
        
        if interactive:
            for path in config.get('monitor_paths', []):
=======
        self._setup_logging()
        if interactive:
            for path in config['monitor_paths']:
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                if os.path.exists(path):
                    try:
                        honeypots = self._create_honeypots(path)
                        self.honeypots.extend(honeypots)
                    except Exception as e:
                        self.logger.debug(f"Skipping honeypots in {path}: {e}")
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

<<<<<<< HEAD
    def pause_monitoring(self):
        """Pause all monitoring activity"""
        with self.pause_lock:
            if self.paused:
                print("ℹ️ Monitoring is already paused.")
                return False
            self.paused = True
            self._log_event('INFO', 'SYSTEM', "⏸️ Monitoring PAUSED by user request")
            print("\n⏸️  Deletion protection monitoring PAUSED.")
            print("   No backups will be created until resumed.")
            print("   Use 'service resume' or 'service unpause' to continue.")
            return True

    def resume_monitoring(self):
        """Resume monitoring activity"""
        with self.pause_lock:
            if not self.paused:
                print("ℹ️ Monitoring is already active.")
                return False
            self.paused = False
            self._log_event('INFO', 'SYSTEM', "▶️ Monitoring RESUMED")
            print("\n▶️  Deletion protection monitoring RESUMED.")
            print("   Backups are now active again.")
            return True

    def is_paused(self) -> bool:
        """Check if monitoring is paused"""
        return self.paused

    def _should_process_file(self, filepath: str) -> bool:
        # CRITICAL FIX: Check if paused first
        if self.paused:
            return False
            
        workspace_path = os.path.normpath(
            self.workspace.base_path if hasattr(self.workspace, 'base_path') 
            else str(self.workspace)
        )
        filepath_norm = os.path.normpath(filepath)
        if filepath_norm.startswith(workspace_path):
            return False
        
        filename = os.path.basename(filepath)
        if '_restored_' in filename:
            return False
        
        # Skip system and temp files
        skip_patterns = ['*.db', '*.db-journal', '*.db-wal', '*.db-shm', '*.sqlite', '*.sqlite3']
        for pattern in skip_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        
        system_patterns = ['*.tmp', '*.temp', '*~', '.DS_Store', 'Thumbs.db', 'desktop.ini', '*.crdownload']
        for pattern in system_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        
        for pattern in self.config.get('exclude_patterns', []):
            if fnmatch.fnmatch(filepath, pattern):
                return False
        
        max_size = self.config.get('max_file_size', 100 * 1024 * 1024)
        try:
            if os.path.getsize(filepath) > max_size:
                return False
        except (OSError, IOError):
            return False
        
        return True

    def _is_trash_path(self, path: str) -> bool:
        return self.platform_detector.is_trash_path(path)

    def _calculate_hash(self, filepath: str) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _categorize(self, filename: str) -> str:
        """Categorize a file based on its extension."""
        ext = os.path.splitext(filename)[1].lower()
        
        # Image files
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif']:
            return 'images'
        
        # Document files
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages', '.md', '.tex']:
            return 'documents'
        
        # Spreadsheet files
        elif ext in ['.xls', '.xlsx', '.csv', '.ods', '.numbers']:
            return 'spreadsheets'
        
        # Code files
        elif ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.ts', '.jsx', '.tsx', 
                    '.rb', '.php', '.html', '.css', '.scss', '.sass', '.less', '.json', '.yaml', '.yml',
                    '.xml', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd']:
            return 'code'
        
        # Config files
        elif ext in ['.json', '.yaml', '.yml', '.ini', '.conf', '.env', '.toml', '.cfg', '.properties']:
            return 'config'
        
        # Archive files
        elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz', '.tgz', '.zst']:
            return 'archives'
        
        # Media files
        elif ext in ['.mp4', '.mp3', '.avi', '.mov', '.wav', '.flac', '.m4a', '.mpg', '.mpeg', '.webm',
                    '.mkv', '.wmv', '.flv', '.aac', '.ogg', '.wma']:
            return 'media'
        
        # Database files
        elif ext in ['.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.fdb']:
            return 'database'
        
        # Log files
        elif ext in ['.log', '.out', '.err']:
            return 'logs'
        
        # Default: other
        else:
            return 'other'

    def _protect_file(self, filepath: str) -> bool:
        try:
            os.chmod(filepath, 0o444)
            protected_dir = self.workspace.get_path('backups_protected')
            os.makedirs(protected_dir, exist_ok=True)
=======
    def _setup_logging(self):
        self.logger = logging.getLogger('DSTerminal')
        self.logger.setLevel(logging.INFO)
        fh = RotatingFileHandler(
            self.workspace.get_log_path(),
            maxBytes=10*1024*1024,
            backupCount=5
        )
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def _create_honeypots(self, directory: str) -> List[str]:
        if not self.interactive:
            return []
        honeypot_files = []
        protected_paths = [
            'C:\\$Recycle.Bin', 'C:\\Windows', 'C:\\Program Files',
            'C:\\Program Files (x86)', '/System', '/sys', '/proc', '/dev'
        ]
        directory_lower = directory.lower()
        for protected in protected_paths:
            if directory_lower.startswith(protected.lower()):
                self.logger.info(f"Skipping honeypot creation in protected path: {directory}")
                return []
        if not os.access(directory, os.W_OK):
            self.logger.info(f"Skipping honeypot creation in non-writable path: {directory}")
            return []
        bait_names = ['passwords.txt', 'credentials.json', 'backup.sql']
        honeypot_dir = os.path.join(directory, '.honeypot')
        try:
            os.makedirs(honeypot_dir, exist_ok=True)
            for name in bait_names:
                filepath = os.path.join(honeypot_dir, name)
                if not os.path.exists(filepath):
                    try:
                        with open(filepath, 'w') as f:
                            f.write(f"# HONEYPOT - {datetime.now()}\n")
                        honeypot_files.append(filepath)
                    except (PermissionError, OSError) as e:
                        self.logger.debug(f"Could not create honeypot {filepath}: {e}")
                        continue
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Could not create honeypot directory in {directory}: {e}")
        return honeypot_files

    def on_created(self, event):
        if event.is_directory: return
        filepath = event.src_path
        if not self._should_process_file(filepath): return
        self._create_backup_with_progress(filepath, 'file_created')

    def on_deleted(self, event):
        if event.is_directory: return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        workspace_path = os.path.normpath(self.workspace.base_path)
        if os.path.normpath(filepath).startswith(workspace_path): return
        skip_extensions = ('.tmp', '.temp', '.db-journal', '.db-wal', '.db-shm')
        if filename.endswith(skip_extensions): return
        try:
            file_size = os.path.getsize(filepath)
        except:
            file_size = 0
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM backups
            WHERE filename = ?
            AND file_size BETWEEN ? AND ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (filename, int(file_size * 0.9), int(file_size * 1.1)))
        backup = cursor.fetchone()
        if not backup:
            cursor.execute('SELECT * FROM backups WHERE filename = ? ORDER BY created_at DESC LIMIT 1', (filename,))
            backup = cursor.fetchone()
        if backup:
            backup_dict = dict(backup)
            if self.interactive and self.ui:
                self.ui.display_notification(
                    "DELETION DETECTED",
                    f"✓ {filename}\nBackup exists - can restore!",
                    "warning"
                )
            self.db.add_deletion_event(filepath, backup_dict['file_hash'], backup_dict['id'])
            self.logger.info(f"Deletion detected, backup exists: {filename}")
        else:
            if self.interactive and self.ui:
                self.ui.display_notification(
                    "DELETION DETECTED",
                    f"⚠ {filename}\nNo backup available",
                    "error"
                )
            self.db.add_deletion_event(filepath, "NO_BACKUP")
            self.logger.warning(f"File deleted without backup: {filename}")

    def on_modified(self, event):
        if event.is_directory: return
        filepath = event.src_path
        if self._should_process_file(filepath):
            self._create_backup_with_progress(filepath, 'file_modified')

    def on_moved(self, event):
        if event.is_directory: return
        if hasattr(event, 'dest_path') and self._is_trash_path(event.dest_path):
            self._create_backup_with_progress(event.src_path, 'moved_to_trash')

    def _create_backup_with_progress(self, filepath: str, trigger: str):
        if not os.path.exists(filepath): return
        filename = os.path.basename(filepath)
        display_name = filename[:40] + '...' if len(filename) > 40 else filename
        if self.interactive and self.ui:
            self.ui.progress.start_operation(f"Backing up: {display_name}", 100)
        try:
            if self.interactive and self.ui: self.ui.progress.update_progress(10, "Analyzing file...")
            file_size = os.path.getsize(filepath)
            if self.interactive and self.ui: self.ui.progress.update_progress(20, "Calculating hash...")
            file_hash = self._calculate_hash(filepath)
            if self.db.version_exists(file_hash):
                if self.interactive and self.ui:
                    self.ui.progress.complete_operation(True, "Already backed up")
                return
            if self.interactive and self.ui: self.ui.progress.update_progress(30, "Categorizing file...")
            category = self._categorize_file(filename)
            if self.interactive and self.ui: self.ui.progress.update_progress(40, "Preparing backup location...")
            backup_dir = os.path.join(
                self.workspace.get_backup_path(category),
                datetime.now().strftime("%Y/%m/%d")
            )
            os.makedirs(backup_dir, exist_ok=True)
            if self.interactive and self.ui: self.ui.progress.update_progress(50, f"Copying {filename[:30]}...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            backup_filename = f"{timestamp}_{filename}"
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(filepath, backup_path)
            if self.interactive and self.ui: self.ui.progress.update_progress(80, "Verifying copy...")
            backup_hash = self._calculate_hash(backup_path)
            if backup_hash != file_hash:
                raise Exception("Hash verification failed")
            if self.interactive and self.ui: self.ui.progress.update_progress(90, "Applying protection...")
            self._protect_file(backup_path)
            encryption_status = 'none'
            if self.config.get('encrypt_backups', False):
                encrypted_path = self.encryption.encrypt_file(backup_path)
                if encrypted_path != backup_path:
                    os.remove(backup_path)
                    backup_path = encrypted_path
                    encryption_status = 'fernet'
            backup_data = {
                'original_path': filepath,
                'backup_path': backup_path,
                'filename': filename,
                'file_hash': file_hash,
                'file_size': file_size,
                'category': category,
                'encryption_status': encryption_status,
                'metadata': {'trigger': trigger}
            }
            self.db.add_backup(backup_data)
            size_mb = file_size / (1024 * 1024)
            if self.interactive and self.ui:
                self.ui.progress.complete_operation(True, f"✓ {filename[:40]} ({size_mb:.2f} MB)")
            self.stats['total_backups'] += 1
            self.stats['total_size'] += file_size
            self.logger.info(f"Backup created: {filename} ({size_mb:.2f} MB)")
        except Exception as e:
            if self.interactive and self.ui:
                self.ui.progress.complete_operation(False, f"Failed: {str(e)}")
            self.logger.error(f"Backup failed for {filename}: {e}")

    def _protect_file(self, filepath: str) -> bool:
        try:
            # Set read-only
            os.chmod(filepath, 0o444)
            
            # Create the protected directory if it doesn't exist
            protected_dir = self.workspace.get_path('backups_protected')
            os.makedirs(protected_dir, exist_ok=True)  # ← ADD THIS LINE
            
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            protected_path = os.path.join(
                protected_dir,
                os.path.basename(filepath) + '.protected'
            )
            if not os.path.exists(protected_path):
                try:
                    os.link(filepath, protected_path)
                except:
                    shutil.copy2(filepath, protected_path)
            self.protected_paths.add(filepath)
            return True
        except Exception as e:
            self.logger.error(f"Failed to protect file {filepath}: {e}")
            return False

<<<<<<< HEAD
    def _backup(self, path: str, trigger: str):
        # CRITICAL FIX: Check if paused before backing up
        if self.paused:
            self._log_event('INFO', path, f"⏸️ Skipped backup (paused)")
            return
            
        if not os.path.exists(path): 
            return
        name = os.path.basename(path)
        if '_restored_' in name:
            return
        
        self._log_event('BACKUP', path, f"Trigger: {trigger}")
        
        for attempt in range(3):
            try:
                time.sleep(0.2 * attempt)
                h = self._calculate_hash(path)
                if self.db.version_exists(h):
                    self._log_event('INFO', path, "Already backed up (hash exists)")
                    return
                
                cat = self._categorize(name)
                backup_dir = os.path.join(
                    self.workspace.get_backup_path(cat),
                    datetime.now().strftime("%Y/%m/%d")
                )
                os.makedirs(backup_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                backup_path = os.path.join(backup_dir, f"{ts}_{name}")
                shutil.copy2(path, backup_path)
                
                self.db.add_backup({
                    'original_path': path,
                    'backup_path': backup_path,
                    'filename': name,
                    'file_hash': h,
                    'file_size': os.path.getsize(path),
                    'category': cat,
                    'metadata': {'trigger': trigger}
                })
                
                size_kb = os.path.getsize(path) / 1024
                self._log_event('BACKUP', path, f"✓ Saved to {backup_path} ({size_kb:.1f} KB)")
                self.stats['total_backups'] += 1
                self.stats['total_size'] += os.path.getsize(path)
                break
            except PermissionError:
                if attempt == 2:
                    self._log_event('WARNING', path, "Skipping locked file")
                continue
            except Exception as e:
                self._log_event('ERROR', path, f"Backup failed: {e}")
                break

    def on_created(self, event):
        if event.is_directory: 
            return
        filepath = event.src_path
        # CRITICAL FIX: Check if paused before processing
        if self.paused:
            self._log_event('INFO', filepath, "⏸️ Skipped (paused) - created")
            return
        self._log_event('CREATED', filepath, "New file detected")
        if self._should_process_file(filepath): 
            self._backup(filepath, 'file_created')

    def on_deleted(self, event):
        if event.is_directory: 
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # CRITICAL FIX: Check if paused before processing
        if self.paused:
            self._log_event('INFO', filepath, "⏸️ Skipped (paused) - deleted")
            return
        
        self._log_event('DELETED', filepath, "File deleted!")
        
        workspace_path = os.path.normpath(self.workspace.base_path)
        if os.path.normpath(filepath).startswith(workspace_path): 
            return
        
        skip_extensions = ('.tmp', '.temp', '.db-journal', '.db-wal', '.db-shm')
        if filename.endswith(skip_extensions): 
            return
        
        try:
            file_size = os.path.getsize(filepath)
        except:
            file_size = 0
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM backups
            WHERE filename = ?
            AND file_size BETWEEN ? AND ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (filename, int(file_size * 0.9), int(file_size * 1.1)))
        backup = cursor.fetchone()
        
        if not backup:
            cursor.execute('SELECT * FROM backups WHERE filename = ? ORDER BY created_at DESC LIMIT 1', (filename,))
            backup = cursor.fetchone()
        
        if backup:
            backup_dict = dict(backup)
            self.db.add_deletion_event(filepath, backup_dict['file_hash'], backup_dict['id'])
            self._log_event('INFO', filepath, f"Backup found (ID: {backup_dict['id']}) - Can restore!")
        else:
            self.db.add_deletion_event(filepath, "NO_BACKUP")
            self._log_event('WARNING', filepath, "⚠️ No backup found! File may be lost.")

    def on_modified(self, event):
        if event.is_directory: 
            return
        filepath = event.src_path
        # CRITICAL FIX: Check if paused before processing
        if self.paused:
            self._log_event('INFO', filepath, "⏸️ Skipped (paused) - modified")
            return
        self._log_event('MODIFIED', filepath, "File modified - checking for changes")
        if self._should_process_file(filepath):
            self._backup(filepath, 'file_modified')

    def on_moved(self, event):
        if event.is_directory: 
            return
        src_path = event.src_path
        dest_path = event.dest_path if hasattr(event, 'dest_path') else 'unknown'
        # CRITICAL FIX: Check if paused before processing
        if self.paused:
            self._log_event('INFO', src_path, "⏸️ Skipped (paused) - moved")
            return
        self._log_event('MOVED', src_path, f"→ {dest_path}")
        
        if self._is_trash_path(dest_path):
            self._log_event('WARNING', src_path, "⚠️ File moved to trash!")
            self._backup(src_path, 'moved_to_trash')

    def _create_honeypots(self, base_path: str) -> List[str]:
        """Create honeypot files to detect deletion attempts"""
        honeypots = []
        honeypot_names = [
            'important_data.txt',
            'backup_config.json',
            'system_restore.log'
        ]
        
        for name in honeypot_names:
            try:
                honeypot_path = os.path.join(base_path, name)
                if not os.path.exists(honeypot_path):
                    with open(honeypot_path, 'w') as f:
                        f.write(f"Honeypot file created at {datetime.now()}\n")
                        f.write("This file is monitored for deletion attempts.\n")
                    os.chmod(honeypot_path, 0o444)  # Read-only
                    honeypots.append(honeypot_path)
                    self._log_event('INFO', honeypot_path, "Honeypot created")
            except Exception as e:
                self.logger.debug(f"Could not create honeypot in {base_path}: {e}")
        
        return honeypots
=======
    def _calculate_hash(self, filepath: str) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _categorize_file(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']: return 'images'
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']: return 'documents'
        elif ext in ['.xls', '.xlsx', '.csv', '.ods']: return 'spreadsheets'
        elif ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.ts']: return 'code'
        elif ext in ['.json', '.yaml', '.yml', '.ini', '.conf', '.env', '.toml']: return 'config'
        elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z', '.bz2']: return 'archives'
        elif ext in ['.mp4', '.mp3', '.avi', '.mov', '.wav', '.flac', '.m4a']: return 'media'
        else: return 'other'

    def _should_process_file(self, filepath: str) -> bool:
        workspace_path = os.path.normpath(self.workspace.base_path)
        filepath_norm = os.path.normpath(filepath)
        if filepath_norm.startswith(workspace_path): return False
        filename = os.path.basename(filepath)
        skip_patterns = ['*.db', '*.db-journal', '*.db-wal', '*.db-shm', '*.sqlite', '*.sqlite3']
        for pattern in skip_patterns:
            if fnmatch.fnmatch(filename, pattern): return False
        system_patterns = ['*.tmp', '*.temp', '*~', '.DS_Store', 'Thumbs.db', 'desktop.ini', '*.crdownload']
        for pattern in system_patterns:
            if fnmatch.fnmatch(filename, pattern): return False
        for pattern in self.config.get('exclude_patterns', []):
            if fnmatch.fnmatch(filepath, pattern): return False
        max_size = self.config.get('max_file_size', 100 * 1024 * 1024)
        try:
            if os.path.getsize(filepath) > max_size: return False
        except (OSError, IOError):
            return False
        return True

    def _is_trash_path(self, path: str) -> bool:
        return self.platform_detector.is_trash_path(path)

    def _is_monitored_path(self, path: str) -> bool:
        path_normalized = self.platform_detector.normalize_path(path)
        for monitor_path in self.config['monitor_paths']:
            monitor_normalized = self.platform_detector.normalize_path(monitor_path)
            if path_normalized.startswith(monitor_normalized):
                return True
        return False
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

    def get_statistics(self) -> Dict[str, Any]:
        db_stats = self.db.get_statistics()
        return {
            'total_backups': db_stats['total_backups'],
            'total_size': db_stats['total_size'],
            'session_backups': self.stats['total_backups'],
            'session_size': self.stats['total_size'],
            'deletions_today': db_stats['deletions_today'],
            'protected_files': len(self.protected_paths)
        }

<<<<<<< HEAD
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'paused': self.paused,
            'total_backups': self.stats['total_backups'],
            'monitored_paths': len(self.config.get('monitor_paths', [])),
            'uptime': str(datetime.now() - self.start_time).split('.')[0] if hasattr(self, 'start_time') else 'N/A',
            'last_event': self._last_event_time
        }
        
    def _setup_console_output(self):
        """Enable real-time console output for monitoring events"""
        self.console_enabled = True
        print("\n" + "=" * 70)
        print("🛡️  DSTERMINAL DELETION PROTECTION - REAL-TIME MONITORING")
        print("=" * 70)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📌 Monitoring events will appear below in real-time")
        print("=" * 70 + "\n")

    def _log_event(self, event_type: str, filepath: str, details: str = ""):
        """Log events to console and log file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        emojis = {
            'CREATED': '📄',
            'MODIFIED': '✏️',
            'DELETED': '🗑️',
            'MOVED': '📂',
            'BACKUP': '💾',
            'ERROR': '❌',
            'INFO': 'ℹ️',
            'WARNING': '⚠️'
        }
        emoji = emojis.get(event_type, 'ℹ️')
        filename = os.path.basename(filepath) if filepath else 'N/A'
        
        # Print to console
        if self.console_enabled:
            print(f"{emoji} [{timestamp}] {event_type:8} | {filename:<30} | {details}")
            sys.stdout.flush()
        
        # Log to file
        self.logger.info(f"{event_type} | {filepath} | {details}")

    def _setup_logging(self):
        self.logger = logging.getLogger('DSTerminal')
        self.logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler(
            self.workspace.get_log_path(),
            maxBytes=10*1024*1024,
            backupCount=5
        )
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def cleanup(self):
        self._log_event('INFO', 'SYSTEM', "Shutting down monitoring...")
=======
    def cleanup(self):
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        self.logger.info("Shutting down DSTerminal...")
        for honeypot in self.honeypots:
            try:
                if os.path.exists(honeypot):
                    os.remove(honeypot)
            except:
                pass
        self.workspace.cleanup_temp_files()
        self.db.close()
        self.logger.info("DSTerminal shutdown complete")
<<<<<<< HEAD
        print("\n🛑 Monitoring stopped.")
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

    def signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)

<<<<<<< HEAD

# ============================================================
# 7. NEW FOLDER WATCHER
# ============================================================

class NewFolderWatcher(FileSystemEventHandler):
=======
class NewFolderWatcher(FileSystemEventHandler):
    """Watches for new folder creation and auto-adds them to monitoring."""
    
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    def __init__(self, config, monitor_handler, observer, workspace):
        self.config = config
        self.monitor_handler = monitor_handler
        self.observer = observer
        self.workspace = workspace
        self.logger = logging.getLogger('FolderWatcher')
    
    def on_created(self, event):
        if not event.is_directory:
            return
<<<<<<< HEAD
        new_folder = event.src_path
        basename = os.path.basename(new_folder)
        if basename.startswith('.') or basename.startswith('$') or basename == '__pycache__':
            return
        workspace_path = os.path.normpath(self.workspace.base_path if hasattr(self.workspace, 'base_path') else str(self.workspace))
        if os.path.normpath(new_folder).startswith(workspace_path):
            return
=======
        
        new_folder = event.src_path
        basename = os.path.basename(new_folder)
        
        if basename.startswith('.') or basename.startswith('$') or basename == '__pycache__':
            return
        
        workspace_path = os.path.normpath(self.workspace if isinstance(self.workspace, str) 
                                          else self.workspace.base_path)
        if os.path.normpath(new_folder).startswith(workspace_path):
            return
        
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if new_folder not in self.config['monitor_paths']:
            self.config['monitor_paths'].append(new_folder)
            if self.observer and self.observer.is_alive():
                self.observer.schedule(
                    self.monitor_handler,
                    path=new_folder,
                    recursive=True
                )
            self.logger.info(f"New folder auto-monitored: {new_folder}")
            print(f"  ✓ New folder detected & monitored: {new_folder}")
<<<<<<< HEAD


# ============================================================
# 8. RESTORE MANAGER
# ============================================================
=======
# In deletion_protection.py
# Inside class DSTerminalMonitor(FileSystemEventHandler):
# Find the existing _should_process_file method and replace with:

    def _should_process_file(self, filepath: str) -> bool:
        # Skip workspace files
        workspace_path = os.path.normpath(
            self.workspace.base_path if hasattr(self.workspace, 'base_path') 
            else str(self.workspace)
        )
        filepath_norm = os.path.normpath(filepath)
        if filepath_norm.startswith(workspace_path):
            return False
        
        # Skip restored files to avoid re-backup loops
        filename = os.path.basename(filepath)
        if '_restored_' in filename:
            return False
        
        # Skip database/temp files
        skip_patterns = ['*.db', '*.db-journal', '*.db-wal', '*.db-shm', '*.sqlite', '*.sqlite3']
        for pattern in skip_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        
        # Skip system files
        system_patterns = ['*.tmp', '*.temp', '*~', '.DS_Store', 'Thumbs.db', 'desktop.ini', '*.crdownload']
        for pattern in system_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        
        # Skip excluded patterns from config
        for pattern in self.config.get('exclude_patterns', []):
            if fnmatch.fnmatch(filepath, pattern):
                return False
        
        # Skip files exceeding max size
        max_size = self.config.get('max_file_size', 100 * 1024 * 1024)
        try:
            if os.path.getsize(filepath) > max_size:
                return False
        except (OSError, IOError):
            return False
        
        return True

    def _backup(self, path: str, trigger: str):
        if not os.path.exists(path): return
        name = os.path.basename(path)
        
        # Skip restored files to avoid loops
        if '_restored_' in name:
            return
        
        # Retry up to 3 times for locked files
        for attempt in range(3):
            try:
                time.sleep(0.2 * attempt)  # Wait longer each retry
                h = self._hash(path)
                if self.db.version_exists(h):
                    return
                
                cat = self._categorize(name)
                backup_dir = os.path.join(
                    self.workspace.get_backup_path(cat),
                    datetime.now().strftime("%Y/%m/%d")
                )
                os.makedirs(backup_dir, exist_ok=True)
                
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                backup_path = os.path.join(backup_dir, f"{ts}_{name}")
                shutil.copy2(path, backup_path)
                
                self.db.add_backup({
                    'original_path': path, 'backup_path': backup_path,
                    'filename': name, 'file_hash': h,
                    'file_size': os.path.getsize(path), 'category': cat,
                    'metadata': {'trigger': trigger}
                })
                self.stats['total_backups'] += 1
                self.stats['total_size'] += os.path.getsize(path)
                self.logger.info(f"Backup created: {name} ({os.path.getsize(path)/1024:.1f} KB)")
                break  # Success — exit retry loop
                
            except PermissionError:
                if attempt == 2:  # Last attempt
                    self.logger.debug(f"Skipping locked file: {name}")
                continue
            except Exception as e:
                self.logger.error(f"Backup failed for {name}: {e}")
                break

# =========================
# ♻️ RESTORE MODULE
# =========================
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

class RestoreManager:
    def __init__(self, workspace, ui=None):
        self.workspace = workspace
        self.db = BackupDatabase(workspace)
        self.encryption = EncryptionManager(workspace)
        self.ui = ui

    def list_backups(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, original_path, backup_path, filename, file_size, category,
                   created_at, restore_count, last_restored, encryption_status
            FROM backups
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_backups(self, query: str) -> List[Dict[str, Any]]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, original_path, backup_path, filename, file_size, category,
                   created_at, restore_count, last_restored, encryption_status
            FROM backups
            WHERE filename LIKE ? OR original_path LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def get_backup_by_id(self, backup_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM backups WHERE id = ?', (backup_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def restore_file(self, backup_id: int, target_path: str = None, overwrite: bool = False) -> bool:
        backup = self.get_backup_by_id(backup_id)
        if not backup:
<<<<<<< HEAD
            print(f"Backup ID {backup_id} not found.")
            return False
        try:
            backup_path = backup['backup_path']
            if not os.path.exists(backup_path):
                raise Exception(f"Backup file not found: {backup_path}")
            if backup.get('encryption_status', 'none') != 'none':
                backup_path = self.encryption.decrypt_file(backup_path)
=======
            if self.ui:
                self.ui.display_notification("RESTORE FAILED", f"Backup ID {backup_id} not found", "error")
            else:
                print(f"Backup ID {backup_id} not found.")
            return False
        display_name = backup['filename'][:40] + '...' if len(backup['filename']) > 40 else backup['filename']
        if self.ui:
            self.ui.progress.start_operation(f"Restoring: {display_name}", 100)
        try:
            if self.ui: self.ui.progress.update_progress(10, "Locating backup...")
            backup_path = backup['backup_path']
            if not os.path.exists(backup_path):
                raise Exception(f"Backup file not found: {backup_path}")
            if self.ui: self.ui.progress.update_progress(20, "Checking encryption...")
            if backup.get('encryption_status', 'none') != 'none':
                if self.ui: self.ui.progress.update_progress(30, "Decrypting file...")
                backup_path = self.encryption.decrypt_file(backup_path)
            if self.ui: self.ui.progress.update_progress(40, "Checking compression...")
            if backup_path.endswith('.zip'):
                if self.ui: self.ui.progress.update_progress(50, "Decompressing file...")
                temp_dir = tempfile.mkdtemp()
                import zipfile
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    zf.extractall(temp_dir)
                backup_path = os.path.join(temp_dir, backup['filename'])
            if self.ui: self.ui.progress.update_progress(60, "Preparing target location...")
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            if target_path is None:
                original_dir = os.path.dirname(backup['original_path'])
                if os.path.exists(original_dir) and os.access(original_dir, os.W_OK):
                    target_path = backup['original_path']
                else:
                    desktop = os.path.expanduser('~/Desktop')
                    if os.path.exists(desktop):
                        target_path = os.path.join(desktop, backup['filename'])
                    else:
                        target_path = os.path.join(os.path.expanduser('~'), backup['filename'])
            else:
                if os.path.isdir(target_path):
                    target_path = os.path.join(target_path, backup['filename'])
<<<<<<< HEAD
=======
            if self.ui: self.ui.progress.update_progress(70, "Checking destination...")
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            if os.path.exists(target_path) and not overwrite:
                base, ext = os.path.splitext(target_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = f"{base}_restored_{timestamp}{ext}"
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
<<<<<<< HEAD
            shutil.copy2(backup_path, target_path)
=======
            if self.ui: self.ui.progress.update_progress(80, "Copying file...")
            shutil.copy2(backup_path, target_path)
            if self.ui: self.ui.progress.update_progress(90, "Verifying restore...")
            restored_size = os.path.getsize(target_path)
            if restored_size != backup['file_size']:
                raise Exception("Restored file size mismatch")
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE backups
                SET restore_count = restore_count + 1, last_restored = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (backup_id,))
            self.db.conn.commit()
            os.chmod(target_path, 0o644)
<<<<<<< HEAD
            size_mb = backup['file_size'] / (1024 * 1024)
            print(f"✓ Restored: {backup['filename']} -> {target_path} ({size_mb:.2f} MB)")
            return True
        except Exception as e:
            print(f"✗ Restore failed: {backup['filename']} - {str(e)}")
=======
            size_mb = restored_size / (1024 * 1024)
            if self.ui:
                self.ui.progress.complete_operation(True, f"✓ Restored to: {target_path}\n  Size: {size_mb:.2f} MB")
                self.ui.display_notification("RESTORE SUCCESSFUL",
                                             f"File: {backup['filename']}\nLocation: {target_path}\nSize: {size_mb:.2f} MB",
                                             "success")
            else:
                print(f"✓ Restored: {backup['filename']} -> {target_path} ({size_mb:.2f} MB)")
            logging.info(f"Restored backup {backup_id}: {backup['filename']} -> {target_path}")
            return True
        except Exception as e:
            if self.ui:
                self.ui.progress.complete_operation(False, f"Failed: {str(e)}")
                self.ui.display_notification("RESTORE FAILED",
                                             f"Could not restore {backup['filename']}\nError: {str(e)}",
                                             "error")
            else:
                print(f"✗ Restore failed: {backup['filename']} - {str(e)}")
            logging.error(f"Restore failed for backup {backup_id}: {e}")
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            return False

    def restore_last_deleted(self) -> bool:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM deletion_events WHERE backed_up = 1 ORDER BY detected_at DESC LIMIT 1')
        event = cursor.fetchone()
        if not event:
<<<<<<< HEAD
            print("No backed-up deletions found")
=======
            msg = "No backed-up deletions found"
            if self.ui:
                self.ui.display_notification("NO DELETIONS", msg, "info")
            else:
                print(msg)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            return False
        return self.restore_file(event['backup_id'])


<<<<<<< HEAD
# ============================================================
# 9. SERVICE MANAGER
# ============================================================
 
class ServiceManager:
=======
# =========================
# 🛠️ SERVICE MANAGER
# =========================

class ServiceManager:
    """
    Cross‑platform service/daemon control.
    """
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    def __init__(self, workspace, pid_file: str = None):
        self.workspace = workspace
        self.pid_file = pid_file or os.path.join(workspace.base_path, 'dsterminal.pid')
        self.logger = logging.getLogger('DSTerminal.service')
<<<<<<< HEAD
        self._process = None

    def start_service(self, config: Dict[str, Any]) -> bool:
        """Start the deletion protection service with proper PID tracking"""
        import subprocess
        import time
        import psutil
        
        # FIX: Call is_running without arguments
        if self.is_running():
            print("[!] Service is already running.")
            return False
        
        try:
            # Get the Python executable and script path
            python_exe = sys.executable
            script_path = os.path.join(os.path.dirname(__file__), 'deletion_protection.py')
            
            # Start the monitoring process in a new window and capture its PID
            if platform.system() == 'Windows':
                # Windows: Use start with window title and get PID
                cmd = f'start "DSTERMINAL MONITOR" "{python_exe}" "{script_path}" --daemon'
                subprocess.Popen(cmd, shell=True)
                
                # Wait a moment for the process to start
                time.sleep(3)
                
                # Find the actual Python process running deletion_protection
                found_pid = None
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python.exe':
                            cmdline = ' '.join(proc.info['cmdline'] or [])
                            if 'deletion_protection.py' in cmdline and '--daemon' in cmdline:
                                found_pid = proc.info['pid']
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if found_pid:
                    with open(self.pid_file, 'w') as f:
                        f.write(str(found_pid))
                    print(f"✅ Service started with PID: {found_pid}")
                    return True
                else:
                    print("⚠️ Could not find monitor process PID. Service may still be running.")
                    # Try to find and update PID
                    self._find_and_update_pid()
                    return True
                    
            else:
                # Linux/macOS: Use terminal
                terminals = ['xterm', 'gnome-terminal', 'konsole', 'terminator']
                for term in terminals:
                    if subprocess.run(['which', term], capture_output=True).returncode == 0:
                        subprocess.Popen([term, '-e', f'{python_exe} {script_path} --daemon'])
                        break
                else:
                    # Fallback: run in background
                    proc = subprocess.Popen([python_exe, script_path, '--daemon'])
                    with open(self.pid_file, 'w') as f:
                        f.write(str(proc.pid))
                
                time.sleep(2)
                
                # Verify the service is running
                if self.is_running():
                    return True
                else:
                    # Try to find the process
                    self._find_and_update_pid()
                    return self.is_running()
                
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            return False
    
    def _find_and_update_pid(self):
        """Find the monitoring process and update PID file"""
        import subprocess
        
        try:
            if platform.system() == 'Windows':
                # Find Python processes running deletion_protection
                result = subprocess.run(
                    ['wmic', 'process', 'where', 'name="python.exe"', 'get', 'processid,commandline'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'deletion_protection' in line.lower() and '--daemon' in line.lower():
                        parts = line.split()
                        for part in parts:
                            if part.isdigit() and len(part) > 3:
                                with open(self.pid_file, 'w') as f:
                                    f.write(part)
                                print(f"✅ Found and updated PID: {part}")
                                return True
            else:
                # Unix/Linux
                result = subprocess.run(
                    ['pgrep', '-f', 'deletion_protection.*--daemon'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if line.strip():
                        pid = int(line.strip())
                        with open(self.pid_file, 'w') as f:
                            f.write(str(pid))
                        print(f"✅ Found and updated PID: {pid}")
                        return True
        except Exception as e:
            print(f"⚠️ Could not find process: {e}")
        
        return False

    def pause_service(self):
        """Pause the monitoring service"""
        # FIX: Use get_detailed_status to check if running
        status = self.get_detailed_status()
        if not status['running']:
            print("❌ Service is not running.")
            return False
        
        try:
            # Create pause flag in the same directory as PID file
            pause_file = os.path.join(os.path.dirname(self.pid_file), 'pause.flag')
            with open(pause_file, 'w') as f:
                f.write('paused')
            print("⏸️  Monitoring PAUSED")
            return True
        except Exception as e:
            print(f"❌ Failed to pause: {e}")
            return False

    def resume_service(self):
        """Resume the monitoring service"""
        pause_file = os.path.join(os.path.dirname(self.pid_file), 'pause.flag')
        if os.path.exists(pause_file):
            try:
                os.remove(pause_file)
                print("▶️  Monitoring RESUMED")
                return True
            except Exception as e:
                print(f"❌ Failed to resume: {e}")
                return False
        else:
            print("ℹ️ Service is not paused.")
            return False

    def is_paused(self) -> bool:
        """Check if service is paused"""
        pause_file = os.path.join(os.path.dirname(self.pid_file), 'pause.flag')
        return os.path.exists(pause_file)

    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed service status"""
        import subprocess
        import platform
        
        pid = self._read_pid()
        running = False
        
        if pid:
            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(
                        ['tasklist', '/FI', f'PID eq {pid}'],
                        capture_output=True, text=True, timeout=5
                    )
                    if str(pid) in result.stdout:
                        running = True
                except:
                    pass
            else:
                try:
                    os.kill(pid, 0)
                    running = True
                except OSError:
                    pass
        
        return {
            'running': running,
            'paused': self.is_paused(),
            'pid_file': self.pid_file,
            'pid': pid if running else None
        }

    def _read_pid(self) -> Optional[int]:
        """Read PID from file"""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return int(content)
        except Exception as e:
            print(f"⚠️ Error reading PID: {e}")
        return None

    def daemonize(self):
=======

    def daemonize(self):
        """Daemonize the process (Unix only)."""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if platform.system() == 'Windows':
            self._windows_detach()
            return
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"First fork failed: {e}\n")
            sys.exit(1)
        os.chdir('/')
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"Second fork failed: {e}\n")
            sys.exit(1)
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        self._write_pid_file()

    def _windows_detach(self):
<<<<<<< HEAD
=======
        """Windows 'detach': hide console."""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        self._write_pid_file()

    def _write_pid_file(self):
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def remove_pid_file(self):
        try:
<<<<<<< HEAD
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
        except OSError:
            pass

    def is_running(self) -> bool:
        """Check if service is running using self.pid_file"""
        if not os.path.exists(self.pid_file):
            return False
        try:
            with open(self.pid_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return False
                pid = int(content)
            
=======
            os.remove(self.pid_file)
        except OSError:
            pass

    @staticmethod
    def is_running(pid_file: str) -> bool:
        if not os.path.exists(pid_file):
            return False
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            if PSUTIL_AVAILABLE:
                import psutil
                return psutil.pid_exists(pid)
            else:
<<<<<<< HEAD
                if platform.system() == 'Windows':
                    import subprocess
                    result = subprocess.run(
                        ['tasklist', '/FI', f'PID eq {pid}'],
                        capture_output=True, text=True, timeout=5
                    )
                    return str(pid) in result.stdout
                else:
                    os.kill(pid, 0)
                    return True
        except (OSError, ValueError, subprocess.TimeoutExpired):
            # PID file exists but process not found - clean it up
            try:
                os.remove(self.pid_file)
            except:
                pass
            return False

    def _find_monitoring_window(self):
        """Find the monitoring window by title or process name"""
        import subprocess
        processes = []
        
        try:
            if platform.system() == 'Windows':
                # Get all Python processes
                result = subprocess.run(
                    ['tasklist', '/V', '/FO', 'CSV'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'python' in line.lower() and ('DSTERMINAL' in line or 'deletion_protection' in line.lower()):
                        parts = line.split(',')
                        if len(parts) > 1:
                            pid_str = parts[1].strip('"')
                            try:
                                processes.append(int(pid_str))
                            except:
                                pass
            else:
                # Unix/Linux - use pgrep
                result = subprocess.run(
                    ['pgrep', '-f', 'deletion_protection'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if line.strip():
                        try:
                            processes.append(int(line.strip()))
                        except:
                            pass
        except Exception as e:
            print(f"⚠️ Could not find monitoring window: {e}")
        
        return processes

    def stop_service(self):
        """Stop the deletion protection service - kills the process and closes the window"""
        import subprocess
        
        print("[*] Stopping deletion protection service...")
        
        # Method 1: Kill by PID from file
        killed_pids = []
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                print(f"  📌 Found PID: {pid}")
                
                if platform.system() == 'Windows':
                    # Kill process tree
                    try:
                        subprocess.run(
                            ['taskkill', '/F', '/T', '/PID', str(pid)],
                            capture_output=True, timeout=5, check=False
                        )
                        print(f"  ✅ Killed process: {pid}")
                        killed_pids.append(pid)
                    except Exception as e:
                        print(f"  ⚠️ Could not kill PID {pid}: {e}")
                    
                    # Also try killing by window title
                    try:
                        subprocess.run(
                            ['taskkill', '/F', '/FI', 'WINDOWTITLE eq DSTERMINAL*'],
                            capture_output=True, timeout=5, check=False
                        )
                        print("  ✅ Killed windows with 'DSTERMINAL' title")
                    except Exception as e:
                        print(f"  ⚠️ Could not kill by title: {e}")
                    
                    # Kill any Python processes running deletion_protection
                    try:
                        # Find all Python processes with deletion_protection
                        result = subprocess.run(
                            ['wmic', 'process', 'where', 'name="python.exe"', 'get', 'processid,commandline'],
                            capture_output=True, text=True, timeout=5
                        )
                        for line in result.stdout.split('\n'):
                            if 'deletion_protection' in line.lower():
                                parts = line.split()
                                for part in parts:
                                    if part.isdigit():
                                        try:
                                            subprocess.run(
                                                ['taskkill', '/F', '/PID', part],
                                                capture_output=True, timeout=5, check=False
                                            )
                                            print(f"  ✅ Killed process: {part}")
                                            killed_pids.append(int(part))
                                        except:
                                            pass
                    except Exception as e:
                        print(f"  ⚠️ Could not kill Python processes: {e}")
                    
                else:
                    # Unix/Linux
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                        time.sleep(1)
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                        print(f"  ✅ Killed process group: {pid}")
                        killed_pids.append(pid)
                    except ProcessLookupError:
                        print("  Process already terminated")
                    except Exception as e:
                        print(f"  ⚠️ Could not kill process: {e}")
                
            except ValueError:
                print("  ⚠️ Invalid PID file")
                self.remove_pid_file()
            except Exception as e:
                print(f"  ⚠️ Error reading PID file: {e}")
        
        # Method 2: Find and kill monitoring windows
        if platform.system() == 'Windows':
            # Get the console window title
            try:
                result = subprocess.run(
                    ['taskkill', '/F', '/FI', 'WINDOWTITLE eq DSTERMINAL MONITOR*'],
                    capture_output=True, timeout=5, check=False
                )
                if result.returncode == 0:
                    print("  ✅ Closed monitoring windows")
            except Exception as e:
                print(f"  ⚠️ Could not close windows: {e}")
            
            # Kill any remaining python processes running deletion_protection
            try:
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/V'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'deletion_protection' in line.lower():
                        # Extract PID
                        parts = line.split()
                        for part in parts:
                            if part.isdigit() and len(part) > 2:
                                try:
                                    subprocess.run(
                                        ['taskkill', '/F', '/PID', part],
                                        capture_output=True, timeout=5, check=False
                                    )
                                    print(f"  ✅ Killed remaining process: {part}")
                                except:
                                    pass
            except Exception as e:
                print(f"  ⚠️ Could not find remaining processes: {e}")
        
        # Remove PID file
        self.remove_pid_file()
        
        if killed_pids:
            print(f"\n✅ Deletion protection service stopped. (killed {len(killed_pids)} process(es))")
            print("   Monitoring window should be closed.")
        else:
            print("\n✅ PID file removed. Service flag cleared.")
            print("   If window is still open, close it manually.")
            print("   Press Ctrl+C in the monitoring window or close it with the X button.")

    def status(self):
        """Check service status"""
        import subprocess
        
        print("[*] Checking service status...")
        
        # Check if PID file exists
        if not os.path.exists(self.pid_file):
            print("  ✗ Service flag: NOT RUNNING")
            print("\n========================================")
            print("🔴 SERVICE STATUS: INACTIVE")
            print("[i] To start: service-start")
            print("========================================")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            process_exists = False
            process_name = None
            
            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(
                        ['tasklist', '/FI', f'PID eq {pid}'],
                        capture_output=True, text=True, timeout=5
                    )
                    if str(pid) in result.stdout:
                        process_exists = True
                        # Extract process name
                        for line in result.stdout.split('\n'):
                            if str(pid) in line:
                                parts = line.split()
                                if len(parts) > 0:
                                    process_name = parts[0]
                                break
                except:
                    pass
            else:
                try:
                    os.kill(pid, 0)
                    process_exists = True
                except OSError:
                    pass
            
            if process_exists:
                print(f"  ✓ Service flag: RUNNING (PID: {pid})")
                print("\n========================================")
                print("🟢 SERVICE STATUS: RUNNING")
                print("========================================")
                
                # Check if paused
                pause_file = os.path.join(os.path.dirname(self.pid_file), 'pause.flag')
                if os.path.exists(pause_file):
                    print("⏸️  Monitoring: PAUSED")
                else:
                    print("▶️  Monitoring: ACTIVE")
                print(f"📌 Process: {process_name or 'python.exe'}")
                print("========================================")
            else:
                print(f"  ⚠️ Service flag: RUNNING but process {pid} not found")
                print("\n========================================")
                print("🟡 SERVICE STATUS: PARTIAL (flag set but no process)")
                print("[i] Try: service-stop then service-start")
                print("========================================")
                # Clean up stale PID file
                self.remove_pid_file()
                
        except ValueError:
            print("  ⚠️ Invalid PID file")
            self.remove_pid_file()
        except Exception as e:
            print(f"  ⚠️ Error checking status: {e}")
# ============================================================
# 10. MAIN - RUNS WHEN EXECUTED DIRECTLY
# ============================================================
if __name__ == "__main__":
    import sys
    import argparse
    import random
    import time
    import platform as plat
    
    # ============================================================
    # CINEMATIC TYPEWRITER EFFECT
    # ============================================================
    
    def typewriter(text, delay=0.03, color_start='', color_end='\033[0m'):
        """Display text with human-like typewriter effect"""
        for char in text:
            sys.stdout.write(f"{color_start}{char}{color_end}")
            sys.stdout.flush()
            time.sleep(delay + (random.random() * 0.03))
        sys.stdout.write('\n')
        sys.stdout.flush()

    def typewriter_line(text, delay=0.025, color_start='', color_end='\033[0m'):
        """Display a line with typewriter effect and newline"""
        typewriter(text, delay, color_start, color_end)

    def typewriter_banner(text, delay=0.03, color_start='\033[96m', color_end='\033[0m'):
        """Display a banner with typewriter effect"""
        for char in text:
            sys.stdout.write(f"{color_start}{char}{color_end}")
            sys.stdout.flush()
            time.sleep(delay + (random.random() * 0.015))
        sys.stdout.write('\n')
        sys.stdout.flush()

    def slow_typewriter(text, delay=0.05, color_start='\033[92m', color_end='\033[0m'):
        """Display text with slower typewriter effect for emphasis"""
        for char in text:
            sys.stdout.write(f"{color_start}{char}{color_end}")
            sys.stdout.flush()
            time.sleep(delay + (random.random() * 0.03))
        sys.stdout.write('\n')
        sys.stdout.flush()

    def matrix_rain_line(length=40, delay=0.001):
        """Display a quick matrix-style rain line"""
        chars = '0123456789ABCDEF'
        line = ''.join(random.choice(chars) if random.random() > 0.5 else ' ' for _ in range(length))
        sys.stdout.write(f"\033[92m{line}\033[0m\n")
        sys.stdout.flush()
        time.sleep(delay)

    # ============================================================
    # BANNER GENERATOR - CINEMATIC
    # ============================================================
    
    def show_cinematic_banner():
        """Display cinematic banner with auto-typing effect"""
        
        # Clear screen
        os.system('cls' if plat.system() == 'Windows' else 'clear')
        
        # Matrix rain intro
        print("\033[92m", end='')
        for _ in range(3):
            matrix_rain_line(50, 0.001)
        print("\033[0m", end='')
        
        time.sleep(0.3)
        
        # Main banner with typewriter
        typewriter_banner("")
        typewriter_banner("█▀▀ ▄▀█ █▀█ █▀▀ ▀█▀ █ █▀█ █▄░█", 0.04, '\033[96m')
        typewriter_banner("█▄▄ █▀█ █▀▄ ██▄ ░█░ █ █▄█ █░▀█", 0.04, '\033[96m')
        typewriter_banner("")
        typewriter_banner("  ██████╗ ███████╗██╗     ███████╗████████╗██╗ ██████╗ ███╗   ██╗", 0.035, '\033[92m')
        typewriter_banner("  ██╔══██╗██╔════╝██║     ██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║", 0.035, '\033[92m')
        typewriter_banner("  ██║  ██║█████╗  ██║     █████╗     ██║   ██║██║   ██║██╔██╗ ██║", 0.035, '\033[92m')
        typewriter_banner("  ██║  ██║██╔══╝  ██║     ██╔══╝     ██║   ██║██║   ██║██║╚██╗██║", 0.035, '\033[92m')
        typewriter_banner("  ██████╔╝███████╗███████╗███████╗   ██║   ██║╚██████╔╝██║ ╚████║", 0.035, '\033[92m')
        typewriter_banner("  ╚═════╝ ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝", 0.035, '\033[92m')
        typewriter_banner("")
        time.sleep(0.3)
        
        # Tagline with typewriter
        typewriter_banner("  ╔══════════════════════════════════════════════════════════════╗", 0.02, '\033[93m')
        typewriter_banner("  ║          DELETION PROTECTION - REAL-TIME MONITORING         ║", 0.02, '\033[93m')
        typewriter_banner("  ║        SYSTEM-WIDE FILE CHANGE DETECTION & BACKUP            ║", 0.02, '\033[93m')
        typewriter_banner("  ╚══════════════════════════════════════════════════════════════╝", 0.02, '\033[93m')
        typewriter_banner("")
        time.sleep(0.3)
        
        typewriter_banner("")
                
        # Quick status display
        typewriter_line("  ╔═══════════════════════════════════════════════════════════╗", 0.015, '\033[90m')
        typewriter_line("  ║  📊 STATUS: INITIALIZING...                              ║", 0.015, '\033[90m')
        typewriter_line("  ╚═══════════════════════════════════════════════════════════╝", 0.015, '\033[90m')
        typewriter_banner("")
        time.sleep(0.5)

    def show_paused_banner():
        """Display paused banner in monitor window"""
        os.system('cls' if plat.system() == 'Windows' else 'clear')
        print("\n" + "=" * 70)
        print("🛡️  DSTERMINAL DELETION PROTECTION")
        print("=" * 70)
        print("⏸️  " + "=" * 60)
        print("⏸️  MONITORING PAUSED - No backups will be created")
        print("⏸️  " + "=" * 60)
        print("\n📌 To resume: Run 'service resume' in the main terminal")
        print("📌 Or delete the pause.flag file from:")
        print(f"   {os.path.expanduser('~/dsterminal_workspace/pause.flag')}")
        print("\n" + "=" * 70)
        print("⏳ Waiting for resume command...")

    def show_active_banner(monitor_paths_count):
        """Show active monitoring banner"""
        os.system('cls' if plat.system() == 'Windows' else 'clear')
        print("\n" + "=" * 70)
        print("🛡️  DSTERMINAL DELETION PROTECTION - REAL-TIME MONITORING")
        print("=" * 70)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Monitoring: {monitor_paths_count} folders")
        print("▶️  Monitoring: ACTIVE")
        print("📌 Press Ctrl+C to stop monitoring")
        print("=" * 70 + "\n")

    # ============================================================
    # MAIN EXECUTION
    # ============================================================
    
    parser = argparse.ArgumentParser(description='DSTerminal Deletion Protection')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    if args.daemon:
        try:
            # Show cinematic banner
            show_cinematic_banner()
            
            # Typewriter status messages
            typewriter_line("  🔍 Analyzing system for monitoring targets...", 0.035, '\033[96m')
            time.sleep(0.5)
            
            # Setup workspace
            workspace = SimpleWorkspace(os.path.expanduser('~/dsterminal_workspace'))
            
            # Get all paths to monitor
            platform_detector = PlatformDetector()
            monitor_paths = []
            
            if platform_detector.is_windows:
                import string
                typewriter_line("  🖥️  Windows System Detected", 0.03, '\033[92m')
                typewriter_line("  📡 Scanning drives...", 0.03, '\033[92m')
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        monitor_paths.append(drive)
                        typewriter_line(f"      ✓ Drive {drive} detected", 0.015, '\033[90m')
            else:
                typewriter_line("  🐧 Linux/macOS System Detected", 0.03, '\033[92m')
                monitor_paths = ['/', '/home', '/usr', '/var', '/opt', '/etc', '/tmp']
                for path in monitor_paths:
                    if os.path.exists(path):
                        typewriter_line(f"      ✓ {path} detected", 0.015, '\033[90m')
            
            # Add user directories
            home = os.path.expanduser('~')
            user_paths = [home, os.path.join(home, 'Desktop'), os.path.join(home, 'Downloads'),
                         os.path.join(home, 'Documents'), os.path.join(home, 'Pictures'),
                         os.path.join(home, 'Videos'), os.path.join(home, 'Music')]
            
            typewriter_line("  📁 Scanning user directories...", 0.03, '\033[92m')
            for path in user_paths:
                if os.path.exists(path) and path not in monitor_paths:
                    monitor_paths.append(path)
                    typewriter_line(f"      ✓ {os.path.basename(path)}", 0.015, '\033[90m')
            
            monitor_paths = list(set([p for p in monitor_paths if os.path.exists(p)]))
            
            config = {
                'monitor_paths': monitor_paths,
                'exclude_patterns': ['*.tmp', '*.temp', '*~', '.DS_Store'],
                'max_file_size': 100 * 1024 * 1024
            }
            
            time.sleep(0.3)
            typewriter_line("")
            typewriter_line(f"  ✅ Monitoring {len(monitor_paths)} folders", 0.035, '\033[92m')
            typewriter_line("  🟢 Press Ctrl+C to stop\n", 0.03, '\033[93m')
            time.sleep(0.5)
            
            # Start monitoring
            monitor = DSTerminalMonitor(config, workspace, interactive=True, verbose=True)
            
            from watchdog.observers import Observer
            observer = Observer()
            
            for path in monitor_paths:
                if os.path.exists(path):
                    observer.schedule(monitor, path, recursive=True)
                    typewriter_line(f"  ✓ Monitoring: {path}", 0.015, '\033[90m')
            
            observer.start()
            
            # ============================================================
            # FIX: PAUSE/RESUME SUPPORT WITH VISUAL INDICATOR
            # ============================================================
            
            # Get the pause flag file path (same as service manager)
            pause_file = os.path.join(workspace.base_path, 'pause.flag')
            
            # Get the PID file path (same as service manager)
            pid_file = os.path.join(workspace.base_path, 'dsterminal.pid')
            
            # Write the actual PID
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            # Show active monitoring banner
            show_active_banner(len(monitor_paths))
            
            # Track state
            was_paused = False
            last_event_time = time.time()
            
            # ============================================================
            # MAIN LOOP WITH PAUSE CHECK - FIXED
            # ============================================================
 
            try:
                while True:
                    # Check if pause flag exists
                    pause_exists = os.path.exists(pause_file)
                    
                    # Update monitor's paused state with lock
                    with monitor.pause_lock:
                        if pause_exists != monitor.paused:
                            monitor.paused = pause_exists
                            if pause_exists:
                                # Show paused banner
                                show_paused_banner()
                                was_paused = True
                            else:
                                # Show active banner
                                show_active_banner(len(monitor_paths))
                                was_paused = False
                    
                    # If not paused, check for events to display
                    if not pause_exists and not was_paused:
                        # This is just to keep the loop alive - events are handled by watchdog
                        pass
                    
                    time.sleep(0.5)
                    
            except KeyboardInterrupt:
                typewriter_line("\n  🛑 Shutting down...", 0.04, '\033[91m')
                observer.stop()
                observer.join()
                typewriter_line("  ✅ Monitoring stopped.", 0.035, '\033[92m')
                # Clean up PID file
                if os.path.exists(pid_file):
                    os.remove(pid_file)
                # Clean up pause flag
                if os.path.exists(pause_file):
                    os.remove(pause_file)
                sys.exit(0)
                
        except Exception as e:
            typewriter_line(f"\n  ❌ Error: {str(e)}", 0.04, '\033[91m')
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    else:
        # Interactive mode - show module info with typewriter effect
        show_cinematic_banner()
        
        time.sleep(0.3)
        typewriter_line("  📦 MODULE INFORMATION", 0.035, '\033[96m')
        typewriter_line("  ════════════════════════════════════════════", 0.02, '\033[90m')
        
        typewriter_line("")
        typewriter_line("  🚀 To run as a service:", 0.03, '\033[96m')
        typewriter_line("  python deletion_protection.py --daemon", 0.025, '\033[93m')
        typewriter_line("")
        typewriter_line("  ⏸️  To pause monitoring:", 0.03, '\033[96m')
        typewriter_line("  Create a file: ~/dsterminal_workspace/pause.flag", 0.025, '\033[93m')
        typewriter_line("  OR use: service pause", 0.025, '\033[93m')
        typewriter_line("")
        typewriter_line("  ▶️  To resume monitoring:", 0.03, '\033[96m')
        typewriter_line("  Delete the pause.flag file", 0.025, '\033[93m')
        typewriter_line("  OR use: service resume", 0.025, '\033[93m')
        typewriter_line("")
=======
                os.kill(pid, 0)
                return True
        except (OSError, ValueError):
            return False

    def stop_service(self):
        if not os.path.exists(self.pid_file):
            print("No PID file found. Service may not be running.")
            return
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            print(f"Sent termination signal to PID {pid}")
            time.sleep(2)
            if self.is_running(self.pid_file):
                print("Service did not stop gracefully, forcing...")
                os.kill(pid, signal.SIGKILL)
            self.remove_pid_file()
            print("Service stopped.")
        except Exception as e:
            print(f"Error stopping service: {e}")

    def status(self):
        if self.is_running(self.pid_file):
            print("DSTerminal service is running.")
        else:
            print("DSTerminal service is not running.")
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
