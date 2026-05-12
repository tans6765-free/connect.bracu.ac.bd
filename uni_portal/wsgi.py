import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')

# Setup Django
django.setup()

# On Vercel cold start: ensure migrations are applied and Google OAuth is configured
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        print("[wsgi] Running migrations...")
        call_command('migrate', '--noinput', verbosity=0)
        print("[wsgi] Migrations complete")
    except Exception as e:
        print(f"[wsgi] Migration warning: {e}")

    # Configure Google OAuth in the database
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()

        if client_id and client_secret:
            # Ensure site is correct
            site, _ = Site.objects.get_or_create(id=1)
            if site.domain != 'connectbracuacbd.vercel.app':
                site.domain = 'connectbracuacbd.vercel.app'
                site.name = 'BracU Central'
                site.save()
                print("[wsgi] Updated Site domain")

            # Clean up old Google apps
            deleted, _ = SocialApp.objects.filter(provider='google').delete()
            if deleted > 0:
                print(f"[wsgi] Deleted {deleted} old Google SocialApp(s)")

            # Create fresh Google app
            app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=client_id,
                secret=client_secret,
            )
            app.sites.add(site)
            print("[wsgi] Created fresh Google SocialApp")
        else:
            print("[wsgi] WARNING: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set")
    except Exception as e:
        print(f"[wsgi] OAuth setup warning: {e}")

application = get_wsgi_application()
