from django.contrib import admin
from typing import Any
from django.contrib.admin import GenericTabularInline
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import ContentView


@admin.register(ContentView)
class ContentViewAdmin(admin.ModelAdmin):
    """Admin interface for the ContentView model."""

    list_display = [
        "content_object",
        "content_type",
        "user",
        "viewer_ip",
        "last_viewed_at",
        "created_at",
    ]

    list_filter = ["content_type", "last_viewed_at", "created_at"]

    date_hierarchy = "last_viewed_at"

    readonly_fields = [
        "content_type",
        "object_id",
        "content_object",
        "user",
        "viewer_ip",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (None, {"fields": ("content_type", "object_id", "content_object")}),
        (_("Viewer Details"), {"fields": ("user", "viewer_ip", "last_viewed_at")}),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Disable the ability to add new ContentView instances via the admin."""
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Disable the ability to change existing ContentView instances via the admin."""
        return False


class ContentViewInline(GenericTabularInline):
    """Inline admin interface for displaying ContentView instances related to a specific content object."""

    model = ContentView
    extra = 0
    readonly_fields = [
        "user",
        "viewer_ip",
        "last_viewed_at",
        "created_at",
        "updated_at",
    ]
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Disable the ability to add new ContentView instances via the inline."""
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Disable the ability to change existing ContentView instances via the inline."""
        return False
