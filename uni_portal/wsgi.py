import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')

django.setup()

if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput')
    except Exception as exc:
        print('WARNING: automatic runtime migrate failed:', exc)

    try:
        from django.conf import settings
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        site_domain = os.environ.get('SITE_DOMAIN', 'localhost:8000')
        site_name = os.environ.get('SITE_NAME', 'BRAC University')
        site, created = Site.objects.get_or_create(
            pk=settings.SITE_ID,
            defaults={'domain': site_domain, 'name': site_name},
        )
        if not created and (site.domain != site_domain or site.name != site_name):
            site.domain = site_domain
            site.name = site_name
            site.save()

        google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        google_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        if google_client_id and google_secret:
            google_app, _ = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'BRAC Google OAuth',
                    'client_id': google_client_id,
                    'secret': google_secret,
                },
            )
            if google_app.client_id != google_client_id or google_app.secret != google_secret:
                google_app.client_id = google_client_id
                google_app.secret = google_secret
                google_app.save()
            if site not in google_app.sites.all():
                google_app.sites.add(site)
    except Exception as exc:
        print('WARNING: runtime site/SocialApp setup failed:', exc)

application = get_wsgi_application()