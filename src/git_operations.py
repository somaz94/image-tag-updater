"""Git operations for image tag updater."""

from __future__ import annotations

import os
import subprocess
import sys
import time

from .config import Config
from .logger import ActionError, Logger


def add_config_env(key: str, value: str) -> None:
    """Append key=value to the git config that child git processes read from the environment.

    Git treats GIT_CONFIG_COUNT/KEY/VALUE as command-scope config, so safe.directory
    is honoured and ~/.gitconfig is never touched.
    """
    count = int(os.environ.get("GIT_CONFIG_COUNT", "0"))
    if count < 0:
        raise ValueError(f"Invalid GIT_CONFIG_COUNT: {count}")
    os.environ[f"GIT_CONFIG_KEY_{count}"] = key
    os.environ[f"GIT_CONFIG_VALUE_{count}"] = value
    os.environ["GIT_CONFIG_COUNT"] = str(count + 1)


class GitOperations:
    """Handle Git operations."""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def run_command(
        self,
        cmd: list[str],
        check: bool = True,
        capture: bool = False,
        show_output: bool = False,
    ) -> str | None:
        """Run a command; with check=True a non-zero exit logs and raises ActionError.

        Args:
            cmd: Command and arguments to run
            check: Whether to raise exception on non-zero exit
            capture: Whether to capture and return stdout
            show_output: Show stdout/stderr even when debug mode is off

        Returns:
            str | None: Stripped stdout if capture=True, None otherwise
        """
        self.logger.debug(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)

            if show_output or self.config.debug:
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)

            if capture:
                return result.stdout.strip()

            return None

        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(cmd)}\n"
            error_msg += f"Exit code: {e.returncode}\n"
            if e.stderr:
                error_msg += f"Error: {e.stderr}"
            self.logger.error(error_msg)

    def configure_git(self) -> None:
        """Configure Git for this process only; no git config file is written."""
        self.logger.debug("\nConfiguring Git...")

        settings = [
            ("safe.directory", "/usr/src"),
            ("safe.directory", "/github/workspace"),
            ("user.name", self.config.git_user_name),
            ("user.email", self.config.git_user_email),
            ("pull.rebase", "false"),
        ]
        for key, value in settings:
            add_config_env(key, value)

    def branch_exists_locally(self, branch: str) -> bool:
        """Check if branch exists locally."""
        result = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0

    def branch_exists_remotely(self, branch: str) -> bool:
        """Check if branch exists on remote."""
        output = self.run_command(
            ["git", "ls-remote", "--heads", "origin", branch], capture=True
        )
        return branch in (output or "")

    def check_branch_existence(self, branch: str) -> tuple[bool, bool]:
        """Check if branch exists locally and remotely.

        Args:
            branch: Branch name to check

        Returns:
            tuple[bool, bool]: (exists_locally, exists_remotely)
        """
        local = self.branch_exists_locally(branch)
        remote = self.branch_exists_remotely(branch)
        return local, remote

    def setup_branch(self) -> None:
        """Setup Git branch."""
        self.logger.debug(f"\nSetting up branch: {self.config.branch}")

        self.run_command(["git", "fetch", "origin"])

        current_branch = self.run_command(
            ["git", "branch", "--show-current"], capture=True
        )

        if self.branch_exists_locally(self.config.branch):
            if current_branch != self.config.branch:
                self.logger.debug(f"Switching to existing branch: {self.config.branch}")
                self.run_command(["git", "checkout", self.config.branch])

            if self.branch_exists_remotely(self.config.branch):
                self.logger.debug("\nPulling latest changes...")
                self.run_command(["git", "pull", "origin", self.config.branch])
        else:
            if self.branch_exists_remotely(self.config.branch):
                self.logger.debug(f"Checking out remote branch: {self.config.branch}")
                self.run_command(
                    [
                        "git",
                        "checkout",
                        "-b",
                        self.config.branch,
                        f"origin/{self.config.branch}",
                    ]
                )
                self.logger.debug("\nPulling latest changes...")
                self.run_command(["git", "pull", "origin", self.config.branch])
            else:
                self.logger.debug(f"Creating new local branch: {self.config.branch}")
                self.run_command(["git", "checkout", "-b", self.config.branch])

    def has_staged_changes(self) -> bool:
        """Check if there are staged changes.

        Calls subprocess directly: run_command() drops the exit code, and
        `git diff --cached --quiet` signals changes with exit 1.
        """
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
            check=False,
        )
        return result.returncode != 0

    def commit_and_push(self, file_info: str) -> str | None:
        """Commit and push changes. Returns commit SHA or None."""
        self.logger.debug("\nStaging changes...")
        self.run_command(["git", "add", "."])

        if not self.has_staged_changes():
            self.logger.info("\n[O] No changes to commit. Nothing to push.")
            return None

        commit_msg = (
            f"{self.config.commit_message} {self.config.target_path} ({file_info})"
        )

        self.logger.debug("\nCreating commit...")
        self.run_command(["git", "commit", "-m", commit_msg])

        commit_sha = self.run_command(["git", "rev-parse", "HEAD"], capture=True)

        self._push_with_retry()

        return commit_sha

    def _push_with_retry(self) -> None:
        """Push changes with retry logic."""
        remote_url = f"https://x-access-token:{self.config.github_token}@github.com/{self.config.repo}"

        for attempt in range(1, self.config.max_retries + 1):
            try:
                self._push_once(remote_url)
                self.logger.success(
                    f"Successfully pushed changes to {self.config.branch}"
                )
                return
            except ActionError as e:
                if attempt == self.config.max_retries:
                    raise ActionError(
                        f"Failed to push changes after {self.config.max_retries} attempts: {e}"
                    ) from e
                self.logger.warning(
                    f"Push failed, retrying... (Attempt {attempt} of {self.config.max_retries})"
                )
                time.sleep(5)

    def _push_once(self, remote_url: str) -> None:
        """Execute a single push attempt without triggering logger.error()."""
        result = subprocess.run(
            ["git", "push", remote_url, self.config.branch],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            error_msg = (
                result.stderr.strip()
                or f"git push exited with code {result.returncode}"
            )
            raise ActionError(error_msg)
