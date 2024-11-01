#!/bin/bash
set -e

# Inputs
TARGET_PATH=$1
TAG_STRING=$2
NEW_TAG=$3
TARGET_VALUES_FILE=$4
GITHUB_TOKEN=$5
COMMIT_MESSAGE=$6
REPO=$7
BRANCH=$8
GIT_USER_NAME=$9
GIT_USER_EMAIL=${10}
BACKUP=${11}  # "true" or "false"

# Navigate to the target directory
cd "$TARGET_PATH" || { echo "Directory not found: $TARGET_PATH"; exit 1; }

# Check if the target values file exists
VALUES_FILE="$TARGET_VALUES_FILE.values.yaml"
if [[ ! -f "$VALUES_FILE" ]]; then
  echo "File not found: $VALUES_FILE"
  exit 1
fi

# Update the image tag in the specified values file
if [[ "$BACKUP" == "true" ]]; then
  sed -i.bak "s|$TAG_STRING:.*|$TAG_STRING: \"$NEW_TAG\"|g" "$VALUES_FILE"
  echo "Backup created: $VALUES_FILE.bak"
else
  sed -i "s|$TAG_STRING:.*|$TAG_STRING: \"$NEW_TAG\"|g" "$VALUES_FILE"
  echo "No backup created."
fi

# Check if there are changes to commit
if git diff --exit-code "$VALUES_FILE"; then
  echo "No changes to commit."
  exit 0
fi

# Configure Git with the provided user name and email
git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"

# Commit and push changes
FULL_PATH="$TARGET_PATH/$VALUES_FILE"
COMMIT_MESSAGE="$COMMIT_MESSAGE $FULL_PATH"
git checkout "$BRANCH"
git add "$VALUES_FILE"
git commit -m "$COMMIT_MESSAGE"
git push "https://x-access-token:$GITHUB_TOKEN@github.com/$REPO" "$BRANCH"
