from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Package, SubPackage
from .forms import PackageForm, SubPackageForm


# ========================
# Package Views
# ========================
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


# ========================
# SubPackage Views
# ========================
@login_required
def subpackage_list(request, package_slug):
    package = get_object_or_404(Package, slug=package_slug)
    subpackages = SubPackage.objects.filter(package=package).order_by('position')

    return render(request, 'package/sub_list.html', {
        'package': package,
        'subpackages': subpackages,
    })


@login_required
def subpackage_create(request, package_slug):
    package = get_object_or_404(Package, slug=package_slug)

    if request.method == 'POST':
        form = SubPackageForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.package = package
            sub.save()
            messages.success(request, f'"{sub.title}" created successfully!')
            return redirect('subpackage_list', package_slug=package.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SubPackageForm()

    return render(request, 'package/sub_form.html', {
        'form': form,
        'package': package,
        'is_edit': False,
    })


@login_required
def subpackage_edit(request, package_slug, slug):
    package = get_object_or_404(Package, slug=package_slug)
    sub = get_object_or_404(SubPackage, slug=slug, package=package)

    if request.method == 'POST':
        form = SubPackageForm(request.POST, request.FILES, instance=sub)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{sub.title}" updated successfully!')
            return redirect('subpackage_list', package_slug=package.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SubPackageForm(instance=sub)

    return render(request, 'package/sub_form.html', {
        'form': form,
        'package': package,
        'sub': sub,
        'is_edit': True,
    })