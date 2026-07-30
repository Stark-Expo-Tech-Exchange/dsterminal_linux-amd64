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

class UpdateManager:
    def __init__(self, config):
        self.config = config
        self.console = Console()
        
        # ============================================================
        # NEW TEST REPOSITORY - PUBLIC
        # ============================================================
        self.github_repo = "Stark-Expo-Tech-Exchange/DSTerminal-Updates-Test"
        
    def _check_github_release(self):
        """Check GitHub for latest release - Complete working version"""
        try:
            import requests
            from datetime import datetime
            
            # Get current version from config
            current_version = self.config.get("CURRENT_VERSION", "1.0.0")
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'DSTerminal-Update-Checker/4.0'
            }
            
            # ============================================================
            # METHOD 1: Try the releases endpoint
            # ============================================================
            api_url = f"https://api.github.com/repos/{self.github_repo}/releases"
            
            self.console.print(f"[dim]Connecting to GitHub API for {self.github_repo}...[/dim]")
            response = requests.get(api_url, timeout=15, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Find the latest release (first one is usually the newest)
                    latest_release = data[0]
                    tag_name = latest_release.get("tag_name", "")
                    self.console.print(f"[green]✓ Found release: {tag_name}[/green]")
                    
                    # Process the release data
                    release_info = self._process_release_data(latest_release)
                    if release_info:
                        return release_info
                else:
                    self.console.print("[red]❌ No releases found via API.[/red]")
                    raise Exception("No releases found in GitHub repository")
            elif response.status_code == 404:
                self.console.print(f"[red]❌ Repository not found: {self.github_repo}[/red]")
                raise Exception(f"Repository {self.github_repo} not found")
            elif response.status_code == 403:
                self.console.print("[yellow]⚠️ Rate limit exceeded or access denied[/yellow]")
                raise Exception("GitHub API rate limit exceeded")
            else:
                self.console.print(f"[yellow]API returned {response.status_code}, trying alternative...[/yellow]")
            
            # ============================================================
            # METHOD 2: Try using tags
            # ============================================================
            self.console.print("[dim]Trying to get latest release by tag...[/dim]")
            
            tags_url = f"https://api.github.com/repos/{self.github_repo}/tags"
            tags_response = requests.get(tags_url, timeout=10, headers=headers)
            
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                if tags_data:
                    latest_tag = tags_data[0].get("name", "")
                    if latest_tag:
                        self.console.print(f"[green]✓ Found latest tag: {latest_tag}[/green]")
                        
                        # Try to get release info for this tag
                        release_url = f"https://api.github.com/repos/{self.github_repo}/releases/tags/{latest_tag}"
                        release_response = requests.get(release_url, timeout=10, headers=headers)
                        
                        if release_response.status_code == 200:
                            return self._process_release_data(release_response.json())
                        else:
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
                    self.console.print("[red]❌ No tags found[/red]")
                    raise Exception("No tags found in repository")
            else:
                self.console.print(f"[red]❌ Failed to get tags: {tags_response.status_code}[/red]")
                raise Exception(f"GitHub API returned {tags_response.status_code} for tags endpoint")
            
            # If we get here, nothing worked
            self.console.print("[red]❌ All GitHub API methods failed[/red]")
            raise Exception("Unable to fetch release information from GitHub")

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
            
            # Look for the ZIP file specifically
            zip_asset = None
            for asset in assets:
                name = asset.get("name", "")
                if name.endswith(".zip") and "Source" not in name:
                    zip_asset = asset
                    break
            
            # If no zip found, use the first asset
            if not zip_asset and assets:
                zip_asset = assets[0]
            
            download_url = None
            asset_name = None
            asset_size = 0
            
            if zip_asset:
                download_url = zip_asset.get("browser_download_url")
                asset_name = zip_asset.get("name")
                asset_size = zip_asset.get("size", 0)
                self.console.print(f"[dim]Found asset: {asset_name} ({asset_size} bytes)[/dim]")
            
            # If no assets, use the zipball URL
            if not download_url:
                download_url = release.get("zipball_url")
                asset_name = f"DSTerminal-{version}.zip"
                self.console.print(f"[dim]No assets found, using zipball[/dim]")
            
            return {
                "version": version,
                "url": release.get("html_url", ""),
                "download_url": download_url,
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
        """Download update with progress bar"""
        try:
            import requests
            import os
            
            self.console.print(f"\n[cyan]📥 Downloading update from GitHub...[/cyan]")
            self.console.print(f"[dim]File: {filename}[/dim]")
            
            if not url:
                self.console.print("[red]No download URL available[/red]")
                return False
            
            response = requests.get(url, stream=True, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            with open(filename, 'wb') as f:
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
            
            if os.path.exists(filename):
                self.console.print(f"[green]✓ Download complete: {filename}[/green]")
                return True
            else:
                self.console.print("[red]Download failed - file not created[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]✗ Download failed: {e}[/red]")
            return False

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
            with console.status("[bold red]🔐 ACCESSING UPDATE SERVERS...[/]", spinner="dots"):
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

        def perform_update(latest):
            """Execute the actual update process"""
            
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
            console.print("[dim]• The installer will be downloaded from GitHub\n"
                        "• Verify the digital signature before running\n"
                        "• Administrator privileges may be required[/dim]\n")
            
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
            
            temp_dir = tempfile.gettempdir()
            installer_name = latest['asset_name'] or f"DSTerminal-v{latest['version']}.zip"
            installer_path = os.path.join(temp_dir, installer_name)
            
            if os.path.exists(installer_path):
                try:
                    os.remove(installer_path)
                except:
                    pass
            
            if not self.download_update(latest['download_url'], installer_path):
                return False
            
            if not os.path.exists(installer_path) or os.path.getsize(installer_path) == 0:
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

        # ===================== MAIN FLOW =====================
        try:
            console.print(Panel(
                Align.center("[bold cyan]🔄 DSTERMINAL UPDATE PROTOCOL 🔄[/bold cyan]"),
                border_style="cyan"
            ))
            
            hacker_animation()
            satellite_scan()
            
            current_version = self.config.get("CURRENT_VERSION", "1.0.0").lstrip("v")
            
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
                    f"• Verify the GitHub repository exists and is public\n"
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
                update_info = (
                    f"[bold red]🚨 UPDATE AVAILABLE! 🚨[/bold red]\n\n"
                    f"[yellow]Current:[/yellow] v{current_version}\n"
                    f"[green]Latest:[/green] v{latest['version']}\n"
                    f"[cyan]Released:[/cyan] {latest.get('published_at', 'Unknown')}\n\n"
                    f"[cyan]Release Notes:[/cyan]\n"
                    f"[dim]{latest['notes'][:400]}[/dim]\n"
                )
                
                if latest.get('prerelease'):
                    update_info += f"\n[red]⚠️ PRE-RELEASE VERSION - Use with caution[/red]\n"
                
                console.print(Panel(
                    update_info,
                    border_style="red",
                    width=90,
                    padding=(1, 2)
                ))
                
                choice = console.input("\n[bold cyan]Download and install update now? (y/N): [/]").lower()
                
                if choice == 'y':
                    return perform_update(latest)
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

# Test configuration
class Config:
    def __init__(self):
        self.config = {
            "CURRENT_VERSION": "1.0.0"  # Set to match your release
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)

# Run the test
if __name__ == "__main__":
    config = Config()
    update_manager = UpdateManager(config)
    update_manager.check_updates()