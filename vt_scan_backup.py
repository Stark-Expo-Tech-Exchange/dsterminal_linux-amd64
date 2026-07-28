continue from here: #!/usr/bin/env python3
"""
DSTerminal - VirusTotal Integration Module
Enhanced Cinematic SOC Dashboard with Graph Visualization
"""

import os
import sys
import time
import json
import shutil
import threading
import requests
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
    (workspace / "graphs").mkdir(exist_ok=True)
    
    return workspace

WORKSPACE = get_workspace_dir()
VT_REPORTS_DIR = WORKSPACE / "vt_reports"
QUARANTINE_DIR = WORKSPACE / "quarantine"
SOC_ALERTS_DIR = WORKSPACE / "soc_alerts"
GRAPHS_DIR = WORKSPACE / "graphs"

# -------------------------------
# CONFIGURATION
# -------------------------------

CONFIG = {
    'VT_API_KEY': '957166d424812a397e328022b84594a8c02757814f6c04518dce7e81179b4b79',
    'MAX_FILE_SIZE': 32 * 1024 * 1024,
    'RATE_LIMIT_DELAY': 15,
    'SOC_OPERATOR_NAME': 'WILSON-SON',
    'SOC_SESSION_ID': f"OP-{random.randint(10000, 99999):05X}",
}

# -------------------------------
# GLOWING COLORS & STYLING
# -------------------------------

RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
BLINK = '\033[5m'
HIDE = '\033[8m'

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
# ASCII GRAPH VISUALIZATION
# -------------------------------

class ASCIIGraph:
    """Generate ASCII art graphs for terminal display"""
    
    @staticmethod
    def draw_bar_chart(data: Dict[str, int], title: str = "Results", width: int = 40) -> str:
        """Draw a horizontal bar chart in ASCII"""
        if not data:
            return "No data available"
        
        max_value = max(data.values()) if data.values() else 1
        chart_lines = []
        
        chart_lines.append(f"{BRIGHT_CYAN}┌{'─' * (width + 4)}┐{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}{title:^{width}}{RESET} {BRIGHT_CYAN}│{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}├{'─' * (width + 4)}┤{RESET}")
        
        for label, value in data.items():
            bar_length = int((value / max_value) * width)
            bar = "█" * bar_length + "░" * (width - bar_length)
            
            # Color code based on value
            if value == 0:
                color = BRIGHT_GREEN
            elif value < 5:
                color = BRIGHT_YELLOW
            else:
                color = BRIGHT_RED
            
            chart_lines.append(f"{BRIGHT_CYAN}│{RESET} {color}{label[:15]:<15} [{bar}] {value}{RESET} {BRIGHT_CYAN}│{RESET}")
        
        chart_lines.append(f"{BRIGHT_CYAN}└{'─' * (width + 4)}┘{RESET}")
        return "\n".join(chart_lines)
    
    @staticmethod
    def draw_pie_chart(data: Dict[str, int], title: str = "Distribution", size: int = 15) -> str:
        """Draw a simple pie chart in ASCII"""
        if not data:
            return "No data available"
        
        total = sum(data.values())
        if total == 0:
            return "No data to display"
        
        chart_lines = []
        chart_lines.append(f"{BRIGHT_CYAN}┌{'─' * 40}┐{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}{title:^36}{RESET} {BRIGHT_CYAN}│{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}├{'─' * 40}┤{RESET}")
        
        # Simple pie chart using blocks
        pie_chars = ["⬤", "◉", "○", "◌", "◎", "●", "◐", "◑", "◒", "◓"]
        
        colors = [BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_RED, BRIGHT_BLUE, BRIGHT_MAGENTA, CYAN]
        color_idx = 0
        
        for label, value in data.items():
            percentage = (value / total) * 100
            pie_icon = pie_chars[color_idx % len(pie_chars)]
            color = colors[color_idx % len(colors)]
            
            # Create simple percentage bar
            bar_length = int(percentage / 5)
            bar = "▓" * bar_length + "░" * (20 - bar_length)
            
            chart_lines.append(f"{BRIGHT_CYAN}│{RESET} {color}{pie_icon}{RESET} {label:<15} {bar} {percentage:.1f}% ({value}){RESET} {BRIGHT_CYAN}│{RESET}")
            color_idx += 1
        
        chart_lines.append(f"{BRIGHT_CYAN}└{'─' * 40}┘{RESET}")
        return "\n".join(chart_lines)
    
    @staticmethod
    def draw_trend_line(data: List[int], title: str = "Trend Analysis", width: int = 40) -> str:
        """Draw a simple trend line graph"""
        if not data or len(data) < 2:
            return "Insufficient data for trend analysis"
        
        max_val = max(data)
        min_val = min(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        chart_lines = []
        chart_lines.append(f"{BRIGHT_CYAN}┌{'─' * (width + 4)}┐{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}{title:^{width}}{RESET} {BRIGHT_CYAN}│{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}├{'─' * (width + 4)}┤{RESET}")
        
        # Create the trend line
        line_points = []
        for i, val in enumerate(data):
            y_pos = int(((val - min_val) / range_val) * 8)  # 8 rows max
            line_points.append((i, y_pos))
        
        # Build the graph grid
        for row in range(9, -1, -1):
            line = f"{BRIGHT_CYAN}│{RESET} "
            for i in range(len(data)):
                y_positions = [p[1] for p in line_points if p[0] == i]
                if y_positions and row == y_positions[0]:
                    line += f"{BRIGHT_RED}●{RESET}"
                else:
                    line += "·"
            line += f" {BRIGHT_CYAN}│{RESET}"
            chart_lines.append(line)
        
        # X-axis labels
        x_axis = f"{BRIGHT_CYAN}│{RESET} " + "".join([str(i % 10) for i in range(len(data))]) + f" {BRIGHT_CYAN}│{RESET}"
        chart_lines.append(x_axis)
        chart_lines.append(f"{BRIGHT_CYAN}└{'─' * (width + 4)}┘{RESET}")
        
        return "\n".join(chart_lines)
    
    @staticmethod
    def draw_radar_chart(metrics: Dict[str, int], title: str = "Security Metrics") -> str:
        """Draw a simple radar/spider chart for security metrics"""
        if not metrics:
            return "No metrics available"
        
        chart_lines = []
        chart_lines.append(f"{BRIGHT_CYAN}┌{'─' * 50}┐{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}{title:^46}{RESET} {BRIGHT_CYAN}│{RESET}")
        chart_lines.append(f"{BRIGHT_CYAN}├{'─' * 50}┤{RESET}")
        
        # Create spider web visualization
        center_x = 25
        center_y = 6
        
        # Draw axes
        axes = ["THREAT", "RISK", "EXPOSURE", "IMPACT", "URGENCY", "COMPLEXITY"]
        
        for i, (label, value) in enumerate(metrics.items()):
            if i < len(axes):
                bar_length = int(value / 10) if value <= 10 else 10
                bar = "█" * bar_length + "░" * (10 - bar_length)
                
                if value < 3:
                    color = BRIGHT_GREEN
                elif value < 7:
                    color = BRIGHT_YELLOW
                else:
                    color = BRIGHT_RED
                
                chart_lines.append(f"{BRIGHT_CYAN}│{RESET} {color}{axes[i]:<10} [{bar}] {value}/10{RESET} {BRIGHT_CYAN}│{RESET}")
        
        chart_lines.append(f"{BRIGHT_CYAN}└{'─' * 50}┘{RESET}")
        return "\n".join(chart_lines)

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
        
    def render_soc_header(self):
        elapsed = (datetime.now() - self.session_start).seconds
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        
        glow = GLOW_FRAMES[self.glow_idx % len(GLOW_FRAMES)]
        
        header = f"""
{BRIGHT_CYAN}╔{'═' * 80}╗{RESET}
{BRIGHT_CYAN}║{RESET} {glow} {BRIGHT_MAGENTA}🔬 DSTERMINAL SOC - THREAT INTELLIGENCE PLATFORM 🔬{RESET} {glow} {BRIGHT_CYAN}║{RESET}
{BRIGHT_CYAN}╠{'═' * 80}╣{RESET}
{BRIGHT_CYAN}║{RESET} {BRIGHT_YELLOW}Operator:{RESET} {CONFIG['SOC_OPERATOR_NAME']:<20} {BRIGHT_YELLOW}Session:{RESET} {BRIGHT_GREEN}{CONFIG['SOC_SESSION_ID']}{RESET:<12} {BRIGHT_YELLOW}Uptime:{RESET} {BRIGHT_CYAN}{hours:02d}:{minutes:02d}:{seconds:02d}{RESET} {BRIGHT_CYAN}║{RESET}
{BRIGHT_CYAN}╚{'═' * 80}╝{RESET}"""
        print(center_text(header))
        
    def render_threat_radar(self):
        threat_icon = THREAT_FRAMES[self.threat_frame_idx % len(THREAT_FRAMES)]
        glow_icon = GLOW_FRAMES[self.glow_idx % len(GLOW_FRAMES)]
        
        if self.threat_level < 30:
            threat_color = BRIGHT_GREEN
            threat_text = "LOW"
            threat_bar = "█" * 3 + "░" * 7
        elif self.threat_level < 70:
            threat_color = BRIGHT_YELLOW
            threat_text = "MEDIUM"
            threat_bar = "█" * 6 + "░" * 4
        else:
            threat_color = BRIGHT_RED + BLINK
            threat_text = "CRITICAL"
            threat_bar = "█" * 10
        
        radar_sweep = ["🟢", "🟡", "🔴", "⚡"][self.threat_frame_idx % 4]
        
        radar = f"""
{BRIGHT_CYAN}┌{'─' * 32}┐{RESET}
{BRIGHT_CYAN}│{RESET} {threat_color}🛸 THREAT RADAR {threat_icon} {glow_icon}{RESET}{' ' * 12}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}├{'─' * 32}┤{RESET}
{BRIGHT_CYAN}│{RESET} {threat_color}Level: {threat_text}{RESET}{' ' * 21}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {threat_color}Score: {self.threat_level}%{RESET}{' ' * 20}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {threat_color}Bar: [{threat_bar}]{RESET}{' ' * 15}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {threat_color}Radar: {radar_sweep}{RESET}{' ' * 20}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└{'─' * 32}┘{RESET}"""
        return radar
    
    def render_scan_status(self):
        scan_icon = SCANNING_FRAMES[self.threat_frame_idx % len(SCANNING_FRAMES)]
        bar = PROGRESS_BARS[self.progress_bar_idx % len(PROGRESS_BARS)]
        
        if self.scan_progress < 30:
            bar_color = BRIGHT_RED
        elif self.scan_progress < 70:
            bar_color = BRIGHT_YELLOW
        else:
            bar_color = BRIGHT_GREEN
        
        status = f"""
{BRIGHT_CYAN}┌{'─' * 38}┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}{scan_icon} ACTIVE SCAN {scan_icon}{RESET}{' ' * 18}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}├{'─' * 38}┤{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Target:{RESET} {self.current_scan_target[:28]:<28}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Action:{RESET} {self.current_action[:28]:<28}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Progress:{RESET} {bar_color}[{bar}]{RESET} {self.scan_progress}%{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└{'─' * 38}┘{RESET}"""
        return status
    
    def render_stats_panel(self):
        total_threats = sum(1 for f in self.findings if f.get('malicious', 0) > 0)
        total_clean = len(self.findings) - total_threats
        total_scans = len(self.findings)
        
        stats = f"""
{BRIGHT_CYAN}┌{'─' * 30}┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GOLD}📊 SOC STATISTICS 📊{RESET}{' ' * 7}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}├{'─' * 30}┤{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Total Scans:{RESET} {BRIGHT_CYAN}{total_scans:<4}{RESET}{' ' * 13}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}Clean:{RESET} {total_clean:<4}{' ' * 14}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_RED}Threats:{RESET} {total_threats:<4}{' ' * 13}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}Detect Rate:{RESET} {self.threat_level}%{' ' * 12}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└{'─' * 30}┘{RESET}"""
        return stats
    
    def render_operator_guidance(self):
        assessment = self.operator.assess_threat(
            sum(1 for f in self.findings if f.get('malicious', 0) > 0),
            len(self.findings) if self.findings else 1
        )
        
        guidance = f"""
{BRIGHT_YELLOW}╔{'═' * 80}╗{RESET}
{BRIGHT_YELLOW}║{RESET} {assessment['glow']} {BRIGHT_MAGENTA}🎯 SOC OPERATOR GUIDANCE {assessment['glow']}{RESET}{' ' * 47}{BRIGHT_YELLOW}║{RESET}
{BRIGHT_YELLOW}╠{'═' * 80}╣{RESET}
{BRIGHT_YELLOW}║{RESET} {BRIGHT_CYAN}Risk Assessment:{RESET} {assessment['color']}{assessment['risk']}{RESET} ({assessment['priority']}){' ' * 45}{BRIGHT_YELLOW}║{RESET}
{BRIGHT_YELLOW}║{RESET} {BRIGHT_CYAN}Action Required:{RESET} {assessment['action'][:62]:<62}{BRIGHT_YELLOW}║{RESET}
{BRIGHT_YELLOW}╚{'═' * 80}╝{RESET}"""
        return center_text(guidance)
    
    def render_graph_panel(self):
        """Render graph visualization panel in the dashboard"""
        if len(self.findings) < 2:
            return ""
        
        # Prepare data for graphs
        threat_counts = []
        for i, finding in enumerate(self.findings[-10:]):  # Last 10 findings
            threat_counts.append(finding.get('malicious', 0))
        
        # Distribution data
        total_threats = sum(1 for f in self.findings if f.get('malicious', 0) > 0)
        total_clean = len(self.findings) - total_threats
        
        distribution = {
            "CLEAN": total_clean,
            "THREATS": total_threats
        }
        
        # Severity distribution
        severity = {
            "LOW": sum(1 for f in self.findings if 0 < f.get('malicious', 0) <= 3),
            "MEDIUM": sum(1 for f in self.findings if 3 < f.get('malicious', 0) <= 10),
            "HIGH": sum(1 for f in self.findings if f.get('malicious', 0) > 10)
        }
        
        graph_panel = f"""
{BRIGHT_CYAN}╔{'═' * 80}╗{RESET}
{BRIGHT_CYAN}║{RESET} {BRIGHT_MAGENTA}📊 REAL-TIME THREAT VISUALIZATION 📊{RESET}{' ' * 38}{BRIGHT_CYAN}║{RESET}
{BRIGHT_CYAN}╠{'═' * 80}╣{RESET}
"""
        
        # Add bar chart
        graph_panel += "\n" + ASCIIGraph.draw_bar_chart(distribution, "Scan Results", 50)
        graph_panel += "\n" + ASCIIGraph.draw_pie_chart(severity, "Threat Severity Distribution", 15)
        
        if len(threat_counts) >= 3:
            graph_panel += "\n" + ASCIIGraph.draw_trend_line(threat_counts, "Threat Detection Trend", 50)
        
        # Security metrics radar
        metrics = {
            "THREAT_LEVEL": min(10, self.threat_level // 10),
            "RISK_SCORE": min(10, self.threat_level // 10),
            "EXPOSURE": min(10, total_threats),
            "IMPACT": min(10, total_threats * 2),
            "URGENCY": min(10, self.threat_level // 8),
            "COMPLEXITY": min(10, len(self.findings) // 2)
        }
        graph_panel += "\n" + ASCIIGraph.draw_radar_chart(metrics, "Security Posture Metrics")
        
        graph_panel += f"\n{BRIGHT_CYAN}╚{'═' * 80}╝{RESET}"
        return center_text(graph_panel)
    
    def render_results_panel(self):
        if not self.findings:
            results = f"""
{BRIGHT_CYAN}┌{'─' * 80}┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_YELLOW}🔍 AWAITING SCAN RESULTS - STANDING BY 🔍{RESET}{' ' * 37}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}└{'─' * 80}┘{RESET}"""
            return center_text(results)
        
        results = f"""
{BRIGHT_GREEN}┌{'─' * 80}┐{RESET}
{BRIGHT_GREEN}│{RESET} {BRIGHT_MAGENTA}📋 LIVE SCAN RESULTS & ALERTS 📋{RESET}{' ' * 38}{BRIGHT_GREEN}│{RESET}
{BRIGHT_GREEN}├{'─' * 80}┤{RESET}"""
        
        for finding in self.findings[-8:]:
            name = finding.get('name', 'Unknown')[:40]
            malicious = finding.get('malicious', 0)
            timestamp = finding.get('timestamp', datetime.now()).strftime("%H:%M:%S") if isinstance(finding.get('timestamp'), datetime) else "N/A"
            
            if malicious > 0:
                color = BRIGHT_RED
                status = f"⚠️ {malicious} detections"
                alert_icon = "🔴"
            else:
                color = BRIGHT_GREEN
                status = "✓ CLEAN"
                alert_icon = "🟢"
            
            results += f"\n{color}│ {alert_icon} {timestamp} | {name:<40} | {status:>25} │{RESET}"
        
        results += f"\n{BRIGHT_GREEN}└{'─' * 80}┘{RESET}"
        return center_text(results)
    
    def render_layer2(self):
        radar = self.render_threat_radar()
        status = self.render_scan_status()
        stats = self.render_stats_panel()
        
        radar_lines = radar.split('\n')
        status_lines = status.split('\n')
        stats_lines = stats.split('\n')
        
        max_lines = max(len(radar_lines), len(status_lines), len(stats_lines))
        
        radar_width = 34
        status_width = 40
        stats_width = 32
        spacer = "   "
        
        radar_lines += [' ' * radar_width] * (max_lines - len(radar_lines))
        status_lines += [' ' * status_width] * (max_lines - len(status_lines))
        stats_lines += [' ' * stats_width] * (max_lines - len(stats_lines))
        
        combined = []
        for r, s, st in zip(radar_lines, status_lines, stats_lines):
            r_padded = r.ljust(radar_width)
            s_padded = s.ljust(status_width)
            st_padded = st.ljust(stats_width)
            combined.append(f"{r_padded}{spacer}{s_padded}{spacer}{st_padded}")
        
        return '\n'.join(combined)
    
    def animate(self, duration: float = 0.08):
        self.threat_frame_idx += 1
        self.progress_bar_idx += 1
        self.glow_idx += 1
        time.sleep(duration)
    
    def render_full(self, show_graphs: bool = True):
        clear_screen()
        
        self.render_soc_header()
        print()
        print()
        
        print(self.render_layer2())
        print()
        print()
        
        print(self.render_operator_guidance())
        print()
        
        if show_graphs and len(self.findings) >= 2:
            print(self.render_graph_panel())
            print()
        
        print(self.render_results_panel())
        print()
        
        self.animate(0.05)
    
    def update_threat_level(self, malicious_count: int, total_scans: int = 90):
        if total_scans > 0:
            ratio = malicious_count / total_scans
            self.threat_level = min(100, int(ratio * 100 * 2))
    
    def add_finding(self, name: str, malicious: int, details: Dict = None):
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
# REPORT GENERATION SYSTEM WITH GRAPHS
# -------------------------------

class ReportGenerator:
    """Handles JSON and PDF report generation with graph visualization"""
    
    @staticmethod
    def save_json_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Path:
        """Save JSON report for any scan type"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = "".join(c for c in str(target) if c.isalnum() or c in '.-_')[:30]
        
        # Prepare graph data for JSON
        total_threats = sum(1 for f in dashboard.findings if f.get('malicious', 0) > 0)
        total_clean = len(dashboard.findings) - total_threats
        
        severity_data = {
            "LOW": sum(1 for f in dashboard.findings if 0 < f.get('malicious', 0) <= 3),
            "MEDIUM": sum(1 for f in dashboard.findings if 3 < f.get('malicious', 0) <= 10),
            "HIGH": sum(1 for f in dashboard.findings if f.get('malicious', 0) > 10)
        }
        
        threat_trend = []
        for finding in dashboard.findings[-20:]:
            threat_trend.append(finding.get('malicious', 0))
        
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
                'total_threats': total_threats,
                'total_clean': total_clean,
                'risk_level': dashboard.threat_level,
                'current_action': dashboard.current_action
            },
            'graph_data': {
                'distribution': {'CLEAN': total_clean, 'THREATS': total_threats},
                'severity': severity_data,
                'threat_trend': threat_trend,
                'security_metrics': {
                    'threat_level': min(10, dashboard.threat_level // 10),
                    'risk_score': min(10, dashboard.threat_level // 10),
                    'exposure': min(10, total_threats),
                    'impact': min(10, total_threats * 2),
                    'urgency': min(10, dashboard.threat_level // 8)
                }
            },
            'results': results
        }
        
        json_file = VT_REPORTS_DIR / f"{scan_type}_{safe_target}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"{BRIGHT_GREEN}[✓] JSON report saved: {json_file}{RESET}")
        return json_file
    
    @staticmethod
    def generate_graph_image(data: Dict, output_path: Path) -> Optional[Path]:
        """Generate graph image using matplotlib for PDF reports"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.patches import Circle, Rectangle, Arc
            
            plt.style.use('dark_background')
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.patch.set_facecolor('#0a0a0a')
            
            # 1. Bar chart for distribution
            ax1 = axes[0, 0]
            distribution = data.get('distribution', {'CLEAN': 0, 'THREATS': 0})
            categories = list(distribution.keys())
            values = list(distribution.values())
            colors_bar = ['#00ff00', '#ff0000'] if 'THREATS' in categories else ['#00ff00']
            bars = ax1.bar(categories, values, color=colors_bar, edgecolor='white', linewidth=1)
            ax1.set_title('Scan Results Distribution', color='#00ff00', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Count', color='white')
            ax1.tick_params(colors='white')
            ax1.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#0a0a0a')
            ax1.spines['bottom'].set_color('white')
            ax1.spines['left'].set_color('white')
            
            # 2. Pie chart for severity
            ax2 = axes[0, 1]
            severity = data.get('severity', {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0})
            severity_colors = ['#00ff00', '#ffff00', '#ff0000']
            severity_labels = [f"{k}\n({v})" for k, v in severity.items() if v > 0]
            severity_values = [v for v in severity.values() if v > 0]
            if severity_values:
                ax2.pie(severity_values, labels=severity_labels, colors=severity_colors[:len(severity_values)],
                        autopct='%1.1f%%', textprops={'color': 'white', 'fontsize': 10})
            ax2.set_title('Threat Severity Distribution', color='#00ff00', fontsize=12, fontweight='bold')
            ax2.set_facecolor('#1a1a1a')
            
            # 3. Trend line
            ax3 = axes[1, 0]
            trend = data.get('threat_trend', [])
            if len(trend) >= 2:
                ax3.plot(trend, color='#ff4444', linewidth=2, marker='o', markersize=6, 
                        markerfacecolor='yellow', markeredgecolor='white')
                ax3.fill_between(range(len(trend)), trend, alpha=0.3, color='red')
            ax3.set_title('Threat Detection Trend', color='#00ff00', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Scan Sequence', color='white')
            ax3.set_ylabel('Detection Count', color='white')
            ax3.tick_params(colors='white')
            ax3.set_facecolor('#1a1a1a')
            ax3.spines['bottom'].set_color('white')
            ax3.spines['left'].set_color('white')
            ax3.grid(True, alpha=0.3, color='white')
            
            # 4. Radar chart for security metrics
            ax4 = axes[1, 1]
            metrics = data.get('security_metrics', {})
            if metrics:
                categories_radar = list(metrics.keys())
                values_radar = list(metrics.values())
                values_radar += values_radar[:1]  # Close the loop
                
                angles = [n / float(len(categories_radar)) * 2 * 3.14159 for n in range(len(categories_radar))]
                angles += angles[:1]
                
                ax4.polar(angles, values_radar, 'o-', linewidth=2, color='#00ff00')
                ax4.fill(angles, values_radar, alpha=0.25, color='#00ff00')
                ax4.set_xticks(angles[:-1])
                ax4.set_xticklabels(categories_radar, color='white', fontsize=8)
                ax4.set_title('Security Posture Metrics', color='#00ff00', fontsize=12, fontweight='bold', pad=20)
                ax4.set_facecolor('#1a1a1a')
                ax4.grid(True, color='white', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, facecolor='#0a0a0a', edgecolor='none')
            plt.close()
            
            return output_path
        except ImportError:
            print(f"{BRIGHT_YELLOW}[!] Matplotlib not installed. Graph image skipped.{RESET}")
            return None
    
    @staticmethod
    def save_pdf_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Optional[Path]:
        """Save PDF report with embedded graph visualizations"""
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
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
        
        # Prepare graph data
        total_threats = sum(1 for f in dashboard.findings if f.get('malicious', 0) > 0)
        total_clean = len(dashboard.findings) - total_threats
        
        severity_data = {
            "LOW": sum(1 for f in dashboard.findings if 0 < f.get('malicious', 0) <= 3),
            "MEDIUM": sum(1 for f in dashboard.findings if 3 < f.get('malicious', 0) <= 10),
            "HIGH": sum(1 for f in dashboard.findings if f.get('malicious', 0) > 10)
        }
        
        threat_trend = []
        for finding in dashboard.findings[-20:]:
            threat_trend.append(finding.get('malicious', 0))
        
        graph_data = {
            'distribution': {'CLEAN': total_clean, 'THREATS': total_threats},
            'severity': severity_data,
            'threat_trend': threat_trend,
            'security_metrics': {
                'Threat': min(10, dashboard.threat_level // 10),
                'Risk': min(10, dashboard.threat_level // 10),
                'Exposure': min(10, total_threats),
                'Impact': min(10, total_threats * 2),
                'Urgency': min(10, dashboard.threat_level // 8)
            }
        }
        
        # Generate graph image
        graph_image_path = GRAPHS_DIR / f"graph_{safe_target}_{timestamp}.png"
        graph_image = ReportGenerator.generate_graph_image(graph_data, graph_image_path)
        
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
        
        # Add graph image if generated
        if graph_image and graph_image.exists():
            img = Image(str(graph_image), width=6*inch, height=5*inch)
            elements.append(img)
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
        ]))
        elements.append(table)
        
        # Statistics summary
        elements.append(Spacer(1, 0.3 * inch))
        stats_text = f"""
        <b>Summary Statistics:</b><br/>
        • Total Scans: {len(dashboard.findings)}<br/>
        • Threats Detected: {total_threats}<br/>
        • Clean Files: {total_clean}<br/>
        • Detection Rate: {dashboard.threat_level}%<br/>
        • Severity - LOW: {severity_data.get('LOW', 0)} | MEDIUM: {severity_data.get('MEDIUM', 0)} | HIGH: {severity_data.get('HIGH', 0)}
        """
        elements.append(Paragraph(stats_text, styles["Normal"]))
        
        doc.build(elements)
        print(f"{BRIGHT_GREEN}[✓] PDF report saved: {pdf_file}{RESET}")
        return pdf_file
    
    @staticmethod
    def save_report(scan_type: str, target: str, results: Dict, dashboard: SOCDashboard) -> Tuple[Path, Optional[Path]]:
        """Save both JSON and PDF reports with graphs"""
        json_file = ReportGenerator.save_json_report(scan_type, target, results, dashboard)
        pdf_file = ReportGenerator.save_pdf_report(scan_type, target, results, dashboard)
        return json_file, pdf_file

# -------------------------------
# ENHANCED VIRUSTOTAL SCANNER
# -------------------------------

class VirusTotalScanner:
    def __init__(self):
        self.dashboard = SOCDashboard()
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
    
    def display_scan_summary_graphs(self):
        """Display graph visualizations after scan completion"""
        if len(self.dashboard.findings) < 2:
            return
        
        print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
        print(center_text(f"{BRIGHT_MAGENTA}📊 SCAN SUMMARY VISUALIZATION 📊{RESET}"))
        print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
        
        # Prepare data
        total_threats = sum(1 for f in self.dashboard.findings if f.get('malicious', 0) > 0)
        total_clean = len(self.dashboard.findings) - total_threats
        
        distribution = {
            "CLEAN": total_clean,
            "THREATS": total_threats
        }
        
        severity = {
            "LOW": sum(1 for f in self.dashboard.findings if 0 < f.get('malicious', 0) <= 3),
            "MEDIUM": sum(1 for f in self.dashboard.findings if 3 < f.get('malicious', 0) <= 10),
            "HIGH": sum(1 for f in self.dashboard.findings if f.get('malicious', 0) > 10)
        }
        
        # Display graphs
        print(ASCIIGraph.draw_bar_chart(distribution, "Overall Scan Results", 50))
        print()
        print(ASCIIGraph.draw_pie_chart(severity, "Threat Severity Distribution", 15))
        
        # Show trend if enough data
        threat_trend = []
        for finding in self.dashboard.findings[-10:]:
            threat_trend.append(finding.get('malicious', 0))
        
        if len(threat_trend) >= 3:
            print()
            print(ASCIIGraph.draw_trend_line(threat_trend, "Threat Detection Trend (Last 10 Scans)", 50))
        
        # Security metrics radar
        metrics = {
            "THREAT": min(10, self.dashboard.threat_level // 10),
            "RISK": min(10, self.dashboard.threat_level // 10),
            "EXPOSURE": min(10, total_threats),
            "IMPACT": min(10, total_threats * 2),
            "URGENCY": min(10, self.dashboard.threat_level // 8)
        }
        print()
        print(ASCIIGraph.draw_radar_chart(metrics, "Security Posture Assessment"))
        
        print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
    
    def _validate_api(self) -> bool:
        if not CONFIG.get('VT_API_KEY'):
            print(f"{BRIGHT_RED}[!] VirusTotal API key not configured!{RESET}")
            print(f"{BRIGHT_YELLOW}[>] Please add your API key to CONFIG['VT_API_KEY']{RESET}")
            return False
        return True
    
    def vt_hash_lookup(self, file_hash: str):
        """Cinematic hash lookup with SOC Dashboard and graph visualization"""
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
                self.dashboard.render_full(show_graphs=True)
                
                # Generate operator advice
                advice = self.dashboard.operator.generate_operator_advice(
                    "hash_lookup", 
                    self.dashboard.findings
                )
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(center_text(f"{BRIGHT_MAGENTA}📋 OPERATOR ADVISORY{RESET}"))
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                print(advice)
                
                # Display graph visualization
                self.display_scan_summary_graphs()
                
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
        """Cinematic file upload with SOC Dashboard and graph visualization"""
        if not self._validate_api():
            return
        
        file_path = os.path.expanduser(file_path)
        
        if not os.path.exists(file_path):
            print(f"{BRIGHT_RED}[!] File not found: {file_path}{RESET}")
            return
        
        file_size = os.path.getsize(file_path)
        if file_size > CONFIG['MAX_FILE_SIZE']:
            print(f"{BRIGHT_RED}[!] File exceeds size limit ({file_size/1024/1024:.2f}MB > 32MB){RESET}")
            return
        
        hashes = self.calculate_file_hash(file_path)
        
        self.dashboard.current_action = f"UPLOADING"
        self.dashboard.current_scan_target = os.path.basename(file_path)
        self.dashboard.scan_progress = 0
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                headers = {"x-apikey": CONFIG['VT_API_KEY']}
                
                for progress in range(10, 101, 20):
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
                
                self.dashboard.current_action = "ANALYZING"
                self.dashboard.scan_progress = 50
                self.dashboard.render_full()
                
                # Start polling in background
                self._poll_results(scan_id, file_path, hashes)
            else:
                print(f"{BRIGHT_RED}[!] Upload failed (HTTP {response.status_code}){RESET}")
                
        except Exception as e:
            print(f"{BRIGHT_RED}[!] Error: {e}{RESET}")
    
    def _poll_results(self, scan_id: str, file_path: str, hashes: Dict):
        """Background polling with SOC Dashboard updates and graph visualization"""
        url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
        headers = {"x-apikey": CONFIG['VT_API_KEY']}
        
        self.dashboard.current_action = "POLLING RESULTS"
        
        for attempt in range(15):
            time.sleep(30)
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    status = result['data']['attributes']['status']
                    
                    if status == 'completed':
                        stats = result['data']['attributes']['stats']
                        malicious = stats.get('malicious', 0)
                        
                        self.dashboard.add_finding(os.path.basename(file_path), malicious, stats)
                        self.dashboard.scan_progress = 100
                        self.dashboard.current_action = "COMPLETE"
                        self.dashboard.render_full(show_graphs=True)
                        
                        # Generate operator advice
                        advice = self.dashboard.operator.generate_operator_advice(
                            "file_scan",
                            self.dashboard.findings
                        )
                        print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                        print(center_text(f"{BRIGHT_MAGENTA}📋 SCAN COMPLETE - OPERATOR ADVISORY{RESET}"))
                        print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                        print(advice)
                        
                        # Display graph visualization
                        self.display_scan_summary_graphs()
                        
                        # Save report for file scan
                        report_results = {
                            'file_name': os.path.basename(file_path),
                            'file_path': file_path,
                            'file_size': os.path.getsize(file_path),
                            'md5': hashes.get('md5', 'N/A'),
                            'sha1': hashes.get('sha1', 'N/A'),
                            'sha256': hashes.get('sha256', 'N/A'),
                            'detections': malicious,
                            'total_scans': sum(stats.values()),
                            'scan_id': scan_id
                        }
                        ReportGenerator.save_report("file_scan", os.path.basename(file_path), report_results, self.dashboard)
                        
                        # Auto-quarantine if infected
                        if malicious > 0:
                            choice = input(f"\n{BRIGHT_RED}Auto-quarantine infected file? (y/N): {RESET}").lower()
                            if choice == 'y':
                                self.quarantine_item(file_path=file_path)
                        return
                    else:
                        self.dashboard.scan_progress = 50 + int(attempt * 3.3)
                        self.dashboard.render_full()
                        
            except Exception as e:
                print(f"{BRIGHT_RED}[!] Polling error: {e}{RESET}")
        
        print(f"{BRIGHT_YELLOW}[!] Results timeout. Check later with scan ID: {scan_id}{RESET}")
    
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
            
            file_size = os.path.getsize(file_path)
            if file_size <= CONFIG['MAX_FILE_SIZE']:
                self.vt_file_scan(file_path)
                time.sleep(CONFIG['RATE_LIMIT_DELAY'])
            else:
                print(f"{BRIGHT_YELLOW}[!] Skipping {os.path.basename(file_path)} (>{CONFIG['MAX_FILE_SIZE']/1024/1024:.0f}MB){RESET}")
        
        # Display final graph visualization
        self.display_scan_summary_graphs()
        
        # Save comprehensive bulk scan report
        bulk_results = {
            'folder': folder_path,
            'total_files_scanned': len(files),
            'skipped_files': max(0, max_files - len(files)),
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
        """Check previous scan results with SOC Dashboard and graph visualization"""
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
                self.dashboard.render_full(show_graphs=True)
                
                advice = self.dashboard.operator.generate_operator_advice(
                    "hash_lookup",
                    self.dashboard.findings
                )
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(center_text(f"{BRIGHT_MAGENTA}📋 PREVIOUS SCAN RESULTS{RESET}"))
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")
                print(advice)
                
                # Display graph visualization
                self.display_scan_summary_graphs()
                
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

def vt_scan_menu():
    scanner = VirusTotalScanner()
    
    while True:
        clear_screen()
        
        print(f"{BRIGHT_RED}{'═' * 80}{RESET}")
        print(center_text(f"{BRIGHT_MAGENTA}{BLINK}🔬 DSTERMINAL SOC - THREAT INTELLIGENCE PLATFORM 🔬{RESET}"))
        print(f"{BRIGHT_RED}{'═' * 80}{RESET}")
        
        matrix_rain(0.3, 2)
        
        print()
        menu_box = f"""
{BRIGHT_CYAN}┌{'─' * 60}┐{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_MAGENTA}🔍 OPERATION SELECTION{BRIGHT_CYAN}{' ' * 37}│{RESET}
{BRIGHT_CYAN}├{'─' * 60}┤{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}1.{RESET} Hash Lookup (VT Intelligence){' ' * 30}{BRIGHT_CYAN}│{RESET}
{BRIGHT_CYAN}│{RESET} {BRIGHT_GREEN}2.{RESET} File Scan (Upload & Analyze){' ' * 30}{BRIGHT_CYAN}│{RESET}
{