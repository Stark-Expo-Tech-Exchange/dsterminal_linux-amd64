#!python
# ============================================================
# FIX UNICODE ENCODING ISSUES FOR WINDOWS CONSOLE
# ============================================================
import sys
import io
import os

# Safe stdout/stderr handling for GUI executables
if sys.platform == 'win32':
    try:
        # Set console code page to UTF-8 (only if console exists)
        if sys.stdout is not None:
            os.system('chcp 65001 > nul')
    except:
        pass
    
    # Replace stdout/stderr with UTF-8 wrappers (only if they exist)
    if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
        except:
            pass
    if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')
        except:
            pass

def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        # Check if stdout exists before printing
        if sys.stdout is not None:
            print(message)
        # If stdout is None (windowed mode), log to file instead
        else:
            try:
                log_path = os.path.join(os.path.dirname(sys.executable), 'dsterminal.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
            except:
                pass
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        if sys.stdout is not None:
            print(clean_message)
        else:
            try:
                log_path = os.path.join(os.path.dirname(sys.executable), 'dsterminal.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(clean_message + '\n')
            except:
                pass
    except:
        pass  # Silent fail for GUI mode

import ast
import subprocess
import sys
import os
import re

def get_imports(filename):
    """Extract all imported modules from a Python file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
    except:
        # Fallback: try with different encoding
        with open(filename, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        tree = ast.parse(content)
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    return imports

# Common standard library modules (don't install these)
STDLIB = {
    'os', 'sys', 're', 'json', 'time', 'datetime', 'collections', 
    'itertools', 'typing', 'math', 'random', 'string', 'subprocess',
    'socket', 'struct', 'hashlib', 'base64', 'uuid', 'pathlib',
    'shutil', 'tempfile', 'glob', 'argparse', 'logging', 'threading',
    'multiprocessing', 'io', 'csv', 'xml', 'html', 'urllib', 'http',
    'email', 'ssl', 'zlib', 'gzip', 'zipfile', 'tarfile', 'pickle',
    'ctypes', 'abc', 'functools', 'operator', 'weakref', 'copy',
    'pprint', 'traceback', 'warnings', 'contextlib', 'asyncio'
}

# Find all Python files in current directory
python_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('auto_install')]

all_imports = set()
for py_file in python_files:
    print(f"ðŸ“‚ Scanning: {py_file}")
    try:
        imports = get_imports(py_file)
        all_imports.update(imports)
    except Exception as e:
        print(f"âš ï¸  Error scanning {py_file}: {e}")

# Remove standard library modules
third_party = [imp for imp in all_imports if imp.lower() not in STDLIB and not imp.startswith('_')]

print("\n" + "="*50)
print(f"ðŸ“¦ Found {len(third_party)} third-party packages to install:")
print("="*50)

# Install each package
installed = []
failed = []
for package in sorted(third_party):
    print(f"\nâ¬‡ï¸  Installing: {package}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        installed.append(package)
    except Exception as e:
        print(f"âŒ Failed to install {package}: {e}")
        failed.append(package)

print("\n" + "="*50)
print("ðŸ“Š Installation Summary:")
print("="*50)
print(f"âœ… Installed: {len(installed)} packages")
if installed:
    print(f"   {', '.join(installed)}")
print(f"âŒ Failed: {len(failed)} packages")
if failed:
    print(f"   {', '.join(failed)}")

# Save requirements
print("\nðŸ“ Saving to requirements.txt...")
try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'freeze'], stdout=open('requirements.txt', 'w'))
    print("âœ… requirements.txt created!")
except:
    print("âš ï¸  Could not create requirements.txt")

print("\nâœ… Done! Run 'python dsterminal.py' to start the application.")