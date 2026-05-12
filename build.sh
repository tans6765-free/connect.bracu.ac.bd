#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings
export PYTHONUNBUFFERED=1

echo "=== Build Start ==="

# CRITICAL: Remove ALL __pycache__ to prevent stale .pyc files
echo "[1/5] Purging __pycache__..."
find . -not -path './.venv/*' -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find . -not -path './.venv/*' -name '*.pyc' -delete 2>/dev/null || true

# Remove old staticfiles
echo "[2/5] Cleaning old staticfiles..."
rm -rf staticfiles/ 2>/dev/null || true

# Install dependencies
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt --quiet

# Collect static files (creates fresh staticfiles/ directory)
echo "[4/5] Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 | grep -v "^Copying\|^Post-process" | head -20

# Verify staticfiles were created
if [ ! -d "staticfiles" ]; then
    echo "ERROR: staticfiles directory was not created!"
    exit 1
fi

if [ ! -f "staticfiles/css/style.css" ]; then
    echo "ERROR: style.css not in staticfiles!"
    ls -la staticfiles/ || echo "staticfiles is empty"
    exit 1
fi

echo "[5/5] Running migrations..."
python manage.py migrate --noinput 2>&1 | tail -3

echo "=== Build Complete ==="
ls -lh staticfiles/css/style.css
ls -lh staticfiles/images/ 2>/dev/null | head -10
