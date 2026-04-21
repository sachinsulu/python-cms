from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog
from .utils import capture_state, capture_diff
from .signals import log_action
from articles.models import Article

User = get_user_model()

class AuditLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.login(username='admin', password='password')

    def test_capture_diff_redaction(self):
        """Verify that sensitive fields are redacted in diffs."""
        old = {"password": "old_pass", "title": "Old Title"}
        new = {"password": "new_pass", "title": "New Title"}
        diff = capture_diff(old, new)
        
        self.assertEqual(diff['password']['before'], '[REDACTED]')
        self.assertEqual(diff['password']['after'], '[REDACTED]')
        self.assertEqual(diff['title']['before'], 'Old Title')
        self.assertEqual(diff['title']['after'], 'New Title')

    def test_audit_log_immutability(self):
        """Verify that AuditLog records cannot be updated."""
        log = AuditLog.objects.create(action='CREATE', model_name='test')
        log.object_repr = "Changed"
        with self.assertRaises(PermissionError):
            log.save()

    def test_article_lifecycle_logging(self):
        """Verify that creating and updating an Article (tracked) creates logs."""
        # Create
        article = Article.objects.create(title="Test Article", slug="test-article", active=True)
        
        log_create = AuditLog.objects.filter(action='CREATE', object_id=str(article.pk)).first()
        self.assertIsNotNone(log_create)
        self.assertEqual(log_create.changes['title']['after'], 'Test Article')
        
        # Update
        article.title = "Updated Title"
        article.save()
        
        log_update = AuditLog.objects.filter(action='UPDATE', object_id=str(article.pk)).first()
        self.assertIsNotNone(log_update)
        self.assertEqual(log_update.changes['title']['before'], 'Test Article')
        self.assertEqual(log_update.changes['title']['after'], 'Updated Title')
        
        # Delete
        obj_repr = str(article)
        article_pk = str(article.pk)
        article.delete()
        
        log_delete = AuditLog.objects.filter(action='DELETE', object_id=article_pk).first()
        self.assertIsNotNone(log_delete)
        self.assertEqual(log_delete.object_repr, obj_repr)

    def test_bulk_action_logging(self):
        """Verify that bulk actions in cms/views.py are logged."""
        a1 = Article.objects.create(title="A1", slug="a1")
        a2 = Article.objects.create(title="A2", slug="a2")
        
        # Test Bulk Delete
        response = self.client.post(f'/apanel/bulk/article/', {
            'selected_ids': [a1.pk, a2.pk],
            'action': 'delete'
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        log_bulk = AuditLog.objects.filter(action='BULK_DELETE').first()
        self.assertIsNotNone(log_bulk)
        self.assertEqual(log_bulk.extra['count'], 2)
        self.assertIn(str(a1.pk), log_bulk.extra['ids'])
