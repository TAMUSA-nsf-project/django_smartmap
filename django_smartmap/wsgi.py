"""
WSGI config for django_smartmap project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import socketio
from map.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_transit.settings')

django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)
