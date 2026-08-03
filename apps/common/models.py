import uuid
from typing import Any, Dict, Optional
from django.contrib.auth.models import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TimeStampModel(models.Model):
    """Abstract base model that adds a UUID primary key and
    created/updated timestamp fields to any model that inherits it."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContentView(TimeStampModel):
    """Tracks a single view of an arbitrary content object (via a
    generic foreign key) by either an authenticated user or an
    anonymous visitor identified by IP address."""

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("Content Type")
    )
    object_id = models.UUIDField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="content_views",
        null=True,
        blank=True,
        verbose_name=_("User"),
    )

    viewer_ip = models.GenericIPAddressField(
        verbose_name=_("Viewer IP Address"), null=True, blank=True
    )

    last_viewed_at = models.DateTimeField()

    class Meta:
        verbose_name = _("Content View")
        verbose_name_plural = _("Content Views")
        unique_together = ["content_type", "object_id", "user", "viewer_ip"]

    def __str__(self) -> str:
        """Return a human-readable representation showing who viewed
        what content and when."""
        return f"{self.content_type} viewed by {self.user.get_full_name() if self.user else 'Anonymous'} at {self.last_viewed_at}"

    @classmethod
    def record_view(
        cls, content_object: Any, user: Optional[User], viewer_ip: Optional[str]
    ) -> "ContentView":
        """Record (or update) a view of the given content object.

        Looks up the ContentType for the passed object and creates a
        ContentView entry for the given user/viewer_ip combination. If
        an entry already exists, its `last_viewed_at` timestamp is
        refreshed instead of creating a duplicate row.

        Args:
            content_object: The model instance being viewed.
            user: The authenticated user viewing the content, or None
                for anonymous visitors.
            viewer_ip: The IP address of the viewer (used to
                distinguish anonymous visitors).

        Returns:
            The created or updated ContentView instance.
        """
        content_type = ContentType.objects.get_for_model(content_object)

        try:
            view, created = cls.objects.get_or_create(
                object_id=content_object.id,
                user=user,
                viewer_ip=viewer_ip,
                content_type=content_type,
                defaults={"last_viewed_at": timezone.now()},
            )
        except IntegrityError:
            # Handle a race condition where two requests try to create
            # the same view at the same time.
            view = cls.objects.get(
                object_id=content_object.id,
                user=user,
                viewer_ip=viewer_ip,
                content_type=content_type,
            )
            created = False

        if not created:
            view.last_viewed_at = timezone.now()
            view.save()

        return view
