import re
import json
from django.forms.models import model_to_dict
from django.conf import settings
from django.utils.encoding import force_str

def get_client_ip(request):
    """
    Returns the client IP address, accounting for reverse proxies.
    Matches Railway/Vercel standard proxy headers.
    """
    if not request:
        return None
        
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Get the first IP in the list
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def capture_state(instance):
    """
    Captures a serializable snapshot of the model instance state.
    Hybrid approach: model_to_dict for relations + __dict__ for internal/non-editable fields.
    """
    if not instance:
        return {}

    # 1. model_to_dict captures most fields + FK/M2M correctly
    data = model_to_dict(instance)
    
    # 2. Add non-editable fields (created_at, position, etc.) from __dict__
    exclude_prefixes = ('_', )
    for k, v in instance.__dict__.items():
        if not k.startswith(exclude_prefixes) and k not in data:
            data[k] = v
            
    # Normalize values for JSON storage
    return normalize_dict(data)

def normalize_dict(data):
    """Recursively converts complex objects to JSON-safe primitives."""
    if isinstance(data, dict):
        return {k: normalize_dict(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [normalize_dict(i) for i in data]
    if hasattr(data, 'pk'):
        return data.pk
    # Handle dates, decimals, etc via force_str if not primitive
    if isinstance(data, (str, int, float, bool, type(None))):
        return data
    return force_str(data)

def capture_diff(old_state, new_state):
    """
    Generates a structured diff between two states.
    Schema: {"field": {"before": x, "after": y}}
    """
    diff = {}
    all_keys = set(old_state.keys()) | set(new_state.keys())
    
    # Settings
    max_len = getattr(settings, 'AUDIT_MAX_FIELD_LENGTH', 1000)
    redact_patterns = getattr(settings, 'AUDIT_REDACT_PATTERNS', [])

    for key in all_keys:
        before = old_state.get(key)
        after = new_state.get(key)
        
        if before != after:
            # Apply Redaction
            if any(re.match(pattern, key, re.IGNORECASE) for pattern in redact_patterns):
                before = "[REDACTED]" if before is not None else None
                after = "[REDACTED]" if after is not None else None
            else:
                # Apply Truncation
                before = truncate_value(before, max_len)
                after = truncate_value(after, max_len)
                
            diff[key] = {
                "before": before,
                "after": after
            }
            
    return diff

def truncate_value(value, max_len):
    """Truncates string values and appends a hash-hint if too long."""
    if not isinstance(value, str) or len(value) <= max_len:
        return value
        
    import hashlib
    hint = hashlib.md5(value.encode()).hexdigest()[:8]
    return f"{value[:max_len]}... [TRUNCATED:{hint}]"
