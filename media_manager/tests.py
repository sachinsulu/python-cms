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
        from django.contrib.auth.models import AnonymousUser
        anon = AnonymousUser()  # is_authenticated = False
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

    def test_hard_delete_removes_db_row(self):
        media = self._create_media()
        pk = media.pk
        with patch("django.db.models.fields.files.FieldFile.delete"):
            MediaService.delete(media)
        self.assertFalse(Media.objects.filter(pk=pk).exists())

    def test_hard_delete_works_even_when_media_in_use(self):
        """Usage records should NOT block deletion — they cascade automatically."""
        from articles.models import Article
        media   = self._create_media()
        article = Article.objects.create(title="Test", content="...", image=media)
        record_media_usage(article, "image", media)
        pk = media.pk
        with patch("django.db.models.fields.files.FieldFile.delete"):
            MediaService.delete(media)  # must not raise
        self.assertFalse(Media.objects.filter(pk=pk).exists())

    def test_hard_delete_clears_usage_records(self):
        """MediaUsage rows should cascade-delete when the Media row is removed."""
        from articles.models import Article
        from .models import MediaUsage
        media   = self._create_media()
        article = Article.objects.create(title="Test", content="...", image=media)
        record_media_usage(article, "image", media)
        self.assertTrue(MediaUsage.objects.filter(media=media).exists())
        with patch("django.db.models.fields.files.FieldFile.delete"):
            MediaService.delete(media)
        self.assertFalse(MediaUsage.objects.filter(media_id=media.pk).exists())


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


class MediaActiveFilteringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("activeuser", password="pass")
        self.active_media = Media.objects.create(
            title="Active",
            file=_fake_file("active.jpg"),
            active=True
        )
        self.inactive_media = Media.objects.create(
            title="Inactive",
            file=_fake_file("inactive.jpg"),
            active=False
        )

    def test_manager_active_filter(self):
        """Media.objects.active() should only return active items."""
        active_qs = Media.objects.active()
        self.assertIn(self.active_media, active_qs)
        self.assertNotIn(self.inactive_media, active_qs)

    def test_picker_api_filters_inactive(self):
        """media_picker_api should not return inactive media."""
        from django.urls import reverse
        from django.test import Client
        import json
        
        client = Client()
        client.force_login(self.user)
        # Add perm
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(Media)
        permissions = Permission.objects.filter(content_type=content_type, codename='view_media')
        self.user.user_permissions.add(*permissions)

        response = client.get(reverse("media_picker_api"))
        data = json.loads(response.content)
        
        results = data.get("results", [])
        ids = [r["id"] for r in results]
        
        self.assertIn(self.active_media.pk, ids)
        self.assertNotIn(self.inactive_media.pk, ids)

    def test_media_fk_field_validation(self):
        """MediaFKField should raise ValidationError for inactive media."""
        from media_manager.fields import MediaFKField
        field = MediaFKField()
        
        # Active media should be fine
        cleaned = field.clean(self.active_media.pk)
        self.assertEqual(cleaned.pk, self.active_media.pk)
        
        # Inactive media should raise
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            field.clean(self.inactive_media.pk)

    def test_article_image_url_filtering(self):
        """Article.image_url should return None if the media is inactive."""
        from articles.models import Article
        article = Article.objects.create(title="Test", image=self.inactive_media)
        self.assertIsNone(article.image_url)
        
        article.image = self.active_media
        article.save()
        self.assertIsNotNone(article.image_url)
