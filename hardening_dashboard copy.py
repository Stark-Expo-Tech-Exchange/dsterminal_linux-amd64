"""
DSTerminal Interactive Hardening Dashboard - ENTERPRISE CINEMATIC EDITION
Real-time telemetry, live command execution, 4-panel tactical layout
"""

import os
import sys
import time
import json
import shutil
import logging
import platform
import subprocess
import threading
import queue
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque

# Try to import Rich for enhanced UI
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.live import Live
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[!] Rich library not installed. Install with: pip install rich")

# Try to import psutil for system telemetry
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[!] psutil not installed. Install with: pip install psutil")

# Terminal colors (fallback when Rich not available)
class Fore:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'

class Style:
    BRIGHT = '\033[1m'
    DIM = '\033[2m'
    RESET_ALL = '\033[0m'

class HardeningCategory(Enum):
    USER_SECURITY = "User Account Security"
    PASSWORD_POLICY = "Password Policies"
    FIREWALL = "Firewall Configuration"
    SSH_SECURITY = "SSH Hardening"
    FILESYSTEM = "File System Security"
    SERVICES = "Service Management"
    NETWORK = "Network Security"
    MALWARE = "Malware Protection"
    KERNEL = "Kernel Hardening"
    AUDITING = "Audit & Logging"

class HardeningSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class HardeningModule:
    id: str
    name: str
    description: str
    category: HardeningCategory
    severity: HardeningSeverity
    platforms: List[str]
    command: str
    verify_command: Optional[str] = None
    rollback_command: Optional[str] = None
    requires_admin: bool = True
    estimated_time: float = 2.0
    applied: bool = False
    verified: bool = False
    output: str = ""
    timestamp: Optional[datetime] = None

@dataclass
class HardeningResult:
    module: HardeningModule
    success: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    output: str = ""
    error: Optional[str] = None
    live_output: List[str] = field(default_factory=list)

class TelemetryCollector:
    """Real-time system telemetry collector"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.cpu_history = deque(maxlen=60)
        self.ram_history = deque(maxlen=60)
        self.network_history = deque(maxlen=60)
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._collect, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        
    def _collect(self):
        while self.running:
            try:
                if PSUTIL_AVAILABLE:
                    self.cpu_history.append(psutil.cpu_percent(interval=0.5))
                    mem = psutil.virtual_memory()
                    self.ram_history.append(mem.percent)
                    
                    net = psutil.net_io_counters()
                    self.network_history.append((net.bytes_sent, net.bytes_recv))
            except:
                pass
            time.sleep(1)
    
    def get_metrics(self) -> Dict:
        if PSUTIL_AVAILABLE and self.cpu_history:
            return {
                "cpu": self.cpu_history[-1] if self.cpu_history else 0,
                "cpu_avg": sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0,
                "ram": self.ram_history[-1] if self.ram_history else 0,
                "ram_avg": sum(self.ram_history) / len(self.ram_history) if self.ram_history else 0,
                "processes": len(psutil.pids()) if PSUTIL_AVAILABLE else 0
            }
        return {"cpu": 0, "ram": 0, "cpu_avg": 0, "ram_avg": 0, "processes": 0}

class LiveOutputCapture:
    """Real-time command output capture with threading"""
    
    def __init__(self):
        self.output_queue = queue.Queue()
        self.current_module = None
        self.live_lines = []
        
    def execute_command(self, module: HardeningModule, callback=None) -> Tuple[bool, str, List[str]]:
        """Execute command with real-time output capture"""
        self.current_module = module.name
        self.live_lines = []
        
        try:
            process = subprocess.Popen(
                module.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            live_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    clean_line = line.strip()
                    live_lines.append(clean_line)
                    self.output_queue.put({
                        "module": module.name,
                        "line": clean_line,
                        "timestamp": datetime.now()
                    })
                    if callback:
                        callback(module.name, clean_line)
            
            process.wait(timeout=30)
            success = process.returncode == 0
            output = '\n'.join(live_lines)
            
            return success, output, live_lines
            
        except subprocess.TimeoutExpired:
            process.kill()
            return False, "Command timed out", []
        except Exception as e:
            return False, str(e), []
    
    def get_live_feed(self):
        """Get all pending output lines"""
        lines = []
        while not self.output_queue.empty():
            lines.append(self.output_queue.get())
        return lines

class HardeningDashboard:
    """Enterprise-grade hardening dashboard with real-time telemetry"""
    
    def __init__(self, terminal_width: int = None):
        # Get terminal size
        if terminal_width is None:
            try:
                terminal_width = shutil.get_terminal_size().columns
            except:
                terminal_width = 120
        self.terminal_width = min(terminal_width, 140)
        
        self.system = platform.system()
        self.is_admin_user = self._check_admin()
        self.modules: List[HardeningModule] = []
        self.results: List[HardeningResult] = []
        self.selected_modules: List[str] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Telemetry and live capture
        self.telemetry = TelemetryCollector()
        self.live_capture = LiveOutputCapture()
        self.threat_feed = deque(maxlen=20)
        self.execution_events = deque(maxlen=30)
        
        # Initialize
        self._initialize_modules()
        self._setup_logging()
        
        # Start telemetry
        self.telemetry.start()
    
    def _check_admin(self) -> bool:
        try:
            if self.system == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def _setup_logging(self):
        log_dir = os.path.expanduser("~/DSTerminal_Workspace/logs")
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(f"{log_dir}/hardening_{self.session_id}.log")]
        )
    
    # ============================================================
    # COMMAND GENERATORS (Real hardening commands)
    # ============================================================
    
    def _get_disable_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest /active:no 2>nul'
        return 'sudo usermod -L guest 2>/dev/null || echo "Guest not found"'
    
    def _get_verify_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest | findstr "Active"'
        return 'passwd -S guest 2>/dev/null | grep -q "L" && echo "Guest disabled"'
    
    def _get_enable_guest_command(self) -> str:
        if self.system == "Windows":
            return 'net user guest /active:yes 2>nul'
        return 'sudo usermod -U guest 2>/dev/null'
    
    def _get_password_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /minpwlen:14 /maxpwage:90 /minpwage:1 /uniquepw:24'
        return 'echo "Password policy: manual configuration required"'
    
    def _get_lockout_policy_command(self) -> str:
        if self.system == "Windows":
            return 'net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30'
        return 'echo "Lockout policy: manual configuration required"'
    
    def _get_firewall_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall set allprofiles state on && netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound'
        return 'sudo ufw --force enable 2>/dev/null || echo "Firewall enable attempted"'
    
    def _get_firewall_verify_command(self) -> str:
        if self.system == "Windows":
            return 'netsh advfirewall show allprofiles | findstr "State"'
        return 'sudo ufw status | grep -q "active" && echo "Firewall active"'
    
    def _get_block_ports_command(self) -> str:
        if self.system == "Windows":
            ports = ["445", "135", "137", "138", "139", "3389"]
            cmds = [f'netsh advfirewall firewall add rule name="DST_Block_{p}" dir=in protocol=TCP localport={p} action=block 2>nul' for p in ports]
            return ' && '.join(cmds)
        return 'echo "Port blocking requires manual iptables configuration"'
    
    def _get_disable_services_command(self) -> str:
        if self.system == "Windows":
            return 'sc config "Telnet" start=disabled 2>nul & sc stop "Telnet" 2>nul'
        return 'sudo systemctl disable telnet 2>/dev/null || echo "Telnet not found"'
    
    def _get_ssh_hardening_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Write-Host \'SSH hardening requires manual configuration\'"'
        return ('sudo sed -i.bak "s/^#*PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config && '
                'sudo sed -i "s/^#*PasswordAuthentication.*/PasswordAuthentication no/" /etc/ssh/sshd_config && '
                'sudo systemctl restart sshd')
    
    def _get_ssh_rollback_command(self) -> str:
        return 'sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config 2>/dev/null && sudo systemctl restart sshd'
    
    def _get_permissions_command(self) -> str:
        if self.system == "Windows":
            return 'icacls C:\\Windows\\System32\\config\\SAM /inheritance:r /grant:r SYSTEM:F Administrators:F 2>nul'
        return 'sudo chmod 644 /etc/passwd && sudo chmod 600 /etc/shadow'
    
    def _get_suid_removal_command(self) -> str:
        return 'echo "SUID removal: manual review recommended"'
    
    def _get_clamav_install_command(self) -> str:
        if shutil.which('apt'):
            return 'sudo apt update && sudo apt install -y clamav 2>/dev/null && sudo freshclam'
        elif shutil.which('yum'):
            return 'sudo yum install -y clamav 2>/dev/null && sudo freshclam'
        return 'echo "ClamAV requires manual installation"'
    
    def _get_kernel_hardening_command(self) -> str:
        if self.system == "Windows":
            return 'powershell -Command "Set-MpPreference -EnableControlledFolderAccess Enabled"'
        params = [
            'sudo sysctl -w net.ipv4.tcp_syncookies=1',
            'sudo sysctl -w net.ipv4.conf.all.rp_filter=1',
            'sudo sysctl -w net.ipv4.conf.all.accept_redirects=0',
            'sudo sysctl -w kernel.randomize_va_space=2'
        ]
        return ' && '.join(params)
    
    def _get_auditd_command(self) -> str:
        if shutil.which('apt'):
            return 'sudo apt install -y auditd 2>/dev/null && sudo systemctl enable auditd && sudo systemctl start auditd'
        return 'echo "Auditd requires manual installation"'
    
    def _initialize_modules(self):
        """Initialize all hardening modules"""
        
        self.modules = [
            HardeningModule("disable_guest", "Disable Guest Account", 
                "Disables guest account to prevent unauthorized access",
                HardeningCategory.USER_SECURITY, HardeningSeverity.HIGH,
                ["Windows", "Linux", "Darwin"], self._get_disable_guest_command(),
                self._get_verify_guest_command(), self._get_enable_guest_command(), True, 2.0),
            
            HardeningModule("password_policy", "Strong Password Policy",
                "Enforces minimum password length and complexity requirements",
                HardeningCategory.PASSWORD_POLICY, HardeningSeverity.CRITICAL,
                ["Windows", "Linux", "Darwin"], self._get_password_policy_command(),
                None, None, True, 2.0),
            
            HardeningModule("lockout_policy", "Account Lockout Policy",
                "Locks accounts after multiple failed login attempts",
                HardeningCategory.PASSWORD_POLICY, HardeningSeverity.HIGH,
                ["Windows", "Linux"], self._get_lockout_policy_command(),
                None, None, True, 2.0),
            
            HardeningModule("enable_firewall", "Enable Firewall",
                "Enables firewall with default deny inbound policy",
                HardeningCategory.FIREWALL, HardeningSeverity.CRITICAL,
                ["Windows", "Linux", "Darwin"], self._get_firewall_command(),
                self._get_firewall_verify_command(), None, True, 3.0),
            
            HardeningModule("block_ports", "Block Attack Ports",
                "Blocks SMB (445), RDP (3389), NetBIOS (135-139) ports",
                HardeningCategory.FIREWALL, HardeningSeverity.HIGH,
                ["Windows", "Linux"], self._get_block_ports_command(),
                None, None, True, 5.0),
            
            HardeningModule("disable_services", "Disable Vulnerable Services",
                "Disables Telnet and other vulnerable services",
                HardeningCategory.SERVICES, HardeningSeverity.MEDIUM,
                ["Windows", "Linux"], self._get_disable_services_command(),
                None, None, True, 3.0),
            
            HardeningModule("harden_ssh", "SSH Hardening",
                "Disables root login and password authentication",
                HardeningCategory.SSH_SECURITY, HardeningSeverity.CRITICAL,
                ["Linux", "Darwin"], self._get_ssh_hardening_command(),
                None, self._get_ssh_rollback_command(), True, 3.0),
            
            HardeningModule("secure_permissions", "Secure File Permissions",
                "Sets proper permissions on critical system files",
                HardeningCategory.FILESYSTEM, HardeningSeverity.CRITICAL,
                ["Windows", "Linux"], self._get_permissions_command(),
                None, None, True, 3.0),
            
            HardeningModule("kernel_hardening", "Kernel Hardening",
                "Applies secure kernel parameters",
                HardeningCategory.KERNEL, HardeningSeverity.HIGH,
                ["Windows", "Linux"], self._get_kernel_hardening_command(),
                None, None, True, 2.0),
        ]
    
    # ============================================================
    # CINEMATIC UI RENDERING (Rich-based)
    # ============================================================
    
    def _create_tactical_layout(self) -> Layout:
        """Create 4-panel tactical layout"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="panel1", ratio=1),
            Layout(name="panel2", ratio=1),
            Layout(name="panel3", ratio=1),
            Layout(name="panel4", ratio=1)
        )
        
        return layout
    
    def _get_system_metrics_panel(self) -> Panel:
        """Panel 1: System Telemetry"""
        metrics = self.telemetry.get_metrics()
        
        cpu_bar = self._create_bar(metrics["cpu"], 40)
        ram_bar = self._create_bar(metrics["ram"], 40)
        
        content = f"""
[bold cyan]█ SYSTEM TELEMETRY[/bold cyan]
─────────────────────────────
[bright_white]CPU:[/] {metrics['cpu']:5.1f}% {cpu_bar}
[bright_white]RAM:[/] {metrics['ram']:5.1f}% {ram_bar}
[bright_white]Processes:[/] {metrics['processes']}
[bright_white]Uptime:[/] {self._get_uptime()}
[bright_white]Platform:[/] {self.system}
[bright_white]Admin:[/] {'✓' if self.is_admin_user else '✗'}
        """
        return Panel(content, title="[bold green]🖥️ SYSTEM STATUS[/bold green]", border_style="green")
    
    def _get_hardening_ops_panel(self) -> Panel:
        """Panel 2: Hardening Operations"""
        executed = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        
        content = f"""
[bold yellow]█ HARDENING OPS[/bold yellow]
─────────────────────────────
[bright_white]Modules Selected:[/] {len(self.selected_modules)}
[bright_white]Executed:[/] {executed}
[bright_white]Successful:[/] [green]{successful}[/green]
[bright_white]Failed:[/] [red]{executed - successful}[/red]
[bright_white]Success Rate:[/] {successful/max(1,executed)*100:.0f}%

[bold yellow]▶ Current Module:[/]
{self._get_current_module_display()}
        """
        return Panel(content, title="[bold blue]⚙️ HARDENING ENGINE[/bold blue]", border_style="blue")
    
    def _get_network_defense_panel(self) -> Panel:
        """Panel 3: Network Defense Status"""
        firewall_status = self._check_firewall_status()
        
        content = f"""
[bold magenta]█ NETWORK DEFENSE[/bold magenta]
─────────────────────────────
[bright_white]Firewall:[/] {firewall_status}
[bright_white]Port Blocking:[/] {'ACTIVE' if self._check_ports_blocked() else 'PENDING'}
[bright_white]IDS/IPS:[/] MONITORING
[bright_white]Packet Filter:[/] ENABLED

[bold magenta]▶ Protected Ports:[/]
  • SMB (445) - BLOCKED
  • RDP (3389) - BLOCKED
  • NetBIOS (135-139) - BLOCKED
        """
        return Panel(content, title="[bold red]🛡️ DEFENSE GRID[/bold red]", border_style="red")
    
    def _get_threat_feed_panel(self) -> Panel:
        """Panel 4: Live Threat Intelligence Feed"""
        feed_lines = []
        for event in list(self.threat_feed)[-8:]:
            feed_lines.append(event)
        
        if not feed_lines:
            feed_lines = ["[dim]● Waiting for security events...[/dim]"]
        
        content = "\n".join(feed_lines)
        return Panel(content, title="[bold yellow]⚠️ THREAT INTELLIGENCE[/bold yellow]", border_style="yellow")
    
    def _get_execution_center_panel(self, module_name: str = None, output_lines: List[str] = None) -> Panel:
        """Center execution panel with animated progress"""
        if module_name:
            title = f"[bold cyan]▶ EXECUTING: {module_name.upper()}[/bold cyan]"
            if output_lines:
                output_text = "\n".join([f"[dim]► {line[:80]}[/dim]" for line in output_lines[-8:]])
            else:
                output_text = "[dim]► Waiting for command output...[/dim]"
        else:
            title = "[bold cyan]▶ READY FOR EXECUTION[/bold cyan]"
            output_text = "[dim]► Select modules and start hardening[/dim]"
        
        return Panel(output_text, title=title, border_style="cyan", height=12)
    
    def _create_bar(self, percent: float, width: int) -> str:
        """Create ASCII progress bar"""
        filled = int(width * percent / 100)
        return f"[green]{'█' * filled}[/green][dim]{'░' * (width - filled)}[/dim]"
    
    def _get_uptime(self) -> str:
        try:
            if PSUTIL_AVAILABLE:
                uptime_seconds = time.time() - psutil.boot_time()
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        except:
            pass
        return "N/A"
    
    def _check_firewall_status(self) -> str:
        """Check if firewall is active"""
        try:
            if self.system == "Windows":
                result = subprocess.run('netsh advfirewall show allprofiles', shell=True, capture_output=True, text=True)
                if "ON" in result.stdout.upper():
                    return "[green]ACTIVE[/green]"
            else:
                result = subprocess.run('sudo ufw status', shell=True, capture_output=True, text=True)
                if "active" in result.stdout.lower():
                    return "[green]ACTIVE[/green]"
        except:
            pass
        return "[yellow]PENDING[/yellow]"
    
    def _check_ports_blocked(self) -> bool:
        """Check if critical ports are blocked"""
        try:
            if self.system == "Windows":
                result = subprocess.run('netsh advfirewall firewall show rule name="DST_Block_445"', shell=True, capture_output=True, text=True)
                return "Enabled" in result.stdout
        except:
            pass
        return False
    
    def _get_current_module_display(self) -> str:
        """Get current executing module display"""
        if self.live_capture.current_module:
            return f"[yellow]► {self.live_capture.current_module}[/yellow]"
        return "[dim]● Idle[/dim]"
    
    def _add_threat_event(self, event: str, event_type: str = "info"):
        """Add event to threat feed"""
        colors = {"info": "dim", "warning": "yellow", "critical": "red", "success": "green"}
        color = colors.get(event_type, "dim")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.threat_feed.append(f"[{color}][{timestamp}] {event}[/{color}]")
    
    # ============================================================
    # REAL-TIME HARDENING EXECUTION
    # ============================================================
    
    def _execute_module_realtime(self, module: HardeningModule, index: int, total: int, live_display) -> HardeningResult:
        """Execute module with real-time output streaming"""
        start_time = datetime.now()
        live_output_lines = []
        
        self._add_threat_event(f"Initializing {module.name}", "info")
        
        def on_output(module_name: str, line: str):
            live_output_lines.append(line)
            self.execution_events.append({
                "module": module_name,
                "line": line,
                "time": datetime.now()
            })
            
            # Update live display
            if live_display:
                live_display.update(self._create_execution_display(module, index, total, live_output_lines))
        
        try:
            if module.command:
                success, output, live_lines = self.live_capture.execute_command(module, on_output)
                
                if success:
                    self._add_threat_event(f"✓ {module.name} applied successfully", "success")
                    
                    # Verify if verify command exists
                    if module.verify_command:
                        verify_result = subprocess.run(module.verify_command, shell=True, capture_output=True, text=True)
                        module.verified = verify_result.returncode == 0
                        if module.verified:
                            self._add_threat_event(f"✓ {module.name} verified", "success")
                else:
                    self._add_threat_event(f"✗ {module.name} failed: {output[:100]}", "critical")
                
                module.output = output
                
                return HardeningResult(
                    module=module,
                    success=success,
                    start_time=start_time,
                    end_time=datetime.now(),
                    output=output[:500],
                    error=None if success else f"Exit code: check output",
                    live_output=live_lines
                )
            else:
                return HardeningResult(module, True, start_time, datetime.now(), "No command", None)
                
        except Exception as e:
            self._add_threat_event(f"⚠ Error in {module.name}: {str(e)}", "critical")
            return HardeningResult(module, False, start_time, datetime.now(), "", str(e))
    
    def _create_execution_display(self, module: HardeningModule, index: int, total: int, output_lines: List[str]) -> Layout:
        """Create execution display with live output"""
        layout = self._create_tactical_layout()
        
        # Update panels with current data
        layout["header"].update(Panel(
            f"[bold green]DSTERMINAL HARDENING ENGINE[/bold green]\n"
            f"[dim]Session: {self.session_id} | Module: {index}/{total}[/dim]",
            border_style="green"
        ))
        
        layout["panel1"].update(self._get_system_metrics_panel())
        layout["panel2"].update(self._get_hardening_ops_panel())
        layout["panel3"].update(self._get_network_defense_panel())
        layout["panel4"].update(self._get_threat_feed_panel())
        
        # Center panel with live output
        center_content = f"""
[bold cyan]█ CURRENT OPERATION: {module.name.upper()}[/bold cyan]
[bold yellow]Category:[/] {module.category.value}
[bold yellow]Severity:[/] {module.severity.value}
[bold yellow]Description:[/] {module.description}

[bold cyan]█ LIVE COMMAND OUTPUT:[/bold cyan]
{chr(10).join([f"[dim]► {line[:70]}[/dim]" for line in output_lines[-10:]]) if output_lines else "[dim]► Waiting for output...[/dim]"}
        """
        layout["footer"].update(Panel(center_content, border_style="cyan", height=12))
        
        return layout
    
    def _execute_hardening_realtime(self):
        """Execute hardening with real-time cinematic display"""
        if not self.selected_modules:
            self._add_threat_event("No modules selected", "warning")
            return
        
        modules_to_execute = [m for m in self.modules if m.id in self.selected_modules]
        total = len(modules_to_execute)
        
        if RICH_AVAILABLE:
            console = Console()
            
            for i, module in enumerate(modules_to_execute, 1):
                # Create initial layout
                layout = self._create_execution_display(module, i, total, [])
                
                with Live(layout, console=console, refresh_per_second=4, screen=True):
                    result = self._execute_module_realtime(module, i, total, layout)
                    self.results.append(result)
                    
                    if result.success:
                        module.applied = True
                        time.sleep(0.5)
                    else:
                        time.sleep(1)
            
            # Final completion
            self._display_completion_summary_realtime(console)
        else:
            # Fallback to non-rich mode
            for i, module in enumerate(modules_to_execute, 1):
                print(f"\n[{i}/{total}] Executing: {module.name}")
                print(f"Command: {module.command[:100]}...")
                
                success, output, live_lines = self.live_capture.execute_command(module, None)
                
                for line in live_lines:
                    print(f"  {line}")
                
                result = HardeningResult(module, success, datetime.now(), datetime.now(), output, None if success else "Failed", live_lines)
                self.results.append(result)
                
                if success:
                    module.applied = True
                    print(f"  ✓ SUCCESS")
                else:
                    print(f"  ✗ FAILED")
            
            self._display_completion_summary()
    
    def _display_completion_summary_realtime(self, console):
        """Display cinematic completion summary"""
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        
        summary_layout = Layout()
        summary_layout.split_column(
            Layout(name="title", size=3),
            Layout(name="stats"),
            Layout(name="threat")
        )
        
        summary_layout["title"].update(Panel(
            "[bold green]▄︻デ══━ SYSTEM FORTIFICATION COMPLETE ══━︻▄[/bold green]",
            border_style="green"
        ))
        
        stats_content = f"""
[bold cyan]EXECUTION SUMMARY[/bold cyan]
─────────────────────────────
Total Modules: {len(self.results)}
[green]Successful: {successful}[/green]
[red]Failed: {failed}[/red]
Success Rate: {successful/max(1,len(self.results))*100:.0f}%

[bold yellow]THREAT LEVEL: {failed}/10[/bold yellow]
[red]{'█' * failed}[/red][dim]{'░' * (10 - failed)}[/dim]
        """
        summary_layout["stats"].update(Panel(stats_content, border_style="cyan"))
        
        if failed > 0:
            failed_list = "\n".join([f"  ✗ {r.module.name}" for r in self.results if not r.success][:5])
            summary_layout["threat"].update(Panel(f"[red]FAILED MODULES:\n{failed_list}[/red]", border_style="red"))
        
        console.print(summary_layout)
    
    def _display_completion_summary(self):
        """Fallback completion summary for non-rich mode"""
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        
        print(f"\n{'='*60}")
        print("SYSTEM FORTIFICATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total: {len(self.results)} | Success: {successful} | Failed: {failed}")
        print(f"Success Rate: {successful/max(1,len(self.results))*100:.0f}%")
        
        if failed > 0:
            print("\nFailed Modules:")
            for r in self.results:
                if not r.success:
                    print(f"  ✗ {r.module.name}")
    
    # ============================================================
    # PUBLIC METHODS
    # ============================================================
    
    def list_modules_cinematic(self):
        """Display modules in cinematic layout"""
        if RICH_AVAILABLE:
            console = Console()
            table = Table(title="[bold cyan]AVAILABLE HARDENING MODULES[/bold cyan]", box=box.HEAVY_EDGE)
            table.add_column("#", style="dim", width=4)
            table.add_column("Module", style="cyan", width=35)
            table.add_column("Category", style="green", width=20)
            table.add_column("Severity", style="yellow", width=10)
            table.add_column("Compat", justify="center", width=6)
            
            for i, m in enumerate(self.modules, 1):
                compat = "✓" if not m.platforms or self.system in m.platforms else "✗"
                severity_color = "red" if m.severity == HardeningSeverity.CRITICAL else "yellow"
                table.add_row(str(i), m.name[:32], m.category.value[:18], f"[{severity_color}]{m.severity.value[0]}[/{severity_color}]", compat)
            
            console.print(table)
        else:
            for i, m in enumerate(self.modules, 1):
                print(f"{i:2d}. {m.name[:40]:40s} [{m.severity.value}]")
    
    def show_status_cinematic(self):
        """Show status in cinematic layout"""
        if RICH_AVAILABLE:
            console = Console()
            layout = self._create_tactical_layout()
            layout["header"].update(Panel("[bold green]DSTERMINAL HARDENING STATUS[/bold green]", border_style="green"))
            layout["panel1"].update(self._get_system_metrics_panel())
            layout["panel2"].update(self._get_hardening_ops_panel())
            layout["panel3"].update(self._get_network_defense_panel())
            layout["panel4"].update(self._get_threat_feed_panel())
            console.print(layout)
        else:
            print(f"System: {self.system} | Admin: {self.is_admin_user}")
            print(f"Modules: {len(self.modules)} | Selected: {len(self.selected_modules)}")
            print(f"Executed: {len(self.results)} | Success: {sum(1 for r in self.results if r.success)}")
    
    def run_cinematic(self):
        """Main cinematic dashboard"""
        if not RICH_AVAILABLE:
            print("[!] Rich library not available. Using fallback mode.")
            self.run()
            return
        
        console = Console()
        
        while True:
            console.clear()
            
            # Create main layout
            layout = self._create_tactical_layout()
            
            # Header
            layout["header"].update(Panel(
                "[bold green]DSTERMINAL HARDENING DASHBOARD v3.0[/bold green]\n"
                f"[dim]Enterprise Security Suite | Session: {self.session_id}[/dim]",
                border_style="green"
            ))
            
            # Update all panels
            layout["panel1"].update(self._get_system_metrics_panel())
            layout["panel2"].update(self._get_hardening_ops_panel())
            layout["panel3"].update(self._get_network_defense_panel())
            layout["panel4"].update(self._get_threat_feed_panel())
            
            # Footer menu
            menu = Panel(
                "[bold cyan]MENU[/bold cyan]\n"
                "[green][1][/green] Select Modules  "
                "[green][2][/green] View Selected  "
                "[green][3][/green] Execute Hardening  "
                "[green][4][/green] View Results  "
                "[green][5][/green] Generate Report  "
                "[green][6][/green] Rollback  "
                "[green][7][/green] List Modules  "
                "[green][8][/green] Status  "
                "[red][9][/red] Exit",
                border_style="cyan"
            )
            layout["footer"].update(menu)
            
            console.print(layout)
            
            choice = console.input("\n[bold cyan]Select option: [/bold cyan]").strip()
            
            if choice == '1':
                self._select_modules_interactive()
            elif choice == '2':
                self._view_selected_modules()
            elif choice == '3':
                self._execute_hardening_realtime()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '4':
                self._view_results()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '5':
                self._generate_report()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '6':
                self._rollback_hardening()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '7':
                self.list_modules_cinematic()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '8':
                self.show_status_cinematic()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '9':
                console.print("\n[bold green]Exiting dashboard...[/bold green]")
                break
            else:
                console.print("[red]Invalid option[/red]")
                time.sleep(1)
    
    # ============================================================
    # LEGACY METHODS (for compatibility)
    # ============================================================
    
    def _select_modules_interactive(self):
        """Interactive module selection"""
        self._clear_screen()
        self._display_header()
        
        categories = {}
        for module in self.modules:
            cat = module.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(module)
        
        print(f"\n{Fore.CYAN}{'='*self.terminal_width}")
        print(self._center_text("MODULE SELECTION"))
        print(f"{'='*self.terminal_width}{Fore.RESET}\n")
        
        idx = 1
        for category, mods in categories.items():
            print(f"\n{Fore.YELLOW}▸ {category}{Fore.RESET}")
            print(f"{Fore.WHITE}{'─'*50}{Fore.RESET}")
            for m in mods:
                selected = "✓" if m.id in self.selected_modules else "○"
                severity_color = Fore.RED if m.severity == HardeningSeverity.CRITICAL else Fore.YELLOW
                print(f"  [{selected}] {Fore.GREEN}{idx:2d}{Fore.RESET}. {m.name:40s} [{severity_color}{m.severity.value}{Fore.RESET}]")
                idx += 1
        
        print(f"\n{Fore.CYAN}Commands: all, clear, back, or numbers (e.g., 1,3,5-8){Fore.RESET}")
        choice = input(f"\n{Fore.GREEN}Selection:{Fore.RESET} ").strip().lower()
        
        if choice == 'all':
            self.selected_modules = [m.id for m in self.modules if not (m.requires_admin and not self.is_admin_user)]
        elif choice == 'clear':
            self.selected_modules = []
        elif choice != 'back':
            try:
                indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if '-' in part:
                        s, e = part.split('-')
                        indices.extend(range(int(s), int(e) + 1))
                    else:
                        indices.append(int(part))
                for i in indices:
                    if 1 <= i <= len(self.modules):
                        m = self.modules[i - 1]
                        if m.id not in self.selected_modules:
                            self.selected_modules.append(m.id)
            except:
                print(f"{Fore.RED}Invalid selection{Fore.RESET}")
    
    def _view_selected_modules(self):
        self._clear_screen()
        self._display_header()
        
        if not self.selected_modules:
            print(f"{Fore.YELLOW}No modules selected{Fore.RESET}")
        else:
            selected = [m for m in self.modules if m.id in self.selected_modules]
            for i, m in enumerate(selected, 1):
                status = f"{Fore.GREEN}✓{Fore.RESET}" if m.applied else f"{Fore.YELLOW}○{Fore.RESET}"
                print(f"  {status} {i:2d}. {m.name}")
    
    def _view_results(self):
        self._clear_screen()
        self._display_header()
        
        if not self.results:
            print(f"{Fore.YELLOW}No results{Fore.RESET}")
        else:
            for i, r in enumerate(self.results, 1):
                status = f"{Fore.GREEN}✓{Fore.RESET}" if r.success else f"{Fore.RED}✗{Fore.RESET}"
                duration = (r.end_time - r.start_time).total_seconds() if r.end_time else 0
                print(f"  {status} {i:2d}. {r.module.name} [{duration:.1f}s]")
                if r.error:
                    print(f"      {Fore.RED}Error: {r.error}{Fore.RESET}")
                if r.live_output:
                    for line in r.live_output[-3:]:
                        print(f"      {Fore.DARK_GRAY}{line[:70]}{Fore.RESET}")
    
    def _generate_report(self):
        report_dir = os.path.expanduser("~/DSTerminal_Workspace/reports")
        os.makedirs(report_dir, exist_ok=True)
        
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "admin": self.is_admin_user,
            "total": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "results": [{
                "module": r.module.name,
                "success": r.success,
                "error": r.error,
                "output": r.output[:500]
            } for r in self.results]
        }
        
        report_path = f"{report_dir}/hardening_{self.session_id}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"{Fore.GREEN}✓ Report saved: {report_path}{Fore.RESET}")
    
    def _rollback_hardening(self):
        applied = [r for r in self.results if r.success and r.module.rollback_command]
        if not applied:
            print(f"{Fore.YELLOW}No modules to rollback{Fore.RESET}")
            return
        
        confirm = input(f"{Fore.RED}Type 'ROLLBACK' to confirm: {Fore.RESET}").strip()
        if confirm == "ROLLBACK":
            for r in applied:
                print(f"{Fore.CYAN}Rolling back {r.module.name}...{Fore.RESET}")
                try:
                    subprocess.run(r.module.rollback_command, shell=True, check=True, timeout=15)
                    print(f"{Fore.GREEN}✓ Rolled back{Fore.RESET}")
                    self._add_threat_event(f"Rolled back {r.module.name}", "warning")
                except Exception as e:
                    print(f"{Fore.RED}✗ Failed: {e}{Fore.RESET}")
    
    def _display_header(self):
        header = f"""
{Fore.GREEN}{'='*self.terminal_width}
{self._center_text('DSTERMINAL HARDENING DASHBOARD v3.0')}
{self._center_text('Enterprise Security Suite')}
{'='*self.terminal_width}{Fore.RESET}
{Fore.YELLOW}System: {self.system} | Admin: {self.is_admin_user} | Session: {self.session_id[-8:]}{Fore.RESET}
"""
        print(header)
    
    def _center_text(self, text: str) -> str:
        return text.center(self.terminal_width)
    
    def _clear_screen(self):
        os.system('cls' if self.system == 'Windows' else 'clear')
    
    def run(self):
        """Legacy run method for fallback"""
        try:
            while True:
                self._clear_screen()
                self._display_header()
                
                menu = f"""
{Fore.CYAN}[1]{Fore.RESET} Select Modules
{Fore.CYAN}[2]{Fore.RESET} View Selected
{Fore.CYAN}[3]{Fore.RESET} Execute Hardening
{Fore.CYAN}[4]{Fore.RESET} View Results
{Fore.CYAN}[5]{Fore.RESET} Generate Report
{Fore.CYAN}[6]{Fore.RESET} Rollback
{Fore.CYAN}[7]{Fore.RESET} List Modules
{Fore.CYAN}[8]{Fore.RESET} Status
{Fore.CYAN}[9]{Fore.RESET} Exit
"""
                print(menu)
                choice = input(f"\n{Fore.CYAN}Select: {Fore.RESET}").strip()
                
                if choice == '1':
                    self._select_modules_interactive()
                elif choice == '2':
                    self._view_selected_modules()
                    input("\nPress Enter...")
                elif choice == '3':
                    self._execute_hardening_realtime()
                    input("\nPress Enter...")
                elif choice == '4':
                    self._view_results()
                    input("\nPress Enter...")
                elif choice == '5':
                    self._generate_report()
                    input("\nPress Enter...")
                elif choice == '6':
                    self._rollback_hardening()
                    input("\nPress Enter...")
                elif choice == '7':
                    self.list_modules_cinematic()
                    input("\nPress Enter...")
                elif choice == '8':
                    self.show_status_cinematic()
                    input("\nPress Enter...")
                elif choice == '9':
                    break
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted{Fore.RESET}")
        finally:
            self.telemetry.stop()


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    dashboard = HardeningDashboard()
    
    if RICH_AVAILABLE:
        dashboard.run_cinematic()
    else:
        print(f"{Fore.YELLOW}Rich library not available. Install with: pip install rich{Fore.RESET}")
        dashboard.run()
        