"""
Django settings for core project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import os

load_dotenv()   

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ---------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gu^1pt(^9a3gv=gw2jtq@q=q0r!%g1$ia+)msfttf$75dz54dt'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    'core.apps.CoreConfig',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Local apps
    'users',
    'courses.apps.CoursesConfig',
    'quizzes',
    'forums',
    'chat',
    'home',

    # Third-party
    'channels',

    # Google Login
    'social_django',
]


# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'courses.middleware.ReminderMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ---------------------------------------------------------------------
# URL & Templates
# ---------------------------------------------------------------------
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Google Login
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'


# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bildung_db',
        'USER': 'root', # change with your MYSQL username
        'PASSWORD': '', # change with your MYSQL password
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# ---------------------------------------------------------------------
# Channels (Redis)
# ---------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    }
}


# ---------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------
AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/accounts/post-login/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True

SOCIALACCOUNT_ADAPTER = "users.adapters.CustomSocialAccountAdapter"

# Google OAuth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '' # Add your key  here
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''  # Add your client secret here
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'select_account',
    'access_type': 'offline',
}

SITE_ID = 1


# ---------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------
# Email (Development)
# ---------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Bildung Platform <noreply@bildung.com>'


# ---------------------------------------------------------------------
# Default PK
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------
# For Invite Link
# ---------------------------------------------------------------------
SITE_URL = 'http://127.0.0.1:8000'
