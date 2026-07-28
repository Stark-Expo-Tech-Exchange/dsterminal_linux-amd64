# find_dsterminal_class.py
import dsterminal
import inspect

print("="*60)
print("FINDING DSTERMINAL CLASS")
print("="*60)

# List all attributes in the module
print("\nAttributes in dsterminal module:")
attrs = dir(dsterminal)
for attr in attrs:
    if not attr.startswith('_'):
        obj = getattr(dsterminal, attr)
        if inspect.isclass(obj):
            print(f"  📦 {attr} (class)")
        elif inspect.isfunction(obj):
            print(f"  🔧 {attr} (function)")
        else:
            print(f"  📄 {attr}")

# Look for any class with "Terminal" or "DST" in name
print("\nSearching for DSTERMINAL class...")
terminal_classes = []
for attr in attrs:
    if not attr.startswith('_'):
        obj = getattr(dsterminal, attr)
        if inspect.isclass(obj):
            if 'terminal' in attr.lower() or 'dst' in attr.lower():
                terminal_classes.append(attr)
                print(f"✅ Found potential class: {attr}")

if terminal_classes:
    print(f"\nPotential classes: {', '.join(terminal_classes)}")
    # Try to instantiate the first one
    try:
        terminal = getattr(dsterminal, terminal_classes[0])()
        print(f"✅ Successfully instantiated {terminal_classes[0]}")
    except Exception as e:
        print(f"❌ Could not instantiate: {e}")
else:
    print("\n❌ No DSTERMINAL class found!")
    print("The class might be defined differently or inside a function.")
    print("\nChecking for main entry point:")
    if hasattr(dsterminal, 'main'):
        print("  ✅ main() function found")
    elif hasattr(dsterminal, 'run'):
        print("  ✅ run() function found")
    else:
        print("  ❌ No main() or run() function found")

print("="*60)