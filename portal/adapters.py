from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Handle Google OAuth with optional email domain restriction.
    In development (DEBUG=True), allows all emails.
    In production, restricts to @g.bracu.ac.bd unless configured otherwise.
    """
    ALLOWED_DOMAIN = getattr(settings, 'ALLOWED_EMAIL_DOMAIN', 'g.bracu.ac.bd')

    def _email_allowed(self, email):
        """Check if email is allowed to sign up."""
        if not email:
            logger.warning("No email found in social account data")
            return False
        
        # In development, allow all emails
        if settings.DEBUG:
            logger.info(f"DEBUG mode: allowing email {email}")
            return True
        
        # In production, restrict to allowed domain
        allowed = email.lower().endswith('@' + self.ALLOWED_DOMAIN)
        if not allowed:
            logger.warning(f"Email {email} not in allowed domain {self.ALLOWED_DOMAIN}")
        return allowed

    def is_open_for_signup(self, request, sociallogin):
        """Allow signup if email is in allowed domain."""
        try:
            email = sociallogin.account.extra_data.get('email') or sociallogin.user.email
            return self._email_allowed(email)
        except Exception as e:
            logger.error(f"Error checking signup eligibility: {e}")
            # Default to True in development, False in production
            return settings.DEBUG

    def authentication_allowed(self, request, sociallogin):
        """Allow authentication if email is in allowed domain."""
        try:
            email = sociallogin.account.extra_data.get('email') or sociallogin.user.email
            return self._email_allowed(email)
        except Exception as e:
            logger.error(f"Error checking authentication eligibility: {e}")
            # Default to True in development, False in production
            return settings.DEBUG

    def save_user(self, request, sociallogin, form=None):
        """Save user from social account."""
        try:
            user = super().save_user(request, sociallogin, form)
            logger.info(f"User {user.username} saved from social account")
            return user
        except Exception as e:
            logger.error(f"Error saving user from social account: {e}")
            raise
