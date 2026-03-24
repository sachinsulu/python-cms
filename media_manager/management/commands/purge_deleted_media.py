# media_manager/management/commands/purge_deleted_media.py
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from media_manager.models import Media
from media_manager.services import MediaService


class Command(BaseCommand):
    help = "Permanently delete soft-deleted media older than --days (default 30)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Delete media soft-deleted more than this many days ago.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview how many records would be purged without deleting.",
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options["days"])
        qs     = Media.objects.deleted().filter(deleted_at__lt=cutoff)
        count  = qs.count()

        if options["dry_run"]:
            self.stdout.write(f"[DRY RUN] Would purge {count} media object(s).")
            return

        purged = 0
        for media in qs.iterator():
            try:
                MediaService.delete(media, soft=False, force=True)
                purged += 1
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(f"Failed to purge Media#{media.pk}: {exc}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Purged {purged} of {count} media object(s).")
        )
