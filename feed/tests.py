from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Comment, Follow, Like, Notification, Repost, Take
from .services import get_feed, toggle_follow

User = get_user_model()


class FeedTestCase(TestCase):
    def setUp(self):
        self.anna = User.objects.create_user(
            "anna", "anna@example.com", "secret123"
        )
        self.leo = User.objects.create_user("leo", "leo@example.com", "secret123")
        self.sam = User.objects.create_user("sam", "sam@example.com", "secret123")
        self.take = Take.objects.create(
            author=self.anna,
            drink_name="Oat flat white",
            content="Silky and sweet, a solid morning keeper.",
        )

    def test_home_renders(self):
        response = self.client.get(reverse("feed:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oat flat white")

    def test_create_take_requires_login(self):
        response = self.client.get(reverse("feed:take_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("feed:login"), response.url)

    def test_create_take(self):
        self.client.force_login(self.anna)
        response = self.client.post(
            reverse("feed:take_create"),
            {"drink_name": "Matcha latte", "content": "Grassy and warm, very smooth."},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Take.objects.filter(drink_name="Matcha latte").exists())

    def test_create_take_rejects_short_content(self):
        self.client.force_login(self.anna)
        response = self.client.post(
            reverse("feed:take_create"),
            {"drink_name": "Espresso", "content": "short"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Take.objects.filter(drink_name="Espresso").exists())

    def test_like_toggle_creates_notification(self):
        self.client.force_login(self.leo)
        url = reverse("feed:like_toggle", args=[self.take.pk])

        response = self.client.post(url, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["liked"])
        self.assertEqual(payload["like_count"], 1)
        self.assertTrue(Like.objects.filter(user=self.leo, take=self.take).exists())
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.anna,
                actor=self.leo,
                kind=Notification.Kind.LIKE,
            ).exists()
        )

        response = self.client.post(url, HTTP_ACCEPT="application/json")
        self.assertFalse(response.json()["liked"])
        self.assertFalse(Like.objects.filter(user=self.leo, take=self.take).exists())

    def test_anonymous_like_returns_401(self):
        response = self.client.post(
            reverse("feed:like_toggle", args=[self.take.pk]),
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_repost_toggle(self):
        self.client.force_login(self.leo)
        url = reverse("feed:repost_toggle", args=[self.take.pk])
        response = self.client.post(url, HTTP_ACCEPT="application/json")
        self.assertTrue(response.json()["reposted"])
        self.assertEqual(response.json()["repost_count"], 1)
        self.assertTrue(Repost.objects.filter(user=self.leo, take=self.take).exists())

    def test_follow_toggle_and_notification(self):
        self.client.force_login(self.leo)
        url = reverse("feed:follow_toggle", args=[self.anna.username])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Follow.objects.filter(follower=self.leo, following=self.anna).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.anna,
                actor=self.leo,
                kind=Notification.Kind.FOLLOW,
            ).exists()
        )

        self.client.post(url)
        self.assertFalse(
            Follow.objects.filter(follower=self.leo, following=self.anna).exists()
        )

    def test_following_feed_filters_takes(self):
        Take.objects.create(
            author=self.leo,
            drink_name="Negroni",
            content="Bitter orange forward, gin shows late.",
        )
        Take.objects.create(
            author=self.sam,
            drink_name="Cola",
            content="Sugary and cold, not much else going on.",
        )
        toggle_follow(self.anna, self.leo)

        self.client.force_login(self.anna)
        response = self.client.get(reverse("feed:home") + "?tab=following")
        self.assertContains(response, "Negroni")
        self.assertNotContains(response, "Cola")

    def test_feed_counts_apply_to_reposted_and_original_entries(self):
        leo_take = Take.objects.create(
            author=self.leo,
            drink_name="Boulevardier",
            content="Bitter, boozy, and warmer than a negroni.",
        )
        Like.objects.create(user=self.sam, take=leo_take)
        Repost.objects.create(user=self.leo, take=leo_take)

        entries = get_feed("all", self.anna)
        matching = [e for e in entries if e.take.pk == leo_take.pk]
        self.assertEqual(len(matching), 2)
        for entry in matching:
            self.assertEqual(entry.take.like_count, 1)
            self.assertEqual(entry.take.repost_count, 1)

    def test_popular_tab_renders(self):
        Like.objects.create(user=self.leo, take=self.take)
        response = self.client.get(reverse("feed:home") + "?tab=popular")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oat flat white")

    def test_comment_create_and_delete(self):
        self.client.force_login(self.leo)
        response = self.client.post(
            reverse("feed:comment_create", args=[self.take.pk]),
            {"content": "Great choice for the morning."},
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(take=self.take, author=self.leo)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.anna,
                kind=Notification.Kind.COMMENT,
            ).exists()
        )

        self.client.post(
            reverse("feed:comment_delete", args=[self.take.pk, comment.pk])
        )
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_profile_page(self):
        response = self.client.get(
            reverse("feed:profile", args=[self.anna.username])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "@anna")

    def test_quick_add_page_and_json(self):
        self.client.force_login(self.anna)
        page = self.client.get(reverse("feed:quick_add"))
        self.assertEqual(page.status_code, 200)

        response = self.client.post(
            reverse("feed:quick_add"),
            {"drink_name": "Iced americano", "content": "Bitter, cold, exactly right."},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload["ok"])
        self.assertTrue(Take.objects.filter(drink_name="Iced americano").exists())

    def test_quick_add_requires_login_json(self):
        response = self.client.post(
            reverse("feed:quick_add"),
            {"drink_name": "Tea", "content": "Warm and calming, nice."},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_pwa_endpoints(self):
        sw = self.client.get("/sw.js")
        self.assertEqual(sw.status_code, 200)
        self.assertTrue(sw["Content-Type"].startswith("application/javascript"))
        self.assertEqual(sw["Service-Worker-Allowed"], "/")

        manifest = self.client.get("/manifest.webmanifest")
        self.assertEqual(manifest.status_code, 200)
        self.assertTrue(
            manifest["Content-Type"].startswith("application/manifest+json")
        )

    @override_settings(MODERATION_KEY="test-key")
    def test_moderation_unlock_and_delete(self):
        response = self.client.post(reverse("feed:mod_home"), {"key": "test-key"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get("is_moderator"))

        self.client.post(reverse("feed:mod_delete", args=[self.take.pk]))
        self.assertFalse(Take.objects.filter(pk=self.take.pk).exists())

    @override_settings(MODERATION_KEY="test-key")
    def test_moderation_rejects_bad_key(self):
        response = self.client.post(reverse("feed:mod_home"), {"key": "nope"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("is_moderator"))

    @override_settings(MODERATION_KEY="")
    def test_moderation_disabled_without_key(self):
        # Fail closed: with no configured key the panel cannot be unlocked.
        response = self.client.post(reverse("feed:mod_home"), {"key": ""})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("is_moderator"))

        # A pre-set moderator session must not be able to delete either.
        session = self.client.session
        session["is_moderator"] = True
        session.save()
        response = self.client.post(
            reverse("feed:mod_delete", args=[self.take.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Take.objects.filter(pk=self.take.pk).exists())

    def test_preferences_set_cookie(self):
        response = self.client.post(reverse("feed:set_theme"), {"theme": "dark"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies["aftertaste_theme"].value, "dark")

        response = self.client.post(reverse("feed:set_lang"), {"lang": "ru"})
        self.assertEqual(response.cookies["aftertaste_lang"].value, "ru")

        response = self.client.post(reverse("feed:set_accent"), {"accent": "210"})
        self.assertEqual(response.cookies["aftertaste_accent"].value, "210")

    def test_delete_account_requires_correct_password(self):
        self.client.force_login(self.anna)
        url = reverse("feed:delete_account")

        response = self.client.post(url, {"password": "wrong"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.anna.pk).exists())

        self.client.post(url, {"password": "secret123"})
        self.assertFalse(User.objects.filter(pk=self.anna.pk).exists())

    def test_cannot_edit_other_users_take(self):
        self.client.force_login(self.leo)
        response = self.client.post(
            reverse("feed:take_edit", args=[self.take.pk]),
            {"drink_name": "Hacked", "content": "This should never be saved."},
        )
        self.assertEqual(response.status_code, 302)
        self.take.refresh_from_db()
        self.assertEqual(self.take.drink_name, "Oat flat white")


class PageRenderingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "mira", "mira@example.com", "secret123"
        )
        self.take = Take.objects.create(
            author=self.user,
            drink_name="Cortado",
            content="Equal parts milk and espresso, short and balanced.",
        )

    def test_login_by_email(self):
        response = self.client.post(
            reverse("feed:login"),
            {"identifier": "mira@example.com", "password": "secret123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_by_username(self):
        response = self.client.post(
            reverse("feed:login"),
            {"identifier": "mira", "password": "secret123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_ignores_external_next(self):
        for target in ("https://evil.example/phish", "//evil.example", "/\\evil.example"):
            response = self.client.post(
                reverse("feed:login") + "?next=" + target,
                {"identifier": "mira", "password": "secret123"},
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/")
            self.client.logout()

    def test_login_honours_local_next(self):
        response = self.client.post(
            reverse("feed:login") + "?next=/settings/",
            {"identifier": "mira", "password": "secret123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/settings/")

    def test_login_rejects_bad_password(self):
        response = self.client.post(
            reverse("feed:login"),
            {"identifier": "mira", "password": "nope"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("feed:register"),
            {
                "username": "newbie",
                "email": "newbie@example.com",
                "password1": "a-strong-pass-42",
                "password2": "a-strong-pass-42",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newbie")
        self.assertTrue(hasattr(user, "profile"))

    def test_settings_renders_anonymous(self):
        response = self.client.get(reverse("feed:settings"))
        self.assertEqual(response.status_code, 200)

    def test_settings_renders_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("feed:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Danger zone")

    def test_take_detail_renders(self):
        response = self.client.get(
            reverse("feed:take_detail", args=[self.take.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cortado")

    def test_notifications_page_requires_login(self):
        response = self.client.get(reverse("feed:notifications"))
        self.assertEqual(response.status_code, 302)

    def test_notifications_page_renders(self):
        self.client.force_login(self.user)
        Notification.objects.create(
            recipient=self.user,
            actor=self.user,
            kind=Notification.Kind.LIKE,
            take=self.take,
        )
        response = self.client.get(reverse("feed:notifications"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cortado")

    def test_russian_register_page(self):
        self.client.cookies["aftertaste_lang"] = "ru"
        response = self.client.get(reverse("feed:register"))
        self.assertContains(response, "Повторите пароль")

    def test_russian_cookie_translates_page(self):
        self.client.cookies["aftertaste_lang"] = "ru"
        response = self.client.get(reverse("feed:home"))
        self.assertContains(response, "Лента")

    def test_manifest_and_service_worker(self):
        self.assertEqual(self.client.get(reverse("feed:manifest")).status_code, 200)
        self.assertEqual(self.client.get(reverse("feed:service_worker")).status_code, 200)

    def test_delete_account_rejects_bad_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("feed:delete_account"), {"password": "wrong"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_account_removes_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("feed:delete_account"), {"password": "secret123"}
        )
        self.assertRedirects(response, reverse("feed:home"))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_update_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("feed:update_profile"),
            {"display_name": "Mira K", "bio": "Coffee, then opinions."},
        )
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, "Mira K")
        self.assertEqual(self.user.profile.bio, "Coffee, then opinions.")


class SeedDemoTests(TestCase):
    def test_seed_demo_is_idempotent(self):
        call_command("seed_demo", verbosity=0)
        first = (
            User.objects.count(),
            Take.objects.count(),
            Like.objects.count(),
            Repost.objects.count(),
            Follow.objects.count(),
            Comment.objects.count(),
            Notification.objects.count(),
        )
        call_command("seed_demo", verbosity=0)
        second = (
            User.objects.count(),
            Take.objects.count(),
            Like.objects.count(),
            Repost.objects.count(),
            Follow.objects.count(),
            Comment.objects.count(),
            Notification.objects.count(),
        )
        self.assertEqual(first, second)
