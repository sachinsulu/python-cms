# media_manager/signals.py
import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Media, MediaFolder
from .utils import bust_folder_tree_cache

logger = logging.getLogger(__name__)


# ── File cleanup on any deletion path ────────────────────────────────────────

@receiver(post_delete, sender=Media)
def delete_media_file_on_model_delete(sender, instance, **kwargs):
    """
    Fires on ANY deletion path — admin, shell, ORM, MediaService.
    MediaService.delete(soft=False) also calls media.delete() which triggers this.
    """
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception as exc:
            logger.error(
                "File cleanup failed for Media id=%s path=%s: %s",
                instance.pk,
                instance.file.name,
                exc,
            )
    if instance.thumbnail:
        try:
            instance.thumbnail.delete(save=False)
        except Exception as exc:
            logger.error(
                "Thumbnail cleanup failed for Media id=%s path=%s: %s",
                instance.pk,
                instance.thumbnail.name,
                exc,
            )


@receiver(post_delete, sender=MediaFolder)
def delete_folder_directory_on_model_delete(sender, instance, **kwargs):
    """
    Cleaner for the physical directory. 
    Note: MediaFolder.slug depends on PK, which is still available in post_delete.
    """
    import shutil
    from django.conf import settings
    import os

    # Resolve the physical path
    # MediaFolder.slug = slugify(name)_pk
    folder_path = os.path.join(settings.MEDIA_ROOT, instance.slug)
    
    if os.path.exists(folder_path):
        try:
            # Only delete if empty? Or delete everything? 
            # FolderService.delete already checks for children/media in DB.
            # But there might be thumbnail subfolders or stray files.
            shutil.rmtree(folder_path)
            logger.info("Physical folder deleted: %s", folder_path)
        except Exception as exc:
            logger.error("Failed to delete physical folder %s: %s", folder_path, exc)


# ── Folder tree cache invalidation ───────────────────────────────────────────

@receiver(post_save, sender=MediaFolder)
@receiver(post_delete, sender=MediaFolder)
def invalidate_folder_cache(sender, **kwargs):
    bust_folder_tree_cache()
