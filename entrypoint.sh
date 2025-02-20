#!/bin/bash

# Exit on any error
set -e

###########################################
# Utility Functions
###########################################
print_header() {
    echo -e "\n=========================================="
    echo "🚀 $1"
    echo -e "==========================================\n"
}

handle_error() {
    echo "❌ Error: $1"
    exit 1
}

debug_log() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "$1"
    fi
}

print_configuration() {
    echo "📋 Configuration:"
    echo "• Path: $TARGET_PATH"
    echo "• Tag: $NEW_TAG"
    echo "• Branch: $BRANCH"
    [[ "$DRY_RUN" == "true" ]] && echo "• Mode: Dry Run"
    [[ -n "$TARGET_VALUES_FILE" ]] && echo "• File: $TARGET_VALUES_FILE"
    [[ -n "$FILE_PATTERN" ]] && echo "• Pattern: $FILE_PATTERN"
}

###########################################
# Validation Functions
###########################################
validate_env_vars() {
    local required_vars=("TARGET_PATH" "NEW_TAG" "TAG_STRING" "GIT_USER_NAME" "GIT_USER_EMAIL" "GITHUB_TOKEN" "REPO" "BRANCH")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            handle_error "Required environment variable $var is not set"
        fi
    done

    if [[ -z "$TARGET_VALUES_FILE" ]] && [[ -z "$FILE_PATTERN" ]]; then
        handle_error "Either TARGET_VALUES_FILE or FILE_PATTERN must be set"
    fi
}

###########################################
# Git Functions
###########################################
setup_git() {
    debug_log "\n⚙️ Configuring Git..."
    git config --global --add safe.directory /usr/src > /dev/null 2>&1 || handle_error "Failed to set safe.directory /usr/src"
    git config --global --add safe.directory /github/workspace > /dev/null 2>&1 || handle_error "Failed to set safe.directory /github/workspace"
    git config --global user.name "$GIT_USER_NAME" > /dev/null 2>&1 || handle_error "Failed to set git user name"
    git config --global user.email "$GIT_USER_EMAIL" > /dev/null 2>&1 || handle_error "Failed to set git user email"
    git config --global pull.rebase false > /dev/null 2>&1 || handle_error "Failed to set pull strategy"
}

setup_branch() {
    debug_log "\n🔄 Setting up branch: $BRANCH"
    git fetch origin > /dev/null 2>&1 || handle_error "Failed to fetch from remote"

    if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
        git checkout "$BRANCH" > /dev/null 2>&1 || handle_error "Failed to checkout branch: $BRANCH"
        if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
            debug_log "\n⬇️ Pulling latest changes..."
            git pull origin "$BRANCH" > /dev/null 2>&1 || handle_error "Failed to pull latest changes"
        fi
    else
        if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
            git checkout -b "$BRANCH" origin/"$BRANCH" > /dev/null 2>&1 || handle_error "Failed to checkout remote branch"
            debug_log "\n⬇️ Pulling latest changes..."
            git pull origin "$BRANCH" > /dev/null 2>&1 || handle_error "Failed to pull latest changes"
        else
            debug_log "Creating new local branch: $BRANCH"
            git checkout -b "$BRANCH" > /dev/null 2>&1 || handle_error "Failed to create new branch"
        fi
    fi
}

commit_and_push() {
    local commit_message="$1"
    local max_attempts=5
    local attempt=1
    local wait_time=5

    while [ $attempt -le $max_attempts ]; do
        debug_log "\n📦 Attempt $attempt: Fetching latest changes..."
        git fetch origin > /dev/null 2>&1 || handle_error "Failed to fetch from remote"
        
        # Try to rebase on top of remote changes
        if ! git rebase origin/$BRANCH > /dev/null 2>&1; then
            debug_log "⚠️ Rebase failed, aborting rebase and retrying..."
            git rebase --abort > /dev/null 2>&1
            attempt=$((attempt + 1))
            if [ $attempt -le $max_attempts ]; then
                debug_log "Waiting ${wait_time}s before next attempt..."
                sleep $wait_time
                wait_time=$((wait_time + 5))
                continue
            fi
            handle_error "Failed to rebase after $max_attempts attempts"
        fi

        # Stage and commit changes
        debug_log "\n📦 Staging changes..."
        git add . > /dev/null 2>&1 || handle_error "Failed to stage changes"
        
        debug_log "\n💾 Creating commit..."
        git commit -m "$commit_message" > /dev/null 2>&1 || handle_error "Failed to commit changes"

        # Try to push with retry logic
        local push_attempts=3
        local push_attempt=1
        
        while [ $push_attempt -le $push_attempts ]; do
            if git push "https://x-access-token:$GITHUB_TOKEN@github.com/$REPO" "$BRANCH" > /dev/null 2>&1; then
                echo "✅ Successfully pushed changes to $BRANCH"
                return 0
            else
                push_attempt=$((push_attempt + 1))
                if [ $push_attempt -le $push_attempts ]; then
                    debug_log "⚠️ Push failed, retrying... (Attempt $push_attempt of $push_attempts)"
                    sleep 5
                    continue
                fi
            fi
        done

        # If push failed, try the whole process again
        attempt=$((attempt + 1))
        if [ $attempt -le $max_attempts ]; then
            debug_log "⚠️ Push failed, retrying entire commit process..."
            sleep $wait_time
            wait_time=$((wait_time + 5))
            continue
        fi
        
        handle_error "Failed to push changes after $max_attempts attempts"
    done
}

###########################################
# File Operations
###########################################
update_file() {
    local file="$1"
    debug_log "\n🔄 Processing file: $file"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "Current tag in $file: $(grep "$TAG_STRING:" "$file")"
        echo "Would change to: $TAG_STRING: \"$NEW_TAG\""
        return
    fi

    if [[ "$BACKUP" == "true" ]]; then
        debug_log "\n💾 Creating backup..."
        cp "$file" "${file}.bak" || handle_error "Failed to create backup"
        debug_log "✅ Backup created: ${file}.bak"
    fi

    debug_log "\n🔄 Updating image tag..."
    if [[ "$BACKUP" == "true" ]]; then
        sed -i.bak "/^\s*$TAG_STRING:/s|:.*|: \"$NEW_TAG\"|" "$file" || handle_error "Failed to update tag with backup"
    else
        sed -i "/^\s*$TAG_STRING:/s|:.*|: \"$NEW_TAG\"|" "$file" || handle_error "Failed to update tag"
    fi

    echo "✅ Updated $file"
}

process_files() {
    if [[ -n "$FILE_PATTERN" ]]; then
        debug_log "\n🔍 Processing files: $FILE_PATTERN"
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
}

###########################################
# Main Script
###########################################
main() {
    print_header "Starting Git Update Process"
    
    validate_env_vars
    print_configuration

    cd "$TARGET_PATH" || handle_error "Directory not found: $TARGET_PATH"
    
    setup_git
    setup_branch
    process_files

    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "\n✅ Dry run completed. No changes were made."
        exit 0
    fi

    if [[ -n "$FILE_PATTERN" ]]; then
        COMMIT_MESSAGE="$COMMIT_MESSAGE $TARGET_PATH ($FILE_PATTERN)"
    else
        COMMIT_MESSAGE="$COMMIT_MESSAGE $TARGET_PATH ($TARGET_VALUES_FILE)"
    fi
    
    commit_and_push "$COMMIT_MESSAGE"
    
    print_header "Process Completed Successfully"
}

# Execute main function
main