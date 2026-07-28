#!/usr/bin/env python3
"""
DSTERMINAL Complete Installer - Automatically installs DSTERMINAL and all dependencies
"""

import subprocess
import sys
import os
import platform
import shutil
import site
from pathlib import Path

class DSTERMINALInstaller:
    def __init__(self):
        self.system = platform.system()
        self.is_admin = self.check_admin()
        self.install_path = os.path.expanduser("~/DSTERMINAL")
        self.dependencies_installed = False
        
    def check_admin(self):
        """Check if running with admin/root privileges"""
        if self.system == "Windows":
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:  # Linux/Mac
            return os.geteuid() == 0
    
    def print_banner(self):
        """Display installer banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗
║   ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║
║   ██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║
║   ██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║
║   ██████╔╝███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
║   ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
║                                                              ║
║                    COMPLETE INSTALLER v2.0                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"\n{'='*60}")
        print(f"System: {self.system}")
        print(f"Install Path: {self.install_path}")
        print(f"Admin Rights: {'Yes' if self.is_admin else 'No'}")
        print(f"{'='*60}\n")
    
    def check_dependencies(self):
        """Check which dependencies are already installed"""
        print("[*] Checking existing dependencies...\n")
        
        dependencies = {
            'nmap': self.check_nmap,
            'whois': self.check_whois,
            'sqlmap': self.check_sqlmap,
            'metasploit': self.check_metasploit,
            'python_packages': self.check_python_packages
        }
        
        self.installed = []
        self.missing = []
        
        for name, check_func in dependencies.items():
            status, version = check_func()
            if status:
                self.installed.append((name, version))
                print(f"  {self.green('✓')} {name:<15} {version}")
            else:
                self.missing.append(name)
                print(f"  {self.red('✗')} {name:<15} Not installed")
        
        return len(self.missing) == 0
    
    def check_nmap(self):
        """Check if nmap is installed"""
        try:
            result = subprocess.run(['nmap', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0].split('version')[1].strip() if 'version' in result.stdout else 'Unknown'
                return True, version
        except:
            pass
        return False, None
    
    def check_whois(self):
        """Check if whois is installed"""
        try:
            result = subprocess.run(['whois', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Installed"
        except:
            pass
        return False, None
    
    def check_sqlmap(self):
        """Check if sqlmap is installed"""
        try:
            result = subprocess.run(['sqlmap', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0] if result.stdout else 'Unknown'
                return True, version[:20]
        except:
            pass
        return False, None
    
    def check_metasploit(self):
        """Check if metasploit is installed"""
        try:
            result = subprocess.run(['msfconsole', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Installed"
        except:
            pass
        return False, None
    
    def check_python_packages(self):
        """Check Python packages"""
        required_packages = ['colorama', 'requests', 'folium', 'plotly', 'reportlab']
        installed = []
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
                installed.append(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        return True, f"All {len(installed)} packages installed"
    
    def install_missing_dependencies(self):
        """Install missing dependencies based on user choice"""
        if not self.missing:
            print(f"\n{self.green('[✓] All dependencies are already installed!')}")
            return True
        
        print(f"\n{self.yellow('[!] Missing dependencies detected:')}")
        for dep in self.missing:
            print(f"    - {dep}")
        
        print(f"\n{self.cyan('[?] Do you want to install missing dependencies?')}")
        print("    1) Yes, install all missing dependencies (recommended)")
        print("    2) Yes, but skip Metasploit (large download)")
        print("    3) No, skip dependency installation")
        print("    4) Show manual installation instructions")
        
        choice = input(f"\n{self.yellow('Select option [1-4]: ')}").strip()
        
        if choice == '1':
            return self.install_all_dependencies()
        elif choice == '2':
            return self.install_all_except_metasploit()
        elif choice == '3':
            print(f"\n{self.yellow('[!] Skipping dependency installation')}")
            print("[*] You can install them manually later")
            return False
        elif choice == '4':
            self.show_manual_instructions()
            return False
        else:
            print(self.red("[!] Invalid option"))
            return False
    
    def install_all_dependencies(self):
        """Install all missing dependencies"""
        print(f"\n{self.green('[+] Installing missing dependencies...')}\n")
        
        success = True
        
        for dep in self.missing:
            if dep == 'nmap':
                success &= self.install_nmap()
            elif dep == 'whois':
                success &= self.install_whois()
            elif dep == 'sqlmap':
                success &= self.install_sqlmap()
            elif dep == 'metasploit':
                success &= self.install_metasploit()
            elif dep == 'python_packages':
                success &= self.install_python_packages()
        
        if success:
            print(f"\n{self.green('[✓] All dependencies installed successfully!')}")
        else:
            print(f"\n{self.red('[!] Some dependencies failed to install')}")
            self.show_manual_instructions()
        
        return success
    
    def install_all_except_metasploit(self):
        """Install all except Metasploit"""
        print(f"\n{self.green('[+] Installing dependencies (excluding Metasploit)...')}\n")
        
        success = True
        
        for dep in self.missing:
            if dep == 'metasploit':
                print(self.yellow("[*] Skipping Metasploit as requested"))
                continue
            elif dep == 'nmap':
                success &= self.install_nmap()
            elif dep == 'whois':
                success &= self.install_whois()
            elif dep == 'sqlmap':
                success &= self.install_sqlmap()
            elif dep == 'python_packages':
                success &= self.install_python_packages()
        
        return success
    
    def install_nmap(self):
        """Install nmap"""
        print("[*] Installing nmap...")
        try:
            if self.system == "Windows":
                # Use chocolatey or download installer
                subprocess.run(['choco', 'install', 'nmap', '-y'], check=True)
            elif self.system == "Linux":
                subprocess.run(['sudo', 'apt', 'install', '-y', 'nmap'], check=True)
            elif self.system == "Darwin":  # macOS
                subprocess.run(['brew', 'install', 'nmap'], check=True)
            print(self.green("  ✓ nmap installed"))
            return True
        except:
            print(self.red("  ✗ Failed to install nmap"))
            return False
    
    def install_whois(self):
        """Install whois"""
        print("[*] Installing whois...")
        try:
            if self.system == "Linux":
                subprocess.run(['sudo', 'apt', 'install', '-y', 'whois'], check=True)
            elif self.system == "Darwin":
                subprocess.run(['brew', 'install', 'whois'], check=True)
            else:
                print(self.yellow("  ℹ Manual installation required for Windows"))
                return False
            print(self.green("  ✓ whois installed"))
            return True
        except:
            print(self.red("  ✗ Failed to install whois"))
            return False
    
    def install_sqlmap(self):
        """Install sqlmap"""
        print("[*] Installing sqlmap...")
        try:
            if self.system == "Linux":
                subprocess.run(['sudo', 'apt', 'install', '-y', 'sqlmap'], check=True)
            elif self.system == "Darwin":
                subprocess.run(['brew', 'install', 'sqlmap'], check=True)
            elif self.system == "Windows":
                subprocess.run(['choco', 'install', 'sqlmap', '-y'], check=True)
            print(self.green("  ✓ sqlmap installed"))
            return True
        except:
            print(self.red("  ✗ Failed to install sqlmap"))
            return False
    
    def install_metasploit(self):
        """Install Metasploit Framework"""
        print("[*] Installing Metasploit Framework (this may take a while)...")
        try:
            if self.system == "Linux":
                # Metasploit installer
                subprocess.run(['curl', 'https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb', '-o', 'msfinstall'], check=True)
                subprocess.run(['chmod', '755', 'msfinstall'], check=True)
                subprocess.run(['sudo', './msfinstall'], check=True)
                subprocess.run(['rm', 'msfinstall'], check=True)
            elif self.system == "Windows":
                subprocess.run(['choco', 'install', 'metasploit', '-y'], check=True)
            print(self.green("  ✓ Metasploit installed"))
            return True
        except:
            print(self.red("  ✗ Failed to install Metasploit"))
            return False
    
    def install_python_packages(self):
        """Install Python packages"""
        print("[*] Installing Python packages...")
        packages = ['colorama', 'requests', 'folium', 'plotly', 'reportlab']
        
        success = True
        for package in packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True, capture_output=True)
                print(self.green(f"  ✓ {package}"))
            except:
                print(self.red(f"  ✗ {package}"))
                success = False
        
        return success
    
    def show_manual_instructions(self):
        """Show manual installation instructions"""
        print(f"\n{self.cyan('='*60)}")
        print(self.yellow("Manual Installation Instructions"))
        print(f"{self.cyan('='*60)}\n")
        
        if self.system == "Windows":
            print("Windows Installation:")
            print("  1. Install Chocolatey: https://chocolatey.org/install")
            print("  2. Run as Administrator:")
            print("     choco install nmap sqlmap metasploit -y")
            print("  3. Install Python packages:")
            print("     pip install colorama requests folium plotly reportlab")
        
        elif self.system == "Linux":
            print("Linux Installation (Ubuntu/Debian):")
            print("  sudo apt update")
            print("  sudo apt install -y nmap whois sqlmap")
            print("  # Metasploit: https://www.metasploit.com/download")
            print("  pip install colorama requests folium plotly reportlab")
        
        elif self.system == "Darwin":
            print("macOS Installation:")
            print("  brew install nmap whois sqlmap")
            print("  # Metasploit: https://www.metasploit.com/download")
            print("  pip install colorama requests folium plotly reportlab")
    
    def install_dsterminal_files(self):
        """Copy DSTERMINAL files to install location"""
        print(f"\n{self.green('[+] Installing DSTERMINAL files...')}")
        
        # Create install directory
        os.makedirs(self.install_path, exist_ok=True)
        
        # Files to copy (adjust based on your files)
        files_to_copy = ['dsterminal.py', 'soc_nmap_dashboard.py']
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, self.install_path)
                print(f"  ✓ Copied {file}")
            else:
                print(self.yellow(f"  ℹ {file} not found in current directory"))
        
        # Create workspace
        workspace = os.path.expanduser("~/dsterminal_workspace")
        os.makedirs(workspace, exist_ok=True)
        os.makedirs(os.path.join(workspace, "scans"), exist_ok=True)
        
        # Create launcher script
        self.create_launcher()
        
        return True
    
    def create_launcher(self):
        """Create platform-specific launcher"""
        if self.system == "Windows":
            launcher = f"""@echo off
cd /d {self.install_path}
python dsterminal.py
pause
"""
            launcher_path = os.path.join(self.install_path, "DSTERMINAL.bat")
        else:
            launcher = f"""#!/bin/bash
cd {self.install_path}
python3 dsterminal.py
"""
            launcher_path = os.path.join(self.install_path, "dsterminal.sh")
            os.chmod(launcher_path, 0o755)
        
        with open(launcher_path, 'w') as f:
            f.write(launcher)
        
        print(f"  ✓ Created launcher: {launcher_path}")
    
    def create_shortcut(self):
        """Create desktop shortcut (Windows)"""
        if self.system == "Windows":
            try:
                import ctypes
                from win32com.client import Dispatch
                
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                shortcut_path = os.path.join(desktop, "DSTERMINAL.lnk")
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{os.path.join(self.install_path, "dsterminal.py")}"'
                shortcut.WorkingDirectory = self.install_path
                shortcut.save()
                
                print(f"  ✓ Created desktop shortcut")
            except:
                print(self.yellow("  ℹ Could not create desktop shortcut"))
    
    def green(self, text):
        return f"\033[92m{text}\033[0m"
    
    def red(self, text):
        return f"\033[91m{text}\033[0m"
    
    def yellow(self, text):
        return f"\033[93m{text}\033[0m"
    
    def cyan(self, text):
        return f"\033[96m{text}\033[0m"
    
    def run(self):
        """Main installation process"""
        self.print_banner()
        
        # Check admin rights
        if not self.is_admin and self.system != "Windows":
            print(self.red("[!] Warning: Not running as root/sudo"))
            print("[*] Some installations may fail without proper privileges\n")
        
        # Check dependencies
        all_installed = self.check_dependencies()
        
        if not all_installed:
            # Ask user if they want to install missing dependencies
            self.install_missing_dependencies()
        else:
            print(f"\n{self.green('[✓] All dependencies are already installed!')}")
        
        # Install DSTERMINAL files
        self.install_dsterminal_files()
        
        # Create shortcut (Windows)
        if self.system == "Windows":
            self.create_shortcut()
        
        # Installation complete
        print(f"\n{self.green('='*60)}")
        print(self.green("[✓] DSTERMINAL Installation Complete!"))
        print(f"{self.green('='*60)}")
        print(f"\nInstallation Location: {self.install_path}")
        print(f"Workspace: ~/dsterminal_workspace")
        print(f"\n{self.cyan('To start DSTERMINAL:')}")
        print(f"  cd {self.install_path}")
        print(f"  python dsterminal.py")
        print(f"\nOr use the launcher: {os.path.join(self.install_path, 'DSTERMINAL.bat' if self.system == 'Windows' else 'dsterminal.sh')}")
        
        # Ask to launch
        launch = input(f"\n{self.yellow('[?] Launch DSTERMINAL now? (y/n): ')}").strip().lower()
        if launch == 'y':
            os.chdir(self.install_path)
            subprocess.run([sys.executable, 'dsterminal.py'])

if __name__ == "__main__":
    installer = DSTERMINALInstaller()
    installer.run()