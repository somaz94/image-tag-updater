"""Git operations for image tag updater."""
import subprocess
import time
from typing import List, Optional

from .config import Config
from .logger import Logger


class GitOperations:
    """Handle Git operations."""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
    
    def run_command(self, cmd: List[str], check: bool = True, capture: bool = False) -> Optional[str]:
        """Run a shell command."""
        try:
            self.logger.debug(f"Running: {' '.join(cmd)}")
            if capture:
                result = subprocess.run(
                    cmd,
                    check=check,
                    capture_output=True,
                    text=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(
                    cmd,
                    check=check,
                    stdout=subprocess.DEVNULL if not self.config.debug else None,
                    stderr=subprocess.DEVNULL if not self.config.debug else None
                )
                return None
        except subprocess.CalledProcessError as e:
            if check:
                self.logger.error(f"Command failed: {' '.join(cmd)}\n{e}")
            return None
    
    def configure_git(self) -> None:
        """Configure Git settings."""
        self.logger.debug("\nConfiguring Git...")
        
        commands = [
            ["git", "config", "--global", "--add", "safe.directory", "/usr/src"],
            ["git", "config", "--global", "--add", "safe.directory", "/github/workspace"],
            ["git", "config", "--global", "user.name", self.config.git_user_name],
            ["git", "config", "--global", "user.email", self.config.git_user_email],
            ["git", "config", "--global", "pull.rebase", "false"],
        ]
        
        for cmd in commands:
            self.run_command(cmd)
    
    def branch_exists_locally(self, branch: str) -> bool:
        """Check if branch exists locally."""
        try:
            result = subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
                capture_output=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def branch_exists_remotely(self, branch: str) -> bool:
        """Check if branch exists on remote."""
        output = self.run_command(
            ["git", "ls-remote", "--heads", "origin", branch],
            capture=True
        )
        return branch in (output or "")
    
    def setup_branch(self) -> None:
        """Setup Git branch."""
        self.logger.debug(f"\nSetting up branch: {self.config.branch}")
        
        # Fetch from remote
        self.run_command(["git", "fetch", "origin"])
        
        # Check current branch
        current_branch = self.run_command(["git", "branch", "--show-current"], capture=True)
        
        if self.branch_exists_locally(self.config.branch):
            # Branch exists locally
            if current_branch != self.config.branch:
                self.logger.debug(f"Switching to existing branch: {self.config.branch}")
                self.run_command(["git", "checkout", self.config.branch])
            
            # Pull if remote branch exists
            if self.branch_exists_remotely(self.config.branch):
                self.logger.debug("\nPulling latest changes...")
                self.run_command(["git", "pull", "origin", self.config.branch])
        else:
            # Branch doesn't exist locally
            if self.branch_exists_remotely(self.config.branch):
                # Remote branch exists, checkout and track it
                self.logger.debug(f"Checking out remote branch: {self.config.branch}")
                self.run_command(["git", "checkout", "-b", self.config.branch, f"origin/{self.config.branch}"])
                self.logger.debug("\nPulling latest changes...")
                self.run_command(["git", "pull", "origin", self.config.branch])
            else:
                # Create new branch locally
                self.logger.debug(f"Creating new local branch: {self.config.branch}")
                self.run_command(["git", "checkout", "-b", self.config.branch])
    
    def has_staged_changes(self) -> bool:
        """Check if there are staged changes."""
        result = self.run_command(
            ["git", "diff", "--cached", "--quiet"],
            check=False
        )
        # git diff --quiet returns 0 if no changes, 1 if changes exist
        return result is None
    
    def commit_and_push(self, file_info: str) -> Optional[str]:
        """Commit and push changes. Returns commit SHA or None."""
        self.logger.debug("\nStaging changes...")
        self.run_command(["git", "add", "."])
        
        # Check if there are staged changes
        if not self.has_staged_changes():
            self.logger.info("\n✅ No changes to commit. Nothing to push.")
            return None
        
        # Create commit message
        commit_msg = f"{self.config.commit_message} {self.config.target_path} ({file_info})"
        
        self.logger.debug("\nCreating commit...")
        self.run_command(["git", "commit", "-m", commit_msg])
        
        # Get commit SHA
        commit_sha = self.run_command(["git", "rev-parse", "HEAD"], capture=True)
        
        # Push changes with retry logic
        self._push_with_retry()
        
        return commit_sha
    
    def _push_with_retry(self) -> None:
        """Push changes with retry logic."""
        remote_url = f"https://x-access-token:{self.config.github_token}@github.com/{self.config.repo}"
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                self.run_command(["git", "push", remote_url, self.config.branch])
                self.logger.success(f"Successfully pushed changes to {self.config.branch}")
                return
            except Exception:
                if attempt == self.config.max_retries:
                    self.logger.error(f"Failed to push changes after {self.config.max_retries} attempts")
                self.logger.warning(f"Push failed, retrying... (Attempt {attempt} of {self.config.max_retries})")
                time.sleep(5)
