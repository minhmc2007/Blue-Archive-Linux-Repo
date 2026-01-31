#!/bin/bash
set -e

# === CONFIG ===
# This determines the name of the database file.
# In pacman.conf, this will match the section name [bal-repo]
REPO_NAME="bal-repo"
# ==============

# 1. Detect if we are in the parent folder or the x86_64 folder
if [ -d "x86_64" ]; then
    cd x86_64
    echo "-> Entering x86_64 directory..."
elif [ -f "bal-welcome-bin-1.0.0-1-x86_64.pkg.tar.zst" ]; then
    echo "-> Already in package directory..."
else
    echo "Error: Could not find x86_64 directory or packages."
    exit 1
fi

# 2. Remove old database files to ensure a clean update
# (This prevents issues where removed packages stick around in the DB)
echo "-> Cleaning old database files..."
rm -f "${REPO_NAME}.db" "${REPO_NAME}.db.tar.gz" \
      "${REPO_NAME}.files" "${REPO_NAME}.files.tar.gz"

# 3. Generate the Repository Database
# repo-add updates the database with the package information.
# We pass *.pkg.tar.zst to add all packages in the current folder.
echo "-> Building Repository Database ($REPO_NAME)..."

# Note: We do NOT use --sign or --verify, so this is unsigned.
repo-add "${REPO_NAME}.db.tar.gz" *.pkg.tar.zst

echo "Repository Generated Successfully!"
echo "Database: $(pwd)/${REPO_NAME}.db.tar.gz"
