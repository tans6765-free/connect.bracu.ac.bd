from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = not os.environ.get('VERCEL')

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://connectbraucacbd.vercel.app',
    'https://bracu.connect.bd',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'uni_portal.wsgi.application'

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

# -----------------------------------------------------------------------
# STATIC FILES — Vercel-safe configuration
#
# KEY FACTS about Vercel serverless:
#   /var/task  = your deployed code, READ-ONLY, always available at runtime
#   /tmp       = writable, but WIPED between cold starts
#
# WHY ManifestStaticFilesStorage fails:
#   It writes staticfiles.json to STATIC_ROOT during collectstatic.
#   Even if collectstatic runs in build.sh writing to /tmp/staticfiles,
#   /tmp is reset before any request arrives, so the manifest is gone.
#
# SOLUTION:
#   1. Use plain StaticFilesStorage — no manifest, no hashing, no file writes.
#      {% static 'css/style.css' %} simply returns '/static/css/style.css'.
#   2. WhiteNoise serves files directly from portal/static (inside /var/task,
#      always readable) via WHITENOISE_ROOT.
#   3. STATIC_ROOT still set so collectstatic doesn't crash, but never read.
# -----------------------------------------------------------------------

STATIC_URL = '/static/'

# Plain storage: no manifest, no hashing, just prepends STATIC_URL
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Source static files live inside /var/task — readable at runtime on Vercel
STATICFILES_DIRS = [BASE_DIR / 'portal' / 'static']

# WhiteNoise serves /static/* directly from this directory at runtime
WHITENOISE_ROOT = str(BASE_DIR / 'portal' / 'static')
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# collectstatic target — only used during build, NEVER read at runtime
STATIC_ROOT = '/tmp/staticfiles'

# -----------------------------------------------------------------------
# AUTH / ALLAUTH
# -----------------------------------------------------------------------
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = 'portal.adapters.CustomSocialAccountAdapter'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        },
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
