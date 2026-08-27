#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DSTerminal Linux Test Script - Python 3.13.5
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃         DSTERMINAL LINUX TEST - PYTHON 3.13.5            ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print()

# 1. Python Version
print(f"🐍 Python Version: {sys.version}")
print(f"   Python Path: {sys.executable}")
print()

# 2. Platform Info
print(f"🖥️  Platform: {platform.system()} {platform.release()}")
print(f"   Architecture: {platform.machine()}")
print(f"   Hostname: {platform.node()}")
print()

# 3. Test Critical Imports
print("📦 Testing Critical Imports:")
critical_modules = [
    ('prompt_toolkit', '✅', '❌'),
    ('colorama', '✅', '❌'),
    ('rich', '✅', '❌'),
    ('requests', '✅', '❌'),
    ('psutil', '✅', '❌'),
    ('netifaces', '✅', '❌'),
    ('watchdog', '✅', '❌'),
    ('cryptography', '✅', '❌'),
    ('OpenSSL', '✅', '❌'),
    ('folium', '✅', '❌'),
    ('plotly', '✅', '❌'),
    ('PIL', '✅', '❌'),
    ('numpy', '✅', '❌'),
    ('reportlab', '✅', '❌'),
    ('flask', '✅', '❌'),
    ('flask_socketio', '✅', '❌'),
    ('eventlet', '✅', '❌'),
    ('tqdm', '✅', '❌'),
    ('pyfiglet', '✅', '❌'),
    ('lxml', '✅', '❌'),
    ('bs4', '✅', '❌'),
    ('whois', '✅', '❌'),
]

all_passed = True
for module_name, pass_mark, fail_mark in critical_modules:
    try:
        __import__(module_name)
        print(f"   {pass_mark} {module_name}")
    except ImportError as e:
        print(f"   {fail_mark} {module_name} - {e}")
        all_passed = False
print()

# 4. Check System Commands
print("🔧 Checking System Commands:")
system_commands = [
    'nmap', 'whois', 'sqlmap', 'nikto', 'xdotool', 'wmctrl',
    'ip', 'ifconfig', 'netstat', 'systemctl'
]

for cmd in system_commands:
    result = subprocess.run(['which', cmd], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ {cmd}: {result.stdout.strip()}")
    else:
        print(f"   ⚠️  {cmd}: Not found")
print()

# 5. Check Workspace
print("📁 Workspace Check:")
workspace = Path.home() / "dsterminal_workspace"
if workspace.exists():
    print(f"   ✅ Workspace: {workspace}")
    subdirs = [d for d in workspace.iterdir() if d.is_dir()]
    print(f"   📂 Subdirectories: {len(subdirs)}")
    for d in subdirs[:5]:
        print(f"      • {d.name}")
    if len(subdirs) > 5:
        print(f"      ... and {len(subdirs) - 5} more")
else:
    print(f"   ⚠️  Workspace not found: {workspace}")
    print(f"   💡 Create with: mkdir -p {workspace}")
print()

# 6. Summary
print("=" * 60)
if all_passed:
    print("✅ All critical modules imported successfully!")
    print("✨ DSTerminal is ready to run!")
else:
    print("⚠️ Some modules are missing. Run:")
    print("   pip install -r requirements_linux.txt")
print("=" * 60)

if all_passed:
    print("\n🚀 To run DSTerminal:")
    print("   python3 dsterminal.py")
    print("   or")
    print("   chmod +x dsterminal.py && ./dsterminal.py")
else:
    print("\n🔧 To fix missing modules:")
    print("   pip install <module-name>")
    print("   or")
    print("   sudo apt install python3-<module-name>")

print()
