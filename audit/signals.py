import logging
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, m2m_changed
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import AuditLog
from .middleware import get_current_request
from .utils import get_client_ip, capture_state, capture_diff

logger = logging.getLogger(__name__)

def is_tracked(instance):
    """Checks if a model should be tracked based on settings whitelist."""
    if not instance:
        return False
    model_path = f"{instance._meta.app_label}.{instance._meta.object_name}"
    return model_path in getattr(settings, 'AUDIT_TRACKED_MODELS', [])

def log_action(action, instance=None, content_type=None, object_id=None, object_repr=None, model_name=None, changes=None, extra=None, request=None):
    """
    Core logging function. Can be called with an instance (for signals)
    or with manual parameters (for bulk actions).
    """
    if not request:
        request = get_current_request()
    
    # Context data
    user = request.user if request and request.user.is_authenticated else None
    ip = get_client_ip(request)
    
    # Resolve model info
    if instance:
        content_type = content_type or ContentType.objects.get_for_model(instance)
        object_id = object_id or str(instance.pk)
        object_repr = object_repr or getattr(instance, '_audit_obj_repr', str(instance))
        model_name = model_name or instance._meta.model_name
    
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr[:255] if object_repr else '',
            model_name=model_name or '',
            changes=changes or {},
            extra=extra or {},
            ip_address=ip,
            request_path=request.path if request else '',
            request_method=request.method if request else '',
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            session_key=request.session.session_key if request and hasattr(request, 'session') else ''
        )
    except Exception as e:
        logger.error(f"Failed to create AuditLog: {e}")

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not is_tracked(instance):
        return
        
    if not hasattr(instance, '_pre_save_snapshot'):
        if instance.pk:
            try:
                db_instance = sender.objects.get(pk=instance.pk)
                instance._pre_save_snapshot = capture_state(db_instance)
            except sender.DoesNotExist:
                instance._pre_save_snapshot = {}
        else:
            instance._pre_save_snapshot = {}

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if not is_tracked(instance):
        return
        
    action = AuditLog.ACTION_CREATE if created else AuditLog.ACTION_UPDATE
    
    new_state = capture_state(instance)
    old_state = getattr(instance, '_pre_save_snapshot', {})
    
    if created:
        diff = {k: {"before": None, "after": v} for k, v in new_state.items()}
    else:
        diff = capture_diff(old_state, new_state)
        
    if diff:
        log_action(action, instance=instance, changes=diff)
        
    if hasattr(instance, '_pre_save_snapshot'):
        del instance._pre_save_snapshot

@receiver(pre_delete)
def audit_pre_delete(sender, instance, **kwargs):
    if not is_tracked(instance):
        return
    instance._audit_obj_repr = str(instance)

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not is_tracked(instance):
        return
    log_action(AuditLog.ACTION_DELETE, instance=instance)

@receiver(m2m_changed)
def audit_m2m_changed(sender, instance, action, **kwargs):
    if not is_tracked(instance) or action not in ['post_add', 'post_remove']:
        return
        
    # Standardized M2M logging: capture full state after change
    # Note: 'sender' here is the through model.
    # We log it as an UPDATE on the 'instance'.
    
    new_state = capture_state(instance)
    # We might not have a reliable 'before' for M2M via signals alone 
    # but we can log that a relationship changed.
    
    log_action(AuditLog.ACTION_UPDATE, instance=instance, extra={
        "m2m_change": True,
        "m2m_action": action,
        "m2m_sender": sender._meta.model_name
    })

@receiver(user_logged_in)
def audit_user_logged_in(sender, request, user, **kwargs):
    """Logs user login event."""
    log_action(AuditLog.ACTION_LOGIN, request=request)

@receiver(user_logged_out)
def audit_user_logged_out(sender, request, user, **kwargs):
    """Logs user logout event."""
    log_action(AuditLog.ACTION_LOGOUT, request=request)
