import json
import logging
from urllib.parse import urlparse

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Case, When, Value, BooleanField
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.utils.text import slugify
from django_ratelimit.decorators import ratelimit

from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage
from django.contrib.auth.models import Group

User = get_user_model()
logger = logging.getLogger(__name__)

# -------------------------
# Global Constants / Helpers
# -------------------------
MODEL_MAP = {
    "article": Article,
    "user": User,
    "group": Group,
    "blog": Blog,
    "package": Package,
    "subpackage": SubPackage,
}

ACTIVE_FIELD_MAP = {
    "article": "active",
    "blog": "active",
    "package": "is_active",
    "subpackage": "is_active",
}


def redirect_back(request, default='/'):
    """Redirect to previous page or default"""
    referer = request.META.get('HTTP_REFERER', default)
    parsed = urlparse(referer)
    if parsed.netloc and parsed.netloc != request.get_host():
        return redirect(default)
    return redirect(referer)


def get_obj_name(obj):
    """Return a display name for object"""
    return getattr(obj, 'title', getattr(obj, 'username', str(obj)))


def check_user_permission(request, model_class, action="change"):
    if request.user.is_superuser:
        return True

    if model_class is User:
        return False

    app_label = model_class._meta.app_label
    model_name = model_class._meta.model_name
    perm = f"{app_label}.{action}_{model_name}"

    return request.user.has_perm(perm)


# -------------------------
# Views
# -------------------------
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@ratelimit(key='user', rate='30/m', method='POST')
@login_required
@require_POST
def toggle_status(request, model_name, pk):
    """Toggle active status of an object using ACTIVE_FIELD_MAP"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({"error": "Invalid model"}, status=400)

    if not check_user_permission(request, model_class, action="change"):
        return JsonResponse({"error": "Permission denied"}, status=403)

    active_field = ACTIVE_FIELD_MAP.get(model_name.lower())
    if not active_field:
        return JsonResponse({"error": "This model does not support status toggling"}, status=400)

    # Only fetch needed fields
    obj = get_object_or_404(model_class.objects.only('pk', active_field), pk=pk)

    current_status = getattr(obj, active_field)
    setattr(obj, active_field, not current_status)
    obj.save(update_fields=[active_field])

    return JsonResponse({
        "status": not current_status,
        "message": f'"{get_obj_name(obj)}" status changed.'
    })


@ratelimit(key='user', rate='30/m', method='POST')
@login_required
@require_POST
def delete_object(request, model_name, pk):
    """Delete a single object"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        messages.error(request, "Invalid model type.")
        return redirect_back(request)

    if not check_user_permission(request, model_class, action="delete"):
        messages.error(request, "You do not have permission to delete this item.")
        return redirect_back(request)

    obj = get_object_or_404(model_class, pk=pk)
    obj_name = get_obj_name(obj)
    obj.delete()

    messages.success(request, f'"{obj_name}" has been deleted successfully.')
    return redirect_back(request)


@ratelimit(key='user', rate='30/m', method='POST')
@login_required
@require_POST
def bulk_action(request, model_name):
    """Perform bulk actions (toggle status or delete)"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        messages.error(request, "Invalid model type.")
        return redirect_back(request)

    # Standardized ID parsing
    selected_ids = request.POST.getlist("selected_ids")
    if not selected_ids:
        raw_ids = request.POST.get("ids", "")
        selected_ids = [i.strip() for i in raw_ids.split(',') if i.strip()]

    if not selected_ids:
        messages.warning(request, "No items selected.")
        return redirect_back(request)

    action = request.POST.get("action") or ("delete" if request.POST.get("ids") else None)
    if not action:
        messages.error(request, "Invalid action.")
        return redirect_back(request)

    # Check permission based on actual action
    required_permission = "delete" if action == "delete" else "change"
    if not check_user_permission(request, model_class, action=required_permission):
        messages.error(request, "You do not have permission for this action.")
        return redirect_back(request)

    queryset = model_class.objects.filter(pk__in=selected_ids)

    if action == "toggle":
        active_field = ACTIVE_FIELD_MAP.get(model_name.lower())
        if not active_field:
            messages.error(request, "This model does not support status toggling.")
            return redirect_back(request)

        # Capture count before operation
        count = queryset.count()
        queryset.update(**{
            active_field: Case(
                When(**{active_field: True}, then=Value(False)),
                When(**{active_field: False}, then=Value(True)),
                output_field=BooleanField(),
            )
        })
        messages.success(request, f"{count} {model_name}(s) status toggled.")

    elif action == "delete":
        # Capture count before delete
        count = queryset.count()
        queryset.delete()
        messages.success(request, f"{count} {model_name}(s) deleted successfully.")

    else:
        messages.error(request, "Invalid action.")

    return redirect_back(request)


@ratelimit(key='user', rate='60/m', method='POST')
@login_required
@require_POST
def update_order(request, model_name):
    """Update position order for drag-and-drop"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({'status': 'error', 'message': 'Invalid model type'}, status=400)

    if not check_user_permission(request, model_class, action="change"):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        order = data.get('order', [])

        try:
            order = [int(obj_id) for obj_id in order]
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid ID format'}, status=400)

        # Only fetch needed fields
        objs = model_class.objects.filter(id__in=order).only('pk', 'position')
        obj_map = {obj.id: obj for obj in objs}

        updated_objs = []
        for position, obj_id in enumerate(order):
            if obj_id in obj_map:
                obj = obj_map[obj_id]
                obj.position = position
                updated_objs.append(obj)

        with transaction.atomic():
            model_class.objects.bulk_update(updated_objs, ['position'])

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        logger.error("Invalid JSON in update_order")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to update order'}, status=500)


@ratelimit(key='user', rate='30/m', method='GET')
@login_required
def ajax_check_slug(request, model_name):
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({"error": "Invalid model", "slug": "", "exists": False}, status=400)

    # Reliable field existence check
    try:
        model_class._meta.get_field('slug')
    except FieldDoesNotExist:
        return JsonResponse({
            "error": f"{model_name} does not have a slug field",
            "slug": "",
            "exists": False
        }, status=400)

    slug = request.GET.get("slug", "").strip()
    object_id = request.GET.get("object_id", "").strip()

    if not slug:
        return JsonResponse({"error": "Slug is required", "slug": "", "exists": False}, status=400)

    slug = slugify(slug)
    if not slug:
        return JsonResponse({"error": "Invalid slug format", "slug": "", "exists": False}, status=400)

    qs = model_class.objects.filter(slug=slug)
    if object_id and object_id.isdigit():
        qs = qs.exclude(pk=int(object_id))

    return JsonResponse({"slug": slug, "exists": qs.exists()})