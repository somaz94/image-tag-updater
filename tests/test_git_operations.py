"""Tests for src/git_operations.py"""

import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.config import Config
from src.git_operations import GitOperations, add_config_env
from src.logger import ActionError, Logger


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


class TestRunCommand:
    def test_success(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="ok\n", stderr="", returncode=0)
            result = git_ops.run_command(["git", "status"])
            assert result is None
            mock_run.assert_called_once()

    def test_capture(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="abc123\n", stderr="", returncode=0
            )
            result = git_ops.run_command(["git", "rev-parse", "HEAD"], capture=True)
            assert result == "abc123"

    def test_show_output(self, git_ops, capsys):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="visible\n", stderr="err\n", returncode=0
            )
            git_ops.run_command(["echo"], show_output=True)
            out = capsys.readouterr()
            assert "visible" in out.out
            assert "err" in out.err

    def test_debug_output(self, debug_git_ops, capsys):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="debug-out\n", stderr="", returncode=0
            )
            debug_git_ops.run_command(["echo"])
            out = capsys.readouterr().out
            assert "debug-out" in out

    def test_failure_with_check(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="error msg"
            )
            with pytest.raises(ActionError):
                git_ops.run_command(["git", "bad-cmd"], check=True)

    def test_failure_no_stderr(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(128, "git", stderr="")
            with pytest.raises(ActionError):
                git_ops.run_command(["git", "fail"], check=True)


@pytest.fixture
def git_env():
    with patch.dict(os.environ):
        for key in [k for k in os.environ if k.startswith("GIT_CONFIG_")]:
            del os.environ[key]
        yield os.environ


def env_config(env):
    return [
        (env[f"GIT_CONFIG_KEY_{i}"], env[f"GIT_CONFIG_VALUE_{i}"])
        for i in range(int(env["GIT_CONFIG_COUNT"]))
    ]


class TestAddConfigEnv:
    def test_first_entry(self, git_env):
        add_config_env("safe.directory", "/repo")
        assert env_config(git_env) == [("safe.directory", "/repo")]

    def test_appends_after_existing_entries(self, git_env):
        git_env.update(
            GIT_CONFIG_COUNT="1",
            GIT_CONFIG_KEY_0="core.pager",
            GIT_CONFIG_VALUE_0="cat",
        )
        add_config_env("user.name", "bot")
        assert env_config(git_env) == [("core.pager", "cat"), ("user.name", "bot")]

    @pytest.mark.parametrize("count", ["abc", "-1"])
    def test_invalid_count(self, git_env, count):
        git_env["GIT_CONFIG_COUNT"] = count
        with pytest.raises(ValueError):
            add_config_env("user.name", "bot")


class TestConfigureGit:
    def test_sets_process_env_without_running_git(self, git_ops, git_env):
        with patch.object(git_ops, "run_command") as mock_cmd:
            git_ops.configure_git()
        mock_cmd.assert_not_called()
        assert env_config(git_env) == [
            ("safe.directory", "/usr/src"),
            ("safe.directory", "/github/workspace"),
            ("user.name", git_ops.config.git_user_name),
            ("user.email", git_ops.config.git_user_email),
            ("pull.rebase", "false"),
        ]


class TestBranchExists:
    def test_local_exists(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert git_ops.branch_exists_locally("main") is True

    def test_local_not_exists(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert git_ops.branch_exists_locally("feature") is False

    def test_local_git_missing_propagates(self, git_ops):
        with (
            patch("subprocess.run", side_effect=FileNotFoundError("git")),
            pytest.raises(FileNotFoundError),
        ):
            git_ops.branch_exists_locally("x")

    def test_remote_exists(self, git_ops):
        with patch.object(
            git_ops, "run_command", return_value="abc123 refs/heads/main"
        ):
            assert git_ops.branch_exists_remotely("main") is True

    def test_remote_not_exists(self, git_ops):
        with patch.object(git_ops, "run_command", return_value=""):
            assert git_ops.branch_exists_remotely("feature") is False

    def test_remote_none(self, git_ops):
        with patch.object(git_ops, "run_command", return_value=None):
            assert git_ops.branch_exists_remotely("x") is False


class TestCheckBranchExistence:
    def test_both(self, git_ops):
        with (
            patch.object(git_ops, "branch_exists_locally", return_value=True),
            patch.object(git_ops, "branch_exists_remotely", return_value=False),
        ):
            local, remote = git_ops.check_branch_existence("main")
            assert local is True
            assert remote is False


class TestSetupBranch:
    def test_local_branch_current(self, git_ops):
        with (
            patch.object(git_ops, "run_command") as mock_cmd,
            patch.object(git_ops, "branch_exists_locally", return_value=True),
            patch.object(git_ops, "branch_exists_remotely", return_value=True),
        ):
            mock_cmd.side_effect = [None, "main", None]  # fetch, show-current, pull
            git_ops.setup_branch()

    def test_local_branch_switch(self, git_ops):
        with (
            patch.object(git_ops, "run_command") as mock_cmd,
            patch.object(git_ops, "branch_exists_locally", return_value=True),
            patch.object(git_ops, "branch_exists_remotely", return_value=False),
        ):
            mock_cmd.side_effect = [
                None,
                "other-branch",
                None,
            ]  # fetch, show-current, checkout
            git_ops.setup_branch()

    def test_remote_only(self, git_ops):
        with (
            patch.object(git_ops, "run_command") as mock_cmd,
            patch.object(git_ops, "branch_exists_locally", return_value=False),
            patch.object(git_ops, "branch_exists_remotely", return_value=True),
        ):
            mock_cmd.side_effect = [
                None,
                "other",
                None,
                None,
            ]  # fetch, current, checkout -b, pull
            git_ops.setup_branch()

    def test_new_branch(self, git_ops):
        with (
            patch.object(git_ops, "run_command") as mock_cmd,
            patch.object(git_ops, "branch_exists_locally", return_value=False),
            patch.object(git_ops, "branch_exists_remotely", return_value=False),
        ):
            mock_cmd.side_effect = [None, "other", None]  # fetch, current, checkout -b
            git_ops.setup_branch()


class TestHasStagedChanges:
    def test_has_changes(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert git_ops.has_staged_changes() is True

    def test_no_changes(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert git_ops.has_staged_changes() is False

    def test_git_missing_propagates(self, git_ops):
        with (
            patch("subprocess.run", side_effect=FileNotFoundError("git")),
            pytest.raises(FileNotFoundError),
        ):
            git_ops.has_staged_changes()


class TestCommitAndPush:
    def test_success(self, git_ops):
        with (
            patch.object(git_ops, "run_command") as mock_cmd,
            patch.object(git_ops, "has_staged_changes", return_value=True),
            patch.object(git_ops, "_push_with_retry"),
        ):
            mock_cmd.side_effect = [None, None, "abc123def"]  # add, commit, rev-parse
            sha = git_ops.commit_and_push("values.yaml")
            assert sha == "abc123def"

    def test_no_changes(self, git_ops):
        with (
            patch.object(git_ops, "run_command") as mock_cmd,
            patch.object(git_ops, "has_staged_changes", return_value=False),
        ):
            mock_cmd.return_value = None
            sha = git_ops.commit_and_push("values.yaml")
            assert sha is None


class TestPushWithRetry:
    def test_success_first_attempt(self, git_ops):
        with patch.object(git_ops, "_push_once"):
            git_ops._push_with_retry()

    def test_retry_then_success(self, git_ops):
        with patch.object(git_ops, "_push_once") as mock_push, patch("time.sleep"):
            mock_push.side_effect = [ActionError("fail"), None]
            git_ops._push_with_retry()

    def test_all_retries_fail(self, git_ops):
        with patch.object(git_ops, "_push_once") as mock_push, patch("time.sleep"):
            mock_push.side_effect = [ActionError("fail")] * 2
            with pytest.raises(ActionError, match="Failed to push"):
                git_ops._push_with_retry()

    def test_push_once_success(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            git_ops._push_once("https://example.com/repo")

    def test_push_once_failure(self, git_ops):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="rejected")
            with pytest.raises(ActionError, match="rejected"):
                git_ops._push_once("https://example.com/repo")
