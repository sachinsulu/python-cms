import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count
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

MAX_FILES_PER_UPLOAD = 20
MAX_TOTAL_SIZE_MB    = 200


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

    # Direct children folders annotated with non-deleted media counts
    child_folders = (
        MediaFolder.objects
        .filter(parent=current_folder)
        .annotate(media_count=Count("media", filter=models.Q(media__is_deleted=False)))
        .order_by("name")
    )

    # Active media in current folder only (not recursive — intentional for UX)
    media_qs = (
        Media.objects.active()
        .filter(folder=current_folder)
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
@ratelimit(key='user', rate='20/m', method='POST', block=True)
def upload_media(request, folder_id=None):
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(MediaFolder, pk=folder_id)

    if request.method == "POST":
        files = request.FILES.getlist("files")

        # Guard 1: file count
        if len(files) > MAX_FILES_PER_UPLOAD:
            messages.error(
                request,
                f"Max {MAX_FILES_PER_UPLOAD} files per upload. You sent {len(files)}."
            )
            return redirect(request.path)

        # Guard 2: total payload size
        total_mb = sum(f.size for f in files) / (1024 * 1024)
        if total_mb > MAX_TOTAL_SIZE_MB:
            messages.error(
                request,
                f"Total upload size {total_mb:.1f} MB exceeds {MAX_TOTAL_SIZE_MB} MB limit."
            )
            return redirect(request.path)

        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            folder   = form.cleaned_data.get("folder") or current_folder
            title    = form.cleaned_data.get("title", "")
            alt_text = form.cleaned_data.get("alt_text", "")

            errors        = []
            success_count = 0

            for file in files:
                try:
                    form.validate_single_file(file)
                    MediaService.upload(
                        file=file,
                        folder=folder,
                        user=request.user,
                        # Only apply manual title/alt to single-file uploads
                        title=title    if len(files) == 1 else "",
                        alt_text=alt_text if len(files) == 1 else "",
                    )
                    success_count += 1
                except Exception as exc:
                    errors.append(str(exc))

            if errors:
                for err in errors:
                    messages.error(request, err)
            if success_count:
                messages.success(
                    request,
                    f"{success_count} file{'s' if success_count > 1 else ''} uploaded successfully."
                )

            if success_count and not errors:
                if current_folder:
                    return redirect("media_folder", folder_id=current_folder.pk)
                return redirect("media_library")
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
    media  = get_object_or_404(Media, pk=media_id)
    folder = media.folder

    MediaService.delete(media, soft=True)   # safe default: soft delete
    messages.success(request, "File deleted.")
    if folder:
        return redirect("media_folder", folder_id=folder.pk)
    return redirect("media_library")


# ── Picker API ────────────────────────────────────────────────────────────────

def _flatten_tree(nodes: list, out: list | None = None) -> list:
    if out is None:
        out = []
    for node in nodes:
        out.append(node)
        _flatten_tree(node.get("children", []), out)
    return out


@login_required
@requires_perm("media_manager.view_media")
@ratelimit(key='user', rate='60/m', method='GET', block=True)
def media_picker_api(request):
    """
    AJAX endpoint for the picker modal.
    Returns paginated media JSON filtered by folder/type/search.
    """
    PICKER_PAGE_SIZE = 30

    qs = (
        Media.objects.active()          # honours soft delete
        .select_related("folder")
        .order_by("-created_at")
    )

    # --- Filtering ---
    folder_id   = request.GET.get("folder")
    type_filter = request.GET.get("type", "")
    q           = request.GET.get("q", "").strip()

    if folder_id == "root":
        qs = qs.filter(folder__isnull=True)
    elif folder_id:
        try:
            qs = qs.filter(folder_id=int(folder_id))
        except (ValueError, TypeError):
            pass

    if type_filter in (Media.TYPE_IMAGE, Media.TYPE_VIDEO, Media.TYPE_FILE):
        qs = qs.filter(type=type_filter)

    if q:
        qs = qs.filter(title__icontains=q)

    # --- Pagination ---
    paginator = Paginator(qs, PICKER_PAGE_SIZE)
    page      = paginator.get_page(request.GET.get("page", 1))

    results = [
        {
            "id":         m.pk,
            "title":      m.title,
            "url":        m.file.url,
            "type":       m.type,
            "size":       m.size_display,
            "dimensions": f"{m.width}×{m.height}" if m.width else "",
            "folder":     m.folder.name if m.folder else "Root",
            "is_image":   m.is_image,
            "filename":   m.filename,
            "needs_alt":  not bool(m.alt_text),
        }
        for m in page.object_list
    ]

    # Folders — use cached O(n) tree, flattened for the sidebar
    flat_folders = _flatten_tree(get_folder_tree())
    folders = [
        {
            "id":        node["folder"].pk,
            "name":      node["folder"].name,
            "parent_id": node["folder"].parent_id,
        }
        for node in flat_folders
    ][:500]

    return JsonResponse({
        "results": results,
        "pagination": {
            "page":        page.number,
            "total_pages": paginator.num_pages,
            "total":       paginator.count,
            "has_next":    page.has_next(),
            "has_prev":    page.has_previous(),
        },
        "folders": folders,
    })