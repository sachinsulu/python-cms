# media_manager/models.py
import os

from django.db import models
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


def media_upload_path(instance, filename):
    """
    Resolves physical upload path based on assigned folder.

    Results:
        With folder:    {slug_pk}/{filename}
        Without folder: library/{filename}

    NOTE: instance.folder must be set BEFORE save() is called.
    MediaService.upload() guarantees this by passing folder= at
    object construction time.
    """
    if instance.folder:
        return f'{instance.folder.slug}/{filename}'
    return f'library/{filename}'

def thumbnail_upload_path(instance, filename):
    if instance.folder:
        return f'{instance.folder.slug}/thumbnails/{filename}'
    return f'library/thumbnails/{filename}'


class MediaFolder(models.Model):
    name   = models.CharField(max_length=255, db_index=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Media Folder"
        verbose_name_plural = "Media Folders"
        unique_together = ["parent", "name"]
        indexes = [
            models.Index(fields=["parent"], name="folder_parent_idx"),
            models.Index(fields=["name"],   name="folder_name_idx"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.parent and self.name.lower() == self.parent.name.lower():
            raise ValidationError(
                f"Cannot create folder '{self.name}' inside a folder with the same name."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_path(self):
        """Returns slash-separated path e.g. 'Articles / Hero'."""
        parts = [self.name]
        node  = self
        while node.parent_id:
            node = node.parent
            parts.insert(0, node.name)
        return " / ".join(parts)

    @property
    def slug(self):
        """Filesystem-safe folder path."""
        parts = [slugify(self.name)]
        node = self
        while node.parent_id:
            node = node.parent
            parts.insert(0, slugify(node.name))
        return "/".join(parts)


    pass

# ── Media ─────────────────────────────────────────────────────────────────────

class MediaQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)


class MediaManager(models.Manager):
    def get_queryset(self):
        return MediaQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class Media(models.Model):
    TYPE_IMAGE = "image"
    TYPE_VIDEO = "video"
    TYPE_FILE  = "file"

    TYPE_CHOICES = [
        (TYPE_IMAGE, "Image"),
        (TYPE_VIDEO, "Video"),
        (TYPE_FILE,  "File"),
    ]

    title  = models.CharField(max_length=255, blank=True)
    file   = models.FileField(upload_to=media_upload_path)
    thumbnail = models.FileField(
        upload_to=thumbnail_upload_path,
        null=True,
        blank=True
    )
    folder = models.ForeignKey(
        MediaFolder,
        null=True,
        blank=True,
        related_name="media",
        on_delete=models.SET_NULL,
    )
    type     = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_FILE,
        editable=False,
    )
    alt_text    = models.CharField(max_length=255, blank=True)
    size        = models.PositiveIntegerField(default=0, editable=False)
    width       = models.PositiveIntegerField(null=True, blank=True, editable=False)
    height      = models.PositiveIntegerField(null=True, blank=True, editable=False)
    uploaded_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_media",
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0, db_index=True)

    objects = MediaManager()

    class Meta:
        ordering = ["position", "-created_at"]
        verbose_name        = "Media"
        verbose_name_plural = "Media"
        indexes = [
            models.Index(fields=["folder"],           name="media_folder_idx"),
            models.Index(fields=["-created_at"],      name="media_created_idx"),
            models.Index(fields=["uploaded_by"],      name="media_uploader_idx"),
            models.Index(fields=["type"],             name="media_type_idx"),
            models.Index(fields=["folder", "position"],    name="media_folder_position_idx"),
            models.Index(fields=["folder", "-created_at"], name="media_folder_created_idx"),
        ]

    @classmethod
    def next_position(cls, folder) -> int:
        """Returns the next available position for a given folder."""
        result = cls.objects.filter(folder=folder).aggregate(max_pos=Max("position"))
        return (result["max_pos"] or 0) + 1

    def __str__(self):
        return self.title or (self.file.name if self.file else f"Media #{self.pk}")

    def save(self, *args, **kwargs):
        # Processing is handled by MediaService.upload() / processing.py.
        # Direct saves (update_fields from move_to_folder, restore, etc.) pass through cleanly.
        super().save(*args, **kwargs)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_image(self):
        return self.type == self.TYPE_IMAGE

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def size_display(self):
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        return f"{self.size / (1024 * 1024):.1f} MB"


# ── MediaUsage ────────────────────────────────────────────────────────────────

class MediaUsage(models.Model):
    """
    Tracks every FK/field that references a Media object.
    Populated via the tracking service layer.
    Enables: "Used in N places", safe-delete warnings, global replace.
    """
    media        = models.ForeignKey(
        Media, on_delete=models.CASCADE, related_name="usages"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id    = models.PositiveIntegerField()
    field_name   = models.CharField(max_length=100)
    position     = models.PositiveIntegerField(default=0)  # Phase 2: per-usage ordering

    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = [("media", "content_type", "object_id", "field_name")]
        indexes = [
            models.Index(fields=["media"],                     name="usage_media_idx"),
            models.Index(fields=["content_type", "object_id"], name="usage_object_idx"),
            models.Index(fields=["content_type", "object_id", "position"], name="usage_order_idx"),
        ]

    def __str__(self):
        return (
            f"Media#{self.media_id} → "
            f"{self.content_type}.{self.field_name} #{self.object_id}"
        )