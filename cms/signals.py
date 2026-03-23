
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

def is_image_in_use_anywhere(img_url):
    """
    Searches all models in the project for a specific image URL.
    """
    # Loop through every model registered in your Django project
    for model in apps.get_models():
        # Look for models that have TextFields
        text_fields = [f.name for f in model._meta.fields if isinstance(f, TextField)]
        
        for field_name in text_fields:
            # Check if any record in this model contains the image URL
            if model.objects.filter(**{f"{field_name}__icontains": img_url}).exists():
                return True
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