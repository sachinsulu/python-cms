# media_manager/tracking.py
"""
Service layer for recording and clearing MediaUsage records.

Usage example (articles/views.py after article.save()):
    from media_manager.tracking import record_media_usage
    record_media_usage(article, "image", article.image)
"""

from django.contrib.contenttypes.models import ContentType

from .models import MediaUsage, Media


def record_media_usage(instance, field_name: str, media: "Media | None") -> None:
    """
    Upsert a usage record for (instance, field_name) → media.
    Pass media=None to clear the record (field was unassigned).
    """
    ct = ContentType.objects.get_for_model(instance)

    # Remove previous record for this field on this object
    MediaUsage.objects.filter(
        content_type=ct,
        object_id=instance.pk,
        field_name=field_name,
    ).delete()

    # Record new one if media is assigned
    if media is not None:
        MediaUsage.objects.get_or_create(
            media=media,
            content_type=ct,
            object_id=instance.pk,
            field_name=field_name,
        )


def clear_media_usage(instance) -> None:
    """
    Remove ALL usage records for a deleted object.
    Call this in a post_delete signal for any model that holds Media FKs.
    """
    ct = ContentType.objects.get_for_model(instance)
    MediaUsage.objects.filter(content_type=ct, object_id=instance.pk).delete()


def get_usage_count(media: "Media") -> int:
    return media.usages.count()


def is_media_in_use(media: "Media") -> bool:
    return media.usages.exists()
