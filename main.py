#!/usr/bin/env python3
"""Main entry point for image tag updater."""
import os
import sys

from src.config import Config
from src.file_processor import FileProcessor
from src.git_operations import GitOperations
from src.logger import Logger


def main() -> None:
    """Main function."""
    # Initialize logger
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    logger = Logger(debug=debug_mode)
    
    logger.print_header("Starting Git Update Process")
    
    try:
        # Load and validate configuration
        config = Config.from_env()
        config.validate()
        config.print_config()
        
        # Navigate to target directory
        logger.debug(f"\n📂 Navigating to target directory: {config.target_path}")
        os.chdir(config.target_path)
        
        # Show directory contents in debug mode
        if config.debug:
            logger.debug("\n📑 Current directory contents:")
            for item in os.listdir("."):
                logger.debug(f"  {item}")
        
        # Initialize Git operations
        git_ops = GitOperations(config, logger)
        
        # Configure Git
        git_ops.configure_git()
        
        # Setup branch
        git_ops.setup_branch()
        
        # Process files
        file_processor = FileProcessor(config, logger)
        changes_made = file_processor.process_files()
        
        # Handle dry run mode
        if config.dry_run:
            logger.info("\n✅ Dry run completed. No changes were made.")
            logger.print_header("Process Completed Successfully")
            return
        
        # If no changes were made, exit successfully
        if not changes_made:
            logger.info("\n✅ No changes needed. Values are already up to date.")
            logger.print_header("Process Completed Successfully")
            return
        
        # Commit and push changes
        file_info = config.file_pattern or config.target_values_file
        git_ops.commit_and_push(file_info)
        
        logger.print_header("Process Completed Successfully")
        
    except ValueError as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
