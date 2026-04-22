import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count

from users.decorators import requires_perm
from media_manager.models import Media
from .models import Gallery, GalleryImage
from .forms import GalleryForm, GalleryImageForm, ImageAddForm
import re as _re
import requests as _requests

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
@login_required
@requires_perm('gallery.view_gallery')
def gallery_list(request):
    current_filter = request.GET.get('type', Gallery.TYPE_INNERPAGE)
    
    if current_filter not in [Gallery.TYPE_HOMEPAGE, Gallery.TYPE_INNERPAGE]:
        current_filter = Gallery.TYPE_INNERPAGE

    galleries = Gallery.objects.filter(
        type=current_filter
    ).annotate(images_count=Count('images', distinct=True)).order_by('position')

    return render(request, 'gallery/list.html', {
        'list': galleries,
        'current_filter': current_filter,
    })


@login_required
@requires_perm('gallery.add_gallery')
def gallery_create(request):
    session_filter = request.GET.get('type', Gallery.TYPE_INNERPAGE)

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
    media_qs = Media.objects.filter(pk__in=media_ids, active=True, type__in=[Media.TYPE_IMAGE, Media.TYPE_VIDEO])
    media_map = {m.pk: m for m in media_qs}

    # Existing media pks already in this gallery (avoid dupes)
    existing_pks = set(
        gallery.images.filter(image_id__in=media_ids).values_list('image_id', flat=True)
    )

    # Determine starting position
    from django.db.models import Max
    last_pos = (gallery.images.aggregate(Max('position'))['position__max'] or 0) + 1

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
            'media_type': media.type,
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


@require_POST
@login_required
@requires_perm('gallery.change_gallery')
def gallery_add_youtube(request, pk):
    """
    AJAX endpoint — accepts JSON { youtube_url: str, title: str }
    Creates a single GalleryImage row with the given YouTube URL.
    Returns JSON { image: {...} } on success or { error: str } on failure.
    """
    import json
    gallery = get_object_or_404(Gallery, pk=pk)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    youtube_url = data.get('youtube_url', '').strip()
    title = data.get('title', '').strip()

    if not youtube_url:
        return JsonResponse({'error': 'youtube_url is required'}, status=400)

    # Validate it looks like a YouTube URL
    yt_pattern = _re.compile(r'(?:v=|youtu\.be/|embed/)([\w-]{11})')
    if not yt_pattern.search(youtube_url):
        return JsonResponse({'error': 'Please enter a valid YouTube URL'}, status=400)

    # If title is empty, fetch metadata (like the PHP example)
    description = ""
    if not title:
        try:
            resp = _requests.get(youtube_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                html = resp.text
                # Get title
                title_m = _re.search(r'<title>(.*?)</title>', html, _re.IGNORECASE)
                if title_m:
                    title = title_m.group(1).replace(' - YouTube', '').strip()
                
                # Get description from meta
                desc_m = _re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, _re.IGNORECASE)
                if not desc_m:
                    desc_m = _re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', html, _re.IGNORECASE)
                if desc_m:
                    description = desc_m.group(1).strip()
        except Exception as e:
            logger.error(f"Error fetching YouTube metadata: {e}")

    from django.db.models import Max
    last_pos = (gallery.images.aggregate(Max('position'))['position__max'] or 0) + 1

    gi = GalleryImage.objects.create(
        gallery=gallery,
        image=None,
        youtube_url=youtube_url,
        title=title or 'YouTube Video',
        description=description,
        active=True,
        position=last_pos,
    )

    return JsonResponse({
        'image': {
            'id': gi.pk,
            'title': gi.title,
            'active': gi.active,
            'position': gi.position,
            'media_type': 'video',
            'is_youtube': True,
            'youtube_thumbnail_url': gi.youtube_thumbnail_url,
            'youtube_embed_url': gi.youtube_embed_url,
            'image_url': '',
            'edit_url': reverse('gallery_image_edit', args=[gallery.pk, gi.pk]),
            'delete_url': reverse('delete_object', args=['galleryimage', gi.pk]),
            'toggle_url': reverse('toggle_status', args=['galleryimage', gi.pk]),
        }
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

            if gallery.media_type == Gallery.MEDIA_TYPE_VIDEO:
                # Video gallery — persist YT URL, clear any file FK
                yt_url = request.POST.get('youtube_url', '').strip()
                gall_img.youtube_url = yt_url
                gall_img.image = None
            else:
                # Image gallery — handle file picker as before
                gall_img.youtube_url = ''
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