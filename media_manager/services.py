# media_manager/services.py
import os
import logging

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile

from .models import Media, MediaFolder, media_upload_path
from .processing import process_upload_file, derive_title

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
            raise PermissionError("Authenticated user required.")

        meta = process_upload_file(file)

        resolved_title = title.strip() or derive_title(file.name)
        resolved_alt   = alt_text.strip() or ""  # Don't silently copy a bad filename

        media = Media(
            file=file,
            folder=folder,          # set BEFORE save so upload_to callable sees it
            uploaded_by=user,
            title=resolved_title,
            alt_text=resolved_alt,
            size=meta["size"],
            type=meta["type"],
            width=meta["width"],
            height=meta["height"],
        )
        media.save()
        logger.info(
            "Media uploaded: id=%s title=%r user=%s",
            media.pk, media.title, user.username,
        )
        return media

    @staticmethod
    def delete(media: Media, soft: bool = True, force: bool = False) -> None:
        """
        soft=True  → marks is_deleted, preserves file (recoverable until purged)
        soft=False → permanent deletion including physical file (via post_delete signal)
        force=True → skips the in-use safety check
        """
        from .tracking import is_media_in_use

        if not force and is_media_in_use(media):
            usage_count = media.usages.count()
            raise ValueError(
                f"Cannot delete Media#{media.pk} — still referenced in "
                f"{usage_count} place(s). Pass force=True to override or "
                "remove references first."
            )

        if soft:
            media.soft_delete()
            logger.info("Media soft-deleted: id=%s title=%r", media.pk, str(media))
        else:
            title, pk = str(media), media.pk
            media.delete()  # post_delete signal handles file cleanup
            logger.info("Media hard-deleted: id=%s title=%r", pk, title)

    @staticmethod
    def move_to_folder(media: Media, folder: MediaFolder | None) -> Media:
        """
        Moves a media file to a new folder using Django's storage API.
        Works with local filesystem, S3, GCS, Azure — any backend.
        Atomic: DB is only updated after a successful file operation.
        """
        if media.folder_id == (folder.pk if folder else None):
            return media  # nothing to do

        old_name = media.file.name

        # Build new path without mutating the instance prematurely
        class _Proxy:
            pass
        proxy = _Proxy()
        proxy.folder = folder
        new_name = media_upload_path(proxy, os.path.basename(old_name))

        if old_name == new_name:
            # Path identical (same folder slug), just update FK
            media.folder = folder
            media.save(update_fields=["folder"])
            return media

        try:
            content = default_storage.open(old_name).read()
            default_storage.save(new_name, ContentFile(content))
            default_storage.delete(old_name)

            media.folder = folder
            media.file.name = new_name
            media.save(update_fields=["file", "folder"])

            logger.info(
                "Media moved: id=%s  %s → %s", media.pk, old_name, new_name
            )

        except Exception as exc:
            # Clean up the partially written destination if it exists
            if default_storage.exists(new_name):
                try:
                    default_storage.delete(new_name)
                except Exception:
                    pass
            logger.error("Media move failed: id=%s error=%s", media.pk, exc)
            raise

        return media