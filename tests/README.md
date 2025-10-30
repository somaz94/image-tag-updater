# Tests

This directory contains test files for the image tag updater.

<br/>

## Running Tests

```bash
# Run all tests
python3 tests/test_local.py

# Or from tests directory
cd tests
python3 test_local.py
```

<br/>

## Test Cases

1. **Basic tag update** - Tests normal tag update operation
2. **Already updated** - Tests when tag is already at target value
3. **Actual file update** - Tests real file modification with backup
