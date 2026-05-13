"""
Django management command to setup Google OAuth in the database.

This command:
1. Reads GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET from environment
2. Creates or updates the Google SocialApp in the database
3. Links it to the correct Site

Usage:
    python manage.py setup_google_oauth

Place this file at: portal/management/commands/setup_google_oauth.py

Directory structure needed:
portal/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── setup_google_oauth.py
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Setup Google OAuth SocialApp from environment variables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site-domain',
            type=str,
            default='connectbracuacbd.vercel.app',
            help='Site domain for the OAuth app'
        )
        parser.add_argument(
            '--site-name',
            type=str,
            default='BRAC University Portal',
            help='Site name'
        )

    def handle(self, *args, **options):
        # Get environment variables
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
        
        site_domain = options['site_domain']
        site_name = options['site_name']
        
        # Validate credentials
        if not client_id or not client_secret:
            raise CommandError(
                'ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment '
                'variables must be set. Got:\n'
                f'  GOOGLE_CLIENT_ID: {"SET" if client_id else "NOT SET"}\n'
                f'  GOOGLE_CLIENT_SECRET: {"SET" if client_secret else "NOT SET"}'
            )
        
        self.stdout.write(
            self.style.WARNING(
                f'Setting up Google OAuth for domain: {site_domain}'
            )
        )
        
        try:
            # Get or create site
            site, site_created = Site.objects.get_or_create(
                id=1,
                defaults={
                    'domain': site_domain,
                    'name': site_name,
                }
            )
            
            if site_created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created new site: {site.domain}')
                )
            else:
                # Update existing site if domain changed
                if site.domain != site_domain:
                    site.domain = site_domain
                    site.name = site_name
                    site.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Updated site domain to: {site.domain}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Using existing site: {site.domain}')
                    )
            
            # Delete old Google app if it exists (to avoid conflicts)
            old_apps = SocialApp.objects.filter(provider='google')
            if old_apps.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Found {old_apps.count()} existing Google app(s). '
                        'Replacing with new configuration...'
                    )
                )
                old_apps.delete()
            
            # Create new Google app
            app = SocialApp.objects.create(
                provider='google',
                name='Google OAuth',
                client_id=client_id,
                secret=client_secret,
            )
            
            # Link app to site
            app.sites.add(site)
            app.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ Google OAuth successfully configured!\n'
                    f'  Provider: Google\n'
                    f'  Client ID: {client_id[:20]}...\n'
                    f'  Secret: {"SET" if client_secret else "NOT SET"}\n'
                    f'  Site: {site.domain}\n'
                )
            )
            
            # Print next steps
            self.stdout.write(
                self.style.SUCCESS(
                    '\n📋 Next steps:\n'
                    '1. Run migrations: python manage.py migrate\n'
                    '2. Restart your Django server\n'
                    '3. Test the Google login button\n'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Error setting up Google OAuth: {str(e)}')
