from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

from .models import Media, MediaFolder

MAX_UPLOAD_SIZE = getattr(settings, "MEDIA_LIBRARY_MAX_UPLOAD_SIZE", 50 * 1024 * 1024)  # 50MB default
ALLOWED_IMAGE_EXTENSIONS = getattr(
    settings, "IMAGE_ALLOWED_EXTENSIONS", ["jpg", "jpeg", "png", "gif", "webp", "heic"]
)
VIDEO_EXTENSIONS = {"mp4", "webm", "ogg", "mov"}


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ["file", "title", "alt_text", "folder"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Auto-detected if left blank"}),
            "alt_text": forms.TextInput(attrs={"placeholder": "Describe the image for accessibility"}),
            "folder": forms.Select(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["folder"].queryset = MediaFolder.objects.select_related("parent").order_by("name")
        self.fields["folder"].empty_label = "— Root (no folder) —"
        self.fields["folder"].required = False

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file or not hasattr(file, "name"):
            return file

        # File size guard
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError(
                f"File too large. Max {MAX_UPLOAD_SIZE // (1024 * 1024)}MB. "
                f"Your file is {file.size / (1024 * 1024):.1f}MB."
            )

        ext = file.name.rsplit(".", 1)[-1].lower()
        allowed_all = ALLOWED_IMAGE_EXTENSIONS + list(VIDEO_EXTENSIONS)

        if ext not in allowed_all:
            raise ValidationError(
                f"File type '.{ext}' is not allowed. "
                f"Allowed: {', '.join(allowed_all)}"
            )

        # Deep image validation (PIL)
        if ext in ALLOWED_IMAGE_EXTENSIONS:
            try:
                file.seek(0)
                with Image.open(file) as img:
                    img.verify()
                file.seek(0)
            except (IOError, SyntaxError, UnidentifiedImageError):
                raise ValidationError(
                    "This file does not appear to be a valid image."
                )

        file.seek(0)
        return file


class FolderCreateForm(forms.ModelForm):
    class Meta:
        model = MediaFolder
        fields = ["name", "parent"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Folder name"}),
            "parent": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = (
            MediaFolder.objects.select_related("parent").order_by("name")
        )
        self.fields["parent"].empty_label = "— Root (no parent) —"
        self.fields["parent"].required = False

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 1:
            raise ValidationError("Folder name cannot be empty.")
        return name