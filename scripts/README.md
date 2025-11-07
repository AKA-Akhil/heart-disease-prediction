# Scripts Directory

This directory contains utility scripts for the heart-disease-prediction project.

## Available Scripts

### 1. find_openai_apis.py

A comprehensive security scanner that detects OpenAI API keys, imports, and usage in the repository.

#### Features:
- 🔍 Scans for OpenAI API keys (sk-* pattern)
- 📦 Detects OpenAI library imports
- 🔧 Finds environment variable references
- 🔐 Identifies OpenAI client usage
- 📜 Searches git history for leaked keys
- 📊 Exports findings to JSON

#### Usage:

```bash
# Basic scan of current directory
python scripts/find_openai_apis.py

# Scan with git history check
python scripts/find_openai_apis.py --check-git-history

# Scan specific directory
python scripts/find_openai_apis.py --path /path/to/directory

# Export findings to JSON
python scripts/find_openai_apis.py --json findings.json

# Combine all options
python scripts/find_openai_apis.py --check-git-history --json findings.json
```

#### What It Detects:

1. **API Keys:**
   - OpenAI API keys (sk-...)
   - Organization keys (org-...)

2. **Code Patterns:**
   - `import openai` or `from openai import ...`
   - `OpenAI()` client initialization
   - Environment variables: `OPENAI_API_KEY`, `OPENAI_ORG`, `OPENAI_API_BASE`

3. **Model References:**
   - GPT-3.5-turbo
   - GPT-4
   - text-davinci
   - text-curie

4. **Git History:**
   - Searches all commits for OpenAI-related patterns

#### Exit Codes:
- `0` - No API keys found (success)
- `1` - API keys detected (failure)

#### Example Output:

```
================================================================================
OpenAI API Detection Report
================================================================================
Scan Location: /path/to/repo

✓ No API keys found

✓ No OpenAI imports found

✓ No OpenAI environment variables found

✓ No OpenAI usage detected

✓ No OpenAI references in git history

================================================================================
Summary
================================================================================
Total Findings: 0
  - API Keys: 0
  - Imports: 0
  - Environment Variables: 0
  - Usage: 0
  - Git History: 0

✓ Repository appears clean of OpenAI API keys
================================================================================
```

#### Integration with CI/CD:

Add to your GitHub Actions workflow:

```yaml
- name: Scan for OpenAI API keys
  run: |
    python scripts/find_openai_apis.py --check-git-history
  continue-on-error: false  # Fail the build if keys are found
```

#### Security Best Practices:

If the scanner finds API keys:
1. **Immediately remove** the keys from the code
2. **Revoke** the keys at https://platform.openai.com/api-keys
3. **Use environment variables** or secret management services
4. **Update `.gitignore`** to prevent future commits
5. **Use git history rewriting** tools if keys were committed:
   ```bash
   # WARNING: This rewrites git history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```

## Adding New Scripts

When adding new scripts to this directory:
1. Make them executable: `chmod +x script_name.py`
2. Add a shebang line: `#!/usr/bin/env python3`
3. Include comprehensive docstrings
4. Add command-line argument support
5. Update this README with usage instructions

## Dependencies

Scripts in this directory should use only standard library modules when possible, or dependencies already listed in the project's `requirements.txt`.

Current scripts dependencies:
- `find_openai_apis.py`: Uses only Python standard library (no external dependencies)
