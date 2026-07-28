#!/usr/bin/env python3
"""
DSTERMINAL Dependency Checker & Auto-Installer
"""

import subprocess
import sys
import os
import platform

class DependencyManager:
    def __init__(self):
        self.system = platform.system()
        self.dependencies = {
            'nmap': self.check_nmap,
            'whois': self.check_whois,
            'sqlmap': self.check_sqlmap,
            'metasploit': self.check_metasploit
        }
    
    def check_nmap(self):
        try:
            subprocess.run(['nmap', '--version'], capture_output=True)
            return True
        except:
            return False
    
    def check_whois(self):
        try:
            subprocess.run(['whois', '--version'], capture_output=True)
            return True
        except:
            return False
    
    def check_sqlmap(self):
        try:
            subprocess.run(['sqlmap', '--version'], capture_output=True)
            return True
        except:
            return False
    
    def check_metasploit(self):
        try:
            subprocess.run(['msfconsole', '--version'], capture_output=True)
            return True
        except:
            return False
    
    def install_missing(self):
        missing = [name for name, check in self.dependencies.items() if not check()]
        
        if not missing:
            print("[✓] All dependencies satisfied!")
            return True
        
        print(f"[!] Missing dependencies: {', '.join(missing)}")
        
        if self.system == "Linux":
            print("[*] Installing missing dependencies...")
            for dep in missing:
                if dep == 'metasploit':
                    print("[*] Manual Metasploit installation required: https://www.metasploit.com/download")
                else:
                    subprocess.run(['sudo', 'apt', 'install', '-y', dep])
        
        elif self.system == "Windows":
            print("[*] Please install missing dependencies manually:")
            for dep in missing:
                if dep == 'nmap':
                    print("  - nmap: https://nmap.org/download.html")
                elif dep == 'sqlmap':
                    print("  - sqlmap: https://sqlmap.org/")
                elif dep == 'whois':
                    print("  - whois: https://docs.microsoft.com/en-us/sysinternals/downloads/whois")
        
        return False

# In your main DSTERMINAL class
def check_dependencies(self):
    """Check and report missing dependencies"""
    deps = DependencyManager()
    
    print(f"{Fore.CYAN}[*] Checking DSTERMINAL dependencies...{Style.RESET_ALL}")
    
    # Check system tools
    missing_tools = []
    for tool in ['nmap', 'whois', 'sqlmap']:
        if shutil.which(tool):
            print(f"{Fore.GREEN}✓ {tool}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {tool} (missing){Style.RESET_ALL}")
            missing_tools.append(tool)
    
    # Check Metasploit
    if shutil.which('msfconsole'):
        print(f"{Fore.GREEN}✓ metasploit{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ metasploit (optional){Style.RESET_ALL}")
    
    # Check Python packages
    missing_packages = []
    for pkg in ['colorama', 'requests', 'folium', 'plotly', 'reportlab']:
        try:
            __import__(pkg)
            print(f"{Fore.GREEN}✓ {pkg}{Style.RESET_ALL}")
        except ImportError:
            print(f"{Fore.RED}✗ {pkg}{Style.RESET_ALL}")
            missing_packages.append(pkg)
    
    if missing_tools or missing_packages:
        print(f"\n{Fore.YELLOW}[!] Missing dependencies detected{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Run 'setup' to install missing dependencies{Style.RESET_ALL}")
        return False
    
    print(f"\n{Fore.GREEN}[✓] All dependencies satisfied!{Style.RESET_ALL}")
    return True

def cmd_setup(self):
    """Install missing dependencies automatically"""
    print(f"{Fore.CYAN}[*] Running DSTERMINAL setup...{Style.RESET_ALL}")
    
    if platform.system() == "Linux":
        print(f"{Fore.YELLOW}[*] Installing missing packages...{Style.RESET_ALL}")
        subprocess.run(['sudo', 'apt', 'update'])
        subprocess.run(['sudo', 'apt', 'install', '-y', 'nmap', 'whois', 'sqlmap'])
        
    elif platform.system() == "Windows":
        print(f"{Fore.YELLOW}[*] Please install manually or use Chocolatey{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Or run: install_dependencies.bat{Style.RESET_ALL}")
    
    # Install Python packages
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    print(f"{Fore.GREEN}[✓] Setup complete!{Style.RESET_ALL}")