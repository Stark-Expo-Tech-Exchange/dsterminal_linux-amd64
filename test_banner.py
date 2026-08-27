#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test file for DSTERMINAL banner and typing effects - CENTERED TYPING FIX
"""

import os
import sys
import time
import random
import shutil
import re
import platform
import traceback

# Set up proper encoding for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Try to import colorama
try:
    from colorama import Fore, Style, init, Back
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
        DIM = '\033[2m'
        LIGHTRED_EX = '\033[91m'
        LIGHTGREEN_EX = '\033[92m'
        LIGHTYELLOW_EX = '\033[93m'
        LIGHTCYAN_EX = '\033[96m'
        LIGHTMAGENTA_EX = '\033[95m'
        LIGHTBLUE_EX = '\033[94m'
    
    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'

# ============================================================
# GLOBAL TYPING FUNCTION - CENTERED TYPING FIX
# ============================================================
def type_text_colored(text, end="\n", color=None, bold=False, delay=0.025, centered=False, width=None):
    """
    Type text with human-like pen writing speed.
    If centered=True, the text will be typed at the center position.
    """
    try:
        # Calculate centering if needed
        if centered:
            if width is None:
                try:
                    width = shutil.get_terminal_size().columns
                except:
                    width = 120
            if width < 60:
                width = 60
            
            # Strip ANSI codes for length calculation
            ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\[[0-9;]*m|\x1b\[[0-9;]*[A-Za-z]')
            clean_text = ansi_escape.sub('', text)
            clean_text = re.sub(r'\x1b\[[0-9;]*m', '', clean_text)
            clean_text = re.sub(r'\x033\[[0-9;]*m', '', clean_text)
            
            padding = max(0, (width - len(clean_text)) // 2)
            # Move cursor to the center position
            sys.stdout.write('\r' + ' ' * padding)
            sys.stdout.flush()
        
        # Write color if provided
        if color:
            if bold:
                sys.stdout.write(Style.BRIGHT if COLORAMA_AVAILABLE else '\033[1m')
            sys.stdout.write(color)
            sys.stdout.flush()
        
        # Type each character with natural pauses
        for char in text:
            try:
                sys.stdout.write(char)
                sys.stdout.flush()
            except UnicodeEncodeError:
                try:
                    sys.stdout.write(char.encode('utf-8', errors='replace').decode('utf-8'))
                    sys.stdout.flush()
                except:
                    sys.stdout.write('?')
                    sys.stdout.flush()
            
            # Natural typing variations
            if char in '.!?,;:':
                time.sleep(delay * 2.0)
            elif char == ' ':
                time.sleep(delay * 0.5)
            else:
                time.sleep(delay)
        
        # Reset color
        if color:
            if COLORAMA_AVAILABLE:
                sys.stdout.write(Style.RESET_ALL)
            else:
                sys.stdout.write('\x1b[0m')
        
        if end:
            sys.stdout.write(end)
        sys.stdout.flush()
    except Exception as e:
        print(f"Error in type_text_colored: {e}")
        print(text)

# ============================================================
# CENTERING HELPER - FOR PRE-CENTERED TEXT
# ============================================================
def center_text(text, width=None):
    """Center text within terminal width - properly handles ANSI codes"""
    if width is None:
        try:
            width = shutil.get_terminal_size().columns
        except:
            width = 120
    
    if width < 60:
        width = 60
    
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\[[0-9;]*m|\x1b\[[0-9;]*[A-Za-z]')
    clean_text = ansi_escape.sub('', text)
    clean_text = re.sub(r'\x1b\[[0-9;]*m', '', clean_text)
    clean_text = re.sub(r'\x033\[[0-9;]*m', '', clean_text)
    
    padding = max(0, (width - len(clean_text)) // 2)
    return ' ' * padding + text

# ============================================================
# COLOR GENERATOR - RETURNS RANDOM COLOR EACH CALL
# ============================================================
def get_random_color():
    """Returns a random color from the available colorama colors"""
    colors = [
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
        Fore.MAGENTA, Fore.CYAN, Fore.LIGHTRED_EX,
        Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX,
        Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX
    ]
    return random.choice(colors)

# ============================================================
# TEST BANNER DISPLAY
# ============================================================
def test_banner():
    """Test the banner display with proper centered typing"""
    try:
        # Clear screen
        os.system('cls' if platform.system().lower() == "windows" else 'clear')
        
        # Get terminal width
        try:
            terminal_width = shutil.get_terminal_size().columns
        except:
            terminal_width = 120
        
        if terminal_width < 60:
            terminal_width = 60
        
        # Neon color definitions
        NEON_CYAN = '\033[38;5;51m'
        NEON_GREEN = '\033[38;5;46m'
        NEON_PINK = '\033[38;5;201m'
        NEON_YELLOW = '\033[38;5;226m'
        NEON_PURPLE = '\033[38;5;199m'
        NEON_BLUE = '\033[38;5;45m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        
        neon_colors = [NEON_GREEN, NEON_CYAN, NEON_PINK, NEON_YELLOW, NEON_PURPLE, NEON_BLUE]
        ascii_color = random.choice(neon_colors)
        
        banner_lines = [
            f"{NEON_CYAN}╔══════════════════════════════════════════════════════════════╗{RESET}",
            f"{NEON_CYAN}║{RESET}  {BOLD}{ascii_color}██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗         {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {BOLD}{ascii_color}██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║         {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {BOLD}{ascii_color}██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║         {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {BOLD}{ascii_color}██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║         {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {BOLD}{ascii_color}██████╔╝███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗    {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {BOLD}{ascii_color}╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝    {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}                                                                                                 {NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}               {NEON_YELLOW}[ ENCRYPTION SUITE v4.0.0.113 - EDITION ]{RESET}                     {NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}              {NEON_PINK}=========================================={RESET}                       {NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}╠══════════════════════════════════════════════════════════════╣{RESET}",
            f"{NEON_CYAN}║{RESET}  {NEON_CYAN}Version       :{RESET} {NEON_GREEN}4.0.0.113                                          {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {NEON_CYAN}Operator ID   :{RESET} {NEON_GREEN}OP-TEST123                                          {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {NEON_CYAN}Session ID    :{RESET} {NEON_GREEN}SESSION-TEST                                        {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {NEON_CYAN}Host          :{RESET} {NEON_GREEN}{platform.node():<46}{RESET} {NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}║{RESET}  {NEON_CYAN}Workspace     :{RESET} {NEON_GREEN}test_workspace                                       {RESET}{NEON_CYAN}║{RESET}",
            f"{NEON_CYAN}╚══════════════════════════════════════════════════════════════╝{RESET}"
        ]
        
        # Display banner - fast
        print("\n")
        for line in banner_lines:
            centered = center_text(line)
            sys.stdout.write(centered + '\n')
            sys.stdout.flush()
            time.sleep(0.005)
        
        print("\n")
        
        # Startup messages with centered typing - EACH GETS RANDOM COLOR
        startup_messages = [
            "⚡ INITIALIZING DSTERMINAL ENGINE...",
            "🔐 Loading security modules...",
            "📡 Establishing secure uplink...",
            "🛰️ Connecting to update servers...",
            "🛰️ Connected...",
            "🔍 Scanning system architecture...",
            "🛡️ Activating firewall protocols...",
            "🌐 Routing through secure nodes...",
            "📊 Analyzing system integrity...",
            "🔑 Generating session encryption keys...",
            "📦 Preparing update infrastructure...",
            "✅ Verification protocols engaged...",
            "🚀 Launching DSTERMINAL Core..."
        ]
        
        typing_speed = 0.025
        
        print("Typing Speed Test (centered typing with random colors):\n")
        
        # Each message gets a RANDOM COLOR
        for msg in startup_messages:
            color = get_random_color()
            type_text_colored(msg, color=color, bold=True, delay=typing_speed, centered=True, width=terminal_width)
            print()
            time.sleep(0.01)
        
        print("\n")
        
        # Completion messages - EACH GETS RANDOM COLOR
        completion_messages = [
            "✅ SECURE CONNECTION ESTABLISHED!",
            "🛡️ All security protocols active",
            "📡 Update servers synchronized",
            "🔑 Session keys generated successfully",
            "🚀 DSTERMINAL Core initialized"
        ]
        
        for msg in completion_messages:
            color = get_random_color()
            type_text_colored(msg, color=color, bold=True, delay=typing_speed, centered=True, width=terminal_width)
            print()
            time.sleep(0.0003)
        
        print("\n")
        
        # System status - EACH GETS RANDOM COLOR
        status_messages = [
            "SYSTEM STATUS:",
            "  ✅ DSTERMINAL v4.0.0.113 loaded",
            "  ✅ User authenticated: TEST-USER",
            "  ✅ Session ID: TEST-SESSION",
            "  ✅ Workspace: test_workspace",
            "  ✅ System ready for operations",
            "\n⏱️  Initialization time: 20 seconds"
        ]
        
        for msg in status_messages:
            color = get_random_color()
            type_text_colored(msg, color=color, bold=True, delay=typing_speed, centered=True, width=terminal_width)
            print()
            time.sleep(0.5)
        
        print("\n")
        print("=" * 60)
        # Final message with random color
        final_color = get_random_color()
        type_text_colored("✅ Test completed successfully!", color=final_color, bold=True, centered=True, width=terminal_width)
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"Error in test_banner: {e}")
        traceback.print_exc()
        print("\nPress any key to exit...")
        try:
            input()
        except:
            pass

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    test_banner()