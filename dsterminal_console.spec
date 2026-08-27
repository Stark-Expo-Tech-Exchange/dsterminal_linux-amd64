# -*- mode: python ; coding: utf-8 -*-

"""
DSTerminal® One-File PyInstaller Specification
================================================

Windows build:
    pyinstaller --clean DSTerminal.spec

IMPORTANT:
    DSTerminal uses Flask-SocketIO with:

        async_mode="threading"

    Do NOT package Eventlet or Gevent as Socket.IO backends.

    The required Windows Socket.IO stack is:

        Flask-SocketIO
        python-socketio
        python-engineio
        simple-websocket
"""

import os

from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
)


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "DSTerminal"
MAIN_SCRIPT = "dsterminal.py"
ICON_FILE = os.path.join(
    "installer_assets",
    "3486-removebg-preview.ico"
)

block_cipher = None


# ============================================================
# COLLECT SOCKET.IO MODULES
# ============================================================
#
# This is the most important part of this spec.
#
# PyInstaller can miss Engine.IO's dynamically selected
# async driver when Flask-SocketIO is frozen.
#
# We explicitly collect the Windows threading driver and
# simple-websocket stack.
#

socketio_hiddenimports = [
    # Flask-SocketIO
    "flask_socketio",

    # python-socketio
    "socketio",
    "socketio.server",
    "socketio.base_server",
    "socketio.async_server",
    "socketio.packet",
    "socketio.manager",
    "socketio.pubsub_manager",
    "socketio.base_manager",
    "socketio.exceptions",

    # python-engineio
    "engineio",
    "engineio.server",
    "engineio.base_server",
    "engineio.packet",
    "engineio.async_drivers",
    "engineio.async_drivers.threading",

    # REQUIRED Windows threading backend
    "engineio.async_drivers._websocket_wsgi",

    # simple-websocket
    "simple_websocket",
    "simple_websocket.ws",

    # websocket dependencies
    "wsproto",
    "h11",
]


# ============================================================
# AUTOMATICALLY COLLECT SOCKET.IO SUBMODULES
# ============================================================

try:
    socketio_hiddenimports += collect_submodules("flask_socketio")
except Exception:
    pass

try:
    socketio_hiddenimports += collect_submodules("socketio")
except Exception:
    pass

try:
    socketio_hiddenimports += collect_submodules("engineio")
except Exception:
    pass

try:
    socketio_hiddenimports += collect_submodules("simple_websocket")
except Exception:
    pass


# Remove duplicates while preserving order
socketio_hiddenimports = list(dict.fromkeys(socketio_hiddenimports))


# ============================================================
# APPLICATION DATA FILES
# ============================================================

datas = [
    # Application resources
    ("tools", "tools"),
    ("static", "static"),
    ("templates", "templates"),

    # Application icon
    ("installer_assets/*.ico", "."),
]


# ============================================================
# OPTIONAL PACKAGE DATA
# ============================================================

#
# Some packages require data files that PyInstaller's normal
# hooks already collect. We explicitly collect selected data
# where appropriate.
#

try:
    datas += collect_data_files("simple_websocket")
except Exception:
    pass


# ============================================================
# HIDDEN IMPORTS
# ============================================================

hiddenimports = [

    # ========================================================
    # PYTHON CORE
    # ========================================================

    "encodings",
    "codecs",
    "io",
    "sys",
    "os",
    "re",
    "time",
    "datetime",
    "json",
    "hashlib",
    "subprocess",
    "shutil",
    "threading",
    "socket",
    "platform",
    "pathlib",
    "tempfile",
    "glob",
    "fnmatch",
    "queue",
    "signal",
    "uuid",

    # ========================================================
    # WINDOWS
    # ========================================================

    "ctypes",
    "ctypes.wintypes",

    # ========================================================
    # NETWORK INTERFACES
    # ========================================================

    "netifaces",

    # ========================================================
    # CLI / UI
    # ========================================================

    "colorama",
    "prompt_toolkit",
    "prompt_toolkit.application",
    "prompt_toolkit.layout",
    "prompt_toolkit.styles",
    "prompt_toolkit.formatted_text",
    "pygments",
    "wcwidth",

    # ========================================================
    # FLASK
    # ========================================================

    "flask",
    "flask.app",
    "flask.blueprints",
    "flask.cli",
    "flask.config",
    "flask.ctx",
    "flask.globals",
    "flask.helpers",
    "flask.json",
    "flask.logging",
    "flask.sessions",
    "flask.templating",
    "flask.views",

    # Werkzeug
    "werkzeug",
    "werkzeug.serving",
    "werkzeug.routing",
    "werkzeug.utils",
    "werkzeug.wrappers",
    "werkzeug.middleware",
    "werkzeug.middleware.proxy_fix",

    # Jinja
    "jinja2",
    "jinja2.ext",

    # Flask dependencies
    "markupsafe",
    "itsdangerous",
    "click",
    "blinker",

    # ========================================================
    # FLASK-SOCKETIO / SOCKET.IO
    # ========================================================

    *socketio_hiddenimports,

    # ========================================================
    # SECURITY / SYSTEM
    # ========================================================

    "psutil",

    "cryptography",
    "cryptography.hazmat",
    "cryptography.hazmat.primitives",
    "cryptography.hazmat.primitives.ciphers",
    "cryptography.hazmat.primitives.hashes",
    "cryptography.hazmat.primitives.serialization",
    "cryptography.hazmat.primitives.asymmetric",
    "cryptography.hazmat.backends",

    "shield_core",

    # ========================================================
    # HTTP / NETWORK
    # ========================================================

    "requests",
    "requests.adapters",
    "urllib3",
    "urllib3.util",
    "urllib3.util.retry",
    "urllib3.connection",
    "urllib3.connectionpool",

    "certifi",
    "charset_normalizer",
    "idna",

    # ========================================================
    # DATA SCIENCE
    # ========================================================

    "numpy",
    "numpy.core",
    "numpy.lib",
    "numpy.random",

    "pandas",
    "pandas.io",
    "pandas.io.json",
    "pandas.io.formats",

    "scipy",
    "scipy.linalg",
    "scipy.sparse",
    "scipy.special",
    "scipy.stats",
    "scipy.spatial",

    # ========================================================
    # MATPLOTLIB
    # ========================================================

    "matplotlib",
    "matplotlib.backends",
    "matplotlib.pyplot",
    "matplotlib.figure",
    "matplotlib.font_manager",
    "matplotlib.rcsetup",

    # ========================================================
    # PIL
    # ========================================================

    "PIL",
    "PIL.Image",
    "PIL.ImageFilter",
    "PIL.ImageDraw",
    "PIL.ImageFont",

    # ========================================================
    # REPORT GENERATION
    # ========================================================

    "reportlab",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
    "reportlab.lib.styles",
    "reportlab.lib.colors",
    "reportlab.lib.units",
    "reportlab.pdfbase",
    "reportlab.pdfgen",
    "reportlab.platypus",

    # ========================================================
    # HTML / XML
    # ========================================================

    "lxml",
    "lxml.etree",
    "lxml.objectify",
    "lxml.isoschematron",

    # ========================================================
    # RICH
    # ========================================================

    "rich",
    "rich.console",
    "rich.table",
    "rich.progress",
    "rich.panel",
    "rich.layout",
    "rich.text",

    # ========================================================
    # GIS / MAPS
    # ========================================================

    "shapely",
    "shapely.geometry",
    "shapely.ops",

    "pyproj",

    "folium",
    "folium.plugins",
    "branca",
    "xyzservices",

    "plotly",
    "plotly.graph_objs",
    "plotly.express",

    "narwhals",

    # ========================================================
    # NETWORK ANALYSIS
    # ========================================================

    "scapy",
    "scapy.all",
    "scapy.layers",
    "scapy.layers.all",
    "scapy.packet",
    "scapy.fields",
    "scapy.utils",

    # ========================================================
    # OPENCV
    # ========================================================

    "cv2",

    # ========================================================
    # DATABASE
    # ========================================================

    "sqlite3",

    # ========================================================
    # LOGGING / DEBUGGING
    # ========================================================

    "logging",
    "traceback",
    "pdb",

    # ========================================================
    # TYPE SYSTEM
    # ========================================================

    "typing",
    "typing_extensions",
]


# ============================================================
# REMOVE EVENTLET / GEVENT
# ============================================================
#
# DSTerminal does NOT need these for the Windows Socket.IO
# implementation.
#
# Keeping them in the frozen application creates competing
# async backends and can cause:
#
#     ValueError: Invalid async_mode specified
#
# especially when PyInstaller freezes the application.
#

excludedimports = [
    "eventlet",
    "eventlet.hubs",
    "eventlet.hubs.epolls",
    "eventlet.hubs.kqueue",
    "eventlet.hubs.selects",
    "eventlet.hubs.threading",
    "eventlet.green",

    "gevent",
    "gevent.socket",
    "gevent.pool",
    "gevent.queue",
    "gevent.select",
    "gevent.thread",
]


# ============================================================
# ANALYSIS
# ============================================================

a = Analysis(
    [MAIN_SCRIPT],

    pathex=[
        os.getcwd(),
    ],

    binaries=[],

    datas=datas,

    hiddenimports=hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[
        "runtime_stdout_fix.py",
    ],

    excludes=excludedimports,

    win_no_prefer_redirects=False,

    win_private_assemblies=False,

    cipher=block_cipher,

    noarchive=False,
)


# ============================================================
# PYZ
# ============================================================

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)


# ============================================================
# EXE
# ============================================================

exe = EXE(
    pyz,

    a.scripts,

    a.binaries,

    a.zipfiles,

    a.datas,

    [],

    name=APP_NAME,

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    #
    # IMPORTANT:
    # Disable UPX for this application.
    #
    # DSTerminal contains:
    #   numpy
    #   scipy
    #   pandas
    #   cryptography
    #   cv2
    #   matplotlib
    #   shapely
    #
    # UPX can introduce unnecessary runtime problems with
    # native DLLs.
    #
    upx=False,

    upx_exclude=[],

    runtime_tmpdir=None,

    #
    # Keep console enabled because DSTerminal is a terminal/SOC
    # application and its runtime diagnostics are useful.
    #
    console=True,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,

    icon=ICON_FILE,
)