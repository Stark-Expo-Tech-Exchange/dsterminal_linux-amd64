# debug_dsterminal.py
import sys
import traceback
import os

print("=" * 60)
print("DEBUGGING DSTERMINAL IMPORT")
print("=" * 60)

# Step 1: Check if dsterminal.py exists
print(f"\n[1] Checking if dsterminal.py exists: {os.path.exists('dsterminal.py')}")

# Step 2: Try to import dsterminal
print("\n[2] Attempting to import dsterminal...")
try:
    import dsterminal
    print(f"âœ… Import successful!")
    
    # Step 3: Check if DSTerminal class exists
    if hasattr(dsterminal, 'DSTerminal'):
        print(f"   âœ… DSTerminal class found")
        
        # Step 4: Try to create instance
        print("\n[3] Attempting to create DSTerminal instance...")
        try:
            terminal = dsterminal.DSTerminal()
            print(f"âœ… DSTerminal instance created successfully!")
            
            # Step 5: Check for update method
            if hasattr(terminal, 'check_for_updates'):
                print(f"   âœ… check_for_updates method found")
            else:
                print(f"   âš ï¸ check_for_updates method not found")
                
            if hasattr(terminal, 'show_version'):
                print(f"   âœ… show_version method found")
            else:
                print(f"   âš ï¸ show_version method not found")
                
        except Exception as e:
            print(f"âŒ Failed to create instance!")
            print(f"   Error: {e}")
            traceback.print_exc()
    else:
        print(f"   âŒ DSTerminal class not found")
        
except Exception as e:
    print(f"âŒ Import failed!")
    print(f"   Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)
print("DEBUGGING COMPLETE")
print("=" * 60)