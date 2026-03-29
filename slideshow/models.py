from django.db import models, transaction
from django.db.models import Max
from ckeditor_uploader.fields import RichTextUploadingField
from media_manager.mixins import MediaUsageMixin


class Slideshow(MediaUsageMixin, models.Model):
    media_fields = ['image']

    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
    ]

    title    = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    type     = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_IMAGE)
    image    = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='slideshow_images',
        verbose_name='Image / Video',
    )
    content  = RichTextUploadingField(blank=True)
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name        = 'Slideshow'
        verbose_name_plural = 'Slideshows'

    @property
    def image_url(self):
        if self.image_id:
            try:
                if self.image.active:
                    return self.image.file.url
            except (ValueError, AttributeError):
                pass
        return None

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk or self.position == 0:
                last = Slideshow.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last or 0) + 1
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title