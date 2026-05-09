#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --ignore=node_modules

echo "Running migrations..."
python manage.py migrate --run-syncdb --noinput

echo "Build completed successfully!"