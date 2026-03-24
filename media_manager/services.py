# media_manager/services.py
import os
import logging

from django.db import transaction
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from PIL import Image
import io

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

        # Ensure file pointer is safe
        file.seek(0)

        if meta.get("type") == "image":
            try:
                with Image.open(file) as img:
                    img_format = img.format or "JPEG"
                    
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                        
                    img.thumbnail((300, 300))

                    thumb_io = io.BytesIO()
                    img.save(thumb_io, format=img_format)

                    filename = os.path.basename(media.file.name)
                    if folder:
                        folder_slug = getattr(folder, 'slug', None) or "root"
                        thumb_name = f"{folder_slug}/thumbnails/{filename}"
                    else:
                        thumb_name = f"root/thumbnails/{filename}"

                    media.thumbnail.save(
                        thumb_name,
                        ContentFile(thumb_io.getvalue()),
                        save=False
                    )

                    media.save(update_fields=["thumbnail"])

            except Exception as e:
                logger.error("Thumbnail generation failed: %s", e)

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
    def delete(media: Media) -> None:
        """
        Permanently deletes a Media object (DB record + files on disk).
        MediaUsage rows are cascade-deleted automatically by the DB.
        The post_delete signal in signals.py handles media.file cleanup.
        """
        storage = media.file.storage

        # 1. Delete thumbnail (not covered by the post_delete signal)
        if media.thumbnail and storage.exists(media.thumbnail.name):
            storage.delete(media.thumbnail.name)

        # 2. Delete DB record — cascades to MediaUsage rows automatically
        pk = media.pk
        media.delete()
        logger.info("Media permanently deleted: id=%s", pk)




class FolderService:

    @staticmethod
    def delete(folder: MediaFolder):
        """
        Delete folder ONLY if empty.
        """

        if folder.children.exists():
            raise ValidationError(
                "Cannot delete folder: contains subfolders."
            )

        if folder.media.exists():
            raise ValidationError(
                "Cannot delete folder: contains media files."
            )

        folder.delete()