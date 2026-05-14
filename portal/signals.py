import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_out
from django.contrib.messages import get_messages
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from allauth.account.signals import user_logged_in
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)
ALLOWED_EMAIL = 'md.tahsinul.islam@g.bracu.ac.bd'


def get_social_email(sociallogin):
    """Extract email from social login data."""
    # Try getting from user.email first
    email = (getattr(sociallogin.user, 'email', '') or '').strip().lower()
    if email:
        return email

    # Try getting from extra_data
    extra_data = getattr(sociallogin.account, 'extra_data', {}) or {}
    email = extra_data.get('email') or extra_data.get('emailAddress')
    if email:
        return str(email).strip().lower()

    return ''


@receiver(pre_social_login)
def validate_google_email(sender, request, sociallogin, **kwargs):
    """
    Validate Google OAuth login - ONLY allow the specified email.
    This handler blocks unauthorized users from logging in.
    """
    try:
        # Extract the email from the social login
        email = get_social_email(sociallogin)
        
        logger.info(f"Pre-social-login: Processing email: {email}")

        # CRITICAL: Only allow the whitelisted email
        if email.lower() != ALLOWED_EMAIL.lower():
            logger.warning(f"BLOCKING unauthorized social login attempt for email: {email}")
            # Raise exception to prevent login
            raise ValidationError(
                f'Access denied. Only {ALLOWED_EMAIL} is authorized to access this portal.'
            )

        # Email is allowed - auto-create/connect user if needed
        logger.info(f"APPROVED social login for email: {email}")
        
        User = get_user_model()
        
        # Check if user exists
        try:
            user = User.objects.get(email__iexact=email)
            logger.info(f"Found existing user with email: {email}")
        except User.DoesNotExist:
            # Create new user for the allowed email
            extra_data = getattr(sociallogin.account, 'extra_data', {}) or {}
            user = User(
                email=email,
                username=email,
                first_name=(extra_data.get('given_name') or '').strip(),
                last_name=(extra_data.get('family_name') or '').strip(),
            )
            user.set_unusable_password()
            user.save()
            logger.info(f"Created new user with email: {email}")
        
        # Populate the sociallogin.user with the correct user
        sociallogin.user = user
        
    except ValidationError:
        raise  # Re-raise to prevent login
    except Exception as e:
        logger.error(f"Error in validate_google_email: {e}", exc_info=True)
        raise ValidationError("An error occurred during authentication. Please try again.")


@receiver(user_logged_out)
def clear_messages_on_logout(sender, request, user, **kwargs):
    """Clear all messages when user logs out to prevent stale messages on login page."""
    try:
        for message in get_messages(request):
            # Iterate through all messages to mark them as read/consumed
            pass
        logger.info(f"Cleared messages for logged out user: {user}")
    except Exception as e:
        logger.warning(f"Error clearing messages on logout: {e}")
