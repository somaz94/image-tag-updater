# Troubleshooting Guide

<br/>

## Table of Contents
- [Common Issues](#common-issues)
- [Debugging](#debugging)
- [Error Messages](#error-messages)
- [Performance Issues](#performance-issues)

<br/>

## Common Issues

<br/>

### Push Failures

**Symptom:** Action fails when pushing changes to repository

**Possible Causes:**
1. Insufficient token permissions
2. Branch protection rules
3. Network issues

**Solutions:**

<details>
<summary>Check Token Permissions</summary>

Ensure your token has the following permissions:
- `repo` (full control)
- `workflow` (if updating workflow files)

```yaml
# Use a Personal Access Token with proper permissions
github_token: ${{ secrets.PAT }}
```

</details>

<details>
<summary>Handle Branch Protection</summary>

If branch protection is enabled:

```yaml
# Option 1: Use a different branch
- uses: somaz94/image-tag-updater@v1
  with:
    branch: automated-updates
    # ... other inputs

# Option 2: Create a PR instead (requires additional workflow)
```

</details>

<details>
<summary>Network Retry</summary>

The action includes automatic retry (3 attempts):
- Wait 5 seconds between retries
- Check GitHub status page for outages
- Enable debug mode to see retry attempts

</details>

<br/>

### File Not Found

**Symptom:** `File not found: charts/somaz/api/dev.values.yaml`

**Solutions:**

```yaml
# 1. Verify path is correct
- name: Debug Directory Structure
  run: |
    ls -la charts/somaz/api/
    find . -name "*.values.yaml"

# 2. Check repository checkout
- name: Checkout Repository
  uses: actions/checkout@v4
  with:
    repository: your-org/your-repo
    token: ${{ secrets.PAT }}

# 3. Use absolute paths
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: ${{ github.workspace }}/charts/somaz/api
```

<br/>

### Tag String Not Found

**Symptom:** `Tag string 'tag' not found in file`

**Cause:** The `tag_string` doesn't match the format in your YAML file

**Check Your YAML Format:**

```yaml
# ✅ Correct - will match default tag_string: "tag"
image:
  tag: "v1.0.0"

# ❌ Won't match - uses different key
image:
  version: "v1.0.0"

# Solution: Specify custom tag_string
- uses: somaz94/image-tag-updater@v1
  with:
    tag_string: "version"
```

**Indentation Issues:**

```yaml
# ✅ Correct spacing
image:
  tag: "v1.0.0"

# ❌ Wrong indentation
image:
    tag: "v1.0.0"  # Extra spaces
```

<br/>

### Invalid Tag Format

**Symptom:** `Invalid tag format: @invalid@tag`

**Tag Requirements:**
- Must start with alphanumeric character
- Can contain: letters, numbers, dots (`.`), underscores (`_`), hyphens (`-`)
- Cannot contain: `@`, `#`, `$`, spaces, special characters

**Valid Examples:**
```
✅ v1.0.0
✅ 2024.01.15
✅ main-abc123
✅ release_1.2.3
✅ v1.0.0-rc.1

❌ @invalid
❌ v1.0.0#beta
❌ tag with spaces
❌ $version
```

<br/>

### File Pattern Not Matching

**Symptom:** No files updated when using `file_pattern`

**Solutions:**

```yaml
# 1. Enable debug to see matched files
- uses: somaz94/image-tag-updater@v1
  with:
    file_pattern: "dev*.values.yaml"
    debug: "true"

# 2. Test pattern in shell
- name: Test Pattern
  run: |
    cd charts/somaz/api
    ls -la dev*.values.yaml

# 3. Use quotes for patterns
file_pattern: "dev*.values.yaml"  # ✅ Correct
file_pattern: dev*.values.yaml    # ❌ May fail in YAML
```

**Common Patterns:**
```yaml
# All dev files
file_pattern: "dev*.values.yaml"

# Multiple specific environments
file_pattern: "{dev,qa,staging}*.values.yaml"

# All values files
file_pattern: "*.values.yaml"
```

<br/>

## Debugging

<br/>

### Enable Debug Mode

```yaml
- name: Update with Debug
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "*.values.yaml"
    new_tag: v1.0.0
    debug: "true"
    github_token: ${{ secrets.PAT }}
```

**Debug Output Includes:**
- Directory contents
- Git configuration
- Branch operations
- File processing details
- Matched files
- Git push attempts

<br/>

### Dry Run Testing

Test without making changes:

```yaml
- name: Test Update (Dry Run)
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "prod*.values.yaml"
    new_tag: v2.0.0
    dry_run: "true"
    debug: "true"
    github_token: ${{ secrets.PAT }}
```

**Dry Run Shows:**
- Current tag values
- What would change
- No actual modifications
- No commits or pushes

<br/>

### Manual Verification

```yaml
- name: Update Images
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "*.values.yaml"
    new_tag: v1.0.0
    github_token: ${{ secrets.PAT }}

- name: Verify Changes
  run: |
    echo "=== Git Log ==="
    git log -1 --stat
    
    echo "=== File Changes ==="
    git diff HEAD~1 HEAD
    
    echo "=== Updated Files ==="
    grep -r "tag:" charts/somaz/api/*.values.yaml
```

<br/>

## Error Messages

<br/>

### "Required environment variable X is not set"

**Cause:** Missing required input parameter

**Solution:**

```yaml
# Check all required inputs
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api    # ✅ Required
    new_tag: v1.0.0                  # ✅ Required
    tag_string: tag                  # ✅ Required
    github_token: ${{ secrets.PAT }} # ✅ Required
    repo: somaz94/image-tag-updater  # ✅ Required
    branch: main                     # ✅ Required
    
    # One of these is required:
    target_values_file: dev.values.yaml  # Option 1
    # OR
    file_pattern: "dev*.values.yaml"     # Option 2
```

<br/>

### "Failed to write after 3 retries"

**Cause:** Persistent file or Git operation failures

**Solutions:**

1. **Check file permissions:**
```yaml
- name: Check Permissions
  run: ls -la charts/somaz/api/
```

2. **Check disk space:**
```yaml
- name: Check Disk Space
  run: df -h
```

3. **Verify Git configuration:**
```yaml
- name: Verify Git
  run: |
    git config --list
    git status
```

<br/>

### "No changes to commit"

**Symptom:** Warning message "No changes to commit. Nothing to push."

**This is normal when:**
- Tag is already at target value
- Files already updated in previous run

**To verify:**
```yaml
- name: Check Current Tags
  run: |
    grep -r "tag:" charts/somaz/api/*.values.yaml
```

<br/>

## Performance Issues

<br/>

### Slow Execution

**Possible Causes:**
1. Large repository
2. Many files to update
3. Network latency

**Optimization:**

```yaml
# 1. Shallow clone
- name: Checkout
  uses: actions/checkout@v4
  with:
    fetch-depth: 1  # Shallow clone

# 2. Update only necessary files
- uses: somaz94/image-tag-updater@v1
  with:
    file_pattern: "prod.values.yaml"  # Specific file
    # Instead of: file_pattern: "*.values.yaml"
```

<br/>

### Multiple Concurrent Updates

**Issue:** Multiple workflows updating same repository

**Solution:** Use concurrency control

```yaml
concurrency:
  group: image-update-${{ github.ref }}
  cancel-in-progress: false  # Wait for previous to complete

jobs:
  update-images:
    runs-on: ubuntu-latest
    steps:
      - uses: somaz94/image-tag-updater@v1
        # ... your configuration
```

<br/>

## Getting Help

If you're still experiencing issues:

1. **Enable Debug Mode:**
   ```yaml
   debug: "true"
   ```

2. **Create an Issue:**
   - Include debug output (remove sensitive data)
   - Describe expected vs actual behavior
   - Include workflow file snippet
   - Mention action version

3. **Check Existing Issues:**
   - [GitHub Issues](https://github.com/somaz94/image-tag-updater/issues)
   - Search for similar problems

4. **Minimal Reproduction:**
   ```yaml
   # Simplest possible workflow that shows the issue
   - uses: somaz94/image-tag-updater@v1
     with:
       target_path: charts/somaz/api
       target_values_file: dev.values.yaml
       new_tag: v1.0.0
       debug: "true"
       github_token: ${{ secrets.PAT }}
   ```

<br/>

## Best Practices to Avoid Issues

1. ✅ Always test with `dry_run: "true"` first
2. ✅ Use `debug: "true"` when troubleshooting
3. ✅ Verify file paths before running
4. ✅ Use specific file patterns when possible
5. ✅ Keep tokens in secrets, never hardcode
6. ✅ Use semantic versioning for tags
7. ✅ Monitor action execution logs
8. ✅ Keep action version up to date
