# Advanced Usage Guide

<br/>

## Table of Contents
- [Multiple File Updates](#multiple-file-updates)
- [Environment-Specific Updates](#environment-specific-updates)
- [Matrix Strategy Deployments](#matrix-strategy-deployments)
- [Integration Patterns](#integration-patterns)
- [Custom Git Operations](#custom-git-operations)

<br/>

## Multiple File Updates

<br/>

### Update Multiple Environment Files

Update all development environment files at once:

```yaml
- name: Update All Dev Environments
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "dev*.values.yaml"
    new_tag: v1.0.1
    github_token: ${{ secrets.PAT }}
```

<br/>

### Update Specific File Combinations

```yaml
- name: Update Staging and QA
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "{staging,qa}*.values.yaml"
    new_tag: v1.0.1
    github_token: ${{ secrets.PAT }}
```

<br/>

## Environment-Specific Updates

<br/>

### Production Deployment

```yaml
name: Production Image Update
on:
  release:
    types: [published]

jobs:
  update-production:
    runs-on: ubuntu-latest
    steps:
      - name: Update Production Images
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api
          file_pattern: "prod*.values.yaml"
          new_tag: ${{ github.event.release.tag_name }}
          github_token: ${{ secrets.PAT }}
          branch: main
          git_user_name: Release Bot
          git_user_email: release-bot@company.com
```

### Development Auto-Update

```yaml
name: Dev Auto-Update
on:
  push:
    branches: [develop]

jobs:
  update-dev:
    runs-on: ubuntu-latest
    steps:
      - name: Update Dev Images
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api
          file_pattern: "dev*.values.yaml"
          new_tag: dev-${{ github.sha }}
          github_token: ${{ secrets.PAT }}
          branch: develop
```

<br/>

## Matrix Strategy Deployments

<br/>

### Multi-Environment Deployment

```yaml
name: Multi-Environment Deploy
on:
  workflow_dispatch:
    inputs:
      new_tag:
        description: 'Image tag to deploy'
        required: true

jobs:
  update-environments:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment:
          - name: development
            pattern: "dev*.values.yaml"
            branch: develop
          - name: staging
            pattern: "staging*.values.yaml"
            branch: staging
          - name: production
            pattern: "prod*.values.yaml"
            branch: main
    steps:
      - name: Update ${{ matrix.environment.name }}
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/somaz/api
          file_pattern: ${{ matrix.environment.pattern }}
          new_tag: ${{ github.event.inputs.new_tag }}
          branch: ${{ matrix.environment.branch }}
          github_token: ${{ secrets.PAT }}
```

<br/>

## Integration Patterns

<br/>

### With Docker Build

```yaml
name: Build and Update
on:
  push:
    branches: [main]

jobs:
  build-and-update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push myapp:${{ github.sha }}

      - name: Update Infrastructure Repo
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/myapp
          file_pattern: "*.values.yaml"
          new_tag: ${{ github.sha }}
          github_token: ${{ secrets.PAT }}
          repo: company/infrastructure
```

### With Semantic Release

```yaml
name: Semantic Release and Deploy
on:
  push:
    branches: [main]

jobs:
  release-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Semantic Release
        id: semantic
        uses: cycjimmy/semantic-release-action@v3

      - name: Update Image Tags
        if: steps.semantic.outputs.new_release_published == 'true'
        uses: somaz94/image-tag-updater@v1
        with:
          target_path: charts/myapp
          file_pattern: "prod*.values.yaml"
          new_tag: ${{ steps.semantic.outputs.new_release_version }}
          github_token: ${{ secrets.PAT }}
```

<br/>

## Custom Git Operations

<br/>

### Custom Branch Strategy

```yaml
- name: Update Feature Branch
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "dev*.values.yaml"
    new_tag: feature-${{ github.head_ref }}
    branch: feature/${{ github.head_ref }}
    github_token: ${{ secrets.PAT }}
```

### Custom Commit Messages

```yaml
- name: Update with Custom Message
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    target_values_file: prod.values.yaml
    new_tag: v2.0.0
    commit_message: "chore(k8s): Update production image to"
    github_token: ${{ secrets.PAT }}
```

<br/>

## Backup and Rollback

<br/>

### With Backup Enabled

```yaml
- name: Update with Backup
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "prod*.values.yaml"
    new_tag: v2.0.0
    backup: "true"
    github_token: ${{ secrets.PAT }}
```

This creates `.bak` files before making changes:
- `prod.values.yaml.bak`
- `prod-us.values.yaml.bak`

### Manual Rollback

```yaml
- name: Rollback to Previous Version
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "prod*.values.yaml"
    new_tag: v1.9.9  # Previous stable version
    github_token: ${{ secrets.PAT }}
```

<br/>

## Testing and Validation

<br/>

### Dry Run Mode

Always test your changes first:

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

<br/>

### Validation After Update

```yaml
- name: Update Images
  id: update
  uses: somaz94/image-tag-updater@v1
  with:
    target_path: charts/somaz/api
    file_pattern: "prod*.values.yaml"
    new_tag: v2.0.0
    github_token: ${{ secrets.PAT }}

- name: Validate Changes
  run: |
    git diff HEAD~1 HEAD
    grep "tag: \"v2.0.0\"" charts/somaz/api/*.values.yaml
```

<br/>

## Best Practices

1. **Always use dry run for production deployments initially**
2. **Enable debug mode when troubleshooting issues**
3. **Use meaningful commit messages for better traceability**
4. **Implement matrix strategies for multi-environment updates**
5. **Enable backup for critical production updates**
6. **Validate changes after updates**
7. **Use semantic versioning for tags**
8. **Document your deployment workflow**
