# dst_footer.py - DSTERMINAL ENTERPRISE FIXED FOOTER ENGINE

import os
import sys
import time
import shutil
import threading
from datetime import datetime

# ============================================================
# ANSI COLORS FALLBACK
# ============================================================

class FooterColors:
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Bright backgrounds
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_CYAN = '\033[106m'

# ============================================================
# DYNAMIC FOOTER CLASS
# ============================================================

class DSTerminalFooter:
    """
    Fixed sticky footer engine for DSTerminal
    """
    
    def __init__(self, version="v2.1.327", dynamic_bg=True):
        self.version = version
        self.dynamic_bg = dynamic_bg
        
        self.current_module = "IDLE"
        self.current_status = "WAITING"
        self.cpu = 0
        self.ram = 0
        self.mode = "ENTERPRISE HARDENING"
        self.session = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.threat_level = "LOW"
        
        # Color animation state
        self.animation_frame = 0
        
    def update(self, cpu=None, ram=None, module=None, status=None, threat=None):
        """Update live telemetry"""
        if cpu is not None:
            self.cpu = cpu
        if ram is not None:
            self.ram = ram
        if module is not None:
            self.current_module = module
        if status is not None:
            self.current_status = status
        if threat is not None:
            self.threat_level = threat
    
    def terminal_width(self):
        try:
            return shutil.get_terminal_size().columns
        except:
            return 120
    
    def build_footer_text(self):
        width = self.terminal_width()
        
        threat_icon = {
            "LOW": "🟢",
            "MEDIUM": "🟡",
            "HIGH": "🔴",
            "CRITICAL": "💀"
        }.get(self.threat_level, "⚪")
        
        left = f" {threat_icon} DSTerminal {self.version} "
        center = f" 💻CPU:{self.cpu}% | 💾RAM:{self.ram}% | MODULE:{self.current_module[:22]}"
        right = f" STATUS:{self.current_status} | ⚡{self.threat_level} "
        
        total = len(left) + len(center) + len(right)
        remaining = width - total - 4
        
        if remaining < 2:
            remaining = 2
        
        left_pad = remaining // 2
        right_pad = remaining - left_pad
        
        footer = left + (" " * left_pad) + center + (" " * right_pad) + right
        return footer[:width]
    
    def get_dynamic_color(self):
        """Get dynamic background color based on threat level"""
        if self.threat_level == "CRITICAL":
            return FooterColors.BG_BRIGHT_RED + FooterColors.BOLD + FooterColors.WHITE
        elif self.threat_level == "HIGH":
            return FooterColors.BG_RED + FooterColors.BOLD + FooterColors.WHITE
        elif self.threat_level == "MEDIUM":
            return FooterColors.BG_YELLOW + FooterColors.BOLD + FooterColors.BLACK
        elif self.cpu > 85:
            return FooterColors.BG_BRIGHT_RED + FooterColors.BOLD + FooterColors.WHITE
        elif self.cpu > 70:
            return FooterColors.BG_RED + FooterColors.BOLD + FooterColors.WHITE
        elif self.cpu > 50:
            return FooterColors.BG_YELLOW + FooterColors.BOLD + FooterColors.BLACK
        else:
            return FooterColors.BG_GREEN + FooterColors.BOLD + FooterColors.BLACK
    
    def render_ansi_fixed(self):
        """Render fixed footer at bottom of terminal"""
        footer = self.build_footer_text()
        height = shutil.get_terminal_size().lines
        
        # Save cursor
        print("\0337", end="")
        
        # Move to bottom
        print(f"\033[{height};1H", end="")
        
        # Clear line
        print("\033[2K", end="")
        
        # Get dynamic color
        color = self.get_dynamic_color()
        
        # Render footer
        print(color + footer + FooterColors.RESET, end="")
        
        # Restore cursor
        print("\0338", end="")
        sys.stdout.flush()
    
    def render(self):
        """Main render method"""
        self.render_ansi_fixed()


# ============================================================
# FOOTER BOOT ANIMATION
# ============================================================

class FooterBootAnimation:
    @staticmethod
    def show(version="v2.1.327"):
        width = shutil.get_terminal_size().columns
        
        # Animated gradient effect
        colors = [
            FooterColors.BG_GREEN,
            FooterColors.BG_BRIGHT_GREEN,
            FooterColors.BG_CYAN,
            FooterColors.BG_BRIGHT_CYAN,
            FooterColors.BG_GREEN
        ]
        
        title = f" DSTerminal {version} | Enterprise Cyber Defense Matrix "
        
        for color in colors:
            top = "▄" * min(width, 100)
            print(color + top + FooterColors.RESET)
            print(color + FooterColors.BOLD + title.center(min(width, 100)) + FooterColors.RESET)
            print(color + top + FooterColors.RESET)
            time.sleep(0.15)
            print("\033[3A", end="")  # Move up for animation
        
        # Final render
        final_color = FooterColors.BG_BRIGHT_GREEN
        print(final_color + "▄" * min(width, 100) + FooterColors.RESET)
        print(final_color + FooterColors.BOLD + title.center(min(width, 100)) + FooterColors.RESET)
        print(final_color + "▄" * min(width, 100) + FooterColors.RESET)
        print()


# ============================================================
# TELEMETRY ENGINE FOR REAL-TIME METRICS
# ============================================================

class TelemetryEngine:
    """Real-time system telemetry collector"""
    
    def __init__(self, update_interval=1.0):
        self.update_interval = update_interval
        self._running = False
        self._thread = None
        self._cpu = 0
        self._ram = 0
        self._processes = 0
        self._rx_mb = 0
        self._tx_mb = 0
        self._threat_level = "LOW"
        
        # Try to import psutil
        try:
            import psutil
            self.psutil = psutil
            self.psutil_available = True
        except ImportError:
            self.psutil_available = False
        
        # Network tracking
        self._last_net_time = time.time()
        self._last_net_rx = 0
        self._last_net_tx = 0
    
    def start(self):
        """Start telemetry collection thread"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop telemetry collection"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _collect_loop(self):
        """Background collection loop"""
        while self._running:
            self._collect_metrics()
            time.sleep(self.update_interval)
    
    def _collect_metrics(self):
        """Collect system metrics"""
        try:
            if self.psutil_available:
                # CPU
                self._cpu = self.psutil.cpu_percent(interval=0.1)
                
                # RAM
                mem = self.psutil.virtual_memory()
                self._ram = mem.percent
                
                # Processes
                self._processes = len(self.psutil.pids())
                
                # Network rate calculation
                net = self.psutil.net_io_counters()
                current_time = time.time()
                time_delta = current_time - self._last_net_time
                
                if time_delta > 0:
                    self._rx_mb = (net.bytes_recv - self._last_net_rx) / (1024 * 1024) / time_delta
                    self._tx_mb = (net.bytes_sent - self._last_net_tx) / (1024 * 1024) / time_delta
                
                self._last_net_time = current_time
                self._last_net_rx = net.bytes_recv
                self._last_net_tx = net.bytes_sent
                
                # Threat level based on CPU/RAM
                if self._cpu > 85 or self._ram > 90:
                    self._threat_level = "CRITICAL"
                elif self._cpu > 70 or self._ram > 80:
                    self._threat_level = "HIGH"
                elif self._cpu > 50 or self._ram > 60:
                    self._threat_level = "MEDIUM"
                else:
                    self._threat_level = "LOW"
                    
        except Exception as e:
            pass
    
    def get_metrics(self):
        """Get current metrics as dict"""
        return {
            "cpu": self._cpu,
            "ram": self._ram,
            "processes": self._processes,
            "rx_mb": self._rx_mb,
            "tx_mb": self._tx_mb,
            "threat_level": self._threat_level
        }
    
    def get_metrics_dict(self):
        """Alias for get_metrics"""
        return self.get_metrics()


# ============================================================
# DYNAMIC FOOTER WITH TELEMETRY INTEGRATION
# ============================================================

class DynamicFooter(DSTerminalFooter):
    """Extended footer with real-time telemetry integration"""
    
    def __init__(self, version="v3.0.0"):
        super().__init__(version=version)
        self.telemetry = None
        self._telemetry_thread = None
        self._running = False
    
    def start(self):
        """Start footer with telemetry"""
        self._running = True
        self.telemetry = TelemetryEngine(update_interval=0.5)
        self.telemetry.start()
        
        # Start footer render thread
        self._telemetry_thread = threading.Thread(target=self._render_loop, daemon=True)
        self._telemetry_thread.start()
    
    def stop(self):
        """Stop footer rendering"""
        self._running = False
        if self.telemetry:
            self.telemetry.stop()
        if self._telemetry_thread:
            self._telemetry_thread.join(timeout=2)
    
    def _render_loop(self):
        """Background render loop"""
        while self._running:
            if self.telemetry:
                metrics = self.telemetry.get_metrics()
                self.update(
                    cpu=metrics.get('cpu', 0),
                    ram=metrics.get('ram', 0),
                    threat=metrics.get('threat_level', 'LOW'),
                    processes=metrics.get('processes', 0)
                )
            self.render_ansi_fixed()
            time.sleep(0.5)
    
    def update_metrics(self, cpu=None, ram=None, threat=None, rx=None, tx=None, processes=None):
        """Update telemetry metrics"""
        if cpu is not None:
            self.cpu = cpu
        if ram is not None:
            self.ram = ram
        if threat is not None:
            self.threat_level = threat
        if processes is not None:
            self.processes = processes
    
    def render(self):
        """Render footer with telemetry data"""
        if self.telemetry:
            metrics = self.telemetry.get_metrics()
            self.update(
                cpu=metrics.get('cpu', self.cpu),
                ram=metrics.get('ram', self.ram),
                threat=metrics.get('threat_level', self.threat_level)
            )
        self.render_ansi_fixed()


# ============================================================
# STANDALONE TEST MODE
# ============================================================

if __name__ == "__main__":
    footer = DSTerminalFooter()
    
    try:
        print("Testing DSTerminal Footer...")
        print("Press Ctrl+C to exit\n")
        
        while True:
            footer.update(
                cpu=25,
                ram=47,
                module="Firewall Hardening",
                status="RUNNING",
                threat="LOW"
            )
            footer.render_ansi_fixed()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nFooter test complete.")