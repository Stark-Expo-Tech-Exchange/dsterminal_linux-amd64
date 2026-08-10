"""
DSTerminal Dashboard Integration Module
Integrates the security dashboard into the main DSTerminal class
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
import threading
import webbrowser
import time
from datetime import datetime

# ============================================================
# SILENCE FLASK, SOCKETIO, AND WERKZEUG LOGS COMPLETELY
# ============================================================
import logging
import contextlib
import io

# Silence standard logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

# Custom context manager to block the "Serving Flask app" and "Debug mode" prints
class SilenceFlaskStartup:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

# ============================================================

# Try to import the dashboard
DASHBOARD_AVAILABLE = False
dashboard_app = None
dashboard_socketio = None

try:
    from dsterminal_complete import app as dashboard_app, socketio as dashboard_socketio
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"[!] Dashboard import error: {e}")

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
            return "[!] Dashboard module not available. Make sure dsterminal_complete.py exists."
            
        if self.is_running:
            return f"[!] Dashboard is already running at {self.dashboard_url}"
            
        def run_dashboard():
            try:
                print("\n" + "=" * 60)
                print("🔮 DSTERMINAL SECURITY DASHBOARD")
                print("=" * 60)
                print(f"📍 Dashboard URL: {self.dashboard_url}")
                print(f"📊 Real-time monitoring active")
                print(f"🔄 Press Ctrl+C in this window to stop")
                print("=" * 60 + "\n")
                
                # SILENTLY START DASHBOARD (No logs printed to terminal)
                with SilenceFlaskStartup():
                    dashboard_socketio.run(dashboard_app, debug=False, host='0.0.0.0', port=self.port, allow_unsafe_werkzeug=True)
                    
            except Exception as e:
                print(f"[!] Dashboard error: {e}")
                
        self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self.dashboard_thread.start()
        self.is_running = True
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        try:
            webbrowser.open(self.dashboard_url)
            return f"[+] Dashboard started at {self.dashboard_url} (opened in browser)"
        except:
            return f"[+] Dashboard started at {self.dashboard_url} (open manually at that URL)"
            
    def stop_dashboard(self):
        """Stop the dashboard"""
        if not self.is_running:
            return "[!] Dashboard is not running"
        
        self.is_running = False
        return "[+] Dashboard stopped (thread terminated)"
        
    def status(self):
        """Get dashboard status"""
        if self.is_running:
            return f"[+] Dashboard is RUNNING at {self.dashboard_url}"
        return "[!] Dashboard is NOT running"
        
    def open_browser(self):
        """Open dashboard in browser"""
        if not self.is_running:
            return "[!] Dashboard is not running. Start it with 'dashboard'"
        try:
            webbrowser.open(self.dashboard_url)
            return f"[+] Opened browser at {self.dashboard_url}"
        except Exception as e:
            return f"[!] Failed to open browser: {e}"
        
    def help(self):
        """Show dashboard commands help"""
        return """
╔═══════════════════════════════════════════════════════════════════╗
║              DSTERMINAL DASHBOARD COMMANDS                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  dashboard           - Start the security dashboard          ║
║  dashboard stop      - Stop the dashboard                    ║
║  dashboard status    - Check dashboard status                ║
║  dashboard browser   - Open dashboard in browser             ║
║  dashboard help      - Show this help                       ║
╚═══════════════════════════════════════════════════════════════════╝
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
        print("[!] Dashboard not available. Commands will not be registered.")
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
    
    print("[+] Dashboard commands registered!")
    return True


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 DSTERMINAL DASHBOARD INTEGRATION TEST")
    print("=" * 60)
    print("Available commands:")
    print("  dashboard        - Start the dashboard")
    print("  dashboard stop   - Stop the dashboard")
    print("  dashboard status - Check status")
    print("  dashboard browser - Open in browser")
    print("  dashboard help   - Show help")
    print("=" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            if cmd == "exit" or cmd == "quit":
                break
            elif cmd == "dashboard":
                print(cmd_dashboard(None))
            elif cmd == "dashboard stop":
                print(cmd_dashboard_stop(None))
            elif cmd == "dashboard status":
                print(cmd_dashboard_status(None))
            elif cmd == "dashboard browser":
                print(cmd_dashboard_browser(None))
            elif cmd == "dashboard help":
                print(cmd_dashboard_help(None))
            else:
                print("Unknown command. Try: dashboard, dashboard stop, dashboard status, dashboard browser, dashboard help")
        except KeyboardInterrupt:
            print("\nExiting...")
            break