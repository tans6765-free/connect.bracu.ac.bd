import os
from django.core.exceptions import MultipleObjectsReturned
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """Allow BrACU emails + Gmail for testing"""
        email = sociallogin.account.extra_data.get('email')
        if not email:
            email = sociallogin.account.extra_data.get('emailAddress')
        if not email:
            emails = sociallogin.account.extra_data.get('emails') or sociallogin.account.extra_data.get('emailAddresses')
            if isinstance(emails, (list, tuple)) and emails:
                first = emails[0]
                if isinstance(first, str):
                    email = first
                elif isinstance(first, dict):
                    email = first.get('value') or first.get('email') or first.get('address')
        if not email:
            email = getattr(sociallogin.user, 'email', None)
        email = (email or '').lower().strip()

        if not email:
            return False

        # Allow everything in DEBUG mode or on Vercel for testing
        if settings.DEBUG or os.environ.get('VERCEL'):
            return True

        # Production: Only BrACU emails
        if email.endswith('@g.bracu.ac.bd') or email.endswith('@bracu.ac.bd'):
            return True

        return False

    def authentication_allowed(self, request, sociallogin):
        """This is the key method that blocks login"""
        return self.is_open_for_signup(request, sociallogin)

    def get_app(self, request, provider, client_id=None):
        """Return a single SocialApp row and clean up duplicates if found."""
        try:
            return super().get_app(request, provider, client_id)
        except MultipleObjectsReturned:
            apps = SocialApp.objects.filter(provider=provider)
            if client_id:
                apps = apps.filter(client_id=client_id)
            app = apps.order_by('id').first()
            if not app:
                raise
            apps.exclude(pk=app.pk).delete()
            return app
