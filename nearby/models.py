from django.db import models, transaction
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Max

# Create your models here.
class Nearby(models.Model):
    title = models.CharField(max_length=255)
    distance = models.CharField(max_length=255)
    map = models.CharField(max_length=255)
    content = RichTextUploadingField(blank=True)
    active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['position']

    def save(self, *args, **kwargs):
        # ✅ FIX: Wrap position logic in atomic transaction
        with transaction.atomic():
            if not self.id:
                # ✅ FIX: Use select_for_update() to lock and prevent race condition
                last_pos = Nearby.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last_pos or 0) + 1

            super().save(*args, **kwargs)

    def __str__(self):
        return self.title