from .defaults import *
import io
from google.cloud import secretmanager
import google.auth
from urllib.parse import urlparse

DEBUG = os.getenv("DEBUG", default="False") == "True"
DEBUG = True

# Attempt to load the Project ID into the environment, safely failing on error.
try:
    _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    print("DefaultCredentialsError")
    pass
# Use GCP secret manager in prod mode
if os.getenv("GOOGLE_CLOUD_PROJECT", None):
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    service_type = os.getenv("GOOGLE_CLOUD_SERVICE_TYPE", default="CE")
    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.getenv("SETTINGS_NAME", f"application_settings{service_type}")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode(
        "UTF-8"
    )

    env.read_env(io.StringIO(payload))
    print("Loaded secret settings" + name + env("CLOUDRUN_SERVICE_URL", default=None))
else:
    raise Exception(
        "No GOOGLE_CLOUD_PROJECT detected. No secrets found."
    )

SECRET_KEY = env("SECRET_KEY")

# [START cloudrun_django_csrf]
# SECURITY WARNING: It's recommended that you use this when
# running in production. The URL will be known once you first deploy
# to Cloud Run. This code takes the URL and converts it to both these settings formats.

CLOUDRUN_SERVICE_URL = env("CLOUDRUN_SERVICE_URL", default=None)
# Adding this for testing the URL. This needs to be moved to secret manager later
DOMAIN_URL = "https://www.mysmartsa.com"
if CLOUDRUN_SERVICE_URL:
    ALLOWED_HOSTS = [urlparse(CLOUDRUN_SERVICE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [CLOUDRUN_SERVICE_URL]
    # SECURE_SSL_REDIRECT = True
    # SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
print(ALLOWED_HOSTS, )
INSTALLED_APPS += ['storages']

# Database
# Use django-environ to parse the connection string
# DATABASE_URL=psql://<username>:<password>@<host>:<port>/<database_name>
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME_DJANGO'),
        'USER': env('DB_USER_DJANGO'),
        'PASSWORD': env('DB_PASSWORD_DJANGO'),
        'HOST': env('CLOUD_SQL_INSTANCE_IP'),
        'PORT': 5432,
    }}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATICFILES_DIRS = []

GS_BUCKET_NAME = env("GS_BUCKET_NAME")
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_DEFAULT_ACL = "publicRead"
STATIC_URL = 'https://storage.googleapis.com/{}/'.format(GS_BUCKET_NAME)

"""
GOOGLE API KEYS GO HERE:
"""
# For the map (restricted to our server's addresses)
GOOGLE_MAP_API_KEY = env("GOOGLE_MAP_API_KEY")

# For the server-side Python Client for Google Maps Services (an unrestricted key, as required)
GOOGLE_PYTHON_API_KEY = env("GOOGLE_PYTHON_API_KEY")

"""
TWILIO API KEYS
"""
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")
