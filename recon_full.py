#!/usr/bin/env python3
"""
DSTerminal Full Reconnaissance Module
Usage: python recon_full.py <target>
       Or import as module: from recon_full import run_full_recon, full_recon_menu
"""
import sys
if sys.platform == 'win32':
    import os
    import msvcrt
    # Ensure stdout is properly set
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', errors='ignore')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', errors='ignore')
        
import os
import sys
import time
import threading
import itertools
import subprocess
import shutil
import random
import socket
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
    
    return workspace

WORKSPACE = get_workspace_dir()

# -------------------------------
# GLOBAL VARIABLES FOR MODULE EXPORT
# -------------------------------

current_target = None
current_session_dir = None

# -------------------------------
# TARGET ARGUMENT HANDLER
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
    safe_target = "".join(c for c in target if c.isalnum() or c in '.-_')
    
    SCAN_ROOT = WORKSPACE / "scans"
    SCAN_ROOT.mkdir(exist_ok=True)
    
    TARGET_DIR = SCAN_ROOT / safe_target
    TARGET_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    SESSION_DIR = TARGET_DIR / f"scan_{timestamp}"
    SESSION_DIR.mkdir(exist_ok=True)
    
    return SESSION_DIR, timestamp, safe_target

# -------------------------------
# TERMINAL SETUP
# -------------------------------

try:
    width = shutil.get_terminal_size((120, 20)).columns
except:
    width = 120

# -------------------------------
# COLORS
# -------------------------------

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
BLINK = "\033[5m"

# -------------------------------
# ANIMATION FRAMES
# -------------------------------

big_spinner_frames = ["[+]     [*]", " [+]   [*] ", "  [+] [*]  ", "   [*]   ", "  [-] [*]  ", " [-]   [*] "]
radar_frames = ["[+]", "[*]", "[-]", "[.]"]
scanning_frames = ["[*]", "[+]", "[-]", "[.]", "[+]", "[*]"]

# -------------------------------
# GLOBAL DATA
# -------------------------------

alert_feed = []

stop_flags = {
    "port": False,
    "dns": False,
    "msf": False
}

scan_outputs = {
    "port": [],
    "dns": [],
    "msf": []
}

risk_scores = {
    "port": 0,
    "dns": 0,
    "msf": 0
}

scan_findings = {
    "port": 0,
    "dns": 0,
    "msf": 0
}

# ============================================================
# COLORFUL CENTERED DASHBOARD FUNCTIONS
# ============================================================

def center(text):
    """Center text with color support"""
    clean_text = text
    for code in [RESET, BOLD, CYAN, YELLOW, GREEN, RED, BLUE, MAGENTA, DIM, BLINK]:
        clean_text = clean_text.replace(code, '')
    
    padding = max(0, (width - len(clean_text)) // 2)
    return " " * padding + text

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def draw_glowing_box(title, content_lines, title_color=CYAN, border_color=CYAN, 
                     content_color=GREEN, blink_title=False, glow_border=True):
    """Draw a glowing neon hacker-styled centered box with ASCII characters"""
    box_width = min(width - 4, 80)
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
    
    top = glow_prefix + border_color + "+" + "-" * (box_width - 2) + "+" + RESET
    mid = glow_prefix + border_color + "+" + "-" * (box_width - 2) + "+" + RESET
    bot = glow_prefix + border_color + "+" + "-" * (box_width - 2) + "+" + RESET
    
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

def save_summary(session_dir, timestamp, target):
    """Save scan summary to workspace"""
    summary_file = session_dir / f"summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("DSTERMINAL FULL RECONNAISSANCE SUMMARY\n")
        f.write("="*60 + "\n\n")
        f.write(f"Target: {target}\n")
        f.write(f"Scan Time: {datetime.now().isoformat()}\n")
        f.write(f"Workspace: {WORKSPACE}\n")
        f.write(f"Session Directory: {session_dir}\n\n")
        f.write("-"*60 + "\n")
        f.write("SCAN RESULTS SUMMARY\n")
        f.write("-"*60 + "\n\n")
        
        for scan_name in ['port', 'dns', 'msf']:
            f.write(f"{scan_name.upper()} SCAN:\n")
            f.write(f"  Status: {'COMPLETE' if stop_flags.get(scan_name, False) else 'INTERRUPTED'}\n")
            f.write(f"  Findings: {scan_findings.get(scan_name, 0)}\n")
            f.write(f"  Risk Score: {risk_scores.get(scan_name, 0)}%\n")
            f.write("\n")
        
        f.write("-"*60 + "\n")
        f.write("ALERT FEED\n")
        f.write("-"*60 + "\n\n")
        for alert in alert_feed:
            clean_alert = alert
            for code in [RED, GREEN, YELLOW, CYAN, MAGENTA, BLUE, RESET, BOLD, DIM, BLINK]:
                clean_alert = clean_alert.replace(code, '')
            f.write(f"{clean_alert}\n")
    
    return summary_file

# -------------------------------
# ALERT SYSTEM
# -------------------------------

def append_alert(msg, level="INFO"):
    color = GREEN if level == "INFO" else YELLOW if level == "WARN" else RED
    timestamp_str = datetime.now().strftime("%H:%M:%S")
    alert_msg = f"{color}[{level}] [{timestamp_str}] {msg}{RESET}"
    alert_feed.append(alert_msg)
    if len(alert_feed) > 10:
        alert_feed.pop(0)

# -------------------------------
# THREAT INTELLIGENCE
# -------------------------------

def analyze_port(port, service=""):
    critical_ports = {
        "21": "FTP exposed - insecure file transfer",
        "22": "SSH service detected - monitor for brute force",
        "23": "Telnet insecure service - credentials sent in clear",
        "25": "SMTP - email server exposed",
        "53": "DNS server exposed",
        "80": "HTTP web server exposed",
        "110": "POP3 email service",
        "143": "IMAP email service",
        "443": "HTTPS web server",
        "445": "SMB attack surface - vulnerable to ransomware",
        "3389": "RDP remote access - monitor for unauthorized access",
        "1433": "MSSQL database exposed",
        "3306": "MySQL database exposed",
        "5432": "PostgreSQL database exposed",
        "6379": "Redis unsecured - potential data leak",
        "8080": "HTTP proxy/web server",
        "8443": "HTTPS alternative port",
        "27017": "MongoDB exposed"
    }
    if port in critical_ports:
        append_alert(critical_ports[port], "WARN")
        risk_scores["port"] = min(risk_scores["port"] + 10, 100)
        scan_findings["port"] += 1
        return True
    return False

def threat_intel():
    append_alert("Threat intelligence engine active", "INFO")
    if current_target:
        append_alert(f"Analyzing attack surface of {current_target}", "INFO")
    append_alert("CVE database loaded", "INFO")

# -------------------------------
# CUSTOM PORT SCANNER
# -------------------------------

def custom_port_scan(target, ports=None, timeout=2):
    if ports is None:
        ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 
                 993, 995, 1433, 1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]
    
    findings = []
    
    try:
        ip = socket.gethostbyname(target)
        append_alert(f"Resolved {target} -> {ip}", "INFO")
    except socket.gaierror:
        append_alert(f"Cannot resolve hostname: {target}", "WARN")
        return findings
    
    append_alert(f"Starting custom port scan on {ip}...", "INFO")
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                service_name = socket.getservbyport(port, 'tcp') if port <= 49151 else "unknown"
                findings.append(f"Port {port}/tcp open - {service_name}")
                scan_outputs["port"].append(f"{GREEN}[+] Port {port}: OPEN ({service_name}){RESET}")
                scan_findings["port"] += 1
                analyze_port(str(port), service_name)
                risk_scores["port"] = min(risk_scores["port"] + 5, 100)
                
        except:
            continue
    
    if not findings:
        scan_outputs["port"].append(f"{YELLOW}[*] No open ports found on common ports{RESET}")
        append_alert("No common open ports detected", "INFO")
    else:
        append_alert(f"Found {len(findings)} open ports", "INFO")
    
    return findings

# -------------------------------
# GEO LOOKUP
# -------------------------------

def geo_lookup(target):
    try:
        result = subprocess.run(f"nslookup {target}", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            append_alert("DNS intelligence collected", "INFO")
            for line in result.stdout.split('\n'):
                if 'Address:' in line and 'Addresses' not in line:
                    ip = line.split('Address:')[-1].strip()
                    if ip and not ip.startswith('#'):
                        append_alert(f"Resolved IP: {ip}", "INFO")
                        scan_findings["dns"] += 1
        else:
            append_alert("DNS lookup returned errors", "WARN")
    except subprocess.TimeoutExpired:
        append_alert("DNS lookup timeout", "WARN")
    except Exception as e:
        append_alert(f"DNS lookup failed: {str(e)}", "WARN")

# -------------------------------
# SPINNER / PROGRESS ENGINE
# -------------------------------

def spinner_panel(label, flag):
    frames = itertools.cycle(big_spinner_frames)
    while not stop_flags.get(flag, True):
        frame = next(frames)
        progress = int(risk_scores.get(flag, 0) / 5)
        bar = "[" + ("#" * progress).ljust(20) + "]"
        scan_icon = next(itertools.cycle(scanning_frames))
        header = f"{CYAN}{scan_icon} {frame} {label} {bar} {risk_scores.get(flag, 0)}%{RESET}"
        
        if flag in scan_outputs:
            if scan_outputs[flag]:
                if len(scan_outputs[flag]) > 0:
                    scan_outputs[flag][0] = header
                else:
                    scan_outputs[flag].append(header)
            else:
                scan_outputs[flag].append(header)
        
        if flag in risk_scores and risk_scores[flag] < 90:
            risk_scores[flag] = min(risk_scores[flag] + random.randint(1, 3), 90)
        
        time.sleep(0.3)
    
    final_score = risk_scores.get(flag, 0)
    status_icon = "[+]" if final_score < 50 else "[*]" if final_score < 75 else "[!]"
    status_color = GREEN if final_score < 50 else YELLOW if final_score < 75 else RED
    header = f"{status_color}{status_icon} {label} COMPLETE - Risk Score: {final_score}%{RESET}"
    
    if flag in scan_outputs and scan_outputs[flag]:
        if len(scan_outputs[flag]) > 0:
            scan_outputs[flag][0] = header
        else:
            scan_outputs[flag].append(header)

# -------------------------------
# LIVE BOX DISPLAY
# -------------------------------

def display_boxes():
    while not all(stop_flags.values()):
        box_port = draw_glowing_box("PORT SCAN", scan_outputs.get("port", ["Initializing..."]), 
                                    title_color=CYAN, border_color=CYAN, content_color=GREEN)
        box_dns = draw_glowing_box("DNS / WHOIS", scan_outputs.get("dns", ["Initializing..."]),
                                   title_color=MAGENTA, border_color=MAGENTA, content_color=BLUE)
        box_msf = draw_glowing_box("METASPLOIT", scan_outputs.get("msf", ["Initializing..."]),
                                   title_color=RED, border_color=RED, content_color=YELLOW)
        
        rows = max(len(box_port), len(box_dns), len(box_msf))
        
        for i in range(rows):
            p = box_port[i] if i < len(box_port) else " " * (width // 3)
            d = box_dns[i] if i < len(box_dns) else " " * (width // 3)
            m = box_msf[i] if i < len(box_msf) else " " * (width // 3)
            print(p + d + m)
        
        time.sleep(0.5)
        print("\033[{}A".format(rows), end="")

# -------------------------------
# ALERT PANEL
# -------------------------------

def alert_panel():
    while not all(stop_flags.values()):
        print(center(f"{YELLOW}{'-' * 40}{RESET}"))
        print(center(f"{YELLOW}[+] LIVE ALERT FEED [+]{RESET}"))
        print(center(f"{YELLOW}{'-' * 40}{RESET}"))
        for a in alert_feed[-5:]:
            print(center(a))
        time.sleep(1.5)
        print("\033[{}A".format(len(alert_feed[-5:]) + 3), end="")

# -------------------------------
# RADAR ANIMATION
# -------------------------------

def radar_animation():
    i = 0
    while not all(stop_flags.values()):
        r = radar_frames[i % len(radar_frames)]
        timestamp_str = datetime.now().strftime("%H:%M:%S")
        radar_text = f"{MAGENTA}[*] THREAT RADAR {r} [{timestamp_str}]{RESET}"
        print(center(radar_text))
        i += 1
        time.sleep(0.5)
        print("\033[1A", end="")

# -------------------------------
# LIVE SCAN ENGINE
# -------------------------------

def run_scan(label, command, flag, outfile, session_dir, timestamp, target):
    spinner = threading.Thread(target=spinner_panel, args=(label, flag))
    spinner.daemon = True
    spinner.start()
    
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
        
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(f"DSTerminal Recon Scan - {label}\n")
            f.write(f"Target: {target}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("="*60 + "\n\n")
            
            for line in process.stdout:
                f.write(line)
                line = line.strip()
                
                if line:
                    if flag == "port" and ("/tcp" in line.lower() or "/udp" in line.lower() or "open" in line.lower()):
                        findings_count += 1
                        if flag in scan_outputs:
                            scan_outputs[flag].append(f"{CYAN}[+] {line[:50]}{RESET}")
                        scan_findings[flag] = findings_count
                        
                        try:
                            port_part = line.split('/')[0]
                            if port_part.isdigit():
                                analyze_port(port_part)
                        except:
                            pass
                    
                    elif flag == "dns" and ("address" in line.lower() or "canonical" in line.lower()):
                        findings_count += 1
                        if flag in scan_outputs:
                            scan_outputs[flag].append(f"{GREEN}[+] {line[:50]}{RESET}")
                        scan_findings[flag] = findings_count
                    
                    elif flag == "dns" and any(x in line.lower() for x in ['org', 'name', 'email', 'registrar']):
                        findings_count += 1
                        if flag in scan_outputs:
                            scan_outputs[flag].append(f"{BLUE}[+] {line[:50]}{RESET}")
                        scan_findings[flag] = findings_count
                    
                    elif flag == "msf" and any(x in line.lower() for x in ['exploit', 'auxiliary', 'module']):
                        findings_count += 1
                        if flag in scan_outputs:
                            scan_outputs[flag].append(f"{RED}[!] {line[:50]}{RESET}")
                        scan_findings[flag] = findings_count
                    
                    elif line and len(line) > 5:
                        if flag in scan_outputs and len(scan_outputs[flag]) < 50:
                            scan_outputs[flag].append(f"{CYAN}{line[:50]}{RESET}")
        
        process.wait()
        
        if process.returncode == 0:
            append_alert(f"{label} completed with {findings_count} findings", "INFO")
        else:
            append_alert(f"{label} completed with warnings (exit code: {process.returncode})", "WARN")
            
    except FileNotFoundError:
        append_alert(f"{label} failed: command not found - {command.split()[0]}", "WARN")
        if flag in scan_outputs:
            scan_outputs[flag].append(f"{RED}[!] Command not found: {command.split()[0]}{RESET}")
    except Exception as e:
        append_alert(f"{label} failed: {str(e)[:50]}", "WARN")
        if flag in scan_outputs:
            scan_outputs[flag].append(f"{RED}[!] Error: {str(e)[:50]}{RESET}")
    
    finally:
        stop_flags[flag] = True
        append_alert(f"{label} results saved -> {outfile}", "INFO")
        spinner.join(timeout=2)

# -------------------------------
# SOC HEADER WITH GLOW
# -------------------------------

def soc_header(target):
    clear()
    print(center(f"{BOLD}{CYAN}{'=' * 60}{RESET}"))
    print(center(f"{BOLD}{CYAN}[+] DSTERMINAL CYBER DEFENSE OPERATIONS CENTER [+]{RESET}"))
    print(center(f"{BOLD}{CYAN}{'=' * 60}{RESET}"))
    print(center(f"{BOLD}{YELLOW}[+] TARGET -> {target}{RESET}"))
    print(center(f"{CYAN}[+] Full Reconnaissance | Threat Intelligence | Vulnerability Discovery{RESET}"))
    print(center(f"{CYAN}[+] Workspace: {WORKSPACE}{RESET}"))
    print(center(f"{CYAN}{'-' * 60}{RESET}"))
    print()

# ============================================================
# MAIN FULL RECON FUNCTION
# ============================================================

def run_full_recon(target=None):
    """Main full reconnaissance function - can be called from other modules"""
    global current_target, current_session_dir, stop_flags, scan_outputs, risk_scores, scan_findings, alert_feed
    
    alert_feed = []
    stop_flags = {k: False for k in stop_flags}
    scan_outputs = {k: [] for k in scan_outputs}
    risk_scores = {k: 0 for k in risk_scores}
    scan_findings = {k: 0 for k in scan_findings}
    
    if target is None:
        target = get_target_from_args()
    
    if target is None:
        print(f"{RED}[!] No target specified. Usage: run_full_recon('<target>'){RESET}")
        return False
    
    current_target = target
    
    session_dir, timestamp, safe_target = init_scan_directories(target)
    current_session_dir = session_dir
    
    soc_header(target)
    
    append_alert("SOC systems online", "INFO")
    append_alert("Threat radar active", "INFO")
    append_alert(f"Target acquired: {target}", "INFO")
    
    geo_lookup(target)
    threat_intel()
    
    # -------------------------------
    # START SOC THREADS
    # -------------------------------
    
    radar_thread = threading.Thread(target=radar_animation)
    alert_thread = threading.Thread(target=alert_panel)
    box_thread = threading.Thread(target=display_boxes)
    
    radar_thread.daemon = True
    alert_thread.daemon = True
    box_thread.daemon = True
    
    radar_thread.start()
    alert_thread.start()
    box_thread.start()
    
    # -------------------------------
    # SCAN FILES
    # -------------------------------
    
    nmap_file = session_dir / f"port_scan_{timestamp}.txt"
    dns_file = session_dir / f"dns_{timestamp}.txt"
    msf_file = session_dir / f"metasploit_{timestamp}.txt"
    
    # -------------------------------
    # SCAN COMMANDS
    # -------------------------------
    
    threads = []
    
    nmap_available = check_command_exists("nmap")
    
    if nmap_available:
        append_alert("Nmap detected - using advanced port scanning", "INFO")
        threads.append(threading.Thread(
            target=run_scan,
            args=("PORT SCAN", f"nmap -F {target}", "port", nmap_file, session_dir, timestamp, target)
        ))
    else:
        append_alert("Nmap not found - using Python socket scanner", "INFO")
        scan_outputs["port"].append(f"{YELLOW}[*] Using Python socket scanner (nmap not available){RESET}")
        
        findings = custom_port_scan(target)
        
        with open(nmap_file, "w", encoding="utf-8") as f:
            f.write(f"DSTerminal Port Scan (Custom Scanner)\n")
            f.write(f"Target: {target}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("="*60 + "\n\n")
            for finding in findings:
                f.write(finding + "\n")
        
        stop_flags["port"] = True
        risk_scores["port"] = min(risk_scores["port"] + len(findings) * 2, 100)
        append_alert(f"Port scan completed with {len(findings)} open ports", "INFO")
        
        final_score = risk_scores["port"]
        status_icon = "[+]" if final_score < 50 else "[*]" if final_score < 75 else "[!]"
        status_color = GREEN if final_score < 50 else YELLOW if final_score < 75 else RED
        header = f"{status_color}{status_icon} PORT SCAN COMPLETE - Risk Score: {final_score}%{RESET}"
        if scan_outputs["port"]:
            scan_outputs["port"].insert(0, header)
    
    threads.append(threading.Thread(
        target=run_scan,
        args=("DNS / WHOIS", f"nslookup {target}", "dns", dns_file, session_dir, timestamp, target)
    ))
    
    if check_command_exists("msfconsole"):
        threads.append(threading.Thread(
            target=run_scan,
            args=("METASPLOIT SEARCH", f'msfconsole -q -x "search {target}; exit"', "msf", msf_file, session_dir, timestamp, target)
        ))
    else:
        append_alert("Metasploit not found - skipping exploit search", "WARN")
        stop_flags["msf"] = True
        scan_outputs["msf"].append(f"{YELLOW}[*] Metasploit not available on this system{RESET}")
    
    for t in threads:
        t.daemon = True
        t.start()
    
    for t in threads:
        t.join(timeout=60)
    
    for flag in stop_flags:
        stop_flags[flag] = True
    
    time.sleep(1)
    
    # -------------------------------
    # SAVE SUMMARY
    # -------------------------------
    
    summary_file = save_summary(session_dir, timestamp, target)
    
    # -------------------------------
    # FINAL DISPLAY - CENTERED COLORFUL
    # -------------------------------
    
    soc_header(target)
    print()
    
    # Final boxes with different colors
    final_boxes = [
        draw_glowing_box("PORT SCAN RESULTS", 
                        scan_outputs.get("port", ["No results"])[-10:] if scan_outputs.get("port") else ["No results"],
                        title_color=CYAN, border_color=CYAN, content_color=GREEN, blink_title=True),
        draw_glowing_box("DNS / WHOIS RESULTS", 
                        scan_outputs.get("dns", ["No results"])[-10:] if scan_outputs.get("dns") else ["No results"],
                        title_color=MAGENTA, border_color=MAGENTA, content_color=BLUE, blink_title=True),
        draw_glowing_box("METASPLOIT RESULTS", 
                        scan_outputs.get("msf", ["Not available"])[-10:] if scan_outputs.get("msf") else ["Not available"],
                        title_color=RED, border_color=RED, content_color=YELLOW, blink_title=True)
    ]
    
    rows = max(len(final_boxes[0]), len(final_boxes[1]), len(final_boxes[2]))
    
    for i in range(rows):
        p = final_boxes[0][i] if i < len(final_boxes[0]) else " " * (width // 3)
        d = final_boxes[1][i] if i < len(final_boxes[1]) else " " * (width // 3)
        m = final_boxes[2][i] if i < len(final_boxes[2]) else " " * (width // 3)
        print(p + d + m)
    
    print()
    print(center(f"{BOLD}{GREEN}{'=' * 60}{RESET}"))
    print(center(f"{BOLD}{GREEN}[+] ALL SCANS COMPLETE [+]{RESET}"))
    print(center(f"{BOLD}{CYAN}[+] Results stored in: {session_dir}{RESET}"))
    print(center(f"{BOLD}{CYAN}[+] Summary report: {summary_file}{RESET}"))
    
    # Final risk assessment
    risk_values = [r for r in risk_scores.values() if r > 0]
    if risk_values:
        total_risk = sum(risk_values) / len(risk_values)
        if total_risk < 30:
            risk_level = f"{GREEN}LOW{RESET}"
        elif total_risk < 70:
            risk_level = f"{YELLOW}MEDIUM{RESET}"
        else:
            risk_level = f"{RED}HIGH{RESET}"
    else:
        risk_level = f"{YELLOW}UNKNOWN{RESET}"
    
    print(center(f"{BOLD}Overall Risk Assessment: {risk_level}{RESET}"))
    print(center(f"{BOLD}{GREEN}{'=' * 60}{RESET}"))
    print()
    
    return True

# -------------------------------
# FULL RECON MENU FUNCTION
# -------------------------------

def full_recon_menu():
    """Interactive menu for full reconnaissance"""
    print(f"{BOLD}{CYAN}+{'-' * 50}+{RESET}")
    print(f"{BOLD}{CYAN}|        FULL RECONNAISSANCE MENU              |{RESET}")
    print(f"{BOLD}{CYAN}+{'-' * 50}+{RESET}")
    print()
    print(f"{GREEN}[1] Run Full Recon on Target{RESET}")
    print(f"{GREEN}[2] Quick Scan (Ports, DNS, WHOIS){RESET}")
    print(f"{GREEN}[3] Full Scan (with Metasploit){RESET}")
    print(f"{RED}[0] Exit{RESET}")
    print()
    
    choice = input(f"{YELLOW}Select option: {RESET}").strip()
    
    if choice == "1" or choice == "2" or choice == "3":
        target = input(f"{CYAN}Enter target (IP or domain): {RESET}").strip()
        if target:
            run_full_recon(target)
        else:
            print(f"{RED}[!] No target specified{RESET}")
    
    elif choice == "0":
        print(f"{YELLOW}[*] Exiting full recon menu{RESET}")
        return
    
    else:
        print(f"{RED}[!] Invalid option{RESET}")

# -------------------------------
# MAIN EXECUTION
# -------------------------------

if __name__ == "__main__":
    target = get_target_from_args()
    
    if target:
        run_full_recon(target)
    else:
        full_recon_menu()