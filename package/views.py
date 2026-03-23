from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from users.decorators import requires_perm
from django.contrib import messages
from .models import Package, SubPackage, SubPackageAmenity
from .forms import PackageForm, SubPackageForm
from features.models import Feature


def _save_amenities(sub, selected_ids, ordered_ids):
    position_map = {int(pk): idx for idx, pk in enumerate(ordered_ids)}
    sub.amenity_links.all().delete()
    links = []
    for pk in selected_ids:
        pk = int(pk)
        links.append(SubPackageAmenity(
            subpackage=sub,
            feature_id=pk,
            position=position_map.get(pk, 9999),
        ))
    links.sort(key=lambda x: x.position)
    for idx, link in enumerate(links):
        link.position = idx
    SubPackageAmenity.objects.bulk_create(links)


# ========================
# Package Views
# ========================
@login_required
@requires_perm('package.view_package')
def package_list(request):
    packages = Package.objects.all().order_by('position')
    return render(request, 'package/list.html', {'packages': packages})


@login_required
@requires_perm('package.add_package')
def package_create(request):
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            package = form.save(commit=False)
            if request.POST.get('remove_image') == '1':
                package.image = None
            package.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Package saved! You can create a new one now.")
                return redirect('package_create')
            elif action == 'save_and_quit':
                return redirect('package_list')
            else:
                messages.success(request, "Package saved!")
                return redirect('package_edit', slug=package.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = PackageForm()
    return render(request, 'package/form.html', {'form': form, 'is_edit': False})


@login_required
@requires_perm('package.change_package')
def package_edit(request, slug):
    package = get_object_or_404(Package, slug=slug)
    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)
        if form.is_valid():
            pkg = form.save(commit=False)
            if request.POST.get('remove_image') == '1':
                pkg.image = None
            pkg.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('package_create')
            elif action == 'save_and_quit':
                return redirect('package_list')
            else:
                messages.success(request, "Package updated successfully!")
                return redirect('package_edit', slug=pkg.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        initial = {}
        if package.image_id:
            initial['image_media'] = package.image_id
        form = PackageForm(instance=package, initial=initial)
    return render(request, 'package/form.html', {
        'form': form,
        'is_edit': True,
        'package': package,
    })


# ========================
# SubPackage Views
# ========================
@login_required
@requires_perm('package.view_subpackage')
def subpackage_list(request, package_slug):
    package = get_object_or_404(Package, slug=package_slug)
    subpackages = SubPackage.objects.filter(package=package).order_by('position')
    return render(request, 'package/sub_list.html', {
        'package': package,
        'subpackages': subpackages,
    })


@login_required
@requires_perm('package.add_subpackage')
def subpackage_create(request, package_slug):
    package = get_object_or_404(Package, slug=package_slug)
    feature_group = package.feature_group

    if request.method == 'POST':
        form = SubPackageForm(request.POST, feature_group=feature_group)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.package = package
            if request.POST.get('remove_image') == '1':
                sub.image = None
            sub.save()

            selected_ids = request.POST.getlist('amenities')
            ordered_ids = [
                pk for pk in request.POST.get('amenity_order', '').split(',') if pk.strip()
            ]
            if not ordered_ids:
                ordered_ids = selected_ids
            _save_amenities(sub, selected_ids, ordered_ids)

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Sub-package saved! You can create a new one now.")
                return redirect('subpackage_create', package_slug=package.slug)
            elif action == 'save_and_quit':
                return redirect('subpackage_list', package_slug=package.slug)
            else:
                messages.success(request, "Sub-package saved!")
                return redirect('subpackage_edit', package_slug=package.slug, slug=sub.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SubPackageForm(feature_group=feature_group)

    return render(request, 'package/sub_form.html', {
        'form': form,
        'package': package,
        'is_edit': False,
    })


@login_required
@requires_perm('package.change_subpackage')
def subpackage_edit(request, package_slug, slug):
    package = get_object_or_404(Package, slug=package_slug)
    sub = get_object_or_404(SubPackage, slug=slug, package=package)
    feature_group = package.feature_group

    if request.method == 'POST':
        form = SubPackageForm(request.POST, instance=sub, feature_group=feature_group)
        if form.is_valid():
            obj = form.save(commit=False)
            if request.POST.get('remove_image') == '1':
                obj.image = None
            obj.save()

            selected_ids = request.POST.getlist('amenities')
            ordered_ids = [
                pk for pk in request.POST.get('amenity_order', '').split(',') if pk.strip()
            ]
            if not ordered_ids:
                ordered_ids = selected_ids
            _save_amenities(sub, selected_ids, ordered_ids)

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('subpackage_create', package_slug=package.slug)
            elif action == 'save_and_quit':
                return redirect('subpackage_list', package_slug=package.slug)
            else:
                messages.success(request, "Sub-package updated successfully!")
                return redirect('subpackage_edit', package_slug=package.slug, slug=obj.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        initial = {}
        if sub.image_id:
            initial['image_media'] = sub.image_id
        form = SubPackageForm(instance=sub, feature_group=feature_group, initial=initial)

    return render(request, 'package/sub_form.html', {
        'form': form,
        'package': package,
        'sub': sub,
        'is_edit': True,
        'existing_amenity_ids': list(
            sub.amenity_links.order_by('position').values_list('feature_id', flat=True)
        ),
    })