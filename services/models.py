# services/models.py
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Service(models.Model):
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

    # ── Legacy ────────────────────────────────────────────────────
    image_legacy = models.ImageField(
        upload_to='services/',
        blank=True, null=True,
        verbose_name='[Legacy] Image',
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
        if self.image_legacy:
            try:
                return self.image_legacy.url
            except (ValueError, AttributeError):
                pass
        return None

    def __str__(self):
        return self.title