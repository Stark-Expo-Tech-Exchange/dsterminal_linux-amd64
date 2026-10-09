#!python
# ============================================================
# DSTerminal v6.0.0 — Unified Engine + UI + CLI + Daemon
# ============================================================
"""
Single-file ransomware defense platform.

 

Architecture:
  ┌──────────────┐   ┌────────────┐   ┌────────────┐
  │ DashboardUI  │   │ CLI REPL   │   │ Daemon     │
  └──────┬───────┘   └─────┬──────┘   └─────┬──────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
              ┌───────────────────────────┐
              │      ShieldCore           │
              │  rules · ML · IF · session│
              │  · IOC · auto-response    │
              │  · SIEM · watchdog        │
              └───────────────────────────┘
                           ▼
              Shared workspace + config

Contract:
  - Engine owns ALL detection and response.
  - Dashboard is a thin view. It never scans.
  - CLI is a thin shell. It never duplicates logic.
  - Workspace resolution is centralized.
  - Every alert the user sees was produced by analyze_event().
"""
# ============================================================
# GEVENT MONKEY-PATCH (must happen before other imports)
# ============================================================
# ============================================================
# GEVENT — deferred patch (see cmd_dashboard)
# ============================================================
try:
    import gevent  # noqa: F401  — presence check only
    from gevent import monkey  # noqa: F401
    _GEVENT_AVAILABLE = True
except ImportError:
    _GEVENT_AVAILABLE = False

# Backwards-compat alias used elsewhere in the file
_EVENTLET_OK = _GEVENT_AVAILABLE
import sys
import os
import io
import time
import json
import csv
import signal
import atexit
import shutil
import hashlib
import threading
import glob
import re
import pickle
import numpy
import argparse
import platform
import tempfile
from collections import deque, defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Set, Any, Tuple
from numpy.random import default_rng as _default_rng
# ============================================================
# WINDOWS CONSOLE FIX
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except Exception:
        pass
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        else:
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
            except Exception:
                pass
    except Exception:
        pass

# ============================================================
# OPTIONAL IMPORTS
# ============================================================
# ============================================================
# OPTIONAL MODULES — Reports subsystem
# ============================================================
try:
    from reportlab.lib.pagesizes import letter as _rl_letter
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

# The report generator itself is defined in this file, so this is
# really just a feature flag that the CLI and dashboard consult.
REPORTS_AVAILABLE = True   # always available — HTML+JSON are stdlib

try:
    import numpy as np
except ImportError:
    print("[!] numpy required. Install: pip install numpy")
    sys.exit(1)
try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_OK = True
except ImportError:
    WATCHDOG_OK = False

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_OK = True
except ImportError:
    TORCH_OK = False

try:
    import psutil
    PSUTIL_OK = True
except ImportError:
    PSUTIL_OK = False

try:
    from colorama import init as colorama_init
    colorama_init(autoreset=True, convert=True, strip=False)
    COLORS_OK = True
except ImportError:
    COLORS_OK = False

# Flask is optional — only needed for UI mode
try:
    from flask import Flask, jsonify, render_template_string, request, send_file
    from flask_socketio import SocketIO, emit
    FLASK_OK = True
except ImportError:
    FLASK_OK = False


# ============================================================
# COLORS
# ============================================================
class Colors:
    HEADER = '\033[95m'; BLUE = '\033[94m'; CYAN = '\033[96m'
    GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'
    BOLD = '\033[1m'; UNDERLINE = '\033[4m'; END = '\033[0m'
    DIM = '\033[2m'; BLINK = '\033[5m'; REVERSE = '\033[7m'
    BRIGHT_GREEN = '\033[92;1m'; BRIGHT_RED = '\033[91;1m'
    BRIGHT_YELLOW = '\033[93;1m'; BRIGHT_CYAN = '\033[96;1m'
    BRIGHT_MAGENTA = '\033[95;1m'

    @staticmethod
    def strip(text):
        return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)
# ============================================================
# SYSTEM-WIDE WATCH TARGETS
# ============================================================
# ============================================================
# EMBEDDED DEFAULT MODELS (base64-encoded pickles)
# ============================================================
# ============================================================
# EMBEDDED DEFAULT MODELS (base64-encoded pickles)
# ============================================================
import base64 as _b64

# Trained ThreatClassifier (logistic regression). Regenerate with:
#   cd <workspace>/models
#   python -c "import base64, pathlib; print(base64.encodebytes(pathlib.Path('shield_clf.pkl').read_bytes()).decode())"
# Then paste the output inside the b64decode triple-quoted string below.
_EMBEDDED_CLF_B64 = _b64.b64decode("""
e38+ZpXgPDtH6b7Y0Wu+WpsavnX1Hb/gD7C9qccZPtstqT4nmGW8LZzEvqJeIb8aa4I/RH7ZPikd
AT1m+Kc/rZ09P2Kk8D6UdJRijAFilGgCjAZzY2FsYXKUk5RoDowCZjiUiYiHlFKUKEsDaBJOTk5K
/////0r/////SwB0lGJDCFE2TBxfO80/lIaUUpSMBG1lYW6UaARoB0sAhZRoCYeUUpQoSwFLF4WU
aBGJQ1w3Sr5AITouPz6W1T4X6xc+iQXrPr2q/j6miRM/uohCQoLbpEQ9SQ1BHUfnSIinnD7/+KY/
brtAPlCaQ0Fsv/g+WDDaQGGbpT5OyJQ+51uXPpU0wT6asac+OImaPpR0lGKMA3ZhcpRoBGgHSwCF
lGgJh5RSlChLAUsXhZRoEYlDXC4L2UkHpOdICG0XSNflnkfXnxpIYz8cSNNWakdoE0tPQes+VGR/
mUyHbKBcic6JR2c9JkqJUi9HuY7aSwEDHEiCSTJMK/CJR01eg0fv7IJHyHekRzKvjkf9a3VHlHSU
YowJbl91cGRhdGVzlEoAxAkAjApuX2ZlYXR1cmVzlEsXdS4=
""")


def _materialize_embedded_model(target_path: str, data: bytes) -> bool:
    """Write embedded model bytes to disk if the target doesn't exist."""
    if not data:
        return False
    if os.path.exists(target_path):
        return False
    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'wb') as f:
            f.write(data)
        print(f"[bootstrap] wrote embedded model -> {target_path}")
        return True
    except Exception as e:
        print(f"[bootstrap] failed to materialize embedded model: {e}")
        return False
# ============================================================
# TERMINAL UTILS
# ============================================================
def get_terminal_width() -> int:
    try:
        w = shutil.get_terminal_size().columns
        return min(max(w, 80), 120)
    except Exception:
        return 80

def _json_safe(obj):
    """
    Recursively convert numpy scalars/arrays and tuples into plain
    Python types that Flask's default JSON encoder can handle.
    """
    import numpy as _np_local
    if isinstance(obj, _np_local.generic):
        return obj.item()
    if isinstance(obj, _np_local.ndarray):
        return [_json_safe(v) for v in obj.tolist()]
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, set):
        return [_json_safe(v) for v in obj]
    return obj

def center_text(text: str, width: int = None) -> str:
    if width is None:
        width = get_terminal_width()
    pad = max(0, (width - len(Colors.strip(text))) // 2)
    return ' ' * pad + text

# ============================================================
# CENTERED / BOXED OUTPUT HELPERS
# ============================================================
def _box_width() -> int:
    """Responsive box width based on terminal size."""
    try:
        w = shutil.get_terminal_size().columns
    except Exception:
        w = 80
    return min(max(w, 60), 100)


def cprint(text: str = "", color: str = "", bold: bool = False):
    """Center-print a single line of text."""
    width = _box_width()
    plain = Colors.strip(text)
    pad = max(0, (width - len(plain)) // 2)
    prefix = " " * pad
    if color:
        sys.stdout.write(f"{prefix}{color}")
        if bold:
            sys.stdout.write(Colors.BOLD)
        sys.stdout.write(text)
        sys.stdout.write(Colors.END)
    else:
        sys.stdout.write(f"{prefix}{text}")
    sys.stdout.write("\n")
    sys.stdout.flush()


def ctype(text: str, color: str = Colors.CYAN, delay: float = 0.012,
          centered: bool = True):
    """Type text character-by-character, optionally centered."""
    width = _box_width() if centered else 0
    plain = Colors.strip(text)
    pad = " " * max(0, (width - len(plain)) // 2) if centered else ""

    if color:
        sys.stdout.write(color)
    for ch in pad + text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        if ch not in (" ", "\t"):
            time.sleep(delay)
    if color:
        sys.stdout.write(Colors.END)
    sys.stdout.write("\n")
    sys.stdout.flush()


def print_boxed(title: str, lines: list, color: str = Colors.CYAN,
                width: Optional[int] = None, center: bool = True):
    """
    Draw a bordered box with a title and lines of content.
    All lines are padded to a fixed inner width so the right border
    lines up perfectly regardless of content length.
    """
    if width is None:
        width = _box_width()

    # width is the TOTAL box width including borders.
    # Layout: │ + 2 spaces + content + 2 spaces + │
    inner = width - 6            # content column count

    term_w = get_terminal_width()
    pad = " " * max(0, (term_w - width) // 2) if center else ""

    # ---- Top border with centered title ----
    title_plain = Colors.strip(title)
    if len(title_plain) > inner + 2:
        title_plain = title_plain[:inner - 1] + "…"
    title_seg = f" {title_plain} "
    lead = max(0, (inner + 4 - len(title_seg)) // 2)
    trail = max(0, inner + 4 - len(title_seg) - lead)
    print(f"{pad}{color}┌{'─' * lead}{title_seg}{'─' * trail}┐{Colors.END}")

    # ---- Content rows ----
    for line in lines:
        plain = Colors.strip(line)
        if len(plain) > inner:
            plain = plain[:inner - 3] + "..."
        # Pad using the stripped length, but emit the colored line
        right = " " * max(0, inner - len(plain))
        print(f"{pad}{color}│{Colors.END}  {line}{right}  {color}│{Colors.END}")

    # ---- Bottom border ----
    print(f"{pad}{color}└{'─' * (inner + 4)}┘{Colors.END}")


def print_centered_header(title: str, subtitle: str = "",
                          color: str = Colors.CYAN):
    """Print a centered header with a decorative underline."""
    width = _box_width()
    print()
    cprint(title, color=color, bold=True)
    if subtitle:
        cprint(subtitle, color=Colors.DIM)
    bar = "─" * width
    pad = " " * max(0, (get_terminal_width() - width) // 2)
    print(f"{pad}{Colors.DIM}{bar}{Colors.END}")
    print()

def _hostname() -> str:
    try:
        return os.uname().nodename
    except Exception:
        return os.environ.get("COMPUTERNAME") or "unknown"


OBSERVER_PROCESS_NAMES = {"watchdog", "watcher"}


def _self_process_names() -> Set[str]:
    names = set(OBSERVER_PROCESS_NAMES) | {"shield_core", "shield_core.py",
                                           "dsterminal", "dsterminal.py"}
    try:
        names.add(os.path.basename(sys.argv[0]))
    except Exception:
        pass
    names.add(os.path.basename(sys.executable))
    return {n for n in names if n}


def _is_self_event(event: "FileEvent") -> bool:
    """True only if this event is genuinely us — the running shield process."""
    if event.pid and event.pid == os.getpid():
        return True
    # pid=0 events come from the watcher, not from our own code. They
    # can't be killed, but they can be quarantined. Don't flag them.
    if event.pid == 0:
        return False
    if event.process_name in _self_process_names():
        return True
    return False


# ============================================================
# WORKSPACE RESOLUTION — SINGLE SOURCE OF TRUTH
# ============================================================
def resolve_workspace_dir(explicit: Optional[str] = None) -> str:
    """
    Priority:
      1. explicit argument
      2. DSTERMINAL_WORKSPACE env var
      3. frozen exe → OS-appropriate AppData
      4. script → ~/dsterminal_workspace
    """
    if explicit:
        return os.path.abspath(os.path.expanduser(explicit))

    env = os.environ.get("DSTERMINAL_WORKSPACE")
    if env:
        return os.path.abspath(os.path.expanduser(env))

    if getattr(sys, 'frozen', False):
        if os.name == 'nt':
            base = os.environ.get("APPDATA") or os.path.expanduser("~")
            return os.path.join(base, "DSTerminal", "workspace")
        elif sys.platform == "darwin":
            return os.path.join(os.path.expanduser("~"),
                                "Library", "Application Support",
                                "DSTerminal", "workspace")
        else:
            return os.path.join(os.path.expanduser("~"),
                                ".config", "DSTerminal", "workspace")

    return os.path.expanduser("~/dsterminal_workspace")

# ============================================================
# WATCH ROOT RESOLUTION
# ============================================================
# ============================================================
# WATCH SCOPE HELPERS
# ============================================================
def _user_scope_roots() -> List[str]:
    """
    Return the current user's ransomware-target directories:
    Desktop, Documents, Downloads, Pictures, Videos, Music,
    plus OneDrive and Dropbox if present.

    This is the recommended default scope. It covers what
    ransomware actually encrypts and ignores source trees,
    build outputs, caches, and system files where almost all
    false positives come from.
    """
    home = os.path.expanduser("~")
    out: List[str] = []
    candidates = (
        "Desktop", "Documents", "Downloads",
        "Pictures", "Videos", "Music",
        "OneDrive", "Dropbox",
    )
    for sub in candidates:
        p = os.path.join(home, sub)
        if os.path.isdir(p):
            out.append(os.path.abspath(p))
    return out


# ============================================================
# WATCH ROOT RESOLUTION
# ============================================================
def resolve_watch_roots(explicit: Optional[str]) -> List[str]:
    """
    Return the list of root directories to watch.

    explicit == 'user'   -> Desktop, Documents, Downloads, Pictures,
                            Videos, Music, OneDrive, Dropbox
    explicit == 'all'    -> curated system-wide fan-out
    explicit is a path   -> [that single path]
    explicit is None     -> 'user' scope (the dashboard default)
    """
    # Normalize the argument
    explicit_norm = (explicit or "").strip().lower()

    # ---- 'user' scope (default) ----
    if explicit_norm in ("", "user"):
        roots = _user_scope_roots()
        return roots

    # ---- explicit single path ----
    if explicit_norm != "all":
        return [os.path.abspath(os.path.expanduser(explicit))]

    # ---- 'all' scope: system-wide fan-out ----
    roots: List[str] = []

    if os.name == "nt":
        sys_drive = os.environ.get("SystemDrive", "C:")
        users_root = f"{sys_drive}\\Users"
        if os.path.isdir(users_root):
            skip = {"All Users", "Default", "Default User",
                    "Public", "desktop.ini"}
            try:
                for name in os.listdir(users_root):
                    p = os.path.join(users_root, name)
                    if (os.path.isdir(p) and name not in skip
                            and not name.startswith('.')):
                        roots.append(p)
            except OSError:
                pass

        pd = os.environ.get("ProgramData", f"{sys_drive}\\ProgramData")
        if os.path.isdir(pd):
            roots.append(pd)

        for t in (f"{sys_drive}\\Temp", f"{sys_drive}\\Windows\\Temp"):
            if os.path.isdir(t):
                roots.append(t)

        try:
            import string as _string
            from ctypes import windll
            bitmask = windll.kernel32.GetLogicalDrives()
            for i, letter in enumerate(_string.ascii_uppercase):
                if not (bitmask & (1 << i)):
                    continue
                drive = f"{letter}:\\"
                try:
                    dtype = windll.kernel32.GetDriveTypeW(drive)
                except Exception:
                    continue
                if dtype not in (2, 3, 4):
                    continue
                if drive.rstrip('\\').upper() == sys_drive.upper():
                    continue
                if os.path.isdir(drive):
                    roots.append(drive)
        except Exception:
            pass
    else:
        for c in ("/home", "/root", "/var/tmp", "/tmp", "/mnt", "/media"):
            if os.path.isdir(c):
                roots.append(c)

    # Dedupe and prune nested roots
    existing = []
    for r in roots:
        try:
            ap = os.path.abspath(r)
        except Exception:
            continue
        if os.path.isdir(ap):
            existing.append(ap)

    existing = sorted(set(existing), key=len)
    pruned: List[str] = []
    for r in existing:
        if any(r == p or r.startswith(p + os.sep) for p in pruned):
            continue
        pruned.append(r)
    return pruned
# ============================================================
# AUTO-TYPE ENGINE
# ============================================================
class AutoTypeEngine:
    def __init__(self, delay: float = 0.03):
        self.delay = delay

    def type_text(self, text, color="", end="\n", delay=None, centered=False):
        d = self.delay if delay is None else delay
        out = center_text(text) if centered else text
        if color: sys.stdout.write(color)
        for ch in out:
            sys.stdout.write(ch); sys.stdout.flush(); time.sleep(d)
        if color: sys.stdout.write(Colors.END)
        if end: sys.stdout.write(end)
        sys.stdout.flush()

    def type_status(self, t, c=Colors.CYAN, centered=False):
        self.type_text(f"[*] {t}", c, centered=centered)

    def type_success(self, t, centered=False):
        self.type_text(f"[+] {t}", Colors.GREEN, centered=centered)

    def type_warning(self, t, centered=False):
        self.type_text(f"[!] {t}", Colors.YELLOW, centered=centered)

    def type_error(self, t, centered=False):
        self.type_text(f"[x] {t}", Colors.RED, centered=centered)

    def type_info(self, t, centered=False):
        self.type_text(f"[i] {t}", Colors.CYAN, centered=centered)

    def type_banner(self, lines, color=Colors.CYAN, delay=0.02):
        for ln in lines:
            self.type_text(ln, color=color, delay=delay, centered=True)
            time.sleep(0.04)

    def type_box(self, title, lines, border=Colors.CYAN):
        W = get_terminal_width()
        bw = min(64, W - 10)
        pad = max(0, (W - bw - 2) // 2)
        cl = lambda t: len(Colors.strip(t))
        print(" " * pad + f"{border}┌{'─' * bw}┐{Colors.END}")
        title_t = f" {title} "
        tp = max(0, (bw - cl(title_t)) // 2)
        print(" " * pad + f"{border}│{Colors.END}{' ' * tp}"
              f"{Colors.YELLOW}{Colors.BOLD}{title_t}{Colors.END}"
              f"{' ' * (bw - cl(title_t) - tp)}{border}│{Colors.END}")
        print(" " * pad + f"{border}├{'─' * bw}┤{Colors.END}")
        for line in lines[:20]:
            if cl(line) > bw - 2:
                line = line[:bw - 5] + "..."
            p = max(0, bw - cl(line) - 2)
            print(" " * pad + f"{border}│{Colors.END} {line}"
                  f"{' ' * p} {border}│{Colors.END}")
        print(" " * pad + f"{border}└{'─' * bw}┘{Colors.END}")


# ============================================================
# ENUMS & DATACLASSES
# ============================================================
class ThreatLevel(Enum):
    CLEAN = 0
    SUSPICIOUS = 1
    ANOMALY = 2
    HIGH_RISK = 3
    RANSOMWARE_DETECTED = 4


@dataclass
class FileEvent:
    path: str
    operation: str
    process_name: str
    timestamp: float = field(default_factory=time.time)
    hash: str = ""
    pid: int = 0


@dataclass
class SecurityPolicies:
    allow_mfa_override: bool = True
    block_untrusted_scripts: bool = True
    max_file_ops_per_second: int = 30
    honeypot_paths: List[str] = field(default_factory=list)
    backup_enabled: bool = True
    auto_rollback: bool = True
    deploy_user_honeypots: bool = False


# ============================================================
# FEATURE VECTOR — 23 features
# ============================================================
FEATURE_NAMES_V57 = [
    "file_entropy", "file_size_delta", "extension_changed",
    "is_honeypot", "is_system_path", "is_user_doc", "write_ratio",
    "ops_per_sec", "unique_files_touched", "unique_extensions",
    "avg_file_size", "suspicious_name_score",
    "external_conn_count", "bytes_sent_ratio",
    "hour_of_day", "is_off_hours", "burst_score",
    "parent_proc_suspicious",
    "write_then_rename_rate",
    "read_write_burst",
    "extension_transition_score",
    "repeated_filename_pattern",
    "off_hours_entropy",
]


@dataclass
class FeatureVector:
    file_entropy: float
    file_size_delta: float
    extension_changed: int
    is_honeypot: int
    is_system_path: int
    is_user_doc: int
    write_ratio: float
    ops_per_sec: float
    unique_files_touched: int
    unique_extensions: int
    avg_file_size: float
    suspicious_name_score: float
    external_conn_count: int
    bytes_sent_ratio: float
    hour_of_day: int
    is_off_hours: int
    burst_score: float
    parent_proc_suspicious: float = 0.0
    write_then_rename_rate: float = 0.0
    read_write_burst: float = 0.0
    extension_transition_score: float = 0.0
    repeated_filename_pattern: float = 0.0
    off_hours_entropy: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([
            self.file_entropy, self.file_size_delta, self.extension_changed,
            self.is_honeypot, self.is_system_path, self.is_user_doc,
            self.write_ratio, self.ops_per_sec, self.unique_files_touched,
            self.unique_extensions, self.avg_file_size, self.suspicious_name_score,
            self.external_conn_count, self.bytes_sent_ratio,
            self.hour_of_day, self.is_off_hours, self.burst_score,
            self.parent_proc_suspicious, self.write_then_rename_rate,
            self.read_write_burst, self.extension_transition_score,
            self.repeated_filename_pattern, self.off_hours_entropy,
        ], dtype=np.float32)

    @staticmethod
    def feature_names() -> List[str]:
        return list(FEATURE_NAMES_V57)

    @staticmethod
    def n_features() -> int:
        return len(FEATURE_NAMES_V57)


# ============================================================
# FEATURE EXTRACTOR
# ============================================================
class FeatureExtractor:
    BASENAME_HISTORY_MAX = 50_000
    PRUNE_INTERVAL_SEC = 600.0
    RANSOM_EXTENSIONS = {
        '.locked', '.encrypted', '.crypto', '.crypt', '.enc',
        '.wcry', '.wncry', '.zepto', '.cerber', '.locky',
        '.ryk', '.ryuk', '.conti', '.lockbit', '.revil',
    }
    SYSTEM_PATH_MARKERS = [
        'windows\\system32', 'windows\\syswow64',
        'program files', '/usr/bin', '/usr/lib', '/etc/',
    ]
    USER_DOC_MARKERS = [
        'documents', 'desktop', 'downloads', 'pictures',
        'videos', 'music', '/home/',
    ]
    SCRIPT_INTERPRETERS = {
        'powershell.exe', 'pwsh.exe', 'cmd.exe', 'wscript.exe',
        'cscript.exe', 'mshta.exe', 'rundll32.exe', 'regsvr32.exe',
        'python.exe', 'python3', 'bash', 'sh', 'zsh', 'perl', 'ruby',
        'node', 'php',
    }

    def __init__(self, honeypot_paths: Optional[Set[str]] = None):
        self.honeypot_paths = honeypot_paths or set()
        self.file_history: Dict[str, float] = {}
        self._recent_ops: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self._basename_history: Dict[str, Set[str]] = defaultdict(set)
        self._basename_seen: Dict[str, float] = {}   # basename -> last_touch
        self._hourly_activity: Dict[int, int] = defaultdict(int)
        self._last_prune = time.time()

    def _prune(self, now: float):
        if now - self._last_prune < self.PRUNE_INTERVAL_SEC:
            return
        self._last_prune = now

        # Bound basename history: drop least-recently-seen entries
        if len(self._basename_history) > self.BASENAME_HISTORY_MAX:
            # Sort by last seen; drop oldest 25%
            items = sorted(self._basename_seen.items(), key=lambda kv: kv[1])
            drop = len(items) // 4
            for name, _ in items[:drop]:
                self._basename_history.pop(name, None)
                self._basename_seen.pop(name, None)

        # Bound per-file stat cache
        if len(self.file_history) > 200_000:
            # Simple eviction: keep the most recently touched half.
            # We don't track touch time per path, so just drop oldest keys.
            for k in list(self.file_history.keys())[:len(self.file_history) // 2]:
                self.file_history.pop(k, None)

    def _extension_transition_score(self, event: FileEvent) -> float:
        self._prune(event.timestamp)
        base = os.path.splitext(os.path.basename(event.path))[0]
        ext = os.path.splitext(event.path)[1].lower()
        self._basename_history[base].add(ext)
        self._basename_seen[base] = event.timestamp
        exts = self._basename_history[base]
        if len(exts) < 2: return 0.0
        has_doc = any(e in {'.doc', '.docx', '.xls', '.xlsx', '.pdf',
                            '.ppt', '.pptx', '.txt', '.jpg', '.png'}
                      for e in exts)
        has_ransom = any(e in self.RANSOM_EXTENSIONS for e in exts)
        if has_doc and has_ransom: return 1.0
        if has_ransom: return 0.6
        return 0.0

    def _entropy(self, data: bytes) -> float:
        if not data: return 0.0
        counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
        probs = counts / len(data)
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)))

    def _suspicious_name_score(self, name: str) -> float:
        tokens = ['ransom', 'crypt', 'lock', 'encrypt', 'miner',
                  'worm', 'trojan', 'payload', 'inject']
        n = name.lower()
        hits = sum(1 for t in tokens if t in n)
        return min(1.0, hits / 3.0)

    def _parent_suspicious(self, process_name: str) -> float:
        p = process_name.lower()
        for interp in self.SCRIPT_INTERPRETERS:
            if interp in p:
                return 1.0
        return 0.0

    def _write_then_rename_rate(self, event: FileEvent) -> float:
        ops = self._recent_ops[event.process_name]
        if len(ops) < 4: return 0.0
        now = event.timestamp
        recent = [o for o in ops if now - o['ts'] < 2.0]
        if not recent: return 0.0
        transitions = 0
        for i in range(len(recent) - 1):
            a, b = recent[i], recent[i+1]
            if a['op'] == 'write' and b['op'] in ('delete', 'rename'):
                transitions += 1
        return min(1.0, transitions / max(len(recent), 1))

    def _read_write_burst(self, event: FileEvent) -> float:
        ops = self._recent_ops[event.process_name]
        if len(ops) < 3: return 0.0
        now = event.timestamp
        recent = [o for o in ops if now - o['ts'] < 1.0]
        pairs = 0
        by_path = defaultdict(list)
        for o in recent:
            by_path[o['path']].append(o['op'])
        for path, oplist in by_path.items():
            for i in range(len(oplist) - 1):
                if oplist[i] == 'read' and oplist[i+1] == 'write':
                    pairs += 1
        return min(1.0, pairs / 5.0)

    def _repeated_filename_pattern(self, event: FileEvent) -> float:
        base = os.path.splitext(os.path.basename(event.path))[0]
        return min(1.0, len(self._basename_history.get(base, set())) / 5.0)

    def _off_hours_entropy(self, event: FileEvent) -> float:
        hour = datetime.fromtimestamp(event.timestamp).hour
        self._hourly_activity[hour] += 1
        total = sum(self._hourly_activity.values())
        if total < 10: return 0.0
        p = self._hourly_activity[hour] / total
        return float(min(1.0, max(0.0, 1.0 - p * 24)))

    def extract(self, event: FileEvent,
                process_stats: Dict[str, Any]) -> FeatureVector:
        entropy = 0.0
        size_delta = 0.0
        try:
            if os.path.exists(event.path):
                size = os.path.getsize(event.path)
                with open(event.path, 'rb') as f:
                    sample = f.read(4096)
                entropy = self._entropy(sample)
                prev = self.file_history.get(event.path, size)
                size_delta = (size - prev) / max(prev, 1)
                self.file_history[event.path] = size
        except Exception:
            pass

        ext = os.path.splitext(event.path)[1].lower()
        ext_changed = 1 if ext in self.RANSOM_EXTENSIONS else 0
        p = event.path.lower().replace('/', '\\')
        is_sys = int(any(m in p for m in self.SYSTEM_PATH_MARKERS))
        is_doc = int(any(m in p for m in self.USER_DOC_MARKERS))

        dt = datetime.fromtimestamp(event.timestamp)
        hour = dt.hour

        self._recent_ops[event.process_name].append({
            'ts': event.timestamp, 'op': event.operation, 'path': event.path,
        })

        return FeatureVector(
            file_entropy=entropy,
            file_size_delta=size_delta,
            extension_changed=ext_changed,
            is_honeypot=int(event.path in self.honeypot_paths),
            is_system_path=is_sys,
            is_user_doc=is_doc,
            write_ratio=process_stats.get('write_ratio', 0.5),
            ops_per_sec=process_stats.get('ops_per_sec', 0.0),
            unique_files_touched=process_stats.get('unique_files', 0),
            unique_extensions=process_stats.get('unique_extensions', 0),
            avg_file_size=process_stats.get('avg_file_size', 0.0),
            suspicious_name_score=self._suspicious_name_score(event.process_name),
            external_conn_count=process_stats.get('external_conn', 0),
            bytes_sent_ratio=process_stats.get('bytes_sent_ratio', 0.0),
            hour_of_day=hour,
            is_off_hours=int(hour < 8 or hour > 18),
            burst_score=process_stats.get('burst_score', 1.0),
            parent_proc_suspicious=self._parent_suspicious(event.process_name),
            write_then_rename_rate=self._write_then_rename_rate(event),
            read_write_burst=self._read_write_burst(event),
            extension_transition_score=self._extension_transition_score(event),
            repeated_filename_pattern=self._repeated_filename_pattern(event),
            off_hours_entropy=self._off_hours_entropy(event),
        )


# ============================================================
# LAYER 2a: LOGISTIC REGRESSION
# ============================================================
class ThreatClassifier:
    def __init__(self, n_features: int = None, l2: float = 1e-3,
                 lr: float = 0.05):
        self.n_features = n_features or FeatureVector.n_features()
        self.l2 = l2
        self.lr = lr
        rng = np.random.default_rng(42)
        self.w = rng.normal(0, 0.01, size=self.n_features).astype(np.float32)
        self.b = np.float32(0.0)
        self.n_updates = 0
        self.mean = np.zeros(self.n_features, dtype=np.float32)
        self.var = np.ones(self.n_features, dtype=np.float32)

    def _norm(self, x, update=False):
        if update:
            self.n_updates += 1
            d = x - self.mean
            self.mean += d / self.n_updates
            self.var += d * (x - self.mean)
        std = np.sqrt(self.var / max(self.n_updates, 1)) + 1e-6
        return (x - self.mean) / std

    @staticmethod
    def _sigmoid(z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))

    def predict_proba(self, x):
        xn = self._norm(x, update=False)
        return float(self._sigmoid(float(np.dot(self.w, xn) + self.b)))

    def partial_fit(self, x, y):
        xn = self._norm(x, update=True)
        p = self._sigmoid(float(np.dot(self.w, xn) + self.b))
        g = p - y
        self.w -= self.lr * (g * xn + self.l2 * self.w)
        self.b -= self.lr * g

    def fit(self, X, y, epochs=50, batch_size=32, verbose=False):
        n = len(X)
        if n == 0:
            if verbose:
                print("  [!] No training samples — skipping fit")
            return
        rng = np.random.default_rng(0)
        for ep in range(epochs):
            idx = rng.permutation(n)
            loss = 0.0
            for i in range(0, n, batch_size):
                for j in idx[i:i+batch_size]:
                    xj = self._norm(X[j], update=True)
                    p = self._sigmoid(float(np.dot(self.w, xj) + self.b))
                    loss += -(y[j]*np.log(p+1e-9) +
                              (1-y[j])*np.log(1-p+1e-9))
                    g = p - y[j]
                    self.w -= self.lr * (g * xj + self.l2 * self.w)
                    self.b -= self.lr * g
            if verbose and (ep % 10 == 0 or ep == epochs - 1):
                print(f"  epoch {ep:3d}  loss={loss/n:.4f}")

    def explain(self, x, top_k=5):
        xn = self._norm(x, update=False)
        c = self.w * xn
        return sorted(zip(FeatureVector.feature_names(), c),
                      key=lambda t: abs(t[1]), reverse=True)[:top_k]

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({'w': self.w, 'b': self.b, 'mean': self.mean,
                         'var': self.var, 'n_updates': self.n_updates,
                         'n_features': self.n_features}, f)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            d = pickle.load(f)
        n = d.get('n_features', 17)
        target_n = FeatureVector.n_features()
        c = cls(n_features=target_n)

        def _resize(arr, fill, target):
            arr = np.asarray(arr, dtype=np.float32)
            if len(arr) == target:
                return arr
            if len(arr) > target:
                return arr[:target]
            return np.concatenate([arr, np.full(target - len(arr), fill, dtype=np.float32)])

        c.w = _resize(d['w'], 0.0, target_n)
        c.mean = _resize(d['mean'], 0.0, target_n)
        c.var = _resize(d['var'], 1.0, target_n)
        c.b = np.float32(d['b'])
        c.n_updates = int(d.get('n_updates', 0))
        return c

# ============================================================
# LAYER 2b: PYTORCH MLP
# ============================================================
if TORCH_OK:
    class _MLPNet(nn.Module):
        def __init__(self, n_features: int = None, hidden: int = 32):
            super().__init__()
            nf = n_features or FeatureVector.n_features()
            self.net = nn.Sequential(
                nn.Linear(nf, hidden), nn.ReLU(), nn.Dropout(0.1),
                nn.Linear(hidden, hidden // 2), nn.ReLU(),
                nn.Linear(hidden // 2, 1),
            )
        def forward(self, x):
            return self.net(x).squeeze(-1)


class NeuralThreatClassifier:
    def __init__(self, n_features: int = None, lr: float = 1e-3,
                 weight_decay: float = 1e-4, hidden: int = 32):
        if not TORCH_OK:
            raise ImportError("PyTorch not installed (pip install torch)")
        self.n_features = n_features or FeatureVector.n_features()
        self.lr = lr
        self.weight_decay = weight_decay
        self.hidden = hidden
        self.n_updates = 0
        self.mean = np.zeros(self.n_features, dtype=np.float32)
        self.var = np.ones(self.n_features, dtype=np.float32)
        self.model = _MLPNet(self.n_features, hidden)
        self.opt = torch.optim.Adam(self.model.parameters(),
                                    lr=lr, weight_decay=weight_decay)

    def _norm(self, x, update=False):
        if update:
            self.n_updates += 1
            d = x - self.mean
            self.mean += d / self.n_updates
            self.var += d * (x - self.mean)
        std = np.sqrt(self.var / max(self.n_updates, 1)) + 1e-6
        return (x - self.mean) / std

    def predict_proba(self, x) -> float:
        xn = self._norm(x, update=False)
        self.model.eval()
        with torch.no_grad():
            t = torch.from_numpy(xn.astype(np.float32)).unsqueeze(0)
            return float(torch.sigmoid(self.model(t)).item())

    def partial_fit(self, x, y):
        xn = self._norm(x, update=True)
        self.model.train()
        t = torch.from_numpy(xn.astype(np.float32)).unsqueeze(0)
        target = torch.tensor([float(y)])
        loss = F.binary_cross_entropy_with_logits(self.model(t), target)
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

    def fit(self, X, y, epochs=50, batch_size=64, verbose=False):
        if len(X) == 0:
            if verbose: print("  [!] No samples")
            return
        for xj in X:
            self._norm(xj, update=True)
        Xn = np.stack([self._norm(x, update=False) for x in X])
        Xt = torch.from_numpy(Xn.astype(np.float32))
        yt = torch.from_numpy(y.astype(np.float32))
        n = len(Xt)
        rng = np.random.default_rng(0)
        self.model.train()
        for ep in range(epochs):
            idx = rng.permutation(n)
            total = 0.0
            for i in range(0, n, batch_size):
                b = idx[i:i+batch_size]
                logits = self.model(Xt[b])
                loss = F.binary_cross_entropy_with_logits(logits, yt[b])
                self.opt.zero_grad()
                loss.backward()
                self.opt.step()
                total += loss.item() * len(b)
            if verbose and (ep % 10 == 0 or ep == epochs - 1):
                print(f"  epoch {ep:3d}  loss={total/n:.4f}")

    def explain(self, x, top_k=5):
        xn = self._norm(x, update=False)
        self.model.eval()
        t = torch.from_numpy(xn.astype(np.float32)).unsqueeze(0)
        t.requires_grad_(True)
        logit = self.model(t)
        logit.backward()
        grad = t.grad.detach().cpu().numpy().flatten()
        contrib = grad * xn
        return sorted(zip(FeatureVector.feature_names(), contrib),
                      key=lambda p: abs(p[1]), reverse=True)[:top_k]

    def save(self, path):
        torch.save({'state_dict': self.model.state_dict(),
                    'mean': self.mean, 'var': self.var,
                    'n_updates': self.n_updates,
                    'n_features': self.n_features,
                    'hidden': self.hidden}, path)

    @classmethod
    def load(cls, path):
        d = torch.load(path, weights_only=False)
        obj = cls(n_features=d['n_features'], hidden=d.get('hidden', 32))
        obj.model.load_state_dict(d['state_dict'])
        obj.mean = d['mean']
        obj.var = d['var']
        obj.n_updates = d['n_updates']
        return obj


def make_classifier(backend: str, n_features: int = None, lr: float = 0.05):
    nf = n_features or FeatureVector.n_features()
    if backend == 'torch':
        if TORCH_OK:
            return NeuralThreatClassifier(n_features=nf, lr=1e-3)
        print(f"{Colors.YELLOW}[!] torch not installed; using LR backend{Colors.END}")
    return ThreatClassifier(n_features=nf, lr=lr)


# ============================================================
# MODEL EVALUATOR
# ============================================================
class ModelEvaluator:
    @staticmethod
    def confusion_matrix(y_true, y_pred):
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        tn = int(((y_true == 0) & (y_pred == 0)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        return {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn}

    @staticmethod
    def metrics(y_true, y_pred, y_prob=None):
        cm = ModelEvaluator.confusion_matrix(y_true, y_pred)
        tp, tn, fp, fn = cm['tp'], cm['tn'], cm['fp'], cm['fn']
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-9)
        accuracy = (tp + tn) / max(len(y_true), 1)
        fpr = fp / max(fp + tn, 1)
        fnr = fn / max(fn + tp, 1)
        out = {
            'n': int(len(y_true)),
            'accuracy': round(float(accuracy), 4),
            'precision': round(float(precision), 4),
            'recall': round(float(recall), 4),
            'f1': round(float(f1), 4),
            'fpr': round(float(fpr), 4),
            'fnr': round(float(fnr), 4),
            **cm,
        }
        if y_prob is not None:
            out['roc_auc'] = ModelEvaluator._roc_auc(y_true, y_prob)
            out['pr_auc'] = ModelEvaluator._pr_auc(y_true, y_prob)
            out['brier'] = ModelEvaluator._brier(y_true, y_prob)
        return out

    @staticmethod
    def _roc_auc(y_true, y_prob):
        y_true = np.asarray(y_true)
        y_prob = np.asarray(y_prob)
        order = np.argsort(y_prob)
        y_sorted = y_true[order]
        n_pos = int((y_sorted == 1).sum())
        n_neg = int((y_sorted == 0).sum())
        if n_pos == 0 or n_neg == 0: return 0.5
        ranks = np.arange(1, len(y_sorted) + 1)
        sum_pos_ranks = ranks[y_sorted == 1].sum()
        auc = (sum_pos_ranks - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
        return round(float(auc), 4)

    @staticmethod
    def _pr_auc(y_true, y_prob):
        y_true = np.asarray(y_true).astype(int)
        y_prob = np.asarray(y_prob).astype(float)
        n_pos = int((y_true == 1).sum())
        if n_pos == 0: return 0.0
        order = np.argsort(-y_prob)
        y_sorted = y_true[order]
        tp = np.cumsum(y_sorted)
        ranks = np.arange(1, len(y_sorted) + 1)
        precision_at_k = tp / ranks
        ap = float((precision_at_k * y_sorted).sum() / n_pos)
        return round(ap, 4)

    @staticmethod
    def _brier(y_true, y_prob):
        return round(float(np.mean((y_prob - y_true) ** 2)), 4)

    @staticmethod
    def calibration(y_true, y_prob, n_bins=10):
        bins = np.linspace(0, 1, n_bins + 1)
        rows = []
        for i in range(n_bins):
            lo, hi = bins[i], bins[i+1]
            mask = (y_prob >= lo) & (y_prob < hi)
            if mask.sum() == 0: continue
            rows.append({
                'bin': f"{lo:.1f}-{hi:.1f}",
                'count': int(mask.sum()),
                'avg_pred': round(float(y_prob[mask].mean()), 3),
                'avg_true': round(float(y_true[mask].mean()), 3),
            })
        return rows

    @staticmethod
    def threshold_sweep(y_true, y_prob, thresholds=None):
        if thresholds is None:
            thresholds = np.arange(0.05, 1.0, 0.05)
        rows = []
        for t in thresholds:
            pred = (y_prob >= t).astype(int)
            m = ModelEvaluator.metrics(y_true, pred)
            rows.append({
                'threshold': round(float(t), 2),
                'precision': m['precision'],
                'recall': m['recall'],
                'f1': m['f1'],
                'fpr': m['fpr'],
                'accuracy': m['accuracy'],
            })
        return rows

    @staticmethod
    def print_report(name, m):
        print(f"\n{Colors.BOLD}═══ {name} ═══{Colors.END}")
        print(f"  Samples    : {m['n']}")
        print(f"  Accuracy   : {Colors.GREEN}{m['accuracy']:.4f}{Colors.END}")
        print(f"  Precision  : {m['precision']:.4f}   "
              f"Recall: {m['recall']:.4f}   F1: {m['f1']:.4f}")
        print(f"  FPR        : {m['fpr']:.4f}   FNR: {m['fnr']:.4f}")
        if 'roc_auc' in m:
            print(f"  ROC-AUC    : {m['roc_auc']:.4f}   "
                  f"PR-AUC: {m['pr_auc']:.4f}   Brier: {m['brier']:.4f}")
        print(f"  CM         : TP={m['tp']} TN={m['tn']} "
              f"FP={m['fp']} FN={m['fn']}")


def stratified_split(X, y, test_size=0.2, seed=42):
    rng = np.random.default_rng(seed)
    idx0 = np.where(y == 0)[0]
    idx1 = np.where(y == 1)[0]
    rng.shuffle(idx0)
    rng.shuffle(idx1)
    n0_test = int(len(idx0) * test_size)
    n1_test = int(len(idx1) * test_size)
    test_idx = np.concatenate([idx0[:n0_test], idx1[:n1_test]])
    train_idx = np.concatenate([idx0[n0_test:], idx1[n1_test:]])
    rng.shuffle(test_idx)
    rng.shuffle(train_idx)
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


# ============================================================
# LAYER 3: ISOLATION FOREST
# ============================================================
class AnomalyDetector:
    def __init__(self, n_features: int = None, contamination: float = 0.02,
                 min_samples: int = 500, min_train_calls: int = 3):
        self.n_features = n_features or FeatureVector.n_features()
        self.contamination = contamination
        self.min_samples = min_samples
        self.min_train_calls = min_train_calls
        self.train_calls = 0
        self.model: Optional[Any] = None
        self.buffer: List[np.ndarray] = []

    def observe(self, x, label=None):
        if label == 1: return
        self.buffer.append(x.astype(np.float32))
        if len(self.buffer) > 10000:
            self.buffer = self.buffer[-5000:]

    def train_if_ready(self) -> bool:
        if not SKLEARN_OK: return False
        if len(self.buffer) < self.min_samples: return False
        X = np.stack(self.buffer)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42, n_jobs=-1,
            max_samples=min(len(X), 256),
        )
        self.model.fit(X)
        self.train_calls += 1
        return True

    def score(self, x) -> Tuple[float, int]:
        if self.model is None:
            return 0.0, 0
        denom = max(self.min_train_calls, 1)   # <-- guard
        trust = min(1.0, self.train_calls / float(denom))
        if trust <= 0.0:
            return 0.0, 0
        xr = x.reshape(1, -1)
        raw = float(self.model.score_samples(xr)[0])
        pred = int(self.model.predict(xr)[0])
        anom = float(np.clip(0.5 - raw, 0.0, 1.0)) * trust
        if trust < 1.0:
            pred = 0
        return anom, (1 if pred == -1 else 0)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'buffer': self.buffer[-2000:],
                'train_calls': self.train_calls,
                'contamination': self.contamination,
                'min_samples': self.min_samples,
                'min_train_calls': self.min_train_calls,
                'n_features': self.n_features,
            }, f)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            d = pickle.load(f)
        obj = cls(
            n_features=d.get('n_features', 17),
            contamination=d.get('contamination', 0.02),
            min_samples=d.get('min_samples', 500),
            min_train_calls=d.get('min_train_calls', 3),
        )
        obj.model = d.get('model')
        obj.buffer = d.get('buffer', [])
        obj.train_calls = d.get('train_calls', 0)
        return obj


# ============================================================
# LAYER 4: HYBRID DECISION ENGINE
# ============================================================
@dataclass
class Decision:
    threat_level: ThreatLevel
    rule_score: float
    ml_score: float
    anomaly_score: float
    fused_score: float
    reasons: List[str]
    top_features: List[Tuple[str, float]]


class HybridDecisionEngine:
    MIN_ML_UPDATES = 50

    def __init__(self, classifier, anomaly,
                 ml_weight=0.7, rule_weight=0.25, anomaly_weight=0.05):
        self.clf = classifier
        self.anomaly = anomaly
        self.ml_weight = ml_weight
        self.rule_weight = rule_weight
        self.anomaly_weight = anomaly_weight
        self.feedback_buffer: List[Tuple[np.ndarray, int]] = []

    def _rule_score(self, fv: FeatureVector):
        reasons = []
        score = 0.0
        veto = False
        if fv.is_honeypot:
            return 1.0, ["HONEYPOT TOUCHED"], True
        if fv.extension_changed:
            score += 0.35; reasons.append("Ransomware extension")
        if fv.file_entropy > 7.5:
            score += 0.25; reasons.append(f"High entropy ({fv.file_entropy:.2f})")
        if fv.ops_per_sec > 30:
            score += 0.20; reasons.append(f"Burst write ({fv.ops_per_sec:.0f} ops/s)")
        if fv.unique_extensions > 5:
            score += 0.15; reasons.append(f"Mass ext rewrite ({fv.unique_extensions})")
        if fv.suspicious_name_score > 0.3:
            score += 0.15; reasons.append("Suspicious process name")
        if fv.is_off_hours and fv.ops_per_sec > 10:
            score += 0.10; reasons.append("Off-hours activity")
        if fv.is_system_path and fv.ops_per_sec < 5 and not fv.extension_changed:
            score -= 0.20; reasons.append("Benign system activity")
        if fv.parent_proc_suspicious > 0.5:
            score += 0.10; reasons.append("Script-interpreter parent")
        if fv.extension_transition_score > 0.5:
            score += 0.20; reasons.append("Doc→encrypted transition")
        if fv.write_then_rename_rate > 0.3:
            score += 0.10; reasons.append("Write→rename pattern")
        return max(0.0, min(1.0, score)), reasons, veto

    def decide(self, fv: FeatureVector, learn_ok: bool = True) -> Decision:
        rule_score, reasons, veto = self._rule_score(fv)
        x = fv.to_array()
        ml_score_raw = self.clf.predict_proba(x)
        anom_score, is_anom = self.anomaly.score(x)

        n_upd = getattr(self.clf, "n_updates", 0)
        if n_upd < self.MIN_ML_UPDATES:
            ml_trust = 0.10
            reasons.append(
                f"ML undertrained ({n_upd}/{self.MIN_ML_UPDATES}) — downweighted")
        else:
            ml_trust = 1.0
        ml_score = ml_score_raw * ml_trust

        if veto:
            fused = 1.0
            reasons.append("RULE VETO: forcing malicious")
        else:
            fused = (self.rule_weight * rule_score +
                     self.ml_weight * ml_score +
                     self.anomaly_weight * anom_score)
            if rule_score >= 0.5:
                rule_floor = 0.8 * rule_score
                if fused < rule_floor:
                    fused = rule_floor
                    reasons.append(f"Rule floor applied ({rule_floor:.2f})")
            if rule_score > 0.6 and ml_score > 0.7:
                fused = min(1.0, fused + 0.10)
                reasons.append("Rules + ML agree")

        if fused >= 0.85 or veto:
            level = ThreatLevel.RANSOMWARE_DETECTED
        elif fused >= 0.75:
            level = ThreatLevel.HIGH_RISK
        elif fused >= 0.60:
            level = ThreatLevel.SUSPICIOUS
        elif (is_anom and anom_score > 0.6
              and self.anomaly.train_calls >= self.anomaly.min_train_calls):
            level = ThreatLevel.ANOMALY
            reasons.append(f"Unsupervised anomaly ({anom_score:.2f})")
        else:
            level = ThreatLevel.CLEAN

        # Only pay for explanation when the user will actually see it.
        if level == ThreatLevel.CLEAN and not veto:
            top_feats: List[Tuple[str, float]] = []
        else:
            top_feats = self.clf.explain(x, top_k=5)

        if learn_ok:
            self.anomaly.observe(
                x, label=None if level != ThreatLevel.RANSOMWARE_DETECTED else 1)

        return Decision(
            threat_level=level, rule_score=rule_score,
            ml_score=ml_score_raw, anomaly_score=anom_score,
            fused_score=fused, reasons=reasons, top_features=top_feats,
        )

    def record_feedback(self, fv, true_label):
        x = fv.to_array()
        self.feedback_buffer.append((x, true_label))
        self.clf.partial_fit(x, true_label)
        if true_label == 0:
            self.anomaly.observe(x, label=0)

    def replay_feedback(self, epochs=5):
        if not self.feedback_buffer: return
        X = np.stack([x for x, _ in self.feedback_buffer])
        y = np.array([y for _, y in self.feedback_buffer])
        self.clf.fit(X, y, epochs=epochs)


# ============================================================
# LAYER 5: PROCESS CORRELATION
# ============================================================
@dataclass
class ProcessSession:
    pid: int
    process_name: str
    start_time: float = field(default_factory=time.time)
    events: List[FileEvent] = field(default_factory=list)
    extensions_touched: Set[str] = field(default_factory=set)
    dirs_touched: Set[str] = field(default_factory=set)
    total_bytes_written: int = 0
    total_files: int = 0
    ransomware_ext_hits: int = 0
    honeypot_hits: int = 0
    peak_ops_sec: float = 0.0
    last_decision: Optional[Decision] = None

    def add(self, event: FileEvent):
        self.events.append(event)
        ext = os.path.splitext(event.path)[1].lower()
        self.extensions_touched.add(ext)
        self.dirs_touched.add(os.path.dirname(event.path))
        self.total_files += 1
        if ext in FeatureExtractor.RANSOM_EXTENSIONS:
            self.ransomware_ext_hits += 1
        try:
            self.total_bytes_written += os.path.getsize(event.path)
        except Exception:
            pass

    @property
    def duration_sec(self) -> float:
        if not self.events: return 0.0
        return self.events[-1].timestamp - self.events[0].timestamp

    @property
    def dir_diversity(self) -> int:
        return len(self.dirs_touched)

    @property
    def ext_diversity(self) -> int:
        return len(self.extensions_touched)


class ProcessCorrelator:
    # Caps on session tracking. System-wide watching can generate
    # thousands of sessions per hour; without eviction this dict
    # grows unbounded for the lifetime of the process.
    MAX_SESSIONS = 2000
    MAX_SESSION_AGE_SEC = 3600.0      # drop sessions idle >1h
    EVICT_EVERY_N = 100               # run eviction every N observe calls

    def __init__(self, shield, events_per_check=20, seconds_per_check=30.0):
        self.shield = shield
        self.sessions: Dict[Any, ProcessSession] = {}
        self.events_per_check = events_per_check
        self.seconds_per_check = seconds_per_check
        self.last_check: Dict[Any, float] = {}
        self._observe_count = 0

    def _evict(self):
        """Prune stale and excess sessions."""
        now = time.time()

        # 1. Drop sessions idle longer than MAX_SESSION_AGE_SEC.
        stale = [
            key for key, sess in self.sessions.items()
            if (not sess.events or
                (now - sess.events[-1].timestamp) > self.MAX_SESSION_AGE_SEC)
        ]
        for key in stale:
            self.sessions.pop(key, None)
            self.last_check.pop(key, None)

        # 2. Hard cap: keep only the most recently active MAX_SESSIONS.
        if len(self.sessions) > self.MAX_SESSIONS:
            items = sorted(
                self.sessions.items(),
                key=lambda kv: (kv[1].events[-1].timestamp
                                if kv[1].events else kv[1].start_time),
                reverse=True,
            )
            keep = dict(items[:self.MAX_SESSIONS])
            self.sessions = keep
            self.last_check = {k: v for k, v in self.last_check.items()
                              if k in keep}

    def _resolve_watchdog_pid(self, path: str) -> int:
        if not PSUTIL_OK:
            return 0
        try:
            target = os.path.abspath(path)
        except Exception:
            return 0

        # Cache hit
        cached = self._pid_cache.get(target)
        if cached and time.time() - cached[1] < 30:
            return cached[0]

        try:
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    for fl in p.open_files():
                        if os.path.abspath(fl.path) == target:
                            self._pid_cache[target] = (p.info['pid'], time.time())
                            return p.info['pid']
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        except Exception:
            pass

        self._pid_cache[target] = (0, time.time())
        if len(self._pid_cache) > 500:
            # drop oldest half
            items = sorted(self._pid_cache.items(), key=lambda kv: kv[1][1])
            for k, _ in items[:250]:
                self._pid_cache.pop(k, None)
        return 0

    def _key(self, event: FileEvent):
        # Real PID wins.
        if event.pid:
            return ('pid', event.pid)

        # Watchdog/synthetic: try to resolve the real writer.
        name = event.process_name
        if name in OBSERVER_PROCESS_NAMES:
            real_pid = self._resolve_watchdog_pid(event.path)
            if real_pid:
                return ('pid', real_pid)
            # Fall back to name+directory so different target dirs don't
            # collapse into one giant session.
            return ('name_dir', name, os.path.dirname(event.path))

        # Any other pid-less event: key by (name, dirname).
        return ('name_dir', name, os.path.dirname(event.path))

    def observe(self, event: FileEvent) -> Optional[Decision]:
        # Periodic eviction — cheap and keeps memory bounded under
        # system-wide watching load.
        self._observe_count += 1
        if self._observe_count % self.EVICT_EVERY_N == 0:
            self._evict()

        if event.process_name in OBSERVER_PROCESS_NAMES:
            return None

        key = self._key(event)
        sess = self.sessions.get(key)
        if sess is None:
            sess = ProcessSession(pid=event.pid,
                                  process_name=event.process_name)
            self.sessions[key] = sess
            self.last_check[key] = time.time()
        sess.add(event)

        now = time.time()
        events_since = len(sess.events) % self.events_per_check == 0
        time_since = (now - self.last_check.get(key, now)) > self.seconds_per_check

        if events_since or time_since:
            self.last_check[key] = now
            agg = self._aggregate_decision(sess)
            if agg is not None:
                sess.last_decision = agg
                return agg
        return None

    def _aggregate_decision(self, sess: ProcessSession) -> Optional[Decision]:
        if len(sess.events) < 3:
            return None
        ev_last = sess.events[-1]
        stats = {
            'ops_per_sec': sess.peak_ops_sec,
            'unique_files': sess.total_files,
            'unique_extensions': sess.ext_diversity,
            'avg_file_size': sess.total_bytes_written / max(sess.total_files, 1),
            'write_ratio': 0.95,
            'burst_score': 1.0,
        }
        fv = self.shield.extractor.extract(ev_last, stats)
        fv.unique_files_touched = sess.total_files
        fv.unique_extensions = sess.ext_diversity
        fv.extension_changed = 1 if sess.ransomware_ext_hits > 0 else 0
        fv.is_honeypot = 1 if sess.honeypot_hits > 0 else 0
        d = self.shield.engine.decide(fv, learn_ok=False)

        if (sess.ransomware_ext_hits >= 5
                or sess.dir_diversity >= 3
                or (sess.total_files >= 100 and sess.ext_diversity >= 8)):
            d.reasons.append(
                f"SESSION: {sess.total_files} files across "
                f"{sess.dir_diversity} dirs, {sess.ext_diversity} exts")
            if d.threat_level.value < ThreatLevel.HIGH_RISK.value:
                d.threat_level = ThreatLevel.HIGH_RISK
                d.fused_score = max(d.fused_score, 0.7)
                d.reasons.append("Session-level elevation")
        return d

    def summary(self):
        out = []
        for key, s in self.sessions.items():
            out.append({
                'pid': s.pid, 'process': s.process_name,
                'duration_s': round(s.duration_sec, 1),
                'files': s.total_files, 'dirs': s.dir_diversity,
                'exts': s.ext_diversity,
                'ransom_ext_hits': s.ransomware_ext_hits,
                'peak_ops': round(s.peak_ops_sec, 1),
                'last_level': s.last_decision.threat_level.name
                              if s.last_decision else "-",
            })
        return sorted(out, key=lambda x: -x['files'])

# ============================================================
# LAYER 6: THREAT INTEL
# ============================================================
class ThreatIntel:
    IOC_HASH_FLOOR_BYTES = 4 * 1024
    IOC_HASH_CEIL_BYTES = 10 * 1024 * 1024
    def __init__(self):
        self.hashes: Set[str] = set()
        self.process_patterns: List[re.Pattern] = []
        self.path_patterns: List[re.Pattern] = []
        # NEW: cache keyed by (abspath, mtime_ns, size) -> sha256
        self._hash_cache: Dict[Tuple[str, int, int], str] = {}
        self._hash_cache_max = 20_000

    def hash_file(self, path: str, mtime_ns: int = None,
                  size: int = None) -> str:
        """
        SHA-256 of file contents, cached by (abspath, mtime_ns, size).
        Callers that already stat'd the file should pass mtime_ns/size
        to skip a redundant stat.
        """
        try:
            ap = os.path.abspath(path)
            if mtime_ns is None or size is None:
                st = os.stat(ap)
                mtime_ns = st.st_mtime_ns
                size = st.st_size
            key = (ap, mtime_ns, size)
            cached = self._hash_cache.get(key)
            if cached is not None:
                return cached

            h = hashlib.sha256()
            with open(ap, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    h.update(chunk)
            digest = h.hexdigest()

            # LRU-ish eviction: drop oldest quarter when full
            if len(self._hash_cache) >= self._hash_cache_max:
                drop = len(self._hash_cache) // 4
                for k in list(self._hash_cache.keys())[:drop]:
                    self._hash_cache.pop(k, None)
            self._hash_cache[key] = digest
            return digest
        except Exception:
            return ""

    # Hash bounds: below FLOOR there's nothing useful; above CEIL we
    # refuse to read the whole file for a hot-path check.


    def _consume_line(self, line: str) -> bool:
        if line.startswith('hash:'):
            self.hashes.add(line[5:].strip().lower())
        elif line.startswith('proc:'):
            self.process_patterns.append(re.compile(line[5:].strip(), re.I))
        elif line.startswith('path:'):
            self.path_patterns.append(re.compile(line[5:].strip()))
        elif re.fullmatch(r'[0-9a-fA-F]{64}', line):
            self.hashes.add(line.lower())
        else:
            self.process_patterns.append(re.compile(re.escape(line), re.I))
        return True

    def load_file(self, path: str) -> int:
        n = 0
        with open(path) as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'): continue
                try:
                    if self._consume_line(line): n += 1
                except Exception:
                    continue
        return n

    def load_url(self, url: str) -> int:
        try:
            import requests
        except ImportError:
            raise ImportError("requests not installed")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        n = 0
        for raw in r.text.splitlines():
            line = raw.strip()
            if not line or line.startswith('#'): continue
            try:
                if self._consume_line(line): n += 1
            except Exception:
                continue
        return n

    def match(self, event: FileEvent, file_hash: str = "") -> List[str]:
        hits = []
        if file_hash and file_hash.lower() in self.hashes:
            hits.append(f"IOC hash {file_hash[:12]}…")
        for pat in self.process_patterns:
            if pat.search(event.process_name):
                hits.append(f"IOC process {pat.pattern}")
        for pat in self.path_patterns:
            if pat.search(event.path):
                hits.append(f"IOC path {pat.pattern}")
        return hits

    def save(self, path: str):
        with open(path, 'w') as f:
            for h in sorted(self.hashes): f.write(f"hash:{h}\n")
            for p in self.process_patterns: f.write(f"proc:{p.pattern}\n")
            for p in self.path_patterns: f.write(f"path:{p.pattern}\n")

    @classmethod
    def load(cls, path: str):
        obj = cls()
        if os.path.exists(path):
            try:
                n = obj.load_file(path)
                print(f"[intel] loaded {n} IOCs from {path}")
            except Exception as e:
                print(f"[intel] load failed: {e}")
        # else: silent — no file is a valid state
        return obj

# ============================================================
# AUTO-RESPONSE
# ============================================================
@dataclass
class RollbackEntry:
    path: str
    operation: str
    timestamp: float
    size_at_touch: int = 0
    backup_path: Optional[str] = None
    restored: bool = False
    error: str = ""


class RollbackManager:
    SNAPSHOT_TTL_SEC = 3600.0
    MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024 * 1024   # 2 GB budget
    MAX_SINGLE_FILE_BYTES = 100 * 1024 * 1024     # 100 MB per file
    SWEEP_INTERVAL_SEC = 300.0

    def __init__(self, shield, max_entries_per_process: int = 500):
        self.shield = shield
        self.max_entries_per_process = max_entries_per_process
        self.history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_entries_per_process))
        self._snapshots: Dict[str, Tuple[float, str, int]] = {}
        self._last_sweep = time.time()
        self._snap_lock = threading.Lock() 

    def _sweep(self, now: float):
        """Drop expired snapshot cache entries and .vss files over budget."""
        if now - self._last_sweep < self.SWEEP_INTERVAL_SEC:
            return
        self._last_sweep = now

        # 1) Expire cache entries (do NOT delete files here — they may still
        #    be needed for rollback of recent writes; just forget the cache)
        for path, (ts, _, _) in list(self._snapshots.items()):
            if now - ts > self.SNAPSHOT_TTL_SEC:
                self._snapshots.pop(path, None)

        # 2) Budget enforcement: sum .vss files, evict oldest first
        try:
            entries = []
            total = 0
            for name in os.listdir(self.shield.backup_dir):
                if not name.endswith(".vss"):
                    continue
                full = os.path.join(self.shield.backup_dir, name)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                entries.append((st.st_mtime, full, st.st_size))
                total += st.st_size

            if total <= self.MAX_SNAPSHOT_BYTES:
                return

            entries.sort()  # oldest first
            for _, full, size in entries:
                if total <= self.MAX_SNAPSHOT_BYTES:
                    break
                try:
                    os.remove(full)
                    total -= size
                except OSError:
                    pass
        except Exception:
            pass

    def snapshot_before_write(self, event: FileEvent) -> Optional[str]:
        if not self.shield.policies.backup_enabled:
            return None
        try:
            st = os.stat(event.path)
        except OSError:
            return None
        if st.st_size > self.MAX_SINGLE_FILE_BYTES:
            return None

        now = time.time()
        self._sweep(now)

        with self._snap_lock:
            cached = self._snapshots.get(event.path)
            if cached and (now - cached[0]) < self.SNAPSHOT_TTL_SEC:
                return cached[1]    

        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        dest = os.path.join(self.shield.backup_dir,
                            f"{ts}_{os.path.basename(event.path)}.vss")
        try:
            shutil.copy2(event.path, dest)
            self._snapshots[event.path] = (now, dest, st.st_size)
            return dest
        except Exception:
            return None

    def record(self, event: FileEvent, backup_path: Optional[str]):
        try:
            size = os.path.getsize(event.path) if os.path.exists(event.path) else 0
        except OSError:
            size = 0
        entry = RollbackEntry(
            path=event.path, operation=event.operation,
            timestamp=event.timestamp, size_at_touch=size,
            backup_path=backup_path)
        self.history[event.process_name].append(entry)

    def rollback_process(self, process_name: str,
                         dry_run: bool = False) -> Dict[str, Any]:
        entries = list(self.history.get(process_name, []))
        if not entries:
            return {'process': process_name, 'attempted': 0,
                    'restored': 0, 'failed': 0, 'skipped': 0, 'details': []}
        write_entries = [e for e in entries if e.operation == 'write']
        write_entries.reverse()
        restored = failed = skipped = 0
        details = []
        for e in write_entries:
            if not e.backup_path or not os.path.exists(e.backup_path):
                skipped += 1
                details.append({'path': e.path, 'status': 'no_snapshot'})
                continue
            if dry_run:
                details.append({'path': e.path, 'status': 'would_restore'})
                restored += 1
                continue
            try:
                if os.path.exists(e.path):
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    trash = os.path.join(
                        self.shield.quarantine_dir,
                        f"rollback_{ts}_{os.path.basename(e.path)}.pre")
                    shutil.move(e.path, trash)
                shutil.copy2(e.backup_path, e.path)
                e.restored = True
                restored += 1
                details.append({'path': e.path, 'status': 'restored'})
            except Exception as ex:
                failed += 1
                e.error = str(ex)
                details.append({'path': e.path, 'status': 'failed',
                                'error': str(ex)})
        self.history.pop(process_name, None)
        return {'process': process_name,
                'attempted': len(write_entries),
                'restored': restored, 'failed': failed,
                'skipped': skipped, 'details': details[:50]}

class Whitelist:
    """
    Persistent user-editable process whitelist. Additions are stored
    in a JSON file next to blacklist.json and loaded on startup.

    The built-in defaults (ProcessKiller.DEFAULT_PROTECTED_PROCESSES)
    are always active. User entries are added on top and can be
    removed without touching the defaults.
    """

    def __init__(self, path: str):
        self.path = path
        self.user_entries: Set[str] = set()
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path) as f:
                data = json.load(f)
            if isinstance(data, list):
                self.user_entries = {str(x).lower() for x in data if x}
            elif isinstance(data, dict) and "entries" in data:
                self.user_entries = {str(x).lower()
                                     for x in data["entries"] if x}
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Whitelist load failed: {e}{Colors.END}")
            self.user_entries = set()

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump({
                    'entries': sorted(self.user_entries),
                }, f, indent=2)
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Whitelist save failed: {e}{Colors.END}")

    def add(self, name: str) -> bool:
        n = (name or "").strip().lower()
        if not n:
            return False
        if n in self.user_entries:
            return False
        self.user_entries.add(n)
        self.save()
        return True

    def remove(self, name: str) -> bool:
        n = (name or "").strip().lower()
        if n not in self.user_entries:
            return False
        self.user_entries.discard(n)
        self.save()
        return True

    def all_names(self) -> Set[str]:
        return set(self.user_entries)

    def categorize(self, name: str) -> str:
        """Best-effort category for display. Mirrors the defaults
        so user additions still show up grouped sensibly."""
        n = (name or "").lower()
        n_no_ext = n[:-4] if n.endswith(".exe") else n

        windows_core = {"svchost", "lsass", "csrss", "wininit",
                        "services", "winlogon", "smss", "system",
                        "system idle process", "registry",
                        "memory compression"}
        windows_shell = {"explorer", "dwm", "sihost", "ctfmon",
                         "taskhostw", "runtimebroker", "conhost",
                         "startmenuexperiencehost",
                         "shellexperiencehost", "searchapp",
                         "searchindexer", "searchhost",
                         "textinputhost"}
        security_stack = {"msmpeng", "nissrv", "securityhealthservice",
                          "securityhealthsystray", "windefend"}
        networking = {"dns", "rpcss", "smartscreen"}
        windows_services = {"audiodg", "wmiprvse"}
        third_party_av = {"cb", "carbonblack", "cylancesvc",
                          "sentinelagent", "csexec"}

        if n_no_ext in windows_core:      return 'windows-core'
        if n_no_ext in windows_shell:     return 'windows-shell'
        if n_no_ext in security_stack:    return 'security-stack'
        if n_no_ext in networking:        return 'networking'
        if n_no_ext in windows_services:  return 'windows-services'
        if n_no_ext in third_party_av:    return 'third-party-av'
        return 'user-added'

class ProcessKiller:
    # Built-in defaults. These are always active and cannot be removed
    # through the dashboard — they represent processes whose termination
    # would take down the OS, the shell, or the security stack.
    DEFAULT_PROTECTED_PROCESSES = {
        # Windows core
        "svchost.exe", "lsass.exe", "csrss.exe", "wininit.exe",
        "services.exe", "winlogon.exe", "smss.exe", "system",
        "system idle process", "registry", "memory compression",
        # Windows shell / UI
        "explorer.exe", "dwm.exe", "sihost.exe", "ctfmon.exe",
        "taskhostw.exe", "runtimebroker.exe", "conhost.exe",
        "startmenuexperiencehost.exe", "shellexperiencehost.exe",
        "searchapp.exe", "searchindexer.exe", "searchhost.exe",
        "textinputhost.exe",
        # Security stack
        "msmpeng.exe", "nissrv.exe", "securityhealthservice.exe",
        "securityhealthsystray.exe", "windefend.exe",
        # Networking / RPC
        "dns.exe", "rpcss.exe", "smartscreen.exe",
        # Audio / WMI
        "audiodg.exe", "wmiprvse.exe",
        # Common AV agents
        "cb.exe", "carbonblack.exe", "cylancesvc.exe",
        "sentinelagent.exe", "csexec.exe",
    }

    def __init__(self, shield):
        self.shield = shield
        self.psutil = psutil if PSUTIL_OK else None
        self.available = PSUTIL_OK

        # Persistent user-editable whitelist
        wl_path = os.path.join(shield.models_dir, "whitelist.json")
        self.whitelist = Whitelist(wl_path)

    def _protected_names(self) -> Set[str]:
        """Union of built-in defaults and user-added entries.
        Both are matched case-insensitively with `.exe` normalization."""
        return self.DEFAULT_PROTECTED_PROCESSES | self.whitelist.all_names()

    def _is_protected(self, name: str) -> bool:
        n = (name or "").lower().strip()
        if not n:
            return False
        n_no_ext = n[:-4] if n.endswith(".exe") else n
        for p in self._protected_names():
            p_no_ext = p[:-4] if p.endswith(".exe") else p
            if n == p or n_no_ext == p_no_ext:
                return True
        return False

    def kill_tree(self, pid: int, process_name: str,
                  dry_run: bool = False) -> Dict[str, Any]:
        result = {'pid': pid, 'process': process_name,
                  'killed': [], 'failed': [], 'method': 'none'}

        if pid <= 1:
            result['method'] = 'refused'
            result['failed'].append('pid <= 1')
            return result
        if pid == os.getpid():
            result['method'] = 'refused'
            result['failed'].append('would kill self')
            return result
        try:
            if os.getppid() == pid:
                result['method'] = 'refused'
                result['failed'].append('would kill parent')
                return result
        except Exception:
            pass

        if self._is_protected(process_name):
            result['method'] = 'refused'
            result['failed'].append(f'protected process: {process_name}')
            return result

        if not self.available:
            result['method'] = 'unavailable'
            return result
        if not self.psutil.pid_exists(pid):
            result['method'] = 'not_running'
            return result
        if dry_run:
            result['method'] = 'dry_run'
            try:
                p = self.psutil.Process(pid)
                children = p.children(recursive=True)
                result['killed'] = [p.name()] + [c.name() for c in children]
            except Exception:
                pass
            return result

        try:
            parent = self.psutil.Process(pid)
            children = parent.children(recursive=True)

            for c in children:
                try:
                    if self._is_protected(c.name()):
                        result['method'] = 'refused'
                        result['failed'].append(
                            f'child is protected: {c.name()}')
                        return result
                except Exception:
                    continue

            for c in children:
                try: c.terminate()
                except Exception: pass
            gone, alive = self.psutil.wait_procs(children, timeout=3)
            for c in alive:
                try: c.kill()
                except Exception: pass
            try:
                parent.terminate()
                try: parent.wait(timeout=3)
                except self.psutil.TimeoutExpired: parent.kill()
            except Exception:
                pass
            result['method'] = 'psutil'
            result['killed'] = [process_name] + [c.name() for c in children]
        except Exception as e:
            result['method'] = 'psutil_error'
            result['failed'].append(str(e))
        return result


class ProcessBlacklist:
    def __init__(self, path: str):
        self.path = path
        self.entries: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path) as f:
                self.entries = json.load(f)
        except Exception:
            self.entries = {}
        banned = _self_process_names()
        before = len(self.entries)
        self.entries = {k: v for k, v in self.entries.items() if k not in banned}
        if len(self.entries) != before:
            print(f"{Colors.YELLOW}[!] Purged {before - len(self.entries)} "
                  f"self entries from blacklist{Colors.END}")
            self.save()

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self.entries, f, indent=2)
        except Exception:
            pass

    def add(self, process_name: str, reason: str = "", pid: int = 0):
        if process_name in _self_process_names():
            return
        now = time.time()
        e = self.entries.setdefault(process_name, {
            'hits': 0, 'first_seen': now, 'reasons': []
        })
        e['hits'] += 1
        e['last_seen'] = now
        e['last_pid'] = pid
        if reason and reason not in e['reasons']:
            e['reasons'].append(reason)
            e['reasons'] = e['reasons'][-5:]
        self.save()

    def contains(self, process_name: str) -> bool:
        return process_name in self.entries

    def get(self, process_name: str) -> Optional[Dict[str, Any]]:
        return self.entries.get(process_name)

    def remove(self, process_name: str):
        if process_name in self.entries:
            del self.entries[process_name]
            self.save()

    def summary(self) -> List[Dict[str, Any]]:
        out = []
        for name, e in self.entries.items():
            out.append({
                'process': name, 'hits': e.get('hits', 0),
                'last_seen': e.get('last_seen'),
                'reasons': e.get('reasons', [])[:3],
            })
        return sorted(out, key=lambda x: -x['hits'])


@dataclass
class AutoResponsePolicy:
    kill_process: bool = True
    rollback_files: bool = True
    quarantine_current: bool = True
    blacklist_process: bool = True
    dry_run: bool = False
    min_level: ThreatLevel = ThreatLevel.RANSOMWARE_DETECTED
    always_respond_to_high_risk: bool = False
    enabled: bool = True          # NEW — master switch (Auto-Q toggle)

class AutoResponse:
    def __init__(self, shield, policy: AutoResponsePolicy = None):
        self.shield = shield
        self.policy = policy or AutoResponsePolicy()
        self.rollback = RollbackManager(shield)
        self.killer = ProcessKiller(shield)

    def _is_self(self, event: FileEvent) -> Optional[str]:
        if event.pid and event.pid == os.getpid():
            return f"my pid={os.getpid()}"
        if event.pid == 0:
            return None                       # unattributable, not self
        if event.process_name in _self_process_names():
            return f"self/observer name={event.process_name}"
        return None

    def handle(self, event: FileEvent, d: Decision) -> Dict[str, Any]:
        print(f"[AutoResponse.handle] entered q={self.policy.quarantine_current} dry_run={self.policy.dry_run} path={event.path}")

        self_reason = self._is_self(event)
        if self_reason:
            report = {
                'timestamp': datetime.now().isoformat(),
                'event': asdict(event),
                'decision': {'level': d.threat_level.name,
                             'rule': d.rule_score, 'ml': d.ml_score,
                             'anomaly': d.anomaly_score,
                             'fused': d.fused_score,
                             'reasons': list(d.reasons)},
                'dry_run': self.policy.dry_run,
                'skipped': 'self_process_protection',
                'skipped_reason': self_reason,
                'kill': None, 'quarantine': None,
                'rollback': None, 'blacklist': None,
            }
            self._save_response_report(report)
            return report

        report = {
            'timestamp': datetime.now().isoformat(),
            'event': asdict(event),
            'decision': {'level': d.threat_level.name,
                         'rule': d.rule_score, 'ml': d.ml_score,
                         'anomaly': d.anomaly_score,
                         'fused': d.fused_score,
                         'reasons': list(d.reasons)},
            'dry_run': self.policy.dry_run,
            'kill': None, 'quarantine': None,
            'rollback': None, 'blacklist': None,
        }

        if self.policy.blacklist_process:
            if not self.policy.dry_run:
                self.shield.blacklist.add(
                    event.process_name,
                    reason=f"detected {d.threat_level.name}",
                    pid=event.pid)
            report['blacklist'] = {'process': event.process_name,
                                   'applied': not self.policy.dry_run}

        if self.policy.kill_process and event.pid:
            report['kill'] = self.killer.kill_tree(
                event.pid, event.process_name, dry_run=self.policy.dry_run)

        if self.policy.quarantine_current:
            if self.policy.dry_run:
                report['quarantine'] = {'path': event.path,
                                        'status': 'would_quarantine'}
            else:
                # Tell the UI we're starting a quarantine cycle.
                self.shield._emit_quarantine(
                    'start',
                    path=event.path,
                    process=event.process_name,
                    level=d.threat_level.name,
                )
                ok = self.shield.quarantine_file(event.path)
                report['quarantine'] = {
                    'path': event.path,
                    'status': 'quarantined' if ok else 'failed'}
                # Tell the UI it's done (success or failure).
                self.shield._emit_quarantine(
                    'done',
                    path=event.path,
                    process=event.process_name,
                    level=d.threat_level.name,
                    ok=ok,
                )

        if self.policy.rollback_files:
            summary = self.rollback.rollback_process(
                event.process_name, dry_run=self.policy.dry_run)
            report['rollback'] = summary

        self._save_response_report(report)
        return report

    def _save_response_report(self, report: Dict[str, Any]):
        p = os.path.join(
            self.shield.workspace_dir, "reports",
            f"autoresponse_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json")
        try:
            with open(p, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        except Exception:
            pass

class ReportGenerator:
    """
    Generates well-formatted reports for each detection.
    Outputs: HTML, JSON, PDF (if reportlab is installed).

    Reports are written to:
        <workspace>/ransom/reports/
    with a per-event subdirectory so each detection has its own
    bundle of three files.
    """

    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.reports_root = os.path.join(workspace_dir, "ransom", "reports")
        os.makedirs(self.reports_root, exist_ok=True)
        self._check_pdf_support()

    def _check_pdf_support(self):
        try:
            from reportlab.lib.pagesizes import letter  # noqa: F401
            self.PDF_OK = True
        except ImportError:
            self.PDF_OK = False

    def generate(self, event: "FileEvent", decision: "Decision",
                 response: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Write a full report bundle for a single detection.
        Returns {html, json, pdf, dir}.
        """
        ts = datetime.fromtimestamp(event.timestamp)
        stamp = ts.strftime("%Y%m%d_%H%M%S_%f")
        level = decision.threat_level.name
        safe_name = re.sub(r'[^A-Za-z0-9._-]', '_',
                           os.path.basename(event.path))[:80]
        report_dir = os.path.join(self.reports_root,
                                  f"{stamp}__{level}__{safe_name}")
        os.makedirs(report_dir, exist_ok=True)

        bundle = self._build_bundle(event, decision, response)

        json_path = os.path.join(report_dir, "report.json")
        html_path = os.path.join(report_dir, "report.html")
        pdf_path = os.path.join(report_dir, "report.pdf")

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(bundle, f, indent=2, default=str)
        except Exception as e:
            print(f"{Colors.YELLOW}[!] report JSON write failed: {e}"
                  f"{Colors.END}")

        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self._render_html(bundle))
        except Exception as e:
            print(f"{Colors.YELLOW}[!] report HTML write failed: {e}"
                  f"{Colors.END}")

        pdf_written = False
        if self.PDF_OK:
            try:
                self._render_pdf(bundle, pdf_path)
                pdf_written = True
            except Exception as e:
                print(f"{Colors.YELLOW}[!] report PDF write failed: {e}"
                      f"{Colors.END}")

        return {
            'dir': report_dir,
            'json': json_path,
            'html': html_path,
            'pdf': pdf_path if pdf_written else "",
        }

    def _build_bundle(self, event, decision, response):
        return {
            'report_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'hostname': _hostname(),
            'workspace': self.workspace_dir,
            'event': asdict(event),
            'decision': {
                'level': decision.threat_level.name,
                'rule_score': float(decision.rule_score),
                'ml_score': float(decision.ml_score),
                'anomaly_score': float(decision.anomaly_score),
                'fused_score': float(decision.fused_score),
                'reasons': list(decision.reasons),
                'top_features': [
                    {'name': str(n), 'contribution': float(v)}
                    for n, v in decision.top_features
                ],
            },
            'response': response or {},
        }

    def _render_html(self, bundle: dict) -> str:
        event = bundle['event']
        dec = bundle['decision']
        resp = bundle['response']

        def row(label, value):
            return (f'<tr><td class="lbl">{label}</td>'
                    f'<td class="val">{value}</td></tr>')

        reasons_html = "".join(
            f'<li>{r}</li>' for r in dec.get('reasons', [])
        ) or '<li class="muted">No reasons recorded</li>'

        features_html = "".join(
            f'<tr><td class="lbl">{f["name"]}</td>'
            f'<td class="val">{f["contribution"]:+.4f}</td></tr>'
            for f in dec.get('top_features', [])
        ) or '<tr><td colspan="2" class="muted">No features</td></tr>'

        response_html = self._render_response_section(resp)

        # Severity color
        sev_color = {
            'CLEAN': '#00ff88',
            'SUSPICIOUS': '#ffcc00',
            'HIGH_RISK': '#ff6600',
            'RANSOMWARE_DETECTED': '#ff0033',
            'ANOMALY': '#bc8cff',
        }.get(dec['level'], '#cccccc')

        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>DSTerminal Report - {event.get('path','')}</title>
<style>
  body {{ background: #0a0e17; color: #d0d0d0;
          font-family: 'Segoe UI', 'Courier New', monospace;
          margin: 0; padding: 30px; }}
  .wrap {{ max-width: 980px; margin: 0 auto; }}
  .header {{ border-bottom: 2px solid {sev_color}; padding-bottom: 16px;
             margin-bottom: 24px; }}
  .header h1 {{ color: {sev_color}; font-size: 22px; margin: 0 0 6px 0;
                letter-spacing: 2px; }}
  .header .meta {{ color: #6a7a7a; font-size: 12px; }}
  h2 {{ color: #00ccff; font-size: 13px; letter-spacing: 2px;
        text-transform: uppercase; margin: 24px 0 8px 0; }}
  table {{ width: 100%; border-collapse: collapse;
           background: #0f1520; border-radius: 6px; overflow: hidden; }}
  tr {{ border-bottom: 1px solid #1a2530; }}
  tr:last-child {{ border-bottom: none; }}
  td {{ padding: 8px 12px; font-size: 12px; vertical-align: top; }}
  td.lbl {{ color: #6a7a7a; width: 220px; }}
  td.val {{ color: #d0d0d0; font-family: 'Courier New', monospace;
            word-break: break-all; }}
  .muted {{ color: #4a5a5a; }}
  ul {{ margin: 0; padding-left: 20px; }}
  li {{ font-size: 12px; margin: 4px 0; color: #d0d0d0; }}
  .sev {{ display: inline-block; padding: 3px 10px; border-radius: 10px;
          font-size: 11px; font-weight: bold; letter-spacing: 1px;
          background: {sev_color}22; color: {sev_color};
          border: 1px solid {sev_color}; }}
  .footer {{ margin-top: 40px; padding-top: 12px;
             border-top: 1px solid #1a2530; color: #4a5a5a;
             font-size: 10px; text-align: center; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
</style></head><body>
<div class="wrap">
  <div class="header">
    <h1>DSTERMINAL DETECTION INCIDENT RESPONSE REPORT</h1>
    <div class="meta">
      Generated: {bundle['generated_at']}<br>
      Host: {bundle['hostname']} &nbsp;|&nbsp;
      Workspace: {bundle['workspace']}
    </div>
    <div style="margin-top:12px;">
      <span class="sev">{dec['level']}</span>
      &nbsp; fused score: <b>{dec['fused_score']:.4f}</b>
    </div>
  </div>

  <h2>Event</h2>
  <table>
    {row('Path', event.get('path',''))}
    {row('Operation', event.get('operation',''))}
    {row('Process', event.get('process_name',''))}
    {row('PID', event.get('pid',''))}
    {row('Timestamp', datetime.fromtimestamp(event.get('timestamp',0)).isoformat())}
    {row('File hash', event.get('hash','') or '&mdash;')}
  </table>

  <div class="grid">
    <div>
      <h2>Scores</h2>
      <table>
        {row('Rule', f"{dec['rule_score']:.4f}")}
        {row('ML', f"{dec['ml_score']:.4f}")}
        {row('Anomaly', f"{dec['anomaly_score']:.4f}")}
        {row('Fused', f"<b>{dec['fused_score']:.4f}</b>")}
      </table>
    </div>
    <div>
      <h2>Top features</h2>
      <table>{features_html}</table>
    </div>
  </div>

  <h2>Reasons</h2>
  <ul>{reasons_html}</ul>

  <h2>Auto-response</h2>
  {response_html}

  <div class="footer">
    DSTerminal v6.0 &mdash; Report generated automatically
    by ShieldCore on threat detection.
  </div>
</div>
</body></html>"""

    def _render_response_section(self, resp: dict) -> str:
        if not resp:
            return ('<div class="muted" style="padding:8px 12px;">'
                    'No auto-response was taken for this event.</div>')

        def esc(v):
            if v is None:
                return '&mdash;'
            return str(v)

        rows = []
        if resp.get('skipped'):
            rows.append(
                f'<tr><td class="lbl">Skipped</td>'
                f'<td class="val">{esc(resp.get("skipped"))}'
                f' ({esc(resp.get("skipped_reason",""))})</td></tr>')

        kill = resp.get('kill')
        if kill:
            rows.append(
                f'<tr><td class="lbl">Kill</td><td class="val">'
                f'method={esc(kill.get("method"))}, '
                f'killed={kill.get("killed") or "[]"}, '
                f'failed={kill.get("failed") or "[]"}'
                f'</td></tr>')

        q = resp.get('quarantine')
        if q:
            rows.append(
                f'<tr><td class="lbl">Quarantine</td><td class="val">'
                f'{esc(q.get("status"))} &mdash; {esc(q.get("path"))}'
                f'</td></tr>')

        rb = resp.get('rollback')
        if rb:
            rows.append(
                f'<tr><td class="lbl">Rollback</td><td class="val">'
                f'attempted={esc(rb.get("attempted"))}, '
                f'restored={esc(rb.get("restored"))}, '
                f'failed={esc(rb.get("failed"))}'
                f'</td></tr>')

        bl = resp.get('blacklist')
        if bl:
            rows.append(
                f'<tr><td class="lbl">Blacklist</td><td class="val">'
                f'{esc(bl.get("process"))} &mdash; '
                f'applied={esc(bl.get("applied"))}'
                f'</td></tr>')

        if not rows:
            return ('<div class="muted" style="padding:8px 12px;">'
                    'Response recorded but no actions listed.</div>')

        return '<table>' + ''.join(rows) + '</table>'

    def _render_pdf(self, bundle: dict, out_path: str):
        """Render a PDF using reportlab. Requires: pip install reportlab."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )

        event = bundle['event']
        dec = bundle['decision']
        resp = bundle['response']

        sev_color_map = {
            'CLEAN': colors.HexColor('#00aa55'),
            'SUSPICIOUS': colors.HexColor('#cc9900'),
            'HIGH_RISK': colors.HexColor('#cc5500'),
            'RANSOMWARE_DETECTED': colors.HexColor('#cc0033'),
            'ANOMALY': colors.HexColor('#8c66cc'),
        }
        sev = dec['level']
        accent = sev_color_map.get(sev, colors.HexColor('#666666'))

        doc = SimpleDocTemplate(
            out_path, pagesize=letter,
            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
            topMargin=0.75 * inch, bottomMargin=0.75 * inch,
            title=f"DSTerminal Report - {sev}",
            author="DSTerminal v6.0",
        )

        styles = getSampleStyleSheet()
        h1 = ParagraphStyle('h1', parent=styles['Heading1'],
                            textColor=accent, fontSize=18,
                            spaceAfter=6, fontName='Helvetica-Bold')
        h2 = ParagraphStyle('h2', parent=styles['Heading2'],
                            textColor=colors.HexColor('#005577'),
                            fontSize=11, spaceBefore=14, spaceAfter=4,
                            fontName='Helvetica-Bold')
        body = ParagraphStyle('body', parent=styles['BodyText'],
                              fontSize=9, leading=12)
        muted = ParagraphStyle('muted', parent=body,
                               textColor=colors.HexColor('#666666'))
        label = ParagraphStyle('label', parent=body,
                               textColor=colors.HexColor('#555555'))

        story = []
        story.append(Paragraph("DSTERMINAL DETECTION INCIDENT RESPONSE REPORT", h1))
        story.append(Paragraph(
            f"Host: {bundle['hostname']} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Generated: {bundle['generated_at']}",
            muted))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f'<font color="{accent.hexval()}"><b>{sev}</b></font> '
            f'&nbsp;&nbsp; fused score: '
            f'<b>{dec["fused_score"]:.4f}</b>',
            body))
        story.append(Spacer(1, 12))

        def kv_table(rows):
            data = [[Paragraph(k, label), Paragraph(str(v), body)]
                    for k, v in rows]
            t = Table(data, colWidths=[1.6 * inch, 5.4 * inch])
            t.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('LINEBELOW', (0, 0), (-1, -2), 0.25,
                 colors.HexColor('#dddddd')),
            ]))
            return t

        story.append(Paragraph("Event", h2))
        story.append(kv_table([
            ("Path", event.get('path', '')),
            ("Operation", event.get('operation', '')),
            ("Process", event.get('process_name', '')),
            ("PID", event.get('pid', '')),
            ("Timestamp",
             datetime.fromtimestamp(event.get('timestamp', 0)).isoformat()),
            ("File hash", event.get('hash', '') or "—"),
        ]))

        story.append(Paragraph("Scores", h2))
        story.append(kv_table([
            ("Rule", f"{dec['rule_score']:.4f}"),
            ("ML", f"{dec['ml_score']:.4f}"),
            ("Anomaly", f"{dec['anomaly_score']:.4f}"),
            ("Fused", f"{dec['fused_score']:.4f}"),
        ]))

        if dec.get('top_features'):
            story.append(Paragraph("Top features", h2))
            story.append(kv_table([
                (f["name"], f"{f['contribution']:+.4f}")
                for f in dec['top_features']
            ]))

        story.append(Paragraph("Reasons", h2))
        if dec.get('reasons'):
            for r in dec['reasons']:
                story.append(Paragraph(f"• {r}", body))
        else:
            story.append(Paragraph("No reasons recorded", muted))

        story.append(Paragraph("Auto-response", h2))
        if resp:
            rows = []
            if resp.get('skipped'):
                rows.append(("Skipped", f'{resp["skipped"]} '
                             f'({resp.get("skipped_reason","")})'))
            kill = resp.get('kill')
            if kill:
                rows.append(("Kill",
                             f'method={kill.get("method")}, '
                             f'killed={kill.get("killed") or []}, '
                             f'failed={kill.get("failed") or []}'))
            q = resp.get('quarantine')
            if q:
                rows.append(("Quarantine",
                             f'{q.get("status")} — {q.get("path")}'))
            rb = resp.get('rollback')
            if rb:
                rows.append(("Rollback",
                             f'attempted={rb.get("attempted")}, '
                             f'restored={rb.get("restored")}, '
                             f'failed={rb.get("failed")}'))
            bl = resp.get('blacklist')
            if bl:
                rows.append(("Blacklist",
                             f'{bl.get("process")} — '
                             f'applied={bl.get("applied")}'))
            if rows:
                story.append(kv_table(rows))
            else:
                story.append(Paragraph("Response recorded but no actions",
                                       muted))
        else:
            story.append(Paragraph(
                "No auto-response was taken for this event.", muted))

        story.append(Spacer(1, 24))
        story.append(Paragraph(
            "Generated automatically by ShieldCore.",
            muted))

        doc.build(story)

# ============================================================
# SIEM (compact — full implementations)
# ============================================================
class SiemTarget:
    name = "base"
    def send(self, events): raise NotImplementedError
    def test(self): return True, "not implemented"


class SplunkHEC(SiemTarget):
    name = "splunk"
    def __init__(self, cfg):
        self.url = cfg["url"].rstrip('/')
        self.token = cfg["token"]
        self.index = cfg.get("index", "main")
        self.source = cfg.get("source", "shield_core")
        self.sourcetype = cfg.get("sourcetype", "shield:event")
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)
    def send(self, events):
        try: import requests
        except ImportError: return False
        url = f"{self.url}/services/collector/event"
        headers = {"Authorization": f"Splunk {self.token}",
                   "Content-Type": "application/json"}
        body = "\n".join(json.dumps({
            "time": e.get("timestamp", time.time()), "host": _hostname(),
            "source": self.source, "sourcetype": self.sourcetype,
            "index": self.index, "event": e}) for e in events)
        try:
            r = requests.post(url, data=body, headers=headers,
                              verify=self.verify, timeout=self.timeout)
            return r.status_code in (200, 201)
        except Exception: return False
    def test(self):
        try: import requests
        except ImportError: return False, "requests not installed"
        try:
            r = requests.get(f"{self.url}/services/collector/health",
                             headers={"Authorization": f"Splunk {self.token}"},
                             verify=self.verify, timeout=self.timeout)
            return r.status_code == 200, f"HTTP {r.status_code}"
        except Exception as e: return False, str(e)


class ElasticBulk(SiemTarget):
    name = "elastic"
    def __init__(self, cfg):
        self.url = cfg["url"].rstrip('/')
        self.index = cfg.get("index", "shield-events")
        self.api_key = cfg.get("api_key")
        self.username = cfg.get("username")
        self.password = cfg.get("password")
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)
    def _headers(self):
        h = {"Content-Type": "application/x-ndjson"}
        if self.api_key: h["Authorization"] = f"ApiKey {self.api_key}"
        return h
    def _auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None
    def send(self, events):
        try: import requests
        except ImportError: return False
        idx = self.index
        if "%" in idx: idx = datetime.now().strftime(idx)
        lines = []
        for e in events:
            lines.append(json.dumps({"index": {"_index": idx}}))
            lines.append(json.dumps(e))
        body = "\n".join(lines) + "\n"
        try:
            r = requests.post(f"{self.url}/_bulk", data=body,
                              headers=self._headers(), auth=self._auth(),
                              verify=self.verify, timeout=self.timeout)
            return r.status_code in (200, 201)
        except Exception: return False
    def test(self):
        try: import requests
        except ImportError: return False, "requests not installed"
        try:
            r = requests.get(f"{self.url}/", headers=self._headers(),
                             auth=self._auth(), verify=self.verify,
                             timeout=self.timeout)
            return r.status_code == 200, f"HTTP {r.status_code}"
        except Exception as e: return False, str(e)


class LokiPush(SiemTarget):
    name = "loki"
    def __init__(self, cfg):
        self.url = cfg["url"].rstrip('/')
        self.labels = cfg.get("labels", {"job": "shield_core"})
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)
    def send(self, events):
        try: import requests
        except ImportError: return False
        values = []
        for e in events:
            ts_ns = str(int(e.get("timestamp", time.time()) * 1_000_000_000))
            values.append([ts_ns, json.dumps(e)])
        payload = {"streams": [{"stream": self.labels, "values": values}]}
        try:
            r = requests.post(f"{self.url}/loki/api/v1/push", json=payload,
                              verify=self.verify, timeout=self.timeout)
            return r.status_code in (200, 204)
        except Exception: return False
    def test(self):
        try: import requests
        except ImportError: return False, "requests not installed"
        try:
            r = requests.get(f"{self.url}/ready",
                             verify=self.verify, timeout=self.timeout)
            return r.status_code == 200, f"HTTP {r.status_code}"
        except Exception as e: return False, str(e)


class GenericWebhook(SiemTarget):
    name = "webhook"
    def __init__(self, cfg):
        self.url = cfg["url"]
        self.headers = cfg.get("headers", {})
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)
    def send(self, events):
        try: import requests
        except ImportError: return False
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        try:
            r = requests.post(self.url, json={"events": events},
                              headers=headers, verify=self.verify,
                              timeout=self.timeout)
            return r.status_code in (200, 201, 202, 204)
        except Exception: return False
    def test(self):
        try: import requests
        except ImportError: return False, "requests not installed"
        try:
            r = requests.post(self.url, json={"events": [{"test": True}]},
                              headers=self.headers, verify=self.verify,
                              timeout=self.timeout)
            return r.status_code < 500, f"HTTP {r.status_code}"
        except Exception as e: return False, str(e)


def make_siem_target(cfg):
    t = cfg.get("type", "").lower()
    try:
        if t == "splunk": return SplunkHEC(cfg)
        if t == "elastic": return ElasticBulk(cfg)
        if t == "loki": return LokiPush(cfg)
        if t == "webhook": return GenericWebhook(cfg)
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Bad SIEM target ({t}): {e}{Colors.END}")
    return None


class SiemForwarder:
    def __init__(self, targets=None, batch_size=50, flush_interval=5.0,
                 queue_max=10000):
        self.targets = []
        for cfg in (targets or []):
            t = make_siem_target(cfg)
            if t: self.targets.append(t)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue = deque(maxlen=queue_max)
        self.queue_max = queue_max
        self.dropped = 0
        self.sent = 0
        self.failed = 0
        self._stop = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
    def start(self):
        if not self.targets: return
        if self._thread and self._thread.is_alive(): return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
    def stop(self):
        self._stop.set()
        if self._thread: self._thread.join(timeout=3)
    def emit(self, event_dict):
        with self._lock:
            if len(self.queue) >= self.queue_max: self.dropped += 1
            self.queue.append(event_dict)
    def _drain_batch(self):
        batch = []
        with self._lock:
            while self.queue and len(batch) < self.batch_size:
                batch.append(self.queue.popleft())
        return batch
    def _loop(self):
        last_flush = time.time()
        while not self._stop.is_set():
            batch = self._drain_batch()
            now = time.time()
            if batch and (len(batch) >= self.batch_size or
                        now - last_flush >= self.flush_interval):
                self._send_to_all(batch)
                last_flush = now
            time.sleep(0.25)
        while True:
            batch = self._drain_batch()
            if not batch: break
            self._send_to_all(batch)

    def _send_to_all(self, batch):
        for t in self.targets:
            ok = False
            for attempt in range(3):
                try: ok = t.send(batch)
                except Exception: ok = False
                if ok: break
                time.sleep(0.5 * (2 ** attempt))
            if ok: self.sent += len(batch)
            else: self.failed += len(batch)
    def flush(self, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if not self.queue: return
            time.sleep(0.1)
    def stats(self):
        return {"targets": [t.name for t in self.targets],
                "queued": len(self.queue), "sent": self.sent,
                "failed": self.failed, "dropped": self.dropped}
    def test_targets(self):
        return [(t.name, *t.test()) for t in self.targets]


# ============================================================
# WATCHDOG BRIDGE
# ============================================================
class ShieldEventHandler:
    def __init__(self, shield, ignore_patterns=None):
        self.shield = shield
        self.ignore_patterns = [re.compile(p) for p in (ignore_patterns or [])]
        self._recent: Dict[str, float] = {}
        self._debounce_sec = 0.15

    def _should_ignore(self, path: str) -> bool:
        normalized = path.replace('\\', '/')
        for pat in self.ignore_patterns:
            if pat.search(normalized) or pat.search(path):
                return True
        try:
            ws = os.path.abspath(self.shield.workspace_dir).replace('\\', '/')
            p = os.path.abspath(path).replace('\\', '/')
            if p.startswith(ws): return True
        except Exception:
            pass
        if path.endswith(('.pkl', '.pyc', '.pt', '.log', '.tmp')):
            return True
        base = os.path.basename(path)
        if base.startswith(('~$', '~WR', '~DF', '~PP')):
            return True
        return False

    def _debounced(self, path: str) -> bool:
        now = time.time()
        last = self._recent.get(path, 0)
        if now - last < self._debounce_sec: return True
        self._recent[path] = now
        if len(self._recent) > 5000:
            cutoff = now - 60
            self._recent = {k: v for k, v in self._recent.items() if v > cutoff}
        return False

    def _emit(self, path: str, op: str):
        if self._should_ignore(path): return
        if self._debounced(path): return
        ev = FileEvent(path=path, operation=op,
                    process_name="watchdog", pid=0)
        if op == 'write':
            try:
                if os.path.getsize(path) <= self.shield.intel.IOC_HASH_CEIL_BYTES:
                    ev.hash = self.shield.intel.hash_file(path)
            except OSError:
                pass
        try:
            self.shield.analyze_event(ev)
        except Exception as e:
            print(f"[watchdog] analyze error: {e}")
            
    def dispatch(self, event):
        if getattr(event, 'is_directory', False): return
        et = getattr(event, 'event_type', None)
        if et == 'moved':
            src = getattr(event, 'src_path', None)
            dst = getattr(event, 'dest_path', None)
            if src: self._emit(src, 'delete')
            if dst: self._emit(dst, 'write')
        elif et == 'deleted':
            self._emit(event.src_path, 'delete')
        elif et in ('created', 'modified'):
            self._emit(event.src_path, 'write')


if WATCHDOG_OK:
    class _WatchdogBridge(FileSystemEventHandler):
        def __init__(self, handler):
            super().__init__()
            self.handler = handler
        def on_any_event(self, event):
            try:
                self.handler.dispatch(event)
            except Exception:
                pass


# ============================================================
# CONFIG
# ============================================================
DEFAULT_CONFIG = {
    "workspace": None, "backend": "lr", "shadow_mode": False,
    "deploy_user_honeypots": False, "watch_path": None, "realtime": True,
    "auto_response": {
        "kill_process": True,
        "rollback_files": True,
        "quarantine_current": True,
        "blacklist_process": True,
        "dry_run": False,
        "min_level": "RANSOMWARE_DETECTED",
        "always_respond_to_high_risk": False,   # NEW — explicit opt-in
    },
    "siem": {"enabled": False, "targets": [], "batch_size": 50,
             "flush_interval": 5.0, "queue_max": 10000},
}

def _deep_merge(base, overlay):
    for k, v in overlay.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def load_config(path):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if path and os.path.exists(path):
        try:
            with open(path) as f:
                user = json.load(f)
            _deep_merge(cfg, user)
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Config load failed: {e}{Colors.END}")
    return cfg


# ============================================================
# SHIELDCORE — THE ENGINE
# ============================================================
class ShieldCore:
    def __init__(self, workspace_dir=None, autotrain_if=True,
                 shadow_mode=False, backend="lr",
                 deploy_user_honeypots=False,
                 save_intel_on_exit: bool = True):
        self.workspace_dir = resolve_workspace_dir(workspace_dir)
        self.threat_level = ThreatLevel.CLEAN
        self._threat_level_expires_at = 0.0
        self.event_log = []
        self.honeypot_paths = []
        self.quarantine_dir = None
        self.backup_dir = None
        self.honeypot_dir = None
        self.policies = SecurityPolicies()
        self.policies.deploy_user_honeypots = deploy_user_honeypots
        self.is_active = False
        self._monitor_thread = None
        self._stop_monitoring = False
        self.shadow_mode = shadow_mode
        self.backend = backend
        self.typer = AutoTypeEngine(delay=0.02)
        self.models_dir = os.path.join(self.workspace_dir, "models")
        self.incidents_dir = os.path.join(self.workspace_dir, "incidents")
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.incidents_dir, exist_ok=True)

        ext = 'pt' if backend == 'torch' and TORCH_OK else 'pkl'
        self.clf_path = os.path.join(self.models_dir, f"shield_clf.{ext}")
        self.if_path = os.path.join(self.models_dir, "shield_if.pkl")
        self.intel_path = os.path.join(self.models_dir, "intel.txt")
        self.intel_url_path = os.path.join(self.models_dir, "intel_url.txt")
        self.blacklist_path = os.path.join(self.models_dir, "blacklist.json")
        _materialize_embedded_model(self.clf_path, _EMBEDDED_CLF_B64)
        self._init_workspace()

        # Classifier
        # Classifier — load if trained, otherwise train and save
        if os.path.exists(self.clf_path):
            try:
                if self.clf_path.endswith('.pt'):
                    self.classifier = NeuralThreatClassifier.load(self.clf_path)
                else:
                    self.classifier = ThreatClassifier.load(self.clf_path)
                self.typer.type_success("Loaded classifier")
            except Exception as e:
                self.typer.type_warning(f"Classifier load failed: {e} — retraining")
                self.classifier = self._bootstrap_classifier()
        else:
            self.typer.type_warning("No ML model found — bootstrapping synthetic")
            self.classifier = self._bootstrap_classifier()

        # Anomaly detector — seed with synthetic-clean baseline on first run
        # so it can produce a signal immediately without waiting for real
        # traffic to accumulate. Once enough real events arrive, the normal
        # training loop retrains it on the mixed pool.
        if os.path.exists(self.if_path):
            try:
                self.anomaly = AnomalyDetector.load(self.if_path)
                self.typer.type_success(
                    f"Loaded IsolationForest (train_calls={self.anomaly.train_calls})")
            except Exception as e:
                self.typer.type_warning(f"IF load failed: {e} — reseeding")
                self.anomaly = AnomalyDetector()
                self._bootstrap_anomaly()
        else:
            self.anomaly = AnomalyDetector()
            self._bootstrap_anomaly()

        self.intel = ThreatIntel.load(self.intel_path)
        self.extractor = FeatureExtractor(honeypot_paths=set(self.honeypot_paths))
        self.engine = HybridDecisionEngine(self.classifier, self.anomaly)

        self.process_stats = defaultdict(lambda: {
            'ops': deque(maxlen=500), 'files': set(), 'extensions': set(),
            'sizes': deque(maxlen=200), 'reads': 0, 'writes': 0,
        })

        self.correlator = ProcessCorrelator(self, events_per_check=20)
        self.autotrain_if = autotrain_if
        self._anomaly_hits = defaultdict(int)

        self.blacklist = ProcessBlacklist(self.blacklist_path)
        self.auto_response_policy = AutoResponsePolicy()
        self.auto_response = AutoResponse(self, self.auto_response_policy)
        self.siem = None
        self.reporter = ReportGenerator(self.workspace_dir)

        self.save_intel_on_exit = bool(save_intel_on_exit)
        # v6.0: event callback for external consumers (dashboard)
        self._event_callback = None
        self._quarantine_callback = None

        if self.shadow_mode:
            self.typer.type_warning("SHADOW MODE: detections logged only")
        if self.policies.deploy_user_honeypots:
            self.typer.type_warning("User-directory honeypots ENABLED")

    # ========================================================
    # MODEL BOOTSTRAP — called on first run when models are missing
    # ========================================================
    def _bootstrap_classifier(self):
        """Train a fresh classifier on synthetic data and persist it."""
        try:
            print(f"{Colors.CYAN}[*] Generating synthetic training data...{Colors.END}")
            X, y = generate_realistic_synthetic(n_benign=4000, n_malicious=4000)
            print(f"{Colors.CYAN}[*] Training {self.backend} on {len(X)} samples...{Colors.END}")
            clf = make_classifier(self.backend)
            clf.fit(X, y, epochs=80, batch_size=64, verbose=True)
            try:
                clf.save(self.clf_path)
                size_kb = os.path.getsize(self.clf_path) / 1024
                print(f"{Colors.GREEN}[+] Classifier trained and saved → "
                      f"{self.clf_path} ({size_kb:.1f} KB){Colors.END}")
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Save failed: {e}{Colors.END}")
            return clf
        except Exception as e:
            print(f"{Colors.RED}[!] Bootstrap failed: {e}{Colors.END}")
            return make_classifier(self.backend)
            
    def _bootstrap_anomaly(self):
        """
        Prefill the IsolationForest training buffer with synthetic-clean
        feature vectors so it can train immediately on a fresh install.
        Without this, IF stays dormant until ~500 real benign events
        accumulate, which may take hours.

        Note: seed distribution is intentionally broad so the model
        doesn't flag legitimate variation as anomalous. False-positive
        rate self-corrects as real events are mixed in during retraining.
        """
        try:
            from numpy.random import default_rng
            rng = _default_rng(7)
            NF = FeatureVector.n_features()

            for _ in range(600):
                v = np.zeros(NF, dtype=np.float32)
                v[0]  = rng.normal(4.2, 0.9)          # entropy
                v[1]  = rng.normal(0.01, 0.03)        # size delta
                v[2]  = 0                              # extension_changed
                v[3]  = 0                              # is_honeypot
                v[4]  = rng.integers(0, 2)            # is_system_path
                v[5]  = rng.integers(0, 2)            # is_user_doc
                v[6]  = rng.uniform(0.15, 0.65)       # write_ratio
                v[7]  = rng.uniform(0, 4)             # ops_per_sec
                v[8]  = rng.integers(1, 20)           # unique_files
                v[9]  = rng.integers(1, 4)            # unique_extensions
                v[10] = rng.uniform(1e3, 8e5)         # avg_file_size
                v[11] = rng.uniform(0, 0.05)          # suspicious_name_score
                v[12] = 0                              # external_conn_count
                v[13] = 0.0                            # bytes_sent_ratio
                v[14] = rng.integers(8, 19)           # hour_of_day
                v[15] = 0                              # is_off_hours
                v[16] = rng.uniform(0.7, 1.4)         # burst_score
                # remaining features stay at 0 (they're recent additions)

                self.anomaly.observe(v, label=0)

            if self.anomaly.train_if_ready():
                try:
                    self.anomaly.save(self.if_path)
                    self.typer.type_success(
                        f"IsolationForest seeded and trained on "
                        f"{len(self.anomaly.buffer)} synthetic samples")
                except Exception as e:
                    self.typer.type_warning(f"IF save failed: {e}")
            else:
                self.typer.type_warning(
                    "IsolationForest not ready after seed — will train later")
        except Exception as e:
            self.typer.type_warning(f"IF bootstrap failed: {e}")

    # ========================================================

    def _init_workspace(self):
        subdirs = ["reports", "logs", "quarantine", "backups", "honeypots",
                   "models", "incidents", "training"]
        for sd in subdirs:
            p = os.path.join(self.workspace_dir, sd)
            os.makedirs(p, exist_ok=True)
            if sd == "quarantine": self.quarantine_dir = p
            elif sd == "backups": self.backup_dir = p
            elif sd == "honeypots": self.honeypot_dir = p
        self._deploy_honeypots()

    def _deploy_honeypots(self):
        deployed = 0
        for name, content in [
            ("honeypot_1.txt", "HONEYPOT - DO NOT MODIFY"),
            ("honeypot_2.txt", "HONEYPOT - DO NOT MODIFY"),
            ("system_backup.bak", "HONEYPOT - System Backup"),
        ]:
            try:
                p = os.path.join(self.honeypot_dir, name)
                with open(p, 'w') as f:
                    f.write(f"{content}\nCreated: {datetime.now()}\n")
                self.honeypot_paths.append(p)
                deployed += 1
            except Exception:
                pass

        if self.policies.deploy_user_honeypots:
            for profile in self._get_all_user_profiles():
                for sub, fname, cont in [
                    ("Documents", "honeypot_1.txt", "HONEYPOT - User Doc"),
                    ("Desktop", "honeypot_2.txt", "HONEYPOT - User Desktop"),
                    ("Downloads", "system_backup.bak", "HONEYPOT - User DL"),
                ]:
                    try:
                        d = os.path.join(profile, sub)
                        os.makedirs(d, exist_ok=True)
                        p = os.path.join(d, fname)
                        if not os.path.exists(p):
                            with open(p, 'w') as f:
                                f.write(f"{cont}\nDeployed: {datetime.now()}\n")
                            self.honeypot_paths.append(p)
                            deployed += 1
                    except Exception:
                        pass

    def _get_all_user_profiles(self):
        profiles = []
        try:
            if os.name == 'nt':
                base = "C:\\Users"
                if os.path.exists(base):
                    skip = {'All Users', 'Default', 'Default User',
                            'Public', 'desktop.ini'}
                    for u in os.listdir(base):
                        p = os.path.join(base, u)
                        if os.path.isdir(p) and u not in skip and not u.startswith('.'):
                            profiles.append(p)
            else:
                base = "/home"
                if os.path.exists(base):
                    for u in os.listdir(base):
                        p = os.path.join(base, u)
                        if os.path.isdir(p) and not u.startswith('.'):
                            profiles.append(p)
                if os.path.exists('/root'):
                    profiles.append('/root')
        except Exception:
            pass
        cur = os.path.expanduser("~")
        if cur not in profiles:
            profiles.append(cur)
        return profiles

    def _update_process_stats(self, event: FileEvent):
        s = self.process_stats[event.process_name]
        now = event.timestamp
        s['ops'].append(now)
        s['files'].add(event.path)
        s['extensions'].add(os.path.splitext(event.path)[1].lower())
        if event.operation == 'write':
            s['writes'] += 1
        else:
            s['reads'] += 1
        try:
            s['sizes'].append(os.path.getsize(event.path))
        except Exception:
            pass
        recent = [t for t in s['ops'] if now - t < 5.0]
        ops_sec = len(recent) / 5.0
        long_r = [t for t in s['ops'] if now - t < 60.0]
        long_rate = len(long_r) / 60.0
        burst = ops_sec / max(long_rate, 0.01)
        return {
            'ops_per_sec': ops_sec,
            'unique_files': len(s['files']),
            'unique_extensions': len(s['extensions']),
            'avg_file_size': float(np.mean(s['sizes'])) if s['sizes'] else 0.0,
            'write_ratio': s['writes'] / max(1, s['writes'] + s['reads']),
            'burst_score': burst,
        }

    def _apply_intel(self, event: FileEvent, d: Decision) -> Decision:
        if not (self.intel.hashes or self.intel.process_patterns
                or self.intel.path_patterns):
            return d

        fh = ""
        if event.operation == 'write' and event.hash:
            fh = event.hash
        elif event.operation == 'write' and self.intel.hashes:
            try:
                st = os.stat(event.path)
                if (self.intel.IOC_HASH_FLOOR_BYTES
                        <= st.st_size
                        <= self.intel.IOC_HASH_CEIL_BYTES):
                    fh = self.intel.hash_file(
                        event.path,
                        mtime_ns=st.st_mtime_ns,
                        size=st.st_size)
            except OSError:
                fh = ""

        hits = self.intel.match(event, fh)
        if hits:
            d.threat_level = ThreatLevel.RANSOMWARE_DETECTED
            d.fused_score = 1.0
            d.reasons.insert(0, "IOC MATCH: " + "; ".join(hits))
        return d

    def _siem_emit(self, event, d, kind="event"):
        if not self.siem:
            return
        self.siem.emit({
            "kind": kind, "timestamp": event.timestamp,
            "host": _hostname(),
            "event": {"path": event.path, "operation": event.operation,
                      "process_name": event.process_name, "pid": event.pid},
            "decision": {"level": d.threat_level.name, "rule": d.rule_score,
                         "ml": d.ml_score, "anomaly": d.anomaly_score,
                         "fused": d.fused_score, "reasons": d.reasons},
            "workspace": self.workspace_dir,
        })
    
    def _emit_quarantine(self, phase, path, process, level, ok=None):
        cb = getattr(self, "_quarantine_callback", None)
        print(f"[_emit_quarantine] phase={phase} cb={'yes' if cb else 'NONE'} path={path}")
        if cb is None:
            return

        try:
            cb({
                'phase': phase,
                'path': path,
                'process': process,
                'level': level,
                'ok': ok,
                'timestamp': time.time(),
            })
        except Exception:
            pass


    def _log_decision(self, event: FileEvent, d: Decision):
        color = {
            ThreatLevel.CLEAN: Colors.GREEN,
            ThreatLevel.SUSPICIOUS: Colors.YELLOW,
            ThreatLevel.HIGH_RISK: Colors.BRIGHT_YELLOW,
            ThreatLevel.RANSOMWARE_DETECTED: Colors.BRIGHT_RED,
            ThreatLevel.ANOMALY: Colors.BRIGHT_MAGENTA,
        }.get(d.threat_level, Colors.END)
        fname = os.path.basename(event.path)[:40]
        print(f"{color}[{d.threat_level.name:22s}]{Colors.END} "
              f"{fname:40s} "
              f"rule={d.rule_score:.2f} ml={d.ml_score:.2f} "
              f"anom={d.anomaly_score:.2f} fused={d.fused_score:.2f}")

    def analyze_event(self, event: FileEvent) -> Decision:
        backup_path = None
        if event.operation == 'write':
            backup_path = self.auto_response.rollback.snapshot_before_write(event)
            self.auto_response.rollback.record(event, backup_path)

        self.event_log.append(event)

        # --- Stats + features computed ONCE ---
        stats = self._update_process_stats(event)
        key = event.pid if event.pid else (hash(event.process_name) & 0xFFFFFFFF)
        sess = self.correlator.sessions.get(key)
        if sess is not None:
            sess.peak_ops_sec = max(sess.peak_ops_sec, stats['ops_per_sec'])

        fv = self.extractor.extract(event, stats)
        d = self.engine.decide(fv)
        d = self._apply_intel(event, d)

        if (not _is_self_event(event)
                and self.blacklist.contains(event.process_name)):
            entry = self.blacklist.get(event.process_name)
            if d.threat_level.value < ThreatLevel.HIGH_RISK.value:
                d.threat_level = ThreatLevel.HIGH_RISK
                d.fused_score = max(d.fused_score, 0.65)
                d.reasons.append(
                    f"Blacklisted process (hits={entry.get('hits', 0)})")

        self._log_decision(event, d)

        if d.threat_level.value >= ThreatLevel.SUSPICIOUS.value:
            self._siem_emit(event, d, kind="detection")

        agg = self.correlator.observe(event)
        if agg and agg.threat_level.value > d.threat_level.value:
            if agg.threat_level.value >= self.auto_response_policy.min_level.value:
                d = agg
            else:
                self._siem_emit(event, agg, kind="session_elevation")

        if d.threat_level == ThreatLevel.ANOMALY:
            self._anomaly_hits[event.process_name] += 1
            if self._anomaly_hits[event.process_name] >= 5:
                d.threat_level = ThreatLevel.HIGH_RISK
                d.fused_score = max(d.fused_score, 0.65)
                d.reasons.append("Escalated: 5+ anomalies")

        # Persist incident with the SAME feature vector we decided on
        self._save_incident(event, d, fv)

        # Notify external consumers (dashboard)
        if self._event_callback:
            try:
                self._event_callback(
                    event_dict=asdict(event),
                    decision_dict={
                        'level': d.threat_level.name,
                        'rule': d.rule_score,
                        'ml': d.ml_score,
                        'anomaly': d.anomaly_score,
                        'fused': d.fused_score,
                        'reasons': list(d.reasons),
                        'top_features': d.top_features,
                    })
            except Exception as cb_err:
                print(f"[callback] {cb_err}")

        # --- Single, explicit auto-response gate ---
        # --- Auto-response gate (single call) ---
        response_data = None
        if d.threat_level.value >= self.auto_response_policy.min_level.value:
            response_data = self._respond_to_threat(event, d)

        # Track highest recent threat level; decay after hold window
        if d.threat_level.value > ThreatLevel.CLEAN.value:
            self.threat_level = d.threat_level
            self._threat_level_expires_at = time.time() + 25.0
        elif (hasattr(self, "_threat_level_expires_at")
              and time.time() >= self._threat_level_expires_at):
            self.threat_level = ThreatLevel.CLEAN

        if d.threat_level.value >= ThreatLevel.SUSPICIOUS.value:
            try:
                self.reporter.generate(event, d, response_data)
            except Exception as rpt_err:
                print(f"[report] generation failed: {rpt_err}")

        return d


    def _respond_to_threat(self, event, d):
        if self.shadow_mode:
            return None
        if event.pid and event.pid == os.getpid():
            return None
        report = self.auto_response.handle(event, d)
        self._siem_emit(event, d, kind="response")
        return report

    def _save_incident(self, event: FileEvent, d: Decision,
                       fv: "FeatureVector"):
        """
        Persist incident using the exact FeatureVector used for the decision.

        Write policy:
          - normal mode : only SUSPICIOUS and above
          - shadow mode : SUSPICIOUS and above, PLUS a small deterministic
                          sample of CLEAN events (for offline review) —
                          sampling avoids writing one JSON per file touch.
        """
        level_val = d.threat_level.value
        is_clean = level_val < ThreatLevel.SUSPICIOUS.value

        if is_clean:
            if not self.shadow_mode:
                return
            # Shadow mode: sample ~1 in 200 CLEAN events to keep disk sane
            if (hash((event.path, event.process_name)) & 0xFF) != 0:
                return

        p = os.path.join(
            self.incidents_dir,
            f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{event.process_name}.json")
        try:
            with open(p, 'w') as f:
                json.dump({
                    'event': asdict(event),
                    'features': fv.to_array().tolist(),
                    'feature_names': FeatureVector.feature_names(),
                    'decision': {'level': d.threat_level.name,
                                 'rule': d.rule_score, 'ml': d.ml_score,
                                 'anomaly': d.anomaly_score,
                                 'fused': d.fused_score,
                                 'reasons': d.reasons},
                    'label': None,
                    'shadow': self.shadow_mode,
                }, f, indent=2)
        except Exception:
            pass

    def generate_forensic_report(self):
        rep = {
            "timestamp": datetime.now().isoformat(),
            "threat_level": self.threat_level.name,
            "events_analyzed": len(self.event_log),
            "honeypots_deployed": len(self.honeypot_paths),
            "quarantine_dir": self.quarantine_dir,
            "backup_dir": self.backup_dir,
            "model_path": self.clf_path,
            "if_buffer_size": len(self.anomaly.buffer),
            "if_train_calls": self.anomaly.train_calls,
            "blacklist": self.blacklist.summary()[:20],
            "sessions": self.correlator.summary()[:10],
        }
        p = os.path.join(self.workspace_dir, "reports",
                         f"forensic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(p, 'w') as f:
                json.dump(rep, f, indent=2)
        except Exception:
            pass
        return rep

    def quarantine_file(self, file_path):
        if not os.path.exists(file_path):
            return False
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = os.path.join(self.quarantine_dir,
                            f"{ts}_{os.path.basename(file_path)}.locked")
        try:
            shutil.move(file_path, dest)
            return True
        except Exception:
            return False

    def learn_from_feedback(self, event, true_label):
        stats = self._update_process_stats(event)
        fv = self.extractor.extract(event, stats)
        self.engine.record_feedback(fv, true_label)
        self.save_models()

    def save_models(self):
        try: self.classifier.save(self.clf_path)
        except Exception: pass
        try: self.anomaly.save(self.if_path)
        except Exception: pass
        if getattr(self, "save_intel_on_exit", True):
            try: self.intel.save(self.intel_path)
            except Exception: pass
        try: self.blacklist.save()
        except Exception: pass

    def train_anomaly_now(self):
        ok = self.anomaly.train_if_ready()
        if ok:
            self.anomaly.save(self.if_path)
        return ok

    def get_status(self):
        # Decay if the hold window expired and nothing refreshed it
        if (self.threat_level != ThreatLevel.CLEAN
                and time.time() >= getattr(self, "_threat_level_expires_at", 0)):
            self.threat_level = ThreatLevel.CLEAN
        return {
            "threat_level": self.threat_level.name,
            "is_active": self.is_active,
            "shadow_mode": self.shadow_mode,
            "backend": self.backend,
            "events_monitored": len(self.event_log),
            "honeypots": len(self.honeypot_paths),
            "workspace_dir": self.workspace_dir,
            "ml_updates": self.classifier.n_updates,
            "ml_trusted": self.classifier.n_updates >= HybridDecisionEngine.MIN_ML_UPDATES,
            "if_samples": len(self.anomaly.buffer),
            "if_ready": self.anomaly.model is not None,
            "if_train_calls": self.anomaly.train_calls,
            "if_trusted": self.anomaly.train_calls >= self.anomaly.min_train_calls,
            "sessions_tracked": len(self.correlator.sessions),
            "ioc_hashes": len(self.intel.hashes),
            "blacklist_size": len(self.blacklist.entries),
            "siem_enabled": self.siem is not None,
        }

    def start_monitoring(self):
        if self.is_active: return
        self.is_active = True
        self._stop_monitoring = False

        def loop():
            n = 0
            while not self._stop_monitoring:
                try:
                    n += 1
                    # Retrain every ~100 seconds while undertrained, then
                    # every ~30 minutes once trusted.
                    if n % 20 == 0 and self.autotrain_if:
                        needs_train = (
                            self.anomaly.model is None
                            or self.anomaly.train_calls < self.anomaly.min_train_calls
                        )
                        if needs_train:
                            if self.anomaly.train_if_ready():
                                try:
                                    self.anomaly.save(self.if_path)
                                    print(
                                        f"[autotrain] IF retrained — "
                                        f"train_calls={self.anomaly.train_calls}"
                                    )
                                except Exception:
                                    pass
                        elif n % 360 == 0:
                            # Every 30 min, refresh the model on new data
                            if self.anomaly.train_if_ready():
                                try:
                                    self.anomaly.save(self.if_path)
                                except Exception:
                                    pass
                    time.sleep(5)
                except Exception:
                    time.sleep(10)

        self._monitor_thread = threading.Thread(target=loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        self._stop_monitoring = True
        self.is_active = False


# ============================================================
# SHIELDENGINEAPI — the facade the dashboard calls
# ============================================================
class ShieldEngineAPI:
    """
    Frontend facade over ShieldCore.

    Contract:
      - The engine owns detection, response, and state.
      - The dashboard only reads via this API.
      - Commands go through this API back to the engine.
      - No parallel detection, no mock fallback.
    """

    def __init__(self, workspace_dir: str = None,
                 backend: str = "lr",
                 shadow_mode: bool = False,
                 save_intel_on_exit: bool = False):
        self.workspace_dir = resolve_workspace_dir(workspace_dir)
        self.shield = ShieldCore(
            workspace_dir=self.workspace_dir,
            backend=backend,
            shadow_mode=shadow_mode,
        )
        # Persist the IOC feed on shutdown? The dashboard defaults to
        # False so a manual edit to intel.txt isn't clobbered by an
        # empty in-memory set on exit. CLI paths keep the class default.
        self.shield.save_intel_on_exit = bool(save_intel_on_exit)
        self._lock = threading.Lock()

    # -------- Lifecycle --------
    def start(self):
        self.shield.start_monitoring()

    def shutdown(self):
        self.shield.stop_monitoring()
        self.shield.save_models()

    # -------- Event stream --------
    def register_event_callback(self, callback):
        def _bridge(event_dict, decision_dict):
            try:
                callback(event_dict, decision_dict)
            except Exception as e:
                print(f"[API] callback error: {e}")
        self.shield._event_callback = _bridge

    def unregister_event_callback(self):
        self.shield._event_callback = None
    
    def register_quarantine_callback(self, callback):
        """callback(payload_dict) -> None. phase in {'start','done'}."""
        def _bridge(payload):
            try:
                callback(payload)
            except Exception as e:
                print(f"[API] quarantine callback error: {e}")
        self.shield._quarantine_callback = _bridge

    def unregister_quarantine_callback(self):
        self.shield._quarantine_callback = None
    # -------- Read: status --------
    def get_status(self) -> Dict[str, Any]:
        base = self.shield.get_status()
        base['incidents_total'] = self._count_incidents()
        base['quarantine_total'] = self._count_quarantine()
        return base

    # -------- Read: incidents --------
    def list_incidents(self, limit: int = 100,
                       since: float = 0,
                       include_labeled: bool = True) -> List[Dict[str, Any]]:
        inc_dir = self.shield.incidents_dir
        if not os.path.isdir(inc_dir):
            return []
        files = sorted(glob.glob(os.path.join(inc_dir, "*.json")))
        results = []
        for fp in files[-limit:]:
            try:
                with open(fp) as f:
                    d = json.load(f)
                if not include_labeled and d.get('label') is not None:
                    continue
                ts = d.get('event', {}).get('timestamp', 0)
                if ts < since:
                    continue
                d['file'] = os.path.basename(fp)
                results.append(d)
            except Exception:
                continue
        results.sort(
            key=lambda x: x.get('event', {}).get('timestamp', 0),
            reverse=True)
        return results

    def get_incident(self, filename: str) -> Optional[Dict[str, Any]]:
        fp = os.path.join(self.shield.incidents_dir, filename)
        if not os.path.exists(fp):
            return None
        try:
            with open(fp) as f:
                d = json.load(f)
            d['file'] = os.path.basename(fp)
            return d
        except Exception:
            return None

    def _count_incidents(self) -> int:
        return len(glob.glob(os.path.join(self.shield.incidents_dir, "*.json")))
    
    def quarantine_file(self, file_path: str) -> bool:
        """Quarantine a single file. Path is validated against the quarantine dir."""
        with self._lock:
            return self.shield.quarantine_file(file_path)
            

    # -------- Read: quarantine --------
    def list_quarantine(self) -> List[Dict[str, Any]]:
        q_dir = self.shield.quarantine_dir
        if not os.path.isdir(q_dir):
            return []
        out = []
        for root, _, names in os.walk(q_dir):
            for n in names:
                full = os.path.join(root, n)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                out.append({
                    'quarantine_path': full,
                    'name': n,
                    'size': st.st_size,
                    'mtime': st.st_mtime,
                    'kind': 'rollback_pre' if n.endswith('.pre') else 'quarantine',
                })
        out.sort(key=lambda x: x['mtime'], reverse=True)
        return out

    def _count_quarantine(self) -> int:
        return len(self.list_quarantine())

    # -------- Read: blacklist / reports / sessions --------
    def list_blacklist(self):
        return self.shield.blacklist.summary()

    def list_whitelist(self) -> List[Dict[str, Any]]:
        """
        Return the whitelist as a list of {name, category, source}
        dicts. `source` is 'default' for built-ins and 'user' for
        entries added through the dashboard.
        """
        killer = self.shield.auto_response.killer
        defaults = killer.DEFAULT_PROTECTED_PROCESSES
        user = killer.whitelist.all_names()
        out = []
        for n in sorted(defaults | user):
            out.append({
                'name': n,
                'category': killer.whitelist.categorize(n),
                'source': 'user' if n in user else 'default',
            })
        return out

    def list_reports(self, limit: int = 20):
        rep_dir = os.path.join(self.workspace_dir, "reports")
        out = []
        for fp in sorted(glob.glob(os.path.join(rep_dir, "*.json")))[-limit:]:
            try:
                with open(fp) as f:
                    d = json.load(f)
                d['file'] = os.path.basename(fp)
                out.append(d)
            except Exception:
                continue
        return out

    def list_sessions(self):
        return self.shield.correlator.summary()

    # -------- Write: label incident --------
    def label_incident(self, filename: str, label: int) -> bool:
        if label not in (0, 1):
            return False
        fp = os.path.join(self.shield.incidents_dir, filename)
        if not os.path.exists(fp):
            return False
        with self._lock:
            try:
                with open(fp) as f:
                    d = json.load(f)
                d['label'] = label
                with open(fp, 'w') as f:
                    json.dump(d, f, indent=2)
                if 'features' in d:
                    feats = list(d['features'])
                    while len(feats) < FeatureVector.n_features():
                        feats.append(0.0)
                    fv = FeatureVector(*feats[:FeatureVector.n_features()])
                    self.shield.engine.record_feedback(fv, label)
                    self.shield.save_models()
                return True
            except Exception as e:
                print(f"[API] label_incident error: {e}")
                return False

    # -------- Safety helper --------
    def _safe_quarantine_path(self, candidate: str) -> Optional[str]:
        """
        Return the abspath iff it lives inside the quarantine dir.
        Rejects traversal, symlink escapes, and absolute paths elsewhere.
        """
        if not candidate:
            return None
        try:
            qdir = os.path.realpath(self.shield.quarantine_dir)
            real = os.path.realpath(candidate)
        except Exception:
            return None
        if real == qdir:
            return None
        if not real.startswith(qdir + os.sep):
            return None
        return real

    # -------- Quarantine ops (path-safe + locked) --------
    def restore_from_quarantine(self, quarantine_path: str) -> bool:
        with self._lock:
            safe = self._safe_quarantine_path(quarantine_path)
            if not safe or not os.path.exists(safe):
                return False
            original = self._find_original_path(safe)
            if not original:
                return False
            # Also guard the destination: refuse to overwrite if it's
            # outside a sane target — but original comes from recorded
            # incidents, so trust it after normalizing.
            try:
                original = os.path.abspath(os.path.expanduser(original))
                os.makedirs(os.path.dirname(original), exist_ok=True)
                # If a file already exists at destination, move it aside
                if os.path.exists(original):
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    aside = os.path.join(
                        self.shield.quarantine_dir,
                        f"restore_pre_{ts}_{os.path.basename(original)}.pre")
                    shutil.move(original, aside)
                shutil.move(safe, original)
                return True
            except Exception as e:
                print(f"[API] restore failed: {e}")
                return False

    def delete_quarantined(self, quarantine_path: str) -> bool:
        with self._lock:
            safe = self._safe_quarantine_path(quarantine_path)
            if not safe:
                return False
            try:
                if os.path.exists(safe):
                    os.remove(safe)
                    return True
            except Exception:
                pass
            return False

    def _find_original_path(self, quarantine_path: str) -> Optional[str]:
        base = os.path.basename(quarantine_path)
        for suffix in ('.locked', '.pre'):
            if base.endswith(suffix):
                base = base[:-len(suffix)]
        m = re.match(r'^(?:rollback_)?\d{8}_\d{6}(?:_\d+)?_(.+)$', base)
        if m:
            base = m.group(1)
        # Look in incidents for matching basename
        for inc in self.list_incidents(limit=1000):
            ev = inc.get('event', {})
            if os.path.basename(ev.get('path', '')) == base:
                return ev.get('path')
        return None


    # -------- Write: blacklist --------
    def blacklist_add(self, process_name: str, reason: str = "manual") -> bool:
        with self._lock:
            try:
                self.shield.blacklist.add(process_name, reason=reason)
                return True
            except Exception:
                return False

    def blacklist_remove(self, process_name: str) -> bool:
        with self._lock:
            try:
                self.shield.blacklist.remove(process_name)
                return True
            except Exception:
                return False

    def set_auto_response(self, **kwargs):
        with self._lock:
            pol = self.shield.auto_response_policy
            for k, v in kwargs.items():
                if hasattr(pol, k):
                    setattr(pol, k, v)

    def set_auto_quarantine(self, on: bool):
        with self._lock:
            pol = self.shield.auto_response_policy
            pol.enabled = bool(on)
            pol.quarantine_current = bool(on)
            pol.kill_process = bool(on)
            pol.rollback_files = bool(on)
            pol.blacklist_process = bool(on)

    def get_auto_response(self) -> Dict[str, Any]:
        pol = self.shield.auto_response_policy
        return {
            'enabled': pol.enabled,
            'kill_process': pol.kill_process,
            'rollback_files': pol.rollback_files,
            'quarantine_current': pol.quarantine_current,
            'blacklist_process': pol.blacklist_process,
            'dry_run': pol.dry_run,
            'min_level': pol.min_level.name,
        }
# ============================================================
# STATIC ASSET BOOTSTRAP — fetch JS libs on first run
# ============================================================
def ensure_static_assets(static_dir: str) -> bool:
    """
    Download the JS bundles the dashboard needs if they're missing.
    Returns True if all assets are present after the call.
    """
    os.makedirs(static_dir, exist_ok=True)

    assets = {
        "socket.io.min.js":
            "https://cdn.socket.io/4.7.5/socket.io.min.js",
        "chart.min.js":
            "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
    }

    try:
        import requests
    except ImportError:
        print(f"{Colors.YELLOW}[!] 'requests' not installed — cannot "
              f"download dashboard JS assets.{Colors.END}")
        print(f"    Install: pip install requests")
        return False

    ok = True
    for name, url in assets.items():
        target = os.path.join(static_dir, name)
        if os.path.exists(target) and os.path.getsize(target) > 1000:
            continue
        try:
            print(f"[dashboard] downloading {name} ...")
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            with open(target, 'wb') as f:
                f.write(r.content)
            size_kb = os.path.getsize(target) / 1024
            print(f"[dashboard] saved {name} ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Failed to download {name}: {e}"
                  f"{Colors.END}")
            ok = False

    return ok
# ============================================================
# DASHBOARD UI — thin Flask wrapper over ShieldEngineAPI
# ============================================================
class DashboardUI:
    """
    Pure frontend over ShieldEngineAPI.
    Never scans. Never detects. Never quarantines directly.
    Every value it shows comes from the engine.
    """

    def __init__(self, api: ShieldEngineAPI,
                 host: str = "127.0.0.1",
                 port: int = 5000,
                 open_browser: bool = True):
        if not FLASK_OK:
            raise RuntimeError(
                "Flask required for UI mode.\n"
                "  pip install flask flask-socketio")

        self.api = api
        self.host = host
        self.port = port
        self.open_browser = open_browser
        
        _ALLOWED_ORIGINS = os.environ.get("DSTERM_CORS", "*")

        static_dir = os.path.join(api.workspace_dir, "static")
        os.makedirs(static_dir, exist_ok=True)
        ensure_static_assets(static_dir)

        self.app = Flask(__name__,
                         static_folder=static_dir,
                         static_url_path="/static")

        # Random per-process secret unless the operator pinned one.
        secret = os.environ.get("DSTERMINAL_SECRET")
        if not secret:
            secret = hashlib.sha256(
                f"{os.getpid()}:{time.time()}:{id(self)}".encode()
            ).hexdigest()
        self.app.config["SECRET_KEY"] = secret

        # CORS: only same-origin by default. If you explicitly bind to
        # something other than loopback, you must opt in via env.
        allowed = [f"http://{host}:{port}", f"http://127.0.0.1:{port}",
                   f"http://localhost:{port}"]
        env_origins = os.environ.get("DSTERMINAL_CORS_ORIGINS")
        if env_origins:
            allowed.extend(o.strip() for o in env_origins.split(",") if o.strip())

        def _detect_async_mode() -> str:
            """
            Return the best available async_mode for Flask-SocketIO.
            Priority: eventlet -> gevent -> threading.
            """
            # 1) eventlet (requires greenlet on newer versions)
            try:
                import eventlet  # noqa: F401
                import greenlet  # noqa: F401
                print("[dashboard] SocketIO async_mode = eventlet")
                return "eventlet"
            except ImportError:
                pass
            except Exception as e:
                print(f"[dashboard] eventlet check failed: {e}")

            # 2) gevent
            try:
                from gevent import monkey  # noqa: F401
                import gevent  # noqa: F401
                print("[dashboard] SocketIO async_mode = gevent")
                return "gevent"
            except ImportError:
                pass
            except Exception as e:
                print(f"[dashboard] gevent check failed: {e}")

            # 3) threading (always available)
            print("[dashboard] SocketIO async_mode = threading")
            return "threading"

        

        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins=_ALLOWED_ORIGINS,
            async_mode=_detect_async_mode(),
        )

        # Shutdown flag used by long-lived background loops so they can
        # exit cleanly when the server stops (see stop()).
        self._running = True

        api.register_event_callback(self._on_engine_event)
        api.register_quarantine_callback(self._on_quarantine)
        self._register_routes()
        self._register_sockets()
    def stop(self):
        """Signal background loops to exit and detach from the engine."""
        self._running = False
        try:
            self.api.unregister_event_callback()
        except Exception:
            pass
        try:
            self.api.unregister_quarantine_callback()
        except Exception:
            pass
    # -------- Engine → WebSocket bridge --------
    def _on_engine_event(self, event_dict, decision_dict):
        try:
            # Coerce numpy scalars and arrays to native Python types so
            # Flask's JSON encoder can serialize them.
            event_dict = _json_safe(event_dict)
            decision_dict = _json_safe(decision_dict)
            self.socketio.emit("engine_event", {
                "event": event_dict,
                "decision": decision_dict,
            })
        except Exception as e:
            print(f"[dashboard] socketio.emit(engine_event) failed: {e}")

    def _on_quarantine(self, payload):
        try:
            self.socketio.emit("quarantine_progress", _json_safe(payload))
        except Exception as e:
            print(f"[dashboard] socketio.emit(quarantine_progress) failed: {e}")

    # -------- Routes (all thin adapters) --------
    def _register_routes(self):
        api = self.api
        app = self.app

        @app.route("/")
        def index():
            return render_template_string(DASHBOARD_HTML)

        @app.route("/api/status")
        def status():
            engine = api.get_status()
            incidents = api.list_incidents(limit=5000)
            quarantine = api.list_quarantine()
            blacklist = api.list_blacklist()
            sessions = api.list_sessions()
            whitelist = api.list_whitelist()

            # Risk score reflects the last 24 hours only — otherwise
            # the score pins at 100 forever and never decays.
            now = time.time()
            cutoff = now - 86400          # 24 hours
            recent = [i for i in incidents
                      if i.get("event", {}).get("timestamp", 0) >= cutoff]

            pending = [i for i in recent if i.get("label") is None]
            rans = [i for i in recent
                    if i.get("decision", {}).get("level") == "RANSOMWARE_DETECTED"]
            high = [i for i in recent
                    if i.get("decision", {}).get("level") == "HIGH_RISK"]

            risk = min(100,
                len(rans) * 20 +
                len(high) * 10 +
                (30 if engine.get("threat_level") == "RANSOMWARE_DETECTED" else 0) +
                (15 if engine.get("threat_level") == "HIGH_RISK" else 0))

            return jsonify({
                'threat_level': engine.get('threat_level', 'CLEAN'),
                'risk_score': risk,
                'events_monitored': engine.get('events_monitored', 0),
                'honeypots': engine.get('honeypots', 0),
                'ml_updates': engine.get('ml_updates', 0),
                'ml_trusted': engine.get('ml_trusted', False),
                'if_samples': engine.get('if_samples', 0),
                'if_trusted': engine.get('if_trusted', False),
                'sessions_tracked': engine.get('sessions_tracked', 0),
                'blacklist_size': engine.get('blacklist_size', 0),
                'siem_enabled': engine.get('siem_enabled', False),
                'shadow_mode': engine.get('shadow_mode', False),
                'workspace_dir': engine.get('workspace_dir'),
                'incidents_total': engine.get('incidents_total', 0),
                'incidents_pending': len(pending),
                'incidents_ransomware': len(rans),
                'incidents_high_risk': len(high),
                'quarantine_total': engine.get('quarantine_total', 0),
                'incidents': incidents[:30],
                'quarantine': quarantine[:30],
                'blacklist': blacklist[:30],
                'sessions': sessions[:10],
                'auto_response': api.get_auto_response(),
                'system': self._system_metrics(),
                'recommendations': self._recommendations(engine),
                'whitelist_total': len(whitelist),
                'whitelist': whitelist,
            })

        @app.route("/api/incidents")
        def list_incidents():
            limit = int(request.args.get("limit", 100))
            return jsonify(api.list_incidents(limit=limit))

        @app.route("/api/incidents/<path:filename>")
        def get_incident(filename):
            inc = api.get_incident(filename)
            if not inc:
                return jsonify({"error": "not found"}), 404
            return jsonify(inc)

        @app.route("/api/incidents/<path:filename>/label", methods=["POST"])
        def label_incident(filename):
            data = request.json or {}
            label = data.get("label")
            if label not in (0, 1):
                return jsonify({"success": False,
                                "error": "label must be 0 or 1"}), 400
            return jsonify({"success": api.label_incident(filename, label)})

        @app.route("/api/quarantine", methods=["POST"])
        def quarantine():
            data = request.json or {}
            fp = data.get("file_path")
            if not fp:
                return jsonify({"success": False,
                                "error": "file_path required"}), 400
            return jsonify({"success": api.quarantine_file(fp)})

        @app.route("/api/quarantine/list")
        def quarantine_list():
            return jsonify(api.list_quarantine())

        @app.route("/api/quarantine/restore", methods=["POST"])
        def quarantine_restore():
            qp = (request.json or {}).get("quarantine_path")
            if not qp:
                return jsonify({"success": False,
                                "error": "quarantine_path required"}), 400
            return jsonify({"success": api.restore_from_quarantine(qp)})

        @app.route("/api/quarantine/delete", methods=["POST"])
        def quarantine_delete():
            qp = (request.json or {}).get("quarantine_path")
            if not qp:
                return jsonify({"success": False,
                                "error": "quarantine_path required"}), 400
            return jsonify({"success": api.delete_quarantined(qp)})

        @app.route("/api/blacklist")
        def blacklist():
            return jsonify(api.list_blacklist())

        @app.route("/api/blacklist/add", methods=["POST"])
        def blacklist_add():
            name = (request.json or {}).get("process_name")
            if not name:
                return jsonify({"success": False,
                                "error": "process_name required"}), 400
            return jsonify({"success": api.blacklist_add(name)})

        @app.route("/api/blacklist/remove", methods=["POST"])
        def blacklist_remove():
            name = (request.json or {}).get("process_name")
            if not name:
                return jsonify({"success": False,
                                "error": "process_name required"}), 400
            return jsonify({"success": api.blacklist_remove(name)})

        @app.route("/api/whitelist")
        def whitelist():
            return jsonify(api.list_whitelist())

        @app.route("/api/whitelist/add", methods=["POST"])
        def whitelist_add():
            payload = request.json or {}
            name = (payload.get("process_name") or "").strip()
            if not name:
                return jsonify({"success": False,
                                "error": "process_name required"}), 400
            killer = api.shield.auto_response.killer
            added = killer.whitelist.add(name)
            return jsonify({
                "success": added,
                "message": "added" if added else "already present",
                "name": name.lower(),
            })

        @app.route("/api/whitelist/remove", methods=["POST"])
        def whitelist_remove():
            payload = request.json or {}
            name = (payload.get("process_name") or "").strip().lower()
            if not name:
                return jsonify({"success": False,
                                "error": "process_name required"}), 400
            killer = api.shield.auto_response.killer
            # Refuse to remove built-in defaults — they're safety rails.
            if name in killer.DEFAULT_PROTECTED_PROCESSES:
                return jsonify({
                    "success": False,
                    "error": "cannot remove built-in default",
                }), 403
            removed = killer.whitelist.remove(name)
            return jsonify({
                "success": removed,
                "message": "removed" if removed else "not found",
                "name": name,
            })

        @app.route("/api/auto-response", methods=["GET", "POST"])
        def auto_response():
            if request.method == "GET":
                return jsonify(api.get_auto_response())
            payload = request.json or {}
            if "enabled" in payload:
                api.set_auto_quarantine(bool(payload["enabled"]))
            else:
                api.set_auto_response(**payload)
            return jsonify(api.get_auto_response())

        @app.route("/api/reports")
        def reports():
            return jsonify(api.list_reports(limit=20))

        @app.route("/api/reports/list")
        def reports_list():
            """
            List report bundles under <workspace>/ransom/reports/.
            Each directory is one detection with HTML/JSON/PDF inside.
            """
            root = os.path.join(api.workspace_dir, "ransom", "reports")
            if not os.path.isdir(root):
                return jsonify([])
            out = []
            for name in sorted(os.listdir(root), reverse=True):
                full = os.path.join(root, name)
                if not os.path.isdir(full):
                    continue
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                files = {}
                for fn in ("report.html", "report.json", "report.pdf"):
                    fp = os.path.join(full, fn)
                    files[fn] = os.path.exists(fp)
                # Try to read a summary from the JSON
                summary = {}
                jp = os.path.join(full, "report.json")
                if os.path.exists(jp):
                    try:
                        with open(jp, encoding='utf-8') as f:
                            j = json.load(f)
                        summary = {
                            'level': j.get('decision', {}).get('level'),
                            'fused': j.get('decision', {}).get('fused_score'),
                            'path': j.get('event', {}).get('path'),
                            'process': j.get('event', {}).get('process_name'),
                            'timestamp': j.get('event', {}).get('timestamp'),
                        }
                    except Exception:
                        pass
                out.append({
                    'name': name,
                    'mtime': st.st_mtime,
                    'files': files,
                    'summary': summary,
                })
            return jsonify(out)

        @app.route("/api/reports/download/<path:report_name>/<path:filename>")
        def reports_download(report_name, filename):
            """
            Serve a single file from a report bundle. Restricts access
            to the reports directory to prevent path traversal.
            """
            root = os.path.realpath(
                os.path.join(api.workspace_dir, "ransom", "reports"))
            full = os.path.realpath(
                os.path.join(root, report_name, filename))
            if not full.startswith(root + os.sep):
                return jsonify({"error": "invalid path"}), 400
            if not os.path.isfile(full):
                return jsonify({"error": "not found"}), 404
            return send_file(
                full,
                as_attachment=True,
                download_name=filename,
                mimetype=(
                    'text/html' if filename.endswith('.html') else
                    'application/json' if filename.endswith('.json') else
                    'application/pdf' if filename.endswith('.pdf') else
                    'application/octet-stream'
                ),
            )

    # -------- SocketIO --------
    def _register_sockets(self):
        socketio = self.socketio
        app = self.app

        @socketio.on("connect")
        def on_connect():
            print(f"[dashboard] client connected: {request.sid}")
            emit("connected", {"status": "connected"})

        @socketio.on("subscribe_updates")
        def on_subscribe():
            sid = request.sid

            def loop():
                while self._running:
                    try:
                        with app.app_context():
                            socketio.emit("status_update",
                                          self.api.get_status(),
                                          room=sid)
                        time.sleep(5)
                    except (KeyboardInterrupt, SystemExit):
                        return
                    except Exception:
                        time.sleep(10)

            threading.Thread(target=loop, daemon=True).start()
    # -------- Helpers --------
    @staticmethod
    def _system_metrics():
        if not PSUTIL_OK:
            return {"cpu": 0, "memory": 0, "disk": 0, "processes": 0}
        try:
            return {
                "cpu": psutil.cpu_percent(interval=0.2),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage(os.path.abspath(os.sep)).percent,
                "processes": len(psutil.pids()),
            }
        except Exception:
            return {"cpu": 0, "memory": 0, "disk": 0, "processes": 0}

    @staticmethod
    def _recommendations(engine):
        recs = []
        tl = engine.get("threat_level")
        if tl == "RANSOMWARE_DETECTED":
            recs.append("[!] Active ransomware — review incidents")
            recs.append("[i] Blacklist the offending process")
        elif tl == "HIGH_RISK":
            recs.append("[!] Elevated risk — inspect recent incidents")
        if not engine.get("ml_trusted"):
            recs.append(
                f"[i] ML undertrained ({engine.get('ml_updates', 0)}/50) "
                f"— label incidents to improve")
        if not engine.get("if_trusted"):
            recs.append("[i] Anomaly detector needs more training")
        if engine.get("blacklist_size", 0) > 5:
            recs.append("[i] Large blacklist — verify no false positives")
        if not recs:
            recs.append("[OK] No action required")
        return recs

    # -------- Run --------
    def run(self):
        if self.open_browser:
            threading.Thread(target=self._open_browser, daemon=True).start()

        import logging
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        logging.getLogger("socketio").setLevel(logging.ERROR)
        logging.getLogger("engineio").setLevel(logging.ERROR)

        print(f"\n{'═' * 64}")
        print(f"  DSTERMINAL v6.0 — DASHBOARD")
        print(f"  http://{self.host}:{self.port}")
        print(f"  Workspace: {self.api.workspace_dir}")
        print(f"  Shadow: {self.api.shield.shadow_mode}")
        print(f"  Reports: HTML+JSON "
              f"{'+ PDF' if REPORTLAB_OK else '(no PDF — pip install reportlab)'}")
        print(f"  Ctrl+C to stop")
        print(f"{'═' * 64}\n")


        self.socketio.run(self.app,
                              host=self.host, port=self.port,
                              debug=False,
                              allow_unsafe_werkzeug=True)


    def _open_browser(self):
        import webbrowser
        time.sleep(1.5)
        try:
            webbrowser.open(f"http://{self.host}:{self.port}")
        except Exception:
            pass

# ============================================================
# DASHBOARD HTML TEMPLATE
# ============================================================
DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <title>DSTERMINAL VISIBILITY THREAT DASHBOARD</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body {
            width: 100%; height: 100%; overflow-x: hidden;
            background: #0a0e17; color: #00ff88;
            font-family: 'Segoe UI', monospace;
        }
        body { padding: 15px; min-height: 100vh; display: flex; flex-direction: column; }

        /* ============================================================
           Header
           ============================================================ */
        .header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 15px 25px; border-bottom: 2px solid rgba(0,255,136,0.15);
            margin-bottom: 20px; background: rgba(0,0,0,0.4);
            border-radius: 10px; position: relative; overflow: hidden;
            flex-shrink: 0; flex-wrap: wrap; gap: 10px;
        }
        .header::before {
            content: ''; position: absolute; top: -2px; left: -100%;
            width: 300%; height: 4px;
            background: linear-gradient(90deg, transparent, #00ff88, #00ccff, #ff00ff, #00ff88, transparent);
            animation: glow-scan 3s linear infinite; filter: blur(2px); z-index: 2;
        }
        @keyframes glow-scan {
            0%   { transform: translateX(-33%); opacity: 0.3; }
            50%  { opacity: 1; }
            100% { transform: translateX(33%); opacity: 0.3; }
        }
        .dst-logo-container { display: flex; align-items: center; gap: 12px; position: relative; z-index: 3; }
        .dst-logo-img {
            width: 48px; height: 48px; object-fit: contain;
            filter: drop-shadow(0 0 20px rgba(0,255,136,0.3));
            animation: logo-glow 2s ease-in-out infinite;
            border-radius: 8px; background: rgba(0,0,0,0.2); padding: 2px;
        }
        @keyframes logo-glow {
            0%, 100% { filter: drop-shadow(0 0 20px rgba(0,255,136,0.3)); }
            50%      { filter: drop-shadow(0 0 40px rgba(0,255,136,0.6)) drop-shadow(0 0 80px rgba(0,255,136,0.2)); }
        }
        .dst-logo-text {
            font-family: 'Courier New', monospace; font-weight: bold; font-size: 24px;
            letter-spacing: 3px;
            background: linear-gradient(135deg, #00ff88, #00ccff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: neon-pulse 2s ease-in-out infinite;
        }
        .dst-logo-text .highlight { -webkit-text-fill-color: #ff00ff; }
        @keyframes neon-pulse {
            0%, 100% { filter: drop-shadow(0 0 10px rgba(0,255,136,0.3)); }
            50%      { filter: drop-shadow(0 0 30px rgba(0,255,136,0.5)) drop-shadow(0 0 60px rgba(0,255,136,0.2)); }
        }
        .dst-logo-badge {
            font-size: 10px; color: #2a5a4a;
            border: 1px solid rgba(0,255,136,0.15);
            padding: 2px 8px; border-radius: 10px;
            letter-spacing: 1px; -webkit-text-fill-color: #2a5a4a;
        }

        .header .status-right {
            display: flex; align-items: center; gap: 15px; font-size: 13px;
            position: relative; z-index: 3; flex-wrap: wrap;
        }
        .header-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .control-btn {
            background: rgba(0,255,136,0.05); border: 1px solid rgba(0,255,136,0.2);
            color: #00ff88; padding: 4px 12px; border-radius: 4px;
            cursor: pointer; font-size: 10px; font-family: monospace;
            transition: all 0.3s;
        }
        .control-btn:hover { background: rgba(0,255,136,0.15); border-color: #00ff88; }
        .control-btn.danger  { border-color: #ff0033; color: #ff0033; }
        .control-btn.danger:hover  { background: rgba(255,0,51,0.15); }
        .control-btn.success { border-color: #00ff88; color: #00ff88; }

        .glow-dot {
            display: inline-block; width: 12px; height: 12px; border-radius: 50%;
            margin-right: 6px; animation: dot-pulse 1.5s ease-in-out infinite;
            position: relative;
        }
        .glow-dot::after {
            content: ''; position: absolute; top: -4px; left: -4px; right: -4px; bottom: -4px;
            border-radius: 50%; animation: dot-ring 2s ease-in-out infinite;
            border: 2px solid rgba(0, 255, 136, 0.2);
        }
        .glow-dot.green  { background: #00ff88; box-shadow: 0 0 30px rgba(0, 255, 136, 0.6); }
        .glow-dot.red    { background: #ff0033; box-shadow: 0 0 30px rgba(255, 0, 51, 0.6); animation-duration: 0.5s; }
        .glow-dot.yellow { background: #ffcc00; box-shadow: 0 0 30px rgba(255, 204, 0, 0.6); }
        @keyframes dot-pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50%      { transform: scale(1.3); opacity: 0.7; }
        }
        @keyframes dot-ring {
            0%, 100% { transform: scale(1); opacity: 0.3; }
            50%      { transform: scale(1.5); opacity: 0; }
        }
        #statusText {
            font-family: 'Courier New', monospace; font-weight: bold;
            letter-spacing: 2px; text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
            animation: status-glow 2s ease-in-out infinite; position: relative;
        }
        @keyframes status-glow {
            0%, 100% { opacity: 1; }
            50%      { opacity: 0.8; text-shadow: 0 0 30px rgba(0, 255, 136, 0.5); }
        }
        .status-protected { color: #00ff88; text-shadow: 0 0 30px rgba(0, 255, 136, 0.4); }
        .status-attack    { color: #ff0033; text-shadow: 0 0 30px rgba(255, 0, 51, 0.4); animation: attack-pulse 0.5s ease-in-out infinite; }
        @keyframes attack-pulse {
            0%, 100% { opacity: 1; }
            50%      { opacity: 0.5; text-shadow: 0 0 60px rgba(255, 0, 51, 0.8); }
        }

        /* ============================================================
           Auto-Q toggle button
           ============================================================ */
        .toggle-btn {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 5px 12px; border-radius: 14px;
            border: 1px solid rgba(0,255,136,0.35);
            background: rgba(0,255,136,0.08);
            color: #00ff88;
            font-family: 'Courier New', monospace;
            font-size: 10px; letter-spacing: 1px;
            cursor: pointer; transition: all 0.25s;
        }
        .toggle-btn:hover { background: rgba(0,255,136,0.18); }
        .toggle-btn.off {
            border-color: rgba(120,120,120,0.35);
            background: rgba(120,120,120,0.08);
            color: #7a8a7a;
        }
        .toggle-dot {
            display: inline-block; width: 10px; height: 10px; border-radius: 50%;
            background: #00ff88; box-shadow: 0 0 10px rgba(0,255,136,0.9);
            transition: all 0.25s;
        }
        .toggle-btn.off .toggle-dot { background: #556; box-shadow: none; }

        /* ============================================================
           Danger alert banner (blinking, fixed to top)
           ============================================================ */
        .danger-alert {
            display: none;
            position: fixed; top: 0; left: 0; right: 0;
            z-index: 9998;
            padding: 14px 20px;
            background: rgba(255, 0, 51, 0.15);
            border-bottom: 2px solid #ff0033;
            color: #ff0033;
            font-weight: bold; font-size: 15px; letter-spacing: 1px;
            text-align: center;
            animation: alert-flash 0.8s ease-in-out infinite;
            backdrop-filter: blur(3px);
        }
        .danger-alert.show { display: block; }
        .danger-alert .alert-icon {
            display: inline-block; margin-right: 10px;
            animation: alert-shake 0.6s ease-in-out infinite;
        }
        @keyframes alert-flash {
            0%, 100% { background: rgba(255,0,51,0.15); box-shadow: 0 0 20px rgba(255,0,51,0.2); }
            50%      { background: rgba(255,0,51,0.35); box-shadow: 0 0 60px rgba(255,0,51,0.6); }
        }
        @keyframes alert-shake {
            0%,100% { transform: translateX(0); }
            25%     { transform: translateX(-4px); }
            75%     { transform: translateX(4px); }
        }

        /* ============================================================
           Quarantine progress overlay (centered, modal)
           ============================================================ */
        .quarantine-overlay {
            display: none;
            position: fixed; inset: 0; z-index: 10001;   /* was 9999 */
            background: rgba(2, 6, 12, 0.82);
            backdrop-filter: blur(6px);
            align-items: center; justify-content: center;
            flex-direction: column; gap: 22px; text-align: center;
        }
        .quarantine-overlay.show { display: flex; }

        .quarantine-panel {
            width: min(620px, 88vw);
            padding: 30px 34px;
            border: 2px solid #ff0033;
            border-radius: 14px;
            background: linear-gradient(180deg, rgba(40,0,10,0.9), rgba(10,0,5,0.95));
            box-shadow: 0 0 80px rgba(255,0,51,0.35);
            animation: q-panel-in 0.35s ease-out;
        }
        @keyframes q-panel-in {
            from { transform: scale(0.92); opacity: 0; }
            to   { transform: scale(1);    opacity: 1; }
        }
        .quarantine-panel h2 {
            color: #ff0033; font-size: 20px; letter-spacing: 3px;
            margin-bottom: 6px;
            text-shadow: 0 0 20px rgba(255,0,51,0.6);
        }
        .quarantine-panel .q-sub {
            color: #ff8a9e; font-size: 11px; margin-bottom: 20px;
            font-family: 'Courier New', monospace; word-break: break-all;
        }
        .q-bar-track {
            width: 100%; height: 22px; border-radius: 12px;
            background: rgba(255,0,51,0.08);
            border: 1px solid rgba(255,0,51,0.35);
            overflow: hidden; position: relative;
        }
        .q-bar-fill {
            height: 100%; width: 0%;
            background: linear-gradient(90deg, #ff0033, #ff4d66, #ff0033);
            background-size: 200% 100%;
            border-radius: 12px;
            transition: width 0.25s linear;
            animation: q-stripes 1.2s linear infinite;
            box-shadow: 0 0 20px rgba(255,0,51,0.7);
        }
        @keyframes q-stripes {
            0%   { background-position: 0% 0; }
            100% { background-position: -200% 0; }
        }
        .q-bar-label {
            display: flex; justify-content: space-between;
            margin-top: 8px; font-size: 11px; color: #ff8a9e;
            font-family: 'Courier New', monospace;
        }
        .q-percent {
            color: #fff; font-weight: bold; font-size: 32px;
            margin-top: 14px;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 20px rgba(255,0,51,0.7);
        }
        .q-status-text {
            color: #ff8a9e; font-size: 11px; margin-top: 4px;
            font-family: 'Courier New', monospace; letter-spacing: 1px;
        }
        .q-status-text.done { color: #00ff88; }

        /* ============================================================
           Grid / cards
           ============================================================ */
        .dashboard-content { flex: 1; display: flex; flex-direction: column; gap: 15px; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 15px; }
        .card {
            background: rgba(0,255,136,0.03); border: 1px solid rgba(0,255,136,0.12);
            border-radius: 8px; padding: 15px 18px;
        }
        .card-title {
            font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
            color: #2a5a4a; margin-bottom: 8px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .value { font-size: 28px; font-weight: bold; color: #fff; }
        .value.danger  { color: #ff0033; }
        .value.warning { color: #ffcc00; }
        .value.success { color: #00ff88; }
        .sub { font-size: 11px; color: #2a5a4a; margin-top: 4px; }
        .col-span-3  { grid-column: span 3; }
        .col-span-4  { grid-column: span 4; }
        .col-span-6  { grid-column: span 6; }
        .col-span-8  { grid-column: span 8; }
        .col-span-12 { grid-column: span 12; }

        .threat-badge { padding: 4px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; }
        .badge-clean       { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff88; }
        .badge-suspicious  { background: rgba(255,204,0,0.15); color: #ffcc00; border: 1px solid #ffcc00; }
        .badge-high        { background: rgba(255,102,0,0.15); color: #ff6600; border: 1px solid #ff6600; }
        .badge-ransomware  { background: rgba(255,0,51,0.2); color: #ff0033; border: 1px solid #ff0033; animation: pulse 1s infinite; }
        .badge-anomaly     { background: rgba(188,140,255,0.2); color: #bc8cff; border: 1px solid #bc8cff; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

        .chart-container { height: 180px; margin-top: 6px; position: relative; min-height: 100px; }

        .event-log {
            max-height: 300px; overflow-y: auto; font-size: 12px;
            background: rgba(0,0,0,0.3); border-radius: 4px; padding: 8px;
        }
        .event-log .no-events { color: #2a5a4a; text-align: center; padding: 20px 0; font-size: 11px; }
        .event-item {
            padding: 4px 8px; border-bottom: 1px solid rgba(0,255,136,0.04);
            display: flex; justify-content: space-between; align-items: center;
            font-size: 11px; animation: slideIn 0.3s ease;
            font-family: 'Courier New', monospace;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to   { opacity: 1; transform: translateX(0); }
        }
        .event-item .time { color: #2a5a4a; min-width: 70px; font-size: 10px; }
        .event-item .proc { color: #00ccff; min-width: 100px; }
        .event-item .file {
            color: #fff; max-width: 200px; overflow: hidden;
            text-overflow: ellipsis; white-space: nowrap; flex: 1;
        }
        .event-item .operation {
            padding: 2px 10px; border-radius: 3px; font-size: 9px;
            font-weight: bold; text-transform: uppercase;
            min-width: 50px; text-align: center;
        }
        .op-CLEAN               { background: rgba(0,255,136,0.15);  color: #00ff88; }
        .op-SUSPICIOUS          { background: rgba(255,204,0,0.15);  color: #ffcc00; }
        .op-HIGH_RISK           { background: rgba(255,102,0,0.2);   color: #ff6600; }
        .op-RANSOMWARE_DETECTED { background: rgba(255,0,51,0.2);    color: #ff0033; }
        .op-ANOMALY             { background: rgba(188,140,255,0.2); color: #bc8cff; }

        .list-item {
            padding: 6px 0; border-bottom: 1px solid rgba(0,255,136,0.05);
            font-size: 11px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .list-item .action-btn {
            padding: 2px 8px; border-radius: 3px; cursor: pointer;
            font-size: 9px; font-family: monospace; margin-left: 4px;
        }
        .action-btn.danger  { background: rgba(255,0,51,0.1);  border: 1px solid #ff0033; color: #ff0033; }
        .action-btn.success { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; color: #00ff88; }
        .action-btn:hover { opacity: 0.8; }

        .text-center { text-align: center; }
        .text-muted  { color: #2a5a4a; font-size: 10px; margin-top: 5px; }
        .mt-10 { margin-top: 10px; }

        .recommendation-box {
            background: rgba(0,255,136,0.05); border-left: 4px solid #00ff88;
            padding: 6px 10px; margin: 3px 0; border-radius: 4px;
            font-size: 10px; color: #aaa;
        }
        #recommendationList.panel-hidden { display: none; }

        .footer-text {
            text-align: center; margin-top: 15px; color: #2a5a4a;
            font-size: 9px;
            border-top: 1px solid rgba(0,255,136,0.05);
            padding-top: 10px; flex-shrink: 0;
        }

        .modal {
            display: none; position: fixed; top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); z-index: 10000;
            justify-content: center; align-items: center;
        }
        .modal.show { display: flex; }
        .modal-content {
            background: #0a0e17; border: 1px solid #00ff88;
            border-radius: 12px; padding: 30px; max-width: 800px;
            width: 90%; max-height: 80vh; overflow-y: auto;
        }
        .modal-content h2 { color: #00ff88; margin-bottom: 15px; }
        .modal-content .close {
            float: right; cursor: pointer; color: #ff0033; font-size: 24px;
        }

        .incident-row {
            padding: 8px 10px; border-bottom: 1px solid rgba(0,255,136,0.05);
            display: flex; justify-content: space-between; align-items: center;
            font-size: 12px; font-family: 'Courier New', monospace;
        }
        .incident-row:hover { background: rgba(0,255,136,0.03); }
        .incident-row .label-btn {
            padding: 2px 8px; margin-left: 4px; border-radius: 3px;
            cursor: pointer; font-size: 10px;
        }
        .label-btn.mal { background: rgba(255,0,51,0.1);  border: 1px solid #ff0033; color: #ff0033; }
        .label-btn.ben { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; color: #00ff88; }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
        ::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 2px; }

                .control-btn.warning { border-color: #ffcc00; color: #ffcc00; }
        .control-btn.warning:hover { background: rgba(255,204,0,0.15); }

        .category-badge {
            display: inline-block;
            font-size: 8px;
            padding: 1px 6px;
            border-radius: 3px;
            margin-left: 6px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .cat-windows-core     { background: rgba(0,204,255,0.15); color: #00ccff; }
        .cat-windows-shell    { background: rgba(255,204,0,0.15); color: #ffcc00; }
        .cat-security-stack   { background: rgba(0,255,136,0.15); color: #00ff88; }
        .cat-networking       { background: rgba(140,140,255,0.15); color: #8c8cff; }
        .cat-windows-services { background: rgba(200,200,200,0.15); color: #c8c8c8; }
        .cat-third-party-av   { background: rgba(255,102,0,0.15); color: #ff6600; }
        .cat-other            { background: rgba(120,120,120,0.15); color: #888; }
        .cat-user-added { background: rgba(255,204,0,0.15); color: #ffcc00; }
    </style>
</head>
<body>

<!-- Blinking danger alert banner (top of viewport) -->
<div class="danger-alert" id="dangerAlert">
    <span class="alert-icon">[!]</span>
    <span id="dangerAlertText">THREAT DETECTED</span>
</div>

<!-- Centered quarantine progress overlay -->
<div class="quarantine-overlay" id="quarantineOverlay">
    <div class="quarantine-panel">
        <h2 id="qPanelTitle">QUARANTINE IN PROGRESS</h2>
        <div class="q-sub" id="qPanelTarget">—</div>
        <div class="q-bar-track">
            <div class="q-bar-fill" id="qBarFill"></div>
        </div>
        <div class="q-bar-label">
            <span id="qBarStage">Analyzing…</span>
            <span id="qBarElapsed">0s / 20s</span>
        </div>
        <div class="q-percent" id="qPercent">0%</div>
        <div class="q-status-text" id="qStatusText">Securing the file…</div>
    </div>
</div>

<header class="header">
    <div class="dst-logo-container">
        <img src="/static/3486-removebg-preview.ico" alt="DSTerminal Logo"
             class="dst-logo-img"
             onerror="this.style.display='none'; document.getElementById('logoFallback').style.display='flex';">
        <div id="logoFallback" style="display:none; align-items:center; justify-content:center; width:48px; height:48px;">
            <svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="4" width="40" height="40" rx="8" stroke="#00ff88" stroke-width="2" fill="none"/>
                <text x="24" y="28" font-family="Courier New, monospace" font-size="20" font-weight="bold" fill="#00ff88" text-anchor="middle">D</text>
                <text x="24" y="40" font-family="Courier New, monospace" font-size="8" fill="#00ff88" text-anchor="middle">TERMINAL</text>
            </svg>
        </div>
        <div>
            <div class="dst-logo-text">DSTERMINAL <span class="highlight">●</span></div>
            <div class="dst-logo-badge">SHIELD_CORE v6.0</div>
        </div>
    </div>
    <div class="status-right">
        <span>
            <span class="glow-dot green" id="statusDot"></span>
            <span id="statusText" class="status-protected">[OK] PROTECTED</span>
        </span>
        <span id="headerTime"></span>
        <div class="header-controls">
            <button class="toggle-btn on" id="autoQToggle" onclick="toggleAutoQ()">
                <span class="toggle-dot"></span>
                <span id="autoQLabel">AUTO-Q ON</span>
            </button>
            <button class="control-btn" onclick="showIncidents()">[LIST] INCIDENTS</button>
            <button class="control-btn success" onclick="showQuarantine()">[FOLDER] QUARANTINE</button>
            <button class="control-btn danger" onclick="showBlacklist()">[LOCK] BLACKLIST</button>
            <button class="control-btn warning" onclick="showWhitelist()">[SHIELD] WHITELIST</button>
            <button class="control-btn" onclick="showReports()" style="border-color:#00ccff;color:#00ccff;">[DOC] REPORTS</button>
        </div>
    </div>
</header>

<div class="dashboard-content">
    <div class="grid">
        <div class="card col-span-3">
            <div class="card-title">Threat Level</div>
            <div id="threatDisplay"><span class="threat-badge badge-clean">CLEAN</span></div>
        </div>
        <div class="card col-span-3">
            <div class="card-title">Risk Score</div>
            <div class="value" id="riskScore">0</div>
            <div class="sub" id="riskTrend">No incidents</div>
        </div>
        <div class="card col-span-3">
            <div class="card-title">Incidents</div>
            <div class="value" id="incidentCount">0</div>
            <div class="sub" id="incidentBreakdown">Pending: 0 | Ransom: 0</div>
        </div>
        <div class="card col-span-3">
            <div class="card-title">System</div>
            <div class="value" id="responseMetric">0%</div>
            <div class="sub">CPU: <span id="cpuVal">0%</span> | RAM: <span id="ramVal">0%</span></div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-6">
            <div class="card-title">[CHART] Threat Activity</div>
            <div class="chart-container">
                <canvas id="threatChart"></canvas>
            </div>
        </div>
        <div class="card col-span-6">
            <div class="card-title">[CHART] System Resources</div>
            <div class="chart-container">
                <canvas id="systemChart"></canvas>
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-3">
            <div class="card-title">[CORE] Engine Status</div>
            <div id="engineStatus">
                <div class="list-item"><span>ML Updates</span><span id="mlUpdates">0</span></div>
                <div class="list-item"><span>ML Trusted</span><span id="mlTrusted">no</span></div>
                <div class="list-item"><span>IF Samples</span><span id="ifSamples">0</span></div>
                <div class="list-item"><span>IF Trusted</span><span id="ifTrusted">no</span></div>
                <div class="list-item"><span>Sessions</span><span id="sessionCount">0</span></div>
                <div class="list-item"><span>Honeypots</span><span id="honeypotCount">0</span></div>
            </div>
        </div>
        <div class="card col-span-3">
            <div class="card-title">[TIP] Recommendations</div>
            <div id="recommendationList" class="panel-hidden">
                <div class="recommendation-box">[i] No active threats.</div>
            </div>
        </div>
        <div class="card col-span-3">
            <div class="card-title">[LOCK] Quarantine <span style="font-size:8px;color:#2a5a4a;" id="quarantineCount"></span>
                <button class="control-btn success" style="font-size:8px;padding:2px 8px;" onclick="showQuarantine()">VIEW ALL</button>
            </div>
            <div id="quarantineList" style="max-height:200px;overflow-y:auto;">
                <div class="text-muted text-center">Empty</div>
            </div>
        </div>
        <div class="card col-span-3">
            <div class="card-title">[SHIELD] Whitelisted <span style="font-size:8px;color:#2a5a4a;" id="whitelistCount"></span>
                <button class="control-btn warning" style="font-size:8px;padding:2px 8px;" onclick="showWhitelist()">VIEW ALL</button>
            </div>
            <div id="whitelistList" style="max-height:200px;overflow-y:auto;">
                <div class="text-muted text-center">Loading…</div>
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-12">
            <div class="card-title">[LIVE] Engine Event Stream
                <span style="font-size:8px;color:#2a5a4a;">real-time from shield_core.analyze_event()</span>
            </div>
            <div class="event-log" id="eventLog">
                <div class="no-events">Waiting for events from shield_core engine...</div>
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card col-span-12">
            <div class="card-title">[LIST] Recent Incidents</div>
            <div id="incidentList" style="max-height:300px;overflow-y:auto;">
                <div class="text-muted text-center">No incidents yet</div>
            </div>
        </div>
    </div>
</div>

<div class="modal" id="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>
        <h2 id="modalTitle">Details</h2>
        <div id="modalBody"></div>
    </div>
</div>

<div class="footer-text">
    DSTERMINAL v6.0 • Shield_Core • <span id="footerTime"></span>
</div>

<script>
// ============================================================
// SocketIO
// ============================================================
const socket = io();

// ============================================================
// Charts
// ============================================================
let threatChart = null;
let systemChart = null;
let threatData = [];
let timeLabels = [];

function initCharts() {
    const threatCanvas = document.getElementById('threatChart');
    const systemCanvas = document.getElementById('systemChart');
    if (!threatCanvas || !systemCanvas) { setTimeout(initCharts, 500); return; }
    try {
        if (threatChart) threatChart.destroy();
        threatChart = new Chart(threatCanvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Start'],
                datasets: [{
                    label: 'Threat',
                    data: [0],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0,255,136,0.1)',
                    fill: true, tension: 0.4, borderWidth: 2,
                    pointRadius: 4, pointBackgroundColor: '#00ff88'
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: { duration: 250 },
                plugins: { legend: { labels: { color: '#2a5a4a', font: { size: 10 } } } },
                scales: {
                    y: {
                        min: 0, max: 4, ticks: {
                            callback: v => ['CLEAN','SUSP','HIGH','RANSOM','ANOM'][v] || v,
                            color: '#2a5a4a', font: { size: 9 }, stepSize: 1
                        },
                        grid: { color: 'rgba(0,255,136,0.05)' }
                    },
                    x: {
                        ticks: { color: '#2a5a4a', font: { size: 8 }, maxTicksLimit: 10 },
                        grid: { color: 'rgba(0,255,136,0.05)' }
                    }
                }
            }
        });

        if (systemChart) systemChart.destroy();
        systemChart = new Chart(systemCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['CPU','RAM','DISK'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#00ff88','#00ccff','#ffcc00'],
                    borderColor: '#0a0e17', borderWidth: 2
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#2a5a4a', font: { size: 10 } } }
                },
                cutout: '60%'
            }
        });
    } catch (e) {
        console.error('chart init error', e);
        setTimeout(initCharts, 1000);
    }
}

// ============================================================
// Threat state machine
// ============================================================
const THREAT_LEVELS = {
    'CLEAN': 0,
    'SUSPICIOUS': 1,
    'HIGH_RISK': 2,
    'RANSOMWARE_DETECTED': 3,
    'ANOMALY': 4
};

// How long the UI keeps displaying "threat active" after the last
// threat event. Long enough to cover the 20 s quarantine animation
// and let the user read it.
const THREAT_HOLD_MS = 25000;
const QUARANTINE_DURATION_MS = 20000;

let threatState = {
    level: 'CLEAN',
    lastThreatAt: 0,
    activeQuarantine: null,
};

function isActiveThreat() {
    return threatState.level !== 'CLEAN'
        && (Date.now() - threatState.lastThreatAt) < THREAT_HOLD_MS;
}

// ============================================================
// Danger alert banner
// ============================================================
function showDangerAlert(level) {
    const el = document.getElementById('dangerAlert');
    const txt = document.getElementById('dangerAlertText');
    const msg = {
        'SUSPICIOUS':          'SUSPICIOUS ACTIVITY DETECTED',
        'HIGH_RISK':           'HIGH RISK THREAT DETECTED',
        'RANSOMWARE_DETECTED': 'RANSOMWARE DETECTED — QUARANTINE ENGAGED',
        'ANOMALY':             'ANOMALOUS FILE BEHAVIOR DETECTED'
    }[level] || 'THREAT DETECTED';
    txt.textContent = msg;
    el.classList.add('show');
}
function hideDangerAlert() {
    document.getElementById('dangerAlert').classList.remove('show');
}

// ============================================================
// Quarantine progress (20 s, animated)
// ============================================================
const QUARANTINE_STAGES = [
    { pct:  10, label: 'Analyzing target…'       },
    { pct:  25, label: 'Correlating session…'    },
    { pct:  45, label: 'Evaluating response…'    },
    { pct:  65, label: 'Containing threat…'      },
    { pct:  85, label: 'Verifying integrity…'    },
    { pct: 100, label: 'Sealed.'                 },
];

function startQuarantineProgress(target, mode) {
    // mode = 'quarantine' (real action) or 'response' (informational)
    console.log('[startQuarantineProgress] mode=' + mode + ' target=' + target);
    mode = mode || 'response';

    if (threatState.activeQuarantine) {
        cancelQuarantineProgress();
    }
    const overlay  = document.getElementById('quarantineOverlay');
    const fill     = document.getElementById('qBarFill');
    const stage    = document.getElementById('qBarStage');
    const elapsed  = document.getElementById('qBarElapsed');
    const percent  = document.getElementById('qPercent');
    const status   = document.getElementById('qStatusText');
    const title    = document.getElementById('qPanelTitle');
    const targetEl = document.getElementById('qPanelTarget');

    // Wording differs by mode
    if (mode === 'quarantine') {
        title.textContent = 'QUARANTINE IN PROGRESS';
        status.textContent = 'Securing the file…';
    } else {
        title.textContent = 'THREAT RESPONSE IN PROGRESS';
        status.textContent = 'Analyzing and containing…';
    }
    status.className = 'q-status-text';

    targetEl.textContent = target || '—';
    fill.style.width = '0%';
    percent.textContent = '0%';
    overlay.classList.add('show');

    const start = Date.now();
    const state = { start, raf: null, timeout: null, target, mode };
    threatState.activeQuarantine = state;

    function tick() {
        const t = Math.min(1, (Date.now() - start) / QUARANTINE_DURATION_MS);
        const pct = Math.round(t * 100);
        fill.style.width = pct + '%';
        percent.textContent = pct + '%';
        elapsed.textContent = `${Math.floor(t * 20)}s / 20s`;
        for (let i = QUARANTINE_STAGES.length - 1; i >= 0; i--) {
            if (pct >= QUARANTINE_STAGES[i].pct) {
                if (stage.textContent !== QUARANTINE_STAGES[i].label) {
                    stage.textContent = QUARANTINE_STAGES[i].label;
                }
                break;
            }
        }
        if (t < 1) state.raf = requestAnimationFrame(tick);
        else finishQuarantineProgress(state);
    }
    state.raf = requestAnimationFrame(tick);
}

function finishQuarantineProgress(state) {
    if (threatState.activeQuarantine !== state) return;
    const statusEl = document.getElementById('qStatusText');
    const titleEl = document.getElementById('qPanelTitle');
    if (state.mode === 'quarantine') {
        titleEl.textContent = 'QUARANTINE COMPLETE';
        statusEl.textContent = 'Quarantined.';
    } else {
        titleEl.textContent = 'RESPONSE COMPLETE';
        statusEl.textContent = 'Threat logged.';
    }
    statusEl.className = 'q-status-text done';
    state.timeout = setTimeout(() => {
        document.getElementById('quarantineOverlay').classList.remove('show');
        threatState.activeQuarantine = null;
    }, 2500);
}

function cancelQuarantineProgress() {
    const q = threatState.activeQuarantine;
    if (!q) return;
    if (q.raf) cancelAnimationFrame(q.raf);
    if (q.timeout) clearTimeout(q.timeout);
    document.getElementById('quarantineOverlay').classList.remove('show');
    threatState.activeQuarantine = null;
}

// ============================================================
// Threat chart sampling
// ============================================================
function pushThreatSample() {
    const now = new Date().toLocaleTimeString();
    const active = isActiveThreat();
    const effectiveLevel = active ? THREAT_LEVELS[threatState.level] : 0;

    timeLabels.push(now);
    threatData.push(effectiveLevel);
    if (timeLabels.length > 60) { timeLabels.shift(); threatData.shift(); }
    if (!threatChart) return;

    const lineColor = active ? '#ff0033' : '#00ff88';
    const fillColor = active ? 'rgba(255,0,51,0.12)' : 'rgba(0,255,136,0.1)';
    threatChart.data.datasets[0].borderColor = lineColor;
    threatChart.data.datasets[0].pointBackgroundColor = lineColor;
    threatChart.data.datasets[0].backgroundColor = fillColor;
    threatChart.data.labels = timeLabels;
    threatChart.data.datasets[0].data = threatData;
    threatChart.update('none');
}

// ============================================================
// Reconcile threat UI (banner, status, recommendations)
// ============================================================
function reconcileThreatUI() {
    const active = isActiveThreat();
    const level = threatState.level;

    const statusText = document.getElementById('statusText');
    const statusDot  = document.getElementById('statusDot');

    if (active) {
        statusText.textContent = '[!] ATTACK';
        statusText.className = 'status-attack';
        statusDot.className = 'glow-dot red';
        showDangerAlert(level);
        // Recommendations panel is shown while a threat is active
        const rec = document.getElementById('recommendationList');
        rec.classList.remove('panel-hidden');
        if (!rec.dataset.populated) {
            rec.innerHTML = '<div class="recommendation-box">'
                          + '[!] Review the incident and confirm or override '
                          + 'the auto-response.</div>';
        }
    } else {
        statusText.textContent = '[OK] PROTECTED';
        statusText.className = 'status-protected';
        statusDot.className = 'glow-dot green';
        hideDangerAlert();
        // Recommendations panel hides when no active threat
        document.getElementById('recommendationList')
            .classList.add('panel-hidden');
    }
}

// ============================================================
// Status update handler
// ============================================================
function updateStatus(data) {
    const maps = {
        'CLEAN':               { cls: 'badge-clean',      text: 'CLEAN' },
        'SUSPICIOUS':          { cls: 'badge-suspicious', text: 'SUSPICIOUS' },
        'HIGH_RISK':           { cls: 'badge-high',       text: 'HIGH RISK' },
        'RANSOMWARE_DETECTED': { cls: 'badge-ransomware', text: '[!] RANSOMWARE' },
        'ANOMALY':             { cls: 'badge-anomaly',    text: 'ANOMALY' }
    };
    const t = maps[data.threat_level] || maps['CLEAN'];
    document.getElementById('threatDisplay').innerHTML =
        `<span class="threat-badge ${t.cls}">${t.text}</span>`;

    // Update the state machine from the polled status too
    if (data.threat_level && data.threat_level !== 'CLEAN') {
        threatState.level = data.threat_level;
        threatState.lastThreatAt = Date.now();
    } else if (data.threat_level === 'CLEAN'
               && (Date.now() - threatState.lastThreatAt) >= THREAT_HOLD_MS) {
        threatState.level = 'CLEAN';
    }
    reconcileThreatUI();

    document.getElementById('riskScore').textContent = Math.round(data.risk_score || 0);
    document.getElementById('riskTrend').textContent =
        data.incidents_ransomware
            ? `${data.incidents_ransomware} ransomware (24h)`
            : data.incidents_high_risk
              ? `${data.incidents_high_risk} high risk (24h)`
              : 'No incidents in last 24h';

    document.getElementById('incidentCount').textContent = data.incidents_total || 0;
    document.getElementById('incidentBreakdown').textContent =
        `Pending: ${data.incidents_pending || 0} | Ransom: ${data.incidents_ransomware || 0}`;

    if (data.system) {
        document.getElementById('cpuVal').textContent = Math.round(data.system.cpu || 0) + '%';
        document.getElementById('ramVal').textContent = Math.round(data.system.memory || 0) + '%';
        document.getElementById('responseMetric').textContent = Math.round(data.system.cpu || 0) + '%';
        if (systemChart) {
            systemChart.data.datasets[0].data = [
                Math.round(data.system.cpu || 0),
                Math.round(data.system.memory || 0),
                Math.round(data.system.disk || 0)
            ];
            systemChart.update('none');
        }
    }

    // Engine status
    document.getElementById('mlUpdates').textContent  = data.ml_updates || 0;
    document.getElementById('mlTrusted').textContent  = data.ml_trusted ? 'yes' : 'no';
    document.getElementById('mlTrusted').style.color  = data.ml_trusted ? '#00ff88' : '#ffcc00';
    document.getElementById('ifSamples').textContent  = data.if_samples || 0;
    document.getElementById('ifTrusted').textContent  = data.if_trusted ? 'yes' : 'no';
    document.getElementById('ifTrusted').style.color  = data.if_trusted ? '#00ff88' : '#ffcc00';
    document.getElementById('sessionCount').textContent   = data.sessions_tracked || 0;
    document.getElementById('honeypotCount').textContent  = data.honeypots || 0;

    if (data.recommendations) updateRecommendations(data.recommendations);
    if (data.quarantine)      updateQuarantine(data.quarantine);
    if (data.whitelist)       updateWhitelist(data.whitelist);
    if (data.incidents)       updateIncidentList(data.incidents);

    const now = new Date().toLocaleTimeString();
    document.getElementById('headerTime').textContent = now;
    document.getElementById('footerTime').textContent = new Date().toLocaleString();

    pushThreatSample();
}

// ============================================================
// Recommendations panel
// ============================================================
function updateRecommendations(recs) {
    const el = document.getElementById('recommendationList');
    // Visibility is owned by reconcileThreatUI(). Just populate.
    if (!recs || recs.length === 0) {
        el.dataset.populated = '';
        el.innerHTML = '<div class="recommendation-box">'
                     + '[i] Threat detected — waiting for engine '
                     + 'recommendation…</div>';
        return;
    }
    el.dataset.populated = '1';
    el.innerHTML = recs.map(r => `<div class="recommendation-box">${r}</div>`).join('');
}

// ============================================================
// Quarantine list
// ============================================================
function updateQuarantine(items) {
    const el = document.getElementById('quarantineList');
    document.getElementById('quarantineCount').textContent =
        `(${(items || []).length})`;
    if (!items || items.length === 0) {
        el.innerHTML = '<div class="text-muted text-center">Empty</div>';
        return;
    }
    el.innerHTML = items.slice(0, 10).map(f => `
        <div class="list-item">
            <span style="color:#ffcc00;font-size:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:180px;">
                ${f.name}
            </span>
            <span>
                <button class="action-btn success" onclick="restoreQ('${f.quarantine_path.replace(/\\/g,'\\\\')}')">R</button>
                <button class="action-btn danger" onclick="deleteQ('${f.quarantine_path.replace(/\\/g,'\\\\')}')">X</button>
            </span>
        </div>
    `).join('');
}

// ============================================================
// Incident list
// ============================================================
function updateIncidentList(incidents) {
    const el = document.getElementById('incidentList');
    if (!incidents || incidents.length === 0) {
        el.innerHTML = '<div class="text-muted text-center">No incidents yet</div>';
        return;
    }
    el.innerHTML = incidents.slice(0, 20).map(i => {
        const ev  = i.event || {};
        const dec = i.decision || {};
        const label = i.label;
        const lbl = label === 1 ? 'M' : label === 0 ? 'B' : '?';
        const lvl = dec.level || 'CLEAN';
        return `
            <div class="incident-row">
                <span style="color:#2a5a4a;min-width:70px;font-size:10px;">
                    ${new Date((ev.timestamp || 0) * 1000).toLocaleTimeString()}
                </span>
                <span class="op-${lvl}" style="padding:2px 8px;border-radius:3px;font-size:10px;">
                    ${lvl}
                </span>
                <span style="color:#00ccff;min-width:120px;font-size:10px;">
                    ${(ev.process_name || 'unknown').slice(0,20)}
                </span>
                <span style="color:#fff;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px;">
                    ${(ev.path || '').split(/[\\/]/).pop().slice(0,40)}
                </span>
                <span style="color:#00ff88;font-size:10px;min-width:40px;">
                    ${(dec.fused || 0).toFixed(2)}
                </span>
                <span style="min-width:30px;text-align:center;">[${lbl}]</span>
                <span>
                    <button class="label-btn mal" onclick="labelIncident('${i.file}', 1)">M</button>
                    <button class="label-btn ben" onclick="labelIncident('${i.file}', 0)">B</button>
                </span>
            </div>
        `;
    }).join('');
}

function updateWhitelist(items) {
    const el = document.getElementById('whitelistList');
    const countEl = document.getElementById('whitelistCount');
    if (countEl) countEl.textContent = `(${(items || []).length})`;

    if (!items || items.length === 0) {
        el.innerHTML = '<div class="text-muted text-center">Empty</div>';
        return;
    }
    // Show user-added first, then a sample of defaults
    const user = items.filter(p => p.source === 'user');
    const defaults = items.filter(p => p.source !== 'user');
    const shown = [...user, ...defaults].slice(0, 10);
    el.innerHTML = shown.map(p => `
        <div class="list-item">
            <span style="color:${p.source === 'user' ? '#ffcc00' : '#00ccff'};
                         font-size:10px;overflow:hidden;text-overflow:ellipsis;
                         white-space:nowrap;max-width:140px;"
                  title="${p.name}${p.source === 'user' ? ' (user)' : ''}">
                ${p.name}
            </span>
            <span class="category-badge cat-${p.category}">
                ${p.category.replace('windows-', 'win-').replace('third-party-', '3p-')}
            </span>
        </div>
    `).join('');
}

function showWhitelist() {
    const modal = document.getElementById('modal');
    document.getElementById('modalTitle').textContent =
        '[SHIELD] Whitelisted Processes (protected from kill)';
    document.getElementById('modalBody').innerHTML =
        '<div class="text-muted text-center">Loading…</div>';
    modal.classList.add('show');

    fetch('/api/whitelist').then(r => r.json()).then(items => {
        const body = document.getElementById('modalBody');
        if (!items || items.length === 0) {
            body.innerHTML = '<div class="text-muted text-center">Whitelist empty</div>';
            return;
        }

        // Group by category
        const byCat = {};
        items.forEach(p => {
            if (!byCat[p.category]) byCat[p.category] = [];
            byCat[p.category].push(p);
        });
        const order = [
            'windows-core', 'windows-shell', 'security-stack',
            'networking', 'windows-services', 'third-party-av',
            'user-added', 'other'
        ];

        let html = `
            <div style="margin-bottom:16px;padding:10px;background:rgba(0,204,255,0.05);border-left:3px solid #00ccff;border-radius:4px;">
                <div style="color:#00ccff;font-size:11px;letter-spacing:1px;margin-bottom:6px;">
                    [ + ] ADD PROCESS TO WHITELIST
                </div>
                <div style="display:flex;gap:8px;">
                    <input id="wl-add-input" type="text"
                           placeholder="e.g. myapp.exe or myapp"
                           style="flex:1;background:#0a0e17;border:1px solid rgba(0,204,255,0.35);
                                  color:#00ff88;padding:6px 10px;border-radius:4px;
                                  font-family:'Courier New',monospace;font-size:12px;">
                    <button class="control-btn warning" onclick="whitelistAdd()">ADD</button>
                </div>
                <div style="color:#2a5a4a;font-size:9px;margin-top:6px;">
                    Name matched case-insensitively; .exe suffix optional.
                    Built-in defaults cannot be removed.
                </div>
            </div>
        `;

        order.forEach(cat => {
            const entries = byCat[cat];
            if (!entries || entries.length === 0) return;
            html += `<div style="margin:14px 0 6px 0;">
                       <span class="category-badge cat-${cat}">${cat}</span>
                       <span style="color:#2a5a4a;font-size:10px;margin-left:8px;">
                           ${entries.length} process(es)
                       </span>
                     </div>`;
            entries.forEach(p => {
                const isDefault = p.source === 'default';
                const removeBtn = isDefault
                    ? `<span style="color:#2a5a4a;font-size:9px;
                                    margin-right:8px;">[built-in]</span>`
                    : `<button class="action-btn danger"
                               style="padding:2px 8px;font-size:9px;"
                               onclick="whitelistRemove('${p.name}')">REMOVE</button>`;
                html += `
                    <div class="list-item" style="display:flex;
                                                  justify-content:space-between;
                                                  align-items:center;">
                        <span style="color:#00ccff;font-size:11px;
                                     font-family:'Courier New',monospace;">
                            ${p.name}
                        </span>
                        ${removeBtn}
                    </div>`;
            });
        });

        body.innerHTML = html;

        // Wire the Enter key in the add input
        const inp = document.getElementById('wl-add-input');
        if (inp) {
            inp.addEventListener('keydown', e => {
                if (e.key === 'Enter') whitelistAdd();
            });
            inp.focus();
        }
    });
}

function showReports() {
    const modal = document.getElementById('modal');
    document.getElementById('modalTitle').textContent =
        '[DOC] Detection Reports';
    document.getElementById('modalBody').innerHTML =
        '<div class="text-muted text-center">Loading…</div>';
    modal.classList.add('show');

    fetch('/api/reports/list').then(r => r.json()).then(items => {
        const body = document.getElementById('modalBody');
        if (!items || items.length === 0) {
            body.innerHTML =
                '<div class="text-muted text-center">' +
                'No reports yet. Reports are generated automatically ' +
                'on every SUSPICIOUS-or-higher detection.</div>';
            return;
        }

        const levelColors = {
            'CLEAN': '#00ff88',
            'SUSPICIOUS': '#ffcc00',
            'HIGH_RISK': '#ff6600',
            'RANSOMWARE_DETECTED': '#ff0033',
            'ANOMALY': '#bc8cff',
        };

        const headerHtml = `
            <div style="margin-bottom:16px;padding:10px;
                        background:rgba(0,204,255,0.05);
                        border-left:3px solid #00ccff;border-radius:4px;">
                <div style="color:#00ccff;font-size:11px;
                            letter-spacing:1px;">
                    ${items.length} report(s) in
                    C:\\Users\\stark\\dsterminal_workspace\\ransom\\reports
                </div>
                <div style="color:#2a5a4a;font-size:9px;margin-top:4px;">
                    Each bundle contains HTML (viewable in browser),
                    JSON (machine-readable), and PDF (printable)
                    &mdash; if reportlab is installed.
                </div>
            </div>
        `;

        const rowsHtml = items.slice(0, 200).map(r => {
            const s = r.summary || {};
            const lvl = s.level || '?';
            const color = levelColors[lvl] || '#888';
            const ts = s.timestamp
                ? new Date(s.timestamp * 1000).toLocaleString()
                : new Date(r.mtime * 1000).toLocaleString();
            const name = (s.path || '').split(/[\\/]/).pop() || r.name;
            const proc = s.process || '?';
            const fused = (s.fused != null) ? s.fused.toFixed(2) : '—';

            const dl = (ext, label, enabled) => enabled
                ? `<a class="action-btn success"
                       style="text-decoration:none;padding:3px 8px;
                              border-radius:3px;margin-left:4px;
                              font-size:10px;"
                       href="/api/reports/download/${encodeURIComponent(r.name)}/${ext}">
                       ${label}
                     </a>`
                : `<span class="action-btn"
                        style="opacity:0.3;padding:3px 8px;
                               border-radius:3px;margin-left:4px;
                               font-size:10px;color:#666;
                               border:1px solid #333;">
                       ${label}
                     </span>`;

            return `
                <div class="incident-row" style="display:flex;
                                                 justify-content:space-between;
                                                 align-items:center;
                                                 padding:8px 10px;
                                                 border-bottom:1px solid rgba(0,255,136,0.05);">
                    <span style="color:#2a5a4a;min-width:140px;font-size:10px;">
                        ${ts}
                    </span>
                    <span style="color:${color};font-weight:bold;
                                 min-width:150px;font-size:10px;">
                        ${lvl}
                    </span>
                    <span style="color:#00ccff;min-width:100px;font-size:10px;
                                 overflow:hidden;text-overflow:ellipsis;
                                 white-space:nowrap;"
                          title="${proc}">
                        ${proc.substring(0, 15)}
                    </span>
                    <span style="color:#fff;flex:1;font-size:10px;
                                 overflow:hidden;text-overflow:ellipsis;
                                 white-space:nowrap;"
                          title="${s.path || ''}">
                        ${name}
                    </span>
                    <span style="color:#00ff88;min-width:50px;font-size:10px;
                                 text-align:right;">
                        ${fused}
                    </span>
                    <span style="min-width:210px;text-align:right;">
                        ${dl('report.html', 'HTML', r.files['report.html'])}
                        ${dl('report.json', 'JSON', r.files['report.json'])}
                        ${dl('report.pdf', 'PDF', r.files['report.pdf'])}
                    </span>
                </div>
            `;
        }).join('');

        body.innerHTML = headerHtml + rowsHtml;
    }).catch(err => {
        document.getElementById('modalBody').innerHTML =
            '<div class="text-muted text-center">' +
            'Failed to load reports: ' + err.message + '</div>';
    });
}

function whitelistAdd() {
    const inp = document.getElementById('wl-add-input');
    if (!inp) return;
    const name = inp.value.trim();
    if (!name) return;
    fetch('/api/whitelist/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({process_name: name})
    }).then(r => r.json()).then(d => {
        if (d.success) {
            inp.value = '';
            refresh();
            showWhitelist();
        } else {
            alert(d.error || d.message || 'add failed');
        }
    });
}

function whitelistRemove(name) {
    if (!confirm(`Remove ${name} from whitelist?`)) return;
    fetch('/api/whitelist/remove', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({process_name: name})
    }).then(r => r.json()).then(d => {
        if (d.success) {
            refresh();
            showWhitelist();
        } else {
            alert(d.error || d.message || 'remove failed');
        }
    });
}

// ============================================================
// Event stream
// ============================================================
function appendEvent(ev, dec) {
    const log = document.getElementById('eventLog');
    const noEv = log.querySelector('.no-events');
    if (noEv) log.innerHTML = '';
    const div = document.createElement('div');
    div.className = 'event-item';
    const lvl = dec.level || 'CLEAN';
    div.innerHTML = `
        <span class="time">${new Date((ev.timestamp || 0) * 1000).toLocaleTimeString()}</span>
        <span class="proc">[${(ev.process_name || 'system').slice(0,15)}]</span>
        <span class="file" title="${ev.path || ''}">${(ev.path || '').split(/[\\/]/).pop().slice(0,50)}</span>
        <span class="operation op-${lvl}">${lvl}</span>
    `;
    log.insertBefore(div, log.firstChild);
    while (log.children.length > 100) log.removeChild(log.lastChild);
}

// ============================================================
// Auto-Q toggle
// ============================================================
async function toggleAutoQ() {
    const btn = document.getElementById('autoQToggle');
    const lbl = document.getElementById('autoQLabel');
    const nowOn = btn.classList.contains('on');
    const next = !nowOn;
    btn.classList.toggle('on', next);
    btn.classList.toggle('off', !next);
    lbl.textContent = next ? 'AUTO-Q ON' : 'AUTO-Q OFF';
    try {
        await fetch('/api/auto-response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: next })
        });
    } catch (e) {
        btn.classList.toggle('on', nowOn);
        btn.classList.toggle('off', !nowOn);
        lbl.textContent = nowOn ? 'AUTO-Q ON' : 'AUTO-Q OFF';
    }
}

// ============================================================
// Modal + actions
// ============================================================
function closeModal() { document.getElementById('modal').classList.remove('show'); }

function showIncidents() {
    const modal = document.getElementById('modal');
    document.getElementById('modalTitle').textContent = '[LIST] All Incidents';
    document.getElementById('modalBody').innerHTML =
        '<div class="text-muted text-center">Loading...</div>';
    modal.classList.add('show');
    fetch('/api/incidents?limit=200').then(r => r.json()).then(incs => {
        const body = document.getElementById('modalBody');
        if (!incs.length) {
            body.innerHTML = '<div class="text-muted text-center">No incidents</div>';
            return;
        }
        body.innerHTML = incs.map(i => {
            const ev = i.event || {};
            const dec = i.decision || {};
            const lbl = i.label === 1 ? 'M' : i.label === 0 ? 'B' : '?';
            return `
                <div class="incident-row">
                    <span style="color:#2a5a4a;font-size:10px;">
                        ${new Date((ev.timestamp || 0) * 1000).toLocaleString()}
                    </span>
                    <span class="op-${dec.level}" style="padding:2px 8px;border-radius:3px;font-size:10px;">
                        ${dec.level}
                    </span>
                    <span style="color:#00ccff;font-size:10px;">${ev.process_name}</span>
                    <span style="color:#fff;flex:1;font-size:10px;overflow:hidden;text-overflow:ellipsis;">
                        ${ev.path}
                    </span>
                    <span style="color:#00ff88;">${(dec.fused||0).toFixed(2)}</span>
                    <span>[${lbl}]</span>
                    <button class="label-btn mal" onclick="labelIncident('${i.file}', 1)">M</button>
                    <button class="label-btn ben" onclick="labelIncident('${i.file}', 0)">B</button>
                </div>
            `;
        }).join('');
    });
}

function showQuarantine() {
    const modal = document.getElementById('modal');
    document.getElementById('modalTitle').textContent = '[FOLDER] Quarantine';
    document.getElementById('modalBody').innerHTML =
        '<div class="text-muted text-center">Loading...</div>';
    modal.classList.add('show');
    fetch('/api/quarantine/list').then(r => r.json()).then(items => {
        const body = document.getElementById('modalBody');
        if (!items.length) {
            body.innerHTML = '<div class="text-muted text-center">Empty</div>';
            return;
        }
        body.innerHTML = items.map(f => `
            <div class="list-item">
                <span style="color:#ffcc00;font-size:10px;">${f.quarantine_path}</span>
                <span>
                    <button class="action-btn success" onclick="restoreQ('${f.quarantine_path.replace(/\\/g,'\\\\')}')">RESTORE</button>
                    <button class="action-btn danger" onclick="deleteQ('${f.quarantine_path.replace(/\\/g,'\\\\')}')">DELETE</button>
                </span>
            </div>
        `).join('');
    });
}

function showBlacklist() {
    const modal = document.getElementById('modal');
    document.getElementById('modalTitle').textContent = '[LOCK] Blacklisted Processes';
    document.getElementById('modalBody').innerHTML =
        '<div class="text-muted text-center">Loading...</div>';
    modal.classList.add('show');
    fetch('/api/blacklist').then(r => r.json()).then(items => {
        const body = document.getElementById('modalBody');
        if (!items.length) {
            body.innerHTML = '<div class="text-muted text-center">Blacklist empty</div>';
            return;
        }
        body.innerHTML = items.map(e => `
            <div class="list-item">
                <span style="color:#ff0033;">${e.process}</span>
                <span style="color:#2a5a4a;font-size:10px;">hits=${e.hits}</span>
                <button class="action-btn danger" onclick="removeBlacklist('${e.process}')">REMOVE</button>
            </div>
        `).join('');
    });
}

function restoreQ(path) {
    if (!confirm('Restore this file?')) return;
    fetch('/api/quarantine/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quarantine_path: path })
    }).then(r => r.json()).then(d => {
        alert(d.success ? 'Restored' : 'Failed');
        refresh();
    });
}
function deleteQ(path) {
    if (!confirm('Permanently delete?')) return;
    fetch('/api/quarantine/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quarantine_path: path })
    }).then(r => r.json()).then(d => {
        alert(d.success ? 'Deleted' : 'Failed');
        refresh();
    });
}
function labelIncident(file, label) {
    fetch('/api/incidents/' + encodeURIComponent(file) + '/label', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label: label })
    }).then(r => r.json()).then(d => {
        if (!d.success) alert('Label failed');
        refresh();
    });
}
function removeBlacklist(name) {
    if (!confirm(`Remove ${name} from blacklist?`)) return;
    fetch('/api/blacklist/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ process_name: name })
    }).then(r => r.json()).then(d => {
        alert(d.success ? 'Removed' : 'Failed');
        showBlacklist();
    });
}

function refresh() {
    fetch('/api/status').then(r => r.json()).then(updateStatus).catch(() => {});
    // Populate whitelist on boot
    fetch('/api/whitelist').then(r => r.json()).then(updateWhitelist).catch(() => {});
}

// ============================================================
// SocketIO event handlers
// ============================================================
socket.on('connect', () => {
    console.log('connected to engine bridge');
    socket.emit('subscribe_updates');
});

socket.on('status_update', updateStatus);

socket.on('engine_event', (payload) => {
    console.log('[engine_event]', payload.decision.level, payload.decision.fused);
    appendEvent(payload.event, payload.decision);

    const lvl = payload.decision.level;

    if (lvl && lvl !== 'CLEAN') {
        // Close any open modal — a threat takes precedence
        document.getElementById('modal').classList.remove('show');

        threatState.level = lvl;
        threatState.lastThreatAt = Date.now();
        reconcileThreatUI();
        pushThreatSample();

        // Unconditionally show the overlay. Any prior animation is
        // cancelled by startQuarantineProgress itself.
        const target = (payload.event && payload.event.path) || '—';
        startQuarantineProgress(target, 'response');
    }
});

// Quarantine lifecycle from the engine
socket.on('quarantine_progress', (payload) => {
    console.log('[quarantine_progress]', payload.phase, payload.path, payload.level);
    if (payload.phase === 'start') {
            // If a 'response' overlay is already showing, upgrade it
        if (threatState.activeQuarantine &&
            threatState.activeQuarantine.mode === 'response') {
            cancelQuarantineProgress();
        }
        startQuarantineProgress(payload.path, 'quarantine');

        threatState.level = payload.level || threatState.level;
        threatState.lastThreatAt = Date.now();
        reconcileThreatUI();
    }
});

// ============================================================
// Boot
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    refresh();
    setInterval(refresh, 5000);

    // Decay ticker — re-evaluates the threat state every second so
    // the banner and panel hide promptly once the hold window
    // expires, without waiting for the next poll.
    setInterval(() => {
        const wasActive = isActiveThreat();
        reconcileThreatUI();
        if (wasActive && !isActiveThreat()) {
            pushThreatSample();
        }
    }, 1000);

    // Sync Auto-Q toggle state from the engine
    fetch('/api/auto-response').then(r => r.json()).then(d => {
        const on = d.enabled !== false;
        const btn = document.getElementById('autoQToggle');
        const lbl = document.getElementById('autoQLabel');
        btn.classList.toggle('on', on);
        btn.classList.toggle('off', !on);
        lbl.textContent = on ? 'AUTO-Q ON' : 'AUTO-Q OFF';
    });
});
</script>
</body>
</html>
"""

# CLI COMMANDS

def generate_synthetic_training_data(n_benign=2000, n_malicious=2000):
    rng = np.random.default_rng(7)
    X, y = [], []
    NF = FeatureVector.n_features()

    def pad(row):
        while len(row) < NF: row.append(0.0)
        return row[:NF]

    for _ in range(n_benign):
        X.append(pad([
            rng.normal(4.5, 0.8), rng.normal(0.01, 0.02),
            rng.choice([0, 1], p=[0.97, 0.03]), 0,
            rng.integers(0, 2), rng.integers(0, 2),
            rng.uniform(0.2, 0.6), rng.uniform(0, 5),
            rng.integers(1, 20), rng.integers(1, 3),
            rng.uniform(1e4, 1e6), rng.uniform(0, 0.1),
            0, 0.0, rng.integers(8, 19),
            rng.choice([0, 1], p=[0.9, 0.1]), rng.uniform(0.8, 1.5),
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        ]))
        y.append(0)

    for _ in range(n_malicious):
        X.append(pad([
            rng.normal(7.7, 0.25), rng.normal(1.5, 0.5),
            rng.choice([0, 1], p=[0.15, 0.85]),
            rng.choice([0, 1], p=[0.7, 0.3]),
            rng.integers(0, 2), rng.integers(0, 2),
            rng.uniform(0.8, 1.0), rng.uniform(20, 200),
            rng.integers(50, 5000), rng.integers(5, 30),
            rng.uniform(1e3, 1e6), rng.uniform(0.4, 1.0),
            rng.integers(0, 5), rng.uniform(0.0, 0.9),
            rng.choice([rng.integers(0, 8), rng.integers(19, 24)]),
            rng.choice([0, 1], p=[0.4, 0.6]), rng.uniform(4.0, 25.0),
            rng.choice([0, 1], p=[0.3, 0.7]),
            rng.uniform(0.2, 1.0), rng.uniform(0.3, 1.0),
            rng.uniform(0.4, 1.0), rng.uniform(0.3, 1.0),
            rng.uniform(0.3, 1.0),
        ]))
        y.append(1)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


def generate_realistic_synthetic(n_benign=4000, n_malicious=4000):
    """Realistic dataset with 5% label noise for real-world testing."""
    rng = np.random.default_rng(123)
    X, y = [], []
    NF = FeatureVector.n_features()

    def pad(row):
        while len(row) < NF: row.append(0.0)
        return row[:NF]

    for _ in range(int(n_benign * 0.85)):
        X.append(pad([
            rng.normal(4.2, 0.6), rng.normal(0.005, 0.01),
            0, 0, rng.integers(0, 2), rng.integers(0, 2),
            rng.uniform(0.1, 0.4), rng.uniform(0, 3),
            rng.integers(1, 15), rng.integers(1, 3),
            rng.uniform(5e3, 5e5), rng.uniform(0, 0.05),
            0, 0.0, rng.integers(8, 19), 0, rng.uniform(0.7, 1.4),
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        ]))
        y.append(0)

    for _ in range(int(n_benign * 0.15)):
        X.append(pad([
            rng.normal(6.9, 0.7), rng.normal(0.5, 0.4),
            rng.choice([0, 1], p=[0.85, 0.15]), 0, 0,
            rng.integers(0, 2), rng.uniform(0.6, 0.9),
            rng.uniform(8, 30), rng.integers(30, 300),
            rng.integers(1, 5), rng.uniform(1e5, 5e6),
            rng.uniform(0.05, 0.25), 0, 0.0,
            rng.integers(0, 24), 1, rng.uniform(2.0, 5.0),
            rng.uniform(0, 0.4), rng.uniform(0, 0.3), rng.uniform(0, 0.4),
            rng.uniform(0.1, 0.5), rng.uniform(0, 0.4), rng.uniform(0, 0.5),
        ]))
        y.append(0)

    for _ in range(int(n_malicious * 0.65)):
        X.append(pad([
            rng.normal(7.85, 0.15), rng.normal(1.8, 0.5),
            1, rng.choice([0, 1], p=[0.6, 0.4]),
            rng.integers(0, 2), rng.integers(0, 2),
            rng.uniform(0.85, 1.0), rng.uniform(30, 250),
            rng.integers(100, 8000), rng.integers(6, 40),
            rng.uniform(5e2, 5e5), rng.uniform(0.5, 1.0),
            rng.integers(0, 8), rng.uniform(0.0, 0.95),
            rng.choice([rng.integers(0, 7), rng.integers(20, 24)]),
            1, rng.uniform(5.0, 30.0),
            rng.uniform(0.4, 1.0), rng.uniform(0.4, 1.0),
            rng.uniform(0.4, 1.0), rng.uniform(0.6, 1.0),
            rng.uniform(0.5, 1.0), rng.uniform(0.3, 1.0),
        ]))
        y.append(1)

    for _ in range(int(n_malicious * 0.35)):
        X.append(pad([
            rng.normal(6.2, 0.6), rng.normal(0.3, 0.3),
            rng.choice([0, 1], p=[0.55, 0.45]),
            rng.choice([0, 1], p=[0.9, 0.1]),
            rng.integers(0, 2), rng.integers(0, 2),
            rng.uniform(0.5, 0.8), rng.uniform(2, 12),
            rng.integers(10, 80), rng.integers(2, 6),
            rng.uniform(5e3, 1e6), rng.uniform(0.05, 0.4),
            rng.integers(0, 3), rng.uniform(0.0, 0.4),
            rng.integers(0, 24),
            rng.choice([0, 1], p=[0.5, 0.5]),
            rng.uniform(1.2, 3.5),
            rng.uniform(0.2, 0.7), rng.uniform(0.1, 0.5),
            rng.uniform(0.1, 0.5), rng.uniform(0.3, 0.8),
            rng.uniform(0.2, 0.6), rng.uniform(0.2, 0.6),
        ]))
        y.append(1)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    # Inject 5% label noise
    n_flip = int(len(y) * 0.05)
    if n_flip > 0:
        flip_idx = rng.choice(len(y), size=n_flip, replace=False)
        for i in flip_idx:
            y[i] = 1 - y[i]

    idx = rng.permutation(len(X))
    return X[idx], y[idx]


def bootstrap_model(workspace_dir, backend="lr", realistic=True):
    os.makedirs(os.path.join(workspace_dir, "models"), exist_ok=True)
    if realistic:
        X, y = generate_realistic_synthetic()
    else:
        X, y = generate_synthetic_training_data()
    clf = make_classifier(backend)
    print(f"[*] Training {backend} on {len(X)} synthetic samples...")
    clf.fit(X, y, epochs=80, batch_size=64, verbose=True)
    ext = 'pt' if backend == 'torch' and TORCH_OK else 'pkl'
    out = os.path.join(workspace_dir, "models", f"shield_clf.{ext}")
    clf.save(out)
    print(f"[+] Saved → {out}")
    return out


def load_csv(csv_path):
    X, y = [], []
    with open(csv_path, newline='') as f:
        rows = list(csv.reader(f))
    if not rows:
        return np.array([]), np.array([])

    start = 0
    try:
        float(rows[0][0])
        float(rows[0][-1])
    except (ValueError, IndexError):
        start = 1

    nf = FeatureVector.n_features()
    skipped = 0
    for idx, row in enumerate(rows[start:], start=start + 1):
        if not row or all(not c.strip() for c in row):
            continue
        if len(row) < nf + 1:
            skipped += 1
            if skipped <= 5:
                print(f"{Colors.YELLOW}[!] {csv_path}:{idx}: "
                      f"expected {nf + 1} columns, got {len(row)} — skipped"
                      f"{Colors.END}")
            continue
        try:
            X.append([float(v) for v in row[:nf]])
            y.append(int(float(row[nf])))
        except (ValueError, TypeError) as e:
            skipped += 1
            if skipped <= 5:
                print(f"{Colors.YELLOW}[!] {csv_path}:{idx}: {e} — skipped"
                      f"{Colors.END}")
            continue

    if skipped > 5:
        print(f"{Colors.YELLOW}[!] {csv_path}: skipped {skipped} malformed "
              f"row(s) total{Colors.END}")

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)

# ============================================================
# ANALYST CLI (for `label`)
# ============================================================
class AnalystCLI:
    def __init__(self, api):
        self.api = api

    def list_pending(self, include_observer=False):
        pending = []
        for inc in self.api.list_incidents(limit=1000, include_labeled=False):
            proc = inc.get('event', {}).get('process_name', '')
            if not include_observer and proc in OBSERVER_PROCESS_NAMES:
                continue
            pending.append(inc)
        return pending

    def label_incident(self, filename, label):
        return self.api.label_incident(filename, label)

    def bulk_label_report(self):
        incidents = self.api.list_incidents(limit=10000)
        lb = lm = p = 0
        for i in incidents:
            if i.get('label') == 0: lb += 1
            elif i.get('label') == 1: lm += 1
            else: p += 1
        print(f"\n{Colors.BOLD}Dataset stats{Colors.END}")
        print(f"  Total : {len(incidents)}")
        print(f"  Benign: {Colors.GREEN}{lb}{Colors.END}  "
              f"Malicious: {Colors.RED}{lm}{Colors.END}  "
              f"Pending: {Colors.YELLOW}{p}{Colors.END}")

    def run_interactive(self, include_observer=False):
        pending = self.list_pending(include_observer=include_observer)
        if not pending:
            print(f"{Colors.GREEN}No pending incidents.{Colors.END}")
            return
        print(f"\n{Colors.BOLD}{len(pending)} incidents pending review{Colors.END}\n")
        for inc in pending:
            ev = inc.get('event', {})
            dec = inc.get('decision', {})
            print(f"\n  {Colors.CYAN}{ev.get('process_name', '?')}{Colors.END}")
            print(f"  {ev.get('path', '')}")
            print(f"  {Colors.YELLOW}{dec.get('level')}{Colors.END} "
                  f"rule={dec.get('rule',0):.2f} "
                  f"ml={dec.get('ml',0):.2f} "
                  f"fused={dec.get('fused',0):.2f}")
            for r in dec.get('reasons', [])[:4]:
                print(f"    → {r}")
            try:
                choice = input("\n  [m]alicious [b]enign [s]kip [q]uit > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print(); break
            if choice == 'm':
                self.label_incident(inc['file'], 1)
                print(f"  {Colors.RED}✓ marked malicious{Colors.END}")
            elif choice == 'b':
                self.label_incident(inc['file'], 0)
                print(f"  {Colors.GREEN}✓ marked benign{Colors.END}")
            elif choice == 'q':
                break
            else:
                print(f"  {Colors.DIM}skipped{Colors.END}")
        print(f"\n{Colors.GREEN}✓ Feedback applied.{Colors.END}")


# ============================================================
# CLI COMMAND IMPLEMENTATIONS
# ============================================================
def cmd_demo(args):
    typer = AutoTypeEngine(delay=0.02)
    os.system('cls' if os.name == 'nt' else 'clear')
    print_boxed(
        "DSTERMINAL v6.0 — UNIFIED SHIELD_CORE EDITION",
        [
            "",
            f"{Colors.CYAN}Engine + UI + CLI + Daemon — one file, one truth{Colors.END}",
            "",
        ],
        color=Colors.CYAN,
    )
    print()

    ws = resolve_workspace_dir(args.workspace)
    backend = getattr(args, 'backend', 'lr')
    ext = 'pt' if backend == 'torch' and TORCH_OK else 'pkl'
    clf_path = os.path.join(ws, "models", f"shield_clf.{ext}")

    if not os.path.exists(clf_path):
        typer.type_status(f"Bootstrapping synthetic model ({backend})...")
        bootstrap_model(ws, backend=backend)

    shield = ShieldCore(workspace_dir=ws,
                        shadow_mode=getattr(args, 'shadow', False),
                        backend=backend)

    typer.type_status("Running detection tests...", Colors.CYAN)
    hp = shield.honeypot_paths[0] if shield.honeypot_paths else "/tmp/hp.txt"
    tmpdir = tempfile.gettempdir()
    doc_path = os.path.join(tmpdir, "document.docx")
    enc_path = os.path.join(tmpdir, "payroll.xlsx.encrypted")

    with open(doc_path, 'w') as f:
        f.write("benign document content " * 100)
    with open(enc_path, 'wb') as f:
        f.write(os.urandom(4096))

    tests = [
        (hp, "invoice.pdf.exe", "malicious (honeypot veto)"),
        (doc_path, "winword.exe", "clean"),
        (enc_path, "cryptolocker.exe", "malicious"),
    ]
    for path, proc, expect in tests:
        ev = FileEvent(path=path, operation='write',
                       process_name=proc, pid=9999)
        shield.analyze_event(ev)

    try:
        shield.generate_forensic_report()
    except Exception:
        pass

    st = shield.get_status()
    typer.type_box("✅ ENGINE STATUS", [
        f"Backend        : {st['backend']}",
        f"ML updates     : {st['ml_updates']:,}  trusted={st['ml_trusted']}",
        f"IF samples     : {st['if_samples']}",
        f"IF ready       : {st['if_ready']}",
        f"Blacklist size : {st['blacklist_size']}",
        f"Workspace      : {shield.workspace_dir}",
        "",
        "Next:",
    ], Colors.GREEN)


def cmd_make_dataset(args):
    ws = resolve_workspace_dir(args.workspace)
    out = args.out or os.path.join(ws, "training", "synth.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    X, y = generate_realistic_synthetic(
        n_benign=args.n_benign, n_malicious=args.n_malicious)
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(FeatureVector.feature_names() + ['label'])
        for xi, yi in zip(X, y):
            w.writerow(list(xi) + [int(yi)])
    nb = int((y == 0).sum()); nm = int((y == 1).sum())
    print(f"{Colors.GREEN}[+] {len(X)} samples ({nb}B/{nm}M) → {out}{Colors.END}")


def cmd_accuracy(args):
    ws = resolve_workspace_dir(args.workspace)
    csv_path = args.csv or os.path.join(ws, "training", "synth.csv")
    if not os.path.exists(csv_path):
        print(f"{Colors.RED}[x] {csv_path} not found.{Colors.END}")
        print(f"    Run `python dsterminal.py make-dataset` first.")
        return
    X, y = load_csv(csv_path)
    if len(X) == 0:
        print(f"{Colors.RED}[x] Empty dataset.{Colors.END}"); return
    nb = int((y == 0).sum()); nm = int((y == 1).sum())
    print(f"{Colors.BOLD}Dataset{Colors.END}: {len(X)} samples ({nb}B/{nm}M)")

    X_tr, X_te, y_tr, y_te = stratified_split(X, y, test_size=args.test_size, seed=args.seed)
    print(f"  Train: {len(X_tr)}  Test: {len(X_te)}")

    clf = make_classifier(args.backend)
    print(f"\n{Colors.CYAN}[*] Training {args.backend}...{Colors.END}")
    clf.fit(X_tr, y_tr, epochs=args.epochs, batch_size=64, verbose=True)

    probs_te = np.array([clf.predict_proba(x) for x in X_te])
    preds_te = (probs_te >= args.threshold).astype(int)
    m = ModelEvaluator.metrics(y_te, preds_te, probs_te)
    ModelEvaluator.print_report(f"{args.backend.upper()} — Test Set", m)

    print(f"\n{Colors.BOLD}Threshold Sweep{Colors.END}")
    print(f"  {'Thr':>5} {'Prec':>7} {'Rec':>7} {'F1':>7} {'FPR':>7} {'Acc':>7}")
    for row in ModelEvaluator.threshold_sweep(y_te, probs_te):
        print(f"  {row['threshold']:>5.2f} {row['precision']:>7.3f} "
              f"{row['recall']:>7.3f} {row['f1']:>7.3f} "
              f"{row['fpr']:>7.3f} {row['accuracy']:>7.3f}")

    print(f"\n{Colors.BOLD}Calibration{Colors.END}")
    print(f"  {'Bin':>10} {'N':>5} {'AvgPred':>9} {'AvgTrue':>9}")
    for r in ModelEvaluator.calibration(y_te, probs_te):
        print(f"  {r['bin']:>10} {r['count']:>5} "
              f"{r['avg_pred']:>9.3f} {r['avg_true']:>9.3f}")


def cmd_cv(args):
    ws = resolve_workspace_dir(args.workspace)
    csv_path = args.csv or os.path.join(ws, "training", "synth.csv")
    if not os.path.exists(csv_path):
        print(f"{Colors.RED}[x] {csv_path} not found.{Colors.END}")
        return
    X, y = load_csv(csv_path)
    if len(X) == 0:
        print(f"{Colors.RED}[x] Empty.{Colors.END}")
        return
    k = args.folds
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(X))
    folds = np.array_split(idx, k)
    print(f"{Colors.BOLD}{k}-Fold CV{Colors.END} ({len(X)} samples)\n")
    print(f"  {'Fold':>5} {'Acc':>7} {'Prec':>7} {'Rec':>7} {'F1':>7} {'AUC':>7}")
    all_m = []
    for i in range(k):
        test_idx = folds[i]
        train_idx = np.concatenate([folds[j] for j in range(k) if j != i])
        clf = make_classifier(args.backend)
        clf.fit(X[train_idx], y[train_idx], epochs=args.epochs, verbose=False)
        probs = np.array([clf.predict_proba(x) for x in X[test_idx]])
        preds = (probs >= 0.5).astype(int)
        m = ModelEvaluator.metrics(y[test_idx], preds, probs)
        all_m.append(m)
        print(f"  {i+1:>5} {m['accuracy']:>7.3f} {m['precision']:>7.3f} "
              f"{m['recall']:>7.3f} {m['f1']:>7.3f} {m.get('roc_auc', 0):>7.3f}")
    avg = {kk: round(float(np.mean([m[kk] for m in all_m])), 4)
           for kk in ['accuracy','precision','recall','f1','roc_auc']}
    std = {kk: round(float(np.std([m[kk] for m in all_m])), 4)
           for kk in ['accuracy','precision','recall','f1','roc_auc']}
    print(f"\n  {Colors.BOLD}Mean ± Std{Colors.END}")
    for kk in avg:
        print(f"    {kk:10s} {avg[kk]:.4f} ± {std[kk]:.4f}")


def cmd_train(args):
    ws = resolve_workspace_dir(args.workspace)
    ext = 'pt' if args.backend == 'torch' and TORCH_OK else 'pkl'
    out = os.path.join(ws, "models", f"shield_clf.{ext}")
    X, y = load_csv(args.csv)
    if len(X) == 0:
        print(f"{Colors.RED}[x] No data.{Colors.END}"); return
    print(f"[*] Training {args.backend} on {len(X)} samples...")
    clf = make_classifier(args.backend)
    clf.fit(X, y, epochs=args.epochs, batch_size=64, verbose=True)
    clf.save(out)
    print(f"[+] Saved → {out}")


def cmd_train_anomaly(args):
    ws = resolve_workspace_dir(args.workspace)
    shield = ShieldCore(workspace_dir=ws, backend=args.backend)
    existing = len(shield.anomaly.buffer)
    print(f"[*] Buffer: {existing} / {shield.anomaly.min_samples} needed")

    if existing < shield.anomaly.min_samples:
        n = 0
        for inc in glob.glob(os.path.join(ws, "incidents", "*.json")):
            try:
                with open(inc) as f: d = json.load(f)
                if d.get('label') == 0:
                    feats = list(d['features'])
                    while len(feats) < FeatureVector.n_features():
                        feats.append(0.0)
                    shield.anomaly.observe(
                        np.array(feats[:FeatureVector.n_features()],
                                 dtype=np.float32), label=0)
                    n += 1
            except Exception:
                continue
        print(f"[*] Loaded {n} labeled-benign incidents")

    if len(shield.anomaly.buffer) < shield.anomaly.min_samples:
        print(f"{Colors.YELLOW}[!] Still not enough — need "
              f"{shield.anomaly.min_samples}, have {len(shield.anomaly.buffer)}"
              f"{Colors.END}")
        return

    print("[*] Training IsolationForest...")
    if shield.train_anomaly_now():
        print(f"{Colors.GREEN}[+] Trained on {len(shield.anomaly.buffer)} samples"
              f"{Colors.END}")
        print(f"[+] train_calls = {shield.anomaly.train_calls}")


def cmd_export(args):
    ws = resolve_workspace_dir(args.workspace)
    inc_dir = os.path.join(ws, "incidents")
    out_csv = args.out or os.path.join(ws, "training", "labeled.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    count = 0
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(FeatureVector.feature_names() + ['label'])
        for fp in glob.glob(os.path.join(inc_dir, "*.json")):
            try:
                with open(fp) as fh: d = json.load(fh)
                if d.get('label') is None: continue
                feats = list(d['features'])
                while len(feats) < FeatureVector.n_features():
                    feats.append(0.0)
                w.writerow(feats[:FeatureVector.n_features()] + [d['label']])
                count += 1
            except Exception:
                continue
    print(f"[+] Exported {count} labeled samples → {out_csv}")


def cmd_label(args):
    ws = resolve_workspace_dir(args.workspace)
    api = ShieldEngineAPI(
        workspace_dir=ws,
        backend=args.backend,
        shadow_mode=getattr(args, 'shadow', False),
        save_intel_on_exit=False,
    )
    cli = AnalystCLI(api)
    cli.bulk_label_report()
    if not args.stats:
        cli.run_interactive(include_observer=False)


def cmd_purge_legacy(args):
    ws = resolve_workspace_dir(args.workspace)
    inc_dir = os.path.join(ws, "incidents")
    banned = _self_process_names() | OBSERVER_PROCESS_NAMES
    removed = 0
    for fp in glob.glob(os.path.join(inc_dir, "*.json")):
        try:
            with open(fp) as f: d = json.load(f)
            proc = d.get('event', {}).get('process_name', '')
            reasons = d.get('decision', {}).get('reasons', []) or []
            poisoned = (
                proc in banned
                or any('Blacklisted process' in r for r in reasons)
            )
            if poisoned:
                if not args.dry_run: os.remove(fp)
                removed += 1
        except Exception:
            continue
    action = "Would remove" if args.dry_run else "Removed"
    print(f"{action} {removed} self/observer incident(s)")


def cmd_watch(args):
    ws = resolve_workspace_dir(args.workspace)
    shield = ShieldCore(workspace_dir=ws,
                        shadow_mode=args.shadow,
                        backend=args.backend)
    root = os.path.expanduser(args.path or "~")

    if not WATCHDOG_OK:
        print(f"{Colors.RED}[x] watchdog not installed. pip install watchdog{Colors.END}")
        return

    handler = ShieldEventHandler(shield, ignore_patterns=[
        r'\.swp$', r'\.swx$', r'\.kate-swp$', r'~$',
        r'(^|/)\.\#', r'\.~lock\.', r'\.goutputstream-',
        r'\.tmp$', r'\.log$', r'\.part$', r'\.crdownload$',
        r'\.git/', r'__pycache__/', r'node_modules/',
        r'\.venv/', r'venv/', r'\.cache/',
        r'\.jpg$', r'\.jpeg$', r'\.png$', r'\.gif$',
        r'\.mp4$', r'\.mov$', r'\.mkv$', r'\.avi$',
        r'\.zip$', r'\.7z$', r'\.rar$', r'\.tar$', r'\.gz$',
        r'/proc/', r'/sys/', r'/dev/', r'/run/',
        r'/tmp/', r'/var/tmp/', r'/var/log/',
        r'AppData[\\/]Local[\\/]Temp',
        r'AppData[\\/]Roaming[\\/]Mozilla',
        r'AppData[\\/]Local[\\/]Google[\\/]Chrome',
        r'AppData[\\/]Roaming[\\/]Microsoft[\\/]Windows',
        r'AppData[\\/]Local[\\/]Microsoft[\\/]Windows',
        r'\.sqlite', r'\.sqlite-wal', r'\.sqlite-journal',
        r'\.etl$', r'\.evtx$', r'\.dmp$', r'\.wer$',
                # source code and installer scripts — dev activity, not threats
        r'\.py$', r'\.pyc$', r'\.pyo$',
        r'\.ps1$', r'\.psm1$', r'\.psd1$',
        r'\.sh$', r'\.bash$', r'\.zsh$',
        r'\.bat$', r'\.cmd$',
        r'\.js$', r'\.mjs$', r'\.ts$', r'\.tsx$', r'\.jsx$',
        r'\.c$', r'\.h$', r'\.cpp$', r'\.hpp$', r'\.go$', r'\.rs$',
        r'\.java$', r'\.kt$', r'\.cs$', r'\.rb$', r'\.php$',
        r'\.md$', r'\.rst$', r'\.markdown$',
        r'\.cfg$', r'\.ini$', r'\.toml$', r'\.yaml$', r'\.yml$',
        r'\.dtd$', r'\.xsd$',
        r'\.txt$',                      # many FPs, is spammy
        r'\.jpg$', r'\.jpeg$', r'\.png$', r'\.gif$', r'\.svg$', r'\.ico$',
        r'\.db$', r'\.db-wal$', r'\.db-shm$',
        r'\.sqlite$', r'\.sqlite3$', r'\.sqlite-wal$', r'\.sqlite-shm$',
    ])
    bridge = _WatchdogBridge(handler)
    observer = Observer()
    observer.schedule(bridge, root, recursive=True)
    observer.start()

    print(f"{Colors.CYAN}[*] Watching: {root}{Colors.END}")
    print(f"{Colors.DIM}    Shadow={args.shadow}  Ctrl+C to stop{Colors.END}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Stopping...{Colors.END}")
    finally:
        observer.stop()
        try: observer.join(timeout=3)
        except Exception: pass
        shield.save_models()
        print(f"{Colors.GREEN}[+] Stopped. Models saved.{Colors.END}")


def cmd_intel(args):
    ws = resolve_workspace_dir(args.workspace)
    intel_path = os.path.join(ws, "models", "intel.txt")
    intel = ThreatIntel.load(intel_path)
    if args.add:
        n = intel.load_file(args.add); intel.save(intel_path)
        print(f"{Colors.GREEN}[+] Added {n} IOCs{Colors.END}")
        return
    if args.url:
        try:
            n = intel.load_url(args.url); intel.save(intel_path)
            print(f"{Colors.GREEN}[+] Fetched {n} IOCs{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[x] {e}{Colors.END}")
        return
    print(f"Hashes: {len(intel.hashes)}  Proc: {len(intel.process_patterns)}  "
          f"Path: {len(intel.path_patterns)}")


def cmd_blacklist(args):
    ws = resolve_workspace_dir(args.workspace)
    api = ShieldEngineAPI(workspace_dir=ws)
    if args.clear:
        n = len(api.shield.blacklist.entries)
        api.shield.blacklist.entries.clear()
        api.shield.blacklist.save()
        print(f"{Colors.GREEN}[+] Cleared {n}{Colors.END}"); return
    if args.remove:
        api.blacklist_remove(args.remove)
        print(f"{Colors.GREEN}[+] Removed{Colors.END}"); return
    if args.add:
        api.blacklist_add(args.add)
        print(f"{Colors.GREEN}[+] Added{Colors.END}"); return
    entries = api.list_blacklist()
    if not entries:
        print(f"{Colors.GREEN}Blacklist empty.{Colors.END}"); return
    for e in entries:
        print(f"  {e['process']:40s} hits={e['hits']}  reasons={e['reasons']}")

def cmd_reports(args):
    
    ws = resolve_workspace_dir(args.workspace)
    reports_root = os.path.join(ws, "ransom", "reports")

    if args.dir:
        print(reports_root)
        return

    if not os.path.isdir(reports_root):
        print(f"{Colors.YELLOW}[!] No reports directory yet.{Colors.END}")
        print(f"    {reports_root}")
        print(f"    Reports are generated automatically on any "
              f"SUSPICIOUS-or-higher detection.")
        return

    # Prune mode
    if args.prune is not None:
        cutoff = time.time() - (args.prune * 86400)
        removed = 0
        for name in os.listdir(reports_root):
            full = os.path.join(reports_root, name)
            if not os.path.isdir(full):
                continue
            try:
                st = os.stat(full)
            except OSError:
                continue
            if st.st_mtime < cutoff:
                try:
                    shutil.rmtree(full)
                    removed += 1
                except Exception as e:
                    print(f"{Colors.YELLOW}[!] Failed to remove {name}: {e}"
                          f"{Colors.END}")
        print(f"{Colors.GREEN}[+] Pruned {removed} report(s) older than "
              f"{args.prune} days{Colors.END}")
        return

    # List mode
    entries = []
    for name in sorted(os.listdir(reports_root), reverse=True):
        full = os.path.join(reports_root, name)
        if not os.path.isdir(full):
            continue
        summary = {}
        jp = os.path.join(full, "report.json")
        if os.path.exists(jp):
            try:
                with open(jp, encoding='utf-8') as f:
                    j = json.load(f)
                summary = {
                    'level': j.get('decision', {}).get('level', '?'),
                    'fused': j.get('decision', {}).get('fused_score', 0.0),
                    'path': j.get('event', {}).get('path', ''),
                    'process': j.get('event', {}).get('process_name', ''),
                    'ts': j.get('event', {}).get('timestamp', 0),
                }
            except Exception:
                pass
        entries.append({'name': name, 'dir': full, 'summary': summary})

    if args.latest:
        entries = entries[:args.latest]

    if not entries:
        print(f"{Colors.YELLOW}[!] No reports found.{Colors.END}")
        return

    if args.open:
        newest = entries[0]
        html_path = os.path.join(newest['dir'], "report.html")
        if os.path.exists(html_path):
            try:
                import webbrowser
                webbrowser.open(f"file:///{html_path}")
                print(f"{Colors.GREEN}[+] Opened {html_path}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[x] Open failed: {e}{Colors.END}")
        else:
            print(f"{Colors.RED}[x] No HTML in {newest['name']}{Colors.END}")
        return

    # Default: print a table
    print(f"\n{Colors.BOLD}Reports{Colors.END}  ({len(entries)} total)")
    print(f"{Colors.DIM}{reports_root}{Colors.END}\n")
    print(f"  {'When':<20} {'Level':<22} {'Fused':>6}  "
          f"{'Process':<20} File")
    print(f"  {'-'*20} {'-'*22} {'-'*6}  {'-'*20} {'-'*40}")

    level_color = {
        'CLEAN': Colors.GREEN,
        'SUSPICIOUS': Colors.YELLOW,
        'HIGH_RISK': Colors.BRIGHT_YELLOW,
        'RANSOMWARE_DETECTED': Colors.BRIGHT_RED,
        'ANOMALY': Colors.BRIGHT_MAGENTA,
    }

    for e in entries:
        s = e['summary']
        ts = (datetime.fromtimestamp(s.get('ts') or 0)
              .strftime('%Y-%m-%d %H:%M:%S')
              if s.get('ts') else e['name'][:15])
        lvl = s.get('level', '?')
        color = level_color.get(lvl, Colors.END)
        proc = (s.get('process') or '?')[:20]
        fname = os.path.basename(s.get('path', '') or e['name'])[:40]
        fused = s.get('fused', 0.0)
        print(f"  {ts:<20} {color}{lvl:<22}{Colors.END} "
              f"{fused:>6.2f}  {proc:<20} {fname}")

def cmd_daemon(args):
    cfg = load_config(args.config) if args.config else load_config(None)
    ws = resolve_workspace_dir(args.workspace or cfg.get("workspace"))
    backend = args.backend or cfg.get("backend", "lr")
    shadow = args.shadow if args.shadow is not None else cfg.get("shadow_mode", False)

    shield = ShieldCore(workspace_dir=ws, shadow_mode=shadow, backend=backend)

    ar = cfg.get("auto_response", {})
    shield.auto_response_policy.kill_process = ar.get("kill_process", True)
    shield.auto_response_policy.rollback_files = ar.get("rollback_files", True)
    shield.auto_response_policy.quarantine_current = ar.get("quarantine_current", True)
    shield.auto_response_policy.blacklist_process = ar.get("blacklist_process", True)
    shield.auto_response_policy.dry_run = ar.get("dry_run", False)
    shield.auto_response_policy.always_respond_to_high_risk = ar.get(
        "always_respond_to_high_risk", False)
    try:
        shield.auto_response_policy.min_level = ThreatLevel[
            ar.get("min_level", "RANSOMWARE_DETECTED")]
    except KeyError:
        pass

    siem_cfg = cfg.get("siem", {})
    if siem_cfg.get("enabled"):
        shield.siem = SiemForwarder(
            targets=siem_cfg.get("targets", []),
            batch_size=siem_cfg.get("batch_size", 50),
            flush_interval=siem_cfg.get("flush_interval", 5.0))
        shield.siem.start()

    pid_path = args.pid or os.path.join(ws, "shield.pid")
    log_path = args.log or os.path.join(ws, "logs", "daemon.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Stale PID check
    if os.path.exists(pid_path):
        try:
            with open(pid_path) as f:
                old_pid = int(f.read().strip())
            alive = False
            try:
                os.kill(old_pid, 0)
                alive = True
            except OSError:
                alive = False
            if alive and old_pid != os.getpid():
                print(f"{Colors.RED}[x] Another instance (pid={old_pid}) is "
                      f"running.{Colors.END}")
                sys.exit(1)
            else:
                os.remove(pid_path)
        except Exception:
            pass

    with open(pid_path, 'w') as f:
        f.write(str(os.getpid()))

    def log(msg):
        line = f"{datetime.now().isoformat()} [pid={os.getpid()}] {msg}"
        try:
            with open(log_path, 'a') as f:
                f.write(line + "\n")
        except Exception:
            pass
        print(Colors.DIM + line + Colors.END)

    def cleanup():
        try:
            if os.path.exists(pid_path):
                with open(pid_path) as f:
                    if f.read().strip() == str(os.getpid()):
                        os.remove(pid_path)
        except Exception:
            pass

    def on_term(signum, frame):
        log(f"SIGTERM/SIGINT ({signum}) — shutting down")
        shield.stop_monitoring()
        if shield.siem:
            try:
                shield.siem.flush(timeout=5)
            except Exception:
                pass
        shield.save_models()
        cleanup()
        log("Daemon stopped cleanly")
        sys.exit(0)

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)

    watch_path = args.path or cfg.get("watch_path")
    observer = None
    if watch_path and WATCHDOG_OK:
        handler = ShieldEventHandler(shield, ignore_patterns=[
            r'\.swp$', r'\.swx$', r'\.kate-swp$', r'~$',
            r'(^|/)\.\#', r'\.~lock\.', r'\.goutputstream-',
            r'\.tmp$', r'\.log$', r'\.part$', r'\.crdownload$',
            r'\.git/', r'__pycache__/', r'node_modules/',
            r'\.venv/', r'venv/', r'\.cache/',
            r'/proc/', r'/sys/', r'/dev/', r'/run/',
        ])
        bridge = _WatchdogBridge(handler)
        observer = Observer()
        observer.schedule(bridge, os.path.expanduser(watch_path), recursive=True)
        observer.start()
        log(f"Watching: {watch_path}")

    shield.start_monitoring()
    log(f"Shield daemon started (pid={os.getpid()})")
    log(f"Workspace: {ws}")
    log(f"Backend: {backend}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        on_term(2, None)
    finally:
        if observer:
            observer.stop()
            try:
                observer.join(timeout=3)
            except Exception:
                pass
        try:
            shield.stop_monitoring()
            shield.save_models()
            if shield.siem:
                shield.siem.flush(timeout=3)
        except Exception:
            pass
        cleanup()


# ============================================================
# Dashboard: engine + live watcher + Flask UI, in one process
# ============================================================
def cmd_dashboard(args):
    """
    Start the engine, attach one watchdog observer per watch root, and
    serve the real-time monitoring dashboard.

    By default this fans out across the whole system (user profiles,
    ProgramData, temp dirs, additional drives). Pass --watch-path PATH
    to scope it down to a single directory, or --watch-path all for
    an explicit system-wide run.

    Gevent monkey-patching is deferred until *after* all observers
    start, so watchdog's OS threads use native queue primitives.
    """
    if not FLASK_OK:
        print(f"{Colors.RED}[x] Dashboard needs Flask + Flask-SocketIO."
              f"{Colors.END}")
        print(f"    Install: pip install flask flask-socketio")
        print(f"    Falling back to CLI shell.\n")
        return run_cli_repl(args)

    if not WATCHDOG_OK:
        print(f"{Colors.YELLOW}[!] watchdog not installed — dashboard will "
              f"run but show no live events.{Colors.END}")
        print(f"    Install: pip install watchdog")

    ws = resolve_workspace_dir(args.workspace)
    api = ShieldEngineAPI(
        workspace_dir=ws,
        backend=args.backend,
        shadow_mode=getattr(args, 'shadow', False),
    )
    api.start()
    print(f"{Colors.GREEN}[+] Engine started — workspace: {ws}{Colors.END}")

    # ------------------------------------------------------------------
    # Fan-out: one observer per watch root. Must be started BEFORE the
    # gevent monkey-patch so watchdog uses native queue primitives.
    # ------------------------------------------------------------------
    observers: List = []
    watch_arg = getattr(args, 'watch_path', None)
    roots = resolve_watch_roots(watch_arg)

    if not WATCHDOG_OK:
        pass  # already warned
    elif not roots:
        print(f"{Colors.YELLOW}[!] No watch roots resolved — no live events"
              f"{Colors.END}")
    else:
        ignore_patterns = [
            # editor / temp / lock files
            r'\.swp$', r'\.swx$', r'\.kate-swp$', r'~$',
            r'(^|/)\.\#', r'\.~lock\.', r'\.goutputstream-',
            r'\.tmp$', r'\.log$', r'\.part$', r'\.crdownload$',
            r'\.bak$', r'\.crdownload$',
            # Windows shell housekeeping
            r'desktop\.ini$',
            r'thumbs\.db$',
            r'\.lnk$',                  # shortcut files
            r'\.tmp$', r'\.partial$',
            r'NTUSER\.DAT',
            r'UsrClass\.dat',
            r'IconCache',
            r'\.db-shm$', r'\.db-wal$',
            r'AppData[\\/]Local[\\/]IconCache',
            r'AppData[\\/]Roaming[\\/]Microsoft[\\/]Windows[\\/]Recent',
            r'AppData[\\/]Local[\\/]Microsoft[\\/]Windows[\\/]Explorer',
            # Office lock files
            r'\.~lock\.',
            r'\.~.*\.tmp$',
            # Sentinel/marker files
            r'\.gitkeep$',
            r'\.nomedia$',
            r'\.DS_Store$',
            # dev / build artifact directories
            r'\.git/', r'__pycache__/', r'node_modules/',
            r'\.venv/', r'venv/', r'\.cache/',
            r'\.idea/', r'\.vscode/', r'\.vs/',
            r'\.gradle/', r'\.m2/', r'\.cargo/', r'\.nuget/',
            r'[\\/]target[\\/]', r'[\\/]build[\\/]', r'[\\/]dist[\\/]',
            # OS pseudo filesystems
            r'/proc/', r'/sys/', r'/dev/', r'/run/',
            # browser caches — massive write churn
            r'AppData[\\/]Local[\\/]Google[\\/]Chrome',
            r'AppData[\\/]Local[\\/]Mozilla',
            r'AppData[\\/]Local[\\/]Microsoft[\\/]Edge',
            r'AppData[\\/]Local[\\/]Packages',
            r'AppData[\\/]Roaming[\\/]Mozilla',
            r'AppData[\\/]Roaming[\\/]Code',
            r'AppData[\\/]Local[\\/]Microsoft[\\/]Windows[\\/]INetCache',
            r'AppData[\\/]Local[\\/]Temp',
            # cloud sync
            r'OneDrive', r'Dropbox', r'Google[\\/]Drive',
            # package managers
            r'AppData[\\/]Local[\\/]pip',
            r'AppData[\\/]Roaming[\\/]npm-cache',
            r'AppData[\\/]Local[\\/]Yarn',
            # windows update + defender
            r'SoftwareDistribution',
            r'Windows Defender',
            # sysinternals-style logs
            r'\.etl$', r'\.evtx$', r'\.dmp$', r'\.wer$',
            # sqlite WAL churn
            r'\.sqlite', r'\.sqlite-wal', r'\.sqlite-journal',
        ]

        print(f"{Colors.CYAN}[*] Watching {len(roots)} root(s):"
              f"{Colors.END}")
        for r in roots:
            print(f"      {r}")

        for root in roots:
            try:
                handler = ShieldEventHandler(api.shield,
                                             ignore_patterns=ignore_patterns)
                bridge = _WatchdogBridge(handler)
                obs = Observer()
                obs.schedule(bridge, root, recursive=True)
                obs.start()
                observers.append(obs)
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Failed to watch {root}: {e}"
                      f"{Colors.END}")

        print(f"{Colors.GREEN}[+] Live monitoring active across "
              f"{len(observers)} root(s){Colors.END}")

    # ------------------------------------------------------------------
    # Deferred gevent monkey-patch — AFTER all observers are running.
    # ------------------------------------------------------------------
    # gevent disabled — threading mode is enough for a local single-user
    # dashboard and avoids the gevent/engineio disconnect race conditions.

    # ------------------------------------------------------------------
    # Build and run the Flask-SocketIO server.
    # ------------------------------------------------------------------
    ui = DashboardUI(
        api=api,
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
    )

    # Silence the harmless LoopExit from concurrent.futures worker threads
    # that try to wake up after the gevent hub has already shut down.
    import logging as _lg
    _lg.getLogger("concurrent.futures").setLevel(_lg.CRITICAL)
    _lg.getLogger("gevent").setLevel(_lg.CRITICAL)
    # Quiet noisy gevent / engineio / socketio stack traces that happen
    # when the browser disconnects mid-handshake. They're harmless.
    _lg.getLogger("gevent").setLevel(_lg.CRITICAL)
    _lg.getLogger("engineio").setLevel(_lg.CRITICAL)
    _lg.getLogger("socketio").setLevel(_lg.CRITICAL)
    _lg.getLogger("engineio.server").setLevel(_lg.CRITICAL)
    _lg.getLogger("socketio.server").setLevel(_lg.CRITICAL)

    try:
        ui.run()
    except KeyboardInterrupt:
        pass

    finally:
        try:
            ui.stop()
        except Exception:
            pass
        for obs in observers:
            try:
                obs.stop()
                obs.join(timeout=3)
            except Exception:
                pass
        api.shutdown()
        print(f"{Colors.GREEN}[+] Stopped cleanly.{Colors.END}")


def cmd_config_init(args):
    out = os.path.expanduser(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    print(f"{Colors.GREEN}[+] Wrote {out}{Colors.END}")


def cmd_siem(args):
    cfg = load_config(args.config) if args.config else load_config(None)
    siem_cfg = cfg.get("siem", {})
    if not siem_cfg.get("enabled"):
        print(f"{Colors.YELLOW}[!] SIEM not enabled in config.{Colors.END}")
        return
    forwarder = SiemForwarder(targets=siem_cfg.get("targets", []))
    if args.test:
        print(f"\n{Colors.BOLD}Testing {len(forwarder.targets)} target(s){Colors.END}")
        for name, ok, msg in forwarder.test_targets():
            color = Colors.GREEN if ok else Colors.RED
            print(f"  {color}{'OK ' if ok else 'FAIL'}{Colors.END} {name:12s} {msg}")
        return
    print(f"Targets: {[t.name for t in forwarder.targets]}")


# ============================================================
# CLI REPL MODE
# ============================================================
def run_cli_repl(args):
    """Interactive analyst shell backed by the engine."""
    ws = resolve_workspace_dir(args.workspace)
    api = ShieldEngineAPI(workspace_dir=ws, backend=args.backend)
    api.start()

    # Live event stream to terminal
    def on_event(event_dict, decision_dict):
        level = decision_dict.get("level", "CLEAN")
        color = {
            "CLEAN": Colors.GREEN,
            "SUSPICIOUS": Colors.YELLOW,
            "HIGH_RISK": Colors.BRIGHT_YELLOW,
            "RANSOMWARE_DETECTED": Colors.BRIGHT_RED,
            "ANOMALY": Colors.BRIGHT_MAGENTA,
        }.get(level, Colors.END)
        path = os.path.basename(event_dict.get("path", ""))[:40]
        proc = event_dict.get("process_name", "?")[:20]
        print(f"{color}[{level:22s}]{Colors.END} {path:40s} {proc}")

    api.register_event_callback(on_event)

    os.system('cls' if os.name == 'nt' else 'clear')

    # Banner
    ctype("╔══════════════════════════════════════════════════════╗",
          color=Colors.CYAN, delay=0.001)
    ctype("║     DSTERMINAL  v6.0  —  SHIELD  COMMAND  SHELL       ║",
          color=Colors.CYAN, delay=0.003)
    ctype("╚══════════════════════════════════════════════════════╝",
          color=Colors.CYAN, delay=0.001)
    print()

    # Status line
    ctype(f"[ OK ]  Engine running  ·  {os.path.basename(ws)}",
          color=Colors.GREEN, delay=0.008)
    print()
    time.sleep(0.15)

    # Command reference in a box
    print_boxed(
        "COMMAND REFERENCE",
        [
            f"{Colors.GREEN}status{Colors.END}           - engine status",
            f"{Colors.GREEN}incidents [N]{Colors.END}    - list N most recent incidents",
            f"{Colors.GREEN}label <f> <0|1>{Colors.END}  - label incident (0=benign, 1=malicious)",
            f"{Colors.GREEN}quarantine <p>{Colors.END}   - quarantine file at path",
            f"{Colors.GREEN}restore <p>{Colors.END}      - restore file from quarantine",
            f"{Colors.GREEN}blacklist{Colors.END}        - show process blacklist",
            f"{Colors.GREEN}reports [N]{Colors.END}      - list N most recent reports",
            f"{Colors.GREEN}reports --open{Colors.END}   - open newest report in browser",
            f"{Colors.GREEN}help{Colors.END}             - show this list",
            f"{Colors.GREEN}quit{Colors.END}             - exit shell",
        ],
        color=Colors.CYAN,
    )
    print()
    time.sleep(0.1)

    try:
        while True:
            try:
                pad = " " * 4
                line = input(f"{Colors.CYAN}ShieldCore>{Colors.END} "
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print(); break
            if not line: continue
            parts = line.split(maxsplit=1)
            cmd = parts[0].lower()
            rest = parts[1] if len(parts) > 1 else ""

            if cmd in ("quit", "exit", "q"):
                break
            elif cmd == "status":
                st = api.get_status()

                # Threat level with color
                tl = st.get('threat_level', 'CLEAN')
                tl_color = {
                    'CLEAN': Colors.GREEN,
                    'SUSPICIOUS': Colors.YELLOW,
                    'HIGH_RISK': Colors.BRIGHT_YELLOW,
                    'RANSOMWARE_DETECTED': Colors.BRIGHT_RED,
                    'ANOMALY': Colors.BRIGHT_MAGENTA,
                }.get(tl, Colors.GREEN)

                def badge(ok):  # quick yes/no badge
                    return (f"{Colors.GREEN}yes{Colors.END}" if ok
                            else f"{Colors.YELLOW}no{Colors.END}")

                lines = [
                    f"threat_level      : {tl_color}{tl}{Colors.END}",
                    f"events_monitored  : {st.get('events_monitored', 0):,}",
                    f"honeypots         : {st.get('honeypots', 0)}",
                    f"ml_updates        : {st.get('ml_updates', 0):,}",
                    f"ml_trusted        : {badge(st.get('ml_trusted', False))}",
                    f"if_samples        : {st.get('if_samples', 0):,}",
                    f"if_ready          : {badge(st.get('if_ready', False))}",
                    f"if_train_calls    : {st.get('if_train_calls', 0)}",
                    f"blacklist_size    : {st.get('blacklist_size', 0)}",
                    f"incidents_total   : {st.get('incidents_total', 0)}",
                    f"quarantine_total  : {st.get('quarantine_total', 0)}",
                    f"sessions_tracked  : {st.get('sessions_tracked', 0)}",
                    f"ioc_hashes        : {st.get('ioc_hashes', 0)}",
                    f"siem_enabled      : {badge(st.get('siem_enabled', False))}",
                    f"shadow_mode       : {badge(st.get('shadow_mode', False))}",
                ]
                print_boxed("ENGINE STATUS", lines, color=tl_color)
                print()
            elif cmd == "incidents":
                n = int(rest) if rest.isdigit() else 20
                incidents = api.list_incidents(limit=n)
                if not incidents:
                    cprint("  No incidents recorded yet.", color=Colors.DIM)
                    print()
                else:
                    lines = []
                    for inc in incidents:
                        ev = inc.get('event', {})
                        dec = inc.get('decision', {})
                        lvl = dec.get('level', '?')
                        lbl = {None: '?', 0: 'B', 1: 'M'}.get(
                            inc.get('label'), '?')
                        lvl_color = {
                            'CLEAN': Colors.GREEN,
                            'SUSPICIOUS': Colors.YELLOW,
                            'HIGH_RISK': Colors.BRIGHT_YELLOW,
                            'RANSOMWARE_DETECTED': Colors.BRIGHT_RED,
                            'ANOMALY': Colors.BRIGHT_MAGENTA,
                        }.get(lvl, Colors.DIM)
                        fname = os.path.basename(
                            ev.get('path', '')).ljust(30)[:30]
                        proc = (ev.get('process_name', '?'))[:15]
                        ts = datetime.fromtimestamp(
                            ev.get('timestamp', 0)
                        ).strftime('%H:%M:%S') if ev.get('timestamp') else '--:--:--'
                        lines.append(
                            f"[{lbl}] {ts}  "
                            f"{lvl_color}{lvl:<22}{Colors.END}  "
                            f"{proc:<15}  {fname}"
                        )
                    print_boxed(f"INCIDENTS  ({len(incidents)} shown)",
                                lines, color=Colors.CYAN)
                    print()
            
            elif cmd == "label":
                try:
                    fname, lab = rest.rsplit(maxsplit=1)
                    if lab in ('0','1'):
                        ok = api.label_incident(fname, int(lab))
                        print(f"  {'[OK]' if ok else '[FAIL]'}")
                    else:
                        print("  label must be 0 or 1")
                except ValueError:
                    print("  usage: label <filename> <0|1>")
            elif cmd == "quarantine":
                if rest:
                    ok = api.quarantine_file(rest)
                    print(f"  {'[OK]' if ok else '[FAIL]'}")

            elif cmd == "restore":
                if not rest:
                    cprint("  usage: restore <quarantine_path>", color=Colors.YELLOW)
                    print()
                else:
                    ok = api.restore_from_quarantine(rest)
                    if ok:
                        cprint(f"  [ OK ]  Restored: {rest}", color=Colors.GREEN)
                    else:
                        cprint(f"  [FAIL]  Could not restore: {rest}", color=Colors.RED)
                    print()

            elif cmd == "blacklist":
                entries = api.list_blacklist()
                if not entries:
                    cprint("  Blacklist is empty.", color=Colors.DIM)
                    print()
                else:
                    lines = []
                    for e in entries:
                        proc = e['process'][:30].ljust(30)
                        hits = f"hits={e['hits']}"
                        reasons = ", ".join(e.get('reasons', [])[:2])
                        lines.append(
                            f"{Colors.BRIGHT_RED}{proc}{Colors.END}  {hits}  {reasons}"
                        )
                    print_boxed(f"PROCESS BLACKLIST  ({len(entries)})",
                                lines, color=Colors.BRIGHT_RED)
                    print()

            elif cmd == "quarantine":
                if not rest:
                    cprint("  usage: quarantine <file_path>", color=Colors.YELLOW)
                    print()
                else:
                    ok = api.quarantine_file(rest)
                    if ok:
                        cprint(f"  [ OK ]  Quarantined: {rest}", color=Colors.GREEN)
                    else:
                        cprint(f"  [FAIL]  Could not quarantine: {rest}",
                            color=Colors.RED)
                    print()

            elif cmd == "reports":
                reports_root = os.path.join(ws, "ransom", "reports")
                if not os.path.isdir(reports_root):
                    cprint("  No reports yet.", color=Colors.DIM)
                    cprint("  Reports are generated on any SUSPICIOUS-or-higher detection.",
                        color=Colors.DIM)
                    print()
                else:
                    names = sorted(os.listdir(reports_root), reverse=True)
                    n = int(rest) if rest and rest.isdigit() else 10
                    rows = []
                    for name in names:
                        if len(rows) >= n:
                            break
                        jp = os.path.join(reports_root, name, "report.json")
                        if not os.path.exists(jp):
                            continue
                        try:
                            with open(jp, encoding='utf-8') as f:
                                j = json.load(f)
                            lvl = j.get('decision', {}).get('level', '?')
                            fused = j.get('decision', {}).get('fused_score', 0)
                            path = j.get('event', {}).get('path', '')
                            lvl_color = {
                                'CLEAN': Colors.GREEN,
                                'SUSPICIOUS': Colors.YELLOW,
                                'HIGH_RISK': Colors.BRIGHT_YELLOW,
                                'RANSOMWARE_DETECTED': Colors.BRIGHT_RED,
                                'ANOMALY': Colors.BRIGHT_MAGENTA,
                            }.get(lvl, Colors.DIM)
                            rows.append(
                                f"{lvl_color}{lvl:<22}{Colors.END} "
                                f"{fused:>5.2f}  "
                                f"{os.path.basename(path)[:35]:<35}"
                            )
                        except Exception:
                            continue
                    if not rows:
                        cprint("  No reports found.", color=Colors.DIM)
                        print()
                    else:
                        print_boxed(f"DETECTION REPORTS  ({len(rows)})",
                                    rows, color=Colors.CYAN)
                        print()
                        
            elif cmd in ("help", "?", "h"):
                os.system('cls' if os.name == 'nt' else 'clear')
                print_boxed(
                    "COMMAND REFERENCE",
                    [
                        f"{Colors.GREEN}status{Colors.END}           - engine status",
                        f"{Colors.GREEN}incidents [N]{Colors.END}    - list N most recent incidents",
                        f"{Colors.GREEN}label <f> <0|1>{Colors.END}  - label incident",
                        f"{Colors.GREEN}quarantine <p>{Colors.END}   - quarantine file at path",
                        f"{Colors.GREEN}restore <p>{Colors.END}      - restore file from quarantine",
                        f"{Colors.GREEN}blacklist{Colors.END}        - show process blacklist",
                        f"{Colors.GREEN}reports [N]{Colors.END}      - list N most recent reports",
                        f"{Colors.GREEN}reports --open{Colors.END}   - open newest report in browser",
                        f"{Colors.GREEN}help{Colors.END}             - show this list",
                        f"{Colors.GREEN}quit{Colors.END}             - exit shell",
                    ],
                    color=Colors.CYAN,
                )
                print()

            else:
                print(f"  unknown command: {cmd}")
    finally:
        api.shutdown()
        print()
        ctype("[ OK ]  Shield engine stopped cleanly.",
              color=Colors.GREEN, delay=0.01)
        print()


def run_ui(args):
    """
    No-subcommand entry point. Delegates to cmd_dashboard so there's a
    single source of truth for the UI startup path.
    """
    if not hasattr(args, 'watch_path'):
        args.watch_path = None
    return cmd_dashboard(args)

# ============================================================
# MAIN
# ============================================================
def main():
    p = argparse.ArgumentParser(
        prog="dsterminal",
        description="DSTerminal v6.0 — Unified Shield_Core Platform")

    p.add_argument("--workspace", "-w", default=None)
    p.add_argument("--backend", choices=['lr', 'torch'], default='lr')
    p.add_argument("--deploy-honeypots", action="store_true", default=None)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--no-browser", action="store_true")
    p.add_argument("--shadow", action="store_true")
    p.add_argument("--cli", action="store_true",
                   help="Force interactive CLI mode instead of UI")

    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("demo", help="Run detection demo")
    sp.add_argument("--shadow", action="store_true")
    sp.set_defaults(func=cmd_demo)

    sp = sub.add_parser("make-dataset", help="Generate synthetic training data")
    sp.add_argument("--out", default=None)
    sp.add_argument("--n-benign", type=int, default=4000)
    sp.add_argument("--n-malicious", type=int, default=4000)
    sp.set_defaults(func=cmd_make_dataset)

    sp = sub.add_parser("accuracy", help="Evaluate model on CSV")
    sp.add_argument("--csv", default=None)
    sp.add_argument("--test-size", type=float, default=0.2)
    sp.add_argument("--threshold", type=float, default=0.5)
    sp.add_argument("--epochs", type=int, default=100)
    sp.add_argument("--seed", type=int, default=42)
    sp.set_defaults(func=cmd_accuracy)

    sp = sub.add_parser("cv", help="K-fold cross-validation")
    sp.add_argument("--csv", default=None)
    sp.add_argument("--folds", type=int, default=5)
    sp.add_argument("--epochs", type=int, default=60)
    sp.add_argument("--seed", type=int, default=42)
    sp.set_defaults(func=cmd_cv)

    sp = sub.add_parser("train", help="Train from CSV")
    sp.add_argument("--csv", required=True)
    sp.add_argument("--epochs", type=int, default=100)
    sp.set_defaults(func=cmd_train)

    sp = sub.add_parser("train-anomaly", help="Train IsolationForest")
    sp.set_defaults(func=cmd_train_anomaly)

    sp = sub.add_parser("reports", help="Manage and view detection reports")
    sp.add_argument("--out", default=None)
    sp.add_argument("--latest", type=int, default=20,
                    help="Show only the N most recent (default: 20)")
    sp.add_argument("--open", action="store_true",
                    help="Open newest report HTML in the browser")
    sp.add_argument("--dir", action="store_true",
                    help="Print reports directory path and exit")
    sp.add_argument("--prune", type=int, default=None,
                    metavar="DAYS",
                    help="Delete reports older than N days")
    sp.set_defaults(func=cmd_reports)

    sp = sub.add_parser("label", help="Interactively label incidents")
    sp.add_argument("--stats", action="store_true")
    sp.set_defaults(func=cmd_label)

    sp = sub.add_parser("purge-legacy",
                        help="Remove self/observer incidents")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_purge_legacy)

    sp = sub.add_parser("dashboard",
                        help="Launch the real-time monitoring dashboard")
    sp.add_argument("--watch-path", default=None,
                    help="Monitoring scope. Default: 'user' (Desktop, "
                         "Documents, Downloads, Pictures, Videos, Music, "
                         "OneDrive, Dropbox). Pass 'all' for system-wide "
                         "(user profiles, ProgramData, temp dirs, "
                         "additional drives). Pass a specific directory "
                         "path to scope to that directory only.")
    sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=5000)
    sp.add_argument("--no-browser", action="store_true")
    sp.add_argument("--shadow", action="store_true")
    sp.set_defaults(func=cmd_dashboard)

    sp = sub.add_parser("intel", help="Manage IOC feed")
    sp.add_argument("--add", default=None)
    sp.add_argument("--url", default=None)
    sp.set_defaults(func=cmd_intel)

    sp = sub.add_parser("blacklist", help="Manage process blacklist")
    sp.add_argument("--add", default=None)
    sp.add_argument("--remove", default=None)
    sp.add_argument("--clear", action="store_true")
    sp.set_defaults(func=cmd_blacklist)

    sp = sub.add_parser("daemon", help="Run as background daemon")
    sp.add_argument("--config", default=None)
    sp.add_argument("--pid", default=None)
    sp.add_argument("--log", default=None)
    sp.add_argument("--path", default=None)
    sp.add_argument("--shadow", dest="shadow", action="store_true", default=None)
    sp.set_defaults(func=cmd_daemon)

    sp = sub.add_parser("siem", help="Manage SIEM forwarding")
    sp.add_argument("--config", default=None)
    sp.add_argument("--test", action="store_true")
    sp.set_defaults(func=cmd_siem)

    sp = sub.add_parser("config-init", help="Write starter config")
    sp.add_argument("--out", default="~/.shield_core.json")
    sp.set_defaults(func=cmd_config_init)

    args = p.parse_args()

    # If no subcommand specified:
    #   --cli flag      → REPL
    #   default         → dashboard UI
    if not args.cmd:
        if args.cli or not FLASK_OK:
            return run_cli_repl(args)
        return run_ui(args)

    # If a subcommand IS specified, dispatch to it
    args.func(args)


if __name__ == "__main__":
    main()
