# popup/models.py
from django.db import models, transaction
from django.db.models import Max

from media_manager.mixins import MediaUsageMixin


class Popup(MediaUsageMixin, models.Model):
    media_fields = ['file']
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
    ]

    title      = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date   = models.DateField()
    type       = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=TYPE_IMAGE
    )
    link       = models.CharField(max_length=500, blank=True)
    status     = models.BooleanField(default=True)
    position   = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # ── FK — points to Media for both image and video ─────────────
    file = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='popup_files',
        verbose_name='File',
    )

    class Meta:
        ordering            = ['position']
        verbose_name        = 'Popup'
        verbose_name_plural = 'Popups'

    @property
    def file_url(self):
        """
        Resolves file URL from FK. Works for both image and video types.
        """
        if self.file_id:
            try:
                return self.file.file.url
            except (ValueError, AttributeError):
                pass
        return None

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                last = Popup.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last or 0) + 1
            super().save(*args, **kwargs)

    @property
    def is_image(self):
        return self.type == self.TYPE_IMAGE

    @property
    def is_video(self):
        return self.type == self.TYPE_VIDEO