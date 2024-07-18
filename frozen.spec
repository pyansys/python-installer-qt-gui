"""pyinstaller app generation"""
import glob
import os
import sys

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata
from ansys.tools.path.misc import is_linux

block_cipher = None

# path where this file is located
try:
    THIS_PATH = os.path.dirname(__file__)
except NameError:
    THIS_PATH = os.getcwd()

OUT_PATH = 'ansys_python_manager'
APP_NAME = 'ansys_python_manager' if is_linux() else 'Ansys Python Manager'

INSTALLER_PATH = os.path.join(THIS_PATH, 'src/ansys/tools/installer')
ASSETS_PATH = os.path.join(INSTALLER_PATH, 'assets')
ICON_FILE = os.path.join(ASSETS_PATH, 'pyansys_icon.ico')

# consider testing paths
main_py = os.path.join(THIS_PATH, 'src/ansys/tools/installer/__main__.py')

if not os.path.isfile(main_py):
    raise FileNotFoundError(f'Unable to locate main entrypoint at {main_py}')

added_files = [
    (os.path.join(ASSETS_PATH, 'pyansys-light.png'), 'assets'),
    (os.path.join(ASSETS_PATH, 'ansys-favicon.png'), 'assets'),
    (os.path.join(ASSETS_PATH, 'pyansys_icon.ico'), 'assets'),
    (os.path.join(INSTALLER_PATH, 'VERSION'), '.'),
]

# Missing metadata
added_files += copy_metadata('ansys-tools-path')

if is_linux() and os.getenv("ADD_PYTHON_BINARIES","true") == "true":
    added_files +=[(os.path.join(ASSETS_PATH, 'python-asset'), 'assets')]

if is_linux():
    added_files +=[(os.path.join(ASSETS_PATH, 'scripts'), 'assets')]

a = Analysis([main_py],
             pathex=[INSTALLER_PATH],
             binaries=[],
             datas=added_files,
             hiddenimports=['_cffi_backend'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# a.datas += [('.ico', icon_file, 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=APP_NAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon=ICON_FILE)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=OUT_PATH)
