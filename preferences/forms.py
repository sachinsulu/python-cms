from django import forms
from django.core.exceptions import ValidationError
from .models import SitePreferences

# All image fields handled via picker — no PIL validation needed here.
# PIL validation happens inside MediaService.upload() during library upload.

IMAGE_FIELDS = [
    'icon', 'logo', 'fb_sharing', 'twitter_sharing',
    'gallery_image', 'contact_image', 'default_image',
    'facilities_image', 'offer_image',
]


class MediaFKField(forms.IntegerField):
    """
    Hidden integer field that receives a Media.pk from the JS picker.

    Behaviour:
    - If empty/None  → returns None (field is not required)
    - If pk provided → validates existence, returns Media instance
    - If pk invalid  → raises ValidationError with clear message
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('widget', forms.HiddenInput())
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        if value is None:
            return None
        from media_manager.models import Media
        try:
            return Media.objects.get(pk=value)
        except Media.DoesNotExist:
            raise ValidationError(
                f"Selected media (id={value}) no longer exists. "
                "Please choose a different file from the library."
            )


class SitePreferencesForm(forms.ModelForm):

    # One hidden picker field per image
    icon_media             = MediaFKField()
    logo_media             = MediaFKField()
    fb_sharing_media       = MediaFKField()
    twitter_sharing_media  = MediaFKField()
    gallery_image_media    = MediaFKField()
    contact_image_media    = MediaFKField()
    default_image_media    = MediaFKField()
    facilities_image_media = MediaFKField()
    offer_image_media      = MediaFKField()

    class Meta:
        model  = SitePreferences
        # Image FK fields are handled by the MediaFKField above,
        # not by ModelForm's default FK handling.
        fields = [
            'is_maintenance',
            'site_title', 'site_name', 'copyright_text',
            'google_analytics_code', 'facebook_pixel_code', 'online_booking_code',
            'robots_txt',
            'booking_type', 'hotel_result_page', 'hotel_code',
        ]
        widgets = {
            'site_title':            forms.TextInput(attrs={'placeholder': 'e.g. My Hotel | Official Site'}),
            'site_name':             forms.TextInput(attrs={'placeholder': 'e.g. My Hotel'}),
            'copyright_text':        forms.TextInput(attrs={'placeholder': 'e.g. © 2025 My Hotel. All rights reserved.'}),
            'google_analytics_code': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste full <script> tag here'}),
            'facebook_pixel_code':   forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste full <script> tag here'}),
            'online_booking_code':   forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste booking widget embed code here'}),
            'robots_txt':            forms.Textarea(attrs={'rows': 6, 'placeholder': 'User-agent: *\nAllow: /'}),
            'hotel_result_page':     forms.TextInput(attrs={'placeholder': 'e.g. /booking/results/'}),
            'hotel_code':            forms.TextInput(attrs={'placeholder': 'e.g. HTL-001'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Apply each picker value to the corresponding FK field.
        # Only overwrite if the picker submitted a value — preserves
        # existing FK when the user saves without touching an image field.
        for field in IMAGE_FIELDS:
            media_obj = self.cleaned_data.get(f'{field}_media')
            if media_obj is not None:
                setattr(instance, field, media_obj)

        if commit:
            instance.save()
        return instance