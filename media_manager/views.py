import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import ensure_csrf_cookie

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
        "total_count": media_qs.count(),
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


@login_required
@requires_perm("media_manager.delete_media")
def delete_media(request, media_id):
    media = get_object_or_404(Media, pk=media_id)
    folder = media.folder

    if request.method == "POST":
        MediaService.delete(media)
        messages.success(request, "File deleted.")
        if folder:
            return redirect("media_folder", folder_id=folder.pk)
        return redirect("media_library")

    # GET — should not happen in normal flow, redirect safely
    return redirect("media_library")