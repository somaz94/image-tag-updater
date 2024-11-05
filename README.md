# Image Tag Updater GitHub Action

[![License](https://img.shields.io/github/license/somaz94/image-tag-updater)](https://github.com/somaz94/container-action)
![Latest Tag](https://img.shields.io/github/v/tag/somaz94/image-tag-updater)
![Top Language](https://img.shields.io/github/languages/top/somaz94/image-tag-updater?color=green&logo=shell&logoColor=b)

## Description

The **Image Tag Updater** GitHub Action is designed to update image tags in a
specified file within a repository. It’s particularly useful in GitOps
workflows, where configuration changes need to be automatically reflected across
multiple repositories.

## Description

This action allows users to update specific lines in configuration files,
typically to update image tags, and commits the changes directly to the
repository. It supports checking out multiple repositories, making it ideal for
updating infrastructure repositories based on changes in source code
repositories.

## Inputs

| Input                | Required | Description                                                                   | Default                |
| -------------------- | -------- | ----------------------------------------------------------------------------- | ---------------------- |
| `target_path`        | Yes      | The directory path where the values file is located                           | N/A                    |
| `tag_string`         | No       | The tag string to match for updating the image tag                            | `"tag"`                |
| `new_tag`            | Yes      | The new image tag to replace the current one (e.g., `v1.0.1`)                 | N/A                    |
| `target_values_file` | Yes      | The prefix name of the values file to update (without .values.yaml extension) | N/A                    |
| `github_token`       | Yes      | A GitHub token for authenticating the push to the repository                  | N/A                    |
| `commit_message`     | No       | The commit message for the update                                             | `"Update image tag"`   |
| `branch`             | No       | The branch where changes should be committed                                  | `"main"`               |
| `git_user_name`      | No       | The Git username for commits                                                  | `"GitHub Action"`      |
| `git_user_email`     | No       | The Git email for commits                                                     | `"actions@github.com"` |
| `backup`             | No       | Specifies whether to create a backup file (true/false)                        | `"false"`              |
| `repo`               | Yes      | Git repository for commits (Repo to update)                                   | N/A           |

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

      # Step 2: Run Image Tag Updater in the infrastructure repository
      - name: Update Image Tag in Infrastructure Repo
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api 
          new_tag: ${{ steps.vars.outputs.short_sha }}
          target_values_file: dev1 
          github_token: ${{ secrets.PAT }}
          git_user_name: somaz
          git_user_email: genius5711@gmail.com
          repo: somaz94/image-tag-updater # Git repository for commits (Repo to update) 

      - name: Confirm Git log
        run: |
          git log -1

```

## Notes

- GitHub Token: Make sure `secrets.GITHUB_TOKEN` (or a custom token with write
  permissions) is configured correctly to allow the Action to push changes to
  the infrastructure repository.
- Custom GitHub Token: For better security, you could create a dedicated token
  for this Action, granting it only the necessary permissions for the
  infrastructure repository.
- Backup Option: Use the backup option to control whether a backup file is
  created (true) or not (false).
