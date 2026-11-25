"""Root URL configuration for Aftertaste."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("feed.urls")),
]
