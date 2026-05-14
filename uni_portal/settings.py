from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-prod')

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
if os.environ.get('VERCEL'):
    DEBUG = False  # Disable DEBUG on Vercel

ALLOWED_HOSTS = [
    'connectbracuacbd.vercel.app',
    'localhost',
    '127.0.0.1',
    '*.vercel.app',
] if not DEBUG else ['*']

# ═══════════════════════════════════════════════════════════════════════════
# CSRF & COOKIE SECURITY - FIXED FOR OAUTH
# ═══════════════════════════════════════════════════════════════════════════

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://connectbracuacbd.vercel.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# CSRF Protection
CSRF_COOKIE_SECURE = DEBUG == False
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'  # CRITICAL: Allow OAuth redirect from Google

# ═══════════════════════════════════════════════════════════════════════════
# SESSION CONFIGURATION - FIXED FOR LOGIN PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════

# Use database-backed sessions (not signed_cookies)
# This allows sessions to persist across requests and be refreshed
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_AGE = 30 * 24 * 60 * 60  # 30 days
SESSION_COOKIE_NAME = 'bracu_sessionid'
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SECURE = DEBUG == False  # HTTPS only in production
SESSION_COOKIE_SAMESITE = 'Lax'  # Allow OAuth redirect
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep sessions alive

# CRITICAL FIX: Refresh session on every request
# This prevents "you were logged out" situations
SESSION_SAVE_EVERY_REQUEST = True

# ═══════════════════════════════════════════════════════════════════════════
# SECURITY HEADERS
# ═══════════════════════════════════════════════════════════════════════════

SECURE_SSL_REDIRECT = not DEBUG and not os.environ.get('VERCEL')
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',  # CRITICAL: Must be here for session backend
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'portal',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # SessionMiddleware MUST come before AuthenticationMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Auth middlewares must come after session
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'portal.middleware.VercelExceptionLoggingMiddleware',
]

ROOT_URLCONF = 'uni_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'portal' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'portal.context_processors.google_oauth',  # Pass google_client_id to templates
            ],
        },
    },
]

WSGI_APPLICATION = 'uni_portal.wsgi.application'

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

if os.environ.get('VERCEL'):
    # On Vercel, use PostgreSQL if available, otherwise SQLite in /tmp
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Use PostgreSQL
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=db_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    else:
        # Fallback to SQLite in /tmp
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/tmp/db.sqlite3',
            }
        }
else:
    # Local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ═══════════════════════════════════════════════════════════════════════════
# STATIC FILES
# ═══════════════════════════════════════════════════════════════════════════

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'portal' / 'static']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# ═══════════════════════════════════════════════════════════════════════════
# ALLAUTH / GOOGLE OAUTH - AUTO-CONFIGURED FROM ENV VARS
# ═══════════════════════════════════════════════════════════════════════════

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email settings
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True

# Auto signup for Google accounts
SOCIALACCOUNT_AUTO_SIGNUP = True

# Use custom adapter for better OAuth handling
SOCIALACCOUNT_ADAPTER = 'portal.adapters.CustomSocialAccountAdapter'

# Store OAuth tokens for future use
SOCIALACCOUNT_STORE_TOKENS = True

# Google OAuth Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'VERIFIED_EMAIL': True,
        'VERSION': 'v2',
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# AUTO-SETUP GOOGLE OAUTH ON STARTUP
# ═══════════════════════════════════════════════════════════════════════════
def setup_google_oauth_on_startup():
    """Auto-setup Google OAuth SocialApp from environment variables."""
    import os
    from django.contrib.sites.models import Site
    from allauth.socialaccount.models import SocialApp
    
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
    
    if not client_id or not client_secret:
        return  # Skip if credentials not set
    
    try:
        # Determine site domain based on environment
        if os.environ.get('VERCEL'):
            site_domain = os.environ.get('VERCEL_URL', 'connectbracuacbd.vercel.app')
        else:
            site_domain = 'localhost:8000'
        
        # Get or create site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': site_domain,
                'name': 'BRAC University Portal',
            }
        )
        
        # Check if Google SocialApp already exists
        google_apps = SocialApp.objects.filter(provider='google')
        
        if google_apps.exists():
            # Update existing app
            app = google_apps.first()
            app.client_id = client_id
            app.secret = client_secret
            app.save()
        else:
            # Create new app
            app = SocialApp.objects.create(
                provider='google',
                name='Google OAuth',
                client_id=client_id,
                secret=client_secret,
            )
        
        # Link app to site if not already linked
        if not app.sites.filter(id=1).exists():
            app.sites.add(site)
        
        # Also update site domain if it changed
        if site.domain != site_domain:
            site.domain = site_domain
            site.save()
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not auto-setup Google OAuth: {e}")

# Run on startup (after apps are ready)
from django.core.signals import ready
from django.dispatch import receiver
from django.apps import AppConfig

@receiver(ready, dispatch_uid='setup_google_oauth')
def setup_on_ready(sender, **kwargs):
    setup_google_oauth_on_startup()

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Note: Google OAuth auto-setup is defined above in settings.py

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING (Optional - for debugging)
# ═══════════════════════════════════════════════════════════════════════════

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if not DEBUG else 'DEBUG',
    },
}
