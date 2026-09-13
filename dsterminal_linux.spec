# -*- mode: python ; coding: utf-8 -*-

"""
DSTerminal Linux PyInstaller Specification
-------------------------------------------

Builds a self-contained Linux executable containing:

    - Python runtime
    - Python dependencies
    - DSTerminal application modules
    - Application resources
    - Required package data

The resulting executable can be used by the Debian packaging stage.

Build:

    python -m PyInstaller --clean --noconfirm dsterminal_linux.spec

Output:

    dist/dsterminal
"""

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
)


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(SPECPATH).resolve()
HOOKS_DIR = PROJECT_ROOT / "hooks"

MAIN_SCRIPT = PROJECT_ROOT / "dsterminal.py"


# ============================================================================
# VALIDATION
# ============================================================================

if not MAIN_SCRIPT.exists():
    raise SystemExit(
        f"\nERROR: DSTerminal entry point was not found:\n"
        f"       {MAIN_SCRIPT}\n"
        f"\nPlace this spec file in the DSTerminal project directory.\n"
    )


# ============================================================================
# APPLICATION DATA
# ============================================================================

datas = []


def add_data(source, destination):
    """
    Add a file or directory to the PyInstaller bundle only when it exists.
    """
    source = Path(source)

    if source.exists():
        datas.append(
            (
                str(source),
                destination,
            )
        )


# ---------------------------------------------------------------------------
# Version / documentation / licensing
# ---------------------------------------------------------------------------

add_data(PROJECT_ROOT / "VERSION", ".")
add_data(PROJECT_ROOT / "version.txt", ".")
add_data(PROJECT_ROOT / "version_info.txt", ".")
add_data(PROJECT_ROOT / "license.txt", ".")
add_data(PROJECT_ROOT / "CREDITS.txt", ".")
add_data(PROJECT_ROOT / "README.txt", ".")
add_data(PROJECT_ROOT / "CHANGELOG.txt", ".")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

add_data(PROJECT_ROOT / "config.json", ".")
add_data(PROJECT_ROOT / "config", "config")


# ---------------------------------------------------------------------------
# Runtime resources
# ---------------------------------------------------------------------------

add_data(PROJECT_ROOT / "static", "static")
add_data(PROJECT_ROOT / "templates", "templates")
add_data(PROJECT_ROOT / "json", "json")
add_data(PROJECT_ROOT / "licenses", "licenses")
add_data(PROJECT_ROOT / "installer_assets", "installer_assets")


# ============================================================================
# DSTerminal APPLICATION MODULES
# ============================================================================
#
# These are explicitly listed because DSTerminal uses feature modules,
# command dispatch and potentially dynamic/conditional imports.
# ============================================================================

DSTERMINAL_MODULES = [
    # Core
    "dst_modules",
    "dst_footer",
    "edu_typing_engine",
    "operator_session",
    "telemetry_engine",
    "crypto_engine",
    "dependency_checker",
    "diagnostic",

    # Main application
    "dsterminal_complete",
    "dsterminal_dashboard",
    "dsterminal_security",
    "dsterminal_agent",
    "dashboard",

    # Defensive security
    "integrity_monitor",
    "deletion_protection",
    "ransomware_monitor",
    "shield_core",

    # Network/security
    "network_security",
    "wifi_audit",
    "recon",
    "recon_full",
    "certcheck",
    "web_security_analyzer",
    "steg_analyzer",
    "exploit_scanner",
    "financial_forensics",

    # SOC
    "soc_automated_lab",
    "soc_enhanced_modules",
    "soc_nmap_dashboard",

    # Scanners
    "sqlmap_scanner",
    "sqlmap_advanced",
    "vt_scan",
    "ioc_edu",

    # Reporting / utilities
    "generate_report",
    "user_guide",
    "update",
    "post_dst",
    "qr_wrapper",
]


# ============================================================================
# HIDDEN IMPORTS
# ============================================================================

hiddenimports = list(DSTERMINAL_MODULES)


# ============================================================================
# THIRD-PARTY PYTHON DEPENDENCIES
# ============================================================================
#
# Only packages actually available in the BUILD environment are added.
#
# This is important:
#
#     Missing optional package -> skipped
#     Installed package        -> bundled
#
# The customer does NOT need pip or Python for bundled packages.
# ============================================================================

THIRD_PARTY_PACKAGES = [
    # Terminal/UI
    "prompt_toolkit",
    "rich",
    "colorama",
    "pyfiglet",

    # Networking/system
    "requests",
    "psutil",
    "netifaces",

    # Security/crypto
    "cryptography",
    "OpenSSL",

    # Reporting
    "reportlab",

    # Data/scientific
    "numpy",
    "PIL",

    # Visualization
    "matplotlib",
    "plotly",
    "folium",

    # Utility
    "tqdm",
    "pytz",
    "timezonefinder",

    # WHOIS
    "whois",
]


# ============================================================================
# SAFELY COLLECT THIRD-PARTY SUBMODULES
# ============================================================================

for package in THIRD_PARTY_PACKAGES:

    try:
        hiddenimports += collect_submodules(package)

    except Exception:
        # Package may not be installed in the current build environment.
        pass


# Remove duplicate imports while preserving order.

hiddenimports = list(
    dict.fromkeys(hiddenimports)
)


# ============================================================================
# THIRD-PARTY PACKAGE DATA
# ============================================================================

DATA_PACKAGES = [
    "prompt_toolkit",
    "rich",
    "reportlab",
    "cryptography",
    "PIL",
    "matplotlib",
    "plotly",
    "folium",
    "pyfiglet",
]


for package in DATA_PACKAGES:

    try:

        package_data = collect_data_files(
            package,
            include_py_files=False,
        )

        datas.extend(package_data)

    except Exception:

        pass


# ============================================================================
# REMOVE DUPLICATE DATA ENTRIES
# ============================================================================

_unique_datas = []
_seen_datas = set()

for source, destination in datas:

    key = (
        str(source),
        str(destination),
    )

    if key not in _seen_datas:

        _seen_datas.add(key)
        _unique_datas.append(
            (
                source,
                destination,
            )
        )

datas = _unique_datas


# ============================================================================
# EXCLUSIONS
# ============================================================================
#
# These modules are not required by the Linux build.
# ============================================================================

excludes = [
    # Windows
    "win32api",
    "win32con",
    "win32event",
    "win32file",
    "win32gui",
    "win32process",
    "win32service",
    "win32serviceutil",
    "pywin32_system32",
    "msvcrt",

    # macOS
    "_scproxy",

    # Development
    "pytest",
    "IPython",
    "jupyter",
]


# ============================================================================
# OPTIONAL HOOK DIRECTORY
# ============================================================================

hookspath = []

if HOOKS_DIR.exists():

    hookspath = [
        str(HOOKS_DIR)
    ]


# ============================================================================
# ANALYSIS
# ============================================================================

a = Analysis(
    [
        str(MAIN_SCRIPT)
    ],

    pathex=[
        str(PROJECT_ROOT)
    ],

    binaries=[],

    datas=datas,

    hiddenimports=hiddenimports,

    hookspath=hookspath,

    hooksconfig={},

    runtime_hooks=[],

    excludes=excludes,

    noarchive=False,

    # Improves reproducibility of the build.
    cipher=None,
)


# ============================================================================
# PYTHON BYTECODE ARCHIVE
# ============================================================================

pyz = PYZ(
    a.pure,
    a.zipped_data,
)


# ============================================================================
# ONE-FILE LINUX EXECUTABLE
# ============================================================================
#
# This produces:
#
#     dist/dsterminal
#
# The executable contains the bundled Python interpreter and Python
# dependencies.
#
# console=True is REQUIRED because DSTerminal is a terminal/SOC application.
# ============================================================================

exe = EXE(

    pyz,

    a.scripts,

    a.binaries,

    a.datas,

    a.zipfiles,

    name="dsterminal",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=False,

    console=True,

    disable_windowed_traceback=False,

    # Single executable.
    exclude_binaries=False,

)