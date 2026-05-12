import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')
django.setup()

if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput')
    except Exception as e:
        print("Migrate warning:", e)

    # -----------------------------------------------------------------------
    # FIX: Delete stale SocialApp rows then recreate exactly one fresh entry
    # from the current env vars.  Previously the code only deleted without
    # recreating, which broke older allauth versions that look up the DB row
    # instead of reading SOCIALACCOUNT_PROVIDERS['google']['APP'].
    # -----------------------------------------------------------------------
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        # Clean up duplicates
        deleted, _ = SocialApp.objects.filter(provider='google').delete()
        print(f"Cleaned up {deleted} old Google SocialApp(s)")

        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

        if client_id and client_secret:
            site, _ = Site.objects.get_or_create(
                id=1,
                defaults={'domain': 'connectbracuacbd.vercel.app', 'name': 'BracU Portal'}
            )
            if site.domain != 'connectbracuacbd.vercel.app' or site.name != 'BracU Portal':
                site.domain = 'connectbracuacbd.vercel.app'
                site.name = 'BracU Portal'
                site.save()

            apps = SocialApp.objects.filter(provider='google')
            if apps.exists():
                app = apps.order_by('id').first()
                apps.exclude(pk=app.pk).delete()
                app.name = 'Google'
                app.client_id = client_id
                app.secret = client_secret
                app.save()
            else:
                app = SocialApp.objects.create(
                    provider='google',
                    name='Google',
                    client_id=client_id,
                    secret=client_secret,
                )
            app.sites.set([site])
            print("Created fresh Google SocialApp")
        else:
            print("WARNING: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set — Google login will not work")
    except Exception as e:
        print("SocialApp setup warning:", e)

application = get_wsgi_application()