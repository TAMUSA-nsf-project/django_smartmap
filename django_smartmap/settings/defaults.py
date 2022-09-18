"""
Django settings for django_smartmap project.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from pathlib import Path
import os
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

ALLOWED_HOSTS = []

DEBUG = False

env = environ.Env(
    DATABASE_URL=(str, os.getenv("DATABASE_URL")),
)

# Application definition

INSTALLED_APPS = [
    # My apps
    'main',
    'map',
    'bus',
    'users',
    'commons',
    'communications',

    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'phonenumber_field',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'django_smartmap.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'django_smartmap.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

"""
Logins
"""
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'main:index'  # needed to get the currently used login page to work

"""
Security
"""
CSRF_COOKIE_HTTPONLY = True  # for httponly alert
SESSION_COOKIE_SECURE = True  # cookie secure
SECURE_CONTENT_TYPE_NOSNIFF = True
# CSRF_COOKIE_SECURE = True  # to avoid transmitting the CSRF cookie over HTTP accidentally.
# SECURE_BROWSER_XSS_FILTER = True

CSP_DEFAULT_SRC = ("'self'", '')

CSP_STYLE_SRC = ("'self'", 'cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css',
                 'cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/css/bootstrap4-toggle.min.css',
                 'polyfill.io/v3/polyfill.min.js', 'fonts.googleapis.com',
                 'cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css', 'storage.googleapis.com')

CSP_SCRIPT_SRC = (
    "'self'", 'data:', 'cdnjs.cloudflare.com', 'https://maps.google.com', 'polyfill.io/v3/polyfill.min.js',
    'maps.googleapis.com',
    'https://storage.googleapis.com', 'cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.1/socket.io.js', 'cdn.jsdelivr.net')

CSP_CONNECT_SRC = ("'self'", 'cdnjs.cloudflare.com', 'cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.1/socket.io.js',
                   'maps.googleapis.com', 'polyfill.io/v3/polyfill.min.js',
                   'cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/js/bootstrap4-toggle.min.js')
CSP_FONT_SRC = (
    "'self'", 'data:', 'fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmEU9fChc4EsA.woff2', 'maps.googleapis.com',
    '*.gstatic.com', 'cdnjs.cloudflare.com/', 'storage.googleapis.com')
CSP_IMG_SRC = (
    "'self'", 'cdnjs.cloudflare.com', 'www.iconshock.com', 'maps.googleapis.com', 'maps.gstatic.com',
    '*.googleapis.com',
    'data:', 'blob:', '*.ggpht.com', 'storage.googleapis.com')

'''maps.gstatic.com/mapfiles/api-3/images/spotlight-poi2_hdpi.png
    cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/js/bootstrap4-toggle.min.js',
      '''
CSP_INCLUDE_NONCE_IN = (
    'script-src', 'connect-src', 'style-src', 'font-src', 'img-src')  # for inline javascript and style csss

CSP_FRAME_ANCESTORS = ("'none'")
CSP_PREFETCH_SRC = ("'none'")
CSP_FORM_ACTION = ("'self'")
CSP_OBJECT_SRC = ("'self'")
CSP_FRAME_SRC = ("'self'", 'maps.google.com', 'maps.googleapis.com')
CSP_MANIFEST_SRC = ("'none'")
CSP_MEDIA_SRC = ("'self'")
