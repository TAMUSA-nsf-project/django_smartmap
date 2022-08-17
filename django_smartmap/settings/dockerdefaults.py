from .defaults import *

import io
from urllib.parse import urlparse
import environ
import google.auth
from google.cloud import secretmanager

DEBUG = os.getenv("DEBUG", default="False") == "True"

env = environ.Env(
    SECRET_KEY=(str, os.getenv("SECRET_KEY")),
    DATABASE_URL=(str, os.getenv("DATABASE_URL")),
    GS_BUCKET_NAME=(str, os.getenv("GS_BUCKET_NAME", default=None)),
)

# Attempt to load the Project ID into the environment, safely failing on error.
try:
    _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    pass

# Use GCP secret manager in prod mode
if os.getenv("GOOGLE_CLOUD_PROJECT", None):
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.getenv("SETTINGS_NAME", "application_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode(
        "UTF-8"
    )

    env.read_env(io.StringIO(payload))
elif not DEBUG:
    raise Exception(
        "No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found."
    )

SECRET_KEY = env("SECRET_KEY")

# [START cloudrun_django_csrf]
# SECURITY WARNING: It's recommended that you use this when
# running in production. The URL will be known once you first deploy
# to Cloud Run. This code takes the URL and converts it to both these settings formats.

CLOUDRUN_SERVICE_URL = env("CLOUDRUN_SERVICE_URL", default=None)
if not DEBUG and CLOUDRUN_SERVICE_URL:
    ALLOWED_HOSTS = [urlparse(CLOUDRUN_SERVICE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [CLOUDRUN_SERVICE_URL]
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS += ['storages']

# Add sslserevr app if running dev mode
if DEBUG:
    INSTALLED_APPS += ['sslserver']

# Database
# Use django-environ to parse the connection string
# DATABASE_URL=psql://<username>:<password>@<host>:<port>/<database_name>
DATABASES = {"default": env.db()}

# If the flag as been set, configure to use proxy
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", "False") == "True":
    DATABASES["default"]["HOST"] = "cloudsql-proxy"
    DATABASES["default"]["PORT"] = 5432

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATICFILES_DIRS = []
if os.getenv("GS_BUCKET_NAME", None):
    GS_BUCKET_NAME = env("GS_BUCKET_NAME")
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_DEFAULT_ACL = "publicRead"
else:
    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ]
    STATIC_ROOT = str(BASE_DIR / "static")


"""
GOOGLE API KEYS GO HERE:
"""
# For the map (restricted to our server's addresses)
GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")

# For the server-side Python Client for Google Maps Services (an unrestricted key, as required)
GOOGLE_PYTHON_API_KEY = os.getenv("GOOGLE_PYTHON_API_KEY")


