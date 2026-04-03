# media_manager/management/commands/import_ckeditor_uploads.py
"""
Management command: import_ckeditor_uploads

Scans media/uploads/ (the legacy CKEditor drop folder) and creates a Media
record for every file that is not already tracked, putting them in the
"ckeditor" MediaFolder so they appear in the Media Manager library.

Usage:
    python manage.py import_ckeditor_uploads           # dry-run (preview only)
    python manage.py import_ckeditor_uploads --apply   # actually import

Options:
    --apply         Write records to the database (default is dry-run).
    --folder NAME   Target folder name in Media Manager (default: ckeditor).
    --scan-path     Relative path inside MEDIA_ROOT to scan (default: uploads).
"""
import os
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from media_manager.models import Media, MediaFolder
from media_manager.processing import process_upload_file, derive_title

logger = logging.getLogger(__name__)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"}
VIDEO_EXTS = {".mp4", ".webm", ".ogg", ".mov", ".avi", ".mkv"}
SKIP_DIRS  = {"thumbnails"}  # skip auto-generated thumbnail subdirs


class Command(BaseCommand):
    help = "Import legacy CKEditor uploads from media/uploads/ into the Media Manager."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Write records to the database. Without this flag the command is a dry-run.",
        )
        parser.add_argument(
            "--folder",
            default="ckeditor",
            help="MediaFolder name to import files into (created if missing).",
        )
        parser.add_argument(
            "--scan-path",
            default="uploads",
            help="Subdirectory inside MEDIA_ROOT to scan (default: uploads).",
        )

    def handle(self, *args, **options):
        apply       = options["apply"]
        folder_name = options["folder"]
        scan_rel    = options["scan_path"]

        scan_dir = os.path.join(settings.MEDIA_ROOT, scan_rel)

        if not os.path.isdir(scan_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {scan_dir}"))
            return

        if not apply:
            self.stdout.write(
                self.style.WARNING(
                    "DRY-RUN mode -- no records will be written. "
                    "Pass --apply to actually import.\n"
                )
            )

        # Load existing tracked paths to skip duplicates
        existing_paths = set(Media.objects.values_list("file", flat=True))

        # Collect candidate files
        to_import = []
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, settings.MEDIA_ROOT).replace("\\", "/")

                if rel_path in existing_paths:
                    self.stdout.write(f"  SKIP (already tracked): {rel_path}")
                    continue

                ext = os.path.splitext(filename)[1].lower()
                if ext not in IMAGE_EXTS and ext not in VIDEO_EXTS:
                    self.stdout.write(f"  SKIP (unsupported type .{ext}): {rel_path}")
                    continue

                to_import.append((abs_path, rel_path, filename))

        if not to_import:
            self.stdout.write(self.style.SUCCESS("Nothing to import."))
            return

        self.stdout.write(f"\nFound {len(to_import)} file(s) to import:\n")
        for _, rel, _ in to_import:
            self.stdout.write(f"  - {rel}")

        if not apply:
            self.stdout.write(
                self.style.WARNING(
                    f"\nDry-run complete. Run with --apply to import {len(to_import)} file(s)."
                )
            )
            return

        # Get or create the target folder
        folder, created = MediaFolder.objects.get_or_create(name=folder_name, parent=None)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created folder "{folder_name}".'))
        else:
            self.stdout.write(f'Using existing folder "{folder_name}" (id={folder.pk}).\n')

        # Import each file by registering it directly against the existing path
        imported = 0
        failed   = 0

        for abs_path, rel_path, filename in to_import:
            try:
                # Use process_upload_file for type/dimension detection
                with open(abs_path, "rb") as fh:
                    from django.core.files import File as DjangoFile
                    django_file = DjangoFile(fh, name=filename)
                    meta = process_upload_file(django_file)

                title = derive_title(filename)

                media = Media(
                    title=title,
                    folder=folder,
                    type=meta["type"],
                    size=meta["size"],
                    width=meta.get("width"),
                    height=meta.get("height"),
                    position=Media.next_position(folder),
                )
                # Point the FileField at the existing path — no file copy or re-upload
                media.file.name = rel_path
                media.save()

                self.stdout.write(
                    self.style.SUCCESS(f"  OK  {rel_path}  (id={media.pk}, type={meta['type']})")
                )
                imported += 1

            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  FAIL  {rel_path}  -- {exc}"))
                logger.exception("Failed to import %s", rel_path)
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Imported: {imported}   Failed: {failed}"
            )
        )
