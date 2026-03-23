import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from users.decorators import requires_perm
from .models import Media, MediaFolder
from .forms import MediaUploadForm, FolderCreateForm
from .services import MediaService
from .utils import get_folder_tree, get_breadcrumbs

logger = logging.getLogger(__name__)
MEDIA_PER_PAGE = 40


@ensure_csrf_cookie
@login_required
@requires_perm("media_manager.view_media")
def media_library(request, folder_id=None):
    """
    Main library view.
    Loads folders (one query) and media (one query + optional filter).
    """
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(MediaFolder, pk=folder_id)

    # Direct children folders for the current level
    child_folders = MediaFolder.objects.filter(
        parent=current_folder
    ).order_by("name")

    # Media in current folder only (not recursive — intentional for UX)
    media_qs = (
        Media.objects.filter(folder=current_folder)
        .select_related("folder", "uploaded_by")
        .order_by("-created_at")
    )

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        media_qs = media_qs.filter(title__icontains=q)

    # Type filter
    type_filter = request.GET.get("type", "")
    if type_filter in (Media.TYPE_IMAGE, Media.TYPE_VIDEO, Media.TYPE_FILE):
        media_qs = media_qs.filter(type=type_filter)

    paginator = Paginator(media_qs, MEDIA_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    folder_tree = get_folder_tree()
    breadcrumbs = get_breadcrumbs(current_folder)

    return render(request, "media_manager/library.html", {
        "page_obj": page_obj,
        "child_folders": child_folders,
        "folder_tree": folder_tree,
        "current_folder": current_folder,
        "breadcrumbs": breadcrumbs,
        "q": q,
        "type_filter": type_filter,
        "total_count": paginator.count,
    })


@login_required
@requires_perm("media_manager.add_media")
def upload_media(request, folder_id=None):
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(MediaFolder, pk=folder_id)

    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                MediaService.upload(
                    file=form.cleaned_data["file"],
                    folder=form.cleaned_data.get("folder") or current_folder,
                    user=request.user,
                    title=form.cleaned_data.get("title", ""),
                    alt_text=form.cleaned_data.get("alt_text", ""),
                )
                messages.success(request, "File uploaded successfully.")
                if current_folder:
                    return redirect("media_folder", folder_id=current_folder.pk)
                return redirect("media_library")
            except Exception as exc:
                logger.error("Upload failed: %s", exc)
                messages.error(request, "Upload failed. Please try again.")
        else:
            logger.warning("Upload form errors: %s", form.errors)
    else:
        form = MediaUploadForm(initial={"folder": current_folder})

    return render(request, "media_manager/upload.html", {
        "form": form,
        "current_folder": current_folder,
    })


@login_required
@requires_perm("media_manager.add_mediafolder")
def create_folder(request):
    if request.method == "POST":
        form = FolderCreateForm(request.POST)
        if form.is_valid():
            folder = form.save()
            messages.success(request, f'Folder "{folder.name}" created.')
            if folder.parent:
                return redirect("media_folder", folder_id=folder.parent.pk)
            return redirect("media_library")
    else:
        parent_id = request.GET.get("parent")
        initial = {}
        if parent_id:
            try:
                initial["parent"] = MediaFolder.objects.get(pk=parent_id)
            except MediaFolder.DoesNotExist:
                pass
        form = FolderCreateForm(initial=initial)

    return render(request, "media_manager/upload.html", {
        "form": form,
        "is_folder_form": True,
    })


@require_POST
@login_required
@requires_perm("media_manager.delete_media")
def delete_media(request, media_id):
    media = get_object_or_404(Media, pk=media_id)
    folder = media.folder

    MediaService.delete(media)
    messages.success(request, "File deleted.")
    if folder:
        return redirect("media_folder", folder_id=folder.pk)
    return redirect("media_library")


@login_required
@requires_perm("media_manager.view_media")
@ratelimit(key='user', rate='30/m', method='GET')
def media_picker_api(request):
    """
    AJAX endpoint for the picker modal.
    Returns paginated media JSON filtered by folder/type/search.
    """
    PICKER_PAGE_SIZE = 30

    qs = (
        Media.objects
        .select_related("folder")
        .order_by("-created_at")
    )

    # Filters
    folder_id = request.GET.get("folder")
    if folder_id == "root":
        qs = qs.filter(folder__isnull=True)
    elif folder_id:
        try:
            qs = qs.filter(folder_id=int(folder_id))
        except (ValueError, TypeError):
            pass

    type_filter = request.GET.get("type", "")
    if type_filter in (Media.TYPE_IMAGE, Media.TYPE_VIDEO, Media.TYPE_FILE):
        qs = qs.filter(type=type_filter)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(title__icontains=q)

    paginator = Paginator(qs, PICKER_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page", 1))

    results = []
    for m in page.object_list:
        results.append({
            "id": m.pk,
            "title": m.title,
            "url": m.file.url,
            "type": m.type,
            "size_display": m.size_display,
            "dimensions": f"{m.width}×{m.height}" if m.width else "",
            "folder": m.folder.name if m.folder else "Root",
            "is_image": m.is_image,
            "filename": m.filename,
        })

    # Folder list for sidebar (one query, flat list)
    folders = list(
        MediaFolder.objects
        .values("id", "name", "parent_id")
        .order_by("name")
    )

    return JsonResponse({
        "results": results,
        "has_next": page.has_next(),
        "has_previous": page.has_previous(),
        "page": page.number,
        "total_pages": paginator.num_pages,
        "total_count": paginator.count,
        "folders": folders,
    })