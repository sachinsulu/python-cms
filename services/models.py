# services/models.py
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import transaction
from django.db.models import Max

from media_manager.mixins import MediaUsageMixin


class Service(MediaUsageMixin, models.Model):
    media_fields = ['image']
    TYPE_MAIN_SERVICE = 'main-service'
    TYPE_SERVICE      = 'service'
    TYPE_CHOICES      = [
        (TYPE_MAIN_SERVICE, 'Main Service'),
        (TYPE_SERVICE,      'Service'),
    ]

    title  = models.CharField(max_length=255)
    icon   = models.CharField(
        max_length=255, blank=True,
        help_text='CSS class e.g. fa-brands fa-instagram'
    )
    link    = models.CharField(max_length=500, blank=True)
    content = RichTextUploadingField(blank=True)
    status  = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    type    = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_MAIN_SERVICE
    )


    # ── FK ────────────────────────────────────────────────────────
    image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='service_images',
        verbose_name='Image',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['position']
        verbose_name        = 'Service'
        verbose_name_plural = 'Services'

    @property
    def image_url(self):
        if self.image_id:
            try:
                return self.image.file.url
            except (ValueError, AttributeError):
                pass
        return None

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk or self.position == 0:
                last = Service.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last or 0) + 1
            super().save(*args, **kwargs)