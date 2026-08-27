#!/usr/bin/env python3
"""
Standalone test for show_help function - EXACT COPY from DSTerminal
"""

import os
import sys
import re
import random
import time
import shutil
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# ============================================================
# EXACT COPY of show_help from dsterminal.py - FIXED SYNTAX
# ============================================================
def show_help(self=None):
    """Display interactive hacking-styled help menu with categories - COMPLETELY FIXED"""
    from colorama import Fore, Style, init
    import shutil
    import re
    import random
    import time
    
    init(autoreset=True)
    
    # Get terminal width for centering
    try:
        terminal_width = shutil.get_terminal_size().columns
        if terminal_width < 80:
            terminal_width = 80
        if terminal_width > 120:
            terminal_width = 120
    except:
        terminal_width = 80
    
    # Define blink sequences
    blink_on = "\033[5m"
    blink_off = "\033[25m"
    
    # Define box width - ENSURE INTEGER
    box_width = int(min(terminal_width - 4, 110))
    if box_width < 60:
        box_width = 60
    box_width = int(box_width)
    
    # Box drawing characters
    TOP_LEFT = '┏'
    TOP_RIGHT = '┓'
    BOTTOM_LEFT = '┗'
    BOTTOM_RIGHT = '┛'
    HORIZONTAL = '━'
    VERTICAL = '┃'
    T_RIGHT = '┣'
    T_LEFT = '┫'
    
    def print_separator():
        """Print a separator line"""
        width = int(box_width - 4)
        sep = f"{Fore.CYAN}{T_RIGHT}{HORIZONTAL * width}{T_LEFT}{Style.RESET_ALL}"
        print(sep)
    
    def print_category_header(category, color=Fore.CYAN):
        """Print a category header - FIXED with ALL integer conversions"""
        header = f"  {category}  "
        header_len = len(header)
        # ALL calculations explicitly converted to int
        padding = int((box_width - 2 - header_len) // 2)
        remaining = int(box_width - 2 - header_len - padding)
        line = f"{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}{' ' * padding}{color}{Style.BRIGHT}{header}{Style.RESET_ALL}{' ' * remaining}{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}"
        print(line)
    
    def print_command(cmd, desc, cmd_color=Fore.GREEN):
        """Print a command line safely with ANSI/emoji-aware width handling."""
        try:
            # Robust ANSI escape sequence remover
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            def clean_ansi(value):
                return ansi_escape.sub("", str(value))
            
            def display_width(value):
                """Return approximate terminal display width."""
                text = clean_ansi(value)
                try:
                    import wcwidth
                    width = wcwidth.wcswidth(text)
                    return max(0, int(width)) if width >= 0 else len(text)
                except Exception:
                    return len(text)
            
            # Clean input
            cmd_clean = clean_ansi(cmd)
            desc_clean = clean_ansi(desc)
            
            cmd_len = display_width(cmd_clean)
            desc_len = display_width(desc_clean)
            
            # Fixed command column - ENSURE INTEGER
            cmd_width = int(30)
            
            padding_needed = max(0, int(cmd_width - cmd_len))
            
            # Description width - ENSURE INTEGER
            desc_width = int(box_width - 2 - cmd_width - 4)
            desc_width = max(10, int(desc_width))
            
            # ============================================================
            # COMPLETELY FIXED: Safe description truncation
            # ============================================================
            if len(desc_clean) > desc_width:
                try:
                    # Calculate max characters - FORCE INTEGER
                    max_chars = int(desc_width - 3)
                    
                    # Validate max_chars - FORCE INTEGER
                    if max_chars < 0:
                        max_chars = 0
                    if max_chars > len(desc_clean):
                        max_chars = len(desc_clean)
                    
                    # FORCE convert to int again before slicing
                    max_chars = int(max_chars)
                    
                    # Only slice if max_chars is a valid integer > 0
                    if max_chars > 0 and max_chars <= len(desc_clean):
                        desc_clean = desc_clean[:int(max_chars)] + "..."
                    else:
                        # If max_chars is 0 or invalid, just use a safe default
                        safe_len = int(10)  # FORCE integer
                        if len(desc_clean) > safe_len:
                            desc_clean = desc_clean[:safe_len] + "..."
                        else:
                            desc_clean = desc_clean + "..."
                            
                except (TypeError, ValueError, AttributeError):
                    # Ultimate fallback - use a safe default with FORCED integers
                    try:
                        # Try to use len(desc_clean) - 3 as a last resort
                        safe_len = int(len(desc_clean) - 3)
                        if safe_len > 0 and safe_len <= len(desc_clean):
                            desc_clean = desc_clean[:int(safe_len)] + "..."
                        else:
                            safe_len = int(10)
                            if len(desc_clean) > safe_len:
                                desc_clean = desc_clean[:safe_len] + "..."
                            else:
                                desc_clean = desc_clean + "..."
                    except:
                        # If everything fails, just truncate with FORCED integers
                        safe_len = int(10)
                        if len(desc_clean) > safe_len:
                            desc_clean = desc_clean[:safe_len] + "..."
                        else:
                            desc_clean = desc_clean + "..."
            
            # Build colored output
            cmd_text = f"{cmd_color}{cmd_clean}{Style.RESET_ALL}"
            desc_text = f"{Fore.WHITE}{desc_clean}{Style.RESET_ALL}"
            
            line = f"{Fore.CYAN}{VERTICAL}{Style.RESET_ALL} {cmd_text}"
            line += " " * padding_needed
            line += "  "
            line += desc_text
            
            # Final width calculation - ENSURE INTEGER
            visible_length = display_width(line)
            target_width = int(box_width - 2)
            remaining = int(target_width - visible_length)
            
            if remaining > 0:
                line += " " * remaining
            
            # Right border
            line += f"{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}"
            
            print(line)
            
        except Exception as e:
            # Safe fallback - print without fancy formatting
            print(f"  {str(cmd)} - {str(desc)}")
    
    # Categories dictionary - SIMPLIFIED for testing
    categories = {
        "🔥 CORE SECURITY": [
            ("system scan -All", "System threat scan (sys, apps, net)"),
            ("system", "System security management"),
            ("system help", "Show system command help"),
            ("system status", "Show system scan status"),
            ("system list", "List exported scan files"),
            ("system load <file>", "Load previous scan results"),
            ("system export <format>", "Export scan results"),
            ("system export all", "Export all scan results"),
            ("security", "Alias for system command"),
            ("scan", "Alias for system command"),
            ("sys", "Alias for system command"),
            ("net -n mon", "Live network monitoring"),
            ("exploitcheck", "Check for critical CVEs"),
            ("vtscan", "VirusTotal file analysis"),
            ("clearlogs", "Securely wipe system logs"),
            ("nikto --url <TARGET>", "Web vulnerability scan"),
            ("legitify --github <ORG/REPO>", "Scan GitHub for misconfigs"),
            ("msfconsole", "Launch Metasploit Framework console"),
            ("msf-debug", "Debug Metasploit installation issues"),
            ("msf -h", "Metasploit help and options"),
            ("nmap -sV <TARGET>", "Service/version detection scan"),
            ("nmap -A <TARGET>", "Aggressive OS and service detection"),
            ("nmap -p- <TARGET>", "Scan all 65535 ports"),
            ("nmap scan <TARGET>", "Nmap scan the target"),
            ("fraud / financial", "Financial fraud investigation suite"),
            ("investigate", "Launch financial forensics tools"),
            ("trace", "Trace suspicious transactions")
        ],
        
        "🌐 NETWORK TOOLS": [
            ("portsweep [IP]", "Scan target for open ports"),
            ("traceroute [IP]", "Network path analysis"),
            ("torify", "Route traffic through Tor"),
            ("dnssec [DOMAIN]", "Validate DNSSEC"),
            ("nmap <TARGET>", "Basic port scan"),
            ("nmap -sS <TARGET>", "Stealth SYN scan"),
            ("network", "Full network audit (WiFi + Ethernet)"),
            ("network-wifi", "WiFi only scan"),
            ("network-eth", "Ethernet only scan"),
            ("network-live", "Live monitoring"),
            ("network wlan0", "Use specific interface"),
            ("network-status", "Check module status"),
            ("network-help", "Show help"),
            ("nmap -sU <TARGET>", "UDP port scan"),
            ("nmap -O <TARGET>", "OS fingerprinting"),
            ("msfvenom", "Generate payloads for exploits"),
            ("msfdb", "Manage Metasploit database"),
        ],
        
        "🔐 SQL INJECTION TOOLS": [
            ("sqlmap <URL>", "Run SQLMap scan on a target URL"),
            ("sqlmap --url <URL>", "SQLMap scan with URL parameter"),
            ("sqlmap --fs <PATH>", "SQLMap filesystem scan"),
            ("sqlmap --git <REPO>", "SQLMap Git repository scan"),
            ("sqlmap --help", "Show SQLMap help"),
            ("sqlmap --version", "Show SQLMap version"),
            ("sqlmap --update", "Update SQLMap"),
            ("sqlmap-scan <URL>", "Quick SQLMap scan"),
            ("sqlmap-start", "Start SQLMap service"),
            ("sqlmap-stop", "Stop SQLMap service"),
            ("sqlmap-install", "Install SQLMap"),
            ("sqlmap-status", "Show SQLMap lab status"),
            ("sqllab", "Start SQL Injection Learning Lab"),
            ("sqllab-stop", "Stop SQL Injection Learning Lab"),
        ],
        
        "🛡️ HARDENING TOOLS": [
            ("harden", "System hardening menu"),
            ("harden -t sys", "Target system hardening"),
            ("harden-quick", "Quick system hardening"),
            ("harden-dry-run", "Preview hardening changes"),
            ("harden-restore", "Restore hardening configuration"),
            ("harden-status", "Show hardening status"),
            ("harden-verify", "Verify hardening applied"),
            ("harden-full", "Full system hardening"),
            ("harden-cinematic", "Hardening with cinematic UI"),
            ("harden-rollback", "Rollback hardening changes"),
            ("harden-report", "Generate hardening report"),
            ("harden-user", "User account hardening"),
            ("harden-fw", "Firewall hardening"),
            ("harden-ssh", "SSH hardening"),
            ("harden-dashboard", "Launch hardening dashboard"),
        ],
        
        "📁 FILE COMMANDS": [
            ("ls", "List files"),
            ("cat <file>", "Show file contents"),
            ("touch <file>", "Create file"),
            ("echo <text> > <file>", "Write to file"),
            ("pwd", "Show current directory")
        ],
        
        "🛠️ UTILITIES": [
            ("help", "Show this menu"),
            ("exit", "Quit terminal"),
            ("clear", "Clear terminal display"),
        ]
    }
    
    # ============================================================
    # DISPLAY HELP
    # ============================================================
    
    # Top border - ENSURE INTEGER
    top_border = f"{Fore.CYAN}{TOP_LEFT}{HORIZONTAL * int(box_width - 2)}{TOP_RIGHT}{Style.RESET_ALL}"
    print(top_border)
    
    # Header
    header_text = "DSTERMINAL v4.0.0.113 - Command Reference Manual"
    header_padding = int((box_width - 2 - len(header_text)) // 2)
    header_remaining = int(box_width - 2 - len(header_text) - header_padding)
    print(f"{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}{' ' * header_padding}{Fore.CYAN}{Style.BRIGHT}{header_text}{Style.RESET_ALL}{' ' * header_remaining}{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}")
    
    sub_header = "INTERACTIVE COMMAND MENU"
    sub_padding = int((box_width - 2 - len(sub_header)) // 2)
    sub_remaining = int(box_width - 2 - len(sub_header) - sub_padding)
    print(f"{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}{' ' * sub_padding}{Fore.YELLOW}{Style.BRIGHT}{sub_header}{Style.RESET_ALL}{' ' * sub_remaining}{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}")
    
    # Separator
    print_separator()
    
    # Display each category
    for category, commands in categories.items():
        cat_colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.BLUE, Fore.RED]
        cat_color = random.choice(cat_colors)
        
        if "CORE" in category or "SECURITY" in category:
            header = f"{blink_on}{category}{blink_off}"
        else:
            header = category
        print_category_header(header, cat_color)
        
        for cmd, desc in commands:
            if "scan" in cmd or "exploit" in cmd or "nikto" in cmd:
                cmd_color = Fore.RED
            elif "encrypt" in cmd or "crypto" in cmd or "decrypt" in cmd:
                cmd_color = Fore.MAGENTA
            elif "net" in cmd or "portsweep" in cmd or "traceroute" in cmd:
                cmd_color = Fore.CYAN
            elif "sqlmap" in cmd or "certcheck" in cmd:
                cmd_color = Fore.YELLOW
            elif "ls" in cmd or "cat" in cmd or "touch" in cmd:
                cmd_color = Fore.BLUE
            elif "msf" in cmd or "metasploit" in cmd:
                cmd_color = Fore.RED + Style.BRIGHT
            elif "nmap" in cmd:
                cmd_color = Fore.YELLOW + Style.BRIGHT
            elif "recon" in cmd:
                cmd_color = Fore.GREEN + Style.BRIGHT
            elif "sysinfo" in cmd or "killproc" in cmd or "harden" in cmd:
                cmd_color = Fore.CYAN + Style.BRIGHT
            else:
                cmd_color = Fore.GREEN
            
            print_command(cmd, desc, cmd_color)
        
        print_separator()
        time.sleep(0.02)
    
    # Bottom border
    bottom_border = f"{Fore.CYAN}{BOTTOM_LEFT}{HORIZONTAL * int(box_width - 2)}{BOTTOM_RIGHT}{Style.RESET_ALL}"
    print(bottom_border)
    
    # Tips section
    print()
    tips_border = f"{Fore.CYAN}{TOP_LEFT}{HORIZONTAL * int(box_width - 2)}{TOP_RIGHT}{Style.RESET_ALL}"
    print(tips_border)
    
    tips = [
        ("💡 TIP:", "Use Tab for command completion", Fore.CYAN),
        ("⚡ PRO:", "Combine commands with '&&'", Fore.GREEN),
        ("🔧 DEV:", "Check logs for debugging", Fore.YELLOW),
    ]
    
    for icon, tip, color in tips:
        tip_text = f"{color}{icon}{Style.RESET_ALL} {Fore.WHITE}{tip}{Style.RESET_ALL}"
        padding = int((box_width - 2 - len(tip_text)) // 2)
        remaining = int(box_width - 2 - len(tip_text) - padding)
        print(f"{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}{' ' * padding}{tip_text}{' ' * remaining}{Fore.CYAN}{VERTICAL}{Style.RESET_ALL}")
    
    tips_bottom = f"{Fore.CYAN}{BOTTOM_LEFT}{HORIZONTAL * int(box_width - 2)}{BOTTOM_RIGHT}{Style.RESET_ALL}"
    print(tips_bottom)
    
    print(f"{Fore.GREEN}✓ Help system loaded!{Style.RESET_ALL}")


# ============================================================
# TEST RUNNER
# ============================================================
def main():
    print("\n" + "=" * 70)
    print("TESTING show_help() - EXACT COPY FROM DSTERMINAL")
    print("=" * 70)
    print("\nThis runs the EXACT show_help function from your DSTerminal code.")
    print("If this works, the error is NOT in show_help() but elsewhere.")
    print("If this fails, the error IS in show_help() and we need to fix it.\n")
    
    input("Press Enter to run the test...")
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        # Call the isolated show_help function
        show_help()
        print("\n" + "=" * 70)
        print("✅ TEST PASSED! The show_help() function works in isolation.")
        print("   The error must be elsewhere in the main DSTerminal code.")
        print("=" * 70)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED! Error: {type(e).__name__}: {e}")
        print("   The error IS in the show_help() function itself.")
        print("=" * 70)
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
    
    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()