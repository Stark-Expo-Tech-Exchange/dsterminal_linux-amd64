# test_minimal.py
"""
Minimal test to reproduce the error
"""

import sys
import os

print("Starting minimal test...")
sys.stdout.flush()

# Try to reproduce the error with minimal code
try:
    # Attempt to manipulate stdout
    if sys.platform == 'win32':
        print("Windows detected")
        
        # Try the problematic code pattern
        if hasattr(sys.stdout, 'buffer'):
            print("stdout has buffer")
            try:
                # This is what might be causing the issue
                sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', errors='ignore')
                print("Reopened stdout successfully")
            except Exception as e:
                print(f"Failed to reopen stdout: {e}")
        
        if hasattr(sys.stderr, 'buffer'):
            print("stderr has buffer")
            try:
                sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', errors='ignore')
                print("Reopened stderr successfully")
            except Exception as e:
                print(f"Failed to reopen stderr: {e}")
    
    print("Test completed successfully")
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()