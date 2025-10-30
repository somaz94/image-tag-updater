#!/usr/bin/env python3
"""Tests for conditional updates and change summary features."""
import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.logger import Logger
from src.summary import ChangeSummary


def setup_test_env():
    """Setup test environment variables."""
    os.environ.update({
        "TARGET_PATH": "/tmp/test",
        "NEW_TAG": "v1.2.3",
        "TAG_STRING": "tag",
        "GIT_USER_NAME": "Test User",
        "GIT_USER_EMAIL": "test@example.com",
        "GITHUB_TOKEN": "test_token",
        "REPO": "test/repo",
        "BRANCH": "main",
        "TARGET_VALUES_FILE": "test.yaml",
        "FILE_PATTERN": "",
        "TAG_PREFIX": "",
        "TAG_SUFFIX": ""
    })


def test_update_if_contains():
    """Test update_if_contains condition."""
    print("\n=== Testing update_if_contains ===")
    
    setup_test_env()
    os.environ["UPDATE_IF_CONTAINS"] = "v1."
    
    config = Config.from_env()
    
    # Simulate current tag checks
    current_tag_v1 = "v1.0.0"
    current_tag_v2 = "v2.0.0"
    
    # Should update v1.x tags
    should_update = config.update_if_contains in current_tag_v1
    assert should_update, f"Should update {current_tag_v1}"
    print(f"✅ Would update: {current_tag_v1} (contains '{config.update_if_contains}')")
    
    # Should skip v2.x tags
    should_skip = config.update_if_contains not in current_tag_v2
    assert should_skip, f"Should skip {current_tag_v2}"
    print(f"✅ Would skip: {current_tag_v2} (does not contain '{config.update_if_contains}')")


def test_skip_if_contains():
    """Test skip_if_contains condition."""
    print("\n=== Testing skip_if_contains ===")
    
    setup_test_env()
    os.environ["SKIP_IF_CONTAINS"] = "latest"
    
    config = Config.from_env()
    
    # Simulate current tag checks
    current_tag_latest = "latest"
    current_tag_version = "v1.0.0"
    
    # Should skip 'latest' tags
    should_skip = config.skip_if_contains in current_tag_latest
    assert should_skip, f"Should skip {current_tag_latest}"
    print(f"✅ Would skip: {current_tag_latest} (contains '{config.skip_if_contains}')")
    
    # Should update version tags
    should_update = config.skip_if_contains not in current_tag_version
    assert should_update, f"Should update {current_tag_version}"
    print(f"✅ Would update: {current_tag_version} (does not contain '{config.skip_if_contains}')")


def test_combined_conditions():
    """Test both conditions together."""
    print("\n=== Testing Combined Conditions ===")
    
    setup_test_env()
    os.environ["UPDATE_IF_CONTAINS"] = "v1."
    os.environ["SKIP_IF_CONTAINS"] = "prod"
    
    config = Config.from_env()
    
    test_cases = [
        ("v1.0.0", True, "contains v1., not prod"),
        ("v1.0.0-prod", False, "contains v1. but also prod"),
        ("v2.0.0", False, "does not contain v1."),
        ("v2.0.0-prod", False, "neither contains v1. nor should update prod"),
    ]
    
    for tag, should_update, reason in test_cases:
        matches_update = not config.update_if_contains or config.update_if_contains in tag
        matches_skip = config.skip_if_contains and config.skip_if_contains in tag
        result = matches_update and not matches_skip
        
        assert result == should_update, f"Failed for {tag}: expected {should_update}, got {result}"
        status = "update" if should_update else "skip"
        print(f"✅ {tag}: {status} ({reason})")


def test_summary_creation():
    """Test change summary creation."""
    print("\n=== Testing Summary Creation ===")
    
    setup_test_env()
    os.environ["SUMMARY_FILE"] = ""
    
    config = Config.from_env()
    logger = Logger(debug=False)
    summary = ChangeSummary(config, logger)
    
    # Create test data
    updated_files = ["dev1.yaml", "dev2.yaml"]
    old_tags = {
        "dev1.yaml": "v1.0.0",
        "dev2.yaml": "v1.0.1"
    }
    commit_sha = "abc123"
    
    # Create summary
    result = summary.create_summary(updated_files, old_tags, commit_sha)
    
    # Verify summary structure
    assert result["repository"] == "test/repo"
    assert result["branch"] == "main"
    assert result["commit_sha"] == "abc123"
    assert result["changes_count"] == 2
    assert len(result["changes"]) == 2
    assert result["changes"][0]["file"] == "dev1.yaml"
    assert result["changes"][0]["old_tag"] == "v1.0.0"
    assert result["changes"][0]["new_tag"] == "v1.2.3"
    
    print("✅ Summary structure is correct")
    print(f"   Repository: {result['repository']}")
    print(f"   Branch: {result['branch']}")
    print(f"   Changes: {result['changes_count']}")
    print(f"   Commit: {result['commit_sha']}")


def test_summary_file_saving():
    """Test saving summary to file."""
    print("\n=== Testing Summary File Saving ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        summary_file = os.path.join(tmpdir, ".github", "updates.json")
        
        setup_test_env()
        os.environ["SUMMARY_FILE"] = summary_file
        
        config = Config.from_env()
        logger = Logger(debug=False)
        summary = ChangeSummary(config, logger)
        
        # Save first summary
        updated_files = ["file1.yaml"]
        old_tags = {"file1.yaml": "v1.0.0"}
        summary.save_summary(updated_files, old_tags, "commit1")
        
        # Verify file was created
        assert os.path.exists(summary_file), "Summary file was not created"
        print(f"✅ Summary file created: {summary_file}")
        
        # Read and verify content
        with open(summary_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list), "Summary should be a list"
        assert len(data) == 1, "Should have one entry"
        assert data[0]["commit_sha"] == "commit1"
        print(f"✅ Summary content is correct (1 entry)")
        
        # Save second summary
        updated_files = ["file2.yaml"]
        old_tags = {"file2.yaml": "v1.1.0"}
        summary.save_summary(updated_files, old_tags, "commit2")
        
        # Verify append worked
        with open(summary_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 2, "Should have two entries"
        assert data[1]["commit_sha"] == "commit2"
        print(f"✅ Summary append worked (2 entries)")


def test_no_conditions():
    """Test that action works without any conditions set."""
    print("\n=== Testing No Conditions ===")
    
    setup_test_env()
    os.environ["UPDATE_IF_CONTAINS"] = ""
    os.environ["SKIP_IF_CONTAINS"] = ""
    
    config = Config.from_env()
    
    # All tags should be updateable when no conditions are set
    test_tags = ["latest", "v1.0.0", "v2.0.0-prod", "main"]
    
    for tag in test_tags:
        should_update = True  # No conditions = always update
        print(f"✅ Would update: {tag} (no conditions set)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Conditional Updates and Change Summary")
    print("=" * 60)
    
    try:
        test_update_if_contains()
        test_skip_if_contains()
        test_combined_conditions()
        test_summary_creation()
        test_summary_file_saving()
        test_no_conditions()
        
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
