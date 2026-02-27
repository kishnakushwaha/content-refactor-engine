#!/usr/bin/env bash
# start.sh

# Exit on error
set -o errexit

echo "Starting FastAPI Production Server..."
cd backend

# Use Gunicorn as a process manager with Uvicorn workers for production stability
# Uses the PORT environment variable provided automatically by Render
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
