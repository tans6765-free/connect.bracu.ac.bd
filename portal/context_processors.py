import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def portal_context(request):
    """
    Inject portal-wide context into all templates.
    Reads Google Client ID from environment variable directly — no DB query needed.
    """
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()

    # Fallback: try DB if env not set
    if not google_client_id:
        try:
            from allauth.socialaccount.models import SocialApp
            app = SocialApp.objects.filter(provider='google').first()
            if app:
                google_client_id = app.client_id
        except Exception:
            pass

    ctx = {
        'google_client_id': google_client_id,
        'DEBUG': settings.DEBUG,
        'SITE_NAME': 'BRAC University Portal',
    }

    # Add logged-in user info for topbar/sidebar
    if request.user.is_authenticated:
        ctx['user_full_name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        ctx['user_email'] = request.user.email
    
    return ctx
