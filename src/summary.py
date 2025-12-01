"""Change summary utilities for image tag updater."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import Config
from .logger import Logger


class ChangeSummary:
    """Handle change summary generation and storage."""
    
    MAX_ENTRIES = 100  # Maximum number of summary entries to keep
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
    
    def create_summary(
        self,
        updated_files: List[str],
        old_tags: Dict[str, str],
        commit_sha: Optional[str] = None
    ) -> Dict:
        """Create a summary of changes."""
        final_tag = self.config.get_final_tag()
        
        # Create change records for each file
        changes = []
        for file_path in updated_files:
            old_tag = old_tags.get(file_path, "")
            changes.append({
                "file": file_path,
                "old_tag": old_tag,
                "new_tag": final_tag,
                "tag_string": self.config.tag_string
            })
        
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "repository": self.config.repo,
            "branch": self.config.branch,
            "commit_sha": commit_sha or "",
            "target_path": self.config.target_path,
            "changes_count": len(updated_files),
            "changes": changes,
            "dry_run": self.config.dry_run
        }
        
        return summary
    
    def save_summary(
        self,
        updated_files: List[str],
        old_tags: Dict[str, str],
        commit_sha: Optional[str] = None
    ) -> None:
        """Save change summary to file."""
        if not self.config.summary_file:
            return
        
        summary = self.create_summary(updated_files, old_tags, commit_sha)
        
        # Ensure parent directory exists
        summary_path = Path(self.config.summary_file)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing summaries if file exists
        summaries = []
        if summary_path.exists():
            try:
                with open(summary_path, 'r') as f:
                    summaries = json.load(f)
                if not isinstance(summaries, list):
                    summaries = [summaries]
            except json.JSONDecodeError as e:
                self.logger.warning(f"Invalid JSON in summary file: {e}")
                summaries = []
            except IOError as e:
                self.logger.warning(f"Could not read summary file: {e}")
                summaries = []
        
        # Append new summary
        summaries.append(summary)
        
        # Keep only last N entries to prevent file from growing too large
        summaries = summaries[-self.MAX_ENTRIES:]
        
        # Write updated summaries
        try:
            with open(summary_path, 'w') as f:
                json.dump(summaries, f, indent=2)
            self.logger.success(f"Summary saved to: {self.config.summary_file}")
            self.logger.debug(f"Summary content:\n{json.dumps(summary, indent=2)}")
        except IOError as e:
            self.logger.error(f"Failed to write summary file: {e}")
    
    def print_summary(
        self,
        updated_files: List[str],
        old_tags: Dict[str, str],
        commit_sha: Optional[str] = None
    ) -> None:
        """Print change summary to console."""
        if not updated_files:
            return
        
        final_tag = self.config.get_final_tag()
        
        self.logger.info("\n📊 Change Summary:")
        self.logger.info(f"   Updated {len(updated_files)} file(s)")
        
        for file_path in updated_files:
            old_tag = old_tags.get(file_path, "unknown")
            self.logger.info(f"   • {file_path}")
            self.logger.info(f"     {old_tag} → {final_tag}")
        
        if commit_sha:
            self.logger.info(f"\n   Commit: {commit_sha}")
