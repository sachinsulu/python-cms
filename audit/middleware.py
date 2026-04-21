import contextvars
from django.conf import settings

# ContextVar to store the request object for use in signals
_audit_request_ctx = contextvars.ContextVar('audit_request', default=None)

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set the request context
        token = _audit_request_ctx.set(request)
        
        try:
            response = self.get_response(request)
        finally:
            # Clear the context to avoid leaks in async/worker environments
            _audit_request_ctx.reset(token)
            _audit_request_ctx.set(None)
            
        return response

def get_current_request():
    """Safety helper to fetch current request from context."""
    return _audit_request_ctx.get()
