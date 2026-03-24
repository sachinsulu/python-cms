# testimonials/models.py
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import transaction
from django.db.models import Max

from media_manager.mixins import MediaUsageMixin


class Testimonial(MediaUsageMixin, models.Model):
    media_fields = ['image']
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    title    = models.CharField(max_length=255)
    name     = models.CharField(max_length=255)
    content  = RichTextUploadingField()
    rating   = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, default=5
    )
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)


    # ── FK ────────────────────────────────────────────────────────
    image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='testimonial_images',
        verbose_name='Image',
    )

    linksrc  = models.URLField(blank=True, null=True, verbose_name='Link Source')
    country  = models.CharField(max_length=100, blank=True)
    via_type = models.CharField(max_length=100, blank=True, verbose_name='Via')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['position']
        verbose_name        = 'Testimonial'
        verbose_name_plural = 'Testimonials'

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