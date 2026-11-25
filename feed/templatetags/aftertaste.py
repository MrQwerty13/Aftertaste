from __future__ import annotations

from django import template
from django.utils import timezone

from feed.i18n import translate

register = template.Library()


@register.filter(name="tr")
def tr(key=None, lang: str = "en") -> str:
    return translate(lang, str(key or ""))


@register.filter
def when(value, lang: str = "en") -> str:
    if not value:
        return ""
    try:
        local = timezone.localtime(value)
    except (ValueError, AttributeError):
        local = value
    if lang == "ru":
        return local.strftime("%d.%m.%Y · %H:%M")
    return local.strftime("%b %d, %Y · %H:%M")


@register.filter
def initial(value) -> str:
    text = str(value or "").strip()
    return text[:1].upper()


@register.filter
def has_liked(take, user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    return bool(getattr(take, "liked_by_me", False))


@register.filter
def has_reposted(take, user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    return bool(getattr(take, "reposted_by_me", False))


@register.filter
def byline(name, lang: str = "en") -> str:
    return translate(lang, "feed.by", name=name)


@register.filter
def comments_label(count, lang: str = "en") -> str:
    return translate(lang, "feed.comments", count=count)


@register.filter
def reposted_by(name, lang: str = "en") -> str:
    return translate(lang, "feed.reposted_by", name=name)


@register.filter
def joined_when(value, lang: str = "en") -> str:
    if not value:
        return ""
    try:
        local = timezone.localtime(value)
    except (ValueError, AttributeError):
        local = value
    formatted = local.strftime("%d.%m.%Y") if lang == "ru" else local.strftime("%b %Y")
    return translate(lang, "profile.joined", when=formatted)
