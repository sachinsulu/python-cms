# features/models.py
from django.db import models, transaction
from django.db.models import Max
from ckeditor_uploader.fields import RichTextUploadingField


class FeatureGroup(models.Model):
    title    = models.CharField(max_length=255)
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']

    def save(self, *args, **kwargs):
        if not self.pk or self.position == 0:
            with transaction.atomic():
                last = FeatureGroup.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Feature(models.Model):
    group   = models.ForeignKey(
        FeatureGroup, on_delete=models.CASCADE, related_name='features'
    )
    title   = models.CharField(max_length=255)
    content = RichTextUploadingField(blank=True)
    icon    = models.CharField(
        max_length=255, blank=True,
        help_text='CSS class e.g. fa-solid fa-star'
    )
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # ── FK ────────────────────────────────────────────────────────
    image = models.ForeignKey(
        'media_manager.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='feature_images',
        verbose_name='Image',
    )

    class Meta:
        ordering = ['position']

    @property
    def image_url(self):
        if self.image_id:
            try:
                return self.image.file.url
            except (ValueError, AttributeError):
                pass
        return None

    def save(self, *args, **kwargs):
        if not self.pk or self.position == 0:
            with transaction.atomic():
                last = Feature.objects.select_for_update().filter(
                    group=self.group
                ).aggregate(Max('position'))['position__max']
                self.position = (last or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} -> {self.group.title}"