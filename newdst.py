#!/usr/bin/env python3
"""
DSTERMINAL - Cyber Security Terminal
With Intelligent Placeholder and SIEM Dashboard
"""

import sys
import os
import time
import random
import threading
import shutil
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import json
import re

# ============================================================
# PROMPT_TOOLKIT IMPORTS
# ============================================================

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style
    from prompt_toolkit.completion import NestedCompleter
    from prompt_toolkit.layout.processors import Processor, Transformation
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.layout import processors
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError as e:
    PROMPT_TOOLKIT_AVAILABLE = False
    print(f"[!] prompt_toolkit not available: {e}")

# ============================================================
# COLOR CLASS
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

# ============================================================
# PLACEHOLDER PROCESSOR
# ============================================================

class PlaceholderProcessor(Processor):
    """Processor that adds placeholder text to empty buffer with random colors"""
    
    def __init__(self, get_placeholder_data):
        self.get_placeholder_data = get_placeholder_data
    
    def apply_transformation(self, transformation_input):
        # Only show placeholder when buffer is empty
        if transformation_input.document.text:
            return Transformation(transformation_input.fragments)
        
        placeholder_data = self.get_placeholder_data()
        if not placeholder_data or not placeholder_data['text']:
            return Transformation(transformation_input.fragments)
        
        # Create formatted text with each character having its own color
        formatted = []
        for char, color in placeholder_data['colored_chars']:
            if color:
                formatted.append((f'fg:{color}', char))
            else:
                formatted.append(('', char))
        
        return Transformation(formatted)

# ============================================================
# SECURITY TERMINAL CLASS
# ============================================================

class SecurityTerminal:
    """Main Security Terminal with intelligent placeholder"""
    
    def __init__(self, quiet=False):
        self.quiet = quiet
        
        # Workspace setup
        self.workspace_path = os.path.expanduser("~/dsterminal_workspace")
        os.makedirs(self.workspace_path, exist_ok=True)
        os.makedirs(os.path.join(self.workspace_path, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_path, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_path, "quarantine"), exist_ok=True)
        
        # Initialize placeholder variables
        self.placeholder_text = ""
        self.placeholder_colors = []
        self.placeholder_lock = threading.Lock()
        self.current_input = ""
        self.cursor_running = False
        self.cursor_visible = True
        self.cursor_color_index = 0
        self.cursor_colors = ['#00ff88', '#00ccff', '#ff00ff', '#ffcc00']
        self.app = None
        self.session = None
        self.start_time = datetime.now()
        
        # Initialize SIEM metrics
        self.alert_count = random.randint(200, 300)
        self.critical_alerts = random.randint(8, 20)
        self.high_alerts = random.randint(30, 60)
        self.incident_count = random.randint(8, 18)
        self.risk_score = random.randint(60, 85)
        self.event_rate = random.randint(120, 250)
        self.active_sessions = random.randint(2, 8)
        self.mttr = f"{random.randint(3, 6)}.{random.randint(0, 9)}h"
        
        # Session ID
        self.session_id = f"DST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Log file
        self.log_file = os.path.join(self.workspace_path, "logs", f"session_{self.session_id}.log")
        
        print(f"[+] DSTERMINAL v4.0.0.113 initialized")
        print(f"[WORKSPACE] Reports: {self.workspace_path}/reports")
        print(f"[WORKSPACE] Logs: {self.workspace_path}/logs")
        print(f"[WORKSPACE] Quarantine: {self.workspace_path}/quarantine")
    
    def is_admin(self) -> bool:
        """Check if running with admin privileges"""
        try:
            return os.getuid() == 0
        except AttributeError:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    def log_command(self, cmd):
        """Log command to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {cmd}\n")
        except:
            pass
    
    def log_to_siem(self, msg):
        """Log to SIEM"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[SIEM] {msg}\n")
        except:
            pass
    
    def save_session_end(self):
        """Save session end"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Session ended\n")
        except:
            pass

    # ============================================================
    # CURSOR BLINK & ANIMATION
    # ============================================================

    def _start_cursor_blink(self):
        """Start the animated cursor in a background thread"""
        self.cursor_running = True
        self.cursor_thread = threading.Thread(target=self._animate_cursor, daemon=True)
        self.cursor_thread.start()

    def _animate_cursor(self):
        """Animate cursor with blinking and color cycling"""
        while self.cursor_running:
            self.cursor_visible = not self.cursor_visible
            if not self.cursor_visible:
                self.cursor_color_index = (self.cursor_color_index + 1) % len(self.cursor_colors)
            if hasattr(self, 'app') and self.app:
                try:
                    self.app.invalidate()
                except:
                    pass
            time.sleep(0.5)

    def _get_cursor_char(self) -> str:
        return "▌" if self.cursor_visible else " "

    def _get_cursor_color(self) -> str:
        return self.cursor_colors[self.cursor_color_index]

    def _get_uptime(self) -> str:
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"

    def _update_siem_metrics(self):
        """Update SIEM metrics in real-time"""
        self.alert_count += random.randint(-5, 10)
        self.alert_count = max(100, min(400, self.alert_count))
        self.critical_alerts += random.randint(-1, 2)
        self.critical_alerts = max(5, min(30, self.critical_alerts))
        self.high_alerts += random.randint(-2, 3)
        self.high_alerts = max(20, min(80, self.high_alerts))
        self.incident_count += random.randint(-1, 1)
        self.incident_count = max(8, min(25, self.incident_count))
        self.risk_score += random.randint(-2, 3)
        self.risk_score = max(50, min(95, self.risk_score))
        self.event_rate += random.randint(-10, 20)
        self.event_rate = max(50, min(300, self.event_rate))
        self.active_sessions += random.randint(-1, 1)
        self.active_sessions = max(1, min(10, self.active_sessions))

    # ============================================================
    # PLACEHOLDER METHODS
    # ============================================================

    def _get_placeholder_texts(self) -> list:
        """Return intelligent placeholder prompts"""
        return [
            "Type 'help' to see all available commands...",
            "Try 'system scan' to check for vulnerabilities...",
            "Use 'net mon' to monitor network traffic...",
            "Run 'soc status' to check security operations center...",
            "Type 'dashboard' to view live security metrics...",
            "Need to harden your system? Try 'harden'...",
            "Check for threats with 'ransomwatch'...",
            "Use 'integrity scan' to verify file integrity...",
            "Try 'crypto-verify' for cryptographic verification...",
            "Run 'vuln-scan' to identify vulnerabilities...",
            "Use 'recon' for network reconnaissance...",
            "Try 'sqlmap' for SQL injection testing...",
            "Use 'nikto' for web server scanning...",
            "Run 'trufflehog' to find secrets in code...",
            "Type 'exploit-scan' to check for exploits...",
            "Use 'forensic' for forensic analysis...",
            "Try 'fraud-investigate' for fraud detection...",
            "Run 'integrity restore' to restore files...",
            "Use 'crypto-backup' for cryptographic backups...",
            "Type 'system info' to view system information...",
            "Try 'net scan' for network scanning...",
            "Use 'websec' for web security analysis...",
            "Run 'wifi-audit' for wireless security audit...",
            "Type 'soc-intel' for threat intelligence...",
            "Need help? Type 'help <command>' for details...",
            "Use 'clear' to clean the terminal screen...",
            "Run 'dst-status' to check DSTERMINAL status...",
            "Type 'exit' to close the terminal safely...",
            "Remember to always verify with 'integrity verify'...",
            "Stay secure with 'harden-full' for complete hardening...",
            "Monitor your system with 'monitor start'...",
            "Check logs with 'dst-logs'...",
            "Use 'recon-full' for thorough reconnaissance...",
            "Try 'crypto-list' to list available crypto tools...",
            "Run 'stegcheck' for steganography detection...",
            "Use 'memdump' for memory analysis...",
            "Secure your network with 'harden-ssh'...",
            "Check firewall with 'harden-fw'...",
            "Use 'soc-reports' to generate security reports...",
            "Try 'ioc-education' to learn about IOCs...",
            "Run 'integrity-report' for integrity reports...",
            "Use 'crypto-export' to export crypto keys...",
            "Type 'harden-status' to check hardening status...",
            "Need to restore? Try 'restore-last'...",
            "Use 'list-backups' to see available backups...",
            "Try 'dst-workspace' to manage workspaces...",
            "Run 'auto-discover' for automatic discovery...",
            "Monitor all with 'monitor-all'...",
            "Type 'show-paths' to see configured paths...",
            "Use 'registry mon' to monitor registry...",
            "Run 'soc-start' to start SOC monitoring...",
            "Try 'soc-quick' for quick SOC scan...",
            "Generate reports with 'soc-report'...",
            "Check alerts with 'soc-alerts'...",
            "Use 'soc-map' for SOC mapping...",
            "Type 'soc-history' to view SOC history...",
            "Run 'soc-pdf' to export SOC report as PDF...",
            "Need to scan? Try 'scan-full' for complete scan...",
            "Use 'quick-scan' for fast scanning...",
            "Try 'deep-scan' for thorough analysis...",
            "Run 'web-security' for web security audit...",
            "Use 'web-scan' for web scanning...",
            "Check headers with 'web-headers'...",
            "Verify SSL with 'web-ssl'...",
            "Find vulnerabilities with 'web-vuln'...",
            "Type 'web-full' for complete web analysis...",
            "Type 'exit' to close, or 'help' to explore..."
        ]

    def _get_color_palette(self) -> list:
        """Return color palette for placeholder text"""
        return [
            '#ff6b6b', '#ffa94d', '#ffd93d', '#6bcb77', '#4d96ff',
            '#9b59b6', '#ff6b9d', '#00d2d3', '#f368e0', '#ff9ff3',
            '#54a0ff', '#5f27cd', '#01a3a4', '#f8a5c2', '#778beb'
        ]

    def _animate_placeholder(self):
        """Background thread to animate the typing effect with random colors"""
        color_palette = self._get_color_palette()
        
        while self.cursor_running:
            if hasattr(self, 'current_input') and self.current_input:
                with self.placeholder_lock:
                    self.placeholder_text = ""
                    self.placeholder_colors = []
                time.sleep(0.1)
                continue
            
            full_text = random.choice(self._get_placeholder_texts())
            typed_text = ""
            temp_colors = []
            
            for char in full_text:
                if not self.cursor_running:
                    return
                if hasattr(self, 'current_input') and self.current_input:
                    break
                
                typed_text += char
                color = random.choice(color_palette)
                temp_colors.append((char, color))
                
                with self.placeholder_lock:
                    self.placeholder_text = typed_text
                    self.placeholder_colors = temp_colors
                
                if hasattr(self, 'app') and self.app:
                    try:
                        self.app.invalidate()
                    except:
                        pass
                
                delay = random.uniform(0.02, 0.08)
                if char in ['.', ',', '!', '?', ';', ':']:
                    delay *= 2.0
                if random.random() < 0.03:
                    delay += random.uniform(0.1, 0.3)
                if char == ' ':
                    delay *= 0.6
                time.sleep(delay)
            
            if not (hasattr(self, 'current_input') and self.current_input):
                time.sleep(random.uniform(1.0, 2.0))
            
            while len(typed_text) > 0:
                if not self.cursor_running:
                    return
                if hasattr(self, 'current_input') and self.current_input:
                    break
                
                typed_text = typed_text[:-1]
                if temp_colors:
                    temp_colors.pop()
                
                with self.placeholder_lock:
                    self.placeholder_text = typed_text
                    self.placeholder_colors = temp_colors
                
                if hasattr(self, 'app') and self.app:
                    try:
                        self.app.invalidate()
                    except:
                        pass
                time.sleep(random.uniform(0.01, 0.03))
            
            if not (hasattr(self, 'current_input') and self.current_input):
                time.sleep(random.uniform(0.5, 1.0))

    def _get_placeholder_data(self) -> dict:
        """Return current placeholder text and colors"""
        if hasattr(self, 'current_input') and self.current_input:
            return {'text': '', 'colored_chars': []}
        
        with self.placeholder_lock:
            return {
                'text': self.placeholder_text if hasattr(self, 'placeholder_text') else "",
                'colored_chars': self.placeholder_colors if hasattr(self, 'placeholder_colors') else []
            }

    def _get_prompt_siem_dashboard(self) -> HTML:
        """Multi-Line SIEM Dashboard Prompt with live stats"""
        self._update_siem_metrics()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        version = "4.0.0.113"
        cursor_char = self._get_cursor_char()
        cursor_color = self._get_cursor_color()
        
        alert_color = 'ansired' if self.alert_count > 300 else 'ansiyellow' if self.alert_count > 200 else 'ansigreen'
        critical_color = 'ansired' if self.critical_alerts > 20 else 'ansiyellow' if self.critical_alerts > 10 else 'ansigreen'
        high_color = 'ansiyellow' if self.high_alerts > 50 else 'ansigreen'
        incident_color = 'ansired' if self.incident_count > 15 else 'ansiyellow' if self.incident_count > 10 else 'ansigreen'
        risk_color = 'ansired' if self.risk_score > 70 else 'ansiyellow' if self.risk_score > 50 else 'ansigreen'
        
        return HTML(
            f"<ansiwhite>┌─[</ansiwhite>"
            f"<ansiyellow>{timestamp}</ansiyellow>"
            f"<ansiwhite>]</ansiwhite> "
            f"<ansicyan>📊</ansicyan> "
            f"<ansigreen>SIEM=>DSTERMINAL CYBER-OPS</ansigreen> "
            f"<ansiwhite>v{version}</ansiwhite>\n"
            f"<ansiwhite>├─</ansiwhite> "
            f"<ansiyellow>Alerts:</ansiyellow> "
            f"<{alert_color}>{self.alert_count}</{alert_color}> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>Critical:</ansiyellow> "
            f"<{critical_color}>{self.critical_alerts}</{critical_color}> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>High:</ansiyellow> "
            f"<{high_color}>{self.high_alerts}</{high_color}>\n"
            f"<ansiwhite>├─</ansiwhite> "
            f"<ansiyellow>Incidents:</ansiyellow> "
            f"<{incident_color}>{self.incident_count}</{incident_color}> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>MTTR:</ansiyellow> "
            f"<ansigreen>{self.mttr}</ansigreen> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>Risk:</ansiyellow> "
            f"<{risk_color}>{self.risk_score}%</{risk_color}>\n"
            f"<ansiwhite>├─</ansiwhite> "
            f"<ansiyellow>EPS (Events Per Second):</ansiyellow> "
            f"<ansigreen>{self.event_rate}/s</ansigreen> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>Sessions:</ansiyellow> "
            f"<ansicyan>{self.active_sessions}</ansicyan> "
            f"<ansiwhite>│</ansiwhite> "
            f"<ansiyellow>Uptime:</ansiyellow> "
            f"<ansigreen>{self._get_uptime()}</ansigreen>\n"
            f"<ansiwhite>└─</ansiwhite>"
            f"<ansired>❯</ansired> "
            f"<style color='{cursor_color}'>{cursor_char}</style> "
        )

    # ============================================================
    # COMMAND HANDLERS
    # ============================================================

    def handle_command(self, cmd):
        """Handle user commands"""
        cmd = cmd.strip()
        if not cmd:
            return
        
        parts = cmd.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Basic commands
        if command == "help":
            self.show_help()
            return
        elif command == "clear":
            self.clear_screen()
            return
        elif command == "exit":
            print("\n[!] Exiting DSTERMINAL...")
            sys.exit(0)
        elif command == "status":
            self.show_status()
            return
        elif command == "dashboard":
            self.show_dashboard()
            return
        else:
            print(f"[!] Unknown command: {cmd}")
            print("    Type 'help' for available commands")
    
    def show_help(self):
        """Show help menu"""
        print(f"\n{Colors.CYAN}┌─ DSTERMINAL HELP MENU ──────────────────────{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.GREEN}│  help      - Show this help menu{Colors.END}")
        print(f"{Colors.GREEN}│  clear     - Clear the screen{Colors.END}")
        print(f"{Colors.GREEN}│  exit      - Exit DSTERMINAL{Colors.END}")
        print(f"{Colors.GREEN}│  status    - Show system status{Colors.END}")
        print(f"{Colors.GREEN}│  dashboard - Show SIEM dashboard{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}└──────────────────────────────────────────────{Colors.END}")
    
    def show_status(self):
        """Show system status"""
        print(f"\n{Colors.CYAN}┌─ SYSTEM STATUS ─────────────────────────────{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.GREEN}│  Version: 4.0.0.113{Colors.END}")
        print(f"{Colors.GREEN}│  Uptime: {self._get_uptime()}{Colors.END}")
        print(f"{Colors.GREEN}│  Session: {self.session_id}{Colors.END}")
        print(f"{Colors.GREEN}│  Admin: {'Yes' if self.is_admin() else 'No'}{Colors.END}")
        print(f"{Colors.GREEN}│  Workspace: {self.workspace_path}{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}└──────────────────────────────────────────────{Colors.END}")
    
    def show_dashboard(self):
        """Show SIEM dashboard"""
        self._update_siem_metrics()
        print(f"\n{Colors.CYAN}┌─ SIEM DASHBOARD ────────────────────────────{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.YELLOW}│  Alerts: {self.alert_count}{Colors.END}")
        print(f"{Colors.YELLOW}│  Critical: {self.critical_alerts}{Colors.END}")
        print(f"{Colors.YELLOW}│  High: {self.high_alerts}{Colors.END}")
        print(f"{Colors.YELLOW}│  Incidents: {self.incident_count}{Colors.END}")
        print(f"{Colors.YELLOW}│  Risk Score: {self.risk_score}%{Colors.END}")
        print(f"{Colors.YELLOW}│  EPS: {self.event_rate}/s{Colors.END}")
        print(f"{Colors.YELLOW}│  Active Sessions: {self.active_sessions}{Colors.END}")
        print(f"{Colors.YELLOW}│  MTTR: {self.mttr}{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}└──────────────────────────────────────────────{Colors.END}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()
    
    def print_banner(self):
        """Print DSTERMINAL banner"""
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════╗
║         DSTERMINAL Cyber Security Terminal v4.0.0.113      ║
║         Intelligent Placeholder with Rainbow Colors         ║
║         Type 'help' for commands or 'exit' to quit          ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
        """)

    # ============================================================
    # MAIN RUN METHOD
    # ============================================================

    def run(self):
        """Run the terminal with SIEM Dashboard prompt and intelligent placeholder"""
        self.print_banner()
        
        # Initialize placeholder variables
        self.placeholder_text = ""
        self.placeholder_colors = []
        self.placeholder_lock = threading.Lock()
        self.current_input = ""
        
        # Define available commands for autocompletion
        COMMANDS = {
            "help": None,
            "clear": None,
            "exit": None,
            "status": None,
            "dashboard": None,
        }
        
        completer = NestedCompleter.from_nested_dict(COMMANDS)
        
        # Style for the bottom toolbar
        try:
            style = Style([
                ('bottom-toolbar', 'bg:#1a1a2e #33ff33'),
                ('bottom-toolbar.text', '#078507'),
            ])
        except:
            style = None
        
        # Start cursor blink
        self._start_cursor_blink()
        
        # Create placeholder processor
        placeholder_processor = PlaceholderProcessor(self._get_placeholder_data)
        
        # Create the prompt session WITH the placeholder processor
        self.session = PromptSession(
            history=FileHistory('.dst_history'),
            auto_suggest=AutoSuggestFromHistory(),
            completer=completer,
            bottom_toolbar=HTML(
                "<b>DSTerminal</b> v{} | Mode: <style bg='{}'>{}</style>"
            ).format(
                "4.0.0.113",
                "ansired" if self.is_admin() else "ansigreen",
                "ADMIN" if self.is_admin() else "USER",
            ),
            style=style,
            reserve_space_for_menu=0,
            complete_while_typing=True,
            refresh_interval=0.5,
            input_processors=[placeholder_processor],
        )
        
        # Get the application reference
        self.app = self.session.app
        
        # Start the intelligent placeholder animation thread
        placeholder_thread = threading.Thread(target=self._animate_placeholder, daemon=True)
        placeholder_thread.start()
        
        # Watch buffer for changes to detect user typing
        buffer = self.session.default_buffer
        
        def on_text_changed(_):
            """Detect when buffer content changes"""
            text = buffer.text
            
            with self.placeholder_lock:
                if text:
                    self.current_input = text
                    self.placeholder_text = ""
                    self.placeholder_colors = []
                else:
                    self.current_input = ""
            
            if self.app:
                try:
                    self.app.invalidate()
                except:
                    pass
        
        buffer.on_text_changed += on_text_changed
        
        while True:
            try:
                prompt_text = self._get_prompt_siem_dashboard()
                user_input = self.session.prompt(prompt_text)
                
                self.current_input = user_input
                self.log_command(user_input)
                self.log_to_siem(f"Command executed: {user_input}")
                
                if user_input.lower() == "exit":
                    self.save_session_end()
                    print(f"\n{Colors.GREEN}[✓] Session ended. Log saved.{Colors.END}")
                    break
                
                self.handle_command(user_input.strip())
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[!] Use 'exit' to quit or 'help' for commands{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[!] Error: {str(e)}{Colors.END}")
                self.log_to_siem(f"Error: {str(e)}")
            finally:
                with self.placeholder_lock:
                    self.current_input = ""
                    self.placeholder_text = ""
                    self.placeholder_colors = []

# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        terminal = SecurityTerminal()
        terminal.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Terminated by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[!] Fatal error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)