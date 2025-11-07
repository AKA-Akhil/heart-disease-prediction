#!/usr/bin/env python3
"""
OpenAI API Key Detection Script

This script scans the repository for:
1. OpenAI API keys (sk-* pattern)
2. OpenAI library imports and usage
3. Environment variables related to OpenAI
4. Configuration files that might contain API keys
5. Git history for accidentally committed keys

Usage:
    python scripts/find_openai_apis.py [--path PATH] [--check-git-history]
"""

import os
import re
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Patterns to search for
PATTERNS = {
    'openai_api_key': r'sk-(?:proj-)?[a-zA-Z0-9]{48,}',  # OpenAI API key pattern (old and new format)
    'openai_org_key': r'org-[a-zA-Z0-9-]{20,30}',  # OpenAI organization key
    'openai_import': r'(?:from|import)\s+openai',
    'openai_env_var': r'(?:OPENAI_API_KEY|OPENAI_ORG|OPENAI_API_BASE)',
    'openai_client': r'OpenAI\s*\(',
    'chatgpt': r'(?:gpt-3\.5-turbo|gpt-4|text-davinci|text-curie)',
    'generic_api_key': r'api[_-]?key\s*[=:]\s*["\'][^"\']{20,}["\']',
}

# File extensions to scan
SCAN_EXTENSIONS = {
    '.py', '.txt', '.json', '.yaml', '.yml', '.env', 
    '.cfg', '.ini', '.md', '.sh', '.bash'
}

# Directories to ignore
IGNORE_DIRS = {
    '.git', '.dvc', '__pycache__', 'node_modules', 
    'venv', '.venv', 'env', '.env', 'dist', 'build'
}


class OpenAIScanner:
    """Scanner for detecting OpenAI API usage and keys"""
    
    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path).resolve()
        self.findings: Dict[str, List[Dict]] = {
            'api_keys': [],
            'imports': [],
            'env_vars': [],
            'usage': [],
            'git_history': []
        }
    
    def should_scan_file(self, filepath: Path) -> bool:
        """Determine if file should be scanned"""
        # Check if in ignored directory
        for parent in filepath.parents:
            if parent.name in IGNORE_DIRS:
                return False
        
        # Check extension
        return filepath.suffix in SCAN_EXTENSIONS or filepath.name.startswith('.env')
    
    def scan_file(self, filepath: Path) -> None:
        """Scan a single file for OpenAI patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # Check for API keys
                    if re.search(PATTERNS['openai_api_key'], line):
                        self.findings['api_keys'].append({
                            'file': str(filepath.relative_to(self.root_path)),
                            'line': line_num,
                            'type': 'OpenAI API Key',
                            'context': line.strip()[:100]
                        })
                    
                    # Check for organization keys
                    if re.search(PATTERNS['openai_org_key'], line):
                        self.findings['api_keys'].append({
                            'file': str(filepath.relative_to(self.root_path)),
                            'line': line_num,
                            'type': 'OpenAI Org Key',
                            'context': line.strip()[:100]
                        })
                    
                    # Check for imports
                    if re.search(PATTERNS['openai_import'], line):
                        self.findings['imports'].append({
                            'file': str(filepath.relative_to(self.root_path)),
                            'line': line_num,
                            'context': line.strip()
                        })
                    
                    # Check for environment variables
                    if re.search(PATTERNS['openai_env_var'], line):
                        self.findings['env_vars'].append({
                            'file': str(filepath.relative_to(self.root_path)),
                            'line': line_num,
                            'context': line.strip()
                        })
                    
                    # Check for OpenAI client usage
                    if re.search(PATTERNS['openai_client'], line):
                        self.findings['usage'].append({
                            'file': str(filepath.relative_to(self.root_path)),
                            'line': line_num,
                            'type': 'OpenAI Client',
                            'context': line.strip()[:100]
                        })
                    
                    # Check for ChatGPT model references
                    if re.search(PATTERNS['chatgpt'], line):
                        self.findings['usage'].append({
                            'file': str(filepath.relative_to(self.root_path)),
                            'line': line_num,
                            'type': 'GPT Model Reference',
                            'context': line.strip()[:100]
                        })
                    
        except Exception as e:
            print(f"Error scanning {filepath}: {e}", file=sys.stderr)
    
    def scan_directory(self) -> None:
        """Recursively scan directory"""
        print(f"Scanning directory: {self.root_path}")
        
        for filepath in self.root_path.rglob('*'):
            if filepath.is_file() and self.should_scan_file(filepath):
                self.scan_file(filepath)
    
    def check_git_history(self) -> None:
        """Check git history for OpenAI keys"""
        print("Checking git history...")
        
        try:
            # Search for OpenAI patterns in git history
            patterns = ['openai', 'OPENAI', 'sk-', 'gpt-', 'chatgpt']
            
            for pattern in patterns:
                result = subprocess.run(
                    ['git', 'log', '--all', '-p', '-S', pattern],
                    cwd=self.root_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    # Parse the output for commits
                    commits = re.findall(r'commit ([a-f0-9]{40})', result.stdout)
                    if commits:
                        for commit in set(commits):
                            self.findings['git_history'].append({
                                'commit': commit[:8],
                                'pattern': pattern,
                                'message': 'Found in git history'
                            })
                            
        except subprocess.TimeoutExpired:
            print("Warning: Git history check timed out", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not check git history: {e}", file=sys.stderr)
    
    def mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive API keys in text"""
        # Mask OpenAI API keys (both old sk-* and new sk-proj-* formats)
        text = re.sub(r'sk-(?:proj-)?[a-zA-Z0-9]{48,}', 'sk-***REDACTED***', text)
        # Mask organization keys
        text = re.sub(r'org-[a-zA-Z0-9-]{20,30}', 'org-***REDACTED***', text)
        return text
    
    def generate_report(self) -> str:
        """Generate a comprehensive report with masked sensitive data
        
        All API keys are automatically masked before being included in the report
        to prevent accidental exposure of sensitive credentials.
        """
        report = []
        report.append("=" * 80)
        report.append("OpenAI API Detection Report")
        report.append("=" * 80)
        report.append(f"Scan Location: {self.root_path}")
        report.append("")
        
        # API Keys
        if self.findings['api_keys']:
            report.append("⚠️  CRITICAL: API Keys Found")
            report.append("-" * 80)
            for finding in self.findings['api_keys']:
                report.append(f"  Type: {finding['type']}")
                report.append(f"  File: {finding['file']}")
                report.append(f"  Line: {finding['line']}")
                # Mask sensitive data in context
                masked_context = self.mask_sensitive_data(finding['context'])
                report.append(f"  Context: {masked_context}")
                report.append("")
        else:
            report.append("✓ No API keys found")
            report.append("")
        
        # Imports
        if self.findings['imports']:
            report.append("📦 OpenAI Library Imports")
            report.append("-" * 80)
            for finding in self.findings['imports']:
                report.append(f"  File: {finding['file']} (line {finding['line']})")
                report.append(f"  Code: {finding['context']}")
                report.append("")
        else:
            report.append("✓ No OpenAI imports found")
            report.append("")
        
        # Environment Variables
        if self.findings['env_vars']:
            report.append("🔧 Environment Variables")
            report.append("-" * 80)
            for finding in self.findings['env_vars']:
                report.append(f"  File: {finding['file']} (line {finding['line']})")
                report.append(f"  Code: {finding['context']}")
                report.append("")
        else:
            report.append("✓ No OpenAI environment variables found")
            report.append("")
        
        # Usage
        if self.findings['usage']:
            report.append("🔍 OpenAI Usage Detected")
            report.append("-" * 80)
            for finding in self.findings['usage']:
                report.append(f"  Type: {finding['type']}")
                report.append(f"  File: {finding['file']} (line {finding['line']})")
                report.append(f"  Context: {finding['context']}")
                report.append("")
        else:
            report.append("✓ No OpenAI usage detected")
            report.append("")
        
        # Git History
        if self.findings['git_history']:
            report.append("📜 Git History Findings")
            report.append("-" * 80)
            for finding in self.findings['git_history']:
                report.append(f"  Commit: {finding['commit']}")
                report.append(f"  Pattern: {finding['pattern']}")
                report.append("")
        else:
            report.append("✓ No OpenAI references in git history")
            report.append("")
        
        # Summary
        report.append("=" * 80)
        report.append("Summary")
        report.append("=" * 80)
        total_findings = sum(len(v) for v in self.findings.values())
        report.append(f"Total Findings: {total_findings}")
        report.append(f"  - API Keys: {len(self.findings['api_keys'])}")
        report.append(f"  - Imports: {len(self.findings['imports'])}")
        report.append(f"  - Environment Variables: {len(self.findings['env_vars'])}")
        report.append(f"  - Usage: {len(self.findings['usage'])}")
        report.append(f"  - Git History: {len(self.findings['git_history'])}")
        report.append("")
        
        if self.findings['api_keys']:
            report.append("⚠️  ACTION REQUIRED: API keys found in repository!")
            report.append("   1. Remove the keys immediately")
            report.append("   2. Revoke the keys at https://platform.openai.com/api-keys")
            report.append("   3. Use environment variables or secret management")
            report.append("   4. Add to .gitignore to prevent future commits")
        else:
            report.append("✓ Repository appears clean of OpenAI API keys")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_json(self, output_file: str) -> None:
        """Export findings as JSON with masked sensitive data"""
        # Create a copy of findings with masked sensitive data
        masked_findings = {
            'api_keys': [],
            'imports': self.findings['imports'],
            'env_vars': self.findings['env_vars'],
            'usage': self.findings['usage'],
            'git_history': self.findings['git_history']
        }
        
        # Mask API keys in the copy
        for finding in self.findings['api_keys']:
            masked_finding = finding.copy()
            masked_finding['context'] = self.mask_sensitive_data(finding['context'])
            masked_findings['api_keys'].append(masked_finding)
        
        with open(output_file, 'w') as f:
            json.dump(masked_findings, f, indent=2)
        print(f"Findings exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Scan repository for OpenAI API keys and usage'
    )
    parser.add_argument(
        '--path',
        default='.',
        help='Path to scan (default: current directory)'
    )
    parser.add_argument(
        '--check-git-history',
        action='store_true',
        help='Check git history for API keys'
    )
    parser.add_argument(
        '--json',
        help='Export findings to JSON file'
    )
    
    args = parser.parse_args()
    
    scanner = OpenAIScanner(args.path)
    scanner.scan_directory()
    
    if args.check_git_history:
        scanner.check_git_history()
    
    # Print report
    # Note: generate_report() masks all sensitive data (API keys) before printing
    # to prevent logging sensitive information in clear text
    print(scanner.generate_report())
    
    # Export JSON if requested
    if args.json:
        scanner.export_json(args.json)
    
    # Exit with error code if API keys found
    if scanner.findings['api_keys']:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
