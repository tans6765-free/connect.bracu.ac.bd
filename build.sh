#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings
export PYTHONUNBUFFERED=1

echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo "Collecting static files..."
python manage.py collectstatic --noinput --no-default-ignore 2>&1 | grep -v "^Copying" | grep -v "^$"

echo "Running migrations..."
python manage.py migrate --run-syncdb --noinput 2>&1 | tail -5

echo "Build completed!"