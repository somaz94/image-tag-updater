"""Tests for main.py"""
import os
import pytest
from unittest.mock import patch, MagicMock

from main import write_output, main


# ---------------------------------------------------------------------------
# write_output
# ---------------------------------------------------------------------------

class TestWriteOutput:
    def test_with_github_output(self, tmp_path):
        output_file = str(tmp_path / "output")
        with patch.dict(os.environ, {"GITHUB_OUTPUT": output_file}):
            write_output("key", "value")

        with open(output_file) as f:
            content = f.read()
        assert "key<<EOF" in content
        assert "value" in content
        assert content.strip().endswith("EOF")

    def test_without_github_output(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GITHUB_OUTPUT", None)
            write_output("key", "value")  # should not raise

    def test_multiple_outputs(self, tmp_path):
        output_file = str(tmp_path / "output")
        with patch.dict(os.environ, {"GITHUB_OUTPUT": output_file}):
            write_output("k1", "v1")
            write_output("k2", "v2")

        with open(output_file) as f:
            content = f.read()
        assert "k1" in content
        assert "k2" in content


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

class TestMain:
    def _env(self, tmpdir, **overrides):
        base = {
            "TARGET_PATH": tmpdir,
            "NEW_TAG": "v2.0.0",
            "TAG_STRING": "tag",
            "GIT_USER_NAME": "bot",
            "GIT_USER_EMAIL": "bot@ci.com",
            "GITHUB_TOKEN": "ghp_xxx",
            "REPO": "org/repo",
            "BRANCH": "main",
            "TARGET_VALUES_FILE": "values.yaml",
            "FILE_PATTERN": "",
            "BACKUP": "false",
            "DRY_RUN": "true",
            "DEBUG": "false",
            "TAG_PREFIX": "",
            "TAG_SUFFIX": "",
            "UPDATE_IF_CONTAINS": "",
            "SKIP_IF_CONTAINS": "",
            "SUMMARY_FILE": "",
            "COMMIT_MESSAGE": "Update",
        }
        base.update(overrides)
        return base

    @patch("main.GitOperations")
    def test_dry_run_success(self, mock_git_cls, tmp_path):
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        github_output = str(tmp_path / "github_output")

        env = self._env(str(tmp_path), GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            main()

        with open(github_output) as f:
            content = f.read()
        assert "changes_made" in content

    @patch("main.GitOperations")
    def test_no_changes(self, mock_git_cls, tmp_path):
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v2.0.0"\n')
        github_output = str(tmp_path / "github_output")

        env = self._env(str(tmp_path), GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            main()

        with open(github_output) as f:
            content = f.read()
        assert "false" in content

    def test_missing_required_field(self, tmp_path):
        env = self._env(str(tmp_path), TARGET_PATH="")
        with patch.dict(os.environ, env, clear=False):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_debug_mode_error(self, tmp_path):
        env = self._env(str(tmp_path), DEBUG="true", TARGET_VALUES_FILE="nonexistent.yaml")
        values = tmp_path / "nonexistent.yaml"
        # Don't create the file, so file_processor will fail
        with patch.dict(os.environ, env, clear=False):
            with pytest.raises(SystemExit):
                main()

    @patch("main.GitOperations")
    def test_dry_run_with_summary_file(self, mock_git_cls, tmp_path):
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        summary_file = str(tmp_path / "summary.json")
        github_output = str(tmp_path / "github_output")

        env = self._env(str(tmp_path), GITHUB_OUTPUT=github_output, SUMMARY_FILE=summary_file)
        with patch.dict(os.environ, env, clear=False):
            main()

        assert os.path.exists(summary_file)

    @patch("main.GitOperations")
    def test_actual_run_with_changes(self, mock_git_cls, tmp_path):
        """Non-dry-run: should commit and push via mocked git ops."""
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        github_output = str(tmp_path / "github_output")

        mock_git = MagicMock()
        mock_git.commit_and_push.return_value = "abc123def4567890"
        mock_git_cls.return_value = mock_git

        env = self._env(str(tmp_path), DRY_RUN="false", GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            main()

        mock_git.commit_and_push.assert_called_once()
        with open(github_output) as f:
            content = f.read()
        assert "abc123d" in content  # short sha

    @patch("main.GitOperations")
    def test_debug_mode_directory_listing(self, mock_git_cls, tmp_path):
        """Debug mode should list directory contents."""
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        github_output = str(tmp_path / "github_output")

        env = self._env(str(tmp_path), DEBUG="true", GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            main()

    @patch("main.GitOperations")
    def test_non_dry_run_no_changes(self, mock_git_cls, tmp_path):
        """Non-dry-run with same tag should exit without commit."""
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v2.0.0"\n')
        github_output = str(tmp_path / "github_output")

        env = self._env(str(tmp_path), DRY_RUN="false", GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            main()

        mock_git_cls.return_value.commit_and_push.assert_not_called()
        with open(github_output) as f:
            content = f.read()
        assert "false" in content

    @patch("main.GitOperations")
    def test_actual_run_with_summary_file(self, mock_git_cls, tmp_path):
        """Non-dry-run with summary file should save summary with commit SHA."""
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        summary_file = str(tmp_path / "summary.json")
        github_output = str(tmp_path / "github_output")

        mock_git = MagicMock()
        mock_git.commit_and_push.return_value = "abc123def4567890"
        mock_git_cls.return_value = mock_git

        env = self._env(str(tmp_path), DRY_RUN="false", GITHUB_OUTPUT=github_output, SUMMARY_FILE=summary_file)
        with patch.dict(os.environ, env, clear=False):
            main()

        assert os.path.exists(summary_file)

    @patch("main.GitOperations")
    def test_actual_run_commit_returns_none(self, mock_git_cls, tmp_path):
        """Non-dry-run where commit_and_push returns None (no staged changes)."""
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        github_output = str(tmp_path / "github_output")

        mock_git = MagicMock()
        mock_git.commit_and_push.return_value = None
        mock_git_cls.return_value = mock_git

        env = self._env(str(tmp_path), DRY_RUN="false", GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            main()

        with open(github_output) as f:
            content = f.read()
        # commit_sha should be empty string
        assert "commit_sha<<EOF" in content

    @patch("main.GitOperations")
    def test_unexpected_exception(self, mock_git_cls, tmp_path):
        """Unexpected exception should be caught and exit with code 1."""
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        github_output = str(tmp_path / "github_output")

        mock_git_cls.side_effect = RuntimeError("unexpected")

        env = self._env(str(tmp_path), GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("main.GitOperations")
    def test_unexpected_exception_debug(self, mock_git_cls, tmp_path):
        """Unexpected exception in debug mode should print traceback."""
        values = tmp_path / "values.yaml"
        values.write_text('image:\n  tag: "v1.0.0"\n')
        github_output = str(tmp_path / "github_output")

        mock_git_cls.side_effect = RuntimeError("unexpected debug")

        env = self._env(str(tmp_path), DEBUG="true", GITHUB_OUTPUT=github_output)
        with patch.dict(os.environ, env, clear=False):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
