from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from functools import wraps
from .models import Module, PageMeta
from .forms import ModuleForm, PageMetaForm


def superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Existing Module views — unchanged ──────────────────────────

@superuser_required
def module_list(request):
    items = Module.objects.all()
    return render(request, 'core/module_list.html', {'items': items})


@superuser_required
def module_create(request):
    form = ModuleForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Module created successfully.')
        return redirect('module_list')
    return render(request, 'core/module_form.html', {'form': form})


@superuser_required
def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    form = ModuleForm(request.POST or None, instance=module)
    if form.is_valid():
        form.save()
        messages.success(request, 'Module updated successfully.')
        return redirect('module_list')
    return render(request, 'core/module_form.html', {'form': form})


@superuser_required
@require_POST
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    module.delete()
    messages.success(request, 'Module deleted successfully.')
    return redirect('module_list')


# ── New PageMeta view — one view handles create + update ───────

@login_required
@require_POST
def save_page_meta(request, url_name):
    """
    Called via POST from any list page's collapsible meta form.
    url_name identifies which Module this meta belongs to.
    Redirects back to the same list page after saving.
    """
    module = get_object_or_404(Module, url_name=url_name)

    # Get existing PageMeta or prepare a new one
    try:
        instance = module.page_meta
    except PageMeta.DoesNotExist:
        instance = None

    form = PageMetaForm(request.POST, instance=instance)

    if form.is_valid():
        page_meta = form.save(commit=False)
        page_meta.module = module
        page_meta.save()
        messages.success(request, 'Page meta saved successfully.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')

    # Redirect back to the list page this was submitted from
    return redirect(url_name)