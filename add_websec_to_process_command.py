# add_websec_to_process_command.py
"""
Add web security commands to process_command in dsterminal.py
"""
import re

print("="*60)
print("ADDING WEB SECURITY COMMANDS TO PROCESS_COMMAND")
print("="*60)

# Read the file
with open('dsterminal.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if web security commands already exist
if 'web-security' in content and 'websec' in content:
    print("✅ Web security commands already found in process_command")
    print("No changes needed!")
else:
    print("⚠️ Web security commands NOT found in process_command")
    print("Adding them now...")
    
    # Find the hardening commands section end
    # Look for the pattern after the hardening commands
    hardening_end_pattern = r"(elif cmd_lower == 'harden-users':\s+self\.harden_users_only\(\)\s+return True)"
    
    match = re.search(hardening_end_pattern, content)
    
    if match:
        insert_pos = match.end()
        
        websec_block = '''
    
    # ======================== WEB SECURITY COMMANDS ============================
    # Web Security Analyzer commands
    elif cmd_lower in ['web-security', 'websec', 'ws', 'web-analyzer', 'wsa']:
        self.launch_web_security_analyzer()
        return True
    
    # Web Security quick scan commands (redirect to dashboard)
    elif cmd_lower in ['web-scan', 'webscan', 'web-headers', 'webheaders', 'web-ssl', 'webssl', 'web-vuln', 'webvuln', 'web-full', 'webfull']:
        if hasattr(self, 'web_security_available') and self.web_security_available:
            print(f"{Fore.YELLOW}[!] Please use the web-security dashboard for scanning{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Type 'web-security' to launch the full dashboard{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Or run: web-security --help for options{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Web Security Analyzer not available{Style.RESET_ALL}")
        return True
'''
        
        new_content = content[:insert_pos] + websec_block + content[insert_pos:]
        
        # Write the file
        with open('dsterminal.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Added web security commands after hardening section")
    else:
        print("❌ Could not find hardening section end")
        print("Please manually add the commands")

print("="*60)
print("Patch complete!")
print("\nTo test, run:")
print("  python -c 'import dsterminal; dsterminal.main()'")
print("  Then type: web-security")