import logging
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_updated
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

logger = logging.getLogger(__name__)
ALLOWED_EMAIL = 'md.tahsinul.islam@g.bracu.ac.bd'

def ensure_correct_site_config():
    """Ensure site domain and SocialApp are correctly configured"""
    try:
        site, _ = Site.objects.get_or_create(id=1)
        if site.domain != 'connectbracuacbd.vercel.app':
            logger.warning(f"[Fix] Fixing site domain from '{site.domain}' to 'connectbracuacbd.vercel.app'")
            site.domain = 'connectbracuacbd.vercel.app'
            site.name = 'BracU Portal'
            site.save()
        
        # Ensure Google SocialApp is linked to the correct site
        google_apps = SocialApp.objects.filter(provider='google')
        for app in google_apps:
            if not app.sites.filter(id=1).exists():
                logger.warning(f"[Fix] Adding site to Google SocialApp")
                app.sites.add(site)
    except Exception as e:
        logger.exception(f"[Fix] Error in ensure_correct_site_config: {e}")


def get_social_email(sociallogin):
    email = (getattr(sociallogin.user, 'email', '') or '').strip().lower()
    if email:
        return email

    extra_data = getattr(sociallogin.account, 'extra_data', {}) or {}
    email = extra_data.get('email') or extra_data.get('emailAddress')
    if email:
        return str(email).strip().lower()

    return ''


def create_or_connect_user(request, sociallogin, email):
    User = get_user_model()
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        user = User(
            email=email,
            username=email,
            first_name=(sociallogin.account.extra_data.get('given_name') or '').strip(),
            last_name=(sociallogin.account.extra_data.get('family_name') or '').strip(),
        )
        user.set_unusable_password()
        user.save()

    if not sociallogin.is_existing:
        sociallogin.connect(request, user)
    return user


@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    """Handle Google social logins before authentication"""
    try:
        ensure_correct_site_config()
        email = get_social_email(sociallogin)
        logger.info(f"[Signal] pre_social_login triggered for email: {email}")

        if email != ALLOWED_EMAIL:
            logger.warning(f"[Signal] Blocking social login for unauthorized email: {email}")
            return

        create_or_connect_user(request, sociallogin, email)
        logger.info(f"[Signal] Connected social login to user {email}")
    except Exception as e:
        logger.exception(f"[Signal] Error in pre_social_login_handler: {e}")


@receiver(social_account_updated)
def social_account_updated_handler(sender, request, sociallogin, **kwargs):
    """Log OAuth account updates"""
    try:
        logger.info(f"[Signal] social_account_updated triggered for {sociallogin.account.provider}")
    except Exception as e:
        logger.exception(f"[Signal] Error in social_account_updated_handler: {e}")
