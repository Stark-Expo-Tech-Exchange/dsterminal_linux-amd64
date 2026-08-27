#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch script to add 'import sys' to Python files that are missing it.
This fixes the NameError: name 'sys' is not defined error.
"""

import os
import re
from pathlib import Path

# List of files to patch
FILES_TO_PATCH = [
    'certcheck.py',
    'web_security_analyzer.py',
    'exploit_scanner.py',
    'network_security.py',
    'dashboard.py',
    'dsterminal_dashboard.py',
    'dsterminal_complete.py',
    'financial_forensics.py',
    'hardening_dashboard.py',
    'integrity_monitor.py',
    'ioc_edu.py',
    'ransomware_monitor.py',
    'recon.py',
    'recon_full.py',
    'shield_core.py',
    'soc_automated_lab.py',
    'soc_enhanced_modules.py',
    'soc_nmap_dashboard.py',
    'sqlmap_advanced.py',
    'sqlmap_scanner.py',
    'steg_analyzer.py',
    'update.py',
    'vt_scan.py',
    'wifi_audit.py',
    'crypto_engine.py',
]

def patch_file(filepath):
    """Add import sys to the beginning of the file if missing"""
    if not os.path.exists(filepath):
        print(f"⚠️ File not found: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if 'import sys' is already present
        if 'import sys' in content[:200]:
            print(f"⏭️ {filepath} - already has import sys")
            return True

        # Find the shebang line or first line
        lines = content.split('\n')
        new_lines = []
        inserted = False

        for i, line in enumerate(lines):
            # If it's a shebang line, add import sys right after
            if not inserted and line.startswith('#!'):
                new_lines.append(line)
                new_lines.append('import sys')
                inserted = True
            # If it's a coding declaration, add import sys right after
            elif not inserted and line.startswith('# -*- coding:'):
                new_lines.append(line)
                new_lines.append('import sys')
                inserted = True
            # If it's the first non-comment line, add import sys before it
            elif not inserted and line.strip() and not line.startswith('#'):
                new_lines.append('import sys')
                new_lines.append('')
                new_lines.append(line)
                inserted = True
            else:
                new_lines.append(line)

        # If still not inserted, add at the very beginning
        if not inserted:
            new_lines.insert(0, 'import sys')
            new_lines.insert(0, '')

        new_content = '\n'.join(new_lines)

        # Only write if content changed
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {filepath} - added import sys")
            return True
        else:
            print(f"⏭️ {filepath} - no changes needed")
            return True

    except Exception as e:
        print(f"❌ {filepath} - Error: {e}")
        return False

def scan_and_patch_all():
    """Scan current directory for .py files and patch those with sys usage but no import"""
    print("\n" + "="*70)
    print("Import Sys Patch Script")
    print("="*70 + "\n")

    fixed = 0
    failed = 0
    skipped = 0

    # First, patch known files
    for file in FILES_TO_PATCH:
        if os.path.exists(file):
            if patch_file(file):
                fixed += 1
            else:
                failed += 1
        else:
            print(f"⏭️ File not found: {file}")
            skipped += 1

    # Also scan for any other .py files that might have the issue
    print("\n" + "="*70)
    print("Scanning additional .py files...")
    print("="*70 + "\n")

    for py_file in Path('.').glob('*.py'):
        if py_file.name in FILES_TO_PATCH:
            continue  # Already processed
        if py_file.name.startswith('patch_'):
            continue  # Skip this script
        if py_file.name == 'patch_import_sys.py':
            continue

        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check if the file uses sys but doesn't import it
            if 'sys.' in content and 'import sys' not in content[:200]:
                print(f"🔍 Found potential issue in: {py_file.name}")
                if patch_file(py_file.name):
                    fixed += 1
                else:
                    failed += 1
        except:
            pass

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Files patched: {fixed}")
    print(f"❌ Files failed: {failed}")
    print(f"⏭️ Files skipped: {skipped}")
    print("="*70)

def main():
    scan_and_patch_all()

if __name__ == "__main__":
    main()