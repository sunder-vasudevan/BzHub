#!/bin/bash
# Usage: ./create_pr.sh "Fixes #123: Short PR title" "Detailed PR body"

TITLE="$1"
BODY="$2"
BASE_BRANCH="dev"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Push current branch
git push -u origin "$CURRENT_BRANCH"

# Create PR
gh pr create --base "$BASE_BRANCH" --head "$CURRENT_BRANCH" --title "$TITLE" --body "$BODY"
