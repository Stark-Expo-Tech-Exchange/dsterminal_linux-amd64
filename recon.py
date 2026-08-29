#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DSTerminal Reconnaissance Module - Enterprise Cinematic Edition
Centered SOC Dashboard with real-time scanning and report generation
Features: Color typing, intelligent box drawing, centered layout, full WHOIS data
Usage: python recon.py <target>
       Or import as module: from recon import run_recon, recon_menu
"""

import sys
import os
import threading
import time
import shutil
import subprocess
import random
import re
import textwrap
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib

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
# GET CORRECT USER HOME DIRECTORY (even when running with sudo)
# ============================================================
def get_user_home():
    """Get the correct user home directory even when running with sudo"""
    if os.getenv('SUDO_USER'):
        import pwd
        return pwd.getpwnam(os.getenv('SUDO_USER')).pw_dir
    else:
        return os.path.expanduser("~")

USER_HOME = get_user_home()

# ============================================================
# ANSI COLOR DEFINITIONS (ALWAYS AVAILABLE)
# ============================================================
class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    LIGHTBLACK = "\033[90m"
    LIGHTRED = "\033[91m"
    LIGHTGREEN = "\033[92m"
    LIGHTYELLOW = "\033[93m"
    LIGHTBLUE = "\033[94m"
    LIGHTMAGENTA = "\033[95m"
    LIGHTCYAN = "\033[96m"
    LIGHTWHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    BLINK_OFF = "\033[25m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    RESET_ALL = "\033[0m"
    
    @staticmethod
    def strip(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# ============================================================
# TRY TO IMPORT COLORAMA
# ============================================================
try:
    from colorama import init as colorama_init
    colorama_init(autoreset=False, convert=True, strip=False, wrap=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

# ============================================================
# UNIFIED COLOR CONSTANTS
# ============================================================
RESET = Colors.RESET
BOLD = Colors.BOLD
DIM = Colors.DIM
BLINK = Colors.BLINK
BLINK_OFF = Colors.BLINK_OFF
UNDERLINE = Colors.UNDERLINE

CYAN = Colors.CYAN
LIGHTCYAN_EX = Colors.LIGHTCYAN
GREEN = Colors.GREEN
LIGHTGREEN_EX = Colors.LIGHTGREEN
RED = Colors.RED
LIGHTRED_EX = Colors.LIGHTRED
YELLOW = Colors.YELLOW
LIGHTYELLOW_EX = Colors.LIGHTYELLOW
BLUE = Colors.BLUE
LIGHTBLUE_EX = Colors.LIGHTBLUE
MAGENTA = Colors.MAGENTA
LIGHTMAGENTA_EX = Colors.LIGHTMAGENTA
WHITE = Colors.WHITE
LIGHTWHITE_EX = Colors.LIGHTWHITE

MATRIX_COLORS = [LIGHTGREEN_EX, LIGHTCYAN_EX, LIGHTMAGENTA_EX, LIGHTYELLOW_EX, GREEN, CYAN]

# ============================================================
# ANSI HELPERS
# ============================================================
ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

def strip_ansi(text: str) -> str:
    if text is None:
        return ""
    return ANSI_RE.sub("", str(text))

def visible_len(text: str) -> int:
    return len(strip_ansi(text))

def fit_visible(text: str, width: int) -> str:
    if width <= 0:
        return ""
    clean = strip_ansi(text)
    if len(clean) <= width:
        return text
    if width <= 3:
        return clean[:width]
    return clean[:width - 3] + "..."

# ============================================================
# COLOR TYPING ENGINE - HUMAN-LIKE PEN TYPING
# ============================================================

class ColorTyping:
    """Human-like color typing engine with glowing effects"""
    
    def __init__(self, speed=0.035, variance=0.008, break_chars=80):
        self.speed = speed
        self.variance = variance
        self.break_chars = break_chars
        self.current_line_length = 0
    
    def type_text(self, text: str, color: str = "", speed: float = None, 
                  auto_break: bool = True, indent: int = 0, 
                  glow: bool = False, blink: bool = False, 
                  bold: bool = False, newline: bool = True,
                  dim: bool = False, underline: bool = False):
        """Type text with human-like rhythm and color effects"""
        import sys
        import time
        import random
        
        delay = speed if speed is not None else self.speed
        
        if indent > 0:
            sys.stdout.write(" " * indent)
            sys.stdout.flush()
        
        # Build effects with proper colorama colors
        effects = ""
        if color:
            effects += color
        if glow or bold:
            effects += BOLD
        if blink:
            effects += BLINK
        if dim:
            effects += DIM
        if underline:
            effects += UNDERLINE
        
        if effects:
            sys.stdout.write(effects)
            sys.stdout.flush()
        
        # Auto break with proper wrapping
        if auto_break and len(text) > self.break_chars:
            words = text.split()
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 > self.break_chars:
                    self._type_line(current_line.rstrip(), delay)
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    if indent > 0:
                        sys.stdout.write(" " * indent)
                        sys.stdout.flush()
                    if effects:
                        sys.stdout.write(effects)
                        sys.stdout.flush()
                    current_line = word + " "
                else:
                    current_line += word + " "
            
            if current_line:
                self._type_line(current_line.rstrip(), delay)
        else:
            self._type_line(text, delay)
        
        if effects:
            sys.stdout.write(RESET)
            if blink:
                sys.stdout.write(BLINK_OFF)
            sys.stdout.flush()
        
        if newline:
            sys.stdout.write("\n")
            sys.stdout.flush()
    
    def _type_line(self, text: str, delay: float):
        import sys
        import time
        import random
        
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            self.current_line_length += 1
            
            if char in ".!?,":
                time.sleep(delay * 2.0)
            elif char in ";:":
                time.sleep(delay * 1.5)
            elif char == " ":
                time.sleep(delay * 0.7)
            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                time.sleep(delay * 1.2)
            elif char in "0123456789":
                time.sleep(delay * 1.1)
            else:
                time.sleep(delay + (random.random() - 0.5) * self.variance)
    
    def type_glow_box(self, title: str, content_lines: List[str], 
                      title_color: str = LIGHTCYAN_EX,
                      border_color: str = CYAN,
                      content_color: str = LIGHTGREEN_EX,
                      blink_title: bool = False,
                      glow_border: bool = True,
                      width: int = None,
                      speed: float = None):
        """Type a glowing box with animated text typing"""
        if width is None:
            width = get_terminal_width()
        
        box_width = min(width - 4, 90)
        box_width = max(box_width, 60)
        left_margin = max(0, (width - box_width) // 2)
        inner_width = box_width - 4
        
        # Box characters
        TOP_LEFT = "╔"
        TOP_RIGHT = "╗"
        BOTTOM_LEFT = "╚"
        BOTTOM_RIGHT = "╝"
        HORIZONTAL = "═"
        VERTICAL = "║"
        T_LEFT = "╠"
        T_RIGHT = "╣"
        
        # Wrap content
        wrapped_lines = []
        for line in content_lines:
            if not line.strip():
                wrapped_lines.append("")
                continue
            clean_line = strip_ansi(line)
            if len(clean_line) > inner_width:
                wrapped_lines.extend(textwrap.wrap(line, inner_width, break_long_words=False))
            else:
                wrapped_lines.append(line)
        
        # Use BLINK and BLINK_OFF
        glow_prefix = BOLD if glow_border else ""
        title_prefix = BOLD
        if blink_title:
            title_prefix += BLINK
        
        top = f"{' ' * left_margin}{glow_prefix}{border_color}{TOP_LEFT}{HORIZONTAL * (box_width - 2)}{TOP_RIGHT}{RESET}"
        title_text = f" {title} ".center(box_width - 2)
        title_line = f"{' ' * left_margin}{title_prefix}{title_color}{VERTICAL}{title_text}{VERTICAL}{RESET}"
        if blink_title:
            title_line += BLINK_OFF
        mid = f"{' ' * left_margin}{glow_prefix}{border_color}{T_LEFT}{HORIZONTAL * (box_width - 2)}{T_RIGHT}{RESET}"
        bot = f"{' ' * left_margin}{glow_prefix}{border_color}{BOTTOM_LEFT}{HORIZONTAL * (box_width - 2)}{BOTTOM_RIGHT}{RESET}"
        
        delay = speed if speed is not None else self.speed
        
        # Print top border (no typing)
        sys.stdout.write(top + "\n")
        sys.stdout.flush()
        time.sleep(delay * 2)
        
        # Print title with typing effect
        sys.stdout.write(title_line + "\n")
        sys.stdout.flush()
        time.sleep(delay * 3)
        
        # Print mid separator
        sys.stdout.write(mid + "\n")
        sys.stdout.flush()
        time.sleep(delay * 2)
        
        # Print content with typing effect
        for line in wrapped_lines:
            has_color = re.search(r'\x1b\[[0-9;]*m', line)
            clean_line = strip_ansi(line)
            padding_needed = inner_width - len(clean_line)
            if padding_needed < 0:
                padding_needed = 0
            
            left_border = f"{' ' * left_margin}{glow_prefix}{border_color}{VERTICAL} {RESET}"
            sys.stdout.write(left_border)
            sys.stdout.flush()
            
            if has_color:
                # Print with colors preserved
                sys.stdout.write(line + " " * padding_needed)
                sys.stdout.flush()
            else:
                # Type with content color
                self.type_text(line.ljust(inner_width), color=content_color, newline=False, speed=delay)
            
            right_border = f" {glow_prefix}{border_color}{VERTICAL}{RESET}\n"
            sys.stdout.write(right_border)
            sys.stdout.flush()
            time.sleep(delay * 0.5)
        
        # Print bottom border
        sys.stdout.write(bot + "\n")
        sys.stdout.flush()
        time.sleep(delay * 2)
        sys.stdout.write("\n")
        sys.stdout.flush()

# ============================================================
# TERMINAL UTILITIES - CENTERED LAYOUT
# ============================================================
def get_terminal_width() -> int:
    try:
        width = shutil.get_terminal_size().columns
        return min(max(width, 80), 140)
    except:
        return 80

def center_text(text: str, width: int = None) -> str:
    if width is None:
        width = get_terminal_width()
    clean = strip_ansi(text)
    padding = max(0, (width - len(clean)) // 2)
    return " " * padding + text

def center_print(text: str, color: str = "", width: int = None):
    if width is None:
        width = get_terminal_width()
    if color:
        print(center_text(f"{color}{text}{RESET}", width))
    else:
        print(center_text(text, width))

def print_colored(text: str, color: str = ""):
    if color:
        print(f"{color}{text}{RESET}")
    else:
        print(text)

def draw_centered_box(title: str, content_lines: List[str], 
                      title_color: str = LIGHTCYAN_EX,
                      border_color: str = CYAN,
                      content_color: str = LIGHTGREEN_EX,
                      blink_title: bool = False,
                      glow_border: bool = True,
                      width: int = None,
                      use_typing: bool = False):
    """Draw a centered glowing neon hacker-styled box with proper text fitting"""
    if use_typing:
        typing = ColorTyping()
        typing.type_glow_box(title, content_lines, title_color, border_color, 
                            content_color, blink_title, glow_border, width)
        return
    
    if width is None:
        width = get_terminal_width()
    
    box_width = min(width - 4, 90)
    box_width = max(box_width, 60)
    left_margin = max(0, (width - box_width) // 2)
    inner_width = box_width - 4
    
    TOP_LEFT = "╔"
    TOP_RIGHT = "╗"
    BOTTOM_LEFT = "╚"
    BOTTOM_RIGHT = "╝"
    HORIZONTAL = "═"
    VERTICAL = "║"
    T_LEFT = "╠"
    T_RIGHT = "╣"
    
    # Wrap content
    wrapped_lines = []
    for line in content_lines:
        if not line.strip():
            wrapped_lines.append("")
            continue
        clean_line = strip_ansi(line)
        if len(clean_line) > inner_width:
            wrapped_lines.extend(textwrap.wrap(line, inner_width, break_long_words=False))
        else:
            wrapped_lines.append(line)
    
    # Build box with proper colors
    glow_prefix = BOLD if glow_border else ""
    title_prefix = BOLD
    if blink_title:
        title_prefix += BLINK
    
    top = f"{' ' * left_margin}{glow_prefix}{border_color}{TOP_LEFT}{HORIZONTAL * (box_width - 2)}{TOP_RIGHT}{RESET}"
    title_text = f" {title} ".center(box_width - 2)
    title_line = f"{' ' * left_margin}{title_prefix}{title_color}{VERTICAL}{title_text}{VERTICAL}{RESET}"
    if blink_title:
        title_line += BLINK_OFF
    mid = f"{' ' * left_margin}{glow_prefix}{border_color}{T_LEFT}{HORIZONTAL * (box_width - 2)}{T_RIGHT}{RESET}"
    bot = f"{' ' * left_margin}{glow_prefix}{border_color}{BOTTOM_LEFT}{HORIZONTAL * (box_width - 2)}{BOTTOM_RIGHT}{RESET}"
    
    print(top)
    print(title_line)
    print(mid)
    
    for line in wrapped_lines:
        has_color = re.search(r'\x1b\[[0-9;]*m', line)
        clean_line = strip_ansi(line)
        padding_needed = inner_width - len(clean_line)
        if padding_needed < 0:
            padding_needed = 0
        
        left_border = f"{' ' * left_margin}{glow_prefix}{border_color}{VERTICAL} {RESET}"
        if has_color:
            print(f"{left_border}{line}{' ' * padding_needed} {glow_prefix}{border_color}{VERTICAL}{RESET}")
        else:
            print(f"{left_border}{content_color}{line.ljust(inner_width)}{RESET} {glow_prefix}{border_color}{VERTICAL}{RESET}")
    
    print(bot)
    print()

# ============================================================
# STATUS HELPERS
# ============================================================
def status_color(status: str) -> str:
    value = str(status or "").upper()
    if value in ("COMPLETE", "SUCCESS", "OK", "SECURE"):
        return LIGHTGREEN_EX
    if value in ("RUNNING", "SCANNING", "ACTIVE"):
        return LIGHTCYAN_EX
    if value in ("WARNING", "WARN", "IDLE"):
        return LIGHTYELLOW_EX
    if value in ("ERROR", "FAILED", "CRITICAL"):
        return LIGHTRED_EX
    return LIGHTWHITE_EX

def status_icon(status: str) -> str:
    value = str(status or "").upper()
    if value == "COMPLETE":
        return "✅"
    if value == "RUNNING":
        return "⏳"
    if value in ("ERROR", "FAILED", "CRITICAL"):
        return "❌"
    if value == "WARNING":
        return "⚠️"
    return "⏸"

def render_progress_bar(progress: int, width: int = 24) -> str:
    try:
        progress = int(max(0, min(100, progress)))
    except:
        progress = 0
    width = max(5, int(width))
    filled = int((progress / 100) * width)
    remaining = width - filled
    
    if progress >= 100:
        bar_color = LIGHTGREEN_EX
    elif progress >= 70:
        bar_color = LIGHTCYAN_EX
    elif progress >= 35:
        bar_color = LIGHTYELLOW_EX
    else:
        bar_color = LIGHTMAGENTA_EX
    
    return f"[{bar_color}{'█' * filled}{RESET}{DIM}{'░' * remaining}{RESET}]"

# ============================================================
# SCAN DIRECTORY
# ============================================================
def init_scan_directories(target):
    SCAN_ROOT = WORKSPACE / "scans"
    SCAN_ROOT.mkdir(exist_ok=True)
    safe_target = "".join(c for c in target if c.isalnum() or c in '.-_')
    TARGET_DIR = SCAN_ROOT / safe_target
    TARGET_DIR.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    SESSION_DIR = TARGET_DIR / f"scan_{timestamp}"
    SESSION_DIR.mkdir(exist_ok=True)
    return SESSION_DIR, timestamp

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def matrix_rain_effect(lines=3):
    chars = "01"
    width = get_terminal_width()
    for _ in range(lines):
        pieces = []
        count = min(max(width // 4, 1), 35)
        for _ in range(count):
            color = random.choice(MATRIX_COLORS)
            char = random.choice(chars)
            pieces.append(f"{color}{char}{RESET}")
        print(center_text("".join(pieces), width))
        time.sleep(0.03)

def check_command_exists(command):
    try:
        if os.name == "nt":
            result = subprocess.run(["where", command], capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(["which", command], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

# ============================================================
# WORKSPACE
# ============================================================
def get_workspace_dir() -> Path:
    home = Path(USER_HOME)
    workspace = home / "dsterminal_workspace"
    workspace.mkdir(exist_ok=True)
    return workspace

WORKSPACE = get_workspace_dir()
current_target = None
current_dashboard = None
REPORT_VERSION = "v4.0.0.113"
REPORT_MODULE = "DSTerminal Reconnaissance Module"

# ============================================================
# SOC DASHBOARD
# ============================================================
class SOCDashboard:
    def __init__(self):
        self.scan_metrics = {
            'ports': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'dns': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'whois': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'metasploit': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []}
        }
        self.lock = threading.Lock()
        self.typing = ColorTyping()
    
    def update_metric(self, scan_name, progress=None, status=None, findings=None, output_line=None):
        with self.lock:
            if scan_name not in self.scan_metrics:
                return
            metric = self.scan_metrics[scan_name]
            if progress is not None:
                metric['progress'] = max(0, min(100, int(progress)))
            if status is not None:
                metric['status'] = str(status).upper()
            if findings is not None:
                metric['findings'] = max(0, int(findings))
            if output_line is not None:
                metric['output'].append(str(output_line))
    
    def _get_col_data(self, scan_name, col_width):
        metrics = self.scan_metrics.get(scan_name, {})
        status = metrics.get('status', 'IDLE')
        progress = metrics.get('progress', 0)
        findings = metrics.get('findings', 0)
        s_color = status_color(status)
        icon = status_icon(status)
        bar = render_progress_bar(progress, max(10, min(22, col_width - 15)))
        return [
            f"{DIM}{scan_name.upper()}{RESET}",
            f"{s_color}{icon} {status}{RESET}",
            f"{LIGHTCYAN_EX}{bar}{RESET} {LIGHTWHITE_EX}{progress}%{RESET}",
            f"{LIGHTGREEN_EX}🔍 {findings}{RESET}"
        ]
    
    def render_dashboard(self):
        with self.lock:
            width = get_terminal_width()
            box_width = min(width - 4, 90)
            left_margin = max(0, (width - box_width) // 2)
            col_width = (box_width - 2) // 3
            border_color = LIGHTCYAN_EX
            
            print()
            print(f"{' ' * left_margin}{BOLD}{border_color}{BOX['tl']}{BOX['h'] * (box_width - 2)}{BOX['tr']}{RESET}")
            
            title = " [*] DSTerminal SOC REAL-TIME DASHBOARD [*] ".center(box_width - 2)
            print(f"{' ' * left_margin}{BOLD}{LIGHTCYAN_EX}{BOX['v']}{title}{BOX['v']}{RESET}")
            
            print(f"{' ' * left_margin}{BOLD}{border_color}{BOX['ml']}{BOX['h'] * (box_width - 2)}{BOX['mr']}{RESET}")
            
            headers = [("PORT SCAN", LIGHTGREEN_EX), ("DNS RESOLUTION", LIGHTCYAN_EX), ("WHOIS LOOKUP", LIGHTMAGENTA_EX)]
            header_line = f"{' ' * left_margin}{BOLD}{border_color}{BOX['v']}{RESET}"
            for header, h_color in headers:
                clean = header
                pad = max(0, col_width - len(clean))
                left_pad = pad // 2
                right_pad = pad - left_pad
                header_line += f"{' ' * left_pad}{h_color}{header}{RESET}{' ' * right_pad}"
            header_line += f"{BOLD}{border_color}{BOX['v']}{RESET}"
            print(header_line)
            
            print(f"{' ' * left_margin}{BOLD}{border_color}{BOX['ml']}{BOX['h'] * (box_width - 2)}{BOX['mr']}{RESET}")
            
            columns = [self._get_col_data('ports', col_width), self._get_col_data('dns', col_width), self._get_col_data('whois', col_width)]
            max_rows = max(len(col) for col in columns)
            
            for row_idx in range(max_rows):
                line = f"{' ' * left_margin}{BOLD}{border_color}{BOX['v']}{RESET}"
                for column in columns:
                    cell = column[row_idx] if row_idx < len(column) else ""
                    clean_cell = strip_ansi(cell)
                    if len(clean_cell) > col_width:
                        cell = fit_visible(cell, col_width)
                        clean_cell = strip_ansi(cell)
                    padding = max(0, col_width - len(clean_cell))
                    line += cell + " " * padding
                line += f"{BOLD}{border_color}{BOX['v']}{RESET}"
                print(line)
            
            print(f"{' ' * left_margin}{BOLD}{border_color}{BOX['bl']}{BOX['h'] * (box_width - 2)}{BOX['br']}{RESET}")
            print()
    
    def get_summary(self):
        with self.lock:
            return {name: {'status': metrics['status'], 'findings': metrics['findings']} for name, metrics in self.scan_metrics.items()}

# ============================================================
# BOX CHARACTERS
# ============================================================
BOX = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h": "═", "v": "║", "ml": "╠", "mr": "╣"
}

# ============================================================
# CINEMATIC SPINNER
# ============================================================
class CinematicSpinner:
    def __init__(self, dashboard, scan_name, target):
        self.dashboard = dashboard
        self.scan_name = scan_name
        self.target = target
        self.stop_event = threading.Event()
        self.start_time = None
        
    def animate_with_dashboard(self):
        self.start_time = time.time()
        last_update = 0
        while not self.stop_event.is_set():
            elapsed = int(time.time() - self.start_time)
            if time.time() - last_update > 0.3:
                progress = min(100, int((elapsed / 15) * 100))
                self.dashboard.update_metric(self.scan_name, progress=progress, status='RUNNING')
                self.dashboard.render_dashboard()
                last_update = time.time()
            time.sleep(0.1)
        self.dashboard.update_metric(self.scan_name, progress=100, status='COMPLETE')
        self.dashboard.render_dashboard()

# ============================================================
# SCAN ENGINE
# ============================================================
def save_output_to_file(session_dir, timestamp, scan_name, output_lines):
    output_file = session_dir / f"{scan_name}_{timestamp}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"DSTerminal Recon Scan - {scan_name.upper()}\n")
        f.write(f"Target: {current_target if current_target else 'Unknown'}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("="*60 + "\n\n")
        for line in output_lines:
            f.write(line + "\n")
    return output_file

def run_cinematic_scan(label, command, scan_name, dashboard, session_dir, timestamp, target):
    dashboard.update_metric(scan_name, progress=0, status='RUNNING', findings=0)
    spinner = CinematicSpinner(dashboard, scan_name, target)
    t = threading.Thread(target=spinner.animate_with_dashboard)
    t.daemon = True
    t.start()
    
    output_lines = []
    findings_count = 0
    typing = ColorTyping()
    
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            line = line.rstrip()
            output_lines.append(line)
            if scan_name == 'ports' and ('open' in line.lower() or 'tcp' in line.lower()):
                findings_count += 1
                dashboard.update_metric(scan_name, findings=findings_count)
            elif scan_name == 'dns' and ('address' in line.lower() or 'canonical' in line.lower()):
                findings_count += 1
                dashboard.update_metric(scan_name, findings=findings_count)
            elif scan_name == 'whois' and line.strip() and not line.startswith('%'):
                findings_count += 1
                dashboard.update_metric(scan_name, findings=findings_count)
            elif scan_name == 'metasploit' and ('exploit' in line.lower() or 'auxiliary' in line.lower()):
                findings_count += 1
                dashboard.update_metric(scan_name, findings=findings_count)
        process.wait()
    except:
        spinner.stop_event.set()
        t.join(timeout=1)
        dashboard.update_metric(scan_name, status='ERROR')
        return []
    finally:
        spinner.stop_event.set()
        t.join(timeout=1)
    
    if output_lines:
        output_file = save_output_to_file(session_dir, timestamp, scan_name, output_lines)
        display_lines = []
        for line in output_lines[:8]:
            display_lines.append(line[:70] + "..." if len(line) > 70 else line)
        if len(output_lines) > 8:
            display_lines.append(f"{DIM}... and {len(output_lines) - 8} more lines{RESET}")
        draw_centered_box(f"📊 SCAN RESULTS: {scan_name.upper()}", display_lines,
                          title_color=LIGHTMAGENTA_EX, border_color=CYAN,
                          content_color=LIGHTGREEN_EX, blink_title=True, use_typing=True)
        center_print(f"{CYAN}[+] Results saved to: {output_file}{RESET}")
        print()
    return output_lines

# ============================================================
# BANNER
# ============================================================
def show_banner(target):
    ascii_lines = [
        "  ██████╗ ███████╗██╗     ███████╗██╗  ██╗",
        "  ██╔══██╗██╔══██║██║     ██╔════╝██║  ██║",
        "  ██║  ██║███████║██║     ███████╗███████║",
        "  ██║  ██║██╔══██║██║     ╚════██║██╔══██║",
        "  ██████╔╝██║  ██║███████╗███████║██║  ██║",
        "  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝",
        "",
        f"  {BOLD}DSTERMINAL RECONNAISSANCE ENGINE{RESET}",
        f"  {CYAN}Target:{RESET} {LIGHTYELLOW_EX}{target}{RESET}",
        f"  {CYAN}Timestamp:{RESET} {DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}"
    ]
    draw_centered_box("⚡ DSTERMINAL RECON ENGINE ⚡", ascii_lines,
                      title_color=LIGHTCYAN_EX, border_color=CYAN,
                      content_color=LIGHTGREEN_EX, blink_title=True, use_typing=True)

# ============================================================
# ACTION PLAN
# ============================================================
def generate_action_plan(weaknesses, target):
    action_plan = []
    action_plan.append("=" * 70)
    action_plan.append("📋 COMPREHENSIVE ACTION PLAN - WEAKNESS MITIGATION")
    action_plan.append("=" * 70)
    action_plan.append("")
    action_plan.append(f"Target: {target}")
    action_plan.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    action_plan.append("")
    
    for i, weakness in enumerate(weaknesses, 1):
        title = weakness.get('title', 'Unknown Weakness')
        description = weakness.get('description', '')
        recommendation = weakness.get('recommendation', '')
        
        action_plan.append("")
        action_plan.append("=" * 70)
        action_plan.append(f"🔴 WEAKNESS #{i}: {title}")
        action_plan.append("=" * 70)
        action_plan.append("")
        action_plan.append("📖 DESCRIPTION:")
        action_plan.append(f"   {description}")
        action_plan.append("")
        action_plan.append("🚨 ATTACK SCENARIO:")
        action_plan.append("   " + "─" * 60)
        action_plan.append("   Step 1: Attacker identifies the weakness")
        action_plan.append("   Step 2: Attacker crafts exploit")
        action_plan.append("   Step 3: Attacker executes attack")
        action_plan.append("   Step 4: System compromise")
        action_plan.append("   " + "─" * 60)
        action_plan.append("")
        
        if "HTTP Without HTTPS" in title:
            action_plan.append("🔍 DETAILED ATTACK STEPS:")
            action_plan.append("   1. Attacker sets up fake Wi-Fi hotspot (MITM)")
            action_plan.append("   2. Victim connects to fake network")
            action_plan.append("   3. Attacker intercepts unencrypted HTTP traffic")
            action_plan.append("   4. Attacker captures login credentials and session cookies")
            action_plan.append("   5. Attacker gains access to university systems")
            action_plan.append("")
            action_plan.append("🛡️ MITIGATION STEPS:")
            action_plan.append("   1. Install SSL certificate (Let's Encrypt)")
            action_plan.append("   2. Configure HTTPS on web server")
            action_plan.append("   3. Force HTTP to HTTPS redirect (301)")
            action_plan.append("   4. Enable HSTS header")
            action_plan.append("   5. Monitor SSL certificate expiry")
            action_plan.append("")
            action_plan.append("💻 COMMANDS:")
            action_plan.append("   sudo apt-get update")
            action_plan.append("   sudo apt-get install certbot python3-certbot-nginx -y")
            action_plan.append(f"   sudo certbot --nginx -d {target} -d www.{target}")
            action_plan.append("   sudo systemctl enable certbot.timer")
            action_plan.append("   sudo systemctl start certbot.timer")
            action_plan.append("")
            
        elif "Exposed Contact Information" in title:
            action_plan.append("🔍 DETAILED ATTACK STEPS (Social Engineering):")
            action_plan.append("   1. Attacker searches WHOIS for contact details")
            action_plan.append("   2. Identifies key staff members and their roles")
            action_plan.append("   3. Crafts personalized spear-phishing email")
            action_plan.append("   4. Email appears to come from legitimate source")
            action_plan.append("   5. Employee trusts email and clicks malicious link")
            action_plan.append("   6. Credentials stolen or malware installed")
            action_plan.append("")
            action_plan.append("🛡️ MITIGATION STEPS:")
            action_plan.append("   1. Contact domain registrar (MW Registry)")
            action_plan.append("   2. Enable WHOIS privacy protection")
            action_plan.append("   3. Use generic contact emails (admin@domain)")
            action_plan.append("   4. Remove personal phone numbers")
            action_plan.append("   5. Train staff on social engineering awareness")
            action_plan.append("")
            action_plan.append("📧 RECOMMENDED CONTACTS:")
            action_plan.append("   Admin: admin@domain.com")
            action_plan.append("   Tech: tech@domain.com")
            action_plan.append("   Billing: billing@domain.com")
            action_plan.append("")
            
        elif "SSH Service Detected" in title:
            action_plan.append("🔍 DETAILED ATTACK STEPS:")
            action_plan.append("   1. Attacker scans for open SSH port 22")
            action_plan.append("   2. Attacker performs brute force attack")
            action_plan.append("   3. Weak credentials are compromised")
            action_plan.append("   4. Attacker gains shell access to server")
            action_plan.append("")
            action_plan.append("🛡️ MITIGATION STEPS:")
            action_plan.append("   1. Use key-based authentication only")
            action_plan.append("   2. Disable root login")
            action_plan.append("   3. Change default SSH port")
            action_plan.append("   4. Implement fail2ban")
            action_plan.append("   5. Use strong passwords or MFA")
            action_plan.append("")
            action_plan.append("💻 COMMANDS:")
            action_plan.append("   sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config")
            action_plan.append("   sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config")
            action_plan.append("   sudo sed -i 's/^#*Port 22/Port 2222/' /etc/ssh/sshd_config")
            action_plan.append("   sudo systemctl restart sshd")
            action_plan.append("")
            
        elif "SMB Service Detected" in title:
            action_plan.append("🔍 DETAILED ATTACK STEPS:")
            action_plan.append("   1. Attacker scans for SMB ports 445/139")
            action_plan.append("   2. Attacker uses known exploits (EternalBlue)")
            action_plan.append("   3. Attacker gains remote code execution")
            action_plan.append("   4. Ransomware deployment")
            action_plan.append("")
            action_plan.append("🛡️ MITIGATION STEPS:")
            action_plan.append("   1. Apply security patches immediately")
            action_plan.append("   2. Disable SMBv1")
            action_plan.append("   3. Use SMB encryption")
            action_plan.append("   4. Restrict access to trusted IPs")
            action_plan.append("   5. Monitor SMB logs")
            action_plan.append("")
            action_plan.append("💻 COMMANDS:")
            action_plan.append("   # Disable SMBv1 on Windows")
            action_plan.append("   Set-SmbServerConfiguration -EnableSMB1Protocol $false")
            action_plan.append("   # Enable SMB encryption")
            action_plan.append("   Set-SmbServerConfiguration -EncryptData $true")
            action_plan.append("")
            
        action_plan.append("✅ RECOMMENDATION:")
        action_plan.append(f"   {recommendation}")
        action_plan.append("")
        action_plan.append("📊 VERIFICATION:")
        action_plan.append("   After implementing fixes, verify by running scan again")
        action_plan.append("   " + "─" * 60)
        action_plan.append("")
    
    action_plan.append("")
    action_plan.append("=" * 70)
    action_plan.append("📊 EXECUTIVE SUMMARY")
    action_plan.append("=" * 70)
    action_plan.append("")
    action_plan.append(f"Total Weaknesses Found: {len(weaknesses)}")
    action_plan.append("")
    
    critical = sum(1 for w in weaknesses if "HTTP" in w['title'] or "SSH" in w['title'])
    high = sum(1 for w in weaknesses if "SMB" in w['title'] or "DNS" in w['title'])
    medium = sum(1 for w in weaknesses if "Contact" in w['title'])
    
    action_plan.append("🔴 CRITICAL (Immediate Action Required):")
    action_plan.append(f"   • {critical} weakness(es) requiring immediate attention")
    action_plan.append("")
    action_plan.append("🟡 HIGH (Action Within 1 Week):")
    action_plan.append(f"   • {high} weakness(es) requiring attention")
    action_plan.append("")
    action_plan.append("🟢 MEDIUM (Action Within 1 Month):")
    action_plan.append(f"   • {medium} weakness(es) requiring attention")
    action_plan.append("")
    
    action_plan.append("📋 NEXT STEPS:")
    action_plan.append("   1. Prioritize CRITICAL weaknesses")
    action_plan.append("   2. Create ticket for each weakness")
    action_plan.append("   3. Assign to appropriate team member")
    action_plan.append("   4. Set deadlines for completion")
    action_plan.append("   5. Verify fixes by re-scanning")
    action_plan.append("   6. Document all changes")
    action_plan.append("")
    
    action_plan.append("=" * 70)
    action_plan.append("✅ ACTION PLAN GENERATED SUCCESSFULLY")
    action_plan.append("=" * 70)
    return action_plan

# ============================================================
# WEAKNESS ANALYSIS
# ============================================================
def analyze_weaknesses(scan_results, target):
    weaknesses = []
    ports_data = scan_results.get('ports', {})
    port_output = ' '.join(ports_data.get('output', []))
    
    if '80/tcp' in port_output and '443/tcp' not in port_output:
        weaknesses.append({
            'title': 'HTTP Without HTTPS',
            'description': f'Port 80 (HTTP) is open but port 443 (HTTPS) is not detected. Traffic to {target} is not encrypted.',
            'recommendation': 'Enable HTTPS on the web server and redirect all HTTP traffic to HTTPS using 301 redirects.'
        })
    
    if '22/tcp' in port_output:
        weaknesses.append({
            'title': 'SSH Service Detected',
            'description': f'SSH port 22 is open on {target}. SSH is a common attack vector.',
            'recommendation': 'Ensure SSH uses key-based authentication, disable root login, and consider changing default port.'
        })
    
    if '445/tcp' in port_output or '139/tcp' in port_output:
        weaknesses.append({
            'title': 'SMB Service Detected',
            'description': f'SMB ports 445/139 are open on {target}. SMB is frequently targeted by ransomware.',
            'recommendation': 'Ensure SMB is properly patched, use SMB encryption, and restrict access to trusted IPs.'
        })
    
    dns_data = scan_results.get('dns', {})
    dns_output = ' '.join(dns_data.get('output', []))
    
    if 'NXDOMAIN' in dns_output or 'not found' in dns_output:
        weaknesses.append({
            'title': 'DNS Resolution Issue',
            'description': f'DNS resolution for {target} returned an error. This may indicate DNS misconfiguration.',
            'recommendation': 'Verify DNS records are correctly configured and propagate properly.'
        })
    
    whois_data = scan_results.get('whois', {})
    whois_output = ' '.join(whois_data.get('output', []))
    
    if '@' in whois_output and 'phone' in whois_output.lower():
        weaknesses.append({
            'title': 'Exposed Contact Information',
            'description': f'WHOIS data for {target} exposes email addresses and phone numbers that could be used for social engineering.',
            'recommendation': 'Enable WHOIS privacy protection through your domain registrar to mask contact details.'
        })
    
    if not weaknesses:
        weaknesses.append({
            'title': 'No Critical Weaknesses Detected',
            'description': f'Reconnaissance of {target} did not identify any critical security weaknesses.',
            'recommendation': 'Continue regular security assessments and maintain good security hygiene.'
        })
    
    return weaknesses

# ============================================================
# PDF REPORT
# ============================================================
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as reportlab_colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def generate_pdf_report(target, session_dir, total_findings, scan_results, weaknesses, action_plan):
    if not PDF_AVAILABLE:
        print(f"{YELLOW}⚠️ ReportLab not installed. PDF generation skipped.{RESET}")
        return None
    
    try:
        pdf_file = session_dir / f"recon_report_{target.replace('.', '_')}.pdf"
        
        doc = SimpleDocTemplate(str(pdf_file), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=28,
                                     textColor=reportlab_colors.HexColor('#00ff00'), alignment=TA_CENTER,
                                     spaceAfter=20, fontName='Helvetica-Bold')
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=14,
                                        textColor=reportlab_colors.HexColor('#00ccff'), alignment=TA_CENTER, spaceAfter=30)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=16,
                                       textColor=reportlab_colors.HexColor('#00aaff'), spaceAfter=10, spaceBefore=10,
                                       fontName='Helvetica-Bold')
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10,
                                    textColor=reportlab_colors.HexColor('#ffffff'), alignment=TA_LEFT, spaceAfter=4)
        
        def add_watermark(canvas_obj, doc_obj):
            canvas_obj.saveState()
            canvas_obj.setFillColor(reportlab_colors.HexColor('#0a0a0a'))
            canvas_obj.rect(0, 0, 595, 842, fill=1)
            canvas_obj.setFont('Helvetica-Bold', 60)
            canvas_obj.setFillColor(reportlab_colors.HexColor('#1a3a1a'))
            canvas_obj.setFillAlpha(0.15)
            page_width, page_height = A4
            canvas_obj.translate(page_width / 2, page_height / 2)
            canvas_obj.rotate(45)
            canvas_obj.drawCentredString(0, 0, "DSTERMINAL")
            canvas_obj.restoreState()
        
        story.append(Paragraph("DSTERMINAL RECONNAISSANCE REPORT", title_style))
        story.append(Paragraph(f"{REPORT_MODULE} {REPORT_VERSION}", subtitle_style))
        story.append(Spacer(1, 0.2*inch))
        
        metadata_data = [
            ["🎯 Target:", target],
            ["📅 Scan Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["📊 Total Findings:", str(total_findings)]
        ]
        meta_table = Table(metadata_data, colWidths=[120, 350])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), reportlab_colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (0, -1), reportlab_colors.HexColor('#00ff00')),
            ('BACKGROUND', (1, 0), (1, -1), reportlab_colors.HexColor('#0d1117')),
            ('TEXTCOLOR', (1, 0), (1, -1), reportlab_colors.HexColor('#ffffff')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, reportlab_colors.HexColor('#00ff00')),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("┌─ SCAN RESULTS SUMMARY ─┐", heading_style))
        for scan_name, data in scan_results.items():
            if data:
                status = data.get('status', 'UNKNOWN')
                findings = data.get('findings', 0)
                story.append(Paragraph(f"  {scan_name.upper()}: {status} (Findings: {findings})", body_style))
        story.append(Spacer(1, 0.2*inch))
        
        if weaknesses:
            story.append(Paragraph("┌─ WEAKNESSES & RECOMMENDATIONS ─┐", heading_style))
            for weakness in weaknesses:
                story.append(Paragraph(f"  ⚠️ {weakness['title']}", 
                    ParagraphStyle('WeakTitle', parent=styles['Normal'], textColor=reportlab_colors.HexColor('#ff8800'), fontName='Helvetica-Bold', fontSize=11)))
                story.append(Paragraph(f"     {weakness['description'][:200]}...", body_style))
                story.append(Paragraph(f"     💡 {weakness['recommendation'][:200]}...", body_style))
                story.append(Spacer(1, 0.05*inch))
        
        story.append(PageBreak())
        
        if action_plan:
            story.append(Paragraph("┌─ COMPREHENSIVE ACTION PLAN ─┐", heading_style))
            for line in action_plan[:25]:
                if line.startswith("="):
                    story.append(Paragraph(f"  {line}", body_style))
                elif line.startswith("📋") or line.startswith("📊"):
                    story.append(Paragraph(f"  {line}", 
                        ParagraphStyle('ActionHeader', parent=styles['Normal'], textColor=reportlab_colors.HexColor('#00ccff'), fontName='Helvetica-Bold', fontSize=11)))
                else:
                    story.append(Paragraph(f"  {line}", body_style))
        
        story.append(PageBreak())
        
        whois_data = scan_results.get('whois', {})
        whois_output = whois_data.get('output', [])
        if whois_output:
            story.append(Paragraph("┌─ FULL WHOIS DATA ─┐", heading_style))
            line_count = 0
            for line in whois_output:
                if line_count > 60:
                    story.append(Paragraph(f"  ... and {len(whois_output) - 60} more lines", body_style))
                    break
                if line.strip() and not (line.startswith('%') and 'Tim' not in line and 'Whois' not in line):
                    story.append(Paragraph(f"  {line[:100]}", body_style))
                    line_count += 1
        
        doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
        return pdf_file
    except Exception as e:
        print(f"{RED}❌ PDF generation failed: {str(e)}{RESET}")
        return None

# ============================================================
# HTML REPORT
# ============================================================
def generate_html_report(target, session_dir, total_findings, scan_results, weaknesses, action_plan):
    try:
        html_file = session_dir / f"recon_report_{target.replace('.', '_')}.html"
        
        scan_results_html = ""
        for scan_name, data in scan_results.items():
            status = data.get('status', 'UNKNOWN')
            findings = data.get('findings', 0)
            status_color = "#00ff00" if status == "COMPLETE" else "#ffcc00" if status == "RUNNING" else "#ff0000"
            
            if scan_name == 'whois':
                output_lines = data.get('output', [])
                whois_display = "\n".join(output_lines) if output_lines else "No WHOIS data available"
                scan_results_html += f"""
            <div class="scan-result whois-result">
                <div class="scan-header">
                    <span class="scan-name">{scan_name.upper()}</span>
                    <span class="scan-status" style="color:{status_color}">{status}</span>
                    <span class="scan-findings">🔍 {findings} lines</span>
                </div>
                <div class="scan-output">
                    <div class="whois-data"><pre>{whois_display}</pre></div>
                    <div class="data-count">Total WHOIS lines: {len(output_lines)}</div>
                </div>
            </div>
            """
            else:
                output_lines = data.get('output', [])
                display_lines = output_lines[:30] if output_lines else ["No output captured"]
                scan_results_html += f"""
            <div class="scan-result">
                <div class="scan-header">
                    <span class="scan-name">{scan_name.upper()}</span>
                    <span class="scan-status" style="color:{status_color}">{status}</span>
                    <span class="scan-findings">🔍 {findings} findings</span>
                </div>
                <div class="scan-output"><pre>{"\n".join(display_lines)}</pre>
                {f'<div class="more-lines">... and {len(output_lines) - 30} more lines</div>' if len(output_lines) > 30 else ''}</div>
            </div>
            """
        
        weaknesses_html = ""
        for w in weaknesses:
            weaknesses_html += f"""
            <div class="weakness">
                <div class="weakness-title">⚠️ {w['title']}</div>
                <div class="weakness-desc">{w['description']}</div>
                <div class="weakness-recommendation">💡 {w['recommendation']}</div>
            </div>
            """
        
        action_plan_html = ""
        if action_plan:
            action_plan_html = '<div class="section action-plan"><h2>📋 COMPREHENSIVE ACTION PLAN</h2><div class="action-plan-content">'
            for line in action_plan:
                if line.startswith("="):
                    action_plan_html += f'<div class="separator">{line}</div>'
                elif line.startswith("📋") or line.startswith("📊"):
                    action_plan_html += f'<div class="action-header">{line}</div>'
                elif line.startswith("🔴"):
                    action_plan_html += f'<div class="critical-header">{line}</div>'
                elif line.startswith("🟡"):
                    action_plan_html += f'<div class="high-header">{line}</div>'
                elif line.startswith("🟢"):
                    action_plan_html += f'<div class="medium-header">{line}</div>'
                else:
                    action_plan_html += f'<div class="action-body">{line}</div>'
            action_plan_html += '</div></div>'
        
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>DSTerminal Reconnaissance Report - {target}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Courier New',monospace;background:#0a0a0a;color:#00ff00;padding:20px;}}
.container{{max-width:1200px;margin:0 auto;background:rgba(10,20,10,0.95);padding:30px;border-radius:15px;border:1px solid rgba(0,255,0,0.1);}}
.header{{text-align:center;border-bottom:2px solid rgba(0,255,0,0.2);padding-bottom:20px;margin-bottom:30px;}}
.header h1{{color:#00ff00;font-size:2.2em;text-shadow:0 0 20px rgba(0,255,0,0.3);letter-spacing:3px;}}
.header .subtitle{{color:#00cc88;font-size:1em;opacity:0.8;margin-top:5px;letter-spacing:2px;}}
.section{{background:rgba(0,20,0,0.8);border-radius:10px;padding:20px;margin-bottom:20px;border-left:3px solid #00ff00;}}
.section h2{{color:#00ccff;font-size:1.3em;margin-bottom:15px;letter-spacing:2px;border-bottom:1px solid rgba(0,204,255,0.1);padding-bottom:10px;}}
.summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin:15px 0;}}
.summary-card{{background:rgba(0,255,0,0.03);padding:15px;border-radius:8px;text-align:center;border:1px solid rgba(0,255,0,0.08);}}
.summary-card .value{{font-size:28px;font-weight:bold;color:#00ff00;}}
.summary-card .label{{font-size:11px;color:#446644;margin-top:5px;}}
.scan-result{{background:rgba(0,30,0,0.5);padding:15px;margin:10px 0;border-radius:8px;border-left:3px solid #00cc88;}}
.whois-result{{border-left-color:#ff6600;background:rgba(30,20,0,0.3);}}
.scan-header{{display:flex;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;}}
.scan-name{{color:#00ccff;font-weight:bold;font-size:1.1em;}}
.scan-status{{color:#00ff00;font-weight:bold;}}
.scan-findings{{color:#ffcc00;}}
.scan-output pre{{color:#88cc88;font-size:0.8em;background:rgba(0,10,0,0.5);padding:10px;border-radius:5px;overflow-x:auto;max-height:400px;overflow-y:auto;white-space:pre-wrap;word-wrap:break-word;}}
.whois-data pre{{color:#ffaa00;background:rgba(30,20,0,0.3);max-height:600px;border-left:2px solid #ff6600;}}
.weakness{{background:rgba(255,100,0,0.05);padding:15px;margin:10px 0;border-radius:8px;border-left:3px solid #ff6600;}}
.weakness-title{{color:#ff6600;font-weight:bold;font-size:1em;}}
.weakness-desc{{color:#ccaa88;margin:5px 0;font-size:0.9em;}}
.weakness-recommendation{{color:#00ff88;margin-top:5px;font-size:0.9em;}}
.action-plan{{border-left-color:#00ccff;background:rgba(0,50,80,0.2);}}
.action-header{{color:#00ccff;font-weight:bold;font-size:1.1em;margin-top:10px;margin-bottom:5px;}}
.critical-header{{color:#ff0000;font-weight:bold;margin-top:8px;}}
.high-header{{color:#ff6600;font-weight:bold;margin-top:8px;}}
.medium-header{{color:#ffcc00;font-weight:bold;margin-top:8px;}}
.action-body{{color:#ccffcc;margin:3px 0;}}
.data-count{{color:#ffcc00;font-size:0.8em;margin-top:5px;padding:5px 10px;background:rgba(255,204,0,0.05);border-radius:3px;display:inline-block;}}
.footer{{text-align:center;margin-top:30px;padding-top:20px;border-top:1px solid rgba(0,255,0,0.05);color:#224422;font-size:0.7em;letter-spacing:1px;}}
</style></head>
<body>
<div class="container">
<div class="header"><h1>██████ DSTERMINAL RECON ██████</h1><div class="subtitle">{REPORT_MODULE} {REPORT_VERSION}</div>
<div class="meta">🎯 Target: {target} | 📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div></div>
<div class="section"><h2>📊 SCAN SUMMARY</h2>
<div class="summary-grid">
<div class="summary-card"><div class="value">{len(scan_results)}</div><div class="label">Scans Performed</div></div>
<div class="summary-card"><div class="value">{total_findings}</div><div class="label">Total Findings</div></div>
<div class="summary-card"><div class="value">{sum(1 for s in scan_results.values() if s.get('status') == 'COMPLETE')}</div><div class="label">Completed Scans</div></div>
<div class="summary-card"><div class="value">{session_dir}</div><div class="label">Session Directory</div></div>
</div></div>
<div class="section"><h2>🔍 SCAN RESULTS</h2>{scan_results_html}</div>
<div class="section"><h2>⚠️ WEAKNESSES & RECOMMENDATIONS</h2>{weaknesses_html if weaknesses_html else '<div style="color: #446644;">✅ No significant weaknesses detected.</div>'}</div>
{action_plan_html}
<div class="footer">{REPORT_MODULE} {REPORT_VERSION} | © 2024 DSTerminal Security Suite</div>
</div></body></html>"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return html_file
    except Exception as e:
        print(f"{RED}❌ HTML generation failed: {str(e)}{RESET}")
        return None

# ============================================================
# MAIN RECON FUNCTION
# ============================================================
def run_recon(target=None):
    global current_target, current_dashboard
    
    if target is None:
        target = get_target_from_args()
    if target is None:
        print_colored("[!] No target specified. Usage: run_recon('<target>')", RED)
        return False
    
    current_target = target
    clear_screen()
    matrix_rain_effect(3)
    time.sleep(0.5)
    show_banner(target)
    time.sleep(0.5)
    
    session_dir, timestamp = init_scan_directories(target)
    
    info_lines = [
        f"{BOLD}🎯 Target:{RESET} {LIGHTYELLOW_EX}{target}{RESET}",
        f"{BOLD}📁 Workspace:{RESET} {DIM}{WORKSPACE}{RESET}",
        f"{BOLD}📂 Session:{RESET} {DIM}{session_dir}{RESET}"
    ]
    draw_centered_box("📋 SCAN CONFIGURATION", info_lines,
                      title_color=LIGHTCYAN_EX, border_color=CYAN,
                      content_color=LIGHTGREEN_EX, use_typing=True)
    time.sleep(0.5)
    
    dashboard = SOCDashboard()
    current_dashboard = dashboard
    dashboard.render_dashboard()
    
    scans = [
        ("🔍 PORT SCAN", f"nmap -F {target}", "ports"),
        ("🔍 DNS RESOLUTION", f"nslookup {target}", "dns"),
        ("🔍 WHOIS LOOKUP", f"whois {target}", "whois"),
    ]
    
    for label, cmd, scan_name in scans:
        cmd_name = cmd.split()[0]
        if check_command_exists(cmd_name) or cmd_name in ['nslookup', 'whois']:
            run_cinematic_scan(label, cmd, scan_name, dashboard, session_dir, timestamp, target)
        else:
            center_print(f"{BOLD}{YELLOW}[!] {cmd_name} not found - skipping{RESET}")
            dashboard.update_metric(scan_name, status='ERROR', findings=0)
        time.sleep(0.3)
        matrix_rain_effect(1)
    
    if check_command_exists("msfconsole"):
        run_cinematic_scan("🔍 METASPLOIT SEARCH",
                          f'msfconsole -q -x "search {target}; exit"',
                          "metasploit", dashboard, session_dir, timestamp, target)
    else:
        center_print(f"{BOLD}{YELLOW}[!] Metasploit not found - skipping{RESET}")
        dashboard.update_metric('metasploit', status='ERROR', findings=0)
    
    summary_file = session_dir / f"summary_{timestamp}.txt"
    summary = dashboard.get_summary()
    total_findings = 0
    scan_results = {}
    
    for scan_name in dashboard.scan_metrics.keys():
        output_file = session_dir / f"{scan_name}_{timestamp}.txt"
        output_lines = []
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                output_lines = f.read().splitlines()
        scan_results[scan_name] = {
            'status': summary[scan_name]['status'],
            'findings': summary[scan_name]['findings'],
            'output': output_lines
        }
        total_findings += summary[scan_name]['findings']
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("DSTERMINAL RECONNAISSANCE SUMMARY\n")
        f.write("="*60 + "\n\n")
        f.write(f"Target: {target}\n")
        f.write(f"Scan Time: {datetime.now().isoformat()}\n")
        f.write(f"Workspace: {WORKSPACE}\n")
        f.write(f"Session Directory: {session_dir}\n\n")
        f.write("-"*60 + "\n")
        f.write("SCAN RESULTS SUMMARY\n")
        f.write("-"*60 + "\n\n")
        for scan_name, metrics in summary.items():
            f.write(f"{scan_name.upper()}:\n")
            f.write(f"  Status: {metrics['status']}\n")
            f.write(f"  Findings: {metrics['findings']}\n")
            output_file = session_dir / f"{scan_name}_{timestamp}.txt"
            if output_file.exists():
                f.write(f"  Output: {output_file}\n")
            f.write("\n")
        f.write("-"*60 + "\n")
        f.write(f"TOTAL FINDINGS: {total_findings}\n")
        f.write("="*60 + "\n")
    
    weaknesses = analyze_weaknesses(scan_results, target)
    action_plan = generate_action_plan(weaknesses, target)
    action_plan_file = session_dir / f"action_plan_{timestamp}.txt"
    with open(action_plan_file, 'w', encoding='utf-8') as f:
        for line in action_plan:
            f.write(line + "\n")
    
    print_colored("\n[+] Generating reports with action plan...", CYAN)
    
    html_file = generate_html_report(target, session_dir, total_findings, scan_results, weaknesses, action_plan)
    if html_file:
        center_print(f"{GREEN}✅ HTML Report: {html_file}{RESET}")
    
    pdf_file = generate_pdf_report(target, session_dir, total_findings, scan_results, weaknesses, action_plan)
    if pdf_file:
        center_print(f"{GREEN}✅ PDF Report: {pdf_file}{RESET}")
    
    print("\n" * 2)
    draw_centered_box("📋 ACTION PLAN GENERATED",
                     [f"Action Plan saved to: {action_plan_file}",
                      f"Weaknesses Found: {len(weaknesses)}",
                      "See PDF/HTML reports for complete details"],
                     title_color=LIGHTYELLOW_EX, border_color=CYAN,
                     content_color=LIGHTGREEN_EX, blink_title=True, use_typing=True)
    
    print("\n" * 2)
    final_lines = [f"Total Findings: {total_findings}",
                   f"Weaknesses Found: {len(weaknesses)}",
                   f"Scan Session: {session_dir}",
                   f"Summary Report: {summary_file}",
                   f"Action Plan: {action_plan_file}"]
    if pdf_file:
        final_lines.append(f"PDF Report: {pdf_file}")
    if html_file:
        final_lines.append(f"HTML Report: {html_file}")
    
    draw_centered_box("✅ INFORMATION GATHERING COMPLETE", final_lines,
                      title_color=LIGHTGREEN_EX, border_color=GREEN,
                      content_color=LIGHTCYAN_EX, blink_title=True, use_typing=True)
    
    dashboard.render_dashboard()
    center_print(f"{BOLD}{LIGHTCYAN_EX}{'═' * min(get_terminal_width() - 4, 80)}{RESET}")
    center_print(f"{BOLD}{LIGHTCYAN_EX}[+] DSTERMINAL SOC - RECONNAISSANCE COMPLETE [+]{RESET}")
    matrix_rain_effect(2)
    print()
    return True

# ============================================================
# GET TARGET FROM ARGS
# ============================================================
def get_target_from_args():
    if len(sys.argv) < 2:
        return None
    return sys.argv[1]

# ============================================================
# RECON MENU
# ============================================================
def recon_menu():
    draw_centered_box("🎯 RECONNAISSANCE MENU",
                     [f"{LIGHTGREEN_EX}[1]{RESET} Quick Scan (Ports, DNS, WHOIS)",
                      f"{LIGHTGREEN_EX}[2]{RESET} Full Scan (with Metasploit)",
                      f"{LIGHTGREEN_EX}[3]{RESET} Custom Target",
                      f"{LIGHTRED_EX}[0]{RESET} Exit"],
                     title_color=LIGHTCYAN_EX, border_color=CYAN,
                     content_color=LIGHTGREEN_EX, blink_title=True, use_typing=True)
    
    choice = input(f"\n{LIGHTYELLOW_EX}Select option: {RESET}").strip()
    if choice in ["1", "2", "3"]:
        target = input(f"{LIGHTCYAN_EX}Enter target (IP or domain): {RESET}").strip()
        if target:
            run_recon(target)
        else:
            print_colored("[!] No target specified", RED)
    elif choice == "0":
        print_colored("[*] Exiting recon menu", YELLOW)
    else:
        print_colored("[!] Invalid option", RED)

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    target = get_target_from_args()
    if target:
        run_recon(target)
    else:
        recon_menu()