#0 importing dsterminal_dashboard
try:
from dsterminal_dashboard import register_dashboard_commands, DASHBOARD_AVAILABLE, dashboard_integration
except ImportError:
    DASHBOARD_AVAILABLE = False
def register_dashboard_commands(terminal):
    return False

# 1 importing web_security_analyzer
try:
import web_security_analyzer
WEB_SECURITY_AVAILABLE = True
except ImportError as e:
    WEB_SECURITY_AVAILABLE = False
    safe_print_unicode(f"Warning: web_security_analyzer module not found: {e}")

#2 WiFi Audit Module
try:
    from wifi_audit import NetworkAudit
    NETWORK_AUDIT_AVAILABLE = True
except ImportError as e:
    NETWORK_AUDIT_AVAILABLE = False
    print(f"{Fore.YELLOW}⚠️ WiFi Audit module not found: {e}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   Download wifi_audit from the repository{Style.RESET_ALL}")

# 2. Integrity Monitor - Silent
try:
from integrity_monitor import (
    SystemIntegrityMonitor,
    AlertManager,
    AutoRemediation,
    RealTimeHandler
)
INTEGRITY_AVAILABLE = True
        except:
            SystemIntegrityMonitor = None
            AlertManager = None
            AutoRemediation = None
            RealTimeHandler = None
            pass

# 3. SOC Nmap Dashboard - Silent
try:
from soc_nmap_dashboard import SOCNmapDashboard, SOCNmapIntegration
SOC_NMAP_AVAILABLE = True
        except:
            pass

# 4. VirusTotal - Silent
try:
import vt_scan
from vt_scan import VirusTotalScanner, vt_scan_menu, sync_operator_session
VT_AVAILABLE = True
        except:
            VirusTotalScanner = None
            vt_scan_menu = None
            sync_operator_session = None
            pass

        # 5. Recon Modules - Silent
        try:
            recon_path = os.path.join(BASE_PATH, 'recon.py')
            if os.path.exists(recon_path):
import importlib.util
spec = importlib.util.spec_from_file_location("recon", recon_path)
recon_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recon_module)
ReconScanner = getattr(recon_module, 'ReconScanner', None)
run_recon = getattr(recon_module, 'run_recon', None)
recon_menu = getattr(recon_module, 'recon_menu', None)
RECON_AVAILABLE = True
        except:
            ReconScanner = None
            run_recon = None
            recon_menu = None
            pass

        # 6. Recon Full - Silent
        try:
            recon_full_path = os.path.join(BASE_PATH, 'recon_full.py')
            if os.path.exists(recon_full_path):
import importlib.util
spec = importlib.util.spec_from_file_location("recon_full", recon_full_path)
recon_full_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recon_full_module)
FullReconScanner = getattr(recon_full_module, 'FullReconScanner', None)
run_full_recon = getattr(recon_full_module, 'run_full_recon', None)
full_recon_menu = getattr(recon_full_module, 'full_recon_menu', None)
RECON_FULL_AVAILABLE = True
        except:
            FullReconScanner = None
            run_full_recon = None
            full_recon_menu = None
            pass

        # 7. Hardening Dashboard - Silent
        try:
from hardening_dashboard import HardeningDashboard
HARDENING_AVAILABLE = True
        except:
            HardeningDashboard = None
            pass

        # 8. Ransomware Monitor - Silent
        try:
from ransomware_monitor import RansomwareMonitor, cmd_ransomware
RANSOMWARE_AVAILABLE = True
        except:
            RansomwareMonitor = None
            cmd_ransomware = None
            pass

        # 9. Financial Forensics - Silent
        try:
from financial_forensics import financial_forensics_menu
FINANCIAL_FORENSICS_AVAILABLE = True
        except:
            financial_forensics_menu = None
            pass


        # ============================================================
        # 10 IMPORT STEGANOGRAPHY ANALYZER
        # ============================================================
        STEG_ANALYZER_AVAILABLE = False
        try:
import steg_analyzer
from steg_analyzer import StegAnalyzer, dashboard
STEG_ANALYZER_AVAILABLE = True
print("[✓] StegAnalyzer module loaded successfully")
        except ImportError as e:
            print(f"[!] StegAnalyzer module not found: {e}")
            print(f"[!] Current directory: {os.getcwd()}")
            print(f"[!] Files in directory: {os.listdir('.')}")
        except Exception as e:
            print(f"[!] Error loading StegAnalyzer: {e}")
import traceback
traceback.print_exc()


# 11 Import crypto_engine
try:
    crypto_path = os.path.join(BASE_PATH, 'crypto_engine.py')
    if os.path.exists(crypto_path):
import importlib.util
spec = importlib.util.spec_from_file_location("crypto_engine", crypto_path)
crypto_engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crypto_engine_module)
CryptoEngine = crypto_engine_module.CryptoEngine
crypto_engine = CryptoEngine(BASE_PATH)
    else:
        print(f"⚠ crypto_engine.py not found at: {crypto_path}")
        crypto_engine = None
except Exception as e:
    print(f"⚠ Crypto engine import error: {e}")
    crypto_engine = None

    #12 . Crypto Engine - Silent
    try:
from crypto_engine import CryptoEngine
CRYPTO_AVAILABLE = True
    except:
        CryptoEngine = None
        pass
    # ===================================

    #13 IOC Education Module
    try:
from ioc_edu import IOCEducation
IOC_EDUCATION_AVAILABLE = True
    except ImportError as e:
        IOC_EDUCATION_AVAILABLE = False
        print(f"{Fore.YELLOW}⚠️ IOC Education module not found: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Download ioc_education from the repository{Style.RESET_ALL}")


        #14 Exploit Scanner Module
        try:
from exploit_scanner import ExploitScanner
EXPLOIT_SCANNER_AVAILABLE = True
        except ImportError as e:
            EXPLOIT_SCANNER_AVAILABLE = False
            print(f"{Fore.YELLOW}⚠️ Exploit Scanner module not found: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Download exploit_scanner from the repository{Style.RESET_ALL}")


            # 15. advanced_sql
            # Import the enhanced SQLMap scanner and lab
from sqlmap_advanced import (
    EnhancedSQLMapScanner,
    EnhancedSQLInjectionLab,
    EnhancedPDFNotesGenerator,
    EnhancedLabHTTPHandler,
    ADVANCED_SQL_INJECTION_TECHNIQUES,
    WAF_BYPASS_TECHNIQUES,
    MITRE_ATTACK_MAPPING
)

# ============================================
# FALLBACK FUNCTIONS - if needed
# ============================================
if not RECON_AVAILABLE:
def run_recon():
    print(f"{Fore.YELLOW}Recon module not available.{Style.RESET_ALL}")
def recon_menu():
    print(f"{Fore.YELLOW}Recon module not available.{Style.RESET_ALL}")

    if not RECON_FULL_AVAILABLE:
def run_full_recon():
    print(f"{Fore.YELLOW}Full Recon module not available.{Style.RESET_ALL}")
def full_recon_menu():
    print(f"{Fore.YELLOW}Full Recon module not available.{Style.RESET_ALL}")

    # 16 importing soc_auto..
    try:
from soc_automated_lab import SOCAutomatedLab
SOC_LAB_AVAILABLE = True
    except ImportError:
        SOC_LAB_AVAILABLE = False
        print("[!] SOC Automated Lab module not available")
