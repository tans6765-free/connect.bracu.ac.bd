#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings
export PYTHONUNBUFFERED=1

# CRITICAL: always purge __pycache__ so stale .pyc files never override .py
find . -not -path './.venv/*' -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find . -not -path './.venv/*' -name '*.pyc' -delete 2>/dev/null || true

echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo "Running migrations..."
python manage.py migrate --run-syncdb --noinput 2>&1 | tail -5

echo "Build completed!"
