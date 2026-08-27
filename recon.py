#!python
import sys
"""

# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass

_original_stdout_write = sys.stdout.write

def _safe_stdout_write(text):
    try:
        _original_stdout_write(text)
    except OSError as e:
        if e.errno == 22:
            try:
                clean = text.encode("ascii", "ignore").decode("ascii")
                _original_stdout_write(clean)
            except:
                pass
        else:
            raise
    except UnicodeEncodeError:
        try:
            clean = text.encode("ascii", "ignore").decode("ascii")
            _original_stdout_write(clean)
        except:
            pass

sys.stdout.write = _safe_stdout_write


# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass


    try:
    except OSError as e:
        if e.errno == 22:
            try:
                clean = text.encode("ascii", "ignore").decode("ascii")
                _original_stdout_write(clean)
            except:
                pass
        else:
            raise
    except UnicodeEncodeError:
        try:
            clean = text.encode("ascii", "ignore").decode("ascii")
            _original_stdout_write(clean)
        except:
            pass

sys.stdout.write = _safe_stdout_write

DSTerminal Reconnaissance Module
Usage: python recon.py <target>
       Or import as module: from recon import run_recon, recon_menu
"""
import sys
import os
import threading
import itertools
import time
import shutil
import subprocess
import random
import math
import re
from datetime import datetime
from pathlib import Path

# ============================================================
# FIX WINDOWS CONSOLE ENCODING - MUST BE FIRST
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass
    
    # Fix stdout encoding
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
    # Force color support
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
except ImportError:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
    Back = type('Back', (), {'RESET': '\033[49m'})
except Exception as e:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
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
MATRIX_COLORS = [Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.MAGENTA, Colors.CYAN, Colors.RED]

# ============================================================
# WORKSPACE DIRECTORY SETUP
# ============================================================

def get_workspace_dir() -> Path:
    """Get the DSTerminal workspace directory"""
    home = Path.home()
    workspace = home / "dsterminal_workspace"
    workspace.mkdir(exist_ok=True)
    return workspace

WORKSPACE = get_workspace_dir()

# -------------------------------
# GLOBAL VARIABLES FOR MODULE EXPORT
# -------------------------------

current_target = None
current_dashboard = None

# -------------------------------
# TARGET VALIDATION
# -------------------------------

def get_target_from_args():
    """Get target from command line arguments"""
    if len(sys.argv) < 2:
        return None
    return sys.argv[1]

# ============================================================
# TERMINAL UTILITIES - CENTERED LAYOUT
# ============================================================

def get_terminal_width() -> int:
    """Get terminal width for centering"""
    try:
        width = shutil.get_terminal_size().columns
        return min(max(width, 80), 120)
    except:
        return 80

def center_text(text: str, width: int = None) -> str:
    """Center text within terminal width"""
    if width is None:
        width = get_terminal_width()
    # Strip ANSI codes for length calculation
    clean_text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
    padding = max(0, (width - len(clean_text)) // 2)
    return ' ' * padding + text

def center_print(text: str, color: str = "", width: int = None):
    """Print centered colored text"""
    if width is None:
        width = get_terminal_width()
    if color:
        print(center_text(f"{color}{text}{RESET}", width))
    else:
        print(center_text(text, width))

def print_colored(text: str, color: str = ""):
    """Print colored text without centering"""
    if color:
        print(f"{color}{text}{RESET}")
    else:
        print(text)

# ============================================================
# SCAN DIRECTORY STRUCTURE
# ============================================================

def init_scan_directories(target):
    """Initialize scan directories for a specific target"""
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
    """Create a Matrix-style digital rain effect"""
    chars = "01"
    width = get_terminal_width()
    for _ in range(lines):
        line = ""
        for _ in range(min(width // 4, 30)):
            color = random.choice(MATRIX_COLORS)
            line += color + random.choice(chars) + RESET
        print(center_text(line))
        time.sleep(0.03)

def draw_glowing_box(title, content_lines, title_color=CYAN, border_color=CYAN, 
                     content_color=GREEN, blink_title=False, glow_border=True):
    """Draw a glowing neon hacker-styled centered box with ASCII characters"""
    width = get_terminal_width()
    box_width = min(width - 4, 70)
    left_margin = max(0, (width - box_width) // 2)
    inner = box_width - 4
    
    import textwrap
    wrapped = []
    for line in content_lines:
        if not line.strip():
            wrapped.append("")
            continue
        line = line.rstrip()
        wrapped.extend(textwrap.wrap(line, inner, break_long_words=False, replace_whitespace=False))
    
    glow_prefix = BOLD if glow_border else ""
    title_prefix = BOLD
    if blink_title:
        title_prefix += BLINK
    
    top = glow_prefix + border_color + "+" + "-" * (box_width - 2) + RESET
    mid = glow_prefix + border_color + "+" + "-" * (box_width - 2) + RESET
    bot = glow_prefix + border_color + "+" + "-" * (box_width - 2) + RESET
    
    title_text = f" {title} ".center(box_width - 2)
    title_line = title_prefix + title_color + "|" + title_text + "|" + RESET
    if blink_title:
        title_line += RESET
    
    lines = [top, title_line, mid]
    
    for line in wrapped:
        padded_line = line.ljust(inner)
        lines.append(glow_prefix + border_color + "| " + RESET + content_color + padded_line + RESET + glow_prefix + border_color + " |" + RESET)
    
    lines.append(bot)
    
    return [(" " * left_margin) + line for line in lines]

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
    """Check if a command exists on the system"""
    try:
        if os.name == "nt":
            result = subprocess.run(["where", command], capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(["which", command], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

# ============================================================
# CINEMATIC SOC DASHBOARD
# ============================================================

class SOCDashboard:
    def __init__(self):
        self.scan_metrics = {
            'ports': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'dns': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'whois': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []},
            'metasploit': {'progress': 0, 'status': 'IDLE', 'findings': 0, 'output': []}
        }
        self.active_scans = []
        self.lock = threading.Lock()
        self.spinner_frames = ["[+]", "[*]", "[-]", "[.]"]
        self.progress_chars = ["#", "=", "*", "+"]
        self.term_width = get_terminal_width()
        
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
    
    def get_status_icon(self, status):
        """Get icon based on status"""
        if status == 'COMPLETE':
            return "[+]"
        elif status == 'RUNNING':
            return "[*]"
        elif status == 'ERROR':
            return "[!]"
        else:
            return "[.]"
    
    def render_progress_bar(self, progress, width=20):
        """Render ASCII progress bar"""
        filled = int(progress / 100 * width)
        bar = "[" + "#" * filled + "." * (width - filled) + "]"
        return bar
    
    def render_three_column_panels(self):
        """Render three centered column panels with real-time progress"""
        with self.lock:
            width = get_terminal_width()
            col_width = width // 3
            
            # Column 1: Port Scan
            status1 = self.get_status_color(self.scan_metrics['ports']['status'])
            icon1 = self.get_status_icon(self.scan_metrics['ports']['status'])
            bar1 = self.render_progress_bar(self.scan_metrics['ports']['progress'])
            col1 = [
                f"{status1}{icon1}{RESET} PORT SCAN",
                f"{CYAN}{bar1}{RESET} {self.scan_metrics['ports']['progress']}%",
                f"{GREEN}Findings: {self.scan_metrics['ports']['findings']}{RESET}",
                f"{status1}{self.scan_metrics['ports']['status']}{RESET}"
            ]
            
            # Column 2: DNS
            status2 = self.get_status_color(self.scan_metrics['dns']['status'])
            icon2 = self.get_status_icon(self.scan_metrics['dns']['status'])
            bar2 = self.render_progress_bar(self.scan_metrics['dns']['progress'])
            col2 = [
                f"{status2}{icon2}{RESET} DNS RESOLUTION",
                f"{CYAN}{bar2}{RESET} {self.scan_metrics['dns']['progress']}%",
                f"{GREEN}Findings: {self.scan_metrics['dns']['findings']}{RESET}",
                f"{status2}{self.scan_metrics['dns']['status']}{RESET}"
            ]
            
            # Column 3: WHOIS
            status3 = self.get_status_color(self.scan_metrics['whois']['status'])
            icon3 = self.get_status_icon(self.scan_metrics['whois']['status'])
            bar3 = self.render_progress_bar(self.scan_metrics['whois']['progress'])
            col3 = [
                f"{status3}{icon3}{RESET} WHOIS LOOKUP",
                f"{CYAN}{bar3}{RESET} {self.scan_metrics['whois']['progress']}%",
                f"{GREEN}Findings: {self.scan_metrics['whois']['findings']}{RESET}",
                f"{status3}{self.scan_metrics['whois']['status']}{RESET}"
            ]
            
            # Pad each column
            rows = max(len(col1), len(col2), len(col3))
            
            for i in range(rows):
                line1 = col1[i] if i < len(col1) else ""
                line2 = col2[i] if i < len(col2) else ""
                line3 = col3[i] if i < len(col3) else ""
                
                # Pad each line to column width
                clean1 = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line1)
                clean2 = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line2)
                clean3 = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line3)
                
                padded1 = line1 + " " * (col_width - len(clean1)) if len(clean1) < col_width else line1[:col_width]
                padded2 = line2 + " " * (col_width - len(clean2)) if len(clean2) < col_width else line2[:col_width]
                padded3 = line3 + " " * (col_width - len(clean3)) if len(clean3) < col_width else line3[:col_width]
                
                print(padded1 + padded2 + padded3)
    
    def get_summary(self):
        """Get summary of all scan metrics"""
        return {
            name: {
                'status': metrics['status'],
                'findings': metrics['findings']
            }
            for name, metrics in self.scan_metrics.items()
        }

# ============================================================
# CINEMATIC SPINNER WITH DASHBOARD
# ============================================================

class CinematicSpinner:
    def __init__(self, dashboard, scan_name):
        self.dashboard = dashboard
        self.scan_name = scan_name
        self.stop_event = threading.Event()
        self.spinner_frames = ["[+]", "[*]", "[-]", "[.]"]
        
    def animate_with_dashboard(self):
        """Enhanced spinner that updates the three-column dashboard"""
        start_time = time.time()
        last_dashboard_update = 0
        frame_idx = 0
        
        while not self.stop_event.is_set():
            elapsed = int(time.time() - start_time)
            frame = self.spinner_frames[frame_idx % len(self.spinner_frames)]
            frame_idx += 1
            
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
                
                # Redraw dashboard
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
        # Move cursor up to redraw dashboard area
        print("\033[8A", end="")
        
        # Redraw SOC header
        center_print(f"{BOLD}{CYAN}+{'-' * 60}+{RESET}")
        center_print(f"{BOLD}{CYAN}|                    [*] SOC DASHBOARD [*]                            |{RESET}")
        center_print(f"{BOLD}{CYAN}+{'-' * 60}+{RESET}")
        
        # Render three-column panels
        self.dashboard.render_three_column_panels()
        
        # Separator
        center_print(f"{BOLD}{CYAN}{'-' * 60}{RESET}")

# ============================================================
# SCAN ENGINE
# ============================================================

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
        
        # Display limited results in a colorful box
        result_box = draw_glowing_box(
            f"SCAN RESULTS: {scan_name.upper()}",
            output_lines[:10],
            title_color=MAGENTA,
            border_color=CYAN,
            content_color=GREEN,
            blink_title=True
        )
        for line in result_box:
            print(line)
        if len(output_lines) > 10:
            center_print(f"{DIM}... and {len(output_lines) - 10} more lines{RESET}")
        center_print(f"{CYAN}[+] Results saved to: {output_file}{RESET}")
        print()
    
    return output_lines

# ============================================================
# MAIN RECON FUNCTION
# ============================================================

def run_recon(target=None):
    """Main reconnaissance function - can be called from other modules"""
    global current_target, current_dashboard
    
    if target is None:
        target = get_target_from_args()
    
    if target is None:
        print_colored("[!] No target specified. Usage: run_recon('<target>')", RED)
        return False
    
    current_target = target
    
    clear_screen()
    
    # Matrix rain intro
    matrix_rain_effect(3)
    time.sleep(0.5)
    
    # Animated banner
    banner_lines = [
        f"{BOLD}{CYAN}+{'-' * 60}+{RESET}",
        f"{BOLD}{CYAN}|        [*] DSTERMINAL RECONNAISSANCE ENGINE [*]           |{RESET}",
        f"{BOLD}{CYAN}+{'-' * 60}+{RESET}",
        f"{BOLD}{YELLOW}|        [*] TARGET: {target.upper():<30}           |{RESET}",
        f"{BOLD}{CYAN}+{'-' * 60}+{RESET}"
    ]
    for line in banner_lines:
        center_print(line)
        time.sleep(0.1)
    
    time.sleep(0.5)
    
    # Initialize scan directories
    session_dir, timestamp = init_scan_directories(target)
    
    # Initialize dashboard
    dashboard = SOCDashboard()
    current_dashboard = dashboard
    
    # Initial dashboard render
    center_print(f"{BOLD}{CYAN}+{'-' * 60}+{RESET}")
    center_print(f"{BOLD}{CYAN}|                    [*] SOC DASHBOARD [*]                            |{RESET}")
    center_print(f"{BOLD}{CYAN}+{'-' * 60}+{RESET}")
    
    # Initial three-column panels
    dashboard.render_three_column_panels()
    center_print(f"{BOLD}{CYAN}{'-' * 60}{RESET}")
    
    # Target and directory info
    center_print(f"{BOLD}{GREEN}[+] TARGET ACQUIRED: {target.upper()}{RESET}")
    center_print(f"{BOLD}{YELLOW}[+] SCAN DIRECTORY: {session_dir}{RESET}")
    center_print(f"{BOLD}{CYAN}{'-' * 60}{RESET}")
    print()
    
    time.sleep(1)
    
    # -------------------------------
    # SCAN LIST
    # -------------------------------
    
    scans = [
        ("[+] PORT SCAN", f"nmap -F {target}", "ports"),
        ("[+] DNS RESOLUTION", f"nslookup {target}", "dns"),
        ("[+] WHOIS LOOKUP", f"whois {target}", "whois"),
    ]
    
    # -------------------------------
    # RUN SCANS
    # -------------------------------
    
    for label, cmd, scan_name in scans:
        print()
        center_print(f"{BOLD}{MAGENTA}{label}{RESET}")
        print()
        
        cmd_name = cmd.split()[0]
        if check_command_exists(cmd_name) or cmd_name in ['nslookup', 'whois']:
            run_cinematic_scan(label, cmd, scan_name, dashboard, session_dir, timestamp, target)
        else:
            center_print(f"{BOLD}{YELLOW}[!] {cmd_name} not found - skipping{RESET}")
            dashboard.update_metric(scan_name, status='ERROR', findings=0)
        
        time.sleep(0.5)
        matrix_rain_effect(1)
    
    # -------------------------------
    # METASPLOIT SEARCH
    # -------------------------------
    
    if check_command_exists("msfconsole"):
        run_cinematic_scan(
            "[+] METASPLOIT SEARCH",
            f'msfconsole -q -x "search {target}; exit"',
            "metasploit",
            dashboard,
            session_dir,
            timestamp,
            target
        )
    else:
        center_print(f"{BOLD}{YELLOW}[!] Metasploit not found - skipping{RESET}")
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
    
    # Final completion box
    final_box = draw_glowing_box(
        "[+] INFORMATION GATHERING COMPLETE [+]",
        [
            f"Total Findings: {sum(m['findings'] for m in dashboard.get_summary().values())}",
            f"Scan Session: {session_dir}",
            f"Summary Report: {summary_file}"
        ],
        title_color=GREEN,
        border_color=GREEN,
        content_color=CYAN,
        blink_title=True
    )
    for line in final_box:
        print(line)
    
    print()
    
    # Final three-column summary
    dashboard.render_three_column_panels()
    
    # Separator
    center_print(f"{BOLD}{CYAN}{'-' * 60}{RESET}")
    
    # Matrix rain outro
    matrix_rain_effect(2)
    print()
    center_print(f"{BOLD}{CYAN}[+] DSTERMINAL SOC - RECONNAISSANCE COMPLETE [+]{RESET}")
    print()
    
    return True

# ============================================================
# RECON MENU FUNCTION
# ============================================================

def recon_menu():
    """Interactive menu for reconnaissance"""
    print(f"{BOLD}{CYAN}+{'-' * 50}+{RESET}")
    print(f"{BOLD}{CYAN}|           RECONNAISSANCE MENU                |{RESET}")
    print(f"{BOLD}{CYAN}+{'-' * 50}+{RESET}")
    print()
    print(f"{GREEN}[1] Quick Scan (Ports, DNS, WHOIS){RESET}")
    print(f"{GREEN}[2] Full Scan (with Metasploit){RESET}")
    print(f"{GREEN}[3] Custom Target{RESET}")
    print(f"{RED}[0] Exit{RESET}")
    print()
    
    choice = input(f"{YELLOW}Select option: {RESET}").strip()
    
    if choice == "1" or choice == "2" or choice == "3":
        target = input(f"{CYAN}Enter target (IP or domain): {RESET}").strip()
        if target:
            run_recon(target)
        else:
            print_colored("[!] No target specified", RED)
    
    elif choice == "0":
        print_colored("[*] Exiting recon menu", YELLOW)
        return
    
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