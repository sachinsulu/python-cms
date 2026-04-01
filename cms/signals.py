
import os
import re
import logging
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.db.models import FileField, TextField
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 1. Cleanup when object is DELETED (With Cross-Model Check)
# ---------------------------------------------------------
@receiver(post_delete)
def global_delete_files_on_delete(sender, instance, **kwargs):
    """
    Deletes files only if they are not used by ANY model in the project.
    """
    if sender.__name__ == 'Media':
        return

    for field in instance._meta.fields:
        # A. Standard FileFields
        if isinstance(field, FileField):
            file = getattr(instance, field.name)
            if file and file.name and os.path.isfile(file.path):
                try:
                    os.remove(file.path)
                except Exception as e:
                    logger.error("File cleanup error on delete: %s", e)

        # B. CKEditor Images with Cross-Model Check
        elif isinstance(field, TextField):
            content = getattr(instance, field.name, "")
            if not content:
                continue

            pattern = r'src="' + re.escape(settings.MEDIA_URL) + r'([^"]+)"'
            image_paths = re.findall(pattern, content)

            for path in image_paths:
                full_path = os.path.join(settings.MEDIA_ROOT, path)
                img_url_to_check = settings.MEDIA_URL + path
                
                if is_image_in_use_anywhere(img_url_to_check):
                    logger.debug("CLEANUP: Skipped %s (still used in another record)", path)
                else:
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                            logger.info("CLEANUP: Deleted %s (no usage anywhere)", path)
                        except Exception as e:
                            logger.error("CLEANUP error: %s", e)

# Models that can contain CKEditor-embedded image URLs in TextFields.
# Update this list if you add new models with RichText fields.
_CKEDITOR_CONTENT_FIELDS = [
    ('articles', 'Article',     'content'),
    ('blog',     'Blog',        'content'),
    ('faq',      'FAQ',         'content'),
    ('nearby',   'Nearby',      'content'),
    ('offers',   'Offer',       'content'),
    ('features', 'Feature',     'content'),
    ('services', 'Service',     'content'),
    ('package',  'Package',     'description'),
    ('package',  'SubPackage',  'description'),
    ('location', 'Location',    'content'),
]

def is_image_in_use_anywhere(img_url):
    """
    Checks only known CKEditor-capable models for a specific image URL.
    Avoids a full apps.get_models() scan on every deletion.
    """
    from django.apps import apps
    for app_label, model_name, field_name in _CKEDITOR_CONTENT_FIELDS:
        try:
            model = apps.get_model(app_label, model_name)
            if model.objects.filter(**{f"{field_name}__icontains": img_url}).exists():
                return True
        except LookupError:
            continue
    return False

# ---------------------------------------------------------
# 2. GlobalSlug Synchronization
# ---------------------------------------------------------
TRACKED_SLUG_MODELS = ['Article', 'Blog', 'Package', 'SubPackage']

@receiver(post_save)
def update_global_slug_on_save(sender, instance, created, **kwargs):
    model_name = sender.__name__
    if model_name in TRACKED_SLUG_MODELS and hasattr(instance, 'slug') and instance.slug:
        from core.models import GlobalSlug
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(sender)
        GlobalSlug.objects.update_or_create(
            content_type=content_type,
            object_id=instance.id,
            defaults={'slug': instance.slug}
        )

@receiver(post_delete)
def delete_global_slug_on_delete(sender, instance, **kwargs):
    model_name = sender.__name__
    if model_name in TRACKED_SLUG_MODELS:
        from core.models import GlobalSlug
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(sender)
        GlobalSlug.objects.filter(
            content_type=content_type,
            object_id=instance.id
        ).delete()

