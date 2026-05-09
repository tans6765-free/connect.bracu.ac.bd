from django.db import migrations
import os


def create_google_socialapp(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')

    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    if not client_id or not client_secret:
        print("WARNING: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set, skipping SocialApp creation")
        return

    # Ensure site exists with correct domain
    site, _ = Site.objects.update_or_create(
        pk=1,
        defaults={
            'domain': 'bracuconnectbracuacbd.vercel.app',
            'name': 'BRAC Portal',
        }
    )

    # Create or update Google SocialApp
    google_app = SocialApp.objects.filter(provider='google').first()
    if google_app:
        google_app.client_id = client_id
        google_app.secret = client_secret
        google_app.save()
        print("Updated existing Google SocialApp")
    else:
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=client_secret,
        )
        print("Created Google SocialApp")

    google_app.sites.set([site])
    print("Google SocialApp linked to site successfully")


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
