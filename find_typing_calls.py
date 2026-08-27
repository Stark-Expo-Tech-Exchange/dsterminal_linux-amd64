#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find all typing function calls in dsterminal.py
"""

import re
import os

def find_typing_calls(file_path='dsterminal.py'):
    """Find all typing function calls for replacement"""
    patterns = {
        '_type_text': r'self\._type_text\(([^)]*)\)',
        '_type_header': r'self\._type_header\(([^)]*)\)',
        '_type_success': r'self\._type_success\(([^)]*)\)',
        '_type_error': r'self\._type_error\(([^)]*)\)',
        '_type_warning': r'self\._type_warning\(([^)]*)\)',
        '_type_info': r'self\._type_info\(([^)]*)\)',
        'type_text_colored': r'type_text_colored\(([^)]*)\)',
        'text_type': r'text_type\(([^)]*)\)',
        '_type_finding': r'self\._type_finding\(([^)]*)\)',
        '_type_status': r'self\._type_status\(([^)]*)\)',
        '_cinematic_typing': r'self\._cinematic_typing\(([^)]*)\)',
    }
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {}
    total = 0
    print(f"\n📊 Scanning {file_path} for typing function calls...\n")
    print("=" * 60)
    
    for name, pattern in patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            results[name] = len(matches)
            total += len(matches)
            print(f"  {name:<20}: {len(matches):>3} occurrences")
    
    print("=" * 60)
    print(f"  TOTAL            : {total:>3} occurrences")
    print("\n✅ Scan complete!\n")
    
    return results

def find_with_line_numbers(file_path='dsterminal.py'):
    """Find typing calls with line numbers for reference"""
    patterns = {
        '_type_text': r'self\._type_text',
        '_type_header': r'self\._type_header',
        '_type_success': r'self\._type_success',
        '_type_error': r'self\._type_error',
        '_type_warning': r'self\._type_warning',
        '_type_info': r'self\._type_info',
        'type_text_colored': r'type_text_colored',
        'text_type': r'text_type',
        '_type_finding': r'self\._type_finding',
        '_type_status': r'self\._type_status',
    }
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"\n📊 Line numbers for typing function calls in {file_path}:\n")
    print("=" * 70)
    
    for i, line in enumerate(lines, 1):
        for name, pattern in patterns.items():
            if re.search(pattern, line):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                # Show the line with line number
                line_display = line.strip()[:60] + '...' if len(line.strip()) > 60 else line.strip()
                print(f"  Line {i:>4}: {name:<15} -> {line_display}")
                break
    
    print("=" * 70)
    print("✅ Done!\n")

if __name__ == "__main__":
    # Find all typing calls with counts
    results = find_typing_calls('dsterminal.py')
    
    # Optionally find with line numbers
    print("\n📋 Detailed view with line numbers:")
    find_with_line_numbers('dsterminal.py')