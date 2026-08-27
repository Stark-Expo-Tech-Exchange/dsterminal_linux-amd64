#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to find which files have colorama OSError 22 issues
"""

import os
import sys
import re
import subprocess
from pathlib import Path

# ANSI colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check_file_for_colorama_issues(filepath):
    """Check if a file has colorama OSError 22 issues"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for patched_write function
        if 'def patched_write' in content:
            issues.append('patched_write function found')
        
        # Check for colorama init with convert=True
        if 'init(autoreset=True, strip=False, convert=True)' in content:
            issues.append('colorama init with convert=True')
        
        # Check for AnsiToWin32.write patching
        if 'colorama.AnsiToWin32.write = patched_write' in content:
            issues.append('AnsiToWin32.write patching found')
        
        # Check for duplicate colorama imports
        colorama_imports = re.findall(r'import\s+colorama|from\s+colorama\s+import', content)
        if len(colorama_imports) > 1:
            issues.append(f'Multiple colorama imports ({len(colorama_imports)})')
        
        # Check for sys.stdout.reconfigure without error handling
        if 'sys.stdout.reconfigure' in content and 'except' not in content[content.find('sys.stdout.reconfigure'):content.find('sys.stdout.reconfigure')+200]:
            issues.append('sys.stdout.reconfigure without error handling')
        
        # Check for safe_write function with incorrect indentation
        if 'def safe_write' in content:
            # Check if the function has proper indentation
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def safe_write' in line:
                    # Check the next few lines for indentation issues
                    for j in range(i+1, min(i+10, len(lines))):
                        if 'try:' in lines[j] and not lines[j].startswith('    '):
                            issues.append('safe_write function with indentation issues')
                            break
                    break
        
        # Check for missing re import (needed for ANSI stripping)
        if 'ansi_escape = re.compile' in content and 'import re' not in content:
            issues.append('missing re import for ANSI stripping')
        
        # Check for sys.stdout is None checks
        if 'sys.stdout is None' in content:
            # Check if it's handled properly
            if 'return' not in content[content.find('sys.stdout is None'):content.find('sys.stdout is None')+200]:
                issues.append('sys.stdout is None check without proper return')
    
    except Exception as e:
        issues.append(f'Error reading file: {e}')
    
    return issues

def main():
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}Colorama OSError 22 Issue Scanner{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    # Get all Python files in the current directory
    python_files = []
    for file in Path('.').glob('*.py'):
        if file.name != 'test_colorama_issue.py':  # Skip this script
            python_files.append(file)
    
    # Also check subdirectories
    for dir_path in ['modules', 'tools', 'utils']:
        if os.path.exists(dir_path):
            for file in Path(dir_path).glob('*.py'):
                python_files.append(file)
    
    if not python_files:
        print(f"{Colors.YELLOW}No Python files found{Colors.RESET}")
        return
    
    print(f"{Colors.CYAN}Found {len(python_files)} Python files to check{Colors.RESET}\n")
    
    files_with_issues = []
    files_clean = []
    
    for file in sorted(python_files):
        issues = check_file_for_colorama_issues(file)
        
        if issues:
            files_with_issues.append((file, issues))
            print(f"{Colors.RED}❌ {file}{Colors.RESET}")
            for issue in issues:
                print(f"   {Colors.YELLOW}  ⚠ {issue}{Colors.RESET}")
        else:
            files_clean.append(file)
            print(f"{Colors.GREEN}✅ {file}{Colors.RESET}")
    
    # Summary
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}SUMMARY{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}Clean files: {len(files_clean)}{Colors.RESET}")
    print(f"{Colors.RED}Files with issues: {len(files_with_issues)}{Colors.RESET}")
    
    if files_with_issues:
        print(f"\n{Colors.YELLOW}Files that need fixing:{Colors.RESET}")
        for file, issues in files_with_issues:
            print(f"  {Colors.RED}• {file}{Colors.RESET}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"    {Colors.YELLOW}  - {issue}{Colors.RESET}")
            if len(issues) > 3:
                print(f"    {Colors.DIM}  ... and {len(issues) - 3} more issues{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")

if __name__ == "__main__":
    main()