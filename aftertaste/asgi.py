"""ASGI config for the Aftertaste project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aftertaste.settings")

application = get_asgi_application()
