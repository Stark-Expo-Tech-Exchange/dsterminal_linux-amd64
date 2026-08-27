#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colorama Error Scanner - Check all Python files for potential OSError 22 issues
"""

import os
import re
import sys
import ast
import platform
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Set

class ColoramaErrorScanner:
    """Scan Python files for potential colorama-related errors"""

    # Patterns to check for
    PATTERNS = {
        'direct_colorama_import': r'(?:from\s+colorama\s+import|import\s+colorama)',
        'init_with_convert': r'init\s*\(\s*(?:[^)]*,\s*)?convert\s*=\s*True',
        'init_without_wrap': r'init\s*\(\s*(?:[^)]*,\s*)?wrap\s*=\s*True',
        'stdout_write_direct': r'sys\.stdout\.write\s*\(',
        'stdout_is_none': r'if\s+sys\.stdout\s+is\s+None',
        'oserror_22_handle': r'OSError.*errno\s*==\s*22',
        'safe_stdout_write': r'_safe_stdout_write',
        'colorama_ansitowin32': r'colorama\.ansitowin32',
    }

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.results: List[Dict] = []
        self.fixed_files: List[str] = []
        self.problem_files: List[Dict] = []

    def scan_file(self, filepath: Path) -> Dict:
        """Scan a single Python file for colorama issues"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {'file': str(filepath), 'error': str(e), 'issues': []}

        issues = []

        # Check for colorama import
        if re.search(self.PATTERNS['direct_colorama_import'], content, re.IGNORECASE):
            issues.append('colorama_import')

            # Check if init has convert=False
            if not re.search(r'init\s*\([^)]*convert\s*=\s*False', content, re.IGNORECASE):
                issues.append('colorama_convert_true_or_missing')

            # Check if init has wrap=False
            if not re.search(r'init\s*\([^)]*wrap\s*=\s*False', content, re.IGNORECASE):
                issues.append('colorama_wrap_true_or_missing')

        # Check if sys.stdout.write is used directly without safety
        if re.search(self.PATTERNS['stdout_write_direct'], content):
            if not re.search(self.PATTERNS['safe_stdout_write'], content):
                issues.append('direct_stdout_write_unsafe')

        # Check if OSError 22 is handled
        if not re.search(self.PATTERNS['oserror_22_handle'], content):
            if re.search(self.PATTERNS['stdout_write_direct'], content):
                issues.append('missing_oserror_22_handle')

        # Check if sys.stdout is checked for None
        if re.search(self.PATTERNS['stdout_is_none'], content):
            issues.append('has_stdout_none_check')
        else:
            if re.search(self.PATTERNS['stdout_write_direct'], content):
                issues.append('missing_stdout_none_check')

        return {
            'file': str(filepath),
            'issues': issues,
            'has_issues': len(issues) > 0
        }

    def scan_directory(self, directory: Path = None) -> List[Dict]:
        """Scan all Python files in a directory recursively"""
        if directory is None:
            directory = self.root_dir

        results = []
        python_files = list(directory.rglob('*.py'))

        # Also check for .py files in subdirectories
        for py_file in python_files:
            # Skip virtual environment and cache directories
            if any(part in py_file.parts for part in ['venv', 'env', '__pycache__', '.git']):
                continue

            result = self.scan_file(py_file)
            results.append(result)

            if result['has_issues']:
                self.problem_files.append(result)
            else:
                self.fixed_files.append(str(py_file))

        self.results = results
        return results

    def generate_report(self) -> str:
        """Generate a human-readable report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("COLORAMA ERROR SCAN REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Scan Directory: {self.root_dir}")
        report_lines.append(f"Total Python Files: {len(self.results)}")
        report_lines.append(f"Files with Issues: {len(self.problem_files)}")
        report_lines.append(f"Clean Files: {len(self.fixed_files)}")
        report_lines.append("=" * 80)
        report_lines.append("")

        if self.problem_files:
            report_lines.append("PROBLEM FILES:")
            report_lines.append("-" * 40)

            for result in self.problem_files:
                report_lines.append(f"\n📁 {result['file']}")
                for issue in result['issues']:
                    issue_desc = {
                        'colorama_import': '⚠️  Colorama imported without safety measures',
                        'colorama_convert_true_or_missing': '⚠️  init() missing convert=False',
                        'colorama_wrap_true_or_missing': '⚠️  init() missing wrap=False',
                        'direct_stdout_write_unsafe': '⚠️  Direct sys.stdout.write() without safety',
                        'missing_oserror_22_handle': '⚠️  No OSError 22 handler',
                        'has_stdout_none_check': '✅ Has sys.stdout None check',
                        'missing_stdout_none_check': '⚠️  Missing sys.stdout None check',
                    }
                    report_lines.append(f"   • {issue_desc.get(issue, issue)}")
        else:
            report_lines.append("✅ All files are clean! No issues found.")

        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("RECOMMENDED FIX FOR EACH FILE:")
        report_lines.append("=" * 80)
        report_lines.append("""
Add this at the top of each affected file:

# ============================================================
# FIX: Windows console encoding and colorama issues
# ============================================================
import sys
import os
import platform

if platform.system() == "Windows":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass

    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        elif hasattr(sys.stdout, 'buffer'):
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    except:
        pass

_original_stdout_write = sys.stdout.write if sys.stdout is not None else None

def _safe_stdout_write(text):
    try:
        if _original_stdout_write is not None:
            _original_stdout_write(text)
    except OSError as e:
        if e.errno == 22:
            try:
                clean = text.encode('ascii', 'ignore').decode('ascii')
                if _original_stdout_write is not None:
                    _original_stdout_write(clean)
            except:
                pass
        else:
            raise
    except UnicodeEncodeError:
        try:
            clean = text.encode('ascii', 'ignore').decode('ascii')
            if _original_stdout_write is not None:
                _original_stdout_write(clean)
        except:
            pass

if sys.stdout is not None:
    sys.stdout.write = _safe_stdout_write

# For colorama imports:
try:
    from colorama import init, Fore, Back, Style
    # IMPORTANT: Disable ANSI conversion on Windows
    init(autoreset=True, convert=False, strip=False, wrap=False)
except:
    # Fallback colors
    class Fore:
        RED = '\\033[91m'; GREEN = '\\033[92m'; YELLOW = '\\033[93m'
        BLUE = '\\033[94m'; MAGENTA = '\\033[95m'; CYAN = '\\033[96m'
        WHITE = '\\033[97m'; RESET = '\\033[0m'; DIM = '\\033[2m'

    class Back:
        RED = '\\033[101m'; GREEN = '\\033[102m'; YELLOW = '\\033[103m'
        BLUE = '\\033[104m'; RESET = '\\033[0m'

    class Style:
        BRIGHT = '\\033[1m'; DIM = '\\033[2m'; NORMAL = '\\033[22m'
        RESET_ALL = '\\033[0m'
""")

        return "\n".join(report_lines)

    def save_report(self, filename: str = "colorama_scan_report.txt"):
        """Save the report to a file"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {filename}")

    def print_summary(self):
        """Print a summary to the console"""
        print("\n" + "=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        print(f"Total Python Files: {len(self.results)}")
        print(f"Files with Issues: {len(self.problem_files)}")
        print(f"Clean Files: {len(self.fixed_files)}")
        print("=" * 80)

        if self.problem_files:
            print("\n⚠️  Files that need fixing:")
            for result in self.problem_files:
                print(f"\n  📁 {result['file']}")
                for issue in result['issues']:
                    issue_desc = {
                        'colorama_import': '    ⚠️  Colorama imported without safety measures',
                        'colorama_convert_true_or_missing': '    ⚠️  init() missing convert=False',
                        'colorama_wrap_true_or_missing': '    ⚠️  init() missing wrap=False',
                        'direct_stdout_write_unsafe': '    ⚠️  Direct sys.stdout.write() without safety',
                        'missing_oserror_22_handle': '    ⚠️  No OSError 22 handler',
                        'has_stdout_none_check': '    ✅ Has sys.stdout None check',
                        'missing_stdout_none_check': '    ⚠️  Missing sys.stdout None check',
                    }
                    print(issue_desc.get(issue, issue))
        else:
            print("\n✅ All files are clean!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Scan Python files for colorama OSError 22 issues")
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan')
    parser.add_argument('--report', '-r', default='colorama_scan_report.txt', help='Report output file')

    args = parser.parse_args()

    scanner = ColoramaErrorScanner(args.directory)
    scanner.scan_directory()
    scanner.save_report(args.report)
    scanner.print_summary()


if __name__ == "__main__":
    main()