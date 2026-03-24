# media_manager/processing.py
"""
File-type detection and metadata extraction for uploaded media.
Called ONCE at upload time from MediaService.upload() — never from save().
"""

import os
import logging

from PIL import Image, UnidentifiedImageError
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {"mp4", "webm", "ogg", "mov", "avi", "mkv"}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "heic"}


def process_upload_file(file: UploadedFile) -> dict:
    """
    Determines type, dimensions, and size for an uploaded file.
    Returns a dict of fields to set on the Media instance.
    """
    result = {
        "size": file.size,
        "type": "file",
        "width": None,
        "height": None,
    }

    ext = os.path.splitext(file.name)[1].lstrip(".").lower()

    if ext in VIDEO_EXTENSIONS:
        result["type"] = "video"
        return result

    if ext in IMAGE_EXTENSIONS:
        try:
            file.seek(0)
            with Image.open(file) as img:
                result["width"], result["height"] = img.size
            result["type"] = "image"
        except (IOError, SyntaxError, UnidentifiedImageError):
            logger.warning(
                "File %s failed image validation, stored as generic file.",
                file.name,
            )
            result["type"] = "file"
        finally:
            file.seek(0)

    return result


def derive_title(filename: str) -> str:
    """Human-readable title derived from a raw filename."""
    return (
        os.path.splitext(os.path.basename(filename))[0]
        .replace("_", " ")
        .replace("-", " ")
        .title()
    )
