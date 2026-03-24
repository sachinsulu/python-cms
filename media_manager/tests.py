# media_manager/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.cache import cache
from unittest.mock import patch

from .models import Media, MediaFolder
from .services import MediaService
from .tracking import record_media_usage, is_media_in_use
from .utils import FOLDER_TREE_CACHE_KEY, get_folder_tree

User = get_user_model()


def _fake_file(name="test.jpg", content=b"fake-image-data"):
    f = ContentFile(content, name=name)
    f.size = len(content)
    return f


class MediaServiceUploadTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass")

    @patch("media_manager.processing.Image.open")
    def test_upload_derives_title_from_filename(self, mock_open):
        mock_open.return_value.__enter__.return_value.size = (800, 600)
        f = _fake_file("my_hero_image.jpg")
        media = MediaService.upload(file=f, user=self.user)
        self.assertEqual(media.title, "My Hero Image")

    def test_upload_requires_authenticated_user(self):
        with self.assertRaises(PermissionError):
            MediaService.upload(file=_fake_file(), user=None)

    def test_upload_unauthenticated_user_raises(self):
        anon = User()           # unsaved, not authenticated
        with self.assertRaises(PermissionError):
            MediaService.upload(file=_fake_file(), user=anon)


class MediaServiceDeleteTests(TestCase):

    def setUp(self):
        self.user   = User.objects.create_user("deluser", password="pass")
        self.folder = MediaFolder.objects.create(name="Test Folder")

    def _create_media(self):
        return Media.objects.create(
            title="Test",
            file=_fake_file(),
            type=Media.TYPE_IMAGE,
            size=16,
            uploaded_by=self.user,
        )

    def test_soft_delete_marks_flag_and_preserves_db_row(self):
        media = self._create_media()
        MediaService.delete(media, soft=True, force=True)
        media.refresh_from_db()
        self.assertTrue(media.is_deleted)
        self.assertIsNotNone(media.deleted_at)

    def test_soft_deleted_media_excluded_from_active_qs(self):
        media = self._create_media()
        MediaService.delete(media, soft=True, force=True)
        self.assertFalse(Media.objects.active().filter(pk=media.pk).exists())

    def test_hard_delete_blocked_when_in_use(self):
        from articles.models import Article
        media   = self._create_media()
        article = Article.objects.create(title="Test", content="...", image=media)
        record_media_usage(article, "image", media)
        with self.assertRaises(ValueError):
            MediaService.delete(media, soft=False, force=False)

    def test_hard_delete_force_bypasses_usage_check(self):
        from articles.models import Article
        media   = self._create_media()
        article = Article.objects.create(title="Test", content="...", image=media)
        record_media_usage(article, "image", media)
        pk = media.pk
        with patch("django.db.models.fields.files.FieldFile.delete"):
            MediaService.delete(media, soft=False, force=True)
        self.assertFalse(Media.objects.filter(pk=pk).exists())

    def test_restore_clears_soft_delete_flags(self):
        media = self._create_media()
        media.soft_delete()
        media.restore()
        media.refresh_from_db()
        self.assertFalse(media.is_deleted)
        self.assertIsNone(media.deleted_at)


class MediaUsageTrackingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("trackuser", password="pass")

    def _create_media(self):
        return Media.objects.create(
            title="Track Test",
            file=_fake_file(),
            type=Media.TYPE_IMAGE,
            size=16,
        )

    def test_record_and_check_usage(self):
        from articles.models import Article
        media   = self._create_media()
        article = Article.objects.create(title="A", content="...", image=media)
        record_media_usage(article, "image", media)
        self.assertTrue(is_media_in_use(media))

    def test_usage_cleared_on_null_assignment(self):
        from articles.models import Article
        media   = self._create_media()
        article = Article.objects.create(title="A", content="...", image=media)
        record_media_usage(article, "image", media)
        record_media_usage(article, "image", None)   # unassign
        self.assertFalse(is_media_in_use(media))

    def test_record_updates_not_duplicates(self):
        from articles.models import Article
        media1  = self._create_media()
        media2  = self._create_media()
        article = Article.objects.create(title="B", content="...", image=media1)
        record_media_usage(article, "image", media1)
        record_media_usage(article, "image", media2)   # replace
        self.assertFalse(is_media_in_use(media1))
        self.assertTrue(is_media_in_use(media2))


class FolderTreeCacheTests(TestCase):

    def setUp(self):
        cache.clear()

    def test_cache_populated_on_first_call(self):
        MediaFolder.objects.create(name="Alpha")
        get_folder_tree()
        self.assertIsNotNone(cache.get(FOLDER_TREE_CACHE_KEY))

    def test_cache_busted_on_folder_create(self):
        get_folder_tree()                                    # populate
        self.assertIsNotNone(cache.get(FOLDER_TREE_CACHE_KEY))
        MediaFolder.objects.create(name="New Folder")        # triggers signal
        self.assertIsNone(cache.get(FOLDER_TREE_CACHE_KEY))

    def test_cache_busted_on_folder_delete(self):
        folder = MediaFolder.objects.create(name="Temp")
        get_folder_tree()
        self.assertIsNotNone(cache.get(FOLDER_TREE_CACHE_KEY))
        folder.delete()                                      # triggers signal
        self.assertIsNone(cache.get(FOLDER_TREE_CACHE_KEY))
