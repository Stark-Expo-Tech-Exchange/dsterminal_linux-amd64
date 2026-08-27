#!python
import sys
# -*- coding: utf-8 -*-

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

# update.py - COMPLETE FIXED VERSION WITH PROPER COLORS AND EXIT PAUSE
import os
import time
import random
import platform
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
import requests

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
# DEFINE COLORS CLASS FIRST (ALWAYS AVAILABLE)
# ============================================================
class Colors:
    """Cross-platform color support"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BLINK = '\033[5m'
    
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    
    BRIGHT_CYAN = '\033[96;1m'
    BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_RED = '\033[91;1m'
    BRIGHT_YELLOW = '\033[93;1m'
    BRIGHT_MAGENTA = '\033[95;1m'
    BRIGHT_BLUE = '\033[94;1m'

# ============================================================
# IMPORT COLORAMA WITH PROPER ERROR HANDLING
# ============================================================
try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Use Colors class as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })
except Exception as e:
    COLORAMA_AVAILABLE = False
    # Use Colors class as fallback
    Fore = Colors
    Style = type('Style', (), {
        'RESET_ALL': '\033[0m',
        'BRIGHT': '\033[1m',
        'DIM': '\033[2m'
    })

# ============================================================
# COLOR FUNCTIONS
# ============================================================
RESET = Colors.RESET
BOLD = Colors.BOLD
DIM = Colors.DIM
BLINK = Colors.BLINK

CYAN = Colors.CYAN
YELLOW = Colors.YELLOW
GREEN = Colors.GREEN
RED = Colors.RED
BLUE = Colors.BLUE
MAGENTA = Colors.MAGENTA
WHITE = Colors.WHITE

BRIGHT_CYAN = Colors.BRIGHT_CYAN
BRIGHT_GREEN = Colors.BRIGHT_GREEN
BRIGHT_RED = Colors.BRIGHT_RED
BRIGHT_YELLOW = Colors.BRIGHT_YELLOW
BRIGHT_MAGENTA = Colors.BRIGHT_MAGENTA
BRIGHT_BLUE = Colors.BRIGHT_BLUE

def colorize(text, color=BRIGHT_GREEN):
    """Simple colorize function without Rich"""
    return f"{color}{text}{RESET}"

def strip_rich_markup(text):
    """Strip Rich markup from text"""
    import re
    # Remove [bold], [cyan], [dim], etc.
    text = re.sub(r'\[/?[a-z_]+\]', '', text)
    return text

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
# RICH IMPORTS WITH PROPER INITIALIZATION
# ============================================================
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        Progress, SpinnerColumn, TextColumn, BarColumn, 
        DownloadColumn, TransferSpeedColumn
    )
    from rich.live import Live
    from rich.align import Align
    from rich.table import Table
    from rich import box
    from rich.markdown import Markdown
    from rich.layout import Layout
    from rich.columns import Columns
    from rich.text import Text
    from rich.style import Style as RichStyle
    RICH_AVAILABLE = True
    
    # Force color support
    console = Console(color_system="auto", force_terminal=True)
except ImportError:
    RICH_AVAILABLE = False
    console = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
 
class UpdateManager:
    def __init__(self, config):
        self.config = config
        self.console = console if RICH_AVAILABLE else None
        
        # ============================================================
        # REPOSITORY CONFIGURATION
        # ============================================================
        self.github_repo = "Stark-Expo-Tech-Exchange/DSTerminal_releases_latest"
        
        # ============================================================
        # GITHUB TOKEN
        # ============================================================
        self.github_token = self.config.get("GITHUB_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
        
        # ============================================================
        # DOWNLOAD DIRECTORY - Use Downloads folder
        # ============================================================
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(self.download_dir):
            self.download_dir = tempfile.gettempdir()
        
        self.asset_api_url = None
        
        # Simulated update messages for hacker interface
        self.update_messages = [
            "[*] Scanning module dependencies...",
            "[+] Analyzing version compatibility matrix...",
            "[+] Synchronizing with remote repositories...",
            "[*] Verifying digital signatures...",
            "[+] Extracting package metadata...",
            "[+] Optimizing update pipeline...",
            "[*] Cleaning temporary files...",
            "[+] Configuring update parameters...",
            "[+] Generating performance metrics...",
            "[*] Validating security protocols...",
            "[+] Establishing secure connection...",
            "[+] Downloading delta patches...",
            "[*] Compiling update modules...",
            "[+] Running pre-installation checks...",
            "[+] Analyzing system compatibility...",
            "[*] Scanning for conflicts...",
            "[+] Preparing installation packages...",
            "[+] Accelerating download stream...",
            "[*] Verifying checksums...",
            "[+] Monitoring network throughput...",
            "[*] Decrypting update payload...",
            "[+] Resolving dependency tree...",
            "[+] Generating update manifest...",
            "[*] Building update artifacts...",
            "[+] Launching update engine...",
            "[+] Scanning for available mirrors...",
            "[*] Validating package integrity...",
            "[+] Analyzing disk space requirements...",
            "[+] Optimizing bandwidth usage...",
            "[*] Synchronizing with CDN...",
            "[+] Establishing secure tunnel...",
            "[+] Extracting compressed assets...",
            "[*] Performing pre-flight checks...",
            "[+] Generating update reports...",
            "[*] Verifying SSL certificates...",
            "[+] Resolving domain names...",
            "[+] Querying update servers...",
            "[*] Compiling native extensions...",
            "[+] Running post-installation scripts...",
            "[+] Analyzing performance impact...",
            "[*] Scanning for vulnerabilities...",
            "[+] Creating system restore point...",
            "[+] Applying optimizations...",
            "[*] Rolling back failed components...",
            "[*] Encrypting sensitive data...",
            "[+] Integrating with system services...",
            "[+] Generating update summary...",
            "[*] Cleaning up temporary files...",
            "[+] Optimizing startup sequence...",
            "[+] Broadcasting update status...",
            "[*] Verifying installation integrity...",
            "[+] Archiving previous versions...",
            "[+] Configuring environment variables...",
            "[*] Updating registry entries...",
            "[*] Applying security patches...",
            "[+] Updating DNS records...",
            "[+] Synchronizing with time servers...",
            "[*] Building dependency graph...",
            "[+] Validating installation paths...",
            "[+] Analyzing file system changes...",
            "[*] Detecting hardware capabilities...",
            "[+] Merging configuration files...",
            "[+] Optimizing memory usage...",
            "[*] Verifying network connectivity...",
            "[+] Establishing peer-to-peer connection...",
            "[+] Resolving library dependencies...",
            "[*] Generating diff reports...",
            "[*] Patching binary files...",
            "[+] Preloading update cache...",
            "[+] Scanning for update nodes...",
            "[*] Validating file permissions...",
            "[+] Creating update snapshots...",
            "[+] Adjusting system parameters...",
            "[*] Calculating update size...",
            "[*] Verifying authenticity...",
            "[+] Connecting to update backend...",
            "[+] Receiving update stream...",
            "[*] Compressing update data...",
            "[+] Running simulation tests...",
            "[+] Benchmarking new features...",
            "[*] Checking for regressions...",
            "[+] Managing package versions...",
            "[+] Applying incremental updates...",
            "[*] Synchronizing with database...",
            "[*] Generating security tokens...",
            "[+] Merging code changes...",
            "[+] Monitoring system load...",
            "[*] Optimizing disk I/O...",
            "[+] Boosting update speed...",
            "[+] Transmitting telemetry data...",
            "[*] Inspecting system logs...",
            "[+] Finalizing update package...",
            "[+] Performing final checks...",
            "[*] Generating success metrics...",
            "[*] Locking update state...",
            "[+] Publishing update status...",
            "[+] Notifying update completion...",
            "[*] Finalizing installation...",
            "[+] Update verification complete...",
            "[+] System will be ready for restart...",
            "[+] Update summary will be generated...",
            "[+] Update process verification successful!"
        ]
        
    def _get_headers(self):
        """Get headers for GitHub API requests"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'DSTerminal-Update-Checker/4.0'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
            safe_print_unicode(colorize("Using Generated DSTERMINAL token for authentication", BRIGHT_GREEN))
        
        return headers
        
    def _check_github_release(self):
        """Check GitHub for latest release"""
        try:
            import requests
            from datetime import datetime
            
            current_version = self.config.get("CURRENT_VERSION", "1.0.0")
            
            headers = self._get_headers()
            
            safe_print_unicode(colorize(f"Connecting to UPDATE MODULE API for {self.github_repo}...", BRIGHT_CYAN))
            
            tags_url = f"https://api.github.com/repos/{self.github_repo}/tags"
            safe_print_unicode(colorize("Fetching tags...", BRIGHT_CYAN))
            tags_response = requests.get(tags_url, timeout=15, headers=headers)
            
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                if tags_data:
                    latest_tag = tags_data[0].get("name", "")
                    safe_print_unicode(colorize(f"✓ Found latest tag: {latest_tag}", BRIGHT_GREEN))
                    
                    release_url = f"https://api.github.com/repos/{self.github_repo}/releases/tags/{latest_tag}"
                    safe_print_unicode(colorize(f"Fetching release for tag: {latest_tag}...", BRIGHT_CYAN))
                    release_response = requests.get(release_url, timeout=15, headers=headers)
                    
                    if release_response.status_code == 200:
                        release_data = release_response.json()
                        safe_print_unicode(colorize(f"✓ Found release: {release_data.get('tag_name')}", BRIGHT_GREEN))
                        return self._process_release_data(release_data)
                    else:
                        safe_print_unicode(colorize(f"No release found for tag {latest_tag}, using tag info", BRIGHT_YELLOW))
                        return {
                            "version": latest_tag.lstrip("v"),
                            "url": f"https://github.com/{self.github_repo}/tree/{latest_tag}",
                            "download_url": f"https://github.com/{self.github_repo}/archive/refs/tags/{latest_tag}.zip",
                            "notes": f"DSTerminal {latest_tag}",
                            "prerelease": False,
                            "published_at": datetime.now().strftime('%Y-%m-%d'),
                            "asset_name": f"DSTerminal-{latest_tag}.zip",
                            "asset_size": 0,
                            "from_fallback": True
                        }
                else:
                    safe_print_unicode(colorize("✗ No tags found in repository", BRIGHT_RED))
                    raise Exception("No tags found in repository")
            else:
                safe_print_unicode(colorize(f"✗ Failed to get tags: {tags_response.status_code}", BRIGHT_RED))
                raise Exception(f"UPDATE MODULE API returned {tags_response.status_code} for tags endpoint")
             
        except requests.RequestException as e:
            safe_print_unicode(colorize(f"⚠️ Connection error: {e}", BRIGHT_RED))
            raise Exception(f"Network error while checking for updates: {e}")
        except Exception as e:
            safe_print_unicode(colorize(f"⚠️ Error: {e}", BRIGHT_RED))
            raise

    def _process_release_data(self, release):
        """Process GitHub release data into a standardized format"""
        try:
            from datetime import datetime
            
            tag_name = release.get("tag_name", "").lstrip("v")
            version = tag_name if tag_name else "0.0.0"
            
            assets = release.get("assets", [])
            
            selected_asset = None
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe") or name.endswith(".zip"):
                    selected_asset = asset
                    break
            
            if not selected_asset and assets:
                selected_asset = assets[0]
            
            download_url = None
            asset_api_url = None
            asset_name = None
            asset_size = 0
            
            if selected_asset:
                download_url = selected_asset.get("browser_download_url")
                asset_api_url = selected_asset.get("url")
                asset_name = selected_asset.get("name")
                asset_size = selected_asset.get("size", 0)
                safe_print_unicode(colorize(f"Found asset: {asset_name} ({asset_size:,} bytes)", BRIGHT_CYAN))
            
            return {
                "version": version,
                "url": release.get("html_url", ""),
                "download_url": download_url,
                "asset_api_url": asset_api_url,
                "notes": release.get("body", f"DSTerminal v{version}"),
                "prerelease": release.get("prerelease", False),
                "published_at": release.get("published_at", datetime.now().strftime('%Y-%m-%d'))[:10],
                "asset_name": asset_name,
                "asset_size": asset_size,
                "from_fallback": False
            }
        except Exception as e:
            raise Exception(f"Failed to process release data: {e}")
        
    def download_update(self, url, filename):
        """Download update with progress bar - Supports both public and private repos"""
        try:
            import requests
            import os
            
            safe_print_unicode(colorize(f"\n[+] Downloading update from DSTerminal Update Module...", BRIGHT_CYAN))
            safe_print_unicode(colorize(f"File: {filename}", BRIGHT_CYAN))
            
            if not url:
                safe_print_unicode(colorize("No download URL available", BRIGHT_RED))
                return False
            
            os.makedirs(self.download_dir, exist_ok=True)
            full_path = os.path.join(self.download_dir, filename)
            
            if os.path.exists(full_path):
                try:
                    overwrite = input(colorize("File already exists. Overwrite? (y/N): ", BRIGHT_YELLOW)).strip().lower()
                except:
                    overwrite = 'n'
                if overwrite != 'y':
                    safe_print_unicode(colorize("Download cancelled", BRIGHT_YELLOW))
                    return False
                os.remove(full_path)
            
            download_url = url
            headers = {
                'User-Agent': 'DSTerminal-Updater/4.0',
                'Accept': 'application/octet-stream'
            }
            
            if hasattr(self, 'asset_api_url') and self.asset_api_url:
                safe_print_unicode(colorize("Using asset API URL for download...", BRIGHT_CYAN))
                download_url = self.asset_api_url
                if self.github_token:
                    headers['Authorization'] = f'Bearer {self.github_token}'
                    safe_print_unicode(colorize("Using authentication token", BRIGHT_CYAN))
            
            safe_print_unicode(colorize("Connecting to server...", BRIGHT_CYAN))
            response = requests.get(
                download_url,
                headers=headers,
                stream=True,
                allow_redirects=True,
                timeout=60
            )
            
            if response.status_code == 404 and download_url != url:
                safe_print_unicode(colorize("Asset API failed, trying browser download URL...", BRIGHT_YELLOW))
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/octet-stream'
                }
                response = requests.get(
                    url,
                    headers=headers,
                    stream=True,
                    allow_redirects=True,
                    timeout=60
                )
            
            if response.status_code != 200:
                safe_print_unicode(colorize(f"Status: {response.status_code}", BRIGHT_YELLOW))
                safe_print_unicode(colorize(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}", BRIGHT_YELLOW))
                
                if response.status_code == 404:
                    safe_print_unicode(colorize("File not found. The update might be locked.", BRIGHT_YELLOW))
                    return False
                elif response.status_code == 401 or response.status_code == 403:
                    safe_print_unicode(colorize("Authentication failed. Check your Update token.", BRIGHT_YELLOW))
                    return False
            
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(full_path, 'wb') as f:
                if RICH_AVAILABLE and self.console:
                    with Progress(
                        DownloadColumn(),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TransferSpeedColumn(),
                        console=self.console,
                        transient=False
                    ) as progress:
                        task = progress.add_task("Downloading...", total=total_size if total_size > 0 else None)
                        
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress.update(task, advance=len(chunk))
                                else:
                                    progress.update(task, description=f"Downloading... {downloaded//1024}KB")
                else:
                    # Fallback download without rich
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                sys.stdout.write(f"\rDownloading: {percent}%")
                                sys.stdout.flush()
                    sys.stdout.write("\n")
            
            if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                file_size = os.path.getsize(full_path)
                safe_print_unicode(colorize(f"✓ Download complete!", BRIGHT_GREEN))
                safe_print_unicode(colorize(f"Saved to: {full_path}", BRIGHT_CYAN))
                safe_print_unicode(colorize(f"Size: {file_size:,} bytes ({file_size/(1024*1024):.1f} MB)", BRIGHT_CYAN))
                return full_path
            else:
                safe_print_unicode(colorize("Download failed - file is empty or not created", BRIGHT_RED))
                return False
                
        except requests.exceptions.HTTPError as e:
            safe_print_unicode(colorize(f"✗ HTTP Error: {e.response.status_code}", BRIGHT_RED))
            if e.response.status_code == 404:
                safe_print_unicode(colorize("File not found. The URL might be incorrect.", BRIGHT_YELLOW))
                safe_print_unicode(colorize("Or try downloading manually from Stark Expo Tech Exchange Platform", BRIGHT_YELLOW))
            elif e.response.status_code == 401 or e.response.status_code == 403:
                safe_print_unicode(colorize("Authentication failed. Check your Update token.", BRIGHT_YELLOW))
            return False
        except requests.exceptions.Timeout:
            safe_print_unicode(colorize("✗ Download timeout - Connection took too long", BRIGHT_RED))
            return False
        except requests.exceptions.ConnectionError:
            safe_print_unicode(colorize("✗ Connection error - Check your internet connection", BRIGHT_RED))
            return False
        except Exception as e:
            safe_print_unicode(colorize(f"✗ Download failed: {e}", BRIGHT_RED))
            return False
        
    def perform_update(self, latest):
        """Execute the actual update process"""
        
        console = self.console
        
        if RICH_AVAILABLE and console:
            details_table = Table(box=box.HEAVY_EDGE, border_style="cyan")
            details_table.add_column("Item", style="cyan")
            details_table.add_column("Details", style="white")
            details_table.add_row("New Version", f"[green]v{latest['version']}[/green]")
            details_table.add_row("Installer", latest.get('asset_name', 'Unknown'))
            if latest.get('asset_size'):
                size_mb = latest['asset_size'] / (1024 * 1024)
                details_table.add_row("Size", f"{size_mb:.1f} MB")
            details_table.add_row("Release", latest.get('published_at', 'Unknown'))
            
            console.print(Panel(details_table, title="[bold yellow][+] UPDATE DETAILS[/bold yellow]", border_style="yellow"))
        else:
            safe_print_unicode(colorize("\n=== UPDATE DETAILS ===", BRIGHT_CYAN))
            safe_print_unicode(colorize(f"New Version: v{latest['version']}", BRIGHT_GREEN))
            safe_print_unicode(colorize(f"Installer: {latest.get('asset_name', 'Unknown')}", BRIGHT_CYAN))
            if latest.get('asset_size'):
                size_mb = latest['asset_size'] / (1024 * 1024)
                safe_print_unicode(colorize(f"Size: {size_mb:.1f} MB", BRIGHT_CYAN))
            safe_print_unicode(colorize(f"Release: {latest.get('published_at', 'Unknown')}", BRIGHT_CYAN))
        
        safe_print_unicode(colorize("\n⚠️ SECURITY NOTICE", BRIGHT_RED))
        safe_print_unicode(colorize("- The installer will be downloaded from DSTerminal Update Module", BRIGHT_YELLOW))
        safe_print_unicode(colorize("- Verify the digital signature before running", BRIGHT_YELLOW))
        safe_print_unicode(colorize("- The installer may requires you access to License Key to activate the product and ready for installation process,", BRIGHT_YELLOW))
        safe_print_unicode(colorize("- Administrator privileges may be required", BRIGHT_YELLOW))
        safe_print_unicode(colorize("- If the file is very large (>=243.9 MB), the download will take some time", BRIGHT_YELLOW))
        safe_print_unicode(colorize("- Make sure you have enough disk space and a stable internet connection", BRIGHT_YELLOW))
        
        try:
            confirm = input(colorize("Type 'INSTALL' to download and run the installer: ", BRIGHT_RED)).strip()
        except:
            confirm = ""
        
        if confirm != "INSTALL":
            safe_print_unicode(colorize("Update cancelled", BRIGHT_YELLOW))
            return False
        
        if not latest.get('download_url'):
            safe_print_unicode(
                colorize("No automatic download available", BRIGHT_YELLOW)
            )
            safe_print_unicode(
                colorize("Please download manually from Stark Expo Tech Exchange", BRIGHT_YELLOW)
            )
            return False
        
        self.asset_api_url = latest.get('asset_api_url')
        
        installer_name = latest['asset_name'] or f"DSTerminal-v{latest['version']}.zip"
        download_result = self.download_update(latest['download_url'], installer_name)
        
        if not download_result:
            safe_print_unicode(colorize("Download failed", BRIGHT_RED))
            return False
        
        installer_path = download_result if isinstance(download_result, str) else None
        
        if not installer_path or not os.path.exists(installer_path) or os.path.getsize(installer_path) == 0:
            safe_print_unicode(colorize("Download verification failed", BRIGHT_RED))
            return False
        
        safe_print_unicode(colorize("\n✓ Download verified successfully", BRIGHT_GREEN))
        
        safe_print_unicode(colorize("\n[+] Ready to install update...", BRIGHT_CYAN))
        try:
            run_installer = input(colorize("Run the installer now? (Y/n): ", BRIGHT_YELLOW)).strip().lower()
        except:
            run_installer = 'y'
        
        if run_installer != 'n':
            safe_print_unicode(colorize("Launching installer...", BRIGHT_CYAN))
            time.sleep(1)
            
            try:
                if platform.system().lower() == "windows":
                    os.startfile(installer_path)
                else:
                    if platform.system().lower() != "windows":
                        os.chmod(installer_path, 0o755)
                    subprocess.Popen([installer_path], shell=True)
                
                safe_print_unicode(colorize(f"\n✓ INSTALLER LAUNCHED!", BRIGHT_GREEN))
                safe_print_unicode(colorize("Please complete the installation wizard", BRIGHT_YELLOW))
                safe_print_unicode(colorize(f"Installer location: {installer_path}", BRIGHT_CYAN))
                safe_print_unicode(colorize("After installation, restart DSTerminal", BRIGHT_CYAN))
                return True
                
            except Exception as e:
                safe_print_unicode(colorize(f"Failed to launch installer: {e}", BRIGHT_RED))
                safe_print_unicode(colorize(f"Please run manually: {installer_path}", BRIGHT_YELLOW))
                return False
        else:
            safe_print_unicode(colorize(f"Installer saved to: {installer_path}", BRIGHT_YELLOW))
            return True

    def display_hacker_interface(self, current_version, latest_version=None):
        """Display a hacker-style visibility interface with scrolling updates"""
        
        console = self.console
        
        try:
            if RICH_AVAILABLE and console:
                console.clear()
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass
        
        if RICH_AVAILABLE and console:
            layout = Layout()
            layout.split(
                Layout(name="header", size=6),
                Layout(name="main", size=30),
                Layout(name="footer", size=4)
            )
            
            # ===================== HEADER SECTION =====================
            header_content = Panel(
                Align.center(
                    f"""[bold cyan]### DSTERMINAL UPDATE MODULE v4.0 ###[/bold cyan]
[dim]System: {platform.system()} {platform.machine()}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Current Version: v{current_version}[/dim]"""
                ),
                border_style="cyan",
                box=box.DOUBLE_EDGE,
                height=6
            )
            layout["header"].update(header_content)
            
            # ===================== MAIN CONTENT =====================
            update_table = Table(box=box.SIMPLE, border_style="green", show_header=True)
            update_table.add_column(">>", style="green", width=3)
            update_table.add_column("UPDATE STATUS", style="cyan", width=35)
            update_table.add_column("PROGRESS", style="yellow", width=20)
            update_table.add_column("TIME", style="dim", width=10)
            
            for i in range(min(20, len(self.update_messages))):
                progress = random.randint(0, 100)
                bar = "#" * (progress // 5) + "." * (20 - (progress // 5))
                update_table.add_row(
                    "o",
                    self.update_messages[i][:35],
                    f"{bar} {progress:3d}%",
                    datetime.now().strftime("%H:%M:%S")
                )
            
            layout["main"].update(Panel(
                update_table,
                title="[bold green][*] CHECKING REQUIRED PACKAGES AND SECURITY MODULES[/bold green]",
                border_style="green",
                box=box.HEAVY_EDGE,
                height=30
            ))
            
            # ===================== FOOTER SECTION =====================
            footer_text = """
Press [yellow]Ctrl+C[/yellow] to cancel updates - [yellow]Security Protocol Active[/yellow] - [green]Update Engine Ready[/green]"""
            layout["footer"].update(Panel(
                Align.center(footer_text),
                border_style="dim",
                height=4
            ))
            
            console.print(layout)
            
            safe_print_unicode(colorize("\n[+] INITIALIZING UPDATE PROCESS...", BRIGHT_CYAN))
            
            with Live(refresh_per_second=4, console=console, transient=False) as live:
                
                for i in range(100):
                    message = self.update_messages[i % len(self.update_messages)]
                    
                    progress = random.randint(0, 100)
                    bar = "#" * (progress // 5) + "." * (20 - (progress // 5))
                    
                    new_table = Table(box=box.SIMPLE, border_style="green", show_header=True)
                    new_table.add_column(">>", style="green", width=3)
                    new_table.add_column("UPDATE STATUS", style="cyan", width=35)
                    new_table.add_column("PROGRESS", style="yellow", width=20)
                    new_table.add_column("TIME", style="dim", width=10)
                    
                    start_idx = max(0, i - 14)
                    for j in range(start_idx, i + 1):
                        if j < len(self.update_messages):
                            msg = self.update_messages[j % len(self.update_messages)]
                            p = random.randint(0, 100)
                            b = "#" * (p // 5) + "." * (20 - (p // 5))
                            if j == i:
                                new_table.add_row(
                                    ">>",
                                    f"[bold green]{msg[:35]}[/bold green]",
                                    f"[bold yellow]{b} {p:3d}%[/bold yellow]",
                                    datetime.now().strftime("%H:%M:%S")
                                )
                            else:
                                new_table.add_row(
                                    "o",
                                    msg[:35],
                                    f"{b} {p:3d}%",
                                    datetime.now().strftime("%H:%M:%S")
                                )
                    
                    layout["main"].update(Panel(
                        new_table,
                        title=f"[bold green][*] CHECKING REQUIRED PACKAGES AND SECURITY MODULES ({i+1}/100)[/bold green]",
                        border_style="green",
                        box=box.HEAVY_EDGE,
                        height=30
                    ))
                    
                    layout["footer"].update(Panel(
                        Align.center(
                            f"Processing update {i+1}/100 - [yellow]{progress}%[/yellow] complete - Press [yellow]Ctrl+C[/yellow] to cancel"
                        ),
                        border_style="dim",
                        height=4
                    ))
                    
                    live.update(layout)
                    
                    if i < 20:
                        time.sleep(0.15)
                    elif i < 50:
                        time.sleep(0.25)
                    elif i < 80:
                        time.sleep(0.35)
                    else:
                        time.sleep(0.20)
                    
                    if random.random() < 0.1:
                        time.sleep(0.1)
                
                completion_table = Table(box=box.SIMPLE, border_style="green", show_header=True)
                completion_table.add_column(">>", style="green", width=3)
                completion_table.add_column("UPDATE STATUS", style="cyan", width=35)
                completion_table.add_column("PROGRESS", style="yellow", width=20)
                completion_table.add_column("TIME", style="dim", width=10)
                
                for j in range(max(0, len(self.update_messages) - 15), len(self.update_messages)):
                    msg = self.update_messages[j]
                    completion_table.add_row(
                        "✓",
                        f"[green]{msg[:35]}[/green]",
                        "[green]#################### 100%[/green]",
                        datetime.now().strftime("%H:%M:%S")
                    )
                
                layout["main"].update(Panel(
                    completion_table,
                    title="[bold green]✓ UPDATE SCAN COMPLETE[/bold green]",
                    border_style="green",
                    box=box.HEAVY_EDGE,
                    height=30
                ))
                
                layout["footer"].update(Panel(
                    Align.center(
                        f"[bold green]✓ SCAN COMPLETED SUCCESSFULLY! Checking for available updates...[/bold green]"
                    ),
                    border_style="green",
                    height=4
                ))
                
                live.update(layout)
                time.sleep(2)
        else:
            # Fallback for when rich is not available
            safe_print_unicode(colorize("\n=== DSTERMINAL UPDATE MODULE v4.0 ===", BRIGHT_CYAN))
            safe_print_unicode(colorize(f"System: {platform.system()} {platform.machine()}", BRIGHT_CYAN))
            safe_print_unicode(colorize(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", BRIGHT_CYAN))
            safe_print_unicode(colorize(f"Current Version: v{current_version}", BRIGHT_GREEN))
            safe_print_unicode(colorize("\n[+] INITIALIZING UPDATE PROCESS...", BRIGHT_CYAN))
            
            for i in range(50):
                msg = self.update_messages[i % len(self.update_messages)]
                progress = random.randint(0, 100)
                bar = "#" * (progress // 5) + "." * (20 - (progress // 5))
                safe_print_unicode(f"\r{msg[:40]} [{bar}] {progress}%")
                time.sleep(0.2)
            safe_print_unicode(colorize("\n✓ UPDATE SCAN COMPLETE!", BRIGHT_GREEN))

    def check_updates(self):
        """Cinematic update check with real GitHub API integration"""
        
        import time
        import random
        import subprocess
        import os
        import platform
        import tempfile
        from datetime import datetime

        console = self.console

        # ===================== ANIMATIONS =====================
        def hacker_animation():
            symbols = "###++++--..  "
            try:
                width = min(console.size.width if hasattr(console, 'size') else 80, 1500)
            except:
                width = 80
            for _ in range(3):
                try:
                    line = "".join(random.choice(symbols) for _ in range(min(width, 80)))
                    safe_print_unicode(colorize(line, BRIGHT_GREEN))
                    time.sleep(1.05)
                except:
                    time.sleep(1.05)

        def satellite_scan():
            frames = ["[+]", "[*]", "[-]", "[+]", "[*]", "[-]"]
            if RICH_AVAILABLE and console:
                with Progress(
                    SpinnerColumn(style="cyan"),
                    TextColumn("[bold blue]{task.description}"),
                    transient=True,
                    console=console
                ) as progress:
                    task = progress.add_task("Establishing secure connection...", total=100)
                    for i in range(100):
                        progress.update(task, advance=1,
                                        description=f"{frames[i % len(frames)]} Retrieving files {i}%")
                        time.sleep(0.07)
            else:
                for i in range(20):
                    safe_print_unicode(f"\r{frames[i % len(frames)]} Retrieving files {i*5}%")
                    time.sleep(0.1)
                safe_print_unicode("")

        def version_comparison_animation(current_ver, latest_ver):
            if RICH_AVAILABLE and console:
                with Live(refresh_per_second=10, console=console, transient=True) as live:
                    for i in range(1, 4):
                        bar = "#" * (i * 8)
                        live.update(
                            Panel(
                                f"[bold cyan]Comparing Versions[/]\n\n"
                                f"[yellow]Current:[/] v{current_ver}\n"
                                f"[white]{bar:30}[/]\n\n"
                                f"[green]Latest:[/] v{latest_ver}\n"
                                f"[white]{bar:30}[/]",
                                border_style="cyan",
                                width=50
                            )
                        )
                        time.sleep(1.05)
            else:
                for i in range(1, 4):
                    bar = "#" * (i * 8)
                    safe_print_unicode(colorize("\nComparing Versions", BRIGHT_CYAN))
                    safe_print_unicode(colorize(f"Current: v{current_ver}", BRIGHT_YELLOW))
                    safe_print_unicode(f"{bar:30}")
                    safe_print_unicode(colorize(f"Latest: v{latest_ver}", BRIGHT_GREEN))
                    safe_print_unicode(f"{bar:30}")
                    time.sleep(1.05)

        # ===================== UPDATE LOGIC =====================
        def parse_version(v):
            parts = [int(p) if p.isdigit() else 0 for p in str(v).lstrip("vV").split(".")]
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts)

        # ===================== MAIN FLOW =====================
        try:
            current_version = self.config.get("CURRENT_VERSION", "4.0.0.113").lstrip("v")
            
            # ===================== HACKER INTERFACE =====================
            self.display_hacker_interface(current_version)
            
            if RICH_AVAILABLE and console:
                console.print(Panel(
                    Align.center("[bold cyan][*] DSTERMINAL UPDATE PROTOCOL [*][/bold cyan]"),
                    border_style="cyan"
                ))
            else:
                safe_print_unicode(colorize("\n=== DSTERMINAL UPDATE PROTOCOL ===", BRIGHT_CYAN))
            
            hacker_animation()
            satellite_scan()
            
            if RICH_AVAILABLE and console:
                version_table = Table(box=box.SIMPLE, border_style="blue")
                version_table.add_column("Component", style="cyan")
                version_table.add_column("Version", style="green")
                version_table.add_row("Current Installation", f"v{current_version}")
                version_table.add_row("System", platform.system())
                version_table.add_row("Architecture", platform.machine())
                
                console.print(Panel(version_table, title="[bold][+] SYSTEM STATUS[/bold]", border_style="blue"))
            else:
                safe_print_unicode(colorize("\n=== SYSTEM STATUS ===", BRIGHT_CYAN))
                safe_print_unicode(colorize(f"Current Installation: v{current_version}", BRIGHT_GREEN))
                safe_print_unicode(colorize(f"System: {platform.system()}", BRIGHT_CYAN))
                safe_print_unicode(colorize(f"Architecture: {platform.machine()}", BRIGHT_CYAN))
            
            safe_print_unicode(colorize("\n[*] Checking Modules for available updates...", BRIGHT_CYAN))
            
            try:
                latest = self._check_github_release()
            except Exception as e:
                if RICH_AVAILABLE and console:
                    console.print(Panel(
                        f"[bold red]UPDATE CHECK FAILED[/]\n\n"
                        f"[yellow]{str(e)}[/yellow]\n\n"
                        f"[dim]- Please check your internet connection\n"
                        f"- Verify that you're already using Updated version or if Update Module exists[/dim]\n",
                        border_style="red",
                    ))
                else:
                    safe_print_unicode(colorize(f"UPDATE CHECK FAILED: {str(e)}", BRIGHT_RED))
                return False
            
            if not latest:
                if RICH_AVAILABLE and console:
                    console.print(Panel(
                        "[yellow]⚠️ No update information available[/yellow]",
                        border_style="yellow"
                    ))
                else:
                    safe_print_unicode(colorize("No update information available", BRIGHT_YELLOW))
                return False
            
            version_comparison_animation(current_version, latest['version'])
            
            current_tuple = parse_version(current_version)
            latest_tuple = parse_version(latest['version'])
            
            if latest_tuple > current_tuple:
                if RICH_AVAILABLE and console:
                    console.print(Panel(
                        f"[bold red][!] UPDATES ARE AVAILABLE! [!][/bold red]\n\n"
                        f"[yellow]Current:[/yellow] v{current_version}\n"
                        f"[green]Latest:[/green] v{latest['version']}\n"
                        f"[cyan]Released:[/cyan] {latest.get('published_at', 'Unknown')}\n\n",
                        border_style="red",
                        width=90,
                        padding=(1, 2)
                    ))
                    
                    safe_print_unicode(colorize("Release Notes:", BRIGHT_CYAN))
                    if latest.get('notes'):
                        if RICH_AVAILABLE and console:
                            md = Markdown(latest['notes'])
                            console.print(md)
                        else:
                            safe_print_unicode(latest['notes'])
                    else:
                        safe_print_unicode(colorize("No release notes available", BRIGHT_YELLOW))
                        
                    try:
                        choice = input(colorize("\nDownload and install update now? (y/N): ", BRIGHT_CYAN)).lower()
                    except:
                        choice = 'n'
                    
                    if choice == 'y':
                        return self.perform_update(latest)
                    else:
                        safe_print_unicode(colorize("Update postponed", BRIGHT_YELLOW))
                        return False
                else:
                    safe_print_unicode(colorize(f"\n[!] UPDATES ARE AVAILABLE!", BRIGHT_RED))
                    safe_print_unicode(colorize(f"Current: v{current_version}", BRIGHT_YELLOW))
                    safe_print_unicode(colorize(f"Latest: v{latest['version']}", BRIGHT_GREEN))
                    safe_print_unicode(colorize(f"Released: {latest.get('published_at', 'Unknown')}", BRIGHT_CYAN))
                    
                    try:
                        choice = input(colorize("\nDownload and install update now? (y/N): ", BRIGHT_CYAN)).lower()
                    except:
                        choice = 'n'
                    
                    if choice == 'y':
                        return self.perform_update(latest)
                    else:
                        safe_print_unicode(colorize("Update postponed", BRIGHT_YELLOW))
                        return False
            
            else:
                if RICH_AVAILABLE and console:
                    console.print(Panel(
                        Align.center(
                            f"[bold green]✓ DSTERMINAL IS UP TO DATE![/bold green]\n\n"
                            f"[dim]Version: v{current_version}\n"
                            f"Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
                        ),
                        border_style="green",
                        width=60
                    ))
                else:
                    safe_print_unicode(colorize("\n✓ DSTERMINAL IS UP TO DATE!", BRIGHT_GREEN))
                    safe_print_unicode(colorize(f"Version: v{current_version}", BRIGHT_CYAN))
                    safe_print_unicode(colorize(f"Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", BRIGHT_CYAN))
                
                # ============================================================
                # FIX: ADD PAUSE BEFORE EXITING
                # ============================================================
                safe_print_unicode("\n" + colorize("Press Enter to exit...", BRIGHT_YELLOW))
                try:
                    input()
                except:
                    pass
                return True
            
        except KeyboardInterrupt:
            safe_print_unicode(colorize("\nUpdate cancelled by user", BRIGHT_YELLOW))
            return True
        except Exception as e:
            if RICH_AVAILABLE and console:
                console.print(Panel(
                    f"[bold red]UPDATE ERROR[/]\n\n{str(e)}",
                    border_style="red"
                ))
            else:
                safe_print_unicode(colorize(f"UPDATE ERROR: {str(e)}", BRIGHT_RED))
            import traceback
            traceback.print_exc()
            
            # ============================================================
            # FIX: ADD PAUSE ON ERROR TOO
            # ============================================================
            safe_print_unicode("\n" + colorize("Press Enter to exit...", BRIGHT_YELLOW))
            try:
                input()
            except:
                pass
            return False


# ================================================================
# ONLY RUN THIS WHEN THE FILE IS EXECUTED DIRECTLY, NOT WHEN IMPORTED
# ================================================================
if __name__ == "__main__":
    class Config:
        def __init__(self):
            self.config = {
                "CURRENT_VERSION": "4.0.0.113",
                "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "")
            }
        
        def get(self, key, default=None):
            return self.config.get(key, default)
    
    config = Config()
    update_manager = UpdateManager(config)
    update_manager.check_updates()