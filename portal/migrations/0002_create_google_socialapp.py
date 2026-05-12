from django.db import migrations
import os


def create_google_socialapp(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')

    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    try:
        # Use VERCEL_URL env var if available, otherwise localhost
        site_domain = os.environ.get('VERCEL_URL', 'localhost:8000')
        site, _ = Site.objects.update_or_create(
            pk=1,
            defaults={'domain': site_domain, 'name': 'BRAC Portal'}
        )

        # Remove duplicates, keep one
        try:
            existing = list(SocialApp.objects.filter(provider='google'))
            for app in existing[1:]:
                app.delete()
        except Exception:
            pass

        # Create or update Google SocialApp
        # Even if credentials are missing, we need the SocialApp entry
        # so that the login URL doesn't return a 500 error
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id or 'placeholder-client-id',
                'secret': client_secret or 'placeholder-secret'
            }
        )
        
        if not created:
            # Update with actual credentials if provided
            google_app.client_id = client_id or google_app.client_id
            google_app.secret = client_secret or google_app.secret
            google_app.save()

        google_app.sites.set([site])
        
        if client_id and client_secret:
            print(f"✓ Google SocialApp configured for domain: {site_domain}")
        else:
            print(f"⚠ Google SocialApp placeholder created for domain: {site_domain}")
            print(f"  (Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to enable)")
    except Exception as e:
        print(f"⚠ Warning during Google SocialApp setup: {e}")
        print("  The app will continue to work, but Google OAuth may not be available")


def reverse_google_socialapp(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    SocialApp.objects.filter(provider='google').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
        ('socialaccount', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_google_socialapp, reverse_google_socialapp),
    ]
