# netifaces.py - DSTERMINAL wrapper for netifaces native module
# This file redirects imports to the native .pyd module

import sys
import os

# Try to import the native module
try:
    # First try: import the .pyd directly
    import importlib.util
    
    # Find the .pyd file
    pyd_path = os.path.join(os.path.dirname(__file__), 'netifaces.cp311-win_amd64.pyd')
    if os.path.exists(pyd_path):
        spec = importlib.util.spec_from_file_location('_netifaces_native', pyd_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Copy all attributes to this module
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    globals()[attr_name] = getattr(module, attr_name)
            __all__ = [a for a in dir(module) if not a.startswith('_')]
    else:
        # Fallback: try normal import
        import netifaces as _netifaces
        for attr_name in dir(_netifaces):
            if not attr_name.startswith('_'):
                globals()[attr_name] = getattr(_netifaces, attr_name)
        __all__ = [a for a in dir(_netifaces) if not a.startswith('_')]
        
except ImportError as e:
    # If all else fails, raise a helpful error
    raise ImportError(
        f"Could not import netifaces. The native module file (netifaces.cp311-win_amd64.pyd) "
        f"was not found. Please ensure it's in the same directory as this file.\n"
        f"Original error: {e}"
    )

# Clean up the module's __name__
__name__ = 'netifaces'
