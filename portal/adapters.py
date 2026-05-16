"""
Custom Django-allauth adapter for Google OAuth.
- Reads CLIENT_ID and SECRET from environment variables (no DB SocialApp needed)
- Enforces email whitelist: only md.tahsinul.islam@g.bracu.ac.bd is allowed
- Auto links social account to existing Django user by email
"""

import os
import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import User
from django.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

ALLOWED_EMAIL = 'md.tahsinul.islam@g.bracu.ac.bd'


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for Google OAuth:
    1. Gets client_id/secret from environment variables directly
    2. Only allows the whitelisted BRAC email
    3. Links social account to existing user by email
    """

    def get_app(self, request, provider, client_id=None):
        """
        Override to provide the app config from environment variables.
        This means NO SocialApp entry in the database is required.
        """
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()

        if not google_client_id:
            logger.error("GOOGLE_CLIENT_ID environment variable is not set!")

        # Try to get from DB first (allows admin override)
        try:
            app = SocialApp.objects.get(provider='google')
            # Update from env if env has values
            if google_client_id and app.client_id != google_client_id:
                app.client_id = google_client_id
                app.secret = google_client_secret
                app.save()
            return app
        except SocialApp.DoesNotExist:
            pass
        except SocialApp.MultipleObjectsReturned:
            app = SocialApp.objects.filter(provider='google').first()
            return app

        # Create on-the-fly from environment variables
        try:
            site = Site.objects.get_or_create(
                id=1,
                defaults={
                    'domain': os.environ.get('VERCEL_URL', 'localhost:8000'),
                    'name': 'BRAC University Portal',
                }
            )[0]

            app = SocialApp(
                provider='google',
                name='Google OAuth',
                client_id=google_client_id,
                secret=google_client_secret,
            )
            app.save()
            app.sites.add(site)
            logger.info(f"Created Google SocialApp from env vars. Client ID: {google_client_id[:20]}...")
            return app
        except Exception as e:
            logger.exception(f"Failed to create Google SocialApp: {e}")
            raise

    def is_auto_signup_allowed(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email', '').strip().lower()
        if email == ALLOWED_EMAIL.lower():
            return True
        logger.warning(f"Auto-signup rejected for unauthorized email: {email}")
        return False

    def pre_social_login(self, request, sociallogin):
        """
        Called before login. Enforces whitelist and links accounts by email.
        """
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get('email', '').strip().lower()

        # Enforce whitelist
        if email != ALLOWED_EMAIL.lower():
            logger.warning(f"Blocked social login for: {email}")
            raise ImmediateHttpResponse(
                redirect('/accounts/login/?error=unauthorized')
            )

        # Link to existing user
        try:
            existing_user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, existing_user)
            logger.info(f"Linked social account to existing user: {email}")
        except User.DoesNotExist:
            pass
        except Exception as e:
            logger.exception(f"Error linking social account: {e}")

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        extra = sociallogin.account.extra_data
        user.first_name = extra.get('given_name', '')
        user.last_name = extra.get('family_name', '')
        user.email = extra.get('email', user.email)
        user.save()
        return user

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.email:
            user.email = data.get('email', '')
        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True
