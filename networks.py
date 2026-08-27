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

python network_security_realtime.py

Dashboard
---------

http://127.0.0.1:5000

Production note
---------------

Do NOT expose this dashboard directly to the Internet.
It provides security-sensitive controls such as firewall
blocking and process termination.

Linux:
    Run with appropriate privileges for firewall operations.

    Windows:
        Run as Administrator for firewall operations.
        """

from __future__ import annotations

import argparse
import collections
import datetime
import ipaddress
import json
import os
import platform
import queue
import shutil
import signal
import socket
import subprocess
import threading
import time
import webbrowser
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
# CONFIGURATION
# ============================================================

HOST = "127.0.0.1"
PORT = 5000

MAX_HISTORY = 500
EVENT_HISTORY = 1000
SCAN_INTERVAL = 5
CONNECTION_INTERVAL = 2
BANDWIDTH_INTERVAL = 1

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


def run_command(
    command: List[str],
    timeout: int = 10
) -> Tuple[bool, str]:

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        output = (
            result.stdout.strip()
            or result.stderr.strip()
        )

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

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._load()

    def _load(self):

        if not self.path.exists():
            return

        try:

            with self.path.open(
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

                if isinstance(data, list):
                    self.events = data[-EVENT_HISTORY:]

        except Exception:
            self.events = []

    def append(self, event: SecurityEvent):

        data = asdict(event)

        with self.lock:

            self.events.append(data)

            self.events = self.events[
                -EVENT_HISTORY:
            ]

            try:

                with self.path.open(
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        self.events,
                        f,
                        indent=2,
                        default=str,
                    )

            except Exception:
                pass

def recent(
    self,
    limit: int = 100
) -> List[Dict[str, Any]]:

    with self.lock:
        return list(
    self.events[-limit:]
)


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

        # --------------------------------------------------------
        # Public API
        # --------------------------------------------------------

def block_ip(
    self,
    ip: str,
    reason: str = "Manual block"
) -> Dict[str, Any]:

    if not valid_ip(ip):

        return {
    "success": False,
    "message": "Invalid IP address."
}

with self.lock:

    if ip in self.blocked_ips:

        return {
    "success": False,
    "message": f"{ip} is already blocked."
}

success, message = (
    self._system_block_ip(ip)
)

if not success:

    return {
"success": False,
"message": message
}

self.blocked_ips.add(ip)

rule = {
    "type": "IP",
    "value": ip,
    "action": "BLOCK",
    "reason": reason,
    "created": now_iso(),
}

self.rules.append(rule)

return {
"success": True,
"message": f"Blocked IP {ip}.",
"rule": rule,
}

def unblock_ip(
    self,
    ip: str
) -> Dict[str, Any]:

    with self.lock:

        success, message = (
            self._system_unblock_ip(ip)
        )

        if not success:

            return {
        "success": False,
        "message": message
    }

    self.blocked_ips.discard(ip)

    self.rules = [
        r for r in self.rules
        if not (
            r["type"] == "IP"
            and r["value"] == ip
        )
    ]

    return {
        "success": True,
        "message": f"Unblocked IP {ip}."
    }

def block_port(
    self,
    port: int,
    reason: str = "Manual port block"
) -> Dict[str, Any]:

    if not valid_port(port):

        return {
    "success": False,
    "message": "Invalid port."
}

port = int(port)

with self.lock:

    if port in self.blocked_ports:

        return {
    "success": False,
    "message": f"Port {port} is already blocked."
}

success, message = (
    self._system_block_port(port)
)

if not success:

    return {
"success": False,
"message": message
}

self.blocked_ports.add(port)

rule = {
    "type": "PORT",
    "value": port,
    "action": "BLOCK",
    "reason": reason,
    "created": now_iso(),
}

self.rules.append(rule)

return {
"success": True,
"message": f"Blocked port {port}.",
"rule": rule,
}

def unblock_port(
    self,
    port: int
) -> Dict[str, Any]:

    if not valid_port(port):

        return {
    "success": False,
    "message": "Invalid port."
}

port = int(port)

with self.lock:

    success, message = (
        self._system_unblock_port(port)
    )

    if not success:

        return {
    "success": False,
    "message": message
}

self.blocked_ports.discard(port)

self.rules = [
    r for r in self.rules
    if not (
        r["type"] == "PORT"
        and r["value"] == port
    )
]

return {
    "success": True,
    "message": f"Unblocked port {port}."
}

# --------------------------------------------------------
# Firewall state
# --------------------------------------------------------

def is_blocked(
    self,
    remote_ip: str,
    remote_port: int
) -> bool:

    return (
remote_ip in self.blocked_ips
or remote_port in self.blocked_ports
)

# --------------------------------------------------------
# Windows
# --------------------------------------------------------

def _windows_add_rule(
    self,
    name: str,
    direction: str,
    remote_ip: Optional[str] = None,
    port: Optional[int] = None
) -> Tuple[bool, str]:

    command = [
        "netsh",
        "advfirewall",
        "firewall",
        "add",
        "rule",
        f"name={name}",
        f"dir={direction}",
        "action=block",
        "profile=any",
    ]

    if remote_ip:
        command.append(
            f"remoteip={remote_ip}"
        )

        if port:
            command.extend([
                "protocol=TCP",
                f"remoteport={port}",
            ])

            return run_command(command)

def _windows_delete_rule(
    self,
    name: str
) -> Tuple[bool, str]:

    return run_command([
"netsh",
"advfirewall",
"firewall",
"delete",
"rule",
f"name={name}",
])

# --------------------------------------------------------
# Linux nftables / iptables
# --------------------------------------------------------

def _linux_add_ip(
    self,
    ip: str
) -> Tuple[bool, str]:

    if shutil.which("nft"):

        ok, msg = run_command([
            "nft",
            "add",
            "rule",
            "inet",
            "filter",
            "input",
            "ip",
            "saddr",
            ip,
            "drop",
        ])

        if ok:
            return True, msg

        if shutil.which("iptables"):

            ok, msg = run_command([
                "iptables",
                "-A",
                "INPUT",
                "-s",
                ip,
                "-j",
                "DROP",
            ])

            if ok:
                return True, msg

            return (
            False,
            "No usable Linux firewall command "
            "or insufficient privileges."
        )

def _linux_delete_ip(
    self,
    ip: str
) -> Tuple[bool, str]:

    if shutil.which("iptables"):

        ok, msg = run_command([
            "iptables",
            "-D",
            "INPUT",
            "-s",
            ip,
            "-j",
            "DROP",
        ])

        if ok:
            return True, msg

        return (
        False,
        "Unable to remove Linux firewall rule."
    )

def _linux_add_port(
    self,
    port: int
) -> Tuple[bool, str]:

    if shutil.which("iptables"):

        ok, msg = run_command([
            "iptables",
            "-A",
            "INPUT",
            "-p",
            "tcp",
            "--dport",
            str(port),
            "-j",
            "DROP",
        ])

        if ok:
            return True, msg

        return (
        False,
        "iptables unavailable or insufficient privileges."
    )

def _linux_delete_port(
    self,
    port: int
) -> Tuple[bool, str]:

    if shutil.which("iptables"):

        ok, msg = run_command([
            "iptables",
            "-D",
            "INPUT",
            "-p",
            "tcp",
            "--dport",
            str(port),
            "-j",
            "DROP",
        ])

        if ok:
            return True, msg

        return (
        False,
        "Unable to remove port rule."
    )

    # --------------------------------------------------------
    # Platform firewall
    # --------------------------------------------------------

def _system_block_ip(
    self,
    ip: str
) -> Tuple[bool, str]:

    system = platform.system()

    if system == "Windows":

        ok1, msg1 = (
            self._windows_add_rule(
                f"NSRM_IN_IP_{ip}",
                "in",
                remote_ip=ip,
            )
        )

        ok2, msg2 = (
            self._windows_add_rule(
                f"NSRM_OUT_IP_{ip}",
                "out",
                remote_ip=ip,
            )
        )

        if ok1 and ok2:
            return True, "Windows firewall rule added."

        return False, msg1 or msg2

        if system == "Linux":
            return self._linux_add_ip(ip)

        if system == "Darwin":

            # macOS firewall does not provide the same
            # per-IP blocking interface through the standard
            # application firewall.
            return (
        False,
        "Per-IP firewall control is not implemented "
        "for macOS in this version."
    )

    return False, f"Unsupported OS: {system}"

def _system_unblock_ip(
    self,
    ip: str
) -> Tuple[bool, str]:

    system = platform.system()

    if system == "Windows":

        self._windows_delete_rule(
            f"NSRM_IN_IP_{ip}"
        )

        self._windows_delete_rule(
            f"NSRM_OUT_IP_{ip}"
        )

        return True, "Windows firewall rules removed."

    if system == "Linux":
        return self._linux_delete_ip(ip)

    return (
    False,
    f"Unsupported OS: {system}"
)

def _system_block_port(
    self,
    port: int
) -> Tuple[bool, str]:

    system = platform.system()

    if system == "Windows":

        ok1, msg1 = (
            self._windows_add_rule(
                f"NSRM_IN_PORT_{port}",
                "in",
                port=port,
            )
        )

        ok2, msg2 = (
            self._windows_add_rule(
                f"NSRM_OUT_PORT_{port}",
                "out",
                port=port,
            )
        )

        if ok1 and ok2:
            return True, "Windows port rules added."

        return False, msg1 or msg2

        if system == "Linux":
            return self._linux_add_port(port)

        return (
        False,
        f"Port blocking unsupported on {system}."
    )

def _system_unblock_port(
    self,
    port: int
) -> Tuple[bool, str]:

    system = platform.system()

    if system == "Windows":

        self._windows_delete_rule(
            f"NSRM_IN_PORT_{port}"
        )

        self._windows_delete_rule(
            f"NSRM_OUT_PORT_{port}"
        )

        return True, "Windows port rules removed."

    if system == "Linux":
        return self._linux_delete_port(port)

    return (
    False,
    f"Port unblocking unsupported on {system}."
)

    def _load_existing_rules(self):
        """
        We intentionally do not blindly import all existing
        system firewall rules because they may belong to other
        applications.
        """

        self.blocked_ips = set()
        self.blocked_ports = set()

    def stats(self) -> Dict[str, Any]:

        return {
    "blocked_ips": len(
        self.blocked_ips
    ),
    "blocked_ports": len(
        self.blocked_ports
    ),
    "rules": len(
        self.rules
    ),
}


# ============================================================
# THREAT INTELLIGENCE
# ============================================================

class ThreatIntelligence:

    def __init__(self):

        self.lock = threading.Lock()

        self.indicators = dict(
            DEFAULT_THREAT_INTELLIGENCE
        )

def add(
    self,
    ip: str,
    description: str
) -> bool:

    if not valid_ip(ip):
        return False

    with self.lock:
        self.indicators[ip] = description

        return True

def remove(
    self,
    ip: str
) -> bool:

    with self.lock:

        if ip not in self.indicators:
            return False

        del self.indicators[ip]

        return True

def lookup(
    self,
    ip: str
) -> Optional[str]:

    with self.lock:
        return self.indicators.get(ip)

    def all(self) -> Dict[str, str]:

        with self.lock:
            return dict(self.indicators)


        # ============================================================
        # IDS / IPS
        # ============================================================

class IDSIPS:

def __init__(
    self,
    threat_intelligence: ThreatIntelligence
):

    self.threat_intelligence = (
        threat_intelligence
    )

    self.alerts: List[Dict[str, Any]] = []

    self.connection_history = (
        collections.defaultdict(list)
    )

    self.lock = threading.Lock()

def analyze(
    self,
    connection: Dict[str, Any]
) -> Optional[Dict[str, Any]]:

    remote_ip = connection.get(
        "remote_ip"
    )

    remote_port = int(
        connection.get(
            "remote_port",
            0
        ) or 0
    )

    process = str(
        connection.get(
            "process",
            ""
        )
    ).lower()

    # ----------------------------------------------------
    # Known IOC
    # ----------------------------------------------------

    threat = self.threat_intelligence.lookup(
        remote_ip
    )

    if threat:

        return self._alert(
    "KNOWN_THREAT",
    "CRITICAL",
    (
        f"Connection to threat IOC: "
        f"{threat}"
    ),
    connection,
)

# ----------------------------------------------------
# C2 ports
# ----------------------------------------------------

if remote_port in C2_PORTS:

    return self._alert(
"POSSIBLE_C2",
"HIGH",
(
    f"Connection using suspicious "
    f"C2 port {remote_port}"
),
connection,
)

# ----------------------------------------------------
# Suspicious process
# ----------------------------------------------------

for term in SUSPICIOUS_PROCESS_TERMS:

    if term in process:

        return self._alert(
    "SUSPICIOUS_PROCESS",
    "HIGH",
    (
        f"Suspicious process name: "
        f"{process}"
    ),
    connection,
)

# ----------------------------------------------------
# Port scan
# ----------------------------------------------------

local_ip = connection.get(
    "local_ip"
)

if local_ip and remote_port:

    now = time.time()

    with self.lock:

        history = (
            self.connection_history[
                local_ip
            ]
        )

        history.append(
            (now, remote_port)
        )

        cutoff = now - 60

        self.connection_history[
            local_ip
        ] = [
            item
            for item in history
            if item[0] >= cutoff
        ]

        unique_ports = {
            port
            for _, port in
            self.connection_history[
                local_ip
            ]
        }

        if len(unique_ports) >= 15:

            return self._alert(
        "PORT_SCAN",
        "MEDIUM",
        (
            f"Possible port scan "
            f"from {local_ip}"
        ),
        connection,
    )

    return None

def _alert(
    self,
    alert_type: str,
    severity: str,
    message: str,
    connection: Dict[str, Any]
) -> Dict[str, Any]:

    alert = {
        "timestamp": now_iso(),
        "type": alert_type,
        "severity": severity,
        "message": message,
        "connection": dict(connection),
    }

    with self.lock:

        self.alerts.append(alert)

        trim(
            self.alerts,
            MAX_HISTORY
        )

        return alert

def recent(
    self,
    limit: int = 100
) -> List[Dict[str, Any]]:

    with self.lock:
        return list(
    self.alerts[-limit:]
)


# ============================================================
# SIEM
# ============================================================

class SIEM:

def __init__(
    self,
    store: EventStore
):

    self.store = store

    self.events: List[
        SecurityEvent
    ] = []

    self.correlations = []

    self.lock = threading.Lock()

def log(
    self,
    source: str,
    event_type: str,
    severity: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> SecurityEvent:

    event = SecurityEvent(
        timestamp=now_iso(),
        source=source,
        event_type=event_type,
        severity=severity,
        message=message,
        data=data or {},
    )

    with self.lock:

        self.events.append(event)

        trim(
            self.events,
            EVENT_HISTORY
        )

        self.store.append(event)

        self._correlate(event)

        return event

def _correlate(
    self,
    event: SecurityEvent
):

    # ----------------------------------------------------
    # Brute force
    # ----------------------------------------------------

    if event.event_type == "failed_login":

        source_ip = event.data.get(
            "source_ip"
        )

        with self.lock:

            recent = [
                e
                for e in self.events[-50:]
                if (
                    e.event_type
                    == "failed_login"
                    and e.data.get(
                        "source_ip"
                    ) == source_ip
                )
            ]

            if len(recent) >= 5:

                self.correlations.append({
                    "timestamp": now_iso(),
                    "type": "BRUTE_FORCE",
                    "severity": "HIGH",
                    "message": (
                        f"Possible brute-force "
                        f"attack from {source_ip}"
                    ),
                })

                # ----------------------------------------------------
                # Network scan
                # ----------------------------------------------------

                if event.event_type == "connection_attempt":

                    source_ip = event.data.get(
                        "source_ip"
                    )

                    with self.lock:

                        recent = [
                            e
                            for e in self.events[-100:]
                            if (
                                e.event_type
                                == "connection_attempt"
                                and e.data.get(
                                    "source_ip"
                                ) == source_ip
                            )
                        ]

                        ports = {
                            e.data.get("port")
                            for e in recent
                            if e.data.get("port")
                        }

                        if len(ports) >= 10:

                            self.correlations.append({
                                "timestamp": now_iso(),
                                "type": "PORT_SCAN",
                                "severity": "MEDIUM",
                                "message": (
                                    f"Possible port scan "
                                    f"from {source_ip}"
                                ),
                            })

                            trim(
                                self.correlations,
                                MAX_HISTORY
                            )

def recent(
    self,
    limit: int = 100
) -> List[Dict[str, Any]]:

    with self.lock:

        return [
    asdict(e)
    for e in self.events[-limit:]
]

    def stats(self) -> Dict[str, Any]:

        with self.lock:

            counts = collections.Counter(
                e.severity
                for e in self.events
            )

            return {
                "total": len(self.events),
                "critical": counts["CRITICAL"],
                "high": counts["HIGH"],
                "medium": counts["MEDIUM"],
                "low": counts["LOW"],
                "correlations": len(
                    self.correlations
                ),
            }


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

        self.protocol_stats = (
            collections.Counter()
        )

        self.last_update = None

    def update_bandwidth(self):

        current = psutil.net_io_counters()
        current_time = time.monotonic()

        with self.lock:

            if (
                self.prev_io is not None
                and self.prev_time is not None
            ):

                elapsed = (
                    current_time
                    - self.prev_time
                )

                if elapsed <= 0:
                    elapsed = 1

                    sent = max(
                        0,
                        current.bytes_sent
                        - self.prev_io.bytes_sent
                    )

                    recv = max(
                        0,
                        current.bytes_recv
                        - self.prev_io.bytes_recv
                    )

                    self.upload_kbps = (
                        sent / 1024 / elapsed
                    )

                    self.download_kbps = (
                        recv / 1024 / elapsed
                    )

                    self.bandwidth_history.append({
                        "timestamp": now_iso(),
                        "upload_kbps":
                            round(
                                self.upload_kbps,
                                2
                            ),
                            "download_kbps":
                                round(
                                    self.download_kbps,
                                    2
                                ),
                            })

                            trim(
                                self.bandwidth_history
                            )

                            self.prev_io = current
                            self.prev_time = current_time
                            self.last_update = now_iso()

    def update_connections(self):

        result = []

        protocol_counts = (
            collections.Counter()
        )

        try:

            connections = (
                psutil.net_connections(
                    kind="inet"
                )
            )

        except Exception:

            connections = []

            for conn in connections:

                local_ip = (
                    conn.laddr.ip
                    if conn.laddr
                    else None
                )

                local_port = (
                    conn.laddr.port
                    if conn.laddr
                    else None
                )

                remote_ip = (
                    conn.raddr.ip
                    if conn.raddr
                    else None
                )

                remote_port = (
                    conn.raddr.port
                    if conn.raddr
                    else None
                )

                process = safe_process_name(
                    conn.pid
                )

                item = {
                    "pid": conn.pid,
                    "process": process,
                    "status": conn.status,
                    "local_ip": local_ip,
                    "local_port": local_port,
                    "remote_ip": remote_ip,
                    "remote_port": remote_port,
                }

                result.append(item)

                if remote_port:

                    protocol_counts[
                        self.service_for_port(
                            remote_port
                        )
                    ] += 1

                    with self.lock:

                        self.connections = result

                        self.protocol_stats = (
                            protocol_counts
                        )

    @staticmethod
    def service_for_port(
        port: int
    ) -> str:

        services = {
            20: "FTP",
            21: "FTP",
            22: "SSH",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            465: "SMTPS",
            587: "SMTP",
            993: "IMAPS",
            995: "POP3S",
            3306: "MYSQL",
            5432: "POSTGRES",
            6379: "REDIS",
            8080: "HTTP",
            8443: "HTTPS",
        }

        return services.get(
    port,
    "OTHER"
)

    def snapshot(self) -> Dict[str, Any]:

        with self.lock:

            return {
        "upload_kbps":
            round(
                self.upload_kbps,
                2
            ),
            "download_kbps":
                round(
                    self.download_kbps,
                    2
                ),
                "connections":
                    list(self.connections),
                    "protocol_stats":
                        dict(
                            self.protocol_stats
                        ),
                        "bandwidth_history":
                            list(
                                self.bandwidth_history[
                                    -60:
                                    ]
                                ),
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

        for proc in psutil.process_iter([
            "pid",
            "name",
            "username",
            "status",
            "cpu_percent",
            "memory_percent",
            "create_time",
        ]):

            try:

                info = proc.info

                pid = info.get("pid")
                name = (
                    info.get("name")
                    or "Unknown"
                )

                item = {
                    "pid": pid,
                    "name": name,
                    "username":
                        info.get(
                            "username"
                        ),
                        "status":
                            info.get(
                                "status"
                            ),
                            "cpu_percent":
                                round(
                                    float(
                                        info.get(
                                            "cpu_percent"
                                        ) or 0
                                    ),
                                    2
                                ),
                                "memory_percent":
                                    round(
                                        float(
                                            info.get(
                                                "memory_percent"
                                            ) or 0
                                        ),
                                        2
                                    ),
                                }

                                processes.append(item)

                                lower = name.lower()

                                for term in (
                                    SUSPICIOUS_PROCESS_TERMS
                                ):

                                    if term in lower:

                                        suspicious.append({
                                            **item,
                                            "reason":
                                                f"Process name contains "
                                                f"'{term}'",
                                            })

                                            break

                                        if (
                                            item["memory_percent"]
                                            > 50
                                        ):

                                            suspicious.append({
                                                **item,
                                                "reason":
                                                    "Very high memory usage",
                                                })

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

        except Exception:
            continue

        processes.sort(
            key=lambda x:
                x["cpu_percent"],
                reverse=True
            )

            with self.lock:

                self.processes = processes
                self.suspicious = suspicious
                self.last_scan = now_iso()

                return suspicious

def terminate(
    self,
    pid: int
) -> Tuple[bool, str]:

    try:

        process = psutil.Process(
            int(pid)
        )

        name = process.name()

        process.terminate()

        try:

            process.wait(
                timeout=3
            )

        except psutil.TimeoutExpired:

            process.kill()

            return (
        True,
        f"Process {name} ({pid}) terminated."
    )

    except psutil.NoSuchProcess:

        return (
    False,
    "Process does not exist."
)

except psutil.AccessDenied:

    return (
False,
"Access denied."
)

except Exception as exc:

    return (
False,
str(exc)
)

    def snapshot(self):

        with self.lock:

            return {
        "processes":
            list(
                self.processes
            ),
            "suspicious":
                list(
                    self.suspicious
                ),
                "last_scan":
                    self.last_scan,
                }


                # ============================================================
                # DNS / GEOLOCATION
                # ============================================================

class NetworkIntelligence:

    def __init__(self):

        self.dns_cache = {}
        self.geo_cache = {}

        self.lock = threading.Lock()

def reverse_dns(
    self,
    ip: str
) -> str:

    if not valid_ip(ip):
        return ""

    with self.lock:

        if ip in self.dns_cache:
            return self.dns_cache[ip]

        try:

            hostname = socket.gethostbyaddr(
                ip
            )[0]

        except Exception:

            hostname = ""

            with self.lock:
                self.dns_cache[ip] = hostname

                return hostname

def geolocate(
    self,
    ip: str
) -> Dict[str, Any]:

    if not is_public_ip(ip):
        return {}

    with self.lock:

        if ip in self.geo_cache:
            return self.geo_cache[ip]

        try:

            response = requests.get(
                f"https://ipapi.co/{ip}/json/",
                timeout=4,
            )

            if not response.ok:
                return {}

            data = response.json()

            result = {
                "ip": ip,
                "city": data.get(
                    "city"
                ),
                "region": data.get(
                    "region"
                ),
                "country": data.get(
                    "country_name"
                ),
                "latitude": data.get(
                    "latitude"
                ),
                "longitude": data.get(
                    "longitude"
                ),
                "org": data.get(
                    "org"
                ),
                "asn": data.get(
                    "asn"
                ),
            }

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

def add(
    self,
    severity: str,
    title: str,
    message: str,
    source: str
) -> Dict[str, Any]:

    severity = severity.upper()

    with self.lock:

        self.sequence += 1

        alert = {
            "id":
                self.sequence,
                "timestamp":
                    now_iso(),
                    "severity":
                        severity,
                        "title":
                            title,
                            "message":
                                message,
                                "source":
                                    source,
                                    "status":
                                        "ACTIVE",
                                    }

                                    self.alerts.append(alert)

                                    trim(
                                        self.alerts,
                                        MAX_HISTORY
                                    )

                                    return alert

def acknowledge(
    self,
    alert_id: int
) -> bool:

    with self.lock:

        for alert in self.alerts:

            if alert["id"] == alert_id:

                alert[
                    "status"
                ] = "ACKNOWLEDGED"

                return True

            return False

def recent(
    self,
    limit: int = 100
):

    with self.lock:
        return list(
    self.alerts[-limit:]
)

    def stats(self):

        with self.lock:

            counter = collections.Counter(
                a["severity"]
                for a in self.alerts
            )

            return {
                "total":
                    len(self.alerts),
                    "critical":
                        counter["CRITICAL"],
                        "high":
                            counter["HIGH"],
                            "medium":
                                counter["MEDIUM"],
                                "low":
                                    counter["LOW"],
                                    "active":
                                        sum(
                                            a["status"]
                                            == "ACTIVE"
                                            for a in self.alerts
                                        ),
                                    }


                                    # ============================================================
                                    # MAIN SECURITY ENGINE
                                    # ============================================================

class SecurityEngine:

def __init__(
    self,
    workspace: str
):

    self.workspace = Path(
        workspace
    ).expanduser().resolve()

    self.workspace.mkdir(
        parents=True,
        exist_ok=True
    )

    self.reports = (
        self.workspace
        / "network_reports"
    )

    self.maps = (
        self.reports
        / "threat_maps"
    )

    self.reports.mkdir(
        parents=True,
        exist_ok=True
    )

    self.maps.mkdir(
        parents=True,
        exist_ok=True
    )

    self.store = EventStore(
        self.reports
        / "siem_events.json"
    )

    self.threats = (
        ThreatIntelligence()
    )

    self.firewall = Firewall()

    self.ids = IDSIPS(
        self.threats
    )

    self.siem = SIEM(
        self.store
    )

    self.network = (
        NetworkMonitor()
    )

    self.endpoint = (
        EndpointMonitor()
    )

    self.intelligence = (
        NetworkIntelligence()
    )

    self.alerts = AlertManager()

    self.running = True

    self.last_connection_scan = 0
    self.last_process_scan = 0

    self.alert_cache = set()

    self.clients = []

    self.client_lock = (
        threading.Lock()
    )

    # ========================================================
    # EVENT BROADCAST
    # ========================================================

def broadcast(
    self,
    payload: Dict[str, Any]
):

    with self.client_lock:

        dead = []

        for client in self.clients:

            try:
                client.put_nowait(
                    payload
                )

            except Exception:
                dead.append(client)

                for client in dead:

                    if client in self.clients:
                        self.clients.remove(
                            client
                        )

    def subscribe(self):

        q = queue.Queue(
            maxsize=50
        )

        with self.client_lock:
            self.clients.append(q)

            return q

    def unsubscribe(self, q):

        with self.client_lock:

            if q in self.clients:
                self.clients.remove(q)

                # ========================================================
                # LOG SECURITY EVENT
                # ========================================================

def security_event(
    self,
    source: str,
    event_type: str,
    severity: str,
    message: str,
    data=None,
    alert=False
):

    event = self.siem.log(
        source,
        event_type,
        severity,
        message,
        data or {},
    )

    if alert:

        security_alert = (
            self.alerts.add(
                severity,
                event_type,
                message,
                source,
            )
        )

        self.broadcast({
            "type":
                "alert",
                "data":
                    security_alert,
                })

                self.broadcast({
                    "type":
                        "event",
                        "data":
                            asdict(event),
                        })

                        # ========================================================
                        # CONNECTION ANALYSIS
                        # ========================================================

    def analyze_connections(self):

        snapshot = self.network.snapshot()

        for connection in snapshot[
            "connections"
        ]:

            if (
                connection["status"]
                != "ESTABLISHED"
            ):
                continue

            remote_ip = connection.get(
                "remote_ip"
            )

            if not remote_ip:
                continue

            detection = self.ids.analyze(
                connection
            )

            if detection:

                fingerprint = (
                    detection["type"],
                    remote_ip,
                    connection.get(
                        "remote_port"
                    ),
                    connection.get(
                        "pid"
                    ),
                )

                if fingerprint not in self.alert_cache:

                    self.alert_cache.add(
                        fingerprint
                    )

                    self.security_event(
                        "IDS/IPS",
                        detection["type"],
                        detection["severity"],
                        detection["message"],
                        detection[
                            "connection"
                        ],
                        alert=True,
                    )

                    # ------------------------------------------------
                    # Reactive IPS
                    # ------------------------------------------------

                    if detection[
                        "severity"
                    ] in {
                        "CRITICAL",
                        "HIGH",
                    }:

                        result = (
                            self.firewall.block_ip(
                                remote_ip,
                                (
                                    "Automatic IDS/IPS "
                                    f"detection: "
                                    f"{detection['type']}"
                                )
                            )
                        )

                        if result["success"]:

                            self.security_event(
                                "Firewall",
                                "AUTO_BLOCK",
                                "HIGH",
                                result["message"],
                                {
                                    "ip":
                                        remote_ip,
                                        "reason":
                                            detection[
                                                "message"
                                            ],
                                        },
                                        alert=True,
                                    )

                                    # ========================================================
                                    # PROCESS SCAN
                                    # ========================================================

    def process_scan(self):

        suspicious = (
            self.endpoint.scan()
        )

        for process in suspicious:

            key = (
                "PROCESS",
                process.get("pid"),
                process.get("reason"),
            )

            if key in self.alert_cache:
                continue

            self.alert_cache.add(key)

            self.security_event(
                "Endpoint",
                "SUSPICIOUS_PROCESS",
                "HIGH",
                (
                    f"{process['name']} "
                    f"(PID {process['pid']}): "
                    f"{process['reason']}"
                ),
                process,
                alert=True,
            )

            # ========================================================
            # LIVE UPDATE
            # ========================================================

    def update(self):

        now = time.monotonic()

        self.network.update_bandwidth()

        if (
            now - self.last_connection_scan
            >= CONNECTION_INTERVAL
        ):

            self.network.update_connections()

            self.analyze_connections()

            self.last_connection_scan = now

            if (
                now - self.last_process_scan
                >= SCAN_INTERVAL
            ):

                self.process_scan()

                self.last_process_scan = now

                self.broadcast({
                    "type":
                        "snapshot",
                        "data":
                            self.dashboard_snapshot(),
                        })

                        # ========================================================
                        # SNAPSHOT
                        # ========================================================

    def dashboard_snapshot(self):

        network = (
            self.network.snapshot()
        )

        endpoint = (
            self.endpoint.snapshot()
        )

        alerts = (
            self.alerts.stats()
        )

        firewall = (
            self.firewall.stats()
        )

        siem = (
            self.siem.stats()
        )

        connections = []

        for connection in network[
            "connections"
        ]:

            item = dict(
                connection
            )

            remote = (
                item.get(
                    "remote_ip"
                )
            )

            port = (
                item.get(
                    "remote_port"
                )
            )

            item["blocked"] = (
                self.firewall.is_blocked(
                    remote,
                    port or 0
                )
            )

            item["dns"] = ""

            connections.append(item)

            return {
        "time":
            now_iso(),

            "host":
                socket.gethostname(),

                "platform":
                    platform.platform(),

                    "pid":
                        os.getpid(),

                        "network": {
                            "upload_kbps":
                                network[
                                    "upload_kbps"
                                ],
                                "download_kbps":
                                    network[
                                        "download_kbps"
                                    ],
                                    "connections":
                                        connections,
                                        "protocol_stats":
                                            network[
                                                "protocol_stats"
                                            ],
                                        },

                                        "endpoint": endpoint,

                                        "firewall": firewall,

                                        "ids": {
                                            "alerts":
                                                len(
                                                    self.ids.recent()
                                                ),
                                            },

                                            "siem": siem,

                                            "alerts": alerts,

                                            "threat_intelligence":
                                                self.threats.all(),

                                                "recent_alerts":
                                                    self.alerts.recent(30),

                                                    "recent_events":
                                                        self.siem.recent(30),
                                                    }

                                                    # ========================================================
                                                    # BROWSER CONNECTIONS
                                                    # ========================================================

    def browser_connections(self):

        browsers = []
        browser_pids = set()

        for proc in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                pid = proc.info["pid"]

                name = (
                    proc.info["name"]
                    or ""
                )

                lower = name.lower()

                if any(
                    lower == browser
                    or lower.startswith(
                        browser + "."
                    )
                    or lower.startswith(
                        browser + "-"
                    )
                    for browser
                    in BROWSER_NAMES
                ):

                    browser_pids.add(pid)

                    browsers.append({
                        "pid":
                            pid,
                            "name":
                                name,
                            })

            except Exception:
                continue

            connections = []

            try:

                net = psutil.net_connections(
                    kind="inet"
                )

            except Exception:

                net = []

                for conn in net:

                    if (
                        conn.pid
                        not in browser_pids
                        or conn.status
                        != "ESTABLISHED"
                        or not conn.raddr
                    ):
                        continue

                    remote_ip = (
                        conn.raddr.ip
                    )

                    remote_port = (
                        conn.raddr.port
                    )

                    connections.append({
                        "pid":
                            conn.pid,
                            "process":
                                safe_process_name(
                                    conn.pid
                                ),
                                "remote_ip":
                                    remote_ip,
                                    "remote_port":
                                        remote_port,
                                        "service":
                                            NetworkMonitor.service_for_port(
                                                remote_port
                                            ),
                                            "dns":
                                                self.intelligence.reverse_dns(
                                                    remote_ip
                                                ),
                                            })

                                            return {
                    "browsers":
                        browsers,
                        "connections":
                            connections,
                            "count":
                                len(connections),
                            }

                            # ========================================================
                            # THREAT MAP
                            # ========================================================

    def generate_threat_map(self):

        try:
import folium
        except ImportError:

            return {
        "success":
            False,
            "message":
                "Install folium first."
            }

            snapshot = (
                self.network.snapshot()
            )

            remote_ips = set()

            for conn in snapshot[
                "connections"
            ]:

                remote = conn.get(
                    "remote_ip"
                )

                if (
                    remote
                    and is_public_ip(remote)
                ):

                    remote_ips.add(remote)

                    # Host location
                    host_location = [
                        -13.9833,
                        33.7833,
                    ]

                    try:

                        response = requests.get(
                            "https://ipapi.co/json/",
                            timeout=4
                        )

                        if response.ok:

                            data = response.json()

                            lat = data.get(
                                "latitude"
                            )

                            lon = data.get(
                                "longitude"
                            )

                            if (
                                isinstance(
                                    lat,
                                    (int, float)
                                )
                                and isinstance(
                                    lon,
                                    (int, float)
                                )
                            ):

                                host_location = [
                                    float(lat),
                                    float(lon),
                                ]

                    except Exception:
                        pass

                    threat_map = folium.Map(
                        location=host_location,
                        zoom_start=3,
                        tiles="CartoDB dark_matter",
                    )

                    folium.Marker(
                        host_location,
                        popup=(
                            f"Security Host<br>"
                            f"{socket.gethostname()}"
                        ),
                        icon=folium.Icon(
                            color="red",
                            icon="home",
                        ),
                    ).add_to(threat_map)

                    for ip in list(
                        remote_ips
                    )[:50]:

                        geo = (
                            self.intelligence
                            .geolocate(ip)
                        )

                        lat = geo.get(
                            "latitude"
                        )

                        lon = geo.get(
                            "longitude"
                        )

                        if not (
                            isinstance(
                                lat,
                                (int, float)
                            )
                            and isinstance(
                                lon,
                                (int, float)
                            )
                        ):
                            continue

                        known = (
                            self.threats.lookup(ip)
                        )

                        color = (
                            "red"
                            if known
                            else "green"
                        )

                        popup = (
                            f"<b>{ip}</b><br>"
                            f"DNS: "
                            f"{self.intelligence.reverse_dns(ip)}"
                            f"<br>"
                            f"Location: "
                            f"{geo.get('city', '')}, "
                            f"{geo.get('country', '')}"
                            f"<br>"
                            f"Organization: "
                            f"{geo.get('org', '')}"
                        )

                        folium.CircleMarker(
                            [float(lat), float(lon)],
                            radius=7,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.8,
                            popup=popup,
                        ).add_to(
                            threat_map
                        )

                        folium.PolyLine(
                            [
                                host_location,
                                [float(lat), float(lon)],
                            ],
                            color=color,
                            weight=1,
                            opacity=0.5,
                        ).add_to(
                            threat_map
                        )

                        filename = (
                            self.maps
                            / (
                                "threat_map_"
                                + datetime.datetime.now()
                                .strftime(
                                    "%Y%m%d_%H%M%S"
                                )
                                + ".html"
                            )
                        )

                        threat_map.save(
                            str(filename)
                        )

                        return {
                            "success":
                                True,
                                "file":
                                    str(filename),
                                    "url":
                                        "/maps/"
                                        + filename.name,
                                    }

                                    # ========================================================
                                    # BACKGROUND LOOP
                                    # ========================================================

    def run(self):

        while self.running:

            try:

                self.update()

            except Exception as exc:

                self.security_event(
                    "System",
                    "MONITOR_ERROR",
                    "MEDIUM",
                    str(exc),
                    {},
                    alert=False,
                )

                time.sleep(
                    1
                )

    def stop(self):
        self.running = False


        # ============================================================
        # FLASK APPLICATION
        # ============================================================

        app = Flask(
            __name__
        )

        ENGINE: Optional[
            SecurityEngine
        ] = None


        # ============================================================
        # DASHBOARD HTML
        # ============================================================

        DASHBOARD_HTML = r"""
        <!DOCTYPE html>
        <html lang="en">

        <head>

        <meta charset="UTF-8">

        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Network Security Real-Time SOC</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

        <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #05080d;
                color: #d7e3ef;
                    font-family:
                        Inter,
                        ui-monospace,
                        SFMono-Regular,
                        Consolas,
                        monospace;
                    }

                    header {
                        padding: 18px 24px;
                        background: #080d14;
                            border-bottom: 1px solid #172435;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        }

                        .logo {
                            color: #00ff9c;
                                font-size: 22px;
                                font-weight: bold;
                            }

                            .live {
                                color: #00ff9c;
                                }

                                .container {
                                    padding: 18px;
                                }

                                .grid {
                                    display: grid;
                                    grid-template-columns:
                                        repeat(auto-fit, minmax(240px, 1fr));
                                        gap: 14px;
                                    }

                                    .card {
                                        background: #0a111a;
                                            border: 1px solid #1b2b3e;
                                            border-radius: 8px;
                                            padding: 16px;
                                        }

                                        .card h3 {
                                            margin-top: 0;
                                            color: #6fb7ff;
                                            }

                                            .metric {
                                                font-size: 28px;
                                                color: #00ff9c;
                                                    margin: 8px 0;
                                                }

                                                .small {
                                                    color: #8194a8;
                                                        font-size: 12px;
                                                    }

                                                    .red {
                                                        color: #ff4655;
                                                        }

                                                        .yellow {
                                                            color: #ffd166;
                                                            }

                                                            .blue {
                                                                color: #56b4ff;
                                                                }

                                                                .green {
                                                                    color: #00ff9c;
                                                                    }

                                                                    .orange {
                                                                        color: #ff9f43;
                                                                        }

                                                                        table {
                                                                            width: 100%;
                                                                            border-collapse: collapse;
                                                                            font-size: 12px;
                                                                        }

                                                                        th,
                                                                        td {
                                                                            padding: 8px;
                                                                            border-bottom:
                                                                                1px solid #182536;
                                                                                text-align: left;
                                                                            }

                                                                            th {
                                                                                color: #6fb7ff;
                                                                                }

                                                                                .scroll {
                                                                                    max-height: 420px;
                                                                                    overflow: auto;
                                                                                }

                                                                                input,
                                                                                select,
                                                                                button {
                                                                                    background: #07101a;
                                                                                        border: 1px solid #29425b;
                                                                                        color: #d7e3ef;
                                                                                            padding: 9px;
                                                                                            border-radius: 5px;
                                                                                        }

                                                                                        button {
                                                                                            cursor: pointer;
                                                                                        }

                                                                                        button:hover {
                                                                                            border-color: #00ff9c;
                                                                                                color: #00ff9c;
                                                                                                }

                                                                                                .form {
                                                                                                    display: flex;
                                                                                                    flex-wrap: wrap;
                                                                                                    gap: 8px;
                                                                                                }

                                                                                                .alert {
                                                                                                    padding: 9px;
                                                                                                    margin-bottom: 6px;
                                                                                                    border-left: 3px solid;
                                                                                                    background: #08111a;
                                                                                                    }

                                                                                                    .CRITICAL {
                                                                                                        border-color: #ff304f;
                                                                                                        }

                                                                                                        .HIGH {
                                                                                                            border-color: #ff9f43;
                                                                                                            }

                                                                                                            .MEDIUM {
                                                                                                                border-color: #ffd166;
                                                                                                                }

                                                                                                                .LOW {
                                                                                                                    border-color: #00ff9c;
                                                                                                                    }

                                                                                                                    pre {
                                                                                                                        white-space: pre-wrap;
                                                                                                                    }

                                                                                                                    footer {
                                                                                                                        color: #52677d;
                                                                                                                            padding: 20px;
                                                                                                                            text-align: center;
                                                                                                                        }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .connection-line {
        stroke-dasharray: 8, 6;
        animation: flowLine 1.5s linear infinite;
    }

    @keyframes flowLine {
from { stroke-dashoffset: 0; }
to { stroke-dashoffset: -14; }
}

.pulse-ring {
    animation: pulse 2s ease-out infinite;
}

    @keyframes pulse {
        0% { r: 5; opacity: 1; }
        100% { r: 20; opacity: 0; }
    }

    .map-feed-item {
        background: #0a111a;
            border-left: 3px solid #00ff9c;
            padding: 4px 8px;
            margin-bottom: 3px;
            border-radius: 3px;
            font-size: 11px;
            animation: slideIn 0.3s ease;
        }

        .map-feed-item.critical { border-color: #ff4655; }
            .map-feed-item.high { border-color: #ff9f43; }
                .map-feed-item.medium { border-color: #ffd166; }
                    .map-feed-item.low { border-color: #00ff9c; }

                        .map-feed-item .time { color: #52677d; font-size: 9px; }
                            .map-feed-item .type { font-weight: 600; color: #6fb7ff; }
                                .map-feed-item .severity { font-weight: 600; font-size: 9px; text-transform: uppercase; }
                                .map-feed-item .severity.critical { color: #ff4655; }
                                    .map-feed-item .severity.high { color: #ff9f43; }
                                        .map-feed-item .message { color: #d7e3ef; margin-top: 2px; }
                                            .map-feed-item .ip { color: #56b4ff; font-family: monospace; }

    @keyframes slideIn {
from { opacity: 0; transform: translateX(-10px); }
to { opacity: 1; transform: translateX(0); }
}

.map-tooltip {
    background: #0a111a !important;
        border: 1px solid #1b2b3e !important;
        color: #d7e3ef !important;
            font-family: monospace !important;
            font-size: 11px !important;
            padding: 6px 10px !important;
            border-radius: 4px !important;
        }


        .connection-line { stroke-dasharray: 7 9; animation: mapLineFlow 1.2s linear infinite; }
        .threat-line { animation-duration: .65s; }
        .host-pulse-ring, .threat-pulse-ring { animation: mapPulse 1.4s ease-out infinite; }
    @keyframes mapLineFlow { to { stroke-dashoffset: -32; } }
    @keyframes mapPulse { 0% { opacity:.8; } 70% { opacity:.08; } 100% { opacity:0; } }
    </style>

    </head>

    <body>

    <header>

    <div class="logo">
    NETWORK SECURITY SOC
    </div>

    <div>
    <span class="live"><span id="liveStatus">● LIVE</span></span>
    <span id="clock"></span>
    </div>

    </header>

    <div class="container">

    <div class="grid">

    <div class="card">

    <h3>Firewall</h3>

    <div
class="metric"
id="blockedIPs"
>
0
</div>

<div class="small">
Blocked IPs
</div>

<div
class="metric"
id="blockedPorts"
>
0
</div>

<div class="small">
Blocked Ports
</div>

</div>

<div class="card">

<h3>Network</h3>

<div
class="metric"
id="download"
>
0 KB/s
</div>

<div class="small">
Download
</div>

<div
class="metric"
id="upload"
>
0 KB/s
</div>

<div class="small">
Upload
</div>

</div>

<div class="card">

<h3>Connections</h3>

<div
class="metric"
id="connectionCount"
>
0
</div>

<div class="small">
Active connections
</div>

</div>

<div class="card">

<h3>Security</h3>

<div>
Critical:
    <span
class="red"
id="critical"
>0</span>
</div>

<div>
High:
    <span
class="orange"
id="high"
>0</span>
</div>

<div>
Medium:
    <span
class="yellow"
id="medium"
>0</span>
</div>

<div>
SIEM events:
    <span
class="blue"
id="siem"
>0</span>
</div>

</div>

</div>

<br>

<div class="grid">

<div class="card">

<h3>Firewall Controls</h3>

<div class="form">

<input
id="blockIP"
placeholder="IP address"
/>

<input
id="blockReason"
placeholder="Reason"
/>

<button
onclick="blockIP()"
>
Block IP
</button>

</div>

<br>

<div class="form">

<input
id="unblockIP"
placeholder="IP address"
/>

<button
onclick="unblockIP()"
>
Unblock IP
</button>

</div>

<br>

<div class="form">

<input
id="blockPort"
type="number"
placeholder="Port"
/>

<button
onclick="blockPort()"
>
Block Port
</button>

<input
id="unblockPort"
type="number"
placeholder="Port"
/>

<button
onclick="unblockPort()"
>
Unblock Port
</button>

</div>

</div>

<div class="card">

<h3>Endpoint Controls</h3>

<div class="form">

<input
id="killPID"
type="number"
placeholder="PID"
/>

<button
onclick="killProcess()"
>
Terminate Process
</button>

<button
onclick="scanProcesses()"
>
Run Process Scan
</button>

</div>

<br>

<div class="form">

<input
id="iocIP"
placeholder="Threat IOC IP"
/>

<input
id="iocDescription"
placeholder="IOC description"
/>

<button
onclick="addIOC()"
>
Add IOC
</button>

</div>

</div>

</div>

<br>

<div class="grid">

<div class="card">

<h3>Live Connections</h3>

<div class="scroll">

<table>

<thead>

<tr>

<th>Process</th>
<th>PID</th>
<th>Local</th>
<th>Remote</th>
<th>Status</th>
<th>Action</th>

</tr>

</thead>

<tbody
id="connections"
>
</tbody>

</table>

</div>

</div>

<div class="card" style="grid-column: span 1; min-height: 500px;">
<h3>🗺️ REAL-TIME THREAT MAP & FEED</h3>
<div style="display: flex; flex-direction: column; height: 450px; margin-top: 10px;">
<!-- Map Container -->
<div id="threatMapContainer" style="flex: 2; background: #0a111a; border-radius: 6px; border: 1px solid #1b2b3e; position: relative; overflow: hidden; min-height: 250px;">
    <div id="threatMap" style="width: 100%; height: 100%;">
    <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #52677d; font-size: 13px;">
        <div style="text-align: center;">
        <div style="width: 30px; height: 30px; border: 3px solid #172435; border-top-color: #00ff9c; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px;"></div>
            Loading threat map...
            </div>
            </div>
            </div>
            </div>
            <!-- Threat Feed List -->
            <div style="flex: 1; background: #080d14; border-radius: 6px; border: 1px solid #1b2b3e; display: flex; flex-direction: column; overflow: hidden; margin-top: 8px; min-height: 120px;">
                <div style="padding: 6px 12px; border-bottom: 1px solid #1b2b3e; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">
                <span style="color: #6fb7ff; font-size: 12px; font-weight: 500;">🔴 THREAT FEED</span>
                    <span id="mapFeedBadge" style="background: #ff4655; color: #fff; font-size: 10px; padding: 1px 10px; border-radius: 12px; font-weight: bold;">0</span>
                        </div>
                        <div id="mapFeedList" style="flex: 1; overflow-y: auto; padding: 4px 8px; max-height: 150px;">
                        <div style="color: #52677d; text-align: center; padding: 20px 0; font-size: 12px;">
                            Waiting for events...
                            </div>
                            </div>
                            <div style="padding: 6px 10px; border-top: 1px solid #1b2b3e; display: flex; gap: 6px; flex-shrink: 0; flex-wrap: wrap;">
                            <input id="mapBlockIP" placeholder="Block IP" style="flex:1; background:#07101a; border:1px solid #29425b; color:#d7e3ef; padding:3px 8px; border-radius:4px; font-size:11px; min-width:80px;">
                                <button onclick="mapBlockIP()" style="background:#0a111a; border:1px solid #29425b; color:#d7e3ef; padding:3px 12px; border-radius:4px; cursor:pointer; font-size:11px;">Block</button>
                                    <button onclick="refreshThreatMap()" style="background:#0a111a; border:1px solid #00ff9c; color:#00ff9c; padding:3px 12px; border-radius:4px; cursor:pointer; font-size:11px;">🔄</button>
                                        </div>
                                        </div>
                                        </div>
                                        </div>

                                        </div>

                                        <br>

                                        <div class="grid">

                                        <div class="card">

                                        <h3>Processes</h3>

                                        <div class="scroll">

                                        <table>

                                        <thead>

                                        <tr>

                                        <th>PID</th>
                                        <th>Name</th>
                                        <th>User</th>
                                        <th>CPU</th>
                                        <th>Memory</th>

                                        </tr>

                                        </thead>

                                        <tbody
                                        id="processes"
                                        >
                                        </tbody>

                                        </table>

                                        </div>

                                        </div>

                                        <div class="card">

                                        <h3>SIEM Events</h3>

                                        <div class="scroll">

                                        <table>

                                        <thead>

                                        <tr>

                                        <th>Time</th>
                                        <th>Severity</th>
                                        <th>Type</th>
                                        <th>Message</th>

                                        </tr>

                                        </thead>

                                        <tbody
                                        id="events"
                                        >
                                        </tbody>

                                        </table>

                                        </div>

                                        </div>

                                        </div>

                                        <br>

                                        <div class="grid">

                                        <div class="card">

                                        <h3>Network Protocols</h3>

                                        <pre id="protocols">
                                        Waiting for data...
                                        </pre>

                                        </div>

                                        <div class="card">

                                        <h3>Threat Intelligence</h3>

                                        <div
                                        id="threats"
                                        >
                                        </div>

                                        <br>

                                        <button
                                        onclick="generateMap()"
                                        >
                                        Generate Threat Map
                                        </button>

                                        <button
                                        onclick="browserConnections()"
                                        >
                                        Browser Connections
                                        </button>

                                        </div>

                                        </div>

                                        </div>

                                        <footer>
                                        Real host telemetry — no simulated network traffic
                                        </footer>
                                        <!-- Leaflet JS -->
                                        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                                        <script>

                                        function esc(value) {

                                            if (value === null ||
                                            value === undefined) {
                                                return "";
                                        }

                                        return String(value)
                                            .replaceAll("&", "&amp;")
                                            .replaceAll("<", "&lt;")
                                            .replaceAll(">", "&gt;")
                                            .replaceAll('"', "&quot;")
                                            .replaceAll("'", "&#039;");
                                        }


                                        async function api(
                                            url,
                                            method = "GET",
                                            body = null
                                        ) {

                                            const options = {
                                                method: method,
                                                headers: {
                                                    "Content-Type":
                                                        "application/json"
                                                    }
                                                };

                                                if (body !== null) {
                                                    options.body =
                                                    JSON.stringify(body);
                                                }

                                                const response =
                                                await fetch(
                                                    url,
                                                    options
                                                );

                                                const contentType = response.headers.get("content-type") || "";
                                                if (!contentType.includes("application/json")) {
                                                    throw new Error(`HTTP ${response.status}: expected JSON response`);
                                                }
                                                const payload = await response.json();
                                                if (!response.ok) {
                                                    throw new Error(payload.message || `HTTP ${response.status}`);
                                                }
                                                return payload;
                                            }


                                            function render(data) {

                                                document.getElementById(
                                                    "clock"
                                                ).textContent =
                                                " " + data.time;

                                                document.getElementById(
                                                    "blockedIPs"
                                                ).textContent =
                                                data.firewall.blocked_ips;

                                                document.getElementById(
                                                    "blockedPorts"
                                                ).textContent =
                                                data.firewall.blocked_ports;

                                                document.getElementById(
                                                    "download"
                                                ).textContent =
                                                data.network.download_kbps
                                                + " KB/s";

                                                document.getElementById(
                                                    "upload"
                                                ).textContent =
                                                data.network.upload_kbps
                                                + " KB/s";

                                                document.getElementById(
                                                    "connectionCount"
                                                ).textContent =
                                                data.network.connections.length;

                                                document.getElementById(
                                                    "critical"
                                                ).textContent =
                                                data.alerts.critical;

                                                document.getElementById(
                                                    "high"
                                                ).textContent =
                                                data.alerts.high;

                                                document.getElementById(
                                                    "medium"
                                                ).textContent =
                                                data.alerts.medium;

                                                document.getElementById(
                                                    "siem"
                                                ).textContent =
                                                data.siem.total;

                                                renderConnections(
                                                    data.network.connections
                                                );

                                                renderProcesses(
                                                    data.endpoint.processes
                                                );

                                                renderAlerts(
                                                    data.recent_alerts
                                                );

                                                renderEvents(
                                                    data.recent_events
                                                );

                                                document.getElementById(
                                                    "protocols"
                                                ).textContent =
                                                JSON.stringify(
                                                    data.network.protocol_stats,
                                                    null,
                                                    2
                                                );

                                                renderThreats(
                                                    data.threat_intelligence
                                                );
                                            }


                                            function renderConnections(
                                                connections
                                            ) {

                                                const tbody =
                                                document.getElementById(
                                                    "connections"
                                                );

                                                tbody.innerHTML = "";

                                                for (
                                                    const c of connections
                                                ) {

                                                    const tr =
                                                    document.createElement(
                                                        "tr"
                                                    );

                                                    const remote =
                                                    c.remote_ip
                                                    ? c.remote_ip
                                                    + ":"
                                                    + (
                                                        c.remote_port || ""
                                                    )
                                                    : "";

                                                    tr.innerHTML = `
                                                    <td>${esc(c.process)}</td>
                                                    <td>${esc(c.pid)}</td>
                                                    <td>
                                                    ${esc(c.local_ip)}
                                                    :
                                                        ${esc(c.local_port)}
                                                        </td>
                                                        <td>
                                                        ${esc(remote)}
                                                        </td>
                                                        <td>
                                                        ${
                                                            c.blocked
                                                            ? '<span class="red">BLOCKED</span>'
                                                            : esc(c.status)
                                                        }
                                                        </td>
                                                        <td>
                                                        ${
                                                            c.remote_ip
                                                            ? `
                                                            <button
                                                            onclick="quickBlock('${esc(c.remote_ip)}')"
                                                            >
                                                            Block IP
                                                            </button>
                                                            `
                                                            : ""
                                                        }
                                                        </td>
                                                        `;

                                                        tbody.appendChild(tr);
                                                    }
                                                }


                                                function renderProcesses(
                                                    processes
                                                ) {

                                                    const tbody =
                                                    document.getElementById(
                                                        "processes"
                                                    );

                                                    tbody.innerHTML = "";

                                                    for (
                                                        const p of processes.slice(0, 100)
                                                    ) {

                                                        const tr =
                                                        document.createElement(
                                                            "tr"
                                                        );

                                                        tr.innerHTML = `
                                                        <td>${esc(p.pid)}</td>
                                                        <td>${esc(p.name)}</td>
                                                        <td>${esc(p.username)}</td>
                                                        <td>${esc(p.cpu_percent)}%</td>
                                                        <td>${esc(p.memory_percent)}%</td>
                                                        `;

                                                        tbody.appendChild(tr);
                                                    }
                                                }


                                                function renderAlerts(
                                                    alerts
                                                ) {

                                                    const element =
                                                    document.getElementById(
                                                        "alerts"
                                                    );

                                                    element.innerHTML = "";

                                                    for (
                                                        const alert of
                                                        alerts.slice().reverse()
                                                    ) {

                                                        const div =
                                                        document.createElement(
                                                            "div"
                                                        );

                                                        div.className =
                                                        "alert "
                                                        + alert.severity;

                                                        div.innerHTML = `
                                                        <strong>
                                                        [${esc(alert.severity)}]
                                                        ${esc(alert.title)}
                                                        </strong>
                                                        <br>
                                                        ${esc(alert.message)}
                                                        <br>
                                                        <span class="small">
                                                        ${esc(alert.timestamp)}
                                                        |
                                                        ${esc(alert.source)}
                                                        </span>
                                                        `;

                                                        element.appendChild(div);
                                                    }
                                                }


                                                function renderEvents(
                                                    events
                                                ) {

                                                    const tbody =
                                                    document.getElementById(
                                                        "events"
                                                    );

                                                    tbody.innerHTML = "";

                                                    for (
                                                        const event of
                                                        events.slice().reverse()
                                                    ) {

                                                        const tr =
                                                        document.createElement(
                                                            "tr"
                                                        );

                                                        tr.innerHTML = `
                                                        <td>${esc(event.timestamp)}</td>
                                                        <td>${esc(event.severity)}</td>
                                                        <td>${esc(event.event_type)}</td>
                                                        <td>${esc(event.message)}</td>
                                                        `;

                                                        tbody.appendChild(tr);
                                                    }
                                                }


                                                function renderThreats(
                                                    threats
                                                ) {

                                                    const element =
                                                    document.getElementById(
                                                        "threats"
                                                    );

                                                    element.innerHTML = "";

                                                    for (
                                                        const [ip, description]
                                                        of Object.entries(threats)
                                                    ) {

                                                        element.innerHTML += `
                                                        <div>
                                                        <span class="red">
                                                        ${esc(ip)}
                                                        </span>
                                                        —
                                                        ${esc(description)}
                                                        </div>
                                                        `;
                                                    }
                                                }

                                                // ============================================================
                                                // EMBEDDED THREAT MAP (inside Threat Feed)
                                                // ============================================================
                                                let threatMap = null;
                                                let mapMarkers = Object.create(null);
                                                let mapLines = Object.create(null);
                                                let mapTrafficDots = Object.create(null);
                                                let mapPulseRings = [];
                                                let mapGeoCache = Object.create(null);
                                                let mapHostMarker = null;
                                                let mapHostPulse = null;
                                                let mapRefreshTimer = null;

                                                function clearMapStore(store) {
                                                    for (const key of Object.keys(store)) {
                                                        try { if (threatMap && store[key]) threatMap.removeLayer(store[key]); } catch (_) {}
                                                        delete store[key];
                                                    }
                                                }

                                                function clearThreatMapObjects() {
                                                    clearMapStore(mapMarkers);
                                                    clearMapStore(mapLines);
                                                    clearMapStore(mapTrafficDots);
                                                    for (const ring of mapPulseRings) {
                                                        try { if (threatMap) threatMap.removeLayer(ring); } catch (_) {}
                                                    }
                                                    mapPulseRings = [];
                                                    if (mapHostMarker && threatMap) threatMap.removeLayer(mapHostMarker);
                                                    if (mapHostPulse && threatMap) threatMap.removeLayer(mapHostPulse);
                                                    mapHostMarker = null;
                                                    mapHostPulse = null;
                                                }

                                                function initThreatMap() {
                                                    const container = document.getElementById('threatMap');
                                                    if (!container || typeof L === 'undefined' || threatMap) return;
                                                    container.innerHTML = '';
                                                    threatMap = L.map('threatMap', { center: [-13.9833, 33.7833], zoom: 3, zoomControl: true });
                                                    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                                                        attribution: '&copy; OpenStreetMap, &copy; CartoDB', subdomains: 'abcd', maxZoom: 19, minZoom: 2
                                                    }).addTo(threatMap);
                                                    setTimeout(() => threatMap && threatMap.invalidateSize(), 300);
                                                }

                                                function addHostMarker(geo) {
                                                    if (!threatMap || !geo) return null;
                                                    const lat = Number(geo.latitude), lon = Number(geo.longitude);
                                                    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
                                                    mapHostPulse = L.circleMarker([lat, lon], { radius: 18, color: '#00ff9c', fillColor: '#00ff9c', fillOpacity: 0.08, weight: 2, className: 'host-pulse-ring' }).addTo(threatMap);
                                                    mapHostMarker = L.circleMarker([lat, lon], { radius: 9, color: '#fff', fillColor: '#00ff9c', fillOpacity: 0.95, weight: 2 }).addTo(threatMap);
                                                    mapHostMarker.bindPopup(`<b style="color:#00ff9c">SECURITY HOST</b><br>Host: ${esc(location.hostname)}<br>Public IP: ${esc(geo.ip || 'Unavailable')}<br>Location: ${esc([geo.city, geo.region, geo.country].filter(Boolean).join(', ') || 'Unavailable')}<br><small>IP geolocation is approximate; this is not GPS.</small>`);
                                                        return { lat, lon };
                                                }

                                                function animateConnection(key, start, end, threat) {
                                                    const old = mapTrafficDots[key];
                                                    if (old) { try { threatMap.removeLayer(old.a); } catch (_) {} try { threatMap.removeLayer(old.b); } catch (_) {} }
                                                    const a = L.circleMarker(start, { radius: 3, color: threat ? '#ff4655' : '#56b4ff', fillColor: threat ? '#ff4655' : '#56b4ff', fillOpacity: 1, weight: 0 }).addTo(threatMap);
                                                    const b = L.circleMarker(end, { radius: 3, color: threat ? '#ff4655' : '#00ff9c', fillColor: threat ? '#ff4655' : '#00ff9c', fillOpacity: 1, weight: 0 }).addTo(threatMap);
                                                    mapTrafficDots[key] = { a, b };
                                                    const started = performance.now(), duration = 2200;
                                                    function frame(now) {
                                                        if (!mapTrafficDots[key] || !threatMap) return;
                                                        const f = ((now - started) % duration) / duration, g = (f + 0.5) % 1;
                                                        const p = (x, y, q) => [x[0] + (y[0] - x[0]) * q, x[1] + (y[1] - x[1]) * q];
                                                        a.setLatLng(p(start, end, f));
                                                        b.setLatLng(p(end, start, g));
                                                        requestAnimationFrame(frame);
                                                    }
                                                    requestAnimationFrame(frame);
                                                }

                                                function addMapMarker(ip, data) {
                                                    const lat = Number(data.lat), lon = Number(data.lon);
                                                    if (!threatMap || !Number.isFinite(lat) || !Number.isFinite(lon)) return;
                                                    const threat = Boolean(data.threat), color = threat ? '#ff4655' : '#00ff9c';
                                                    const marker = L.circleMarker([lat, lon], { radius: threat ? 8 : 6, color, fillColor: color, fillOpacity: 0.85, weight: 2 }).addTo(threatMap);
                                                    marker.bindPopup(`<div style="font-family:monospace;font-size:11px;line-height:1.5"><b>${esc(ip)}</b><br>Host: ${esc(data.hostname || 'Unknown')}<br>Location: ${esc(data.location || 'Unknown')}<br>Local port: ${esc(data.localPort || '?')}<br>Remote port: ${esc(data.remotePort || '?')}<br>${threat ? '<b style="color:#ff4655">THREAT / IOC</b>' : '<span style="color:#00ff9c">ACTIVE CONNECTION</span>'}<br><button onclick="quickBlockMap('${ip}')">Block IP</button></div>`);
                                                        mapMarkers[ip] = marker;
                                                        const start = [Number(data.hostLat), Number(data.hostLon)], end = [lat, lon];
                                                        if (Number.isFinite(start[0]) && Number.isFinite(start[1])) {
                                                            mapLines[ip] = L.polyline([start, end], { color: threat ? '#ff4655' : '#56b4ff', weight: threat ? 2.5 : 1.5, opacity: 0.65, dashArray: threat ? '5 8' : '7 9', className: threat ? 'connection-line threat-line' : 'connection-line' }).addTo(threatMap);
                                                            animateConnection(ip, start, end, threat);
                                                        }
                                                        if (threat) mapPulseRings.push(L.circleMarker([lat, lon], { radius: 13, color: '#ff4655', fillColor: '#ff4655', fillOpacity: 0.08, weight: 2, className: 'threat-pulse-ring' }).addTo(threatMap));
                                                    }

                                                    async function getGeo(ip) {
                                                        if (mapGeoCache[ip]) return mapGeoCache[ip];
                                                        try {
                                                            const g = await api(`${API_BASE}/api/geolocate?ip=${encodeURIComponent(ip)}`);
                                                            if (g && Number.isFinite(Number(g.latitude)) && Number.isFinite(Number(g.longitude))) { mapGeoCache[ip] = g; return g; }
                                                        } catch (_) {}
                                                        return null;
                                                        }

                                                        async function loadThreatMapData() {
                                                            if (!threatMap) return;
                                                            try {
                                                                const [snapshot, hostGeo] = await Promise.all([api('/api/snapshot'), api('/api/host-location')]);
                                                                clearThreatMapObjects();
                                                                const host = addHostMarker(hostGeo);
                                                                if (!host) {
                                                                    const box = document.getElementById('threatMap');
                                                                    if (box) box.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;color:#ff9f43;font-size:11px;text-align:center;padding:20px">Host public-IP geolocation unavailable.<br>Network telemetry remains active.</div>';
                                                                        return;
                                                                }
                                                                const connections = snapshot.network?.connections || [];
                                                                const threats = snapshot.threat_intelligence || {};
                                                                const unique = new Map();
                                                                for (const c of connections) {
                                                                    const ip = String(c.remote_ip || '').trim();
                                                                    if (!ip || !isPublicRemoteIp(ip) || unique.has(ip)) continue;
                                                                    unique.set(ip, c);
                                                                }
                                                                const results = await Promise.all(Array.from(unique.entries()).slice(0, 50).map(async ([ip, c]) => [ip, c, await getGeo(ip)]));
                                                                let threatCount = 0;
                                                                for (const [ip, c, geo] of results) {
                                                                    if (!geo) continue;
                                                                    const threat = Boolean(threats[ip]);
                                                                    if (threat) threatCount++;
                                                                    addMapMarker(ip, { lat: geo.latitude, lon: geo.longitude, hostname: c.dns || c.process || 'Unknown', location: [geo.city, geo.region, geo.country].filter(Boolean).join(', '), localPort: c.local_port, remotePort: c.remote_port, threat, hostLat: host.lat, hostLon: host.lon });
                                                                }
                                                                const count = document.getElementById('threatCount');
                                                                if (count) count.textContent = String(threatCount);
                                                                setTimeout(() => threatMap && threatMap.invalidateSize(), 100);
                                                            } catch (error) { console.error('Threat map refresh failed:', error); }
                                                        }

                                                        function isPublicRemoteIp(ip) {
                                                            const p = ip.split('.').map(Number);
                                                            if (p.length !== 4 || p.some(Number.isNaN)) return false;
                                                            if (p[0] === 10 || p[0] === 127 || (p[0] === 192 && p[1] === 168) || (p[0] === 172 && p[1] >= 16 && p[1] <= 31)) return false;
                                                            return true;
                                                        }

                                                        async function refreshThreatMap() { await loadThreatMapData(); }
                                                        async function mapBlockIP() {
                                                            const input = document.getElementById('mapBlockIP'), ip = input ? input.value.trim() : '';
                                                            if (!ip) return;
                                                            const result = await api('/api/firewall/block-ip', 'POST', { ip, reason: 'Map block' });
                                                            alert(result?.message || 'No response');
                                                            if (result?.success) { input.value = ''; await initialLoad(); await refreshThreatMap(); }
                                                        }
                                                        async function quickBlockMap(ip) {
                                                            if (!confirm(`Block ${ip}?`)) return;
                                                            const result = await api('/api/firewall/block-ip', 'POST', { ip, reason: 'Quick map block' });
                                                            alert(result?.message || 'No response');
                                                            if (result?.success) { await initialLoad(); await refreshThreatMap(); }
                                                        }
                                                        function initThreatMapOnLoad() {
                                                            initThreatMap();
                                                            loadThreatMapData();
                                                            if (mapRefreshTimer) clearInterval(mapRefreshTimer);
                                                            mapRefreshTimer = setInterval(loadThreatMapData, 5000);
                                                        }
                                                        window.mapBlockIP = mapBlockIP;
                                                        window.quickBlockMap = quickBlockMap;
                                                        window.refreshThreatMap = refreshThreatMap;


                                                        async function blockIP() {

                                                            const ip =
                                                            document.getElementById(
                                                                "blockIP"
                                                            ).value;

                                                            const reason =
                                                            document.getElementById(
                                                                "blockReason"
                                                            ).value
                                                            || "Dashboard block";

                                                            const result =
                                                            await api(
                                                                "/api/firewall/block-ip",
                                                                "POST",
                                                                {
                                                                    ip,
                                                                    reason
                                                                }
                                                            );

                                                            alert(result.message);
                                                        }


                                                        async function quickBlock(ip) {

                                                            if (!confirm(
                                                                "Block " + ip + "?"
                                                            )) {
                                                                return;
                                                        }

                                                        const result =
                                                        await api(
                                                            "/api/firewall/block-ip",
                                                            "POST",
                                                            {
                                                                ip,
                                                                reason:
                                                                    "Manual block from live connection"
                                                                }
                                                            );

                                                            alert(result.message);
                                                        }


                                                        async function unblockIP() {

                                                            const ip =
                                                            document.getElementById(
                                                                "unblockIP"
                                                            ).value;

                                                            const result =
                                                            await api(
                                                                "/api/firewall/unblock-ip",
                                                                "POST",
                                                                { ip }
                                                            );

                                                            alert(result.message);
                                                        }


                                                        async function blockPort() {

                                                            const port =
                                                            document.getElementById(
                                                                "blockPort"
                                                            ).value;

                                                            const result =
                                                            await api(
                                                                "/api/firewall/block-port",
                                                                "POST",
                                                                { port }
                                                            );

                                                            alert(result.message);
                                                        }


                                                        async function unblockPort() {

                                                            const port =
                                                            document.getElementById(
                                                                "unblockPort"
                                                            ).value;

                                                            const result =
                                                            await api(
                                                                "/api/firewall/unblock-port",
                                                                "POST",
                                                                { port }
                                                            );

                                                            alert(result.message);
                                                        }


                                                        async function killProcess() {

                                                            const pid =
                                                            document.getElementById(
                                                                "killPID"
                                                            ).value;

                                                            if (!confirm(
                                                                "Terminate PID " + pid + "?"
                                                            )) {
                                                                return;
                                                        }

                                                        const result =
                                                        await api(
                                                            "/api/process/terminate",
                                                            "POST",
                                                            { pid }
                                                        );

                                                        alert(result.message);
                                                    }


                                                    async function scanProcesses() {

                                                        const result =
                                                        await api(
                                                            "/api/process/scan",
                                                            "POST"
                                                        );

                                                        alert(
                                                            "Process scan complete. "
                                                            + result.suspicious
                                                            + " suspicious findings."
                                                        );
                                                    }


                                                    async function addIOC() {

                                                        const ip =
                                                        document.getElementById(
                                                            "iocIP"
                                                        ).value;

                                                        const description =
                                                        document.getElementById(
                                                            "iocDescription"
                                                        ).value;

                                                        const result =
                                                        await api(
                                                            "/api/ioc/add",
                                                            "POST",
                                                            {
                                                                ip,
                                                                description
                                                            }
                                                        );

                                                        alert(result.message);
                                                    }


                                                    async function generateMap() {

                                                        const result =
                                                        await api(
                                                            "/api/threat-map",
                                                            "POST"
                                                        );

                                                        if (result.success) {

                                                            window.open(
                                                                result.url,
                                                                "_blank"
                                                            );

                                                        } else {

                                                            alert(result.message);
                                                        }
                                                    }


                                                    async function browserConnections() {

                                                        const result =
                                                        await api(
                                                            "/api/browser-connections"
                                                        );

                                                        let text =
                                                        "BROWSERS\n\n";

                                                        for (
                                                            const browser of result.browsers
                                                        ) {

                                                            text +=
                                                            browser.name
                                                            + " PID "
                                                            + browser.pid
                                                            + "\n";
                                                        }

                                                        text +=
                                                        "\nCONNECTIONS\n\n";

                                                        for (
                                                            const c of result.connections
                                                        ) {

                                                            text +=
                                                            c.process
                                                            + " -> "
                                                            + c.remote_ip
                                                            + ":"
                                                            + c.remote_port
                                                            + " "
                                                            + c.dns
                                                            + "\n";
                                                        }

                                                        alert(text);
                                                    }


                                                    document.addEventListener("DOMContentLoaded", function() {
                                                        setTimeout(initThreatMapOnLoad, 300);
                                                    });

                                                    // ========================================================
                                                    // LIVE DASHBOARD UPDATE CONTROLLER
                                                    // ========================================================

                                                    let liveUpdateTimer = null;
                                                    let liveUpdateBusy = false;
                                                    let liveStreamConnected = false;

                                                    function setLiveStatus(connected, source) {
                                                        liveStreamConnected = connected;
                                                        const el = document.getElementById("liveStatus");
                                                        if (el) {
                                                            el.textContent = connected
                                                            ? "● LIVE " + (source ? "(" + source + ")" : "")
                                                            : "● RECONNECTING";
                                                            el.style.color = connected ? "#00ff9c" : "#ffd166";
                                                        }
                                                    }

                                                    async function initialLoad() {
                                                        try {
                                                            const data = await api("/api/snapshot");
                                                            render(data);
                                                            setLiveStatus(true, "REST");
                                                        } catch (error) {
                                                            console.error("Initial dashboard load failed:", error);
                                                            setLiveStatus(false, "");
                                                        }
                                                    }

                                                    async function livePoll() {
                                                        if (liveUpdateBusy) return;
                                                        liveUpdateBusy = true;

                                                        try {
                                                            const data = await api("/api/snapshot");
                                                            render(data);
                                                            setLiveStatus(true, liveStreamConnected ? "SSE" : "POLL");
                                                        } catch (error) {
                                                            console.error("Live REST update failed:", error);
                                                            setLiveStatus(false, "");
                                                        } finally {
                                                            liveUpdateBusy = false;
                                                        }
                                                    }

                                                    let stream = null;

                                                    function connectLiveStream() {
                                                        try {
                                                            if (stream) stream.close();

                                                            stream = new EventSource("/api/stream");

                                                            stream.onopen = function () {
                                                                setLiveStatus(true, "SSE");
                                                            };

                                                            stream.onmessage = function (event) {
                                                                try {
                                                                    const payload = JSON.parse(event.data);

                                                                    if (payload.type === "snapshot" && payload.data) {
                                                                        render(payload.data);
                                                                        setLiveStatus(true, "SSE");
                                                                    } else if (payload.type === "alert") {
                                                                        const a = payload.data || {};

                                                                        if (
                                                                            (a.severity === "CRITICAL" ||
                                                                            a.severity === "HIGH") &&
                                                                            typeof addMapFeedItem === "function"
                                                                        ) {
                                                                            addMapFeedItem({
                                                                                timestamp: a.timestamp,
                                                                                severity: a.severity,
                                                                                type: a.title || a.type || "Alert",
                                                                                message: a.message || "",
                                                                                ip: a.data?.ip || a.data?.remote_ip || null
                                                                            });
                                                                        }

                                                                        if (threatMap) loadThreatMapData();
                                                                    }
                                                                } catch (error) {
                                                                    console.error("SSE payload error:", error);
                                                                }
                                                            };

                                                            stream.onerror = function () {
                                                                liveStreamConnected = false;
                                                                setLiveStatus(false, "");
                                                            };
                                                        } catch (error) {
                                                            console.error("Unable to create EventSource:", error);
                                                            setLiveStatus(false, "");
                                                        }
                                                    }

                                                    initialLoad();

                                                    // Guaranteed live fallback even if SSE is blocked/buffered.
                                                    liveUpdateTimer = setInterval(livePoll, 2000);

                                                    // SSE provides immediate push updates.
                                                    connectLiveStream();

                                                    </script>

                                                    </body>

                                                    </html>
                                                    """


                                                    # ============================================================
                                                    # FLASK ROUTES
                                                    # ============================================================

    @app.route("/")
    def dashboard():

        return render_template_string(
    DASHBOARD_HTML
)


    @app.route("/api/snapshot")
    def api_snapshot():

        return jsonify(
    ENGINE.dashboard_snapshot()
)


    @app.route("/api/alerts")
    def api_alerts():

        limit = int(
            request.args.get(
                "limit",
                100
            )
        )

        return jsonify(
    ENGINE.alerts.recent(
        limit
    )
)


    @app.route("/api/events")
    def api_events():

        limit = int(
            request.args.get(
                "limit",
                100
            )
        )

        return jsonify(
    ENGINE.siem.recent(
        limit
    )
)


    @app.route("/api/connections")
    def api_connections():

        return jsonify(
    ENGINE.network.snapshot()[
        "connections"
    ]
)


    @app.route("/api/browser-connections")
    def api_browser_connections():

        return jsonify(
    ENGINE.browser_connections()
)


    @app.route(
        "/api/processes"
    )
def api_processes():

    return jsonify(
ENGINE.endpoint.snapshot()
)


# ============================================================
# FIREWALL API
# ============================================================

    @app.route(
        "/api/firewall/block-ip",
        methods=["POST"]
    )
def api_block_ip():

    data = request.get_json(
        silent=True
    ) or {}

    ip = str(
        data.get(
            "ip",
            ""
        )
    ).strip()

    reason = str(
        data.get(
            "reason",
            "Dashboard block"
        )
    )

    result = (
        ENGINE.firewall.block_ip(
            ip,
            reason
        )
    )

    if result["success"]:

        ENGINE.security_event(
            "Firewall",
            "IP_BLOCKED",
            "HIGH",
            result["message"],
            {
                "ip": ip,
                "reason": reason,
            },
            alert=True,
        )

        return jsonify(result)


    @app.route(
        "/api/firewall/unblock-ip",
        methods=["POST"]
    )
def api_unblock_ip():

    data = request.get_json(
        silent=True
    ) or {}

    ip = str(
        data.get(
            "ip",
            ""
        )
    ).strip()

    result = (
        ENGINE.firewall.unblock_ip(
            ip
        )
    )

    if result["success"]:

        ENGINE.security_event(
            "Firewall",
            "IP_UNBLOCKED",
            "LOW",
            result["message"],
            {
                "ip": ip
            },
            alert=False,
        )

        return jsonify(result)


    @app.route(
        "/api/firewall/block-port",
        methods=["POST"]
    )
def api_block_port():

    data = request.get_json(
        silent=True
    ) or {}

    port = data.get(
        "port"
    )

    result = (
        ENGINE.firewall.block_port(
            int(port),
            "Dashboard port block"
        )
        if valid_port(port)
        else {
            "success":
                False,
                "message":
                    "Invalid port."
                }
            )

            if result["success"]:

                ENGINE.security_event(
                    "Firewall",
                    "PORT_BLOCKED",
                    "HIGH",
                    result["message"],
                    {
                        "port":
                            int(port)
                        },
                        alert=True,
                    )

                    return jsonify(result)


    @app.route(
        "/api/firewall/unblock-port",
        methods=["POST"]
    )
def api_unblock_port():

    data = request.get_json(
        silent=True
    ) or {}

    port = data.get(
        "port"
    )

    result = (
        ENGINE.firewall.unblock_port(
            int(port)
        )
        if valid_port(port)
        else {
            "success":
                False,
                "message":
                    "Invalid port."
                }
            )

            if result["success"]:

                ENGINE.security_event(
                    "Firewall",
                    "PORT_UNBLOCKED",
                    "LOW",
                    result["message"],
                    {
                        "port":
                            int(port)
                        },
                        alert=False,
                    )

                    return jsonify(result)


            # ============================================================
            # PROCESS API
            # ============================================================

    @app.route(
        "/api/process/scan",
        methods=["POST"]
    )
def api_process_scan():

    suspicious = (
        ENGINE.endpoint.scan()
    )

    ENGINE.security_event(
        "Endpoint",
        "MANUAL_PROCESS_SCAN",
        "LOW",
        (
            "Manual process scan completed."
        ),
        {
            "suspicious":
                len(suspicious)
            },
            alert=False,
        )

        return jsonify({
"success":
    True,
    "suspicious":
        len(suspicious),
        "results":
            suspicious,
        })


    @app.route(
        "/api/process/terminate",
        methods=["POST"]
    )
def api_process_terminate():

    data = request.get_json(
        silent=True
    ) or {}

    pid = data.get(
        "pid"
    )

    try:
        pid = int(pid)
    except Exception:

        return jsonify({
    "success":
        False,
        "message":
            "Invalid PID."
        })

        # Do not allow accidental termination
        # of this application itself.
        if pid == os.getpid():

            return jsonify({
        "success":
            False,
            "message":
                "Refusing to terminate the security dashboard."
            })

            success, message = (
                ENGINE.endpoint.terminate(
                    pid
                )
            )

            if success:

                ENGINE.security_event(
                    "Endpoint",
                    "PROCESS_TERMINATED",
                    "HIGH",
                    message,
                    {
                        "pid":
                            pid
                        },
                        alert=True,
                    )

                    return jsonify({
            "success":
                success,
                "message":
                    message
                })


                # ============================================================
                # IOC API
                # ============================================================

    @app.route(
        "/api/ioc/add",
        methods=["POST"]
    )
def api_ioc_add():

    data = request.get_json(
        silent=True
    ) or {}

    ip = str(
        data.get(
            "ip",
            ""
        )
    ).strip()

    description = str(
        data.get(
            "description",
            "Custom threat indicator"
        )
    )

    if not ENGINE.threats.add(
        ip,
        description
    ):

        return jsonify({
    "success":
        False,
        "message":
            "Invalid IP address."
        })

        ENGINE.security_event(
            "Threat Intelligence",
            "IOC_ADDED",
            "MEDIUM",
            f"Added IOC {ip}",
            {
                "ip":
                    ip,
                    "description":
                        description,
                    },
                    alert=False,
                )

                return jsonify({
    "success":
        True,
        "message":
            f"Added threat IOC {ip}."
        })


    @app.route(
        "/api/ioc/remove",
        methods=["POST"]
    )
def api_ioc_remove():

    data = request.get_json(
        silent=True
    ) or {}

    ip = str(
        data.get(
            "ip",
            ""
        )
    ).strip()

    success = (
        ENGINE.threats.remove(
            ip
        )
    )

    return jsonify({
"success":
    success,
    "message":
        (
            f"Removed {ip}."
            if success
            else
            f"{ip} was not found."
        )
    })


    # ============================================================
    # DNS API
    # ============================================================

    @app.route(
        "/api/dns"
    )
def api_dns():

    ip = request.args.get(
        "ip",
        ""
    ).strip()

    if not valid_ip(ip):

        return jsonify({
    "success":
        False,
        "message":
            "Invalid IP."
        })

        hostname = (
            ENGINE.intelligence
            .reverse_dns(ip)
        )

        return jsonify({
    "success":
        True,
        "ip":
            ip,
            "hostname":
                hostname,
            })


            # ============================================================
            # GEO API
            # ============================================================

    @app.route(
        "/api/geolocate"
    )
def api_geolocate():

    ip = request.args.get(
        "ip",
        ""
    ).strip()

    if not valid_ip(ip):

        return jsonify({
    "success":
        False,
        "message":
            "Invalid IP."
        })

        return jsonify(
    ENGINE.intelligence
    .geolocate(ip)
)


# ============================================================
# HOST GEOLOCATION API
# ============================================================

    @app.route("/api/host-location")
    def api_host_location():
        try:
            r = requests.get("https://ipapi.co/json/", timeout=4)
            r.raise_for_status()
            d = r.json()
            return jsonify({
        "success": True,
        "ip": d.get("ip", ""),
        "latitude": float(d["latitude"]),
        "longitude": float(d["longitude"]),
        "city": d.get("city", ""),
        "region": d.get("region", ""),
        "country": d.get("country_name", d.get("country", "")),
        "org": d.get("org", ""),
        "source": "ipapi.co",
    })
        except Exception as exc:
            return jsonify({"success": False, "message": str(exc), "latitude": None, "longitude": None})


        # ============================================================
        # THREAT MAP
        # ============================================================

    @app.route(
        "/api/threat-map",
        methods=["POST"]
    )
def api_threat_map():

    return jsonify(
ENGINE.generate_threat_map()
)


    @app.route(
        "/maps/<path:filename>"
    )
def map_file(filename):

from flask import send_from_directory

return send_from_directory(
str(ENGINE.maps),
filename
)


# ============================================================
# LIVE SSE STREAM
# ============================================================

    @app.route(
        "/api/stream"
    )
def api_stream():

    q = ENGINE.subscribe()

def generate():

    try:

        while ENGINE.running:

            try:

                payload = q.get(
                    timeout=15
                )

                yield (
                    "data: "
                    + json.dumps(
                        payload,
                        default=str
                    )
                    + "\n\n"
                )

            except queue.Empty:

                # SSE heartbeat
                yield ": heartbeat\n\n"

    finally:

        ENGINE.unsubscribe(q)

        return Response(
    generate(),
    mimetype="text/event-stream",
    headers={
        "Cache-Control":
            "no-cache",
            "X-Accel-Buffering":
                "no",
                "Connection":
                    "keep-alive",
                    "Content-Type":
                        "text/event-stream; charset=utf-8",
                    },
                )


                # ============================================================
                # HEALTH
                # ============================================================

    @app.route(
        "/api/health"
    )
def api_health():

    return jsonify({
"status":
    "running",
    "time":
        now_iso(),
        "hostname":
            socket.gethostname(),
            "platform":
                platform.platform(),
                "psutil":
                    psutil.__version__,
                })


                # ============================================================
                # STARTUP
                # ============================================================

def main():

    global ENGINE

    parser = argparse.ArgumentParser(
        description=(
            "Network Security "
            "Real-Time Monitoring System"
        )
    )

    parser.add_argument(
        "--workspace",
        "-w",
        default="~/network_security_workspace",
        help="Workspace directory",
    )

    parser.add_argument(
        "--host",
        default=HOST,
        help="Dashboard bind address",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help="Dashboard port",
    )

    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically open browser",
    )

    args = parser.parse_args()

    print()
    print(
        "=" * 70
    )
    print(
        "NETWORK SECURITY REAL-TIME MONITOR"
    )
    print(
        "=" * 70
    )

    print(
        f"Host:       {socket.gethostname()}"
    )

    print(
        f"Platform:   {platform.platform()}"
    )

    print(
        f"PID:        {os.getpid()}"
    )

    print(
        f"Workspace:  "
        f"{Path(args.workspace).expanduser().resolve()}"
    )

    print()

    ENGINE = SecurityEngine(
        args.workspace
    )

    worker = threading.Thread(
        target=ENGINE.run,
        daemon=True,
        name="security-monitor"
    )

    worker.start()

    url = (
        f"http://{args.host}:"
        f"{args.port}"
    )

    print(
        f"Dashboard:  {url}"
    )

    print()

    print(
        "REAL-TIME DATA SOURCES:"
    )

    print(
        "  [+] psutil network counters"
    )

    print(
        "  [+] psutil TCP/UDP connections"
    )

    print(
        "  [+] psutil process telemetry"
    )

    print(
        "  [+] OS firewall"
    )

    print(
        "  [+] local DNS"
    )

    print(
        "  [+] public IP geolocation"
    )

    print()

    if platform.system() == "Windows":

        print(
            "NOTE: Run as Administrator for "
            "firewall/process controls."
        )

    elif platform.system() == "Linux":

        if os.geteuid() != 0:

            print(
                "NOTE: Not running as root. "
                "Some network/firewall/process "
                "information may be restricted."
            )

            print()

            if not args.no_browser:

                try:

                    threading.Timer(
                        1.2,
                        lambda:
                            webbrowser.open(
                                url
                            )
                        ).start()

                except Exception:
                    pass

                try:

                    app.run(
                        host=args.host,
                        port=args.port,
                        debug=False,
                        threaded=True,
                        use_reloader=False,
                    )

                except KeyboardInterrupt:

                    pass

                                                                finally:

                                                                    if ENGINE:

                                                                        ENGINE.stop()

                                                                        print(
                                                                            "\nNetwork Security System stopped."
                                                                        )


if __name__ == "__main__":
    main()