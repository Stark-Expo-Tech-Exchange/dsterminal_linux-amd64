# debug_imports.py
"""
Debug script to find what's closing stdout/stderr
"""
import sys
import os
import traceback

# Save original stdout/stderr
original_stdout = sys.stdout
original_stderr = sys.stderr

# Create a wrapper that tracks when it's closed
class DebugStream:
    def __init__(self, name, original):
        self.name = name
        self.original = original
        self._closed = False
        self._writes = []
        
    def write(self, text):
        if self._closed:
            print(f"🔴 ERROR: Write to closed {self.name}!")
            print(f"   Text was: {repr(text[:100])}")
            print("   Stack trace:")
            traceback.print_stack()
            return
        self._writes.append(text)
        return self.original.write(text)
    
    def flush(self):
        if self._closed:
            return
        return self.original.flush()
    
    def fileno(self):
        if self._closed:
            return -1
        return self.original.fileno()
    
    def close(self):
        print(f"⚠️ {self.name} is being closed!")
        print("   Stack trace:")
        traceback.print_stack()
        self._closed = True
    
    @property
    def closed(self):
        return self._closed
    
    def __getattr__(self, name):
        if self._closed:
            return None
        return getattr(self.original, name)

# Replace stdout/stderr with debug versions
sys.stdout = DebugStream("stdout", sys.__stdout__)
sys.stderr = DebugStream("stderr", sys.__stderr__)

print("=" * 70)
print("DEBUG: Starting import sequence")
print("=" * 70)
sys.stdout.flush()

# Now try to import dsterminal step by step
imports_to_try = [
    ('colorama', 'colorama'),
    ('io', 'io'),
    ('subprocess', 'subprocess'),
    ('platform', 'platform'),
    ('prompt_toolkit', 'prompt_toolkit'),
    ('rich', 'rich'),
    ('reportlab', 'reportlab'),
    ('pyfiglet', 'pyfiglet'),
    ('cryptography', 'cryptography'),
    ('deletion_protection', 'deletion_protection'),
    ('dsterminal', 'dsterminal'),
]

for name, module_name in imports_to_try:
    print(f"\n📦 Importing: {name}")
    sys.stdout.flush()
    try:
        if name == 'dsterminal':
            # Try to import and catch the error
            try:
                import dsterminal
                print(f"✅ {name} imported successfully")
            except SystemExit:
                print(f"❌ {name} caused SystemExit")
            except Exception as e:
                print(f"❌ {name} failed: {e}")
                traceback.print_exc()
                # Check if stdout/stderr are still alive
                if hasattr(sys.stdout, '_closed') and sys.stdout._closed:
                    print("🔴 stdout was closed!")
                if hasattr(sys.stderr, '_closed') and sys.stderr._closed:
                    print("🔴 stderr was closed!")
        else:
            __import__(module_name)
            print(f"✅ {name} imported successfully")
    except Exception as e:
        print(f"❌ {name} failed: {e}")
        traceback.print_exc()

print("\n" + "=" * 70)
print("DEBUG: Import sequence complete")
print("=" * 70)

# Check final status
print(f"\nstdout closed: {sys.stdout.closed if hasattr(sys.stdout, 'closed') else 'N/A'}")
print(f"stderr closed: {sys.stderr.closed if hasattr(sys.stderr, 'closed') else 'N/A'}")