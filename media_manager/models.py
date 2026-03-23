# media_manager/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import os
from PIL import Image, UnidentifiedImageError
from django.db import transaction
from django.db.models import Max

User = get_user_model()


def media_upload_path(instance, filename):
    """
    Resolves physical upload path based on assigned folder.

    Results:
        With folder:    media/{slugified-folder-name}/{filename}
        Without folder: media/library/{filename}

    NOTE: instance.folder must be set BEFORE save() is called.
    MediaService.upload() guarantees this by passing folder= at
    object construction time.
    """
    if instance.folder:
        folder_name = slugify(instance.folder.name)
        return f'{folder_name}/{filename}'
    return f'library/{filename}'


class MediaFolder(models.Model):
    name   = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Media Folder"
        verbose_name_plural = "Media Folders"

    def __str__(self):
        return self.name

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
        """Filesystem-safe folder name."""
        return slugify(self.name)


class Media(models.Model):
    TYPE_IMAGE = "image"
    TYPE_VIDEO = "video"
    TYPE_FILE  = "file"

    TYPE_CHOICES = [
        (TYPE_IMAGE, "Image"),
        (TYPE_VIDEO, "Video"),
        (TYPE_FILE,  "File"),
    ]

    VIDEO_EXTENSIONS = {"mp4", "webm", "ogg", "mov", "avi", "mkv"}

    title  = models.CharField(max_length=255, blank=True)
    file   = models.FileField(upload_to=media_upload_path)  # ← callable now
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering   = ["-created_at"]
        verbose_name        = "Media"
        verbose_name_plural = "Media"

    def __str__(self):
        return self.title or (self.file.name if self.file else f"Media #{self.pk}")

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if self.file and not update_fields:
            if hasattr(self.file, "size"):
                self.size = self.file.size

            if not self.title:
                self.title = os.path.splitext(
                    os.path.basename(self.file.name)
                )[0].replace("_", " ").replace("-", " ").title()
            
            if not self.alt_text:
                self.alt_text = self.title

            ext = os.path.splitext(self.file.name)[1].lstrip(".").lower()
            if ext in self.VIDEO_EXTENSIONS:
                self.type = self.TYPE_VIDEO
            else:
                try:
                    self.file.seek(0)
                    with Image.open(self.file) as img:
                        img.verify()
                    self.file.seek(0)
                    with Image.open(self.file) as img:
                        self.width, self.height = img.size
                    self.type = self.TYPE_IMAGE
                    self.file.seek(0)
                except (IOError, SyntaxError, UnidentifiedImageError):
                    self.type  = self.TYPE_FILE
                    self.width = None
                    self.height = None

        super().save(*args, **kwargs)

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