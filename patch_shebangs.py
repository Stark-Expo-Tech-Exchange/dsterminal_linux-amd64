# patch_shebangs.py - Run this once to fix all shebangs
import os
import sys
import re
from pathlib import Path

def get_python_path():
    """Get the current Python interpreter path"""
    return sys.executable

def patch_shebang(file_path, python_path):
    """Add or update shebang in Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has shebang
        shebang_pattern = r'^#!.*python.*$'
        has_shebang = re.search(shebang_pattern, content, re.MULTILINE)
        
        new_shebang = f'#!{python_path}'
        
        if has_shebang:
            # Replace existing shebang
            new_content = re.sub(shebang_pattern, new_shebang, content, count=1, flags=re.MULTILINE)
            action = "Updated"
        else:
            # Add shebang at the beginning
            new_content = new_shebang + '\n' + content
            action = "Added"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return action, file_path
        
    except Exception as e:
        return f"Error", f"{file_path}: {e}"

def find_python_files(root_dir):
    """Find all Python files in the project"""
    python_files = []
    exclude_dirs = ['venv', '__pycache__', '.git', '.idea', 'node_modules']
    
    for path in Path(root_dir).rglob('*.py'):
        # Skip excluded directories
        if any(exclude in str(path) for exclude in exclude_dirs):
            continue
        # Skip the patch script itself
        if path.name == 'patch_shebangs.py':
            continue
        python_files.append(path)
    
    return python_files

def main():
    # Get the current Python interpreter path
    python_path = sys.executable
    print(f"Using Python interpreter: {python_path}")
    print("-" * 60)
    
    # Find all Python files
    project_root = Path.cwd()
    print(f"Scanning project root: {project_root}")
    print("-" * 60)
    
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files")
    print("-" * 60)
    
    # Patch each file
    patched_count = 0
    error_count = 0
    
    for file_path in python_files:
        action, result = patch_shebang(file_path, python_path)
        if action != "Error":
            patched_count += 1
            print(f"[{action}] {file_path.relative_to(project_root)}")
        else:
            error_count += 1
            print(f"[ERROR] {result}")
    
    print("-" * 60)
    print(f"Summary: {patched_count} files patched, {error_count} errors")

if __name__ == '__main__':
    main()