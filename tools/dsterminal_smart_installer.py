#!python
﻿# dsterminal_smart_installer.py
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

class SmartDSTerminalInstaller:
    """
    The Ultimate DSTerminal Installer - Full Auto Installation with Npcap Support
    """
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.arch = platform.machine()
        self.install_dir = Path.home() / "DSTerminal"
        self.bin_dir = self.install_dir / "bin"
        self.tools_dir = self.install_dir / "tools"
        self.config_dir = self.install_dir / "config"
        self.download_dir = self.install_dir / "downloads"
        
        # Check admin/sudo status
        self.is_admin = self.check_admin()
        
        # OS-specific tool definitions
        self.tool_definitions = self.get_os_specific_tools()
        
        # Installation strategies
        self.strategies = {
            'package_manager': self.install_via_package_manager,
            'python_pip': self.install_via_pip,
            'git_clone': self.install_via_git,
            'binary_download': self.install_via_binary_download,
            'installer_download': self.install_via_installer,
            'bundled': self.install_from_bundled,
            'docker': self.install_via_docker,
            'embedded_script': self.install_embedded_script
        }
    
    def get_os_specific_tools(self):
        """Get OS-specific tool definitions"""
        if self.os_type == 'windows':
            return {
                'sqlmap': {
                    'priority': ['python_pip', 'git_clone', 'bundled'],
                    'pip_package': 'sqlmap',
                    'git_url': 'https://github.com/sqlmapproject/sqlmap.git',
                    'executable': 'sqlmap.py',
                    'wrapper_ext': '.bat'
                },
                'nikto': {
                    'priority': ['git_clone', 'bundled'],
                    'git_url': 'https://github.com/sullo/nikto.git',
                    'executable': 'nikto.pl',
                    'wrapper_ext': '.bat'
                },
                'nmap': {
                    'priority': ['installer_download', 'bundled'],
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
                    'priority': ['installer_download', 'bundled'],
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
                    'priority': ['embedded_script', 'bundled'],
                    'executable': 'whois.ps1',
                    'wrapper_ext': '.bat',
                    'install_paths': [
                        str(Path.home() / "DSTerminal" / "tools" / "whois")
                    ],
                    'executable_name': 'whois.ps1'
                }
            }
        elif self.os_type == 'darwin':  # macOS
            return {
                'sqlmap': {
                    'priority': ['python_pip', 'git_clone', 'bundled'],
                    'pip_package': 'sqlmap',
                    'git_url': 'https://github.com/sqlmapproject/sqlmap.git',
                    'executable': 'sqlmap.py',
                    'wrapper_ext': ''
                },
                'nikto': {
                    'priority': ['package_manager', 'git_clone', 'bundled'],
                    'package_names': {'brew': 'nikto'},
                    'git_url': 'https://github.com/sullo/nikto.git',
                    'executable': 'nikto.pl',
                    'wrapper_ext': ''
                },
                'nmap': {
                    'priority': ['package_manager', 'binary_download', 'bundled'],
                    'package_names': {'brew': 'nmap'},
                    'download_url': 'https://nmap.org/dist/nmap-7.95-{os}-{arch}.{ext}',
                    'executable': 'nmap',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/local/bin', '/opt/local/bin']
                },
                'metasploit': {
                    'priority': ['installer_download', 'docker', 'bundled'],
                    'installer_url': 'https://downloads.metasploit.com/data/releases/metasploit-latest-{os}-{arch}.{ext}',
                    'docker_image': 'metasploitframework/metasploit-framework',
                    'executable': 'msfconsole',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/local/bin', '/opt/metasploit-framework/bin']
                },
                'whois': {
                    'priority': ['package_manager', 'bundled'],
                    'package_names': {'brew': 'whois'},
                    'executable': 'whois',
                    'wrapper_ext': ''
                }
            }
        else:  # Linux and others
            return {
                'sqlmap': {
                    'priority': ['python_pip', 'git_clone', 'bundled'],
                    'pip_package': 'sqlmap',
                    'git_url': 'https://github.com/sqlmapproject/sqlmap.git',
                    'executable': 'sqlmap.py',
                    'wrapper_ext': ''
                },
                'nikto': {
                    'priority': ['package_manager', 'git_clone', 'bundled'],
                    'package_names': {'apt': 'nikto', 'yum': 'nikto', 'dnf': 'nikto'},
                    'git_url': 'https://github.com/sullo/nikto.git',
                    'executable': 'nikto.pl',
                    'wrapper_ext': ''
                },
                'nmap': {
                    'priority': ['package_manager', 'binary_download', 'bundled'],
                    'package_names': {'apt': 'nmap', 'yum': 'nmap', 'dnf': 'nmap'},
                    'download_url': 'https://nmap.org/dist/nmap-7.95-{os}-{arch}.{ext}',
                    'executable': 'nmap',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/bin', '/usr/local/bin']
                },
                'metasploit': {
                    'priority': ['installer_download', 'docker', 'bundled'],
                    'installer_url': 'https://downloads.metasploit.com/data/releases/metasploit-latest-{os}-{arch}.{ext}',
                    'docker_image': 'metasploitframework/metasploit-framework',
                    'executable': 'msfconsole',
                    'wrapper_ext': '',
                    'install_paths': ['/usr/local/bin', '/opt/metasploit-framework/bin']
                },
                'whois': {
                    'priority': ['package_manager', 'bundled'],
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
            print(f"  Admin elevation error: {e}")
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
            
            if show_progress and total_size > 0:
                print(f"  Downloading: {url.split('/')[-1]} ({total_size // (1024*1024)} MB)")
                
                downloaded = 0
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (10 * 1024 * 1024) == 0:
                            print(f"    Progress: {downloaded // (1024 * 1024)} MB")
            else:
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            return True
        except Exception as e:
            print(f"  Download error: {e}")
            return False
    
    def install_npcap(self):
        """Download and install Npcap"""
        print("\n  ðŸ“¦ Installing Npcap (required for Nmap)...")
        
        # Check if already installed
        if self.check_npcap_installed():
            print("  âœ… Npcap is already installed")
            return True
        
        npcap_url = self.tool_definitions['nmap'].get('npcap_url', 'https://npcap.com/dist/npcap-1.79.exe')
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        filename = npcap_url.split('/')[-1]
        download_path = self.download_dir / filename
        
        # Download Npcap
        if not download_path.exists():
            print(f"  Downloading Npcap installer...")
            if not self.download_file(npcap_url, download_path):
                print("  âŒ Failed to download Npcap")
                return False
        
        # Install Npcap silently
        print(f"  Installing Npcap silently...")
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
                    print("  âœ… Npcap installation completed")
                    return True
                except subprocess.TimeoutExpired:
                    process.kill()
                    print("  âš ï¸ Npcap installation timed out")
                    return False
            else:
                if self.run_as_admin(str(download_path), args):
                    print("  âœ… Npcap installer started with admin privileges")
                    time.sleep(10)
                    return True
                else:
                    print("  âŒ Failed to elevate for Npcap installation")
                    return False
        except Exception as e:
            print(f"  âŒ Npcap installation error: {e}")
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
                    print(f"  Installing via {mgr}: {package_name}")
                    
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
                            print("  âš ï¸ Chocolatey requires admin privileges")
                            return False
                    
                    elif mgr == 'winget':
                        subprocess.run(['winget', 'install', package_name, '--silent'], check=True)
                        return True
                        
                except Exception as e:
                    print(f"  Package manager error: {e}")
                    continue
        
        return False
    
    def install_via_pip(self, tool_name, tool_config):
        """Install using pip"""
        if 'pip_package' not in tool_config:
            return False
        
        try:
            print(f"  Installing via pip: {tool_config['pip_package']}")
            subprocess.run([sys.executable, '-m', 'pip', 'install', tool_config['pip_package']], 
                         check=True, capture_output=True)
            return self.create_wrapper(tool_name, tool_config)
        except Exception as e:
            print(f"  Pip error: {e}")
            return False
    
    def install_via_git(self, tool_name, tool_config):
        """Clone from git"""
        if 'git_url' not in tool_config:
            return False
        
        if not self.check_git():
            print("  Git not installed. Skipping git clone.")
            return False
        
        tool_path = self.tools_dir / tool_name
        try:
            # Remove existing directory if it exists
            if tool_path.exists():
                try:
                    shutil.rmtree(tool_path)
                    print(f"  Removed existing directory: {tool_path}")
                except PermissionError:
                    print(f"  âš ï¸ Permission denied removing {tool_path}")
                    print("  Attempting to clone into a new location...")
                    # Use a different name
                    tool_path = self.tools_dir / f"{tool_name}_new"
                    if tool_path.exists():
                        shutil.rmtree(tool_path)
            
            print(f"  Cloning from: {tool_config['git_url']}")
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', tool_config['git_url'], str(tool_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"  Git error: {result.stderr}")
                return False
            
            return self.create_wrapper(tool_name, tool_config)
        except Exception as e:
            print(f"  Git error: {e}")
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
                    print("  âš ï¸ Admin rights needed for installation")
                    print(f"  Please run: {download_path}")
                return self.create_wrapper(tool_name, tool_config)
            
            elif filename.endswith('.dmg'):
                print("  Mounting DMG...")
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
            print(f"  Binary download error: {e}")
            return False
    
    def install_via_installer(self, tool_name, tool_config):
        """Download and run official installer"""
        if 'installer_url' not in tool_config:
            return False
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        filename = tool_config['installer_url'].split('/')[-1]
        download_path = self.download_dir / filename
        
        # Download if not exists
        if not download_path.exists():
            print(f"  Downloading installer: {filename}")
            if not self.download_file(tool_config['installer_url'], download_path):
                return False
        
        # For Nmap, also install Npcap first
        if tool_name == 'nmap':
            print("\n  ðŸ”§ Nmap requires Npcap for packet capture functionality")
            if not self.install_npcap():
                print("  âš ï¸ Npcap installation may have issues, but continuing with Nmap...")
        
        # Get silent args - ONLY for the installer, not for git!
        silent_args = tool_config.get('silent_args', '/S')
        
        print(f"  Running installer...")
        
        try:
            if self.os_type == 'windows':
                if self.is_admin:
                    print("  Waiting for installation to complete (this may take a few minutes)...")
                    
                    # Run installer with silent args
                    process = subprocess.Popen(
                        [str(download_path)] + silent_args.split(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    try:
                        stdout, stderr = process.communicate(timeout=600)
                        print("  âœ… Installation command completed")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        print("  âš ï¸ Installation timed out, but may still be in progress")
                    
                    time.sleep(5)
                    
                else:
                    if self.run_as_admin(str(download_path), silent_args):
                        print("  âœ… Installer started with admin privileges")
                        time.sleep(30)
                    else:
                        print("  âš ï¸ Failed to elevate. Please run installer manually.")
                        subprocess.Popen([str(download_path)])
                
                # Check if installed and add to PATH
                install_success = self.check_tool_installed(tool_name)
                if install_success:
                    print(f"  âœ… {tool_name} installed successfully")
                    self.add_tool_to_path(tool_name, tool_config)
                else:
                    print("  Waiting additional 30 seconds for installation to complete...")
                    time.sleep(30)
                    if self.check_tool_installed(tool_name):
                        print(f"  âœ… {tool_name} installed successfully")
                        self.add_tool_to_path(tool_name, tool_config)
                    else:
                        print(f"  âš ï¸ {tool_name} may still be installing")
                        self.add_tool_to_path(tool_name, tool_config)
                
            else:
                # Linux/Mac
                download_path.chmod(0o755)
                if self.is_admin:
                    subprocess.run([str(download_path), '--mode', 'unattended'], check=True, timeout=600)
                else:
                    subprocess.run(['sudo', str(download_path), '--mode', 'unattended'], check=True, timeout=600)
                self.add_tool_to_path(tool_name, tool_config)
            
            return self.create_wrapper(tool_name, tool_config)
        except subprocess.TimeoutExpired:
            print(f"  âš ï¸ Installation timed out after 10 minutes")
            return self.create_wrapper(tool_name, tool_config)
        except Exception as e:
            print(f"  Installer error: {e}")
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
            # Check if whois script exists
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
        
        print(f"  ðŸ”§ Adding {tool_name} to PATH...")
        
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
        
        # Special handling for whois - use tools directory
        if tool_name == 'whois' and not found_path:
            whois_path = self.tools_dir / "whois"
            if whois_path.exists():
                found_path = str(whois_path)
                print(f"  Found whois at: {found_path}")
        
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
                    print(f"  âœ… Added {found_path} to PATH")
                else:
                    print(f"  âœ… {found_path} already in PATH")
            except Exception as e:
                print(f"  âš ï¸ Could not add to PATH: {e}")
        else:
            print(f"  âš ï¸ Could not find {tool_name} installation directory")
        
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
            print(f"  âœ… Updated wrapper to use: {full_exe_path}")
            return True
        
        # For whois, use powershell to run the script
        if tool_name == 'whois':
            content = f'''@echo off
powershell -ExecutionPolicy Bypass -File "{Path(install_path) / executable}" %*
'''
            with open(wrapper_path, 'w', encoding='ascii') as f:
                f.write(content)
            print(f"  âœ… Updated whois wrapper to use PowerShell")
            return True
        
        return False
    
    def install_from_bundled(self, tool_name, tool_config):
        """Extract from bundled resources"""
        bundle_path = Path(__file__).parent / 'bundled' / tool_name
        
        if not bundle_path.exists():
            print("  No bundled files found, creating stub...")
            return self.create_stub_tool(tool_name, tool_config)
        
        target_path = self.tools_dir / tool_name
        try:
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(bundle_path, target_path)
            return self.create_wrapper(tool_name, tool_config)
        except Exception as e:
            print(f"  Bundled extraction error: {e}")
            return False
    
    def install_via_docker(self, tool_name, tool_config):
        """Install using Docker"""
        if not self.check_docker():
            return False
        
        if 'docker_image' not in tool_config:
            return False
        
        try:
            print(f"  Pulling Docker image: {tool_config['docker_image']}")
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
            print(f"  Docker error: {e}")
            return False
    
    def install_embedded_script(self, tool_name, tool_config):
        """Create embedded script"""
        tool_path = self.tools_dir / tool_name
        tool_path.mkdir(parents=True, exist_ok=True)
        
        if tool_name == 'whois':
            if self.os_type == 'windows':
                # PowerShell WHOIS script
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
                # Python WHOIS script for Linux/Mac
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
            
            # Add whois to PATH after installation
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
        
        # Check system paths
        if self.os_type != 'windows':
            if shutil.which(executable):
                exec_path = Path(shutil.which(executable))
        
        # Check common installation paths
        if not exec_path and 'install_paths' in tool_config:
            for install_path in tool_config['install_paths']:
                test_path = Path(install_path) / executable
                if test_path.exists():
                    exec_path = test_path
                    break
        
        # Check tools directory
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
        """Install tool using best method"""
        if tool_name not in self.tool_definitions:
            print(f"  âš ï¸ Unknown tool: {tool_name}")
            return False
        
        tool_config = self.tool_definitions[tool_name]
        print(f"\nðŸ”§ Installing {tool_name}...")
        
        if tool_config.get('needs_admin', False) and not self.is_admin:
            print("  âš ï¸ This tool requires administrator privileges")
            print("  Will attempt to auto-elevate and install...")
        
        for strategy in tool_config['priority']:
            if strategy in self.strategies:
                print(f"  ðŸ“¦ Trying: {strategy}")
                try:
                    result = self.strategies[strategy](tool_name, tool_config)
                    if result:
                        print(f"  âœ… {tool_name} installed successfully")
                        self.log_installation(tool_name, strategy)
                        return True
                    else:
                        print(f"  âŒ Failed via {strategy}")
                except Exception as e:
                    print(f"  âŒ Error: {e}")
        
        print(f"  âš ï¸ Could not install {tool_name}")
        return False
    
    def install_all(self):
        """Install all tools"""
        print("=" * 60)
        print(f"ðŸš€ DSTerminal Smart Installer - {platform.system()} {platform.release()}")
        print("=" * 60)
        
        env = self.detect_environment()
        print("\nðŸ“Š Environment Detection:")
        for key, value in env.items():
            print(f"  {key}: {value}")
        
        if not self.is_admin:
            print("\nâš ï¸ Running without administrator/root privileges")
            print("   But the installer will attempt to auto-elevate when needed")
            print("   You may see UAC prompts for admin access")
        
        self.setup_directories()
        
        results = {}
        for tool in self.tool_definitions:
            results[tool] = self.smart_install(tool)
        
        print("\n" + "=" * 60)
        print("ðŸ“Š Installation Summary:")
        print("=" * 60)
        for tool, success in results.items():
            status = "âœ…" if success else "âŒ"
            print(f"  {status} {tool}")
        
        print(f"\nðŸ“ Installation Directory:")
        print(f"  {self.install_dir}")
        print(f"  Binaries: {self.bin_dir}")
        
        self.add_to_path()
        self.print_usage_instructions(results)
        self.print_post_install_notes(results)
        
        print("\n" + "=" * 60)
        print("ðŸŽ‰ Installation Complete!")
        print("=" * 60)
        
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
                    print(f"\nâœ… Added {bin_path} to user PATH")
                    print("   Please restart your terminal for changes to take effect")
                else:
                    print(f"\nâœ… {bin_path} already in PATH")
            except Exception as e:
                print(f"\nâš ï¸ Could not update PATH: {e}")
                print(f"   Please manually add this to your PATH:")
                print(f"   {bin_path}")
                print(f'\n   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";{bin_path}", "User")')
        else:
            for rc in ['.bashrc', '.zshrc', '.profile', '.bash_profile']:
                rc_path = Path.home() / rc
                if rc_path.exists():
                    with open(rc_path, 'a') as f:
                        f.write(f'\n# DSTerminal\n')
                        f.write(f'export PATH="{bin_path}:$PATH"\n')
                    print(f"\nâœ… Added to {rc}")
                    print(f"   Run: source {rc}")
                    return
            
            print(f"\nâš ï¸ Could not find shell config. Please add {bin_path} to PATH manually.")
    
    def print_usage_instructions(self, results):
        """Print usage instructions"""
        print("\nðŸ“– Usage Instructions:")
        print("-" * 40)
        
        for tool, success in results.items():
            if success:
                if tool == 'sqlmap':
                    print(f"  sqlmap: sqlmap --help")
                elif tool == 'nikto':
                    print(f"  nikto: nikto -h <host>")
                elif tool == 'nmap':
                    print(f"  nmap: nmap -A <target>")
                elif tool == 'metasploit':
                    print(f"  metasploit: msfconsole")
                elif tool == 'whois':
                    print(f"  whois: whois <domain>")
    
    def print_post_install_notes(self, results):
        """Print post-installation notes"""
        print("\nðŸ“ Post-Installation Notes:")
        print("-" * 40)
        
        if self.os_type == 'windows' and not self.is_admin:
            print("  âš ï¸ Some tools may have triggered UAC prompts")
            print("  Please check if any installation wizards are still open")
            if not results.get('nmap', False):
                print(f"    - Nmap installer: {self.download_dir / 'nmap-7.95-setup.exe'}")
            if not results.get('metasploit', False):
                print(f"    - Metasploit installer: {self.download_dir / 'metasploit-latest-windows-x64-installer.exe'}")
        
        if self.os_type == 'windows':
            if not self.check_npcap_installed():
                print("\n  âš ï¸ Npcap is not installed (required for Nmap scanning)")
                print("  Download from: https://npcap.com/")
        
        # Check if whois is in PATH
        whois_path = str(self.tools_dir / "whois")
        if whois_path not in os.environ.get('PATH', ''):
            print(f"\n  ðŸ’¡ To use whois, add this to PATH:")
            print(f'    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";{whois_path}", "User")')
        
        print("\n  ðŸ’¡ To add tools to PATH permanently:")
        if self.os_type == 'windows':
            print(f'    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";{self.bin_dir}", "User")')
        else:
            print(f'    echo \'export PATH="{self.bin_dir}:$PATH"\' >> ~/.bashrc')
            print('    source ~/.bashrc')
    
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

# Main execution
if __name__ == "__main__":
    installer = SmartDSTerminalInstaller()
    installer.install_all()