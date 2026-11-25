from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

MAX_TAKE_LENGTH = 280
MAX_COMMENT_LENGTH = 280
MAX_DRINK_NAME_LENGTH = 80


class Profile(models.Model):
    """Extra public-facing fields for a Django user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=60, blank=True)
    bio = models.CharField(max_length=280, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return self.display_name or self.user.username

    @property
    def name(self) -> str:
        return self.display_name or self.user.username

    @property
    def initial(self) -> str:
        return self.name[:1].upper()

    def get_absolute_url(self) -> str:
        return reverse("feed:profile", args=[self.user.username])


class TakeQuerySet(models.QuerySet):
    def with_counts(self) -> "TakeQuerySet":
        from django.db.models import Count

        return self.annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
            repost_count=Count("reposts", distinct=True),
        )


class Take(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="takes",
    )
    drink_name = models.CharField(max_length=MAX_DRINK_NAME_LENGTH)
    content = models.TextField(max_length=MAX_TAKE_LENGTH)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    objects = TakeQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self) -> str:
        return f"{self.drink_name} by {self.author.username}"

    def get_absolute_url(self) -> str:
        return reverse("feed:take_detail", args=[self.pk])

    @property
    def is_edited(self) -> bool:
        return self.updated_at is not None


class Like(models.Model):
    take = models.ForeignKey(Take, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["take", "user"], name="unique_like"),
        ]
        indexes = [models.Index(fields=["take", "user"])]

    def __str__(self) -> str:
        return f"{self.user} likes {self.take_id}"


class Comment(models.Model):
    take = models.ForeignKey(Take, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(max_length=MAX_COMMENT_LENGTH)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["take", "created_at"])]

    def __str__(self) -> str:
        return f"Comment by {self.author.username}"


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_links",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower_links",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            ),
            models.CheckConstraint(
                condition=~Q(follower=F("following")),
                name="no_self_follow",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.follower} follows {self.following}"


class Repost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reposts",
    )
    take = models.ForeignKey(Take, on_delete=models.CASCADE, related_name="reposts")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "take"], name="unique_repost"),
        ]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.user} reposted {self.take_id}"


class Notification(models.Model):
    class Kind(models.TextChoices):
        LIKE = "like", "Like"
        COMMENT = "comment", "Comment"
        FOLLOW = "follow", "Follow"
        REPOST = "repost", "Repost"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    take = models.ForeignKey(
        Take,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.actor} -> {self.recipient}: {self.kind}"

    @property
    def target_url(self) -> str:
        if self.take_id:
            return reverse("feed:take_detail", args=[self.take_id])
        if self.kind == self.Kind.FOLLOW:
            return reverse("feed:profile", args=[self.actor.username])
        return reverse("feed:notifications")

    @classmethod
    def push(
        cls,
        *,
        recipient,
        actor,
        kind: str,
        take=None,
        comment=None,
    ) -> "Notification | None":
        """Create a notification unless the actor is the recipient."""
        if recipient == actor:
            return None
        return cls.objects.create(
            recipient=recipient,
            actor=actor,
            kind=kind,
            take=take,
            comment=comment,
        )
