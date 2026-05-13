import logging
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.signals import user_logged_out
from django.contrib.messages import get_messages

logger = logging.getLogger(__name__)
ALLOWED_EMAIL = 'md.tahsinul.islam@g.bracu.ac.bd'


def ensure_correct_site_config():
    """Ensure site domain and SocialApp are correctly configured."""
    try:
        site, _ = Site.objects.get_or_create(id=1)
        # Update site to match the app
        if site.domain != 'connectbracuacbd.vercel.app' and site.domain != 'localhost:8000':
            logger.info(f"Updating site domain from '{site.domain}' to 'connectbracuacbd.vercel.app'")
            site.domain = 'connectbracuacbd.vercel.app'
            site.name = 'BracU Portal'
            site.save()
        
        # Ensure Google SocialApp is linked to the correct site
        google_apps = SocialApp.objects.filter(provider='google')
        for app in google_apps:
            if not app.sites.filter(id=1).exists():
                logger.info("Adding site to Google SocialApp")
                app.sites.add(site)
    except Exception as e:
        logger.warning(f"Error in ensure_correct_site_config: {e}")


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


def create_or_connect_user(request, sociallogin, email):
    """Create user if doesn't exist, then connect the social account."""
    User = get_user_model()
    try:
        # Try to get existing user by email
        user = User.objects.get(email__iexact=email)
        logger.info(f"Found existing user with email: {email}")
    except User.DoesNotExist:
        # Create new user
        user = User(
            email=email,
            username=email,
            first_name=(sociallogin.account.extra_data.get('given_name') or '').strip(),
            last_name=(sociallogin.account.extra_data.get('family_name') or '').strip(),
        )
        user.set_unusable_password()
        user.save()
        logger.info(f"Created new user with email: {email}")

    # Connect social account to user
    if not sociallogin.is_existing:
        sociallogin.connect(request, user)
        logger.info(f"Connected social login to user: {email}")
    
    return user


@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    """
    Handle Google social logins before authentication.
    ONLY allow the specified email address.
    """
    try:
        ensure_correct_site_config()
        
        email = get_social_email(sociallogin)
        logger.info(f"Pre-social-login: Processing email: {email}")

        # IMPORTANT: Only allow the whitelisted email
        if email.lower() != ALLOWED_EMAIL.lower():
            logger.warning(f"Rejecting social login for unauthorized email: {email}")
            # Don't raise exception - just don't connect the user
            # The user will see the normal allauth flow
            return

        # Email is allowed - create/connect user
        logger.info(f"Approved social login for email: {email}")
        create_or_connect_user(request, sociallogin, email)

    except Exception as e:
        logger.exception(f"Error in pre_social_login_handler: {e}")


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
