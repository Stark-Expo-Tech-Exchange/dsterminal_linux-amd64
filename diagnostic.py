# diagnostic.py
"""
Diagnostic script to find the source of "I/O operation on closed file" error
"""

import sys
import os
import traceback
import inspect

def diagnose_io_error():
    """Diagnose I/O operation on closed file error"""
    
    print("=" * 70)
    print("DIAGNOSTIC: Checking Python environment")
    print("=" * 70)
    
    # 1. Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    
    # 2. Check stdout/stderr status
    print("\n" + "=" * 70)
    print("CHECKING STDOUT/STDERR STATUS")
    print("=" * 70)
    
    for name, stream in [('stdout', sys.stdout), ('stderr', sys.stderr)]:
        print(f"\n{name.upper()}:")
        print(f"  Object: {stream}")
        print(f"  Type: {type(stream)}")
        
        if hasattr(stream, 'fileno'):
            try:
                fd = stream.fileno()
                print(f"  Fileno: {fd}")
                print(f"  Is TTY: {os.isatty(fd) if hasattr(os, 'isatty') else 'N/A'}")
            except Exception as e:
                print(f"  ❌ Error getting fileno: {e}")
        
        if hasattr(stream, 'closed'):
            print(f"  Closed: {stream.closed}")
        
        if hasattr(stream, 'buffer'):
            print(f"  Has buffer: Yes")
            if hasattr(stream.buffer, 'closed'):
                print(f"  Buffer closed: {stream.buffer.closed}")
        else:
            print(f"  Has buffer: No")
    
    # 3. Check if any modules are messing with stdout/stderr
    print("\n" + "=" * 70)
    print("CHECKING FOR MODULES THAT MIGHT CLOSE STREAMS")
    print("=" * 70)
    
    # Check for common modules that might cause issues
    suspicious_modules = ['colorama', 'IPython', 'jupyter', 'pyreadline', 'idlelib']
    
    for module_name in suspicious_modules:
        try:
            mod = __import__(module_name)
            print(f"✅ Found module: {module_name} (version: {getattr(mod, '__version__', 'unknown')})")
        except ImportError:
            pass
    
    # 4. Check if we're running in a special environment
    print("\n" + "=" * 70)
    print("CHECKING ENVIRONMENT")
    print("=" * 70)
    
    env_vars = ['TERM', 'COLORTERM', 'PYTHONIOENCODING', 'PYTHONUTF8']
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        print(f"{var}: {value}")
    
    # 5. Try to write to stdout/stderr
    print("\n" + "=" * 70)
    print("TESTING WRITE OPERATIONS")
    print("=" * 70)
    
    try:
        sys.stdout.write("✅ Write to stdout successful\n")
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Write to stdout failed: {e}")
        traceback.print_exc()
    
    try:
        sys.stderr.write("✅ Write to stderr successful\n")
        sys.stderr.flush()
    except Exception as e:
        print(f"❌ Write to stderr failed: {e}")
        traceback.print_exc()
    
    # 6. Try to see if the error occurs when using specific modules
    print("\n" + "=" * 70)
    print("TESTING COMMON MODULES")
    print("=" * 70)
    
    modules_to_test = [
        'subprocess', 'socket', 'time', 'random', 'json', 
        'shutil', 'datetime', 'pathlib', 'typing', 'hashlib'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
        except Exception as e:
            print(f"❌ {module_name} import failed: {e}")
    
    # 7. Try Colorama specifically
    print("\n" + "=" * 70)
    print("TESTING COLORAMA")
    print("=" * 70)
    
    try:
        from colorama import init, Fore, Back, Style
        init(autoreset=True)
        print(f"✅ Colorama initialized successfully")
        print(f"   Fore.RED: {Fore.RED}")
    except Exception as e:
        print(f"❌ Colorama failed: {e}")
        traceback.print_exc()
    
    # 8. Try ReportLab
    print("\n" + "=" * 70)
    print("TESTING REPORTLAB")
    print("=" * 70)
    
    try:
        from reportlab.lib.pagesizes import letter
        print("✅ ReportLab imported successfully")
    except ImportError:
        print("❌ ReportLab not found (this is optional)")
    except Exception as e:
        print(f"❌ ReportLab failed: {e}")
    
    # 9. Check for monkey patching
    print("\n" + "=" * 70)
    print("CHECKING FOR MONKEY PATCHING")
    print("=" * 70)
    
    # Check if stdout has been replaced
    if sys.stdout is not sys.__stdout__:
        print("⚠️ sys.stdout has been replaced!")
        print(f"   Original: {sys.__stdout__}")
        print(f"   Current:  {sys.stdout}")
    
    if sys.stderr is not sys.__stderr__:
        print("⚠️ sys.stderr has been replaced!")
        print(f"   Original: {sys.__stderr__}")
        print(f"   Current:  {sys.stderr}")
    
    # 10. Try to find what's closing the file
    print("\n" + "=" * 70)
    print("ATTEMPTING TO CATCH THE ERROR")
    print("=" * 70)
    
    # Save original write methods
    original_stdout_write = sys.stdout.write
    original_stderr_write = sys.stderr.write
    
    def safe_stdout_write(text):
        try:
            original_stdout_write(text)
        except Exception as e:
            print(f"🔴 stdout.write failed: {e}")
            print(f"   Stack trace:")
            traceback.print_stack()
    
    def safe_stderr_write(text):
        try:
            original_stderr_write(text)
        except Exception as e:
            print(f"🔴 stderr.write failed: {e}")
            print(f"   Stack trace:")
            traceback.print_stack()
    
    # Replace with safe versions if they're not already broken
    try:
        sys.stdout.write = safe_stdout_write
        sys.stderr.write = safe_stderr_write
        print("✅ Installed safe write handlers")
    except Exception as e:
        print(f"❌ Could not install safe handlers: {e}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    diagnose_io_error()