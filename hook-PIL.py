# hook-PIL.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all PIL submodules
hiddenimports = collect_submodules('PIL')
datas = collect_data_files('PIL')