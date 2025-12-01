#!/usr/bin/env python3
"""Main entry point for image tag updater."""
import os
import sys

from src.config import Config
from src.file_processor import FileProcessor
from src.git_operations import GitOperations
from src.logger import Logger
from src.summary import ChangeSummary


def write_output(name: str, value: str) -> None:
    """Write output to GITHUB_OUTPUT file."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            # Use multiline format for safety
            f.write(f"{name}<<EOF\n")
            f.write(f"{value}\n")
            f.write("EOF\n")


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
        logger.debug(f"\nNavigating to target directory: {config.target_path}")
        os.chdir(config.target_path)
        
        # Show directory contents in debug mode
        if config.debug:
            logger.debug("\nCurrent directory contents:")
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
        
        # Initialize change summary
        summary = ChangeSummary(config, logger)
        
        # Prepare outputs
        final_tag = config.get_final_tag()
        updated_files_list = ",".join(file_processor.updated_files)
        old_tags_list = ",".join(file_processor.old_tags.values())
        files_count = str(len(file_processor.updated_files))
        
        # Write outputs
        write_output("files_updated", files_count)
        write_output("updated_files", updated_files_list)
        write_output("old_tags", old_tags_list)
        write_output("new_tag_applied", final_tag)
        write_output("changes_made", str(changes_made).lower())
        
        # Print summary
        if changes_made:
            summary.print_summary(
                file_processor.updated_files,
                file_processor.old_tags
            )
        
        # Handle dry run mode
        if config.dry_run:
            write_output("commit_sha", "")
            # Save summary even in dry run mode
            if config.summary_file:
                summary.save_summary(
                    file_processor.updated_files,
                    file_processor.old_tags
                )
            logger.info("\n✅ Dry run completed. No changes were made.")
            logger.print_header("Process Completed Successfully")
            return
        
        # If no changes were made, exit successfully
        if not changes_made:
            write_output("commit_sha", "")
            logger.info("\n✅ No changes needed. Values are already up to date.")
            logger.print_header("Process Completed Successfully")
            return
        
        # Commit and push changes
        file_info = config.file_pattern or config.target_values_file
        commit_sha = git_ops.commit_and_push(file_info)
        
        # Write commit SHA outputs
        write_output("commit_sha", commit_sha or "")
        commit_sha_short = commit_sha[:7] if commit_sha and len(commit_sha) >= 7 else (commit_sha or "")
        write_output("commit_sha_short", commit_sha_short)
        
        # Save summary with commit SHA
        if config.summary_file:
            summary.save_summary(
                file_processor.updated_files,
                file_processor.old_tags,
                commit_sha
            )
        
        logger.print_header("Process Completed Successfully")
        
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
