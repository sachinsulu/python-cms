# media_manager/ckeditor_views.py
"""
Custom CKEditor upload endpoint.

Replaces the default ckeditor_uploader view so every image uploaded via
CKEditor is registered as a Media record in the Media Manager library.

Security:
  - login_required — unauthenticated POSTs are rejected (401/redirect).
  - File type validation re-uses IMAGE_ALLOWED_EXTENSIONS from settings.
  - File size capped at MEDIA_LIBRARY_MAX_UPLOAD_SIZE (default 50 MB).

Ownership:
  - uploaded_by = request.user
  - All uploads land in the "ckeditor" folder (auto-created if missing).

Response format (CKEditor 4 spec):
  Success: {"uploaded": 1, "fileName": "...", "url": "..."}
  Failure: {"uploaded": 0, "error": {"message": "..."}}
"""
import logging
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import ALLOWED_IMAGE_EXTENSIONS, MAX_UPLOAD_SIZE
from .models import MediaFolder
from .services import MediaService

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

CKEDITOR_FOLDER_NAME = getattr(settings, "CKEDITOR_MEDIA_FOLDER", "ckeditor")

# CKEditor 4 only sends images, so restrict to images only.
ALLOWED_EXTENSIONS = set(ALLOWED_IMAGE_EXTENSIONS)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _error(message: str) -> JsonResponse:
    """CKEditor 4-compatible error response."""
    return JsonResponse({
        "uploaded": 0,
        "error": {"message": message},
    })


def _get_or_create_ckeditor_folder() -> MediaFolder:
    """
    Returns the dedicated CKEditor MediaFolder, creating it if it does not exist.
    This avoids race conditions via get_or_create.
    """
    folder, created = MediaFolder.objects.get_or_create(
        name=CKEDITOR_FOLDER_NAME,
        parent=None,
    )
    if created:
        logger.info("Created CKEditor media folder: '%s'", CKEDITOR_FOLDER_NAME)
    return folder


# ── View ──────────────────────────────────────────────────────────────────────

@csrf_exempt          # CKEditor does not send Django CSRF tokens
@login_required       # Reject unauthenticated users
@require_POST         # Only POST allowed
def ckeditor_upload(request):
    """
    Receives a file upload from CKEditor, validates it, and persists it as a
    Media record via MediaService so it appears in the Media Manager library.
    """
    upload = request.FILES.get("upload")

    if not upload:
        return _error("No file received.")

    # ── Validate file size ────────────────────────────────────────────────────
    if upload.size > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE // (1024 * 1024)
        actual_mb = upload.size / (1024 * 1024)
        return _error(
            f"File too large ({actual_mb:.1f} MB). Maximum allowed: {max_mb} MB."
        )

    # ── Validate file extension ───────────────────────────────────────────────
    ext = os.path.splitext(upload.name)[1].lstrip(".").lower()
    if ext not in ALLOWED_EXTENSIONS:
        return _error(
            f"File type '.{ext}' is not allowed. "
            f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )

    # ── Upload via MediaService ───────────────────────────────────────────────
    try:
        folder = _get_or_create_ckeditor_folder()
        media = MediaService.upload(
            file=upload,
            folder=folder,
            user=request.user,
            # title and alt_text auto-derived from filename inside MediaService
        )
    except PermissionError as exc:
        logger.warning("CKEditor upload rejected: %s", exc)
        return _error("Authentication required.")
    except Exception as exc:
        logger.exception("CKEditor upload failed for file '%s': %s", upload.name, exc)
        return _error("Upload failed. Please try again.")

    logger.info(
        "CKEditor upload: user=%s file=%s media_id=%s",
        request.user.pk,
        upload.name,
        media.pk,
    )

    return JsonResponse({
        "uploaded": 1,
        "fileName": media.filename,
        "url": media.file.url,
        # Extra context for debugging / future use
        "mediaId": media.pk,
        "folder": CKEDITOR_FOLDER_NAME,
    })


@login_required
def ckeditor_browse(request):
    """
    Renders the Media Manager library as a standalone browse view
    for CKEditor selection. Receives CKEditorFuncNum from query params.
    """
    func_num = request.GET.get("CKEditorFuncNum")
    return render(request, "media_manager/ckeditor_browse.html", {
        "CKEditorFuncNum": func_num,
    })
