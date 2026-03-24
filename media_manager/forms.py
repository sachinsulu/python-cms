# media_manager/forms.py
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

from .models import MediaFolder

MAX_UPLOAD_SIZE = getattr(settings, "MEDIA_LIBRARY_MAX_UPLOAD_SIZE", 50 * 1024 * 1024)  # 50MB default
ALLOWED_IMAGE_EXTENSIONS = getattr(
    settings, "IMAGE_ALLOWED_EXTENSIONS", ["jpg", "jpeg", "png", "gif", "webp", "heic"]
)
VIDEO_EXTENSIONS = {"mp4", "webm", "ogg", "mov"}


class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
    
    def allow_multiple_selected(self):
        return True  # Django checks this property to allow multiple

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class MediaUploadForm(forms.Form):
    """Multi-file upload form. View calls validate_single_file() per file."""
    files = MultipleFileField(
        widget=MultipleFileInput(attrs={
            "multiple": True,
            "class": "form-control",
            "id": "id_files",
            "accept": "image/*,video/mp4,video/webm,video/ogg,video/quicktime",
        }),
        required=True,
    )

    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Auto-detected if left blank"}),
    )
    alt_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Describe the image for accessibility"}),
    )
    folder = forms.ModelChoiceField(
        queryset=MediaFolder.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="— Root (no folder) —",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["folder"].queryset = MediaFolder.objects.select_related("parent").order_by("name")

    def validate_single_file(self, file):
        """
        Validate one file object. Returns cleaned file or raises ValidationError.
        Called by the view for each file in request.FILES.getlist('files').
        """
        if file.size > MAX_UPLOAD_SIZE:
            raise ValidationError(
                f"'{file.name}' is too large. Max {MAX_UPLOAD_SIZE // (1024 * 1024)}MB. "
                f"Your file is {file.size / (1024 * 1024):.1f}MB."
            )

        ext = file.name.rsplit(".", 1)[-1].lower()
        allowed_all = ALLOWED_IMAGE_EXTENSIONS + list(VIDEO_EXTENSIONS)

        if ext not in allowed_all:
            raise ValidationError(
                f"'{file.name}': file type '.{ext}' is not allowed. "
                f"Allowed: {', '.join(allowed_all)}"
            )

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