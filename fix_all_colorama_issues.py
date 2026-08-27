#!/usr/bin/env python3
import sys
# -*- coding: utf-8 -*-
"""
Fix all colorama OSError 22 issues in DSTerminal files
"""

import os
import re
from pathlib import Path

# Files to fix
FILES_TO_FIX = [
    'certcheck.py',
    'crypto_engine.py',
    'dashboard.py',
    'dsterminal.py',
    'dsterminal_complete.py',
    'dsterminal_dashboard.py',
    'exploit_scanner.py',
    'financial_forensics.py',
    'hardening_dashboard.py',
    'integrity_monitor.py',
    'ioc_edu.py',
    'network_security.py',
    'ransomware_monitor.py',
    'recon.py',
    'recon_full.py',
    'shield_core.py',
    'soc_automated_lab.py',
    'soc_enhanced_modules.py',
    'soc_nmap_dashboard.py',
    'sqlmap_advanced.py',
    'sqlmap_scanner.py',
    'steg_analyzer.py',
    'update.py',
    'vt_scan.py',
    'web_security_analyzer.py',
    'wifi_audit.py',
]

def fix_file(filepath):
    """Fix colorama issues in a single file"""
    if not os.path.exists(filepath):
        print(f"⚠️ File not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # 1. Fix colorama init: convert=True -> convert=False
        if 'init(autoreset=True, strip=False, convert=True)' in content:
            content = content.replace(
                'init(autoreset=True, strip=False, convert=True)',
                'init(autoreset=True, strip=False, convert=False, wrap=False)'
            )
            changes_made.append('colorama init convert=True -> convert=False, wrap=False')
        
        # 2. Remove patched_write function
        if 'def patched_write(self, text):' in content:
            # Find and remove the patched_write function and its call
            # Look for the pattern
            pattern = r'#\s*Patch colorama to handle OSError 22.*?colorama\.AnsiToWin32\.write\s*=\s*patched_write\s*'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            changes_made.append('removed patched_write function')
        
        # 3. Fix safe_write function if present
        if 'def safe_write(text):' in content:
            # Ensure proper indentation
            lines = content.split('\n')
            new_lines = []
            i = 0
            while i < len(lines):
                if 'def safe_write(text):' in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
                    # Skip any incorrectly indented code
                    while i < len(lines) and (lines[i].strip() == '' or lines[i].startswith('        ')):
                        i += 1
                    # Add the correct implementation
                    new_lines.append('    """Safely write to stdout, handling None or errors"""')
                    new_lines.append('    if sys.stdout is None:')
                    new_lines.append('        try:')
                    new_lines.append('            print(text, end="")')
                    new_lines.append('        except:')
                    new_lines.append('            pass')
                    new_lines.append('        return')
                    new_lines.append('    ')
                    new_lines.append('    try:')
                    new_lines.append('        sys.stdout.write(text)')
                    new_lines.append('        sys.stdout.flush()')
                    new_lines.append('    except (OSError, UnicodeEncodeError, AttributeError):')
                    new_lines.append('        try:')
                    new_lines.append('            print(text, end="")')
                    new_lines.append('        except:')
                    new_lines.append('            pass')
                    changes_made.append('fixed safe_write function')
                else:
                    new_lines.append(lines[i])
                    i += 1
            content = '\n'.join(new_lines)
        
        # 4. Add missing re import for ANSI stripping
        if 'ansi_escape = re.compile' in content and 'import re' not in content:
            # Add re import at the top
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import ') and 'import re' not in content[:i+1]:
                    lines.insert(i+1, 'import re')
                    changes_made.append('added missing re import')
                    break
            content = '\n'.join(lines)
        
        # 5. Remove duplicate colorama imports
        if content.count('import colorama') > 1 or content.count('from colorama import') > 1:
            # Remove duplicate imports
            lines = content.split('\n')
            seen_imports = set()
            new_lines = []
            for line in lines:
                if 'import colorama' in line or 'from colorama import' in line:
                    if line.strip() not in seen_imports:
                        seen_imports.add(line.strip())
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
            changes_made.append('removed duplicate colorama imports')
        
        # 6. Add safe write patch at the top if missing
        if 'if sys.stdout is None:' not in content:
            # Add the safe write patch after imports
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
                elif line.startswith('"""') or line.startswith('#'):
                    insert_pos = i + 1
                else:
                    break
            
            patch_code = [
                '',
                '# ============================================================',
                '# FIX: Handle OSError 22 on Windows',
                '# ============================================================',
                'if sys.platform == "win32":',
                '    try:',
                '        import subprocess as sp',
                '        sp.run(["chcp", "65001"], capture_output=True, shell=True)',
                '    except:',
                '        pass',
                '',
                '_original_stdout_write = sys.stdout.write',
                '',
                'def _safe_stdout_write(text):',
                '    try:',
                '        _original_stdout_write(text)',
                '    except OSError as e:',
                '        if e.errno == 22:',
                '            try:',
                '                clean = text.encode("ascii", "ignore").decode("ascii")',
                '                _original_stdout_write(clean)',
                '            except:',
                '                pass',
                '        else:',
                '            raise',
                '    except UnicodeEncodeError:',
                '        try:',
                '            clean = text.encode("ascii", "ignore").decode("ascii")',
                '            _original_stdout_write(clean)',
                '        except:',
                '            pass',
                '',
                'sys.stdout.write = _safe_stdout_write',
                '',
            ]
            
            lines = lines[:insert_pos] + patch_code + lines[insert_pos:]
            content = '\n'.join(lines)
            changes_made.append('added safe stdout patch')
        
        # Save if changes were made
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filepath} - Fixed: {', '.join(changes_made)}")
            return True
        else:
            print(f"⏭️ {filepath} - No changes needed")
            return True
            
    except Exception as e:
        print(f"❌ {filepath} - Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("Colorama OSError 22 Fixer")
    print("="*70 + "\n")
    
    fixed = 0
    failed = 0
    skipped = 0
    
    for file in FILES_TO_FIX:
        if os.path.exists(file):
            if fix_file(file):
                fixed += 1
            else:
                failed += 1
        else:
            print(f"⚠️ File not found: {file}")
            skipped += 1
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Files fixed: {fixed}")
    print(f"❌ Files failed: {failed}")
    print(f"⏭️ Files skipped: {skipped}")
    print("="*70)

if __name__ == "__main__":
    main()