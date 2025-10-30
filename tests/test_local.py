#!/usr/bin/env python3
"""Tests for image tag updater."""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.file_processor import FileProcessor
from src.logger import Logger


def create_test_values_file(content: str, directory: str) -> str:
    """Create a test values file."""
    file_path = os.path.join(directory, "values.yaml")
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path


def test_basic_tag_update():
    """Test basic tag update."""
    print("\n🧪 Test: Basic tag update")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        content = """
image:
  repository: myapp
  tag: "v1.0.0"
  pullPolicy: Always
"""
        file_path = create_test_values_file(content, tmpdir)
        
        # Create config
        config = Config(
            target_path=tmpdir,
            new_tag="v2.0.0",
            tag_string="tag",
            git_user_name="test",
            git_user_email="test@example.com",
            github_token="token",
            repo="test/repo",
            branch="main",
            target_values_file="values.yaml",
            dry_run=True,
            debug=False  # Disable debug for cleaner output
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        # Process file
        changed = processor.update_file(file_path)
        
        if changed:
            print("✅ PASS: Tag update detected")
            return True
        else:
            print("❌ FAIL: No change detected")
            return False


def test_already_updated():
    """Test when tag is already updated."""
    print("\n🧪 Test: Already updated tag")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """
image:
  tag: "v2.0.0"
"""
        file_path = create_test_values_file(content, tmpdir)
        
        config = Config(
            target_path=tmpdir,
            new_tag="v2.0.0",
            tag_string="tag",
            git_user_name="test",
            git_user_email="test@example.com",
            github_token="token",
            repo="test/repo",
            branch="main",
            target_values_file="values.yaml",
            dry_run=True,
            debug=False  # Disable debug for cleaner output
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        
        if not changed:
            print("✅ PASS: No update needed")
            return True
        else:
            print("❌ FAIL: Unexpected change")
            return False


def test_actual_file_update():
    """Test actual file update (not dry run)."""
    print("\n🧪 Test: Actual file update")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """
image:
  repository: myapp
  tag: "v1.0.0"
  pullPolicy: Always
"""
        file_path = create_test_values_file(content, tmpdir)
        
        config = Config(
            target_path=tmpdir,
            new_tag="v3.0.0",
            tag_string="tag",
            git_user_name="test",
            git_user_email="test@example.com",
            github_token="token",
            repo="test/repo",
            branch="main",
            target_values_file="values.yaml",
            dry_run=False,
            backup=True,
            debug=False  # Disable debug for cleaner output
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        
        # Read updated file
        with open(file_path, 'r') as f:
            updated_content = f.read()
        
        # Check backup exists
        backup_exists = os.path.exists(f"{file_path}.bak")
        
        if changed and 'v3.0.0' in updated_content and backup_exists:
            print("✅ PASS: File updated correctly with backup")
            return True
        else:
            print("❌ FAIL: File update failed")
            print(f"Changed: {changed}, Content has v3.0.0: {'v3.0.0' in updated_content}, Backup: {backup_exists}")
            return False


def main():
    """Run all tests."""
    print("=" * 42)
    print("🧪 Image Tag Updater Tests")
    print("=" * 42)
    
    results = []
    results.append(test_basic_tag_update())
    results.append(test_already_updated())
    results.append(test_actual_file_update())
    
    print("\n" + "=" * 42)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed!")
        print("=" * 42)
        sys.exit(0)
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("=" * 42)
        sys.exit(1)


if __name__ == "__main__":
    main()
