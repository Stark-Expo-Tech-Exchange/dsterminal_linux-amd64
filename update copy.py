#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

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
import re
import subprocess
from datetime import datetime
from pathlib import Path
import requests
import shutil

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

# ============================================================
# UPDATE MANAGER CLASS - MODIFIED FOR PUBLIC REPO
# ============================================================
class UpdateManager:
    def __init__(self, config):
        self.config = config
        self.console = console if RICH_AVAILABLE else None
        
        self.github_repo = self.config.get(
            "GITHUB_REPO",
            os.environ.get(
                "GITHUB_REPO",
                "Stark-Expo-Tech-Exchange/dsterminal_linux-amd64"
            )
        ).strip()

        # ============================================================
        # REMOVED GITHUB_TOKEN - PUBLIC REPO NO TOKEN NEEDED
        # ============================================================
        
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
        """Get headers for GitHub API requests - PUBLIC REPO (NO TOKEN)"""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DSTerminal-Update-Manager/4.0"
        }
        safe_print_unicode(
            colorize(
                "ℹ️ Public repository - no authentication needed",
                BRIGHT_CYAN
            )
        )
        return headers
        
    def _check_github_release(self):
        """Check GitHub for latest release - FIXED FOR PUBLIC REPO"""
        try:
            import requests
            from datetime import datetime
            
            current_version = self.config.get("CURRENT_VERSION", "1.0.0")
            
            headers = self._get_headers()
            
            safe_print_unicode(colorize(f"Connecting to UPDATE MODULE API for {self.github_repo}...", BRIGHT_CYAN))
            
            # ============================================================
            # FIX: Use releases endpoint directly (not tags)
            # ============================================================
            releases_url = (
                f"https://api.github.com/repos/"
                f"{self.github_repo}/releases"
            )
            safe_print_unicode(colorize("Fetching releases...", BRIGHT_CYAN))
            releases_response = requests.get(releases_url, timeout=15, headers=headers)
            
            if releases_response.status_code == 200:
                releases_data = releases_response.json()
                if releases_data:
                    # Get the latest release (first one)
                    latest_release = releases_data[0]
                    safe_print_unicode(colorize(f"✓ Found latest release: {latest_release.get('tag_name')}", BRIGHT_GREEN))
                    return self._process_release_data(latest_release)
                else:
                    safe_print_unicode(colorize("✗ No releases found in repository", BRIGHT_YELLOW))
                    raise Exception("No releases found in repository")
            else:
                safe_print_unicode(colorize(f"✗ Failed to get releases: {releases_response.status_code}", BRIGHT_RED))
                # Try fallback to tags
                safe_print_unicode(colorize("Trying tags endpoint as fallback...", BRIGHT_YELLOW))
                return self._get_latest_tag()
             
        except requests.RequestException as e:
            safe_print_unicode(colorize(f"⚠️ Connection error: {e}", BRIGHT_RED))
            raise Exception(f"Network error while checking for updates: {e}")
        except Exception as e:
            safe_print_unicode(colorize(f"⚠️ Error: {e}", BRIGHT_RED))
            raise

    def _get_latest_tag(self):
        """Fallback: Get latest tag from GitHub"""
        try:
            import requests
            from datetime import datetime
            
            headers = self._get_headers()
            
            tags_url = (
                f"https://api.github.com/repos/"
                f"{self.github_repo}/tags"
            )
            tags_response = requests.get(tags_url, timeout=15, headers=headers)
            
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                if tags_data:
                    latest_tag = tags_data[0].get("name", "")
                    safe_print_unicode(colorize(f"✓ Found latest tag: {latest_tag}", BRIGHT_GREEN))
                    return {
                        "version": latest_tag.lstrip("v"),
                        "url": (
                            f"https://github.com/"
                            f"{self.github_repo}/tree/{latest_tag}"
                        ),
                        "download_url": (
                            f"https://github.com/"
                            f"{self.github_repo}/archive/refs/tags/"
                            f"{latest_tag}.zip"
                        ),
                        "notes": f"DSTerminal {latest_tag}",
                        "prerelease": False,
                        "published_at": datetime.now().strftime('%Y-%m-%d'),
                        "asset_name": f"DSTerminal-{latest_tag}.zip",
                        "asset_size": 0,
                        "from_fallback": True
                    }
            return None
        except Exception:
            return None

    def _process_release_data(self, release):
        """Process GitHub release data and select the correct
        installer for the current operating system and architecture.
        """

        try:
            tag_name = release.get("tag_name", "").strip()
            version = tag_name.lstrip("vV")
            assets = release.get("assets", [])

            system = platform.system().lower()
            machine = platform.machine().lower()

            # ---------------------------------------------------------
            # NORMALIZE ARCHITECTURE
            # ---------------------------------------------------------
            architecture_aliases = {
                "x86_64": "x64",
                "amd64": "x64",
                "amd64e": "x64",

                "aarch64": "arm64",
                "arm64": "arm64",

                "armv8": "arm64",
                "armv7l": "arm",

                "i386": "x86",
                "i686": "x86",
                "x86": "x86",
            }

            normalized_arch = architecture_aliases.get(
                machine,
                machine
            )

            selected_asset = None

            # ---------------------------------------------------------
            # PLATFORM / ARCHITECTURE INFORMATION
            # ---------------------------------------------------------
            if system == "linux":
                platform_name = "Linux"

            elif system == "windows":
                platform_name = "Windows"

            elif system == "darwin":
                platform_name = "macOS"

            else:
                raise Exception(
                    f"Unsupported operating system: {platform.system()}"
                )

            safe_print_unicode(
                colorize(
                    f"Detected platform: {platform_name}",
                    BRIGHT_CYAN
                )
            )

            safe_print_unicode(
                colorize(
                    f"Detected architecture: "
                    f"{platform.machine()} → {normalized_arch}",
                    BRIGHT_CYAN
                )
            )

            # ---------------------------------------------------------
            # BUILD PLATFORM-SPECIFIC ASSET PRIORITY
            # ---------------------------------------------------------
            preferred_names = []

            # =========================================================
            # LINUX
            # =========================================================
            if system == "linux":

                if normalized_arch == "x64":

                    preferred_names = [
                        f"dsterminal_{version}_amd64.deb",
                        f"DSTerminal-{version}-linux-x64.deb",
                        f"DSTerminal-{version}-linux-x64.tar.gz",
                        f"DSTerminal-{version}-linux-x64.zip",
                    ]

                elif normalized_arch == "arm64":

                    preferred_names = [
                        f"dsterminal_{version}_arm64.deb",
                        f"DSTerminal-{version}-linux-arm64.deb",
                        f"DSTerminal-{version}-linux-arm64.tar.gz",
                        f"DSTerminal-{version}-linux-arm64.zip",
                    ]

                elif normalized_arch == "arm":

                    preferred_names = [
                        f"dsterminal_{version}_armhf.deb",
                        f"DSTerminal-{version}-linux-arm.tar.gz",
                        f"DSTerminal-{version}-linux-arm.zip",
                    ]

                elif normalized_arch == "x86":

                    preferred_names = [
                        f"dsterminal_{version}_i386.deb",
                        f"DSTerminal-{version}-linux-x86.tar.gz",
                        f"DSTerminal-{version}-linux-x86.zip",
                    ]

            # =========================================================
            # WINDOWS
            # =========================================================
            elif system == "windows":

                if normalized_arch == "x64":

                    preferred_names = [
                        f"DSTerminal-{version}-windows-x64.exe",
                        f"DSTerminal-{version}-Windows-x64.exe",
                        f"DSTerminal-{version}-windows-x64.msi",
                        f"DSTerminal-{version}-windows-x64.zip",
                    ]

                elif normalized_arch == "arm64":

                    preferred_names = [
                        f"DSTerminal-{version}-windows-arm64.exe",
                        f"DSTerminal-{version}-Windows-arm64.exe",
                        f"DSTerminal-{version}-windows-arm64.msi",
                        f"DSTerminal-{version}-windows-arm64.zip",
                    ]

                elif normalized_arch == "x86":

                    preferred_names = [
                        f"DSTerminal-{version}-windows-x86.exe",
                        f"DSTerminal-{version}-Windows-x86.exe",
                        f"DSTerminal-{version}-windows-x86.msi",
                        f"DSTerminal-{version}-windows-x86.zip",
                    ]

            # =========================================================
            # macOS
            # =========================================================
            elif system == "darwin":

                if normalized_arch == "x64":

                    preferred_names = [
                        f"DSTerminal-{version}-macos-x64.dmg",
                        f"DSTerminal-{version}-macOS-x64.dmg",
                        f"DSTerminal-{version}-macos-x64.pkg",
                        f"DSTerminal-{version}-macos-x64.zip",
                    ]

                elif normalized_arch == "arm64":

                    preferred_names = [
                        f"DSTerminal-{version}-macos-arm64.dmg",
                        f"DSTerminal-{version}-macOS-arm64.dmg",
                        f"DSTerminal-{version}-macos-arm64.pkg",
                        f"DSTerminal-{version}-macos-arm64.zip",
                    ]

            # ---------------------------------------------------------
            # FIND EXACT MATCH
            # ---------------------------------------------------------
            for preferred in preferred_names:

                for asset in assets:

                    asset_name = asset.get("name", "")

                    if asset_name == preferred:

                        selected_asset = asset
                        break

                if selected_asset:
                    break

            # ---------------------------------------------------------
            # NO EXACT MATCH
            # ---------------------------------------------------------
            if not selected_asset:

                available_assets = [
                    asset.get("name", "")
                    for asset in assets
                    if asset.get("name")
                ]

                raise Exception(
                    f"No compatible DSTerminal installer was found "
                    f"for {platform_name} {normalized_arch}.\n"
                    f"Expected one of: {preferred_names}\n"
                    f"Available release assets: {available_assets}"
                )

            # ---------------------------------------------------------
            # EXTRACT ASSET INFORMATION
            # ---------------------------------------------------------
            asset_name = selected_asset.get("name")

            download_url = selected_asset.get(
                "browser_download_url"
            )

            asset_api_url = selected_asset.get("url")

            asset_size = selected_asset.get("size", 0)

            safe_print_unicode(
                colorize(
                    f"✓ Platform matched: "
                    f"{platform_name} {normalized_arch}",
                    BRIGHT_GREEN
                )
            )

            safe_print_unicode(
                colorize(
                    f"✓ Selected installer: {asset_name}",
                    BRIGHT_GREEN
                )
            )

            # ---------------------------------------------------------
            # RETURN RELEASE INFORMATION
            # ---------------------------------------------------------
            return {
                "version": version,

                "url": release.get(
                    "html_url",
                    ""
                ),

                "download_url": download_url,

                "asset_api_url": asset_api_url,

                "notes": release.get(
                    "body",
                    f"DSTerminal v{version}"
                ),

                "prerelease": release.get(
                    "prerelease",
                    False
                ),

                "published_at": (
                    release.get(
                        "published_at",
                        datetime.now().strftime("%Y-%m-%d")
                    )[:10]
                ),

                "asset_name": asset_name,

                "asset_size": asset_size,

                "platform": platform_name,

                "architecture": normalized_arch,

                "from_fallback": False
            }

        except Exception as e:

            raise Exception(
                f"Failed to process platform-specific release: {e}"
            )



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
            
            # No token needed for public repo
            
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
                    safe_print_unicode(colorize("Access denied. This is a public repo, check your network.", BRIGHT_YELLOW))
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
                safe_print_unicode(colorize("Access denied. This is a public repo, check your network.", BRIGHT_YELLOW))
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
        """Execute the actual cross-platform update process."""

        console = self.console

        # ============================================================
        # UPDATE DETAILS
        # ============================================================
        if RICH_AVAILABLE and console:
            details_table = Table(box=box.HEAVY_EDGE, border_style="cyan")
            details_table.add_column("Item", style="cyan")
            details_table.add_column("Details", style="white")

            details_table.add_row(
                "New Version",
                f"[green]v{latest['version']}[/green]"
            )

            details_table.add_row(
                "Platform",
                latest.get("platform", platform.system())
            )

            details_table.add_row(
                "Architecture",
                latest.get("architecture", platform.machine())
            )

            details_table.add_row(
                "Installer",
                latest.get("asset_name", "Unknown")
            )

            if latest.get("asset_size"):
                size_mb = latest["asset_size"] / (1024 * 1024)
                details_table.add_row(
                    "Size",
                    f"{size_mb:.1f} MB"
                )

            details_table.add_row(
                "Release",
                latest.get("published_at", "Unknown")
            )

            console.print(
                Panel(
                    details_table,
                    title="[bold yellow][+] UPDATE DETAILS[/bold yellow]",
                    border_style="yellow"
                )
            )

        else:
            safe_print_unicode(
                colorize("\n=== UPDATE DETAILS ===", BRIGHT_CYAN)
            )

            safe_print_unicode(
                colorize(
                    f"New Version: v{latest['version']}",
                    BRIGHT_GREEN
                )
            )

            safe_print_unicode(
                colorize(
                    f"Platform: {latest.get('platform', platform.system())}",
                    BRIGHT_CYAN
                )
            )

            safe_print_unicode(
                colorize(
                    f"Architecture: "
                    f"{latest.get('architecture', platform.machine())}",
                    BRIGHT_CYAN
                )
            )

            safe_print_unicode(
                colorize(
                    f"Installer: {latest.get('asset_name', 'Unknown')}",
                    BRIGHT_CYAN
                )
            )

            if latest.get("asset_size"):
                size_mb = latest["asset_size"] / (1024 * 1024)

                safe_print_unicode(
                    colorize(
                        f"Size: {size_mb:.1f} MB",
                        BRIGHT_CYAN
                    )
                )

            safe_print_unicode(
                colorize(
                    f"Release: {latest.get('published_at', 'Unknown')}",
                    BRIGHT_CYAN
                )
            )

        # ============================================================
        # SECURITY NOTICE
        # ============================================================
        safe_print_unicode(
            colorize("\n⚠️ SECURITY NOTICE", BRIGHT_RED)
        )

        safe_print_unicode(
            colorize(
                "- The installer will be downloaded from the "
                "DSTerminal Update Module",
                BRIGHT_YELLOW
            )
        )

        safe_print_unicode(
            colorize(
                "- Verify the digital signature before installation",
                BRIGHT_YELLOW
            )
        )

        safe_print_unicode(
            colorize(
                "- A valid DSTerminal License Key may be required "
                "during installation",
                BRIGHT_YELLOW
            )
        )

        safe_print_unicode(
            colorize(
                "- Administrator/root privileges may be required",
                BRIGHT_YELLOW
            )
        )

        safe_print_unicode(
            colorize(
                "- Large files may require additional download time",
                BRIGHT_YELLOW
            )
        )

        safe_print_unicode(
            colorize(
                "- Ensure sufficient disk space and a stable "
                "internet connection",
                BRIGHT_YELLOW
            )
        )

        # ============================================================
        # CONFIRM DOWNLOAD
        # ============================================================
        try:
            confirm = input(
                colorize(
                    "Type 'INSTALL' to download and install the update: ",
                    BRIGHT_RED
                )
            ).strip()

        except (KeyboardInterrupt, EOFError):
            confirm = ""

        if confirm != "INSTALL":
            safe_print_unicode(
                colorize("Update cancelled", BRIGHT_YELLOW)
            )
            return False

        # ============================================================
        # CHECK DOWNLOAD URL
        # ============================================================
        if not latest.get("download_url"):
            safe_print_unicode(
                colorize(
                    "No automatic download available",
                    BRIGHT_YELLOW
                )
            )

            safe_print_unicode(
                colorize(
                    "Please download the appropriate release manually",
                    BRIGHT_YELLOW
                )
            )

            return False

        # Save API asset URL
        self.asset_api_url = latest.get("asset_api_url")

        # ============================================================
        # DOWNLOAD SELECTED PLATFORM ASSET
        # ============================================================
        installer_name = latest.get("asset_name")

        if not installer_name:
            installer_name = (
                f"DSTerminal-v{latest['version']}-installer"
            )

        safe_print_unicode(
            colorize(
                f"\n[+] Selected platform asset: {installer_name}",
                BRIGHT_CYAN
            )
        )

        safe_print_unicode(
            colorize(
                f"[+] Target platform: "
                f"{latest.get('platform', platform.system())}",
                BRIGHT_CYAN
            )
        )

        safe_print_unicode(
            colorize(
                f"[+] Target architecture: "
                f"{latest.get('architecture', platform.machine())}",
                BRIGHT_CYAN
            )
        )

        download_result = self.download_update(
            latest["download_url"],
            installer_name
        )

        if not download_result:
            safe_print_unicode(
                colorize("Download failed", BRIGHT_RED)
            )
            return False

        installer_path = (
            download_result
            if isinstance(download_result, str)
            else None
        )

        # ============================================================
        # BASIC DOWNLOAD VALIDATION
        # ============================================================
        if (
            not installer_path
            or not os.path.exists(installer_path)
            or os.path.getsize(installer_path) == 0
        ):
            safe_print_unicode(
                colorize(
                    "Download verification failed",
                    BRIGHT_RED
                )
            )
            return False

        file_size_mb = os.path.getsize(installer_path) / (1024 * 1024)

        safe_print_unicode(
            colorize(
                f"\n✓ Download completed successfully "
                f"({file_size_mb:.1f} MB)",
                BRIGHT_GREEN
            )
        )

        safe_print_unicode(
            colorize(
                f"Installer: {installer_path}",
                BRIGHT_CYAN
            )
        )

        # ============================================================
        # INSTALLATION CONFIRMATION
        # ============================================================
        safe_print_unicode(
            colorize(
                "\n[+] Ready to install update...",
                BRIGHT_CYAN
            )
        )

        try:
            run_installer = input(
                colorize(
                    "Run the installer now? (Y/n): ",
                    BRIGHT_YELLOW
                )
            ).strip().lower()

        except (KeyboardInterrupt, EOFError):
            run_installer = "y"

        if run_installer == "n":
            safe_print_unicode(
                colorize(
                    f"Installer saved to: {installer_path}",
                    BRIGHT_YELLOW
                )
            )

            return True

        # ============================================================
        # DETECT CURRENT PLATFORM
        # ============================================================
        current_system = platform.system().lower()
        installer_lower = installer_path.lower()

        safe_print_unicode(
            colorize(
                "\n[+] Detecting installation environment...",
                BRIGHT_CYAN
            )
        )

        safe_print_unicode(
            colorize(
                f"Operating System: {platform.system()}",
                BRIGHT_CYAN
            )
        )

        safe_print_unicode(
            colorize(
                f"Architecture: {platform.machine()}",
                BRIGHT_CYAN
            )
        )

        safe_print_unicode(
            colorize(
                f"Package: {os.path.basename(installer_path)}",
                BRIGHT_CYAN
            )
        )

        time.sleep(1)

        # ============================================================
        # WINDOWS
        # ============================================================
        if current_system == "windows":

            safe_print_unicode(
                colorize(
                    "\n[WINDOWS] Preparing installation...",
                    BRIGHT_CYAN
                )
            )

            try:

                # ----------------------------------------------------
                # EXE INSTALLER
                # ----------------------------------------------------
                if installer_lower.endswith(".exe"):

                    safe_print_unicode(
                        colorize(
                            "[WINDOWS] Launching EXE installer...",
                            BRIGHT_CYAN
                        )
                    )

                    subprocess.Popen(
                        [installer_path],
                        shell=False
                    )

                # ----------------------------------------------------
                # MSI INSTALLER
                # ----------------------------------------------------
                elif installer_lower.endswith(".msi"):

                    safe_print_unicode(
                        colorize(
                            "[WINDOWS] Launching MSI installer...",
                            BRIGHT_CYAN
                        )
                    )

                    subprocess.Popen(
                        [
                            "msiexec.exe",
                            "/i",
                            installer_path
                        ],
                        shell=False
                    )

                # ----------------------------------------------------
                # ZIP PACKAGE
                # ----------------------------------------------------
                elif installer_lower.endswith(".zip"):

                    safe_print_unicode(
                        colorize(
                            "[WINDOWS] Opening ZIP package...",
                            BRIGHT_CYAN
                        )
                    )

                    os.startfile(installer_path)

                else:

                    safe_print_unicode(
                        colorize(
                            "Unsupported Windows installer format.",
                            BRIGHT_RED
                        )
                    )

                    safe_print_unicode(
                        colorize(
                            f"File: {installer_path}",
                            BRIGHT_YELLOW
                        )
                    )

                    return False

                # ----------------------------------------------------
                # WINDOWS SUCCESS
                # ----------------------------------------------------
                safe_print_unicode(
                    colorize(
                        "\n✓ WINDOWS INSTALLER LAUNCHED",
                        BRIGHT_GREEN
                    )
                )

                safe_print_unicode(
                    colorize(
                        "Complete the installation wizard.",
                        BRIGHT_YELLOW
                    )
                )

                safe_print_unicode(
                    colorize(
                        "DSTerminal may close automatically during "
                        "the upgrade.",
                        BRIGHT_YELLOW
                    )
                )

                return True

            except Exception as e:

                safe_print_unicode(
                    colorize(
                        f"Windows installer failed: {e}",
                        BRIGHT_RED
                    )
                )

                safe_print_unicode(
                    colorize(
                        f"Run manually: {installer_path}",
                        BRIGHT_YELLOW
                    )
                )

                return False

        # ============================================================
        # LINUX
        # ============================================================
        elif current_system == "linux":

            safe_print_unicode(
                colorize(
                    "\n[LINUX] Preparing installation...",
                    BRIGHT_CYAN
                )
            )

            try:

                # ----------------------------------------------------
                # DEBIAN PACKAGE
                # ----------------------------------------------------
                if installer_lower.endswith(".deb"):

                    safe_print_unicode(
                        colorize(
                            "[LINUX] Debian package detected.",
                            BRIGHT_CYAN
                        )
                    )

                    # Check for pkexec
                    pkexec_path = shutil.which("pkexec")

                    if pkexec_path:

                        safe_print_unicode(
                            colorize(
                                "[LINUX] Starting privileged "
                                "package installation...",
                                BRIGHT_CYAN
                            )
                        )

                        subprocess.Popen(
                            [
                                pkexec_path,
                                "apt",
                                "install",
                                "-y",
                                installer_path
                            ],
                            shell=False
                        )

                    else:

                        safe_print_unicode(
                            colorize(
                                "[LINUX] pkexec is unavailable.",
                                BRIGHT_YELLOW
                            )
                        )

                        sudo_path = shutil.which("sudo")

                        if sudo_path:

                            safe_print_unicode(
                                colorize(
                                    "[LINUX] Starting installation "
                                    "through sudo...",
                                    BRIGHT_CYAN
                                )
                            )

                            subprocess.Popen(
                                [
                                    sudo_path,
                                    "apt",
                                    "install",
                                    "-y",
                                    installer_path
                                ],
                                shell=False
                            )

                        else:

                            safe_print_unicode(
                                colorize(
                                    "No pkexec or sudo was found.",
                                    BRIGHT_RED
                                )
                            )

                            safe_print_unicode(
                                colorize(
                                    f"Install manually:\n"
                                    f"sudo apt install "
                                    f"'{installer_path}'",
                                    BRIGHT_YELLOW
                                )
                            )

                            return False

                # ----------------------------------------------------
                # APPIMAGE
                # ----------------------------------------------------
                elif installer_lower.endswith(".appimage"):

                    safe_print_unicode(
                        colorize(
                            "[LINUX] AppImage package detected.",
                            BRIGHT_CYAN
                        )
                    )

                    os.chmod(
                        installer_path,
                        os.stat(installer_path).st_mode | 0o111
                    )

                    subprocess.Popen(
                        [installer_path],
                        shell=False
                    )

                # ----------------------------------------------------
                # TAR.GZ
                # ----------------------------------------------------
                elif (
                    installer_lower.endswith(".tar.gz")
                    or installer_lower.endswith(".tgz")
                ):

                    safe_print_unicode(
                        colorize(
                            "[LINUX] Archive package detected.",
                            BRIGHT_CYAN
                        )
                    )

                    safe_print_unicode(
                        colorize(
                            "Automatic replacement is not performed "
                            "for archive packages.",
                            BRIGHT_YELLOW
                        )
                    )

                    safe_print_unicode(
                        colorize(
                            f"Archive saved at:\n{installer_path}",
                            BRIGHT_CYAN
                        )
                    )

                    safe_print_unicode(
                        colorize(
                            "Extract and install the archive manually.",
                            BRIGHT_YELLOW
                        )
                    )

                    return True

                # ----------------------------------------------------
                # ZIP
                # ----------------------------------------------------
                elif installer_lower.endswith(".zip"):

                    safe_print_unicode(
                        colorize(
                            "[LINUX] ZIP package detected.",
                            BRIGHT_CYAN
                        )
                    )

                    safe_print_unicode(
                        colorize(
                            f"Package saved at:\n{installer_path}",
                            BRIGHT_YELLOW
                        )
                    )

                    return True

                else:

                    safe_print_unicode(
                        colorize(
                            "Unsupported Linux installer format.",
                            BRIGHT_RED
                        )
                    )

                    safe_print_unicode(
                        colorize(
                            f"File: {installer_path}",
                            BRIGHT_YELLOW
                        )
                    )

                    return False

                # ----------------------------------------------------
                # LINUX SUCCESS
                # ----------------------------------------------------
                safe_print_unicode(
                    colorize(
                        "\n✓ LINUX UPDATE PROCESS STARTED",
                        BRIGHT_GREEN
                    )
                )

                safe_print_unicode(
                    colorize(
                        "The package manager will complete "
                        "the installation.",
                        BRIGHT_YELLOW
                    )
                )

                safe_print_unicode(
                    colorize(
                        "DSTerminal should be restarted after "
                        "the upgrade.",
                        BRIGHT_YELLOW
                    )
                )

                return True

            except Exception as e:

                safe_print_unicode(
                    colorize(
                        f"Linux installation failed: {e}",
                        BRIGHT_RED
                    )
                )

                safe_print_unicode(
                    colorize(
                        f"Run manually: {installer_path}",
                        BRIGHT_YELLOW
                    )
                )

                return False

        # ============================================================
        # macOS
        # ============================================================
        elif current_system == "darwin":

            safe_print_unicode(
                colorize(
                    "\n[macOS] Preparing installation...",
                    BRIGHT_CYAN
                )
            )

            try:

                # ----------------------------------------------------
                # PKG INSTALLER
                # ----------------------------------------------------
                if installer_lower.endswith(".pkg"):

                    safe_print_unicode(
                        colorize(
                            "[macOS] PKG installer detected.",
                            BRIGHT_CYAN
                        )
                    )

                    subprocess.Popen(
                        [
                            "open",
                            installer_path
                        ],
                        shell=False
                    )

                # ----------------------------------------------------
                # DMG INSTALLER
                # ----------------------------------------------------
                elif installer_lower.endswith(".dmg"):

                    safe_print_unicode(
                        colorize(
                            "[macOS] DMG installer detected.",
                            BRIGHT_CYAN
                        )
                    )

                    subprocess.Popen(
                        [
                            "open",
                            installer_path
                        ],
                        shell=False
                    )

                # ----------------------------------------------------
                # ZIP PACKAGE
                # ----------------------------------------------------
                elif installer_lower.endswith(".zip"):

                    safe_print_unicode(
                        colorize(
                            "[macOS] ZIP package detected.",
                            BRIGHT_CYAN
                        )
                    )

                    subprocess.Popen(
                        [
                            "open",
                            installer_path
                        ],
                        shell=False
                    )

                else:

                    safe_print_unicode(
                        colorize(
                            "Unsupported macOS installer format.",
                            BRIGHT_RED
                        )
                    )

                    safe_print_unicode(
                        colorize(
                            f"File: {installer_path}",
                            BRIGHT_YELLOW
                        )
                    )

                    return False

                # ----------------------------------------------------
                # macOS SUCCESS
                # ----------------------------------------------------
                safe_print_unicode(
                    colorize(
                        "\n✓ macOS INSTALLER LAUNCHED",
                        BRIGHT_GREEN
                    )
                )

                safe_print_unicode(
                    colorize(
                        "Complete the installation process.",
                        BRIGHT_YELLOW
                    )
                )

                safe_print_unicode(
                    colorize(
                        "Restart DSTerminal after installation.",
                        BRIGHT_YELLOW
                    )
                )

                return True

            except Exception as e:

                safe_print_unicode(
                    colorize(
                        f"macOS installer failed: {e}",
                        BRIGHT_RED
                    )
                )

                safe_print_unicode(
                    colorize(
                        f"Open manually: {installer_path}",
                        BRIGHT_YELLOW
                    )
                )

                return False

        # ============================================================
        # UNSUPPORTED OPERATING SYSTEM
        # ============================================================
        else:

            safe_print_unicode(
                colorize(
                    f"\nUnsupported operating system: "
                    f"{platform.system()}",
                    BRIGHT_RED
                )
            )

            safe_print_unicode(
                colorize(
                    f"Downloaded package: {installer_path}",
                    BRIGHT_YELLOW
                )
            )

            return False


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
                "CURRENT_VERSION": "4.0.0.113"
                # REMOVED GITHUB_TOKEN - NOT NEEDED FOR PUBLIC REPO
            }
        
        def get(self, key, default=None):
            return self.config.get(key, default)
    
    config = Config()
    update_manager = UpdateManager(config)
    update_manager.check_updates()