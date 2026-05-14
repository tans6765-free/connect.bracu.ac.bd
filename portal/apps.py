from django.apps import AppConfig
from django.conf import settings
import os


class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'

    def ready(self):
        """Import signals and setup OAuth when app is ready."""
        import portal.signals  # noqa
        
        # Auto-setup Google OAuth from environment variables
        self._setup_google_oauth_on_startup()
    
    def _setup_google_oauth_on_startup(self):
        """Auto-configure Google OAuth if credentials are available."""
        # Import Django models INSIDE the method, after app registry is ready
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp
        
        try:
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            
            # Only setup if both credentials are provided
            if not client_id or not client_secret:
                return
            
            # Get current domain
            if os.environ.get('DEBUG') == 'True' or os.environ.get('DEBUG') == '1':
                domain = 'localhost:8000'
            else:
                vercel_url = os.environ.get('VERCEL_URL', '')
                domain = vercel_url or settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'example.com'
            
            # Setup Site
            site, _ = Site.objects.get_or_create(
                pk=settings.SITE_ID,
                defaults={
                    'domain': domain,
                    'name': 'BRAC University Portal'
                }
            )
            if site.domain != domain:
                site.domain = domain
                site.name = 'BRAC University Portal'
                site.save()
            
            # Setup SocialApp for Google OAuth
            app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google OAuth',
                    'client_id': client_id,
                    'secret': client_secret,
                }
            )
            
            # Update credentials if they changed
            if app.client_id != client_id or app.secret != client_secret:
                app.client_id = client_id
                app.secret = client_secret
                app.save()
            
            # Link SocialApp to Site
            if site not in app.sites.all():
                app.sites.add(site)
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not auto-setup Google OAuth: {e}")