from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import AuditLog
from .signals import log_action

def is_audit_authorized(user):
    """Only superusers or users with explicit audit permission."""
    return user.is_superuser or user.has_perm('audit.view_auditlog')

@login_required
@user_passes_test(is_audit_authorized)
def audit_list(request):
    """Paginated list of audit logs with filtering."""
    queryset = AuditLog.objects.all().select_related('user', 'content_type')
    
    # Search
    search_q = request.GET.get('q', '').strip()
    if search_q:
        queryset = queryset.filter(
            Q(object_repr__icontains=search_q) |
            Q(user__username__icontains=search_q) |
            Q(ip_address__icontains=search_q)
        )
        
    # Filters
    action_filter = request.GET.get('action')
    if action_filter:
        queryset = queryset.filter(action=action_filter)
        
    model_filter = request.GET.get('model')
    if model_filter:
        queryset = queryset.filter(model_name=model_filter)
        
    # Pagination
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_q': search_q,
        'action_filter': action_filter,
        'model_filter': model_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
        # Distinct model names for the filter dropdown
        'distinct_models': AuditLog.objects.values_list('model_name', flat=True).distinct().order_by('model_name'),
    }
    return render(request, 'audit/list.html', context)

@login_required
@user_passes_test(is_audit_authorized)
def audit_detail(request, pk):
    """Detailed view for a single log entry, rendering diffs."""
    log = get_object_or_404(AuditLog, pk=pk)
    
    # Process the 'changes' JSON for easier rendering
    # Schema: {"field": {"before": x, "after": y}}
    formatted_changes = []
    if isinstance(log.changes, dict):
        for field, values in log.changes.items():
            formatted_changes.append({
                'field': field,
                'before': values.get('before'),
                'after': values.get('after'),
            })
            
    context = {
        'log': log,
        'changes': formatted_changes,
    }
    return render(request, 'audit/detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def audit_clear(request):
    """Bulk delete all audit logs. Superuser only."""
    if request.method == "POST":
        count = AuditLog.objects.count()
        AuditLog.objects.all().delete()
        log_action(AuditLog.ACTION_CLEAR, extra={"count": count, "performed_by": request.user.username}, request=request)
        messages.success(request, f"Successfully cleared {count} audit log entries.")
    return redirect('audit:list')
