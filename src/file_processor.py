"""File processing utilities for image tag updater."""
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

from .config import Config
from .logger import Logger


class FileProcessor:
    """Handle file operations for updating image tags."""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.updated_files: List[str] = []
        self.old_tags: Dict[str, str] = {}  # file_path -> old_tag
    
    def validate_file_content(self, file_path: str) -> None:
        """Validate that tag string exists in file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if tag_string exists in the file
            pattern = rf'^\s*{re.escape(self.config.tag_string)}:'
            if not re.search(pattern, content, re.MULTILINE):
                self.logger.error(
                    f"Tag string '{self.config.tag_string}' not found in file: {file_path}"
                )
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
    
    def get_current_tag(self, file_path: str) -> str:
        """Extract current tag value from file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            pattern = rf'^\s*{re.escape(self.config.tag_string)}:\s*"?([^"\n]+)"?'
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1).strip()
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get current tag from {file_path}: {e}")
    
    def update_file(self, file_path: str) -> bool:
        """Update tag in file. Returns True if changes were made."""
        self.logger.debug(f"\nProcessing file: {file_path}")
        
        # Get current tag value
        current_tag = self.get_current_tag(file_path)
        
        # Get final tag with prefix/suffix
        final_tag = self.config.get_final_tag()
        
        # If tag is already the target value, skip
        if current_tag == final_tag:
            self.logger.info(f"Tag in {file_path} already set to {final_tag}, skipping update")
            return False
        
        # Store old tag for output
        self.old_tags[file_path] = current_tag
        
        # Dry run mode - show what would change
        if self.config.dry_run:
            self.logger.info(f"Current tag in {file_path}: {self.config.tag_string}: {current_tag}")
            self.logger.info(f"Would change to: {self.config.tag_string}: \"{final_tag}\"")
            self.updated_files.append(file_path)
            return True
        
        # Create backup if requested
        if self.config.backup:
            self.logger.debug("\nCreating backup...")
            backup_path = f"{file_path}.bak"
            try:
                shutil.copy2(file_path, backup_path)
                self.logger.debug(f"Backup created: {backup_path}")
            except Exception as e:
                self.logger.error(f"Failed to create backup: {e}")
        
        # Update the file
        try:
            self.logger.debug("\nUpdating image tag...")
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace the tag value with final tag (including prefix/suffix)
            pattern = rf'(^\s*{re.escape(self.config.tag_string)}:)\s*.*$'
            replacement = rf'\1 "{final_tag}"'
            updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(file_path, 'w') as f:
                f.write(updated_content)
            
            self.logger.success(f"Updated {file_path}")
            self.updated_files.append(file_path)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update file {file_path}: {e}")
    
    def get_files_to_process(self) -> List[str]:
        """Get list of files to process based on configuration."""
        files = []
        
        if self.config.file_pattern:
            self.logger.debug(f"\nProcessing files: {self.config.file_pattern}")
            # Use glob pattern
            from glob import glob
            matched_files = glob(self.config.file_pattern)
            if not matched_files:
                self.logger.error(f"No files found matching pattern: {self.config.file_pattern}")
            files = [f for f in matched_files if os.path.isfile(f)]
        else:
            values_file = self.config.target_values_file
            if not os.path.isfile(values_file):
                self.logger.error(f"File not found: {values_file}")
            files = [values_file]
        
        return files
    
    def process_files(self) -> bool:
        """Process all files. Returns True if any changes were made."""
        files = self.get_files_to_process()
        changes_made = False
        
        for file_path in files:
            self.validate_file_content(file_path)
            if self.update_file(file_path):
                changes_made = True
        
        return changes_made
