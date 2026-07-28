def __init__(self, workspace_root=None, interactive: bool = True):
    """Initialize DSTerminal with integrated operator session management"""
    import platform
    import queue
    from pathlib import Path
    
#  =================================================

# ==================================================
    # ============================================================
    # STEP 1: Set up workspace root FIRST
    # ============================================================
    if workspace_root is None:
        self.workspace_root = os.path.expanduser("~/dsterminal_workspace")
    else:
        self.workspace_root = workspace_root
    
    # Ensure workspace directory exists
    os.makedirs(self.workspace_root, exist_ok=True)
    
    # Create default directories
    default_dirs = ["exploits", "reports", "sandbox", "scans", "operators", 
                   "network_reports", "integrity_reports", "compliance_reports", 
                   "logs", "baselines", "alerts", "quarantine", "forensic", 
                   "auto_quarantine", "siem_logs"]
    for dir_name in default_dirs:
        dir_path = os.path.join(self.workspace_root, dir_name)
        os.makedirs(dir_path, exist_ok=True)
    
    # Create threat_maps subdirectory
    threat_maps_dir = os.path.join(self.workspace_root, 'network_reports', 'threat_maps')
    os.makedirs(threat_maps_dir, exist_ok=True)
    
    # ============================================================
    # STEP 2: Initialize operator session (PERSISTENT STORAGE)
    # This MUST come early so all logging works
    # ============================================================
    self.interactive = interactive
    self.terminal_width = self._get_terminal_width()
    self.system = platform.system()
    
    # Initialize operator session with persistent storage
    self.operator_username = None
    self.session_id = None
    self.session_start = None
    self.operator_dir = None
    self.log_file = None
    self.session_manager_initialized = False
    
    try:
        self.initialize_operator_session()
        self.session_manager_initialized = True
    except Exception as e:
        print(f"⚠ Failed to initialize operator session: {e}")
        # Fallback session
        import uuid
        self.operator_username = f"OP-{uuid.uuid4().hex[:6].upper()}"
        self.session_id = f"SESSION-{uuid.uuid4().hex[:5].upper()}"
        self.session_start = datetime.now()
    
    # ============================================================
    # STEP 3: Set global variables for backward compatibility
    # ============================================================
    global GLOBAL_OPERATOR, GLOBAL_SESSION
    GLOBAL_OPERATOR = self.operator_username
    GLOBAL_SESSION = self.session_id
    
    # ============================================================
    # STEP 4: Set workspace and crypto
    # ============================================================
    self.workspace = str(self.workspace_root)
    self.current_dir = self.workspace_root
    
    try:
        self.crypto = CryptoEngine(os.getcwd())
    except Exception as e:
        print(f"⚠ CryptoEngine initialization failed: {e}")
        self.crypto = None
    
    # ============================================================
    # STEP 5: Initialize scanner and monitoring components
    # ============================================================
    try:
        self.scanner = SQLMapScanner(verbose=True)
    except Exception as e:
        print(f"⚠ SQLMapScanner initialization failed: {e}")
        self.scanner = None
    
    # ============================================================
    # STEP 6: Initialize SOC Nmap Dashboard integration
    # ============================================================
    self.soc_nmap = None
    self.soc_dashboard_active = False
    
    if SOC_NMAP_AVAILABLE and 'SOCNmapIntegration' in globals():
        try:
            self.soc_nmap = SOCNmapIntegration()
        except Exception as e:
            print(f"[!] Failed to initialize SOC Nmap: {e}")
            self.soc_nmap = None
    else:
        self.soc_nmap = None
        print("[!] SOC Nmap Dashboard not available - module or class not found")
    
    # ============================================================
    # STEP 7: Initialize Hardening Dashboard
    # ============================================================
    try:
        self.hardening_dashboard = HardeningDashboard(terminal_width=self.terminal_width)
        self.hardening_enabled = True
    except Exception as e:
        print(f"⚠ Hardening Dashboard initialization failed: {e}")
        self.hardening_dashboard = None
        self.hardening_enabled = False
    
    # ============================================================
    # STEP 8: Register commands (including session commands)
    # ============================================================
    self.commands = {
        'sqlmap': {
            'func': self.cmd_sqlmap,
            'desc': 'Run SQLMap scan on a URL'
        },
        'sqllab': {
            'func': self.cmd_sqllab,
            'desc': 'Start SQL Injection Learning Lab'
        },
        'sqlmap-install': {
            'func': self.cmd_sqlmap_install,
            'desc': 'Install SQLMap'
        },
        'sqlmap-reset': {
            'func': self.cmd_sqlmap_reset,
            'desc': 'Reset SQL Injection Lab database'
        },
        'sqlmap-secure': {
            'func': self.cmd_sqlmap_secure,
            'desc': 'Toggle secure mode on/off'
        },
        'sqlmap-status': {
            'func': self.cmd_sqlmap_status,
            'desc': 'Show SQLMap lab status'
        },
        'sqlmap-help': {
            'func': self.cmd_sqlmap_help,
            'desc': 'Show SQLMap help'
        },
        'sqllab-stop': {
            'func': self.cmd_sqllab_stop,
            'desc': 'Stop SQL Injection Learning Lab'
        },
        'sqlmap-info': {
            'func': self.cmd_sqlmap_info,
            'desc': 'Show SQLMap information and version'
        },
        'sqlmap-file': {
            'func': self.cmd_sqlmap_scan_file,
            'desc': 'Scan URLs from a file'
        },
        'sqlmap-export': {
            'func': self.cmd_sqlmap_export_report,
            'desc': 'Export the last scan report'
        },
        'monitor': {
            'func': self.cmd_monitor,
            'desc': 'Start deletion protection monitor'
        },
        'monitor-all': {
            'func': self.cmd_monitor_all,
            'desc': 'Monitor entire user profile'
        },
        'kill-monitor': {
            'func': self.cmd_kill_monitor,
            'desc': 'Force kill monitoring window'
        },
        'watch-folders': {
            'func': self.cmd_start_folder_watcher,
            'desc': 'Watch for new folders'
        },
        'service-start': {
            'func': self.cmd_service_start,
            'desc': 'Start deletion protection service'
        },
        'service-stop': {
            'func': self.cmd_service_stop,
            'desc': 'Stop deletion protection service'
        },
        'service-status': {
            'func': self.cmd_service_status,
            'desc': 'Show service status'
        },
        'list-backups': {
            'func': self.cmd_list_backups,
            'desc': 'List recent backups'
        },
        'search': {
            'func': self.cmd_search_backups,
            'desc': 'Search backups'
        },
        'restore-id': {
            'func': self.cmd_restore_id,
            'desc': 'Restore backup by ID'
        },
        'restore-last': {
            'func': self.cmd_restore_last,
            'desc': 'Restore last deleted'
        },
        'add-path': {
            'func': self.cmd_add_path,
            'desc': 'Add monitoring path'
        },
        'workspace-info': {
            'func': self.cmd_workspace_info,
            'desc': 'Show workspace info'
        },
        'cleanup': {
            'func': self.cmd_cleanup,
            'desc': 'Clean temp files'
        },
        'platform-info': {
            'func': self.cmd_platform_info,
            'desc': 'Show platform info'
        },
        # SESSION MANAGEMENT COMMANDS
        'session-info': {
            'func': self.display_operator_info,
            'desc': 'Show current session information'
        },
        'session-history': {
            'func': self.show_session_history,
            'desc': 'Show session history'
        },
        'view-log': {
            'func': self.view_session_log,
            'desc': 'View current session log'
        },
        'list-operators': {
            'func': self.list_operators,
            'desc': 'List all registered operators'
        },
        'close-session': {
            'func': self.close_operator_session,
            'desc': 'Close current session'
        },
    }
    
    # ============================================================
    # STEP 9: Initialize configuration
    # ============================================================
    pd = PlatformDetector()
    
    self.config = {
        'version': '3.1.113',
        'monitor_paths': pd.get_trash_paths(),
        'exclude_patterns': ['*.tmp', '*.temp', '*~', '.DS_Store', 'Thumbs.db'],
        'max_file_size': 100 * 1024 * 1024,
        'encrypt_backups': False,
    }
    
    # ============================================================
    # STEP 10: Initialize managers
    # ============================================================
    self.config_manager = None
    self.monitor = None
    self.observer = None
    self.running = False
    
    try:
        self.service_manager = ServiceManager(
            self.workspace_root, 
            pid_file=os.path.join(self.workspace_root, 'dsterminal.pid')
        )
    except Exception as e:
        print(f"⚠ ServiceManager initialization failed: {e}")
        self.service_manager = None
    
    # ============================================================
    # STEP 11: Initialize integrity monitor
    # ============================================================
    self.integrity = None
    self.alert_manager = None
    self.forensic = None
    self.autoremediation = None
    
    if INTEGRITY_AVAILABLE:
        try:
            self.integrity = SystemIntegrityMonitor()
            self.alert_manager = AlertManager(self.integrity)
            self.alert_manager.alerts = []
            self.forensic = ForensicAnalyzer(self.integrity)
            self.autoremediation = AutoRemediation(self.integrity)
            
            if COLORS_AVAILABLE:
                print(f"{Fore.GREEN}✓ Integrity Monitor initialized{Style.RESET_ALL}")
            else:
                print("✓ Integrity Monitor initialized")
                
        except Exception as e:
            if COLORS_AVAILABLE:
                print(f"{Fore.RED}✗ Failed to initialize Integrity Monitor: {e}{Style.RESET_ALL}")
            else:
                print(f"✗ Failed to initialize Integrity Monitor: {e}")
            self.integrity = None
            self.alert_manager = None
            self.forensic = None
            self.autoremediation = None
    else:
        if COLORS_AVAILABLE:
            print(f"{Fore.YELLOW}⚠ Integrity Monitor disabled{Style.RESET_ALL}")
        else:
            print("⚠ Integrity Monitor disabled")
    
    # ============================================================
    # STEP 12: Initialize VirusTotal scanner
    # ============================================================
    self.vt_scanner = None
    if VT_AVAILABLE:
        try:
            self.vt_scanner = VirusTotalScanner()
        except Exception as e:
            print(f"[!] Failed to initialize VT Scanner: {e}")
    
    # ============================================================
    # STEP 13: Initialize console and scanning components
    # ============================================================
    self.console = Console()
    self.scan_queue = queue.Queue()
    self.scan_results = {}
    self.current_scan = None
    self.output_lines = []
    self.scan_progress = 0
    self.scan_status = "Ready"
    self.discovered_ports = []
    self.services_found = []
    self.nmap_mode = False
    
    # Set up workspace root and current directory
    self.workspace = os.path.abspath("DSTerminal_Workspace")
    self.current_dir = self.workspace
    home = Path.home()
    workspace = home / "dsterminal_workspace"
    workspace.mkdir(exist_ok=True)
    
    # Create workspace if it doesn't exist
    if not os.path.exists(self.workspace_root):
        os.makedirs(self.workspace_root)
    
    # Create default directories
    default_dirs = ["exploits", "reports", "sandbox", "scans", "operators"]
    for dir_name in default_dirs:
        dir_path = os.path.join(self.workspace_root, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # ============================================================
    # STEP 14: Setup logging
    # ============================================================
    self._setup_logging()
    
    # ============================================================
    # STEP 15: Log initialization
    # ============================================================
    self.log_to_siem(f"DSTerminal initialized by {self.operator_username}")
    self.log_event("SYSTEM", f"DSTerminal v{self.config['version']} initialized")
    
    # ============================================================
    # STEP 16: Display initialization banner
    # ============================================================
    if interactive:
        self._display_initialization_banner()


def _display_initialization_banner(self):
    """Display initialization banner with operator info"""
    import shutil
    import platform
    
    width = shutil.get_terminal_size().columns
    
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    DSTerminal Security Tool                   ║
╠══════════════════════════════════════════════════════════════╣
║ Version    : {self.config['version']}
║ Operator   : {self.operator_username}
║ Session ID : {self.session_id}
║ Started    : {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
║ Host       : {platform.node()}
║ Workspace  : {self.workspace_root}
╚══════════════════════════════════════════════════════════════╝
    """
    
    for line in banner.splitlines():
        if line.strip():
            padding = max((width - len(line)) // 2, 0)
            print(" " * padding + line)