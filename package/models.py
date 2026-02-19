from django.db import models, transaction
from django.utils.text import slugify
from django.db.models import Max


class Package(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('room', 'Room'),
        ('non_room', 'Non-Room'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
    package_type = models.CharField(
        max_length=10,
        choices=PACKAGE_TYPE_CHOICES,
        default='non_room',
    )
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']

    @property
    def is_room(self):
        return self.package_type == 'room'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.id or self.position == 0:
                last_pos = Package.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last_pos or 0) + 1

            if not self.slug:
                base_slug = slugify(self.title, allow_unicode=True)
                slug = base_slug
                counter = 1
                while Package.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_package_type_display()})"