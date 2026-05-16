#!/bin/bash
set -o errexit

export VERCEL=1
export DJANGO_SETTINGS_MODULE=uni_portal.settings
export PYTHONUNBUFFERED=1

echo "=== Build Start ==="

# 1. Purge pycache
echo "[1/6] Purging __pycache__..."
find . -not -path './.venv/*' -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find . -not -path './.venv/*' -name '*.pyc' -delete 2>/dev/null || true

# 2. Clean old staticfiles
echo "[2/6] Cleaning old staticfiles..."
rm -rf staticfiles/ 2>/dev/null || true

# 3. Install dependencies
echo "[3/6] Installing dependencies..."
pip install -r requirements.txt --quiet

# 4. Collect static files
echo "[4/6] Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 | grep -v "^Copying\|^Post-process" | head -20

if [ ! -d "staticfiles" ]; then
    echo "ERROR: staticfiles directory was not created!"
    exit 1
fi

if [ ! -f "staticfiles/css/style.css" ]; then
    echo "ERROR: style.css not in staticfiles!"
    ls -la staticfiles/ || echo "staticfiles is empty"
    exit 1
fi

# 5. Run migrations
echo "[5/6] Running migrations..."
python manage.py migrate --noinput 2>&1 | tail -5

# 6. Setup Google OAuth from environment variables
echo "[6/6] Setting up Google OAuth from environment..."
python manage.py setup_google_oauth 2>&1 || echo "WARNING: Google OAuth setup failed — check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars"

echo "=== Build Complete ==="
ls -lh staticfiles/css/style.css
ls -lh staticfiles/images/ 2>/dev/null | head -10
