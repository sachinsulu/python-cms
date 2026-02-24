import os
from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import transaction  # ✅ Add this import


class Article(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    content = RichTextUploadingField(blank=False)
    homepage = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
   
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    position = models.PositiveIntegerField(default=0)

    meta_title = models.CharField(
        max_length=60, 
        blank=True, 
       
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
    )
    meta_keywords = models.CharField(
        max_length=205, 
        blank=True, 
        
    )

    class Meta:
        ordering = ['position']
        
    def save(self, *args, **kwargs):
        # ✅ FIX: Wrap position logic in atomic transaction
        with transaction.atomic():
            if not self.id or self.position == 0:
                # ✅ FIX: Use select_for_update() to lock and prevent race condition
                last_pos = Article.objects.select_for_update().aggregate(
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