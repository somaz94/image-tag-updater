"""Shared pytest fixtures for image-tag-updater tests."""
import os
import pytest

# Legacy test files that manage their own env vars
LEGACY_TEST_FILES = {
    "test_local.py",
    "test_new_features.py",
    "test_conditional_summary.py",
}


@pytest.fixture(autouse=True)
def clean_env(request, monkeypatch):
    """Remove environment variables that could leak between tests.

    Skipped for legacy script-based tests that manage env vars manually.
    """
    test_file = request.fspath.basename
    if test_file in LEGACY_TEST_FILES:
        return

    env_keys = [
        "TARGET_PATH", "NEW_TAG", "TAG_STRING",
        "GIT_USER_NAME", "GIT_USER_EMAIL", "GITHUB_TOKEN",
        "REPO", "BRANCH", "COMMIT_MESSAGE",
        "TARGET_VALUES_FILE", "FILE_PATTERN",
        "BACKUP", "DRY_RUN", "DEBUG", "MAX_RETRIES",
        "TAG_PREFIX", "TAG_SUFFIX",
        "UPDATE_IF_CONTAINS", "SKIP_IF_CONTAINS",
        "SUMMARY_FILE", "GITHUB_OUTPUT",
    ]
    for key in env_keys:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def github_output(tmp_path, monkeypatch):
    """Provide a temporary GITHUB_OUTPUT file."""
    output_file = str(tmp_path / "github_output")
    monkeypatch.setenv("GITHUB_OUTPUT", output_file)
    return output_file
