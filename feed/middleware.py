from __future__ import annotations

from django.utils import translation

from .i18n import LANG_COOKIE, normalize_lang


class PreferredLanguageMiddleware:
    """Activate Django's locale from the app's language cookie.

    The visible UI uses the app's own translation layer, but Django's built-in
    auth and admin messages follow the active locale. This keeps password
    validation and other framework messages in the selected language.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = normalize_lang(request.COOKIES.get(LANG_COOKIE))
        translation.activate(language)
        request.LANGUAGE_CODE = language
        try:
            return self.get_response(request)
        finally:
            translation.deactivate()
