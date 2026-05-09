import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')

# On Vercel, /tmp is writable but ephemeral — run migrations on every cold start
# so the SQLite DB and tables always exist when requests arrive.
if os.environ.get('VERCEL'):
    import django
    django.setup()
    from django.core.management import call_command
    try:
        call_command('collectstatic', '--noinput', '--clear', verbosity=0)
    except Exception as e:
        print(f"Collectstatic warning: {e}")
    try:
        call_command('migrate', '--run-syncdb', verbosity=0)
    except Exception as e:
        print(f"Migration warning: {e}")

application = get_wsgi_application()