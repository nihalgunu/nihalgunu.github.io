#!/bin/bash
# Script to deploy website to GitHub Pages

REPO_NAME="nihalgunukula.github.io"
GITHUB_USER="nihalgunukula"

echo "Setting up remote repository..."
git remote add origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git 2>/dev/null || git remote set-url origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git

echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Code pushed successfully!"
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/${GITHUB_USER}/${REPO_NAME}/settings/pages"
echo "2. Under 'Source', select 'Deploy from a branch'"
echo "3. Choose 'main' branch and '/ (root)' folder"
echo "4. Click 'Save'"
echo ""
echo "Your site will be live at: https://${REPO_NAME}"

