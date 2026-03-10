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
| `test_logger.py` | `src/logger.py` | All log methods, debug mode toggle, error exit |
| `test_file_processor.py` | `src/file_processor.py` | File validation, tag extraction, updates, backups, glob patterns |
| `test_git_operations.py` | `src/git_operations.py` | Command execution, branch management, commit/push with retry |
| `test_summary.py` | `src/summary.py` | Summary creation, JSON save/append, edge cases |
| `test_main.py` | `main.py` | `write_output`, `main()` flow (dry-run, actual, error paths) |

### Legacy Script-Based Tests

| File | Description |
|------|-------------|
| `test_local.py` | Core functionality (tag update, pattern matching, validation, edge cases) |
| `test_new_features.py` | Tag prefix/suffix and output generation |
| `test_conditional_summary.py` | Conditional updates and change summary tracking |

<br/>

## Test Coverage

Current coverage: **98%** (133 tests, 0 failures)

```
Name                    Stmts   Miss  Cover
---------------------------------------------
main.py                    76      6    92%
src/__init__.py             5      0   100%
src/config.py              63      0   100%
src/file_processor.py     106      2    98%
src/git_operations.py      93      0   100%
src/logger.py              21      0   100%
src/summary.py             60      0   100%
---------------------------------------------
TOTAL                     424      8    98%
```

Uncovered lines are unreachable code after `sys.exit(1)` calls and the `if __name__ == "__main__"` guard.

<br/>

## Test Design Principles

1. **Isolation** - Each test uses temporary directories via `tmp_path` / `tempfile`
2. **Repeatability** - Tests can be run multiple times without side effects
3. **Coverage** - All major code paths and edge cases tested
4. **Mocking** - External dependencies (`subprocess`, `os.environ`) are mocked
5. **Independence** - Tests do not depend on each other

<br/>

## Adding New Tests

Use pytest conventions for new tests:

```python
import pytest
from src.config import Config


class TestMyFeature:
    def test_expected_behavior(self, tmp_path):
        """Describe what this test verifies."""
        # Setup
        config = Config(...)

        # Execute
        result = config.some_method()

        # Assert
        assert result == expected
```

<br/>

## Requirements

- Python 3.12+
- Dev dependencies: `pytest`, `pytest-cov` (installed via `make venv`)

<br/>

## Continuous Integration

Tests run automatically in CI/CD via `.github/workflows/ci.yml`:
- Before building Docker images
- On every pull request and push to `main`
