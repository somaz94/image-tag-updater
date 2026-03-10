# CLAUDE.md - image-tag-updater

GitHub Action that automates image tag updates in YAML configuration files for GitOps workflows.

## Project Structure

```
main.py                           # Main entrypoint (Config, FileProcessor, GitOps orchestration)
src/
  __init__.py                     # Package init (version, exports)
  config.py                      # Config dataclass (from_env, validate, get_final_tag)
  file_processor.py              # File operations (validate, get_current_tag, update, glob)
  git_operations.py              # Git operations (configure, branch, commit, push with retry)
  logger.py                      # Logger class (info, debug, success, warning, error)
  summary.py                     # ChangeSummary (create, save JSON, print)
tests/
  conftest.py                    # pytest fixtures (clean_env)
  test_config.py                 # Config unit tests
  test_file_processor.py         # FileProcessor unit tests
  test_git_operations.py         # GitOperations unit tests (mocked subprocess)
  test_logger.py                 # Logger unit tests
  test_summary.py                # ChangeSummary unit tests
  test_main.py                   # main() integration tests (mocked)
  test_local.py                  # Legacy script-based tests (13 tests)
  test_new_features.py           # Legacy tag prefix/suffix tests (6 tests)
  test_conditional_summary.py    # Legacy conditional update tests (6 tests)
  README.md                      # Testing documentation
docs/
  ADVANCED_USAGE.md              # Matrix strategies, integration patterns
  TROUBLESHOOTING.md             # Common issues and debugging guide
Dockerfile                       # Single-stage (python:3.14-slim)
action.yml                       # GitHub Action definition (14 inputs, 7 outputs)
Makefile                         # Development commands (test, coverage, lint, docker)
pyproject.toml                   # pytest and coverage configuration
requirements-dev.txt             # Dev dependencies (pytest, pytest-cov)
cliff.toml                       # git-cliff config for release notes
CODEOWNERS                       # Repository code owners
CONTRIBUTORS.md                  # Contributors list
```

## Build & Test

```bash
make venv          # Create virtualenv and install dev dependencies
make test          # Run unit tests with coverage (133 tests, 98%)
make test-local    # Run legacy integration tests
make test-all      # Run all tests (unit + local)
make coverage      # Generate HTML coverage report
make lint          # Run ruff linter
make format        # Format code with ruff
make ci            # Full CI pipeline (lint + format-check + test)
make clean         # Remove venv, cache, and build artifacts
make help          # Show all available commands
```

## Key Inputs

- **Required**: `target_path`, `new_tag`, `github_token`, `repo`
- **File selection** (one required): `target_values_file` OR `file_pattern`
- **Options**: `tag_string`, `branch`, `commit_message`, `git_user_name`, `git_user_email`
- **Features**: `backup`, `dry_run`, `debug`, `tag_prefix`, `tag_suffix`
- **Conditional**: `update_if_contains`, `skip_if_contains`
- **Tracking**: `summary_file`

## Outputs

`files_updated`, `updated_files`, `old_tags`, `new_tag_applied`, `changes_made`, `commit_sha`, `commit_sha_short`

## Workflow Structure

| Workflow | Name | Trigger |
|----------|------|---------|
| `ci.yml` | `Continuous Integration` | push(main), PR, dispatch |
| `release.yml` | `Create release` | tag push `v*` |
| `changelog-generator.yml` | `Generate changelog` | after release, PR merge, dispatch |
| `use-action.yml` | `Smoke Test (Released Action)` | after release, dispatch |
| `use-action-v2.yml` | `Smoke Test v2` | after release, dispatch |
| `contributors.yml` | `Generator Contributors` | after changelog, dispatch |
| `gitlab-mirror.yml` | `GitLab Mirroring` | push(main), dispatch |

### Workflow Chain
```
tag push v* -> Create release
                ├-> Smoke Test (Released Action)
                ├-> Smoke Test v2
                └-> Generate changelog -> Generator Contributors
```

### CI Structure
```
test-local ─────────────┐
build-and-push-docker ──> matrix-test ──> ci-result
```

## Conventions

- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`)
- **Branches**: `main` (production)
- **Secrets**: `PAT_TOKEN` (cross-repo ops), `GITHUB_TOKEN` (changelog, releases)
- **Docker**: Single-stage build, python:3.14-slim base
- **Comments**: English only
- **Testing**: pytest with coverage, fixtures in conftest.py
- **Release**: `git switch` (not `git checkout`), git-cliff for RELEASE.md
- **paths-ignore**: `.github/workflows/**`, `**/*.md`, `backup/**`
- Do NOT commit directly - recommend commit messages only
