from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image as PILImage
from .models import SitePreferences


class SitePreferencesForm(forms.ModelForm):
    # Hidden removal flags for each image field
    remove_icon              = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_logo              = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_fb_sharing        = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_twitter_sharing   = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_gallery_image     = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_contact_image     = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_default_image     = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_facilities_image  = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_offer_image       = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')

    class Meta:
        model  = SitePreferences
        fields = [
            'is_maintenance',
            'site_title', 'site_name', 'copyright_text',
            'icon', 'logo', 'fb_sharing', 'twitter_sharing',
            'gallery_image', 'contact_image', 'default_image',
            'facilities_image', 'offer_image',
            'google_analytics_code', 'facebook_pixel_code', 'online_booking_code',
            'robots_txt',
            'booking_type', 'hotel_result_page', 'hotel_code',
        ]
        widgets = {
            'site_title':             forms.TextInput(attrs={'placeholder': 'e.g. My Hotel | Official Site'}),
            'site_name':              forms.TextInput(attrs={'placeholder': 'e.g. My Hotel'}),
            'copyright_text':         forms.TextInput(attrs={'placeholder': 'e.g. © 2025 My Hotel. All rights reserved.'}),
            'icon':                   forms.FileInput(),
            'logo':                   forms.FileInput(),
            'fb_sharing':             forms.FileInput(),
            'twitter_sharing':        forms.FileInput(),
            'gallery_image':          forms.FileInput(),
            'contact_image':          forms.FileInput(),
            'default_image':          forms.FileInput(),
            'facilities_image':       forms.FileInput(),
            'offer_image':            forms.FileInput(),
            'google_analytics_code':  forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste full <script> tag here'}),
            'facebook_pixel_code':    forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste full <script> tag here'}),
            'online_booking_code':    forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste booking widget embed code here'}),
            'robots_txt':             forms.Textarea(attrs={'rows': 6, 'placeholder': 'User-agent: *\nAllow: /'}),
            'hotel_result_page':      forms.TextInput(attrs={'placeholder': 'e.g. /booking/results/'}),
            'hotel_code':             forms.TextInput(attrs={'placeholder': 'e.g. HTL-001'}),
        }

    def _clean_image_field(self, field_name):
        image = self.cleaned_data.get(field_name)

        if not image:
            return image

        if self.instance and self.instance.pk:
            existing = getattr(self.instance, field_name, None)
            if existing and image == existing:
                return image

        if not hasattr(image, 'file'):
            return image

        max_size        = getattr(settings, 'IMAGE_MAX_FILE_SIZE', 2 * 1024 * 1024)
        allowed_ext     = getattr(settings, 'IMAGE_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic'])
        max_dimensions  = getattr(settings, 'IMAGE_MAX_DIMENSIONS', (1920, 1280))
        allowed_mimetypes = getattr(settings, 'IMAGE_ALLOWED_MIMETYPES', [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic'
        ])

        if image.size > max_size:
            raise ValidationError(
                f"Image too large. Max {max_size // (1024 * 1024)}MB. "
                f"Your file is {image.size / (1024 * 1024):.1f}MB."
            )

        ext = image.name.split('.')[-1].lower()
        if ext not in allowed_ext:
            raise ValidationError(
                f"Invalid type '.{ext}'. Allowed: {', '.join(allowed_ext)}"
            )

        try:
            img = PILImage.open(image)
            img.verify()
            image.seek(0)
        except Exception:
            raise ValidationError("Invalid image file. The file may be corrupted.")

        img = PILImage.open(image)
        w, h = img.size
        mw, mh = max_dimensions
        if w > mw or h > mh:
            raise ValidationError(
                f"Image too large ({w}×{h}px). Max {mw}×{mh}px."
            )
        image.seek(0)

        if hasattr(image, 'content_type') and image.content_type not in allowed_mimetypes:
            raise ValidationError(
                f"Invalid format '{image.content_type}'. Allowed: JPEG, PNG, GIF, WebP, HEIC."
            )

        return image

    # One clean_ method per image field delegating to the shared helper
    def clean_icon(self):              return self._clean_image_field('icon')
    def clean_logo(self):              return self._clean_image_field('logo')
    def clean_fb_sharing(self):        return self._clean_image_field('fb_sharing')
    def clean_twitter_sharing(self):   return self._clean_image_field('twitter_sharing')
    def clean_gallery_image(self):     return self._clean_image_field('gallery_image')
    def clean_contact_image(self):     return self._clean_image_field('contact_image')
    def clean_default_image(self):     return self._clean_image_field('default_image')
    def clean_facilities_image(self):  return self._clean_image_field('facilities_image')
    def clean_offer_image(self):       return self._clean_image_field('offer_image')

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Process each image removal flag
        image_fields = [
            'icon', 'logo', 'fb_sharing', 'twitter_sharing',
            'gallery_image', 'contact_image', 'default_image',
            'facilities_image', 'offer_image',
        ]
        for field in image_fields:
            if self.cleaned_data.get(f'remove_{field}') == '1':
                setattr(instance, field, None)

        if commit:
            instance.save()
        return instance