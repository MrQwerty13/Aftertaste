from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CommentForm, LoginForm, ProfileForm, RegisterForm, TakeForm
from .i18n import (
    ACCENT_COOKIE,
    COOKIE_MAX_AGE,
    LANG_COOKIE,
    THEME_COOKIE,
    normalize_accent,
    normalize_lang,
    normalize_theme,
    request_lang,
    translate,
)
from .models import Comment, Notification, Profile, Take
from .services import (
    attach_counts,
    decorate_for_user,
    get_feed,
    get_profile_entries,
    is_following,
    toggle_follow,
    toggle_like,
    toggle_repost,
)

User = get_user_model()


def _wants_json(request: HttpRequest) -> bool:
    accept = request.headers.get("Accept", "")
    return (
        "application/json" in accept
        or request.headers.get("X-Requested-With") == "fetch"
    )


def _safe_next(request: HttpRequest, default: str = "/") -> str:
    target = (request.POST.get("next") or request.GET.get("next") or "").strip()
    parsed = urlsplit(target)
    if (
        not target
        or not target.startswith("/")
        or target.startswith("//")
        or "\\" in target
        or parsed.scheme
        or parsed.netloc
    ):
        return default
    return target


def home(request: HttpRequest) -> HttpResponse:
    tab = request.GET.get("tab", "all")
    if tab not in {"all", "following", "popular"}:
        tab = "all"
    entries = get_feed(tab, request.user)
    return render(request, "feed.html", {"entries": entries, "tab": tab})


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "about.html")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("feed:home")
    lang = request_lang(request)
    if request.method == "POST":
        form = RegisterForm(request.POST, lang=lang)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, translate(lang, "flash.welcome"))
            return redirect("feed:home")
    else:
        form = RegisterForm(lang=lang)
    return render(request, "auth/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("feed:home")
    lang = request_lang(request)
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"].strip()
            password = form.cleaned_data["password"]
            user = (
                User.objects.filter(
                    Q(username__iexact=identifier) | Q(email__iexact=identifier)
                )
                .order_by("id")
                .first()
            )
            if user and user.is_active and user.check_password(password):
                login(request, user)
                messages.success(
                    request,
                    translate(lang, "flash.hello", username=user.username),
                )
                return redirect(_safe_next(request, "/"))
            form.add_error(None, translate(lang, "auth.invalid_credentials"))
    else:
        form = LoginForm()
    return render(request, "auth/login.html", {"form": form})


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    lang = request_lang(request)
    logout(request)
    messages.success(request, translate(lang, "flash.signed_out"))
    return redirect("feed:home")


# ---------------------------------------------------------------------------
# Takes
# ---------------------------------------------------------------------------


@login_required
def take_create(request: HttpRequest) -> HttpResponse:
    lang = request_lang(request)
    if request.method == "POST":
        form = TakeForm(request.POST, lang=lang)
        if form.is_valid():
            take = form.to_take(request.user)
            take.save()
            messages.success(request, translate(lang, "flash.post_live"))
            return redirect(take)
    else:
        form = TakeForm(lang=lang)
    return render(request, "take_form.html", {"form": form, "mode": "create"})


def take_detail(request: HttpRequest, pk: int) -> HttpResponse:
    take = get_object_or_404(
        Take.objects.select_related("author__profile"), pk=pk
    )
    attach_counts([take])
    decorate_for_user([take], request.user)
    comments = list(take.comments.select_related("author__profile").all())
    lang = request_lang(request)
    return render(
        request,
        "take_detail.html",
        {
            "take": take,
            "comments": comments,
            "comment_form": CommentForm(lang=lang),
        },
    )


@login_required
def take_edit(request: HttpRequest, pk: int) -> HttpResponse:
    take = get_object_or_404(Take, pk=pk)
    lang = request_lang(request)
    if take.author_id != request.user.id:
        messages.error(request, translate(lang, "post_forbidden"))
        return redirect(take)

    if request.method == "POST":
        form = TakeForm(request.POST, lang=lang)
        if form.is_valid():
            take.drink_name = form.cleaned_data["drink_name"]
            take.content = form.cleaned_data["content"]
            take.updated_at = timezone.now()
            take.save(update_fields=["drink_name", "content", "updated_at"])
            messages.success(request, translate(lang, "flash.post_updated"))
            return redirect(take)
    else:
        form = TakeForm(
            initial={"drink_name": take.drink_name, "content": take.content},
            lang=lang,
        )
    return render(
        request,
        "take_form.html",
        {"form": form, "mode": "edit", "take": take},
    )


@login_required
@require_POST
def take_delete(request: HttpRequest, pk: int) -> HttpResponse:
    lang = request_lang(request)
    take = get_object_or_404(Take, pk=pk)
    if take.author_id != request.user.id:
        messages.error(request, translate(lang, "post_forbidden"))
        return redirect(take)
    take.delete()
    messages.success(request, translate(lang, "flash.post_deleted"))
    return redirect("feed:home")


@require_POST
def like_toggle(request: HttpRequest, pk: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": translate(request_lang(request), "like.login")}, status=401
        )
    take = get_object_or_404(Take, pk=pk)
    liked, count = toggle_like(request.user, take)
    return JsonResponse({"liked": liked, "like_count": count})


@require_POST
def repost_toggle(request: HttpRequest, pk: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": translate(request_lang(request), "repost.login")}, status=401
        )
    take = get_object_or_404(Take, pk=pk)
    reposted, count = toggle_repost(request.user, take)
    return JsonResponse({"reposted": reposted, "repost_count": count})


@login_required
@require_POST
def comment_create(request: HttpRequest, pk: int) -> HttpResponse:
    lang = request_lang(request)
    take = get_object_or_404(Take, pk=pk)
    form = CommentForm(request.POST, lang=lang)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.take = take
        comment.author = request.user
        comment.save()
        Notification.push(
            recipient=take.author,
            actor=request.user,
            kind=Notification.Kind.COMMENT,
            take=take,
            comment=comment,
        )
        messages.success(request, translate(lang, "flash.comment_added"))
    else:
        first_error = next(iter(form.errors.values()), None)
        message = first_error[0] if first_error else translate(lang, "comment_empty")
        messages.error(request, message)
    return redirect(take)


@login_required
@require_POST
def comment_delete(request: HttpRequest, pk: int, comment_id: int) -> HttpResponse:
    lang = request_lang(request)
    take = get_object_or_404(Take, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_id, take=take)
    if comment.author_id != request.user.id:
        messages.error(request, translate(lang, "comment_forbidden"))
    else:
        comment.delete()
        messages.success(request, translate(lang, "flash.comment_deleted"))
    return redirect(take)


# ---------------------------------------------------------------------------
# Profiles / social
# ---------------------------------------------------------------------------


def profile(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = get_object_or_404(
        User.objects.select_related("profile"), username=username
    )
    tab = request.GET.get("tab", "takes")
    if tab not in {"takes", "reposts"}:
        tab = "takes"

    entries = get_profile_entries(profile_user, request.user, tab)

    from .models import Follow

    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    takes_count = profile_user.takes.count()
    is_self = request.user == profile_user

    return render(
        request,
        "profile.html",
        {
            "profile_user": profile_user,
            "entries": entries,
            "tab": tab,
            "followers_count": followers_count,
            "following_count": following_count,
            "takes_count": takes_count,
            "is_self": is_self,
            "following": is_following(request.user, profile_user),
        },
    )


@login_required
@require_POST
def follow_toggle(request: HttpRequest, username: str) -> HttpResponse:
    lang = request_lang(request)
    target = get_object_or_404(User, username=username)
    result = toggle_follow(request.user, target)
    if result is None:
        messages.error(request, translate(lang, "follow.login"))
    elif result:
        messages.success(
            request, translate(lang, "flash.followed", name=target.username)
        )
    else:
        messages.success(
            request, translate(lang, "flash.unfollowed", name=target.username)
        )
    return redirect("feed:profile", username=target.username)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


@login_required
def notifications(request: HttpRequest) -> HttpResponse:
    queryset = Notification.objects.filter(recipient=request.user).select_related(
        "actor__profile", "take"
    )
    items = list(queryset[:100])
    queryset.filter(is_read=False).update(is_read=True)
    return render(request, "notifications.html", {"items": items})


@login_required
@require_POST
def mark_notifications_read(request: HttpRequest) -> HttpResponse:
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )
    messages.success(
        request, translate(request_lang(request), "notifications.marked_read")
    )
    return redirect("feed:notifications")


# ---------------------------------------------------------------------------
# Settings / preferences
# ---------------------------------------------------------------------------


def settings_view(request: HttpRequest) -> HttpResponse:
    profile_form = None
    profile_obj = None
    if request.user.is_authenticated:
        profile_obj, _ = Profile.objects.get_or_create(user=request.user)
        profile_form = ProfileForm(instance=profile_obj)
    return render(
        request,
        "settings.html",
        {"profile_form": profile_form, "profile_obj": profile_obj},
    )


@login_required
@require_POST
def update_profile(request: HttpRequest) -> HttpResponse:
    lang = request_lang(request)
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST, instance=profile_obj)
    if form.is_valid():
        form.save()
        messages.success(request, translate(lang, "settings.profile_saved"))
    else:
        first_error = next(iter(form.errors.values()), None)
        messages.error(
            request,
            first_error[0] if first_error else translate(lang, "quick.error"),
        )
    return redirect("feed:settings")


@login_required
@require_POST
def delete_account(request: HttpRequest) -> HttpResponse:
    lang = request_lang(request)
    password = request.POST.get("password", "")
    if not request.user.check_password(password):
        messages.error(request, translate(lang, "settings.delete_bad_password"))
        return redirect("feed:settings")
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, translate(lang, "flash.account_deleted"))
    return redirect("feed:home")


def _prefs_response(request: HttpRequest):
    return redirect(_safe_next(request, "/"))


@require_POST
def set_theme(request: HttpRequest) -> HttpResponse:
    response = _prefs_response(request)
    response.set_cookie(
        THEME_COOKIE,
        normalize_theme(request.POST.get("theme")),
        max_age=COOKIE_MAX_AGE,
        samesite="Lax",
    )
    return response


@require_POST
def set_lang(request: HttpRequest) -> HttpResponse:
    response = _prefs_response(request)
    response.set_cookie(
        LANG_COOKIE,
        normalize_lang(request.POST.get("lang")),
        max_age=COOKIE_MAX_AGE,
        samesite="Lax",
    )
    return response


@require_POST
def set_accent(request: HttpRequest) -> HttpResponse:
    response = _prefs_response(request)
    response.set_cookie(
        ACCENT_COOKIE,
        str(normalize_accent(request.POST.get("accent"))),
        max_age=COOKIE_MAX_AGE,
        samesite="Lax",
    )
    return response


# ---------------------------------------------------------------------------
# PWA quick add
# ---------------------------------------------------------------------------


def quick_add(request: HttpRequest) -> HttpResponse:
    lang = request_lang(request)
    wants_json = _wants_json(request)

    if request.method == "POST":
        if not request.user.is_authenticated:
            if wants_json:
                return JsonResponse(
                    {"error": translate(lang, "quick.login")}, status=401
                )
            messages.error(request, translate(lang, "quick.login"))
            return redirect("feed:login")

        form = TakeForm(request.POST, lang=lang)
        if form.is_valid():
            take = form.to_take(request.user)
            take.save()
            if wants_json:
                return JsonResponse(
                    {
                        "ok": True,
                        "take_id": take.pk,
                        "url": take.get_absolute_url(),
                        "message": translate(lang, "quick.success"),
                    }
                )
            messages.success(request, translate(lang, "quick.success"))
            return redirect("feed:quick_add")
        if wants_json:
            return JsonResponse(
                {"ok": False, "errors": form.errors.get_json_data()}, status=400
            )
        messages.error(request, translate(lang, "quick.error"))
    else:
        form = TakeForm(lang=lang)

    return render(request, "quick_add.html", {"form": form})


def service_worker(request: HttpRequest) -> HttpResponse:
    path = settings.BASE_DIR / "static" / "sw.js"
    response = HttpResponse(
        path.read_text(encoding="utf-8"),
        content_type="application/javascript",
    )
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response


def manifest(request: HttpRequest) -> HttpResponse:
    path = settings.BASE_DIR / "static" / "manifest.webmanifest"
    return HttpResponse(
        path.read_text(encoding="utf-8"),
        content_type="application/manifest+json",
    )


# ---------------------------------------------------------------------------
# Moderation
# ---------------------------------------------------------------------------


def _is_moderator(request: HttpRequest) -> bool:
    return bool(request.session.get("is_moderator"))


def mod_home(request: HttpRequest) -> HttpResponse:
    lang = request_lang(request)
    if request.method == "POST":
        key = (request.POST.get("key") or "").strip()
        if key and key == settings.MODERATION_KEY:
            request.session["is_moderator"] = True
            messages.success(request, translate(lang, "mod.unlocked"))
            return redirect("feed:mod_home")
        messages.error(request, translate(lang, "mod.bad_key"))

    if not _is_moderator(request):
        return render(request, "mod/unlock.html")

    takes = list(
        Take.objects.select_related("author__profile").order_by("-created_at")[:200]
    )
    attach_counts(takes)
    decorate_for_user(takes, None)
    return render(request, "mod/panel.html", {"takes": takes})


@require_POST
def mod_delete(request: HttpRequest, pk: int) -> HttpResponse:
    if not _is_moderator(request):
        return redirect("feed:mod_home")
    lang = request_lang(request)
    take = get_object_or_404(Take, pk=pk)
    take.delete()
    messages.success(request, translate(lang, "mod.deleted"))
    return redirect("feed:mod_home")


@require_POST
def mod_lock(request: HttpRequest) -> HttpResponse:
    request.session.pop("is_moderator", None)
    messages.success(request, translate(request_lang(request), "mod.locked"))
    return redirect("feed:mod_home")
