#!/bin/bash
set -o errexit

export VERCEL=1

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running migrations..."
python manage.py migrate --noinput || true

echo "Build completed successfully!"
