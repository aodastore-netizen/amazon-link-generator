from setuptools import setup

APP = ['amazon_link_generator_desktop.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['webview', 'requests', 'bs4'],
    'includes': ['urllib', 're', 'time', 'random', 'json'],
    'plist': {
        'CFBundleName': '亚马逊链接生成器',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.amazon.linkgenerator',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
