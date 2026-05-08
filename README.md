# University Portal (development)

This is a small Django app scaffolding for a university portal UI (development only).

Setup (Windows):

1. Create and activate a virtualenv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install requirements

```powershell
pip install -r requirements.txt
```

3. Run migrations and start server

```powershell
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ to view the dashboard.

Notes:
- The UI uses Bootstrap CDN and a local stylesheet at `portal/static/css/style.css`.
- This is intended for local development; do not use `DEBUG=True` in production.
