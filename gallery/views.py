import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import JsonResponse

from users.decorators import requires_perm
from media_manager.models import Media
from .models import Gallery, GalleryImage
from .forms import GalleryForm, GalleryImageForm, ImageAddForm

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
@login_required
@requires_perm('gallery.view_gallery')
def gallery_list(request):
    type_param = request.GET.get('type')

    if type_param is not None:
        request.session['gallery_type_filter'] = type_param
        return redirect('gallery_list')

    current_filter = request.session.get('gallery_type_filter', Gallery.TYPE_INNERPAGE)
    
    if current_filter not in [Gallery.TYPE_HOMEPAGE, Gallery.TYPE_INNERPAGE]:
        current_filter = Gallery.TYPE_INNERPAGE

    galleries = Gallery.objects.filter(
        type=current_filter
    ).order_by('position')

    return render(request, 'gallery/list.html', {
        'list': galleries,
        'current_filter': current_filter,
    })


@login_required
@requires_perm('gallery.add_gallery')
def gallery_create(request):
    session_filter = request.session.get('gallery_type_filter', Gallery.TYPE_INNERPAGE)

    if request.method == 'POST':
        form = GalleryForm(request.POST)
        if form.is_valid():
            gallery = form.save(commit=False)
            gallery.type = session_filter
            gallery.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Gallery saved! You can create a new one now.")
                return redirect('gallery_create')
            elif action == 'save_and_quit':
                return redirect('gallery_list')
            else:
                messages.success(request, "Gallery saved!")
                return redirect(reverse('gallery_edit', args=[gallery.pk]))
        else:
            logger.warning("Gallery create form errors: %s", form.errors)
    else:
        form = GalleryForm()

    return render(request, 'gallery/form.html', {
        'form': form,
        'current_filter': session_filter,
    })


@login_required
@requires_perm('gallery.change_gallery')
def gallery_edit(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    current_filter = gallery.type

    if request.method == 'POST':
        form = GalleryForm(request.POST, instance=gallery)
        if form.is_valid():
            gallery = form.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('gallery_create')
            elif action == 'save_and_quit':
                return redirect('gallery_list')
            else:
                messages.success(request, "Gallery saved!")
                return redirect(reverse('gallery_edit', args=[gallery.pk]))
        else:
            logger.warning("Gallery edit form errors: %s", form.errors)
    else:
        form = GalleryForm(instance=gallery)

    return render(request, 'gallery/form.html', {
        'form': form,
        'is_edit': True,
        'gallery': gallery,
        'current_filter': current_filter,
    })


@ensure_csrf_cookie
@login_required
@requires_perm('gallery.change_gallery')
def gallery_images(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    images = gallery.images.select_related('image').order_by('position')

    return render(request, 'gallery/images.html', {
        'gallery': gallery,
        'images': images,
    })


@require_POST
@login_required
@requires_perm('gallery.change_gallery')
def gallery_bulk_add_images(request, pk):
    """
    AJAX endpoint — accepts JSON { ids: [media_pk, ...] }
    Creates GalleryImage rows for each Media pk, skipping duplicates.
    Returns JSON { added: int, skipped: int, images: [...] }
    """
    import json
    gallery = get_object_or_404(Gallery, pk=pk)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    media_ids = data.get('ids', [])
    if not isinstance(media_ids, list) or not media_ids:
        return JsonResponse({'error': 'ids must be a non-empty list'}, status=400)

    if len(media_ids) > 100:
        return JsonResponse({'error': 'Max 100 images per request'}, status=400)

    # Convert media IDs to integers as JSON might pass them as strings
    try:
        media_ids = [int(mid) for mid in media_ids]
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid format for media IDs'}, status=400)

    # Fetch valid, active media objects
    media_qs = Media.objects.filter(pk__in=media_ids, active=True, type=Media.TYPE_IMAGE)
    media_map = {m.pk: m for m in media_qs}

    # Existing media pks already in this gallery (avoid dupes)
    existing_pks = set(
        gallery.images.filter(image_id__in=media_ids).values_list('image_id', flat=True)
    )

    # Determine starting position
    last_pos = gallery.images.count()

    added = 0
    skipped = 0
    new_images = []

    for i, mid in enumerate(media_ids):
        media = media_map.get(mid)
        if not media:
            skipped += 1
            continue
        if mid in existing_pks:
            skipped += 1
            continue

        gi = GalleryImage.objects.create(
            gallery=gallery,
            image=media,
            title=media.title or '',
            active=True,
            position=last_pos + added,
        )
        added += 1
        new_images.append({
            'id': gi.pk,
            'title': gi.title,
            'active': gi.active,
            'position': gi.position,
            'image_url': media.file.url if media.file else None,
            'thumbnail_url': media.thumbnail.url if media.thumbnail else (media.file.url if media.file else None),
            'edit_url': reverse('gallery_image_edit', args=[gallery.pk, gi.pk]),
            'delete_url': reverse('delete_object', args=['galleryimage', gi.pk]),
            'toggle_url': reverse('toggle_status', args=['galleryimage', gi.pk]),
        })

    return JsonResponse({
        'added': added,
        'skipped': skipped,
        'images': new_images,
    })


@login_required
@requires_perm('gallery.change_galleryimage')
def gallery_image_edit(request, pk, img_pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    image_obj = get_object_or_404(GalleryImage, pk=img_pk, gallery=gallery)

    if request.method == 'POST':
        form = GalleryImageForm(request.POST, instance=image_obj)
        if form.is_valid():
            gall_img = form.save(commit=False)
            
            if request.POST.get('remove_image') == '1':
                gall_img.image = None
                
            gall_img.save()
            messages.success(request, "Image details updated.")
            return redirect('gallery_images', pk=gallery.pk)
    else:
        initial = {}
        if image_obj.image_id:
            initial['image_media'] = image_obj.image_id
        form = GalleryImageForm(instance=image_obj, initial=initial)

    return render(request, 'gallery/image_form.html', {
        'form': form,
        'gallery': gallery,
        'image': image_obj,
    })