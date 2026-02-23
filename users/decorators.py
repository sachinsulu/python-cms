from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from core.models import Module


def requires_perm(perm):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not (request.user.is_superuser or request.user.has_perm(perm)):
                messages.error(request, "You don't have permission to do that.")
                return redirect('dashboard')

            # Check if the module linked to this perm is active
            
            app_label = perm.split('.')[0] if '.' in perm else perm
            module = Module.objects.filter(permission_app=app_label).first()
            if module and not module.is_active:
                messages.error(request, "This module is currently disabled.")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator