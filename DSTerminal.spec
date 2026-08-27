# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['dsterminal.py'],
    pathex=[],
    binaries=[],
    datas=[('tools', 'tools'), ('static', 'static'), ('templates', 'templates')],
    hiddenimports=['flask_socketio', 'socketio', 'engineio', 'engineio.async_drivers.threading'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['eventlet', 'gevent'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DSTerminal',
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
    icon=['installer_assets/3486-removebg-preview.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DSTerminal',
)
