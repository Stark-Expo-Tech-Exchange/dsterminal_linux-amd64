"""
DSTerminal - VirusTotal Integration Module
Enhanced Cinematic SOC Dashboard with Hacking-Style Animation
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

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

# =========================================================
# ANSI COLOR STRIPPING FOR RESPONSIVE LAYOUT CALCULATIONS
# =========================================================

ANSI_ESCAPE_PATTERN = re.compile(
    r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
)

def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences from terminal strings
    so visible width calculations remain accurate.
    """
    return ANSI_ESCAPE_PATTERN.sub('', text)
load_dotenv()
 
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

# -------------------------------
# CONFIGURATION
# -------------------------------

CONFIG = {
    'VT_API_KEY': '957166d424812a397e328022b84594a8c02757814f6c04518dce7e81179b4b79',
    'SOC_OPERATOR_NAME': None,
    'SOC_SESSION_ID': None,
}

def sync_operator_session(operator_name: str, session_id: str):
    """
    Sync operator identity from DSTerminal main app
    """
    CONFIG['SOC_OPERATOR_NAME'] = operator_name
    CONFIG['SOC_SESSION_ID'] = session_id

# -------------------------------
# GLOWING COLORS & STYLING
# -------------------------------

RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
BLINK = '\033[5m'
HIDE = '\033[8m'

# Standard colors
CYAN = '\033[96m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
ORANGE = '\033[38;5;208m'
PURPLE = '\033[38;5;129m'
PINK = '\033[38;5;205m'
LIME = '\033[38;5;154m'
GOLD = '\033[38;5;220m'

# Glowing / Bright variants
BRIGHT_CYAN = '\033[96;1m'
BRIGHT_GREEN = '\033[92;1m'
BRIGHT_RED = '\033[91;1m'
BRIGHT_YELLOW = '\033[93;1m'
BRIGHT_MAGENTA = '\033[95;1m'
BRIGHT_BLUE = '\033[94;1m'

# Animation frames
SCANNING_FRAMES = ["🔍", "🔎", "📡", "🛰️", "⚡", "💀", "🎯", "⚠️", "🔬", "🧬", "✨", "🌟"]
THREAT_FRAMES = ["◐", "◓", "◑", "◒", "⦾", "⦿", "⬤", "○", "⟳", "⟲", "↻", "↺", "🌀", "⚡"]
PROGRESS_BARS = ["▱" * 10, "▰" + "▱" * 9, "▰▰" + "▱" * 8, "▰▰▰" + "▱" * 7,
                 "▰" * 4 + "▱" * 6, "▰" * 5 + "▱" * 5, "▰" * 6 + "▱" * 4,
                 "▰" * 7 + "▱" * 3, "▰" * 8 + "▱" * 2, "▰" * 9 + "▱" * 1,
                 "▰" * 10]
HACKING_CHARS = ["░", "▒", "▓", "█", "▄", "▀", "■", "□", "▪", "▫"]
GLOW_FRAMES = ["✨", "⭐", "🌟", "💫", "⚡"]

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
    
    clean_text = text
    for code in [RESET, BOLD, DIM, BLINK, CYAN, YELLOW, GREEN, RED, BLUE, MAGENTA, WHITE, ORANGE, PURPLE, PINK, LIME, GOLD, BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_MAGENTA, BRIGHT_BLUE]:
        clean_text = clean_text.replace(code, '')
    
    padding = max(0, (width - len(clean_text)) // 2)
    return " " * padding + text

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def typewriter_effect(text: str, delay: float = 0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

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
# SOC OPERATOR GUIDANCE SYSTEM
# -------------------------------

class SOCOperatorGuidance:
    def __init__(self):
        self.alerts = []
        self.recommendations = []
        self.current_risk_level = "LOW"
        self.active_incidents = []
        
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
            action = "Investigate detected files. Consider quarantine for confirmed threats."
            priority = "URGENT"
        elif ratio < 0.7:
            risk = "HIGH"
            color = ORANGE
            glow = "🟠"
            action = "IMMEDIATE INVESTIGATION REQUIRED. Multiple threats detected."
            priority = "CRITICAL"
        else:
            risk = "CRITICAL"
            color = BRIGHT_RED + BLINK
            glow = "🔴"
            action = "EMERGENCY RESPONSE NEEDED. System may be compromised."
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
            advice.append(f"{BRIGHT_CYAN}[*] Recommended action: Verify hash against known threat databases{RESET}")
        elif scan_type == "file_scan":
            advice.append(f"{BRIGHT_CYAN}▓▓▓ File Behavior Analysis ▓▓▓{RESET}")
            advice.append(f"{BRIGHT_CYAN}[*] Consider running in sandbox environment{RESET}")
        elif scan_type == "bulk_scan":
            advice.append(f"{BRIGHT_CYAN}▓▓▓ Bulk Scan Analysis ▓▓▓{RESET}")
            advice.append(f"{BRIGHT_CYAN}[*] Prioritize by threat score | Generate incident report{RESET}")
        
        threats = [f for f in findings if f.get('malicious', 0) > 0]
        if threats:
            advice.append(f"{BRIGHT_RED}[!] {len(threats)} malicious items detected{RESET}")
            advice.append(f"{BRIGHT_YELLOW}[>] Recommended: Immediate quarantine and forensic analysis{RESET}")
            advice.append(f"{BRIGHT_YELLOW}[>] Action: Isolate affected system from network{RESET}")
        else:
            advice.append(f"{BRIGHT_GREEN}[✓] No threats detected{RESET}")
            advice.append(f"{BRIGHT_GREEN}[>] System appears secure. Continue monitoring.{RESET}")
        
        return "\n".join(advice)
    
    def log_incident(self, incident_data: Dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alert_file = SOC_ALERTS_DIR / f"incident_{timestamp}.json"
        
        with open(alert_file, 'w') as f:
            json.dump(incident_data, f, indent=2)
        
        self.active_incidents.append(incident_data)
        return alert_file

# -------------------------------
# ENHANCED FOUR-LAYER SOC DASHBOARD
# -------------------------------

# class SOCDashboard:
#     def __init__(self):
#         self.threat_level = 0
#         self.scan_progress = 0
#         self.findings = []
#         self.current_action = "INITIALIZING"
#         self.current_scan_target = "N/A"
#         self.threat_frame_idx = 0
#         self.progress_bar_idx = 0
#         self.glow_idx = 0
#         self.stop_animation = False
#         self.operator = SOCOperatorGuidance()
#         self.session_start = datetime.now()
        
#     def render_soc_header(self):
#         elapsed = (datetime.now() - self.session_start).seconds
#         hours = elapsed // 3600
#         minutes = (elapsed % 3600) // 60
#         seconds = elapsed % 60
        
#         glow = GLOW_FRAMES[self.glow_idx % len(GLOW_FRAMES)]
        
#         header = f"""
# {BRIGHT_CYAN}╔{'═' * 80}╗{RESET}
# {BRIGHT_CYAN}║{RESET} {glow} {BRIGHT_MAGENTA}🔬 DSTERMINAL - THREAT INTELLIGENCE 🔬{RESET} {glow} {BRIGHT_CYAN}║{RESET}
# {BRIGHT_CYAN}╠{'═' * 80}╣{RESET}
# {BRIGHT_CYAN}║{RESET} {BRIGHT_YELLOW}Operator:{RESET} {CONFIG['SOC_OPERATOR_NAME']:<20} {BRIGHT_YELLOW}Session:{RESET} {BRIGHT_GREEN}{CONFIG['SOC_SESSION_ID']}{RESET:<12} {BRIGHT_YELLOW}Uptime:{RESET} {BRIGHT_CYAN}{hours:02d}:{minutes:02d}:{seconds:02d}{RESET} {BRIGHT_CYAN}║{RESET}
# {BRIGHT_CYAN}╚{'═' * 80}╝{RESET}"""
#         print(center_text(header))
        
#     def render_threat_radar(self):
#         threat_icon = THREAT_FRAMES[self.threat_frame_idx % len(THREAT_FRAMES)]
#         glow_icon = GLOW_FRAMES[self.glow_idx % len(GLOW_FRAMES)]
        
#         if self.threat_level < 30:
#             threat_color = BRIGHT_GREEN
#             threat_text = "LOW"
#             threat_bar = "█" * 3 + "░" * 7
#         elif self.threat_level < 70:
#             threat_color = BRIGHT_YELLOW
#             threat_text = "MEDIUM"
#             threat_bar = "█" * 6 + "░" * 4
#         else:
#             threat_color = BRIGHT_RED + BLINK
#             threat_text = "CRITICAL"
#             threat_bar = "█" * 10
        
#         radar_sweep = ["🟢", "🟡", "🔴", "⚡"][self.threat_frame_idx % 4]
        
#         radar = f"""
# {BRIGHT_CYAN}┌{'─' * 32}┐{RESET}
# {BRIGHT_CYAN}│{RESET} {threat_color}🛸 THREAT RADAR {threat_icon} {glow_icon}{RESET}{' ' * 12}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}├{'─' * 32}┤{RESET}
# {BRIGHT_CYAN}│{RESET} {threat_color}Level: {threat_text}{RESET}{' ' * 21}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {threat_color}Score: {self.threat_level}%{RESET}{' ' * 20}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {threat_color}Bar: [{threat_bar}]{RESET}{' ' * 15}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {threat_color}Radar: {radar_sweep}{RESET}{' ' * 20}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}└{'─' * 32}┘{RESET}"""
#         return radar
    
#     def render_scan_status(self):
#         scan_icon = SCANNING_FRAMES[self.threat_frame_idx % len(SCANNING_FRAMES)]
#         bar = PROGRESS_BARS[self.progress_bar_idx % len(PROGRESS_BARS)]
        
#         if self.scan_progress < 30:
#             bar_color = BRIGHT_RED
#         elif self.scan_progress < 70:
#             bar_color = BRIGHT_YELLOW
#         else:
#             bar_color = BRIGHT_GREEN
        
#         status = f"""
# {BRIGHT_CYAN}┌{'─' * 38}┐{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}{scan_icon} ACTIVE SCAN {scan_icon}{RESET}{' ' * 18}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}├{'─' * 38}┤{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Target:{RESET} {self.current_scan_target[:28]:<28}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Action:{RESET} {self.current_action[:28]:<28}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Progress:{RESET} {bar_color}[{bar}]{RESET} {self.scan_progress}%{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}└{'─' * 38}┘{RESET}"""
#         return status
    
#     def render_stats_panel(self):
#         total_threats = sum(1 for f in self.findings if f.get('malicious', 0) > 0)
#         total_clean = len(self.findings) - total_threats
#         total_scans = len(self.findings)
        
#         stats = f"""
# {BRIGHT_CYAN}┌{'─' * 30}┐{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_CYAN}📊 SOC STATISTICS 📊{RESET}{' ' * 7}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}├{'─' * 30}┤{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Total Scans:{RESET} {BRIGHT_CYAN}{total_scans:<4}{RESET}{' ' * 13}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}Clean:{RESET} {total_clean:<4}{' ' * 14}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_RED}Threats:{RESET} {total_threats:<4}{' ' * 13}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Detect Rate:{RESET} {self.threat_level}%{' ' * 12}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}└{'─' * 30}┘{RESET}"""
#         return stats
    
#     def render_operator_guidance(self):
#         assessment = self.operator.assess_threat(
#             sum(1 for f in self.findings if f.get('malicious', 0) > 0),
#             len(self.findings) if self.findings else 1
#         )
        
#         guidance = f"""
# {BRIGHT_YELLOW}╔{'═' * 80}╗{RESET}
# {BRIGHT_YELLOW}║{RESET} {assessment['glow']} {BRIGHT_MAGENTA}🎯 SOC OPERATOR GUIDANCE {assessment['glow']}{RESET}{' ' * 47}{BRIGHT_YELLOW}║{RESET}
# {BRIGHT_YELLOW}╠{'═' * 80}╣{RESET}
# {BRIGHT_YELLOW}║{RESET} {BRIGHT_CYAN}Risk Assessment:{RESET} {assessment['color']}{assessment['risk']}{RESET} ({assessment['priority']}){' ' * 45}{BRIGHT_YELLOW}║{RESET}
# {BRIGHT_YELLOW}║{RESET} {BRIGHT_CYAN}Action Required:{RESET} {assessment['action'][:62]:<62}{BRIGHT_YELLOW}║{RESET}
# {BRIGHT_YELLOW}╚{'═' * 80}╝{RESET}"""
#         return center_text(guidance)
    
#     def render_results_panel(self):
#         if not self.findings:
#             results = f"""
# {BRIGHT_CYAN}┌{'─' * 80}┐{RESET}
# {BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}🔍 AWAITING SCAN RESULTS - STANDING BY 🔍{RESET}{' ' * 37}{BRIGHT_CYAN}│{RESET}
# {BRIGHT_CYAN}└{'─' * 80}┘{RESET}"""
#             return center_text(results)
        
#         results = f"""
# {BRIGHT_GREEN}┌{'─' * 80}┐{RESET}
# {BRIGHT_GREEN}│{RESET} {BRIGHT_MAGENTA}📋 LIVE SCAN RESULTS & ALERTS 📋{RESET}{' ' * 38}{BRIGHT_GREEN}│{RESET}
# {BRIGHT_GREEN}├{'─' * 80}┤{RESET}"""
        
#         for finding in self.findings[-8:]:
#             name = finding.get('name', 'Unknown')[:40]
#             malicious = finding.get('malicious', 0)
#             timestamp = finding.get('timestamp', datetime.now()).strftime("%H:%M:%S") if isinstance(finding.get('timestamp'), datetime) else "N/A"
            
#             if malicious > 0:
#                 color = BRIGHT_RED
#                 status = f"⚠️ {malicious} detections"
#                 alert_icon = "🔴"
#             else:
#                 color = BRIGHT_GREEN
#                 status = "✓ CLEAN"
#                 alert_icon = "🟢"
            
#             results += f"\n{color}│ {alert_icon} {timestamp} | {name:<40} | {status:>25} │{RESET}"
        
#         results += f"\n{BRIGHT_GREEN}└{'─' * 80}┘{RESET}"
#         return center_text(results)
    
#     def render_layer2(self):
#         radar = self.render_threat_radar()
#         status = self.render_scan_status()
#         stats = self.render_stats_panel()
        
#         radar_lines = radar.split('\n')
#         status_lines = status.split('\n')
#         stats_lines = stats.split('\n')
        
#         max_lines = max(len(radar_lines), len(status_lines), len(stats_lines))
        
#         radar_width = 34
#         status_width = 40
#         stats_width = 32
#         spacer = "   "
        
#         radar_lines += [' ' * radar_width] * (max_lines - len(radar_lines))
#         status_lines += [' ' * status_width] * (max_lines - len(status_lines))
#         stats_lines += [' ' * stats_width] * (max_lines - len(stats_lines))
        
#         combined = []
#         for r, s, st in zip(radar_lines, status_lines, stats_lines):
#             r_padded = r.ljust(radar_width)
#             s_padded = s.ljust(status_width)
#             st_padded = st.ljust(stats_width)
#             combined.append(f"{r_padded}{spacer}{s_padded}{spacer}{st_padded}")
        
#         return '\n'.join(combined)
    
#     def animate(self, duration: float = 0.08):
#         self.threat_frame_idx += 1
#         self.progress_bar_idx += 1
#         self.glow_idx += 1
#         time.sleep(duration)
    
#     def render_full(self):
#         clear_screen()
        
#         self.render_soc_header()
#         print()
#         print()
        
#         print(self.render_layer2())
#         print()
#         print()
        
#         print(self.render_operator_guidance())
#         print()
        
#         print(self.render_results_panel())
#         print()
        
#         self.animate(0.05)
    
#     def update_threat_level(self, malicious_count: int, total_scans: int = 90):
#         if total_scans > 0:
#             ratio = malicious_count / total_scans
#             self.threat_level = min(100, int(ratio * 100 * 2))
    
#     def add_finding(self, name: str, malicious: int, details: Dict = None):
#         finding = {
#             'name': name,
#             'malicious': malicious,
#             'details': details or {},
#             'timestamp': datetime.now()
#         }
#         self.findings.append(finding)
#         self.update_threat_level(malicious, 90)
        
#         if malicious > 0:
#             incident_data = {
#                 'timestamp': datetime.now().isoformat(),
#                 'type': 'MALICIOUS_DETECTION',
#                 'indicator': name,
#                 'detections': malicious,
#                 'risk_level': self.threat_level,
#                 'operator': CONFIG['SOC_OPERATOR_NAME'],
#                 'session': CONFIG['SOC_SESSION_ID']
#             }
#             self.operator.log_incident(incident_data)
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

    # =========================
    # RESPONSIVE HELPERS
    # =========================

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

    def pad_panel_height(self, lines, target_height, width):
        while len(lines) < target_height:
            lines.append(" " * width)
        return lines

    # =========================
    # HEADER
    # =========================

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

    # =========================
    # THREAT RADAR
    # =========================

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

    # =========================
    # ACTIVE SCAN
    # =========================

    def render_scan_status(self):
        scan_icon = SCANNING_FRAMES[self.threat_frame_idx % len(SCANNING_FRAMES)]
        bar = PROGRESS_BARS[self.progress_bar_idx % len(PROGRESS_BARS)]

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

    # =========================
    # SOC STATS
    # =========================

    def render_stats_panel(self):
        total_threats = sum(
            1 for f in self.findings if f.get('malicious', 0) > 0
        )

        total_clean = len(self.findings) - total_threats
        total_scans = len(self.findings)

        return f"""
{BRIGHT_CYAN}┌──────────────────────────────┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_CYAN}📊 SOC STATISTICS 📊{RESET}       {BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}├──────────────────────────────┤{RESET}
{BRIGHT_CYAN}│{RESET} Total Scans: {total_scans:<12}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Clean: {total_clean:<19}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Threats: {total_threats:<16}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} Detect Rate: {self.threat_level}%{' ' * 8}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└──────────────────────────────┘{RESET}
"""

    # =========================
    # RESPONSIVE LAYER 2
    # =========================
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

        # PANEL WIDTHS
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

            # CENTER ACTIVE PANEL
            scan_padding = (term_width // 2) - (scan_width // 2)

            # PUSH LEFT PANEL FURTHER LEFT
            left_padding = max(0, scan_padding - radar_width - 24)

            # PUSH RIGHT PANEL FURTHER RIGHT
            right_padding = 24

            line = (
                (" " * left_padding)
                + r
                + (" " * 6)
                + s
                + (" " * right_padding)
                + st
            )

            combined_lines.append(line)

        return "\n".join(combined_lines)
    # =========================
    # OPERATOR GUIDANCE
    # LEFT-ALIGNED
    # =========================

    def render_operator_guidance(self):

        assessment = self.operator.assess_threat(
            sum(
                1 for f in self.findings
                if f.get('malicious', 0) > 0
            ),
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

    # =========================
    # RESULTS PANEL
    # CENTERED
    # =========================

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

            timestamp = finding.get(
                'timestamp',
                datetime.now()
            ).strftime("%H:%M:%S")

            if malicious > 0:
                icon = "🔴"
                status = "⚠ THREAT"
                color = BRIGHT_RED
            else:
                icon = "🟢"
                status = "✓ CLEAN"
                color = BRIGHT_GREEN

            panel += (
                f"\n{color}│ {icon} {timestamp} | "
                f"{name:<45} | "
                f"{status:>12} │{RESET}"
            )

        panel += f"\n{BRIGHT_GREEN}└────────────────────────────────────────────────────────────────────────────────┘{RESET}"

        return self.center_block(panel)

    # =========================
    # MAIN RENDER
    # =========================

    def render_full(self):

        clear_screen()

        self.render_soc_header()

        print("\n")

        print(self.render_layer2())

        print("\n")

        # LEFT SIDE GUIDANCE
        print(self.render_operator_guidance())

        print("\n")

        # CENTERED RESULTS
        print(self.render_results_panel())

        print("\n")

        self.animate(0.05)

    # =========================
    # ANIMATION
    # =========================

    def animate(self, duration: float = 0.08):
        self.threat_frame_idx += 1
        self.progress_bar_idx += 1
        self.glow_idx += 1
        time.sleep(duration)

    # =========================
    # THREAT UPDATES
    # =========================

    def update_threat_level(self, malicious_count, total_scans=90):

        if total_scans > 0:
            ratio = malicious_count / total_scans
            self.threat_level = min(
                100,
                int(ratio * 100 * 2)
            )

    # =========================
    # FINDINGS
    # =========================

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
    """Handles JSON and PDF report generation for all scan types"""
    
    @staticmethod
    def save_json_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Path:
        """Save JSON report for any scan type"""
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
                for f in dashboard.findings[-20:]  # Last 20 findings
            ],
            'summary': {
                'total_scans': len(dashboard.findings),
                'total_threats': sum(1 for f in dashboard.findings if f.get('malicious', 0) > 0),
                'risk_level': dashboard.threat_level,
                'current_action': dashboard.current_action
            },
            'results': results
        }
        
<<<<<<< HEAD
        # Ensure directory exists
        VT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        json_file = VT_REPORTS_DIR / f"{scan_type}_{safe_target}_{timestamp}.json"
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"{BRIGHT_GREEN}[✓] JSON report saved: {json_file}{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Failed to save JSON report: {e}{RESET}")
        
        return json_file

=======
        json_file = VT_REPORTS_DIR / f"{scan_type}_{safe_target}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"{BRIGHT_GREEN}[✓] JSON report saved: {json_file}{RESET}")
        return json_file
    
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    @staticmethod
    def save_pdf_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Optional[Path]:
        """Save PDF report for any scan type"""
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.units import inch
        except ImportError:
            print(f"{BRIGHT_YELLOW}[!] ReportLab not installed. PDF report skipped.{RESET}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = "".join(c for c in str(target) if c.isalnum() or c in '.-_')[:30]
        pdf_file = VT_REPORTS_DIR / f"{scan_type}_{safe_target}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = ParagraphStyle("TitleStyle", fontSize=18, alignment=1, spaceAfter=20, bold=True, textColor=colors.HexColor('#00ff00'))
        elements.append(Paragraph(f"DSTerminal SOC - {scan_type.upper()} Report", title_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Scan info
        elements.append(Paragraph(f"<b>Operator:</b> {CONFIG['SOC_OPERATOR_NAME']}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Session:</b> {CONFIG['SOC_SESSION_ID']}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Target:</b> {target}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Scan Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Risk Level:</b> {dashboard.threat_level}%", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Results table
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
            ('TEXTCOLOR', (2, 1), (2, -1), colors.red),
        ]))
        elements.append(table)
        
        # Statistics summary
        elements.append(Spacer(1, 0.3 * inch))
        total_threats = sum(1 for f in dashboard.findings if f.get('malicious', 0) > 0)
        stats_text = f"""
        <b>Summary Statistics:</b><br/>
        • Total Scans: {len(dashboard.findings)}<br/>
        • Threats Detected: {total_threats}<br/>
        • Clean Files: {len(dashboard.findings) - total_threats}<br/>
        • Detection Rate: {dashboard.threat_level}%
        """
        elements.append(Paragraph(stats_text, styles["Normal"]))
        
        doc.build(elements)
        print(f"{BRIGHT_GREEN}[✓] PDF report saved: {pdf_file}{RESET}")
        return pdf_file
    
    @staticmethod
    def save_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Tuple[Path, Optional[Path]]:
        """Save both JSON and PDF reports"""
        json_file = ReportGenerator.save_json_report(scan_type, target, results, dashboard)
        pdf_file = ReportGenerator.save_pdf_report(scan_type, target, results, dashboard)
        return json_file, pdf_file

# -------------------------------
# ENHANCED VIRUSTOTAL SCANNER
# -------------------------------
# Add this class before the VirusTotalScanner class

class LocalThreatDetector:
    """Local threat detection for analyzing file content before VT scan"""
    
    # Threat indicators and their severity scores
    THREAT_PATTERNS = {
        # C2 Communication Patterns
        r'\[C2_COMMUNICATION_LOG\]': 95,
        r'C2[_ ]?[Ss]erver.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}': 90,
        r'[Bb]eacon[_ ]?[Ii]nterval': 85,
        r'Command[_ ]?and[_ ]?[Cc]ontrol': 85,
        
        # Credential Theft Patterns
        r'\[EXFILTRATED_DATA\]': 95,
        r'password["\']?\s*:\s*["\'][^"\']+["\']': 90,
        r'credentials["\']?\s*:\s*\[': 90,
        r'password_hash["\']?\s*:\s*["\'][a-f0-9]{64}["\']': 85,
        
        # Malicious Commands
        r'powershell.*-ExecutionPolicy Bypass': 95,
        r'\[COMMANDS_RECEIVED\]': 90,
        r'schtasks.*\/create.*\/tr': 85,
        r'Invoke-Expression|iex\s*\(': 90,
        r'rundll32\.exe.*javascript': 80,
        
        # Process/System Manipulation
        r'\[MALICIOUS_INDICATORS\]': 95,
        r'process hollowing': 90,
        r'lsass memory access': 90,
        r'amsi bypass': 90,
        r'powershell downgrade': 85,
        
        # Exfiltration Patterns
        r'Data exfiltrated:\s*\d+\.?\d*\s*MB': 85,
        r'http://[^\s]+\.(exe|ps1|dat|php)': 80,
        
        # Network Scanning
        r'net view.*\/all.*net user.*\/domain': 80,
        r'ipconfig \/all': 70,
        
        # Persistence
        r'Persistence:\s*ACTIVE': 85,
        r'CURRENT_STATUS.*?ESTABLISHED': 80
    }
    
    @classmethod
    def analyze_file(cls, file_path: str) -> Tuple[int, List[Dict]]:
        """
        Analyze a file for threat indicators
        Returns: (threat_score, list_of_findings)
        """
        findings = []
        total_score = 0
        max_possible_score = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            # Check each pattern
            for pattern, score in cls.THREAT_PATTERNS.items():
                max_possible_score += score
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append({
                        'pattern': pattern,
                        'score': score,
                        'severity': cls._get_severity(score)
                    })
                    total_score += score
            
            # Calculate percentage score (0-100)
            threat_percentage = min(100, int((total_score / max_possible_score) * 100)) if max_possible_score > 0 else 0
            
            # Special case: high confidence detection
            if threat_percentage > 70:
                threat_percentage = min(100, threat_percentage + 10)
            
            return threat_percentage, findings
            
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Analysis error: {e}{RESET}")
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
    
    @classmethod
    def generate_threat_report(cls, file_path: str, threat_score: int, findings: List[Dict]) -> str:
        """Generate a detailed threat report"""
        report_lines = []
        report_lines.append(f"\n{BRIGHT_RED}{'='*80}{RESET}")
        report_lines.append(center_text(f"{BRIGHT_RED}{BLINK}🚨 THREAT DETECTED! 🚨{RESET}"))
        report_lines.append(f"{BRIGHT_RED}{'='*80}{RESET}")
        report_lines.append(f"{BRIGHT_YELLOW}File:{RESET} {os.path.basename(file_path)}")
        report_lines.append(f"{BRIGHT_YELLOW}Threat Score:{RESET} {BRIGHT_RED}{threat_score}%{RESET} (CRITICAL)" if threat_score > 70 else f"{BRIGHT_YELLOW}Threat Score:{RESET} {BRIGHT_YELLOW}{threat_score}%{RESET}")
        
        report_lines.append(f"\n{BRIGHT_CYAN}📋 Detected Indicators:{RESET}")
        for i, finding in enumerate(findings[:10], 1):
            severity_color = BRIGHT_RED if finding['severity'] == "CRITICAL" else BRIGHT_YELLOW if finding['severity'] == "HIGH" else BRIGHT_CYAN
            report_lines.append(f"  {severity_color}{i}. [{finding['severity']}] {finding['pattern']}{RESET} (Score: {finding['score']})")
        
        # Add recommendations
        report_lines.append(f"\n{BRIGHT_YELLOW}🎯 Recommended Actions:{RESET}")
        if threat_score > 70:
            report_lines.append(f"  {BRIGHT_RED}🔴 IMMEDIATE ACTION REQUIRED:{RESET}")
            report_lines.append(f"     • Isolate affected system from network")
            report_lines.append(f"     • Block C2 server IPs at firewall")
            report_lines.append(f"     • Reset compromised credentials")
            report_lines.append(f"     • Initiate incident response protocol")
        elif threat_score > 40:
            report_lines.append(f"  {BRIGHT_YELLOW}🟡 URGENT:{RESET}")
            report_lines.append(f"     • Investigate detected indicators")
            report_lines.append(f"     • Run full system scan")
            report_lines.append(f"     • Review network logs for anomalies")
        else:
            report_lines.append(f"  {BRIGHT_GREEN}🟢 ROUTINE:{RESET}")
            report_lines.append(f"     • Continue monitoring")
            report_lines.append(f"     • No immediate action required")
        
        return "\n".join(report_lines)


# Then modify the vt_file_scan method in VirusTotalScanner class:



# Update _poll_results to accept local findings
class VirusTotalScanner:
    def __init__(self, operator=None, session=None):
        self.dashboard = SOCDashboard()
        self.cache_file = WORKSPACE / "vt_cache.json"
        self.scan_history = []
        self.load_cache()

        if operator:
            CONFIG['SOC_OPERATOR_NAME'] = operator
        if session:
            CONFIG['SOC_SESSION_ID'] = session

        self.cache_file = WORKSPACE / "vt_cache.json"
        self.scan_history = []
        self.load_cache()
        
    def load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.scan_history = json.load(f)
            except:
                self.scan_history = []
    
    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.scan_history[-100:], f, indent=2)
    
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
    
    def _validate_api(self) -> bool:
        if not CONFIG.get('VT_API_KEY'):
            print(f"{BRIGHT_RED}[!] VirusTotal API key not configured!{RESET}")
            print(f"{BRIGHT_YELLOW}[>] Please add your API key to CONFIG['VT_API_KEY']{RESET}")
            return False
        return True
    
    def vt_hash_lookup(self, file_hash: str):
        """Cinematic hash lookup with SOC Dashboard and report generation"""
        if not self._validate_api():
            return
        
        self.dashboard.current_action = "HASH LOOKUP"
        self.dashboard.current_scan_target = file_hash[:32]
        self.dashboard.scan_progress = 10
        
        try:
            url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
            headers = {"x-apikey": CONFIG['VT_API_KEY']}
            
            for progress in range(10, 101, 15):
                self.dashboard.scan_progress = progress
                self.dashboard.render_full()
                time.sleep(0.2)
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                attrs = result['data']['attributes']
                stats = attrs['last_analysis_stats']
                malicious = stats.get('malicious', 0)
                
                self.dashboard.add_finding(file_hash, malicious, attrs)
                self.dashboard.scan_progress = 100
                self.dashboard.current_action = "COMPLETE"
                self.dashboard.render_full()
                
                # Generate operator advice
                advice = self.dashboard.operator.generate_operator_advice(
                    "hash_lookup", 
                    self.dashboard.findings
                )
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(center_text(f"{BRIGHT_MAGENTA}📋 OPERATOR ADVISORY{RESET}"))
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                print(advice)
                
                # Save report for hash lookup
                report_results = {
                    'hash': file_hash,
                    'detections': malicious,
                    'total_scans': sum(stats.values()),
                    'first_seen': attrs.get('first_submission_date', 'N/A'),
                    'file_type': attrs.get('type_tag', 'Unknown')
                }
                ReportGenerator.save_report("hash_lookup", file_hash, report_results, self.dashboard)
                
                # Auto-quarantine recommendation
                if malicious > 0:
                    print(f"\n{BRIGHT_RED}[!] MALICIOUS HASH DETECTED!{RESET}")
                    print(f"{BRIGHT_YELLOW}[>] Detection Ratio: {malicious}/{sum(stats.values())}{RESET}")
                    choice = input(f"\n{BRIGHT_RED}Initiate quarantine protocol? (y/N): {RESET}").lower()
                    if choice == 'y':
                        self.quarantine_item(file_hash=file_hash)
            else:
                print(f"{BRIGHT_RED}[!] Hash not found in VirusTotal database{RESET}")
                
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Error: {e}{RESET}")

    def vt_file_scan(self, file_path: str):
        """Cinematic file upload with SOC Dashboard and LOCAL THREAT DETECTION"""
        if not self._validate_api():
            return
        
        file_path = os.path.expanduser(file_path)
        
        if not os.path.exists(file_path):
            print(f"{BRIGHT_RED}[!] File not found: {file_path}{RESET}")
            return
        
        # FIRST: Perform local threat detection
        self.dashboard.current_action = f"LOCAL THREAT ANALYSIS"
        self.dashboard.current_scan_target = os.path.basename(file_path)
        self.dashboard.scan_progress = 10
        self.dashboard.render_full()
        
        threat_score, findings = LocalThreatDetector.analyze_file(file_path)
        
        # Update dashboard with local findings
        self.dashboard.add_finding(os.path.basename(file_path), threat_score, {
            'local_findings': findings,
            'threat_score': threat_score,
            'detection_method': 'LOCAL_PATTERN_MATCHING'
        })
        
        self.dashboard.scan_progress = 50
        self.dashboard.render_full()
        
        # Generate threat report if malicious
        if threat_score > 30:
            report = LocalThreatDetector.generate_threat_report(file_path, threat_score, findings)
            print(report)
            
            # Ask for quarantine
            if threat_score > 70:
                choice = input(f"\n{BRIGHT_RED}Quarantine infected file? (Y/n): {RESET}").lower()
                if choice != 'n':
                    self.quarantine_item(file_path=file_path)
                    return  # Don't upload to VT if already quarantined
        
        # If low threat or user chooses to continue, upload to VirusTotal
        hashes = self.calculate_file_hash(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                headers = {"x-apikey": CONFIG['VT_API_KEY']}
                
                for progress in range(60, 101, 20):
                    self.dashboard.scan_progress = progress
                    self.dashboard.render_full()
                    time.sleep(0.15)
                
                response = requests.post(
                    "https://www.virustotal.com/api/v3/files",
                    headers=headers,
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                scan_id = result['data']['id']
                
                self.dashboard.current_action = "VT ANALYSIS"
                self.dashboard.scan_progress = 70
                self.dashboard.render_full()
                
                # Start polling in background
                self._poll_results(scan_id, file_path, hashes, threat_score, findings)
            else:
                print(f"{BRIGHT_RED}[!] Upload failed (HTTP {response.status_code}){RESET}")
                # Even if VT fails, we still have local results
                self.dashboard.scan_progress = 100
                self.dashboard.current_action = "COMPLETE (LOCAL)"
                self.dashboard.render_full()
                
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Error: {e}{RESET}")

    def _poll_results(self, scan_id: str, file_path: str, hashes: Dict, local_score: int = 0, local_findings: List = None):
        """Background polling with SOC Dashboard updates and report generation"""
        url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
        headers = {"x-apikey": CONFIG['VT_API_KEY']}
        
        self.dashboard.current_action = "POLLING VT RESULTS"
        
        for attempt in range(15):
            time.sleep(30)
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    status = result['data']['attributes']['status']
                    
                    if status == 'completed':
                        stats = result['data']['attributes']['stats']
                        vt_malicious = stats.get('malicious', 0)
                        
                        # Combine local and VT scores
                        final_score = max(local_score, (vt_malicious / sum(stats.values()) * 100) if sum(stats.values()) > 0 else 0)
                        
                        self.dashboard.add_finding(os.path.basename(file_path), final_score, {
                            'vt_stats': stats,
                            'local_score': local_score,
                            'local_findings': local_findings,
                            'combined_score': final_score
                        })
                        self.dashboard.scan_progress = 100
                        self.dashboard.current_action = "COMPLETE"
                        self.dashboard.render_full()
                        
                        # Generate operator advice
                        advice = self.dashboard.operator.generate_operator_advice(
                            "file_scan",
                            self.dashboard.findings
                        )
                        print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                        print(center_text(f"{BRIGHT_MAGENTA}📋 SCAN COMPLETE - OPERATOR ADVISORY{RESET}"))
                        print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                        print(advice)
                        
                        # Show combined results
                        if local_score > 0:
                            print(f"\n{BRIGHT_YELLOW}📊 Local Detection Score: {local_score}%{RESET}")
                        print(f"{BRIGHT_YELLOW}📊 VirusTotal Detections: {vt_malicious}/{sum(stats.values())}{RESET}")
                        print(f"{BRIGHT_RED if final_score > 50 else BRIGHT_GREEN}📊 Final Risk Score: {final_score:.1f}%{RESET}")
                        
<<<<<<< HEAD
                        # Save report FIRST before trying to read it
=======
                        # Save report
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                        report_results = {
                            'file_name': os.path.basename(file_path),
                            'file_path': file_path,
                            'local_threat_score': local_score,
                            'local_findings': local_findings,
                            'vt_detections': vt_malicious,
                            'vt_total_scans': sum(stats.values()),
                            'final_risk_score': final_score,
                            'md5': hashes.get('md5', 'N/A'),
                            'sha256': hashes.get('sha256', 'N/A')
                        }
<<<<<<< HEAD
                        json_file, pdf_file = ReportGenerator.save_report("file_scan", os.path.basename(file_path), report_results, self.dashboard)
                        
                        # Verify file exists before trying to read it
                        if json_file and os.path.exists(json_file):
                            print(f"{BRIGHT_GREEN}[✓] JSON report saved: {json_file}{RESET}")
                        else:
                            print(f"{BRIGHT_YELLOW}[!] JSON report may not have been saved properly{RESET}")
=======
                        ReportGenerator.save_report("file_scan", os.path.basename(file_path), report_results, self.dashboard)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                        
                        # Auto-quarantine if infected
                        if final_score > 70:
                            choice = input(f"\n{BRIGHT_RED}Quarantine infected file? (Y/n): {RESET}").lower()
                            if choice != 'n':
                                self.quarantine_item(file_path=file_path)
                        return
                    else:
                        self.dashboard.scan_progress = 70 + int(attempt * 2)
                        self.dashboard.render_full()
                        
<<<<<<< HEAD
            except requests.exceptions.RequestException as e:
                print(f"{BRIGHT_RED}[!] Network error during polling: {e}{RESET}")
            except json.JSONDecodeError as e:
                print(f"{BRIGHT_RED}[!] Invalid JSON response: {e}{RESET}")
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            except Exception as e:
                print(f"{BRIGHT_RED}[!] Polling error: {e}{RESET}")
        
        print(f"{BRIGHT_YELLOW}[!] Results timeout. Scan ID: {scan_id}{RESET}")
<<<<<<< HEAD
        print(f"{BRIGHT_YELLOW}[!] You can check results later using: check_scan_result('{scan_id}'){RESET}")
        

# ===========================================
=======

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    def vt_bulk_scan(self, folder_path: str, max_files: int = 10):
        """Bulk scan folder with SOC Dashboard and summary report"""
        folder_path = os.path.expanduser(folder_path)
        
        if not os.path.isdir(folder_path):
            print(f"{BRIGHT_RED}[!] Invalid folder: {folder_path}{RESET}")
            return
        
        self.dashboard.current_action = f"BULK SCAN"
        self.dashboard.current_scan_target = os.path.basename(folder_path)
        self.dashboard.scan_progress = 0
        
        files = []
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames[:max_files]:
                files.append(os.path.join(root, filename))
        
        for i, file_path in enumerate(files):
            self.dashboard.current_action = f"SCANNING: {os.path.basename(file_path)}"
            self.dashboard.scan_progress = int((i / len(files)) * 100)
            self.dashboard.render_full()
            
            # No size limit check - all files will be scanned regardless of size
            self.vt_file_scan(file_path)
            time.sleep(1)  # Reduced delay between scans
        
        # Save comprehensive bulk scan report
        bulk_results = {
            'folder': folder_path,
            'total_files_scanned': len(files),
            'skipped_files': 0,  # No files skipped due to size limit
            'scan_summary': {
                'total_threats': sum(1 for f in self.dashboard.findings if f.get('malicious', 0) > 0),
                'total_clean': sum(1 for f in self.dashboard.findings if f.get('malicious', 0) == 0),
                'risk_level': self.dashboard.threat_level
            }
        }
        ReportGenerator.save_report("bulk_scan", os.path.basename(folder_path), bulk_results, self.dashboard)
        
        print(f"\n{BRIGHT_GREEN}[+] Bulk scan complete!{RESET}")
        print(f"{BRIGHT_CYAN}Files scanned: {len(files)}{RESET}")
        
        # Final operator guidance
        final_assessment = self.dashboard.operator.assess_threat(
            sum(1 for f in self.dashboard.findings if f.get('malicious', 0) > 0),
            len(self.dashboard.findings) if self.dashboard.findings else 1
        )
        print(f"{BRIGHT_CYAN}Final Risk Assessment: {final_assessment['color']}{final_assessment['risk']}{RESET}")
        print(f"{BRIGHT_CYAN}Recommended Action: {final_assessment['action'][:50]}{RESET}")
    
    def quarantine_item(self, file_path: str = None, file_hash: str = None):
        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            dest = QUARANTINE_DIR / f"quarantined_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(file_path, dest)
            print(f"{BRIGHT_GREEN}[✓] Quarantined: {dest}{RESET}")
            
            log_file = WORKSPACE / "logs" / "quarantine.log"
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {CONFIG['SOC_OPERATOR_NAME']} | QUARANTINED | {file_path} -> {dest}\n")
                
        elif file_hash:
            hash_file = QUARANTINE_DIR / "quarantined_hashes.txt"
            with open(hash_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {CONFIG['SOC_OPERATOR_NAME']} | {file_hash}\n")
            print(f"{BRIGHT_GREEN}[✓] Malicious hash recorded in quarantine database{RESET}")
    
    def check_scan_result(self, scan_id: str):
        """Check previous scan results with SOC Dashboard and report generation"""
        self.dashboard.current_action = f"RETRIEVING SCAN"
        self.dashboard.current_scan_target = scan_id[:16]
        self.dashboard.render_full()
        
        url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
        headers = {"x-apikey": CONFIG['VT_API_KEY']}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                stats = result['data']['attributes']['stats']
                malicious = stats.get('malicious', 0)
                
                self.dashboard.add_finding(scan_id, malicious, stats)
                self.dashboard.scan_progress = 100
                self.dashboard.current_action = "COMPLETE"
                self.dashboard.render_full()
                
                advice = self.dashboard.operator.generate_operator_advice(
                    "hash_lookup",
                    self.dashboard.findings
                )
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(center_text(f"{BRIGHT_MAGENTA}📋 PREVIOUS SCAN RESULTS{RESET}"))
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                print(advice)
                
                # Save report for previous scan check
                report_results = {
                    'scan_id': scan_id,
                    'detections': malicious,
                    'total_scans': sum(stats.values()),
                    'status': result['data']['attributes']['status']
                }
                ReportGenerator.save_report("check_scan", scan_id, report_results, self.dashboard)
            else:
                print(f"{BRIGHT_RED}[!] Results not available{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Error: {e}{RESET}")
    
    def view_quarantine(self):
        print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
        print(center_text(f"{BRIGHT_MAGENTA}📁 QUARANTINE DIRECTORY{RESET}"))
        print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
        
        if QUARANTINE_DIR.exists():
            items = list(QUARANTINE_DIR.iterdir())
            if items:
                for item in items:
                    size = item.stat().st_size if item.is_file() else "DIR"
                    mod_time = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    print(f"  {BRIGHT_RED}⚠️{RESET} {item.name:<50} {size:>10} bytes  {mod_time}")
            else:
                print(f"  {BRIGHT_GREEN}✓ Quarantine is empty - System appears clean{RESET}")
        else:
            print(f"  {BRIGHT_YELLOW}Quarantine directory not found{RESET}")
        
        log_file = WORKSPACE / "logs" / "quarantine.log"
        if log_file.exists():
            print(f"\n{BRIGHT_CYAN}{'─'*80}{RESET}")
            print(center_text(f"{BRIGHT_YELLOW}📋 QUARANTINE LOG{RESET}"))
            print(f"{BRIGHT_CYAN}{'─'*80}{RESET}")
            with open(log_file, 'r') as f:
                lines = f.readlines()[-5:]
                for line in lines:
                    print(f"  {line.strip()}")

# -------------------------------
# MAIN MENU
# -------------------------------

def vt_scan_menu(operator=None, session=None):
    scanner = VirusTotalScanner(operator, session)
    
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
{BRIGHT_CYAN}│{RESET} {BRIGHT_RED}0.{RESET} Exit & Shutdown{' ' * 40}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└{'─' * 60}┘{RESET}"""
        print(center_text(menu_box))
        print()
        
        operator = CONFIG.get('SOC_OPERATOR_NAME') or "OP-UNKNOWN"
        session = CONFIG.get('SOC_SESSION_ID') or "SESSION-UNKNOWN"
        print(center_text(f"{BRIGHT_YELLOW}[{operator}@{session} ~]$ {RESET}"))
         
        choice = input(center_text(f"{BRIGHT_GREEN}Select operation: {RESET}")).strip()
        
        if choice == "1":
            file_hash = input(center_text(f"{BRIGHT_CYAN}Enter file hash (MD5/SHA1/SHA256): {RESET}")).strip()
            if file_hash:
                scanner.vt_hash_lookup(file_hash)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "2":
            file_path = input(center_text(f"{BRIGHT_CYAN}File path to scan: {RESET}")).strip()
            if file_path:
                scanner.vt_file_scan(file_path)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "3":
            folder_path = input(center_text(f"{BRIGHT_CYAN}Folder path to scan: {RESET}")).strip()
            max_files = input(center_text(f"{BRIGHT_CYAN}Max files to scan (default 10): {RESET}")).strip()
            max_files = int(max_files) if max_files else 10
            if folder_path:
                scanner.vt_bulk_scan(folder_path, max_files)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "4":
            scan_id = input(center_text(f"{BRIGHT_CYAN}Enter scan ID: {RESET}")).strip()
            if scan_id:
                scanner.check_scan_result(scan_id)
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "5":
            scanner.view_quarantine()
            input(center_text(f"{DIM}Press Enter to continue...{RESET}"))
            
        elif choice == "0":
            print(center_text(f"{BRIGHT_RED}⚠️  CLOSING...{RESET}"))
            matrix_rain(0.5, 3)
            print(center_text(f"{BRIGHT_GREEN}✅ DSTerminal SOC - Session Terminated{RESET}"))
            print(center_text(f"{BRIGHT_CYAN}Operator: {CONFIG['SOC_OPERATOR_NAME']} | Session: {CONFIG['SOC_SESSION_ID']}{RESET}"))
            break
        
        else:
            print(center_text(f"{BRIGHT_RED}[!] Invalid operation code{RESET}"))
            time.sleep(1)

# -------------------------------
# ENTRY POINT
# -------------------------------

if __name__ == "__main__":
    clear_screen()
    
    print(center_text(f"{BRIGHT_GREEN}╔{'═' * 80}╗{RESET}"))
    print(center_text(f"{BRIGHT_GREEN}║{RESET} {BRIGHT_MAGENTA}🚀 DSTERMINAL SOC PLATFORM INITIALIZING 🚀{RESET} {BRIGHT_GREEN}║{RESET}"))
    print(center_text(f"{BRIGHT_GREEN}╚{'═' * 80}╝{RESET}"))
    
    matrix_rain(1, 5)
    
    typewriter_effect(center_text(f"{BRIGHT_CYAN}🔐 Establishing secure session...{RESET}"), 0.03)
    time.sleep(0.5)
    typewriter_effect(center_text(f"{BRIGHT_CYAN}🛡️ Loading threat intelligence modules...{RESET}"), 0.03)
    time.sleep(0.5)
    typewriter_effect(center_text(f"{BRIGHT_CYAN}📡 Connecting to VirusTotal API...{RESET}"), 0.03)
    time.sleep(0.5)
    typewriter_effect(center_text(f"{BRIGHT_GREEN}✅ Session established: {CONFIG['SOC_SESSION_ID']}{RESET}"), 0.03)
    time.sleep(1)
    
    vt_scan_menu()