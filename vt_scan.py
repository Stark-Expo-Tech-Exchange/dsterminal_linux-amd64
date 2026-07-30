"""
DSTerminal - VirusTotal Integration Module
Enhanced Cinematic SOC Dashboard with Hacking-Style Animation & Auto-Typing
"""

import os
import sys
import re
import time
import json
import shutil
import random
import hashlib
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =========================================================
# ANSI COLOR STRIPPING FOR RESPONSIVE LAYOUT CALCULATIONS
# =========================================================

ANSI_ESCAPE_PATTERN = re.compile(
    r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
)

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from terminal strings"""
    return ANSI_ESCAPE_PATTERN.sub('', text)

# -------------------------------
# GLOWING COLORS & STYLING (MOVED BEFORE AutoTypeEngine)
# -------------------------------

RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
BLINK = '\033[5m'

CYAN = '\033[96m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
ORANGE = '\033[38;5;208m'
PURPLE = '\033[38;5;129m'

BRIGHT_CYAN = '\033[96;1m'
BRIGHT_GREEN = '\033[92;1m'
BRIGHT_RED = '\033[91;1m'
BRIGHT_YELLOW = '\033[93;1m'
BRIGHT_MAGENTA = '\033[95;1m'
BRIGHT_BLUE = '\033[94;1m'

# Animation frames
SCANNING_FRAMES = ["🔍", "🔎", "📡", "🛰️", "⚡", "💀", "🎯", "⚠️", "🔬", "🧬", "✨", "🌟"]
THREAT_FRAMES = ["◐", "◓", "◑", "◒", "⦾", "⦿", "⬤", "○", "⟳", "⟲", "↻", "↺", "🌀", "⚡"]
GLOW_FRAMES = ["✨", "⭐", "🌟", "💫", "⚡"]

# -------------------------------
# AUTO-TYPING ENGINE
# -------------------------------

class AutoTypeEngine:
    """Handles auto-typing effects with constant delay"""
    
    def __init__(self, delay: float = 0.03):
        self.delay = delay
        self.is_typing = False
        self.type_queue = []
        
    def type_text(self, text: str, color: str = "", end: str = "\n", delay: float = None):
        """Type text with auto-typing effect and constant delay"""
        if delay is None:
            delay = self.delay
            
        if color:
            sys.stdout.write(color)
            
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
            
        if color:
            sys.stdout.write(RESET)
        if end:
            sys.stdout.write(end)
        sys.stdout.flush()
    
    def type_multiline(self, lines: List[str], color: str = "", delay: float = None):
        """Type multiple lines with auto-typing effect"""
        for line in lines:
            self.type_text(line, color=color, end="\n", delay=delay)
            time.sleep(0.05)  # Small pause between lines
    
    def type_banner(self, banner_lines: List[str], color: str = BRIGHT_GREEN, delay: float = None):
        """Type a banner with auto-typing effect"""
        for line in banner_lines:
            self.type_text(line, color=color, end="\n", delay=delay)
            time.sleep(0.03)
    
    def type_with_cursor(self, text: str, color: str = "", delay: float = None):
        """Type text with a blinking cursor effect"""
        if delay is None:
            delay = self.delay
            
        if color:
            sys.stdout.write(color)
            
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
            
        # Blinking cursor effect
        for _ in range(3):
            sys.stdout.write('█')
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b \b')
            sys.stdout.flush()
            time.sleep(0.1)
            
        if color:
            sys.stdout.write(RESET)
        sys.stdout.flush()
    
    def type_progress(self, progress: int, total: int, message: str = "", color: str = BRIGHT_CYAN):
        """Type progress with auto-typing effect"""
        bar_length = 40
        filled = int(bar_length * progress / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        percent = int(progress / total * 100)
        
        text = f"\r{color}[{bar}] {percent:3d}% {message}{RESET}"
        sys.stdout.write(text)
        sys.stdout.flush()

# -------------------------------
# WORKSPACE DIRECTORY SETUP
# -------------------------------

def get_workspace_dir() -> Path:
    """Get the DSTerminal workspace directory"""
    home = Path.home()
    workspace = home / "dsterminal_workspace"
    workspace.mkdir(exist_ok=True)
    
    # Create subdirectories
    (workspace / "integrity_reports").mkdir(exist_ok=True)
    (workspace / "network_reports").mkdir(exist_ok=True)
    (workspace / "compliance_reports").mkdir(exist_ok=True)
    (workspace / "vt_reports").mkdir(exist_ok=True)
    (workspace / "quarantine").mkdir(exist_ok=True)
    (workspace / "logs").mkdir(exist_ok=True)
    (workspace / "scans").mkdir(exist_ok=True)
    (workspace / "soc_alerts").mkdir(exist_ok=True)
    
    return workspace

WORKSPACE = get_workspace_dir()
VT_REPORTS_DIR = WORKSPACE / "vt_reports"
QUARANTINE_DIR = WORKSPACE / "quarantine"
SOC_ALERTS_DIR = WORKSPACE / "soc_alerts"
SCAN_HISTORY_FILE = WORKSPACE / "scan_history.json"

# -------------------------------
# CONFIGURATION
# -------------------------------

CONFIG = {
    'VT_API_KEY': os.environ.get('VT_API_KEY', '957166d424812a397e328022b84594a8c02757814f6c04518dce7e81179b4b79'),
    'SOC_OPERATOR_NAME': None,
    'SOC_SESSION_ID': None,
}

def sync_operator_session(operator_name: str, session_id: str):
    """Sync operator identity from DSTerminal main app"""
    CONFIG['SOC_OPERATOR_NAME'] = operator_name
    CONFIG['SOC_SESSION_ID'] = session_id

# -------------------------------
# TERMINAL UTILITIES
# -------------------------------

def get_terminal_width() -> int:
    try:
        return shutil.get_terminal_size((140, 20)).columns
    except:
        return 140

def center_text(text: str, width: int = None) -> str:
    if width is None:
        width = get_terminal_width()
    
    clean_text = strip_ansi(text)
    padding = max(0, (width - len(clean_text)) // 2)
    return " " * padding + text

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def matrix_rain(duration: float = 0.5, intensity: int = 3):
    chars = "01アイウエオカキクケコサシスセソタチツテト"
    width = get_terminal_width()
    
    for _ in range(intensity):
        line = ""
        for _ in range(width // 4):
            color = random.choice([GREEN, CYAN, MAGENTA, WHITE, BRIGHT_GREEN])
            char = random.choice(chars)
            if random.random() < 0.1:
                char = f"{BLINK}{char}{RESET}"
            line += color + char + RESET
        print(center_text(line))
        time.sleep(duration / intensity)

# -------------------------------
# SCAN HISTORY MANAGER
# -------------------------------

class ScanHistoryManager:
    """Manage scan history for retrieval with option 4"""
    
    @staticmethod
    def save_scan(scan_id: str, file_path: str, scan_type: str, results: Dict):
        """Save scan ID and results to history"""
        history = ScanHistoryManager.load_history()
        
        entry = {
            'scan_id': scan_id,
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'scan_type': scan_type,
            'timestamp': datetime.now().isoformat(),
            'operator': CONFIG['SOC_OPERATOR_NAME'],
            'session': CONFIG['SOC_SESSION_ID'],
            'results': results
        }
        
        history.append(entry)
        
        # Keep only last 100 scans
        if len(history) > 100:
            history = history[-100:]
        
        try:
            with open(SCAN_HISTORY_FILE, 'w') as f:
                json.dump(history, f, indent=2, default=str)
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Failed to save scan history: {e}{RESET}")
    
    @staticmethod
    def load_history() -> List[Dict]:
        """Load scan history from file"""
        if SCAN_HISTORY_FILE.exists():
            try:
                with open(SCAN_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    @staticmethod
    def get_scan_by_id(scan_id: str) -> Optional[Dict]:
        """Get a specific scan by ID"""
        history = ScanHistoryManager.load_history()
        for entry in history:
            if entry.get('scan_id') == scan_id:
                return entry
        return None
    
    @staticmethod
    def list_recent_scans(limit: int = 10) -> List[Dict]:
        """List recent scans"""
        history = ScanHistoryManager.load_history()
        return history[-limit:]

# -------------------------------
# SOC OPERATOR GUIDANCE SYSTEM
# -------------------------------

class SOCOperatorGuidance:
    def __init__(self):
        self.alerts = []
        self.recommendations = []
        self.current_risk_level = "LOW"
        self.active_incidents = []
        self.typer = AutoTypeEngine(delay=0.02)
        
    def assess_threat(self, malicious_count: int, total_scans: int) -> Dict:
        ratio = malicious_count / total_scans if total_scans > 0 else 0
        
        if ratio == 0:
            risk = "LOW"
            color = BRIGHT_GREEN
            glow = "🟢"
            action = "No action required. System appears clean."
            priority = "ROUTINE"
        elif ratio < 0.3:
            risk = "MEDIUM"
            color = BRIGHT_YELLOW
            glow = "🟡"
            action = "Investigate detected files. Consider quarantine."
            priority = "URGENT"
        elif ratio < 0.7:
            risk = "HIGH"
            color = ORANGE
            glow = "🟠"
            action = "IMMEDIATE INVESTIGATION REQUIRED."
            priority = "CRITICAL"
        else:
            risk = "CRITICAL"
            color = BRIGHT_RED + BLINK
            glow = "🔴"
            action = "EMERGENCY RESPONSE NEEDED!"
            priority = "EMERGENCY"
        
        self.current_risk_level = risk
        return {
            'risk': risk,
            'color': color,
            'glow': glow,
            'action': action,
            'priority': priority,
            'ratio': ratio
        }
    
    def generate_operator_advice(self, scan_type: str, findings: List) -> str:
        advice = []
        
        if scan_type == "hash_lookup":
            advice.append(f"{BRIGHT_CYAN}▓▓▓ Hash Analysis Complete ▓▓▓{RESET}")
        elif scan_type == "file_scan":
            advice.append(f"{BRIGHT_CYAN}▓▓▓ File Behavior Analysis ▓▓▓{RESET}")
        elif scan_type == "bulk_scan":
            advice.append(f"{BRIGHT_CYAN}▓▓▓ Bulk Scan Analysis ▓▓▓{RESET}")
        
        threats = [f for f in findings if f.get('malicious', 0) > 0]
        if threats:
            advice.append(f"{BRIGHT_RED}[!] {len(threats)} malicious items detected{RESET}")
            advice.append(f"{BRIGHT_YELLOW}[>] Recommended: Immediate quarantine{RESET}")
        else:
            advice.append(f"{BRIGHT_GREEN}[✓] No threats detected{RESET}")
            advice.append(f"{BRIGHT_GREEN}[>] System appears secure.{RESET}")
        
        return "\n".join(advice)
    
    def log_incident(self, incident_data: Dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alert_file = SOC_ALERTS_DIR / f"incident_{timestamp}.json"
        
        with open(alert_file, 'w') as f:
            json.dump(incident_data, f, indent=2)
        
        self.active_incidents.append(incident_data)
        return alert_file

class SOCDashboard:
    def __init__(self):
        self.threat_level = 0
        self.scan_progress = 0
        self.findings = []
        self.current_action = "INITIALIZING"
        self.current_scan_target = "N/A"
        self.threat_frame_idx = 0
        self.progress_bar_idx = 0
        self.glow_idx = 0
        self.stop_animation = False
        self.operator = SOCOperatorGuidance()
        self.session_start = datetime.now()
        self.typer = AutoTypeEngine(delay=0.025)

    def terminal_width(self):
        try:
            return shutil.get_terminal_size().columns
        except:
            return 120

    def center_block(self, text):
        width = self.terminal_width()
        lines = text.splitlines()
        centered = []

        for line in lines:
            visible = len(strip_ansi(line))
            padding = max(0, (width - visible) // 2)
            centered.append(" " * padding + line)

        return "\n".join(centered)

    def render_soc_header(self):
        elapsed = (datetime.now() - self.session_start).seconds
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        glow = GLOW_FRAMES[self.glow_idx % len(GLOW_FRAMES)]
        width = 85
        title = f"{glow} 🔬 DSTERMINAL - THREAT INTELLIGENCE 🔬 {glow}"

        header = f"""
{BRIGHT_CYAN}╔{'═' * width}╗{RESET}
{BRIGHT_CYAN}║{RESET}{title.center(width)}{BRIGHT_CYAN}║{RESET}
{BRIGHT_CYAN}╠{'═' * width}╣{RESET}
{BRIGHT_CYAN}║{RESET} {BRIGHT_YELLOW}Operator:{RESET} {CONFIG['SOC_OPERATOR_NAME']:<18} {BRIGHT_YELLOW}Session:{RESET} {CONFIG['SOC_SESSION_ID']:<18} {BRIGHT_YELLOW}Uptime:{RESET} {hours:02d}:{minutes:02d}:{seconds:02d} {BRIGHT_CYAN}║{RESET}
{BRIGHT_CYAN}╚{'═' * width}╝{RESET}
"""
        print(self.center_block(header))

    def render_threat_radar(self):
        threat_icon = THREAT_FRAMES[self.threat_frame_idx % len(THREAT_FRAMES)]
        glow_icon = GLOW_FRAMES[self.glow_idx % len(GLOW_FRAMES)]

        if self.threat_level < 30:
            threat_color = BRIGHT_GREEN
            threat_text = "LOW"
            threat_bar = "███░░░░░░░"
            radar_sweep = "🟢"
        elif self.threat_level < 70:
            threat_color = BRIGHT_YELLOW
            threat_text = "MEDIUM"
            threat_bar = "██████░░░░"
            radar_sweep = "🟡"
        else:
            threat_color = BRIGHT_RED + BLINK
            threat_text = "CRITICAL"
            threat_bar = "██████████"
            radar_sweep = "🔴"

        return f"""
{BRIGHT_CYAN}┌────────────────────────────────┐{RESET}
{BRIGHT_CYAN}│{RESET} {threat_color}🛸 THREAT RADAR {threat_icon} {glow_icon}{RESET}            {BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}├────────────────────────────────┤{RESET}
{BRIGHT_CYAN}│{RESET} Level: {threat_text:<22}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Score: {self.threat_level}%{' ' * 20}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Bar: [{threat_bar}]             {BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Radar: {radar_sweep:<21}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└────────────────────────────────┘{RESET}
"""

    def render_scan_status(self):
        scan_icon = SCANNING_FRAMES[self.threat_frame_idx % len(SCANNING_FRAMES)]
        bar = "█" * (self.scan_progress // 10) + "░" * (10 - (self.scan_progress // 10))

        if self.scan_progress < 30:
            bar_color = BRIGHT_RED
        elif self.scan_progress < 70:
            bar_color = BRIGHT_YELLOW
        else:
            bar_color = BRIGHT_GREEN

        return f"""
{BRIGHT_CYAN}┌──────────────────────────────────────┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}🎯 ACTIVE SCAN 🎯{RESET}                  {BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}├──────────────────────────────────────┤{RESET}
{BRIGHT_CYAN}│{RESET} Target: {self.current_scan_target[:26]:<26}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Action: {self.current_action[:26]:<26}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Progress: {bar_color}[{bar}]{RESET} {self.scan_progress:>3}% {BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└──────────────────────────────────────┘{RESET}
"""

    def render_stats_panel(self):
        total_threats = sum(1 for f in self.findings if f.get('malicious', 0) > 0)
        total_clean = len(self.findings) - total_threats

        return f"""
{BRIGHT_CYAN}┌──────────────────────────────┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_CYAN}📊 SOC STATISTICS 📊{RESET}       {BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}├──────────────────────────────┤{RESET}
{BRIGHT_CYAN}│{RESET} Total Scans: {len(self.findings):<12}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Clean: {total_clean:<19}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Threats: {total_threats:<16}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Detect Rate: {self.threat_level}%{' ' * 8}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└──────────────────────────────┘{RESET}
"""

    def render_layer2(self):
        radar = self.render_threat_radar().strip("\n").splitlines()
        scan = self.render_scan_status().strip("\n").splitlines()
        stats = self.render_stats_panel().strip("\n").splitlines()

        max_height = max(len(radar), len(scan), len(stats))
        while len(radar) < max_height:
            radar.append("")
        while len(scan) < max_height:
            scan.append("")
        while len(stats) < max_height:
            stats.append("")

        term_width = self.terminal_width()
        combined_lines = []
        radar_width = 45
        scan_width = 50
        stats_width = 45

        for r, s, st in zip(radar, scan, stats):
            r_visible = len(strip_ansi(r))
            s_visible = len(strip_ansi(s))
            st_visible = len(strip_ansi(st))

            r = r + (" " * max(0, radar_width - r_visible))
            s = s + (" " * max(0, scan_width - s_visible))
            st = st + (" " * max(0, stats_width - st_visible))

            scan_padding = (term_width // 2) - (scan_width // 2)
            left_padding = max(0, scan_padding - radar_width - 24)
            right_padding = 24

            line = (" " * left_padding) + r + (" " * 6) + s + (" " * right_padding) + st
            combined_lines.append(line)

        return "\n".join(combined_lines)

    def render_operator_guidance(self):
        assessment = self.operator.assess_threat(
            sum(1 for f in self.findings if f.get('malicious', 0) > 0),
            len(self.findings) if self.findings else 1
        )

        return f"""
{BRIGHT_YELLOW}╔════════════════════════════════════════════════════════════════════════════════╗{RESET}
{BRIGHT_YELLOW}║{RESET} 🟢 🎯 SOC OPERATOR GUIDANCE 🟢                                               {BRIGHT_YELLOW}║{RESET}
{BRIGHT_YELLOW}╠════════════════════════════════════════════════════════════════════════════════╣{RESET}
{BRIGHT_YELLOW}║{RESET} Risk Assessment: {assessment['risk']} ({assessment['priority']}){' ' * 45}{BRIGHT_YELLOW}║{RESET}
{BRIGHT_YELLOW}║{RESET} Action Required: {assessment['action'][:58]:<58}{' ' * 7}{BRIGHT_YELLOW}║{RESET}
{BRIGHT_YELLOW}╚════════════════════════════════════════════════════════════════════════════════╝{RESET}
"""

    def render_results_panel(self):
        if not self.findings:
            empty = f"""
{BRIGHT_CYAN}┌────────────────────────────────────────────────────────────────────────────────┐{RESET}
{BRIGHT_CYAN}│{RESET} 🔍 AWAITING SCAN RESULTS - STANDING BY 🔍                                 {BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└────────────────────────────────────────────────────────────────────────────────┘{RESET}
"""
            return self.center_block(empty)

        panel = f"""
{BRIGHT_GREEN}┌────────────────────────────────────────────────────────────────────────────────┐{RESET}
{BRIGHT_GREEN}│{RESET} 📋 LIVE SCAN RESULTS & ALERTS 📋                                          {BRIGHT_GREEN}│{RESET}
{BRIGHT_GREEN}├────────────────────────────────────────────────────────────────────────────────┤{RESET}
"""

        for finding in self.findings[-5:]:
            name = finding.get('name', 'Unknown')[:45]
            malicious = finding.get('malicious', 0)
            timestamp = finding.get('timestamp', datetime.now()).strftime("%H:%M:%S")

            if malicious > 0:
                icon = "🔴"
                status = "⚠ THREAT"
                color = BRIGHT_RED
            else:
                icon = "🟢"
                status = "✓ CLEAN"
                color = BRIGHT_GREEN

            panel += f"\n{color}│ {icon} {timestamp} | {name:<45} | {status:>12} │{RESET}"

        panel += f"\n{BRIGHT_GREEN}└────────────────────────────────────────────────────────────────────────────────┘{RESET}"
        return self.center_block(panel)

    def render_full(self):
        clear_screen()
        self.render_soc_header()
        print("\n")
        print(self.render_layer2())
        print("\n")
        print(self.render_operator_guidance())
        print("\n")
        print(self.render_results_panel())
        print("\n")
        self.animate(0.05)

    def animate(self, duration: float = 0.08):
        self.threat_frame_idx += 1
        self.progress_bar_idx += 1
        self.glow_idx += 1
        time.sleep(duration)

    def update_threat_level(self, malicious_count, total_scans=90):
        if total_scans > 0:
            ratio = malicious_count / total_scans
            self.threat_level = min(100, int(ratio * 100 * 2))

    def add_finding(self, name, malicious, details=None):
        finding = {
            'name': name,
            'malicious': malicious,
            'details': details or {},
            'timestamp': datetime.now()
        }
        self.findings.append(finding)
        self.update_threat_level(malicious, 90)

        if malicious > 0:
            incident_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'MALICIOUS_DETECTION',
                'indicator': name,
                'detections': malicious,
                'risk_level': self.threat_level,
                'operator': CONFIG['SOC_OPERATOR_NAME'],
                'session': CONFIG['SOC_SESSION_ID']
            }
            self.operator.log_incident(incident_data)

# -------------------------------
# REPORT GENERATION SYSTEM
# -------------------------------

class ReportGenerator:
    @staticmethod
    def save_json_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = "".join(c for c in str(target) if c.isalnum() or c in '.-_')[:30]
        
        report_data = {
            'scan_type': scan_type,
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'operator': CONFIG['SOC_OPERATOR_NAME'],
            'session_id': CONFIG['SOC_SESSION_ID'],
            'findings': [
                {
                    'name': f.get('name', 'Unknown'),
                    'malicious': f.get('malicious', 0),
                    'timestamp': f.get('timestamp', datetime.now()).isoformat() if isinstance(f.get('timestamp'), datetime) else str(f.get('timestamp'))
                }
                for f in dashboard.findings[-20:]
            ],
            'summary': {
                'total_scans': len(dashboard.findings),
                'total_threats': sum(1 for f in dashboard.findings if f.get('malicious', 0) > 0),
                'risk_level': dashboard.threat_level,
                'current_action': dashboard.current_action
            },
            'results': results
        }
        
        VT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        json_file = VT_REPORTS_DIR / f"{scan_type}_{safe_target}_{timestamp}.json"
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"{BRIGHT_GREEN}[✓] JSON report saved: {json_file}{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Failed to save JSON report: {e}{RESET}")
        
        return json_file
    
    @staticmethod
    def save_pdf_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Optional[Path]:
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import inch
        except ImportError:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = "".join(c for c in str(target) if c.isalnum() or c in '.-_')[:30]
        pdf_file = VT_REPORTS_DIR / f"{scan_type}_{safe_target}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle("TitleStyle", fontSize=18, alignment=1, spaceAfter=20, bold=True, textColor=colors.HexColor('#00ff00'))
        elements.append(Paragraph(f"DSTerminal SOC - {scan_type.upper()} Report", title_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        elements.append(Paragraph(f"<b>Operator:</b> {CONFIG['SOC_OPERATOR_NAME']}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Session:</b> {CONFIG['SOC_SESSION_ID']}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Target:</b> {target}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Scan Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))
        
        data = [["File/Hash", "Detections", "Status", "Time"]]
        for finding in dashboard.findings[-20:]:
            name = finding.get('name', 'Unknown')[:40]
            malicious = finding.get('malicious', 0)
            status = "🔴 INFECTED" if malicious > 0 else "🟢 CLEAN"
            time_str = finding.get('timestamp', datetime.now()).strftime("%H:%M:%S") if isinstance(finding.get('timestamp'), datetime) else "N/A"
            data.append([name, str(malicious), status, time_str])
        
        table = Table(data, colWidths=[2.5*inch, 0.8*inch, 1.2*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        elements.append(table)
        
        doc.build(elements)
        print(f"{BRIGHT_GREEN}[✓] PDF report saved: {pdf_file}{RESET}")
        return pdf_file
    
    @staticmethod
    def save_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Tuple[Path, Optional[Path]]:
        json_file = ReportGenerator.save_json_report(scan_type, target, results, dashboard)
        pdf_file = ReportGenerator.save_pdf_report(scan_type, target, results, dashboard)
        return json_file, pdf_file

# -------------------------------
# LOCAL THREAT DETECTOR
# -------------------------------

class LocalThreatDetector:
    THREAT_PATTERNS = {
        r'powershell.*-ExecutionPolicy Bypass': 95,
        r'Invoke-Expression|iex\s*\(': 90,
        r'rundll32\.exe.*javascript': 80,
        r'password["\']?\s*:\s*["\'][^"\']+["\']': 90,
        r'credentials["\']?\s*:\s*\[': 90,
        r'http://[^\s]+\.(exe|ps1|dat|php)': 80,
        r'process hollowing': 90,
        r'lsass memory access': 90,
        r'amsi bypass': 90,
    }
    
    @classmethod
    def analyze_file(cls, file_path: str) -> Tuple[int, List[Dict]]:
        findings = []
        total_score = 0
        max_possible_score = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            for pattern, score in cls.THREAT_PATTERNS.items():
                max_possible_score += score
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append({
                        'pattern': pattern,
                        'score': score,
                        'severity': cls._get_severity(score)
                    })
                    total_score += score
            
            threat_percentage = min(100, int((total_score / max_possible_score) * 100)) if max_possible_score > 0 else 0
            if threat_percentage > 70:
                threat_percentage = min(100, threat_percentage + 10)
            
            return threat_percentage, findings
        except:
            return 0, []
    
    @classmethod
    def _get_severity(cls, score: int) -> str:
        if score >= 90:
            return "CRITICAL"
        elif score >= 75:
            return "HIGH"
        elif score >= 60:
            return "MEDIUM"
        else:
            return "LOW"

# -------------------------------
# VIRUSTOTAL SCANNER WITH AUTO-TYPING
# -------------------------------

class VirusTotalScanner:
    def __init__(self, operator=None, session=None):
        self.dashboard = SOCDashboard()
        self.scan_results_cache = {}
        self.typer = AutoTypeEngine(delay=0.03)
        
        if operator:
            CONFIG['SOC_OPERATOR_NAME'] = operator
        if session:
            CONFIG['SOC_SESSION_ID'] = session
    
    def _validate_api(self) -> bool:
        if not CONFIG.get('VT_API_KEY'):
            print(f"{BRIGHT_RED}[!] VirusTotal API key not configured!{RESET}")
            return False
        return True
    
    def calculate_file_hash(self, file_path: str) -> Dict[str, str]:
        hashes = {}
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                hashes['md5'] = hashlib.md5(data).hexdigest()
                hashes['sha1'] = hashlib.sha1(data).hexdigest()
                hashes['sha256'] = hashlib.sha256(data).hexdigest()
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Hash calculation failed: {e}{RESET}")
        return hashes
    
    def vt_hash_lookup(self, file_hash: str):
        """Fast hash lookup with SOC Dashboard and auto-typing"""
        if not self._validate_api():
            return
        
        self.dashboard.current_action = "HASH LOOKUP"
        self.dashboard.current_scan_target = file_hash[:32]
        self.dashboard.scan_progress = 10
        
        # Auto-type the hash lookup initiation
        print("\n")
        self.typer.type_text("🔍 INITIATING HASH LOOKUP...", color=BRIGHT_CYAN)
        time.sleep(0.2)
        self.typer.type_text(f"📌 Target Hash: {file_hash[:32]}...", color=BRIGHT_YELLOW)
        time.sleep(0.2)
        
        try:
            url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
            headers = {"x-apikey": CONFIG['VT_API_KEY']}
            
            for progress in range(10, 101, 20):
                self.dashboard.scan_progress = progress
                self.dashboard.render_full()
                time.sleep(0.1)
            
            # Auto-type the API request
            self.typer.type_text("📡 Querying VirusTotal database...", color=BRIGHT_CYAN)
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                attrs = result['data']['attributes']
                stats = attrs['last_analysis_stats']
                malicious = stats.get('malicious', 0)
                
                self.dashboard.add_finding(file_hash, malicious, attrs)
                self.dashboard.scan_progress = 100
                self.dashboard.current_action = "COMPLETE"
                self.dashboard.render_full()
                
                # Auto-type results
                print("\n")
                self.typer.type_text("✅ HASH LOOKUP COMPLETE!", color=BRIGHT_GREEN)
                time.sleep(0.1)
                
                if malicious > 0:
                    self.typer.type_text(f"⚠️  MALICIOUS HASH DETECTED!", color=BRIGHT_RED)
                    self.typer.type_text(f"📊 Detections: {malicious}/{sum(stats.values())}", color=BRIGHT_YELLOW)
                else:
                    self.typer.type_text("✅ Hash is CLEAN - No detections found", color=BRIGHT_GREEN)
                
                # Save to scan history
                ScanHistoryManager.save_scan(file_hash, file_hash, "hash_lookup", {
                    'detections': malicious,
                    'total_scans': sum(stats.values())
                })
                
                advice = self.dashboard.operator.generate_operator_advice("hash_lookup", self.dashboard.findings)
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(center_text(f"{BRIGHT_MAGENTA}📋 OPERATOR ADVISORY{RESET}"))
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                print(advice)
                
                if malicious > 0:
                    choice = input(f"\n{BRIGHT_RED}Initiate quarantine protocol? (y/N): {RESET}").lower()
                    if choice == 'y':
                        self.quarantine_item(file_hash=file_hash)
            else:
                self.typer.type_text("❌ Hash not found in VirusTotal database", color=BRIGHT_RED)
                
        except Exception as e:
            self.typer.type_text(f"❌ Error: {e}", color=BRIGHT_RED)

    def vt_file_scan(self, file_path: str):
        """Fast file scan with SOC Dashboard and auto-typing"""
        if not self._validate_api():
            return
        
        file_path = os.path.expanduser(file_path)
        
        if not os.path.exists(file_path):
            self.typer.type_text(f"❌ File not found: {file_path}", color=BRIGHT_RED)
            return
        
        self.dashboard.current_action = f"LOCAL ANALYSIS"
        self.dashboard.current_scan_target = os.path.basename(file_path)
        self.dashboard.scan_progress = 10
        self.dashboard.render_full()
        
        # Auto-type the scan initiation
        print("\n")
        self.typer.type_text("🔬 INITIATING FILE SCAN...", color=BRIGHT_CYAN)
        time.sleep(0.2)
        self.typer.type_text(f"📄 Target: {os.path.basename(file_path)}", color=BRIGHT_YELLOW)
        time.sleep(0.2)
        self.typer.type_text("🔍 Performing local threat analysis...", color=BRIGHT_CYAN)
        
        # Quick local check
        threat_score, findings = LocalThreatDetector.analyze_file(file_path)
        
        if threat_score > 0:
            self.typer.type_text(f"⚠️  Local detection score: {threat_score}%", color=BRIGHT_YELLOW)
        
        self.dashboard.add_finding(os.path.basename(file_path), threat_score, {
            'local_findings': findings,
            'threat_score': threat_score
        })
        
        self.dashboard.scan_progress = 50
        self.dashboard.render_full()
        
        # Upload to VirusTotal
        hashes = self.calculate_file_hash(file_path)
        
        try:
            self.typer.type_text("📤 Uploading file to VirusTotal...", color=BRIGHT_CYAN)
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                headers = {"x-apikey": CONFIG['VT_API_KEY']}
                
                for progress in range(60, 101, 20):
                    self.dashboard.scan_progress = progress
                    self.dashboard.render_full()
                    time.sleep(0.1)
                
                response = requests.post(
                    "https://www.virustotal.com/api/v3/files",
                    headers=headers,
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                scan_id = result['data']['id']
                
                # Auto-type scan ID
                self.typer.type_text("✅ File uploaded successfully!", color=BRIGHT_GREEN)
                self.typer.type_text(f"📌 Scan ID: {scan_id}", color=BRIGHT_CYAN)
                self.typer.type_text("⏳ Results processing...", color=BRIGHT_YELLOW)
                
                # Save scan ID immediately
                ScanHistoryManager.save_scan(scan_id, file_path, "file_scan", {
                    'file_name': os.path.basename(file_path),
                    'scan_id': scan_id,
                    'status': 'pending'
                })
                
                # Quick poll for results
                self._quick_poll_results(scan_id, file_path, hashes, threat_score, findings)
            else:
                self.typer.type_text(f"❌ Upload failed (HTTP {response.status_code})", color=BRIGHT_RED)
                self.dashboard.scan_progress = 100
                self.dashboard.current_action = "COMPLETE (LOCAL ONLY)"
                self.dashboard.render_full()
                
        except Exception as e:
            self.typer.type_text(f"❌ Error: {e}", color=BRIGHT_RED)

    def _quick_poll_results(self, scan_id: str, file_path: str, hashes: Dict, local_score: int = 0, local_findings: List = None):
        """Quick poll for results with auto-typing"""
        url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
        headers = {"x-apikey": CONFIG['VT_API_KEY']}
        
        self.dashboard.current_action = "RETRIEVING RESULTS"
        
        # Try to get results quickly
        for attempt in range(8):
            time.sleep(5)
            try:
                # Auto-type progress
                self.typer.type_progress(attempt + 1, 8, f"Polling results... ({attempt+1}/8)")
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    status = result['data']['attributes']['status']
                    
                    if status == 'completed':
                        stats = result['data']['attributes']['stats']
                        vt_malicious = stats.get('malicious', 0)
                        total_scans = sum(stats.values())
                        
                        final_score = max(local_score, (vt_malicious / total_scans * 100) if total_scans > 0 else 0)
                        
                        self.dashboard.add_finding(os.path.basename(file_path), final_score, {
                            'vt_stats': stats,
                            'local_score': local_score,
                            'combined_score': final_score
                        })
                        self.dashboard.scan_progress = 100
                        self.dashboard.current_action = "COMPLETE"
                        self.dashboard.render_full()
                        
                        # Update scan history with results
                        ScanHistoryManager.save_scan(scan_id, file_path, "file_scan", {
                            'file_name': os.path.basename(file_path),
                            'scan_id': scan_id,
                            'status': 'completed',
                            'vt_detections': vt_malicious,
                            'total_scans': total_scans,
                            'local_score': local_score,
                            'final_score': final_score,
                            'md5': hashes.get('md5', 'N/A'),
                            'sha256': hashes.get('sha256', 'N/A')
                        })
                        
                        # Auto-type results
                        print("\n")
                        self.typer.type_text("✅ SCAN COMPLETE!", color=BRIGHT_GREEN)
                        time.sleep(0.1)
                        self.typer.type_text(f"📊 VirusTotal Detections: {vt_malicious}/{total_scans}", color=BRIGHT_YELLOW)
                        
                        if final_score > 50:
                            self.typer.type_text(f"⚠️  Risk Score: {final_score:.1f}% - HIGH RISK", color=BRIGHT_RED)
                        else:
                            self.typer.type_text(f"✅ Risk Score: {final_score:.1f}% - LOW RISK", color=BRIGHT_GREEN)
                        
                        self.typer.type_text(f"📌 Scan ID: {scan_id}", color=BRIGHT_CYAN)
                        
                        print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                        print(center_text(f"{BRIGHT_MAGENTA}📋 SCAN COMPLETE - RESULTS{RESET}"))
                        print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                        
                        # Save report
                        report_results = {
                            'file_name': os.path.basename(file_path),
                            'file_path': file_path,
                            'local_threat_score': local_score,
                            'vt_detections': vt_malicious,
                            'vt_total_scans': total_scans,
                            'final_risk_score': final_score,
                            'md5': hashes.get('md5', 'N/A'),
                            'sha256': hashes.get('sha256', 'N/A')
                        }
                        ReportGenerator.save_report("file_scan", os.path.basename(file_path), report_results, self.dashboard)
                        
                        # Auto-quarantine if infected
                        if final_score > 70:
                            self.typer.type_text("⚠️  THREAT DETECTED! Quarantine recommended.", color=BRIGHT_RED)
                            choice = input(f"\n{BRIGHT_RED}Quarantine infected file? (Y/n): {RESET}").lower()
                            if choice != 'n':
                                self.quarantine_item(file_path=file_path)
                        return
                    else:
                        self.dashboard.scan_progress = 70 + int(attempt * 3)
                        self.dashboard.current_action = f"PROCESSING ({attempt+1}/8)"
                        self.dashboard.render_full()
                        
            except:
                continue
        
        self.typer.type_text(f"\n⏳ Results still processing. Scan ID: {scan_id}", color=BRIGHT_YELLOW)
        self.typer.type_text("📌 Use option 4 to check results later", color=BRIGHT_CYAN)

    def vt_bulk_scan(self, folder_path: str, max_files: int = 10):
        """Fast bulk scan with auto-typing"""
        folder_path = os.path.expanduser(folder_path)
        
        if not os.path.isdir(folder_path):
            self.typer.type_text(f"❌ Invalid folder: {folder_path}", color=BRIGHT_RED)
            return
        
        self.dashboard.current_action = "BULK SCAN"
        self.dashboard.current_scan_target = os.path.basename(folder_path)
        self.dashboard.scan_progress = 0
        
        # Auto-type bulk scan initiation
        print("\n")
        self.typer.type_text("📁 INITIATING BULK SCAN...", color=BRIGHT_CYAN)
        time.sleep(0.2)
        self.typer.type_text(f"📂 Target Folder: {os.path.basename(folder_path)}", color=BRIGHT_YELLOW)
        
        files = []
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames[:max_files]:
                files.append(os.path.join(root, filename))
        
        if not files:
            self.typer.type_text("❌ No files found in folder", color=BRIGHT_RED)
            return
        
        self.typer.type_text(f"📄 Found {len(files)} files to scan", color=BRIGHT_CYAN)
        
        # Scan files and collect results
        scanned_files = []
        total_scanned = 0
        
        for file_path in files:
            self.dashboard.current_action = f"SCANNING: {os.path.basename(file_path)}"
            self.dashboard.scan_progress = int((total_scanned / len(files)) * 100)
            self.dashboard.render_full()
            
            # Scan the file
            try:
                hashes = self.calculate_hash(file_path)
                if hashes and hashes.get('sha256'):
                    url = f"https://www.virustotal.com/api/v3/files/{hashes['sha256']}"
                    headers = {"x-apikey": CONFIG['VT_API_KEY']}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        stats = result['data']['attributes']['last_analysis_stats']
                        malicious = stats.get('malicious', 0)
                        # Add finding to dashboard
                        self.dashboard.add_finding(os.path.basename(file_path), malicious, stats)
                        self.typer.type_text(f"  ✓ {os.path.basename(file_path)} - {malicious} detections", color=BRIGHT_GREEN)
                    else:
                        # If VT doesn't have the file, mark as unknown
                        self.dashboard.add_finding(os.path.basename(file_path), 0, {'status': 'not_found'})
                        self.typer.type_text(f"  ⚠ {os.path.basename(file_path)} - Not in VT database", color=BRIGHT_YELLOW)
                else:
                    self.dashboard.add_finding(os.path.basename(file_path), 0, {'status': 'hash_error'})
                    self.typer.type_text(f"  ❌ {os.path.basename(file_path)} - Hash calculation failed", color=BRIGHT_RED)
                    
            except Exception as e:
                self.dashboard.add_finding(os.path.basename(file_path), 0, {'error': str(e)})
                self.typer.type_text(f"  ❌ {os.path.basename(file_path)} - Error: {str(e)[:50]}", color=BRIGHT_RED)
            
            total_scanned += 1
            scanned_files.append(file_path)
            
            # Update progress after each file
            self.dashboard.scan_progress = int((total_scanned / len(files)) * 100)
            self.dashboard.render_full()
            
            # Small delay between scans to avoid rate limiting
            time.sleep(0.5)
        
        # Final update
        self.dashboard.scan_progress = 100
        self.dashboard.current_action = "COMPLETE"
        self.dashboard.render_full()
        
        # Save bulk report
        bulk_results = {
            'folder': folder_path,
            'total_files_scanned': len(files),
            'scanned_files': scanned_files,
            'scan_summary': {
                'total_threats': sum(1 for f in self.dashboard.findings if f.get('malicious', 0) > 0),
                'total_clean': sum(1 for f in self.dashboard.findings if f.get('malicious', 0) == 0),
                'risk_level': self.dashboard.threat_level,
                'total_scanned': len(self.dashboard.findings)
            }
        }
        ReportGenerator.save_report("bulk_scan", os.path.basename(folder_path), bulk_results, self.dashboard)
        
        # Auto-type completion with correct stats
        print("\n")
        self.typer.type_text("✅ BULK SCAN COMPLETE!", color=BRIGHT_GREEN)
        self.typer.type_text(f"📊 Files scanned: {len(files)}", color=BRIGHT_CYAN)
        
        # Calculate correct stats from dashboard findings
        total_threats = sum(1 for f in self.dashboard.findings if f.get('malicious', 0) > 0)
        total_clean = sum(1 for f in self.dashboard.findings if f.get('malicious', 0) == 0)
        
        if total_threats > 0:
            self.typer.type_text(f"⚠️  Threats detected: {total_threats}", color=BRIGHT_RED)
        else:
            self.typer.type_text(f"✅ No threats detected - All {total_clean} files clean", color=BRIGHT_GREEN)
        
        # Final operator guidance
        final_assessment = self.dashboard.operator.assess_threat(
            total_threats,
            len(self.dashboard.findings) if self.dashboard.findings else 1
        )
        print(f"\n{BRIGHT_CYAN}Final Risk Assessment: {final_assessment['color']}{final_assessment['risk']}{RESET}")
        print(f"{BRIGHT_CYAN}Recommended Action: {final_assessment['action'][:50]}{RESET}")
        
    def _quick_scan_file(self, file_path: str):
        """Quick scan a single file for bulk operations"""
        try:
            hashes = self.calculate_hash(file_path)
            if hashes and hashes.get('sha256'):
                url = f"https://www.virustotal.com/api/v3/files/{hashes['sha256']}"
                headers = {"x-apikey": CONFIG['VT_API_KEY']}
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    stats = result['data']['attributes']['last_analysis_stats']
                    malicious = stats.get('malicious', 0)
                    # Add finding to dashboard
                    self.dashboard.add_finding(os.path.basename(file_path), malicious, stats)
                    print(f"{BRIGHT_GREEN}[✓] Scanned: {os.path.basename(file_path)} - {malicious} detections{RESET}")
                else:
                    # If VT doesn't have the file, mark as unknown
                    self.dashboard.add_finding(os.path.basename(file_path), 0, {'status': 'not_found'})
                    print(f"{BRIGHT_YELLOW}[!] {os.path.basename(file_path)} - Not in VT database{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Error scanning {os.path.basename(file_path)}: {e}{RESET}")
            # Still add to findings so the counter updates
            self.dashboard.add_finding(os.path.basename(file_path), 0, {'error': str(e)})
            
    def calculate_hash(self, file_path: str) -> Dict[str, str]:
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                return {
                    'md5': hashlib.md5(data).hexdigest(),
                    'sha1': hashlib.sha1(data).hexdigest(),
                    'sha256': hashlib.sha256(data).hexdigest()
                }
        except:
            return {}

    def check_scan_result(self, scan_id: str):
        """Check previous scan results with auto-typing"""
        self.dashboard.current_action = "RETRIEVING SCAN"
        self.dashboard.current_scan_target = scan_id[:16]
        self.dashboard.render_full()
        
        print("\n")
        self.typer.type_text("🔍 RETRIEVING SCAN RESULTS...", color=BRIGHT_CYAN)
        time.sleep(0.2)
        
        # Check local history first
        history_entry = ScanHistoryManager.get_scan_by_id(scan_id)
        if history_entry and history_entry.get('results', {}).get('status') == 'completed':
            self.typer.type_text("✅ Results found in local history!", color=BRIGHT_GREEN)
            results = history_entry.get('results', {})
            print(f"{BRIGHT_CYAN}File: {results.get('file_name', 'Unknown')}{RESET}")
            print(f"{BRIGHT_YELLOW}Detections: {results.get('vt_detections', 0)}/{results.get('total_scans', 0)}{RESET}")
            
            risk_score = results.get('final_score', 0)
            if risk_score > 50:
                self.typer.type_text(f"⚠️  Risk Score: {risk_score:.1f}% - HIGH RISK", color=BRIGHT_RED)
            else:
                self.typer.type_text(f"✅ Risk Score: {risk_score:.1f}% - LOW RISK", color=BRIGHT_GREEN)
            return
        
        # If not in history, check VT API
        url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
        headers = {"x-apikey": CONFIG['VT_API_KEY']}
        
        try:
            self.typer.type_text("📡 Querying VirusTotal API...", color=BRIGHT_CYAN)
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                stats = result['data']['attributes']['stats']
                malicious = stats.get('malicious', 0)
                total_scans = sum(stats.values())
                
                self.dashboard.add_finding(scan_id, malicious, stats)
                self.dashboard.scan_progress = 100
                self.dashboard.current_action = "COMPLETE"
                self.dashboard.render_full()
                
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(center_text(f"{BRIGHT_MAGENTA}📋 SCAN RESULTS{RESET}"))
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                
                self.typer.type_text(f"📊 Detections: {malicious}/{total_scans}", color=BRIGHT_YELLOW)
                if malicious == 0:
                    self.typer.type_text("✅ Status: CLEAN - No threats detected", color=BRIGHT_GREEN)
                else:
                    self.typer.type_text("⚠️  Status: INFECTED - Threats detected!", color=BRIGHT_RED)
                
                self.typer.type_text(f"📌 Scan ID: {scan_id}", color=BRIGHT_CYAN)
                
                # Save to history
                ScanHistoryManager.save_scan(scan_id, scan_id, "check_scan", {
                    'scan_id': scan_id,
                    'vt_detections': malicious,
                    'total_scans': total_scans,
                    'status': 'completed'
                })
            else:
                self.typer.type_text("❌ Results not available", color=BRIGHT_RED)
                self.typer.type_text("⏳ The scan may still be processing or doesn't exist", color=BRIGHT_YELLOW)
        except Exception as e:
            self.typer.type_text(f"❌ Error: {e}", color=BRIGHT_RED)
    
    def quarantine_item(self, file_path: str = None, file_hash: str = None):
        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            dest = QUARANTINE_DIR / f"quarantined_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(file_path, dest)
            
            self.typer.type_text(f"✅ Quarantined: {dest}", color=BRIGHT_GREEN)
            
            log_file = WORKSPACE / "logs" / "quarantine.log"
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {CONFIG['SOC_OPERATOR_NAME']} | QUARANTINED | {file_path} -> {dest}\n")
        elif file_hash:
            hash_file = QUARANTINE_DIR / "quarantined_hashes.txt"
            with open(hash_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {CONFIG['SOC_OPERATOR_NAME']} | {file_hash}\n")
            self.typer.type_text("✅ Malicious hash recorded in quarantine database", color=BRIGHT_GREEN)
    
    def view_quarantine(self):
        print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
        print(center_text(f"{BRIGHT_MAGENTA}📁 QUARANTINE DIRECTORY{RESET}"))
        print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
        
        if QUARANTINE_DIR.exists():
            items = list(QUARANTINE_DIR.iterdir())
            if items:
                for item in items:
                    if item.is_file():
                        size = item.stat().st_size
                        mod_time = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        print(f"  {BRIGHT_RED}⚠️{RESET} {item.name:<50} {size:>10} bytes  {mod_time}")
                    else:
                        print(f"  {BRIGHT_YELLOW}📁{RESET} {item.name:<50} {'DIR':>10}")
            else:
                self.typer.type_text("✓ Quarantine is empty - System appears clean", color=BRIGHT_GREEN)
        else:
            self.typer.type_text("Quarantine directory not found", color=BRIGHT_YELLOW)

# -------------------------------
# MAIN MENU
# -------------------------------

def vt_scan_menu(operator=None, session=None):
    scanner = VirusTotalScanner(operator, session)
    typer = AutoTypeEngine(delay=0.025)
    
    while True:
        clear_screen()
        
        print(f"{BRIGHT_RED}{'═' * 80}{RESET}")
        print(center_text(f"{BRIGHT_MAGENTA}{BLINK}🔬 DSTERMINAL - THREAT INTELLIGENCE 🔬{RESET}"))
        print(f"{BRIGHT_RED}{'═' * 80}{RESET}")
        
        matrix_rain(0.3, 2)
        
        print()
        menu_box = f"""
{BRIGHT_CYAN}┌{'─' * 60}┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}🔍 OPERATION SELECTION{BRIGHT_CYAN}{' ' * 37}│{RESET}
{BRIGHT_CYAN}├{'─' * 60}┤{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}1.{RESET} Hash Lookup (VT Intelligence){' ' * 30}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}2.{RESET} File Scan (Upload & Analyze){' ' * 30}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}3.{RESET} Bulk Scan Folder{' ' * 39}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}4.{RESET} Check Previous Scan{' ' * 36}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}5.{RESET} View Quarantine{' ' * 39}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}6.{RESET} Show Scan History{' ' * 39}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_RED}0.{RESET} Exit & Shutdown{' ' * 40}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└{'─' * 60}┘{RESET}"""
        print(center_text(menu_box))
        print()
        
        operator = CONFIG.get('SOC_OPERATOR_NAME') or "OP-UNKNOWN"
        session = CONFIG.get('SOC_SESSION_ID') or "SESSION-UNKNOWN"
        print(center_text(f"{BRIGHT_YELLOW}[{operator}@{session} ~]$ {RESET}"))
         
        choice = input(center_text(f"{BRIGHT_GREEN}Select operation: {RESET}")).strip()
        
        if choice == "1":
            typer.type_text("🔍 Enter file hash (MD5/SHA1/SHA256):", color=BRIGHT_CYAN, end=" ")
            file_hash = input().strip()
            if file_hash:
                scanner.vt_hash_lookup(file_hash)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "2":
            typer.type_text("📄 Enter file path to scan:", color=BRIGHT_CYAN, end=" ")
            file_path = input().strip()
            if file_path:
                scanner.vt_file_scan(file_path)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "3":
            typer.type_text("📂 Enter folder path to scan:", color=BRIGHT_CYAN, end=" ")
            folder_path = input().strip()
            typer.type_text("📊 Max files to scan (default 10):", color=BRIGHT_CYAN, end=" ")
            max_files = input().strip()
            max_files = int(max_files) if max_files and max_files.isdigit() else 10
            if folder_path:
                scanner.vt_bulk_scan(folder_path, max_files)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "4":
            typer.type_text("📌 Enter scan ID:", color=BRIGHT_CYAN, end=" ")
            scan_id = input().strip()
            if scan_id:
                scanner.check_scan_result(scan_id)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "5":
            scanner.view_quarantine()
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "6":
            history = ScanHistoryManager.list_recent_scans(10)
            if history:
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(center_text(f"{BRIGHT_MAGENTA}📋 RECENT SCANS{RESET}"))
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                for i, entry in enumerate(reversed(history), 1):
                    scan_id = entry.get('scan_id', 'N/A')[:16]
                    file_name = entry.get('file_name', 'Unknown')[:30]
                    scan_type = entry.get('scan_type', 'Unknown')
                    timestamp = entry.get('timestamp', '')[:19]
                    print(f"  {i}. {BRIGHT_GREEN}{scan_id}{RESET} | {file_name} | {scan_type} | {timestamp}")
            else:
                typer.type_text("📋 No scan history found", color=BRIGHT_YELLOW)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "0":
            print(center_text(f"{BRIGHT_RED}⚠️  CLOSING...{RESET}"))
            matrix_rain(0.5, 3)
            print(center_text(f"{BRIGHT_GREEN}✅ DSTerminal SOC - Session Terminated{RESET}"))
            print(center_text(f"{BRIGHT_CYAN}Operator: {CONFIG['SOC_OPERATOR_NAME']} | Session: {CONFIG['SOC_SESSION_ID']}{RESET}"))
            break
        
        else:
            typer.type_text("❌ Invalid operation code", color=BRIGHT_RED)
            time.sleep(1)

# -------------------------------
# ENTRY POINT
# -------------------------------

if __name__ == "__main__":
    clear_screen()
    
    typer = AutoTypeEngine(delay=0.025)
    
    print(center_text(f"{BRIGHT_GREEN}╔{'═' * 80}╗{RESET}"))
    print(center_text(f"{BRIGHT_GREEN}║{RESET} {BRIGHT_MAGENTA}🚀 DSTERMINAL SOC PLATFORM INITIALIZING 🚀{RESET} {BRIGHT_GREEN}║{RESET}"))
    print(center_text(f"{BRIGHT_GREEN}╚{'═' * 80}╝{RESET}"))
    
    matrix_rain(1, 5)
    
    typer.type_text(center_text("🔐 Establishing secure session..."), color=BRIGHT_CYAN, delay=0.025)
    time.sleep(0.5)
    typer.type_text(center_text("🛡️ Loading threat intelligence modules..."), color=BRIGHT_CYAN, delay=0.025)
    time.sleep(0.5)
    typer.type_text(center_text("📡 Connecting to VirusTotal API..."), color=BRIGHT_CYAN, delay=0.025)
    time.sleep(0.5)
    typer.type_text(center_text("✅ Session established"), color=BRIGHT_GREEN, delay=0.025)
    time.sleep(1)
    
    vt_scan_menu()