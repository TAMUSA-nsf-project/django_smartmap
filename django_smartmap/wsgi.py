"""
WSGI config for django_smartmap project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_smartmap.settings')

# I believe that the settings must be imported after the env var operation above
from django.conf import settings
import socketio

# Socket IO
sio = settings.SIO

django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)
