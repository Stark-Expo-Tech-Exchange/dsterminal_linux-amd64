# -*- coding: utf-8 -*-

"""
NETWORK SECURITY & REAL-TIME MONITORING SYSTEM
================================================

REAL DATA ONLY
--------------

This application monitors the actual local machine using psutil.

Features
--------
1. Real-time network bandwidth
2. Real-time TCP/UDP connections
3. Process monitoring
4. Browser connection monitoring
5. IDS detection
6. Reactive IPS/firewall blocking
7. SIEM event collection
8. SIEM correlation
9. Real-time alerts
10. IP block/unblock
11. Port block/unblock
12. Process termination
13. Custom threat IOC management
14. Reverse DNS
15. Public IP / geolocation
16. Threat map
17. Persistent JSON events
18. Browser dashboard
19. Server-Sent Events live updates
20. REST API

Run
---
    python network_security.py

Dashboard
---------
    http://127.0.0.1:5001
"""

from __future__ import annotations

import sys
import argparse
import collections
import datetime
import ipaddress
import json
import os
import platform
import queue
import shutil
import socket
import subprocess
import threading
import time
import webbrowser
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import psutil
import requests
from flask import (
    Flask,
    Response,
    jsonify,
    render_template_string,
    request,
)

# ============================================================
# FIX WINDOWS CONSOLE ENCODING - MUST BE FIRST
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass
    
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
    Back = type('Back', (), {'RESET': '\033[49m'})
except Exception as e:
    COLORS_AVAILABLE = False
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
# DSTERMINAL INTEGRATION
# ============================================================

import threading
import time
import webbrowser
from pathlib import Path

# Global state for dashboard integration
_SECURITY_DASHBOARD_RUNNING = False
_SECURITY_DASHBOARD_THREAD = None
_SECURITY_ENGINE = None

def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(clean_message)
    except Exception:
        try:
            print(str(message))
        except:
            pass


def start_security_dashboard(host="0.0.0.0", port=5001, open_browser=True):
    """Start the network security Flask dashboard"""
    global _SECURITY_DASHBOARD_RUNNING, _SECURITY_DASHBOARD_THREAD, _SECURITY_ENGINE
    
    if _SECURITY_DASHBOARD_RUNNING:
        return "[!] Network Security dashboard is already running"
    
    try:
        def run_dashboard():
            global _SECURITY_DASHBOARD_RUNNING, _SECURITY_ENGINE
            
            try:
                workspace = "~/network_security_workspace"
                _SECURITY_ENGINE = SecurityEngine(workspace)
                
                worker = threading.Thread(target=_SECURITY_ENGINE.run, daemon=True, name="security-monitor")
                worker.start()
                
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                except:
                    local_ip = "127.0.0.1"
                
                url = f"http://{host if host != '0.0.0.0' else local_ip}:{port}"
                
                safe_print_unicode("\n" + "=" * 60)
                safe_print_unicode("🛡️  NETWORK SECURITY DASHBOARD")
                safe_print_unicode("=" * 60)
                safe_print_unicode(f"📍 Dashboard URL: {url}")
                safe_print_unicode(f"📊 Real-time monitoring active")
                safe_print_unicode(f"🔄 Press Ctrl+C in this window to stop")
                safe_print_unicode("=" * 60 + "\n")
                
                if open_browser:
                    try:
                        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
                    except:
                        pass
                
                global ENGINE
                ENGINE = _SECURITY_ENGINE
                
                app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
                
            except Exception as e:
                safe_print_unicode(f"[!] Network Security dashboard error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                _SECURITY_DASHBOARD_RUNNING = False
                if _SECURITY_ENGINE:
                    _SECURITY_ENGINE.stop()
        
        _SECURITY_DASHBOARD_THREAD = threading.Thread(target=run_dashboard, daemon=True)
        _SECURITY_DASHBOARD_THREAD.start()
        _SECURITY_DASHBOARD_RUNNING = True
        
        time.sleep(2)
        return f"[+] Network Security dashboard started at http://127.0.0.1:{port}"
        
    except Exception as e:
        return f"[!] Failed to start Network Security dashboard: {e}"

def stop_security_dashboard(args=None):
    """Stop the network security dashboard"""
    global _SECURITY_DASHBOARD_RUNNING, _SECURITY_ENGINE
    
    if not _SECURITY_DASHBOARD_RUNNING:
        return "[!] Network Security dashboard is not running"
    
    _SECURITY_DASHBOARD_RUNNING = False
    if _SECURITY_ENGINE:
        _SECURITY_ENGINE.stop()
    return "[+] Network Security dashboard stop requested (server will terminate when thread ends)"

def security_dashboard_status(args=None):
    """Get network security dashboard status"""
    global _SECURITY_DASHBOARD_RUNNING
    
    if _SECURITY_DASHBOARD_RUNNING:
        return f"[+] Network Security dashboard is RUNNING at http://127.0.0.1:5001"
    return "[!] Network Security dashboard is NOT running"

def security_dashboard_browser(args=None):
    """Open network security dashboard in browser"""
    global _SECURITY_DASHBOARD_RUNNING
    
    if not _SECURITY_DASHBOARD_RUNNING:
        return "[!] Network Security dashboard is not running. Start it with 'sec-start'"
    
    try:
        webbrowser.open("http://127.0.0.1:5001")
        return "[+] Opened browser at http://127.0.0.1:5001"
    except Exception as e:
        return f"[!] Failed to open browser: {e}"

def security_dashboard_help(args=None):
    """Show network security dashboard commands help"""
    return """
╔═══════════════════════════════════════════════════════════════════╗
║         NETWORK SECURITY DASHBOARD COMMANDS                      ║
╠═══════════════════════════════════════════════════════════════════╣
║  sec-start       - Start the Network Security dashboard          ║
║  sec-stop        - Stop the Network Security dashboard           ║
║  sec-status      - Check Network Security dashboard status       ║
║  sec-browser     - Open Network Security in browser              ║
║  sec-help        - Show this help                                ║
╚═══════════════════════════════════════════════════════════════════╝
"""

# Command functions for DSTerminal
cmd_sec_start = start_security_dashboard
cmd_sec_stop = stop_security_dashboard
cmd_sec_status = security_dashboard_status
cmd_sec_browser = security_dashboard_browser
cmd_sec_help = security_dashboard_help

# Flag for availability
NETWORK_SECURITY_AVAILABLE = True

# ============================================================
# CONFIGURATION
# ============================================================

HOST = "0.0.0.0"
PORT = 5001

MAX_HISTORY = 500
EVENT_HISTORY = 1000
SCAN_INTERVAL = 5
CONNECTION_INTERVAL = 2

C2_PORTS = {
    4444,
    5555,
    1337,
    6666,
    6667,
    31337,
}

SUSPICIOUS_PROCESS_TERMS = {
    "crypt",
    "miner",
    "keylog",
    "backdoor",
    "trojan",
    "ransom",
    "rootkit",
    "meterpreter",
}

BROWSER_NAMES = {
    "chrome",
    "firefox",
    "msedge",
    "brave",
    "opera",
    "safari",
    "chromium",
    "vivaldi",
}

DEFAULT_THREAT_INTELLIGENCE = {
    "185.130.5.253": "C2 Server",
    "94.102.61.78": "Malware Distribution",
    "45.155.205.233": "Phishing Host",
}


# ============================================================
# HELPERS
# ============================================================

def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def utc_iso() -> str:
    return datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat(timespec="seconds")


def valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except Exception:
        return False


def valid_port(value: Any) -> bool:
    try:
        p = int(value)
        return 1 <= p <= 65535
    except Exception:
        return False


def trim(items: list, maximum: int = MAX_HISTORY):
    if len(items) > maximum:
        del items[:-maximum]


def safe_process_name(pid: Optional[int]) -> str:
    if not pid:
        return "Unknown"
    try:
        return psutil.Process(pid).name()
    except Exception:
        return "Unknown"


def is_public_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
        return not (
            ip.is_private
            or ip.is_loopback
            or ip.is_reserved
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_unspecified
        )
    except Exception:
        return False


def run_command(command: List[str], timeout: int = 10) -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except Exception as exc:
        return False, str(exc)


# ============================================================
# EVENT
# ============================================================

@dataclass
class SecurityEvent:
    timestamp: str
    source: str
    event_type: str
    severity: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PERSISTENT EVENT STORE
# ============================================================

class EventStore:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.events: List[Dict[str, Any]] = []
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.events = data[-EVENT_HISTORY:]
        except Exception:
            self.events = []

    def append(self, event: SecurityEvent):
        data = asdict(event)
        with self.lock:
            self.events.append(data)
            self.events = self.events[-EVENT_HISTORY:]
            try:
                with self.path.open("w", encoding="utf-8") as f:
                    json.dump(self.events, f, indent=2, default=str)
            except Exception:
                pass

    def recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.events[-limit:])


# ============================================================
# FIREWALL
# ============================================================

class Firewall:
    def __init__(self):
        self.lock = threading.Lock()
        self.blocked_ips: Set[str] = set()
        self.blocked_ports: Set[int] = set()
        self.rules: List[Dict[str, Any]] = []
        self._load_existing_rules()

    def block_ip(self, ip: str, reason: str = "Manual block") -> Dict[str, Any]:
        if not valid_ip(ip):
            return {"success": False, "message": "Invalid IP address."}
        with self.lock:
            if ip in self.blocked_ips:
                return {"success": False, "message": f"{ip} is already blocked."}
            success, message = self._system_block_ip(ip)
            if not success:
                return {"success": False, "message": message}
            self.blocked_ips.add(ip)
            rule = {"type": "IP", "value": ip, "action": "BLOCK", "reason": reason, "created": now_iso()}
            self.rules.append(rule)
            return {"success": True, "message": f"Blocked IP {ip}.", "rule": rule}

    def unblock_ip(self, ip: str) -> Dict[str, Any]:
        with self.lock:
            success, message = self._system_unblock_ip(ip)
            if not success:
                return {"success": False, "message": message}
            self.blocked_ips.discard(ip)
            self.rules = [r for r in self.rules if not (r["type"] == "IP" and r["value"] == ip)]
            return {"success": True, "message": f"Unblocked IP {ip}."}

    def block_port(self, port: int, reason: str = "Manual port block") -> Dict[str, Any]:
        if not valid_port(port):
            return {"success": False, "message": "Invalid port."}
        port = int(port)
        with self.lock:
            if port in self.blocked_ports:
                return {"success": False, "message": f"Port {port} is already blocked."}
            success, message = self._system_block_port(port)
            if not success:
                return {"success": False, "message": message}
            self.blocked_ports.add(port)
            rule = {"type": "PORT", "value": port, "action": "BLOCK", "reason": reason, "created": now_iso()}
            self.rules.append(rule)
            return {"success": True, "message": f"Blocked port {port}.", "rule": rule}

    def unblock_port(self, port: int) -> Dict[str, Any]:
        if not valid_port(port):
            return {"success": False, "message": "Invalid port."}
        port = int(port)
        with self.lock:
            success, message = self._system_unblock_port(port)
            if not success:
                return {"success": False, "message": message}
            self.blocked_ports.discard(port)
            self.rules = [r for r in self.rules if not (r["type"] == "PORT" and r["value"] == port)]
            return {"success": True, "message": f"Unblocked port {port}."}

    def is_blocked(self, remote_ip: str, remote_port: int) -> bool:
        return remote_ip in self.blocked_ips or remote_port in self.blocked_ports

    def _windows_add_rule(self, name: str, direction: str, remote_ip: Optional[str] = None, port: Optional[int] = None) -> Tuple[bool, str]:
        command = ["netsh", "advfirewall", "firewall", "add", "rule", f"name={name}", f"dir={direction}", "action=block", "profile=any"]
        if remote_ip:
            command.append(f"remoteip={remote_ip}")
        if port:
            command.extend(["protocol=TCP", f"remoteport={port}"])
        return run_command(command)

    def _windows_delete_rule(self, name: str) -> Tuple[bool, str]:
        return run_command(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={name}"])

    def _linux_add_ip(self, ip: str) -> Tuple[bool, str]:
        if shutil.which("nft"):
            ok, msg = run_command(["nft", "add", "rule", "inet", "filter", "input", "ip", "saddr", ip, "drop"])
            if ok:
                return True, msg
        if shutil.which("iptables"):
            ok, msg = run_command(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
            if ok:
                return True, msg
        return False, "No usable Linux firewall command or insufficient privileges."

    def _linux_delete_ip(self, ip: str) -> Tuple[bool, str]:
        if shutil.which("iptables"):
            ok, msg = run_command(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
            if ok:
                return True, msg
        return False, "Unable to remove Linux firewall rule."

    def _linux_add_port(self, port: int) -> Tuple[bool, str]:
        if shutil.which("iptables"):
            ok, msg = run_command(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "DROP"])
            if ok:
                return True, msg
        return False, "iptables unavailable or insufficient privileges."

    def _linux_delete_port(self, port: int) -> Tuple[bool, str]:
        if shutil.which("iptables"):
            ok, msg = run_command(["iptables", "-D", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "DROP"])
            if ok:
                return True, msg
        return False, "Unable to remove port rule."

    def _system_block_ip(self, ip: str) -> Tuple[bool, str]:
        system = platform.system()
        if system == "Windows":
            ok1, msg1 = self._windows_add_rule(f"NSRM_IN_IP_{ip}", "in", remote_ip=ip)
            ok2, msg2 = self._windows_add_rule(f"NSRM_OUT_IP_{ip}", "out", remote_ip=ip)
            if ok1 and ok2:
                return True, "Windows firewall rule added."
            return False, msg1 or msg2
        if system == "Linux":
            return self._linux_add_ip(ip)
        if system == "Darwin":
            return False, "Per-IP firewall control is not implemented for macOS in this version."
        return False, f"Unsupported OS: {system}"

    def _system_unblock_ip(self, ip: str) -> Tuple[bool, str]:
        system = platform.system()
        if system == "Windows":
            self._windows_delete_rule(f"NSRM_IN_IP_{ip}")
            self._windows_delete_rule(f"NSRM_OUT_IP_{ip}")
            return True, "Windows firewall rules removed."
        if system == "Linux":
            return self._linux_delete_ip(ip)
        return False, f"Unsupported OS: {system}"

    def _system_block_port(self, port: int) -> Tuple[bool, str]:
        system = platform.system()
        if system == "Windows":
            ok1, msg1 = self._windows_add_rule(f"NSRM_IN_PORT_{port}", "in", port=port)
            ok2, msg2 = self._windows_add_rule(f"NSRM_OUT_PORT_{port}", "out", port=port)
            if ok1 and ok2:
                return True, "Windows port rules added."
            return False, msg1 or msg2
        if system == "Linux":
            return self._linux_add_port(port)
        return False, f"Port blocking unsupported on {system}."

    def _system_unblock_port(self, port: int) -> Tuple[bool, str]:
        system = platform.system()
        if system == "Windows":
            self._windows_delete_rule(f"NSRM_IN_PORT_{port}")
            self._windows_delete_rule(f"NSRM_OUT_PORT_{port}")
            return True, "Windows port rules removed."
        if system == "Linux":
            return self._linux_delete_port(port)
        return False, f"Port unblocking unsupported on {system}."

    def _load_existing_rules(self):
        self.blocked_ips = set()
        self.blocked_ports = set()

    def stats(self) -> Dict[str, Any]:
        return {
            "blocked_ips": len(self.blocked_ips),
            "blocked_ports": len(self.blocked_ports),
            "rules": len(self.rules),
        }


# ============================================================
# THREAT INTELLIGENCE
# ============================================================

class ThreatIntelligence:
    def __init__(self):
        self.lock = threading.Lock()
        self.indicators = dict(DEFAULT_THREAT_INTELLIGENCE)

    def add(self, ip: str, description: str) -> bool:
        if not valid_ip(ip):
            return False
        with self.lock:
            self.indicators[ip] = description
        return True

    def remove(self, ip: str) -> bool:
        with self.lock:
            if ip not in self.indicators:
                return False
            del self.indicators[ip]
        return True

    def lookup(self, ip: str) -> Optional[str]:
        with self.lock:
            return self.indicators.get(ip)

    def all(self) -> Dict[str, str]:
        with self.lock:
            return dict(self.indicators)


# ============================================================
# IDS / IPS
# ============================================================

class IDSIPS:
    def __init__(self, threat_intelligence: ThreatIntelligence):
        self.threat_intelligence = threat_intelligence
        self.alerts: List[Dict[str, Any]] = []
        self.connection_history = collections.defaultdict(list)
        self.lock = threading.Lock()

    def analyze(self, connection: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        remote_ip = connection.get("remote_ip")
        remote_port = int(connection.get("remote_port", 0) or 0)
        process = str(connection.get("process", "")).lower()

        threat = self.threat_intelligence.lookup(remote_ip)
        if threat:
            return self._alert("KNOWN_THREAT", "CRITICAL", f"Connection to threat IOC: {threat}", connection)

        if remote_port in C2_PORTS:
            return self._alert("POSSIBLE_C2", "HIGH", f"Connection using suspicious C2 port {remote_port}", connection)

        for term in SUSPICIOUS_PROCESS_TERMS:
            if term in process:
                return self._alert("SUSPICIOUS_PROCESS", "HIGH", f"Suspicious process name: {process}", connection)

        local_ip = connection.get("local_ip")
        if local_ip and remote_port:
            now = time.time()
            with self.lock:
                history = self.connection_history[local_ip]
                history.append((now, remote_port))
                cutoff = now - 60
                self.connection_history[local_ip] = [item for item in history if item[0] >= cutoff]
                unique_ports = {port for _, port in self.connection_history[local_ip]}
                if len(unique_ports) >= 15:
                    return self._alert("PORT_SCAN", "MEDIUM", f"Possible port scan from {local_ip}", connection)
        return None

    def _alert(self, alert_type: str, severity: str, message: str, connection: Dict[str, Any]) -> Dict[str, Any]:
        alert = {"timestamp": now_iso(), "type": alert_type, "severity": severity, "message": message, "connection": dict(connection)}
        with self.lock:
            self.alerts.append(alert)
            trim(self.alerts, MAX_HISTORY)
        return alert

    def recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.alerts[-limit:])


# ============================================================
# SIEM
# ============================================================

class SIEM:
    def __init__(self, store: EventStore):
        self.store = store
        self.events: List[SecurityEvent] = []
        self.correlations = []
        self.lock = threading.Lock()

    def log(self, source: str, event_type: str, severity: str, message: str, data: Optional[Dict[str, Any]] = None) -> SecurityEvent:
        event = SecurityEvent(timestamp=now_iso(), source=source, event_type=event_type, severity=severity, message=message, data=data or {})
        with self.lock:
            self.events.append(event)
            trim(self.events, EVENT_HISTORY)
        self.store.append(event)
        self._correlate(event)
        return event

    def _correlate(self, event: SecurityEvent):
        if event.event_type == "failed_login":
            source_ip = event.data.get("source_ip")
            with self.lock:
                recent = [e for e in self.events[-50:] if e.event_type == "failed_login" and e.data.get("source_ip") == source_ip]
                if len(recent) >= 5:
                    self.correlations.append({"timestamp": now_iso(), "type": "BRUTE_FORCE", "severity": "HIGH", "message": f"Possible brute-force attack from {source_ip}"})
        if event.event_type == "connection_attempt":
            source_ip = event.data.get("source_ip")
            with self.lock:
                recent = [e for e in self.events[-100:] if e.event_type == "connection_attempt" and e.data.get("source_ip") == source_ip]
                ports = {e.data.get("port") for e in recent if e.data.get("port")}
                if len(ports) >= 10:
                    self.correlations.append({"timestamp": now_iso(), "type": "PORT_SCAN", "severity": "MEDIUM", "message": f"Possible port scan from {source_ip}"})
            trim(self.correlations, MAX_HISTORY)

    def recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self.lock:
            return [asdict(e) for e in self.events[-limit:]]

    def stats(self) -> Dict[str, Any]:
        with self.lock:
            counts = collections.Counter(e.severity for e in self.events)
            return {"total": len(self.events), "critical": counts["CRITICAL"], "high": counts["HIGH"], "medium": counts["MEDIUM"], "low": counts["LOW"], "correlations": len(self.correlations)}


# ============================================================
# NETWORK MONITOR
# ============================================================

class NetworkMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.prev_io = None
        self.prev_time = None
        self.upload_kbps = 0.0
        self.download_kbps = 0.0
        self.bandwidth_history = []
        self.connections = []
        self.protocol_stats = collections.Counter()
        self.last_update = None

    def update_bandwidth(self):
        current = psutil.net_io_counters()
        current_time = time.monotonic()
        with self.lock:
            if self.prev_io is not None and self.prev_time is not None:
                elapsed = current_time - self.prev_time
                if elapsed <= 0:
                    elapsed = 1
                sent = max(0, current.bytes_sent - self.prev_io.bytes_sent)
                recv = max(0, current.bytes_recv - self.prev_io.bytes_recv)
                self.upload_kbps = sent / 1024 / elapsed
                self.download_kbps = recv / 1024 / elapsed
                self.bandwidth_history.append({"timestamp": now_iso(), "upload_kbps": round(self.upload_kbps, 2), "download_kbps": round(self.download_kbps, 2)})
                trim(self.bandwidth_history)
            self.prev_io = current
            self.prev_time = current_time
            self.last_update = now_iso()

    def update_connections(self):
        result = []
        protocol_counts = collections.Counter()
        try:
            connections = psutil.net_connections(kind="inet")
        except Exception:
            connections = []
        for conn in connections:
            local_ip = conn.laddr.ip if conn.laddr else None
            local_port = conn.laddr.port if conn.laddr else None
            remote_ip = conn.raddr.ip if conn.raddr else None
            remote_port = conn.raddr.port if conn.raddr else None
            process = safe_process_name(conn.pid)
            item = {"pid": conn.pid, "process": process, "status": conn.status, "local_ip": local_ip, "local_port": local_port, "remote_ip": remote_ip, "remote_port": remote_port}
            result.append(item)
            if remote_port:
                protocol_counts[self.service_for_port(remote_port)] += 1
        with self.lock:
            self.connections = result
            self.protocol_stats = protocol_counts

    @staticmethod
    def service_for_port(port: int) -> str:
        services = {20: "FTP", 21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 465: "SMTPS", 587: "SMTP", 993: "IMAPS", 995: "POP3S", 3306: "MYSQL", 5432: "POSTGRES", 6379: "REDIS", 8080: "HTTP", 8443: "HTTPS"}
        return services.get(port, "OTHER")

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "upload_kbps": round(self.upload_kbps, 2),
                "download_kbps": round(self.download_kbps, 2),
                "connections": list(self.connections),
                "protocol_stats": dict(self.protocol_stats),
                "bandwidth_history": list(self.bandwidth_history[-60:]),
            }


# ============================================================
# ENDPOINT MONITOR
# ============================================================

class EndpointMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.processes = []
        self.suspicious = []
        self.last_scan = None

    def scan(self) -> List[Dict[str, Any]]:
        processes = []
        suspicious = []
        for proc in psutil.process_iter(["pid", "name", "username", "status", "cpu_percent", "memory_percent", "create_time"]):
            try:
                info = proc.info
                pid = info.get("pid")
                name = info.get("name") or "Unknown"
                item = {"pid": pid, "name": name, "username": info.get("username"), "status": info.get("status"), "cpu_percent": round(float(info.get("cpu_percent") or 0), 2), "memory_percent": round(float(info.get("memory_percent") or 0), 2)}
                processes.append(item)
                lower = name.lower()
                for term in SUSPICIOUS_PROCESS_TERMS:
                    if term in lower:
                        suspicious.append({**item, "reason": f"Process name contains '{term}'"})
                        break
                if item["memory_percent"] > 50:
                    suspicious.append({**item, "reason": "Very high memory usage"})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                continue
        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        with self.lock:
            self.processes = processes
            self.suspicious = suspicious
            self.last_scan = now_iso()
        return suspicious

    def terminate(self, pid: int) -> Tuple[bool, str]:
        try:
            process = psutil.Process(int(pid))
            name = process.name()
            process.terminate()
            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                process.kill()
            return True, f"Process {name} ({pid}) terminated."
        except psutil.NoSuchProcess:
            return False, "Process does not exist."
        except psutil.AccessDenied:
            return False, "Access denied."
        except Exception as exc:
            return False, str(exc)

    def snapshot(self):
        with self.lock:
            return {"processes": list(self.processes), "suspicious": list(self.suspicious), "last_scan": self.last_scan}


# ============================================================
# DNS / GEOLOCATION
# ============================================================

class NetworkIntelligence:
    def __init__(self):
        self.dns_cache = {}
        self.geo_cache = {}
        self.lock = threading.Lock()

    def reverse_dns(self, ip: str) -> str:
        if not valid_ip(ip):
            return ""
        with self.lock:
            if ip in self.dns_cache:
                return self.dns_cache[ip]
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = ""
        with self.lock:
            self.dns_cache[ip] = hostname
        return hostname

    def geolocate(self, ip: str) -> Dict[str, Any]:
        if not is_public_ip(ip):
            return {}
        with self.lock:
            if ip in self.geo_cache:
                return self.geo_cache[ip]
        try:
            response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=4)
            if not response.ok:
                return {}
            data = response.json()
            result = {"ip": ip, "city": data.get("city"), "region": data.get("region"), "country": data.get("country_name"), "latitude": data.get("latitude"), "longitude": data.get("longitude"), "org": data.get("org"), "asn": data.get("asn")}
            with self.lock:
                self.geo_cache[ip] = result
            return result
        except Exception:
            return {}


# ============================================================
# ALERT MANAGER
# ============================================================

class AlertManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.alerts = []
        self.sequence = 0

    def add(self, severity: str, title: str, message: str, source: str) -> Dict[str, Any]:
        severity = severity.upper()
        with self.lock:
            self.sequence += 1
            alert = {"id": self.sequence, "timestamp": now_iso(), "severity": severity, "title": title, "message": message, "source": source, "status": "ACTIVE"}
            self.alerts.append(alert)
            trim(self.alerts, MAX_HISTORY)
            return alert

    def acknowledge(self, alert_id: int) -> bool:
        with self.lock:
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert["status"] = "ACKNOWLEDGED"
                    return True
        return False

    def recent(self, limit: int = 100):
        with self.lock:
            return list(self.alerts[-limit:])

    def stats(self):
        with self.lock:
            counter = collections.Counter(a["severity"] for a in self.alerts)
            return {"total": len(self.alerts), "critical": counter["CRITICAL"], "high": counter["HIGH"], "medium": counter["MEDIUM"], "low": counter["LOW"], "active": sum(1 for a in self.alerts if a["status"] == "ACTIVE")}


# ============================================================
# NETWORK DEVICE DISCOVERY & MANAGEMENT WITH ARP SPOOFING
# ============================================================

import subprocess
import re
import ipaddress
import socket
import time
import threading
import platform
from typing import List, Dict, Optional
from scapy.all import ARP, Ether, srp, send, conf
import scapy.all as scapy


# ============================================================
# SUPPRESS SCAPY WARNINGS
# ============================================================

import warnings
import logging

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.getLogger("scapy").setLevel(logging.ERROR)
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

import scapy
scapy.config.conf.logLevel = 40

import sys
import io

class SuppressScapyWarnings:
    """Context manager to suppress Scapy warnings"""
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self._original_stderr

class NetworkDeviceManager:
    """Discover and manage devices on the local network with ARP spoofing"""
    
    def __init__(self):
        self.discovered_devices: List[Dict] = []
        self.blocked_devices: List[Dict] = []
        self.scan_lock = threading.Lock()
        self.blocking_threads = {}
        self.running = True
        self.gateway_ip = None
        self.gateway_mac = None
        self.my_ip = self._get_my_ip()
        self.my_mac = self._get_my_mac()
        self._load_blocked_devices()
        self._discover_gateway()

        import scapy
        scapy.config.conf.logLevel = 40
        scapy.config.conf.verb = 0
        
        self._restore_blocks()
        
    def _get_my_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_my_mac(self) -> str:
        try:
            import psutil
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        return addr.address
        except:
            pass
        
        try:
            import getmac
            return getmac.get_mac_address()
        except:
            return "00:00:00:00:00:00"
    
    def _discover_gateway(self):
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Default Gateway' in line:
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            self.gateway_ip = match.group(1)
                            arp_result = subprocess.run(['arp', '-a', self.gateway_ip], 
                                                       capture_output=True, text=True)
                            mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', arp_result.stdout)
                            if mac_match:
                                self.gateway_mac = mac_match.group(0).replace('-', ':')
                            break
            else:
                result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            self.gateway_ip = match.group(1)
                            arp_result = subprocess.run(['arp', '-n', self.gateway_ip], 
                                                       capture_output=True, text=True)
                            parts = arp_result.stdout.split()
                            if len(parts) >= 3:
                                self.gateway_mac = parts[2] if len(parts) > 2 else None
                            break
        except Exception as e:
            print(f"[!] Could not discover gateway: {e}")
        
        if not self.gateway_ip:
            ip_parts = self.my_ip.split('.')
            for i in range(1, 5):
                test_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{i}"
                if self._ping_host(test_ip):
                    self.gateway_ip = test_ip
                    break
    
    def _restore_blocks(self):
        for device in self.blocked_devices:
            ip = device.get('ip')
            mac = device.get('mac')
            if ip and ip != 'Unknown':
                print(f"[*] Restoring block for {ip}")
                self._start_arp_spoofing(ip, mac)
    
    def _arp_spoof(self, target_ip: str, target_mac: str, spoof_ip: str):
        try:
            packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, hwsrc="00:00:00:00:00:00")
            while self.running and target_ip in self.blocking_threads:
                send(packet, verbose=False)
                time.sleep(0.5)
        except Exception as e:
            print(f"[!] ARP spoof error for {target_ip}: {e}")
    
    def _start_arp_spoofing(self, target_ip: str, target_mac: Optional[str] = None):
        if target_ip in self.blocking_threads:
            return
        
        if not target_mac or target_mac == 'Unknown':
            target_mac = self._get_mac_from_ip(target_ip)
            if not target_mac:
                print(f"[!] Could not get MAC for {target_ip}")
                return
        
        if not self.gateway_ip:
            self._discover_gateway()
        
        if not self.gateway_ip:
            print("[!] Could not discover gateway")
            return
        
        thread = threading.Thread(
            target=self._arp_spoof,
            args=(target_ip, target_mac, self.gateway_ip),
            daemon=True
        )
        self.blocking_threads[target_ip] = thread
        thread.start()
        
        print(f"[+] ARP spoofing started for {target_ip} ({target_mac})")
        
        self._poison_gateway(target_ip, target_mac)
    
    def _poison_gateway(self, target_ip: str, target_mac: str):
        try:
            packet = ARP(op=2, pdst=self.gateway_ip, hwdst=self.gateway_mac, 
                        psrc=target_ip, hwsrc="00:00:00:00:00:00")
            send(packet, verbose=False)
        except Exception as e:
            print(f"[!] Gateway poison error: {e}")
    
    def _stop_arp_spoofing(self, target_ip: str):
        if target_ip in self.blocking_threads:
            del self.blocking_threads[target_ip]
            print(f"[+] ARP spoofing stopped for {target_ip}")
            self._restore_device_connectivity(target_ip)
    
    def _restore_device_connectivity(self, target_ip: str):
        try:
            target_mac = self._get_mac_from_ip(target_ip)
            if not target_mac:
                return
            
            restore_packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, 
                               psrc=self.gateway_ip, hwsrc=self.gateway_mac)
            send(restore_packet, verbose=False)
            
            gateway_packet = ARP(op=2, pdst=self.gateway_ip, hwdst=self.gateway_mac,
                               psrc=target_ip, hwsrc=target_mac)
            send(gateway_packet, verbose=False)
            
            print(f"[+] Connectivity restored for {target_ip}")
        except Exception as e:
            print(f"[!] Restoration error: {e}")
    
    def _get_mac_from_ip(self, ip: str) -> Optional[str]:
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request
            answered, _ = srp(packet, timeout=2, verbose=False)
            if answered:
                return answered[0][1].hwsrc
        except:
            pass
        
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
                match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', result.stdout)
                if match:
                    return match.group(0).replace('-', ':')
            else:
                result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
                parts = result.stdout.split()
                if len(parts) >= 3:
                    return parts[2]
        except:
            pass
        
        return None
    
    def _scan_with_nmap(self, network_cidr: str) -> List[Dict]:
        devices = []
        
        try:
            result = subprocess.run(['nmap', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return devices
            
            print("[*] Using SHIELD_CORE for device discovery...")
            
            result = subprocess.run(
                ['nmap', '-sn', network_cidr],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode != 0:
                return devices
            
            lines = result.stdout.split('\n')
            current_ip = None
            current_mac = None
            current_hostname = None
            my_ip = self._get_my_ip()
            
            for line in lines:
                line = line.strip()
                
                if 'Nmap scan report for' in line:
                    if current_ip and current_ip != my_ip:
                        if not current_mac:
                            current_mac = self._get_mac_from_arp(current_ip)
                        
                        hostname = current_hostname or 'Unknown'
                        try:
                            if not current_hostname:
                                hostname = socket.gethostbyaddr(current_ip)[0]
                        except:
                            pass
                        
                        devices.append({
                            'ip': current_ip,
                            'mac': current_mac or 'Unknown',
                            'hostname': hostname,
                            'vendor': self._get_vendor(current_mac) if current_mac else 'Unknown',
                            'status': 'active',
                            'is_self': current_ip == my_ip
                        })
                    
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        current_ip = ip_match.group(1)
                        current_mac = None
                        current_hostname = None
                
                elif 'MAC Address:' in line:
                    mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', line, re.IGNORECASE)
                    if mac_match:
                        current_mac = mac_match.group(0).replace('-', ':')
                
                elif '(' in line and ')' in line:
                    hostname_match = re.search(r'\(([^)]+)\)', line)
                    if hostname_match:
                        current_hostname = hostname_match.group(1)
            
            if current_ip and current_ip != my_ip:
                if not current_mac:
                    current_mac = self._get_mac_from_arp(current_ip)
                
                hostname = current_hostname or 'Unknown'
                try:
                    if not current_hostname:
                        hostname = socket.gethostbyaddr(current_ip)[0]
                except:
                    pass
                
                devices.append({
                    'ip': current_ip,
                    'mac': current_mac or 'Unknown',
                    'hostname': hostname,
                    'vendor': self._get_vendor(current_mac) if current_mac else 'Unknown',
                    'status': 'active',
                    'is_self': current_ip == my_ip
                })
            
            if my_ip not in [d['ip'] for d in devices]:
                my_mac = self._get_my_mac()
                devices.append({
                    'ip': my_ip,
                    'mac': my_mac,
                    'hostname': socket.gethostname(),
                    'vendor': self._get_vendor(my_mac),
                    'status': 'active',
                    'is_self': True
                })
            
            print(f"[+] SHIELD_CORE found {len(devices)} devices")
            
        except Exception as e:
            print(f"[!] NETWORK scan error: {e}")
        
        return devices

    def _get_mac_from_arp(self, ip: str) -> Optional[str]:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
                match = re.search(r'([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}', result.stdout, re.IGNORECASE)
                if match:
                    return match.group(0).replace('-', ':')
                else:
                    result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
                    parts = result.stdout.split()
                    if len(parts) >= 3:
                        return parts[2]
        except:
            pass
        return None

    def scan_network(self, network_cidr: Optional[str] = None) -> List[Dict]:
        if network_cidr is None:
            network_cidr = self.get_local_network()
        
        devices = []
        my_ip = self._get_my_ip()
        
        nmap_devices = self._scan_with_nmap(network_cidr)
        if nmap_devices:
            devices.extend(nmap_devices)
        
        if not devices or len(devices) < 3:
            arp_devices = self._get_arp_table()
            for device in arp_devices:
                if device['ip'] not in [d['ip'] for d in devices] and device['ip'] != '255.255.255.255':
                    if not device['ip'].startswith(('224.', '239.')):
                        devices.append(device)
        
        if not devices or len(devices) < 3:
            print("[*] Running ping sweep for more devices...")
            network = ipaddress.ip_network(network_cidr, strict=False)
            ip_parts = my_ip.split('.')
            base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            for i in range(1, 20):
                test_ip = f"{base}.{i}"
                if test_ip != my_ip and test_ip not in [d['ip'] for d in devices]:
                    if self._ping_host(test_ip):
                        mac = self._get_mac_from_arp(test_ip)
                        hostname = 'Unknown'
                        try:
                            hostname = socket.gethostbyaddr(test_ip)[0]
                        except:
                            pass
                        devices.append({
                            'ip': test_ip,
                            'mac': mac or 'Unknown',
                            'hostname': hostname,
                            'vendor': self._get_vendor(mac) if mac else 'Unknown',
                            'status': 'active',
                            'is_self': test_ip == my_ip
                        })
        
        if my_ip not in [d['ip'] for d in devices]:
            my_mac = self._get_my_mac()
            devices.append({
                'ip': my_ip,
                'mac': my_mac,
                'hostname': socket.gethostname(),
                'vendor': self._get_vendor(my_mac),
                'status': 'active',
                'is_self': True
            })
        
        with self.scan_lock:
            self.discovered_devices = devices
        
        return devices

    def _arp_spoof(self, target_ip: str, target_mac: str, spoof_ip: str):
        try:
            with SuppressScapyWarnings():
                packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, hwsrc="00:00:00:00:00:00")
                while self.running and target_ip in self.blocking_threads:
                    send(packet, verbose=False)
                    time.sleep(0.5)
        except Exception as e:
            print(f"[!] ARP spoof error for {target_ip}: {e}")
            
    def _get_arp_table(self) -> List[Dict]:
        devices = []
        
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]+)\s+(\w+)', line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2).replace('-', ':')
                        status = match.group(3)
                        if ip != "255.255.255.255":
                            hostname = 'Unknown'
                            try:
                                hostname = socket.gethostbyaddr(ip)[0]
                            except:
                                pass
                            devices.append({
                                'ip': ip,
                                'mac': mac,
                                'hostname': hostname,
                                'vendor': self._get_vendor(mac),
                                'status': status,
                                'is_self': ip == self.my_ip
                            })
            else:
                result = subprocess.run(['arp', '-n'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 3:
                        ip = parts[0]
                        mac = parts[2] if len(parts) > 2 else 'Unknown'
                        if mac != 'Unknown' and ip != '255.255.255.255':
                            hostname = 'Unknown'
                            try:
                                hostname = socket.gethostbyaddr(ip)[0]
                            except:
                                pass
                            devices.append({
                                'ip': ip,
                                'mac': mac,
                                'hostname': hostname,
                                'vendor': self._get_vendor(mac),
                                'status': 'dynamic',
                                'is_self': ip == self.my_ip
                            })
        except Exception as e:
            print(f"[!] Error reading ARP table: {e}")
        
        return devices
    
    def get_local_network(self) -> str:
        ip = self.my_ip
        ip_parts = ip.split('.')
        return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
    
    def _get_vendor(self, mac: str) -> str:
        vendors = {
            '00:0C:29': 'VMware',
            '00:50:56': 'VMware',
            '08:00:27': 'Oracle VirtualBox',
            'F0:18:98': 'Apple',
            'B4:6B:FC': 'Apple',
            '60:03:08': 'Apple',
            'A0:CC:2B': 'Samsung',
            '00:1A:11': 'Samsung',
            '00:22:68': 'Dell',
            '00:1D:09': 'Dell',
            '00:15:C5': 'HP',
            '00:17:A4': 'HP',
            '00:1B:78': 'HP',
            '00:15:00': 'Netgear',
            '00:1A:6B': 'Netgear',
            '00:18:4D': 'Cisco',
            '00:1A:2B': 'Cisco',
            '00:15:63': 'Linksys',
            '00:18:39': 'Linksys',
            '00:1A:7D': 'TP-Link',
            '00:1D:AA': 'TP-Link',
            '00:1B:11': 'D-Link',
            '00:1B:FE': 'D-Link',
            '00:0D:42': 'Roku',
            '00:1C:3B': 'Amazon',
            '00:1D:9B': 'Amazon',
            '00:0E:08': 'Intel',
            '00:1B:FC': 'Intel',
            '00:1C:C0': 'Intel',
            '00:1D:E0': 'Intel',
            '00:1A:6B': 'Broadcom',
            '00:1B:21': 'Broadcom',
            '00:1A:3E': 'Realtek',
            '00:1C:DF': 'Realtek',
            '00:1C:25': 'Qualcomm',
            '00:1D:CA': 'Qualcomm',
            '00:1A:2B': 'Huawei',
            '00:1C:0E': 'Huawei',
            '00:1A:80': 'Xiaomi',
            '00:24:AB': 'Xiaomi',
        }
        
        mac_upper = mac.upper()
        for prefix, vendor in vendors.items():
            if mac_upper.startswith(prefix):
                return vendor
        return 'Unknown'
    
    def _ping_host(self, ip: str) -> bool:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                      capture_output=True, text=True, timeout=2)
            else:
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                      capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def block_device(self, ip: str, mac: Optional[str] = None, reason: str = "Manual block", permanent: bool = True) -> Dict:
        result = {'success': False, 'message': '', 'device': None}
        
        if not mac or mac == 'Unknown':
            mac = self._get_mac_from_ip(ip)
        
        if not mac:
            result['message'] = f"Could not get MAC for {ip}"
            return result
        
        if ip in self.blocking_threads:
            result['message'] = f"Device {ip} is already blocked"
            result['success'] = True
            return result
        
        try:
            self._start_arp_spoofing(ip, mac)
            
            if permanent:
                blocked_device = {
                    'ip': ip,
                    'mac': mac,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'reason': reason,
                    'permanent': True
                }
                self.blocked_devices = [d for d in self.blocked_devices if d['ip'] != ip]
                self.blocked_devices.append(blocked_device)
                self._save_blocked_devices()
            
            if valid_ip(ip):
                self._system_block_ip(ip)
            
            result['success'] = True
            result['message'] = f"Device {ip} ({mac}) blocked via ARP spoofing"
            result['device'] = {'ip': ip, 'mac': mac}
            
        except Exception as e:
            result['message'] = f"Block failed: {str(e)}"
        
        return result
    
    def unblock_device(self, ip: str) -> Dict:
        result = {'success': False, 'message': ''}
        
        try:
            self._stop_arp_spoofing(ip)
            
            self.blocked_devices = [d for d in self.blocked_devices if d['ip'] != ip]
            self._save_blocked_devices()
            
            if valid_ip(ip):
                self._system_unblock_ip(ip)
            
            result['success'] = True
            result['message'] = f"Device {ip} unblocked"
            
        except Exception as e:
            result['message'] = f"Unblock failed: {str(e)}"
        
        return result
    
    def get_blocked_devices(self) -> List[Dict]:
        return self.blocked_devices
    
    def _system_block_ip(self, ip: str) -> Dict:
        try:
            if platform.system() == "Windows":
                rule_name = f"BLOCK_DEVICE_{ip.replace('.', '_')}"
                cmd = ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                       f'name={rule_name}', 'dir=in', 'action=block',
                       f'remoteip={ip}', 'profile=any']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    return {'success': True, 'message': f'Windows firewall rule added for {ip}'}
                else:
                    return {'success': False, 'message': result.stderr}
            else:
                return {'success': False, 'message': 'OS not supported for firewall blocking'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _system_unblock_ip(self, ip: str) -> Dict:
        try:
            if platform.system() == "Windows":
                rule_name = f"BLOCK_DEVICE_{ip.replace('.', '_')}"
                cmd = ['netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                       f'name={rule_name}']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    return {'success': True, 'message': f'Windows firewall rule removed for {ip}'}
                else:
                    return {'success': False, 'message': result.stderr}
            else:
                return {'success': False, 'message': 'OS not supported for firewall unblocking'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _save_blocked_devices(self):
        try:
            path = Path("~/network_security_workspace/blocked_devices.json").expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(self.blocked_devices, f, indent=2)
        except:
            pass
    
    def _load_blocked_devices(self):
        try:
            path = Path("~/network_security_workspace/blocked_devices.json").expanduser()
            if path.exists():
                with open(path, 'r') as f:
                    self.blocked_devices = json.load(f)
        except:
            self.blocked_devices = []

device_manager = NetworkDeviceManager()

# ============================================================
# MAIN SECURITY ENGINE
# ============================================================

class SecurityEngine:
    def __init__(self, workspace: str):
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.reports = self.workspace / "network_reports"
        self.maps = self.reports / "threat_maps"
        self.reports.mkdir(parents=True, exist_ok=True)
        self.maps.mkdir(parents=True, exist_ok=True)

        self.store = EventStore(self.reports / "siem_events.json")
        self.threats = ThreatIntelligence()
        self.firewall = Firewall()
        self.ids = IDSIPS(self.threats)
        self.siem = SIEM(self.store)
        self.network = NetworkMonitor()
        self.endpoint = EndpointMonitor()
        self.intelligence = NetworkIntelligence()
        self.alerts = AlertManager()

        self.running = True
        self.last_connection_scan = 0
        self.last_process_scan = 0
        self.alert_cache = set()
        self.clients = []
        self.client_lock = threading.Lock()

    def broadcast(self, payload: Dict[str, Any]):
        with self.client_lock:
            dead = []
            for client in self.clients:
                try:
                    client.put_nowait(payload)
                except Exception:
                    dead.append(client)
            for client in dead:
                if client in self.clients:
                    self.clients.remove(client)

    def broadcast_event(self, source: str, event_type: str, severity: str, message: str, data=None):
        event = {
            "type": "event",
            "data": {
                "timestamp": now_iso(),
                "source": source,
                "event_type": event_type,
                "severity": severity,
                "message": message,
                "data": data or {}
            }
        }
        self.broadcast(event)
        self.security_event(source, event_type, severity, message, data, alert=(severity in ["CRITICAL", "HIGH"]))

    def subscribe(self):
        q = queue.Queue(maxsize=50)
        with self.client_lock:
            self.clients.append(q)
        return q

    def unsubscribe(self, q):
        with self.client_lock:
            if q in self.clients:
                self.clients.remove(q)

    def security_event(self, source: str, event_type: str, severity: str, message: str, data=None, alert=False):
        event = self.siem.log(source, event_type, severity, message, data or {})
        if alert:
            security_alert = self.alerts.add(severity, event_type, message, source)
            self.broadcast({"type": "alert", "data": security_alert})
        self.broadcast({"type": "event", "data": asdict(event)})

    def analyze_connections(self):
        snapshot = self.network.snapshot()
        for connection in snapshot["connections"]:
            if connection["status"] != "ESTABLISHED":
                continue
            remote_ip = connection.get("remote_ip")
            if not remote_ip:
                continue
            detection = self.ids.analyze(connection)
            if detection:
                fingerprint = (detection["type"], remote_ip, connection.get("remote_port"), connection.get("pid"))
                if fingerprint not in self.alert_cache:
                    self.alert_cache.add(fingerprint)
                    self.security_event("IDS/IPS", detection["type"], detection["severity"], detection["message"], detection["connection"], alert=True)
                    if detection["severity"] in {"CRITICAL", "HIGH"}:
                        result = self.firewall.block_ip(remote_ip, f"Automatic IDS/IPS detection: {detection['type']}")
                        if result["success"]:
                            self.security_event("Firewall", "AUTO_BLOCK", "HIGH", result["message"], {"ip": remote_ip, "reason": detection["message"]}, alert=True)

    def process_scan(self):
        suspicious = self.endpoint.scan()
        for process in suspicious:
            key = ("PROCESS", process.get("pid"), process.get("reason"))
            if key in self.alert_cache:
                continue
            self.alert_cache.add(key)
            self.security_event("Endpoint", "SUSPICIOUS_PROCESS", "HIGH", f"{process['name']} (PID {process['pid']}): {process['reason']}", process, alert=True)

    def update(self):
        now = time.monotonic()
        self.network.update_bandwidth()
        if now - self.last_connection_scan >= CONNECTION_INTERVAL:
            self.network.update_connections()
            self.analyze_connections()
            self.last_connection_scan = now
        if now - self.last_process_scan >= SCAN_INTERVAL:
            self.process_scan()
            self.last_process_scan = now
        self.broadcast({"type": "snapshot", "data": self.dashboard_snapshot()})

    def dashboard_snapshot(self):
        network = self.network.snapshot()
        endpoint = self.endpoint.snapshot()
        alerts = self.alerts.stats()
        firewall = self.firewall.stats()
        siem = self.siem.stats()
        connections = []
        for connection in network["connections"]:
            item = dict(connection)
            remote = item.get("remote_ip")
            port = item.get("remote_port")
            item["blocked"] = self.firewall.is_blocked(remote, port or 0)
            item["dns"] = ""
            connections.append(item)
        return {
            "time": now_iso(),
            "host": socket.gethostname(),
            "platform": platform.platform(),
            "pid": os.getpid(),
            "network": {"upload_kbps": network["upload_kbps"], "download_kbps": network["download_kbps"], "connections": connections, "protocol_stats": network["protocol_stats"]},
            "endpoint": endpoint,
            "firewall": firewall,
            "ids": {"alerts": len(self.ids.recent())},
            "siem": siem,
            "alerts": alerts,
            "threat_intelligence": self.threats.all(),
            "recent_alerts": self.alerts.recent(30),
            "recent_events": self.siem.recent(30),
        }

    def browser_connections(self):
        browsers = []
        browser_pids = set()
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pid = proc.info["pid"]
                name = proc.info["name"] or ""
                lower = name.lower()
                if any(lower == browser or lower.startswith(browser + ".") or lower.startswith(browser + "-") for browser in BROWSER_NAMES):
                    browser_pids.add(pid)
                    browsers.append({"pid": pid, "name": name})
            except Exception:
                continue
        connections = []
        try:
            net = psutil.net_connections(kind="inet")
        except Exception:
            net = []
        for conn in net:
            if conn.pid not in browser_pids or conn.status != "ESTABLISHED" or not conn.raddr:
                continue
            remote_ip = conn.raddr.ip
            remote_port = conn.raddr.port
            connections.append({"pid": conn.pid, "process": safe_process_name(conn.pid), "remote_ip": remote_ip, "remote_port": remote_port, "service": NetworkMonitor.service_for_port(remote_port), "dns": self.intelligence.reverse_dns(remote_ip)})
        return {"browsers": browsers, "connections": connections, "count": len(connections)}

    def generate_threat_map(self):
        try:
            import folium
        except ImportError:
            return {"success": False, "message": "Install folium first."}
        snapshot = self.network.snapshot()
        remote_ips = set()
        for conn in snapshot["connections"]:
            remote = conn.get("remote_ip")
            if remote and is_public_ip(remote):
                remote_ips.add(remote)
        host_location = [-13.9833, 33.7833]
        try:
            response = requests.get("https://ipapi.co/json/", timeout=4)
            if response.ok:
                data = response.json()
                lat = data.get("latitude")
                lon = data.get("longitude")
                if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    host_location = [float(lat), float(lon)]
        except Exception:
            pass
        threat_map = folium.Map(location=host_location, zoom_start=3, tiles="CartoDB dark_matter")
        folium.Marker(host_location, popup=f"Security Host<br>{socket.gethostname()}", icon=folium.Icon(color="red", icon="home")).add_to(threat_map)
        for ip in list(remote_ips)[:50]:
            geo = self.intelligence.geolocate(ip)
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
                continue
            known = self.threats.lookup(ip)
            color = "red" if known else "green"
            popup = f"<b>{ip}</b><br>DNS: {self.intelligence.reverse_dns(ip)}<br>Location: {geo.get('city', '')}, {geo.get('country', '')}<br>Organization: {geo.get('org', '')}"
            folium.CircleMarker([float(lat), float(lon)], radius=7, color=color, fill=True, fill_color=color, fill_opacity=0.8, popup=popup).add_to(threat_map)
            folium.PolyLine([host_location, [float(lat), float(lon)]], color=color, weight=1, opacity=0.5).add_to(threat_map)
        filename = self.maps / (f"threat_map_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        threat_map.save(str(filename))
        return {"success": True, "file": str(filename), "url": "/maps/" + filename.name}

    def run(self):
        while self.running:
            try:
                self.update()
            except Exception as exc:
                self.security_event("System", "MONITOR_ERROR", "MEDIUM", str(exc), {}, alert=False)
            time.sleep(1)

    def stop(self):
        self.running = False


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)
ENGINE: Optional[SecurityEngine] = None

# ============================================================
# AUTHENTICATION - WITH CUSTOM LOGIN PAGE
# ============================================================

from functools import wraps
from flask import request, Response, jsonify, session, redirect, url_for
import secrets

AUTH_USERNAME = "admin"
AUTH_PASSWORD = "admin123"

app.secret_key = secrets.token_hex(16)

# Custom login page HTML - DARK BLUE WITH NEON GLOW
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Security - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: #0a0e1a;
            color: #8899bb;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 0;
            background: radial-gradient(ellipse at 20% 50%, rgba(0, 100, 200, 0.08) 0%, transparent 60%),
                        radial-gradient(ellipse at 80% 50%, rgba(0, 200, 255, 0.08) 0%, transparent 60%),
                        #0a0e1a;
        }
        
        .bg-animation::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 100, 200, 0.02) 2px, rgba(0, 100, 200, 0.02) 4px);
            animation: scanline 8s linear infinite;
            pointer-events: none;
        }
        
        @keyframes scanline {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
        }
        
        .matrix-rain {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
            opacity: 0.08;
        }
        
        .matrix-rain span {
            position: absolute;
            top: -100px;
            color: #00aaff;
            font-size: 14px;
            animation: rain linear infinite;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
        }
        
        @keyframes rain {
            0% { transform: translateY(0); opacity: 1; }
            100% { transform: translateY(110vh); opacity: 0; }
        }
        
        .login-container {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 440px;
            padding: 20px;
        }
        
        .login-box {
            background: #0d1520;
            border: 2px solid #004488;
            border-radius: 6px;
            padding: 35px 40px;
            box-shadow: 0 0 40px rgba(0, 100, 200, 0.15), 0 0 80px rgba(0, 100, 200, 0.05);
            position: relative;
            overflow: hidden;
            animation: neonGlow 4s ease-in-out infinite;
        }
        
        @keyframes neonGlow {
            0%, 100% { border-color: #004488; box-shadow: 0 0 40px rgba(0, 100, 200, 0.15); }
            25% { border-color: #0066cc; box-shadow: 0 0 60px rgba(0, 102, 204, 0.25); }
            50% { border-color: #0088ff; box-shadow: 0 0 80px rgba(0, 136, 255, 0.35); }
            75% { border-color: #0066cc; box-shadow: 0 0 60px rgba(0, 102, 204, 0.25); }
        }
        
        .login-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(transparent 50%, rgba(0, 100, 200, 0.02) 50%);
            background-size: 100% 4px;
            pointer-events: none;
            border-radius: inherit;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 25px;
        }
        
        .logo .icon {
            font-size: 40px;
            display: block;
            margin-bottom: 6px;
            opacity: 0.8;
            filter: drop-shadow(0 0 20px rgba(0, 136, 255, 0.3));
        }
        
        .logo h1 {
            color: #00aaff;
            font-size: 18px;
            letter-spacing: 3px;
            text-transform: uppercase;
            font-weight: normal;
            text-shadow: 0 0 20px rgba(0, 170, 255, 0.3);
        }
        
        .logo .subtitle {
            color: #445577;
            font-size: 11px;
            letter-spacing: 2px;
            margin-top: 4px;
        }
        
        .divider {
            border: none;
            border-top: 1px solid #004488;
            margin: 18px 0;
            box-shadow: 0 0 10px rgba(0, 100, 200, 0.2);
        }
        
        .status {
            text-align: center;
            font-size: 12px;
            margin-bottom: 18px;
            min-height: 22px;
            color: #667799;
            font-family: 'Courier New', monospace;
        }
        
        .status.error {
            color: #cc4455;
            text-shadow: 0 0 20px rgba(204, 68, 85, 0.3);
        }
        
        .status.success {
            color: #00cc88;
            text-shadow: 0 0 20px rgba(0, 204, 136, 0.3);
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        .form-group label {
            display: block;
            color: #445577;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input {
            width: 100%;
            padding: 10px 14px;
            background: #0a0f1a;
            border: 1px solid #004488;
            border-radius: 4px;
            color: #8899bb;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            transition: all 0.3s ease;
            outline: none;
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3);
        }
        
        .form-group input:focus {
            border-color: #00aaff;
            box-shadow: 0 0 30px rgba(0, 170, 255, 0.1), inset 0 0 20px rgba(0, 170, 255, 0.05);
        }
        
        .form-group input::placeholder {
            color: #334466;
        }
        
        .login-btn {
            width: 100%;
            padding: 12px;
            background: transparent;
            border: 2px solid #004488;
            border-radius: 4px;
            color: #00aaff;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 4px;
            animation: btnGlow 4s ease-in-out infinite;
            text-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
        }
        
        @keyframes btnGlow {
            0%, 100% { border-color: #004488; box-shadow: 0 0 20px rgba(0, 100, 200, 0.1); }
            50% { border-color: #0088ff; box-shadow: 0 0 40px rgba(0, 136, 255, 0.3); }
        }
        
        .login-btn:hover {
            background: #00aaff;
            color: #0a0e1a;
            box-shadow: 0 0 60px rgba(0, 170, 255, 0.2);
            border-color: #00aaff;
        }
        
        .login-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .footer {
            text-align: center;
            margin-top: 18px;
            color: #334466;
            font-size: 9px;
            letter-spacing: 1px;
        }
        
        .footer .blink {
            animation: blink 1.2s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.2; }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            20% { transform: translateX(-8px); }
            40% { transform: translateX(8px); }
            60% { transform: translateX(-8px); }
            80% { transform: translateX(8px); }
        }
        
        @media (max-width: 500px) {
            .login-box { padding: 25px 20px; }
            .logo h1 { font-size: 15px; }
            .form-group input { font-size: 12px; padding: 8px 12px; }
            .login-btn { font-size: 11px; padding: 10px; }
        }
    </style>
</head>
<body>

<div class="bg-animation"></div>

<div class="matrix-rain" id="matrixRain"></div>

<div class="login-container">
    <div class="login-box">
        <div class="logo">
            <span class="icon">🛡️</span>
            <h1>Network Security</h1>
            <div class="subtitle">REAL-TIME MONITORING SYSTEM</div>
        </div>
        
        <hr class="divider">
        
        <div class="status" id="status">◉ SECURE ACCESS REQUIRED</div>
        
        <form id="loginForm" autocomplete="off">
            <div class="form-group">
                <label>⏺ USERNAME</label>
                <input type="text" id="username" name="username" placeholder="Enter username" value="admin" autofocus>
            </div>
            
            <div class="form-group">
                <label>⏺ PASSWORD</label>
                <input type="password" id="password" name="password" placeholder="Enter password" value="admin123">
            </div>
            
            <button type="submit" class="login-btn" id="loginBtn">▶ ACCESS GRANTED</button>
        </form>
        
        <div class="footer">
            <span class="blink">●</span> SECURE CONNECTION <span class="blink">●</span>
            <br>
            v2.0 — Encrypted Channel Active
        </div>
    </div>
</div>

<script>
    (function() {
        const container = document.getElementById('matrixRain');
        if (!container) return;
        const chars = '01';
        const numDrops = 25;
        
        for (let i = 0; i < numDrops; i++) {
            const span = document.createElement('span');
            span.textContent = chars[Math.floor(Math.random() * chars.length)];
            span.style.left = Math.random() * 100 + '%';
            span.style.fontSize = (10 + Math.random() * 12) + 'px';
            span.style.animationDuration = (8 + Math.random() * 12) + 's';
            span.style.animationDelay = (Math.random() * 15) + 's';
            span.style.opacity = 0.05 + Math.random() * 0.2;
            span.style.textShadow = '0 0 10px rgba(0, 170, 255, 0.2)';
            container.appendChild(span);
        }
    })();

    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('loginForm');
        const usernameField = document.getElementById('username');
        const passwordField = document.getElementById('password');
        const status = document.getElementById('status');
        const loginBtn = document.getElementById('loginBtn');
        
        if (!form || !usernameField || !passwordField || !status || !loginBtn) {
            console.error('Login form elements not found');
            return;
        }
        
        usernameField.focus();
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = usernameField.value.trim();
            const password = passwordField.value.trim();
            
            if (!username || !password) {
                status.textContent = '❌ Please enter username and password';
                status.className = 'status error';
                return;
            }
            
            loginBtn.disabled = true;
            loginBtn.textContent = '⏳ AUTHENTICATING...';
            status.textContent = '⏳ Authenticating...';
            status.className = 'status';
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.message || 'Login failed');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    status.textContent = '✅ Access Granted! Redirecting...';
                    status.className = 'status success';
                    loginBtn.textContent = '✅ SUCCESS';
                    window.location.href = '/';
                } else {
                    throw new Error(data.message || 'Invalid credentials');
                }
            })
            .catch((error) => {
                status.textContent = '❌ ' + error.message;
                status.className = 'status error';
                loginBtn.textContent = '▶ ACCESS GRANTED';
                loginBtn.disabled = false;
                const box = document.querySelector('.login-box');
                if (box) {
                    box.style.animation = 'shake 0.5s ease';
                    setTimeout(() => {
                        box.style.animation = '';
                    }, 500);
                }
                passwordField.value = '';
                passwordField.focus();
            });
        });

        passwordField.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                form.dispatchEvent(new Event('submit'));
            }
        });
    });
</script>
</body>
</html>
"""

def check_auth(username, password):
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            return f(*args, **kwargs)
        auth = request.authorization
        if auth and check_auth(auth.username, auth.password):
            session['logged_in'] = True
            return f(*args, **kwargs)
        return redirect(url_for('login_page'))
    return decorated


@app.route("/login", methods=["GET"])
def login_page():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    return LOGIN_PAGE


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    if check_auth(username, password):
        session['logged_in'] = True
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ============================================================
# DASHBOARD HTML - DARK BLUE THEME WITH NEON GLOWING BORDERS
# ============================================================

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Network Security Real-Time SOC</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            background: #0a0e1a;
            color: #8899bb;
            font-family: 'Courier New', monospace;
        }
        
        /* Dark Blue Theme with Neon Glow */
        header {
            padding: 14px 20px;
            background: #0d1520;
            border-bottom: 2px solid #004488;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            position: relative;
            z-index: 100;
            animation: headerGlow 4s ease-in-out infinite;
            box-shadow: 0 0 40px rgba(0, 100, 200, 0.1);
        }
        
        @keyframes headerGlow {
            0%, 100% { border-bottom-color: #004488; box-shadow: 0 0 40px rgba(0, 100, 200, 0.1); }
            50% { border-bottom-color: #0088ff; box-shadow: 0 0 60px rgba(0, 136, 255, 0.2); }
        }
        
        .logo { 
            color: #00aaff; 
            font-size: 20px; 
            font-weight: bold; 
            letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(0, 170, 255, 0.3);
        }
        .live { color: #00aaff; text-shadow: 0 0 20px rgba(0, 170, 255, 0.3); }
        .container { padding: 15px; max-width: 100%; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }
        
        /* Card with Neon Glow Border */
        .card {
            background: #0d1520;
            border: 2px solid #004488;
            border-radius: 6px;
            padding: 14px;
            overflow: hidden;
            animation: borderGlow 4s ease-in-out infinite;
            box-shadow: 0 0 20px rgba(0, 100, 200, 0.05);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            box-shadow: 0 0 40px rgba(0, 100, 200, 0.15);
            transform: translateY(-2px);
        }
        
        @keyframes borderGlow {
            0%, 100% { border-color: #004488; box-shadow: 0 0 20px rgba(0, 100, 200, 0.05); }
            25% { border-color: #0066cc; box-shadow: 0 0 30px rgba(0, 102, 204, 0.1); }
            50% { border-color: #0088ff; box-shadow: 0 0 40px rgba(0, 136, 255, 0.15); }
            75% { border-color: #0066cc; box-shadow: 0 0 30px rgba(0, 102, 204, 0.1); }
        }
        
        /* Hacker Panel with Neon Glow */
        .hacker-panel {
            border: 2px solid #004488;
            position: relative;
            transition: all 0.3s ease;
            background: #0d1520;
            animation: panelGlow 5s ease-in-out infinite;
            box-shadow: 0 0 20px rgba(0, 100, 200, 0.05);
        }
        
        @keyframes panelGlow {
            0%, 100% { border-color: #004488; box-shadow: 0 0 20px rgba(0, 100, 200, 0.05); }
            33% { border-color: #0066cc; box-shadow: 0 0 40px rgba(0, 102, 204, 0.1); }
            66% { border-color: #0088ff; box-shadow: 0 0 60px rgba(0, 136, 255, 0.15); }
        }
        
        .hacker-panel:hover {
            border-color: #00aaff;
            box-shadow: 0 0 60px rgba(0, 170, 255, 0.2);
            transform: translateY(-2px);
        }
        
        .card h3 { margin-top: 0; color: #445577; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }
        .metric { font-size: 26px; color: #00aaff; margin: 6px 0; font-weight: normal; text-shadow: 0 0 20px rgba(0, 170, 255, 0.2); }
        .small { color: #445577; font-size: 11px; }
        .red { color: #cc4455; text-shadow: 0 0 20px rgba(204, 68, 85, 0.2); }
        .yellow { color: #ccaa44; text-shadow: 0 0 20px rgba(204, 170, 68, 0.2); }
        .blue { color: #4488cc; text-shadow: 0 0 20px rgba(68, 136, 204, 0.2); }
        .green { color: #00cc88; text-shadow: 0 0 20px rgba(0, 204, 136, 0.2); }
        .orange { color: #cc8844; text-shadow: 0 0 20px rgba(204, 136, 68, 0.2); }
        .white { color: #8899bb; }
        
        table { width: 100%; border-collapse: collapse; font-size: 11px; }
        th, td { padding: 6px; border-bottom: 1px solid #0a0f1a; text-align: left; }
        th { color: #445577; font-weight: normal; letter-spacing: 1px; text-transform: uppercase; font-size: 9px; border-bottom: 1px solid #004488; }
        .scroll { max-height: 360px; overflow: auto; }
        input, select, button {
            background: #0a0f1a;
            border: 1px solid #004488;
            color: #8899bb;
            padding: 7px 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            transition: all 0.3s ease;
        }
        input:focus {
            border-color: #00aaff;
            box-shadow: 0 0 30px rgba(0, 170, 255, 0.1);
            outline: none;
        }
        button { cursor: pointer; transition: all 0.3s ease; }
        button:hover { border-color: #00aaff; color: #00aaff; box-shadow: 0 0 30px rgba(0, 170, 255, 0.1); }
        .form { display: flex; flex-wrap: wrap; gap: 6px; }
        .alert {
            padding: 7px;
            margin-bottom: 4px;
            border-left: 3px solid;
            background: #0d1520;
        }
        .CRITICAL { border-color: #cc4455; }
        .HIGH { border-color: #cc8844; }
        .MEDIUM { border-color: #ccaa44; }
        .LOW { border-color: #00cc88; }
        pre { white-space: pre-wrap; word-wrap: break-word; color: #445577; }
        footer { color: #334466; padding: 15px; text-align: center; font-size: 10px; border-top: 1px solid #004488; margin-top: 10px; animation: footerGlow 4s ease-in-out infinite; }
        
        @keyframes footerGlow {
            0%, 100% { border-top-color: #004488; }
            50% { border-top-color: #0088ff; }
        }
        
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .map-feed-item {
            background: #0d1520;
            border-left: 2px solid #00aaff;
            padding: 3px 6px;
            margin-bottom: 2px;
            border-radius: 2px;
            font-size: 10px;
            animation: slideIn 0.3s ease;
        }
        .map-feed-item.critical { border-color: #cc4455; }
        .map-feed-item.high { border-color: #cc8844; }
        .map-feed-item.medium { border-color: #ccaa44; }
        .map-feed-item.low { border-color: #00cc88; }
        .map-feed-item .time { color: #445577; font-size: 8px; }
        .map-feed-item .type { font-weight: 600; color: #445577; }
        .map-feed-item .severity { font-weight: 600; font-size: 8px; text-transform: uppercase; }
        .map-feed-item .severity.critical { color: #cc4455; }
        .map-feed-item .severity.high { color: #cc8844; }
        .map-feed-item .message { color: #8899bb; margin-top: 2px; }
        .map-feed-item .ip { color: #4488cc; font-family: monospace; }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-8px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .map-tooltip {
            background: #0d1520 !important;
            border: 1px solid #004488 !important;
            color: #8899bb !important;
            font-family: monospace !important;
            font-size: 10px !important;
            padding: 4px 8px !important;
            border-radius: 3px !important;
            box-shadow: 0 0 20px rgba(0, 100, 200, 0.1) !important;
        }

        #threatMap { width: 100%; height: 100%; min-height: 200px; }
        #mapFeedList { max-height: 120px; overflow-y: auto; }
        #mapFeedList::-webkit-scrollbar { width: 3px; }
        #mapFeedList::-webkit-scrollbar-track { background: #0a0e1a; }
        #mapFeedList::-webkit-scrollbar-thumb { background: #004488; border-radius: 2px; }

        .hacker-btn {
            border: 1px solid #004488;
            background: #0d1520;
            color: #8899bb;
            font-size: 10px;
            letter-spacing: 0.5px;
            padding: 6px 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            animation: btnGlow 5s ease-in-out infinite;
        }
        
        @keyframes btnGlow {
            0%, 100% { border-color: #004488; }
            50% { border-color: #0088ff; box-shadow: 0 0 20px rgba(0, 136, 255, 0.1); }
        }
        
        .hacker-btn:hover {
            border-color: #00aaff;
            color: #00aaff;
            background: #0a0f1a;
            box-shadow: 0 0 30px rgba(0, 170, 255, 0.15);
        }
        .hacker-btn-danger { border-color: #663344; color: #cc4455; }
        .hacker-btn-danger:hover { border-color: #cc4455; color: #ff5566; box-shadow: 0 0 30px rgba(204, 68, 85, 0.15); }
        .hacker-btn-warning { border-color: #665533; color: #ccaa44; }
        .hacker-btn-warning:hover { border-color: #ccaa44; color: #ffcc55; box-shadow: 0 0 30px rgba(204, 170, 68, 0.15); }
        .hacker-btn-success { border-color: #336644; color: #00cc88; }
        .hacker-btn-success:hover { border-color: #00cc88; color: #00ff99; box-shadow: 0 0 30px rgba(0, 204, 136, 0.15); }
        .hacker-btn-blue { border-color: #334466; color: #4488cc; }
        .hacker-btn-blue:hover { border-color: #4488cc; color: #66aadd; box-shadow: 0 0 30px rgba(68, 136, 204, 0.15); }

        .hacker-input {
            background: #0a0f1a;
            border: 1px solid #004488;
            color: #8899bb;
            font-family: monospace;
            font-size: 11px;
            padding: 5px 8px;
            transition: all 0.3s ease;
        }
        .hacker-input:focus {
            outline: none;
            border-color: #00aaff;
            box-shadow: 0 0 30px rgba(0, 170, 255, 0.1);
        }
        
        .hacker-table th {
            background: #0d1520;
            border-bottom: 1px solid #004488;
            color: #445577;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 9px;
        }
        .hacker-table td { border-bottom: 1px solid #0a0f1a; }
        .hacker-table tr:hover td { background: #0a0f1a; }

        .hacker-scroll::-webkit-scrollbar { width: 4px; }
        .hacker-scroll::-webkit-scrollbar-track { background: #0a0e1a; }
        .hacker-scroll::-webkit-scrollbar-thumb { background: #004488; border-radius: 2px; }

        .hacker-header {
            border-bottom: 1px solid #004488;
            padding-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
            animation: headerBorderGlow 4s ease-in-out infinite;
        }
        
        @keyframes headerBorderGlow {
            0%, 100% { border-bottom-color: #004488; }
            50% { border-bottom-color: #0088ff; }
        }
        
        .hacker-header .badge {
            background: #004488;
            color: #8899bb;
            padding: 1px 8px;
            border-radius: 2px;
            font-size: 9px;
            animation: badgeGlow 4s ease-in-out infinite;
        }
        
        @keyframes badgeGlow {
            0%, 100% { background: #004488; box-shadow: 0 0 10px rgba(0, 100, 200, 0.1); }
            50% { background: #0088ff; box-shadow: 0 0 20px rgba(0, 136, 255, 0.2); }
        }
        
        .hacker-title {
            font-family: 'Courier New', monospace;
            color: #00aaff;
            font-size: 12px;
            font-weight: normal;
            letter-spacing: 1px;
            text-shadow: 0 0 20px rgba(0, 170, 255, 0.2);
        }
        .hacker-status {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 4px;
        }
        .hacker-status.online { background: #00cc88; box-shadow: 0 0 20px rgba(0, 204, 136, 0.3); }
        .hacker-status.offline { background: #cc4455; box-shadow: 0 0 20px rgba(204, 68, 85, 0.3); }
        .hacker-status.warning { background: #ccaa44; box-shadow: 0 0 20px rgba(204, 170, 68, 0.3); }

        .hacker-alert {
            border-left: 2px solid #00aaff;
            margin-bottom: 4px;
            padding: 6px 10px;
            background: #0d1520;
            border-radius: 2px;
            animation: alertGlow 4s ease-in-out infinite;
        }
        
        @keyframes alertGlow {
            0%, 100% { border-left-color: #00aaff; }
            50% { border-left-color: #0088ff; }
        }
        
        .hacker-alert.critical { border-left-color: #cc4455; }
        .hacker-alert.high { border-left-color: #cc8844; }
        .hacker-alert.medium { border-left-color: #ccaa44; }
        .hacker-alert.low { border-left-color: #00cc88; }

        .progress-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(10, 14, 26, 0.9);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            flex-direction: column;
        }
        .progress-overlay.active { display: flex; }
        .progress-container {
            background: #0d1520;
            border: 2px solid #004488;
            border-radius: 6px;
            padding: 30px 40px;
            min-width: 320px;
            max-width: 80%;
            text-align: center;
            animation: borderGlow 4s ease-in-out infinite;
            box-shadow: 0 0 60px rgba(0, 100, 200, 0.1);
        }
        .progress-title {
            color: #00aaff;
            font-size: 16px;
            margin-bottom: 16px;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 20px rgba(0, 170, 255, 0.2);
        }
        .progress-bar-wrapper {
            background: #0a0f1a;
            border: 1px solid #004488;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #004488, #0088ff, #00aaff);
            border-radius: 4px;
            transition: width 0.3s ease;
            width: 0%;
            box-shadow: 0 0 20px rgba(0, 136, 255, 0.2);
        }
        .progress-percent {
            color: #00aaff;
            font-size: 20px;
            margin-top: 8px;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 20px rgba(0, 170, 255, 0.2);
        }
        .progress-status {
            color: #445577;
            font-size: 12px;
            margin-top: 6px;
            font-family: monospace;
            min-height: 18px;
        }
        .progress-result {
            margin-top: 12px;
            padding: 10px;
            background: #0a0f1a;
            border-radius: 3px;
            border: 1px solid #004488;
            display: none;
            max-height: 150px;
            overflow-y: auto;
            text-align: left;
            font-family: monospace;
            font-size: 11px;
            color: #8899bb;
        }
        .progress-result.show { display: block; }
        .progress-result .item { padding: 3px 6px; border-bottom: 1px solid #0d1520; }
        .progress-result .item.highlight { color: #cc4455; }
        .progress-result .item.success { color: #00cc88; }

        .cache-status {
            font-size: 9px;
            color: #445577;
            font-family: monospace;
            margin-left: 8px;
        }
        .cache-status.cached { color: #00cc88; }
        .cache-status.fresh { color: #4488cc; }
        .cache-status.stale { color: #ccaa44; }

        .warning-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        .warning-overlay.active { display: flex; }

        .warning-box {
            background: #0d1520;
            border: 2px solid #cc4455;
            border-radius: 6px;
            padding: 30px 40px;
            max-width: 500px;
            width: 90%;
            position: relative;
            animation: warningGlow 2s ease-in-out infinite;
            box-shadow: 0 0 60px rgba(204, 68, 85, 0.15);
        }
        
        @keyframes warningGlow {
            0%, 100% { border-color: #cc4455; box-shadow: 0 0 60px rgba(204, 68, 85, 0.15); }
            50% { border-color: #ff6677; box-shadow: 0 0 80px rgba(204, 68, 85, 0.3); }
        }
        
        .warning-icon { font-size: 40px; text-align: center; display: block; margin-bottom: 10px; }
        .warning-title { color: #cc4455; font-family: 'Courier New', monospace; font-size: 18px; text-align: center; margin-bottom: 12px; text-shadow: 0 0 20px rgba(204, 68, 85, 0.3); }
        .warning-text { color: #8899bb; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.6; }
        .warning-text .highlight { color: #cc4455; }
        .warning-text .bullet { color: #ccaa44; padding-right: 6px; }
        .warning-text .info { color: #00cc88; }
        .warning-divider { border: none; border-top: 1px solid #004488; margin: 12px 0; }
        .warning-buttons { display: flex; gap: 10px; justify-content: center; margin-top: 15px; }
        .warning-btn {
            padding: 10px 30px;
            border: 2px solid;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .warning-btn-proceed { 
            background: transparent; 
            border-color: #cc4455; 
            color: #cc4455;
            animation: btnWarning 2s ease-in-out infinite;
        }
        
        @keyframes btnWarning {
            0%, 100% { border-color: #cc4455; box-shadow: 0 0 20px rgba(204, 68, 85, 0.1); }
            50% { border-color: #ff6677; box-shadow: 0 0 40px rgba(204, 68, 85, 0.3); }
        }
        
        .warning-btn-proceed:hover { background: #cc4455; color: #0a0e1a; box-shadow: 0 0 60px rgba(204, 68, 85, 0.3); }
        .warning-btn-cancel { background: transparent; border-color: #445577; color: #445577; }
        .warning-btn-cancel:hover { background: #445577; color: #0a0e1a; }

        .blocking-progress-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10001;
        }
        .blocking-progress-overlay.active { display: flex; }
        .blocking-progress-box {
            background: #0d1520;
            border: 2px solid #004488;
            border-radius: 6px;
            padding: 30px 40px;
            max-width: 400px;
            width: 90%;
            text-align: center;
            animation: borderGlow 4s ease-in-out infinite;
            box-shadow: 0 0 40px rgba(0, 100, 200, 0.1);
        }
        .blocking-progress-icon { font-size: 40px; margin-bottom: 10px; }
        .blocking-progress-title { color: #00aaff; font-family: 'Courier New', monospace; font-size: 16px; margin-bottom: 8px; text-shadow: 0 0 20px rgba(0, 170, 255, 0.2); }
        .blocking-progress-text { color: #445577; font-family: 'Courier New', monospace; font-size: 12px; margin-bottom: 12px; min-height: 18px; }
        .blocking-progress-bar-wrapper {
            background: #0a0f1a;
            border: 1px solid #004488;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
        }
        .blocking-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #004488, #0088ff, #00aaff);
            border-radius: 4px;
            transition: width 0.5s ease;
            width: 0%;
            box-shadow: 0 0 20px rgba(0, 136, 255, 0.2);
        }
        .blocking-progress-percent { color: #00aaff; font-size: 18px; margin-top: 6px; text-shadow: 0 0 20px rgba(0, 170, 255, 0.2); }
        .blocking-progress-status { color: #445577; font-size: 11px; margin-top: 4px; min-height: 16px; }
        .blocking-progress-done { display: none; margin-top: 12px; padding: 12px; background: #0a0f1a; border: 1px solid #00cc88; border-radius: 3px; color: #00cc88; font-size: 12px; }
        .blocking-progress-done.show { display: block; }

        #threatMapContainer {
            border: 2px solid #004488 !important;
            animation: mapGlow 4s ease-in-out infinite !important;
            box-shadow: 0 0 20px rgba(0, 100, 200, 0.05) !important;
        }
        
        @keyframes mapGlow {
            0%, 100% { border-color: #004488; box-shadow: 0 0 20px rgba(0, 100, 200, 0.05); }
            50% { border-color: #0088ff; box-shadow: 0 0 40px rgba(0, 136, 255, 0.15); }
        }

        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            header { flex-direction: column; text-align: center; padding: 10px; }
            .logo { font-size: 16px; }
            .container { padding: 8px; }
            .card { padding: 10px; }
            .progress-container { min-width: unset; padding: 20px; margin: 10px; width: 90%; }
            .hacker-btn { font-size: 9px; padding: 4px 10px; }
            .metric { font-size: 20px; }
            table { font-size: 9px; }
            th, td { padding: 3px; }
            .scroll { max-height: 200px; }
            #threatMapContainer { min-height: 180px; }
        }
        @media (max-width: 480px) {
            header { padding: 6px; }
            .logo { font-size: 13px; }
            .container { padding: 4px; }
            .card { padding: 6px; }
            .hacker-btn { font-size: 8px; padding: 3px 6px; }
            .metric { font-size: 16px; }
            .grid { gap: 6px; }
            .hacker-input { font-size: 9px; padding: 3px 5px; }
            #threatMapContainer { min-height: 120px; }
        }
    </style>
</head>
<body>

<div class="progress-overlay" id="progressOverlay">
    <div class="progress-container">
        <div class="progress-icon" id="progressIcon" style="font-size:35px; margin-bottom:8px;">🔄</div>
        <div class="progress-title" id="progressTitle">SCANNING...</div>
        <div class="progress-bar-wrapper">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <div class="progress-percent" id="progressPercent">0%</div>
        <div class="progress-status" id="progressStatus">Initializing...</div>
        <div class="progress-result" id="progressResult"></div>
    </div>
</div>

<div class="warning-overlay" id="warningOverlay">
    <div class="warning-box">
        <span class="warning-icon">⚠️</span>
        <div class="warning-title">Security Warning</div>
        <hr class="warning-divider">
        <div class="warning-text">
            This is a <span class="highlight">powerful network management tool</span>. Use it responsibly:
            <br><br>
            <span class="bullet">•</span> Only block devices you <span class="highlight">own</span> or have <span class="highlight">permission</span> to manage<br>
            <span class="bullet">•</span> <span class="highlight">Don't</span> block critical infrastructure (routers, servers, etc.)<br>
            <span class="bullet">•</span> Be aware that blocking network devices is <span class="highlight">detectable</span>
            <br><br>
            <span class="info">🔒 This will disconnect the device from the network until you unblock it.</span>
        </div>
        <hr class="warning-divider">
        <div class="warning-buttons">
            <button class="warning-btn warning-btn-cancel" onclick="closeWarning()">Cancel</button>
            <button class="warning-btn warning-btn-proceed" id="proceedBlockBtn">Proceed & Block</button>
        </div>
    </div>
</div>

<div class="blocking-progress-overlay" id="blockingProgressOverlay">
    <div class="blocking-progress-box">
        <div class="blocking-progress-icon">🔄</div>
        <div class="blocking-progress-title">Blocking Device...</div>
        <div class="blocking-progress-text" id="blockProgressText">Initializing blocking sequence...</div>
        <div class="blocking-progress-bar-wrapper">
            <div class="blocking-progress-bar" id="blockingProgressBar"></div>
        </div>
        <div class="blocking-progress-percent" id="blockProgressPercent">0%</div>
        <div class="blocking-progress-status" id="blockProgressStatus">Preparing...</div>
        <div class="blocking-progress-done" id="blockProgressDone">✅ Device blocked successfully!</div>
    </div>
</div>

<header>
    <div class="logo">🔐 NETWORK SURVEILLANCE</div>
    <div>
        <span class="hacker-status online" id="statusDot"></span>
        <span class="live">●</span>
        <span id="clock"></span>
        <span class="cache-status cached" id="cacheStatus">● CACHED</span>
    </div>
</header>

<div class="container">

    <div class="grid">
        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">🔥 Firewall</h3>
                <span class="badge">● ACTIVE</span>
            </div>
            <div class="metric" id="blockedIPs">0</div>
            <div class="small">Blocked IPs</div>
            <div class="metric" id="blockedPorts">0</div>
            <div class="small">Blocked Ports</div>
        </div>

        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">📡 Network</h3>
                <span class="badge">● LIVE</span>
            </div>
            <div class="metric" id="download">0 KB/s</div>
            <div class="small">Download</div>
            <div class="metric" id="upload">0 KB/s</div>
            <div class="small">Upload</div>
        </div>

        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">🔗 Connections</h3>
                <span class="badge" id="connBadge">0</span>
            </div>
            <div class="metric" id="connectionCount">0</div>
            <div class="small">Active connections</div>
        </div>

        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">🛡️ Security</h3>
                <span class="badge">● MONITORING</span>
            </div>
            <div>Critical: <span class="red" id="critical">0</span></div>
            <div>High: <span class="orange" id="high">0</span></div>
            <div>Medium: <span class="yellow" id="medium">0</span></div>
            <div>SIEM events: <span class="blue" id="siem">0</span></div>
        </div>
    </div>

    <div class="card hacker-panel">
        <div class="hacker-header">
            <h3 class="hacker-title">🧪 TEST SIEM EVENTS</h3>
            <span class="badge">● REAL-TIME</span>
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            <button class="hacker-btn hacker-btn-danger" onclick="testSIEMEvents()">🚀 Generate Test</button>
            <button class="hacker-btn hacker-btn-blue" onclick="testCriticalAlerts()">🔴 Critical Alerts</button>
            <button class="hacker-btn hacker-btn-warning" onclick="testAllEvents()">⚡ All Events</button>
            <button class="hacker-btn" onclick="document.getElementById('testResults').innerHTML=''; updateTestStatus('Cleared',true);">🗑️</button>
        </div>
        <div id="testStatus" style="margin-top:6px; font-size:11px; color:#445577;">Ready to test...</div>
        <div id="testResults" style="margin-top:4px; max-height:60px; overflow-y:auto; font-size:10px; background:#0a0f1a; border-radius:2px; padding:3px 6px; border:1px solid #004488;"></div>
    </div>

    <br>

    <div class="grid">
        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">⚙️ Firewall Controls</h3>
            </div>
            <div class="form">
                <input class="hacker-input" id="blockIP" placeholder="IP address">
                <input class="hacker-input" id="blockReason" placeholder="Reason">
                <button class="hacker-btn" onclick="blockIP()">🚫 Block</button>
            </div>
            <br>
            <div class="form">
                <input class="hacker-input" id="unblockIP" placeholder="IP address">
                <button class="hacker-btn hacker-btn-success" onclick="unblockIP()">✅ Unblock</button>
            </div>
            <br>
            <div class="form">
                <input class="hacker-input" id="blockPort" type="number" placeholder="Port">
                <button class="hacker-btn hacker-btn-warning" onclick="blockPort()">🔒 Block Port</button>
                <input class="hacker-input" id="unblockPort" type="number" placeholder="Port">
                <button class="hacker-btn hacker-btn-success" onclick="unblockPort()">🔓 Unblock</button>
            </div>
        </div>

        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">🖥️ Endpoint Controls</h3>
            </div>
            <div class="form">
                <input class="hacker-input" id="killPID" type="number" placeholder="PID">
                <button class="hacker-btn hacker-btn-danger" onclick="killProcess()">🗡️ Terminate</button>
                <button class="hacker-btn hacker-btn-blue" onclick="scanProcesses()">🔍 Scan</button>
            </div>
            <br>
            <div class="form">
                <input class="hacker-input" id="iocIP" placeholder="Threat IOC IP">
                <input class="hacker-input" id="iocDescription" placeholder="IOC desc">
                <button class="hacker-btn hacker-btn-warning" onclick="addIOC()">➕ Add IOC</button>
            </div>
        </div>
    </div>

    <br>

    <div class="grid">
        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">📊 Live Connections</h3>
                <span class="badge">● REAL-TIME</span>
            </div>
            <div class="scroll hacker-scroll">
                <table class="hacker-table">
                    <thead>
                        <tr><th>Process</th><th>PID</th><th>Local</th><th>Remote</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody id="connections"></tbody>
                </table>
            </div>
        </div>

        <div class="card hacker-panel" style="grid-column: span 1; min-height: 400px;">
            <div class="hacker-header">
                <h3 class="hacker-title">🗺️ REAL-TIME THREAT MAP & FEED</h3>
                <span class="badge" id="mapFeedBadge">0</span>
            </div>
            <div style="display: flex; flex-direction: column; height: 380px; margin-top: 6px;">
                <div id="threatMapContainer" style="flex: 2; background: #0a0f1a; border-radius: 4px; border: 2px solid #004488; overflow: hidden; min-height: 180px; position: relative; animation: borderGlow 4s ease-in-out infinite; box-shadow: 0 0 20px rgba(0, 100, 200, 0.05);">
                    <div id="threatMap" style="width: 100%; height: 100%;">
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #445577; font-size: 12px; padding: 15px; flex-direction: column;">
                            <div style="width: 30px; height: 30px; border: 2px solid #004488; border-top-color: #00aaff; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px;"></div>
                            <div>Loading threat map...</div>
                        </div>
                    </div>
                    <div style="position: absolute; bottom: 8px; left: 8px; background: rgba(13, 21, 32, 0.85); border: 1px solid #004488; border-radius: 2px; padding: 4px 8px; font-size: 8px; color: #445577; z-index: 1000;">
                        <span style="color:#cc4455;">●</span> Threat <span style="color:#00aaff;">●</span> Normal
                    </div>
                    <div style="position: absolute; bottom: 8px; right: 8px; z-index: 1000;">
                        <button onclick="refreshThreatMap()" style="background:rgba(13, 21, 32, 0.85); border:1px solid #004488; color:#445577; padding:2px 8px; border-radius:2px; cursor:pointer; font-size:9px;">🔄</button>
                    </div>
                </div>
                <div style="flex: 1; background: #0a0f1a; border-radius: 4px; border: 1px solid #004488; display: flex; flex-direction: column; overflow: hidden; margin-top: 4px; min-height: 80px; animation: borderGlow 4s ease-in-out infinite;">
                    <div style="padding: 3px 8px; border-bottom: 1px solid #004488; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">
                        <span style="color:#445577; font-size: 10px;">🔴 THREAT FEED</span>
                        <span id="mapFeedBadge2" style="background:#004488; color:#8899bb; font-size: 8px; padding: 1px 8px; border-radius: 2px;">0</span>
                    </div>
                    <div id="mapFeedList" style="flex: 1; overflow-y: auto; padding: 3px 4px;" class="hacker-scroll">
                        <div style="color:#445577; text-align:center; padding: 10px 0; font-size: 11px;">Waiting for events...</div>
                    </div>
                    <div style="padding: 3px 6px; border-top: 1px solid #004488; display: flex; gap: 4px; flex-shrink: 0; flex-wrap: wrap;">
                        <input id="mapBlockIP" placeholder="Block IP" class="hacker-input" style="flex:1; padding:2px 6px; font-size:9px; min-width:60px;">
                        <button class="hacker-btn" onclick="mapBlockIP()" style="padding:2px 8px; font-size:9px;">🚫 Block</button>
                        <button class="hacker-btn hacker-btn-blue" onclick="refreshThreatMap()" style="padding:2px 8px; font-size:9px;">🔄</button>
                        <button class="hacker-btn hacker-btn-success" onclick="forceRefresh()" style="padding:2px 8px; font-size:9px;">⚡</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <br>

    <div class="grid">
        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">📊 Processes</h3>
                <span class="badge">● SCANNING</span>
            </div>
            <div class="scroll hacker-scroll">
                <table class="hacker-table">
                    <thead><tr><th>PID</th><th>Name</th><th>User</th><th>CPU</th><th>Memory</th></tr></thead>
                    <tbody id="processes"></tbody>
                </table>
            </div>
        </div>

        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">📋 SIEM Events</h3>
                <span class="badge">● LOGGING</span>
            </div>
            <div class="scroll hacker-scroll">
                <table class="hacker-table">
                    <thead><tr><th>Time</th><th>Severity</th><th>Type</th><th>Message</th></tr></thead>
                    <tbody id="events"></tbody>
                </table>
            </div>
        </div>
    </div>

    <br>

    <div class="grid">
        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">🌐 Network Protocols</h3>
            </div>
            <pre id="protocols" style="color:#00aaff; font-size:11px; max-height:100px; overflow-y:auto; text-shadow: 0 0 10px rgba(0, 170, 255, 0.1);">Waiting for data...</pre>
        </div>

        <div class="card hacker-panel">
            <div class="hacker-header">
                <h3 class="hacker-title">⚠️ Threat Intelligence</h3>
                <span class="badge" id="threatBadge">0</span>
            </div>
            <div id="threats" style="font-size:11px; max-height:100px; overflow-y:auto;"></div>
            <br>
            <div style="display: flex; gap: 4px; flex-wrap: wrap;">
                <button class="hacker-btn hacker-btn-warning" onclick="generateMap()">🗺️ Generate Map</button>
                <button class="hacker-btn hacker-btn-blue" onclick="browserConnections()">🌐 Browser Conn</button>
                <button class="hacker-btn hacker-btn-success" onclick="forceRefresh()">⚡ Refresh</button>
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card hacker-panel" style="grid-column: span 2;">
            <div class="hacker-header">
                <h3 class="hacker-title">🌐 NETWORK DEVICES</h3>
                <span class="badge" id="deviceBadge">0</span>
                <div style="display: flex; gap: 4px;">
                    <button class="hacker-btn hacker-btn-success" onclick="scanNetwork()" style="padding:3px 10px; font-size:9px;">🔄 Scan</button>
                    <button class="hacker-btn hacker-btn-blue" onclick="refreshDevices()" style="padding:3px 10px; font-size:9px;">⟳ Refresh</button>
                </div>
            </div>
            <div style="margin-top: 8px; max-height: 350px; overflow-y: auto;" class="hacker-scroll" id="deviceList">
                <div style="text-align: center; color: #445577; padding: 25px 0;">
                    <div style="font-size: 35px; margin-bottom: 8px;">📡</div>
                    <div>Click "Scan" to discover devices on your network</div>
                    <div style="font-size: 10px; margin-top: 4px; color: #334466;">This will scan your local network (e.g., 192.168.1.0/24)</div>
                </div>
            </div>
            <div style="margin-top: 6px; display: flex; gap: 6px; align-items: center; flex-wrap: wrap; border-top: 1px solid #004488; padding-top: 6px;">
                <span style="color:#445577; font-size:10px;">🔍 Quick Block:</span>
                <input id="quickBlockIP" placeholder="Enter IP to block" class="hacker-input" style="flex:1; padding:3px 6px; font-size:10px; min-width:100px;">
                <input id="quickBlockReason" placeholder="Reason" class="hacker-input" style="flex:1; padding:3px 6px; font-size:10px; min-width:80px;">
                <button class="hacker-btn hacker-btn-danger" onclick="quickBlockDevice()" style="padding:3px 10px; font-size:9px;">🚫 Block</button>
                <span style="color:#334466; font-size:9px;">|</span>
                <button class="hacker-btn hacker-btn-warning" onclick="showBlockedDevices()" style="padding:3px 10px; font-size:9px;">📋 Blocked</button>
            </div>
        </div>
    </div>

</div>

<footer>
    ⚡ Real host telemetry — no simulated network traffic ⚡
    <br>
    <span style="font-size: 9px; color: #334466;">Cache: <span id="cacheAge">0s</span> ago</span>
</footer>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    // ============================================================
    // CONFIGURATION
    // ============================================================

    const API_BASE = window.location.origin;
    const CACHE_KEY = 'network_security_cache';
    const CACHE_TIME_KEY = 'network_security_cache_time';

    // ============================================================
    // UTILITY FUNCTIONS
    // ============================================================

    function esc(value) {
        if (value === null || value === undefined) return "";
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    async function api(url, method = "GET", body = null) {
        const options = { method, headers: { "Content-Type": "application/json" } };
        if (body !== null) options.body = JSON.stringify(body);
        const response = await fetch(url, options);
        return await response.json();
    }

    function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

    // ============================================================
    // TEST SIEM EVENTS
    // ============================================================

    function updateTestStatus(message, isSuccess = true) {
        const statusEl = document.getElementById('testStatus');
        if (statusEl) { statusEl.textContent = message; statusEl.style.color = isSuccess ? '#00cc88' : '#cc4455'; }
    }

    function addTestResult(message, isSuccess = true) {
        const resultsEl = document.getElementById('testResults');
        if (!resultsEl) return;
        const div = document.createElement('div');
        div.style.padding = '2px 0';
        div.style.borderBottom = '1px solid #0d1520';
        div.style.color = isSuccess ? '#00cc88' : '#cc4455';
        div.textContent = (isSuccess ? '✅ ' : '❌ ') + message;
        resultsEl.prepend(div);
        while (resultsEl.children.length > 20) resultsEl.removeChild(resultsEl.lastChild);
    }

    async function testSIEMEvents() {
        updateTestStatus('⏳ Generating test events...', true);
        addTestResult('🚀 Starting SIEM event test...', true);

        const events = [
            {severity: "HIGH", type: "failed_login", msg: "Failed login from 192.168.1.50", data: {source_ip: "192.168.1.50"}},
            {severity: "HIGH", type: "failed_login", msg: "Failed login from 192.168.1.51", data: {source_ip: "192.168.1.51"}},
            {severity: "MEDIUM", type: "connection_attempt", msg: "Port scan from 10.0.0.100", data: {source_ip: "10.0.0.100", port: 22}},
            {severity: "HIGH", type: "suspicious_process", msg: "Suspicious process: cryptominer.exe", data: {pid: 1234, name: "cryptominer.exe"}},
        ];

        for (const event of events) {
            try {
                const response = await api("/api/events", "POST", {
                    source: "Test_Button",
                    event_type: event.type,
                    severity: event.severity,
                    message: event.msg,
                    data: event.data
                });
                if (response && response.success) addTestResult(`[${event.severity}] ${event.type}`, true);
                else addTestResult(`Failed: ${event.type}`, false);
            } catch (error) { addTestResult(`Error: ${event.type}`, false); }
            await sleep(150);
        }
        updateTestStatus('✅ Test completed! Check threat feed and SIEM events.', true);
        addTestResult('✅ SIEM event test complete!', true);
    }

    async function testCriticalAlerts() {
        updateTestStatus('⏳ Generating critical alerts...', true);
        addTestResult('🚀 Starting critical alert test...', true);

        const alerts = [
            {severity: "CRITICAL", type: "Ransomware Detected", msg: "Ransomware activity detected!", data: {threat: "ransomware", score: 95}},
            {severity: "CRITICAL", type: "C2 Communication", msg: "C2 comm on port 4444", data: {remote_ip: "185.130.5.253", port: 4444}},
            {severity: "HIGH", type: "Data Exfiltration", msg: "Large data upload detected", data: {bytes: "500MB", remote_ip: "94.102.61.78"}},
        ];

        for (const alert of alerts) {
            try {
                const response = await api("/api/events", "POST", {
                    source: "Test_Button",
                    event_type: alert.type,
                    severity: alert.severity,
                    message: alert.msg,
                    data: alert.data
                });
                if (response && response.success) addTestResult(`🔴 [${alert.severity}] ${alert.type}`, true);
                else addTestResult(`Failed: ${alert.type}`, false);
            } catch (error) { addTestResult(`Error: ${alert.type}`, false); }
            await sleep(250);
        }
        updateTestStatus('✅ Critical alerts generated!', true);
        addTestResult('✅ Critical alert test complete!', true);
    }

    async function testAllEvents() {
        updateTestStatus('⏳ Generating all event types...', true);
        addTestResult('🚀 Starting comprehensive test...', true);
        document.getElementById('testResults').innerHTML = '';

        for (let i = 1; i <= 3; i++) {
            const ip = `10.0.0.${i}`;
            try {
                const response = await api("/api/firewall/block-ip", "POST", { ip, reason: `Test block ${i}` });
                if (response && response.success) addTestResult(`🔥 Blocked IP ${ip}`, true);
            } catch (error) { addTestResult(`Failed to block ${ip}`, false); }
            await sleep(200);
        }

        const events = [
            {severity: "HIGH", type: "failed_login", msg: "Brute force from 192.168.1.100", data: {source_ip: "192.168.1.100"}},
            {severity: "CRITICAL", type: "known_threat", msg: "Known threat IOC: 185.130.5.253", data: {remote_ip: "185.130.5.253"}},
            {severity: "CRITICAL", type: "ransomware", msg: "Ransomware activity detected!", data: {files_encrypted: 100}},
        ];

        for (const event of events) {
            try {
                const response = await api("/api/events", "POST", {
                    source: "Test_Button",
                    event_type: event.type,
                    severity: event.severity,
                    message: event.msg,
                    data: event.data
                });
                if (response && response.success) addTestResult(`📊 [${event.severity}] ${event.type}`, true);
                else addTestResult(`Failed: ${event.type}`, false);
            } catch (error) { addTestResult(`Error: ${event.type}`, false); }
            await sleep(150);
        }

        try {
            const response = await api("/api/process/scan", "POST");
            if (response && response.success) addTestResult(`🔍 Process scan complete - ${response.suspicious || 0} suspicious`, true);
        } catch (error) { addTestResult('Failed to trigger process scan', false); }

        updateTestStatus('✅ All tests complete! Check real-time updates.', true);
        addTestResult('✅ Comprehensive test complete!', true);
    }

    window.testSIEMEvents = testSIEMEvents;
    window.testCriticalAlerts = testCriticalAlerts;
    window.testAllEvents = testAllEvents;

    // ============================================================
    // PROGRESS BAR
    // ============================================================

    function showProgress(title, icon = '🔄') {
        const overlay = document.getElementById('progressOverlay');
        if (!overlay) { alert(title + ' - Please refresh the page'); return; }
        overlay.className = 'progress-overlay active';
        const bar = document.getElementById('progressBar');
        const percent = document.getElementById('progressPercent');
        const status = document.getElementById('progressStatus');
        const result = document.getElementById('progressResult');
        const titleEl = document.getElementById('progressTitle');
        const iconEl = document.getElementById('progressIcon');
        
        if (bar) bar.style.width = '0%';
        if (percent) percent.textContent = '0%';
        if (status) status.textContent = 'Initializing...';
        if (result) { result.innerHTML = ''; result.className = 'progress-result'; }
        if (titleEl) titleEl.textContent = title;
        if (iconEl) iconEl.textContent = icon;
    }

    function updateProgress(value, statusText) {
        const bar = document.getElementById('progressBar');
        const percent = document.getElementById('progressPercent');
        const status = document.getElementById('progressStatus');
        if (!bar || !percent) return;
        const clamped = Math.min(100, Math.max(0, value));
        bar.style.width = clamped + '%';
        percent.textContent = Math.round(clamped) + '%';
        if (statusText && status) status.textContent = statusText;
    }

    function showProgressResult(resultData, isSuccess = true) {
        let result = document.getElementById('progressResult');
        if (!result) {
            const overlay = document.getElementById('progressOverlay');
            if (overlay) {
                const container = overlay.querySelector('.progress-container');
                if (container) {
                    result = document.createElement('div');
                    result.id = 'progressResult';
                    result.className = 'progress-result';
                    container.appendChild(result);
                }
            }
        }
        if (!result) { console.error('progressResult element not found'); return; }
        const status = document.getElementById('progressStatus');
        const percent = document.getElementById('progressPercent');
        result.className = 'progress-result show';
        if (percent) percent.textContent = '100%';
        if (status) {
            status.textContent = isSuccess ? '✅ Complete!' : '❌ Failed';
            status.style.color = isSuccess ? '#00cc88' : '#cc4455';
        }
        if (Array.isArray(resultData)) {
            let html = '';
            for (const item of resultData) {
                const cls = item.reason ? 'highlight' : 'success';
                html += `<div class="item ${cls}">${esc(item.name || item)}</div>`;
            }
            result.innerHTML = html || '<div class="item">No results</div>';
        } else if (typeof resultData === 'string') {
            result.innerHTML = `<div class="item success">${esc(resultData)}</div>`;
        } else if (resultData && typeof resultData === 'object') {
            result.innerHTML = `<div class="item success">${esc(JSON.stringify(resultData, null, 2))}</div>`;
        }
    }

    function hideProgress() {
        const overlay = document.getElementById('progressOverlay');
        if (!overlay) return;
        overlay.className = 'progress-overlay';
        setTimeout(() => {
            const bar = document.getElementById('progressBar');
            const result = document.getElementById('progressResult');
            if (bar) bar.style.width = '0%';
            if (result) { result.className = 'progress-result'; result.innerHTML = ''; }
        }, 300);
    }

    // ============================================================
    // PERSISTENT CACHE
    // ============================================================

    function saveToCache(data) {
        try { localStorage.setItem(CACHE_KEY, JSON.stringify(data)); localStorage.setItem(CACHE_TIME_KEY, Date.now().toString()); updateCacheAge(); } catch (e) {}
    }

    function loadFromCache() {
        try {
            const data = localStorage.getItem(CACHE_KEY);
            const timestamp = localStorage.getItem(CACHE_TIME_KEY);
            if (data && timestamp) {
                const age = Date.now() - parseInt(timestamp);
                if (age < 60000) return JSON.parse(data);
            }
        } catch (e) {}
        return null;
    }

    function getCacheAge() {
        try {
            const timestamp = localStorage.getItem(CACHE_TIME_KEY);
            if (timestamp) return Math.round((Date.now() - parseInt(timestamp)) / 1000);
        } catch (e) {}
        return null;
    }

    function updateCacheAge() {
        const age = getCacheAge();
        const el = document.getElementById('cacheAge');
        if (el) el.textContent = age !== null ? age + 's' : 'N/A';
        const statusEl = document.getElementById('cacheStatus');
        if (statusEl) {
            if (age !== null && age < 10) { statusEl.className = 'cache-status fresh'; statusEl.textContent = '● FRESH'; }
            else if (age !== null && age < 30) { statusEl.className = 'cache-status cached'; statusEl.textContent = '● CACHED'; }
            else { statusEl.className = 'cache-status stale'; statusEl.textContent = '● STALE'; }
        }
    }

    function clearCache() { try { localStorage.removeItem(CACHE_KEY); localStorage.removeItem(CACHE_TIME_KEY); } catch (e) {} }

    // ============================================================
    // RENDER FUNCTIONS
    // ============================================================

    function render(data) {
        if (!data) return;
        document.getElementById("clock").textContent = " " + data.time;
        document.getElementById("blockedIPs").textContent = data.firewall?.blocked_ips || 0;
        document.getElementById("blockedPorts").textContent = data.firewall?.blocked_ports || 0;
        document.getElementById("download").textContent = (data.network?.download_kbps || 0) + " KB/s";
        document.getElementById("upload").textContent = (data.network?.upload_kbps || 0) + " KB/s";
        document.getElementById("connectionCount").textContent = data.network?.connections?.length || 0;
        document.getElementById("connBadge").textContent = data.network?.connections?.length || 0;
        document.getElementById("critical").textContent = data.alerts?.critical || 0;
        document.getElementById("high").textContent = data.alerts?.high || 0;
        document.getElementById("medium").textContent = data.alerts?.medium || 0;
        document.getElementById("siem").textContent = data.siem?.total || 0;

        renderConnections(data.network?.connections || []);
        renderProcesses(data.endpoint?.processes || []);
        renderAlerts(data.recent_alerts || []);
        renderEvents(data.recent_events || []);
        renderThreats(data.threat_intelligence || {});
        document.getElementById("protocols").textContent = JSON.stringify(data.network?.protocol_stats || {}, null, 2);
        saveToCache(data);
        updateCacheAge();
    }

    function renderConnections(connections) {
        const tbody = document.getElementById("connections");
        tbody.innerHTML = "";
        for (const c of connections) {
            const tr = document.createElement("tr");
            const remote = c.remote_ip ? c.remote_ip + ":" + (c.remote_port || "") : "";
            tr.innerHTML = `
                <td>${esc(c.process)}</td>
                <td>${esc(c.pid)}</td>
                <td>${esc(c.local_ip)}:${esc(c.local_port)}</td>
                <td>${esc(remote)}</td>
                <td>${c.blocked ? '<span class="red">BLOCKED</span>' : esc(c.status)}</td>
                <td>${c.remote_ip ? `<button class="hacker-btn hacker-btn-danger" onclick="quickBlock('${esc(c.remote_ip)}')" style="padding:1px 5px; font-size:8px;">🚫 Block</button>` : ""}</td>
            `;
            tbody.appendChild(tr);
        }
    }

    function renderProcesses(processes) {
        const tbody = document.getElementById("processes");
        tbody.innerHTML = "";
        for (const p of processes.slice(0, 100)) {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td>${esc(p.pid)}</td><td>${esc(p.name)}</td><td>${esc(p.username)}</td><td>${esc(p.cpu_percent)}%</td><td>${esc(p.memory_percent)}%</td>`;
            tbody.appendChild(tr);
        }
    }

    function renderAlerts(alerts) {
        const element = document.getElementById("alerts");
        if (!element) return;
        element.innerHTML = "";
        for (const alert of alerts.slice().reverse()) {
            const div = document.createElement("div");
            div.className = "hacker-alert " + alert.severity.toLowerCase();
            div.innerHTML = `<strong>[${esc(alert.severity)}] ${esc(alert.title)}</strong><br>${esc(alert.message)}<br><span style="color:#445577;font-size:9px;">${esc(alert.timestamp)} | ${esc(alert.source)}</span>`;
            element.appendChild(div);
        }
    }

    function renderEvents(events) {
        const tbody = document.getElementById("events");
        tbody.innerHTML = "";
        for (const event of events.slice().reverse()) {
            const tr = document.createElement("tr");
            const color = { 'CRITICAL': 'red', 'HIGH': 'orange', 'MEDIUM': 'yellow', 'LOW': 'blue' }[event.severity] || 'blue';
            tr.innerHTML = `<td>${esc(event.timestamp)}</td><td class="${color}">${esc(event.severity)}</td><td>${esc(event.event_type)}</td><td>${esc(event.message)}</td>`;
            tbody.appendChild(tr);
        }
    }

    function renderThreats(threats) {
        const element = document.getElementById("threats");
        if (!element) return;
        element.innerHTML = "";
        let count = 0;
        for (const [ip, description] of Object.entries(threats)) {
            element.innerHTML += `<div><span class="red">${esc(ip)}</span> — ${esc(description)}</div>`;
            count++;
        }
        document.getElementById("threatBadge").textContent = count;
    }

    // ============================================================
    // THREAT MAP
    // ============================================================

    let threatMap = null;
    let mapMarkers = {};
    let mapLines = {};
    let mapPulseRings = {};
    let hostMarker = null;
    let hostPulseRings = [];
    let hostLat = -13.9833;
    let hostLon = 33.7833;

    function initThreatMap() {
        const container = document.getElementById('threatMap');
        if (!container) return;
        if (threatMap) { setTimeout(() => { if (threatMap) threatMap.invalidateSize(); }, 300); return; }
        container.innerHTML = '';
        threatMap = L.map('threatMap', { center: [hostLat, hostLon], zoom: 3, zoomControl: true, fadeAnimation: true, zoomAnimation: true, markerZoomAnimation: true, attributionControl: true });
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; CartoDB',
            subdomains: 'abcd', maxZoom: 19, minZoom: 2
        }).addTo(threatMap);
        addHostLocation(hostLat, hostLon);
        setTimeout(() => { if (threatMap) threatMap.invalidateSize(); }, 500);
        setTimeout(() => { if (threatMap) threatMap.invalidateSize(); }, 1500);
    }

    function addHostLocation(lat, lon) {
        if (!threatMap) return;
        if (hostMarker) { threatMap.removeLayer(hostMarker); hostMarker = null; }
        for (const ring of hostPulseRings) { threatMap.removeLayer(ring); }
        hostPulseRings = [];

        hostMarker = L.circleMarker([lat, lon], {
            radius: 10, color: '#cc4455', fillColor: '#cc4455', fillOpacity: 0.8, weight: 2
        }).addTo(threatMap);
        const popupContent = `<div style="text-align:center;background:#0d1520;padding:8px;border:1px solid #004488;border-radius:3px;">
            <div style="color:#cc4455;font-size:16px;">🔴</div>
            <div style="color:#00aaff;font-size:12px;">SECURITY HOST</div>
            <div style="color:#8899bb;font-size:10px;">${window.location.hostname || 'Local Host'}</div>
        </div>`;
        hostMarker.bindPopup(popupContent, { className: 'map-tooltip' });
        threatMap.setView([lat, lon], 4);
    }

    function addMapMarker(ip, data) {
        if (!threatMap) return;
        const key = ip;
        if (mapMarkers[key]) { threatMap.removeLayer(mapMarkers[key]); delete mapMarkers[key]; }
        if (mapLines[key]) { threatMap.removeLayer(mapLines[key]); delete mapLines[key]; }
        if (mapPulseRings[key]) { threatMap.removeLayer(mapPulseRings[key]); delete mapPulseRings[key]; }

        const isThreat = data.threat || false;
        const color = isThreat ? '#cc4455' : '#00aaff';
        const marker = L.circleMarker([data.lat, data.lon], {
            radius: isThreat ? 7 : 4, color: color, fillColor: color, fillOpacity: 0.7, weight: 1
        });
        const popupContent = `<div style="font-size:10px;min-width:150px;color:#8899bb;">
            <div><span style="color:#445577;">IP:</span> <strong style="color:#00aaff;">${ip}</strong></div>
            <div><span style="color:#445577;">Host:</span> ${data.hostname || 'Unknown'}</div>
            <div><span style="color:#445577;">Location:</span> ${data.city || ''}, ${data.country || ''}</div>
            ${isThreat ? `<div style="color:#cc4455;margin-top:3px;">⚠️ THREAT DETECTED</div>` : ''}
            <div style="margin-top:4px;border-top:1px solid #0d1520;padding-top:4px;">
                <button onclick="quickBlockMap('${ip}')" style="background:#1a2a3a;color:#8899bb;border:1px solid #004488;padding:2px 10px;border-radius:2px;cursor:pointer;font-size:9px;">🚫 Block IP</button>
            </div>
        </div>`;
        marker.bindPopup(popupContent, { className: 'map-tooltip', maxWidth: 200 });
        marker.addTo(threatMap);
        mapMarkers[key] = marker;

        if (data.hostLat && data.hostLon && data.lat && data.lon) {
            const line = L.polyline([[data.hostLat, data.hostLon], [data.lat, data.lon]], {
                color: isThreat ? '#cc4455' : '#4488cc', weight: isThreat ? 1.5 : 1, opacity: isThreat ? 0.6 : 0.3
            }).addTo(threatMap);
            mapLines[key] = line;
        }
    }

    async function loadThreatMapData() {
        try {
            const cached = loadFromCache();
            let snapshot = cached;
            if (!snapshot) {
                try { const response = await fetch(API_BASE + '/api/snapshot'); if (response.ok) snapshot = await response.json(); } catch (e) {}
            }
            if (!snapshot) { console.warn('No data available for threat map'); return; }

            try {
                const geo = await fetch('https://ipapi.co/json/').then(r => r.json());
                if (geo.latitude && geo.longitude) {
                    hostLat = geo.latitude; hostLon = geo.longitude;
                    if (hostMarker) { threatMap.removeLayer(hostMarker); hostMarker = null; }
                    for (const ring of hostPulseRings) { threatMap.removeLayer(ring); }
                    hostPulseRings = [];
                    addHostLocation(hostLat, hostLon);
                }
            } catch (e) {}

            const connections = snapshot.network?.connections || [];
            const threats = snapshot.threat_intelligence || {};

            for (const key in mapMarkers) { if (mapMarkers[key]) { threatMap.removeLayer(mapMarkers[key]); delete mapMarkers[key]; } }
            for (const key in mapLines) { if (mapLines[key]) { threatMap.removeLayer(mapLines[key]); delete mapLines[key]; } }
            for (const key in mapPulseRings) { if (mapPulseRings[key]) { threatMap.removeLayer(mapPulseRings[key]); delete mapPulseRings[key]; } }

            const ipMap = {};
            for (const conn of connections) {
                const remoteIp = conn.remote_ip;
                if (!remoteIp || remoteIp === 'N/A' || remoteIp === '127.0.0.1') continue;
                if (ipMap[remoteIp]) continue;
                const isThreat = threats[remoteIp] || false;
                let lat = null, lon = null, city = '', country = '';
                try {
                    const geo = await fetch(API_BASE + '/api/geolocate?ip=' + remoteIp).then(r => r.json());
                    if (geo && geo.latitude && geo.longitude) { lat = geo.latitude; lon = geo.longitude; city = geo.city || ''; country = geo.country || ''; }
                } catch (e) {}
                if (lat === null || lon === null) {
                    const hash = remoteIp.split('.').reduce((a, b) => a + parseInt(b || 0), 0);
                    lat = ((hash % 180) - 90) + (Math.random() * 2 - 1);
                    lon = ((hash * 7) % 360) - 180 + (Math.random() * 2 - 1);
                }
                ipMap[remoteIp] = {
                    lat, lon, city, country,
                    hostname: conn.dns || conn.process || 'Unknown',
                    threat: isThreat || null,
                    hostLat, hostLon
                };
                addMapMarker(remoteIp, ipMap[remoteIp]);
            }
            if (threatMap) setTimeout(() => threatMap.invalidateSize(), 300);
        } catch (error) { console.error('Error loading threat map data:', error); }
    }

    async function refreshThreatMap() { if (!threatMap) initThreatMap(); await loadThreatMapData(); }
    function initThreatMapOnLoad() { setTimeout(() => { initThreatMap(); setTimeout(() => { loadThreatMapData(); if (!window._mapRefreshInterval) { window._mapRefreshInterval = setInterval(loadThreatMapData, 30000); } }, 500); }, 1000); }
    window.addEventListener('resize', function() { if (threatMap) setTimeout(() => threatMap.invalidateSize(), 300); });

    // ============================================================
    // DASHBOARD ACTIONS WITH PROGRESS BAR
    // ============================================================

    async function scanProcesses() {
        showProgress('🔍 SCANNING PROCESSES', '🔍');
        try {
            updateProgress(10, 'Initializing process scan...');
            await sleep(300);
            updateProgress(30, 'Scanning running processes...');
            await sleep(400);
            updateProgress(50, 'Analyzing process behavior...');
            await sleep(400);
            updateProgress(70, 'Checking for suspicious activity...');
            const result = await api("/api/process/scan", "POST");
            updateProgress(90, 'Compiling results...');
            await sleep(300);
            if (result && result.success) {
                const suspicious = result.suspicious || 0;
                const findings = result.results || [];
                if (suspicious > 0) { showProgressResult(findings, true); document.getElementById('progressStatus').textContent = `⚠️ Found ${suspicious} suspicious processes`; } 
                else { showProgressResult(['✅ No suspicious processes found'], true); document.getElementById('progressStatus').textContent = '✅ Scan complete - System clean'; }
            } else { showProgressResult(['❌ Scan failed: ' + (result?.message || 'Unknown error')], false); }
            setTimeout(hideProgress, 3000);
        } catch (error) { updateProgress(100, '❌ Error during scan'); showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 3000); }
    }

    async function forceRefresh() {
        const overlay = document.getElementById('progressOverlay');
        if (!overlay) { location.reload(); return; }
        showProgress('⚡ FORCE REFRESH', '⚡');
        try {
            updateProgress(30, 'Clearing cache...');
            clearCache();
            await sleep(300);
            updateProgress(50, 'Fetching fresh data...');
            const data = await api("/api/snapshot");
            updateProgress(80, 'Updating dashboard...');
            if (data) { render(data); saveToCache(data); if (threatMap) loadThreatMapData(); }
            updateProgress(100, '✅ Refresh complete');
            showProgressResult(['✅ Dashboard refreshed successfully!'], true);
            setTimeout(hideProgress, 2000);
        } catch (error) { showProgressResult(['❌ Error: ' + (error.message || 'Unknown error')], false); setTimeout(hideProgress, 3000); }
    }

    async function generateMap() {
        showProgress('🗺️ GENERATING THREAT MAP', '🗺️');
        try {
            updateProgress(10, 'Collecting connection data...');
            await sleep(300);
            updateProgress(30, 'Geolocating remote IPs...');
            await sleep(500);
            updateProgress(50, 'Building threat map layers...');
            await sleep(400);
            updateProgress(70, 'Rendering map...');
            const result = await api("/api/threat-map", "POST");
            updateProgress(90, 'Finalizing...');
            await sleep(300);
            if (result && result.success) {
                const mapUrl = result.url || result.file;
                showProgressResult(['✅ Threat map generated successfully!', '📍 ' + mapUrl], true);
                document.getElementById('progressStatus').textContent = '✅ Map ready - opening in new tab';
                setTimeout(() => { if (result.url) window.open(result.url, "_blank"); else if (result.file) window.open('/' + result.file, "_blank"); }, 500);
                setTimeout(hideProgress, 4000);
            } else { showProgressResult(['❌ Map generation failed: ' + (result?.message || 'Unknown error')], false); setTimeout(hideProgress, 3000); }
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 3000); }
    }

    async function blockIP() {
        const ip = document.getElementById("blockIP").value;
        const reason = document.getElementById("blockReason").value || "Dashboard block";
        if (!ip) { alert('Please enter an IP address'); return; }
        showProgress('🚫 BLOCKING IP', '🚫');
        try {
            updateProgress(30, `Blocking IP ${ip}...`);
            const result = await api("/api/firewall/block-ip", "POST", { ip, reason });
            if (result && result.success) {
                updateProgress(100, '✅ IP blocked successfully');
                showProgressResult([`✅ IP ${ip} blocked successfully`, `Reason: ${reason}`], true);
                document.getElementById("blockedIPs").textContent = parseInt(document.getElementById("blockedIPs").textContent) + 1;
            } else { showProgressResult(['❌ ' + (result?.message || 'Failed to block IP')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function unblockIP() {
        const ip = document.getElementById("unblockIP").value;
        if (!ip) { alert('Please enter an IP address'); return; }
        showProgress('🔓 UNBLOCKING IP', '🔓');
        try {
            updateProgress(30, `Unblocking IP ${ip}...`);
            const result = await api("/api/firewall/unblock-ip", "POST", { ip });
            if (result && result.success) { updateProgress(100, '✅ IP unblocked successfully'); showProgressResult([`✅ IP ${ip} unblocked successfully`], true); } 
            else { showProgressResult(['❌ ' + (result?.message || 'Failed to unblock IP')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function blockPort() {
        const port = document.getElementById("blockPort").value;
        if (!port) { alert('Please enter a port number'); return; }
        showProgress('🔒 BLOCKING PORT', '🔒');
        try {
            updateProgress(30, `Blocking port ${port}...`);
            const result = await api("/api/firewall/block-port", "POST", { port });
            if (result && result.success) { updateProgress(100, '✅ Port blocked successfully'); showProgressResult([`✅ Port ${port} blocked successfully`], true); } 
            else { showProgressResult(['❌ ' + (result?.message || 'Failed to block port')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function unblockPort() {
        const port = document.getElementById("unblockPort").value;
        if (!port) { alert('Please enter a port number'); return; }
        showProgress('🔓 UNBLOCKING PORT', '🔓');
        try {
            updateProgress(30, `Unblocking port ${port}...`);
            const result = await api("/api/firewall/unblock-port", "POST", { port });
            if (result && result.success) { updateProgress(100, '✅ Port unblocked successfully'); showProgressResult([`✅ Port ${port} unblocked successfully`], true); } 
            else { showProgressResult(['❌ ' + (result?.message || 'Failed to unblock port')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function killProcess() {
        const pid = document.getElementById("killPID").value;
        if (!pid) { alert('Please enter a PID'); return; }
        if (!confirm("Terminate PID " + pid + "?")) return;
        showProgress('🗡️ TERMINATING PROCESS', '🗡️');
        try {
            updateProgress(30, `Terminating PID ${pid}...`);
            const result = await api("/api/process/terminate", "POST", { pid });
            if (result && result.success) { updateProgress(100, '✅ Process terminated'); showProgressResult(['✅ ' + result.message], true); } 
            else { showProgressResult(['❌ ' + (result?.message || 'Failed to terminate')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function addIOC() {
        const ip = document.getElementById("iocIP").value;
        const description = document.getElementById("iocDescription").value;
        if (!ip) { alert('Please enter an IP address'); return; }
        showProgress('➕ ADDING IOC', '➕');
        try {
            updateProgress(30, `Adding IOC ${ip}...`);
            const result = await api("/api/ioc/add", "POST", { ip, description });
            if (result && result.success) { updateProgress(100, '✅ IOC added'); showProgressResult([`✅ Added threat IOC: ${ip}`, `Description: ${description || 'N/A'}`], true); } 
            else { showProgressResult(['❌ ' + (result?.message || 'Failed to add IOC')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function browserConnections() {
        showProgress('🌐 BROWSER CONNECTIONS', '🌐');
        try {
            updateProgress(30, 'Fetching browser connections...');
            const result = await api("/api/browser-connections");
            updateProgress(80, 'Compiling results...');
            await sleep(300);
            let text = "BROWSERS\n\n";
            for (const browser of result.browsers) { text += browser.name + " PID " + browser.pid + "\n"; }
            text += "\nCONNECTIONS\n\n";
            for (const c of result.connections) { text += c.process + " -> " + c.remote_ip + ":" + c.remote_port + " " + c.dns + "\n"; }
            showProgressResult(['✅ Browser connections retrieved'], true);
            document.getElementById('progressStatus').textContent = '✅ Ready';
            setTimeout(hideProgress, 2500);
            alert(text);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    // ============================================================
    // NETWORK DEVICE MANAGEMENT
    // ============================================================

    let discoveredDevices = [];
    let blockedDevices = [];
    let isScanning = false;

    async function scanNetwork() {
        if (isScanning) { alert('Scan already in progress...'); return; }
        isScanning = true;
        const deviceList = document.getElementById('deviceList');
        const badge = document.getElementById('deviceBadge');
        deviceList.innerHTML = `<div style="text-align:center;color:#00aaff;padding:25px 0;"><div style="font-size:35px;margin-bottom:8px;">🔄</div><div>Scanning network for devices...</div><div style="font-size:10px;color:#445577;">This may take 10-30 seconds</div></div>`;
        badge.textContent = '⏳';
        try {
            const response = await fetch('/api/devices/scan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
            if (response.ok) {
                const data = await response.json();
                discoveredDevices = data.devices || [];
                badge.textContent = discoveredDevices.length;
                renderDevices(discoveredDevices);
            } else { throw new Error('Scan failed'); }
        } catch (error) {
            deviceList.innerHTML = `<div style="text-align:center;color:#cc4455;padding:25px 0;"><div style="font-size:35px;">❌</div><div>Failed to scan network</div><div style="font-size:10px;color:#445577;">${error.message}</div><button class="hacker-btn" onclick="scanNetwork()" style="margin-top:8px;padding:4px 16px;">🔄 Retry</button></div>`;
            badge.textContent = '❌';
        }
        isScanning = false;
    }

    function renderDevices(devices) {
        const deviceList = document.getElementById('deviceList');
        if (!deviceList) return;
        if (!devices || devices.length === 0) {
            deviceList.innerHTML = `<div style="text-align:center;color:#445577;padding:25px 0;"><div style="font-size:35px;">📭</div><div>No devices found</div><div style="font-size:10px;color:#334466;">Try scanning again</div></div>`;
            return;
        }
        const sorted = [...devices].sort((a, b) => { if (a.is_self) return -1; if (b.is_self) return 1; return a.ip.localeCompare(b.ip); });
        let html = '<table class="hacker-table" style="width:100%;font-size:10px;"><thead><tr><th>Device</th><th>IP</th><th>MAC</th><th>Vendor</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
        for (const device of sorted) {
            const isSelf = device.is_self || false;
            const isBlocked = blockedDevices.some(d => d.ip === device.ip);
            const vendor = device.vendor || 'Unknown';
            const hostname = device.hostname || 'Unknown';
            const statusColor = isBlocked ? '#cc4455' : '#00aaff';
            const statusText = isBlocked ? '🚫 BLOCKED' : '🟢 Active';
            html += `<tr style="${isSelf ? 'border-left:2px solid #00aaff;' : ''}">
                <td>${isSelf ? '🖥️ Your Machine' : (hostname || device.ip)}</td>
                <td style="color:#4488cc;">${device.ip}</td>
                <td style="font-size:9px;color:#ccaa44;">${device.mac || 'Unknown'}</td>
                <td style="color:${vendor === 'Unknown' ? '#445577' : '#8899bb'};">${vendor}</td>
                <td><span style="color:${statusColor};">${statusText}</span></td>
                <td>${!isSelf ? (isBlocked ? `<button class="hacker-btn hacker-btn-success" onclick="unblockDevice('${device.ip}')" style="padding:1px 6px;font-size:8px;">✅ Unblock</button>` : `<button class="hacker-btn hacker-btn-danger" onclick="blockDevice('${device.ip}','${device.mac||''}')" style="padding:1px 6px;font-size:8px;">🚫 Block</button>`) : `<span style="color:#445577;font-size:8px;">Cannot block self</span>`}</td>
            </tr>`;
        }
        html += '</tbody></table>';
        deviceList.innerHTML = html;
    }

    function blockDevice(ip, mac) {
        const overlay = document.getElementById('warningOverlay');
        if (overlay) { overlay.className = 'warning-overlay active'; }
        document.getElementById('proceedBlockBtn').onclick = function() { closeWarning(); executeBlock(ip, mac); };
    }

    function closeWarning() {
        const overlay = document.getElementById('warningOverlay');
        if (overlay) { overlay.className = 'warning-overlay'; }
    }

    async function executeBlock(ip, mac) {
        const overlay = document.getElementById('blockingProgressOverlay');
        if (overlay) { overlay.className = 'blocking-progress-overlay active'; }
        const bar = document.getElementById('blockingProgressBar');
        const percent = document.getElementById('blockProgressPercent');
        const status = document.getElementById('blockProgressStatus');
        const text = document.getElementById('blockProgressText');
        const done = document.getElementById('blockProgressDone');
        if (bar) bar.style.width = '0%';
        if (percent) percent.textContent = '0%';
        if (status) status.textContent = 'Preparing...';
        if (text) text.textContent = 'Initializing blocking sequence...';
        if (done) done.className = 'blocking-progress-done';
        try {
            const steps = [
                { progress: 25, status: '🔍 Identifying device MAC...', text: 'Locating device on network...' },
                { progress: 50, status: '📡 Sending ARP spoofing packets...', text: 'Disconnecting device from network...' },
                { progress: 75, status: '🔒 Poisoning ARP cache...', text: 'Preventing reconnection...' },
                { progress: 90, status: '💾 Saving block settings...', text: 'Making block permanent...' },
            ];
            for (const step of steps) { await sleep(400); if (bar) bar.style.width = step.progress + '%'; if (percent) percent.textContent = step.progress + '%'; if (status) status.textContent = step.status; if (text) text.textContent = step.text; }
            const response = await fetch('/api/devices/block', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ip, mac, reason: 'Manual block from dashboard', permanent: true }) });
            await sleep(300);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    if (bar) bar.style.width = '100%';
                    if (percent) percent.textContent = '100%';
                    if (status) status.textContent = '✅ Block successful!';
                    if (text) text.textContent = `Device ${ip} is now blocked.`;
                    if (done) { done.className = 'blocking-progress-done show'; done.innerHTML = `✅ Device <strong>${ip}</strong> blocked successfully!<br><span style="color:#445577;font-size:10px;">The device has been disconnected from the network.</span>`; }
                    setTimeout(() => { closeProgress(); refreshDevices(); }, 2500);
                } else { throw new Error(data.message || 'Block failed'); }
            } else { throw new Error('API request failed'); }
        } catch (error) {
            if (bar) bar.style.width = '100%';
            if (percent) percent.textContent = '❌';
            if (status) status.textContent = '❌ Block failed';
            if (text) text.textContent = error.message || 'Unknown error occurred';
            if (done) { done.className = 'blocking-progress-done show'; done.style.borderColor = '#cc4455'; done.style.color = '#cc4455'; done.innerHTML = `❌ Failed to block device: ${error.message}`; }
            setTimeout(closeProgress, 3000);
        }
    }

    function closeProgress() {
        const overlay = document.getElementById('blockingProgressOverlay');
        if (overlay) { overlay.className = 'blocking-progress-overlay'; }
        const done = document.getElementById('blockProgressDone');
        if (done) { done.className = 'blocking-progress-done'; }
    }

    async function unblockDevice(ip) {
        if (!confirm(`Unblock device ${ip}?`)) return;
        const overlay = document.getElementById('blockingProgressOverlay');
        if (overlay) { overlay.className = 'blocking-progress-overlay active'; }
        const bar = document.getElementById('blockingProgressBar');
        const percent = document.getElementById('blockProgressPercent');
        const status = document.getElementById('blockProgressStatus');
        const text = document.getElementById('blockProgressText');
        const done = document.getElementById('blockProgressDone');
        if (bar) bar.style.width = '0%';
        if (percent) percent.textContent = '0%';
        if (status) status.textContent = 'Preparing...';
        if (text) text.textContent = 'Initializing unblock sequence...';
        if (done) done.className = 'blocking-progress-done';
        try {
            await sleep(400);
            if (bar) bar.style.width = '50%';
            if (percent) percent.textContent = '50%';
            if (status) status.textContent = '🔄 Removing ARP spoofing...';
            if (text) text.textContent = 'Restoring network connectivity...';
            const response = await fetch('/api/devices/unblock', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ip }) });
            await sleep(300);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    if (bar) bar.style.width = '100%';
                    if (percent) percent.textContent = '100%';
                    if (status) status.textContent = '✅ Unblock successful!';
                    if (text) text.textContent = `Device ${ip} can now reconnect.`;
                    if (done) { done.className = 'blocking-progress-done show'; done.innerHTML = `✅ Device <strong>${ip}</strong> unblocked successfully!<br><span style="color:#00cc88;">The device can now reconnect.</span>`; }
                    setTimeout(() => { closeProgress(); refreshDevices(); }, 2500);
                } else { throw new Error(data.message || 'Unblock failed'); }
            } else { throw new Error('API request failed'); }
        } catch (error) {
            if (bar) bar.style.width = '100%';
            if (percent) percent.textContent = '❌';
            if (status) status.textContent = '❌ Unblock failed';
            if (text) text.textContent = error.message || 'Unknown error occurred';
            if (done) { done.className = 'blocking-progress-done show'; done.style.borderColor = '#cc4455'; done.style.color = '#cc4455'; done.innerHTML = `❌ Failed to unblock device: ${error.message}`; }
            setTimeout(closeProgress, 3000);
        }
    }

    async function refreshDevices() {
        if (discoveredDevices.length === 0) { scanNetwork(); return; }
        await loadBlockedDevices();
        renderDevices(discoveredDevices);
    }

    async function loadBlockedDevices() {
        try { const response = await fetch('/api/devices/blocked'); if (response.ok) { const data = await response.json(); blockedDevices = data.devices || []; } } catch (error) { console.error('Failed to load blocked devices:', error); }
    }

    function showDeviceInfo(ip) {
        const device = discoveredDevices.find(d => d.ip === ip);
        if (!device) { alert('Device not found'); return; }
        alert(`📡 Device Information\n═══════════════════════════════\nIP: ${device.ip}\nMAC: ${device.mac || 'Unknown'}\nHostname: ${device.hostname || 'Unknown'}\nVendor: ${device.vendor || 'Unknown'}\nStatus: ${device.status || 'Unknown'}\nSelf: ${device.is_self ? '✅ Yes' : 'No'}`);
    }

    async function quickBlockDevice() {
        const ip = document.getElementById('quickBlockIP').value.trim();
        const reason = document.getElementById('quickBlockReason').value.trim() || 'Quick block';
        if (!ip) { alert('Please enter an IP address'); return; }
        const overlay = document.getElementById('warningOverlay');
        if (overlay) { overlay.className = 'warning-overlay active'; }
        document.getElementById('proceedBlockBtn').onclick = function() { closeWarning(); executeBlock(ip, null); };
    }

    async function showBlockedDevices() {
        try {
            const response = await fetch('/api/devices/blocked');
            if (response.ok) {
                const data = await response.json();
                const devices = data.devices || [];
                if (devices.length === 0) { alert('📋 No devices currently blocked'); return; }
                let message = '🚫 BLOCKED DEVICES\n═══════════════════════════════\n\n';
                for (const device of devices) { message += `IP: ${device.ip}\nMAC: ${device.mac || 'Unknown'}\nReason: ${device.reason || 'No reason'}\nBlocked: ${device.timestamp || 'Unknown'}\n─────────────────────────────\n\n`; }
                message += `Total: ${devices.length} device${devices.length !== 1 ? 's' : ''} blocked`;
                alert(message);
            } else { alert('❌ Failed to get blocked devices'); }
        } catch (error) { alert('❌ Error getting blocked devices'); }
    }

    document.addEventListener('DOMContentLoaded', function() {
        loadBlockedDevices();
        setTimeout(scanNetwork, 2000);
    });

    // ============================================================
    // EXISTING QUICK BLOCK FUNCTIONS
    // ============================================================

    async function quickBlock(ip) {
        if (!confirm("Block " + ip + "?")) return;
        showProgress('🚫 BLOCKING IP', '🚫');
        try {
            updateProgress(30, `Blocking IP ${ip}...`);
            const result = await api("/api/firewall/block-ip", "POST", { ip, reason: "Manual block from live connection" });
            if (result && result.success) {
                updateProgress(100, '✅ IP blocked');
                showProgressResult([`✅ IP ${ip} blocked`], true);
                document.getElementById("blockedIPs").textContent = parseInt(document.getElementById("blockedIPs").textContent) + 1;
            } else { showProgressResult(['❌ ' + (result?.message || 'Failed to block IP')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function mapBlockIP() {
        const input = document.getElementById('mapBlockIP');
        const ip = input.value.trim();
        if (!ip) return;
        showProgress('🚫 BLOCKING IP', '🚫');
        try {
            updateProgress(30, `Blocking IP ${ip}...`);
            const result = await api('/api/firewall/block-ip', 'POST', { ip, reason: 'Map block' });
            if (result && result.success) {
                updateProgress(100, '✅ IP blocked');
                showProgressResult([`✅ IP ${ip} blocked`], true);
                input.value = '';
                refreshThreatMap();
            } else { showProgressResult(['❌ ' + (result?.message || 'Failed to block IP')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    async function quickBlockMap(ip) {
        if (!confirm('Block ' + ip + '?')) return;
        showProgress('🚫 BLOCKING IP', '🚫');
        try {
            updateProgress(30, `Blocking IP ${ip}...`);
            const result = await api('/api/firewall/block-ip', 'POST', { ip, reason: 'Quick map block' });
            if (result && result.success) { updateProgress(100, '✅ IP blocked'); showProgressResult([`✅ IP ${ip} blocked`], true); refreshThreatMap(); } 
            else { showProgressResult(['❌ ' + (result?.message || 'Failed to block IP')], false); }
            setTimeout(hideProgress, 2500);
        } catch (error) { showProgressResult(['❌ Error: ' + error.message], false); setTimeout(hideProgress, 2500); }
    }

    // ============================================================
    // SSE STREAM
    // ============================================================

    function connectStream() {
        const eventSource = new EventSource("/api/stream");
        eventSource.onmessage = function(event) {
            try {
                const payload = JSON.parse(event.data);
                if (payload.type === "snapshot") {
                    render(payload.data);
                    saveToCache(payload.data);
                    if (threatMap) loadThreatMapData();
                } else if (payload.type === "alert") {
                    const alert = payload.data;
                    if (alert.severity === 'CRITICAL' || alert.severity === 'HIGH') {
                        const feedList = document.getElementById('mapFeedList');
                        if (feedList) {
                            const item = document.createElement('div');
                            item.className = `map-feed-item ${alert.severity.toLowerCase()}`;
                            item.innerHTML = `<div><span class="time">${alert.timestamp || new Date().toLocaleTimeString()}</span> <span class="severity ${alert.severity.toLowerCase()}">[${alert.severity}]</span> <span class="type">${alert.title || alert.type || 'Alert'}</span></div><div class="message">${alert.message}</div>${alert.data?.ip ? `<div class="ip">📍 ${alert.data.ip}</div>` : ''}`;
                            feedList.prepend(item);
                            while (feedList.children.length > 50) feedList.removeChild(feedList.lastChild);
                            document.getElementById('mapFeedBadge').textContent = feedList.children.length;
                            document.getElementById('mapFeedBadge2').textContent = feedList.children.length;
                        }
                        setTimeout(() => { if (threatMap) loadThreatMapData(); }, 500);
                    }
                } else if (payload.type === "event") {
                    addSIEMEvent(payload.data);
                }
            } catch (error) { console.error('[SSE] Parse error:', error); }
        };
        eventSource.onerror = function() { console.log('[SSE] Connection lost, reconnecting...'); setTimeout(connectStream, 2000); };
        window._eventSource = eventSource;
        return eventSource;
    }

    function startHeartbeat() {
        setInterval(() => { fetch('/api/health', { method: 'GET', headers: { 'Cache-Control': 'no-cache' } }).catch(() => {}); updateCacheAge(); }, 30000);
    }

    function updateNetworkStatus(connected) {
        const dot = document.getElementById('statusDot');
        if (dot) dot.className = 'hacker-status ' + (connected ? 'online' : 'warning');
    }

    function addSIEMEvent(event) {
        const tbody = document.getElementById("events");
        if (!tbody) return;
        const tr = document.createElement("tr");
        const color = { 'CRITICAL': 'red', 'HIGH': 'orange', 'MEDIUM': 'yellow', 'LOW': 'blue' }[event.severity] || 'blue';
        tr.innerHTML = `<td>${esc(event.timestamp || new Date().toLocaleTimeString())}</td><td class="${color}">${esc(event.severity)}</td><td>${esc(event.event_type || 'Unknown')}</td><td>${esc(event.message || '')}</td>`;
        tbody.prepend(tr);
        while (tbody.children.length > 100) tbody.removeChild(tbody.lastChild);
    }

    // ============================================================
    // INITIALIZATION
    // ============================================================

    document.addEventListener('DOMContentLoaded', function() {
        console.log('[Init] Starting dashboard with instant recovery...');
        const cached = loadFromCache();
        if (cached) { console.log('[Init] Rendering cached data instantly...'); render(cached); initThreatMap(); setTimeout(loadThreatMapData, 100); }
        startHeartbeat();
        connectStream();
        setTimeout(async function() {
            try {
                console.log('[Init] Fetching fresh data...');
                const data = await api('/api/snapshot');
                if (data) { render(data); saveToCache(data); if (threatMap) loadThreatMapData(); console.log('[Init] Data updated successfully'); }
            } catch (error) { console.error('[Init] Failed to fetch data:', error); }
        }, 200);
        updateNetworkStatus(true);
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                console.log('[Init] Tab active, refreshing data...');
                setTimeout(async function() {
                    try { const data = await api('/api/snapshot'); if (data) { render(data); saveToCache(data); if (threatMap) loadThreatMapData(); } } catch (error) { console.error('[Init] Refresh error:', error); }
                }, 100);
            }
        });
        window.addEventListener('online', function() { console.log('[Network] Online, reconnecting...'); updateNetworkStatus(true); if (window._eventSource) { window._eventSource.close(); } connectStream(); });
        window.addEventListener('offline', function() { console.log('[Network] Offline'); updateNetworkStatus(false); });
        setInterval(updateCacheAge, 5001);
        console.log('[Init] Dashboard ready with instant recovery!');
    });

    // ============================================================
    // EXPOSE FUNCTIONS
    // ============================================================

    window.blockIP = blockIP;
    window.unblockIP = unblockIP;
    window.blockPort = blockPort;
    window.unblockPort = unblockPort;
    window.killProcess = killProcess;
    window.scanProcesses = scanProcesses;
    window.addIOC = addIOC;
    window.generateMap = generateMap;
    window.browserConnections = browserConnections;
    window.forceRefresh = forceRefresh;
    window.mapBlockIP = mapBlockIP;
    window.quickBlockMap = quickBlockMap;
    window.refreshThreatMap = refreshThreatMap;
    window.initThreatMapOnLoad = initThreatMapOnLoad;
    window.loadThreatMapData = loadThreatMapData;
    window.testSIEMEvents = testSIEMEvents;
    window.testCriticalAlerts = testCriticalAlerts;
    window.testAllEvents = testAllEvents;
    window.updateTestStatus = updateTestStatus;
    window.addTestResult = addTestResult;
    window.quickBlock = quickBlock;
    window.scanNetwork = scanNetwork;
    window.refreshDevices = refreshDevices;
    window.blockDevice = blockDevice;
    window.unblockDevice = unblockDevice;
    window.showBlockedDevices = showBlockedDevices;
    window.quickBlockDevice = quickBlockDevice;
    window.showDeviceInfo = showDeviceInfo;
    window.closeWarning = closeWarning;

</script>
</body>
</html>
"""

# ============================================================
# DEVICE MANAGEMENT API ROUTES
# ============================================================

@app.route("/api/devices/scan", methods=["POST"])
@requires_auth
def api_scan_devices():
    data = request.get_json(silent=True) or {}
    network = data.get("network")
    try:
        devices = device_manager.scan_network(network) if network else device_manager.scan_network()
        return jsonify({"success": True, "count": len(devices), "devices": devices})
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "devices": []}), 500

@app.route("/api/devices")
@requires_auth
def api_get_devices():
    return jsonify({"devices": device_manager.discovered_devices})

@app.route("/api/devices/block", methods=["POST"])
@requires_auth
def api_block_device():
    data = request.get_json(silent=True) or {}
    ip = data.get("ip")
    mac = data.get("mac")
    reason = data.get("reason", "Manual block")
    permanent = data.get("permanent", True)
    if not ip:
        return jsonify({"success": False, "message": "IP address required"})
    result = device_manager.block_device(ip, mac, reason, permanent)
    return jsonify(result)

@app.route("/api/devices/unblock", methods=["POST"])
@requires_auth
def api_unblock_device():
    data = request.get_json(silent=True) or {}
    ip = data.get("ip")
    if not ip:
        return jsonify({"success": False, "message": "IP address required"})
    result = device_manager.unblock_device(ip)
    return jsonify(result)

@app.route("/api/devices/blocked")
@requires_auth
def api_get_blocked_devices():
    return jsonify({"devices": device_manager.get_blocked_devices()})

@app.route("/api/firewall/status")
@requires_auth
def api_firewall_status():
    if ENGINE:
        return jsonify({"blocked_ips": len(ENGINE.firewall.blocked_ips), "blocked_ports": len(ENGINE.firewall.blocked_ports), "rules": len(ENGINE.firewall.rules), "ip_list": list(ENGINE.firewall.blocked_ips)})
    return jsonify({"blocked_ips": 0, "blocked_ports": 0, "rules": 0, "ip_list": []})

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route("/")
@requires_auth
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/snapshot")
@requires_auth
def api_snapshot():
    return jsonify(ENGINE.dashboard_snapshot())

@app.route("/api/alerts")
@requires_auth
def api_alerts():
    limit = int(request.args.get("limit", 100))
    return jsonify(ENGINE.alerts.recent(limit))

@app.route("/api/events", methods=["GET", "POST"])
@requires_auth
def api_events():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        source = data.get("source", "API")
        event_type = data.get("event_type", "unknown")
        severity = data.get("severity", "LOW")
        message = data.get("message", "No message")
        event_data = data.get("data", {})
        ENGINE.broadcast_event(source, event_type, severity, message, event_data)
        return jsonify({"success": True, "message": "Event broadcasted"})
    limit = int(request.args.get("limit", 100))
    return jsonify(ENGINE.siem.recent(limit))

@app.route("/api/connections")
@requires_auth
def api_connections():
    return jsonify(ENGINE.network.snapshot()["connections"])

@app.route("/api/browser-connections")
@requires_auth
def api_browser_connections():
    return jsonify(ENGINE.browser_connections())

@app.route("/api/processes")
@requires_auth
def api_processes():
    return jsonify(ENGINE.endpoint.snapshot())

@app.route("/api/firewall/block-ip", methods=["POST"])
@requires_auth
def api_block_ip():
    data = request.get_json(silent=True) or {}
    ip = str(data.get("ip", "")).strip()
    reason = str(data.get("reason", "Dashboard block"))
    result = ENGINE.firewall.block_ip(ip, reason)
    if result["success"]:
        ENGINE.security_event("Firewall", "IP_BLOCKED", "HIGH", result["message"], {"ip": ip, "reason": reason}, alert=True)
    return jsonify(result)

@app.route("/api/firewall/unblock-ip", methods=["POST"])
@requires_auth
def api_unblock_ip():
    data = request.get_json(silent=True) or {}
    ip = str(data.get("ip", "")).strip()
    result = ENGINE.firewall.unblock_ip(ip)
    if result["success"]:
        ENGINE.security_event("Firewall", "IP_UNBLOCKED", "LOW", result["message"], {"ip": ip}, alert=False)
    return jsonify(result)

@app.route("/api/firewall/block-port", methods=["POST"])
@requires_auth
def api_block_port():
    data = request.get_json(silent=True) or {}
    port = data.get("port")
    result = ENGINE.firewall.block_port(int(port), "Dashboard port block") if valid_port(port) else {"success": False, "message": "Invalid port."}
    if result["success"]:
        ENGINE.security_event("Firewall", "PORT_BLOCKED", "HIGH", result["message"], {"port": int(port)}, alert=True)
    return jsonify(result)

@app.route("/api/firewall/unblock-port", methods=["POST"])
@requires_auth
def api_unblock_port():
    data = request.get_json(silent=True) or {}
    port = data.get("port")
    result = ENGINE.firewall.unblock_port(int(port)) if valid_port(port) else {"success": False, "message": "Invalid port."}
    if result["success"]:
        ENGINE.security_event("Firewall", "PORT_UNBLOCKED", "LOW", result["message"], {"port": int(port)}, alert=False)
    return jsonify(result)

@app.route("/api/process/scan", methods=["POST"])
@requires_auth
def api_process_scan():
    suspicious = ENGINE.endpoint.scan()
    ENGINE.security_event("Endpoint", "MANUAL_PROCESS_SCAN", "LOW", "Manual process scan completed.", {"suspicious": len(suspicious)}, alert=False)
    return jsonify({"success": True, "suspicious": len(suspicious), "results": suspicious})

@app.route("/api/process/terminate", methods=["POST"])
@requires_auth
def api_process_terminate():
    data = request.get_json(silent=True) or {}
    pid = data.get("pid")
    try:
        pid = int(pid)
    except Exception:
        return jsonify({"success": False, "message": "Invalid PID."})
    if pid == os.getpid():
        return jsonify({"success": False, "message": "Refusing to terminate the security dashboard."})
    success, message = ENGINE.endpoint.terminate(pid)
    if success:
        ENGINE.security_event("Endpoint", "PROCESS_TERMINATED", "HIGH", message, {"pid": pid}, alert=True)
    return jsonify({"success": success, "message": message})

@app.route("/api/ioc/add", methods=["POST"])
@requires_auth
def api_ioc_add():
    data = request.get_json(silent=True) or {}
    ip = str(data.get("ip", "")).strip()
    description = str(data.get("description", "Custom threat indicator"))
    if not ENGINE.threats.add(ip, description):
        return jsonify({"success": False, "message": "Invalid IP address."})
    ENGINE.security_event("Threat Intelligence", "IOC_ADDED", "MEDIUM", f"Added IOC {ip}", {"ip": ip, "description": description}, alert=False)
    return jsonify({"success": True, "message": f"Added threat IOC {ip}."})

@app.route("/api/ioc/remove", methods=["POST"])
@requires_auth
def api_ioc_remove():
    data = request.get_json(silent=True) or {}
    ip = str(data.get("ip", "")).strip()
    success = ENGINE.threats.remove(ip)
    return jsonify({"success": success, "message": f"Removed {ip}." if success else f"{ip} was not found."})

@app.route("/api/dns")
@requires_auth
def api_dns():
    ip = request.args.get("ip", "").strip()
    if not valid_ip(ip):
        return jsonify({"success": False, "message": "Invalid IP."})
    hostname = ENGINE.intelligence.reverse_dns(ip)
    return jsonify({"success": True, "ip": ip, "hostname": hostname})

@app.route("/api/geolocate")
@requires_auth
def api_geolocate():
    ip = request.args.get("ip", "").strip()
    if not valid_ip(ip):
        return jsonify({"success": False, "message": "Invalid IP."})
    return jsonify(ENGINE.intelligence.geolocate(ip))

@app.route("/api/threat-map", methods=["POST"])
@requires_auth
def api_threat_map():
    return jsonify(ENGINE.generate_threat_map())

@app.route("/maps/<path:filename>")
@requires_auth
def map_file(filename):
    from flask import send_from_directory
    return send_from_directory(str(ENGINE.maps), filename)

@app.route("/api/stream")
@requires_auth
def api_stream():
    q = ENGINE.subscribe()
    def generate():
        try:
            while ENGINE.running:
                try:
                    payload = q.get(timeout=15)
                    yield "data: " + json.dumps(payload, default=str) + "\n\n"
                except queue.Empty:
                    yield ": heartbeat\n\n"
        finally:
            ENGINE.unsubscribe(q)
    return Response(generate(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"})

@app.route("/api/health")
def api_health():
    return jsonify({"status": "running", "time": now_iso(), "hostname": socket.gethostname(), "platform": platform.platform(), "psutil": psutil.__version__})

# ============================================================
# STARTUP
# ============================================================
import logging
import sys

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

cli = sys.modules.get('flask.cli')
if cli:
    cli.show_server_banner = lambda *args: None
    
def main():
    global ENGINE

    parser = argparse.ArgumentParser(description="Network Security Real-Time Monitoring System")
    parser.add_argument("--workspace", "-w", default="~/network_security_workspace", help="Workspace directory")
    parser.add_argument("--host", default="0.0.0.0", help="Dashboard bind address")
    parser.add_argument("--port", type=int, default=5001, help="Dashboard port")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    args = parser.parse_args()

    print()
    print("=" * 70)
    print("NETWORK SECURITY REAL-TIME MONITOR")
    print("=" * 70)
    print(f"Host:       {socket.gethostname()}")
    print(f"Platform:   {platform.platform()}")
    print(f"PID:        {os.getpid()}")
    print(f"Workspace:  {Path(args.workspace).expanduser().resolve()}")
    print()

    ENGINE = SecurityEngine(args.workspace)
    worker = threading.Thread(target=ENGINE.run, daemon=True, name="security-monitor")
    worker.start()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    url = f"http://{args.host if args.host != '0.0.0.0' else local_ip}:{args.port}"
    print(f"Dashboard:  {url}")
    print(f"Local:      http://127.0.0.1:{args.port}")

    if args.host == "0.0.0.0":
        print(f"\n📡 ACCESS FROM OTHER DEVICES:")
        print(f"   http://{local_ip}:{args.port}")
        print(f"\n⚠️  SECURITY WARNING: Anyone on your network can access this!")

    print()
    print("REAL-TIME DATA SOURCES:")
    print("  [+] psutil network counters")
    print("  [+] psutil TCP/UDP connections")
    print("  [+] psutil process telemetry")
    print("  [+] OS firewall")
    print("  [+] local DNS")
    print("  [+] public IP geolocation")
    print()

    if platform.system() == "Windows":
        print("NOTE: Run as Administrator for firewall/process controls.")
    elif platform.system() == "Linux":
        if os.geteuid() != 0:
            print("NOTE: Not running as root. Some network/firewall/process information may be restricted.")
    print()

    if not args.no_browser:
        try:
            threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{args.port}")).start()
        except Exception:
            pass

    try:
        app.run(host=args.host, port=args.port, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        if ENGINE:
            ENGINE.stop()
        print("\nNetwork Security System stopped.")

if __name__ == "__main__":
    main()