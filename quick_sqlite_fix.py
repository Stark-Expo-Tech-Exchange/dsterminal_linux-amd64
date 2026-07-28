# Save as sqlite_fix.py
import sqlite3
import threading

# Apply SQLite thread fix before importing anything else
sqlite3.enable_callback_tracebacks(True)
sqlite3.threadsafety = 2  # 2 = threads can share connections

# Override the connect method to use check_same_thread=False
_original_connect = sqlite3.connect

def patched_connect(database, *args, **kwargs):
    kwargs['check_same_thread'] = False
    return _original_connect(database, *args, **kwargs)

sqlite3.connect = patched_connect

print("✅ SQLite thread fix applied")
print("\nNow restart the protection module:")
print("python immigration_integration.py")