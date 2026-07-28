#!/usr/bin/env python3
"""
DSTerminal Reconnaissance Module
Usage: python recon.py <target>
       Or import as module: from recon import run_recon, recon_menu
"""

import os
import sys
import threading
import itertools
import time
import shutil
import subprocess
import random
import math
from datetime import datetime
from pathlib import Path

# -------------------------------
# WORKSPACE DIRECTORY SETUP
# -------------------------------

def get_workspace_dir() -> Path:
    """Get the DSTerminal workspace directory"""
    home = Path.home()
    workspace = home / "dsterminal_workspace"
    workspace.mkdir(exist_ok=True)
    
    # Create subdirectories for different report types
    # (workspace / "integrity_reports").mkdir(exist_ok=True)
    # (workspace / "network_reports").mkdir(exist_ok=True)
    # (workspace / "compliance_reports").mkdir(exist_ok=True)
    # (workspace / "logs").mkdir(exist_ok=True)
    # (workspace / "baselines").mkdir(exist_ok=True)
    # (workspace / "alerts").mkdir(exist_ok=True)
    # (workspace / "quarantine").mkdir(exist_ok=True)
    # (workspace / "forensic").mkdir(exist_ok=True)
    # (workspace / "auto_quarantine").mkdir(exist_ok=True)
    # (workspace / "scans").mkdir(exist_ok=True)
    
    return workspace

WORKSPACE = get_workspace_dir()

# -------------------------------
# COLORS (Define before use)
# -------------------------------

MATRIX_COLORS = ['\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[91m']
RESET = '\033[0m'
BOLD = '\033[1m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'

# -------------------------------
# GLOBAL VARIABLES FOR MODULE EXPORT
# -------------------------------

# These will be set when the module is imported
current_target = None
current_dashboard = None

# -------------------------------
# TARGET VALIDATION (only when run as script)
# -------------------------------

def get_target_from_args():
    """Get target from command line arguments"""
    if len(sys.argv) < 2:
        return None
    return sys.argv[1]

# -------------------------------
# SCAN DIRECTORY STRUCTURE
# -------------------------------

def init_scan_directories(target):
    """Initialize scan directories for a specific target"""
    SCAN_ROOT = WORKSPACE / "scans"
    SCAN_ROOT.mkdir(exist_ok=True)
    
    # Create target-specific directory with sanitized name (remove special chars)
    safe_target = "".join(c for c in target if c.isalnum() or c in '.-_')
    TARGET_DIR = SCAN_ROOT / safe_target
    TARGET_DIR.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Create session directory for this scan run
    SESSION_DIR = TARGET_DIR / f"scan_{timestamp}"
    SESSION_DIR.mkdir(exist_ok=True)
    
    return SESSION_DIR, timestamp

# -------------------------------
# ASCII ART & STYLING
# -------------------------------

ASCII_LOGO = """
    ╔══════════════════════════════════════════════════════════╗
    ║     ██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗ ║
    ║     ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║ ║
    ║     ██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║ ║
    ║     ██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║ ║
    ║     ██████╔╝███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║ ║
    ║     ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ║
    ╚══════════════════════════════════════════════════════════╝
"""

# Circle rotation frames
CIRCLE_FRAMES = [
    "◐", "◓", "◑", "◒",  # Basic rotation
    "⦾", "⦿", "⬤", "○",  # Solid/empty
    "⟳", "⟲", "↻", "↺",  # Rotation arrows
    "◜", "◝", "◞", "◟",  # Quarter circles
]

# Progress bar styles
PROGRESS_BARS = [
    "▱▱▱▱▱▱▱▱▱▱",
    "▰▱▱▱▱▱▱▱▱▱",
    "▰▰▱▱▱▱▱▱▱▱",
    "▰▰▰▱▱▱▱▱▱▱",
    "▰▰▰▰▱▱▱▱▱▱",
    "▰▰▰▰▰▱▱▱▱▱",
    "▰▰▰▰▰▰▱▱▱▱",
    "▰▰▰▰▰▰▰▱▱▱",
    "▰▰▰▰▰▰▰▰▱▱",
    "▰▰▰▰▰▰▰▰▰▱",
    "▰▰▰▰▰▰▰▰▰▰",
]

# -------------------------------
# TERMINAL UTILITIES
# -------------------------------

width = shutil.get_terminal_size((120, 20)).columns

def center_text(text):
    """Center text with color support"""
    # Remove color codes for length calculation
    clean_text = text
    for code in [RESET, BOLD, CYAN, YELLOW, GREEN, RED, BLUE, MAGENTA] + MATRIX_COLORS:
        clean_text = clean_text.replace(code, '')
    
    padding = max(0, (width - len(clean_text)) // 2)
    print(" " * padding + text)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def matrix_rain_effect(lines=3):
    """Create a Matrix-style digital rain effect"""
    chars = "01アイウエオカキクケコサシスセソタチツテト"
    for _ in range(lines):
        line = ""
        for _ in range(width // 4):
            color = random.choice(MATRIX_COLORS)
            line += color + random.choice(chars) + RESET
        print(line)
        time.sleep(0.03)

def save_output_to_file(session_dir, timestamp, scan_name, output_lines):
    """Save scan output to workspace file"""
    output_file = session_dir / f"{scan_name}_{timestamp}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"DSTerminal Recon Scan - {scan_name.upper()}\n")
        f.write(f"Target: {current_target if current_target else 'Unknown'}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("="*60 + "\n\n")
        for line in output_lines:
            f.write(line + "\n")
    return output_file

def check_command_exists(command):
    """Check if a command exists on the system (cross-platform)"""
    try:
        if os.name == "nt":  # Windows
            subprocess.run(["where", command], capture_output=True, check=True)
        else:  # Unix/Linux/Mac
            subprocess.run(["which", command], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# -------------------------------
# REAL-TIME SOC DASHBOARD
# -------------------------------

class SOCDashboard:
    def __init__(self):
        self.scan_metrics = {
            'ports': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'dns': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'whois': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'metasploit': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []}
        }
        self.active_scans = []
        self.circle_index = 0
        self.bar_index = 0
        self.lock = threading.Lock()
        
    def update_metric(self, scan_name, progress=None, status=None, findings=None, output_line=None):
        """Update a specific metric"""
        with self.lock:
            if scan_name in self.scan_metrics:
                if progress is not None:
                    self.scan_metrics[scan_name]['progress'] = progress
                if status is not None:
                    self.scan_metrics[scan_name]['status'] = status
                if findings is not None:
                    self.scan_metrics[scan_name]['findings'] = findings
                if output_line is not None:
                    self.scan_metrics[scan_name]['output'].append(output_line)
    
    def get_status_color(self, status):
        """Get color based on status"""
        if status == 'COMPLETE':
            return GREEN
        elif status == 'RUNNING':
            return CYAN
        elif status == 'ERROR':
            return RED
        else:
            return YELLOW
    
    def render_three_column_circles(self):
        """Render three centered column circles with real-time progress"""
        with self.lock:
            # Get current frame and bar
            circle = CIRCLE_FRAMES[self.circle_index % len(CIRCLE_FRAMES)]
            bar = PROGRESS_BARS[self.bar_index % len(PROGRESS_BARS)]
            
            # Calculate column width (each column gets 1/3 of terminal width)
            col_width = width // 3
            
            # Column 1: Port Scan (LEFT)
            col1_status = self.get_status_color(self.scan_metrics['ports']['status'])
            col1_title = f"{col1_status}{circle}{RESET} PORTS"
            col1_prog = f"{CYAN}[{bar}]{RESET}"
            col1_find = f"{GREEN}⚡{self.scan_metrics['ports']['findings']}{RESET}"
            
            # Column 2: DNS (CENTER)
            col2_status = self.get_status_color(self.scan_metrics['dns']['status'])
            col2_title = f"{col2_status}{circle}{RESET} DNS"
            col2_prog = f"{CYAN}[{bar}]{RESET}"
            col2_find = f"{GREEN}⚡{self.scan_metrics['dns']['findings']}{RESET}"
            
            # Column 3: WHOIS (RIGHT)
            col3_status = self.get_status_color(self.scan_metrics['whois']['status'])
            col3_title = f"{col3_status}{circle}{RESET} WHOIS"
            col3_prog = f"{CYAN}[{bar}]{RESET}"
            col3_find = f"{GREEN}⚡{self.scan_metrics['whois']['findings']}{RESET}"
            
            # Pad each column to exactly col_width characters
            col1_title_padded = col1_title.ljust(col_width)
            col2_title_padded = col2_title.ljust(col_width)
            col3_title_padded = col3_title.ljust(col_width)
            
            col1_prog_padded = col1_prog.ljust(col_width)
            col2_prog_padded = col2_prog.ljust(col_width)
            col3_prog_padded = col3_prog.ljust(col_width)
            
            col1_find_padded = f"FINDINGS: {col1_find}".ljust(col_width)
            col2_find_padded = f"FINDINGS: {col2_find}".ljust(col_width)
            col3_find_padded = f"FINDINGS: {col3_find}".ljust(col_width)
            
            # Print the three columns side by side
            print()
            print(f"{col1_title_padded}{col2_title_padded}{col3_title_padded}")
            print(f"{col1_prog_padded}{col2_prog_padded}{col3_prog_padded}")
            print(f"{col1_find_padded}{col2_find_padded}{col3_find_padded}")
            
            # Update frame indices
            self.circle_index += 1
            self.bar_index = (self.bar_index + 1) % len(PROGRESS_BARS)
    
    def get_summary(self):
        """Get summary of all scan metrics"""
        return {
            name: {
                'status': metrics['status'],
                'findings': metrics['findings']
            }
            for name, metrics in self.scan_metrics.items()
        }

# -------------------------------
# CINEMATIC SPINNER WITH DASHBOARD
# -------------------------------

class CinematicSpinner:
    def __init__(self, dashboard, scan_name):
        self.dashboard = dashboard
        self.scan_name = scan_name
        self.stop_event = threading.Event()
        
    def animate_with_dashboard(self):
        """Enhanced spinner that updates the three-column dashboard"""
        start_time = time.time()
        last_dashboard_update = 0
        
        while not self.stop_event.is_set():
            elapsed = int(time.time() - start_time)
            
            # Update dashboard every 0.2 seconds
            if time.time() - last_dashboard_update > 0.2:
                # Calculate progress (simulated for demo)
                progress = min(100, int((elapsed / 10) * 100))
                
                # Update the specific scan metric
                self.dashboard.update_metric(
                    self.scan_name, 
                    progress=progress,
                    status='RUNNING'
                )
                
                # Clear and redraw dashboard
                self.redraw_dashboard()
                last_dashboard_update = time.time()
            
            time.sleep(0.1)
        
        # Mark as complete
        self.dashboard.update_metric(
            self.scan_name,
            progress=100,
            status='COMPLETE'
        )
        self.redraw_dashboard()
    
    def redraw_dashboard(self):
        """Redraw the entire dashboard"""
        # Move cursor up to redraw dashboard area (8 lines)
        print("\033[8A", end="")
        
        # Redraw SOC header
        center_text(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
        center_text(f"{BOLD}{CYAN}║                    🎯 SOC DASHBOARD 🎯                            ║{RESET}")
        center_text(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}")
        
        # Render three-column circles
        self.dashboard.render_three_column_circles()
        
        # Separator
        center_text(f"{BOLD}{CYAN}{'─' * 50}{RESET}")
        
        # Show current scan info
        print()

# -------------------------------
# SCAN ENGINE
# -------------------------------

def run_cinematic_scan(label, command, scan_name, dashboard, session_dir, timestamp, target):
    """Execute scan with cinematic effects and dashboard updates"""
    
    # Initialize scan in dashboard
    dashboard.update_metric(scan_name, progress=0, status='RUNNING', findings=0)
    
    spinner = CinematicSpinner(dashboard, scan_name)
    t = threading.Thread(target=spinner.animate_with_dashboard)
    t.daemon = True
    t.start()
    
    output_lines = []
    findings_count = 0
    
    try:
        # Use shell=True for compatibility with commands like 'nslookup'
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            line = line.rstrip()
            output_lines.append(line)
            
            # Update findings count based on output
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
        
    except KeyboardInterrupt:
        spinner.stop_event.set()
        t.join(timeout=1)
        dashboard.update_metric(scan_name, status='ERROR')
        return []
    
    except Exception as e:
        output_lines.append(f"Error: {str(e)}")
        dashboard.update_metric(scan_name, status='ERROR')
    
    finally:
        spinner.stop_event.set()
        t.join(timeout=1)
    
    # Save output to file
    if output_lines:
        output_file = save_output_to_file(session_dir, timestamp, scan_name, output_lines)
        
        # Display limited results
        print()
        center_text(f"{BOLD}{GREEN}═════ SCAN RESULTS: {scan_name.upper()} ═════{RESET}")
        for line in output_lines[:15]:  # Show first 15 lines
            if line.strip():
                # Truncate long lines and clean for display
                display_line = line[:80] if len(line) > 80 else line
                center_text(f"  {display_line}")
        if len(output_lines) > 15:
            center_text(f"  ... and {len(output_lines) - 15} more lines")
        center_text(f"{BOLD}{CYAN}Results saved to: {output_file}{RESET}")
        print()
    
    return output_lines

# -------------------------------
# MAIN RECON FUNCTION
# -------------------------------

def run_recon(target=None):
    """Main reconnaissance function - can be called from other modules"""
    global current_target, current_dashboard
    
    # Use provided target or get from args
    if target is None:
        target = get_target_from_args()
    
    if target is None:
        print(f"{RED}[!] No target specified. Usage: run_recon('<target>'){RESET}")
        return False
    
    current_target = target
    
    clear()
    
    # Matrix rain intro
    matrix_rain_effect(5)
    time.sleep(0.5)
    
    # Animated logo
    center_text(f"{BOLD}{CYAN}")
    for line in ASCII_LOGO.split('\n'):
        if line.strip():
            center_text(f"{CYAN}{line}{RESET}")
            time.sleep(0.05)
    
    time.sleep(0.5)
    
    # Initialize scan directories
    session_dir, timestamp = init_scan_directories(target)
    
    # Initialize dashboard
    dashboard = SOCDashboard()
    current_dashboard = dashboard
    
    # Initial dashboard render
    center_text(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
    center_text(f"{BOLD}{CYAN}║                    🎯 REAL-TIME SOC DASHBOARD 🎯                 ║{RESET}")
    center_text(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}")
    
    # Initial three-column circles
    dashboard.render_three_column_circles()
    center_text(f"{BOLD}{CYAN}{'─' * 50}{RESET}")
    
    # Target display
    target_text = f"🎯 TARGET ACQUIRED: {target.upper()} 🎯"
    center_text(f"{BOLD}{GREEN}{target_text}{RESET}")
    center_text(f"{BOLD}{CYAN}{'─' * 50}{RESET}")
    print()
    center_text(f"{BOLD}{YELLOW}📁 SCAN DIRECTORY: {session_dir}{RESET}")
    print()
    
    time.sleep(1)
    
    # -------------------------------
    # SCAN LIST
    # -------------------------------
    
    scans = [
        ("🔍 PORT SCAN", f"nmap -F {target}", "ports"),
        ("🌐 DNS RESOLUTION", f"nslookup {target}", "dns"),
        ("📋 WHOIS LOOKUP", f"whois {target}", "whois"),
    ]
    
    # -------------------------------
    # RUN SCANS
    # -------------------------------
    
    for label, cmd, scan_name in scans:
        print()
        center_text(f"{BOLD}{MAGENTA}{label}{RESET}")
        print()
        
        # Check if command exists before running
        cmd_name = cmd.split()[0]
        if check_command_exists(cmd_name) or cmd_name in ['nslookup', 'whois']:
            run_cinematic_scan(label, cmd, scan_name, dashboard, session_dir, timestamp, target)
        else:
            center_text(f"{BOLD}{YELLOW}⚠ {cmd_name} not found - skipping{RESET}")
            dashboard.update_metric(scan_name, status='ERROR', findings=0)
        
        # Brief pause between scans
        time.sleep(0.5)
        matrix_rain_effect(1)
    
    # -------------------------------
    # METASPLOIT SEARCH (optional - only if msfconsole is available)
    # -------------------------------
    
    # Check if metasploit is available using cross-platform function
    if check_command_exists("msfconsole"):
        run_cinematic_scan(
            "💀 METASPLOIT SEARCH",
            f'msfconsole -q -x "search {target}; exit"',
            "metasploit",
            dashboard,
            session_dir,
            timestamp,
            target
        )
    else:
        center_text(f"{BOLD}{YELLOW}⚠ Metasploit not found - skipping{RESET}")
        dashboard.update_metric('metasploit', status='ERROR', findings=0)
    
    # -------------------------------
    # CREATE SUMMARY REPORT
    # -------------------------------
    
    summary_file = session_dir / f"summary_{timestamp}.txt"
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
        
        summary = dashboard.get_summary()
        for scan_name, metrics in summary.items():
            f.write(f"{scan_name.upper()}:\n")
            f.write(f"  Status: {metrics['status']}\n")
            f.write(f"  Findings: {metrics['findings']}\n")
            output_file = session_dir / f"{scan_name}_{timestamp}.txt"
            if output_file.exists():
                f.write(f"  Output: {output_file}\n")
            f.write("\n")
    
    # -------------------------------
    # FINAL DASHBOARD
    # -------------------------------
    
    print("\n" * 2)
    center_text(f"{BOLD}{GREEN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
    center_text(f"{BOLD}{GREEN}║                    🏁 INFORMATION GATHERING COMPLETE 🏁           ║{RESET}")
    center_text(f"{BOLD}{GREEN}╚══════════════════════════════════════════════════════════════════╝{RESET}")
    
    # Final three-column summary
    dashboard.render_three_column_circles()
    
    # Summary statistics
    summary = dashboard.get_summary()
    total_findings = sum(m['findings'] for m in summary.values())
    center_text(f"{BOLD}{CYAN}{'─' * 50}{RESET}")
    center_text(f"{BOLD}{YELLOW}TOTAL FINDINGS: {total_findings}{RESET}")
    center_text(f"{BOLD}{YELLOW}SCAN SESSION: {session_dir}{RESET}")
    center_text(f"{BOLD}{YELLOW}SUMMARY REPORT: {summary_file}{RESET}")
    center_text(f"{BOLD}{GREEN}{'═' * 50}{RESET}")
    
    # Matrix rain outro
    matrix_rain_effect(2)
    print()
    center_text(f"{BOLD}{CYAN}⚡ DSTERMINAL SOC - RECONNAISSANCE COMPLETE ⚡{RESET}")
    print()
    
    return True

# -------------------------------
# RECON MENU FUNCTION
# -------------------------------

def recon_menu():
    """Interactive menu for reconnaissance"""
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║           RECONNAISSANCE MENU                ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════╝{RESET}")
    print()
    print(f"{GREEN}1. Quick Scan (Ports, DNS, WHOIS){RESET}")
    print(f"{GREEN}2. Full Scan (with Metasploit){RESET}")
    print(f"{GREEN}3. Custom Target{RESET}")
    print(f"{RED}0. Exit{RESET}")
    print()
    
    choice = input(f"{YELLOW}Select option: {RESET}").strip()
    
    if choice == "1":
        target = input(f"{CYAN}Enter target (IP or domain): {RESET}").strip()
        if target:
            run_recon(target)
        else:
            print(f"{RED}[!] No target specified{RESET}")
        
    elif choice == "2":
        target = input(f"{CYAN}Enter target (IP or domain): {RESET}").strip()
        if target:
            run_recon(target)
        else:
            print(f"{RED}[!] No target specified{RESET}")
    
    elif choice == "3":
        target = input(f"{CYAN}Enter target (IP or domain): {RESET}").strip()
        if target:
            run_recon(target)
        else:
            print(f"{RED}[!] No target specified{RESET}")
    
    elif choice == "0":
        print(f"{YELLOW}[*] Exiting recon menu{RESET}")
        return
    
    else:
        print(f"{RED}[!] Invalid option{RESET}")

# -------------------------------
# MAIN EXECUTION (when run as script)
# -------------------------------

if __name__ == "__main__":
    target = get_target_from_args()
    
    if target:
        # Run recon directly with target from command line
        run_recon(target)
    else:
        # Show menu if no target provided
        recon_menu()