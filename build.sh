#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings

echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "WARNING: Migrations failed, but continuing..."
}

echo "Build completed successfully!"