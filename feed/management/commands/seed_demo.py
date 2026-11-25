from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from feed.models import Comment, Follow, Like, Notification, Profile, Repost, Take

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo users, takes, follows, reposts, and notifications."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing takes/social data and the demo users first.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Take.objects.all().delete()
            Follow.objects.all().delete()
            Like.objects.all().delete()
            Repost.objects.all().delete()
            Notification.objects.all().delete()
            User.objects.filter(username__in=["anna", "leo"]).delete()

        anna, _ = User.objects.get_or_create(
            username="anna", defaults={"email": "anna@example.com"}
        )
        anna.email = "anna@example.com"
        anna.set_password("password")
        anna.save()

        leo, _ = User.objects.get_or_create(
            username="leo", defaults={"email": "leo@example.com"}
        )
        leo.email = "leo@example.com"
        leo.set_password("password")
        leo.save()

        Profile.objects.update_or_create(
            user=anna,
            defaults={
                "display_name": "Anna",
                "bio": "Oat milk apologist. Chasing the perfect flat white.",
            },
        )
        Profile.objects.update_or_create(
            user=leo,
            defaults={
                "display_name": "Leo",
                "bio": "Bitter is better. Negroni before noon is a lifestyle.",
            },
        )

        if not Take.objects.filter(author=anna).exists():
            take_white = Take.objects.create(
                author=anna,
                drink_name="Oat flat white",
                content=(
                    "Silky, a little sweet from the oat milk, espresso still "
                    "clear underneath. Morning keeper."
                ),
            )
            take_hojicha = Take.objects.create(
                author=anna,
                drink_name="Hojicha latte",
                content=(
                    "Toasty, almost cocoa-like, very soft caffeine. Perfect "
                    "rainy afternoon drink."
                ),
            )
        else:
            take_white = Take.objects.filter(author=anna).order_by("created_at").first()
            take_hojicha = (
                Take.objects.filter(author=anna).order_by("-created_at").first()
            )

        if not Take.objects.filter(author=leo).exists():
            take_negroni = Take.objects.create(
                author=leo,
                drink_name="Negroni",
                content=(
                    "Bitter orange forward, gin shows late. Best with one big "
                    "ice cube and nowhere to be."
                ),
            )
        else:
            take_negroni = Take.objects.filter(author=leo).order_by("created_at").first()

        Follow.objects.get_or_create(follower=anna, following=leo)
        Follow.objects.get_or_create(follower=leo, following=anna)

        def ensure_like(user, take):
            like, created = Like.objects.get_or_create(user=user, take=take)
            if created:
                Notification.push(
                    recipient=take.author,
                    actor=user,
                    kind=Notification.Kind.LIKE,
                    take=take,
                )
            return like

        def ensure_repost(user, take):
            repost, created = Repost.objects.get_or_create(user=user, take=take)
            if created:
                Notification.push(
                    recipient=take.author,
                    actor=user,
                    kind=Notification.Kind.REPOST,
                    take=take,
                )
            return repost

        if take_white:
            ensure_like(leo, take_white)
            ensure_repost(leo, take_white)
        if take_negroni:
            ensure_like(anna, take_negroni)

        if not Comment.objects.filter(take=take_white, author=leo).exists():
            comment = Comment.objects.create(
                take=take_white,
                author=leo,
                content="That oat milk texture is exactly what I chase on weekday mornings.",
            )
            Notification.push(
                recipient=anna,
                actor=leo,
                kind=Notification.Kind.COMMENT,
                take=take_white,
                comment=comment,
            )

        if take_hojicha and not Comment.objects.filter(
            take=take_hojicha, author=leo
        ).exists():
            comment = Comment.objects.create(
                take=take_hojicha,
                author=leo,
                content="Hojicha is underrated. Try it iced next.",
            )
            Notification.push(
                recipient=anna,
                actor=leo,
                kind=Notification.Kind.COMMENT,
                take=take_hojicha,
                comment=comment,
            )

        if options.get("verbosity", 1):
            self.stdout.write(
                self.style.SUCCESS(
                    "Seeded demo users anna@example.com / leo@example.com "
                    "(password: password)."
                )
            )
