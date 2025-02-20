# Image Tag Updater GitHub Action

[![License](https://img.shields.io/github/license/somaz94/image-tag-updater)](https://github.com/somaz94/container-action)
![Latest Tag](https://img.shields.io/github/v/tag/somaz94/image-tag-updater)
![Top Language](https://img.shields.io/github/languages/top/somaz94/image-tag-updater?color=green&logo=shell&logoColor=b)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Image%20Tag%20Updater-blue?logo=github)](https://github.com/marketplace/actions/image-tag-updater)

## Description

The **Image Tag Updater** GitHub Action is designed to update image tags in a
specified file within a repository. It's particularly useful in GitOps
workflows, where configuration changes need to be automatically reflected across
multiple repositories.

<br/>

This action allows users to update specific lines in configuration files,
typically to update image tags, and commits the changes directly to the
repository. It supports checking out multiple repositories, making it ideal for
updating infrastructure repositories based on changes in source code
repositories.

<br/>

## Features

- 🔄 Automated image tag updates in configuration files
- 🔒 Secure authentication with GitHub tokens
- 💾 Optional backup creation
- 🎯 Precise targeting of specific values in YAML files
- 📝 Customizable commit messages and Git credentials
- 🔍 Detailed execution logs
- ⚡ Support for multiple repositories and branches

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

<br/>

## Advanced Features

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

### Dry Run Mode
Test your changes without actually applying them:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    dry_run: "true"
    file_pattern: "dev*.values.yaml"
    new_tag: v1.0.1
```

<br/>

### Debug Mode
Enable detailed logging for troubleshooting:
```yaml
- uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "dev*.values.yaml"
    new_tag: v1.0.1
    debug: "true"
```

Debug mode provides additional information such as:
- Directory contents
- Git operation details
- File processing steps
- Detailed error messages

<br/>

## Example Workflows

<br/>

### Production Deployment
```yaml
name: Production Image Update
on:
  workflow_dispatch:
    inputs:
      new_tag:
        description: 'New image tag to deploy'
        required: true

jobs:
  update-image:
    runs-on: ubuntu-latest
    steps:
      - uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api
          file_pattern: "prod*.values.yaml"
          new_tag: ${{ github.event.inputs.new_tag }}
          verify_tag: "true"
          notification_webhook: ${{ secrets.DISCORD_WEBHOOK }}
          github_token: ${{ secrets.PAT }}
```

<br/>

### Development Testing
```yaml
name: Dev Image Update
on:
  push:
    branches: [ develop ]

jobs:
  update-image:
    runs-on: ubuntu-latest
    steps:
      - uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api
          file_pattern: "dev*.values.yaml"
          new_tag: ${{ github.sha }}
          dry_run: "true"
          github_token: ${{ secrets.PAT }}
```

<br/>

## Example Workflow

This example demonstrates how to use the **Image Tag Updater** Action to update
an image tag in an infrastructure repository. It:

- Checks out the infrastructure repository where the image tag update will be
   applied.
- Runs the Action to update the specified image tag in the infrastructure
   repository.

```yaml
name: Example Workflow using Image Tag Updater

on:
  workflow_dispatch:
    inputs:
      run:
        description: 'workflow run'
        required: true
        default: 'true'

permissions:
  contents: write

jobs:
  acton-module:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout infrastructure repository
        uses: actions/checkout@v4
        with:
          repository: somaz94/image-tag-updater 
          token: ${{ secrets.PAT }}  

      - name: Set short sha
        id: vars
        run: |
          echo "short_sha=$(git rev-parse --short HEAD)" >> "$GITHUB_OUTPUT"

      # dry run
      - name: Dry Run
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api 
          new_tag: ${{ steps.vars.outputs.short_sha }}
          target_values_file: dev2
          branch: test
          github_token: ${{ secrets.PAT }}
          DRY_RUN: true

      - name: Run Image Tag Updater in the infrastructure repository
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api 
          new_tag: ${{ steps.vars.outputs.short_sha }}
          # target_values_file: dev2
          branch: test
          github_token: ${{ secrets.PAT }}
          git_user_name: GitHub Actions
          git_user_email: actions@github.com
          repo: somaz94/image-tag-updater
          file_pattern: "dev*.values.yaml"
          registry_url: nginx

      - name: Confirm Git log
        run: |
          git log -1

```

<br/>

## Notes

- GitHub Token: Make sure `secrets.GITHUB_TOKEN` (or a custom token with write
  permissions) is configured correctly to allow the Action to push changes to
  the infrastructure repository.
- Custom GitHub Token: For better security, you could create a dedicated token
  for this Action, granting it only the necessary permissions for the
  infrastructure repository.
- Backup Option: Use the backup option to control whether a backup file is
  created (true) or not (false).
- File Selection: You can use either `file_pattern` (e.g., "dev*.values.yaml") or
  `target_values_file` (e.g., "dev1.values.yaml") to specify which files to update. Only one
  of these options is required.

<br/>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br/>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.