
import os
import re
import logging
from django.db.models.signals import post_delete, pre_save
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
# 2. Cleanup when file is UPDATED (FileFields)
# ---------------------------------------------------------
@receiver(pre_save)
def global_delete_old_files_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False

    for field in instance._meta.fields:
        if isinstance(field, FileField):
            old_file = getattr(old_instance, field.name)
            new_file = getattr(instance, field.name)

            if old_file and old_file != new_file:
                if old_file.name and os.path.isfile(old_file.path):
                    try:
                        os.remove(old_file.path)
                    except Exception as e:
                        logger.error("File update cleanup error: %s", e)