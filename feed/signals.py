from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=get_user_model(), dispatch_uid="feed.create_profile")
def ensure_profile(sender, instance, created, **kwargs) -> None:
    if created:
        Profile.objects.get_or_create(user=instance)
