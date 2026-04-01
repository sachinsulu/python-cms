from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from users.decorators import requires_perm
from django.contrib import messages
from .models import Package, SubPackage, SubPackageAmenity, SubPackageImage
from .forms import PackageForm, SubPackageForm, SubPackageImageForm
from features.models import Feature
from media_manager.models import Media
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Count
import json


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
    subpackages = SubPackage.objects.filter(package=package).annotate(
        images_count=Count('images', distinct=True)
    ).order_by('position')
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

# ========================
# SubPackage Image Views
# ========================

@ensure_csrf_cookie
@login_required
@requires_perm('package.change_subpackage')
def subpackage_images(request, package_slug, slug):
    package = get_object_or_404(Package, slug=package_slug)
    sub = get_object_or_404(SubPackage, slug=slug, package=package)
    images = sub.images.select_related('image').order_by('position')

    return render(request, 'package/sub_images.html', {
        'package': package,
        'sub': sub,
        'images': images,
    })


@require_POST
@login_required
@requires_perm('package.change_subpackage')
def subpackage_bulk_add_images(request, package_slug, slug):
    package = get_object_or_404(Package, slug=package_slug)
    sub = get_object_or_404(SubPackage, slug=slug, package=package)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    media_ids = data.get('ids', [])
    if not isinstance(media_ids, list) or not media_ids:
        return JsonResponse({'error': 'ids must be a non-empty list'}, status=400)

    if len(media_ids) > 100:
        return JsonResponse({'error': 'Max 100 images per request'}, status=400)

    try:
        media_ids = [int(mid) for mid in media_ids]
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid format for media IDs'}, status=400)

    media_qs = Media.objects.filter(pk__in=media_ids, active=True, type=Media.TYPE_IMAGE)
    media_map = {m.pk: m for m in media_qs}

    existing_pks = set(
        sub.images.filter(image_id__in=media_ids).values_list('image_id', flat=True)
    )

    last_pos = sub.images.count()

    added = 0
    skipped = 0
    new_images = []

    for i, mid in enumerate(media_ids):
        media = media_map.get(mid)
        if not media or mid in existing_pks:
            skipped += 1
            continue

        spi = SubPackageImage.objects.create(
            subpackage=sub,
            image=media,
            title=media.title or '',
            active=True,
            position=last_pos + added,
        )
        added += 1
        new_images.append({
            'id': spi.pk,
            'title': spi.title,
            'active': spi.active,
            'position': spi.position,
            'image_url': media.file.url if media.file else None,
            'thumbnail_url': media.thumbnail.url if media.thumbnail else (media.file.url if media.file else None),
            'edit_url': reverse('subpackage_image_edit', args=[package.slug, sub.slug, spi.pk]),
            'delete_url': reverse('delete_object', args=['subpackageimage', spi.pk]),
            'toggle_url': reverse('toggle_status', args=['subpackageimage', spi.pk]),
        })

    return JsonResponse({
        'added': added,
        'skipped': skipped,
        'images': new_images,
    })


@login_required
@requires_perm('package.change_subpackage')
def subpackage_image_edit(request, package_slug, slug, img_pk):
    package = get_object_or_404(Package, slug=package_slug)
    sub = get_object_or_404(SubPackage, slug=slug, package=package)
    image_obj = get_object_or_404(SubPackageImage, pk=img_pk, subpackage=sub)

    if request.method == 'POST':
        form = SubPackageImageForm(request.POST, instance=image_obj)
        if form.is_valid():
            spi = form.save(commit=False)
            if request.POST.get('remove_image') == '1':
                spi.image = None
            spi.save()
            messages.success(request, "Image details updated.")
            return redirect('subpackage_images', package_slug=package.slug, slug=sub.slug)
    else:
        initial = {}
        if image_obj.image_id:
            initial['image_media'] = image_obj.image_id
        form = SubPackageImageForm(instance=image_obj, initial=initial)

    return render(request, 'package/sub_image_form.html', {
        'form': form,
        'package': package,
        'sub': sub,
        'image': image_obj,
    })