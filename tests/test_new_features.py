#!/usr/bin/env python3
"""Tests for new features: outputs and tag prefix/suffix."""
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config


def test_tag_prefix():
    """Test tag prefix functionality."""
    print("\n=== Testing Tag Prefix ===")
    
    # Set environment variables
    os.environ.update({
        "TARGET_PATH": "/tmp/test",
        "NEW_TAG": "1.2.3",
        "TAG_STRING": "tag",
        "GIT_USER_NAME": "Test User",
        "GIT_USER_EMAIL": "test@example.com",
        "GITHUB_TOKEN": "test_token",
        "REPO": "test/repo",
        "BRANCH": "main",
        "TAG_PREFIX": "v"
    })
    
    config = Config.from_env()
    final_tag = config.get_final_tag()
    
    assert final_tag == "v1.2.3", f"Expected 'v1.2.3', got '{final_tag}'"
    print(f"✅ Tag prefix test passed: {config.new_tag} -> {final_tag}")


def test_tag_suffix():
    """Test tag suffix functionality."""
    print("\n=== Testing Tag Suffix ===")
    
    os.environ.update({
        "NEW_TAG": "latest",
        "TAG_PREFIX": "",
        "TAG_SUFFIX": "-prod"
    })
    
    config = Config.from_env()
    final_tag = config.get_final_tag()
    
    assert final_tag == "latest-prod", f"Expected 'latest-prod', got '{final_tag}'"
    print(f"✅ Tag suffix test passed: {config.new_tag} -> {final_tag}")


def test_tag_prefix_and_suffix():
    """Test both prefix and suffix."""
    print("\n=== Testing Tag Prefix and Suffix ===")
    
    os.environ.update({
        "NEW_TAG": "1.2.3",
        "TAG_PREFIX": "release-",
        "TAG_SUFFIX": "-staging"
    })
    
    config = Config.from_env()
    final_tag = config.get_final_tag()
    
    assert final_tag == "release-1.2.3-staging", f"Expected 'release-1.2.3-staging', got '{final_tag}'"
    print(f"✅ Prefix and suffix test passed: {config.new_tag} -> {final_tag}")


def test_no_prefix_suffix():
    """Test without prefix/suffix."""
    print("\n=== Testing No Prefix/Suffix ===")
    
    os.environ.update({
        "NEW_TAG": "v1.0.0",
        "TAG_PREFIX": "",
        "TAG_SUFFIX": ""
    })
    
    config = Config.from_env()
    final_tag = config.get_final_tag()
    
    assert final_tag == "v1.0.0", f"Expected 'v1.0.0', got '{final_tag}'"
    print(f"✅ No prefix/suffix test passed: {final_tag}")


def test_tag_validation_with_prefix_suffix():
    """Test tag validation with prefix/suffix."""
    print("\n=== Testing Tag Validation ===")
    
    # Valid case
    os.environ.update({
        "NEW_TAG": "1.2.3",
        "TAG_PREFIX": "v",
        "TAG_SUFFIX": "-prod",
        "TARGET_VALUES_FILE": "test.yaml",
        "FILE_PATTERN": ""
    })
    
    config = Config.from_env()
    try:
        config.validate()
        print(f"✅ Validation passed for: {config.get_final_tag()}")
    except ValueError as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
    
    # Invalid case - final tag starts with special character
    print("\nTesting invalid tag format...")
    os.environ.update({
        "NEW_TAG": "1.2.3",
        "TAG_PREFIX": "@",
        "TAG_SUFFIX": "",
        "TARGET_VALUES_FILE": "test.yaml",
        "FILE_PATTERN": ""
    })
    
    config = Config.from_env()
    try:
        config.validate()
        print(f"❌ Should have failed validation for: {config.get_final_tag()}")
        sys.exit(1)
    except ValueError as e:
        print(f"✅ Correctly rejected invalid tag: {e}")


def test_print_config():
    """Test config printing with prefix/suffix."""
    print("\n=== Testing Config Print ===")
    
    os.environ.update({
        "NEW_TAG": "1.2.3",
        "TAG_PREFIX": "v",
        "TAG_SUFFIX": "-prod",
        "TARGET_VALUES_FILE": "test.yaml",
        "FILE_PATTERN": ""
    })
    
    config = Config.from_env()
    print("\nConfig output:")
    config.print_config()
    print("✅ Config print test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing New Features: Outputs and Tag Prefix/Suffix")
    print("=" * 60)
    
    try:
        test_tag_prefix()
        test_tag_suffix()
        test_tag_prefix_and_suffix()
        test_no_prefix_suffix()
        test_tag_validation_with_prefix_suffix()
        test_print_config()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
