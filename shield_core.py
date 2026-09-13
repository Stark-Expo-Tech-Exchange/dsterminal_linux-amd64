#!python
# ============================================================
# DSTerminal Shield Core v5.6.2 - HARDENED + CLEAN EDITION
# ============================================================
"""
Shield_Core: Hybrid Rule-Based + Trainable ML Ransomware Defense
with Auto-Escalation, Rollback, Daemon Mode, and SIEM Forwarding.

v5.6.1 fixes vs v5.6:
  - ProcessBlacklist purges self/observer entries on load (poison cleanup)
  - AutoResponse never blacklists self/observer processes
  - _respond_to_threat uses safe `or {}` access for None fields
    (fixes: 'NoneType' object has no attribute 'get')
  - analyze_event skips blacklist escalation for self/observer
  - _respond_to_threat silently returns early for self/observer
    (no more spam: 🚨 AUTO-RESPONSE + 🛡 Refusing)
  - _is_self_event() helper for consistent self-detection

v5.6 hardening (retained):
  - AutoResponse refuses to act on self/observer processes
  - ProcessKiller refuses to kill init, self, parent
  - ProcessCorrelator skips observer-originated events
  - Session elevations are advisory, not action-triggering
  - ML confidence gate: downweighted until n_updates >= 50
  - DaemonRuntime detects & clears stale PID files
  - Better CLI hints (siem disabled, undertrained classifier)

Optional deps (all graceful):
  pip install watchdog flask torch requests psutil
"""
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
import argparse
from collections import deque, defaultdict
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Set, Any, Tuple

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
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    except Exception:
        pass

# ============================================================
# OPTIONAL IMPORTS
# ============================================================
try:
    import numpy as np
except ImportError:
    print("[!] numpy not installed - run: pip install numpy"); sys.exit(1)

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
    from colorama import init, Fore, Back, Style
    init(autoreset=True, convert=True, strip=False)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

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
# TERMINAL UTILS
# ============================================================
def get_terminal_width() -> int:
    try:
        w = shutil.get_terminal_size().columns
        return min(max(w, 80), 120)
    except Exception:
        return 80

def center_text(text: str, width: int = None) -> str:
    if width is None:
        width = get_terminal_width()
    pad = max(0, (width - len(Colors.strip(text))) // 2)
    return ' ' * pad + text

def print_centered(text: str, color: str = "", width: int = None):
    if width is None:
        width = get_terminal_width()
    print(center_text(f"{color}{text}{Colors.END}" if color else text, width))

def _hostname() -> str:
    try:
        return os.uname().nodename
    except Exception:
        return os.environ.get("COMPUTERNAME") or "unknown"

# v5.6.1: hoisted so ProcessBlacklist.load can purge these names
OBSERVER_PROCESS_NAMES = {"watchdog", "watcher"}

def _self_process_names() -> Set[str]:
    """Names we must never auto-respond against or blacklist."""
    names = set(OBSERVER_PROCESS_NAMES) | {"shield_core", "shield_core.py"}
    try:
        names.add(os.path.basename(sys.argv[0]))
    except Exception:
        pass
    names.add(os.path.basename(sys.executable))
    return {n for n in names if n}

def _is_self_event(event: "FileEvent") -> bool:
    """v5.6.1: True if this event came from us or our observer."""
    if event.pid == os.getpid():
        return True
    if event.process_name in _self_process_names():
        return True
    return False

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
        print(" " * pad + f"{border}│{Colors.END}{' ' * tp}{Colors.YELLOW}{Colors.BOLD}"
              f"{title_t}{Colors.END}{' ' * (bw - cl(title_t) - tp)}{border}│{Colors.END}")
        print(" " * pad + f"{border}├{'─' * bw}┤{Colors.END}")
        for line in lines[:20]:
            if cl(line) > bw - 2:
                line = line[:bw - 5] + "..."
            p = max(0, bw - cl(line) - 2)
            print(" " * pad + f"{border}│{Colors.END} {line}{' ' * p} {border}│{Colors.END}")
        print(" " * pad + f"{border}└{'─' * bw}┘{Colors.END}")

# ============================================================
# ENUMS & DATACLASSES
# ============================================================
class ThreatLevel(Enum):
    CLEAN = 0
    SUSPICIOUS = 1
    HIGH_RISK = 2
    RANSOMWARE_DETECTED = 3
    ANOMALY = 4

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
# FEATURE VECTOR
# ============================================================
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

    def to_array(self) -> np.ndarray:
        return np.array([
            self.file_entropy, self.file_size_delta, self.extension_changed,
            self.is_honeypot, self.is_system_path, self.is_user_doc,
            self.write_ratio, self.ops_per_sec, self.unique_files_touched,
            self.unique_extensions, self.avg_file_size, self.suspicious_name_score,
            self.external_conn_count, self.bytes_sent_ratio,
            self.hour_of_day, self.is_off_hours, self.burst_score,
        ], dtype=np.float32)

    @staticmethod
    def feature_names() -> List[str]:
        return [
            "file_entropy", "file_size_delta", "extension_changed",
            "is_honeypot", "is_system_path", "is_user_doc", "write_ratio",
            "ops_per_sec", "unique_files_touched", "unique_extensions",
            "avg_file_size", "suspicious_name_score",
            "external_conn_count", "bytes_sent_ratio",
            "hour_of_day", "is_off_hours", "burst_score",
        ]


class FeatureExtractor:
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

    def __init__(self, honeypot_paths: Optional[Set[str]] = None):
        self.honeypot_paths = honeypot_paths or set()
        self.file_history: Dict[str, float] = {}

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

    def extract(self, event: FileEvent, process_stats: Dict[str, Any]) -> FeatureVector:
        entropy = 0.0; size_delta = 0.0
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
            external_conn_count=0,
            bytes_sent_ratio=0.0,
            hour_of_day=hour,
            is_off_hours=int(hour < 8 or hour > 18),
            burst_score=process_stats.get('burst_score', 1.0),
        )

# ============================================================
# LAYER 2a: LOGISTIC REGRESSION
# ============================================================
class ThreatClassifier:
    def __init__(self, n_features: int = 17, l2: float = 1e-3, lr: float = 0.05):
        self.n_features = n_features
        self.l2 = l2; self.lr = lr
        rng = np.random.default_rng(42)
        self.w = rng.normal(0, 0.01, size=n_features).astype(np.float32)
        self.b = np.float32(0.0)
        self.n_updates = 0
        self.mean = np.zeros(n_features, dtype=np.float32)
        self.var = np.ones(n_features, dtype=np.float32)

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
            if verbose: print("  [!] No training samples — skipping fit")
            return
        rng = np.random.default_rng(0)
        for ep in range(epochs):
            idx = rng.permutation(n); loss = 0.0
            for i in range(0, n, batch_size):
                for j in idx[i:i+batch_size]:
                    xj = self._norm(X[j], update=True)
                    p = self._sigmoid(float(np.dot(self.w, xj) + self.b))
                    loss += -(y[j]*np.log(p+1e-9) + (1-y[j])*np.log(1-p+1e-9))
                    g = p - y[j]
                    self.w -= self.lr * (g * xj + self.l2 * self.w)
                    self.b -= self.lr * g
            if verbose and ep % 10 == 0:
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
        with open(path, 'rb') as f: d = pickle.load(f)
        c = cls(n_features=d['n_features'])
        c.w = d['w']; c.b = d['b']; c.mean = d['mean']
        c.var = d['var']; c.n_updates = d['n_updates']
        return c

# ============================================================
# LAYER 2b: PYTORCH MLP (same interface)
# ============================================================
if TORCH_OK:
    class _MLPNet(nn.Module):
        def __init__(self, n_features: int = 17, hidden: int = 32):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(n_features, hidden), nn.ReLU(), nn.Dropout(0.1),
                nn.Linear(hidden, hidden // 2), nn.ReLU(),
                nn.Linear(hidden // 2, 1),
            )
        def forward(self, x):
            return self.net(x).squeeze(-1)


class NeuralThreatClassifier:
    def __init__(self, n_features: int = 17, lr: float = 1e-3,
                 weight_decay: float = 1e-4, hidden: int = 32):
        if not TORCH_OK:
            raise ImportError("PyTorch not installed (pip install torch)")
        self.n_features = n_features; self.lr = lr
        self.weight_decay = weight_decay; self.hidden = hidden
        self.n_updates = 0
        self.mean = np.zeros(n_features, dtype=np.float32)
        self.var = np.ones(n_features, dtype=np.float32)
        self.model = _MLPNet(n_features, hidden)
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
        self.opt.zero_grad(); loss.backward(); self.opt.step()

    def fit(self, X, y, epochs=50, batch_size=64, verbose=False):
        if len(X) == 0:
            if verbose: print("  [!] No samples")
            return
        for xj in X: self._norm(xj, update=True)
        Xn = np.stack([self._norm(x, update=False) for x in X])
        Xt = torch.from_numpy(Xn.astype(np.float32))
        yt = torch.from_numpy(y.astype(np.float32))
        n = len(Xt); rng = np.random.default_rng(0)
        self.model.train()
        for ep in range(epochs):
            idx = rng.permutation(n); total = 0.0
            for i in range(0, n, batch_size):
                b = idx[i:i+batch_size]
                logits = self.model(Xt[b])
                loss = F.binary_cross_entropy_with_logits(logits, yt[b])
                self.opt.zero_grad(); loss.backward(); self.opt.step()
                total += loss.item() * len(b)
            if verbose and ep % 10 == 0:
                print(f"  epoch {ep:3d}  loss={total/n:.4f}")

    def explain(self, x, top_k=5):
        xn = self._norm(x, update=False)
        self.model.eval()
        t = torch.from_numpy(xn.astype(np.float32)).unsqueeze(0).requires_grad_(True)
        logit = self.model(t); logit.backward()
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
        obj.mean = d['mean']; obj.var = d['var']; obj.n_updates = d['n_updates']
        return obj


def make_classifier(backend: str, n_features: int = 17, lr: float = 0.05):
    if backend == 'torch':
        if TORCH_OK:
            return NeuralThreatClassifier(n_features=n_features, lr=1e-3)
        print(f"{Colors.YELLOW}[!] torch not installed; using LR backend{Colors.END}")
    return ThreatClassifier(n_features=n_features, lr=lr)

# ============================================================
# LAYER 3: ISOLATION FOREST (trust-ramped)
# ============================================================
class AnomalyDetector:
    def __init__(self, n_features: int = 17, contamination: float = 0.02,
                 min_samples: int = 500, min_train_calls: int = 3):
        self.n_features = n_features
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
        trust = min(1.0, self.train_calls / float(self.min_train_calls))
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
            }, f)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f: d = pickle.load(f)
        obj = cls(
            contamination=d.get('contamination', 0.02),
            min_samples=d.get('min_samples', 500),
            min_train_calls=d.get('min_train_calls', 3),
        )
        obj.model = d.get('model')
        obj.buffer = d.get('buffer', [])
        obj.train_calls = d.get('train_calls', 0)
        return obj

# ============================================================
# LAYER 4: HYBRID DECISION ENGINE (ML confidence gate)
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
    MIN_ML_UPDATES = 50  # ML trust threshold

    def __init__(self, classifier, anomaly,
                 ml_weight=0.5, rule_weight=0.3, anomaly_weight=0.2):
        self.clf = classifier; self.anomaly = anomaly
        self.ml_weight = ml_weight
        self.rule_weight = rule_weight
        self.anomaly_weight = anomaly_weight
        self.feedback_buffer: List[Tuple[np.ndarray, int]] = []

    def _rule_score(self, fv: FeatureVector):
        reasons = []; score = 0.0; veto = False
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
        return max(0.0, min(1.0, score)), reasons, veto

    def decide(self, fv: FeatureVector, learn_ok: bool = True) -> Decision:
        rule_score, reasons, veto = self._rule_score(fv)
        x = fv.to_array()
        ml_score_raw = self.clf.predict_proba(x)
        anom_score, is_anom = self.anomaly.score(x)
        top_feats = self.clf.explain(x, top_k=5)

        # ML confidence gate
        n_upd = getattr(self.clf, "n_updates", 0)
        if n_upd < self.MIN_ML_UPDATES:
            ml_trust = 0.10
            reasons.append(
                f"ML undertrained ({n_upd}/{self.MIN_ML_UPDATES}) — "
                f"downweighted to 10%")
        else:
            ml_trust = 1.0
        ml_score = ml_score_raw * ml_trust

        if veto:
            fused = 1.0; reasons.append("RULE VETO: forcing malicious")
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
            if rule_score >= 0.5 and ml_score < 0.2 and ml_trust >= 1.0:
                reasons.append(f"⚠ Conflict: rules={rule_score:.2f} ml={ml_score:.2f}")

        if fused >= 0.85 or veto:
            level = ThreatLevel.RANSOMWARE_DETECTED
        elif fused >= 0.60:
            level = ThreatLevel.HIGH_RISK
        elif fused >= 0.35:
            level = ThreatLevel.SUSPICIOUS
        elif (is_anom and anom_score > 0.6
              and self.anomaly.train_calls >= self.anomaly.min_train_calls):
            level = ThreatLevel.ANOMALY
            reasons.append(f"Unsupervised anomaly ({anom_score:.2f})")
        else:
            level = ThreatLevel.CLEAN

        if learn_ok:
            self.anomaly.observe(x, label=None
                                 if level != ThreatLevel.RANSOMWARE_DETECTED else 1)

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
# LAYER 5: PROCESS CORRELATION (skips observer events)
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
    def file_rate(self) -> float:
        return self.total_files / max(self.duration_sec, 1e-3)

    @property
    def dir_diversity(self) -> int:
        return len(self.dirs_touched)

    @property
    def ext_diversity(self) -> int:
        return len(self.extensions_touched)


class ProcessCorrelator:
    def __init__(self, shield, events_per_check=20, seconds_per_check=30.0):
        self.shield = shield
        self.sessions: Dict[int, ProcessSession] = {}
        self.events_per_check = events_per_check
        self.seconds_per_check = seconds_per_check
        self.last_check: Dict[int, float] = {}

    def _key(self, event: FileEvent) -> int:
        return event.pid if event.pid else (hash(event.process_name) & 0xFFFFFFFF)

    def observe(self, event: FileEvent) -> Optional[Decision]:
        # v5.6.1: never correlate observer-originated events
        if event.process_name in OBSERVER_PROCESS_NAMES:
            return None
        key = self._key(event)
        sess = self.sessions.get(key)
        if sess is None:
            sess = ProcessSession(pid=event.pid, process_name=event.process_name)
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
        if len(sess.events) < 3: return None
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

        if (sess.ransomware_ext_hits >= 5 or sess.dir_diversity >= 3 or
                (sess.total_files >= 100 and sess.ext_diversity >= 8)):
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
    def __init__(self):
        self.hashes: Set[str] = set()
        self.process_patterns: List[re.Pattern] = []
        self.path_patterns: List[re.Pattern] = []

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
            raise ImportError("requests not installed (pip install requests)")
        r = requests.get(url, timeout=15); r.raise_for_status()
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

    def hash_file(self, path: str) -> str:
        try:
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def save(self, path: str):
        with open(path, 'w') as f:
            for h in sorted(self.hashes): f.write(f"hash:{h}\n")
            for p in self.process_patterns: f.write(f"proc:{p.pattern}\n")
            for p in self.path_patterns: f.write(f"path:{p.pattern}\n")

    @classmethod
    def load(cls, path: str):
        obj = cls()
        if os.path.exists(path): obj.load_file(path)
        return obj

# ============================================================
# AUTO-RESPONSE — Rollback, Kill, Blacklist (v5.6.1)
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
    def __init__(self, shield, max_entries_per_process: int = 500):
        self.shield = shield
        self.max_entries_per_process = max_entries_per_process
        self.history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_entries_per_process))
        self._snapshots: Dict[str, Tuple[float, str]] = {}
        self._snapshot_ttl = 3600.0

    def snapshot_before_write(self, event: FileEvent) -> Optional[str]:
        if not self.shield.policies.backup_enabled:
            return None
        if not os.path.exists(event.path):
            return None
        try:
            if os.path.getsize(event.path) > 100 * 1024 * 1024:
                return None
        except OSError:
            return None

        now = time.time()
        cached = self._snapshots.get(event.path)
        if cached and (now - cached[0]) < self._snapshot_ttl:
            return cached[1]

        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        dest = os.path.join(
            self.shield.backup_dir,
            f"{ts}_{os.path.basename(event.path)}.vss")
        try:
            shutil.copy2(event.path, dest)
            self._snapshots[event.path] = (now, dest)
            return dest
        except Exception:
            return None

    def record(self, event: FileEvent, backup_path: Optional[str]):
        try:
            size = os.path.getsize(event.path) if os.path.exists(event.path) else 0
        except OSError:
            size = 0
        entry = RollbackEntry(
            path=event.path,
            operation=event.operation,
            timestamp=event.timestamp,
            size_at_touch=size,
            backup_path=backup_path,
        )
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
                details.append({'path': e.path, 'status': 'would_restore',
                                'from': e.backup_path})
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
        return {
            'process': process_name,
            'attempted': len(write_entries),
            'restored': restored,
            'failed': failed,
            'skipped': skipped,
            'details': details[:50],
        }

    def process_summary(self, process_name: str) -> Dict[str, Any]:
        entries = list(self.history.get(process_name, []))
        return {
            'process': process_name,
            'files_touched': len(entries),
            'writes': sum(1 for e in entries if e.operation == 'write'),
            'reads': sum(1 for e in entries if e.operation == 'read'),
            'with_snapshot': sum(1 for e in entries if e.backup_path),
        }


class ProcessKiller:
    def __init__(self, shield):
        self.shield = shield
        self.psutil = psutil if PSUTIL_OK else None
        self.available = PSUTIL_OK

    def kill_tree(self, pid: int, process_name: str,
                  dry_run: bool = False) -> Dict[str, Any]:
        result = {'pid': pid, 'process': process_name,
                  'killed': [], 'failed': [], 'method': 'none'}

        # refuse to kill init, self, or parent
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

        if not self.available:
            result['method'] = 'unavailable'
            result['failed'].append('psutil not installed')
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
        # v5.6.1: purge self/observer entries from poisoned blacklists
        banned = _self_process_names()
        before = len(self.entries)
        self.entries = {k: v for k, v in self.entries.items() if k not in banned}
        if len(self.entries) != before:
            print(f"{Colors.YELLOW}[!] Purged {before - len(self.entries)} "
                  f"self/observer entries from blacklist{Colors.END}")
            self.save()

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self.entries, f, indent=2)
        except Exception:
            pass

    def add(self, process_name: str, reason: str = "", pid: int = 0):
        # v5.6.1: refuse to add self/observer names
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
                'process': name,
                'hits': e.get('hits', 0),
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


class AutoResponse:
    def __init__(self, shield, policy: AutoResponsePolicy = None):
        self.shield = shield
        self.policy = policy or AutoResponsePolicy()
        self.rollback = RollbackManager(shield)
        self.killer = ProcessKiller(shield)

    def _is_self(self, event: FileEvent) -> Optional[str]:
        """Return reason if event targets self/observer, else None."""
        my_pid = os.getpid()
        safe_names = _self_process_names()
        if event.pid == my_pid:
            return f"my pid={my_pid}"
        if event.process_name in safe_names:
            return f"self/observer name={event.process_name}"
        return None

    def handle(self, event: FileEvent, d: Decision) -> Dict[str, Any]:
        # v5.6.1: refuse to act on our own process
        self_reason = self._is_self(event)
        if self_reason:
            self.shield.typer.type_warning(
                f"🛡  Refusing auto-response on self/observer: {self_reason}")
            report = {
                'timestamp': datetime.now().isoformat(),
                'event': asdict(event),
                'decision': {
                    'level': d.threat_level.name,
                    'rule': d.rule_score, 'ml': d.ml_score,
                    'anomaly': d.anomaly_score, 'fused': d.fused_score,
                    'reasons': list(d.reasons),
                },
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
            'decision': {
                'level': d.threat_level.name,
                'rule': d.rule_score, 'ml': d.ml_score,
                'anomaly': d.anomaly_score, 'fused': d.fused_score,
                'reasons': list(d.reasons),
            },
            'dry_run': self.policy.dry_run,
            'kill': None,
            'quarantine': None,
            'rollback': None,
            'blacklist': None,
        }

        if self.policy.blacklist_process:
            is_self = self._is_self(event) is not None
            if not self.policy.dry_run and not is_self:
                self.shield.blacklist.add(
                    event.process_name,
                    reason=f"detected {d.threat_level.name}",
                    pid=event.pid)
            report['blacklist'] = {
                'process': event.process_name,
                'applied': (not self.policy.dry_run) and (not is_self),
            }

        if self.policy.kill_process and event.pid:
            report['kill'] = self.killer.kill_tree(
                event.pid, event.process_name, dry_run=self.policy.dry_run)
            killed_n = len(report['kill'].get('killed', []))
            self.shield.typer.type_error(
                f"🔪 Kill {'(dry-run) ' if self.policy.dry_run else ''}"
                f"{event.process_name} (pid={event.pid}): {killed_n} killed")

        if self.policy.quarantine_current:
            if self.policy.dry_run:
                report['quarantine'] = {
                    'path': event.path,
                    'status': 'would_quarantine',
                }
            else:
                ok = self.shield.quarantine_file(event.path)
                report['quarantine'] = {
                    'path': event.path,
                    'status': 'quarantined' if ok else 'failed',
                }

        if self.policy.rollback_files:
            summary = self.rollback.rollback_process(
                event.process_name, dry_run=self.policy.dry_run)
            report['rollback'] = summary
            self.shield.typer.type_error(
                f"♻️  Rollback {'(dry-run) ' if self.policy.dry_run else ''}"
                f"{summary['restored']}/{summary['attempted']} files restored "
                f"({summary['failed']} failed)")

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

# ============================================================
# SIEM FORWARDING
# ============================================================
class SiemTarget:
    name = "base"
    def send(self, events: List[Dict[str, Any]]) -> bool:
        raise NotImplementedError
    def test(self) -> Tuple[bool, str]:
        return True, "not implemented"


class SplunkHEC(SiemTarget):
    name = "splunk"
    def __init__(self, cfg: Dict[str, Any]):
        self.url = cfg["url"].rstrip('/')
        self.token = cfg["token"]
        self.index = cfg.get("index", "main")
        self.source = cfg.get("source", "shield_core")
        self.sourcetype = cfg.get("sourcetype", "shield:event")
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)

    def send(self, events):
        try:
            import requests
        except ImportError:
            return False
        url = f"{self.url}/services/collector/event"
        headers = {
            "Authorization": f"Splunk {self.token}",
            "Content-Type": "application/json",
        }
        body = "\n".join(json.dumps({
            "time": e.get("timestamp", time.time()),
            "host": _hostname(),
            "source": self.source,
            "sourcetype": self.sourcetype,
            "index": self.index,
            "event": e,
        }) for e in events)
        try:
            r = requests.post(url, data=body, headers=headers,
                              verify=self.verify, timeout=self.timeout)
            return r.status_code in (200, 201)
        except Exception:
            return False

    def test(self):
        try:
            import requests
        except ImportError:
            return False, "requests not installed"
        url = f"{self.url}/services/collector/health"
        headers = {"Authorization": f"Splunk {self.token}"}
        try:
            r = requests.get(url, headers=headers,
                             verify=self.verify, timeout=self.timeout)
            return r.status_code == 200, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)


class ElasticBulk(SiemTarget):
    name = "elastic"
    def __init__(self, cfg: Dict[str, Any]):
        self.url = cfg["url"].rstrip('/')
        self.index = cfg.get("index", "shield-events")
        self.api_key = cfg.get("api_key")
        self.username = cfg.get("username")
        self.password = cfg.get("password")
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)

    def _headers(self):
        h = {"Content-Type": "application/x-ndjson"}
        if self.api_key:
            h["Authorization"] = f"ApiKey {self.api_key}"
        return h

    def _auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def _resolve_index(self) -> str:
        idx = self.index
        if "%" in idx:
            idx = datetime.now().strftime(idx)
        return idx

    def send(self, events):
        try:
            import requests
        except ImportError:
            return False
        idx = self._resolve_index()
        lines = []
        for e in events:
            lines.append(json.dumps({"index": {"_index": idx}}))
            lines.append(json.dumps(e))
        body = "\n".join(lines) + "\n"
        url = f"{self.url}/_bulk"
        try:
            r = requests.post(url, data=body, headers=self._headers(),
                              auth=self._auth(), verify=self.verify,
                              timeout=self.timeout)
            return r.status_code in (200, 201)
        except Exception:
            return False

    def test(self):
        try:
            import requests
        except ImportError:
            return False, "requests not installed"
        try:
            r = requests.get(f"{self.url}/", headers=self._headers(),
                             auth=self._auth(), verify=self.verify,
                             timeout=self.timeout)
            return r.status_code == 200, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)


class LokiPush(SiemTarget):
    name = "loki"
    def __init__(self, cfg: Dict[str, Any]):
        self.url = cfg["url"].rstrip('/')
        self.labels = cfg.get("labels", {"job": "shield_core"})
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)
        self.username = cfg.get("username")
        self.password = cfg.get("password")

    def _auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def send(self, events):
        try:
            import requests
        except ImportError:
            return False
        values = []
        for e in events:
            ts_ns = str(int(e.get("timestamp", time.time()) * 1_000_000_000))
            values.append([ts_ns, json.dumps(e)])
        payload = {"streams": [{"stream": self.labels, "values": values}]}
        url = f"{self.url}/loki/api/v1/push"
        try:
            r = requests.post(url, json=payload,
                              auth=self._auth(), verify=self.verify,
                              timeout=self.timeout)
            return r.status_code in (200, 204)
        except Exception:
            return False

    def test(self):
        try:
            import requests
        except ImportError:
            return False, "requests not installed"
        try:
            r = requests.get(f"{self.url}/ready",
                             auth=self._auth(), verify=self.verify,
                             timeout=self.timeout)
            return r.status_code == 200, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)


class GenericWebhook(SiemTarget):
    name = "webhook"
    def __init__(self, cfg: Dict[str, Any]):
        self.url = cfg["url"]
        self.headers = cfg.get("headers", {})
        self.verify = cfg.get("verify_tls", True)
        self.timeout = cfg.get("timeout", 10)

    def send(self, events):
        try:
            import requests
        except ImportError:
            return False
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        try:
            r = requests.post(self.url, json={"events": events},
                              headers=headers, verify=self.verify,
                              timeout=self.timeout)
            return r.status_code in (200, 201, 202, 204)
        except Exception:
            return False

    def test(self):
        try:
            import requests
        except ImportError:
            return False, "requests not installed"
        try:
            r = requests.post(self.url, json={"events": [{"test": True}]},
                              headers=self.headers, verify=self.verify,
                              timeout=self.timeout)
            return r.status_code < 500, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)


def make_siem_target(cfg: Dict[str, Any]) -> Optional[SiemTarget]:
    t = cfg.get("type", "").lower()
    try:
        if t == "splunk":   return SplunkHEC(cfg)
        if t == "elastic":  return ElasticBulk(cfg)
        if t == "loki":     return LokiPush(cfg)
        if t == "webhook":  return GenericWebhook(cfg)
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Bad SIEM target ({t}): {e}{Colors.END}")
    return None


class SiemForwarder:
    def __init__(self, targets: List[Dict[str, Any]] = None,
                 batch_size: int = 50, flush_interval: float = 5.0,
                 queue_max: int = 10000):
        self.targets: List[SiemTarget] = []
        for cfg in (targets or []):
            t = make_siem_target(cfg)
            if t:
                self.targets.append(t)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue: "deque[Dict[str, Any]]" = deque(maxlen=queue_max)
        self.queue_max = queue_max
        self.dropped = 0
        self.sent = 0
        self.failed = 0
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self):
        if not self.targets: return
        if self._thread and self._thread.is_alive(): return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def emit(self, event_dict: Dict[str, Any]):
        with self._lock:
            if len(self.queue) >= self.queue_max:
                self.dropped += 1
            self.queue.append(event_dict)

    def _drain_batch(self) -> List[Dict[str, Any]]:
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
            should_flush = (len(batch) >= self.batch_size or
                            (batch and now - last_flush >= self.flush_interval))
            if should_flush and batch:
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
                try:
                    ok = t.send(batch)
                except Exception:
                    ok = False
                if ok: break
                time.sleep(0.5 * (2 ** attempt))
            if ok:
                self.sent += len(batch)
            else:
                self.failed += len(batch)

    def flush(self, timeout: float = 5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if not self.queue:
                    return
            time.sleep(0.1)

    def stats(self) -> Dict[str, Any]:
        return {
            "targets": [t.name for t in self.targets],
            "queued": len(self.queue),
            "sent": self.sent,
            "failed": self.failed,
            "dropped": self.dropped,
        }

    def test_targets(self) -> List[Tuple[str, bool, str]]:
        out = []
        for t in self.targets:
            ok, msg = t.test()
            out.append((t.name, ok, msg))
        return out

# ============================================================
# CONFIG FILE
# ============================================================
DEFAULT_CONFIG = {
    "workspace": None,
    "backend": "lr",
    "shadow_mode": False,
    "deploy_user_honeypots": False,
    "watch_path": None,
    "realtime": True,
    "auto_response": {
        "kill_process": True,
        "rollback_files": True,
        "quarantine_current": True,
        "blacklist_process": True,
        "dry_run": False,
        "min_level": "RANSOMWARE_DETECTED",
    },
    "siem": {
        "enabled": False,
        "targets": [],
        "batch_size": 50,
        "flush_interval": 5.0,
        "queue_max": 10000,
    },
}

def _deep_merge(base: dict, overlay: dict):
    for k, v in overlay.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v

def load_config(path: str) -> Dict[str, Any]:
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
# DAEMON RUNTIME (stale PID detection)
# ============================================================
class DaemonRuntime:
    def __init__(self, shield: "ShieldCore", pid_path: str,
                 log_path: str = None):
        self.shield = shield
        self.pid_path = pid_path
        self.log_path = log_path or os.path.join(
            shield.workspace_dir, "logs", "daemon.log")
        self._shutdown = threading.Event()
        self._reload = threading.Event()
        self._stats = threading.Event()
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def _write_pid(self):
        # detect and clear stale PID files
        if os.path.exists(self.pid_path):
            try:
                with open(self.pid_path) as f:
                    old_pid = int(f.read().strip())
                alive = False
                try:
                    os.kill(old_pid, 0)
                    alive = True
                except OSError:
                    alive = False
                if alive and old_pid != os.getpid():
                    print(f"{Colors.RED}[x] Another instance is running "
                          f"(pid={old_pid}). Aborting.{Colors.END}")
                    sys.exit(1)
                else:
                    print(f"{Colors.YELLOW}[!] Removing stale PID file "
                          f"(pid={old_pid} is dead){Colors.END}")
                    os.remove(self.pid_path)
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Could not verify PID file: "
                      f"{e}{Colors.END}")
        try:
            with open(self.pid_path, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            print(f"[!] Could not write PID file {self.pid_path}: {e}")

    def _remove_pid(self):
        try:
            if os.path.exists(self.pid_path):
                with open(self.pid_path) as f:
                    pid_in_file = f.read().strip()
                if pid_in_file == str(os.getpid()):
                    os.remove(self.pid_path)
        except Exception:
            pass

    def _log(self, msg: str):
        line = f"{datetime.now().isoformat()} [daemon pid={os.getpid()}] {msg}\n"
        try:
            with open(self.log_path, 'a') as f:
                f.write(line)
        except Exception:
            pass
        print(f"{Colors.DIM}{line.rstrip()}{Colors.END}")

    def _install_signals(self):
        def handle_term(signum, frame):
            self._log(f"Received SIGTERM/SIGINT ({signum}); shutting down")
            self._shutdown.set()
        def handle_hup(signum, frame):
            self._log("Received SIGHUP; will reload IOC feed")
            self._reload.set()
        def handle_usr1(signum, frame):
            self._log("Received SIGUSR1; will dump status")
            self._stats.set()

        signal.signal(signal.SIGTERM, handle_term)
        signal.signal(signal.SIGINT, handle_term)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, handle_hup)
        if hasattr(signal, "SIGUSR1"):
            signal.signal(signal.SIGUSR1, handle_usr1)
        atexit.register(self._remove_pid)

    def run(self, watch_path: str = None, realtime: bool = True):
        self._write_pid()
        self._install_signals()
        self._log(f"Shield daemon started (pid={os.getpid()})")
        self._log(f"Workspace: {self.shield.workspace_dir}")
        self._log(f"Backend:   {self.shield.backend}")
        self._log(f"Shadow:    {self.shield.shadow_mode}")

        observer = None
        if watch_path and realtime and WATCHDOG_OK:
            handler = ShieldEventHandler(self.shield, ignore_patterns=[
                r'\.swp$', r'\.swx$', r'\.kate-swp$', r'~$',
                r'(^|/)\.\#', r'\.~lock\.', r'\.goutputstream-',
                r'\.tmp$', r'\.log$', r'\.part$', r'\.crdownload$',
                r'\.git/', r'__pycache__/', r'node_modules/',
                r'\.venv/', r'venv/', r'\.cache/',
                r'/proc/', r'/sys/', r'/dev/', r'/run/',
            ])
            bridge = _WatchdogBridge(handler)
            observer = Observer()
            observer.schedule(bridge, os.path.expanduser(watch_path),
                              recursive=True)
            observer.start()
            self._log(f"Watchdog watching: {watch_path}")

        self.shield.start_monitoring()
        self._log("Monitoring thread active")

        last_stats = time.time()
        try:
            while not self._shutdown.is_set():
                if self._reload.is_set():
                    self._reload.clear()
                    try:
                        n = self.shield.intel.load_file(self.shield.intel_path)
                        self.shield.intel.save(self.shield.intel_path)
                        self._log(f"Reloaded {n} IOCs on SIGHUP")
                    except Exception as e:
                        self._log(f"IOC reload failed: {e}")

                if self._stats.is_set():
                    self._stats.clear()
                    st = self.shield.get_status()
                    self._log(f"STATUS: {json.dumps(st)}")

                if time.time() - last_stats > 300:
                    last_stats = time.time()
                    st = self.shield.get_status()
                    self._log(f"periodic: events={st['events_monitored']} "
                              f"blacklist={st['blacklist_size']} "
                              f"sessions={st['sessions_tracked']}")

                time.sleep(1)
        finally:
            self._log("Shutdown requested; cleaning up...")
            self.shield.stop_monitoring()
            if observer:
                observer.stop()
                try: observer.join(timeout=3)
                except Exception: pass
            if getattr(self.shield, "siem", None):
                try:
                    self.shield.siem.flush(timeout=5.0)
                    self._log("SIEM queue flushed")
                except Exception as e:
                    self._log(f"SIEM flush error: {e}")
            self.shield.save_models()
            self._remove_pid()
            self._log("Daemon stopped cleanly")

# ============================================================
# CORE: SHIELD CORE v5.6.1
# ============================================================
class ShieldCore:
    def __init__(self, workspace_dir: str = None, autotrain_if: bool = True,
                 shadow_mode: bool = False, backend: str = "lr",
                 deploy_user_honeypots: bool = False):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/dsterminal_workspace")
        self.threat_level = ThreatLevel.CLEAN
        self.event_log: List[FileEvent] = []
        self.honeypot_paths: List[str] = []
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

        self._init_workspace()

        # Classifier
        if os.path.exists(self.clf_path):
            try:
                if self.clf_path.endswith('.pt'):
                    self.classifier = NeuralThreatClassifier.load(self.clf_path)
                else:
                    self.classifier = ThreatClassifier.load(self.clf_path)
                self.typer.type_success(f"Loaded classifier ({self.clf_path})")
            except Exception as e:
                self.typer.type_warning(f"Classifier load failed ({e}); fresh")
                self.classifier = make_classifier(backend)
        else:
            self.classifier = make_classifier(backend)
            self.typer.type_warning("No ML model found - bootstrapping synthetic")

        # Anomaly
        if os.path.exists(self.if_path):
            try:
                self.anomaly = AnomalyDetector.load(self.if_path)
                self.typer.type_success(
                    f"Loaded IsolationForest model "
                    f"(train_calls={self.anomaly.train_calls})")
            except Exception as e:
                self.typer.type_warning(f"IF load failed ({e}); fresh")
                self.anomaly = AnomalyDetector(n_features=17)
        else:
            self.anomaly = AnomalyDetector(n_features=17)

        # Intel
        self.intel = ThreatIntel.load(self.intel_path)

        self.extractor = FeatureExtractor(honeypot_paths=set(self.honeypot_paths))
        self.engine = HybridDecisionEngine(self.classifier, self.anomaly)

        self.process_stats: Dict[str, Dict] = defaultdict(lambda: {
            'ops': deque(maxlen=500),
            'files': set(), 'extensions': set(),
            'sizes': deque(maxlen=200),
            'reads': 0, 'writes': 0,
        })

        self.correlator = ProcessCorrelator(self, events_per_check=20)
        self.autotrain_if = autotrain_if
        self._anomaly_hits: Dict[str, int] = defaultdict(int)

        # Blacklist + auto-response
        self.blacklist = ProcessBlacklist(self.blacklist_path)
        self.auto_response_policy = AutoResponsePolicy(
            kill_process=True,
            rollback_files=True,
            quarantine_current=True,
            blacklist_process=True,
            dry_run=False,
        )
        self.auto_response = AutoResponse(self, self.auto_response_policy)

        # SIEM (wired later by daemon/cmd)
        self.siem: Optional[SiemForwarder] = None

        if self.shadow_mode:
            self.typer.type_warning("SHADOW MODE: detections logged, no quarantine")
        if self.policies.deploy_user_honeypots:
            self.typer.type_warning(
                "User-directory honeypots ENABLED (~/Documents, etc.)")
        if self.blacklist.entries:
            self.typer.type_warning(
                f"Blacklist has {len(self.blacklist.entries)} entries")

    # -------- Workspace / honeypots --------
    def _init_workspace(self):
        self.typer.type_status("Initializing Shield Core workspace...")
        subdirs = ["reports", "logs", "quarantine", "backups", "honeypots",
                   "models", "incidents", "training"]
        for sd in subdirs:
            p = os.path.join(self.workspace_dir, sd)
            os.makedirs(p, exist_ok=True)
            if sd == "quarantine": self.quarantine_dir = p
            elif sd == "backups": self.backup_dir = p
            elif sd == "honeypots": self.honeypot_dir = p
        self.typer.type_success(f"Workspace: {self.workspace_dir}")
        self._deploy_honeypots()

    def _deploy_honeypots(self):
        self.typer.type_status("Deploying honeypots...", Colors.YELLOW)
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
                self.honeypot_paths.append(p); deployed += 1
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
                            self.honeypot_paths.append(p); deployed += 1
                    except Exception:
                        pass
        else:
            self.typer.type_info(
                "User-directory honeypots skipped (use --deploy-honeypots to enable)")

        self.typer.type_success(f"Deployed {deployed} honeypots")

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
        if cur not in profiles: profiles.append(cur)
        return profiles

    def _is_admin(self):
        try:
            if os.name == 'nt':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return os.geteuid() == 0
        except Exception:
            return False

    # -------- Event analysis --------
    def _update_process_stats(self, event: FileEvent):
        s = self.process_stats[event.process_name]
        now = event.timestamp
        s['ops'].append(now)
        s['files'].add(event.path)
        s['extensions'].add(os.path.splitext(event.path)[1].lower())
        if event.operation == 'write': s['writes'] += 1
        else: s['reads'] += 1
        try: s['sizes'].append(os.path.getsize(event.path))
        except Exception: pass

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
        fh = ""
        try:
            if os.path.exists(event.path) and os.path.getsize(event.path) < 50_000_000:
                fh = self.intel.hash_file(event.path)
        except Exception:
            pass
        hits = self.intel.match(event, fh)
        if hits:
            d.threat_level = ThreatLevel.RANSOMWARE_DETECTED
            d.fused_score = 1.0
            d.reasons.insert(0, "IOC MATCH: " + "; ".join(hits))
            self.typer.type_error(f"🎯 IOC HIT: {hits[0]}")
        return d

    def _siem_emit(self, event: FileEvent, d: Decision, kind: str = "event"):
        if not self.siem:
            return
        payload = {
            "kind": kind,
            "timestamp": event.timestamp,
            "host": _hostname(),
            "event": {
                "path": event.path,
                "operation": event.operation,
                "process_name": event.process_name,
                "pid": event.pid,
            },
            "decision": {
                "level": d.threat_level.name,
                "rule": d.rule_score,
                "ml": d.ml_score,
                "anomaly": d.anomaly_score,
                "fused": d.fused_score,
                "reasons": d.reasons,
            },
            "workspace": self.workspace_dir,
        }
        self.siem.emit(payload)

    def analyze_event(self, event: FileEvent) -> Decision:
        # Pre-write snapshot for rollback
        backup_path = None
        if event.operation == 'write':
            backup_path = self.auto_response.rollback.snapshot_before_write(event)
            self.auto_response.rollback.record(event, backup_path)

        self.event_log.append(event)
        stats = self._update_process_stats(event)

        key = event.pid if event.pid else (hash(event.process_name) & 0xFFFFFFFF)
        sess = self.correlator.sessions.get(key)
        if sess is not None:
            sess.peak_ops_sec = max(sess.peak_ops_sec, stats['ops_per_sec'])

        fv = self.extractor.extract(event, stats)
        d = self.engine.decide(fv)
        d = self._apply_intel(event, d)

        # Blacklist auto-escalation (v5.6.1: never for self/observer)
        if (not _is_self_event(event)
                and self.blacklist.contains(event.process_name)):
            entry = self.blacklist.get(event.process_name)
            if d.threat_level.value < ThreatLevel.HIGH_RISK.value:
                d.threat_level = ThreatLevel.HIGH_RISK
                d.fused_score = max(d.fused_score, 0.65)
                d.reasons.append(
                    f"Blacklisted process (hits={entry.get('hits', 0)})")

        self._log_decision(event, d)

        # Ship detection events to SIEM
        if d.threat_level.value >= ThreatLevel.SUSPICIOUS.value:
            self._siem_emit(event, d, kind="detection")

        # Session correlation (advisory only)
        agg = self.correlator.observe(event)
        if agg and agg.threat_level.value > d.threat_level.value:
            self.typer.type_warning(
                f"[SESSION] Elevated to {agg.threat_level.name} "
                f"for PID {event.pid or '?'} ({event.process_name})")
            for r in agg.reasons[-2:]:
                print(f"   {Colors.DIM}→ {r}{Colors.END}")
            if agg.threat_level.value >= self.auto_response_policy.min_level.value:
                d = agg
            else:
                self._siem_emit(event, agg, kind="session_elevation")

        # ANOMALY escalation
        if d.threat_level == ThreatLevel.ANOMALY:
            self._anomaly_hits[event.process_name] += 1
            count = self._anomaly_hits[event.process_name]
            if count >= 5:
                d.threat_level = ThreatLevel.HIGH_RISK
                d.fused_score = max(d.fused_score, 0.65)
                d.reasons.append(
                    f"Escalated: {count} anomalies from {event.process_name}")

        # Full auto-response on confirmed threat
        if d.threat_level.value >= self.auto_response_policy.min_level.value:
            self._respond_to_threat(event, d)
        elif d.threat_level == ThreatLevel.HIGH_RISK:
            self._respond_to_threat(event, d)

        return d

    def _log_decision(self, event: FileEvent, d: Decision):
        color = {
            ThreatLevel.CLEAN: Colors.GREEN,
            ThreatLevel.SUSPICIOUS: Colors.YELLOW,
            ThreatLevel.HIGH_RISK: Colors.BRIGHT_YELLOW,
            ThreatLevel.RANSOMWARE_DETECTED: Colors.BRIGHT_RED,
            ThreatLevel.ANOMALY: Colors.BRIGHT_MAGENTA,
        }[d.threat_level]
        print(f"{color}[{d.threat_level.name:22s}]{Colors.END} "
              f"{os.path.basename(event.path)[:40]:40s} "
              f"rule={d.rule_score:.2f} ml={d.ml_score:.2f} "
              f"anom={d.anomaly_score:.2f} fused={d.fused_score:.2f}")
        for r in d.reasons[:2]:
            print(f"   {Colors.DIM}→ {r}{Colors.END}")

    def _respond_to_threat(self, event: FileEvent, d: Decision):
        # v5.6.1: silently skip self/observer events before any logging
        if _is_self_event(event):
            return

        if self.shadow_mode:
            self.typer.type_warning(
                f"[SHADOW] Would respond to {event.process_name} "
                f"(fused={d.fused_score:.2f}, level={d.threat_level.name})")
            self._save_incident(event, d)
            return

        self.typer.type_error(
            f"🚨 AUTO-RESPONSE: {event.process_name} "
            f"({d.threat_level.name}, fused={d.fused_score:.2f})")

        report = self.auto_response.handle(event, d)
        self._save_incident(event, d)
        self._siem_emit(event, d, kind="response")

        # v5.6.1: safe access even when report fields are explicitly None
        kill_report = report.get('kill') or {}
        rollback_report = report.get('rollback') or {}
        killed = len(kill_report.get('killed', []) or [])
        restored = rollback_report.get('restored', 0)
        attempted = rollback_report.get('attempted', 0)
        skipped = report.get('skipped')
        if skipped:
            self.typer.type_info(
                f"Response SKIPPED ({skipped}): {report.get('skipped_reason', '')}")
        else:
            self.typer.type_info(
                f"Response: killed={killed}, "
                f"rollback={restored}/{attempted}, "
                f"blacklisted={self.blacklist.contains(event.process_name)}")

    def _save_incident(self, event: FileEvent, d: Decision):
        p = os.path.join(
            self.incidents_dir,
            f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{event.process_name}.json")
        stats = self._update_process_stats(event)
        fv = self.extractor.extract(event, stats)
        try:
            with open(p, 'w') as f:
                json.dump({
                    'event': asdict(event),
                    'features': fv.to_array().tolist(),
                    'feature_names': FeatureVector.feature_names(),
                    'decision': {
                        'level': d.threat_level.name,
                        'rule': d.rule_score, 'ml': d.ml_score,
                        'anomaly': d.anomaly_score, 'fused': d.fused_score,
                        'reasons': d.reasons,
                    },
                    'label': None,
                }, f, indent=2)
        except Exception as e:
            self.typer.type_warning(f"Incident save failed: {e}")

    # -------- Response / Recovery (low-level) --------
    def contain_threat(self, process_name: str, pid: int) -> bool:
        try:
            if PSUTIL_OK and psutil.pid_exists(pid) and pid != os.getpid():
                pr = psutil.Process(pid); pr.terminate(); pr.wait(timeout=5)
                self.typer.type_success(f"Terminated {process_name}")
                return True
        except Exception as e:
            self.typer.type_error(f"Terminate failed: {e}")
        return False

    def quarantine_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path): return False
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = os.path.join(self.quarantine_dir,
                            f"{ts}_{os.path.basename(file_path)}.locked")
        try:
            shutil.move(file_path, dest)
            self.typer.type_success(f"Quarantined: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            self.typer.type_error(f"Quarantine failed: {e}")
            return False

    def create_restore_point(self, file_path: str) -> bool:
        if not self.policies.backup_enabled or not os.path.exists(file_path):
            return False
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = os.path.join(self.backup_dir,
                            f"{ts}_{os.path.basename(file_path)}.vss")
        try:
            shutil.copy2(file_path, dest); return True
        except Exception:
            return False

    def rollback_file(self, file_path: str) -> bool:
        pattern = f"*_{os.path.basename(file_path)}.vss"
        baks = glob.glob(os.path.join(self.backup_dir, pattern))
        if not baks: return False
        latest = max(baks, key=os.path.getctime)
        try:
            shutil.copy2(latest, file_path); return True
        except Exception:
            return False

    # -------- Learning / persistence --------
    def learn_from_feedback(self, event: FileEvent, true_label: int):
        stats = self._update_process_stats(event)
        fv = self.extractor.extract(event, stats)
        self.engine.record_feedback(fv, true_label)
        self.save_models()
        self.typer.type_success(f"Learned: label={true_label}")

    def save_models(self):
        try: self.classifier.save(self.clf_path)
        except Exception as e: self.typer.type_warning(f"Clf save failed: {e}")
        try: self.anomaly.save(self.if_path)
        except Exception as e: self.typer.type_warning(f"IF save failed: {e}")
        try: self.intel.save(self.intel_path)
        except Exception: pass
        try: self.blacklist.save()
        except Exception: pass

    def train_anomaly_now(self) -> bool:
        ok = self.anomaly.train_if_ready()
        if ok:
            self.anomaly.save(self.if_path)
            self.typer.type_success(
                f"IsolationForest trained on {len(self.anomaly.buffer)} samples "
                f"(call #{self.anomaly.train_calls}, "
                f"trust at {min(self.anomaly.train_calls, self.anomaly.min_train_calls)}"
                f"/{self.anomaly.min_train_calls})")
        else:
            self.typer.type_warning(
                f"IF needs {self.anomaly.min_samples} samples "
                f"(have {len(self.anomaly.buffer)})")
        return ok

    # -------- Reporting --------
    def generate_forensic_report(self) -> Dict:
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
            "auto_response_policy": {
                'kill_process': self.auto_response_policy.kill_process,
                'rollback_files': self.auto_response_policy.rollback_files,
                'dry_run': self.auto_response_policy.dry_run,
                'min_level': self.auto_response_policy.min_level.name,
            },
            "siem": self.siem.stats() if self.siem else None,
            "sessions": self.correlator.summary()[:10],
            "recent_events": [
                {"time": datetime.fromtimestamp(e.timestamp).isoformat(),
                 "file": os.path.basename(e.path),
                 "process": e.process_name, "op": e.operation}
                for e in self.event_log[-10:]
            ],
        }
        p = os.path.join(self.workspace_dir, "reports",
                         f"forensic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(p, 'w') as f: json.dump(rep, f, indent=2)
        return rep

    def get_status(self):
        return {
            "threat_level": self.threat_level.name,
            "is_active": self.is_active,
            "shadow_mode": self.shadow_mode,
            "backend": self.backend,
            "events_monitored": len(self.event_log),
            "honeypots": len(self.honeypot_paths),
            "quarantine_dir": self.quarantine_dir,
            "backup_dir": self.backup_dir,
            "workspace_dir": self.workspace_dir,
            "ml_updates": self.classifier.n_updates,
            "ml_trusted": self.classifier.n_updates >= HybridDecisionEngine.MIN_ML_UPDATES,
            "if_samples": len(self.anomaly.buffer),
            "if_ready": self.anomaly.model is not None,
            "if_train_calls": self.anomaly.train_calls,
            "if_trusted": self.anomaly.train_calls >= self.anomaly.min_train_calls,
            "sessions_tracked": len(self.correlator.sessions),
            "ioc_hashes": len(self.intel.hashes),
            "ioc_proc": len(self.intel.process_patterns),
            "ioc_path": len(self.intel.path_patterns),
            "blacklist_size": len(self.blacklist.entries),
            "auto_response_dry_run": self.auto_response_policy.dry_run,
            "siem_enabled": self.siem is not None,
        }

    # -------- Monitoring thread --------
    def start_monitoring(self):
        if self.is_active: return
        self.is_active = True; self._stop_monitoring = False
        def loop():
            n = 0
            while not self._stop_monitoring:
                try:
                    n += 1
                    if n % 20 == 0 and self.autotrain_if:
                        if self.anomaly.model is None:
                            self.anomaly.train_if_ready()
                    time.sleep(5)
                except Exception:
                    time.sleep(10)
        self._monitor_thread = threading.Thread(target=loop, daemon=True)
        self._monitor_thread.start()
        self.typer.type_success("Monitoring active")

    def stop_monitoring(self):
        self._stop_monitoring = True; self.is_active = False

# ============================================================
# SYNTHETIC BOOTSTRAP
# ============================================================
def generate_synthetic_training_data(n_benign=2000, n_malicious=2000):
    rng = np.random.default_rng(7)
    X, y = [], []
    for _ in range(n_benign):
        X.append([
            rng.normal(4.5, 0.8), rng.normal(0.01, 0.02),
            rng.choice([0, 1], p=[0.97, 0.03]), 0,
            rng.integers(0, 2), rng.integers(0, 2),
            rng.uniform(0.2, 0.6), rng.uniform(0, 5),
            rng.integers(1, 20), rng.integers(1, 3),
            rng.uniform(1e4, 1e6), rng.uniform(0, 0.1),
            0, 0.0, rng.integers(8, 19),
            rng.choice([0, 1], p=[0.9, 0.1]), rng.uniform(0.8, 1.5),
        ])
        y.append(0)
    for _ in range(n_malicious):
        X.append([
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
        ])
        y.append(1)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def bootstrap_model(workspace_dir: str, backend: str = "lr"):
    os.makedirs(os.path.join(workspace_dir, "models"), exist_ok=True)
    X, y = generate_synthetic_training_data()
    clf = make_classifier(backend)
    print(f"[*] Training {backend} on {len(X)} synthetic samples...")
    clf.fit(X, y, epochs=80, batch_size=64, verbose=True)
    ext = 'pt' if backend == 'torch' and TORCH_OK else 'pkl'
    out = os.path.join(workspace_dir, "models", f"shield_clf.{ext}")
    clf.save(out)
    print(f"[+] Saved → {out}")
    return out


def train_from_csv(csv_path: str, model_out: str, epochs: int = 100,
                   backend: str = "lr"):
    if not os.path.exists(csv_path):
        print(f"{Colors.RED}[x] CSV not found: {csv_path}{Colors.END}")
        return
    X, y = [], []
    with open(csv_path, newline='') as f:
        rows = list(csv.reader(f))
    if not rows:
        print(f"{Colors.YELLOW}[!] CSV is empty.{Colors.END}"); return

    start_idx = 0
    try:
        float(rows[0][0]); float(rows[0][17])
    except (ValueError, IndexError):
        start_idx = 1

    skipped = 0
    for row in rows[start_idx:]:
        if len(row) < 18:
            skipped += 1; continue
        try:
            X.append([float(v) for v in row[:17]])
            y.append(int(float(row[17])))
        except (ValueError, TypeError):
            skipped += 1; continue

    if skipped:
        print(f"{Colors.YELLOW}[!] Skipped {skipped} malformed row(s){Colors.END}")
    if not X:
        print(f"{Colors.YELLOW}[!] No valid rows.{Colors.END}"); return

    X = np.array(X, dtype=np.float32); y = np.array(y, dtype=np.int32)
    nb = int((y == 0).sum()); nm = int((y == 1).sum())
    if nb == 0 or nm == 0:
        print(f"{Colors.YELLOW}[!] Only one class (benign={nb}, malicious={nm})."
              f"{Colors.END}")

    print(f"[*] Training {backend} on {len(X)} samples ({nb} benign / {nm} malicious)...")
    clf = make_classifier(backend)
    clf.fit(X, y, epochs=epochs, batch_size=64, verbose=True)
    clf.save(model_out)
    print(f"[+] Saved → {model_out}")

# ============================================================
# WATCHDOG REAL-TIME OBSERVER
# ============================================================
class ShieldEventHandler:
    def __init__(self, shield: ShieldCore,
                 ignore_patterns: Optional[List[str]] = None):
        self.shield = shield
        self.ignore_patterns = [re.compile(p) for p in (ignore_patterns or [])]
        self._recent: Dict[str, float] = {}
        self._debounce_sec = 0.15

    def _should_ignore(self, path: str) -> bool:
        for pat in self.ignore_patterns:
            if pat.search(path): return True
        try:
            ws = os.path.abspath(self.shield.workspace_dir)
            if os.path.abspath(path).startswith(ws): return True
        except Exception:
            pass
        if path.endswith(('.pkl', '.pyc', '.pt')): return True

        base = os.path.basename(path)
        for hp in self.shield.honeypot_paths:
            hp_base = os.path.basename(hp)
            if hp_base in base and base != hp_base:
                return True

        if base.startswith('.'):
            for marker in ('.swp', '.swx', '.kate-swp', '.goutputstream',
                           '.~lock', '.tmp', '.crdownload', '.part'):
                if marker in base:
                    return True
            if base.endswith('~'):
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
        if self._should_ignore(path) or self._debounced(path): return
        # pid=0 so correlator/auto-response never treat this as a real process
        ev = FileEvent(path=path, operation=op,
                       process_name="watchdog", pid=0)
        try: self.shield.analyze_event(ev)
        except Exception as e:
            self.shield.typer.type_warning(f"watchdog analyze error: {e}")

    def dispatch(self, event):
        if event.is_directory: return
        et = event.event_type
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
        def __init__(self, handler): super().__init__(); self.handler = handler
        def on_any_event(self, event):
            try: self.handler.dispatch(event)
            except Exception: pass

# ============================================================
# FLASK DASHBOARD
# ============================================================
DASHBOARD_HTML = r"""
<!doctype html><html><head><meta charset="utf-8">
<title>Shield_Core Dashboard</title>
<style>
  :root { --bg:#0d1117; --panel:#161b22; --text:#e6edf3; --dim:#7d8590;
          --green:#3fb950; --red:#f85149; --yellow:#d29922; --blue:#58a6ff;
          --magenta:#bc8cff; }
  body { background:var(--bg); color:var(--text);
         font-family: ui-monospace, Menlo, Consolas, monospace;
         margin:0; padding:24px; }
  h1 { color:var(--blue); margin:0 0 4px 0; }
  .sub { color:var(--dim); margin-bottom:24px; }
  .grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
  .card { background:var(--panel); padding:16px; border-radius:8px; }
  .card .label { color:var(--dim); font-size:12px; }
  .card .value { font-size:24px; font-weight:bold; margin-top:4px; }
  .green { color:var(--green); } .red { color:var(--red); }
  .yellow { color:var(--yellow); } .magenta { color:var(--magenta); }
  table { width:100%; border-collapse:collapse; margin-top:16px; }
  th, td { padding:8px 10px; text-align:left; border-bottom:1px solid #21262d;
           font-size:13px; }
  th { color:var(--dim); font-weight:normal; }
  tr:hover { background:#1c2128; }
  .badge { padding:2px 8px; border-radius:10px; font-size:11px; }
  .b-CLEAN { background:#1f6feb33; color:var(--blue); }
  .b-SUSPICIOUS { background:#d2992233; color:var(--yellow); }
  .b-HIGH_RISK { background:#d2992266; color:var(--yellow); }
  .b-RANSOMWARE_DETECTED { background:#f8514933; color:var(--red); }
  .b-ANOMALY { background:#bc8cff33; color:var(--magenta); }
  button { background:var(--panel); color:var(--text); border:1px solid #30363d;
           padding:4px 10px; border-radius:6px; cursor:pointer; }
  button.m:hover { border-color:var(--red); color:var(--red); }
  button.b:hover { border-color:var(--green); color:var(--green); }
  .row-actions button { margin-right:4px; }
</style></head><body>
  <h1>Shield_Core Dashboard</h1>
  <div class="sub">Live hybrid ransomware defense telemetry</div>
  <div class="grid" id="summary"></div>
  <table><thead><tr>
    <th>Time</th><th>Level</th><th>Process</th><th>File</th>
    <th>Fused</th><th>Rule / ML / Anom</th><th>Label</th><th>Actions</th>
  </tr></thead><tbody id="rows"></tbody></table>
<script>
async function refresh() {
  const s = await (await fetch('/api/summary')).json();
  document.getElementById('summary').innerHTML = `
    <div class="card"><div class="label">Total incidents</div><div class="value">${s.total}</div></div>
    <div class="card"><div class="label">Malicious</div><div class="value red">${s.malicious}</div></div>
    <div class="card"><div class="label">Benign</div><div class="value green">${s.benign}</div></div>
    <div class="card"><div class="label">Pending review</div><div class="value yellow">${s.pending}</div></div>
  `;
  const rows = await (await fetch('/api/incidents')).json();
  document.getElementById('rows').innerHTML = rows.reverse().map(r => `
    <tr>
      <td>${new Date(r.time*1000).toLocaleTimeString()}</td>
      <td><span class="badge b-${r.level}">${r.level}</span></td>
      <td>${r.process}</td>
      <td title="${r.path}">${r.path.split('/').pop().slice(0,40)}</td>
      <td>${r.fused.toFixed(2)}</td>
      <td>${r.rule.toFixed(2)} / ${r.ml.toFixed(2)} / ${r.anom.toFixed(2)}</td>
      <td>${r.label === 1 ? '<span class="red">malicious</span>' :
            r.label === 0 ? '<span class="green">benign</span>' :
            '<span class="dim">pending</span>'}</td>
      <td class="row-actions">
        <button class="m" onclick="label('${r.file}', 1)">M</button>
        <button class="b" onclick="label('${r.file}', 0)">B</button>
      </td>
    </tr>`).join('');
}
async function label(file, label) {
  await fetch('/api/label', {method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({file, label})});
  refresh();
}
refresh(); setInterval(refresh, 4000);
</script></body></html>
"""


def create_dashboard_app(workspace_dir: str):
    try:
        from flask import Flask, jsonify, render_template_string, request
    except ImportError:
        raise ImportError("Flask not installed (pip install flask)")

    app = Flask(__name__)
    inc_dir = os.path.join(workspace_dir, "incidents")

    @app.route("/")
    def index():
        return render_template_string(DASHBOARD_HTML)

    @app.route("/api/summary")
    def api_summary():
        files = glob.glob(os.path.join(inc_dir, "*.json"))
        lb = lm = pending = 0; levels = {}
        for fp in files:
            try:
                with open(fp) as f: d = json.load(f)
                lab = d.get('label')
                if lab == 0: lb += 1
                elif lab == 1: lm += 1
                else: pending += 1
                lvl = d.get('decision', {}).get('level', 'UNKNOWN')
                levels[lvl] = levels.get(lvl, 0) + 1
            except Exception:
                continue
        return jsonify({'total': len(files), 'benign': lb,
                        'malicious': lm, 'pending': pending, 'levels': levels})

    @app.route("/api/incidents")
    def api_incidents():
        limit = int(request.args.get('limit', 200))
        rows = []
        for fp in sorted(glob.glob(os.path.join(inc_dir, "*.json")))[-limit:]:
            try:
                with open(fp) as f: d = json.load(f)
                ev = d['event']; dec = d['decision']
                rows.append({
                    'file': os.path.basename(fp),
                    'process': ev['process_name'], 'path': ev['path'],
                    'time': ev['timestamp'], 'level': dec['level'],
                    'rule': dec['rule'], 'ml': dec['ml'],
                    'anom': dec['anomaly'], 'fused': dec['fused'],
                    'reasons': dec['reasons'][:3],
                    'label': d.get('label'),
                })
            except Exception:
                continue
        return jsonify(rows)

    @app.route("/api/label", methods=['POST'])
    def api_label():
        data = request.get_json() or {}
        fname = data.get('file'); label = data.get('label')
        if not fname or label not in (0, 1):
            return jsonify({'ok': False, 'error': 'file and label required'}), 400
        fp = os.path.join(inc_dir, fname)
        if not os.path.exists(fp):
            return jsonify({'ok': False, 'error': 'not found'}), 404
        with open(fp) as f: d = json.load(f)
        d['label'] = int(label)
        with open(fp, 'w') as f: json.dump(d, f, indent=2)
        return jsonify({'ok': True})

    @app.route("/api/blacklist")
    def api_blacklist():
        bl_path = os.path.join(workspace_dir, "models", "blacklist.json")
        if not os.path.exists(bl_path):
            return jsonify([])
        try:
            with open(bl_path) as f: return jsonify(json.load(f))
        except Exception:
            return jsonify([])

    return app

# ============================================================
# ANALYST CLI
# ============================================================
class AnalystCLI:
    def __init__(self, shield: ShieldCore):
        self.shield = shield
        self.incidents_dir = shield.incidents_dir

    def list_pending(self, include_observer: bool = False):
        banned = _self_process_names() | OBSERVER_PROCESS_NAMES
        files = sorted(glob.glob(os.path.join(self.incidents_dir, "*.json")))
        pending = []
        for fp in files:
            try:
                with open(fp) as f: d = json.load(f)
                if d.get('label') is not None: continue
                if not include_observer:
                    proc = d.get('event', {}).get('process_name', '')
                    if proc in banned: continue
                pending.append(fp)
            except Exception:
                continue
        return pending

    def show_incident(self, fp):
        with open(fp) as f: d = json.load(f)
        print(f"\n{Colors.BOLD}── Incident: {os.path.basename(fp)} ──{Colors.END}")
        ev = d['event']; dec = d['decision']
        print(f"  Process : {Colors.CYAN}{ev['process_name']}{Colors.END}")
        print(f"  Path    : {ev['path']}")
        print(f"  Op      : {ev['operation']}")
        print(f"  Time    : {datetime.fromtimestamp(ev['timestamp']).isoformat()}")
        print(f"  Decision: {Colors.YELLOW}{dec['level']}{Colors.END} "
              f"(rule={dec['rule']:.2f} ml={dec['ml']:.2f} "
              f"anom={dec['anomaly']:.2f} fused={dec['fused']:.2f})")
        print(f"  Reasons :")
        for r in dec['reasons']: print(f"    → {r}")
        fv_arr = np.array(d['features'], dtype=np.float32)
        expl = self.shield.classifier.explain(fv_arr, top_k=6)
        print(f"  {Colors.DIM}Top contributing features:{Colors.END}")
        for name, contrib in expl:
            bar = '█' * int(min(abs(contrib), 1.0) * 20)
            sign = '+' if contrib > 0 else '-'
            color = Colors.RED if contrib > 0 else Colors.GREEN
            print(f"    {name:24s} {color}{sign}{abs(contrib):.3f} {bar}{Colors.END}")

    def label_incident(self, fp, label):
        with open(fp) as f: d = json.load(f)
        d['label'] = label
        with open(fp, 'w') as f: json.dump(d, f, indent=2)
        fv = FeatureVector(*d['features'])
        self.shield.engine.record_feedback(fv, label)
        self.shield.save_models()

    def run_interactive(self, include_observer: bool = False):
        pending = self.list_pending(include_observer=include_observer)
        if not pending:
            print(f"{Colors.GREEN}No pending incidents to label.{Colors.END}")
            return
        print(f"\n{Colors.BOLD}{len(pending)} incidents pending review{Colors.END}\n")
        for fp in pending:
            self.show_incident(fp)
            print(f"\n  {Colors.BOLD}Label:{Colors.END}  "
                  f"[{Colors.RED}m{Colors.END}]alicious  "
                  f"[{Colors.GREEN}b{Colors.END}]enign  "
                  f"[{Colors.YELLOW}s{Colors.END}]kip  "
                  f"[{Colors.CYAN}q{Colors.END}]uit")
            try: choice = input("  > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print(); break
            if choice == 'm':
                self.label_incident(fp, 1)
                print(f"  {Colors.RED}✓ malicious{Colors.END}")
            elif choice == 'b':
                self.label_incident(fp, 0)
                print(f"  {Colors.GREEN}✓ benign{Colors.END}")
            elif choice == 'q': break
            else: print(f"  {Colors.DIM}Skipped{Colors.END}")
        self.shield.engine.replay_feedback(epochs=5)
        self.shield.save_models()
        print(f"\n{Colors.GREEN}✓ Feedback applied.{Colors.END}")

    def bulk_label_report(self):
        files = glob.glob(os.path.join(self.incidents_dir, "*.json"))
        lb = lm = p = 0
        for fp in files:
            try:
                with open(fp) as f: d = json.load(f)
                if d.get('label') == 0: lb += 1
                elif d.get('label') == 1: lm += 1
                else: p += 1
            except Exception:
                continue
        print(f"\n{Colors.BOLD}Dataset stats{Colors.END}")
        print(f"  Total : {len(files)}")
        print(f"  Benign: {Colors.GREEN}{lb}{Colors.END}  "
              f"Malicious: {Colors.RED}{lm}{Colors.END}  "
              f"Pending: {Colors.YELLOW}{p}{Colors.END}")

# ============================================================
# CLI COMMANDS
# ============================================================
def _ensure_file(path, size=4096, high_entropy=False):
    try:
        if os.path.exists(path): return path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if high_entropy:
            with open(path, 'wb') as f: f.write(os.urandom(size))
        else:
            with open(path, 'w') as f:
                f.write("sample content " * (size // 16))
        return path
    except Exception:
        import tempfile
        fd, tmp = tempfile.mkstemp(prefix="shield_"); os.close(fd)
        if high_entropy:
            with open(tmp, 'wb') as f: f.write(os.urandom(size))
        else:
            with open(tmp, 'w') as f:
                f.write("sample content " * (size // 16))
        return tmp


def cmd_purge_legacy(args):
    """
    Remove incident JSONs and blacklist entries created by self/observer
    processes (from pre-v5.6.1 poisoned runs).
    """
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    inc_dir = os.path.join(ws, "incidents")
    bl_path = os.path.join(ws, "models", "blacklist.json")
    banned = _self_process_names() | OBSERVER_PROCESS_NAMES

    removed_incidents = 0
    kept_incidents = 0

    if not os.path.isdir(inc_dir):
        print(f"{Colors.YELLOW}[!] No incidents dir at {inc_dir}{Colors.END}")
        return

    for fp in glob.glob(os.path.join(inc_dir, "*.json")):
        try:
            with open(fp) as f:
                d = json.load(f)
            proc = d.get('event', {}).get('process_name', '')
            reasons = d.get('decision', {}).get('reasons', []) or []
            poisoned = (
                proc in banned
                or any('Blacklisted process' in r for r in reasons)
                or any('self_process_protection' in str(r) for r in reasons)
            )
            if poisoned:
                if args.dry_run:
                    print(f"{Colors.DIM}would remove:{Colors.END} {fp}")
                else:
                    os.remove(fp)
                removed_incidents += 1
            else:
                kept_incidents += 1
        except Exception:
            continue

    # Purge blacklist entries
    removed_bl = 0
    if os.path.exists(bl_path):
        try:
            with open(bl_path) as f:
                entries = json.load(f)
            before = len(entries)
            entries = {k: v for k, v in entries.items() if k not in banned}
            removed_bl = before - len(entries)
            if removed_bl and not args.dry_run:
                with open(bl_path, 'w') as f:
                    json.dump(entries, f, indent=2)
        except Exception:
            pass

    verb = "Would remove" if args.dry_run else "Removed"
    print(f"\n{Colors.BOLD}Legacy purge summary{Colors.END}")
    print(f"  {verb} {removed_incidents} poisoned incident file(s)")
    print(f"  Kept {kept_incidents} valid incident file(s)")
    print(f"  {verb} {removed_bl} blacklist entry/entries")
    if args.dry_run:
        print(f"\n  {Colors.DIM}Dry-run mode. Rerun without --dry-run to apply.{Colors.END}")


def cmd_demo(args):
    typer = AutoTypeEngine(delay=0.02)
    os.system('cls' if os.name == 'nt' else 'clear')
    typer.type_banner([
        "╔══════════════════════════════════════════════════════════════╗",
        "║    DSTERMINAL SHIELD CORE v5.6.1 - CLEAN EDITION            ║",
        "║   Rules + LR/MLP + IsolationForest + Session + Intel + Web  ║",
        "║   + Auto-Response + Daemon + SIEM + Self-Protection         ║",
        "╚══════════════════════════════════════════════════════════════╝",
    ], Colors.CYAN)

    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    backend = getattr(args, 'backend', 'lr')
    ext = 'pt' if backend == 'torch' and TORCH_OK else 'pkl'
    clf_path = os.path.join(ws, "models", f"shield_clf.{ext}")

    if not os.path.exists(clf_path):
        typer.type_status(f"Bootstrapping synthetic model ({backend})...")
        bootstrap_model(ws, backend=backend)

    shadow = getattr(args, "shadow", False)
    deploy_hp = getattr(args, "deploy_honeypots", False)
    shield = ShieldCore(workspace_dir=ws, shadow_mode=shadow, backend=backend,
                        deploy_user_honeypots=deploy_hp)
    typer.type_status("Running detection tests...", Colors.CYAN)

    hp = shield.honeypot_paths[0] if shield.honeypot_paths else _ensure_file("/tmp/hp.txt")

    tests = [
        (hp, "invoice.pdf.exe", "malicious (honeypot veto)"),
        (_ensure_file("/tmp/document.docx", high_entropy=False),
         "winword.exe", "clean"),
        (_ensure_file("/tmp/payroll.xlsx.encrypted", high_entropy=True),
         "cryptolocker.exe", "malicious (ext+entropy+name)"),
    ]
    for path, proc, expect in tests:
        ev = FileEvent(path=path, operation='write', process_name=proc, pid=9999)
        shield.analyze_event(ev)
        print(f"  {Colors.DIM}expected: {expect}{Colors.END}")
        print()

    typer.type_status("Training IsolationForest on observed samples...")
    Xb, _ = generate_synthetic_training_data(n_benign=600, n_malicious=0)
    for x in Xb[:600]: shield.anomaly.observe(x, label=0)
    shield.anomaly.min_samples = 100
    for _ in range(3):
        shield.anomaly.train_if_ready()

    if getattr(shield.classifier, "n_updates", 0) < HybridDecisionEngine.MIN_ML_UPDATES:
        typer.type_warning(
            f"Classifier has only {shield.classifier.n_updates} updates. "
            f"ML scores are downweighted until {HybridDecisionEngine.MIN_ML_UPDATES}.")
        typer.type_info(
            "Next: `python shield_core.py label` → mark incidents → "
            "`export` → `train --csv …`")

    shield.generate_forensic_report()
    st = shield.get_status()
    typer.type_box("✅ SHIELD STATUS", [
        f"Threat Level   : {st['threat_level']}",
        f"Backend        : {st['backend']}",
        f"Shadow Mode    : {st['shadow_mode']}",
        f"Events analyzed: {st['events_monitored']}",
        f"Honeypots      : {st['honeypots']}",
        f"ML updates     : {st['ml_updates']}  trusted={st['ml_trusted']}",
        f"IF samples     : {st['if_samples']}",
        f"IF ready       : {st['if_ready']}",
        f"IF train calls : {st['if_train_calls']}",
        f"IF trusted     : {st['if_trusted']}",
        f"Sessions       : {st['sessions_tracked']}",
        f"IOC hashes     : {st['ioc_hashes']}",
        f"Blacklist size : {st['blacklist_size']}",
        f"AutoResp dry   : {st['auto_response_dry_run']}",
        f"SIEM enabled   : {st['siem_enabled']}",
        f"Workspace      : {shield.workspace_dir}",
    ], Colors.GREEN)
    print()


def cmd_label(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    shield = ShieldCore(workspace_dir=ws, backend=args.backend)
    cli = AnalystCLI(shield)
    cli.bulk_label_report()
    if not args.stats:
        cli.run_interactive(include_observer=args.include_observer)


def cmd_bootstrap(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    ext = 'pt' if args.backend == 'torch' and TORCH_OK else 'pkl'
    model_path = os.path.join(ws, "models", f"shield_clf.{ext}")
    if os.path.exists(model_path) and not args.force:
        print(f"{Colors.YELLOW}[!] Model exists at {model_path}{Colors.END}")
        try:
            ans = input("    Overwrite? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = 'n'
        if ans != 'y': print("    Aborted."); return
    bootstrap_model(ws, backend=args.backend)


def cmd_train(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    ext = 'pt' if args.backend == 'torch' and TORCH_OK else 'pkl'
    out = os.path.join(ws, "models", f"shield_clf.{ext}")
    train_from_csv(args.csv, out, epochs=args.epochs, backend=args.backend)


def cmd_export(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    inc_dir = os.path.join(ws, "incidents")
    out_csv = args.out or os.path.join(ws, "training", "labeled.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    count = 0
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(FeatureVector.feature_names() + ['label'])
        banned = _self_process_names() | OBSERVER_PROCESS_NAMES
        skipped = 0
        for fp in glob.glob(os.path.join(inc_dir, "*.json")):
            try:
                with open(fp) as fh: d = json.load(fh)
                if d.get('label') is None: continue
                proc = d.get('event', {}).get('process_name', '')
                if proc in banned:
                    skipped += 1
                    continue
                w.writerow(list(d['features']) + [d['label']]); count += 1
            except Exception:
                continue
        if skipped:
            print(f"{Colors.YELLOW}[!] Skipped {skipped} self/observer incident(s){Colors.END}")
    print(f"[+] Exported {count} labeled samples → {out_csv}")


def cmd_train_anomaly(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    shield = ShieldCore(workspace_dir=ws, backend=args.backend)
    existing = len(shield.anomaly.buffer)
    n = 0
    for fp in glob.glob(os.path.join(shield.incidents_dir, "*.json")):
        try:
            with open(fp) as f: d = json.load(f)
            if d.get('label') == 0:
                shield.anomaly.observe(np.array(d['features'], dtype=np.float32), 0)
                n += 1
        except Exception:
            continue
    print(f"[*] Loaded {n} new benign; buffer: {existing} → {len(shield.anomaly.buffer)}")
    if len(shield.anomaly.buffer) >= shield.anomaly.min_samples:
        shield.train_anomaly_now()
    else:
        print(f"{Colors.YELLOW}[!] Need {shield.anomaly.min_samples}, "
              f"have {len(shield.anomaly.buffer)}{Colors.END}")


def cmd_watch(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    deploy_hp = getattr(args, "deploy_honeypots", False)
    shield = ShieldCore(workspace_dir=ws, shadow_mode=args.shadow,
                        backend=args.backend,
                        deploy_user_honeypots=deploy_hp)
    root = args.path or os.path.expanduser("~")
    print(f"{Colors.CYAN}[*] Watching: {root}  (poll every {args.interval}s){Colors.END}")
    print(f"{Colors.DIM}    Ctrl+C to stop{Colors.END}")
    seen = {}
    try:
        while True:
            for dirpath, _, files in os.walk(root):
                for fn in files:
                    fp = os.path.join(dirpath, fn)
                    try: mtime = os.path.getmtime(fp)
                    except OSError: continue
                    if fp not in seen:
                        seen[fp] = mtime; continue
                    if mtime > seen[fp]:
                        seen[fp] = mtime
                        shield.analyze_event(FileEvent(
                            path=fp, operation='write',
                            process_name="watcher", pid=0))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Stopping watcher.{Colors.END}")
        shield.save_models()


def cmd_watch_realtime(args):
    if not WATCHDOG_OK:
        print(f"{Colors.RED}[x] watchdog not installed (pip install watchdog){Colors.END}")
        print(f"    Falling back to polling mode.")
        return cmd_watch(args)

    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    deploy_hp = getattr(args, "deploy_honeypots", False)
    shield = ShieldCore(workspace_dir=ws, shadow_mode=args.shadow,
                        backend=args.backend,
                        deploy_user_honeypots=deploy_hp)
    root = os.path.expanduser(args.path or "~")

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
    observer.schedule(bridge, root, recursive=True)
    observer.start()

    print(f"{Colors.CYAN}[*] Watchdog active on {root}{Colors.END}")
    print(f"{Colors.DIM}    Shadow={args.shadow}  "
          f"User honeypots={'on' if deploy_hp else 'off'}  "
          f"Ctrl+C to stop{Colors.END}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Stopping...{Colors.END}")
    finally:
        observer.stop(); observer.join(timeout=3)
        shield.save_models()
        print(f"{Colors.GREEN}[+] Stopped. Models saved.{Colors.END}")


def cmd_dashboard(args):
    try:
        app = create_dashboard_app(
            args.workspace or os.path.expanduser("~/dsterminal_workspace"))
    except ImportError as e:
        print(f"{Colors.RED}[x] {e}{Colors.END}"); return
    print(f"{Colors.CYAN}[*] Dashboard: http://{args.host}:{args.port}{Colors.END}")
    app.run(host=args.host, port=args.port, debug=False)


def cmd_intel(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    intel_path = os.path.join(ws, "models", "intel.txt")
    intel_url_path = os.path.join(ws, "models", "intel_url.txt")
    intel = ThreatIntel.load(intel_path)

    if args.refresh:
        n = intel.load_file(intel_path) if os.path.exists(intel_path) else 0
        extra = 0
        if os.path.exists(intel_url_path):
            with open(intel_url_path) as f:
                url = f.read().strip()
            if url:
                try:
                    extra = intel.load_url(url)
                    print(f"{Colors.GREEN}[+] Refreshed {extra} IOCs from {url}{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[x] Refresh failed: {e}{Colors.END}")
        intel.save(intel_path)
        print(f"[+] Reloaded {n} local IOCs. "
              f"Total: {len(intel.hashes)} hashes, "
              f"{len(intel.process_patterns)} proc, "
              f"{len(intel.path_patterns)} path")
        return

    if args.add:
        n = intel.load_file(args.add); intel.save(intel_path)
        print(f"{Colors.GREEN}[+] Added {n} IOCs from {args.add}{Colors.END}")
        print(f"    Total: {len(intel.hashes)} hashes, "
              f"{len(intel.process_patterns)} proc, "
              f"{len(intel.path_patterns)} path")
        return
    if args.url:
        try:
            n = intel.load_url(args.url); intel.save(intel_path)
            with open(intel_url_path, 'w') as f:
                f.write(args.url)
            print(f"{Colors.GREEN}[+] Fetched {n} IOCs from {args.url}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[x] {e}{Colors.END}")
        return
    if args.autolabel:
        inc_dir = os.path.join(ws, "incidents")
        n = 0
        for fp in glob.glob(os.path.join(inc_dir, "*.json")):
            try:
                with open(fp) as f: d = json.load(f)
                if d.get('label') is not None: continue
                ev = FileEvent(**d['event'])
                if intel.match(ev, ""):
                    d['label'] = 1; d['auto_label'] = "intel"
                    with open(fp, 'w') as f: json.dump(d, f, indent=2)
                    n += 1
            except Exception:
                continue
        print(f"{Colors.GREEN}[+] Auto-labeled {n} incidents{Colors.END}")
        return
    print(f"{Colors.BOLD}Threat Intel{Colors.END}")
    print(f"  Hashes : {len(intel.hashes)}")
    print(f"  Proc   : {len(intel.process_patterns)}")
    print(f"  Path   : {len(intel.path_patterns)}")
    print(f"  File   : {intel_path}")


def cmd_rollback(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    shield = ShieldCore(workspace_dir=ws, backend=args.backend)
    mgr = RollbackManager(shield)

    for fp in glob.glob(os.path.join(shield.incidents_dir, "*.json")):
        try:
            with open(fp) as f: d = json.load(f)
            ev_dict = d.get('event', {})
            proc = ev_dict.get('process_name')
            if not proc: continue
            if args.process and proc != args.process: continue
            ev = FileEvent(**ev_dict)
            pattern = f"*_{os.path.basename(ev.path)}.vss"
            snaps = sorted(glob.glob(os.path.join(shield.backup_dir, pattern)),
                           key=os.path.getmtime)
            backup = snaps[-1] if snaps else None
            mgr.record(ev, backup)
        except Exception:
            continue

    if args.list:
        print(f"\n{Colors.BOLD}Processes with recorded file touches:{Colors.END}")
        for pname, entries in mgr.history.items():
            n_write = sum(1 for e in entries if e.operation == 'write')
            n_snap = sum(1 for e in entries if e.backup_path)
            print(f"  {Colors.CYAN}{pname:40s}{Colors.END} "
                  f"writes={n_write:4d}  snapshots={n_snap:4d}")
        print(f"\n  {Colors.DIM}Blacklist:{Colors.END}")
        for b in shield.blacklist.summary():
            print(f"  {Colors.RED}{b['process']:40s}{Colors.END} "
                  f"hits={b['hits']}  reasons={b['reasons']}")
        return

    if not args.process:
        print(f"{Colors.RED}[x] --process required (or use --list){Colors.END}")
        return

    print(f"\n{Colors.BOLD}Rolling back: {args.process}{Colors.END}")
    summary = mgr.rollback_process(args.process, dry_run=args.dry_run)
    print(f"  Attempted : {summary['attempted']}")
    print(f"  Restored  : {Colors.GREEN}{summary['restored']}{Colors.END}")
    print(f"  Failed    : {Colors.RED}{summary['failed']}{Colors.END}")
    print(f"  Skipped   : {Colors.DIM}{summary['skipped']}{Colors.END}")
    for det in summary['details'][:20]:
        color = Colors.GREEN if det['status'] in ('restored', 'would_restore') else Colors.RED
        print(f"    {color}{det['status']:15s}{Colors.END} {det.get('path', '')[:70]}")

    if args.unblacklist and shield.blacklist.contains(args.process):
        shield.blacklist.remove(args.process)
        print(f"  {Colors.GREEN}✓ Removed from blacklist{Colors.END}")


def cmd_blacklist(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    shield = ShieldCore(workspace_dir=ws, backend=args.backend)

    if args.clear:
        count = len(shield.blacklist.entries)
        shield.blacklist.entries.clear()
        shield.blacklist.save()
        print(f"{Colors.GREEN}[+] Cleared {count} blacklist entries{Colors.END}")
        return
    if args.remove:
        if shield.blacklist.contains(args.remove):
            shield.blacklist.remove(args.remove)
            print(f"{Colors.GREEN}[+] Removed {args.remove}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[!] Not in blacklist: {args.remove}{Colors.END}")
        return
    if args.add:
        shield.blacklist.add(args.add, reason="manual")
        print(f"{Colors.GREEN}[+] Added {args.add}{Colors.END}")
        return

    entries = shield.blacklist.summary()
    if not entries:
        print(f"{Colors.GREEN}Blacklist is empty.{Colors.END}")
        return
    print(f"\n{Colors.BOLD}Process blacklist ({len(entries)}){Colors.END}")
    for e in entries:
        last = (datetime.fromtimestamp(e['last_seen']).isoformat()
                if e.get('last_seen') else "?")
        print(f"  {Colors.RED}{e['process']:40s}{Colors.END} "
              f"hits={e['hits']:3d}  last={last}")
        if e.get('reasons'):
            print(f"    {Colors.DIM}reasons: {', '.join(e['reasons'])}{Colors.END}")
    print(f"\n  {Colors.DIM}File: {shield.blacklist_path}{Colors.END}")


def cmd_response(args):
    ws = args.workspace or os.path.expanduser("~/dsterminal_workspace")
    shield = ShieldCore(workspace_dir=ws, backend=args.backend)

    pol = shield.auto_response_policy
    if args.dry_run: pol.dry_run = True
    if args.no_kill: pol.kill_process = False
    if args.no_rollback: pol.rollback_files = False
    if args.no_quarantine: pol.quarantine_current = False
    pol.min_level = ThreatLevel[args.min_level]

    print(f"\n{Colors.BOLD}Auto-Response Policy{Colors.END}")
    print(f"  Kill process      : {Colors.GREEN if pol.kill_process else Colors.RED}"
          f"{pol.kill_process}{Colors.END}")
    print(f"  Rollback files    : {Colors.GREEN if pol.rollback_files else Colors.RED}"
          f"{pol.rollback_files}{Colors.END}")
    print(f"  Quarantine file   : {Colors.GREEN if pol.quarantine_current else Colors.RED}"
          f"{pol.quarantine_current}{Colors.END}")
    print(f"  Blacklist process : "
          f"{Colors.GREEN if pol.blacklist_process else Colors.RED}"
          f"{pol.blacklist_process}{Colors.END}")
    print(f"  Dry run           : "
          f"{Colors.YELLOW if pol.dry_run else Colors.GREEN}"
          f"{pol.dry_run}{Colors.END}")
    print(f"  Min threat level  : {Colors.YELLOW}{pol.min_level.name}{Colors.END}")
    print(f"  Self-protection   : {Colors.GREEN}always on{Colors.END} "
          f"(never acts on self/observer)")


def cmd_daemon(args):
    """Run Shield_Core as a long-lived daemon."""
    cfg = load_config(args.config) if args.config else load_config(None)

    ws = (args.workspace or cfg.get("workspace")
          or os.path.expanduser("~/dsterminal_workspace"))
    backend = args.backend or cfg.get("backend", "lr")
    shadow = args.shadow if args.shadow is not None else cfg.get("shadow_mode", False)
    deploy_hp = (args.deploy_honeypots
                 if args.deploy_honeypots is not None
                 else cfg.get("deploy_user_honeypots", False))

    shield = ShieldCore(workspace_dir=ws, shadow_mode=shadow,
                        backend=backend,
                        deploy_user_honeypots=deploy_hp)

    ar = cfg.get("auto_response", {})
    shield.auto_response_policy.kill_process = ar.get("kill_process", True)
    shield.auto_response_policy.rollback_files = ar.get("rollback_files", True)
    shield.auto_response_policy.quarantine_current = ar.get("quarantine_current", True)
    shield.auto_response_policy.blacklist_process = ar.get("blacklist_process", True)
    shield.auto_response_policy.dry_run = ar.get("dry_run", False)
    try:
        shield.auto_response_policy.min_level = ThreatLevel[ar.get(
            "min_level", "RANSOMWARE_DETECTED")]
    except KeyError:
        pass

    siem_cfg = cfg.get("siem", {})
    if siem_cfg.get("enabled"):
        shield.siem = SiemForwarder(
            targets=siem_cfg.get("targets", []),
            batch_size=siem_cfg.get("batch_size", 50),
            flush_interval=siem_cfg.get("flush_interval", 5.0),
            queue_max=siem_cfg.get("queue_max", 10000),
        )
        shield.siem.start()
        print(f"{Colors.GREEN}[+] SIEM forwarder active: "
              f"{len(siem_cfg.get('targets', []))} targets{Colors.END}")

    pid_path = args.pid or os.path.join(ws, "shield.pid")
    log_path = args.log or os.path.join(ws, "logs", "daemon.log")
    watch_path = args.path or cfg.get("watch_path")
    realtime = cfg.get("realtime", True) if args.realtime is None else args.realtime

    daemon = DaemonRuntime(shield, pid_path=pid_path, log_path=log_path)
    daemon.run(watch_path=watch_path, realtime=realtime)


def cmd_siem(args):
    """Manage SIEM forwarding."""
    cfg = load_config(args.config) if args.config else load_config(None)
    siem_cfg = cfg.get("siem", {})
    if not siem_cfg.get("enabled"):
        print(f"{Colors.YELLOW}[!] SIEM not enabled in config.{Colors.END}")
        print(f"    Enable it by editing your config and setting:")
        print(f'      {{"siem": {{"enabled": true, "targets": [ ... ]}}}}')
        print(f"")
        print(f"    Then verify:")
        print(f"      python shield_core.py siem --config "
              f"{args.config or '~/.shield_core.json'} --test")
        return

    forwarder = SiemForwarder(
        targets=siem_cfg.get("targets", []),
        batch_size=siem_cfg.get("batch_size", 50),
        flush_interval=siem_cfg.get("flush_interval", 5.0),
        queue_max=siem_cfg.get("queue_max", 10000),
    )

    if args.test:
        print(f"\n{Colors.BOLD}Testing {len(forwarder.targets)} SIEM "
              f"target(s){Colors.END}")
        for name, ok, msg in forwarder.test_targets():
            color = Colors.GREEN if ok else Colors.RED
            print(f"  {color}{'OK ' if ok else 'FAIL'}{Colors.END} "
                  f"{name:12s} {msg}")
        return

    if args.emit_test:
        import uuid
        test_ev = {
            "kind": "test",
            "timestamp": time.time(),
            "host": _hostname(),
            "event": {
                "path": "/tmp/shield_siem_test.txt",
                "operation": "write",
                "process_name": "shield_siem_test",
                "pid": os.getpid(),
            },
            "decision": {
                "level": "CLEAN",
                "rule": 0.0, "ml": 0.0, "anomaly": 0.0, "fused": 0.0,
                "reasons": ["synthetic test event"],
            },
            "test_id": str(uuid.uuid4()),
        }
        print(f"{Colors.CYAN}[*] Sending synthetic test event to "
              f"{len(forwarder.targets)} target(s)...{Colors.END}")
        forwarder.start()
        forwarder.emit(test_ev)
        forwarder.flush(timeout=5.0)
        forwarder.stop()
        print(f"{Colors.GREEN}[+] Sent. Check your SIEM for "
              f"test_id={test_ev['test_id']}{Colors.END}")
        return

    print(f"\n{Colors.BOLD}SIEM Targets{Colors.END}")
    for t in forwarder.targets:
        print(f"  - {t.name}")
    print(f"\n  batch_size     : {siem_cfg.get('batch_size', 50)}")
    print(f"  flush_interval : {siem_cfg.get('flush_interval', 5.0)}s")
    print(f"  queue_max      : {siem_cfg.get('queue_max', 10000)}")


def cmd_config_init(args):
    """Write a starter config file."""
    out = os.path.expanduser(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    if os.path.exists(out):
        print(f"{Colors.YELLOW}[!] {out} already exists.{Colors.END}")
        try:
            ans = input("    Overwrite? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = 'n'
        if ans != 'y':
            print("    Aborted."); return
    with open(out, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    print(f"{Colors.GREEN}[+] Wrote starter config → {out}{Colors.END}")
    print(f"    Edit it, then run: python shield_core.py daemon --config {out}")

# ============================================================
# MAIN
# ============================================================
def main():
    p = argparse.ArgumentParser(
        prog="shield_core",
        description="Shield_Core v5.6.1 - Hardened + Clean Edition")
    p.add_argument("--workspace", "-w", default=None,
                   help="Workspace dir (default: ~/dsterminal_workspace)")
    p.add_argument("--backend", choices=['lr', 'torch'], default='lr',
                   help="Classifier backend")
    p.add_argument("--deploy-honeypots", action="store_true", default=None,
                   help="Deploy decoys into user dirs (~/Documents, etc.)")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("demo", help="Run detection demo")
    sp.add_argument("--shadow", action="store_true")
    sp.set_defaults(func=cmd_demo)

    sp = sub.add_parser("bootstrap", help="Bootstrap synthetic model")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_bootstrap)

    sp = sub.add_parser("label", help="Label incidents")
    sp.add_argument("--stats", action="store_true")
    sp.add_argument("--include-observer", action="store_true",
                    help="Include self/observer incidents (rarely wanted)")
    sp.set_defaults(func=cmd_label)

    sp = sub.add_parser("purge-legacy",
                        help="Remove self/observer incidents from pre-v5.6.1 runs")
    sp.add_argument("--dry-run", action="store_true",
                    help="Show what would be removed, don't delete")
    sp.set_defaults(func=cmd_purge_legacy)

    sp = sub.add_parser("train", help="Train from CSV")
    sp.add_argument("--csv", required=True)
    sp.add_argument("--epochs", type=int, default=100)
    sp.set_defaults(func=cmd_train)

    sp = sub.add_parser("export", help="Export labeled incidents to CSV")
    sp.add_argument("--out", default=None)
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("train-anomaly", help="Train IsolationForest")
    sp.set_defaults(func=cmd_train_anomaly)

    sp = sub.add_parser("watch", help="Watch directory tree")
    sp.add_argument("--path", default=None)
    sp.add_argument("--interval", type=float, default=2.0)
    sp.add_argument("--shadow", action="store_true")
    sp.add_argument("--realtime", action="store_true",
                    help="Use watchdog (fast) instead of polling")
    sp.set_defaults(func=lambda a: cmd_watch_realtime(a) if a.realtime else cmd_watch(a))

    sp = sub.add_parser("dashboard", help="Web dashboard")
    sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=5000)
    sp.set_defaults(func=cmd_dashboard)

    sp = sub.add_parser("intel", help="Manage IOC feed")
    sp.add_argument("--add", help="Load IOC file")
    sp.add_argument("--url", help="Fetch from URL")
    sp.add_argument("--refresh", action="store_true",
                    help="Reload local + refetch last URL")
    sp.add_argument("--autolabel", action="store_true")
    sp.set_defaults(func=cmd_intel)

    sp = sub.add_parser("rollback", help="Roll back files touched by a process")
    sp.add_argument("--process", help="Process name (e.g. suspicious.exe)")
    sp.add_argument("--dry-run", action="store_true",
                    help="Show what would be restored, don't touch files")
    sp.add_argument("--list", action="store_true",
                    help="List processes with recorded file touches")
    sp.add_argument("--unblacklist", action="store_true",
                    help="Also remove the process from blacklist")
    sp.set_defaults(func=cmd_rollback)

    sp = sub.add_parser("blacklist", help="Manage the process blacklist")
    sp.add_argument("--add", help="Add a process name")
    sp.add_argument("--remove", help="Remove a process name")
    sp.add_argument("--clear", action="store_true",
                    help="Clear the entire blacklist")
    sp.set_defaults(func=cmd_blacklist)

    sp = sub.add_parser("response", help="Configure / inspect auto-response policy")
    sp.add_argument("--dry-run", action="store_true",
                    help="Enable dry-run for this session")
    sp.add_argument("--no-kill", action="store_true",
                    help="Disable process kill")
    sp.add_argument("--no-rollback", action="store_true",
                    help="Disable file rollback")
    sp.add_argument("--no-quarantine", action="store_true",
                    help="Disable current-file quarantine")
    sp.add_argument("--min-level", default="RANSOMWARE_DETECTED",
                    choices=['SUSPICIOUS', 'HIGH_RISK',
                             'RANSOMWARE_DETECTED', 'ANOMALY'],
                    help="Minimum threat level to trigger auto-response")
    sp.set_defaults(func=cmd_response)

    sp = sub.add_parser("daemon", help="Run as a long-lived daemon")
    sp.add_argument("--config", default=None, help="Path to JSON config file")
    sp.add_argument("--pid", default=None,
                    help="PID file (default: <workspace>/shield.pid)")
    sp.add_argument("--log", default=None,
                    help="Log file (default: <workspace>/logs/daemon.log)")
    sp.add_argument("--path", default=None,
                    help="Directory to watch (overrides config)")
    sp.add_argument("--realtime", dest="realtime", action="store_true",
                    default=None, help="Force watchdog mode")
    sp.add_argument("--poll", dest="realtime", action="store_false",
                    help="Force polling mode")
    sp.add_argument("--shadow", dest="shadow", action="store_true",
                    default=None)
    sp.add_argument("--no-shadow", dest="shadow", action="store_false")
    sp.add_argument("--deploy-honeypots", dest="deploy_honeypots",
                    action="store_true", default=None)
    sp.set_defaults(func=cmd_daemon)

    sp = sub.add_parser("siem", help="Manage SIEM forwarding")
    sp.add_argument("--config", default=None, help="JSON config file")
    sp.add_argument("--test", action="store_true",
                    help="Test connectivity to all targets")
    sp.add_argument("--emit-test", action="store_true",
                    help="Send a synthetic test event")
    sp.set_defaults(func=cmd_siem)

    sp = sub.add_parser("config-init", help="Write a starter config file")
    sp.add_argument("--out", default="~/.shield_core.json",
                    help="Output path")
    sp.set_defaults(func=cmd_config_init)

    args = p.parse_args()
    if not args.cmd:
        args.shadow = False
        cmd_demo(args); return
    args.func(args)


if __name__ == "__main__":
    main()