from __future__ import annotations

from .i18n import (
    ACCENT_COOKIE,
    LANG_COOKIE,
    THEME_COOKIE,
    normalize_accent,
    normalize_lang,
    normalize_theme,
)
from .models import Notification


def preferences(request):
    lang = normalize_lang(request.COOKIES.get(LANG_COOKIE))
    theme = normalize_theme(request.COOKIES.get(THEME_COOKIE))
    accent = normalize_accent(request.COOKIES.get(ACCENT_COOKIE))

    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()

    return {
        "lang": lang,
        "theme": theme,
        "accent": accent,
        "unread_notifications": unread_notifications,
    }
