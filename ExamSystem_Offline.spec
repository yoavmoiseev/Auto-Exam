# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Exam System - Offline Standalone Version
Based on School Scheduler approach with proper Flask packaging
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules
import os

block_cipher = None

# Collect all Flask-related packages
datas = []
binaries = []
hiddenimports = []

# Collect Flask and its dependencies
for pkg in ['flask', 'werkzeug', 'jinja2', 'click', 'itsdangerous', 'markupsafe']:
    tmp_ret = collect_all(pkg)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

# Application data folders
datas += [
    ('templates', 'templates'),
    ('static', 'static'),
    ('data', 'data'),
    ('services', 'services'),
    ('routes', 'routes'),
    ('video', 'video'),
    ('Exams', 'Exams'),
]

# Hidden imports for Flask app
hiddenimports += [
    'flask',
    'flask.json',
    'werkzeug',
    'werkzeug.security',
    'werkzeug.serving',
    'werkzeug.middleware',
    'werkzeug.middleware.proxy_fix',
    'jinja2',
    'jinja2.ext',
    'sqlite3',
    'hashlib',
    'logging',
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'email.mime.base',
    'datetime',
    'json',
    'os',
    'sys',
    'threading',
    'signal',
    'webbrowser',
    'socket',
    'time',
]

a = Analysis(
    ['launcher_offline.py'],  # Use new launcher
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        '_tkinter',
        'PIL',
        'PyQt5',
        'PySide2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ExamSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # Keep console for server output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ExamSystem',
)
