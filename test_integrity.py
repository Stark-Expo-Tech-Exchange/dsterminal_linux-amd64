#!/usr/bin/env python3
"""
Test script for DSTerminal Integrity Monitor
Run this to create a test environment and test all commands
"""

import os
import sys
import shutil
import tempfile
import time
from datetime import datetime

# Add colorama for nice output
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    # Fallback
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        RESET = '\033[0m'
    
    class Style:
        BRIGHT = '\033[1m'; RESET_ALL = '\033[0m'

def setup_test_environment():
    """Create a test directory structure with sample files"""
    
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}Setting up DSTerminal Integrity Test Environment{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    # Create test directories
    test_dir = os.path.join(os.getcwd(), "test_integrity_env")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    os.makedirs(test_dir)
    
    # Create subdirectories mimicking system structure
    dirs = [
        "configs",
        "logs", 
        "databases",
        "critical",
        "user_files",
        "temp"
    ]
    
    for dir_name in dirs:
        os.makedirs(os.path.join(test_dir, dir_name))
    
    print(f"{Fore.GREEN}✓ Created test directory: {test_dir}{Style.RESET_ALL}")
    
    # Create sample files
    files = {
        "configs/app_config.conf": "# Application Configuration\nsetting1=value1\nsetting2=value2\n",
        "configs/network_config.conf": "# Network Settings\nhostname=localhost\nport=8080\n",
        "logs/system.log": "[INFO] System started\n[INFO] Service running\n",
        "logs/access.log": "192.168.1.100 - - [10/Oct/2023] GET /index.html\n",
        "databases/users.db": "user1:password_hash1\nuser2:password_hash2\n",
        "databases/products.db": "product1:100\nproduct2:200\n",
        "critical/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:User:/home/user:/bin/bash\n",
        "critical/hosts": "127.0.0.1 localhost\n::1 localhost\n",
        "user_files/document.txt": "This is a test document.\n",
        "user_files/notes.txt": "Important notes here.\n",
        "temp/temp_file.tmp": "Temporary data\n"
    }
    
    for file_path, content in files.items():
        full_path = os.path.join(test_dir, file_path)
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"{Fore.GREEN}  ✓ Created: {file_path}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✅ Test environment created successfully!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Test directory: {test_dir}{Style.RESET_ALL}\n")
    
    return test_dir

def modify_test_files(test_dir):
    """Modify some files to simulate changes"""
    print(f"\n{Fore.CYAN}Modifying test files to simulate changes...{Style.RESET_ALL}")
    
    # Modify a config file
    config_file = os.path.join(test_dir, "configs/app_config.conf")
    with open(config_file, 'a') as f:
        f.write("\n# New setting added\nsetting3=newvalue3\n")
    print(f"{Fore.YELLOW}  ✏️ Modified: configs/app_config.conf{Style.RESET_ALL}")
    
    # Create a new file
    new_file = os.path.join(test_dir, "user_files/new_document.txt")
    with open(new_file, 'w') as f:
        f.write("This is a newly created file.\n")
    print(f"{Fore.GREEN}  ✨ Created: user_files/new_document.txt{Style.RESET_ALL}")
    
    # Delete a file
    delete_file = os.path.join(test_dir, "temp/temp_file.tmp")
    if os.path.exists(delete_file):
        os.remove(delete_file)
        print(f"{Fore.RED}  🗑️ Deleted: temp/temp_file.tmp{Style.RESET_ALL}")
    
    # Modify critical file
    critical_file = os.path.join(test_dir, "critical/hosts")
    with open(critical_file, 'a') as f:
        f.write("192.168.1.100 malicious-site.com\n")
    print(f"{Fore.RED}  ⚠️ Modified critical: critical/hosts{Style.RESET_ALL}")
    
    print(f"{Fore.GREEN}✓ Test modifications complete{Style.RESET_ALL}")

def test_integrity_commands():
    """Test all integrity commands"""
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}TESTING INTEGRITY COMMANDS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    # This function will be called from within DSTerminal
    # We're just printing the commands to test
    commands = [
        ("integrity help", "Show help menu"),
        ("integrity list all", "List all files"),
        ("integrity list critical", "List critical files"),
        ("integrity list configs", "List config files"),
        ("integrity list logs", "List log files"),
        ("integrity list databases", "List database files"),
        ("integrity list user", "List user files"),
        ("integrity baseline", "Create initial baseline"),
        ("integrity scan", "Run integrity scan"),
        ("integrity report", "Generate report"),
        ("integrity compare data/baselines/latest_baseline.json", "Compare with baseline"),
        ("integrity monitor", "Start real-time monitoring (Ctrl+C to stop)"),
        ("integrity alerts", "Show alerts"),
        ("integrity forensic timeline", "Show forensic timeline"),
        ("integrity quarantine test_integrity_env/critical/hosts", "Quarantine suspicious file"),
        ("integrity restore test_integrity_env/critical/hosts", "Restore from quarantine")
    ]
    
    for cmd, desc in commands:
        print(f"{Fore.CYAN}Command:{Style.RESET_ALL} {Fore.GREEN}{cmd}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  Description: {desc}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {'.' * 40}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✅ Test commands listed. Run them in DSTerminal to test.{Style.RESET_ALL}")

def main():
    """Main test function"""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print(r"""
    ╔═══════════════════════════════════════════╗
    ║     DSTERMINAL INTEGRITY TEST SUITE       ║
    ╚═══════════════════════════════════════════╝
    """)
    print(f"{Style.RESET_ALL}")
    
    # Setup test environment
    test_dir = setup_test_environment()
    
    # Print instructions
    print(f"\n{Fore.YELLOW}📋 TEST INSTRUCTIONS:{Style.RESET_ALL}")
    print(f"1. Start DSTerminal")
    print(f"2. Navigate to the test directory (optional):")
    print(f"   {Fore.CYAN}cd {test_dir}{Style.RESET_ALL}")
    print(f"3. Run integrity commands to test")
    print(f"4. After initial tests, run modifications:")
    print(f"   {Fore.CYAN}python test_integrity.py --modify{Style.RESET_ALL}")
    print(f"5. Re-run integrity scan to detect changes")
    
    # Check for modify flag
    if len(sys.argv) > 1 and sys.argv[1] == "--modify":
        modify_test_files(test_dir)
    
    # Show commands to test
    test_integrity_commands()
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Test environment ready!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Test directory: {test_dir}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()