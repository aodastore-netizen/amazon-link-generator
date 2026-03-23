# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 获取 Playwright 浏览器路径
try:
    import playwright
    playwright_path = os.path.dirname(playwright.__file__)
    browser_path = os.path.join(playwright_path, 'driver', 'package', '.local-browsers')
except:
    browser_path = None

# 数据文件
added_files = []
if browser_path and os.path.exists(browser_path):
    added_files.append((browser_path, 'playwright_browsers'))

a = Analysis(
    ['amazon_link_generator_desktop.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'webview', 'webview.platforms.winforms',
        'requests', 'bs4', 'urllib', 're', 'time', 'random', 'json',
        'playwright', 'playwright.sync_api', 'playwright._impl',
        'playwright._impl._driver', 'playwright._impl._browser_type',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
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
    name='amazon_link_generator',
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
    icon=None,
)
