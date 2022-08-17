from .defaults import *

# From command line:  pip install -r requirements.txt
from dotenv import load_dotenv

# Load settings from .env
dotenv_path = os.path.join(BASE_DIR, "env", "sqlitedev.env")
load_dotenv(dotenv_path=dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")
GOOGLE_PYTHON_API_KEY = os.getenv("GOOGLE_PYTHON_API_KEY")

DEBUG = True

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


