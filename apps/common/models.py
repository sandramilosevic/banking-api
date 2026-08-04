import uuid
from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TimeStampModel(models.Model):
    """Abstract base model that adds a UUID primary key and
    created/updated timestamp fields to any model that inherits it."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContentView(TimeStampModel):
    """Append-only log that records EVERY view of an arbitrary content
    object (via a generic foreign key) by either an authenticated user
    or an anonymous visitor identified by IP address.

    Each call to record_view() creates a new row rather than updating
    an existing one. This matters for a banking application because:
      - Compliance (PCI-DSS, SOX, internal audit policies) typically
        requires an immutable trail of WHO accessed WHAT and WHEN,
        not just "last seen".
      - An "overwrite" approach destroys history - you can't
        reconstruct how many times something was viewed or the exact
        times it happened.
      - Forensic investigation (e.g. suspicious access to a customer
        account) needs the full access list, not an aggregate.

    If you need a quick "last viewed" lookup (e.g. for a UI badge like
    "viewed 5 min ago"), use get_last_view() below - it's a single
    query against this log rather than a separately maintained mutable
    field.
    """

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("Content Type")
    )
    object_id = models.UUIDField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="content_views",
        null=True,
        blank=True,
        verbose_name=_("User"),
    )

    viewer_ip = models.GenericIPAddressField(
        verbose_name=_("Viewer IP Address"), null=True, blank=True
    )

    # Note: there is no separate last_viewed_at field. Since every row
    # represents exactly one view at one point in time, created_at
    # (inherited from TimeStampModel) already carries that information -
    # no need for a second, mutable timestamp field.

    class Meta:
        verbose_name = _("Content View")
        verbose_name_plural = _("Content Views")

        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user"]),
            models.Index(fields=["viewer_ip"]),
        ]

    def __str__(self) -> str:
        """Return a human-readable representation showing who viewed
        what content and when."""
        return (
            f"{self.content_type} viewed by "
            f"{self.user.get_full_name() if self.user else 'Anonymous'} "
            f"at {self.created_at}"
        )

    @classmethod
    def record_view(
        cls, content_object: Any, user: Optional[User], viewer_ip: Optional[str]
    ) -> "ContentView":
        """Record a view of the given content object.

        Looks up the ContentType for the passed object and creates a
        new ContentView row for this call (append-only log - see the
        class docstring above).

        Args:
            content_object: The model instance being viewed.
            user: The authenticated user viewing the content, or None
                for anonymous visitors.
            viewer_ip: The IP address of the viewer (used to
                distinguish anonymous visitors).

        Returns:
            The newly created ContentView instance.
        """
        content_type = ContentType.objects.get_for_model(content_object)

        return cls.objects.create(
            content_type=content_type,
            object_id=content_object.id,
            user=user,
            viewer_ip=viewer_ip,
        )

    @classmethod
    def get_last_view(
        cls,
        content_object: Any,
        user: Optional[User] = None,
        viewer_ip: Optional[str] = None,
    ) -> Optional["ContentView"]:
        """Return the most recent recorded view for the given content
        object, optionally filtered by user and/or viewer IP.

        This replaces the functionality that the old last_viewed_at
        field used to provide: "when was this last viewed" is now
        answered by querying the append-only log instead of reading a
        separately maintained mutable field.
        """
        content_type = ContentType.objects.get_for_model(content_object)
        qs = cls.objects.filter(content_type=content_type, object_id=content_object.id)
        if user is not None:
            qs = qs.filter(user=user)
        if viewer_ip is not None:
            qs = qs.filter(viewer_ip=viewer_ip)
        return qs.order_by("-created_at").first()
