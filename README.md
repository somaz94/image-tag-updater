# Image Tag Updater GitHub Action

[![License](https://img.shields.io/github/license/somaz94/image-tag-updater)](https://github.com/somaz94/image-tag-updater)
![Latest Tag](https://img.shields.io/github/v/tag/somaz94/image-tag-updater)
![Top Language](https://img.shields.io/github/languages/top/somaz94/image-tag-updater?color=green&logo=python&logoColor=blue)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Image%20Tag%20Updater-blue?logo=github)](https://github.com/marketplace/actions/image-tag-updater)
![CI](https://github.com/somaz94/image-tag-updater/actions/workflows/ci.yml/badge.svg)

<br/>

## Description

The **Image Tag Updater** GitHub Action automates image tag updates in configuration files, making GitOps workflows seamless and efficient. Perfect for Kubernetes Helm values files and infrastructure-as-code repositories.

**Key Features:**
- Automated image tag updates in YAML configuration files
- Support for single file or multiple files via patterns
- Dry run mode for safe testing
- Optional backup creation before updates
- Debug mode for troubleshooting
- Secure GitHub token authentication
- Fast Python-based execution

<br/>

## Documentation

### Comprehensive Guides:
- [Advanced Usage Guide](docs/ADVANCED_USAGE.md) - Matrix strategies, multi-environment deployments, integration patterns
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues, debugging tips, performance optimization

<br/>

## Quick Start

```yaml
- name: Update Image Tag
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    target_values_file: production.values.yaml
    new_tag: v1.0.1
    github_token: ${{ secrets.PAT }}
```

<br/>

## Inputs

| Input                | Required | Description                                                                   | Default                |
| -------------------- | -------- | ----------------------------------------------------------------------------- | ---------------------- |
| `target_path`        | Yes      | The directory path where the values file is located                           | N/A                    |
| `tag_string`         | No       | The tag string to match for updating the image tag                            | `"tag"`                |
| `new_tag`            | Yes      | The new image tag to replace the current one (e.g., `v1.0.1`)                 | N/A                    |
| `target_values_file` | No       | The prefix name of the values file to update                                  | N/A                    |
| `github_token`       | Yes      | A GitHub token for authenticating the push to the repository                  | N/A                    |
| `commit_message`     | No       | The commit message for the update                                             | `"Update image tag in"`|
| `branch`             | No       | The branch where changes should be committed                                  | `"main"`               |
| `git_user_name`      | No       | The Git username for commits                                                  | `"GitHub Action"`      |
| `git_user_email`     | No       | The Git email for commits                                                     | `"actions@github.com"` |
| `backup`             | No       | Specifies whether to create a backup file (true/false)                        | `"false"`              |
| `repo`               | Yes      | Git repository for commits (Repo to update)                                   | N/A                    |
| `file_pattern`       | No       | File pattern to match multiple files (e.g., "*.values.yaml")                  | `""`                   |
| `dry_run`            | No       | Run in dry-run mode without making actual changes                             | `"false"`              |
| `debug`              | No       | Enable detailed debug logging                                                 | `"false"`              |
| `tag_prefix`         | No       | Prefix to add to the new tag (e.g., "v", "release-")                          | `""`                   |
| `tag_suffix`         | No       | Suffix to add to the new tag (e.g., "-prod", "-staging")                      | `""`                   |
| `update_if_contains` | No       | Only update if current tag contains this string (e.g., "v1.", "dev")          | `""`                   |
| `skip_if_contains`   | No       | Skip update if current tag contains this string (e.g., "latest", "prod")      | `""`                   |
| `summary_file`       | No       | Path to save change summary JSON file (e.g., ".github/image-updates.json")    | `""`                   |

<br/>

## Outputs

| Output            | Description                                                             |
| ----------------- | ----------------------------------------------------------------------- |
| `files_updated`   | Number of files that were updated                                       |
| `updated_files`   | Comma-separated list of file paths that were updated                    |
| `old_tags`        | Comma-separated list of previous tag values                             |
| `new_tag_applied` | The final tag value that was applied (including prefix/suffix)          |
| `changes_made`    | Boolean indicating whether any changes were made (`true` or `false`)    |
| `commit_sha`      | SHA of the created commit (empty if dry run or no changes)              |
| `commit_sha_short`| Short SHA (7 chars) of the created commit (empty if dry run or no changes) |

<br/>

## Advanced Features

### Conditional Updates
Control which tags get updated based on their current values:

**Update only specific versions:**
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "*.values.yaml"
    new_tag: v2.0.0
    update_if_contains: "v1."    # Only update v1.x tags
    github_token: ${{ secrets.PAT }}
```

**Skip certain tags:**
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "*.values.yaml"
    new_tag: v1.5.0
    skip_if_contains: "latest"   # Don't update 'latest' tags
    github_token: ${{ secrets.PAT }}
```

**Combined conditions:**
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    file_pattern: "prod*.values.yaml"
    new_tag: v2.0.0
    update_if_contains: "v1."    # Only update v1.x versions
    skip_if_contains: "prod"     # But skip production tags
    github_token: ${{ secrets.PAT }}
```

<br/>

### Change Summary Tracking
Automatically track all image tag updates in a JSON file:

```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "*.values.yaml"
    new_tag: v1.2.3
    summary_file: ".github/image-updates.json"
    github_token: ${{ secrets.PAT }}
```

**Summary file format:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "repository": "company/infrastructure",
    "branch": "main",
    "commit_sha": "abc123def456",
    "target_path": "charts/somaz/api",
    "changes_count": 3,
    "changes": [
      {
        "file": "dev1.values.yaml",
        "old_tag": "v1.0.0",
        "new_tag": "v1.2.3",
        "tag_string": "tag"
      },
      {
        "file": "dev2.values.yaml",
        "old_tag": "v1.0.1",
        "new_tag": "v1.2.3",
        "tag_string": "tag"
      }
    ],
    "dry_run": false
  }
]
```

**Use cases:**
- 📊 Audit trail for compliance
- 🔄 Rollback reference
- 📈 Deployment history tracking
- 🔍 Troubleshooting deployments

<br/>

### Tag Prefix and Suffix
Add prefixes and suffixes to your tags for flexible versioning:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    target_values_file: production.values.yaml
    new_tag: "1.2.3"
    tag_prefix: "v"          # Results in: v1.2.3
    tag_suffix: "-prod"      # Results in: 1.2.3-prod
    github_token: ${{ secrets.PAT }}
```

Combined prefix and suffix:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    new_tag: "1.2.3"
    tag_prefix: "release-"   # Results in: release-1.2.3-staging
    tag_suffix: "-staging"
```

<br/>

### Using Outputs
Access action outputs in subsequent steps:
```yaml
- name: Update Image Tag
  id: update
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "*.values.yaml"
    new_tag: v1.0.1
    github_token: ${{ secrets.PAT }}

- name: Use Outputs
  run: |
    echo "Updated ${{ steps.update.outputs.files_updated }} files"
    echo "Files: ${{ steps.update.outputs.updated_files }}"
    echo "Applied tag: ${{ steps.update.outputs.new_tag_applied }}"
    echo "Commit: ${{ steps.update.outputs.commit_sha_short }}"

- name: Notify on Success
  if: steps.update.outputs.changes_made == 'true'
  run: |
    echo "Image tags updated successfully!"
    echo "Old tags: ${{ steps.update.outputs.old_tags }}"
    echo "New tag: ${{ steps.update.outputs.new_tag_applied }}"
    echo "Commit: ${{ steps.update.outputs.commit_sha_short }}"
```

<br/>

### Multiple File Updates
You can update multiple files at once using the `file_pattern` input:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "dev*.values.yaml"  # Updates all dev environment files
    new_tag: v1.0.1
```

<br/>

## Example Workflows

### Basic Usage

**Update single file:**
```yaml
- name: Update Production Tag
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    target_values_file: production.values.yaml
    new_tag: v1.0.1
    github_token: ${{ secrets.PAT }}
```

**Update multiple files with pattern:**
```yaml
- name: Update All Dev Environments
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "dev*.values.yaml"
    new_tag: dev-${{ github.sha }}
    github_token: ${{ secrets.PAT }}
```

<br/>

### Advanced Features

**Dry Run Mode** - Test changes without applying:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "prod*.values.yaml"
    new_tag: v2.0.0
    dry_run: "true"
    github_token: ${{ secrets.PAT }}
```

**Debug Mode** - Enable detailed logging:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "*.values.yaml"
    new_tag: v1.0.1
    debug: "true"
    github_token: ${{ secrets.PAT }}
```

**With Backup** - Create backup before changes:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    target_values_file: production.values.yaml
    new_tag: v2.0.0
    backup: "true"
    github_token: ${{ secrets.PAT }}
```

📖 **[View Advanced Usage Guide →](docs/ADVANCED_USAGE.md)**

<br/>

## Complete Workflow Example

This example demonstrates using the action with common patterns:

```yaml
name: Update Infrastructure

on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  update-images:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Infrastructure Repo
        uses: actions/checkout@v4
        with:
          repository: company/infrastructure
          token: ${{ secrets.PAT }}

      - name: Set Image Tag
        id: vars
        run: echo "tag=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT

      - name: Test Update (Dry Run)
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/myapp
          file_pattern: "dev*.values.yaml"
          new_tag: ${{ steps.vars.outputs.tag }}
          dry_run: "true"
          debug: "true"
          github_token: ${{ secrets.PAT }}

      - name: Apply Update
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/myapp
          file_pattern: "dev*.values.yaml"
          new_tag: ${{ steps.vars.outputs.tag }}
          branch: main
          github_token: ${{ secrets.PAT }}
          git_user_name: GitHub Actions
          git_user_email: actions@github.com
          repo: company/infrastructure
          commit_message: "chore: Update dev image to"
```

<br/>

## Troubleshooting

### Common Issues:

<details>
<summary>Push fails with permission error?</summary>

1. Verify token has `repo` permissions
2. Check branch protection rules
3. Ensure target branch exists
4. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#push-failures)

</details>

<details>
<summary>File not found error?</summary>

1. Verify path: `ls -la charts/somaz/api/`
2. Check repository checkout
3. Use absolute paths if needed
4. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#file-not-found)

</details>

<details>
<summary>Tag string not found in file?</summary>

1. Check YAML format and indentation
2. Verify `tag_string` matches your YAML key
3. Enable debug mode to see details
4. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#tag-string-not-found)

</details>

<details>
<summary>Invalid tag format error?</summary>

Tags must:
- Start with alphanumeric character
- Contain only: `a-z`, `A-Z`, `0-9`, `.`, `_`, `-`

Valid examples: `v1.0.0`, `2024.01.15`, `main-abc123`

</details>

[→ See full troubleshooting guide](docs/TROUBLESHOOTING.md)

<br/>

## Notes

- **GitHub Token**: Ensure your token has `repo` write permissions
- **File Selection**: Use either `file_pattern` or `target_values_file` (not both)
- **Backup Files**: When enabled, creates `.bak` files before modifications
- **Security**: The action validates all inputs and handles errors safely

For detailed information, see:
- 📖 [Advanced Usage Guide](docs/ADVANCED_USAGE.md) - Matrix strategies, integrations, rollback procedures
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues, debugging, performance tips

<br/>

## Security Best Practices

- Use repository-scoped tokens with minimum required permissions (`repo` scope)
- Enable branch protection rules on target branches
- Regularly rotate GitHub tokens and update secrets
- Use dry run mode to validate changes before applying
- Monitor GitHub audit logs for action usage
- Keep commit messages descriptive for audit trails

<br/>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

<br/>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.