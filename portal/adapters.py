import os
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """Allow BrACU emails + Gmail for testing"""
        email = (sociallogin.account.extra_data.get('email') or '').lower().strip()
        
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