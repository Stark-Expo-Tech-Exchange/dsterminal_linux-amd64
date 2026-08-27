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

DSTerminal Dashboard Integration Module
Integrates the security dashboard into the main DSTerminal class
"""
import sys
import os
import threading
import webbrowser
import time
import re
from datetime import datetime

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
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    DIM = '\033[2m'
    BRIGHT = '\033[1m'
    LIGHTRED_EX = '\033[91m'
    LIGHTGREEN_EX = '\033[92m'
    LIGHTYELLOW_EX = '\033[93m'
    LIGHTCYAN_EX = '\033[96m'
    LIGHTMAGENTA_EX = '\033[95m'
    LIGHTBLUE_EX = '\033[94m'
    LIGHTWHITE_EX = '\033[97m'
    
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
    Back = type('Back', (), {
        'RESET': '\033[49m',
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m'
    })
except Exception as e:
    COLORS_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
    Back = type('Back', (), {
        'RESET': '\033[49m',
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m'
    })

# ============================================================
# SIMPLE SAFE PRINT FUNCTION
# ============================================================
def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(clean_message)
    except Exception:
        try:
            print(str(message))
        except:
            pass

# ============================================================
# SILENCE FLASK, SOCKETIO, AND WERKZEUG LOGS COMPLETELY
# ============================================================
import logging
import contextlib
import io as io_lib

# Silence standard logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

# Custom context manager to block the "Serving Flask app" and "Debug mode" prints
class SilenceFlaskStartup:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = io_lib.StringIO()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

# ============================================================
# TRY TO IMPORT THE DASHBOARD
# ============================================================
DASHBOARD_AVAILABLE = False
dashboard_app = None
dashboard_socketio = None

try:
    from dsterminal_complete import app as dashboard_app, socketio as dashboard_socketio
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    # Silent import - don't print errors during import
    pass
except Exception as e:
    # Silent import - don't print errors during import
    pass

# ============================================================
# DASHBOARD INTEGRATION CLASS
# ============================================================

class DashboardIntegration:
    """
    Dashboard integration handler for DSTerminal
    Provides commands to start, stop, and manage the dashboard
    """
    
    def __init__(self):
        self.dashboard_thread = None
        self.is_running = False
        self.dashboard_url = "http://localhost:5000"
        self.port = 5000
        self.dashboard_available = DASHBOARD_AVAILABLE
        
    def start_dashboard(self):
        """Start the Flask dashboard in a background thread"""
        if not self.dashboard_available:
            return f"{Fore.RED}[!] Dashboard module not available. Make sure dsterminal_complete.py exists.{Fore.RESET}"
            
        if self.is_running:
            return f"{Fore.YELLOW}[!] Dashboard is already running at {self.dashboard_url}{Fore.RESET}"
            
        def run_dashboard():
            try:
                safe_print_unicode("\n" + "=" * 60)
                safe_print_unicode(f"{Fore.CYAN}🔮 DSTERMINAL SECURITY DASHBOARD{Fore.RESET}")
                safe_print_unicode("=" * 60)
                safe_print_unicode(f"{Fore.GREEN}📍 Dashboard URL: {self.dashboard_url}{Fore.RESET}")
                safe_print_unicode(f"{Fore.CYAN}📊 Real-time monitoring active{Fore.RESET}")
                safe_print_unicode(f"{Fore.YELLOW}🔄 Press Ctrl+C in this window to stop{Fore.RESET}")
                safe_print_unicode("=" * 60 + "\n")
                
                # SILENTLY START DASHBOARD (No logs printed to terminal)
                with SilenceFlaskStartup():
                    if dashboard_socketio is not None:
                        dashboard_socketio.run(dashboard_app, debug=False, host='0.0.0.0', port=self.port, allow_unsafe_werkzeug=True)
                    else:
                        # Fallback: run without socketio
                        dashboard_app.run(debug=False, host='0.0.0.0', port=self.port)
                    
            except Exception as e:
                safe_print_unicode(f"{Fore.RED}[!] Dashboard error: {e}{Fore.RESET}")
                
        self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self.dashboard_thread.start()
        self.is_running = True
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        try:
            webbrowser.open(self.dashboard_url)
            return f"{Fore.GREEN}[+] Dashboard started at {self.dashboard_url} (opened in browser){Fore.RESET}"
        except:
            return f"{Fore.GREEN}[+] Dashboard started at {self.dashboard_url} (open manually at that URL){Fore.RESET}"
            
    def stop_dashboard(self):
        """Stop the dashboard"""
        if not self.is_running:
            return f"{Fore.YELLOW}[!] Dashboard is not running{Fore.RESET}"
        
        self.is_running = False
        # Note: The thread will continue running until the server stops
        # This is a limitation of Flask's built-in server
        return f"{Fore.GREEN}[+] Dashboard stop requested (server will terminate when thread ends){Fore.RESET}"
        
    def status(self):
        """Get dashboard status"""
        if self.is_running:
            return f"{Fore.GREEN}[+] Dashboard is RUNNING at {self.dashboard_url}{Fore.RESET}"
        return f"{Fore.RED}[!] Dashboard is NOT running{Fore.RESET}"
        
    def open_browser(self):
        """Open dashboard in browser"""
        if not self.is_running:
            return f"{Fore.RED}[!] Dashboard is not running. Start it with 'dashboard'{Fore.RESET}"
        try:
            webbrowser.open(self.dashboard_url)
            return f"{Fore.GREEN}[+] Opened browser at {self.dashboard_url}{Fore.RESET}"
        except Exception as e:
            return f"{Fore.RED}[!] Failed to open browser: {e}{Fore.RESET}"
        
    def help(self):
        """Show dashboard commands help"""
        return f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════╗
║              DSTERMINAL DASHBOARD COMMANDS                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  {Fore.GREEN}dashboard{Fore.CYAN}           - Start the security dashboard          ║
║  {Fore.GREEN}dashboard stop{Fore.CYAN}      - Stop the dashboard                    ║
║  {Fore.GREEN}dashboard status{Fore.CYAN}    - Check dashboard status                ║
║  {Fore.GREEN}dashboard browser{Fore.CYAN}   - Open dashboard in browser             ║
║  {Fore.GREEN}dashboard help{Fore.CYAN}      - Show this help                       ║
╚═══════════════════════════════════════════════════════════════════╝{Fore.RESET}
"""

# Create singleton instance
dashboard_integration = DashboardIntegration()


# ============================================================
# COMMAND FUNCTIONS FOR DSTERMINAL
# ============================================================

def cmd_dashboard(args):
    """Start the security dashboard"""
    return dashboard_integration.start_dashboard()

def cmd_dashboard_stop(args):
    """Stop the security dashboard"""
    return dashboard_integration.stop_dashboard()

def cmd_dashboard_status(args):
    """Show dashboard status"""
    return dashboard_integration.status()

def cmd_dashboard_browser(args):
    """Open dashboard in browser"""
    return dashboard_integration.open_browser()

def cmd_dashboard_help(args):
    """Show dashboard help"""
    return dashboard_integration.help()


# ============================================================
# REGISTER COMMANDS - Function to be called from dsterminal.py
# ============================================================

def register_dashboard_commands(terminal_instance):
    """
    Register dashboard commands with the DSTerminal instance
    Call this from your SecurityTerminal __init__ or register_commands method
    """
    if not DASHBOARD_AVAILABLE:
        safe_print_unicode(f"{Fore.RED}[!] Dashboard not available. Commands will not be registered.{Fore.RESET}")
        return False
    
    # Register commands
    terminal_instance.commands['dashboard'] = cmd_dashboard
    terminal_instance.commands['dashboard stop'] = cmd_dashboard_stop
    terminal_instance.commands['dashboard status'] = cmd_dashboard_status
    terminal_instance.commands['dashboard browser'] = cmd_dashboard_browser
    terminal_instance.commands['dashboard help'] = cmd_dashboard_help
    
    # Also add shortcuts
    terminal_instance.commands['dash'] = cmd_dashboard
    terminal_instance.commands['dash-stop'] = cmd_dashboard_stop
    terminal_instance.commands['dash-status'] = cmd_dashboard_status
    
    safe_print_unicode(f"{Fore.GREEN}[+] Dashboard commands registered!{Fore.RESET}")
    return True


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    safe_print_unicode("=" * 60)
    safe_print_unicode(f"{Fore.CYAN}🧪 DSTERMINAL DASHBOARD INTEGRATION TEST{Fore.RESET}")
    safe_print_unicode("=" * 60)
    safe_print_unicode(f"{Fore.YELLOW}Available commands:{Fore.RESET}")
    safe_print_unicode(f"  {Fore.GREEN}dashboard{Fore.RESET}        - Start the dashboard")
    safe_print_unicode(f"  {Fore.GREEN}dashboard stop{Fore.RESET}   - Stop the dashboard")
    safe_print_unicode(f"  {Fore.GREEN}dashboard status{Fore.RESET} - Check status")
    safe_print_unicode(f"  {Fore.GREEN}dashboard browser{Fore.RESET} - Open in browser")
    safe_print_unicode(f"  {Fore.GREEN}dashboard help{Fore.RESET}   - Show help")
    safe_print_unicode("=" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            if cmd == "exit" or cmd == "quit":
                break
            elif cmd == "dashboard":
                safe_print_unicode(cmd_dashboard(None))
            elif cmd == "dashboard stop":
                safe_print_unicode(cmd_dashboard_stop(None))
            elif cmd == "dashboard status":
                safe_print_unicode(cmd_dashboard_status(None))
            elif cmd == "dashboard browser":
                safe_print_unicode(cmd_dashboard_browser(None))
            elif cmd == "dashboard help":
                safe_print_unicode(cmd_dashboard_help(None))
            else:
                safe_print_unicode(f"{Fore.YELLOW}Unknown command. Try: dashboard, dashboard stop, dashboard status, dashboard browser, dashboard help{Fore.RESET}")
        except KeyboardInterrupt:
            safe_print_unicode(f"\n{Fore.YELLOW}Exiting...{Fore.RESET}")
            break
        except Exception as e:
            safe_print_unicode(f"{Fore.RED}[!] Error: {e}{Fore.RESET}")