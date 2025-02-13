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
    local required_vars=("TARGET_PATH" "TARGET_VALUES_FILE" "TAG_STRING" "NEW_TAG" "GIT_USER_NAME" "GIT_USER_EMAIL" "GITHUB_TOKEN" "REPO" "BRANCH")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            handle_error "Required environment variable $var is not set"
        fi
    done
}

print_header "Starting Git Update Process"

# Validate environment variables
validate_env_vars

# Allow git operations in the current directory
git config --global --add safe.directory /usr/src || handle_error "Failed to set safe.directory /usr/src"
git config --global --add safe.directory /github/workspace || handle_error "Failed to set safe.directory /github/workspace"

# Print current configuration
echo "📋 Current Configuration:"
echo "  • Target Path: $TARGET_PATH"
echo "  • Values File: $TARGET_VALUES_FILE"
echo "  • Tag String: $TAG_STRING"
echo "  • New Tag: $NEW_TAG"
echo "  • Branch: $BRANCH"
echo "  • Backup Enabled: ${BACKUP:-false}"

# Navigate to the target directory
echo -e "\n📂 Navigating to target directory..."
cd "$TARGET_PATH" || handle_error "Directory not found: $TARGET_PATH"

# Confirm directory contents
echo -e "\n📑 Current directory contents:"
ls -al

# Check if the target values file exists
VALUES_FILE="$TARGET_VALUES_FILE.values.yaml"
[[ -f "$VALUES_FILE" ]] || handle_error "File not found: $VALUES_FILE"

# Create backup if requested
if [[ "$BACKUP" == "true" ]]; then
    echo -e "\n💾 Creating backup..."
    cp "$VALUES_FILE" "${VALUES_FILE}.bak" || handle_error "Failed to create backup"
    echo "✅ Backup created: ${VALUES_FILE}.bak"
fi

# Update the image tag
echo -e "\n🔄 Updating image tag..."
if [[ "$BACKUP" == "true" ]]; then
    sed -i.bak "/^\s*$TAG_STRING:/s|:.*|: \"$NEW_TAG\"|" "$VALUES_FILE" || handle_error "Failed to update tag with backup"
else
    sed -i "/^\s*$TAG_STRING:/s|:.*|: \"$NEW_TAG\"|" "$VALUES_FILE" || handle_error "Failed to update tag"
fi

# Configure Git
echo -e "\n⚙️ Configuring Git..."
git config --global user.name "$GIT_USER_NAME" || handle_error "Failed to set git user name"
git config --global user.email "$GIT_USER_EMAIL" || handle_error "Failed to set git user email"

# Checkout branch
echo -e "\n🔄 Checking out branch: $BRANCH"
git checkout "$BRANCH" || handle_error "Failed to checkout branch: $BRANCH"

# Pull latest changes
echo -e "\n⬇️ Pulling latest changes..."
git pull origin "$BRANCH" || handle_error "Failed to pull latest changes"

git status

# Check for changes
echo -e "\n🔍 Checking for changes..."
if git diff --exit-code "$VALUES_FILE"; then
    echo "✅ No changes to commit."
    exit 0
fi

# Commit and push changes
echo -e "\n📤 Committing and pushing changes..."
FULL_PATH="$TARGET_PATH/$VALUES_FILE"
COMMIT_MESSAGE="$COMMIT_MESSAGE $FULL_PATH"

git add "$VALUES_FILE" || handle_error "Failed to stage changes"
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