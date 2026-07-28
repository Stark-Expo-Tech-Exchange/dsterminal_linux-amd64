import sys

with open('dsterminal.py', 'r') as f:
    content = f.read()

# Check if console is defined
if 'console = Console()' not in content and 'from rich.console import Console' not in content:
    # Add the import and console definition
    lines = content.split('\n')
    new_lines = []
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Look for rich import or similar
        if 'import rich' in line or 'from rich' in line or 'Console' in line:
            # Add console definition after imports
            if not added and i+1 < len(lines):
                new_lines.append('console = Console()')
                added = True
    
    if not added:
        # Add at the beginning of the file
        new_lines.insert(0, 'from rich.console import Console')
        new_lines.insert(1, 'console = Console()')
    
    content = '\n'.join(new_lines)
    
    with open('dsterminal_fixed.py', 'w') as f:
        f.write(content)
    
    print("Created dsterminal_fixed.py with console definition")
else:
    print("console already defined in script")
