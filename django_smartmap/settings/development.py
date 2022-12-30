from .defaults import *

DEBUG = True


env.read_env(env_file=os.path.join(BASE_DIR, "env", "local.env"))


SECRET_KEY = os.getenv("SECRET_KEY", "NoxUmTUaQ7BvTPxIlKaQTTQvHS3aQBO3aV5zBKqrHuP6gZyyYZ")

INSTALLED_APPS += ['sslserver']
ALLOWED_HOSTS = ['*']

SYNC_BUS_SCHEDULES = False

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# If the flag as been set, configure to use proxy
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", "False") == "True":
    DATABASES["default"]["HOST"] = "cloudsql-proxy"
    DATABASES["default"]["PORT"] = 5432


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATICFILES_DIRS = []

if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", "False") == "True":
    GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME")
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_DEFAULT_ACL = "publicRead"
    STATIC_URL = 'https://storage.googleapis.com/{}/'.format(GS_BUCKET_NAME)
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
GOOGLE_MAP_API_KEY = env("GOOGLE_MAP_API_KEY")

# For the server-side Python Client for Google Maps Services (an unrestricted key, as required)
GOOGLE_PYTHON_API_KEY = env("GOOGLE_PYTHON_API_KEY")


"""
TWILIO
"""
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")
