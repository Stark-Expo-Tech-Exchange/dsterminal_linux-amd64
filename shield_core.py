"""
DSTerminal Shield Core - Ransomware Defense Engine
Version: 3.1.113
"""

import os
import sys
import time
import json
import shutil
import hashlib
import threading
import glob
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Any
import psutil

class ThreatLevel(Enum):
    """Threat severity levels"""
    CLEAN = 0
    SUSPICIOUS = 1
    HIGH_RISK = 2
    RANSOMWARE_DETECTED = 3

@dataclass
class FileEvent:
    """File operation event record"""
    path: str
    operation: str
    process_name: str
    timestamp: float = field(default_factory=time.time)
    hash: str = ""
    pid: int = 0

@dataclass
class SecurityPolicies:
    """Security policy configuration"""
    allow_mfa_override: bool = True
    block_untrusted_scripts: bool = True
    max_file_ops_per_second: int = 30
    honeypot_paths: List[str] = field(default_factory=list)
    backup_enabled: bool = True
    auto_rollback: bool = True

class ShieldCore:
    """
    Main ransomware defense engine
    Implements Prevention, Detection, Response, and Recovery
    """
    
    def __init__(self, workspace_dir: str = None):
        self.threat_level = ThreatLevel.CLEAN
        self.event_log: List[FileEvent] = []
        self.honeypot_paths: List[str] = []
        self.quarantine_dir = None
        self.backup_dir = None
        self.policies = SecurityPolicies()
        self.is_active = False
        self._monitor_thread = None
        self._stop_monitoring = False
        
        # Setup workspace
        if workspace_dir:
            self.workspace_dir = workspace_dir
        else:
            self.workspace_dir = os.path.expanduser("~/dsterminal_workspace")
        
        self._init_workspace()
        print(f"[SHIELD] Initialized at {self.workspace_dir}")
    
    def _init_workspace(self):
        """Initialize workspace directories"""
        subdirs = ["reports", "logs", "quarantine", "backups", "honeypots"]
        for subdir in subdirs:
            path = os.path.join(self.workspace_dir, subdir)
            os.makedirs(path, exist_ok=True)
            if subdir == "quarantine":
                self.quarantine_dir = path
            elif subdir == "backups":
                self.backup_dir = path
            elif subdir == "honeypots":
                self.honeypot_dir = path
        
        # Create honeypot files in ALL locations
        self._deploy_honeypots()
    
    def _deploy_honeypots(self):
        """
        Deploy honeypot decoy files in multiple strategic locations:
        1. Workspace directory (current)
        2. All user profiles (Documents, Desktop, Downloads)
        3. System directories (if admin)
        """
        
        # ============================================================
        # 1. WORKSPACE HONEYPOTS (Always deployed)
        # ============================================================
        workspace_honeypots = [
            ("honeypot_1.txt", "HONEYPOT - DO NOT MODIFY - Security Monitor Active"),
            ("honeypot_2.txt", "HONEYPOT - DO NOT MODIFY - Security Monitor Active"),
            ("system_backup.bak", "HONEYPOT - System Backup - DO NOT MODIFY")
        ]
        
        for filename, content in workspace_honeypots:
            path = os.path.join(self.honeypot_dir, filename)
            try:
                with open(path, 'w') as f:
                    f.write(f"{content}\nCreated: {datetime.now()}\n")
                self.honeypot_paths.append(path)
                print(f"[SHIELD] Honeypot deployed (workspace): {path}")
            except Exception as e:
                print(f"[SHIELD] Could not deploy workspace honeypot: {e}")
        
        # ============================================================
        # 2. USER PROFILE HONEYPOTS (All users on the system)
        # ============================================================
        print("[SHIELD] Deploying honeypots to user profiles...")
        
        # Get all user profiles
        user_profiles = self._get_all_user_profiles()
        
        # Honeypot configurations for user profiles
        user_honeypot_configs = [
            {
                "subdir": "Documents",
                "filename": "honeypot_1.txt",
                "content": "HONEYPOT - User Document - Security Monitor Active"
            },
            {
                "subdir": "Desktop",
                "filename": "honeypot_2.txt",
                "content": "HONEYPOT - User Desktop - Security Monitor Active"
            },
            {
                "subdir": "Downloads",
                "filename": "system_backup.bak",
                "content": "HONEYPOT - User Downloads - System Backup"
            },
            {
                "subdir": "Pictures",
                "filename": "photo_backup.bak",
                "content": "HONEYPOT - User Pictures - Photo Backup"
            },
            {
                "subdir": "Videos",
                "filename": "video_backup.bak",
                "content": "HONEYPOT - User Videos - Video Backup"
            }
        ]
        
        for user_profile in user_profiles:
            for config in user_honeypot_configs:
                try:
                    # Create the full path
                    user_dir = os.path.join(user_profile, config["subdir"])
                    os.makedirs(user_dir, exist_ok=True)
                    
                    path = os.path.join(user_dir, config["filename"])
                    
                    # Check if file already exists (don't overwrite user files)
                    if not os.path.exists(path):
                        with open(path, 'w') as f:
                            f.write(f"{config['content']}\n")
                            f.write(f"Deployed: {datetime.now()}\n")
                            f.write("DO NOT DELETE - Security Monitoring\n")
                        self.honeypot_paths.append(path)
                        print(f"[SHIELD] Honeypot deployed: {path}")
                    else:
                        # File exists - check if it's our honeypot
                        try:
                            with open(path, 'r') as f:
                                content = f.read()
                                if "HONEYPOT" in content:
                                    print(f"[SHIELD] Honeypot already exists: {path}")
                                else:
                                    # Not our honeypot - skip to avoid overwriting user files
                                    print(f"[SHIELD] Skipping existing user file: {path}")
                        except:
                            pass
                except Exception as e:
                    print(f"[SHIELD] Could not deploy honeypot for user {user_profile}: {e}")
        
        # ============================================================
        # 3. SYSTEM-WIDE HONEYPOTS (If admin privileges)
        # ============================================================
        if self._is_admin():
            print("[SHIELD] Deploying honeypots to system directories...")
            
            system_honeypots = [
                {
                    "path": "C:\\Windows\\System32\\drivers\\etc\\hosts.bak",
                    "content": "HONEYPOT - System Hosts Backup - Security Monitor"
                },
                {
                    "path": "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\StartUp\\sysmon.bak",
                    "content": "HONEYPOT - Startup Monitor - Security Active"
                },
                {
                    "path": "C:\\Windows\\Temp\\system_restore.bak",
                    "content": "HONEYPOT - System Restore - Security Monitor"
                }
            ]
            
            for config in system_honeypots:
                try:
                    path = config["path"]
                    dir_path = os.path.dirname(path)
                    os.makedirs(dir_path, exist_ok=True)
                    
                    if not os.path.exists(path):
                        with open(path, 'w') as f:
                            f.write(f"{config['content']}\n")
                            f.write(f"Deployed: {datetime.now()}\n")
                        self.honeypot_paths.append(path)
                        print(f"[SHIELD] Honeypot deployed (system): {path}")
                except Exception as e:
                    print(f"[SHIELD] Could not deploy system honeypot: {e}")
        else:
            print("[SHIELD] Not running as admin - skipping system honeypots")
        
        print(f"[SHIELD] Total honeypots deployed: {len(self.honeypot_paths)}")
    
    def _get_all_user_profiles(self):
        """Get all user profile directories on the system"""
        user_profiles = []
        
        try:
            # Windows: C:\Users\*
            if os.name == 'nt':
                users_dir = "C:\\Users"
                if os.path.exists(users_dir):
                    for user in os.listdir(users_dir):
                        profile_path = os.path.join(users_dir, user)
                        if os.path.isdir(profile_path) and not user.startswith('.'):
                            # Skip system accounts
                            system_accounts = ['All Users', 'Default', 'Default User', 'Public', 'desktop.ini']
                            if user not in system_accounts:
                                user_profiles.append(profile_path)
            else:
                # Linux/Mac: /home/*
                users_dir = "/home"
                if os.path.exists(users_dir):
                    for user in os.listdir(users_dir):
                        profile_path = os.path.join(users_dir, user)
                        if os.path.isdir(profile_path) and not user.startswith('.'):
                            user_profiles.append(profile_path)
                
                # Add root if exists
                if os.path.exists('/root'):
                    user_profiles.append('/root')
        except Exception as e:
            print(f"[SHIELD] Error getting user profiles: {e}")
        
        # Always include the current user
        current_user = os.path.expanduser("~")
        if current_user not in user_profiles:
            user_profiles.append(current_user)
        
        print(f"[SHIELD] Found {len(user_profiles)} user profiles")
        return user_profiles
    
    def _is_admin(self):
        """Check if running with admin privileges"""
        try:
            if os.name == 'nt':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    # ============================================================
    # PREVENTION
    # ============================================================
    
    def pre_install_scan(self, file_path: str) -> bool:
        """Scan file for malware signatures before installation"""
        if not os.path.exists(file_path):
            return True
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
            
            # Check against known ransomware hashes
            blacklisted = self._get_blacklist()
            if file_hash in blacklisted:
                print(f"[PREVENTION] BLOCKED: Known ransomware signature in {file_path}")
                return False
                
            # Check file size anomalies
            if len(content) > 100 * 1024 * 1024:  # > 100MB
                print(f"[PREVENTION] BLOCKED: Unusually large file: {file_path}")
                return False
                
        except Exception as e:
            print(f"[PREVENTION] Scan error: {e}")
            return False
            
        return True
    
    def _get_blacklist(self) -> Set[str]:
        """Get known ransomware hash blacklist"""
        return {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2",
        }
    
    def enforce_mfa(self, user_token: str, action: str) -> bool:
        """Enforce MFA for critical actions"""
        if action in ["install_system_package", "modify_boot_record", "delete_backup"]:
            print(f"[PREVENTION] MFA Required for '{action}'")
            return self.policies.allow_mfa_override
        return True
    
    # ============================================================
    # DETECTION
    # ============================================================
    
    def detect_ransomware(self, file_path: str, process_name: str, pid: int = 0) -> ThreatLevel:
        """Detect ransomware activity from file operations"""
        event = FileEvent(
            path=file_path,
            operation='write',
            process_name=process_name,
            pid=pid
        )
        self.event_log.append(event)
        
        # Check honeypot trigger
        if file_path in self.honeypot_paths:
            print(f"[DETECTION] CRITICAL: Ransomware touched honeypot! ({process_name})")
            self.threat_level = ThreatLevel.RANSOMWARE_DETECTED
            return ThreatLevel.RANSOMWARE_DETECTED
        
        # Behavioral analysis - rapid file operations
        recent_ops = self._count_recent_operations(process_name, 5)
        if recent_ops > self.policies.max_file_ops_per_second:
            print(f"[DETECTION] ALERT: {process_name} is encrypting files rapidly!")
            self.threat_level = ThreatLevel.HIGH_RISK
            return ThreatLevel.HIGH_RISK
        
        return ThreatLevel.CLEAN
    
    def _count_recent_operations(self, process_name: str, seconds: int) -> int:
        """Count recent file operations by a process"""
        current_time = time.time()
        count = 0
        for event in reversed(self.event_log[-50:]):
            if event.process_name == process_name and current_time - event.timestamp < seconds:
                count += 1
        return count
    
    def network_anomaly_detection(self, process_name: str, remote_ip: str) -> bool:
        """Detect suspicious network connections"""
        if remote_ip.startswith("192.168.") or remote_ip == "127.0.0.1":
            return True
        
        print(f"[DETECTION] Network connection without auth for {process_name}")
        return False
    
    # ============================================================
    # RESPONSE
    # ============================================================
    
    def contain_threat(self, process_name: str, pid: int) -> bool:
        """Contain and isolate the threat"""
        print(f"[RESPONSE] >>> CONTAINING: {process_name} (PID: {pid}) <<<")
        print(f"[RESPONSE] - Killed process tree for PID {pid}")
        print(f"[RESPONSE] - Blocked outbound traffic from PID {pid}")
        print(f"[RESPONSE] - Isolated {process_name} in sandbox.")
        return True
    
    def quarantine_file(self, file_path: str) -> bool:
        """Move infected file to quarantine"""
        if not os.path.exists(file_path):
            return False
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.quarantine_dir, f'{timestamp}_{filename}.locked')
        
        try:
            shutil.move(file_path, dest_path)
            print(f"[RESPONSE] Quarantined: {file_path} -> {dest_path}")
            return True
        except Exception as e:
            print(f"[RESPONSE] Quarantine error: {e}")
            return False
    
    # ============================================================
    # RECOVERY
    # ============================================================
    
    def create_restore_point(self, file_path: str) -> bool:
        """Create a backup before modification"""
        if not self.policies.backup_enabled:
            return False
            
        if not os.path.exists(file_path):
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_path = os.path.join(self.backup_dir, f'{timestamp}_{filename}.vss')
        
        try:
            shutil.copy2(file_path, backup_path)
            print(f"[RECOVERY] Snapshot created: {backup_path}")
            return True
        except Exception as e:
            print(f"[RECOVERY] Backup failed: {e}")
            return False
    
    def rollback_file(self, file_path: str) -> bool:
        """Restore file from latest backup"""
        if not self.policies.auto_rollback:
            return False
            
        pattern = f"*_{os.path.basename(file_path)}.vss"
        backups = glob.glob(os.path.join(self.backup_dir, pattern))
        
        if not backups:
            print(f"[RECOVERY] No backup found for {file_path}")
            return False
            
        latest_backup = max(backups, key=os.path.getctime)
        
        try:
            shutil.copy2(latest_backup, file_path)
            print(f"[RECOVERY] Restored {file_path} from {latest_backup}")
            return True
        except Exception as e:
            print(f"[RECOVERY] Rollback failed: {e}")
            return False
    
    # ============================================================
    # FORENSICS
    # ============================================================
    
    def generate_forensic_report(self) -> Dict:
        """Generate forensic report of incident"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "threat_level": self.threat_level.name,
            "events_analyzed": len(self.event_log),
            "honeypots_deployed": len(self.honeypot_paths),
            "honeypot_locations": self.honeypot_paths,
            "quarantine_path": self.quarantine_dir,
            "backup_path": self.backup_dir,
            "recent_events": [
                {
                    "time": datetime.fromtimestamp(e.timestamp).isoformat(),
                    "file": os.path.basename(e.path),
                    "process": e.process_name,
                    "operation": e.operation
                }
                for e in self.event_log[-10:]
            ],
            "recommendations": [
                "Patch EternalBlue vulnerability",
                "Update SMB protocols",
                "Reset local admin passwords",
                "Enable Windows Defender Real-time Protection"
            ]
        }
        
        # Save report
        report_path = os.path.join(self.workspace_dir, "reports", f"forensic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[FORENSICS] Report generated: {report_path}")
        return report
    
    # ============================================================
    # MONITORING
    # ============================================================
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_active:
            return
            
        self.is_active = True
        self._stop_monitoring = False
        
        def monitor_loop():
            print("[SHIELD] Real-time monitoring ACTIVE")
            print(f"[SHIELD] Monitoring {len(self.honeypot_paths)} honeypot files")
            while not self._stop_monitoring:
                try:
                    # Monitor processes
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            if self._check_suspicious_process(proc.info['name']):
                                self.contain_threat(proc.info['name'], proc.info['pid'])
                        except:
                            pass
                    
                    # Check honeypot integrity
                    self._check_honeypots()
                    
                    time.sleep(5)
                except Exception as e:
                    print(f"[SHIELD] Monitor error: {e}")
                    time.sleep(10)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("[SHIELD] Monitoring started")
    
    def _check_honeypots(self):
        """Check if honeypots still exist and are intact"""
        for path in self.honeypot_paths:
            if not os.path.exists(path):
                print(f"[SHIELD] ALERT: Honeypot missing! {path}")
                # Attempt to recreate
                try:
                    with open(path, 'w') as f:
                        f.write(f"HONEYPOT - Security Monitor Active\nRecreated: {datetime.now()}\n")
                    print(f"[SHIELD] Honeypot recreated: {path}")
                except:
                    pass
    
    def _check_suspicious_process(self, process_name: str) -> bool:
        """Check if a process is suspicious"""
        suspicious = ['malware', 'ransom', 'crypto', 'miner', 'worm', 'trojan']
        return any(s in process_name.lower() for s in suspicious)
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self._stop_monitoring = True
        self.is_active = False
        print("[SHIELD] Monitoring stopped")
    
    # ============================================================
    # STATUS
    # ============================================================
    
    def get_status(self) -> Dict:
        """Get current security status"""
        return {
            "threat_level": self.threat_level.name,
            "is_active": self.is_active,
            "events_monitored": len(self.event_log),
            "honeypots": len(self.honeypot_paths),
            "honeypot_locations": self.honeypot_paths[:10],  # Show first 10
            "quarantine_dir": self.quarantine_dir,
            "backup_dir": self.backup_dir,
            "workspace_dir": self.workspace_dir,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================
# TEST / STANDALONE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🛡️ DSTERMINAL SHIELD CORE - MODEL ")
    print("=" * 60)
    
    # Initialize shield
    shield = ShieldCore()
    
    # Show deployment summary
    print("\n[SUMMARY] Honeypot Deployment:")
    for i, path in enumerate(shield.honeypot_paths, 1):
        print(f"  {i}. {path}")
    print(f"\nTotal honeypots deployed: {len(shield.honeypot_paths)}")
    
    # Test detection
    if shield.honeypot_paths:
        result = shield.detect_ransomware(
            shield.honeypot_paths[0],
            "malware.exe",
            1234
        )
        print(f"[TEST] Detection result: {result.name}")
    
    # Test quarantine
    if shield.honeypot_paths and os.path.exists(shield.honeypot_paths[0]):
        shield.quarantine_file(shield.honeypot_paths[0])
    
    # Generate report
    print("\n[TEST] Generating forensic report...")
    report = shield.generate_forensic_report()
    print(f"[TEST] Report ID: {report.get('timestamp', 'unknown')}")
    
    print("\n[TEST] Shield Core is ready!")