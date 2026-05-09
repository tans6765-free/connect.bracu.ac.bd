"""
Auto-create Google OAuth SocialApp from environment variables.
This runs on every deployment and ensures allauth has the credentials it needs.
"""

from django.db import migrations
import os


def create_google_socialapp(apps, schema_editor):
    """Create Google OAuth SocialApp if it doesn't exist"""
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')
    
    # Get client ID and secret from env vars
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    # Only create if we have both credentials
    if not client_id or not client_secret:
        print("⚠️  Skipping Google SocialApp creation: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set")
        return
    
    # Check if Google app already exists
    google_app = SocialApp.objects.filter(provider='google').first()
    if google_app:
        print("✓ Google SocialApp already exists, updating credentials...")
        google_app.client_id = client_id
        google_app.secret = client_secret
        google_app.save()
        return
    
    # Get the default site
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        print("✓ Creating default Site...")
        site = Site.objects.create(pk=1, domain='bracu.connect.bd', name='BRAC Portal')
    
    # Create Google SocialApp
    print("✓ Creating Google SocialApp...")
    google_app = SocialApp.objects.create(
        provider='google',
        name='Google',
        client_id=client_id,
        secret=client_secret,
    )
    google_app.sites.add(site)
    print(f"✓ Google SocialApp created successfully")


def reverse_google_socialapp(apps, schema_editor):
    """Remove Google SocialApp (for rollback)"""
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    SocialApp.objects.filter(provider='google').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_google_socialapp, reverse_google_socialapp),
    ]
