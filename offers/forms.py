from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image as PILImage

from .models import Offer


class OfferForm(forms.ModelForm):
    remove_image = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )

    class Meta:
        model = Offer
        fields = [
            'title', 'start_date', 'end_date', 'image',
            'discount_type',
            'fixed_discount', 'fixed_rate', 'fixed_people',
            'link', 'content', 'active',
        ]
        widgets = {
            'title':          forms.TextInput(attrs={'placeholder': 'Offer title'}),
            'start_date':     forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date':       forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'image':          forms.FileInput(),
            'discount_type':  forms.Select(attrs={'id': 'id_discount_type'}),
            'fixed_discount': forms.NumberInput(attrs={'placeholder': 'Discount amount', 'step': '0.01'}),
            'fixed_rate':     forms.NumberInput(attrs={'placeholder': 'Rate', 'step': '0.01'}),
            'fixed_people':   forms.NumberInput(attrs={'placeholder': 'No. of people'}),
            'link':           forms.TextInput(attrs={'placeholder': 'https://example.com or /page/'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end   = cleaned.get('end_date')
        if start and end and end < start:
            raise ValidationError('End date cannot be before start date.')
        return cleaned

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image
        if self.instance and self.instance.pk and self.instance.image:
            if image == self.instance.image:
                return image
        if not hasattr(image, 'file'):
            return image

        max_size    = getattr(settings, 'IMAGE_MAX_FILE_SIZE', 2 * 1024 * 1024)
        allowed_ext = getattr(settings, 'IMAGE_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'webp'])
        max_dim     = getattr(settings, 'IMAGE_MAX_DIMENSIONS', (1920, 1280))

        if image.size > max_size:
            raise ValidationError(
                f"Image too large. Max {max_size//(1024*1024)}MB. "
                f"Your file is {image.size/(1024*1024):.1f}MB."
            )
        ext = image.name.rsplit('.', 1)[-1].lower()
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
        mw, mh = max_dim
        if w > mw or h > mh:
            raise ValidationError(f"Image too large ({w}×{h}). Max {mw}×{mh}px.")
        image.seek(0)
        return image