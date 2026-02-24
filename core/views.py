from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from functools import wraps
from .models import Module
from .forms import ModuleForm


def superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


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
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted successfully.')
        return redirect('module_list')
    return redirect('module_list')