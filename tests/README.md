# Test Suite

This directory contains comprehensive tests for the image-tag-updater action.

<br/>

## Running Tests

```bash
# Create venv and install dev dependencies
make venv

# Run all tests with coverage
make test

# Generate HTML coverage report
make coverage

# Run individual test files
make test-local
make test-features
make test-conditional
```

<br/>

## Test Files

### Pytest-Based Unit Tests

| File | Module Under Test | Tests |
|------|-------------------|-------|
| `test_config.py` | `src/config.py` | `Config.from_env`, `validate`, `get_final_tag`, `print_config` |
| `test_logger.py` | `src/logger.py` | All log methods, debug mode toggle, `error()` raising `ActionError` |
| `test_file_processor.py` | `src/file_processor.py` | File validation, tag extraction, updates, backups, glob patterns |
| `test_git_operations.py` | `src/git_operations.py` | Command execution, branch management, commit/push with retry |
| `test_summary.py` | `src/summary.py` | Summary creation, JSON save/append, edge cases |
| `test_main.py` | `main.py` | `write_output`, `main()` flow (dry-run, actual, error paths) |

### Legacy Script-Based Tests

| File | Description |
|------|-------------|
| `test_local.py` | Core functionality (tag update, pattern matching, validation, edge cases) |
| `test_new_features.py` | Tag prefix/suffix and final-tag validation |
| `test_conditional_summary.py` | Conditional updates and change summary tracking |

<br/>

## Test Coverage

`make test` prints per-module coverage with the missing line numbers. `make coverage` also writes an HTML report to `htmlcov/`.

<br/>

## Test Design Principles

1. **Isolation** - Each test uses temporary directories via `tmp_path` / `tempfile`
2. **Repeatability** - Tests can be run multiple times without side effects
3. **Coverage** - All major code paths and edge cases tested
4. **Mocking** - External dependencies (`subprocess`, `os.environ`) are mocked
5. **Independence** - pytest tests do not depend on each other. The legacy scripts manage `os.environ` themselves, so `conftest.py` skips its env cleanup for them.

<br/>

## Adding New Tests

Use pytest conventions for new tests:

```python
import pytest
from src.config import Config


class TestMyFeature:
    def test_expected_behavior(self, tmp_path):
        config = Config(...)
        result = config.some_method()
        assert result == expected
```

<br/>

## Requirements

- Python 3.12+
- Dev dependencies from `requirements-dev.txt` (installed via `make venv`)

<br/>

## Continuous Integration

`.github/workflows/ci.yml` runs only the three legacy scripts (the `test-local` job), on every pull request and push to `main`, before the Docker build. Run the pytest suite and ruff locally with `make ci`.
