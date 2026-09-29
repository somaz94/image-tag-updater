#!/usr/bin/env python3
"""Legacy script tests for tag prefix/suffix and final-tag validation."""

import os
import sys
from pathlib import Path

# CI runs this file as a script, where only tests/ is on sys.path.
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config


def test_tag_prefix():
    print("\n=== Testing Tag Prefix ===")

    os.environ.update(
        {
            "TARGET_PATH": "/tmp/test",
            "NEW_TAG": "1.2.3",
            "TAG_STRING": "tag",
            "GIT_USER_NAME": "Test User",
            "GIT_USER_EMAIL": "test@example.com",
            "GITHUB_TOKEN": "test_token",
            "REPO": "test/repo",
            "BRANCH": "main",
            "TAG_PREFIX": "v",
        }
    )

    config = Config.from_env()
    final_tag = config.get_final_tag()

    assert final_tag == "v1.2.3", f"Expected 'v1.2.3', got '{final_tag}'"
    print(f"[O] Tag prefix test passed: {config.new_tag} -> {final_tag}")


def test_tag_suffix():
    print("\n=== Testing Tag Suffix ===")

    os.environ.update({"NEW_TAG": "latest", "TAG_PREFIX": "", "TAG_SUFFIX": "-prod"})

    config = Config.from_env()
    final_tag = config.get_final_tag()

    assert final_tag == "latest-prod", f"Expected 'latest-prod', got '{final_tag}'"
    print(f"[O] Tag suffix test passed: {config.new_tag} -> {final_tag}")


def test_tag_prefix_and_suffix():
    print("\n=== Testing Tag Prefix and Suffix ===")

    os.environ.update(
        {"NEW_TAG": "1.2.3", "TAG_PREFIX": "release-", "TAG_SUFFIX": "-staging"}
    )

    config = Config.from_env()
    final_tag = config.get_final_tag()

    assert final_tag == "release-1.2.3-staging", (
        f"Expected 'release-1.2.3-staging', got '{final_tag}'"
    )
    print(f"[O] Prefix and suffix test passed: {config.new_tag} -> {final_tag}")


def test_no_prefix_suffix():
    print("\n=== Testing No Prefix/Suffix ===")

    os.environ.update({"NEW_TAG": "v1.0.0", "TAG_PREFIX": "", "TAG_SUFFIX": ""})

    config = Config.from_env()
    final_tag = config.get_final_tag()

    assert final_tag == "v1.0.0", f"Expected 'v1.0.0', got '{final_tag}'"
    print(f"[O] No prefix/suffix test passed: {final_tag}")


def test_tag_validation_with_prefix_suffix():
    print("\n=== Testing Tag Validation ===")

    os.environ.update(
        {
            "NEW_TAG": "1.2.3",
            "TAG_PREFIX": "v",
            "TAG_SUFFIX": "-prod",
            "TARGET_VALUES_FILE": "test.yaml",
            "FILE_PATTERN": "",
        }
    )

    config = Config.from_env()
    try:
        config.validate()
        print(f"[O] Validation passed for: {config.get_final_tag()}")
    except ValueError as e:
        print(f"[X] Validation failed: {e}")
        sys.exit(1)

    # "@" prefix: TAG_PATTERN requires an alphanumeric first character.
    print("\nTesting invalid tag format...")
    os.environ.update(
        {
            "NEW_TAG": "1.2.3",
            "TAG_PREFIX": "@",
            "TAG_SUFFIX": "",
            "TARGET_VALUES_FILE": "test.yaml",
            "FILE_PATTERN": "",
        }
    )

    config = Config.from_env()
    try:
        config.validate()
        print(f"[X] Should have failed validation for: {config.get_final_tag()}")
        sys.exit(1)
    except ValueError as e:
        print(f"[O] Correctly rejected invalid tag: {e}")


def test_print_config():
    print("\n=== Testing Config Print ===")

    os.environ.update(
        {
            "NEW_TAG": "1.2.3",
            "TAG_PREFIX": "v",
            "TAG_SUFFIX": "-prod",
            "TARGET_VALUES_FILE": "test.yaml",
            "FILE_PATTERN": "",
        }
    )

    config = Config.from_env()
    print("\nConfig output:")
    config.print_config()
    print("[O] Config print test passed")


def main():
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
        print("[O] All tests passed!")
        print("=" * 60)

    except Exception as e:  # noqa: BLE001
        print(f"\n[X] Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
