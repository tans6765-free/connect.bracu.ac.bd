import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_portal.settings')

# Setup Django first
django.setup()

# === VERCEL + LOCAL SETUP ===
if os.environ.get('VERCEL') or os.environ.get('DEBUG', 'True').lower() == 'true':
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput')
        print("✅ Migrations applied")
    except Exception as e:
        print("⚠️ Migrate warning:", e)

    try:
        from django.conf import settings
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        # Site setup
        site_domain = os.environ.get('SITE_DOMAIN', 'connectbracuacbd.vercel.app')
        site, created = Site.objects.get_or_create(
            pk=settings.SITE_ID,
            defaults={'domain': site_domain, 'name': 'BRAC University'}
        )
        if not created:
            site.domain = site_domain
            site.name = 'BRAC University'
            site.save()

        # === STRONG CLEANUP FOR GOOGLE SOCIALAPP ===
        google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        google_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()

        if google_client_id and google_secret:
            # Delete ALL google providers (this is the key)
            SocialApp.objects.filter(provider='google').delete()
            
            # Create exactly one
            app = SocialApp.objects.create(
                provider='google',
                name='BRAC Google OAuth',
                client_id=google_client_id,
                secret=google_secret,
            )
            app.sites.add(site)
            print("✅ Google SocialApp cleaned and recreated")
        else:
            print("⚠️ Google credentials not found in env vars")
    except Exception as e:
        print("❌ SocialApp setup error:", str(e))

application = get_wsgi_application()