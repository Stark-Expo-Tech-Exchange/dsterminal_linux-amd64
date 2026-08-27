# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


# ============================================================
# SOCKET.IO / ENGINE.IO HIDDEN IMPORTS
# ============================================================

hiddenimports = []

hiddenimports += collect_submodules("flask_socketio")
hiddenimports += collect_submodules("socketio")
hiddenimports += collect_submodules("engineio")
hiddenimports += collect_submodules("simple_websocket")


# ============================================================
# ANALYSIS
# ============================================================

a = Analysis(
    ["test_socketio.py"],

    pathex=[],

    binaries=[],

    datas=[],

    hiddenimports=hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[
        "eventlet",
        "gevent",
        "geventwebsocket",
    ],

    noarchive=False,
)


# ============================================================
# PYZ
# ============================================================

pyz = PYZ(
    a.pure
)


# ============================================================
# EXE
# ============================================================

exe = EXE(
    pyz,
    a.scripts,

    a.binaries,
    a.datas,

    [],

    name="DSTerminal_SocketIO_Test",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    console=True,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,
)