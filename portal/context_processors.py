"""
Context processor to make Google OAuth configuration available in templates.

Place this file at: portal/context_processors.py
"""

from django.conf import settings
from allauth.socialaccount.models import SocialApp


def google_oauth(request):
    """
    Pass Google OAuth configuration to all templates.
    
    This makes the following variables available in templates:
    - google_client_id: The Google Client ID (or None if not configured)
    - DEBUG: Whether Django is in debug mode
    - SITE_NAME: Name of the site
    """
    try:
        # Try to get the Google SocialApp from database
        # This is the authoritative source configured in Django Admin
        google_app = SocialApp.objects.get(provider='google')
        google_client_id = google_app.client_id if google_app else None
    except SocialApp.DoesNotExist:
        # Google OAuth not configured in Django Admin
        google_client_id = None
    except Exception as e:
        # Error accessing database (shouldn't happen in normal operation)
        google_client_id = None
        print(f"Error getting Google SocialApp: {e}")
    
    return {
        'google_client_id': google_client_id,
        'DEBUG': settings.DEBUG,
        'SITE_NAME': 'BRAC University Portal',
    }
