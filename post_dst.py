#!python
import os
import sys
import platform
import subprocess
import json
import shutil
from pathlib import Path
import requests
import time
import zipfile
import tarfile
import stat
import ctypes
import winreg
import argparse
import hashlib
import cmd

# ============================================================
# BUNDLED PACKAGES MANAGER
# ============================================================

class BundledPackageManager:
    """
    Manages bundled packages for offline installation
    """
    
    def __init__(self, bundle_dir=None):
        if bundle_dir is None:
            # Try to find bundled directory
            possible_paths = [
                Path(__file__).parent / "bundled",
                Path.cwd() / "bundled",
                Path.home() / "DSTerminal" / "bundled"
            ]
            
            self.bundle_dir = None
            for path in possible_paths:
                if path.exists():
                    self.bundle_dir = path
                    break
            
            if self.bundle_dir is None:
                self.bundle_dir = Path(__file__).parent / "bundled"
        else:
            self.bundle_dir = Path(bundle_dir)
        
        self.bundle_dir.mkdir(parents=True, exist_ok=True)
        
        # Define bundle structure
        self.bundle_structure = {
            'nmap': {
                'files': ['nmap-7.95-setup.exe'],
                'install_type': 'executable',
                'silent_args': '/S /npcap-install /npcap-silent-install',
                'description': 'Nmap network scanner'
            },
            'npcap': {
                'files': ['npcap-1.79.exe'],
                'install_type': 'executable',
                'silent_args': '/S /npcap_silent_install /npcap_winpcap_mode /npcap_loopback_support',
                'description': 'Npcap packet capture library'
            },
            'metasploit': {
                'files': ['metasploit-latest-windows-x64-installer.exe'],
                'install_type': 'executable',
                'silent_args': '/S',
                'description': 'Metasploit Framework'
            },
            'sqlmap': {
                'files': ['sqlmap.zip'],
                'install_type': 'archive',
                'extract_to': 'sqlmap',
                'description': 'SQL injection tool'
            },
            'nikto': {
                'files': ['nikto.zip'],
                'install_type': 'archive',
                'extract_to': 'nikto',
                'description': 'Web server scanner'
            },
            'whois': {
                'files': ['whois.ps1'],
                'install_type': 'script',
                'install_path': 'tools/whois',
                'description': 'Whois lookup script'
            }
        }
    
    def get_bundle_path(self, package_name):
        """Get path to bundle for a package"""
        if package_name not in self.bundle_structure:
            return None
        
        package_dir = self.bundle_dir / package_name
        return package_dir
    
    def is_bundle_available(self, package_name):
        """Check if a bundle is available"""
        if package_name not in self.bundle_structure:
            return False
        
        package_dir = self.bundle_dir / package_name
        if not package_dir.exists():
            return False
        
        # Check if all required files exist
        required_files = self.bundle_structure[package_name]['files']
        for file_name in required_files:
            if not (package_dir / file_name).exists():
                return False
        
        return True
    
    def verify_bundle(self, package_name):
        """Verify bundle integrity using checksum if available"""
        if not self.is_bundle_available(package_name):
            return False
        
        package_dir = self.bundle_dir / package_name
        checksum_file = package_dir / f"{package_name}.sha256"
        
        if not checksum_file.exists():
            # No checksum file, assume it's valid
            return True
        
        with open(checksum_file, 'r') as f:
            expected_checksum = f.read().strip()
        
        # Verify each file
        for file_name in self.bundle_structure[package_name]['files']:
            if file_name.endswith('.sha256'):
                continue
            
            file_path = package_dir / file_name
            if file_path.exists():
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                actual_checksum = sha256_hash.hexdigest()
                
                if actual_checksum != expected_checksum:
                    print(f"âŒ Checksum mismatch for {file_name}")
                    return False
        
        return True
    
    def install_from_bundle(self, package_name, installer):
        """Install a tool from bundled package"""
        if not self.is_bundle_available(package_name):
            return False
        
        # Verify bundle integrity
        if not self.verify_bundle(package_name):
            print(f"âŒ Bundle verification failed for {package_name}")
            return False
        
        package_dir = self.bundle_dir / package_name
        bundle_info = self.bundle_structure[package_name]
        
        print(f"ðŸ“¦ Installing {package_name} from bundled package...")
        
        if bundle_info['install_type'] == 'executable':
            # Find the executable file
            for file_name in bundle_info['files']:
                exe_path = package_dir / file_name
                if exe_path.exists():
                    print(f"  Running installer: {file_name}")
                    try:
                        silent_args = bundle_info.get('silent_args', '/S')
                        if installer.os_type == 'windows':
                            if installer.is_admin:
                                process = subprocess.Popen(
                                    [str(exe_path)] + silent_args.split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                )
                                try:
                                    stdout, stderr = process.communicate(timeout=300)
                                    print(f"  âœ… {package_name} installed from bundle")
                                    return True
                                except subprocess.TimeoutExpired:
                                    process.kill()
                                    print(f"  âš ï¸ Installation timed out")
                                    return False
                            else:
                                installer.run_as_admin(str(exe_path), silent_args)
                                print(f"  âœ… {package_name} installer started with admin privileges")
                                return True
                        else:
                            exe_path.chmod(0o755)
                            subprocess.run([str(exe_path), '--mode', 'unattended'], 
                                         check=False, timeout=300)
                            print(f"  âœ… {package_name} installed from bundle")
                            return True
                    except Exception as e:
                        print(f"  âŒ Installation failed: {e}")
                        return False
            
            return False
        
        elif bundle_info['install_type'] == 'archive':
            # Extract archive
            for file_name in bundle_info['files']:
                if file_name.endswith('.zip'):
                    archive_path = package_dir / file_name
                    if archive_path.exists():
                        extract_to = installer.tools_dir / bundle_info.get('extract_to', package_name)
                        print(f"  Extracting: {file_name} to {extract_to}")
                        try:
                            # Remove existing directory if it exists
                            if extract_to.exists():
                                shutil.rmtree(extract_to, ignore_errors=True)
                            extract_to.mkdir(parents=True, exist_ok=True)
                            
                            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                                zip_ref.extractall(extract_to.parent)
                            print(f"  âœ… {package_name} extracted from bundle")
                            return True
                        except Exception as e:
                            print(f"  âŒ Extraction failed: {e}")
                            return False
            
            return False
        
        elif bundle_info['install_type'] == 'script':
            # Copy script
            for file_name in bundle_info['files']:
                script_path = package_dir / file_name
                if script_path.exists():
                    install_path = installer.tools_dir / bundle_info.get('install_path', package_name)
                    install_path.mkdir(parents=True, exist_ok=True)
                    target_path = install_path / file_name
                    shutil.copy2(script_path, target_path)
                    print(f"  âœ… {package_name} script copied from bundle")
                    return True
            
            return False
        
        return False
    
    def list_bundled_packages(self):
        """List all available bundled packages"""
        available = []
        for package_name in self.bundle_structure:
            if self.is_bundle_available(package_name):
                available.append(package_name)
        return available
    
    def get_bundle_size(self, package_name):
        """Get size of a bundle in MB"""
        if not self.is_bundle_available(package_name):
            return 0
        
        package_dir = self.bundle_dir / package_name
        size = sum(f.stat().st_size for f in package_dir.glob('**/*') if f.is_file())
        return size / (1024 * 1024)


# ============================================================
# SMART INSTALLER CLASS (UPDATED WITH BUNDLED SUPPORT)
# ============================================================

class SmartDSTerminalInstaller:
    """
    The Ultimate DSTerminal Installer - Full Auto Installation with Bundled Support
    """
    
    def __init__(self, verbose=True):
        self.os_type = platform.system().lower()
        self.arch = platform.machine()
        self.install_dir = Path.home() / "DSTerminal"
        self.bin_dir = self.install_dir / "bin"
        self.tools_dir = self.install_dir / "tools"
        self.config_dir = self.install_dir / "config"
        self.download_dir = self.install_dir / "downloads"
        self.verbose = verbose
        
        # Initialize bundled package manager
        self.bundle_manager = BundledPackageManager()
        
        # Check admin/sudo status
        self.is_admin = self.check_admin()
        
        # OS-specific tool definitions with bundled priority
        self.tool_definitions = self.get_os_specific_tools()
        
        # Installation strategies (prioritize bundled)
        self.strategies = {
            'bundled': self.install_from_bundled,
            'package_manager': self.install_via_package_manager,
            'python_pip': self.install_via_pip,
            'git_clone': self.install_via_git,
            'binary_download': self.install_via_binary_download,
            'installer_download': self.install_via_installer,
            'docker': self.install_via_docker,
            'embedded_script': self.install_embedded_script
        }
    
    def log(self, message, color=None, level="INFO"):
        """Log message with optional color"""
        if not self.verbose:
            return
            
        colors = {
            "GREEN": "\033[92m",
            "YELLOW": "\033[93m",
            "RED": "\033[91m",
            "CYAN": "\033[96m",
            "RESET": "\033[0m"
        }
        
        if color and color in colors:
            print(f"{colors[color]}{message}{colors['RESET']}")
        else:
            print(message)
    
    def get_os_specific_tools(self):
        """Get OS-specific tool definitions with bundled priority"""
        if self.os_type == 'windows':
            return {
                'sqlmap': {
                    'priority': ['bundled', 'python_pip', 'git_clone'],
                    'pip_package': 'sqlmap',
                    'git_url': 'https://github.com/sqlmapproject/sqlmap.git',
                    'executable': 'sqlmap.py',
                    'wrapper_ext': '.bat'
                },
                'nikto': {
                    'priority': ['bundled', 'git_clone'],
                    'git_url': 'https://github.com/sullo/nikto.git',
                    'executable': 'nikto.pl',
                    'wrapper_ext': '.bat'
                },
                'nmap': {
                    'priority': ['bundled', 'installer_download'],
                    'installer_url': 'https://nmap.org/dist/nmap-7.95-setup.exe',
                    'executable': 'nmap.exe',
                    'wrapper_ext': '.bat',
                    'needs_admin': True,
                    'silent_args': '/S',
                    'install_paths': [
                        r"C:\Program Files\Nmap",
                        r"C:\Program Files (x86)\Nmap"
                    ],
                    'executable_name': 'nmap.exe',
                    'npcap_url': 'https://npcap.com/dist/npcap-1.79.exe',
                    'npcap_silent_args': '/S'
                },
                'metasploit': {
                    'priority': ['bundled', 'installer_download'],
                    'installer_url': 'https://downloads.metasploit.com/data/releases/metasploit-latest-windows-x64-installer.exe',
                    'executable': 'msfconsole.bat',
                    'wrapper_ext': '.bat',
                    'needs_admin': True,
                    'silent_args': '/S',
                    'install_paths': [
                        r"C:\metasploit-framework",
                        r"C:\Program Files\metasploit-framework"
                    ],
                    'executable_name': 'msfconsole.bat'
                },
                'whois': {
                    'priority': ['bundled', 'embedded_script'],
                    'executable': 'whois.ps1',
                    'wrapper_ext': '.bat',
                    'install_paths': [
                        str(Path.home() / "DSTerminal" / "tools" / "whois")
                    ],
                    'executable_name': 'whois.ps1'
                },
                'npcap': {
                    'priority': ['bundled', 'installer_download'],
                    'installer_url': 'https://npcap.com/dist/npcap-1.79.exe',
                    'executable': 'npcap.exe',
                    'wrapper_ext': '.bat',
                    'needs_admin': True,
                    'silent_args': '/S /npcap_silent_install /npcap_winpcap_mode /npcap_loopback_support',
                    'install_paths': [
                        r"C:\Program Files\Npcap",
                        r"C:\Windows\System32\Npcap"
                    ]
                }
            }
        else:
            return self.get_unix_tools()
    
    def get_unix_tools(self):
        """Get Unix/Linux/macOS tool definitions"""
        if self.os_type == 'darwin':
            return {
                'sqlmap': {
                    'priority': ['python_pip', 'git_clone'],
                    'pip_package': 'sqlmap',
                    'git_url': 'https://github.com/sqlmapproject/sqlmap.git',
                    'executable': 'sqlmap.py',
                    'wrapper_ext': ''
                },
                'nikto': {
                    'priority': ['package_manager', 'git_clone'],
                    'package_names': {'brew': 'nikto'},
                    'git_url': 'https://github.com/sullo/nikto.git',
                    'executable': 'nikto.pl',
                    'wrapper_ext': ''
                },
                'nmap': {
                    'priority': ['package_manager', 'binary_download'],
                    'package_names': {'brew': 'nmap'},
                    'download_url': 'https://nmap.org/dist/nmap-7.95-{os}-{arch}.{ext}',
                    'executable': 'nmap',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/local/bin', '/opt/local/bin']
                },
                'metasploit': {
                    'priority': ['installer_download', 'docker'],
                    'installer_url': 'https://downloads.metasploit.com/data/releases/metasploit-latest-{os}-{arch}.{ext}',
                    'docker_image': 'metasploitframework/metasploit-framework',
                    'executable': 'msfconsole',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/local/bin', '/opt/metasploit-framework/bin']
                },
                'whois': {
                    'priority': ['package_manager'],
                    'package_names': {'brew': 'whois'},
                    'executable': 'whois',
                    'wrapper_ext': ''
                }
            }
        else:  # Linux
            return {
                'sqlmap': {
                    'priority': ['python_pip', 'git_clone'],
                    'pip_package': 'sqlmap',
                    'git_url': 'https://github.com/sqlmapproject/sqlmap.git',
                    'executable': 'sqlmap.py',
                    'wrapper_ext': ''
                },
                'nikto': {
                    'priority': ['package_manager', 'git_clone'],
                    'package_names': {'apt': 'nikto', 'yum': 'nikto', 'dnf': 'nikto'},
                    'git_url': 'https://github.com/sullo/nikto.git',
                    'executable': 'nikto.pl',
                    'wrapper_ext': ''
                },
                'nmap': {
                    'priority': ['package_manager', 'binary_download'],
                    'package_names': {'apt': 'nmap', 'yum': 'nmap', 'dnf': 'nmap'},
                    'download_url': 'https://nmap.org/dist/nmap-7.95-{os}-{arch}.{ext}',
                    'executable': 'nmap',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/bin', '/usr/local/bin']
                },
                'metasploit': {
                    'priority': ['installer_download', 'docker'],
                    'installer_url': 'https://downloads.metasploit.com/data/releases/metasploit-latest-{os}-{arch}.{ext}',
                    'docker_image': 'metasploitframework/metasploit-framework',
                    'executable': 'msfconsole',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/local/bin', '/opt/metasploit-framework/bin']
                },
                'whois': {
                    'priority': ['package_manager'],
                    'package_names': {'apt': 'whois', 'yum': 'whois', 'dnf': 'whois'},
                    'executable': 'whois',
                    'wrapper_ext': ''
                }
            }
    
    def check_admin(self):
        """Check if running with admin/root privileges"""
        try:
            if self.os_type == 'windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def run_as_admin(self, command, args=None):
        """Run a command with administrator privileges on Windows"""
        if self.os_type != 'windows':
            return False
        
        try:
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", str(command), args or "", None, 1
            )
            return result > 32
        except Exception as e:
            self.log(f"  Admin elevation error: {e}", "RED")
            return False
    
    def detect_environment(self):
        """Detect environment"""
        return {
            'has_internet': self.check_internet(),
            'is_admin': self.is_admin,
            'os': self.os_type,
            'arch': self.arch,
            'python_version': sys.version.split()[0],
            'package_managers': self.check_package_managers()
        }
    
    def check_internet(self):
        """Check internet connectivity"""
        try:
            requests.get('https://github.com', timeout=5)
            return True
        except:
            return False
    
    def check_package_managers(self):
        """Check for available package managers"""
        managers = {}
        if shutil.which('apt-get'):
            managers['apt'] = True
        if shutil.which('yum'):
            managers['yum'] = True
        if shutil.which('dnf'):
            managers['dnf'] = True
        if shutil.which('brew'):
            managers['brew'] = True
        if shutil.which('choco'):
            managers['choco'] = True
        if shutil.which('winget'):
            managers['winget'] = True
        return managers
    
    def check_pip(self):
        """Check if pip is available"""
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def check_git(self):
        """Check if git is available"""
        return shutil.which('git') is not None
    
    def check_docker(self):
        """Check if Docker is available"""
        return shutil.which('docker') is not None
    
    def check_npcap_installed(self):
        """Check if Npcap is installed"""
        npcap_paths = [
            r"C:\Windows\System32\Npcap",
            r"C:\Program Files\Npcap",
            r"C:\Windows\SysWOW64\Npcap"
        ]
        for path in npcap_paths:
            if Path(path).exists():
                return True
        return False
    
    def download_file(self, url, dest_path, show_progress=True):
        """Download file with progress"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            if show_progress and total_size > 0 and self.verbose:
                self.log(f"  Downloading: {url.split('/')[-1]} ({total_size // (1024*1024)} MB)", "YELLOW")
                
                downloaded = 0
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (10 * 1024 * 1024) == 0:
                            self.log(f"    Progress: {downloaded // (1024 * 1024)} MB", "YELLOW")
            else:
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            return True
        except Exception as e:
            self.log(f"  Download error: {e}", "RED")
            return False
    
    def install_npcap(self):
        """Download and install Npcap"""
        self.log("\n  ðŸ“¦ Installing Npcap (required for Nmap)...", "CYAN")
        
        if self.check_npcap_installed():
            self.log("  âœ… Npcap is already installed", "GREEN")
            return True
        
        npcap_url = self.tool_definitions['nmap'].get('npcap_url', 'https://npcap.com/dist/npcap-1.79.exe')
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        filename = npcap_url.split('/')[-1]
        download_path = self.download_dir / filename
        
        if not download_path.exists():
            self.log("  Downloading Npcap installer...", "YELLOW")
            if not self.download_file(npcap_url, download_path):
                self.log("  âŒ Failed to download Npcap", "RED")
                return False
        
        self.log("  Installing Npcap silently...", "YELLOW")
        try:
            args = '/S /npcap_silent_install /npcap_winpcap_mode /npcap_loopback_support'
            
            if self.is_admin:
                process = subprocess.Popen(
                    [str(download_path)] + args.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                try:
                    stdout, stderr = process.communicate(timeout=120)
                    self.log("  âœ… Npcap installation completed", "GREEN")
                    return True
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.log("  âš ï¸ Npcap installation timed out", "YELLOW")
                    return False
            else:
                if self.run_as_admin(str(download_path), args):
                    self.log("  âœ… Npcap installer started with admin privileges", "GREEN")
                    time.sleep(10)
                    return True
                else:
                    self.log("  âŒ Failed to elevate for Npcap installation", "RED")
                    return False
        except Exception as e:
            self.log(f"  âŒ Npcap installation error: {e}", "RED")
            return False
    
    def install_via_package_manager(self, tool_name, tool_config):
        """Install using system package manager"""
        if 'package_names' not in tool_config:
            return False
        
        pkg_managers = self.check_package_managers()
        if not pkg_managers:
            return False
        
        for mgr in pkg_managers:
            if mgr in tool_config['package_names']:
                package_name = tool_config['package_names'][mgr]
                try:
                    self.log(f"  Installing via {mgr}: {package_name}", "YELLOW")
                    
                    if mgr == 'apt':
                        if self.is_admin:
                            subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
                            subprocess.run(['apt-get', 'install', '-y', package_name], check=True, capture_output=True)
                        else:
                            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                            subprocess.run(['sudo', 'apt-get', 'install', '-y', package_name], check=True)
                        return True
                    
                    elif mgr == 'yum':
                        if self.is_admin:
                            subprocess.run(['yum', 'install', '-y', package_name], check=True)
                        else:
                            subprocess.run(['sudo', 'yum', 'install', '-y', package_name], check=True)
                        return True
                    
                    elif mgr == 'dnf':
                        if self.is_admin:
                            subprocess.run(['dnf', 'install', '-y', package_name], check=True)
                        else:
                            subprocess.run(['sudo', 'dnf', 'install', '-y', package_name], check=True)
                        return True
                    
                    elif mgr == 'brew':
                        subprocess.run(['brew', 'install', package_name], check=True)
                        return True
                    
                    elif mgr == 'choco':
                        if self.is_admin:
                            subprocess.run(['choco', 'install', package_name, '-y'], check=True)
                            return True
                        else:
                            self.log("  âš ï¸ Chocolatey requires admin privileges", "YELLOW")
                            return False
                    
                    elif mgr == 'winget':
                        subprocess.run(['winget', 'install', package_name, '--silent'], check=True)
                        return True
                        
                except Exception as e:
                    self.log(f"  Package manager error: {e}", "RED")
                    continue
        
        return False
    
    def install_via_pip(self, tool_name, tool_config):
        """Install using pip"""
        if 'pip_package' not in tool_config:
            return False
        
        try:
            self.log(f"  Installing via pip: {tool_config['pip_package']}", "YELLOW")
            subprocess.run([sys.executable, '-m', 'pip', 'install', tool_config['pip_package']], 
                         check=True, capture_output=True)
            return self.create_wrapper(tool_name, tool_config)
        except Exception as e:
            self.log(f"  Pip error: {e}", "RED")
            return False
    
    def install_via_git(self, tool_name, tool_config):
        """Clone from git"""
        if 'git_url' not in tool_config:
            return False
        
        if not self.check_git():
            self.log("  Git not installed. Skipping git clone.", "YELLOW")
            return False
        
        tool_path = self.tools_dir / tool_name
        try:
            if tool_path.exists():
                try:
                    shutil.rmtree(tool_path)
                    self.log(f"  Removed existing directory: {tool_path}", "YELLOW")
                except PermissionError:
                    self.log(f"  âš ï¸ Permission denied removing {tool_path}", "YELLOW")
                    self.log("  Attempting to clone into a new location...", "YELLOW")
                    tool_path = self.tools_dir / f"{tool_name}_new"
                    if tool_path.exists():
                        shutil.rmtree(tool_path)
            
            self.log(f"  Cloning from: {tool_config['git_url']}", "YELLOW")
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', tool_config['git_url'], str(tool_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log(f"  Git error: {result.stderr}", "RED")
                return False
            
            return self.create_wrapper(tool_name, tool_config)
        except Exception as e:
            self.log(f"  Git error: {e}", "RED")
            return False
    
    def install_via_binary_download(self, tool_name, tool_config):
        """Download and install binary"""
        if 'download_url' not in tool_config:
            return False
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        os_map = {'windows': 'win', 'linux': 'linux', 'darwin': 'macos'}
        arch_map = {'AMD64': '64', 'x86_64': '64', 'arm64': 'arm64'}
        
        os_key = os_map.get(self.os_type, self.os_type)
        arch_key = arch_map.get(self.arch, '64')
        
        if self.os_type == 'windows':
            ext = 'exe'
        elif self.os_type == 'darwin':
            ext = 'dmg'
        else:
            ext = 'tar.gz' if self.arch == 'arm64' else 'rpm'
        
        url = tool_config['download_url'].format(os=os_key, arch=arch_key, ext=ext)
        
        try:
            filename = url.split('/')[-1]
            download_path = self.download_dir / filename
            
            if not self.download_file(url, download_path):
                return False
            
            if filename.endswith('.exe'):
                if self.is_admin:
                    subprocess.run([str(download_path), '/S'], check=False)
                else:
                    self.log("  âš ï¸ Admin rights needed for installation", "YELLOW")
                    self.log(f"  Please run: {download_path}", "YELLOW")
                return self.create_wrapper(tool_name, tool_config)
            
            elif filename.endswith('.dmg'):
                self.log("  Mounting DMG...", "YELLOW")
                subprocess.run(['hdiutil', 'attach', str(download_path)], check=True)
                subprocess.run(['cp', '-R', '/Volumes/Nmap/Nmap.app', '/Applications/'], check=True)
                subprocess.run(['hdiutil', 'detach', '/Volumes/Nmap'], check=True)
                return self.create_wrapper(tool_name, tool_config)
            
            elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
                extract_dir = self.tools_dir / tool_name
                extract_dir.mkdir(parents=True, exist_ok=True)
                with tarfile.open(download_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
                return self.create_wrapper(tool_name, tool_config)
            
            elif filename.endswith('.rpm'):
                if self.is_admin:
                    subprocess.run(['rpm', '-i', str(download_path)], check=True)
                else:
                    subprocess.run(['sudo', 'rpm', '-i', str(download_path)], check=True)
                return self.create_wrapper(tool_name, tool_config)
            
            elif filename.endswith('.deb'):
                if self.is_admin:
                    subprocess.run(['dpkg', '-i', str(download_path)], check=True)
                else:
                    subprocess.run(['sudo', 'dpkg', '-i', str(download_path)], check=True)
                return self.create_wrapper(tool_name, tool_config)
            
            return False
        except Exception as e:
            self.log(f"  Binary download error: {e}", "RED")
            return False
    
    def install_via_installer(self, tool_name, tool_config):
        """Download and run official installer"""
        if 'installer_url' not in tool_config:
            return False
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        filename = tool_config['installer_url'].split('/')[-1]
        download_path = self.download_dir / filename
        
        if not download_path.exists():
            self.log(f"  Downloading installer: {filename}", "YELLOW")
            if not self.download_file(tool_config['installer_url'], download_path):
                return False
        
        if tool_name == 'nmap':
            self.log("\n  ðŸ”§ Nmap requires Npcap for packet capture functionality", "CYAN")
            if not self.install_npcap():
                self.log("  âš ï¸ Npcap installation may have issues, but continuing with Nmap...", "YELLOW")
        
        silent_args = tool_config.get('silent_args', '/S')
        
        self.log(f"  Running installer...", "YELLOW")
        
        try:
            if self.os_type == 'windows':
                if self.is_admin:
                    self.log("  Waiting for installation to complete (this may take a few minutes)...", "YELLOW")
                    
                    process = subprocess.Popen(
                        [str(download_path)] + silent_args.split(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    try:
                        stdout, stderr = process.communicate(timeout=600)
                        self.log("  âœ… Installation command completed", "GREEN")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        self.log("  âš ï¸ Installation timed out, but may still be in progress", "YELLOW")
                    
                    time.sleep(5)
                    
                else:
                    if self.run_as_admin(str(download_path), silent_args):
                        self.log("  âœ… Installer started with admin privileges", "GREEN")
                        time.sleep(30)
                    else:
                        self.log("  âš ï¸ Failed to elevate. Please run installer manually.", "YELLOW")
                        subprocess.Popen([str(download_path)])
                
                install_success = self.check_tool_installed(tool_name)
                if install_success:
                    self.log(f"  âœ… {tool_name} installed successfully", "GREEN")
                    self.add_tool_to_path(tool_name, tool_config)
                else:
                    self.log("  Waiting additional 30 seconds for installation to complete...", "YELLOW")
                    time.sleep(30)
                    if self.check_tool_installed(tool_name):
                        self.log(f"  âœ… {tool_name} installed successfully", "GREEN")
                        self.add_tool_to_path(tool_name, tool_config)
                    else:
                        self.log(f"  âš ï¸ {tool_name} may still be installing", "YELLOW")
                        self.add_tool_to_path(tool_name, tool_config)
                
            else:
                download_path.chmod(0o755)
                if self.is_admin:
                    subprocess.run([str(download_path), '--mode', 'unattended'], check=True, timeout=600)
                else:
                    subprocess.run(['sudo', str(download_path), '--mode', 'unattended'], check=True, timeout=600)
                self.add_tool_to_path(tool_name, tool_config)
            
            return self.create_wrapper(tool_name, tool_config)
        except subprocess.TimeoutExpired:
            self.log(f"  âš ï¸ Installation timed out after 10 minutes", "YELLOW")
            return self.create_wrapper(tool_name, tool_config)
        except Exception as e:
            self.log(f"  Installer error: {e}", "RED")
            return self.create_wrapper(tool_name, tool_config)
    
    def check_tool_installed(self, tool_name):
        """Check if tool is installed on system"""
        if tool_name == 'nmap':
            common_paths = [
                r"C:\Program Files\Nmap\nmap.exe",
                r"C:\Program Files (x86)\Nmap\nmap.exe"
            ]
            for path in common_paths:
                if Path(path).exists():
                    return True
        
        elif tool_name == 'metasploit':
            common_paths = [
                r"C:\metasploit-framework\msfconsole.bat",
                r"C:\metasploit-framework\bin\msfconsole.bat",
                r"C:\Program Files\metasploit-framework\msfconsole.bat"
            ]
            for path in common_paths:
                if Path(path).exists():
                    return True
        
        elif tool_name == 'whois':
            whois_path = self.tools_dir / "whois" / "whois.ps1"
            if whois_path.exists():
                return True
        
        return False
    
    def add_tool_to_path(self, tool_name, tool_config):
        """Automatically add tool installation directory to PATH"""
        if self.os_type != 'windows':
            return False
        
        if 'install_paths' not in tool_config:
            return False
        
        self.log(f"  ðŸ”§ Adding {tool_name} to PATH...", "CYAN")
        
        install_paths = tool_config['install_paths']
        executable_name = tool_config.get('executable_name', tool_config.get('executable', tool_name))
        found_path = None
        
        for install_path in install_paths:
            if Path(install_path).exists():
                found_path = install_path
                break
            test_path = Path(install_path) / executable_name
            if test_path.exists():
                found_path = install_path
                break
        
        if tool_name == 'whois' and not found_path:
            whois_path = self.tools_dir / "whois"
            if whois_path.exists():
                found_path = str(whois_path)
                self.log(f"  Found whois at: {found_path}", "GREEN")
        
        if found_path:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
                current_path, _ = winreg.QueryValueEx(key, "Path")
                winreg.CloseKey(key)
                
                if found_path not in current_path:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE)
                    new_path = f"{current_path};{found_path}"
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    winreg.CloseKey(key)
                    
                    os.environ['PATH'] = f"{os.environ.get('PATH', '')};{found_path}"
                    self.log(f"  âœ… Added {found_path} to PATH", "GREEN")
                else:
                    self.log(f"  âœ… {found_path} already in PATH", "GREEN")
            except Exception as e:
                self.log(f"  âš ï¸ Could not add to PATH: {e}", "YELLOW")
        else:
            self.log(f"  âš ï¸ Could not find {tool_name} installation directory", "YELLOW")
        
        self.update_wrapper_with_full_path(tool_name, tool_config, found_path)
        return True
    
    def update_wrapper_with_full_path(self, tool_name, tool_config, install_path):
        """Update wrapper to use full path to executable"""
        if not install_path:
            return False
        
        executable = tool_config.get('executable_name', tool_config.get('executable', tool_name))
        wrapper_path = self.bin_dir / f"{tool_name}.bat"
        
        if not wrapper_path.exists():
            return False
        
        full_exe_path = Path(install_path) / executable
        if full_exe_path.exists():
            content = f'''@echo off
"{full_exe_path}" %*
'''
            with open(wrapper_path, 'w', encoding='ascii') as f:
                f.write(content)
            self.log(f"  âœ… Updated wrapper to use: {full_exe_path}", "GREEN")
            return True
        
        if tool_name == 'whois':
            content = f'''@echo off
powershell -ExecutionPolicy Bypass -File "{Path(install_path) / executable}" %*
'''
            with open(wrapper_path, 'w', encoding='ascii') as f:
                f.write(content)
            self.log(f"  âœ… Updated whois wrapper to use PowerShell", "GREEN")
            return True
        
        return False
    
    def install_from_bundled(self, tool_name, tool_config):
        """Install from bundled package"""
        if not self.bundle_manager.is_bundle_available(tool_name):
            self.log(f"  No bundled package found for {tool_name}", "YELLOW")
            return False
        
        self.log(f"  Installing from bundled package...", "CYAN")
        return self.bundle_manager.install_from_bundle(tool_name, self)
    
    def install_via_docker(self, tool_name, tool_config):
        """Install using Docker"""
        if not self.check_docker():
            return False
        
        if 'docker_image' not in tool_config:
            return False
        
        try:
            self.log(f"  Pulling Docker image: {tool_config['docker_image']}", "YELLOW")
            subprocess.run(['docker', 'pull', tool_config['docker_image']], check=True)
            
            wrapper_path = self.bin_dir / f"{tool_name}.bat" if self.os_type == 'windows' else self.bin_dir / tool_name
            
            if self.os_type == 'windows':
                content = f'''@echo off
docker run --rm -it {tool_config['docker_image']} %*
'''
            else:
                content = f'''#!/bin/bash
docker run --rm -it {tool_config['docker_image']} "$@"
'''
            
            with open(wrapper_path, 'w') as f:
                f.write(content)
            
            if self.os_type != 'windows':
                wrapper_path.chmod(0o755)
            
            return True
        except Exception as e:
            self.log(f"  Docker error: {e}", "RED")
            return False
    
    def install_embedded_script(self, tool_name, tool_config):
        """Create embedded script"""
        tool_path = self.tools_dir / tool_name
        tool_path.mkdir(parents=True, exist_ok=True)
        
        if tool_name == 'whois':
            if self.os_type == 'windows':
                script_path = tool_path / "whois.ps1"
                script_content = '''param(
    [Parameter(Mandatory=$true)]
    [string]$Domain
)

$whoisServer = "whois.internic.net"
try {
    $tcp = New-Object System.Net.Sockets.TcpClient($whoisServer, 43)
    $stream = $tcp.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $writer.WriteLine($Domain)
    $writer.Flush()
    
    $reader = New-Object System.IO.StreamReader($stream)
    while ($line = $reader.ReadLine()) {
        if ($line -match "^>") { continue }
        Write-Host $line
    }
    
    $reader.Close()
    $writer.Close()
    $tcp.Close()
} catch {
    Write-Error "Error querying WHOIS: $_"
}
'''
                with open(script_path, 'w') as f:
                    f.write(script_content)
            else:
                script_path = tool_path / "whois.py"
                script_content = '''#!/usr/bin/env python3
import socket
import sys

def whois(domain):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("whois.internic.net", 43))
        s.send((domain + "\\r\\n").encode())
        response = s.recv(4096).decode()
        s.close()
        return response
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(whois(sys.argv[1]))
    else:
        print("Usage: whois <domain>")
'''
                with open(script_path, 'w') as f:
                    f.write(script_content)
                script_path.chmod(0o755)
            
            self.add_tool_to_path(tool_name, tool_config)
            return self.create_wrapper(tool_name, tool_config)
        
        return False
    
    def create_stub_tool(self, tool_name, tool_config):
        """Create a stub tool with instructions"""
        tool_path = self.tools_dir / tool_name
        tool_path.mkdir(parents=True, exist_ok=True)
        
        readme_path = tool_path / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(f"{tool_name} - Tool Not Installed\n")
            f.write("=" * 40 + "\n\n")
            f.write("This tool was not automatically installed.\n\n")
            f.write("To install manually:\n")
            
            if tool_name == 'metasploit':
                f.write("1. Download from: https://www.metasploit.com/\n")
                f.write("2. Or install via: gem install metasploit-framework\n")
                if self.os_type == 'windows':
                    f.write("3. Or install via: choco install metasploit -y (Admin required)\n")
                else:
                    f.write("3. Or install via: apt-get install metasploit-framework\n")
            elif tool_name == 'nmap':
                f.write("1. Download from: https://nmap.org/download.html\n")
                if self.os_type == 'windows':
                    f.write("2. Or install via: choco install nmap -y (Admin required)\n")
                    f.write("3. Also install Npcap: https://npcap.com/\n")
                else:
                    f.write("2. Or install via: apt-get install nmap\n")
            elif tool_name == 'nikto':
                f.write("1. Clone from: git clone https://github.com/sullo/nikto.git\n")
                if self.os_type == 'windows':
                    f.write("2. Or install via: choco install nikto -y (Admin required)\n")
                else:
                    f.write("2. Or install via: apt-get install nikto\n")
            elif tool_name == 'whois':
                if self.os_type == 'windows':
                    f.write("1. Download from: https://docs.microsoft.com/en-us/sysinternals/downloads/whois\n")
                else:
                    f.write("1. Or install via: apt-get install whois\n")
        
        return self.create_wrapper(tool_name, tool_config)
    
    def create_wrapper(self, tool_name, tool_config):
        """Create wrapper scripts for tools"""
        wrapper_ext = tool_config.get('wrapper_ext', '.bat' if self.os_type == 'windows' else '')
        wrapper_name = f"{tool_name}{wrapper_ext}"
        wrapper_path = self.bin_dir / wrapper_name
        wrapper_path.parent.mkdir(parents=True, exist_ok=True)
        
        executable = tool_config.get('executable_name', tool_config.get('executable', tool_name))
        tool_path = self.tools_dir / tool_name
        
        exec_path = None
        
        if self.os_type != 'windows':
            if shutil.which(executable):
                exec_path = Path(shutil.which(executable))
        
        if not exec_path and 'install_paths' in tool_config:
            for install_path in tool_config['install_paths']:
                test_path = Path(install_path) / executable
                if test_path.exists():
                    exec_path = test_path
                    break
        
        if not exec_path:
            for ext in ['', '.py', '.pl', '.ps1', '.exe', '.sh', '.bat']:
                test_path = tool_path / f"{executable}{ext}"
                if test_path.exists():
                    exec_path = test_path
                    break
            if not exec_path:
                for file in tool_path.glob('*'):
                    if file.is_file() and not file.suffix in ['.txt', '.md', '.json']:
                        exec_path = file
                        break
        
        if exec_path:
            if exec_path.suffix == '.py':
                cmd = f'python3 "{exec_path}"' if self.os_type != 'windows' else f'python "{exec_path}"'
            elif exec_path.suffix == '.pl':
                cmd = f'perl "{exec_path}"'
            elif exec_path.suffix == '.ps1':
                cmd = f'powershell -ExecutionPolicy Bypass -File "{exec_path}"'
            elif exec_path.suffix == '.sh':
                cmd = f'bash "{exec_path}"'
            else:
                cmd = f'"{exec_path}"'
        else:
            if shutil.which(tool_name):
                cmd = shutil.which(tool_name)
            else:
                if self.os_type == 'windows':
                    cmd = f'echo "{tool_name} not found. See {tool_path}\\README.txt for instructions"'
                else:
                    cmd = f'echo "{tool_name} not found. See {tool_path}/README.txt for instructions"'
        
        if self.os_type == 'windows':
            content = f'''@echo off
{cmd} %*
'''
        else:
            content = f'''#!/bin/bash
{cmd} "$@"
'''
        
        with open(wrapper_path, 'w', encoding='ascii') as f:
            f.write(content)
        
        if self.os_type != 'windows':
            wrapper_path.chmod(0o755)
        
        return True
    
    def smart_install(self, tool_name):
        """Intelligently install a tool using best available method"""
        if tool_name not in self.tool_definitions:
            self.log(f"  âš ï¸ Unknown tool: {tool_name}", "RED")
            return False
        
        tool_config = self.tool_definitions[tool_name]
        self.log(f"\nðŸ”§ Installing {tool_name}...", "CYAN")
        
        # Check if tool needs admin and warn
        if tool_config.get('needs_admin', False) and not self.is_admin:
            self.log("  âš ï¸ This tool requires administrator privileges", "YELLOW")
            self.log("  Will attempt to auto-elevate and install...", "YELLOW")
        
        # Try strategies in priority order
        for strategy in tool_config['priority']:
            if strategy in self.strategies:
                self.log(f"  ðŸ“¦ Trying: {strategy}", "YELLOW")
                try:
                    result = self.strategies[strategy](tool_name, tool_config)
                    if result:
                        self.log(f"  âœ… {tool_name} installed successfully", "GREEN")
                        self.log_installation(tool_name, strategy)
                        return True
                    else:
                        self.log(f"  âŒ Failed via {strategy}", "RED")
                except Exception as e:
                    self.log(f"  âŒ Error: {e}", "RED")
        
        self.log(f"  âš ï¸ Could not install {tool_name}", "RED")
        return False
    
    def install_all(self):
        """Install all tools"""
        self.log("=" * 60, "CYAN")
        self.log(f"ðŸš€ DSTerminal Smart Installer - {platform.system()} {platform.release()}", "CYAN")
        self.log("=" * 60, "CYAN")
        
        env = self.detect_environment()
        self.log("\nðŸ“Š Environment Detection:", "CYAN")
        for key, value in env.items():
            self.log(f"  {key}: {value}")
        
        # Show bundled packages
        bundled = self.bundle_manager.list_bundled_packages()
        if bundled:
            self.log(f"\nðŸ“¦ Bundled packages available: {', '.join(bundled)}", "GREEN")
            self.log("   These will be installed first before downloading.", "GREEN")
        
        if not self.is_admin:
            self.log("\nâš ï¸ Running without administrator/root privileges", "YELLOW")
            self.log("   But the installer will attempt to auto-elevate when needed", "YELLOW")
            self.log("   You may see UAC prompts for admin access", "YELLOW")
        
        self.setup_directories()
        
        results = {}
        for tool in self.tool_definitions:
            results[tool] = self.smart_install(tool)
        
        self.log("\n" + "=" * 60, "CYAN")
        self.log("ðŸ“Š Installation Summary:", "CYAN")
        self.log("=" * 60, "CYAN")
        for tool, success in results.items():
            status = "âœ…" if success else "âŒ"
            self.log(f"  {status} {tool}")
        
        self.log(f"\nðŸ“ Installation Directory:", "CYAN")
        self.log(f"  {self.install_dir}")
        self.log(f"  Binaries: {self.bin_dir}")
        
        self.add_to_path()
        self.print_usage_instructions(results)
        self.print_post_install_notes(results)
        
        self.log("\n" + "=" * 60, "CYAN")
        self.log("ðŸŽ‰ Installation Complete!", "CYAN")
        self.log("=" * 60, "CYAN")
        
        return results
    
    def setup_directories(self):
        """Create directories"""
        for dir_path in [self.install_dir, self.bin_dir, self.tools_dir, self.config_dir, self.download_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def add_to_path(self):
        """Add DSTerminal bin directory to system PATH"""
        bin_path = str(self.bin_dir)
        
        if self.os_type == 'windows':
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
                current_path = winreg.QueryValueEx(key, "Path")[0]
                
                if bin_path not in current_path:
                    new_path = f"{current_path};{bin_path}"
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    winreg.CloseKey(key)
                    os.environ['PATH'] = f"{os.environ.get('PATH', '')};{bin_path}"
                    self.log(f"\nâœ… Added {bin_path} to user PATH", "GREEN")
                    self.log("   Please restart your terminal for changes to take effect", "YELLOW")
                else:
                    self.log(f"\nâœ… {bin_path} already in PATH", "GREEN")
            except Exception as e:
                self.log(f"\nâš ï¸ Could not update PATH: {e}", "YELLOW")
                self.log(f"   Please manually add this to your PATH:", "YELLOW")
                self.log(f"   {bin_path}", "YELLOW")
                self.log(f'\n   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";{bin_path}", "User")', "YELLOW")
        else:
            for rc in ['.bashrc', '.zshrc', '.profile', '.bash_profile']:
                rc_path = Path.home() / rc
                if rc_path.exists():
                    with open(rc_path, 'a') as f:
                        f.write(f'\n# DSTerminal\n')
                        f.write(f'export PATH="{bin_path}:$PATH"\n')
                    self.log(f"\nâœ… Added to {rc}", "GREEN")
                    self.log(f"   Run: source {rc}", "YELLOW")
                    return
            
            self.log(f"\nâš ï¸ Could not find shell config. Please add {bin_path} to PATH manually.", "YELLOW")
    
    def print_usage_instructions(self, results):
        """Print usage instructions"""
        self.log("\nðŸ“– Usage Instructions:", "CYAN")
        self.log("-" * 40, "CYAN")
        
        for tool, success in results.items():
            if success:
                if tool == 'sqlmap':
                    self.log(f"  sqlmap: sqlmap --help")
                elif tool == 'nikto':
                    self.log(f"  nikto: nikto -h <host>")
                elif tool == 'nmap':
                    self.log(f"  nmap: nmap -A <target>")
                elif tool == 'metasploit':
                    self.log(f"  metasploit: msfconsole")
                elif tool == 'whois':
                    self.log(f"  whois: whois <domain>")
    
    def print_post_install_notes(self, results):
        """Print post-installation notes"""
        self.log("\nðŸ“ Post-Installation Notes:", "CYAN")
        self.log("-" * 40, "CYAN")
        
        if self.os_type == 'windows' and not self.is_admin:
            self.log("  âš ï¸ Some tools may have triggered UAC prompts", "YELLOW")
            self.log("  Please check if any installation wizards are still open", "YELLOW")
            if not results.get('nmap', False):
                self.log(f"    - Nmap installer: {self.download_dir / 'nmap-7.95-setup.exe'}")
            if not results.get('metasploit', False):
                self.log(f"    - Metasploit installer: {self.download_dir / 'metasploit-latest-windows-x64-installer.exe'}")
        
        if self.os_type == 'windows':
            if not self.check_npcap_installed():
                self.log("\n  âš ï¸ Npcap is not installed (required for Nmap scanning)", "YELLOW")
                self.log("  Download from: https://npcap.com/", "YELLOW")
        
        whois_path = str(self.tools_dir / "whois")
        if whois_path not in os.environ.get('PATH', ''):
            self.log(f"\n  ðŸ’¡ To use whois, add this to PATH:", "YELLOW")
            self.log(f'    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";{whois_path}", "User")', "YELLOW")
        
        self.log("\n  ðŸ’¡ To add tools to PATH permanently:", "YELLOW")
        if self.os_type == 'windows':
            self.log(f'    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";{self.bin_dir}", "User")', "YELLOW")
        else:
            self.log(f'    echo \'export PATH="{self.bin_dir}:$PATH"\' >> ~/.bashrc', "YELLOW")
            self.log('    source ~/.bashrc', "YELLOW")
    
    def log_installation(self, tool_name, method):
        """Log installation"""
        log_file = self.config_dir / 'install_log.json'
        log_data = {}
        if log_file.exists():
            try:
                with open(log_file) as f:
                    log_data = json.load(f)
            except:
                pass
        
        log_data[tool_name] = {
            'method': method,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'os': self.os_type,
            'admin': self.is_admin
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)


# ============================================================
# DSTERMINAL COMMAND LINE INTERFACE
# ============================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='DSTerminal - Security Tools Management Console',
        epilog='Run without arguments to enter interactive mode'
    )
    parser.add_argument(
        '--install-all',
        action='store_true',
        help='Install all tools and exit'
    )
    parser.add_argument(
        '--install',
        nargs='+',
        help='Install specific tools (space separated)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check installation status and exit'
    )
    parser.add_argument(
        '--list-bundles',
        action='store_true',
        help='List available bundled packages'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    args = parser.parse_args()
    
    # Handle bundle listing
    if args.list_bundles:
        bundle_manager = BundledPackageManager()
        available = bundle_manager.list_bundled_packages()
        print("\nðŸ“¦ Available Bundled Packages:")
        print("-" * 40)
        for package in bundle_manager.bundle_structure:
            status = "âœ…" if package in available else "âŒ"
            size = bundle_manager.get_bundle_size(package)
            size_str = f"({size:.2f} MB)" if size > 0 else ""
            print(f"  {status} {package:<12} {size_str}")
        return
    
    # Handle installation
    installer = SmartDSTerminalInstaller(verbose=not args.quiet)
    
    if args.install_all:
        installer.install_all()
    elif args.install:
        for tool in args.install:
            installer.smart_install(tool)
    elif args.check:
        # Check installation status
        print("\nðŸ” Tool Status:")
        print("-" * 40)
        for tool in installer.tool_definitions:
            installed = installer.check_tool_installed(tool)
            bundled = installer.bundle_manager.is_bundle_available(tool)
            status = "âœ…" if installed else ("ðŸ“¦" if bundled else "âŒ")
            print(f"  {status} {tool:<12} {'Installed' if installed else ('Bundled' if bundled else 'Missing')}")
    else:
        # Interactive mode
        print("=" * 60)
        print("ðŸš€ DSTerminal - Security Tools Management Console")
        print("=" * 60)
        print(f"OS: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        
        # Show bundled packages
        bundle_manager = BundledPackageManager()
        available = bundle_manager.list_bundled_packages()
        if available:
            print(f"\nðŸ“¦ Bundled packages available: {', '.join(available)}")
            print("   These will be used first during installation.")
        
        print("\nðŸ“‹ Commands:")
        print("  --install-all    Install all tools")
        print("  --install <tool> Install specific tool")
        print("  --check          Check tool status")
        print("  --list-bundles   List bundled packages")
        print("  --help           Show this help")
        print("\nExample: python dsterminal.py --install-all")
        print("=" * 60)


if __name__ == "__main__":
    main()