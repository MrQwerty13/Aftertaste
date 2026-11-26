"""Django settings for the Aftertaste project."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_runserver() -> bool:
    """True when invoked via ``manage.py runserver`` (local development)."""
    return len(sys.argv) > 1 and Path(sys.argv[1]).name == "runserver"


# ``manage.py runserver`` is a local development command; treat it as an
# explicit opt-in to debug mode even if DJANGO_DEBUG was not set. Any other
# deployment path (gunicorn/uwsgi/asgi) defaults to DEBUG=False.
IS_DEV_SERVER = _is_runserver()

DEV_SECRET_KEY = "django-insecure-aftertaste-dev-secret-change-me"

SECRET_KEY = os.environ.get("SECRET_KEY", DEV_SECRET_KEY if IS_DEV_SERVER else "")
if not SECRET_KEY:
    raise RuntimeError(
        "The SECRET_KEY environment variable must be set when running outside "
        "of the local development server. Generate one with e.g.:\n"
        '  python -c \'from django.core.management.utils import '
        'get_random_secret_key; print(get_random_secret_key())\''
    )

DEBUG = env_bool("DJANGO_DEBUG", IS_DEV_SERVER)

_default_hosts = "*" if IS_DEV_SERVER else ""
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", _default_hosts).split(",")
    if host.strip()
]
if not DEBUG and not ALLOWED_HOSTS:
    raise RuntimeError(
        "DJANGO_ALLOWED_HOSTS must be configured (comma-separated) when "
        "DEBUG is disabled."
    )

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "feed",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "feed.middleware.PreferredLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "aftertaste.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "feed.context_processors.preferences",
            ],
        },
    },
]

WSGI_APPLICATION = "aftertaste.wsgi.application"
ASGI_APPLICATION = "aftertaste.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "feed:login"
LOGIN_REDIRECT_URL = "feed:home"

MODERATION_KEY = os.environ.get("MODERATION_KEY", "")
if not MODERATION_KEY:
    # Fail closed: without an explicitly configured key the moderation
    # panel cannot be unlocked at all (see feed.views.mod_home).
    MODERATION_KEY = ""

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# In production, mark session/CSRF cookies as secure and scope them to HTTPS.
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)

# Security headers.
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool(
    "DJANGO_SESSION_EXPIRE_AT_BROWSER_CLOSE", not DEBUG
)
# Only enable HSTS when it is safe to do so (DEBUG off and not overridden).
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = False
