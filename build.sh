#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --no-default-ignore

echo "Running migrations..."
python manage.py migrate --run-syncdb --noinput || true

echo "Build completed successfully!"