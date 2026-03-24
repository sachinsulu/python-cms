# media_manager/mixins.py
from django.db import models
from .tracking import record_media_usage, clear_media_usage

class MediaUsageMixin:
    """
    Mixin to automatically track Media usage for any model with Media ForeignKeys.
    
    To use:
    1. Add MediaUsageMixin as a base class.
    2. Define `media_fields` as a list of field names that are Media FKs.
    """
    media_fields = ['image']  # Default, can be overridden

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for field in self.media_fields:
            if hasattr(self, field):
                media = getattr(self, field)
                record_media_usage(self, field, media)

    def delete(self, *args, **kwargs):
        clear_media_usage(self)
        super().delete(*args, **kwargs)
