# media_manager/services.py
import os
import logging

from django.db import transaction
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
            position=Media.next_position(folder),
        )
        media.save()
        logger.info(
            "Media uploaded: id=%s title=%r position=%s",
            media.pk, media.title, media.position,
        )
        return media

    @staticmethod
    @transaction.atomic
    def reorder(media_ids: list[int], folder) -> None:
        """
        Reorders media within a folder atomically.

        - Validates all IDs belong to the specified folder (IDOR prevention)
        - Uses bulk_update — single query for N items
        - Gaps from deletions are collapsed by this operation

        Args:
            media_ids: Ordered list of Media PKs as submitted by drag/drop frontend
            folder:    MediaFolder instance or None (root)
        """
        if not media_ids:
            return

        # Security: only update media that actually belongs to this folder
        # Prevents a malicious payload from reordering media in other folders
        qs = Media.objects.filter(pk__in=media_ids, folder=folder)
        media_map = {m.pk: m for m in qs.only("pk", "position")}

        if not media_map:
            return

        updates = []
        for index, media_id in enumerate(media_ids):
            media = media_map.get(media_id)
            if media is not None:
                media.position = index
                updates.append(media)

        Media.objects.bulk_update(updates, ["position"])
        logger.info(
            "Media reordered: folder=%s count=%s",
            getattr(folder, "pk", "root"),
            len(updates),
        )

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
            media.file.name = new_name
        except Exception as exc:
            # Clean up the partially written destination if it exists
            if default_storage.exists(new_name):
                try:
                    default_storage.delete(new_name)
                except Exception:
                    pass
            logger.error("Media move failed: id=%s error=%s", media.pk, exc)
            raise

        media.folder = folder
        media.position = Media.next_position(folder)  # place at end of new folder
        media.save(update_fields=["file", "folder", "position"])

        logger.info("Media moved: id=%s → folder=%s position=%s",
                    media.pk, getattr(folder, "pk", "root"), media.position)
        return media