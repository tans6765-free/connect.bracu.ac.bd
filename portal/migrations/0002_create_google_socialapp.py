from django.db import migrations


def create_google_socialapp(apps, schema_editor):
    # Intentionally left empty — SocialApp is now created in wsgi.py
    # at runtime so credentials from env vars are always current.
    # This migration just ensures the dependency chain is correct.
    pass


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