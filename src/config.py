"""Configuration management for image tag updater."""
import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration class for image tag updater."""
    
    target_path: str
    new_tag: str
    tag_string: str
    git_user_name: str
    git_user_email: str
    github_token: str
    repo: str
    branch: str
    commit_message: str = "Update image tag"
    target_values_file: Optional[str] = None
    file_pattern: Optional[str] = None
    backup: bool = False
    dry_run: bool = False
    debug: bool = False
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            target_path=os.getenv("TARGET_PATH", ""),
            new_tag=os.getenv("NEW_TAG", ""),
            tag_string=os.getenv("TAG_STRING", ""),
            git_user_name=os.getenv("GIT_USER_NAME", ""),
            git_user_email=os.getenv("GIT_USER_EMAIL", ""),
            github_token=os.getenv("GITHUB_TOKEN", ""),
            repo=os.getenv("REPO", ""),
            branch=os.getenv("BRANCH", ""),
            commit_message=os.getenv("COMMIT_MESSAGE", "Update image tag"),
            target_values_file=os.getenv("TARGET_VALUES_FILE"),
            file_pattern=os.getenv("FILE_PATTERN"),
            backup=os.getenv("BACKUP", "false").lower() == "true",
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
            debug=os.getenv("DEBUG", "false").lower() == "true",
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        required_fields = [
            "target_path", "new_tag", "tag_string",
            "git_user_name", "git_user_email", "github_token",
            "repo", "branch"
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Required field '{field}' is not set")
        
        # Validate tag format
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$', self.new_tag):
            raise ValueError(
                f"Invalid tag format: {self.new_tag}. "
                "Tags should only contain alphanumeric characters, dots, underscores, and hyphens."
            )
        
        # Check if at least one of target_values_file or file_pattern is set
        if not self.target_values_file and not self.file_pattern:
            raise ValueError("Either target_values_file or file_pattern must be set")
        
        # Check if both are set (not allowed)
        if self.target_values_file and self.file_pattern:
            raise ValueError("Cannot set both target_values_file and file_pattern. Choose one.")
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("📋 Configuration:")
        print(f"• Path: {self.target_path}")
        print(f"• Tag: {self.new_tag}")
        print(f"• Branch: {self.branch}")
        if self.dry_run:
            print("• Mode: Dry Run")
        if self.target_values_file:
            print(f"• File: {self.target_values_file}")
        if self.file_pattern:
            print(f"• Pattern: {self.file_pattern}")
