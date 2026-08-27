#!python
import sys
"""
DSTerminal - Deletion Protection Module
Import this into the main DSTerminal class.
Contains: BackupDatabase, EncryptionManager, DSTerminalMonitor, 
           RestoreManager, ServiceManager
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

# ============================================================
# 1. IMPORTS FIRST
# ============================================================

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
    WATCHDOG_AVAILABLE = False

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
            'hostname': platform.node(),
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


# ============================================================
# 4. DATABASE SYSTEM
# ============================================================

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


# ============================================================
# 5. ENCRYPTION SYSTEM
# ============================================================

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


# ============================================================
# 6. MONITOR HANDLER
# ============================================================

class DSTerminalMonitor(FileSystemEventHandler):
    def __init__(self, config: Dict[str, Any], workspace, interactive: bool = True, ui=None):
        self.config = config
        self.workspace = workspace
        self.interactive = interactive
        self.ui = ui
        self.db = BackupDatabase(workspace)
        self.encryption = EncryptionManager(workspace)
        self.platform_detector = PlatformDetector()
        self.stats = defaultdict(int)
        self.deletion_events = []
        self.honeypots = []
        self.protected_paths = set()
        self._setup_logging()
        if interactive:
            for path in config.get('monitor_paths', []):
                if os.path.exists(path):
                    try:
                        honeypots = self._create_honeypots(path)
                        self.honeypots.extend(honeypots)
                    except Exception as e:
                        self.logger.debug(f"Skipping honeypots in {path}: {e}")
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

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

    def _should_process_file(self, filepath: str) -> bool:
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
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif']:
            return 'images'
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages', '.md', '.tex']:
            return 'documents'
        elif ext in ['.xls', '.xlsx', '.csv', '.ods', '.numbers']:
            return 'spreadsheets'
        elif ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.ts', '.jsx', '.tsx', 
                    '.rb', '.php', '.html', '.css', '.scss', '.sass', '.less', '.json', '.yaml', '.yml',
                    '.xml', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd']:
            return 'code'
        elif ext in ['.json', '.yaml', '.yml', '.ini', '.conf', '.env', '.toml', '.cfg', '.properties']:
            return 'config'
        elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz', '.tgz', '.zst']:
            return 'archives'
        elif ext in ['.mp4', '.mp3', '.avi', '.mov', '.wav', '.flac', '.m4a', '.mpg', '.mpeg', '.webm',
                    '.mkv', '.wmv', '.flv', '.aac', '.ogg', '.wma']:
            return 'media'
        elif ext in ['.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.fdb']:
            return 'database'
        elif ext in ['.log', '.out', '.err']:
            return 'logs'
        else:
            return 'other'

    def _protect_file(self, filepath: str) -> bool:
        try:
            os.chmod(filepath, 0o444)
            protected_dir = self.workspace.get_path('backups_protected')
            os.makedirs(protected_dir, exist_ok=True)
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

    def _backup(self, path: str, trigger: str):
        if not os.path.exists(path): 
            return
        name = os.path.basename(path)
        if '_restored_' in name:
            return
        for attempt in range(3):
            try:
                time.sleep(0.2 * attempt)
                h = self._calculate_hash(path)
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
                    'original_path': path,
                    'backup_path': backup_path,
                    'filename': name,
                    'file_hash': h,
                    'file_size': os.path.getsize(path),
                    'category': cat,
                    'metadata': {'trigger': trigger}
                })
                self.stats['total_backups'] += 1
                self.stats['total_size'] += os.path.getsize(path)
                self.logger.info(f"Backup created: {name} ({os.path.getsize(path)/1024:.1f} KB)")
                break
            except PermissionError:
                if attempt == 2:
                    self.logger.debug(f"Skipping locked file: {name}")
                continue
            except Exception as e:
                self.logger.error(f"Backup failed for {name}: {e}")
                break

    def on_created(self, event):
        if event.is_directory: 
            return
        filepath = event.src_path
        if self._should_process_file(filepath): 
            self._backup(filepath, 'file_created')

    def on_deleted(self, event):
        if event.is_directory: 
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)
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
            if self.interactive and self.ui:
                self.ui.display_notification(
                    "DELETION DETECTED",
                    f"âœ“ {filename}\nBackup exists - can restore!",
                    "warning"
                )
            self.db.add_deletion_event(filepath, backup_dict['file_hash'], backup_dict['id'])
            self.logger.info(f"Deletion detected, backup exists: {filename}")
        else:
            if self.interactive and self.ui:
                self.ui.display_notification(
                    "DELETION DETECTED",
                    f"âš  {filename}\nNo backup available",
                    "error"
                )
            self.db.add_deletion_event(filepath, "NO_BACKUP")
            self.logger.warning(f"File deleted without backup: {filename}")

    def on_modified(self, event):
        if event.is_directory: 
            return
        filepath = event.src_path
        if self._should_process_file(filepath):
            self._backup(filepath, 'file_modified')

    def on_moved(self, event):
        if event.is_directory: 
            return
        if hasattr(event, 'dest_path') and self._is_trash_path(event.dest_path):
            self._backup(event.src_path, 'moved_to_trash')

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

    def cleanup(self):
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

    def signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)


# ============================================================
# 7. NEW FOLDER WATCHER
# ============================================================

class NewFolderWatcher(FileSystemEventHandler):
    def __init__(self, config, monitor_handler, observer, workspace):
        self.config = config
        self.monitor_handler = monitor_handler
        self.observer = observer
        self.workspace = workspace
        self.logger = logging.getLogger('FolderWatcher')
    
    def on_created(self, event):
        if not event.is_directory:
            return
        new_folder = event.src_path
        basename = os.path.basename(new_folder)
        if basename.startswith('.') or basename.startswith('$') or basename == '__pycache__':
            return
        workspace_path = os.path.normpath(self.workspace.base_path if hasattr(self.workspace, 'base_path') else str(self.workspace))
        if os.path.normpath(new_folder).startswith(workspace_path):
            return
        if new_folder not in self.config['monitor_paths']:
            self.config['monitor_paths'].append(new_folder)
            if self.observer and self.observer.is_alive():
                self.observer.schedule(
                    self.monitor_handler,
                    path=new_folder,
                    recursive=True
                )
            self.logger.info(f"New folder auto-monitored: {new_folder}")
            print(f"  âœ“ New folder detected & monitored: {new_folder}")


# ============================================================
# 8. RESTORE MANAGER
# ============================================================

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
            print(f"Backup ID {backup_id} not found.")
            return False
        try:
            backup_path = backup['backup_path']
            if not os.path.exists(backup_path):
                raise Exception(f"Backup file not found: {backup_path}")
            if backup.get('encryption_status', 'none') != 'none':
                backup_path = self.encryption.decrypt_file(backup_path)
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
            if os.path.exists(target_path) and not overwrite:
                base, ext = os.path.splitext(target_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = f"{base}_restored_{timestamp}{ext}"
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(backup_path, target_path)
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE backups
                SET restore_count = restore_count + 1, last_restored = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (backup_id,))
            self.db.conn.commit()
            os.chmod(target_path, 0o644)
            size_mb = backup['file_size'] / (1024 * 1024)
            print(f"âœ“ Restored: {backup['filename']} -> {target_path} ({size_mb:.2f} MB)")
            return True
        except Exception as e:
            print(f"âœ— Restore failed: {backup['filename']} - {str(e)}")
            return False

    def restore_last_deleted(self) -> bool:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM deletion_events WHERE backed_up = 1 ORDER BY detected_at DESC LIMIT 1')
        event = cursor.fetchone()
        if not event:
            print("No backed-up deletions found")
            return False
        return self.restore_file(event['backup_id'])


# ============================================================
# 9. SERVICE MANAGER
# ============================================================

class ServiceManager:
    def __init__(self, workspace, pid_file: str = None):
        self.workspace = workspace
        self.pid_file = pid_file or os.path.join(workspace.base_path, 'dsterminal.pid')
        self.logger = logging.getLogger('DSTerminal.service')

    def start_service(self, config: Dict[str, Any]) -> bool:
        """Start the deletion protection service with proper PID tracking"""
        import subprocess
        
        # Check if service is already running
        if self.is_running():
            print("[!] Service is already running.")
            return False
        
        try:
            python_exe = sys.executable
            script_path = os.path.join(os.path.dirname(__file__), 'deletion_protection.py')
            
            if platform.system() == 'Windows':
                cmd = f'start "DSTERMINAL MONITOR" "{python_exe}" "{script_path}" --daemon'
                subprocess.Popen(cmd, shell=True)
                time.sleep(2)
                
                # Find and update PID
                self._find_and_update_pid()
                print(f"âœ… Service started")
                return True
            else:
                terminals = ['xterm', 'gnome-terminal', 'konsole', 'terminator']
                for term in terminals:
                    if subprocess.run(['which', term], capture_output=True).returncode == 0:
                        subprocess.Popen([term, '-e', f'{python_exe} {script_path} --daemon'])
                        break
                else:
                    proc = subprocess.Popen([python_exe, script_path, '--daemon'])
                    with open(self.pid_file, 'w') as f:
                        f.write(str(proc.pid))
                
                time.sleep(2)
                if self.is_running():
                    print(f"âœ… Service started with PID: {self._read_pid()}")
                    return True
                else:
                    self._find_and_update_pid()
                    return self.is_running()
                
        except Exception as e:
            print(f"âŒ Failed to start service: {e}")
            return False
    
    def _find_and_update_pid(self):
        """Find the monitoring process and update PID file"""
        import subprocess
        
        try:
            if platform.system() == 'Windows':
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
                                print(f"âœ… Found and updated PID: {part}")
                                return True
            else:
                result = subprocess.run(
                    ['pgrep', '-f', 'deletion_protection.*--daemon'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if line.strip():
                        pid = int(line.strip())
                        with open(self.pid_file, 'w') as f:
                            f.write(str(pid))
                        print(f"âœ… Found and updated PID: {pid}")
                        return True
        except Exception as e:
            print(f"âš ï¸ Could not find process: {e}")
        
        return False

    def _read_pid(self) -> Optional[int]:
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return int(content)
        except Exception:
            pass
        return None

    def is_running(self) -> bool:
        if not os.path.exists(self.pid_file):
            return False
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            if PSUTIL_AVAILABLE:
                return psutil.pid_exists(pid)
            else:
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
        except (OSError, ValueError):
            return False

    def remove_pid_file(self):
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
        except OSError:
            pass

    def stop_service(self):
        """Stop the deletion protection service"""
        import subprocess
        
        print("[*] Stopping deletion protection service...")
        
        # Kill by PID from file
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if platform.system() == 'Windows':
                    subprocess.run(
                        ['taskkill', '/F', '/T', '/PID', str(pid)],
                        capture_output=True, timeout=5, check=False
                    )
                    print(f"âœ… Killed process: {pid}")
                else:
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                        time.sleep(1)
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                        print(f"âœ… Killed process group: {pid}")
                    except ProcessLookupError:
                        print("  Process already terminated")
                    except Exception as e:
                        print(f"âš ï¸ Could not kill process: {e}")
            except Exception as e:
                print(f"âš ï¸ Error reading PID file: {e}")
        
        # Kill by window title (Windows)
        if platform.system() == 'Windows':
            try:
                subprocess.run(
                    ['taskkill', '/F', '/FI', 'WINDOWTITLE eq DSTERMINAL MONITOR*'],
                    capture_output=True, timeout=5, check=False
                )
                print("âœ… Closed monitoring windows")
            except Exception:
                pass
        
        self.remove_pid_file()
        print("âœ… Deletion protection service stopped.")

    def status(self):
        """Check service status"""
        if self.is_running():
            pid = self._read_pid()
            print(f"ðŸŸ¢ SERVICE STATUS: RUNNING (PID: {pid})")
            print("â–¶ï¸  Monitoring: ACTIVE")
        else:
            print("ðŸ”´ SERVICE STATUS: INACTIVE")
            print("[i] To start: service-start")


# ============================================================
# 10. MAIN - RUNS WHEN EXECUTED DIRECTLY
# ============================================================

if __name__ == "__main__":
    import argparse
    import random
    
    parser = argparse.ArgumentParser(description='DSTerminal Deletion Protection')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    if args.daemon:
        try:
            workspace = SimpleWorkspace(os.path.expanduser('~/dsterminal_workspace'))
            
            # Get all paths to monitor
            platform_detector = PlatformDetector()
            monitor_paths = []
            
            if platform_detector.is_windows:
                import string
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        monitor_paths.append(drive)
            else:
                monitor_paths = ['/', '/home', '/usr', '/var', '/opt', '/etc', '/tmp']
                monitor_paths = [p for p in monitor_paths if os.path.exists(p)]
            
            # Add user directories
            home = os.path.expanduser('~')
            user_paths = [home, os.path.join(home, 'Desktop'), os.path.join(home, 'Downloads'),
                         os.path.join(home, 'Documents'), os.path.join(home, 'Pictures'),
                         os.path.join(home, 'Videos'), os.path.join(home, 'Music')]
            
            for path in user_paths:
                if os.path.exists(path) and path not in monitor_paths:
                    monitor_paths.append(path)
            
            monitor_paths = list(set([p for p in monitor_paths if os.path.exists(p)]))
            
            config = {
                'monitor_paths': monitor_paths,
                'exclude_patterns': ['*.tmp', '*.temp', '*~', '.DS_Store'],
                'max_file_size': 100 * 1024 * 1024
            }
            
            print(f"âœ… Monitoring {len(monitor_paths)} folders")
            print("ðŸŸ¢ Press Ctrl+C to stop\n")
            
            # Start monitoring
            monitor = DSTerminalMonitor(config, workspace, interactive=True)
            
            from watchdog.observers import Observer
            observer = Observer()
            
            for path in monitor_paths:
                if os.path.exists(path):
                    observer.schedule(monitor, path, recursive=True)
                    print(f"  âœ“ Monitoring: {path}")
            
            observer.start()
            
            # Write PID file
            pid_file = os.path.join(workspace.base_path, 'dsterminal.pid')
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n  ðŸ›‘ Shutting down...")
                observer.stop()
                observer.join()
                print("  âœ… Monitoring stopped.")
                if os.path.exists(pid_file):
                    os.remove(pid_file)
                sys.exit(0)
                
        except Exception as e:
            print(f"\nâŒ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    else:
        # Interactive mode - show module info
        print("=" * 70)
        print("ðŸ›¡ï¸  DSTERMINAL DELETION PROTECTION MODULE")
        print("=" * 70)
        print("")
        print("  ðŸš€ To run as a service:")
        print("  python deletion_protection.py --daemon")
        print("")
        print("  ðŸ“Œ Import this module into the main DSTerminal class:")
        print("  from deletion_protection import DSTerminalMonitor, BackupDatabase, RestoreManager, ServiceManager")
        print("")
        print("  ðŸ’¡ Available classes:")
        print("     - DSTerminalMonitor: Real-time file change monitoring")
        print("     - BackupDatabase: SQLite backup storage")
        print("     - RestoreManager: File restoration")
        print("     - ServiceManager: Service control")
        print("     - EncryptionManager: Fernet encryption")
        print("     - PlatformDetector: Cross-platform utilities")
        print("")
        print("=" * 70)