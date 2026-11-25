from django.contrib import admin

from .models import Comment, Follow, Like, Notification, Profile, Repost, Take


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "created_at")
    search_fields = ("user__username", "user__email", "display_name")


@admin.register(Take)
class TakeAdmin(admin.ModelAdmin):
    list_display = ("drink_name", "author", "created_at", "updated_at")
    search_fields = ("drink_name", "content", "author__username")
    list_filter = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "take", "created_at")
    search_fields = ("content", "author__username")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "take", "created_at")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")


@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):
    list_display = ("user", "take", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "actor", "kind", "created_at", "is_read")
    list_filter = ("kind", "is_read")
