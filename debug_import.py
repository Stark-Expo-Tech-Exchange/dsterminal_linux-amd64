#!python
# debug_import.py
import sys
import traceback

print("=" * 60)
print("DEBUGGING UPDATE IMPORT")
print("=" * 60)

# Step 1: Check if file exists
import os
print(f"\n[1] Checking if update.py exists: {os.path.exists('update.py')}")

# Step 2: Try to import
print("\n[2] Attempting to import UpdateManager...")
try:
    from update import UpdateManager
    print(f"âœ… Import successful!")
    print(f"   UpdateManager class: {UpdateManager}")
except Exception as e:
    print(f"âŒ Import failed!")
    print(f"   Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Try to create an instance
print("\n[3] Attempting to create UpdateManager instance...")
try:
    config = {"CURRENT_VERSION": "3.0.0", "GITHUB_TOKEN": ""}
    manager = UpdateManager(config)
    print(f"âœ… UpdateManager instance created successfully!")
    print(f"   GitHub repo: {manager.github_repo}")
    print(f"   Download dir: {manager.download_dir}")
except Exception as e:
    print(f"âŒ Failed to create instance!")
    print(f"   Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("âœ… All checks passed! update.py is working correctly.")
print("=" * 60)