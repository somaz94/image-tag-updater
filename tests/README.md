# Test Suite

This directory contains comprehensive tests for the image-tag-updater action.

<br/>

## Running Tests

```bash
# Run all tests
python3 tests/test_local.py

# Or from project root
python3 -m tests.test_local
```

<br/>

## Test Coverage

The test suite covers **13 comprehensive test cases**:

### 1. Basic Functionality Tests
- **Test 1: Basic tag update** - Standard tag replacement in values.yaml
- **Test 2: Already updated tag** - Skip update when tag is already correct
- **Test 3: Actual file update with backup** - Real file modification with backup creation

### 2. Pattern Matching Tests
- **Test 4: Multiple files with pattern** - Glob pattern matching (dev*.values.yaml)
- **Test 5: Custom tag string** - Using custom tag field names (e.g., imageTag)

### 3. Validation Tests
- **Test 6: Invalid tag format validation** - Reject tags with invalid characters
- **Test 7: Valid tag formats** - Accept various valid tag formats
  - Semantic versions (v1.0.0)
  - Date-based tags (2024.01.15)
  - Git-based tags (main-abc123)
  - Pre-release tags (1.2.3-beta)

### 4. Configuration Tests
- **Test 8: File update without backup** - Update without creating backup file
- **Test 9: Nested YAML structure** - Handle multiple tag occurrences in nested structures
- **Test 10: Configuration validation** - Validate config constraints
  - Reject both file_pattern and target_values_file
  - Require at least one file selection method

### 5. Edge Cases & Debug Tests
- **Test 11: Debug mode logging** - Verify debug output works correctly
- **Test 12: Empty file handling** - Handle empty YAML files gracefully
- **Test 13: File without target tag** - Detect files missing tag field

<br/>

## Test Requirements

- Python 3.12+
- No external dependencies (uses only standard library)
- Temporary directories for isolated testing
- All tests are repeatable and independent

<br/>

## Test Output

Each test provides clear pass/fail indicators:
- ✅ PASS: Test succeeded
- ❌ FAIL: Test failed with details

Final summary shows:
```
📊 Test Results: 13/13 passed
✅ All tests passed!
```

<br/>

## Test Design Principles

1. **Isolation** - Each test uses temporary directories
2. **Repeatability** - Tests can be run multiple times without side effects
3. **Coverage** - All major code paths and edge cases tested
4. **Clarity** - Clear test names and descriptive output
5. **Independence** - Tests don't depend on each other

<br/>

## Adding New Tests

To add a new test:

1. Create a test function with descriptive name
2. Use `tempfile.TemporaryDirectory()` for isolation
3. Include clear print statements for output
4. Return `True` for pass, `False` for fail
5. Add to the `tests` list in `main()`

Example:
```python
def test_my_new_feature():
    """Test description."""
    print("\n🧪 Test X: My new feature")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test setup
        # ...
        
        # Run test
        result = some_function()
        
        if result == expected:
            print("   ✅ PASS: Feature works")
            return True
        else:
            print("   ❌ FAIL: Feature failed")
            return False
```

<br/>

## Continuous Integration

These tests run automatically in CI/CD:
- Before building Docker images
- Before deploying to GitHub Actions
- On every pull request

See `.github/workflows/ci.yml` for CI configuration.
