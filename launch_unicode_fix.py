# launch_unicode_fix.py
import sys
import os
import subprocess

# Set environment for UTF-8
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['PYTHONUTF8'] = '1'

# Launch the main script
subprocess.run([sys.executable, 'dsterminal.py'], env=env)