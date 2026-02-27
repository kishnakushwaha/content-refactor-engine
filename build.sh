#!/usr/bin/env bash
# build.sh

# Exit on error
set -o errexit

echo "Installing backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Create database directory if it doesn't exist
cd ..
mkdir -p database
echo "Build complete."
