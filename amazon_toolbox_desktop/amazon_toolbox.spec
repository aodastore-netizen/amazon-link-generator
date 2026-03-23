# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# 添加数据文件
added_files = [
    ('app/templates', 'app/templates'),
    ('static/css', 'static/css'),
    ('static/js', 'static/js'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flask',
        'flask_cors',
        'webview',
        'playwright',
        'bs4',
        'requests',
        'lxml',
        'app.server',
        'app.link_generator',
        'app.rank_checker',
        'app.real_link_fetcher',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='亚马逊工具箱',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns' if sys.platform == 'darwin' else 'icon.ico',
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='亚马逊工具箱.app',
        icon='icon.icns',
        bundle_identifier='com.nan.amazon-toolbox',
    )
