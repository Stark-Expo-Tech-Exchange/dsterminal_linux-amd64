#!/usr/bin/env python3
"""
DSTERMINAL AUTO-FIXER
Automatically finds and fixes the "slice indices must be integers" error
"""

import re
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

class DSTerminalFixer:
    def __init__(self):
        self.fixes_applied = []
        self.backup_path = None
        
    def find_dsterminal_files(self):
        """Find DSTERMINAL files in common locations"""
        search_paths = [
            Path.cwd(),
            Path.home() / 'Desktop',
            Path.home() / 'Documents',
            Path.home() / 'Downloads',
            Path.home() / 'dsterminal',
            Path.home() / 'DSTERMINAL',
        ]
        
        found_files = []
        for path in search_paths:
            if path.exists():
                # Search for Python files with terminal in name
                for file in path.glob('*terminal*.py'):
                    found_files.append(file)
                for file in path.glob('*DSTERMINAL*.py'):
                    found_files.append(file)
                for file in path.glob('*dsterminal*.py'):
                    found_files.append(file)
                # Also check for the main file
                if (path / 'DSTERMINAL.py').exists():
                    found_files.append(path / 'DSTERMINAL.py')
                if (path / 'dsterminal.py').exists():
                    found_files.append(path / 'dsterminal.py')
                    
        # Remove duplicates
        return list(set(found_files))
    
    def analyze_file(self, file_path):
        """Analyze the DSTERMINAL file for the error source"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
        
        issues = []
        line_numbers = []
        
        # Check for string slicing with potential non-integer values
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Look for string slicing patterns
            slice_patterns = [
                r'\[([^:\]]+):([^:\]]+)\]',  # [start:end]
                r'\[([^:\]]+):\]',  # [start:]
                r'\[:([^:\]]+)\]',  # [:end]
                r'\[([^:\]]+)\]',  # [index]
            ]
            
            for pattern in slice_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if 'len' in line or ' ' in match.group(0):
                        # Check if the slice contains non-integer values
                        if not re.search(r'\d+', match.group(0)):
                            issues.append({
                                'line_num': i,
                                'line': line.strip(),
                                'slice': match.group(0),
                                'issue': 'Non-integer slice value'
                            })
                            if i not in line_numbers:
                                line_numbers.append(i)
            
            # Check for len() function that might be returning non-integer
            if 'len(' in line and ')' in line:
                # Extract the len() call
                len_matches = re.finditer(r'len\(([^)]+)\)', line)
                for match in len_matches:
                    inner = match.group(1)
                    # Check if len is being used on something that might have emojis
                    if '[' in inner or ']' in inner or any(c in inner for c in '!@#$%^&*()_+'):
                        issues.append({
                            'line_num': i,
                            'line': line.strip(),
                            'slice': f"len({inner})",
                            'issue': 'len() on string with special characters may cause issues'
                        })
                        if i not in line_numbers:
                            line_numbers.append(i)
            
            # Check for show_help or help function
            if 'def show_help' in line or 'def _show_help' in line:
                issues.append({
                    'line_num': i,
                    'line': line.strip(),
                    'slice': 'show_help function',
                    'issue': 'Help function might contain problematic slicing'
                })
                if i not in line_numbers:
                    line_numbers.append(i)
            
            # Check for text_type or type function that might use slicing
            if 'text_type' in line or '_type_text' in line or '_type_finding' in line:
                if '[' in line and ']' in line:
                    issues.append({
                        'line_num': i,
                        'line': line.strip(),
                        'slice': 'text_type function with slicing',
                        'issue': 'Typing function might be using slicing'
                    })
                    if i not in line_numbers:
                        line_numbers.append(i)
        
        return {
            'content': content,
            'lines': lines,
            'issues': issues,
            'line_numbers': sorted(line_numbers)
        }
    
    def create_backup(self, file_path):
        """Create a backup of the original file"""
        backup_dir = file_path.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'{file_path.stem}_backup_{timestamp}{file_path.suffix}'
        
        shutil.copy2(file_path, backup_path)
        self.backup_path = backup_path
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def apply_fix(self, file_path, analysis):
        """Apply fixes to the file"""
        if not analysis or not analysis['issues']:
            print("❌ No issues found to fix")
            return False
        
        content = analysis['content']
        lines = analysis['lines']
        
        # Create a copy of the content to modify
        new_content = content
        
        # Fix 1: Add safe_len function if not present
        if 'def safe_len' not in content:
            safe_len_func = '''
    def safe_len(self, text):
        """Safely get length of text, handling emojis and special characters"""
        try:
            import re
            ansi_escape = re.compile(r'\\x1b\\[[0-9;]*[a-zA-Z]|\\x1b\\[[0-9;]*m')
            clean = ansi_escape.sub('', str(text))
            try:
                import wcwidth
                return sum(wcwidth.wcwidth(c) for c in clean)
            except:
                return len(clean.encode('ascii', 'ignore').decode('ascii', 'ignore'))
        except:
            return len(str(text))
'''
            # Find the class definition to insert the method
            class_match = re.search(r'class\s+\w+.*?:', content)
            if class_match:
                insert_pos = class_match.end()
                # Find the first method to insert after
                methods = re.finditer(r'\n\s+def\s+\w+', content)
                for method in methods:
                    if method.start() > insert_pos:
                        # Insert before the first method
                        new_content = (content[:method.start()] + 
                                     safe_len_func + 
                                     content[method.start():])
                        self.fixes_applied.append("Added safe_len function")
                        break
                else:
                    # If no methods found, insert at the end of the class
                    class_end = content.rfind('\n    def')
                    if class_end == -1:
                        class_end = len(content)
                    new_content = (content[:class_end] + 
                                 safe_len_func + 
                                 content[class_end:])
                    self.fixes_applied.append("Added safe_len function at end of class")
            else:
                # If no class found, add at the top
                new_content = safe_len_func + content
                self.fixes_applied.append("Added safe_len function at top")
        
        # Fix 2: Replace problematic show_help function
        show_help_pattern = r'def\s+show_help\s*\([^)]*\)\s*:.*?(?=def\s|\Z)'
        show_help_matches = list(re.finditer(show_help_pattern, new_content, re.DOTALL))
        
        if show_help_matches:
            for match in show_help_matches:
                # Create a safe version of show_help
                safe_help = '''
    def show_help(self):
        """Display help menu with proper emoji handling"""
        try:
            from colorama import Fore, Style, init
            import shutil
            import re
            import time
            
            init(autoreset=True)
            
            # Get terminal width
            try:
                terminal_width = shutil.get_terminal_size().columns
                if terminal_width < 80:
                    terminal_width = 80
                if terminal_width > 120:
                    terminal_width = 120
            except:
                terminal_width = 80
            
            box_width = min(terminal_width - 4, 110)
            if box_width < 60:
                box_width = 60
            
            def safe_print(text, color=None, end='\\n'):
                """Print text safely"""
                try:
                    if color:
                        print(f"{color}{text}{Style.RESET_ALL}", end=end)
                    else:
                        print(text, end=end)
                except:
                    print(str(text), end=end)
            
            # Simple header
            safe_print("=" * box_width, Fore.CYAN)
            safe_print(" DSTERMINAL v4.0.0.113 - Command Reference Manual", Fore.CYAN)
            safe_print(" INTERACTIVE COMMAND MENU", Fore.YELLOW)
            safe_print("=" * box_width, Fore.CYAN)
            
            # Basic commands
            commands = {
                "System Commands": {
                    "sysinfo": "Detailed system report",
                    "certcheck <domain>": "Check SSL/TLS certificates",
                    "harden": "System hardening menu"
                },
                "Network Commands": {
                    "nmap <TARGET>": "Network scan",
                    "net -n mon": "Live network monitoring",
                    "portsweep [IP]": "Scan for open ports"
                },
                "Utility Commands": {
                    "help": "Show this help menu",
                    "clear": "Clear terminal screen",
                    "exit": "Quit terminal"
                }
            }
            
            for category, cmds in commands.items():
                safe_print(f"\\n {category}", Fore.CYAN)
                safe_print("-" * (box_width - 2), Fore.CYAN)
                for cmd, desc in cmds.items():
                    try:
                        cmd_len = self.safe_len(cmd) if hasattr(self, 'safe_len') else len(cmd)
                        padding = max(0, 25 - cmd_len)
                        safe_print(f"  {cmd}{' ' * padding} - {desc}", Fore.GREEN)
                    except:
                        safe_print(f"  {cmd} - {desc}", Fore.GREEN)
            
            safe_print("=" * box_width, Fore.CYAN)
            safe_print("\\n💡 Type 'help <command>' for detailed information", Fore.YELLOW)
            safe_print("💡 Type 'exit' to quit", Fore.YELLOW)
            
            # Interactive search (simplified, safe version)
            while True:
                try:
                    user_input = input(f"{Fore.CYAN}└─$ {Style.RESET_ALL}").strip().lower()
                    if user_input in ["exit", "q", ""]:
                        break
                    elif user_input == "search":
                        print(f"{Fore.YELLOW}Enter search term: {Style.RESET_ALL}", end="")
                        term = input().strip().lower()
                        if term:
                            found = False
                            print(f"\\n{Fore.GREEN}Search results for '{term}':{Style.RESET_ALL}")
                            for category, cmds in commands.items():
                                for cmd, desc in cmds.items():
                                    if term in cmd.lower() or term in desc.lower():
                                        found = True
                                        print(f"  {cmd} - {desc}")
                            if not found:
                                print(f"{Fore.RED}No commands found{Style.RESET_ALL}")
                    else:
                        found = False
                        for category, cmds in commands.items():
                            for cmd, desc in cmds.items():
                                if user_input in cmd.lower():
                                    found = True
                                    print(f"{Fore.GREEN}{cmd}:{Style.RESET_ALL} {desc}")
                        if not found:
                            print(f"{Fore.RED}Command '{user_input}' not found{Style.RESET_ALL}")
                except (KeyboardInterrupt, EOFError):
                    print()
                    break
            
            print(f"{Fore.GREEN}Help system closed{Style.RESET_ALL}")
            
        except Exception as e:
            # Ultimate fallback
            print(f"\\n{Fore.RED}Error in help: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Available commands: sysinfo, certcheck, help, exit{Style.RESET_ALL}")
'''
                
                # Replace the old show_help with the new one
                new_content = new_content[:match.start()] + safe_help + new_content[match.end():]
                self.fixes_applied.append("Replaced show_help function with safe version")
        
        # Fix 3: Replace any problematic len() calls with safe_len
        len_pattern = r'len\(([^)]+)\)'
        len_matches = list(re.finditer(len_pattern, new_content))
        for match in reversed(len_matches):
            inner = match.group(1)
            # Only replace if it might contain emojis or special chars
            if any(c in inner for c in '!@#$%^&*()_+[]{}'):
                # Check if this is in a slicing operation
                before = new_content[:match.start()]
                after = new_content[match.end():]
                if '[' in before and ']' in after:
                    # Replace len with self.safe_len
                    new_content = (new_content[:match.start()] + 
                                 f"self.safe_len({inner})" + 
                                 new_content[match.end():])
                    self.fixes_applied.append(f"Replaced len({inner}) with safe_len")
        
        # Write the fixed content back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False
    
    def run(self):
        """Main execution"""
        print("=" * 70)
        print(" DSTERMINAL AUTO-FIXER - Find and Fix Slice Error")
        print("=" * 70)
        print()
        
        # Find DSTERMINAL files
        print("🔍 Searching for DSTERMINAL files...")
        files = self.find_dsterminal_files()
        
        if not files:
            print("❌ No DSTERMINAL files found.")
            print("\nPlease enter the path to your DSTERMINAL file:")
            user_path = input("Path: ").strip()
            if user_path and Path(user_path).exists():
                files = [Path(user_path)]
            else:
                print("❌ File not found. Exiting.")
                return
        
        print(f"\n✅ Found {len(files)} file(s):")
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file}")
        
        # Let user select file
        print("\nSelect file to fix (or 0 to fix all):")
        choice = input("Number: ").strip()
        
        try:
            if choice == "0":
                selected_files = files
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    selected_files = [files[idx]]
                else:
                    print("❌ Invalid selection.")
                    return
        except ValueError:
            print("❌ Invalid input. Exiting.")
            return
        
        # Process each file
        for file_path in selected_files:
            print(f"\n{'=' * 70}")
            print(f" Processing: {file_path.name}")
            print('=' * 70)
            
            # Create backup
            self.create_backup(file_path)
            
            # Analyze file
            print("🔍 Analyzing file...")
            analysis = self.analyze_file(file_path)
            
            if not analysis:
                print("❌ Could not analyze file.")
                continue
            
            print(f"📊 Found {len(analysis['issues'])} potential issue(s)")
            
            if analysis['issues']:
                print("\nIssues found:")
                for issue in analysis['issues'][:10]:  # Show first 10
                    print(f"  Line {issue['line_num']}: {issue['issue']}")
                    print(f"    {issue['line'][:100]}")
                if len(analysis['issues']) > 10:
                    print(f"  ... and {len(analysis['issues']) - 10} more")
            else:
                print("✅ No issues found in this file.")
                continue
            
            # Apply fixes
            print("\n🔧 Applying fixes...")
            if self.apply_fix(file_path, analysis):
                print(f"✅ Fixed {len(self.fixes_applied)} issue(s):")
                for fix in self.fixes_applied:
                    print(f"  ✓ {fix}")
                print(f"\n✅ File saved: {file_path}")
                print(f"💾 Backup saved: {self.backup_path}")
            else:
                print("❌ Failed to apply fixes.")
        
        print("\n" + "=" * 70)
        print(" ✅ Auto-fixer completed!")
        print("=" * 70)
        print("\n💡 If the issue persists, try:")
        print("  1. Restart DSTERMINAL")
        print("  2. Check if the backup file works")
        print("  3. Manually review the fixed code")

if __name__ == "__main__":
    try:
        fixer = DSTerminalFixer()
        fixer.run()
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()