"""
Management command to setup Google OAuth from environment variables.
Run automatically in build.sh, or manually:
    python manage.py setup_google_oauth
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Setup Google OAuth SocialApp from environment variables'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force recreate even if exists')

    def handle(self, *args, **options):
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
        vercel_url = os.environ.get('VERCEL_URL', '').strip()
        is_vercel = bool(os.environ.get('VERCEL'))

        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR(
                'GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not set. '
                'Google login will not work!'
            ))
            return

        # Determine site domain
        if vercel_url:
            site_domain = vercel_url.replace('https://', '').replace('http://', '').rstrip('/')
        elif is_vercel:
            site_domain = 'connectbracuacbd.vercel.app'
        else:
            site_domain = 'localhost:8000'

        site_name = 'BRAC University Portal'

        # Update or create site
        site, _ = Site.objects.get_or_create(id=1, defaults={
            'domain': site_domain,
            'name': site_name,
        })
        if site.domain != site_domain:
            site.domain = site_domain
            site.name = site_name
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Updated site domain → {site_domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Site: {site_domain}'))

        # Create or update Google SocialApp
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        if not created:
            app.client_id = client_id
            app.secret = client_secret
            app.name = 'Google OAuth'
            app.save()

        # Make sure site is linked
        if not app.sites.filter(id=1).exists():
            app.sites.add(site)

        status = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{status} Google SocialApp — Client ID: {client_id[:20]}...'
        ))
        self.stdout.write(self.style.SUCCESS('✓ Google OAuth configured successfully!'))
