import logging
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile

from .models import Media, MediaFolder

User = get_user_model()
logger = logging.getLogger(__name__)


class MediaService:

    @staticmethod
    def upload(
        file: UploadedFile,
        folder: MediaFolder | None = None,
        user: User | None = None,
        title: str = "",
        alt_text: str = "",
    ) -> Media:
        """
        Create and persist a Media instance.
        All metadata extraction happens in Media.save().
        """
        if user is None or not user.is_authenticated:
            raise PermissionError("An authenticated user is required to upload media.")

        media = Media(
            file=file,
            folder=folder,
            uploaded_by=user,
            title=title,
            alt_text=alt_text,
        )
        media.save()
        logger.info(
            "Media uploaded: id=%s title=%r user=%s",
            media.pk,
            media.title,
            user.username,
        )
        return media

    @staticmethod
    def delete(media: Media) -> None:
        """
        Delete the Media record AND its physical file from disk.
        The cms/signals.py global cleanup will also fire — that's fine,
        it's idempotent (checks os.path.isfile before removing).
        """
        title = str(media)
        pk = media.pk
        if media.file:
            try:
                media.file.delete(save=False)
            except Exception as exc:
                logger.error(
                    "Failed to delete file for Media id=%s: %s", pk, exc
                )
        media.delete()
        logger.info("Media deleted: id=%s title=%r", pk, title)

    @staticmethod
    def move_to_folder(
        media: Media, folder: MediaFolder | None
    ) -> Media:
        """Move a media item to a different folder (or root if None)."""
        media.folder = folder
        media.save(update_fields=["folder"])
        return media