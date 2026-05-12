#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings
export PYTHONUNBUFFERED=1

echo "==> Cleaning cache..."
find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

echo "==> Installing dependencies..."
pip install -r requirements.txt --quiet

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "Build completed!"