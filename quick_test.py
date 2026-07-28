#!/usr/bin/env python3
"""
Quick test to verify all DSTerminal dependencies work
"""

def test_all_modules():
    print("=" * 60)
    print("DSTerminal - Dependency Test")
    print("=" * 60)
    
    # Test imports
    modules = [
        ("Cryptography", "cryptography"),
        ("HTTP Requests", "requests"),
        ("Color Output", "colorama"),
        ("Rich Console", "rich"),
        ("User Input", "prompt_toolkit"),
        ("ASCII Art", "pyfiglet")
    ]
    
    results = []
    
    for name, module_name in modules:
        try:
            __import__(module_name)
            results.append((name, "✅ PASS"))
        except ImportError as e:
            results.append((name, f"❌ FAIL: {e}"))
    
    # Print results
    for name, status in results:
        print(f"{name:20} {status}")
    
    print("=" * 60)
    
    # If all passed, show demo
    if all("✅" in status for _, status in results):
        print("\n🎉 All modules loaded successfully!")
        
        # Demo some features
        import pyfiglet
        font = pyfiglet.Figlet(font='small')
        print(font.renderText('READY'))
        
        import colorama
        from colorama import Fore, Back, Style
        colorama.init()
        
        print(f"{Fore.GREEN}✓ Cryptography: Secure communications")
        print(f"{Fore.BLUE}✓ Requests: HTTP client ready")
        print(f"{Fore.YELLOW}✓ Colorama: Colored terminal output")
        print(f"{Fore.CYAN}✓ Rich: Beautiful console formatting")
        print(f"{Fore.MAGENTA}✓ Prompt Toolkit: Interactive prompts")
        print(f"{Fore.WHITE}✓ Pyfiglet: ASCII art capabilities")
        print(Style.RESET_ALL)
        
        print("=" * 60)
        print("🚀 DSTerminal is ready to launch!")
        return True
    else:
        print("\n⚠️  Some modules failed to load.")
        return False

if __name__ == "__main__":
    test_all_modules()
