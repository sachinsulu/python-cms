from .models import Module

def sidebar_menu(request):
    if not request.user.is_authenticated:
        return {}

    items = Module.objects.filter(is_active=True)
    visible = []

    for item in items:
        if request.user.is_superuser:
            visible.append(item)
        elif item.superuser_only:
            continue
        elif item.permission_app and request.user.has_module_perms(item.permission_app):
            visible.append(item)

    return {'sidebar_menu': visible}