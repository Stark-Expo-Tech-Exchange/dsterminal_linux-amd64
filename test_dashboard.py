#!/usr/bin/env python
"""Debug script to test dashboard commands"""

import sys
sys.path.insert(0, '.')

print("="*60)
print("ðŸ§ª DSTERMINAL DASHBOARD DEBUG TEST")
print("="*60)

try:
    from dsterminal import SecurityTerminal
    
    print("\n[1] Creating terminal instance...")
    terminal = SecurityTerminal(interactive=False, quiet=True)
    
    print("\n[2] Checking commands dictionary...")
    print(f"    Total commands: {len(terminal.commands)}")
    print(f"    'dashboard' in commands: {'dashboard' in terminal.commands}")
    print(f"    'test' in commands: {'test' in terminal.commands}")
    
    print("\n[3] Testing 'test' command...")
    if 'test' in terminal.commands:
        cmd_entry = terminal.commands['test']
        
        # Handle both dictionary and direct function
        if isinstance(cmd_entry, dict) and 'func' in cmd_entry:
            # It's a dictionary with 'func' key
            result = cmd_entry['func'](['arg1', 'arg2'])
        elif callable(cmd_entry):
            # It's a direct function
            result = cmd_entry(['arg1', 'arg2'])
        else:
            print(f"    âŒ Unknown command type: {type(cmd_entry)}")
            result = None
        
        print(f"    Result: {result}")
    else:
        print("    âŒ 'test' command not found!")
    
    print("\n[4] Testing 'dashboard' command...")
    if 'dashboard' in terminal.commands:
        cmd_entry = terminal.commands['dashboard']
        
        # Handle both dictionary and direct function
        if isinstance(cmd_entry, dict) and 'func' in cmd_entry:
            result = cmd_entry['func']([])
        elif callable(cmd_entry):
            result = cmd_entry([])
        else:
            print(f"    âŒ Unknown command type: {type(cmd_entry)}")
            result = None
        
        print(f"    Result: {result}")
    else:
        print("    âŒ 'dashboard' command not found!")
    
    print("\n[5] Checking dashboard status...")
    print(f"    soc_dashboard_active: {terminal.soc_dashboard_active}")
    
    print("\nâœ… Test complete!")
    
except Exception as e:
    print(f"\nâŒ Error: {e}")
    import traceback
    traceback.print_exc()

print("="*60)