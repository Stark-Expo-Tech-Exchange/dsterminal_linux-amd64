# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('static', 'static'), ('3486-removebg-preview.ico', '.')]
binaries = []
hiddenimports = ['psutil', 'netifaces', 'flask', 'flask_socketio', 'socketio', 'engineio', 'werkzeug', 'werkzeug.wsgi', 'jinja2', 'markupsafe', 'datetime', 'json', 'hashlib', 'threading', 'subprocess', 'shutil', 'platform', 'webbrowser', 'random', 'time', 'os', 'sys', 'logging', 'contextlib', 'io', 'colorama', 'colorama.ansitowin32', 'colorama.win32', 'colorama.initialise']
tmp_ret = collect_all('flask')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('flask_socketio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('werkzeug')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jinja2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('markupsafe')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('python_socketio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('python_engineio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['dsterminal.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas', 'opencv-python', 'cv2', 'torch', 'tensorflow', 'scipy', 'sklearn', 'PyQt5', 'PyQt6', 'tkinter', 'test', 'pytest', 'setuptools', 'pip', '_tkinter', 'tkinter', 'distutils', 'wheel'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dsterminal_win-4.0.0.113_x64-amd64',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
