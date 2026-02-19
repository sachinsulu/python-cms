from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Package
from .forms import PackageForm


@login_required
def package_list(request):
    packages = Package.objects.all().order_by('position')
    return render(request, 'package/list.html', {
        'packages': packages,
    })


@login_required
def package_create(request):
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Package created successfully!")
            return redirect('package_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = PackageForm()

    return render(request, 'package/form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def package_edit(request, slug):
    package = get_object_or_404(Package, slug=slug)

    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, "Package updated successfully!")
            return redirect('package_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = PackageForm(instance=package)

    return render(request, 'package/form.html', {
        'form': form,
        'is_edit': True,
        'package': package,
    })