# media_manager/services.py
import os
import logging
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import shutil

from .models import Media, MediaFolder, media_upload_path

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
        folder must be passed here — not set after — so media_upload_path
        can resolve the correct filesystem path at upload time.
        """
        if user is None or not user.is_authenticated:
            raise PermissionError(
                "An authenticated user is required to upload media."
            )

        media = Media(
            file=file,
            folder=folder,   # ← set BEFORE save so upload_to callable sees it
            uploaded_by=user,
            title=title,
            alt_text=alt_text,
        )
        media.save()
        logger.info(
            "Media uploaded: id=%s title=%r path=%s user=%s",
            media.pk,
            media.title,
            media.file.name,
            user.username,
        )
        return media

    @staticmethod
    def delete(media: Media) -> None:
        """
        Delete the Media record AND its physical file from disk.
        """
        title = str(media)
        pk    = media.pk
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
        media: Media,
        folder: MediaFolder | None,
    ) -> Media:
        """
        Move a media item to a different folder.

        This physically moves the file on disk to match the new folder path,
        then updates the FK and file field in the database.

        If the physical move fails, the operation is aborted — the database
        record is NOT updated so it stays consistent with the filesystem.
        """
        if media.folder == folder:
            return media  # nothing to do

        # Calculate the new path using the same callable logic
        # We temporarily set folder on the instance so upload_to can resolve it
        old_file_name = media.file.name
        old_file_path = media.file.path

        # Build new path
        media.folder = folder
        new_file_name = media_upload_path(media, os.path.basename(old_file_name))
        new_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name)

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

        try:
            shutil.move(old_file_path, new_file_path)

            # Update the file field to point to the new path
            media.file.name = new_file_name
            media.save(update_fields=['file', 'folder'])

            logger.info(
                "Media moved: id=%s from=%s to=%s",
                media.pk, old_file_name, new_file_name,
            )

        except Exception as exc:
            # Roll back the folder assignment on the instance
            # so it stays consistent with what's on disk
            logger.error(
                "Media move failed: id=%s error=%s", media.pk, exc
            )
            # Re-fetch from DB to restore clean state
            media.refresh_from_db()
            raise

        return media