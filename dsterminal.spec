# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# Exclude heavy/unnecessary modules
excludes = [
    'pytest', 'PyQt5', 'PyQt6', 
    'IPython', 'jupyter', 'matplotlib.tests', 'numpy.tests', 
    'pandas.tests', 'scipy', 'scipy.tests', 'setuptools.tests',
    'distutils.tests', '_posixshmem', 'resource', 'fcntl',
    'unittest',  # Exclude test framework
    'xmlrpc',  # Exclude if not needed
]

# Collect data files from directories
def collect_dir(src, dest):
    datas = []
    if os.path.exists(src):
        for item in os.listdir(src):
            src_path = os.path.join(src, item)
            if os.path.isfile(src_path):
                datas.append((src_path, dest))
            elif os.path.isdir(src_path):
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, src)
                        datas.append((file_path, os.path.join(dest, rel_path)))
    return datas

datas = []

# Add directories
for dir_name in ['config', 'data', 'docs', 'installer_assets', 'logo_path', 
                  'footer_logo_path', 'redist', 'scans', 'templates', 'tools', 
                  'update', 'DSTerminal_Workspace']:
    if os.path.exists(dir_name):
        datas.extend(collect_dir(dir_name, dir_name))
        print(f"[*] Collected directory: {dir_name}")

# Add individual files
files = [
    'VERSION', 'license.txt', 'README.md', 'requirements.txt',
    'version_info.txt',
    'icon-removebg-preview.ico', 'financial_forensics.py', 
    'install_dependencies.sh', 'install_dependencies.bat', 'dependency_checker.py',
    'crypto_engine.py', 'integrity_monitor.py', 'recon.py', 'recon_full.py', 
    'install_dsterminal.py',
    'vt_scan.py', 'edu_typing_engine.py', 'soc_nmap_dashboard.py',
    'deletion_protection.py', 'hardening_dashboard.py', 'dst_footer.py', 
    'telemetry_engine.py', 'setupt.sh', 'setupt.bat',
    # Dependency installation scripts
    'install_nmap.ps1', 'install_python_packages.ps1', 'check_dependencies.ps1', 
    'install_metasploit.ps1', 'install_all_dependencies.ps1',
    'install_nmap.bat', 'install_remaining_deps.ps1', 'install_remaining_deps.bat', 
    'check_deps.bat', 'install_chocolatey.ps1',
    'install_whois.ps1', 'install_sqlmap.ps1', 'install_nmap_admin.ps1', 
    'install_dsterminal.py',
]

for file in files:
    if os.path.exists(file):
        datas.append((file, '.'))
        print(f"[*] Collected file: {file}")

print(f"[*] Total data files collected: {len(datas)}")

# Comprehensive hidden imports for all DSTerminal functionality
hiddenimports = [
    # Rich Console & UI
    'rich', 'rich.console', 'rich.panel', 'rich.align', 'rich.table',
    'rich.live', 'rich.layout', 'rich.progress', 'rich.syntax', 'rich.traceback',
    'rich.markdown', 'rich.columns', 'rich.tree', 'rich.prompt', 'rich.status',
    'rich.box', 'rich.text', 'rich.style', 'rich.color', 'rich.theme',
    'rich.segment', 'rich.measure', 'rich.padding', 'rich.control',
    
    # Colorama for cross-platform colors
    'colorama', 'colorama.initialise', 'colorama.ansitowin32',
    'colorama.winterm', 'colorama.win32',
    
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
    'tkinter.simpledialog', 'tkinter.scrolledtext', 'tkinter.colorchooser',
    'tkinter.font', 'tkinter.dnd', 'tkinter.commondialog',
    'turtle',

    # Core Python libraries
    'json', 'os', 'sys', 'time', 'random', 'datetime', 'threading',
    'pathlib', 'shutil', 'platform', 'subprocess', 'hashlib', 'base64',
    'logging', 're', 'collections', 'itertools', 'functools', 'glob',
    'tempfile', 'io', 'abc', 'weakref', 'copy', 'math', 'string',
    'typing', 'enum', 'dataclasses', 'contextlib', 'signal', 'atexit',
    'inspect', 'ast', 'traceback', 'warnings',
    
    # Network & Web
    'requests', 'requests.packages', 'requests.packages.urllib3',
    'requests.auth', 'requests.cookies', 'requests.sessions',
    'urllib3', 'urllib.parse', 'urllib.request', 'urllib.error',
    'socket', 'ssl', 'http.client', 'http.server',
    'webbrowser', 'email', 'email.mime', 'email.mime.text', 'email.mime.multipart',
    'smtplib', 'ftplib', 'telnetlib', 'json.decoder', 'json.encoder',
    
    # timezone finder
    'timezonefinder', 'timezonefinder.timezonefinder',
    'h3', 'h3._version', 'h3.api', 'h3.api.numpy_int',
    'importlib.metadata', 'importlib.resources',

    # Data Processing & Visualization
    'psutil', 'psutil._psutil_windows', 'psutil._common',
    'folium', 'folium.folium', 'folium.plugins', 'folium.map',
    'plotly', 'plotly.graph_objects', 'plotly.express', 'plotly.subplots',
    'plotly.io', 'plotly.offline', 'plotly.validators', 'plotly.tools',
    'pandas', 'numpy', 'numpy.core', 'numpy.linalg', 'numpy.random',
    
    # Reporting & PDF
    'reportlab', 'reportlab.pdfgen', 'reportlab.lib.pagesizes', 'reportlab.lib.units',
    'reportlab.lib.colors', 'reportlab.platypus', 'reportlab.platypus.tables',
    'reportlab.pdfbase', 'reportlab.pdfbase.pdfmetrics', 'reportlab.graphics',
    'reportlab.graphics.shapes', 'reportlab.graphics.renderPDF',
    
    # File System & Operations
    'shutil', 'filecmp', 'stat', 'fnmatch', 'pickle', 'shelve',
    
    # Windows Specific
    'win32api', 'win32com', 'win32com.client', 'win32com.shell', 'win32com.shell.shell',
    'win32ctypes', 'win32ctypes.pywin32', 'win32ctypes.pywin32.win32api',
    'win32security', 'win32file', 'win32con', 'win32process', 'win32event',
    'win32gui', 'win32ui', 'ctypes', 'ctypes.wintypes', 'winreg',
    'msvcrt', '_winapi',
    
    # Terminal & Progress Bars
    'tqdm', 'tqdm.std', 'tqdm.rich', 'tqdm.asyncio',
    'prompt_toolkit', 'prompt_toolkit.shortcuts', 'prompt_toolkit.styles',
    'pyfiglet', 'pyfiglet.fonts', 'ascii_magic', 'ascii_magic._ascii_magic',
    
    # Cryptography & Security
    'cryptography', 'cryptography.hazmat', 'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.ciphers', 'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.backends', 'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.primitives.asymmetric', 'cryptography.hazmat.primitives.kdf',
    'cryptography.hazmat.primitives.padding', 'cryptography.fernet', 'cryptography.x509',
    'hashlib', 'hmac', 'secrets', 'jwt', 'jwt.algorithms', 'jwt.utils',
    
    # Web Scraping & APIs
    'urllib3', 'urllib3.poolmanager', 'urllib3.util', 'urllib3.util.retry',
    'beautifulsoup4', 'bs4', 'bs4.builder', 'bs4.builder._html5lib',
    
    # Syntax Highlighting
    'pygments', 'pygments.lexers', 'pygments.formatters', 'pygments.styles',
    'pygments.token', 'pygments.lexer', 'pygments.formatter', 'pygments.style',
    
    # Textual UI (if used)
    'textual', 'textual.app', 'textual.widgets', 'textual.containers',
    'textual.screen', 'textual.events', 'textual.messages', 'textual.css',
    
    # DSTERMINAL Modules
    'financial_forensics', 'crypto_engine', 'integrity_monitor',
    'recon', 'recon_full', 'vt_scan', 'edu_typing_engine', 'hardening_dashboard',
    'deletion_protection', 'soc_nmap_dashboard', 'telemetry_engine', 'dst_footer',
    
    # Networking Tools
    'socket', 'ipaddress', 'dns', 'dns.resolver', 'dns.query', 'dns.message',
    'dns.name', 'dns.rdatatype', 'dns.rdataclass', 'dns.zone', 'dns.tsig',
    'scapy', 'scapy.all', 'scapy.layers', 'scapy.layers.inet', 'scapy.utils',
    
    # Compression (if needed)
    'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'zstandard',
    
    # XML/HTML Processing
    'xml', 'xml.etree', 'xml.etree.ElementTree', 'xml.dom', 'xml.sax',
    'html', 'html.parser', 'html.entities',
    
    # Date/Time
    'calendar', 'zoneinfo', 'dateutil', 'dateutil.parser', 'dateutil.tz',
    
    # System Information
    'platform', 'sysconfig', 'site', 'cpuinfo', 'wmi', 'win32com.client',
    
    # Binary/Hex Processing
    'binascii', 'codecs', 'struct', 'array',
]

# Collect hidden submodules from key packages
try:
    hiddenimports.extend(collect_submodules('rich'))
    print("[*] Collected rich submodules")
except Exception as e:
    print(f"[!] Could not collect rich submodules: {e}")

try:
    hiddenimports.extend(collect_submodules('psutil'))
    print("[*] Collected psutil submodules")
except Exception as e:
    print(f"[!] Could not collect psutil submodules: {e}")

try:
    hiddenimports.extend(collect_submodules('reportlab'))
    print("[*] Collected reportlab submodules")
except Exception as e:
    print(f"[!] Could not collect reportlab submodules: {e}")

try:
    hiddenimports.extend(collect_submodules('folium'))
    print("[*] Collected folium submodules")
except Exception as e:
    print(f"[!] Could not collect folium submodules: {e}")

try:
    hiddenimports.extend(collect_submodules('plotly'))
    print("[*] Collected plotly submodules")
except Exception as e:
    print(f"[!] Could not collect plotly submodules: {e}")

# Remove duplicates while preserving order
hiddenimports = list(dict.fromkeys(hiddenimports))
print(f"[*] Total hidden imports: {len(hiddenimports)}")

a = Analysis(
    ['dsterminal.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dsterminal_win-2026_v2.1.327_x64-amd64',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='installer_assets/3486-removebg-preview.ico' if os.path.exists('installer_assets/3486-removebg-preview.ico') else None,
    uac_admin=False,  # Keep False to avoid admin requirement for running the EXE
)

print("\n[*] Build spec processing complete!")
print(f"[*] Output will be: dist/dsterminal_win-2026_v2.1.327_x64-amd64.exe")