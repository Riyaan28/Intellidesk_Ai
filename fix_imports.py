"""
Fix all relative imports in AI and backend modules
"""
import os
import re

def fix_file(filepath):
    """Fix relative imports in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match relative imports
    pattern = r'from \.(\w+) import'
    
    def replace_import(match):
        module = match.group(1)
        return f'''try:
    from .{module} import'''
    
    # Check if file already has try-except for imports
    if 'except ImportError:' in content:
        print(f"Skipping {filepath} - already has try-except")
        return False
    
    # Find all relative imports
    matches = list(re.finditer(pattern, content))
    if not matches:
        print(f"No relative imports found in {filepath}")
        return False
    
    print(f"Fixing {filepath}")
    
    # For simplicity, let's just add sys.path manipulation at the top
    lines = content.split('\n')
    
    # Find where imports start
    import_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')):
            import_start = i
            break
    
    if import_start > 0:
        # Insert sys.path code before first import
        insert_lines = [
            'import sys',
            'import os',
            'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))',
            ''
        ]
        for line in reversed(insert_lines):
            if line not in content:
                lines.insert(import_start, line)
    
    new_content = '\n'.join(lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

# Fix AI module files
ai_dir = r'C:\Users\sharm\Desktop\code\projects\Intellidesk\ai'
ai_files = ['urgency.py', 'embeddings.py', 'deduplication.py', 'auto_reply.py', '__init__.py']

for filename in ai_files:
    filepath = os.path.join(ai_dir, filename)
    if os.path.exists(filepath):
        fix_file(filepath)

print("Done!")
