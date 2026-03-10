"""Tests for src/git_operations.py"""
import subprocess
import pytest
from unittest.mock import patch, MagicMock, call

from src.config import Config
from src.git_operations import GitOperations
from src.logger import Logger


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    return Config(
        target_path="/tmp",
        new_tag="v2.0.0",
        tag_string="tag",
        git_user_name="bot",
        git_user_email="bot@ci.com",
        github_token="ghp_xxx",
        repo="org/repo",
        branch="main",
        target_values_file="values.yaml",
        max_retries=2,
    )


@pytest.fixture
def logger():
    return Logger(debug=False)


@pytest.fixture
def debug_logger():
    return Logger(debug=True)


@pytest.fixture
def git_ops(config, logger):
    return GitOperations(config, logger)


@pytest.fixture
def debug_git_ops(config, debug_logger):
    cfg = Config(
        target_path="/tmp",
        new_tag="v2.0.0",
        tag_string="tag",
        git_user_name="bot",
        git_user_email="bot@ci.com",
        github_token="ghp_xxx",
        repo="org/repo",
        branch="main",
        target_values_file="values.yaml",
        max_retries=2,
        debug=True,
    )
    return GitOperations(cfg, debug_logger)


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------

class TestRunCommand:
    def test_success(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="ok\n", stderr="", returncode=0)
            result = git_ops.run_command(["git", "status"])
            assert result is None
            mock_run.assert_called_once()

    def test_capture(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="abc123\n", stderr="", returncode=0)
            result = git_ops.run_command(["git", "rev-parse", "HEAD"], capture=True)
            assert result == "abc123"

    def test_show_output(self, git_ops, capsys):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="visible\n", stderr="err\n", returncode=0)
            git_ops.run_command(["echo"], show_output=True)
            out = capsys.readouterr()
            assert "visible" in out.out
            assert "err" in out.err

    def test_debug_output(self, debug_git_ops, capsys):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="debug-out\n", stderr="", returncode=0)
            debug_git_ops.run_command(["echo"])
            out = capsys.readouterr().out
            assert "debug-out" in out

    def test_failure_with_check(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="error msg")
            with pytest.raises(SystemExit):
                git_ops.run_command(["git", "bad-cmd"], check=True)

    def test_failure_without_check(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="")
            result = git_ops.run_command(["git", "bad-cmd"], check=False)
            assert result is None

    def test_failure_no_stderr(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(128, "git", stderr="")
            with pytest.raises(SystemExit):
                git_ops.run_command(["git", "fail"], check=True)


# ---------------------------------------------------------------------------
# configure_git
# ---------------------------------------------------------------------------

class TestConfigureGit:
    def test_runs_all_commands(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd:
            git_ops.configure_git()
            assert mock_cmd.call_count == 5


# ---------------------------------------------------------------------------
# branch_exists_locally / remotely
# ---------------------------------------------------------------------------

class TestBranchExists:
    def test_local_exists(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert git_ops.branch_exists_locally("main") is True

    def test_local_not_exists(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert git_ops.branch_exists_locally("feature") is False

    def test_local_exception(self, git_ops):
        with patch("subprocess.run", side_effect=Exception("fail")):
            assert git_ops.branch_exists_locally("x") is False

    def test_remote_exists(self, git_ops):
        with patch.object(git_ops, "run_command", return_value="abc123 refs/heads/main"):
            assert git_ops.branch_exists_remotely("main") is True

    def test_remote_not_exists(self, git_ops):
        with patch.object(git_ops, "run_command", return_value=""):
            assert git_ops.branch_exists_remotely("feature") is False

    def test_remote_none(self, git_ops):
        with patch.object(git_ops, "run_command", return_value=None):
            assert git_ops.branch_exists_remotely("x") is False


# ---------------------------------------------------------------------------
# check_branch_existence
# ---------------------------------------------------------------------------

class TestCheckBranchExistence:
    def test_both(self, git_ops):
        with patch.object(git_ops, "branch_exists_locally", return_value=True), \
             patch.object(git_ops, "branch_exists_remotely", return_value=False):
            local, remote = git_ops.check_branch_existence("main")
            assert local is True
            assert remote is False


# ---------------------------------------------------------------------------
# setup_branch
# ---------------------------------------------------------------------------

class TestSetupBranch:
    def test_local_branch_current(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch.object(git_ops, "branch_exists_locally", return_value=True), \
             patch.object(git_ops, "branch_exists_remotely", return_value=True):
            mock_cmd.side_effect = [None, "main", None]  # fetch, show-current, pull
            git_ops.setup_branch()

    def test_local_branch_switch(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch.object(git_ops, "branch_exists_locally", return_value=True), \
             patch.object(git_ops, "branch_exists_remotely", return_value=False):
            mock_cmd.side_effect = [None, "other-branch", None]  # fetch, show-current, checkout
            git_ops.setup_branch()

    def test_remote_only(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch.object(git_ops, "branch_exists_locally", return_value=False), \
             patch.object(git_ops, "branch_exists_remotely", return_value=True):
            mock_cmd.side_effect = [None, "other", None, None]  # fetch, current, checkout -b, pull
            git_ops.setup_branch()

    def test_new_branch(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch.object(git_ops, "branch_exists_locally", return_value=False), \
             patch.object(git_ops, "branch_exists_remotely", return_value=False):
            mock_cmd.side_effect = [None, "other", None]  # fetch, current, checkout -b
            git_ops.setup_branch()


# ---------------------------------------------------------------------------
# has_staged_changes
# ---------------------------------------------------------------------------

class TestHasStagedChanges:
    def test_has_changes(self, git_ops):
        with patch.object(git_ops, "run_command", return_value=None):
            assert git_ops.has_staged_changes() is True

    def test_no_changes(self, git_ops):
        with patch.object(git_ops, "run_command", return_value=""):
            assert git_ops.has_staged_changes() is False


# ---------------------------------------------------------------------------
# commit_and_push
# ---------------------------------------------------------------------------

class TestCommitAndPush:
    def test_success(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch.object(git_ops, "has_staged_changes", return_value=True), \
             patch.object(git_ops, "_push_with_retry"):
            mock_cmd.side_effect = [None, None, "abc123def"]  # add, commit, rev-parse
            sha = git_ops.commit_and_push("values.yaml")
            assert sha == "abc123def"

    def test_no_changes(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch.object(git_ops, "has_staged_changes", return_value=False):
            mock_cmd.return_value = None
            sha = git_ops.commit_and_push("values.yaml")
            assert sha is None


# ---------------------------------------------------------------------------
# _push_with_retry
# ---------------------------------------------------------------------------

class TestPushWithRetry:
    def test_success_first_attempt(self, git_ops):
        with patch.object(git_ops, "run_command"):
            git_ops._push_with_retry()

    def test_retry_then_success(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch("time.sleep"):
            mock_cmd.side_effect = [Exception("fail"), None]
            git_ops._push_with_retry()

    def test_all_retries_fail(self, git_ops):
        with patch.object(git_ops, "run_command") as mock_cmd, \
             patch("time.sleep"):
            mock_cmd.side_effect = [Exception("fail")] * 2
            with pytest.raises(SystemExit):
                git_ops._push_with_retry()
