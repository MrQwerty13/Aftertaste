from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.db.models import Count

from .models import Follow, Like, Notification, Repost, Take


@dataclass
class FeedEntry:
    take: Take
    actor: object
    kind: str
    timestamp: datetime

    @property
    def is_repost(self) -> bool:
        return self.kind == "repost"


def attach_counts(takes) -> None:
    takes = list(takes)
    ids = [take.pk for take in takes]
    if not ids:
        return

    counts = {pk: {"like": 0, "comment": 0, "repost": 0} for pk in ids}

    for row in (
        Like.objects.filter(take_id__in=ids)
        .values("take_id")
        .annotate(total=Count("id"))
    ):
        counts[row["take_id"]]["like"] = row["total"]

    for row in (
        Repost.objects.filter(take_id__in=ids)
        .values("take_id")
        .annotate(total=Count("id"))
    ):
        counts[row["take_id"]]["repost"] = row["total"]

    from .models import Comment

    for row in (
        Comment.objects.filter(take_id__in=ids)
        .values("take_id")
        .annotate(total=Count("id"))
    ):
        counts[row["take_id"]]["comment"] = row["total"]

    for take in takes:
        bucket = counts.get(take.pk, {"like": 0, "comment": 0, "repost": 0})
        take.like_count = bucket["like"]
        take.comment_count = bucket["comment"]
        take.repost_count = bucket["repost"]


def decorate_for_user(takes, user) -> None:
    takes = list(takes)
    ids = [take.pk for take in takes]
    liked: set[int] = set()
    reposted: set[int] = set()
    if user is not None and user.is_authenticated and ids:
        liked = set(
            Like.objects.filter(user=user, take_id__in=ids).values_list(
                "take_id", flat=True
            )
        )
        reposted = set(
            Repost.objects.filter(user=user, take_id__in=ids).values_list(
                "take_id", flat=True
            )
        )
    for take in takes:
        take.liked_by_me = take.pk in liked
        take.reposted_by_me = take.pk in reposted


def _finish(entries: list[FeedEntry], user) -> list[FeedEntry]:
    canonical: dict[int, Take] = {}
    for entry in entries:
        canonical.setdefault(entry.take.pk, entry.take)
    for entry in entries:
        entry.take = canonical[entry.take.pk]
    all_takes = list(canonical.values())
    attach_counts(all_takes)
    decorate_for_user(all_takes, user)
    return entries


def get_feed(tab: str, user) -> list[FeedEntry]:
    if tab == "popular":
        takes = list(
            Take.objects.select_related("author__profile").order_by("-created_at")[:200]
        )
        attach_counts(takes)
        decorate_for_user(takes, user)
        takes.sort(
            key=lambda take: (
                take.like_count * 2 + take.comment_count * 2 + take.repost_count * 3,
                take.created_at,
            ),
            reverse=True,
        )
        takes = takes[:50]
        return [FeedEntry(take, take.author, "post", take.created_at) for take in takes]

    takes_qs = Take.objects.select_related("author__profile")
    reposts_qs = Repost.objects.select_related(
        "take__author__profile", "user__profile"
    )

    if tab == "following":
        if not user.is_authenticated:
            return []
        followed_ids = set(
            Follow.objects.filter(follower=user).values_list("following_id", flat=True)
        )
        followed_ids.add(user.pk)
        takes_qs = takes_qs.filter(author_id__in=followed_ids)
        reposts_qs = reposts_qs.filter(user_id__in=followed_ids)

    takes = list(takes_qs.order_by("-created_at")[:60])
    reposts = list(reposts_qs.order_by("-created_at")[:60])

    entries = [FeedEntry(take, take.author, "post", take.created_at) for take in takes]
    entries += [FeedEntry(repost.take, repost.user, "repost", repost.created_at) for repost in reposts]
    entries.sort(key=lambda entry: entry.timestamp, reverse=True)
    return _finish(entries[:60], user)


def get_profile_entries(profile_user, viewer, tab: str = "takes") -> list[FeedEntry]:
    if tab == "reposts":
        reposts = list(
            Repost.objects.filter(user=profile_user)
            .select_related("take__author__profile", "user__profile")
            .order_by("-created_at")
        )
        entries = [
            FeedEntry(repost.take, repost.user, "repost", repost.created_at)
            for repost in reposts
        ]
    else:
        takes = list(
            Take.objects.filter(author=profile_user)
            .select_related("author__profile")
            .order_by("-created_at")
        )
        entries = [FeedEntry(take, take.author, "post", take.created_at) for take in takes]

    return _finish(entries, viewer)


def toggle_like(user, take: Take) -> tuple[bool, int]:
    like, created = Like.objects.get_or_create(user=user, take=take)
    if created:
        Notification.push(
            recipient=take.author,
            actor=user,
            kind=Notification.Kind.LIKE,
            take=take,
        )
    else:
        like.delete()
    return created, take.likes.count()


def toggle_repost(user, take: Take) -> tuple[bool, int]:
    repost, created = Repost.objects.get_or_create(user=user, take=take)
    if created:
        Notification.push(
            recipient=take.author,
            actor=user,
            kind=Notification.Kind.REPOST,
            take=take,
        )
    else:
        repost.delete()
    return created, take.reposts.count()


def toggle_follow(user, target) -> bool | None:
    if user == target:
        return None
    follow, created = Follow.objects.get_or_create(follower=user, following=target)
    if created:
        Notification.push(
            recipient=target,
            actor=user,
            kind=Notification.Kind.FOLLOW,
        )
        return True
    follow.delete()
    return False


def is_following(user, target) -> bool:
    if not getattr(user, "is_authenticated", False) or user == target:
        return False
    return Follow.objects.filter(follower=user, following=target).exists()
