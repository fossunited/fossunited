#!/bin/bash

# Get the current git repository URL
APP_REPO=$(git config --get remote.origin.url)

# Get the current branch name
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Export the environment variables
export APP_REPO
export BRANCH_NAME

# Write the variables to a .env file in the same directory
SCRIPT_DIR=$(dirname "$0")
ENV_FILE="$SCRIPT_DIR/.env"

echo "APP_REPO=$APP_REPO" > "$ENV_FILE"
echo "BRANCH_NAME=$BRANCH_NAME" >> "$ENV_FILE"

# Print the variables for verification
echo "APP_REPO=$APP_REPO"
echo "BRANCH_NAME=$BRANCH_NAME"
echo ".env file written to $ENV_FILE"