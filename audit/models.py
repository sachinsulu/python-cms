from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class AuditLog(models.Model):
    # Constants for actions
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_BULK_DELETE = 'BULK_DELETE'
    ACTION_BULK_TOGGLE = 'BULK_TOGGLE'
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_CLEAR = 'CLEAR'
    
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Create'),
        (ACTION_UPDATE, 'Update'),
        (ACTION_DELETE, 'Delete'),
        (ACTION_BULK_DELETE, 'Bulk Delete'),
        (ACTION_BULK_TOGGLE, 'Bulk Toggle'),
        (ACTION_LOGIN, 'Login'),
        (ACTION_LOGOUT, 'Logout'),
        (ACTION_CLEAR, 'Clear Logs'),
    ]

    # Content identification (Generic Relations)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Human-readable info
    object_repr = models.CharField(max_length=255, blank=True, help_text="Cached string representation of the object.")
    model_name = models.CharField(max_length=100, db_index=True, blank=True)
    
    # Forensic context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_path = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Action and Payload
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    changes = models.JSONField(default=dict, help_text='Schema: {"field": {"before": x, "after": y}}')
    extra = models.JSONField(default=dict, blank=True, help_text="Module-specific metadata.")
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id'], name='audit_obj_idx'),
            models.Index(fields=['user', 'timestamp'], name='audit_user_time_idx'),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.action} on {self.model_name}:{self.object_id} by {self.user or 'System'}"

    def save(self, *args, **kwargs):
        """Standard AuditLog records are immutable. Only allow creation."""
        if self.pk:
            raise PermissionError("AuditLog records are immutable.")
        super().save(*args, **kwargs)
