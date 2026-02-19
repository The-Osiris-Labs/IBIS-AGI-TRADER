#!/usr/bin/env python3
"""
Script to fix logger initialization issues in the IBIS project.
"""

import os
import re


def fix_logger_initialization():
    """Fix logger initialization issues in all Python files."""
    
    # Find all Python files
    python_files = []
    for dir_name in ['ibis', 'examples', 'tests']:
        dir_path = os.path.join("/root/projects/Dont enter unless solicited/AGI Trader", dir_name)
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
    
    # Patterns to match
    patterns = [
        # Match logger initialization with static names
        (r'logger\s*=\s*logging\.getLogger\s*\(\s*["\'].*["\']\s*\)', 
         'logger = get_logger(__name__)'),
        # Match import from logging module when get_logger is used
        (r'import logging', ''),
        # Match from logging import ...
        (r'from\s+logging\s+import\s+.*', ''),
        # Ensure we have the correct import
        (r'^(?!from ibis.core.logging_config import get_logger)', 
         'from ibis.core.logging_config import get_logger\n')
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if file is the logging config itself
            if 'logging_config.py' in file_path:
                continue
            
            # Fix imports and logger initialization
            modified = content
            
            # Check if logger is used in the file
            if 'logger' in modified or 'logging' in modified:
                # Replace logger initialization
                modified = re.sub(r'logger\s*=\s*logging\.getLogger\s*\(\s*["\'].*["\']\s*\)', 
                                 'logger = get_logger(__name__)', modified)
                
                # Check if we need to add the correct import
                if 'from ibis.core.logging_config import get_logger' not in modified:
                    # Add import after any existing imports or at the beginning
                    if 'import' in modified:
                        # Find first import statement and add after it
                        lines = modified.split('\n')
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import') or line.strip().startswith('from'):
                                # Find the last import line
                                j = i
                                while j < len(lines) and (lines[j].strip().startswith('import') or 
                                                          lines[j].strip().startswith('from') or
                                                          lines[j].strip() == ''):
                                    j += 1
                                lines.insert(j, 'from ibis.core.logging_config import get_logger')
                                modified = '\n'.join(lines)
                    else:
                        modified = 'from ibis.core.logging_config import get_logger\n' + modified
                
                # Remove duplicate imports
                lines = modified.split('\n')
                seen = set()
                filtered_lines = []
                for line in lines:
                    if line.strip() and line.strip() not in seen:
                        if not line.strip().startswith('import logging') and \
                           not line.strip().startswith('from logging'):
                            seen.add(line.strip())
                            filtered_lines.append(line)
                    else:
                        filtered_lines.append(line)
                modified = '\n'.join(filtered_lines)
            
            # Only write if content changed
            if content != modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified)
                print(f"Fixed: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")


def main():
    fix_logger_initialization()
    print("\nLogger initialization fixes completed.")


if __name__ == "__main__":
    main()
