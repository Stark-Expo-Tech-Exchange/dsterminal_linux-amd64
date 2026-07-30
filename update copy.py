# update.py - COMPLETE FIXED VERSION WITH DOWNLOADS FOLDER
import os
import sys
import time
import random
import platform
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
import requests
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

class UpdateManager:
    def __init__(self, config):
        self.config = config
        self.console = Console()
        
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
            # Fallback to temp if Downloads doesn't exist
            self.download_dir = tempfile.gettempdir()
        
        # Initialize asset_api_url
        self.asset_api_url = None
        
    def _get_headers(self):
        """Get headers for GitHub API requests"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'DSTerminal-Update-Checker/4.0'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
            self.console.print("[dim]Using Generated DSTERMINAL token for authentication[/dim]")
        
        return headers
        
    def _check_github_release(self):
        """Check GitHub for latest release"""
        try:
            import requests
            from datetime import datetime
            
            # Get current version from config
            current_version = self.config.get("CURRENT_VERSION", "1.0.0")
            
            headers = self._get_headers()
            
            # ============================================================
            # METHOD 1: Try getting releases by tag (this works!)
            # ============================================================
            self.console.print(f"[dim]Connecting to UPDATE MODULE API for {self.github_repo}...[/dim]")
            
            # First, get all tags
            tags_url = f"https://api.github.com/repos/{self.github_repo}/tags"
            self.console.print("[dim]Fetching tags...[/dim]")
            tags_response = requests.get(tags_url, timeout=15, headers=headers)
            
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                if tags_data:
                    # Get the latest tag (first one is usually the newest)
                    latest_tag = tags_data[0].get("name", "")
                    self.console.print(f"[green]✓ Found latest tag: {latest_tag}[/green]")
                    
                    # Now get the release info for this tag
                    release_url = f"https://api.github.com/repos/{self.github_repo}/releases/tags/{latest_tag}"
                    self.console.print(f"[dim]Fetching release for tag: {latest_tag}...[/dim]")
                    release_response = requests.get(release_url, timeout=15, headers=headers)
                    
                    if release_response.status_code == 200:
                        release_data = release_response.json()
                        self.console.print(f"[green]✓ Found release: {release_data.get('tag_name')}[/green]")
                        return self._process_release_data(release_data)
                    else:
                        self.console.print(f"[yellow]No release found for tag {latest_tag}, using tag info[/yellow]")
                        # Return tag info with download URL
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
                    self.console.print("[red]❌ No tags found in repository[/red]")
                    raise Exception("No tags found in repository")
            else:
                self.console.print(f"[red]❌ Failed to get tags: {tags_response.status_code}[/red]")
                raise Exception(f"UPDATE MODULE API returned {tags_response.status_code} for tags endpoint")
             
        except requests.RequestException as e:
            self.console.print(f"[red]⚠️ Connection error: {e}[/red]")
            raise Exception(f"Network error while checking for updates: {e}")
        except Exception as e:
            self.console.print(f"[red]⚠️ Error: {e}[/red]")
            raise

    def _process_release_data(self, release):
        """Process GitHub release data into a standardized format"""
        try:
            from datetime import datetime
            
            # Extract release information
            tag_name = release.get("tag_name", "").lstrip("v")
            version = tag_name if tag_name else "0.0.0"
            
            # Find assets
            assets = release.get("assets", [])
            
            # Look for the first executable or zip file
            selected_asset = None
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe") or name.endswith(".zip"):
                    selected_asset = asset
                    break
            
            # If no exe/zip found, use the first asset
            if not selected_asset and assets:
                selected_asset = assets[0]
            
            download_url = None
            asset_api_url = None
            asset_name = None
            asset_size = 0
            
            if selected_asset:
                # Get both URLs
                download_url = selected_asset.get("browser_download_url")
                asset_api_url = selected_asset.get("url")  # API URL for private repos
                asset_name = selected_asset.get("name")
                asset_size = selected_asset.get("size", 0)
                self.console.print(f"[dim]Found asset: {asset_name} ({asset_size:,} bytes)[/dim]")

            
            return {
                "version": version,
                "url": release.get("html_url", ""),
                "download_url": download_url,
                "asset_api_url": asset_api_url,  # Store for private repo downloads
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
            
            self.console.print(f"\n[cyan]📥 Downloading update from DSTerminal Update Module...[/cyan]")
            self.console.print(f"[dim]File: {filename}[/dim]")
            
            if not url:
                self.console.print("[red]No download URL available[/red]")
                return False
            
            # Ensure the Downloads directory exists
            os.makedirs(self.download_dir, exist_ok=True)
            full_path = os.path.join(self.download_dir, filename)
            
            # If file exists, ask to overwrite
            if os.path.exists(full_path):
                overwrite = self.console.input(f"[yellow]File already exists. Overwrite? (y/N): [/]").strip().lower()
                if overwrite != 'y':
                    self.console.print("[yellow]Download cancelled[/yellow]")
                    return False
                os.remove(full_path)
            
            # First attempt: Try with asset API URL (works for both public and private)
            download_url = url
            headers = {
                'User-Agent': 'DSTerminal-Updater/4.0',
                'Accept': 'application/octet-stream'
            }
            
            # Check if we have an asset API URL to use instead
            if hasattr(self, 'asset_api_url') and self.asset_api_url:
                self.console.print("[dim]Using asset API URL for download...[/dim]")
                download_url = self.asset_api_url
                if self.github_token:
                    headers['Authorization'] = f'Bearer {self.github_token}'
                    self.console.print("[dim]Using authentication token[/dim]")
            
            self.console.print("[dim]Connecting to server...[/dim]")
            response = requests.get(
                download_url,
                headers=headers,
                stream=True,
                allow_redirects=True,
                timeout=60
            )
            
            # If asset API URL fails, try browser_download_url
            if response.status_code == 404 and download_url != url:
                self.console.print("[dim]Asset API failed, trying browser download URL...[/dim]")
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
            
            # Diagnostic output if still failing
            if response.status_code != 200:
                self.console.print(f"[dim]Status: {response.status_code}[/dim]")
                self.console.print(f"[dim]Final URL: {response.url}[/dim]")
                self.console.print(f"[dim]Content-Type: {response.headers.get('Content-Type', 'Unknown')}[/dim]")
                
                if response.status_code == 404:
                    self.console.print("[yellow]File not found. The URL might be incorrect.[/yellow]")
                    self.console.print("[dim]Try downloading manually from the GitHub releases page[/dim]")
                    return False
                elif response.status_code == 401 or response.status_code == 403:
                    self.console.print("[yellow]Authentication failed. Check your GitHub token.[/yellow]")
                    return False
            
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            with open(full_path, 'wb') as f:
                with Progress(
                    DownloadColumn(),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TransferSpeedColumn(),
                    console=self.console,
                    transient=False
                ) as progress:
                    task = progress.add_task("[green]Downloading...[/green]", total=total_size if total_size > 0 else None)
                    
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress.update(task, advance=len(chunk))
                            else:
                                progress.update(task, description=f"[green]Downloading... {downloaded//1024}KB[/green]")
            
            if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                file_size = os.path.getsize(full_path)
                self.console.print(f"[green]✓ Download complete![/green]")
                self.console.print(f"[dim]Saved to: {full_path}[/dim]")
                self.console.print(f"[dim]Size: {file_size:,} bytes ({file_size/(1024*1024):.1f} MB)[/dim]")
                return full_path
            else:
                self.console.print("[red]Download failed - file is empty or not created[/red]")
                return False
                
        except requests.exceptions.HTTPError as e:
            self.console.print(f"[red]✗ HTTP Error: {e.response.status_code}[/red]")
            if e.response.status_code == 404:
                self.console.print("[yellow]File not found. The URL might be incorrect.[/yellow]")
                self.console.print("[dim]Try downloading manually from: https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/releases[/dim]")
            elif e.response.status_code == 401 or e.response.status_code == 403:
                self.console.print("[yellow]Authentication failed. Check your GitHub token.[/yellow]")
            return False
        except requests.exceptions.Timeout:
            self.console.print("[red]✗ Download timeout - Connection took too long[/red]")
            return False
        except requests.exceptions.ConnectionError:
            self.console.print("[red]✗ Connection error - Check your internet connection[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]✗ Download failed: {e}[/red]")
            return False
        
    def perform_update(self, latest):
        """Execute the actual update process"""
        
        console = self.console
        
        details_table = Table(box=box.HEAVY_EDGE, border_style="cyan")
        details_table.add_column("Item", style="cyan")
        details_table.add_column("Details", style="white")
        details_table.add_row("New Version", f"[green]v{latest['version']}[/green]")
        details_table.add_row("Installer", latest.get('asset_name', 'Unknown'))
        if latest.get('asset_size'):
            size_mb = latest['asset_size'] / (1024 * 1024)
            details_table.add_row("Size", f"{size_mb:.1f} MB")
        details_table.add_row("Release", latest.get('published_at', 'Unknown'))
        
        console.print(Panel(details_table, title="[bold yellow]📦 UPDATE DETAILS[/bold yellow]", border_style="yellow"))
        
        console.print("\n[bold red]⚠️ SECURITY NOTICE[/bold red]")
        console.print("[dim]• The installer will be downloaded from DSTerminal Update Module\n"
                    "• Verify the digital signature before running\n"
                    "• The installer may requires you access to License Key to activate the product and ready for installation process,\n"
                    "• Administrator privileges may be required\n"
                    "• If the file is very large (>=243.9 MB), the download will take some time\n"
                    "• Make sure you have enough disk space and a stable internet connection[/dim]\n")
        
        confirm = console.input("[bold red]Type 'INSTALL' to download and run the installer: [/]").strip()
        
        if confirm != "INSTALL":
            console.print("[yellow]Update cancelled[/yellow]")
            return False
        
        if not latest.get('download_url'):
            console.print(Panel(
                "[yellow]No automatic download available[/]\n\n"
                f"Please download manually from:\n{latest['url']}",
                border_style="yellow"
            ))
            return False
        
        # Store asset API URL for download method
        self.asset_api_url = latest.get('asset_api_url')
        
        # Download to Downloads folder
        installer_name = latest['asset_name'] or f"DSTerminal-v{latest['version']}.zip"
        download_result = self.download_update(latest['download_url'], installer_name)
        
        if not download_result:
            console.print("[red]Download failed[/red]")
            return False
        
        installer_path = download_result if isinstance(download_result, str) else None
        
        if not installer_path or not os.path.exists(installer_path) or os.path.getsize(installer_path) == 0:
            console.print("[red]Download verification failed[/red]")
            return False
        
        console.print("\n[green]✓ Download verified successfully[/green]")
        
        console.print("\n[cyan]🔧 Ready to install update...[/cyan]")
        run_installer = console.input("[bold yellow]Run the installer now? (Y/n): [/]").strip().lower()
        
        if run_installer != 'n':
            console.print("[cyan]Launching installer...[/cyan]")
            time.sleep(1)
            
            try:
                if platform.system().lower() == "windows":
                    os.startfile(installer_path)
                else:
                    if platform.system().lower() != "windows":
                        os.chmod(installer_path, 0o755)
                    subprocess.Popen([installer_path], shell=True)
                
                console.print(Panel(
                    f"[bold green]✅ INSTALLER LAUNCHED![/bold green]\n\n"
                    f"[yellow]Please complete the installation wizard[/yellow]\n"
                    f"[dim]Installer location: {installer_path}[/dim]\n\n"
                    f"[cyan]After installation, restart DSTerminal[/cyan]",
                    border_style="green"
                ))
                return True
                
            except Exception as e:
                console.print(f"[red]Failed to launch installer: {e}[/red]")
                console.print(f"[yellow]Please run manually: {installer_path}[/yellow]")
                return False
        else:
            console.print(f"[yellow]Installer saved to: {installer_path}[/yellow]")
            return True

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
            symbols = "█▓▒░▄▀■►▼▲◄▶◀◢◣◥◤▬▭▮▯┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬═║"
            width = min(console.size.width, 80)
            with console.status("[bold red]🔐 ACCESSING UPDATE MODULE...[/]", spinner="dots"):
                for _ in range(3):
                    console.print(
                        "".join(random.choice(symbols) for _ in range(width)),
                        style="bold green"
                    )
                    time.sleep(1.0)

        def satellite_scan():
            frames = ["🛰", "📡", "📶", "🔍", "🎯", "⚡"]
            with Progress(
                SpinnerColumn(style="cyan"),
                TextColumn("[bold blue]{task.description}"),
                transient=True,
                console=console
            ) as progress:
                task = progress.add_task("Establishing secure connection...", total=100)
                for i in range(100):
                    progress.update(task, advance=1,
                                    description=f"{frames[i % len(frames)]} Scanning {i}%")
                    time.sleep(0.1)

        def version_comparison_animation(current_ver, latest_ver):
            with Live(refresh_per_second=10, console=console, transient=True) as live:
                for i in range(1, 4):
                    bar = "█" * (i * 8)
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
                    time.sleep(1.0)

        # ===================== UPDATE LOGIC =====================
        def parse_version(v):
            parts = [int(p) if p.isdigit() else 0 for p in str(v).lstrip("vV").split(".")]
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts)

        # ===================== MAIN FLOW =====================
        try:
            console.print(Panel(
                Align.center("[bold cyan]🔄 DSTERMINAL UPDATE PROTOCOL 🔄[/bold cyan]"),
                border_style="cyan"
            ))
            
            hacker_animation()
            satellite_scan()
            
            current_version = self.config.get("CURRENT_VERSION", "3.1.113").lstrip("v")
            
            version_table = Table(box=box.SIMPLE, border_style="blue")
            version_table.add_column("Component", style="cyan")
            version_table.add_column("Version", style="green")
            version_table.add_row("Current Installation", f"v{current_version}")
            version_table.add_row("System", platform.system())
            version_table.add_row("Architecture", platform.machine())
            
            console.print(Panel(version_table, title="[bold]📊 SYSTEM STATUS[/bold]", border_style="blue"))
            
            console.print("\n[cyan]🔍 Checking Modules for updates...[/cyan]")
            
            try:
                latest = self._check_github_release()
            except Exception as e:
                console.print(Panel(
                    f"[bold red]UPDATE CHECK FAILED[/]\n\n"
                    f"[yellow]{str(e)}[/yellow]\n\n"
                    f"[dim]• Please check your internet connection\n"
                    f"• Verify the GitHub repository exists\n"
                    f"• Visit: https://github.com/{self.github_repo}[/dim]",
                    border_style="red"
                ))
                return False
            
            if not latest:
                console.print(Panel(
                    "[yellow]⚠️ No update information available[/yellow]",
                    border_style="yellow"
                ))
                return False
            
            version_comparison_animation(current_version, latest['version'])
            
            current_tuple = parse_version(current_version)
            latest_tuple = parse_version(latest['version'])
            
            if latest_tuple > current_tuple:
                console.print(Panel(
                    f"[bold red]🚨 UPDATES ARE AVAILABLE! 🚨[/bold red]\n\n"
                    f"[yellow]Current:[/yellow] v{current_version}\n"
                    f"[green]Latest:[/green] v{latest['version']}\n"
                    f"[cyan]Released:[/cyan] {latest.get('published_at', 'Unknown')}\n\n",
                    border_style="red",
                    width=90,
                    padding=(1, 2)
                ))
                
                # Render release notes with Markdown
                console.print("[bold cyan]Release Notes:[/bold cyan]")
                if latest.get('notes'):
                    md = Markdown(latest['notes'])
                    console.print(md)
                else:
                    console.print("[dim]No release notes available[/dim]")
                    # ===============
                choice = console.input("\n[bold cyan]Download and install update now? (y/N): [/]").lower()
                
                if choice == 'y':
                    return self.perform_update(latest)
                else:
                    console.print("[yellow]Update postponed[/yellow]")
                    return False
            
            else:
                console.print(Panel(
                    Align.center(
                        f"[bold green]✅ DSTERMINAL IS UP TO DATE![/bold green]\n\n"
                        f"[dim]Version: v{current_version}\n"
                        f"Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
                    ),
                    border_style="green",
                    width=60
                ))
                return True
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Update cancelled by user[/yellow]")
            return True
        except Exception as e:
            console.print(Panel(
                f"[bold red]UPDATE ERROR[/]\n\n{str(e)}",
                border_style="red"
            ))
            import traceback
            traceback.print_exc()
            return False


# ================================================================
# ONLY RUN THIS WHEN THE FILE IS EXECUTED DIRECTLY, NOT WHEN IMPORTED
# ================================================================
if __name__ == "__main__":
    # Test configuration - ONLY runs when this file is executed directly
    class Config:
        def __init__(self):
            self.config = {
                "CURRENT_VERSION": "3.1.113",
                "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "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")
            }
        
        def get(self, key, default=None):
            return self.config.get(key, default)
    
    config = Config()
    update_manager = UpdateManager(config)
    update_manager.check_updates()