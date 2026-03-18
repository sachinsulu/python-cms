from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image as PILImage

from .models import Popup

# 50MB limit for videos
VIDEO_MAX_SIZE = 50 * 1024 * 1024
VIDEO_ALLOWED_EXT = ['mp4', 'webm', 'ogg', 'mov']


class PopupForm(forms.ModelForm):
    remove_file = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')

    class Meta:
        model = Popup
        fields = ['title', 'start_date', 'end_date', 'type', 'file', 'link', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Popup title',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_type',
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
            }),
            'link': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com or /page/',
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'title': 'Title',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'type': 'Type',
            'file': 'Upload File',
            'link': 'Link (optional)',
            'status': 'Status',
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end   = cleaned.get('end_date')
        if start and end and end < start:
            raise ValidationError("End date cannot be before start date.")
        return cleaned

    def clean_file(self):
        file        = self.cleaned_data.get('file')
        popup_type  = self.cleaned_data.get('type') or self.data.get('type')

        if not file:
            return file

        # Skip re-validation if the file object hasn't changed (edit mode)
        if self.instance and self.instance.pk and self.instance.file:
            if file == self.instance.file:
                return file

        if not hasattr(file, 'file'):
            return file

        ext = file.name.rsplit('.', 1)[-1].lower()

        if popup_type == Popup.TYPE_IMAGE:
            max_size    = getattr(settings, 'IMAGE_MAX_FILE_SIZE', 2 * 1024 * 1024)
            allowed_ext = getattr(settings, 'IMAGE_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'webp'])
            max_dim     = getattr(settings, 'IMAGE_MAX_DIMENSIONS', (1920, 1280))

            if file.size > max_size:
                raise ValidationError(
                    f"Image too large. Max {max_size // (1024*1024)}MB. "
                    f"Your file is {file.size / (1024*1024):.1f}MB."
                )
            if ext not in allowed_ext:
                raise ValidationError(f"Invalid type '.{ext}'. Allowed: {', '.join(allowed_ext)}")

            try:
                img = PILImage.open(file)
                img.verify()
                file.seek(0)
            except Exception:
                raise ValidationError("Invalid image file.")

            file.seek(0)
            img = PILImage.open(file)
            w, h = img.size
            mw, mh = max_dim
            if w > mw or h > mh:
                raise ValidationError(f"Image too large ({w}×{h}). Max {mw}×{mh}px.")
            file.seek(0)

        elif popup_type == Popup.TYPE_VIDEO:
            if file.size > VIDEO_MAX_SIZE:
                raise ValidationError(
                    f"Video too large. Max {VIDEO_MAX_SIZE // (1024*1024)}MB. "
                    f"Your file is {file.size / (1024*1024):.1f}MB."
                )
            if ext not in VIDEO_ALLOWED_EXT:
                raise ValidationError(f"Invalid type '.{ext}'. Allowed: {', '.join(VIDEO_ALLOWED_EXT)}")

        return file
