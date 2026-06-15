# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json.example', '.'),
    ],
    hiddenimports=[
        'psutil',
        'httpx',
        'win32evtlog',
        'win32evtlogutil',
        'win32con',
        'win32api',
        'win32security',
        'win32net',
        'win32file',
        'win32process',
        'win32service',
        'win32timezone',
        'win32cred',
        'pythoncom',
        'pywintypes',
        'win32com',
        'win32com.client',
        'win32com.server',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy',
        'PIL', 'cv2', 'torch', 'tensorflow', 'jupyter',
        'notebook', 'IPython', 'pytest', 'sphinx',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='j1noc-agent',
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
    icon=None,
    version='version_info.txt',
)