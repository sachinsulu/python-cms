from django.db import models, transaction
from django.db.models import Max


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
                last = FeatureGroup.objects.select_for_update().aggregate(Max('position'))['position__max']
                self.position = (last or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Feature(models.Model):
    group = models.ForeignKey(FeatureGroup, on_delete=models.CASCADE, related_name='features')
    title    = models.CharField(max_length=255)
    image    = models.ImageField(upload_to='features/', blank=True, null=True)
    content  = models.TextField(blank=True)
    icon     = models.CharField(max_length=255, blank=True, help_text='CSS class e.g. fa-solid fa-star')
    active   = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']

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