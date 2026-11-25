from django.urls import path

from . import views

app_name = "feed"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("quick/", views.quick_add, name="quick_add"),
    path("sw.js", views.service_worker, name="service_worker"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    # Auth
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Settings / preferences
    path("settings/", views.settings_view, name="settings"),
    path("settings/profile/", views.update_profile, name="update_profile"),
    path("settings/delete/", views.delete_account, name="delete_account"),
    path("prefs/theme/", views.set_theme, name="set_theme"),
    path("prefs/lang/", views.set_lang, name="set_lang"),
    path("prefs/accent/", views.set_accent, name="set_accent"),
    # Notifications
    path("notifications/", views.notifications, name="notifications"),
    path(
        "notifications/read/",
        views.mark_notifications_read,
        name="mark_notifications_read",
    ),
    # Takes
    path("takes/new/", views.take_create, name="take_create"),
    path("takes/<int:pk>/", views.take_detail, name="take_detail"),
    path("takes/<int:pk>/edit/", views.take_edit, name="take_edit"),
    path("takes/<int:pk>/delete/", views.take_delete, name="take_delete"),
    path("takes/<int:pk>/like/", views.like_toggle, name="like_toggle"),
    path("takes/<int:pk>/repost/", views.repost_toggle, name="repost_toggle"),
    path("takes/<int:pk>/comments/", views.comment_create, name="comment_create"),
    path(
        "takes/<int:pk>/comments/<int:comment_id>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
    # Profiles / social
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    # Moderation (secret, not linked from the UI)
    path("del/", views.mod_home, name="mod_home"),
    path("del/<int:pk>/delete/", views.mod_delete, name="mod_delete"),
    path("del/lock/", views.mod_lock, name="mod_lock"),
]
