from django.db import models,transaction
from django.utils.text import slugify
from django.db.models import Max

# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    homepage = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']
    

    def save(self, *args, **kwargs):
    # ✅ FIX: Wrap position logic in atomic transaction
        with transaction.atomic():
            if not self.id or self.position == 0:
                # ✅ FIX: Use select_for_update() to lock and prevent race condition
                last_pos = Blog.objects.select_for_update().aggregate(
                    Max('position')
                )['position__max']
                self.position = (last_pos or 0) + 1
            
            # Unique Slug Logic
            if not self.slug:
                from cms.utils import is_slug_taken
                base_slug = slugify(self.title, allow_unicode=True)
                slug = base_slug
                counter = 1
                while is_slug_taken(slug, exclude_obj=self):
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug
            
            super().save(*args, **kwargs)


    def __str__(self):
        return self.title