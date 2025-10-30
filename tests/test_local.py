#!/usr/bin/env python3
"""Comprehensive tests for image tag updater."""
import os
import sys
import tempfile
import shutil
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.file_processor import FileProcessor
from src.logger import Logger


def create_test_values_file(content: str, directory: str, filename: str = "values.yaml") -> str:
    """Create a test values file."""
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path


def test_basic_tag_update():
    """Test basic tag update."""
    print("\n🧪 Test 1: Basic tag update")
    
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
            new_tag="v2.0.0",
            tag_string="tag",
            git_user_name="test",
            git_user_email="test@example.com",
            github_token="token",
            repo="test/repo",
            branch="main",
            target_values_file="values.yaml",
            dry_run=True,
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        
        if changed:
            print("   ✅ PASS: Tag update detected")
            return True
        else:
            print("   ❌ FAIL: No change detected")
            return False


def test_already_updated():
    """Test when tag is already updated."""
    print("\n🧪 Test 2: Already updated tag")
    
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
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        
        if not changed:
            print("   ✅ PASS: No update needed")
            return True
        else:
            print("   ❌ FAIL: Unexpected change")
            return False


def test_actual_file_update():
    """Test actual file update (not dry run)."""
    print("\n🧪 Test 3: Actual file update with backup")
    
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
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        
        with open(file_path, 'r') as f:
            updated_content = f.read()
        
        backup_exists = os.path.exists(f"{file_path}.bak")
        
        if changed and 'v3.0.0' in updated_content and backup_exists:
            print("   ✅ PASS: File updated correctly with backup")
            return True
        else:
            print("   ❌ FAIL: File update failed")
            return False


def test_multiple_files_pattern():
    """Test multiple files with pattern matching."""
    print("\n🧪 Test 4: Multiple files with pattern (dev*.values.yaml)")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple files
        files = {
            "dev1.values.yaml": "image:\n  tag: \"v1.0.0\"",
            "dev2.values.yaml": "image:\n  tag: \"v1.0.0\"",
            "prod.values.yaml": "image:\n  tag: \"v1.0.0\"",  # Should NOT match
        }
        
        for filename, content in files.items():
            create_test_values_file(content, tmpdir, filename)
        
        # Change to tmpdir to test pattern matching
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            config = Config(
                target_path=tmpdir,
                new_tag="v2.0.0",
                tag_string="tag",
                git_user_name="test",
                git_user_email="test@example.com",
                github_token="token",
                repo="test/repo",
                branch="main",
                file_pattern="dev*.values.yaml",
                dry_run=True,
                debug=False
            )
            
            logger = Logger(debug=False)
            processor = FileProcessor(config, logger)
            
            matched_files = processor.get_files_to_process()
            
            # Should match dev1 and dev2, but not prod
            if len(matched_files) == 2 and all('dev' in f for f in matched_files):
                print(f"   ✅ PASS: Pattern matched {len(matched_files)} files correctly")
                return True
            else:
                print(f"   ❌ FAIL: Expected 2 dev files, got {len(matched_files)}: {matched_files}")
                return False
        finally:
            os.chdir(original_cwd)


def test_custom_tag_string():
    """Test custom tag string."""
    print("\n🧪 Test 5: Custom tag string (imageTag)")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """
app:
  imageTag: "v1.0.0"
  name: myapp
"""
        file_path = create_test_values_file(content, tmpdir)
        
        config = Config(
            target_path=tmpdir,
            new_tag="v2.0.0",
            tag_string="imageTag",  # Custom tag string
            git_user_name="test",
            git_user_email="test@example.com",
            github_token="token",
            repo="test/repo",
            branch="main",
            target_values_file="values.yaml",
            dry_run=True,
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        
        if changed:
            print("   ✅ PASS: Custom tag string worked")
            return True
        else:
            print("   ❌ FAIL: Custom tag string not detected")
            return False


def test_invalid_tag_format():
    """Test invalid tag format validation."""
    print("\n🧪 Test 6: Invalid tag format validation")
    
    try:
        config = Config(
            target_path="/tmp",
            new_tag="@invalid@tag!",  # Invalid characters
            tag_string="tag",
            git_user_name="test",
            git_user_email="test@example.com",
            github_token="token",
            repo="test/repo",
            branch="main",
            target_values_file="values.yaml",
            dry_run=True,
            debug=False
        )
        config.validate()  # Trigger validation
        print("   ❌ FAIL: Invalid tag was accepted")
        return False
    except ValueError as e:
        if "Invalid tag format" in str(e):
            print("   ✅ PASS: Invalid tag rejected correctly")
            return True
        else:
            print(f"   ❌ FAIL: Wrong error: {e}")
            return False


def test_valid_tag_formats():
    """Test various valid tag formats."""
    print("\n🧪 Test 7: Valid tag formats")
    
    valid_tags = [
        "v1.0.0",
        "2024.01.15",
        "main-abc123",
        "1.2.3-beta",
        "prod_v1",
        "release.2024.01",
    ]
    
    all_valid = True
    for tag in valid_tags:
        try:
            config = Config(
                target_path="/tmp",
                new_tag=tag,
                tag_string="tag",
                git_user_name="test",
                git_user_email="test@example.com",
                github_token="token",
                repo="test/repo",
                branch="main",
                dry_run=True,
                debug=False
            )
        except ValueError:
            print(f"   ❌ Valid tag '{tag}' was rejected")
            all_valid = False
    
    if all_valid:
        print(f"   ✅ PASS: All {len(valid_tags)} valid tags accepted")
        return True
    else:
        print("   ❌ FAIL: Some valid tags were rejected")
        return False


def test_no_backup():
    """Test file update without backup."""
    print("\n🧪 Test 8: File update without backup")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """
image:
  tag: "v1.0.0"
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
            dry_run=False,
            backup=False,  # No backup
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        backup_exists = os.path.exists(f"{file_path}.bak")
        
        if changed and not backup_exists:
            print("   ✅ PASS: File updated without backup")
            return True
        else:
            print("   ❌ FAIL: Backup incorrectly created or file not updated")
            return False


def test_nested_yaml_structure():
    """Test nested YAML structure."""
    print("\n🧪 Test 9: Nested YAML structure")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """
global:
  image:
    registry: docker.io
  apps:
    frontend:
      tag: "v1.0.0"
    backend:
      tag: "v1.0.0"
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
            dry_run=False,
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        changed = processor.update_file(file_path)
        
        with open(file_path, 'r') as f:
            updated_content = f.read()
        
        # Count occurrences of new tag
        new_tag_count = updated_content.count('v2.0.0')
        
        if changed and new_tag_count == 2:  # Both frontend and backend
            print("   ✅ PASS: All nested tags updated")
            return True
        else:
            print(f"   ❌ FAIL: Expected 2 tag updates, found {new_tag_count}")
            return False


def test_config_validation():
    """Test configuration validation."""
    print("\n🧪 Test 10: Configuration validation")
    
    test_cases = [
        {
            "name": "Both file_pattern and target_values_file",
            "params": {
                "target_path": "/tmp",
                "new_tag": "v1.0.0",
                "tag_string": "tag",
                "git_user_name": "test",
                "git_user_email": "test@example.com",
                "github_token": "token",
                "repo": "test/repo",
                "branch": "main",
                "file_pattern": "*.yaml",
                "target_values_file": "values.yaml",
            },
            "should_fail": True,
        },
        {
            "name": "Neither file_pattern nor target_values_file",
            "params": {
                "target_path": "/tmp",
                "new_tag": "v1.0.0",
                "tag_string": "tag",
                "git_user_name": "test",
                "git_user_email": "test@example.com",
                "github_token": "token",
                "repo": "test/repo",
                "branch": "main",
            },
            "should_fail": True,
        },
    ]
    
    all_passed = True
    for test_case in test_cases:
        try:
            config = Config(**test_case["params"])
            config.validate()  # Trigger validation
            if test_case["should_fail"]:
                print(f"   ❌ {test_case['name']}: Should have failed")
                all_passed = False
        except ValueError:
            if test_case["should_fail"]:
                pass  # Expected
            else:
                print(f"   ❌ {test_case['name']}: Unexpected failure")
                all_passed = False
    
    if all_passed:
        print("   ✅ PASS: Configuration validation working")
        return True
    else:
        return False


def test_debug_mode():
    """Test debug mode logging."""
    print("\n🧪 Test 11: Debug mode logging")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """
image:
  tag: "v1.0.0"
"""
        file_path = create_test_values_file(content, tmpdir)
        
        # Test with debug mode
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
            debug=True  # Enable debug
        )
        
        logger = Logger(debug=True)
        processor = FileProcessor(config, logger)
        
        # Just verify it doesn't crash with debug mode
        changed = processor.update_file(file_path)
        
        if changed:
            print("   ✅ PASS: Debug mode working")
            return True
        else:
            print("   ❌ FAIL: Debug mode issue")
            return False


def test_empty_file():
    """Test handling empty file."""
    print("\n🧪 Test 12: Empty file handling")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = ""
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
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        # Empty file means current_tag is empty string
        # new_tag is v2.0.0, so they're different, will return True
        # But it's dry_run so file won't actually change
        changed = processor.update_file(file_path)
        
        # Read file to confirm it wasn't changed (dry run)
        with open(file_path, 'r') as f:
            final_content = f.read()
        
        # For empty file with no tag field, it should detect "change" in dry-run
        # but file should remain empty
        if changed and final_content == "":
            print("   ✅ PASS: Empty file handled correctly (dry-run detected potential change)")
            return True
        else:
            print("   ❌ FAIL: Empty file handling issue")
            return False


def test_file_without_tag():
    """Test file without target tag string."""
    print("\n🧪 Test 13: File without target tag")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """
image:
  repository: myapp
  pullPolicy: Always
# No tag field
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
            debug=False
        )
        
        logger = Logger(debug=False)
        processor = FileProcessor(config, logger)
        
        # File without tag field will have empty current_tag
        # This will be detected as change in dry-run mode
        changed = processor.update_file(file_path)
        
        # Read file to confirm it wasn't changed (dry run)
        with open(file_path, 'r') as f:
            final_content = f.read()
        
        # Should detect potential change but not modify file in dry-run
        if changed and "v2.0.0" not in final_content:
            print("   ✅ PASS: File without tag handled correctly (would add tag)")
            return True
        else:
            print("   ❌ FAIL: Unexpected behavior")
            return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("🧪 Image Tag Updater - Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        test_basic_tag_update,
        test_already_updated,
        test_actual_file_update,
        test_multiple_files_pattern,
        test_custom_tag_string,
        test_invalid_tag_format,
        test_valid_tag_formats,
        test_no_backup,
        test_nested_yaml_structure,
        test_config_validation,
        test_debug_mode,
        test_empty_file,
        test_file_without_tag,
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed!")
        print("=" * 50)
        sys.exit(0)
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
