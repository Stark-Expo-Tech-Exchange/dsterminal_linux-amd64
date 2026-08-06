# -*- coding: utf-8 -*-
# ============================================================================
# GLOBAL VARIABLES - Single source of truth
# ============================================================================

GLOBAL_OPERATOR = None
GLOBAL_SESSION = None
COLORS_AVAILABLE = True
SOC_NMAP_AVAILABLE = False
INTEGRITY_AVAILABLE = False
VT_AVAILABLE = False
RECON_AVAILABLE = False
RECON_FULL_AVAILABLE = False
HARDENING_AVAILABLE = False
RANSOMWARE_AVAILABLE = False
FINANCIAL_FORENSICS_AVAILABLE = False
WEB_SECURITY_AVAILABLE = False
CRYPTO_AVAILABLE = False
PSUTIL_AVAILABLE = False

# ============================================================================
# GLOBAL VARIABLES - Single source of truth
# ============================================================================


import sys
import queue
import subprocess
import os
import platform

def maximize_terminal():
    """Maximize terminal window on startup - Cross Platform"""
    system = platform.system()
    
    if system == "Windows":
        try:
            subprocess.run(['powershell', '-Command', 
                '$hwnd = (Get-Process -Id $pid).MainWindowHandle; '
                'Add-Type -MemberDefinition @"[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);"@ -Name "Win32" -Namespace "Utils"; '
                '[Utils.Win32]::ShowWindow($hwnd, 3)'], 
                capture_output=True, timeout=2)
        except:
            pass
    
    elif system == "Linux":
        try:
            result = subprocess.run(['which', 'xdotool'], capture_output=True, timeout=1)
            if result.returncode == 0:
                subprocess.run(['xdotool', 'getactivewindow', 'windowsize', '100%', '100%'], capture_output=True, timeout=1)
            else:
                sys.stdout.write('\x1b[8;40;140t')
                sys.stdout.flush()
        except:
            pass
    
    elif system == "Darwin":  # macOS
        try:
            applescript = '''
            tell application "Terminal"
                activate
                set bounds of front window to {0, 22, 1440, 878}
                set front window's size to {140, 40}
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], capture_output=True, timeout=2)
        except:
            try:
                sys.stdout.write('\x1b[8;40;140t')
                sys.stdout.flush()
            except:
                pass

# Call maximize_terminal with timeout protection
try:
    maximize_terminal()
except:
    pass

# ==
# Get base path - DEFINE THIS FIRST
# ==
def get_base_path():
    """Get the base path for the application"""
    if getattr(sys, 'frozen', False):
        # Add your code here
        pass
# Call the function at startup
maximize_terminal()

import tempfile
from pathlib import Path
# Add at the top of the file with other imports
import timezonefinder
import pytz
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# Then update the imports in live_monitor
def get_base_path():
    """Get the base path for the application (works for both development and installed versions)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        else:
            return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
if BASE_PATH not in sys.path:
    sys.path.insert(0, BASE_PATH)

try:
    os.chdir(BASE_PATH)
except:
    pass

# ==
# WORKSPACE - Define BEFORE using
# ==
def init_workspace():
    workspace_path = os.path.expanduser("~/dsterminal_workspace")
    subdirs = ["sandbox", "scans", "exploits", "reports", "operators", 
               "backups", "logs", "config", "database", "temp"]
    try:
        os.makedirs(workspace_path, exist_ok=True)
        for subdir in subdirs:
            os.makedirs(os.path.join(workspace_path, subdir), exist_ok=True)
        os.makedirs(os.path.join(workspace_path, "reports", "network_reports"), exist_ok=True)
        os.makedirs(os.path.join(workspace_path, "reports", "threat_maps"), exist_ok=True)
        os.makedirs(os.path.join(workspace_path, "reports", "forensic"), exist_ok=True)
        return workspace_path
    except:
        return os.path.expanduser("~/dsterminal_workspace")

WORKSPACE = init_workspace()

# ==
# FAST IMPORTS - Only import what's needed
# ==
import tempfile
from pathlib import Path
import time
import random
import json
import os
import sys
import platform
import subprocess
import shutil
import socket
import uuid
import hashlib
import logging
import threading
import queue
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter, WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
# 
# Import edu_typing_engine - NOW BASE_PATH is defined
# 
# Set the base path

# Add the base path to Python path
if BASE_PATH not in sys.path:
    sys.path.insert(0, BASE_PATH)

try:
    os.chdir(BASE_PATH)
except:
    pass
# Change to the base path
os.chdir(BASE_PATH)

# Now continue with the rest of your imports and code...
# ===
VERSION = "2.1.327"
APP_NAME = "DSTerminal"
DESCRIPTION = "Defensive Security Terminal"
AUTHOR = "Spark Wilson Spink | Powered By Stark Expo Tech Exchange"

def show_version():
    print(f"{APP_NAME} v{VERSION}")
    print(DESCRIPTION)
    print(f"Developed by {AUTHOR}")

def run_terminal():
    """Initialize and run the security terminal"""
    terminal = SecurityTerminal()
    terminal.run()


def main():
    """Main entry point for DSTerminal."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--version", "-v", "version"]:
            show_version()
            return
        if arg == "--monitor-only":
            from deletion_protection import DSTerminalMonitor
            from workspace import SimpleWorkspace
            return
    try:
        terminal = SecurityTerminal()
        terminal.run()
    except KeyboardInterrupt:
        print("\\n[!] Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    if '--monitor-only' in sys.argv:
        import time
        from platform_detector import PlatformDetector
        from workspace import SimpleWorkspace
        
        ws_idx = sys.argv.index('--workspace') if '--workspace' in sys.argv else None
        paths_idx = sys.argv.index('--paths') if '--paths' in sys.argv else None
        
        workspace_path = sys.argv[ws_idx + 1] if ws_idx else os.getcwd()
        
        print("""
╔══════════════════════════════════════════════════════╗
║         DSTERMINAL DELETION PROTECTION               ║
║         Background Monitoring Active                 ║
║         Close this window to stop                    ║
╚══════════════════════════════════════════════════════╝
        """)
        
        # Load config with all paths
        if paths_idx:
            monitor_paths = sys.argv[paths_idx + 1].split(',')
        else:
            pd = PlatformDetector()
            monitor_paths = pd.get_trash_paths()
        
        config = {
            'version': '4.0.0.113',
            'monitor_paths': monitor_paths,
            'exclude_patterns': ['*.tmp', '*.temp', '*~', '.DS_Store', 'Thumbs.db'],
            'max_file_size': 100 * 1024 * 1024,
            'encrypt_backups': False,
        }
        
        ws = SimpleWorkspace(workspace_path)
        monitor = DSTerminalMonitor(config, ws, interactive=False, ui=None)
        
        from watchdog.observers import Observer
        observer = Observer()
        
        for path in monitor_paths:
            if os.path.exists(path):
                try:
                    observer.schedule(monitor, path=path, recursive=True)
                    print(f"  ✓ Monitoring: {path}")
                except Exception as e:
                    print(f"  ✗ Skipping {path}: {e}")
        
        observer.start()
        print(f"\n[*] Monitoring {len(monitor_paths)} folders.")
        print("[*] Press Ctrl+C to stop.\n")
        sys.stdout.flush()
        
        try:
            while True:
                time.sleep(1)
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n[*] Stopping...")
            observer.stop()
            observer.join()
            monitor.cleanup()
            print("[✓] Monitoring stopped.")
        
        sys.exit(0)
    
    # Normal terminal startup
    terminal = SecurityTerminal()
    terminal.run()