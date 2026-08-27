# test_imports.py
"""
Test imports one by one to find the culprit
"""
import sys
import os

print("Testing imports...")
sys.stdout.flush()

# List of modules to test in order
modules = [
    'sys',
    'os', 
    'platform',
    'subprocess',
    'io',
    'time',
    'random',
    'json',
    'shutil',
    'socket',
    'uuid',
    'hashlib',
    'logging',
    'threading',
    'queue',
    're',
    'datetime',
    'pathlib',
    'typing',
    'dataclasses',
    'tempfile',
    'math',
    'shlex',
    'netifaces',
    'getpass',
    'requests',
    'psutil',
    'tqdm',
    'textwrap',
    'ssl',
    'whois',
    'OpenSSL',
    'cryptography',
    'colorama',
    'prompt_toolkit',
    'rich',
    'pyfiglet',
    'reportlab',
    'folium',
    'plotly',
    'PIL',
    'numpy',
    'pytz',
    'timezonefinder',
    'cartopy',
    'matplotlib',
]

for module_name in modules:
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
    except ImportError:
        print(f"⚠️ {module_name} not installed (skipping)")
    except Exception as e:
        print(f"❌ {module_name} FAILED: {e}")
        # Check if stdout is still working
        try:
            sys.stdout.write(f"   stdout still works\n")
            sys.stdout.flush()
        except:
            print(f"   🔴 stdout is dead after importing {module_name}!")
            break
    sys.stdout.flush()

print("\nTest complete!")