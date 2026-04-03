"""Tests for src/config.py"""
import os
import pytest
from unittest.mock import patch

from src.config import Config, TAG_PATTERN, REQUIRED_FIELDS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def base_config_kwargs():
    """Minimal valid Config keyword arguments."""
    return {
        "target_path": "/tmp/test",
        "new_tag": "v1.0.0",
        "tag_string": "tag",
        "git_user_name": "test",
        "git_user_email": "test@example.com",
        "github_token": "token",
        "repo": "test/repo",
        "branch": "main",
        "target_values_file": "values.yaml",
    }


@pytest.fixture
def valid_config(base_config_kwargs):
    return Config(**base_config_kwargs)


# ---------------------------------------------------------------------------
# from_env
# ---------------------------------------------------------------------------

class TestFromEnv:
    def test_from_env_basic(self):
        env = {
            "TARGET_PATH": "/app",
            "NEW_TAG": "v2.0.0",
            "TAG_STRING": "imageTag",
            "GIT_USER_NAME": "bot",
            "GIT_USER_EMAIL": "bot@ci.com",
            "GITHUB_TOKEN": "ghp_xxx",
            "REPO": "org/repo",
            "BRANCH": "develop",
            "COMMIT_MESSAGE": "deploy",
            "TARGET_VALUES_FILE": "values.yaml",
            "FILE_PATTERN": "",
            "BACKUP": "true",
            "DRY_RUN": "true",
            "DEBUG": "true",
            "MAX_RETRIES": "5",
            "TAG_PREFIX": "v",
            "TAG_SUFFIX": "-prod",
            "UPDATE_IF_CONTAINS": "v1.",
            "SKIP_IF_CONTAINS": "latest",
            "SUMMARY_FILE": "summary.json",
        }
        with patch.dict(os.environ, env, clear=False):
            cfg = Config.from_env()

        assert cfg.target_path == "/app"
        assert cfg.new_tag == "v2.0.0"
        assert cfg.tag_string == "imageTag"
        assert cfg.backup is True
        assert cfg.dry_run is True
        assert cfg.debug is True
        assert cfg.max_retries == 5
        assert cfg.tag_prefix == "v"
        assert cfg.tag_suffix == "-prod"
        assert cfg.update_if_contains == "v1."
        assert cfg.skip_if_contains == "latest"
        assert cfg.summary_file == "summary.json"

    def test_from_env_defaults(self):
        env = {
            "TARGET_PATH": "/app",
            "NEW_TAG": "v1.0.0",
            "TAG_STRING": "tag",
            "GIT_USER_NAME": "bot",
            "GIT_USER_EMAIL": "bot@ci.com",
            "GITHUB_TOKEN": "ghp_xxx",
            "REPO": "org/repo",
            "BRANCH": "main",
        }
        # Remove keys that would interfere
        for k in ["BACKUP", "DRY_RUN", "DEBUG", "TAG_PREFIX", "TAG_SUFFIX",
                   "UPDATE_IF_CONTAINS", "SKIP_IF_CONTAINS", "SUMMARY_FILE",
                   "COMMIT_MESSAGE", "MAX_RETRIES", "TARGET_VALUES_FILE", "FILE_PATTERN"]:
            os.environ.pop(k, None)

        with patch.dict(os.environ, env, clear=False):
            cfg = Config.from_env()

        assert cfg.backup is False
        assert cfg.dry_run is False
        assert cfg.debug is False
        assert cfg.max_retries == 3
        assert cfg.tag_prefix == ""
        assert cfg.tag_suffix == ""
        assert cfg.commit_message == "Update image tag"


# ---------------------------------------------------------------------------
# get_final_tag
# ---------------------------------------------------------------------------

class TestGetFinalTag:
    def test_no_prefix_suffix(self, valid_config):
        assert valid_config.get_final_tag() == "v1.0.0"

    def test_with_prefix(self, base_config_kwargs):
        cfg = Config(**{**base_config_kwargs, "new_tag": "1.0.0", "tag_prefix": "v"})
        assert cfg.get_final_tag() == "v1.0.0"

    def test_with_suffix(self, base_config_kwargs):
        cfg = Config(**{**base_config_kwargs, "tag_suffix": "-prod"})
        assert cfg.get_final_tag() == "v1.0.0-prod"

    def test_with_both(self, base_config_kwargs):
        cfg = Config(**{**base_config_kwargs, "new_tag": "1.0.0", "tag_prefix": "release-", "tag_suffix": "-staging"})
        assert cfg.get_final_tag() == "release-1.0.0-staging"


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_valid_config(self, valid_config):
        valid_config.validate()  # should not raise

    def test_missing_required_field(self, base_config_kwargs):
        base_config_kwargs["target_path"] = ""
        cfg = Config(**base_config_kwargs)
        with pytest.raises(ValueError, match="Required fields are not set"):
            cfg.validate()

    def test_invalid_tag_format(self, base_config_kwargs):
        base_config_kwargs["new_tag"] = "@invalid!"
        cfg = Config(**base_config_kwargs)
        with pytest.raises(ValueError, match="Invalid tag format"):
            cfg.validate()

    def test_invalid_final_tag_format(self, base_config_kwargs):
        base_config_kwargs["tag_prefix"] = "@"
        cfg = Config(**base_config_kwargs)
        with pytest.raises(ValueError, match="Invalid final tag format"):
            cfg.validate()

    def test_neither_file_nor_pattern(self, base_config_kwargs):
        base_config_kwargs["target_values_file"] = None
        base_config_kwargs["file_pattern"] = None
        cfg = Config(**base_config_kwargs)
        with pytest.raises(ValueError, match="Either target_values_file or file_pattern"):
            cfg.validate()

    def test_both_file_and_pattern(self, base_config_kwargs):
        base_config_kwargs["file_pattern"] = "*.yaml"
        cfg = Config(**base_config_kwargs)
        with pytest.raises(ValueError, match="Cannot set both"):
            cfg.validate()

    def test_invalid_repo_format(self, base_config_kwargs):
        base_config_kwargs["repo"] = "invalid-no-slash"
        cfg = Config(**base_config_kwargs)
        with pytest.raises(ValueError, match="Invalid repo format"):
            cfg.validate()

    def test_valid_repo_format(self, base_config_kwargs):
        base_config_kwargs["repo"] = "my-org/my-repo.name"
        cfg = Config(**base_config_kwargs)
        cfg.validate()  # should not raise


# ---------------------------------------------------------------------------
# print_config
# ---------------------------------------------------------------------------

class TestPrintConfig:
    def test_basic(self, valid_config, capsys):
        valid_config.print_config()
        out = capsys.readouterr().out
        assert "Configuration:" in out
        assert valid_config.target_path in out
        assert valid_config.new_tag in out

    def test_with_prefix_suffix(self, base_config_kwargs, capsys):
        cfg = Config(**{**base_config_kwargs, "new_tag": "1.0.0", "tag_prefix": "v", "tag_suffix": "-rc"})
        cfg.print_config()
        out = capsys.readouterr().out
        assert "Final Tag" in out

    def test_dry_run(self, base_config_kwargs, capsys):
        cfg = Config(**{**base_config_kwargs, "dry_run": True})
        cfg.print_config()
        out = capsys.readouterr().out
        assert "Dry Run" in out

    def test_file_pattern(self, base_config_kwargs, capsys):
        base_config_kwargs["target_values_file"] = None
        cfg = Config(**{**base_config_kwargs, "file_pattern": "*.yaml"})
        cfg.print_config()
        out = capsys.readouterr().out
        assert "Pattern" in out
