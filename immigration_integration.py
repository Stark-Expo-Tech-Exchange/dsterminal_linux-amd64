"""
DSTERMINAL - Complete Immigration System Protection Module
Active Protection + Real-Time Data Replication

DESIGN PHILOSOPHY:
- Integrate directly with the main immigration system
- Watch ALL passport activities in real-time
- Replicate EVERY data change as it happens
- Maintain a complete backup ready for restoration
- Auto-recover when the main system is breached

Author: DSTerminal AI Security Team
Version: 2.0.0
"""

import os
import sys
import json
import time
import hashlib
import threading
import queue
import sqlite3
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# DEPENDENCY CHECK
# ============================================================

def check_and_install_dependencies():
    """Check and install required dependencies"""
    dependencies = ['psutil']
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"[!] Installing missing dependencies: {', '.join(missing)}")
        for dep in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print("[✓] All dependencies installed!")

check_and_install_dependencies()

try:
    import psutil
except ImportError:
    psutil = None

# ============================================================
# CONSTANTS
# ============================================================

VERSION = "2.0.0"

class ReplicationStatus(Enum):
    SYNCED = "synced"
    PENDING = "pending"
    FAILED = "failed"
    RESTORED = "restored"

class ActivityType(Enum):
    PASSPORT_APPLICATION = "passport_application"
    PASSPORT_ISSUED = "passport_issued"
    PASSPORT_RENEWED = "passport_renewed"
    PASSPORT_CANCELLED = "passport_cancelled"
    BIO_DATA_UPDATED = "bio_data_updated"
    SYSTEM_LOGIN = "system_login"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    DATA_EXPORT = "data_export"
    UNKNOWN = "unknown"

# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class ImmigrationSystemConfig:
    """Complete configuration for immigration system integration"""
    
    # Main System Paths (use user directory for testing)
    system_path: str = str(Path.home() / "PassportSystem")
    database_path: str = str(Path.home() / "PassportSystem/Database/passport.db")
    config_path: str = str(Path.home() / "PassportSystem/Config")
    logs_path: str = str(Path.home() / "PassportSystem/Logs")
    biometrics_path: str = str(Path.home() / "PassportSystem/Biometrics")
    photos_path: str = str(Path.home() / "PassportSystem/Photos")
    
    # Backup Configuration (use user directory for testing)
    backup_path: str = str(Path.home() / "DSTerminal_Backup")
    backup_interval: int = 60  # seconds
    max_backups: int = 100
    
    # Replication Configuration
    replicate_biometrics: bool = True
    replicate_photos: bool = True
    replicate_database: bool = True
    
    # Monitoring Configuration
    monitor_interval: int = 5  # seconds
    watch_files: bool = True
    watch_processes: bool = True
    
    # Recovery Configuration
    auto_recovery: bool = True
    recovery_test_interval: int = 300  # seconds

# ============================================================
# COLOR CODES
# ============================================================

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    DIM = '\033[2m'

def cprint(text: str, color: str = Colors.GREEN, bold: bool = False):
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.RESET}")

def print_header(text: str):
    print("\n" + "="*80)
    cprint(f" {text} ".center(80), Colors.CYAN, True)
    print("="*80)

def print_section(text: str):
    cprint(f"\n► {text}", Colors.YELLOW, True)
    print("─"*60)

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class PassportRecord:
    passport_number: str
    full_name: str
    date_of_birth: str
    place_of_birth: str
    nationality: str
    gender: str
    id_number: str
    issue_date: str
    expiry_date: str
    passport_type: str
    status: str
    biometric_hash: str
    photo_hash: str
    signature_hash: str
    created_at: str
    updated_at: str
    last_activity: str
    activity_type: str

@dataclass
class SystemState:
    status: str = "healthy"
    last_check: str = ""
    total_passports: int = 0
    active_passports: int = 0
    pending_applications: int = 0
    system_uptime: str = "0h"
    backup_count: int = 0
    replication_status: str = "active"

# ============================================================
# MAIN PROTECTION ENGINE
# ============================================================

class ImmigrationProtectionEngine:
    """Main protection engine for Malawi Immigration System"""
    
    def __init__(self, config: ImmigrationSystemConfig = None):
        self.config = config or ImmigrationSystemConfig()
        self.running = False
        self.alerts = []
        self.backup_counter = 0
        
        # Queues
        self.activity_queue = queue.Queue()
        self.backup_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        
        # State tracking
        self.current_state = SystemState()
        self.file_hashes = {}
        self.process_hashes = {}
        
        # Database connections
        self.main_db = None
        self.backup_db = None
        self.recovery_db = None
        
        # Setup directories
        self._setup_directories()
        
        # Initialize connections
        self._initialize_connections()
    
    def _setup_directories(self):
        """Setup all required directories"""
        print_section("Setting up Protection Environment")
        
        # Use user's home directory for testing
        home = str(Path.home())
        
        # Replace D:/ with user's home for testing
        if self.config.backup_path.startswith("D:/"):
            self.config.backup_path = f"{home}/DSTerminal_Backup"
        
        # Main system paths
        paths = [
            self.config.system_path,
            self.config.database_path,
            self.config.logs_path,
            self.config.biometrics_path,
            self.config.photos_path,
            self.config.config_path
        ]
        
        for path in paths:
            if path:
                try:
                    if os.path.exists(path):
                        cprint(f"  ✓ Found: {path}", Colors.GREEN)
                    else:
                        os.makedirs(path, exist_ok=True)
                        cprint(f"  ✓ Created: {path}", Colors.CYAN)
                except Exception as e:
                    cprint(f"  ⚠️ Could not create {path}: {e}", Colors.YELLOW)
        
        # Backup paths
        backup_dirs = [
            self.config.backup_path,
            f"{self.config.backup_path}/database",
            f"{self.config.backup_path}/biometrics",
            f"{self.config.backup_path}/photos",
            f"{self.config.backup_path}/config",
            f"{self.config.backup_path}/recovery_points",
            f"{self.config.backup_path}/logs"
        ]
        
        for path in backup_dirs:
            try:
                os.makedirs(path, exist_ok=True)
                cprint(f"  ✓ Backup: {path}", Colors.DIM)
            except Exception as e:
                cprint(f"  ⚠️ Could not create {path}: {e}", Colors.YELLOW)
        
        cprint("  ✅ Directories ready", Colors.GREEN)
    
    def _initialize_connections(self):
        """Initialize database connections"""
        print_section("Initializing Connections")
        
        try:
            # Connect to main database
            db_dir = os.path.dirname(self.config.database_path)
            os.makedirs(db_dir, exist_ok=True)
            
            self.main_db = sqlite3.connect(self.config.database_path)
            self._create_main_database()
            cprint("  ✅ Main database ready", Colors.GREEN)
            
            # Create backup database
            backup_db_path = f"{self.config.backup_path}/database/backup.db"
            self.backup_db = sqlite3.connect(backup_db_path)
            self._create_backup_database()
            cprint("  ✅ Backup database ready", Colors.GREEN)
            
            # Create recovery database
            recovery_db_path = f"{self.config.backup_path}/recovery_points/recovery.db"
            self.recovery_db = sqlite3.connect(recovery_db_path)
            self._create_recovery_database()
            cprint("  ✅ Recovery database ready", Colors.GREEN)
            
        except Exception as e:
            cprint(f"  ❌ Connection error: {e}", Colors.RED)
            raise
    
    def _create_main_database(self):
        """Create main database structure"""
        cursor = self.main_db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passports (
                passport_number TEXT PRIMARY KEY,
                full_name TEXT,
                date_of_birth TEXT,
                nationality TEXT,
                issue_date TEXT,
                expiry_date TEXT,
                status TEXT,
                biometric_hash TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user TEXT,
                activity TEXT,
                passport_number TEXT,
                details TEXT
            )
        """)
        
        # Add sample data for testing
        cursor.execute("SELECT COUNT(*) FROM passports")
        if cursor.fetchone()[0] == 0:
            sample_data = [
                ('MW123456', 'John Doe', '1990-01-01', 'Malawian', '2024-01-01', '2034-01-01', 'active', 'hash123', datetime.now().isoformat(), datetime.now().isoformat()),
                ('MW123457', 'Jane Smith', '1992-05-15', 'Malawian', '2024-02-01', '2034-02-01', 'active', 'hash456', datetime.now().isoformat(), datetime.now().isoformat()),
                ('MW123458', 'David Banda', '1988-10-20', 'Malawian', '2024-03-01', '2034-03-01', 'pending', 'hash789', datetime.now().isoformat(), datetime.now().isoformat())
            ]
            cursor.executemany("""
                INSERT INTO passports (passport_number, full_name, date_of_birth, nationality, issue_date, expiry_date, status, biometric_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_data)
            self.main_db.commit()
            cprint("  ✓ Sample data added", Colors.DIM)
        
        self.main_db.commit()
    
    def _create_backup_database(self):
        """Create backup database structure"""
        cursor = self.backup_db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passports (
                passport_number TEXT PRIMARY KEY,
                full_name TEXT,
                date_of_birth TEXT,
                nationality TEXT,
                issue_date TEXT,
                expiry_date TEXT,
                status TEXT,
                biometric_hash TEXT,
                created_at TEXT,
                updated_at TEXT,
                backup_timestamp TEXT,
                backup_type TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_timestamp TEXT,
                backup_type TEXT,
                total_records INTEGER,
                status TEXT,
                description TEXT
            )
        """)
        self.backup_db.commit()
    
    def _create_recovery_database(self):
        """Create recovery point database"""
        cursor = self.recovery_db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                point_type TEXT,
                description TEXT,
                status TEXT,
                file_path TEXT
            )
        """)
        self.recovery_db.commit()
    
    # ============================================================
    # CORE FUNCTIONALITY
    # ============================================================
    
    def start_protection(self):
        """Start complete protection with real-time replication"""
        print_header("🛡️ DSTERMINAL - IMMIGRATION SYSTEM PROTECTION")
        cprint(f"Version: {VERSION}", Colors.DIM)
        cprint(f"Deployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.DIM)
        print()
        
        print("System: Malawi Immigration Passport System")
        print("="*80)
        
        cprint("  ✓ Active Monitoring: ENABLED", Colors.GREEN)
        cprint("  ✓ Real-Time Replication: ENABLED", Colors.GREEN)
        cprint("  ✓ Automated Backup: ENABLED", Colors.GREEN)
        cprint("  ✓ Quick Recovery: ENABLED", Colors.GREEN)
        print("="*80)
        
        self.running = True
        
        # Start all monitoring threads
        threads = [
            (self._monitor_database, "Database Monitor"),
            (self._monitor_file_system, "File System Monitor"),
            (self._process_activities, "Activity Processor"),
            (self._process_backups, "Backup Processor"),
            (self._process_alerts, "Alert Processor"),
            (self._monitor_replication, "Replication Monitor"),
            (self._health_check, "Health Check")
        ]
        
        if psutil:
            threads.append((self._monitor_processes, "Process Monitor"))
        
        print("\n🚀 Starting Protection Services...")
        for thread_func, name in threads:
            thread = threading.Thread(target=thread_func, daemon=True)
            thread.start()
            cprint(f"  ✓ {name} started", Colors.GREEN)
        
        print("\n" + "="*80)
        cprint("✅ ALL PROTECTION SERVICES ACTIVE", Colors.GREEN, True)
        print("="*80)
        
        print("\n📊 STATUS:")
        print(f"  System: {self.current_state.status}")
        print(f"  Replication: {self.current_state.replication_status}")
        print(f"  Backups: {self.backup_counter}")
        print("\n📋 Commands:")
        print("  status    - View system status")
        print("  alerts    - View alerts")
        print("  backup    - Create manual backup")
        print("  recover   - Test recovery")
        print("  replicate - Force replication")
        print("  stop      - Stop protection")
        print("  help      - Show help")
        print()
    
    # ============================================================
    # DATABASE MONITORING
    # ============================================================
    
    def _monitor_database(self):
        """Monitor database for changes and replicate"""
        while self.running:
            try:
                if not self.main_db or not self.backup_db:
                    time.sleep(5)
                    continue
                
                cursor = self.main_db.cursor()
                cursor.execute("""
                    SELECT passport_number, full_name, date_of_birth, nationality,
                           issue_date, expiry_date, status, biometric_hash,
                           created_at, updated_at
                    FROM passports
                    ORDER BY updated_at DESC
                """)
                records = cursor.fetchall()
                
                self.current_state.total_passports = len(records)
                self.current_state.active_passports = len([r for r in records if r[6] == 'active'])
                
                for record in records:
                    passport_number = record[0]
                    backup_cursor = self.backup_db.cursor()
                    backup_cursor.execute(
                        "SELECT updated_at FROM passports WHERE passport_number = ?",
                        (passport_number,)
                    )
                    backup_record = backup_cursor.fetchone()
                    
                    if not backup_record or backup_record[0] != record[9]:
                        self._replicate_record(record)
                        
                        activity = {
                            'timestamp': datetime.now().isoformat(),
                            'passport_number': passport_number,
                            'action': 'replicated' if backup_record else 'created',
                            'type': ActivityType.PASSPORT_APPLICATION.value
                        }
                        self.activity_queue.put(activity)
                
                self.current_state.last_check = datetime.now().isoformat()
                self._check_suspicious_activities()
                
                time.sleep(self.config.monitor_interval)
                
            except Exception as e:
                cprint(f"⚠️ Database monitoring error: {e}", Colors.YELLOW)
                time.sleep(10)
    
    def _replicate_record(self, record: Tuple):
        """Replicate a single record to backup"""
        try:
            cursor = self.backup_db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO passports (
                    passport_number, full_name, date_of_birth, nationality,
                    issue_date, expiry_date, status, biometric_hash,
                    created_at, updated_at, backup_timestamp, backup_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record[0], record[1], record[2], record[3],
                record[4], record[5], record[6], record[7],
                record[8], record[9],
                datetime.now().isoformat(),
                'full_replication'
            ))
            self.backup_db.commit()
            self.backup_counter += 1
            cprint(f"  ✓ Replicated: {record[0]}", Colors.DIM)
            
        except Exception as e:
            cprint(f"  ❌ Replication error for {record[0]}: {e}", Colors.RED)
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'REPLICATION_FAILED',
                'severity': 'CRITICAL',
                'message': f'Failed to replicate record: {record[0]}',
                'details': {'passport': record[0], 'error': str(e)}
            }
            self.alert_queue.put(alert)
    
    def _check_suspicious_activities(self):
        """Check for suspicious database activities"""
        try:
            cursor = self.main_db.cursor()
            
            # Check for rapid applications
            cursor.execute("""
                SELECT COUNT(*), user FROM audit_log 
                WHERE activity = 'passport_application'
                AND timestamp > datetime('now', '-1 hour')
                GROUP BY user
                HAVING COUNT(*) > 10
            """)
            
            suspicious = cursor.fetchall()
            for count, user in suspicious:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'EXCESSIVE_APPLICATIONS',
                    'severity': 'HIGH',
                    'message': f'User {user} submitted {count} applications in 1 hour',
                    'details': {'user': user, 'count': count}
                }
                self.alert_queue.put(alert)
                cprint(f"⚠️ Suspicious: {user} submitted {count} applications", Colors.YELLOW)
                
        except Exception as e:
            pass
    
    # ============================================================
    # FILE SYSTEM MONITORING
    # ============================================================
    
    def _monitor_file_system(self):
        """Monitor critical file system changes"""
        while self.running:
            try:
                paths_to_watch = [
                    (self.config.database_path, "database"),
                    (self.config.biometrics_path, "biometrics"),
                    (self.config.photos_path, "photos"),
                    (self.config.config_path, "config")
                ]
                
                for path, name in paths_to_watch:
                    if path and os.path.exists(path):
                        if os.path.isfile(path):
                            self._watch_file(path, name)
                        elif os.path.isdir(path):
                            self._watch_directory(path, name)
                
                time.sleep(10)
                
            except Exception as e:
                cprint(f"⚠️ File system monitoring error: {e}", Colors.YELLOW)
                time.sleep(10)
    
    def _watch_file(self, file_path: str, name: str):
        """Watch a single file for changes"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
            
            if file_path in self.file_hashes:
                if self.file_hashes[file_path] != file_hash:
                    self._backup_file(file_path, name)
                    cprint(f"  ✓ File backed up: {os.path.basename(file_path)}", Colors.CYAN)
            
            self.file_hashes[file_path] = file_hash
            
        except Exception as e:
            pass
    
    def _watch_directory(self, dir_path: str, name: str):
        """Watch a directory for changes"""
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files[:50]:  # Limit for performance
                    file_path = os.path.join(root, file)
                    self._watch_file(file_path, name)
        except Exception as e:
            pass
    
    def _backup_file(self, file_path: str, category: str):
        """Create a backup of a file"""
        try:
            backup_path = f"{self.config.backup_path}/{category}"
            os.makedirs(backup_path, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_file = f"{backup_path}/{timestamp}_{filename}"
            
            shutil.copy2(file_path, backup_file)
            
            cursor = self.recovery_db.cursor()
            cursor.execute("""
                INSERT INTO recovery_points (timestamp, point_type, description, status, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                category,
                f"Backup of {filename}",
                "active",
                backup_file
            ))
            self.recovery_db.commit()
            
        except Exception as e:
            cprint(f"  ❌ Backup error for {file_path}: {e}", Colors.RED)
    
    # ============================================================
    # PROCESS MONITORING
    # ============================================================
    
    def _monitor_processes(self):
        """Monitor critical system processes"""
        if not psutil:
            return
        
        critical_processes = [
            'passport_db.exe',
            'passport_app.exe',
            'biometric_server.exe',
            'print_service.exe'
        ]
        
        while self.running:
            try:
                running_processes = [p.name() for p in psutil.process_iter()]
                
                for proc in critical_processes:
                    if proc not in running_processes:
                        alert = {
                            'timestamp': datetime.now().isoformat(),
                            'type': 'PROCESS_STOPPED',
                            'severity': 'CRITICAL',
                            'message': f'Critical process stopped: {proc}',
                            'details': {'process': proc}
                        }
                        self.alert_queue.put(alert)
                        cprint(f"🚨 Critical process stopped: {proc}", Colors.RED)
                
                time.sleep(30)
                
            except Exception as e:
                time.sleep(30)
    
    # ============================================================
    # ACTIVITY PROCESSING
    # ============================================================
    
    def _process_activities(self):
        """Process all system activities"""
        while self.running:
            try:
                activity = self.activity_queue.get(timeout=1)
                self._log_activity(activity)
            except queue.Empty:
                continue
            except Exception as e:
                cprint(f"⚠️ Activity processing error: {e}", Colors.YELLOW)
    
    def _log_activity(self, activity: Dict):
        """Log activity to audit trail"""
        cursor = self.backup_db.cursor()
        cursor.execute("""
            INSERT INTO backup_metadata (backup_timestamp, backup_type, total_records, status, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            activity['timestamp'],
            'activity_log',
            1,
            'processed',
            f"{activity.get('action', 'unknown')} - {activity.get('passport_number', 'N/A')}"
        ))
        self.backup_db.commit()
    
    # ============================================================
    # BACKUP PROCESSING
    # ============================================================
    
    def _process_backups(self):
        """Process backup queue"""
        while self.running:
            try:
                self._create_full_backup()
                self._backup_database()
                self.current_state.backup_count = self.backup_counter
                time.sleep(self.config.backup_interval)
            except Exception as e:
                cprint(f"⚠️ Backup processing error: {e}", Colors.YELLOW)
                time.sleep(10)
    
    def _create_full_backup(self):
        """Create a complete system backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"full_backup_{timestamp}"
        backup_dir = f"{self.config.backup_path}/recovery_points/{backup_name}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            if os.path.exists(self.config.database_path):
                shutil.copy2(self.config.database_path, f"{backup_dir}/passport.db")
            
            if os.path.exists(self.config.config_path):
                shutil.copytree(self.config.config_path, f"{backup_dir}/config", dirs_exist_ok=True)
            
            metadata = {
                'backup_name': backup_name,
                'timestamp': timestamp,
                'type': 'full_backup',
                'status': 'completed',
                'records': self.current_state.total_passports,
            }
            
            with open(f"{backup_dir}/metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            cursor = self.recovery_db.cursor()
            cursor.execute("""
                INSERT INTO recovery_points (timestamp, point_type, description, status, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                'full_backup',
                f'Full system backup {backup_name}',
                'completed',
                backup_dir
            ))
            self.recovery_db.commit()
            
            cprint(f"  ✓ Full backup created: {backup_name}", Colors.GREEN)
            
        except Exception as e:
            cprint(f"  ❌ Full backup failed: {e}", Colors.RED)
    
    def _backup_database(self):
        """Create a database backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.config.backup_path}/database/backup_{timestamp}.db"
            
            if os.path.exists(self.config.database_path):
                shutil.copy2(self.config.database_path, backup_file)
                cprint(f"  ✓ Database backup: {os.path.basename(backup_file)}", Colors.DIM)
            
        except Exception as e:
            cprint(f"  ❌ Database backup error: {e}", Colors.RED)
    
    # ============================================================
    # REPLICATION MONITOR
    # ============================================================
    
    def _monitor_replication(self):
        """Monitor replication status"""
        while self.running:
            try:
                main_count = 0
                backup_count = 0
                
                if self.main_db:
                    cursor = self.main_db.cursor()
                    cursor.execute("SELECT COUNT(*) FROM passports")
                    main_count = cursor.fetchone()[0]
                
                if self.backup_db:
                    cursor = self.backup_db.cursor()
                    cursor.execute("SELECT COUNT(*) FROM passports")
                    backup_count = cursor.fetchone()[0]
                
                if main_count == backup_count:
                    self.current_state.replication_status = "synced"
                else:
                    self.current_state.replication_status = "out_of_sync"
                    cprint(f"⚠️ Replication out of sync: Main={main_count}, Backup={backup_count}", Colors.YELLOW)
                    self._resync_database()
                
                time.sleep(60)
                
            except Exception as e:
                cprint(f"⚠️ Replication monitoring error: {e}", Colors.YELLOW)
                time.sleep(60)
    
    def _resync_database(self):
        """Resync backup with main database"""
        cprint("🔄 Resyncing database...", Colors.CYAN)
        
        try:
            cursor = self.main_db.cursor()
            cursor.execute("SELECT * FROM passports")
            records = cursor.fetchall()
            
            backup_cursor = self.backup_db.cursor()
            backup_cursor.execute("DELETE FROM passports")
            
            for record in records:
                self._replicate_record(record)
            
            self.backup_db.commit()
            cprint("  ✅ Resync complete", Colors.GREEN)
            
        except Exception as e:
            cprint(f"  ❌ Resync failed: {e}", Colors.RED)
    
    # ============================================================
    # HEALTH CHECK
    # ============================================================
    
    def _health_check(self):
        """Perform regular health checks"""
        while self.running:
            try:
                is_healthy = self._check_system_health()
                
                if not is_healthy:
                    self.current_state.status = "breached"
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'SYSTEM_BREACH',
                        'severity': 'CRITICAL',
                        'message': 'System integrity compromised!',
                        'details': {'action': 'initiate_recovery'}
                    }
                    self.alert_queue.put(alert)
                    
                    if self.config.auto_recovery:
                        self._initiate_recovery()
                
                self.current_state.last_check = datetime.now().isoformat()
                time.sleep(self.config.recovery_test_interval)
                
            except Exception as e:
                cprint(f"⚠️ Health check error: {e}", Colors.YELLOW)
                time.sleep(60)
    
    def _check_system_health(self) -> bool:
        """Check system health status"""
        try:
            if self.main_db:
                cursor = self.main_db.cursor()
                cursor.execute("SELECT COUNT(*) FROM passports")
                count = cursor.fetchone()[0]
                
                if count == 0 and self.current_state.total_passports > 0:
                    return False
            
            if os.path.exists(self.config.database_path):
                if not self._verify_file_integrity(self.config.database_path):
                    return False
            
            return True
            
        except Exception as e:
            return False
    
    def _verify_file_integrity(self, file_path: str) -> bool:
        """Verify file integrity"""
        try:
            with open(file_path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            if file_path in self.file_hashes:
                return self.file_hashes[file_path] == current_hash
            
            self.file_hashes[file_path] = current_hash
            return True
            
        except Exception as e:
            return False
    
    # ============================================================
    # RECOVERY ENGINE
    # ============================================================
    
    def _initiate_recovery(self):
        """Initiate system recovery from backup"""
        print_section("🚨 INITIATING SYSTEM RECOVERY")
        cprint("System breach detected! Starting recovery...", Colors.RED, True)
        
        try:
            latest_recovery = self._get_latest_recovery_point()
            
            if not latest_recovery:
                cprint("  ❌ No recovery points found!", Colors.RED)
                return
            
            cprint(f"  ✓ Found recovery point: {latest_recovery['timestamp']}", Colors.GREEN)
            self._restore_database(latest_recovery)
            self._restore_files(latest_recovery)
            self._verify_restoration()
            
            self.current_state.status = "recovered"
            
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'RECOVERY_COMPLETE',
                'severity': 'HIGH',
                'message': 'System successfully recovered from backup',
                'details': {'recovery_point': latest_recovery['timestamp']}
            }
            self.alert_queue.put(alert)
            
            cprint("  ✅ Recovery complete!", Colors.GREEN, True)
            
        except Exception as e:
            cprint(f"  ❌ Recovery failed: {e}", Colors.RED)
    
    def _get_latest_recovery_point(self) -> Optional[Dict]:
        """Get the latest recovery point"""
        try:
            cursor = self.recovery_db.cursor()
            cursor.execute("""
                SELECT * FROM recovery_points 
                WHERE status = 'completed'
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'timestamp': row[1],
                    'type': row[2],
                    'description': row[3],
                    'status': row[4],
                    'file_path': row[5]
                }
            return None
            
        except Exception as e:
            return None
    
    def _restore_database(self, recovery_point: Dict):
        """Restore database from recovery point"""
        try:
            backup_db = f"{recovery_point['file_path']}/passport.db"
            
            if os.path.exists(backup_db):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                corrupted_backup = f"{self.config.backup_path}/corrupted_{timestamp}.db"
                shutil.copy2(self.config.database_path, corrupted_backup)
                shutil.copy2(backup_db, self.config.database_path)
                cprint("  ✓ Database restored", Colors.GREEN)
            else:
                cprint("  ⚠️ Database backup not found", Colors.YELLOW)
                
        except Exception as e:
            raise Exception(f"Database restore failed: {e}")
    
    def _restore_files(self, recovery_point: Dict):
        """Restore files from recovery point"""
        try:
            config_backup = f"{recovery_point['file_path']}/config"
            
            if os.path.exists(config_backup):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                corrupted_config = f"{self.config.backup_path}/corrupted_config_{timestamp}"
                shutil.copytree(self.config.config_path, corrupted_config, dirs_exist_ok=True)
                shutil.copytree(config_backup, self.config.config_path, dirs_exist_ok=True)
                cprint("  ✓ Config files restored", Colors.GREEN)
            else:
                cprint("  ⚠️ Config backup not found", Colors.YELLOW)
                
        except Exception as e:
            raise Exception(f"File restore failed: {e}")
    
    def _verify_restoration(self):
        """Verify the restoration was successful"""
        try:
            cursor = self.main_db.cursor()
            cursor.execute("SELECT COUNT(*) FROM passports")
            count = cursor.fetchone()[0]
            
            if count > 0:
                cprint(f"  ✓ Database verification: {count} records found", Colors.GREEN)
            else:
                cprint("  ⚠️ Database verification: No records found", Colors.YELLOW)
                
        except Exception as e:
            raise Exception(f"Verification failed: {e}")
    
    # ============================================================
    # ALERT PROCESSING
    # ============================================================
    
    def _process_alerts(self):
        """Process alerts from all sources"""
        while self.running:
            try:
                alert = self.alert_queue.get(timeout=1)
                self.alerts.append(alert)
                self._display_alert(alert)
            except queue.Empty:
                continue
            except Exception as e:
                cprint(f"⚠️ Alert processing error: {e}", Colors.YELLOW)
    
    def _display_alert(self, alert: Dict):
        """Display an alert"""
        severity = alert.get('severity', 'INFO')
        alert_type = alert.get('type', 'UNKNOWN')
        
        if severity == 'CRITICAL':
            color = Colors.RED
            emoji = '🚨'
        elif severity == 'HIGH':
            color = Colors.YELLOW
            emoji = '⚠️'
        elif severity == 'MEDIUM':
            color = Colors.CYAN
            emoji = '⚡'
        else:
            color = Colors.GREEN
            emoji = 'ℹ️'
        
        print(f"\n{color}{emoji} ALERT: {alert_type}{Colors.RESET}")
        print(f"  Severity: {severity}")
        print(f"  Time: {alert.get('timestamp', datetime.now().isoformat())}")
        print(f"  Message: {alert.get('message', 'No message')}")
        
        if alert.get('details'):
            print(f"  Details: {alert['details']}")
    
    # ============================================================
    # PUBLIC METHODS
    # ============================================================
    
    def get_status(self) -> Dict:
        """Get complete system status"""
        return {
            'system': {
                'status': self.current_state.status,
                'uptime': self.current_state.system_uptime,
                'last_check': self.current_state.last_check
            },
            'replication': {
                'status': self.current_state.replication_status,
                'total_passports': self.current_state.total_passports,
                'active_passports': self.current_state.active_passports,
                'pending_applications': self.current_state.pending_applications
            },
            'backup': {
                'count': self.current_state.backup_count,
                'last_backup': self.backup_counter,
                'location': self.config.backup_path
            },
            'alerts': {
                'total': len(self.alerts),
                'recent': self.alerts[-3:] if self.alerts else []
            },
            'config': {
                'system_path': self.config.system_path,
                'database_path': self.config.database_path,
                'backup_path': self.config.backup_path,
                'auto_recovery': self.config.auto_recovery
            }
        }
    
    def create_manual_backup(self):
        """Create a manual backup"""
        cprint("\n💾 Creating manual backup...", Colors.CYAN)
        self._create_full_backup()
        cprint("✅ Manual backup complete", Colors.GREEN)
    
    def test_recovery(self):
        """Test recovery process"""
        cprint("\n🧪 Testing recovery process...", Colors.CYAN)
        
        self._create_full_backup()
        cprint("  ✓ Backup created", Colors.GREEN)
        
        cprint("  Simulating data corruption...", Colors.YELLOW)
        if os.path.exists(self.config.database_path):
            temp_path = f"{self.config.database_path}.temp"
            shutil.move(self.config.database_path, temp_path)
            self._initiate_recovery()
            
            if not os.path.exists(self.config.database_path):
                shutil.move(temp_path, self.config.database_path)
                cprint("  ⚠️ Recovery test: Original restored", Colors.YELLOW)
            else:
                cprint("  ✅ Recovery test: Successful", Colors.GREEN)
                os.remove(temp_path)
    
    def force_replication(self):
        """Force full replication"""
        cprint("\n🔄 Forcing full replication...", Colors.CYAN)
        self._resync_database()
        cprint("✅ Replication complete", Colors.GREEN)
    
    def stop_protection(self):
        """Stop all protection services"""
        self.running = False
        
        if hasattr(self, 'main_db') and self.main_db:
            self.main_db.close()
        if hasattr(self, 'backup_db') and self.backup_db:
            self.backup_db.close()
        if hasattr(self, 'recovery_db') and self.recovery_db:
            self.recovery_db.close()
        
        cprint("\n🛑 Protection stopped", Colors.YELLOW)

# ============================================================
# CONFIGURATION MANAGER
# ============================================================

class ConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "immigration_config.json"
        
    def create_sample_config(self):
        """Create sample configuration file"""
        sample_config = {
            "system_path": str(Path.home() / "PassportSystem"),
            "database_path": str(Path.home() / "PassportSystem/Database/passport.db"),
            "config_path": str(Path.home() / "PassportSystem/Config"),
            "logs_path": str(Path.home() / "PassportSystem/Logs"),
            "biometrics_path": str(Path.home() / "PassportSystem/Biometrics"),
            "photos_path": str(Path.home() / "PassportSystem/Photos"),
            "backup_path": str(Path.home() / "DSTerminal_Backup"),
            "backup_interval": 60,
            "max_backups": 100,
            "replicate_biometrics": True,
            "replicate_photos": True,
            "replicate_database": True,
            "monitor_interval": 5,
            "watch_files": True,
            "watch_processes": True,
            "auto_recovery": True,
            "recovery_test_interval": 300
        }
        with open(self.config_path, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"✅ Sample config created: {self.config_path}")
    
    def load_config(self) -> ImmigrationSystemConfig:
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            print(f"⚠️ Config file not found: {self.config_path}")
            return ImmigrationSystemConfig()
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            return ImmigrationSystemConfig(**data)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return ImmigrationSystemConfig()

# ============================================================
# INTERACTIVE MODE
# ============================================================

def interactive_mode(protection: ImmigrationProtectionEngine):
    """Run interactive command mode"""
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == 'status':
                status = protection.get_status()
                print_header("SYSTEM STATUS")
                print(f"  System Status: {status['system']['status']}")
                print(f"  Replication: {status['replication']['status']}")
                print(f"  Total Passports: {status['replication']['total_passports']}")
                print(f"  Backups: {status['backup']['count']}")
                print(f"  Alerts: {status['alerts']['total']}")
                print(f"  Auto Recovery: {status['config']['auto_recovery']}")
                
            elif command == 'alerts':
                print_header("RECENT ALERTS")
                if protection.alerts:
                    for alert in protection.alerts[-10:]:
                        print(f"  [{alert['timestamp']}] {alert['severity']} - {alert['type']}")
                        print(f"    {alert['message']}")
                else:
                    print("  No alerts")
                    
            elif command == 'backup':
                protection.create_manual_backup()
                
            elif command == 'recover':
                protection.test_recovery()
                
            elif command == 'replicate':
                protection.force_replication()
                
            elif command == 'stop':
                protection.stop_protection()
                break
                
            elif command == 'help':
                print_header("AVAILABLE COMMANDS")
                print("  status    - Show system status")
                print("  alerts    - Show recent alerts")
                print("  backup    - Create manual backup")
                print("  recover   - Test recovery")
                print("  replicate - Force replication")
                print("  stop      - Stop protection")
                print("  help      - Show this help")
                
            elif command == '':
                continue
                
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Stopping...")
            protection.stop_protection()
            break

# ============================================================
# MAIN
# ============================================================

def main():
    """Main function"""
    print("\n" + "="*80)
    cprint("🇲🇼 DSTERMINAL - MALAWI IMMIGRATION SYSTEM PROTECTION", Colors.CYAN, True)
    print("="*80)
    
    # Load configuration
    config_path = "immigration_config.json"
    config_manager = ConfigManager(config_path)
    
    if not os.path.exists(config_path):
        response = input("\n⚠️ No config found. Create sample? (y/n): ").strip().lower()
        if response == 'y':
            config_manager.create_sample_config()
            print("\n⚠️ Please edit immigration_config.json with your system paths.")
            print("Then run the script again.")
            return
        else:
            print("Using default configuration...")
    
    config = config_manager.load_config()
    
    # Initialize protection
    protection = ImmigrationProtectionEngine(config)
    
    # Start protection
    protection.start_protection()
    
    # Enter interactive mode
    interactive_mode(protection)
    
    print("\n👋 Exiting...")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()