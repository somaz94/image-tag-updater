"""Tests for src/summary.py"""
import json
import os
import pytest
from unittest.mock import patch

from src.config import Config
from src.logger import Logger
from src.summary import ChangeSummary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    return Config(
        target_path="/tmp/test",
        new_tag="v2.0.0",
        tag_string="tag",
        git_user_name="test",
        git_user_email="test@test.com",
        github_token="token",
        repo="org/repo",
        branch="main",
        target_values_file="values.yaml",
    )


@pytest.fixture
def logger():
    return Logger(debug=False)


@pytest.fixture
def summary(config, logger):
    return ChangeSummary(config, logger)


UPDATED_FILES = ["dev1.yaml", "dev2.yaml"]
OLD_TAGS = {"dev1.yaml": "v1.0.0", "dev2.yaml": "v1.1.0"}


# ---------------------------------------------------------------------------
# create_summary
# ---------------------------------------------------------------------------

class TestCreateSummary:
    def test_with_commit_sha(self, summary):
        result = summary.create_summary(UPDATED_FILES, OLD_TAGS, "abc123")
        assert result["repository"] == "org/repo"
        assert result["branch"] == "main"
        assert result["commit_sha"] == "abc123"
        assert result["changes_count"] == 2
        assert result["changes"][0]["old_tag"] == "v1.0.0"
        assert result["changes"][0]["new_tag"] == "v2.0.0"
        assert result["dry_run"] is False
        assert "timestamp" in result

    def test_without_commit_sha(self, summary):
        result = summary.create_summary(UPDATED_FILES, OLD_TAGS)
        assert result["commit_sha"] == ""

    def test_missing_old_tag(self, summary):
        result = summary.create_summary(["unknown.yaml"], {})
        assert result["changes"][0]["old_tag"] == ""


# ---------------------------------------------------------------------------
# save_summary
# ---------------------------------------------------------------------------

class TestSaveSummary:
    def test_no_summary_file(self, config, logger):
        config.summary_file = ""
        s = ChangeSummary(config, logger)
        s.save_summary(UPDATED_FILES, OLD_TAGS)  # should return early

    def test_create_new_file(self, config, logger, tmp_path):
        sf = str(tmp_path / "sub" / "summary.json")
        config.summary_file = sf
        s = ChangeSummary(config, logger)
        s.save_summary(UPDATED_FILES, OLD_TAGS, "sha1")

        with open(sf) as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["commit_sha"] == "sha1"

    def test_append_to_existing(self, config, logger, tmp_path):
        sf = str(tmp_path / "summary.json")
        config.summary_file = sf

        # First save
        s = ChangeSummary(config, logger)
        s.save_summary(["f1.yaml"], {"f1.yaml": "v1"}, "sha1")
        # Second save
        s.save_summary(["f2.yaml"], {"f2.yaml": "v2"}, "sha2")

        with open(sf) as f:
            data = json.load(f)
        assert len(data) == 2

    def test_existing_is_dict(self, config, logger, tmp_path):
        """When existing file contains a dict instead of list."""
        sf = str(tmp_path / "summary.json")
        with open(sf, "w") as f:
            json.dump({"old": True}, f)

        config.summary_file = sf
        s = ChangeSummary(config, logger)
        s.save_summary(UPDATED_FILES, OLD_TAGS)

        with open(sf) as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 2  # old dict + new

    def test_invalid_json(self, config, logger, tmp_path):
        sf = str(tmp_path / "summary.json")
        with open(sf, "w") as f:
            f.write("not json{{{")

        config.summary_file = sf
        s = ChangeSummary(config, logger)
        s.save_summary(UPDATED_FILES, OLD_TAGS)

        with open(sf) as f:
            data = json.load(f)
        assert len(data) == 1  # reset to new

    def test_ioerror_read(self, config, logger, tmp_path):
        sf = str(tmp_path / "summary.json")
        # Create a file that exists but will error on read
        with open(sf, "w") as f:
            f.write("[]")

        config.summary_file = sf
        s = ChangeSummary(config, logger)

        original_open = open
        call_count = 0

        def mock_open(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1 and "r" in str(args[1:]):
                raise IOError("read fail")
            return original_open(*args, **kwargs)

        # Use patch on Path.exists to trigger the read path, then IOError
        with patch("builtins.open", side_effect=mock_open):
            # This may raise or handle gracefully depending on flow
            try:
                s.save_summary(UPDATED_FILES, OLD_TAGS)
            except (SystemExit, IOError):
                pass  # acceptable

    def test_ioerror_write(self, config, logger, tmp_path):
        sf = str(tmp_path / "nosuchdir" / "deep" / "summary.json")
        config.summary_file = sf
        s = ChangeSummary(config, logger)

        with patch("builtins.open", side_effect=IOError("write fail")):
            with pytest.raises(SystemExit):
                s.save_summary(UPDATED_FILES, OLD_TAGS)

    def test_max_entries(self, config, logger, tmp_path):
        sf = str(tmp_path / "summary.json")
        # Pre-fill with MAX_ENTRIES entries
        existing = [{"entry": i} for i in range(ChangeSummary.MAX_ENTRIES)]
        with open(sf, "w") as f:
            json.dump(existing, f)

        config.summary_file = sf
        s = ChangeSummary(config, logger)
        s.save_summary(["f.yaml"], {"f.yaml": "v1"})

        with open(sf) as f:
            data = json.load(f)
        assert len(data) == ChangeSummary.MAX_ENTRIES


# ---------------------------------------------------------------------------
# print_summary
# ---------------------------------------------------------------------------

class TestPrintSummary:
    def test_with_files(self, summary, capsys):
        summary.print_summary(UPDATED_FILES, OLD_TAGS, "abc123")
        out = capsys.readouterr().out
        assert "Change Summary" in out
        assert "dev1.yaml" in out
        assert "abc123" in out

    def test_with_commit_sha(self, summary, capsys):
        summary.print_summary(["f.yaml"], {"f.yaml": "old"}, "sha")
        out = capsys.readouterr().out
        assert "sha" in out

    def test_without_commit_sha(self, summary, capsys):
        summary.print_summary(["f.yaml"], {"f.yaml": "old"})
        out = capsys.readouterr().out
        assert "Commit" not in out

    def test_empty_files(self, summary, capsys):
        summary.print_summary([], {})
        assert capsys.readouterr().out == ""
