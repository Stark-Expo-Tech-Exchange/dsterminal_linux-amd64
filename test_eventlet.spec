# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['test_eventlet.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['eventlet', 'eventlet.hubs', 'eventlet.hubs.selects', 'eventlet.hubs.epolls', 'eventlet.hubs.poll', 'eventlet.hubs.threading', 'flask_socketio', 'socketio', 'engineio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['eventlet.hubs.kqueue', 'eventlet.hubs.kqueue_event'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='test_eventlet',
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
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='test_eventlet',
)
