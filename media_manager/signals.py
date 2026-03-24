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


# ── Folder tree cache invalidation ───────────────────────────────────────────

@receiver(post_save, sender=MediaFolder)
@receiver(post_delete, sender=MediaFolder)
def invalidate_folder_cache(sender, **kwargs):
    bust_folder_tree_cache()
