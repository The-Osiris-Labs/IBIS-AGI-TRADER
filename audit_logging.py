#!/usr/bin/env python3
"""
Comprehensive audit script for IBIS project logging system.
"""

import os
import re
from typing import List, Dict, Tuple


def find_python_files(root_dir: str) -> List[str]:
    """Find all Python files in ibis, examples, and tests directories."""
    python_files = []
    for dir_name in ['ibis', 'examples', 'tests']:
        dir_path = os.path.join(root_dir, dir_name)
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
    return python_files


def audit_file(file_path: str) -> List[Dict]:
    """Audit a single Python file for logging issues."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
    except Exception as e:
        issues.append({
            'line': 0,
            'type': 'ERROR',
            'message': f"Could not read file: {e}"
        })
        return issues
    
    # 1. Check logger import
    has_correct_import = False
    has_standard_logging_import = False
    
    import_matches = re.findall(r'from\s+([^\s]+)\s+import\s+([^\n]+)', content)
    for module, imports in import_matches:
        if module == 'ibis.core.logging_config' and 'get_logger' in imports:
            has_correct_import = True
        elif module == 'logging' and 'getLogger' in imports:
            has_standard_logging_import = True
    
    if 'import logging' in content:
        has_standard_logging_import = True
    
    if not has_correct_import and not has_standard_logging_import:
        # Check if logger is used at all
        if 'logger' in content or 'logging' in content:
            issues.append({
                'line': 0,
                'type': 'WARNING',
                'message': "Logger imported from unknown source"
            })
    elif has_standard_logging_import and 'get_logger' in content:
        issues.append({
            'line': 0,
            'type': 'ERROR',
            'message': "Using get_logger but importing from standard logging module"
        })
    
    # 2. Check logger initialization
    logger_initialization = []
    for i, line in enumerate(lines):
        if 'get_logger' in line or 'getLogger' in line:
            logger_initialization.append((i + 1, line.strip()))
    
    if logger_initialization:
        for line_num, line in logger_initialization:
            if '__name__' not in line:
                issues.append({
                    'line': line_num,
                    'type': 'WARNING',
                    'message': f"Logger initialized with static name instead of __name__: {line}"
                })
    else:
        # Check if logger is used
        if 'logger' in content or 'logging' in content:
            issues.append({
                'line': 0,
                'type': 'WARNING',
                'message': "Logger usage detected but no initialization found"
            })
    
    # 3. Check for print statements
    for i, line in enumerate(lines):
        if 'print(' in line and not re.match(r'^\s*#', line):
            issues.append({
                'line': i + 1,
                'type': 'WARNING',
                'message': f"Print statement found: {line.strip()}"
            })
    
    # 4. Check exception handling
    for i, line in enumerate(lines):
        if 'except' in line and not re.match(r'^\s*#', line):
            # Look for logging in exception blocks
            j = i + 1
            while j < len(lines):
                line_j = lines[j]
                if re.match(r'^\s*(def|class|if|for|while|try|except)', line_j):
                    break
                if 'logger' in line_j or 'logging' in line_j:
                    if 'exc_info=True' not in line_j and 'exc_info=1' not in line_j:
                        issues.append({
                            'line': j + 1,
                            'type': 'WARNING',
                            'message': f"Exception logging without exc_info=True: {line_j.strip()}"
                        })
                    break
                j += 1
    
    # 5. Check for module-level handler configuration
    handler_patterns = [
        r'logging\.(StreamHandler|FileHandler|RotatingFileHandler|TimedRotatingFileHandler|Handler)',
        r'logger\.addHandler',
        r'logging\.basicConfig'
    ]
    
    for pattern in handler_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Check if it's in a comment
            line_num = content[:match.start()].count('\n') + 1
            line = lines[line_num - 1]
            if not re.match(r'^\s*#', line):
                issues.append({
                    'line': line_num,
                    'type': 'ERROR',
                    'message': f"Module-level logging handler configuration found: {match.group()}"
                })
    
    return issues


def main():
    root_dir = "/root/projects/Dont enter unless solicited/AGI Trader"
    python_files = find_python_files(root_dir)
    
    all_issues = []
    
    for file_path in python_files:
        issues = audit_file(file_path)
        if issues:
            all_issues.append({
                'file': file_path,
                'issues': issues
            })
    
    # Generate report
    print(f"IBIS Project Logging Audit Report")
    print(f"{'='*80}")
    print(f"Total files audited: {len(python_files)}")
    print(f"Files with issues: {len(all_issues)}")
    print(f"{'='*80}\n")
    
    for item in all_issues:
        print(f"\033[1;34m{item['file']}\033[0m")
        for issue in item['issues']:
            line_str = f":{issue['line']}" if issue['line'] > 0 else ""
            if issue['type'] == 'ERROR':
                print(f"  \033[1;31mERROR{line_str}: {issue['message']}\033[0m")
            elif issue['type'] == 'WARNING':
                print(f"  \033[1;33mWARNING{line_str}: {issue['message']}\033[0m")
        print()
    
    # Summary by issue type
    print(f"{'='*80}")
    print(f"Issue Summary:")
    error_count = 0
    warning_count = 0
    for item in all_issues:
        for issue in item['issues']:
            if issue['type'] == 'ERROR':
                error_count += 1
            elif issue['type'] == 'WARNING':
                warning_count += 1
    
    print(f"  Errors:   {error_count}")
    print(f"  Warnings: {warning_count}")
    print(f"  Total:    {error_count + warning_count}")


if __name__ == "__main__":
    main()
