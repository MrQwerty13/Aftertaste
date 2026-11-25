"""WSGI config for the Aftertaste project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aftertaste.settings")

application = get_wsgi_application()
