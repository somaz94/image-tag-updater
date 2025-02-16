#!/bin/bash

# Exit on any error
set -e

# Function for printing headers
print_header() {
    echo -e "\n=========================================="
    echo "🚀 $1"
    echo -e "==========================================\n"
}

# Function for error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Function to validate required environment variables
validate_env_vars() {
    local required_vars=("TARGET_PATH" "NEW_TAG" "TAG_STRING" "GIT_USER_NAME" "GIT_USER_EMAIL" "GITHUB_TOKEN" "REPO" "BRANCH")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            handle_error "Required environment variable $var is not set"
        fi
    done

    # Check if at least one of TARGET_VALUES_FILE or FILE_PATTERN is set
    if [[ -z "$TARGET_VALUES_FILE" ]] && [[ -z "$FILE_PATTERN" ]]; then
        handle_error "Either TARGET_VALUES_FILE or FILE_PATTERN must be set"
    fi
}

# Function to update a single file
update_file() {
    local file="$1"
    echo -e "\n🔄 Processing file: $file"

    # If dry run mode is enabled, show what would be changed
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 Dry run mode - showing potential changes for $file:"
        echo "Current tag line: $(grep "$TAG_STRING:" "$file")"
        echo "Would change to:  $TAG_STRING: \"$NEW_TAG\""
        return
    fi

    # Create backup if requested
    if [[ "$BACKUP" == "true" ]]; then
        echo -e "\n💾 Creating backup..."
        cp "$file" "${file}.bak" || handle_error "Failed to create backup"
        echo "✅ Backup created: ${file}.bak"
    fi

    # Update the image tag
    echo -e "\n🔄 Updating image tag..."
    if [[ "$BACKUP" == "true" ]]; then
        sed -i.bak "/^\s*$TAG_STRING:/s|:.*|: \"$NEW_TAG\"|" "$file" || handle_error "Failed to update tag with backup"
    else
        sed -i "/^\s*$TAG_STRING:/s|:.*|: \"$NEW_TAG\"|" "$file" || handle_error "Failed to update tag"
    fi

    echo "✅ Successfully updated $file"
}

print_header "Starting Git Update Process"

# Validate environment variables
validate_env_vars

# Print current configuration
echo "📋 Current Configuration:"
echo "  • Target Path: $TARGET_PATH"
echo "  • Tag String: $TAG_STRING"
echo "  • New Tag: $NEW_TAG"
echo "  • Branch: $BRANCH"
echo "  • Backup Enabled: ${BACKUP:-false}"
echo "  • Dry Run Mode: ${DRY_RUN:-false}"
echo "  • Commit Message: ${COMMIT_MESSAGE:-Update image tag in}"
[[ -n "$TARGET_VALUES_FILE" ]] && echo "  • Values File: $TARGET_VALUES_FILE"
[[ -n "$FILE_PATTERN" ]] && echo "  • File Pattern: $FILE_PATTERN"

# Navigate to the target directory
echo -e "\n📂 Navigating to target directory..."
cd "$TARGET_PATH" || handle_error "Directory not found: $TARGET_PATH"

# Confirm directory contents
echo -e "\n📑 Current directory contents:"
ls -la

# Configure Git with safe directory settings first
echo -e "\n⚙️ Configuring Git..."
git config --global --add safe.directory /usr/src || handle_error "Failed to set safe.directory /usr/src"
git config --global --add safe.directory /github/workspace || handle_error "Failed to set safe.directory /github/workspace"

# Configure Git user and pull strategy
git config --global user.name "$GIT_USER_NAME" || handle_error "Failed to set git user name"
git config --global user.email "$GIT_USER_EMAIL" || handle_error "Failed to set git user email"
git config --global pull.rebase false || handle_error "Failed to set pull strategy"

# Fetch and checkout branch
echo -e "\n🔄 Checking out branch: $BRANCH"
git fetch origin || handle_error "Failed to fetch from remote"

# Check if branch exists locally or remotely
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    # Branch exists locally
    git checkout "$BRANCH" || handle_error "Failed to checkout branch: $BRANCH"
    
    # Pull if remote branch exists
    if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
        echo -e "\n⬇️ Pulling latest changes..."
        git pull origin "$BRANCH" || handle_error "Failed to pull latest changes"
    fi
else
    # Check if branch exists in remote
    if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
        # Remote branch exists, checkout and track it
        git checkout -b "$BRANCH" origin/"$BRANCH" || handle_error "Failed to checkout remote branch"
        echo -e "\n⬇️ Pulling latest changes..."
        git pull origin "$BRANCH" || handle_error "Failed to pull latest changes"
    else
        # Create new branch locally
        echo "Creating new local branch: $BRANCH"
        git checkout -b "$BRANCH" || handle_error "Failed to create new branch"
    fi
fi

# Process files based on input
if [[ -n "$FILE_PATTERN" ]]; then
    echo -e "\n🔍 Searching for files matching pattern: $FILE_PATTERN"
    files=($FILE_PATTERN)
    if [ ${#files[@]} -eq 0 ]; then
        handle_error "No files found matching pattern: $FILE_PATTERN"
    fi
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            update_file "$file"
        fi
    done
else
    VALUES_FILE="$TARGET_VALUES_FILE"
    if [[ ! -f "$VALUES_FILE" ]]; then
        handle_error "File not found: $VALUES_FILE"
    fi
    update_file "$VALUES_FILE"
fi

# If dry run mode is enabled, exit here
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "\n✅ Dry run completed. No changes were made."
    exit 0
fi

# Stage and commit changes
echo -e "\n📦 Staging changes..."
git add . || handle_error "Failed to stage changes"

# Create commit message
if [[ -n "$FILE_PATTERN" ]]; then
    COMMIT_MESSAGE="$COMMIT_MESSAGE $TARGET_PATH ($FILE_PATTERN)"
else
    COMMIT_MESSAGE="$COMMIT_MESSAGE $TARGET_PATH ($TARGET_VALUES_FILE)"
fi

# Commit changes
echo -e "\n💾 Creating commit..."
git commit -m "$COMMIT_MESSAGE" || handle_error "Failed to commit changes"

# Push changes with retry logic
MAX_RETRIES=3
RETRY_COUNT=0
while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
    if git push "https://x-access-token:$GITHUB_TOKEN@github.com/$REPO" "$BRANCH"; then
        echo "✅ $(date '+%Y-%m-%d %H:%M:%S') Successfully pushed changes to remote"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [[ $RETRY_COUNT -eq $MAX_RETRIES ]]; then
            handle_error "Failed to push changes after $MAX_RETRIES attempts"
        fi
        echo "⚠️ $(date '+%Y-%m-%d %H:%M:%S') Push failed, retrying in 5 seconds... (Attempt $RETRY_COUNT of $MAX_RETRIES)"
        sleep 5
    fi
done

print_header "Process Completed Successfully"