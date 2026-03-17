from django import forms
from .models import Service
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image as PILImage


class ServiceForm(forms.ModelForm):
    remove_image = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')

    class Meta:
        model = Service
        fields = ['title', 'link', 'content', 'image', 'icon', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'link':  forms.TextInput(attrs={'placeholder': 'https://'}),
            'icon':  forms.TextInput(attrs={'placeholder': 'e.g. fa-brands fa-instagram'}),
            'image': forms.FileInput(),
            'content': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image
        if self.instance and self.instance.pk and self.instance.image:
            if image == self.instance.image:
                return image
        if not hasattr(image, 'file'):
            return image

        max_size       = getattr(settings, 'IMAGE_MAX_FILE_SIZE', 2 * 1024 * 1024)
        allowed_ext    = getattr(settings, 'IMAGE_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'webp'])
        max_dimensions = getattr(settings, 'IMAGE_MAX_DIMENSIONS', (1920, 1280))

        if image.size > max_size:
            raise ValidationError(
                f"Image too large. Max {max_size/(1024*1024):.0f}MB. "
                f"Your file is {image.size/(1024*1024):.1f}MB."
            )
        ext = image.name.split('.')[-1].lower()
        if ext not in allowed_ext:
            raise ValidationError(f"Invalid type '.{ext}'. Allowed: {', '.join(allowed_ext)}")

        try:
            img = PILImage.open(image)
            img.verify()
            image.seek(0)
        except Exception:
            raise ValidationError("Invalid image file.")

        image.seek(0)
        img = PILImage.open(image)
        w, h = img.size
        mw, mh = max_dimensions
        if w > mw or h > mh:
            raise ValidationError(f"Image too large ({w}x{h}). Max {mw}x{mh}px.")
        image.seek(0)
        return image
