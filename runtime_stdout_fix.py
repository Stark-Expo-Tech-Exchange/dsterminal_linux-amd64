# runtime_stdout_fix.py
# DSTerminal® PyInstaller console runtime hook

import os
import sys

# ------------------------------------------------------------
# Windows UTF-8 environment
# ------------------------------------------------------------

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


# ------------------------------------------------------------
# Keep PyInstaller console stdin/stdout/stderr intact
# ------------------------------------------------------------

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        pass


if sys.stderr is not None:
    try:
        sys.stderr.reconfigure(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        pass


# ------------------------------------------------------------
# Windows console code page
# ------------------------------------------------------------

if os.name == "nt":
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32

        # UTF-8 input/output
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)

    except Exception:
        pass


# ------------------------------------------------------------
# IMPORTANT:
# Do NOT replace:
#
#   sys.stdin
#   sys.stdout
#   sys.stderr
#
# Do NOT monkey-patch prompt_toolkit.
#
# DSTerminal's command dispatcher must retain direct
# access to the real Windows console input stream.
# ------------------------------------------------------------

try:
    sys.stdout.write(
        "[RUNTIME] DSTerminal console runtime hooks loaded\n"
    )
    sys.stdout.flush()
except Exception:
    pass