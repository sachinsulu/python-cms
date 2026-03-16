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
    """
    Persist amenity selections with positions.
    ordered_ids  — feature PKs in drag-sorted order (from hidden input).
    selected_ids — feature PKs that are checked (from checkbox POST).
    Only features that are both checked AND in the allowed queryset are saved.
    Position follows ordered_ids; unchecked features are removed.
    """
    # Build a position map from the drag order; fall back to enumeration
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

    # Sort before bulk_create so positions are clean
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
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Package created successfully!")
            return redirect('package_list')
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
        form = SubPackageForm(request.POST, request.FILES, feature_group=feature_group)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.package = package
            sub.save()

            selected_ids = request.POST.getlist('amenities')
            ordered_ids = [
                pk for pk in request.POST.get('amenity_order', '').split(',') if pk.strip()
            ]
            if not ordered_ids:
                ordered_ids = selected_ids

            _save_amenities(sub, selected_ids, ordered_ids)

            messages.success(request, f'"{sub.title}" created successfully!')
            return redirect('subpackage_list', package_slug=package.slug)
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
        form = SubPackageForm(request.POST, request.FILES, instance=sub, feature_group=feature_group)
        if form.is_valid():
            form.save()

            selected_ids = request.POST.getlist('amenities')
            ordered_ids = [
                pk for pk in request.POST.get('amenity_order', '').split(',') if pk.strip()
            ]
            if not ordered_ids:
                ordered_ids = selected_ids

            _save_amenities(sub, selected_ids, ordered_ids)

            messages.success(request, f'"{sub.title}" updated successfully!')
            return redirect('subpackage_list', package_slug=package.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SubPackageForm(instance=sub, feature_group=feature_group)

    return render(request, 'package/sub_form.html', {
        'form': form,
        'package': package,
        'sub': sub,
        'is_edit': True,
        # Pass sorted existing amenities so JS can build the initial drag order
        'existing_amenity_ids': list(
            sub.amenity_links.order_by('position').values_list('feature_id', flat=True)
        ),
    })