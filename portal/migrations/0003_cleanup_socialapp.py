from django.db import migrations
import os


def cleanup_google_socialapp(apps, schema_editor):
    """Delete all duplicate Google SocialApp rows. wsgi.py creates exactly one on startup."""
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    deleted, _ = SocialApp.objects.filter(provider='google').delete()
    print(f"Deleted {deleted} Google SocialApp row(s) — will be recreated by wsgi.py")


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0002_create_google_socialapp'),
    ]
    operations = [
        migrations.RunPython(cleanup_google_socialapp, migrations.RunPython.noop),
    ]
